import sys
from pathlib import Path
from datetime import datetime
import json
import asyncio
import httpx


# -------------------------------------------------------------------
# Ensure project root is on PYTHONPATH
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# -------------------------------------------------------------------
# Config + Logging
# -------------------------------------------------------------------

from app.core.config import config
from app.core.logging_config import get_logger

logger = get_logger(__name__)


# -------------------------------------------------------------------
# Custom Error
# -------------------------------------------------------------------

class ImportCreationError(Exception):
    """Raised when import creation in CDATA fails"""
    pass


# -------------------------------------------------------------------
# Inline CDATA Import Logic (from original import_operations.py)
# -------------------------------------------------------------------

async def save_import_to_atlas(
    import_params: dict,
    object_name: str,
    filename: str,
) -> dict:
    try:
        logger.info("=" * 80)
        logger.info("CDATA IMPORT CREATION")
        logger.info("=" * 80)
        logger.info(f"Object: {object_name}")
        logger.info(f"Filename: {filename}")

        # ------------------------------------------------------------
        # Step 1: Validate import_params
        # ------------------------------------------------------------
        params = import_params.get("params")
        if not params:
            raise ValueError("import_params missing 'params' key")

        field_overrides = params.get("fieldOverrides", [])
        if not field_overrides:
            raise ValueError("import_params.params.fieldOverrides is empty")

        first_field_name = field_overrides[0].get("fieldName")
        if not first_field_name:
            raise ValueError("First fieldOverride missing 'fieldName'")

        logger.info("✓ Import params validated")
        logger.info(f"  Field overrides: {len(field_overrides)}")
        logger.info(f"  Lookup field: {first_field_name}")

        # ------------------------------------------------------------
        # Step 2: Build saveImport URL
        # ------------------------------------------------------------
        url = (
            f"{config.CDATA_API_BASE}/rest/web/import/saveImport/"
            f"builder:{object_name}/{filename}"
            f"?lookupField={first_field_name}&headerRowCount=1"
        )

        logger.info(f"✓ URL: {url}")

        # ------------------------------------------------------------
        # Step 3: Call CDATA saveImport endpoint
        # ------------------------------------------------------------
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json=import_params,
                auth=(config.CDATA_USERNAME, config.CDATA_PASSWORD),
                headers={"Content-Type": "application/json"},
            )

            logger.info(f"Response status: {response.status_code}")

            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                detail = f"CDATA saveImport failed: {exc}"
                if exc.response is not None:
                    detail += f" | Response body: {exc.response.text}"
                raise ImportCreationError(detail)

        # ------------------------------------------------------------
        # Step 4: Parse response
        # ------------------------------------------------------------
        data = response.json() if response.text else {}

        logger.info("✓ Import definition created successfully in CDATA")

        return {
            "success": True,
            "status_code": response.status_code,
            "url": url,
            "data": data,
        }

    except ImportCreationError:
        raise

    except ValueError as exc:
        raise ImportCreationError(f"Invalid import_params: {exc}")

    except httpx.HTTPError as exc:
        raise ImportCreationError(f"Failed to call CDATA API: {exc}")

    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise ImportCreationError(f"Import creation failed: {exc}")


# -------------------------------------------------------------------
# Result Builder
# -------------------------------------------------------------------

def build_step_9_result() -> dict:
    return {
        "step": "Step 9: Create Import in CDATA",
        "step_number": "9",
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "errors": [],
    }


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

async def main() -> int:
    print("=" * 80)
    print("TESTING STEP 9: CREATE IMPORT IN CDATA")
    print("INLINE CDATA LOGIC (NO CLIENT IMPORT)")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_8c_file = project_root / "test_results" / "step_8c_import_params.json"
    output_file = project_root / "test_results" / "step_9_cdata_import.json"

    result = build_step_9_result()

    try:
        with open(step_8c_file, "r", encoding="utf-8") as f:
            step8c_data = json.load(f)

        if not step8c_data.get("success"):
            raise RuntimeError("Step 8c did not complete successfully")

        data = step8c_data["data"]

        import_params = data["import_params"]
        object_name = data["object_name"]
        file_name = data["file_name"]

        print("\nCreating import in CDATA...")
        print(f"Object: {object_name}")
        print(f"File: {file_name}")
        print(f"Import Name: {import_params['params']['importName']}")

        try:
            import_result = await save_import_to_atlas(
                import_params=import_params,
                object_name=object_name,
                filename=file_name,
            )
        except ImportCreationError as exc:
            import_result = {
                "success": False,
                "error": str(exc),
                "status_code": None,
                "url": None,
                "data": None,
            }

        result["data"] = {
            "object_name": object_name,
            "file_name": file_name,
            "file_path": data["file_path"],
            "import_params": import_params,
            "import_result": import_result,
            "cdata_import_created": import_result.get("success", False),
            "cdata_status_code": import_result.get("status_code"),
            "cdata_url": import_result.get("url"),
        }

        if not import_result.get("success"):
            result["errors"].append(import_result.get("error"))

        # IMPORTANT: Step 9 never fails the pipeline
        result["success"] = True
        result["timestamp"] = datetime.now().isoformat()

    except Exception as exc:
        result["errors"].append(str(exc))
        result["success"] = False

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\nStep 9 Summary:")
    print(f"  Pipeline Success: {result['success']}")
    print(f"  CDATA Import Created: {result['data'].get('cdata_import_created')}")
    print(f"  Errors: {result['errors']}")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
