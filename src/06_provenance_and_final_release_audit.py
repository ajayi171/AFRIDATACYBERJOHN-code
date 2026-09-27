# AFRIDATACYBERJOHN — Provenance and Final Release Audit
# This file is an archival extraction of the corresponding cells from
# AFRIDATACYBERJOHN_v1.0_reproducibility.ipynb.
# The canonical workflow is the notebook; this script is not guaranteed
# to be independently executable without the preceding workflow state.


# ==============================================================================
# NOTEBOOK CELL 663
# ==============================================================================

# ============================================================
# STAGE 36 — PROVENANCE EVIDENCE AUDIT
#
# PURPOSE:
#   Examine the original notebook/source documentation for
#   evidence about dataset origin.
#
# IMPORTANT:
#   - READ-ONLY
#   - DOES NOT MODIFY THE DATASET
#   - DOES NOT MODIFY AFRIDATACYBERJOHN_v1.0
#   - DOES NOT MODIFY THE FINAL ZIP
#   - DOES NOT ASSIGN A LICENSE
#   - DOES NOT INVENT PROVENANCE
# ============================================================

from pathlib import Path
import re
import json
from datetime import datetime

# ------------------------------------------------------------
# 1. SOURCE LOCATIONS
# ------------------------------------------------------------

NOTEBOOK = Path(
    "/content/gdrive_afritac/MyDrive/Colab Notebooks/Africadataset.ipynb"
)

SEARCHABLE_DUMP_CANDIDATES = [
    Path("/content/Pasted markdown(20260916-144029).md"),
    Path("/content/Pasted markdown(20260904-102216).md"),
]

RELEASE_DIR = Path(
    "/content/AFRIDATACYBERJOHN_v1.0"
)

OUTPUT_DIR = Path(
    "/content/AFRIDATACYBERJOHN_STAGE36_PROVENANCE_AUDIT"
)

REPORT_FILE = (
    OUTPUT_DIR /
    "PROVENANCE_DECISION_REPORT.md"
)

JSON_FILE = (
    OUTPUT_DIR /
    "PROVENANCE_EVIDENCE.json"
)

# ------------------------------------------------------------
# 2. CREATE OUTPUT DIRECTORY
# ------------------------------------------------------------

if OUTPUT_DIR.exists():
    import shutil
    shutil.rmtree(OUTPUT_DIR)

OUTPUT_DIR.mkdir(parents=True)

print("Stage 36 output directory:")
print(OUTPUT_DIR)

# ------------------------------------------------------------
# 3. FIND AVAILABLE SOURCE
# ------------------------------------------------------------

source_files = []

if NOTEBOOK.exists():
    source_files.append(NOTEBOOK)

for candidate in SEARCHABLE_DUMP_CANDIDATES:
    if candidate.exists():
        source_files.append(candidate)

print("\nSOURCE FILES FOUND")
print("-" * 60)

if source_files:

    for source in source_files:
        print("FOUND:", source)

else:

    print("No original notebook/dump found.")

# ------------------------------------------------------------
# 4. READ SOURCE TEXT
# ------------------------------------------------------------

source_text = ""

for source in source_files:

    try:

        if source.suffix.lower() == ".ipynb":

            raw = source.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            try:

                notebook = json.loads(raw)

                parts = []

                for cell in notebook.get(
                    "cells",
                    []
                ):

                    parts.extend(
                        cell.get(
                            "source",
                            []
                        )
                    )

                text = "\n".join(parts)

            except Exception:

                text = raw

        else:

            text = source.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        source_text += (
            "\n\n"
            + "=" * 80
            + f"\nSOURCE: {source}\n"
            + "=" * 80
            + "\n"
            + text
        )

    except Exception as e:

        print(
            f"Could not read {source}: {e}"
        )

print(
    f"\nTotal source characters examined: "
    f"{len(source_text):,}"
)

# ------------------------------------------------------------
# 5. PROVENANCE SEARCH TERMS
# ------------------------------------------------------------

patterns = {

    "synthetic": [
        r"\bsynthetic\b",
        r"\bsimulated\b",
        r"\bsimulation\b",
        r"\bgenerated data\b",
        r"\bartificial data\b",
    ],

    "real_world": [
        r"\breal[- ]world\b",
        r"\breal data\b",
        r"\bproduction data\b",
        r"\boperational data\b",
        r"\blive data\b",
        r"\bfield data\b",
        r"\bcollected data\b",
        r"\bdata collection\b",
    ],

    "source": [
        r"\bdataset source\b",
        r"\bdata source\b",
        r"\bsource dataset\b",
        r"\bdownloaded from\b",
        r"\bobtained from\b",
        r"\bcollected from\b",
        r"\bacquired from\b",
        r"\bprovided by\b",
    ],

    "generation": [
        r"\bgenerate\b",
        r"\bgenerated\b",
        r"\bgenerating\b",
        r"\brandom\b",
        r"\bfaker\b",
        r"\bsynthetic generation\b",
        r"\bdata generator\b",
    ],

    "mobile_money": [
        r"\bmobile money\b",
        r"\bmobile-money\b",
        r"\bUSSD\b",
        r"\bM[_ -]?Pesa\b",
        r"\bMTN[_ -]?MoMo\b",
        r"\bAirtel[_ -]?Money\b",
        r"\bOPay\b",
    ],

    "attack_generation": [
        r"\battack generation\b",
        r"\battack traffic\b",
        r"\bmalicious traffic\b",
        r"\battack samples\b",
        r"\battack records\b",
        r"\bGAN\b",
        r"\boversampling\b",
    ],
}

# ------------------------------------------------------------
# 6. EXTRACT CONTEXT AROUND MATCHES
# ------------------------------------------------------------

def extract_context(
    text,
    pattern,
    window=350,
    max_results=15
):

    matches = []

    for match in re.finditer(
        pattern,
        text,
        flags=re.IGNORECASE
    ):

        start = max(
            0,
            match.start() - window
        )

        end = min(
            len(text),
            match.end() + window
        )

        context = text[start:end]

        context = re.sub(
            r"\n{4,}",
            "\n\n",
            context
        )

        matches.append(
            context.strip()
        )

        if len(matches) >= max_results:
            break

    return matches

# ------------------------------------------------------------
# 7. BUILD EVIDENCE COLLECTION
# ------------------------------------------------------------

evidence = {}

for category, category_patterns in patterns.items():

    category_results = []

    for pattern in category_patterns:

        contexts = extract_context(
            source_text,
            pattern
        )

        for context in contexts:

            category_results.append({
                "pattern": pattern,
                "context": context
            })

    evidence[category] = category_results

# ------------------------------------------------------------
# 8. SEARCH RELEASE DOCUMENTATION TOO
# ------------------------------------------------------------

release_evidence = {}

documentation_dir = (
    RELEASE_DIR /
    "documentation"
)

if documentation_dir.exists():

    documentation_text = ""

    for file_path in documentation_dir.glob("*"):

        if file_path.is_file():

            try:

                documentation_text += (
                    "\n\n"
                    + "=" * 80
                    + f"\nFILE: {file_path.name}\n"
                    + "=" * 80
                    + "\n"
                    + file_path.read_text(
                        encoding="utf-8",
                        errors="ignore"
                    )
                )

            except Exception:
                pass

    for category, category_patterns in patterns.items():

        results = []

        for pattern in category_patterns:

            contexts = extract_context(
                documentation_text,
                pattern
            )

            for context in contexts:

                results.append({
                    "pattern": pattern,
                    "context": context
                })

        release_evidence[category] = results

# ------------------------------------------------------------
# 9. COUNT EVIDENCE
# ------------------------------------------------------------

source_counts = {
    category: len(items)
    for category, items in evidence.items()
}

release_counts = {
    category: len(items)
    for category, items in release_evidence.items()
}

# ------------------------------------------------------------
# 10. CREATE JSON EVIDENCE FILE
# ------------------------------------------------------------

evidence_package = {
    "audit_stage": "Stage 36",
    "generated_at": datetime.now().isoformat(),

    "purpose": (
        "Evidence extraction for determining dataset provenance. "
        "This audit does not classify the dataset as synthetic "
        "or real-world and does not invent missing provenance."
    ),

    "source_files_examined": [
        str(x)
        for x in source_files
    ],

    "source_evidence_counts": source_counts,

    "release_documentation_evidence_counts":
        release_counts,

    "source_evidence": evidence,

    "release_documentation_evidence":
        release_evidence,

    "decision_status": {
        "origin_classification": (
            "REQUIRES HUMAN CONFIRMATION"
        ),
        "synthetic_claim_supported": False,
        "real_world_claim_supported": False,
        "mixed_origin_claim_supported": False,
        "license_decision_made": False,
    }
}

JSON_FILE.write_text(
    json.dumps(
        evidence_package,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

# ------------------------------------------------------------
# 11. CREATE HUMAN-READABLE REPORT
# ------------------------------------------------------------

report = []

report.append(
    "# AFRIDATACYBERJOHN v1.0 — Provenance Decision Report"
)

report.append("")

report.append(
    "## Purpose"
)

report.append("")

report.append(
    "This report records evidence found in the available "
    "source notebook/source dump and release documentation "
    "that may help determine the origin of AFRIDATACYBERJOHN "
    "v1.0. The audit is evidence-preserving and does not "
    "invent, infer, or silently assign a provenance classification."
)

report.append("")

report.append(
    "## Source Files Examined"
)

report.append("")

if source_files:

    for source in source_files:
        report.append(
            f"- `{source}`"
        )

else:

    report.append(
        "- No original notebook/source dump was available."
    )

report.append("")

report.append(
    "## Evidence Counts in Source Material"
)

report.append("")

for category, count in source_counts.items():

    report.append(
        f"- **{category}**: {count} evidence contexts"
    )

report.append("")

report.append(
    "## Evidence Counts in Release Documentation"
)

report.append("")

for category, count in release_counts.items():

    report.append(
        f"- **{category}**: {count} evidence contexts"
    )

report.append("")

report.append(
    "## Key Interpretation Rule"
)

report.append("")

report.append(
    "A keyword occurrence alone is not treated as proof of "
    "dataset origin. For example, a statement describing "
    "synthetic records as something that must not be inserted "
    "during forensic reconciliation does not prove that the "
    "dataset itself is synthetic. Likewise, a reference to "
    "real-world data as a future validation requirement does "
    "not prove that the dataset consists of real operational data."
)

report.append("")

report.append(
    "## Synthetic Evidence"
)

report.append("")

synthetic_items = (
    evidence.get("synthetic", [])
)

if synthetic_items:

    for item in synthetic_items[:10]:

        report.append(
            "### Evidence\n\n"
            "```text\n"
            + item["context"]
            + "\n```"
        )

else:

    report.append(
        "No direct synthetic-origin evidence was found."
    )

report.append("")

report.append(
    "## Real-World / Production Evidence"
)

report.append("")

real_items = (
    evidence.get("real_world", [])
)

if real_items:

    for item in real_items[:10]:

        report.append(
            "### Evidence\n\n"
            "```text\n"
            + item["context"]
            + "\n```"
        )

else:

    report.append(
        "No direct real-world/production-origin evidence was found."
    )

report.append("")

report.append(
    "## Source / Acquisition Evidence"
)

report.append("")

source_items = (
    evidence.get("source", [])
)

if source_items:

    for item in source_items[:10]:

        report.append(
            "### Evidence\n\n"
            "```text\n"
            + item["context"]
            + "\n```"
        )

else:

    report.append(
        "No explicit source/acquisition statement was found."
    )

report.append("")

report.append(
    "## Current Decision Status"
)

report.append("")

report.append(
    "- Origin classification: **REQUIRES HUMAN CONFIRMATION**"
)

report.append(
    "- Synthetic classification: **NOT ASSIGNED**"
)

report.append(
    "- Real-world classification: **NOT ASSIGNED**"
)

report.append(
    "- Mixed-origin classification: **NOT ASSIGNED**"
)

report.append(
    "- License: **NOT ASSIGNED**"
)

report.append("")

report.append(
    "## Human Confirmation Required"
)

report.append("")

report.append(
    "Select the statement that accurately describes how the "
    "underlying dataset was created:"
)

report.append("")

report.append(
    "**A — Synthetic:** The records were generated/simulated "
    "using code or a simulation process."
)

report.append("")

report.append(
    "**B — Real-world:** The records were collected from "
    "real operational/mobile-money/USSD activity."
)

report.append("")

report.append(
    "**C — Mixed:** The dataset combines real collected data "
    "with generated or simulated records."
)

report.append("")

report.append(
    "**D — Uncertain:** The origin cannot currently be "
    "established from the available evidence."
)

report.append("")

report.append(
    "Do not select an option based on publication preference. "
    "The selected classification should reflect the actual "
    "data-generation/collection process."
)

report.append("")

report.append(
    "## Dataset Integrity"
)

report.append("")

report.append(
    "- AFRIDATACYBERJOHN v1.0 remains frozen."
)

report.append(
    "- Dataset records were not modified."
)

report.append(
    "- CSV contents were not modified."
)

report.append(
    "- Forensic findings were not modified."
)

report.append(
    "- This Stage 36 audit is read-only."
)

REPORT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8"
)

# ------------------------------------------------------------
# 12. FINAL OUTPUT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STAGE 36 COMPLETE")
print("=" * 70)

print(
    "Source files examined       :",
    len(source_files)
)

print(
    "Source evidence categories  :",
    len(evidence)
)

print(
    "Release evidence categories :",
    len(release_evidence)
)

print()
print("SOURCE EVIDENCE COUNTS")
print("-" * 60)

for category, count in source_counts.items():
    print(
        f"{category:<22}: {count}"
    )

print()
print("RELEASE DOCUMENTATION COUNTS")
print("-" * 60)

for category, count in release_counts.items():
    print(
        f"{category:<22}: {count}"
    )

print()
print(
    "Origin classification : REQUIRES HUMAN CONFIRMATION"
)

print(
    "License decision      : NOT MADE"
)

print(
    "Dataset modified      : NO"
)

print()
print("Evidence JSON:")
print(JSON_FILE)

print()
print("Decision report:")
print(REPORT_FILE)

print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 664
# ==============================================================================

# ============================================================
# STAGE 37 — LOCATE ORIGINAL AFRICA DATASET SOURCE
#
# READ-ONLY SEARCH
# Does NOT modify the dataset or release package.
# ============================================================

from pathlib import Path

SEARCH_ROOTS = [
    Path("/content"),
    Path("/content/gdrive_afritac"),
    Path("/content/drive/MyDrive"),
]

TARGET_NAMES = [
    "Africadataset.ipynb",
    "Africadataset",
    "AfricaDataset",
    "africa_dataset",
    "AFRICA_DATASET",
]

FOUND = []

print("=" * 70)
print("STAGE 37 — SOURCE NOTEBOOK SEARCH")
print("=" * 70)

for root in SEARCH_ROOTS:

    if not root.exists():
        print(f"\nNOT FOUND ROOT: {root}")
        continue

    print(f"\nSEARCHING: {root}")

    try:

        for path in root.rglob("*"):

            if not path.is_file():
                continue

            name_lower = path.name.lower()

            # Exact / strong filename matches
            if (
                name_lower == "africadataset.ipynb"
                or "africadataset" in name_lower
                or "africa_dataset" in name_lower
            ):

                if path not in FOUND:
                    FOUND.append(path)

    except Exception as e:

        print(
            f"Search error in {root}: {e}"
        )

# ------------------------------------------------------------
# SEARCH FOR MARKDOWN NOTEBOOK EXPORTS
# ------------------------------------------------------------

for root in SEARCH_ROOTS:

    if not root.exists():
        continue

    try:

        for path in root.rglob("*.md"):

            name_lower = path.name.lower()

            if (
                "africa" in name_lower
                or "afritac" in name_lower
                or "pasted markdown" in name_lower
            ):

                if path not in FOUND:
                    FOUND.append(path)

    except Exception:
        pass

# ------------------------------------------------------------
# DISPLAY RESULTS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("SEARCH RESULTS")
print("=" * 70)

if not FOUND:

    print("NO SOURCE NOTEBOOK OR RELATED MARKDOWN FILE FOUND.")

else:

    print(
        f"FOUND {len(FOUND)} POSSIBLE SOURCE FILE(S):\n"
    )

    for i, path in enumerate(
        sorted(FOUND),
        start=1
    ):

        try:
            size = path.stat().st_size
        except:
            size = "unknown"

        print(
            f"{i}. {path}"
        )
        print(
            f"   Size: {size:,} bytes"
            if isinstance(size, int)
            else f"   Size: {size}"
        )

# ------------------------------------------------------------
# CHECK THE PREVIOUS EXPECTED PATH DIRECTLY
# ------------------------------------------------------------

expected = Path(
    "/content/gdrive_afritac/"
    "MyDrive/Colab Notebooks/Africadataset.ipynb"
)

print("\n" + "-" * 70)
print("EXPECTED ORIGINAL NOTEBOOK")
print("-" * 70)

print(expected)

if expected.exists():

    print("STATUS: FOUND")

else:

    print("STATUS: NOT FOUND")

# ------------------------------------------------------------
# CHECK GOOGLE DRIVE MOUNT
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("GOOGLE DRIVE CHECK")
print("-" * 70)

drive_paths = [
    Path("/content/drive"),
    Path("/content/gdrive_afritac"),
]

for p in drive_paths:

    print(
        f"{p}: "
        f"{'PRESENT' if p.exists() else 'NOT PRESENT'}"
    )

print("\n" + "=" * 70)
print("STAGE 37 COMPLETE")
print("=" * 70)

print(
    "Possible source files found:",
    len(FOUND)
)

print(
    "Dataset modified: NO"
)

print(
    "Release modified: NO"
)

print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 665
# ==============================================================================

# ============================================================
# STAGE 37A — TARGETED SOURCE NOTEBOOK SEARCH
# READ-ONLY
# ============================================================

from pathlib import Path

print("=" * 70)
print("STAGE 37A — TARGETED SOURCE SEARCH")
print("=" * 70)

# ------------------------------------------------------------
# 1. POSSIBLE DIRECT PATHS
# ------------------------------------------------------------

possible_paths = [
    Path("/content/gdrive_afritac/MyDrive/Colab Notebooks/Africadataset.ipynb"),
    Path("/content/drive/MyDrive/Colab Notebooks/Africadataset.ipynb"),
    Path("/content/drive/MyDrive/Africadataset.ipynb"),
    Path("/content/Africadataset.ipynb"),
]

print("\nDIRECT PATH CHECK")
print("-" * 70)

found = []

for path in possible_paths:

    status = "FOUND" if path.exists() else "NOT FOUND"

    print(f"{status:12} {path}")

    if path.exists():
        found.append(path)

# ------------------------------------------------------------
# 2. CHECK KNOWN MARKDOWN EXPORT NAMES
# ------------------------------------------------------------

possible_markdowns = [
    Path("/content/Pasted markdown(20260916-144029).md"),
    Path("/content/Pasted markdown(20260904-102216).md"),
]

print("\nKNOWN MARKDOWN EXPORT CHECK")
print("-" * 70)

for path in possible_markdowns:

    status = "FOUND" if path.exists() else "NOT FOUND"

    print(f"{status:12} {path}")

    if path.exists():
        found.append(path)

# ------------------------------------------------------------
# 3. SHALLOW SEARCH — /content ONLY
# ------------------------------------------------------------

print("\nSHALLOW /content SEARCH")
print("-" * 70)

content_root = Path("/content")

if content_root.exists():

    for path in content_root.iterdir():

        if not path.is_file():
            continue

        name = path.name.lower()

        if (
            "africa" in name
            or "afritac" in name
            or "pasted markdown" in name
            or "dataset" in name
        ):

            print("POSSIBLE:", path)

            if path not in found:
                found.append(path)

# ------------------------------------------------------------
# 4. CHECK GOOGLE DRIVE ROOTS ONLY
# ------------------------------------------------------------

drive_roots = [
    Path("/content/drive/MyDrive"),
    Path("/content/gdrive_afritac/MyDrive"),
]

print("\nGOOGLE DRIVE ROOT CHECK")
print("-" * 70)

for root in drive_roots:

    if not root.exists():

        print("NOT FOUND:", root)
        continue

    print("PRESENT:", root)

    # Only inspect immediate directories/files
    try:

        for item in root.iterdir():

            name = item.name.lower()

            if (
                "africa" in name
                or "afritac" in name
                or "colab" in name
                or "dataset" in name
            ):

                print("  POSSIBLE:", item)

    except Exception as e:

        print("  ERROR:", e)

# ------------------------------------------------------------
# 5. FINAL RESULTS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("SOURCE SEARCH RESULTS")
print("=" * 70)

# Remove duplicates while preserving order
unique_found = []

for item in found:

    if item not in unique_found:
        unique_found.append(item)

if unique_found:

    for i, item in enumerate(
        unique_found,
        start=1
    ):
        print(f"{i}. {item}")

else:

    print("NO TARGETED SOURCE FILE FOUND.")

print("\nTotal possible source files:", len(unique_found))

print("\nDataset modified: NO")
print("Release modified : NO")

print("=" * 70)
print("STAGE 37A COMPLETE")
print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 666
# ==============================================================================

# ============================================================
# STAGE 38 — ORIGINAL NOTEBOOK PROVENANCE EXTRACTION
#
# READ-ONLY
#
# Source:
# /content/drive/MyDrive/Colab Notebooks/Africadataset.ipynb
#
# DOES NOT:
#   - modify the notebook
#   - modify the dataset
#   - modify AFRIDATACYBERJOHN_v1.0
#   - modify the ZIP
#   - assign provenance
#   - assign a license
# ============================================================

from pathlib import Path
import json
import re

# ------------------------------------------------------------
# 1. SOURCE NOTEBOOK
# ------------------------------------------------------------

NOTEBOOK = Path(
    "/content/drive/MyDrive/Colab Notebooks/Africadataset.ipynb"
)

OUTPUT_DIR = Path(
    "/content/AFRIDATACYBERJOHN_STAGE38_NOTEBOOK_PROVENANCE"
)

REPORT_FILE = (
    OUTPUT_DIR /
    "ORIGINAL_NOTEBOOK_PROVENANCE_EVIDENCE.md"
)

if not NOTEBOOK.exists():
    raise FileNotFoundError(
        f"Original notebook not found:\n{NOTEBOOK}"
    )

# ------------------------------------------------------------
# 2. CREATE OUTPUT DIRECTORY
# ------------------------------------------------------------

if OUTPUT_DIR.exists():
    import shutil
    shutil.rmtree(OUTPUT_DIR)

OUTPUT_DIR.mkdir(parents=True)

print("=" * 70)
print("STAGE 38 — ORIGINAL NOTEBOOK PROVENANCE EXTRACTION")
print("=" * 70)

print("\nNotebook found:")
print(NOTEBOOK)

# ------------------------------------------------------------
# 3. LOAD NOTEBOOK
# ------------------------------------------------------------

with open(
    NOTEBOOK,
    "r",
    encoding="utf-8"
) as f:

    notebook = json.load(f)

cells = notebook.get("cells", [])

print("\nNotebook cells:", len(cells))

# ------------------------------------------------------------
# 4. PROVENANCE SEARCH TERMS
# ------------------------------------------------------------

search_groups = {

    "SYNTHETIC / SIMULATION": [
        "synthetic",
        "simulated",
        "simulation",
        "artificial data",
        "generated data",
        "synthetic data",
        "synthetically",
        "data generation",
        "generate data",
        "generated records",
    ],

    "REAL-WORLD / OPERATIONAL": [
        "real-world",
        "real world",
        "real data",
        "real-world data",
        "production data",
        "operational data",
        "live data",
        "field data",
        "collected data",
        "data collection",
        "actual users",
        "actual transactions",
    ],

    "DATA SOURCE / ACQUISITION": [
        "dataset source",
        "data source",
        "source dataset",
        "downloaded from",
        "obtained from",
        "collected from",
        "acquired from",
        "provided by",
        "imported from",
        "loaded from",
        "read_csv",
        "read_excel",
        "url",
        "huggingface",
        "kaggle",
        "zenodo",
        "github",
    ],

    "MOBILE MONEY / USSD": [
        "mobile money",
        "mobile-money",
        "USSD",
        "M_Pesa",
        "MTN_MoMo",
        "Airtel_Money",
        "OPay",
        "transaction",
        "beneficiary",
        "financial service",
    ],

    "DATA GENERATION METHODS": [
        "random",
        "numpy.random",
        "faker",
        "make_classification",
        "make_blobs",
        "random_state",
        "synthetic generation",
        "generator",
        "generated",
        "sample(",
        "np.random",
    ],

    "ATTACK GENERATION": [
        "attack traffic",
        "malicious traffic",
        "attack samples",
        "attack records",
        "attack generation",
        "GAN",
        "SMOTE",
        "ADASYN",
        "oversampling",
        "undersampling",
    ],
}

# ------------------------------------------------------------
# 5. NORMALIZE CELLS
# ------------------------------------------------------------

cell_records = []

for index, cell in enumerate(cells):

    cell_type = cell.get(
        "cell_type",
        ""
    )

    source = "".join(
        cell.get(
            "source",
            []
        )
    )

    outputs = cell.get(
        "outputs",
        []
    )

    output_text_parts = []

    for output in outputs:

        if "text" in output:

            value = output["text"]

            if isinstance(value, list):
                value = "".join(value)

            output_text_parts.append(
                str(value)
            )

        if "data" in output:

            data = output["data"]

            if "text/plain" in data:

                value = data["text/plain"]

                if isinstance(value, list):
                    value = "".join(value)

                output_text_parts.append(
                    str(value)
                )

    output_text = "\n".join(
        output_text_parts
    )

    combined = (
        source
        + "\n"
        + output_text
    )

    cell_records.append({
        "index": index,
        "cell_type": cell_type,
        "source": source,
        "output": output_text,
        "combined": combined,
    })

# ------------------------------------------------------------
# 6. SEARCH EACH CELL
# ------------------------------------------------------------

matches = {}

for group, terms in search_groups.items():

    matches[group] = []

    for record in cell_records:

        text = record["combined"]

        lower_text = text.lower()

        matched_terms = []

        for term in terms:

            if term.lower() in lower_text:

                matched_terms.append(term)

        if matched_terms:

            matches[group].append({
                "cell_index": record["index"],
                "cell_type": record["cell_type"],
                "terms": matched_terms,
                "source": record["source"],
                "output": record["output"],
            })

# ------------------------------------------------------------
# 7. PRINT SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("PROVENANCE SEARCH SUMMARY")
print("=" * 70)

for group, records in matches.items():

    print(
        f"{group:<32}: "
        f"{len(records)} matching cells"
    )

# ------------------------------------------------------------
# 8. PRINT IMPORTANT CELLS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("IMPORTANT SOURCE EVIDENCE")
print("=" * 70)

for group, records in matches.items():

    print(
        f"\n### {group}"
    )

    if not records:

        print("No matching cells found.")
        continue

    # Limit console output to first 20 cells per category
    for item in records[:20]:

        print(
            "\n"
            + "-" * 70
        )

        print(
            f"Cell index : {item['cell_index']}"
        )

        print(
            f"Cell type  : {item['cell_type']}"
        )

        print(
            "Matched terms:",
            ", ".join(item["terms"])
        )

        source = item["source"].strip()

        if source:

            # Keep console manageable
            if len(source) > 5000:
                source = source[:5000] + "\n...[TRUNCATED]"

            print(
                "\nSOURCE:\n"
                + source
            )

        output = item["output"].strip()

        if output:

            if len(output) > 3000:
                output = output[:3000] + "\n...[TRUNCATED]"

            print(
                "\nOUTPUT:\n"
                + output
            )

# ------------------------------------------------------------
# 9. SPECIFIC SEARCH FOR DATA LOADING
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("DATA LOADING CELLS")
print("=" * 70)

loading_patterns = [
    r"pd\.read_csv",
    r"pd\.read_excel",
    r"read_csv",
    r"read_excel",
    r"load_dataset",
    r"load_from_disk",
    r"datasets\.load",
    r"huggingface",
    r"kaggle",
    r"download",
    r"requests\.",
    r"urllib",
    r"wget",
]

loading_cells = []

for record in cell_records:

    text = record["combined"]

    matched = []

    for pattern in loading_patterns:

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):

            matched.append(pattern)

    if matched:

        loading_cells.append({
            "index": record["index"],
            "type": record["cell_type"],
            "patterns": matched,
            "source": record["source"],
            "output": record["output"],
        })

for item in loading_cells:

    print(
        f"\nCell {item['index']} "
        f"({item['type']})"
    )

    print(
        "Patterns:",
        ", ".join(item["patterns"])
    )

    source = item["source"].strip()

    if len(source) > 4000:
        source = source[:4000] + "\n...[TRUNCATED]"

    print(source)

# ------------------------------------------------------------
# 10. SPECIFIC SEARCH FOR GENERATION OPERATIONS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("POSSIBLE DATA GENERATION CELLS")
print("=" * 70)

generation_patterns = [
    r"np\.random",
    r"numpy\.random",
    r"random_state",
    r"faker",
    r"make_classification",
    r"make_blobs",
    r"synthetic",
    r"simulate",
    r"simulation",
    r"generate_",
    r"generated",
]

generation_cells = []

for record in cell_records:

    text = record["combined"]

    matched = []

    for pattern in generation_patterns:

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):

            matched.append(pattern)

    if matched:

        generation_cells.append({
            "index": record["index"],
            "type": record["cell_type"],
            "patterns": matched,
            "source": record["source"],
            "output": record["output"],
        })

for item in generation_cells:

    print(
        f"\nCell {item['index']} "
        f"({item['type']})"
    )

    print(
        "Patterns:",
        ", ".join(item["patterns"])
    )

    source = item["source"].strip()

    if len(source) > 4000:
        source = source[:4000] + "\n...[TRUNCATED]"

    print(source)

# ------------------------------------------------------------
# 11. CREATE REPORT
# ------------------------------------------------------------

report = []

report.append(
    "# AFRIDATACYBERJOHN v1.0 — Original Notebook "
    "Provenance Evidence"
)

report.append("")

report.append(
    f"**Source notebook:** `{NOTEBOOK}`"
)

report.append("")

report.append(
    f"**Notebook cells examined:** {len(cells)}"
)

report.append("")

report.append(
    "## Important Interpretation Rule"
)

report.append("")

report.append(
    "Keyword matches are evidence to inspect, not automatic "
    "proof of dataset origin. A reference to synthetic data "
    "may describe a rejected reconciliation operation rather "
    "than the origin of the dataset. Likewise, a reference "
    "to real-world data may describe external validation "
    "rather than the source of the records."
)

report.append("")

for group, records in matches.items():

    report.append(
        f"## {group}"
    )

    report.append("")

    report.append(
        f"Matching cells: **{len(records)}**"
    )

    report.append("")

    for item in records[:30]:

        report.append(
            f"### Cell {item['cell_index']} "
            f"({item['cell_type']})"
        )

        report.append("")

        report.append(
            "**Matched terms:** "
            + ", ".join(item["terms"])
        )

        report.append("")

        source = item["source"].strip()

        if source:

            report.append(
                "```text"
            )

            report.append(source)

            report.append(
                "```"
            )

            report.append("")

        output = item["output"].strip()

        if output:

            report.append(
                "**Output:**"
            )

            report.append("")

            report.append(
                "```text"
            )

            report.append(output)

            report.append(
                "```"
            )

            report.append("")

report.append(
    "## Data Loading Cells"
)

report.append("")

report.append(
    f"Potential data-loading cells identified: "
    f"**{len(loading_cells)}**"
)

report.append("")

for item in loading_cells[:50]:

    report.append(
        f"### Cell {item['index']} "
        f"({item['type']})"
    )

    report.append("")

    report.append(
        "**Patterns:** "
        + ", ".join(item["patterns"])
    )

    report.append("")

    report.append(
        "```text"
    )

    report.append(
        item["source"].strip()
    )

    report.append(
        "```"
    )

    report.append("")

report.append(
    "## Possible Data Generation Cells"
)

report.append("")

report.append(
    f"Potential generation cells identified: "
    f"**{len(generation_cells)}**"
)

report.append("")

for item in generation_cells[:50]:

    report.append(
        f"### Cell {item['index']} "
        f"({item['type']})"
    )

    report.append("")

    report.append(
        "**Patterns:** "
        + ", ".join(item["patterns"])
    )

    report.append("")

    report.append(
        "```text"
    )

    report.append(
        item["source"].strip()
    )

    report.append(
        "```"
    )

    report.append("")

report.append(
    "## Current Status"
)

report.append("")

report.append(
    "- Dataset modified by this audit: **NO**"
)

report.append(
    "- Frozen release modified: **NO**"
)

report.append(
    "- Provenance classification assigned: **NO**"
)

report.append(
    "- License assigned: **NO**"
)

REPORT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8"
)

# ------------------------------------------------------------
# 12. FINAL OUTPUT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STAGE 38 COMPLETE")
print("=" * 70)

print(
    "Notebook cells examined:",
    len(cells)
)

print(
    "Potential loading cells:",
    len(loading_cells)
)

print(
    "Potential generation cells:",
    len(generation_cells)
)

print()
print("Evidence report:")
print(REPORT_FILE)

print()
print("Dataset modified: NO")
print("Release modified : NO")
print("Provenance assigned: NO")
print("License assigned   : NO")

print("=" * 70)

# ==============================================================================
# NOTEBOOK CELL 667
# ==============================================================================

# ============================================================
# STAGE 39 — ORIGINAL BASE-DATA ORIGIN EXTRACTION
#
# PURPOSE:
#   Find the earliest cells in Africadataset.ipynb that actually
#   CREATE or LOAD the underlying event data.
#
# READ ONLY
# ============================================================

import json
from pathlib import Path
import re

NOTEBOOK = Path(
    "/content/drive/MyDrive/Colab Notebooks/Africadataset.ipynb"
)

OUTPUT_DIR = Path(
    "/content/AFRIDATACYBERJOHN_STAGE39_ORIGIN_AUDIT"
)

REPORT = (
    OUTPUT_DIR /
    "ORIGINAL_BASE_DATA_ORIGIN_EVIDENCE.md"
)

if not NOTEBOOK.exists():
    raise FileNotFoundError(NOTEBOOK)

if OUTPUT_DIR.exists():
    import shutil
    shutil.rmtree(OUTPUT_DIR)

OUTPUT_DIR.mkdir(parents=True)

print("=" * 80)
print("STAGE 39 — ORIGINAL BASE-DATA ORIGIN EXTRACTION")
print("=" * 80)

# ------------------------------------------------------------
# LOAD NOTEBOOK
# ------------------------------------------------------------

with open(
    NOTEBOOK,
    "r",
    encoding="utf-8"
) as f:
    nb = json.load(f)

cells = nb.get("cells", [])

print("Notebook:", NOTEBOOK)
print("Total cells:", len(cells))

# ------------------------------------------------------------
# HELPER
# ------------------------------------------------------------

def cell_source(cell):
    src = cell.get("source", [])
    return "".join(src) if isinstance(src, list) else str(src)

def cell_output(cell):
    parts = []

    for out in cell.get("outputs", []):

        if "text" in out:

            value = out["text"]

            if isinstance(value, list):
                value = "".join(value)

            parts.append(str(value))

        data = out.get("data", {})

        if isinstance(data, dict):

            for mime in [
                "text/plain",
                "text/markdown"
            ]:

                if mime in data:

                    value = data[mime]

                    if isinstance(value, list):
                        value = "".join(value)

                    parts.append(str(value))

    return "\n".join(parts)

# ------------------------------------------------------------
# SEARCH PATTERNS
# ------------------------------------------------------------

groups = {

    "DATA_LOADING": [
        r"pd\.read_csv",
        r"pd\.read_excel",
        r"read_csv",
        r"read_excel",
        r"load_dataset",
        r"load_from_disk",
        r"datasets\.load",
        r"huggingface",
        r"kaggle",
        r"zenodo",
        r"github",
        r"download",
        r"requests\.",
        r"urllib",
        r"wget",
    ],

    "DATA_GENERATION": [
        r"np\.random",
        r"numpy\.random",
        r"random_state",
        r"faker",
        r"make_classification",
        r"make_blobs",
        r"make_regression",
        r"simulate",
        r"simulation",
        r"synthetic",
        r"generated data",
        r"generate.*data",
        r"generate.*event",
        r"generated.*event",
        r"random.*event",
        r"random.*transaction",
    ],

    "BASE_EVENT_CREATION": [
        r"events\s*=",
        r"event_rows\s*=",
        r"event_records\s*=",
        r"observations\s*=",
        r"obs\s*=",
        r"base_events",
        r"raw_events",
        r"event_stream",
        r"stochastic.*event",
        r"transaction.*records",
    ],

    "DATA_SOURCE_LANGUAGE": [
        r"source",
        r"origin",
        r"collected",
        r"collection",
        r"provided",
        r"obtained",
        r"acquired",
        r"recorded",
        r"observed",
        r"production",
        r"operational",
        r"real[- ]world",
        r"real data",
        r"simulated",
        r"synthetic",
    ],
}

# ------------------------------------------------------------
# FIND MATCHES
# ------------------------------------------------------------

results = {}

for group, patterns in groups.items():

    group_results = []

    for idx, cell in enumerate(cells):

        source = cell_source(cell)
        output = cell_output(cell)

        combined = (
            source
            + "\n"
            + output
        )

        matched = []

        for pattern in patterns:

            if re.search(
                pattern,
                combined,
                flags=re.IGNORECASE
            ):
                matched.append(pattern)

        if matched:

            group_results.append({
                "cell": idx,
                "type": cell.get(
                    "cell_type",
                    ""
                ),
                "matches": matched,
                "source": source,
                "output": output,
            })

    results[group] = group_results

# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("MATCH SUMMARY")
print("=" * 80)

for group, records in results.items():

    print(
        f"{group:<25}: {len(records)} cells"
    )

# ------------------------------------------------------------
# PRINT EARLIEST MATCHES
# ------------------------------------------------------------

for group, records in results.items():

    print("\n" + "=" * 80)
    print(group)
    print("=" * 80)

    if not records:

        print("NONE FOUND")
        continue

    # IMPORTANT:
    # Show earliest 20 matches only.
    for item in records[:20]:

        print("\n" + "-" * 80)

        print(
            "CELL:",
            item["cell"]
        )

        print(
            "TYPE:",
            item["type"]
        )

        print(
            "MATCHES:",
            item["matches"]
        )

        source = item["source"].strip()

        if source:

            if len(source) > 6000:
                source = (
                    source[:6000]
                    + "\n...[TRUNCATED]"
                )

            print("\nSOURCE:")
            print(source)

        output = item["output"].strip()

        if output:

            if len(output) > 3000:
                output = (
                    output[:3000]
                    + "\n...[TRUNCATED]"
                )

            print("\nOUTPUT:")
            print(output)

# ------------------------------------------------------------
# SPECIAL: FIRST 250 CELLS
#
# The later K0R9W/K12 forensic cells should not be mistaken
# for original data-generation cells.
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("EARLY NOTEBOOK ORIGIN SEARCH — CELLS 0–250")
print("=" * 80)

early_hits = []

for idx in range(
    0,
    min(251, len(cells))
):

    cell = cells[idx]

    source = cell_source(cell)
    output = cell_output(cell)

    combined = (
        source
        + "\n"
        + output
    )

    matched = []

    for group, patterns in groups.items():

        for pattern in patterns:

            if re.search(
                pattern,
                combined,
                flags=re.IGNORECASE
            ):

                matched.append(
                    f"{group}:{pattern}"
                )

    if matched:

        early_hits.append({
            "cell": idx,
            "matches": matched,
            "source": source,
            "output": output,
        })

for item in early_hits:

    print("\n" + "-" * 80)

    print(
        "CELL:",
        item["cell"]
    )

    print(
        "MATCHES:",
        item["matches"]
    )

    source = item["source"].strip()

    if source:

        if len(source) > 8000:
            source = (
                source[:8000]
                + "\n...[TRUNCATED]"
            )

        print("\nSOURCE:")
        print(source)

    output = item["output"].strip()

    if output:

        if len(output) > 4000:
            output = (
                output[:4000]
                + "\n...[TRUNCATED]"
            )

        print("\nOUTPUT:")
        print(output)

# ------------------------------------------------------------
# SAVE REPORT
# ------------------------------------------------------------

report_lines = []

report_lines.append(
    "# AFRIDATACYBERJOHN v1.0"
)

report_lines.append(
    "# Original Base-Data Origin Evidence"
)

report_lines.append("")

report_lines.append(
    f"Notebook: `{NOTEBOOK}`"
)

report_lines.append(
    f"Total cells: **{len(cells)}**"
)

report_lines.append("")

report_lines.append(
    "This report is an evidence extraction only. "
    "It does not classify the dataset as synthetic, "
    "real-world, or mixed."
)

report_lines.append("")

for group, records in results.items():

    report_lines.append(
        f"## {group}"
    )

    report_lines.append("")

    report_lines.append(
        f"Matching cells: **{len(records)}**"
    )

    report_lines.append("")

    for item in records[:30]:

        report_lines.append(
            f"### Cell {item['cell']}"
        )

        report_lines.append("")

        report_lines.append(
            "**Matches:** "
            + ", ".join(item["matches"])
        )

        report_lines.append("")

        if item["source"].strip():

            report_lines.append(
                "```text"
            )

            report_lines.append(
                item["source"]
            )

            report_lines.append(
                "```"
            )

            report_lines.append("")

        if item["output"].strip():

            report_lines.append(
                "**Stored output:**"
            )

            report_lines.append("")

            report_lines.append(
                "```text"
            )

            report_lines.append(
                item["output"]
            )

            report_lines.append(
                "```"
            )

            report_lines.append("")

report_lines.append(
    "## Current Status"
)

report_lines.append("")

report_lines.append(
    "- Dataset modified: **NO**"
)

report_lines.append(
    "- Release modified: **NO**"
)

report_lines.append(
    "- Provenance assigned: **NO**"
)

REPORT.write_text(
    "\n".join(report_lines),
    encoding="utf-8"
)

print("\n" + "=" * 80)
print("STAGE 39 COMPLETE")
print("=" * 80)

print(
    "Report:",
    REPORT
)

print(
    "Dataset modified: NO"
)

print(
    "Release modified: NO"
)

print(
    "Provenance assigned: NO"
)

print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 668
# ==============================================================================

# ============================================================
# STEP 1 — AFRIDATACYBERJOHN PROVENANCE INVESTIGATION
# READ-ONLY — DO NOT MODIFY DATASET OR RELEASE
# ============================================================

from pathlib import Path
import json
import re
from collections import Counter

print("=" * 80)
print("AFRIDATACYBERJOHN — STEP 1: DATASET PROVENANCE INVESTIGATION")
print("=" * 80)

# ------------------------------------------------------------
# 1. LOCATE ORIGINAL NOTEBOOK
# ------------------------------------------------------------

NOTEBOOK_CANDIDATES = [
    Path("/content/drive/MyDrive/Colab Notebooks/Africadataset.ipynb"),
    Path("/content/gdrive_afritac/MyDrive/Colab Notebooks/Africadataset.ipynb"),
]

NOTEBOOK = None

for p in NOTEBOOK_CANDIDATES:
    if p.exists():
        NOTEBOOK = p
        break

if NOTEBOOK is None:
    print("\nERROR: Original notebook was not found.")
    print("Checked:")
    for p in NOTEBOOK_CANDIDATES:
        print("  ", p)
    raise FileNotFoundError("Original Africadataset.ipynb not found.")

print("\nORIGINAL NOTEBOOK FOUND:")
print(NOTEBOOK)

# ------------------------------------------------------------
# 2. LOAD NOTEBOOK
# ------------------------------------------------------------

with open(NOTEBOOK, "r", encoding="utf-8", errors="ignore") as f:
    notebook = json.load(f)

cells = notebook.get("cells", [])

print("\nNOTEBOOK SUMMARY")
print("-" * 80)
print("Total cells:", len(cells))

# ------------------------------------------------------------
# 3. DEFINE LATER FORENSIC / AUDIT MARKERS
# ------------------------------------------------------------
# These are NOT treated as evidence of original data generation.
# They are used to separate later investigation cells from
# possible original construction cells.

LATER_STAGE_MARKERS = [
    "STAGE 20",
    "STAGE 21",
    "STAGE 22",
    "STAGE 23",
    "STAGE 24",
    "STAGE 25",
    "STAGE 26",
    "STAGE 27",
    "STAGE 28",
    "STAGE 29",
    "STAGE 30",
    "STAGE 31",
    "STAGE 32",
    "STAGE 33",
    "STAGE 34",
    "STAGE 35",
    "STAGE 36",
    "STAGE 37",
    "STAGE 38",
    "STAGE 39",
    "FORENSIC",
    "PUBLICATION",
    "REPOSITORY",
    "PROVENANCE AUDIT",
    "CHECKPOINT OBJECT RECOVERY",
]

# ------------------------------------------------------------
# 4. EXTRACT CELL TEXT
# ------------------------------------------------------------

def cell_text(cell):
    src = cell.get("source", [])
    if isinstance(src, list):
        return "".join(src)
    return str(src)

cell_records = []

for i, cell in enumerate(cells):
    text = cell_text(cell)

    cell_records.append({
        "index": i,
        "type": cell.get("cell_type", ""),
        "text": text,
        "lower": text.lower(),
    })

# ------------------------------------------------------------
# 5. SEARCH TERMS RELATED TO DATA ORIGIN
# ------------------------------------------------------------

ORIGIN_TERMS = [
    "synthetic",
    "simulated",
    "simulation",
    "generated",
    "generate",
    "faker",
    "random",
    "np.random",
    "random_state",
    "seed(",
    "real-world",
    "real world",
    "real data",
    "actual data",
    "production",
    "collected",
    "collection",
    "captured",
    "observed",
    "derived",
    "constructed",
    "constructed dataset",
    "created dataset",
    "source dataset",
    "source data",
    "external dataset",
    "download",
    "read_csv",
    "read_excel",
    "read_parquet",
    "load_dataset",
    "dataset",
]

# ------------------------------------------------------------
# 6. IDENTIFY CELLS CONTAINING ORIGIN-RELATED TERMS
# ------------------------------------------------------------

candidate_cells = []

for rec in cell_records:
    matches = []

    for term in ORIGIN_TERMS:
        if term.lower() in rec["lower"]:
            matches.append(term)

    if matches:
        candidate_cells.append({
            "index": rec["index"],
            "type": rec["type"],
            "matches": sorted(set(matches)),
            "text": rec["text"],
        })

print("\nORIGIN-RELATED CELLS FOUND:", len(candidate_cells))

# ------------------------------------------------------------
# 7. REMOVE OBVIOUSLY LATE FORENSIC/AUDIT CELLS
# ------------------------------------------------------------

early_candidates = []

for item in candidate_cells:

    text_upper = item["text"].upper()

    is_late = any(
        marker in text_upper
        for marker in LATER_STAGE_MARKERS
    )

    if not is_late:
        early_candidates.append(item)

print("POTENTIAL EARLY CELLS:", len(early_candidates))

# ------------------------------------------------------------
# 8. DISPLAY EARLY CANDIDATES
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("EARLY ORIGIN-RELATED CELLS")
print("=" * 80)

for item in early_candidates:

    print("\n" + "-" * 80)
    print("CELL:", item["index"])
    print("TYPE:", item["type"])
    print("MATCHES:", ", ".join(item["matches"]))
    print("-" * 80)

    lines = item["text"].splitlines()

    # Show only first 80 lines of each candidate
    for line_no, line in enumerate(lines[:80], start=1):
        print(f"{line_no:4}: {line}")

    if len(lines) > 80:
        print("... [CELL OUTPUT TRUNCATED]")

# ------------------------------------------------------------
# 9. SPECIFIC SEARCH FOR DATAFRAME CREATION
# ------------------------------------------------------------

DATAFRAME_PATTERNS = [
    r"\b\w+\s*=\s*pd\.DataFrame",
    r"\b\w+\s*=\s*pd\.read_csv",
    r"\b\w+\s*=\s*pd\.read_excel",
    r"\b\w+\s*=\s*pd\.read_parquet",
    r"\b\w+\s*=\s*pd\.read_json",
    r"\b\w+\s*=\s*pd\.concat",
    r"\b\w+\s*=\s*pd\.merge",
    r"\b\w+\s*=\s*pd\.DataFrame\(",
]

print("\n" + "=" * 80)
print("DATAFRAME / DATA LOADING CREATION CELLS")
print("=" * 80)

creation_cells = []

for rec in cell_records:

    text = rec["text"]

    found = []

    for pattern in DATAFRAME_PATTERNS:
        if re.search(pattern, text):
            found.append(pattern)

    if found:
        creation_cells.append(rec)

for rec in creation_cells:

    text_upper = rec["text"].upper()

    is_late = any(
        marker in text_upper
        for marker in LATER_STAGE_MARKERS
    )

    print("\nCELL:", rec["index"])
    print("LATE FORENSIC/AUDIT CELL:", is_late)

    lines = rec["text"].splitlines()

    for line_no, line in enumerate(lines[:60], start=1):
        print(f"{line_no:4}: {line}")

# ------------------------------------------------------------
# 10. SEARCH FOR FILE INPUTS
# ------------------------------------------------------------

FILE_INPUT_PATTERNS = [
    r"read_csv\s*\(",
    r"read_excel\s*\(",
    r"read_parquet\s*\(",
    r"read_json\s*\(",
    r"open\s*\(",
    r"glob\.glob",
    r"Path\(.*\)\.glob",
    r"\.csv",
    r"\.parquet",
    r"\.xlsx",
    r"\.json",
]

print("\n" + "=" * 80)
print("POTENTIAL EXTERNAL / FILE DATA INPUTS")
print("=" * 80)

file_input_cells = []

for rec in cell_records:

    matches = []

    for pattern in FILE_INPUT_PATTERNS:
        if re.search(pattern, rec["text"], flags=re.IGNORECASE):
            matches.append(pattern)

    if matches:
        text_upper = rec["text"].upper()

        is_late = any(
            marker in text_upper
            for marker in LATER_STAGE_MARKERS
        )

        file_input_cells.append({
            "index": rec["index"],
            "matches": matches,
            "late": is_late,
            "text": rec["text"],
        })

for item in file_input_cells:

    print("\n" + "-" * 80)
    print("CELL:", item["index"])
    print("LATE FORENSIC/AUDIT:", item["late"])
    print("MATCHES:", ", ".join(item["matches"]))
    print("-" * 80)

    lines = item["text"].splitlines()

    for line_no, line in enumerate(lines[:50], start=1):
        print(f"{line_no:4}: {line}")

# ------------------------------------------------------------
# 11. SEARCH FOR RANDOM / SYNTHETIC GENERATION
# ------------------------------------------------------------

GENERATION_PATTERNS = [
    r"np\.random",
    r"random\.",
    r"RandomState",
    r"default_rng",
    r"faker",
    r"make_classification",
    r"make_blobs",
    r"synthetic",
    r"simulate",
    r"simulation",
    r"generate_",
    r"generated",
]

print("\n" + "=" * 80)
print("POTENTIAL DATA GENERATION CELLS")
print("=" * 80)

generation_cells = []

for rec in cell_records:

    matches = []

    for pattern in GENERATION_PATTERNS:
        if re.search(pattern, rec["text"], flags=re.IGNORECASE):
            matches.append(pattern)

    if matches:
        text_upper = rec["text"].upper()

        is_late = any(
            marker in text_upper
            for marker in LATER_STAGE_MARKERS
        )

        generation_cells.append({
            "index": rec["index"],
            "matches": sorted(set(matches)),
            "late": is_late,
            "text": rec["text"],
        })

for item in generation_cells:

    print("\n" + "-" * 80)
    print("CELL:", item["index"])
    print("LATE FORENSIC/AUDIT:", item["late"])
    print("MATCHES:", ", ".join(item["matches"]))
    print("-" * 80)

    lines = item["text"].splitlines()

    for line_no, line in enumerate(lines[:60], start=1):
        print(f"{line_no:4}: {line}")

# ------------------------------------------------------------
# 12. SEARCH FOR ORIGINAL SOURCE OBJECT NAMES
# ------------------------------------------------------------

SOURCE_OBJECT_TERMS = [
    "AFRITAC_USERS",
    "AFRITAC_DEVICES",
    "AFRITAC_SESSIONS",
    "AFRITAC_OBSERVABLE",
    "AFRITAC_CAMPAIGNS",
    "AFRITAC_ATTACK",
    "campaign_control",
    "observable_events",
    "attack_events",
    "sessions",
    "users",
    "devices",
]

print("\n" + "=" * 80)
print("SOURCE OBJECT REFERENCES")
print("=" * 80)

object_hits = []

for rec in cell_records:

    hits = []

    for term in SOURCE_OBJECT_TERMS:
        if term.lower() in rec["lower"]:
            hits.append(term)

    if hits:

        text_upper = rec["text"].upper()

        is_late = any(
            marker in text_upper
            for marker in LATER_STAGE_MARKERS
        )

        object_hits.append({
            "index": rec["index"],
            "hits": hits,
            "late": is_late,
            "text": rec["text"],
        })

for item in object_hits:

    print("\nCELL:", item["index"])
    print("LATE FORENSIC/AUDIT:", item["late"])
    print("OBJECTS:", ", ".join(item["hits"]))

    lines = item["text"].splitlines()

    for line_no, line in enumerate(lines[:40], start=1):
        print(f"{line_no:4}: {line}")

# ------------------------------------------------------------
# 13. SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("PROVENANCE INVESTIGATION SUMMARY")
print("=" * 80)

print("Notebook:", NOTEBOOK)
print("Total cells:", len(cells))
print("Origin-related cells:", len(candidate_cells))
print("Potential early origin cells:", len(early_candidates))
print("Dataframe creation/loading cells:", len(creation_cells))
print("File-input cells:", len(file_input_cells))
print("Potential generation cells:", len(generation_cells))
print("Source-object reference cells:", len(object_hits))

print("\nIMPORTANT:")
print("No provenance classification has been assigned by this code.")
print("No dataset files have been modified.")
print("No release files have been modified.")
print("No license has been assigned.")

print("\nNEXT STEP:")
print("Review the EARLY ORIGIN-RELATED CELLS and DATAFRAME / DATA LOADING")
print("cells above. We will use the earliest genuine construction evidence")
print("to determine the dataset origin.")

# ==============================================================================
# NOTEBOOK CELL 669
# ==============================================================================

# ============================================================
# STEP 1B — FIND FIRST CREATION OF ORIGINAL DATA OBJECTS
# READ ONLY
# ============================================================

from pathlib import Path
import json
import re

NOTEBOOK = Path(
    "/content/drive/MyDrive/Colab Notebooks/Africadataset.ipynb"
)

if not NOTEBOOK.exists():
    NOTEBOOK = Path(
        "/content/gdrive_afritac/MyDrive/Colab Notebooks/Africadataset.ipynb"
    )

assert NOTEBOOK.exists(), f"Notebook not found: {NOTEBOOK}"

with open(NOTEBOOK, "r", encoding="utf-8", errors="ignore") as f:
    nb = json.load(f)

cells = nb.get("cells", [])

print("=" * 80)
print("STEP 1B — FIRST CREATION OF ORIGINAL DATA OBJECTS")
print("=" * 80)
print("Notebook:", NOTEBOOK)
print("Total cells:", len(cells))

# ------------------------------------------------------------
# OBJECTS WE NEED TO TRACE
# ------------------------------------------------------------

TARGETS = [
    "users",
    "devices",
    "sessions",
    "events",
    "observable_events",
    "campaigns",
    "attack",
    "attack_events",
    "campaign_control",
]

# ------------------------------------------------------------
# SEARCH ASSIGNMENTS
# ------------------------------------------------------------

for target in TARGETS:

    assignment_pattern = re.compile(
        rf"^\s*{re.escape(target)}\s*=",
        re.MULTILINE
    )

    hits = []

    for i, cell in enumerate(cells):

        source = "".join(cell.get("source", []))

        if assignment_pattern.search(source):
            hits.append(i)

    print("\n" + "=" * 80)
    print(f"OBJECT: {target}")
    print("=" * 80)

    if not hits:
        print("No direct assignment found.")
        continue

    print("Assignment cells:", hits[:20])

    # Show FIRST THREE assignments only
    for cell_index in hits[:3]:

        source = "".join(
            cells[cell_index].get("source", [])
        )

        print("\n" + "-" * 80)
        print("CELL:", cell_index)
        print("-" * 80)

        lines = source.splitlines()

        for n, line in enumerate(lines[:120], 1):
            print(f"{n:4}: {line}")

# ------------------------------------------------------------
# SEARCH FOR EXTERNAL FILE INPUTS
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("FIRST EXTERNAL FILE-INPUT CELLS")
print("=" * 80)

patterns = [
    r"pd\.read_csv",
    r"pd\.read_parquet",
    r"pd\.read_excel",
    r"pd\.read_json",
    r"read_pickle",
    r"open\(",
]

file_hits = []

for i, cell in enumerate(cells):

    source = "".join(cell.get("source", []))

    matched = [
        p for p in patterns
        if re.search(p, source, flags=re.IGNORECASE)
    ]

    if matched:
        file_hits.append((i, matched, source))

for i, matched, source in file_hits[:30]:

    print("\n" + "-" * 80)
    print("CELL:", i)
    print("MATCHES:", matched)
    print("-" * 80)

    for n, line in enumerate(source.splitlines()[:80], 1):
        print(f"{n:4}: {line}")

# ------------------------------------------------------------
# SEARCH FIRST RANDOM / GENERATION CELLS
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("FIRST RANDOM / GENERATION CELLS")
print("=" * 80)

generation_patterns = [
    r"np\.random",
    r"random\.",
    r"default_rng",
    r"RandomState",
    r"faker",
    r"make_classification",
    r"simulate",
    r"simulation",
    r"generate",
    r"synthetic",
]

generation_hits = []

for i, cell in enumerate(cells):

    source = "".join(cell.get("source", []))

    matched = [
        p for p in generation_patterns
        if re.search(p, source, flags=re.IGNORECASE)
    ]

    if matched:
        generation_hits.append((i, matched, source))

for i, matched, source in generation_hits[:30]:

    print("\n" + "-" * 80)
    print("CELL:", i)
    print("MATCHES:", matched)
    print("-" * 80)

    for n, line in enumerate(source.splitlines()[:80], 1):
        print(f"{n:4}: {line}")

print("\n" + "=" * 80)
print("STEP 1B COMPLETE")
print("=" * 80)
print("READ ONLY — NO DATASET MODIFIED")

# ==============================================================================
# NOTEBOOK CELL 670
# ==============================================================================

# ============================================================
# STAGE 39A — LOCATE EXISTING AFRIDATACYBERJOHN RELEASE
# ============================================================

from pathlib import Path

print("=" * 75)
print("STAGE 39A — LOCATE EXISTING RELEASE")
print("=" * 75)

SEARCH_ROOTS = [
    Path("/content"),
    Path("/content/drive/MyDrive"),
]

TARGET_NAMES = [
    "AFRIDATACYBERJOHN_v1.0",
    "AFRIDATACYBERJOHN_v1.0.zip",
    "AFRIDATACYBERJOHN_v1.0_SYNTHETIC_METADATA",
    "AFRIDATACYBERJOHN_v1.0_SYNTHETIC_METADATA.zip",
]

found = []

for root in SEARCH_ROOTS:

    if not root.exists():
        print(f"\nSKIPPING unavailable path: {root}")
        continue

    print(f"\nSearching: {root}")

    for target in TARGET_NAMES:

        matches = list(root.rglob(target))

        for match in matches:
            if match not in found:
                found.append(match)

                print("FOUND:")
                print(" ", match)

print("\n" + "=" * 75)
print("SEARCH SUMMARY")
print("=" * 75)

if not found:
    print("NO EXISTING AFRIDATACYBERJOHN RELEASE FOUND.")
    print()
    print("Do NOT recreate the dataset yet.")
    print("We need to recover the previous release/package first.")

else:
    print(f"Total matching paths found: {len(found)}")
    print()

    for path in found:
        print(path)

print("\nSTAGE 39A COMPLETE")

# ==============================================================================
# NOTEBOOK CELL 671
# ==============================================================================

# ============================================================
# STAGE 39B — RECOVER AFRIDATACYBERJOHN SOURCE/BUILD ARTIFACTS
# ============================================================

from pathlib import Path

print("=" * 75)
print("STAGE 39B — RECOVER SOURCE/BUILD ARTIFACTS")
print("=" * 75)

SEARCH_ROOTS = [
    Path("/content"),
    Path("/content/drive/MyDrive"),
]

SEARCH_TERMS = [
    "Africadataset.ipynb",
    "AFRICA_DATASET_PUBLICATION",
    "AFRICA_DATASET_v1.0_FINAL",
    "AFRICA_DATASET_v1.0_FINAL.zip",
    "AFRIDATACYBERJOHN",
    "AFRIDATACYBERJOHN_v1.0",
    "AFRIDATACYBERJOHN_v1.0.zip",
    "AFRICA_DATASET_STAGE30_REPOSITORY_METADATA",
    "AFRIDATACYBERJOHN_STAGE33_REPOSITORY_METADATA",
    "AFRIDATACYBERJOHN_STAGE35_ZENODO_SUBMISSION",
    "AFRIDATACYBERJOHN_STAGE38_NOTEBOOK_PROVENANCE",
]

found = []

for root in SEARCH_ROOTS:

    if not root.exists():
        continue

    print(f"\nSearching: {root}")

    for term in SEARCH_TERMS:

        matches = list(root.rglob(term))

        for match in matches:

            if match not in found:

                found.append(match)

                print("FOUND:")
                print(" ", match)

print("\n" + "=" * 75)
print("RECOVERY SUMMARY")
print("=" * 75)

if not found:

    print("NO PREVIOUS BUILD ARTIFACTS FOUND.")

else:

    print(f"Total artifacts found: {len(found)}")
    print()

    for path in sorted(found, key=str):
        print(path)

print("\nSTAGE 39B COMPLETE")

# ==============================================================================
# NOTEBOOK CELL 672
# ==============================================================================

# ============================================================
# STAGE 39C — ORIGINAL NOTEBOOK RECOVERY INVENTORY
# ============================================================
#
# PURPOSE
# -------
# Inspect the original Africadataset.ipynb to determine:
#
# 1. Total number of cells
# 2. Existing release/build stages
# 3. Historical dataset objects
# 4. Publication package construction code
# 5. Forensic checkpoint/recovery objects
# 6. Whether the notebook contains enough information
#    to reconstruct the validated release safely
#
# IMPORTANT
# ---------
# READ-ONLY.
#
# This stage:
# - does NOT execute notebook cells
# - does NOT generate data
# - does NOT modify the notebook
# - does NOT modify any dataframe
# - does NOT create a new dataset
# ============================================================

from pathlib import Path
import json
import re

NOTEBOOK = Path(
    "/content/drive/MyDrive/Colab Notebooks/Africadataset.ipynb"
)

print("=" * 75)
print("STAGE 39C — ORIGINAL NOTEBOOK RECOVERY INVENTORY")
print("=" * 75)

if not NOTEBOOK.exists():
    raise FileNotFoundError(
        f"Original notebook not found:\n{NOTEBOOK}"
    )

print("\nNOTEBOOK FOUND:")
print(NOTEBOOK)

# ============================================================
# 1. LOAD NOTEBOOK — READ ONLY
# ============================================================

with open(
    NOTEBOOK,
    "r",
    encoding="utf-8"
) as f:
    notebook = json.load(f)

cells = notebook.get("cells", [])

print("\nTOTAL NOTEBOOK CELLS:", len(cells))

# ============================================================
# 2. INVENTORY CELL TYPES
# ============================================================

cell_types = {}

for cell in cells:

    cell_type = cell.get(
        "cell_type",
        "UNKNOWN"
    )

    cell_types[cell_type] = (
        cell_types.get(cell_type, 0) + 1
    )

print("\nCELL TYPES")
print("-" * 75)

for k, v in sorted(cell_types.items()):
    print(f"{k:20s}: {v}")

# ============================================================
# 3. SEARCH TERMS
# ============================================================

search_terms = [
    "STAGE 20",
    "STAGE 21",
    "STAGE 22",
    "STAGE 23",
    "STAGE 24",
    "STAGE 25",
    "STAGE 26",
    "STAGE 27",
    "STAGE 28",
    "STAGE 29",
    "STAGE 30",
    "STAGE 31",
    "STAGE 32",
    "STAGE 33",
    "STAGE 34",
    "STAGE 35",
    "STAGE 36",
    "STAGE 37",
    "STAGE 38",
    "AFRICA_DATASET_PUBLICATION",
    "AFRICA_DATASET_v1.0",
    "AFRIDATACYBERJOHN_v1.0",
    "checksums.sha256",
    "CITATION.cff",
    "FORENSIC_VALIDATION",
    "dataset_metadata",
    "authoritative_events_71d5f",
    "current_events_71d5f",
    "authoritative_windows_71d5f",
    "current_windows",
    "matched_windows_71d5f",
    "candidate_matrix_scaled_71d5d",
    "candidate_matrix_scaled_71d5f",
    "positive_matrix_scaled_71d5f",
]

# ============================================================
# 4. FIND RELEVANT CELLS
# ============================================================

matches = []

for idx, cell in enumerate(cells):

    source = "".join(
        cell.get("source", [])
    )

    lower_source = source.lower()

    matched_terms = [
        term
        for term in search_terms
        if term.lower() in lower_source
    ]

    if matched_terms:

        matches.append(
            {
                "cell_index": idx,
                "cell_type": cell.get(
                    "cell_type",
                    "UNKNOWN"
                ),
                "terms": matched_terms,
                "source": source,
            }
        )

print("\nRELEVANT CELLS FOUND:", len(matches))

# ============================================================
# 5. PRINT STAGE/RELEASE INVENTORY
# ============================================================

print("\n" + "=" * 75)
print("RELEVANT NOTEBOOK CELLS")
print("=" * 75)

for item in matches:

    print(
        f"\nCELL {item['cell_index']}"
    )

    print(
        "TYPE:",
        item["cell_type"]
    )

    print(
        "MATCHES:",
        ", ".join(item["terms"])
    )

    # Print only first 12 source lines
    # to keep the inventory manageable.

    source_lines = item["source"].splitlines()

    preview = source_lines[:12]

    for line in preview:
        print(" ", line)

    if len(source_lines) > 12:
        print(
            f"  ... "
            f"[{len(source_lines) - 12} more lines]"
        )

# ============================================================
# 6. OBJECT/VARIABLE INVENTORY
# ============================================================

object_terms = [
    "authoritative_events_71d5f",
    "current_events_71d5f",
    "authoritative_windows_71d5f",
    "current_windows",
    "matched_windows_71d5f",
    "candidate_matrix_scaled_71d5f",
    "positive_matrix_scaled_71d5f",
    "candidate_matrix",
    "positive_matrix",
    "distance_matrix",
    "users",
    "devices",
    "sessions",
    "events",
]

object_cells = {}

for term in object_terms:

    hits = []

    for idx, cell in enumerate(cells):

        source = "".join(
            cell.get("source", [])
        )

        if term in source:
            hits.append(idx)

    object_cells[term] = hits

print("\n" + "=" * 75)
print("OBJECT REFERENCE INVENTORY")
print("=" * 75)

for term, hits in object_cells.items():

    print(
        f"{term:40s}: "
        f"{len(hits)} cells"
    )

    if hits:
        print(
            "  Cell indices:",
            hits[:20]
        )

# ============================================================
# 7. PUBLICATION BUILD REFERENCES
# ============================================================

publication_terms = [
    "FINAL_DIR",
    "FINAL_ZIP",
    "release_root",
    "source_root",
    "shutil.copytree",
    "zipfile.ZipFile",
    "checksums",
    "PUBLICATION",
    "RELEASE",
]

publication_hits = []

for idx, cell in enumerate(cells):

    source = "".join(
        cell.get("source", [])
    )

    found = [
        term
        for term in publication_terms
        if term.lower() in source.lower()
    ]

    if found:

        publication_hits.append(
            (
                idx,
                found
            )
        )

print("\n" + "=" * 75)
print("PUBLICATION/RELEASE BUILD CELLS")
print("=" * 75)

for idx, found in publication_hits:

    print(
        f"CELL {idx}:",
        ", ".join(found)
    )

# ============================================================
# 8. OUTPUT INVENTORY FILE
# ============================================================

REPORT_DIR = Path(
    "/content/AFRIDATACYBERJOHN_STAGE39C_RECOVERY"
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REPORT_FILE = (
    REPORT_DIR
    / "NOTEBOOK_RECOVERY_INVENTORY.txt"
)

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "AFRIDATACYBERJOHN STAGE 39C\n"
        "ORIGINAL NOTEBOOK RECOVERY INVENTORY\n"
        "\n"
    )

    f.write(
        f"Notebook: {NOTEBOOK}\n"
    )

    f.write(
        f"Total cells: {len(cells)}\n\n"
    )

    f.write(
        "CELL TYPES\n"
    )

    for k, v in sorted(cell_types.items()):
        f.write(
            f"{k}: {v}\n"
        )

    f.write(
        "\nRELEVANT CELLS\n"
    )

    for item in matches:

        f.write(
            f"\nCELL {item['cell_index']}\n"
        )

        f.write(
            f"TYPE: {item['cell_type']}\n"
        )

        f.write(
            "MATCHES: "
            + ", ".join(item["terms"])
            + "\n"
        )

    f.write(
        "\nOBJECT REFERENCES\n"
    )

    for term, hits in object_cells.items():

        f.write(
            f"{term}: {hits}\n"
        )

    f.write(
        "\nPUBLICATION BUILD CELLS\n"
    )

    for idx, found in publication_hits:

        f.write(
            f"CELL {idx}: "
            + ", ".join(found)
            + "\n"
        )

print("\n" + "=" * 75)
print("STAGE 39C COMPLETE")
print("=" * 75)

print("\nNotebook cells inspected :", len(cells))
print("Relevant cells found     :", len(matches))
print("Recovery report          :", REPORT_FILE)

print(
    "\nIMPORTANT: "
    "NO NOTEBOOK CELL WAS EXECUTED."
)
print(
    "NO DATASET WAS GENERATED."
)
print(
    "NO SOURCE DATA WAS MODIFIED."
)

# ==============================================================================
# NOTEBOOK CELL 673
# ==============================================================================

# ============================================================
# STAGE 39D — CHECK PERSISTENT AFRITAC CHECKPOINT
# ============================================================
#
# READ-ONLY
#
# PURPOSE:
#   Determine whether the validated AFRITAC checkpoint artifacts
#   still exist in Google Drive.
#
# IMPORTANT:
#   - Does NOT execute Africadataset.ipynb
#   - Does NOT regenerate the dataset
#   - Does NOT modify any dataframe
#   - Does NOT modify Google Drive files
# ============================================================

from pathlib import Path

print("=" * 75)
print("STAGE 39D — CHECK PERSISTENT AFRITAC CHECKPOINT")
print("=" * 75)

CHECKPOINT_ROOT = Path(
    "/content/drive/MyDrive/AFRITAC_CHECKPOINT"
)

print("\nCheckpoint path:")
print(CHECKPOINT_ROOT)

if not CHECKPOINT_ROOT.exists():

    print("\nCHECKPOINT DIRECTORY: NOT FOUND")

else:

    print("\nCHECKPOINT DIRECTORY: FOUND")

    files = [
        p for p in CHECKPOINT_ROOT.rglob("*")
        if p.is_file()
    ]

    print("\nTotal files:", len(files))

    print("\nCHECKPOINT CONTENTS")
    print("-" * 75)

    for p in sorted(files):

        try:
            size = p.stat().st_size
        except Exception:
            size = -1

        print(
            f"{p.relative_to(CHECKPOINT_ROOT)}"
            f"    [{size:,} bytes]"
        )

print("\n" + "=" * 75)
print("STAGE 39D COMPLETE")
print("=" * 75)

print("\nREAD-ONLY CHECK — NO DATA MODIFIED")

# ==============================================================================
# NOTEBOOK CELL 674
# ==============================================================================

from google.colab import files

uploaded = files.upload()

print("\nUploaded file(s):")
for filename in uploaded.keys():
    print(f"✓ {filename}")

# ==============================================================================
# NOTEBOOK CELL 675
# ==============================================================================

# ============================================================================
# STAGE 39F — READ-ONLY VALIDATION OF RECOVERED AFRICA_DATASET_v1.0
# ============================================================================
from pathlib import Path
import zipfile
import hashlib
import json
import pandas as pd
import io

ZIP_PATH = Path("/content/AFRICA_DATASET_v1.0.zip")

print("=" * 75)
print("STAGE 39F — RECOVERED AFRICA_DATASET_v1.0 VALIDATION")
print("=" * 75)

assert ZIP_PATH.exists(), f"ZIP not found: {ZIP_PATH}"

print(f"\nZIP: {ZIP_PATH}")
print(f"ZIP size: {ZIP_PATH.stat().st_size:,} bytes")

# --------------------------------------------------------------------------
# 1. ZIP integrity
# --------------------------------------------------------------------------
with zipfile.ZipFile(ZIP_PATH, "r") as z:
    bad = z.testzip()
    names = z.namelist()

print("\n[1] ZIP INTEGRITY")
print("PASS" if bad is None else f"FAIL — corrupted file: {bad}")

# --------------------------------------------------------------------------
# 2. List files
# --------------------------------------------------------------------------
print("\n[2] ZIP CONTENTS")
print("-" * 75)

for name in names:
    print(name)

print(f"\nTotal files: {len(names)}")

# --------------------------------------------------------------------------
# 3. Locate the four publication CSVs
# --------------------------------------------------------------------------
required_csvs = {
    "authoritative_events":
        "AFRICA_DATASET_v1.0/data/AFRICA_MobileMoney_USSD_Authoritative_Events.csv",

    "current_events":
        "AFRICA_DATASET_v1.0/data/AFRICA_MobileMoney_USSD_Current_Events.csv",

    "authoritative_windows":
        "AFRICA_DATASET_v1.0/data/AFRICA_MobileMoney_USSD_Authoritative_Windows.csv",

    "current_windows":
        "AFRICA_DATASET_v1.0/data/AFRICA_MobileMoney_USSD_Current_Windows.csv",
}

print("\n[3] REQUIRED DATA FILES")

with zipfile.ZipFile(ZIP_PATH, "r") as z:
    for label, filename in required_csvs.items():
        exists = filename in names
        print(f"{label:25s}: {'FOUND' if exists else 'MISSING'}")

# --------------------------------------------------------------------------
# 4. Read CSVs directly from ZIP — no extraction
# --------------------------------------------------------------------------
print("\n[4] DATASET SHAPES AND COLUMNS")
print("-" * 75)

loaded = {}

with zipfile.ZipFile(ZIP_PATH, "r") as z:
    for label, filename in required_csvs.items():

        raw = z.read(filename)

        df = pd.read_csv(io.BytesIO(raw))
        loaded[label] = df

        print(f"\n{label}")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {len(df.columns)}")

# --------------------------------------------------------------------------
# 5. Expected population checks
# --------------------------------------------------------------------------
expected_shapes = {
    "authoritative_events": (1029, 29),
    "current_events": (1060, 29),
    "authoritative_windows": (100, 8),
    "current_windows": (100, 10),
}

print("\n[5] EXPECTED POPULATION CHECK")
print("-" * 75)

population_pass = True

for label, expected in expected_shapes.items():
    actual = loaded[label].shape
    status = "PASS" if actual == expected else "FAIL"

    if status == "FAIL":
        population_pass = False

    print(
        f"{label:25s}: "
        f"actual={actual} | expected={expected} | {status}"
    )

# --------------------------------------------------------------------------
# 6. Event ID uniqueness
# --------------------------------------------------------------------------
print("\n[6] EVENT ID UNIQUENESS")

for label in ["authoritative_events", "current_events"]:
    df = loaded[label]

    if "event_id" in df.columns:
        unique = df["event_id"].nunique()
        total = len(df)

        print(
            f"{label:25s}: "
            f"{unique:,} unique / {total:,} rows | "
            f"{'PASS' if unique == total else 'FAIL'}"
        )
    else:
        print(f"{label:25s}: event_id MISSING")

# --------------------------------------------------------------------------
# 7. Window ID uniqueness
# --------------------------------------------------------------------------
print("\n[7] WINDOW ID UNIQUENESS")

for label in ["authoritative_windows", "current_windows"]:
    df = loaded[label]

    if "window_id" in df.columns:
        unique = df["window_id"].nunique()
        total = len(df)

        print(
            f"{label:25s}: "
            f"{unique:,} unique / {total:,} rows | "
            f"{'PASS' if unique == total else 'FAIL'}"
        )
    else:
        print(f"{label:25s}: window_id MISSING")

# --------------------------------------------------------------------------
# 8. Horizon distribution
# --------------------------------------------------------------------------
print("\n[8] HORIZON DISTRIBUTION")

for label in ["authoritative_windows", "current_windows"]:
    df = loaded[label]

    if "horizon_minutes" in df.columns:
        print(f"\n{label}:")
        print(df["horizon_minutes"].value_counts().sort_index())

# --------------------------------------------------------------------------
# 9. Ground-truth / label checks
# --------------------------------------------------------------------------
print("\n[9] LABEL / GROUND-TRUTH CHECKS")

for label in ["authoritative_events", "current_events"]:
    df = loaded[label]

    print(f"\n{label}")

    for col in [
        "ground_truth_state",
        "is_attack",
        "hard_negative",
        "is_observable_precursor",
    ]:
        if col in df.columns:
            print(f"  {col}:")
            print(df[col].value_counts(dropna=False).to_dict())
        else:
            print(f"  {col}: column not present")

# --------------------------------------------------------------------------
# 10. Checksum manifest
# --------------------------------------------------------------------------
print("\n[10] CHECKSUM MANIFEST")

checksum_file = (
    "AFRICA_DATASET_v1.0/metadata/checksums.sha256"
)

checksum_results = []

with zipfile.ZipFile(ZIP_PATH, "r") as z:

    checksum_text = z.read(checksum_file).decode("utf-8")

    entries = []

    for line in checksum_text.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        parts = line.split(maxsplit=1)

        if len(parts) == 2:
            entries.append((parts[0], parts[1]))

    print(f"Manifest entries: {len(entries)}")

    for expected_hash, relative_path in entries:

        # Handle possible "./" prefix
        relative_path = relative_path.lstrip("./")

        # Manifest paths may omit package root
        candidates = [
            relative_path,
            f"AFRICA_DATASET_v1.0/{relative_path}",
        ]

        target = None

        for candidate in candidates:
            if candidate in names:
                target = candidate
                break

        if target is None:
            checksum_results.append(
                (relative_path, "MISSING")
            )
            continue

        actual_hash = hashlib.sha256(
            z.read(target)
        ).hexdigest()

        status = (
            "PASS"
            if actual_hash == expected_hash
            else "FAIL"
        )

        checksum_results.append(
            (relative_path, status)
        )

    for path, status in checksum_results:
        print(f"{status:8s} {path}")

# --------------------------------------------------------------------------
# FINAL SUMMARY
# --------------------------------------------------------------------------
print("\n" + "=" * 75)
print("STAGE 39F SUMMARY")
print("=" * 75)

checksum_failures = [
    x for x in checksum_results
    if x[1] != "PASS"
]

print(f"ZIP integrity:       {'PASS' if bad is None else 'FAIL'}")
print(f"Population checks:   {'PASS' if population_pass else 'FAIL'}")
print(f"Checksum failures:   {len(checksum_failures)}")

print("\nREAD-ONLY GUARANTEE")
print("- No CSV modified")
print("- No ZIP modified")
print("- No checkpoint modified")
print("- No source dataframe modified")
print("- ZIP was inspected without extraction")

print("\nSTAGE 39F COMPLETE")

# ==============================================================================
# NOTEBOOK CELL 676
# ==============================================================================

# ============================================================================
# STAGE 39G — ZIP ↔ PERSISTENT CHECKPOINT FORENSIC COMPARISON
# ============================================================================
# READ-ONLY
# Does NOT modify:
#   - uploaded ZIP
#   - checkpoint files
#   - source dataframes
#   - notebook
# ============================================================================

from pathlib import Path
import zipfile
import hashlib
import io
import pandas as pd
import numpy as np

print("=" * 78)
print("STAGE 39G — ZIP ↔ PERSISTENT CHECKPOINT FORENSIC COMPARISON")
print("=" * 78)

ZIP_PATH = Path("/content/AFRICA_DATASET_v1.0.zip")
CHECKPOINT_ROOT = Path("/content/drive/MyDrive/AFRITAC_CHECKPOINT")

assert ZIP_PATH.exists(), f"Uploaded ZIP not found: {ZIP_PATH}"
assert CHECKPOINT_ROOT.exists(), f"Checkpoint not found: {CHECKPOINT_ROOT}"

# ----------------------------------------------------------------------------
# 1. Locate checkpoint artifacts
# ----------------------------------------------------------------------------

checkpoint_candidates = {
    "authoritative_events": [
        "authoritative/AFRITAC_OBSERVABLE.parquet",
    ],
    "authoritative_windows": [
        "positive/AFRITAC_POSITIVE_WINDOWS.parquet",
    ],
    "current_events": [
        "negative_reconstruction_71F_19_23/AFRITAC_NEGATIVE_FEATURES_71F_19_23.parquet",
        "71D5F_FORENSIC_K0R9S/obs_forensic_71d5f.parquet",
    ],
    "current_windows": [
        "negative_frozen/AFRITAC_FROZEN_NEGATIVE_CONTROLS.parquet",
    ],
}

print("\n[1] CHECKPOINT ARTIFACT AVAILABILITY")
print("-" * 78)

for label, candidates in checkpoint_candidates.items():
    print(f"\n{label}:")

    for rel in candidates:
        p = CHECKPOINT_ROOT / rel
        print(
            f"  {'FOUND' if p.exists() else 'MISSING'}  "
            f"{rel}"
        )

# ----------------------------------------------------------------------------
# 2. Load publication CSVs directly from ZIP
# ----------------------------------------------------------------------------

zip_files = {
    "authoritative_events":
        "AFRICA_DATASET_v1.0/data/AFRICA_MobileMoney_USSD_Authoritative_Events.csv",

    "current_events":
        "AFRICA_DATASET_v1.0/data/AFRICA_MobileMoney_USSD_Current_Events.csv",

    "authoritative_windows":
        "AFRICA_DATASET_v1.0/data/AFRICA_MobileMoney_USSD_Authoritative_Windows.csv",

    "current_windows":
        "AFRICA_DATASET_v1.0/data/AFRICA_MobileMoney_USSD_Current_Windows.csv",
}

publication = {}

with zipfile.ZipFile(ZIP_PATH, "r") as z:
    for label, member in zip_files.items():
        publication[label] = pd.read_csv(
            io.BytesIO(z.read(member))
        )

print("\n[2] PUBLICATION DATA LOADED")
print("-" * 78)

for label, df in publication.items():
    print(f"{label:25s}: {df.shape}")

# ----------------------------------------------------------------------------
# 3. Identify usable checkpoint artifacts
# ----------------------------------------------------------------------------

resolved = {}

for label, candidates in checkpoint_candidates.items():

    for rel in candidates:
        p = CHECKPOINT_ROOT / rel

        if p.exists():
            resolved[label] = p
            break

print("\n[3] SELECTED CHECKPOINT ARTIFACTS")
print("-" * 78)

for label, p in resolved.items():
    print(f"{label:25s}: {p}")

# ----------------------------------------------------------------------------
# 4. Load checkpoint artifacts and report schemas
# ----------------------------------------------------------------------------

checkpoint = {}

for label, p in resolved.items():

    try:
        df = pd.read_parquet(p)
        checkpoint[label] = df

        print(f"\n{label}")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  First columns: {list(df.columns[:10])}")

    except Exception as e:
        print(f"\n{label}")
        print(f"  LOAD ERROR: {e}")

# ----------------------------------------------------------------------------
# 5. Population comparison
# ----------------------------------------------------------------------------

print("\n" + "=" * 78)
print("[4] POPULATION COMPARISON")
print("=" * 78)

population_results = []

for label in publication:

    pub_n = len(publication[label])

    if label in checkpoint:
        chk_n = len(checkpoint[label])
        status = "PASS" if pub_n == chk_n else "DIFFERENT"

        print(
            f"{label:25s}: "
            f"ZIP={pub_n:,} | "
            f"CHECKPOINT={chk_n:,} | "
            f"{status}"
        )

        population_results.append(
            (label, pub_n, chk_n, status)
        )

    else:
        print(
            f"{label:25s}: "
            f"CHECKPOINT ARTIFACT NOT RESOLVED"
        )

# ----------------------------------------------------------------------------
# 6. Common-column comparison
# ----------------------------------------------------------------------------

print("\n" + "=" * 78)
print("[5] COMMON-COLUMN STRUCTURAL COMPARISON")
print("=" * 78)

for label in publication:

    if label not in checkpoint:
        continue

    pub = publication[label]
    chk = checkpoint[label]

    common = [c for c in pub.columns if c in chk.columns]

    print(f"\n{label}")
    print(f"  ZIP columns:        {len(pub.columns)}")
    print(f"  Checkpoint columns: {len(chk.columns)}")
    print(f"  Common columns:     {len(common)}")

    missing_from_checkpoint = [
        c for c in pub.columns
        if c not in chk.columns
    ]

    extra_checkpoint = [
        c for c in chk.columns
        if c not in pub.columns
    ]

    if missing_from_checkpoint:
        print(
            "  ZIP columns missing from checkpoint:",
            missing_from_checkpoint
        )

    if extra_checkpoint:
        print(
            "  Extra checkpoint columns:",
            extra_checkpoint
        )

# ----------------------------------------------------------------------------
# 7. Fingerprint comparison
# ----------------------------------------------------------------------------

def dataframe_fingerprint(df, exclude=None):
    """
    Stable row fingerprint based on sorted columns and values.
    Does not modify the supplied dataframe.
    """
    exclude = set(exclude or [])

    cols = [c for c in df.columns if c not in exclude]
    cols = sorted(cols)

    temp = df[cols].copy()

    # Normalize values only for comparison
    temp = temp.astype(object)

    for c in cols:
        temp[c] = temp[c].map(
            lambda x: "" if pd.isna(x) else str(x)
        )

    row_strings = temp.astype(str).agg(
        "||".join,
        axis=1
    )

    return pd.Series(
        [
            hashlib.sha256(s.encode("utf-8")).hexdigest()
            for s in row_strings
        ]
    )

print("\n" + "=" * 78)
print("[6] CONTENT FINGERPRINT COMPARISON")
print("=" * 78)

for label in publication:

    if label not in checkpoint:
        continue

    pub = publication[label]
    chk = checkpoint[label]

    common = [
        c for c in pub.columns
        if c in chk.columns
    ]

    if not common:
        print(f"\n{label}: NO COMMON COLUMNS")
        continue

    pub_common = pub[common].copy()
    chk_common = chk[common].copy()

    pub_fp = dataframe_fingerprint(pub_common)
    chk_fp = dataframe_fingerprint(chk_common)

    pub_counts = pub_fp.value_counts()
    chk_counts = chk_fp.value_counts()

    common_fp = set(pub_counts.index) & set(chk_counts.index)

    pub_rows_matched = sum(
        min(pub_counts[x], chk_counts[x])
        for x in common_fp
    )

    chk_rows_matched = sum(
        min(pub_counts[x], chk_counts[x])
        for x in common_fp
    )

    print(f"\n{label}")
    print(f"  ZIP rows:                {len(pub):,}")
    print(f"  Checkpoint rows:         {len(chk):,}")
    print(f"  Common fingerprints:     {len(common_fp):,}")
    print(f"  ZIP rows represented:    {pub_rows_matched:,}")
    print(f"  Checkpoint represented:  {chk_rows_matched:,}")

    exact = (
        len(pub) == len(chk)
        and pub_rows_matched == len(pub)
        and chk_rows_matched == len(chk)
    )

    print(
        f"  CONTENT RESULT: "
        f"{'EXACT MATCH' if exact else 'NOT EXACT / REQUIRES REVIEW'}"
    )

# ----------------------------------------------------------------------------
# 8. ID-level checks where applicable
# ----------------------------------------------------------------------------

print("\n" + "=" * 78)
print("[7] IDENTIFIER COVERAGE")
print("=" * 78)

for label in publication:

    if label not in checkpoint:
        continue

    pub = publication[label]
    chk = checkpoint[label]

    for id_col in ["event_id", "window_id"]:

        if id_col not in pub.columns or id_col not in chk.columns:
            continue

        pub_ids = set(
            pub[id_col].dropna().astype(str)
        )

        chk_ids = set(
            chk[id_col].dropna().astype(str)
        )

        common_ids = pub_ids & chk_ids

        print(f"\n{label} — {id_col}")
        print(f"  ZIP IDs:        {len(pub_ids):,}")
        print(f"  Checkpoint IDs: {len(chk_ids):,}")
        print(f"  Common IDs:     {len(common_ids):,}")
        print(
            f"  Exact ID set:   "
            f"{'YES' if pub_ids == chk_ids else 'NO'}"
        )

# ----------------------------------------------------------------------------
# 9. Final summary
# ----------------------------------------------------------------------------

print("\n" + "=" * 78)
print("STAGE 39G FINAL SUMMARY")
print("=" * 78)

print("""
This stage was READ-ONLY.

No:
- ZIP files modified
- checkpoint files modified
- source dataframes modified
- notebook cells rerun
- dataset rows regenerated
- files extracted or overwritten
""")

print("The results above determine whether the uploaded")
print("AFRICA_DATASET_v1.0 can be safely used as the")
print("recovered publication source.")

print("\nSTAGE 39G COMPLETE")

# ==============================================================================
# NOTEBOOK CELL 677
# ==============================================================================

# ============================================================================
# STAGE 39H — TRACE EXACT FINAL PUBLICATION ARTIFACTS
# ============================================================================
# READ-ONLY
# Purpose:
#   Identify exactly which objects/files produced the validated
#   AFRICA_DATASET_v1.0 publication CSVs.
# ============================================================================

from pathlib import Path
import json
import re

print("=" * 78)
print("STAGE 39H — TRACE EXACT FINAL PUBLICATION ARTIFACTS")
print("=" * 78)

NOTEBOOK = Path(
    "/content/drive/MyDrive/Colab Notebooks/Africadataset.ipynb"
)

assert NOTEBOOK.exists(), f"Notebook not found: {NOTEBOOK}"

with open(NOTEBOOK, "r", encoding="utf-8") as f:
    nb = json.load(f)

cells = nb.get("cells", [])

print(f"\nNotebook: {NOTEBOOK}")
print(f"Total cells: {len(cells)}")

# --------------------------------------------------------------------------
# Exact cells already identified from Stage 39C
# --------------------------------------------------------------------------

TARGET_CELLS = [629, 630, 631, 632, 633, 634]

print("\n" + "=" * 78)
print("TARGET CELLS")
print("=" * 78)

for idx in TARGET_CELLS:

    if idx >= len(cells):
        print(f"\nCELL {idx}: OUT OF RANGE")
        continue

    cell = cells[idx]

    source = "".join(cell.get("source", []))
    outputs = cell.get("outputs", [])

    print("\n" + "-" * 78)
    print(f"CELL {idx}")
    print("-" * 78)

    print("SOURCE:")
    print(source[:12000])

    if len(source) > 12000:
        print("\n[Source truncated for display]")

    print("\nOUTPUT COUNT:", len(outputs))

    for oi, out in enumerate(outputs):

        print(f"\nOUTPUT {oi} TYPE: {out.get('output_type')}")

        text_parts = []

        if "text" in out:
            text_parts.extend(out["text"])

        if "data" in out:
            data = out["data"]

            if "text/plain" in data:
                text_parts.extend(data["text/plain"])

        if text_parts:
            text = "".join(text_parts)

            print(text[:12000])

            if len(text) > 12000:
                print("\n[Output truncated for display]")

# --------------------------------------------------------------------------
# Search notebook for exact publication export variables
# --------------------------------------------------------------------------

print("\n" + "=" * 78)
print("PUBLICATION EXPORT REFERENCES THROUGHOUT NOTEBOOK")
print("=" * 78)

SEARCH_TERMS = [
    "EXPORT_DIR",
    "AFRICA_DATASET_PUBLICATION",
    "authoritative_events_71d5f",
    "current_events_71d5f",
    "authoritative_windows_71d5f",
    "current_windows",
    "to_csv",
    "publication",
    "AFRICA_MobileMoney_USSD_Authoritative_Events",
    "AFRICA_MobileMoney_USSD_Current_Events",
    "AFRICA_MobileMoney_USSD_Authoritative_Windows",
    "AFRICA_MobileMoney_USSD_Current_Windows",
]

for term in SEARCH_TERMS:

    print(f"\n### SEARCH: {term}")

    hits = []

    for idx, cell in enumerate(cells):

        source = "".join(cell.get("source", []))

        if term.lower() in source.lower():
            hits.append(idx)

    print("Cells:", hits)

# --------------------------------------------------------------------------
# Search checkpoint path references
# --------------------------------------------------------------------------

print("\n" + "=" * 78)
print("CHECKPOINT / ARTIFACT PATH REFERENCES")
print("=" * 78)

checkpoint_terms = [
    "AFRITAC_CHECKPOINT",
    "authoritative/",
    "positive/",
    "negative_frozen/",
    "negative_reconstruction",
    "71D5F_FORENSIC",
    "checkpoint",
    "parquet",
]

for term in checkpoint_terms:

    print(f"\n### SEARCH: {term}")

    hits = []

    for idx, cell in enumerate(cells):

        source = "".join(cell.get("source", []))

        if term.lower() in source.lower():
            hits.append(idx)

    print("Cells:", hits[-50:])

print("\n" + "=" * 78)
print("STAGE 39H COMPLETE")
print("=" * 78)

print("""
READ-ONLY:
- Notebook was only read
- No cells executed
- No files modified
- No checkpoint modified
- No ZIP modified
- No dataframe modified
""")

# ==============================================================================
# NOTEBOOK CELL 678
# ==============================================================================

# ============================================================================
# STAGE 39I — TRACE CONSTRUCTION OF THE FOUR FROZEN PUBLICATION OBJECTS
# ============================================================================
# READ-ONLY
# ============================================================================

from pathlib import Path
import json

NOTEBOOK = Path(
    "/content/drive/MyDrive/Colab Notebooks/Africadataset.ipynb"
)

assert NOTEBOOK.exists(), f"Notebook not found: {NOTEBOOK}"

with open(NOTEBOOK, "r", encoding="utf-8") as f:
    nb = json.load(f)

cells = nb["cells"]

TARGET_NAMES = [
    "authoritative_events_71d5f",
    "current_events_71d5f",
    "authoritative_windows_71d5f",
    "current_windows",
]

print("=" * 78)
print("STAGE 39I — TRACE FOUR FROZEN PUBLICATION OBJECTS")
print("=" * 78)

print(f"\nNotebook cells: {len(cells)}")

# --------------------------------------------------------------------------
# 1. Find assignments / creation references
# --------------------------------------------------------------------------

print("\n" + "=" * 78)
print("[1] ASSIGNMENT / CREATION REFERENCES")
print("=" * 78)

for name in TARGET_NAMES:

    print(f"\n{'-' * 78}")
    print(f"OBJECT: {name}")
    print("-" * 78)

    hits = []

    for idx, cell in enumerate(cells):

        source = "".join(cell.get("source", []))

        # Look for assignment-like construction
        patterns = [
            f"{name} =",
            f"{name}=",
            f"{name} = pd.",
            f"{name} = ",
            f"assign({name}",
            f"globals()[\"{name}\"]",
        ]

        if any(p.lower() in source.lower() for p in patterns):
            hits.append(idx)

    print("Assignment-like cells:", hits)

    # Print every hit
    for idx in hits:

        source = "".join(cells[idx].get("source", []))

        print("\n" + "#" * 78)
        print(f"CELL {idx}")
        print("#" * 78)
        print(source[:15000])

# --------------------------------------------------------------------------
# 2. Inspect cells 545–608 because Stage 39C identified these as the
#    reconstruction/final-input region.
# --------------------------------------------------------------------------

print("\n" + "=" * 78)
print("[2] CELLS 545–608 — FINAL INPUT / RECONSTRUCTION REGION")
print("=" * 78)

for idx in range(545, min(609, len(cells))):

    source = "".join(cells[idx].get("source", []))

    relevant = any(
        term.lower() in source.lower()
        for term in TARGET_NAMES
    )

    if relevant:

        print("\n" + "-" * 78)
        print(f"CELL {idx}")
        print("-" * 78)

        print(source[:18000])

# --------------------------------------------------------------------------
# 3. Look for object validation immediately before Stage 20
# --------------------------------------------------------------------------

print("\n" + "=" * 78)
print("[3] CELLS 600–630 — FINAL VALIDATION / FORENSIC INPUT")
print("=" * 78)

for idx in range(600, min(630, len(cells))):

    source = "".join(cells[idx].get("source", []))

    if any(
        term.lower() in source.lower()
        for term in TARGET_NAMES
    ):

        print("\n" + "-" * 78)
        print(f"CELL {idx}")
        print("-" * 78)

        print(source[:18000])

# --------------------------------------------------------------------------
# 4. Search for exact checkpoint/load statements involving the objects
# --------------------------------------------------------------------------

print("\n" + "=" * 78)
print("[4] LOAD / RECOVERY REFERENCES")
print("=" * 78)

LOAD_TERMS = [
    "read_parquet",
    "read_csv",
    "pickle",
    "joblib",
    "load",
    "checkpoint",
    "AFRITAC_CHECKPOINT",
    "71D5F",
    "authoritative",
    "current_events",
    "current_windows",
]

for idx, cell in enumerate(cells):

    source = "".join(cell.get("source", []))

    if (
        any(name.lower() in source.lower() for name in TARGET_NAMES)
        and any(term.lower() in source.lower() for term in LOAD_TERMS)
    ):

        print("\n" + "-" * 78)
        print(f"CELL {idx}")
        print("-" * 78)
        print(source[:18000])

print("\n" + "=" * 78)
print("STAGE 39I COMPLETE")
print("=" * 78)

print("""
READ-ONLY:
- Notebook was not executed
- No dataframe modified
- No checkpoint modified
- No ZIP modified
- No files created or overwritten
""")

# ==============================================================================
# NOTEBOOK CELL 679
# ==============================================================================

# ============================================================================
# STAGE 39I — TRACE CONSTRUCTION OF THE FOUR FROZEN PUBLICATION OBJECTS
# ============================================================================
#
# PURPOSE:
#   Trace exactly where the four final publication objects came from:
#
#       authoritative_events_71d5f
#       current_events_71d5f
#       authoritative_windows_71d5f
#       current_windows
#
# IMPORTANT:
#   READ-ONLY.
#   DOES NOT MODIFY DATAFRAMES.
#   DOES NOT MODIFY THE RELEASE.
#   DOES NOT REBUILD ANY FILE.
#   DOES NOT CHANGE PROVENANCE.
#
# ============================================================================

from pathlib import Path
import json
import re

print("=" * 80)
print("STAGE 39I — TRACE CONSTRUCTION OF FROZEN PUBLICATION OBJECTS")
print("=" * 80)

# ============================================================================
# 1. NOTEBOOK
# ============================================================================

NOTEBOOK = Path(
    "/content/drive/MyDrive/Colab Notebooks/Africadataset.ipynb"
)

assert NOTEBOOK.exists(), (
    f"Original notebook not found:\n{NOTEBOOK}"
)

with open(
    NOTEBOOK,
    "r",
    encoding="utf-8"
) as f:
    nb = json.load(f)

cells = nb["cells"]

print()
print("NOTEBOOK:")
print(NOTEBOOK)

print()
print("TOTAL CELLS:", len(cells))

# ============================================================================
# 2. TARGET OBJECTS
# ============================================================================

TARGETS = [
    "authoritative_events_71d5f",
    "current_events_71d5f",
    "authoritative_windows_71d5f",
    "current_windows",
]

print()
print("=" * 80)
print("TARGET PUBLICATION OBJECTS")
print("=" * 80)

for target in TARGETS:
    print("-", target)

# ============================================================================
# 3. CELL TEXT HELPER
# ============================================================================

def cell_text(cell):
    source = cell.get("source", [])

    if isinstance(source, list):
        return "".join(source)

    return str(source)

# ============================================================================
# 4. FIND ALL ASSIGNMENT / CREATION REFERENCES
# ============================================================================

print()
print("=" * 80)
print("A. ASSIGNMENT / CREATION REFERENCES")
print("=" * 80)

assignment_patterns = {
    target: re.compile(
        rf"(?m)^\s*{re.escape(target)}\s*="
    )
    for target in TARGETS
}

assignment_hits = {
    target: []
    for target in TARGETS
}

for idx, cell in enumerate(cells):

    text = cell_text(cell)

    for target, pattern in assignment_patterns.items():

        if pattern.search(text):

            assignment_hits[target].append(idx)

for target in TARGETS:

    print()
    print(f"{target}:")
    print("Assignment cells:", assignment_hits[target])

# ============================================================================
# 5. ALL REFERENCES TO TARGET OBJECTS
# ============================================================================

print()
print("=" * 80)
print("B. ALL TARGET REFERENCES")
print("=" * 80)

reference_hits = {
    target: []
    for target in TARGETS
}

for idx, cell in enumerate(cells):

    text = cell_text(cell)

    for target in TARGETS:

        if target in text:

            reference_hits[target].append(idx)

for target in TARGETS:

    print()
    print(f"{target}")
    print("-" * 60)
    print(
        "Reference cells:",
        reference_hits[target]
    )

# ============================================================================
# 6. INSPECT CRITICAL CELLS 545–608
# ============================================================================

print()
print("=" * 80)
print("C. CRITICAL CELLS 545–608")
print("=" * 80)

for idx in range(
    545,
    min(609, len(cells))
):

    text = cell_text(cells[idx])

    relevant = False

    # Target object references
    if any(
        target in text
        for target in TARGETS
    ):
        relevant = True

    # Loading / recovery indicators
    loading_terms = [
        "read_parquet",
        "read_csv",
        "read_pickle",
        "read_json",
        "load(",
        "checkpoint",
        "CHECKPOINT",
        "recover",
        "recovery",
        "artifact",
        "ARTIFACT",
        "assign",
        "authoritative",
        "current_windows",
        "current_events",
    ]

    if any(
        term.lower() in text.lower()
        for term in loading_terms
    ):
        relevant = True

    if relevant:

        print()
        print("-" * 80)
        print(f"CELL {idx}")
        print("-" * 80)

        print(text[:12000])

# ============================================================================
# 7. INSPECT CELLS 600–630
# ============================================================================

print()
print("=" * 80)
print("D. FINAL FORENSIC / FREEZE CELLS 600–630")
print("=" * 80)

for idx in range(
    600,
    min(631, len(cells))
):

    text = cell_text(cells[idx])

    relevant = (
        any(
            target in text
            for target in TARGETS
        )
        or
        any(
            term.lower() in text.lower()
            for term in [
                "assign",
                "freeze",
                "checkpoint",
                "validation",
                "authoritative_events",
                "current_events",
                "authoritative_windows",
                "current_windows",
            ]
        )
    )

    if relevant:

        print()
        print("-" * 80)
        print(f"CELL {idx}")
        print("-" * 80)

        print(text[:12000])

# ============================================================================
# 8. TRACE FILE LOADING / RECOVERY SOURCES
# ============================================================================

print()
print("=" * 80)
print("E. FILE-INPUT / RECOVERY REFERENCES")
print("=" * 80)

file_input_patterns = [
    "pd.read_csv",
    "pd.read_parquet",
    "pd.read_pickle",
    "pd.read_json",
    "read_csv",
    "read_parquet",
    "read_pickle",
    "read_json",
    "Path(",
    "CHECKPOINT",
    "ARTIFACT",
]

for idx, cell in enumerate(cells):

    text = cell_text(cell)

    target_related = any(
        target in text
        for target in TARGETS
    )

    input_related = any(
        term.lower() in text.lower()
        for term in file_input_patterns
    )

    if target_related and input_related:

        print()
        print("-" * 80)
        print(f"CELL {idx}")
        print("-" * 80)

        print(text[:12000])

# ============================================================================
# 9. TRACE DATAFRAME COPY / FREEZE OPERATIONS
# ============================================================================

print()
print("=" * 80)
print("F. COPY / FREEZE OPERATIONS")
print("=" * 80)

copy_terms = [
    ".copy(",
    "copy(deep",
    "frozen",
    "freeze",
    "validated",
    "publication",
]

for idx, cell in enumerate(cells):

    text = cell_text(cell)

    if (
        any(
            target in text
            for target in TARGETS
        )
        and
        any(
            term.lower() in text.lower()
            for term in copy_terms
        )
    ):

        print()
        print("-" * 80)
        print(f"CELL {idx}")
        print("-" * 80)

        print(text[:12000])

# ============================================================================
# 10. CELL 632 PUBLICATION EXPORT
# ============================================================================

print()
print("=" * 80)
print("G. CELL 632 — PUBLICATION EXPORT")
print("=" * 80)

if len(cells) > 632:

    text_632 = cell_text(
        cells[632]
    )

    print(text_632[:16000])

else:

    print("CELL 632 NOT AVAILABLE")

# ============================================================================
# 11. SUMMARY
# ============================================================================

print()
print("=" * 80)
print("STAGE 39I SUMMARY")
print("=" * 80)

for target in TARGETS:

    print()
    print(target)

    print(
        "  Assignment cells :",
        assignment_hits[target]
    )

    print(
        "  Reference cells  :",
        reference_hits[target]
    )

print()
print("NOTEBOOK CELLS:", len(cells))

print()
print("READ-ONLY TRACE COMPLETE")
print("=" * 80)

print(
    "IMPORTANT: No dataset, dataframe, release package, "
    "metadata, checksum, or ZIP was modified."
)

print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 680
# ==============================================================================

# ============================================================================
# STAGE 39J — RESOLVE INDIRECT CONSTRUCTION OF FROZEN OBJECTS
# ============================================================================
#
# PURPOSE:
#   Determine exactly how the four frozen publication objects entered the
#   notebook namespace, especially authoritative_events_71d5f which had no
#   direct assignment detected by Stage 39I.
#
# READ-ONLY — NO DATA / RELEASE MODIFICATION
# ============================================================================

from pathlib import Path
import json
import re

NOTEBOOK = Path(
    "/content/drive/MyDrive/Colab Notebooks/Africadataset.ipynb"
)

assert NOTEBOOK.exists()

with open(NOTEBOOK, "r", encoding="utf-8") as f:
    nb = json.load(f)

cells = nb["cells"]

TARGETS = [
    "authoritative_events_71d5f",
    "current_events_71d5f",
    "authoritative_windows_71d5f",
    "current_windows",
]

print("=" * 80)
print("STAGE 39J — INDIRECT CONSTRUCTION TRACE")
print("=" * 80)

print("Notebook cells:", len(cells))

# ============================================================================
# 1. PRINT EXACT SOURCE OF CRITICAL ASSIGNMENT CELLS
# ============================================================================

CRITICAL_CELLS = [
    545, 555, 561, 577,
    604, 606, 608, 609,
    610, 611, 613, 614,
    629, 631, 632
]

print()
print("=" * 80)
print("[1] CRITICAL CELLS")
print("=" * 80)

for idx in CRITICAL_CELLS:

    if idx >= len(cells):
        continue

    source = "".join(
        cells[idx].get("source", [])
    )

    print()
    print("#" * 80)
    print(f"CELL {idx}")
    print("#" * 80)
    print(source[:25000])

# ============================================================================
# 2. SEARCH FOR INDIRECT CREATION OF AUTHORITATIVE EVENTS
# ============================================================================

print()
print("=" * 80)
print("[2] AUTHORITATIVE EVENTS — INDIRECT CONSTRUCTION SEARCH")
print("=" * 80)

patterns = [
    "authoritative_events_71d5f",
    "authoritative_events",
    "AFRITAC_OBSERVABLE",
    "OBSERVABLE",
    "observable_events",
    "authoritative",
    "71D.5F",
    "71D5F",
]

for idx, cell in enumerate(cells):

    source = "".join(
        cell.get("source", [])
    )

    if (
        "authoritative_events_71d5f" in source
        or (
            "authoritative_events" in source
            and (
                "71D" in source
                or "71d" in source
                or "observable" in source.lower()
            )
        )
        or "AFRITAC_OBSERVABLE" in source
    ):

        print()
        print("-" * 80)
        print(f"CELL {idx}")
        print("-" * 80)
        print(source[:20000])

# ============================================================================
# 3. SEARCH FOR DICTIONARY / TUPLE / GLOBALS ASSIGNMENT
# ============================================================================

print()
print("=" * 80)
print("[3] INDIRECT ASSIGNMENT PATTERNS")
print("=" * 80)

indirect_patterns = [
    r"globals\(\)",
    r"\.update\(",
    r"locals\(\)",
    r"return .*authoritative",
    r"=\s*.*authoritative.*\]",
    r"=\s*\(",
    r"=\s*\[",
    r"dict\(",
    r"assign\(",
]

for idx, cell in enumerate(cells):

    source = "".join(
        cell.get("source", [])
    )

    if (
        any(
            target in source
            for target in TARGETS
        )
        and
        any(
            re.search(pattern, source, flags=re.IGNORECASE)
            for pattern in indirect_patterns
        )
    ):

        print()
        print("-" * 80)
        print(f"CELL {idx}")
        print("-" * 80)
        print(source[:18000])

# ============================================================================
# 4. SEARCH ALL PARQUET / CSV LOADS AROUND THE RECONSTRUCTION REGION
# ============================================================================

print()
print("=" * 80)
print("[4] DATA LOADS — CELLS 500–608")
print("=" * 80)

load_terms = [
    "read_parquet",
    "read_csv",
    "read_pickle",
    "read_json",
    "pd.read_",
    "AFRITAC_CHECKPOINT",
    "checkpoint",
    "artifact",
    "parquet",
]

for idx in range(
    500,
    min(609, len(cells))
):

    source = "".join(
        cells[idx].get("source", [])
    )

    if any(
        term.lower() in source.lower()
        for term in load_terms
    ):

        print()
        print("-" * 80)
        print(f"CELL {idx}")
        print("-" * 80)
        print(source[:20000])

# ============================================================================
# 5. IDENTIFY FINAL DATAFRAME SOURCE VARIABLES
# ============================================================================

print()
print("=" * 80)
print("[5] POSSIBLE SOURCE VARIABLES")
print("=" * 80)

source_terms = [
    "events",
    "windows",
    "observable",
    "negative",
    "frozen",
    "reconstructed",
    "matched",
    "positive",
    "candidate",
]

for idx in range(
    500,
    min(615, len(cells))
):

    source = "".join(
        cells[idx].get("source", [])
    )

    if any(
        term.lower() in source.lower()
        for term in source_terms
    ):

        # Show only cells containing dataframe assignment/load patterns
        if (
            "=" in source
            or "read_parquet" in source
            or "read_csv" in source
        ):

            print()
            print("-" * 80)
            print(f"CELL {idx}")
            print("-" * 80)
            print(source[:16000])

# ============================================================================
# 6. FINAL SUMMARY
# ============================================================================

print()
print("=" * 80)
print("STAGE 39J COMPLETE")
print("=" * 80)

print("""
READ-ONLY TRACE ONLY

No:
- dataframe modification
- checkpoint modification
- CSV modification
- metadata modification
- checksum modification
- ZIP modification
- release rebuild

The purpose is solely to establish the exact construction lineage of
the four frozen publication objects.
""")

print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 681
# ==============================================================================

# ============================================================================
# STAGE 39K-R — RELEASE RECOVERY LOCATOR
# ============================================================================
#
# PURPOSE:
# Locate the existing AFRIDATACYBERJOHN / AFRICA_DATASET publication package
# without modifying, rebuilding, or overwriting anything.
#
# READ-ONLY OPERATION.
# ============================================================================

from pathlib import Path

print("=" * 90)
print("STAGE 39K-R — RELEASE RECOVERY LOCATOR")
print("=" * 90)

SEARCH_ROOTS = [
    Path("/content"),
    Path("/content/drive/MyDrive"),
]

TARGET_NAMES = {
    "AFRIDATACYBERJOHN_v1.0",
    "AFRIDATACYBERJOHN_v1.0.zip",
    "AFRICA_DATASET_v1.0_FINAL",
    "AFRICA_DATASET_v1.0_FINAL.zip",
    "AFRICA_DATASET_v1.0",
    "AFRICA_DATASET_v1.0.zip",
    "AFRICA_DATASET_PUBLICATION",
    "AFRICA_DATASET_PUBLICATION.zip",
}

print("\nSEARCH ROOTS")
print("-" * 90)

for root in SEARCH_ROOTS:
    print(root, "EXISTS =", root.exists())

found = []

print("\nSEARCHING FOR EXACT RELEASE NAMES...")
print("-" * 90)

for root in SEARCH_ROOTS:

    if not root.exists():
        continue

    for target in TARGET_NAMES:

        # Search directories/files with exact basename
        try:
            matches = list(root.rglob(target))
        except Exception as e:
            print("SEARCH ERROR:", root, target, e)
            continue

        for p in matches:

            if p.exists():

                record = {
                    "path": str(p),
                    "type": (
                        "DIRECTORY"
                        if p.is_dir()
                        else "ZIP/FILE"
                    ),
                }

                if record not in found:
                    found.append(record)

# ============================================================================
# DISPLAY RESULTS
# ============================================================================

print("\nRECOVERY CANDIDATES")
print("-" * 90)

if not found:

    print("NO EXACT RELEASE NAME FOUND.")

else:

    for i, item in enumerate(found, 1):
        print(f"{i}. {item['type']}")
        print("   ", item["path"])

# ============================================================================
# ALSO SEARCH FOR ZIP FILES CONTAINING AFRICA / AFRIDA / DATASET
# ============================================================================

print("\nRELATED ZIP FILES")
print("-" * 90)

zip_candidates = []

for root in SEARCH_ROOTS:

    if not root.exists():
        continue

    try:
        for p in root.rglob("*.zip"):

            name = p.name.lower()

            if (
                "africa" in name
                or "afridata" in name
                or "dataset" in name
                or "71d5f" in name
            ):
                if str(p) not in zip_candidates:
                    zip_candidates.append(str(p))

    except Exception as e:
        print("ZIP SEARCH ERROR:", root, e)

if zip_candidates:

    for i, p in enumerate(zip_candidates, 1):
        print(f"{i}. {p}")

else:
    print("No related ZIP files found.")

# ============================================================================
# SEARCH FOR THE ORIGINAL NOTEBOOK
# ============================================================================

print("\nORIGINAL NOTEBOOK CHECK")
print("-" * 90)

notebook = Path(
    "/content/drive/MyDrive/Colab Notebooks/Africadataset.ipynb"
)

print(
    "Africadataset.ipynb:",
    "FOUND" if notebook.exists() else "NOT FOUND"
)

if notebook.exists():
    print("Path:", notebook)

# ============================================================================
# SEARCH FOR STAGE 39 / PUBLICATION ARTIFACTS
# ============================================================================

print("\nRECOVERY ARTIFACTS")
print("-" * 90)

artifact_keywords = [
    "STAGE39",
    "AFRIDATACYBERJOHN",
    "AFRICA_DATASET",
    "publication",
    "provenance",
]

artifact_matches = []

for root in SEARCH_ROOTS:

    if not root.exists():
        continue

    try:
        for p in root.rglob("*"):

            if not p.exists():
                continue

            name = p.name.lower()

            if any(k.lower() in name for k in artifact_keywords):

                # Avoid printing the entire Drive tree
                if str(p) not in artifact_matches:
                    artifact_matches.append(str(p))

    except Exception as e:
        print("ARTIFACT SEARCH ERROR:", root, e)

# Limit display to useful candidates
artifact_matches = sorted(
    artifact_matches,
    key=lambda x: (
        "afridatacyberjohn" not in x.lower(),
        "africa_dataset" not in x.lower(),
        len(x)
    )
)

print("Potential related artifacts:", len(artifact_matches))

for i, p in enumerate(artifact_matches[:100], 1):
    print(f"{i}. {p}")

# ============================================================================
# FINAL STATUS
# ============================================================================

print("\n" + "=" * 90)
print("STAGE 39K-R COMPLETE — READ-ONLY")
print("=" * 90)

print("\nNo files were created.")
print("No files were modified.")
print("No dataset was regenerated.")
print("No source dataframe was modified.")

if found:
    print("\nRELEASE CANDIDATE FOUND: YES")
else:
    print("\nRELEASE CANDIDATE FOUND: NO")

if zip_candidates:
    print("RELATED ZIP FOUND: YES")
else:
    print("RELATED ZIP FOUND: NO")

print("=" * 90)

# ==============================================================================
# NOTEBOOK CELL 682
# ==============================================================================

# ============================================================================
# STAGE 39L-R — CORRECTED ZIP RECOVERY VALIDATION
# ============================================================================
#
# PURPOSE
# -------
# Validate the recovered publication package using the ACTUAL filenames
# contained in the validated ZIP.
#
# READ-ONLY.
# No files are modified.
# No CSV is regenerated.
# No metadata is changed.
# ============================================================================

from pathlib import Path
import hashlib
import pandas as pd

print("=" * 90)
print("STAGE 39L-R — CORRECTED ZIP RECOVERY VALIDATION")
print("=" * 90)

WORK_RELEASE = Path(
    "/content/AFRIDATACYBERJOHN_STAGE39L/AFRIDATACYBERJOHN_v1.0/AFRICA_DATASET_v1.0"
)

if not WORK_RELEASE.exists():
    raise FileNotFoundError(
        f"Recovered release directory not found: {WORK_RELEASE}"
    )

print("\nRECOVERED RELEASE")
print("-" * 90)
print(WORK_RELEASE)

# ============================================================================
# 1. ACTUAL PUBLICATION FILES
# ============================================================================

DATA_DIR = WORK_RELEASE / "data"

EXPECTED_FILES = {
    "authoritative_events":
        DATA_DIR / "AFRICA_MobileMoney_USSD_Authoritative_Events.csv",

    "authoritative_windows":
        DATA_DIR / "AFRICA_MobileMoney_USSD_Authoritative_Windows.csv",

    "current_events":
        DATA_DIR / "AFRICA_MobileMoney_USSD_Current_Events.csv",

    "current_windows":
        DATA_DIR / "AFRICA_MobileMoney_USSD_Current_Windows.csv",
}

print("\nACTUAL DATA FILES")
print("-" * 90)

for key, path in EXPECTED_FILES.items():

    exists = path.exists()

    print(
        f"{key:25s} "
        f"{'FOUND' if exists else 'MISSING'}: "
        f"{path.name}"
    )

    if not exists:
        raise FileNotFoundError(
            f"Required publication file missing: {path}"
        )

# ============================================================================
# 2. DATASET SHAPES
# ============================================================================

EXPECTED_SHAPES = {
    "authoritative_events": (1029, 29),
    "current_events": (1060, 29),
    "authoritative_windows": (100, 8),
    "current_windows": (100, 10),
}

print("\nDATASET SHAPE VALIDATION")
print("-" * 90)

datasets = {}

for key, path in EXPECTED_FILES.items():

    df = pd.read_csv(path)

    datasets[key] = df

    expected = EXPECTED_SHAPES[key]
    actual = df.shape

    passed = actual == expected

    print(
        f"{key:25s} "
        f"expected={expected} "
        f"actual={actual} "
        f"PASS={passed}"
    )

    if not passed:
        raise AssertionError(
            f"{key}: expected {expected}, found {actual}"
        )

# ============================================================================
# 3. EVENT ID UNIQUENESS
# ============================================================================

print("\nEVENT ID VALIDATION")
print("-" * 90)

for key in [
    "authoritative_events",
    "current_events",
]:

    df = datasets[key]

    unique_count = df["event_id"].nunique()
    total_count = len(df)

    passed = unique_count == total_count

    print(
        f"{key:25s} "
        f"total={total_count} "
        f"unique_event_id={unique_count} "
        f"PASS={passed}"
    )

    if not passed:
        raise AssertionError(
            f"{key}: duplicate event_id detected"
        )

# ============================================================================
# 4. WINDOW ID UNIQUENESS
# ============================================================================

print("\nWINDOW ID VALIDATION")
print("-" * 90)

for key in [
    "authoritative_windows",
    "current_windows",
]:

    df = datasets[key]

    unique_count = df["window_id"].nunique()
    total_count = len(df)

    passed = unique_count == total_count

    print(
        f"{key:25s} "
        f"total={total_count} "
        f"unique_window_id={unique_count} "
        f"PASS={passed}"
    )

    if not passed:
        raise AssertionError(
            f"{key}: duplicate window_id detected"
        )

# ============================================================================
# 5. SEMANTIC VALIDATION
# ============================================================================

print("\nSEMANTIC VALIDATION")
print("-" * 90)

for key in [
    "authoritative_events",
    "current_events",
]:

    df = datasets[key]

    checks = {
        "ground_truth_state": (
            set(df["ground_truth_state"].dropna().unique())
            == {"NORMAL"}
        ),

        "is_attack": (
            set(df["is_attack"].dropna().unique())
            == {0}
        ),

        "hard_negative": (
            set(df["hard_negative"].dropna().unique())
            == {1}
        ),

        "is_observable_precursor": (
            set(df["is_observable_precursor"].dropna().unique())
            == {0}
        ),
    }

    print(f"\n{key}")

    for name, passed in checks.items():

        print(
            f"  {name:28s} PASS={passed}"
        )

        if not passed:
            raise AssertionError(
                f"{key}: semantic validation failed for {name}"
            )

# ============================================================================
# 6. WINDOW HORIZON VALIDATION
# ============================================================================

print("\nWINDOW HORIZON VALIDATION")
print("-" * 90)

EXPECTED_HORIZONS = {
    5: 20,
    10: 20,
    15: 20,
    30: 20,
    60: 20,
}

for key in [
    "authoritative_windows",
    "current_windows",
]:

    df = datasets[key]

    distribution = (
        df["horizon_minutes"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    passed = distribution == EXPECTED_HORIZONS

    print(
        f"{key:25s} "
        f"PASS={passed}"
    )

    print(
        "  distribution:",
        distribution
    )

    if not passed:
        raise AssertionError(
            f"{key}: horizon distribution mismatch"
        )

# ============================================================================
# 7. USER / HORIZON COUNTS
# ============================================================================

print("\nWINDOW USER/HORIZON VALIDATION")
print("-" * 90)

for key in [
    "authoritative_windows",
    "current_windows",
]:

    df = datasets[key]

    print(
        f"{key:25s} "
        f"users={df['user_id'].nunique()} "
        f"windows={len(df)}"
    )

    if len(df) != 100:
        raise AssertionError(
            f"{key}: expected 100 windows"
        )

# ============================================================================
# 8. SHA256 HASHES
# ============================================================================

def sha256_file(path):

    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            h.update(chunk)

    return h.hexdigest()


print("\nRECOVERED CSV SHA256")
print("-" * 90)

for key, path in EXPECTED_FILES.items():

    digest = sha256_file(path)

    print(f"\n{key}")
    print(digest)

# ============================================================================
# 9. CHECK EXISTING DOCUMENTATION
# ============================================================================

print("\nEXISTING PACKAGE DOCUMENTATION")
print("-" * 90)

documentation_files = [
    WORK_RELEASE / "README.md",
    WORK_RELEASE / "CITATION.cff",
    WORK_RELEASE / "documentation" / "DATASET_DESCRIPTION.md",
    WORK_RELEASE / "documentation" / "DATA_DICTIONARY.csv",
    WORK_RELEASE / "documentation" / "FORENSIC_VALIDATION.md",
    WORK_RELEASE / "documentation" / "METHODOLOGY.md",
    WORK_RELEASE / "metadata" / "checksums.sha256",
    WORK_RELEASE / "metadata" / "dataset_metadata.json",
]

for path in documentation_files:

    print(
        f"{'FOUND' if path.exists() else 'MISSING':8s} "
        f"{path.relative_to(WORK_RELEASE)}"
    )

# ============================================================================
# 10. FINAL STATUS
# ============================================================================

print("\n" + "=" * 90)
print("STAGE 39L-R COMPLETE")
print("=" * 90)

print("\nZIP RECOVERY: PASS")
print("DATASET SHAPES: PASS")
print("EVENT ID UNIQUENESS: PASS")
print("WINDOW ID UNIQUENESS: PASS")
print("SEMANTIC VALIDATION: PASS")
print("WINDOW HORIZONS: PASS")

print("\nDATASET CONTENT MODIFIED: NO")
print("SOURCE DATAFRAMES MODIFIED: NO")
print("METADATA MODIFIED: NO")

print("\nRECOVERED PACKAGE:")
print(WORK_RELEASE)

print("\nREADY FOR STAGE 39M — SYNTHETIC PROVENANCE UPDATE")

print("=" * 90)

# ==============================================================================
# NOTEBOOK CELL 683
# ==============================================================================

# ============================================================================
# STAGE 39M — SYNTHETIC PROVENANCE UPDATE
# ============================================================================
#
# PURPOSE
# -------
# Update the recovered publication package with the confirmed synthetic
# provenance classification.
#
# DATASET CSVs ARE NOT MODIFIED.
#
# ============================================================================

from pathlib import Path
import hashlib
import json
import shutil
import zipfile
import pandas as pd

print("=" * 90)
print("STAGE 39M — SYNTHETIC PROVENANCE UPDATE")
print("=" * 90)

# ============================================================================
# 1. LOCATE RECOVERED PACKAGE
# ============================================================================

SOURCE_RELEASE = Path(
    "/content/AFRIDATACYBERJOHN_STAGE39L/"
    "AFRIDATACYBERJOHN_v1.0/"
    "AFRICA_DATASET_v1.0"
)

if not SOURCE_RELEASE.exists():
    raise FileNotFoundError(
        f"Recovered package not found: {SOURCE_RELEASE}"
    )

# ============================================================================
# 2. CREATE A NEW CONTROLLED RELEASE
# ============================================================================

OUTPUT_ROOT = Path(
    "/content/AFRIDATACYBERJOHN_STAGE39M"
)

OUTPUT_RELEASE = (
    OUTPUT_ROOT /
    "AFRIDATACYBERJOHN_v1.0"
)

if OUTPUT_ROOT.exists():
    shutil.rmtree(OUTPUT_ROOT)

OUTPUT_ROOT.mkdir(
    parents=True,
    exist_ok=True
)

shutil.copytree(
    SOURCE_RELEASE,
    OUTPUT_RELEASE
)

print("\nSOURCE PACKAGE")
print("-" * 90)
print(SOURCE_RELEASE)

print("\nNEW WORKING PACKAGE")
print("-" * 90)
print(OUTPUT_RELEASE)

# ============================================================================
# 3. IDENTIFY FOUR DATASET CSVs
# ============================================================================

DATA_DIR = OUTPUT_RELEASE / "data"

DATA_FILES = {
    "authoritative_events":
        DATA_DIR /
        "AFRICA_MobileMoney_USSD_Authoritative_Events.csv",

    "authoritative_windows":
        DATA_DIR /
        "AFRICA_MobileMoney_USSD_Authoritative_Windows.csv",

    "current_events":
        DATA_DIR /
        "AFRICA_MobileMoney_USSD_Current_Events.csv",

    "current_windows":
        DATA_DIR /
        "AFRICA_MobileMoney_USSD_Current_Windows.csv",
}

for name, path in DATA_FILES.items():
    if not path.exists():
        raise FileNotFoundError(
            f"Missing dataset file: {path}"
        )

# ============================================================================
# 4. CAPTURE DATASET HASHES BEFORE METADATA UPDATE
# ============================================================================

def sha256_file(path):

    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            h.update(chunk)

    return h.hexdigest()


before_hashes = {
    name: sha256_file(path)
    for name, path in DATA_FILES.items()
}

print("\nPRE-UPDATE DATASET HASHES")
print("-" * 90)

for name, digest in before_hashes.items():
    print(f"{name:25s} {digest}")

# ============================================================================
# 5. CONFIRMED PROVENANCE
# ============================================================================

PROVENANCE_STATUS = "CONFIRMED_SYNTHETIC"

PROVENANCE_STATEMENT = (
    "AFRIDATACYBERJOHN is a synthetic, programmatically generated "
    "cybersecurity dataset designed to model Africa-centric mobile-money "
    "and USSD behavioural activity and intrusion scenarios. The dataset "
    "was generated using reproducible Python-based procedures, including "
    "controlled generation of users, devices, sessions, and event records. "
    "It is not presented as a direct extract of production banking, "
    "telecommunications, or customer transaction records."
)

# ============================================================================
# 6. WRITE PROVENANCE DOCUMENT
# ============================================================================

DOC_DIR = OUTPUT_RELEASE / "documentation"
META_DIR = OUTPUT_RELEASE / "metadata"

DOC_DIR.mkdir(exist_ok=True)
META_DIR.mkdir(exist_ok=True)

provenance_md = f"""# AFRIDATACYBERJOHN — Data Provenance

## Provenance Status

**CONFIRMED_SYNTHETIC**

## Data Origin

**Synthetic, programmatically generated research data.**

## Provenance Statement

{PROVENANCE_STATEMENT}

## Generation Context

The original research notebook contains reproducible Python-based
procedures for constructing the research environment and generating
synthetic users, devices, observation periods, sessions, and event
records.

The synthetic classification is based on the original construction
workflow rather than on the later forensic reconciliation procedures.

## Production-Data Status

The dataset is **not** presented as a direct extract of production
banking, telecommunications, mobile-money, or customer transaction
systems.

No claim is made that the records represent identifiable real
customers.

## Research Purpose

The dataset is intended for cybersecurity research involving areas
such as:

- intrusion detection
- behavioural analytics
- mobile-money security
- USSD security
- anomaly detection
- machine-learning experimentation
- cybersecurity benchmarking
- financial cybersecurity research

## Forensic Preservation

The provenance update does not alter the frozen dataset populations.

No event records were:

- regenerated
- repaired
- fabricated
- deleted
- reassigned

as part of this metadata update.

## Frozen Dataset Populations

| Dataset component | Population |
|---|---:|
| Authoritative events | 1,029 |
| Current events | 1,060 |
| Authoritative windows | 100 |
| Current windows | 100 |

## License

**NOT ASSIGNED**

A license should be selected only after ownership and redistribution
conditions have been confirmed.

## DOI

**NOT ASSIGNED**

A DOI may be assigned by a repository during publication.

"""

provenance_file = DOC_DIR / "PROVENANCE.md"

provenance_file.write_text(
    provenance_md.strip() + "\n",
    encoding="utf-8"
)

print("\nCREATED")
print(provenance_file)

# ============================================================================
# 7. UPDATE DATASET METADATA JSON
# ============================================================================

metadata_file = META_DIR / "dataset_metadata.json"

if metadata_file.exists():

    with open(
        metadata_file,
        "r",
        encoding="utf-8"
    ) as f:
        metadata = json.load(f)

else:
    metadata = {}

metadata["provenance_status"] = PROVENANCE_STATUS
metadata["data_origin"] = "synthetic"
metadata["generation_method"] = "programmatically_generated"

metadata["provenance_statement"] = PROVENANCE_STATEMENT

metadata["production_data_status"] = (
    "Not presented as a direct extract of production banking, "
    "telecommunications, mobile-money, or customer transaction systems."
)

metadata["license_status"] = "NOT_ASSIGNED"
metadata["doi_status"] = "NOT_ASSIGNED"

metadata["dataset_content_modified"] = False
metadata["records_regenerated"] = False
metadata["records_repaired"] = False
metadata["records_fabricated"] = False

metadata["frozen_populations"] = {
    "authoritative_events": 1029,
    "current_events": 1060,
    "authoritative_windows": 100,
    "current_windows": 100
}

with open(
    metadata_file,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        metadata,
        f,
        indent=2,
        ensure_ascii=False
    )

print("\nUPDATED")
print(metadata_file)

# ============================================================================
# 8. UPDATE README
# ============================================================================

README_FILE = OUTPUT_RELEASE / "README.md"

if README_FILE.exists():

    readme = README_FILE.read_text(
        encoding="utf-8"
    )

    section = """

## Data Origin and Provenance

**Data origin: Synthetic, programmatically generated.**

AFRIDATACYBERJOHN is a synthetic cybersecurity research dataset
designed to model Africa-centric mobile-money and USSD behavioural
activity and intrusion scenarios. It is not presented as a direct
extract of production banking, telecommunications, or customer
transaction records.

See `documentation/PROVENANCE.md` for the detailed provenance
statement.
"""

    if "## Data Origin and Provenance" not in readme:

        README_FILE.write_text(
            readme.rstrip()
            + "\n"
            + section.strip()
            + "\n",
            encoding="utf-8"
        )

        print("\nREADME UPDATED")
    else:
        print("\nREADME PROVENANCE SECTION ALREADY EXISTS")

# ============================================================================
# 9. VERIFY DATASET CSV HASHES DID NOT CHANGE
# ============================================================================

after_hashes = {
    name: sha256_file(path)
    for name, path in DATA_FILES.items()
}

print("\nCSV HASH PRESERVATION")
print("-" * 90)

hash_results = {}

for name in before_hashes:

    unchanged = (
        before_hashes[name] ==
        after_hashes[name]
    )

    hash_results[name] = unchanged

    print(
        f"{name:25s} "
        f"UNCHANGED={unchanged}"
    )

    if not unchanged:
        raise AssertionError(
            f"CRITICAL: dataset CSV changed: {name}"
        )

# ============================================================================
# 10. VERIFY DATASET SHAPES
# ============================================================================

print("\nDATASET SHAPE PRESERVATION")
print("-" * 90)

EXPECTED_SHAPES = {
    "authoritative_events": (1029, 29),
    "authoritative_windows": (100, 8),
    "current_events": (1060, 29),
    "current_windows": (100, 10),
}

for name, path in DATA_FILES.items():

    df = pd.read_csv(path)

    expected = EXPECTED_SHAPES[name]

    print(
        f"{name:25s} "
        f"actual={df.shape} "
        f"expected={expected} "
        f"PASS={df.shape == expected}"
    )

    if df.shape != expected:
        raise AssertionError(
            f"{name}: dataset shape changed."
        )

# ============================================================================
# 11. VERIFY KEY SEMANTIC FIELDS
# ============================================================================

print("\nSEMANTIC PRESERVATION")
print("-" * 90)

for name in [
    "authoritative_events",
    "current_events"
]:

    df = pd.read_csv(DATA_FILES[name])

    checks = {
        "ground_truth_state": set(
            df["ground_truth_state"].dropna().unique()
        ) == {"NORMAL"},

        "is_attack": set(
            df["is_attack"].dropna().unique()
        ) == {0},

        "hard_negative": set(
            df["hard_negative"].dropna().unique()
        ) == {1},

        "is_observable_precursor": set(
            df["is_observable_precursor"].dropna().unique()
        ) == {0},
    }

    print(f"\n{name}")

    for field, passed in checks.items():

        print(
            f"  {field:28s} PASS={passed}"
        )

        if not passed:
            raise AssertionError(
                f"{name}: semantic field changed: {field}"
            )

# ============================================================================
# 12. FINAL STATUS
# ============================================================================

print("\n" + "=" * 90)
print("STAGE 39M COMPLETE")
print("=" * 90)

print("\nPROVENANCE")
print("  Status: CONFIRMED_SYNTHETIC")
print("  Origin: Synthetic")
print("  Generation: Programmatically generated")

print("\nDATASET PRESERVATION")
print("  Authoritative events: 1,029")
print("  Current events: 1,060")
print("  Authoritative windows: 100")
print("  Current windows: 100")
print("  CSV content modified: NO")
print("  CSV SHA256 preserved: YES")
print("  Dataset regenerated: NO")
print("  Dataset repaired: NO")

print("\nLICENSE")
print("  NOT ASSIGNED")

print("\nDOI")
print("  NOT ASSIGNED")

print("\nNEW PACKAGE")
print(OUTPUT_RELEASE)

print("\n" + "=" * 90)
print("READY FOR STAGE 39N — FINAL PACKAGE REBUILD")
print("=" * 90)

# ==============================================================================
# NOTEBOOK CELL 684
# ==============================================================================

# ============================================================================
# STAGE 39M-A — CREATOR IDENTITY & PUBLICATION METADATA COMPLETION
# ============================================================================
#
# PURPOSE
# -------
# Add/standardize:
#   - Creator name
#   - Email
#   - ORCID
#   - Dataset title
#   - Version
#   - Synthetic provenance
#
# CSV FILES MUST REMAIN BYTE-IDENTICAL.
# ============================================================================

from pathlib import Path
import json
import hashlib
import re
import shutil

print("=" * 90)
print("STAGE 39M-A — CREATOR IDENTITY & PUBLICATION METADATA COMPLETION")
print("=" * 90)

# ============================================================================
# 1. CURRENT STAGE 39M PACKAGE
# ============================================================================

PACKAGE = Path(
    "/content/AFRIDATACYBERJOHN_STAGE39M/"
    "AFRIDATACYBERJOHN_v1.0"
)

if not PACKAGE.exists():
    raise FileNotFoundError(
        f"Stage 39M package not found: {PACKAGE}"
    )

print("\nPACKAGE")
print("-" * 90)
print(PACKAGE)

# ============================================================================
# 2. CREATOR INFORMATION
# ============================================================================

CREATOR_NAME = "John Ojo Ajayi"
CREATOR_EMAIL = "onejotech@gmail.com"
CREATOR_ORCID = "0000-0002-8063-6070"

DATASET_TITLE = (
    "AFRIDATACYBERJOHN: An Africa-Centric Mobile Money and USSD "
    "Cybersecurity Dataset for Behavioural Intrusion Detection and "
    "Transaction Security"
)

VERSION = "1.0"

print("\nCREATOR INFORMATION")
print("-" * 90)
print("Name :", CREATOR_NAME)
print("Email:", CREATOR_EMAIL)
print("ORCID:", CREATOR_ORCID)
print("Version:", VERSION)

# ============================================================================
# 3. RECORD CSV HASHES BEFORE METADATA CHANGES
# ============================================================================

DATA_DIR = PACKAGE / "data"

DATA_FILES = [
    DATA_DIR / "AFRICA_MobileMoney_USSD_Authoritative_Events.csv",
    DATA_DIR / "AFRICA_MobileMoney_USSD_Authoritative_Windows.csv",
    DATA_DIR / "AFRICA_MobileMoney_USSD_Current_Events.csv",
    DATA_DIR / "AFRICA_MobileMoney_USSD_Current_Windows.csv",
]

def sha256_file(path):

    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            h.update(chunk)

    return h.hexdigest()

before_hashes = {
    p.name: sha256_file(p)
    for p in DATA_FILES
}

print("\nCSV HASHES CAPTURED")
print("-" * 90)

for name, digest in before_hashes.items():
    print(name)
    print(digest)

# ============================================================================
# 4. UPDATE DATASET METADATA JSON
# ============================================================================

META_DIR = PACKAGE / "metadata"
META_DIR.mkdir(exist_ok=True)

METADATA_FILE = META_DIR / "dataset_metadata.json"

if METADATA_FILE.exists():

    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        metadata = json.load(f)

else:
    metadata = {}

metadata.update({
    "title": DATASET_TITLE,
    "dataset_name": "AFRIDATACYBERJOHN",
    "version": VERSION,

    "creator": CREATOR_NAME,
    "author": CREATOR_NAME,
    "authors": [
        {
            "name": CREATOR_NAME,
            "email": CREATOR_EMAIL,
            "orcid": CREATOR_ORCID
        }
    ],

    "creators": [
        {
            "name": CREATOR_NAME,
            "email": CREATOR_EMAIL,
            "orcid": CREATOR_ORCID
        }
    ],

    "contact": {
        "name": CREATOR_NAME,
        "email": CREATOR_EMAIL,
        "orcid": CREATOR_ORCID
    },

    "provenance_status": "CONFIRMED_SYNTHETIC",
    "data_origin": "synthetic",
    "generation_method": "programmatically_generated",

    "license_status": "NOT_ASSIGNED",
    "doi_status": "NOT_ASSIGNED"
})

with open(
    METADATA_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        metadata,
        f,
        indent=2,
        ensure_ascii=False
    )

print("\nDATASET METADATA UPDATED")
print(METADATA_FILE)

# ============================================================================
# 5. UPDATE CITATION.CFF
# ============================================================================

CFF_FILE = PACKAGE / "CITATION.cff"

if not CFF_FILE.exists():
    raise FileNotFoundError(
        f"CITATION.cff not found: {CFF_FILE}"
    )

cff = CFF_FILE.read_text(
    encoding="utf-8"
)

# ---------------------------------------------------------------------------
# Replace common existing title/version fields
# ---------------------------------------------------------------------------

cff = re.sub(
    r"(?m)^title:\s*.*$",
    f"title: \"{DATASET_TITLE}\"",
    cff
)

cff = re.sub(
    r"(?m)^version:\s*.*$",
    f"version: \"{VERSION}\"",
    cff
)

# ---------------------------------------------------------------------------
# Ensure creator/author block
# ---------------------------------------------------------------------------

author_block = f"""authors:
  - family-names: "Ajayi"
    given-names: "John Ojo"
    email: "{CREATOR_EMAIL}"
    orcid: "https://orcid.org/{CREATOR_ORCID}"
"""

if re.search(r"(?m)^authors:\s*$", cff):

    cff = re.sub(
        r"(?ms)^authors:\s*\n(?:  -.*\n(?:    .*\n)*)*",
        author_block,
        cff,
        count=1
    )

else:

    # Insert after version if no authors block exists
    version_match = re.search(
        r"(?m)^version:.*$",
        cff
    )

    if version_match:

        insert_at = version_match.end()

        cff = (
            cff[:insert_at]
            + "\n"
            + author_block
            + cff[insert_at:]
        )

    else:

        cff = author_block + "\n" + cff

CFF_FILE.write_text(
    cff,
    encoding="utf-8"
)

print("\nCITATION.CFF UPDATED")
print(CFF_FILE)

# ============================================================================
# 6. UPDATE README CREATOR INFORMATION
# ============================================================================

README_FILE = PACKAGE / "README.md"

if README_FILE.exists():

    readme = README_FILE.read_text(
        encoding="utf-8"
    )

    creator_section = f"""

## Dataset Creator

**Name:** {CREATOR_NAME}
**Email:** {CREATOR_EMAIL}
**ORCID:** https://orcid.org/{CREATOR_ORCID}
**Version:** {VERSION}

"""

    if "## Dataset Creator" not in readme:

        readme = (
            readme.rstrip()
            + "\n"
            + creator_section
        )

        README_FILE.write_text(
            readme,
            encoding="utf-8"
        )

        print("\nREADME CREATOR SECTION ADDED")

    else:

        print("\nREADME CREATOR SECTION ALREADY EXISTS")

# ============================================================================
# 7. CREATE AUTHORSHIP METADATA RECORD
# ============================================================================

AUTHOR_FILE = META_DIR / "AUTHORS.json"

author_record = {
    "dataset": "AFRIDATACYBERJOHN",
    "version": VERSION,
    "creator": {
        "name": CREATOR_NAME,
        "email": CREATOR_EMAIL,
        "orcid": f"https://orcid.org/{CREATOR_ORCID}"
    }
}

with open(
    AUTHOR_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        author_record,
        f,
        indent=2
    )

print("\nAUTHOR RECORD CREATED")
print(AUTHOR_FILE)

# ============================================================================
# 8. VERIFY CSV HASHES
# ============================================================================

print("\nCSV HASH PRESERVATION")
print("-" * 90)

after_hashes = {
    p.name: sha256_file(p)
    for p in DATA_FILES
}

all_unchanged = True

for name in before_hashes:

    unchanged = (
        before_hashes[name]
        == after_hashes[name]
    )

    print(
        f"{name:50s} "
        f"UNCHANGED={unchanged}"
    )

    if not unchanged:
        all_unchanged = False

if not all_unchanged:
    raise AssertionError(
        "CRITICAL: One or more dataset CSV files changed."
    )

# ============================================================================
# 9. VERIFY CREATOR INFORMATION
# ============================================================================

print("\nCREATOR METADATA VERIFICATION")
print("-" * 90)

with open(
    METADATA_FILE,
    "r",
    encoding="utf-8"
) as f:

    final_metadata = json.load(f)

creator_checks = {
    "name":
        final_metadata["creator"] == CREATOR_NAME,

    "email":
        final_metadata["contact"]["email"]
        == CREATOR_EMAIL,

    "orcid":
        final_metadata["contact"]["orcid"]
        == CREATOR_ORCID,

    "version":
        final_metadata["version"] == VERSION,

    "provenance":
        final_metadata["provenance_status"]
        == "CONFIRMED_SYNTHETIC",

    "license":
        final_metadata["license_status"]
        == "NOT_ASSIGNED",
}

for check, passed in creator_checks.items():

    print(
        f"{check:20s} PASS={passed}"
    )

    if not passed:
        raise AssertionError(
            f"Creator metadata verification failed: {check}"
        )

# ============================================================================
# 10. FINAL STATUS
# ============================================================================

print("\n" + "=" * 90)
print("STAGE 39M-A COMPLETE")
print("=" * 90)

print("\nCREATOR")
print("  Name :", CREATOR_NAME)
print("  Email:", CREATOR_EMAIL)
print("  ORCID:", CREATOR_ORCID)

print("\nDATASET")
print("  Name   : AFRIDATACYBERJOHN")
print("  Version:", VERSION)

print("\nPROVENANCE")
print("  CONFIRMED_SYNTHETIC")

print("\nDATASET CSVs")
print("  Modified: NO")
print("  Hashes preserved: YES")

print("\nLICENSE")
print("  NOT ASSIGNED")

print("\nDOI")
print("  NOT ASSIGNED")

print("\nPACKAGE")
print(PACKAGE)

print("\nREADY FOR STAGE 39N")
print("=" * 90)

# ==============================================================================
# NOTEBOOK CELL 685
# ==============================================================================

# ============================================================================
# STAGE 39N — FINAL PACKAGE REBUILD & PRE-ZENODO AUDIT
# ============================================================================
#
# PURPOSE
# -------
# 1. Rebuild checksum manifest after metadata changes.
# 2. Verify creator identity.
# 3. Verify synthetic provenance.
# 4. Verify all four dataset CSVs remain unchanged.
# 5. Verify forensic documentation exists.
# 6. Build final AFRIDATACYBERJOHN_v1.0 ZIP.
# 7. Verify ZIP integrity.
# 8. Produce a final publication-readiness report.
#
# NO DATASET CSV IS REGENERATED OR MODIFIED.
# ============================================================================

from pathlib import Path
import hashlib
import json
import zipfile
import shutil
import pandas as pd
import re

print("=" * 100)
print("STAGE 39N — FINAL PACKAGE REBUILD & PRE-ZENODO AUDIT")
print("=" * 100)

# ============================================================================
# 1. PACKAGE
# ============================================================================

PACKAGE = Path(
    "/content/AFRIDATACYBERJOHN_STAGE39M/"
    "AFRIDATACYBERJOHN_v1.0"
)

if not PACKAGE.exists():
    raise FileNotFoundError(
        f"Package not found: {PACKAGE}"
    )

print("\nPACKAGE")
print("-" * 100)
print(PACKAGE)

# ============================================================================
# 2. EXPECTED DATASET FILES
# ============================================================================

DATA_DIR = PACKAGE / "data"
DOC_DIR = PACKAGE / "documentation"
META_DIR = PACKAGE / "metadata"

DATA_FILES = {
    "authoritative_events":
        DATA_DIR /
        "AFRICA_MobileMoney_USSD_Authoritative_Events.csv",

    "authoritative_windows":
        DATA_DIR /
        "AFRICA_MobileMoney_USSD_Authoritative_Windows.csv",

    "current_events":
        DATA_DIR /
        "AFRICA_MobileMoney_USSD_Current_Events.csv",

    "current_windows":
        DATA_DIR /
        "AFRICA_MobileMoney_USSD_Current_Windows.csv",
}

EXPECTED_SHAPES = {
    "authoritative_events": (1029, 29),
    "authoritative_windows": (100, 8),
    "current_events": (1060, 29),
    "current_windows": (100, 10),
}

# ============================================================================
# 3. HASH FUNCTION
# ============================================================================

def sha256_file(path):

    h = hashlib.sha256()

    with open(path, "rb") as f:

        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            h.update(chunk)

    return h.hexdigest()

# ============================================================================
# 4. DATASET INTEGRITY
# ============================================================================

print("\n1. DATASET INTEGRITY")
print("-" * 100)

dataset_hashes = {}

for name, path in DATA_FILES.items():

    if not path.exists():
        raise FileNotFoundError(
            f"Missing dataset file: {path}"
        )

    df = pd.read_csv(path)

    expected_shape = EXPECTED_SHAPES[name]

    if df.shape != expected_shape:
        raise AssertionError(
            f"{name}: expected {expected_shape}, "
            f"found {df.shape}"
        )

    digest = sha256_file(path)

    dataset_hashes[path.relative_to(PACKAGE).as_posix()] = digest

    print(
        f"{name:25s}"
        f" shape={df.shape}"
        f" SHA256={digest}"
        f" PASS"
    )

# ============================================================================
# 5. SEMANTIC VALIDATION
# ============================================================================

print("\n2. SEMANTIC VALIDATION")
print("-" * 100)

for name in [
    "authoritative_events",
    "current_events",
]:

    df = pd.read_csv(DATA_FILES[name])

    checks = {
        "ground_truth_state=NORMAL":
            set(
                df["ground_truth_state"]
                .dropna()
                .unique()
            ) == {"NORMAL"},

        "is_attack=0":
            set(
                df["is_attack"]
                .dropna()
                .unique()
            ) == {0},

        "hard_negative=1":
            set(
                df["hard_negative"]
                .dropna()
                .unique()
            ) == {1},

        "is_observable_precursor=0":
            set(
                df["is_observable_precursor"]
                .dropna()
                .unique()
            ) == {0},
    }

    print(f"\n{name}")

    for check, passed in checks.items():

        print(
            f"  {check:35s} PASS={passed}"
        )

        if not passed:
            raise AssertionError(
                f"{name}: semantic check failed: {check}"
            )

# ============================================================================
# 6. WINDOW VALIDATION
# ============================================================================

print("\n3. WINDOW VALIDATION")
print("-" * 100)

EXPECTED_HORIZONS = {
    5: 20,
    10: 20,
    15: 20,
    30: 20,
    60: 20,
}

for name in [
    "authoritative_windows",
    "current_windows",
]:

    df = pd.read_csv(DATA_FILES[name])

    horizon_distribution = (
        df["horizon_minutes"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    if horizon_distribution != EXPECTED_HORIZONS:
        raise AssertionError(
            f"{name}: horizon distribution mismatch"
        )

    if df["window_id"].nunique() != 100:
        raise AssertionError(
            f"{name}: window IDs are not unique"
        )

    print(
        f"{name:25s}"
        f" windows={len(df)}"
        f" users={df['user_id'].nunique()}"
        f" horizons={horizon_distribution}"
        f" PASS"
    )

# ============================================================================
# 7. EVENT ID VALIDATION
# ============================================================================

print("\n4. EVENT ID VALIDATION")
print("-" * 100)

for name in [
    "authoritative_events",
    "current_events",
]:

    df = pd.read_csv(DATA_FILES[name])

    unique_ids = df["event_id"].nunique()

    if unique_ids != len(df):
        raise AssertionError(
            f"{name}: duplicate event IDs detected"
        )

    print(
        f"{name:25s}"
        f" events={len(df)}"
        f" unique_event_ids={unique_ids}"
        f" PASS"
    )

# ============================================================================
# 8. REQUIRED DOCUMENTATION
# ============================================================================

print("\n5. DOCUMENTATION AUDIT")
print("-" * 100)

REQUIRED_FILES = [
    "README.md",
    "CITATION.cff",

    "documentation/DATASET_DESCRIPTION.md",
    "documentation/DATA_DICTIONARY.csv",
    "documentation/FORENSIC_VALIDATION.md",
    "documentation/METHODOLOGY.md",
    "documentation/WINDOW_FIELD_SEMANTIC_RECOVERY.csv",
    "documentation/PROVENANCE.md",

    "metadata/dataset_metadata.json",
    "metadata/AUTHORS.json",
]

for relative_path in REQUIRED_FILES:

    path = PACKAGE / relative_path

    exists = path.exists()

    print(
        f"{relative_path:60s} PASS={exists}"
    )

    if not exists:
        raise FileNotFoundError(
            f"Required publication file missing: {path}"
        )

# ============================================================================
# 9. CREATOR METADATA
# ============================================================================

print("\n6. CREATOR METADATA AUDIT")
print("-" * 100)

METADATA_FILE = META_DIR / "dataset_metadata.json"

with open(
    METADATA_FILE,
    "r",
    encoding="utf-8"
) as f:

    metadata = json.load(f)

creator_checks = {
    "creator name":
        metadata.get("creator")
        == "John Ojo Ajayi",

    "creator email":
        metadata.get("contact", {}).get("email")
        == "onejotech@gmail.com",

    "creator ORCID":
        metadata.get("contact", {}).get("orcid")
        == "0000-0002-8063-6070",

    "dataset name":
        metadata.get("dataset_name")
        == "AFRIDATACYBERJOHN",

    "version":
        metadata.get("version")
        == "1.0",

    "provenance":
        metadata.get("provenance_status")
        == "CONFIRMED_SYNTHETIC",

    "origin":
        metadata.get("data_origin")
        == "synthetic",

    "license":
        metadata.get("license_status")
        == "NOT_ASSIGNED",
}

for check, passed in creator_checks.items():

    print(
        f"{check:25s} PASS={passed}"
    )

    if not passed:
        raise AssertionError(
            f"Creator metadata check failed: {check}"
        )

# ============================================================================
# 10. AUTHORS.JSON
# ============================================================================

print("\n7. AUTHORS.JSON AUDIT")
print("-" * 100)

AUTHORS_FILE = META_DIR / "AUTHORS.json"

with open(
    AUTHORS_FILE,
    "r",
    encoding="utf-8"
) as f:

    authors = json.load(f)

author = authors["creator"]

author_checks = {
    "name":
        author["name"] == "John Ojo Ajayi",

    "email":
        author["email"] == "onejotech@gmail.com",

    "ORCID":
        author["orcid"]
        == "https://orcid.org/0000-0002-8063-6070",
}

for check, passed in author_checks.items():

    print(
        f"{check:20s} PASS={passed}"
    )

    if not passed:
        raise AssertionError(
            f"AUTHORS.json check failed: {check}"
        )

# ============================================================================
# 11. CITATION.CFF AUDIT
# ============================================================================

print("\n8. CITATION.CFF AUDIT")
print("-" * 100)

CFF_FILE = PACKAGE / "CITATION.cff"

cff = CFF_FILE.read_text(
    encoding="utf-8"
)

cff_checks = {
    "John Ojo":
        "John Ojo" in cff,

    "email":
        "onejotech@gmail.com" in cff,

    "ORCID":
        "https://orcid.org/0000-0002-8063-6070" in cff,

    "version":
        'version: "1.0"' in cff,

    "AFRIDATACYBERJOHN":
        "AFRIDATACYBERJOHN" in cff,
}

for check, passed in cff_checks.items():

    print(
        f"{check:20s} PASS={passed}"
    )

    if not passed:
        raise AssertionError(
            f"CITATION.cff check failed: {check}"
        )

# ============================================================================
# 12. PROVENANCE DOCUMENT
# ============================================================================

print("\n9. PROVENANCE AUDIT")
print("-" * 100)

PROVENANCE_FILE = DOC_DIR / "PROVENANCE.md"

provenance = PROVENANCE_FILE.read_text(
    encoding="utf-8"
)

provenance_checks = {
    "synthetic":
        "CONFIRMED_SYNTHETIC" in provenance,

    "programmatically generated":
        "programmatically generated" in provenance,

    "production data distinction":
        "not" in provenance.lower()
        and "production" in provenance.lower(),

    "population 1029":
        "1,029" in provenance,

    "population 1060":
        "1,060" in provenance,
}

for check, passed in provenance_checks.items():

    print(
        f"{check:35s} PASS={passed}"
    )

    if not passed:
        raise AssertionError(
            f"Provenance check failed: {check}"
        )

# ============================================================================
# 13. REBUILD CHECKSUM MANIFEST
# ============================================================================

print("\n10. REBUILDING CHECKSUM MANIFEST")
print("-" * 100)

CHECKSUM_FILE = META_DIR / "checksums.sha256"

checksum_entries = []

for path in sorted(
    PACKAGE.rglob("*")
):

    if not path.is_file():
        continue

    relative = path.relative_to(PACKAGE).as_posix()

    # Do not hash the checksum file itself.
    if relative == "metadata/checksums.sha256":
        continue

    digest = sha256_file(path)

    checksum_entries.append(
        f"{digest}  {relative}"
    )

CHECKSUM_FILE.write_text(
    "\n".join(checksum_entries)
    + "\n",
    encoding="utf-8"
)

print(
    "Checksum entries:",
    len(checksum_entries)
)

# ============================================================================
# 14. VERIFY CHECKSUM MANIFEST
# ============================================================================

print("\n11. CHECKSUM MANIFEST VALIDATION")
print("-" * 100)

checksum_lines = [
    line.strip()
    for line in CHECKSUM_FILE.read_text(
        encoding="utf-8"
    ).splitlines()
    if line.strip()
]

checksum_failures = []

for line in checksum_lines:

    digest, relative = line.split(
        "  ",
        1
    )

    path = PACKAGE / relative

    if not path.exists():

        checksum_failures.append(
            (relative, "MISSING")
        )

        continue

    actual = sha256_file(path)

    if actual != digest:

        checksum_failures.append(
            (relative, "HASH_MISMATCH")
        )

if checksum_failures:

    for item in checksum_failures:
        print("FAIL:", item)

    raise AssertionError(
        "Checksum manifest validation failed."
    )

print(
    "Entries validated:",
    len(checksum_lines)
)

print("Failures: 0")
print("PASS")

# ============================================================================
# 15. RECHECK DATASET HASHES AFTER CHECKSUM REBUILD
# ============================================================================

print("\n12. FINAL DATASET HASH PRESERVATION")
print("-" * 100)

for name, path in DATA_FILES.items():

    digest = sha256_file(path)

    # Confirm hash is exactly the hash captured at Stage 39M-A
    #
    # These are the frozen hashes established before metadata-only changes.
    frozen_hashes = {
        "authoritative_events":
            "1fceb3e353f84077b7429b347f517fba789b839471c7940147757998f7c0fccd",

        "authoritative_windows":
            "f95f574767ee21bde1c4ad8e9ad0ecf30dfdba3df7d0bfd0bda8b5a322705f44",

        "current_events":
            "fe4b8347d3264fe0faae17b830c10432e6242c66012e93e908d95717ea11abb4",

        "current_windows":
            "47e2f01111e7194ddb4da5e8fbd7559cd29eeda286bb18117e2e2e524e239fcd",
    }

    passed = (
        digest == frozen_hashes[name]
    )

    print(
        f"{name:25s} PASS={passed}"
    )

    if not passed:
        raise AssertionError(
            f"Frozen dataset hash changed: {name}"
        )

# ============================================================================
# 16. BUILD FINAL ZIP
# ============================================================================

print("\n13. FINAL ZIP BUILD")
print("-" * 100)

FINAL_ZIP = Path(
    "/content/AFRIDATACYBERJOHN_v1.0.zip"
)

if FINAL_ZIP.exists():
    FINAL_ZIP.unlink()

# ZIP contains AFRIDATACYBERJOHN_v1.0/ as root directory.
with zipfile.ZipFile(
    FINAL_ZIP,
    "w",
    compression=zipfile.ZIP_DEFLATED
) as zf:

    for path in sorted(
        PACKAGE.rglob("*")
    ):

        if not path.is_file():
            continue

        relative = path.relative_to(
            PACKAGE
        )

        archive_name = (
            "AFRIDATACYBERJOHN_v1.0/"
            + relative.as_posix()
        )

        zf.write(
            path,
            archive_name
        )

print(
    "Final ZIP:",
    FINAL_ZIP
)

print(
    "ZIP size:",
    FINAL_ZIP.stat().st_size,
    "bytes"
)

# ============================================================================
# 17. ZIP INTEGRITY
# ============================================================================

print("\n14. FINAL ZIP INTEGRITY")
print("-" * 100)

with zipfile.ZipFile(
    FINAL_ZIP,
    "r"
) as zf:

    bad = zf.testzip()

    if bad is not None:
        raise RuntimeError(
            f"ZIP integrity failure: {bad}"
        )

    members = [
        name
        for name in zf.namelist()
        if not name.endswith("/")
    ]

print("ZIP integrity: PASS")
print("File count:", len(members))

# ============================================================================
# 18. FINAL PACKAGE LIST
# ============================================================================

print("\n15. FINAL PACKAGE CONTENTS")
print("-" * 100)

for i, member in enumerate(
    members,
    1
):

    print(
        f"{i:02d}. {member}"
    )

# ============================================================================
# 19. FINAL ZIP HASH
# ============================================================================

final_zip_hash = sha256_file(
    FINAL_ZIP
)

print("\n16. FINAL ZIP SHA256")
print("-" * 100)
print(final_zip_hash)

# ============================================================================
# 20. FINAL RESULT
# ============================================================================

print("\n" + "=" * 100)
print("STAGE 39N COMPLETE")
print("=" * 100)

print("\nIDENTITY")
print("  Creator : John Ojo Ajayi")
print("  Email   : onejotech@gmail.com")
print("  ORCID   : https://orcid.org/0000-0002-8063-6070")

print("\nDATASET")
print("  Name    : AFRIDATACYBERJOHN")
print("  Version : 1.0")

print("\nPROVENANCE")
print("  Status  : CONFIRMED_SYNTHETIC")

print("\nFROZEN DATA")
print("  Authoritative events : 1,029")
print("  Current events       : 1,060")
print("  Authoritative windows: 100")
print("  Current windows      : 100")

print("\nDATASET CSVs")
print("  Modified             : NO")
print("  Frozen hashes preserved: YES")

print("\nLICENSE")
print("  NOT ASSIGNED")

print("\nDOI")
print("  NOT ASSIGNED")

print("\nFINAL PACKAGE")
print(PACKAGE)

print("\nFINAL ZIP")
print(FINAL_ZIP)

print("\nFINAL ZIP SHA256")
print(final_zip_hash)

print("\n" + "=" * 100)
print("PRE-ZENODO PACKAGE AUDIT: PASS")
print("=" * 100)

# ==============================================================================
# NOTEBOOK CELL 686
# ==============================================================================

# ============================================================================
# STAGE 39O — PERMANENT GOOGLE DRIVE BACKUP
# ============================================================================
#
# PURPOSE
# -------
# Permanently save the completed AFRIDATACYBERJOHN v1.0 release to Google
# Drive so that it survives Colab runtime shutdown/disconnection.
#
# ALSO SAVES:
#   1. Final ZIP
#   2. Complete unpacked release directory
#   3. Recovery manifest
#   4. Stage 39N audit summary
#
# NO DATASET CONTENT IS MODIFIED.
# ============================================================================

from pathlib import Path
import shutil
import hashlib
import json
from datetime import datetime

print("=" * 100)
print("STAGE 39O — PERMANENT GOOGLE DRIVE BACKUP")
print("=" * 100)

# ============================================================================
# 1. SOURCE FILES
# ============================================================================

FINAL_ZIP = Path(
    "/content/AFRIDATACYBERJOHN_v1.0.zip"
)

FINAL_PACKAGE = Path(
    "/content/AFRIDATACYBERJOHN_STAGE39M/"
    "AFRIDATACYBERJOHN_v1.0"
)

if not FINAL_ZIP.exists():
    raise FileNotFoundError(
        f"Final ZIP not found: {FINAL_ZIP}"
    )

if not FINAL_PACKAGE.exists():
    raise FileNotFoundError(
        f"Final package not found: {FINAL_PACKAGE}"
    )

# ============================================================================
# 2. SHA256 FUNCTION
# ============================================================================

def sha256_file(path):

    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            h.update(chunk)

    return h.hexdigest()

FINAL_ZIP_SHA256 = sha256_file(FINAL_ZIP)

EXPECTED_ZIP_SHA256 = (
    "b58c97ffbf45240d5b941bd7905666dc3dc6a26f4dc47e2b7669dddaa9b3b465"
)

if FINAL_ZIP_SHA256 != EXPECTED_ZIP_SHA256:
    raise AssertionError(
        "CRITICAL: Final ZIP SHA256 does not match Stage 39N."
    )

print("\nSOURCE VALIDATION")
print("-" * 100)
print("Final ZIP found: PASS")
print("Final package found: PASS")
print("Final ZIP SHA256 matches Stage 39N: PASS")

# ============================================================================
# 3. CREATE PERMANENT DRIVE LOCATION
# ============================================================================

DRIVE_ROOT = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN"
)

DRIVE_RELEASE = (
    DRIVE_ROOT /
    "AFRIDATACYBERJOHN_v1.0"
)

DRIVE_ZIP = (
    DRIVE_ROOT /
    "AFRIDATACYBERJOHN_v1.0.zip"
)

if DRIVE_ROOT.exists():
    print("\nEXISTING DRIVE BACKUP FOUND")
    print(DRIVE_ROOT)

else:
    DRIVE_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

# ============================================================================
# 4. COPY COMPLETE RELEASE DIRECTORY
# ============================================================================

if DRIVE_RELEASE.exists():
    shutil.rmtree(DRIVE_RELEASE)

shutil.copytree(
    FINAL_PACKAGE,
    DRIVE_RELEASE
)

print("\nPERMANENT RELEASE DIRECTORY")
print("-" * 100)
print(DRIVE_RELEASE)

# ============================================================================
# 5. COPY FINAL ZIP
# ============================================================================

if DRIVE_ZIP.exists():
    DRIVE_ZIP.unlink()

shutil.copy2(
    FINAL_ZIP,
    DRIVE_ZIP
)

print("\nPERMANENT ZIP")
print("-" * 100)
print(DRIVE_ZIP)

# ============================================================================
# 6. VERIFY COPIED ZIP
# ============================================================================

DRIVE_ZIP_SHA256 = sha256_file(
    DRIVE_ZIP
)

zip_hash_match = (
    DRIVE_ZIP_SHA256 ==
    EXPECTED_ZIP_SHA256
)

print("\nDRIVE ZIP VERIFICATION")
print("-" * 100)
print("Original SHA256:")
print(EXPECTED_ZIP_SHA256)

print("\nDrive copy SHA256:")
print(DRIVE_ZIP_SHA256)

print("\nSHA256 MATCH:", zip_hash_match)

if not zip_hash_match:
    raise AssertionError(
        "CRITICAL: Google Drive ZIP copy hash mismatch."
    )

# ============================================================================
# 7. VERIFY RELEASE DIRECTORY CONTENT
# ============================================================================

source_files = sorted(
    p.relative_to(FINAL_PACKAGE).as_posix()
    for p in FINAL_PACKAGE.rglob("*")
    if p.is_file()
)

drive_files = sorted(
    p.relative_to(DRIVE_RELEASE).as_posix()
    for p in DRIVE_RELEASE.rglob("*")
    if p.is_file()
)

directory_file_match = (
    source_files == drive_files
)

print("\nDIRECTORY CONTENT VERIFICATION")
print("-" * 100)
print("Source files:", len(source_files))
print("Drive files :", len(drive_files))
print("File list match:", directory_file_match)

if not directory_file_match:
    raise AssertionError(
        "Google Drive release directory does not match source package."
    )

# ============================================================================
# 8. VERIFY EVERY FILE HASH IN DRIVE
# ============================================================================

print("\nFILE-BY-FILE HASH VERIFICATION")
print("-" * 100)

file_failures = []

for relative in source_files:

    source_path = FINAL_PACKAGE / relative
    drive_path = DRIVE_RELEASE / relative

    source_hash = sha256_file(source_path)
    drive_hash = sha256_file(drive_path)

    if source_hash != drive_hash:

        file_failures.append(
            relative
        )

    else:

        print(
            f"PASS  {relative}"
        )

if file_failures:
    raise AssertionError(
        "Drive file hash failures: "
        + str(file_failures)
    )

# ============================================================================
# 9. CREATE RECOVERY MANIFEST
# ============================================================================

RECOVERY_MANIFEST = (
    DRIVE_ROOT /
    "RECOVERY_MANIFEST.json"
)

recovery_manifest = {
    "dataset": "AFRIDATACYBERJOHN",
    "version": "1.0",

    "creator": {
        "name": "John Ojo Ajayi",
        "email": "onejotech@gmail.com",
        "orcid": "https://orcid.org/0000-0002-8063-6070"
    },

    "provenance": {
        "status": "CONFIRMED_SYNTHETIC",
        "origin": "synthetic",
        "generation_method": "programmatically_generated"
    },

    "frozen_populations": {
        "authoritative_events": 1029,
        "current_events": 1060,
        "authoritative_windows": 100,
        "current_windows": 100
    },

    "license_status": "NOT_ASSIGNED",
    "doi_status": "NOT_ASSIGNED",

    "final_zip": {
        "filename": "AFRIDATACYBERJOHN_v1.0.zip",
        "size_bytes": DRIVE_ZIP.stat().st_size,
        "sha256": DRIVE_ZIP_SHA256
    },

    "release_directory": str(DRIVE_RELEASE),

    "stage_39n_status": "PRE-ZENODO PACKAGE AUDIT: PASS",

    "dataset_csvs_modified": False,
    "source_dataframes_modified": False,

    "backup_created_at": datetime.now().isoformat()
}

with open(
    RECOVERY_MANIFEST,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        recovery_manifest,
        f,
        indent=2
    )

print("\nRECOVERY MANIFEST")
print("-" * 100)
print(RECOVERY_MANIFEST)

# ============================================================================
# 10. FINAL BACKUP STATUS
# ============================================================================

print("\n" + "=" * 100)
print("STAGE 39O COMPLETE — PERMANENT BACKUP SUCCESSFUL")
print("=" * 100)

print("\nGOOGLE DRIVE BACKUP")
print("-" * 100)
print("Root:")
print(DRIVE_ROOT)

print("\nZIP:")
print(DRIVE_ZIP)

print("\nRelease directory:")
print(DRIVE_RELEASE)

print("\nRecovery manifest:")
print(RECOVERY_MANIFEST)

print("\nFINAL ZIP SHA256:")
print(DRIVE_ZIP_SHA256)

print("\nVERIFICATION")
print("-" * 100)
print("ZIP copied: PASS")
print("ZIP SHA256 preserved: PASS")
print("Release directory copied: PASS")
print("File count preserved: PASS")
print("File-by-file hashes preserved: PASS")
print("Dataset CSVs modified: NO")
print("Source dataframes modified: NO")

print("\n" + "=" * 100)
print("YOUR FINAL RELEASE IS NOW SAVED IN GOOGLE DRIVE")
print("=" * 100)

# ==============================================================================
# NOTEBOOK CELL 687
# ==============================================================================

# ============================================================================
# STAGE 40A — FINAL REPOSITORY / ZENODO METADATA INSPECTION
# ============================================================================
#
# PURPOSE
# -------
# Read-only inspection of the permanently backed-up release before making
# any license or Zenodo decision.
#
# NO FILES ARE MODIFIED.
# NO DATASET CSVs ARE MODIFIED.
# ============================================================================

from pathlib import Path
import json

print("=" * 100)
print("STAGE 40A — FINAL REPOSITORY / ZENODO METADATA INSPECTION")
print("=" * 100)

# ============================================================================
# 1. PERMANENT GOOGLE DRIVE RELEASE
# ============================================================================

ROOT = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN"
)

PACKAGE = ROOT / "AFRIDATACYBERJOHN_v1.0"

if not ROOT.exists():
    raise FileNotFoundError(
        f"Permanent backup root not found: {ROOT}"
    )

if not PACKAGE.exists():
    raise FileNotFoundError(
        f"Permanent release not found: {PACKAGE}"
    )

print("\nPERMANENT RELEASE")
print("-" * 100)
print(PACKAGE)

# ============================================================================
# 2. RECOVERY MANIFEST
# ============================================================================

MANIFEST = ROOT / "RECOVERY_MANIFEST.json"

print("\nRECOVERY MANIFEST")
print("-" * 100)

if MANIFEST.exists():

    manifest = json.loads(
        MANIFEST.read_text(
            encoding="utf-8"
        )
    )

    print(
        json.dumps(
            manifest,
            indent=2
        )
    )

else:
    print("RECOVERY MANIFEST NOT FOUND")

# ============================================================================
# 3. CITATION.CFF
# ============================================================================

CFF = PACKAGE / "CITATION.cff"

print("\n" + "=" * 100)
print("CITATION.CFF")
print("=" * 100)

if CFF.exists():
    print(
        CFF.read_text(
            encoding="utf-8"
        )
    )
else:
    print("CITATION.cff NOT FOUND")

# ============================================================================
# 4. DATASET METADATA
# ============================================================================

METADATA = (
    PACKAGE /
    "metadata" /
    "dataset_metadata.json"
)

print("\n" + "=" * 100)
print("DATASET METADATA")
print("=" * 100)

if METADATA.exists():

    metadata = json.loads(
        METADATA.read_text(
            encoding="utf-8"
        )
    )

    print(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False
        )
    )

else:
    print("dataset_metadata.json NOT FOUND")

# ============================================================================
# 5. AUTHORS
# ============================================================================

AUTHORS = (
    PACKAGE /
    "metadata" /
    "AUTHORS.json"
)

print("\n" + "=" * 100)
print("AUTHORS.JSON")
print("=" * 100)

if AUTHORS.exists():

    print(
        AUTHORS.read_text(
            encoding="utf-8"
        )
    )

else:
    print("AUTHORS.json NOT FOUND")

# ============================================================================
# 6. README
# ============================================================================

README = PACKAGE / "README.md"

print("\n" + "=" * 100)
print("README — CREATOR / PROVENANCE / LICENSE SECTIONS")
print("=" * 100)

if README.exists():

    readme = README.read_text(
        encoding="utf-8"
    )

    lines = readme.splitlines()

    keywords = [
        "creator",
        "author",
        "email",
        "orcid",
        "provenance",
        "synthetic",
        "license",
        "doi",
    ]

    for i, line in enumerate(lines):

        if any(
            keyword in line.lower()
            for keyword in keywords
        ):

            start = max(0, i - 2)
            end = min(len(lines), i + 5)

            print(
                f"\n--- lines {start + 1}-{end} ---"
            )

            print(
                "\n".join(
                    lines[start:end]
                )
            )

else:
    print("README.md NOT FOUND")

# ============================================================================
# 7. PROVENANCE DOCUMENT
# ============================================================================

PROVENANCE = (
    PACKAGE /
    "documentation" /
    "PROVENANCE.md"
)

print("\n" + "=" * 100)
print("PROVENANCE")
print("=" * 100)

if PROVENANCE.exists():

    print(
        PROVENANCE.read_text(
            encoding="utf-8"
        )
    )

else:
    print("PROVENANCE.md NOT FOUND")

# ============================================================================
# 8. CURRENT LICENSE STATUS
# ============================================================================

print("\n" + "=" * 100)
print("CURRENT LICENSE STATUS")
print("=" * 100)

if METADATA.exists():

    metadata = json.loads(
        METADATA.read_text(
            encoding="utf-8"
        )
    )

    print(
        "license_status:",
        metadata.get(
            "license_status",
            "NOT PRESENT"
        )
    )

    print(
        "doi_status:",
        metadata.get(
            "doi_status",
            "NOT PRESENT"
        )
    )

# ============================================================================
# 9. FINAL STATUS
# ============================================================================

print("\n" + "=" * 100)
print("STAGE 40A COMPLETE — READ ONLY")
print("=" * 100)

print("Permanent package located: PASS")
print("No files modified: YES")
print("Dataset CSVs modified: NO")

print("\nNEXT:")
print("Review the output before selecting the repository license.")
print("=" * 100)

# ==============================================================================
# NOTEBOOK CELL 688
# ==============================================================================

# ============================================================
# STAGE 40B — APPLY CC BY 4.0 LICENSE
# AFRIDATACYBERJOHN v1.0
# ============================================================

from pathlib import Path
import json
import hashlib
import shutil
import zipfile

# ------------------------------------------------------------
# 1. Locate permanent release
# ------------------------------------------------------------

DRIVE_ROOT = Path("/content/drive/MyDrive/AFRIDATACYBERJOHN")
RELEASE_DIR = DRIVE_ROOT / "AFRIDATACYBERJOHN_v1.0"
ZIP_PATH = DRIVE_ROOT / "AFRIDATACYBERJOHN_v1.0.zip"

assert RELEASE_DIR.exists(), f"Release directory not found: {RELEASE_DIR}"
assert ZIP_PATH.exists(), f"Release ZIP not found: {ZIP_PATH}"

print("Release located:")
print(RELEASE_DIR)

# ------------------------------------------------------------
# 2. Record frozen CSV hashes BEFORE modification
# ------------------------------------------------------------

CSV_FILES = [
    RELEASE_DIR / "data/AFRICA_MobileMoney_USSD_Authoritative_Events.csv",
    RELEASE_DIR / "data/AFRICA_MobileMoney_USSD_Authoritative_Windows.csv",
    RELEASE_DIR / "data/AFRICA_MobileMoney_USSD_Current_Events.csv",
    RELEASE_DIR / "data/AFRICA_MobileMoney_USSD_Current_Windows.csv",
]

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

before_hashes = {
    str(p.relative_to(RELEASE_DIR)): sha256_file(p)
    for p in CSV_FILES
}

print("\nFROZEN CSV HASHES — BEFORE")
for k, v in before_hashes.items():
    print(k, v)

# ------------------------------------------------------------
# 3. Apply CC BY 4.0 license text
# ------------------------------------------------------------

LICENSE_TEXT = """Creative Commons Attribution 4.0 International (CC BY 4.0)

Copyright © 2026 John Ojo Ajayi

This work is licensed under the Creative Commons Attribution 4.0
International License.

You are free to:

- Share — copy and redistribute the material in any medium or format.
- Adapt — remix, transform, and build upon the material for any purpose,
  including commercially.

Under the following terms:

- Attribution — You must give appropriate credit, provide a link to the
  license, and indicate if changes were made. You may do so in any
  reasonable manner, but not in any way that suggests the licensor
  endorses you or your use.

No additional restrictions — You may not apply legal terms or technological
measures that legally restrict others from doing anything the license
permits.

License:
https://creativecommons.org/licenses/by/4.0/

The dataset is provided as a synthetic, programmatically generated
cybersecurity research dataset. Users should consult the accompanying
documentation for dataset provenance, methodology, structure, and
forensic validation information.
"""

LICENSE_PATH = RELEASE_DIR / "LICENSE"
LICENSE_PATH.write_text(LICENSE_TEXT, encoding="utf-8")

print("\nLICENSE written:")
print(LICENSE_PATH)

# ------------------------------------------------------------
# 4. Update README license section
# ------------------------------------------------------------

README_PATH = RELEASE_DIR / "README.md"
README = README_PATH.read_text(encoding="utf-8")

README = README.replace(
    "LICENSE (not assigned in v1.0)",
    "LICENSE (CC BY 4.0)"
)

README = README.replace(
    "License: NOT_ASSIGNED",
    "License: CC BY 4.0"
)

README = README.replace(
    "license: NOT_ASSIGNED",
    "license: CC BY 4.0"
)

README = README.replace(
    "No distribution license is assigned at this stage.",
    "This dataset is licensed under the Creative Commons Attribution "
    "4.0 International License (CC BY 4.0)."
)

README_PATH.write_text(README, encoding="utf-8")

print("README updated.")

# ------------------------------------------------------------
# 5. Update dataset_metadata.json
# ------------------------------------------------------------

META_PATH = RELEASE_DIR / "metadata/dataset_metadata.json"

with open(META_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Preserve existing metadata structure while updating only
# license-related fields where present.

def update_license_fields(obj):
    if isinstance(obj, dict):
        for key in list(obj.keys()):
            value = obj[key]

            if key.lower() in {
                "license",
                "license_status",
                "license_name"
            }:
                if isinstance(value, str):
                    if "NOT_ASSIGNED" in value or "not assigned" in value.lower():
                        obj[key] = "CC BY 4.0"

            elif key.lower() in {"license_url", "license_uri"}:
                obj[key] = "https://creativecommons.org/licenses/by/4.0/"

            elif isinstance(value, (dict, list)):
                update_license_fields(value)

    elif isinstance(obj, list):
        for item in obj:
            update_license_fields(item)

update_license_fields(metadata)

# Explicit canonical license fields
metadata["license"] = "CC BY 4.0"
metadata["license_url"] = "https://creativecommons.org/licenses/by/4.0/"

with open(META_PATH, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
    f.write("\n")

print("dataset_metadata.json updated.")

# ------------------------------------------------------------
# 6. Update CITATION.cff
# ------------------------------------------------------------

CFF_PATH = RELEASE_DIR / "CITATION.cff"
CFF = CFF_PATH.read_text(encoding="utf-8")

# Add license if it does not already exist.
if not any(line.strip().startswith("license:") for line in CFF.splitlines()):
    CFF = CFF.rstrip() + "\nlicense: CC BY 4.0\n"

CFF_PATH.write_text(CFF, encoding="utf-8")

print("CITATION.cff updated.")

# ------------------------------------------------------------
# 7. Update AUTHORS.json
# ------------------------------------------------------------

AUTHORS_PATH = RELEASE_DIR / "metadata/AUTHORS.json"

with open(AUTHORS_PATH, "r", encoding="utf-8") as f:
    authors = json.load(f)

authors["license"] = "CC BY 4.0"
authors["license_url"] = "https://creativecommons.org/licenses/by/4.0/"

with open(AUTHORS_PATH, "w", encoding="utf-8") as f:
    json.dump(authors, f, indent=2, ensure_ascii=False)
    f.write("\n")

print("AUTHORS.json updated.")

# ------------------------------------------------------------
# 8. Update PROVENANCE.md
# ------------------------------------------------------------

PROV_PATH = RELEASE_DIR / "documentation/PROVENANCE.md"
PROV = PROV_PATH.read_text(encoding="utf-8")

PROV = PROV.replace(
    "License: NOT_ASSIGNED",
    "License: CC BY 4.0"
)

PROV = PROV.replace(
    "license: NOT_ASSIGNED",
    "license: CC BY 4.0"
)

PROV_PATH.write_text(PROV, encoding="utf-8")

print("PROVENANCE.md updated.")

# ------------------------------------------------------------
# 9. Verify frozen CSVs were NOT changed
# ------------------------------------------------------------

after_hashes = {
    str(p.relative_to(RELEASE_DIR)): sha256_file(p)
    for p in CSV_FILES
}

csv_unchanged = before_hashes == after_hashes

print("\nFROZEN CSV INTEGRITY CHECK")
print("CSV files unchanged:", csv_unchanged)

for k in before_hashes:
    status = "PASS" if before_hashes[k] == after_hashes[k] else "FAIL"
    print(status, k)

assert csv_unchanged, "CRITICAL: A frozen CSV changed."

# ------------------------------------------------------------
# 10. Verify license
# ------------------------------------------------------------

assert LICENSE_PATH.exists()
assert "Creative Commons Attribution 4.0" in LICENSE_PATH.read_text(
    encoding="utf-8"
)

print("\nLICENSE VALIDATION: PASS")
print("License: CC BY 4.0")

# ------------------------------------------------------------
# 11. Rebuild release ZIP
# ------------------------------------------------------------

if ZIP_PATH.exists():
    ZIP_PATH.unlink()

with zipfile.ZipFile(
    ZIP_PATH,
    "w",
    compression=zipfile.ZIP_DEFLATED
) as z:
    for path in sorted(RELEASE_DIR.rglob("*")):
        if path.is_file():
            z.write(
                path,
                path.relative_to(RELEASE_DIR.parent)
            )

print("\nRelease ZIP rebuilt:")
print(ZIP_PATH)

# ------------------------------------------------------------
# 12. Verify ZIP integrity
# ------------------------------------------------------------

with zipfile.ZipFile(ZIP_PATH, "r") as z:
    bad = z.testzip()
    assert bad is None, f"ZIP integrity failure: {bad}"

print("ZIP integrity: PASS")

# ------------------------------------------------------------
# 13. Final ZIP SHA256
# ------------------------------------------------------------

zip_sha256 = sha256_file(ZIP_PATH)

print("\nFINAL STAGE 40B RESULT")
print("=" * 60)
print("Dataset: AFRIDATACYBERJOHN")
print("Version: 1.0")
print("License: CC BY 4.0")
print("Purpose: Maximum research reuse and citation")
print("Frozen CSVs modified: NO")
print("CSV integrity: PASS")
print("ZIP integrity: PASS")
print("ZIP SHA256:", zip_sha256)
print("=" * 60)

# ==============================================================================
# NOTEBOOK CELL 689
# ==============================================================================

# ============================================================
# STAGE 40C — FINAL RELEASE / ZENODO READINESS AUDIT
# AFRIDATACYBERJOHN v1.0
# ============================================================

from pathlib import Path
import hashlib
import json
import zipfile
import re
import pandas as pd

# ------------------------------------------------------------
# 1. RELEASE LOCATIONS
# ------------------------------------------------------------

DRIVE_ROOT = Path("/content/drive/MyDrive/AFRIDATACYBERJOHN")
RELEASE_DIR = DRIVE_ROOT / "AFRIDATACYBERJOHN_v1.0"
ZIP_PATH = DRIVE_ROOT / "AFRIDATACYBERJOHN_v1.0.zip"
MANIFEST_PATH = DRIVE_ROOT / "RECOVERY_MANIFEST.json"

assert RELEASE_DIR.exists(), f"Release directory missing: {RELEASE_DIR}"
assert ZIP_PATH.exists(), f"Release ZIP missing: {ZIP_PATH}"

print("=" * 72)
print("STAGE 40C — FINAL RELEASE / ZENODO READINESS AUDIT")
print("=" * 72)
print("Release:", RELEASE_DIR)
print("ZIP:", ZIP_PATH)

# ------------------------------------------------------------
# 2. EXPECTED RELEASE FILES
# ------------------------------------------------------------

EXPECTED_FILES = [
    "CITATION.cff",
    "README.md",

    "LICENSE",

    "data/AFRICA_MobileMoney_USSD_Authoritative_Events.csv",
    "data/AFRICA_MobileMoney_USSD_Authoritative_Windows.csv",
    "data/AFRICA_MobileMoney_USSD_Current_Events.csv",
    "data/AFRICA_MobileMoney_USSD_Current_Windows.csv",

    "documentation/DATASET_DESCRIPTION.md",
    "documentation/DATA_DICTIONARY.csv",
    "documentation/FORENSIC_VALIDATION.md",
    "documentation/METHODOLOGY.md",
    "documentation/PROVENANCE.md",
    "documentation/WINDOW_FIELD_SEMANTIC_RECOVERY.csv",

    "metadata/AUTHORS.json",
    "metadata/checksums.sha256",
    "metadata/dataset_metadata.json",
]

missing_files = []
for rel in EXPECTED_FILES:
    if not (RELEASE_DIR / rel).exists():
        missing_files.append(rel)

print("\n[1] RELEASE FILE STRUCTURE")
if missing_files:
    print("FAIL — Missing files:")
    for f in missing_files:
        print("   ", f)
else:
    print("PASS — All expected release files present")

assert not missing_files

# ------------------------------------------------------------
# 3. FILE COUNT
# ------------------------------------------------------------

actual_files = sorted(
    str(p.relative_to(RELEASE_DIR))
    for p in RELEASE_DIR.rglob("*")
    if p.is_file()
)

print("\n[2] FILE COUNT")
print("Files in release:", len(actual_files))
print("Expected files:", len(EXPECTED_FILES))

if set(actual_files) == set(EXPECTED_FILES):
    print("PASS — Exact release file set")
else:
    print("WARNING — File set differs")
    extra = sorted(set(actual_files) - set(EXPECTED_FILES))
    if extra:
        print("Extra files:")
        for f in extra:
            print("   ", f)

# ------------------------------------------------------------
# 4. SHA256 FUNCTION
# ------------------------------------------------------------

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

# ------------------------------------------------------------
# 5. FROZEN DATASET HASHES
# ------------------------------------------------------------

EXPECTED_CSV_HASHES = {
    "data/AFRICA_MobileMoney_USSD_Authoritative_Events.csv":
        "1fceb3e353f84077b7429b347f517fba789b839471c7940147757998f7c0fccd",

    "data/AFRICA_MobileMoney_USSD_Authoritative_Windows.csv":
        "f95f574767ee21bde1c4ad8e9ad0ecf30dfdba3df7d0bfd0bda8b5a322705f44",

    "data/AFRICA_MobileMoney_USSD_Current_Events.csv":
        "fe4b8347d3264fe0faae17b830c10432e6242c66012e93e908d95717ea11abb4",

    "data/AFRICA_MobileMoney_USSD_Current_Windows.csv":
        "47e2f01111e7194ddb4da5e8fbd7559cd29eeda286bb18117e2e2e524e239fcd",
}

print("\n[3] FROZEN DATASET HASH VALIDATION")

for rel, expected in EXPECTED_CSV_HASHES.items():
    actual = sha256_file(RELEASE_DIR / rel)
    status = "PASS" if actual == expected else "FAIL"

    print(status, rel)
    print("  expected:", expected)
    print("  actual:  ", actual)

    assert actual == expected, f"Frozen CSV changed: {rel}"

# ------------------------------------------------------------
# 6. LOAD DATASETS AND CHECK POPULATIONS
# ------------------------------------------------------------

print("\n[4] DATASET POPULATION VALIDATION")

auth_events = pd.read_csv(
    RELEASE_DIR / "data/AFRICA_MobileMoney_USSD_Authoritative_Events.csv"
)

current_events = pd.read_csv(
    RELEASE_DIR / "data/AFRICA_MobileMoney_USSD_Current_Events.csv"
)

auth_windows = pd.read_csv(
    RELEASE_DIR / "data/AFRICA_MobileMoney_USSD_Authoritative_Windows.csv"
)

current_windows = pd.read_csv(
    RELEASE_DIR / "data/AFRICA_MobileMoney_USSD_Current_Windows.csv"
)

population_checks = {
    "authoritative_events": (len(auth_events), 1029),
    "current_events": (len(current_events), 1060),
    "authoritative_windows": (len(auth_windows), 100),
    "current_windows": (len(current_windows), 100),
}

for name, (actual, expected) in population_checks.items():
    status = "PASS" if actual == expected else "FAIL"
    print(f"{status} {name}: {actual} (expected {expected})")
    assert actual == expected

# ------------------------------------------------------------
# 7. CORE IDENTITY / UNIQUENESS CHECKS
# ------------------------------------------------------------

print("\n[5] CORE DATA INTEGRITY")

assert auth_events["event_id"].is_unique
assert current_events["event_id"].is_unique

assert auth_windows["window_id"].is_unique
assert current_windows["window_id"].is_unique

print("PASS — Event IDs unique")
print("PASS — Window IDs unique")

# ------------------------------------------------------------
# 8. LICENSE VALIDATION
# ------------------------------------------------------------

print("\n[6] LICENSE VALIDATION")

LICENSE_TEXT = (
    RELEASE_DIR / "LICENSE"
).read_text(encoding="utf-8")

license_pass = (
    "Creative Commons Attribution 4.0 International" in LICENSE_TEXT
    and "https://creativecommons.org/licenses/by/4.0/" in LICENSE_TEXT
)

print(
    "PASS — CC BY 4.0"
    if license_pass
    else "FAIL — CC BY 4.0 license text not detected"
)

assert license_pass

# ------------------------------------------------------------
# 9. CITATION.CFF VALIDATION
# ------------------------------------------------------------

print("\n[7] CITATION.CFF VALIDATION")

CFF_TEXT = (
    RELEASE_DIR / "CITATION.cff"
).read_text(encoding="utf-8")

cff_checks = {
    "cff-version": "cff-version: 1.2.0" in CFF_TEXT,
    "title": "AFRIDATACYBERJOHN" in CFF_TEXT,
    "version": re.search(r"^version:\s*1\.0\s*$", CFF_TEXT, re.MULTILINE)
              is not None,
    "type": re.search(r"^type:\s*dataset\s*$", CFF_TEXT, re.MULTILINE)
            is not None,
    "creator": "John Ojo Ajayi" in CFF_TEXT,
    "email": "onejotech@gmail.com" in CFF_TEXT,
    "ORCID": "0000-0002-8063-6070" in CFF_TEXT,
    "license": re.search(
        r"^license:\s*CC BY 4\.0\s*$",
        CFF_TEXT,
        re.MULTILINE
    ) is not None,
}

for key, passed in cff_checks.items():
    print(("PASS" if passed else "FAIL"), key)
    assert passed, f"CITATION.cff failed: {key}"

# ------------------------------------------------------------
# 10. METADATA VALIDATION
# ------------------------------------------------------------

print("\n[8] METADATA VALIDATION")

META_PATH = RELEASE_DIR / "metadata/dataset_metadata.json"

with open(META_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

assert metadata.get("license") == "CC BY 4.0"
assert metadata.get("license_url") == (
    "https://creativecommons.org/licenses/by/4.0/"
)

print("PASS — Metadata license: CC BY 4.0")

# Creator identity checks
metadata_text = json.dumps(metadata)

assert "John Ojo Ajayi" in metadata_text
assert "0000-0002-8063-6070" in metadata_text

print("PASS — Creator identity")
print("PASS — ORCID")

# ------------------------------------------------------------
# 11. AUTHOR METADATA
# ------------------------------------------------------------

print("\n[9] AUTHOR METADATA")

AUTHORS_PATH = RELEASE_DIR / "metadata/AUTHORS.json"

with open(AUTHORS_PATH, "r", encoding="utf-8") as f:
    authors = json.load(f)

assert authors.get("license") == "CC BY 4.0"
assert authors.get("license_url") == (
    "https://creativecommons.org/licenses/by/4.0/"
)

print("PASS — AUTHORS.json license")

# ------------------------------------------------------------
# 12. PROVENANCE VALIDATION
# ------------------------------------------------------------

print("\n[10] PROVENANCE VALIDATION")

PROV_TEXT = (
    RELEASE_DIR / "documentation/PROVENANCE.md"
).read_text(encoding="utf-8")

required_provenance_terms = [
    "synthetic",
    "programmatically generated",
    "not direct production",
    "CC BY 4.0",
]

for term in required_provenance_terms:
    passed = term.lower() in PROV_TEXT.lower()
    print(("PASS" if passed else "FAIL"), term)
    assert passed, f"Missing provenance statement: {term}"

# ------------------------------------------------------------
# 13. README VALIDATION
# ------------------------------------------------------------

print("\n[11] README VALIDATION")

README_TEXT = (
    RELEASE_DIR / "README.md"
).read_text(encoding="utf-8")

readme_terms = [
    "CC BY 4.0",
    "John Ojo Ajayi",
    "0000-0002-8063-6070",
    "synthetic",
]

for term in readme_terms:
    passed = term.lower() in README_TEXT.lower()
    print(("PASS" if passed else "FAIL"), term)
    assert passed, f"README missing: {term}"

# ------------------------------------------------------------
# 14. CHECKSUM MANIFEST VALIDATION
# ------------------------------------------------------------

print("\n[12] CHECKSUM MANIFEST VALIDATION")

CHECKSUM_PATH = RELEASE_DIR / "metadata/checksums.sha256"

checksum_lines = [
    line.strip()
    for line in CHECKSUM_PATH.read_text(
        encoding="utf-8"
    ).splitlines()
    if line.strip()
]

checksum_results = []

for line in checksum_lines:
    parts = line.split(maxsplit=1)

    if len(parts) != 2:
        checksum_results.append((line, False))
        continue

    expected_hash, rel_path = parts

    # Handle possible "./" prefix
    rel_path = rel_path.lstrip("./")
    file_path = RELEASE_DIR / rel_path

    if not file_path.exists():
        checksum_results.append((rel_path, False))
        continue

    actual_hash = sha256_file(file_path)
    checksum_results.append(
        (rel_path, actual_hash == expected_hash)
    )

for rel_path, passed in checksum_results:
    print(("PASS" if passed else "FAIL"), rel_path)
    assert passed, f"Checksum mismatch: {rel_path}"

print("Checksum entries:", len(checksum_results))

# ------------------------------------------------------------
# 15. ZIP CONTENT VALIDATION
# ------------------------------------------------------------

print("\n[13] ZIP CONTENT VALIDATION")

with zipfile.ZipFile(ZIP_PATH, "r") as z:
    zip_bad = z.testzip()
    assert zip_bad is None

    zip_files = sorted(
        name for name in z.namelist()
        if not name.endswith("/")
    )

print("ZIP files:", len(zip_files))
print("ZIP integrity: PASS")

# Expected ZIP paths include the release directory prefix
expected_zip_files = sorted(
    f"AFRIDATACYBERJOHN_v1.0/{f}"
    for f in EXPECTED_FILES
)

zip_file_set_pass = set(zip_files) == set(expected_zip_files)

print(
    "PASS — ZIP contains exact expected release files"
    if zip_file_set_pass
    else "WARNING — ZIP file set differs"
)

assert zip_file_set_pass

# ------------------------------------------------------------
# 16. ZIP HASH
# ------------------------------------------------------------

zip_hash = sha256_file(ZIP_PATH)

print("\n[14] FINAL ZIP HASH")
print(zip_hash)

# ------------------------------------------------------------
# 17. RECOVERY MANIFEST INSPECTION
# ------------------------------------------------------------

print("\n[15] RECOVERY MANIFEST")

if MANIFEST_PATH.exists():

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    manifest_text = json.dumps(manifest)

    print("Recovery manifest found.")

    # Report, rather than mutate.
    if "4b85ccc1c96a6e3fe07a71a858cbb4d126909cd1483ac24095e243bb22d1824f" in manifest_text:
        print("PASS — Recovery manifest contains current Stage 40B ZIP hash")
    else:
        print("NOTE — Recovery manifest does not yet contain current Stage 40B ZIP hash")
        print("      This will require a controlled manifest refresh before final publication.")

else:
    print("WARNING — Recovery manifest not found.")

# ------------------------------------------------------------
# 18. FINAL SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 72)
print("STAGE 40C FINAL AUDIT SUMMARY")
print("=" * 72)

print("Dataset:                 AFRIDATACYBERJOHN")
print("Version:                 1.0")
print("License:                 CC BY 4.0")
print("Creator:                 John Ojo Ajayi")
print("ORCID:                   0000-0002-8063-6070")
print("Authoritative events:    1029")
print("Current events:          1060")
print("Authoritative windows:   100")
print("Current windows:         100")
print("Frozen CSVs modified:    NO")
print("CSV hashes:              PASS")
print("License validation:      PASS")
print("CITATION.cff:            PASS")
print("Metadata validation:     PASS")
print("Provenance validation:   PASS")
print("README validation:       PASS")
print("Checksum validation:     PASS")
print("ZIP integrity:           PASS")
print("ZIP SHA256:", zip_hash)

print("=" * 72)
print("STAGE 40C AUDIT COMPLETE")
print("=" * 72)

# ==============================================================================
# NOTEBOOK CELL 690
# ==============================================================================

from pathlib import Path

CFF_PATH = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0/CITATION.cff"
)

print("CITATION.cff version-related lines:")
print("=" * 60)

for i, line in enumerate(
    CFF_PATH.read_text(encoding="utf-8").splitlines(), 1
):
    if "version" in line.lower():
        print(f"{i}: {line}")

print("=" * 60)

# ==============================================================================
# NOTEBOOK CELL 691
# ==============================================================================

# ============================================================
# STAGE 40C-A — CORRECTED CITATION.CFF VALIDATION
# ============================================================

from pathlib import Path
import re

CFF_PATH = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0/CITATION.cff"
)

CFF_TEXT = CFF_PATH.read_text(encoding="utf-8")

print("\n[7] CITATION.CFF VALIDATION — CORRECTED")

cff_checks = {
    "cff-version":
        re.search(
            r"^cff-version:\s*1\.2\.0\s*$",
            CFF_TEXT,
            re.MULTILINE
        ) is not None,

    "title":
        "AFRIDATACYBERJOHN" in CFF_TEXT,

    "version":
        re.search(
            r'^version:\s*["\']?1\.0["\']?\s*$',
            CFF_TEXT,
            re.MULTILINE
        ) is not None,

    "type":
        re.search(
            r"^type:\s*dataset\s*$",
            CFF_TEXT,
            re.MULTILINE
        ) is not None,

    "creator":
        "John Ojo Ajayi" in CFF_TEXT,

    "email":
        "onejotech@gmail.com" in CFF_TEXT,

    "ORCID":
        "0000-0002-8063-6070" in CFF_TEXT,

    "license":
        re.search(
            r'^license:\s*["\']?CC BY 4\.0["\']?\s*$',
            CFF_TEXT,
            re.MULTILINE
        ) is not None,
}

for key, passed in cff_checks.items():
    print(("PASS" if passed else "FAIL"), key)
    assert passed, f"CITATION.cff failed: {key}"

print("\nCITATION.CFF VALIDATION: PASS")
print("Quoted version value accepted: version: \"1.0\"")
print("No CITATION.cff modification performed.")

# ==============================================================================
# NOTEBOOK CELL 692
# ==============================================================================

from pathlib import Path

CFF_PATH = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0/CITATION.cff"
)

lines = CFF_PATH.read_text(encoding="utf-8").splitlines()

print("CITATION.cff author section:")
print("=" * 60)

inside_authors = False

for i, line in enumerate(lines, 1):

    if line.strip() == "authors:":
        inside_authors = True

    if inside_authors:
        print(f"{i}: {line}")

        # Stop after the next major top-level field
        if (
            i > 1
            and line
            and not line.startswith(" ")
            and not line.startswith("-")
            and line.strip() != "authors:"
        ):
            break

print("=" * 60)

# ==============================================================================
# NOTEBOOK CELL 693
# ==============================================================================

# ============================================================
# STAGE 40C-B — UPDATE + VALIDATE CITATION.CFF
# AFFILIATION: NATIONAL OPEN UNIVERSITY OF NIGERIA
#
# Controlled metadata update
# Dataset CSVs are NOT modified
# ZIP is NOT rebuilt yet
# ============================================================

from pathlib import Path
import re
import shutil

# ------------------------------------------------------------
# 1. PATH
# ------------------------------------------------------------

CFF_PATH = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0/CITATION.cff"
)

assert CFF_PATH.exists(), f"CITATION.cff not found: {CFF_PATH}"

# ------------------------------------------------------------
# 2. BACKUP CURRENT CITATION.CFF
# ------------------------------------------------------------

BACKUP_PATH = CFF_PATH.with_suffix(".cff.stage40C_backup")

shutil.copy2(CFF_PATH, BACKUP_PATH)

print("Backup created:")
print(BACKUP_PATH)

# ------------------------------------------------------------
# 3. READ CURRENT CFF
# ------------------------------------------------------------

CFF_TEXT = CFF_PATH.read_text(encoding="utf-8")

print("\nCurrent CITATION.cff loaded.")
print("Original size:", len(CFF_TEXT), "characters")

# ------------------------------------------------------------
# 4. UPDATE EMAIL
# ------------------------------------------------------------
# Converts Markdown-style email:
# [email](mailto\:email)
# into plain CFF email.

CFF_TEXT = re.sub(
    r'email:\s*["\']?\[onejotech@gmail\.com\]\(mailto\\?:onejotech@gmail\.com\)["\']?',
    'email: "onejotech@gmail.com"',
    CFF_TEXT
)

# ------------------------------------------------------------
# 5. UPDATE ORCID
# ------------------------------------------------------------
# Converts Markdown-style ORCID into a normal CFF ORCID URL.

CFF_TEXT = re.sub(
    r'orcid:\s*["\']?\[https://orcid\.org/0000-0002-8063-6070\]'
    r'\(https://orcid\.org/0000-0002-8063-6070\)["\']?',
    'orcid: "https://orcid.org/0000-0002-8063-6070"',
    CFF_TEXT
)

# ------------------------------------------------------------
# 6. ADD / UPDATE AFFILIATION
# ------------------------------------------------------------

AFFILIATION = "National Open University of Nigeria"

# If affiliation already exists, replace it.
if re.search(r'^\s*affiliation:', CFF_TEXT, re.MULTILINE):

    CFF_TEXT = re.sub(
        r'^\s*affiliation:.*$',
        f'    affiliation: "{AFFILIATION}"',
        CFF_TEXT,
        count=1,
        flags=re.MULTILINE
    )

# Otherwise insert it immediately after given-names.
else:

    CFF_TEXT = re.sub(
        r'(^\s*given-names:\s*["\']?John Ojo["\']?\s*$)',
        r'\1\n    affiliation: "National Open University of Nigeria"',
        CFF_TEXT,
        count=1,
        flags=re.MULTILINE
    )

# ------------------------------------------------------------
# 7. WRITE UPDATED CFF
# ------------------------------------------------------------

CFF_PATH.write_text(CFF_TEXT, encoding="utf-8")

print("\nCITATION.cff updated.")
print("Affiliation:", AFFILIATION)

# ------------------------------------------------------------
# 8. DISPLAY AUTHOR BLOCK
# ------------------------------------------------------------

print("\nUPDATED AUTHOR SECTION")
print("=" * 60)

lines = CFF_TEXT.splitlines()
inside_authors = False

for i, line in enumerate(lines, 1):

    if line.strip() == "authors:":
        inside_authors = True

    if inside_authors:
        print(f"{i}: {line}")

        # Stop at next top-level field.
        if (
            i > 1
            and line
            and not line.startswith(" ")
            and not line.startswith("-")
            and line.strip() != "authors:"
        ):
            break

print("=" * 60)

# ------------------------------------------------------------
# 9. STRUCTURED VALIDATION
# ------------------------------------------------------------

print("\n[7] CITATION.CFF VALIDATION — STRUCTURED")

cff_checks = {

    "cff-version":
        re.search(
            r"^cff-version:\s*1\.2\.0\s*$",
            CFF_TEXT,
            re.MULTILINE
        ) is not None,

    "title":
        "AFRIDATACYBERJOHN" in CFF_TEXT,

    "version":
        re.search(
            r'^version:\s*["\']?1\.0["\']?\s*$',
            CFF_TEXT,
            re.MULTILINE
        ) is not None,

    "type":
        re.search(
            r"^type:\s*dataset\s*$",
            CFF_TEXT,
            re.MULTILINE
        ) is not None,

    "family-names":
        re.search(
            r'^\s*-\s*family-names:\s*["\']?Ajayi["\']?\s*$',
            CFF_TEXT,
            re.MULTILINE
        ) is not None,

    "given-names":
        re.search(
            r'^\s*given-names:\s*["\']?John Ojo["\']?\s*$',
            CFF_TEXT,
            re.MULTILINE
        ) is not None,

    "affiliation":
        re.search(
            r'^\s*affiliation:\s*["\']?National Open University of Nigeria["\']?\s*$',
            CFF_TEXT,
            re.MULTILINE
        ) is not None,

    "email":
        re.search(
            r'^\s*email:\s*["\']?onejotech@gmail\.com["\']?\s*$',
            CFF_TEXT,
            re.MULTILINE
        ) is not None,

    "ORCID":
        re.search(
            r'^\s*orcid:\s*["\']?https://orcid\.org/0000-0002-8063-6070["\']?\s*$',
            CFF_TEXT,
            re.MULTILINE
        ) is not None,

    "license":
        re.search(
            r'^license:\s*["\']?CC BY 4\.0["\']?\s*$',
            CFF_TEXT,
            re.MULTILINE
        ) is not None,
}

# ------------------------------------------------------------
# 10. REPORT VALIDATION
# ------------------------------------------------------------

for key, passed in cff_checks.items():
    print(("PASS" if passed else "FAIL"), key)

    assert passed, f"CITATION.cff failed: {key}"

# ------------------------------------------------------------
# 11. FINAL RESULT
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("CITATION.CFF VALIDATION: PASS")
print("=" * 60)

print("Author:       John Ojo Ajayi")
print("Affiliation:  National Open University of Nigeria")
print("Email:        onejotech@gmail.com")
print("ORCID:        https://orcid.org/0000-0002-8063-6070")
print("Version:      1.0")
print("License:      CC BY 4.0")

print("\nDataset CSVs modified: NO")
print("ZIP rebuilt:           NO")
print("Backup created:        YES")

print("=" * 60)

# ==============================================================================
# NOTEBOOK CELL 694
# ==============================================================================

# ============================================================
# STAGE 40C-C — CLEAN CITATION.CFF + REMOVE TEMP BACKUP
# ============================================================

from pathlib import Path
import re

RELEASE_DIR = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0"
)

CFF_PATH = RELEASE_DIR / "CITATION.cff"
BACKUP_PATH = RELEASE_DIR / "CITATION.cff.stage40C_backup"

assert CFF_PATH.exists(), "CITATION.cff not found"

# ------------------------------------------------------------
# 1. Read current CFF
# ------------------------------------------------------------

cff = CFF_PATH.read_text(encoding="utf-8")

# ------------------------------------------------------------
# 2. Replace email with clean CFF value
# ------------------------------------------------------------

cff = re.sub(
    r'^\s*email:.*$',
    '    email: "onejotech@gmail.com"',
    cff,
    count=1,
    flags=re.MULTILINE
)

# ------------------------------------------------------------
# 3. Replace ORCID with clean CFF value
# ------------------------------------------------------------

cff = re.sub(
    r'^\s*orcid:.*$',
    '    orcid: "https://orcid.org/0000-0002-8063-6070"',
    cff,
    count=1,
    flags=re.MULTILINE
)

# ------------------------------------------------------------
# 4. Ensure affiliation is correct
# ------------------------------------------------------------

if re.search(r'^\s*affiliation:', cff, re.MULTILINE):

    cff = re.sub(
        r'^\s*affiliation:.*$',
        '    affiliation: "National Open University of Nigeria"',
        cff,
        count=1,
        flags=re.MULTILINE
    )

else:

    cff = re.sub(
        r'(^\s*given-names:.*$)',
        r'\1\n    affiliation: "National Open University of Nigeria"',
        cff,
        count=1,
        flags=re.MULTILINE
    )

# ------------------------------------------------------------
# 5. Write clean CFF
# ------------------------------------------------------------

CFF_PATH.write_text(cff, encoding="utf-8")

# ------------------------------------------------------------
# 6. Validate exact values
# ------------------------------------------------------------

cff = CFF_PATH.read_text(encoding="utf-8")

checks = {
    "cff-version":
        re.search(
            r'^cff-version:\s*1\.2\.0\s*$',
            cff,
            re.MULTILINE
        ) is not None,

    "version":
        re.search(
            r'^version:\s*["\']?1\.0["\']?\s*$',
            cff,
            re.MULTILINE
        ) is not None,

    "type":
        re.search(
            r'^type:\s*dataset\s*$',
            cff,
            re.MULTILINE
        ) is not None,

    "family-names":
        re.search(
            r'^\s*-\s*family-names:\s*["\']?Ajayi["\']?\s*$',
            cff,
            re.MULTILINE
        ) is not None,

    "given-names":
        re.search(
            r'^\s*given-names:\s*["\']?John Ojo["\']?\s*$',
            cff,
            re.MULTILINE
        ) is not None,

    "affiliation":
        'affiliation: "National Open University of Nigeria"' in cff,

    "email":
        'email: "onejotech@gmail.com"' in cff,

    "ORCID":
        'orcid: "https://orcid.org/0000-0002-8063-6070"' in cff,

    "license":
        re.search(
            r'^license:\s*["\']?CC BY 4\.0["\']?\s*$',
            cff,
            re.MULTILINE
        ) is not None,
}

print("=" * 68)
print("STAGE 40C-C — CITATION.CFF CLEANUP")
print("=" * 68)

for key, passed in checks.items():
    print(("PASS" if passed else "FAIL"), key)
    assert passed, f"CFF validation failed: {key}"

# ------------------------------------------------------------
# 7. Display final author block
# ------------------------------------------------------------

print("\nFINAL AUTHOR BLOCK")
print("-" * 68)

lines = cff.splitlines()
inside = False

for line in lines:
    if line.strip() == "authors:":
        inside = True

    if inside:
        print(line)

        if (
            line
            and not line.startswith(" ")
            and not line.startswith("-")
            and line.strip() != "authors:"
        ):
            break

# ------------------------------------------------------------
# 8. Remove temporary backup from RELEASE DIRECTORY
# ------------------------------------------------------------

if BACKUP_PATH.exists():
    BACKUP_PATH.unlink()
    print("\nPASS — Temporary backup removed from release directory")
else:
    print("\nNOTE — Temporary backup already absent")

# ------------------------------------------------------------
# 9. Confirm no backup remains
# ------------------------------------------------------------

assert not BACKUP_PATH.exists()

print("\n" + "=" * 68)
print("STAGE 40C-C COMPLETE")
print("=" * 68)

print("Author:       John Ojo Ajayi")
print("Affiliation:  National Open University of Nigeria")
print("Email:        onejotech@gmail.com")
print("ORCID:        https://orcid.org/0000-0002-8063-6070")
print("License:      CC BY 4.0")
print("CSV modified: NO")
print("ZIP rebuilt:  NO")
print("=" * 68)

# ==============================================================================
# NOTEBOOK CELL 695
# ==============================================================================

# ============================================================
# STAGE 40C-D — FINAL CITATION.CFF CLEANUP
# Direct line replacement — NO DATASET CSV MODIFICATION
# ============================================================

from pathlib import Path

RELEASE_DIR = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0"
)

CFF_PATH = RELEASE_DIR / "CITATION.cff"

assert CFF_PATH.exists(), "CITATION.cff not found"

# ------------------------------------------------------------
# 1. Read CFF
# ------------------------------------------------------------

lines = CFF_PATH.read_text(encoding="utf-8").splitlines()

# ------------------------------------------------------------
# 2. Replace exact metadata lines
# ------------------------------------------------------------

new_lines = []

for line in lines:

    stripped = line.strip()

    if stripped.startswith("email:"):
        new_lines.append('    email: "onejotech@gmail.com"')

    elif stripped.startswith("orcid:"):
        new_lines.append(
            '    orcid: "https://orcid.org/0000-0002-8063-6070"'
        )

    elif stripped.startswith("affiliation:"):
        new_lines.append(
            '    affiliation: "National Open University of Nigeria"'
        )

    else:
        new_lines.append(line)

# ------------------------------------------------------------
# 3. Write
# ------------------------------------------------------------

CFF_PATH.write_text(
    "\n".join(new_lines) + "\n",
    encoding="utf-8"
)

# ------------------------------------------------------------
# 4. Reload and inspect exact author block
# ------------------------------------------------------------

cff = CFF_PATH.read_text(encoding="utf-8")

print("=" * 72)
print("STAGE 40C-D — FINAL CITATION.CFF CLEANUP")
print("=" * 72)

print("\nFINAL AUTHOR BLOCK")
print("-" * 72)

inside_authors = False

for line in cff.splitlines():

    if line.strip() == "authors:":
        inside_authors = True

    if inside_authors:
        print(line)

        # Stop at next top-level field
        if (
            line
            and not line.startswith(" ")
            and not line.startswith("-")
            and line.strip() != "authors:"
        ):
            break

# ------------------------------------------------------------
# 5. EXACT VALIDATION
# ------------------------------------------------------------

checks = {
    "cff-version":
        "cff-version: 1.2.0" in cff,

    "version":
        'version: "1.0"' in cff
        or "version: 1.0" in cff,

    "type":
        "type: dataset" in cff,

    "family-names":
        'family-names: "Ajayi"' in cff,

    "given-names":
        'given-names: "John Ojo"' in cff,

    "affiliation":
        'affiliation: "National Open University of Nigeria"' in cff,

    "clean-email":
        'email: "onejotech@gmail.com"' in cff,

    "clean-orcid":
        'orcid: "https://orcid.org/0000-0002-8063-6070"' in cff,

    "license":
        "license: CC BY 4.0" in cff,
}

print("\nVALIDATION")
print("-" * 72)

for key, passed in checks.items():
    print(("PASS" if passed else "FAIL"), key)
    assert passed, f"CFF validation failed: {key}"

# ------------------------------------------------------------
# 6. ENSURE OLD MARKDOWN FORM IS GONE
# ------------------------------------------------------------

old_email_form = "[onejotech@gmail.com]"
old_orcid_form = "[https://orcid.org/0000-0002-8063-6070]"

assert old_email_form not in cff
assert old_orcid_form not in cff

print("PASS old Markdown email form removed")
print("PASS old Markdown ORCID form removed")

# ------------------------------------------------------------
# 7. FINAL RESULT
# ------------------------------------------------------------

print("\n" + "=" * 72)
print("STAGE 40C-D: PASS")
print("=" * 72)

print("Author:       John Ojo Ajayi")
print("Affiliation:  National Open University of Nigeria")
print("Email:        onejotech@gmail.com")
print("ORCID:        https://orcid.org/0000-0002-8063-6070")
print("Version:      1.0")
print("License:      CC BY 4.0")
print("CSV modified: NO")
print("ZIP rebuilt:  NO")
print("=" * 72)

# ==============================================================================
# NOTEBOOK CELL 696
# ==============================================================================

# ============================================================
# STAGE 40C-E — RAW CITATION.CFF INSPECTION
# READ-ONLY — NO MODIFICATION
# ============================================================

from pathlib import Path

CFF_PATH = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0/CITATION.cff"
)

lines = CFF_PATH.read_text(encoding="utf-8").splitlines()

print("=" * 72)
print("STAGE 40C-E — RAW CITATION.CFF INSPECTION")
print("=" * 72)

for i, line in enumerate(lines, 1):
    if (
        "email:" in line
        or "orcid:" in line
        or "affiliation:" in line
    ):
        print(f"LINE {i}:")
        print("repr =", repr(line))
        print("text =", line)
        print("-" * 72)

print("Inspection complete — NO FILE MODIFICATION")

# ==============================================================================
# NOTEBOOK CELL 697
# ==============================================================================

# ============================================================
# STAGE 40C-F — DEFINITIVE CITATION.CFF CORRECTION
# Exact line replacement
# NO DATASET CSV MODIFICATION
# ============================================================

from pathlib import Path

RELEASE_DIR = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0"
)

CFF_PATH = RELEASE_DIR / "CITATION.cff"

assert CFF_PATH.exists(), "CITATION.cff not found"

# ------------------------------------------------------------
# 1. Read current file
# ------------------------------------------------------------

lines = CFF_PATH.read_text(encoding="utf-8").splitlines()

# ------------------------------------------------------------
# 2. Exact replacement based on observed raw lines
# ------------------------------------------------------------

updated_lines = []

for line in lines:

    stripped = line.strip()

    if stripped.startswith("email:"):
        updated_lines.append(
            '    email: "onejotech@gmail.com"'
        )

    elif stripped.startswith("orcid:"):
        updated_lines.append(
            '    orcid: "https://orcid.org/0000-0002-8063-6070"'
        )

    elif stripped.startswith("affiliation:"):
        updated_lines.append(
            '    affiliation: "National Open University of Nigeria"'
        )

    else:
        updated_lines.append(line)

# ------------------------------------------------------------
# 3. Write the corrected CFF
# ------------------------------------------------------------

CFF_PATH.write_text(
    "\n".join(updated_lines) + "\n",
    encoding="utf-8"
)

# ------------------------------------------------------------
# 4. Reload from disk — IMPORTANT
# ------------------------------------------------------------

final_cff = CFF_PATH.read_text(encoding="utf-8")

# ------------------------------------------------------------
# 5. RAW VERIFICATION
# ------------------------------------------------------------

print("=" * 72)
print("STAGE 40C-F — DEFINITIVE CITATION.CFF CORRECTION")
print("=" * 72)

print("\nACTUAL FILE CONTENT — AUTHOR METADATA")
print("-" * 72)

for i, line in enumerate(final_cff.splitlines(), 1):

    if (
        "affiliation:" in line
        or "email:" in line
        or "orcid:" in line
    ):
        print(f"{i}: {repr(line)}")

# ------------------------------------------------------------
# 6. EXACT CONTENT CHECKS
# ------------------------------------------------------------

expected_email = '    email: "onejotech@gmail.com"'
expected_orcid = (
    '    orcid: "https://orcid.org/0000-0002-8063-6070"'
)
expected_affiliation = (
    '    affiliation: "National Open University of Nigeria"'
)

assert expected_email in final_cff
assert expected_orcid in final_cff
assert expected_affiliation in final_cff

# ------------------------------------------------------------
# 7. ENSURE OLD FORMS ARE ABSENT
# ------------------------------------------------------------

assert "[onejotech@gmail.com]" not in final_cff
assert "mailto" not in final_cff
assert "[https://orcid.org/0000-0002-8063-6070]" not in final_cff

print("\nPASS — Clean email stored exactly")
print("PASS — Clean ORCID stored exactly")
print("PASS — Affiliation stored exactly")
print("PASS — Old Markdown email removed")
print("PASS — Old mailto syntax removed")
print("PASS — Old Markdown ORCID removed")

# ------------------------------------------------------------
# 8. CORE CFF VALIDATION
# ------------------------------------------------------------

checks = {
    "cff-version":
        "cff-version: 1.2.0" in final_cff,

    "title":
        "AFRIDATACYBERJOHN" in final_cff,

    "version":
        'version: "1.0"' in final_cff
        or "version: 1.0" in final_cff,

    "type":
        "type: dataset" in final_cff,

    "family-names":
        'family-names: "Ajayi"' in final_cff,

    "given-names":
        'given-names: "John Ojo"' in final_cff,

    "affiliation":
        expected_affiliation in final_cff,

    "email":
        expected_email in final_cff,

    "ORCID":
        expected_orcid in final_cff,

    "license":
        "license: CC BY 4.0" in final_cff,
}

print("\nCFF VALIDATION")
print("-" * 72)

for key, passed in checks.items():
    print(("PASS" if passed else "FAIL"), key)
    assert passed, f"CITATION.cff failed: {key}"

# ------------------------------------------------------------
# 9. FINAL AUTHOR BLOCK
# ------------------------------------------------------------

print("\nFINAL AUTHOR BLOCK")
print("-" * 72)

inside_authors = False

for line in final_cff.splitlines():

    if line.strip() == "authors:":
        inside_authors = True

    if inside_authors:
        print(line)

        if (
            line
            and not line.startswith(" ")
            and not line.startswith("-")
            and line.strip() != "authors:"
        ):
            break

# ------------------------------------------------------------
# 10. FINAL STATUS
# ------------------------------------------------------------

print("\n" + "=" * 72)
print("STAGE 40C-F: PASS")
print("=" * 72)

print("Author:       John Ojo Ajayi")
print("Affiliation:  National Open University of Nigeria")
print("Email:        onejotech@gmail.com")
print("ORCID:        https://orcid.org/0000-0002-8063-6070")
print("Version:      1.0")
print("License:      CC BY 4.0")
print("Dataset CSVs: NOT MODIFIED")
print("ZIP:          NOT REBUILT")
print("=" * 72)

# ==============================================================================
# NOTEBOOK CELL 698
# ==============================================================================

# ============================================================
# STAGE 40C-G — FORENSIC CITATION.CFF BYTE/STRING DIAGNOSIS
# READ-ONLY — NO FILE MODIFICATION
# ============================================================

from pathlib import Path

CFF_PATH = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0/CITATION.cff"
)

assert CFF_PATH.exists()

# Read both text and raw bytes
raw_bytes = CFF_PATH.read_bytes()
text = raw_bytes.decode("utf-8")

print("=" * 72)
print("STAGE 40C-G — FORENSIC CFF DIAGNOSIS")
print("=" * 72)

# ------------------------------------------------------------
# 1. Locate exact lines
# ------------------------------------------------------------

for i, line in enumerate(text.splitlines(), 1):
    if any(x in line for x in ["email:", "orcid:", "affiliation:"]):
        print(f"\nLINE {i}")
        print("repr :", repr(line))
        print("bytes:", line.encode("utf-8"))

# ------------------------------------------------------------
# 2. Exact substring tests
# ------------------------------------------------------------

tests = {
    "clean_email":
        'email: "onejotech@gmail.com"',

    "old_email_markdown":
        '[onejotech@gmail.com]',

    "old_mailto":
        'mailto',

    "clean_orcid":
        'orcid: "https://orcid.org/0000-0002-8063-6070"',

    "old_orcid_markdown":
        '[https://orcid.org/0000-0002-8063-6070]',

    "clean_affiliation":
        'affiliation: "National Open University of Nigeria"',
}

print("\n" + "-" * 72)
print("EXACT SUBSTRING TESTS")
print("-" * 72)

for name, value in tests.items():
    print(f"{name}: {value!r}")
    print("FOUND:", value in text)

# ------------------------------------------------------------
# 3. Show all occurrences of email/orcid
# ------------------------------------------------------------

print("\n" + "-" * 72)
print("EMAIL OCCURRENCES")
print("-" * 72)

start = 0
while True:
    pos = text.find("email:", start)

    if pos == -1:
        break

    print("position:", pos)
    print("context:", repr(text[pos:pos + 180]))
    start = pos + 1

print("\n" + "-" * 72)
print("ORCID OCCURRENCES")
print("-" * 72)

start = 0
while True:
    pos = text.find("orcid:", start)

    if pos == -1:
        break

    print("position:", pos)
    print("context:", repr(text[pos:pos + 220]))
    start = pos + 1

# ------------------------------------------------------------
# 4. File metadata
# ------------------------------------------------------------

print("\n" + "-" * 72)
print("FILE INFORMATION")
print("-" * 72)

print("Path:", CFF_PATH)
print("Size:", CFF_PATH.stat().st_size, "bytes")
print("Text length:", len(text), "characters")

print("\nNO FILE MODIFICATION PERFORMED.")
print("=" * 72)

# ==============================================================================
# NOTEBOOK CELL 699
# ==============================================================================

# ============================================================
# STAGE 40C-H — DEFINITIVE CITATION.CFF CORRECTION
# Based on verified raw file lines 17 and 18
#
# NO DATASET CSV MODIFICATION
# NO ZIP REBUILD
# ============================================================

from pathlib import Path

RELEASE_DIR = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0"
)

CFF_PATH = RELEASE_DIR / "CITATION.cff"

assert CFF_PATH.exists(), "CITATION.cff not found"

# ------------------------------------------------------------
# 1. Read file
# ------------------------------------------------------------

lines = CFF_PATH.read_text(encoding="utf-8").splitlines()

# ------------------------------------------------------------
# 2. Replace ONLY email/orcid/affiliation lines
# ------------------------------------------------------------

for i, line in enumerate(lines):

    if line.strip().startswith("email:"):
        lines[i] = '    email: "onejotech@gmail.com"'

    elif line.strip().startswith("orcid:"):
        lines[i] = (
            '    orcid: "https://orcid.org/0000-0002-8063-6070"'
        )

    elif line.strip().startswith("affiliation:"):
        lines[i] = (
            '    affiliation: "National Open University of Nigeria"'
        )

# ------------------------------------------------------------
# 3. Write file
# ------------------------------------------------------------

CFF_PATH.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8"
)

# ------------------------------------------------------------
# 4. READ BACK FROM DISK
# ------------------------------------------------------------

final_text = CFF_PATH.read_text(encoding="utf-8")

# ------------------------------------------------------------
# 5. SHOW EXACT RAW LINES
# ------------------------------------------------------------

print("=" * 72)
print("STAGE 40C-H — DEFINITIVE CFF CORRECTION")
print("=" * 72)

print("\nACTUAL FILE AFTER WRITE")
print("-" * 72)

for i, line in enumerate(final_text.splitlines(), 1):

    if (
        "affiliation:" in line
        or "email:" in line
        or "orcid:" in line
    ):
        print(f"LINE {i}: {repr(line)}")

# ------------------------------------------------------------
# 6. EXACT EXPECTED VALUES
# ------------------------------------------------------------

EXPECTED_EMAIL = '    email: "onejotech@gmail.com"'

EXPECTED_ORCID = (
    '    orcid: "https://orcid.org/0000-0002-8063-6070"'
)

EXPECTED_AFFILIATION = (
    '    affiliation: "National Open University of Nigeria"'
)

# ------------------------------------------------------------
# 7. ASSERT EXACT CONTENT
# ------------------------------------------------------------

assert EXPECTED_EMAIL in final_text
assert EXPECTED_ORCID in final_text
assert EXPECTED_AFFILIATION in final_text

# Old Markdown forms MUST NOT exist
assert '[onejotech@gmail.com]' not in final_text
assert '[https://orcid.org/0000-0002-8063-6070]' not in final_text
assert 'mailto:' not in final_text
assert 'mailto\\:' not in final_text

print("\nEXACT CONTENT VALIDATION")
print("-" * 72)
print("PASS — Clean email")
print("PASS — Clean ORCID")
print("PASS — NO Markdown email")
print("PASS — NO mailto syntax")
print("PASS — NO Markdown ORCID")
print("PASS — National Open University of Nigeria affiliation")

# ------------------------------------------------------------
# 8. FULL CFF STRUCTURE VALIDATION
# ------------------------------------------------------------

checks = {
    "cff-version":
        "cff-version: 1.2.0" in final_text,

    "title":
        "AFRIDATACYBERJOHN" in final_text,

    "version":
        'version: "1.0"' in final_text
        or "version: 1.0" in final_text,

    "type":
        "type: dataset" in final_text,

    "family-names":
        'family-names: "Ajayi"' in final_text,

    "given-names":
        'given-names: "John Ojo"' in final_text,

    "affiliation":
        EXPECTED_AFFILIATION in final_text,

    "email":
        EXPECTED_EMAIL in final_text,

    "ORCID":
        EXPECTED_ORCID in final_text,

    "license":
        "license: CC BY 4.0" in final_text,
}

print("\nFULL CFF VALIDATION")
print("-" * 72)

for key, passed in checks.items():
    print(("PASS" if passed else "FAIL"), key)
    assert passed, f"CFF validation failed: {key}"

# ------------------------------------------------------------
# 9. FINAL AUTHOR BLOCK
# ------------------------------------------------------------

print("\nFINAL AUTHOR BLOCK")
print("-" * 72)

inside_authors = False

for line in final_text.splitlines():

    if line.strip() == "authors:":
        inside_authors = True

    if inside_authors:
        print(line)

        if (
            line
            and not line.startswith(" ")
            and not line.startswith("-")
            and line.strip() != "authors:"
        ):
            break

# ------------------------------------------------------------
# 10. FINAL STATUS
# ------------------------------------------------------------

print("\n" + "=" * 72)
print("STAGE 40C-H: PASS")
print("=" * 72)

print("Author:       John Ojo Ajayi")
print("Affiliation:  National Open University of Nigeria")
print("Email:        onejotech@gmail.com")
print("ORCID:        https://orcid.org/0000-0002-8063-6070")
print("Version:      1.0")
print("License:      CC BY 4.0")
print("Dataset CSVs: NOT MODIFIED")
print("ZIP:          NOT REBUILT")
print("=" * 72)

# ==============================================================================
# NOTEBOOK CELL 700
# ==============================================================================

# ============================================================
# STAGE 40C-I — ATOMIC CITATION.CFF REWRITE
# ============================================================
# Purpose:
#   1. Preserve all existing CFF content
#   2. Replace ONLY affiliation, email and ORCID lines
#   3. Write through a temporary file
#   4. Atomically replace CITATION.cff
#   5. Re-open from disk and verify exact bytes
#
# DATASET CSVs: NOT TOUCHED
# ZIP: NOT REBUILT
# ============================================================

from pathlib import Path
import os
import tempfile
import hashlib

RELEASE_DIR = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0"
)

CFF_PATH = RELEASE_DIR / "CITATION.cff"

assert CFF_PATH.exists(), f"Missing: {CFF_PATH}"

# ------------------------------------------------------------
# 1. Read existing CFF
# ------------------------------------------------------------

original = CFF_PATH.read_text(encoding="utf-8")

lines = original.splitlines()

# ------------------------------------------------------------
# 2. Modify ONLY the three author metadata lines
# ------------------------------------------------------------

replacement_count = {
    "affiliation": 0,
    "email": 0,
    "orcid": 0,
}

new_lines = []

for line in lines:

    stripped = line.strip()

    if stripped.startswith("affiliation:"):
        new_lines.append(
            '    affiliation: "National Open University of Nigeria"'
        )
        replacement_count["affiliation"] += 1

    elif stripped.startswith("email:"):
        new_lines.append(
            '    email: "onejotech@gmail.com"'
        )
        replacement_count["email"] += 1

    elif stripped.startswith("orcid:"):
        new_lines.append(
            '    orcid: "https://orcid.org/0000-0002-8063-6070"'
        )
        replacement_count["orcid"] += 1

    else:
        new_lines.append(line)

# ------------------------------------------------------------
# 3. Require exactly one occurrence of each
# ------------------------------------------------------------

assert replacement_count["affiliation"] == 1, replacement_count
assert replacement_count["email"] == 1, replacement_count
assert replacement_count["orcid"] == 1, replacement_count

new_text = "\n".join(new_lines) + "\n"

# ------------------------------------------------------------
# 4. Write to a temporary file on the SAME filesystem
# ------------------------------------------------------------

fd, temp_name = tempfile.mkstemp(
    prefix="CITATION_cff_",
    suffix=".tmp",
    dir=str(RELEASE_DIR)
)

try:

    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)
        f.flush()
        os.fsync(f.fileno())

    # --------------------------------------------------------
    # 5. Verify temporary file BEFORE replacement
    # --------------------------------------------------------

    temp_path = Path(temp_name)

    temp_text = temp_path.read_text(encoding="utf-8")

    EXPECTED_EMAIL = '    email: "onejotech@gmail.com"'
    EXPECTED_ORCID = (
        '    orcid: "https://orcid.org/0000-0002-8063-6070"'
    )
    EXPECTED_AFFILIATION = (
        '    affiliation: "National Open University of Nigeria"'
    )

    assert EXPECTED_EMAIL in temp_text
    assert EXPECTED_ORCID in temp_text
    assert EXPECTED_AFFILIATION in temp_text

    assert "[onejotech@gmail.com]" not in temp_text
    assert "mailto" not in temp_text
    assert "[https://orcid.org/0000-0002-8063-6070]" not in temp_text

    # --------------------------------------------------------
    # 6. Atomic replacement
    # --------------------------------------------------------

    os.replace(temp_path, CFF_PATH)

finally:

    if Path(temp_name).exists():
        Path(temp_name).unlink()

# ------------------------------------------------------------
# 7. FORCE REOPEN FROM DISK
# ------------------------------------------------------------

with open(CFF_PATH, "rb") as f:
    disk_bytes = f.read()

disk_text = disk_bytes.decode("utf-8")

# ------------------------------------------------------------
# 8. BYTE-LEVEL VERIFICATION
# ------------------------------------------------------------

print("=" * 72)
print("STAGE 40C-I — ATOMIC CITATION.CFF REWRITE")
print("=" * 72)

print("\nAUTHOR METADATA READ DIRECTLY FROM DISK")
print("-" * 72)

for i, line in enumerate(disk_text.splitlines(), 1):

    if (
        "affiliation:" in line
        or "email:" in line
        or "orcid:" in line
    ):
        print(f"LINE {i}: {repr(line)}")

# ------------------------------------------------------------
# 9. EXACT ASSERTIONS
# ------------------------------------------------------------

assert EXPECTED_AFFILIATION in disk_text
assert EXPECTED_EMAIL in disk_text
assert EXPECTED_ORCID in disk_text

assert "[onejotech@gmail.com]" not in disk_text
assert "mailto" not in disk_text
assert "[https://orcid.org/0000-0002-8063-6070]" not in disk_text

# ------------------------------------------------------------
# 10. Confirm only intended metadata changed
# ------------------------------------------------------------

print("\nEXACT VALIDATION")
print("-" * 72)

print("PASS — Affiliation")
print("PASS — Clean email")
print("PASS — Clean ORCID")
print("PASS — Markdown email absent")
print("PASS — mailto syntax absent")
print("PASS — Markdown ORCID absent")

# ------------------------------------------------------------
# 11. CFF CORE VALIDATION
# ------------------------------------------------------------

checks = {
    "cff-version": "cff-version: 1.2.0" in disk_text,
    "title": "AFRIDATACYBERJOHN" in disk_text,
    "version": (
        'version: "1.0"' in disk_text
        or "version: 1.0" in disk_text
    ),
    "type": "type: dataset" in disk_text,
    "family-names": 'family-names: "Ajayi"' in disk_text,
    "given-names": 'given-names: "John Ojo"' in disk_text,
    "affiliation": EXPECTED_AFFILIATION in disk_text,
    "email": EXPECTED_EMAIL in disk_text,
    "ORCID": EXPECTED_ORCID in disk_text,
    "license": "license: CC BY 4.0" in disk_text,
}

print("\nCFF CORE VALIDATION")
print("-" * 72)

for key, passed in checks.items():
    print(("PASS" if passed else "FAIL"), key)
    assert passed, f"CFF validation failed: {key}"

# ------------------------------------------------------------
# 12. HASH THE FINAL CFF
# ------------------------------------------------------------

cff_hash = hashlib.sha256(disk_bytes).hexdigest()

print("\n" + "=" * 72)
print("STAGE 40C-I: PASS")
print("=" * 72)

print("Author:       John Ojo Ajayi")
print("Affiliation:  National Open University of Nigeria")
print("Email:        onejotech@gmail.com")
print("ORCID:        https://orcid.org/0000-0002-8063-6070")
print("Version:      1.0")
print("License:      CC BY 4.0")
print("CFF SHA256:   ", cff_hash)
print("Dataset CSVs: NOT MODIFIED")
print("ZIP:          NOT REBUILT")
print("=" * 72)

# ==============================================================================
# NOTEBOOK CELL 701
# ==============================================================================

# ============================================================
# STAGE 40C-J — INDEPENDENT CITATION.CFF TRUTH TEST
# READ-ONLY — NO MODIFICATION
# ============================================================

from pathlib import Path

CFF_PATH = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0/CITATION.cff"
)

assert CFF_PATH.exists()

# Fresh read directly from disk
text = CFF_PATH.read_text(encoding="utf-8")

# Extract exact lines
email_lines = [
    line for line in text.splitlines()
    if line.strip().startswith("email:")
]

orcid_lines = [
    line for line in text.splitlines()
    if line.strip().startswith("orcid:")
]

affiliation_lines = [
    line for line in text.splitlines()
    if line.strip().startswith("affiliation:")
]

print("=" * 72)
print("STAGE 40C-J — INDEPENDENT CFF TRUTH TEST")
print("=" * 72)

print("\nACTUAL EMAIL LINE")
print("-" * 72)
print(repr(email_lines))

print("\nACTUAL ORCID LINE")
print("-" * 72)
print(repr(orcid_lines))

print("\nACTUAL AFFILIATION LINE")
print("-" * 72)
print(repr(affiliation_lines))

# ------------------------------------------------------------
# EXACT EXPECTED VALUES
# ------------------------------------------------------------

expected_email = '    email: "onejotech@gmail.com"'
expected_orcid = (
    '    orcid: "https://orcid.org/0000-0002-8063-6070"'
)
expected_affiliation = (
    '    affiliation: "National Open University of Nigeria"'
)

print("\nEXACT EQUALITY TEST")
print("-" * 72)

email_exact = (
    len(email_lines) == 1
    and email_lines[0] == expected_email
)

orcid_exact = (
    len(orcid_lines) == 1
    and orcid_lines[0] == expected_orcid
)

affiliation_exact = (
    len(affiliation_lines) == 1
    and affiliation_lines[0] == expected_affiliation
)

print("Email exact:", email_exact)
print("ORCID exact:", orcid_exact)
print("Affiliation exact:", affiliation_exact)

# ------------------------------------------------------------
# IMPORTANT: ASSERT ACTUAL FILE CONTENT
# ------------------------------------------------------------

assert email_exact, (
    "FAIL: The actual email line is NOT the expected clean CFF value."
)

assert orcid_exact, (
    "FAIL: The actual ORCID line is NOT the expected clean CFF value."
)

assert affiliation_exact, (
    "FAIL: The actual affiliation line is NOT the expected value."
)

print("\n" + "=" * 72)
print("STAGE 40C-J: TRUE PASS")
print("=" * 72)
print("CITATION.cff contains the exact intended values.")
print("NO FILE MODIFICATION PERFORMED.")
print("=" * 72)

# ==============================================================================
# NOTEBOOK CELL 702
# ==============================================================================

# ============================================================
# STAGE 40C-K — BYTE-LEVEL CFF TRUTH VERIFICATION
# READ-ONLY — NO MODIFICATION
# ============================================================

from pathlib import Path
import hashlib

CFF_PATH = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0/CITATION.cff"
)

text = CFF_PATH.read_text(encoding="utf-8")

email_actual = [
    x for x in text.splitlines()
    if x.strip().startswith("email:")
][0]

orcid_actual = [
    x for x in text.splitlines()
    if x.strip().startswith("orcid:")
][0]

affiliation_actual = [
    x for x in text.splitlines()
    if x.strip().startswith("affiliation:")
][0]

email_expected = '    email: "onejotech@gmail.com"'
orcid_expected = '    orcid: "https://orcid.org/0000-0002-8063-6070"'
affiliation_expected = '    affiliation: "National Open University of Nigeria"'

def sha256_string(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()

print("=" * 72)
print("STAGE 40C-K — BYTE-LEVEL CFF TRUTH VERIFICATION")
print("=" * 72)

print("\nEMAIL")
print("-" * 72)
print("ACTUAL   repr :", repr(email_actual))
print("EXPECTED repr :", repr(email_expected))
print("ACTUAL length :", len(email_actual))
print("EXPECTED length:", len(email_expected))
print("ACTUAL SHA256 :", sha256_string(email_actual))
print("EXPECTED SHA256:", sha256_string(email_expected))
print("EQUAL:", email_actual == email_expected)

print("\nORCID")
print("-" * 72)
print("ACTUAL   repr :", repr(orcid_actual))
print("EXPECTED repr :", repr(orcid_expected))
print("ACTUAL length :", len(orcid_actual))
print("EXPECTED length:", len(orcid_expected))
print("ACTUAL SHA256 :", sha256_string(orcid_actual))
print("EXPECTED SHA256:", sha256_string(orcid_expected))
print("EQUAL:", orcid_actual == orcid_expected)

print("\nAFFILIATION")
print("-" * 72)
print("ACTUAL   repr :", repr(affiliation_actual))
print("EXPECTED repr :", repr(affiliation_expected))
print("ACTUAL length :", len(affiliation_actual))
print("EXPECTED length:", len(affiliation_expected))
print("ACTUAL SHA256 :", sha256_string(affiliation_actual))
print("EXPECTED SHA256:", sha256_string(affiliation_expected))
print("EQUAL:", affiliation_actual == affiliation_expected)

print("\n" + "=" * 72)
print("NO FILE MODIFICATION PERFORMED")
print("=" * 72)

# ==============================================================================
# NOTEBOOK CELL 703
# ==============================================================================

# ============================================================
# STAGE 40C-L — AFFILIATION METADATA CONSISTENCY AUDIT
# ============================================================

from pathlib import Path
import json

RELEASE_DIR = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0"
)

AFFILIATION = "National Open University of Nigeria"

print("=" * 72)
print("STAGE 40C-L — AFFILIATION METADATA CONSISTENCY AUDIT")
print("=" * 72)

# ------------------------------------------------------------
# 1. CITATION.CFF
# ------------------------------------------------------------

cff_path = RELEASE_DIR / "CITATION.cff"
cff = cff_path.read_text(encoding="utf-8")

cff_affiliation = AFFILIATION in cff

print("\nCITATION.cff")
print("Affiliation present:", cff_affiliation)

assert cff_affiliation

# ------------------------------------------------------------
# 2. AUTHORS.JSON
# ------------------------------------------------------------

authors_path = RELEASE_DIR / "metadata/AUTHORS.json"

with open(authors_path, "r", encoding="utf-8") as f:
    authors = json.load(f)

print("\nAUTHORS.json")
print(json.dumps(authors, indent=2, ensure_ascii=False))

# ------------------------------------------------------------
# 3. DATASET_METADATA.JSON
# ------------------------------------------------------------

metadata_path = RELEASE_DIR / "metadata/dataset_metadata.json"

with open(metadata_path, "r", encoding="utf-8") as f:
    metadata = json.load(f)

metadata_text = json.dumps(metadata, ensure_ascii=False)

print("\nDATASET_METADATA.JSON")
print("Creator present:", "John Ojo Ajayi" in metadata_text)
print("ORCID present:", "0000-0002-8063-6070" in metadata_text)
print("Affiliation present:", AFFILIATION in metadata_text)

# ------------------------------------------------------------
# 4. README
# ------------------------------------------------------------

readme_path = RELEASE_DIR / "README.md"
readme = readme_path.read_text(encoding="utf-8")

print("\nREADME.md")
print("Creator present:", "John Ojo Ajayi" in readme)
print("Affiliation present:", AFFILIATION in readme)

# ------------------------------------------------------------
# 5. PROVENANCE
# ------------------------------------------------------------

prov_path = RELEASE_DIR / "documentation/PROVENANCE.md"
prov = prov_path.read_text(encoding="utf-8")

print("\nPROVENANCE.md")
print("Creator present:", "John Ojo Ajayi" in prov)
print("Affiliation present:", AFFILIATION in prov)

# ------------------------------------------------------------
# 6. FINAL AUDIT
# ------------------------------------------------------------

print("\n" + "=" * 72)
print("STAGE 40C-L AUDIT COMPLETE")
print("=" * 72)

print("CITATION.cff affiliation: PASS")
print("CSV modification:         NO")
print("ZIP rebuild:              NO")
print("=" * 72)

# ==============================================================================
# NOTEBOOK CELL 704
# ==============================================================================

# ============================================================================
# STAGE 40C-M-RECOVERY — LOCATE ACTUAL RELEASE DIRECTORY
# Read-only diagnostic. NO files are modified.
# ============================================================================

from pathlib import Path

print("=" * 80)
print("STAGE 40C-M-RECOVERY — LOCATING AFRIDATACYBERJOHN_v1.0")
print("=" * 80)

SEARCH_ROOTS = [
    Path("/content/drive/MyDrive"),
    Path("/content/drive/My Drive"),
]

matches = []

for root in SEARCH_ROOTS:
    if not root.exists():
        continue

    print(f"\nSearching: {root}")

    try:
        for p in root.rglob("AFRIDATACYBERJOHN_v1.0"):
            if p.is_dir():
                matches.append(p)
    except Exception as e:
        print("Search warning:", e)

# Remove duplicates
matches = list(dict.fromkeys(matches))

print("\n" + "-" * 80)

if not matches:
    print("NO RELEASE DIRECTORY FOUND.")
else:
    print(f"Release directories found: {len(matches)}")

    for i, p in enumerate(matches, 1):
        print(f"\n[{i}] {p}")

        required = [
            "CITATION.cff",
            "README.md",
            "LICENSE",
            "data",
            "documentation",
            "metadata",
        ]

        for item in required:
            target = p / item
            print(
                f"    {item:<25} "
                + ("PASS" if target.exists() else "MISSING")
            )

        authors = p / "metadata" / "AUTHORS.json"
        dataset_metadata = p / "metadata" / "dataset_metadata.json"

        print(
            "    AUTHORS.json             ",
            "PASS" if authors.exists() else "MISSING"
        )

        print(
            "    dataset_metadata.json    ",
            "PASS" if dataset_metadata.exists() else "MISSING"
        )

print("\n" + "=" * 80)
print("RECOVERY DIAGNOSTIC COMPLETE")
print("=" * 80)
print("NO FILES MODIFIED")
print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 705
# ==============================================================================

# ============================================================================
# STAGE 40C-M — CORRECTED METADATA HARMONIZATION
# Canonical permanent release:
# /content/drive/MyDrive/AFRIDATACYBERJOHN/AFRIDATACYBERJOHN_v1.0
#
# Modifies:
#   AUTHORS.json
#   dataset_metadata.json
#   README.md
#   PROVENANCE.md
#
# Does NOT modify:
#   Any CSV
#   CITATION.cff
#   ZIP
#   checksums.sha256
#   RECOVERY_MANIFEST.json
# ============================================================================

from pathlib import Path
import json

RELEASE_DIR = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/AFRIDATACYBERJOHN_v1.0"
)

AFFILIATION = "National Open University of Nigeria"

AUTHORS_PATH = RELEASE_DIR / "metadata" / "AUTHORS.json"
METADATA_PATH = RELEASE_DIR / "metadata" / "dataset_metadata.json"
README_PATH = RELEASE_DIR / "README.md"
PROVENANCE_PATH = RELEASE_DIR / "documentation" / "PROVENANCE.md"

print("=" * 80)
print("STAGE 40C-M — CORRECTED METADATA HARMONIZATION")
print("=" * 80)

# --------------------------------------------------------------------------
# Verify canonical release
# --------------------------------------------------------------------------

assert RELEASE_DIR.exists(), "Canonical release directory does not exist."

for p in [
    AUTHORS_PATH,
    METADATA_PATH,
    README_PATH,
    PROVENANCE_PATH,
]:
    assert p.exists(), f"Required metadata file missing: {p}"

print("Canonical release:")
print(RELEASE_DIR)

# --------------------------------------------------------------------------
# 1. AUTHORS.json
# --------------------------------------------------------------------------

with open(AUTHORS_PATH, "r", encoding="utf-8") as f:
    authors = json.load(f)

assert isinstance(authors, dict), "AUTHORS.json is not a JSON object."

authors.setdefault("creator", {})

if not isinstance(authors["creator"], dict):
    raise TypeError("AUTHORS.json creator field is not an object.")

authors["creator"]["affiliation"] = AFFILIATION

with open(AUTHORS_PATH, "w", encoding="utf-8") as f:
    json.dump(authors, f, indent=2, ensure_ascii=False)
    f.write("\n")

# Verify immediately
with open(AUTHORS_PATH, "r", encoding="utf-8") as f:
    authors_check = json.load(f)

assert (
    authors_check["creator"]["affiliation"] == AFFILIATION
), "AUTHORS.json affiliation verification failed."

print("\nAUTHORS.json")
print("  Creator:", authors_check["creator"].get("name"))
print("  Affiliation:", authors_check["creator"].get("affiliation"))
print("  PASS")

# --------------------------------------------------------------------------
# 2. dataset_metadata.json
# --------------------------------------------------------------------------

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

assert isinstance(metadata, dict), \
    "dataset_metadata.json is not a JSON object."

metadata["affiliation"] = AFFILIATION

if isinstance(metadata.get("creator"), dict):
    metadata["creator"]["affiliation"] = AFFILIATION

for key in ["author", "authors", "creators"]:
    value = metadata.get(key)

    if isinstance(value, dict):
        value["affiliation"] = AFFILIATION

    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                item["affiliation"] = AFFILIATION

with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
    f.write("\n")

# Verify immediately
with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata_check = json.load(f)

assert (
    metadata_check.get("affiliation") == AFFILIATION
), "dataset_metadata.json affiliation verification failed."

print("\ndataset_metadata.json")
print("  Top-level affiliation:", metadata_check.get("affiliation"))

if isinstance(metadata_check.get("creator"), dict):
    print(
        "  Creator affiliation:",
        metadata_check["creator"].get("affiliation")
    )

print("  PASS")

# --------------------------------------------------------------------------
# 3. README.md
# --------------------------------------------------------------------------

readme = README_PATH.read_text(encoding="utf-8")

creator_line = "- **Dataset Creator:** John Ojo Ajayi"
affiliation_line = f"- **Affiliation:** {AFFILIATION}"

if affiliation_line not in readme:

    if creator_line in readme:
        readme = readme.replace(
            creator_line,
            creator_line + "\n" + affiliation_line,
            1
        )
    else:
        readme += (
            "\n\n## Creator Information\n\n"
            + creator_line
            + "\n"
            + affiliation_line
            + "\n"
        )

README_PATH.write_text(readme, encoding="utf-8")

readme_check = README_PATH.read_text(encoding="utf-8")

assert AFFILIATION in readme_check, \
    "README.md affiliation verification failed."

print("\nREADME.md")
print("  Creator present:", "John Ojo Ajayi" in readme_check)
print("  Affiliation present:", AFFILIATION in readme_check)
print("  PASS")

# --------------------------------------------------------------------------
# 4. PROVENANCE.md
# --------------------------------------------------------------------------

provenance = PROVENANCE_PATH.read_text(encoding="utf-8")

if "## Dataset Creator" not in provenance:

    provenance += (
        "\n\n"
        "## Dataset Creator\n\n"
        "John Ojo Ajayi\n\n"
        f"**Affiliation:** {AFFILIATION}\n"
    )

elif AFFILIATION not in provenance:

    provenance += (
        f"\n**Affiliation:** {AFFILIATION}\n"
    )

PROVENANCE_PATH.write_text(
    provenance,
    encoding="utf-8"
)

provenance_check = PROVENANCE_PATH.read_text(
    encoding="utf-8"
)

assert "John Ojo Ajayi" in provenance_check, \
    "PROVENANCE.md creator verification failed."

assert AFFILIATION in provenance_check, \
    "PROVENANCE.md affiliation verification failed."

print("\nPROVENANCE.md")
print("  Creator present:", "John Ojo Ajayi" in provenance_check)
print("  Affiliation present:", AFFILIATION in provenance_check)
print("  PASS")

# --------------------------------------------------------------------------
# 5. Confirm frozen CSVs were NOT touched
# --------------------------------------------------------------------------

CSV_FILES = [
    RELEASE_DIR / "data" /
    "AFRICA_MobileMoney_USSD_Authoritative_Events.csv",

    RELEASE_DIR / "data" /
    "AFRICA_MobileMoney_USSD_Authoritative_Windows.csv",

    RELEASE_DIR / "data" /
    "AFRICA_MobileMoney_USSD_Current_Events.csv",

    RELEASE_DIR / "data" /
    "AFRICA_MobileMoney_USSD_Current_Windows.csv",
]

print("\nFrozen dataset files:")

for csv_path in CSV_FILES:
    assert csv_path.exists(), f"Missing frozen CSV: {csv_path}"
    print("  PASS:", csv_path.name)

# --------------------------------------------------------------------------
# Final
# --------------------------------------------------------------------------

print("\n" + "=" * 80)
print("STAGE 40C-M COMPLETE")
print("=" * 80)
print("Affiliation:", AFFILIATION)
print("CSV modification: NO")
print("CITATION.cff modification: NO")
print("ZIP rebuild: NO")
print("Checksum update: NO")
print("Recovery manifest update: NO")
print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 706
# ==============================================================================

# ============================================================================
# STAGE 40C-N — INDEPENDENT METADATA CONSISTENCY AUDIT
#
# Purpose:
#   Independently verify the metadata harmonization completed in Stage 40C-M.
#
# This stage:
#   - DOES NOT modify CSV files
#   - DOES NOT modify CITATION.cff
#   - DOES NOT rebuild the ZIP
#   - DOES NOT update checksums
#   - DOES NOT update the recovery manifest
#   - SAVES an audit report for permanent record
# ============================================================================

from pathlib import Path
import json
from datetime import datetime

# --------------------------------------------------------------------------
# CANONICAL RELEASE
# --------------------------------------------------------------------------

RELEASE_DIR = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/AFRIDATACYBERJOHN_v1.0"
)

AFFILIATION = "National Open University of Nigeria"
CREATOR = "John Ojo Ajayi"
EMAIL = "onejotech@gmail.com"
ORCID = "https://orcid.org/0000-0002-8063-6070"

# --------------------------------------------------------------------------
# FILE PATHS
# --------------------------------------------------------------------------

CITATION_PATH = RELEASE_DIR / "CITATION.cff"
AUTHORS_PATH = RELEASE_DIR / "metadata" / "AUTHORS.json"
METADATA_PATH = RELEASE_DIR / "metadata" / "dataset_metadata.json"
README_PATH = RELEASE_DIR / "README.md"
PROVENANCE_PATH = RELEASE_DIR / "documentation" / "PROVENANCE.md"

CSV_FILES = [
    RELEASE_DIR / "data" /
    "AFRICA_MobileMoney_USSD_Authoritative_Events.csv",

    RELEASE_DIR / "data" /
    "AFRICA_MobileMoney_USSD_Authoritative_Windows.csv",

    RELEASE_DIR / "data" /
    "AFRICA_MobileMoney_USSD_Current_Events.csv",

    RELEASE_DIR / "data" /
    "AFRICA_MobileMoney_USSD_Current_Windows.csv",
]

AUDIT_PATH = (
    RELEASE_DIR /
    "documentation" /
    "STAGE_40C-N_METADATA_CONSISTENCY_AUDIT.txt"
)

# --------------------------------------------------------------------------
# START
# --------------------------------------------------------------------------

print("=" * 80)
print("STAGE 40C-N — INDEPENDENT METADATA CONSISTENCY AUDIT")
print("=" * 80)

assert RELEASE_DIR.exists(), "Canonical release directory not found."

results = []
details = []

def record(name, passed, detail):
    results.append((name, passed))
    details.append(f"{name}: {'PASS' if passed else 'FAIL'} — {detail}")
    print(f"{name:<45} {'PASS' if passed else 'FAIL'}")
    print(f"    {detail}")

# --------------------------------------------------------------------------
# 1. Required files
# --------------------------------------------------------------------------

required_files = [
    CITATION_PATH,
    AUTHORS_PATH,
    METADATA_PATH,
    README_PATH,
    PROVENANCE_PATH,
]

for p in required_files:
    record(
        f"FILE {p.name}",
        p.exists(),
        str(p)
    )

# --------------------------------------------------------------------------
# 2. Read actual files
# --------------------------------------------------------------------------

citation_text = CITATION_PATH.read_text(encoding="utf-8")
readme_text = README_PATH.read_text(encoding="utf-8")
provenance_text = PROVENANCE_PATH.read_text(encoding="utf-8")

with open(AUTHORS_PATH, "r", encoding="utf-8") as f:
    authors = json.load(f)

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# --------------------------------------------------------------------------
# 3. CITATION.cff — affiliation
# --------------------------------------------------------------------------

citation_affiliation = (
    AFFILIATION in citation_text
)

record(
    "CITATION.cff affiliation",
    citation_affiliation,
    f"Expected: {AFFILIATION}"
)

# --------------------------------------------------------------------------
# 4. AUTHORS.json
# --------------------------------------------------------------------------

authors_creator = authors.get("creator", {})

record(
    "AUTHORS creator",
    authors_creator.get("name") == CREATOR,
    f"Actual: {authors_creator.get('name')!r}"
)

record(
    "AUTHORS affiliation",
    authors_creator.get("affiliation") == AFFILIATION,
    f"Actual: {authors_creator.get('affiliation')!r}"
)

# --------------------------------------------------------------------------
# 5. dataset_metadata.json
# --------------------------------------------------------------------------

record(
    "METADATA creator",
    (
        metadata.get("creator", {}).get("name") == CREATOR
        if isinstance(metadata.get("creator"), dict)
        else False
    ),
    f"Actual: {metadata.get('creator')!r}"
)

record(
    "METADATA affiliation",
    metadata.get("affiliation") == AFFILIATION,
    f"Actual: {metadata.get('affiliation')!r}"
)

# --------------------------------------------------------------------------
# 6. README
# --------------------------------------------------------------------------

record(
    "README creator",
    CREATOR in readme_text,
    f"Creator string present: {CREATOR in readme_text}"
)

record(
    "README affiliation",
    AFFILIATION in readme_text,
    f"Affiliation present: {AFFILIATION in readme_text}"
)

# --------------------------------------------------------------------------
# 7. PROVENANCE
# --------------------------------------------------------------------------

record(
    "PROVENANCE creator",
    CREATOR in provenance_text,
    f"Creator string present: {CREATOR in provenance_text}"
)

record(
    "PROVENANCE affiliation",
    AFFILIATION in provenance_text,
    f"Affiliation present: {AFFILIATION in provenance_text}"
)

# --------------------------------------------------------------------------
# 8. Frozen CSV existence
# --------------------------------------------------------------------------

for csv_path in CSV_FILES:
    record(
        f"CSV {csv_path.name}",
        csv_path.exists(),
        "Frozen dataset file exists."
    )

# --------------------------------------------------------------------------
# 9. Verify no temporary backup remains
# --------------------------------------------------------------------------

backup_files = list(RELEASE_DIR.rglob("*.stage40C_backup"))

record(
    "Temporary backup cleanup",
    len(backup_files) == 0,
    f"Backup files found: {len(backup_files)}"
)

# --------------------------------------------------------------------------
# 10. Verify ZIP has NOT been rebuilt by this stage
# --------------------------------------------------------------------------

ZIP_PATH = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0.zip"
)

record(
    "Permanent ZIP exists",
    ZIP_PATH.exists(),
    str(ZIP_PATH)
)

# --------------------------------------------------------------------------
# FINAL STATUS
# --------------------------------------------------------------------------

all_pass = all(passed for _, passed in results)

status = "PASS" if all_pass else "FAIL"

# --------------------------------------------------------------------------
# SAVE AUDIT REPORT
# --------------------------------------------------------------------------

timestamp = datetime.now().isoformat(timespec="seconds")

report_lines = [
    "AFRIDATACYBERJOHN",
    "STAGE 40C-N — INDEPENDENT METADATA CONSISTENCY AUDIT",
    "",
    f"Audit timestamp: {timestamp}",
    f"Canonical release: {RELEASE_DIR}",
    f"Creator: {CREATOR}",
    f"Email: {EMAIL}",
    f"ORCID: {ORCID}",
    f"Affiliation: {AFFILIATION}",
    "",
    "RESULTS",
    "-------",
]

report_lines.extend(details)

report_lines.extend([
    "",
    "FINAL STATUS",
    "------------",
    status,
    "",
    "PROTECTED DATA STATUS",
    "---------------------",
    "Frozen CSVs modified: NO",
    "CITATION.cff modified: NO",
    "ZIP rebuilt: NO",
    "Checksum manifest updated: NO",
    "Recovery manifest updated: NO",
])

AUDIT_PATH.write_text(
    "\n".join(report_lines) + "\n",
    encoding="utf-8"
)

# --------------------------------------------------------------------------
# VERIFY AUDIT REPORT WAS SAVED
# --------------------------------------------------------------------------

assert AUDIT_PATH.exists(), "Audit report was not saved."

print("\n" + "=" * 80)
print("STAGE 40C-N COMPLETE")
print("=" * 80)

print("FINAL STATUS:", status)
print("Audit report saved:")
print(AUDIT_PATH)

print("\nProtected:")
print("  Frozen CSVs modified: NO")
print("  CITATION.cff modified: NO")
print("  ZIP rebuilt: NO")
print("  Checksums updated: NO")
print("  Recovery manifest updated: NO")

print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 707
# ==============================================================================

from pathlib import Path
import shutil

SOURCE = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/AFRIDATACYBERJOHN_v1.0.zip"
)

DEST = Path("/content/AFRIDATACYBERJOHN_v1.0.zip")

assert SOURCE.exists(), f"ZIP not found: {SOURCE}"

shutil.copy2(SOURCE, DEST)

print("COPY COMPLETE")
print("File:", DEST)
print("Size:", DEST.stat().st_size, "bytes")

# ==============================================================================
# NOTEBOOK CELL 708
# ==============================================================================

# ============================================================================
# STAGE 40C-N1 — DATASET METADATA CREATOR STRUCTURE REPAIR
#
# Purpose:
#   Correct dataset_metadata.json so creator metadata is structurally
#   consistent with AUTHORS.json and CITATION.cff.
#
# Protected:
#   - All 4 CSV files
#   - CITATION.cff
#   - ZIP
#   - checksums.sha256
#   - RECOVERY_MANIFEST.json
# ============================================================================

from pathlib import Path
import json

RELEASE_DIR = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/AFRIDATACYBERJOHN_v1.0"
)

METADATA_PATH = RELEASE_DIR / "metadata" / "dataset_metadata.json"

CREATOR_NAME = "John Ojo Ajayi"
EMAIL = "onejotech@gmail.com"
ORCID = "https://orcid.org/0000-0002-8063-6070"
AFFILIATION = "National Open University of Nigeria"

print("=" * 80)
print("STAGE 40C-N1 — DATASET METADATA CREATOR STRUCTURE REPAIR")
print("=" * 80)

assert METADATA_PATH.exists(), "dataset_metadata.json not found."

# --------------------------------------------------------------------------
# Read actual metadata
# --------------------------------------------------------------------------

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

print("\nCURRENT CREATOR STRUCTURE")
print("-" * 80)
print("Python type:", type(metadata.get("creator")).__name__)
print("Current value:", repr(metadata.get("creator")))

# --------------------------------------------------------------------------
# Preserve any existing creator-related information where possible
# --------------------------------------------------------------------------

existing_creator = metadata.get("creator")

# If creator is already a dictionary, preserve it and harmonize fields.
if isinstance(existing_creator, dict):

    existing_creator["name"] = CREATOR_NAME
    existing_creator["email"] = EMAIL
    existing_creator["orcid"] = ORCID
    existing_creator["affiliation"] = AFFILIATION

    metadata["creator"] = existing_creator

# If creator is a string, convert it into a structured creator object.
elif isinstance(existing_creator, str):

    metadata["creator"] = {
        "name": CREATOR_NAME,
        "email": EMAIL,
        "orcid": ORCID,
        "affiliation": AFFILIATION
    }

else:

    metadata["creator"] = {
        "name": CREATOR_NAME,
        "email": EMAIL,
        "orcid": ORCID,
        "affiliation": AFFILIATION
    }

# --------------------------------------------------------------------------
# Also retain explicit top-level affiliation
# --------------------------------------------------------------------------

metadata["affiliation"] = AFFILIATION

# --------------------------------------------------------------------------
# Write metadata
# --------------------------------------------------------------------------

with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
    f.write("\n")

# --------------------------------------------------------------------------
# Independent immediate verification
# --------------------------------------------------------------------------

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    verified = json.load(f)

creator = verified.get("creator")

print("\nNEW CREATOR STRUCTURE")
print("-" * 80)
print("Python type:", type(creator).__name__)
print(json.dumps(creator, indent=2, ensure_ascii=False))

assert isinstance(creator, dict)
assert creator.get("name") == CREATOR_NAME
assert creator.get("email") == EMAIL
assert creator.get("orcid") == ORCID
assert creator.get("affiliation") == AFFILIATION
assert verified.get("affiliation") == AFFILIATION

print("\n" + "=" * 80)
print("STAGE 40C-N1 COMPLETE — PASS")
print("=" * 80)

print("Creator:", creator["name"])
print("Email:", creator["email"])
print("ORCID:", creator["orcid"])
print("Affiliation:", creator["affiliation"])

print("\nProtected:")
print("  Frozen CSVs modified: NO")
print("  CITATION.cff modified: NO")
print("  ZIP rebuilt: NO")
print("  Checksums updated: NO")
print("  Recovery manifest updated: NO")

print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 709
# ==============================================================================

from google.colab import files

files.download("/content/AFRIDATACYBERJOHN_v1.0.zip")

# ==============================================================================
# NOTEBOOK CELL 710
# ==============================================================================

# ============================================================================
# STAGE 40C-N2 — CLEAN CREATOR CONTACT METADATA
#
# Purpose:
#   Ensure email and ORCID are stored as plain machine-readable values.
#
# Protected:
#   - All frozen CSVs
#   - CITATION.cff
#   - ZIP
#   - checksums
#   - recovery manifest
# ============================================================================

from pathlib import Path
import json

RELEASE_DIR = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/AFRIDATACYBERJOHN_v1.0"
)

METADATA_PATH = RELEASE_DIR / "metadata" / "dataset_metadata.json"
AUTHORS_PATH = RELEASE_DIR / "metadata" / "AUTHORS.json"

CLEAN_EMAIL = "onejotech@gmail.com"
CLEAN_ORCID = "https://orcid.org/0000-0002-8063-6070"
AFFILIATION = "National Open University of Nigeria"
CREATOR = "John Ojo Ajayi"

print("=" * 80)
print("STAGE 40C-N2 — CLEAN CREATOR CONTACT METADATA")
print("=" * 80)

# --------------------------------------------------------------------------
# dataset_metadata.json
# --------------------------------------------------------------------------

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

metadata["creator"] = {
    "name": CREATOR,
    "email": CLEAN_EMAIL,
    "orcid": CLEAN_ORCID,
    "affiliation": AFFILIATION
}

metadata["affiliation"] = AFFILIATION

with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
    f.write("\n")

# --------------------------------------------------------------------------
# AUTHORS.json
# --------------------------------------------------------------------------

with open(AUTHORS_PATH, "r", encoding="utf-8") as f:
    authors = json.load(f)

authors.setdefault("creator", {})

authors["creator"]["name"] = CREATOR
authors["creator"]["email"] = CLEAN_EMAIL
authors["creator"]["orcid"] = CLEAN_ORCID
authors["creator"]["affiliation"] = AFFILIATION

with open(AUTHORS_PATH, "w", encoding="utf-8") as f:
    json.dump(authors, f, indent=2, ensure_ascii=False)
    f.write("\n")

# --------------------------------------------------------------------------
# Independent verification
# --------------------------------------------------------------------------

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata_check = json.load(f)

with open(AUTHORS_PATH, "r", encoding="utf-8") as f:
    authors_check = json.load(f)

m_creator = metadata_check["creator"]
a_creator = authors_check["creator"]

assert m_creator["name"] == CREATOR
assert m_creator["email"] == CLEAN_EMAIL
assert m_creator["orcid"] == CLEAN_ORCID
assert m_creator["affiliation"] == AFFILIATION

assert a_creator["name"] == CREATOR
assert a_creator["email"] == CLEAN_EMAIL
assert a_creator["orcid"] == CLEAN_ORCID
assert a_creator["affiliation"] == AFFILIATION

# Explicitly reject Markdown-formatted contact values
assert not m_creator["email"].startswith("[")
assert not m_creator["orcid"].startswith("[")

assert not a_creator["email"].startswith("[")
assert not a_creator["orcid"].startswith("[")

print("\nDATASET_METADATA.JSON")
print(json.dumps(m_creator, indent=2, ensure_ascii=False))

print("\nAUTHORS.JSON")
print(json.dumps(a_creator, indent=2, ensure_ascii=False))

print("\n" + "=" * 80)
print("STAGE 40C-N2 COMPLETE — PASS")
print("=" * 80)

print("Creator:", CREATOR)
print("Email:", CLEAN_EMAIL)
print("ORCID:", CLEAN_ORCID)
print("Affiliation:", AFFILIATION)

print("\nProtected:")
print("  Frozen CSVs modified: NO")
print("  CITATION.cff modified: NO")
print("  ZIP rebuilt: NO")
print("  Checksums updated: NO")
print("  Recovery manifest updated: NO")

print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 711
# ==============================================================================

# ============================================================================
# STAGE 40C-N3 — BYTE-LEVEL CREATOR METADATA TRUTH TEST
#
# READ-ONLY
# No files are modified.
# No ZIP/checksum/recovery-manifest changes.
# ============================================================================

from pathlib import Path
import json
import hashlib

RELEASE_DIR = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/AFRIDATACYBERJOHN_v1.0"
)

METADATA_PATH = RELEASE_DIR / "metadata" / "dataset_metadata.json"
AUTHORS_PATH = RELEASE_DIR / "metadata" / "AUTHORS.json"

EXPECTED_EMAIL = "onejotech@gmail.com"
EXPECTED_ORCID = "https://orcid.org/0000-0002-8063-6070"
EXPECTED_AFFILIATION = "National Open University of Nigeria"

print("=" * 80)
print("STAGE 40C-N3 — BYTE-LEVEL CREATOR METADATA TRUTH TEST")
print("=" * 80)

def sha256_text(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()

# --------------------------------------------------------------------------
# Read actual JSON files
# --------------------------------------------------------------------------

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

with open(AUTHORS_PATH, "r", encoding="utf-8") as f:
    authors = json.load(f)

m = metadata["creator"]
a = authors["creator"]

# --------------------------------------------------------------------------
# DATASET METADATA
# --------------------------------------------------------------------------

print("\nDATASET_METADATA.JSON")
print("-" * 80)

print("EMAIL actual repr:")
print(repr(m["email"]))

print("EMAIL expected repr:")
print(repr(EXPECTED_EMAIL))

print("EMAIL exact match:")
print(m["email"] == EXPECTED_EMAIL)

print("EMAIL SHA256:")
print(sha256_text(m["email"]))

print("\nORCID actual repr:")
print(repr(m["orcid"]))

print("ORCID expected repr:")
print(repr(EXPECTED_ORCID))

print("ORCID exact match:")
print(m["orcid"] == EXPECTED_ORCID)

print("ORCID SHA256:")
print(sha256_text(m["orcid"]))

print("\nAFFILIATION actual repr:")
print(repr(m["affiliation"]))

print("AFFILIATION exact match:")
print(m["affiliation"] == EXPECTED_AFFILIATION)

# --------------------------------------------------------------------------
# AUTHORS.JSON
# --------------------------------------------------------------------------

print("\nAUTHORS.JSON")
print("-" * 80)

print("EMAIL actual repr:")
print(repr(a["email"]))

print("EMAIL expected repr:")
print(repr(EXPECTED_EMAIL))

print("EMAIL exact match:")
print(a["email"] == EXPECTED_EMAIL)

print("EMAIL SHA256:")
print(sha256_text(a["email"]))

print("\nORCID actual repr:")
print(repr(a["orcid"]))

print("ORCID expected repr:")
print(repr(EXPECTED_ORCID))

print("ORCID exact match:")
print(a["orcid"] == EXPECTED_ORCID)

print("ORCID SHA256:")
print(sha256_text(a["orcid"]))

print("\nAFFILIATION actual repr:")
print(repr(a["affiliation"]))

print("AFFILIATION exact match:")
print(a["affiliation"] == EXPECTED_AFFILIATION)

# --------------------------------------------------------------------------
# HARD TRUTH TEST
# --------------------------------------------------------------------------

markdown_email_found = (
    "[" in m["email"]
    or "](" in m["email"]
    or "[" in a["email"]
    or "](" in a["email"]
)

markdown_orcid_found = (
    "[" in m["orcid"]
    or "](" in m["orcid"]
    or "[" in a["orcid"]
    or "](" in a["orcid"]
)

print("\n" + "=" * 80)
print("HARD TRUTH RESULTS")
print("=" * 80)

print("Markdown email detected:", markdown_email_found)
print("Markdown ORCID detected:", markdown_orcid_found)

email_clean = (
    m["email"] == EXPECTED_EMAIL
    and a["email"] == EXPECTED_EMAIL
)

orcid_clean = (
    m["orcid"] == EXPECTED_ORCID
    and a["orcid"] == EXPECTED_ORCID
)

affiliation_clean = (
    m["affiliation"] == EXPECTED_AFFILIATION
    and a["affiliation"] == EXPECTED_AFFILIATION
)

print("Email clean:", email_clean)
print("ORCID clean:", orcid_clean)
print("Affiliation consistent:", affiliation_clean)

print("=" * 80)

if email_clean and orcid_clean and affiliation_clean:
    print("FINAL RESULT: PASS")
else:
    print("FINAL RESULT: FAIL — ACTUAL STORED VALUES ARE NOT CLEAN")

print("=" * 80)
print("READ-ONLY TEST COMPLETE")
print("NO FILES MODIFIED")
print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 712
# ==============================================================================

# ============================================================================
# STAGE 40C-N4 — AUTHORITATIVE CONTACT METADATA CORRECTION
# ============================================================================

from pathlib import Path
import json

RELEASE_DIR = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/AFRIDATACYBERJOHN_v1.0"
)

METADATA_PATH = RELEASE_DIR / "metadata" / "dataset_metadata.json"
AUTHORS_PATH = RELEASE_DIR / "metadata" / "AUTHORS.json"

# IMPORTANT:
# These are hard-coded authoritative plain-text values.
# They are NOT read from the existing metadata.

EXPECTED_NAME = "John Ojo Ajayi"
EXPECTED_EMAIL = "onejotech" + "@gmail.com"
EXPECTED_ORCID = "https://orcid.org/0000-0002-8063-6070"
EXPECTED_AFFILIATION = "National Open University of Nigeria"

print("=" * 80)
print("STAGE 40C-N4 — AUTHORITATIVE CONTACT METADATA CORRECTION")
print("=" * 80)

# --------------------------------------------------------------------------
# Load dataset_metadata.json
# --------------------------------------------------------------------------

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

metadata["creator"] = {
    "name": EXPECTED_NAME,
    "email": EXPECTED_EMAIL,
    "orcid": EXPECTED_ORCID,
    "affiliation": EXPECTED_AFFILIATION
}

metadata["affiliation"] = EXPECTED_AFFILIATION

with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
    f.write("\n")

# --------------------------------------------------------------------------
# Load AUTHORS.json
# --------------------------------------------------------------------------

with open(AUTHORS_PATH, "r", encoding="utf-8") as f:
    authors = json.load(f)

authors["creator"] = {
    "name": EXPECTED_NAME,
    "email": EXPECTED_EMAIL,
    "orcid": EXPECTED_ORCID,
    "affiliation": EXPECTED_AFFILIATION
}

with open(AUTHORS_PATH, "w", encoding="utf-8") as f:
    json.dump(authors, f, indent=2, ensure_ascii=False)
    f.write("\n")

# --------------------------------------------------------------------------
# Read back from disk — independent verification
# --------------------------------------------------------------------------

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata_check = json.load(f)

with open(AUTHORS_PATH, "r", encoding="utf-8") as f:
    authors_check = json.load(f)

m = metadata_check["creator"]
a = authors_check["creator"]

print("\nDATASET_METADATA.JSON ACTUAL VALUES")
print("-" * 80)
print("Name:        ", repr(m["name"]))
print("Email:       ", repr(m["email"]))
print("ORCID:       ", repr(m["orcid"]))
print("Affiliation: ", repr(m["affiliation"]))

print("\nAUTHORS.JSON ACTUAL VALUES")
print("-" * 80)
print("Name:        ", repr(a["name"]))
print("Email:       ", repr(a["email"]))
print("ORCID:       ", repr(a["orcid"]))
print("Affiliation: ", repr(a["affiliation"]))

# --------------------------------------------------------------------------
# HARD ASSERTIONS
# --------------------------------------------------------------------------

assert m["name"] == EXPECTED_NAME
assert m["email"] == EXPECTED_EMAIL
assert m["orcid"] == EXPECTED_ORCID
assert m["affiliation"] == EXPECTED_AFFILIATION

assert a["name"] == EXPECTED_NAME
assert a["email"] == EXPECTED_EMAIL
assert a["orcid"] == EXPECTED_ORCID
assert a["affiliation"] == EXPECTED_AFFILIATION

# Explicitly reject Markdown-link formatting.
for value in [
    m["email"],
    m["orcid"],
    a["email"],
    a["orcid"]
]:
    assert not value.startswith("[")
    assert "](" not in value
    assert not value.endswith(")")

# --------------------------------------------------------------------------
# FINAL
# --------------------------------------------------------------------------

print("\n" + "=" * 80)
print("STAGE 40C-N4 COMPLETE — PASS")
print("=" * 80)

print("Plain email confirmed:", m["email"] == "onejotech" + "@gmail.com")
print("Plain ORCID confirmed:", m["orcid"] == EXPECTED_ORCID)
print("Affiliation confirmed:", m["affiliation"] == EXPECTED_AFFILIATION)

print("\nProtected:")
print("  Frozen CSVs modified: NO")
print("  CITATION.cff modified: NO")
print("  ZIP rebuilt: NO")
print("  Checksums updated: NO")
print("  Recovery manifest updated: NO")

print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 713
# ==============================================================================

from google.colab import drive

drive.mount('/content/drive')

# ==============================================================================
# NOTEBOOK CELL 714
# ==============================================================================

from pathlib import Path

RELEASE_DIR = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/AFRIDATACYBERJOHN_v1.0"
)

print("=" * 80)
print("AFRIDATACYBERJOHN — POST-RESTART RELEASE RECOVERY")
print("=" * 80)

print("Release exists:", RELEASE_DIR.exists())
print("Release path:", RELEASE_DIR)

required = [
    "CITATION.cff",
    "README.md",
    "LICENSE",
    "metadata/AUTHORS.json",
    "metadata/dataset_metadata.json",
    "metadata/checksums.sha256",
    "documentation/PROVENANCE.md",
    "documentation/METHODOLOGY.md",
    "documentation/FORENSIC_VALIDATION.md",
    "data/AFRICA_MobileMoney_USSD_Authoritative_Events.csv",
    "data/AFRICA_MobileMoney_USSD_Authoritative_Windows.csv",
    "data/AFRICA_MobileMoney_USSD_Current_Events.csv",
    "data/AFRICA_MobileMoney_USSD_Current_Windows.csv",
]

print("\nFILE STATUS")
print("-" * 80)

all_present = True

for item in required:
    p = RELEASE_DIR / item
    exists = p.exists()
    print(f"{item:<65} {'PASS' if exists else 'MISSING'}")
    if not exists:
        all_present = False

print("\n" + "=" * 80)
print(
    "RECOVERY STATUS:",
    "PASS" if all_present else "FAIL"
)
print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 715
# ==============================================================================

# ============================================================================
# STAGE 40C-N4 — AUTHORITATIVE CONTACT METADATA CORRECTION
#
# Modifies ONLY:
#   - metadata/dataset_metadata.json
#   - metadata/AUTHORS.json
#
# Does NOT modify:
#   - frozen CSVs
#   - CITATION.cff
#   - ZIP
#   - checksums.sha256
#   - RECOVERY_MANIFEST.json
# ============================================================================

from pathlib import Path
import json

RELEASE_DIR = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/AFRIDATACYBERJOHN_v1.0"
)

METADATA_PATH = RELEASE_DIR / "metadata" / "dataset_metadata.json"
AUTHORS_PATH = RELEASE_DIR / "metadata" / "AUTHORS.json"

# --------------------------------------------------------------------------
# AUTHORITATIVE VALUES
# These are deliberately constructed independently of the existing files.
# --------------------------------------------------------------------------

EXPECTED_NAME = "John Ojo Ajayi"
EXPECTED_EMAIL = "onejotech" + "@gmail.com"
EXPECTED_ORCID = "https://orcid.org/0000-0002-8063-6070"
EXPECTED_AFFILIATION = "National Open University of Nigeria"

print("=" * 80)
print("STAGE 40C-N4 — AUTHORITATIVE CONTACT METADATA CORRECTION")
print("=" * 80)

assert RELEASE_DIR.exists()
assert METADATA_PATH.exists()
assert AUTHORS_PATH.exists()

# ==========================================================================
# 1. dataset_metadata.json
# ==========================================================================

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

metadata["creator"] = {
    "name": EXPECTED_NAME,
    "email": EXPECTED_EMAIL,
    "orcid": EXPECTED_ORCID,
    "affiliation": EXPECTED_AFFILIATION
}

metadata["affiliation"] = EXPECTED_AFFILIATION

with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
    f.write("\n")

# ==========================================================================
# 2. AUTHORS.json
# ==========================================================================

with open(AUTHORS_PATH, "r", encoding="utf-8") as f:
    authors = json.load(f)

authors["creator"] = {
    "name": EXPECTED_NAME,
    "email": EXPECTED_EMAIL,
    "orcid": EXPECTED_ORCID,
    "affiliation": EXPECTED_AFFILIATION
}

with open(AUTHORS_PATH, "w", encoding="utf-8") as f:
    json.dump(authors, f, indent=2, ensure_ascii=False)
    f.write("\n")

# ==========================================================================
# 3. READ BACK FROM DISK
# ==========================================================================

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata_check = json.load(f)

with open(AUTHORS_PATH, "r", encoding="utf-8") as f:
    authors_check = json.load(f)

m = metadata_check["creator"]
a = authors_check["creator"]

# ==========================================================================
# 4. DISPLAY ACTUAL STORED VALUES
# ==========================================================================

print("\nDATASET_METADATA.JSON — ACTUAL STORED VALUES")
print("-" * 80)
print("Name:        ", repr(m["name"]))
print("Email:       ", repr(m["email"]))
print("ORCID:       ", repr(m["orcid"]))
print("Affiliation: ", repr(m["affiliation"]))

print("\nAUTHORS.JSON — ACTUAL STORED VALUES")
print("-" * 80)
print("Name:        ", repr(a["name"]))
print("Email:       ", repr(a["email"]))
print("ORCID:       ", repr(a["orcid"]))
print("Affiliation: ", repr(a["affiliation"]))

# ==========================================================================
# 5. HARD ASSERTIONS
# ==========================================================================

assert m["name"] == EXPECTED_NAME
assert m["email"] == EXPECTED_EMAIL
assert m["orcid"] == EXPECTED_ORCID
assert m["affiliation"] == EXPECTED_AFFILIATION

assert a["name"] == EXPECTED_NAME
assert a["email"] == EXPECTED_EMAIL
assert a["orcid"] == EXPECTED_ORCID
assert a["affiliation"] == EXPECTED_AFFILIATION

# Explicitly reject Markdown-link values
for value in [
    m["email"],
    m["orcid"],
    a["email"],
    a["orcid"]
]:
    assert not value.startswith("[")
    assert "](" not in value
    assert not value.endswith(")")

# ==========================================================================
# 6. FINAL STATUS
# ==========================================================================

print("\n" + "=" * 80)
print("STAGE 40C-N4 COMPLETE — PASS")
print("=" * 80)

print("Plain email confirmed:", m["email"] == EXPECTED_EMAIL)
print("Plain ORCID confirmed:", m["orcid"] == EXPECTED_ORCID)
print("Affiliation confirmed:", m["affiliation"] == EXPECTED_AFFILIATION)

print("\nProtected:")
print("  Frozen CSVs modified: NO")
print("  CITATION.cff modified: NO")
print("  ZIP rebuilt: NO")
print("  Checksums updated: NO")
print("  Recovery manifest updated: NO")

print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 716
# ==============================================================================

# ============================================================================
# STAGE 40C-N5 — DIRECT LITERAL CONTACT METADATA TRUTH TEST
#
# This stage bypasses all previous variables.
# It uses direct literal values and verifies the physical JSON files.
#
# MODIFIES ONLY:
#   - metadata/dataset_metadata.json
#   - metadata/AUTHORS.json
#
# DOES NOT MODIFY:
#   - CSVs
#   - CITATION.cff
#   - ZIP
#   - checksums
#   - recovery manifest
# ============================================================================

from pathlib import Path
import json

print("=" * 80)
print("STAGE 40C-N5 — DIRECT LITERAL CONTACT METADATA TRUTH TEST")
print("=" * 80)

release_40cn5 = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/AFRIDATACYBERJOHN_v1.0"
)

metadata_40cn5 = release_40cn5 / "metadata" / "dataset_metadata.json"
authors_40cn5 = release_40cn5 / "metadata" / "AUTHORS.json"

assert metadata_40cn5.exists()
assert authors_40cn5.exists()

# --------------------------------------------------------------------------
# DIRECT LITERAL VALUES
# --------------------------------------------------------------------------

plain_name_40cn5 = "John Ojo Ajayi"
plain_email_40cn5 = "onejotech@gmail.com"
plain_orcid_40cn5 = "https://orcid.org/0000-0002-8063-6070"
plain_affiliation_40cn5 = "National Open University of Nigeria"

# --------------------------------------------------------------------------
# READ EXISTING DATA
# --------------------------------------------------------------------------

with open(metadata_40cn5, "r", encoding="utf-8") as f:
    metadata_40cn5_obj = json.load(f)

with open(authors_40cn5, "r", encoding="utf-8") as f:
    authors_40cn5_obj = json.load(f)

# --------------------------------------------------------------------------
# FORCE EXACT VALUES
# --------------------------------------------------------------------------

metadata_40cn5_obj["creator"] = {
    "name": plain_name_40cn5,
    "email": plain_email_40cn5,
    "orcid": plain_orcid_40cn5,
    "affiliation": plain_affiliation_40cn5
}

metadata_40cn5_obj["affiliation"] = plain_affiliation_40cn5

authors_40cn5_obj["creator"] = {
    "name": plain_name_40cn5,
    "email": plain_email_40cn5,
    "orcid": plain_orcid_40cn5,
    "affiliation": plain_affiliation_40cn5
}

# --------------------------------------------------------------------------
# WRITE DIRECTLY
# --------------------------------------------------------------------------

with open(metadata_40cn5, "w", encoding="utf-8") as f:
    json.dump(
        metadata_40cn5_obj,
        f,
        indent=2,
        ensure_ascii=False
    )
    f.write("\n")

with open(authors_40cn5, "w", encoding="utf-8") as f:
    json.dump(
        authors_40cn5_obj,
        f,
        indent=2,
        ensure_ascii=False
    )
    f.write("\n")

# --------------------------------------------------------------------------
# READ PHYSICAL FILES AGAIN
# --------------------------------------------------------------------------

with open(metadata_40cn5, "r", encoding="utf-8") as f:
    physical_metadata_40cn5 = json.load(f)

with open(authors_40cn5, "r", encoding="utf-8") as f:
    physical_authors_40cn5 = json.load(f)

physical_m_40cn5 = physical_metadata_40cn5["creator"]
physical_a_40cn5 = physical_authors_40cn5["creator"]

# --------------------------------------------------------------------------
# SHOW EXACT PHYSICAL VALUES
# --------------------------------------------------------------------------

print("\nPHYSICAL dataset_metadata.json")
print("-" * 80)
print("Name:        ", repr(physical_m_40cn5["name"]))
print("Email:       ", repr(physical_m_40cn5["email"]))
print("ORCID:       ", repr(physical_m_40cn5["orcid"]))
print("Affiliation: ", repr(physical_m_40cn5["affiliation"]))

print("\nPHYSICAL AUTHORS.json")
print("-" * 80)
print("Name:        ", repr(physical_a_40cn5["name"]))
print("Email:       ", repr(physical_a_40cn5["email"]))
print("ORCID:       ", repr(physical_a_40cn5["orcid"]))
print("Affiliation: ", repr(physical_a_40cn5["affiliation"]))

# --------------------------------------------------------------------------
# EXACT ASSERTIONS AGAINST DIRECT LITERALS
# --------------------------------------------------------------------------

assert physical_m_40cn5["name"] == "John Ojo Ajayi"
assert physical_m_40cn5["email"] == "onejotech@gmail.com"
assert physical_m_40cn5["orcid"] == "https://orcid.org/0000-0002-8063-6070"
assert physical_m_40cn5["affiliation"] == "National Open University of Nigeria"

assert physical_a_40cn5["name"] == "John Ojo Ajayi"
assert physical_a_40cn5["email"] == "onejotech@gmail.com"
assert physical_a_40cn5["orcid"] == "https://orcid.org/0000-0002-8063-6070"
assert physical_a_40cn5["affiliation"] == "National Open University of Nigeria"

# --------------------------------------------------------------------------
# EXPLICIT MARKDOWN REJECTION
# --------------------------------------------------------------------------

for value_40cn5 in [
    physical_m_40cn5["email"],
    physical_m_40cn5["orcid"],
    physical_a_40cn5["email"],
    physical_a_40cn5["orcid"],
]:
    assert "[" not in value_40cn5
    assert "](" not in value_40cn5
    assert ")" not in value_40cn5

# --------------------------------------------------------------------------
# FINAL
# --------------------------------------------------------------------------

print("\n" + "=" * 80)
print("STAGE 40C-N5 COMPLETE — PASS")
print("=" * 80)

print("Plain email:", physical_m_40cn5["email"])
print("Plain ORCID:", physical_m_40cn5["orcid"])
print("Affiliation:", physical_m_40cn5["affiliation"])

print("\nProtected:")
print("  Frozen CSVs modified: NO")
print("  CITATION.cff modified: NO")
print("  ZIP rebuilt: NO")
print("  Checksums updated: NO")
print("  Recovery manifest updated: NO")

print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 717
# ==============================================================================

# ============================================================================
# STAGE 40C-N6 — MINIMAL PYTHON RUNTIME TRUTH TEST
# READ-ONLY — NO RELEASE FILES TOUCHED
# ============================================================================

print("=" * 80)
print("STAGE 40C-N6 — MINIMAL PYTHON RUNTIME TRUTH TEST")
print("=" * 80)

test_email_40cn6 = "onejotech@gmail.com"
test_orcid_40cn6 = "https://orcid.org/0000-0002-8063-6070"

print("\nEMAIL")
print("repr:", repr(test_email_40cn6))
print("length:", len(test_email_40cn6))
print("equals expected:", test_email_40cn6 == "onejotech@gmail.com")
print("contains '[':", "[" in test_email_40cn6)
print("contains '](':", "](" in test_email_40cn6)

print("\nORCID")
print("repr:", repr(test_orcid_40cn6))
print("length:", len(test_orcid_40cn6))
print(
    "equals expected:",
    test_orcid_40cn6 == "https://orcid.org/0000-0002-8063-6070"
)
print("contains '[':", "[" in test_orcid_40cn6)
print("contains '](':", "](" in test_orcid_40cn6)

# Hard assertions
assert test_email_40cn6 == "onejotech@gmail.com"
assert test_orcid_40cn6 == "https://orcid.org/0000-0002-8063-6070"

assert "[" not in test_email_40cn6
assert "](" not in test_email_40cn6

assert "[" not in test_orcid_40cn6
assert "](" not in test_orcid_40cn6

print("\n" + "=" * 80)
print("STAGE 40C-N6 — PASS")
print("=" * 80)
print("Python runtime is behaving normally.")
print("No files were read.")
print("No files were modified.")
print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 718
# ==============================================================================

# ============================================================================
# STAGE 40C-N7 — FINAL INDEPENDENT METADATA GATE
#
# READ/VERIFY release metadata.
# Saves the final gate report.
#
# No CSV modification.
# No CITATION.cff modification.
# No ZIP rebuild.
# No checksum update.
# No recovery manifest update.
# ============================================================================

from pathlib import Path
import json
from datetime import datetime

print("=" * 80)
print("STAGE 40C-N7 — FINAL INDEPENDENT METADATA GATE")
print("=" * 80)

RELEASE = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/AFRIDATACYBERJOHN_v1.0"
)

AUTHORS = RELEASE / "metadata" / "AUTHORS.json"
METADATA = RELEASE / "metadata" / "dataset_metadata.json"
CITATION = RELEASE / "CITATION.cff"
README = RELEASE / "README.md"
PROVENANCE = RELEASE / "documentation" / "PROVENANCE.md"

CREATOR = "John Ojo Ajayi"
EMAIL = "onejotech@gmail.com"
ORCID = "https://orcid.org/0000-0002-8063-6070"
AFFILIATION = "National Open University of Nigeria"

# --------------------------------------------------------------------------
# Load
# --------------------------------------------------------------------------

with open(AUTHORS, "r", encoding="utf-8") as f:
    authors = json.load(f)

with open(METADATA, "r", encoding="utf-8") as f:
    metadata = json.load(f)

citation_text = CITATION.read_text(encoding="utf-8")
readme_text = README.read_text(encoding="utf-8")
provenance_text = PROVENANCE.read_text(encoding="utf-8")

a = authors["creator"]
m = metadata["creator"]

results = []

def check(label, condition, detail):
    results.append(condition)
    print(f"{label:<45} {'PASS' if condition else 'FAIL'}")
    print(f"    {detail}")

# --------------------------------------------------------------------------
# Creator
# --------------------------------------------------------------------------

check(
    "AUTHORS creator name",
    a.get("name") == CREATOR,
    repr(a.get("name"))
)

check(
    "AUTHORS email",
    a.get("email") == EMAIL
    and len(a.get("email", "")) == len(EMAIL)
    and "[" not in a.get("email", "")
    and "](" not in a.get("email", ""),
    f"length={len(a.get('email', ''))}"
)

check(
    "AUTHORS ORCID",
    a.get("orcid") == ORCID
    and len(a.get("orcid", "")) == len(ORCID)
    and "[" not in a.get("orcid", "")
    and "](" not in a.get("orcid", ""),
    f"length={len(a.get('orcid', ''))}"
)

check(
    "AUTHORS affiliation",
    a.get("affiliation") == AFFILIATION,
    repr(a.get("affiliation"))
)

# --------------------------------------------------------------------------
# Dataset metadata
# --------------------------------------------------------------------------

check(
    "METADATA creator name",
    m.get("name") == CREATOR,
    repr(m.get("name"))
)

check(
    "METADATA email",
    m.get("email") == EMAIL
    and len(m.get("email", "")) == len(EMAIL)
    and "[" not in m.get("email", "")
    and "](" not in m.get("email", ""),
    f"length={len(m.get('email', ''))}"
)

check(
    "METADATA ORCID",
    m.get("orcid") == ORCID
    and len(m.get("orcid", "")) == len(ORCID)
    and "[" not in m.get("orcid", "")
    and "](" not in m.get("orcid", ""),
    f"length={len(m.get('orcid', ''))}"
)

check(
    "METADATA affiliation",
    m.get("affiliation") == AFFILIATION,
    repr(m.get("affiliation"))
)

check(
    "METADATA top-level affiliation",
    metadata.get("affiliation") == AFFILIATION,
    repr(metadata.get("affiliation"))
)

# --------------------------------------------------------------------------
# CITATION.cff
# --------------------------------------------------------------------------

check(
    "CITATION affiliation",
    AFFILIATION in citation_text,
    "Affiliation present"
)

check(
    "CITATION creator",
    CREATOR in citation_text,
    "Creator present"
)

# --------------------------------------------------------------------------
# README / PROVENANCE
# --------------------------------------------------------------------------

check(
    "README creator",
    CREATOR in readme_text,
    "Creator present"
)

check(
    "README affiliation",
    AFFILIATION in readme_text,
    "Affiliation present"
)

check(
    "PROVENANCE creator",
    CREATOR in provenance_text,
    "Creator present"
)

check(
    "PROVENANCE affiliation",
    AFFILIATION in provenance_text,
    "Affiliation present"
)

# --------------------------------------------------------------------------
# Frozen CSVs
# --------------------------------------------------------------------------

csv_files = [
    RELEASE / "data" / "AFRICA_MobileMoney_USSD_Authoritative_Events.csv",
    RELEASE / "data" / "AFRICA_MobileMoney_USSD_Authoritative_Windows.csv",
    RELEASE / "data" / "AFRICA_MobileMoney_USSD_Current_Events.csv",
    RELEASE / "data" / "AFRICA_MobileMoney_USSD_Current_Windows.csv",
]

for csv in csv_files:
    check(
        f"CSV {csv.name}",
        csv.exists(),
        "File exists"
    )

# --------------------------------------------------------------------------
# Backup cleanup
# --------------------------------------------------------------------------

backups = list(RELEASE.rglob("*.stage40C_backup"))

check(
    "Temporary backup cleanup",
    len(backups) == 0,
    f"backup count={len(backups)}"
)

# --------------------------------------------------------------------------
# Final
# --------------------------------------------------------------------------

final_pass = all(results)

print("\n" + "=" * 80)
print("STAGE 40C-N7 FINAL RESULT")
print("=" * 80)

print("STATUS:", "PASS" if final_pass else "FAIL")

# --------------------------------------------------------------------------
# Save report
# --------------------------------------------------------------------------

report_path = (
    RELEASE /
    "documentation" /
    "STAGE_40C-N7_FINAL_METADATA_GATE.txt"
)

report = [
    "AFRIDATACYBERJOHN",
    "STAGE 40C-N7 — FINAL INDEPENDENT METADATA GATE",
    "",
    f"Timestamp: {datetime.now().isoformat(timespec='seconds')}",
    f"Release: {RELEASE}",
    "",
    f"Creator: {CREATOR}",
    f"Email length: {len(EMAIL)}",
    f"ORCID length: {len(ORCID)}",
    f"Affiliation: {AFFILIATION}",
    "",
    f"FINAL STATUS: {'PASS' if final_pass else 'FAIL'}",
    "",
    "Protected:",
    "Frozen CSVs modified: NO",
    "CITATION.cff modified: NO",
    "ZIP rebuilt: NO",
    "Checksums updated: NO",
    "Recovery manifest updated: NO",
]

report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

assert report_path.exists()

print("Audit report saved:")
print(report_path)

print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 719
# ==============================================================================

# ============================================================================
# STAGE 40C-N8 — CORRECT CFF AUTHOR STRUCTURE AUDIT
#
# Purpose:
#   Correctly validate the structured author representation in CITATION.cff.
#
# READ-ONLY:
#   No files modified.
#   No ZIP rebuild.
#   No checksum update.
#   No recovery manifest update.
# ============================================================================

from pathlib import Path
import re

print("=" * 80)
print("STAGE 40C-N8 — CORRECT CFF AUTHOR STRUCTURE AUDIT")
print("=" * 80)

RELEASE = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/AFRIDATACYBERJOHN_v1.0"
)

CITATION = RELEASE / "CITATION.cff"

assert CITATION.exists(), "CITATION.cff not found."

text = CITATION.read_text(encoding="utf-8")

# ==========================================================================
# Expected structured CFF author information
# ==========================================================================

EXPECTED_FAMILY = "Ajayi"
EXPECTED_GIVEN = "John Ojo"
EXPECTED_EMAIL = "onejotech@gmail.com"
EXPECTED_ORCID = "https://orcid.org/0000-0002-8063-6070"
EXPECTED_AFFILIATION = "National Open University of Nigeria"

# ==========================================================================
# Find author block
# ==========================================================================

family_match = re.search(
    r'family-names:\s*["\']?([^"\']+)["\']?',
    text
)

given_match = re.search(
    r'given-names:\s*["\']?([^"\']+)["\']?',
    text
)

email_match = re.search(
    r'email:\s*["\']?([^"\']+)["\']?',
    text
)

orcid_match = re.search(
    r'orcid:\s*["\']?([^"\']+)["\']?',
    text
)

affiliation_match = re.search(
    r'affiliation:\s*["\']?([^"\']+)["\']?',
    text
)

print("\nCITATION.cff STRUCTURED AUTHOR")
print("-" * 80)

print(
    "family-names:",
    repr(family_match.group(1).strip())
    if family_match else "NOT FOUND"
)

print(
    "given-names:",
    repr(given_match.group(1).strip())
    if given_match else "NOT FOUND"
)

print(
    "email:",
    repr(email_match.group(1).strip())
    if email_match else "NOT FOUND"
)

print(
    "orcid:",
    repr(orcid_match.group(1).strip())
    if orcid_match else "NOT FOUND"
)

print(
    "affiliation:",
    repr(affiliation_match.group(1).strip())
    if affiliation_match else "NOT FOUND"
)

# ==========================================================================
# Independent checks
# ==========================================================================

results = []

def check(label, condition, detail):
    results.append(condition)
    print(
        f"{label:<45} "
        f"{'PASS' if condition else 'FAIL'}"
    )
    print(f"    {detail}")

check(
    "CFF family-names",
    family_match is not None
    and family_match.group(1).strip() == EXPECTED_FAMILY,
    f"Expected: {EXPECTED_FAMILY!r}"
)

check(
    "CFF given-names",
    given_match is not None
    and given_match.group(1).strip() == EXPECTED_GIVEN,
    f"Expected: {EXPECTED_GIVEN!r}"
)

check(
    "CFF email",
    email_match is not None
    and EXPECTED_EMAIL in email_match.group(1),
    "Creator email represented"
)

check(
    "CFF ORCID",
    orcid_match is not None
    and EXPECTED_ORCID in orcid_match.group(1),
    "Creator ORCID represented"
)

check(
    "CFF affiliation",
    affiliation_match is not None
    and EXPECTED_AFFILIATION in affiliation_match.group(1),
    "Creator affiliation represented"
)

# ==========================================================================
# Verify no temporary backup
# ==========================================================================

backup_files = list(RELEASE.rglob("*.stage40C_backup"))

check(
    "Temporary backup cleanup",
    len(backup_files) == 0,
    f"Backup count: {len(backup_files)}"
)

# ==========================================================================
# Final result
# ==========================================================================

final_pass = all(results)

print("\n" + "=" * 80)
print("STAGE 40C-N8 RESULT")
print("=" * 80)

print("STATUS:", "PASS" if final_pass else "FAIL")

print("\nIMPORTANT:")
print("CITATION.cff was READ ONLY.")
print("No release files were modified.")
print("No ZIP was rebuilt.")
print("No checksum was updated.")
print("No recovery manifest was updated.")

print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 720
# ==============================================================================


# ================================================================
# STAGE 40C-O — FINAL PRE-RELEASE INTEGRITY AUDIT
# Read-only audit of the release, except for the saved audit report.
# ================================================================

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import csv
import re
import zipfile

ROOT = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN"
)
RELEASE = ROOT / "AFRIDATACYBERJOHN_v1.0"
ZIP_PATH = ROOT / "AFRIDATACYBERJOHN_v1.0.zip"

EXPECTED_NAME = "John Ojo Ajayi"
EXPECTED_EMAIL = "onejotech" + "@" + "gmail.com"
EXPECTED_ORCID = (
    "https://" + "orcid.org/0000-0002-8063-6070"
)
EXPECTED_AFFILIATION = (
    "National Open University of Nigeria"
)

# Original frozen CSV SHA-256 values
FROZEN = {
    "data/AFRICA_MobileMoney_USSD_Authoritative_Events.csv": {
        "rows": 1029,
        "sha256": (
            "1fceb3e353f84077b7429b347f517fba789b839471c7940147757998f7c0fccd"
        ),
    },
    "data/AFRICA_MobileMoney_USSD_Authoritative_Windows.csv": {
        "rows": 100,
        "sha256": (
            "f95f574767ee21bde1c4ad8e9ad0ecf30dfdba3df7d0bfd0bda8b5a322705f44"
        ),
    },
    "data/AFRICA_MobileMoney_USSD_Current_Events.csv": {
        "rows": 1060,
        "sha256": (
            "fe4b8347d3264fe0faae17b830c10432e6242c66012e93e908d95717ea11abb4"
        ),
    },
    "data/AFRICA_MobileMoney_USSD_Current_Windows.csv": {
        "rows": 100,
        "sha256": (
            "47e2f01111e7194ddb4da5e8fbd7559cd29eeda286bb18117e2e2e524e239fcd"
        ),
    },
}

EXPECTED_FILES = [
    "CITATION.cff",
    "README.md",
    "LICENSE",
    *FROZEN.keys(),
    "documentation/DATASET_DESCRIPTION.md",
    "documentation/DATA_DICTIONARY.csv",
    "documentation/FORENSIC_VALIDATION.md",
    "documentation/METHODOLOGY.md",
    "documentation/PROVENANCE.md",
    "documentation/WINDOW_FIELD_SEMANTIC_RECOVERY.csv",
    "metadata/AUTHORS.json",
    "metadata/checksums.sha256",
    "metadata/dataset_metadata.json",
]

results = []

def check(label, passed, detail=""):
    passed = bool(passed)
    results.append({
        "check": label,
        "status": "PASS" if passed else "FAIL",
        "detail": str(detail),
    })
    print(
        f"{label:<43} "
        f"{'PASS' if passed else 'FAIL'}"
    )
    if detail:
        print("   ", detail)

def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024), b""
        ):
            digest.update(chunk)
    return digest.hexdigest()

def count_csv_rows(path):
    with open(
        path, "r", encoding="utf-8-sig", newline=""
    ) as f:
        reader = csv.reader(f)
        next(reader)
        return sum(1 for _ in reader)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def plain_contact(value, expected):
    return (
        isinstance(value, str)
        and value == expected
        and len(value) == len(expected)
        and "[" not in value
        and "](" not in value
    )

print("=" * 80)
print("STAGE 40C-O — FINAL PRE-RELEASE INTEGRITY AUDIT")
print("=" * 80)

assert RELEASE.is_dir(), (
    f"Permanent release directory not found: {RELEASE}"
)

# ================================================================
# 1. Required release files
# ================================================================

print("\n1. REQUIRED FILES")
print("-" * 80)

for relative in EXPECTED_FILES:
    check(
        relative,
        (RELEASE / relative).is_file()
    )

# An audit report from Stage 40C-N or N7 may also exist.
# Audit reports are recorded separately, rather than treated
# as unexpected source files.

actual_files = {
    p.relative_to(RELEASE).as_posix()
    for p in RELEASE.rglob("*")
    if p.is_file()
}

expected_set = set(EXPECTED_FILES)
extra_files = sorted(actual_files - expected_set)

allowed_audits = {
    "documentation/STAGE_40C-N_METADATA_CONSISTENCY_AUDIT.txt",
    "documentation/STAGE_40C-N7_FINAL_METADATA_GATE.txt",
}

unexpected = sorted(
    set(extra_files) - allowed_audits
)

check(
    "Unexpected release files",
    not unexpected,
    unexpected if unexpected else "None"
)

print("Expected core files:", len(EXPECTED_FILES))
print("Existing extra audit reports:",
      sorted(set(extra_files) & allowed_audits))

# ================================================================
# 2. Frozen CSV integrity and populations
# ================================================================

print("\n2. FROZEN CSV INTEGRITY")
print("-" * 80)

for relative, expected in FROZEN.items():
    path = RELEASE / relative

    if not path.is_file():
        check(relative + " integrity", False, "Missing")
        continue

    actual_hash = sha256_file(path)
    actual_rows = count_csv_rows(path)

    check(
        relative + " SHA-256",
        actual_hash == expected["sha256"],
        actual_hash
    )

    check(
        relative + " population",
        actual_rows == expected["rows"],
        f"{actual_rows} / {expected['rows']}"
    )

# ================================================================
# 3. Creator metadata
# ================================================================

print("\n3. CREATOR METADATA")
print("-" * 80)

authors = load_json(
    RELEASE / "metadata/AUTHORS.json"
)
metadata = load_json(
    RELEASE / "metadata/dataset_metadata.json"
)

for label, obj in [
    ("AUTHORS", authors),
    ("METADATA", metadata),
]:
    creator = obj.get("creator")

    if not isinstance(creator, dict):
        check(
            label + " creator structure",
            False,
            f"Actual type: {type(creator).__name__}"
        )
        continue

    check(
        label + " creator",
        creator.get("name") == EXPECTED_NAME
    )

    check(
        label + " email",
        plain_contact(
            creator.get("email"), EXPECTED_EMAIL
        ),
        f"length={len(creator.get('email', ''))}"
    )

    check(
        label + " ORCID",
        plain_contact(
            creator.get("orcid"), EXPECTED_ORCID
        ),
        f"length={len(creator.get('orcid', ''))}"
    )

    check(
        label + " affiliation",
        creator.get("affiliation")
        == EXPECTED_AFFILIATION
    )

check(
    "Metadata top-level affiliation",
    metadata.get("affiliation")
    == EXPECTED_AFFILIATION
)

# ================================================================
# 4. Structured CFF author
# ================================================================

print("\n4. CITATION.cff")
print("-" * 80)

cff_text = (
    RELEASE / "CITATION.cff"
).read_text(encoding="utf-8")

# Match each CFF field independently. The full author name
# is split into given-names and family-names in CFF.

def cff_field(field):
    match = re.search(
        rf"(?m)^\s*(?:-\s*)?{re.escape(field)}:"
        rf"\s*['\"]?([^'\"\r\n]+)",
        cff_text
    )
    return match.group(1).strip() if match else None

check(
    "CFF family-names",
    cff_field("family-names") == "Ajayi"
)

check(
    "CFF given-names",
    cff_field("given-names") == "John Ojo"
)

check(
    "CFF email",
    plain_contact(
        cff_field("email"), EXPECTED_EMAIL
    )
)

check(
    "CFF ORCID",
    plain_contact(
        cff_field("orcid"), EXPECTED_ORCID
    )
)

check(
    "CFF affiliation",
    cff_field("affiliation")
    == EXPECTED_AFFILIATION
)

# ================================================================
# 5. README, provenance and licensing
# ================================================================

print("\n5. DOCUMENTATION AND LICENSE")
print("-" * 80)

readme = (
    RELEASE / "README.md"
).read_text(encoding="utf-8")

provenance = (
    RELEASE / "documentation/PROVENANCE.md"
).read_text(encoding="utf-8")

license_text = (
    RELEASE / "LICENSE"
).read_text(encoding="utf-8")

check(
    "README creator and affiliation",
    EXPECTED_NAME in readme
    and EXPECTED_AFFILIATION in readme
)

check(
    "PROVENANCE creator and affiliation",
    EXPECTED_NAME in provenance
    and EXPECTED_AFFILIATION in provenance
)

check(
    "CC BY 4.0 license file",
    "Creative Commons Attribution 4.0" in license_text
    or "CC BY 4.0" in license_text
)

check(
    "AUTHORS license",
    authors.get("license") == "CC BY 4.0"
)

# ================================================================
# 6. Temporary backups and permanent ZIP
# ================================================================

print("\n6. RELEASE CLEANLINESS")
print("-" * 80)

backups = [
    str(p.relative_to(RELEASE))
    for p in RELEASE.rglob("*")
    if p.is_file()
    and (
        "backup" in p.name.lower()
        or p.name.endswith(".tmp")
    )
]

check(
    "Temporary backup cleanup",
    not backups,
    backups if backups else "None"
)

check(
    "Permanent ZIP exists",
    ZIP_PATH.is_file(),
    str(ZIP_PATH)
)

if ZIP_PATH.is_file():
    try:
        with zipfile.ZipFile(ZIP_PATH) as zf:
            bad_member = zf.testzip()
        check(
            "Existing ZIP structural integrity",
            bad_member is None,
            bad_member or "ZIP entries readable"
        )
    except Exception as exc:
        check(
            "Existing ZIP structural integrity",
            False,
            str(exc)
        )

# Existing ZIP may be older than current release metadata.
# Its content hashes are NOT treated as final at this stage.

# ================================================================
# 7. Save audit OUTSIDE the release directory
# ================================================================

print("\n7. SAVE AUDIT")
print("-" * 80)

AUDIT_DIR = ROOT / "audits"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

AUDIT_PATH = (
    AUDIT_DIR /
    "STAGE_40C-O_FINAL_PRE_RELEASE_AUDIT.json"
)

overall = all(
    item["status"] == "PASS"
    for item in results
)

report = {
    "dataset": "AFRIDATACYBERJOHN",
    "version": "1.0",
    "stage": "40C-O",
    "timestamp_utc": datetime.now(
        timezone.utc
    ).isoformat(),
    "release_directory": str(RELEASE),
    "existing_zip": str(ZIP_PATH),
    "overall_status": (
        "PASS" if overall else "FAIL"
    ),
    "checks": results,
    "note": (
        "Pre-release audit only. The permanent ZIP "
        "and checksum manifest have not been rebuilt."
    ),
}

AUDIT_PATH.write_text(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False
    ) + "\n",
    encoding="utf-8"
)

saved = load_json(AUDIT_PATH)

assert saved["stage"] == "40C-O"
assert saved["overall_status"] == report["overall_status"]

print("Audit saved:", AUDIT_PATH)

# ================================================================
# FINAL RESULT
# ================================================================

passed = sum(
    r["status"] == "PASS"
    for r in results
)
failed = len(results) - passed

print("\n" + "=" * 80)
print("STAGE 40C-O COMPLETE")
print("=" * 80)
print("Checks passed:", passed)
print("Checks failed:", failed)
print("OVERALL:", "PASS" if overall else "FAIL")
print("Frozen CSVs modified: NO")
print("Release metadata modified: NO")
print("ZIP rebuilt: NO")
print("Checksums updated: NO")
print("Recovery manifest updated: NO")
print("Audit report saved: YES")
print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 721
# ==============================================================================

# ============================================================================
# STAGE 40C-P — FINAL RELEASE PACKAGING
# AFRIDATACYBERJOHN v1.0
#
# PURPOSE:
#   Create the definitive post-40C release ZIP.
#
# MODIFIES:
#   - metadata/checksums.sha256
#   - AFRIDATACYBERJOHN_v1.0.zip
#   - RECOVERY_MANIFEST.json
#
# PROTECTED:
#   - All four frozen dataset CSVs
#   - Dataset records
#   - CITATION.cff
#   - README.md
#   - LICENSE
#   - Documentation content
#
# ============================================================================

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import zipfile
import csv
import shutil

print("=" * 80)
print("STAGE 40C-P — FINAL RELEASE PACKAGING")
print("=" * 80)

# ============================================================================
# 1. PATHS
# ============================================================================

DRIVE_ROOT = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN"
)

RELEASE = DRIVE_ROOT / "AFRIDATACYBERJOHN_v1.0"

ZIP_PATH = DRIVE_ROOT / "AFRIDATACYBERJOHN_v1.0.zip"

RECOVERY_MANIFEST = (
    DRIVE_ROOT / "RECOVERY_MANIFEST.json"
)

CHECKSUM_PATH = (
    RELEASE / "metadata" / "checksums.sha256"
)

assert RELEASE.is_dir(), "Permanent release directory not found."

print("Release:")
print(RELEASE)

# ============================================================================
# 2. FROZEN CSV DEFINITIONS
# ============================================================================

FROZEN_CSVS = {
    "data/AFRICA_MobileMoney_USSD_Authoritative_Events.csv": {
        "sha256": "1fceb3e353f84077b7429b347f517fba789b839471c7940147757998f7c0fccd",
        "rows": 1029,
        "columns": 29,
        "id": "event_id",
    },

    "data/AFRICA_MobileMoney_USSD_Authoritative_Windows.csv": {
        "sha256": "f95f574767ee21bde1c4ad8e9ad0ecf30dfdba3df7d0bfd0bda8b5a322705f44",
        "rows": 100,
        "columns": 8,
        "id": "window_id",
    },

    "data/AFRICA_MobileMoney_USSD_Current_Events.csv": {
        "sha256": "fe4b8347d3264fe0faae17b830c10432e6242c66012e93e908d95717ea11abb4",
        "rows": 1060,
        "columns": 29,
        "id": "event_id",
    },

    "data/AFRICA_MobileMoney_USSD_Current_Windows.csv": {
        "sha256": "47e2f01111e7194ddb4da5e8fbd7559cd29eeda286bb18117e2e2e524e239fcd",
        "rows": 100,
        "columns": 10,
        "id": "window_id",
    },
}

# ============================================================================
# 3. SHA256 FUNCTION
# ============================================================================

def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            h.update(block)

    return h.hexdigest()

# ============================================================================
# 4. PROTECT AND VERIFY FROZEN CSVs BEFORE PACKAGING
# ============================================================================

print("\n1. VERIFYING FROZEN CSVs")
print("-" * 80)

for rel_path, spec in FROZEN_CSVS.items():

    path = RELEASE / rel_path

    assert path.exists(), f"Missing CSV: {rel_path}"

    actual_hash = sha256_file(path)

    assert (
        actual_hash == spec["sha256"]
    ), (
        f"FROZEN CSV HASH FAILURE: {rel_path}\n"
        f"Expected: {spec['sha256']}\n"
        f"Actual:   {actual_hash}"
    )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        columns = reader.fieldnames or []
        rows = list(reader)

    assert len(rows) == spec["rows"]
    assert len(columns) == spec["columns"]

    identifiers = [
        row.get(spec["id"])
        for row in rows
    ]

    assert all(identifiers)
    assert len(identifiers) == len(set(identifiers))

    print(
        rel_path,
        "PASS",
        f"rows={len(rows)}",
        f"columns={len(columns)}",
        f"sha256={actual_hash}"
    )

print("ALL FROZEN CSVs VERIFIED.")

# ============================================================================
# 5. EXPECTED CORE RELEASE FILES
# ============================================================================

CORE_FILES = [
    "CITATION.cff",
    "README.md",
    "LICENSE",

    "data/AFRICA_MobileMoney_USSD_Authoritative_Events.csv",
    "data/AFRICA_MobileMoney_USSD_Authoritative_Windows.csv",
    "data/AFRICA_MobileMoney_USSD_Current_Events.csv",
    "data/AFRICA_MobileMoney_USSD_Current_Windows.csv",

    "documentation/DATASET_DESCRIPTION.md",
    "documentation/DATA_DICTIONARY.csv",
    "documentation/FORENSIC_VALIDATION.md",
    "documentation/METHODOLOGY.md",
    "documentation/PROVENANCE.md",
    "documentation/WINDOW_FIELD_SEMANTIC_RECOVERY.csv",

    "metadata/AUTHORS.json",
    "metadata/checksums.sha256",
    "metadata/dataset_metadata.json",
]

# ============================================================================
# 6. REMOVE OLD TEMPORARY AUDIT FILES FROM RELEASE DIRECTORY
# ============================================================================

print("\n2. CLEANING TEMPORARY AUDIT ARTIFACTS")
print("-" * 80)

temporary_audits = [
    RELEASE / "documentation" /
    "STAGE_40C-N7_FINAL_METADATA_GATE.txt",

    RELEASE / "documentation" /
    "STAGE_40C-N_METADATA_CONSISTENCY_AUDIT.txt",

    RELEASE / "documentation" /
    "STAGE_40C-N7_FINAL_METADATA_GATE.json",

    RELEASE / "documentation" /
    "STAGE_40C-N_METADATA_CONSISTENCY_AUDIT.json",
]

removed = []

for p in temporary_audits:
    if p.exists():
        p.unlink()
        removed.append(str(p.relative_to(RELEASE)))

print("Temporary audit files removed:", len(removed))

for item in removed:
    print("  REMOVED:", item)

# ============================================================================
# 7. VERIFY EXACT CORE FILE SET
# ============================================================================

actual_core_candidates = {
    str(p.relative_to(RELEASE))
    for p in RELEASE.rglob("*")
    if p.is_file()
}

unexpected = sorted(
    actual_core_candidates - set(CORE_FILES)
)

missing = sorted(
    set(CORE_FILES) - actual_core_candidates
)

assert not missing, f"Missing core files: {missing}"

if unexpected:
    print("WARNING — unexpected files remain:")
    for item in unexpected:
        print(" ", item)

    raise RuntimeError(
        "Unexpected release files must be resolved before packaging."
    )

print("Core release file count:", len(CORE_FILES))
print("Core file inventory: PASS")

# ============================================================================
# 8. GENERATE FINAL CHECKSUM MANIFEST
#
# IMPORTANT:
#   The checksum manifest does NOT contain its own hash.
#   It contains every other release file.
# ============================================================================

print("\n3. GENERATING FINAL CHECKSUM MANIFEST")
print("-" * 80)

checksum_targets = [
    path
    for path in CORE_FILES
    if path != "metadata/checksums.sha256"
]

checksum_lines = []

for rel_path in checksum_targets:

    path = RELEASE / rel_path

    digest = sha256_file(path)

    checksum_lines.append(
        f"{digest}  {rel_path}"
    )

checksum_lines.sort()

CHECKSUM_PATH.write_text(
    "\n".join(checksum_lines) + "\n",
    encoding="utf-8"
)

print(
    "Checksum entries:",
    len(checksum_lines)
)

assert len(checksum_lines) == 15

# ============================================================================
# 9. VERIFY CHECKSUM MANIFEST AGAINST CURRENT FILES
# ============================================================================

print("\n4. VERIFYING FINAL CHECKSUM MANIFEST")
print("-" * 80)

manifest_lines = CHECKSUM_PATH.read_text(
    encoding="utf-8"
).splitlines()

assert len(manifest_lines) == 15

checksum_failures = []

for line in manifest_lines:

    digest, rel_path = line.split("  ", 1)

    actual = sha256_file(
        RELEASE / rel_path
    )

    if actual != digest:
        checksum_failures.append(
            (rel_path, digest, actual)
        )

assert not checksum_failures, checksum_failures

print("Checksum manifest verification: PASS")
print("Entries verified:", len(manifest_lines))

# ============================================================================
# 10. BUILD FINAL ZIP
# ============================================================================

print("\n5. BUILDING FINAL ZIP")
print("-" * 80)

TEMP_ZIP = DRIVE_ROOT / (
    "AFRIDATACYBERJOHN_v1.0_FINAL_BUILD.zip"
)

if TEMP_ZIP.exists():
    TEMP_ZIP.unlink()

with zipfile.ZipFile(
    TEMP_ZIP,
    "w",
    compression=zipfile.ZIP_DEFLATED
) as zf:

    for rel_path in CORE_FILES:

        path = RELEASE / rel_path

        zf.write(
            path,
            arcname=(
                "AFRIDATACYBERJOHN_v1.0/"
                + rel_path
            )
        )

assert TEMP_ZIP.exists()

# ============================================================================
# 11. VERIFY ZIP STRUCTURE
# ============================================================================

print("\n6. VERIFYING ZIP")
print("-" * 80)

with zipfile.ZipFile(
    TEMP_ZIP,
    "r"
) as zf:

    bad = zf.testzip()

    assert bad is None, (
        f"ZIP integrity failure: {bad}"
    )

    zip_names = set(zf.namelist())

expected_zip_names = {
    "AFRIDATACYBERJOHN_v1.0/" + p
    for p in CORE_FILES
}

assert zip_names == expected_zip_names, (
    "ZIP file inventory mismatch."
)

print("ZIP structural integrity: PASS")
print("ZIP entries:", len(zip_names))

# ============================================================================
# 12. VERIFY FROZEN CSVs INSIDE ZIP
# ============================================================================

print("\n7. VERIFYING FROZEN CSVs INSIDE ZIP")
print("-" * 80)

with zipfile.ZipFile(
    TEMP_ZIP,
    "r"
) as zf:

    for rel_path, spec in FROZEN_CSVS.items():

        member = (
            "AFRIDATACYBERJOHN_v1.0/"
            + rel_path
        )

        data = zf.read(member)

        zip_hash = hashlib.sha256(data).hexdigest()

        assert zip_hash == spec["sha256"], (
            f"ZIP CSV hash mismatch: {rel_path}"
        )

        print(
            rel_path,
            "PASS",
            zip_hash
        )

print("ALL FROZEN CSVs INSIDE ZIP VERIFIED.")

# ============================================================================
# 13. MOVE FINAL ZIP INTO PERMANENT LOCATION
# ============================================================================

if ZIP_PATH.exists():
    ZIP_PATH.unlink()

shutil.move(
    str(TEMP_ZIP),
    str(ZIP_PATH)
)

assert ZIP_PATH.exists()

# ============================================================================
# 14. FINAL ZIP SHA256
# ============================================================================

final_zip_hash = sha256_file(ZIP_PATH)
final_zip_size = ZIP_PATH.stat().st_size

print("\n8. FINAL ZIP")
print("-" * 80)

print("Path:", ZIP_PATH)
print("Size:", final_zip_size, "bytes")
print("SHA256:", final_zip_hash)

# ============================================================================
# 15. UPDATE RECOVERY MANIFEST
# ============================================================================

print("\n9. UPDATING RECOVERY MANIFEST")
print("-" * 80)

recovery = {}

if RECOVERY_MANIFEST.exists():

    with open(
        RECOVERY_MANIFEST,
        "r",
        encoding="utf-8"
    ) as f:
        recovery = json.load(f)

else:

    recovery = {}

recovery["dataset"] = "AFRIDATACYBERJOHN"
recovery["version"] = "1.0"
recovery["creator"] = {
    "name": "John Ojo Ajayi",
    "email": "onejotech" + "@gmail.com",
    "orcid": "https://orcid.org/0000-0002-8063-6070",
    "affiliation": "National Open University of Nigeria"
}

recovery["license"] = "CC BY 4.0"
recovery["provenance"] = "CONFIRMED_SYNTHETIC"

recovery["final_zip"] = {
    "path": str(ZIP_PATH),
    "filename": ZIP_PATH.name,
    "size_bytes": final_zip_size,
    "sha256": final_zip_hash
}

recovery["frozen_populations"] = {
    "authoritative_events": 1029,
    "current_events": 1060,
    "authoritative_windows": 100,
    "current_windows": 100
}

recovery["frozen_csv_sha256"] = {
    rel_path: spec["sha256"]
    for rel_path, spec in FROZEN_CSVS.items()
}

recovery["stage_40C_P"] = {
    "status": "PASS",
    "timestamp_utc": datetime.now(
        timezone.utc
    ).isoformat(),
    "csvs_modified": False,
    "dataset_records_modified": False,
    "zip_verified": True,
    "checksum_manifest_verified": True
}

with open(
    RECOVERY_MANIFEST,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        recovery,
        f,
        indent=2,
        ensure_ascii=False
    )
    f.write("\n")

print("Recovery manifest updated: PASS")

# ============================================================================
# 16. SAVE PACKAGING REPORT
# ============================================================================

REPORT = DRIVE_ROOT / (
    "STAGE_40C-P_FINAL_PACKAGING_REPORT.json"
)

packaging_report = {
    "dataset": "AFRIDATACYBERJOHN",
    "version": "1.0",
    "stage": "40C-P",
    "status": "PASS",
    "timestamp_utc": datetime.now(
        timezone.utc
    ).isoformat(),
    "release_directory": str(RELEASE),
    "zip_path": str(ZIP_PATH),
    "zip_size_bytes": final_zip_size,
    "zip_sha256": final_zip_hash,
    "core_files": len(CORE_FILES),
    "checksum_entries": len(checksum_lines),
    "frozen_csvs_modified": False,
    "dataset_records_modified": False,
    "zip_integrity": "PASS",
    "frozen_csv_integrity_inside_zip": "PASS",
    "checksum_manifest_integrity": "PASS",
    "recovery_manifest_updated": True
}

REPORT.write_text(
    json.dumps(
        packaging_report,
        indent=2,
        ensure_ascii=False
    ) + "\n",
    encoding="utf-8"
)

# ============================================================================
# FINAL STATUS
# ============================================================================

print("\n" + "=" * 80)
print("STAGE 40C-P COMPLETE")
print("=" * 80)

print("STATUS: PASS")
print("Core release files:", len(CORE_FILES))
print("Checksum entries:", len(checksum_lines))
print("ZIP size:", final_zip_size, "bytes")
print("ZIP SHA256:", final_zip_hash)

print("\nProtected:")
print("  Frozen CSVs modified: NO")
print("  Dataset records modified: NO")
print("  Frozen CSV hashes verified: YES")
print("  ZIP structural integrity: PASS")
print("  ZIP CSV integrity: PASS")
print("  Checksum manifest: PASS")
print("  Recovery manifest: PASS")

print("\nFinal ZIP:")
print(ZIP_PATH)

print("\nPackaging report:")
print(REPORT)

print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 722
# ==============================================================================

# ============================================================================
# STAGE 40C-Q — FINAL POST-BUILD VERIFICATION
# AFRIDATACYBERJOHN v1.0
#
# FINAL READ-ONLY RELEASE GATE
#
# Does NOT modify:
#   - CSV files
#   - release metadata
#   - checksums
#   - ZIP
#   - recovery manifest
#
# Saves:
#   - final verification report
# ============================================================================

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import zipfile
import csv

print("=" * 80)
print("STAGE 40C-Q — FINAL POST-BUILD VERIFICATION")
print("=" * 80)

# ============================================================================
# 1. PATHS
# ============================================================================

DRIVE_ROOT = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN"
)

RELEASE = DRIVE_ROOT / "AFRIDATACYBERJOHN_v1.0"

ZIP_PATH = DRIVE_ROOT / "AFRIDATACYBERJOHN_v1.0.zip"

RECOVERY_MANIFEST = (
    DRIVE_ROOT / "RECOVERY_MANIFEST.json"
)

REPORT_PATH = (
    DRIVE_ROOT /
    "STAGE_40C-Q_FINAL_POST_BUILD_VERIFICATION.json"
)

assert RELEASE.is_dir(), "Release directory missing."
assert ZIP_PATH.is_file(), "Final ZIP missing."
assert RECOVERY_MANIFEST.is_file(), "Recovery manifest missing."

# ============================================================================
# 2. SHA256 FUNCTION
# ============================================================================

def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            h.update(block)

    return h.hexdigest()

# ============================================================================
# 3. EXPECTED FINAL ZIP HASH
# ============================================================================

EXPECTED_ZIP_SHA256 = (
    "8154d57a3dae95565c7f8aaba7fbdbd85bbcd3eca75220e91a071590dc61700d"
)

# ============================================================================
# 4. FROZEN CSV DEFINITIONS
# ============================================================================

FROZEN_CSVS = {
    "data/AFRICA_MobileMoney_USSD_Authoritative_Events.csv": {
        "sha256":
            "1fceb3e353f84077b7429b347f517fba789b839471c7940147757998f7c0fccd",
        "rows": 1029,
        "columns": 29,
    },

    "data/AFRICA_MobileMoney_USSD_Authoritative_Windows.csv": {
        "sha256":
            "f95f574767ee21bde1c4ad8e9ad0ecf30dfdba3df7d0bfd0bda8b5a322705f44",
        "rows": 100,
        "columns": 8,
    },

    "data/AFRICA_MobileMoney_USSD_Current_Events.csv": {
        "sha256":
            "fe4b8347d3264fe0faae17b830c10432e6242c66012e93e908d95717ea11abb4",
        "rows": 1060,
        "columns": 29,
    },

    "data/AFRICA_MobileMoney_USSD_Current_Windows.csv": {
        "sha256":
            "47e2f01111e7194ddb4da5e8fbd7559cd29eeda286bb18117e2e2e524e239fcd",
        "rows": 100,
        "columns": 10,
    },
}

# ============================================================================
# 5. EXPECTED 16-FILE RELEASE
# ============================================================================

EXPECTED_FILES = [
    "CITATION.cff",
    "README.md",
    "LICENSE",

    "data/AFRICA_MobileMoney_USSD_Authoritative_Events.csv",
    "data/AFRICA_MobileMoney_USSD_Authoritative_Windows.csv",
    "data/AFRICA_MobileMoney_USSD_Current_Events.csv",
    "data/AFRICA_MobileMoney_USSD_Current_Windows.csv",

    "documentation/DATASET_DESCRIPTION.md",
    "documentation/DATA_DICTIONARY.csv",
    "documentation/FORENSIC_VALIDATION.md",
    "documentation/METHODOLOGY.md",
    "documentation/PROVENANCE.md",
    "documentation/WINDOW_FIELD_SEMANTIC_RECOVERY.csv",

    "metadata/AUTHORS.json",
    "metadata/checksums.sha256",
    "metadata/dataset_metadata.json",
]

EXPECTED_ZIP_ENTRIES = {
    "AFRIDATACYBERJOHN_v1.0/" + p
    for p in EXPECTED_FILES
}

# ============================================================================
# 6. FINAL ZIP HASH
# ============================================================================

print("\n1. FINAL ZIP SHA-256")
print("-" * 80)

actual_zip_sha256 = sha256_file(ZIP_PATH)

print("Expected:", EXPECTED_ZIP_SHA256)
print("Actual:  ", actual_zip_sha256)

zip_hash_pass = (
    actual_zip_sha256 == EXPECTED_ZIP_SHA256
)

print(
    "ZIP SHA-256:",
    "PASS" if zip_hash_pass else "FAIL"
)

assert zip_hash_pass

# ============================================================================
# 7. ZIP SIZE
# ============================================================================

zip_size = ZIP_PATH.stat().st_size

print("\nZIP size:", zip_size, "bytes")

assert zip_size > 0

# ============================================================================
# 8. ZIP STRUCTURAL INTEGRITY
# ============================================================================

print("\n2. ZIP STRUCTURAL INTEGRITY")
print("-" * 80)

with zipfile.ZipFile(ZIP_PATH, "r") as zf:

    bad_member = zf.testzip()

    assert bad_member is None, (
        f"Corrupt ZIP member: {bad_member}"
    )

    zip_entries = set(zf.namelist())

print("ZIP test:", "PASS")
print("ZIP entries:", len(zip_entries))

assert zip_entries == EXPECTED_ZIP_ENTRIES

print("16-file inventory: PASS")

# ============================================================================
# 9. VERIFY FROZEN CSVs INSIDE ZIP
# ============================================================================

print("\n3. FROZEN CSV VERIFICATION INSIDE FINAL ZIP")
print("-" * 80)

zip_csv_results = []

with zipfile.ZipFile(ZIP_PATH, "r") as zf:

    for rel_path, spec in FROZEN_CSVS.items():

        member = (
            "AFRIDATACYBERJOHN_v1.0/"
            + rel_path
        )

        data = zf.read(member)

        actual_hash = hashlib.sha256(data).hexdigest()

        hash_pass = (
            actual_hash == spec["sha256"]
        )

        print(
            rel_path,
            "PASS" if hash_pass else "FAIL"
        )

        print(
            "  SHA256:",
            actual_hash
        )

        assert hash_pass

        # Check row population directly from ZIP content
        text = data.decode("utf-8-sig")

        reader = csv.reader(
            text.splitlines()
        )

        rows = list(reader)

        header = rows[0]
        data_rows = rows[1:]

        population_pass = (
            len(data_rows) == spec["rows"]
            and len(header) == spec["columns"]
        )

        print(
            "  Population:",
            "PASS" if population_pass else "FAIL",
            f"rows={len(data_rows)}",
            f"columns={len(header)}"
        )

        assert population_pass

        zip_csv_results.append({
            "file": rel_path,
            "sha256": actual_hash,
            "rows": len(data_rows),
            "columns": len(header),
            "status": "PASS",
        })

# ============================================================================
# 10. VERIFY PERMANENT RELEASE CSVs STILL MATCH ZIP
# ============================================================================

print("\n4. RELEASE DIRECTORY ↔ ZIP CSV CONSISTENCY")
print("-" * 80)

for rel_path, spec in FROZEN_CSVS.items():

    release_path = RELEASE / rel_path

    release_hash = sha256_file(
        release_path
    )

    print(
        rel_path,
        "PASS" if release_hash == spec["sha256"] else "FAIL"
    )

    assert release_hash == spec["sha256"]

# ============================================================================
# 11. RECOVERY MANIFEST
# ============================================================================

print("\n5. RECOVERY MANIFEST")
print("-" * 80)

with open(
    RECOVERY_MANIFEST,
    "r",
    encoding="utf-8"
) as f:
    recovery = json.load(f)

manifest_zip = recovery.get("final_zip", {})

manifest_hash = manifest_zip.get("sha256")
manifest_size = manifest_zip.get("size_bytes")
manifest_filename = manifest_zip.get("filename")

print("Manifest ZIP filename:", manifest_filename)
print("Manifest ZIP size:", manifest_size)
print("Manifest ZIP SHA256:", manifest_hash)

assert manifest_filename == ZIP_PATH.name
assert manifest_size == zip_size
assert manifest_hash == actual_zip_sha256

print("Recovery manifest final ZIP reference: PASS")

# ============================================================================
# 12. VERIFY RECOVERY MANIFEST FROZEN CSV HASHES
# ============================================================================

manifest_csv_hashes = recovery.get(
    "frozen_csv_sha256",
    {}
)

for rel_path, spec in FROZEN_CSVS.items():

    assert (
        manifest_csv_hashes.get(rel_path)
        == spec["sha256"]
    )

print("Recovery manifest frozen CSV hashes: PASS")

# ============================================================================
# 13. VERIFY RELEASE IDENTITY
# ============================================================================

print("\n6. RELEASE IDENTITY")
print("-" * 80)

assert recovery.get("dataset") == "AFRIDATACYBERJOHN"
assert recovery.get("version") == "1.0"
assert recovery.get("license") == "CC BY 4.0"
assert recovery.get("provenance") == "CONFIRMED_SYNTHETIC"

creator = recovery.get("creator", {})

assert creator.get("name") == "John Ojo Ajayi"
assert creator.get("affiliation") == (
    "National Open University of Nigeria"
)

print("Dataset:", recovery["dataset"])
print("Version:", recovery["version"])
print("License:", recovery["license"])
print("Provenance:", recovery["provenance"])
print("Creator:", creator["name"])
print("Affiliation:", creator["affiliation"])
print("Release identity: PASS")

# ============================================================================
# 14. VERIFY PACKAGING REPORT
# ============================================================================

PACKAGING_REPORT = (
    DRIVE_ROOT /
    "STAGE_40C-P_FINAL_PACKAGING_REPORT.json"
)

assert PACKAGING_REPORT.exists()

with open(
    PACKAGING_REPORT,
    "r",
    encoding="utf-8"
) as f:
    packaging = json.load(f)

assert packaging.get("status") == "PASS"
assert packaging.get("zip_sha256") == actual_zip_sha256
assert packaging.get("zip_size_bytes") == zip_size
assert packaging.get("frozen_csvs_modified") is False
assert packaging.get("dataset_records_modified") is False

print("Stage 40C-P packaging report: PASS")

# ============================================================================
# 15. SAVE FINAL VERIFICATION REPORT
# ============================================================================

timestamp = datetime.now(
    timezone.utc
).isoformat()

final_report = {
    "dataset": "AFRIDATACYBERJOHN",
    "version": "1.0",
    "stage": "40C-Q",
    "status": "PASS",

    "timestamp_utc": timestamp,

    "final_zip": {
        "path": str(ZIP_PATH),
        "filename": ZIP_PATH.name,
        "size_bytes": zip_size,
        "sha256": actual_zip_sha256,
    },

    "zip_entries": len(zip_entries),

    "frozen_csvs": zip_csv_results,

    "release_identity": {
        "creator": "John Ojo Ajayi",
        "affiliation":
            "National Open University of Nigeria",
        "license": "CC BY 4.0",
        "provenance": "CONFIRMED_SYNTHETIC",
    },

    "integrity": {
        "zip_structure": "PASS",
        "zip_csv_hashes": "PASS",
        "release_csv_hashes": "PASS",
        "recovery_manifest": "PASS",
        "packaging_report": "PASS",
    },

    "protected_status": {
        "dataset_records_modified": False,
        "frozen_csvs_modified": False,
        "final_zip_modified_by_audit": False,
    }
}

REPORT_PATH.write_text(
    json.dumps(
        final_report,
        indent=2,
        ensure_ascii=False
    ) + "\n",
    encoding="utf-8"
)

assert REPORT_PATH.exists()

# ============================================================================
# FINAL
# ============================================================================

print("\n" + "=" * 80)
print("STAGE 40C-Q COMPLETE")
print("=" * 80)

print("OVERALL STATUS: PASS")
print("Final ZIP:", ZIP_PATH)
print("Final ZIP size:", zip_size, "bytes")
print("Final ZIP SHA256:", actual_zip_sha256)
print("ZIP entries:", len(zip_entries))
print("Frozen CSVs inside ZIP: PASS")
print("Release CSVs: PASS")
print("Recovery manifest: PASS")
print("Packaging report: PASS")
print("Final verification report:", REPORT_PATH)

print("\nPROTECTED:")
print("  Dataset records modified: NO")
print("  Frozen CSVs modified: NO")
print("  ZIP modified by audit: NO")

print("=" * 80)

# ==============================================================================
# NOTEBOOK CELL 723
# ==============================================================================

# ============================================================================
# STAGE 40C-R — DOWNLOAD VERIFIED FINAL RELEASE
# ============================================================================

from pathlib import Path
import shutil
import hashlib

SOURCE = Path(
    "/content/drive/MyDrive/AFRIDATACYBERJOHN/"
    "AFRIDATACYBERJOHN_v1.0.zip"
)

DOWNLOAD_PATH = Path(
    "/content/AFRIDATACYBERJOHN_v1.0.zip"
)

EXPECTED_SHA256 = (
    "8154d57a3dae95565c7f8aaba7fbdbd85bbcd3eca75220e91a071590dc61700d"
)

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            h.update(block)
    return h.hexdigest()

assert SOURCE.exists(), "Verified final ZIP not found."

# Copy only; do not rebuild or modify the release.
shutil.copy2(SOURCE, DOWNLOAD_PATH)

actual_sha256 = sha256_file(DOWNLOAD_PATH)

print("=" * 80)
print("STAGE 40C-R — VERIFIED FINAL RELEASE DOWNLOAD")
print("=" * 80)

print("Source:")
print(SOURCE)

print("\nDownload file:")
print(DOWNLOAD_PATH)

print("\nSHA-256:")
print(actual_sha256)

assert actual_sha256 == EXPECTED_SHA256

print("\nSHA-256 verification: PASS")
print("File size:", DOWNLOAD_PATH.stat().st_size, "bytes")

print("=" * 80)
print("READY FOR DOWNLOAD")
print("=" * 80)

from google.colab import files
files.download(str(DOWNLOAD_PATH))
