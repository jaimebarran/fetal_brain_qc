# Fetal Brain Quality Control
## About
![fetal brain QC](img/fetal_brain_qc.png)

*Fetal brain QC* is a tool to facilitate quality annotations of T2w fetal brain MRI images, by creating interactive html-based visual reports from fetal brain scans. It uses a pair of low-resolution (LR) T2w images with corresponding brain masks to provide snapshots of the brain in the three orientations of the acquisition in the subject-space. 

The code is based on MRIQC [1], available at https://github.com/nipreps/mriqc.

**Note.** The current version of *Fetal brain QC* only works on low-resolution T2w images.

**Disclaimer.** Fetal brain QC is not intended for clinical use.


## Installation
fetal_brain_qc was developed in Ubuntu 22.04 and tested for python 3.9.15

To install this repository, first clone it via
```
git clone git@github.com:Medical-Image-Analysis-Laboratory/fetal_brain_qc.git
```
and enter into the directory. Create a conda environment using `conda env create -f environment.yml `

### fetal_brain_utils
Clone and install [fetal_brain_utils](https://github.com/Medical-Image-Analysis-Laboratory/fetal_brain_utils) using `python -m pip install -e .`

### MONAIfbs [2]
Download and install [MONAIfbs](https://github.com/gift-surg/MONAIfbs/tree/main): clone the repository, go into the repository and install it using `python -m pip install -e .`

Download the pretrained model [here](https://zenodo.org/record/4282679#.X7fyttvgqL5), and to add it to `fetal_brain_qc/models/MONAIfbs_dynunet_ckpt.pt`.

### fetal-IQA [3,4,5]
Download the checkpoint `pytorch.ckpt` from [fetal-IQA](https://github.com/daviddmc/fetal-IQA) at [https://zenodo.org/record/7368570]. Rename it to `fetal_IQA_pytorch.ckpt` and put it into `fetal_brain_qc/models`.

### pl-fetal-brain-assessment [6]
Download a checkpoint from [pl-fetal-brain-assessment](https://github.com/FNNDSC/pl-fetal-brain-assessment) from [this link](https://fnndsc.childrens.harvard.edu/mri_pipeline/ivan/quality_assessment/). Rename it to `FNNDSC_qcnet_ckpt.hdf5` and put it into `fetal_brain_qc/models`.

### Final Step
Finally, move back to the `fetal_brain_qc` repository and install `fetal_brain_qc` using `python -m pip install -e .`

## Usage
*Fetal brain QC* starts from a [BIDS](https://bids.neuroimaging.io/) dataset (containing `NIfTI` formatted images), as well as an additional folder containing *brain masks*. 

The recommended workflow is to use `qc_run_pipeline`
```
usage: qc_run_pipeline [-h] [--mask-patterns MASK_PATTERNS [MASK_PATTERNS ...]] [--bids-csv BIDS_CSV] [--anonymize-name | --no-anonymize-name] [--randomize | --no-randomize] [--seed SEED]
                       [--n-reports N_REPORTS] [--n-raters N_RATERS]
                       bids_dir out_path

Given a `bids_dir`, lists the LR series in the directory and tries to find corresponding masks given by `mask_patterns`. Then, saves all the found pairs of (LR series, masks) in a CSV file at `bids_csv`

positional arguments:
  bids_dir              BIDS directory containing the LR series.
  out_path              Path where the reports will be stored.

optional arguments:
  -h, --help            show this help message and exit
  --mask-patterns MASK_PATTERNS [MASK_PATTERNS ...]
                        List of patterns to find the LR masks corresponding to the LR series. Patterns will be of the form
                        "sub-{subject}[/ses-{session}][/{datatype}]/sub-{subject}[_ses-{session}][_acq-{acquisition}][_run-{run}]_{suffix}.nii.gz", and the different fields will be substituted based on
                        the structure of bids_dir. The code will attempt to find the mask corresponding to the first pattern, and if it fails, will attempt the next one, etc. If no masks are found, a
                        warning message will be displayed for the given subject, session and run. (default: ['/media/tsanchez/tsanchez_data/data/data_anon/derivatives/refined_masks/sub-{subject}[/ses-{
                        session}][/{datatype}]/sub-{subject}[_ses-{session}][_acq-{acquisition}][_run-{run}]_{suffix}.nii.gz', '/media/tsanchez/tsanchez_data/data/data_anon/derivatives/automated_masks/
                        sub-{subject}[/ses-{session}][/{datatype}]/sub-{subject}[_ses-{session}][_acq-{acquisition}][_run-{run}]_{suffix}.nii.gz'])
  --bids-csv BIDS_CSV   CSV file where the list of available LR series and masks is stored. (default: bids_csv.csv)
  --anonymize-name, --no-anonymize-name
                        Whether an anonymized name must be stored along the paths in `out-csv`. This will determine whether the reports will be anonymous in the end. (default: True)
  --randomize, --no-randomize
                        Whether the order of the reports should be randomized. The number of splits will be given by `n-raters` and the number of reports in each split by `n-reports`. The results will
                        be stored in different subfolders of `out-path` (default: True)
  --seed SEED           Seed to control the randomization (to be used with randomize=True). (default: 42)
  --n-reports N_REPORTS
                        Number of reports that should be used in the randomized study (to be used with randomize=True). (default: 100)
  --n-raters N_RATERS   Number of permutations of the data that must be computed (to be used with randomize=True). (default: 3)
  --navigation, --no-navigation
                        Whether the user should be able to freely navigate between reports. This is
                        disabled for rating, to force user to process reports sequentially.
                        (default: False)

```
**Remark.** This script runs the whole pipeline of *fetal brain QC*, i.e. listing of BIDS directory and masks -> (anonymization of data) -> report generation (-> randomization of reports) -> index file generation

Each part of the pipeline can also be called individually, as shown below.

- `qc_list_bids_csv` (+ anonymization)
```
usage: qc_list_bids_csv [-h] [--mask-patterns MASK_PATTERNS [MASK_PATTERNS ...]] [--out-csv OUT_CSV] [--anonymize-name | --no-anonymize-name] bids-dir

Given a `bids_dir`, lists the LR series in the directory and tries to find corresponding masks given by `mask_patterns`. Then, saves all the found pairs of (LR series, masks) in a CSV file at `out_csv`

positional arguments:
  bids_dir              BIDS directory containing the LR series.

options:
  -h, --help            show this help message and exit
  --mask-patterns MASK_PATTERNS [MASK_PATTERNS ...]
                        List of patterns to find the LR masks corresponding to the LR series. Patterns will be of the form
                        "sub-{subject}[/ses-{session}][/{datatype}]/sub-{subject}[_ses-{session}][_acq-{acquisition}][_run-{run}]_{suffix}.nii.gz", and the different fields will be substituted based on
                        the structure of bids_dir. The code will attempt to find the mask corresponding to the first pattern, and if it fails, will attempt the next one, etc. If no masks are found, a
                        warning message will be displayed for the given subject, session and run.
  --out-csv OUT_CSV     CSV file where the list of available LR series and masks is stored.
  --anonymize-name, --no-anonymize-name
                        Whether an anonymized name must be stored along the paths in `out-csv`. This will determine whether the reports will be anonymous in the end. (default: True)
```

- `qc_generate_reports`
```
usage: qc_generate_reports [-h] [--add-js | --no-add-js] out-path bids-csv

positional arguments:
  out_path              Path where the reports will be stored.
  bids_csv              Path where the bids config csv file is located.

optional arguments:
  -h, --help            show this help message and exit
  --add-js, --no-add-js
                        Whether some javascript should be added to the report for interaction with the index file. (default: True)
```

- `qc_randomize_reports`
```
usage: qc_randomize_reports [-h] [--seed SEED] [--n-reports N_REPORTS] [--n-raters N_RATERS] reports-path out-path

Randomization of the reports located in `reports_path`. By default, the `n-reports` random reports will be sampled and `n-reports` different permutations of these reports will be saved as subfolders of
`out-path` labelled as split_1 to split_<n-raters>. Each folder will contain an `ordering.csv` file with the randomized ordering to be used.

positional arguments:
  reports_path          Path where the reports are located
  out_path              Path where the randomized reports will be stored.

optional arguments:
  -h, --help            show this help message and exit
  --seed SEED           Seed to control the randomization (default: 42)
  --n-reports N_REPORTS
                        Number of reports that should be used in the randomized study. (default: 100)
  --n-raters N_RATERS   Number of raters (number of permutations of the data that must be computed). (default: 3)
```

- `qc_generate_index`
```
usage: qc_generate_index [-h] [--add-script-to-reports | --no-add-script-to-reports] [--use-ordering-file | --no-use-ordering-file] reports-path [reports-path ...]

positional arguments:
  reports_path          Path where the reports are located

options:
  -h, --help            show this help message and exit
  --add-script-to-reports, --no-add-script-to-reports
                        Whether some javascript should be added to the report for interaction with the index file. (default: False)
  --use-ordering-file, --no-use-ordering-file
                        Whether ordering.csv should be used to construct the ordering of index.html. The file should be located in the report-path folder. (default: False)
  --navigation, --no-navigation
                        Whether the user should be able to freely navigate between reports. This is
                        disabled for rating, to force user to process reports sequentially.
                        (default: False)

```
## License
Part of this work is based on MRIQC, which is licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## References
[1] Esteban, Oscar, et al. "MRIQC: Advancing the automatic prediction of image quality in MRI from unseen sites." PloS one 12.9 (2017): e0184661.
[2] Ranzini, Marta, et al. "MONAIfbs: MONAI-based fetal brain MRI deep learning segmentation." arXiv preprint arXiv:2103.13314 (2021).

[3] Semi-supervised learning for fetal brain MRI quality assessment with ROI consistency

[4] Gagoski, Borjan, et al. "Automated detection and reacquisition of motion‐degraded images in fetal HASTE imaging at 3 T." Magnetic Resonance in Medicine 87.4 (2022): 1914-1922.

[5] Lala, Sayeri, et al. "A deep learning approach for image quality assessment of fetal brain MRI." Proceedings of the 27th Annual Meeting of ISMRM, Montréal, Québec, Canada. 2019.

[6] https://github.com/FNNDSC/pl-fetal-brain-assessment
