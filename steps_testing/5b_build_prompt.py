import sys
from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict, Any


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
# Local Prompt Builder (Inline)
# -------------------------------------------------------------------

def build_prompt(columns: List[str], fields: List[Dict[str, Any]]) -> str:
    """
    Build the AI mapping prompt.
    """
    payload = {"fields": fields}
    fields_json = json.dumps(payload, ensure_ascii=False)

    return f"Column List: {columns},\nFields Object: {fields_json}"


# -------------------------------------------------------------------
# Persistence
# -------------------------------------------------------------------

def save_results(result: dict, output_file: Path) -> None:
    print("\nSaving Step 5b results...")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Results saved to: {output_file}")


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main() -> int:
    print("=" * 80)
    print("TESTING STEP 5b: BUILD PROMPT FOR AI AGENT")
    print("PHASE 5: PERSIST PROMPT RESULT")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_5a_results = project_root / "test_results" / "step_5a_ai_agent.json"
    output_file = project_root / "test_results" / "step_5b_prompt.json"

    result = build_step_5b_result()

    try:
        step5a_data = load_step_5a_results(step_5a_results)
        validate_step_5a_success(step5a_data, result)

        if not result["errors"]:
            columns = step5a_data["data"]["columns"]
            formatted_fields = step5a_data["data"]["formatted_fields"]

            prompt = build_prompt(columns, formatted_fields)

            result["data"] = {
                "object_name": step5a_data["data"]["object_name"],
                "file_name": step5a_data["data"]["file_name"],
                "file_path": step5a_data["data"]["file_path"],
                "columns": columns,
                "raw_fields": step5a_data["data"]["raw_fields"],
                "formatted_fields": formatted_fields,
                "agent_created": step5a_data["data"]["agent_created"],
                "agent_name": step5a_data["data"]["agent_name"],
                "agent_instructions_length": step5a_data["data"]["agent_instructions_length"],
                "prompt": prompt,
                "prompt_length": len(prompt),
            }

            result["success"] = True
            result["timestamp"] = datetime.now().isoformat()

            save_results(result, output_file)

    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Error: {exc}")

    print("\nFinal Step 5b result:")
    print(f"  Success: {result['success']}")
    print(f"  Prompt Length: {result['data'].get('prompt_length')}")
    print(f"  Errors: {result['errors']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
