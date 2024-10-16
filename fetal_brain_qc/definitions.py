import os
import fetal_brain_qc as fbqc


MANU_BASE = (
    "/media/tsanchez/tsanchez_data/data/data_anon/derivatives/refined_masks/"
)
AUTO_BASE = (
    "/media/tsanchez/tsanchez_data/data/data_anon/derivatives/automated_masks/"
)
MASK_PATTERN = (
    "sub-{subject}[/ses-{session}][/{datatype}]/sub-{subject}"
    "[_ses-{session}][_acq-{acquisition}][_run-{run}]_{suffix}.nii.gz"
)

MASK_PATTERN_LIST = [MANU_BASE + MASK_PATTERN, AUTO_BASE + MASK_PATTERN]

BRAIN_CKPT = os.path.join(
    os.path.dirname(fbqc.__file__), "models/MONAIfbs_dynunet_ckpt.pt"
)

FETAL_IQA_CKPT = os.path.join(
    os.path.dirname(fbqc.__file__), "models/fetal_IQA_pytorch.ckpt"
)

FETAL_STACK_IQA_CKPT = os.path.join(
    os.path.dirname(fbqc.__file__), "models/FNNDSC_qcnet_ckpt.hdf5"
)

AUTO_MASK_PATH = "/media/tsanchez/tsanchez_data/data/out_anon/masks"

OUT_JSON_ORDER = [
    "sr-id",
    "session",
    "ga",
    "stacks",
    "use_auto_mask",
    "config_path",
    "info",
    "im_path",
    "mask_path",
]

SLICER_PATH = "/home/tsanchez/Slicer-5.0.3-linux-amd64/Slicer"

PATTERN = (
    "/sub-{subject}[/ses-{session}][/{datatype}]/sub-{subject}"
    "[_ses-{session}][_acq-{acquisition}][_run-{run}]_{suffix}.{extension}"
)
