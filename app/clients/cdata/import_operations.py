"""
CDATA import operations client.

Handles creating import definitions in the CDATA system by calling
the saveImport endpoint.
"""

from typing import Dict, Any
import json
import httpx
from app.core.config import config
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ImportCreationError(Exception):
    """Raised when import creation in CDATA fails"""
    pass


async def save_import_to_atlas(
    import_params: Dict[str, Any],
    object_name: str,
    filename: str,
) -> Dict[str, Any]:
    """
    Call the CDATA saveImport endpoint to create an import definition.
    
    This sends the import_params we built to CDATA, which creates
    the import definition in the system.
    
    The CDATA endpoint expects:
    - URL: /rest/web/import/saveImport/builder:{object_name}/{filename}
    - Query params: lookupField (from first fieldOverride), headerRowCount=1
    - Body: Complete import_params structure
    
    Args:
        import_params: Complete import configuration from params_builder
            {
                "params": {
                    "fieldOverrides": [...],
                    "importName": "...",
                    "importDescription": "...",
                    "importInstructions": "..."
                }
            }
        object_name: CDATA object name (e.g., "employee")
        filename: CSV filename in ImportFiles directory (e.g., "employees.csv")
        
    Returns:
        Dictionary with:
        {
            "success": True,
            "status_code": 200,
            "url": "http://...",
            "data": {...}  # Response from CDATA
        }
        
    Raises:
        ImportCreationError: If import creation fails
        
    Example:
        result = await save_import_to_atlas(
            import_params={"params": {...}},
            object_name="employee",
            filename="employees.csv"
        )
        
        # Returns:
        # {
        #     "success": True,
        #     "status_code": 200,
        #     "url": "http://localhost:8080/rest/web/import/saveImport/...",
        #     "data": {...}
        # }
    """
    try:
        logger.info("=" * 80)
        logger.info("CDATA IMPORT CREATION")
        logger.info("=" * 80)
        logger.info(f"Object: {object_name}")
        logger.info(f"Filename: {filename}")
        
        # ================================================================
        # Step 1: Validate import_params structure
        # ================================================================
        logger.info("Step 1: Validating import_params structure...")
        
        params = import_params.get("params")
        if not params:
            raise ValueError("import_params is missing 'params' key")
        
        field_overrides = params.get("fieldOverrides", [])
        if not field_overrides:
            raise ValueError("import_params.params.fieldOverrides is empty")
        
        # The first field override determines lookupField in this flow
        first_field_name = field_overrides[0].get("fieldName")
        if not first_field_name:
            raise ValueError("First fieldOverride is missing 'fieldName'")
        
        logger.info(f"✓ Import params validated")
        logger.info(f"  Field overrides: {len(field_overrides)}")
        logger.info(f"  Lookup field: {first_field_name}")
        
        # ================================================================
        # Step 2: Build saveImport URL
        # ================================================================
        logger.info("Step 2: Building saveImport URL...")
        
        url = (
            f"{config.CDATA_API_BASE}/rest/web/import/saveImport/"
            f"builder:{object_name}/{filename}"
            f"?lookupField={first_field_name}&headerRowCount=1"
        )
        
        logger.info(f"✓ URL: {url}")
        
        # ================================================================
        # Step 3: Log import params being sent (debug)
        # ================================================================
        logger.debug("=" * 60)
        logger.debug("Import Params being sent to CDATA:")
        logger.debug(json.dumps(import_params, indent=2))
        logger.debug("=" * 60)
        
        # ================================================================
        # Step 4: Call CDATA saveImport endpoint
        # ================================================================
        logger.info("Step 3: Calling CDATA saveImport endpoint...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json=import_params,
                auth=(config.CDATA_USERNAME, config.CDATA_PASSWORD),
                headers={"Content-Type": "application/json"},
            )
            
            logger.info(f"Response status: {response.status_code}")
            
            # Check for HTTP errors
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                # Include server response body if possible
                error_detail = f"CDATA saveImport failed: {e}"
                if e.response is not None:
                    error_detail += f" | Response body: {e.response.text}"
                logger.error(error_detail)
                raise ImportCreationError(error_detail)
        
        # ================================================================
        # Step 5: Parse and return response
        # ================================================================
        logger.info("Step 4: Processing CDATA response...")
        
        # Parse response data
        data = response.json() if response.text else {}
        
        logger.info("✓ Import definition created successfully in CDATA")
        if data:
            logger.debug(f"Response data: {json.dumps(data, indent=2)}")
        
        result = {
            "success": True,
            "status_code": response.status_code,
            "url": url,
            "data": data,
        }
        
        logger.info("=" * 80)
        logger.info("✓ IMPORT CREATION SUCCESSFUL")
        logger.info("=" * 80)
        
        return result
        
    except ImportCreationError:
        # Re-raise our custom error
        raise
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise ImportCreationError(f"Invalid import_params: {str(e)}")
        
    except httpx.HTTPError as e:
        logger.error(f"HTTP error calling CDATA: {e}")
        raise ImportCreationError(f"Failed to call CDATA API: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error creating import: {e}")
        import traceback
        traceback.print_exc()
        raise ImportCreationError(f"Import creation failed: {str(e)}")