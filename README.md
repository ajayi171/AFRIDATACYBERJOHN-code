# AFRIDATACYBERJOHN Code

Reproducible research code associated with **AFRIDATACYBERJOHN v1.0**, a synthetic, programmatically generated Africa-centric mobile-money and USSD cybersecurity dataset for behavioural intrusion-detection research.

## Repository status

This repository contains the research notebook used during dataset generation, reconstruction, validation, provenance analysis, and release preparation, together with archival Python extractions of the major workflow stages.

**Canonical source:** `notebooks/AFRIDATACYBERJOHN_v1.0_reproducibility.ipynb`

The extracted scripts under `src/` preserve notebook cell order and dependencies. They are provided to make the workflow easier to inspect and cite; they are not claimed to be independent command-line programs unless explicitly documented as such.

## Dataset

The associated dataset is permanently archived on Zenodo:

- Version 1.0 DOI: https://doi.org/10.5281/zenodo.22934273
- Dataset license: CC BY 4.0

The repository does **not** redistribute the frozen dataset CSV files. Obtain the dataset from the Zenodo record above.

## Reproducibility scope

The notebook records the research workflow from the synthetic generation environment through behavioural matching, hard-negative construction, forensic validation, and publication/release verification.

The original synthetic-generation configuration includes:

- Random seed: `20260901`
- Initial synthetic users: `100`
- Initial synthetic devices: `200`
- Initial synthetic sessions: `2000`
- Observation period: `2026-01-01 00:00:00` to `2026-06-30 23:59:59`

The released analytical dataset is a validated subset/release representation and should not be confused with the initial prototype population.

## Behavioural matching

The recovered workflow constructs a 16-dimensional behavioural signature containing:

1. `event_count`
2. `session_count`
3. `modality_count`
4. `event_type_count`
5. `delay_mean`
6. `delay_std`
7. `last_5_share`
8. `last_10_share`
9. `last_15_share`
10. `last_30_share`
11. `new_device_rate`
12. `location_change_rate`
13. `roaming_rate`
14. `transaction_count`
15. `transaction_amount_sum`
16. `event_type_entropy`

The horizon set is `{5, 10, 15, 30, 60}` minutes with a 60-minute observable lookback in the recovered workflow.

The user-level `user_match_distance` is based on the recovered profile-matching procedure: five horizon signatures are aggregated for each positive user, control-user profiles are formed from their candidate signatures, robust feature scaling is applied, and Euclidean distance is used for one-to-one matching. The notebook is the authoritative implementation reference.

## Hard-negative semantics

The hard-negative controls are intended to represent behaviourally similar **normal** activity. They should not be interpreted as confirmed attacks. The associated released records are synthetic and are not production banking, telecommunications, or customer records.

## Environment

The workflow was developed in a Python/Google Colab-style environment and uses common scientific Python packages. Some notebook cells reference Google Colab, mounted Drive paths, previously created in-memory objects, or project artifacts; these cells require adaptation when run outside the original environment.

See `requirements.txt` and `environment.yml` for the principal Python dependencies.

## Repository map

```text
AFRIDATACYBERJOHN-code/
├── README.md
├── LICENSE
├── CITATION.cff
├── requirements.txt
├── environment.yml
├── notebooks/
│   └── AFRIDATACYBERJOHN_v1.0_reproducibility.ipynb
├── src/
│   ├── 01_synthetic_and_normal_stream.py
│   ├── 02_attack_campaign_and_observable_stream.py
│   ├── 03_prediction_windows_and_hard_negative_pipeline.py
│   ├── 04_forensic_validation.py
│   ├── 05_publication_and_release_preparation.py
│   └── 06_provenance_and_final_release_audit.py
└── docs/
    ├── REPRODUCTION.md
    └── CODE_STRUCTURE.md
```

## Citation

When using the dataset, cite the AFRIDATACYBERJOHN Zenodo record. When using or adapting this code, cite this repository and its archived Zenodo code release when available.

## License

The code in this repository is released under the MIT License. The dataset itself has a separate CC BY 4.0 license.
