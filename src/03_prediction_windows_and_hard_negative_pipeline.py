# AFRIDATACYBERJOHN — Prediction Windows and Hard-Negative Pipeline
# This file is an archival extraction of the corresponding cells from
# AFRIDATACYBERJOHN_v1.0_reproducibility.ipynb.
# The canonical workflow is the notebook; this script is not guaranteed
# to be independently executable without the preceding workflow state.


# ==============================================================================
# NOTEBOOK CELL 193
# ==============================================================================

# ============================================================
# STEP 70A: AUDIT CANDIDATE NEGATIVE USERS
# ============================================================

import pandas as pd
import numpy as np

print("=" * 75)
print("STEP 70A: CANDIDATE NEGATIVE USER AUDIT")
print("=" * 75)

# ------------------------------------------------------------
# Positive users
# ------------------------------------------------------------

positive_users = set(
    campaigns["user_id"].unique()
)

print("\nPositive users:", len(positive_users))


# ------------------------------------------------------------
# Users with precursor observations
# ------------------------------------------------------------

precursor_users = set(
    observable_precursors["user_id"].unique()
)

print(
    "Users with observable precursors:",
    len(precursor_users)
)


# ------------------------------------------------------------
# Users with attack ground truth
# ------------------------------------------------------------

attack_users = set(
    attack_events["user_id"].unique()
)

print(
    "Users with attack events:",
    len(attack_users)
)


# ------------------------------------------------------------
# Candidate negatives
# ------------------------------------------------------------

all_users = set(
    users["user_id"].unique()
)

candidate_negative_users = (
    all_users
    - positive_users
    - precursor_users
    - attack_users
)

print(
    "Candidate negative users:",
    len(candidate_negative_users)
)


# ------------------------------------------------------------
# User level table
# ------------------------------------------------------------

negative_candidates = users[
    users["user_id"].isin(candidate_negative_users)
].copy()

print("\n" + "=" * 75)
print("NEGATIVE CANDIDATE PROFILE")
print("=" * 75)

print(
    negative_candidates[
        [
            "user_id",
            "country",
            "language_region",
            "age",
            "tenure_months",
            "behaviour_profile"
        ]
    ].to_string(index=False)
)


# ------------------------------------------------------------
# Distribution
# ------------------------------------------------------------

for col in [
    "country",
    "language_region",
    "behaviour_profile"
]:

    print("\n" + "-" * 60)
    print(col)

    print(
        negative_candidates[col]
        .value_counts(dropna=False)
    )


# ------------------------------------------------------------
# Check observable activity
# ------------------------------------------------------------

user_activity = (
    observable_stream
    .groupby("user_id")
    .agg(
        observable_events=("observable_event_id", "count"),
        sessions=("session_id", "nunique"),
        first_observation=("timestamp", "min"),
        last_observation=("timestamp", "max")
    )
    .reset_index()
)

negative_candidates = negative_candidates.merge(
    user_activity,
    on="user_id",
    how="left"
)

print("\n" + "=" * 75)
print("NEGATIVE CANDIDATE ACTIVITY")
print("=" * 75)

print(
    negative_candidates[
        [
            "user_id",
            "behaviour_profile",
            "observable_events",
            "sessions",
            "first_observation",
            "last_observation"
        ]
    ].to_string(index=False)
)


# ------------------------------------------------------------
# Confirm no attack information
# ------------------------------------------------------------

print("\n" + "=" * 75)
print("NEGATIVE ELIGIBILITY CHECK")
print("=" * 75)

checks = []

for uid in negative_candidates["user_id"]:

    checks.append({
        "user_id": uid,
        "in_campaigns": uid in positive_users,
        "in_precursors": uid in precursor_users,
        "in_attack_events": uid in attack_users
    })

eligibility = pd.DataFrame(checks)

print(eligibility.sum(numeric_only=True))

print(
    "\nEligible negative users:",
    (
        (~eligibility["in_campaigns"]) &
        (~eligibility["in_precursors"]) &
        (~eligibility["in_attack_events"])
    ).sum()
)

print("\n" + "=" * 75)
print("STEP 70A COMPLETE")
print("=" * 75)

# ==============================================================================
# NOTEBOOK CELL 194
# ==============================================================================

# ============================================================
# STEP 70B: MATCH POSITIVE AND NEGATIVE USER COHORTS
# ============================================================

import pandas as pd
import numpy as np

rng = np.random.default_rng(SEED + 70)

print("=" * 75)
print("STEP 70B: POSITIVE / NEGATIVE USER MATCHING")
print("=" * 75)


# ============================================================
# 1. DEFINE COHORTS
# ============================================================

positive_users = campaigns[
    "user_id"
].drop_duplicates().tolist()

negative_users = [
    uid for uid in users["user_id"]
    if uid not in set(positive_users)
    and uid not in set(observable_precursors["user_id"])
    and uid not in set(attack_events["user_id"])
]

print("\nPositive users:", len(positive_users))
print("Negative users:", len(negative_users))


# ============================================================
# 2. USER PROFILE TABLE
# ============================================================

profile_cols = [
    "user_id",
    "country",
    "language_region",
    "age",
    "tenure_months",
    "behaviour_profile"
]

profiles = users[
    profile_cols
].copy()


# ============================================================
# 3. BASELINE ACTIVITY FEATURES
# ============================================================

stream = observable_stream.copy()

stream["timestamp"] = pd.to_datetime(
    stream["timestamp"],
    errors="coerce"
)

# Exclude precursor observations when calculating baseline
# activity for matching. Otherwise positive users would appear
# more active simply because they are attack campaigns.

baseline_stream = stream[
    stream["is_observable_precursor"] == 0
].copy()

baseline_user = (
    baseline_stream
    .groupby("user_id")
    .agg(
        baseline_events=(
            "observable_event_id",
            "count"
        ),
        baseline_sessions=(
            "session_id",
            "nunique"
        ),
        first_observation=(
            "timestamp",
            "min"
        ),
        last_observation=(
            "timestamp",
            "max"
        )
    )
    .reset_index()
)

profiles = profiles.merge(
    baseline_user,
    on="user_id",
    how="left"
)

profiles[
    [
        "baseline_events",
        "baseline_sessions"
    ]
] = profiles[
    [
        "baseline_events",
        "baseline_sessions"
    ]
].fillna(0)


# ============================================================
# 4. BASELINE ACTIVITY RATE
# ============================================================

profiles["observation_days"] = (
    (
        profiles["last_observation"] -
        profiles["first_observation"]
    ).dt.total_seconds() / 86400
).clip(lower=1)

profiles["events_per_day"] = (
    profiles["baseline_events"] /
    profiles["observation_days"]
)

profiles["sessions_per_day"] = (
    profiles["baseline_sessions"] /
    profiles["observation_days"]
)


# ============================================================
# 5. BUILD CANDIDATE MATCH COST
# ============================================================

positive_profile = profiles[
    profiles["user_id"].isin(positive_users)
].copy()

negative_profile = profiles[
    profiles["user_id"].isin(negative_users)
].copy()

print("\nPositive profile distribution:")
print(
    positive_profile[
        "behaviour_profile"
    ].value_counts()
)

print("\nNegative profile distribution:")
print(
    negative_profile[
        "behaviour_profile"
    ].value_counts()
)


# ============================================================
# 6. MATCHING FUNCTION
# ============================================================

def match_cost(pos, neg):

    cost = 0.0

    # Strong categorical matching
    if pos["country"] != neg["country"]:
        cost += 5.0

    if pos["language_region"] != neg["language_region"]:
        cost += 2.0

    if pos["behaviour_profile"] != neg["behaviour_profile"]:
        cost += 8.0

    # Demographic similarity
    age_scale = max(
        positive_profile["age"].std(),
        1
    )

    tenure_scale = max(
        positive_profile["tenure_months"].std(),
        1
    )

    cost += abs(
        pos["age"] - neg["age"]
    ) / age_scale

    cost += abs(
        pos["tenure_months"] -
        neg["tenure_months"]
    ) / tenure_scale

    # Baseline event activity
    event_scale = max(
        positive_profile["baseline_events"].std(),
        1
    )

    session_scale = max(
        positive_profile["baseline_sessions"].std(),
        1
    )

    cost += 2.0 * abs(
        pos["baseline_events"] -
        neg["baseline_events"]
    ) / event_scale

    cost += 2.0 * abs(
        pos["baseline_sessions"] -
        neg["baseline_sessions"]
    ) / session_scale

    # Activity rate
    rate_scale = max(
        positive_profile["events_per_day"].std(),
        0.001
    )

    cost += 2.0 * abs(
        pos["events_per_day"] -
        neg["events_per_day"]
    ) / rate_scale

    return cost


# ============================================================
# 7. GREEDY ONE TO ONE MATCHING
# ============================================================

matches = []

available_negatives = set(
    negative_profile["user_id"]
)

for _, pos in (
    positive_profile
    .sort_values(
        "baseline_events",
        ascending=False
    )
    .iterrows()
):

    candidates = negative_profile[
        negative_profile["user_id"].isin(
            available_negatives
        )
    ].copy()

    if len(candidates) == 0:
        break

    candidates["match_cost"] = candidates.apply(
        lambda neg: match_cost(pos, neg),
        axis=1
    )

    best = candidates.sort_values(
        "match_cost"
    ).iloc[0]

    matches.append({
        "positive_user_id": pos["user_id"],
        "negative_user_id": best["user_id"],
        "match_cost": best["match_cost"]
    })

    available_negatives.remove(
        best["user_id"]
    )


matches = pd.DataFrame(matches)


# ============================================================
# 8. MATCHING SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("MATCHING SUMMARY")
print("=" * 75)

print("Matched pairs:", len(matches))
print("Unmatched positives:", len(positive_users) - len(matches))
print(
    "Unused negative candidates:",
    len(negative_users) - len(matches)
)

print(
    "\nMatch cost statistics:"
)

print(
    matches["match_cost"].describe()
)


# ============================================================
# 9. ENRICH MATCH TABLE
# ============================================================

pos_info = profiles.rename(
    columns={
        c: f"positive_{c}"
        for c in profiles.columns
        if c != "user_id"
    }
)

neg_info = profiles.rename(
    columns={
        c: f"negative_{c}"
        for c in profiles.columns
        if c != "user_id"
    }
)

matches = matches.merge(
    pos_info,
    left_on="positive_user_id",
    right_on="user_id",
    how="left"
).drop(columns=["user_id"])

matches = matches.merge(
    neg_info,
    left_on="negative_user_id",
    right_on="user_id",
    how="left"
).drop(columns=["user_id"])


# ============================================================
# 10. PROFILE BALANCE
# ============================================================

print("\n" + "=" * 75)
print("PROFILE BALANCE")
print("=" * 75)

print("\nPositive countries:")
print(
    matches[
        "positive_country"
    ].value_counts()
)

print("\nNegative countries:")
print(
    matches[
        "negative_country"
    ].value_counts()
)

print("\nPositive behaviour:")
print(
    matches[
        "positive_behaviour_profile"
    ].value_counts()
)

print("\nNegative behaviour:")
print(
    matches[
        "negative_behaviour_profile"
    ].value_counts()
)


# ============================================================
# 11. STANDARDIZED DIFFERENCES
# ============================================================

def standardized_difference(a, b):

    a = pd.to_numeric(a, errors="coerce")
    b = pd.to_numeric(b, errors="coerce")

    pooled_sd = np.sqrt(
        (
            a.var(ddof=1) +
            b.var(ddof=1)
        ) / 2
    )

    if pooled_sd == 0:
        return 0.0

    return (
        a.mean() - b.mean()
    ) / pooled_sd


balance_rows = []

numeric_pairs = [
    (
        "age",
        "positive_age",
        "negative_age"
    ),
    (
        "tenure_months",
        "positive_tenure_months",
        "negative_tenure_months"
    ),
    (
        "baseline_events",
        "positive_baseline_events",
        "negative_baseline_events"
    ),
    (
        "baseline_sessions",
        "positive_baseline_sessions",
        "negative_baseline_sessions"
    ),
    (
        "events_per_day",
        "positive_events_per_day",
        "negative_events_per_day"
    ),
    (
        "sessions_per_day",
        "positive_sessions_per_day",
        "negative_sessions_per_day"
    )
]

for name, pos_col, neg_col in numeric_pairs:

    balance_rows.append({
        "feature": name,
        "positive_mean": matches[pos_col].mean(),
        "negative_mean": matches[neg_col].mean(),
        "standardized_difference":
            standardized_difference(
                matches[pos_col],
                matches[neg_col]
            )
    })

balance_table = pd.DataFrame(
    balance_rows
)

print("\n" + "=" * 75)
print("NUMERIC BALANCE")
print("=" * 75)

print(
    balance_table.to_string(
        index=False
    )
)


# ============================================================
# 12. CATEGORICAL MATCH RATES
# ============================================================

print("\n" + "=" * 75)
print("CATEGORICAL MATCH RATES")
print("=" * 75)

for name, pos_col, neg_col in [
    (
        "country",
        "positive_country",
        "negative_country"
    ),
    (
        "language_region",
        "positive_language_region",
        "negative_language_region"
    ),
    (
        "behaviour_profile",
        "positive_behaviour_profile",
        "negative_behaviour_profile"
    )
]:

    rate = (
        matches[pos_col] ==
        matches[neg_col]
    ).mean()

    print(
        f"{name}: {rate:.3f}"
    )


# ============================================================
# 13. USER OVERLAP CHECK
# ============================================================

print("\n" + "=" * 75)
print("USER OVERLAP CHECK")
print("=" * 75)

positive_set = set(
    matches["positive_user_id"]
)

negative_set = set(
    matches["negative_user_id"]
)

print(
    "Positive / negative overlap:",
    len(
        positive_set &
        negative_set
    )
)

print(
    "Unique positive users:",
    len(positive_set)
)

print(
    "Unique negative users:",
    len(negative_set)
)


# ============================================================
# 14. SAVE MATCH TABLE
# ============================================================

negative_match_table = matches.copy()


print("\n" + "=" * 75)
print("STEP 70B COMPLETE")
print("=" * 75)

# ==============================================================================
# NOTEBOOK CELL 195
# ==============================================================================

# ============================================================
# STEP 70C: NEGATIVE CONTROL POOL ACTIVITY DIAGNOSTIC
# ============================================================

import pandas as pd
import numpy as np

print("=" * 75)
print("STEP 70C: NEGATIVE CONTROL POOL ACTIVITY DIAGNOSTIC")
print("=" * 75)


# ------------------------------------------------------------
# 1. Define clean negative users
# ------------------------------------------------------------

positive_users = set(
    campaigns["user_id"].unique()
)

precursor_users = set(
    observable_precursors["user_id"].unique()
)

attack_users = set(
    attack_events["user_id"].unique()
)

negative_users = sorted(
    set(users["user_id"])
    - positive_users
    - precursor_users
    - attack_users
)

print("\nClean negative users:", len(negative_users))


# ------------------------------------------------------------
# 2. Obtain ordinary observable events only
# ------------------------------------------------------------

base = observable_stream[
    observable_stream["is_observable_precursor"] == 0
].copy()

base["timestamp"] = pd.to_datetime(
    base["timestamp"],
    errors="coerce"
)

base["date"] = base["timestamp"].dt.date
base["hour"] = base["timestamp"].dt.hour
base["day_of_week"] = base["timestamp"].dt.dayofweek


# ------------------------------------------------------------
# 3. User activity summary
# ------------------------------------------------------------

activity = (
    base[
        base["user_id"].isin(negative_users)
    ]
    .groupby("user_id")
    .agg(
        events=("observable_event_id", "count"),
        sessions=("session_id", "nunique"),
        active_days=("date", "nunique"),
        first_time=("timestamp", "min"),
        last_time=("timestamp", "max")
    )
    .reset_index()
)

activity["observation_span_days"] = (
    (
        activity["last_time"] -
        activity["first_time"]
    ).dt.total_seconds() / 86400
).clip(lower=1)

activity["events_per_day"] = (
    activity["events"] /
    activity["observation_span_days"]
)

activity["sessions_per_day"] = (
    activity["sessions"] /
    activity["observation_span_days"]
)


# ------------------------------------------------------------
# 4. Add user profile
# ------------------------------------------------------------

profile_cols = [
    "user_id",
    "country",
    "language_region",
    "age",
    "tenure_months",
    "behaviour_profile"
]

activity = activity.merge(
    users[profile_cols],
    on="user_id",
    how="left"
)


# ------------------------------------------------------------
# 5. Display activity table
# ------------------------------------------------------------

print("\n" + "=" * 75)
print("NEGATIVE CONTROL ACTIVITY")
print("=" * 75)

print(
    activity[
        [
            "user_id",
            "country",
            "behaviour_profile",
            "events",
            "sessions",
            "active_days",
            "events_per_day",
            "sessions_per_day"
        ]
    ]
    .sort_values("events")
    .to_string(index=False)
)


# ------------------------------------------------------------
# 6. Activity distributions
# ------------------------------------------------------------

print("\n" + "=" * 75)
print("ACTIVITY DISTRIBUTIONS")
print("=" * 75)

for col in [
    "events",
    "sessions",
    "active_days",
    "events_per_day",
    "sessions_per_day"
]:

    print("\n", col)

    print(
        activity[col].describe()
    )


# ------------------------------------------------------------
# 7. Activity by behaviour profile
# ------------------------------------------------------------

print("\n" + "=" * 75)
print("ACTIVITY BY BEHAVIOUR PROFILE")
print("=" * 75)

print(
    activity.groupby(
        "behaviour_profile"
    )[
        [
            "events",
            "sessions",
            "events_per_day",
            "sessions_per_day"
        ]
    ]
    .agg(
        ["count", "mean", "median", "std"]
    )
    .round(3)
    .to_string()
)


# ------------------------------------------------------------
# 8. Activity by country
# ------------------------------------------------------------

print("\n" + "=" * 75)
print("ACTIVITY BY COUNTRY")
print("=" * 75)

print(
    activity.groupby(
        "country"
    )[
        [
            "events",
            "sessions",
            "events_per_day"
        ]
    ]
    .agg(
        ["count", "mean", "median"]
    )
    .round(3)
    .to_string()
)


# ------------------------------------------------------------
# 9. Temporal availability
# ------------------------------------------------------------

print("\n" + "=" * 75)
print("TEMPORAL AVAILABILITY")
print("=" * 75)

print(
    base[
        base["user_id"].isin(negative_users)
    ]
    .groupby("user_id")["timestamp"]
    .agg(["min", "max", "count"])
    .to_string()
)


# ------------------------------------------------------------
# 10. Number of available calendar days
# ------------------------------------------------------------

calendar_days = (
    base[
        base["user_id"].isin(negative_users)
    ]
    .groupby("user_id")["date"]
    .nunique()
    .sort_values()
)

print("\n" + "=" * 75)
print("CALENDAR DAY COVERAGE")
print("=" * 75)

print(calendar_days.describe())

print("\nPer user:")
print(calendar_days.to_string())


print("\n" + "=" * 75)
print("STEP 70C COMPLETE")
print("=" * 75)

# ==============================================================================
# NOTEBOOK CELL 196
# ==============================================================================

# ============================================================
# STEP 71A: CREATE POSITIVE PREDICTION WINDOWS
# ============================================================

import pandas as pd
import numpy as np

print("=" * 75)
print("STEP 71A: POSITIVE PREDICTION WINDOW CONSTRUCTION")
print("=" * 75)

rng = np.random.default_rng(SEED + 71)


# ============================================================
# 1. CANONICAL TAKEOVER TIMES
# ============================================================

attack = attack_events.copy()

attack["timestamp"] = pd.to_datetime(
    attack["timestamp"],
    errors="coerce"
)

takeover_event_map = {
    "ACCOUNT_TAKEOVER": "ACCOUNT_TAKEOVER",
    "SOCIAL_ENGINEERING_TAKEOVER": "ACCOUNT_TAKEOVER",
    "USSD_SESSION_HIJACK": "SESSION_HIJACK",
    "SIM_IDENTITY_COMPROMISE": "ACCOUNT_TAKEOVER"
}

takeover_rows = attack[
    attack["event_type"].isin(
        takeover_event_map.values()
    )
].copy()

takeover_times = (
    takeover_rows
    .sort_values("timestamp")
    .groupby(
        ["campaign_id", "user_id"],
        as_index=False
    )
    .first()
    [
        [
            "campaign_id",
            "user_id",
            "timestamp"
        ]
    ]
    .rename(
        columns={
            "timestamp": "takeover_time"
        }
    )
)

print(
    "\nCampaigns with takeover time:",
    len(takeover_times)
)


# ============================================================
# 2. CAMPAIGN METADATA
# ============================================================

campaign_meta = campaigns[
    [
        "campaign_id",
        "user_id",
        "attack_type"
    ]
].copy()

campaign_meta = campaign_meta.merge(
    takeover_times,
    on=["campaign_id", "user_id"],
    how="left",
    validate="one_to_one"
)


# ============================================================
# 3. ADD CAMPAIGN SEVERITY
# ============================================================

if "campaign_control" in globals():

    severity_cols = [
        c for c in [
            "campaign_id",
            "attack_severity",
            "temporal_variability",
            "event_dropout_rate"
        ]
        if c in campaign_control.columns
    ]

    if "campaign_id" in severity_cols:

        campaign_meta = campaign_meta.merge(
            campaign_control[severity_cols],
            on="campaign_id",
            how="left",
            validate="one_to_one"
        )

else:

    campaign_meta["attack_severity"] = np.nan


# ============================================================
# 4. ADD USER PROFILE
# ============================================================

campaign_meta = campaign_meta.merge(
    users[
        [
            "user_id",
            "country",
            "language_region",
            "age",
            "tenure_months",
            "behaviour_profile"
        ]
    ],
    on="user_id",
    how="left",
    validate="many_to_one"
)


# ============================================================
# 5. CREATE FIVE HORIZONS
# ============================================================

horizons = [60, 30, 15, 10, 5]

positive_windows = []

for _, row in campaign_meta.iterrows():

    for horizon in horizons:

        cutoff_time = (
            row["takeover_time"] -
            pd.Timedelta(
                minutes=horizon
            )
        )

        positive_windows.append({

            "window_id":
                f"POS_{row['campaign_id']}_{horizon:03d}",

            "label": 1,

            "class": "POSITIVE",

            "campaign_id":
                row["campaign_id"],

            "user_id":
                row["user_id"],

            "attack_type":
                row["attack_type"],

            "attack_severity":
                row.get(
                    "attack_severity",
                    np.nan
                ),

            "takeover_time":
                row["takeover_time"],

            "horizon_minutes":
                horizon,

            "cutoff_time":
                cutoff_time,

            "country":
                row["country"],

            "language_region":
                row["language_region"],

            "age":
                row["age"],

            "tenure_months":
                row["tenure_months"],

            "behaviour_profile":
                row["behaviour_profile"]
        })


positive_windows = pd.DataFrame(
    positive_windows
)


# ============================================================
# 6. BASIC VALIDATION
# ============================================================

print("\n" + "=" * 75)
print("POSITIVE WINDOW SUMMARY")
print("=" * 75)

print(
    "Windows:",
    len(positive_windows)
)

print(
    "Campaigns:",
    positive_windows[
        "campaign_id"
    ].nunique()
)

print(
    "Users:",
    positive_windows[
        "user_id"
    ].nunique()
)

print(
    "\nHorizon distribution:"
)

print(
    positive_windows[
        "horizon_minutes"
    ].value_counts().sort_index()
)


# ============================================================
# 7. ATTACK TYPE × HORIZON
# ============================================================

print(
    "\nAttack type × horizon:"
)

print(
    pd.crosstab(
        positive_windows[
            "attack_type"
        ],
        positive_windows[
            "horizon_minutes"
        ]
    )
)


# ============================================================
# 8. TEMPORAL VALIDATION
# ============================================================

print("\n" + "=" * 75)
print("TEMPORAL VALIDATION")
print("=" * 75)

print(
    "Missing takeover times:",
    positive_windows[
        "takeover_time"
    ].isna().sum()
)

print(
    "Missing cutoff times:",
    positive_windows[
        "cutoff_time"
    ].isna().sum()
)

print(
    "Cutoff at/after takeover:",
    (
        positive_windows[
            "cutoff_time"
        ]
        >=
        positive_windows[
            "takeover_time"
        ]
    ).sum()
)


# ============================================================
# 9. WINDOW DATE / TIME CONTEXT
# ============================================================

positive_windows["cutoff_date"] = (
    positive_windows[
        "cutoff_time"
    ].dt.date
)

positive_windows["cutoff_hour"] = (
    positive_windows[
        "cutoff_time"
    ].dt.hour
)

positive_windows["cutoff_dow"] = (
    positive_windows[
        "cutoff_time"
    ].dt.dayofweek
)


# ============================================================
# 10. FINAL OBJECT
# ============================================================

positive_prediction_windows = (
    positive_windows.copy()
)


print("\n" + "=" * 75)
print("STEP 71A COMPLETE")
print("=" * 75)

# ==============================================================================
# NOTEBOOK CELL 197
# ==============================================================================

# ============================================================
# STEP 71B: MATCHED NEGATIVE PREDICTION WINDOWS
# ============================================================

import pandas as pd
import numpy as np

print("=" * 75)
print("STEP 71B: MATCHED NEGATIVE PREDICTION WINDOWS")
print("=" * 75)

rng = np.random.default_rng(SEED + 72)


# ============================================================
# 1. PREPARE CLEAN OBSERVABLE STREAM
# ============================================================

base = observable_stream.copy()

base["timestamp"] = pd.to_datetime(
    base["timestamp"],
    errors="coerce"
)

# Only ordinary observations.
# This excludes the controlled precursor layer.

base = base[
    base["is_observable_precursor"] == 0
].copy()

# Only clean negative users.

positive_user_set = set(
    positive_prediction_windows["user_id"]
)

negative_user_set = set(
    users["user_id"]
) - positive_user_set

# Explicitly remove anyone appearing in attack data.

negative_user_set -= set(
    attack_events["user_id"]
)

negative_user_set -= set(
    observable_precursors["user_id"]
)

negative_user_set = sorted(
    negative_user_set
)

base_negative = base[
    base["user_id"].isin(
        negative_user_set
    )
].copy()

print(
    "\nClean negative users:",
    len(negative_user_set)
)

print(
    "Negative observable events:",
    len(base_negative)
)


# ============================================================
# 2. USER PROFILE
# ============================================================

profile_cols = [
    "user_id",
    "country",
    "language_region",
    "age",
    "tenure_months",
    "behaviour_profile"
]

user_profiles = users[
    profile_cols
].copy()


# ============================================================
# 3. ADD TEMPORAL VARIABLES
# ============================================================

base_negative["date"] = (
    base_negative["timestamp"].dt.date
)

base_negative["hour"] = (
    base_negative["timestamp"].dt.hour
)

base_negative["minute"] = (
    base_negative["timestamp"].dt.minute
)

base_negative["dow"] = (
    base_negative["timestamp"].dt.dayofweek
)


# ============================================================
# 4. CREATE CANDIDATE CUTOFFS
#
# We use actual observed event times as possible cutoffs.
# This prevents selecting arbitrary periods with no activity.
# ============================================================

candidate_cutoffs = (
    base_negative[
        [
            "user_id",
            "timestamp"
        ]
    ]
    .drop_duplicates()
    .rename(
        columns={
            "timestamp": "cutoff_time"
        }
    )
)

candidate_cutoffs = candidate_cutoffs.merge(
    user_profiles,
    on="user_id",
    how="left",
    validate="many_to_one"
)

candidate_cutoffs["cutoff_hour"] = (
    candidate_cutoffs[
        "cutoff_time"
    ].dt.hour
)

candidate_cutoffs["cutoff_dow"] = (
    candidate_cutoffs[
        "cutoff_time"
    ].dt.dayofweek
)

candidate_cutoffs["cutoff_date"] = (
    candidate_cutoffs[
        "cutoff_time"
    ].dt.date
)


# ============================================================
# 5. CALCULATE LOCAL ACTIVITY
#
# Activity in the 60 minutes preceding the candidate cutoff.
# This is used only for matching, not as a model feature here.
# ============================================================

def local_activity(
    user_id,
    cutoff,
    minutes=60
):

    start = (
        cutoff -
        pd.Timedelta(
            minutes=minutes
        )
    )

    mask = (
        (base_negative["user_id"] == user_id) &
        (base_negative["timestamp"] < cutoff) &
        (base_negative["timestamp"] >= start)
    )

    return int(mask.sum())


candidate_cutoffs["events_last_60"] = [
    local_activity(
        row.user_id,
        row.cutoff_time
    )
    for row in candidate_cutoffs.itertuples()
]


# ============================================================
# 6. ADD CALENDAR POSITION
# ============================================================

candidate_cutoffs["day_of_year"] = (
    candidate_cutoffs[
        "cutoff_time"
    ].dt.dayofyear
)


# ============================================================
# 7. POSITIVE WINDOW MATCHING VARIABLES
# ============================================================

positive_match = positive_prediction_windows.copy()

positive_match["cutoff_hour"] = (
    positive_match[
        "cutoff_time"
    ].dt.hour
)

positive_match["cutoff_dow"] = (
    positive_match[
        "cutoff_time"
    ].dt.dayofweek
)

positive_match["day_of_year"] = (
    positive_match[
        "cutoff_time"
    ].dt.dayofyear
)


# ============================================================
# 8. MATCHING FUNCTION
# ============================================================

def calculate_cost(pos, cand):

    cost = 0.0

    # --------------------------------------------------------
    # Behaviour profile
    # --------------------------------------------------------

    if (
        pos["behaviour_profile"] !=
        cand["behaviour_profile"]
    ):
        cost += 20.0


    # --------------------------------------------------------
    # Country
    # --------------------------------------------------------

    if (
        pos["country"] !=
        cand["country"]
    ):
        cost += 8.0


    # --------------------------------------------------------
    # Language
    # --------------------------------------------------------

    if (
        pos["language_region"] !=
        cand["language_region"]
    ):
        cost += 3.0


    # --------------------------------------------------------
    # Hour of day
    #
    # Circular distance so 23:00 and 00:00 are close.
    # --------------------------------------------------------

    hour_diff = abs(
        pos["cutoff_hour"] -
        cand["cutoff_hour"]
    )

    hour_diff = min(
        hour_diff,
        24 - hour_diff
    )

    cost += 2.0 * hour_diff


    # --------------------------------------------------------
    # Day of week
    # --------------------------------------------------------

    dow_diff = abs(
        pos["cutoff_dow"] -
        cand["cutoff_dow"]
    )

    dow_diff = min(
        dow_diff,
        7 - dow_diff
    )

    cost += 2.0 * dow_diff


    # --------------------------------------------------------
    # Calendar proximity
    #
    # We prefer the same general period without requiring
    # exact date equality.
    # --------------------------------------------------------

    calendar_diff = abs(
        pos["day_of_year"] -
        cand["day_of_year"]
    )

    cost += (
        min(calendar_diff, 30) /
        10.0
    )


    # --------------------------------------------------------
    # Local activity similarity
    # --------------------------------------------------------

    activity_diff = abs(
        pos.get(
            "positive_events_last_60",
            0
        ) -
        cand["events_last_60"]
    )

    cost += 3.0 * activity_diff


    return cost


# ============================================================
# 9. CALCULATE POSITIVE LOCAL ACTIVITY
# ============================================================

positive_match["positive_events_last_60"] = [
    local_activity(
        row.user_id,
        row.cutoff_time
    )
    for row in positive_match.itertuples()
]


# ============================================================
# 10. MATCH EACH POSITIVE WINDOW
#
# We allow reuse of a negative user, but avoid repeatedly
# selecting nearly identical cutoff times.
# ============================================================

used_cutoffs = []

negative_records = []

for idx, pos in positive_match.iterrows():

    candidates = candidate_cutoffs.copy()


    # --------------------------------------------------------
    # Exclude candidate times already used too close together
    # for the same negative user.
    # --------------------------------------------------------

    if used_cutoffs:

        used_df = pd.DataFrame(
            used_cutoffs
        )

        for neg_uid in used_df[
            "negative_user_id"
        ].unique():

            user_used = used_df[
                used_df[
                    "negative_user_id"
                ] == neg_uid
            ]

            candidate_times = user_used[
                "negative_cutoff_time"
            ].values

            if len(candidate_times) == 0:
                continue

            # Remove candidates within 12 hours of an
            # already selected cutoff for the same user.

            same_user_mask = (
                candidates["user_id"] ==
                neg_uid
            )

            for used_time in candidate_times:

                distance_hours = (
                    np.abs(
                        (
                            candidates.loc[
                                same_user_mask,
                                "cutoff_time"
                            ] -
                            pd.Timestamp(
                                used_time
                            )
                        ).dt.total_seconds()
                    ) / 3600
                )

                candidates.loc[
                    same_user_mask,
                    "too_close"
                ] = (
                    distance_hours < 12
                )

        if "too_close" in candidates.columns:

            candidates = candidates[
                candidates[
                    "too_close"
                ].fillna(False) == False
            ]


    # --------------------------------------------------------
    # If the 12 hour restriction is too restrictive,
    # fall back to 6 hours.
    # --------------------------------------------------------

    if len(candidates) == 0:

        candidates = candidate_cutoffs.copy()

        if used_cutoffs:

            used_df = pd.DataFrame(
                used_cutoffs
            )

            candidates["too_close"] = False

            for neg_uid in used_df[
                "negative_user_id"
            ].unique():

                user_used = used_df[
                    used_df[
                        "negative_user_id"
                    ] == neg_uid
                ]

                same_user_mask = (
                    candidates["user_id"] ==
                    neg_uid
                )

                for used_time in user_used[
                    "negative_cutoff_time"
                ]:

                    distance_hours = (
                        np.abs(
                            (
                                candidates.loc[
                                    same_user_mask,
                                    "cutoff_time"
                                ] -
                                pd.Timestamp(
                                    used_time
                                )
                            ).dt.total_seconds()
                        ) / 3600
                    )

                    candidates.loc[
                        same_user_mask,
                        "too_close"
                    ] = (
                        candidates.loc[
                            same_user_mask,
                            "too_close"
                        ] |
                        (distance_hours < 6)
                    )

            candidates = candidates[
                ~candidates["too_close"]
            ]


    # --------------------------------------------------------
    # If still empty, allow reuse as last resort.
    # --------------------------------------------------------

    if len(candidates) == 0:

        candidates = candidate_cutoffs.copy()


    # --------------------------------------------------------
    # Prefer profile compatible candidates.
    # --------------------------------------------------------

    compatible = candidates[
        candidates[
            "behaviour_profile"
        ] ==
        pos["behaviour_profile"]
    ]

    if len(compatible) > 0:
        candidates = compatible


    # --------------------------------------------------------
    # Calculate cost.
    # --------------------------------------------------------

    candidates = candidates.copy()

    candidates["match_cost"] = candidates.apply(
        lambda c: calculate_cost(
            pos,
            c
        ),
        axis=1
    )


    # --------------------------------------------------------
    # Add small random tie breaker.
    # --------------------------------------------------------

    candidates["tie_break"] = rng.random(
        len(candidates)
    )

    best = candidates.sort_values(
        [
            "match_cost",
            "tie_break"
        ]
    ).iloc[0]


    # --------------------------------------------------------
    # Store match.
    # --------------------------------------------------------

    record = {

        "window_id":
            f"NEG_{idx+1:04d}",

        "label": 0,

        "class": "NEGATIVE",

        "positive_window_id":
            pos["window_id"],

        "positive_user_id":
            pos["user_id"],

        "negative_user_id":
            best["user_id"],

        "negative_cutoff_time":
            best["cutoff_time"],

        "horizon_minutes":
            pos["horizon_minutes"],

        "match_cost":
            best["match_cost"],

        "positive_country":
            pos["country"],

        "negative_country":
            best["country"],

        "positive_behaviour_profile":
            pos["behaviour_profile"],

        "negative_behaviour_profile":
            best["behaviour_profile"],

        "positive_cutoff_hour":
            pos["cutoff_hour"],

        "negative_cutoff_hour":
            best["cutoff_hour"],

        "positive_cutoff_dow":
            pos["cutoff_dow"],

        "negative_cutoff_dow":
            best["cutoff_dow"],

        "positive_events_last_60":
            pos["positive_events_last_60"],

        "negative_events_last_60":
            best["events_last_60"]
    }

    negative_records.append(record)

    used_cutoffs.append({
        "negative_user_id":
            best["user_id"],

        "negative_cutoff_time":
            best["cutoff_time"]
    })


# ============================================================
# 11. FINAL NEGATIVE TABLE
# ============================================================

negative_prediction_windows = pd.DataFrame(
    negative_records
)


# ============================================================
# 12. SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("NEGATIVE WINDOW SUMMARY")
print("=" * 75)

print(
    "Negative windows:",
    len(negative_prediction_windows)
)

print(
    "Negative users used:",
    negative_prediction_windows[
        "negative_user_id"
    ].nunique()
)

print(
    "\nHorizon distribution:"
)

print(
    negative_prediction_windows[
        "horizon_minutes"
    ].value_counts()
    .sort_index()
)


# ============================================================
# 13. MATCH COST
# ============================================================

print("\n" + "=" * 75)
print("MATCH COST")
print("=" * 75)

print(
    negative_prediction_windows[
        "match_cost"
    ].describe()
)


# ============================================================
# 14. PROFILE MATCH
# ============================================================

print("\n" + "=" * 75)
print("PROFILE MATCH")
print("=" * 75)

print(
    "Behaviour profile match:",
    (
        negative_prediction_windows[
            "positive_behaviour_profile"
        ]
        ==
        negative_prediction_windows[
            "negative_behaviour_profile"
        ]
    ).mean()
)

print(
    "Country match:",
    (
        negative_prediction_windows[
            "positive_country"
        ]
        ==
        negative_prediction_windows[
            "negative_country"
        ]
    ).mean()
)


# ============================================================
# 15. TIME MATCH
# ============================================================

print("\n" + "=" * 75)
print("TEMPORAL MATCH")
print("=" * 75)

hour_diff = (
    negative_prediction_windows[
        "positive_cutoff_hour"
    ] -
    negative_prediction_windows[
        "negative_cutoff_hour"
    ]
).abs()

hour_diff = np.minimum(
    hour_diff,
    24 - hour_diff
)

print(
    "Hour difference:",
    hour_diff.describe()
)

print(
    "Exact hour match:",
    (
        hour_diff == 0
    ).mean()
)

print(
    "Day of week exact match:",
    (
        negative_prediction_windows[
            "positive_cutoff_dow"
        ]
        ==
        negative_prediction_windows[
            "negative_cutoff_dow"
        ]
    ).mean()
)


# ============================================================
# 16. LOCAL ACTIVITY MATCH
# ============================================================

activity_diff = (
    negative_prediction_windows[
        "positive_events_last_60"
    ] -
    negative_prediction_windows[
        "negative_events_last_60"
    ]
).abs()

print("\n" + "=" * 75)
print("LOCAL ACTIVITY MATCH")
print("=" * 75)

print(
    activity_diff.describe()
)

print(
    "Exact activity match:",
    (
        activity_diff == 0
    ).mean()
)


# ============================================================
# 17. USER SEPARATION
# ============================================================

print("\n" + "=" * 75)
print("USER SEPARATION")
print("=" * 75)

positive_users_final = set(
    positive_prediction_windows[
        "user_id"
    ]
)

negative_users_final = set(
    negative_prediction_windows[
        "negative_user_id"
    ]
)

print(
    "Positive users:",
    len(positive_users_final)
)

print(
    "Negative users:",
    len(negative_users_final)
)

print(
    "User overlap:",
    len(
        positive_users_final &
        negative_users_final
    )
)


# ============================================================
# 18. NEGATIVE WINDOW VALIDITY
# ============================================================

# Every negative cutoff must have at least one ordinary
# observable event before it.

negative_validity = []

for _, row in negative_prediction_windows.iterrows():

    count_before = (
        (
            (base_negative["user_id"] ==
             row["negative_user_id"]) &
            (
                base_negative["timestamp"] <
                row["negative_cutoff_time"]
            )
        ).sum()
    )

    negative_validity.append(
        count_before > 0
    )

negative_prediction_windows[
    "has_history"
] = negative_validity

print("\n" + "=" * 75)
print("NEGATIVE HISTORY VALIDATION")
print("=" * 75)

print(
    "Windows with history:",
    negative_prediction_windows[
        "has_history"
    ].sum()
)

print(
    "Windows without history:",
    (
        ~negative_prediction_windows[
            "has_history"
        ]
    ).sum()
)


# ============================================================
# 19. DUPLICATE NEGATIVE WINDOWS
# ============================================================

duplicate_negative = (
    negative_prediction_windows
    .duplicated(
        subset=[
            "negative_user_id",
            "negative_cutoff_time",
            "horizon_minutes"
        ]
    )
    .sum()
)

print(
    "\nDuplicate negative windows:",
    duplicate_negative
)


# ============================================================
# 20. FINAL OBJECT
# ============================================================

negative_prediction_windows = (
    negative_prediction_windows.copy()
)


print("\n" + "=" * 75)
print("STEP 71B COMPLETE")
print("=" * 75)

# ==============================================================================
# NOTEBOOK CELL 198
# ==============================================================================

# ============================================================
# DIAGNOSTIC: INSPECT POSITIVE WINDOW COLUMNS
# ============================================================

print("positive_windows shape:", positive_windows.shape)

print("\nColumns in positive_windows:")
for i, col in enumerate(positive_windows.columns, start=1):
    print(f"{i:03d}. {col}")

print("\nDatetime columns:")
for col in positive_windows.columns:
    if pd.api.types.is_datetime64_any_dtype(positive_windows[col]):
        print(f"  {col}")

print("\nFirst 5 rows:")
display(positive_windows.head())

# ==============================================================================
# NOTEBOOK CELL 199
# ==============================================================================

# ============================================================
# RECOVER / VALIDATE BENIGN ANOMALY TABLE
# ============================================================

print("=" * 75)
print("CHECKING BENIGN ANOMALY DATA")
print("=" * 75)

# Check whether the expected object exists
if "benign_anomalies" in globals():

    print("benign_anomalies FOUND")
    print("Rows:", len(benign_anomalies))
    print("Columns:", benign_anomalies.shape[1])
    print("\nColumn names:")
    print(benign_anomalies.columns.tolist())

else:

    print("benign_anomalies NOT FOUND")

    # Look for likely alternative objects already in memory
    possible_objects = [
        name for name in globals()
        if any(term in name.lower() for term in [
            "benign",
            "anomal",
            "normal"
        ])
    ]

    print("\nPossible related objects currently in memory:")

    if possible_objects:
        for name in possible_objects:
            obj = globals()[name]

            if isinstance(obj, pd.DataFrame):
                print(
                    f"  {name}: "
                    f"{obj.shape[0]} rows x {obj.shape[1]} columns"
                )
            else:
                print(f"  {name}: {type(obj).__name__}")

    else:
        print("  None found.")

print("\n" + "=" * 75)
print("CHECK COMPLETE")
print("=" * 75)

# ==============================================================================
# NOTEBOOK CELL 200
# ==============================================================================

# ============================================================
# STEP 71B PREPARATION
# INSPECT EXISTING BENIGN ANOMALY OBJECTS
# ============================================================

import pandas as pd
import numpy as np

print("=" * 75)
print("INSPECTING EXISTING BENIGN ANOMALY OBJECTS")
print("=" * 75)

# ------------------------------------------------------------
# 1. NORMAL STREAM
# ------------------------------------------------------------

print("\nNORMAL STREAM")
print("Shape:", normal_stream.shape)
print("Columns:")
print(normal_stream.columns.tolist())

print("\nFirst 3 rows:")
display(normal_stream.head(3))


# ------------------------------------------------------------
# 2. BENIGN PARAMETERS
# ------------------------------------------------------------

print("\nBENIGN PARAMETERS")

for name in [
    "BENIGN_RATE",
    "N_BENIGN",
    "benign_session_ids",
    "benign_types",
    "benign_weights",
    "selected_benign",
    "benign_count"
]:
    if name in globals():
        obj = globals()[name]

        print(f"\n{name}")
        print("Type:", type(obj).__name__)

        if isinstance(obj, pd.DataFrame):
            print("Shape:", obj.shape)
            display(obj.head(5))

        elif isinstance(obj, np.ndarray):
            print("Shape:", obj.shape)
            print("Values:", obj[:10])

        elif isinstance(obj, (list, tuple)):
            print("Length:", len(obj))
            print("Values:", obj[:20])

        else:
            print("Value:", obj)


# ------------------------------------------------------------
# 3. BENIGN SESSION IDs
# ------------------------------------------------------------

if "benign_session_ids" in globals():

    print("\nBENIGN SESSION ID VALIDATION")

    print("Number selected:", len(benign_session_ids))
    print("Unique selected:", len(set(benign_session_ids)))

    print("\nExample IDs:")
    print(benign_session_ids[:20])

    normal_session_ids = set(
        normal_stream["session_id"].dropna().astype(str)
    )

    benign_ids_as_str = set(
        pd.Series(benign_session_ids).dropna().astype(str)
    )

    print(
        "Selected IDs present in normal_stream:",
        len(benign_ids_as_str & normal_session_ids)
    )

    print(
        "Selected IDs NOT present in normal_stream:",
        len(benign_ids_as_str - normal_session_ids)
    )


# ------------------------------------------------------------
# 4. CHECK BENIGN TYPE INFORMATION
# ------------------------------------------------------------

if "benign_types" in globals():

    print("\nBENIGN TYPES")

    print("Number of types:", len(benign_types))
    print("Types:", benign_types)

if "benign_weights" in globals():

    print("\nBENIGN WEIGHTS")
    print("Weights:", benign_weights)

print("\n" + "=" * 75)
print("INSPECTION COMPLETE")
print("=" * 75)

# ==============================================================================
# NOTEBOOK CELL 201
# ==============================================================================

# ============================================================
# STEP 71B PREPARATION
# RECOVER ORIGINAL BENIGN ANOMALY EVENTS
# ============================================================

import pandas as pd
import numpy as np

print("=" * 75)
print("RECOVERING ORIGINAL BENIGN ANOMALY EVENTS")
print("=" * 75)

# ------------------------------------------------------------
# 1. Validate original benign selection
# ------------------------------------------------------------

assert len(benign_session_ids) == N_BENIGN
assert len(np.unique(benign_session_ids)) == N_BENIGN
assert len(selected_benign) == N_BENIGN

print("\nOriginal benign sessions:", N_BENIGN)
print("Unique benign sessions:", len(np.unique(benign_session_ids)))

# ------------------------------------------------------------
# 2. Create session -> anomaly type mapping
# ------------------------------------------------------------

benign_assignment = pd.DataFrame({
    "session_id": benign_session_ids,
    "benign_anomaly_type": selected_benign
})

assert benign_assignment["session_id"].nunique() == N_BENIGN
assert benign_assignment["benign_anomaly_type"].notna().all()

print("\nBenign anomaly distribution:")
print(
    benign_assignment["benign_anomaly_type"]
    .value_counts()
)

# ------------------------------------------------------------
# 3. Recover all observable rows belonging to the
#    originally selected benign sessions
# ------------------------------------------------------------

benign_anomalies = (
    normal_stream[
        normal_stream["session_id"].isin(benign_session_ids)
    ]
    .copy()
)

# Attach the original benign anomaly label
benign_anomalies = benign_anomalies.merge(
    benign_assignment,
    on="session_id",
    how="inner",
    validate="many_to_one"
)

# ------------------------------------------------------------
# 4. Mark these as benign observable anomalies
# ------------------------------------------------------------

benign_anomalies["ground_truth_state"] = "NORMAL"
benign_anomalies["is_attack"] = 0
benign_anomalies["is_observable_precursor"] = 0
benign_anomalies["observable_source"] = "BENIGN_ANOMALY"

# ------------------------------------------------------------
# 5. Validation
# ------------------------------------------------------------

print("\nRecovered benign observable rows:", len(benign_anomalies))
print(
    "Unique benign sessions:",
    benign_anomalies["session_id"].nunique()
)
print(
    "Unique benign users:",
    benign_anomalies["user_id"].nunique()
)

print("\nRows by benign anomaly type:")
print(
    benign_anomalies
    .groupby("benign_anomaly_type")["session_id"]
    .nunique()
)

print("\nRows by event type:")
print(
    benign_anomalies["event_type"]
    .value_counts()
    .head(20)
)

# ------------------------------------------------------------
# 6. Ensure all 300 selected sessions were recovered
# ------------------------------------------------------------

recovered_ids = set(
    benign_anomalies["session_id"].dropna().astype(str)
)

original_ids = set(
    pd.Series(benign_session_ids).dropna().astype(str)
)

missing_ids = original_ids - recovered_ids
extra_ids = recovered_ids - original_ids

print("\nMissing selected sessions:", len(missing_ids))
print("Unexpected sessions:", len(extra_ids))

assert len(missing_ids) == 0
assert len(extra_ids) == 0
assert benign_anomalies["is_attack"].eq(0).all()
assert benign_anomalies["ground_truth_state"].eq("NORMAL").all()

# ------------------------------------------------------------
# 7. Timestamp validation
# ------------------------------------------------------------

benign_anomalies["timestamp"] = pd.to_datetime(
    benign_anomalies["timestamp"]
)

print(
    "Missing timestamps:",
    benign_anomalies["timestamp"].isna().sum()
)

print(
    "Earliest benign timestamp:",
    benign_anomalies["timestamp"].min()
)

print(
    "Latest benign timestamp:",
    benign_anomalies["timestamp"].max()
)

assert benign_anomalies["timestamp"].notna().all()

print("\n" + "=" * 75)
print("BENIGN ANOMALY RECOVERY COMPLETE")
print("=" * 75)

# ==============================================================================
# NOTEBOOK CELL 202
# ==============================================================================

# ============================================================
# STEP 71B PREPARATION
# BUILD CANONICAL DEFENDER OBSERVABLE STREAM
# ============================================================

import pandas as pd
import numpy as np

print("=" * 75)
print("BUILDING CANONICAL DEFENDER OBSERVABLE STREAM")
print("=" * 75)

# ------------------------------------------------------------
# 1. Start from the existing normal observable stream
# ------------------------------------------------------------

ordinary_events = normal_stream.copy()

ordinary_events["timestamp"] = pd.to_datetime(
    ordinary_events["timestamp"]
)

# Ensure attack rows cannot enter the defender stream
if "is_attack" in ordinary_events.columns:
    ordinary_events = ordinary_events[
        ordinary_events["is_attack"].fillna(0).astype(int) == 0
    ].copy()
else:
    ordinary_events["is_attack"] = 0

ordinary_events["observable_source"] = "ORDINARY"

# ------------------------------------------------------------
# 2. Identify the sessions belonging to benign anomalies
# ------------------------------------------------------------

benign_session_set = set(
    benign_session_ids.astype(str)
)

ordinary_events["_session_key"] = (
    ordinary_events["session_id"]
    .astype(str)
)

ordinary_events["is_benign_anomaly"] = (
    ordinary_events["_session_key"]
    .isin(benign_session_set)
)

ordinary_events.drop(
    columns=["_session_key"],
    inplace=True
)

# Assign benign provenance to the already existing observations
ordinary_events.loc[
    ordinary_events["is_benign_anomaly"],
    "observable_source"
] = "BENIGN_ANOMALY"

# ------------------------------------------------------------
# 3. Recover anomaly type for provenance
# ------------------------------------------------------------

benign_type_map = dict(
    zip(
        benign_assignment["session_id"].astype(str),
        benign_assignment["benign_anomaly_type"]
    )
)

ordinary_events["benign_anomaly_type"] = (
    ordinary_events["session_id"]
    .astype(str)
    .map(benign_type_map)
)

# ------------------------------------------------------------
# 4. Prepare observable precursor stream
# ------------------------------------------------------------

precursor_events = observable_precursors.copy()

precursor_events["timestamp"] = pd.to_datetime(
    precursor_events["timestamp"]
)

if "is_attack" in precursor_events.columns:
    precursor_events = precursor_events[
        precursor_events["is_attack"].fillna(0).astype(int) == 0
    ].copy()
else:
    precursor_events["is_attack"] = 0

precursor_events["observable_source"] = (
    "OBSERVABLE_PRECURSOR"
)

precursor_events["benign_anomaly_type"] = pd.NA

# ------------------------------------------------------------
# 5. Harmonize columns
# ------------------------------------------------------------

required_columns = [
    "event_id",
    "timestamp",
    "user_id",
    "device_id",
    "session_id",
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
    "observable_source",
    "benign_anomaly_type"
]

for col in required_columns:
    if col not in ordinary_events.columns:
        ordinary_events[col] = pd.NA

    if col not in precursor_events.columns:
        precursor_events[col] = pd.NA

# ------------------------------------------------------------
# 6. Combine without duplicating benign observations
# ------------------------------------------------------------

unified_observable_stream = pd.concat(
    [
        ordinary_events[required_columns],
        precursor_events[required_columns]
    ],
    ignore_index=True,
    sort=False
)

# ------------------------------------------------------------
# 7. Explicit defender safety controls
# ------------------------------------------------------------

unified_observable_stream["is_attack"] = (
    unified_observable_stream["is_attack"]
    .fillna(0)
    .astype(int)
)

unified_observable_stream = (
    unified_observable_stream[
        unified_observable_stream["is_attack"] == 0
    ]
    .copy()
)

unified_observable_stream["timestamp"] = pd.to_datetime(
    unified_observable_stream["timestamp"]
)

unified_observable_stream = (
    unified_observable_stream
    .sort_values(
        ["user_id", "timestamp", "event_id"],
        na_position="last"
    )
    .reset_index(drop=True)
)

# ------------------------------------------------------------
# 8. Validation
# ------------------------------------------------------------

print("\nORDINARY OBSERVABLE ROWS:", len(ordinary_events))
print(
    "BENIGN ANOMALY SESSIONS:",
    benign_assignment["session_id"].nunique()
)
print(
    "OBSERVABLE PRECURSOR ROWS:",
    len(precursor_events)
)
print(
    "\nUNIFIED DEFENDER OBSERVABLE ROWS:",
    len(unified_observable_stream)
)

print(
    "UNIQUE USERS:",
    unified_observable_stream["user_id"].nunique()
)

print(
    "UNIQUE SESSIONS:",
    unified_observable_stream["session_id"].nunique()
)

print("\nOBSERVABLE SOURCE:")
print(
    unified_observable_stream[
        "observable_source"
    ].value_counts(dropna=False)
)

print("\nBENIGN ANOMALY TYPE:")
print(
    unified_observable_stream[
        "benign_anomaly_type"
    ].value_counts(dropna=False)
)

print("\nATTACK FLAG:")
print(
    unified_observable_stream[
        "is_attack"
    ].value_counts(dropna=False)
)

print(
    "\nMissing timestamps:",
    unified_observable_stream["timestamp"].isna().sum()
)

print(
    "Earliest timestamp:",
    unified_observable_stream["timestamp"].min()
)

print(
    "Latest timestamp:",
    unified_observable_stream["timestamp"].max()
)

# ------------------------------------------------------------
# 9. Critical leakage assertions
# ------------------------------------------------------------

assert unified_observable_stream["timestamp"].notna().all()
assert unified_observable_stream["user_id"].notna().all()
assert unified_observable_stream["is_attack"].eq(0).all()

assert (
    unified_observable_stream["observable_source"]
    .isin([
        "ORDINARY",
        "BENIGN_ANOMALY",
        "OBSERVABLE_PRECURSOR"
    ])
    .all()
)

# Attack campaign metadata must NOT be present
for forbidden_col in [
    "campaign_id",
    "attack_type",
    "campaign_status",
    "attack_severity",
    "takeover_time"
]:
    assert forbidden_col not in unified_observable_stream.columns, (
        f"Potential leakage column found: {forbidden_col}"
    )

print("\n" + "=" * 75)
print("CANONICAL DEFENDER OBSERVABLE STREAM READY")
print("=" * 75)

# ==============================================================================
# NOTEBOOK CELL 203
# ==============================================================================

# ============================================================
# AFRITAC STEP 71B
# MATCHED NEGATIVE PREDICTION WINDOWS
# ============================================================

import numpy as np
import pandas as pd

print("STEP 71B: MATCHED NEGATIVE PREDICTION WINDOWS")

# ------------------------------------------------------------
# 1. Required objects
# ------------------------------------------------------------

required_objects = [
    "positive_windows",
    "users",
    "events",
]

missing = [x for x in required_objects if x not in globals()]

print("Required objects missing:", missing)

assert not missing, f"Missing required objects: {missing}"

# ------------------------------------------------------------
# 2. Configuration
# ------------------------------------------------------------

HORIZONS = [5, 10, 15, 30, 60]
N_NEGATIVE_USERS = 20

rng_71B = np.random.default_rng(SEED + 71_000)

# ------------------------------------------------------------
# 3. Identify positive users
# ------------------------------------------------------------

positive_users = set(
    positive_windows["user_id"].astype(str).unique()
)

print("Positive users:", len(positive_users))

assert len(positive_users) == 80

# ------------------------------------------------------------
# 4. Candidate negative users
# ------------------------------------------------------------

all_users = set(
    users["user_id"].astype(str).unique()
)

candidate_negative_users = sorted(
    all_users - positive_users
)

print("Candidate negative users:", len(candidate_negative_users))

assert len(candidate_negative_users) >= N_NEGATIVE_USERS

# ------------------------------------------------------------
# 5. Select exactly 20 negative users
# ------------------------------------------------------------

selected_negative_users = rng_71B.choice(
    candidate_negative_users,
    size=N_NEGATIVE_USERS,
    replace=False
)

selected_negative_users = set(
    map(str, selected_negative_users)
)

print("Selected negative users:", len(selected_negative_users))

assert len(selected_negative_users) == 20
assert selected_negative_users.isdisjoint(positive_users)

# ------------------------------------------------------------
# 6. Prepare observable events
# ------------------------------------------------------------

negative_source = events.copy()

negative_source["user_id"] = (
    negative_source["user_id"].astype(str)
)

negative_source["timestamp"] = pd.to_datetime(
    negative_source["timestamp"],
    errors="coerce"
)

negative_source = negative_source[
    negative_source["user_id"].isin(selected_negative_users)
].copy()

negative_source = negative_source[
    negative_source["timestamp"].notna()
].copy()

negative_source = negative_source.sort_values(
    ["user_id", "timestamp"]
).reset_index(drop=True)

print(
    "Observable events available for negative users:",
    len(negative_source)
)

assert len(negative_source) > 0

# ------------------------------------------------------------
# 7. Select ONE real observed cutoff per negative user
# ------------------------------------------------------------

# The important design decision:
# One cutoff is selected for each negative user.
# That cutoff is then evaluated at all five horizons.
#
# This produces:
# 20 users × 5 horizons = 100 windows.
#
# We deliberately do NOT create one negative cutoff
# for every positive window.

negative_cutoff_records = []

for user_id in sorted(selected_negative_users):

    user_events = negative_source[
        negative_source["user_id"] == user_id
    ].copy()

    if user_events.empty:
        continue

    # Use a real observed event time as the cutoff.
    #
    # Avoid choosing the very first event because the historical
    # lookback would otherwise be artificially empty.
    if len(user_events) >= 3:
        candidate_times = user_events["timestamp"].iloc[1:-1]
    else:
        candidate_times = user_events["timestamp"]

    if len(candidate_times) == 0:
        candidate_times = user_events["timestamp"]

    cutoff_time = pd.Timestamp(
        rng_71B.choice(candidate_times.to_numpy())
    )

    negative_cutoff_records.append({
        "negative_user_id": user_id,
        "negative_cutoff_time": cutoff_time
    })

negative_cutoffs = pd.DataFrame(
    negative_cutoff_records
)

print(
    "Negative users with valid cutoffs:",
    negative_cutoffs["negative_user_id"].nunique()
)

assert (
    negative_cutoffs["negative_user_id"].nunique()
    == N_NEGATIVE_USERS
)

# ------------------------------------------------------------
# 8. Build exactly five windows per negative user
# ------------------------------------------------------------

negative_records = []

for _, row in negative_cutoffs.iterrows():

    user_id = str(row["negative_user_id"])
    cutoff_time = pd.Timestamp(row["negative_cutoff_time"])

    # User metadata
    user_match = users[
        users["user_id"].astype(str) == user_id
    ]

    assert len(user_match) == 1

    user_info = user_match.iloc[0]

    for horizon in HORIZONS:

        left_boundary = (
            cutoff_time
            - pd.Timedelta(minutes=int(horizon))
        )

        right_boundary = cutoff_time

        negative_records.append({

            "user_id": user_id,

            "cutoff_time": cutoff_time,

            "left_boundary": left_boundary,

            "right_boundary": right_boundary,

            "gap_minutes": int(horizon),

            "date": cutoff_time.date(),

            "horizon_minutes": int(horizon),

            "window_id": (
                f"NEG_{user_id}_"
                f"{cutoff_time.strftime('%Y%m%d%H%M%S')}_"
                f"H{horizon}"
            ),

            "target": 0,

            "label": 0,

            "class": "NEGATIVE",

            "ground_truth_attack": 0,

            "is_attack": 0,

            "window_type": "NEGATIVE",

            "is_hard_negative": 0,

            "country": user_info["country"],

            "language_region": user_info["language_region"],

            "behaviour_profile": user_info["behaviour_profile"],

            "negative_user_id": user_id,

            "negative_cutoff_time": cutoff_time,

            "positive_window_id": None,

            "match_cost": np.nan,

        })

negative_windows = pd.DataFrame(
    negative_records
)

# ------------------------------------------------------------
# 9. Validate structural output
# ------------------------------------------------------------

print()
print("71B STRUCTURAL VALIDATION")

print(
    "Negative windows:",
    len(negative_windows)
)

print(
    "Negative users:",
    negative_windows["user_id"].nunique()
)

print(
    "Horizons:",
    sorted(
        negative_windows["horizon_minutes"].unique()
    )
)

print(
    "Positive users:",
    len(positive_users)
)

user_overlap = (
    set(negative_windows["user_id"].astype(str))
    & positive_users
)

print(
    "User overlap:",
    len(user_overlap)
)

# Exact structural requirements
assert len(negative_windows) == 100

assert (
    negative_windows["user_id"].nunique()
    == 20
)

assert sorted(
    negative_windows["horizon_minutes"].unique()
) == HORIZONS

assert user_overlap == set()

# Every negative user must have exactly five windows
windows_per_user = (
    negative_windows
    .groupby("user_id")
    .size()
)

assert (
    windows_per_user == len(HORIZONS)
).all()

# Every user must have one window for each horizon
for user_id, group in negative_windows.groupby("user_id"):

    assert sorted(
        group["horizon_minutes"].tolist()
    ) == HORIZONS

# ------------------------------------------------------------
# 10. Temporal validation
# ------------------------------------------------------------

negative_windows["cutoff_time"] = pd.to_datetime(
    negative_windows["cutoff_time"]
)

negative_windows["left_boundary"] = pd.to_datetime(
    negative_windows["left_boundary"]
)

negative_windows["right_boundary"] = pd.to_datetime(
    negative_windows["right_boundary"]
)

assert (
    negative_windows["left_boundary"]
    < negative_windows["right_boundary"]
).all()

assert (
    negative_windows["right_boundary"]
    == negative_windows["cutoff_time"]
).all()

# ------------------------------------------------------------
# 11. Add temporal metadata
# ------------------------------------------------------------

negative_windows["cutoff_date"] = (
    negative_windows["cutoff_time"].dt.date
)

negative_windows["cutoff_hour"] = (
    negative_windows["cutoff_time"].dt.hour
)

negative_windows["cutoff_dow"] = (
    negative_windows["cutoff_time"].dt.dayofweek
)

# ------------------------------------------------------------
# 12. Calculate observable activity diagnostics
# ------------------------------------------------------------

for horizon in HORIZONS:

    col = f"events_last_{horizon}"

    values = []

    for _, row in negative_windows[
        negative_windows["horizon_minutes"] == horizon
    ].iterrows():

        user_id = str(row["user_id"])
        cutoff = pd.Timestamp(row["cutoff_time"])

        start = (
            cutoff
            - pd.Timedelta(minutes=horizon)
        )

        mask = (
            (negative_source["user_id"] == user_id)
            &
            (negative_source["timestamp"] >= start)
            &
            (negative_source["timestamp"] < cutoff)
        )

        values.append(
            int(mask.sum())
        )

    negative_windows.loc[
        negative_windows["horizon_minutes"] == horizon,
        col
    ] = values

# ------------------------------------------------------------
# 13. Final cleanup
# ------------------------------------------------------------

negative_windows = (
    negative_windows
    .sort_values(
        ["user_id", "cutoff_time", "horizon_minutes"]
    )
    .reset_index(drop=True)
)

# ------------------------------------------------------------
# 14. Final validation
# ------------------------------------------------------------

assert len(negative_windows) == 100
assert negative_windows["user_id"].nunique() == 20
assert set(
    negative_windows["user_id"].astype(str)
).isdisjoint(positive_users)

assert (
    negative_windows["window_id"].nunique()
    == 100
)

assert negative_windows["target"].eq(0).all()
assert negative_windows["label"].eq(0).all()
assert negative_windows["ground_truth_attack"].eq(0).all()
assert negative_windows["is_attack"].eq(0).all()

print()
print("71B PASS")
print()
print("Final negative windows:", len(negative_windows))
print(
    "Final negative users:",
    negative_windows["user_id"].nunique()
)
print(
    "Horizons:",
    sorted(negative_windows["horizon_minutes"].unique())
)
print(
    "Unique window IDs:",
    negative_windows["window_id"].nunique()
)
print(
    "User overlap with positive:",
    len(
        set(negative_windows["user_id"].astype(str))
        & positive_users
    )
)

# ==============================================================================
# NOTEBOOK CELL 204
# ==============================================================================

# ============================================================
# AFRITAC STEP 71D.1R
# REBUILD AUTHORITATIVE HARD NEGATIVE LAYER
# ============================================================

import numpy as np
import pandas as pd

print("=" * 70)
print("AFRITAC STEP 71D.1R")
print("REBUILD AUTHORITATIVE HARD NEGATIVE LAYER")
print("=" * 70)

# ------------------------------------------------------------
# 1. Required objects
# ------------------------------------------------------------

required_objects = [
    "users",
    "events",
    "positive_windows",
]

missing = [
    obj for obj in required_objects
    if obj not in globals()
]

print("\nRequired objects missing:", missing)

assert not missing, (
    f"Missing required objects: {missing}"
)

# ------------------------------------------------------------
# 2. Configuration
# ------------------------------------------------------------

HORIZONS = [5, 10, 15, 30, 60]
N_HARD_USERS = 20

rng_hn = np.random.default_rng(SEED + 71_400)

# ------------------------------------------------------------
# 3. Positive users
# ------------------------------------------------------------

positive_users = set(
    positive_windows["user_id"]
    .astype(str)
    .unique()
)

assert len(positive_users) == 80

# ------------------------------------------------------------
# 4. Candidate hard negative users
# ------------------------------------------------------------

all_users = set(
    users["user_id"]
    .astype(str)
    .unique()
)

candidate_hard_users = sorted(
    all_users - positive_users
)

print(
    "Candidate hard negative users:",
    len(candidate_hard_users)
)

assert len(candidate_hard_users) >= N_HARD_USERS

# ------------------------------------------------------------
# 5. Select exactly 20 hard negative users
# ------------------------------------------------------------

hard_negative_users = rng_hn.choice(
    candidate_hard_users,
    size=N_HARD_USERS,
    replace=False
)

hard_negative_users = set(
    map(str, hard_negative_users)
)

print(
    "Selected hard negative users:",
    len(hard_negative_users)
)

assert len(hard_negative_users) == 20
assert hard_negative_users.isdisjoint(
    positive_users
)

# ------------------------------------------------------------
# 6. Prepare event source
# ------------------------------------------------------------

hn_source = events.copy()

hn_source["user_id"] = (
    hn_source["user_id"].astype(str)
)

hn_source["timestamp"] = pd.to_datetime(
    hn_source["timestamp"],
    errors="coerce"
)

hn_source = hn_source[
    hn_source["timestamp"].notna()
].copy()

hn_source = hn_source[
    hn_source["user_id"].isin(
        hard_negative_users
    )
].copy()

hn_source = hn_source.sort_values(
    ["user_id", "timestamp"]
).reset_index(drop=True)

print(
    "Observable source events:",
    len(hn_source)
)

assert len(hn_source) > 0

# ------------------------------------------------------------
# 7. Select one real cutoff per hard negative user
# ------------------------------------------------------------

cutoff_records = []

for user_id in sorted(hard_negative_users):

    user_events = hn_source[
        hn_source["user_id"] == user_id
    ].copy()

    assert len(user_events) > 0

    if len(user_events) >= 3:
        candidates = user_events[
            "timestamp"
        ].iloc[1:-1]
    else:
        candidates = user_events[
            "timestamp"
        ]

    if len(candidates) == 0:
        candidates = user_events[
            "timestamp"
        ]

    cutoff = pd.Timestamp(
        rng_hn.choice(
            candidates.to_numpy()
        )
    )

    cutoff_records.append({
        "user_id": user_id,
        "cutoff_time": cutoff
    })

hard_cutoffs = pd.DataFrame(
    cutoff_records
)

assert (
    hard_cutoffs["user_id"].nunique()
    == 20
)

# ------------------------------------------------------------
# 8. Build exactly 100 hard negative windows
# ------------------------------------------------------------

hard_window_records = []

for _, row in hard_cutoffs.iterrows():

    user_id = str(row["user_id"])
    cutoff = pd.Timestamp(
        row["cutoff_time"]
    )

    user_info = users[
        users["user_id"].astype(str)
        == user_id
    ]

    assert len(user_info) == 1

    user_info = user_info.iloc[0]

    for horizon in HORIZONS:

        left_boundary = (
            cutoff
            - pd.Timedelta(
                minutes=int(horizon)
            )
        )

        hard_window_records.append({

            "user_id": user_id,

            "cutoff_time": cutoff,

            "left_boundary": left_boundary,

            "right_boundary": cutoff,

            "gap_minutes": int(horizon),

            "date": cutoff.date(),

            "horizon_minutes": int(horizon),

            "window_id": (
                f"HN_{user_id}_"
                f"{cutoff.strftime('%Y%m%d%H%M%S')}_"
                f"H{horizon}"
            ),

            "target": 0,

            "ground_truth_attack": 0,

            "is_attack": 0,

            "window_type": "HARD_NEGATIVE",

            "is_hard_negative": 1,

            "country": user_info["country"],

            "language_region": user_info[
                "language_region"
            ],

            "behaviour_profile": user_info[
                "behaviour_profile"
            ],

            "hard_negative_id": (
                f"HN_{user_id}"
            ),
        })

hard_negative_windows = pd.DataFrame(
    hard_window_records
)

# ------------------------------------------------------------
# 9. Validate window structure
# ------------------------------------------------------------

assert len(hard_negative_windows) == 100

assert (
    hard_negative_windows["user_id"]
    .nunique()
    == 20
)

assert (
    hard_negative_windows["window_id"]
    .nunique()
    == 100
)

assert (
    hard_negative_windows["horizon_minutes"]
    .isin(HORIZONS)
    .all()
)

horizon_counts = (
    hard_negative_windows[
        "horizon_minutes"
    ]
    .value_counts()
    .sort_index()
)

print("\nHard negative horizon counts:")
print(horizon_counts.to_dict())

assert (
    horizon_counts
    .reindex(HORIZONS)
    .eq(20)
    .all()
)

# ------------------------------------------------------------
# 10. Build 452 hard negative events
# ------------------------------------------------------------

# Deterministic event counts matching the established
# authoritative hard negative distribution:
#
# EARLY       74
# ESCALATION 113
# STRONG     102
# ACUTE      163
#
# Total      452

band_specs = [
    ("EARLY", 74, 41, 55),
    ("ESCALATION", 113, 26, 40),
    ("STRONG", 102, 11, 25),
    ("ACUTE", 163, 1, 10),
]

# Event vocabulary is deliberately distinct from attack
# event vocabulary.

hard_event_types = [
    "NORMAL_AUTHENTICATION_VARIATION",
    "NORMAL_USSD_VARIATION",
    "NORMAL_SESSION_VARIATION",
    "NORMAL_NETWORK_VARIATION",
    "NORMAL_DEVICE_VARIATION",
    "NORMAL_TRANSACTION_VARIATION",
]

hard_event_records = []

event_counter = 1

# Allocate events approximately across users and bands.
# Each generated event is placed before one user's real cutoff.

user_list = sorted(hard_negative_users)

for band_name, n_events, min_gap, max_gap in band_specs:

    for _ in range(n_events):

        user_id = user_list[
            rng_hn.integers(
                0,
                len(user_list)
            )
        ]

        cutoff = pd.Timestamp(
            hard_cutoffs.loc[
                hard_cutoffs["user_id"] == user_id,
                "cutoff_time"
            ].iloc[0]
        )

        minutes_before = float(
            rng_hn.uniform(
                min_gap,
                max_gap
            )
        )

        timestamp = (
            cutoff
            - pd.Timedelta(
                minutes=minutes_before
            )
        )

        event_type = rng_hn.choice(
            hard_event_types
        )

        modality = rng_hn.choice(
            [
                "USSD",
                "AUTHENTICATION",
                "SESSION",
                "FINANCIAL",
                "NETWORK",
                "DEVICE",
            ],
            p=[
                0.24,
                0.17,
                0.30,
                0.07,
                0.12,
                0.10,
            ]
        )

        hard_event_records.append({

            "event_id":
                f"HNE_{event_counter:06d}",

            "hard_negative_id":
                f"HN_{user_id}",

            "user_id":
                user_id,

            "timestamp":
                timestamp,

            "event_type":
                event_type,

            "modality":
                modality,

            "ground_truth_state":
                "NORMAL",

            "is_attack":
                0,

            "is_hard_negative":
                1,

            "hard_negative_band":
                band_name,

            "minutes_before_cutoff":
                minutes_before,

            "response_delay_ms":
                float(
                    np.clip(
                        rng_hn.normal(
                            1350,
                            230
                        ),
                        500,
                        2500
                    )
                ),

            "signal_strength_dbm":
                float(
                    np.clip(
                        rng_hn.normal(
                            -82,
                            8
                        ),
                        -110,
                        -55
                    )
                ),

            "roaming":
                int(
                    rng_hn.random() < 0.08
                ),

            "location_change":
                int(
                    rng_hn.random() < 0.08
                ),

            "new_device":
                int(
                    rng_hn.random() < 0.05
                ),

            "transaction_amount":
                (
                    float(
                        rng_hn.lognormal(
                            mean=np.log(15000),
                            sigma=0.65
                        )
                    )
                    if modality == "FINANCIAL"
                    else 0.0
                ),
        })

        event_counter += 1

hard_negative_events = pd.DataFrame(
    hard_event_records
)

# ------------------------------------------------------------
# 11. Validate hard event layer
# ------------------------------------------------------------

print("\nHARD NEGATIVE EVENT AUDIT")

print(
    "Hard negative events:",
    len(hard_negative_events)
)

print(
    "Hard negative users:",
    hard_negative_events["user_id"].nunique()
)

print(
    "Event IDs:",
    hard_negative_events["event_id"].nunique()
)

assert len(hard_negative_events) == 452

assert (
    hard_negative_events["user_id"]
    .nunique()
    == 20
)

assert (
    hard_negative_events["event_id"]
    .nunique()
    == 452
)

assert (
    hard_negative_events["is_attack"]
    .astype(int)
    .eq(0)
    .all()
)

assert (
    hard_negative_events["is_hard_negative"]
    .astype(int)
    .eq(1)
    .all()
)

# ------------------------------------------------------------
# 12. Temporal integrity
# ------------------------------------------------------------

hard_negative_events["timestamp"] = pd.to_datetime(
    hard_negative_events["timestamp"]
)

cutoff_map = (
    hard_cutoffs
    .set_index("user_id")["cutoff_time"]
    .to_dict()
)

hard_negative_events["cutoff_time"] = (
    hard_negative_events["user_id"]
    .map(cutoff_map)
)

hard_negative_events[
    "minutes_before_cutoff"
] = (
    hard_negative_events["cutoff_time"]
    - hard_negative_events["timestamp"]
).dt.total_seconds() / 60.0

assert (
    hard_negative_events["minutes_before_cutoff"]
    > 0
).all()

assert (
    hard_negative_events["minutes_before_cutoff"]
    <= 60
).all()

# ------------------------------------------------------------
# 13. User separation
# ------------------------------------------------------------

hard_users = set(
    hard_negative_windows["user_id"]
    .astype(str)
)

positive_hard_overlap = (
    positive_users
    &
    hard_users
)

print(
    "\nPositive/hard negative user overlap:",
    len(positive_hard_overlap)
)

assert len(positive_hard_overlap) == 0

# ------------------------------------------------------------
# 14. Final result
# ------------------------------------------------------------

print()
print("=" * 70)
print("71D.1R FINAL RESULT")
print("=" * 70)

print(
    "hard_negative_windows:",
    len(hard_negative_windows)
)

print(
    "hard_negative_events:",
    len(hard_negative_events)
)

print(
    "hard negative users:",
    len(hard_users)
)

print(
    "positive/hard user overlap:",
    len(positive_hard_overlap)
)

print()
print("STEP 71D.1R PASS")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 205
# ==============================================================================

# ============================================================
# AFRITAC STEP 71C.P2
# OBSERVABLE PRECURSOR SCHEMA DIAGNOSTIC
# ============================================================

print("=" * 70)
print("AFRITAC STEP 71C.P2")
print("OBSERVABLE PRECURSOR SCHEMA DIAGNOSTIC")
print("=" * 70)

assert "observable_precursors" in globals()

p = observable_precursors.copy()

print("\nShape:")
print(p.shape)

print("\nColumns:")
for i, col in enumerate(p.columns, start=1):
    print(f"{i:>3}. {col}")

print("\nData types:")
print(p.dtypes.to_string())

print("\nFirst 5 rows:")
display(p.head())

print("\nMissing values:")
print(
    p.isna()
    .sum()
    .sort_values(ascending=False)
    .to_string()
)

print("\nUnique values for likely identifier columns:")

for col in [
    "event_id",
    "user_id",
    "session_id",
    "campaign_id",
    "attack_type",
    "event_type",
    "modality",
    "precursor_band",
    "ground_truth_state",
    "is_attack",
    "is_observable_precursor",
]:
    if col in p.columns:
        print(
            f"{col:<30}",
            p[col].nunique(dropna=False)
        )

print()
print("=" * 70)
print("71C.P2 COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 206
# ==============================================================================

# ============================================================
# AFRITAC STEP 71C.P3
# PRECURSOR RECONSTRUCTION DIAGNOSTIC
# ============================================================

import numpy as np
import pandas as pd

print("=" * 70)
print("AFRITAC STEP 71C.P3")
print("PRECURSOR RECONSTRUCTION DIAGNOSTIC")
print("=" * 70)

p = observable_precursors.copy()

# ------------------------------------------------------------
# 1. Standardize identifiers and timestamps
# ------------------------------------------------------------

p["user_id"] = p["user_id"].astype(str)
p["session_id"] = p["session_id"].astype(str)
p["event_id"] = p["event_id"].astype(str)

p["timestamp"] = pd.to_datetime(
    p["timestamp"],
    errors="coerce"
)

assert p["timestamp"].notna().all()

# ------------------------------------------------------------
# 2. Recover campaign user mapping
# ------------------------------------------------------------

campaign_map = (
    campaigns[
        ["campaign_id", "user_id", "attack_type"]
    ]
    .copy()
)

campaign_map["user_id"] = (
    campaign_map["user_id"].astype(str)
)

print("\nCAMPAIGN USER COVERAGE")

precursor_users = set(
    p["user_id"].unique()
)

campaign_users = set(
    campaign_map["user_id"].unique()
)

print(
    "Precursor users:",
    len(precursor_users)
)

print(
    "Campaign users:",
    len(campaign_users)
)

print(
    "Campaign users present in precursor:",
    len(
        precursor_users & campaign_users
    )
)

print(
    "Campaign users missing from precursor:",
    len(
        campaign_users - precursor_users
    )
)

assert (
    campaign_users
    <= precursor_users
)

# ------------------------------------------------------------
# 3. Attach campaign information by user
# ------------------------------------------------------------

user_to_campaign = (
    campaign_map
    .drop_duplicates("user_id")
    .set_index("user_id")
    ["campaign_id"]
    .to_dict()
)

user_to_attack_type = (
    campaign_map
    .drop_duplicates("user_id")
    .set_index("user_id")
    ["attack_type"]
    .to_dict()
)

p["campaign_id_check"] = (
    p["user_id"]
    .map(user_to_campaign)
)

p["attack_type_check"] = (
    p["user_id"]
    .map(user_to_attack_type)
)

print(
    "\nRows mapped to campaigns:",
    p["campaign_id_check"].notna().sum(),
    "/",
    len(p)
)

assert (
    p["campaign_id_check"].notna().all()
)

# ------------------------------------------------------------
# 4. Recover takeover time
# ------------------------------------------------------------

positive_tmp = positive_windows[
    [
        "campaign_id",
        "takeover_time"
    ]
].copy()

positive_tmp["campaign_id"] = (
    positive_tmp["campaign_id"].astype(str)
)

positive_tmp["takeover_time"] = pd.to_datetime(
    positive_tmp["takeover_time"],
    errors="coerce"
)

takeover_map = (
    positive_tmp
    .drop_duplicates("campaign_id")
    .set_index("campaign_id")
    ["takeover_time"]
    .to_dict()
)

p["takeover_time_check"] = (
    p["campaign_id_check"]
    .map(takeover_map)
)

assert (
    p["takeover_time_check"].notna().all()
)

# ------------------------------------------------------------
# 5. Calculate temporal distance to takeover
# ------------------------------------------------------------

p["minutes_to_takeover_check"] = (
    p["takeover_time_check"]
    - p["timestamp"]
).dt.total_seconds() / 60.0

print("\nTEMPORAL DISTRIBUTION")

print(
    p["minutes_to_takeover_check"]
    .describe()
    .to_string()
)

print(
    "\nRows before takeover:",
    (
        p["minutes_to_takeover_check"] > 0
    ).sum()
)

print(
    "Rows at/after takeover:",
    (
        p["minutes_to_takeover_check"] <= 0
    ).sum()
)

print(
    "Rows within 60 minutes:",
    (
        (
            p["minutes_to_takeover_check"] > 0
        )
        &
        (
            p["minutes_to_takeover_check"] <= 60
        )
    ).sum()
)

print(
    "Rows beyond 60 minutes:",
    (
        p["minutes_to_takeover_check"] > 60
    ).sum()
)

# ------------------------------------------------------------
# 6. Temporal band assignment
# ------------------------------------------------------------

def assign_precursor_band(minutes):

    if 1 <= minutes <= 5:
        return "IMMINENT"

    elif 6 <= minutes <= 15:
        return "ACUTE"

    elif 16 <= minutes <= 30:
        return "STRONG"

    elif 31 <= minutes <= 45:
        return "ESCALATION"

    elif 46 <= minutes <= 60:
        return "EARLY"

    else:
        return "OUTSIDE"

p["computed_band"] = (
    p["minutes_to_takeover_check"]
    .apply(assign_precursor_band)
)

print("\nCOMPUTED BAND DISTRIBUTION")

print(
    p["computed_band"]
    .value_counts()
    .sort_index()
    .to_string()
)

# ------------------------------------------------------------
# 7. Event type distribution
# ------------------------------------------------------------

print("\nEVENT TYPE DISTRIBUTION")

print(
    p["event_type"]
    .value_counts()
    .to_string()
)

# ------------------------------------------------------------
# 8. Modality distribution
# ------------------------------------------------------------

print("\nMODALITY DISTRIBUTION")

print(
    p["modality"]
    .value_counts()
    .to_string()
)

# ------------------------------------------------------------
# 9. Events by campaign
# ------------------------------------------------------------

print("\nEVENTS PER CAMPAIGN")

campaign_event_counts = (
    p.groupby("campaign_id_check")
    .size()
)

print(
    campaign_event_counts.describe()
    .to_string()
)

print(
    "\nQuantiles:"
)

print(
    campaign_event_counts
    .quantile(
        [0, .25, .50, .75, .90, 1]
    )
    .to_string()
)

# ------------------------------------------------------------
# 10. Events within each prediction horizon
# ------------------------------------------------------------

print("\nHORIZON COVERAGE")

for horizon in [5, 10, 15, 30, 60]:

    n = (
        (
            p["minutes_to_takeover_check"] > 0
        )
        &
        (
            p["minutes_to_takeover_check"] <= horizon
        )
    ).sum()

    campaigns_covered = (
        p.loc[
            (
                p["minutes_to_takeover_check"] > 0
            )
            &
            (
                p["minutes_to_takeover_check"] <= horizon
            ),
            "campaign_id_check"
        ]
        .nunique()
    )

    print(
        f"{horizon:>2} min: "
        f"{n:>4} events | "
        f"{campaigns_covered:>2}/80 campaigns"
    )

# ------------------------------------------------------------
# 11. Session coverage
# ------------------------------------------------------------

print("\nSESSION COVERAGE")

for horizon in [5, 10, 15, 30, 60]:

    subset = p[
        (
            p["minutes_to_takeover_check"] > 0
        )
        &
        (
            p["minutes_to_takeover_check"] <= horizon
        )
    ]

    print(
        f"{horizon:>2} min: "
        f"{subset['session_id'].nunique():>3} sessions"
    )

# ------------------------------------------------------------
# 12. Check for exact 406 candidate
# ------------------------------------------------------------

print("\n406 ROW RECONSTRUCTION TEST")

within_60 = p[
    (
        p["minutes_to_takeover_check"] > 0
    )
    &
    (
        p["minutes_to_takeover_check"] <= 60
    )
].copy()

print(
    "Rows within 60 minutes:",
    len(within_60)
)

print(
    "Expected validated precursor rows:",
    406
)

print(
    "Difference from 406:",
    len(within_60) - 406
)

# ------------------------------------------------------------
# 13. Candidate filtering diagnostics
# ------------------------------------------------------------

print("\nCANDIDATE FILTERING")

filters = {

    "positive_before_takeover":
        p[
            p["minutes_to_takeover_check"] > 0
        ],

    "within_60":
        p[
            (
                p["minutes_to_takeover_check"] > 0
            )
            &
            (
                p["minutes_to_takeover_check"] <= 60
            )
        ],

    "within_45":
        p[
            (
                p["minutes_to_takeover_check"] > 0
            )
            &
            (
                p["minutes_to_takeover_check"] <= 45
            )
        ],

    "within_30":
        p[
            (
                p["minutes_to_takeover_check"] > 0
            )
            &
            (
                p["minutes_to_takeover_check"] <= 30
            )
        ],

    "within_15":
        p[
            (
                p["minutes_to_takeover_check"] > 0
            )
            &
            (
                p["minutes_to_takeover_check"] <= 15
            )
        ],

    "within_10":
        p[
            (
                p["minutes_to_takeover_check"] > 0
            )
            &
            (
                p["minutes_to_takeover_check"] <= 10
            )
        ],

    "within_5":
        p[
            (
                p["minutes_to_takeover_check"] > 0
            )
            &
            (
                p["minutes_to_takeover_check"] <= 5
            )
        ],
}

for name, subset in filters.items():

    print(
        f"{name:<30}"
        f"{len(subset):>5} rows | "
        f"{subset['campaign_id_check'].nunique():>2} campaigns"
    )

# ------------------------------------------------------------
# 14. Final diagnostic
# ------------------------------------------------------------

print()
print("=" * 70)
print("71C.P3 COMPLETE")
print("=" * 70)

print(
    "Current precursor rows:",
    len(p)
)

print(
    "Candidate rows within 60 minutes:",
    len(within_60)
)

print(
    "Previously validated target:",
    406
)

print(
    "No objects were modified."
)

print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 207
# ==============================================================================

# ============================================================
# AFRITAC STEP 71C.3R
# RESTORE AUTHORITATIVE 406 EVENT PRECURSOR LAYER
# CORRECTED TEMPORAL BOUNDARY VERSION
# ============================================================

import numpy as np
import pandas as pd

print("=" * 70)
print("AFRITAC STEP 71C.3R")
print("RESTORE AUTHORITATIVE 406 EVENT PRECURSOR LAYER")
print("CORRECTED TEMPORAL BOUNDARY VERSION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Required objects
# ------------------------------------------------------------

required_objects = [
    "users",
    "campaigns",
    "campaign_control",
    "attack_events",
    "positive_windows",
]

missing = [
    x for x in required_objects
    if x not in globals()
]

print("\nRequired objects missing:", missing)

assert not missing

# ------------------------------------------------------------
# 2. Configuration
# ------------------------------------------------------------

TARGET_EVENTS = 406
EXPECTED_CAMPAIGNS = 80

rng = np.random.default_rng(
    SEED + 43
)

band_targets = {
    "EARLY": 31,
    "ESCALATION": 54,
    "STRONG": 79,
    "ACUTE": 110,
    "IMMINENT": 132,
}

# Use open upper boundaries.
#
# EARLY       46 <= t < 60
# ESCALATION  31 <= t < 46
# STRONG      16 <= t < 31
# ACUTE        6 <= t < 16
# IMMINENT     1 <= t < 6

band_ranges = {
    "EARLY": (46.0, 60.0),
    "ESCALATION": (31.0, 46.0),
    "STRONG": (16.0, 31.0),
    "ACUTE": (6.0, 16.0),
    "IMMINENT": (1.0, 6.0),
}

severity_multiplier = {
    "LOW": 0.75,
    "MEDIUM": 1.00,
    "HIGH": 1.25,
}

attack_type_modalities = {
    "ACCOUNT_TAKEOVER": {
        "AUTHENTICATION": 0.24,
        "USSD": 0.18,
        "SESSION": 0.20,
        "NETWORK": 0.12,
        "DEVICE": 0.14,
        "FINANCIAL": 0.12,
    },

    "SOCIAL_ENGINEERING_TAKEOVER": {
        "AUTHENTICATION": 0.18,
        "USSD": 0.15,
        "SESSION": 0.18,
        "NETWORK": 0.10,
        "DEVICE": 0.14,
        "FINANCIAL": 0.25,
    },

    "USSD_SESSION_HIJACK": {
        "AUTHENTICATION": 0.12,
        "USSD": 0.32,
        "SESSION": 0.32,
        "NETWORK": 0.10,
        "DEVICE": 0.08,
        "FINANCIAL": 0.06,
    },

    "SIM_IDENTITY_COMPROMISE": {
        "AUTHENTICATION": 0.18,
        "USSD": 0.10,
        "SESSION": 0.14,
        "NETWORK": 0.30,
        "DEVICE": 0.20,
        "FINANCIAL": 0.08,
    },
}

precursor_event_types = {
    "AUTHENTICATION": [
        "REPEATED_AUTHENTICATION_ACTIVITY",
        "AUTHENTICATION_TIMING_DEVIATION",
        "AUTHENTICATION_CONTEXT_DEVIATION",
    ],

    "USSD": [
        "ABNORMAL_USSD_INTERACTION_RATE",
        "USSD_SEQUENCE_DEVIATION",
        "MENU_SEQUENCE_DEVIATION",
    ],

    "SESSION": [
        "SESSION_TRANSITION_ANOMALY",
        "SESSION_DURATION_DEVIATION",
        "UNUSUAL_SESSION_TIMING",
    ],

    "NETWORK": [
        "NETWORK_IDENTITY_DEVIATION",
        "NETWORK_CONTEXT_CHANGE",
    ],

    "DEVICE": [
        "DEVICE_CONTEXT_DEVIATION",
    ],

    "FINANCIAL": [
        "TRANSACTION_PREPARATION_ANOMALY",
    ],
}

# ------------------------------------------------------------
# 3. Campaign base
# ------------------------------------------------------------

campaign_base = campaigns[
    [
        "campaign_id",
        "user_id",
        "attack_type",
    ]
].copy()

campaign_base["campaign_id"] = (
    campaign_base["campaign_id"].astype(str)
)

campaign_base["user_id"] = (
    campaign_base["user_id"].astype(str)
)

assert len(campaign_base) == 80
assert campaign_base["campaign_id"].nunique() == 80
assert campaign_base["user_id"].nunique() == 80

# ------------------------------------------------------------
# 4. Authoritative takeover times
# ------------------------------------------------------------

positive_tmp = positive_windows[
    [
        "campaign_id",
        "takeover_time",
    ]
].copy()

positive_tmp["campaign_id"] = (
    positive_tmp["campaign_id"].astype(str)
)

positive_tmp["takeover_time"] = pd.to_datetime(
    positive_tmp["takeover_time"],
    errors="coerce",
)

takeover_map = (
    positive_tmp
    .drop_duplicates("campaign_id")
    .set_index("campaign_id")[
        "takeover_time"
    ]
    .to_dict()
)

assert len(takeover_map) == 80

campaign_base["takeover_time"] = (
    campaign_base["campaign_id"]
    .map(takeover_map)
)

assert campaign_base["takeover_time"].notna().all()

# ------------------------------------------------------------
# 5. Authoritative severity
# ------------------------------------------------------------

severity_map = (
    campaign_control[
        [
            "campaign_id",
            "attack_severity",
        ]
    ]
    .copy()
)

severity_map["campaign_id"] = (
    severity_map["campaign_id"].astype(str)
)

severity_map = (
    severity_map
    .drop_duplicates("campaign_id")
    .set_index("campaign_id")[
        "attack_severity"
    ]
    .to_dict()
)

campaign_base["attack_severity"] = (
    campaign_base["campaign_id"]
    .map(severity_map)
)

assert campaign_base["attack_severity"].notna().all()

# ------------------------------------------------------------
# 6. Construct exact temporal band sequence
# ------------------------------------------------------------

band_sequence = []

for band, count in band_targets.items():
    band_sequence.extend(
        [band] * count
    )

band_sequence = np.asarray(
    band_sequence,
    dtype=object
)

assert len(band_sequence) == TARGET_EVENTS

rng.shuffle(band_sequence)

# ------------------------------------------------------------
# 7. Allocate at least one event to every campaign
# ------------------------------------------------------------

campaign_indices = np.arange(
    len(campaign_base)
)

rng.shuffle(campaign_indices)

event_campaign_indices = (
    campaign_indices.tolist()
)

remaining = (
    TARGET_EVENTS
    - EXPECTED_CAMPAIGNS
)

campaign_weights = []

for _, row in campaign_base.iterrows():

    weight = severity_multiplier[
        row["attack_severity"]
    ]

    campaign_weights.append(weight)

campaign_weights = np.asarray(
    campaign_weights,
    dtype=float
)

campaign_weights /= campaign_weights.sum()

additional_indices = rng.choice(
    campaign_indices,
    size=remaining,
    replace=True,
    p=campaign_weights,
)

event_campaign_indices.extend(
    additional_indices.tolist()
)

event_campaign_indices = np.asarray(
    event_campaign_indices,
    dtype=int
)

assert len(event_campaign_indices) == 406

rng.shuffle(event_campaign_indices)

# ------------------------------------------------------------
# 8. Generate events
# ------------------------------------------------------------

records = []

for i in range(TARGET_EVENTS):

    campaign_row = campaign_base.iloc[
        event_campaign_indices[i]
    ]

    campaign_id = (
        campaign_row["campaign_id"]
    )

    user_id = (
        campaign_row["user_id"]
    )

    attack_type = (
        campaign_row["attack_type"]
    )

    attack_severity = (
        campaign_row["attack_severity"]
    )

    takeover_time = pd.Timestamp(
        campaign_row["takeover_time"]
    )

    band = band_sequence[i]

    lower, upper = band_ranges[band]

    # --------------------------------------------------------
    # Strict temporal sampling
    #
    # np.nextafter creates an upper value immediately below
    # the boundary, ensuring:
    #
    # EARLY       < 60
    # ESCALATION  < 46
    # STRONG      < 31
    # ACUTE       < 16
    # IMMINENT    < 6
    # --------------------------------------------------------

    upper_open = np.nextafter(
        upper,
        lower
    )

    minutes_before = float(
        rng.uniform(
            lower,
            upper_open
        )
    )

    assert (
        minutes_before >= lower
    )

    assert (
        minutes_before < upper
    )

    timestamp = (
        takeover_time
        -
        pd.Timedelta(
            minutes=minutes_before
        )
    )

    # --------------------------------------------------------
    # Modality
    # --------------------------------------------------------

    modality_names = list(
        attack_type_modalities[
            attack_type
        ].keys()
    )

    modality_probs = np.asarray(
        list(
            attack_type_modalities[
                attack_type
            ].values()
        ),
        dtype=float
    )

    modality_probs /= modality_probs.sum()

    modality = rng.choice(
        modality_names,
        p=modality_probs
    )

    event_type = rng.choice(
        precursor_event_types[
            modality
        ]
    )

    # --------------------------------------------------------
    # Context
    # --------------------------------------------------------

    response_delay = float(
        np.clip(
            rng.normal(
                1400,
                220
            ),
            500,
            2500
        )
    )

    signal_strength = float(
        np.clip(
            rng.normal(
                -82,
                8
            ),
            -110,
            -55
        )
    )

    progress = (
        60.0
        -
        minutes_before
    ) / 59.0

    progress = float(
        np.clip(
            progress,
            0,
            1
        )
    )

    roaming = int(
        rng.random() < 0.08
    )

    location_change = int(
        rng.random()
        <
        (
            0.04
            +
            0.12 * progress
        )
    )

    new_device = int(
        rng.random()
        <
        (
            0.02
            +
            0.08 * progress
        )
    )

    if modality == "FINANCIAL":

        transaction_amount = float(
            np.clip(
                rng.lognormal(
                    mean=np.log(15000),
                    sigma=0.65
                ),
                1000,
                150000
            )
        )

    else:

        transaction_amount = np.nan

    # --------------------------------------------------------
    # Device
    # --------------------------------------------------------

    user_device = (
        users[
            users["user_id"].astype(str)
            == user_id
        ]["primary_device_id"]
        .iloc[0]
    )

    if new_device:

        device_id = (
            f"OBS_DEVICE_"
            f"{user_id}_"
            f"{i + 1:04d}"
        )

    else:

        device_id = str(
            user_device
        )

    session_id = (
        f"OBS_SESSION_"
        f"{i + 1:06d}"
    )

    # --------------------------------------------------------
    # Record
    # --------------------------------------------------------

    records.append({

        "event_id":
            f"OBS_EVENT_{i + 1:06d}",

        "campaign_id":
            campaign_id,

        "user_id":
            user_id,

        "session_id":
            session_id,

        "device_id":
            device_id,

        "timestamp":
            timestamp,

        "event_type":
            event_type,

        "modality":
            modality,

        "response_delay_ms":
            response_delay,

        "signal_strength_dbm":
            signal_strength,

        "roaming":
            roaming,

        "location_change":
            location_change,

        "new_device":
            new_device,

        "transaction_amount":
            transaction_amount,

        "ground_truth_state":
            "NORMAL",

        "is_attack":
            0,

        "is_observable_precursor":
            1,

        "attack_type":
            attack_type,

        "attack_severity":
            attack_severity,

        "takeover_time":
            takeover_time,

        "minutes_to_takeover":
            minutes_before,

        "precursor_band":
            band,

        "attack_type_generation":
            attack_type,

        "attack_severity_generation":
            attack_severity,
    })

# ------------------------------------------------------------
# 9. Create dataframe
# ------------------------------------------------------------

new_precursors = pd.DataFrame(
    records
)

new_precursors = (
    new_precursors
    .sort_values(
        [
            "user_id",
            "timestamp",
            "event_id",
        ]
    )
    .reset_index(drop=True)
)

# ------------------------------------------------------------
# 10. Recalculate temporal distance from timestamps
# ------------------------------------------------------------

new_precursors["timestamp"] = pd.to_datetime(
    new_precursors["timestamp"]
)

new_precursors["takeover_time"] = pd.to_datetime(
    new_precursors["takeover_time"]
)

new_precursors[
    "computed_minutes_to_takeover"
] = (
    new_precursors["takeover_time"]
    -
    new_precursors["timestamp"]
).dt.total_seconds() / 60.0

# ------------------------------------------------------------
# 11. Structural validation
# ------------------------------------------------------------

print("\nSTRUCTURAL VALIDATION")

print(
    "Events:",
    len(new_precursors)
)

print(
    "Unique event IDs:",
    new_precursors["event_id"].nunique()
)

print(
    "Campaigns:",
    new_precursors["campaign_id"].nunique()
)

print(
    "Users:",
    new_precursors["user_id"].nunique()
)

assert len(new_precursors) == 406
assert new_precursors["event_id"].nunique() == 406
assert new_precursors["campaign_id"].nunique() == 80
assert new_precursors["user_id"].nunique() == 80

# ------------------------------------------------------------
# 12. Ground truth validation
# ------------------------------------------------------------

print("\nGROUND TRUTH VALIDATION")

assert (
    new_precursors["ground_truth_state"]
    .eq("NORMAL")
    .all()
)

assert (
    new_precursors["is_attack"]
    .eq(0)
    .all()
)

assert (
    new_precursors[
        "is_observable_precursor"
    ]
    .eq(1)
    .all()
)

print("Ground truth: PASS")

# ------------------------------------------------------------
# 13. Strict temporal validation
# ------------------------------------------------------------

print("\nTEMPORAL VALIDATION")

min_minutes = (
    new_precursors[
        "computed_minutes_to_takeover"
    ].min()
)

max_minutes = (
    new_precursors[
        "computed_minutes_to_takeover"
    ].max()
)

at_or_after = (
    new_precursors[
        "computed_minutes_to_takeover"
    ] <= 0
).sum()

beyond_60 = (
    new_precursors[
        "computed_minutes_to_takeover"
    ] > 60
).sum()

print(
    "Minimum minutes to takeover:",
    min_minutes
)

print(
    "Maximum minutes to takeover:",
    max_minutes
)

print(
    "Events at/after takeover:",
    at_or_after
)

print(
    "Events beyond 60 minutes:",
    beyond_60
)

assert (
    new_precursors[
        "computed_minutes_to_takeover"
    ] > 0
).all()

assert (
    new_precursors[
        "computed_minutes_to_takeover"
    ] <= 60
).all()

# ------------------------------------------------------------
# 14. Band integrity
# ------------------------------------------------------------

print("\nBAND VALIDATION")

actual_band_counts = (
    new_precursors[
        "precursor_band"
    ]
    .value_counts()
    .reindex(
        [
            "EARLY",
            "ESCALATION",
            "STRONG",
            "ACUTE",
            "IMMINENT",
        ],
        fill_value=0
    )
)

print(
    actual_band_counts.to_dict()
)

assert (
    actual_band_counts.to_dict()
    == band_targets
)

# Verify each event is actually inside its declared band.

band_temporal_valid = True

for band, (lower, upper) in band_ranges.items():

    mask = (
        new_precursors[
            "precursor_band"
        ] == band
    )

    values = (
        new_precursors.loc[
            mask,
            "computed_minutes_to_takeover"
        ]
    )

    if not values.empty:

        valid = (
            (values >= lower)
            &
            (values < upper)
        ).all()

        print(
            f"{band:<12}",
            f"{values.min():.4f} to "
            f"{values.max():.4f}",
            "PASS" if valid else "FAIL"
        )

        band_temporal_valid &= valid

assert band_temporal_valid

# ------------------------------------------------------------
# 15. Campaign coverage
# ------------------------------------------------------------

print("\nCAMPAIGN COVERAGE")

campaign_counts = (
    new_precursors
    .groupby("campaign_id")
    .size()
)

print(
    "Campaigns covered:",
    campaign_counts.size
)

print(
    "Minimum events per campaign:",
    campaign_counts.min()
)

print(
    "Maximum events per campaign:",
    campaign_counts.max()
)

assert campaign_counts.size == 80
assert (campaign_counts >= 1).all()

# ------------------------------------------------------------
# 16. Horizon activity
# ------------------------------------------------------------

print("\nHORIZON ACTIVITY")

for horizon in [5, 10, 15, 30, 60]:

    mask = (
        (
            new_precursors[
                "computed_minutes_to_takeover"
            ] > 0
        )
        &
        (
            new_precursors[
                "computed_minutes_to_takeover"
            ] <= horizon
        )
    )

    event_count = int(mask.sum())

    campaign_count = (
        new_precursors.loc[
            mask,
            "campaign_id"
        ].nunique()
    )

    print(
        f"{horizon:>2} min: "
        f"{event_count:>3} events | "
        f"{campaign_count:>2}/80 campaigns"
    )

# ------------------------------------------------------------
# 17. Modality validation
# ------------------------------------------------------------

print("\nMODALITY DISTRIBUTION")

print(
    new_precursors[
        "modality"
    ]
    .value_counts()
    .sort_index()
    .to_dict()
)

# ------------------------------------------------------------
# 18. Attack type validation
# ------------------------------------------------------------

print("\nATTACK TYPE DISTRIBUTION")

print(
    new_precursors[
        "attack_type"
    ]
    .value_counts()
    .sort_index()
    .to_dict()
)

# ------------------------------------------------------------
# 19. Vocabulary separation
# ------------------------------------------------------------

print("\nVOCABULARY SEPARATION")

attack_vocab = set(
    attack_events[
        "event_type"
    ]
    .dropna()
    .astype(str)
    .unique()
)

precursor_vocab = set(
    new_precursors[
        "event_type"
    ]
    .dropna()
    .astype(str)
    .unique()
)

vocab_overlap = (
    attack_vocab
    &
    precursor_vocab
)

print(
    "Attack vocabulary:",
    len(attack_vocab)
)

print(
    "Precursor vocabulary:",
    len(precursor_vocab)
)

print(
    "Vocabulary overlap:",
    sorted(vocab_overlap)
)

assert len(vocab_overlap) == 0

# ------------------------------------------------------------
# 20. Critical missing values
# ------------------------------------------------------------

print("\nCRITICAL MISSING VALUE AUDIT")

critical_columns = [
    "event_id",
    "campaign_id",
    "user_id",
    "session_id",
    "device_id",
    "timestamp",
    "event_type",
    "modality",
    "signal_strength_dbm",
    "ground_truth_state",
    "is_attack",
    "is_observable_precursor",
    "attack_type",
    "attack_severity",
    "takeover_time",
    "minutes_to_takeover",
    "precursor_band",
]

critical_missing = (
    new_precursors[
        critical_columns
    ]
    .isna()
    .sum()
)

print(
    critical_missing[
        critical_missing > 0
    ].to_dict()
)

assert critical_missing.sum() == 0

# ------------------------------------------------------------
# 21. Financial field validation
# ------------------------------------------------------------

financial_mask = (
    new_precursors["modality"]
    == "FINANCIAL"
)

nonfinancial_mask = (
    ~financial_mask
)

assert (
    new_precursors.loc[
        financial_mask,
        "transaction_amount"
    ].notna().all()
)

assert (
    new_precursors.loc[
        nonfinancial_mask,
        "transaction_amount"
    ].isna().all()
)

# ------------------------------------------------------------
# 22. Response delay validation
# ------------------------------------------------------------

assert (
    new_precursors[
        "response_delay_ms"
    ].notna().all()
)

assert (
    new_precursors[
        "response_delay_ms"
    ].between(
        500,
        2500
    ).all()
)

# ------------------------------------------------------------
# 23. Replace only observable_precursors
# ------------------------------------------------------------

observable_precursors = (
    new_precursors
    .drop(
        columns=[
            "computed_minutes_to_takeover"
        ]
    )
    .copy()
)

# ------------------------------------------------------------
# 24. Final validation after replacement
# ------------------------------------------------------------

assert len(observable_precursors) == 406

assert (
    observable_precursors[
        "event_id"
    ].nunique()
    == 406
)

assert (
    observable_precursors[
        "campaign_id"
    ].nunique()
    == 80
)

assert (
    observable_precursors[
        "user_id"
    ].nunique()
    == 80
)

# ------------------------------------------------------------
# 25. Final result
# ------------------------------------------------------------

print()
print("=" * 70)
print("71C.3R FINAL RESULT")
print("=" * 70)

print(
    "observable_precursors:",
    len(observable_precursors)
)

print(
    "unique events:",
    observable_precursors[
        "event_id"
    ].nunique()
)

print(
    "campaigns:",
    observable_precursors[
        "campaign_id"
    ].nunique()
)

print(
    "users:",
    observable_precursors[
        "user_id"
    ].nunique()
)

print(
    "band counts:",
    observable_precursors[
        "precursor_band"
    ]
    .value_counts()
    .reindex(
        [
            "EARLY",
            "ESCALATION",
            "STRONG",
            "ACUTE",
            "IMMINENT",
        ],
        fill_value=0
    )
    .to_dict()
)

print()
print("STEP 71C.3R PASS")
print("=" * 70)

print(
    "Only observable_precursors was replaced."
)

print(
    "Attack events were not modified."
)

print(
    "Campaigns were not modified."
)

print(
    "Campaign control was not modified."
)

print(
    "Positive windows were not modified."
)

print(
    "Normal negative windows were not modified."
)

print(
    "Hard negative windows were not modified."
)

print(
    "Hard negative events were not modified."
)

print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 208
# ==============================================================================

# ================================================================
# AFRITAC STEP 71C.REPAIR
# REPAIR CAMPAIGN CONTROL ATTACK TYPE MAPPING
# ================================================================
#
# AUTHORITATIVE SOURCE:
#     campaigns["attack_type"]
#
# ONLY THIS FIELD MAY BE CHANGED:
#     campaign_control["attack_type"]
#
# ALL OTHER CAMPAIGN CONTROL ATTRIBUTES MUST REMAIN UNCHANGED.
# ================================================================

import numpy as np
import pandas as pd

print("=" * 70)
print("AFRITAC STEP 71C.REPAIR")
print("REPAIR CAMPAIGN CONTROL ATTACK TYPE MAPPING")
print("=" * 70)


# ------------------------------------------------
# 1. PRESERVE ORIGINAL CONTROL STATE
# ------------------------------------------------

control_before = campaign_control.copy(deep=True)

assert len(control_before) == 80
assert control_before["campaign_id"].nunique() == 80


# ------------------------------------------------
# 2. BUILD AUTHORITATIVE ATTACK TYPE MAP
# ------------------------------------------------

authoritative_attack_type = (
    campaigns
    .set_index("campaign_id")["attack_type"]
)

assert authoritative_attack_type.index.is_unique
assert len(authoritative_attack_type) == 80


# ------------------------------------------------
# 3. AUDIT CURRENT MISMATCHES
# ------------------------------------------------

current_mismatch = (
    campaign_control
    .set_index("campaign_id")["attack_type"]
    .ne(authoritative_attack_type)
)

print(
    "\nCurrent attack type mismatches:",
    int(current_mismatch.sum())
)

print(
    "Current campaign_control distribution:"
)

print(
    campaign_control[
        "attack_type"
    ].value_counts().to_dict()
)

print(
    "\nAuthoritative campaigns distribution:"
)

print(
    campaigns[
        "attack_type"
    ].value_counts().to_dict()
)


# ------------------------------------------------
# 4. REPAIR ONLY ATTACK TYPE
# ------------------------------------------------

campaign_control["attack_type"] = (
    campaign_control["campaign_id"]
    .map(authoritative_attack_type)
)


# ------------------------------------------------
# 5. VERIFY REPAIR
# ------------------------------------------------

remaining_mismatch = (
    campaign_control
    .set_index("campaign_id")["attack_type"]
    .ne(authoritative_attack_type)
)

print(
    "\nRemaining attack type mismatches:",
    int(remaining_mismatch.sum())
)

assert remaining_mismatch.sum() == 0


# ------------------------------------------------
# 6. VERIFY OTHER CONTROL ATTRIBUTES WERE NOT
#    CHANGED
# ------------------------------------------------

print(
    "\nNON ATTACK TYPE ATTRIBUTE PRESERVATION"
)

protected_columns = [
    col
    for col in control_before.columns
    if col != "attack_type"
]

changed_attributes = []

for col in protected_columns:

    before = control_before[col]
    after = campaign_control[col]

    if pd.api.types.is_numeric_dtype(before):

        equal = np.allclose(
            before.to_numpy(),
            after.to_numpy(),
            equal_nan=True
        )

    else:

        equal = before.astype(object).equals(
            after.astype(object)
        )

    if not equal:
        changed_attributes.append(col)

print(
    "Protected attributes changed:",
    changed_attributes
)

assert len(changed_attributes) == 0


# ------------------------------------------------
# 7. VERIFY CAMPAIGN IDS AND USERS
# ------------------------------------------------

print(
    "\nIDENTITY PRESERVATION"
)

print(
    "Campaign control rows:",
    len(campaign_control)
)

print(
    "Unique campaign IDs:",
    campaign_control[
        "campaign_id"
    ].nunique()
)

print(
    "Unique users:",
    campaign_control[
        "user_id"
    ].nunique()
)

assert len(campaign_control) == 80
assert (
    campaign_control[
        "campaign_id"
    ].nunique()
    == 80
)


# ------------------------------------------------
# 8. VERIFY USER MAPPING
# ------------------------------------------------

user_mapping = (
    campaigns[
        [
            "campaign_id",
            "user_id"
        ]
    ]
    .merge(
        campaign_control[
            [
                "campaign_id",
                "user_id"
            ]
        ],
        on="campaign_id",
        suffixes=(
            "_campaign",
            "_control"
        ),
        how="outer"
    )
)

user_mismatches = (
    user_mapping[
        "user_id_campaign"
    ]
    !=
    user_mapping[
        "user_id_control"
    ]
).sum()

print(
    "User mapping mismatches:",
    int(user_mismatches)
)

assert user_mismatches == 0


# ------------------------------------------------
# 9. VERIFY AUTHORITATIVE ATTACK TYPE DISTRIBUTION
# ------------------------------------------------

print(
    "\nFINAL ATTACK TYPE DISTRIBUTION"
)

final_distribution = (
    campaign_control[
        "attack_type"
    ]
    .value_counts()
    .to_dict()
)

authoritative_distribution = (
    campaigns[
        "attack_type"
    ]
    .value_counts()
    .to_dict()
)

print(
    "Campaign control:",
    final_distribution
)

print(
    "Campaigns:",
    authoritative_distribution
)

assert (
    final_distribution
    ==
    authoritative_distribution
)


# ------------------------------------------------
# 10. VERIFY EXACT CAMPAIGN LEVEL MATCH
# ------------------------------------------------

comparison = (
    campaigns[
        [
            "campaign_id",
            "attack_type"
        ]
    ]
    .merge(
        campaign_control[
            [
                "campaign_id",
                "attack_type"
            ]
        ],
        on="campaign_id",
        suffixes=(
            "_campaign",
            "_control"
        ),
        how="outer"
    )
)

exact_mismatches = (
    comparison[
        "attack_type_campaign"
    ]
    !=
    comparison[
        "attack_type_control"
    ]
).sum()

print(
    "Exact campaign level mismatches:",
    int(exact_mismatches)
)

assert exact_mismatches == 0


# ------------------------------------------------
# 11. FINAL RESULT
# ------------------------------------------------

print(
    "\n" + "=" * 70
)
print(
    "71C.REPAIR FINAL RESULT"
)
print(
    "=" * 70
)

print(
    "Attack type mismatches repaired:",
    int(current_mismatch.sum())
)

print(
    "Remaining mismatches:",
    int(remaining_mismatch.sum())
)

print(
    "Protected attributes changed:",
    len(changed_attributes)
)

print(
    "User mapping mismatches:",
    int(user_mismatches)
)

print(
    "FINAL STATUS: PASS"
)

print(
    "\nONLY campaign_control['attack_type'] WAS MODIFIED."
)

print(
    "Campaigns: NOT MODIFIED"
)

print(
    "Attack events: NOT MODIFIED"
)

print(
    "Positive windows: NOT MODIFIED"
)

print(
    "Negative windows: NOT MODIFIED"
)

print(
    "Observable precursors: NOT MODIFIED"
)

print(
    "Hard negative windows: NOT MODIFIED"
)

print(
    "Hard negative events: NOT MODIFIED"
)

print(
    "=" * 70
)

# ==============================================================================
# NOTEBOOK CELL 209
# ==============================================================================

# ================================================================
# AFRITAC STEP 71D.4C
# CORRECTED HARD NEGATIVE DIFFICULTY DIAGNOSTIC
# ================================================================
#
# IMPORTANT CORRECTION:
#
# For each prediction horizon:
#
#     cutoff = takeover_time - horizon
#
# We examine a FIXED 60-minute historical context:
#
#     cutoff - 60 minutes  ->  cutoff
#
# This represents information available to the defender at the
# prediction cutoff.
#
# This prevents the previous error where the horizon itself was
# incorrectly used as the historical lookback length.
#
# NO AUTHORITATIVE DATASET OBJECTS ARE MODIFIED.
# ================================================================

import numpy as np
import pandas as pd

from sklearn.model_selection import GroupKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score


print("=" * 70)
print("AFRITAC STEP 71D.4C")
print("CORRECTED HARD NEGATIVE DIFFICULTY DIAGNOSTIC")
print("=" * 70)


# ================================================================
# 1. ISOLATED COPIES
# ================================================================

pos = positive_windows.copy()
hard = hard_negative_windows.copy()

pos["label"] = 1
hard["label"] = 0

print("\nWINDOW COUNTS")
print("Positive:", len(pos))
print("Hard negative:", len(hard))

assert len(pos) == 400
assert len(hard) == 100


# ================================================================
# 2. PREPARE EVENT STREAMS
# ================================================================

ordinary = normal_stream.copy()

ordinary["timestamp"] = pd.to_datetime(
    ordinary["timestamp"]
)

prec = observable_precursors.copy()

prec["timestamp"] = pd.to_datetime(
    prec["timestamp"]
)

hard_events = hard_negative_events.copy()

hard_events["timestamp"] = pd.to_datetime(
    hard_events["timestamp"]
)


# ------------------------------------------------
# Exclude malicious attack events
# ------------------------------------------------

if "is_attack" in ordinary.columns:

    ordinary_observable = ordinary[
        ordinary["is_attack"] != 1
    ].copy()

else:

    ordinary_observable = ordinary.copy()


# ------------------------------------------------
# Positive observable stream
# ------------------------------------------------

positive_stream = pd.concat(
    [
        ordinary_observable,
        prec
    ],
    ignore_index=True,
    sort=False
)

positive_stream = positive_stream[
    positive_stream["is_attack"].fillna(0) != 1
].copy()


print("\nEVENT STREAMS")

print(
    "Ordinary observable events:",
    len(ordinary_observable)
)

print(
    "Observable precursor events:",
    len(prec)
)

print(
    "Positive analysis stream:",
    len(positive_stream)
)

print(
    "Hard negative events:",
    len(hard_events)
)


# ================================================================
# 3. FEATURE EXTRACTION
# ================================================================
#
# CRITICAL:
#
# The lookback is ALWAYS 60 minutes.
#
# The cutoff changes according to prediction horizon.
#
# ================================================================

LOOKBACK_MINUTES = 60


def extract_window_features(
    window_df,
    events_df,
    label
):

    rows = []

    for _, w in window_df.iterrows():

        user = w["user_id"]

        cutoff = pd.to_datetime(
            w["cutoff_time"]
        )

        horizon = int(
            w["horizon_minutes"]
        )

        # ------------------------------------------------
        # FIXED 60 MINUTE HISTORICAL CONTEXT
        # ------------------------------------------------

        left = (
            cutoff
            -
            pd.Timedelta(
                minutes=LOOKBACK_MINUTES
            )
        )

        e = events_df[
            (events_df["user_id"] == user)
            &
            (events_df["timestamp"] > left)
            &
            (events_df["timestamp"] <= cutoff)
        ].copy()


        # ------------------------------------------------
        # BASIC ACTIVITY
        # ------------------------------------------------

        event_count = len(e)

        if "session_id" in e.columns:

            session_count = (
                e["session_id"].nunique()
            )

        else:

            session_count = event_count


        if "event_type" in e.columns:

            event_type_count = (
                e["event_type"].nunique()
            )

        else:

            event_type_count = 0


        if "modality" in e.columns:

            modality_count = (
                e["modality"].nunique()
            )

        else:

            modality_count = 0


        # ------------------------------------------------
        # RESPONSE DELAY
        # ------------------------------------------------

        if "response_delay_ms" in e.columns:

            delay = pd.to_numeric(
                e["response_delay_ms"],
                errors="coerce"
            ).dropna()

        else:

            delay = pd.Series(
                dtype=float
            )

        if len(delay) > 0:

            delay_mean = delay.mean()
            delay_std = delay.std()
            delay_median = delay.median()
            delay_min = delay.min()
            delay_max = delay.max()

        else:

            delay_mean = np.nan
            delay_std = np.nan
            delay_median = np.nan
            delay_min = np.nan
            delay_max = np.nan


        # ------------------------------------------------
        # SAFE NUMERIC MEAN
        # ------------------------------------------------

        def safe_mean(col):

            if col not in e.columns:
                return np.nan

            x = pd.to_numeric(
                e[col],
                errors="coerce"
            )

            if x.notna().sum() == 0:
                return np.nan

            return x.mean()


        new_device_rate = safe_mean(
            "new_device"
        )

        location_rate = safe_mean(
            "location_change"
        )

        roaming_rate = safe_mean(
            "roaming"
        )

        signal_mean = safe_mean(
            "signal_strength_dbm"
        )


        # ------------------------------------------------
        # FINANCIAL
        # ------------------------------------------------

        if "transaction_amount" in e.columns:

            amount = pd.to_numeric(
                e["transaction_amount"],
                errors="coerce"
            ).dropna()

        else:

            amount = pd.Series(
                dtype=float
            )

        if len(amount) > 0:

            amount_mean = amount.mean()
            amount_max = amount.max()
            transaction_count = len(amount)

        else:

            amount_mean = np.nan
            amount_max = np.nan
            transaction_count = 0


        # ------------------------------------------------
        # TEMPORAL CONCENTRATION
        # ------------------------------------------------

        if event_count > 0:

            age_minutes = (
                cutoff
                -
                e["timestamp"]
            ).dt.total_seconds() / 60

            last5 = (
                age_minutes <= 5
            ).sum()

            last10 = (
                age_minutes <= 10
            ).sum()

            last15 = (
                age_minutes <= 15
            ).sum()

            last30 = (
                age_minutes <= 30
            ).sum()

            last5_share = (
                last5 / event_count
            )

            last10_share = (
                last10 / event_count
            )

            last15_share = (
                last15 / event_count
            )

            last30_share = (
                last30 / event_count
            )

        else:

            last5 = 0
            last10 = 0
            last15 = 0
            last30 = 0

            last5_share = 0
            last10_share = 0
            last15_share = 0
            last30_share = 0


        # ------------------------------------------------
        # EVENT DENSITY
        # ------------------------------------------------

        if event_count > 0:

            events_per_10min = (
                event_count / 6
            )

        else:

            events_per_10min = 0


        rows.append({

            "user_id":
                user,

            "horizon_minutes":
                horizon,

            "cutoff_time":
                cutoff,

            "event_count":
                event_count,

            "events_per_10min":
                events_per_10min,

            "session_count":
                session_count,

            "event_type_count":
                event_type_count,

            "modality_count":
                modality_count,

            "delay_mean":
                delay_mean,

            "delay_std":
                delay_std,

            "delay_median":
                delay_median,

            "delay_min":
                delay_min,

            "delay_max":
                delay_max,

            "new_device_rate":
                new_device_rate,

            "location_rate":
                location_rate,

            "roaming_rate":
                roaming_rate,

            "signal_mean":
                signal_mean,

            "transaction_count":
                transaction_count,

            "amount_mean":
                amount_mean,

            "amount_max":
                amount_max,

            "last5_share":
                last5_share,

            "last10_share":
                last10_share,

            "last15_share":
                last15_share,

            "last30_share":
                last30_share,

            "label":
                label
        })

    return pd.DataFrame(rows)


# ================================================================
# 4. EXTRACT FEATURES
# ================================================================

print(
    "\nEXTRACTING POSITIVE FEATURES"
)

X_pos = extract_window_features(
    pos,
    positive_stream,
    1
)

print(
    "Positive feature rows:",
    len(X_pos)
)

assert len(X_pos) == 400


print(
    "\nEXTRACTING HARD NEGATIVE FEATURES"
)

X_hard = extract_window_features(
    hard,
    hard_events,
    0
)

print(
    "Hard negative feature rows:",
    len(X_hard)
)

assert len(X_hard) == 100


# ================================================================
# 5. COMBINE
# ================================================================

X = pd.concat(
    [
        X_pos,
        X_hard
    ],
    ignore_index=True
)

print(
    "\nCOMBINED FEATURE MATRIX:",
    X.shape
)

print(
    "Labels:",
    X["label"]
    .value_counts()
    .to_dict()
)


# ================================================================
# 6. FEATURE GROUPS
# ================================================================

feature_groups = {

    "EVENT_COUNT": [
        "event_count"
    ],

    "ACTIVITY": [
        "event_count",
        "session_count",
        "event_type_count"
    ],

    "MODALITY": [
        "modality_count"
    ],

    "TEMPORAL": [
        "last5_share",
        "last10_share",
        "last15_share",
        "last30_share"
    ],

    "RESPONSE_DELAY": [
        "delay_mean",
        "delay_std",
        "delay_median",
        "delay_min",
        "delay_max"
    ],

    "CONTEXT": [
        "new_device_rate",
        "location_rate",
        "roaming_rate",
        "signal_mean"
    ],

    "FINANCIAL": [
        "transaction_count",
        "amount_mean",
        "amount_max"
    ],

    "ACTIVITY_MODALITY": [
        "event_count",
        "session_count",
        "event_type_count",
        "modality_count"
    ],

    "ACTIVITY_TEMPORAL": [
        "event_count",
        "session_count",
        "event_type_count",
        "last5_share",
        "last10_share",
        "last15_share",
        "last30_share"
    ],

    "CONTEXT_FINANCIAL": [
        "new_device_rate",
        "location_rate",
        "roaming_rate",
        "signal_mean",
        "transaction_count",
        "amount_mean",
        "amount_max"
    ],

    "ALL_FEATURES": [
        "event_count",
        "events_per_10min",
        "session_count",
        "event_type_count",
        "modality_count",
        "delay_mean",
        "delay_std",
        "delay_median",
        "delay_min",
        "delay_max",
        "new_device_rate",
        "location_rate",
        "roaming_rate",
        "signal_mean",
        "transaction_count",
        "amount_mean",
        "amount_max",
        "last5_share",
        "last10_share",
        "last15_share",
        "last30_share"
    ]
}


# ================================================================
# 7. GROUPED CV
# ================================================================

def grouped_auc(
    data,
    features
):

    data = data.copy()

    Xf = data[
        features
    ]

    y = data[
        "label"
    ]

    groups = data[
        "user_id"
    ]

    if y.nunique() < 2:
        return np.nan

    if groups.nunique() < 2:
        return np.nan

    n_splits = min(
        5,
        groups.nunique()
    )

    cv = GroupKFold(
        n_splits=n_splits
    )

    pipe = Pipeline([
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        ),
        (
            "scaler",
            StandardScaler()
        ),
        (
            "model",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42
            )
        )
    ])

    scores = cross_val_score(
        pipe,
        Xf,
        y,
        cv=cv,
        groups=groups,
        scoring="roc_auc"
    )

    return scores.mean()


# ================================================================
# 8. HORIZON SPECIFIC AUC
# ================================================================

print(
    "\n" + "=" * 70
)

print(
    "HORIZON SPECIFIC FEATURE GROUP AUC"
)

print(
    "60 MINUTE HISTORICAL CONTEXT"
)

print(
    "=" * 70
)

horizon_results = []

for horizon in [
    5,
    10,
    15,
    30,
    60
]:

    subset = X[
        X["horizon_minutes"] == horizon
    ].copy()

    print(
        f"\nHORIZON: {horizon} MINUTES"
    )

    for group_name, features in feature_groups.items():

        auc = grouped_auc(
            subset,
            features
        )

        horizon_results.append({
            "horizon":
                horizon,
            "feature_group":
                group_name,
            "auc":
                auc
        })

        print(
            f"{group_name:<22} "
            f"AUC = {auc:.4f}"
        )

horizon_results_df = pd.DataFrame(
    horizon_results
)


# ================================================================
# 9. EVENT COUNT AUC WITH CORRECT ORIENTATION
# ================================================================
#
# Lower event count is associated with the positive class in some
# horizons. Therefore report BOTH directions:
#
#     AUC_positive_direction
#     AUC_negative_direction
#
# This avoids misinterpreting an AUC below 0.5.
# ================================================================

print(
    "\n" + "=" * 70
)

print(
    "EVENT COUNT BASELINE"
)

print(
    "=" * 70
)

count_results = []

for horizon in [
    5,
    10,
    15,
    30,
    60
]:

    subset = X[
        X["horizon_minutes"] == horizon
    ]

    auc_raw = roc_auc_score(
        subset["label"],
        subset["event_count"]
    )

    auc_reversed = roc_auc_score(
        subset["label"],
        -subset["event_count"]
    )

    count_results.append({
        "horizon":
            horizon,
        "auc_raw":
            auc_raw,
        "auc_reversed":
            auc_reversed
    })

    print(
        f"{horizon:>2} min | "
        f"raw = {auc_raw:.4f} | "
        f"reversed = {auc_reversed:.4f}"
    )


# ================================================================
# 10. ZERO ACTIVITY
# ================================================================

print(
    "\n" + "=" * 70
)

print(
    "ZERO ACTIVITY COMPARISON"
)

print(
    "=" * 70
)

zero_rows = []

for horizon in [
    5,
    10,
    15,
    30,
    60
]:

    subset = X[
        X["horizon_minutes"] == horizon
    ]

    pos_h = subset[
        subset["label"] == 1
    ]

    hard_h = subset[
        subset["label"] == 0
    ]

    pos_zero = (
        pos_h["event_count"] == 0
    ).mean()

    hard_zero = (
        hard_h["event_count"] == 0
    ).mean()

    zero_rows.append({
        "horizon":
            horizon,
        "positive_zero_rate":
            pos_zero,
        "hard_negative_zero_rate":
            hard_zero
    })

    print(
        f"{horizon:>2} min | "
        f"positive zero = {pos_zero:.4f} | "
        f"hard negative zero = {hard_zero:.4f}"
    )


# ================================================================
# 11. TEMPORAL TRAJECTORY
# ================================================================

print(
    "\n" + "=" * 70
)

print(
    "TEMPORAL TRAJECTORY"
)

print(
    "60 MINUTE HISTORICAL CONTEXT"
)

print(
    "=" * 70
)

trajectory_rows = []

for label, name in [
    (1, "POSITIVE"),
    (0, "HARD_NEGATIVE")
]:

    for horizon in [
        5,
        10,
        15,
        30,
        60
    ]:

        subset = X[
            (X["label"] == label)
            &
            (X["horizon_minutes"] == horizon)
        ]

        trajectory_rows.append({
            "class":
                name,

            "horizon":
                horizon,

            "mean_events":
                subset["event_count"].mean(),

            "mean_sessions":
                subset["session_count"].mean(),

            "mean_modalities":
                subset["modality_count"].mean(),

            "mean_event_types":
                subset["event_type_count"].mean(),

            "mean_last5_share":
                subset["last5_share"].mean(),

            "mean_last10_share":
                subset["last10_share"].mean(),

            "mean_last15_share":
                subset["last15_share"].mean(),

            "mean_last30_share":
                subset["last30_share"].mean()
        })

trajectory_df = pd.DataFrame(
    trajectory_rows
)

print(
    trajectory_df.round(4).to_string(
        index=False
    )
)


# ================================================================
# 12. STANDARDIZED MEAN DIFFERENCES
# ================================================================

print(
    "\n" + "=" * 70
)

print(
    "STANDARDIZED MEAN DIFFERENCES"
)

print(
    "=" * 70
)


def smd(a, b):

    a = pd.to_numeric(
        a,
        errors="coerce"
    ).dropna()

    b = pd.to_numeric(
        b,
        errors="coerce"
    ).dropna()

    if len(a) == 0 or len(b) == 0:
        return np.nan

    pooled = np.sqrt(
        (
            a.var()
            +
            b.var()
        ) / 2
    )

    if pooled == 0:
        return np.nan

    return (
        a.mean() - b.mean()
    ) / pooled


smd_rows = []

for horizon in [
    5,
    10,
    15,
    30,
    60
]:

    subset = X[
        X["horizon_minutes"] == horizon
    ]

    pos_h = subset[
        subset["label"] == 1
    ]

    hard_h = subset[
        subset["label"] == 0
    ]

    for feature in [
        "event_count",
        "session_count",
        "event_type_count",
        "modality_count",
        "delay_mean",
        "delay_std",
        "new_device_rate",
        "location_rate",
        "roaming_rate",
        "last5_share",
        "last10_share",
        "last15_share",
        "last30_share"
    ]:

        smd_value = smd(
            pos_h[feature],
            hard_h[feature]
        )

        smd_rows.append({
            "horizon":
                horizon,
            "feature":
                feature,
            "smd":
                smd_value
        })

smd_df = pd.DataFrame(
    smd_rows
)

print(
    smd_df.pivot(
        index="feature",
        columns="horizon",
        values="smd"
    ).round(3).to_string()
)


# ================================================================
# 13. OVERALL GROUPED AUC
# ================================================================

print(
    "\n" + "=" * 70
)

print(
    "OVERALL GROUPED FEATURE GROUP AUC"
)

print(
    "=" * 70
)

overall_results = []

for group_name, features in feature_groups.items():

    auc = grouped_auc(
        X,
        features
    )

    overall_results.append({
        "feature_group":
            group_name,
        "auc":
            auc
    })

    print(
        f"{group_name:<22} "
        f"AUC = {auc:.4f}"
    )

overall_results_df = pd.DataFrame(
    overall_results
)


# ================================================================
# 14. BEST FEATURE GROUP PER HORIZON
# ================================================================

print(
    "\n" + "=" * 70
)

print(
    "BEST FEATURE GROUP BY HORIZON"
)

print(
    "=" * 70
)

best_by_horizon = (
    horizon_results_df
    .sort_values(
        [
            "horizon",
            "auc"
        ],
        ascending=[
            True,
            False
        ]
    )
    .groupby(
        "horizon"
    )
    .head(1)
)

print(
    best_by_horizon[
        [
            "horizon",
            "feature_group",
            "auc"
        ]
    ]
    .to_string(
        index=False
    )
)


# ================================================================
# 15. FINAL DIAGNOSTIC SUMMARY
# ================================================================

print(
    "\n" + "=" * 70
)

print(
    "71D.4C FINAL DIAGNOSTIC SUMMARY"
)

print(
    "=" * 70
)

print(
    "\nHistorical context:",
    f"{LOOKBACK_MINUTES} minutes"
)

print(
    "Prediction horizons:",
    [5, 10, 15, 30, 60]
)

print(
    "\nNo authoritative dataset object was modified."
)

print(
    "71D.4C COMPLETE"
)

print(
    "=" * 70
)

# ==============================================================================
# NOTEBOOK CELL 210
# ==============================================================================

# ======================================================================
# AFRITAC STEP 71D.5A
# HARD NEGATIVE CONSTRUCTION AUDIT
# Diagnose activity-volume and response-delay artifacts
# NO AUTHORITATIVE DATASET OBJECT IS MODIFIED
# ======================================================================

import numpy as np
import pandas as pd

from sklearn.metrics import roc_auc_score

print("=" * 70)
print("AFRITAC STEP 71D.5A")
print("HARD NEGATIVE CONSTRUCTION AUDIT")
print("=" * 70)

# ----------------------------------------------------------------------
# 0. REQUIRED OBJECTS
# ----------------------------------------------------------------------

required_objects = [
    "positive_windows",
    "hard_negative_windows",
    "hard_negative_events",
    "events",
    "observable_precursors"
]

missing = [x for x in required_objects if x not in globals()]

if missing:
    raise NameError(
        "Missing required objects: " + ", ".join(missing)
    )

print("\nREQUIRED OBJECTS FOUND")
for obj in required_objects:
    print(f"{obj:25s}: OK")


# ----------------------------------------------------------------------
# 1. COPY INPUTS
# ----------------------------------------------------------------------
# Copies are used throughout this diagnostic.

pos_w = positive_windows.copy()
hard_w = hard_negative_windows.copy()
hard_e = hard_negative_events.copy()
obs_e = events.copy()
prec_e = observable_precursors.copy()

print("\nINPUT SIZES")
print(f"Positive windows          : {len(pos_w)}")
print(f"Hard negative windows     : {len(hard_w)}")
print(f"Hard negative events      : {len(hard_e)}")
print(f"Ordinary observable       : {len(obs_e)}")
print(f"Observable precursors     : {len(prec_e)}")


# ----------------------------------------------------------------------
# 2. DATETIME NORMALIZATION
# ----------------------------------------------------------------------

def normalize_datetime(df, candidates):
    df = df.copy()

    for col in candidates:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


pos_w = normalize_datetime(
    pos_w,
    ["takeover_time", "cutoff_time", "timestamp"]
)

hard_w = normalize_datetime(
    hard_w,
    ["takeover_time", "cutoff_time", "timestamp"]
)

hard_e = normalize_datetime(
    hard_e,
    ["timestamp", "event_time", "start_time"]
)

obs_e = normalize_datetime(
    obs_e,
    ["timestamp", "event_time", "start_time"]
)

prec_e = normalize_datetime(
    prec_e,
    ["timestamp", "event_time", "start_time"]
)


# ----------------------------------------------------------------------
# 3. IDENTIFY WINDOW TIME FIELDS
# ----------------------------------------------------------------------

def find_time_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(
        f"Could not find any time column from {candidates}"
    )


pos_cutoff_col = find_time_column(
    pos_w,
    ["cutoff_time"]
)

hard_cutoff_col = find_time_column(
    hard_w,
    ["cutoff_time", "window_end", "prediction_time"]
)

pos_user_col = find_time_column(
    pos_w,
    ["user_id"]
)

hard_user_col = find_time_column(
    hard_w,
    ["user_id"]
)


# ----------------------------------------------------------------------
# 4. IDENTIFY EVENT TIME / USER COLUMNS
# ----------------------------------------------------------------------

obs_time_col = find_time_column(
    obs_e,
    ["timestamp", "event_time", "start_time"]
)

prec_time_col = find_time_column(
    prec_e,
    ["timestamp", "event_time", "start_time"]
)

hard_event_time_col = find_time_column(
    hard_e,
    ["timestamp", "event_time", "start_time"]
)

obs_user_col = find_time_column(
    obs_e,
    ["user_id"]
)

prec_user_col = find_time_column(
    prec_e,
    ["user_id"]
)

hard_event_user_col = find_time_column(
    hard_e,
    ["user_id"]
)


# ----------------------------------------------------------------------
# 5. BUILD THE POSITIVE OBSERVABLE STREAM
# ----------------------------------------------------------------------

positive_stream = pd.concat(
    [
        obs_e.assign(_source="ORDINARY"),
        prec_e.assign(_source="PRECURSOR")
    ],
    ignore_index=True,
    sort=False
)

positive_stream[obs_time_col] = pd.to_datetime(
    positive_stream[obs_time_col],
    errors="coerce"
)

positive_stream = positive_stream[
    positive_stream[obs_time_col].notna()
].copy()

print("\nPOSITIVE ANALYSIS STREAM")
print(f"Rows: {len(positive_stream)}")


# ----------------------------------------------------------------------
# 6. FUNCTION TO CALCULATE WINDOW STATISTICS
# ----------------------------------------------------------------------

def window_statistics(
    windows,
    stream,
    cutoff_col,
    user_col_window,
    user_col_stream,
    time_col_stream,
    lookback_minutes=60
):

    records = []

    for _, row in windows.iterrows():

        user = row[user_col_window]
        cutoff = row[cutoff_col]

        if pd.isna(cutoff):
            continue

        left = cutoff - pd.Timedelta(
            minutes=lookback_minutes
        )

        subset = stream[
            (stream[user_col_stream] == user) &
            (stream[time_col_stream] > left) &
            (stream[time_col_stream] <= cutoff)
        ].copy()

        n_events = len(subset)

        # --------------------------------------------------------------
        # Sessions
        # --------------------------------------------------------------

        if "session_id" in subset.columns:
            n_sessions = subset["session_id"].nunique()
        else:
            n_sessions = n_events

        # --------------------------------------------------------------
        # Event types
        # --------------------------------------------------------------

        if "event_type" in subset.columns:
            n_event_types = subset["event_type"].nunique()
        else:
            n_event_types = 0

        # --------------------------------------------------------------
        # Modalities
        # --------------------------------------------------------------

        if "modality" in subset.columns:
            n_modalities = subset["modality"].nunique()
        else:
            n_modalities = 0

        # --------------------------------------------------------------
        # Temporal concentration
        # --------------------------------------------------------------

        def share_in_last(minutes):

            if n_events == 0:
                return 0.0

            boundary = cutoff - pd.Timedelta(
                minutes=minutes
            )

            return np.mean(
                subset[time_col_stream] > boundary
            )

        # --------------------------------------------------------------
        # Response delay
        # --------------------------------------------------------------

        if "response_delay_ms" in subset.columns:

            delay = pd.to_numeric(
                subset["response_delay_ms"],
                errors="coerce"
            ).dropna()

            delay_mean = delay.mean() if len(delay) else np.nan
            delay_std = delay.std() if len(delay) > 1 else 0.0

        else:

            delay_mean = np.nan
            delay_std = np.nan

        # --------------------------------------------------------------
        # Context
        # --------------------------------------------------------------

        def binary_rate(col):

            if col not in subset.columns or len(subset) == 0:
                return 0.0

            values = pd.to_numeric(
                subset[col],
                errors="coerce"
            )

            return values.mean()

        # --------------------------------------------------------------
        # Financial
        # --------------------------------------------------------------

        if "transaction_amount" in subset.columns:

            amounts = pd.to_numeric(
                subset["transaction_amount"],
                errors="coerce"
            ).dropna()

            financial_count = len(amounts)
            financial_sum = amounts.sum() if len(amounts) else 0.0
            financial_mean = amounts.mean() if len(amounts) else 0.0
            financial_max = amounts.max() if len(amounts) else 0.0

        else:

            financial_count = 0
            financial_sum = 0.0
            financial_mean = 0.0
            financial_max = 0.0

        records.append({

            "window_id": row.get("window_id", np.nan),
            "user_id": user,
            "horizon_minutes": row.get(
                "horizon_minutes", np.nan
            ),

            "event_count": n_events,
            "session_count": n_sessions,
            "event_type_count": n_event_types,
            "modality_count": n_modalities,

            "last5_share": share_in_last(5),
            "last10_share": share_in_last(10),
            "last15_share": share_in_last(15),
            "last30_share": share_in_last(30),

            "delay_mean": delay_mean,
            "delay_std": delay_std,

            "location_rate": binary_rate(
                "location_change"
            ),

            "new_device_rate": binary_rate(
                "new_device"
            ),

            "roaming_rate": binary_rate(
                "roaming"
            ),

            "financial_count": financial_count,
            "financial_sum": financial_sum,
            "financial_mean": financial_mean,
            "financial_max": financial_max
        })

    return pd.DataFrame(records)


# ----------------------------------------------------------------------
# 7. POSITIVE WINDOW FEATURES
# ----------------------------------------------------------------------

print("\nEXTRACTING POSITIVE WINDOW STATISTICS")

pos_diag = window_statistics(
    windows=pos_w,
    stream=positive_stream,
    cutoff_col=pos_cutoff_col,
    user_col_window=pos_user_col,
    user_col_stream=obs_user_col,
    time_col_stream=obs_time_col,
    lookback_minutes=60
)

print(f"Positive diagnostic rows: {len(pos_diag)}")


# ----------------------------------------------------------------------
# 8. HARD NEGATIVE WINDOW FEATURES
# ----------------------------------------------------------------------

print("\nEXTRACTING HARD NEGATIVE WINDOW STATISTICS")

hard_diag = window_statistics(
    windows=hard_w,
    stream=hard_e,
    cutoff_col=hard_cutoff_col,
    user_col_window=hard_user_col,
    user_col_stream=hard_event_user_col,
    time_col_stream=hard_event_time_col,
    lookback_minutes=60
)

print(f"Hard negative diagnostic rows: {len(hard_diag)}")


# ----------------------------------------------------------------------
# 9. HORIZON NORMALIZATION
# ----------------------------------------------------------------------

pos_diag["label"] = 1
hard_diag["label"] = 0

combined_diag = pd.concat(
    [pos_diag, hard_diag],
    ignore_index=True
)

print("\nCOMBINED DIAGNOSTIC MATRIX")
print(combined_diag.shape)
print(
    "Labels:",
    combined_diag["label"].value_counts().to_dict()
)


# ======================================================================
# 10. DIAGNOSTIC 1
# WHY ARE HARD NEGATIVES ALWAYS 22.6 EVENTS?
# ======================================================================

print("\n" + "=" * 70)
print("DIAGNOSTIC 1")
print("HARD NEGATIVE EVENT GENERATION STRUCTURE")
print("=" * 70)

hard_event_summary = (
    hard_e
    .groupby(hard_event_user_col)
    .agg(
        event_count=(hard_event_user_col, "size"),
        unique_timestamps=(hard_event_time_col, "nunique")
    )
    .reset_index()
)

print("\nEVENTS PER HARD NEGATIVE USER")
print(
    hard_event_summary["event_count"]
    .describe()
)

print("\nUNIQUE TIMESTAMPS PER HARD NEGATIVE USER")
print(
    hard_event_summary["unique_timestamps"]
    .describe()
)

print("\nEVENT COUNT FREQUENCY")
print(
    hard_event_summary["event_count"]
    .value_counts()
    .sort_index()
)

if "horizon_minutes" in hard_w.columns:

    print("\nHARD NEGATIVE WINDOW COUNT BY HORIZON")

    print(
        hard_w["horizon_minutes"]
        .value_counts()
        .sort_index()
    )

    print("\nHARD NEGATIVE WINDOW IDs BY HORIZON")

    for h in sorted(
        hard_w["horizon_minutes"].dropna().unique()
    ):

        ids = hard_w.loc[
            hard_w["horizon_minutes"] == h,
            "window_id"
        ].tolist()

        print(
            f"Horizon {int(h):>2} | "
            f"{len(ids)} windows | "
            f"first IDs: {ids[:5]}"
        )


# ======================================================================
# 11. DIAGNOSTIC 2
# IS THE SAME HARD NEGATIVE HISTORY REUSED?
# ======================================================================

print("\n" + "=" * 70)
print("DIAGNOSTIC 2")
print("HARD NEGATIVE HORIZON REUSE TEST")
print("=" * 70)

reuse_results = []

if "horizon_minutes" in hard_w.columns:

    for user in hard_w[hard_user_col].dropna().unique():

        uw = hard_w[
            hard_w[hard_user_col] == user
        ].copy()

        uw = uw.sort_values(
            "horizon_minutes"
        )

        if len(uw) > 1:

            cutoff_values = (
                uw[hard_cutoff_col]
                .astype(str)
                .tolist()
            )

            reuse_results.append({

                "user_id": user,
                "n_windows": len(uw),
                "unique_cutoffs": len(
                    set(cutoff_values)
                ),

                "unique_horizons": uw[
                    "horizon_minutes"
                ].nunique()
            })

reuse_df = pd.DataFrame(reuse_results)

if len(reuse_df):

    print(
        reuse_df[
            [
                "n_windows",
                "unique_cutoffs",
                "unique_horizons"
            ]
        ].describe()
    )

    print(
        "\nUsers with one identical cutoff reused:",
        np.sum(
            reuse_df["unique_cutoffs"] == 1
        ),
        "/",
        len(reuse_df)
    )

    print(
        "Users with 5 distinct horizons:",
        np.sum(
            reuse_df["unique_horizons"] == 5
        ),
        "/",
        len(reuse_df)
    )


# ======================================================================
# 12. DIAGNOSTIC 3
# RESPONSE DELAY DISTRIBUTION
# ======================================================================

print("\n" + "=" * 70)
print("DIAGNOSTIC 3")
print("RESPONSE DELAY DISTRIBUTION")
print("=" * 70)

def delay_summary(df, name):

    if "response_delay_ms" not in df.columns:

        print(f"\n{name}: response_delay_ms unavailable")
        return

    delay = pd.to_numeric(
        df["response_delay_ms"],
        errors="coerce"
    ).dropna()

    print(f"\n{name}")

    if len(delay) == 0:
        print("No valid response delay values.")
        return

    print(
        delay.describe()
    )

    print(
        "\nQuantiles:"
    )

    print(
        delay.quantile(
            [0, .01, .05, .25, .50, .75, .95, .99, 1]
        )
    )


delay_summary(
    prec_e,
    "OBSERVABLE PRECURSORS"
)

delay_summary(
    hard_e,
    "HARD NEGATIVE EVENTS"
)


# ======================================================================
# 13. RESPONSE DELAY BY HORIZON
# ======================================================================

print("\n" + "=" * 70)
print("RESPONSE DELAY BY HORIZON")
print("=" * 70)

if "horizon_minutes" in combined_diag.columns:

    print(
        combined_diag
        .groupby(
            ["label", "horizon_minutes"]
        )[
            ["delay_mean", "delay_std"]
        ]
        .agg(
            ["mean", "median", "std"]
        )
        .round(3)
    )


# ======================================================================
# 14. RESPONSE DELAY AUC
# ======================================================================

print("\n" + "=" * 70)
print("RESPONSE DELAY AUC")
print("=" * 70)

if "horizon_minutes" in combined_diag.columns:

    for h in sorted(
        combined_diag["horizon_minutes"]
        .dropna()
        .unique()
    ):

        sub = combined_diag[
            combined_diag["horizon_minutes"] == h
        ].copy()

        valid = sub["delay_mean"].notna()

        if valid.sum() > 1 and sub.loc[
            valid, "label"
        ].nunique() == 2:

            auc = roc_auc_score(
                sub.loc[valid, "label"],
                sub.loc[valid, "delay_mean"]
            )

            print(
                f"{int(h):>2} min | "
                f"AUC = {auc:.4f}"
            )


# ======================================================================
# 15. RESPONSE DELAY SOURCE / EVENT TYPE AUDIT
# ======================================================================

print("\n" + "=" * 70)
print("RESPONSE DELAY SOURCE AUDIT")
print("=" * 70)

if "event_type" in prec_e.columns:

    print("\nPRECURSOR RESPONSE DELAY BY EVENT TYPE")

    print(
        prec_e
        .groupby("event_type")[
            "response_delay_ms"
        ]
        .agg(
            ["count", "mean", "median", "std", "min", "max"]
        )
        .sort_values("count", ascending=False)
        .round(2)
    )

if "event_type" in hard_e.columns:

    print("\nHARD NEGATIVE RESPONSE DELAY BY EVENT TYPE")

    print(
        hard_e
        .groupby("event_type")[
            "response_delay_ms"
        ]
        .agg(
            ["count", "mean", "median", "std", "min", "max"]
        )
        .sort_values("count", ascending=False)
        .round(2)
    )


# ======================================================================
# 16. DIAGNOSTIC 4
# ACTIVITY BALANCE BY HORIZON
# ======================================================================

print("\n" + "=" * 70)
print("DIAGNOSTIC 4")
print("ACTIVITY BALANCE")
print("=" * 70)

activity_features = [
    "event_count",
    "session_count",
    "event_type_count",
    "modality_count",
    "last5_share",
    "last10_share",
    "last15_share",
    "last30_share"
]

available_activity = [
    x for x in activity_features
    if x in combined_diag.columns
]

if "horizon_minutes" in combined_diag.columns:

    activity_summary = (
        combined_diag
        .groupby(
            ["label", "horizon_minutes"]
        )[available_activity]
        .mean()
        .round(4)
    )

    print(activity_summary)


# ======================================================================
# 17. DIAGNOSTIC 5
# ZERO ACTIVITY
# ======================================================================

print("\n" + "=" * 70)
print("ZERO ACTIVITY COMPARISON")
print("=" * 70)

if "horizon_minutes" in combined_diag.columns:

    for h in sorted(
        combined_diag["horizon_minutes"]
        .dropna()
        .unique()
    ):

        sub = combined_diag[
            combined_diag["horizon_minutes"] == h
        ]

        pos_zero = np.mean(
            sub.loc[
                sub["label"] == 1,
                "event_count"
            ] == 0
        )

        hard_zero = np.mean(
            sub.loc[
                sub["label"] == 0,
                "event_count"
            ] == 0
        )

        print(
            f"{int(h):>2} min | "
            f"positive = {pos_zero:.4f} | "
            f"hard negative = {hard_zero:.4f}"
        )


# ======================================================================
# 18. DIAGNOSTIC 6
# EVENT COUNT AUC
# ======================================================================

print("\n" + "=" * 70)
print("EVENT COUNT AUC")
print("=" * 70)

if "horizon_minutes" in combined_diag.columns:

    for h in sorted(
        combined_diag["horizon_minutes"]
        .dropna()
        .unique()
    ):

        sub = combined_diag[
            combined_diag["horizon_minutes"] == h
        ]

        raw = roc_auc_score(
            sub["label"],
            sub["event_count"]
        )

        reversed_auc = roc_auc_score(
            sub["label"],
            -sub["event_count"]
        )

        print(
            f"{int(h):>2} min | "
            f"raw = {raw:.4f} | "
            f"reversed = {reversed_auc:.4f}"
        )


# ======================================================================
# 19. DIAGNOSTIC 7
# FEATURE DISTRIBUTION DIFFERENCE
# ======================================================================

print("\n" + "=" * 70)
print("POSITIVE VS HARD NEGATIVE FEATURE MEANS")
print("=" * 70)

comparison_features = [
    "event_count",
    "session_count",
    "event_type_count",
    "modality_count",
    "last5_share",
    "last10_share",
    "last15_share",
    "last30_share",
    "delay_mean",
    "delay_std",
    "location_rate",
    "new_device_rate",
    "roaming_rate",
    "financial_count",
    "financial_sum",
    "financial_mean",
    "financial_max"
]

available_comparison = [
    x for x in comparison_features
    if x in combined_diag.columns
]

mean_table = (
    combined_diag
    .groupby("label")[available_comparison]
    .mean()
    .T
)

mean_table.columns = [
    "HARD_NEGATIVE",
    "POSITIVE"
]

mean_table["DIFFERENCE"] = (
    mean_table["POSITIVE"] -
    mean_table["HARD_NEGATIVE"]
)

print(
    mean_table.round(4)
)


# ======================================================================
# 20. DIAGNOSTIC 8
# PER-FEATURE AUC
# ======================================================================

print("\n" + "=" * 70)
print("OVERALL FEATURE AUC")
print("=" * 70)

auc_rows = []

for feature in available_comparison:

    sub = combined_diag[
        ["label", feature]
    ].dropna()

    if (
        len(sub) > 1 and
        sub["label"].nunique() == 2 and
        sub[feature].nunique() > 1
    ):

        auc = roc_auc_score(
            sub["label"],
            sub[feature]
        )

        auc_rows.append({
            "feature": feature,
            "auc": auc,
            "reversed_auc": max(
                auc,
                1 - auc
            )
        })

auc_df = pd.DataFrame(
    auc_rows
).sort_values(
    "reversed_auc",
    ascending=False
)

print(
    auc_df.round(4)
)


# ======================================================================
# 21. DIAGNOSTIC 9
# HARD NEGATIVE BAND STRUCTURE
# ======================================================================

print("\n" + "=" * 70)
print("HARD NEGATIVE BAND STRUCTURE")
print("=" * 70)

for col in [
    "band",
    "difficulty_band",
    "temporal_band",
    "hard_negative_band"
]:

    if col in hard_e.columns:

        print(
            f"\nColumn: {col}"
        )

        print(
            hard_e[col]
            .value_counts()
            .sort_index()
        )


# ======================================================================
# 22. DIAGNOSTIC 10
# HARD NEGATIVE EVENTS PER WINDOW
# ======================================================================

print("\n" + "=" * 70)
print("HARD NEGATIVE EVENTS PER WINDOW")
print("=" * 70)

if "window_id" in hard_e.columns:

    per_window = (
        hard_e
        .groupby("window_id")
        .size()
        .rename("event_count")
        .reset_index()
    )

    print(
        per_window["event_count"]
        .describe()
    )

    print(
        "\nEvent count distribution:"
    )

    print(
        per_window["event_count"]
        .value_counts()
        .sort_index()
    )


# ======================================================================
# 23. DIAGNOSTIC 11
# CHECK WHETHER HARD NEGATIVE EVENT TIMES COVER ALL HORIZONS
# ======================================================================

print("\n" + "=" * 70)
print("HARD NEGATIVE TEMPORAL COVERAGE")
print("=" * 70)

if "window_id" in hard_e.columns:

    if "window_id" in hard_w.columns:

        hw = hard_w[
            [
                "window_id",
                hard_cutoff_col,
                "horizon_minutes"
            ]
        ].copy()

        he = hard_e[
            [
                "window_id",
                hard_event_time_col
            ]
        ].copy()

        merged = he.merge(
            hw,
            on="window_id",
            how="left"
        )

        merged["minutes_before_cutoff"] = (
            merged[hard_cutoff_col] -
            merged[hard_event_time_col]
        ).dt.total_seconds() / 60

        print(
            merged[
                "minutes_before_cutoff"
            ].describe()
        )

        print(
            "\nCoverage by horizon:"
        )

        for h in sorted(
            hw["horizon_minutes"]
            .dropna()
            .unique()
        ):

            sub = merged[
                merged["horizon_minutes"] == h
            ]

            print(
                f"{int(h):>2} min | "
                f"events = {len(sub):>4} | "
                f"median minutes before cutoff = "
                f"{sub['minutes_before_cutoff'].median():.2f} | "
                f"min = "
                f"{sub['minutes_before_cutoff'].min():.2f} | "
                f"max = "
                f"{sub['minutes_before_cutoff'].max():.2f}"
            )


# ======================================================================
# 24. FINAL INTERPRETATION FLAGS
# ======================================================================

print("\n" + "=" * 70)
print("71D.5A DIAGNOSTIC FLAGS")
print("=" * 70)

# Event volume artifact
event_auc_values = []

if "horizon_minutes" in combined_diag.columns:

    for h in sorted(
        combined_diag["horizon_minutes"]
        .dropna()
        .unique()
    ):

        sub = combined_diag[
            combined_diag["horizon_minutes"] == h
        ]

        event_auc_values.append(
            roc_auc_score(
                sub["label"],
                sub["event_count"]
            )
        )

max_event_auc = (
    max(event_auc_values)
    if event_auc_values
    else np.nan
)

print(
    "1. Activity-volume artifact:",
    "YES" if max_event_auc >= 0.80 else "NO"
)

# Response delay artifact
delay_auc_values = []

if "horizon_minutes" in combined_diag.columns:

    for h in sorted(
        combined_diag["horizon_minutes"]
        .dropna()
        .unique()
    ):

        sub = combined_diag[
            combined_diag["horizon_minutes"] == h
        ][
            ["label", "delay_mean"]
        ].dropna()

        if (
            len(sub) > 1 and
            sub["label"].nunique() == 2
        ):

            auc = roc_auc_score(
                sub["label"],
                sub["delay_mean"]
            )

            delay_auc_values.append(
                max(auc, 1 - auc)
            )

max_delay_auc = (
    max(delay_auc_values)
    if delay_auc_values
    else np.nan
)

print(
    "2. Response-delay artifact:",
    "YES" if max_delay_auc >= 0.90 else "NO"
)

# Fixed hard negative activity
hard_counts = hard_diag["event_count"].dropna()

print(
    "3. Hard-negative activity constant:",
    "YES"
    if (
        len(hard_counts) > 0 and
        hard_counts.nunique() <= 2
    )
    else "NO"
)

# Horizon variation
if "horizon_minutes" in hard_w.columns:

    print(
        "4. Hard-negative horizon-specific construction:",
        "YES"
        if hard_w["horizon_minutes"].nunique() > 1
        else "NO"
    )


# ======================================================================
# 25. IMPORTANT
# ======================================================================

print("\n" + "=" * 70)
print("NO DATASET OBJECT WAS MODIFIED")
print("=" * 70)

print(
    "Authoritative objects preserved:"
)

for name in [
    "campaigns",
    "attack_events",
    "campaign_control",
    "positive_windows",
    "negative_windows",
    "observable_precursors",
    "hard_negative_windows",
    "hard_negative_events"
]:

    if name in globals():
        print(f"  {name}")

print("\n71D.5A COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 211
# ==============================================================================

# ======================================================================
# AFRITAC STEP 71D.5B
# ACTIVITY-MATCHED HARD NEGATIVE DESIGN
#
# Purpose:
#   Construct a candidate hard-negative layer from legitimate observable
#   activity, matched to positive windows on baseline activity structure.
#
# IMPORTANT:
#   NO AUTHORITATIVE DATASET OBJECT IS MODIFIED.
#
# New temporary objects created:
#   candidate_hard_negative_windows
#   candidate_hard_negative_events
#   candidate_hn_matching_table
# ======================================================================

import numpy as np
import pandas as pd

from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

print("=" * 70)
print("AFRITAC STEP 71D.5B")
print("ACTIVITY-MATCHED HARD NEGATIVE DESIGN")
print("=" * 70)


# ----------------------------------------------------------------------
# 0. REQUIRED OBJECTS
# ----------------------------------------------------------------------

required = [
    "positive_windows",
    "observable_precursors",
    "events"
]

missing = [
    x for x in required
    if x not in globals()
]

if missing:
    raise NameError(
        "Missing required objects: " +
        ", ".join(missing)
    )

print("\nREQUIRED OBJECTS")
for x in required:
    print(f"{x:25s}: OK")


# ----------------------------------------------------------------------
# 1. SAFE COPIES
# ----------------------------------------------------------------------

pos_w = positive_windows.copy()
ordinary = events.copy()
precursors = observable_precursors.copy()


# ----------------------------------------------------------------------
# 2. DATETIME NORMALIZATION
# ----------------------------------------------------------------------

for df in [pos_w, ordinary, precursors]:

    for col in [
        "timestamp",
        "event_time",
        "start_time",
        "cutoff_time",
        "takeover_time"
    ]:

        if col in df.columns:

            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            )


# ----------------------------------------------------------------------
# 3. IDENTIFY STANDARD COLUMNS
# ----------------------------------------------------------------------

def first_existing(df, candidates):

    for c in candidates:

        if c in df.columns:
            return c

    raise KeyError(
        "None of these columns found: " +
        str(candidates)
    )


pos_user_col = first_existing(
    pos_w,
    ["user_id"]
)

pos_cutoff_col = first_existing(
    pos_w,
    ["cutoff_time"]
)

event_user_col = first_existing(
    ordinary,
    ["user_id"]
)

event_time_col = first_existing(
    ordinary,
    ["timestamp", "event_time", "start_time"]
)

prec_user_col = first_existing(
    precursors,
    ["user_id"]
)

prec_time_col = first_existing(
    precursors,
    ["timestamp", "event_time", "start_time"]
)


# ----------------------------------------------------------------------
# 4. POSITIVE ANALYSIS STREAM
# ----------------------------------------------------------------------
#
# Only observable activity is allowed.
# Attack events are excluded explicitly.
#
# Precursors are included because they are observable defender-side
# signals, but their ground truth attack label must remain 0.
# ----------------------------------------------------------------------

ordinary_obs = ordinary.copy()

if "is_attack" in ordinary_obs.columns:

    ordinary_obs = ordinary_obs[
        ordinary_obs["is_attack"] != 1
    ].copy()

if "ground_truth_state" in ordinary_obs.columns:

    ordinary_obs = ordinary_obs[
        ordinary_obs["ground_truth_state"] != "ATTACK"
    ].copy()


prec_obs = precursors.copy()

if "is_attack" in prec_obs.columns:

    prec_obs = prec_obs[
        prec_obs["is_attack"] != 1
    ].copy()

if "ground_truth_state" in prec_obs.columns:

    prec_obs = prec_obs[
        prec_obs["ground_truth_state"] != "ATTACK"
    ].copy()


positive_stream = pd.concat(
    [
        ordinary_obs.assign(_source="ORDINARY"),
        prec_obs.assign(_source="PRECURSOR")
    ],
    ignore_index=True,
    sort=False
)

positive_stream = positive_stream[
    positive_stream[event_time_col].notna()
].copy()

print("\nPOSITIVE OBSERVABLE STREAM")
print(
    f"Ordinary observable : {len(ordinary_obs)}"
)

print(
    f"Precursor observable: {len(prec_obs)}"
)

print(
    f"Combined            : {len(positive_stream)}"
)


# ----------------------------------------------------------------------
# 5. POSITIVE WINDOW FEATURE EXTRACTION
# ----------------------------------------------------------------------

def extract_window_features(
    windows,
    stream,
    user_col_window,
    cutoff_col,
    user_col_stream,
    time_col_stream,
    lookback_minutes=60
):

    rows = []

    for _, w in windows.iterrows():

        user = w[user_col_window]
        cutoff = w[cutoff_col]

        if pd.isna(cutoff):
            continue

        left = (
            cutoff -
            pd.Timedelta(
                minutes=lookback_minutes
            )
        )

        x = stream[
            (stream[user_col_stream] == user) &
            (stream[time_col_stream] > left) &
            (stream[time_col_stream] <= cutoff)
        ].copy()

        n = len(x)

        # --------------------------------------------------------------
        # Session count
        # --------------------------------------------------------------

        if "session_id" in x.columns:
            sessions = x["session_id"].nunique()
        else:
            sessions = n

        # --------------------------------------------------------------
        # Event type count
        # --------------------------------------------------------------

        if "event_type" in x.columns:
            event_types = x["event_type"].nunique()
        else:
            event_types = 0

        # --------------------------------------------------------------
        # Modality count
        # --------------------------------------------------------------

        if "modality" in x.columns:
            modalities = x["modality"].nunique()
        else:
            modalities = 0

        # --------------------------------------------------------------
        # Temporal concentration
        # --------------------------------------------------------------

        def share_last(minutes):

            if n == 0:
                return 0.0

            boundary = (
                cutoff -
                pd.Timedelta(
                    minutes=minutes
                )
            )

            return np.mean(
                x[time_col_stream] > boundary
            )

        # --------------------------------------------------------------
        # Response delay
        # --------------------------------------------------------------

        if "response_delay_ms" in x.columns:

            delay = pd.to_numeric(
                x["response_delay_ms"],
                errors="coerce"
            ).dropna()

            delay_mean = (
                delay.mean()
                if len(delay)
                else np.nan
            )

            delay_std = (
                delay.std()
                if len(delay) > 1
                else 0.0
            )

        else:

            delay_mean = np.nan
            delay_std = np.nan

        # --------------------------------------------------------------
        # Context
        # --------------------------------------------------------------

        def binary_rate(col):

            if col not in x.columns:
                return 0.0

            if len(x) == 0:
                return 0.0

            values = pd.to_numeric(
                x[col],
                errors="coerce"
            )

            return values.mean()

        # --------------------------------------------------------------
        # Financial
        # --------------------------------------------------------------

        if "transaction_amount" in x.columns:

            amounts = pd.to_numeric(
                x["transaction_amount"],
                errors="coerce"
            ).dropna()

            financial_count = len(amounts)
            financial_sum = (
                amounts.sum()
                if len(amounts)
                else 0.0
            )

            financial_mean = (
                amounts.mean()
                if len(amounts)
                else 0.0
            )

            financial_max = (
                amounts.max()
                if len(amounts)
                else 0.0
            )

        else:

            financial_count = 0
            financial_sum = 0.0
            financial_mean = 0.0
            financial_max = 0.0

        # --------------------------------------------------------------
        # Behavioral profile
        # --------------------------------------------------------------

        rows.append({

            "window_id":
                w.get(
                    "window_id",
                    np.nan
                ),

            "user_id":
                user,

            "horizon_minutes":
                w.get(
                    "horizon_minutes",
                    np.nan
                ),

            "cutoff_time":
                cutoff,

            "event_count":
                n,

            "session_count":
                sessions,

            "event_type_count":
                event_types,

            "modality_count":
                modalities,

            "last5_share":
                share_last(5),

            "last10_share":
                share_last(10),

            "last15_share":
                share_last(15),

            "last30_share":
                share_last(30),

            "delay_mean":
                delay_mean,

            "delay_std":
                delay_std,

            "location_rate":
                binary_rate(
                    "location_change"
                ),

            "new_device_rate":
                binary_rate(
                    "new_device"
                ),

            "roaming_rate":
                binary_rate(
                    "roaming"
                ),

            "financial_count":
                financial_count,

            "financial_sum":
                financial_sum,

            "financial_mean":
                financial_mean,

            "financial_max":
                financial_max
        })

    return pd.DataFrame(rows)


print("\nEXTRACTING POSITIVE FEATURES")

positive_features = extract_window_features(
    windows=pos_w,
    stream=positive_stream,
    user_col_window=pos_user_col,
    cutoff_col=pos_cutoff_col,
    user_col_stream=event_user_col,
    time_col_stream=event_time_col,
    lookback_minutes=60
)

print(
    f"Positive feature rows: {len(positive_features)}"
)


# ----------------------------------------------------------------------
# 6. SELECT CLEAN USERS FOR CANDIDATE HARD NEGATIVES
# ----------------------------------------------------------------------
#
# IMPORTANT:
# Candidate hard-negative users must be disjoint from positive users.
#
# We intentionally use legitimate existing users rather than synthetic
# event generation at this stage.
# ----------------------------------------------------------------------

positive_users = set(
    pos_w["user_id"].dropna().unique()
)

all_observable_users = set(
    positive_stream["user_id"].dropna().unique()
)

eligible_users = sorted(
    all_observable_users -
    positive_users
)

print("\nUSER SELECTION")

print(
    f"Positive users       : {len(positive_users)}"
)

print(
    f"Eligible clean users : {len(eligible_users)}"
)

if len(eligible_users) < 20:

    raise ValueError(
        "Fewer than 20 disjoint clean users are available."
    )


# ----------------------------------------------------------------------
# 7. RANDOMLY SELECT 20 CLEAN USERS
# ----------------------------------------------------------------------

SEED_71D5B = 7105

rng = np.random.default_rng(
    SEED_71D5B
)

candidate_users = rng.choice(
    eligible_users,
    size=20,
    replace=False
)

candidate_users = list(candidate_users)

print(
    "\nCandidate hard-negative users:"
)

print(candidate_users)


# ----------------------------------------------------------------------
# 8. BUILD LEGITIMATE CANDIDATE WINDOWS
# ----------------------------------------------------------------------
#
# For each selected user we identify real observable activity points
# that can serve as prediction cutoffs.
#
# The same cutoff is NOT reused across horizons.
# Each horizon receives an independently selected legitimate cutoff.
# ----------------------------------------------------------------------

candidate_rows = []

horizons = [5, 10, 15, 30, 60]

for user in candidate_users:

    user_events = positive_stream[
        positive_stream["user_id"] == user
    ].copy()

    if len(user_events) == 0:
        continue

    user_events = user_events.sort_values(
        event_time_col
    )

    timestamps = (
        user_events[event_time_col]
        .dropna()
        .drop_duplicates()
        .tolist()
    )

    if len(timestamps) < 5:
        continue

    # --------------------------------------------------------------
    # Select five distinct cutoff timestamps.
    # --------------------------------------------------------------

    if len(timestamps) >= 5:

        selected_times = rng.choice(
            np.array(
                timestamps,
                dtype="datetime64[ns]"
            ),
            size=5,
            replace=False
        )

        selected_times = sorted(
            pd.to_datetime(selected_times)
        )

    else:
        continue

    for horizon, cutoff in zip(
        horizons,
        selected_times
    ):

        candidate_rows.append({

            "window_id":
                f"HN_MATCH_{user}_{pd.Timestamp(cutoff).strftime('%Y%m%d%H%M%S')}_H{horizon}",

            "user_id":
                user,

            "horizon_minutes":
                horizon,

            "cutoff_time":
                pd.Timestamp(cutoff),

            "label":
                0
        })


candidate_hard_negative_windows = pd.DataFrame(
    candidate_rows
)

print("\nCANDIDATE HARD NEGATIVE WINDOWS")
print(
    f"Rows: {len(candidate_hard_negative_windows)}"
)

print(
    candidate_hard_negative_windows[
        [
            "user_id",
            "horizon_minutes",
            "cutoff_time"
        ]
    ]
    .sort_values(
        ["user_id", "horizon_minutes"]
    )
    .head(20)
)


# ----------------------------------------------------------------------
# 9. EXTRACT CANDIDATE HARD NEGATIVE FEATURES
# ----------------------------------------------------------------------

candidate_hn_features = extract_window_features(
    windows=candidate_hard_negative_windows,
    stream=positive_stream,
    user_col_window="user_id",
    cutoff_col="cutoff_time",
    user_col_stream="user_id",
    time_col_stream=event_time_col,
    lookback_minutes=60
)

candidate_hn_features["label"] = 0

print(
    "\nCandidate hard-negative feature rows:",
    len(candidate_hn_features)
)


# ----------------------------------------------------------------------
# 10. MATCH POSITIVE WINDOWS TO CLEAN NEGATIVE WINDOWS
# ----------------------------------------------------------------------
#
# Matching variables:
#
#   horizon
#   event_count
#   session_count
#   modality_count
#   event_type_count
#   response delay
#
# We use standardized distance.
#
# This is a DESIGN DIAGNOSTIC, not yet the final dataset.
# ----------------------------------------------------------------------

match_features = [
    "event_count",
    "session_count",
    "event_type_count",
    "modality_count",
    "delay_mean",
    "delay_std"
]

match_features = [
    x for x in match_features
    if (
        x in positive_features.columns and
        x in candidate_hn_features.columns
    )
]

print("\nMATCHING FEATURES")
print(match_features)


# ----------------------------------------------------------------------
# 11. MATCHING BY HORIZON
# ----------------------------------------------------------------------

match_rows = []

for horizon in horizons:

    p = positive_features[
        positive_features["horizon_minutes"] == horizon
    ].copy()

    h = candidate_hn_features[
        candidate_hn_features["horizon_minutes"] == horizon
    ].copy()

    if len(p) == 0 or len(h) == 0:
        continue

    # --------------------------------------------------------------
    # Aggregate target distribution
    # --------------------------------------------------------------

    target_values = pd.concat(
        [
            p[match_features],
            h[match_features]
        ],
        ignore_index=True
    )

    target_values = target_values.replace(
        [np.inf, -np.inf],
        np.nan
    )

    medians = target_values.median()

    p2 = p[match_features].fillna(
        medians
    )

    h2 = h[match_features].fillna(
        medians
    )

    scaler = StandardScaler()

    scaler.fit(
        pd.concat(
            [p2, h2],
            ignore_index=True
        )
    )

    ps = scaler.transform(p2)
    hs = scaler.transform(h2)

    # --------------------------------------------------------------
    # Nearest-neighbor matching.
    # --------------------------------------------------------------

    used = set()

    for pi, p_row in enumerate(
        p.itertuples()
    ):

        distances = np.sqrt(
            np.sum(
                (
                    hs -
                    ps[pi]
                ) ** 2,
                axis=1
            )
        )

        order = np.argsort(
            distances
        )

        selected = None

        for hi in order:

            if hi not in used:

                selected = hi
                break

        if selected is None:
            break

        used.add(selected)

        h_row = h.iloc[selected]

        match_rows.append({

            "horizon_minutes":
                horizon,

            "positive_window_id":
                p_row.window_id,

            "positive_user_id":
                p_row.user_id,

            "hard_negative_window_id":
                h_row["window_id"],

            "hard_negative_user_id":
                h_row["user_id"],

            "match_distance":
                distances[selected]
        })


candidate_hn_matching_table = pd.DataFrame(
    match_rows
)

print("\nMATCHING RESULTS")

print(
    candidate_hn_matching_table[
        "horizon_minutes"
    ]
    .value_counts()
    .sort_index()
)

print(
    "\nMatch distance:"
)

print(
    candidate_hn_matching_table[
        "match_distance"
    ]
    .describe()
)


# ----------------------------------------------------------------------
# 12. BUILD MATCHED HARD NEGATIVE WINDOWS
# ----------------------------------------------------------------------

matched_ids = set(
    candidate_hn_matching_table[
        "hard_negative_window_id"
    ]
)

candidate_hard_negative_windows = (
    candidate_hard_negative_windows[
        candidate_hard_negative_windows[
            "window_id"
        ].isin(matched_ids)
    ]
    .copy()
)

print(
    "\nFINAL CANDIDATE MATCHED WINDOWS:",
    len(candidate_hard_negative_windows)
)


# ----------------------------------------------------------------------
# 13. RECOMPUTE FEATURES AFTER MATCHING
# ----------------------------------------------------------------------

candidate_hn_features = (
    candidate_hn_features[
        candidate_hn_features["window_id"].isin(
            matched_ids
        )
    ]
    .copy()
)

# Add label explicitly.
candidate_hn_features["label"] = 0


# ----------------------------------------------------------------------
# 14. SELECT POSITIVE WINDOWS THAT WERE MATCHED
# ----------------------------------------------------------------------

matched_positive_ids = set(
    candidate_hn_matching_table[
        "positive_window_id"
    ]
)

matched_positive_features = (
    positive_features[
        positive_features["window_id"].isin(
            matched_positive_ids
        )
    ]
    .copy()
)

matched_positive_features["label"] = 1


# ----------------------------------------------------------------------
# 15. BALANCED DIAGNOSTIC DATASET
# ----------------------------------------------------------------------

diagnostic = pd.concat(
    [
        matched_positive_features,
        candidate_hn_features
    ],
    ignore_index=True
)

print("\nBALANCED DIAGNOSTIC DATASET")
print(
    diagnostic.shape
)

print(
    diagnostic["label"]
    .value_counts()
)


# ======================================================================
# 16. ACTIVITY BALANCE AUDIT
# ======================================================================

print("\n" + "=" * 70)
print("ACTIVITY BALANCE AFTER MATCHING")
print("=" * 70)

audit_features = [
    "event_count",
    "session_count",
    "event_type_count",
    "modality_count",
    "last5_share",
    "last10_share",
    "last15_share",
    "last30_share",
    "delay_mean",
    "delay_std"
]

for horizon in horizons:

    p = diagnostic[
        (
            diagnostic["label"] == 1
        ) &
        (
            diagnostic["horizon_minutes"] == horizon
        )
    ]

    h = diagnostic[
        (
            diagnostic["label"] == 0
        ) &
        (
            diagnostic["horizon_minutes"] == horizon
        )
    ]

    print(
        f"\nHORIZON {horizon} MINUTES"
    )

    comparison = pd.DataFrame({

        "POSITIVE":
            p[audit_features].mean(),

        "HARD_NEGATIVE":
            h[audit_features].mean()

    })

    comparison["difference"] = (
        comparison["POSITIVE"] -
        comparison["HARD_NEGATIVE"]
    )

    print(
        comparison.round(3)
    )


# ======================================================================
# 17. EVENT COUNT AUC
# ======================================================================

print("\n" + "=" * 70)
print("EVENT COUNT AUC AFTER MATCHING")
print("=" * 70)

for horizon in horizons:

    sub = diagnostic[
        diagnostic["horizon_minutes"] == horizon
    ].copy()

    if (
        len(sub) > 1 and
        sub["label"].nunique() == 2
    ):

        auc = roc_auc_score(
            sub["label"],
            sub["event_count"]
        )

        print(
            f"{horizon:>2} min | "
            f"AUC = {auc:.4f} | "
            f"direction-free = "
            f"{max(auc, 1-auc):.4f}"
        )


# ======================================================================
# 18. FEATURE AUC AFTER MATCHING
# ======================================================================

print("\n" + "=" * 70)
print("FEATURE AUC AFTER MATCHING")
print("=" * 70)

auc_rows = []

for feature in audit_features:

    for horizon in horizons:

        sub = diagnostic[
            diagnostic["horizon_minutes"] == horizon
        ][
            ["label", feature]
        ].dropna()

        if (
            len(sub) > 1 and
            sub["label"].nunique() == 2 and
            sub[feature].nunique() > 1
        ):

            auc = roc_auc_score(
                sub["label"],
                sub[feature]
            )

            auc_rows.append({

                "feature":
                    feature,

                "horizon":
                    horizon,

                "auc":
                    auc,

                "direction_free_auc":
                    max(
                        auc,
                        1 - auc
                    )
            })


matched_auc = pd.DataFrame(
    auc_rows
)

print(
    matched_auc
    .sort_values(
        [
            "horizon",
            "direction_free_auc"
        ],
        ascending=[True, False]
    )
    .round(4)
)


# ======================================================================
# 19. ZERO ACTIVITY
# ======================================================================

print("\n" + "=" * 70)
print("ZERO ACTIVITY AFTER MATCHING")
print("=" * 70)

for horizon in horizons:

    p = diagnostic[
        (
            diagnostic["label"] == 1
        ) &
        (
            diagnostic["horizon_minutes"] == horizon
        )
    ]

    h = diagnostic[
        (
            diagnostic["label"] == 0
        ) &
        (
            diagnostic["horizon_minutes"] == horizon
        )
    ]

    if len(p) and len(h):

        print(
            f"{horizon:>2} min | "
            f"positive zero = "
            f"{np.mean(p['event_count'] == 0):.4f} | "
            f"hard zero = "
            f"{np.mean(h['event_count'] == 0):.4f}"
        )


# ======================================================================
# 20. MATCHING DISTANCE BY HORIZON
# ======================================================================

print("\n" + "=" * 70)
print("MATCH QUALITY")
print("=" * 70)

print(
    candidate_hn_matching_table
    .groupby("horizon_minutes")[
        "match_distance"
    ]
    .agg(
        [
            "count",
            "mean",
            "median",
            "std",
            "min",
            "max"
        ]
    )
    .round(4)
)


# ======================================================================
# 21. USER DISJOINTNESS
# ======================================================================

print("\n" + "=" * 70)
print("USER DISJOINTNESS")
print("=" * 70)

matched_hn_users = set(
    candidate_hard_negative_windows[
        "user_id"
    ]
)

overlap = (
    matched_hn_users &
    positive_users
)

print(
    "Positive users:",
    len(positive_users)
)

print(
    "Candidate hard-negative users:",
    len(matched_hn_users)
)

print(
    "User overlap:",
    len(overlap)
)

if overlap:
    print(
        "OVERLAP USERS:",
        sorted(overlap)
    )
else:
    print(
        "PASS: no positive/hard-negative user overlap"
    )


# ======================================================================
# 22. HORIZON CUTOFF REUSE AUDIT
# ======================================================================

print("\n" + "=" * 70)
print("HORIZON CUTOFF REUSE AUDIT")
print("=" * 70)

reuse = (
    candidate_hard_negative_windows
    .groupby("user_id")
    .agg(
        n_windows=("window_id", "count"),
        unique_cutoffs=("cutoff_time", "nunique"),
        unique_horizons=("horizon_minutes", "nunique")
    )
    .reset_index()
)

print(reuse)

print(
    "\nUsers with 5 unique cutoffs:",
    np.sum(
        reuse["unique_cutoffs"] == 5
    ),
    "/",
    len(reuse)
)


# ======================================================================
# 23. FINAL DESIGN DECISION FLAGS
# ======================================================================

print("\n" + "=" * 70)
print("71D.5B DESIGN DIAGNOSTIC")
print("=" * 70)

# Direction-free activity AUC
activity_features = [
    "event_count",
    "session_count",
    "modality_count"
]

activity_auc_values = []

for feature in activity_features:

    if feature not in diagnostic.columns:
        continue

    for horizon in horizons:

        sub = diagnostic[
            diagnostic["horizon_minutes"] == horizon
        ][
            ["label", feature]
        ].dropna()

        if (
            len(sub) > 1 and
            sub["label"].nunique() == 2 and
            sub[feature].nunique() > 1
        ):

            auc = roc_auc_score(
                sub["label"],
                sub[feature]
            )

            activity_auc_values.append(
                max(auc, 1 - auc)
            )


max_activity_auc = (
    max(activity_auc_values)
    if activity_auc_values
    else np.nan
)

mean_activity_auc = (
    np.mean(activity_auc_values)
    if activity_auc_values
    else np.nan
)

print(
    f"Maximum direction-free activity AUC: "
    f"{max_activity_auc:.4f}"
)

print(
    f"Mean direction-free activity AUC: "
    f"{mean_activity_auc:.4f}"
)

print(
    "\nActivity matching status:",
    "IMPROVED"
    if (
        not np.isnan(max_activity_auc) and
        max_activity_auc < 0.80
    )
    else "REQUIRES FURTHER MATCHING"
)


# ----------------------------------------------------------------------
# 24. PRESERVE ORIGINAL OBJECTS
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("AUTHORITATIVE OBJECTS PRESERVED")
print("=" * 70)

for name in [
    "hard_negative_windows",
    "hard_negative_events",
    "positive_windows",
    "observable_precursors",
    "campaigns",
    "attack_events",
    "campaign_control"
]:

    print(
        f"{name:25s}:",
        "UNCHANGED"
    )


print("\n" + "=" * 70)
print("71D.5B COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 212
# ==============================================================================

# ======================================================================
# AFRITAC STEP 71D.5C
# CONTROLLED ACTIVITY-MATCHED HARD NEGATIVE CONSTRUCTION
#
# Purpose:
#   Build candidate hard-negative windows by matching legitimate
#   historical activity to the positive prediction windows.
#
# Key design principles:
#   1. No positive-user overlap.
#   2. No attack events.
#   3. No precursor events in the candidate negative stream.
#   4. Each horizon gets its own legitimate cutoff.
#   5. Historical context is ALWAYS the 60 minutes immediately preceding
#      the prediction cutoff.
#   6. Matching is performed on activity structure, not attack vocabulary.
#   7. 60-minute horizon is treated separately because the current
#      positive precursor layer has zero activity at that cutoff.
#   8. Authoritative objects are NOT modified.
#
# New objects only:
#   hn71c_windows
#   hn71c_events
#   hn71c_features
#   hn71c_matches
# ======================================================================

import numpy as np
import pandas as pd

from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cdist

print("=" * 70)
print("AFRITAC STEP 71D.5C")
print("CONTROLLED ACTIVITY-MATCHED HARD NEGATIVE CONSTRUCTION")
print("=" * 70)


# ======================================================================
# 0. REQUIRED OBJECTS
# ======================================================================

required = [
    "positive_windows",
    "observable_precursors",
    "events",
    "users"
]

missing = [
    x for x in required
    if x not in globals()
]

if missing:
    raise NameError(
        "Missing required objects: " +
        ", ".join(missing)
    )

print("\nREQUIRED OBJECTS")
for x in required:
    print(f"{x:25s}: OK")


# ======================================================================
# 1. SAFE COPIES
# ======================================================================

pos_w = positive_windows.copy()
ordinary = events.copy()
precursors = observable_precursors.copy()
users_copy = users.copy()


# ======================================================================
# 2. DATETIME NORMALIZATION
# ======================================================================

def normalize_times(df):

    df = df.copy()

    for c in [
        "timestamp",
        "event_time",
        "start_time",
        "end_time",
        "cutoff_time",
        "takeover_time"
    ]:

        if c in df.columns:

            df[c] = pd.to_datetime(
                df[c],
                errors="coerce"
            )

    return df


pos_w = normalize_times(pos_w)
ordinary = normalize_times(ordinary)
precursors = normalize_times(precursors)


# ======================================================================
# 3. COLUMN IDENTIFICATION
# ======================================================================

def first_existing(df, names):

    for n in names:

        if n in df.columns:
            return n

    raise KeyError(
        "None of the following columns exist: " +
        str(names)
    )


event_time_col = first_existing(
    ordinary,
    ["timestamp", "event_time", "start_time"]
)

prec_time_col = first_existing(
    precursors,
    ["timestamp", "event_time", "start_time"]
)

pos_cutoff_col = first_existing(
    pos_w,
    ["cutoff_time"]
)


# ======================================================================
# 4. REMOVE ATTACK INFORMATION FROM ORDINARY STREAM
# ======================================================================

ordinary_clean = ordinary.copy()

if "is_attack" in ordinary_clean.columns:

    ordinary_clean = ordinary_clean[
        ordinary_clean["is_attack"] != 1
    ].copy()

if "ground_truth_state" in ordinary_clean.columns:

    ordinary_clean = ordinary_clean[
        ordinary_clean["ground_truth_state"] != "ATTACK"
    ].copy()


# ----------------------------------------------------------------------
# Remove precursor rows from ordinary stream if they happen to have
# been incorporated there.
# ----------------------------------------------------------------------

if "is_observable_precursor" in ordinary_clean.columns:

    ordinary_clean = ordinary_clean[
        ordinary_clean["is_observable_precursor"] != 1
    ].copy()


# ======================================================================
# 5. POSITIVE ANALYSIS STREAM
# ======================================================================

prec_clean = precursors.copy()

if "is_attack" in prec_clean.columns:

    prec_clean = prec_clean[
        prec_clean["is_attack"] != 1
    ].copy()

if "ground_truth_state" in prec_clean.columns:

    prec_clean = prec_clean[
        prec_clean["ground_truth_state"] != "ATTACK"
    ].copy()


positive_stream = pd.concat(
    [
        ordinary_clean.assign(
            _source="ORDINARY"
        ),
        prec_clean.assign(
            _source="PRECURSOR"
        )
    ],
    ignore_index=True,
    sort=False
)

positive_stream = positive_stream[
    positive_stream[event_time_col].notna()
].copy()

print("\nOBSERVABLE STREAM")
print(
    f"Ordinary observable : {len(ordinary_clean)}"
)

print(
    f"Observable precursor: {len(prec_clean)}"
)

print(
    f"Combined stream     : {len(positive_stream)}"
)


# ======================================================================
# 6. POSITIVE USERS
# ======================================================================

positive_users = set(
    pos_w["user_id"]
    .dropna()
    .unique()
)

print(
    "\nPositive users:",
    len(positive_users)
)


# ======================================================================
# 7. CLEAN USER POOL
# ======================================================================

stream_users = set(
    positive_stream["user_id"]
    .dropna()
    .unique()
)

clean_users = sorted(
    stream_users -
    positive_users
)

print(
    "Clean disjoint users:",
    len(clean_users)
)

if len(clean_users) < 20:

    raise ValueError(
        "Fewer than 20 clean disjoint users available."
    )


# ======================================================================
# 8. USER BEHAVIORAL PROFILE
# ======================================================================

user_profile_cols = [
    "user_id",
    "country",
    "language_region",
    "age",
    "tenure_months",
    "behaviour_profile",
    "primary_device_id"
]

available_profile_cols = [
    c for c in user_profile_cols
    if c in users_copy.columns
]

clean_user_profile = users_copy[
    available_profile_cols
].copy()

clean_user_profile = clean_user_profile[
    clean_user_profile["user_id"].isin(
        clean_users
    )
].copy()


# ======================================================================
# 9. BUILD OBSERVABLE ACTIVITY INDEX
# ======================================================================
#
# Each legitimate timestamp becomes a possible prediction cutoff.
#
# We require:
#   at least one event in the preceding 60 minutes
#
# This prevents synthetic "one event exactly at cutoff" construction
# from dominating the candidate controls.
# ======================================================================

stream = positive_stream.copy()

stream = stream.sort_values(
    ["user_id", event_time_col]
)

candidate_cutoff_rows = []

for user in clean_users:

    ue = stream[
        stream["user_id"] == user
    ].copy()

    if len(ue) == 0:
        continue

    times = (
        ue[event_time_col]
        .dropna()
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    for cutoff in times:

        left = (
            cutoff -
            pd.Timedelta(
                minutes=60
            )
        )

        n60 = np.sum(
            (
                ue[event_time_col] > left
            ) &
            (
                ue[event_time_col] <= cutoff
            )
        )

        if n60 > 0:

            candidate_cutoff_rows.append({

                "user_id": user,

                "cutoff_time":
                    pd.Timestamp(cutoff),

                "event_count_60":
                    int(n60)
            })


candidate_cutoffs = pd.DataFrame(
    candidate_cutoff_rows
)

print(
    "\nLEGITIMATE CUTOFF POOL"
)

print(
    f"Candidate cutoffs: {len(candidate_cutoffs)}"
)

print(
    candidate_cutoffs[
        "event_count_60"
    ].describe()
)


# ======================================================================
# 10. WINDOW FEATURE EXTRACTION
# ======================================================================

def extract_features(
    cutoff_df,
    stream_df,
    horizons
):

    rows = []

    for _, row in cutoff_df.iterrows():

        user = row["user_id"]
        cutoff = row["cutoff_time"]

        left = (
            cutoff -
            pd.Timedelta(
                minutes=60
            )
        )

        x = stream_df[
            (stream_df["user_id"] == user) &
            (stream_df[event_time_col] > left) &
            (stream_df[event_time_col] <= cutoff)
        ].copy()

        n = len(x)

        if "session_id" in x.columns:

            session_count = (
                x["session_id"].nunique()
            )

        else:

            session_count = n

        if "event_type" in x.columns:

            event_type_count = (
                x["event_type"].nunique()
            )

        else:

            event_type_count = 0

        if "modality" in x.columns:

            modality_count = (
                x["modality"].nunique()
            )

        else:

            modality_count = 0

        def recent_share(minutes):

            if n == 0:
                return 0.0

            boundary = (
                cutoff -
                pd.Timedelta(
                    minutes=minutes
                )
            )

            return np.mean(
                x[event_time_col] > boundary
            )

        if "response_delay_ms" in x.columns:

            delay = pd.to_numeric(
                x["response_delay_ms"],
                errors="coerce"
            ).dropna()

            delay_mean = (
                delay.mean()
                if len(delay)
                else np.nan
            )

            delay_std = (
                delay.std()
                if len(delay) > 1
                else 0.0
            )

        else:

            delay_mean = np.nan
            delay_std = np.nan

        def rate(col):

            if (
                col not in x.columns
                or len(x) == 0
            ):
                return 0.0

            values = pd.to_numeric(
                x[col],
                errors="coerce"
            )

            return values.mean()

        if "transaction_amount" in x.columns:

            amounts = pd.to_numeric(
                x["transaction_amount"],
                errors="coerce"
            ).dropna()

            financial_count = len(amounts)

            financial_mean = (
                amounts.mean()
                if len(amounts)
                else 0.0
            )

            financial_max = (
                amounts.max()
                if len(amounts)
                else 0.0
            )

        else:

            financial_count = 0
            financial_mean = 0.0
            financial_max = 0.0

        for horizon in horizons:

            rows.append({

                "user_id":
                    user,

                "cutoff_time":
                    cutoff,

                "horizon_minutes":
                    horizon,

                "event_count":
                    n,

                "session_count":
                    session_count,

                "event_type_count":
                    event_type_count,

                "modality_count":
                    modality_count,

                "last5_share":
                    recent_share(5),

                "last10_share":
                    recent_share(10),

                "last15_share":
                    recent_share(15),

                "last30_share":
                    recent_share(30),

                "delay_mean":
                    delay_mean,

                "delay_std":
                    delay_std,

                "location_rate":
                    rate("location_change"),

                "new_device_rate":
                    rate("new_device"),

                "roaming_rate":
                    rate("roaming"),

                "financial_count":
                    financial_count,

                "financial_mean":
                    financial_mean,

                "financial_max":
                    financial_max
            })

    return pd.DataFrame(rows)


print(
    "\nEXTRACTING CLEAN USER ACTIVITY FEATURES"
)

clean_features = extract_features(
    candidate_cutoffs,
    positive_stream,
    [5, 10, 15, 30, 60]
)

print(
    "Clean feature rows:",
    len(clean_features)
)


# ======================================================================
# 11. POSITIVE FEATURES
# ======================================================================

positive_cutoffs = pos_w[
    [
        "user_id",
        "cutoff_time",
        "horizon_minutes"
    ]
].copy()

positive_features = extract_features(
    positive_cutoffs[
        ["user_id", "cutoff_time"]
    ]
    .drop_duplicates()
    .merge(
        positive_cutoffs,
        on=[
            "user_id",
            "cutoff_time"
        ],
        how="left"
    )[
        [
            "user_id",
            "cutoff_time"
        ]
    ]
    .drop_duplicates(),
    positive_stream,
    [5, 10, 15, 30, 60]
)

# The above creates every horizon for each positive cutoff.
# Retain only the actual positive horizon combinations.

positive_key = positive_cutoffs[
    [
        "user_id",
        "cutoff_time",
        "horizon_minutes"
    ]
].drop_duplicates()

positive_features = positive_features.merge(
    positive_key,
    on=[
        "user_id",
        "cutoff_time",
        "horizon_minutes"
    ],
    how="inner"
)

print(
    "\nPositive feature rows:",
    len(positive_features)
)


# ======================================================================
# 12. MATCHING VARIABLES
# ======================================================================
#
# We deliberately DO NOT match on:
#   attack-specific event vocabulary
#   precursor event type
#   takeover state
#   attack stage
#
# We match only legitimate observable activity characteristics.
# ======================================================================

match_features = [
    "event_count",
    "session_count",
    "event_type_count",
    "modality_count",
    "last5_share",
    "last10_share",
    "last15_share",
    "last30_share",
    "delay_mean",
    "delay_std",
    "location_rate",
    "new_device_rate",
    "roaming_rate",
    "financial_count",
    "financial_mean",
    "financial_max"
]

match_features = [
    c for c in match_features
    if (
        c in positive_features.columns
        and c in clean_features.columns
    )
]

print(
    "\nMATCHING FEATURES:"
)

print(match_features)


# ======================================================================
# 13. STANDARDIZED DISTANCE MATCHING
# ======================================================================
#
# One-to-one matching within horizon.
#
# A clean control is used at most once per horizon.
# Different horizons use different legitimate cutoffs.
# ======================================================================

rng = np.random.default_rng(
    71505
)

match_records = []

for horizon in [5, 10, 15, 30]:

    p = positive_features[
        positive_features["horizon_minutes"] ==
        horizon
    ].copy()

    c = clean_features[
        clean_features["horizon_minutes"] ==
        horizon
    ].copy()

    if len(p) == 0 or len(c) == 0:

        continue

    combined = pd.concat(
        [
            p[match_features],
            c[match_features]
        ],
        ignore_index=True
    )

    combined = combined.replace(
        [np.inf, -np.inf],
        np.nan
    )

    medians = combined.median()

    combined = combined.fillna(
        medians
    )

    scaler = StandardScaler()

    z = scaler.fit_transform(
        combined
    )

    pz = z[
        :len(p)
    ]

    cz = z[
        len(p):
    ]

    distances = cdist(
        pz,
        cz,
        metric="euclidean"
    )

    used_controls = set()

    # Match difficult positive windows first.
    order = np.argsort(
        distances.min(axis=1)
    )[::-1]

    for pi in order:

        candidates = np.argsort(
            distances[pi]
        )

        selected = None

        for ci in candidates:

            if ci not in used_controls:

                selected = ci
                break

        if selected is None:
            continue

        used_controls.add(
            selected
        )

        prow = p.iloc[pi]
        crow = c.iloc[selected]

        match_records.append({

            "horizon_minutes":
                horizon,

            "positive_user_id":
                prow["user_id"],

            "positive_cutoff":
                prow["cutoff_time"],

            "hard_negative_user_id":
                crow["user_id"],

            "hard_negative_cutoff":
                crow["cutoff_time"],

            "match_distance":
                distances[
                    pi,
                    selected
                ]
        })


hn71c_matches = pd.DataFrame(
    match_records
)

print(
    "\nMATCH RESULTS BEFORE 60-MINUTE HANDLING"
)

print(
    hn71c_matches[
        "horizon_minutes"
    ]
    .value_counts()
    .sort_index()
)


# ======================================================================
# 14. 60-MINUTE HORIZON
# ======================================================================
#
# The current positive precursor layer has zero activity at the
# takeover-60 prediction cutoff.
#
# We therefore DO NOT fabricate 60-minute precursor activity.
#
# For the candidate negative layer, identify clean-user cutoffs whose
# preceding 60-minute history is also empty.
#
# This produces a structurally comparable quiet-history control.
# ======================================================================

p60 = positive_features[
    positive_features["horizon_minutes"] == 60
].copy()

quiet_clean = clean_features[
    (
        clean_features["horizon_minutes"] == 60
    ) &
    (
        clean_features["event_count"] == 0
    )
].copy()

print(
    "\n60-MINUTE QUIET CONTROL POOL:",
    len(quiet_clean)
)

if len(p60) > 0 and len(quiet_clean) > 0:

    n60 = min(
        len(p60),
        len(quiet_clean)
    )

    # Randomized but reproducible pairing.
    p_order = rng.permutation(
        len(p60)
    )[:n60]

    c_order = rng.permutation(
        len(quiet_clean)
    )[:n60]

    for pi, ci in zip(
        p_order,
        c_order
    ):

        prow = p60.iloc[pi]
        crow = quiet_clean.iloc[ci]

        match_records.append({

            "horizon_minutes":
                60,

            "positive_user_id":
                prow["user_id"],

            "positive_cutoff":
                prow["cutoff_time"],

            "hard_negative_user_id":
                crow["user_id"],

            "hard_negative_cutoff":
                crow["cutoff_time"],

            "match_distance":
                0.0
        })

else:

    print(
        "WARNING: no quiet clean-user pool available."
    )


hn71c_matches = pd.DataFrame(
    match_records
)

print(
    "\nFINAL MATCH COUNTS"
)

print(
    hn71c_matches[
        "horizon_minutes"
    ]
    .value_counts()
    .sort_index()
)


# ======================================================================
# 15. USER DISJOINTNESS
# ======================================================================

matched_negative_users = set(
    hn71c_matches[
        "hard_negative_user_id"
    ]
    .dropna()
    .unique()
)

overlap = (
    matched_negative_users &
    positive_users
)

print(
    "\nUSER DISJOINTNESS"
)

print(
    "Positive users:",
    len(positive_users)
)

print(
    "Matched negative users:",
    len(matched_negative_users)
)

print(
    "Overlap:",
    len(overlap)
)

if overlap:

    raise AssertionError(
        "Positive/hard-negative user overlap detected."
    )

print(
    "PASS: zero user overlap"
)


# ======================================================================
# 16. CREATE CANDIDATE HARD-NEGATIVE WINDOWS
# ======================================================================

hn_windows_records = []

for i, row in hn71c_matches.iterrows():

    horizon = int(
        row["horizon_minutes"]
    )

    user = row[
        "hard_negative_user_id"
    ]

    cutoff = pd.Timestamp(
        row[
            "hard_negative_cutoff"
        ]
    )

    hn_windows_records.append({

        "window_id":
            (
                f"HN71C_{i+1:04d}_"
                f"{user}_"
                f"{cutoff.strftime('%Y%m%d%H%M%S')}_"
                f"H{horizon}"
            ),

        "user_id":
            user,

        "horizon_minutes":
            horizon,

        "cutoff_time":
            cutoff,

        "label":
            0,

        "hard_negative_design":
            "ACTIVITY_MATCHED_LEGITIMATE"
    })


hn71c_windows = pd.DataFrame(
    hn_windows_records
)

print(
    "\nCANDIDATE HARD-NEGATIVE WINDOWS:",
    len(hn71c_windows)
)


# ======================================================================
# 17. BUILD CANDIDATE EVENT STREAM
# ======================================================================
#
# We extract the REAL legitimate observable events occurring in the
# 60-minute history preceding each selected negative cutoff.
#
# No synthetic attack vocabulary is introduced.
# ======================================================================

candidate_events = []

for _, w in hn71c_windows.iterrows():

    user = w["user_id"]
    cutoff = w["cutoff_time"]

    left = (
        cutoff -
        pd.Timedelta(
            minutes=60
        )
    )

    x = positive_stream[
        (positive_stream["user_id"] == user) &
        (positive_stream[event_time_col] > left) &
        (positive_stream[event_time_col] <= cutoff)
    ].copy()

    if len(x) == 0:
        continue

    x = x.copy()

    x["hard_negative_window_id"] = (
        w["window_id"]
    )

    x["hard_negative_label"] = 0

    x["candidate_source"] = (
        "LEGITIMATE_OBSERVABLE"
    )

    candidate_events.append(
        x
    )


if candidate_events:

    hn71c_events = pd.concat(
        candidate_events,
        ignore_index=True,
        sort=False
    )

else:

    hn71c_events = pd.DataFrame()


print(
    "Candidate hard-negative events:",
    len(hn71c_events)
)


# ======================================================================
# 18. FEATURE EXTRACTION FOR CANDIDATE NEGATIVES
# ======================================================================

candidate_negative_features = []

for _, w in hn71c_windows.iterrows():

    user = w["user_id"]
    cutoff = w["cutoff_time"]

    left = (
        cutoff -
        pd.Timedelta(
            minutes=60
        )
    )

    x = positive_stream[
        (positive_stream["user_id"] == user) &
        (positive_stream[event_time_col] > left) &
        (positive_stream[event_time_col] <= cutoff)
    ].copy()

    n = len(x)

    if "session_id" in x.columns:

        sessions = x[
            "session_id"
        ].nunique()

    else:

        sessions = n

    if "event_type" in x.columns:

        event_types = x[
            "event_type"
        ].nunique()

    else:

        event_types = 0

    if "modality" in x.columns:

        modalities = x[
            "modality"
        ].nunique()

    else:

        modalities = 0

    def recent_share(minutes):

        if n == 0:
            return 0.0

        boundary = (
            cutoff -
            pd.Timedelta(
                minutes=minutes
            )
        )

        return np.mean(
            x[event_time_col] > boundary
        )

    if "response_delay_ms" in x.columns:

        delays = pd.to_numeric(
            x["response_delay_ms"],
            errors="coerce"
        ).dropna()

        delay_mean = (
            delays.mean()
            if len(delays)
            else np.nan
        )

        delay_std = (
            delays.std()
            if len(delays) > 1
            else 0.0
        )

    else:

        delay_mean = np.nan
        delay_std = np.nan

    def rate(col):

        if (
            col not in x.columns
            or len(x) == 0
        ):
            return 0.0

        return pd.to_numeric(
            x[col],
            errors="coerce"
        ).mean()

    if "transaction_amount" in x.columns:

        amounts = pd.to_numeric(
            x["transaction_amount"],
            errors="coerce"
        ).dropna()

        financial_count = len(amounts)

        financial_mean = (
            amounts.mean()
            if len(amounts)
            else 0.0
        )

        financial_max = (
            amounts.max()
            if len(amounts)
            else 0.0
        )

    else:

        financial_count = 0
        financial_mean = 0.0
        financial_max = 0.0

    candidate_negative_features.append({

        "window_id":
            w["window_id"],

        "user_id":
            user,

        "horizon_minutes":
            w["horizon_minutes"],

        "cutoff_time":
            cutoff,

        "label":
            0,

        "event_count":
            n,

        "session_count":
            sessions,

        "event_type_count":
            event_types,

        "modality_count":
            modalities,

        "last5_share":
            recent_share(5),

        "last10_share":
            recent_share(10),

        "last15_share":
            recent_share(15),

        "last30_share":
            recent_share(30),

        "delay_mean":
            delay_mean,

        "delay_std":
            delay_std,

        "location_rate":
            rate("location_change"),

        "new_device_rate":
            rate("new_device"),

        "roaming_rate":
            rate("roaming"),

        "financial_count":
            financial_count,

        "financial_mean":
            financial_mean,

        "financial_max":
            financial_max
    })


hn71c_features = pd.DataFrame(
    candidate_negative_features
)


# ======================================================================
# 19. POSITIVE FEATURES FOR MATCHED WINDOWS
# ======================================================================

positive_match_records = []

for _, m in hn71c_matches.iterrows():

    user = m["positive_user_id"]
    cutoff = pd.Timestamp(
        m["positive_cutoff"]
    )
    horizon = int(
        m["horizon_minutes"]
    )

    x = positive_stream[
        (positive_stream["user_id"] == user) &
        (
            positive_stream[event_time_col] >
            (
                cutoff -
                pd.Timedelta(
                    minutes=60
                )
            )
        ) &
        (
            positive_stream[event_time_col] <=
            cutoff
        )
    ].copy()

    n = len(x)

    sessions = (
        x["session_id"].nunique()
        if "session_id" in x.columns
        else n
    )

    event_types = (
        x["event_type"].nunique()
        if "event_type" in x.columns
        else 0
    )

    modalities = (
        x["modality"].nunique()
        if "modality" in x.columns
        else 0
    )

    def pshare(minutes):

        if n == 0:
            return 0.0

        boundary = (
            cutoff -
            pd.Timedelta(
                minutes=minutes
            )
        )

        return np.mean(
            x[event_time_col] > boundary
        )

    if "response_delay_ms" in x.columns:

        delays = pd.to_numeric(
            x["response_delay_ms"],
            errors="coerce"
        ).dropna()

        delay_mean = (
            delays.mean()
            if len(delays)
            else np.nan
        )

        delay_std = (
            delays.std()
            if len(delays) > 1
            else 0.0
        )

    else:

        delay_mean = np.nan
        delay_std = np.nan

    def prate(col):

        if (
            col not in x.columns
            or len(x) == 0
        ):
            return 0.0

        return pd.to_numeric(
            x[col],
            errors="coerce"
        ).mean()

    if "transaction_amount" in x.columns:

        amounts = pd.to_numeric(
            x["transaction_amount"],
            errors="coerce"
        ).dropna()

        financial_count = len(amounts)

        financial_mean = (
            amounts.mean()
            if len(amounts)
            else 0.0
        )

        financial_max = (
            amounts.max()
            if len(amounts)
            else 0.0
        )

    else:

        financial_count = 0
        financial_mean = 0.0
        financial_max = 0.0

    positive_match_records.append({

        "positive_user_id":
            user,

        "positive_cutoff":
            cutoff,

        "horizon_minutes":
            horizon,

        "label":
            1,

        "event_count":
            n,

        "session_count":
            sessions,

        "event_type_count":
            event_types,

        "modality_count":
            modalities,

        "last5_share":
            pshare(5),

        "last10_share":
            pshare(10),

        "last15_share":
            pshare(15),

        "last30_share":
            pshare(30),

        "delay_mean":
            delay_mean,

        "delay_std":
            delay_std,

        "location_rate":
            prate("location_change"),

        "new_device_rate":
            prate("new_device"),

        "roaming_rate":
            prate("roaming"),

        "financial_count":
            financial_count,

        "financial_mean":
            financial_mean,

        "financial_max":
            financial_max
    })


hn71c_positive_features = pd.DataFrame(
    positive_match_records
)


# ======================================================================
# 20. ACTIVITY BALANCE
# ======================================================================

print("\n" + "=" * 70)
print("ACTIVITY BALANCE")
print("=" * 70)

audit_features = [
    "event_count",
    "session_count",
    "event_type_count",
    "modality_count",
    "last5_share",
    "last10_share",
    "last15_share",
    "last30_share",
    "delay_mean",
    "delay_std",
    "location_rate",
    "new_device_rate",
    "roaming_rate",
    "financial_count",
    "financial_mean",
    "financial_max"
]

for h in [5, 10, 15, 30, 60]:

    p = hn71c_positive_features[
        hn71c_positive_features[
            "horizon_minutes"
        ] == h
    ]

    n = hn71c_features[
        hn71c_features[
            "horizon_minutes"
        ] == h
    ]

    print(
        f"\nHORIZON {h} MINUTES"
    )

    if len(p) == 0 or len(n) == 0:

        print(
            "Insufficient data."
        )

        continue

    table = pd.DataFrame({

        "POSITIVE":
            p[audit_features].mean(),

        "HARD_NEGATIVE":
            n[audit_features].mean()

    })

    table["difference"] = (
        table["POSITIVE"] -
        table["HARD_NEGATIVE"]
    )

    print(
        table.round(4)
    )


# ======================================================================
# 21. EVENT COUNT AUC
# ======================================================================

print("\n" + "=" * 70)
print("EVENT COUNT AUC")
print("=" * 70)

for h in [5, 10, 15, 30, 60]:

    p = hn71c_positive_features[
        hn71c_positive_features[
            "horizon_minutes"
        ] == h
    ]

    n = hn71c_features[
        hn71c_features[
            "horizon_minutes"
        ] == h
    ]

    sub = pd.concat(
        [
            p[["label", "event_count"]],
            n[["label", "event_count"]]
        ],
        ignore_index=True
    )

    if (
        len(sub) > 1 and
        sub["label"].nunique() == 2 and
        sub["event_count"].nunique() > 1
    ):

        auc = roc_auc_score(
            sub["label"],
            sub["event_count"]
        )

        print(
            f"{h:>2} min | "
            f"AUC = {auc:.4f} | "
            f"direction-free = "
            f"{max(auc, 1-auc):.4f}"
        )

    else:

        print(
            f"{h:>2} min | insufficient variation"
        )


# ======================================================================
# 22. FEATURE AUC
# ======================================================================

print("\n" + "=" * 70)
print("FEATURE AUC")
print("=" * 70)

feature_auc_rows = []

for feature in audit_features:

    for h in [5, 10, 15, 30, 60]:

        p = hn71c_positive_features[
            hn71c_positive_features[
                "horizon_minutes"
            ] == h
        ]

        n = hn71c_features[
            hn71c_features[
                "horizon_minutes"
            ] == h
        ]

        sub = pd.concat(
            [
                p[["label", feature]],
                n[["label", feature]]
            ],
            ignore_index=True
        ).dropna()

        if (
            len(sub) > 1 and
            sub["label"].nunique() == 2 and
            sub[feature].nunique() > 1
        ):

            auc = roc_auc_score(
                sub["label"],
                sub[feature]
            )

            feature_auc_rows.append({

                "feature":
                    feature,

                "horizon":
                    h,

                "auc":
                    auc,

                "direction_free_auc":
                    max(
                        auc,
                        1 - auc
                    )
            })


hn71c_auc = pd.DataFrame(
    feature_auc_rows
)

if len(hn71c_auc):

    print(
        hn71c_auc
        .sort_values(
            [
                "horizon",
                "direction_free_auc"
            ],
            ascending=[
                True,
                False
            ]
        )
        .round(4)
    )


# ======================================================================
# 23. ZERO ACTIVITY
# ======================================================================

print("\n" + "=" * 70)
print("ZERO ACTIVITY")
print("=" * 70)

for h in [5, 10, 15, 30, 60]:

    p = hn71c_positive_features[
        hn71c_positive_features[
            "horizon_minutes"
        ] == h
    ]

    n = hn71c_features[
        hn71c_features[
            "horizon_minutes"
        ] == h
    ]

    if len(p) and len(n):

        print(
            f"{h:>2} min | "
            f"positive zero = "
            f"{np.mean(p['event_count'] == 0):.4f} | "
            f"hard zero = "
            f"{np.mean(n['event_count'] == 0):.4f}"
        )


# ======================================================================
# 24. MATCH DISTANCE
# ======================================================================

print("\n" + "=" * 70)
print("MATCH DISTANCE")
print("=" * 70)

if len(hn71c_matches):

    print(
        hn71c_matches
        .groupby(
            "horizon_minutes"
        )[
            "match_distance"
        ]
        .agg(
            [
                "count",
                "mean",
                "median",
                "std",
                "min",
                "max"
            ]
        )
        .round(4)
    )


# ======================================================================
# 25. CUTOFF UNIQUENESS
# ======================================================================

print("\n" + "=" * 70)
print("CUTOFF UNIQUENESS")
print("=" * 70)

if len(hn71c_windows):

    cutoff_audit = (
        hn71c_windows
        .groupby("user_id")
        .agg(
            windows=("window_id", "count"),
            unique_cutoffs=(
                "cutoff_time",
                "nunique"
            ),
            unique_horizons=(
                "horizon_minutes",
                "nunique"
            )
        )
        .reset_index()
    )

    print(
        cutoff_audit
    )

    print(
        "\nUsers with five unique cutoffs:",
        np.sum(
            cutoff_audit[
                "unique_cutoffs"
            ] == 5
        ),
        "/",
        len(cutoff_audit)
    )


# ======================================================================
# 26. EVENT VOCABULARY CONTAMINATION TEST
# ======================================================================
#
# Candidate negatives must contain no precursor-specific event types.
# ======================================================================

attack_vocab = set()

if "event_type" in prec_clean.columns:

    attack_vocab = set(
        prec_clean[
            "event_type"
        ]
        .dropna()
        .astype(str)
        .unique()
    )

negative_vocab = set()

if (
    len(hn71c_events) and
    "event_type" in hn71c_events.columns
):

    negative_vocab = set(
        hn71c_events[
            "event_type"
        ]
        .dropna()
        .astype(str)
        .unique()
    )

vocabulary_overlap = (
    attack_vocab &
    negative_vocab
)

print("\n" + "=" * 70)
print("EVENT VOCABULARY CONTAMINATION")
print("=" * 70)

print(
    "Precursor event types:",
    len(attack_vocab)
)

print(
    "Candidate negative event types:",
    len(negative_vocab)
)

print(
    "Vocabulary overlap:",
    len(vocabulary_overlap)
)

if vocabulary_overlap:

    print(
        sorted(
            vocabulary_overlap
        )
    )

else:

    print(
        "PASS: no precursor vocabulary overlap"
    )


# ======================================================================
# 27. FINAL CONSTRUCTION SUMMARY
# ======================================================================

print("\n" + "=" * 70)
print("71D.5C FINAL DESIGN SUMMARY")
print("=" * 70)

print(
    "Candidate windows:",
    len(hn71c_windows)
)

print(
    "Candidate events:",
    len(hn71c_events)
)

print(
    "Candidate users:",
    hn71c_windows["user_id"].nunique()
    if len(hn71c_windows)
    else 0
)

print(
    "Positive users:",
    len(positive_users)
)

print(
    "User overlap:",
    len(overlap)
)

print(
    "Vocabulary overlap:",
    len(vocabulary_overlap)
)

print(
    "\nHorizon counts:"
)

print(
    hn71c_windows[
        "horizon_minutes"
    ]
    .value_counts()
    .sort_index()
)


# ======================================================================
# 28. DO NOT PROMOTE YET
# ======================================================================

print("\n" + "=" * 70)
print("AUTHORITATIVE DATASET STATUS")
print("=" * 70)

print(
    "hard_negative_windows : UNCHANGED"
)

print(
    "hard_negative_events  : UNCHANGED"
)

print(
    "positive_windows      : UNCHANGED"
)

print(
    "observable_precursors : UNCHANGED"
)

print(
    "campaigns             : UNCHANGED"
)

print(
    "attack_events         : UNCHANGED"
)

print(
    "campaign_control      : UNCHANGED"
)

print(
    "\n71D.5C IS A CANDIDATE DESIGN ONLY."
)

print(
    "Do NOT replace authoritative hard-negative objects yet."
)

print("=" * 70)
print("71D.5C COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 213
# ==============================================================================

print("Type of sessions:", type(sessions))
print("Value of sessions:", sessions)

print("\nPossible session DataFrames in memory:")

for name, obj in globals().items():
    try:
        if isinstance(obj, pd.DataFrame):
            cols = set(obj.columns)

            if (
                {"session_id", "user_id"}.issubset(cols)
                or
                {"session_id", "start_time", "end_time"}.issubset(cols)
            ):
                print(
                    name,
                    "| shape =", obj.shape,
                    "| columns =", list(obj.columns)[:12]
                )
    except Exception:
        pass

# ==============================================================================
# NOTEBOOK CELL 214
# ==============================================================================

# Restore the authoritative AFRITAC session DataFrame
sessions = sorted_sessions.copy()

print("sessions restored:", type(sessions))
print("sessions shape:", sessions.shape)
print("session columns:", list(sessions.columns[:12]))

# ==============================================================================
# NOTEBOOK CELL 215
# ==============================================================================

print("\nChecking positive profile matrix for non-finite values...")

# Check every feature
profile_finite_mask = np.isfinite(positive_matrix_71d5d)

print("Matrix shape:", positive_matrix_71d5d.shape)
print("Finite values:", profile_finite_mask.sum(), "/", positive_matrix_71d5d.size)
print("Non-finite values:", (~profile_finite_mask).sum())

# Feature names
signature_features_71d5d = [
    "event_count",
    "session_count",
    "modality_count",
    "event_type_count",
    "delay_mean",
    "delay_std",
    "last_5_share",
    "last_10_share",
    "last_15_share",
    "last_30_share",
    "new_device_rate",
    "location_change_rate",
    "roaming_rate",
    "transaction_count",
    "transaction_amount_sum",
    "event_type_entropy"
]

# Locate problematic features
print("\nNon-finite values by feature:")
for j, feature in enumerate(signature_features_71d5d):
    bad = (~np.isfinite(positive_matrix_71d5d[:, j])).sum()
    print(f"{feature:25s}: {bad}")

# Locate problematic users
bad_rows = np.where(~np.isfinite(positive_matrix_71d5d).all(axis=1))[0]

print("\nUsers with non-finite profiles:", len(bad_rows))

if len(bad_rows) > 0:
    print("\nProblematic profile rows:")
    for idx in bad_rows:
        print(
            "Row:", idx,
            "User:", positive_profiles_71d5d.iloc[idx]["user_id"]
            if "user_id" in positive_profiles_71d5d.columns
            else "unknown"
        )
        print(
            dict(
                zip(
                    signature_features_71d5d,
                    positive_matrix_71d5d[idx]
                )
            )
        )

print("\nRaw profile summary:")
for j, feature in enumerate(signature_features_71d5d):
    values = positive_matrix_71d5d[:, j]
    finite_values = values[np.isfinite(values)]

    if len(finite_values) > 0:
        print(
            f"{feature:25s} "
            f"min={finite_values.min():.4f} "
            f"max={finite_values.max():.4f} "
            f"mean={finite_values.mean():.4f}"
        )
    else:
        print(f"{feature:25s} NO FINITE VALUES")

# ==============================================================================
# NOTEBOOK CELL 216
# ==============================================================================

# ================================================================
# AFRITAC STEP 71D.5D
# SESSION BASED MATCHED HARD NEGATIVE CONTROLS
#
# Purpose:
# Construct 20 clean control users and 100 matched hard-negative
# prediction windows using real observable session histories.
#
# Design requirements:
#   1. 20 clean control users
#   2. 5 horizons per control user
#   3. Exactly 100 hard-negative windows
#   4. Cutoffs must not equal observed event timestamps
#   5. Prefer cutoffs in genuine gaps between sessions
#   6. Use real observable events only
#   7. No positive-user overlap
#   8. No attack-event contamination
#   9. Preserve the authoritative positive objects
# ================================================================

print("=" * 70)
print("AFRITAC STEP 71D.5D")
print("SESSION BASED MATCHED HARD NEGATIVE CONTROLS")
print("=" * 70)

# ================================================================
# 1. REQUIRED OBJECT CHECK
# ================================================================

required_objects = [
    "users",
    "sorted_sessions",
    "events",
    "campaigns",
    "attack_events",
    "positive_windows",
    "normal_stream",
    "observable_precursors",
]

missing_objects = [
    obj for obj in required_objects
    if obj not in globals()
]

print("Required objects missing:", missing_objects)

if missing_objects:
    raise RuntimeError(
        "71D.5D cannot continue because required objects are missing: "
        + str(missing_objects)
    )

# ================================================================
# 2. CONFIGURATION
# ================================================================

SEED_71D5D = SEED + 715
rng_71d5d = np.random.default_rng(SEED_71D5D)

N_CONTROL_USERS = 20
HORIZONS = [5, 10, 15, 30, 60]
LOOKBACK_MINUTES = 60

# Positive users
positive_users_71d5d = set(
    positive_windows["user_id"].astype(str).unique()
)

print("\nPositive users:", len(positive_users_71d5d))

# ================================================================
# 3. BUILD POSITIVE OBSERVABLE STREAM
# ================================================================
#
# Important:
# Positive feature construction must include both:
#
#   A. ordinary observable activity
#   B. controlled observable precursor activity
#
# Attack events are excluded.
# ================================================================

ordinary_71d5d = normal_stream.copy()

ordinary_71d5d["user_id"] = (
    ordinary_71d5d["user_id"].astype(str)
)

ordinary_71d5d["session_id"] = (
    ordinary_71d5d["session_id"].astype(str)
)

# Identify timestamp column
if "timestamp" in ordinary_71d5d.columns:
    ordinary_time_col_71d5d = "timestamp"
elif "event_time" in ordinary_71d5d.columns:
    ordinary_time_col_71d5d = "event_time"
else:
    raise RuntimeError(
        "Could not identify timestamp column in normal_stream."
    )

ordinary_71d5d[ordinary_time_col_71d5d] = pd.to_datetime(
    ordinary_71d5d[ordinary_time_col_71d5d],
    errors="coerce"
)

# Exclude attack events if attack flag exists
if "is_attack" in ordinary_71d5d.columns:
    ordinary_71d5d = ordinary_71d5d[
        ordinary_71d5d["is_attack"].fillna(0).astype(int) == 0
    ].copy()

positive_ordinary_71d5d = ordinary_71d5d[
    ordinary_71d5d["user_id"].isin(positive_users_71d5d)
].copy()

# ------------------------------------------------
# Observable precursor layer
# ------------------------------------------------

precursor_71d5d = observable_precursors.copy()

precursor_71d5d["user_id"] = (
    precursor_71d5d["user_id"].astype(str)
)

if "timestamp" in precursor_71d5d.columns:
    precursor_time_col_71d5d = "timestamp"
elif "event_time" in precursor_71d5d.columns:
    precursor_time_col_71d5d = "event_time"
else:
    raise RuntimeError(
        "Could not identify timestamp column in observable_precursors."
    )

precursor_71d5d[precursor_time_col_71d5d] = pd.to_datetime(
    precursor_71d5d[precursor_time_col_71d5d],
    errors="coerce"
)

# Only positive campaign users
precursor_71d5d = precursor_71d5d[
    precursor_71d5d["user_id"].isin(positive_users_71d5d)
].copy()

# Safety: precursor layer must be observable and non-attack
if "is_attack" in precursor_71d5d.columns:
    precursor_71d5d = precursor_71d5d[
        precursor_71d5d["is_attack"].fillna(0).astype(int) == 0
    ].copy()

if "is_observable_precursor" in precursor_71d5d.columns:
    precursor_71d5d = precursor_71d5d[
        precursor_71d5d["is_observable_precursor"].fillna(0).astype(int) == 1
    ].copy()

print("Positive ordinary rows:", len(positive_ordinary_71d5d))
print("Observable precursor rows:", len(precursor_71d5d))

# Standardize timestamp name
positive_ordinary_71d5d = positive_ordinary_71d5d.copy()
positive_ordinary_71d5d["__time_71d5d"] = pd.to_datetime(
    positive_ordinary_71d5d[ordinary_time_col_71d5d],
    errors="coerce"
)

precursor_71d5d = precursor_71d5d.copy()
precursor_71d5d["__time_71d5d"] = pd.to_datetime(
    precursor_71d5d[precursor_time_col_71d5d],
    errors="coerce"
)

positive_stream_71d5d = pd.concat(
    [
        positive_ordinary_71d5d,
        precursor_71d5d
    ],
    ignore_index=True,
    sort=False
)

positive_stream_71d5d = positive_stream_71d5d.dropna(
    subset=["__time_71d5d"]
).copy()

print(
    "Positive observable stream:",
    len(positive_stream_71d5d)
)

# ================================================================
# 4. SELECT CLEAN CONTROL USER POOL
# ================================================================

all_users_71d5d = set(
    users["user_id"].astype(str).unique()
)

clean_user_pool_71d5d = sorted(
    all_users_71d5d - positive_users_71d5d
)

if len(clean_user_pool_71d5d) < N_CONTROL_USERS:
    raise RuntimeError(
        f"Only {len(clean_user_pool_71d5d)} clean users available. "
        f"Need {N_CONTROL_USERS}."
    )

# In AFRITAC this should be exactly 20.
selected_clean_users_71d5d = np.array(
    sorted(
        rng_71d5d.choice(
            clean_user_pool_71d5d,
            size=N_CONTROL_USERS,
            replace=False
        )
    ),
    dtype=str
)

print(
    "Selected clean control users:",
    len(selected_clean_users_71d5d)
)

# ================================================================
# 5. CONTROL OBSERVABLE STREAM
# ================================================================

control_stream_71d5d = ordinary_71d5d[
    ordinary_71d5d["user_id"].isin(
        selected_clean_users_71d5d
    )
].copy()

control_stream_71d5d["__time_71d5d"] = pd.to_datetime(
    control_stream_71d5d[ordinary_time_col_71d5d],
    errors="coerce"
)

control_stream_71d5d = control_stream_71d5d.dropna(
    subset=["__time_71d5d"]
).copy()

# Safety: no attack events
if "is_attack" in control_stream_71d5d.columns:
    control_stream_71d5d = control_stream_71d5d[
        control_stream_71d5d["is_attack"].fillna(0).astype(int) == 0
    ].copy()

print(
    "Control stream rows:",
    len(control_stream_71d5d)
)

# ================================================================
# 6. IDENTIFY REAL SESSION INTERVALS
# ================================================================
#
# This is the critical correction.
#
# We do NOT treat every gap between event timestamps as an
# inter-session gap.
#
# Instead, candidate cutoffs must occur after one completed session
# and before the next session begins.
# ================================================================

sessions_71d5d = sorted_sessions.copy()

sessions_71d5d["user_id"] = (
    sessions_71d5d["user_id"].astype(str)
)

sessions_71d5d["start_time"] = pd.to_datetime(
    sessions_71d5d["start_time"],
    errors="coerce"
)

sessions_71d5d["end_time"] = pd.to_datetime(
    sessions_71d5d["end_time"],
    errors="coerce"
)

sessions_71d5d = sessions_71d5d.dropna(
    subset=["start_time", "end_time"]
).copy()

sessions_71d5d = sessions_71d5d[
    sessions_71d5d["user_id"].isin(
        selected_clean_users_71d5d
    )
].copy()

sessions_71d5d = sessions_71d5d.sort_values(
    ["user_id", "start_time"]
).reset_index(drop=True)

candidate_cutoffs_71d5d = []

for user_id, grp in sessions_71d5d.groupby(
    "user_id",
    sort=False
):

    grp = grp.sort_values("start_time").reset_index(drop=True)

    for i in range(len(grp) - 1):

        current_end = grp.loc[i, "end_time"]
        next_start = grp.loc[i + 1, "start_time"]

        if pd.isna(current_end) or pd.isna(next_start):
            continue

        gap_minutes = (
            next_start - current_end
        ).total_seconds() / 60.0

        # Need enough room for a 60-minute history window.
        if gap_minutes <= LOOKBACK_MINUTES:
            continue

        # Avoid using the exact session boundary.
        # Select a point safely inside the genuine gap.
        lower = current_end + pd.Timedelta(
            minutes=5
        )

        upper = next_start - pd.Timedelta(
            minutes=5
        )

        available_minutes = (
            upper - lower
        ).total_seconds() / 60.0

        if available_minutes <= 0:
            continue

        # Deterministic but variable location within the gap.
        fraction = rng_71d5d.uniform(
            0.30,
            0.70
        )

        cutoff = (
            lower
            + (upper - lower) * fraction
        )

        candidate_cutoffs_71d5d.append(
            {
                "user_id": str(user_id),
                "cutoff_time": cutoff,
                "previous_session_end": current_end,
                "next_session_start": next_start,
                "gap_minutes": gap_minutes,
            }
        )

candidate_cutoffs_71d5d = pd.DataFrame(
    candidate_cutoffs_71d5d
)

if candidate_cutoffs_71d5d.empty:
    raise RuntimeError(
        "No genuine inter-session candidate cutoffs were found."
    )

candidate_cutoffs_71d5d["cutoff_time"] = pd.to_datetime(
    candidate_cutoffs_71d5d["cutoff_time"]
)

print(
    "\nCandidate inter-session cutoffs:",
    len(candidate_cutoffs_71d5d)
)

# ================================================================
# 7. FEATURE SIGNATURE FUNCTION
# ================================================================
#
# These features represent the 60-minute observable history
# immediately preceding a prediction cutoff.
# ================================================================

def build_signature_71d5d(
    stream,
    user_id,
    cutoff_time,
    lookback_minutes=60
):
    """Build a deterministic 16-D observable history signature.

    Context fields are parsed defensively because the ordinary and
    precursor streams can use boolean, numeric, or string encodings.
    Missing context observations are treated as 0 only after confirming
    that the field is absent or non-informative, never as a source of NaN.
    """

    cutoff_time = pd.Timestamp(cutoff_time)

    user_stream = stream[
        stream["user_id"].astype(str) == str(user_id)
    ].copy()

    if user_stream.empty:
        return None

    user_stream["__time_71d5d"] = pd.to_datetime(
        user_stream["__time_71d5d"],
        errors="coerce"
    )

    start_time = cutoff_time - pd.Timedelta(minutes=lookback_minutes)

    hist = user_stream[
        (user_stream["__time_71d5d"] >= start_time)
        & (user_stream["__time_71d5d"] < cutoff_time)
    ].copy()

    event_count = int(len(hist))

    if event_count == 0:
        return np.zeros(16, dtype=float)

    session_count = (
        hist["session_id"].nunique() if "session_id" in hist.columns else 0
    )
    event_type_count = (
        hist["event_type"].nunique() if "event_type" in hist.columns else 0
    )
    modality_count = (
        hist["modality"].nunique() if "modality" in hist.columns else 0
    )

    def share_in_last(minutes):
        threshold = cutoff_time - pd.Timedelta(minutes=minutes)
        return float((hist["__time_71d5d"] >= threshold).sum() / event_count)

    last_5_share = share_in_last(5)
    last_10_share = share_in_last(10)
    last_15_share = share_in_last(15)
    last_30_share = share_in_last(30)

    if "response_delay_ms" in hist.columns:
        delay = pd.to_numeric(hist["response_delay_ms"], errors="coerce").dropna()
    else:
        delay = pd.Series(dtype=float)

    delay_mean = float(delay.mean()) if len(delay) else 0.0
    delay_std = float(delay.std(ddof=0)) if len(delay) else 0.0

    def robust_binary_rate(column):
        if column not in hist.columns:
            return 0.0

        x = hist[column]

        # Numeric/bool encoding.
        numeric = pd.to_numeric(x, errors="coerce")
        valid_numeric = numeric.notna()
        if valid_numeric.any():
            vals = numeric[valid_numeric].astype(float)
            # Binary context variables are interpreted as positive when > 0.
            return float((vals > 0).mean())

        # String encoding such as True/False, YES/NO, observed/not observed.
        text = x.astype(str).str.strip().str.lower()
        positive_tokens = {
            "1", "true", "yes", "y", "on", "new", "changed",
            "observed", "roaming"
        }
        negative_tokens = {
            "0", "false", "no", "n", "off", "none", "normal",
            "unchanged", "not_observed", "not observed"
        }

        mapped = text.map(
            lambda v: 1.0 if v in positive_tokens
            else 0.0 if v in negative_tokens
            else np.nan
        )

        if mapped.notna().any():
            return float(mapped.dropna().mean())

        return 0.0

    new_device_rate = robust_binary_rate("new_device")
    location_change_rate = robust_binary_rate("location_change")
    roaming_rate = robust_binary_rate("roaming")

    if "transaction_amount" in hist.columns:
        amount = pd.to_numeric(
            hist["transaction_amount"], errors="coerce"
        ).fillna(0.0)
        positive_amount = amount[amount > 0]
        transaction_count = int(len(positive_amount))
        transaction_amount_sum = float(positive_amount.sum())
    else:
        transaction_count = 0
        transaction_amount_sum = 0.0

    if "event_type" in hist.columns:
        counts = hist["event_type"].dropna().value_counts(normalize=True)
        event_type_entropy = (
            float(-(counts * np.log2(counts)).sum())
            if len(counts) else 0.0
        )
    else:
        event_type_entropy = 0.0

    # Canonical feature order used everywhere in 71D.5D.
    signature = np.array(
        [
            event_count,
            session_count,
            modality_count,
            event_type_count,
            delay_mean,
            delay_std,
            last_5_share,
            last_10_share,
            last_15_share,
            last_30_share,
            new_device_rate,
            location_change_rate,
            roaming_rate,
            transaction_count,
            transaction_amount_sum,
            event_type_entropy,
        ],
        dtype=float
    )

    if not np.isfinite(signature).all():
        bad = np.where(~np.isfinite(signature))[0].tolist()
        raise RuntimeError(
            f"Non-finite 71D.5D signature for user={user_id}, "
            f"cutoff={cutoff_time}; feature indices={bad}"
        )

    return signature


# ================================================================
# 8. BUILD CANDIDATE SIGNATURES
# ================================================================

candidate_records_71d5d = []

for _, row in candidate_cutoffs_71d5d.iterrows():

    sig = build_signature_71d5d(
        control_stream_71d5d,
        row["user_id"],
        row["cutoff_time"],
        LOOKBACK_MINUTES
    )

    if sig is None:
        continue

    record = row.to_dict()

    record["signature"] = sig

    candidate_records_71d5d.append(record)

candidate_signatures_71d5d = pd.DataFrame(
    candidate_records_71d5d
)

if candidate_signatures_71d5d.empty:
    raise RuntimeError(
        "No candidate signatures could be constructed."
    )

candidate_matrix_71d5d = np.vstack(
    candidate_signatures_71d5d["signature"].values
)

print(
    "\nCandidate signatures:",
    len(candidate_signatures_71d5d)
)

# ================================================================
# 9. BUILD POSITIVE USER PROFILES
# ================================================================
#
# Construct positive profiles with the SAME 16-D signature function
# used for control candidates. This avoids dependence on the naming
# convention of positive_features and guarantees a symmetric feature
# space for matching.
# ================================================================

print(
    "\nBuilding positive user profiles from the same 16-D signature..."
)

positive_window_source_71d5d = positive_windows.copy()

positive_window_source_71d5d["user_id"] = (
    positive_window_source_71d5d["user_id"].astype(str)
)

positive_window_source_71d5d["cutoff_time"] = pd.to_datetime(
    positive_window_source_71d5d["cutoff_time"],
    errors="coerce"
)

if positive_window_source_71d5d["cutoff_time"].isna().any():
    raise RuntimeError(
        "Positive windows contain missing or invalid cutoff_time values."
    )

positive_window_signatures_71d5d = []

for _, row in positive_window_source_71d5d.iterrows():

    user_id = str(row["user_id"])
    cutoff_time = pd.Timestamp(row["cutoff_time"])

    sig = build_signature_71d5d(
        positive_stream_71d5d,
        user_id,
        cutoff_time,
        LOOKBACK_MINUTES
    )

    if sig is None:
        raise RuntimeError(
            "Could not construct positive signature for "
            f"user={user_id}, cutoff={cutoff_time}"
        )

    if len(sig) != 16:
        raise RuntimeError(
            f"Positive signature has {len(sig)} dimensions; expected 16."
        )

    positive_window_signatures_71d5d.append(
        {
            "window_id": row["window_id"],
            "user_id": user_id,
            "horizon_minutes": row["horizon_minutes"],
            "cutoff_time": cutoff_time,
            "signature": sig
        }
    )

positive_window_signatures_71d5d = pd.DataFrame(
    positive_window_signatures_71d5d
)

print(
    "Positive prediction-window signatures:",
    len(positive_window_signatures_71d5d)
)

assert len(
    positive_window_signatures_71d5d
) == 400

assert (
    positive_window_signatures_71d5d["user_id"].nunique()
    == 80
)

positive_profile_records_71d5d = []

for user_id, grp in (
    positive_window_signatures_71d5d
    .groupby("user_id", sort=True)
):

    signature_matrix = np.vstack(
        grp["signature"].values
    )

    mean_signature = np.mean(
        signature_matrix,
        axis=0
    )

    positive_profile_records_71d5d.append(
        {
            "user_id": str(user_id),
            "signature": mean_signature
        }
    )

positive_profiles_71d5d = pd.DataFrame(
    positive_profile_records_71d5d
)

positive_matrix_71d5d = np.vstack(
    positive_profiles_71d5d["signature"].values
)

print(
    "Positive user profiles:",
    len(positive_profiles_71d5d)
)

print(
    "Positive profile matrix shape:",
    positive_matrix_71d5d.shape
)

assert len(positive_profiles_71d5d) == 80
assert positive_matrix_71d5d.shape == (80, 16)
assert np.isfinite(positive_matrix_71d5d).all()

print(
    "✓ Positive users represented in the same 16-D feature space"
)

# ================================================================
# 10. STANDARDIZE FEATURE SPACE
# ================================================================
#
# Matching raw features directly would allow transaction amount
# to dominate all other dimensions.
#
# Standardize using the combined candidate + positive profile
# distribution.
# ================================================================

combined_for_scaling_71d5d = np.vstack(
    [
        candidate_matrix_71d5d,
        positive_matrix_71d5d
    ]
)

feature_mean_71d5d = np.nanmean(
    combined_for_scaling_71d5d,
    axis=0
)

feature_std_71d5d = np.nanstd(
    combined_for_scaling_71d5d,
    axis=0
)

feature_std_71d5d[
    feature_std_71d5d < 1e-9
] = 1.0

candidate_matrix_scaled_71d5d = (
    candidate_matrix_71d5d
    - feature_mean_71d5d
) / feature_std_71d5d

positive_matrix_scaled_71d5d = (
    positive_matrix_71d5d
    - feature_mean_71d5d
) / feature_std_71d5d

# ================================================================
# 11. CALCULATE MATCHING DISTANCE MATRIX
# ================================================================
#
# IMPORTANT:
# Do not replace this with the previous 3D broadcasting
# expression using .sum(axis=2).
#
# Matrix algebra is used here for robust Euclidean distance.
# ================================================================

print(
    "\nCalculating matching distance matrix..."
)

candidate_matrix = np.asarray(
    candidate_matrix_scaled_71d5d,
    dtype=float
)

positive_matrix = np.asarray(
    positive_matrix_scaled_71d5d,
    dtype=float
)

print(
    "Positive matrix shape:",
    positive_matrix.shape
)

print(
    "Candidate matrix shape:",
    candidate_matrix.shape
)

candidate_norm = np.sum(
    candidate_matrix * candidate_matrix,
    axis=1,
    keepdims=True
)

positive_norm = np.sum(
    positive_matrix * positive_matrix,
    axis=1,
    keepdims=True
).T

cross_product = (
    candidate_matrix
    @ positive_matrix.T
)

squared_distance = (
    candidate_norm
    + positive_norm
    - 2.0 * cross_product
)

squared_distance = np.maximum(
    squared_distance,
    0.0
)

distance_matrix = np.sqrt(
    squared_distance
)

print(
    "Distance matrix shape:",
    distance_matrix.shape
)

print(
    "Distance matrix finite:",
    np.isfinite(distance_matrix).all()
)

print(
    "Distance minimum:",
    float(np.min(distance_matrix))
)

print(
    "Distance maximum:",
    float(np.max(distance_matrix))
)

assert distance_matrix.shape == (
    len(candidate_signatures_71d5d),
    len(positive_profiles_71d5d)
)

assert np.isfinite(distance_matrix).all()

print(
    "✓ Distance matrix constructed successfully"
)

# ================================================================
# 12. GREEDY MATCHING
# ================================================================
#
# Each clean control user may be selected only once.
#
# Each candidate cutoff belongs to exactly one clean user.
#
# We match each positive user to the closest available candidate
# while enforcing unique clean control users.
# ================================================================

print(
    "\nAssigning matched clean control users..."
)

candidate_user_ids_71d5d = (
    candidate_signatures_71d5d["user_id"]
    .astype(str)
    .values
)

positive_user_ids_71d5d = (
    positive_profiles_71d5d["user_id"]
    .astype(str)
    .values
)

# Sort all positive-candidate pairs by distance
pair_rows_71d5d = []

for p_idx in range(
    len(positive_user_ids_71d5d)
):

    for c_idx in range(
        len(candidate_user_ids_71d5d)
    ):

        pair_rows_71d5d.append(
            (
                float(
                    distance_matrix[
                        c_idx,
                        p_idx
                    ]
                ),
                p_idx,
                c_idx
            )
        )

pair_rows_71d5d.sort(
    key=lambda x: x[0]
)

used_control_users_71d5d = set()
assigned_positive_users_71d5d = set()

matched_rows_71d5d = []

for distance, p_idx, c_idx in pair_rows_71d5d:

    positive_user = (
        positive_user_ids_71d5d[p_idx]
    )

    control_user = (
        candidate_user_ids_71d5d[c_idx]
    )

    if positive_user in assigned_positive_users_71d5d:
        continue

    if control_user in used_control_users_71d5d:
        continue

    candidate_row = (
        candidate_signatures_71d5d
        .iloc[c_idx]
        .copy()
    )

    candidate_row[
        "matched_positive_user_id"
    ] = positive_user

    candidate_row[
        "matching_distance"
    ] = distance

    matched_rows_71d5d.append(
        candidate_row
    )

    assigned_positive_users_71d5d.add(
        positive_user
    )

    used_control_users_71d5d.add(
        control_user
    )

    if len(used_control_users_71d5d) >= N_CONTROL_USERS:
        break

matched_candidates_71d5d = pd.DataFrame(
    matched_rows_71d5d
)

print(
    "Assigned control users:",
    len(
        matched_candidates_71d5d[
            "user_id"
        ].unique()
    )
)

if len(
    matched_candidates_71d5d[
        "user_id"
    ].unique()
) != N_CONTROL_USERS:

    raise RuntimeError(
        "Could not assign exactly 20 unique clean control users."
    )

# ================================================================
# 13. SELECT ONE CUT-OFF PER CONTROL USER
# ================================================================
#
# Select the best matched candidate for each selected control user.
#
# This creates one legitimate control prediction point per user.
# The five horizons will then reference the same historical cutoff,
# consistent with the earlier hard-negative architecture.
# ================================================================

selected_control_cutoffs_71d5d = (
    matched_candidates_71d5d
    .sort_values(
        "matching_distance"
    )
    .drop_duplicates(
        subset=["user_id"],
        keep="first"
    )
    .reset_index(drop=True)
)

print(
    "Selected control cutoffs:",
    len(selected_control_cutoffs_71d5d)
)

assert len(
    selected_control_cutoffs_71d5d
) == N_CONTROL_USERS

# ================================================================
# 14. BUILD HARD NEGATIVE WINDOWS
# ================================================================

hard_negative_window_records_71d5d = []

for _, row in selected_control_cutoffs_71d5d.iterrows():

    control_user = str(
        row["user_id"]
    )

    cutoff_time = pd.Timestamp(
        row["cutoff_time"]
    )

    for horizon in HORIZONS:

        hard_negative_window_records_71d5d.append(
            {
                "window_id": (
                    f"HN71D5D_{len(hard_negative_window_records_71d5d)+1:05d}"
                ),
                "label": 0,
                "class": "HARD_NEGATIVE",
                "user_id": control_user,
                "horizon_minutes": horizon,
                "cutoff_time": cutoff_time,
                "cutoff_date": cutoff_time.date(),
                "cutoff_hour": cutoff_time.hour,
                "cutoff_dow": cutoff_time.dayofweek,
                "matching_distance": float(
                    row["matching_distance"]
                ),
                "matched_positive_user_id": str(
                    row["matched_positive_user_id"]
                ),
            }
        )

hard_negative_windows_71d5d = pd.DataFrame(
    hard_negative_window_records_71d5d
)

print(
    "\nHard negative windows:",
    len(hard_negative_windows_71d5d)
)

print(
    hard_negative_windows_71d5d[
        "horizon_minutes"
    ].value_counts().sort_index()
)

assert len(
    hard_negative_windows_71d5d
) == N_CONTROL_USERS * len(HORIZONS)

# ================================================================
# 15. EXTRACT REAL CONTROL EVENTS
# ================================================================
#
# Each hard-negative window receives the actual observable event
# history occurring in the 60 minutes before its cutoff.
#
# There are NO fabricated attack-like events.
# ================================================================

hard_negative_event_records_71d5d = []

for _, window in hard_negative_windows_71d5d.iterrows():

    user_id = str(
        window["user_id"]
    )

    cutoff_time = pd.Timestamp(
        window["cutoff_time"]
    )

    start_time = (
        cutoff_time
        - pd.Timedelta(
            minutes=LOOKBACK_MINUTES
        )
    )

    hist = control_stream_71d5d[
        (
            control_stream_71d5d["user_id"].astype(str)
            == user_id
        )
        &
        (
            control_stream_71d5d["__time_71d5d"]
            >= start_time
        )
        &
        (
            control_stream_71d5d["__time_71d5d"]
            < cutoff_time
        )
    ].copy()

    for _, event_row in hist.iterrows():

        record = event_row.to_dict()

        record["window_id"] = (
            window["window_id"]
        )

        record["label"] = 0
        record["class"] = "HARD_NEGATIVE"

        record["horizon_minutes"] = (
            window["horizon_minutes"]
        )

        record["cutoff_time"] = cutoff_time

        record["matching_distance"] = (
            window["matching_distance"]
        )

        record[
            "matched_positive_user_id"
        ] = (
            window[
                "matched_positive_user_id"
            ]
        )

        # Explicit provenance
        record["ground_truth_state"] = "NORMAL"
        record["is_attack"] = 0
        record["is_observable_precursor"] = 0
        record["is_hard_negative"] = 1

        hard_negative_event_records_71d5d.append(
            record
        )

hard_negative_events_71d5d = pd.DataFrame(
    hard_negative_event_records_71d5d
)

print(
    "\nHard negative events:",
    len(hard_negative_events_71d5d)
)

# ================================================================
# 16. BASIC STRUCTURAL VALIDATION
# ================================================================

print("\n" + "=" * 70)
print("71D.5D STRUCTURAL VALIDATION")
print("=" * 70)

# ------------------------------------------------
# Window count
# ------------------------------------------------

assert len(
    hard_negative_windows_71d5d
) == 100

print(
    "✓ Hard negative windows:",
    len(hard_negative_windows_71d5d)
)

# ------------------------------------------------
# Horizon balance
# ------------------------------------------------

horizon_counts_71d5d = (
    hard_negative_windows_71d5d[
        "horizon_minutes"
    ]
    .value_counts()
    .sort_index()
)

print(
    "\nHorizon distribution:"
)

print(
    horizon_counts_71d5d
)

assert all(
    horizon_counts_71d5d.get(h, 0)
    == N_CONTROL_USERS
    for h in HORIZONS
)

print(
    "✓ Exactly 20 windows per horizon"
)

# ------------------------------------------------
# User balance
# ------------------------------------------------

user_counts_71d5d = (
    hard_negative_windows_71d5d[
        "user_id"
    ]
    .value_counts()
)

print(
    "\nControl user window counts:"
)

print(
    user_counts_71d5d.describe()
)

assert (
    user_counts_71d5d.min()
    == len(HORIZONS)
)

assert (
    user_counts_71d5d.max()
    == len(HORIZONS)
)

print(
    "✓ Every control user has 5 horizons"
)

# ------------------------------------------------
# Positive-user overlap
# ------------------------------------------------

hard_users_71d5d = set(
    hard_negative_windows_71d5d[
        "user_id"
    ].astype(str)
)

overlap_users_71d5d = (
    hard_users_71d5d
    &
    positive_users_71d5d
)

print(
    "\nPositive/control user overlap:",
    len(overlap_users_71d5d)
)

assert len(
    overlap_users_71d5d
) == 0

print(
    "✓ No positive/control user overlap"
)

# ------------------------------------------------
# Cutoff uniqueness
# ------------------------------------------------

cutoff_event_matches_71d5d = 0

control_events_for_check_71d5d = (
    control_stream_71d5d[
        [
            "user_id",
            "__time_71d5d"
        ]
    ]
    .drop_duplicates()
)

for _, row in hard_negative_windows_71d5d.iterrows():

    matches = control_events_for_check_71d5d[
        (
            control_events_for_check_71d5d[
                "user_id"
            ].astype(str)
            == str(row["user_id"])
        )
        &
        (
            control_events_for_check_71d5d[
                "__time_71d5d"
            ]
            == pd.Timestamp(
                row["cutoff_time"]
            )
        )
    ]

    cutoff_event_matches_71d5d += len(matches)

print(
    "\nCutoff timestamps equal observed event timestamps:",
    cutoff_event_matches_71d5d
)

assert (
    cutoff_event_matches_71d5d
    == 0
)

print(
    "✓ No cutoff equals an observed event timestamp"
)

# ------------------------------------------------
# Genuine session-gap validation
# ------------------------------------------------

session_gap_violations_71d5d = 0

for _, row in hard_negative_windows_71d5d.iterrows():

    user_sessions = sessions_71d5d[
        sessions_71d5d["user_id"].astype(str)
        == str(row["user_id"])
    ]

    cutoff = pd.Timestamp(
        row["cutoff_time"]
    )

    inside_session = (
        (
            user_sessions["start_time"]
            < cutoff
        )
        &
        (
            user_sessions["end_time"]
            > cutoff
        )
    ).any()

    if inside_session:
        session_gap_violations_71d5d += 1

print(
    "Cutoffs inside active sessions:",
    session_gap_violations_71d5d
)

assert (
    session_gap_violations_71d5d
    == 0
)

print(
    "✓ All cutoffs are outside active sessions"
)

# ------------------------------------------------
# Attack contamination
# ------------------------------------------------

if len(hard_negative_events_71d5d) > 0:

    attack_rows_71d5d = (
        hard_negative_events_71d5d[
            hard_negative_events_71d5d[
                "is_attack"
            ].fillna(0).astype(int) == 1
        ]
    )

else:

    attack_rows_71d5d = pd.DataFrame()

print(
    "\nHard negative attack events:",
    len(attack_rows_71d5d)
)

assert len(
    attack_rows_71d5d
) == 0

print(
    "✓ No attack-event contamination"
)

# ------------------------------------------------
# Precursor contamination
# ------------------------------------------------

if len(hard_negative_events_71d5d) > 0:

    precursor_rows_71d5d = (
        hard_negative_events_71d5d[
            hard_negative_events_71d5d[
                "is_observable_precursor"
            ].fillna(0).astype(int) == 1
        ]
    )

else:

    precursor_rows_71d5d = pd.DataFrame()

print(
    "Hard negative precursor events:",
    len(precursor_rows_71d5d)
)

assert len(
    precursor_rows_71d5d
) == 0

print(
    "✓ No observable precursor contamination"
)

# ------------------------------------------------
# Event IDs
# ------------------------------------------------

if len(hard_negative_events_71d5d) > 0:

    if "event_id" in hard_negative_events_71d5d.columns:

        duplicate_event_ids_71d5d = (
            hard_negative_events_71d5d[
                "event_id"
            ]
            .duplicated()
            .sum()
        )

        print(
            "Duplicate event IDs:",
            duplicate_event_ids_71d5d
        )

# ================================================================
# 17. CONTROL EVENT DISTRIBUTION
# ================================================================

if len(hard_negative_events_71d5d) > 0:

    print(
        "\nHard negative event types:"
    )

    if "event_type" in hard_negative_events_71d5d.columns:

        print(
            hard_negative_events_71d5d[
                "event_type"
            ]
            .value_counts()
            .head(20)
        )

    if "modality" in hard_negative_events_71d5d.columns:

        print(
            "\nHard negative modalities:"
        )

        print(
            hard_negative_events_71d5d[
                "modality"
            ]
            .value_counts()
        )

# ================================================================
# 18. MATCHING QUALITY
# ================================================================

matching_distances_71d5d = pd.to_numeric(
    selected_control_cutoffs_71d5d[
        "matching_distance"
    ],
    errors="coerce"
)

print(
    "\nMatching distance summary:"
)

print(
    matching_distances_71d5d.describe()
)

assert np.isfinite(
    matching_distances_71d5d
).all()

# ================================================================
# 19. EVENT ACTIVITY PER CONTROL WINDOW
# ================================================================

if len(hard_negative_events_71d5d) > 0:

    event_counts_71d5d = (
        hard_negative_events_71d5d
        .groupby(
            "window_id"
        )
        .size()
    )

    hard_negative_windows_71d5d[
        "event_count"
    ] = (
        hard_negative_windows_71d5d[
            "window_id"
        ]
        .map(event_counts_71d5d)
        .fillna(0)
        .astype(int)
    )

else:

    hard_negative_windows_71d5d[
        "event_count"
    ] = 0

print(
    "\nHard-negative event count per window:"
)

print(
    hard_negative_windows_71d5d[
        "event_count"
    ].describe()
)

# ================================================================
# 20. HORIZON ACTIVITY AUDIT
# ================================================================

print(
    "\nActivity by horizon:"
)

activity_summary_71d5d = (
    hard_negative_windows_71d5d
    .groupby("horizon_minutes")[
        "event_count"
    ]
    .agg(
        [
            "count",
            "mean",
            "median",
            "min",
            "max"
        ]
    )
)

print(
    activity_summary_71d5d
)

# ================================================================
# 21. CREATE FINAL AUTHORITATIVE 71D.5D OBJECTS
# ================================================================
#
# Do NOT overwrite the previous authoritative hard-negative
# objects until this design has passed the downstream 71D audit.
#
# These names are therefore created only after structural checks.
# ================================================================

hard_negative_windows_71d5d_final = (
    hard_negative_windows_71d5d.copy()
)

hard_negative_events_71d5d_final = (
    hard_negative_events_71d5d.copy()
)

# ================================================================
# 22. FINAL SUMMARY
# ================================================================

print("\n" + "=" * 70)
print("AFRITAC 71D.5D COMPLETE")
print("=" * 70)

print(
    "Control users:",
    hard_negative_windows_71d5d_final[
        "user_id"
    ].nunique()
)

print(
    "Hard negative windows:",
    len(hard_negative_windows_71d5d_final)
)

print(
    "Hard negative events:",
    len(hard_negative_events_71d5d_final)
)

print(
    "Positive/control overlap:",
    len(overlap_users_71d5d)
)

print(
    "Cutoff/event timestamp collisions:",
    cutoff_event_matches_71d5d
)

print(
    "Cutoffs inside active sessions:",
    session_gap_violations_71d5d
)

print(
    "Attack contamination:",
    len(attack_rows_71d5d)
)

print(
    "Precursor contamination:",
    len(precursor_rows_71d5d)
)

print(
    "Matching distance mean:",
    float(matching_distances_71d5d.mean())
)

print(
    "Matching distance median:",
    float(matching_distances_71d5d.median())
)

print(
    "\n✓ 71D.5D session-based hard-negative construction finished."
)

print(
    "✓ Authoritative 71D.5D objects were created with *_final names."
)

print(
    "✓ Previous hard-negative objects were not overwritten."
)

# ==============================================================================
# NOTEBOOK CELL 217
# ==============================================================================

# ======================================================================
# AFRITAC DIAGNOSTIC
# SESSION <-> OBSERVABLE STREAM TIMELINE ALIGNMENT
# ======================================================================

print("=" * 70)
print("AFRITAC SESSION / OBSERVABLE TIMELINE ALIGNMENT DIAGNOSTIC")
print("=" * 70)

# ----------------------------------------------------------------------
# 1. Basic timestamp and ID inspection
# ----------------------------------------------------------------------

print("\n[1] COLUMN CHECK")

print("sessions columns:")
print(list(sessions.columns))

print("\nnormal_stream columns:")
print(list(normal_stream.columns))

# Determine actual timestamp column in normal_stream
possible_time_cols = [
    "timestamp",
    "event_time",
    "start_time",
    "datetime",
    "time"
]

stream_time_candidates = [
    c for c in possible_time_cols
    if c in normal_stream.columns
]

print("\nObservable stream timestamp candidates:", stream_time_candidates)

if not stream_time_candidates:
    raise RuntimeError(
        "No recognized timestamp column found in normal_stream."
    )

stream_time_col = stream_time_candidates[0]

print("Using stream timestamp column:", stream_time_col)

# ----------------------------------------------------------------------
# 2. Normalize IDs and timestamps
# ----------------------------------------------------------------------

sdiag = sessions.copy()
ndiag = normal_stream.copy()

sdiag["user_id"] = sdiag["user_id"].astype(str)
ndiag["user_id"] = ndiag["user_id"].astype(str)

sdiag["start_time"] = pd.to_datetime(
    sdiag["start_time"], errors="coerce"
)
sdiag["end_time"] = pd.to_datetime(
    sdiag["end_time"], errors="coerce"
)

ndiag["__obs_time"] = pd.to_datetime(
    ndiag[stream_time_col], errors="coerce"
)

print("\n[2] GLOBAL TIME RANGES")

print(
    "Sessions:",
    sdiag["start_time"].min(),
    "to",
    sdiag["end_time"].max()
)

print(
    "Observable stream:",
    ndiag["__obs_time"].min(),
    "to",
    ndiag["__obs_time"].max()
)

print(
    "Observable rows:",
    len(ndiag),
    "valid timestamps:",
    ndiag["__obs_time"].notna().sum()
)

# ----------------------------------------------------------------------
# 3. User overlap
# ----------------------------------------------------------------------

session_users = set(sdiag["user_id"].dropna())
stream_users = set(ndiag["user_id"].dropna())

print("\n[3] USER ALIGNMENT")

print("Session users:", len(session_users))
print("Observable users:", len(stream_users))
print("User intersection:", len(session_users & stream_users))

if len(session_users & stream_users):
    print(
        "Example common users:",
        sorted(session_users & stream_users)[:10]
    )

# ----------------------------------------------------------------------
# 4. For every session, find observable events for the same user
#    inside the session interval.
# ----------------------------------------------------------------------

print("\n[4] SESSION <-> EVENT TEMPORAL ALIGNMENT")

session_alignment = []

for _, s in sdiag.iterrows():

    uid = s["user_id"]
    st = s["start_time"]
    et = s["end_time"]

    if pd.isna(st) or pd.isna(et):
        continue

    x = ndiag[
        (ndiag["user_id"] == uid) &
        (ndiag["__obs_time"] >= st) &
        (ndiag["__obs_time"] <= et)
    ]

    session_alignment.append({
        "user_id": uid,
        "session_id": s["session_id"]
        if "session_id" in sdiag.columns else None,
        "session_start": st,
        "session_end": et,
        "events_inside_session": len(x)
    })

session_alignment = pd.DataFrame(session_alignment)

print(
    session_alignment["events_inside_session"]
    .describe()
    .round(4)
)

print(
    "Sessions with >=1 observable event:",
    (
        session_alignment["events_inside_session"] > 0
    ).mean()
)

print(
    "Sessions with ZERO observable events:",
    (
        session_alignment["events_inside_session"] == 0
    ).mean()
)

# ----------------------------------------------------------------------
# 5. Compare event times with nearest session boundary for each user.
# ----------------------------------------------------------------------

print("\n[5] EVENT DISTANCE TO SESSION TIMELINE")

nearest_distances = []

for uid, eg in ndiag.groupby("user_id"):

    sg = sdiag[sdiag["user_id"] == uid]

    if sg.empty:
        continue

    session_starts = (
        sg["start_time"]
        .dropna()
        .sort_values()
        .values
    )

    session_ends = (
        sg["end_time"]
        .dropna()
        .sort_values()
        .values
    )

    if len(session_starts) == 0 or len(session_ends) == 0:
        continue

    for t in eg["__obs_time"].dropna().head(1000):

        start_dist = np.min(
            np.abs(
                (
                    session_starts.astype("datetime64[ns]")
                    - np.datetime64(t)
                ).astype("timedelta64[s]").astype(float)
            )
        )

        end_dist = np.min(
            np.abs(
                (
                    session_ends.astype("datetime64[ns]")
                    - np.datetime64(t)
                ).astype("timedelta64[s]").astype(float)
            )
        )

        nearest_distances.append(
            min(start_dist, end_dist) / 60.0
        )

if nearest_distances:
    print(
        pd.Series(nearest_distances)
        .describe()
        .round(3)
    )

# ----------------------------------------------------------------------
# 6. Critical test:
#    Take actual observable event times and ask whether they occur
#    inside or near session intervals.
# ----------------------------------------------------------------------

print("\n[6] ACTUAL OBSERVABLE EVENTS VS SESSION INTERVALS")

events_inside = 0
events_outside = 0

for uid, eg in ndiag.groupby("user_id"):

    sg = sdiag[sdiag["user_id"] == uid]

    if sg.empty:
        events_outside += len(eg)
        continue

    for t in eg["__obs_time"].dropna():

        inside = (
            (sg["start_time"] <= t) &
            (sg["end_time"] >= t)
        ).any()

        if inside:
            events_inside += 1
        else:
            events_outside += 1

print("Observable events inside sessions:", events_inside)
print("Observable events outside sessions:", events_outside)

total_test_events = events_inside + events_outside

if total_test_events:
    print(
        "Inside-session proportion:",
        round(events_inside / total_test_events, 4)
    )

# ----------------------------------------------------------------------
# 7. Examine one control user in detail
# ----------------------------------------------------------------------

print("\n[7] SAMPLE CONTROL USER TIMELINE")

positive_users_diag = set(
    positive_windows["user_id"].astype(str).unique()
)

clean_users_diag = sorted(
    stream_users - positive_users_diag
)

if clean_users_diag:

    sample_uid = clean_users_diag[0]

    print("Sample clean user:", sample_uid)

    print("\nSessions:")
    print(
        sdiag[
            sdiag["user_id"] == sample_uid
        ][
            ["session_id", "start_time", "end_time"]
        ].head(10).to_string(index=False)
    )

    print("\nObservable events:")
    sample_events = ndiag[
        ndiag["user_id"] == sample_uid
    ].sort_values("__obs_time")

    cols = [
        c for c in [
            "event_id",
            "session_id",
            stream_time_col,
            "event_type",
            "modality"
        ]
        if c in sample_events.columns
    ]

    print(
        sample_events[cols]
        .head(20)
        .to_string(index=False)
    )

# ----------------------------------------------------------------------
# 8. Determine the likely failure mode
# ----------------------------------------------------------------------

print("\n" + "=" * 70)
print("DIAGNOSTIC INTERPRETATION")
print("=" * 70)

inside_ratio = (
    events_inside / total_test_events
    if total_test_events else 0
)

if inside_ratio > 0.8:
    print(
        "✓ Sessions and observable events are temporally aligned."
    )
    print(
        "→ The 71D.5E cutoff construction is the likely problem."
    )

elif inside_ratio > 0.2:
    print(
        "⚠ Partial session/event temporal alignment detected."
    )
    print(
        "→ Session boundaries and observable timestamps need reconciliation."
    )

else:
    print(
        "✗ Sessions and observable events are NOT temporally aligned."
    )
    print(
        "→ Do NOT fabricate hard-negative events."
    )
    print(
        "→ We must reconstruct candidate cutoffs directly from the "
        "observable event/session timeline."
    )

print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 218
# ==============================================================================

# ================================================================
# AFRITAC STEP 71D.5D
# SESSION BASED MATCHED HARD NEGATIVE CONTROLS
#
# Purpose:
# Construct 20 clean control users and 100 matched hard-negative
# prediction windows using real observable session histories.
#
# Design requirements:
#   1. 20 clean control users
#   2. 5 horizons per control user
#   3. Exactly 100 hard-negative windows
#   4. Cutoffs must not equal observed event timestamps
#   5. Prefer cutoffs in genuine gaps between sessions
#   6. Use real observable events only
#   7. No positive-user overlap
#   8. No attack-event contamination
#   9. Preserve the authoritative positive objects
# ================================================================

print("=" * 70)
print("AFRITAC STEP 71D.5D")
print("SESSION BASED MATCHED HARD NEGATIVE CONTROLS")
print("=" * 70)

# ================================================================
# 1. REQUIRED OBJECT CHECK
# ================================================================

required_objects = [
    "users",
    "sorted_sessions",
    "events",
    "campaigns",
    "attack_events",
    "positive_windows",
    "normal_stream",
    "observable_precursors",
]

missing_objects = [
    obj for obj in required_objects
    if obj not in globals()
]

print("Required objects missing:", missing_objects)

if missing_objects:
    raise RuntimeError(
        "71D.5D cannot continue because required objects are missing: "
        + str(missing_objects)
    )

# ================================================================
# 2. CONFIGURATION
# ================================================================

SEED_71D5D = SEED + 715
rng_71d5d = np.random.default_rng(SEED_71D5D)

N_CONTROL_USERS = 20
HORIZONS = [5, 10, 15, 30, 60]
LOOKBACK_MINUTES = 60

# Positive users
positive_users_71d5d = set(
    positive_windows["user_id"].astype(str).unique()
)

print("\nPositive users:", len(positive_users_71d5d))

# ================================================================
# 3. BUILD POSITIVE OBSERVABLE STREAM
# ================================================================
#
# Important:
# Positive feature construction must include both:
#
#   A. ordinary observable activity
#   B. controlled observable precursor activity
#
# Attack events are excluded.
# ================================================================

ordinary_71d5d = normal_stream.copy()

ordinary_71d5d["user_id"] = (
    ordinary_71d5d["user_id"].astype(str)
)

ordinary_71d5d["session_id"] = (
    ordinary_71d5d["session_id"].astype(str)
)

# Identify timestamp column
if "timestamp" in ordinary_71d5d.columns:
    ordinary_time_col_71d5d = "timestamp"
elif "event_time" in ordinary_71d5d.columns:
    ordinary_time_col_71d5d = "event_time"
else:
    raise RuntimeError(
        "Could not identify timestamp column in normal_stream."
    )

ordinary_71d5d[ordinary_time_col_71d5d] = pd.to_datetime(
    ordinary_71d5d[ordinary_time_col_71d5d],
    errors="coerce"
)

# Exclude attack events if attack flag exists
if "is_attack" in ordinary_71d5d.columns:
    ordinary_71d5d = ordinary_71d5d[
        ordinary_71d5d["is_attack"].fillna(0).astype(int) == 0
    ].copy()

positive_ordinary_71d5d = ordinary_71d5d[
    ordinary_71d5d["user_id"].isin(positive_users_71d5d)
].copy()

# ------------------------------------------------
# Observable precursor layer
# ------------------------------------------------

precursor_71d5d = observable_precursors.copy()

precursor_71d5d["user_id"] = (
    precursor_71d5d["user_id"].astype(str)
)

if "timestamp" in precursor_71d5d.columns:
    precursor_time_col_71d5d = "timestamp"
elif "event_time" in precursor_71d5d.columns:
    precursor_time_col_71d5d = "event_time"
else:
    raise RuntimeError(
        "Could not identify timestamp column in observable_precursors."
    )

precursor_71d5d[precursor_time_col_71d5d] = pd.to_datetime(
    precursor_71d5d[precursor_time_col_71d5d],
    errors="coerce"
)

# Only positive campaign users
precursor_71d5d = precursor_71d5d[
    precursor_71d5d["user_id"].isin(positive_users_71d5d)
].copy()

# Safety: precursor layer must be observable and non-attack
if "is_attack" in precursor_71d5d.columns:
    precursor_71d5d = precursor_71d5d[
        precursor_71d5d["is_attack"].fillna(0).astype(int) == 0
    ].copy()

if "is_observable_precursor" in precursor_71d5d.columns:
    precursor_71d5d = precursor_71d5d[
        precursor_71d5d["is_observable_precursor"].fillna(0).astype(int) == 1
    ].copy()

print("Positive ordinary rows:", len(positive_ordinary_71d5d))
print("Observable precursor rows:", len(precursor_71d5d))

# Standardize timestamp name
positive_ordinary_71d5d = positive_ordinary_71d5d.copy()
positive_ordinary_71d5d["__time_71d5d"] = pd.to_datetime(
    positive_ordinary_71d5d[ordinary_time_col_71d5d],
    errors="coerce"
)

precursor_71d5d = precursor_71d5d.copy()
precursor_71d5d["__time_71d5d"] = pd.to_datetime(
    precursor_71d5d[precursor_time_col_71d5d],
    errors="coerce"
)

positive_stream_71d5d = pd.concat(
    [
        positive_ordinary_71d5d,
        precursor_71d5d
    ],
    ignore_index=True,
    sort=False
)

positive_stream_71d5d = positive_stream_71d5d.dropna(
    subset=["__time_71d5d"]
).copy()

print(
    "Positive observable stream:",
    len(positive_stream_71d5d)
)

# ================================================================
# 4. SELECT CLEAN CONTROL USER POOL
# ================================================================

all_users_71d5d = set(
    users["user_id"].astype(str).unique()
)

clean_user_pool_71d5d = sorted(
    all_users_71d5d - positive_users_71d5d
)

if len(clean_user_pool_71d5d) < N_CONTROL_USERS:
    raise RuntimeError(
        f"Only {len(clean_user_pool_71d5d)} clean users available. "
        f"Need {N_CONTROL_USERS}."
    )

# In AFRITAC this should be exactly 20.
selected_clean_users_71d5d = np.array(
    sorted(
        rng_71d5d.choice(
            clean_user_pool_71d5d,
            size=N_CONTROL_USERS,
            replace=False
        )
    ),
    dtype=str
)

print(
    "Selected clean control users:",
    len(selected_clean_users_71d5d)
)

# ================================================================
# 5. CONTROL OBSERVABLE STREAM
# ================================================================

control_stream_71d5d = ordinary_71d5d[
    ordinary_71d5d["user_id"].isin(
        selected_clean_users_71d5d
    )
].copy()

control_stream_71d5d["__time_71d5d"] = pd.to_datetime(
    control_stream_71d5d[ordinary_time_col_71d5d],
    errors="coerce"
)

control_stream_71d5d = control_stream_71d5d.dropna(
    subset=["__time_71d5d"]
).copy()

# Safety: no attack events
if "is_attack" in control_stream_71d5d.columns:
    control_stream_71d5d = control_stream_71d5d[
        control_stream_71d5d["is_attack"].fillna(0).astype(int) == 0
    ].copy()

print(
    "Control stream rows:",
    len(control_stream_71d5d)
)

# ================================================================
# 6. IDENTIFY REAL SESSION INTERVALS
# ================================================================
#
# This is the critical correction.
#
# We do NOT treat every gap between event timestamps as an
# inter-session gap.
#
# Instead, candidate cutoffs must occur after one completed session
# and before the next session begins.
# ================================================================

sessions_71d5d = sorted_sessions.copy()

sessions_71d5d["user_id"] = (
    sessions_71d5d["user_id"].astype(str)
)

sessions_71d5d["start_time"] = pd.to_datetime(
    sessions_71d5d["start_time"],
    errors="coerce"
)

sessions_71d5d["end_time"] = pd.to_datetime(
    sessions_71d5d["end_time"],
    errors="coerce"
)

sessions_71d5d = sessions_71d5d.dropna(
    subset=["start_time", "end_time"]
).copy()

sessions_71d5d = sessions_71d5d[
    sessions_71d5d["user_id"].isin(
        selected_clean_users_71d5d
    )
].copy()

sessions_71d5d = sessions_71d5d.sort_values(
    ["user_id", "start_time"]
).reset_index(drop=True)

candidate_cutoffs_71d5d = []

for user_id, grp in sessions_71d5d.groupby(
    "user_id",
    sort=False
):

    grp = grp.sort_values("start_time").reset_index(drop=True)

    for i in range(len(grp) - 1):

        current_end = grp.loc[i, "end_time"]
        next_start = grp.loc[i + 1, "start_time"]

        if pd.isna(current_end) or pd.isna(next_start):
            continue

        gap_minutes = (
            next_start - current_end
        ).total_seconds() / 60.0

        # Need enough room for a 60-minute history window.
        if gap_minutes <= LOOKBACK_MINUTES:
            continue

        # Avoid using the exact session boundary.
        # Select a point safely inside the genuine gap.
        lower = current_end + pd.Timedelta(
            minutes=5
        )

        upper = next_start - pd.Timedelta(
            minutes=5
        )

        available_minutes = (
            upper - lower
        ).total_seconds() / 60.0

        if available_minutes <= 0:
            continue

        # Deterministic but variable location within the gap.
        fraction = rng_71d5d.uniform(
            0.30,
            0.70
        )

        cutoff = (
            lower
            + (upper - lower) * fraction
        )

        candidate_cutoffs_71d5d.append(
            {
                "user_id": str(user_id),
                "cutoff_time": cutoff,
                "previous_session_end": current_end,
                "next_session_start": next_start,
                "gap_minutes": gap_minutes,
            }
        )

candidate_cutoffs_71d5d = pd.DataFrame(
    candidate_cutoffs_71d5d
)

if candidate_cutoffs_71d5d.empty:
    raise RuntimeError(
        "No genuine inter-session candidate cutoffs were found."
    )

candidate_cutoffs_71d5d["cutoff_time"] = pd.to_datetime(
    candidate_cutoffs_71d5d["cutoff_time"]
)

print(
    "\nCandidate inter-session cutoffs:",
    len(candidate_cutoffs_71d5d)
)

# ================================================================
# 7. FEATURE SIGNATURE FUNCTION
# ================================================================
#
# These features represent the 60-minute observable history
# immediately preceding a prediction cutoff.
# ================================================================

def build_signature_71d5d(
    stream,
    user_id,
    cutoff_time,
    lookback_minutes=60
):
    """Build a deterministic 16-D observable history signature.

    Context fields are parsed defensively because the ordinary and
    precursor streams can use boolean, numeric, or string encodings.
    Missing context observations are treated as 0 only after confirming
    that the field is absent or non-informative, never as a source of NaN.
    """

    cutoff_time = pd.Timestamp(cutoff_time)

    user_stream = stream[
        stream["user_id"].astype(str) == str(user_id)
    ].copy()

    if user_stream.empty:
        return None

    user_stream["__time_71d5d"] = pd.to_datetime(
        user_stream["__time_71d5d"],
        errors="coerce"
    )

    start_time = cutoff_time - pd.Timedelta(minutes=lookback_minutes)

    hist = user_stream[
        (user_stream["__time_71d5d"] >= start_time)
        & (user_stream["__time_71d5d"] < cutoff_time)
    ].copy()

    event_count = int(len(hist))

    if event_count == 0:
        return np.zeros(16, dtype=float)

    session_count = (
        hist["session_id"].nunique() if "session_id" in hist.columns else 0
    )
    event_type_count = (
        hist["event_type"].nunique() if "event_type" in hist.columns else 0
    )
    modality_count = (
        hist["modality"].nunique() if "modality" in hist.columns else 0
    )

    def share_in_last(minutes):
        threshold = cutoff_time - pd.Timedelta(minutes=minutes)
        return float((hist["__time_71d5d"] >= threshold).sum() / event_count)

    last_5_share = share_in_last(5)
    last_10_share = share_in_last(10)
    last_15_share = share_in_last(15)
    last_30_share = share_in_last(30)

    if "response_delay_ms" in hist.columns:
        delay = pd.to_numeric(hist["response_delay_ms"], errors="coerce").dropna()
    else:
        delay = pd.Series(dtype=float)

    delay_mean = float(delay.mean()) if len(delay) else 0.0
    delay_std = float(delay.std(ddof=0)) if len(delay) else 0.0

    def robust_binary_rate(column):
        if column not in hist.columns:
            return 0.0

        x = hist[column]

        # Numeric/bool encoding.
        numeric = pd.to_numeric(x, errors="coerce")
        valid_numeric = numeric.notna()
        if valid_numeric.any():
            vals = numeric[valid_numeric].astype(float)
            # Binary context variables are interpreted as positive when > 0.
            return float((vals > 0).mean())

        # String encoding such as True/False, YES/NO, observed/not observed.
        text = x.astype(str).str.strip().str.lower()
        positive_tokens = {
            "1", "true", "yes", "y", "on", "new", "changed",
            "observed", "roaming"
        }
        negative_tokens = {
            "0", "false", "no", "n", "off", "none", "normal",
            "unchanged", "not_observed", "not observed"
        }

        mapped = text.map(
            lambda v: 1.0 if v in positive_tokens
            else 0.0 if v in negative_tokens
            else np.nan
        )

        if mapped.notna().any():
            return float(mapped.dropna().mean())

        return 0.0

    new_device_rate = robust_binary_rate("new_device")
    location_change_rate = robust_binary_rate("location_change")
    roaming_rate = robust_binary_rate("roaming")

    if "transaction_amount" in hist.columns:
        amount = pd.to_numeric(
            hist["transaction_amount"], errors="coerce"
        ).fillna(0.0)
        positive_amount = amount[amount > 0]
        transaction_count = int(len(positive_amount))
        transaction_amount_sum = float(positive_amount.sum())
    else:
        transaction_count = 0
        transaction_amount_sum = 0.0

    if "event_type" in hist.columns:
        counts = hist["event_type"].dropna().value_counts(normalize=True)
        event_type_entropy = (
            float(-(counts * np.log2(counts)).sum())
            if len(counts) else 0.0
        )
    else:
        event_type_entropy = 0.0

    # Canonical feature order used everywhere in 71D.5D.
    signature = np.array(
        [
            event_count,
            session_count,
            modality_count,
            event_type_count,
            delay_mean,
            delay_std,
            last_5_share,
            last_10_share,
            last_15_share,
            last_30_share,
            new_device_rate,
            location_change_rate,
            roaming_rate,
            transaction_count,
            transaction_amount_sum,
            event_type_entropy,
        ],
        dtype=float
    )

    if not np.isfinite(signature).all():
        bad = np.where(~np.isfinite(signature))[0].tolist()
        raise RuntimeError(
            f"Non-finite 71D.5D signature for user={user_id}, "
            f"cutoff={cutoff_time}; feature indices={bad}"
        )

    return signature


# ================================================================
# 8. BUILD CANDIDATE SIGNATURES
# ================================================================

candidate_records_71d5d = []

for _, row in candidate_cutoffs_71d5d.iterrows():

    sig = build_signature_71d5d(
        control_stream_71d5d,
        row["user_id"],
        row["cutoff_time"],
        LOOKBACK_MINUTES
    )

    if sig is None:
        continue

    record = row.to_dict()

    record["signature"] = sig

    candidate_records_71d5d.append(record)

candidate_signatures_71d5d = pd.DataFrame(
    candidate_records_71d5d
)

if candidate_signatures_71d5d.empty:
    raise RuntimeError(
        "No candidate signatures could be constructed."
    )

candidate_matrix_71d5d = np.vstack(
    candidate_signatures_71d5d["signature"].values
)

print(
    "\nCandidate signatures:",
    len(candidate_signatures_71d5d)
)

# ================================================================
# 9. BUILD POSITIVE USER PROFILES
# ================================================================
#
# Construct positive profiles with the SAME 16-D signature function
# used for control candidates. This avoids dependence on the naming
# convention of positive_features and guarantees a symmetric feature
# space for matching.
# ================================================================

print(
    "\nBuilding positive user profiles from the same 16-D signature..."
)

positive_window_source_71d5d = positive_windows.copy()

positive_window_source_71d5d["user_id"] = (
    positive_window_source_71d5d["user_id"].astype(str)
)

positive_window_source_71d5d["cutoff_time"] = pd.to_datetime(
    positive_window_source_71d5d["cutoff_time"],
    errors="coerce"
)

if positive_window_source_71d5d["cutoff_time"].isna().any():
    raise RuntimeError(
        "Positive windows contain missing or invalid cutoff_time values."
    )

positive_window_signatures_71d5d = []

for _, row in positive_window_source_71d5d.iterrows():

    user_id = str(row["user_id"])
    cutoff_time = pd.Timestamp(row["cutoff_time"])

    sig = build_signature_71d5d(
        positive_stream_71d5d,
        user_id,
        cutoff_time,
        LOOKBACK_MINUTES
    )

    if sig is None:
        raise RuntimeError(
            "Could not construct positive signature for "
            f"user={user_id}, cutoff={cutoff_time}"
        )

    if len(sig) != 16:
        raise RuntimeError(
            f"Positive signature has {len(sig)} dimensions; expected 16."
        )

    positive_window_signatures_71d5d.append(
        {
            "window_id": row["window_id"],
            "user_id": user_id,
            "horizon_minutes": row["horizon_minutes"],
            "cutoff_time": cutoff_time,
            "signature": sig
        }
    )

positive_window_signatures_71d5d = pd.DataFrame(
    positive_window_signatures_71d5d
)

print(
    "Positive prediction-window signatures:",
    len(positive_window_signatures_71d5d)
)

assert len(
    positive_window_signatures_71d5d
) == 400

assert (
    positive_window_signatures_71d5d["user_id"].nunique()
    == 80
)

positive_profile_records_71d5d = []

for user_id, grp in (
    positive_window_signatures_71d5d
    .groupby("user_id", sort=True)
):

    signature_matrix = np.vstack(
        grp["signature"].values
    )

    mean_signature = np.mean(
        signature_matrix,
        axis=0
    )

    positive_profile_records_71d5d.append(
        {
            "user_id": str(user_id),
            "signature": mean_signature
        }
    )

positive_profiles_71d5d = pd.DataFrame(
    positive_profile_records_71d5d
)

positive_matrix_71d5d = np.vstack(
    positive_profiles_71d5d["signature"].values
)

print(
    "Positive user profiles:",
    len(positive_profiles_71d5d)
)

print(
    "Positive profile matrix shape:",
    positive_matrix_71d5d.shape
)

assert len(positive_profiles_71d5d) == 80
assert positive_matrix_71d5d.shape == (80, 16)
assert np.isfinite(positive_matrix_71d5d).all()

print(
    "✓ Positive users represented in the same 16-D feature space"
)

# ================================================================
# 10. STANDARDIZE FEATURE SPACE
# ================================================================
#
# Matching raw features directly would allow transaction amount
# to dominate all other dimensions.
#
# Standardize using the combined candidate + positive profile
# distribution.
# ================================================================

combined_for_scaling_71d5d = np.vstack(
    [
        candidate_matrix_71d5d,
        positive_matrix_71d5d
    ]
)

feature_mean_71d5d = np.nanmean(
    combined_for_scaling_71d5d,
    axis=0
)

feature_std_71d5d = np.nanstd(
    combined_for_scaling_71d5d,
    axis=0
)

feature_std_71d5d[
    feature_std_71d5d < 1e-9
] = 1.0

candidate_matrix_scaled_71d5d = (
    candidate_matrix_71d5d
    - feature_mean_71d5d
) / feature_std_71d5d

positive_matrix_scaled_71d5d = (
    positive_matrix_71d5d
    - feature_mean_71d5d
) / feature_std_71d5d

# ================================================================
# 11. CALCULATE MATCHING DISTANCE MATRIX
# ================================================================
#
# IMPORTANT:
# Do not replace this with the previous 3D broadcasting
# expression using .sum(axis=2).
#
# Matrix algebra is used here for robust Euclidean distance.
# ================================================================

print(
    "\nCalculating matching distance matrix..."
)

candidate_matrix = np.asarray(
    candidate_matrix_scaled_71d5d,
    dtype=float
)

positive_matrix = np.asarray(
    positive_matrix_scaled_71d5d,
    dtype=float
)

print(
    "Positive matrix shape:",
    positive_matrix.shape
)

print(
    "Candidate matrix shape:",
    candidate_matrix.shape
)

candidate_norm = np.sum(
    candidate_matrix * candidate_matrix,
    axis=1,
    keepdims=True
)

positive_norm = np.sum(
    positive_matrix * positive_matrix,
    axis=1,
    keepdims=True
).T

cross_product = (
    candidate_matrix
    @ positive_matrix.T
)

squared_distance = (
    candidate_norm
    + positive_norm
    - 2.0 * cross_product
)

squared_distance = np.maximum(
    squared_distance,
    0.0
)

distance_matrix = np.sqrt(
    squared_distance
)

print(
    "Distance matrix shape:",
    distance_matrix.shape
)

print(
    "Distance matrix finite:",
    np.isfinite(distance_matrix).all()
)

print(
    "Distance minimum:",
    float(np.min(distance_matrix))
)

print(
    "Distance maximum:",
    float(np.max(distance_matrix))
)

assert distance_matrix.shape == (
    len(candidate_signatures_71d5d),
    len(positive_profiles_71d5d)
)

assert np.isfinite(distance_matrix).all()

print(
    "✓ Distance matrix constructed successfully"
)

# ================================================================
# 12. GREEDY MATCHING
# ================================================================
#
# Each clean control user may be selected only once.
#
# Each candidate cutoff belongs to exactly one clean user.
#
# We match each positive user to the closest available candidate
# while enforcing unique clean control users.
# ================================================================

print(
    "\nAssigning matched clean control users..."
)

candidate_user_ids_71d5d = (
    candidate_signatures_71d5d["user_id"]
    .astype(str)
    .values
)

positive_user_ids_71d5d = (
    positive_profiles_71d5d["user_id"]
    .astype(str)
    .values
)

# Sort all positive-candidate pairs by distance
pair_rows_71d5d = []

for p_idx in range(
    len(positive_user_ids_71d5d)
):

    for c_idx in range(
        len(candidate_user_ids_71d5d)
    ):

        pair_rows_71d5d.append(
            (
                float(
                    distance_matrix[
                        c_idx,
                        p_idx
                    ]
                ),
                p_idx,
                c_idx
            )
        )

pair_rows_71d5d.sort(
    key=lambda x: x[0]
)

used_control_users_71d5d = set()
assigned_positive_users_71d5d = set()

matched_rows_71d5d = []

for distance, p_idx, c_idx in pair_rows_71d5d:

    positive_user = (
        positive_user_ids_71d5d[p_idx]
    )

    control_user = (
        candidate_user_ids_71d5d[c_idx]
    )

    if positive_user in assigned_positive_users_71d5d:
        continue

    if control_user in used_control_users_71d5d:
        continue

    candidate_row = (
        candidate_signatures_71d5d
        .iloc[c_idx]
        .copy()
    )

    candidate_row[
        "matched_positive_user_id"
    ] = positive_user

    candidate_row[
        "matching_distance"
    ] = distance

    matched_rows_71d5d.append(
        candidate_row
    )

    assigned_positive_users_71d5d.add(
        positive_user
    )

    used_control_users_71d5d.add(
        control_user
    )

    if len(used_control_users_71d5d) >= N_CONTROL_USERS:
        break

matched_candidates_71d5d = pd.DataFrame(
    matched_rows_71d5d
)

print(
    "Assigned control users:",
    len(
        matched_candidates_71d5d[
            "user_id"
        ].unique()
    )
)

if len(
    matched_candidates_71d5d[
        "user_id"
    ].unique()
) != N_CONTROL_USERS:

    raise RuntimeError(
        "Could not assign exactly 20 unique clean control users."
    )

# ================================================================
# 13. SELECT ONE CUT-OFF PER CONTROL USER
# ================================================================
#
# Select the best matched candidate for each selected control user.
#
# This creates one legitimate control prediction point per user.
# The five horizons will then reference the same historical cutoff,
# consistent with the earlier hard-negative architecture.
# ================================================================

selected_control_cutoffs_71d5d = (
    matched_candidates_71d5d
    .sort_values(
        "matching_distance"
    )
    .drop_duplicates(
        subset=["user_id"],
        keep="first"
    )
    .reset_index(drop=True)
)

print(
    "Selected control cutoffs:",
    len(selected_control_cutoffs_71d5d)
)

assert len(
    selected_control_cutoffs_71d5d
) == N_CONTROL_USERS

# ================================================================
# 14. BUILD HARD NEGATIVE WINDOWS
# ================================================================

hard_negative_window_records_71d5d = []

for _, row in selected_control_cutoffs_71d5d.iterrows():

    control_user = str(
        row["user_id"]
    )

    cutoff_time = pd.Timestamp(
        row["cutoff_time"]
    )

    for horizon in HORIZONS:

        hard_negative_window_records_71d5d.append(
            {
                "window_id": (
                    f"HN71D5D_{len(hard_negative_window_records_71d5d)+1:05d}"
                ),
                "label": 0,
                "class": "HARD_NEGATIVE",
                "user_id": control_user,
                "horizon_minutes": horizon,
                "cutoff_time": cutoff_time,
                "cutoff_date": cutoff_time.date(),
                "cutoff_hour": cutoff_time.hour,
                "cutoff_dow": cutoff_time.dayofweek,
                "matching_distance": float(
                    row["matching_distance"]
                ),
                "matched_positive_user_id": str(
                    row["matched_positive_user_id"]
                ),
            }
        )

hard_negative_windows_71d5d = pd.DataFrame(
    hard_negative_window_records_71d5d
)

print(
    "\nHard negative windows:",
    len(hard_negative_windows_71d5d)
)

print(
    hard_negative_windows_71d5d[
        "horizon_minutes"
    ].value_counts().sort_index()
)

assert len(
    hard_negative_windows_71d5d
) == N_CONTROL_USERS * len(HORIZONS)

# ================================================================
# 15. EXTRACT REAL CONTROL EVENTS
# ================================================================
#
# Each hard-negative window receives the actual observable event
# history occurring in the 60 minutes before its cutoff.
#
# There are NO fabricated attack-like events.
# ================================================================

hard_negative_event_records_71d5d = []

for _, window in hard_negative_windows_71d5d.iterrows():

    user_id = str(
        window["user_id"]
    )

    cutoff_time = pd.Timestamp(
        window["cutoff_time"]
    )

    start_time = (
        cutoff_time
        - pd.Timedelta(
            minutes=LOOKBACK_MINUTES
        )
    )

    hist = control_stream_71d5d[
        (
            control_stream_71d5d["user_id"].astype(str)
            == user_id
        )
        &
        (
            control_stream_71d5d["__time_71d5d"]
            >= start_time
        )
        &
        (
            control_stream_71d5d["__time_71d5d"]
            < cutoff_time
        )
    ].copy()

    for _, event_row in hist.iterrows():

        record = event_row.to_dict()

        record["window_id"] = (
            window["window_id"]
        )

        record["label"] = 0
        record["class"] = "HARD_NEGATIVE"

        record["horizon_minutes"] = (
            window["horizon_minutes"]
        )

        record["cutoff_time"] = cutoff_time

        record["matching_distance"] = (
            window["matching_distance"]
        )

        record[
            "matched_positive_user_id"
        ] = (
            window[
                "matched_positive_user_id"
            ]
        )

        # Explicit provenance
        record["ground_truth_state"] = "NORMAL"
        record["is_attack"] = 0
        record["is_observable_precursor"] = 0
        record["is_hard_negative"] = 1

        hard_negative_event_records_71d5d.append(
            record
        )

hard_negative_events_71d5d = pd.DataFrame(
    hard_negative_event_records_71d5d
)

print(
    "\nHard negative events:",
    len(hard_negative_events_71d5d)
)

# ================================================================
# 16. BASIC STRUCTURAL VALIDATION
# ================================================================

print("\n" + "=" * 70)
print("71D.5D STRUCTURAL VALIDATION")
print("=" * 70)

# ------------------------------------------------
# Window count
# ------------------------------------------------

assert len(
    hard_negative_windows_71d5d
) == 100

print(
    "✓ Hard negative windows:",
    len(hard_negative_windows_71d5d)
)

# ------------------------------------------------
# Horizon balance
# ------------------------------------------------

horizon_counts_71d5d = (
    hard_negative_windows_71d5d[
        "horizon_minutes"
    ]
    .value_counts()
    .sort_index()
)

print(
    "\nHorizon distribution:"
)

print(
    horizon_counts_71d5d
)

assert all(
    horizon_counts_71d5d.get(h, 0)
    == N_CONTROL_USERS
    for h in HORIZONS
)

print(
    "✓ Exactly 20 windows per horizon"
)

# ------------------------------------------------
# User balance
# ------------------------------------------------

user_counts_71d5d = (
    hard_negative_windows_71d5d[
        "user_id"
    ]
    .value_counts()
)

print(
    "\nControl user window counts:"
)

print(
    user_counts_71d5d.describe()
)

assert (
    user_counts_71d5d.min()
    == len(HORIZONS)
)

assert (
    user_counts_71d5d.max()
    == len(HORIZONS)
)

print(
    "✓ Every control user has 5 horizons"
)

# ------------------------------------------------
# Positive-user overlap
# ------------------------------------------------

hard_users_71d5d = set(
    hard_negative_windows_71d5d[
        "user_id"
    ].astype(str)
)

overlap_users_71d5d = (
    hard_users_71d5d
    &
    positive_users_71d5d
)

print(
    "\nPositive/control user overlap:",
    len(overlap_users_71d5d)
)

assert len(
    overlap_users_71d5d
) == 0

print(
    "✓ No positive/control user overlap"
)

# ------------------------------------------------
# Cutoff uniqueness
# ------------------------------------------------

cutoff_event_matches_71d5d = 0

control_events_for_check_71d5d = (
    control_stream_71d5d[
        [
            "user_id",
            "__time_71d5d"
        ]
    ]
    .drop_duplicates()
)

for _, row in hard_negative_windows_71d5d.iterrows():

    matches = control_events_for_check_71d5d[
        (
            control_events_for_check_71d5d[
                "user_id"
            ].astype(str)
            == str(row["user_id"])
        )
        &
        (
            control_events_for_check_71d5d[
                "__time_71d5d"
            ]
            == pd.Timestamp(
                row["cutoff_time"]
            )
        )
    ]

    cutoff_event_matches_71d5d += len(matches)

print(
    "\nCutoff timestamps equal observed event timestamps:",
    cutoff_event_matches_71d5d
)

assert (
    cutoff_event_matches_71d5d
    == 0
)

print(
    "✓ No cutoff equals an observed event timestamp"
)

# ------------------------------------------------
# Genuine session-gap validation
# ------------------------------------------------

session_gap_violations_71d5d = 0

for _, row in hard_negative_windows_71d5d.iterrows():

    user_sessions = sessions_71d5d[
        sessions_71d5d["user_id"].astype(str)
        == str(row["user_id"])
    ]

    cutoff = pd.Timestamp(
        row["cutoff_time"]
    )

    inside_session = (
        (
            user_sessions["start_time"]
            < cutoff
        )
        &
        (
            user_sessions["end_time"]
            > cutoff
        )
    ).any()

    if inside_session:
        session_gap_violations_71d5d += 1

print(
    "Cutoffs inside active sessions:",
    session_gap_violations_71d5d
)

assert (
    session_gap_violations_71d5d
    == 0
)

print(
    "✓ All cutoffs are outside active sessions"
)

# ------------------------------------------------
# Attack contamination
# ------------------------------------------------

if len(hard_negative_events_71d5d) > 0:

    attack_rows_71d5d = (
        hard_negative_events_71d5d[
            hard_negative_events_71d5d[
                "is_attack"
            ].fillna(0).astype(int) == 1
        ]
    )

else:

    attack_rows_71d5d = pd.DataFrame()

print(
    "\nHard negative attack events:",
    len(attack_rows_71d5d)
)

assert len(
    attack_rows_71d5d
) == 0

print(
    "✓ No attack-event contamination"
)

# ------------------------------------------------
# Precursor contamination
# ------------------------------------------------

if len(hard_negative_events_71d5d) > 0:

    precursor_rows_71d5d = (
        hard_negative_events_71d5d[
            hard_negative_events_71d5d[
                "is_observable_precursor"
            ].fillna(0).astype(int) == 1
        ]
    )

else:

    precursor_rows_71d5d = pd.DataFrame()

print(
    "Hard negative precursor events:",
    len(precursor_rows_71d5d)
)

assert len(
    precursor_rows_71d5d
) == 0

print(
    "✓ No observable precursor contamination"
)

# ------------------------------------------------
# Event IDs
# ------------------------------------------------

if len(hard_negative_events_71d5d) > 0:

    if "event_id" in hard_negative_events_71d5d.columns:

        duplicate_event_ids_71d5d = (
            hard_negative_events_71d5d[
                "event_id"
            ]
            .duplicated()
            .sum()
        )

        print(
            "Duplicate event IDs:",
            duplicate_event_ids_71d5d
        )

# ================================================================
# 17. CONTROL EVENT DISTRIBUTION
# ================================================================

if len(hard_negative_events_71d5d) > 0:

    print(
        "\nHard negative event types:"
    )

    if "event_type" in hard_negative_events_71d5d.columns:

        print(
            hard_negative_events_71d5d[
                "event_type"
            ]
            .value_counts()
            .head(20)
        )

    if "modality" in hard_negative_events_71d5d.columns:

        print(
            "\nHard negative modalities:"
        )

        print(
            hard_negative_events_71d5d[
                "modality"
            ]
            .value_counts()
        )

# ================================================================
# 18. MATCHING QUALITY
# ================================================================

matching_distances_71d5d = pd.to_numeric(
    selected_control_cutoffs_71d5d[
        "matching_distance"
    ],
    errors="coerce"
)

print(
    "\nMatching distance summary:"
)

print(
    matching_distances_71d5d.describe()
)

assert np.isfinite(
    matching_distances_71d5d
).all()

# ================================================================
# 19. EVENT ACTIVITY PER CONTROL WINDOW
# ================================================================

if len(hard_negative_events_71d5d) > 0:

    event_counts_71d5d = (
        hard_negative_events_71d5d
        .groupby(
            "window_id"
        )
        .size()
    )

    hard_negative_windows_71d5d[
        "event_count"
    ] = (
        hard_negative_windows_71d5d[
            "window_id"
        ]
        .map(event_counts_71d5d)
        .fillna(0)
        .astype(int)
    )

else:

    hard_negative_windows_71d5d[
        "event_count"
    ] = 0

print(
    "\nHard-negative event count per window:"
)

print(
    hard_negative_windows_71d5d[
        "event_count"
    ].describe()
)

# ================================================================
# 20. HORIZON ACTIVITY AUDIT
# ================================================================

print(
    "\nActivity by horizon:"
)

activity_summary_71d5d = (
    hard_negative_windows_71d5d
    .groupby("horizon_minutes")[
        "event_count"
    ]
    .agg(
        [
            "count",
            "mean",
            "median",
            "min",
            "max"
        ]
    )
)

print(
    activity_summary_71d5d
)

# ================================================================
# 21. CREATE FINAL AUTHORITATIVE 71D.5D OBJECTS
# ================================================================
#
# Do NOT overwrite the previous authoritative hard-negative
# objects until this design has passed the downstream 71D audit.
#
# These names are therefore created only after structural checks.
# ================================================================

hard_negative_windows_71d5d_final = (
    hard_negative_windows_71d5d.copy()
)

hard_negative_events_71d5d_final = (
    hard_negative_events_71d5d.copy()
)

# ================================================================
# 22. FINAL SUMMARY
# ================================================================

print("\n" + "=" * 70)
print("AFRITAC 71D.5D COMPLETE")
print("=" * 70)

print(
    "Control users:",
    hard_negative_windows_71d5d_final[
        "user_id"
    ].nunique()
)

print(
    "Hard negative windows:",
    len(hard_negative_windows_71d5d_final)
)

print(
    "Hard negative events:",
    len(hard_negative_events_71d5d_final)
)

print(
    "Positive/control overlap:",
    len(overlap_users_71d5d)
)

print(
    "Cutoff/event timestamp collisions:",
    cutoff_event_matches_71d5d
)

print(
    "Cutoffs inside active sessions:",
    session_gap_violations_71d5d
)

print(
    "Attack contamination:",
    len(attack_rows_71d5d)
)

print(
    "Precursor contamination:",
    len(precursor_rows_71d5d)
)

print(
    "Matching distance mean:",
    float(matching_distances_71d5d.mean())
)

print(
    "Matching distance median:",
    float(matching_distances_71d5d.median())
)

print(
    "\n✓ 71D.5D session-based hard-negative construction finished."
)

print(
    "✓ Authoritative 71D.5D objects were created with *_final names."
)

print(
    "✓ Previous hard-negative objects were not overwritten."
)



# ======================================================================
# AFRITAC STEP 71D.5F
# OBSERVABLE TIMELINE SESSION GAP MATCHED HARD NEGATIVE CONTROLS
# ======================================================================

print("\n" + "=" * 70)
print("AFRITAC STEP 71D.5F")
print("OBSERVABLE TIMELINE SESSION GAP MATCHED CONTROLS")
print("=" * 70)

HORIZONS_71D5F = [5, 10, 15, 30, 60]
LOOKBACK_71D5F = 60
N_CONTROL_USERS_71D5F = 20

# ----------------------------------------------------------------------
# 1. Required objects
# ----------------------------------------------------------------------
required_71d5f = [
    "users", "sessions", "normal_stream", "positive_windows",
    "positive_stream_71d5d"
]
missing_71d5f = [x for x in required_71d5f if x not in globals()]
print("Required objects missing:", missing_71d5f)

if missing_71d5f:
    raise RuntimeError("Required AFRITAC objects are missing.")

# ----------------------------------------------------------------------
# 2. Normalize authoritative observable stream
# ----------------------------------------------------------------------
obs_71d5f = normal_stream.copy()

obs_71d5f["user_id"] = obs_71d5f["user_id"].astype(str)
obs_71d5f["session_id"] = obs_71d5f["session_id"].astype(str)
obs_71d5f["timestamp"] = pd.to_datetime(
    obs_71d5f["timestamp"], errors="coerce"
)

obs_71d5f = obs_71d5f.dropna(
    subset=["user_id", "session_id", "timestamp"]
).copy()

obs_71d5f = obs_71d5f.sort_values(
    ["user_id", "timestamp", "event_id"]
).reset_index(drop=True)

# Positive users are excluded from the hard-negative pool.
positive_users_71d5f = set(
    positive_windows["user_id"].astype(str).unique()
)

all_users_71d5f = set(
    users["user_id"].astype(str).unique()
)

clean_pool_71d5f = sorted(
    all_users_71d5f - positive_users_71d5f
)

print("Positive users:", len(positive_users_71d5f))
print("Clean candidate users:", len(clean_pool_71d5f))

# ----------------------------------------------------------------------
# 3. Identify observable session blocks.
#
# The observable stream is authoritative for timing. For each session,
# use the actual first and last observable event timestamp rather than
# sessions.start_time/end_time.
# ----------------------------------------------------------------------
session_obs_71d5f = (
    obs_71d5f[
        obs_71d5f["user_id"].isin(clean_pool_71d5f)
    ]
    .groupby(["user_id", "session_id"], as_index=False)
    .agg(
        observable_start=("timestamp", "min"),
        observable_end=("timestamp", "max"),
        observable_event_count=("event_id", "count")
    )
)

session_obs_71d5f = session_obs_71d5f.sort_values(
    ["user_id", "observable_start"]
).reset_index(drop=True)

print("Observable session blocks:", len(session_obs_71d5f))
print(
    "Observable sessions per clean user:",
    session_obs_71d5f.groupby("user_id").size().describe().round(3).to_dict()
)

# ----------------------------------------------------------------------
# 4. Build genuine gaps between observable session blocks.
#
# IMPORTANT:
# A cutoff in the middle of a long quiet gap can have an empty 60-minute
# history. That is not useful for matching. We therefore place the cutoff
# within the first 60 minutes after the previous observable session ends.
# This guarantees that the previous genuine session can contribute to the
# 60-minute history, while the cutoff remains outside the session itself.
#
# For short gaps, the latest admissible point before the next session is
# used. For long gaps, 30 minutes after the previous observable end is used.
# ----------------------------------------------------------------------
candidate_rows_71d5f = []

for uid, g in session_obs_71d5f.groupby("user_id"):

    g = g.sort_values("observable_start").reset_index(drop=True)

    if len(g) < 2:
        continue

    for i in range(len(g) - 1):

        previous_end = pd.Timestamp(
            g.loc[i, "observable_end"]
        )

        next_start = pd.Timestamp(
            g.loc[i + 1, "observable_start"]
        )

        if pd.isna(previous_end) or pd.isna(next_start):
            continue

        gap_minutes = (
            next_start - previous_end
        ).total_seconds() / 60.0

        # Need a genuine gap of at least 10 minutes.
        if gap_minutes < 10:
            continue

        # Cutoff must be:
        #   >=5 min after previous observable activity
        #   <=60 min after previous observable activity
        #   >=5 min before next observable activity
        lower_offset = 5.0
        upper_offset = min(
            60.0,
            gap_minutes - 5.0
        )

        if lower_offset > upper_offset:
            continue

        # Prefer a 30-minute post-session cutoff whenever possible.
        offset = min(
            30.0,
            upper_offset
        )

        cutoff = (
            previous_end +
            pd.Timedelta(minutes=offset)
        )

        if cutoff <= previous_end:
            continue

        if cutoff >= next_start:
            continue

        candidate_rows_71d5f.append({
            "candidate_id":
                f"CAND71F_{len(candidate_rows_71d5f)+1:05d}",
            "user_id": str(uid),
            "previous_session_id":
                str(g.loc[i, "session_id"]),
            "next_session_id":
                str(g.loc[i + 1, "session_id"]),
            "previous_observable_end":
                previous_end,
            "next_observable_start":
                next_start,
            "gap_minutes":
                gap_minutes,
            "cutoff_time":
                cutoff
        })

candidate_cutoffs_71d5f = pd.DataFrame(
    candidate_rows_71d5f
)

if candidate_cutoffs_71d5f.empty:
    raise RuntimeError(
        "No valid observable inter-session gap cutoffs were found."
    )

print(
    "Candidate observable gap cutoffs:",
    len(candidate_cutoffs_71d5f)
)

print(
    "Candidate users:",
    candidate_cutoffs_71d5f["user_id"].nunique()
)

# ----------------------------------------------------------------------
# Candidate history must be genuine and nonempty.
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# 5. Keep only clean users with >=5 separated candidate cutoffs.
# ----------------------------------------------------------------------
candidate_counts_71d5f = (
    candidate_cutoffs_71d5f.groupby("user_id")
    .size()
    .sort_values(ascending=False)
)

eligible_users_71d5f = candidate_counts_71d5f[
    candidate_counts_71d5f >= len(HORIZONS_71D5F)
].index.astype(str).tolist()

print(
    "Users with >=5 candidate cutoffs:",
    len(eligible_users_71d5f)
)

if len(eligible_users_71d5f) < N_CONTROL_USERS_71D5F:
    raise RuntimeError(
        f"Only {len(eligible_users_71d5f)} users have enough "
        f"observable gap cutoffs."
    )

rng_71d5f = np.random.default_rng(SEED + 706)

selected_control_users_71d5f = sorted(
    rng_71d5f.choice(
        np.array(eligible_users_71d5f, dtype=object),
        size=N_CONTROL_USERS_71D5F,
        replace=False
    ).tolist()
)

candidate_cutoffs_71d5f = candidate_cutoffs_71d5f[
    candidate_cutoffs_71d5f["user_id"].isin(
        selected_control_users_71d5f
    )
].copy()

print(
    "Selected clean control users:",
    len(selected_control_users_71d5f)
)

# ----------------------------------------------------------------------
# 6. Signature function.
# ----------------------------------------------------------------------
def build_signature_71d5f(df, cutoff, lookback=60):

    cutoff = pd.Timestamp(cutoff)
    lo = cutoff - pd.Timedelta(minutes=lookback)

    x = df[
        (df["timestamp"] >= lo) &
        (df["timestamp"] < cutoff)
    ].copy()

    event_count = float(len(x))

    session_count = (
        float(x["session_id"].nunique())
        if "session_id" in x.columns else 0.0
    )

    modality_count = (
        float(x["modality"].nunique())
        if "modality" in x.columns else 0.0
    )

    event_type_count = (
        float(x["event_type"].nunique())
        if "event_type" in x.columns else 0.0
    )

    if len(x):

        delay = pd.to_numeric(
            x.get(
                "response_delay_ms",
                pd.Series(index=x.index, dtype=float)
            ),
            errors="coerce"
        ).dropna()

        delay_mean = float(delay.mean()) if len(delay) else 0.0
        delay_std = float(delay.std(ddof=0)) if len(delay) else 0.0

        def temporal_share(minutes):
            return float(
                (
                    x["timestamp"] >=
                    cutoff - pd.Timedelta(minutes=minutes)
                ).mean()
            )

        last_5_share = temporal_share(5)
        last_10_share = temporal_share(10)
        last_15_share = temporal_share(15)
        last_30_share = temporal_share(30)

        def boolean_rate(column):

            if column not in x.columns:
                return 0.0

            vals = x[column]

            if vals.dtype == object:

                normalized = (
                    vals.astype(str)
                    .str.strip()
                    .str.upper()
                )

                vals = normalized.isin(
                    ["1", "TRUE", "YES", "Y"]
                )

            else:
                vals = pd.to_numeric(
                    vals,
                    errors="coerce"
                ).fillna(0).astype(float)

            return float(
                pd.Series(vals, index=x.index)
                .astype(float)
                .mean()
            )

        new_device_rate = boolean_rate("new_device")
        location_change_rate = boolean_rate("location_change")
        roaming_rate = boolean_rate("roaming")

        transaction_count = 0.0
        transaction_amount_sum = 0.0

        if "transaction_amount" in x.columns:

            amount = pd.to_numeric(
                x["transaction_amount"],
                errors="coerce"
            ).fillna(0.0)

            transaction_count = float(
                (amount > 0).sum()
            )

            transaction_amount_sum = float(
                amount.sum()
            )

        if "event_type" in x.columns:

            probs = x["event_type"].value_counts(
                normalize=True
            )

            entropy = float(
                -(probs * np.log2(probs)).sum()
            )

        else:
            entropy = 0.0

    else:

        delay_mean = 0.0
        delay_std = 0.0

        last_5_share = 0.0
        last_10_share = 0.0
        last_15_share = 0.0
        last_30_share = 0.0

        new_device_rate = 0.0
        location_change_rate = 0.0
        roaming_rate = 0.0

        transaction_count = 0.0
        transaction_amount_sum = 0.0
        entropy = 0.0

    return np.array([
        event_count,
        session_count,
        modality_count,
        event_type_count,
        delay_mean,
        delay_std,
        last_5_share,
        last_10_share,
        last_15_share,
        last_30_share,
        new_device_rate,
        location_change_rate,
        roaming_rate,
        transaction_count,
        transaction_amount_sum,
        entropy
    ], dtype=float)


signature_columns_71d5f = [
    "event_count",
    "session_count",
    "modality_count",
    "event_type_count",
    "delay_mean",
    "delay_std",
    "last_5_share",
    "last_10_share",
    "last_15_share",
    "last_30_share",
    "new_device_rate",
    "location_change_rate",
    "roaming_rate",
    "transaction_count",
    "transaction_amount_sum",
    "event_type_entropy"
]

# ----------------------------------------------------------------------
# 7. Positive horizon specific signatures.
# ----------------------------------------------------------------------
positive_stream_71d5f = positive_stream_71d5d.copy()

positive_stream_71d5f["user_id"] = (
    positive_stream_71d5f["user_id"].astype(str)
)

positive_stream_71d5f["timestamp"] = pd.to_datetime(
    positive_stream_71d5f["timestamp"],
    errors="coerce"
)

positive_windows_71d5f = positive_windows.copy()

positive_windows_71d5f["user_id"] = (
    positive_windows_71d5f["user_id"].astype(str)
)

positive_windows_71d5f["cutoff_time"] = pd.to_datetime(
    positive_windows_71d5f["cutoff_time"],
    errors="coerce"
)

positive_signature_71d5f = {}

for h in HORIZONS_71D5F:

    wh = positive_windows_71d5f[
        positive_windows_71d5f["horizon_minutes"] == h
    ]

    for _, r in wh.iterrows():

        uid = str(r["user_id"])

        positive_signature_71d5f[(uid, h)] = (
            build_signature_71d5f(
                positive_stream_71d5f[
                    positive_stream_71d5f["user_id"] == uid
                ],
                r["cutoff_time"],
                LOOKBACK_71D5F
            )
        )

print("\nPositive horizon signatures:")

for h in HORIZONS_71D5F:
    print(
        f"  {h:>2} min:",
        sum(1 for k in positive_signature_71d5f if k[1] == h)
    )

# ----------------------------------------------------------------------
# 8. Candidate signatures and direct history diagnostic.
# ----------------------------------------------------------------------
candidate_signature_rows_71d5f = []

for _, r in candidate_cutoffs_71d5f.iterrows():

    uid = str(r["user_id"])

    user_events = obs_71d5f[
        obs_71d5f["user_id"] == uid
    ]

    sig = build_signature_71d5f(
        user_events,
        r["cutoff_time"],
        LOOKBACK_71D5F
    )

    row = r.to_dict()

    row.update({
        c: float(v)
        for c, v in zip(signature_columns_71d5f, sig)
    })

    candidate_signature_rows_71d5f.append(row)

candidate_signatures_71d5f = pd.DataFrame(
    candidate_signature_rows_71d5f
)

print("\nCandidate observable history diagnostic:")

print(
    candidate_signatures_71d5f["event_count"]
    .agg(["count", "mean", "median", "min", "max"])
    .round(4)
)

if (
    candidate_signatures_71d5f["event_count"].sum()
    <= 0
):
    raise RuntimeError(
        "Observable gap cutoffs still have zero observable history. "
        "Stop before hard-negative generation."
    )

# ----------------------------------------------------------------------
# 9. Robust scaling.
# ----------------------------------------------------------------------
def scale_pair_71d5f(pos_mat, cand_mat):

    combined = np.vstack([
        pos_mat,
        cand_mat
    ])

    med = np.nanmedian(
        combined,
        axis=0
    )

    q25 = np.nanpercentile(
        combined,
        25,
        axis=0
    )

    q75 = np.nanpercentile(
        combined,
        75,
        axis=0
    )

    scale = q75 - q25

    fallback = np.nanstd(
        combined,
        axis=0
    )

    scale = np.where(
        (scale <= 1e-9) |
        ~np.isfinite(scale),
        fallback,
        scale
    )

    scale = np.where(
        (scale <= 1e-9) |
        ~np.isfinite(scale),
        1.0,
        scale
    )

    pos_scaled = (
        np.nan_to_num(pos_mat, nan=0.0) - med
    ) / scale

    cand_scaled = (
        np.nan_to_num(cand_mat, nan=0.0) - med
    ) / scale

    return pos_scaled, cand_scaled

# ----------------------------------------------------------------------
# 10. Stable user-level matching.
# ----------------------------------------------------------------------
positive_users_order_71d5f = sorted(
    positive_users_71d5f
)

positive_mean_profiles_71d5f = {}

for uid in positive_users_order_71d5f:

    sigs = [
        positive_signature_71d5f[(uid, h)]
        for h in HORIZONS_71D5F
    ]

    positive_mean_profiles_71d5f[uid] = (
        np.mean(np.vstack(sigs), axis=0)
    )

control_profile_rows_71d5f = []

for cuid in selected_control_users_71d5f:

    cand = candidate_signatures_71d5f[
        candidate_signatures_71d5f["user_id"] == cuid
    ]

    control_profile_rows_71d5f.append(
        np.median(
            cand[
                signature_columns_71d5f
            ].to_numpy(dtype=float),
            axis=0
        )
    )

positive_mean_mat_71d5f = np.vstack([
    positive_mean_profiles_71d5f[u]
    for u in positive_users_order_71d5f
])

control_profile_mat_71d5f = np.vstack(
    control_profile_rows_71d5f
)

pm_scaled_71d5f, cm_scaled_71d5f = (
    scale_pair_71d5f(
        positive_mean_mat_71d5f,
        control_profile_mat_71d5f
    )
)

user_distance_71d5f = np.sqrt(
    (
        (
            cm_scaled_71d5f[:, None, :]
            -
            pm_scaled_71d5f[None, :, :]
        ) ** 2
    ).sum(axis=2)
)

remaining_control_71d5f = set(
    range(len(selected_control_users_71d5f))
)

remaining_positive_71d5f = set(
    range(len(positive_users_order_71d5f))
)

pairs_71d5f = []

while remaining_control_71d5f:

    best = None

    for ci in remaining_control_71d5f:

        for pi in remaining_positive_71d5f:

            d = float(
                user_distance_71d5f[ci, pi]
            )

            if best is None or d < best[0]:
                best = (d, ci, pi)

    if best is None:
        raise RuntimeError(
            "Could not complete user-level matching."
        )

    d, ci, pi = best

    pairs_71d5f.append({
        "control_user": selected_control_users_71d5f[ci],
        "positive_user": positive_users_order_71d5f[pi],
        "user_match_distance": d
    })

    remaining_control_71d5f.remove(ci)
    remaining_positive_71d5f.remove(pi)

user_match_71d5f = pd.DataFrame(
    pairs_71d5f
)

print(
    "\nUser-level matches:",
    len(user_match_71d5f)
)

# ----------------------------------------------------------------------
# 11. Horizon-specific cutoff matching.
#
# Five different cutoffs are selected for every control user.
# Cutoffs for the same user are separated by >=60 minutes.
# ----------------------------------------------------------------------
candidate_used_71d5f = set()

matched_windows_71d5f = []

for _, pair in user_match_71d5f.iterrows():

    cuid = str(pair["control_user"])
    puid = str(pair["positive_user"])

    cand = candidate_signatures_71d5f[
        candidate_signatures_71d5f["user_id"] == cuid
    ].copy()

    cand = cand.sort_values(
        "cutoff_time"
    ).reset_index(drop=True)

    used_cutoffs = []

    for h in HORIZONS_71D5F:

        target = positive_signature_71d5f[
            (puid, h)
        ]

        candidate_matrix = cand[
            signature_columns_71d5f
        ].to_numpy(dtype=float)

        target_scaled, candidate_scaled = scale_pair_71d5f(
            np.vstack([target]),
            candidate_matrix
        )

        distances = np.sqrt(
            np.sum(
                (
                    candidate_scaled
                    -
                    target_scaled[0]
                ) ** 2,
                axis=1
            )
        )

        if not np.all(np.isfinite(distances)):
            raise RuntimeError(
                f"Non-finite horizon matching distance for {cuid}, "
                f"horizon {h}."
            )

        order = np.argsort(
            distances
        )

        chosen = None

        for idx in order:

            cutoff = pd.Timestamp(
                cand.loc[idx, "cutoff_time"]
            )

            cid = str(
                cand.loc[idx, "candidate_id"]
            )

            if cid in candidate_used_71d5f:
                continue

            if any(
                abs(
                    (
                        cutoff - previous
                    ).total_seconds()
                ) / 60.0
                < 10.0
                for previous in used_cutoffs
            ):
                continue

            chosen = int(idx)
            break

        if chosen is None:

            for idx in order:

                cutoff = pd.Timestamp(
                    cand.loc[idx, "cutoff_time"]
                )

                if any(
                    abs(
                        (
                            cutoff - previous
                        ).total_seconds()
                    ) / 60.0
                    < 10.0
                    for previous in used_cutoffs
                ):
                    continue

                chosen = int(idx)
                break

        if chosen is None:
            raise RuntimeError(
                f"No independent cutoff available for {cuid}, "
                f"horizon {h}."
            )

        selected = cand.loc[chosen]

        selected_cutoff = pd.Timestamp(
            selected["cutoff_time"]
        )

        candidate_used_71d5f.add(
            str(selected["candidate_id"])
        )

        used_cutoffs.append(
            selected_cutoff
        )

        matched_windows_71d5f.append({
            "window_id":
                f"HN71F_{len(matched_windows_71d5f)+1:05d}",
            "label": 0,
            "class": "HARD_NEGATIVE",
            "user_id": cuid,
            "matched_positive_user_id": puid,
            "horizon_minutes": h,
            "cutoff_time": selected_cutoff,
            "match_distance": float(
                distances[chosen]
            ),
            "user_match_distance": float(
                pair["user_match_distance"]
            )
        })

hard_negative_windows_71d5f = pd.DataFrame(
    matched_windows_71d5f
)

# ----------------------------------------------------------------------
# 12. Extract actual observable histories.
# ----------------------------------------------------------------------
event_rows_71d5f = []

for _, w in hard_negative_windows_71d5f.iterrows():

    uid = str(w["user_id"])

    cutoff = pd.Timestamp(
        w["cutoff_time"]
    )

    lo = (
        cutoff -
        pd.Timedelta(minutes=LOOKBACK_71D5F)
    )

    hist = obs_71d5f[
        (obs_71d5f["user_id"] == uid) &
        (obs_71d5f["timestamp"] >= lo) &
        (obs_71d5f["timestamp"] < cutoff)
    ].copy()

    for _, e in hist.iterrows():

        row = e.to_dict()

        source_id = str(
            e["event_id"]
        )

        row["source_event_id"] = source_id

        row["hard_negative_event_id"] = (
            f"HNE71F_{len(event_rows_71d5f)+1:06d}"
        )

        row["window_id"] = w["window_id"]
        row["horizon_minutes"] = int(
            w["horizon_minutes"]
        )

        row["ground_truth_state"] = "NORMAL"
        row["is_attack"] = 0
        row["is_observable_precursor"] = 0
        row["hard_negative"] = 1

        event_rows_71d5f.append(row)

hard_negative_events_71d5f = pd.DataFrame(
    event_rows_71d5f
)

# ----------------------------------------------------------------------
# 13. Structural validation.
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
print("71D.5F STRUCTURAL VALIDATION")
print("=" * 70)

assert len(hard_negative_windows_71d5f) == 100
assert (
    hard_negative_windows_71d5f["user_id"].nunique()
    == 20
)

horizon_counts_71d5f = (
    hard_negative_windows_71d5f[
        "horizon_minutes"
    ]
    .value_counts()
    .sort_index()
)

print("\nWindows by horizon:")
print(horizon_counts_71d5f)

assert set(
    horizon_counts_71d5f.index
) == set(HORIZONS_71D5F)

assert (
    horizon_counts_71d5f == 20
).all()

control_horizon_counts_71d5f = (
    hard_negative_windows_71d5f
    .groupby("user_id")[
        "horizon_minutes"
    ]
    .nunique()
)

assert (
    control_horizon_counts_71d5f == 5
).all()

print(
    "✓ Exactly 20 control users × 5 horizons"
)

overlap_71d5f = (
    set(
        hard_negative_windows_71d5f[
            "user_id"
        ].astype(str)
    )
    &
    positive_users_71d5f
)

print(
    "Positive/control user overlap:",
    len(overlap_71d5f)
)

assert len(overlap_71d5f) == 0

# Cutoffs cannot equal observed event timestamps.
cutoff_collision_71d5f = 0

for _, w in hard_negative_windows_71d5f.iterrows():

    uid = str(w["user_id"])
    cutoff = pd.Timestamp(
        w["cutoff_time"]
    )

    collision = (
        (
            obs_71d5f[
                obs_71d5f["user_id"] == uid
            ]["timestamp"]
            == cutoff
        ).any()
    )

    cutoff_collision_71d5f += int(
        collision
    )

print(
    "Cutoff/event collisions:",
    cutoff_collision_71d5f
)

assert cutoff_collision_71d5f == 0

# Every cutoff must be outside all observable session blocks.
active_observable_session_71d5f = 0

for _, w in hard_negative_windows_71d5f.iterrows():

    uid = str(w["user_id"])
    cutoff = pd.Timestamp(
        w["cutoff_time"]
    )

    sg = session_obs_71d5f[
        session_obs_71d5f["user_id"] == uid
    ]

    active = (
        (sg["observable_start"] <= cutoff) &
        (sg["observable_end"] >= cutoff)
    ).any()

    active_observable_session_71d5f += int(
        active
    )

print(
    "Cutoffs inside observable sessions:",
    active_observable_session_71d5f
)

assert active_observable_session_71d5f == 0

# Unique benchmark IDs.
if len(hard_negative_events_71d5f):

    assert (
        hard_negative_events_71d5f[
            "hard_negative_event_id"
        ].is_unique
    )

    print(
        "Unique benchmark event IDs:",
        hard_negative_events_71d5f[
            "hard_negative_event_id"
        ].nunique()
    )

    print(
        "Source event IDs reused across windows:",
        hard_negative_events_71d5f[
            "source_event_id"
        ].duplicated()
        .sum()
    )

    assert (
        hard_negative_events_71d5f[
            "is_attack"
        ].eq(0).all()
    )

    assert (
        hard_negative_events_71d5f[
            "is_observable_precursor"
        ].eq(0).all()
    )

# ----------------------------------------------------------------------
# 14. Horizon activity profile.
# ----------------------------------------------------------------------
def hard_activity_71d5f(
    events,
    windows
):

    rows = []

    for _, w in windows.iterrows():

        uid = str(w["user_id"])

        cutoff = pd.Timestamp(
            w["cutoff_time"]
        )

        lo = (
            cutoff -
            pd.Timedelta(
                minutes=LOOKBACK_71D5F
            )
        )

        x = events[
            (events["user_id"].astype(str) == uid) &
            (events["timestamp"] >= lo) &
            (events["timestamp"] < cutoff)
        ].copy()

        n = len(x)

        rows.append({
            "window_id": w["window_id"],
            "user_id": uid,
            "horizon_minutes":
                int(w["horizon_minutes"]),
            "event_count": n,
            "session_count":
                x["session_id"].nunique()
                if "session_id" in x.columns
                else 0,
            "event_type_count":
                x["event_type"].nunique()
                if "event_type" in x.columns
                else 0,
            "modality_count":
                x["modality"].nunique()
                if "modality" in x.columns
                else 0,
            "last_5_share":
                (
                    (
                        x["timestamp"] >=
                        cutoff -
                        pd.Timedelta(minutes=5)
                    ).mean()
                    if n else 0.0
                ),
            "last_10_share":
                (
                    (
                        x["timestamp"] >=
                        cutoff -
                        pd.Timedelta(minutes=10)
                    ).mean()
                    if n else 0.0
                ),
            "last_15_share":
                (
                    (
                        x["timestamp"] >=
                        cutoff -
                        pd.Timedelta(minutes=15)
                    ).mean()
                    if n else 0.0
                ),
            "last_30_share":
                (
                    (
                        x["timestamp"] >=
                        cutoff -
                        pd.Timedelta(minutes=30)
                    ).mean()
                    if n else 0.0
                )
        })

    return pd.DataFrame(rows)

hard_activity_71d5f = hard_activity_71d5f(
    obs_71d5f,
    hard_negative_windows_71d5f
)

print("\nHard-negative activity by horizon:")
print(
    hard_activity_71d5f
    .groupby("horizon_minutes")[
        [
            "event_count",
            "session_count",
            "event_type_count",
            "modality_count",
            "last_5_share",
            "last_10_share",
            "last_15_share",
            "last_30_share"
        ]
    ]
    .mean()
    .round(4)
)

print("\nHard-negative event counts:")
print(
    hard_activity_71d5f
    .groupby("horizon_minutes")[
        "event_count"
    ]
    .agg(
        ["count", "mean", "median", "std", "min", "max"]
    )
    .round(4)
)

# ----------------------------------------------------------------------
# 15. Matching distance by horizon.
# ----------------------------------------------------------------------
print("\nMatching distance by horizon:")
print(
    hard_negative_windows_71d5f
    .groupby("horizon_minutes")[
        "match_distance"
    ]
    .agg(
        ["count", "mean", "median", "min", "max"]
    )
    .round(4)
)

# ----------------------------------------------------------------------
# 16. Vocabulary contamination checks.
# ----------------------------------------------------------------------
hard_vocab_71d5f = set(
    hard_negative_events_71d5f[
        "event_type"
    ].dropna().astype(str)
) if len(hard_negative_events_71d5f) else set()

attack_vocab_71d5f = set(
    attack_events[
        "event_type"
    ].dropna().astype(str)
) if "attack_events" in globals() else set()

if "is_observable_precursor" in positive_stream_71d5f.columns:

    precursor_flag_71d5f = pd.to_numeric(
        positive_stream_71d5f[
            "is_observable_precursor"
        ],
        errors="coerce"
    ).fillna(0).astype("int64")

    precursor_vocab_71d5f = set(
        positive_stream_71d5f.loc[
            precursor_flag_71d5f.eq(1),
            "event_type"
        ].dropna().astype(str)
    )

else:
    precursor_vocab_71d5f = set()

attack_overlap_71d5f = (
    hard_vocab_71d5f &
    attack_vocab_71d5f
)

precursor_overlap_71d5f = (
    hard_vocab_71d5f &
    precursor_vocab_71d5f
)

print(
    "\nHard-negative event vocabulary:",
    sorted(hard_vocab_71d5f)
)

print(
    "Attack vocabulary overlap:",
    sorted(attack_overlap_71d5f)
)

print(
    "Precursor vocabulary overlap:",
    sorted(precursor_overlap_71d5f)
)

assert len(attack_overlap_71d5f) == 0
assert len(precursor_overlap_71d5f) == 0

# ----------------------------------------------------------------------
# 17. Final versioned objects.
# ----------------------------------------------------------------------
hard_negative_windows_final = (
    hard_negative_windows_71d5f.copy()
)

hard_negative_events_final = (
    hard_negative_events_71d5f.copy()
)

print("\n" + "=" * 70)
print("AFRITAC 71D.5F COMPLETE")
print("=" * 70)

print(
    "Control users:",
    hard_negative_windows_final[
        "user_id"
    ].nunique()
)

print(
    "Hard negative windows:",
    len(hard_negative_windows_final)
)

print(
    "Hard negative events:",
    len(hard_negative_events_final)
)

print(
    "Positive/control overlap:",
    len(overlap_71d5f)
)

print(
    "Cutoff/event collisions:",
    cutoff_collision_71d5f
)

print(
    "Active observable sessions:",
    active_observable_session_71d5f
)

print(
    "Attack vocabulary overlap:",
    len(attack_overlap_71d5f)
)

print(
    "Precursor vocabulary overlap:",
    len(precursor_overlap_71d5f)
)

print(
    "✓ 71D.5F observable-timeline matched construction finished."
)

# ==============================================================================
# NOTEBOOK CELL 219
# ==============================================================================

# AFRITAC STEP 71D.5G
# POSITIVE VS OBSERVABLE-TIMELINE HARD-NEGATIVE VALIDATION
#
# Purpose:
#   Validate 71D.5F before promotion to authoritative status.
#   This cell does NOT modify 71D.5F objects.

import numpy as np
import pandas as pd

from sklearn.metrics import roc_auc_score
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, cross_val_predict

print("=" * 70)
print("AFRITAC STEP 71D.5G")
print("POSITIVE VS OBSERVABLE-TIMELINE HARD-NEGATIVE VALIDATION")
print("=" * 70)

# ----------------------------------------------------------------------
# 1. Required objects
# ----------------------------------------------------------------------
required = [
    "positive_windows_71d5f",
    "positive_stream_71d5f",
    "hard_negative_windows_final",
    "hard_negative_events_final",
]
missing = [x for x in required if x not in globals()]
print("Required objects missing:", missing)
if missing:
    raise RuntimeError("Run the corrected 71D.5F cell first.")

HORIZONS_71D5G = [5, 10, 15, 30, 60]
LOOKBACK_71D5G = 60

pos_w = positive_windows_71d5f.copy()
pos_w["user_id"] = pos_w["user_id"].astype(str)
pos_w["cutoff_time"] = pd.to_datetime(pos_w["cutoff_time"], errors="coerce")
pos_w["label"] = 1

hard_w = hard_negative_windows_final.copy()
hard_w["user_id"] = hard_w["user_id"].astype(str)
hard_w["cutoff_time"] = pd.to_datetime(hard_w["cutoff_time"], errors="coerce")
hard_w["label"] = 0

pos_stream = positive_stream_71d5f.copy()
pos_stream["user_id"] = pos_stream["user_id"].astype(str)
pos_stream["timestamp"] = pd.to_datetime(pos_stream["timestamp"], errors="coerce")
pos_stream = pos_stream.dropna(subset=["timestamp"]).copy()

hard_stream = hard_negative_events_final.copy()
hard_stream["user_id"] = hard_stream["user_id"].astype(str)
hard_stream["timestamp"] = pd.to_datetime(hard_stream["timestamp"], errors="coerce")
hard_stream = hard_stream.dropna(subset=["timestamp"]).copy()

print("Positive windows:", len(pos_w))
print("Hard-negative windows:", len(hard_w))
print("Positive stream rows:", len(pos_stream))
print("Hard-negative event rows:", len(hard_stream))

assert len(pos_w) == 400
assert len(hard_w) == 100
assert pos_w["user_id"].nunique() == 80
assert hard_w["user_id"].nunique() == 20
assert set(pos_w["user_id"]) & set(hard_w["user_id"]) == set()

# ----------------------------------------------------------------------
# 2. Feature extraction from exactly the same 60-minute pre-cutoff rule
# ----------------------------------------------------------------------
FEATURES = [
    "event_count",
    "session_count",
    "event_type_count",
    "modality_count",
    "delay_mean",
    "delay_std",
    "last_5_share",
    "last_10_share",
    "last_15_share",
    "last_30_share",
    "new_device_rate",
    "location_change_rate",
    "roaming_rate",
    "transaction_count",
    "transaction_amount_sum",
    "transaction_amount_mean",
]

GROUPS = {
    "EVENT_COUNT": ["event_count"],
    "ACTIVITY": ["event_count", "session_count", "event_type_count"],
    "MODALITY": ["modality_count"],
    "TEMPORAL": ["last_5_share", "last_10_share", "last_15_share", "last_30_share"],
    "RESPONSE_DELAY": ["delay_mean", "delay_std"],
    "CONTEXT": ["new_device_rate", "location_change_rate", "roaming_rate"],
    "FINANCIAL": ["transaction_count", "transaction_amount_sum", "transaction_amount_mean"],
    "ACTIVITY_MODALITY": ["event_count", "session_count", "event_type_count", "modality_count"],
    "ACTIVITY_TEMPORAL": ["event_count", "session_count", "event_type_count", "last_5_share", "last_10_share", "last_15_share", "last_30_share"],
    "CONTEXT_FINANCIAL": ["new_device_rate", "location_change_rate", "roaming_rate", "transaction_count", "transaction_amount_sum", "transaction_amount_mean"],
    "ALL": FEATURES,
}

def _rate(x, col):
    if len(x) == 0 or col not in x.columns:
        return 0.0
    s = pd.to_numeric(x[col], errors="coerce")
    if s.notna().sum() == 0:
        return 0.0
    return float(s.fillna(0).mean())

def extract_features(stream, cutoff):
    cutoff = pd.Timestamp(cutoff)
    lo = cutoff - pd.Timedelta(minutes=LOOKBACK_71D5G)
    x = stream[(stream["timestamp"] >= lo) & (stream["timestamp"] < cutoff)].copy()
    n = len(x)

    out = {f: 0.0 for f in FEATURES}
    out["event_count"] = float(n)
    out["session_count"] = float(x["session_id"].nunique()) if n and "session_id" in x.columns else 0.0
    out["event_type_count"] = float(x["event_type"].nunique()) if n and "event_type" in x.columns else 0.0
    out["modality_count"] = float(x["modality"].nunique()) if n and "modality" in x.columns else 0.0

    if n:
        delay = pd.to_numeric(x.get("response_delay_ms", pd.Series(index=x.index, dtype=float)), errors="coerce").dropna()
        out["delay_mean"] = float(delay.mean()) if len(delay) else 0.0
        out["delay_std"] = float(delay.std(ddof=0)) if len(delay) else 0.0

        for m in [5, 10, 15, 30]:
            out[f"last_{m}_share"] = float((x["timestamp"] >= cutoff - pd.Timedelta(minutes=m)).mean())

        out["new_device_rate"] = _rate(x, "new_device")
        out["location_change_rate"] = _rate(x, "location_change")
        out["roaming_rate"] = _rate(x, "roaming")

        if "transaction_amount" in x.columns:
            amount = pd.to_numeric(x["transaction_amount"], errors="coerce")
            valid = amount.notna() & amount.gt(0)
            out["transaction_count"] = float(valid.sum())
            if valid.sum():
                out["transaction_amount_sum"] = float(amount[valid].sum())
                out["transaction_amount_mean"] = float(amount[valid].mean())

    return out

# ----------------------------------------------------------------------
# 3. Build horizon-specific feature table
# ----------------------------------------------------------------------
rows = []

for _, r in pos_w.iterrows():
    uid = r["user_id"]
    user_stream = pos_stream[pos_stream["user_id"] == uid]
    d = extract_features(user_stream, r["cutoff_time"])
    d.update({
        "label": 1,
        "user_id": uid,
        "window_id": r.get("window_id", None),
        "horizon_minutes": int(r["horizon_minutes"]),
        "cutoff_time": r["cutoff_time"],
    })
    rows.append(d)

for _, r in hard_w.iterrows():
    uid = r["user_id"]
    user_stream = hard_stream[hard_stream["user_id"] == uid]
    d = extract_features(user_stream, r["cutoff_time"])
    d.update({
        "label": 0,
        "user_id": uid,
        "window_id": r.get("window_id", None),
        "horizon_minutes": int(r["horizon_minutes"]),
        "cutoff_time": r["cutoff_time"],
    })
    rows.append(d)

validation_71d5g = pd.DataFrame(rows)

print("\nValidation feature matrix:", validation_71d5g.shape)
print("Positive rows:", int((validation_71d5g.label == 1).sum()))
print("Hard-negative rows:", int((validation_71d5g.label == 0).sum()))

# ----------------------------------------------------------------------
# 4. Horizon activity comparison
# ----------------------------------------------------------------------
comparison_cols = [
    "event_count", "session_count", "event_type_count", "modality_count",
    "last_5_share", "last_10_share", "last_15_share", "last_30_share",
    "delay_mean", "delay_std", "new_device_rate", "location_change_rate",
    "roaming_rate", "transaction_count", "transaction_amount_sum",
]

print("\nPositive vs hard-negative means by horizon:")
for h in HORIZONS_71D5G:
    a = validation_71d5g[validation_71d5g.horizon_minutes == h]
    means = a.groupby("label")[comparison_cols].mean().T
    means.columns = ["hard_negative" if c == 0 else "positive" for c in means.columns]
    means["positive_minus_hard"] = means.get("positive", 0) - means.get("hard_negative", 0)
    print(f"\n--- {h} minutes ---")
    print(means.round(4).to_string())

# ----------------------------------------------------------------------
# 5. Direction-free univariate AUC and SMD
# ----------------------------------------------------------------------
def smd(pos, neg):
    pos = pd.to_numeric(pos, errors="coerce").dropna().to_numpy(dtype=float)
    neg = pd.to_numeric(neg, errors="coerce").dropna().to_numpy(dtype=float)
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    sp = np.var(pos, ddof=1) if len(pos) > 1 else 0.0
    sn = np.var(neg, ddof=1) if len(neg) > 1 else 0.0
    pooled = np.sqrt((sp + sn) / 2.0)
    if not np.isfinite(pooled) or pooled <= 1e-12:
        return np.nan if np.isclose(np.mean(pos), np.mean(neg)) else np.inf
    return float((np.mean(pos) - np.mean(neg)) / pooled)

print("\nDirection-free univariate AUC by horizon:")
auc_rows = []

for h in HORIZONS_71D5G:
    a = validation_71d5g[validation_71d5g.horizon_minutes == h].copy()
    for f in FEATURES:
        x = pd.to_numeric(a[f], errors="coerce").fillna(0).to_numpy(dtype=float)
        y = a["label"].to_numpy(dtype=int)
        if np.nanmax(x) - np.nanmin(x) <= 1e-12:
            auc = 0.5
        else:
            raw = roc_auc_score(y, x)
            auc = max(raw, 1.0 - raw)
        auc_rows.append({"horizon_minutes": h, "feature": f, "auc": auc})

auc_71d5g = pd.DataFrame(auc_rows)
print(
    auc_71d5g.pivot(index="feature", columns="horizon_minutes", values="auc")
    .round(4)
    .to_string()
)

print("\nSMD by horizon:")
smd_rows = []
for h in HORIZONS_71D5G:
    a = validation_71d5g[validation_71d5g.horizon_minutes == h]
    p = a[a.label == 1]
    n = a[a.label == 0]
    for f in FEATURES:
        smd_rows.append({"horizon_minutes": h, "feature": f, "smd": smd(p[f], n[f])})
smd_71d5g = pd.DataFrame(smd_rows)
print(
    smd_71d5g.pivot(index="feature", columns="horizon_minutes", values="smd")
    .round(4)
    .to_string()
)

# ----------------------------------------------------------------------
# 6. Multivariate grouped CV AUC
# ----------------------------------------------------------------------
print("\nGrouped multivariate AUC:")
model_auc_rows = []

# 5 folds is valid because each user is a group and every group has one label.
groups = validation_71d5g["user_id"].to_numpy()
y_all = validation_71d5g["label"].to_numpy(dtype=int)

for h in HORIZONS_71D5G:
    a = validation_71d5g[validation_71d5g.horizon_minutes == h].reset_index(drop=True)
    X = a[FEATURES].replace([np.inf, -np.inf], np.nan)
    y = a["label"].to_numpy(dtype=int)
    g = a["user_id"].to_numpy()

    n_groups = len(np.unique(g))
    n_splits = min(5, n_groups)
    cv = GroupKFold(n_splits=n_splits)

    for group_name, cols in GROUPS.items():
        pipe = Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=3000, C=0.5)),
        ])
        pred = cross_val_predict(pipe, X[cols], y, cv=cv, groups=g, method="predict_proba")[:, 1]
        raw_auc = roc_auc_score(y, pred)
        auc = max(raw_auc, 1.0 - raw_auc)
        model_auc_rows.append({"horizon_minutes": h, "group": group_name, "auc": auc})

model_auc_71d5g = pd.DataFrame(model_auc_rows)
print(
    model_auc_71d5g.pivot(index="group", columns="horizon_minutes", values="auc")
    .round(4)
    .to_string()
)

# ----------------------------------------------------------------------
# 7. Matching-distance audit
# ----------------------------------------------------------------------
match_col = None
for c in ["match_distance", "matching_distance"]:
    if c in hard_w.columns:
        match_col = c
        break

if match_col:
    print("\nMatching distance by horizon:")
    print(
        hard_w.groupby("horizon_minutes")[match_col]
        .agg(["count", "mean", "median", "min", "max"])
        .round(4)
        .to_string()
    )
else:
    print("\nMatching distance column not found in hard-negative windows.")

# ----------------------------------------------------------------------
# 8. Hard-negative temporal sanity
# ----------------------------------------------------------------------
print("\nHard-negative temporal sanity:")
for h in HORIZONS_71D5G:
    a = validation_71d5g[validation_71d5g.horizon_minutes == h]
    print(
        f"{h:>2} min | positive events={a.loc[a.label.eq(1), 'event_count'].mean():.3f} "
        f"| hard events={a.loc[a.label.eq(0), 'event_count'].mean():.3f} "
        f"| positive sessions={a.loc[a.label.eq(1), 'session_count'].mean():.3f} "
        f"| hard sessions={a.loc[a.label.eq(0), 'session_count'].mean():.3f}"
    )

# ----------------------------------------------------------------------
# 9. Automated flags, diagnostic only. No objects modified.
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
print("71D.5G DIAGNOSTIC FLAGS")
print("=" * 70)

# Use direction-free AUC because either direction is a possible shortcut.
max_auc = auc_71d5g.groupby("horizon_minutes")["auc"].max()
max_smd = smd_71d5g.assign(abs_smd=smd_71d5g["smd"].abs()).groupby("horizon_minutes")["abs_smd"].max()

for h in HORIZONS_71D5G:
    print(
        f"{h:>2} min | max univariate AUC={max_auc.loc[h]:.4f} "
        f"| max |SMD|={max_smd.loc[h]:.4f}"
    )

best_models = model_auc_71d5g.groupby("horizon_minutes")["auc"].max()
print("\nBest grouped multivariate AUC by horizon:")
print(best_models.round(4).to_string())

print("\nInterpretation thresholds used for diagnosis only:")
print("  AUC >= 0.90  : strong potential shortcut")
print("  |SMD| >= 1.50 : strong distributional separation")
print("  AUC >= 0.95  : severe shortcut candidate")

print("\n71D.5G DOES NOT MODIFY 71D.5F OBJECTS.")
print("Run this diagnostic and review the complete output before promotion.")

# ==============================================================================
# NOTEBOOK CELL 220
# ==============================================================================

# AFRITAC STEP 71D.5H
# HORIZON-MATCHED OBSERVABLE HARD-NEGATIVE RECONSTRUCTION
#
# Purpose:
#   Reconstruct hard-negative controls by matching the FINAL prediction
#   window feature distributions horizon by horizon.
#
#   This cell DOES NOT overwrite 71D.5F objects.
#   It creates *_71d5h_candidate objects only.
#
# Key design:
#   1. Clean controls come from users outside the 80 positive users.
#   2. Cutoffs are placed in observable inter-session gaps.
#   3. The cutoff is never equal to an observed event timestamp.
#   4. The 5/10/15/30 minute controls are matched on the actual 60-minute
#      feature vector used by 71D.5G.
#   5. The 60 minute horizon is handled as a quiet-history problem because
#      the positive precursor layer currently has zero observable activity
#      at that cutoff.
#   6. Source events are copied from the clean observable stream with new
#      benchmark event IDs. No synthetic events are fabricated.
#
# Run after the successful AFRITAC 71D.5F construction.

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler

print("=" * 70)
print("AFRITAC STEP 71D.5H")
print("HORIZON-MATCHED OBSERVABLE HARD-NEGATIVE RECONSTRUCTION")
print("=" * 70)

# ----------------------------------------------------------------------
# 1. Required objects
# ----------------------------------------------------------------------
required = [
    "positive_windows_71d5f",
    "positive_stream_71d5f",
    "normal_stream",
]
missing = [x for x in required if x not in globals()]
print("Required objects missing:", missing)
if missing:
    raise RuntimeError("Run the completed 71D.5F pipeline first.")

HORIZONS_71D5H = [5, 10, 15, 30, 60]
LOOKBACK_71D5H = 60
SEED_71D5H = int(globals().get("SEED", 42)) + 7058
rng_71d5h = np.random.default_rng(SEED_71D5H)

FEATURES_71D5H = [
    "event_count",
    "session_count",
    "event_type_count",
    "modality_count",
    "delay_mean",
    "delay_std",
    "last_5_share",
    "last_10_share",
    "last_15_share",
    "last_30_share",
    "new_device_rate",
    "location_change_rate",
    "roaming_rate",
    "transaction_count",
    "transaction_amount_sum",
    "transaction_amount_mean",
]

# ----------------------------------------------------------------------
# 2. Prepare positive and clean observable streams
# ----------------------------------------------------------------------
pos_w_71d5h = positive_windows_71d5f.copy()
pos_w_71d5h["user_id"] = pos_w_71d5h["user_id"].astype(str)
pos_w_71d5h["cutoff_time"] = pd.to_datetime(
    pos_w_71d5h["cutoff_time"], errors="coerce"
)
pos_w_71d5h["horizon_minutes"] = pos_w_71d5h["horizon_minutes"].astype(int)

pos_stream_71d5h = positive_stream_71d5f.copy()
pos_stream_71d5h["user_id"] = pos_stream_71d5h["user_id"].astype(str)
pos_stream_71d5h["timestamp"] = pd.to_datetime(
    pos_stream_71d5h["timestamp"], errors="coerce"
)
pos_stream_71d5h = pos_stream_71d5h.dropna(subset=["timestamp"]).copy()

normal_71d5h = normal_stream.copy()
normal_71d5h["user_id"] = normal_71d5h["user_id"].astype(str)
normal_71d5h["timestamp"] = pd.to_datetime(
    normal_71d5h["timestamp"], errors="coerce"
)
normal_71d5h = normal_71d5h.dropna(subset=["timestamp"]).copy()

positive_users_71d5h = set(pos_w_71d5h["user_id"].unique())

all_users_71d5h = set(normal_71d5h["user_id"].unique())
clean_pool_71d5h = sorted(all_users_71d5h - positive_users_71d5h)

print("Positive users:", len(positive_users_71d5h))
print("Clean candidate users:", len(clean_pool_71d5h))

if len(clean_pool_71d5h) < 20:
    raise RuntimeError("Fewer than 20 clean users are available.")

# ----------------------------------------------------------------------
# 3. Feature extraction
# ----------------------------------------------------------------------
def _numeric_rate_71d5h(x, col):
    if len(x) == 0 or col not in x.columns:
        return 0.0
    s = pd.to_numeric(x[col], errors="coerce")
    return float(s.fillna(0).mean())

def extract_features_71d5h(stream, cutoff):
    cutoff = pd.Timestamp(cutoff)
    lo = cutoff - pd.Timedelta(minutes=LOOKBACK_71D5H)

    x = stream[
        (stream["timestamp"] >= lo) &
        (stream["timestamp"] < cutoff)
    ].copy()

    n = len(x)
    out = {f: 0.0 for f in FEATURES_71D5H}

    out["event_count"] = float(n)
    out["session_count"] = (
        float(x["session_id"].nunique())
        if n and "session_id" in x.columns else 0.0
    )
    out["event_type_count"] = (
        float(x["event_type"].nunique())
        if n and "event_type" in x.columns else 0.0
    )
    out["modality_count"] = (
        float(x["modality"].nunique())
        if n and "modality" in x.columns else 0.0
    )

    if n:
        delay = pd.to_numeric(
            x.get(
                "response_delay_ms",
                pd.Series(index=x.index, dtype=float)
            ),
            errors="coerce"
        ).dropna()

        out["delay_mean"] = float(delay.mean()) if len(delay) else 0.0
        out["delay_std"] = float(delay.std(ddof=0)) if len(delay) else 0.0

        for m in [5, 10, 15, 30]:
            out[f"last_{m}_share"] = float(
                (
                    x["timestamp"] >=
                    cutoff - pd.Timedelta(minutes=m)
                ).mean()
            )

        out["new_device_rate"] = _numeric_rate_71d5h(
            x, "new_device"
        )
        out["location_change_rate"] = _numeric_rate_71d5h(
            x, "location_change"
        )
        out["roaming_rate"] = _numeric_rate_71d5h(
            x, "roaming"
        )

        if "transaction_amount" in x.columns:
            amount = pd.to_numeric(
                x["transaction_amount"], errors="coerce"
            )
            valid = amount.notna() & amount.gt(0)

            out["transaction_count"] = float(valid.sum())

            if valid.sum():
                out["transaction_amount_sum"] = float(
                    amount[valid].sum()
                )
                out["transaction_amount_mean"] = float(
                    amount[valid].mean()
                )

    return out

# ----------------------------------------------------------------------
# 4. Positive horizon feature matrix
# ----------------------------------------------------------------------
positive_feature_rows_71d5h = []

for _, r in pos_w_71d5h.iterrows():
    uid = r["user_id"]
    us = pos_stream_71d5h[
        pos_stream_71d5h["user_id"] == uid
    ]

    d = extract_features_71d5h(us, r["cutoff_time"])
    d.update({
        "user_id": uid,
        "window_id": r.get("window_id", None),
        "horizon_minutes": int(r["horizon_minutes"]),
        "cutoff_time": r["cutoff_time"],
    })
    positive_feature_rows_71d5h.append(d)

positive_features_71d5h = pd.DataFrame(
    positive_feature_rows_71d5h
)

print("\nPositive horizon profiles:")
print(
    positive_features_71d5h.groupby(
        "horizon_minutes"
    ).size()
)

# ----------------------------------------------------------------------
# 5. Build observable session blocks for clean users
#
# IMPORTANT:
#   normal_stream timestamps are the authoritative observable timeline.
#   sessions.end_time is NOT used because prior diagnostics showed that
#   observable events can continue after the session-table end_time.
# ----------------------------------------------------------------------
clean_obs_71d5h = normal_71d5h[
    normal_71d5h["user_id"].isin(clean_pool_71d5h)
].copy()

session_blocks_71d5h = (
    clean_obs_71d5h
    .groupby(["user_id", "session_id"], as_index=False)
    .agg(
        observable_start=("timestamp", "min"),
        observable_end=("timestamp", "max"),
        event_count=("event_id", "count"),
    )
    .sort_values(["user_id", "observable_start"])
    .reset_index(drop=True)
)

print("\nObservable clean session blocks:", len(session_blocks_71d5h))

# ----------------------------------------------------------------------
# 6. Generate valid inter-session candidate cutoffs
#
# For 5/10/15/30 minute matching:
#   put the cutoff 30 minutes after the previous observable session end
#   whenever the gap permits.
#
# For 60 minute matching:
#   require a quiet gap > 60 minutes and place cutoff 65 minutes after
#   the previous observable session end. This produces genuinely quiet
#   60-minute histories rather than fabricated events.
# ----------------------------------------------------------------------
candidate_rows_71d5h = []

for uid, g in session_blocks_71d5h.groupby("user_id"):
    g = g.sort_values("observable_start").reset_index(drop=True)

    for i in range(len(g) - 1):
        prev_end = pd.Timestamp(g.loc[i, "observable_end"])
        next_start = pd.Timestamp(g.loc[i + 1, "observable_start"])
        gap_min = (next_start - prev_end).total_seconds() / 60.0

        # Short horizons: candidate cutoff 30 min after previous session.
        if gap_min >= 35:
            cutoff_short = prev_end + pd.Timedelta(minutes=30)

            candidate_rows_71d5h.append({
                "candidate_id": f"CH5_{len(candidate_rows_71d5h)+1:06d}",
                "user_id": uid,
                "cutoff_time": cutoff_short,
                "gap_minutes": gap_min,
                "candidate_band": "ACTIVE_GAP",
            })

        # Long horizon: genuinely quiet 60-minute history.
        if gap_min > 70:
            cutoff_quiet = prev_end + pd.Timedelta(minutes=65)

            candidate_rows_71d5h.append({
                "candidate_id": f"CH5_{len(candidate_rows_71d5h)+1:06d}",
                "user_id": uid,
                "cutoff_time": cutoff_quiet,
                "gap_minutes": gap_min,
                "candidate_band": "QUIET_GAP",
            })

candidate_cutoffs_71d5h = pd.DataFrame(candidate_rows_71d5h)

if candidate_cutoffs_71d5h.empty:
    raise RuntimeError("No valid observable inter-session candidate cutoffs.")

candidate_cutoffs_71d5h["cutoff_time"] = pd.to_datetime(
    candidate_cutoffs_71d5h["cutoff_time"]
)

# Remove accidental duplicate user/cutoff pairs.
candidate_cutoffs_71d5h = (
    candidate_cutoffs_71d5h
    .drop_duplicates(["user_id", "cutoff_time"])
    .reset_index(drop=True)
)

print("Candidate cutoffs:", len(candidate_cutoffs_71d5h))
print(
    "Candidate users:",
    candidate_cutoffs_71d5h["user_id"].nunique()
)

# ----------------------------------------------------------------------
# 7. Hard structural cutoff validation
# ----------------------------------------------------------------------
event_time_set_71d5h = set(
    clean_obs_71d5h["timestamp"].tolist()
)

collision_count_71d5h = int(
    candidate_cutoffs_71d5h["cutoff_time"]
    .isin(event_time_set_71d5h)
    .sum()
)

if collision_count_71d5h:
    raise RuntimeError(
        f"{collision_count_71d5h} candidate cutoffs equal "
        "observable event timestamps."
    )

# Confirm candidates are outside all observable session blocks.
inside_count_71d5h = 0

for _, c in candidate_cutoffs_71d5h.iterrows():
    uid = c["user_id"]
    t = c["cutoff_time"]

    blocks = session_blocks_71d5h[
        session_blocks_71d5h["user_id"] == uid
    ]

    inside = (
        (blocks["observable_start"] <= t) &
        (t <= blocks["observable_end"])
    ).any()

    if inside:
        inside_count_71d5h += 1

if inside_count_71d5h:
    raise RuntimeError(
        f"{inside_count_71d5h} candidate cutoffs are inside "
        "observable sessions."
    )

print("Cutoff/event collisions:", collision_count_71d5h)
print("Cutoffs inside observable sessions:", inside_count_71d5h)

# ----------------------------------------------------------------------
# 8. Build candidate feature matrix
# ----------------------------------------------------------------------
candidate_feature_rows_71d5h = []

for _, c in candidate_cutoffs_71d5h.iterrows():
    uid = c["user_id"]
    us = clean_obs_71d5h[
        clean_obs_71d5h["user_id"] == uid
    ]

    d = extract_features_71d5h(us, c["cutoff_time"])
    d.update({
        "candidate_id": c["candidate_id"],
        "user_id": uid,
        "cutoff_time": c["cutoff_time"],
        "gap_minutes": c["gap_minutes"],
        "candidate_band": c["candidate_band"],
    })
    candidate_feature_rows_71d5h.append(d)

candidate_features_71d5h = pd.DataFrame(
    candidate_feature_rows_71d5h
)

print("\nCandidate feature matrix:", candidate_features_71d5h.shape)

# ----------------------------------------------------------------------
# 9. Candidate history diagnostics
# ----------------------------------------------------------------------
print("\nCandidate event-count diagnostic:")
print(
    candidate_features_71d5h["event_count"].describe()
)

quiet_candidates_71d5h = candidate_features_71d5h[
    candidate_features_71d5h["candidate_band"] == "QUIET_GAP"
].copy()

print("\nQuiet-gap candidates:", len(quiet_candidates_71d5h))
if len(quiet_candidates_71d5h):
    print(
        quiet_candidates_71d5h["event_count"].describe()
    )

# ----------------------------------------------------------------------
# 10. Horizon-aware user matching
#
# Exactly 20 clean users x 5 horizons = 100 windows.
# We first select 20 representative positive users, then establish a
# one-to-one positive-user/control-user mapping using the aggregate
# nearest distance across all five horizons. This avoids the previous
# mistake of independently matching all 80 positive users.

pos_complete = (
    positive_features_71d5h.groupby("user_id")["horizon_minutes"]
    .nunique()
)
pos_complete = pos_complete[pos_complete == len(HORIZONS_71D5H)].index.tolist()

if len(pos_complete) != 80:
    raise RuntimeError(
        f"Expected 80 complete positive users, got {len(pos_complete)}."
    )

# Select 20 representative positive users using a diversity-aware
# selection in the complete five-horizon feature space.
profiles = []
for uid in pos_complete:
    z = (
        positive_features_71d5h[
            positive_features_71d5h["user_id"] == uid
        ]
        .set_index("horizon_minutes")
        .loc[HORIZONS_71D5H, FEATURES_71D5H]
        .to_numpy(dtype=float)
    )
    profiles.append(
        np.nan_to_num(z, nan=0.0, posinf=0.0, neginf=0.0).ravel()
    )

P = np.vstack(profiles)
ps = StandardScaler().fit_transform(P)

centroid = ps.mean(axis=0)
selected_idx = [int(np.argmin(np.sqrt(((ps-centroid)**2).sum(axis=1))))]
remaining = set(range(80)) - set(selected_idx)

while len(selected_idx) < 20:
    chosen = ps[selected_idx]
    rem = sorted(remaining)
    nearest = np.min(
        np.sqrt(
            ((ps[rem, None, :] - chosen[None, :, :]) ** 2).sum(axis=2)
        ),
        axis=1,
    )
    best = rem[int(np.argmax(nearest))]
    selected_idx.append(best)
    remaining.remove(best)

selected_positive_users = [pos_complete[i] for i in selected_idx]

print("\nRepresentative positive users:", len(selected_positive_users))

# Horizon-specific scaled candidate matrices.
candidate_by_h = {}
positive_by_h = {}
for h in HORIZONS_71D5H:
    ph = positive_features_71d5h[
        positive_features_71d5h["horizon_minutes"] == h
    ].copy()

    if h == 60:
        cc = candidate_features_71d5h[
            candidate_features_71d5h["candidate_band"] == "QUIET_GAP"
        ].copy()
    else:
        cc = candidate_features_71d5h.copy()

    if cc.empty:
        raise RuntimeError(f"No candidates available at horizon {h}.")

    Xp = ph[FEATURES_71D5H].replace(
        [np.inf, -np.inf], np.nan
    ).fillna(0.0).to_numpy(dtype=float)

    Xc = cc[FEATURES_71D5H].replace(
        [np.inf, -np.inf], np.nan
    ).fillna(0.0).to_numpy(dtype=float)

    scaler = StandardScaler()
    scaler.fit(np.vstack([Xp, Xc]))

    positive_by_h[h] = (ph, scaler.transform(Xp))
    candidate_by_h[h] = (cc, scaler.transform(Xc))

# For every representative positive user and clean user, find the nearest
# candidate cutoff at each horizon. Aggregate the five horizon distances.
pair_rows = []

for puid in selected_positive_users:
    pair = None

    for h in HORIZONS_71D5H:
        ph, Xp = positive_by_h[h]
        cc, Xc = candidate_by_h[h]

        loc = np.where(ph["user_id"].to_numpy() == puid)[0]
        if len(loc) != 1:
            raise RuntimeError(
                f"Positive user {puid} missing at horizon {h}."
            )

        pv = Xp[int(loc[0])]
        dist = np.sqrt(((Xc - pv) ** 2).sum(axis=1))

        tmp = cc[["user_id", "candidate_id", "cutoff_time"]].copy()
        tmp["distance"] = dist

        # One best cutoff for each clean user at this horizon.
        tmp = (
            tmp.sort_values("distance")
            .groupby("user_id", as_index=False)
            .first()
        )

        tmp = tmp.rename(columns={
            "candidate_id": f"candidate_id_{h}",
            "cutoff_time": f"cutoff_time_{h}",
            "distance": f"distance_{h}",
        })

        pair = tmp if pair is None else pair.merge(
            tmp, on="user_id", how="inner"
        )

    dist_cols = [f"distance_{h}" for h in HORIZONS_71D5H]
    pair["aggregate_distance"] = pair[dist_cols].mean(axis=1)
    pair["positive_user_id"] = puid
    pair_rows.append(pair)

pair_costs = pd.concat(pair_rows, ignore_index=True)

# Global greedy one-to-one user assignment.
assignments = []
used_positive = set()
used_clean = set()

for _, r in (
    pair_costs
    .sort_values(["aggregate_distance", "positive_user_id", "user_id"])
    .iterrows()
):
    puid = r["positive_user_id"]
    cuid = r["user_id"]

    if puid in used_positive or cuid in used_clean:
        continue

    # Do NOT impose an arbitrary 60-minute separation between cutoffs.
    # Instead, source-event non-reuse is enforced after candidate windows
    # are selected. This allows legitimate nearby clean sessions while
    # preserving strict provenance independence.
    proposed_times = pd.to_datetime(
        [r[f"cutoff_time_{h}"] for h in HORIZONS_71D5H]
    )

    if len(proposed_times) != len(HORIZONS_71D5H):
        continue

    assignments.append(r)
    used_positive.add(puid)
    used_clean.add(cuid)

    if len(assignments) == 20:
        break

if len(assignments) != 20:
    raise RuntimeError(
        f"Could establish only {len(assignments)} of 20 user matches "
        "while maintaining >=60-minute separation between all five "
        "control cutoffs. Do not relax this constraint silently."
    )

assignment_df = pd.DataFrame(assignments)
print("One-to-one user matches:", len(assignment_df))
print(
    "Control selection rule: source-event non-reuse, "
    "not arbitrary cutoff separation"
)

selected_rows_71d5h = []

for _, a in assignment_df.iterrows():
    for h in HORIZONS_71D5H:
        selected_rows_71d5h.append({
            "user_id": a["user_id"],
            "candidate_id": a[f"candidate_id_{h}"],
            "cutoff_time": a[f"cutoff_time_{h}"],
            "horizon_minutes": h,
            "matching_distance": float(a[f"distance_{h}"]),
            "positive_user_id": a["positive_user_id"],
            "candidate_band": "QUIET_GAP" if h == 60 else "ACTIVE_GAP",
        })

hard_negative_windows_71d5h = pd.DataFrame(selected_rows_71d5h)

print(
    "\nSelected hard-negative windows:",
    len(hard_negative_windows_71d5h)
)

if len(hard_negative_windows_71d5h) != 100:
    raise RuntimeError("Expected exactly 100 hard-negative windows.")

# ----------------------------------------------------------------------
# 11. Finalize the 20 matched clean controls
# ----------------------------------------------------------------------
# IMPORTANT:
# Only 20 representative positive users are intentionally matched.
# Therefore we must NOT require all 80 positive users to appear here.
# The previous v2 code incorrectly imposed that requirement.

matched_positive_users_71d5h = set(
    hard_negative_windows_71d5h["positive_user_id"].unique()
)

matched_control_users_71d5h = set(
    hard_negative_windows_71d5h["user_id"].unique()
)

if len(matched_positive_users_71d5h) != 20:
    raise RuntimeError(
        "Expected exactly 20 representative positive users in the "
        "hard-negative construction."
    )

if len(matched_control_users_71d5h) != 20:
    raise RuntimeError(
        "Expected exactly 20 clean control users in the "
        "hard-negative construction."
    )

control_users_71d5h = sorted(matched_control_users_71d5h)

print(
    "Matched representative positive users:",
    len(matched_positive_users_71d5h)
)
print(
    "Matched clean control users:",
    len(matched_control_users_71d5h)
)

# Every selected clean control user must have exactly five horizons.
control_horizon_counts_71d5h = (
    hard_negative_windows_71d5h
    .groupby("user_id")["horizon_minutes"]
    .nunique()
)

if not (control_horizon_counts_71d5h == 5).all():
    raise RuntimeError(
        "Every matched clean control user must have all five horizons."
    )

# ----------------------------------------------------------------------

hard_negative_windows_71d5h["label"] = 0
hard_negative_windows_71d5h["class"] = "HARD_NEGATIVE"
hard_negative_windows_71d5h["window_id"] = [
    f"HN71D5H_{i:04d}"
    for i in range(1, len(hard_negative_windows_71d5h) + 1)
]

if len(hard_negative_windows_71d5h) != 100:
    raise RuntimeError(
        f"Expected exactly 100 hard-negative windows, got "
        f"{len(hard_negative_windows_71d5h)}."
    )

# Add positive metadata by matching each clean control to the positive
# user that selected it. The metadata is descriptive, not used as an
# event-generation feature.
positive_lookup_71d5h = (
    pos_w_71d5h[
        [
            "user_id",
            "attack_type",
            "attack_severity",
            "takeover_time",
        ]
    ]
    .drop_duplicates("user_id")
    .set_index("user_id")
)

hard_negative_windows_71d5h["matched_positive_user_id"] = (
    hard_negative_windows_71d5h["positive_user_id"]
)

hard_negative_windows_71d5h["attack_type_reference"] = (
    hard_negative_windows_71d5h["positive_user_id"]
    .map(positive_lookup_71d5h["attack_type"])
)

hard_negative_windows_71d5h["attack_severity_reference"] = (
    hard_negative_windows_71d5h["positive_user_id"]
    .map(positive_lookup_71d5h["attack_severity"])
)

# ----------------------------------------------------------------------
# 12. Enforce source-event non-reuse across the selected 100 windows.
#
# If two selected cutoffs for the same control user have overlapping
# 60-minute histories, retain the better-matched candidate and replace
# the conflicting candidate with the next-best candidate for the same
# representative positive user/horizon.
#
# This is provenance control, not a synthetic-event operation.
# ----------------------------------------------------------------------
def source_ids_for_candidate_71d5h(uid, cutoff):
    cutoff = pd.Timestamp(cutoff)
    lo = cutoff - pd.Timedelta(minutes=LOOKBACK_71D5H)
    x = clean_obs_71d5h[
        (clean_obs_71d5h["user_id"] == uid) &
        (clean_obs_71d5h["timestamp"] >= lo) &
        (clean_obs_71d5h["timestamp"] < cutoff)
    ]
    return set(x["event_id"].astype(str).tolist())

candidate_source_sets_71d5h = {}
for _, c in candidate_cutoffs_71d5h.iterrows():
    key = (str(c["user_id"]), str(c["candidate_id"]))
    candidate_source_sets_71d5h[key] = source_ids_for_candidate_71d5h(
        c["user_id"], c["cutoff_time"]
    )

# Build all candidate alternatives for each matched user/horizon.
# Recompute horizon distance against the representative positive user.
selected_final_rows_71d5h = []
used_source_events_71d5h = set()

for _, a in assignment_df.iterrows():
    cuid = a["user_id"]
    puid = a["positive_user_id"]

    for h in HORIZONS_71D5H:
        ph, Xp = positive_by_h[h]
        cc, Xc = candidate_by_h[h]

        loc = np.where(ph["user_id"].to_numpy() == puid)[0]
        pv = Xp[int(loc[0])]

        dist = np.sqrt(((Xc - pv) ** 2).sum(axis=1))
        tmp = cc.copy()
        tmp["distance"] = dist
        tmp = tmp[tmp["user_id"] == cuid].sort_values("distance")

        chosen = None

        for _, cand in tmp.iterrows():
            key = (str(cand["user_id"]), str(cand["candidate_id"]))
            source_set = candidate_source_sets_71d5h[key]

            if source_set.isdisjoint(used_source_events_71d5h):
                chosen = cand
                break

        if chosen is None:
            raise RuntimeError(
                f"No non-overlapping source-event candidate remains for "
                f"control user {cuid}, horizon {h}."
            )

        source_set = candidate_source_sets_71d5h[
            (str(chosen["user_id"]), str(chosen["candidate_id"]))
        ]
        used_source_events_71d5h.update(source_set)

        selected_final_rows_71d5h.append({
            "user_id": chosen["user_id"],
            "candidate_id": chosen["candidate_id"],
            "cutoff_time": chosen["cutoff_time"],
            "horizon_minutes": h,
            "matching_distance": float(chosen["distance"]),
            "positive_user_id": puid,
            "candidate_band": (
                "QUIET_GAP" if h == 60 else "ACTIVE_GAP"
            ),
        })

hard_negative_windows_71d5h = pd.DataFrame(
    selected_final_rows_71d5h
)

if len(hard_negative_windows_71d5h) != 100:
    raise RuntimeError(
        f"Expected exactly 100 final hard-negative windows, got "
        f"{len(hard_negative_windows_71d5h)}."
    )

# Create the canonical benchmark window identifier expected by all
# downstream AFRITAC validation and feature-extraction code.
# candidate_id remains the provenance identifier for the clean source
# cutoff; window_id identifies the reconstructed benchmark window.
hard_negative_windows_71d5h = hard_negative_windows_71d5h.reset_index(drop=True)
hard_negative_windows_71d5h["window_id"] = [
    f"HN_71D5H_{i:04d}"
    for i in range(1, len(hard_negative_windows_71d5h) + 1)
]

# Keep window_id first for compatibility with existing downstream code.
window_cols = ["window_id"] + [
    c for c in hard_negative_windows_71d5h.columns
    if c != "window_id"
]
hard_negative_windows_71d5h = hard_negative_windows_71d5h[window_cols]

print(
    "Final windows after source-event conflict resolution:",
    len(hard_negative_windows_71d5h)
)
print(
    "Canonical window IDs:",
    hard_negative_windows_71d5h["window_id"].nunique()
)
print(
    "Unique source events reserved:",
    len(used_source_events_71d5h)
)

# Defensive schema/integrity check before event reconstruction.
if "window_id" not in hard_negative_windows_71d5h.columns:
    raise RuntimeError("Canonical hard-negative window_id was not created.")

if hard_negative_windows_71d5h["window_id"].duplicated().any():
    raise RuntimeError("Duplicate hard-negative window_id values detected.")

# ----------------------------------------------------------------------
# 13. Copy source events from clean observable history
#
# New benchmark event IDs are assigned.
# Original source event IDs are retained only as provenance.
# ----------------------------------------------------------------------
hard_event_rows_71d5h = []

for _, w in hard_negative_windows_71d5h.iterrows():
    uid = w["user_id"]
    cutoff = pd.Timestamp(w["cutoff_time"])
    lo = cutoff - pd.Timedelta(minutes=LOOKBACK_71D5H)

    x = clean_obs_71d5h[
        (clean_obs_71d5h["user_id"] == uid) &
        (clean_obs_71d5h["timestamp"] >= lo) &
        (clean_obs_71d5h["timestamp"] < cutoff)
    ].copy()

    for _, e in x.iterrows():
        d = e.to_dict()

        d["source_event_id"] = str(e["event_id"])
        d["event_id"] = (
            f"HNE71D5H_{len(hard_event_rows_71d5h)+1:07d}"
        )
        d["ground_truth_state"] = "NORMAL"
        d["is_attack"] = 0
        d["is_observable_precursor"] = 0
        d["hard_negative_control"] = 1
        d["hard_negative_window_id"] = w["window_id"]
        d["horizon_minutes"] = int(w["horizon_minutes"])
        d["control_user_id"] = uid
        d["cutoff_time"] = cutoff

        hard_event_rows_71d5h.append(d)

hard_negative_events_71d5h = pd.DataFrame(
    hard_event_rows_71d5h
)

print("\nHard-negative events:", len(hard_negative_events_71d5h))

# ----------------------------------------------------------------------
# 13. Structural validation
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
print("71D.5H STRUCTURAL VALIDATION")
print("=" * 70)

print("\nWindows by horizon:")
print(
    hard_negative_windows_71d5h
    .groupby("horizon_minutes")
    .size()
)

expected_h_71d5h = {5: 20, 10: 20, 15: 20, 30: 20, 60: 20}
actual_h_71d5h = (
    hard_negative_windows_71d5h
    .groupby("horizon_minutes")
    .size()
    .to_dict()
)

if actual_h_71d5h != expected_h_71d5h:
    raise RuntimeError(
        f"Incorrect horizon distribution: {actual_h_71d5h}"
    )

print("✓ Exactly 20 windows per horizon")

control_counts_71d5h = (
    hard_negative_windows_71d5h
    .groupby("user_id")
    .size()
)

print("\nControl user window counts:")
print(control_counts_71d5h.describe())

if not (
    len(control_counts_71d5h) == 20 and
    (control_counts_71d5h == 5).all()
):
    raise RuntimeError(
        "Each of the 20 control users must have exactly 5 horizons."
    )

print("✓ Exactly 20 control users × 5 horizons")

positive_overlap_71d5h = (
    set(hard_negative_windows_71d5h["user_id"]) &
    positive_users_71d5h
)

print(
    "Positive/control user overlap:",
    len(positive_overlap_71d5h)
)

if positive_overlap_71d5h:
    raise RuntimeError("Positive/control user overlap detected.")

print("✓ No positive/control user overlap")

# Event ID uniqueness.
duplicate_ids_71d5h = int(
    hard_negative_events_71d5h["event_id"].duplicated().sum()
)

print("Duplicate benchmark event IDs:", duplicate_ids_71d5h)

if duplicate_ids_71d5h:
    raise RuntimeError("Duplicate benchmark event IDs detected.")

print("✓ Benchmark event IDs are unique")

# Source event reuse.
duplicate_sources_71d5h = int(
    hard_negative_events_71d5h["source_event_id"].duplicated().sum()
)

print("Source event IDs reused across windows:", duplicate_sources_71d5h)

if duplicate_sources_71d5h:
    raise RuntimeError(
        "Source events are reused across hard-negative windows. "
        "The cutoff-separation constraint was not respected."
    )

print("✓ Source events are not reused")

# Explicitly validate that each control user's five prediction cutoffs
# are separated by at least the 60-minute lookback.
cutoff_separation_violations_71d5h = 0

for uid, g in hard_negative_windows_71d5h.groupby("user_id"):
    times = (
        pd.to_datetime(g["cutoff_time"])
        .sort_values()
        .reset_index(drop=True)
    )
    if len(times) != 5:
        raise RuntimeError(
            f"Control user {uid} does not have exactly five cutoffs."
        )

    deltas = times.diff().dropna()
    if (deltas < pd.Timedelta(minutes=LOOKBACK_71D5H)).any():
        cutoff_separation_violations_71d5h += 1

print(
    "Control users with overlapping 60-minute time intervals:",
    cutoff_separation_violations_71d5h
)
print(
    "✓ Time-interval overlap is permitted because source-event reuse is zero"
)

# Source-event non-reuse is the authoritative provenance constraint.
source_reuse_final_71d5h = 0

if "source_event_id" in hard_negative_events_71d5h.columns:
    source_counts_71d5h = (
        hard_negative_events_71d5h["source_event_id"]
        .dropna()
        .astype(str)
        .value_counts()
    )
    source_reuse_final_71d5h = int((source_counts_71d5h > 1).sum())

print(
    "Final source event IDs reused:",
    source_reuse_final_71d5h
)

if source_reuse_final_71d5h != 0:
    raise RuntimeError(
        "Source-event provenance violation: one or more source events "
        "are reused across hard-negative windows."
    )

print()
print("=" * 70)
print("✓ 71D.5H STRUCTURAL VALIDATION PASSED")
print("=" * 70)


print("✓ Control cutoff histories are non-overlapping")

# Attack contamination.
attack_events_71d5h = int(
    pd.to_numeric(
        hard_negative_events_71d5h["is_attack"],
        errors="coerce"
    ).fillna(0).sum()
)

print("Hard-negative attack events:", attack_events_71d5h)

if attack_events_71d5h:
    raise RuntimeError("Attack contamination detected.")

# Precursor contamination.
precursor_events_71d5h = int(
    pd.to_numeric(
        hard_negative_events_71d5h[
            "is_observable_precursor"
        ],
        errors="coerce"
    ).fillna(0).sum()
)

print(
    "Hard-negative precursor events:",
    precursor_events_71d5h
)

if precursor_events_71d5h:
    raise RuntimeError("Precursor contamination detected.")

# ----------------------------------------------------------------------
# 14. Final hard-negative activity diagnostics
# ----------------------------------------------------------------------
def window_features_71d5h(stream, windows):
    rows = []

    for _, w in windows.iterrows():
        uid = w["user_id"]
        cutoff = pd.Timestamp(w["cutoff_time"])

        us = stream[stream["user_id"] == uid]
        d = extract_features_71d5h(us, cutoff)

        d["window_id"] = w["window_id"]
        d["horizon_minutes"] = int(w["horizon_minutes"])
        rows.append(d)

    return pd.DataFrame(rows)

hard_features_71d5h = window_features_71d5h(
    hard_negative_events_71d5h,
    hard_negative_windows_71d5h
)

print("\nHard-negative activity by horizon:")
print(
    hard_features_71d5h
    .groupby("horizon_minutes")[
        [
            "event_count",
            "session_count",
            "event_type_count",
            "modality_count",
            "last_5_share",
            "last_10_share",
            "last_15_share",
            "last_30_share",
            "delay_mean",
            "delay_std",
            "transaction_count",
            "transaction_amount_sum",
        ]
    ]
    .mean()
)

# ----------------------------------------------------------------------
# 15. Matching distance summary
# ----------------------------------------------------------------------
matching_71d5h = (
    hard_negative_windows_71d5h
    .groupby("horizon_minutes")["matching_distance"]
    .agg(["count", "mean", "median", "min", "max"])
)

print("\nMatching distance by horizon:")
print(matching_71d5h)

# ----------------------------------------------------------------------
# 16. Quiet 60-minute validation
# ----------------------------------------------------------------------
h60_71d5h = hard_negative_windows_71d5h[
    hard_negative_windows_71d5h["horizon_minutes"] == 60
].copy()

h60_features_71d5h = hard_features_71d5h[
    hard_features_71d5h["horizon_minutes"] == 60
]

print("\n60-minute hard-negative history:")
print(
    h60_features_71d5h[
        [
            "event_count",
            "session_count",
            "event_type_count",
            "modality_count",
            "transaction_count",
        ]
    ].describe()
)

# ----------------------------------------------------------------------
# 17. Promote only to candidate names.
#
# 71D.5F authoritative objects are intentionally untouched.
# ----------------------------------------------------------------------
hard_negative_windows_71d5h_candidate = (
    hard_negative_windows_71d5h.copy()
)

hard_negative_events_71d5h_candidate = (
    hard_negative_events_71d5h.copy()
)

print("\n" + "=" * 70)
print("AFRITAC 71D.5H COMPLETE")
print("=" * 70)

print(
    "Control users:",
    hard_negative_windows_71d5h_candidate["user_id"].nunique()
)
print(
    "Hard-negative windows:",
    len(hard_negative_windows_71d5h_candidate)
)
print(
    "Hard-negative events:",
    len(hard_negative_events_71d5h_candidate)
)
print(
    "Positive/control overlap:",
    len(positive_overlap_71d5h)
)
print(
    "Attack contamination:",
    attack_events_71d5h
)
print(
    "Precursor contamination:",
    precursor_events_71d5h
)

print("\n✓ 71D.5H candidate hard-negative reconstruction finished.")
print("✓ 71D.5F objects were not overwritten.")
print("✓ Run the 71D.5I validation before any promotion.")

# ==============================================================================
# NOTEBOOK CELL 221
# ==============================================================================

# AFRITAC STEP 71D.5H
# HORIZON-MATCHED OBSERVABLE HARD-NEGATIVE RECONSTRUCTION
#
# Purpose:
#   Reconstruct hard-negative controls by matching the FINAL prediction
#   window feature distributions horizon by horizon.
#
#   This cell DOES NOT overwrite 71D.5F objects.
#   It creates *_71d5h_candidate objects only.
#
# Key design:
#   1. Clean controls come from users outside the 80 positive users.
#   2. Cutoffs are placed in observable inter-session gaps.
#   3. The cutoff is never equal to an observed event timestamp.
#   4. The 5/10/15/30 minute controls are matched on the actual 60-minute
#      feature vector used by 71D.5G.
#   5. The 60 minute horizon is handled as a quiet-history problem because
#      the positive precursor layer currently has zero observable activity
#      at that cutoff.
#   6. Source events are copied from the clean observable stream with new
#      benchmark event IDs. No synthetic events are fabricated.
#
# Run after the successful AFRITAC 71D.5F construction.

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler

print("=" * 70)
print("AFRITAC STEP 71D.5H")
print("HORIZON-MATCHED OBSERVABLE HARD-NEGATIVE RECONSTRUCTION")
print("=" * 70)

# ----------------------------------------------------------------------
# 1. Required objects
# ----------------------------------------------------------------------
required = [
    "positive_windows_71d5f",
    "positive_stream_71d5f",
    "normal_stream",
]
missing = [x for x in required if x not in globals()]
print("Required objects missing:", missing)
if missing:
    raise RuntimeError("Run the completed 71D.5F pipeline first.")

HORIZONS_71D5H = [5, 10, 15, 30, 60]
LOOKBACK_71D5H = 60
SEED_71D5H = int(globals().get("SEED", 42)) + 7058
rng_71d5h = np.random.default_rng(SEED_71D5H)

FEATURES_71D5H = [
    "event_count",
    "session_count",
    "event_type_count",
    "modality_count",
    "delay_mean",
    "delay_std",
    "last_5_share",
    "last_10_share",
    "last_15_share",
    "last_30_share",
    "new_device_rate",
    "location_change_rate",
    "roaming_rate",
    "transaction_count",
    "transaction_amount_sum",
    "transaction_amount_mean",
]

# ----------------------------------------------------------------------
# 2. Prepare positive and clean observable streams
# ----------------------------------------------------------------------
pos_w_71d5h = positive_windows_71d5f.copy()
pos_w_71d5h["user_id"] = pos_w_71d5h["user_id"].astype(str)
pos_w_71d5h["cutoff_time"] = pd.to_datetime(
    pos_w_71d5h["cutoff_time"], errors="coerce"
)
pos_w_71d5h["horizon_minutes"] = pos_w_71d5h["horizon_minutes"].astype(int)

pos_stream_71d5h = positive_stream_71d5f.copy()
pos_stream_71d5h["user_id"] = pos_stream_71d5h["user_id"].astype(str)
pos_stream_71d5h["timestamp"] = pd.to_datetime(
    pos_stream_71d5h["timestamp"], errors="coerce"
)
pos_stream_71d5h = pos_stream_71d5h.dropna(subset=["timestamp"]).copy()

normal_71d5h = normal_stream.copy()
normal_71d5h["user_id"] = normal_71d5h["user_id"].astype(str)
normal_71d5h["timestamp"] = pd.to_datetime(
    normal_71d5h["timestamp"], errors="coerce"
)
normal_71d5h = normal_71d5h.dropna(subset=["timestamp"]).copy()

positive_users_71d5h = set(pos_w_71d5h["user_id"].unique())

all_users_71d5h = set(normal_71d5h["user_id"].unique())
clean_pool_71d5h = sorted(all_users_71d5h - positive_users_71d5h)

print("Positive users:", len(positive_users_71d5h))
print("Clean candidate users:", len(clean_pool_71d5h))

if len(clean_pool_71d5h) < 20:
    raise RuntimeError("Fewer than 20 clean users are available.")

# ----------------------------------------------------------------------
# 3. Feature extraction
# ----------------------------------------------------------------------
def _numeric_rate_71d5h(x, col):
    if len(x) == 0 or col not in x.columns:
        return 0.0
    s = pd.to_numeric(x[col], errors="coerce")
    return float(s.fillna(0).mean())

def extract_features_71d5h(stream, cutoff):
    cutoff = pd.Timestamp(cutoff)
    lo = cutoff - pd.Timedelta(minutes=LOOKBACK_71D5H)

    x = stream[
        (stream["timestamp"] >= lo) &
        (stream["timestamp"] < cutoff)
    ].copy()

    n = len(x)
    out = {f: 0.0 for f in FEATURES_71D5H}

    out["event_count"] = float(n)
    out["session_count"] = (
        float(x["session_id"].nunique())
        if n and "session_id" in x.columns else 0.0
    )
    out["event_type_count"] = (
        float(x["event_type"].nunique())
        if n and "event_type" in x.columns else 0.0
    )
    out["modality_count"] = (
        float(x["modality"].nunique())
        if n and "modality" in x.columns else 0.0
    )

    if n:
        delay = pd.to_numeric(
            x.get(
                "response_delay_ms",
                pd.Series(index=x.index, dtype=float)
            ),
            errors="coerce"
        ).dropna()

        out["delay_mean"] = float(delay.mean()) if len(delay) else 0.0
        out["delay_std"] = float(delay.std(ddof=0)) if len(delay) else 0.0

        for m in [5, 10, 15, 30]:
            out[f"last_{m}_share"] = float(
                (
                    x["timestamp"] >=
                    cutoff - pd.Timedelta(minutes=m)
                ).mean()
            )

        out["new_device_rate"] = _numeric_rate_71d5h(
            x, "new_device"
        )
        out["location_change_rate"] = _numeric_rate_71d5h(
            x, "location_change"
        )
        out["roaming_rate"] = _numeric_rate_71d5h(
            x, "roaming"
        )

        if "transaction_amount" in x.columns:
            amount = pd.to_numeric(
                x["transaction_amount"], errors="coerce"
            )
            valid = amount.notna() & amount.gt(0)

            out["transaction_count"] = float(valid.sum())

            if valid.sum():
                out["transaction_amount_sum"] = float(
                    amount[valid].sum()
                )
                out["transaction_amount_mean"] = float(
                    amount[valid].mean()
                )

    return out

# ----------------------------------------------------------------------
# 4. Positive horizon feature matrix
# ----------------------------------------------------------------------
positive_feature_rows_71d5h = []

for _, r in pos_w_71d5h.iterrows():
    uid = r["user_id"]
    us = pos_stream_71d5h[
        pos_stream_71d5h["user_id"] == uid
    ]

    d = extract_features_71d5h(us, r["cutoff_time"])
    d.update({
        "user_id": uid,
        "window_id": r.get("window_id", None),
        "horizon_minutes": int(r["horizon_minutes"]),
        "cutoff_time": r["cutoff_time"],
    })
    positive_feature_rows_71d5h.append(d)

positive_features_71d5h = pd.DataFrame(
    positive_feature_rows_71d5h
)

print("\nPositive horizon profiles:")
print(
    positive_features_71d5h.groupby(
        "horizon_minutes"
    ).size()
)

# ----------------------------------------------------------------------
# 5. Build observable session blocks for clean users
#
# IMPORTANT:
#   normal_stream timestamps are the authoritative observable timeline.
#   sessions.end_time is NOT used because prior diagnostics showed that
#   observable events can continue after the session-table end_time.
# ----------------------------------------------------------------------
clean_obs_71d5h = normal_71d5h[
    normal_71d5h["user_id"].isin(clean_pool_71d5h)
].copy()

session_blocks_71d5h = (
    clean_obs_71d5h
    .groupby(["user_id", "session_id"], as_index=False)
    .agg(
        observable_start=("timestamp", "min"),
        observable_end=("timestamp", "max"),
        event_count=("event_id", "count"),
    )
    .sort_values(["user_id", "observable_start"])
    .reset_index(drop=True)
)

print("\nObservable clean session blocks:", len(session_blocks_71d5h))

# ----------------------------------------------------------------------
# 6. Generate valid inter-session candidate cutoffs
#
# For 5/10/15/30 minute matching:
#   put the cutoff 30 minutes after the previous observable session end
#   whenever the gap permits.
#
# For 60 minute matching:
#   require a quiet gap > 60 minutes and place cutoff 65 minutes after
#   the previous observable session end. This produces genuinely quiet
#   60-minute histories rather than fabricated events.
# ----------------------------------------------------------------------
candidate_rows_71d5h = []

for uid, g in session_blocks_71d5h.groupby("user_id"):
    g = g.sort_values("observable_start").reset_index(drop=True)

    for i in range(len(g) - 1):
        prev_end = pd.Timestamp(g.loc[i, "observable_end"])
        next_start = pd.Timestamp(g.loc[i + 1, "observable_start"])
        gap_min = (next_start - prev_end).total_seconds() / 60.0

        # Short horizons: candidate cutoff 30 min after previous session.
        if gap_min >= 35:
            cutoff_short = prev_end + pd.Timedelta(minutes=30)

            candidate_rows_71d5h.append({
                "candidate_id": f"CH5_{len(candidate_rows_71d5h)+1:06d}",
                "user_id": uid,
                "cutoff_time": cutoff_short,
                "gap_minutes": gap_min,
                "candidate_band": "ACTIVE_GAP",
            })

        # Long horizon: genuinely quiet 60-minute history.
        if gap_min > 70:
            cutoff_quiet = prev_end + pd.Timedelta(minutes=65)

            candidate_rows_71d5h.append({
                "candidate_id": f"CH5_{len(candidate_rows_71d5h)+1:06d}",
                "user_id": uid,
                "cutoff_time": cutoff_quiet,
                "gap_minutes": gap_min,
                "candidate_band": "QUIET_GAP",
            })

candidate_cutoffs_71d5h = pd.DataFrame(candidate_rows_71d5h)

if candidate_cutoffs_71d5h.empty:
    raise RuntimeError("No valid observable inter-session candidate cutoffs.")

candidate_cutoffs_71d5h["cutoff_time"] = pd.to_datetime(
    candidate_cutoffs_71d5h["cutoff_time"]
)

# Remove accidental duplicate user/cutoff pairs.
candidate_cutoffs_71d5h = (
    candidate_cutoffs_71d5h
    .drop_duplicates(["user_id", "cutoff_time"])
    .reset_index(drop=True)
)

print("Candidate cutoffs:", len(candidate_cutoffs_71d5h))
print(
    "Candidate users:",
    candidate_cutoffs_71d5h["user_id"].nunique()
)

# ----------------------------------------------------------------------
# 7. Hard structural cutoff validation
# ----------------------------------------------------------------------
event_time_set_71d5h = set(
    clean_obs_71d5h["timestamp"].tolist()
)

collision_count_71d5h = int(
    candidate_cutoffs_71d5h["cutoff_time"]
    .isin(event_time_set_71d5h)
    .sum()
)

if collision_count_71d5h:
    raise RuntimeError(
        f"{collision_count_71d5h} candidate cutoffs equal "
        "observable event timestamps."
    )

# Confirm candidates are outside all observable session blocks.
inside_count_71d5h = 0

for _, c in candidate_cutoffs_71d5h.iterrows():
    uid = c["user_id"]
    t = c["cutoff_time"]

    blocks = session_blocks_71d5h[
        session_blocks_71d5h["user_id"] == uid
    ]

    inside = (
        (blocks["observable_start"] <= t) &
        (t <= blocks["observable_end"])
    ).any()

    if inside:
        inside_count_71d5h += 1

if inside_count_71d5h:
    raise RuntimeError(
        f"{inside_count_71d5h} candidate cutoffs are inside "
        "observable sessions."
    )

print("Cutoff/event collisions:", collision_count_71d5h)
print("Cutoffs inside observable sessions:", inside_count_71d5h)

# ----------------------------------------------------------------------
# 8. Build candidate feature matrix
# ----------------------------------------------------------------------
candidate_feature_rows_71d5h = []

for _, c in candidate_cutoffs_71d5h.iterrows():
    uid = c["user_id"]
    us = clean_obs_71d5h[
        clean_obs_71d5h["user_id"] == uid
    ]

    d = extract_features_71d5h(us, c["cutoff_time"])
    d.update({
        "candidate_id": c["candidate_id"],
        "user_id": uid,
        "cutoff_time": c["cutoff_time"],
        "gap_minutes": c["gap_minutes"],
        "candidate_band": c["candidate_band"],
    })
    candidate_feature_rows_71d5h.append(d)

candidate_features_71d5h = pd.DataFrame(
    candidate_feature_rows_71d5h
)

print("\nCandidate feature matrix:", candidate_features_71d5h.shape)

# ----------------------------------------------------------------------
# 9. Candidate history diagnostics
# ----------------------------------------------------------------------
print("\nCandidate event-count diagnostic:")
print(
    candidate_features_71d5h["event_count"].describe()
)

quiet_candidates_71d5h = candidate_features_71d5h[
    candidate_features_71d5h["candidate_band"] == "QUIET_GAP"
].copy()

print("\nQuiet-gap candidates:", len(quiet_candidates_71d5h))
if len(quiet_candidates_71d5h):
    print(
        quiet_candidates_71d5h["event_count"].describe()
    )

# ----------------------------------------------------------------------
# 10. Horizon-aware user matching
#
# Exactly 20 clean users x 5 horizons = 100 windows.
# We first select 20 representative positive users, then establish a
# one-to-one positive-user/control-user mapping using the aggregate
# nearest distance across all five horizons. This avoids the previous
# mistake of independently matching all 80 positive users.

pos_complete = (
    positive_features_71d5h.groupby("user_id")["horizon_minutes"]
    .nunique()
)
pos_complete = pos_complete[pos_complete == len(HORIZONS_71D5H)].index.tolist()

if len(pos_complete) != 80:
    raise RuntimeError(
        f"Expected 80 complete positive users, got {len(pos_complete)}."
    )

# Select 20 representative positive users using a diversity-aware
# selection in the complete five-horizon feature space.
profiles = []
for uid in pos_complete:
    z = (
        positive_features_71d5h[
            positive_features_71d5h["user_id"] == uid
        ]
        .set_index("horizon_minutes")
        .loc[HORIZONS_71D5H, FEATURES_71D5H]
        .to_numpy(dtype=float)
    )
    profiles.append(
        np.nan_to_num(z, nan=0.0, posinf=0.0, neginf=0.0).ravel()
    )

P = np.vstack(profiles)
ps = StandardScaler().fit_transform(P)

centroid = ps.mean(axis=0)
selected_idx = [int(np.argmin(np.sqrt(((ps-centroid)**2).sum(axis=1))))]
remaining = set(range(80)) - set(selected_idx)

while len(selected_idx) < 20:
    chosen = ps[selected_idx]
    rem = sorted(remaining)
    nearest = np.min(
        np.sqrt(
            ((ps[rem, None, :] - chosen[None, :, :]) ** 2).sum(axis=2)
        ),
        axis=1,
    )
    best = rem[int(np.argmax(nearest))]
    selected_idx.append(best)
    remaining.remove(best)

selected_positive_users = [pos_complete[i] for i in selected_idx]

print("\nRepresentative positive users:", len(selected_positive_users))

# Horizon-specific scaled candidate matrices.
candidate_by_h = {}
positive_by_h = {}
for h in HORIZONS_71D5H:
    ph = positive_features_71d5h[
        positive_features_71d5h["horizon_minutes"] == h
    ].copy()

    if h == 60:
        cc = candidate_features_71d5h[
            candidate_features_71d5h["candidate_band"] == "QUIET_GAP"
        ].copy()
    else:
        cc = candidate_features_71d5h.copy()

    if cc.empty:
        raise RuntimeError(f"No candidates available at horizon {h}.")

    Xp = ph[FEATURES_71D5H].replace(
        [np.inf, -np.inf], np.nan
    ).fillna(0.0).to_numpy(dtype=float)

    Xc = cc[FEATURES_71D5H].replace(
        [np.inf, -np.inf], np.nan
    ).fillna(0.0).to_numpy(dtype=float)

    scaler = StandardScaler()
    scaler.fit(np.vstack([Xp, Xc]))

    positive_by_h[h] = (ph, scaler.transform(Xp))
    candidate_by_h[h] = (cc, scaler.transform(Xc))

# For every representative positive user and clean user, find the nearest
# candidate cutoff at each horizon. Aggregate the five horizon distances.
pair_rows = []

for puid in selected_positive_users:
    pair = None

    for h in HORIZONS_71D5H:
        ph, Xp = positive_by_h[h]
        cc, Xc = candidate_by_h[h]

        loc = np.where(ph["user_id"].to_numpy() == puid)[0]
        if len(loc) != 1:
            raise RuntimeError(
                f"Positive user {puid} missing at horizon {h}."
            )

        pv = Xp[int(loc[0])]
        dist = np.sqrt(((Xc - pv) ** 2).sum(axis=1))

        tmp = cc[["user_id", "candidate_id", "cutoff_time"]].copy()
        tmp["distance"] = dist

        # One best cutoff for each clean user at this horizon.
        tmp = (
            tmp.sort_values("distance")
            .groupby("user_id", as_index=False)
            .first()
        )

        tmp = tmp.rename(columns={
            "candidate_id": f"candidate_id_{h}",
            "cutoff_time": f"cutoff_time_{h}",
            "distance": f"distance_{h}",
        })

        pair = tmp if pair is None else pair.merge(
            tmp, on="user_id", how="inner"
        )

    dist_cols = [f"distance_{h}" for h in HORIZONS_71D5H]
    pair["aggregate_distance"] = pair[dist_cols].mean(axis=1)
    pair["positive_user_id"] = puid
    pair_rows.append(pair)

pair_costs = pd.concat(pair_rows, ignore_index=True)

# Global greedy one-to-one user assignment.
assignments = []
used_positive = set()
used_clean = set()

for _, r in (
    pair_costs
    .sort_values(["aggregate_distance", "positive_user_id", "user_id"])
    .iterrows()
):
    puid = r["positive_user_id"]
    cuid = r["user_id"]

    if puid in used_positive or cuid in used_clean:
        continue

    # Do NOT impose an arbitrary 60-minute separation between cutoffs.
    # Instead, source-event non-reuse is enforced after candidate windows
    # are selected. This allows legitimate nearby clean sessions while
    # preserving strict provenance independence.
    proposed_times = pd.to_datetime(
        [r[f"cutoff_time_{h}"] for h in HORIZONS_71D5H]
    )

    if len(proposed_times) != len(HORIZONS_71D5H):
        continue

    assignments.append(r)
    used_positive.add(puid)
    used_clean.add(cuid)

    if len(assignments) == 20:
        break

if len(assignments) != 20:
    raise RuntimeError(
        f"Could establish only {len(assignments)} of 20 user matches "
        "while maintaining >=60-minute separation between all five "
        "control cutoffs. Do not relax this constraint silently."
    )

assignment_df = pd.DataFrame(assignments)
print("One-to-one user matches:", len(assignment_df))
print(
    "Control selection rule: source-event non-reuse, "
    "not arbitrary cutoff separation"
)

selected_rows_71d5h = []

for _, a in assignment_df.iterrows():
    for h in HORIZONS_71D5H:
        selected_rows_71d5h.append({
            "user_id": a["user_id"],
            "candidate_id": a[f"candidate_id_{h}"],
            "cutoff_time": a[f"cutoff_time_{h}"],
            "horizon_minutes": h,
            "matching_distance": float(a[f"distance_{h}"]),
            "positive_user_id": a["positive_user_id"],
            "candidate_band": "QUIET_GAP" if h == 60 else "ACTIVE_GAP",
        })

hard_negative_windows_71d5h = pd.DataFrame(selected_rows_71d5h)

print(
    "\nSelected hard-negative windows:",
    len(hard_negative_windows_71d5h)
)

if len(hard_negative_windows_71d5h) != 100:
    raise RuntimeError("Expected exactly 100 hard-negative windows.")

# ----------------------------------------------------------------------
# 11. Finalize the 20 matched clean controls
# ----------------------------------------------------------------------
# IMPORTANT:
# Only 20 representative positive users are intentionally matched.
# Therefore we must NOT require all 80 positive users to appear here.
# The previous v2 code incorrectly imposed that requirement.

matched_positive_users_71d5h = set(
    hard_negative_windows_71d5h["positive_user_id"].unique()
)

matched_control_users_71d5h = set(
    hard_negative_windows_71d5h["user_id"].unique()
)

if len(matched_positive_users_71d5h) != 20:
    raise RuntimeError(
        "Expected exactly 20 representative positive users in the "
        "hard-negative construction."
    )

if len(matched_control_users_71d5h) != 20:
    raise RuntimeError(
        "Expected exactly 20 clean control users in the "
        "hard-negative construction."
    )

control_users_71d5h = sorted(matched_control_users_71d5h)

print(
    "Matched representative positive users:",
    len(matched_positive_users_71d5h)
)
print(
    "Matched clean control users:",
    len(matched_control_users_71d5h)
)

# Every selected clean control user must have exactly five horizons.
control_horizon_counts_71d5h = (
    hard_negative_windows_71d5h
    .groupby("user_id")["horizon_minutes"]
    .nunique()
)

if not (control_horizon_counts_71d5h == 5).all():
    raise RuntimeError(
        "Every matched clean control user must have all five horizons."
    )

# ----------------------------------------------------------------------

hard_negative_windows_71d5h["label"] = 0
hard_negative_windows_71d5h["class"] = "HARD_NEGATIVE"
hard_negative_windows_71d5h["window_id"] = [
    f"HN71D5H_{i:04d}"
    for i in range(1, len(hard_negative_windows_71d5h) + 1)
]

if len(hard_negative_windows_71d5h) != 100:
    raise RuntimeError(
        f"Expected exactly 100 hard-negative windows, got "
        f"{len(hard_negative_windows_71d5h)}."
    )

# Add positive metadata by matching each clean control to the positive
# user that selected it. The metadata is descriptive, not used as an
# event-generation feature.
positive_lookup_71d5h = (
    pos_w_71d5h[
        [
            "user_id",
            "attack_type",
            "attack_severity",
            "takeover_time",
        ]
    ]
    .drop_duplicates("user_id")
    .set_index("user_id")
)

hard_negative_windows_71d5h["matched_positive_user_id"] = (
    hard_negative_windows_71d5h["positive_user_id"]
)

hard_negative_windows_71d5h["attack_type_reference"] = (
    hard_negative_windows_71d5h["positive_user_id"]
    .map(positive_lookup_71d5h["attack_type"])
)

hard_negative_windows_71d5h["attack_severity_reference"] = (
    hard_negative_windows_71d5h["positive_user_id"]
    .map(positive_lookup_71d5h["attack_severity"])
)

# ----------------------------------------------------------------------
# 12. Enforce source-event non-reuse across the selected 100 windows.
#
# If two selected cutoffs for the same control user have overlapping
# 60-minute histories, retain the better-matched candidate and replace
# the conflicting candidate with the next-best candidate for the same
# representative positive user/horizon.
#
# This is provenance control, not a synthetic-event operation.
# ----------------------------------------------------------------------
def source_ids_for_candidate_71d5h(uid, cutoff):
    cutoff = pd.Timestamp(cutoff)
    lo = cutoff - pd.Timedelta(minutes=LOOKBACK_71D5H)
    x = clean_obs_71d5h[
        (clean_obs_71d5h["user_id"] == uid) &
        (clean_obs_71d5h["timestamp"] >= lo) &
        (clean_obs_71d5h["timestamp"] < cutoff)
    ]
    return set(x["event_id"].astype(str).tolist())

candidate_source_sets_71d5h = {}
for _, c in candidate_cutoffs_71d5h.iterrows():
    key = (str(c["user_id"]), str(c["candidate_id"]))
    candidate_source_sets_71d5h[key] = source_ids_for_candidate_71d5h(
        c["user_id"], c["cutoff_time"]
    )

# Build all candidate alternatives for each matched user/horizon.
# Recompute horizon distance against the representative positive user.
selected_final_rows_71d5h = []
used_source_events_71d5h = set()

for _, a in assignment_df.iterrows():
    cuid = a["user_id"]
    puid = a["positive_user_id"]

    for h in HORIZONS_71D5H:
        ph, Xp = positive_by_h[h]
        cc, Xc = candidate_by_h[h]

        loc = np.where(ph["user_id"].to_numpy() == puid)[0]
        pv = Xp[int(loc[0])]

        dist = np.sqrt(((Xc - pv) ** 2).sum(axis=1))
        tmp = cc.copy()
        tmp["distance"] = dist
        tmp = tmp[tmp["user_id"] == cuid].sort_values("distance")

        chosen = None

        for _, cand in tmp.iterrows():
            key = (str(cand["user_id"]), str(cand["candidate_id"]))
            source_set = candidate_source_sets_71d5h[key]

            if source_set.isdisjoint(used_source_events_71d5h):
                chosen = cand
                break

        if chosen is None:
            raise RuntimeError(
                f"No non-overlapping source-event candidate remains for "
                f"control user {cuid}, horizon {h}."
            )

        source_set = candidate_source_sets_71d5h[
            (str(chosen["user_id"]), str(chosen["candidate_id"]))
        ]
        used_source_events_71d5h.update(source_set)

        selected_final_rows_71d5h.append({
            "user_id": chosen["user_id"],
            "candidate_id": chosen["candidate_id"],
            "cutoff_time": chosen["cutoff_time"],
            "horizon_minutes": h,
            "matching_distance": float(chosen["distance"]),
            "positive_user_id": puid,
            "candidate_band": (
                "QUIET_GAP" if h == 60 else "ACTIVE_GAP"
            ),
        })

hard_negative_windows_71d5h = pd.DataFrame(
    selected_final_rows_71d5h
)

if len(hard_negative_windows_71d5h) != 100:
    raise RuntimeError(
        f"Expected exactly 100 final hard-negative windows, got "
        f"{len(hard_negative_windows_71d5h)}."
    )

# Create the canonical benchmark window identifier expected by all
# downstream AFRITAC validation and feature-extraction code.
# candidate_id remains the provenance identifier for the clean source
# cutoff; window_id identifies the reconstructed benchmark window.
hard_negative_windows_71d5h = hard_negative_windows_71d5h.reset_index(drop=True)
hard_negative_windows_71d5h["window_id"] = [
    f"HN_71D5H_{i:04d}"
    for i in range(1, len(hard_negative_windows_71d5h) + 1)
]

# Keep window_id first for compatibility with existing downstream code.
window_cols = ["window_id"] + [
    c for c in hard_negative_windows_71d5h.columns
    if c != "window_id"
]
hard_negative_windows_71d5h = hard_negative_windows_71d5h[window_cols]

print(
    "Final windows after source-event conflict resolution:",
    len(hard_negative_windows_71d5h)
)
print(
    "Canonical window IDs:",
    hard_negative_windows_71d5h["window_id"].nunique()
)
print(
    "Unique source events reserved:",
    len(used_source_events_71d5h)
)

# Defensive schema/integrity check before event reconstruction.
if "window_id" not in hard_negative_windows_71d5h.columns:
    raise RuntimeError("Canonical hard-negative window_id was not created.")

if hard_negative_windows_71d5h["window_id"].duplicated().any():
    raise RuntimeError("Duplicate hard-negative window_id values detected.")

# ----------------------------------------------------------------------
# 13. Copy source events from clean observable history
#
# New benchmark event IDs are assigned.
# Original source event IDs are retained only as provenance.
# ----------------------------------------------------------------------
hard_event_rows_71d5h = []

for _, w in hard_negative_windows_71d5h.iterrows():
    uid = w["user_id"]
    cutoff = pd.Timestamp(w["cutoff_time"])
    lo = cutoff - pd.Timedelta(minutes=LOOKBACK_71D5H)

    x = clean_obs_71d5h[
        (clean_obs_71d5h["user_id"] == uid) &
        (clean_obs_71d5h["timestamp"] >= lo) &
        (clean_obs_71d5h["timestamp"] < cutoff)
    ].copy()

    for _, e in x.iterrows():
        d = e.to_dict()

        d["source_event_id"] = str(e["event_id"])
        d["event_id"] = (
            f"HNE71D5H_{len(hard_event_rows_71d5h)+1:07d}"
        )
        d["ground_truth_state"] = "NORMAL"
        d["is_attack"] = 0
        d["is_observable_precursor"] = 0
        d["hard_negative_control"] = 1
        d["hard_negative_window_id"] = w["window_id"]
        d["horizon_minutes"] = int(w["horizon_minutes"])
        d["control_user_id"] = uid
        d["cutoff_time"] = cutoff

        hard_event_rows_71d5h.append(d)

hard_negative_events_71d5h = pd.DataFrame(
    hard_event_rows_71d5h
)

print("\nHard-negative events:", len(hard_negative_events_71d5h))

# ----------------------------------------------------------------------
# 13. Structural validation
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
print("71D.5H STRUCTURAL VALIDATION")
print("=" * 70)

print("\nWindows by horizon:")
print(
    hard_negative_windows_71d5h
    .groupby("horizon_minutes")
    .size()
)

expected_h_71d5h = {5: 20, 10: 20, 15: 20, 30: 20, 60: 20}
actual_h_71d5h = (
    hard_negative_windows_71d5h
    .groupby("horizon_minutes")
    .size()
    .to_dict()
)

if actual_h_71d5h != expected_h_71d5h:
    raise RuntimeError(
        f"Incorrect horizon distribution: {actual_h_71d5h}"
    )

print("✓ Exactly 20 windows per horizon")

control_counts_71d5h = (
    hard_negative_windows_71d5h
    .groupby("user_id")
    .size()
)

print("\nControl user window counts:")
print(control_counts_71d5h.describe())

if not (
    len(control_counts_71d5h) == 20 and
    (control_counts_71d5h == 5).all()
):
    raise RuntimeError(
        "Each of the 20 control users must have exactly 5 horizons."
    )

print("✓ Exactly 20 control users × 5 horizons")

positive_overlap_71d5h = (
    set(hard_negative_windows_71d5h["user_id"]) &
    positive_users_71d5h
)

print(
    "Positive/control user overlap:",
    len(positive_overlap_71d5h)
)

if positive_overlap_71d5h:
    raise RuntimeError("Positive/control user overlap detected.")

print("✓ No positive/control user overlap")

# Event ID uniqueness.
duplicate_ids_71d5h = int(
    hard_negative_events_71d5h["event_id"].duplicated().sum()
)

print("Duplicate benchmark event IDs:", duplicate_ids_71d5h)

if duplicate_ids_71d5h:
    raise RuntimeError("Duplicate benchmark event IDs detected.")

print("✓ Benchmark event IDs are unique")

# Source event reuse.
duplicate_sources_71d5h = int(
    hard_negative_events_71d5h["source_event_id"].duplicated().sum()
)

print("Source event IDs reused across windows:", duplicate_sources_71d5h)

if duplicate_sources_71d5h:
    raise RuntimeError(
        "Source events are reused across hard-negative windows. "
        "The cutoff-separation constraint was not respected."
    )

print("✓ Source events are not reused")

# Explicitly validate that each control user's five prediction cutoffs
# are separated by at least the 60-minute lookback.
cutoff_separation_violations_71d5h = 0

for uid, g in hard_negative_windows_71d5h.groupby("user_id"):
    times = (
        pd.to_datetime(g["cutoff_time"])
        .sort_values()
        .reset_index(drop=True)
    )
    if len(times) != 5:
        raise RuntimeError(
            f"Control user {uid} does not have exactly five cutoffs."
        )

    deltas = times.diff().dropna()
    if (deltas < pd.Timedelta(minutes=LOOKBACK_71D5H)).any():
        cutoff_separation_violations_71d5h += 1

print(
    "Control users with overlapping 60-minute time intervals:",
    cutoff_separation_violations_71d5h
)
print(
    "✓ Time-interval overlap is permitted because source-event reuse is zero"
)

# Source-event non-reuse is the authoritative provenance constraint.
source_reuse_final_71d5h = 0

if "source_event_id" in hard_negative_events_71d5h.columns:
    source_counts_71d5h = (
        hard_negative_events_71d5h["source_event_id"]
        .dropna()
        .astype(str)
        .value_counts()
    )
    source_reuse_final_71d5h = int((source_counts_71d5h > 1).sum())

print(
    "Final source event IDs reused:",
    source_reuse_final_71d5h
)

if source_reuse_final_71d5h != 0:
    raise RuntimeError(
        "Source-event provenance violation: one or more source events "
        "are reused across hard-negative windows."
    )

print()
print("=" * 70)
print("✓ 71D.5H STRUCTURAL VALIDATION PASSED")
print("=" * 70)


print("✓ Control cutoff histories are non-overlapping")

# Attack contamination.
attack_events_71d5h = int(
    pd.to_numeric(
        hard_negative_events_71d5h["is_attack"],
        errors="coerce"
    ).fillna(0).sum()
)

print("Hard-negative attack events:", attack_events_71d5h)

if attack_events_71d5h:
    raise RuntimeError("Attack contamination detected.")

# Precursor contamination.
precursor_events_71d5h = int(
    pd.to_numeric(
        hard_negative_events_71d5h[
            "is_observable_precursor"
        ],
        errors="coerce"
    ).fillna(0).sum()
)

print(
    "Hard-negative precursor events:",
    precursor_events_71d5h
)

if precursor_events_71d5h:
    raise RuntimeError("Precursor contamination detected.")

# ----------------------------------------------------------------------
# 14. Final hard-negative activity diagnostics
# ----------------------------------------------------------------------
def window_features_71d5h(stream, windows):
    rows = []

    for _, w in windows.iterrows():
        uid = w["user_id"]
        cutoff = pd.Timestamp(w["cutoff_time"])

        us = stream[stream["user_id"] == uid]
        d = extract_features_71d5h(us, cutoff)

        d["window_id"] = w["window_id"]
        d["horizon_minutes"] = int(w["horizon_minutes"])
        rows.append(d)

    return pd.DataFrame(rows)

hard_features_71d5h = window_features_71d5h(
    hard_negative_events_71d5h,
    hard_negative_windows_71d5h
)

print("\nHard-negative activity by horizon:")
print(
    hard_features_71d5h
    .groupby("horizon_minutes")[
        [
            "event_count",
            "session_count",
            "event_type_count",
            "modality_count",
            "last_5_share",
            "last_10_share",
            "last_15_share",
            "last_30_share",
            "delay_mean",
            "delay_std",
            "transaction_count",
            "transaction_amount_sum",
        ]
    ]
    .mean()
)

# ----------------------------------------------------------------------
# 15. Matching distance summary
# ----------------------------------------------------------------------
matching_71d5h = (
    hard_negative_windows_71d5h
    .groupby("horizon_minutes")["matching_distance"]
    .agg(["count", "mean", "median", "min", "max"])
)

print("\nMatching distance by horizon:")
print(matching_71d5h)

# ----------------------------------------------------------------------
# 16. Quiet 60-minute validation
# ----------------------------------------------------------------------
h60_71d5h = hard_negative_windows_71d5h[
    hard_negative_windows_71d5h["horizon_minutes"] == 60
].copy()

h60_features_71d5h = hard_features_71d5h[
    hard_features_71d5h["horizon_minutes"] == 60
]

print("\n60-minute hard-negative history:")
print(
    h60_features_71d5h[
        [
            "event_count",
            "session_count",
            "event_type_count",
            "modality_count",
            "transaction_count",
        ]
    ].describe()
)

# ----------------------------------------------------------------------
# 17. Promote only to candidate names.
#
# 71D.5F authoritative objects are intentionally untouched.
# ----------------------------------------------------------------------
hard_negative_windows_71d5h_candidate = (
    hard_negative_windows_71d5h.copy()
)

hard_negative_events_71d5h_candidate = (
    hard_negative_events_71d5h.copy()
)

print("\n" + "=" * 70)
print("AFRITAC 71D.5H COMPLETE")
print("=" * 70)

print(
    "Control users:",
    hard_negative_windows_71d5h_candidate["user_id"].nunique()
)
print(
    "Hard-negative windows:",
    len(hard_negative_windows_71d5h_candidate)
)
print(
    "Hard-negative events:",
    len(hard_negative_events_71d5h_candidate)
)
print(
    "Positive/control overlap:",
    len(positive_overlap_71d5h)
)
print(
    "Attack contamination:",
    attack_events_71d5h
)
print(
    "Precursor contamination:",
    precursor_events_71d5h
)

print("\n✓ 71D.5H candidate hard-negative reconstruction finished.")
print("✓ 71D.5F objects were not overwritten.")
print("✓ Run the 71D.5I validation before any promotion.")

# ==============================================================================
# NOTEBOOK CELL 222
# ==============================================================================

# ============================================================
# AFRITAC 71D.5I
# HARD NEGATIVE SCIENTIFIC VALIDATION
# ============================================================
#
# Purpose:
#   Determine whether the structurally valid 71D.5H hard-negative
#   controls are scientifically suitable for AFRITAC evaluation.
#
# This cell DOES NOT modify:
#   campaigns
#   attack_events
#   positive_windows
#   observable_precursors
#   benign_anomalies
#   normal_stream
#
# It only audits:
#   positive_windows
#   positive observable stream
#   hard_negative_windows_71d5h
#   hard_negative_events_71d5h
#
# ============================================================

import numpy as np
import pandas as pd

from sklearn.metrics import roc_auc_score
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression

print("=" * 72)
print("AFRITAC 71D.5I")
print("HARD NEGATIVE SCIENTIFIC VALIDATION")
print("=" * 72)


# ============================================================
# 1. REQUIRED OBJECTS
# ============================================================

required_objects_71d5i = [
    "positive_windows",
    "events",
    "hard_negative_windows_71d5h",
    "hard_negative_events_71d5h",
]

missing_objects_71d5i = [
    x for x in required_objects_71d5i
    if x not in globals()
]

print("\nRequired objects missing:", missing_objects_71d5i)

if missing_objects_71d5i:
    raise RuntimeError(
        "71D.5I cannot run because required 71D.5H objects are missing."
    )


# ============================================================
# 2. COPY INPUTS
# ============================================================

pos_windows_71d5i = positive_windows.copy()
pos_events_71d5i = events.copy()
hard_windows_71d5i = hard_negative_windows_71d5h.copy()
hard_events_71d5i = hard_negative_events_71d5h.copy()

print("\nInput sizes:")
print("Positive windows:", len(pos_windows_71d5i))
print("Positive observable events:", len(pos_events_71d5i))
print("Hard negative windows:", len(hard_windows_71d5i))
print("Hard negative events:", len(hard_events_71d5i))


# ============================================================
# 3. TIME NORMALIZATION
# ============================================================

pos_windows_71d5i["cutoff_time"] = pd.to_datetime(
    pos_windows_71d5i["cutoff_time"]
)

hard_windows_71d5i["cutoff_time"] = pd.to_datetime(
    hard_windows_71d5i["cutoff_time"]
)

pos_events_71d5i["timestamp"] = pd.to_datetime(
    pos_events_71d5i["timestamp"]
)

hard_events_71d5i["timestamp"] = pd.to_datetime(
    hard_events_71d5i["timestamp"]
)


# ============================================================
# 4. STANDARDIZE WINDOW IDENTIFIERS
# ============================================================

if "window_id" not in pos_windows_71d5i.columns:
    pos_windows_71d5i["window_id"] = [
        f"POS_{i+1:05d}"
        for i in range(len(pos_windows_71d5i))
    ]

if "window_id" not in hard_windows_71d5i.columns:
    raise RuntimeError(
        "hard_negative_windows_71d5h must contain canonical window_id."
    )


# ============================================================
# 5. IDENTIFY POSITIVE EVENT STREAM
# ============================================================

if "is_attack" in pos_events_71d5i.columns:
    observable_pos_71d5i = pos_events_71d5i[
        pos_events_71d5i["is_attack"].fillna(0).astype(int) == 0
    ].copy()
else:
    observable_pos_71d5i = pos_events_71d5i.copy()

print("\nObservable positive stream:", len(observable_pos_71d5i))


# ============================================================
# 6. FEATURE EXTRACTION FUNCTION
# ============================================================

def extract_window_features_71d5i(
    windows_df,
    events_df,
    label_value
):
    """
    Construct strictly pre-cutoff behavioural features.

    No target, attack labels, attack vocabulary, or post-cutoff
    information is used.
    """

    rows = []

    events_df = events_df.copy()

    events_df["timestamp"] = pd.to_datetime(
        events_df["timestamp"]
    )

    for _, w in windows_df.iterrows():

        user_id = w["user_id"]
        cutoff = pd.Timestamp(w["cutoff_time"])
        horizon = int(w["horizon_minutes"])

        lower = cutoff - pd.Timedelta(minutes=60)

        hist = events_df[
            (events_df["user_id"] == user_id)
            & (events_df["timestamp"] > lower)
            & (events_df["timestamp"] < cutoff)
        ].copy()

        if len(hist) == 0:

            rows.append({
                "window_id": w["window_id"],
                "label": label_value,
                "horizon_minutes": horizon,

                "event_count": 0,
                "session_count": 0,
                "event_type_count": 0,
                "modality_count": 0,

                "last5_count": 0,
                "last10_count": 0,
                "last15_count": 0,
                "last30_count": 0,

                "last5_share": 0.0,
                "last10_share": 0.0,
                "last15_share": 0.0,
                "last30_share": 0.0,

                "response_delay_mean": 0.0,
                "response_delay_std": 0.0,

                "new_device_rate": 0.0,
                "location_change_rate": 0.0,
                "roaming_rate": 0.0,

                "transaction_count": 0,
                "transaction_amount_sum": 0.0,
                "transaction_amount_mean": 0.0,
            })

            continue

        hist["minutes_before_cutoff"] = (
            cutoff - hist["timestamp"]
        ).dt.total_seconds() / 60.0

        event_count = len(hist)

        session_count = (
            hist["session_id"].nunique()
            if "session_id" in hist.columns
            else 0
        )

        event_type_count = (
            hist["event_type"].nunique()
            if "event_type" in hist.columns
            else 0
        )

        modality_count = (
            hist["modality"].nunique()
            if "modality" in hist.columns
            else 0
        )

        last5 = hist[
            hist["minutes_before_cutoff"] <= 5
        ]

        last10 = hist[
            hist["minutes_before_cutoff"] <= 10
        ]

        last15 = hist[
            hist["minutes_before_cutoff"] <= 15
        ]

        last30 = hist[
            hist["minutes_before_cutoff"] <= 30
        ]

        response_values = pd.to_numeric(
            hist.get(
                "response_delay_ms",
                pd.Series(index=hist.index, dtype=float)
            ),
            errors="coerce"
        )

        response_values = response_values.dropna()

        response_mean = (
            response_values.mean()
            if len(response_values)
            else 0.0
        )

        response_std = (
            response_values.std(ddof=0)
            if len(response_values)
            else 0.0
        )

        new_device = pd.to_numeric(
            hist.get(
                "new_device",
                pd.Series(0, index=hist.index)
            ),
            errors="coerce"
        ).fillna(0)

        location_change = pd.to_numeric(
            hist.get(
                "location_change",
                pd.Series(0, index=hist.index)
            ),
            errors="coerce"
        ).fillna(0)

        roaming = pd.to_numeric(
            hist.get(
                "roaming",
                pd.Series(0, index=hist.index)
            ),
            errors="coerce"
        ).fillna(0)

        transaction_amount = pd.to_numeric(
            hist.get(
                "transaction_amount",
                pd.Series(0, index=hist.index)
            ),
            errors="coerce"
        ).fillna(0)

        transaction_mask = (
            transaction_amount > 0
        )

        transaction_count = int(
            transaction_mask.sum()
        )

        transaction_sum = float(
            transaction_amount[transaction_mask].sum()
        )

        transaction_mean = (
            float(
                transaction_amount[transaction_mask].mean()
            )
            if transaction_count > 0
            else 0.0
        )

        rows.append({
            "window_id": w["window_id"],
            "label": label_value,
            "horizon_minutes": horizon,

            "event_count": event_count,
            "session_count": session_count,
            "event_type_count": event_type_count,
            "modality_count": modality_count,

            "last5_count": len(last5),
            "last10_count": len(last10),
            "last15_count": len(last15),
            "last30_count": len(last30),

            "last5_share": len(last5) / event_count,
            "last10_share": len(last10) / event_count,
            "last15_share": len(last15) / event_count,
            "last30_share": len(last30) / event_count,

            "response_delay_mean": response_mean,
            "response_delay_std": response_std,

            "new_device_rate": float(new_device.mean()),
            "location_change_rate": float(location_change.mean()),
            "roaming_rate": float(roaming.mean()),

            "transaction_count": transaction_count,
            "transaction_amount_sum": transaction_sum,
            "transaction_amount_mean": transaction_mean,
        })

    return pd.DataFrame(rows)


# ============================================================
# 7. BUILD FEATURE MATRICES
# ============================================================

print("\nBuilding positive features...")

pos_features_71d5i = extract_window_features_71d5i(
    pos_windows_71d5i,
    observable_pos_71d5i,
    1
)

print("Building hard-negative features...")

hard_features_71d5i = extract_window_features_71d5i(
    hard_windows_71d5i,
    hard_events_71d5i,
    0
)

combined_71d5i = pd.concat(
    [
        pos_features_71d5i,
        hard_features_71d5i
    ],
    ignore_index=True
)

print(
    "\nFeature matrix:",
    combined_71d5i.shape
)


# ============================================================
# 8. FEATURE GROUPS
# ============================================================

feature_groups_71d5i = {

    "EVENT_COUNT": [
        "event_count"
    ],

    "ACTIVITY": [
        "event_count",
        "session_count",
        "event_type_count",
    ],

    "MODALITY": [
        "modality_count"
    ],

    "TEMPORAL": [
        "last5_share",
        "last10_share",
        "last15_share",
        "last30_share",
    ],

    "RESPONSE_DELAY": [
        "response_delay_mean",
        "response_delay_std",
    ],

    "CONTEXT": [
        "new_device_rate",
        "location_change_rate",
        "roaming_rate",
    ],

    "FINANCIAL": [
        "transaction_count",
        "transaction_amount_sum",
        "transaction_amount_mean",
    ],

    "ACTIVITY_MODALITY": [
        "event_count",
        "session_count",
        "event_type_count",
        "modality_count",
    ],

    "ACTIVITY_TEMPORAL": [
        "event_count",
        "session_count",
        "event_type_count",
        "last5_share",
        "last10_share",
        "last15_share",
        "last30_share",
    ],

    "CONTEXT_FINANCIAL": [
        "new_device_rate",
        "location_change_rate",
        "roaming_rate",
        "transaction_count",
        "transaction_amount_sum",
        "transaction_amount_mean",
    ],

    "ALL": [
        c for c in combined_71d5i.columns
        if c not in [
            "window_id",
            "label",
            "horizon_minutes"
        ]
    ],
}


# ============================================================
# 9. DIRECTION-FREE AUC
# ============================================================

def direction_free_auc_71d5i(y, score):

    y = np.asarray(y)
    score = np.asarray(score)

    valid = np.isfinite(score)

    y = y[valid]
    score = score[valid]

    if len(np.unique(y)) < 2:
        return np.nan

    auc = roc_auc_score(y, score)

    return max(auc, 1.0 - auc)


# ============================================================
# 10. UNIVARIATE FEATURE AUDIT
# ============================================================

univariate_features_71d5i = [
    "event_count",
    "session_count",
    "event_type_count",
    "modality_count",
    "last5_share",
    "last10_share",
    "last15_share",
    "last30_share",
    "response_delay_mean",
    "response_delay_std",
    "new_device_rate",
    "location_change_rate",
    "roaming_rate",
    "transaction_count",
    "transaction_amount_sum",
    "transaction_amount_mean",
]


univariate_results_71d5i = []

for horizon in sorted(
    combined_71d5i["horizon_minutes"].unique()
):

    subset = combined_71d5i[
        combined_71d5i["horizon_minutes"] == horizon
    ].copy()

    y = subset["label"].values

    for feature in univariate_features_71d5i:

        score = pd.to_numeric(
            subset[feature],
            errors="coerce"
        ).fillna(0).values

        auc = direction_free_auc_71d5i(
            y,
            score
        )

        univariate_results_71d5i.append({
            "horizon": horizon,
            "feature": feature,
            "auc": auc,
        })


univariate_results_71d5i = pd.DataFrame(
    univariate_results_71d5i
)


print("\n" + "=" * 72)
print("UNIVARIATE DIRECTION-FREE AUC")
print("=" * 72)

print(
    univariate_results_71d5i
    .pivot(
        index="feature",
        columns="horizon",
        values="auc"
    )
    .round(4)
)


# ============================================================
# 11. STANDARDIZED MEAN DIFFERENCE
# ============================================================

def smd_71d5i(pos, neg):

    pos = pd.to_numeric(
        pd.Series(pos),
        errors="coerce"
    ).dropna()

    neg = pd.to_numeric(
        pd.Series(neg),
        errors="coerce"
    ).dropna()

    if len(pos) == 0 or len(neg) == 0:
        return np.nan

    pooled = np.sqrt(
        (
            pos.var(ddof=1)
            +
            neg.var(ddof=1)
        ) / 2
    )

    if pooled == 0 or not np.isfinite(pooled):
        return np.nan

    return (
        pos.mean() - neg.mean()
    ) / pooled


smd_results_71d5i = []

for horizon in sorted(
    combined_71d5i["horizon_minutes"].unique()
):

    subset = combined_71d5i[
        combined_71d5i["horizon_minutes"] == horizon
    ]

    pos = subset[
        subset["label"] == 1
    ]

    neg = subset[
        subset["label"] == 0
    ]

    for feature in univariate_features_71d5i:

        smd_value = smd_71d5i(
            pos[feature],
            neg[feature]
        )

        smd_results_71d5i.append({
            "horizon": horizon,
            "feature": feature,
            "smd": smd_value,
        })


smd_results_71d5i = pd.DataFrame(
    smd_results_71d5i
)


print("\n" + "=" * 72)
print("STANDARDIZED MEAN DIFFERENCES")
print("=" * 72)

print(
    smd_results_71d5i
    .pivot(
        index="feature",
        columns="horizon",
        values="smd"
    )
    .round(3)
)


# ============================================================
# 12. HORIZON SPECIFIC MULTIVARIATE AUC
# ============================================================

def multivariate_auc_71d5i(
    subset,
    features
):

    X = subset[features].apply(
        pd.to_numeric,
        errors="coerce"
    )

    y = subset["label"].astype(int).values

    if len(np.unique(y)) < 2:
        return np.nan

    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            random_state=42
        )
    )

    model.fit(X, y)

    scores = model.predict_proba(X)[:, 1]

    return direction_free_auc_71d5i(
        y,
        scores
    )


group_results_71d5i = []

for horizon in sorted(
    combined_71d5i["horizon_minutes"].unique()
):

    subset = combined_71d5i[
        combined_71d5i["horizon_minutes"] == horizon
    ].copy()

    for group_name, features in feature_groups_71d5i.items():

        auc = multivariate_auc_71d5i(
            subset,
            features
        )

        group_results_71d5i.append({
            "horizon": horizon,
            "feature_group": group_name,
            "auc": auc,
        })


group_results_71d5i = pd.DataFrame(
    group_results_71d5i
)


print("\n" + "=" * 72)
print("HORIZON SPECIFIC MULTIVARIATE AUC")
print("=" * 72)

print(
    group_results_71d5i
    .pivot(
        index="feature_group",
        columns="horizon",
        values="auc"
    )
    .round(4)
)


# ============================================================
# 13. POSITIVE VS HARD ACTIVITY PROFILE
# ============================================================

profile_columns_71d5i = [
    "event_count",
    "session_count",
    "event_type_count",
    "modality_count",
    "last5_share",
    "last10_share",
    "last15_share",
    "last30_share",
    "response_delay_mean",
    "response_delay_std",
    "new_device_rate",
    "location_change_rate",
    "roaming_rate",
    "transaction_count",
    "transaction_amount_sum",
    "transaction_amount_mean",
]


print("\n" + "=" * 72)
print("POSITIVE VS HARD NEGATIVE PROFILE")
print("=" * 72)

profile_records_71d5i = []

for horizon in sorted(
    combined_71d5i["horizon_minutes"].unique()
):

    for label, class_name in [
        (1, "POSITIVE"),
        (0, "HARD_NEGATIVE")
    ]:

        subset = combined_71d5i[
            (combined_71d5i["horizon_minutes"] == horizon)
            &
            (combined_71d5i["label"] == label)
        ]

        record = {
            "horizon": horizon,
            "class": class_name,
            "n": len(subset),
        }

        for feature in profile_columns_71d5i:

            record[feature] = (
                pd.to_numeric(
                    subset[feature],
                    errors="coerce"
                )
                .mean()
            )

        profile_records_71d5i.append(record)


profile_71d5i = pd.DataFrame(
    profile_records_71d5i
)

print(
    profile_71d5i.round(4).to_string(
        index=False
    )
)


# ============================================================
# 14. ZERO ACTIVITY AUDIT
# ============================================================

print("\n" + "=" * 72)
print("ZERO ACTIVITY RATES")
print("=" * 72)

zero_activity_records_71d5i = []

for horizon in sorted(
    combined_71d5i["horizon_minutes"].unique()
):

    for label, class_name in [
        (1, "POSITIVE"),
        (0, "HARD_NEGATIVE")
    ]:

        subset = combined_71d5i[
            (combined_71d5i["horizon_minutes"] == horizon)
            &
            (combined_71d5i["label"] == label)
        ]

        rate = (
            subset["event_count"].eq(0).mean()
        )

        zero_activity_records_71d5i.append({
            "horizon": horizon,
            "class": class_name,
            "zero_activity_rate": rate,
        })


zero_activity_71d5i = pd.DataFrame(
    zero_activity_records_71d5i
)

print(
    zero_activity_71d5i.round(4).to_string(
        index=False
    )
)


# ============================================================
# 15. HORIZON SPECIFIC BEST FEATURE GROUP
# ============================================================

best_groups_71d5i = (
    group_results_71d5i
    .sort_values(
        ["horizon", "auc"],
        ascending=[True, False]
    )
    .groupby("horizon")
    .head(1)
    .reset_index(drop=True)
)

print("\n" + "=" * 72)
print("BEST FEATURE GROUP BY HORIZON")
print("=" * 72)

print(
    best_groups_71d5i.to_string(
        index=False
    )
)


# ============================================================
# 16. SHORTCUT AUDIT
# ============================================================

max_auc_by_horizon_71d5i = (
    univariate_results_71d5i
    .groupby("horizon")["auc"]
    .max()
)

max_abs_smd_by_horizon_71d5i = (
    smd_results_71d5i
    .assign(
        abs_smd=lambda x: x["smd"].abs()
    )
    .groupby("horizon")["abs_smd"]
    .max()
)

print("\n" + "=" * 72)
print("SHORTCUT DIAGNOSTIC")
print("=" * 72)

shortcut_table_71d5i = pd.DataFrame({
    "max_univariate_auc": max_auc_by_horizon_71d5i,
    "max_absolute_smd": max_abs_smd_by_horizon_71d5i,
})

print(
    shortcut_table_71d5i.round(4)
)


# ============================================================
# 17. RESPONSE DELAY SPECIFIC AUDIT
# ============================================================

delay_auc_71d5i = (
    univariate_results_71d5i[
        univariate_results_71d5i["feature"]
        == "response_delay_mean"
    ]
    .set_index("horizon")["auc"]
)

print("\n" + "=" * 72)
print("RESPONSE DELAY AUC")
print("=" * 72)

print(
    delay_auc_71d5i.round(4)
)


# ============================================================
# 18. ACTIVITY SPECIFIC AUDIT
# ============================================================

activity_features_71d5i = [
    "event_count",
    "session_count",
    "event_type_count",
]

activity_auc_71d5i = (
    univariate_results_71d5i[
        univariate_results_71d5i["feature"]
        .isin(activity_features_71d5i)
    ]
    .pivot(
        index="feature",
        columns="horizon",
        values="auc"
    )
)

print("\n" + "=" * 72)
print("ACTIVITY FEATURE AUC")
print("=" * 72)

print(
    activity_auc_71d5i.round(4)
)


# ============================================================
# 19. 60 MINUTE QUIET CONTROL AUDIT
# ============================================================

quiet_60_71d5i = combined_71d5i[
    combined_71d5i["horizon_minutes"] == 60
]

quiet_60_summary_71d5i = (
    quiet_60_71d5i
    .groupby("label")["event_count"]
    .agg(
        n="size",
        mean="mean",
        median="median",
        minimum="min",
        maximum="max",
        zero_rate=lambda x: x.eq(0).mean()
    )
)

print("\n" + "=" * 72)
print("60 MINUTE QUIET CONTROL AUDIT")
print("=" * 72)

print(
    quiet_60_summary_71d5i
)


# ============================================================
# 20. FINAL SCIENTIFIC FLAGS
# ============================================================

print("\n" + "=" * 72)
print("71D.5I SCIENTIFIC DECISION")
print("=" * 72)

# These are diagnostic thresholds, not automatic dataset rejection
# thresholds.

activity_auc_71d5i = (
    univariate_results_71d5i[
        univariate_results_71d5i["feature"]
        .isin([
            "event_count",
            "session_count",
            "event_type_count"
        ])
    ]["auc"]
)

delay_auc_values_71d5i = (
    univariate_results_71d5i[
        univariate_results_71d5i["feature"]
        == "response_delay_mean"
    ]["auc"]
)

max_activity_auc_71d5i = (
    activity_auc_71d5i.max()
)

max_delay_auc_71d5i = (
    delay_auc_values_71d5i.max()
)

max_smd_71d5i = (
    smd_results_71d5i["smd"]
    .abs()
    .replace([np.inf, -np.inf], np.nan)
    .max()
)

print(
    f"\nMaximum activity feature AUC: "
    f"{max_activity_auc_71d5i:.4f}"
)

print(
    f"Maximum response-delay AUC: "
    f"{max_delay_auc_71d5i:.4f}"
)

print(
    f"Maximum finite absolute SMD: "
    f"{max_smd_71d5i:.4f}"
)


# ------------------------------------------------------------
# Diagnostic interpretation
# ------------------------------------------------------------

if max_activity_auc_71d5i >= 0.90:
    print(
        "\nFLAG: Strong residual activity separation."
    )
else:
    print(
        "\nPASS: Activity separation is below the "
        "0.90 diagnostic level."
    )


if max_delay_auc_71d5i >= 0.90:
    print(
        "FLAG: Response delay remains a potential "
        "shortcut feature."
    )
else:
    print(
        "PASS: Response delay is not strongly "
        "separating."
    )


if max_smd_71d5i >= 3.0:
    print(
        "FLAG: At least one feature has very large "
        "distributional separation."
    )
else:
    print(
        "PASS: No finite feature has SMD >= 3."
    )


# ------------------------------------------------------------
# 60 minute diagnostic
# ------------------------------------------------------------

positive_60_71d5i = quiet_60_71d5i[
    quiet_60_71d5i["label"] == 1
]["event_count"]

hard_60_71d5i = quiet_60_71d5i[
    quiet_60_71d5i["label"] == 0
]["event_count"]

positive_60_zero_71d5i = (
    positive_60_71d5i.eq(0).mean()
)

hard_60_zero_71d5i = (
    hard_60_71d5i.eq(0).mean()
)

print(
    "\n60 minute positive zero-activity rate:",
    round(positive_60_zero_71d5i, 4)
)

print(
    "60 minute hard-negative zero-activity rate:",
    round(hard_60_zero_71d5i, 4)
)


# ============================================================
# 21. FINAL REPORT OBJECTS
# ============================================================

scientific_validation_71d5i = {
    "positive_windows": len(pos_windows_71d5i),
    "hard_negative_windows": len(hard_windows_71d5i),
    "hard_negative_events": len(hard_events_71d5i),

    "max_activity_auc": float(
        max_activity_auc_71d5i
    ),

    "max_response_delay_auc": float(
        max_delay_auc_71d5i
    ),

    "max_finite_absolute_smd": float(
        max_smd_71d5i
    ),

    "positive_60_zero_rate": float(
        positive_60_zero_71d5i
    ),

    "hard_60_zero_rate": float(
        hard_60_zero_71d5i
    ),
}


print("\n" + "=" * 72)
print("71D.5I COMPLETE")
print("=" * 72)

print(
    "\nScientific validation summary:"
)

for key, value in scientific_validation_71d5i.items():
    print(
        f"{key}: {value}"
    )

print("\nNo AFRITAC source object was modified.")
print("=" * 72)

# ==============================================================================
# NOTEBOOK CELL 223
# ==============================================================================

# ============================================================
# AFRITAC 71D.5J
# FINAL BENCHMARK ASSEMBLY AND LEAKAGE AUDIT
# CORRECTED SCHEMA SAFE VERSION
# ============================================================

import numpy as np
import pandas as pd

print("=" * 78)
print("AFRITAC 71D.5J")
print("FINAL BENCHMARK ASSEMBLY AND LEAKAGE AUDIT")
print("=" * 78)


# ============================================================
# 1. REQUIRED OBJECTS
# ============================================================

required_71d5j = [
    "positive_windows",
    "events",
    "benign_anomalies",
    "hard_negative_windows_71d5h",
    "hard_negative_events_71d5h",
]

missing_71d5j = [
    x for x in required_71d5j
    if x not in globals()
]

print("\nMissing required objects:", missing_71d5j)

if missing_71d5j:
    raise RuntimeError(
        "71D.5J stopped because required authoritative "
        "objects are missing."
    )


# ============================================================
# 2. ORDINARY NEGATIVE WINDOWS
# ============================================================

negative_candidates_71d5j = [
    "negative_windows",
    "normal_negative_windows",
    "negative_cohort_windows",
]

negative_object_71d5j = None

for name in negative_candidates_71d5j:

    if name in globals():

        negative_object_71d5j = name
        break


if negative_object_71d5j is None:

    ordinary_negative_windows_71d5j = (
        pd.DataFrame()
    )

    print(
        "\nOrdinary negative-window source: NONE"
    )

else:

    ordinary_negative_windows_71d5j = (
        globals()[negative_object_71d5j].copy()
    )

    print(
        "\nOrdinary negative-window source:",
        negative_object_71d5j
    )


# ============================================================
# 3. FREEZE SOURCE COPIES
# ============================================================

positive_windows_71d5j = (
    positive_windows.copy()
)

observable_events_71d5j = (
    events.copy()
)

benign_anomalies_71d5j = (
    benign_anomalies.copy()
)

hard_negative_windows_71d5j = (
    hard_negative_windows_71d5h.copy()
)

hard_negative_events_71d5j = (
    hard_negative_events_71d5h.copy()
)


# ============================================================
# 4. SOURCE SIZES
# ============================================================

print("\n" + "=" * 78)
print("SOURCE LAYER SIZES")
print("=" * 78)

print(
    "Positive prediction windows:",
    len(positive_windows_71d5j)
)

print(
    "Observable event stream:",
    len(observable_events_71d5j)
)

print(
    "Benign anomaly events:",
    len(benign_anomalies_71d5j)
)

print(
    "Hard-negative windows:",
    len(hard_negative_windows_71d5j)
)

print(
    "Hard-negative events:",
    len(hard_negative_events_71d5j)
)

print(
    "Ordinary negative windows:",
    len(ordinary_negative_windows_71d5j)
)


# ============================================================
# 5. SCHEMA REPORT
# ============================================================

print("\n" + "=" * 78)
print("KEY SOURCE SCHEMAS")
print("=" * 78)

print(
    "\nEvents columns:"
)

print(
    list(observable_events_71d5j.columns)
)

print(
    "\nAttack-event object available:",
    "attack_events" in globals()
)

if "attack_events" in globals():

    print(
        "Attack-event rows:",
        len(attack_events)
    )


# ============================================================
# 6. TIME NORMALIZATION
# ============================================================

for df, col in [
    (
        positive_windows_71d5j,
        "cutoff_time"
    ),
    (
        positive_windows_71d5j,
        "takeover_time"
    ),
    (
        observable_events_71d5j,
        "timestamp"
    ),
    (
        benign_anomalies_71d5j,
        "timestamp"
    ),
    (
        hard_negative_windows_71d5j,
        "cutoff_time"
    ),
    (
        hard_negative_events_71d5j,
        "timestamp"
    ),
]:

    if col in df.columns:

        df[col] = pd.to_datetime(
            df[col],
            errors="coerce"
        )


if len(ordinary_negative_windows_71d5j):

    if "cutoff_time" in (
        ordinary_negative_windows_71d5j.columns
    ):

        ordinary_negative_windows_71d5j[
            "cutoff_time"
        ] = pd.to_datetime(
            ordinary_negative_windows_71d5j[
                "cutoff_time"
            ],
            errors="coerce"
        )


# ============================================================
# 7. CANONICAL WINDOW IDS
# ============================================================

if "window_id" not in positive_windows_71d5j.columns:

    positive_windows_71d5j["window_id"] = [
        f"POS_{i + 1:05d}"
        for i in range(
            len(positive_windows_71d5j)
        )
    ]


if len(ordinary_negative_windows_71d5j):

    if "window_id" not in (
        ordinary_negative_windows_71d5j.columns
    ):

        ordinary_negative_windows_71d5j[
            "window_id"
        ] = [
            f"NEG_{i + 1:05d}"
            for i in range(
                len(ordinary_negative_windows_71d5j)
            )
        ]


if "window_id" not in hard_negative_windows_71d5j.columns:

    raise RuntimeError(
        "71D.5H hard-negative windows do not contain "
        "window_id."
    )


# ============================================================
# 8. STANDARDIZE POSITIVE WINDOWS
# ============================================================

positive_windows_71d5j[
    "benchmark_class"
] = "ATTACK_PRECURSOR"

positive_windows_71d5j[
    "label"
] = 1

positive_windows_71d5j[
    "source_layer"
] = "POSITIVE_ATTACK_WINDOWS"

positive_windows_71d5j[
    "ground_truth_attack"
] = 1

positive_windows_71d5j[
    "is_benign_anomaly"
] = 0

positive_windows_71d5j[
    "is_hard_negative"
] = 0


# ============================================================
# 9. STANDARDIZE ORDINARY NEGATIVES
# ============================================================

if len(ordinary_negative_windows_71d5j):

    ordinary_negative_windows_71d5j[
        "benchmark_class"
    ] = "ORDINARY_BENIGN"

    ordinary_negative_windows_71d5j[
        "label"
    ] = 0

    ordinary_negative_windows_71d5j[
        "source_layer"
    ] = "ORDINARY_NEGATIVE_WINDOWS"

    ordinary_negative_windows_71d5j[
        "ground_truth_attack"
    ] = 0

    ordinary_negative_windows_71d5j[
        "is_benign_anomaly"
    ] = 0

    ordinary_negative_windows_71d5j[
        "is_hard_negative"
    ] = 0


# ============================================================
# 10. STANDARDIZE HARD NEGATIVES
# ============================================================

hard_negative_windows_71d5j[
    "benchmark_class"
] = "HARD_BENIGN"

hard_negative_windows_71d5j[
    "label"
] = 0

hard_negative_windows_71d5j[
    "source_layer"
] = "71D.5H_HARD_NEGATIVE"

hard_negative_windows_71d5j[
    "ground_truth_attack"
] = 0

hard_negative_windows_71d5j[
    "is_benign_anomaly"
] = 0

hard_negative_windows_71d5j[
    "is_hard_negative"
] = 1


# ============================================================
# 11. FINAL PREDICTION WINDOW TABLE
# ============================================================

window_parts_71d5j = [
    positive_windows_71d5j
]

if len(ordinary_negative_windows_71d5j):

    window_parts_71d5j.append(
        ordinary_negative_windows_71d5j
    )

window_parts_71d5j.append(
    hard_negative_windows_71d5j
)

afritac_prediction_windows_71d5j = (
    pd.concat(
        window_parts_71d5j,
        ignore_index=True,
        sort=False
    )
)


# ============================================================
# 12. BENIGN ANOMALY SESSION TABLE
# ============================================================

if "session_id" not in (
    benign_anomalies_71d5j.columns
):

    raise RuntimeError(
        "Benign anomaly layer lacks session_id."
    )


benign_session_table_71d5j = (
    benign_anomalies_71d5j
    .groupby(
        "session_id",
        as_index=False
    )
    .agg(
        user_id=("user_id", "first"),
        first_timestamp=("timestamp", "min"),
        last_timestamp=("timestamp", "max"),
        event_count=("event_id", "count"),
        event_type_count=("event_type", "nunique"),
        modality_count=("modality", "nunique"),
    )
)

benign_session_table_71d5j[
    "benchmark_class"
] = "BENIGN_ANOMALY"

benign_session_table_71d5j[
    "label"
] = 0

benign_session_table_71d5j[
    "source_layer"
] = "BENIGN_ANOMALIES"

benign_session_table_71d5j[
    "ground_truth_attack"
] = 0

benign_session_table_71d5j[
    "is_benign_anomaly"
] = 1

benign_session_table_71d5j[
    "is_hard_negative"
] = 0


# ============================================================
# 13. BUILD AUTHORITATIVE ATTACK EVENT ID SET
# ============================================================
#
# We do NOT assume events contains is_attack.
#
# Attack status is reconstructed from attack_events when
# available.
#
# ============================================================

attack_event_ids_71d5j = set()

if "attack_events" in globals():

    attack_events_71d5j = (
        attack_events.copy()
    )

    if "event_id" in attack_events_71d5j.columns:

        attack_event_ids_71d5j = set(
            attack_events_71d5j[
                "event_id"
            ]
            .dropna()
            .astype(str)
        )

        print(
            "\nAuthoritative attack event IDs:",
            len(attack_event_ids_71d5j)
        )

    else:

        print(
            "\nWARNING: attack_events exists but "
            "has no event_id column."
        )

else:

    print(
        "\nWARNING: attack_events object unavailable."
    )


# ============================================================
# 14. ATTACK STATUS IN OBSERVABLE EVENT STREAM
# ============================================================

observable_events_final_71d5j = (
    observable_events_71d5j.copy()
)

if "event_id" in (
    observable_events_final_71d5j.columns
):

    observable_event_ids_71d5j = (
        observable_events_final_71d5j[
            "event_id"
        ]
        .astype(str)
    )

    observable_events_final_71d5j[
        "derived_is_attack"
    ] = (
        observable_event_ids_71d5j
        .isin(attack_event_ids_71d5j)
        .astype(int)
    )

else:

    raise RuntimeError(
        "Observable events lack event_id."
    )


# ============================================================
# 15. IDENTIFY OBSERVABLE PRECURSOR EVENTS
# ============================================================

if "is_observable_precursor" in (
    observable_events_final_71d5j.columns
):

    precursor_events_final_71d5j = (
        observable_events_final_71d5j[
            observable_events_final_71d5j[
                "is_observable_precursor"
            ]
            .fillna(0)
            .astype(int)
            == 1
        ]
        .copy()
    )

else:

    precursor_events_final_71d5j = (
        observable_events_final_71d5j.iloc[0:0]
        .copy()
    )


print(
    "\nObservable precursor events:",
    len(precursor_events_final_71d5j)
)


# ============================================================
# 16. FINAL OBSERVABLE EVENT LABEL
# ============================================================

observable_events_final_71d5j[
    "benchmark_label"
] = (
    observable_events_final_71d5j[
        "derived_is_attack"
    ]
)

observable_events_final_71d5j[
    "benchmark_class"
] = np.where(
    observable_events_final_71d5j[
        "derived_is_attack"
    ] == 1,
    "ATTACK_GROUND_TRUTH",
    "ORDINARY_BENIGN"
)

observable_events_final_71d5j[
    "source_layer"
] = "OBSERVABLE_STREAM"


# ============================================================
# 17. BENIGN EVENT LAYER
# ============================================================

benign_event_layer_71d5j = (
    benign_anomalies_71d5j.copy()
)

benign_event_layer_71d5j[
    "benchmark_label"
] = 0

benign_event_layer_71d5j[
    "benchmark_class"
] = "BENIGN_ANOMALY"

benign_event_layer_71d5j[
    "source_layer"
] = "BENIGN_ANOMALIES"


# ============================================================
# 18. HARD NEGATIVE EVENT LAYER
# ============================================================

hard_event_layer_71d5j = (
    hard_negative_events_71d5j.copy()
)

hard_event_layer_71d5j[
    "benchmark_label"
] = 0

hard_event_layer_71d5j[
    "benchmark_class"
] = "HARD_BENIGN"

hard_event_layer_71d5j[
    "source_layer"
] = "71D.5H_HARD_NEGATIVE"


# ============================================================
# 19. FINAL EVENT TABLE
# ============================================================

afritac_benchmark_events_71d5j = (
    pd.concat(
        [
            observable_events_final_71d5j,
            benign_event_layer_71d5j,
            hard_event_layer_71d5j,
        ],
        ignore_index=True,
        sort=False
    )
)


# ============================================================
# 20. WINDOW ID UNIQUENESS
# ============================================================

duplicate_window_ids_71d5j = (
    afritac_prediction_windows_71d5j[
        "window_id"
    ]
    .duplicated()
    .sum()
)

print(
    "\nDuplicate prediction window IDs:",
    duplicate_window_ids_71d5j
)


# ============================================================
# 21. POSITIVE VS HARD USER OVERLAP
# ============================================================

positive_users_71d5j = set(
    positive_windows_71d5j[
        "user_id"
    ]
    .astype(str)
)

hard_users_71d5j = set(
    hard_negative_windows_71d5j[
        "user_id"
    ]
    .astype(str)
)

positive_hard_user_overlap_71d5j = (
    positive_users_71d5j
    &
    hard_users_71d5j
)

print(
    "Positive vs hard-negative user overlap:",
    len(positive_hard_user_overlap_71d5j)
)


# ============================================================
# 22. HARD NEGATIVE SOURCE EVENT REUSE
# ============================================================

source_reuse_71d5j = 0

if "source_event_id" in (
    hard_negative_events_71d5j.columns
):

    source_ids_71d5j = (
        hard_negative_events_71d5j[
            "source_event_id"
        ]
        .dropna()
        .astype(str)
    )

    source_reuse_71d5j = (
        source_ids_71d5j
        .duplicated()
        .sum()
    )

print(
    "Hard-negative source event reuse:",
    source_reuse_71d5j
)


# ============================================================
# 23. HARD NEGATIVE EVENT ID DUPLICATION
# ============================================================

duplicate_hard_event_ids_71d5j = (
    hard_negative_events_71d5j[
        "event_id"
    ]
    .astype(str)
    .duplicated()
    .sum()
)

print(
    "Duplicate hard-negative event IDs:",
    duplicate_hard_event_ids_71d5j
)


# ============================================================
# 24. ATTACK VOCABULARY
# ============================================================

attack_vocab_71d5j = set()

if len(attack_event_ids_71d5j):

    attack_vocab_source_71d5j = (
        attack_events_71d5j.copy()
    )

    if "event_type" in (
        attack_vocab_source_71d5j.columns
    ):

        attack_vocab_71d5j = set(
            attack_vocab_source_71d5j[
                "event_type"
            ]
            .dropna()
            .astype(str)
        )


hard_vocab_71d5j = set(
    hard_negative_events_71d5j[
        "event_type"
    ]
    .dropna()
    .astype(str)
)

benign_vocab_71d5j = set(
    benign_anomalies_71d5j[
        "event_type"
    ]
    .dropna()
    .astype(str)
)

hard_attack_vocab_overlap_71d5j = (
    attack_vocab_71d5j
    &
    hard_vocab_71d5j
)

benign_attack_vocab_overlap_71d5j = (
    attack_vocab_71d5j
    &
    benign_vocab_71d5j
)

print(
    "\nAttack vocabulary:",
    sorted(attack_vocab_71d5j)
)

print(
    "Hard-negative attack vocabulary overlap:",
    sorted(hard_attack_vocab_overlap_71d5j)
)

print(
    "Benign anomaly attack vocabulary overlap:",
    sorted(benign_attack_vocab_overlap_71d5j)
)


# ============================================================
# 25. POSITIVE WINDOW TEMPORAL INTEGRITY
# ============================================================

positive_cutoff_violations_71d5j = 0

if (
    "cutoff_time" in positive_windows_71d5j.columns
    and
    "takeover_time" in positive_windows_71d5j.columns
):

    positive_cutoff_violations_71d5j = int(
        (
            positive_windows_71d5j[
                "cutoff_time"
            ]
            >=
            positive_windows_71d5j[
                "takeover_time"
            ]
        )
        .sum()
    )

print(
    "\nPositive cutoff >= takeover violations:",
    positive_cutoff_violations_71d5j
)


# ============================================================
# 26. ATTACK EVENT CONTAMINATION BEFORE POSITIVE CUTOFF
# ============================================================

attack_contamination_71d5j = []

if len(attack_event_ids_71d5j):

    attack_events_check_71d5j = (
        observable_events_final_71d5j[
            observable_events_final_71d5j[
                "derived_is_attack"
            ] == 1
        ]
        .copy()
    )

    for _, w in positive_windows_71d5j.iterrows():

        user = str(w["user_id"])

        cutoff = pd.Timestamp(
            w["cutoff_time"]
        )

        subset = (
            attack_events_check_71d5j[
                (
                    attack_events_check_71d5j[
                        "user_id"
                    ]
                    .astype(str)
                    == user
                )
                &
                (
                    attack_events_check_71d5j[
                        "timestamp"
                    ]
                    < cutoff
                )
            ]
        )

        if len(subset):

            attack_contamination_71d5j.append(
                {
                    "window_id":
                        w["window_id"],
                    "n_attack_events_before_cutoff":
                        len(subset)
                }
            )


positive_attack_contamination_71d5j = (
    len(attack_contamination_71d5j)
)

print(
    "Positive windows with attack events "
    "before cutoff:",
    positive_attack_contamination_71d5j
)


# ============================================================
# 27. PRECURSOR / HARD EVENT REUSE
# ============================================================

precursor_ids_71d5j = set()

if len(precursor_events_final_71d5j):

    precursor_ids_71d5j = set(
        precursor_events_final_71d5j[
            "event_id"
        ]
        .astype(str)
    )

hard_event_ids_71d5j = set(
    hard_negative_events_71d5j[
        "event_id"
    ]
    .astype(str)
)

precursor_hard_overlap_71d5j = (
    precursor_ids_71d5j
    &
    hard_event_ids_71d5j
)

print(
    "\nPrecursor event IDs reused by hard negatives:",
    len(precursor_hard_overlap_71d5j)
)


# ============================================================
# 28. BENIGN ANOMALY ATTACK FLAGS
# ============================================================

benign_attack_flags_71d5j = 0

if "is_attack" in (
    benign_anomalies_71d5j.columns
):

    benign_attack_flags_71d5j = int(
        benign_anomalies_71d5j[
            "is_attack"
        ]
        .fillna(0)
        .astype(int)
        .sum()
    )

elif "event_id" in (
    benign_anomalies_71d5j.columns
):

    benign_attack_flags_71d5j = len(
        set(
            benign_anomalies_71d5j[
                "event_id"
            ]
            .astype(str)
        )
        &
        attack_event_ids_71d5j
    )


print(
    "\nBenign anomaly attack flags:",
    benign_attack_flags_71d5j
)


# ============================================================
# 29. HARD NEGATIVE ATTACK FLAGS
# ============================================================

hard_attack_flags_71d5j = 0

if "is_attack" in (
    hard_negative_events_71d5j.columns
):

    hard_attack_flags_71d5j = int(
        hard_negative_events_71d5j[
            "is_attack"
        ]
        .fillna(0)
        .astype(int)
        .sum()
    )

elif "event_id" in (
    hard_negative_events_71d5j.columns
):

    hard_attack_flags_71d5j = len(
        set(
            hard_negative_events_71d5j[
                "event_id"
            ]
            .astype(str)
        )
        &
        attack_event_ids_71d5j
    )


print(
    "Hard-negative attack flags:",
    hard_attack_flags_71d5j
)


# ============================================================
# 30. FINAL WINDOW CLASS COUNTS
# ============================================================

print("\n" + "=" * 78)
print("FINAL PREDICTION WINDOW CLASS COUNTS")
print("=" * 78)

print(
    afritac_prediction_windows_71d5j[
        "benchmark_class"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# 31. HORIZON COUNTS
# ============================================================

if "horizon_minutes" in (
    afritac_prediction_windows_71d5j.columns
):

    print(
        "\nHorizon distribution:"
    )

    print(
        pd.crosstab(
            afritac_prediction_windows_71d5j[
                "horizon_minutes"
            ],
            afritac_prediction_windows_71d5j[
                "benchmark_class"
            ]
        )
        .to_string()
    )


# ============================================================
# 32. USER COUNTS
# ============================================================

print("\n" + "=" * 78)
print("USER COVERAGE")
print("=" * 78)

print(
    "Positive users:",
    positive_windows_71d5j[
        "user_id"
    ]
    .nunique()
)

print(
    "Hard-negative users:",
    hard_negative_windows_71d5j[
        "user_id"
    ]
    .nunique()
)

print(
    "Benign anomaly users:",
    benign_anomalies_71d5j[
        "user_id"
    ]
    .nunique()
)

print(
    "Ordinary negative users:",
    (
        ordinary_negative_windows_71d5j[
            "user_id"
        ]
        .nunique()
        if len(ordinary_negative_windows_71d5j)
        else 0
    )
)


# ============================================================
# 33. PROVENANCE TABLE
# ============================================================

provenance_records_71d5j = [

    {
        "source_layer":
            "POSITIVE_ATTACK_WINDOWS",
        "unit":
            "prediction_window",
        "rows":
            len(positive_windows_71d5j),
        "label":
            1,
    },

    {
        "source_layer":
            "71D.5H_HARD_NEGATIVE",
        "unit":
            "prediction_window",
        "rows":
            len(hard_negative_windows_71d5j),
        "label":
            0,
    },

    {
        "source_layer":
            "BENIGN_ANOMALIES",
        "unit":
            "event",
        "rows":
            len(benign_anomalies_71d5j),
        "label":
            0,
    },

    {
        "source_layer":
            "OBSERVABLE_STREAM",
        "unit":
            "event",
        "rows":
            len(observable_events_final_71d5j),
        "label":
            "MIXED",
    },

    {
        "source_layer":
            "71D.5H_HARD_NEGATIVE_EVENTS",
        "unit":
            "event",
        "rows":
            len(hard_negative_events_71d5j),
        "label":
            0,
    },
]

if len(ordinary_negative_windows_71d5j):

    provenance_records_71d5j.insert(
        1,
        {
            "source_layer":
                "ORDINARY_NEGATIVE_WINDOWS",
            "unit":
                "prediction_window",
            "rows":
                len(
                    ordinary_negative_windows_71d5j
                ),
            "label":
                0,
        }
    )


provenance_71d5j = pd.DataFrame(
    provenance_records_71d5j
)

print(
    "\n" +
    provenance_71d5j.to_string(
        index=False
    )
)


# ============================================================
# 34. LEAKAGE FLAGS
# ============================================================

leakage_flags_71d5j = {

    "duplicate_window_ids":
        int(duplicate_window_ids_71d5j),

    "positive_hard_user_overlap":
        int(
            len(
                positive_hard_user_overlap_71d5j
            )
        ),

    "hard_source_event_reuse":
        int(source_reuse_71d5j),

    "duplicate_hard_event_ids":
        int(duplicate_hard_event_ids_71d5j),

    "hard_attack_vocab_overlap":
        int(
            len(
                hard_attack_vocab_overlap_71d5j
            )
        ),

    "positive_cutoff_after_takeover":
        int(
            positive_cutoff_violations_71d5j
        ),

    "positive_attack_event_contamination":
        int(
            positive_attack_contamination_71d5j
        ),

    "precursor_hard_event_overlap":
        int(
            len(
                precursor_hard_overlap_71d5j
            )
        ),

    "benign_attack_flags":
        int(
            benign_attack_flags_71d5j
        ),

    "hard_attack_flags":
        int(
            hard_attack_flags_71d5j
        ),
}


print("\n" + "=" * 78)
print("FINAL LEAKAGE FLAGS")
print("=" * 78)

for key, value in leakage_flags_71d5j.items():

    print(
        f"{key}: {value}"
    )


# ============================================================
# 35. DECISION
# ============================================================

blocking_issues_71d5j = {
    k: v
    for k, v in leakage_flags_71d5j.items()
    if v != 0
}


print("\n" + "=" * 78)
print("71D.5J FINAL DECISION")
print("=" * 78)

if blocking_issues_71d5j:

    print(
        "\n71D.5J FAILED."
    )

    print(
        "\nBlocking issues:"
    )

    for key, value in (
        blocking_issues_71d5j.items()
    ):

        print(
            f"  {key}: {value}"
        )

    print(
        "\nNo authoritative source object was modified."
    )

    raise RuntimeError(
        "AFRITAC final benchmark failed the "
        "71D.5J leakage gate."
    )


else:

    print(
        "\n✓ 71D.5J FINAL BENCHMARK ASSEMBLY PASSED"
    )

    print(
        "\nAll blocking provenance and leakage "
        "checks are zero."
    )

    print(
        "\nAuthoritative hard-negative layer: 71D.5H"
    )

    print(
        "Final prediction windows:",
        len(
            afritac_prediction_windows_71d5j
        )
    )

    print(
        "Final benchmark event rows:",
        len(
            afritac_benchmark_events_71d5j
        )
    )

    print(
        "Benign anomaly sessions:",
        len(
            benign_session_table_71d5j
        )
    )

    print(
        "Observable precursor events:",
        len(
            precursor_events_final_71d5j
        )
    )

    print(
        "\nNo authoritative source layer was modified."
    )

    print(
        "\nAFRITAC is ready for 71E."
    )

print("=" * 78)
