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

def build_step_5b_result() -> dict:
    """
    Build the base result object for Step 5b.
    """
    return {
        "step": "Step 5b: Build Prompt for AI Agent",
        "step_number": "5b",
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "errors": [],
    }


# -------------------------------------------------------------------
# Load & Validate Step 5a
# -------------------------------------------------------------------

def load_step_5a_results(step_5a_file: Path) -> dict:
    print("\nLoading Step 5a results...")
    print(f"Step 5a results path: {step_5a_file}")

    if not step_5a_file.exists():
        raise FileNotFoundError(f"Step 5a results not found: {step_5a_file}")

    with open(step_5a_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Step 5a results loaded successfully.")
    return data


def validate_step_5a_success(step5a_data: dict, result: dict) -> None:
    print("\nValidating Step 5a success status...")

    if not step5a_data.get("success"):
        error = "Step 5a did not complete successfully"
        result["errors"].append(error)
        print(f"Validation failed: {error}")
        return

    print("Step 5a completed successfully.")


# -------------------------------------------------------------------
# Phase 3: Prompt Construction
# -------------------------------------------------------------------

def build_ai_prompt(columns, formatted_fields) -> str:
    """
    Build the AI mapping prompt using shared logic.
    """
    from app.services.mapping.ai_agent import build_prompt

    print("\nBuilding prompt for AI agent...")
    prompt = build_prompt(columns, formatted_fields)
    print("Prompt built successfully.")

    return prompt

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main() -> int:
    print("=" * 80)
    print("TESTING STEP 5b: BUILD PROMPT FOR AI AGENT")
    print("PHASE 1: RESULT CONTRACT + STEP 5a LOAD")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_5a_results = project_root / "test_results" / "step_5a_ai_agent.json"

    result = build_step_5b_result()

    try:
        step5a_data = load_step_5a_results(step_5a_results)
        validate_step_5a_success(step5a_data, result)

        if not result["errors"]:
            print("\nExtracting required data from Step 5a...")

            result["data"] = {
                "object_name": step5a_data["data"]["object_name"],
                "file_name": step5a_data["data"]["file_name"],
                "file_path": step5a_data["data"]["file_path"],
                "columns": step5a_data["data"]["columns"],
                "formatted_fields": step5a_data["data"]["formatted_fields"],
            }

            print("Data extraction complete.")
            print(f"  Columns: {len(result['data']['columns'])}")
            print(f"  Formatted fields: {len(result['data']['formatted_fields'])}")

    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Error: {exc}")

    print("\nCurrent Step 5b result state:")
    print(f"  Data keys: {list(result['data'].keys())}")
    print(f"  Errors: {result['errors']}")
    print(f"  Success: {result['success']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
