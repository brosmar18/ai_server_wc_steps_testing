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
    """
    Build the base result object for Step 7.
    """
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

def load_step_6b_results(step_6b_file: Path) -> dict:
    print("\nLoading Step 6b results...")
    print(f"Step 6b results path: {step_6b_file}")

    if not step_6b_file.exists():
        raise FileNotFoundError(f"Step 6b results not found: {step_6b_file}")

    with open(step_6b_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Step 6b results loaded successfully.")
    return data


def validate_step_6b_success(step6b_data: dict, result: dict) -> None:
    print("\nValidating Step 6b success status...")

    if not step6b_data.get("success"):
        error = "Step 6b did not complete successfully"
        result["errors"].append(error)
        print(f"Validation failed: {error}")
        return

    print("Step 6b completed successfully.")


# -------------------------------------------------------------------
# Integration (Phase 1 only)
# -------------------------------------------------------------------

def integrate_step_6b_data(step6b_data: dict, result: dict) -> None:
    """
    Carry forward Step 6b data required for Step 7.
    """
    result["data"] = {
        "object_name": step6b_data["data"]["object_name"],
        "file_name": step6b_data["data"]["file_name"],
        "file_path": step6b_data["data"]["file_path"],
        "reference_mappings": step6b_data["data"]["reference_mappings"],
        "ref_obj_ai_mappings": step6b_data["data"]["ref_obj_ai_mappings"],
    }


# -------------------------------------------------------------------
# Finalization
# -------------------------------------------------------------------

def finalize_step_7_success(result: dict) -> None:
    result["success"] = len(result["errors"]) == 0


def save_result_to_json(result: dict, output_file: Path) -> None:
    print("\nSaving Step 7 results to JSON...")

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
    print("TESTING STEP 7: BUILD FINAL MAPPINGS DICTIONARY")
    print("PHASE 1: LOAD & VALIDATE STEP 6b")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_6b_results = project_root / "test_results" / "step_6b_reference_mappings.json"
    output_file = project_root / "test_results" / "step_7_final_mappings.json"

    result = build_step_7_result()

    try:
        step6b_data = load_step_6b_results(step_6b_results)
        validate_step_6b_success(step6b_data, result)

        if not result["errors"]:
            integrate_step_6b_data(step6b_data, result)

    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Unexpected error: {exc}")

    finalize_step_7_success(result)
    save_result_to_json(result, output_file)

    print("\nFinal Step 7 result (Phase 1):")
    print(f"  Success: {result['success']}")
    print(f"  Reference mappings: {len(result['data'].get('reference_mappings', []))}")
    print(f"  Errors: {result['errors']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
