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
    """
    Build the base result object for Step 5d.
    """
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
# Integration (no separation yet)
# -------------------------------------------------------------------

def integrate_step_5c_data(step5c_data: dict, result: dict) -> None:
    """
    Carry forward Step 5c data unchanged.
    """
    result["data"] = dict(step5c_data["data"])

    # Placeholders for separation (future phases)
    result["data"]["final_mappings"] = []
    result["data"]["reference_mappings"] = []
    result["data"]["final_mappings_count"] = 0
    result["data"]["reference_mappings_count"] = 0


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
    print("PHASE 1: LOAD + VALIDATE STEP 5c")
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

        result["success"] = len(result["errors"]) == 0
        save_results(result, output_file)

    except Exception as exc:
        result["errors"].append(str(exc))
        result["success"] = False
        save_results(result, output_file)
        print(f"Unexpected error: {exc}")

    print("\nFinal Step 5d result (Phase 1):")
    print(f"  Success: {result['success']}")
    print(f"  Total AI Mappings: {result['data'].get('total_mappings')}")
    print(f"  Errors: {result['errors']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
