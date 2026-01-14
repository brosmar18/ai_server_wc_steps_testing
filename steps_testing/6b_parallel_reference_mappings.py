import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# -------------------------------------------------------------------
# Ensure project root is on PYTHONPATH
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# -------------------------------------------------------------------
# Imports (same ones used in production logic)
# -------------------------------------------------------------------

from agents import Runner, trace
from app.services.mapping.ai_agent import create_mapping_agent
from app.schemas.mapping_agent import MappingObject

# -------------------------------------------------------------------
# Result Builder
# -------------------------------------------------------------------

def build_step_6b_result() -> dict:
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
        return json.load(f)

def validate_step_6a_success(step6a_data: dict, result: dict) -> None:
    print("\nValidating Step 6a success status...")

    if not step6a_data.get("success"):
        error = "Step 6a did not complete successfully"
        result["errors"].append(error)
        print(f"Validation failed: {error}")
        return

    print("Step 6a completed successfully.")

# -------------------------------------------------------------------
# Phase 2: Build Reference Work Units
# -------------------------------------------------------------------

def build_reference_work_units(step6a_data: dict) -> List[Dict]:
    work_units: List[Dict] = []

    ref_mappings = step6a_data["data"]["reference_mappings"]
    formatted_ref_schemas = step6a_data["data"]["formatted_ref_schemas"]

    for rm in ref_mappings:
        ref_name = rm["ref_obj_name"]
        ref_fields = formatted_ref_schemas.get(ref_name, [])

        if not ref_fields:
            continue

        work_units.append({
            "column": rm["column"],
            "parent_field_name": rm["parent_field_name"],
            "ref_object_name": ref_name,
            "ref_fields": ref_fields,
        })

    return work_units

# -------------------------------------------------------------------
# Phase 4: Parallel AI Execution
# -------------------------------------------------------------------

async def run_parallel_reference_ai(
    work_units: List[Dict]
) -> None:
    print("\nRunning reference mappings in parallel...")
    print(f"✓ Dispatching {len(work_units)} parallel AI calls")

    mapping_agent = create_mapping_agent()

    prompts: List[str] = []
    for unit in work_units:
        column = unit["column"]
        fields = unit["ref_fields"]

        prompt = f"Column List: [{column}],\nFields Object: {json.dumps({'fields': fields})}"
        prompts.append(prompt)

    with trace("Parallel Reference Object Mapping"):
        results = await asyncio.gather(
            *[Runner.run(mapping_agent, p) for p in prompts]
        )

    print(f"✓ Completed {len(results)} parallel AI calls")

    for unit, result in zip(work_units, results):
        unit["ai_result_raw"] = result.final_output
        print(f"✓ AI completed for column: {unit['column']}")

# -------------------------------------------------------------------
# Phase 5: Normalize AI Results (CRITICAL FIX)
# -------------------------------------------------------------------

def normalize_reference_ai_results(work_units: List[Dict]) -> Dict[str, Dict]:
    final_mappings: Dict[str, Dict] = {}

    for unit in work_units:
        result_obj: MappingObject = unit.get("ai_result_raw")

        if not result_obj or not result_obj.mappings:
            continue

        m = result_obj.mappings[0]

        final_mappings[unit["column"]] = {
            "column": unit["column"],
            "parent_field_name": unit["parent_field_name"],
            "field_name": m.fieldName,
            "field_type": m.fieldType,
            "ref_object_name": unit["ref_object_name"],
        }

        # Remove non-serializable object
        unit.pop("ai_result_raw", None)

    return final_mappings

# -------------------------------------------------------------------
# Persistence
# -------------------------------------------------------------------

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

async def main() -> int:
    print("=" * 80)
    print("TESTING STEP 6b: RUN PARALLEL REFERENCE MAPPINGS")
    print("PHASE 4: PARALLEL AI EXECUTION")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_6a_results = project_root / "test_results" / "step_6a_reference_schemas.json"
    output_file = project_root / "test_results" / "step_6b_reference_mappings.json"

    result = build_step_6b_result()

    try:
        step6a_data = load_step_6a_results(step_6a_results)
        validate_step_6a_success(step6a_data, result)

        if result["errors"]:
            raise RuntimeError("Validation failed")

        work_units = build_reference_work_units(step6a_data)
        await run_parallel_reference_ai(work_units)

        ref_obj_ai_mappings = normalize_reference_ai_results(work_units)

        result["data"] = {
            "object_name": step6a_data["data"]["object_name"],
            "file_name": step6a_data["data"]["file_name"],
            "file_path": step6a_data["data"]["file_path"],
            "reference_mappings": step6a_data["data"]["reference_mappings"],
            "ref_obj_ai_mappings": ref_obj_ai_mappings,
            "ref_mappings_count": len(ref_obj_ai_mappings),
        }

        result["success"] = True
        result["timestamp"] = datetime.now().isoformat()

    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Unexpected error: {exc}")

    save_result_to_json(result, output_file)

    print("\nFinal Step 6b result:")
    print(f"  Success: {result['success']}")
    print(f"  Reference mappings created: {result['data'].get('ref_mappings_count')}")
    print(f"  Errors: {result['errors']}")

    return 0 if result["success"] else 1

# -------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())
