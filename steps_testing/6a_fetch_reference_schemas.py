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

def build_step_6a_result() -> dict:
    """
    Build the base result object for Step 6a.
    """
    return {
        "step": "Step 6a: Fetch Reference Object Schemas",
        "step_number": "6a",
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "errors": [],
    }


# -------------------------------------------------------------------
# Load & Validate Step 5d
# -------------------------------------------------------------------

def load_step_5d_results(step_5d_file: Path) -> dict:
    print("\nLoading Step 5d results...")
    print(f"Step 5d results path: {step_5d_file}")

    if not step_5d_file.exists():
        raise FileNotFoundError(f"Step 5d results not found: {step_5d_file}")

    with open(step_5d_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Step 5d results loaded successfully.")
    return data


def validate_step_5d_success(step5d_data: dict, result: dict) -> None:
    print("\nValidating Step 5d success status...")

    if not step5d_data.get("success"):
        error = "Step 5d did not complete successfully"
        result["errors"].append(error)
        print(f"Validation failed: {error}")
        return

    print("Step 5d completed successfully.")


# -------------------------------------------------------------------
# Integration (Phase 1)
# -------------------------------------------------------------------

def integrate_step_5d_data(step5d_data: dict, result: dict) -> None:
    """
    Carry forward Step 5d data unchanged.
    """
    result["data"] = {
        "object_name": step5d_data["data"]["object_name"],
        "file_name": step5d_data["data"]["file_name"],
        "file_path": step5d_data["data"]["file_path"],
        "columns": step5d_data["data"]["columns"],
        "final_mappings": step5d_data["data"]["final_mappings"],
        "reference_mappings": step5d_data["data"]["reference_mappings"],
    }


# -------------------------------------------------------------------
# Finalization
# -------------------------------------------------------------------

def finalize_step_6a_success(result: dict) -> None:
    result["success"] = len(result["errors"]) == 0


def save_results(result: dict, output_file: Path) -> None:
    print("\nSaving Step 6a results (Phase 1)...")

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
    print("TESTING STEP 6a: FETCH REFERENCE OBJECT SCHEMAS")
    print("PHASE 1: LOAD & VALIDATE INPUT")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_5d_results = project_root / "test_results" / "step_5d_mappings_separated.json"
    output_file = project_root / "test_results" / "step_6a_reference_schemas.json"

    result = build_step_6a_result()

    try:
        step5d_data = load_step_5d_results(step_5d_results)
        validate_step_5d_success(step5d_data, result)

        if not result["errors"]:
            integrate_step_5d_data(step5d_data, result)

    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Unexpected error: {exc}")

    finalize_step_6a_success(result)
    save_results(result, output_file)

    print("\nFinal Step 6a result (Phase 1):")
    print(f"  Success: {result['success']}")
    print(f"  Reference Mappings: {len(result['data'].get('reference_mappings', []))}")
    print(f"  Errors: {result['errors']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
