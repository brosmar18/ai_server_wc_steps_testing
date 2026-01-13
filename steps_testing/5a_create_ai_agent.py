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

def build_step_5a_result() -> dict:
    """
    Build the base result object for Step 5a.
    """
    return {
        "step": "Step 5a: Create AI Mapping Agent",
        "step_number": "5a",
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "errors": [],
    }


# -------------------------------------------------------------------
# Load & Validate Step 4
# -------------------------------------------------------------------

def load_step_4_results(step_4_file: Path) -> dict:
    print("\nLoading Step 4 results...")
    print(f"Step 4 results path: {step_4_file}")

    if not step_4_file.exists():
        raise FileNotFoundError(f"Step 4 results not found: {step_4_file}")

    with open(step_4_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Step 4 results loaded successfully.")
    return data


def validate_step_4_success(step4_data: dict, result: dict) -> None:
    print("\nValidating Step 4 success status...")

    if not step4_data.get("success"):
        error = "Step 4 did not complete successfully"
        result["errors"].append(error)
        print(f"Validation failed: {error}")
        return

    print("Step 4 completed successfully.")


# -------------------------------------------------------------------
# Integration
# -------------------------------------------------------------------

def integrate_step_4_data(step4_data: dict, result: dict) -> None:
    """
    Carry forward Step 4 data unchanged into Step 5a.
    """
    result["data"] = dict(step4_data["data"])

    # Agent placeholders
    result["data"]["agent_created"] = False
    result["data"]["agent_name"] = None
    result["data"]["agent_instructions_length"] = None


# -------------------------------------------------------------------
# Phase 6: Create AI Agent
# -------------------------------------------------------------------

def create_ai_agent(result: dict) -> None:
    """
    Create the AI mapping agent and record metadata only.
    """
    print("\nCreating AI mapping agent...")

    try:
        from app.services.mapping.ai_agent import create_mapping_agent
    except Exception as exc:
        error = f"Failed to import AI agent module: {exc}"
        result["errors"].append(error)
        print(f"❌ {error}")
        return

    agent = create_mapping_agent()

    result["data"]["agent_created"] = True
    result["data"]["agent_name"] = agent.name
    result["data"]["agent_instructions_length"] = len(agent.instructions)

    print("AI agent created successfully:")
    print(f"  Agent Name: {agent.name}")
    print(f"  Instructions Length: {len(agent.instructions)} characters")


# -------------------------------------------------------------------
# Finalization
# -------------------------------------------------------------------

def finalize_step_5a_success(result: dict) -> None:
    result["success"] = len(result["errors"]) == 0


def save_result_to_json(result: dict, output_file: Path) -> None:
    """
    Persist Step 5a results to disk.
    """
    print("\nSaving Step 5a results to JSON...")

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
    print("TESTING STEP 5a: CREATE AI MAPPING AGENT")
    print("PHASE 7: RESULT PERSISTENCE")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_4_results = project_root / "test_results" / "step_4_formatted_fields.json"
    output_file = project_root / "test_results" / "step_5a_ai_agent.json"

    result = build_step_5a_result()

    try:
        step4_data = load_step_4_results(step_4_results)
        validate_step_4_success(step4_data, result)

        if not result["errors"]:
            integrate_step_4_data(step4_data, result)
            create_ai_agent(result)

    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Unexpected error: {exc}")

    finalize_step_5a_success(result)
    save_result_to_json(result, output_file)

    print("\nFinal Step 5a result:")
    print(f"  Success: {result['success']}")
    print(f"  Agent Created: {result['data'].get('agent_created')}")
    print(f"  Errors: {result['errors']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
