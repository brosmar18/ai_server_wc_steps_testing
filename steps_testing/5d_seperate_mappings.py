import sys
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List


# -------------------------------------------------------------------
# Ensure project root is on PYTHONPATH
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# -------------------------------------------------------------------
# Result Builder
# -------------------------------------------------------------------

def build_step_5d_result() -> dict:
    return {
        "step": "Step 5d: Separate Mappings",
        "step_number": "5d",
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "errors": [],
    }


# -------------------------------------------------------------------
# Load & Validate Step 5c
# -------------------------------------------------------------------

def load_step_5c_results(step_5c_file: Path) -> dict:
    print("\nLoading Step 5c results...")
    print(f"Step 5c results path: {step_5c_file}")

    if not step_5c_file.exists():
        raise FileNotFoundError(f"Step 5c results not found: {step_5c_file}")

    with open(step_5c_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Step 5c results loaded successfully.")
    return data


def validate_step_5c_success(step5c_data: dict, result: dict) -> None:
    print("\nValidating Step 5c success status...")

    if not step5c_data.get("success"):
        error = "Step 5c did not complete successfully"
        result["errors"].append(error)
        print(f"Validation failed: {error}")
        return

    print("Step 5c completed successfully.")


# -------------------------------------------------------------------
# Mapping Builders
# -------------------------------------------------------------------

def build_final_mappings(ai_mappings: List[Dict]) -> List[Dict]:
    results: List[Dict] = []

    for mapping in ai_mappings:
        if mapping.get("fieldType") != "reference":
            results.append({
                "column": mapping["column"],
                "fieldName": mapping["fieldName"],
                "fieldType": mapping["fieldType"],
            })

    return results


def build_reference_mappings(ai_mappings: List[Dict]) -> List[Dict]:
    results: List[Dict] = []

    for mapping in ai_mappings:
        if (
            mapping.get("fieldType") == "reference"
            and mapping.get("refObjectName")
        ):
            results.append({
                "column": mapping["column"],
                "parent_field_name": mapping["fieldName"],
                "field_type": mapping["fieldType"],
                "ref_obj_name": mapping["refObjectName"],
            })

    return results


# -------------------------------------------------------------------
# Validation (NEW — Phase 4)
# -------------------------------------------------------------------

def validate_step_5d_result(result: dict) -> None:
    """
    Enforce correctness rules for Step 5d.
    """
    data = result["data"]

    final_count = data.get("final_mappings_count", 0)
    ref_count = data.get("reference_mappings_count", 0)
    total = data.get("total_mappings", 0)

    if final_count <= 0:
        result["errors"].append("No final (non-reference) mappings produced")

    if final_count + ref_count != total:
        result["errors"].append(
            f"Mapping count mismatch: final({final_count}) + reference({ref_count}) != total({total})"
        )


# -------------------------------------------------------------------
# Integration
# -------------------------------------------------------------------

def integrate_step_5c_data(step5c_data: dict, result: dict) -> None:
    result["data"] = dict(step5c_data["data"])

    ai_mappings = step5c_data["data"]["ai_mappings"]

    final_mappings = build_final_mappings(ai_mappings)
    reference_mappings = build_reference_mappings(ai_mappings)

    result["data"]["final_mappings"] = final_mappings
    result["data"]["final_mappings_count"] = len(final_mappings)

    result["data"]["reference_mappings"] = reference_mappings
    result["data"]["reference_mappings_count"] = len(reference_mappings)


# -------------------------------------------------------------------
# Persistence
# -------------------------------------------------------------------

def save_results(result: dict, output_file: Path) -> None:
    print("\nSaving Step 5d results...")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Results saved to: {output_file}")
    print(f"File size: {output_file.stat().st_size} bytes")


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main() -> int:
    print("=" * 80)
    print("TESTING STEP 5d: SEPARATE MAPPINGS")
    print("PHASE 4: RESULT VALIDATION")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_5c_results = project_root / "test_results" / "step_5c_agent_execution.json"
    output_file = project_root / "test_results" / "step_5d_mappings_separated.json"

    result = build_step_5d_result()

    try:
        step5c_data = load_step_5c_results(step_5c_results)
        validate_step_5c_success(step5c_data, result)

        if not result["errors"]:
            integrate_step_5c_data(step5c_data, result)
            validate_step_5d_result(result)

        result["success"] = len(result["errors"]) == 0
        save_results(result, output_file)

    except Exception as exc:
        result["errors"].append(str(exc))
        result["success"] = False
        save_results(result, output_file)
        print(f"Unexpected error: {exc}")

    print("\nFinal Step 5d result (Phase 4):")
    print(f"  Success: {result['success']}")
    print(f"  Final Mappings: {result['data'].get('final_mappings_count')}")
    print(f"  Reference Mappings: {result['data'].get('reference_mappings_count')}")
    print(f"  Errors: {result['errors']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
