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

def build_step_7_result() -> dict:
    return {
        "step": "Step 7: Build Final Mappings Dictionary",
        "step_number": "7",
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "errors": [],
    }

# -------------------------------------------------------------------
# Load & Validate Step 6b
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
# Phase 3: Build Unified Mappings
# -------------------------------------------------------------------

def build_final_mappings_dict(
    final_mappings: list,
    ref_obj_ai_mappings: dict,
) -> dict:
    """
    Combine non-reference and reference mappings into one dictionary.
    Matches import_builder.py logic exactly.
    """
    all_mappings = {}

    # Non-reference mappings
    for m in final_mappings:
        all_mappings[m["column"]] = {
            "column": m["column"],
            "fieldName": m["fieldName"],
            "fieldType": m["fieldType"],
        }

    # Reference mappings
    for column, ref in ref_obj_ai_mappings.items():
        all_mappings[column] = {
            "column": column,
            "fieldName": ref["parent_field_name"],
            "fieldType": "reference",
            "refObjectName": ref["ref_object_name"],
            "lookupFieldName": ref["field_name"],
        }

    return all_mappings

# -------------------------------------------------------------------
# Finalization
# -------------------------------------------------------------------

def finalize_success(result: dict) -> None:
    result["success"] = len(result["errors"]) == 0


def save_result(result: dict, output_file: Path) -> None:
    print("\nSaving Step 7 results...")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Saved: {output_file}")

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main() -> int:
    print("=" * 80)
    print("TESTING STEP 7: BUILD FINAL MAPPINGS DICTIONARY")
    print("PHASE 3: BUILD UNIFIED MAPPINGS")
    print("=" * 80)

    root = Path(__file__).parent.parent
    step6b_file = root / "test_results" / "step_6b_reference_mappings.json"
    output_file = root / "test_results" / "step_7_final_mappings.json"

    result = build_step_7_result()

    try:
        # ------------------------------------------------------------
        # Load Step 6b ONLY (linear pipeline)
        # ------------------------------------------------------------
        step6b = load_json(step6b_file)
        validate_success(step6b, "Step 6b", result)

        if not result["errors"]:
            # --------------------------------------------------------
            # Carry forward ALL prior data
            # --------------------------------------------------------
            result["data"] = dict(step6b["data"])

            final_mappings = result["data"]["final_mappings"]
            ref_obj_ai_mappings = result["data"]["ref_obj_ai_mappings"]

            # --------------------------------------------------------
            # Build unified mappings dictionary
            # --------------------------------------------------------
            all_mappings = build_final_mappings_dict(
                final_mappings=final_mappings,
                ref_obj_ai_mappings=ref_obj_ai_mappings,
            )

            # --------------------------------------------------------
            # Add Step 7 outputs
            # --------------------------------------------------------
            result["data"]["all_mappings_dict"] = all_mappings
            result["data"]["total_mappings_count"] = len(all_mappings)
            result["data"]["non_reference_count"] = len(final_mappings)
            result["data"]["reference_count"] = len(ref_obj_ai_mappings)

    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Unexpected error: {exc}")

    finalize_success(result)
    save_result(result, output_file)

    print("\nFinal Step 7 result:")
    print(f"  Success: {result['success']}")
    print(f"  Total mappings: {result['data'].get('total_mappings_count')}")
    print(f"  Errors: {result['errors']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
