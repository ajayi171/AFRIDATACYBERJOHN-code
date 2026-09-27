# Code Structure

| Component | Notebook cells | Purpose |
|---|---:|---|
| Synthetic and normal stream | 42–103 | Synthetic users, devices, sessions, events, normal context and behavioural calibration |
| Campaign and observable stream | 104–192 | Campaign, attack timeline, observable precursor and defender-observable stream construction |
| Prediction windows and hard negatives | 193–223 | Candidate users, prediction windows, matching, hard-negative reconstruction and validation |
| Forensic validation | 607–631 | Event, session, transaction and global forensic reconciliation; final Stage 20B checkpoint |
| Publication/release preparation | 632–662 | CSV export, data dictionary, documentation, package and repository metadata preparation |
| Provenance/final release audit | 663–723 | Provenance recovery, metadata checks, license/CFF validation, final release packaging and verification |

The complete notebook remains the authoritative source because many stages depend on variables and objects created earlier in the same notebook session.
