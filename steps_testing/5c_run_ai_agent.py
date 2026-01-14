import sys
from pathlib import Path
from datetime import datetime
import json
import asyncio


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
# Integration
# -------------------------------------------------------------------

def integrate_step_5b_data(step5b_data: dict, result: dict) -> None:
    """
    Carry forward Step 5b data unchanged into Step 5c.
    """
    result["data"] = dict(step5b_data["data"])

    # Execution placeholders
    result["data"]["agent_recreated"] = False
    result["data"]["execution_primitives_loaded"] = False
    result["data"]["agent_executed"] = False
    result["data"]["ai_mappings"] = []
    result["data"]["total_mappings"] = 0


# -------------------------------------------------------------------
# Phase 2: Recreate AI Agent (same import pattern as 5a)
# -------------------------------------------------------------------

def recreate_ai_agent(result: dict):
    print("\nRecreating AI mapping agent...")

    try:
        from app.services.mapping.ai_agent import create_mapping_agent
    except Exception as exc:
        error = f"Failed to import AI agent module: {exc}"
        result["errors"].append(error)
        print(f"❌ {error}")
        return None

    try:
        agent = create_mapping_agent()
    except Exception as exc:
        error = f"Failed to create AI agent: {exc}"
        result["errors"].append(error)
        print(f"❌ {error}")
        return None

    result["data"]["agent_recreated"] = True
    result["data"]["agent_name"] = agent.name
    result["data"]["agent_instructions_length"] = len(agent.instructions)

    print("AI agent recreated successfully:")
    print(f"  Agent Name: {agent.name}")
    print(f"  Instructions Length: {len(agent.instructions)} characters")

    return agent


# -------------------------------------------------------------------
# Phase 3: Import Execution Primitives
# -------------------------------------------------------------------

def import_execution_primitives(result: dict):
    print("\nImporting AI execution primitives...")

    try:
        from agents import Runner, trace
    except Exception as exc:
        error = f"Failed to import execution primitives: {exc}"
        result["errors"].append(error)
        print(f"❌ {error}")
        return None, None

    result["data"]["execution_primitives_loaded"] = True
    print("Execution primitives imported successfully.")

    return Runner, trace


# -------------------------------------------------------------------
# Phase 5: Execute Agent and Capture Mappings
# -------------------------------------------------------------------

async def run_agent_and_capture_mappings(
    *,
    agent,
    prompt: str,
    Runner,
    trace,
    result: dict,
) -> None:
    print("\nRunning AI agent with prompt...")
    print("This may take a few moments...")

    try:
        with trace("Parent Object: Column -> Field Mapping"):
            run_result = await Runner.run(agent, prompt)

        final_output = getattr(run_result, "final_output", None)
        if final_output is None:
            raise RuntimeError("Runner.run returned no final_output")

        # Typical case: final_output is a Pydantic model with .mappings
        mappings = getattr(final_output, "mappings", None)

        # Fallback: final_output might already be a dict
        if mappings is None and isinstance(final_output, dict):
            mappings = final_output.get("mappings")

        if mappings is None:
            raise RuntimeError("final_output did not contain 'mappings'")

        # Convert mappings to plain dicts
        mappings_dicts = []
        for m in mappings:
            if hasattr(m, "model_dump"):
                mappings_dicts.append(m.model_dump())
            elif isinstance(m, dict):
                mappings_dicts.append(m)
            else:
                mappings_dicts.append(dict(m))

        result["data"]["ai_mappings"] = mappings_dicts
        result["data"]["total_mappings"] = len(mappings_dicts)
        result["data"]["agent_executed"] = True

        print("✓ AI agent completed successfully")
        print(f"  Generated {len(mappings_dicts)} mappings")

        # Show first 3 mappings for proof-of-life
        if mappings_dicts:
            print("\nSample mappings (first 3):")
            for idx, mm in enumerate(mappings_dicts[:3], start=1):
                col = mm.get("column")
                field = mm.get("fieldName")
                ftype = mm.get("fieldType")
                ref = mm.get("refObjectName")
                print(f"{idx}. Column: {col!r} -> {field} ({ftype})")
                if ref:
                    print(f"   refObjectName: {ref}")

    except Exception as exc:
        error = f"AI execution failed: {exc}"
        result["errors"].append(error)
        print(f"❌ {error}")


# -------------------------------------------------------------------
# Persistence
# -------------------------------------------------------------------

def save_results(result: dict, output_file: Path) -> None:
    print("\nSaving Step 5c results...")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Results saved to: {output_file}")
    print(f"File size: {output_file.stat().st_size} bytes")


# -------------------------------------------------------------------
# Async Orchestration
# -------------------------------------------------------------------

async def run_step_5c() -> int:
    print("=" * 80)
    print("TESTING STEP 5c: RUN AI AGENT")
    print("PHASE 5: EXECUTE AGENT AND CAPTURE MAPPINGS")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_5b_results = project_root / "test_results" / "step_5b_prompt.json"
    output_file = project_root / "test_results" / "step_5c_agent_execution.json"

    result = build_step_5c_result()

    try:
        step5b_data = load_step_5b_results(step_5b_results)
        validate_step_5b_success(step5b_data, result)

        if not result["errors"]:
            integrate_step_5b_data(step5b_data, result)

            agent = recreate_ai_agent(result)
            Runner, trace = import_execution_primitives(result)

            if not result["errors"] and agent and Runner and trace:
                prompt = result["data"]["prompt"]
                await run_agent_and_capture_mappings(
                    agent=agent,
                    prompt=prompt,
                    Runner=Runner,
                    trace=trace,
                    result=result,
                )

        result["success"] = len(result["errors"]) == 0
        save_results(result, output_file)

    except Exception as exc:
        result["errors"].append(str(exc))
        result["success"] = False
        save_results(result, output_file)
        print(f"Unexpected error: {exc}")

    print("\nFinal Step 5c result (Phase 5):")
    print(f"  Success: {result['success']}")
    print(f"  Agent Recreated: {result['data'].get('agent_recreated')}")
    print(f"  Agent Executed: {result['data'].get('agent_executed')}")
    print(f"  Total Mappings: {result['data'].get('total_mappings')}")
    print(f"  Errors: {result['errors']}")

    return 0 if result["success"] else 1


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main() -> int:
    return asyncio.run(run_step_5c())


if __name__ == "__main__":
    sys.exit(main())
