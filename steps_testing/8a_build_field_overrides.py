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
# Core Logic
# -------------------------------------------------------------------

def build_field_overrides(columns: list, mappings: dict) -> list:
    """
    Inline version of params_builder.build_field_overrides
    """
    field_overrides = []

    for col_index, column_name in enumerate(columns):
        if column_name not in mappings:
            raise KeyError(f"No mapping found for column '{column_name}'")

        mapping = mappings[column_name]

        # Simple field
        if mapping["fieldType"] != "reference":
            field_overrides.append({
                "col": col_index,
                "fieldName": mapping["fieldName"],
            })

        # Reference field
        else:
            field_overrides.append({
                "col": col_index,
                "fieldName": mapping["fieldName"],
                "lookupRefObject": mapping["refObjectName"],
                "lookupFieldName": mapping["lookupFieldName"],
                "createOnMissing": True,
            })

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
    step5d_file = root / "test_results" / "step_5d_mappings_separated.json"
    output_file = root / "test_results" / "step_8a_field_overrides.json"

    result = build_step_8a_result()

    try:
        step7 = load_json(step7_file)
        step5d = load_json(step5d_file)

        validate_success(step7, "Step 7", result)
        validate_success(step5d, "Step 5d", result)

        if not result["errors"]:
            columns = step5d["data"]["columns"]
            mappings = step7["data"]["all_mappings_dict"]

            field_overrides = build_field_overrides(columns, mappings)

            ref_count = sum(1 for fo in field_overrides if "lookupRefObject" in fo)
            simple_count = len(field_overrides) - ref_count

            result["data"] = {
                "object_name": step7["data"]["object_name"],
                "file_name": step7["data"]["file_name"],
                "file_path": step7["data"]["file_path"],
                "columns": columns,
                "all_mappings_dict": mappings,
                "field_overrides": field_overrides,
                "field_overrides_count": len(field_overrides),
                "simple_fields_count": simple_count,
                "reference_fields_count": ref_count,
            }

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
