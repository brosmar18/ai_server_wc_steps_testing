import sys
from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict, Any



def build_step_4_result() -> dict:
    """
    Build the base result object for Step 4.

    This locks the Step 4 output contract.
    """
    return {
        "step": "Step 4: Format CDATA Fields",
        "step_number": 4,
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "errors": [],
    }


def load_step_3_results(step_3_file: Path) -> dict:
    print("\nLoading Step 3 results...")
    print(f"Step 3 results path: {step_3_file}")

    if not step_3_file.exists():
        raise FileNotFoundError(f"Step 3 results not found: {step_3_file}")

    with open(step_3_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Step 3 results loaded successfully.")
    return data

def validate_step_3_success(step3_data: dict, result: dict) -> None:
    print("\nValidating Step 3 success status...")

    if not step3_data.get("success"):
        error = "Step 3 did not complete successfully"
        result["errors"].append(error)
        print(f"Validation failed: {error}")
        return

    print("Step 3 completed successfully.")



def format_fields(raw_fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    formatted = []

    for raw in raw_fields:
        field_name = raw.get("fieldName")
        if not field_name:
            continue

        field_type = str(raw.get("fieldType", "")).lower()
        label = raw.get("label", field_name)

        formatted_field = {
            "field_name": field_name,
            "label": label,
            "field_type": field_type,
        }

        if field_type == "reference":
            options = raw.get("options", {})
            ref_objects = options.get("refObjects")

            if ref_objects and isinstance(ref_objects, list):
                formatted_field["ref_object_name"] = ref_objects[0].get("name")
            else:
                formatted_field["ref_object_name"] = "UNKNOWN_REFERENCE"

        formatted.append(formatted_field)

    return formatted



def integrate_step_4_data(
    step3_data: dict,
    formatted_fields: List[Dict[str, Any]],
    result: dict,
) -> None:
    
    result["data"] = {
        "object_name": step3_data["data"]["object_name"],
        "file_name": step3_data["data"]["file_name"],
        "file_path": step3_data["data"]["file_path"],
        "columns": step3_data["data"]["columns"],
        "raw_fields": step3_data["data"]["raw_fields"],
        "formatted_fields": formatted_fields,
    }

    print("\nIntegrated Step 4 data:")
    print(f"  Object Name: {result['data']['object_name']}")
    print(f"  File Name: {result['data']['file_name']}")
    print(f"  Formatted Fields: {len(formatted_fields)}")

def finalize_step_success(result: dict) -> None:
    formatted_fields = result["data"].get("formatted_fields", [])
    result["success"] = not result["errors"] and len(formatted_fields) > 0


def save_result_to_json(result: dict, output_file: Path) -> None:
    print("\nSaving Step 4 results...")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Result saved to: {output_file}")
    print(f"File size: {output_file.stat().st_size} bytes")



def main() -> int:
    print("=" * 80)
    print("TESTING STEP 4: FORMAT CDATA FIELDS")
    print("PHASE 8: FINALIZATION")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_3_results = project_root / "test_results" / "step_3_cdata_schema.json"
    output_file = project_root / "test_results" / "step_4_formatted_fields.json"

    result = build_step_4_result()

    try:
        step3_data = load_step_3_results(step_3_results)
        validate_step_3_success(step3_data, result)

        if not result["errors"]:
            raw_fields = step3_data["data"]["raw_fields"]
            formatted_fields = format_fields(raw_fields)
            integrate_step_4_data(step3_data, formatted_fields, result)

    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Error: {exc}")

    finalize_step_success(result)
    save_result_to_json(result, output_file)

    print("\nFinal Step 4 result:")
    print(f"  Success: {result['success']}")
    print(f"  Errors: {result['errors']}")
    print(f"  Formatted Fields: {len(result['data'].get('formatted_fields', []))}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())