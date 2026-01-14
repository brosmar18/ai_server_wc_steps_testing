import sys
import asyncio
from pathlib import Path
from datetime import datetime
import json
import os
from typing import List, Dict

from agents import Agent
from app.schemas.mapping_agent import MappingObject
from app.core.config import config


# -------------------------------------------------------------------
# Ensure project root is on PYTHONPATH
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# -------------------------------------------------------------------
# Result Builder
# -------------------------------------------------------------------

def build_step_5c_result() -> dict:
    return {
        "step": "Step 5c: Run AI Agent",
        "step_number": "5c",
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "errors": [],
    }


# -------------------------------------------------------------------
# Load & Validate Step 5b
# -------------------------------------------------------------------

def load_step_5b_results(step_5b_file: Path) -> dict:
    print("\nLoading Step 5b results...")
    print(f"Step 5b results path: {step_5b_file}")

    if not step_5b_file.exists():
        raise FileNotFoundError(f"Step 5b results not found: {step_5b_file}")

    with open(step_5b_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Step 5b results loaded successfully.")
    return data


def validate_step_5b_success(step5b_data: dict, result: dict) -> None:
    print("\nValidating Step 5b success status...")

    if not step5b_data.get("success"):
        error = "Step 5b did not complete successfully"
        result["errors"].append(error)
        print(f"Validation failed: {error}")
        return

    print("Step 5b completed successfully.")


# -------------------------------------------------------------------
# ORIGINAL AI AGENT CREATION (verbatim logic)
# -------------------------------------------------------------------

def create_mapping_agent() -> Agent:
    """
    Function to create AI mapping agent.
    """
    try:
        print("\nCreating AI mapping agent...")

        os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY

        agent = Agent(
            name="mapping_agent",
            instructions="""
                You are an expert at mapping CSV column names to database field definitions.

                The user will provide:
                1) A list of column names from a CSV file
                2) A fields object containing field definitions

                Your job is to map each column to its corresponding fieldName using the fieldName, 
                field label, fieldType, and whats_this (help text) values to support your reasoning.

                You will also note the fieldType value for the field that you mapped to a column.
                If the field is a reference field, you should include the refObjectName when provided.

                CRITICAL: Return ONLY valid JSON with this exact structure:

                {
                  "mappings": [
                    {
                      "column": "<column name from the CSV>",
                      "fieldName": "<matching fieldName>",
                      "fieldType": "<fieldType>",
                      "refObjectName": "<only when fieldType == reference>"
                    }
                  ]
                }

                Rules:
                - Map ALL columns
                - Use exact field names
                - Do not include null refObjectName
                - Do not include explanation text
            """,
            output_type=MappingObject,
        )

        print("✓ AI mapping agent created successfully")
        return agent

    except Exception as exc:
        raise RuntimeError(f"Failed to create mapping agent: {exc}") from exc


# -------------------------------------------------------------------
# Save Results
# -------------------------------------------------------------------

def save_results(result: dict, output_file: Path) -> None:
    print("\nSaving Step 5c results...")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Results saved to: {output_file}")
    print(f"File size: {output_file.stat().st_size} bytes")


# -------------------------------------------------------------------
# Async Main
# -------------------------------------------------------------------

async def main() -> int:
    print("=" * 80)
    print("TESTING STEP 5c: RUN AI AGENT")
    print("PHASE 4: AGENT RECREATION (ORIGINAL LOGIC)")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_5b_results = project_root / "test_results" / "step_5b_prompt.json"
    step_5c_output = project_root / "test_results" / "step_5c_agent_execution.json"

    result = build_step_5c_result()

    try:
        step5b_data = load_step_5b_results(step_5b_results)
        validate_step_5b_success(step5b_data, result)

        if not result["errors"]:
            agent = create_mapping_agent()

            print(f"  Agent name: {agent.name}")
            print(f"  Instructions length: {len(agent.instructions)} characters")

            result["data"] = {
                "object_name": step5b_data["data"]["object_name"],
                "file_name": step5b_data["data"]["file_name"],
                "file_path": step5b_data["data"]["file_path"],
                "columns": step5b_data["data"]["columns"],
                "raw_fields": step5b_data["data"]["raw_fields"],
                "formatted_fields": step5b_data["data"]["formatted_fields"],
                "agent_created": True,
                "agent_name": agent.name,
                "agent_instructions_length": len(agent.instructions),
                "prompt": step5b_data["data"]["prompt"],
                "prompt_length": step5b_data["data"]["prompt_length"],
                "ai_mappings": [],
                "total_mappings": 0,
            }

        save_results(result, step_5c_output)

    except Exception as exc:
        result["errors"].append(str(exc))
        save_results(result, step_5c_output)
        print(f"Error: {exc}")

    print("\nFinal Step 5c result (Phase 4):")
    print(f"  Success: {result['success']}")
    print(f"  Agent Created: {result['data'].get('agent_created', False)}")
    print(f"  Errors: {result['errors']}")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
