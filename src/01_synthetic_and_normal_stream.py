# AFRIDATACYBERJOHN — Synthetic Generation and Normal Stream
# This file is an archival extraction of the corresponding cells from
# AFRIDATACYBERJOHN_v1.0_reproducibility.ipynb.
# The canonical workflow is the notebook; this script is not guaranteed
# to be independently executable without the preceding workflow state.


# ==============================================================================
# NOTEBOOK CELL 42
# ==============================================================================

# AFRITAC Prototype v0.1
# Reproducible research environment

import numpy as np
import pandas as pd
import random
import uuid
from datetime import datetime, timedelta

# Reproducibility
SEED = 20260901

np.random.seed(SEED)
random.seed(SEED)

# Prototype configuration
N_USERS = 100
N_DEVICES = 200
N_SESSIONS = 2000

print("AFRITAC Prototype v0.1")
print("=" * 40)
print("Random seed:", SEED)
print("Users:", N_USERS)
print("Devices:", N_DEVICES)
print("Sessions:", N_SESSIONS)

# ==============================================================================
# NOTEBOOK CELL 43
# ==============================================================================

# Define the synthetic observation period

START_DATE = datetime(2026, 1, 1, 0, 0, 0)
END_DATE = datetime(2026, 6, 30, 23, 59, 59)

print("Observation period:")
print("Start:", START_DATE)
print("End:  ", END_DATE)

# ==============================================================================
# NOTEBOOK CELL 44
# ==============================================================================

# Generate synthetic users

users = pd.DataFrame({
    "user_id": [
        f"USER_{i:05d}"
        for i in range(1, N_USERS + 1)
    ],

    "age": np.random.randint(
        18, 76, N_USERS
    ),

    "tenure_months": np.random.randint(
        1, 121, N_USERS
    ),

    "country": np.random.choice(
        [
            "Nigeria",
            "Ghana",
            "Kenya",
            "Tanzania",
            "Uganda",
            "South_Africa",
            "Mozambique"
        ],
        N_USERS
    ),

    "language_region": np.random.choice(
        [
            "Anglophone",
            "Francophone",
            "Lusophone"
        ],
        N_USERS
    )
})

print("Users generated:", len(users))
print()
print(users.head())

# ==============================================================================
# NOTEBOOK CELL 45
# ==============================================================================

print(users.info())

# ==============================================================================
# NOTEBOOK CELL 46
# ==============================================================================

print(users.describe(include="all"))

# ==============================================================================
# NOTEBOOK CELL 47
# ==============================================================================

print(users["country"].value_counts())

# ==============================================================================
# NOTEBOOK CELL 48
# ==============================================================================

# Generate synthetic devices

DEVICE_TYPES = [
    "Android",
    "iOS",
    "FeaturePhone"
]

devices = pd.DataFrame({
    "device_id": [
        f"DEVICE_{i:05d}"
        for i in range(1, N_DEVICES + 1)
    ],

    "device_type": np.random.choice(
        DEVICE_TYPES,
        N_DEVICES,
        p=[0.70, 0.20, 0.10]
    ),

    "os_version": np.random.choice(
        [
            "low",
            "medium",
            "high"
        ],
        N_DEVICES
    ),

    "device_age_months": np.random.randint(
        1, 61, N_DEVICES
    )
})

print("Devices generated:", len(devices))
print()
print(devices.head())

# ==============================================================================
# NOTEBOOK CELL 49
# ==============================================================================

# Assign each user a primary device

primary_devices = np.random.choice(
    devices["device_id"],
    size=N_USERS,
    replace=False
)

users["primary_device_id"] = primary_devices

print(users.head())

# ==============================================================================
# NOTEBOOK CELL 50
# ==============================================================================

# Correct language-region assignment based on country scenario

language_map = {
    "Nigeria": "Anglophone",
    "Ghana": "Anglophone",
    "Kenya": "Anglophone",
    "Uganda": "Anglophone",
    "Tanzania": "Anglophone",
    "Mozambique": "Lusophone",
    "South_Africa": "Anglophone"
}

users["language_region"] = users["country"].map(language_map)

print(users[["user_id", "country", "language_region"]].head(20))

# ==============================================================================
# NOTEBOOK CELL 51
# ==============================================================================

print(
    pd.crosstab(
        users["country"],
        users["language_region"]
    )
)

# ==============================================================================
# NOTEBOOK CELL 52
# ==============================================================================

# ==========================================
# AFRITAC: Session Generator v0.1
# ==========================================

SESSION_TYPES = [
    "balance",
    "transfer",
    "withdrawal",
    "airtime",
    "bill_payment",
    "merchant",
    "loan"
]

USSD_CODES = {
    "Nigeria": "*737#",
    "Ghana": "*170#",
    "Kenya": "*334#",
    "Tanzania": "*150*00#",
    "Uganda": "*165#",
    "South_Africa": "*120#",
    "Mozambique": "*150#"
}

PLATFORMS = {
    "Nigeria": ["MTN_MoMo", "OPay", "PalmPay"],
    "Ghana": ["MTN_MoMo", "Airtel_Money"],
    "Kenya": ["M_Pesa", "Airtel_Money"],
    "Tanzania": ["M_Pesa", "Airtel_Money"],
    "Uganda": ["MTN_MoMo", "Airtel_Money"],
    "South_Africa": ["Other"],
    "Mozambique": ["M_Pesa", "Other"]
}

# Randomly select users for sessions
session_users = np.random.choice(
    users["user_id"],
    size=N_SESSIONS,
    replace=True
)

sessions = pd.DataFrame({
    "session_id": [
        f"SESSION_{i:06d}"
        for i in range(1, N_SESSIONS + 1)
    ],

    "user_id": session_users
})

# Attach user attributes
sessions = sessions.merge(
    users[
        [
            "user_id",
            "age",
            "tenure_months",
            "country",
            "language_region",
            "primary_device_id"
        ]
    ],
    on="user_id",
    how="left"
)

# Assign device
sessions["device_id"] = sessions["primary_device_id"]

# Assign session type
sessions["session_type"] = np.random.choice(
    SESSION_TYPES,
    size=N_SESSIONS
)

# Assign USSD code according to country
sessions["ussd_code"] = sessions["country"].map(
    USSD_CODES
)

# Assign platform according to country
sessions["mobile_money_platform"] = [
    np.random.choice(PLATFORMS[country])
    for country in sessions["country"]
]

# Generate session start times
total_seconds = int(
    (END_DATE - START_DATE).total_seconds()
)

random_seconds = np.random.randint(
    0,
    total_seconds,
    N_SESSIONS
)

sessions["start_time"] = [
    START_DATE + timedelta(seconds=int(x))
    for x in random_seconds
]

# Normal session duration
sessions["duration_sec"] = np.clip(
    np.random.gamma(
        shape=3.0,
        scale=15.0,
        size=N_SESSIONS
    ),
    5,
    300
).round(0).astype(int)

# Calculate end time
sessions["end_time"] = (
    sessions["start_time"]
    + pd.to_timedelta(
        sessions["duration_sec"],
        unit="s"
    )
)

# Number of menu interactions
sessions["menu_interactions"] = np.clip(
    np.random.poisson(
        lam=4,
        size=N_SESSIONS
    ),
    1,
    8
)

print("Sessions generated:", len(sessions))
print()
print(sessions.head())

# ==============================================================================
# NOTEBOOK CELL 53
# ==============================================================================

print(sessions.shape)
print()
print(sessions.dtypes)

# ==============================================================================
# NOTEBOOK CELL 54
# ==============================================================================

print(
    sessions[
        [
            "duration_sec",
            "menu_interactions"
        ]
    ].describe()
)

# ==============================================================================
# NOTEBOOK CELL 55
# ==============================================================================

print(
    sessions["session_type"].value_counts()
)

# ==============================================================================
# NOTEBOOK CELL 56
# ==============================================================================

print(
    sessions[
        [
            "user_id",
            "device_id",
            "country",
            "mobile_money_platform",
            "ussd_code"
        ]
    ].head(20)
)

# ==============================================================================
# NOTEBOOK CELL 57
# ==============================================================================

# ==========================================
# AFRITAC: Normal Event Generator v0.1
# ==========================================

events = []

for _, session in sessions.iterrows():

    session_id = session["session_id"]
    user_id = session["user_id"]
    device_id = session["device_id"]

    start_time = session["start_time"]
    duration = int(session["duration_sec"])
    menu_count = int(session["menu_interactions"])

    # Session start
    events.append({
        "event_id": f"EVENT_{len(events)+1:08d}",
        "timestamp": start_time,
        "user_id": user_id,
        "device_id": device_id,
        "session_id": session_id,
        "event_type": "SESSION_START",
        "modality": "SESSION",
        "event_stage": "normal"
    })

    # Authentication
    auth_time = start_time + timedelta(
        seconds=int(min(5, max(1, duration * 0.10)))
    )

    events.append({
        "event_id": f"EVENT_{len(events)+1:08d}",
        "timestamp": auth_time,
        "user_id": user_id,
        "device_id": device_id,
        "session_id": session_id,
        "event_type": "AUTHENTICATION_SUCCESS",
        "modality": "AUTHENTICATION",
        "event_stage": "normal"
    })

    # USSD initiation
    ussd_time = start_time + timedelta(
        seconds=int(min(10, max(2, duration * 0.20)))
    )

    events.append({
        "event_id": f"EVENT_{len(events)+1:08d}",
        "timestamp": ussd_time,
        "user_id": user_id,
        "device_id": device_id,
        "session_id": session_id,
        "event_type": "USSD_INITIATION",
        "modality": "USSD",
        "event_stage": "normal"
    })

    # Menu interactions
    usable_duration = max(1, duration - 10)

    for i in range(menu_count):

        offset = 10 + int(
            (usable_duration / max(1, menu_count)) * i
        )

        event_time = start_time + timedelta(
            seconds=min(offset, duration - 1)
        )

        events.append({
            "event_id": f"EVENT_{len(events)+1:08d}",
            "timestamp": event_time,
            "user_id": user_id,
            "device_id": device_id,
            "session_id": session_id,
            "event_type": "MENU_INTERACTION",
            "modality": "USSD",
            "event_stage": "normal",
            "interaction_number": i + 1
        })

    # USSD response
    response_offset = max(1, duration - 3)

    events.append({
        "event_id": f"EVENT_{len(events)+1:08d}",
        "timestamp": start_time + timedelta(
            seconds=response_offset
        ),
        "user_id": user_id,
        "device_id": device_id,
        "session_id": session_id,
        "event_type": "USSD_RESPONSE",
        "modality": "USSD",
        "event_stage": "normal"
    })

    # Session end
    events.append({
        "event_id": f"EVENT_{len(events)+1:08d}",
        "timestamp": session["end_time"],
        "user_id": user_id,
        "device_id": device_id,
        "session_id": session_id,
        "event_type": "SESSION_END",
        "modality": "SESSION",
        "event_stage": "normal"
    })


events = pd.DataFrame(events)

# Sort chronologically
events = events.sort_values(
    ["timestamp", "user_id", "session_id"]
).reset_index(drop=True)

print("Events generated:", len(events))
print()
print(events.head(20))

# ==============================================================================
# NOTEBOOK CELL 58
# ==============================================================================

print("\n=== EVENT TYPES ===")
print(events["event_type"].value_counts())

# ==============================================================================
# NOTEBOOK CELL 59
# ==============================================================================

print("\n=== MODALITIES ===")
print(events["modality"].value_counts())

# ==============================================================================
# NOTEBOOK CELL 60
# ==============================================================================

print("\n=== EVENTS PER SESSION ===")

events_per_session = (
    events.groupby("session_id")
    .size()
)

print(events_per_session.describe())

# ==============================================================================
# NOTEBOOK CELL 61
# ==============================================================================

print("\n=== TEMPORAL RANGE ===")
print("First event:", events["timestamp"].min())
print("Last event: ", events["timestamp"].max())

# ==============================================================================
# NOTEBOOK CELL 62
# ==============================================================================

# Verify chronological ordering within every session

session_order_check = (
    events
    .groupby("session_id")["timestamp"]
    .apply(lambda x: x.is_monotonic_increasing)
)

print(
    "Sessions correctly ordered:",
    session_order_check.all()
)

print(
    "Sessions with ordering problems:",
    (~session_order_check).sum()
)

# ==============================================================================
# NOTEBOOK CELL 63
# ==============================================================================

example_session = sessions.iloc[0]["session_id"]

print(
    events[
        events["session_id"] == example_session
    ][
        [
            "event_id",
            "timestamp",
            "event_type",
            "modality"
        ]
    ].to_string(index=False)
)

# ==============================================================================
# NOTEBOOK CELL 64
# ==============================================================================

# ==========================================
# AFRITAC: User Behavioural Profiles
# ==========================================

USER_PROFILES = [
    "conservative",
    "regular",
    "high_activity"
]

users["behaviour_profile"] = np.random.choice(
    USER_PROFILES,
    size=len(users),
    p=[0.40, 0.45, 0.15]
)

print(
    users["behaviour_profile"].value_counts()
)

# ==============================================================================
# NOTEBOOK CELL 65
# ==============================================================================

print(
    users[
        [
            "user_id",
            "age",
            "country",
            "behaviour_profile"
        ]
    ].head(20)
)

# ==============================================================================
# NOTEBOOK CELL 66
# ==============================================================================

# Attach behavioural profile to sessions

sessions = sessions.merge(
    users[
        [
            "user_id",
            "behaviour_profile"
        ]
    ],
    on="user_id",
    how="left"
)

print(
    sessions[
        [
            "session_id",
            "user_id",
            "behaviour_profile",
            "session_type"
        ]
    ].head(20)
)

# ==============================================================================
# NOTEBOOK CELL 67
# ==============================================================================

# ==========================================
# AFRITAC: Normal Network Context
# ==========================================

NETWORK_TYPES = [
    "2G",
    "3G",
    "4G",
    "5G"
]

sessions["network_type"] = np.random.choice(
    NETWORK_TYPES,
    size=len(sessions),
    p=[0.10, 0.20, 0.55, 0.15]
)

# Signal strength in dBm
sessions["signal_strength_dbm"] = np.clip(
    np.random.normal(
        loc=-75,
        scale=12,
        size=len(sessions)
    ),
    -110,
    -40
).round(0).astype(int)

# Synthetic cell tower
sessions["cell_tower_id"] = [
    f"TOWER_{np.random.randint(1, 301):04d}"
    for _ in range(len(sessions))
]

# Small proportion of legitimate roaming
sessions["roaming"] = np.random.choice(
    [0, 1],
    size=len(sessions),
    p=[0.90, 0.10]
)

print(
    sessions[
        [
            "session_id",
            "network_type",
            "signal_strength_dbm",
            "cell_tower_id",
            "roaming"
        ]
    ].head(20)
)

# ==============================================================================
# NOTEBOOK CELL 68
# ==============================================================================

# ==========================================
# Normal response delay
# ==========================================

sessions["response_delay_ms"] = np.clip(
    np.random.lognormal(
        mean=np.log(900),
        sigma=0.55,
        size=len(sessions)
    ),
    100,
    5000
).round(0).astype(int)

print(
    sessions["response_delay_ms"].describe()
)

# ==============================================================================
# NOTEBOOK CELL 69
# ==============================================================================

# ==========================================
# Legitimate device variation
# ==========================================

sessions["new_device"] = np.random.choice(
    [0, 1],
    size=len(sessions),
    p=[0.96, 0.04]
)

print(
    sessions["new_device"].value_counts()
)

# ==============================================================================
# NOTEBOOK CELL 70
# ==============================================================================

# ==========================================
# Legitimate location variation
# ==========================================

sessions["location_change"] = np.random.choice(
    [0, 1],
    size=len(sessions),
    p=[0.93, 0.07]
)

print(
    sessions["location_change"].value_counts()
)

# ==============================================================================
# NOTEBOOK CELL 71
# ==============================================================================

# ==========================================
# AFRITAC: Enrich Event Stream v0.1
# ==========================================

# Select session-level contextual variables
session_context = sessions[
    [
        "session_id",
        "country",
        "language_region",
        "mobile_money_platform",
        "session_type",
        "ussd_code",
        "network_type",
        "signal_strength_dbm",
        "cell_tower_id",
        "roaming",
        "response_delay_ms",
        "new_device",
        "location_change",
        "behaviour_profile"
    ]
].copy()

# Attach context to every event
events = events.merge(
    session_context,
    on="session_id",
    how="left"
)

print("Enriched event shape:", events.shape)

print(
    events[
        [
            "event_id",
            "timestamp",
            "user_id",
            "device_id",
            "session_id",
            "event_type",
            "modality",
            "country",
            "network_type",
            "signal_strength_dbm",
            "response_delay_ms",
            "new_device",
            "location_change"
        ]
    ].head(20)
)

# ==============================================================================
# NOTEBOOK CELL 72
# ==============================================================================

print("Missing values:")
print(
    events.isnull()
    .sum()
    .sort_values(ascending=False)
    .head(20)
)

# ==============================================================================
# NOTEBOOK CELL 73
# ==============================================================================

print("=== NORMAL EVENT CONTEXT ===")

print(
    events[
        [
            "network_type",
            "roaming",
            "new_device",
            "location_change"
        ]
    ].describe(include="all")
)

# ==============================================================================
# NOTEBOOK CELL 74
# ==============================================================================

profile_summary = (
    sessions
    .groupby("behaviour_profile")
    .agg(
        sessions=("session_id", "count"),
        mean_duration=("duration_sec", "mean"),
        mean_menu_interactions=("menu_interactions", "mean"),
        mean_response_delay=("response_delay_ms", "mean"),
        new_device_rate=("new_device", "mean"),
        roaming_rate=("roaming", "mean")
    )
)

print(profile_summary)

# ==============================================================================
# NOTEBOOK CELL 75
# ==============================================================================

daily_events = (
    events
    .set_index("timestamp")
    .resample("D")
    .size()
)

print(daily_events.describe())

print("\nDays with events:", len(daily_events))
print("Maximum events in one day:", daily_events.max())
print("Minimum events in one day:", daily_events.min())

# ==============================================================================
# NOTEBOOK CELL 76
# ==============================================================================

# Check overlapping sessions for the same user

sorted_sessions = sessions.sort_values(
    ["user_id", "start_time"]
).copy()

sorted_sessions["previous_end_time"] = (
    sorted_sessions
    .groupby("user_id")["end_time"]
    .shift()
)

sorted_sessions["overlap"] = (
    sorted_sessions["start_time"]
    < sorted_sessions["previous_end_time"]
)

print(
    "Potential overlapping sessions:",
    sorted_sessions["overlap"].sum()
)

# ==============================================================================
# NOTEBOOK CELL 77
# ==============================================================================

print(
    "Duplicate event IDs:",
    events["event_id"].duplicated().sum()
)

print(
    "Duplicate session IDs:",
    events["session_id"].duplicated().sum()
)

# ==============================================================================
# NOTEBOOK CELL 78
# ==============================================================================

# ==========================================
# AFRITAC: Complete Normal Context
# ==========================================

# Legitimate device variation
if "new_device" not in sessions.columns:
    sessions["new_device"] = np.random.choice(
        [0, 1],
        size=len(sessions),
        p=[0.96, 0.04]
    )

# Legitimate location variation
if "location_change" not in sessions.columns:
    sessions["location_change"] = np.random.choice(
        [0, 1],
        size=len(sessions),
        p=[0.93, 0.07]
    )

# Normal response delay
if "response_delay_ms" not in sessions.columns:
    sessions["response_delay_ms"] = np.clip(
        np.random.lognormal(
            mean=np.log(900),
            sigma=0.55,
            size=len(sessions)
        ),
        100,
        5000
    ).round(0).astype(int)

# Network type
if "network_type" not in sessions.columns:
    sessions["network_type"] = np.random.choice(
        ["2G", "3G", "4G", "5G"],
        size=len(sessions),
        p=[0.10, 0.20, 0.55, 0.15]
    )

# Signal strength
if "signal_strength_dbm" not in sessions.columns:
    sessions["signal_strength_dbm"] = np.clip(
        np.random.normal(
            loc=-75,
            scale=12,
            size=len(sessions)
        ),
        -110,
        -40
    ).round(0).astype(int)

# Cell tower
if "cell_tower_id" not in sessions.columns:
    sessions["cell_tower_id"] = [
        f"TOWER_{np.random.randint(1, 301):04d}"
        for _ in range(len(sessions))
    ]

# Legitimate roaming
if "roaming" not in sessions.columns:
    sessions["roaming"] = np.random.choice(
        [0, 1],
        size=len(sessions),
        p=[0.90, 0.10]
    )

print("Normal context variables are ready.")

context_columns = [
    "network_type",
    "signal_strength_dbm",
    "cell_tower_id",
    "roaming",
    "response_delay_ms",
    "new_device",
    "location_change"
]

print("\nContext columns:")
print(context_columns)

print("\nMissing values:")
print(sessions[context_columns].isnull().sum())

# ==============================================================================
# NOTEBOOK CELL 79
# ==============================================================================

print(
    sessions[
        [
            "session_id",
            "user_id",
            "country",
            "mobile_money_platform",
            "network_type",
            "signal_strength_dbm",
            "roaming",
            "response_delay_ms",
            "new_device",
            "location_change"
        ]
    ].head(10)
)

# ==============================================================================
# NOTEBOOK CELL 80
# ==============================================================================

# ==========================================
# AFRITAC: Enrich Event Stream v0.1
# ==========================================

session_context = sessions[
    [
        "session_id",
        "country",
        "language_region",
        "mobile_money_platform",
        "session_type",
        "ussd_code",
        "network_type",
        "signal_strength_dbm",
        "cell_tower_id",
        "roaming",
        "response_delay_ms",
        "new_device",
        "location_change",
        "behaviour_profile"
    ]
].copy()

# Remove previously attached context if this cell
# has already been executed
context_columns_to_remove = [
    "country",
    "language_region",
    "mobile_money_platform",
    "session_type",
    "ussd_code",
    "network_type",
    "signal_strength_dbm",
    "cell_tower_id",
    "roaming",
    "response_delay_ms",
    "new_device",
    "location_change",
    "behaviour_profile"
]

existing_columns = [
    col for col in context_columns_to_remove
    if col in events.columns
]

if existing_columns:
    events = events.drop(
        columns=existing_columns
    )

# Attach session context
events = events.merge(
    session_context,
    on="session_id",
    how="left"
)

print("Enriched event shape:", events.shape)

print("\nMissing values:")
print(
    events[
        context_columns_to_remove
    ].isnull().sum()
)

# ==============================================================================
# NOTEBOOK CELL 81
# ==============================================================================

print(
    events[
        [
            "event_id",
            "timestamp",
            "user_id",
            "device_id",
            "session_id",
            "event_type",
            "modality",
            "country",
            "network_type",
            "signal_strength_dbm",
            "response_delay_ms",
            "new_device",
            "location_change"
        ]
    ].head(15).to_string(index=False)
)

# ==============================================================================
# NOTEBOOK CELL 82
# ==============================================================================

profile_summary = (
    sessions
    .groupby("behaviour_profile")
    .agg(
        sessions=("session_id", "count"),
        mean_duration=("duration_sec", "mean"),
        mean_menu_interactions=("menu_interactions", "mean"),
        mean_response_delay=("response_delay_ms", "mean"),
        new_device_rate=("new_device", "mean"),
        roaming_rate=("roaming", "mean"),
        location_change_rate=("location_change", "mean")
    )
)

print(profile_summary)

# ==============================================================================
# NOTEBOOK CELL 83
# ==============================================================================

session_order_check = (
    events
    .groupby("session_id")["timestamp"]
    .apply(lambda x: x.is_monotonic_increasing)
)

print(
    "Sessions correctly ordered:",
    session_order_check.all()
)

print(
    "Sessions with ordering problems:",
    (~session_order_check).sum()
)

# ==============================================================================
# NOTEBOOK CELL 84
# ==============================================================================

# ==========================================
# AFRITAC: Behavioural Profile Calibration
# ==========================================

profile_params = {
    "conservative": {
        "duration_mean": 30,
        "duration_sd": 12,
        "menu_lambda": 3.0,
        "response_mean": 850
    },

    "regular": {
        "duration_mean": 50,
        "duration_sd": 18,
        "menu_lambda": 4.0,
        "response_mean": 1000
    },

    "high_activity": {
        "duration_mean": 80,
        "duration_sd": 30,
        "menu_lambda": 5.5,
        "response_mean": 1200
    }
}

# Generate profile dependent session behaviour

for profile, params in profile_params.items():

    mask = sessions["behaviour_profile"] == profile
    n = mask.sum()

    # Session duration
    durations = np.random.normal(
        loc=params["duration_mean"],
        scale=params["duration_sd"],
        size=n
    )

    sessions.loc[mask, "duration_sec"] = np.clip(
        durations,
        5,
        300
    ).round().astype(int)

    # Menu interactions
    interactions = np.random.poisson(
        lam=params["menu_lambda"],
        size=n
    )

    sessions.loc[mask, "menu_interactions"] = np.clip(
        interactions,
        1,
        10
    )

    # Response delay
    response = np.random.lognormal(
        mean=np.log(params["response_mean"]),
        sigma=0.45,
        size=n
    )

    sessions.loc[mask, "response_delay_ms"] = np.clip(
        response,
        100,
        5000
    ).round().astype(int)


# Recalculate session end times
sessions["end_time"] = (
    sessions["start_time"]
    + pd.to_timedelta(
        sessions["duration_sec"],
        unit="s"
    )
)

print("Behavioural profiles recalibrated.")

# ==============================================================================
# NOTEBOOK CELL 85
# ==============================================================================

profile_summary = (
    sessions
    .groupby("behaviour_profile")
    .agg(
        sessions=("session_id", "count"),
        mean_duration=("duration_sec", "mean"),
        median_duration=("duration_sec", "median"),
        mean_menu_interactions=("menu_interactions", "mean"),
        mean_response_delay=("response_delay_ms", "mean")
    )
)

print(profile_summary)

# ==============================================================================
# NOTEBOOK CELL 86
# ==============================================================================

# ==========================================
# AFRITAC: Transaction Behaviour
# ==========================================

transaction_types = {
    "balance": None,
    "transfer": "transfer",
    "withdrawal": "withdrawal",
    "airtime": "airtime",
    "bill_payment": "bill_payment",
    "merchant": "merchant",
    "loan": "loan"
}

sessions["transaction_type"] = (
    sessions["session_type"]
    .map(transaction_types)
)

# Whether the session generates a financial transaction
sessions["has_transaction"] = (
    sessions["transaction_type"]
    .notna()
    .astype(int)
)

# Generate transaction amount
sessions["transaction_amount"] = 0.0

transaction_mask = sessions["has_transaction"] == 1

sessions.loc[
    transaction_mask,
    "transaction_amount"
] = np.clip(
    np.random.lognormal(
        mean=np.log(2500),
        sigma=1.1,
        size=transaction_mask.sum()
    ),
    10,
    100000
).round(2)

print(
    sessions[
        [
            "session_type",
            "transaction_type",
            "has_transaction",
            "transaction_amount"
        ]
    ].head(20)
)

# ==============================================================================
# NOTEBOOK CELL 87
# ==============================================================================

# ==========================================
# Transaction amount calibration
# ==========================================

amount_ranges = {
    "transfer": (500, 100000),
    "withdrawal": (500, 50000),
    "airtime": (50, 10000),
    "bill_payment": (100, 50000),
    "merchant": (100, 75000),
    "loan": (1000, 100000)
}

for transaction_type, (low, high) in amount_ranges.items():

    mask = sessions["transaction_type"] == transaction_type
    n = mask.sum()

    if n > 0:
        sessions.loc[
            mask,
            "transaction_amount"
        ] = np.random.uniform(
            low,
            high,
            n
        ).round(2)

print(
    sessions[
        [
            "transaction_type",
            "transaction_amount"
        ]
    ].groupby("transaction_type")
    .agg(
        count=("transaction_amount", "count"),
        mean=("transaction_amount", "mean"),
        median=("transaction_amount", "median"),
        maximum=("transaction_amount", "max")
    )
)

# ==============================================================================
# NOTEBOOK CELL 88
# ==============================================================================

# ==========================================
# AFRITAC: Beneficiary Context
# ==========================================

sessions["new_beneficiary"] = 0

transfer_mask = (
    sessions["transaction_type"] == "transfer"
)

sessions.loc[
    transfer_mask,
    "new_beneficiary"
] = np.random.choice(
    [0, 1],
    size=transfer_mask.sum(),
    p=[0.90, 0.10]
)

print(
    sessions["new_beneficiary"].value_counts()
)

# ==============================================================================
# NOTEBOOK CELL 89
# ==============================================================================

# ==========================================
# AFRITAC: Transaction Velocity
# ==========================================

sessions = sessions.sort_values(
    ["user_id", "start_time"]
).reset_index(drop=True)

sessions["previous_session_time"] = (
    sessions
    .groupby("user_id")["start_time"]
    .shift()
)

sessions["time_since_previous_session_min"] = (
    (
        sessions["start_time"]
        - sessions["previous_session_time"]
    )
    .dt.total_seconds()
    / 60
)

sessions["time_since_previous_session_min"] = (
    sessions["time_since_previous_session_min"]
    .fillna(-1)
)

print(
    sessions[
        [
            "user_id",
            "start_time",
            "time_since_previous_session_min"
        ]
    ].head(20)
)

# ==============================================================================
# NOTEBOOK CELL 90
# ==============================================================================

# ==========================================
# AFRITAC: Improved Financial Behaviour
# ==========================================

# User-specific financial activity factor
profile_factor = {
    "conservative": 0.65,
    "regular": 1.00,
    "high_activity": 1.45
}

sessions["financial_activity_factor"] = (
    sessions["behaviour_profile"]
    .map(profile_factor)
)

# Base transaction distributions
transaction_params = {
    "transfer":      (3000, 1.20),
    "withdrawal":    (2500, 1.10),
    "airtime":       (500, 0.80),
    "bill_payment":  (3500, 1.00),
    "merchant":      (2500, 1.10),
    "loan":          (10000, 1.00)
}

for transaction_type, (base_amount, sigma) in transaction_params.items():

    mask = (
        sessions["transaction_type"]
        == transaction_type
    )

    n = mask.sum()

    if n == 0:
        continue

    profile_multiplier = (
        sessions.loc[
            mask,
            "financial_activity_factor"
        ].values
    )

    amounts = (
        np.random.lognormal(
            mean=np.log(base_amount),
            sigma=sigma,
            size=n
        )
        * profile_multiplier
    )

    sessions.loc[
        mask,
        "transaction_amount"
    ] = np.clip(
        amounts,
        10,
        100000
    ).round(2)

print("Improved transaction model applied.")

# ==============================================================================
# NOTEBOOK CELL 91
# ==============================================================================

transaction_summary = (
    sessions[
        sessions["has_transaction"] == 1
    ]
    .groupby("transaction_type")
    ["transaction_amount"]
    .agg(
        count="count",
        mean="mean",
        median="median",
        std="std",
        minimum="min",
        maximum="max"
    )
)

print(transaction_summary)

# ==============================================================================
# NOTEBOOK CELL 92
# ==============================================================================

financial_profile_summary = (
    sessions[
        sessions["has_transaction"] == 1
    ]
    .groupby("behaviour_profile")
    ["transaction_amount"]
    .agg(
        count="count",
        mean="mean",
        median="median",
        std="std",
        maximum="max"
    )
)

print(financial_profile_summary)

# ==============================================================================
# NOTEBOOK CELL 93
# ==============================================================================

# ==========================================
# AFRITAC: Rebuild Normal Event Stream
# ==========================================

events = []

for _, session in sessions.iterrows():

    session_id = session["session_id"]
    user_id = session["user_id"]
    device_id = session["device_id"]

    start_time = session["start_time"]
    duration = int(session["duration_sec"])
    menu_count = int(session["menu_interactions"])

    def add_event(
        timestamp,
        event_type,
        modality,
        **extra
    ):
        record = {
            "event_id": f"EVENT_{len(events)+1:08d}",
            "timestamp": timestamp,
            "user_id": user_id,
            "device_id": device_id,
            "session_id": session_id,
            "event_type": event_type,
            "modality": modality,
            "event_stage": "normal"
        }

        record.update(extra)
        events.append(record)

    # 1. Session start
    add_event(
        start_time,
        "SESSION_START",
        "SESSION"
    )

    # 2. Authentication
    auth_time = start_time + timedelta(
        seconds=min(
            5,
            max(1, int(duration * 0.10))
        )
    )

    add_event(
        auth_time,
        "AUTHENTICATION_SUCCESS",
        "AUTHENTICATION",
        authentication_method="PIN"
    )

    # 3. USSD initiation
    ussd_time = start_time + timedelta(
        seconds=min(
            10,
            max(2, int(duration * 0.20))
        )
    )

    add_event(
        ussd_time,
        "USSD_INITIATION",
        "USSD"
    )

    # 4. Menu interactions
    usable_duration = max(1, duration - 10)

    for i in range(menu_count):

        offset = 10 + int(
            (usable_duration / max(1, menu_count)) * i
        )

        event_time = start_time + timedelta(
            seconds=min(
                offset,
                duration - 1
            )
        )

        add_event(
            event_time,
            "MENU_INTERACTION",
            "USSD",
            interaction_number=i + 1
        )

    # 5. USSD response
    response_offset = max(1, duration - 3)

    add_event(
        start_time + timedelta(
            seconds=response_offset
        ),
        "USSD_RESPONSE",
        "USSD"
    )

    # 6. Financial transaction
    if session["has_transaction"] == 1:

        transaction_offset = max(
            1,
            duration - 2
        )

        add_event(
            start_time + timedelta(
                seconds=transaction_offset
            ),
            "TRANSACTION",
            "FINANCIAL",
            transaction_type=session["transaction_type"],
            transaction_amount=session["transaction_amount"],
            new_beneficiary=session["new_beneficiary"]
        )

    # 7. Session end
    add_event(
        session["end_time"],
        "SESSION_END",
        "SESSION"
    )


events = pd.DataFrame(events)

# Attach session context
session_context = sessions[
    [
        "session_id",
        "country",
        "language_region",
        "mobile_money_platform",
        "session_type",
        "ussd_code",
        "network_type",
        "signal_strength_dbm",
        "cell_tower_id",
        "roaming",
        "response_delay_ms",
        "new_device",
        "location_change",
        "behaviour_profile"
    ]
].copy()

events = events.merge(
    session_context,
    on="session_id",
    how="left"
)

# Chronological order
events = (
    events
    .sort_values(
        ["timestamp", "user_id", "session_id"]
    )
    .reset_index(drop=True)
)

print("New event count:", len(events))
print("New event shape:", events.shape)

# ==============================================================================
# NOTEBOOK CELL 94
# ==============================================================================

print("=== EVENT TYPES ===")
print(events["event_type"].value_counts())

# ==============================================================================
# NOTEBOOK CELL 95
# ==============================================================================

print("\n=== MODALITIES ===")
print(events["modality"].value_counts())

# ==============================================================================
# NOTEBOOK CELL 96
# ==============================================================================

print("\n=== MISSING VALUES ===")

important_columns = [
    "event_id",
    "timestamp",
    "user_id",
    "device_id",
    "session_id",
    "event_type",
    "modality",
    "country",
    "network_type",
    "response_delay_ms"
]

print(
    events[important_columns]
    .isnull()
    .sum()
)

# ==============================================================================
# NOTEBOOK CELL 97
# ==============================================================================

session_order_check = (
    events
    .groupby("session_id")["timestamp"]
    .apply(
        lambda x: x.is_monotonic_increasing
    )
)

print(
    "Correctly ordered sessions:",
    session_order_check.all()
)

print(
    "Sessions with ordering problems:",
    (~session_order_check).sum()
)

# ==============================================================================
# NOTEBOOK CELL 98
# ==============================================================================

transaction_session = sessions[
    sessions["has_transaction"] == 1
].iloc[0]["session_id"]

print(
    events[
        events["session_id"]
        == transaction_session
    ][
        [
            "timestamp",
            "event_type",
            "modality",
            "transaction_type",
            "transaction_amount",
            "new_beneficiary"
        ]
    ].to_string(index=False)
)

# ==============================================================================
# NOTEBOOK CELL 99
# ==============================================================================

# ==========================================
# AFRITAC: Benign Anomaly Assignment
# ==========================================

BENIGN_RATE = 0.15

N_BENIGN = int(len(sessions) * BENIGN_RATE)

# Select sessions reproducibly
rng = np.random.default_rng(SEED + 37)

benign_session_ids = rng.choice(
    sessions["session_id"].values,
    size=N_BENIGN,
    replace=False
)

sessions["benign_anomaly"] = 0
sessions["benign_anomaly_type"] = "none"

sessions.loc[
    sessions["session_id"].isin(benign_session_ids),
    "benign_anomaly"
] = 1

# Assign anomaly types
benign_types = [
    "BENIGN_NEW_DEVICE",
    "BENIGN_NETWORK",
    "BENIGN_HIGH_VALUE",
    "BENIGN_BEHAVIOUR"
]

benign_weights = [
    0.30,
    0.30,
    0.20,
    0.20
]

selected_benign = rng.choice(
    benign_types,
    size=N_BENIGN,
    p=benign_weights
)

sessions.loc[
    sessions["session_id"].isin(benign_session_ids),
    "benign_anomaly_type"
] = selected_benign

print("Total sessions:", len(sessions))
print("Benign anomaly sessions:", sessions["benign_anomaly"].sum())

print("\nBenign anomaly distribution:")
print(
    sessions[
        sessions["benign_anomaly"] == 1
    ]["benign_anomaly_type"].value_counts()
)

# ==============================================================================
# NOTEBOOK CELL 100
# ==============================================================================

# ==========================================
# AFRITAC: Apply Benign Anomaly Mechanisms
# ==========================================

# ------------------------------------------
# 1. Legitimate new device
# ------------------------------------------

mask = (
    sessions["benign_anomaly_type"]
    == "BENIGN_NEW_DEVICE"
)

sessions.loc[mask, "new_device"] = 1

# Importantly:
# No authentication failure
# No SIM manipulation
# No identity attack
# No financial compromise


# ------------------------------------------
# 2. Legitimate network degradation
# ------------------------------------------

mask = (
    sessions["benign_anomaly_type"]
    == "BENIGN_NETWORK"
)

n = mask.sum()

if n > 0:

    sessions.loc[mask, "signal_strength_dbm"] = np.clip(
        rng.normal(
            loc=-98,
            scale=5,
            size=n
        ),
        -110,
        -85
    ).round().astype(int)

    sessions.loc[mask, "response_delay_ms"] = np.clip(
        rng.lognormal(
            mean=np.log(3000),
            sigma=0.40,
            size=n
        ),
        1500,
        8000
    ).round().astype(int)

    sessions.loc[mask, "roaming"] = rng.choice(
        [0, 1],
        size=n,
        p=[0.60, 0.40]
    )


# ------------------------------------------
# 3. Legitimate high-value transaction
# ------------------------------------------

mask = (
    sessions["benign_anomaly_type"]
    == "BENIGN_HIGH_VALUE"
)

n = mask.sum()

if n > 0:

    # Restrict to sessions that can actually
    # produce a financial transaction.
    transaction_capable = (
        sessions["has_transaction"] == 1
    )

    eligible = mask & transaction_capable

    sessions.loc[
        eligible,
        "transaction_amount"
    ] = rng.uniform(
        50000,
        100000,
        eligible.sum()
    ).round(2)

    # Known beneficiary remains known
    sessions.loc[
        eligible,
        "new_beneficiary"
    ] = 0


# ------------------------------------------
# 4. Legitimate behavioural deviation
# ------------------------------------------

mask = (
    sessions["benign_anomaly_type"]
    == "BENIGN_BEHAVIOUR"
)

n = mask.sum()

if n > 0:

    sessions.loc[mask, "duration_sec"] = np.clip(
        sessions.loc[mask, "duration_sec"] * 2,
        5,
        300
    ).round().astype(int)

    sessions.loc[mask, "menu_interactions"] = np.clip(
        sessions.loc[mask, "menu_interactions"] + 3,
        1,
        10
    ).astype(int)


# Recalculate session end time
sessions["end_time"] = (
    sessions["start_time"]
    + pd.to_timedelta(
        sessions["duration_sec"],
        unit="s"
    )
)

print("Benign anomaly mechanisms applied.")

# ==============================================================================
# NOTEBOOK CELL 101
# ==============================================================================

print(
    sessions[
        [
            "benign_anomaly_type",
            "duration_sec",
            "menu_interactions",
            "response_delay_ms",
            "signal_strength_dbm",
            "roaming",
            "new_device",
            "transaction_amount",
            "new_beneficiary"
        ]
    ]
    .groupby("benign_anomaly_type")
    .agg(
        sessions=("duration_sec", "count"),
        mean_duration=("duration_sec", "mean"),
        mean_interactions=("menu_interactions", "mean"),
        mean_delay=("response_delay_ms", "mean"),
        mean_signal=("signal_strength_dbm", "mean"),
        roaming_rate=("roaming", "mean"),
        new_device_rate=("new_device", "mean"),
        mean_transaction=("transaction_amount", "mean"),
        new_beneficiary_rate=("new_beneficiary", "mean")
    )
)

# ==============================================================================
# NOTEBOOK CELL 102
# ==============================================================================

# ==========================================
# Ground truth state before attacks
# ==========================================

sessions["ground_truth_state"] = np.where(
    sessions["benign_anomaly"] == 1,
    "BENIGN_ANOMALY",
    "NORMAL"
)

print(
    sessions["ground_truth_state"].value_counts()
)

# ==============================================================================
# NOTEBOOK CELL 103
# ==============================================================================

# ==========================================
# AFRITAC: Rebuild Event Stream
# Normal + Benign Anomalies
# ==========================================

events = []

for _, session in sessions.iterrows():

    session_id = session["session_id"]
    user_id = session["user_id"]
    device_id = session["device_id"]

    start_time = session["start_time"]
    duration = int(session["duration_sec"])
    menu_count = int(session["menu_interactions"])

    def add_event(
        timestamp,
        event_type,
        modality,
        **extra
    ):
        record = {
            "event_id": f"EVENT_{len(events)+1:08d}",
            "timestamp": timestamp,
            "user_id": user_id,
            "device_id": device_id,
            "session_id": session_id,
            "event_type": event_type,
            "modality": modality,
            "event_stage": session["ground_truth_state"]
        }

        record.update(extra)
        events.append(record)

    # Session start
    add_event(
        start_time,
        "SESSION_START",
        "SESSION"
    )

    # Legitimate device event
    if session["new_device"] == 1:

        add_event(
            start_time + timedelta(seconds=2),
            "NEW_DEVICE_OBSERVED",
            "DEVICE",
            device_change=1
        )

    # Authentication
    auth_offset = min(
        6,
        max(1, int(duration * 0.10))
    )

    add_event(
        start_time + timedelta(seconds=auth_offset),
        "AUTHENTICATION_SUCCESS",
        "AUTHENTICATION",
        authentication_method="PIN"
    )

    # USSD initiation
    ussd_offset = min(
        10,
        max(2, int(duration * 0.20))
    )

    add_event(
        start_time + timedelta(seconds=ussd_offset),
        "USSD_INITIATION",
        "USSD"
    )

    # Menu interactions
    usable_duration = max(
        1,
        duration - 10
    )

    for i in range(menu_count):

        offset = 10 + int(
            (usable_duration / max(1, menu_count)) * i
        )

        offset = min(
            offset,
            max(1, duration - 1)
        )

        add_event(
            start_time + timedelta(seconds=offset),
            "MENU_INTERACTION",
            "USSD",
            interaction_number=i + 1
        )

    # USSD response
    response_offset = max(
        1,
        duration - 3
    )

    add_event(
        start_time + timedelta(seconds=response_offset),
        "USSD_RESPONSE",
        "USSD",
        response_delay_ms=session["response_delay_ms"]
    )

    # Financial transaction
    if session["has_transaction"] == 1:

        transaction_offset = max(
            1,
            duration - 2
        )

        add_event(
            start_time + timedelta(seconds=transaction_offset),
            "TRANSACTION",
            "FINANCIAL",
            transaction_type=session["transaction_type"],
            transaction_amount=session["transaction_amount"],
            new_beneficiary=session["new_beneficiary"]
        )

    # Session end
    add_event(
        session["end_time"],
        "SESSION_END",
        "SESSION"
    )


events = pd.DataFrame(events)

# Attach session context
session_context = sessions[
    [
        "session_id",
        "country",
        "language_region",
        "mobile_money_platform",
        "session_type",
        "ussd_code",
        "network_type",
        "signal_strength_dbm",
        "cell_tower_id",
        "roaming",
        "response_delay_ms",
        "new_device",
        "location_change",
        "behaviour_profile",
        "benign_anomaly",
        "benign_anomaly_type",
        "ground_truth_state"
    ]
].copy()

events = events.merge(
    session_context,
    on="session_id",
    how="left"
)

events = (
    events
    .sort_values(
        ["timestamp", "user_id", "session_id"]
    )
    .reset_index(drop=True)
)

print("Events generated:", len(events))
print("Shape:", events.shape)
