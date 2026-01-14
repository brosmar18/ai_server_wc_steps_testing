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

def build_step_8c_result() -> dict:
    return {
        "step": "Step 8c: Combine into Final Import Params",
        "step_number": "8c",
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "errors": [],
    }


# -------------------------------------------------------------------
# Load & Validate Step 8b
# -------------------------------------------------------------------

def load_step_8b_results(step_8b_file: Path) -> dict:
    print("\nLoading Step 8b results...")
    print(f"Step 8b results path: {step_8b_file}")

    if not step_8b_file.exists():
        raise FileNotFoundError(f"Step 8b results not found: {step_8b_file}")

    with open(step_8b_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Step 8b results loaded successfully.")
    return data


def validate_step_8b_success(step8b_data: dict, result: dict) -> None:
    print("\nValidating Step 8b success status...")

    if not step8b_data.get("success"):
        error = "Step 8b did not complete successfully"
        result["errors"].append(error)
        print(f"Validation failed: {error}")
        return

    print("Step 8b completed successfully.")


# -------------------------------------------------------------------
# Integration (Phase 1: carry forward only)
# -------------------------------------------------------------------

def integrate_step_8b_data(step8b_data: dict, result: dict) -> None:
    """
    Carry forward all required data unchanged.
    NO combination logic yet.
    """
    result["data"] = {
        "object_name": step8b_data["data"]["object_name"],
        "file_name": step8b_data["data"]["file_name"],
        "file_path": step8b_data["data"]["file_path"],
        "columns": step8b_data["data"].get("columns"),
        "all_mappings_dict": step8b_data["data"].get("all_mappings_dict"),
        "ref_obj_ai_mappings": step8b_data["data"].get("ref_obj_ai_mappings"),
        "field_overrides": step8b_data["data"]["field_overrides"],
        "import_metadata": step8b_data["data"]["import_metadata"],
    }


# -------------------------------------------------------------------
# Finalization
# -------------------------------------------------------------------

def finalize_step_8c_success(result: dict) -> None:
    result["success"] = len(result["errors"]) == 0


def save_result_to_json(result: dict, output_file: Path) -> None:
    print("\nSaving Step 8c results...")

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
    print("TESTING STEP 8c: COMBINE INTO FINAL IMPORT PARAMS")
    print("PHASE 1: LOAD & VALIDATE STEP 8b")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_8b_results = project_root / "test_results" / "step_8b_import_metadata.json"
    output_file = project_root / "test_results" / "step_8c_import_params.json"

    result = build_step_8c_result()

    try:
        step8b_data = load_step_8b_results(step_8b_results)
        validate_step_8b_success(step8b_data, result)

        if not result["errors"]:
            integrate_step_8b_data(step8b_data, result)

    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Unexpected error: {exc}")

    finalize_step_8c_success(result)
    save_result_to_json(result, output_file)

    print("\nFinal Step 8c result (Phase 1):")
    print(f"  Success: {result['success']}")
    print(f"  Field overrides: {len(result['data'].get('field_overrides', []))}")
    print(f"  Metadata keys: {list(result['data'].get('import_metadata', {}).keys())}")
    print(f"  Errors: {result['errors']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
