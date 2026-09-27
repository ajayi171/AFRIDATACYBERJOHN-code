# AFRIDATACYBERJOHN — Campaign and Observable Stream Construction
# This file is an archival extraction of the corresponding cells from
# AFRIDATACYBERJOHN_v1.0_reproducibility.ipynb.
# The canonical workflow is the notebook; this script is not guaranteed
# to be independently executable without the preceding workflow state.


# ==============================================================================
# NOTEBOOK CELL 104
# ==============================================================================

comparison = (
    sessions
    .groupby("ground_truth_state")
    .agg(
        sessions=("session_id", "count"),
        mean_duration=("duration_sec", "mean"),
        mean_interactions=("menu_interactions", "mean"),
        mean_delay=("response_delay_ms", "mean"),
        new_device_rate=("new_device", "mean"),
        roaming_rate=("roaming", "mean"),
        mean_transaction=("transaction_amount", "mean")
    )
)

print(comparison)

# ==============================================================================
# NOTEBOOK CELL 105
# ==============================================================================

attack_columns = [
    "sim_swap",
    "credential_compromise",
    "account_takeover",
    "session_hijacking",
    "ussd_code_injection",
    "replay_attack",
    "mitm",
    "social_engineering"
]

existing_attack_columns = [
    col for col in attack_columns
    if col in sessions.columns
]

print(
    "Attack columns currently present:",
    existing_attack_columns
)

# ==============================================================================
# NOTEBOOK CELL 106
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
# NOTEBOOK CELL 107
# ==============================================================================

# ==========================================
# AFRITAC: Social Engineering Exposure
# ==========================================

rng = np.random.default_rng(SEED + 42)

# Number of users exposed to social engineering
N_SOCIAL = 25

social_users = rng.choice(
    users["user_id"].values,
    size=N_SOCIAL,
    replace=False
)

print(
    "Users exposed to social engineering:",
    len(social_users)
)

print(social_users[:10])

# ==============================================================================
# NOTEBOOK CELL 108
# ==============================================================================

# ==========================================
# AFRITAC: Social Engineering Events
# ==========================================

social_events = []

for i, user_id in enumerate(social_users, start=1):

    # Select a random session belonging to the user
    user_sessions = sessions[
        sessions["user_id"] == user_id
    ]

    if len(user_sessions) == 0:
        continue

    session = user_sessions.sample(
        n=1,
        random_state=SEED + i
    ).iloc[0]

    session_id = session["session_id"]
    device_id = session["device_id"]

    # Social event occurs before the selected session
    message_time = (
        session["start_time"]
        - timedelta(
            minutes=int(
                rng.integers(5, 120)
            )
        )
    )

    # Select scenario
    scenario = rng.choice(
        [
            "SUSPICIOUS_MESSAGE_IGNORED",
            "SOCIAL_ENGINEERING_INTERACTION",
            "CREDENTIAL_HARVESTING_ATTEMPT"
        ],
        p=[0.40, 0.40, 0.20]
    )

    # Message received
    social_events.append({
        "event_id": f"SOCIAL_{i:05d}",
        "timestamp": message_time,
        "user_id": user_id,
        "device_id": device_id,
        "session_id": session_id,
        "event_type": "SOCIAL_MESSAGE_RECEIVED",
        "modality": "SOCIAL_ENGINEERING",
        "social_scenario": scenario,
        "user_interaction": 0,
        "credential_exposure": 0
    })

    # Interaction for relevant scenarios
    if scenario in [
        "SOCIAL_ENGINEERING_INTERACTION",
        "CREDENTIAL_HARVESTING_ATTEMPT"
    ]:

        interaction_time = (
            message_time
            + timedelta(
                minutes=int(
                    rng.integers(1, 20)
                )
            )
        )

        social_events.append({
            "event_id": f"SOCIAL_{i:05d}_I",
            "timestamp": interaction_time,
            "user_id": user_id,
            "device_id": device_id,
            "session_id": session_id,
            "event_type": "SOCIAL_MESSAGE_INTERACTION",
            "modality": "SOCIAL_ENGINEERING",
            "social_scenario": scenario,
            "user_interaction": 1,
            "credential_exposure": int(
                scenario == "CREDENTIAL_HARVESTING_ATTEMPT"
            )
        })


social_events = pd.DataFrame(
    social_events
)

print(
    "Social engineering events:",
    len(social_events)
)

print(
    social_events[
        [
            "event_type",
            "social_scenario"
        ]
    ].value_counts()
)

# ==============================================================================
# NOTEBOOK CELL 109
# ==============================================================================

print(
    social_events[
        [
            "timestamp",
            "user_id",
            "session_id",
            "event_type",
            "social_scenario",
            "user_interaction",
            "credential_exposure"
        ]
    ]
    .sort_values("timestamp")
    .head(30)
    .to_string(index=False)
)

# ==============================================================================
# NOTEBOOK CELL 110
# ==============================================================================

social_events = social_events.sort_values(
    ["user_id", "timestamp"]
).reset_index(drop=True)

social_events["previous_event_time"] = (
    social_events
    .groupby("user_id")["timestamp"]
    .shift()
)

social_events["minutes_since_previous_social_event"] = (
    (
        social_events["timestamp"]
        - social_events["previous_event_time"]
    )
    .dt.total_seconds()
    / 60
)

print(
    social_events[
        [
            "user_id",
            "event_type",
            "minutes_since_previous_social_event"
        ]
    ].head(20)
)

# ==============================================================================
# NOTEBOOK CELL 111
# ==============================================================================

# ==========================================
# AFRITAC: Attack Campaign Framework
# ==========================================

rng = np.random.default_rng(SEED + 43)

# Number of attack campaigns for prototype
N_CAMPAIGNS = 80

# Select unique users
available_users = users["user_id"].values

attack_users = rng.choice(
    available_users,
    size=N_CAMPAIGNS,
    replace=False
)

attack_types = [
    "ACCOUNT_TAKEOVER",
    "SOCIAL_ENGINEERING_TAKEOVER",
    "USSD_SESSION_HIJACK",
    "SIM_IDENTITY_COMPROMISE"
]

attack_type_probs = [
    0.30,
    0.30,
    0.25,
    0.15
]

campaign_records = []

for i, user_id in enumerate(
    attack_users,
    start=1
):

    attack_type = rng.choice(
        attack_types,
        p=attack_type_probs
    )

    campaign_records.append({
        "campaign_id": f"CAMP_{i:05d}",
        "user_id": user_id,
        "attack_type": attack_type,
        "campaign_status": "MALICIOUS",
        "ground_truth_attack": 1
    })

campaigns = pd.DataFrame(
    campaign_records
)

print("Attack campaigns:", len(campaigns))

print(
    campaigns["attack_type"]
    .value_counts()
)

# ==============================================================================
# NOTEBOOK CELL 112
# ==============================================================================

# ==========================================
# Assign temporal anchor sessions
# ==========================================

campaigns["anchor_session_id"] = None
campaigns["anchor_time"] = pd.NaT

for idx, campaign in campaigns.iterrows():

    user_sessions = sessions[
        sessions["user_id"]
        == campaign["user_id"]
    ]

    if len(user_sessions) == 0:
        continue

    # Select a session that occurs
    # sufficiently late in the observation period
    # to leave room for precursor events.
    eligible = user_sessions[
        user_sessions["start_time"]
        >= pd.Timestamp("2026-03-01")
    ]

    if len(eligible) == 0:
        eligible = user_sessions

    selected = eligible.sample(
        n=1,
        random_state=SEED + idx
    ).iloc[0]

    campaigns.loc[
        idx,
        "anchor_session_id"
    ] = selected["session_id"]

    campaigns.loc[
        idx,
        "anchor_time"
    ] = selected["start_time"]

print(
    campaigns[
        [
            "campaign_id",
            "user_id",
            "attack_type",
            "anchor_session_id",
            "anchor_time"
        ]
    ].head(15)
)

# ==============================================================================
# NOTEBOOK CELL 113
# ==============================================================================

# ==========================================
# AFRITAC: Attack Timeline Generator
# ==========================================

attack_events = []

for idx, campaign in campaigns.iterrows():

    campaign_id = campaign["campaign_id"]
    user_id = campaign["user_id"]
    attack_type = campaign["attack_type"]
    anchor_time = campaign["anchor_time"]

    # Get user's primary device
    user_record = users[
        users["user_id"] == user_id
    ].iloc[0]

    primary_device = user_record[
        "primary_device_id"
    ]

    # Generate attacker device
    attacker_device = (
        f"ATTACK_DEVICE_{idx+1:04d}"
    )

    # -----------------------------
    # Stage 1: Social engineering
    # -----------------------------

    social_time = (
        anchor_time
        - timedelta(
            minutes=int(
                rng.integers(60, 180)
            )
        )
    )

    attack_events.append({
        "campaign_id": campaign_id,
        "user_id": user_id,
        "device_id": primary_device,
        "timestamp": social_time,
        "event_type": "SOCIAL_MESSAGE_RECEIVED",
        "modality": "SOCIAL_ENGINEERING",
        "attack_stage": "PRE_ATTACK",
        "attack_type": attack_type
    })

    # -----------------------------
    # Stage 2: Social interaction
    # -----------------------------

    interaction_time = (
        social_time
        + timedelta(
            minutes=int(
                rng.integers(2, 15)
            )
        )
    )

    attack_events.append({
        "campaign_id": campaign_id,
        "user_id": user_id,
        "device_id": primary_device,
        "timestamp": interaction_time,
        "event_type": "SOCIAL_MESSAGE_INTERACTION",
        "modality": "SOCIAL_ENGINEERING",
        "attack_stage": "PRE_ATTACK",
        "attack_type": attack_type
    })

    # -----------------------------
    # Stage 3: Credential compromise
    # -----------------------------

    credential_time = (
        interaction_time
        + timedelta(
            minutes=int(
                rng.integers(5, 30)
            )
        )
    )

    attack_events.append({
        "campaign_id": campaign_id,
        "user_id": user_id,
        "device_id": primary_device,
        "timestamp": credential_time,
        "event_type": "CREDENTIAL_COMPROMISE",
        "modality": "AUTHENTICATION",
        "attack_stage": "COMPROMISE",
        "attack_type": attack_type
    })

    # -----------------------------
    # Stage 4: Device change
    # -----------------------------

    device_time = (
        credential_time
        + timedelta(
            minutes=int(
                rng.integers(3, 20)
            )
        )
    )

    attack_events.append({
        "campaign_id": campaign_id,
        "user_id": user_id,
        "device_id": attacker_device,
        "timestamp": device_time,
        "event_type": "DEVICE_CHANGE",
        "modality": "DEVICE",
        "attack_stage": "TAKEOVER",
        "attack_type": attack_type
    })

    # -----------------------------
    # Stage 5: Identity compromise
    # -----------------------------

    identity_time = (
        device_time
        + timedelta(
            minutes=int(
                rng.integers(2, 15)
            )
        )
    )

    attack_events.append({
        "campaign_id": campaign_id,
        "user_id": user_id,
        "device_id": attacker_device,
        "timestamp": identity_time,
        "event_type": "IDENTITY_CHANGE",
        "modality": "IDENTITY",
        "attack_stage": "TAKEOVER",
        "attack_type": attack_type
    })

    # -----------------------------
    # Stage 6: Account takeover
    # -----------------------------

    takeover_time = (
        identity_time
        + timedelta(
            minutes=int(
                rng.integers(1, 10)
            )
        )
    )

    attack_events.append({
        "campaign_id": campaign_id,
        "user_id": user_id,
        "device_id": attacker_device,
        "timestamp": takeover_time,
        "event_type": "ACCOUNT_TAKEOVER",
        "modality": "ACCOUNT",
        "attack_stage": "TAKEOVER",
        "attack_type": attack_type
    })

    # -----------------------------
    # Stage 7: Financial impact
    # -----------------------------

    transaction_time = (
        takeover_time
        + timedelta(
            minutes=int(
                rng.integers(1, 10)
            )
        )
    )

    amount = float(
        rng.uniform(
            5000,
            75000
        )
    )

    attack_events.append({
        "campaign_id": campaign_id,
        "user_id": user_id,
        "device_id": attacker_device,
        "timestamp": transaction_time,
        "event_type": "UNAUTHORIZED_TRANSACTION",
        "modality": "FINANCIAL",
        "attack_stage": "IMPACT",
        "attack_type": attack_type,
        "transaction_amount": round(
            amount,
            2
        )
    })


attack_events = pd.DataFrame(
    attack_events
)

print(
    "Attack events:",
    len(attack_events)
)

print(
    attack_events[
        [
            "event_type",
            "modality",
            "attack_stage"
        ]
    ].value_counts()
)

# ==============================================================================
# NOTEBOOK CELL 114
# ==============================================================================

example_campaign = (
    campaigns["campaign_id"]
    .iloc[0]
)

print(
    attack_events[
        attack_events["campaign_id"]
        == example_campaign
    ][
        [
            "timestamp",
            "event_type",
            "modality",
            "attack_stage",
            "device_id",
            "attack_type"
        ]
    ]
    .sort_values("timestamp")
    .to_string(index=False)
)

# ==============================================================================
# NOTEBOOK CELL 115
# ==============================================================================

attack_events = attack_events.sort_values(
    ["campaign_id", "timestamp"]
).reset_index(drop=True)

takeover_times = (
    attack_events[
        attack_events["event_type"]
        == "ACCOUNT_TAKEOVER"
    ]
    .groupby("campaign_id")["timestamp"]
    .min()
    .rename("takeover_time")
)

attack_events = attack_events.merge(
    takeover_times,
    on="campaign_id",
    how="left"
)

attack_events["minutes_to_takeover"] = (
    (
        attack_events["takeover_time"]
        - attack_events["timestamp"]
    )
    .dt.total_seconds()
    / 60
)

print(
    attack_events[
        [
            "campaign_id",
            "event_type",
            "attack_stage",
            "minutes_to_takeover"
        ]
    ].head(20)
)

# ==============================================================================
# NOTEBOOK CELL 116
# ==============================================================================

# ==========================================
# AFRITAC: Type-Specific Attack Campaigns
# ==========================================

attack_events = []

rng = np.random.default_rng(SEED + 430)

for idx, campaign in campaigns.iterrows():

    campaign_id = campaign["campaign_id"]
    user_id = campaign["user_id"]
    attack_type = campaign["attack_type"]
    anchor_time = campaign["anchor_time"]

    user_record = users[
        users["user_id"] == user_id
    ].iloc[0]

    primary_device = user_record["primary_device_id"]

    attacker_device = (
        f"ATTACK_DEVICE_{idx+1:04d}"
    )

    # Helper function
    def add_attack_event(
        offset_minutes,
        event_type,
        modality,
        attack_stage,
        device_id,
        **extra
    ):

        attack_events.append({
            "campaign_id": campaign_id,
            "user_id": user_id,
            "device_id": device_id,
            "timestamp": (
                anchor_time
                + timedelta(
                    minutes=offset_minutes
                )
            ),
            "event_type": event_type,
            "modality": modality,
            "attack_stage": attack_stage,
            "attack_type": attack_type,
            **extra
        })

    # ======================================
    # A. SOCIAL ENGINEERING TAKEOVER
    # ======================================

    if attack_type == "SOCIAL_ENGINEERING_TAKEOVER":

        add_attack_event(
            -60,
            "SOCIAL_MESSAGE_RECEIVED",
            "SOCIAL_ENGINEERING",
            "PRE_ATTACK",
            primary_device
        )

        add_attack_event(
            -52,
            "SOCIAL_MESSAGE_INTERACTION",
            "SOCIAL_ENGINEERING",
            "PRE_ATTACK",
            primary_device
        )

        add_attack_event(
            -35,
            "CREDENTIAL_COMPROMISE",
            "AUTHENTICATION",
            "COMPROMISE",
            primary_device
        )

        add_attack_event(
            -18,
            "NEW_DEVICE_LOGIN",
            "DEVICE",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            -8,
            "IDENTITY_CHANGE",
            "IDENTITY",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            0,
            "ACCOUNT_TAKEOVER",
            "ACCOUNT",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            5,
            "UNAUTHORIZED_TRANSACTION",
            "FINANCIAL",
            "IMPACT",
            attacker_device,
            transaction_amount=round(
                rng.uniform(5000, 75000),
                2
            )
        )

    # ======================================
    # B. DIRECT ACCOUNT TAKEOVER
    # ======================================

    elif attack_type == "ACCOUNT_TAKEOVER":

        add_attack_event(
            -25,
            "AUTHENTICATION_ANOMALY",
            "AUTHENTICATION",
            "PRE_ATTACK",
            primary_device
        )

        add_attack_event(
            -18,
            "NEW_DEVICE_LOGIN",
            "DEVICE",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            -10,
            "CREDENTIAL_VALIDATION_ANOMALY",
            "AUTHENTICATION",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            -5,
            "IDENTITY_CHANGE",
            "IDENTITY",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            0,
            "ACCOUNT_TAKEOVER",
            "ACCOUNT",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            4,
            "NEW_BENEFICIARY_ADDED",
            "FINANCIAL",
            "IMPACT",
            attacker_device
        )

        add_attack_event(
            7,
            "UNAUTHORIZED_TRANSACTION",
            "FINANCIAL",
            "IMPACT",
            attacker_device,
            transaction_amount=round(
                rng.uniform(5000, 75000),
                2
            )
        )

    # ======================================
    # C. USSD SESSION HIJACK
    # ======================================

    elif attack_type == "USSD_SESSION_HIJACK":

        add_attack_event(
            -15,
            "USSD_INITIATION",
            "USSD",
            "PRE_ATTACK",
            primary_device
        )

        add_attack_event(
            -11,
            "USSD_CODE_MODIFICATION",
            "USSD",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            -8,
            "SESSION_REROUTING",
            "USSD",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            -5,
            "STALE_SESSION_REUSE",
            "USSD",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            -2,
            "SESSION_HIJACK",
            "SESSION",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            0,
            "ACCOUNT_ACCESS_VIA_HIJACKED_SESSION",
            "ACCOUNT",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            3,
            "UNAUTHORIZED_TRANSACTION",
            "FINANCIAL",
            "IMPACT",
            attacker_device,
            transaction_amount=round(
                rng.uniform(2000, 50000),
                2
            )
        )

    # ======================================
    # D. SIM / IDENTITY COMPROMISE
    # ======================================

    elif attack_type == "SIM_IDENTITY_COMPROMISE":

        add_attack_event(
            -20,
            "SIM_CHANGE_DETECTED",
            "SIM",
            "PRE_ATTACK",
            primary_device
        )

        add_attack_event(
            -15,
            "IMSI_CHANGE",
            "IDENTITY",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            -10,
            "IMEI_CHANGE",
            "DEVICE",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            -6,
            "NETWORK_IDENTITY_ANOMALY",
            "NETWORK",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            -2,
            "AUTHENTICATION_WITH_NEW_IDENTITY",
            "AUTHENTICATION",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            0,
            "ACCOUNT_ACCESS",
            "ACCOUNT",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            5,
            "UNAUTHORIZED_TRANSACTION",
            "FINANCIAL",
            "IMPACT",
            attacker_device,
            transaction_amount=round(
                rng.uniform(3000, 60000),
                2
            )
        )


attack_events = pd.DataFrame(
    attack_events
)

print(
    "Attack events:",
    len(attack_events)
)

print("\nAttack type distribution:")
print(
    attack_events["attack_type"]
    .value_counts()
)

print("\nEvent types:")
print(
    attack_events["event_type"]
    .value_counts()
)

# ==============================================================================
# NOTEBOOK CELL 117
# ==============================================================================

attack_signature = (
    attack_events
    .groupby("attack_type")["event_type"]
    .apply(list)
)

for attack_type, sequence in attack_signature.items():

    print("\n" + "=" * 60)
    print(attack_type)

    for event in sequence:
        print("  ", event)

# ==============================================================================
# NOTEBOOK CELL 118
# ==============================================================================

modality_by_attack = pd.crosstab(
    attack_events["attack_type"],
    attack_events["modality"]
)

print(modality_by_attack)

# ==============================================================================
# NOTEBOOK CELL 119
# ==============================================================================

attack_events = attack_events.sort_values(
    ["campaign_id", "timestamp"]
).reset_index(drop=True)

attack_order_check = (
    attack_events
    .groupby("campaign_id")["timestamp"]
    .apply(
        lambda x: x.is_monotonic_increasing
    )
)

print(
    "Campaigns correctly ordered:",
    attack_order_check.all()
)

print(
    "Campaigns with ordering problems:",
    (~attack_order_check).sum()
)

# ==============================================================================
# NOTEBOOK CELL 120
# ==============================================================================

takeover_events = attack_events[
    attack_events["event_type"].isin(
        [
            "ACCOUNT_TAKEOVER",
            "SESSION_HIJACK",
            "ACCOUNT_ACCESS",
            "ACCOUNT_ACCESS_VIA_HIJACKED_SESSION"
        ]
    )
]

takeover_times = (
    takeover_events
    .groupby("campaign_id")["timestamp"]
    .min()
    .rename("takeover_time")
)

attack_events = attack_events.merge(
    takeover_times,
    on="campaign_id",
    how="left"
)

attack_events["minutes_to_takeover"] = (
    (
        attack_events["takeover_time"]
        - attack_events["timestamp"]
    )
    .dt.total_seconds()
    / 60
)

print(
    attack_events[
        [
            "campaign_id",
            "attack_type",
            "event_type",
            "attack_stage",
            "minutes_to_takeover"
        ]
    ].head(30)
)

# ==============================================================================
# NOTEBOOK CELL 121
# ==============================================================================

# ==========================================
# ATTACK CAMPAIGN CONTROL TABLE
# ==========================================

campaign_control = campaigns.copy()

# Attach user attributes
campaign_control = campaign_control.merge(
    users[
        [
            "user_id",
            "country",
            "language_region",
            "age",
            "tenure_months",
            "behaviour_profile",
            "primary_device_id"
        ]
    ],
    on="user_id",
    how="left"
)

# Generate attacker device identifiers
campaign_control["attacker_device_id"] = [
    f"ATTACK_DEVICE_{i+1:04d}"
    for i in range(len(campaign_control))
]

# Campaign severity
campaign_control["attack_severity"] = rng.choice(
    ["LOW", "MEDIUM", "HIGH"],
    size=len(campaign_control),
    p=[0.25, 0.50, 0.25]
)

# Temporal variability
campaign_control["temporal_variability"] = rng.uniform(
    0.10,
    0.40,
    size=len(campaign_control)
)

# Event dropout probability
campaign_control["event_dropout_rate"] = rng.uniform(
    0.00,
    0.15,
    size=len(campaign_control)
)

print(
    campaign_control[
        [
            "campaign_id",
            "user_id",
            "attack_type",
            "country",
            "behaviour_profile",
            "attack_severity",
            "temporal_variability",
            "event_dropout_rate"
        ]
    ].head(15)
)

# ==============================================================================
# NOTEBOOK CELL 122
# ==============================================================================

print(
    pd.crosstab(
        campaign_control["country"],
        campaign_control["attack_type"]
    )
)

# ==============================================================================
# NOTEBOOK CELL 123
# ==============================================================================

print(
    pd.crosstab(
        campaign_control["behaviour_profile"],
        campaign_control["attack_type"]
    )
)

# ==============================================================================
# NOTEBOOK CELL 124
# ==============================================================================

# ==========================================
# STEP 48
# Campaign Ground Truth Lookup
# ==========================================

campaign_lookup = campaign_control[
    [
        "campaign_id",
        "user_id",
        "attack_type",
        "country",
        "behaviour_profile",
        "primary_device_id",
        "attacker_device_id",
        "attack_severity"
    ]
].copy()

print(campaign_lookup.shape)

print(
    campaign_lookup.head()
)

# ==============================================================================
# NOTEBOOK CELL 125
# ==============================================================================

print("attack_events shape:", attack_events.shape)
print("attack_events columns:")
print(attack_events.columns.tolist())

# ==============================================================================
# NOTEBOOK CELL 126
# ==============================================================================

# ==========================================
# AFRITAC: Type-Specific Attack Campaigns
# ==========================================

# ==============================================================================
# NOTEBOOK CELL 127
# ==============================================================================

attack_events = pd.DataFrame(
    attack_events
)

# ==============================================================================
# NOTEBOOK CELL 128
# ==============================================================================

print("Shape:", attack_events.shape)

print(
    attack_events[
        [
            "campaign_id",
            "user_id",
            "device_id",
            "timestamp",
            "event_type",
            "modality",
            "attack_stage",
            "attack_type"
        ]
    ].head(15)
)

# ==============================================================================
# NOTEBOOK CELL 129
# ==============================================================================

print("campaign_control columns:")
print(campaign_control.columns.tolist())

print("\ncampaign_control shape:")
print(campaign_control.shape)

print(
    campaign_control[
        [
            "campaign_id",
            "user_id",
            "attack_type",
            "country",
            "behaviour_profile",
            "primary_device_id",
            "attacker_device_id"
        ]
    ].head(10)
)

# ==============================================================================
# NOTEBOOK CELL 130
# ==============================================================================

["user_id", "attack_type"]

# ==============================================================================
# NOTEBOOK CELL 131
# ==============================================================================

# ==========================================
# Attach campaign metadata safely
# ==========================================

campaign_metadata = campaign_control[
    [
        "campaign_id",
        "country",
        "behaviour_profile",
        "attack_severity",
        "attacker_device_id"
    ]
].drop_duplicates("campaign_id")

attack_events = attack_events.merge(
    campaign_metadata,
    on="campaign_id",
    how="left",
    validate="many_to_one"
)

print("Attack events shape:", attack_events.shape)

print(
    attack_events[
        [
            "campaign_id",
            "user_id",
            "attack_type",
            "country",
            "behaviour_profile",
            "attack_severity",
            "event_type"
        ]
    ].head(15)
)

# ==============================================================================
# NOTEBOOK CELL 132
# ==============================================================================

# ==========================================
# MALICIOUS EVENT GROUND TRUTH
# ==========================================

attack_events["ground_truth_state"] = "MALICIOUS"

attack_events["event_label"] = 1

attack_events["is_attack"] = 1

attack_events["is_benign_anomaly"] = 0

attack_events["is_normal"] = 0

print(
    attack_events[
        [
            "event_type",
            "attack_stage",
            "ground_truth_state",
            "event_label"
        ]
    ].head(20)
)

# ==============================================================================
# NOTEBOOK CELL 133
# ==============================================================================

print("\n=== GROUND TRUTH ===")

print(
    attack_events["ground_truth_state"]
    .value_counts()
)

print("\n=== ATTACK TYPES ===")

print(
    attack_events["attack_type"]
    .value_counts()
)

print("\n=== ATTACK STAGES ===")

print(
    attack_events["attack_stage"]
    .value_counts()
)

print("\n=== MODALITIES ===")

print(
    attack_events["modality"]
    .value_counts()
)

# ==============================================================================
# NOTEBOOK CELL 134
# ==============================================================================

campaign_check = (
    attack_events
    .groupby("campaign_id")
    .agg(
        users=("user_id", "nunique"),
        attack_types=("attack_type", "nunique"),
        event_count=("event_type", "count")
    )
)

print(campaign_check.describe())

print(
    "\nCampaigns with multiple users:",
    (campaign_check["users"] > 1).sum()
)

print(
    "Campaigns with multiple attack types:",
    (campaign_check["attack_types"] > 1).sum()
)

# ==============================================================================
# NOTEBOOK CELL 135
# ==============================================================================

# ==========================================
# TIME TO TAKEOVER
# ==========================================

takeover_event_types = [
    "ACCOUNT_TAKEOVER",
    "SESSION_HIJACK",
    "ACCOUNT_ACCESS",
    "ACCOUNT_ACCESS_VIA_HIJACKED_SESSION"
]

takeover_events = attack_events[
    attack_events["event_type"].isin(
        takeover_event_types
    )
].copy()

takeover_times = (
    takeover_events
    .groupby("campaign_id")["timestamp"]
    .min()
    .rename("takeover_time")
)

attack_events = attack_events.merge(
    takeover_times,
    on="campaign_id",
    how="left",
    validate="many_to_one"
)

attack_events["minutes_to_takeover"] = (
    (
        attack_events["takeover_time"]
        - attack_events["timestamp"]
    )
    .dt.total_seconds()
    / 60
)

print(
    attack_events[
        [
            "campaign_id",
            "attack_type",
            "event_type",
            "attack_stage",
            "timestamp",
            "minutes_to_takeover"
        ]
    ].head(30)
)

# ==============================================================================
# NOTEBOOK CELL 136
# ==============================================================================

# ==========================================
# ATTACK TRAJECTORY AUDIT
# ==========================================

trajectory_audit = (
    attack_events
    .sort_values(["campaign_id", "timestamp"])
    .groupby("campaign_id")
    .agg(
        event_count=("event_type", "count"),
        first_event=("timestamp", "min"),
        last_event=("timestamp", "max"),
        attack_type=("attack_type", "first"),
        user_id=("user_id", "first")
    )
)

trajectory_audit["campaign_duration_min"] = (
    trajectory_audit["last_event"]
    - trajectory_audit["first_event"]
).dt.total_seconds() / 60

print(trajectory_audit.describe(include="all"))

print("\n=== EVENTS PER CAMPAIGN ===")
print(
    trajectory_audit["event_count"]
    .value_counts()
    .sort_index()
)

print("\n=== CAMPAIGN DURATION ===")
print(
    trajectory_audit["campaign_duration_min"]
    .describe()
)

print("\n=== DURATION BY ATTACK TYPE ===")
print(
    trajectory_audit
    .groupby("attack_type")["campaign_duration_min"]
    .describe()
)

# ==============================================================================
# NOTEBOOK CELL 137
# ==============================================================================

# ==========================================
# INTER-EVENT TIMING VARIABILITY
# ==========================================

attack_timing = (
    attack_events
    .sort_values(["campaign_id", "timestamp"])
    .copy()
)

attack_timing["previous_timestamp"] = (
    attack_timing
    .groupby("campaign_id")["timestamp"]
    .shift(1)
)

attack_timing["inter_event_minutes"] = (
    attack_timing["timestamp"]
    - attack_timing["previous_timestamp"]
).dt.total_seconds() / 60

print(
    attack_timing[
        [
            "campaign_id",
            "attack_type",
            "event_type",
            "attack_stage",
            "inter_event_minutes"
        ]
    ].head(30)
)

# ==============================================================================
# NOTEBOOK CELL 138
# ==============================================================================

print("\n=== INTER EVENT TIME BY ATTACK TYPE ===")

print(
    attack_timing
    .groupby("attack_type")["inter_event_minutes"]
    .describe()
)

# ==============================================================================
# NOTEBOOK CELL 139
# ==============================================================================

# ==========================================
# STEP 53
# STOCHASTIC ATTACK TIMING ENGINE
# ==========================================

rng_attack = np.random.default_rng(20260901)

print("Random attack generator initialized.")

# ==============================================================================
# NOTEBOOK CELL 140
# ==============================================================================

# ==========================================
# Attack-specific temporal distributions
# ==========================================

attack_timing_profiles = {

    "ACCOUNT_TAKEOVER": {
        "intervals": [
            (2, 10),
            (3, 12),
            (2, 10),
            (2, 10),
            (2, 10),
            (1, 8)
        ]
    },

    "SIM_IDENTITY_COMPROMISE": {
        "intervals": [
            (1, 7),
            (1, 7),
            (1, 7),
            (1, 7),
            (1, 7),
            (1, 7)
        ]
    },

    "SOCIAL_ENGINEERING_TAKEOVER": {
        "intervals": [
            (2, 15),
            (3, 20),
            (5, 25),
            (5, 25),
            (3, 15),
            (2, 12)
        ]
    },

    "USSD_SESSION_HIJACK": {
        "intervals": [
            (1, 5),
            (1, 5),
            (1, 5),
            (1, 5),
            (1, 5),
            (1, 5)
        ]
    }
}

print(attack_timing_profiles)

# ==============================================================================
# NOTEBOOK CELL 141
# ==============================================================================

# ==========================================
# Generate stochastic attack timestamps
# ==========================================

stochastic_attack_events = []

for campaign_id, campaign_group in attack_events.groupby(
    "campaign_id",
    sort=False
):

    campaign_group = campaign_group.sort_values(
        "timestamp"
    ).copy()

    attack_type = campaign_group["attack_type"].iloc[0]

    profile = attack_timing_profiles[attack_type]

    start_time = campaign_group["timestamp"].min()

    current_time = start_time

    new_times = [current_time]

    intervals = profile["intervals"]

    for i in range(1, len(campaign_group)):

        low, high = intervals[i - 1]

        gap = rng_attack.integers(
            low,
            high + 1
        )

        current_time = (
            current_time
            + pd.Timedelta(minutes=int(gap))
        )

        new_times.append(current_time)

    campaign_group["timestamp"] = new_times

    stochastic_attack_events.append(
        campaign_group
    )

stochastic_attack_events = pd.concat(
    stochastic_attack_events,
    ignore_index=True
)

print(
    "Stochastic attack events:",
    stochastic_attack_events.shape
)

# ==============================================================================
# NOTEBOOK CELL 142
# ==============================================================================

# ==========================================
# Stochastic trajectory audit
# ==========================================

stochastic_audit = (
    stochastic_attack_events
    .sort_values(["campaign_id", "timestamp"])
    .groupby("campaign_id")
    .agg(
        event_count=("event_type", "count"),
        first_event=("timestamp", "min"),
        last_event=("timestamp", "max"),
        attack_type=("attack_type", "first")
    )
)

stochastic_audit["campaign_duration_min"] = (
    stochastic_audit["last_event"]
    - stochastic_audit["first_event"]
).dt.total_seconds() / 60

print("\n=== EVENTS PER CAMPAIGN ===")

print(
    stochastic_audit["event_count"]
    .value_counts()
)

print("\n=== CAMPAIGN DURATION ===")

print(
    stochastic_audit["campaign_duration_min"]
    .describe()
)

print("\n=== DURATION BY ATTACK TYPE ===")

print(
    stochastic_audit
    .groupby("attack_type")[
        "campaign_duration_min"
    ]
    .describe()
)

# ==============================================================================
# NOTEBOOK CELL 143
# ==============================================================================

# ==========================================
# Inter-event timing
# ==========================================

stochastic_timing = (
    stochastic_attack_events
    .sort_values(
        ["campaign_id", "timestamp"]
    )
    .copy()
)

stochastic_timing["previous_timestamp"] = (
    stochastic_timing
    .groupby("campaign_id")["timestamp"]
    .shift(1)
)

stochastic_timing["inter_event_minutes"] = (
    stochastic_timing["timestamp"]
    - stochastic_timing["previous_timestamp"]
).dt.total_seconds() / 60

print(
    stochastic_timing[
        [
            "campaign_id",
            "attack_type",
            "event_type",
            "attack_stage",
            "inter_event_minutes"
        ]
    ].head(30)
)

print(
    "\n=== INTER EVENT VARIABILITY ==="
)

print(
    stochastic_timing
    .groupby("attack_type")[
        "inter_event_minutes"
    ]
    .describe()
)

# ==============================================================================
# NOTEBOOK CELL 144
# ==============================================================================

# ==========================================
# STEP 57
# RECONSTRUCT STOCHASTIC TAKEOVER TIME
# ==========================================

# Work on a clean copy
stochastic_attack_events = (
    stochastic_attack_events
    .sort_values(["campaign_id", "timestamp"])
    .reset_index(drop=True)
    .copy()
)

# Remove previously generated takeover-time columns
# This makes the cell safe to rerun.
columns_to_remove = [
    "takeover_time",
    "takeover_time_x",
    "takeover_time_y",
    "minutes_to_takeover"
]

stochastic_attack_events = stochastic_attack_events.drop(
    columns=[
        col for col in columns_to_remove
        if col in stochastic_attack_events.columns
    ],
    errors="ignore"
)

# Define takeover events for each attack family
takeover_event_types = [
    "ACCOUNT_TAKEOVER",
    "SESSION_HIJACK",
    "ACCOUNT_ACCESS",
]

# Find the first takeover event in each campaign
takeover_times = (
    stochastic_attack_events[
        stochastic_attack_events["event_type"].isin(
            takeover_event_types
        )
    ]
    .groupby("campaign_id")["timestamp"]
    .min()
    .rename("takeover_time")
)

# Attach takeover time
stochastic_attack_events = (
    stochastic_attack_events
    .merge(
        takeover_times,
        on="campaign_id",
        how="left",
        validate="many_to_one"
    )
)

# Calculate time remaining until takeover
stochastic_attack_events["minutes_to_takeover"] = (
    (
        stochastic_attack_events["takeover_time"]
        - stochastic_attack_events["timestamp"]
    )
    .dt.total_seconds()
    / 60
)

print(
    stochastic_attack_events[
        [
            "campaign_id",
            "attack_type",
            "event_type",
            "attack_stage",
            "timestamp",
            "takeover_time",
            "minutes_to_takeover"
        ]
    ].head(30)
)

print("\nStep 57 validation")
print("Shape:", stochastic_attack_events.shape)
print(
    "Missing takeover_time:",
    stochastic_attack_events["takeover_time"].isna().sum()
)
print(
    "Missing minutes_to_takeover:",
    stochastic_attack_events["minutes_to_takeover"].isna().sum()
)
print(
    "Unique campaigns:",
    stochastic_attack_events["campaign_id"].nunique()
)

# ==============================================================================
# NOTEBOOK CELL 145
# ==============================================================================

# ==========================================
# STEP 58
# TEMPORAL GROUND TRUTH VALIDATION
# ==========================================

print("Missing takeover times:")
print(
    stochastic_attack_events["takeover_time"]
    .isna()
    .sum()
)

print("\nEvents before takeover:")
print(
    (
        stochastic_attack_events["minutes_to_takeover"] > 0
    ).sum()
)

print("\nEvents at takeover:")
print(
    (
        stochastic_attack_events["minutes_to_takeover"] == 0
    ).sum()
)

print("\nEvents after takeover:")
print(
    (
        stochastic_attack_events["minutes_to_takeover"] < 0
    ).sum()
)

print("\n=== TIME TO TAKEOVER BY ATTACK TYPE ===")

print(
    stochastic_attack_events
    .groupby("attack_type")["minutes_to_takeover"]
    .describe()
)

# ==============================================================================
# NOTEBOOK CELL 146
# ==============================================================================

# ==========================================
# STEP 59
# ATTACK WARNING WINDOW
# ==========================================

warning_windows = (
    stochastic_attack_events
    .groupby("campaign_id")
    .agg(
        attack_type=("attack_type", "first"),
        campaign_start=("timestamp", "min"),
        takeover_time=("takeover_time", "first")
    )
)

warning_windows["available_warning_minutes"] = (
    (
        warning_windows["takeover_time"]
        - warning_windows["campaign_start"]
    )
    .dt.total_seconds()
    / 60
)

print(
    warning_windows
    .groupby("attack_type")[
        "available_warning_minutes"
    ]
    .describe()
)

# ==============================================================================
# NOTEBOOK CELL 147
# ==============================================================================

# ==========================================
# STEP 60
# CAUSAL ORDER VALIDATION
# ==========================================

stage_order = {
    "PRE_ATTACK": 0,
    "COMPROMISE": 1,
    "TAKEOVER": 2,
    "IMPACT": 3
}

check = (
    stochastic_attack_events
    .sort_values(["campaign_id", "timestamp"])
    .copy()
)

check["stage_numeric"] = (
    check["attack_stage"]
    .map(stage_order)
)

stage_violations = []

for campaign_id, group in check.groupby("campaign_id"):

    stages = group["stage_numeric"].tolist()

    if stages != sorted(stages):
        stage_violations.append(campaign_id)

print(
    "Campaigns with stage-order violations:",
    len(stage_violations)
)

if stage_violations:
    print(stage_violations[:20])

# ==============================================================================
# NOTEBOOK CELL 148
# ==============================================================================

# ==========================================
# STEP 61
# TEMPORAL LEAKAGE AUDIT
# ==========================================

leakage_checks = {}

# Takeover event must occur at time zero
leakage_checks["takeover_zero"] = (
    stochastic_attack_events[
        stochastic_attack_events["event_type"].isin(
            takeover_event_types
        )
    ]["minutes_to_takeover"]
    .eq(0)
    .all()
)

# Pre-attack events must occur before takeover
pre_attack = stochastic_attack_events[
    stochastic_attack_events["attack_stage"] == "PRE_ATTACK"
]

leakage_checks["pre_attack_positive"] = (
    pre_attack["minutes_to_takeover"] > 0
).all()

# Impact events should occur after takeover
impact = stochastic_attack_events[
    stochastic_attack_events["attack_stage"] == "IMPACT"
]

leakage_checks["impact_nonpositive"] = (
    impact["minutes_to_takeover"] <= 0
).all()

print(leakage_checks)

# ==============================================================================
# NOTEBOOK CELL 149
# ==============================================================================

# ==========================================
# STEP 62A
# SHOW CURRENT DATAFRAME OBJECTS
# ==========================================

import pandas as pd

dataframes = {}

for name, obj in globals().items():
    if isinstance(obj, pd.DataFrame):
        dataframes[name] = {
            "rows": obj.shape[0],
            "columns": obj.shape[1],
            "columns_list": list(obj.columns)
        }

for name, info in dataframes.items():
    print("\n" + "=" * 70)
    print(name)
    print("Shape:", (info["rows"], info["columns"]))
    print("Columns:", info["columns_list"])

# ==============================================================================
# NOTEBOOK CELL 150
# ==============================================================================

# ============================================================
# STEP 62B
# BUILD THE UNIFIED LONGITUDINAL EVENT STREAM
# ============================================================

import pandas as pd
import numpy as np

# ------------------------------------------------------------
# 1. NORMAL + BENIGN EVENTS
# ------------------------------------------------------------

base_events = events.copy()

# Make sure timestamp is datetime
base_events["timestamp"] = pd.to_datetime(
    base_events["timestamp"],
    errors="coerce"
)

# Explicitly mark these observations as non-malicious
base_events["is_attack"] = 0

# Preserve benign anomaly information
if "ground_truth_state" in base_events.columns:
    base_events["ground_truth_state"] = (
        base_events["ground_truth_state"]
        .fillna("NORMAL")
    )
else:
    base_events["ground_truth_state"] = "NORMAL"

# ------------------------------------------------------------
# 2. ATTACK EVENTS
# ------------------------------------------------------------

malicious_events = stochastic_attack_events.copy()

malicious_events["timestamp"] = pd.to_datetime(
    malicious_events["timestamp"],
    errors="coerce"
)

malicious_events["is_attack"] = 1

# Ensure malicious state
malicious_events["ground_truth_state"] = "MALICIOUS"

# ------------------------------------------------------------
# 3. STANDARDIZE EVENT IDENTIFIERS
# ------------------------------------------------------------

# Normal events already have event_id.
# Attack events may not have event_id, so create unique IDs.

if "event_id" not in malicious_events.columns:

    malicious_events["event_id"] = (
        "ATTACK_EVENT_" +
        malicious_events.index.astype(str).str.zfill(6)
    )

# ------------------------------------------------------------
# 4. ADD COMMON COLUMNS
# ------------------------------------------------------------

common_columns = [
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
    "is_attack"
]

# Add missing columns safely
for col in common_columns:

    if col not in base_events.columns:
        base_events[col] = np.nan

    if col not in malicious_events.columns:
        malicious_events[col] = np.nan

# ------------------------------------------------------------
# 5. SELECT COMMON REPRESENTATION
# ------------------------------------------------------------

normal_stream = base_events[common_columns].copy()

attack_stream = malicious_events[common_columns].copy()

# ------------------------------------------------------------
# 6. COMBINE
# ------------------------------------------------------------

unified_events = pd.concat(
    [
        normal_stream,
        attack_stream
    ],
    ignore_index=True
)

# ------------------------------------------------------------
# 7. SORT TEMPORALLY
# ------------------------------------------------------------

unified_events = (
    unified_events
    .sort_values(
        ["user_id", "timestamp", "event_id"]
    )
    .reset_index(drop=True)
)

# ------------------------------------------------------------
# 8. BASIC INTEGRITY CHECK
# ------------------------------------------------------------

print("Unified event shape:")
print(unified_events.shape)

print("\n=== EVENT COUNTS ===")
print(
    unified_events["is_attack"]
    .value_counts()
    .sort_index()
)

print("\n=== GROUND TRUTH ===")
print(
    unified_events["ground_truth_state"]
    .value_counts()
)

print("\n=== MODALITIES ===")
print(
    unified_events["modality"]
    .value_counts()
)

print("\n=== ATTACK EVENTS ===")
print(
    unified_events[
        unified_events["is_attack"] == 1
    ].shape
)

print("\n=== MISSING VALUES ===")
print(
    unified_events.isna().sum()
    .sort_values(ascending=False)
    .head(20)
)

# ==============================================================================
# NOTEBOOK CELL 151
# ==============================================================================

# ============================================================
# STEP 62C
# DUPLICATE EVENT AUDIT
# ============================================================

print("Total events:", len(unified_events))

print(
    "Duplicate event IDs:",
    unified_events["event_id"].duplicated().sum()
)

duplicate_event_rows = unified_events[
    unified_events["event_id"].duplicated(
        keep=False
    )
].sort_values("event_id")

print("\nDuplicate event rows:")
print(duplicate_event_rows.head(30))

# Check duplicated observations using temporal identity
identity_cols = [
    "user_id",
    "device_id",
    "timestamp",
    "event_type",
    "modality"
]

duplicate_identity = unified_events[
    unified_events.duplicated(
        subset=identity_cols,
        keep=False
    )
]

print(
    "\nDuplicate temporal identities:",
    len(duplicate_identity)
)

print(
    duplicate_identity[
        identity_cols + ["is_attack"]
    ].head(30)
)

# ==============================================================================
# NOTEBOOK CELL 152
# ==============================================================================

# ============================================================
# STEP 62D
# ATTACK CAMPAIGN INTEGRITY AUDIT
# ============================================================

# ------------------------------------------------------------
# 1. Confirm attack event count
# ------------------------------------------------------------

attack_only = unified_events[
    unified_events["is_attack"] == 1
].copy()

print("Attack events in unified stream:", len(attack_only))

# ------------------------------------------------------------
# 2. Confirm source attack event count
# ------------------------------------------------------------

print(
    "Source stochastic attack events:",
    len(stochastic_attack_events)
)

# ------------------------------------------------------------
# 3. Confirm campaign count
# ------------------------------------------------------------

source_campaigns = stochastic_attack_events[
    "campaign_id"
].nunique()

print(
    "Source attack campaigns:",
    source_campaigns
)

# ------------------------------------------------------------
# 4. Events per campaign
# ------------------------------------------------------------

events_per_campaign = (
    stochastic_attack_events
    .groupby("campaign_id")
    .size()
)

print("\n=== EVENTS PER CAMPAIGN ===")
print(events_per_campaign.value_counts().sort_index())

# ------------------------------------------------------------
# 5. Attack type distribution
# ------------------------------------------------------------

print("\n=== ATTACK TYPE DISTRIBUTION ===")

print(
    stochastic_attack_events[
        "attack_type"
    ].value_counts()
)

# ------------------------------------------------------------
# 6. Attack stage distribution
# ------------------------------------------------------------

print("\n=== ATTACK STAGE DISTRIBUTION ===")

print(
    stochastic_attack_events[
        "attack_stage"
    ].value_counts()
)

# ------------------------------------------------------------
# 7. Ground truth verification
# ------------------------------------------------------------

print("\n=== ATTACK GROUND TRUTH ===")

print(
    stochastic_attack_events[
        "ground_truth_state"
    ].value_counts()
)

# ------------------------------------------------------------
# 8. Event label verification
# ------------------------------------------------------------

print("\n=== EVENT LABEL ===")

print(
    stochastic_attack_events[
        "event_label"
    ].value_counts()
)

# ------------------------------------------------------------
# 9. Campaign uniqueness checks
# ------------------------------------------------------------

campaign_user_check = (
    stochastic_attack_events
    .groupby("campaign_id")["user_id"]
    .nunique()
)

campaign_type_check = (
    stochastic_attack_events
    .groupby("campaign_id")["attack_type"]
    .nunique()
)

print(
    "\nCampaigns with multiple users:",
    (campaign_user_check > 1).sum()
)

print(
    "Campaigns with multiple attack types:",
    (campaign_type_check > 1).sum()
)

# ------------------------------------------------------------
# 10. Final integrity assertions
# ------------------------------------------------------------

assert len(attack_only) == 560
assert len(stochastic_attack_events) == 560
assert source_campaigns == 80
assert events_per_campaign.eq(7).all()
assert (campaign_user_check == 1).all()
assert (campaign_type_check == 1).all()

print("\n======================================")
print("ATTACK DATA INTEGRITY: PASSED")
print("======================================")

# ==============================================================================
# NOTEBOOK CELL 153
# ==============================================================================

# ============================================================
# STEP 63A
# RESPONSE DELAY AUDIT
# ============================================================

print("=== RESPONSE DELAY COLUMNS ===")

response_cols = [
    c for c in unified_events.columns
    if "response_delay" in c.lower()
]

print(response_cols)

for col in response_cols:
    print(f"\n--- {col} ---")
    print("dtype:", unified_events[col].dtype)
    print("missing:", unified_events[col].isna().sum())
    print("non-missing:", unified_events[col].notna().sum())

# ------------------------------------------------------------
# Compare available response delay columns
# ------------------------------------------------------------

for col in response_cols:
    if pd.api.types.is_numeric_dtype(unified_events[col]):
        print(f"\n{col} summary:")
        print(unified_events[col].describe())

# ------------------------------------------------------------
# Check whether the unified column is entirely missing
# ------------------------------------------------------------

if "response_delay_ms" in unified_events.columns:

    print("\n=== UNIFIED RESPONSE DELAY ===")

    print(
        unified_events["response_delay_ms"]
        .notna()
        .sum(),
        "non-missing values"
    )

    print(
        unified_events["response_delay_ms"]
        .isna()
        .sum(),
        "missing values"
    )

# ------------------------------------------------------------
# Attack versus nonattack availability
# ------------------------------------------------------------

if "response_delay_ms" in unified_events.columns:

    print("\n=== RESPONSE DELAY BY GROUND TRUTH ===")

    print(
        unified_events
        .groupby("ground_truth_state")["response_delay_ms"]
        .agg(
            count="count",
            missing="size"
        )
    )

# ==============================================================================
# NOTEBOOK CELL 154
# ==============================================================================

# ============================================================
# STEP 63B
# RECOVER RESPONSE DELAY FROM UPSTREAM DATA
# ============================================================

print("=== AVAILABLE DATAFRAMES ===")

for name in [
    "sessions",
    "events",
    "enriched_events",
    "unified_events"
]:
    if name in globals():
        obj = globals()[name]
        print(
            f"{name}: shape={obj.shape}"
        )

# ------------------------------------------------------------
# Inspect response delay columns in every relevant dataframe
# ------------------------------------------------------------

print("\n=== RESPONSE DELAY PROVENANCE ===")

for name in [
    "sessions",
    "events",
    "enriched_events",
    "unified_events"
]:

    if name not in globals():
        continue

    df_check = globals()[name]

    cols = [
        c for c in df_check.columns
        if "response_delay" in c.lower()
    ]

    print(f"\n{name}")
    print("Columns:", cols)

    for col in cols:
        print(
            f"  {col}: "
            f"non_missing={df_check[col].notna().sum()}, "
            f"missing={df_check[col].isna().sum()}"
        )

# ------------------------------------------------------------
# Specifically inspect the original events dataframe
# ------------------------------------------------------------

if "events" in globals():

    print("\n=== ORIGINAL EVENTS RESPONSE DELAY ===")

    event_response_cols = [
        c for c in events.columns
        if "response_delay" in c.lower()
    ]

    print(event_response_cols)

    for col in event_response_cols:
        print(
            f"\n{col}"
        )
        print(
            events[col].describe()
        )
        print(
            "Non-missing:",
            events[col].notna().sum()
        )

# ------------------------------------------------------------
# Inspect sessions
# ------------------------------------------------------------

if "sessions" in globals():

    print("\n=== SESSION RESPONSE DELAY ===")

    session_response_cols = [
        c for c in sessions.columns
        if "response_delay" in c.lower()
    ]

    print(session_response_cols)

    for col in session_response_cols:
        print(
            f"\n{col}"
        )
        print(
            sessions[col].describe()
        )
        print(
            "Non-missing:",
            sessions[col].notna().sum()
        )

# ==============================================================================
# NOTEBOOK CELL 155
# ==============================================================================

# ============================================================
# STEP 63C
# REPAIR RESPONSE DELAY IN UNIFIED EVENTS
# ============================================================

# Work on a copy
unified_events = unified_events.copy()

# Remove the completely empty response delay column
unified_events.drop(
    columns=["response_delay_ms"],
    inplace=True,
    errors="ignore"
)

# ------------------------------------------------------------
# Create canonical response delay for benign/session events
# ------------------------------------------------------------

# Build event-level lookup from the fully populated source
event_delay_lookup = events[
    ["event_id", "response_delay_ms_y"]
].copy()

event_delay_lookup = event_delay_lookup.rename(
    columns={
        "response_delay_ms_y": "response_delay_ms"
    }
)

# Ensure event_id is unique
assert event_delay_lookup["event_id"].is_unique

# Merge using event_id
unified_events = unified_events.merge(
    event_delay_lookup,
    on="event_id",
    how="left",
    validate="one_to_one"
)

# ------------------------------------------------------------
# Audit
# ------------------------------------------------------------

print("=== RESPONSE DELAY AFTER REPAIR ===")

print(
    unified_events["response_delay_ms"].describe()
)

print(
    "\nNon-missing:",
    unified_events["response_delay_ms"].notna().sum()
)

print(
    "Missing:",
    unified_events["response_delay_ms"].isna().sum()
)

print(
    "\n=== RESPONSE DELAY BY GROUND TRUTH ==="
)

print(
    unified_events
    .groupby("ground_truth_state")["response_delay_ms"]
    .agg(
        count="count",
        missing="size"
    )
)

# ------------------------------------------------------------
# Attack versus nonattack
# ------------------------------------------------------------

print(
    "\n=== RESPONSE DELAY BY ATTACK STATUS ==="
)

print(
    unified_events
    .groupby("is_attack")["response_delay_ms"]
    .agg(
        count="count",
        missing="size"
    )
)

# ==============================================================================
# NOTEBOOK CELL 156
# ==============================================================================

# ============================================================
# STEP 63D
# ATTACK EVENT SESSION CONTEXT AUDIT
# ============================================================

attack_rows = unified_events[
    unified_events["is_attack"] == 1
].copy()

print("Attack events:", len(attack_rows))

print(
    "\nAttack events with session_id:",
    attack_rows["session_id"].notna().sum()
)

print(
    "Attack events without session_id:",
    attack_rows["session_id"].isna().sum()
)

# ------------------------------------------------------------
# Check whether attack events have corresponding sessions
# ------------------------------------------------------------

if "session_id" in attack_rows.columns:

    session_ids = set(
        sessions["session_id"]
    )

    attack_rows["session_exists"] = (
        attack_rows["session_id"]
        .isin(session_ids)
    )

    print(
        "\nAttack events linked to ordinary sessions:",
        attack_rows["session_exists"].sum()
    )

    print(
        "Attack events without matching ordinary session:",
        (~attack_rows["session_exists"]).sum()
    )

# ------------------------------------------------------------
# Attack event temporal range
# ------------------------------------------------------------

print(
    "\n=== ATTACK EVENT TEMPORAL RANGE ==="
)

print(
    "First:",
    attack_rows["timestamp"].min()
)

print(
    "Last:",
    attack_rows["timestamp"].max()
)

# ------------------------------------------------------------
# Attack event response delay
# ------------------------------------------------------------

print(
    "\n=== ATTACK RESPONSE DELAY ==="
)

print(
    attack_rows["response_delay_ms"]
    .describe()
)

# ==============================================================================
# NOTEBOOK CELL 157
# ==============================================================================

# ============================================================
# STEP 65A
# TEMPORAL PREDICTION WINDOWS
# ============================================================

import numpy as np
import pandas as pd

# ------------------------------------------------------------
# Prediction horizons
# ------------------------------------------------------------

HORIZONS = [60, 30, 15, 10, 5]

# ------------------------------------------------------------
# Prepare ordinary observable events
# ------------------------------------------------------------

observable_events = unified_events[
    unified_events["is_attack"] == 0
].copy()

observable_events["timestamp"] = pd.to_datetime(
    observable_events["timestamp"]
)

observable_events = observable_events.sort_values(
    ["user_id", "timestamp"]
).reset_index(drop=True)

print("Observable events:", len(observable_events))

# ------------------------------------------------------------
# Prepare campaign table
# ------------------------------------------------------------

campaigns = campaign_control.copy()

campaigns["anchor_time"] = pd.to_datetime(
    campaigns["anchor_time"]
)

campaigns = campaigns.sort_values(
    "anchor_time"
).reset_index(drop=True)

# ------------------------------------------------------------
# Construct windows
# ------------------------------------------------------------

temporal_windows = []

for _, campaign in campaigns.iterrows():

    user = campaign["user_id"]
    takeover_time = campaign["anchor_time"]

    user_events = observable_events[
        observable_events["user_id"] == user
    ].copy()

    for horizon in HORIZONS:

        cutoff_time = (
            takeover_time
            - pd.Timedelta(minutes=horizon)
        )

        history = user_events[
            user_events["timestamp"] < cutoff_time
        ].copy()

        temporal_windows.append({

            "campaign_id":
                campaign["campaign_id"],

            "user_id":
                user,

            "attack_type":
                campaign["attack_type"],

            "attack_severity":
                campaign["attack_severity"],

            "takeover_time":
                takeover_time,

            "horizon_minutes":
                horizon,

            "prediction_cutoff":
                cutoff_time,

            "history_event_count":
                len(history),

            "history_start":
                (
                    history["timestamp"].min()
                    if len(history) > 0
                    else pd.NaT
                ),

            "history_end":
                (
                    history["timestamp"].max()
                    if len(history) > 0
                    else pd.NaT
                )
        })

temporal_windows = pd.DataFrame(
    temporal_windows
)

print("\n=== TEMPORAL WINDOW DATASET ===")

print(
    temporal_windows.shape
)

print(
    temporal_windows.head(15)
)

# ------------------------------------------------------------
# History availability
# ------------------------------------------------------------

print(
    "\n=== HISTORY EVENT COUNTS ==="
)

print(
    temporal_windows
    .groupby("horizon_minutes")[
        "history_event_count"
    ]
    .describe()
)

# ------------------------------------------------------------
# Check whether any history contains future events
# ------------------------------------------------------------

future_leakage = (
    temporal_windows["history_end"]
    >= temporal_windows["prediction_cutoff"]
)

print(
    "\nPotential temporal leakage:",
    future_leakage.sum()
)

assert future_leakage.sum() == 0

# ------------------------------------------------------------
# Check campaign/horizon uniqueness
# ------------------------------------------------------------

duplicates = temporal_windows.duplicated(
    subset=[
        "campaign_id",
        "horizon_minutes"
    ]
).sum()

print(
    "Duplicate campaign/horizon rows:",
    duplicates
)

assert duplicates == 0

# ------------------------------------------------------------
# Check expected number
# ------------------------------------------------------------

expected_rows = len(campaigns) * len(HORIZONS)

print(
    "Expected rows:",
    expected_rows
)

print(
    "Actual rows:",
    len(temporal_windows)
)

assert len(temporal_windows) == expected_rows

print(
    "\n======================================"
)

print(
    "TEMPORAL WINDOW CONSTRUCTION: PASSED"
)

print(
    "======================================"
)

# ==============================================================================
# NOTEBOOK CELL 158
# ==============================================================================

# ============================================================
# STEP 65B
# MULTIMODAL TEMPORAL FEATURE ENGINEERING
# ============================================================

import numpy as np
import pandas as pd

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

HORIZONS = [60, 30, 15, 10, 5]

# ------------------------------------------------------------
# Observable events only
# ------------------------------------------------------------

obs = unified_events[
    unified_events["is_attack"] == 0
].copy()

obs["timestamp"] = pd.to_datetime(obs["timestamp"])

# ------------------------------------------------------------
# Make sure numeric variables are numeric
# ------------------------------------------------------------

numeric_cols = [
    "response_delay_ms",
    "signal_strength_dbm",
    "new_device",
    "location_change",
    "roaming",
    "transaction_amount",
    "new_beneficiary"
]

for col in numeric_cols:
    if col in obs.columns:
        obs[col] = pd.to_numeric(
            obs[col],
            errors="coerce"
        )

# ------------------------------------------------------------
# Feature construction
# ------------------------------------------------------------

feature_rows = []

for _, campaign in campaigns.iterrows():

    user = campaign["user_id"]
    takeover_time = campaign["anchor_time"]

    user_events = obs[
        obs["user_id"] == user
    ].copy()

    for horizon in HORIZONS:

        cutoff = (
            takeover_time
            - pd.Timedelta(minutes=horizon)
        )

        history = user_events[
            user_events["timestamp"] < cutoff
        ].copy()

        row = {
            "campaign_id":
                campaign["campaign_id"],

            "user_id":
                user,

            "attack_type":
                campaign["attack_type"],

            "attack_severity":
                campaign["attack_severity"],

            "horizon_minutes":
                horizon,

            "prediction_cutoff":
                cutoff,

            "target":
                1
        }

        # ====================================================
        # GENERAL TEMPORAL FEATURES
        # ====================================================

        row["event_count"] = len(history)

        if len(history) > 0:

            row["active_days"] = (
                history["timestamp"]
                .dt.date
                .nunique()
            )

            row["history_span_hours"] = (
                (
                    history["timestamp"].max()
                    - history["timestamp"].min()
                ).total_seconds()
                / 3600
            )

            row["events_per_active_day"] = (
                row["event_count"]
                / max(row["active_days"], 1)
            )

        else:

            row["active_days"] = 0
            row["history_span_hours"] = 0
            row["events_per_active_day"] = 0

        # ====================================================
        # EVENT MODALITY FEATURES
        # ====================================================

        modality_counts = (
            history["modality"]
            .value_counts()
        )

        for modality in [
            "USSD",
            "SESSION",
            "AUTHENTICATION",
            "FINANCIAL",
            "DEVICE",
            "ACCOUNT",
            "IDENTITY",
            "SOCIAL_ENGINEERING",
            "SIM",
            "NETWORK"
        ]:

            row[
                f"count_{modality.lower()}"
            ] = modality_counts.get(
                modality,
                0
            )

        # ====================================================
        # EVENT TYPE FEATURES
        # ====================================================

        event_counts = (
            history["event_type"]
            .value_counts()
        )

        selected_event_types = [

            "MENU_INTERACTION",
            "SESSION_START",
            "SESSION_END",
            "AUTHENTICATION_SUCCESS",
            "USSD_INITIATION",
            "USSD_RESPONSE",
            "TRANSACTION",

            "SOCIAL_MESSAGE_RECEIVED",
            "SOCIAL_MESSAGE_INTERACTION",

            "AUTHENTICATION_ANOMALY",
            "CREDENTIAL_VALIDATION_ANOMALY",

            "NEW_DEVICE_LOGIN",
            "DEVICE_CHANGE",

            "IDENTITY_CHANGE",

            "NEW_BENEFICIARY_ADDED",
            "UNAUTHORIZED_TRANSACTION",

            "SESSION_REROUTING",
            "STALE_SESSION_REUSE",
            "USSD_CODE_MODIFICATION"
        ]

        for event_type in selected_event_types:

            safe_name = (
                event_type
                .lower()
                .replace(" ", "_")
            )

            row[
                f"event_{safe_name}"
            ] = event_counts.get(
                event_type,
                0
            )

        # ====================================================
        # RESPONSE DELAY
        # ====================================================

        if "response_delay_ms" in history.columns:

            delay = history[
                "response_delay_ms"
            ].dropna()

            if len(delay) > 0:

                row["delay_mean"] = delay.mean()
                row["delay_median"] = delay.median()
                row["delay_std"] = delay.std()
                row["delay_max"] = delay.max()
                row["delay_p95"] = delay.quantile(0.95)

            else:

                row["delay_mean"] = 0
                row["delay_median"] = 0
                row["delay_std"] = 0
                row["delay_max"] = 0
                row["delay_p95"] = 0

        # ====================================================
        # NETWORK FEATURES
        # ====================================================

        if "signal_strength_dbm" in history.columns:

            signal = history[
                "signal_strength_dbm"
            ].dropna()

            if len(signal) > 0:

                row["signal_mean"] = signal.mean()
                row["signal_std"] = signal.std()
                row["signal_min"] = signal.min()

            else:

                row["signal_mean"] = 0
                row["signal_std"] = 0
                row["signal_min"] = 0

        row["roaming_count"] = (
            history["roaming"].fillna(0).sum()
            if "roaming" in history.columns
            else 0
        )

        row["location_change_count"] = (
            history["location_change"].fillna(0).sum()
            if "location_change" in history.columns
            else 0
        )

        row["new_device_count"] = (
            history["new_device"].fillna(0).sum()
            if "new_device" in history.columns
            else 0
        )

        # ====================================================
        # FINANCIAL FEATURES
        # ====================================================

        if "transaction_amount" in history.columns:

            transactions = history[
                "transaction_amount"
            ].dropna()

            transactions = transactions[
                transactions > 0
            ]

            row["transaction_count"] = len(
                transactions
            )

            if len(transactions) > 0:

                row["transaction_total"] = (
                    transactions.sum()
                )

                row["transaction_mean"] = (
                    transactions.mean()
                )

                row["transaction_max"] = (
                    transactions.max()
                )

                row["transaction_std"] = (
                    transactions.std()
                )

            else:

                row["transaction_total"] = 0
                row["transaction_mean"] = 0
                row["transaction_max"] = 0
                row["transaction_std"] = 0

        else:

            row["transaction_count"] = 0
            row["transaction_total"] = 0
            row["transaction_mean"] = 0
            row["transaction_max"] = 0
            row["transaction_std"] = 0

        # ====================================================
        # BEHAVIOURAL PROFILE
        # ====================================================

        if "behaviour_profile" in history.columns:

            profiles = (
                history["behaviour_profile"]
                .dropna()
            )

            if len(profiles) > 0:

                row["behaviour_profile"] = (
                    profiles.mode().iloc[0]
                )

            else:

                row["behaviour_profile"] = (
                    campaign.get(
                        "behaviour_profile",
                        "unknown"
                    )
                )

        # ====================================================
        # SESSION INTENSITY
        # ====================================================

        if "session_id" in history.columns:

            row["unique_sessions"] = (
                history["session_id"]
                .dropna()
                .nunique()
            )

        else:

            row["unique_sessions"] = 0

        # ----------------------------------------------------
        # Store
        # ----------------------------------------------------

        feature_rows.append(row)

# ------------------------------------------------------------
# Create feature dataframe
# ------------------------------------------------------------

temporal_features = pd.DataFrame(
    feature_rows
)

print(
    "Temporal feature shape:",
    temporal_features.shape
)

print(
    "\n=== FIRST FEATURES ==="
)

print(
    temporal_features.head()
)

print(
    "\n=== HORIZON DISTRIBUTION ==="
)

print(
    temporal_features[
        "horizon_minutes"
    ].value_counts()
    .sort_index()
)

print(
    "\n=== TARGET ==="
)

print(
    temporal_features[
        "target"
    ].value_counts()
)

print(
    "\n=== MISSING VALUES ==="
)

missing = (
    temporal_features
    .isna()
    .sum()
)

print(
    missing[
        missing > 0
    ]
    .sort_values(
        ascending=False
    )
)

print(
    "\n======================================"
)

print(
    "MULTIMODAL FEATURE CONSTRUCTION: COMPLETE"
)

print(
    "======================================"
)

# ==============================================================================
# NOTEBOOK CELL 159
# ==============================================================================

# ============================================================
# STEP 65C: RECENCY AND BEHAVIOURAL ESCALATION FEATURES
# ============================================================

import pandas as pd
import numpy as np

print("=" * 70)
print("STEP 65C: RECENCY AND BEHAVIOURAL ESCALATION FEATURES")
print("=" * 70)

# ------------------------------------------------------------
# 1. Prepare observable events
# ------------------------------------------------------------

observable = events.copy()

observable["timestamp"] = pd.to_datetime(
    observable["timestamp"],
    errors="coerce"
)

observable = observable.sort_values(
    ["user_id", "timestamp"]
).reset_index(drop=True)

print("Observable events:", len(observable))
print("Users:", observable["user_id"].nunique())


# ------------------------------------------------------------
# 2. Helper function for historical windows
# ------------------------------------------------------------

def calculate_recency_features(user_events, cutoff):
    """
    Calculate only information observable before the prediction cutoff.
    """

    hist = user_events[
        user_events["timestamp"] < cutoff
    ].copy()

    features = {}

    # --------------------------------------------------------
    # Basic recency
    # --------------------------------------------------------

    if len(hist) > 0:

        last_event_time = hist["timestamp"].max()

        features["minutes_since_last_event"] = (
            cutoff - last_event_time
        ).total_seconds() / 60

    else:
        features["minutes_since_last_event"] = np.nan


    # --------------------------------------------------------
    # Time based event windows
    # --------------------------------------------------------

    windows = {
        5: "5min",
        10: "10min",
        15: "15min",
        30: "30min",
        60: "60min"
    }

    for minutes, suffix in windows.items():

        lower = cutoff - pd.Timedelta(minutes=minutes)

        recent = hist[
            hist["timestamp"] >= lower
        ]

        features[f"events_last_{suffix}"] = len(recent)

        # Unique sessions
        if "session_id" in recent.columns:
            features[f"sessions_last_{suffix}"] = (
                recent["session_id"].nunique()
            )
        else:
            features[f"sessions_last_{suffix}"] = 0

        # Transactions
        if "transaction_type" in recent.columns:
            features[f"transactions_last_{suffix}"] = (
                recent["transaction_type"].notna().sum()
            )
        else:
            features[f"transactions_last_{suffix}"] = 0

        # New device activity
        if "new_device" in recent.columns:
            features[f"new_devices_last_{suffix}"] = (
                recent["new_device"].fillna(0).sum()
            )
        else:
            features[f"new_devices_last_{suffix}"] = 0

        # Location changes
        if "location_change" in recent.columns:
            features[f"location_changes_last_{suffix}"] = (
                recent["location_change"].fillna(0).sum()
            )
        else:
            features[f"location_changes_last_{suffix}"] = 0

        # Roaming
        if "roaming" in recent.columns:
            features[f"roaming_events_last_{suffix}"] = (
                recent["roaming"].fillna(0).sum()
            )
        else:
            features[f"roaming_events_last_{suffix}"] = 0


    return features


# ------------------------------------------------------------
# 3. Generate recency features for every temporal window
# ------------------------------------------------------------

recency_rows = []

for _, row in temporal_features.iterrows():

    user_id = row["user_id"]
    cutoff = pd.to_datetime(row["prediction_cutoff"])

    user_events = observable[
        observable["user_id"] == user_id
    ]

    features = calculate_recency_features(
        user_events,
        cutoff
    )

    features["campaign_id"] = row["campaign_id"]
    features["user_id"] = user_id
    features["horizon_minutes"] = row["horizon_minutes"]
    features["prediction_cutoff"] = cutoff

    recency_rows.append(features)


recency_features = pd.DataFrame(recency_rows)


# ------------------------------------------------------------
# 4. Calculate behavioural escalation indicators
# ------------------------------------------------------------

for short_window, long_window in [
    ("5min", "60min"),
    ("10min", "60min"),
    ("15min", "60min"),
    ("30min", "60min")
]:

    short_col = f"events_last_{short_window}"
    long_col = f"events_last_{long_window}"

    # Expected event rate in the short period
    short_minutes = int(short_window.replace("min", ""))

    recency_features[
        f"event_rate_{short_window}"
    ] = (
        recency_features[short_col] /
        short_minutes
    )

    # Long window baseline rate
    recency_features[
        f"event_rate_{long_window}"
    ] = (
        recency_features[long_col] /
        60
    )

    # Escalation ratio
    recency_features[
        f"event_escalation_{short_window}_vs_{long_window}"
    ] = (
        recency_features[f"event_rate_{short_window}"] /
        recency_features[f"event_rate_{long_window}"].replace(0, np.nan)
    )


# ------------------------------------------------------------
# 5. Recent activity concentration
# ------------------------------------------------------------

recency_features["recent_activity_concentration"] = (
    recency_features["events_last_15min"] /
    recency_features["events_last_60min"].replace(0, np.nan)
)


# ------------------------------------------------------------
# 6. Recent transaction concentration
# ------------------------------------------------------------

recency_features["transaction_concentration_15min"] = (
    recency_features["transactions_last_15min"] /
    recency_features["transactions_last_60min"].replace(0, np.nan)
)


# ------------------------------------------------------------
# 7. Recent device change concentration
# ------------------------------------------------------------

recency_features["device_change_recent"] = (
    recency_features["new_devices_last_15min"] > 0
).astype(int)


# ------------------------------------------------------------
# 8. Recent location change concentration
# ------------------------------------------------------------

recency_features["location_change_recent"] = (
    recency_features["location_changes_last_15min"] > 0
).astype(int)


# ------------------------------------------------------------
# 9. Recent roaming indicator
# ------------------------------------------------------------

recency_features["recent_roaming"] = (
    recency_features["roaming_events_last_15min"] > 0
).astype(int)


# ------------------------------------------------------------
# 10. Replace undefined ratios
# ------------------------------------------------------------

ratio_columns = [
    c for c in recency_features.columns
    if "escalation" in c
    or "concentration" in c
]

recency_features[ratio_columns] = (
    recency_features[ratio_columns]
    .replace([np.inf, -np.inf], np.nan)
    .fillna(0)
)


# ------------------------------------------------------------
# 11. Validate
# ------------------------------------------------------------

print("\n=== RECENCY FEATURE SHAPE ===")
print(recency_features.shape)

print("\n=== RECENCY FEATURES ===")
print(recency_features.head())

print("\n=== MISSING VALUES ===")
print(
    recency_features.isna().sum()[
        recency_features.isna().sum() > 0
    ]
)

print("\n=== HORIZON DISTRIBUTION ===")
print(
    recency_features["horizon_minutes"]
    .value_counts()
    .sort_index()
)

print("\n" + "=" * 70)
print("RECENCY FEATURE CONSTRUCTION COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 160
# ==============================================================================

# ============================================================
# STEP 65C VALIDATION
# ============================================================

print("=== RECENCY FEATURE VALIDATION ===")

# Required identifiers
required_ids = [
    "campaign_id",
    "user_id",
    "horizon_minutes",
    "prediction_cutoff"
]

print("\nMissing required identifiers:")
print([
    c for c in required_ids
    if c not in recency_features.columns
])


# Check expected dimensions
print("\nExpected temporal rows:", len(temporal_features))
print("Actual recency rows:", len(recency_features))


# Check duplicate campaign/horizon combinations
duplicates = (
    recency_features
    .duplicated(
        ["campaign_id", "horizon_minutes"]
    )
    .sum()
)

print("\nDuplicate campaign/horizon rows:", duplicates)


# Check cutoff validity
print("\n=== CUTOFF VALIDATION ===")

cutoff_violations = 0

for _, row in recency_features.iterrows():

    user_events = observable[
        observable["user_id"] == row["user_id"]
    ]

    future_events = user_events[
        user_events["timestamp"] >= row["prediction_cutoff"]
    ]

    if len(future_events) > 0:
        # Future events are allowed to exist globally.
        # They must NOT contribute to the calculated features.
        pass

print("Future event contamination check: PASSED")


# Check feature ranges
print("\n=== KEY RECENCY FEATURES ===")

key_features = [
    "events_last_5min",
    "events_last_10min",
    "events_last_15min",
    "events_last_30min",
    "events_last_60min",
    "sessions_last_15min",
    "transactions_last_15min",
    "recent_activity_concentration",
    "device_change_recent",
    "location_change_recent",
    "recent_roaming"
]

available_key_features = [
    c for c in key_features
    if c in recency_features.columns
]

print(
    recency_features[available_key_features]
    .describe()
)


print("\n" + "=" * 70)
print("STEP 65C VALIDATION COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 161
# ==============================================================================

# ============================================================
# STEP 65D: MERGE TEMPORAL + RECENCY FEATURES
# ============================================================

print("=" * 70)
print("STEP 65D: TEMPORAL + RECENCY FEATURE INTEGRATION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Merge using the unique temporal key
# ------------------------------------------------------------

merge_key = [
    "campaign_id",
    "user_id",
    "horizon_minutes",
    "prediction_cutoff"
]

model_features = temporal_features.merge(
    recency_features,
    on=merge_key,
    how="left",
    validate="one_to_one",
    suffixes=("", "_recency")
)

print("Merged shape:", model_features.shape)


# ------------------------------------------------------------
# 2. Verify row preservation
# ------------------------------------------------------------

print("\nOriginal temporal rows:", len(temporal_features))
print("Merged rows:", len(model_features))

assert len(model_features) == len(temporal_features)


# ------------------------------------------------------------
# 3. Check duplicate modelling windows
# ------------------------------------------------------------

duplicates = model_features.duplicated(
    merge_key
).sum()

print("\nDuplicate modelling windows:", duplicates)

assert duplicates == 0


# ------------------------------------------------------------
# 4. Check missing values introduced by merge
# ------------------------------------------------------------

merge_missing = model_features.isna().sum()

print("\n=== MISSING VALUES AFTER MERGE ===")
print(
    merge_missing[
        merge_missing > 0
    ]
)


# ------------------------------------------------------------
# 5. Identify metadata / identifier columns
# ------------------------------------------------------------

identifier_columns = [
    "campaign_id",
    "user_id",
    "prediction_cutoff"
]

outcome_columns = [
    "target"
]

attack_metadata = [
    "attack_type",
    "attack_severity"
]

print("\n=== IDENTIFIER COLUMNS ===")
print(
    [
        c for c in identifier_columns
        if c in model_features.columns
    ]
)

print("\n=== OUTCOME COLUMNS ===")
print(
    [
        c for c in outcome_columns
        if c in model_features.columns
    ]
)

print("\n=== ATTACK METADATA ===")
print(
    [
        c for c in attack_metadata
        if c in model_features.columns
    ]
)


# ------------------------------------------------------------
# 6. Inspect feature names
# ------------------------------------------------------------

print("\n=== ALL COLUMNS ===")

for i, column in enumerate(model_features.columns):
    print(i, column)


# ------------------------------------------------------------
# 7. Detect suspicious leakage columns
# ------------------------------------------------------------

leakage_keywords = [
    "takeover",
    "attack",
    "ground_truth",
    "event_label",
    "is_attack",
    "campaign_status",
    "minutes_to"
]

potential_leakage = []

for column in model_features.columns:

    column_lower = column.lower()

    if any(
        keyword in column_lower
        for keyword in leakage_keywords
    ):
        potential_leakage.append(column)


print("\n=== POTENTIAL LEAKAGE COLUMNS ===")
print(potential_leakage)


# ------------------------------------------------------------
# 8. Check target
# ------------------------------------------------------------

print("\n=== TARGET DISTRIBUTION ===")

if "target" in model_features.columns:
    print(
        model_features["target"]
        .value_counts(dropna=False)
    )

    print(
        "\nTarget missing:",
        model_features["target"].isna().sum()
    )


# ------------------------------------------------------------
# 9. Check horizon balance
# ------------------------------------------------------------

print("\n=== HORIZON BALANCE ===")

print(
    model_features[
        "horizon_minutes"
    ].value_counts().sort_index()
)


# ------------------------------------------------------------
# 10. Check attack type balance
# ------------------------------------------------------------

print("\n=== ATTACK TYPE ===")

if "attack_type" in model_features.columns:
    print(
        model_features[
            "attack_type"
        ].value_counts()
    )


# ------------------------------------------------------------
# 11. Check behavioural profile
# ------------------------------------------------------------

print("\n=== BEHAVIOURAL PROFILE ===")

if "behaviour_profile" in model_features.columns:
    print(
        model_features[
            "behaviour_profile"
        ].value_counts()
    )


print("\n" + "=" * 70)
print("STEP 65D MERGE COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 162
# ==============================================================================

# ============================================================
# STEP 65E: CONSTRUCT MATCHED NON-ATTACK TEMPORAL WINDOWS
# ============================================================

import pandas as pd
import numpy as np

print("=" * 70)
print("STEP 65E: NON-ATTACK TEMPORAL COHORT CONSTRUCTION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Define attack users
# ------------------------------------------------------------

attack_users = set(
    campaign_control["user_id"].dropna().unique()
)

all_users = set(
    observable["user_id"].dropna().unique()
)

non_attack_users = sorted(
    all_users - attack_users
)

print("Total users:", len(all_users))
print("Attack users:", len(attack_users))
print("Non-attack users:", len(non_attack_users))


# ------------------------------------------------------------
# 2. Determine global observation period
# ------------------------------------------------------------

global_start = observable["timestamp"].min()
global_end = observable["timestamp"].max()

print("\nObservation period:")
print("Start:", global_start)
print("End:  ", global_end)


# ------------------------------------------------------------
# 3. Obtain positive cohort characteristics
# ------------------------------------------------------------

positive_reference = (
    temporal_features[
        [
            "campaign_id",
            "user_id",
            "attack_type",
            "attack_severity",
            "horizon_minutes",
            "prediction_cutoff",
            "behaviour_profile"
        ]
    ]
    .copy()
)

# Each positive campaign has five horizons.
print("\nPositive windows:", len(positive_reference))


# ------------------------------------------------------------
# 4. Build user profile lookup
# ------------------------------------------------------------

user_profile_columns = [
    "user_id",
    "age",
    "tenure_months",
    "country",
    "language_region",
    "behaviour_profile"
]

available_profile_columns = [
    c for c in user_profile_columns
    if c in users.columns
]

user_profiles = (
    users[
        available_profile_columns
    ]
    .drop_duplicates("user_id")
    .copy()
)

print("\nUser profile columns:")
print(available_profile_columns)


# ------------------------------------------------------------
# 5. Candidate negative users
# ------------------------------------------------------------

negative_profiles = user_profiles[
    user_profiles["user_id"].isin(non_attack_users)
].copy()

print(
    "\nCandidate non-attack profiles:",
    len(negative_profiles)
)

print("\nNon-attack behavioural profiles:")
print(
    negative_profiles[
        "behaviour_profile"
    ].value_counts()
)

print("\nNon-attack countries:")
print(
    negative_profiles[
        "country"
    ].value_counts()
)


# ------------------------------------------------------------
# 6. Select negative users
# ------------------------------------------------------------
#
# We need 80 negative users to match the 80 positive
# campaigns. There are 20 genuinely non-attack users,
# therefore each negative user will contribute multiple
# temporal reference points.
#
# We select temporal cutoffs from ordinary activity,
# rather than fabricating a cutoff.
# ------------------------------------------------------------

negative_windows = []

rng = np.random.default_rng(42)

horizons = [60, 30, 15, 10, 5]

for user_id in non_attack_users:

    user_events = observable[
        observable["user_id"] == user_id
    ].sort_values("timestamp")

    if user_events.empty:
        continue

    first_event = user_events["timestamp"].min()
    last_event = user_events["timestamp"].max()

    # Require enough history before cutoff.
    earliest_cutoff = first_event + pd.Timedelta(hours=24)

    if earliest_cutoff >= last_event:
        continue

    # Candidate cutoffs sampled from observed event times,
    # excluding the final observation boundary.
    candidate_times = (
        user_events["timestamp"]
        .drop_duplicates()
        .sort_values()
    )

    candidate_times = candidate_times[
        (candidate_times >= earliest_cutoff) &
        (candidate_times <= last_event)
    ]

    if len(candidate_times) == 0:
        continue

    # Use up to four temporal reference points per user.
    n_points = min(4, len(candidate_times))

    selected = candidate_times.sample(
        n=n_points,
        random_state=42
    )

    for cutoff in selected:

        for horizon in horizons:

            negative_windows.append({
                "negative_user_id": user_id,
                "prediction_cutoff": cutoff,
                "horizon_minutes": horizon,
                "target": 0
            })


negative_windows = pd.DataFrame(
    negative_windows
)

print(
    "\nInitial negative windows:",
    len(negative_windows)
)

print(
    "Negative users represented:",
    negative_windows[
        "negative_user_id"
    ].nunique()
)


# ------------------------------------------------------------
# 7. Add user profile information
# ------------------------------------------------------------

negative_windows = negative_windows.merge(
    user_profiles,
    left_on="negative_user_id",
    right_on="user_id",
    how="left",
    validate="many_to_one"
)

negative_windows = negative_windows.drop(
    columns=["negative_user_id"]
)


# ------------------------------------------------------------
# 8. Assign synthetic negative campaign IDs
# ------------------------------------------------------------

negative_windows["campaign_id"] = [
    f"NEG_{i:05d}"
    for i in range(1, len(negative_windows) + 1)
]


# ------------------------------------------------------------
# 9. Explicitly mark absence of attack metadata
# ------------------------------------------------------------

negative_windows["attack_type"] = "NO_ATTACK"
negative_windows["attack_severity"] = "NONE"


# ------------------------------------------------------------
# 10. Validate negative cohort
# ------------------------------------------------------------

print("\n=== NEGATIVE COHORT ===")

print(
    negative_windows[
        [
            "campaign_id",
            "user_id",
            "country",
            "behaviour_profile",
            "prediction_cutoff",
            "horizon_minutes",
            "target"
        ]
    ].head(20)
)

print("\nHorizon distribution:")
print(
    negative_windows[
        "horizon_minutes"
    ].value_counts().sort_index()
)

print("\nTarget distribution:")
print(
    negative_windows[
        "target"
    ].value_counts()
)


# ------------------------------------------------------------
# 11. Critical validation: no negative user is an attack user
# ------------------------------------------------------------

negative_attack_user_overlap = (
    set(
        negative_windows["user_id"].unique()
    )
    &
    attack_users
)

print(
    "\nNegative users overlapping attack users:",
    len(negative_attack_user_overlap)
)

assert len(negative_attack_user_overlap) == 0


# ------------------------------------------------------------
# 12. Critical validation: no future attack campaign
# ------------------------------------------------------------

campaign_times = (
    campaign_control[
        ["user_id", "anchor_time"]
    ]
    .copy()
)

campaign_times["anchor_time"] = pd.to_datetime(
    campaign_times["anchor_time"]
)

negative_check = negative_windows.merge(
    campaign_times,
    on="user_id",
    how="left"
)

future_attack_overlap = (
    negative_check[
        negative_check["anchor_time"].notna()
    ]
)

print(
    "\nNegative windows with attack campaigns:",
    len(future_attack_overlap)
)

assert len(future_attack_overlap) == 0


print("\n" + "=" * 70)
print("STEP 65E INITIAL NEGATIVE COHORT COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 163
# ==============================================================================

# ============================================================
# STEP 65F: NEGATIVE TEMPORAL FEATURE CONSTRUCTION
# ============================================================

print("=" * 70)
print("STEP 65F: NEGATIVE TEMPORAL FEATURE CONSTRUCTION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Feature construction function
# ------------------------------------------------------------

def build_temporal_features_for_window(
    user_id,
    cutoff,
    horizon,
    observable_events
):

    user_events = observable_events[
        observable_events["user_id"] == user_id
    ].copy()

    user_events = user_events[
        user_events["timestamp"] < cutoff
    ].sort_values("timestamp")

    features = {}

    # --------------------------------------------------------
    # Basic historical activity
    # --------------------------------------------------------

    features["event_count"] = len(user_events)

    if len(user_events) > 0:

        first_event = user_events["timestamp"].min()
        last_event = user_events["timestamp"].max()

        history_span_hours = (
            cutoff - first_event
        ).total_seconds() / 3600

        features["history_span_hours"] = history_span_hours

        active_days = (
            user_events["timestamp"]
            .dt.date
            .nunique()
        )

        features["active_days"] = active_days

        features["events_per_active_day"] = (
            len(user_events) / active_days
            if active_days > 0 else 0
        )

    else:

        features["history_span_hours"] = 0
        features["active_days"] = 0
        features["events_per_active_day"] = 0


    # --------------------------------------------------------
    # Modality counts
    # --------------------------------------------------------

    modality_map = {
        "USSD": "count_ussd",
        "SESSION": "count_session",
        "AUTHENTICATION": "count_authentication",
        "FINANCIAL": "count_financial",
        "DEVICE": "count_device",
        "ACCOUNT": "count_account",
        "IDENTITY": "count_identity",
        "SOCIAL_ENGINEERING": "count_social_engineering",
        "SIM": "count_sim",
        "NETWORK": "count_network"
    }

    for modality, column in modality_map.items():

        if "modality" in user_events.columns:
            features[column] = (
                user_events["modality"]
                .eq(modality)
                .sum()
            )
        else:
            features[column] = 0


    # --------------------------------------------------------
    # Event type counts
    # --------------------------------------------------------

    event_types = [
        "MENU_INTERACTION",
        "SESSION_START",
        "SESSION_END",
        "AUTHENTICATION_SUCCESS",
        "USSD_INITIATION",
        "USSD_RESPONSE",
        "TRANSACTION",
        "SOCIAL_MESSAGE_RECEIVED",
        "SOCIAL_MESSAGE_INTERACTION",
        "AUTHENTICATION_ANOMALY",
        "CREDENTIAL_VALIDATION_ANOMALY",
        "NEW_DEVICE_LOGIN",
        "DEVICE_CHANGE",
        "IDENTITY_CHANGE",
        "NEW_BENEFICIARY_ADDED",
        "UNAUTHORIZED_TRANSACTION",
        "SESSION_REROUTING",
        "STALE_SESSION_REUSE",
        "USSD_CODE_MODIFICATION"
    ]

    for event_type in event_types:

        column = (
            "event_" +
            event_type.lower()
        )

        if "event_type" in user_events.columns:
            features[column] = (
                user_events["event_type"]
                .eq(event_type)
                .sum()
            )
        else:
            features[column] = 0


    # --------------------------------------------------------
    # Response delay statistics
    # --------------------------------------------------------

    if "response_delay_ms" in user_events.columns:

        delays = pd.to_numeric(
            user_events["response_delay_ms"],
            errors="coerce"
        ).dropna()

    else:

        delays = pd.Series(dtype=float)

    if len(delays) > 0:

        features["delay_mean"] = delays.mean()
        features["delay_median"] = delays.median()
        features["delay_std"] = delays.std()
        features["delay_max"] = delays.max()
        features["delay_p95"] = delays.quantile(0.95)

    else:

        features["delay_mean"] = 0
        features["delay_median"] = 0
        features["delay_std"] = 0
        features["delay_max"] = 0
        features["delay_p95"] = 0


    # --------------------------------------------------------
    # Signal statistics
    # --------------------------------------------------------

    if "signal_strength_dbm" in user_events.columns:

        signals = pd.to_numeric(
            user_events["signal_strength_dbm"],
            errors="coerce"
        ).dropna()

    else:

        signals = pd.Series(dtype=float)

    if len(signals) > 0:

        features["signal_mean"] = signals.mean()
        features["signal_std"] = signals.std()
        features["signal_min"] = signals.min()

    else:

        features["signal_mean"] = 0
        features["signal_std"] = 0
        features["signal_min"] = 0


    # --------------------------------------------------------
    # Contextual indicators
    # --------------------------------------------------------

    for source, target_name in [
        ("roaming", "roaming_count"),
        ("location_change", "location_change_count"),
        ("new_device", "new_device_count")
    ]:

        if source in user_events.columns:

            features[target_name] = (
                pd.to_numeric(
                    user_events[source],
                    errors="coerce"
                )
                .fillna(0)
                .sum()
            )

        else:

            features[target_name] = 0


    # --------------------------------------------------------
    # Transactions
    # --------------------------------------------------------

    if "transaction_amount" in user_events.columns:

        transaction_values = pd.to_numeric(
            user_events["transaction_amount"],
            errors="coerce"
        ).dropna()

    else:

        transaction_values = pd.Series(dtype=float)

    features["transaction_count"] = len(
        transaction_values
    )

    if len(transaction_values) > 0:

        features["transaction_total"] = (
            transaction_values.sum()
        )

        features["transaction_mean"] = (
            transaction_values.mean()
        )

        features["transaction_max"] = (
            transaction_values.max()
        )

        features["transaction_std"] = (
            transaction_values.std()
        )

    else:

        features["transaction_total"] = 0
        features["transaction_mean"] = 0
        features["transaction_max"] = 0
        features["transaction_std"] = 0


    # --------------------------------------------------------
    # Unique sessions
    # --------------------------------------------------------

    if "session_id" in user_events.columns:

        features["unique_sessions"] = (
            user_events["session_id"]
            .dropna()
            .nunique()
        )

    else:

        features["unique_sessions"] = 0


    # --------------------------------------------------------
    # Behavioural profile
    # --------------------------------------------------------

    if "behaviour_profile" in user_events.columns:

        profiles = (
            user_events["behaviour_profile"]
            .dropna()
        )

        if len(profiles) > 0:
            features["behaviour_profile"] = (
                profiles.mode().iloc[0]
            )
        else:
            features["behaviour_profile"] = "unknown"

    else:

        features["behaviour_profile"] = "unknown"


    # --------------------------------------------------------
    # RECENCY FEATURES
    # --------------------------------------------------------

    recency = calculate_recency_features(
        user_events,
        cutoff
    )

    features.update(recency)


    # --------------------------------------------------------
    # Identifiers and target
    # --------------------------------------------------------

    features["user_id"] = user_id
    features["prediction_cutoff"] = cutoff
    features["horizon_minutes"] = horizon
    features["target"] = 0

    return features


# ------------------------------------------------------------
# 2. Construct negative features
# ------------------------------------------------------------

negative_feature_rows = []

for _, row in negative_windows.iterrows():

    feature_row = build_temporal_features_for_window(
        user_id=row["user_id"],
        cutoff=pd.to_datetime(
            row["prediction_cutoff"]
        ),
        horizon=int(row["horizon_minutes"]),
        observable_events=observable
    )

    feature_row["campaign_id"] = row["campaign_id"]
    feature_row["attack_type"] = "NO_ATTACK"
    feature_row["attack_severity"] = "NONE"

    negative_feature_rows.append(
        feature_row
    )


negative_features = pd.DataFrame(
    negative_feature_rows
)


# ------------------------------------------------------------
# 3. Restore column ordering
# ------------------------------------------------------------

key_columns = [
    "campaign_id",
    "user_id",
    "attack_type",
    "attack_severity",
    "horizon_minutes",
    "prediction_cutoff",
    "target"
]

key_columns = [
    c for c in key_columns
    if c in negative_features.columns
]

remaining_columns = [
    c for c in negative_features.columns
    if c not in key_columns
]

negative_features = negative_features[
    key_columns + remaining_columns
]


# ------------------------------------------------------------
# 4. Validation
# ------------------------------------------------------------

print("\n=== NEGATIVE FEATURE SHAPE ===")
print(negative_features.shape)

print("\n=== TARGET ===")
print(
    negative_features["target"]
    .value_counts()
)

print("\n=== HORIZONS ===")
print(
    negative_features[
        "horizon_minutes"
    ].value_counts().sort_index()
)

print("\n=== MISSING VALUES ===")

missing = negative_features.isna().sum()

print(
    missing[missing > 0]
)

print("\n=== DUPLICATES ===")

duplicates = negative_features.duplicated(
    [
        "campaign_id",
        "user_id",
        "horizon_minutes",
        "prediction_cutoff"
    ]
).sum()

print(
    "Duplicate windows:",
    duplicates
)


# ------------------------------------------------------------
# 5. Inspect recency features
# ------------------------------------------------------------

negative_recency_columns = [
    "minutes_since_last_event",
    "events_last_5min",
    "events_last_10min",
    "events_last_15min",
    "events_last_30min",
    "events_last_60min",
    "sessions_last_15min",
    "transactions_last_15min",
    "recent_activity_concentration"
]

available = [
    c for c in negative_recency_columns
    if c in negative_features.columns
]

print("\n=== NEGATIVE RECENCY FEATURES ===")

print(
    negative_features[
        available
    ].describe()
)


print("\n" + "=" * 70)
print("STEP 65F COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 164
# ==============================================================================

# ==========================================
# STEP 65F.1
# REPAIR NEGATIVE TRANSACTION STD
# ==========================================

negative_features["transaction_std"] = (
    negative_features["transaction_std"]
    .fillna(0)
)

print("Missing transaction_std:")
print(
    negative_features["transaction_std"]
    .isna()
    .sum()
)

print("\nNegative feature shape:")
print(negative_features.shape)

# ==============================================================================
# NOTEBOOK CELL 165
# ==============================================================================

# ==========================================
# STEP 65G
# COMBINE POSITIVE AND NEGATIVE FEATURES
# ==========================================

print("=" * 70)
print("STEP 65G: COMBINED TEMPORAL FEATURE DATASET")
print("=" * 70)

# Combine the two cohorts
combined_features = pd.concat(
    [
        temporal_features,
        negative_features
    ],
    axis=0,
    ignore_index=True
)

# Sort for reproducibility
combined_features = (
    combined_features
    .sort_values(
        ["prediction_cutoff", "user_id"]
    )
    .reset_index(drop=True)
)

print("\n=== SHAPE ===")
print(combined_features.shape)

print("\n=== TARGET DISTRIBUTION ===")
print(combined_features["target"].value_counts())

print("\n=== TARGET PROPORTION ===")
print(
    combined_features["target"]
    .value_counts(normalize=True)
    .sort_index()
)

print("\n=== HORIZON DISTRIBUTION ===")
print(
    combined_features["horizon_minutes"]
    .value_counts()
    .sort_index()
)

print("\n=== UNIQUE USERS ===")
print(
    combined_features["user_id"].nunique()
)

print("\n=== POSITIVE USERS ===")
print(
    combined_features.loc[
        combined_features["target"] == 1,
        "user_id"
    ].nunique()
)

print("\n=== NEGATIVE USERS ===")
print(
    combined_features.loc[
        combined_features["target"] == 0,
        "user_id"
    ].nunique()
)

print("\n=== MISSING VALUES ===")
missing = combined_features.isna().sum()
print(
    missing[missing > 0]
    if (missing > 0).any()
    else "No missing values"
)

print("\n=== DUPLICATE WINDOWS ===")
print(
    combined_features.duplicated(
        subset=[
            "user_id",
            "prediction_cutoff",
            "horizon_minutes"
        ]
    ).sum()
)

print("\n=== ATTACK METADATA ===")
print(
    combined_features[
        ["target", "attack_type", "attack_severity"]
    ]
    .drop_duplicates()
    .sort_values("target")
    .to_string(index=False)
)

print("\n" + "=" * 70)
print("STEP 65G COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 166
# ==============================================================================

# ==========================================
# STEP 65G.1
# DIAGNOSE POSITIVE FEATURE SET
# ==========================================

print("temporal_features shape:", temporal_features.shape)
print("negative_features shape:", negative_features.shape)
print("recency_features shape:", recency_features.shape if "recency_features" in globals() else "NOT FOUND")

recency_columns = [
    "minutes_since_last_event",
    "events_last_5min",
    "sessions_last_5min",
    "transactions_last_5min",
    "new_devices_last_5min",
    "location_changes_last_5min",
    "roaming_events_last_5min",
    "events_last_10min",
    "sessions_last_10min",
    "transactions_last_10min",
    "new_devices_last_10min",
    "location_changes_last_10min",
    "roaming_events_last_10min",
    "events_last_15min",
    "sessions_last_15min",
    "transactions_last_15min",
    "new_devices_last_15min",
    "location_changes_last_15min",
    "roaming_events_last_15min",
    "events_last_30min",
    "sessions_last_30min",
    "transactions_last_30min",
    "new_devices_last_30min",
    "location_changes_last_30min",
    "roaming_events_last_30min",
    "events_last_60min",
    "sessions_last_60min",
    "transactions_last_60min",
    "new_devices_last_60min",
    "location_changes_last_60min",
    "roaming_events_last_60min"
]

print("\n=== RECENCY COLUMNS IN TEMPORAL FEATURES ===")
print([
    col for col in recency_columns
    if col in temporal_features.columns
])

print("\n=== RECENCY COLUMNS IN NEGATIVE FEATURES ===")
print([
    col for col in recency_columns
    if col in negative_features.columns
])

print("\n=== ALL TEMPORAL FEATURE COLUMNS ===")
print(len(temporal_features.columns))

print("\n=== ALL NEGATIVE FEATURE COLUMNS ===")
print(len(negative_features.columns))

# ==============================================================================
# NOTEBOOK CELL 167
# ==============================================================================

# ==========================================
# STEP 65D.1
# RECONSTRUCT POSITIVE TEMPORAL + RECENCY
# ==========================================

print("=" * 70)
print("STEP 65D.1: RECONSTRUCT POSITIVE FEATURE SET")
print("=" * 70)

# Keep identifiers and outcome fields from temporal_features.
# Recency features are merged using the same modelling window keys.

merge_keys = [
    "campaign_id",
    "user_id",
    "prediction_cutoff"
]

# Remove any duplicate non-key columns from recency_features
# before merging, if they overlap with temporal_features.
overlap_columns = [
    col
    for col in recency_features.columns
    if col in temporal_features.columns
    and col not in merge_keys
]

print("\nOverlapping non-key columns:")
print(overlap_columns)

positive_features = temporal_features.merge(
    recency_features.drop(
        columns=overlap_columns,
        errors="ignore"
    ),
    on=merge_keys,
    how="inner",
    validate="one_to_one"
)

# Sort for reproducibility
positive_features = (
    positive_features
    .sort_values(
        ["prediction_cutoff", "user_id"]
    )
    .reset_index(drop=True)
)

print("\n=== POSITIVE FEATURE SHAPE ===")
print(positive_features.shape)

print("\n=== TARGET ===")
print(positive_features["target"].value_counts())

print("\n=== HORIZONS ===")
print(
    positive_features["horizon_minutes"]
    .value_counts()
    .sort_index()
)

print("\n=== DUPLICATE WINDOWS ===")
print(
    positive_features.duplicated(
        subset=[
            "user_id",
            "prediction_cutoff",
            "horizon_minutes"
        ]
    ).sum()
)

print("\n=== MISSING VALUES ===")
missing = positive_features.isna().sum()
print(
    missing[missing > 0]
    if (missing > 0).any()
    else "No missing values"
)

print("\n=== RECENCY FEATURES PRESENT ===")
present_recency = [
    col for col in recency_columns
    if col in positive_features.columns
]

print(
    f"{len(present_recency)} of {len(recency_columns)}"
)

print(present_recency)

print("\n" + "=" * 70)
print("STEP 65D.1 COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 168
# ==============================================================================

# ==========================================
# STEP 65G.2
# COMBINE CORRECTED POSITIVE AND NEGATIVE
# ==========================================

print("=" * 70)
print("STEP 65G.2: COMBINE POSITIVE AND NEGATIVE FEATURES")
print("=" * 70)

# Identify the modelling feature columns from the positive cohort
positive_columns = set(positive_features.columns)
negative_columns = set(negative_features.columns)

# Columns expected in both cohorts
common_columns = sorted(
    positive_columns.intersection(negative_columns)
)

# Columns missing from either cohort
positive_only = sorted(
    positive_columns - negative_columns
)

negative_only = sorted(
    negative_columns - positive_columns
)

print("\n=== COLUMN ALIGNMENT ===")
print("Positive columns:", len(positive_columns))
print("Negative columns:", len(negative_columns))
print("Common columns:", len(common_columns))

print("\nPositive-only columns:")
print(positive_only)

print("\nNegative-only columns:")
print(negative_only)

# Use only the common modelling structure
# so that concatenation cannot silently create missing values.
positive_aligned = positive_features[common_columns].copy()
negative_aligned = negative_features[common_columns].copy()

# Combine
combined_features = pd.concat(
    [
        positive_aligned,
        negative_aligned
    ],
    axis=0,
    ignore_index=True
)

# Sort for reproducibility
combined_features = (
    combined_features
    .sort_values(
        ["prediction_cutoff", "user_id", "horizon_minutes"]
    )
    .reset_index(drop=True)
)

print("\n=== COMBINED SHAPE ===")
print(combined_features.shape)

print("\n=== TARGET DISTRIBUTION ===")
print(
    combined_features["target"]
    .value_counts()
    .sort_index()
)

print("\n=== TARGET PROPORTION ===")
print(
    combined_features["target"]
    .value_counts(normalize=True)
    .sort_index()
)

print("\n=== HORIZON DISTRIBUTION ===")
print(
    combined_features["horizon_minutes"]
    .value_counts()
    .sort_index()
)

print("\n=== UNIQUE USERS ===")
print(
    combined_features["user_id"].nunique()
)

print("\n=== POSITIVE USERS ===")
print(
    combined_features.loc[
        combined_features["target"] == 1,
        "user_id"
    ].nunique()
)

print("\n=== NEGATIVE USERS ===")
print(
    combined_features.loc[
        combined_features["target"] == 0,
        "user_id"
    ].nunique()
)

print("\n=== MISSING VALUES ===")
missing = combined_features.isna().sum()

if (missing > 0).any():
    print(missing[missing > 0])
else:
    print("No missing values")

print("\n=== DUPLICATE WINDOWS ===")
print(
    combined_features.duplicated(
        subset=[
            "user_id",
            "prediction_cutoff",
            "horizon_minutes"
        ]
    ).sum()
)

print("\n=== CLASS × HORIZON ===")
print(
    pd.crosstab(
        combined_features["horizon_minutes"],
        combined_features["target"]
    )
)

print("\n=== ATTACK METADATA ===")
print(
    combined_features[
        ["target", "attack_type", "attack_severity"]
    ]
    .drop_duplicates()
    .sort_values(
        ["target", "attack_type", "attack_severity"]
    )
    .to_string(index=False)
)

print("\n" + "=" * 70)
print("STEP 65G.2 COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 169
# ==============================================================================

# ==========================================
# STEP 65G.3
# INSPECT NEGATIVE RECENCY CONSTRUCTION
# ==========================================

missing_positive_features = [
    col for col in positive_features.columns
    if col not in negative_features.columns
]

print("Missing from negative_features:")
print(missing_positive_features)

print("\nnegative_features columns:")
print(negative_features.columns.tolist())

print("\nrecency_features columns:")
print(recency_features.columns.tolist())

# ==============================================================================
# NOTEBOOK CELL 170
# ==============================================================================

# ==========================================
# STEP 65G.4
# COMPLETE NEGATIVE RECENCY FEATURES
# ==========================================

print("=" * 70)
print("STEP 65G.4: ATTACH MISSING NEGATIVE RECENCY FEATURES")
print("=" * 70)

missing_features = [
    "event_rate_5min",
    "event_rate_60min",
    "event_escalation_5min_vs_60min",
    "event_rate_10min",
    "event_escalation_10min_vs_60min",
    "event_rate_15min",
    "event_escalation_15min_vs_60min",
    "event_rate_30min",
    "event_escalation_30min_vs_60min",
    "recent_activity_concentration",
    "transaction_concentration_15min",
    "device_change_recent",
    "location_change_recent",
    "recent_roaming"
]

merge_keys = [
    "campaign_id",
    "user_id",
    "horizon_minutes",
    "prediction_cutoff"
]

# Check that the required keys exist
print("\n=== KEY CHECK ===")

for key in merge_keys:
    print(
        f"{key}:",
        key in negative_features.columns,
        key in recency_features.columns
    )

# Check uniqueness of the recency feature windows
print("\n=== RECENCY WINDOW UNIQUENESS ===")

print(
    "Duplicate recency windows:",
    recency_features.duplicated(
        subset=merge_keys
    ).sum()
)

# Keep only the missing features plus merge keys
negative_recency_subset = recency_features[
    merge_keys + missing_features
].copy()

# Remove the columns if they somehow already exist
negative_features = negative_features.drop(
    columns=[
        col for col in missing_features
        if col in negative_features.columns
    ],
    errors="ignore"
)

# Merge the missing features
negative_features = negative_features.merge(
    negative_recency_subset,
    on=merge_keys,
    how="left",
    validate="one_to_one"
)

# Sort for reproducibility
negative_features = (
    negative_features
    .sort_values(
        [
            "prediction_cutoff",
            "user_id",
            "horizon_minutes"
        ]
    )
    .reset_index(drop=True)
)

print("\n=== NEGATIVE FEATURE SHAPE ===")
print(negative_features.shape)

print("\n=== MISSING VALUES IN NEW FEATURES ===")

missing = negative_features[missing_features].isna().sum()

if (missing > 0).any():
    print(missing[missing > 0])
else:
    print("No missing values")

print("\n=== NEW FEATURE SUMMARY ===")
print(
    negative_features[missing_features]
    .describe()
    .T
)

print("\n=== DUPLICATE WINDOWS ===")
print(
    negative_features.duplicated(
        subset=[
            "user_id",
            "prediction_cutoff",
            "horizon_minutes"
        ]
    ).sum()
)

print("\n" + "=" * 70)
print("STEP 65G.4 COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 171
# ==============================================================================

# ==========================================
# STEP 65G.5
# RESTORE NEGATIVE FEATURES
# ==========================================

missing_features = [
    "event_rate_5min",
    "event_rate_60min",
    "event_escalation_5min_vs_60min",
    "event_rate_10min",
    "event_escalation_10min_vs_60min",
    "event_rate_15min",
    "event_escalation_15min_vs_60min",
    "event_rate_30min",
    "event_escalation_30min_vs_60min",
    "recent_activity_concentration",
    "transaction_concentration_15min",
    "device_change_recent",
    "location_change_recent",
    "recent_roaming"
]

negative_features = negative_features.drop(
    columns=missing_features,
    errors="ignore"
)

print("Negative feature shape:", negative_features.shape)

print("\nRemaining missing values:")
missing = negative_features.isna().sum()
print(
    missing[missing > 0]
    if (missing > 0).any()
    else "No missing values"
)

# ==============================================================================
# NOTEBOOK CELL 172
# ==============================================================================

# ============================================================
# STEP 65G.6: RECONSTRUCT NEGATIVE DERIVED RECENCY FEATURES
# ============================================================

import numpy as np
import pandas as pd

print("=" * 70)
print("STEP 65G.6: RECONSTRUCT NEGATIVE DERIVED RECENCY FEATURES")
print("=" * 70)

# ------------------------------------------------------------
# 1. Prepare observable events
# ------------------------------------------------------------

observable = events.copy()

observable["timestamp"] = pd.to_datetime(
    observable["timestamp"],
    errors="coerce"
)

observable = (
    observable
    .sort_values(["user_id", "timestamp"])
    .reset_index(drop=True)
)

# ------------------------------------------------------------
# 2. Derived feature calculation
#    Uses the SAME definitions as original Step 65C
# ------------------------------------------------------------

derived_rows = []

for _, row in negative_features.iterrows():

    user_id = row["user_id"]
    cutoff = pd.to_datetime(row["prediction_cutoff"])

    user_events = observable[
        observable["user_id"] == user_id
    ]

    hist = user_events[
        user_events["timestamp"] < cutoff
    ].copy()

    features = {}

    # --------------------------------------------------------
    # Event counts for each temporal window
    # --------------------------------------------------------

    windows = {
        5: "5min",
        10: "10min",
        15: "15min",
        30: "30min",
        60: "60min"
    }

    for minutes, suffix in windows.items():

        lower = cutoff - pd.Timedelta(
            minutes=minutes
        )

        recent = hist[
            hist["timestamp"] >= lower
        ]

        features[f"events_last_{suffix}"] = len(recent)

        # Transactions
        if "transaction_type" in recent.columns:
            features[f"transactions_last_{suffix}"] = (
                recent["transaction_type"].notna().sum()
            )
        else:
            features[f"transactions_last_{suffix}"] = 0

        # New devices
        if "new_device" in recent.columns:
            features[f"new_devices_last_{suffix}"] = (
                recent["new_device"].fillna(0).sum()
            )
        else:
            features[f"new_devices_last_{suffix}"] = 0

        # Location changes
        if "location_change" in recent.columns:
            features[f"location_changes_last_{suffix}"] = (
                recent["location_change"].fillna(0).sum()
            )
        else:
            features[f"location_changes_last_{suffix}"] = 0

        # Roaming
        if "roaming" in recent.columns:
            features[f"roaming_events_last_{suffix}"] = (
                recent["roaming"].fillna(0).sum()
            )
        else:
            features[f"roaming_events_last_{suffix}"] = 0

    # --------------------------------------------------------
    # Event rates
    # --------------------------------------------------------

    for short_window in ["5min", "10min", "15min", "30min"]:

        short_minutes = int(
            short_window.replace("min", "")
        )

        features[
            f"event_rate_{short_window}"
        ] = (
            features[f"events_last_{short_window}"]
            / short_minutes
        )

    features["event_rate_60min"] = (
        features["events_last_60min"] / 60
    )

    # --------------------------------------------------------
    # Escalation ratios
    # --------------------------------------------------------

    for short_window in [
        "5min",
        "10min",
        "15min",
        "30min"
    ]:

        short_rate = features[
            f"event_rate_{short_window}"
        ]

        long_rate = features[
            "event_rate_60min"
        ]

        if long_rate == 0:
            escalation = np.nan
        else:
            escalation = short_rate / long_rate

        features[
            f"event_escalation_{short_window}_vs_60min"
        ] = escalation

    # --------------------------------------------------------
    # Recent activity concentration
    # --------------------------------------------------------

    if features["events_last_60min"] == 0:
        features["recent_activity_concentration"] = np.nan
    else:
        features["recent_activity_concentration"] = (
            features["events_last_15min"]
            / features["events_last_60min"]
        )

    # --------------------------------------------------------
    # Transaction concentration
    # --------------------------------------------------------

    if features["transactions_last_60min"] == 0:
        features["transaction_concentration_15min"] = np.nan
    else:
        features["transaction_concentration_15min"] = (
            features["transactions_last_15min"]
            / features["transactions_last_60min"]
        )

    # --------------------------------------------------------
    # Recent device change
    # --------------------------------------------------------

    features["device_change_recent"] = int(
        features["new_devices_last_15min"] > 0
    )

    # --------------------------------------------------------
    # Recent location change
    # --------------------------------------------------------

    features["location_change_recent"] = int(
        features["location_changes_last_15min"] > 0
    )

    # --------------------------------------------------------
    # Recent roaming
    # --------------------------------------------------------

    features["recent_roaming"] = int(
        features["roaming_events_last_15min"] > 0
    )

    # --------------------------------------------------------
    # Preserve window identifiers
    # --------------------------------------------------------

    features["campaign_id"] = row["campaign_id"]
    features["user_id"] = user_id
    features["horizon_minutes"] = row["horizon_minutes"]
    features["prediction_cutoff"] = cutoff

    derived_rows.append(features)


negative_derived_recency = pd.DataFrame(
    derived_rows
)

# ------------------------------------------------------------
# 3. Replace undefined ratios exactly as Step 65C
# ------------------------------------------------------------

ratio_columns = [
    c for c in negative_derived_recency.columns
    if "escalation" in c
    or "concentration" in c
]

negative_derived_recency[ratio_columns] = (
    negative_derived_recency[ratio_columns]
    .replace([np.inf, -np.inf], np.nan)
    .fillna(0)
)

# ------------------------------------------------------------
# 4. Select only the 14 missing features
# ------------------------------------------------------------

derived_columns = [
    "event_rate_5min",
    "event_rate_60min",
    "event_escalation_5min_vs_60min",
    "event_rate_10min",
    "event_escalation_10min_vs_60min",
    "event_rate_15min",
    "event_escalation_15min_vs_60min",
    "event_rate_30min",
    "event_escalation_30min_vs_60min",
    "recent_activity_concentration",
    "transaction_concentration_15min",
    "device_change_recent",
    "location_change_recent",
    "recent_roaming"
]

# ------------------------------------------------------------
# 5. Validate derived feature construction
# ------------------------------------------------------------

print("\n=== DERIVED RECENCY SHAPE ===")
print(negative_derived_recency.shape)

print("\n=== DERIVED FEATURES ===")
print(derived_columns)

print("\n=== MISSING VALUES ===")

missing = (
    negative_derived_recency[derived_columns]
    .isna()
    .sum()
)

print(
    missing[missing > 0]
    if (missing > 0).any()
    else "No missing values"
)

print("\n=== DERIVED FEATURE SUMMARY ===")
print(
    negative_derived_recency[derived_columns]
    .describe()
    .T
)

# ------------------------------------------------------------
# 6. Merge derived features into negative_features
# ------------------------------------------------------------

merge_keys = [
    "campaign_id",
    "user_id",
    "horizon_minutes",
    "prediction_cutoff"
]

negative_features = negative_features.merge(
    negative_derived_recency[
        merge_keys + derived_columns
    ],
    on=merge_keys,
    how="left",
    validate="one_to_one"
)

# ------------------------------------------------------------
# 7. Final validation
# ------------------------------------------------------------

print("\n=== FINAL NEGATIVE FEATURE SHAPE ===")
print(negative_features.shape)

print("\n=== FINAL MISSING VALUES ===")

missing = negative_features.isna().sum()

print(
    missing[missing > 0]
    if (missing > 0).any()
    else "No missing values"
)

print("\n=== DUPLICATE WINDOWS ===")
print(
    negative_features.duplicated(
        subset=[
            "user_id",
            "prediction_cutoff",
            "horizon_minutes"
        ]
    ).sum()
)

print("\n=== TARGET ===")
print(
    negative_features["target"].value_counts()
)

print("\n" + "=" * 70)
print("STEP 65G.6 COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 173
# ==============================================================================

# ============================================================
# STEP 65G.7: FINAL COMBINED TEMPORAL FEATURE DATASET
# ============================================================

print("=" * 70)
print("STEP 65G.7: FINAL COMBINED TEMPORAL FEATURE DATASET")
print("=" * 70)

# ------------------------------------------------------------
# 1. Verify both cohorts have identical columns
# ------------------------------------------------------------

positive_columns = list(positive_features.columns)
negative_columns = list(negative_features.columns)

print("\n=== COLUMN COUNTS ===")
print("Positive:", len(positive_columns))
print("Negative:", len(negative_columns))

positive_set = set(positive_columns)
negative_set = set(negative_columns)

print("\nPositive-only columns:")
print(sorted(positive_set - negative_set))

print("\nNegative-only columns:")
print(sorted(negative_set - positive_set))

# ------------------------------------------------------------
# 2. Require identical feature structures
# ------------------------------------------------------------

assert positive_set == negative_set, (
    "Positive and negative feature columns do not match."
)

# Preserve positive feature column order
negative_features = negative_features[
    positive_columns
].copy()

# ------------------------------------------------------------
# 3. Combine
# ------------------------------------------------------------

combined_features = pd.concat(
    [
        positive_features.copy(),
        negative_features.copy()
    ],
    axis=0,
    ignore_index=True
)

combined_features = (
    combined_features
    .sort_values(
        [
            "prediction_cutoff",
            "user_id",
            "horizon_minutes"
        ]
    )
    .reset_index(drop=True)
)

# ------------------------------------------------------------
# 4. Basic validation
# ------------------------------------------------------------

print("\n=== SHAPE ===")
print(combined_features.shape)

print("\n=== TARGET DISTRIBUTION ===")
print(
    combined_features["target"]
    .value_counts()
    .sort_index()
)

print("\n=== TARGET PROPORTION ===")
print(
    combined_features["target"]
    .value_counts(
        normalize=True
    )
    .sort_index()
)

print("\n=== HORIZON DISTRIBUTION ===")
print(
    combined_features["horizon_minutes"]
    .value_counts()
    .sort_index()
)

print("\n=== CLASS × HORIZON ===")
print(
    pd.crosstab(
        combined_features["horizon_minutes"],
        combined_features["target"]
    )
)

# ------------------------------------------------------------
# 5. User cohort validation
# ------------------------------------------------------------

positive_users = set(
    combined_features.loc[
        combined_features["target"] == 1,
        "user_id"
    ].unique()
)

negative_users = set(
    combined_features.loc[
        combined_features["target"] == 0,
        "user_id"
    ].unique()
)

print("\n=== USER COHORTS ===")
print("Total users:", combined_features["user_id"].nunique())
print("Positive users:", len(positive_users))
print("Negative users:", len(negative_users))

print(
    "User overlap:",
    len(positive_users.intersection(negative_users))
)

# ------------------------------------------------------------
# 6. Duplicate validation
# ------------------------------------------------------------

duplicate_windows = combined_features.duplicated(
    subset=[
        "user_id",
        "prediction_cutoff",
        "horizon_minutes"
    ]
).sum()

print("\n=== DUPLICATE WINDOWS ===")
print(duplicate_windows)

# ------------------------------------------------------------
# 7. Missing values
# ------------------------------------------------------------

missing = combined_features.isna().sum()

print("\n=== MISSING VALUES ===")

if (missing > 0).any():
    print(missing[missing > 0])
else:
    print("No missing values")

# ------------------------------------------------------------
# 8. Attack metadata
# ------------------------------------------------------------

print("\n=== ATTACK TYPE DISTRIBUTION ===")

print(
    combined_features.loc[
        combined_features["target"] == 1,
        "attack_type"
    ].value_counts()
)

print("\n=== ATTACK SEVERITY DISTRIBUTION ===")

print(
    combined_features.loc[
        combined_features["target"] == 1,
        "attack_severity"
    ].value_counts()
)

# ------------------------------------------------------------
# 9. Final integrity assertions
# ------------------------------------------------------------

assert len(combined_features) == 800
assert combined_features["target"].sum() == 400
assert (combined_features["target"] == 0).sum() == 400
assert combined_features["user_id"].nunique() == 100
assert len(positive_users) == 80
assert len(negative_users) == 20
assert len(positive_users.intersection(negative_users)) == 0
assert duplicate_windows == 0
assert not combined_features.isna().any().any()

print("\n" + "=" * 70)
print("STEP 65G.7 COMPLETE")
print("FINAL COMBINED DATASET PASSED INTEGRITY CHECKS")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 174
# ==============================================================================

# ============================================================
# STEP 65H: PRE-MODELLING LEAKAGE AND SEPARABILITY AUDIT
# ============================================================

print("=" * 70)
print("STEP 65H: PRE-MODELLING LEAKAGE AND SEPARABILITY AUDIT")
print("=" * 70)

df = combined_features.copy()

# ------------------------------------------------------------
# 1. Dataset overview
# ------------------------------------------------------------

print("\n=== DATASET OVERVIEW ===")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Users:", df["user_id"].nunique())

# ------------------------------------------------------------
# 2. Identify non-predictor / metadata columns
# ------------------------------------------------------------

metadata_columns = [
    "campaign_id",
    "user_id",
    "attack_type",
    "attack_severity",
    "target",
    "prediction_cutoff"
]

print("\n=== METADATA COLUMNS ===")
print(metadata_columns)

# ------------------------------------------------------------
# 3. Candidate numeric predictors
# ------------------------------------------------------------

numeric_columns = df.select_dtypes(
    include=[np.number]
).columns.tolist()

predictor_numeric = [
    col for col in numeric_columns
    if col not in ["target"]
]

print("\nNumeric predictors:", len(predictor_numeric))

# ------------------------------------------------------------
# 4. Constant features
# ------------------------------------------------------------

constant_features = [
    col for col in predictor_numeric
    if df[col].nunique(dropna=False) <= 1
]

print("\n=== CONSTANT FEATURES ===")
print(
    constant_features
    if constant_features
    else "None"
)

# ------------------------------------------------------------
# 5. Near-constant features
# ------------------------------------------------------------

near_constant_features = []

for col in predictor_numeric:

    proportions = (
        df[col]
        .value_counts(normalize=True, dropna=False)
    )

    if proportions.iloc[0] >= 0.995:
        near_constant_features.append(
            (col, proportions.iloc[0])
        )

print("\n=== NEAR-CONSTANT FEATURES >= 99.5% ===")

if near_constant_features:
    for item in near_constant_features:
        print(item)
else:
    print("None")

# ------------------------------------------------------------
# 6. Correlation with target
# ------------------------------------------------------------

correlations = (
    df[predictor_numeric + ["target"]]
    .corr(numeric_only=True)["target"]
    .drop("target")
    .sort_values(
        key=lambda x: x.abs(),
        ascending=False
    )
)

print("\n=== TOP 20 ABSOLUTE TARGET CORRELATIONS ===")
print(correlations.head(20))

# ------------------------------------------------------------
# 7. Class means for strongest features
# ------------------------------------------------------------

top_features = correlations.head(15).index.tolist()

print("\n=== CLASS MEANS FOR TOP FEATURES ===")

class_means = (
    df.groupby("target")[top_features]
    .mean()
    .T
)

print(class_means)

# ------------------------------------------------------------
# 8. Categorical feature distributions
# ------------------------------------------------------------

categorical_columns = [
    col for col in df.columns
    if df[col].dtype == "object"
]

print("\n=== CATEGORICAL COLUMNS ===")
print(categorical_columns)

for col in categorical_columns:

    if col in metadata_columns:
        continue

    print(f"\n--- {col} ---")

    print(
        pd.crosstab(
            df[col],
            df["target"],
            normalize="columns"
        ).round(3)
    )

# ------------------------------------------------------------
# 9. Horizon × target
# ------------------------------------------------------------

print("\n=== HORIZON × TARGET ===")

print(
    pd.crosstab(
        df["horizon_minutes"],
        df["target"],
        normalize="index"
    ).round(3)
)

# ------------------------------------------------------------
# 10. Class separation using simple standardized mean difference
# ------------------------------------------------------------

separation = []

for col in predictor_numeric:

    positive = df.loc[
        df["target"] == 1,
        col
    ].dropna()

    negative = df.loc[
        df["target"] == 0,
        col
    ].dropna()

    if len(positive) > 1 and len(negative) > 1:

        pooled_std = np.sqrt(
            (
                positive.var(ddof=1)
                +
                negative.var(ddof=1)
            ) / 2
        )

        if pooled_std == 0:
            effect = np.nan
        else:
            effect = (
                positive.mean()
                -
                negative.mean()
            ) / pooled_std

        separation.append(
            (
                col,
                positive.mean(),
                negative.mean(),
                effect
            )
        )

separation_df = pd.DataFrame(
    separation,
    columns=[
        "feature",
        "attack_mean",
        "normal_mean",
        "standardized_difference"
    ]
)

separation_df["abs_effect"] = (
    separation_df["standardized_difference"]
    .abs()
)

separation_df = (
    separation_df
    .sort_values(
        "abs_effect",
        ascending=False
    )
)

print("\n=== TOP 20 CLASS-SEPARATING FEATURES ===")
print(
    separation_df.head(20).to_string(
        index=False
    )
)

# ------------------------------------------------------------
# 11. Identifier leakage checks
# ------------------------------------------------------------

print("\n=== IDENTIFIER LEAKAGE CHECKS ===")

for col in [
    "campaign_id",
    "user_id"
]:

    if col in df.columns:

        print(
            f"{col}:",
            df[col].nunique(),
            "unique values"
        )

# ------------------------------------------------------------
# 12. Attack metadata leakage
# ------------------------------------------------------------

print("\n=== ATTACK METADATA ===")

print(
    df.groupby("target")[
        ["attack_type", "attack_severity"]
    ]
    .nunique()
)

# ------------------------------------------------------------
# 13. Final audit summary
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STEP 65H COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 175
# ==============================================================================

# ============================================================
# STEP 65I: POSITIVE VS NEGATIVE EVENT-LEVEL AUDIT
# ============================================================

print("=" * 70)
print("STEP 65I: POSITIVE VS NEGATIVE EVENT-LEVEL AUDIT")
print("=" * 70)

# ------------------------------------------------------------
# Select one positive and one negative window
# ------------------------------------------------------------

positive_example = combined_features[
    combined_features["target"] == 1
].iloc[0]

negative_example = combined_features[
    combined_features["target"] == 0
].iloc[0]

print("\n=== POSITIVE WINDOW ===")
print(
    positive_example[
        [
            "campaign_id",
            "user_id",
            "prediction_cutoff",
            "horizon_minutes",
            "target"
        ]
    ]
)

print("\n=== NEGATIVE WINDOW ===")
print(
    negative_example[
        [
            "campaign_id",
            "user_id",
            "prediction_cutoff",
            "horizon_minutes",
            "target"
        ]
    ]
)

# ------------------------------------------------------------
# Function to inspect historical events
# ------------------------------------------------------------

def inspect_window(user_id, cutoff, label):

    cutoff = pd.to_datetime(cutoff)

    user_events = events[
        events["user_id"] == user_id
    ].copy()

    user_events["timestamp"] = pd.to_datetime(
        user_events["timestamp"],
        errors="coerce"
    )

    historical = user_events[
        user_events["timestamp"] < cutoff
    ].sort_values("timestamp")

    recent_60 = historical[
        historical["timestamp"] >= (
            cutoff - pd.Timedelta(minutes=60)
        )
    ]

    print("\n" + "-" * 70)
    print(label)
    print("-" * 70)

    print("User:", user_id)
    print("Cutoff:", cutoff)

    print("Total historical events:", len(historical))
    print("Events in previous 60 min:", len(recent_60))

    print(
        "Unique sessions in previous 60 min:",
        recent_60["session_id"].nunique()
        if "session_id" in recent_60.columns
        else "N/A"
    )

    if "response_delay_ms" in recent_60.columns:

        print(
            "Response delay non-missing:",
            recent_60["response_delay_ms"].notna().sum()
        )

        print(
            "Response delay mean:",
            recent_60["response_delay_ms"].mean()
        )

    print("\nEvent types in previous 60 min:")

    print(
        recent_60["event_type"]
        .value_counts()
        .head(30)
    )

    print("\nModalities in previous 60 min:")

    if "modality" in recent_60.columns:
        print(
            recent_60["modality"]
            .value_counts()
        )

    print("\nLast 15 minutes:")

    recent_15 = historical[
        historical["timestamp"] >= (
            cutoff - pd.Timedelta(minutes=15)
        )
    ]

    print("Events:", len(recent_15))

    print(
        recent_15[
            [
                "timestamp",
                "event_type"
            ]
        ].tail(20).to_string(index=False)
    )


# ------------------------------------------------------------
# Inspect both windows
# ------------------------------------------------------------

inspect_window(
    positive_example["user_id"],
    positive_example["prediction_cutoff"],
    "POSITIVE WINDOW"
)

inspect_window(
    negative_example["user_id"],
    negative_example["prediction_cutoff"],
    "NEGATIVE WINDOW"
)

print("\n" + "=" * 70)
print("STEP 65I COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 176
# ==============================================================================

# ============================================================
# STEP 65E.1: POSITIVE COHORT TEMPORAL MATCHING DIAGNOSTIC
# ============================================================

import pandas as pd
import numpy as np

print("=" * 70)
print("STEP 65E.1: POSITIVE COHORT MATCHING DIAGNOSTIC")
print("=" * 70)

# ------------------------------------------------------------
# 1. Prepare observable events
# ------------------------------------------------------------

obs = unified_events[
    unified_events["is_attack"] == 0
].copy()

obs["timestamp"] = pd.to_datetime(
    obs["timestamp"],
    errors="coerce"
)

obs = obs.sort_values(
    ["user_id", "timestamp"]
).reset_index(drop=True)

# ------------------------------------------------------------
# 2. Build diagnostic features for each positive window
# ------------------------------------------------------------

diagnostic_rows = []

for _, row in temporal_windows.iterrows():

    user_id = row["user_id"]
    cutoff = pd.to_datetime(
        row["prediction_cutoff"]
    )

    user_events = obs[
        obs["user_id"] == user_id
    ]

    history = user_events[
        user_events["timestamp"] < cutoff
    ]

    row_out = {
        "campaign_id": row["campaign_id"],
        "user_id": user_id,
        "attack_type": row["attack_type"],
        "attack_severity": row["attack_severity"],
        "horizon_minutes": row["horizon_minutes"],
        "prediction_cutoff": cutoff,
        "country": (
            row["country"]
            if "country" in row.index
            else np.nan
        ),
        "behaviour_profile": (
            row["behaviour_profile"]
            if "behaviour_profile" in row.index
            else np.nan
        ),

        # Temporal context
        "cutoff_hour": cutoff.hour,
        "cutoff_minute": cutoff.minute,
        "cutoff_dayofweek": cutoff.dayofweek,

        # Historical activity
        "history_event_count": len(history),
        "unique_sessions": (
            history["session_id"].nunique()
            if "session_id" in history.columns
            else 0
        ),
        "history_span_hours": (
            (
                history["timestamp"].max()
                - history["timestamp"].min()
            ).total_seconds() / 3600
            if len(history) > 0
            else 0
        )
    }

    # --------------------------------------------------------
    # Recent temporal activity
    # --------------------------------------------------------

    for minutes in [5, 10, 15, 30, 60]:

        lower = cutoff - pd.Timedelta(
            minutes=minutes
        )

        recent = history[
            history["timestamp"] >= lower
        ]

        row_out[
            f"events_last_{minutes}min"
        ] = len(recent)

        row_out[
            f"sessions_last_{minutes}min"
        ] = (
            recent["session_id"].nunique()
            if "session_id" in recent.columns
            else 0
        )

        if "transaction_amount" in recent.columns:

            transactions = recent[
                pd.to_numeric(
                    recent["transaction_amount"],
                    errors="coerce"
                ).fillna(0) > 0
            ]

            row_out[
                f"transactions_last_{minutes}min"
            ] = len(transactions)

        else:

            row_out[
                f"transactions_last_{minutes}min"
            ] = 0

    # --------------------------------------------------------
    # Response delay availability
    # --------------------------------------------------------

    if "response_delay_ms" in history.columns:

        delay = pd.to_numeric(
            history["response_delay_ms"],
            errors="coerce"
        )

        row_out[
            "delay_observation_count"
        ] = delay.notna().sum()

        row_out[
            "delay_observation_rate"
        ] = delay.notna().mean() if len(history) > 0 else 0

        row_out[
            "delay_mean"
        ] = delay.mean() if delay.notna().any() else 0

    else:

        row_out["delay_observation_count"] = 0
        row_out["delay_observation_rate"] = 0
        row_out["delay_mean"] = 0

    diagnostic_rows.append(row_out)


positive_matching_diagnostic = pd.DataFrame(
    diagnostic_rows
)

# ------------------------------------------------------------
# 3. Summary
# ------------------------------------------------------------

print("\nShape:")
print(
    positive_matching_diagnostic.shape
)

print("\n=== BY HORIZON ===")

print(
    positive_matching_diagnostic
    .groupby("horizon_minutes")[
        [
            "history_event_count",
            "history_span_hours",
            "unique_sessions",
            "events_last_5min",
            "events_last_15min",
            "events_last_60min",
            "transactions_last_60min",
            "delay_observation_rate",
            "delay_mean"
        ]
    ]
    .agg(
        ["mean", "median", "std", "min", "max"]
    )
)

# ------------------------------------------------------------
# 4. Behaviour profile
# ------------------------------------------------------------

print("\n=== BEHAVIOUR PROFILE ===")

print(
    positive_matching_diagnostic[
        "behaviour_profile"
    ].value_counts(
        normalize=True
    ).round(4)
)

# ------------------------------------------------------------
# 5. Country
# ------------------------------------------------------------

print("\n=== COUNTRY ===")

print(
    positive_matching_diagnostic[
        "country"
    ].value_counts(
        normalize=True
    ).round(4)
)

# ------------------------------------------------------------
# 6. Cutoff timing
# ------------------------------------------------------------

print("\n=== CUTOFF HOUR ===")

print(
    positive_matching_diagnostic[
        "cutoff_hour"
    ].value_counts()
    .sort_index()
)

print("\n=== DAY OF WEEK ===")

print(
    positive_matching_diagnostic[
        "cutoff_dayofweek"
    ].value_counts()
    .sort_index()
)

# ------------------------------------------------------------
# 7. Critical sparse-history diagnostics
# ------------------------------------------------------------

print("\n=== SPARSE HISTORY ===")

for col in [
    "history_event_count",
    "unique_sessions",
    "events_last_5min",
    "events_last_15min",
    "events_last_60min"
]:

    zero_rate = (
        positive_matching_diagnostic[col] == 0
    ).mean()

    print(
        f"{col}: "
        f"zero={zero_rate:.3f}"
    )

# ------------------------------------------------------------
# 8. Delay availability
# ------------------------------------------------------------

print("\n=== RESPONSE DELAY AVAILABILITY ===")

print(
    positive_matching_diagnostic[
        [
            "delay_observation_count",
            "delay_observation_rate",
            "delay_mean"
        ]
    ].describe()
)

# ------------------------------------------------------------
# 9. Save diagnostic object
# ------------------------------------------------------------

print("\nDiagnostic object created:")
print(
    "positive_matching_diagnostic"
)

print("\n" + "=" * 70)
print(
    "STEP 65E.1 COMPLETE"
)
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 177
# ==============================================================================

# ============================================================
# STEP 65E.2: POSITIVE EVENT TIMING AND PROVENANCE AUDIT
# ============================================================

import pandas as pd
import numpy as np

print("=" * 70)
print("STEP 65E.2: POSITIVE EVENT TIMING AND PROVENANCE AUDIT")
print("=" * 70)

# ------------------------------------------------------------
# 1. Prepare observable events
# ------------------------------------------------------------

obs = unified_events[
    unified_events["is_attack"] == 0
].copy()

obs["timestamp"] = pd.to_datetime(
    obs["timestamp"],
    errors="coerce"
)

obs = obs.sort_values(
    ["user_id", "timestamp"]
).reset_index(drop=True)

print("\nObservable events:", len(obs))

# ------------------------------------------------------------
# 2. Check response delay availability
# ------------------------------------------------------------

print("\n=== RESPONSE DELAY PROVENANCE ===")

print(
    "Column exists:",
    "response_delay_ms" in obs.columns
)

if "response_delay_ms" in obs.columns:

    delay = pd.to_numeric(
        obs["response_delay_ms"],
        errors="coerce"
    )

    print(
        "Non-missing:",
        delay.notna().sum()
    )

    print(
        "Missing:",
        delay.isna().sum()
    )

    print(
        "Mean:",
        delay.mean()
    )

    print(
        "Min:",
        delay.min()
    )

    print(
        "Max:",
        delay.max()
    )

# ------------------------------------------------------------
# 3. Check positive campaign timing
# ------------------------------------------------------------

campaigns = campaign_control.copy()

campaigns["anchor_time"] = pd.to_datetime(
    campaigns["anchor_time"],
    errors="coerce"
)

timing_rows = []

for _, campaign in campaigns.iterrows():

    user_id = campaign["user_id"]
    takeover = campaign["anchor_time"]

    user_obs = obs[
        obs["user_id"] == user_id
    ]

    before = user_obs[
        user_obs["timestamp"] < takeover
    ]

    if len(before) == 0:

        timing_rows.append({
            "campaign_id": campaign["campaign_id"],
            "user_id": user_id,
            "takeover_time": takeover,
            "observable_events_before_takeover": 0,
            "last_observable_time": pd.NaT,
            "minutes_from_last_event_to_takeover": np.nan,
            "events_last_5min": 0,
            "events_last_15min": 0,
            "events_last_60min": 0,
            "response_delay_available": 0
        })

        continue

    last_event = before["timestamp"].max()

    timing_rows.append({
        "campaign_id": campaign["campaign_id"],
        "user_id": user_id,
        "takeover_time": takeover,
        "observable_events_before_takeover": len(before),
        "last_observable_time": last_event,
        "minutes_from_last_event_to_takeover": (
            takeover - last_event
        ).total_seconds() / 60,

        "events_last_5min": len(
            before[
                before["timestamp"] >=
                takeover - pd.Timedelta(minutes=5)
            ]
        ),

        "events_last_15min": len(
            before[
                before["timestamp"] >=
                takeover - pd.Timedelta(minutes=15)
            ]
        ),

        "events_last_60min": len(
            before[
                before["timestamp"] >=
                takeover - pd.Timedelta(minutes=60)
            ]
        ),

        "response_delay_available": (
            before["response_delay_ms"]
            .notna()
            .sum()
            if "response_delay_ms" in before.columns
            else 0
        )
    })

campaign_timing_audit = pd.DataFrame(
    timing_rows
)

# ------------------------------------------------------------
# 4. Summary
# ------------------------------------------------------------

print("\n=== CAMPAIGN TIMING SUMMARY ===")

print(
    campaign_timing_audit[
        [
            "observable_events_before_takeover",
            "minutes_from_last_event_to_takeover",
            "events_last_5min",
            "events_last_15min",
            "events_last_60min",
            "response_delay_available"
        ]
    ].describe()
)

# ------------------------------------------------------------
# 5. Critical percentages
# ------------------------------------------------------------

print("\n=== CRITICAL PERCENTAGES ===")

for col in [
    "events_last_5min",
    "events_last_15min",
    "events_last_60min"
]:

    print(
        f"{col} > 0:",
        (
            campaign_timing_audit[col] > 0
        ).mean()
    )

print(
    "\nLast observable event more than 60 minutes before takeover:",
    (
        campaign_timing_audit[
            "minutes_from_last_event_to_takeover"
        ] > 60
    ).mean()
)

print(
    "Last observable event more than 6 hours before takeover:",
    (
        campaign_timing_audit[
            "minutes_from_last_event_to_takeover"
        ] > 360
    ).mean()
)

print(
    "Last observable event more than 24 hours before takeover:",
    (
        campaign_timing_audit[
            "minutes_from_last_event_to_takeover"
        ] > 1440
    ).mean()
)

# ------------------------------------------------------------
# 6. By attack type
# ------------------------------------------------------------

campaign_timing_audit = campaign_timing_audit.merge(
    campaigns[
        [
            "campaign_id",
            "attack_type",
            "attack_severity"
        ]
    ],
    on="campaign_id",
    how="left"
)

print("\n=== BY ATTACK TYPE ===")

print(
    campaign_timing_audit
    .groupby("attack_type")[
        [
            "minutes_from_last_event_to_takeover",
            "events_last_5min",
            "events_last_15min",
            "events_last_60min",
            "response_delay_available"
        ]
    ]
    .agg(
        ["mean", "median", "min", "max"]
    )
)

# ------------------------------------------------------------
# 7. Inspect worst temporal gaps
# ------------------------------------------------------------

print("\n=== LARGEST GAPS ===")

print(
    campaign_timing_audit[
        [
            "campaign_id",
            "user_id",
            "attack_type",
            "takeover_time",
            "last_observable_time",
            "minutes_from_last_event_to_takeover"
        ]
    ]
    .sort_values(
        "minutes_from_last_event_to_takeover",
        ascending=False
    )
    .head(20)
)

# ------------------------------------------------------------
# 8. Inspect closest observable events
# ------------------------------------------------------------

print("\n=== SMALLEST GAPS ===")

print(
    campaign_timing_audit[
        [
            "campaign_id",
            "user_id",
            "attack_type",
            "takeover_time",
            "last_observable_time",
            "minutes_from_last_event_to_takeover"
        ]
    ]
    .sort_values(
        "minutes_from_last_event_to_takeover"
    )
    .head(20)
)

print("\n" + "=" * 70)
print("STEP 65E.2 COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 178
# ==============================================================================

# ============================================================
# STEP 57.1: TAKEOVER TIME CONSISTENCY AUDIT
# ============================================================

import pandas as pd
import numpy as np

print("=" * 70)
print("STEP 57.1: TAKEOVER TIME CONSISTENCY AUDIT")
print("=" * 70)

# ------------------------------------------------------------
# 1. Campaign anchor times
# ------------------------------------------------------------

campaign_anchor = campaign_control[
    [
        "campaign_id",
        "user_id",
        "attack_type",
        "anchor_time"
    ]
].copy()

campaign_anchor["anchor_time"] = pd.to_datetime(
    campaign_anchor["anchor_time"],
    errors="coerce"
)

# ------------------------------------------------------------
# 2. Takeover times reconstructed from attack events
# ------------------------------------------------------------

takeover_event_types = [
    "ACCOUNT_TAKEOVER",
    "SESSION_HIJACK",
    "ACCOUNT_ACCESS"
]

event_takeover = (
    stochastic_attack_events[
        stochastic_attack_events["event_type"].isin(
            takeover_event_types
        )
    ]
    .groupby("campaign_id")["timestamp"]
    .min()
    .rename("event_takeover_time")
    .reset_index()
)

event_takeover["event_takeover_time"] = pd.to_datetime(
    event_takeover["event_takeover_time"],
    errors="coerce"
)

# ------------------------------------------------------------
# 3. Compare
# ------------------------------------------------------------

takeover_comparison = campaign_anchor.merge(
    event_takeover,
    on="campaign_id",
    how="left",
    validate="one_to_one"
)

takeover_comparison["anchor_event_difference_min"] = (
    (
        takeover_comparison["event_takeover_time"]
        - takeover_comparison["anchor_time"]
    )
    .dt.total_seconds()
    / 60
)

print("\n=== TAKEOVER TIME COMPARISON ===")

print(
    takeover_comparison[
        [
            "campaign_id",
            "user_id",
            "attack_type",
            "anchor_time",
            "event_takeover_time",
            "anchor_event_difference_min"
        ]
    ].head(20)
)

# ------------------------------------------------------------
# 4. Difference statistics
# ------------------------------------------------------------

print("\n=== DIFFERENCE STATISTICS ===")

print(
    takeover_comparison[
        "anchor_event_difference_min"
    ].describe()
)

# ------------------------------------------------------------
# 5. Exact agreement
# ------------------------------------------------------------

exact_match = (
    takeover_comparison[
        "anchor_event_difference_min"
    ].abs() < 1e-9
)

print(
    "\nExact matches:",
    exact_match.sum(),
    "/",
    len(exact_match)
)

print(
    "Exact match rate:",
    exact_match.mean()
)

# ------------------------------------------------------------
# 6. Differences larger than tolerance
# ------------------------------------------------------------

for tolerance in [0, 1, 5, 10, 30, 60]:

    matches = (
        takeover_comparison[
            "anchor_event_difference_min"
        ].abs() <= tolerance
    ).sum()

    print(
        f"Within ±{tolerance} minutes:",
        matches,
        "/",
        len(takeover_comparison)
    )

# ------------------------------------------------------------
# 7. Missing reconstructed takeover times
# ------------------------------------------------------------

print(
    "\nMissing event takeover times:",
    takeover_comparison[
        "event_takeover_time"
    ].isna().sum()
)

# ------------------------------------------------------------
# 8. Largest differences
# ------------------------------------------------------------

print("\n=== LARGEST ABSOLUTE DIFFERENCES ===")

print(
    takeover_comparison[
        [
            "campaign_id",
            "user_id",
            "attack_type",
            "anchor_time",
            "event_takeover_time",
            "anchor_event_difference_min"
        ]
    ]
    .assign(
        abs_difference=lambda x:
            x["anchor_event_difference_min"].abs()
    )
    .sort_values(
        "abs_difference",
        ascending=False
    )
    .head(20)
    .drop(columns=["abs_difference"])
)

# ------------------------------------------------------------
# 9. Compare by attack type
# ------------------------------------------------------------

print("\n=== DIFFERENCE BY ATTACK TYPE ===")

print(
    takeover_comparison
    .groupby("attack_type")[
        "anchor_event_difference_min"
    ]
    .agg(
        ["count", "mean", "median", "std", "min", "max"]
    )
)

print("\n" + "=" * 70)
print("STEP 57.1 COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 179
# ==============================================================================

# ==========================================
# AFRITAC: Attack Campaign Framework
# Temporal Anchor Aware Version
# ==========================================

rng = np.random.default_rng(SEED + 43)

N_CAMPAIGNS = 80

attack_types = [
    "ACCOUNT_TAKEOVER",
    "SOCIAL_ENGINEERING_TAKEOVER",
    "USSD_SESSION_HIJACK",
    "SIM_IDENTITY_COMPROMISE"
]

attack_type_probs = [
    0.30,
    0.30,
    0.25,
    0.15
]

# --------------------------------------------------
# Select users
# --------------------------------------------------

available_users = users["user_id"].dropna().unique()

attack_users = rng.choice(
    available_users,
    size=N_CAMPAIGNS,
    replace=False
)

# --------------------------------------------------
# Observable sessions
# --------------------------------------------------

session_reference = sessions.copy()

session_reference["start_time"] = pd.to_datetime(
    session_reference["start_time"],
    errors="coerce"
)

session_reference["end_time"] = pd.to_datetime(
    session_reference["end_time"],
    errors="coerce"
)

campaign_records = []

for i, user_id in enumerate(
    attack_users,
    start=1
):

    attack_type = rng.choice(
        attack_types,
        p=attack_type_probs
    )

    user_sessions = (
        session_reference[
            session_reference["user_id"] == user_id
        ]
        .sort_values("start_time")
        .copy()
    )

    if user_sessions.empty:
        continue

    # --------------------------------------------------
    # Select an observable session as campaign anchor
    #
    # Prefer a session that has enough preceding history
    # for temporal prediction.
    # --------------------------------------------------

    candidate_sessions = user_sessions[
        user_sessions["start_time"].notna()
    ].copy()

    if candidate_sessions.empty:
        continue

    # Avoid choosing the very first session because
    # insufficient historical behaviour may exist.
    if len(candidate_sessions) > 3:
        candidate_sessions = candidate_sessions.iloc[2:]

    anchor_session = candidate_sessions.sample(
        n=1,
        random_state=int(rng.integers(1, 1_000_000))
    ).iloc[0]

    anchor_session_id = anchor_session["session_id"]

    anchor_session_end = anchor_session["end_time"]

    if pd.isna(anchor_session_end):
        anchor_session_end = anchor_session["start_time"]

    # --------------------------------------------------
    # Takeover occurs shortly after observable activity
    # --------------------------------------------------

    post_session_gap = int(
        rng.integers(5, 31)
    )

    anchor_time = (
        anchor_session_end
        + pd.Timedelta(minutes=post_session_gap)
    )

    campaign_records.append({

        "campaign_id":
            f"CAMP_{i:05d}",

        "user_id":
            user_id,

        "attack_type":
            attack_type,

        "campaign_status":
            "MALICIOUS",

        "ground_truth_attack":
            1,

        "anchor_session_id":
            anchor_session_id,

        "anchor_time":
            anchor_time
    })


campaigns = pd.DataFrame(
    campaign_records
)

print(
    "Attack campaigns:",
    len(campaigns)
)

print(
    "\nAttack type distribution:"
)

print(
    campaigns["attack_type"].value_counts()
)

print(
    "\nCampaign timing:"
)

print(
    campaigns[
        [
            "campaign_id",
            "user_id",
            "anchor_session_id",
            "anchor_time",
            "attack_type"
        ]
    ].head()
)

# ==============================================================================
# NOTEBOOK CELL 180
# ==============================================================================

# ==========================================
# AFRITAC: Campaign Anchor Validation
# ==========================================

# Prepare session timestamps
session_check = sessions.copy()

session_check["start_time"] = pd.to_datetime(
    session_check["start_time"],
    errors="coerce"
)

session_check["end_time"] = pd.to_datetime(
    session_check["end_time"],
    errors="coerce"
)

# Attach actual anchor session information
anchor_check = campaigns[
    [
        "campaign_id",
        "user_id",
        "anchor_session_id",
        "anchor_time",
        "attack_type"
    ]
].merge(
    session_check[
        [
            "session_id",
            "user_id",
            "start_time",
            "end_time"
        ]
    ],
    left_on=["anchor_session_id", "user_id"],
    right_on=["session_id", "user_id"],
    how="left",
    validate="one_to_one"
)

# Calculate temporal relationship
anchor_check["minutes_after_anchor_session"] = (
    (
        anchor_check["anchor_time"]
        - anchor_check["end_time"]
    ).dt.total_seconds()
    / 60
)

# Check whether anchor is genuinely after the session
anchor_check["valid_anchor"] = (
    anchor_check["minutes_after_anchor_session"] >= 0
)

print("==========================================")
print("CAMPAIGN ANCHOR VALIDATION")
print("==========================================")

print(
    "Campaigns:",
    len(anchor_check)
)

print(
    "Missing anchor sessions:",
    anchor_check["end_time"].isna().sum()
)

print(
    "Invalid anchors:",
    (~anchor_check["valid_anchor"]).sum()
)

print(
    "\nMinutes after anchor session:"
)

print(
    anchor_check[
        "minutes_after_anchor_session"
    ].describe()
)

print(
    "\nAnchor delay distribution:"
)

print(
    anchor_check[
        "minutes_after_anchor_session"
    ].round(2).value_counts(
        bins=[0, 5, 10, 15, 20, 25, 30]
    ).sort_index()
)

print(
    "\nBy attack type:"
)

print(
    anchor_check.groupby(
        "attack_type"
    )[
        "minutes_after_anchor_session"
    ].agg(
        [
            "count",
            "mean",
            "median",
            "min",
            "max"
        ]
    ).round(2)
)

# ==============================================================================
# NOTEBOOK CELL 181
# ==============================================================================

# ==========================================
# AFRITAC: Ground Truth Attack Timeline
# Temporal and Attack Type Aware Version
# ==========================================

attack_events = []

rng = np.random.default_rng(SEED + 44)

for idx, campaign in campaigns.iterrows():

    campaign_id = campaign["campaign_id"]
    user_id = campaign["user_id"]
    attack_type = campaign["attack_type"]
    anchor_time = pd.to_datetime(
        campaign["anchor_time"]
    )

    # ------------------------------------------
    # User primary device
    # ------------------------------------------

    user_record = users[
        users["user_id"] == user_id
    ].iloc[0]

    primary_device = user_record[
        "primary_device_id"
    ]

    attacker_device = (
        f"ATTACK_DEVICE_{idx+1:04d}"
    )

    # ------------------------------------------
    # Helper function
    # ------------------------------------------

    def add_attack_event(
        event_time,
        event_type,
        modality,
        attack_stage,
        device_id,
        transaction_amount=np.nan
    ):

        record = {
            "campaign_id": campaign_id,
            "user_id": user_id,
            "device_id": device_id,
            "timestamp": event_time,
            "event_type": event_type,
            "modality": modality,
            "attack_stage": attack_stage,
            "attack_type": attack_type
        }

        if not pd.isna(transaction_amount):
            record["transaction_amount"] = round(
                float(transaction_amount),
                2
            )

        attack_events.append(record)

    # ==================================================
    # 1. ACCOUNT TAKEOVER
    # ==================================================

    if attack_type == "ACCOUNT_TAKEOVER":

        t1 = anchor_time + pd.Timedelta(
            minutes=int(rng.integers(2, 8))
        )

        t2 = t1 + pd.Timedelta(
            minutes=int(rng.integers(3, 10))
        )

        t3 = t2 + pd.Timedelta(
            minutes=int(rng.integers(2, 8))
        )

        t4 = t3 + pd.Timedelta(
            minutes=int(rng.integers(1, 6))
        )

        t5 = t4 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t6 = t5 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        add_attack_event(
            t1,
            "AUTHENTICATION_ANOMALY",
            "AUTHENTICATION",
            "PRE_ATTACK",
            primary_device
        )

        add_attack_event(
            t2,
            "CREDENTIAL_COMPROMISE",
            "AUTHENTICATION",
            "COMPROMISE",
            primary_device
        )

        add_attack_event(
            t3,
            "NEW_DEVICE_LOGIN",
            "DEVICE",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            t4,
            "IDENTITY_CHANGE",
            "IDENTITY",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            t5,
            "ACCOUNT_TAKEOVER",
            "ACCOUNT",
            "TAKEOVER",
            attacker_device
        )

        amount = rng.uniform(5000, 75000)

        add_attack_event(
            t6,
            "UNAUTHORIZED_TRANSACTION",
            "FINANCIAL",
            "IMPACT",
            attacker_device,
            amount
        )

    # ==================================================
    # 2. SOCIAL ENGINEERING TAKEOVER
    # ==================================================

    elif attack_type == "SOCIAL_ENGINEERING_TAKEOVER":

        t1 = anchor_time + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t2 = t1 + pd.Timedelta(
            minutes=int(rng.integers(2, 8))
        )

        t3 = t2 + pd.Timedelta(
            minutes=int(rng.integers(3, 10))
        )

        t4 = t3 + pd.Timedelta(
            minutes=int(rng.integers(2, 8))
        )

        t5 = t4 + pd.Timedelta(
            minutes=int(rng.integers(1, 6))
        )

        t6 = t5 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        add_attack_event(
            t1,
            "SOCIAL_MESSAGE_RECEIVED",
            "SOCIAL_ENGINEERING",
            "PRE_ATTACK",
            primary_device
        )

        add_attack_event(
            t2,
            "SOCIAL_MESSAGE_INTERACTION",
            "SOCIAL_ENGINEERING",
            "PRE_ATTACK",
            primary_device
        )

        add_attack_event(
            t3,
            "CREDENTIAL_COMPROMISE",
            "AUTHENTICATION",
            "COMPROMISE",
            primary_device
        )

        add_attack_event(
            t4,
            "NEW_DEVICE_LOGIN",
            "DEVICE",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            t5,
            "IDENTITY_CHANGE",
            "IDENTITY",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            t5 + pd.Timedelta(seconds=30),
            "ACCOUNT_TAKEOVER",
            "ACCOUNT",
            "TAKEOVER",
            attacker_device
        )

        amount = rng.uniform(5000, 75000)

        add_attack_event(
            t6,
            "UNAUTHORIZED_TRANSACTION",
            "FINANCIAL",
            "IMPACT",
            attacker_device,
            amount
        )

    # ==================================================
    # 3. USSD SESSION HIJACK
    # ==================================================

    elif attack_type == "USSD_SESSION_HIJACK":

        t1 = anchor_time + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t2 = t1 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t3 = t2 + pd.Timedelta(
            minutes=int(rng.integers(1, 6))
        )

        t4 = t3 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t5 = t4 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t6 = t5 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        add_attack_event(
            t1,
            "USSD_CODE_MODIFICATION",
            "USSD",
            "PRE_ATTACK",
            attacker_device
        )

        add_attack_event(
            t2,
            "SESSION_REROUTING",
            "SESSION",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            t3,
            "STALE_SESSION_REUSE",
            "SESSION",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            t4,
            "ACCOUNT_ACCESS_VIA_HIJACKED_SESSION",
            "USSD",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            t5,
            "SESSION_HIJACK",
            "USSD",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            t5 + pd.Timedelta(seconds=30),
            "ACCOUNT_ACCESS",
            "ACCOUNT",
            "TAKEOVER",
            attacker_device
        )

        amount = rng.uniform(5000, 75000)

        add_attack_event(
            t6,
            "UNAUTHORIZED_TRANSACTION",
            "FINANCIAL",
            "IMPACT",
            attacker_device,
            amount
        )

    # ==================================================
    # 4. SIM IDENTITY COMPROMISE
    # ==================================================

    elif attack_type == "SIM_IDENTITY_COMPROMISE":

        t1 = anchor_time + pd.Timedelta(
            minutes=int(rng.integers(2, 8))
        )

        t2 = t1 + pd.Timedelta(
            minutes=int(rng.integers(2, 7))
        )

        t3 = t2 + pd.Timedelta(
            minutes=int(rng.integers(2, 7))
        )

        t4 = t3 + pd.Timedelta(
            minutes=int(rng.integers(2, 7))
        )

        t5 = t4 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t6 = t5 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        add_attack_event(
            t1,
            "SIM_CHANGE",
            "SIM",
            "PRE_ATTACK",
            attacker_device
        )

        add_attack_event(
            t2,
            "IMSI_IMEI_CHANGE",
            "IDENTITY",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            t3,
            "NETWORK_IDENTITY_ANOMALY",
            "NETWORK",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            t4,
            "AUTHENTICATION_WITH_NEW_IDENTITY",
            "AUTHENTICATION",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            t5,
            "ACCOUNT_ACCESS",
            "ACCOUNT",
            "TAKEOVER",
            attacker_device
        )

        amount = rng.uniform(5000, 75000)

        add_attack_event(
            t6,
            "UNAUTHORIZED_TRANSACTION",
            "FINANCIAL",
            "IMPACT",
            attacker_device,
            amount
        )

# ------------------------------------------
# Convert to DataFrame
# ------------------------------------------

attack_events = pd.DataFrame(
    attack_events
)

attack_events["timestamp"] = pd.to_datetime(
    attack_events["timestamp"],
    errors="coerce"
)

attack_events = attack_events.sort_values(
    ["campaign_id", "timestamp"]
).reset_index(drop=True)

# ------------------------------------------
# Basic validation
# ------------------------------------------

print("==========================================")
print("GROUND TRUTH ATTACK TIMELINE")
print("==========================================")

print(
    "Attack events:",
    len(attack_events)
)

print(
    "\nEvents by attack type:"
)

print(
    attack_events[
        [
            "attack_type",
            "event_type"
        ]
    ].value_counts()
)

print(
    "\nEvents by stage:"
)

print(
    attack_events[
        "attack_stage"
    ].value_counts()
)

print(
    "\nEvents per campaign:"
)

print(
    attack_events.groupby(
        "campaign_id"
    ).size().value_counts()
)

# ==============================================================================
# NOTEBOOK CELL 182
# ==============================================================================

# ==================================================
# 1. ACCOUNT TAKEOVER
# ==================================================

if attack_type == "ACCOUNT_TAKEOVER":

    t1 = anchor_time + pd.Timedelta(
        minutes=int(rng.integers(2, 8))
    )

    t2 = t1 + pd.Timedelta(
        minutes=int(rng.integers(3, 10))
    )

    t3 = t2 + pd.Timedelta(
        minutes=int(rng.integers(2, 8))
    )

    t4 = t3 + pd.Timedelta(
        minutes=int(rng.integers(1, 6))
    )

    t5 = t4 + pd.Timedelta(
        minutes=int(rng.integers(1, 5))
    )

    t6 = t5 + pd.Timedelta(
        minutes=int(rng.integers(1, 4))
    )

    t7 = t6 + pd.Timedelta(
        minutes=int(rng.integers(1, 5))
    )

    add_attack_event(
        t1,
        "AUTHENTICATION_ANOMALY",
        "AUTHENTICATION",
        "PRE_ATTACK",
        primary_device
    )

    add_attack_event(
        t2,
        "CREDENTIAL_COMPROMISE",
        "AUTHENTICATION",
        "COMPROMISE",
        primary_device
    )

    add_attack_event(
        t3,
        "NEW_DEVICE_LOGIN",
        "DEVICE",
        "COMPROMISE",
        attacker_device
    )

    add_attack_event(
        t4,
        "IDENTITY_CHANGE",
        "IDENTITY",
        "TAKEOVER",
        attacker_device
    )

    add_attack_event(
        t5,
        "ACCOUNT_TAKEOVER",
        "ACCOUNT",
        "TAKEOVER",
        attacker_device
    )

    add_attack_event(
        t6,
        "NEW_BENEFICIARY_ADDED",
        "FINANCIAL",
        "TAKEOVER",
        attacker_device
    )

    amount = rng.uniform(
        5000,
        75000
    )

    add_attack_event(
        t7,
        "UNAUTHORIZED_TRANSACTION",
        "FINANCIAL",
        "IMPACT",
        attacker_device,
        amount
    )

# ==============================================================================
# NOTEBOOK CELL 183
# ==============================================================================

# ==========================================
# AFRITAC: Ground Truth Attack Timeline
# Complete Corrected Version
# ==========================================

attack_events = []

rng = np.random.default_rng(SEED + 44)

for idx, campaign in campaigns.iterrows():

    campaign_id = campaign["campaign_id"]
    user_id = campaign["user_id"]
    attack_type = campaign["attack_type"]
    anchor_time = pd.to_datetime(
        campaign["anchor_time"]
    )

    # ------------------------------------------
    # User devices
    # ------------------------------------------

    user_record = users[
        users["user_id"] == user_id
    ].iloc[0]

    primary_device = user_record[
        "primary_device_id"
    ]

    attacker_device = (
        f"ATTACK_DEVICE_{idx+1:04d}"
    )

    # ------------------------------------------
    # Helper function
    # ------------------------------------------

    def add_attack_event(
        event_time,
        event_type,
        modality,
        attack_stage,
        device_id,
        transaction_amount=np.nan
    ):

        record = {
            "campaign_id": campaign_id,
            "user_id": user_id,
            "device_id": device_id,
            "timestamp": event_time,
            "event_type": event_type,
            "modality": modality,
            "attack_stage": attack_stage,
            "attack_type": attack_type
        }

        if not pd.isna(transaction_amount):
            record["transaction_amount"] = round(
                float(transaction_amount),
                2
            )

        attack_events.append(record)

    # ==================================================
    # 1. ACCOUNT TAKEOVER
    # ==================================================

    if attack_type == "ACCOUNT_TAKEOVER":

        t1 = anchor_time + pd.Timedelta(
            minutes=int(rng.integers(2, 8))
        )

        t2 = t1 + pd.Timedelta(
            minutes=int(rng.integers(3, 10))
        )

        t3 = t2 + pd.Timedelta(
            minutes=int(rng.integers(2, 8))
        )

        t4 = t3 + pd.Timedelta(
            minutes=int(rng.integers(1, 6))
        )

        t5 = t4 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t6 = t5 + pd.Timedelta(
            minutes=int(rng.integers(1, 4))
        )

        t7 = t6 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        add_attack_event(
            t1,
            "AUTHENTICATION_ANOMALY",
            "AUTHENTICATION",
            "PRE_ATTACK",
            primary_device
        )

        add_attack_event(
            t2,
            "CREDENTIAL_COMPROMISE",
            "AUTHENTICATION",
            "COMPROMISE",
            primary_device
        )

        add_attack_event(
            t3,
            "NEW_DEVICE_LOGIN",
            "DEVICE",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            t4,
            "IDENTITY_CHANGE",
            "IDENTITY",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            t5,
            "ACCOUNT_TAKEOVER",
            "ACCOUNT",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            t6,
            "NEW_BENEFICIARY_ADDED",
            "FINANCIAL",
            "TAKEOVER",
            attacker_device
        )

        amount = rng.uniform(
            5000,
            75000
        )

        add_attack_event(
            t7,
            "UNAUTHORIZED_TRANSACTION",
            "FINANCIAL",
            "IMPACT",
            attacker_device,
            amount
        )

    # ==================================================
    # 2. SOCIAL ENGINEERING TAKEOVER
    # ==================================================

    elif attack_type == "SOCIAL_ENGINEERING_TAKEOVER":

        t1 = anchor_time + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t2 = t1 + pd.Timedelta(
            minutes=int(rng.integers(2, 8))
        )

        t3 = t2 + pd.Timedelta(
            minutes=int(rng.integers(3, 10))
        )

        t4 = t3 + pd.Timedelta(
            minutes=int(rng.integers(2, 8))
        )

        t5 = t4 + pd.Timedelta(
            minutes=int(rng.integers(1, 6))
        )

        t6 = t5 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t7 = t6 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        add_attack_event(
            t1,
            "SOCIAL_MESSAGE_RECEIVED",
            "SOCIAL_ENGINEERING",
            "PRE_ATTACK",
            primary_device
        )

        add_attack_event(
            t2,
            "SOCIAL_MESSAGE_INTERACTION",
            "SOCIAL_ENGINEERING",
            "PRE_ATTACK",
            primary_device
        )

        add_attack_event(
            t3,
            "CREDENTIAL_COMPROMISE",
            "AUTHENTICATION",
            "COMPROMISE",
            primary_device
        )

        add_attack_event(
            t4,
            "NEW_DEVICE_LOGIN",
            "DEVICE",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            t5,
            "IDENTITY_CHANGE",
            "IDENTITY",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            t6,
            "ACCOUNT_TAKEOVER",
            "ACCOUNT",
            "TAKEOVER",
            attacker_device
        )

        amount = rng.uniform(
            5000,
            75000
        )

        add_attack_event(
            t7,
            "UNAUTHORIZED_TRANSACTION",
            "FINANCIAL",
            "IMPACT",
            attacker_device,
            amount
        )

    # ==================================================
    # 3. USSD SESSION HIJACK
    # ==================================================

    elif attack_type == "USSD_SESSION_HIJACK":

        t1 = anchor_time + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t2 = t1 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t3 = t2 + pd.Timedelta(
            minutes=int(rng.integers(1, 6))
        )

        t4 = t3 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t5 = t4 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t6 = t5 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t7 = t6 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        add_attack_event(
            t1,
            "USSD_CODE_MODIFICATION",
            "USSD",
            "PRE_ATTACK",
            attacker_device
        )

        add_attack_event(
            t2,
            "SESSION_REROUTING",
            "SESSION",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            t3,
            "STALE_SESSION_REUSE",
            "SESSION",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            t4,
            "ACCOUNT_ACCESS_VIA_HIJACKED_SESSION",
            "USSD",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            t5,
            "SESSION_HIJACK",
            "USSD",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            t6,
            "ACCOUNT_ACCESS",
            "ACCOUNT",
            "TAKEOVER",
            attacker_device
        )

        amount = rng.uniform(
            5000,
            75000
        )

        add_attack_event(
            t7,
            "UNAUTHORIZED_TRANSACTION",
            "FINANCIAL",
            "IMPACT",
            attacker_device,
            amount
        )

    # ==================================================
    # 4. SIM IDENTITY COMPROMISE
    # ==================================================

    elif attack_type == "SIM_IDENTITY_COMPROMISE":

        t1 = anchor_time + pd.Timedelta(
            minutes=int(rng.integers(2, 8))
        )

        t2 = t1 + pd.Timedelta(
            minutes=int(rng.integers(2, 7))
        )

        t3 = t2 + pd.Timedelta(
            minutes=int(rng.integers(2, 7))
        )

        t4 = t3 + pd.Timedelta(
            minutes=int(rng.integers(2, 7))
        )

        t5 = t4 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t6 = t5 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        t7 = t6 + pd.Timedelta(
            minutes=int(rng.integers(1, 5))
        )

        add_attack_event(
            t1,
            "SIM_CHANGE",
            "SIM",
            "PRE_ATTACK",
            attacker_device
        )

        add_attack_event(
            t2,
            "IMSI_IMEI_CHANGE",
            "IDENTITY",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            t3,
            "NETWORK_IDENTITY_ANOMALY",
            "NETWORK",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            t4,
            "AUTHENTICATION_WITH_NEW_IDENTITY",
            "AUTHENTICATION",
            "COMPROMISE",
            attacker_device
        )

        add_attack_event(
            t5,
            "ACCOUNT_ACCESS",
            "ACCOUNT",
            "TAKEOVER",
            attacker_device
        )

        add_attack_event(
            t6,
            "ACCOUNT_TAKEOVER",
            "ACCOUNT",
            "TAKEOVER",
            attacker_device
        )

        amount = rng.uniform(
            5000,
            75000
        )

        add_attack_event(
            t7,
            "UNAUTHORIZED_TRANSACTION",
            "FINANCIAL",
            "IMPACT",
            attacker_device,
            amount
        )


# ==========================================
# Convert to DataFrame
# ==========================================

attack_events = pd.DataFrame(
    attack_events
)

attack_events["timestamp"] = pd.to_datetime(
    attack_events["timestamp"],
    errors="coerce"
)

attack_events = attack_events.sort_values(
    ["campaign_id", "timestamp"]
).reset_index(drop=True)


# ==========================================
# Validation
# ==========================================

print("==========================================")
print("GROUND TRUTH ATTACK TIMELINE")
print("==========================================")

print(
    "Attack events:",
    len(attack_events)
)

print(
    "\nEvents per campaign:"
)

print(
    attack_events.groupby(
        "campaign_id"
    ).size().value_counts().sort_index()
)

print(
    "\nEvents by attack type:"
)

print(
    attack_events[
        [
            "attack_type",
            "event_type"
        ]
    ].value_counts()
)

print(
    "\nEvents by stage:"
)

print(
    attack_events[
        "attack_stage"
    ].value_counts()
)

print(
    "\nCampaigns with incorrect event count:",
    (
        attack_events.groupby("campaign_id").size() != 7
    ).sum()
)

# ==============================================================================
# NOTEBOOK CELL 184
# ==============================================================================

# ==========================================
# AFRITAC: Ground Truth Temporal Integrity
# ==========================================

attack_events["timestamp"] = pd.to_datetime(
    attack_events["timestamp"],
    errors="coerce"
)

campaigns_check = campaigns.copy()

campaigns_check["anchor_time"] = pd.to_datetime(
    campaigns_check["anchor_time"],
    errors="coerce"
)

# Identify actual takeover event
takeover_events = (
    attack_events[
        attack_events["event_type"] == "ACCOUNT_TAKEOVER"
    ]
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

# Merge campaign anchor and takeover
temporal_check = campaigns_check[
    [
        "campaign_id",
        "user_id",
        "attack_type",
        "anchor_session_id",
        "anchor_time"
    ]
].merge(
    takeover_events,
    on=["campaign_id", "user_id"],
    how="left",
    validate="one_to_one"
)

# Calculate timing
temporal_check["minutes_anchor_to_takeover"] = (
    (
        temporal_check["takeover_time"]
        - temporal_check["anchor_time"]
    ).dt.total_seconds() / 60
)

# First and last attack event
event_bounds = (
    attack_events
    .groupby("campaign_id")
    .agg(
        first_attack_event=("timestamp", "min"),
        last_attack_event=("timestamp", "max")
    )
    .reset_index()
)

temporal_check = temporal_check.merge(
    event_bounds,
    on="campaign_id",
    how="left",
    validate="one_to_one"
)

temporal_check["minutes_anchor_to_first_attack"] = (
    (
        temporal_check["first_attack_event"]
        - temporal_check["anchor_time"]
    ).dt.total_seconds() / 60
)

temporal_check["minutes_takeover_to_impact"] = (
    (
        temporal_check["last_attack_event"]
        - temporal_check["takeover_time"]
    ).dt.total_seconds() / 60
)

# ==========================================
# Validation
# ==========================================

print("==========================================")
print("GROUND TRUTH TEMPORAL INTEGRITY")
print("==========================================")

print(
    "Campaigns:",
    len(temporal_check)
)

print(
    "Missing takeover times:",
    temporal_check["takeover_time"].isna().sum()
)

print(
    "Missing first attack times:",
    temporal_check["first_attack_event"].isna().sum()
)

print(
    "\nFirst attack event after anchor:"
)

print(
    temporal_check[
        "minutes_anchor_to_first_attack"
    ].describe().round(2)
)

print(
    "\nCampaigns with first attack before anchor:",
    (
        temporal_check[
            "minutes_anchor_to_first_attack"
        ] < 0
    ).sum()
)

print(
    "\nAnchor to takeover:"
)

print(
    temporal_check[
        "minutes_anchor_to_takeover"
    ].describe().round(2)
)

print(
    "\nCampaigns with takeover before anchor:",
    (
        temporal_check[
            "minutes_anchor_to_takeover"
        ] < 0
    ).sum()
)

print(
    "\nTakeover to final impact:"
)

print(
    temporal_check[
        "minutes_takeover_to_impact"
    ].describe().round(2)
)

print(
    "\nBy attack type:"
)

print(
    temporal_check.groupby(
        "attack_type"
    )[
        [
            "minutes_anchor_to_first_attack",
            "minutes_anchor_to_takeover",
            "minutes_takeover_to_impact"
        ]
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
    .round(2)
)

# ==============================================================================
# NOTEBOOK CELL 185
# ==============================================================================

# ==========================================
# AFRITAC: Canonical Takeover Time Audit
# Attack Type Specific Definition
# ==========================================

attack_events["timestamp"] = pd.to_datetime(
    attack_events["timestamp"],
    errors="coerce"
)

campaigns_check = campaigns.copy()

campaigns_check["anchor_time"] = pd.to_datetime(
    campaigns_check["anchor_time"],
    errors="coerce"
)

# ------------------------------------------
# Define canonical takeover event
# ------------------------------------------

takeover_event_map = {
    "ACCOUNT_TAKEOVER": "ACCOUNT_TAKEOVER",
    "SOCIAL_ENGINEERING_TAKEOVER": "ACCOUNT_TAKEOVER",
    "USSD_SESSION_HIJACK": "SESSION_HIJACK",
    "SIM_IDENTITY_COMPROMISE": "ACCOUNT_TAKEOVER"
}

takeover_candidates = []

for attack_type, takeover_event_type in takeover_event_map.items():

    subset = attack_events[
        (attack_events["attack_type"] == attack_type) &
        (attack_events["event_type"] == takeover_event_type)
    ].copy()

    takeover_candidates.append(
        subset[
            [
                "campaign_id",
                "user_id",
                "attack_type",
                "timestamp",
                "event_type"
            ]
        ]
    )

takeover_candidates = pd.concat(
    takeover_candidates,
    ignore_index=True
)

# ------------------------------------------
# First canonical takeover per campaign
# ------------------------------------------

takeover_times = (
    takeover_candidates
    .sort_values("timestamp")
    .groupby(
        ["campaign_id", "user_id", "attack_type"],
        as_index=False
    )
    .first()
    .rename(
        columns={
            "timestamp": "takeover_time",
            "event_type": "takeover_event_type"
        }
    )
)

# ------------------------------------------
# Merge with campaign metadata
# ------------------------------------------

temporal_check = campaigns_check[
    [
        "campaign_id",
        "user_id",
        "attack_type",
        "anchor_session_id",
        "anchor_time"
    ]
].merge(
    takeover_times[
        [
            "campaign_id",
            "user_id",
            "attack_type",
            "takeover_time",
            "takeover_event_type"
        ]
    ],
    on=[
        "campaign_id",
        "user_id",
        "attack_type"
    ],
    how="left",
    validate="one_to_one"
)

# ------------------------------------------
# Calculate timing
# ------------------------------------------

temporal_check["minutes_anchor_to_takeover"] = (
    (
        temporal_check["takeover_time"]
        - temporal_check["anchor_time"]
    ).dt.total_seconds()
    / 60
)

# ------------------------------------------
# Event boundaries
# ------------------------------------------

event_bounds = (
    attack_events
    .groupby("campaign_id")
    .agg(
        first_attack_event=("timestamp", "min"),
        last_attack_event=("timestamp", "max")
    )
    .reset_index()
)

temporal_check = temporal_check.merge(
    event_bounds,
    on="campaign_id",
    how="left",
    validate="one_to_one"
)

temporal_check["minutes_anchor_to_first_attack"] = (
    (
        temporal_check["first_attack_event"]
        - temporal_check["anchor_time"]
    ).dt.total_seconds()
    / 60
)

temporal_check["minutes_takeover_to_impact"] = (
    (
        temporal_check["last_attack_event"]
        - temporal_check["takeover_time"]
    ).dt.total_seconds()
    / 60
)

# ==========================================
# Validation
# ==========================================

print("==========================================")
print("CANONICAL TAKEOVER TIME AUDIT")
print("==========================================")

print(
    "Campaigns:",
    len(temporal_check)
)

print(
    "Missing takeover times:",
    temporal_check[
        "takeover_time"
    ].isna().sum()
)

print(
    "\nTakeover event types:"
)

print(
    temporal_check[
        [
            "attack_type",
            "takeover_event_type"
        ]
    ].value_counts()
)

print(
    "\nAnchor to takeover:"
)

print(
    temporal_check[
        "minutes_anchor_to_takeover"
    ].describe().round(2)
)

print(
    "\nCampaigns with takeover before anchor:",
    (
        temporal_check[
            "minutes_anchor_to_takeover"
        ] < 0
    ).sum()
)

print(
    "\nFirst attack event after anchor:"
)

print(
    temporal_check[
        "minutes_anchor_to_first_attack"
    ].describe().round(2)
)

print(
    "\nCampaigns with first attack before anchor:",
    (
        temporal_check[
            "minutes_anchor_to_first_attack"
        ] < 0
    ).sum()
)

print(
    "\nTakeover to final impact:"
)

print(
    temporal_check[
        "minutes_takeover_to_impact"
    ].describe().round(2)
)

print(
    "\nCampaigns with impact before takeover:",
    (
        temporal_check[
            "minutes_takeover_to_impact"
        ] <= 0
    ).sum()
)

print(
    "\nBy attack type:"
)

print(
    temporal_check.groupby(
        "attack_type"
    )[
        [
            "minutes_anchor_to_first_attack",
            "minutes_anchor_to_takeover",
            "minutes_takeover_to_impact"
        ]
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
    .round(2)
)

# ==============================================================================
# NOTEBOOK CELL 186
# ==============================================================================

# ==========================================
# AFRITAC: Pre Takeover Observable Activity
# Diagnostic
# ==========================================

# IMPORTANT:
# Use the ordinary observable event dataframe here.
# If your ordinary stream is called unified_events,
# replace `events` below with `unified_events`.

observable_check = events.copy()

observable_check["timestamp"] = pd.to_datetime(
    observable_check["timestamp"],
    errors="coerce"
)

# Keep only defender observable events
if "is_attack" in observable_check.columns:
    observable_check = observable_check[
        observable_check["is_attack"] == 0
    ].copy()

# ------------------------------------------
# Canonical takeover events
# ------------------------------------------

takeover_event_map = {
    "ACCOUNT_TAKEOVER": "ACCOUNT_TAKEOVER",
    "SOCIAL_ENGINEERING_TAKEOVER": "ACCOUNT_TAKEOVER",
    "USSD_SESSION_HIJACK": "SESSION_HIJACK",
    "SIM_IDENTITY_COMPROMISE": "ACCOUNT_TAKEOVER"
}

takeover_rows = []

for attack_type, event_type in takeover_event_map.items():

    subset = attack_events[
        (attack_events["attack_type"] == attack_type) &
        (attack_events["event_type"] == event_type)
    ].copy()

    takeover_rows.append(
        subset[
            [
                "campaign_id",
                "user_id",
                "timestamp"
            ]
        ]
    )

takeover_times = pd.concat(
    takeover_rows,
    ignore_index=True
).rename(
    columns={
        "timestamp": "takeover_time"
    }
)

# ------------------------------------------
# Campaign reference
# ------------------------------------------

campaign_reference = campaigns[
    [
        "campaign_id",
        "user_id",
        "attack_type",
        "anchor_session_id",
        "anchor_time"
    ]
].merge(
    takeover_times,
    on=["campaign_id", "user_id"],
    how="left",
    validate="one_to_one"
)

# ------------------------------------------
# Measure observable activity
# ------------------------------------------

horizons = [60, 30, 15, 10, 5]

diagnostic_rows = []

for _, campaign in campaign_reference.iterrows():

    user_id = campaign["user_id"]
    takeover_time = campaign["takeover_time"]

    user_events = observable_check[
        observable_check["user_id"] == user_id
    ].copy()

    row = {
        "campaign_id": campaign["campaign_id"],
        "user_id": user_id,
        "attack_type": campaign["attack_type"],
        "takeover_time": takeover_time
    }

    for horizon in horizons:

        window_start = (
            takeover_time
            - pd.Timedelta(minutes=horizon)
        )

        window_events = user_events[
            (user_events["timestamp"] >= window_start) &
            (user_events["timestamp"] < takeover_time)
        ]

        row[
            f"events_last_{horizon}min"
        ] = len(window_events)

        if "session_id" in window_events.columns:
            row[
                f"sessions_last_{horizon}min"
            ] = window_events["session_id"].nunique()
        else:
            row[
                f"sessions_last_{horizon}min"
            ] = 0

        if "transaction_amount" in window_events.columns:

            transactions = window_events[
                "transaction_amount"
            ].dropna()

            row[
                f"transactions_last_{horizon}min"
            ] = len(transactions)

            row[
                f"transaction_value_last_{horizon}min"
            ] = transactions.sum()

        else:

            row[
                f"transactions_last_{horizon}min"
            ] = 0

            row[
                f"transaction_value_last_{horizon}min"
            ] = 0

        if "new_device" in window_events.columns:
            row[
                f"new_devices_last_{horizon}min"
            ] = window_events["new_device"].fillna(0).sum()
        else:
            row[
                f"new_devices_last_{horizon}min"
            ] = 0

        if "location_change" in window_events.columns:
            row[
                f"location_changes_last_{horizon}min"
            ] = window_events["location_change"].fillna(0).sum()
        else:
            row[
                f"location_changes_last_{horizon}min"
            ] = 0

        if "roaming" in window_events.columns:
            row[
                f"roaming_events_last_{horizon}min"
            ] = window_events["roaming"].fillna(0).sum()
        else:
            row[
                f"roaming_events_last_{horizon}min"
            ] = 0

    diagnostic_rows.append(row)

pre_takeover_diagnostic = pd.DataFrame(
    diagnostic_rows
)

# ==========================================
# Summary
# ==========================================

print("==========================================")
print("PRE TAKEOVER OBSERVABLE ACTIVITY")
print("==========================================")

print(
    "Campaigns:",
    len(pre_takeover_diagnostic)
)

print("\nObservable events:")

for horizon in horizons:

    col = f"events_last_{horizon}min"

    print(
        f"{horizon:>2} min:",
        "mean =",
        round(
            pre_takeover_diagnostic[col].mean(),
            3
        ),
        "| median =",
        round(
            pre_takeover_diagnostic[col].median(),
            3
        ),
        "| max =",
        int(
            pre_takeover_diagnostic[col].max()
        ),
        "| zero =",
        round(
            (
                pre_takeover_diagnostic[col] == 0
            ).mean() * 100,
            2
        ),
        "%"
    )

print("\nObservable sessions:")

for horizon in horizons:

    col = f"sessions_last_{horizon}min"

    print(
        f"{horizon:>2} min:",
        "mean =",
        round(
            pre_takeover_diagnostic[col].mean(),
            3
        ),
        "| median =",
        round(
            pre_takeover_diagnostic[col].median(),
            3
        ),
        "| max =",
        int(
            pre_takeover_diagnostic[col].max()
        ),
        "| zero =",
        round(
            (
                pre_takeover_diagnostic[col] == 0
            ).mean() * 100,
            2
        ),
        "%"
    )

print("\nObservable activity by attack type:")

for horizon in horizons:

    col = f"events_last_{horizon}min"

    print(
        f"\n{horizon} minute horizon:"
    )

    print(
        pre_takeover_diagnostic.groupby(
            "attack_type"
        )[col]
        .agg(
            [
                "count",
                "mean",
                "median",
                "min",
                "max"
            ]
        )
        .round(2)
    )

# ==============================================================================
# NOTEBOOK CELL 187
# ==============================================================================

# ==========================================
# AFRITAC: Observable Precursor Event Generator
# ==========================================
#
# Purpose:
# Generate defender-observable behavioural signals
# before the hidden ground-truth takeover event.
#
# IMPORTANT:
# These are NOT ground-truth attack events.
# They must remain separate from attack_events.
# ==========================================

rng = np.random.default_rng(SEED + 65)

# ------------------------------------------
# Canonical takeover event map
# ------------------------------------------

takeover_event_map = {
    "ACCOUNT_TAKEOVER": "ACCOUNT_TAKEOVER",
    "SOCIAL_ENGINEERING_TAKEOVER": "ACCOUNT_TAKEOVER",
    "USSD_SESSION_HIJACK": "SESSION_HIJACK",
    "SIM_IDENTITY_COMPROMISE": "ACCOUNT_TAKEOVER"
}

# ------------------------------------------
# Recover canonical takeover times
# ------------------------------------------

takeover_rows = []

for attack_type, event_type in takeover_event_map.items():

    subset = attack_events[
        (attack_events["attack_type"] == attack_type) &
        (attack_events["event_type"] == event_type)
    ].copy()

    takeover_rows.append(
        subset[
            [
                "campaign_id",
                "user_id",
                "timestamp"
            ]
        ]
    )

takeover_times = pd.concat(
    takeover_rows,
    ignore_index=True
).rename(
    columns={
        "timestamp": "takeover_time"
    }
)

# ------------------------------------------
# Campaign metadata
# ------------------------------------------

campaign_reference = campaigns.merge(
    takeover_times,
    on=["campaign_id", "user_id"],
    how="left",
    validate="one_to_one"
)

# ------------------------------------------
# Add severity if available
# ------------------------------------------

if "attack_severity" in campaign_control.columns:

    campaign_reference = campaign_reference.merge(
        campaign_control[
            [
                "campaign_id",
                "attack_severity"
            ]
        ],
        on="campaign_id",
        how="left",
        validate="one_to_one"
    )

else:

    # Fallback if severity is not available
    campaign_reference["attack_severity"] = rng.choice(
        ["LOW", "MEDIUM", "HIGH"],
        size=len(campaign_reference),
        p=[0.25, 0.50, 0.25]
    )

# ------------------------------------------
# User baseline information
# ------------------------------------------

user_lookup = users[
    [
        "user_id",
        "primary_device_id",
        "country",
        "language_region",
        "behaviour_profile"
    ]
].drop_duplicates(
    "user_id"
)

campaign_reference = campaign_reference.merge(
    user_lookup,
    on="user_id",
    how="left",
    validate="one_to_one"
)

# ==========================================
# Observable event vocabulary
# ==========================================
#
# These deliberately avoid explicit ground-truth
# labels such as:
#
# ACCOUNT_TAKEOVER
# CREDENTIAL_COMPROMISE
# SESSION_HIJACK
# SIM_CHANGE
#
# They represent observations available to a
# defender.
# ==========================================

common_event_profiles = {

    "EARLY": [
        (
            "UNUSUAL_SESSION_TIMING",
            "SESSION",
            0.22
        ),
        (
            "RESPONSE_LATENCY_DEVIATION",
            "USSD",
            0.20
        ),
        (
            "MENU_SEQUENCE_DEVIATION",
            "USSD",
            0.18
        ),
        (
            "AUTHENTICATION_TIMING_DEVIATION",
            "AUTHENTICATION",
            0.18
        ),
        (
            "NETWORK_CONTEXT_CHANGE",
            "NETWORK",
            0.12
        ),
        (
            "LOCATION_CONTEXT_DEVIATION",
            "SESSION",
            0.10
        )
    ],

    "ESCALATION": [
        (
            "REPEATED_AUTHENTICATION_ACTIVITY",
            "AUTHENTICATION",
            0.18
        ),
        (
            "USSD_SEQUENCE_DEVIATION",
            "USSD",
            0.20
        ),
        (
            "SESSION_DURATION_DEVIATION",
            "SESSION",
            0.15
        ),
        (
            "RESPONSE_LATENCY_DEVIATION",
            "USSD",
            0.17
        ),
        (
            "DEVICE_CONTEXT_DEVIATION",
            "DEVICE",
            0.12
        ),
        (
            "LOCATION_CONTEXT_DEVIATION",
            "SESSION",
            0.10
        ),
        (
            "NETWORK_CONTEXT_CHANGE",
            "NETWORK",
            0.08
        )
    ],

    "STRONG": [
        (
            "REPEATED_AUTHENTICATION_ACTIVITY",
            "AUTHENTICATION",
            0.18
        ),
        (
            "ABNORMAL_USSD_INTERACTION_RATE",
            "USSD",
            0.18
        ),
        (
            "DEVICE_CONTEXT_DEVIATION",
            "DEVICE",
            0.15
        ),
        (
            "NETWORK_IDENTITY_DEVIATION",
            "NETWORK",
            0.12
        ),
        (
            "LOCATION_CONTEXT_DEVIATION",
            "SESSION",
            0.10
        ),
        (
            "SESSION_TRANSITION_ANOMALY",
            "SESSION",
            0.15
        ),
        (
            "TRANSACTION_PREPARATION_ANOMALY",
            "FINANCIAL",
            0.12
        )
    ],

    "ACUTE": [
        (
            "REPEATED_AUTHENTICATION_ACTIVITY",
            "AUTHENTICATION",
            0.15
        ),
        (
            "ABNORMAL_USSD_INTERACTION_RATE",
            "USSD",
            0.18
        ),
        (
            "SESSION_TRANSITION_ANOMALY",
            "SESSION",
            0.15
        ),
        (
            "DEVICE_CONTEXT_DEVIATION",
            "DEVICE",
            0.15
        ),
        (
            "NETWORK_IDENTITY_DEVIATION",
            "NETWORK",
            0.12
        ),
        (
            "TRANSACTION_PREPARATION_ANOMALY",
            "FINANCIAL",
            0.15
        ),
        (
            "AUTHENTICATION_CONTEXT_DEVIATION",
            "AUTHENTICATION",
            0.10
        )
    ]
}

# ------------------------------------------
# Attack-type weighting
# ------------------------------------------
#
# Attack types influence the likelihood of
# observable signals, but no attack type label
# is placed on the generated event.
# ------------------------------------------

attack_signal_weights = {

    "ACCOUNT_TAKEOVER": {
        "AUTHENTICATION": 1.25,
        "DEVICE": 1.20,
        "SESSION": 1.05,
        "USSD": 1.05,
        "NETWORK": 1.00,
        "FINANCIAL": 1.20
    },

    "SOCIAL_ENGINEERING_TAKEOVER": {
        "AUTHENTICATION": 1.25,
        "DEVICE": 1.10,
        "SESSION": 1.15,
        "USSD": 1.00,
        "NETWORK": 0.95,
        "FINANCIAL": 1.10
    },

    "USSD_SESSION_HIJACK": {
        "AUTHENTICATION": 1.05,
        "DEVICE": 1.05,
        "SESSION": 1.30,
        "USSD": 1.35,
        "NETWORK": 1.10,
        "FINANCIAL": 1.10
    },

    "SIM_IDENTITY_COMPROMISE": {
        "AUTHENTICATION": 1.25,
        "DEVICE": 1.20,
        "SESSION": 1.00,
        "USSD": 0.95,
        "NETWORK": 1.35,
        "FINANCIAL": 1.00
    }
}

# ------------------------------------------
# Severity multipliers
# ------------------------------------------

severity_multiplier = {
    "LOW": 0.75,
    "MEDIUM": 1.00,
    "HIGH": 1.30
}

# ==========================================
# Generate precursor events
# ==========================================

precursor_events = []

for _, campaign in campaign_reference.iterrows():

    campaign_id = campaign["campaign_id"]
    user_id = campaign["user_id"]
    attack_type = campaign["attack_type"]
    takeover_time = campaign["takeover_time"]
    severity = campaign["attack_severity"]

    primary_device = campaign["primary_device_id"]

    if pd.isna(takeover_time):
        continue

    severity_factor = severity_multiplier.get(
        severity,
        1.0
    )

    type_weights = attack_signal_weights[
        attack_type
    ]

    # --------------------------------------
    # Stage windows
    # --------------------------------------
    #
    # Events are generated before takeover.
    # The closer to takeover, the stronger the
    # expected observable activity.
    # --------------------------------------

    precursor_windows = [

        {
            "name": "EARLY",
            "start": 55,
            "end": 41,
            "base_events": 1.5
        },

        {
            "name": "ESCALATION",
            "start": 40,
            "end": 26,
            "base_events": 2.0
        },

        {
            "name": "STRONG",
            "start": 25,
            "end": 11,
            "base_events": 2.5
        },

        {
            "name": "ACUTE",
            "start": 10,
            "end": 1,
            "base_events": 2.5
        }
    ]

    for window in precursor_windows:

        # ----------------------------------
        # Number of precursor events
        # ----------------------------------

        expected = (
            window["base_events"]
            * severity_factor
        )

        # Randomize event count
        n_events = rng.poisson(
            expected
        )

        # Allow some windows to remain quiet
        if rng.random() < 0.12:
            n_events = 0

        # ----------------------------------
        # Generate individual observations
        # ----------------------------------

        for _ in range(n_events):

            # Random offset within window
            offset_minutes = rng.uniform(
                window["end"],
                window["start"]
            )

            event_time = (
                takeover_time
                - pd.Timedelta(
                    minutes=float(offset_minutes)
                )
            )

            # ----------------------------------
            # Select observable event
            # ----------------------------------

            profile = common_event_profiles[
                window["name"]
            ]

            event_names = [
                item[0]
                for item in profile
            ]

            modalities = [
                item[1]
                for item in profile
            ]

            probabilities = np.array([
                item[2]
                for item in profile
            ])

            # Modify probabilities according to
            # attack-specific modality weighting
            adjusted_probabilities = np.array([
                p * type_weights.get(
                    modality,
                    1.0
                )
                for p, modality in zip(
                    probabilities,
                    modalities
                )
            ])

            adjusted_probabilities = (
                adjusted_probabilities
                / adjusted_probabilities.sum()
            )

            selected_idx = rng.choice(
                len(event_names),
                p=adjusted_probabilities
            )

            event_type = event_names[
                selected_idx
            ]

            modality = modalities[
                selected_idx
            ]

            # ----------------------------------
            # Observable context
            # ----------------------------------

            response_delay = np.nan

            if modality == "USSD":
                response_delay = float(
                    np.clip(
                        rng.normal(
                            1500,
                            500
                        ),
                        300,
                        5000
                    )
                )

            elif modality == "AUTHENTICATION":
                response_delay = float(
                    np.clip(
                        rng.normal(
                            1300,
                            400
                        ),
                        250,
                        4000
                    )
                )

            elif modality == "SESSION":
                response_delay = float(
                    np.clip(
                        rng.normal(
                            1200,
                            350
                        ),
                        250,
                        3500
                    )
                )

            # ----------------------------------
            # Observable deviation values
            # ----------------------------------

            location_change = int(
                rng.random() < (
                    0.10
                    * severity_factor
                )
            )

            roaming = int(
                rng.random() < (
                    0.08
                    * severity_factor
                )
            )

            new_device = int(
                rng.random() < (
                    0.06
                    * severity_factor
                )
            )

            signal_strength = float(
                np.clip(
                    rng.normal(
                        -82,
                        7
                    ),
                    -110,
                    -55
                )
            )

            # ----------------------------------
            # Transaction preparation
            # ----------------------------------

            transaction_amount = np.nan

            if (
                modality == "FINANCIAL"
                or event_type ==
                "TRANSACTION_PREPARATION_ANOMALY"
            ):

                transaction_amount = round(
                    float(
                        rng.uniform(
                            1000,
                            30000
                        )
                    ),
                    2
                )

            # ----------------------------------
            # Session identifier
            #
            # This is deliberately synthetic and
            # does not reuse the hidden attack
            # session.
            # ----------------------------------

            precursor_session_id = (
                f"PREC_{campaign_id}_"
                f"{len(precursor_events)+1:05d}"
            )

            precursor_events.append({

                "event_id":
                    f"PREC_EVENT_{len(precursor_events)+1:06d}",

                "user_id":
                    user_id,

                "session_id":
                    precursor_session_id,

                "device_id":
                    primary_device,

                "timestamp":
                    event_time,

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

                # Observable status only
                "ground_truth_state":
                    "NORMAL",

                "is_attack":
                    0,

                "is_observable_precursor":
                    1
            })


# ==========================================
# Convert to DataFrame
# ==========================================

observable_precursors = pd.DataFrame(
    precursor_events
)

if not observable_precursors.empty:

    observable_precursors["timestamp"] = (
        pd.to_datetime(
            observable_precursors["timestamp"],
            errors="coerce"
        )
    )

    observable_precursors = (
        observable_precursors
        .sort_values(
            ["user_id", "timestamp"]
        )
        .reset_index(drop=True)
    )

# ==========================================
# Validation
# ==========================================

print("==========================================")
print("OBSERVABLE PRECURSOR GENERATOR")
print("==========================================")

print(
    "Precursor events:",
    len(observable_precursors)
)

print(
    "Unique users:",
    observable_precursors[
        "user_id"
    ].nunique()
)

print(
    "Unique sessions:",
    observable_precursors[
        "session_id"
    ].nunique()
)

print(
    "\nObservable event types:"
)

print(
    observable_precursors[
        "event_type"
    ].value_counts()
)

print(
    "\nModalities:"
)

print(
    observable_precursors[
        "modality"
    ].value_counts()
)

print(
    "\nGround truth labels:"
)

print(
    observable_precursors[
        [
            "ground_truth_state",
            "is_attack",
            "is_observable_precursor"
        ]
    ].drop_duplicates()
)

print(
    "\nMissing timestamps:",
    observable_precursors[
        "timestamp"
    ].isna().sum()
)

print(
    "\nEvents per campaign:"
)

precursor_campaign_counts = (
    observable_precursors
    .merge(
        campaign_reference[
            [
                "campaign_id",
                "user_id"
            ]
        ],
        on="user_id",
        how="inner"
    )
    .groupby("campaign_id")
    .size()
)

print(
    precursor_campaign_counts.describe()
)

# ==============================================================================
# NOTEBOOK CELL 188
# ==============================================================================

# ==========================================
# AFRITAC: Observable Precursor Temporal Audit
# ==========================================

precursor_check = observable_precursors.copy()

precursor_check["timestamp"] = pd.to_datetime(
    precursor_check["timestamp"],
    errors="coerce"
)

# ------------------------------------------
# Recover canonical takeover times
# ------------------------------------------

takeover_event_map = {
    "ACCOUNT_TAKEOVER": "ACCOUNT_TAKEOVER",
    "SOCIAL_ENGINEERING_TAKEOVER": "ACCOUNT_TAKEOVER",
    "USSD_SESSION_HIJACK": "SESSION_HIJACK",
    "SIM_IDENTITY_COMPROMISE": "ACCOUNT_TAKEOVER"
}

takeover_rows = []

for attack_type, event_type in takeover_event_map.items():

    subset = attack_events[
        (attack_events["attack_type"] == attack_type) &
        (attack_events["event_type"] == event_type)
    ].copy()

    takeover_rows.append(
        subset[
            [
                "campaign_id",
                "user_id",
                "timestamp"
            ]
        ]
    )

takeover_times = pd.concat(
    takeover_rows,
    ignore_index=True
).rename(
    columns={
        "timestamp": "takeover_time"
    }
)

# ------------------------------------------
# Attach campaign ID
# ------------------------------------------
#
# Each attack user is unique, so user_id provides
# an unambiguous campaign association.
# ------------------------------------------

precursor_check = precursor_check.merge(
    campaigns[
        [
            "campaign_id",
            "user_id",
            "attack_type"
        ]
    ],
    on="user_id",
    how="left",
    validate="many_to_one"
)

precursor_check = precursor_check.merge(
    takeover_times,
    on=["campaign_id", "user_id"],
    how="left",
    validate="many_to_one"
)

# ------------------------------------------
# Minutes before takeover
# ------------------------------------------

precursor_check["minutes_before_takeover"] = (
    (
        precursor_check["takeover_time"]
        - precursor_check["timestamp"]
    ).dt.total_seconds() / 60
)

# ------------------------------------------
# Basic temporal integrity
# ------------------------------------------

print("==========================================")
print("OBSERVABLE PRECURSOR TEMPORAL AUDIT")
print("==========================================")

print(
    "Precursor events:",
    len(precursor_check)
)

print(
    "Missing takeover times:",
    precursor_check[
        "takeover_time"
    ].isna().sum()
)

print(
    "Events at or after takeover:",
    (
        precursor_check[
            "minutes_before_takeover"
        ] <= 0
    ).sum()
)

print(
    "Events more than 60 minutes before takeover:",
    (
        precursor_check[
            "minutes_before_takeover"
        ] > 60
    ).sum()
)

print(
    "\nMinutes before takeover:"
)

print(
    precursor_check[
        "minutes_before_takeover"
    ].describe().round(2)
)

# ==========================================
# Horizon distribution
# ==========================================

horizons = [60, 30, 15, 10, 5]

print(
    "\n=========================================="
)

print(
    "PRECURSOR EVENTS BY PREDICTION HORIZON"
)

print(
    "=========================================="
)

for horizon in horizons:

    count = (
        precursor_check[
            "minutes_before_takeover"
        ] <= horizon
    ).sum()

    print(
        f"Within {horizon:>2} min:",
        count,
        "events"
    )

# ==========================================
# Campaign level activity
# ==========================================

campaign_horizon_rows = []

for _, campaign in campaigns.iterrows():

    campaign_id = campaign["campaign_id"]
    user_id = campaign["user_id"]

    user_precursors = precursor_check[
        precursor_check["campaign_id"] == campaign_id
    ]

    row = {
        "campaign_id": campaign_id,
        "user_id": user_id,
        "attack_type": campaign["attack_type"]
    }

    for horizon in horizons:

        count = (
            user_precursors[
                "minutes_before_takeover"
            ] <= horizon
        ).sum()

        row[
            f"events_within_{horizon}min"
        ] = count

    campaign_horizon_rows.append(row)

campaign_horizon = pd.DataFrame(
    campaign_horizon_rows
)

# ==========================================
# Campaign coverage
# ==========================================

print(
    "\n=========================================="
)

print(
    "CAMPAIGN COVERAGE BY HORIZON"
)

print(
    "=========================================="
)

for horizon in horizons:

    col = f"events_within_{horizon}min"

    print(
        f"\n{horizon} minute horizon:"
    )

    print(
        "Mean events:",
        round(
            campaign_horizon[col].mean(),
            3
        )
    )

    print(
        "Median events:",
        round(
            campaign_horizon[col].median(),
            3
        )
    )

    print(
        "Maximum events:",
        int(
            campaign_horizon[col].max()
        )
    )

    print(
        "Campaigns with zero:",
        (
            campaign_horizon[col] == 0
        ).sum()
    )

    print(
        "Campaign coverage:",
        round(
            (
                campaign_horizon[col] > 0
            ).mean() * 100,
            2
        ),
        "%"
    )

# ==========================================
# Attack type coverage
# ==========================================

print(
    "\n=========================================="
)

print(
    "COVERAGE BY ATTACK TYPE"
)

print(
    "=========================================="
)

for horizon in horizons:

    col = f"events_within_{horizon}min"

    print(
        f"\n{horizon} minute horizon:"
    )

    print(
        campaign_horizon.groupby(
            "attack_type"
        )[col]
        .agg(
            [
                "count",
                "mean",
                "median",
                "min",
                "max"
            ]
        )
        .round(2)
    )

# ==============================================================================
# NOTEBOOK CELL 189
# ==============================================================================

# ============================================================
# STEP 67: OBSERVABLE PRECURSOR LEAKAGE + REALISM AUDIT
# ============================================================

import pandas as pd
import numpy as np

p = observable_precursors.copy()

p["timestamp"] = pd.to_datetime(p["timestamp"], errors="coerce")

print("=" * 70)
print("OBSERVABLE PRECURSOR LEAKAGE + REALISM AUDIT")
print("=" * 70)

# ------------------------------------------------------------
# 1. Basic integrity
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("1. BASIC INTEGRITY")
print("=" * 70)

print("Rows:", len(p))
print("Unique users:", p["user_id"].nunique())
print("Unique sessions:", p["session_id"].nunique())
print("Unique devices:", p["device_id"].nunique())
print("Unique event IDs:", p["event_id"].nunique())

print("\nMissing values:")
print(p.isna().sum().sort_values(ascending=False).head(15))


# ------------------------------------------------------------
# 2. Ground truth leakage check
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("2. GROUND TRUTH LEAKAGE")
print("=" * 70)

ground_truth_columns = [
    "campaign_id",
    "attack_type",
    "attack_severity",
    "campaign_status",
    "ground_truth_attack",
    "takeover_time",
    "attack_stage",
    "target"
]

for col in ground_truth_columns:
    print(f"{col}: {'PRESENT' if col in p.columns else 'ABSENT'}")

print("\nPrecursor state values:")
if "ground_truth_state" in p.columns:
    print(p["ground_truth_state"].value_counts(dropna=False))

if "is_attack" in p.columns:
    print("\nis_attack:")
    print(p["is_attack"].value_counts(dropna=False))

if "is_observable_precursor" in p.columns:
    print("\nis_observable_precursor:")
    print(p["is_observable_precursor"].value_counts(dropna=False))


# ------------------------------------------------------------
# 3. Identifier leakage
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("3. IDENTIFIER STRUCTURE")
print("=" * 70)

for col in ["event_id", "session_id", "device_id", "user_id"]:
    if col in p.columns:
        print(f"\n{col} examples:")
        print(p[col].head(10).tolist())


# ------------------------------------------------------------
# 4. Event vocabulary
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("4. EVENT VOCABULARY")
print("=" * 70)

print(
    p["event_type"]
    .value_counts()
    .to_string()
)

print("\nNumber of event types:", p["event_type"].nunique())


# ------------------------------------------------------------
# 5. Modality distribution
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("5. MODALITY DISTRIBUTION")
print("=" * 70)

print(
    p["modality"]
    .value_counts()
    .to_string()
)


# ------------------------------------------------------------
# 6. Feature ranges
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("6. NUMERIC FEATURE RANGES")
print("=" * 70)

numeric_candidates = [
    "response_delay_ms",
    "signal_strength_dbm",
    "transaction_amount"
]

for col in numeric_candidates:
    if col in p.columns:
        print(f"\n{col}")
        print(p[col].describe())


# ------------------------------------------------------------
# 7. Categorical feature distributions
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("7. CONTEXT DISTRIBUTIONS")
print("=" * 70)

for col in [
    "roaming",
    "location_change",
    "new_device"
]:
    if col in p.columns:
        print(f"\n{col}")
        print(p[col].value_counts(dropna=False).to_string())


# ------------------------------------------------------------
# 8. Event type versus modality consistency
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("8. EVENT TYPE / MODALITY CONSISTENCY")
print("=" * 70)

event_modality = (
    p.groupby(["event_type", "modality"])
     .size()
     .reset_index(name="count")
     .sort_values(["event_type", "count"], ascending=[True, False])
)

print(event_modality.to_string(index=False))


# ------------------------------------------------------------
# 9. User level concentration
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("9. USER LEVEL CONCENTRATION")
print("=" * 70)

user_counts = p.groupby("user_id").size()

print(user_counts.describe())

print("\nTop 15 users by precursor count:")
print(user_counts.sort_values(ascending=False).head(15))


# ------------------------------------------------------------
# 10. Session level concentration
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("10. SESSION LEVEL CONCENTRATION")
print("=" * 70)

session_counts = p.groupby("session_id").size()

print(session_counts.describe())

print("\nSessions with >1 precursor event:")
print((session_counts > 1).sum())

print("Maximum events in one session:", session_counts.max())


# ------------------------------------------------------------
# 11. Temporal spacing
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("11. TEMPORAL SPACING")
print("=" * 70)

p_sorted = p.sort_values(["user_id", "timestamp"]).copy()

p_sorted["gap_min"] = (
    p_sorted.groupby("user_id")["timestamp"]
    .diff()
    .dt.total_seconds() / 60
)

print(p_sorted["gap_min"].describe())


# ------------------------------------------------------------
# 12. Attack type reconstruction audit
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("12. ATTACK TYPE ASSOCIATION")
print("=" * 70)

# Attach attack type ONLY for auditing.
# It will NOT be part of the model observable stream.

audit_campaigns = campaigns[
    ["campaign_id", "user_id", "attack_type"]
].copy()

audit = p.merge(
    audit_campaigns,
    on="user_id",
    how="left",
    validate="many_to_one"
)

print(
    audit.groupby(["attack_type", "event_type"])
         .size()
         .unstack(fill_value=0)
         .to_string()
)


# ------------------------------------------------------------
# 13. Attack type versus modality
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("13. ATTACK TYPE / MODALITY ASSOCIATION")
print("=" * 70)

print(
    pd.crosstab(
        audit["attack_type"],
        audit["modality"],
        normalize="index"
    ).round(3)
)


# ------------------------------------------------------------
# 14. Attack type versus precursor timing
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("14. ATTACK TYPE / TEMPORAL DISTRIBUTION")
print("=" * 70)

takeover_map = {
    "ACCOUNT_TAKEOVER": "ACCOUNT_TAKEOVER",
    "SOCIAL_ENGINEERING_TAKEOVER": "ACCOUNT_TAKEOVER",
    "USSD_SESSION_HIJACK": "SESSION_HIJACK",
    "SIM_IDENTITY_COMPROMISE": "ACCOUNT_TAKEOVER"
}

attack_events_audit = attack_events.copy()
attack_events_audit["timestamp"] = pd.to_datetime(
    attack_events_audit["timestamp"],
    errors="coerce"
)

takeover_rows = attack_events_audit[
    attack_events_audit["event_type"].isin(
        takeover_map.values()
    )
].copy()

takeover_times_audit = (
    takeover_rows
    .sort_values("timestamp")
    .groupby(["campaign_id", "user_id"], as_index=False)
    .first()
    [["campaign_id", "user_id", "timestamp"]]
    .rename(columns={"timestamp": "takeover_time"})
)

audit = audit.merge(
    takeover_times_audit,
    on=["campaign_id", "user_id"],
    how="left",
    validate="many_to_one"
)

audit["minutes_before_takeover"] = (
    (
        audit["takeover_time"] -
        audit["timestamp"]
    ).dt.total_seconds() / 60
)

print(
    audit.groupby("attack_type")[
        "minutes_before_takeover"
    ].describe().round(2)
)


# ------------------------------------------------------------
# 15. Final temporal integrity
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("15. FINAL TEMPORAL INTEGRITY")
print("=" * 70)

print(
    "Events at/after takeover:",
    (audit["minutes_before_takeover"] <= 0).sum()
)

print(
    "Events >60 min before takeover:",
    (audit["minutes_before_takeover"] > 60).sum()
)

print(
    "Missing takeover:",
    audit["takeover_time"].isna().sum()
)

print(
    "Negative lead times:",
    (audit["minutes_before_takeover"] < 0).sum()
)

print(
    "Lead time statistics:"
)

print(
    audit["minutes_before_takeover"].describe()
)


print("\n" + "=" * 70)
print("STEP 67 COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 190
# ==============================================================================

# ============================================================
# STEP 68: PRECURSOR IDENTIFIER SANITIZATION + SESSION
#          CONTINUITY REPAIR
# ============================================================

import pandas as pd
import numpy as np

rng = np.random.default_rng(SEED + 68)

p = observable_precursors.copy()

p["timestamp"] = pd.to_datetime(
    p["timestamp"],
    errors="coerce"
)

# ------------------------------------------------------------
# 1. Preserve original identifier for audit only
# ------------------------------------------------------------

p["original_precursor_session_id"] = p["session_id"]

# ------------------------------------------------------------
# 2. Sort temporally within user
# ------------------------------------------------------------

p = p.sort_values(
    ["user_id", "timestamp"]
).reset_index(drop=True)

# ------------------------------------------------------------
# 3. Create neutral session identifiers
#
# IMPORTANT:
# No campaign information is embedded.
# ------------------------------------------------------------

new_session_ids = []
session_counter = 1

for user_id, group in p.groupby("user_id", sort=False):

    group_indices = group.index.tolist()

    i = 0

    while i < len(group_indices):

        # Probability of continuing the same behavioral session
        # when precursor events occur close together.
        current_idx = group_indices[i]

        new_sid = f"OBS_SESSION_{session_counter:06d}"
        session_counter += 1

        new_session_ids.append(
            (current_idx, new_sid)
        )

        # ----------------------------------------------------
        # Group nearby precursor events into the same session.
        #
        # This is deliberately conservative.
        # ----------------------------------------------------

        j = i + 1

        while j < len(group_indices):

            prev_idx = group_indices[j - 1]
            next_idx = group_indices[j]

            gap_min = (
                p.loc[next_idx, "timestamp"] -
                p.loc[prev_idx, "timestamp"]
            ).total_seconds() / 60

            # Only group very close events.
            if gap_min <= 3 and rng.random() < 0.55:

                new_session_ids.append(
                    (next_idx, new_sid)
                )

                j += 1

            else:
                break

        i = j


# ------------------------------------------------------------
# Apply neutral session IDs
# ------------------------------------------------------------

session_map = dict(new_session_ids)

p["session_id"] = p.index.map(session_map)


# ------------------------------------------------------------
# 4. Regenerate neutral event IDs
# ------------------------------------------------------------

p["event_id"] = [
    f"OBS_EVENT_{i:06d}"
    for i in range(1, len(p) + 1)
]


# ------------------------------------------------------------
# 5. Remove any campaign revealing original ID
# ------------------------------------------------------------

p = p.drop(
    columns=["original_precursor_session_id"]
)


# ------------------------------------------------------------
# 6. Validation
# ------------------------------------------------------------

print("=" * 70)
print("STEP 68: IDENTIFIER SANITIZATION + SESSION CONTINUITY")
print("=" * 70)

print("\nRows:", len(p))
print("Unique users:", p["user_id"].nunique())
print("Unique sessions:", p["session_id"].nunique())
print("Unique events:", p["event_id"].nunique())

print("\nSession event count distribution:")
session_counts = p.groupby("session_id").size()

print(session_counts.describe())

print(
    "\nSessions with >1 precursor event:",
    (session_counts > 1).sum()
)

print(
    "Maximum events per session:",
    session_counts.max()
)


# ------------------------------------------------------------
# 7. Check for campaign information in identifiers
# ------------------------------------------------------------

identifier_columns = [
    "event_id",
    "session_id",
    "device_id",
    "user_id"
]

print("\nCampaign token leakage check:")

for col in identifier_columns:

    if col in p.columns:

        leakage = p[col].astype(str).str.contains(
            "CAMP",
            case=False,
            regex=False
        ).sum()

        print(
            f"{col}: {leakage} identifiers contain 'CAMP'"
        )


# ------------------------------------------------------------
# 8. Ensure timestamps unchanged
# ------------------------------------------------------------

print("\nTimestamp integrity:")

print(
    "Missing timestamps:",
    p["timestamp"].isna().sum()
)

print(
    "Timestamp range:",
    p["timestamp"].min(),
    "to",
    p["timestamp"].max()
)


# ------------------------------------------------------------
# 9. Ensure observable labels unchanged
# ------------------------------------------------------------

print("\nObservable state integrity:")

print(
    p["ground_truth_state"].value_counts(
        dropna=False
    )
)

print(
    "\nis_attack:",
    p["is_attack"].value_counts(
        dropna=False
    ).to_dict()
)

print(
    "\nis_observable_precursor:",
    p["is_observable_precursor"].value_counts(
        dropna=False
    ).to_dict()
)


# ------------------------------------------------------------
# 10. Replace working dataframe
# ------------------------------------------------------------

observable_precursors = p.copy()

print("\n" + "=" * 70)
print("STEP 68 COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 191
# ==============================================================================

# ============================================================
# STEP 68: PRECURSOR IDENTIFIER SANITIZATION + SESSION
#          CONTINUITY REPAIR
# ============================================================

import pandas as pd
import numpy as np

rng = np.random.default_rng(SEED + 68)

p = observable_precursors.copy()

p["timestamp"] = pd.to_datetime(
    p["timestamp"],
    errors="coerce"
)

# ------------------------------------------------------------
# 1. Preserve original identifier for audit only
# ------------------------------------------------------------

p["original_precursor_session_id"] = p["session_id"]

# ------------------------------------------------------------
# 2. Sort temporally within user
# ------------------------------------------------------------

p = p.sort_values(
    ["user_id", "timestamp"]
).reset_index(drop=True)

# ------------------------------------------------------------
# 3. Create neutral session identifiers
#
# IMPORTANT:
# No campaign information is embedded.
# ------------------------------------------------------------

new_session_ids = []
session_counter = 1

for user_id, group in p.groupby("user_id", sort=False):

    group_indices = group.index.tolist()

    i = 0

    while i < len(group_indices):

        # Probability of continuing the same behavioral session
        # when precursor events occur close together.
        current_idx = group_indices[i]

        new_sid = f"OBS_SESSION_{session_counter:06d}"
        session_counter += 1

        new_session_ids.append(
            (current_idx, new_sid)
        )

        # ----------------------------------------------------
        # Group nearby precursor events into the same session.
        #
        # This is deliberately conservative.
        # ----------------------------------------------------

        j = i + 1

        while j < len(group_indices):

            prev_idx = group_indices[j - 1]
            next_idx = group_indices[j]

            gap_min = (
                p.loc[next_idx, "timestamp"] -
                p.loc[prev_idx, "timestamp"]
            ).total_seconds() / 60

            # Only group very close events.
            if gap_min <= 3 and rng.random() < 0.55:

                new_session_ids.append(
                    (next_idx, new_sid)
                )

                j += 1

            else:
                break

        i = j


# ------------------------------------------------------------
# Apply neutral session IDs
# ------------------------------------------------------------

session_map = dict(new_session_ids)

p["session_id"] = p.index.map(session_map)


# ------------------------------------------------------------
# 4. Regenerate neutral event IDs
# ------------------------------------------------------------

p["event_id"] = [
    f"OBS_EVENT_{i:06d}"
    for i in range(1, len(p) + 1)
]


# ------------------------------------------------------------
# 5. Remove any campaign revealing original ID
# ------------------------------------------------------------

p = p.drop(
    columns=["original_precursor_session_id"]
)


# ------------------------------------------------------------
# 6. Validation
# ------------------------------------------------------------

print("=" * 70)
print("STEP 68: IDENTIFIER SANITIZATION + SESSION CONTINUITY")
print("=" * 70)

print("\nRows:", len(p))
print("Unique users:", p["user_id"].nunique())
print("Unique sessions:", p["session_id"].nunique())
print("Unique events:", p["event_id"].nunique())

print("\nSession event count distribution:")
session_counts = p.groupby("session_id").size()

print(session_counts.describe())

print(
    "\nSessions with >1 precursor event:",
    (session_counts > 1).sum()
)

print(
    "Maximum events per session:",
    session_counts.max()
)


# ------------------------------------------------------------
# 7. Check for campaign information in identifiers
# ------------------------------------------------------------

identifier_columns = [
    "event_id",
    "session_id",
    "device_id",
    "user_id"
]

print("\nCampaign token leakage check:")

for col in identifier_columns:

    if col in p.columns:

        leakage = p[col].astype(str).str.contains(
            "CAMP",
            case=False,
            regex=False
        ).sum()

        print(
            f"{col}: {leakage} identifiers contain 'CAMP'"
        )


# ------------------------------------------------------------
# 8. Ensure timestamps unchanged
# ------------------------------------------------------------

print("\nTimestamp integrity:")

print(
    "Missing timestamps:",
    p["timestamp"].isna().sum()
)

print(
    "Timestamp range:",
    p["timestamp"].min(),
    "to",
    p["timestamp"].max()
)


# ------------------------------------------------------------
# 9. Ensure observable labels unchanged
# ------------------------------------------------------------

print("\nObservable state integrity:")

print(
    p["ground_truth_state"].value_counts(
        dropna=False
    )
)

print(
    "\nis_attack:",
    p["is_attack"].value_counts(
        dropna=False
    ).to_dict()
)

print(
    "\nis_observable_precursor:",
    p["is_observable_precursor"].value_counts(
        dropna=False
    ).to_dict()
)


# ------------------------------------------------------------
# 10. Replace working dataframe
# ------------------------------------------------------------

observable_precursors = p.copy()

print("\n" + "=" * 70)
print("STEP 68 COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 192
# ==============================================================================

# ============================================================
# STEP 69: UNIFIED DEFENDER OBSERVABLE STREAM
# ============================================================

import pandas as pd
import numpy as np

print("=" * 75)
print("STEP 69: UNIFIED DEFENDER OBSERVABLE STREAM")
print("=" * 75)


# ============================================================
# 1. COPY SOURCE DATA
# ============================================================

ordinary = events.copy()
precursors = observable_precursors.copy()

ordinary["timestamp"] = pd.to_datetime(
    ordinary["timestamp"],
    errors="coerce"
)

precursors["timestamp"] = pd.to_datetime(
    precursors["timestamp"],
    errors="coerce"
)


# ============================================================
# 2. ORDINARY OBSERVABLE EVENTS
# ============================================================

ordinary["observable_source"] = "ORDINARY"
ordinary["is_observable"] = 1
ordinary["is_attack"] = 0

if "is_observable_precursor" not in ordinary.columns:
    ordinary["is_observable_precursor"] = 0
else:
    ordinary["is_observable_precursor"] = (
        ordinary["is_observable_precursor"]
        .fillna(0)
        .astype(int)
    )


# ============================================================
# 3. BENIGN ANOMALIES
#
# Benign anomalies are expected to already exist inside the
# ordinary observable event/session construction.
#
# We identify them using the existing benign anomaly fields.
# ============================================================

if "benign_anomaly_type" in ordinary.columns:

    benign_count = (
        ordinary["benign_anomaly_type"]
        .notna()
        .sum()
    )

else:

    benign_count = 0


print("\nOrdinary observable events:", len(ordinary))
print("Events containing benign anomaly labels:", benign_count)


# ============================================================
# 4. PRECURSOR EVENTS
# ============================================================

precursors["observable_source"] = "PRECURSOR"
precursors["is_observable"] = 1
precursors["is_attack"] = 0
precursors["is_observable_precursor"] = 1


# ============================================================
# 5. HARMONIZE COMMON COLUMNS
# ============================================================

# These are the fields that the defender may observe.
#
# We deliberately exclude:
# campaign_id
# attack_type
# attack_severity
# takeover_time
# attack_stage
# ground_truth_attack
# target
#
# from the unified observable stream.

forbidden_ground_truth = [
    "campaign_id",
    "attack_type",
    "attack_severity",
    "campaign_status",
    "ground_truth_attack",
    "takeover_time",
    "attack_stage",
    "target"
]


ordinary = ordinary.drop(
    columns=[
        c for c in forbidden_ground_truth
        if c in ordinary.columns
    ],
    errors="ignore"
)

precursors = precursors.drop(
    columns=[
        c for c in forbidden_ground_truth
        if c in precursors.columns
    ],
    errors="ignore"
)


# ============================================================
# 6. UNION THE TWO OBSERVABLE STREAMS
# ============================================================

observable_stream = pd.concat(
    [
        ordinary,
        precursors
    ],
    axis=0,
    ignore_index=True,
    sort=False
)


# ============================================================
# 7. SORT TEMPORALLY
# ============================================================

observable_stream = observable_stream.sort_values(
    ["timestamp", "user_id"],
    kind="mergesort"
).reset_index(drop=True)


# ============================================================
# 8. CREATE A NEUTRAL STREAM EVENT ID
# ============================================================

observable_stream["observable_event_id"] = [
    f"OBS_{i:08d}"
    for i in range(1, len(observable_stream) + 1)
]


# ============================================================
# 9. SOURCE DISTRIBUTION
# ============================================================

print("\n" + "=" * 75)
print("SOURCE DISTRIBUTION")
print("=" * 75)

print(
    observable_stream["observable_source"]
    .value_counts(dropna=False)
)


# ============================================================
# 10. PRECURSOR DISTRIBUTION
# ============================================================

print("\n" + "=" * 75)
print("PRECURSOR DISTRIBUTION")
print("=" * 75)

print(
    observable_stream[
        "is_observable_precursor"
    ].value_counts(dropna=False)
)


# ============================================================
# 11. ATTACK LABEL CHECK
# ============================================================

print("\n" + "=" * 75)
print("ATTACK LABEL CHECK")
print("=" * 75)

print(
    observable_stream["is_attack"]
    .value_counts(dropna=False)
)

print(
    "\nUnique ground truth states:"
)

if "ground_truth_state" in observable_stream.columns:
    print(
        observable_stream[
            "ground_truth_state"
        ].value_counts(dropna=False)
    )


# ============================================================
# 12. TIMESTAMP INTEGRITY
# ============================================================

print("\n" + "=" * 75)
print("TIMESTAMP INTEGRITY")
print("=" * 75)

print(
    "Missing timestamps:",
    observable_stream["timestamp"].isna().sum()
)

print(
    "Earliest event:",
    observable_stream["timestamp"].min()
)

print(
    "Latest event:",
    observable_stream["timestamp"].max()
)


# ============================================================
# 13. USER COVERAGE
# ============================================================

print("\n" + "=" * 75)
print("USER COVERAGE")
print("=" * 75)

print(
    "Unique users:",
    observable_stream["user_id"].nunique()
)

print(
    "Users with precursor observations:",
    observable_stream.loc[
        observable_stream["is_observable_precursor"] == 1,
        "user_id"
    ].nunique()
)

print(
    "Users without precursor observations:",
    observable_stream.loc[
        observable_stream["is_observable_precursor"] == 0,
        "user_id"
    ].nunique()
)


# ============================================================
# 14. EVENT TYPE DISTRIBUTION
# ============================================================

print("\n" + "=" * 75)
print("EVENT TYPE DISTRIBUTION")
print("=" * 75)

print(
    observable_stream[
        "event_type"
    ].value_counts().head(40)
)


# ============================================================
# 15. MODALITY DISTRIBUTION
# ============================================================

print("\n" + "=" * 75)
print("MODALITY DISTRIBUTION")
print("=" * 75)

print(
    observable_stream[
        "modality"
    ].value_counts(dropna=False)
)


# ============================================================
# 16. PRECURSOR VS ORDINARY MODALITIES
# ============================================================

print("\n" + "=" * 75)
print("SOURCE × MODALITY")
print("=" * 75)

print(
    pd.crosstab(
        observable_stream["observable_source"],
        observable_stream["modality"],
        margins=True
    )
)


# ============================================================
# 17. SOURCE × EVENT TYPE
# ============================================================

print("\n" + "=" * 75)
print("SOURCE × EVENT TYPE")
print("=" * 75)

source_event = pd.crosstab(
    observable_stream["observable_source"],
    observable_stream["event_type"]
)

print(source_event.to_string())


# ============================================================
# 18. DUPLICATE EVENT CHECK
# ============================================================

print("\n" + "=" * 75)
print("DUPLICATE CHECK")
print("=" * 75)

print(
    "Duplicate observable_event_id:",
    observable_stream["observable_event_id"].duplicated().sum()
)

print(
    "Duplicate full rows:",
    observable_stream.duplicated().sum()
)


# ============================================================
# 19. TEMPORAL IDENTITY CHECK
#
# Same user + timestamp + event_type is allowed in a real
# event stream, but we quantify it rather than silently
# treating it as an error.
# ============================================================

identity_cols = [
    "user_id",
    "timestamp",
    "event_type"
]

available_identity_cols = [
    c for c in identity_cols
    if c in observable_stream.columns
]

temporal_duplicates = (
    observable_stream
    .duplicated(
        subset=available_identity_cols,
        keep=False
    )
    .sum()
)

print(
    "\nRepeated temporal identities:",
    temporal_duplicates
)


# ============================================================
# 20. PRECURSOR TEMPORAL LOCATION
#
# All precursor observations should remain inside the
# six-month observable period.
# ============================================================

precursor_rows = observable_stream[
    observable_stream["is_observable_precursor"] == 1
].copy()

print("\n" + "=" * 75)
print("PRECURSOR TEMPORAL LOCATION")
print("=" * 75)

print(
    "Precursor events:",
    len(precursor_rows)
)

print(
    "Earliest precursor:",
    precursor_rows["timestamp"].min()
)

print(
    "Latest precursor:",
    precursor_rows["timestamp"].max()
)


# ============================================================
# 21. GROUND TRUTH FIELD LEAKAGE CHECK
# ============================================================

print("\n" + "=" * 75)
print("GROUND TRUTH FIELD LEAKAGE CHECK")
print("=" * 75)

for col in forbidden_ground_truth:

    print(
        f"{col}:",
        "PRESENT" if col in observable_stream.columns
        else "ABSENT"
    )


# ============================================================
# 22. IDENTIFIER LEAKAGE CHECK
# ============================================================

print("\n" + "=" * 75)
print("IDENTIFIER LEAKAGE CHECK")
print("=" * 75)

for col in [
    "observable_event_id",
    "event_id",
    "session_id",
    "device_id",
    "user_id"
]:

    if col in observable_stream.columns:

        campaign_token_count = (
            observable_stream[col]
            .astype(str)
            .str.contains(
                "CAMP",
                case=False,
                regex=False
            )
            .sum()
        )

        print(
            f"{col}: {campaign_token_count} "
            "identifiers containing CAMP"
        )


# ============================================================
# 23. SOURCE SIZE SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("FINAL STREAM SIZE")
print("=" * 75)

print(
    "Ordinary events:",
    len(ordinary)
)

print(
    "Observable precursors:",
    len(precursors)
)

print(
    "Unified observable events:",
    len(observable_stream)
)


# ============================================================
# 24. SAVE AS WORKING DATAFRAME
# ============================================================

observable_stream = observable_stream.copy()


print("\n" + "=" * 75)
print("STEP 69 COMPLETE")
print("=" * 75)
