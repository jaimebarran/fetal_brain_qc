from bs4 import BeautifulSoup as bs
from pathlib import Path
import numpy as np
import nibabel as ni
import copy
from pathlib import Path
import csv
import os
import operator
from collections import defaultdict
from functools import reduce
import json
import random


def squeeze_dim(arr, dim):
    if arr.shape[dim] == 1:
        return np.squeeze(arr, axis=dim)
    return arr


def iter_bids_dict(bids_dict: dict, _depth=0, max_depth=1):
    """Return a single iterator over the dictionary obtained from
    iter_dir - flexibly handles cases with and without a session date.
    Taken from https://thispointer.com/python-how-to-iterate-over-
    nested-dictionary-dict-of-dicts/
    """
    assert _depth >= 0
    for key, value in bids_dict.items():
        if isinstance(value, dict) and _depth < max_depth:
            # If value is dict then iterate over all its values
            for keyvalue in iter_bids_dict(
                value, _depth + 1, max_depth=max_depth
            ):
                yield (key, *keyvalue)
        else:
            # If value is not dict type then yield the value
            yield (key, value)


class nested_defaultdict:
    """Convenience class to create an arbitrary nested dictionary
    using defaultdict. The dictionary can be accessed using tuples
    of keys (k1,k2,k3,...).
    """

    def __init__(self):
        self._nested_dd = self.nested_default_dict()

    def __repr__(self):
        return json.dumps(self._nested_dd)

    def __str__(self):
        return json.dumps(self._nested_dd)

    def nested_default_dict(self):
        """Define a nested default dictionary"""
        return defaultdict(self.nested_default_dict)

    def get(self, map_list):
        """Get an item from a nested dictionary using a tuple of keys"""
        return reduce(operator.getitem, map_list, self._nested_dd)

    def set(self, map_list, value):
        """Set an item in a nested dictionary using a tuple of keys"""
        self.get(map_list[:-1])[map_list[-1]] = value

    def to_dict(self):
        return json.loads(json.dumps(self._nested_dd))


def csv_to_list(csv_path):
    file_list = []
    reader = csv.DictReader(open(csv_path))
    for i, line in enumerate(reader):
        file_list.append(line)
    return file_list


def fill_pattern(bids_layout, sub, ses, run, pattern, suffix="T2w_mask"):

    query = bids_layout.get(subject=sub, session=ses, run=run)[0]
    acquisition = query.entities["acquisition"]
    ents = {
        "subject": sub,
        "session": ses,
        "run": run,
        "datatype": "anat",
        "acquisition": acquisition,
        "suffix": suffix,
    }
    return bids_layout.build_path(ents, pattern, validate=False)


def iter_bids(
    bids_layout,
    extension="nii.gz",
    datatype="anat",
    suffix="T2w",
    target=None,
    return_type="filename",
):
    """Return a single iterator over the BIDSLayout obtained from
    pybids - flexibly handles cases with and without a session date.
    """
    for sub in sorted(bids_layout.get_subjects()):
        for ses in [None] + sorted(bids_layout.get_sessions(subject=sub)):
            for run in sorted(bids_layout.get_runs(subject=sub, session=ses)):
                out = bids_layout.get(
                    subject=sub,
                    session=ses,
                    run=run,
                    extension=extension,
                    datatype=datatype,
                    suffix=suffix,
                    target=target,
                    return_type=return_type,
                )
                if len(out) > 0:
                    yield (sub, ses, run, out[0])


def get_html_index(folder, use_ordering_file=False):
    """List all html files in the input `folder` or,
    if `use_ordering_file=True`, loads the ordering from
    `folder`/ordering.csv
    """
    folder = Path(folder)
    index_list = sorted(
        [
            f
            for f in Path(folder).iterdir()
            if f.is_file() and f.suffix == ".html" and "index" not in f.name
        ]
    )
    # raw_reports will not be ordered
    if "raw_reports" not in folder.name and (
        use_ordering_file and len(index_list) > 0
    ):
        ordering_file = Path(folder) / "ordering.csv"
        if not os.path.isfile(ordering_file):
            raise Exception(
                f"File ordering.csv not found at {ordering_file}. "
                "Did you mean to run with `--no-use-ordering-file`?"
            )

        reader = csv.DictReader(open(ordering_file))
        index_list = [Path(folder) / f["name"] for f in reader]
    elif len(index_list) > 0:
        if os.path.isfile(Path(folder) / "ordering.csv"):
            print(
                f"\tWARNING: ordering.csv was found but not used in {folder}.\n"
                f"\tDid you mean to run with --use-ordering-file?"
            )
    random.shuffle(index_list)
    return index_list


def add_message_to_reports(index_list):
    """Given a folder (`out_folder`) and a list of files in it (`index_list`),
    injects a javascript function into the html file to make it able to interact
    with the index.html file.
    """
    for file in index_list:
        # Parse HTML file in Beautiful Soup
        soup = bs(open(file), "html.parser")
        out = soup.find("script", type="text/javascript")
        in_str = out.string[1:]
        nspaces = len(in_str) - len(in_str.lstrip())
        newline = "\n" + " " * nspaces
        script_func = (
            f"{newline}$('#btn-download').click(function () {{{newline}"
            f"    window.parent.postMessage({{'message': 'rating done'}}, '*');"
            f"{newline}}});{newline}"
        )
        out.string = script_func + out.string
        with open(file, "w", encoding="utf-8") as f_output:
            f_output.write(str(soup))


def get_cropped_stack_based_on_mask(
    image_ni, mask_ni, boundary_i=0, boundary_j=0, boundary_k=0, unit="mm"
):
    """
    Crops the input image to the field of view given by the bounding box
    around its mask.
    Original code by Michael Ebner:
    https://github.com/gift-surg/NiftyMIC/blob/master/niftymic/base/stack.py

    Input
    -----
    image_ni:
        Nifti image
    mask_ni:
        Corresponding nifti mask
    boundary_i:
    boundary_j:
    boundary_k:
    unit:
        The unit defining the dimension size in nifti

    Output
    ------
    image_cropped:
        Image cropped to the bounding box of mask_ni
    mask_cropped
        Mask cropped to its bounding box
    """

    image_ni = copy.deepcopy(image_ni)
    image = image_ni.get_fdata()
    mask = squeeze_dim(mask_ni.get_fdata(), -1)
    # Get rectangular region surrounding the masked voxels
    [x_range, y_range, z_range] = get_rectangular_masked_region(mask)

    if np.array([x_range, y_range, z_range]).all() is None:
        print("Cropping to bounding box of mask led to an empty image.")
        return None

    if unit == "mm":
        spacing = image_ni.header.get_zooms()
        boundary_i = np.round(boundary_i / float(spacing[0]))
        boundary_j = np.round(boundary_j / float(spacing[1]))
        boundary_k = np.round(boundary_k / float(spacing[2]))

    shape = image.shape
    x_range[0] = np.max([0, x_range[0] - boundary_i])
    x_range[1] = np.min([shape[0], x_range[1] + boundary_i])

    y_range[0] = np.max([0, y_range[0] - boundary_j])
    y_range[1] = np.min([shape[1], y_range[1] + boundary_j])

    z_range[0] = np.max([0, z_range[0] - boundary_k])
    z_range[1] = np.min([shape[2], z_range[1] + boundary_k])
    # Crop to image region defined by rectangular mask

    new_origin = list(
        ni.affines.apply_affine(
            mask_ni.affine, [x_range[0], y_range[0], z_range[0]]
        )
    ) + [1]
    new_affine = image_ni.affine
    new_affine[:, -1] = new_origin
    image_cropped = crop_image_to_region(image, x_range, y_range, z_range)
    image_cropped = ni.Nifti1Image(image_cropped, new_affine)
    return image_cropped


def crop_image_to_region(
    image: np.ndarray,
    range_x: np.ndarray,
    range_y: np.ndarray,
    range_z: np.ndarray,
) -> np.ndarray:
    """
    Crop given image to region defined by voxel space ranges
    Original code by Michael Ebner:
    https://github.com/gift-surg/NiftyMIC/blob/master/niftymic/base/stack.py

    Input
    ------
    image: np.array
        image which will be cropped
    range_x: (int, int)
        pair defining x interval in voxel space for image cropping
    range_y: (int, int)
        pair defining y interval in voxel space for image cropping
    range_z: (int, int)
        pair defining z interval in voxel space for image cropping

    Output
    ------
    image_cropped:
        The image cropped to the given x-y-z region.
    """
    image_cropped = image[
        range_x[0] : range_x[1],
        range_y[0] : range_y[1],
        range_z[0] : range_z[1],
    ]
    return image_cropped


def get_rectangular_masked_region(
    mask: np.ndarray,
) -> tuple:
    """
    Computes the bounding box around the given mask
    Original code by Michael Ebner:
    https://github.com/gift-surg/NiftyMIC/blob/master/niftymic/base/stack.py

    Input
    -----
    mask: np.ndarray
        Input mask
    range_x:
        pair defining x interval of mask in voxel space
    range_y:
        pair defining y interval of mask in voxel space
    range_z:
        pair defining z interval of mask in voxel space
    """
    if np.sum(abs(mask)) == 0:
        return None, None, None
    shape = mask.shape
    # Compute sum of pixels of each slice along specified directions
    sum_xy = np.sum(mask, axis=(0, 1))  # sum within x-y-plane
    sum_xz = np.sum(mask, axis=(0, 2))  # sum within x-z-plane
    sum_yz = np.sum(mask, axis=(1, 2))  # sum within y-z-plane

    # Find masked regions (non-zero sum!)
    range_x = np.zeros(2)
    range_y = np.zeros(2)
    range_z = np.zeros(2)

    # Non-zero elements of numpy array nda defining x_range
    ran = np.nonzero(sum_yz)[0]
    range_x[0] = np.max([0, ran[0]])
    range_x[1] = np.min([shape[0], ran[-1] + 1])

    # Non-zero elements of numpy array nda defining y_range
    ran = np.nonzero(sum_xz)[0]
    range_y[0] = np.max([0, ran[0]])
    range_y[1] = np.min([shape[1], ran[-1] + 1])

    # Non-zero elements of numpy array nda defining z_range
    ran = np.nonzero(sum_xy)[0]
    range_z[0] = np.max([0, ran[0]])
    range_z[1] = np.min([shape[2], ran[-1] + 1])

    # Numpy reads the array as z,y,x coordinates! So swap them accordingly
    return (
        range_x.astype(int),
        range_y.astype(int),
        range_z.astype(int),
    )


def validate_inputs(args):
    """Check the validity of the arguments given
    in run_pipeline.py
    """
    if args.brain_extraction:
        assert (
            len(args.mask_patterns) == 1
        ), "A single mask_pattern must be provided when brain_extraction is enabled"
        assert args.mask_patterns_base is None, (
            "`mask_patterns_base` must be None when brain_extraction is enabled, "
            "as `out_path`/masks is used as the folder to store the outputs."
        )
    if args.randomize:
        raw_reports = Path(args.out_path) / "raw_reports/"
        assert not os.path.exists(raw_reports), (
            f"{args.out_path}/raw_reports path exists. Please define a different "
            "`out_path` for the experiment."
        )
        for i in range(args.n_raters):
            split = Path(args.out_path) / f"split_{i+1}/"
            assert not os.path.exists(split), (
                f"{split} path exists. Please define a different "
                "`out_path` for the experiment."
            )


def print_title(text):
    terminal_size = os.get_terminal_size().columns
    dashes_length = min(len(text) + 10, terminal_size)
    dashes = ("-" * dashes_length).center(terminal_size)
    text = text.upper().center(terminal_size)
    print("\n" + dashes + "\n" + text + "\n" + dashes + "\n")
