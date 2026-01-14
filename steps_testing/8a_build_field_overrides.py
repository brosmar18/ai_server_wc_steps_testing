import sys
from pathlib import Path
from datetime import datetime
import json

# -------------------------------------------------------------------
# Ensure project root is on PYTHONPATH
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# -------------------------------------------------------------------
# Result Builder
# -------------------------------------------------------------------

def build_step_8a_result() -> dict:
    return {
        "step": "Step 8a: Build Field Overrides",
        "step_number": "8a",
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "errors": [],
    }

# -------------------------------------------------------------------
# Load Helpers
# -------------------------------------------------------------------

def load_json(path: Path) -> dict:
    print(f"\nLoading results: {path}")
    if not path.exists():
        raise FileNotFoundError(path)

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_success(step_data: dict, step_name: str, result: dict) -> None:
    print(f"Validating {step_name} success status...")
    if not step_data.get("success"):
        error = f"{step_name} did not complete successfully"
        result["errors"].append(error)
        print(f"Validation failed: {error}")
        return
    print(f"{step_name} completed successfully.")

# -------------------------------------------------------------------
# Core Logic (STRICT & SAFE)
# -------------------------------------------------------------------

def build_field_overrides(columns: list, mappings: dict, ref_obj_ai_mappings: dict) -> list:
    """
    Build fieldOverrides array for import params.
    Matches app/services/import_config/params_builder.py logic exactly.

    CDATA expects fieldOverrides to be an array where each element represents
    a CSV column and its mapping configuration.

    Args:
        columns: List of CSV column names in order
        mappings: Dictionary of all mappings (parent + reference)
        ref_obj_ai_mappings: Reference object lookup field mappings

    Returns:
        List of field override objects (one per column)
    """
    field_overrides = []

    for col_index, column_name in enumerate(columns):
        # Get the mapping for this column
        if column_name not in mappings:
            print(f"WARNING: No mapping found for column '{column_name}', skipping")
            continue

        mapping = mappings[column_name]

        # Check if this is a reference field
        if mapping.get("fieldType") == "reference" and column_name in ref_obj_ai_mappings:
            # REFERENCE FIELD - Get lookup info from ref_obj_ai_mappings
            ref_mapping = ref_obj_ai_mappings[column_name]
            override = {
                "col": col_index,
                "fieldName": mapping["fieldName"],
                "lookupRefObject": ref_mapping["ref_object_name"],
                "lookupFieldName": ref_mapping["field_name"],
                "createOnMissing": True  # Always true for reference fields
            }
        else:
            # SIMPLE FIELD - No createOnMissing at all
            override = {
                "col": col_index,
                "fieldName": mapping["fieldName"]
            }

        field_overrides.append(override)

    return field_overrides

# -------------------------------------------------------------------
# Finalization
# -------------------------------------------------------------------

def finalize_success(result: dict) -> None:
    result["success"] = len(result["errors"]) == 0


def save_result(result: dict, output_file: Path) -> None:
    print("\nSaving Step 8a results...")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Saved: {output_file}")

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main() -> int:
    print("=" * 80)
    print("TESTING STEP 8a: BUILD FIELD OVERRIDES")
    print("PHASE 3: FIELD OVERRIDE CONSTRUCTION")
    print("=" * 80)

    root = Path(__file__).parent.parent
    step7_file = root / "test_results" / "step_7_final_mappings.json"
    output_file = root / "test_results" / "step_8a_field_overrides.json"

    result = build_step_8a_result()

    try:
        # ------------------------------------------------------------
        # Load Step 7 ONLY (linear pipeline)
        # ------------------------------------------------------------
        step7 = load_json(step7_file)
        validate_success(step7, "Step 7", result)

        if not result["errors"]:
            # Carry forward all prior data
            result["data"] = dict(step7["data"])

            columns = result["data"]["columns"]
            mappings = result["data"]["all_mappings_dict"]
            ref_obj_ai_mappings = result["data"]["ref_obj_ai_mappings"]

            field_overrides = build_field_overrides(columns, mappings, ref_obj_ai_mappings)

            # Safety check: field_overrides should match or be less than columns
            # (less if some columns were skipped due to no mapping)
            if len(field_overrides) > len(columns):
                raise ValueError(
                    f"Field override count ERROR: "
                    f"{len(field_overrides)} overrides for {len(columns)} columns"
                )

            ref_count = sum(1 for fo in field_overrides if "lookupRefObject" in fo)
            simple_count = len(field_overrides) - ref_count

            result["data"].update({
                "field_overrides": field_overrides,
                "field_overrides_count": len(field_overrides),
                "simple_fields_count": simple_count,
                "reference_fields_count": ref_count,
            })

    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Unexpected error: {exc}")

    finalize_success(result)
    save_result(result, output_file)

    print("\nFinal Step 8a result:")
    print(f"  Success: {result['success']}")
    print(f"  Field overrides: {result['data'].get('field_overrides_count')}")
    print(f"  Errors: {result['errors']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
