import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import json
from datetime import datetime
from typing import List, Dict, Any

import httpx
from app.core.config import config

def build_step_3_result() -> dict:


    return {
        "step": "Step 3: Fetch CDATA Object Schema",
        "step_nummber": 3,
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "errors": []
    }

def load_step_2_results(step_2_file: Path) -> dict:

    print("\nLoading Step 2 Results...")
    
    if not step_2_file.exists():
        raise FileNotFoundError(f"Step 2 results not found: {step_2_file}")
    
    with open(step_2_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Step 2 results loaded!")
    return data

def validate_step_2_success(step2_data: dict, result: dict) -> None:

    print("\nValidating Step 2 success status...")

    if not step2_data.get("success"):
        error = "Step 2 did not complete successfully"
        result["errors"].append(error)
        print(f"Validation failed: {error}")

        return
    
    print("Step 2 completed successfully!")

# -------------------------------------------------------------------
# Local CDATA client primitives (rebuilt, not imported)
# -------------------------------------------------------------------

class CDataAPIError(Exception):
    """Raised when CDATA API Calls Fail"""
    pass


def fetch_object_data(object_name: str) -> List[Dict[str, Any]]:

    # Fetch field defs for a given object from the CDATA API

    try:
        # Input validation
        if not object_name or not object_name.strip():
            raise ValueError("object_name cannot be empty")
        
        object_name = object_name.strip()

        # Build Request
        url = f"{config.CDATA_API_BASE}/rest/web/advancedFilter/simpleFilters"
        params = {"object": object_name}

        print("\nCalling CDATA API")
        print(f"URL: {url}")
        print(f"Params: {params}")


        response = httpx.get(
            url=url,
            params=params,
            auth=config.CDATA_AUTH,
            timeout=30.0
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):
            raise CDataAPIError("CDATA response is not a list")
        
        return data
    
    except  ValueError:
        raise

    except httpx.HTTPStatusError as exc:
        raise CDataAPIError(
            f"CDATA API returned stats {exc.response.status_code}"
        ) from exc
    
    except Exception as exc:
        raise CDataAPIError(
            f"Unexpected error fetching CDATA schema: {exc}"
        ) from exc
    

def finalize_step_3_data(
    step2_data: dict,
    raw_fields: list,
    result: dict,
) -> None:
    result["data"] = {
        "object_name": step2_data["data"]["object_name"],
        "file_name": step2_data["data"]["file_name"],
        "file_path": step2_data["data"]["file_path"],
        "columns": step2_data["data"]["columns"],
        "raw_fields": raw_fields,
    }

def finalize_step_success(result: dict) -> None:
    result["success"] = (
        len(result["errors"]) == 0
        and bool(result["data"].get("raw_fields"))
    )

def save_result_to_json(result: dict, output_file: Path) -> None:
    print("\nSaving step 3 result to JSON...")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Result saved to: {output_file}")
    print(f"File size: {output_file.stat().st_size} bytes")



def main() -> None:
    print("=" * 80)
    print("TESTING STEP 3: FETCH CDATA OBJECT SCHEMA")
    print("PHASE 2: CONFIGURATION ONLY")
    print("=" * 80)

    # Configuration (defined, not used yet)
    project_root = Path(__file__).parent.parent
    step_2_results = project_root / "test_results" / "step_2_csv_parsing.json"
    output_file = project_root / "test_results" / "step_3_cdata_schema.json"
    



    result = build_step_3_result()

    try:
        step2_data = load_step_2_results(step_2_results)
        validate_step_2_success(step2_data, result)

        if not result["errors"]:
          object_name = step2_data["data"]["object_name"]
          raw_fields = fetch_object_data(object_name)
          finalize_step_3_data(step2_data, raw_fields, result)



    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Error: {exc}")

    finalize_step_success(result)
    save_result_to_json(result, output_file)

    print("\nFinal Step 3 result:")
    print(f"  Success: {result['success']}")
    print(f"  Errors: {result['errors']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)