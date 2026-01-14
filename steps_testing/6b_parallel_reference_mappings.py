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

def build_step_6b_result() -> dict:
    """
    Build the base result object for Step 6b.
    """
    return {
        "step": "Step 6b: Run Parallel Reference Mappings",
        "step_number": "6b",
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "errors": [],
    }


# -------------------------------------------------------------------
# Load & Validate Step 6a
# -------------------------------------------------------------------

def load_step_6a_results(step_6a_file: Path) -> dict:
    print("\nLoading Step 6a results...")
    print(f"Step 6a results path: {step_6a_file}")

    if not step_6a_file.exists():
        raise FileNotFoundError(f"Step 6a results not found: {step_6a_file}")

    with open(step_6a_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Step 6a results loaded successfully.")
    return data


def validate_step_6a_success(step6a_data: dict, result: dict) -> None:
    print("\nValidating Step 6a success status...")

    if not step6a_data.get("success"):
        error = "Step 6a did not complete successfully"
        result["errors"].append(error)
        print(f"Validation failed: {error}")
        return

    print("Step 6a completed successfully.")


# -------------------------------------------------------------------
# Integration (carry forward data only)
# -------------------------------------------------------------------

def integrate_step_6a_data(step6a_data: dict, result: dict) -> None:
    """
    Carry forward Step 6a data unchanged.
    """
    result["data"] = {
        "object_name": step6a_data["data"]["object_name"],
        "file_name": step6a_data["data"]["file_name"],
        "file_path": step6a_data["data"]["file_path"],
        "columns": step6a_data["data"]["columns"],
        "final_mappings": step6a_data["data"]["final_mappings"],
        "reference_mappings": step6a_data["data"]["reference_mappings"],
        "ref_schemas": step6a_data["data"]["ref_schemas"],
        "unique_ref_objects": step6a_data["data"]["unique_ref_objects"],

        # Placeholders for later phases
        "ref_obj_ai_mappings": {},
        "ref_mappings_count": 0,
    }


# -------------------------------------------------------------------
# Finalization
# -------------------------------------------------------------------

def finalize_step_6b_success(result: dict) -> None:
    result["success"] = len(result["errors"]) == 0


def save_result_to_json(result: dict, output_file: Path) -> None:
    print("\nSaving Step 6b results to JSON...")

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
    print("TESTING STEP 6b: RUN PARALLEL REFERENCE MAPPINGS")
    print("PHASE 1: LOAD & VALIDATE STEP 6a")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_6a_results = project_root / "test_results" / "step_6a_reference_schemas.json"
    output_file = project_root / "test_results" / "step_6b_reference_mappings.json"

    result = build_step_6b_result()

    try:
        step6a_data = load_step_6a_results(step_6a_results)
        validate_step_6a_success(step6a_data, result)

        if not result["errors"]:
            integrate_step_6a_data(step6a_data, result)

    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Unexpected error: {exc}")

    finalize_step_6b_success(result)
    save_result_to_json(result, output_file)

    print("\nFinal Step 6b result (Phase 1):")
    print(f"  Success: {result['success']}")
    print(f"  Reference mappings found: {len(result['data'].get('reference_mappings', []))}")
    print(f"  Errors: {result['errors']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
