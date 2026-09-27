# AFRIDATACYBERJOHN — Forensic Validation Stages 1–20B
# This file is an archival extraction of the corresponding cells from
# AFRIDATACYBERJOHN_v1.0_reproducibility.ipynb.
# The canonical workflow is the notebook; this script is not guaranteed
# to be independently executable without the preceding workflow state.


# ==============================================================================
# NOTEBOOK CELL 607
# ==============================================================================

print("=" * 70)
print("71D.5F NON MATCHING WINDOW FORENSICS")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 608
# ==============================================================================

# ============================================================
# 71D.5F INPUT VALIDATION
# ============================================================

print("71D.5F INPUT VALIDATION")
print("=" * 70)

print("authoritative_events_71d5f:",
      authoritative_events_71d5f.shape)

print("current_events_71d5f:",
      current_events_71d5f.shape)

print("\nRequired objects:")
required = [
    "authoritative_events_71d5f",
    "current_events_71d5f",
    "authoritative_windows_71d5f",
    "current_windows",
]

for name in required:
    print(f"{name:40s}",
          "OK" if name in globals() else "MISSING")

print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 609
# ==============================================================================

# ============================================================
# 71D.5F NON MATCHING WINDOW FORENSICS
# STAGE 1: WINDOW LEVEL COMPARISON
# ============================================================

print("=" * 70)
print("71D.5F NON MATCHING WINDOW FORENSICS")
print("=" * 70)

print("\nEVENT POPULATIONS")
print("-" * 70)
print("Authoritative events:", authoritative_events_71d5f.shape)
print("Current events:      ", current_events_71d5f.shape)
print("Event difference:    ",
      len(current_events_71d5f) - len(authoritative_events_71d5f))

print("\nWINDOW POPULATIONS")
print("-" * 70)
print("Authoritative windows:", authoritative_windows_71d5f.shape)
print("Current windows:      ", current_windows.shape)

print("\nAUTHORITATIVE WINDOW COLUMNS")
print("-" * 70)
print(authoritative_windows_71d5f.columns.tolist())

print("\nCURRENT WINDOW COLUMNS")
print("-" * 70)
print(current_windows.columns.tolist())

print("\nAUTHORITATIVE WINDOW SAMPLE")
print("-" * 70)
display(authoritative_windows_71d5f.head())

print("\nCURRENT WINDOW SAMPLE")
print("-" * 70)
display(current_windows.head())

# ==============================================================================
# NOTEBOOK CELL 610
# ==============================================================================

# ============================================================
# 71D.5F NON MATCHING WINDOW FORENSICS
# STAGE 2: EXACT WINDOW COMPARISON
# ============================================================

print("=" * 70)
print("71D.5F STAGE 2: EXACT WINDOW COMPARISON")
print("=" * 70)

# Fields shared by both window tables
comparison_cols = [
    "window_id",
    "user_id",
    "matched_positive_user_id",
    "candidate_id",
    "horizon_minutes",
    "cutoff_time",
    "match_distance",
    "user_match_distance",
]

auth_cmp = authoritative_windows_71d5f[comparison_cols].copy()
curr_cmp = current_windows[comparison_cols].copy()

# Normalize datetime representation
auth_cmp["cutoff_time"] = pd.to_datetime(auth_cmp["cutoff_time"])
curr_cmp["cutoff_time"] = pd.to_datetime(curr_cmp["cutoff_time"])

# Sort before comparison
auth_cmp = auth_cmp.sort_values("window_id").reset_index(drop=True)
curr_cmp = curr_cmp.sort_values("window_id").reset_index(drop=True)

# Compare
window_comparison = auth_cmp.merge(
    curr_cmp,
    on="window_id",
    how="outer",
    suffixes=("_auth", "_current"),
    indicator=True
)

# Fields to test
compare_fields = [
    "user_id",
    "matched_positive_user_id",
    "candidate_id",
    "horizon_minutes",
    "cutoff_time",
    "match_distance",
    "user_match_distance",
]

# Identify differences
difference_masks = []

for col in compare_fields:
    left = window_comparison[f"{col}_auth"]
    right = window_comparison[f"{col}_current"]

    if pd.api.types.is_numeric_dtype(left):
        mask = ~np.isclose(
            left.astype(float),
            right.astype(float),
            equal_nan=True
        )
    else:
        mask = left.fillna("<NA>").astype(str) != right.fillna("<NA>").astype(str)

    difference_masks.append(mask)

window_comparison["has_difference"] = np.logical_or.reduce(
    difference_masks
)

nonmatching_windows_71d5f = window_comparison[
    window_comparison["has_difference"]
].copy()

print("\nTOTAL WINDOWS:", len(window_comparison))
print("MATCHING WINDOWS:", (~window_comparison["has_difference"]).sum())
print("NON MATCHING WINDOWS:", window_comparison["has_difference"].sum())

print("\nWINDOW MERGE STATUS")
print(window_comparison["_merge"].value_counts(dropna=False))

if len(nonmatching_windows_71d5f) > 0:

    print("\nNON MATCHING WINDOW IDs")
    print("-" * 70)
    print(
        nonmatching_windows_71d5f["window_id"]
        .tolist()
    )

    print("\nNON MATCHING WINDOWS")
    print("-" * 70)

    display(
        nonmatching_windows_71d5f[
            [
                "window_id",
                "user_id_auth",
                "user_id_current",
                "matched_positive_user_id_auth",
                "matched_positive_user_id_current",
                "candidate_id_auth",
                "candidate_id_current",
                "horizon_minutes_auth",
                "horizon_minutes_current",
                "cutoff_time_auth",
                "cutoff_time_current",
                "match_distance_auth",
                "match_distance_current",
                "user_match_distance_auth",
                "user_match_distance_current",
            ]
        ]
    )

else:
    print("\nALL 100 WINDOWS MATCH EXACTLY.")

# ==============================================================================
# NOTEBOOK CELL 611
# ==============================================================================

# ============================================================
# 71D.5F STAGE 2B
# NORMALIZED WINDOW ID COMPARISON
# ============================================================

print("=" * 70)
print("71D.5F STAGE 2B: NORMALIZED WINDOW COMPARISON")
print("=" * 70)

comparison_cols = [
    "window_id",
    "user_id",
    "matched_positive_user_id",
    "candidate_id",
    "horizon_minutes",
    "cutoff_time",
    "match_distance",
    "user_match_distance",
]

auth_cmp = authoritative_windows_71d5f[comparison_cols].copy()
curr_cmp = current_windows[comparison_cols].copy()

# ------------------------------------------------------------
# Normalize window IDs
# HNW71F_001  ->  1
# HN71F_00001 ->  1
# ------------------------------------------------------------

auth_cmp["window_key"] = (
    auth_cmp["window_id"]
    .astype(str)
    .str.extract(r"(\d+)$")[0]
    .astype(int)
)

curr_cmp["window_key"] = (
    curr_cmp["window_id"]
    .astype(str)
    .str.extract(r"(\d+)$")[0]
    .astype(int)
)

# Normalize datetimes
auth_cmp["cutoff_time"] = pd.to_datetime(auth_cmp["cutoff_time"])
curr_cmp["cutoff_time"] = pd.to_datetime(curr_cmp["cutoff_time"])

# Sort
auth_cmp = auth_cmp.sort_values("window_key").reset_index(drop=True)
curr_cmp = curr_cmp.sort_values("window_key").reset_index(drop=True)

# ------------------------------------------------------------
# Merge using normalized window key
# ------------------------------------------------------------

window_comparison_71d5f = auth_cmp.merge(
    curr_cmp,
    on="window_key",
    how="outer",
    suffixes=("_auth", "_current"),
    indicator=True
)

print("\nTOTAL WINDOW KEYS:", len(window_comparison_71d5f))

print("\nMERGE STATUS")
print("-" * 70)
print(
    window_comparison_71d5f["_merge"]
    .value_counts(dropna=False)
)

# ------------------------------------------------------------
# Compare substantive fields
# ------------------------------------------------------------

compare_fields = [
    "user_id",
    "matched_positive_user_id",
    "candidate_id",
    "horizon_minutes",
    "cutoff_time",
    "match_distance",
    "user_match_distance",
]

difference_masks = []

for col in compare_fields:

    left = window_comparison_71d5f[f"{col}_auth"]
    right = window_comparison_71d5f[f"{col}_current"]

    if pd.api.types.is_numeric_dtype(left):
        mask = ~np.isclose(
            left.astype(float),
            right.astype(float),
            equal_nan=True
        )
    else:
        mask = (
            left.fillna("<NA>").astype(str)
            !=
            right.fillna("<NA>").astype(str)
        )

    difference_masks.append(mask)

window_comparison_71d5f["has_difference"] = np.logical_or.reduce(
    difference_masks
)

nonmatching_71d5f = window_comparison_71d5f[
    window_comparison_71d5f["has_difference"]
].copy()

matching_71d5f = window_comparison_71d5f[
    ~window_comparison_71d5f["has_difference"]
].copy()

print("\nRESULT")
print("-" * 70)
print("Matching windows:    ", len(matching_71d5f))
print("Nonmatching windows: ", len(nonmatching_71d5f))

# ------------------------------------------------------------
# Show actual mismatches
# ------------------------------------------------------------

if len(nonmatching_71d5f) > 0:

    print("\nACTUAL NONMATCHING WINDOWS")
    print("-" * 70)

    display(
        nonmatching_71d5f[
            [
                "window_key",
                "window_id_auth",
                "window_id_current",
                "user_id_auth",
                "user_id_current",
                "matched_positive_user_id_auth",
                "matched_positive_user_id_current",
                "candidate_id_auth",
                "candidate_id_current",
                "horizon_minutes_auth",
                "horizon_minutes_current",
                "cutoff_time_auth",
                "cutoff_time_current",
                "match_distance_auth",
                "match_distance_current",
                "user_match_distance_auth",
                "user_match_distance_current",
            ]
        ]
    )

else:

    print("\nALL 100 WINDOWS MATCH AFTER ID NORMALIZATION.")

# ==============================================================================
# NOTEBOOK CELL 612
# ==============================================================================

# ============================================================
# 71D.5F STAGE 3: MISMATCH PATTERN BY USER
# ============================================================

print("=" * 70)
print("71D.5F STAGE 3: MISMATCH PATTERN BY USER")
print("=" * 70)

# Start from normalized comparison already created
x = window_comparison_71d5f.copy()

# Determine whether each field differs
fields = [
    "user_id",
    "matched_positive_user_id",
    "candidate_id",
    "horizon_minutes",
    "cutoff_time",
    "match_distance",
    "user_match_distance",
]

for col in fields:
    a = x[f"{col}_auth"]
    b = x[f"{col}_current"]

    if pd.api.types.is_numeric_dtype(a):
        x[f"{col}_diff"] = ~np.isclose(
            a.astype(float),
            b.astype(float),
            equal_nan=True
        )
    else:
        x[f"{col}_diff"] = (
            a.fillna("<NA>").astype(str)
            !=
            b.fillna("<NA>").astype(str)
        )

# Overall mismatch
x["any_diff"] = x[
    [f"{c}_diff" for c in fields]
].any(axis=1)

# ------------------------------------------------------------
# 1. Window result by authoritative user
# ------------------------------------------------------------

user_summary_71d5f = (
    x.groupby("user_id_auth", dropna=False)
     .agg(
         windows=("window_key", "count"),
         matching=("any_diff", lambda s: (~s).sum()),
         nonmatching=("any_diff", "sum")
     )
     .reset_index()
)

print("\nWINDOW STATUS BY AUTHORITATIVE USER")
print("-" * 70)

display(
    user_summary_71d5f
    .sort_values(["nonmatching", "user_id_auth"], ascending=[False, True])
)

# ------------------------------------------------------------
# 2. Which users have any mismatch?
# ------------------------------------------------------------

print("\nUSERS WITH NONMATCHING WINDOWS")
print("-" * 70)

display(
    user_summary_71d5f[
        user_summary_71d5f["nonmatching"] > 0
    ]
)

# ------------------------------------------------------------
# 3. Field-level mismatch counts
# ------------------------------------------------------------

print("\nFIELD LEVEL MISMATCH COUNTS")
print("-" * 70)

field_summary = pd.DataFrame({
    "field": fields,
    "mismatch_count": [
        int(x[f"{c}_diff"].sum())
        for c in fields
    ]
})

display(field_summary)

# ------------------------------------------------------------
# 4. Matching window IDs
# ------------------------------------------------------------

print("\nMATCHING WINDOW KEYS")
print("-" * 70)

print(
    x.loc[~x["any_diff"], "window_key"]
     .astype(int)
     .tolist()
)

# ------------------------------------------------------------
# 5. Authoritative/current user mapping
# ------------------------------------------------------------

print("\nAUTHORITATIVE USER -> CURRENT USER MAPPING")
print("-" * 70)

mapping = (
    x.groupby("user_id_auth")["user_id_current"]
     .agg(lambda s: sorted(set(s.dropna())))
     .reset_index()
)

display(mapping)

# ==============================================================================
# NOTEBOOK CELL 613
# ==============================================================================

# ============================================================
# 71D.5F STAGE 4: VERIFY USER BLOCK PERMUTATION
# ============================================================

print("=" * 70)
print("71D.5F STAGE 4: USER BLOCK PERMUTATION VERIFICATION")
print("=" * 70)

# ------------------------------------------------------------
# Build compact five-horizon signatures for every user
# ------------------------------------------------------------

auth = authoritative_windows_71d5f.copy()
curr = current_windows.copy()

# Normalize window numbering
auth["window_key"] = (
    auth["window_id"]
    .astype(str)
    .str.extract(r"(\d+)$")[0]
    .astype(int)
)

curr["window_key"] = (
    curr["window_id"]
    .astype(str)
    .str.extract(r"(\d+)$")[0]
    .astype(int)
)

# Sort by user and horizon
auth = auth.sort_values(
    ["user_id", "horizon_minutes"]
).reset_index(drop=True)

curr = curr.sort_values(
    ["user_id", "horizon_minutes"]
).reset_index(drop=True)

# ------------------------------------------------------------
# Create a deterministic signature from the substantive
# window fields
# ------------------------------------------------------------

signature_fields = [
    "horizon_minutes",
    "cutoff_time",
    "candidate_id",
    "matched_positive_user_id",
    "match_distance",
    "user_match_distance",
]

def make_user_signature(df):

    rows = []

    for _, r in df.sort_values("horizon_minutes").iterrows():

        cutoff = pd.to_datetime(r["cutoff_time"])

        rows.append(
            (
                int(r["horizon_minutes"]),
                str(cutoff),
                str(r["candidate_id"]),
                str(r["matched_positive_user_id"]),
                round(float(r["match_distance"]), 8),
                round(float(r["user_match_distance"]), 8),
            )
        )

    return tuple(rows)


auth_signatures = (
    auth.groupby("user_id", sort=True)
        .apply(make_user_signature)
        .to_dict()
)

curr_signatures = (
    curr.groupby("user_id", sort=True)
        .apply(make_user_signature)
        .to_dict()
)

# ------------------------------------------------------------
# Compare every current user against every authoritative user
# ------------------------------------------------------------

results = []

for current_user, current_sig in curr_signatures.items():

    matches = [
        auth_user
        for auth_user, auth_sig in auth_signatures.items()
        if current_sig == auth_sig
    ]

    results.append({
        "current_user": current_user,
        "matching_authoritative_users": matches,
        "n_matches": len(matches)
    })

permutation_check_71d5f = pd.DataFrame(results)

print("\nCURRENT USER -> EXACT AUTHORITATIVE BLOCK MATCH")
print("-" * 70)

display(permutation_check_71d5f)

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

exact_block_matches = permutation_check_71d5f[
    permutation_check_71d5f["n_matches"] == 1
]

no_matches = permutation_check_71d5f[
    permutation_check_71d5f["n_matches"] == 0
]

ambiguous = permutation_check_71d5f[
    permutation_check_71d5f["n_matches"] > 1
]

print("\nSUMMARY")
print("-" * 70)
print("Current users:", len(curr_signatures))
print("Exact block matches:", len(exact_block_matches))
print("No block match:", len(no_matches))
print("Ambiguous block matches:", len(ambiguous))

print("\nEXPECTED USER BLOCK COUNT")
print("-" * 70)
print("Authoritative users:", auth["user_id"].nunique())
print("Current users:", curr["user_id"].nunique())

# ==============================================================================
# NOTEBOOK CELL 614
# ==============================================================================

# ============================================================
# 71D.5F STAGE 5
# DEFINITIVE WINDOW ID PERMUTATION MAP
# ============================================================

print("=" * 70)
print("71D.5F STAGE 5: DEFINITIVE WINDOW ID PERMUTATION MAP")
print("=" * 70)

auth = authoritative_windows_71d5f.copy()
curr = current_windows.copy()

# ------------------------------------------------------------
# Normalize window IDs
# ------------------------------------------------------------

auth["window_key"] = (
    auth["window_id"]
    .astype(str)
    .str.extract(r"(\d+)$")[0]
    .astype(int)
)

curr["window_key"] = (
    curr["window_id"]
    .astype(str)
    .str.extract(r"(\d+)$")[0]
    .astype(int)
)

# ------------------------------------------------------------
# Match using USER + HORIZON
#
# These are the stable substantive identifiers.
# ------------------------------------------------------------

auth_key = auth[
    [
        "window_id",
        "window_key",
        "user_id",
        "matched_positive_user_id",
        "candidate_id",
        "horizon_minutes",
        "cutoff_time",
        "match_distance",
        "user_match_distance",
    ]
].copy()

curr_key = curr[
    [
        "window_id",
        "window_key",
        "user_id",
        "matched_positive_user_id",
        "candidate_id",
        "horizon_minutes",
        "cutoff_time",
        "match_distance",
        "user_match_distance",
    ]
].copy()

# Match the actual substantive block by user + horizon
mapping_71d5f = auth_key.merge(
    curr_key,
    on=["user_id", "horizon_minutes"],
    how="outer",
    suffixes=("_auth", "_current"),
    indicator=True
)

print("\nMERGE STATUS")
print("-" * 70)
print(mapping_71d5f["_merge"].value_counts(dropna=False))

print("\nTOTAL USER-HORIZON PAIRS:", len(mapping_71d5f))

# ------------------------------------------------------------
# Compare all substantive fields
# ------------------------------------------------------------

fields = [
    "matched_positive_user_id",
    "candidate_id",
    "cutoff_time",
    "match_distance",
    "user_match_distance",
]

for col in fields:

    a = mapping_71d5f[f"{col}_auth"]
    b = mapping_71d5f[f"{col}_current"]

    if pd.api.types.is_numeric_dtype(a):

        mapping_71d5f[f"{col}_same"] = np.isclose(
            a.astype(float),
            b.astype(float),
            equal_nan=True
        )

    else:

        mapping_71d5f[f"{col}_same"] = (
            a.fillna("<NA>").astype(str)
            ==
            b.fillna("<NA>").astype(str)
        )

mapping_71d5f["content_matches"] = mapping_71d5f[
    [f"{c}_same" for c in fields]
].all(axis=1)

print("\nCONTENT MATCH RESULT")
print("-" * 70)
print(
    "Content matching pairs:",
    int(mapping_71d5f["content_matches"].sum())
)
print(
    "Content mismatching pairs:",
    int((~mapping_71d5f["content_matches"]).sum())
)

# ------------------------------------------------------------
# Window ID equality
# ------------------------------------------------------------

mapping_71d5f["window_id_same"] = (
    mapping_71d5f["window_key_auth"]
    ==
    mapping_71d5f["window_key_current"]
)

print("\nWINDOW ID RESULT")
print("-" * 70)
print(
    "Same window key:",
    int(mapping_71d5f["window_id_same"].sum())
)
print(
    "Different window key:",
    int((~mapping_71d5f["window_id_same"]).sum())
)

# ------------------------------------------------------------
# Definitive permutation table
# ------------------------------------------------------------

permutation_map_71d5f = mapping_71d5f[
    [
        "window_key_auth",
        "window_id_auth",
        "window_key_current",
        "window_id_current",
        "user_id",
        "horizon_minutes",
        "content_matches",
        "window_id_same",
    ]
].sort_values("window_key_auth")

print("\nDEFINITIVE WINDOW PERMUTATION MAP")
print("-" * 70)

display(permutation_map_71d5f)

# ------------------------------------------------------------
# Show only genuinely reassigned IDs
# ------------------------------------------------------------

reassigned = permutation_map_71d5f[
    ~permutation_map_71d5f["window_id_same"]
].copy()

print("\nREASSIGNED WINDOW IDS")
print("-" * 70)
print("Count:", len(reassigned))

display(reassigned)

# ==============================================================================
# NOTEBOOK CELL 615
# ==============================================================================

# ============================================================
# 71D.5F STAGE 6
# FINAL WINDOW ID PERMUTATION VALIDATION
# ============================================================

print("=" * 70)
print("71D.5F STAGE 6: FINAL WINDOW ID PERMUTATION VALIDATION")
print("=" * 70)

pm = permutation_map_71d5f.copy()

# ------------------------------------------------------------
# Basic integrity
# ------------------------------------------------------------

print("\nTOTAL MAPPINGS:", len(pm))

print("\nAUTHORITATIVE WINDOW IDs:")
print("Unique:", pm["window_id_auth"].nunique())

print("\nCURRENT WINDOW IDs:")
print("Unique:", pm["window_id_current"].nunique())

# ------------------------------------------------------------
# One-to-one validation
# ------------------------------------------------------------

auth_duplicates = pm[
    pm["window_id_auth"].duplicated(keep=False)
]

current_duplicates = pm[
    pm["window_id_current"].duplicated(keep=False)
]

print("\nDUPLICATE CHECK")
print("-" * 70)
print("Duplicate authoritative IDs:", len(auth_duplicates))
print("Duplicate current IDs:", len(current_duplicates))

# ------------------------------------------------------------
# Content validation
# ------------------------------------------------------------

print("\nCONTENT VALIDATION")
print("-" * 70)
print("Content matches:",
      int(pm["content_matches"].sum()))
print("Content mismatches:",
      int((~pm["content_matches"]).sum()))

# ------------------------------------------------------------
# Identity permutation validation
# ------------------------------------------------------------

print("\nID PERMUTATION")
print("-" * 70)
print("Same IDs:",
      int(pm["window_id_same"].sum()))

print("Reassigned IDs:",
      int((~pm["window_id_same"]).sum()))

# ------------------------------------------------------------
# Final integrity condition
# ------------------------------------------------------------

valid_mapping = (
    len(pm) == 100
    and pm["window_id_auth"].nunique() == 100
    and pm["window_id_current"].nunique() == 100
    and len(auth_duplicates) == 0
    and len(current_duplicates) == 0
    and pm["content_matches"].all()
)

print("\nFINAL WINDOW PERMUTATION STATUS")
print("=" * 70)

if valid_mapping:
    print("PASS")
    print("All 100 authoritative windows map one-to-one")
    print("to 100 current windows with identical content.")
    print("The 85 differences are window-ID reassignment only.")
else:
    print("FAIL")
    print("Further investigation required.")

# ==============================================================================
# NOTEBOOK CELL 616
# ==============================================================================

# ============================================================
# 71D.5F STAGE 7
# IDENTIFY THE 31 EXTRA CURRENT EVENTS
# ============================================================

print("=" * 70)
print("71D.5F STAGE 7: EXTRA EVENT FORENSICS")
print("=" * 70)

auth = authoritative_events_71d5f.copy()
curr = current_events_71d5f.copy()

print("\nEVENT COUNTS")
print("-" * 70)
print("Authoritative:", len(auth))
print("Current:      ", len(curr))
print("Difference:   ", len(curr) - len(auth))

print("\nEVENT COLUMNS")
print("-" * 70)
print(auth.columns.tolist())

# ------------------------------------------------------------
# Find candidate identity columns
# ------------------------------------------------------------

preferred_keys = [
    "event_id",
    "event_uid",
    "id",
    "event_key",
    "session_id",
    "timestamp",
    "user_id",
]

available_keys = [
    c for c in preferred_keys
    if c in auth.columns and c in curr.columns
]

print("\nAVAILABLE IDENTITY COLUMNS")
print("-" * 70)
print(available_keys)

# ------------------------------------------------------------
# Show duplicated values in candidate identity columns
# ------------------------------------------------------------

print("\nDUPLICATE CHECK")
print("-" * 70)

for col in available_keys:
    auth_dup = auth[col].duplicated().sum()
    curr_dup = curr[col].duplicated().sum()

    print(
        f"{col:25s} "
        f"authoritative_duplicates={auth_dup:<5} "
        f"current_duplicates={curr_dup}"
    )

# ------------------------------------------------------------
# Try exact identity matching using the strongest available key
# ------------------------------------------------------------

if "event_id" in available_keys:
    identity_col = "event_id"
elif "event_uid" in available_keys:
    identity_col = "event_uid"
elif "event_key" in available_keys:
    identity_col = "event_key"
elif "id" in available_keys:
    identity_col = "id"
else:
    identity_col = None

print("\nSELECTED PRIMARY IDENTITY COLUMN")
print("-" * 70)
print(identity_col)

if identity_col is not None:

    auth_ids = set(auth[identity_col].dropna())
    curr_ids = set(curr[identity_col].dropna())

    extra_ids = curr_ids - auth_ids
    missing_ids = auth_ids - curr_ids

    print("\nIDENTITY SET COMPARISON")
    print("-" * 70)
    print("Authoritative unique IDs:", len(auth_ids))
    print("Current unique IDs:      ", len(curr_ids))
    print("Current only:            ", len(extra_ids))
    print("Authoritative only:      ", len(missing_ids))

    print("\nCURRENT ONLY IDS")
    print("-" * 70)
    print(sorted(extra_ids)[:100])

    print("\nAUTHORITATIVE ONLY IDS")
    print("-" * 70)
    print(sorted(missing_ids)[:100])

    extra_events_71d5f = curr[
        curr[identity_col].isin(extra_ids)
    ].copy()

    missing_events_71d5f = auth[
        auth[identity_col].isin(missing_ids)
    ].copy()

    print("\nEXTRA CURRENT EVENTS")
    print("-" * 70)
    print("Rows:", len(extra_events_71d5f))

    display(extra_events_71d5f)

else:

    print(
        "\nNo obvious event identity column was found."
    )
    print(
        "Do not attempt to infer the 31 events yet."
    )

# ==============================================================================
# NOTEBOOK CELL 617
# ==============================================================================

# ============================================================
# 71D.5F STAGE 8
# EVENT CONTENT FINGERPRINT FORENSICS
# ============================================================

print("=" * 70)
print("71D.5F STAGE 8: EVENT CONTENT FINGERPRINT FORENSICS")
print("=" * 70)

auth = authoritative_events_71d5f.copy()
curr = current_events_71d5f.copy()

print("\nSOURCE COUNTS")
print("-" * 70)
print("Authoritative:", len(auth))
print("Current:      ", len(curr))
print("Net difference:", len(curr) - len(auth))

# ------------------------------------------------------------
# Columns that identify the actual event content.
#
# We deliberately exclude:
# event_id
# source_event_id
# hard_negative_event_id
# window_id
# horizon_minutes
#
# These may be generated/reassigned identifiers or derived
# forensic fields.
# ------------------------------------------------------------

excluded = {
    "event_id",
    "source_event_id",
    "hard_negative_event_id",
    "window_id",
    "horizon_minutes",
}

fingerprint_cols = [
    c for c in auth.columns
    if c not in excluded
]

print("\nFINGERPRINT COLUMNS")
print("-" * 70)
print(fingerprint_cols)
print("\nNumber of fingerprint columns:", len(fingerprint_cols))

# ------------------------------------------------------------
# Normalize values for deterministic comparison
# ------------------------------------------------------------

def normalize_event_frame(df, columns):

    out = df[columns].copy()

    for col in columns:

        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = pd.to_datetime(
                out[col],
                errors="coerce"
            ).astype("string")

        elif pd.api.types.is_numeric_dtype(out[col]):
            out[col] = pd.to_numeric(
                out[col],
                errors="coerce"
            ).round(10)

        else:
            out[col] = (
                out[col]
                .astype("string")
                .fillna("<NA>")
                .str.strip()
            )

    return out


auth_fp = normalize_event_frame(
    auth,
    fingerprint_cols
)

curr_fp = normalize_event_frame(
    curr,
    fingerprint_cols
)

# ------------------------------------------------------------
# Create deterministic row fingerprints
# ------------------------------------------------------------

auth_fp["_fingerprint"] = (
    pd.util.hash_pandas_object(
        auth_fp,
        index=False
    )
)

curr_fp["_fingerprint"] = (
    pd.util.hash_pandas_object(
        curr_fp,
        index=False
    )
)

# ------------------------------------------------------------
# Fingerprint set comparison
# ------------------------------------------------------------

auth_hashes = set(auth_fp["_fingerprint"])
curr_hashes = set(curr_fp["_fingerprint"])

common_hashes = auth_hashes & curr_hashes
current_only_hashes = curr_hashes - auth_hashes
auth_only_hashes = auth_hashes - curr_hashes

print("\nFINGERPRINT SET COMPARISON")
print("-" * 70)
print("Authoritative unique fingerprints:", len(auth_hashes))
print("Current unique fingerprints:      ", len(curr_hashes))
print("Common fingerprints:              ", len(common_hashes))
print("Current only fingerprints:        ", len(current_only_hashes))
print("Authoritative only fingerprints:  ", len(auth_only_hashes))

# ------------------------------------------------------------
# Row level fingerprint membership
# ------------------------------------------------------------

auth_fp["content_match"] = (
    auth_fp["_fingerprint"].isin(common_hashes)
)

curr_fp["content_match"] = (
    curr_fp["_fingerprint"].isin(common_hashes)
)

print("\nROW LEVEL CONTENT MATCH")
print("-" * 70)
print(
    "Authoritative rows with matching content:",
    int(auth_fp["content_match"].sum())
)
print(
    "Current rows with matching content:",
    int(curr_fp["content_match"].sum())
)

print(
    "Authoritative rows without matching content:",
    int((~auth_fp["content_match"]).sum())
)

print(
    "Current rows without matching content:",
    int((~curr_fp["content_match"]).sum())
)

# ------------------------------------------------------------
# Show current rows whose content does not occur in
# authoritative events
# ------------------------------------------------------------

current_content_only = curr[
    curr_fp["_fingerprint"].isin(current_only_hashes)
].copy()

authoritative_content_only = auth[
    auth_fp["_fingerprint"].isin(auth_only_hashes)
].copy()

print("\nCURRENT CONTENT ONLY")
print("-" * 70)
print("Rows:", len(current_content_only))

display(
    current_content_only[
        [
            c for c in [
                "event_id",
                "timestamp",
                "user_id",
                "device_id",
                "session_id",
                "event_type",
                "window_id",
                "horizon_minutes",
                "hard_negative"
            ]
            if c in current_content_only.columns
        ]
    ].head(100)
)

print("\nAUTHORITATIVE CONTENT ONLY")
print("-" * 70)
print("Rows:", len(authoritative_content_only))

display(
    authoritative_content_only[
        [
            c for c in [
                "event_id",
                "timestamp",
                "user_id",
                "device_id",
                "session_id",
                "event_type",
                "window_id",
                "horizon_minutes",
                "hard_negative"
            ]
            if c in authoritative_content_only.columns
        ]
    ].head(100)
)

# ==============================================================================
# NOTEBOOK CELL 618
# ==============================================================================

# ============================================================
# 71D.5F STAGE 9
# UNMATCHED EVENT SEQUENCE FORENSICS
# ============================================================

print("=" * 70)
print("71D.5F STAGE 9: UNMATCHED EVENT SEQUENCE FORENSICS")
print("=" * 70)

auth = authoritative_events_71d5f.copy()
curr = current_events_71d5f.copy()

# ------------------------------------------------------------
# 1. RECREATE STAGE 8 FINGERPRINTS
# ------------------------------------------------------------

excluded = {
    "event_id",
    "source_event_id",
    "hard_negative_event_id",
    "window_id",
    "horizon_minutes",
}

fingerprint_cols = [
    c for c in auth.columns
    if c not in excluded
]

def normalize_event_frame(df, columns):
    out = df[columns].copy()

    for col in columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = pd.to_datetime(
                out[col],
                errors="coerce"
            ).astype("string")

        elif pd.api.types.is_numeric_dtype(out[col]):
            out[col] = pd.to_numeric(
                out[col],
                errors="coerce"
            ).round(10)

        else:
            out[col] = (
                out[col]
                .astype("string")
                .fillna("<NA>")
                .str.strip()
            )

    return out


auth_fp = normalize_event_frame(auth, fingerprint_cols)
curr_fp = normalize_event_frame(curr, fingerprint_cols)

auth_fp["_fingerprint"] = pd.util.hash_pandas_object(
    auth_fp,
    index=False
)

curr_fp["_fingerprint"] = pd.util.hash_pandas_object(
    curr_fp,
    index=False
)

auth_hashes = set(auth_fp["_fingerprint"])
curr_hashes = set(curr_fp["_fingerprint"])

common_hashes = auth_hashes & curr_hashes

auth_only_hashes = auth_hashes - curr_hashes
curr_only_hashes = curr_hashes - auth_hashes

# ------------------------------------------------------------
# 2. ISOLATE UNMATCHED RECORDS
# ------------------------------------------------------------

auth_unmatched = auth[
    auth_fp["_fingerprint"].isin(auth_only_hashes)
].copy()

curr_unmatched = curr[
    curr_fp["_fingerprint"].isin(curr_only_hashes)
].copy()

print("\nUNMATCHED COUNTS")
print("-" * 70)
print("Authoritative unmatched:", len(auth_unmatched))
print("Current unmatched:      ", len(curr_unmatched))
print("Difference:             ", len(curr_unmatched) - len(auth_unmatched))

# ------------------------------------------------------------
# 3. CREATE EVENT SEQUENCE POSITION
# ------------------------------------------------------------

for df in [auth_unmatched, curr_unmatched]:

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df["event_seq"] = (
        df.sort_values(
            ["session_id", "timestamp", "event_id"]
        )
        .groupby("session_id")
        .cumcount() + 1
    )

# ------------------------------------------------------------
# 4. SESSION LEVEL COMPARISON
# ------------------------------------------------------------

auth_sessions = (
    auth_unmatched
    .groupby("session_id")
    .agg(
        auth_rows=("event_id", "size"),
        auth_user=("user_id", "first"),
        auth_start=("timestamp", "min"),
        auth_end=("timestamp", "max"),
        auth_event_types=("event_type", lambda x: "|".join(x.astype(str)))
    )
    .reset_index()
)

curr_sessions = (
    curr_unmatched
    .groupby("session_id")
    .agg(
        curr_rows=("event_id", "size"),
        curr_user=("user_id", "first"),
        curr_start=("timestamp", "min"),
        curr_end=("timestamp", "max"),
        curr_event_types=("event_type", lambda x: "|".join(x.astype(str)))
    )
    .reset_index()
)

print("\nSESSION COUNTS")
print("-" * 70)
print("Authoritative unmatched sessions:", len(auth_sessions))
print("Current unmatched sessions:      ", len(curr_sessions))

# ------------------------------------------------------------
# 5. SESSION SIGNATURE
# ------------------------------------------------------------

def make_session_signature(df):

    tmp = (
        df.sort_values(
            ["session_id", "timestamp", "event_id"]
        )
        .groupby("session_id")
    )

    signatures = []

    for session_id, g in tmp:

        g = g.sort_values(
            ["timestamp", "event_id"]
        )

        signatures.append({
            "session_id": session_id,
            "user_id": g["user_id"].iloc[0],
            "event_count": len(g),
            "event_types": tuple(g["event_type"].astype(str)),
            "device_ids": tuple(g["device_id"].astype(str)),
            "timestamps": tuple(
                g["timestamp"].astype(str)
            ),
            "signature": (
                g["user_id"].iloc[0],
                len(g),
                tuple(g["event_type"].astype(str))
            )
        })

    return pd.DataFrame(signatures)


auth_sig = make_session_signature(auth_unmatched)
curr_sig = make_session_signature(curr_unmatched)

print("\nSESSION SIGNATURE SUMMARY")
print("-" * 70)

print(
    "Authoritative unique signatures:",
    auth_sig["signature"].nunique()
)

print(
    "Current unique signatures:",
    curr_sig["signature"].nunique()
)

# ------------------------------------------------------------
# 6. EXACT SESSION SIGNATURE MATCHING
# ------------------------------------------------------------

auth_sig_keyed = (
    auth_sig
    .groupby("signature")
    .agg(
        auth_sessions=("session_id", list),
        auth_count=("session_id", "size")
    )
    .reset_index()
)

curr_sig_keyed = (
    curr_sig
    .groupby("signature")
    .agg(
        curr_sessions=("session_id", list),
        curr_count=("session_id", "size")
    )
    .reset_index()
)

session_sig_compare = auth_sig_keyed.merge(
    curr_sig_keyed,
    on="signature",
    how="outer",
    indicator=True
)

print("\nSESSION SIGNATURE MATCH")
print("-" * 70)

print(
    session_sig_compare["_merge"]
    .value_counts()
)

# ------------------------------------------------------------
# 7. MATCH UNMATCHED SESSIONS BY STRUCTURAL SIGNATURE
# ------------------------------------------------------------

matched_session_signatures = session_sig_compare[
    session_sig_compare["_merge"] == "both"
].copy()

print(
    "\nMatched session signatures:",
    len(matched_session_signatures)
)

print(
    "Authoritative sessions represented:",
    int(matched_session_signatures["auth_count"].sum())
)

print(
    "Current sessions represented:",
    int(matched_session_signatures["curr_count"].sum())
)

# ------------------------------------------------------------
# 8. EVENT TYPE SEQUENCE COMPARISON
# ------------------------------------------------------------

auth_sequences = (
    auth_unmatched
    .sort_values(["session_id", "timestamp", "event_id"])
    .groupby("session_id")["event_type"]
    .apply(tuple)
    .reset_index(name="auth_sequence")
)

curr_sequences = (
    curr_unmatched
    .sort_values(["session_id", "timestamp", "event_id"])
    .groupby("session_id")["event_type"]
    .apply(tuple)
    .reset_index(name="curr_sequence")
)

print("\nEVENT TYPE SEQUENCES")
print("-" * 70)
print(
    "Authoritative unmatched sequences:",
    len(auth_sequences)
)
print(
    "Current unmatched sequences:",
    len(curr_sequences)
)

# ------------------------------------------------------------
# 9. DISPLAY STRUCTURAL MATCHES
# ------------------------------------------------------------

sequence_matches = auth_sequences.merge(
    curr_sequences,
    left_on="auth_sequence",
    right_on="curr_sequence",
    how="inner"
)

print("\nEXACT EVENT TYPE SEQUENCE MATCHES")
print("-" * 70)
print("Matched sequence pairs:", len(sequence_matches))

if len(sequence_matches) > 0:
    display(
        sequence_matches.head(100)
    )

# ------------------------------------------------------------
# 10. DISPLAY UNMATCHED SESSION STRUCTURES
# ------------------------------------------------------------

print("\nAUTHORITATIVE UNMATCHED SESSION STRUCTURES")
print("-" * 70)

display(
    auth_sig[
        [
            "session_id",
            "user_id",
            "event_count",
            "event_types"
        ]
    ].head(100)
)

print("\nCURRENT UNMATCHED SESSION STRUCTURES")
print("-" * 70)

display(
    curr_sig[
        [
            "session_id",
            "user_id",
            "event_count",
            "event_types"
        ]
    ].head(100)
)

print("\n" + "=" * 70)
print("STAGE 9 COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 619
# ==============================================================================

# ============================================================
# 71D.5F STAGE 10
# UNMATCHED SESSION SEQUENCE ALIGNMENT
# ============================================================

print("=" * 70)
print("71D.5F STAGE 10: UNMATCHED SESSION SEQUENCE ALIGNMENT")
print("=" * 70)

auth = authoritative_events_71d5f.copy()
curr = current_events_71d5f.copy()

# ------------------------------------------------------------
# RECREATE STAGE 8 UNMATCHED EVENT SETS
# ------------------------------------------------------------

excluded = {
    "event_id",
    "source_event_id",
    "hard_negative_event_id",
    "window_id",
    "horizon_minutes",
}

fingerprint_cols = [
    c for c in auth.columns
    if c not in excluded
]

def normalize_event_frame(df, columns):
    out = df[columns].copy()

    for col in columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = pd.to_datetime(
                out[col],
                errors="coerce"
            ).astype("string")

        elif pd.api.types.is_numeric_dtype(out[col]):
            out[col] = pd.to_numeric(
                out[col],
                errors="coerce"
            ).round(10)

        else:
            out[col] = (
                out[col]
                .astype("string")
                .fillna("<NA>")
                .str.strip()
            )

    return out


auth_fp = normalize_event_frame(auth, fingerprint_cols)
curr_fp = normalize_event_frame(curr, fingerprint_cols)

auth_fp["_fingerprint"] = pd.util.hash_pandas_object(
    auth_fp,
    index=False
)

curr_fp["_fingerprint"] = pd.util.hash_pandas_object(
    curr_fp,
    index=False
)

common_hashes = (
    set(auth_fp["_fingerprint"])
    &
    set(curr_fp["_fingerprint"])
)

auth_only_hashes = (
    set(auth_fp["_fingerprint"])
    -
    set(curr_fp["_fingerprint"])
)

curr_only_hashes = (
    set(curr_fp["_fingerprint"])
    -
    set(auth_fp["_fingerprint"])
)

auth_unmatched = auth[
    auth_fp["_fingerprint"].isin(auth_only_hashes)
].copy()

curr_unmatched = curr[
    curr_fp["_fingerprint"].isin(curr_only_hashes)
].copy()

auth_unmatched["timestamp"] = pd.to_datetime(
    auth_unmatched["timestamp"],
    errors="coerce"
)

curr_unmatched["timestamp"] = pd.to_datetime(
    curr_unmatched["timestamp"],
    errors="coerce"
)

# ------------------------------------------------------------
# 1. SESSION SUMMARY
# ------------------------------------------------------------

def session_summary(df, prefix):

    rows = []

    for session_id, g in df.groupby("session_id"):

        g = g.sort_values(
            ["timestamp", "event_id"]
        ).reset_index(drop=True)

        rows.append({
            "session_id": session_id,
            "user_id": g["user_id"].iloc[0],
            "event_count": len(g),
            "start": g["timestamp"].min(),
            "end": g["timestamp"].max(),
            "event_types": tuple(
                g["event_type"].astype(str)
            )
        })

    return pd.DataFrame(rows)


auth_sessions = session_summary(
    auth_unmatched,
    "auth"
)

curr_sessions = session_summary(
    curr_unmatched,
    "curr"
)

print("\nSESSION SUMMARY")
print("-" * 70)

print(
    "Authoritative sessions:",
    len(auth_sessions)
)

print(
    "Current sessions:",
    len(curr_sessions)
)

# ------------------------------------------------------------
# 2. GROUP SESSIONS BY USER
# ------------------------------------------------------------

print("\nUSER DISTRIBUTION OF UNMATCHED SESSIONS")
print("-" * 70)

user_compare = pd.merge(
    auth_sessions.groupby("user_id").agg(
        auth_sessions=("session_id", "count"),
        auth_events=("event_count", "sum")
    ).reset_index(),

    curr_sessions.groupby("user_id").agg(
        curr_sessions=("session_id", "count"),
        curr_events=("event_count", "sum")
    ).reset_index(),

    on="user_id",
    how="outer"
).fillna(0)

display(user_compare)

# ------------------------------------------------------------
# 3. DISPLAY ALL UNMATCHED EVENTS IN SEQUENCE
# ------------------------------------------------------------

display_cols = [
    "event_id",
    "timestamp",
    "user_id",
    "device_id",
    "session_id",
    "event_type",
    "modality",
    "session_type",
    "transaction_type",
    "transaction_amount",
    "new_beneficiary",
    "ground_truth_state",
    "is_attack",
    "is_observable_precursor",
    "hard_negative"
]

display_cols = [
    c for c in display_cols
    if c in auth_unmatched.columns
]

print("\nAUTHORITATIVE UNMATCHED EVENTS")
print("-" * 70)

display(
    auth_unmatched[
        display_cols
    ].sort_values(
        ["user_id", "session_id", "timestamp"]
    )
)

print("\nCURRENT UNMATCHED EVENTS")
print("-" * 70)

display(
    curr_unmatched[
        display_cols
    ].sort_values(
        ["user_id", "session_id", "timestamp"]
    )
)

# ------------------------------------------------------------
# 4. EVENT TYPE COUNTS BY USER
# ------------------------------------------------------------

auth_type_counts = (
    auth_unmatched
    .groupby(["user_id", "event_type"])
    .size()
    .unstack(fill_value=0)
)

curr_type_counts = (
    curr_unmatched
    .groupby(["user_id", "event_type"])
    .size()
    .unstack(fill_value=0)
)

all_users = sorted(
    set(auth_type_counts.index)
    |
    set(curr_type_counts.index)
)

all_event_types = sorted(
    set(auth_type_counts.columns)
    |
    set(curr_type_counts.columns)
)

auth_type_counts = auth_type_counts.reindex(
    index=all_users,
    columns=all_event_types,
    fill_value=0
)

curr_type_counts = curr_type_counts.reindex(
    index=all_users,
    columns=all_event_types,
    fill_value=0
)

print("\nAUTHORITATIVE EVENT TYPE COUNTS BY USER")
print("-" * 70)

display(auth_type_counts)

print("\nCURRENT EVENT TYPE COUNTS BY USER")
print("-" * 70)

display(curr_type_counts)

print("\nEVENT TYPE COUNT DIFFERENCE")
print("-" * 70)

display(
    curr_type_counts - auth_type_counts
)

# ------------------------------------------------------------
# 5. SESSION LENGTH COMPARISON BY USER
# ------------------------------------------------------------

print("\nSESSION LENGTHS BY USER")
print("-" * 70)

auth_lengths = (
    auth_sessions
    .groupby("user_id")["event_count"]
    .apply(list)
    .reset_index(name="authoritative_session_lengths")
)

curr_lengths = (
    curr_sessions
    .groupby("user_id")["event_count"]
    .apply(list)
    .reset_index(name="current_session_lengths")
)

length_compare = auth_lengths.merge(
    curr_lengths,
    on="user_id",
    how="outer"
)

display(length_compare)

# ------------------------------------------------------------
# 6. TIMESTAMP RANGE COMPARISON
# ------------------------------------------------------------

print("\nTIMESTAMP RANGES BY USER")
print("-" * 70)

auth_time = (
    auth_unmatched
    .groupby("user_id")["timestamp"]
    .agg(
        auth_first="min",
        auth_last="max"
    )
    .reset_index()
)

curr_time = (
    curr_unmatched
    .groupby("user_id")["timestamp"]
    .agg(
        curr_first="min",
        curr_last="max"
    )
    .reset_index()
)

time_compare = auth_time.merge(
    curr_time,
    on="user_id",
    how="outer"
)

time_compare["first_time_difference_seconds"] = (
    time_compare["curr_first"]
    -
    time_compare["auth_first"]
).dt.total_seconds()

time_compare["last_time_difference_seconds"] = (
    time_compare["curr_last"]
    -
    time_compare["auth_last"]
).dt.total_seconds()

display(time_compare)

# ------------------------------------------------------------
# 7. FINAL STRUCTURAL SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STAGE 10 STRUCTURAL SUMMARY")
print("=" * 70)

print(
    "Authoritative unmatched events:",
    len(auth_unmatched)
)

print(
    "Current unmatched events:",
    len(curr_unmatched)
)

print(
    "Authoritative unmatched sessions:",
    auth_unmatched["session_id"].nunique()
)

print(
    "Current unmatched sessions:",
    curr_unmatched["session_id"].nunique()
)

print(
    "Authoritative unmatched users:",
    auth_unmatched["user_id"].nunique()
)

print(
    "Current unmatched users:",
    curr_unmatched["user_id"].nunique()
)

print("=" * 70)
print("STAGE 10 COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 620
# ==============================================================================

# ============================================================
# 71D.5F STAGE 11
# EXACT UNMATCHED EVENT SEQUENCE ALIGNMENT
# ============================================================

print("=" * 70)
print("71D.5F STAGE 11: EXACT UNMATCHED EVENT SEQUENCE ALIGNMENT")
print("=" * 70)

auth = authoritative_events_71d5f.copy()
curr = current_events_71d5f.copy()

# ------------------------------------------------------------
# 1. RECREATE STAGE 8 UNMATCHED EVENTS
# ------------------------------------------------------------

excluded = {
    "event_id",
    "source_event_id",
    "hard_negative_event_id",
    "window_id",
    "horizon_minutes",
}

fingerprint_cols = [
    c for c in auth.columns
    if c not in excluded
]

def normalize_event_frame(df, columns):
    out = df[columns].copy()

    for col in columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = pd.to_datetime(
                out[col],
                errors="coerce"
            ).astype("string")

        elif pd.api.types.is_numeric_dtype(out[col]):
            out[col] = pd.to_numeric(
                out[col],
                errors="coerce"
            ).round(10)

        else:
            out[col] = (
                out[col]
                .astype("string")
                .fillna("<NA>")
                .str.strip()
            )

    return out


auth_fp = normalize_event_frame(auth, fingerprint_cols)
curr_fp = normalize_event_frame(curr, fingerprint_cols)

auth_fp["_fingerprint"] = pd.util.hash_pandas_object(
    auth_fp,
    index=False
)

curr_fp["_fingerprint"] = pd.util.hash_pandas_object(
    curr_fp,
    index=False
)

auth_only_hashes = (
    set(auth_fp["_fingerprint"])
    -
    set(curr_fp["_fingerprint"])
)

curr_only_hashes = (
    set(curr_fp["_fingerprint"])
    -
    set(auth_fp["_fingerprint"])
)

auth_unmatched = auth[
    auth_fp["_fingerprint"].isin(auth_only_hashes)
].copy()

curr_unmatched = curr[
    curr_fp["_fingerprint"].isin(curr_only_hashes)
].copy()

auth_unmatched["timestamp"] = pd.to_datetime(
    auth_unmatched["timestamp"],
    errors="coerce"
)

curr_unmatched["timestamp"] = pd.to_datetime(
    curr_unmatched["timestamp"],
    errors="coerce"
)

# ------------------------------------------------------------
# 2. ADD SEQUENCE POSITION
# ------------------------------------------------------------

auth_unmatched = auth_unmatched.sort_values(
    ["user_id", "session_id", "timestamp", "event_id"]
).copy()

curr_unmatched = curr_unmatched.sort_values(
    ["user_id", "session_id", "timestamp", "event_id"]
).copy()

auth_unmatched["seq"] = (
    auth_unmatched
    .groupby("session_id")
    .cumcount()
    + 1
)

curr_unmatched["seq"] = (
    curr_unmatched
    .groupby("session_id")
    .cumcount()
    + 1
)

# ------------------------------------------------------------
# 3. CREATE EVENT SIGNATURE WITHOUT TIMESTAMP
# ------------------------------------------------------------

sequence_columns = [
    "user_id",
    "device_id",
    "event_type",
    "modality",
    "session_type",
    "transaction_type",
    "transaction_amount",
    "new_beneficiary",
    "ground_truth_state",
    "is_attack",
    "is_observable_precursor",
    "hard_negative",
]

sequence_columns = [
    c for c in sequence_columns
    if c in auth_unmatched.columns
]

def clean_value(v):
    if pd.isna(v):
        return "<NA>"
    return str(v).strip()


def event_signature(row):
    return tuple(
        clean_value(row[c])
        for c in sequence_columns
    )


auth_unmatched["event_signature"] = auth_unmatched.apply(
    event_signature,
    axis=1
)

curr_unmatched["event_signature"] = curr_unmatched.apply(
    event_signature,
    axis=1
)

# ------------------------------------------------------------
# 4. EXACT SIGNATURE MATCH COUNTS
# ------------------------------------------------------------

auth_sig_counts = (
    auth_unmatched["event_signature"]
    .value_counts()
)

curr_sig_counts = (
    curr_unmatched["event_signature"]
    .value_counts()
)

common_signatures = (
    set(auth_sig_counts.index)
    &
    set(curr_sig_counts.index)
)

print("\nEVENT SIGNATURE MATCH")
print("-" * 70)

print(
    "Authoritative unique signatures:",
    len(auth_sig_counts)
)

print(
    "Current unique signatures:",
    len(curr_sig_counts)
)

print(
    "Common signatures:",
    len(common_signatures)
)

print(
    "Authoritative rows represented:",
    sum(
        auth_sig_counts[s]
        for s in common_signatures
    )
)

print(
    "Current rows represented:",
    sum(
        curr_sig_counts[s]
        for s in common_signatures
    )
)

# ------------------------------------------------------------
# 5. MATCH EVENTS WITHIN USER
# ------------------------------------------------------------

candidate_rows = []

for user_id in sorted(
    set(auth_unmatched["user_id"])
    &
    set(curr_unmatched["user_id"])
):

    a = auth_unmatched[
        auth_unmatched["user_id"] == user_id
    ].copy()

    c = curr_unmatched[
        curr_unmatched["user_id"] == user_id
    ].copy()

    for a_idx, arow in a.iterrows():

        candidates = c[
            c["event_signature"]
            ==
            arow["event_signature"]
        ].copy()

        if len(candidates) == 0:
            continue

        candidates["time_diff_seconds"] = (
            candidates["timestamp"]
            -
            arow["timestamp"]
        ).abs().dt.total_seconds()

        candidates = candidates.sort_values(
            "time_diff_seconds"
        )

        best = candidates.iloc[0]

        candidate_rows.append({
            "auth_index": a_idx,
            "auth_event_id": arow["event_id"],
            "auth_user_id": arow["user_id"],
            "auth_session_id": arow["session_id"],
            "auth_timestamp": arow["timestamp"],
            "auth_event_type": arow["event_type"],
            "curr_index": best.name,
            "curr_event_id": best["event_id"],
            "curr_user_id": best["user_id"],
            "curr_session_id": best["session_id"],
            "curr_timestamp": best["timestamp"],
            "curr_event_type": best["event_type"],
            "time_diff_seconds": best["time_diff_seconds"],
        })

candidate_matches = pd.DataFrame(candidate_rows)

# ------------------------------------------------------------
# 6. ENFORCE ONE TO ONE MATCHING
# ------------------------------------------------------------

if len(candidate_matches) > 0:

    candidate_matches = candidate_matches.sort_values(
        [
            "auth_event_id",
            "time_diff_seconds"
        ]
    )

    candidate_matches = (
        candidate_matches
        .drop_duplicates(
            subset=["auth_event_id"],
            keep="first"
        )
    )

    candidate_matches = candidate_matches.sort_values(
        [
            "curr_event_id",
            "time_diff_seconds"
        ]
    )

    candidate_matches = (
        candidate_matches
        .drop_duplicates(
            subset=["curr_event_id"],
            keep="first"
        )
    )

# ------------------------------------------------------------
# 7. MATCH QUALITY
# ------------------------------------------------------------

print("\nONE TO ONE EVENT MATCHING")
print("-" * 70)

print(
    "Candidate event matches:",
    len(candidate_matches)
)

if len(candidate_matches) > 0:

    print(
        "Exact signature matches:",
        len(candidate_matches)
    )

    print(
        "Maximum time difference:",
        candidate_matches[
            "time_diff_seconds"
        ].max(),
        "seconds"
    )

    print(
        "Median time difference:",
        candidate_matches[
            "time_diff_seconds"
        ].median(),
        "seconds"
    )

    print(
        "Matches within 60 seconds:",
        int(
            (
                candidate_matches[
                    "time_diff_seconds"
                ] <= 60
            ).sum()
        )
    )

    print(
        "Matches within 300 seconds:",
        int(
            (
                candidate_matches[
                    "time_diff_seconds"
                ] <= 300
            ).sum()
        )
    )

# ------------------------------------------------------------
# 8. IDENTIFY AUTHORITATIVE EVENTS WITHOUT MATCH
# ------------------------------------------------------------

matched_auth_ids = set()

if len(candidate_matches) > 0:
    matched_auth_ids = set(
        candidate_matches["auth_event_id"]
    )

auth_remaining = auth_unmatched[
    ~auth_unmatched["event_id"].isin(
        matched_auth_ids
    )
].copy()

# ------------------------------------------------------------
# 9. IDENTIFY CURRENT EVENTS WITHOUT MATCH
# ------------------------------------------------------------

matched_curr_ids = set()

if len(candidate_matches) > 0:
    matched_curr_ids = set(
        candidate_matches["curr_event_id"]
    )

curr_remaining = curr_unmatched[
    ~curr_unmatched["event_id"].isin(
        matched_curr_ids
    )
].copy()

print("\nUNMATCHED AFTER STRUCTURAL ALIGNMENT")
print("-" * 70)

print(
    "Authoritative events remaining:",
    len(auth_remaining)
)

print(
    "Current events remaining:",
    len(curr_remaining)
)

# ------------------------------------------------------------
# 10. DISPLAY EVENT MAPPING
# ------------------------------------------------------------

print("\nEVENT MAPPING")
print("-" * 70)

if len(candidate_matches) > 0:
    display(
        candidate_matches[
            [
                "auth_event_id",
                "auth_user_id",
                "auth_session_id",
                "auth_timestamp",
                "auth_event_type",
                "curr_event_id",
                "curr_session_id",
                "curr_timestamp",
                "curr_event_type",
                "time_diff_seconds"
            ]
        ].sort_values(
            [
                "auth_user_id",
                "auth_timestamp"
            ]
        )
    )

# ------------------------------------------------------------
# 11. DISPLAY REMAINING CURRENT EVENTS
# ------------------------------------------------------------

print("\nCURRENT EVENTS NOT STRUCTURALLY MATCHED")
print("-" * 70)

if len(curr_remaining) > 0:
    display(
        curr_remaining[
            [
                "event_id",
                "timestamp",
                "user_id",
                "device_id",
                "session_id",
                "event_type",
                "transaction_type",
                "transaction_amount",
                "new_beneficiary",
                "hard_negative"
            ]
        ]
    )

# ------------------------------------------------------------
# 12. DISPLAY REMAINING AUTHORITATIVE EVENTS
# ------------------------------------------------------------

print("\nAUTHORITATIVE EVENTS NOT STRUCTURALLY MATCHED")
print("-" * 70)

if len(auth_remaining) > 0:
    display(
        auth_remaining[
            [
                "event_id",
                "timestamp",
                "user_id",
                "device_id",
                "session_id",
                "event_type",
                "transaction_type",
                "transaction_amount",
                "new_beneficiary",
                "hard_negative"
            ]
        ]
    )

# ------------------------------------------------------------
# 13. FINAL STAGE SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STAGE 11 COMPLETE")
print("=" * 70)

print(
    "Authoritative unmatched:",
    len(auth_unmatched)
)

print(
    "Current unmatched:",
    len(curr_unmatched)
)

print(
    "One to one structural matches:",
    len(candidate_matches)
)

print(
    "Authoritative remaining:",
    len(auth_remaining)
)

print(
    "Current remaining:",
    len(curr_remaining)
)

print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 621
# ==============================================================================

# ============================================================
# 71D.5F STAGE 12
# SESSION EDIT DISTANCE FORENSICS
# ============================================================

print("=" * 70)
print("71D.5F STAGE 12: SESSION EDIT DISTANCE FORENSICS")
print("=" * 70)

auth = authoritative_events_71d5f.copy()
curr = current_events_71d5f.copy()

# ------------------------------------------------------------
# RECREATE STAGE 8 UNMATCHED EVENTS
# ------------------------------------------------------------

excluded = {
    "event_id",
    "source_event_id",
    "hard_negative_event_id",
    "window_id",
    "horizon_minutes",
}

fingerprint_cols = [
    c for c in auth.columns
    if c not in excluded
]

def normalize_event_frame(df, columns):
    out = df[columns].copy()

    for col in columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = pd.to_datetime(
                out[col],
                errors="coerce"
            ).astype("string")

        elif pd.api.types.is_numeric_dtype(out[col]):
            out[col] = pd.to_numeric(
                out[col],
                errors="coerce"
            ).round(10)

        else:
            out[col] = (
                out[col]
                .astype("string")
                .fillna("<NA>")
                .str.strip()
            )

    return out


auth_fp = normalize_event_frame(
    auth,
    fingerprint_cols
)

curr_fp = normalize_event_frame(
    curr,
    fingerprint_cols
)

auth_fp["_fingerprint"] = pd.util.hash_pandas_object(
    auth_fp,
    index=False
)

curr_fp["_fingerprint"] = pd.util.hash_pandas_object(
    curr_fp,
    index=False
)

auth_only = (
    set(auth_fp["_fingerprint"])
    -
    set(curr_fp["_fingerprint"])
)

curr_only = (
    set(curr_fp["_fingerprint"])
    -
    set(auth_fp["_fingerprint"])
)

auth_unmatched = auth[
    auth_fp["_fingerprint"].isin(auth_only)
].copy()

curr_unmatched = curr[
    curr_fp["_fingerprint"].isin(curr_only)
].copy()

auth_unmatched["timestamp"] = pd.to_datetime(
    auth_unmatched["timestamp"],
    errors="coerce"
)

curr_unmatched["timestamp"] = pd.to_datetime(
    curr_unmatched["timestamp"],
    errors="coerce"
)

# ------------------------------------------------------------
# 1. SESSION LISTS BY USER
# ------------------------------------------------------------

auth_sessions = (
    auth_unmatched
    .groupby(["user_id", "session_id"])
    .agg(
        start=("timestamp", "min"),
        end=("timestamp", "max"),
        events=("event_id", "count")
    )
    .reset_index()
)

curr_sessions = (
    curr_unmatched
    .groupby(["user_id", "session_id"])
    .agg(
        start=("timestamp", "min"),
        end=("timestamp", "max"),
        events=("event_id", "count")
    )
    .reset_index()
)

print("\nSESSION PAIRS BY USER")
print("-" * 70)

display(
    auth_sessions.merge(
        curr_sessions,
        on="user_id",
        how="outer",
        suffixes=("_auth", "_curr")
    )
)

# ------------------------------------------------------------
# 2. LEVENSHTEIN STYLE SEQUENCE ALIGNMENT
# ------------------------------------------------------------

def align_sequences(a, b):
    """
    Global sequence alignment using unit insertion,
    deletion and substitution cost.
    """

    n = len(a)
    m = len(b)

    dp = [[0] * (m + 1) for _ in range(n + 1)]
    op = [[None] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        dp[i][0] = i
        op[i][0] = "DELETE"

    for j in range(1, m + 1):
        dp[0][j] = j
        op[0][j] = "INSERT"

    for i in range(1, n + 1):

        for j in range(1, m + 1):

            if a[i - 1] == b[j - 1]:

                dp[i][j] = dp[i - 1][j - 1]
                op[i][j] = "MATCH"

            else:

                delete_cost = dp[i - 1][j] + 1
                insert_cost = dp[i][j - 1] + 1
                substitute_cost = dp[i - 1][j - 1] + 1

                best = min(
                    delete_cost,
                    insert_cost,
                    substitute_cost
                )

                dp[i][j] = best

                if best == substitute_cost:
                    op[i][j] = "SUBSTITUTE"
                elif best == delete_cost:
                    op[i][j] = "DELETE"
                else:
                    op[i][j] = "INSERT"

    # Backtrack
    i = n
    j = m

    alignment = []

    while i > 0 or j > 0:

        operation = op[i][j]

        if operation == "MATCH":

            alignment.append(
                (
                    "MATCH",
                    a[i - 1],
                    b[j - 1]
                )
            )

            i -= 1
            j -= 1

        elif operation == "SUBSTITUTE":

            alignment.append(
                (
                    "SUBSTITUTE",
                    a[i - 1],
                    b[j - 1]
                )
            )

            i -= 1
            j -= 1

        elif operation == "DELETE":

            alignment.append(
                (
                    "DELETE",
                    a[i - 1],
                    None
                )
            )

            i -= 1

        elif operation == "INSERT":

            alignment.append(
                (
                    "INSERT",
                    None,
                    b[j - 1]
                )
            )

            j -= 1

    alignment.reverse()

    return dp[n][m], alignment


# ------------------------------------------------------------
# 3. ALIGN SESSIONS
# ------------------------------------------------------------

alignment_results = []

for user_id in sorted(
    set(auth_unmatched["user_id"])
    |
    set(curr_unmatched["user_id"])
):

    auth_user = auth_unmatched[
        auth_unmatched["user_id"] == user_id
    ].copy()

    curr_user = curr_unmatched[
        curr_unmatched["user_id"] == user_id
    ].copy()

    auth_session_ids = (
        auth_user
        .sort_values("timestamp")
        ["session_id"]
        .drop_duplicates()
        .tolist()
    )

    curr_session_ids = (
        curr_user
        .sort_values("timestamp")
        ["session_id"]
        .drop_duplicates()
        .tolist()
    )

    # Pair sessions by chronological order.
    pair_count = max(
        len(auth_session_ids),
        len(curr_session_ids)
    )

    for k in range(pair_count):

        auth_sid = (
            auth_session_ids[k]
            if k < len(auth_session_ids)
            else None
        )

        curr_sid = (
            curr_session_ids[k]
            if k < len(curr_session_ids)
            else None
        )

        if auth_sid is None:
            alignment_results.append({
                "user_id": user_id,
                "auth_session": None,
                "curr_session": curr_sid,
                "distance": None,
                "matches": 0,
                "insertions": curr_user[
                    curr_user["session_id"] == curr_sid
                ]["event_type"].count(),
                "deletions": 0,
                "substitutions": 0
            })
            continue

        if curr_sid is None:
            alignment_results.append({
                "user_id": user_id,
                "auth_session": auth_sid,
                "curr_session": None,
                "distance": None,
                "matches": 0,
                "insertions": 0,
                "deletions": auth_user[
                    auth_user["session_id"] == auth_sid
                ]["event_type"].count(),
                "substitutions": 0
            })
            continue

        a_seq = (
            auth_user[
                auth_user["session_id"] == auth_sid
            ]
            .sort_values(
                ["timestamp", "event_id"]
            )["event_type"]
            .astype(str)
            .tolist()
        )

        c_seq = (
            curr_user[
                curr_user["session_id"] == curr_sid
            ]
            .sort_values(
                ["timestamp", "event_id"]
            )["event_type"]
            .astype(str)
            .tolist()
        )

        distance, alignment = align_sequences(
            a_seq,
            c_seq
        )

        matches = sum(
            1 for x in alignment
            if x[0] == "MATCH"
        )

        insertions = sum(
            1 for x in alignment
            if x[0] == "INSERT"
        )

        deletions = sum(
            1 for x in alignment
            if x[0] == "DELETE"
        )

        substitutions = sum(
            1 for x in alignment
            if x[0] == "SUBSTITUTE"
        )

        alignment_results.append({
            "user_id": user_id,
            "auth_session": auth_sid,
            "curr_session": curr_sid,
            "distance": distance,
            "matches": matches,
            "insertions": insertions,
            "deletions": deletions,
            "substitutions": substitutions,
            "auth_sequence": tuple(a_seq),
            "curr_sequence": tuple(c_seq)
        })

# ------------------------------------------------------------
# 4. DISPLAY ALIGNMENT RESULTS
# ------------------------------------------------------------

alignment_df = pd.DataFrame(
    alignment_results
)

print("\nSESSION ALIGNMENT RESULTS")
print("-" * 70)

display(
    alignment_df
)

# ------------------------------------------------------------
# 5. TOTAL EDIT OPERATIONS
# ------------------------------------------------------------

print("\nTOTAL EDIT OPERATIONS")
print("-" * 70)

for col in [
    "matches",
    "insertions",
    "deletions",
    "substitutions"
]:

    print(
        col + ":",
        int(
            alignment_df[col]
            .fillna(0)
            .sum()
        )
    )

print(
    "Total alignment distance:",
    int(
        alignment_df["distance"]
        .fillna(0)
        .sum()
    )
)

# ------------------------------------------------------------
# 6. CHECK WHETHER INSERTIONS EQUAL 31
# ------------------------------------------------------------

total_insertions = int(
    alignment_df["insertions"]
    .fillna(0)
    .sum()
)

total_deletions = int(
    alignment_df["deletions"]
    .fillna(0)
    .sum()
)

total_substitutions = int(
    alignment_df["substitutions"]
    .fillna(0)
    .sum()
)

print("\nFORENSIC DIFFERENCE CHECK")
print("-" * 70)

print(
    "Expected current excess:",
    len(curr_unmatched) - len(auth_unmatched)
)

print(
    "Observed insertions:",
    total_insertions
)

print(
    "Observed deletions:",
    total_deletions
)

print(
    "Observed substitutions:",
    total_substitutions
)

# ------------------------------------------------------------
# 7. FINAL STATUS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STAGE 12 COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 622
# ==============================================================================

# ============================================================
# 71D.5F STAGE 13
# FOUR SUBSTITUTION FORENSICS
# ============================================================

print("=" * 70)
print("71D.5F STAGE 13: FOUR SUBSTITUTION FORENSICS")
print("=" * 70)

auth = authoritative_events_71d5f.copy()
curr = current_events_71d5f.copy()

# ------------------------------------------------------------
# 1. RECREATE UNMATCHED EVENT POPULATIONS
# ------------------------------------------------------------

excluded = {
    "event_id",
    "source_event_id",
    "hard_negative_event_id",
    "window_id",
    "horizon_minutes",
}

fingerprint_cols = [
    c for c in auth.columns
    if c not in excluded
]

def normalize_event_frame(df, columns):
    out = df[columns].copy()

    for col in columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = pd.to_datetime(
                out[col],
                errors="coerce"
            ).astype("string")

        elif pd.api.types.is_numeric_dtype(out[col]):
            out[col] = pd.to_numeric(
                out[col],
                errors="coerce"
            ).round(10)

        else:
            out[col] = (
                out[col]
                .astype("string")
                .fillna("<NA>")
                .str.strip()
            )

    return out


auth_fp = normalize_event_frame(
    auth,
    fingerprint_cols
)

curr_fp = normalize_event_frame(
    curr,
    fingerprint_cols
)

auth_fp["_fingerprint"] = pd.util.hash_pandas_object(
    auth_fp,
    index=False
)

curr_fp["_fingerprint"] = pd.util.hash_pandas_object(
    curr_fp,
    index=False
)

auth_only = (
    set(auth_fp["_fingerprint"])
    -
    set(curr_fp["_fingerprint"])
)

curr_only = (
    set(curr_fp["_fingerprint"])
    -
    set(auth_fp["_fingerprint"])
)

auth_unmatched = auth[
    auth_fp["_fingerprint"].isin(auth_only)
].copy()

curr_unmatched = curr[
    curr_fp["_fingerprint"].isin(curr_only)
].copy()

auth_unmatched["timestamp"] = pd.to_datetime(
    auth_unmatched["timestamp"],
    errors="coerce"
)

curr_unmatched["timestamp"] = pd.to_datetime(
    curr_unmatched["timestamp"],
    errors="coerce"
)

# ------------------------------------------------------------
# 2. BUILD EVENT TYPE SEQUENCES
# ------------------------------------------------------------

auth_unmatched = auth_unmatched.sort_values(
    ["user_id", "session_id", "timestamp", "event_id"]
).copy()

curr_unmatched = curr_unmatched.sort_values(
    ["user_id", "session_id", "timestamp", "event_id"]
).copy()

# ------------------------------------------------------------
# 3. ALIGN EACH USER'S SESSIONS CHRONOLOGICALLY
# ------------------------------------------------------------

def align_sequences(a, b):

    n = len(a)
    m = len(b)

    dp = [[0] * (m + 1) for _ in range(n + 1)]
    op = [[None] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        dp[i][0] = i
        op[i][0] = "DELETE"

    for j in range(1, m + 1):
        dp[0][j] = j
        op[0][j] = "INSERT"

    for i in range(1, n + 1):

        for j in range(1, m + 1):

            if a[i - 1] == b[j - 1]:

                dp[i][j] = dp[i - 1][j - 1]
                op[i][j] = "MATCH"

            else:

                choices = [
                    (dp[i - 1][j - 1] + 1, "SUBSTITUTE"),
                    (dp[i - 1][j] + 1, "DELETE"),
                    (dp[i][j - 1] + 1, "INSERT")
                ]

                dp[i][j], op[i][j] = min(
                    choices,
                    key=lambda x: x[0]
                )

    i = n
    j = m

    alignment = []

    while i > 0 or j > 0:

        operation = op[i][j]

        if operation == "MATCH":
            alignment.append(
                (
                    "MATCH",
                    i - 1,
                    j - 1
                )
            )
            i -= 1
            j -= 1

        elif operation == "SUBSTITUTE":
            alignment.append(
                (
                    "SUBSTITUTE",
                    i - 1,
                    j - 1
                )
            )
            i -= 1
            j -= 1

        elif operation == "DELETE":
            alignment.append(
                (
                    "DELETE",
                    i - 1,
                    None
                )
            )
            i -= 1

        elif operation == "INSERT":
            alignment.append(
                (
                    "INSERT",
                    None,
                    j - 1
                )
            )
            j -= 1

    alignment.reverse()

    return alignment


# ------------------------------------------------------------
# 4. FIND ALL SUBSTITUTIONS
# ------------------------------------------------------------

substitution_records = []

for user_id in sorted(
    set(auth_unmatched["user_id"])
    &
    set(curr_unmatched["user_id"])
):

    auth_user = auth_unmatched[
        auth_unmatched["user_id"] == user_id
    ].copy()

    curr_user = curr_unmatched[
        curr_unmatched["user_id"] == user_id
    ].copy()

    auth_sessions = (
        auth_user
        .sort_values("timestamp")
        ["session_id"]
        .drop_duplicates()
        .tolist()
    )

    curr_sessions = (
        curr_user
        .sort_values("timestamp")
        ["session_id"]
        .drop_duplicates()
        .tolist()
    )

    for k in range(
        min(
            len(auth_sessions),
            len(curr_sessions)
        )
    ):

        auth_sid = auth_sessions[k]
        curr_sid = curr_sessions[k]

        a = (
            auth_user[
                auth_user["session_id"] == auth_sid
            ]
            .sort_values(
                ["timestamp", "event_id"]
            )
            .reset_index(drop=True)
        )

        c = (
            curr_user[
                curr_user["session_id"] == curr_sid
            ]
            .sort_values(
                ["timestamp", "event_id"]
            )
            .reset_index(drop=True)
        )

        a_types = a["event_type"].astype(str).tolist()
        c_types = c["event_type"].astype(str).tolist()

        alignment = align_sequences(
            a_types,
            c_types
        )

        for operation, ai, ci in alignment:

            if operation != "SUBSTITUTE":
                continue

            ar = a.iloc[ai]
            cr = c.iloc[ci]

            substitution_records.append({
                "user_id": user_id,
                "auth_session": auth_sid,
                "curr_session": curr_sid,

                "auth_event_id": ar["event_id"],
                "auth_timestamp": ar["timestamp"],
                "auth_event_type": ar["event_type"],

                "curr_event_id": cr["event_id"],
                "curr_timestamp": cr["timestamp"],
                "curr_event_type": cr["event_type"],

                "time_difference_seconds": (
                    cr["timestamp"]
                    -
                    ar["timestamp"]
                ).total_seconds()
            })


substitutions = pd.DataFrame(
    substitution_records
)

# ------------------------------------------------------------
# 5. DISPLAY THE FOUR SUBSTITUTIONS
# ------------------------------------------------------------

print("\nSUBSTITUTION RECORDS")
print("-" * 70)

print(
    "Number of substitutions:",
    len(substitutions)
)

display(substitutions)

# ------------------------------------------------------------
# 6. COMPARE EVERY FIELD
# ------------------------------------------------------------

compare_columns = [
    c for c in auth.columns
    if c not in {
        "event_id",
        "source_event_id",
        "hard_negative_event_id",
        "window_id",
        "horizon_minutes"
    }
]

comparison_rows = []

for _, row in substitutions.iterrows():

    ar = auth[
        auth["event_id"] == row["auth_event_id"]
    ].iloc[0]

    cr = curr[
        curr["event_id"] == row["curr_event_id"]
    ].iloc[0]

    for col in compare_columns:

        av = ar[col]
        cv = cr[col]

        if pd.isna(av) and pd.isna(cv):
            continue

        if str(av) == str(cv):
            continue

        comparison_rows.append({
            "user_id": row["user_id"],
            "auth_session": row["auth_session"],
            "curr_session": row["curr_session"],
            "auth_event_id": row["auth_event_id"],
            "curr_event_id": row["curr_event_id"],
            "field": col,
            "authoritative_value": av,
            "current_value": cv
        })

field_differences = pd.DataFrame(
    comparison_rows
)

# ------------------------------------------------------------
# 7. FIELD LEVEL DIFFERENCES
# ------------------------------------------------------------

print("\nFIELD LEVEL DIFFERENCES")
print("-" * 70)

print(
    "Total differing fields:",
    len(field_differences)
)

if len(field_differences) > 0:
    display(
        field_differences
    )

# ------------------------------------------------------------
# 8. DIFFERENCE COUNTS BY FIELD
# ------------------------------------------------------------

if len(field_differences) > 0:

    print("\nDIFFERENCES BY FIELD")
    print("-" * 70)

    display(
        field_differences[
            "field"
        ]
        .value_counts()
        .rename_axis("field")
        .reset_index(name="difference_count")
    )

# ------------------------------------------------------------
# 9. FULL RECORD COMPARISON
# ------------------------------------------------------------

print("\nFULL SUBSTITUTION RECORD COMPARISON")
print("-" * 70)

for _, row in substitutions.iterrows():

    print("\n" + "-" * 70)

    print(
        "USER:",
        row["user_id"]
    )

    print(
        "AUTHORITATIVE:",
        row["auth_event_id"],
        "|",
        row["auth_session"],
        "|",
        row["auth_timestamp"],
        "|",
        row["auth_event_type"]
    )

    print(
        "CURRENT:",
        row["curr_event_id"],
        "|",
        row["curr_session"],
        "|",
        row["curr_timestamp"],
        "|",
        row["curr_event_type"]
    )

    ar = auth[
        auth["event_id"] == row["auth_event_id"]
    ]

    cr = curr[
        curr["event_id"] == row["curr_event_id"]
    ]

    display(
        pd.DataFrame({
            "authoritative": ar.iloc[0],
            "current": cr.iloc[0]
        })
    )

# ------------------------------------------------------------
# 10. FINAL STATUS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STAGE 13 COMPLETE")
print("=" * 70)

print(
    "Substitutions identified:",
    len(substitutions)
)

print(
    "Field differences identified:",
    len(field_differences)
)

print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 623
# ==============================================================================

# ============================================================
# 71D.5F STAGE 14
# SUBSTITUTION PROVENANCE FORENSICS
# ============================================================

print("=" * 70)
print("71D.5F STAGE 14: SUBSTITUTION PROVENANCE FORENSICS")
print("=" * 70)

auth = authoritative_events_71d5f.copy()
curr = current_events_71d5f.copy()

# ------------------------------------------------------------
# FOUR KNOWN SUBSTITUTIONS FROM STAGE 13
# ------------------------------------------------------------

substitutions = [
    ("EVENT_00003479", "EVENT_00003503"),
    ("EVENT_00003480", "EVENT_00003504"),
    ("EVENT_00017984", "EVENT_00017871"),
    ("EVENT_00017985", "EVENT_00017872"),
]

# ------------------------------------------------------------
# 1. DISPLAY SOURCE RECORDS
# ------------------------------------------------------------

print("\nKNOWN SUBSTITUTIONS")
print("-" * 70)

for auth_id, curr_id in substitutions:

    ar = auth[
        auth["event_id"] == auth_id
    ]

    cr = curr[
        curr["event_id"] == curr_id
    ]

    print("\n" + "-" * 70)
    print(
        "AUTHORITATIVE:",
        auth_id
    )
    print(
        "CURRENT:",
        curr_id
    )

    if len(ar) > 0:
        print("\nAuthoritative record:")
        display(ar)

    if len(cr) > 0:
        print("\nCurrent record:")
        display(cr)

# ------------------------------------------------------------
# 2. SEARCH CURRENT DATA FOR THE AUTHORITATIVE EVENT CONTENT
#    WITHOUT USING EVENT_ID, SESSION_ID OR WINDOW_ID
# ------------------------------------------------------------

search_columns = [
    "user_id",
    "device_id",
    "event_type",
    "modality",
    "country",
    "language_region",
    "mobile_money_platform",
    "session_type",
    "ussd_code",
    "network_type",
    "signal_strength_dbm",
    "response_delay_ms",
    "new_device",
    "location_change",
    "behaviour_profile",
    "transaction_type",
    "transaction_amount",
    "new_beneficiary",
    "ground_truth_state",
    "is_attack",
    "is_observable_precursor",
    "hard_negative",
]

search_columns = [
    c for c in search_columns
    if c in auth.columns
]

def values_equal(a, b):

    if pd.isna(a) and pd.isna(b):
        return True

    return str(a) == str(b)


print("\nAUTHORITATIVE CONTENT SEARCH IN CURRENT DATA")
print("-" * 70)

for auth_id, curr_id in substitutions:

    ar = auth[
        auth["event_id"] == auth_id
    ].iloc[0]

    candidate = curr[
        curr["user_id"] == ar["user_id"]
    ].copy()

    match_mask = pd.Series(
        True,
        index=candidate.index
    )

    for col in search_columns:

        if col == "event_type":
            continue

        if col == "timestamp":
            continue

        match_mask &= candidate[col].map(
            lambda x: values_equal(
                x,
                ar[col]
            )
        )

    matches = candidate[
        match_mask
    ].copy()

    print("\n" + "-" * 70)
    print(
        "Authoritative event:",
        auth_id
    )

    print(
        "Current event paired by Stage 13:",
        curr_id
    )

    print(
        "Potential current content matches:",
        len(matches)
    )

    if len(matches) > 0:

        display(
            matches[
                [
                    c for c in [
                        "event_id",
                        "timestamp",
                        "user_id",
                        "device_id",
                        "session_id",
                        "event_type",
                        "mobile_money_platform",
                        "session_type",
                        "transaction_type",
                        "transaction_amount",
                        "new_beneficiary",
                        "window_id",
                        "horizon_minutes",
                        "hard_negative"
                    ]
                    if c in matches.columns
                ]
            ]
        )

# ------------------------------------------------------------
# 3. SEARCH CURRENT DATA FOR TRANSACTION EVENTS
# ------------------------------------------------------------

print("\nCURRENT TRANSACTION EVENTS FOR AFFECTED USERS")
print("-" * 70)

affected_users = sorted(
    set(
        auth[
            auth["event_id"].isin(
                [x[0] for x in substitutions]
            )
        ]["user_id"]
    )
)

current_transactions = curr[
    curr["user_id"].isin(affected_users)
    &
    (
        curr["event_type"].astype(str)
        ==
        "TRANSACTION"
    )
].copy()

display(
    current_transactions[
        [
            c for c in [
                "event_id",
                "timestamp",
                "user_id",
                "device_id",
                "session_id",
                "event_type",
                "mobile_money_platform",
                "session_type",
                "transaction_type",
                "transaction_amount",
                "new_beneficiary",
                "window_id",
                "horizon_minutes",
                "hard_negative"
            ]
            if c in current_transactions.columns
        ]
    ]
)

# ------------------------------------------------------------
# 4. SEARCH AUTHORITATIVE DATA FOR CURRENT SUBSTITUTE CONTENT
# ------------------------------------------------------------

print("\nCURRENT SUBSTITUTE CONTENT SEARCH IN AUTHORITATIVE DATA")
print("-" * 70)

for auth_id, curr_id in substitutions:

    cr = curr[
        curr["event_id"] == curr_id
    ].iloc[0]

    candidate = auth[
        auth["user_id"] == cr["user_id"]
    ].copy()

    match_mask = pd.Series(
        True,
        index=candidate.index
    )

    for col in search_columns:

        if col == "event_type":
            continue

        if col == "timestamp":
            continue

        match_mask &= candidate[col].map(
            lambda x: values_equal(
                x,
                cr[col]
            )
        )

    matches = candidate[
        match_mask
    ].copy()

    print("\n" + "-" * 70)
    print(
        "Current event:",
        curr_id
    )

    print(
        "Potential authoritative content matches:",
        len(matches)
    )

    if len(matches) > 0:

        display(
            matches[
                [
                    c for c in [
                        "event_id",
                        "timestamp",
                        "user_id",
                        "device_id",
                        "session_id",
                        "event_type",
                        "mobile_money_platform",
                        "session_type",
                        "transaction_type",
                        "transaction_amount",
                        "new_beneficiary",
                        "window_id",
                        "horizon_minutes",
                        "hard_negative"
                    ]
                    if c in matches.columns
                ]
            ]
        )

# ------------------------------------------------------------
# 5. CHECK WHETHER THE FOUR AUTHORITATIVE EVENTS EXIST
#    IN CURRENT UNDER ANY EVENT TYPE
# ------------------------------------------------------------

print("\nTRANSACTION PRESERVATION CHECK")
print("-" * 70)

auth_transactions = auth[
    auth["event_id"].isin(
        [
            "EVENT_00003480",
            "EVENT_00017985"
        ]
    )
].copy()

for _, ar in auth_transactions.iterrows():

    same_user = curr[
        curr["user_id"] == ar["user_id"]
    ].copy()

    print("\nAuthoritative transaction:")
    print(
        ar[
            [
                "event_id",
                "user_id",
                "transaction_type",
                "transaction_amount",
                "new_beneficiary"
            ]
        ].to_dict()
    )

    print(
        "Current transactions for same user:"
    )

    display(
        same_user[
            same_user["event_type"].astype(str)
            ==
            "TRANSACTION"
        ][
            [
                c for c in [
                    "event_id",
                    "timestamp",
                    "session_id",
                    "transaction_type",
                    "transaction_amount",
                    "new_beneficiary",
                    "window_id",
                    "horizon_minutes"
                ]
                if c in same_user.columns
            ]
        ]
    )

# ------------------------------------------------------------
# 6. FINAL PROVENANCE SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STAGE 14 COMPLETE")
print("=" * 70)

print(
    "Substitutions investigated:",
    len(substitutions)
)

print(
    "Affected users:",
    affected_users
)

print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 624
# ==============================================================================

# ======================================================================
# 71D.5F STAGE 15: FULL SESSION ALIGNMENT PROVENANCE
# ======================================================================

import pandas as pd
import numpy as np
from difflib import SequenceMatcher

print("=" * 70)
print("71D.5F STAGE 15: FULL SESSION ALIGNMENT PROVENANCE")
print("=" * 70)

# ----------------------------------------------------------------------
# 1. Recreate the unmatched populations
# ----------------------------------------------------------------------

EXCLUDED_FP = {
    "event_id",
    "source_event_id",
    "hard_negative_event_id",
    "window_id",
    "horizon_minutes",
}

fp_cols = [c for c in authoritative_events_71d5f.columns
           if c not in EXCLUDED_FP]

auth_fp = authoritative_events_71d5f[fp_cols].astype(str).agg("|".join, axis=1)
curr_fp = current_events_71d5d5f[fp_cols].astype(str).agg("|".join, axis=1) \
    if "current_events_71d5d5f" in globals() else current_events_71d5f[fp_cols].astype(str).agg("|".join, axis=1)

common_fp = set(auth_fp) & set(curr_fp)

auth_unmatched = authoritative_events_71d5f[
    ~auth_fp.isin(common_fp)
].copy()

curr_unmatched = current_events_71d5f[
    ~curr_fp.isin(common_fp)
].copy()

# ----------------------------------------------------------------------
# 2. Four known substitutions
# ----------------------------------------------------------------------

sub_pairs = [
    ("EVENT_00003479", "EVENT_00003503"),
    ("EVENT_00003480", "EVENT_00003504"),
    ("EVENT_00017984", "EVENT_00017871"),
    ("EVENT_00017985", "EVENT_00017872"),
]

print("\nKNOWN SUBSTITUTION PAIRS")
print("-" * 70)

for a, c in sub_pairs:
    ar = authoritative_events_71d5f[
        authoritative_events_71d5f["event_id"] == a
    ].iloc[0]

    cr = current_events_71d5f[
        current_events_71d5f["event_id"] == c
    ].iloc[0]

    print(
        f"{a} ({ar['user_id']}, {ar['session_id']}, "
        f"{ar['event_type']})"
        f"  -->  "
        f"{c} ({cr['user_id']}, {cr['session_id']}, "
        f"{cr['event_type']})"
    )

# ----------------------------------------------------------------------
# 3. Build event-type + session sequences for every affected session
# ----------------------------------------------------------------------

affected_users = ["USER_00019", "USER_00093"]

for user in affected_users:

    print("\n" + "=" * 70)
    print(f"USER: {user}")
    print("=" * 70)

    auth_user = authoritative_events_71d5f[
        authoritative_events_71d5f["user_id"] == user
    ].copy()

    curr_user = current_events_71d5f[
        current_events_71d5f["user_id"] == user
    ].copy()

    auth_sessions = (
        auth_user.groupby("session_id")["timestamp"]
        .min()
        .sort_values()
        .index
        .tolist()
    )

    curr_sessions = (
        curr_user.groupby("session_id")["timestamp"]
        .min()
        .sort_values()
        .index
        .tolist()
    )

    print("\nAUTHORITATIVE SESSIONS")
    print("-" * 70)

    for sid in auth_sessions:
        s = auth_user[auth_user["session_id"] == sid].sort_values("timestamp")

        print(f"\n{sid} | {len(s)} events")

        for _, r in s.iterrows():
            print(
                f"  {r['event_id']} | "
                f"{r['timestamp']} | "
                f"{r['event_type']} | "
                f"{r['modality']} | "
                f"{r['mobile_money_platform']} | "
                f"{r['transaction_type']} | "
                f"{r['transaction_amount']}"
            )

    print("\nCURRENT SESSIONS")
    print("-" * 70)

    for sid in curr_sessions:
        s = curr_user[curr_user["session_id"] == sid].sort_values("timestamp")

        print(f"\n{sid} | {len(s)} events")

        for _, r in s.iterrows():
            print(
                f"  {r['event_id']} | "
                f"{r['timestamp']} | "
                f"{r['event_type']} | "
                f"{r['modality']} | "
                f"{r['mobile_money_platform']} | "
                f"{r['transaction_type']} | "
                f"{r['transaction_amount']}"
            )

# ----------------------------------------------------------------------
# 4. Directly inspect the two sessions containing the substitutions
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("SUBSTITUTION SESSION COMPARISON")
print("=" * 70)

session_pairs = [
    ("USER_00019", "SESSION_001008", "SESSION_000346"),
    ("USER_00093", "SESSION_001513", "SESSION_000659"),
]

for user, auth_sid, curr_sid in session_pairs:

    print("\n" + "-" * 70)
    print(f"USER: {user}")
    print(f"AUTH SESSION: {auth_sid}")
    print(f"CURR SESSION: {curr_sid}")
    print("-" * 70)

    a = authoritative_events_71d5f[
        (authoritative_events_71d5f["user_id"] == user) &
        (authoritative_events_71d5f["session_id"] == auth_sid)
    ].sort_values("timestamp")

    c = current_events_71d5f[
        (current_events_71d5f["user_id"] == user) &
        (current_events_71d5f["session_id"] == curr_sid)
    ].sort_values("timestamp")

    print("\nAUTH SEQUENCE:")
    print(
        " -> ".join(
            f"{r.event_type}[{r.event_id}]"
            for _, r in a.iterrows()
        )
    )

    print("\nCURRENT SEQUENCE:")
    print(
        " -> ".join(
            f"{r.event_type}[{r.event_id}]"
            for _, r in c.iterrows()
        )
    )

    print("\nAUTH EVENT IDs:")
    print(a["event_id"].tolist())

    print("\nCURRENT EVENT IDs:")
    print(c["event_id"].tolist())

# ----------------------------------------------------------------------
# 5. Determine whether the substitutions are positionally aligned
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("POSITIONAL ALIGNMENT TEST")
print("=" * 70)

for user, auth_sid, curr_sid in session_pairs:

    a = authoritative_events_71d5f[
        (authoritative_events_71d5f["user_id"] == user) &
        (authoritative_events_71d5f["session_id"] == auth_sid)
    ].sort_values("timestamp").reset_index(drop=True)

    c = current_events_71d5f[
        (current_events_71d5f["user_id"] == user) &
        (current_events_71d5f["session_id"] == curr_sid)
    ].sort_values("timestamp").reset_index(drop=True)

    print("\n" + "-" * 70)
    print(f"{user}: {auth_sid} --> {curr_sid}")
    print("-" * 70)

    n = min(len(a), len(c))

    for i in range(n):

        ar = a.iloc[i]
        cr = c.iloc[i]

        same_type = ar["event_type"] == cr["event_type"]
        same_modality = ar["modality"] == cr["modality"]
        same_platform = (
            ar["mobile_money_platform"] ==
            cr["mobile_money_platform"]
        )

        print(
            f"POS {i:02d}: "
            f"{ar['event_id']} {ar['event_type']}"
            f"  <->  "
            f"{cr['event_id']} {cr['event_type']}"
            f" | type={same_type}"
            f" modality={same_modality}"
            f" platform={same_platform}"
        )

# ----------------------------------------------------------------------
# 6. Final diagnostic
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("STAGE 15 DIAGNOSTIC")
print("=" * 70)

print("""
This stage does NOT modify either dataset.

Purpose:
1. Establish the complete event order within the affected sessions.
2. Determine whether the four substitutions remain aligned after
   accounting for the 31 inserted events.
3. Determine whether the transaction events are genuinely replaced,
   or whether the earlier session pairing produced an alignment artifact.

Do not repair or overwrite any records yet.
Paste the complete output before proceeding.
""")

# ==============================================================================
# NOTEBOOK CELL 625
# ==============================================================================

# ======================================================================
# 71D.5F STAGE 16: INSERTION / DELETION SEMANTIC FORENSICS
# ======================================================================

import pandas as pd
import numpy as np

print("=" * 70)
print("71D.5F STAGE 16: INSERTION / DELETION SEMANTIC FORENSICS")
print("=" * 70)

# ----------------------------------------------------------------------
# 1. Define affected users
# ----------------------------------------------------------------------

affected_users = [
    "USER_00019",
    "USER_00065",
    "USER_00083",
    "USER_00093"
]

# ----------------------------------------------------------------------
# 2. Compare event-type populations by affected user
# ----------------------------------------------------------------------

print("\nEVENT-TYPE POPULATION DIFFERENCE")
print("-" * 70)

for user in affected_users:

    a = authoritative_events_71d5f[
        authoritative_events_71d5f["user_id"] == user
    ]

    c = current_events_71d5f[
        current_events_71d5f["user_id"] == user
    ]

    a_counts = a["event_type"].value_counts()
    c_counts = c["event_type"].value_counts()

    all_types = sorted(
        set(a_counts.index) | set(c_counts.index)
    )

    print(f"\nUSER: {user}")
    print(
        f"{'EVENT TYPE':30s}"
        f"{'AUTH':>8s}"
        f"{'CURRENT':>10s}"
        f"{'DELTA':>10s}"
    )

    for et in all_types:

        av = int(a_counts.get(et, 0))
        cv = int(c_counts.get(et, 0))

        print(
            f"{et:30s}"
            f"{av:8d}"
            f"{cv:10d}"
            f"{cv-av:10d}"
        )

# ----------------------------------------------------------------------
# 3. Compare modality populations
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("MODALITY POPULATION DIFFERENCE")
print("=" * 70)

for user in affected_users:

    a = authoritative_events_71d5f[
        authoritative_events_71d5f["user_id"] == user
    ]

    c = current_events_71d5f[
        current_events_71d5f["user_id"] == user
    ]

    a_counts = a["modality"].value_counts()
    c_counts = c["modality"].value_counts()

    all_modalities = sorted(
        set(a_counts.index) | set(c_counts.index)
    )

    print(f"\nUSER: {user}")

    for m in all_modalities:

        av = int(a_counts.get(m, 0))
        cv = int(c_counts.get(m, 0))

        print(
            f"{m:20s} "
            f"AUTH={av:3d} "
            f"CURRENT={cv:3d} "
            f"DELTA={cv-av:+3d}"
        )

# ----------------------------------------------------------------------
# 4. Compare transaction populations
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("TRANSACTION FORENSICS")
print("=" * 70)

for user in affected_users:

    a_tx = authoritative_events_71d5f[
        (authoritative_events_71d5f["user_id"] == user) &
        (authoritative_events_71d5f["event_type"] == "TRANSACTION")
    ].copy()

    c_tx = current_events_71d5f[
        (current_events_71d5f["user_id"] == user) &
        (current_events_71d5f["event_type"] == "TRANSACTION")
    ].copy()

    print(f"\nUSER: {user}")
    print(
        f"Authoritative transactions: {len(a_tx)}"
    )
    print(
        f"Current transactions:       {len(c_tx)}"
    )

    if len(a_tx):
        print("\nAUTHORITATIVE TRANSACTIONS:")

        for _, r in a_tx.iterrows():

            print(
                f"{r['event_id']} | "
                f"{r['timestamp']} | "
                f"{r['mobile_money_platform']} | "
                f"{r['session_type']} | "
                f"{r['transaction_type']} | "
                f"{r['transaction_amount']} | "
                f"hard_negative={r['hard_negative']}"
            )

    if len(c_tx):
        print("\nCURRENT TRANSACTIONS:")

        for _, r in c_tx.iterrows():

            print(
                f"{r['event_id']} | "
                f"{r['timestamp']} | "
                f"{r['mobile_money_platform']} | "
                f"{r['session_type']} | "
                f"{r['transaction_type']} | "
                f"{r['transaction_amount']} | "
                f"hard_negative={r['hard_negative']}"
            )

# ----------------------------------------------------------------------
# 5. Identify ALL authoritative transaction events absent from current
#    by substantive transaction signature
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("AUTHORITATIVE TRANSACTION PRESERVATION TEST")
print("=" * 70)

tx_signature_cols = [
    "user_id",
    "device_id",
    "mobile_money_platform",
    "session_type",
    "transaction_type",
    "transaction_amount",
    "new_beneficiary",
    "ground_truth_state",
    "is_attack",
    "hard_negative",
]

auth_tx = authoritative_events_71d5f[
    authoritative_events_71d5f["event_type"] == "TRANSACTION"
].copy()

curr_tx = current_events_71d5f[
    current_events_71d5f["event_type"] == "TRANSACTION"
].copy()

auth_tx_sig = auth_tx[tx_signature_cols].astype(str).agg("|".join, axis=1)
curr_tx_sig = curr_tx[tx_signature_cols].astype(str).agg("|".join, axis=1)

auth_tx["tx_signature"] = auth_tx_sig
curr_tx["tx_signature"] = curr_tx_sig

current_tx_signatures = set(curr_tx["tx_signature"])

auth_tx["preserved_in_current"] = (
    auth_tx["tx_signature"].isin(current_tx_signatures)
)

print(
    "\nTotal authoritative transactions:",
    len(auth_tx)
)

print(
    "Authoritative transactions preserved:",
    int(auth_tx["preserved_in_current"].sum())
)

print(
    "Authoritative transactions absent:",
    int((~auth_tx["preserved_in_current"]).sum())
)

print("\nABSENT AUTHORITATIVE TRANSACTIONS:")

print(
    auth_tx.loc[
        ~auth_tx["preserved_in_current"],
        [
            "event_id",
            "user_id",
            "timestamp",
            "mobile_money_platform",
            "session_type",
            "transaction_type",
            "transaction_amount",
            "new_beneficiary",
            "ground_truth_state",
            "is_attack",
            "hard_negative"
        ]
    ].to_string(index=False)
)

# ----------------------------------------------------------------------
# 6. Check whether current has transactions that have no authoritative
#    equivalent
# ----------------------------------------------------------------------

auth_tx_signatures = set(auth_tx["tx_signature"])

curr_tx["exists_in_authoritative"] = (
    curr_tx["tx_signature"].isin(auth_tx_signatures)
)

print("\n" + "=" * 70)
print("CURRENT TRANSACTION NOVELTY")
print("=" * 70)

print(
    "Current transactions:",
    len(curr_tx)
)

print(
    "Current transactions matching authoritative:",
    int(curr_tx["exists_in_authoritative"].sum())
)

print(
    "Current transactions without authoritative equivalent:",
    int((~curr_tx["exists_in_authoritative"]).sum())
)

print("\nCURRENT-ONLY TRANSACTIONS:")

print(
    curr_tx.loc[
        ~curr_tx["exists_in_authoritative"],
        [
            "event_id",
            "user_id",
            "timestamp",
            "mobile_money_platform",
            "session_type",
            "transaction_type",
            "transaction_amount",
            "new_beneficiary",
            "ground_truth_state",
            "is_attack",
            "hard_negative"
        ]
    ].to_string(index=False)
)

# ----------------------------------------------------------------------
# 7. FINAL STAGE 16 STATUS
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("STAGE 16 COMPLETE")
print("=" * 70)

print("""
Interpretation targets:

A. If exactly two authoritative transactions are absent and all other
   authoritative transactions are preserved, the two missing transactions
   explain the semantic substitutions.

B. If additional authoritative transactions are absent, the discrepancy
   is broader than the two known substitutions.

C. If current-only transactions greatly exceed the expected population
   difference, investigate transaction generation/reconstruction logic.

D. No source dataframe is modified in this stage.
""")

# ==============================================================================
# NOTEBOOK CELL 626
# ==============================================================================

# ======================================================================
# 71D.5F STAGE 17: COMPLETE TRANSACTION SESSION PROVENANCE
# ======================================================================

import pandas as pd
import numpy as np

print("=" * 70)
print("71D.5F STAGE 17: COMPLETE TRANSACTION SESSION PROVENANCE")
print("=" * 70)

# ----------------------------------------------------------------------
# 1. Reconstruct authoritative/current transaction sets
# ----------------------------------------------------------------------

auth_tx = authoritative_events_71d5f[
    authoritative_events_71d5f["event_type"] == "TRANSACTION"
].copy()

curr_tx = current_events_71d5f[
    current_events_71d5f["event_type"] == "TRANSACTION"
].copy()

tx_cols = [
    "user_id",
    "device_id",
    "mobile_money_platform",
    "session_type",
    "transaction_type",
    "transaction_amount",
    "new_beneficiary",
    "ground_truth_state",
    "is_attack",
    "hard_negative",
]

auth_tx["tx_signature"] = (
    auth_tx[tx_cols].astype(str).agg("|".join, axis=1)
)

curr_tx["tx_signature"] = (
    curr_tx[tx_cols].astype(str).agg("|".join, axis=1)
)

current_tx_signatures = set(curr_tx["tx_signature"])

auth_tx["preserved"] = auth_tx["tx_signature"].isin(
    current_tx_signatures
)

curr_tx_signatures = set(auth_tx["tx_signature"])

curr_tx["authoritative_equivalent"] = (
    curr_tx["tx_signature"].isin(curr_tx_signatures)
)

missing_auth_tx = auth_tx[
    ~auth_tx["preserved"]
].copy()

current_only_tx = curr_tx[
    ~curr_tx["authoritative_equivalent"]
].copy()

# ----------------------------------------------------------------------
# 2. Display every missing authoritative transaction with session
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("ALL MISSING AUTHORITATIVE TRANSACTIONS")
print("=" * 70)

missing_display = [
    "event_id",
    "timestamp",
    "user_id",
    "device_id",
    "session_id",
    "event_type",
    "modality",
    "mobile_money_platform",
    "session_type",
    "transaction_type",
    "transaction_amount",
    "new_beneficiary",
    "window_id",
    "horizon_minutes",
    "hard_negative",
]

print(
    missing_auth_tx[missing_display]
    .sort_values(["user_id", "timestamp"])
    .to_string(index=False)
)

# ----------------------------------------------------------------------
# 3. Display every current-only transaction with session
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("ALL CURRENT-ONLY TRANSACTIONS")
print("=" * 70)

current_only_display = [
    "event_id",
    "timestamp",
    "user_id",
    "device_id",
    "session_id",
    "event_type",
    "modality",
    "mobile_money_platform",
    "session_type",
    "transaction_type",
    "transaction_amount",
    "new_beneficiary",
    "window_id",
    "horizon_minutes",
    "hard_negative",
]

print(
    current_only_tx[current_only_display]
    .sort_values(["user_id", "timestamp"])
    .to_string(index=False)
)

# ----------------------------------------------------------------------
# 4. Print complete sessions containing missing authoritative transactions
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("SESSIONS CONTAINING MISSING AUTHORITATIVE TRANSACTIONS")
print("=" * 70)

for _, tx in missing_auth_tx.sort_values("timestamp").iterrows():

    user = tx["user_id"]
    sid = tx["session_id"]

    session = authoritative_events_71d5f[
        (authoritative_events_71d5f["user_id"] == user) &
        (authoritative_events_71d5f["session_id"] == sid)
    ].sort_values("timestamp")

    print("\n" + "-" * 70)
    print(
        f"AUTH SESSION | USER={user} | SESSION={sid}"
    )
    print(
        f"MISSING TRANSACTION={tx['event_id']} | "
        f"{tx['transaction_type']} | "
        f"{tx['transaction_amount']}"
    )
    print("-" * 70)

    for _, r in session.iterrows():

        marker = (
            "  <<< MISSING FROM CURRENT"
            if r["event_id"] == tx["event_id"]
            else ""
        )

        print(
            f"{r['event_id']} | "
            f"{r['timestamp']} | "
            f"{r['event_type']} | "
            f"{r['modality']} | "
            f"{r['mobile_money_platform']} | "
            f"{r['transaction_type']} | "
            f"{r['transaction_amount']}"
            f"{marker}"
        )

# ----------------------------------------------------------------------
# 5. Print complete sessions containing current-only transactions
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("SESSIONS CONTAINING CURRENT-ONLY TRANSACTIONS")
print("=" * 70)

for _, tx in current_only_tx.sort_values("timestamp").iterrows():

    user = tx["user_id"]
    sid = tx["session_id"]

    session = current_events_71d5f[
        (current_events_71d5f["user_id"] == user) &
        (current_events_71d5f["session_id"] == sid)
    ].sort_values("timestamp")

    print("\n" + "-" * 70)
    print(
        f"CURRENT SESSION | USER={user} | SESSION={sid}"
    )
    print(
        f"CURRENT-ONLY TRANSACTION={tx['event_id']} | "
        f"{tx['transaction_type']} | "
        f"{tx['transaction_amount']}"
    )
    print("-" * 70)

    for _, r in session.iterrows():

        marker = (
            "  <<< CURRENT-ONLY"
            if r["event_id"] == tx["event_id"]
            else ""
        )

        print(
            f"{r['event_id']} | "
            f"{r['timestamp']} | "
            f"{r['event_type']} | "
            f"{r['modality']} | "
            f"{r['mobile_money_platform']} | "
            f"{r['transaction_type']} | "
            f"{r['transaction_amount']}"
            f"{marker}"
        )

# ----------------------------------------------------------------------
# 6. Test whether missing/current-only transactions form a paired
#    transformation by USER + temporal position
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("TRANSACTION TEMPORAL PROXIMITY TEST")
print("=" * 70)

for user in sorted(
    set(missing_auth_tx["user_id"]) |
    set(current_only_tx["user_id"])
):

    a = missing_auth_tx[
        missing_auth_tx["user_id"] == user
    ].sort_values("timestamp")

    c = current_only_tx[
        current_only_tx["user_id"] == user
    ].sort_values("timestamp")

    print(f"\nUSER: {user}")

    print("\nMissing authoritative transactions:")

    for _, r in a.iterrows():
        print(
            f"  {r['event_id']} | "
            f"{r['timestamp']} | "
            f"{r['transaction_type']} | "
            f"{r['transaction_amount']} | "
            f"{r['session_id']}"
        )

    print("\nCurrent-only transactions:")

    for _, r in c.iterrows():
        print(
            f"  {r['event_id']} | "
            f"{r['timestamp']} | "
            f"{r['transaction_type']} | "
            f"{r['transaction_amount']} | "
            f"{r['session_id']}"
        )

# ----------------------------------------------------------------------
# 7. Compare transaction counts by user
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("TRANSACTION COUNT RECONCILIATION BY USER")
print("=" * 70)

users = sorted(
    set(authoritative_events_71d5f["user_id"]) |
    set(current_events_71d5f["user_id"])
)

rows = []

for user in users:

    a = int(
        (authoritative_events_71d5f["user_id"] == user)
        .__and__(
            authoritative_events_71d5f["event_type"] == "TRANSACTION"
        ).sum()
    )

    c = int(
        (current_events_71d5f["user_id"] == user)
        .__and__(
            current_events_71d5f["event_type"] == "TRANSACTION"
        ).sum()
    )

    if a != c:

        rows.append({
            "user_id": user,
            "authoritative_transactions": a,
            "current_transactions": c,
            "delta": c - a
        })

print(
    pd.DataFrame(rows)
    .sort_values("user_id")
    .to_string(index=False)
)

# ----------------------------------------------------------------------
# 8. Final status
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("STAGE 17 COMPLETE")
print("=" * 70)

print(
    f"Missing authoritative transactions: {len(missing_auth_tx)}"
)

print(
    f"Current-only transactions:           {len(current_only_tx)}"
)

print("""
Do NOT repair any transaction records yet.

The objective is to determine whether the missing and current-only
transactions represent a systematic transformation, reassignment,
session reconstruction effect, or independent data mutation.
""")

# ==============================================================================
# NOTEBOOK CELL 627
# ==============================================================================

# ======================================================================
# 71D.5F STAGE 18: SESSION PROVENANCE MAPPING
# ======================================================================

import pandas as pd
import numpy as np

print("=" * 70)
print("71D.5F STAGE 18: SESSION PROVENANCE MAPPING")
print("=" * 70)

# ----------------------------------------------------------------------
# 1. Build normalized session signatures
# ----------------------------------------------------------------------

def build_session_signature(df):

    rows = []

    for (user, session), g in df.groupby(
        ["user_id", "session_id"],
        sort=False
    ):

        g = g.sort_values("timestamp")

        event_types = tuple(g["event_type"].astype(str))

        platforms = tuple(
            g["mobile_money_platform"].astype(str)
        )

        modalities = tuple(
            g["modality"].astype(str)
        )

        transaction_types = tuple(
            g["transaction_type"]
            .fillna("NONE")
            .astype(str)
        )

        transaction_amounts = tuple(
            g["transaction_amount"]
            .fillna("NONE")
            .astype(str)
        )

        rows.append({
            "user_id": user,
            "session_id": session,
            "n_events": len(g),
            "event_types": event_types,
            "platforms": platforms,
            "modalities": modalities,
            "transaction_types": transaction_types,
            "transaction_amounts": transaction_amounts,
            "start_time": g["timestamp"].min(),
            "end_time": g["timestamp"].max(),
        })

    return pd.DataFrame(rows)


auth_sessions = build_session_signature(
    authoritative_events_71d5f
)

curr_sessions = build_session_signature(
    current_events_71d5f
)

# ----------------------------------------------------------------------
# 2. Identify sessions containing missing authoritative transactions
# ----------------------------------------------------------------------

missing_auth_session_ids = (
    missing_auth_tx[
        ["user_id", "session_id"]
    ]
    .drop_duplicates()
)

print("\n" + "=" * 70)
print("MISSING AUTHORITATIVE TRANSACTION SESSIONS")
print("=" * 70)

print(
    missing_auth_session_ids.to_string(index=False)
)

# ----------------------------------------------------------------------
# 3. Exact session-signature matching within same user
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("EXACT SESSION SIGNATURE SEARCH")
print("=" * 70)

for _, target in missing_auth_session_ids.iterrows():

    user = target["user_id"]
    sid = target["session_id"]

    a = auth_sessions[
        (auth_sessions["user_id"] == user) &
        (auth_sessions["session_id"] == sid)
    ].iloc[0]

    candidates = curr_sessions[
        curr_sessions["user_id"] == user
    ].copy()

    exact = candidates[
        candidates["event_types"].apply(
            lambda x: x == a["event_types"]
        )
    ]

    print("\n" + "-" * 70)
    print(f"AUTH SESSION: {user} / {sid}")
    print(
        f"Events: {a['n_events']} | "
        f"Sequence: {a['event_types']}"
    )

    if len(exact):

        print("EXACT CURRENT SESSION MATCHES:")

        print(
            exact[
                [
                    "user_id",
                    "session_id",
                    "n_events",
                    "event_types",
                    "start_time"
                ]
            ].to_string(index=False)
        )

    else:

        print("EXACT CURRENT SESSION MATCH: NONE")

# ----------------------------------------------------------------------
# 4. Find nearest current session by event-type edit distance
# ----------------------------------------------------------------------

def levenshtein(a, b):

    n = len(a)
    m = len(b)

    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = i

    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):

        for j in range(1, m + 1):

            cost = 0 if a[i - 1] == b[j - 1] else 1

            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost
            )

    return dp[n][m]


print("\n" + "=" * 70)
print("NEAREST CURRENT SESSION SEARCH")
print("=" * 70)

nearest_rows = []

for _, target in missing_auth_session_ids.iterrows():

    user = target["user_id"]
    sid = target["session_id"]

    a = auth_sessions[
        (auth_sessions["user_id"] == user) &
        (auth_sessions["session_id"] == sid)
    ].iloc[0]

    candidates = curr_sessions[
        curr_sessions["user_id"] == user
    ].copy()

    for _, c in candidates.iterrows():

        dist = levenshtein(
            a["event_types"],
            c["event_types"]
        )

        nearest_rows.append({
            "user_id": user,
            "auth_session": sid,
            "current_session": c["session_id"],
            "auth_events": a["n_events"],
            "current_events": c["n_events"],
            "edit_distance": dist,
            "auth_sequence": a["event_types"],
            "current_sequence": c["event_types"],
            "auth_start": a["start_time"],
            "current_start": c["start_time"],
        })


nearest_df = pd.DataFrame(nearest_rows)

nearest_df = nearest_df.sort_values(
    [
        "user_id",
        "auth_session",
        "edit_distance",
        "current_start"
    ]
)

print(
    nearest_df.groupby(
        ["user_id", "auth_session"],
        as_index=False
    ).head(3).to_string(index=False)
)

# ----------------------------------------------------------------------
# 5. Determine whether missing transaction sessions have structural
#    counterparts with the same session length and platform
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("STRUCTURAL COUNTERPART TEST")
print("=" * 70)

for _, target in missing_auth_session_ids.iterrows():

    user = target["user_id"]
    sid = target["session_id"]

    a = auth_sessions[
        (auth_sessions["user_id"] == user) &
        (auth_sessions["session_id"] == sid)
    ].iloc[0]

    candidates = curr_sessions[
        (curr_sessions["user_id"] == user) &
        (curr_sessions["n_events"] == a["n_events"])
    ].copy()

    print("\n" + "-" * 70)
    print(f"{user} / {sid}")
    print(
        f"Authoritative length={a['n_events']}"
    )

    if len(candidates):

        print(
            candidates[
                [
                    "session_id",
                    "n_events",
                    "event_types",
                    "platforms",
                    "start_time"
                ]
            ].to_string(index=False)
        )

    else:

        print(
            "NO CURRENT SESSION WITH SAME USER + SESSION LENGTH"
        )

# ----------------------------------------------------------------------
# 6. Check temporal neighborhood around each missing session
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("TEMPORAL NEIGHBORHOOD TEST")
print("=" * 70)

for _, target in missing_auth_session_ids.iterrows():

    user = target["user_id"]
    sid = target["session_id"]

    a = auth_sessions[
        (auth_sessions["user_id"] == user) &
        (auth_sessions["session_id"] == sid)
    ].iloc[0]

    t = pd.Timestamp(a["start_time"])

    candidates = curr_sessions[
        curr_sessions["user_id"] == user
    ].copy()

    candidates["time_distance_seconds"] = (
        candidates["start_time"] - t
    ).abs().dt.total_seconds()

    print("\n" + "-" * 70)
    print(f"{user} / {sid}")

    print(
        candidates.sort_values(
            "time_distance_seconds"
        )[
            [
                "session_id",
                "start_time",
                "n_events",
                "event_types",
                "time_distance_seconds"
            ]
        ].head(5).to_string(index=False)
    )

# ----------------------------------------------------------------------
# 7. Final diagnostic
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("STAGE 18 COMPLETE")
print("=" * 70)

print("""
Interpretation:

1. EXACT MATCH:
   The authoritative session exists in current under another session ID.

2. NEAREST STRUCTURAL MATCH:
   The session may have been reconstructed/transformed.

3. NO STRUCTURAL OR TEMPORAL MATCH:
   The authoritative session is genuinely absent.

Do not repair anything yet.
""")

# ==============================================================================
# NOTEBOOK CELL 628
# ==============================================================================

# ======================================================================
# 71D.5F STAGE 19: GLOBAL POPULATION RECONCILIATION
# ======================================================================

import pandas as pd
import numpy as np

print("=" * 70)
print("71D.5F STAGE 19: GLOBAL POPULATION RECONCILIATION")
print("=" * 70)

# ----------------------------------------------------------------------
# 1. GLOBAL EVENT-TYPE RECONCILIATION
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("GLOBAL EVENT-TYPE RECONCILIATION")
print("=" * 70)

auth_event_counts = (
    authoritative_events_71d5f["event_type"]
    .value_counts()
)

curr_event_counts = (
    current_events_71d5f["event_type"]
    .value_counts()
)

event_types = sorted(
    set(auth_event_counts.index) |
    set(curr_event_counts.index)
)

event_rows = []

for et in event_types:

    a = int(auth_event_counts.get(et, 0))
    c = int(curr_event_counts.get(et, 0))

    event_rows.append({
        "event_type": et,
        "authoritative": a,
        "current": c,
        "delta": c - a
    })

event_recon = pd.DataFrame(event_rows)

print(
    event_recon.to_string(index=False)
)

print(
    "\nTOTAL AUTHORITATIVE:",
    len(authoritative_events_71d5f)
)

print(
    "TOTAL CURRENT:",
    len(current_events_71d5f)
)

print(
    "NET DELTA:",
    len(current_events_71d5f) -
    len(authoritative_events_71d5f)
)

# ----------------------------------------------------------------------
# 2. GLOBAL MODALITY RECONCILIATION
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("GLOBAL MODALITY RECONCILIATION")
print("=" * 70)

auth_mod = authoritative_events_71d5f["modality"].value_counts()
curr_mod = current_events_71d5f["modality"].value_counts()

modalities = sorted(
    set(auth_mod.index) |
    set(curr_mod.index)
)

mod_rows = []

for m in modalities:

    a = int(auth_mod.get(m, 0))
    c = int(curr_mod.get(m, 0))

    mod_rows.append({
        "modality": m,
        "authoritative": a,
        "current": c,
        "delta": c - a
    })

print(
    pd.DataFrame(mod_rows).to_string(index=False)
)

# ----------------------------------------------------------------------
# 3. GLOBAL SESSION-LENGTH DISTRIBUTION
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("GLOBAL SESSION LENGTH DISTRIBUTION")
print("=" * 70)

auth_lengths = (
    authoritative_events_71d5f
    .groupby(["user_id", "session_id"])
    .size()
    .value_counts()
    .sort_index()
)

curr_lengths = (
    current_events_71d5f
    .groupby(["user_id", "session_id"])
    .size()
    .value_counts()
    .sort_index()
)

lengths = sorted(
    set(auth_lengths.index) |
    set(curr_lengths.index)
)

length_rows = []

for n in lengths:

    a = int(auth_lengths.get(n, 0))
    c = int(curr_lengths.get(n, 0))

    length_rows.append({
        "events_per_session": n,
        "authoritative_sessions": a,
        "current_sessions": c,
        "delta_sessions": c - a
    })

print(
    pd.DataFrame(length_rows).to_string(index=False)
)

print(
    "\nAUTHORITATIVE SESSION COUNT:",
    authoritative_events_71d5f[
        ["user_id", "session_id"]
    ].drop_duplicates().shape[0]
)

print(
    "CURRENT SESSION COUNT:",
    current_events_71d5f[
        ["user_id", "session_id"]
    ].drop_duplicates().shape[0]
)

# ----------------------------------------------------------------------
# 4. GLOBAL TRANSACTION RECONCILIATION
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("GLOBAL TRANSACTION RECONCILIATION")
print("=" * 70)

auth_tx_count = int(
    (
        authoritative_events_71d5f["event_type"]
        == "TRANSACTION"
    ).sum()
)

curr_tx_count = int(
    (
        current_events_71d5f["event_type"]
        == "TRANSACTION"
    ).sum()
)

print(
    "Authoritative transactions:",
    auth_tx_count
)

print(
    "Current transactions:",
    curr_tx_count
)

print(
    "Transaction delta:",
    curr_tx_count - auth_tx_count
)

print(
    "Authoritative transactions absent:",
    len(missing_auth_tx)
)

print(
    "Current-only transactions:",
    len(current_only_tx)
)

print(
    "Transaction conservation equation:"
)

print(
    f"{auth_tx_count} - {len(missing_auth_tx)} "
    f"+ {len(current_only_tx)} = "
    f"{auth_tx_count - len(missing_auth_tx) + len(current_only_tx)}"
)

# ----------------------------------------------------------------------
# 5. GLOBAL USER POPULATION RECONCILIATION
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("GLOBAL USER EVENT RECONCILIATION")
print("=" * 70)

auth_user_counts = (
    authoritative_events_71d5f
    .groupby("user_id")
    .size()
    .rename("authoritative")
)

curr_user_counts = (
    current_events_71d5f
    .groupby("user_id")
    .size()
    .rename("current")
)

user_recon = pd.concat(
    [auth_user_counts, curr_user_counts],
    axis=1
).fillna(0)

user_recon["authoritative"] = (
    user_recon["authoritative"].astype(int)
)

user_recon["current"] = (
    user_recon["current"].astype(int)
)

user_recon["delta"] = (
    user_recon["current"] -
    user_recon["authoritative"]
)

print(
    user_recon[
        user_recon["delta"] != 0
    ].sort_values("delta").to_string()
)

print(
    "\nUsers with zero event delta:",
    int((user_recon["delta"] == 0).sum())
)

print(
    "Users with non-zero event delta:",
    int((user_recon["delta"] != 0).sum())
)

# ----------------------------------------------------------------------
# 6. GLOBAL WINDOW EVENT RECONCILIATION
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("WINDOW-LEVEL EVENT RECONCILIATION")
print("=" * 70)

auth_window_counts = (
    authoritative_events_71d5f
    .groupby("window_id")
    .size()
    .rename("authoritative_events")
)

curr_window_counts = (
    current_events_71d5f
    .groupby("window_id")
    .size()
    .rename("current_events")
)

window_recon = pd.concat(
    [auth_window_counts, curr_window_counts],
    axis=1
).fillna(0)

window_recon["authoritative_events"] = (
    window_recon["authoritative_events"].astype(int)
)

window_recon["current_events"] = (
    window_recon["current_events"].astype(int)
)

window_recon["delta"] = (
    window_recon["current_events"] -
    window_recon["authoritative_events"]
)

print(
    "Authoritative windows:",
    len(auth_window_counts)
)

print(
    "Current windows:",
    len(curr_window_counts)
)

print(
    "Windows with non-zero event delta:",
    int((window_recon["delta"] != 0).sum())
)

print(
    "Total positive window deltas:",
    int(
        window_recon.loc[
            window_recon["delta"] > 0,
            "delta"
        ].sum()
    )
)

print(
    "Total negative window deltas:",
    int(
        window_recon.loc[
            window_recon["delta"] < 0,
            "delta"
        ].sum()
    )
)

# ----------------------------------------------------------------------
# 7. GROUND-TRUTH / ATTACK CONSERVATION
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("GROUND-TRUTH / ATTACK RECONCILIATION")
print("=" * 70)

for col in [
    "ground_truth_state",
    "is_attack",
    "hard_negative",
    "is_observable_precursor"
]:

    print(f"\nCOLUMN: {col}")

    a = (
        authoritative_events_71d5f[col]
        .value_counts(dropna=False)
        .rename("authoritative")
    )

    c = (
        current_events_71d5f[col]
        .value_counts(dropna=False)
        .rename("current")
    )

    r = pd.concat([a, c], axis=1).fillna(0)

    r["delta"] = r["current"] - r["authoritative"]

    print(
        r.to_string()
    )

# ----------------------------------------------------------------------
# 8. FINAL GLOBAL BALANCE
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("FINAL GLOBAL BALANCE")
print("=" * 70)

print(
    "EVENT BALANCE:",
    len(current_events_71d5f) -
    len(authoritative_events_71d5f)
)

print(
    "EXPECTED EVENT BALANCE: +31"
)

print(
    "TRANSACTION BALANCE:",
    curr_tx_count - auth_tx_count
)

print(
    "EXPECTED TRANSACTION BALANCE:",
    -2
)

print(
    "WINDOW COUNT BALANCE:",
    len(curr_window_counts) -
    len(auth_window_counts)
)

print(
    "SESSION COUNT BALANCE:",
    len(
        current_events_71d5f[
            ["user_id", "session_id"]
        ].drop_duplicates()
    )
    -
    len(
        authoritative_events_71d5f[
            ["user_id", "session_id"]
        ].drop_duplicates()
    )
)

print("\n" + "=" * 70)
print("STAGE 19 COMPLETE")
print("=" * 70)

print("""
NO DATA HAS BEEN MODIFIED.

If all global balances reconcile and the remaining differences can be
expressed as deterministic population transformations, the forensic
reconciliation can be considered complete.

If any conservation equation fails, we continue forensic tracing.
""")

# ==============================================================================
# NOTEBOOK CELL 629
# ==============================================================================

# ======================================================================
# 71D.5F STAGE 20: FORENSIC FINDINGS FREEZE
# ======================================================================

print("=" * 70)
print("71D.5F STAGE 20: FORENSIC FINDINGS FREEZE")
print("=" * 70)

# ----------------------------------------------------------------------
# 1. Core population summary
# ----------------------------------------------------------------------

forensic_summary_71d5f = {
    "authoritative_events": len(authoritative_events_71d5f),
    "current_events": len(current_events_71d5f),

    "event_delta": (
        len(current_events_71d5f)
        - len(authoritative_events_71d5f)
    ),

    "authoritative_windows": (
        authoritative_events_71d5f["window_id"]
        .nunique()
    ),

    "current_windows": (
        current_events_71d5f["window_id"]
        .nunique()
    ),

    "authoritative_sessions": (
        authoritative_events_71d5f[
            ["user_id", "session_id"]
        ].drop_duplicates().shape[0]
    ),

    "current_sessions": (
        current_events_71d5f[
            ["user_id", "session_id"]
        ].drop_duplicates().shape[0]
    ),

    "authoritative_transactions": (
        authoritative_events_71d5f["event_type"]
        .eq("TRANSACTION")
        .sum()
    ),

    "current_transactions": (
        current_events_71d5f["event_type"]
        .eq("TRANSACTION")
        .sum()
    ),

    "missing_authoritative_transactions": len(missing_auth_tx),

    "current_only_transactions": len(current_only_tx),

    "affected_users": int(
        (user_recon["delta"] != 0).sum()
    ),

    "unaffected_users": int(
        (user_recon["delta"] == 0).sum()
    ),

    "forensic_status": "COMPLETE",
}

# ----------------------------------------------------------------------
# 2. Event-type deltas
# ----------------------------------------------------------------------

forensic_summary_71d5f["event_type_deltas"] = (
    event_recon
    .set_index("event_type")["delta"]
    .to_dict()
)

# ----------------------------------------------------------------------
# 3. Modality deltas
# ----------------------------------------------------------------------

modality_recon = pd.DataFrame(mod_rows)

forensic_summary_71d5f["modality_deltas"] = (
    modality_recon
    .set_index("modality")["delta"]
    .to_dict()
)

# ----------------------------------------------------------------------
# 4. Affected-user deltas
# ----------------------------------------------------------------------

forensic_summary_71d5f["affected_user_deltas"] = (
    user_recon[
        user_recon["delta"] != 0
    ]["delta"]
    .to_dict()
)

# ----------------------------------------------------------------------
# 5. Conservation equations
# ----------------------------------------------------------------------

forensic_summary_71d5f["event_conservation"] = (
    f"{len(authoritative_events_71d5f)} + "
    f"{len(current_events_71d5f) - len(authoritative_events_71d5f)} "
    f"= {len(current_events_71d5f)}"
)

forensic_summary_71d5f["transaction_conservation"] = (
    f"{len(authoritative_events_71d5f[authoritative_events_71d5f['event_type'].eq('TRANSACTION')])} - "
    f"{len(missing_auth_tx)} + "
    f"{len(current_only_tx)} = "
    f"{len(current_events_71d5f[current_events_71d5f['event_type'].eq('TRANSACTION')])}"
)

forensic_summary_71d5f["menu_transaction_balance"] = (
    "+33 MENU_INTERACTION - 2 TRANSACTION = +31 EVENTS"
)

# ----------------------------------------------------------------------
# 6. Label conservation
# ----------------------------------------------------------------------

label_columns = [
    "ground_truth_state",
    "is_attack",
    "hard_negative",
    "is_observable_precursor"
]

label_checks = {}

for col in label_columns:

    auth_values = (
        authoritative_events_71d5f[col]
        .value_counts(dropna=False)
        .to_dict()
    )

    curr_values = (
        current_events_71d5f[col]
        .value_counts(dropna=False)
        .to_dict()
    )

    label_checks[col] = {
        "authoritative": auth_values,
        "current": curr_values,
        "identical": auth_values == curr_values
    }

forensic_summary_71d5f["label_conservation"] = label_checks

# ----------------------------------------------------------------------
# 7. Print frozen summary
# ----------------------------------------------------------------------

print("\nCORE FORENSIC SUMMARY")
print("-" * 70)

for key, value in forensic_summary_71d5f.items():

    if isinstance(value, dict):

        print(f"\n{key}:")

        for k, v in value.items():
            print(f"  {k}: {v}")

    else:

        print(f"{key}: {value}")

# ----------------------------------------------------------------------
# 8. Assertions — NO SILENT PASSING
# ----------------------------------------------------------------------

assert (
    forensic_summary_71d5f["authoritative_events"] == 1029
)

assert (
    forensic_summary_71d5f["current_events"] == 1060
)

assert (
    forensic_summary_71d5f["event_delta"] == 31
)

assert (
    forensic_summary_71d5f["authoritative_windows"] == 100
)

assert (
    forensic_summary_71d5f["current_windows"] == 100
)

assert (
    forensic_summary_71d5f["authoritative_sessions"] == 100
)

assert (
    forensic_summary_71d5f["current_sessions"] == 100
)

assert (
    forensic_summary_71d5f["authoritative_transactions"] == 49
)

assert (
    forensic_summary_71d5f["current_transactions"] == 47
)

assert (
    len(missing_auth_tx) == 9
)

assert (
    len(current_only_tx) == 7
)

assert (
    event_recon.loc[
        event_recon["event_type"] == "MENU_INTERACTION",
        "delta"
    ].iloc[0] == 33
)

assert (
    event_recon.loc[
        event_recon["event_type"] == "TRANSACTION",
        "delta"
    ].iloc[0] == -2
)

for col in label_columns:

    assert (
        label_checks[col]["identical"] is True
    )

print("\n" + "=" * 70)
print("ALL FORENSIC ASSERTIONS PASSED")
print("=" * 70)

print("""
71D.5F FORENSIC STATE IS FROZEN.

No source dataframe was modified.
No event was repaired.
No session was renamed.
No window was reassigned.
No transaction was fabricated.

The discrepancy has been fully characterized at the
event, transaction, session, user, window, modality,
and label-population levels.
""")

# ==============================================================================
# NOTEBOOK CELL 630
# ==============================================================================

# ======================================================================
# 71D.5F STAGE 20A: CORRECTED LABEL SEMANTIC VALIDATION
# ======================================================================

print("=" * 70)
print("71D.5F STAGE 20A: CORRECTED LABEL SEMANTIC VALIDATION")
print("=" * 70)

label_semantic_checks_71d5f = {}

label_columns = [
    "ground_truth_state",
    "is_attack",
    "hard_negative",
    "is_observable_precursor"
]

for col in label_columns:

    auth_values = set(
        authoritative_events_71d5f[col]
        .dropna()
        .unique()
    )

    curr_values = set(
        current_events_71d5f[col]
        .dropna()
        .unique()
    )

    identical_value_domain = (
        auth_values == curr_values
    )

    label_semantic_checks_71d5f[col] = {
        "authoritative_values": sorted(
            list(auth_values),
            key=str
        ),
        "current_values": sorted(
            list(curr_values),
            key=str
        ),
        "identical_value_domain":
            identical_value_domain
    }

    print(f"\nCOLUMN: {col}")
    print(
        "Authoritative values:",
        sorted(list(auth_values), key=str)
    )
    print(
        "Current values:",
        sorted(list(curr_values), key=str)
    )
    print(
        "Identical semantic domain:",
        identical_value_domain
    )

# ----------------------------------------------------------------------
# Explicit semantic assertions
# ----------------------------------------------------------------------

assert (
    label_semantic_checks_71d5f[
        "ground_truth_state"
    ]["identical_value_domain"]
    is True
)

assert (
    label_semantic_checks_71d5f[
        "is_attack"
    ]["identical_value_domain"]
    is True
)

assert (
    label_semantic_checks_71d5f[
        "hard_negative"
    ]["identical_value_domain"]
    is True
)

assert (
    label_semantic_checks_71d5f[
        "is_observable_precursor"
    ]["identical_value_domain"]
    is True
)

# ----------------------------------------------------------------------
# Verify exact semantic state of ALL current events
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("CURRENT DATASET LABEL STATE")
print("=" * 70)

print(
    "\nground_truth_state:"
)

print(
    current_events_71d5f[
        "ground_truth_state"
    ].value_counts(dropna=False)
)

print(
    "\nis_attack:"
)

print(
    current_events_71d5f[
        "is_attack"
    ].value_counts(dropna=False)
)

print(
    "\nhard_negative:"
)

print(
    current_events_71d5f[
        "hard_negative"
    ].value_counts(dropna=False)
)

print(
    "\nis_observable_precursor:"
)

print(
    current_events_71d5f[
        "is_observable_precursor"
    ].value_counts(dropna=False)
)

# ----------------------------------------------------------------------
# Final semantic assertions
# ----------------------------------------------------------------------

assert (
    current_events_71d5f[
        "ground_truth_state"
    ].eq("NORMAL").all()
)

assert (
    current_events_71d5f[
        "is_attack"
    ].eq(0).all()
)

assert (
    current_events_71d5f[
        "hard_negative"
    ].eq(1).all()
)

assert (
    current_events_71d5f[
        "is_observable_precursor"
    ].eq(0).all()
)

print("\n" + "=" * 70)
print("STAGE 20A PASSED")
print("=" * 70)

print("""
LABEL SEMANTICS ARE CONSERVED.

The authoritative and current populations have the same
semantic label domain.

All current events are:
    ground_truth_state      = NORMAL
    is_attack               = 0
    hard_negative           = 1
    is_observable_precursor = 0

The frequency difference (1029 -> 1060) is expected because
the current population contains 31 additional events.

No source dataframe was modified.
""")

# ==============================================================================
# NOTEBOOK CELL 631
# ==============================================================================

# ======================================================================
# 71D.5F STAGE 20B: SAVE FORENSIC CHECKPOINT
# ======================================================================

import json
from pathlib import Path
from datetime import datetime

print("=" * 70)
print("71D.5F STAGE 20B: SAVE FORENSIC CHECKPOINT")
print("=" * 70)

# ----------------------------------------------------------------------
# 1. Build final frozen checkpoint
# ----------------------------------------------------------------------

checkpoint_71d5f = {
    "investigation": "71D.5F NON MATCHING WINDOW FORENSICS",

    "status": "COMPLETE",

    "checkpoint": "STAGE 20A",

    "timestamp": datetime.now().isoformat(),

    "population": {
        "authoritative_events": 1029,
        "current_events": 1060,
        "event_delta": 31,

        "authoritative_windows": 100,
        "current_windows": 100,

        "authoritative_sessions": 100,
        "current_sessions": 100,
    },

    "event_type_reconciliation": {
        "AUTHENTICATION_SUCCESS": 0,
        "MENU_INTERACTION": 33,
        "NEW_DEVICE_OBSERVED": 0,
        "SESSION_END": 0,
        "SESSION_START": 0,
        "TRANSACTION": -2,
        "USSD_INITIATION": 0,
        "USSD_RESPONSE": 0,
    },

    "modality_reconciliation": {
        "AUTHENTICATION": 0,
        "DEVICE": 0,
        "FINANCIAL": -2,
        "SESSION": 0,
        "USSD": 33,
    },

    "transaction_reconciliation": {
        "authoritative_transactions": 49,
        "missing_authoritative_transactions": 9,
        "current_only_transactions": 7,
        "current_transactions": 47,
        "equation": "49 - 9 + 7 = 47",
    },

    "affected_users": {
        "USER_00019": 6,
        "USER_00065": 6,
        "USER_00083": 5,
        "USER_00093": 14,
    },

    "unaffected_users": 16,

    "label_semantics": {
        "ground_truth_state": "NORMAL",
        "is_attack": 0,
        "hard_negative": 1,
        "is_observable_precursor": 0,
        "semantic_domain_conserved": True,
    },

    "structural_findings": {
        "event_population_same": False,
        "window_population_same": True,
        "session_population_same": True,
        "event_delta_explained": True,
        "transaction_delta_explained": True,
        "label_semantics_conserved": True,
        "one_to_one_event_mapping": False,
        "one_to_one_session_mapping": False,
    },

    "conservation": {
        "events": "1029 + 31 = 1060",
        "transactions": "49 - 9 + 7 = 47",
        "event_balance": "+33 MENU_INTERACTION - 2 TRANSACTION = +31",
        "sessions": "100 = 100",
        "windows": "100 = 100",
    },

    "source_data_modified": False,

    "repair_performed": False,

    "forensic_conclusion": (
        "The authoritative and current populations represent "
        "the same 100-window and 100-session population but differ "
        "through structural transformation of event composition "
        "within four users. The current population contains 31 "
        "additional events, consisting of 33 additional "
        "MENU_INTERACTION/USSD events offset by 2 fewer "
        "TRANSACTION/FINANCIAL events. Nine authoritative "
        "transactions are absent and seven current-only transactions "
        "are present. All current events remain NORMAL, non-attack, "
        "hard-negative and non-observable-precursor."
    )
}

# ----------------------------------------------------------------------
# 2. Save JSON checkpoint
# ----------------------------------------------------------------------

checkpoint_path = Path(
    "/mnt/data/71D5F_forensic_checkpoint_stage20A.json"
)

with open(
    checkpoint_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        checkpoint_71d5f,
        f,
        indent=4,
        default=str
    )

# ----------------------------------------------------------------------
# 3. Save compact text audit record
# ----------------------------------------------------------------------

audit_path = Path(
    "/mnt/data/71D5F_forensic_audit_stage20A.txt"
)

audit_text = f"""
======================================================================
71D.5F NON MATCHING WINDOW FORENSICS
FORENSIC AUDIT CHECKPOINT — STAGE 20A
======================================================================

STATUS
------
FORENSIC RECONCILIATION: COMPLETE
SOURCE DATA MODIFIED: NO
REPAIR PERFORMED: NO

POPULATION
----------
Authoritative events: 1029
Current events:       1060
Net event delta:      +31

Authoritative windows: 100
Current windows:       100

Authoritative sessions: 100
Current sessions:       100

EVENT-TYPE RECONCILIATION
-------------------------
MENU_INTERACTION:       +33
TRANSACTION:              -2
All other event types:    0

Balance:
+33 MENU_INTERACTION - 2 TRANSACTION = +31 EVENTS

MODALITY RECONCILIATION
-----------------------
USSD:       +33
FINANCIAL:   -2
All other modalities: 0

TRANSACTION RECONCILIATION
--------------------------
Authoritative transactions:          49
Missing authoritative transactions:   9
Current-only transactions:            7
Current transactions:                47

Conservation:
49 - 9 + 7 = 47

AFFECTED USERS
--------------
USER_00019: +6
USER_00065: +6
USER_00083: +5
USER_00093: +14

Total: +31

Unaffected users: 16

LABEL SEMANTICS
---------------
ground_truth_state      = NORMAL
is_attack               = 0
hard_negative           = 1
is_observable_precursor = 0

Label semantic domain conserved: YES

STRUCTURAL FINDINGS
-------------------
Same window population: YES
Same session population: YES
One-to-one event mapping: NO
One-to-one session mapping: NO

The discrepancy represents structural transformation of event
composition rather than a simple event-ID or session-ID mismatch.

FINAL CONCLUSION
----------------
The authoritative and current populations represent the same
100-window and 100-session population but differ through
structural transformation of event composition within four users.

The current population contains 31 additional events, consisting
of 33 additional MENU_INTERACTION/USSD events offset by 2 fewer
TRANSACTION/FINANCIAL events.

Nine authoritative transactions are absent and seven current-only
transactions are present.

All current events remain NORMAL, non-attack, hard-negative and
non-observable-precursor.

No source dataframe was modified.
No repair was performed.

======================================================================
END OF CHECKPOINT
======================================================================
"""

with open(
    audit_path,
    "w",
    encoding="utf-8"
) as f:

    f.write(audit_text.strip())

# ----------------------------------------------------------------------
# 4. Verify files exist
# ----------------------------------------------------------------------

assert checkpoint_path.exists()
assert audit_path.exists()

print("\nCHECKPOINT FILES SAVED")
print("-" * 70)

print(checkpoint_path)
print(audit_path)

print("\n" + "=" * 70)
print("STAGE 20B COMPLETE — FORENSIC STATE SAVED")
print("=" * 70)
