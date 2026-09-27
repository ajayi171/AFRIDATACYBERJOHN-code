# Reproduction Guide

## 1. Obtain the dataset

Download AFRIDATACYBERJOHN v1.0 from Zenodo using DOI `10.5281/zenodo.22934273`.

## 2. Environment

Create the conda environment from `environment.yml`, or install the packages in `requirements.txt` in a compatible Python environment.

## 3. Canonical workflow

Open:

`notebooks/AFRIDATACYBERJOHN_v1.0_reproducibility.ipynb`

Run the workflow sequentially. The notebook contains a long research history, including exploratory, diagnostic, forensic, reconstruction, and release-validation stages. Some cells depend on objects created earlier in the notebook or on recovered project artifacts.

## 4. Important reproducibility note

The notebook is the canonical research record. The six Python files under `src/` are archival stage extractions from the notebook; they preserve the corresponding cell code but may depend on state created by earlier stages.

## 5. Frozen release protection

The public dataset release should not be overwritten by rerunning exploratory or forensic cells. Reproduction experiments should use a separate working directory and should treat the Zenodo release as immutable input.
