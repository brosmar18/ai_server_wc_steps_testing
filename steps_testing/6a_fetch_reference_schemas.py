import sys
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Any

import httpx


# -------------------------------------------------------------------
# Ensure project root is on PYTHONPATH
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


from app.core.config import config


# -------------------------------------------------------------------
# Result Builder
# -------------------------------------------------------------------

def build_step_6a_result() -> dict:
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
# Reference Object Extraction
# -------------------------------------------------------------------

def extract_unique_reference_objects(reference_mappings: list) -> list:
    unique_objects = sorted(
        {rm["ref_obj_name"] for rm in reference_mappings if rm.get("ref_obj_name")}
    )

    print(f"\nUnique reference objects detected: {len(unique_objects)}")
    for obj in unique_objects:
        print(f"  - {obj}")

    return unique_objects


# -------------------------------------------------------------------
# Local CDATA Client
# -------------------------------------------------------------------

class CDataAPIError(Exception):
    pass


def fetch_reference_schema(object_name: str) -> List[Dict[str, Any]]:
    if not object_name or not object_name.strip():
        raise ValueError("Reference object name cannot be empty")

    object_name = object_name.strip()

    url = f"{config.CDATA_API_BASE}/rest/web/advancedFilter/simpleFilters"
    params = {"object": object_name}

    print(f"\nFetching CDATA schema for reference object: {object_name}")

    response = httpx.get(
        url=url,
        params=params,
        auth=config.CDATA_AUTH,
        timeout=30.0,
    )

    response.raise_for_status()
    data = response.json()

    if not isinstance(data, list):
        raise CDataAPIError("CDATA response is not a list")

    print(f"✓ Fetched {len(data)} fields for '{object_name}'")
    return data


# -------------------------------------------------------------------
# Formatting (NEW in Phase 5)
# -------------------------------------------------------------------

def format_reference_fields(raw_fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize CDATA reference object fields.
    """
    formatted = []

    for raw in raw_fields:
        field_name = raw.get("fieldName")
        if not field_name:
            continue

        options = raw.get("options", {})

        formatted.append({
            "field_name": field_name,
            "field_label": raw.get("label", field_name),
            "field_type": str(raw.get("fieldType", "")).lower(),
            "whats_this": options.get("title"),
        })

    return formatted



# -------------------------------------------------------------------
# Integration
# -------------------------------------------------------------------

def integrate_reference_schemas(step5d_data: dict, result: dict) -> None:
    """
    Carry forward ALL Step 5d data, then add reference schema information.
    This preserves the linear pipeline contract.
    """

    # ------------------------------------------------------------------
    # 1. Carry forward ALL upstream data (CRITICAL)
    # ------------------------------------------------------------------
    result["data"] = dict(step5d_data["data"])

    # ------------------------------------------------------------------
    # 2. Extract reference mappings
    # ------------------------------------------------------------------
    reference_mappings = result["data"]["reference_mappings"]
    unique_ref_objects = extract_unique_reference_objects(reference_mappings)

    raw_ref_schemas: Dict[str, List[Dict[str, Any]]] = {}
    formatted_ref_schemas: Dict[str, List[Dict[str, Any]]] = {}

    for ref_object_name in unique_ref_objects:
        raw_schema = fetch_reference_schema(ref_object_name)
        raw_ref_schemas[ref_object_name] = raw_schema

        formatted_ref_schemas[ref_object_name] = format_reference_fields(raw_schema)

        print(
            f"✓ Normalized {len(formatted_ref_schemas[ref_object_name])} fields "
            f"for reference object '{ref_object_name}'"
        )

    # ------------------------------------------------------------------
    # 3. Add new Step 6a outputs (do NOT remove existing keys)
    # ------------------------------------------------------------------
    result["data"]["unique_ref_objects"] = unique_ref_objects
    result["data"]["raw_ref_schemas"] = raw_ref_schemas
    result["data"]["formatted_ref_schemas"] = formatted_ref_schemas
    result["data"]["ref_schemas_count"] = len(formatted_ref_schemas)



# -------------------------------------------------------------------
# Finalization
# -------------------------------------------------------------------

def finalize_step_6a_success(result: dict) -> None:
    result["success"] = len(result["errors"]) == 0


def save_results(result: dict, output_file: Path) -> None:
    print("\nSaving Step 6a results (Phase 5)...")

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
    print("PHASE 5: FORMAT REFERENCE SCHEMAS")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_5d_results = project_root / "test_results" / "step_5d_mappings_separated.json"
    output_file = project_root / "test_results" / "step_6a_reference_schemas.json"

    result = build_step_6a_result()

    try:
        step5d_data = load_step_5d_results(step_5d_results)
        validate_step_5d_success(step5d_data, result)

        if not result["errors"]:
            integrate_reference_schemas(step5d_data, result)

    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Unexpected error: {exc}")

    finalize_step_6a_success(result)
    save_results(result, output_file)

    print("\nFinal Step 6a result (Phase 5):")
    print(f"  Success: {result['success']}")
    print(f"  Reference Objects: {len(result['data'].get('unique_ref_objects', []))}")
    print(f"  Schemas Formatted: {result['data'].get('ref_schemas_count')}")
    print(f"  Errors: {result['errors']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
