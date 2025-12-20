"""
This router provides the endpoint to fetch fields from CDATA objects
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.clients.cdata.object_operations import fetch_object_data, CDataAPIError
from app.clients.cdata.formatters import format_fields
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/objects",
    tags=["objects"]
)

@router.get("/{object_name}/fields")
async def get_object_fields(object_name: str) -> Dict[str, Any]:
    """
    Get field defs for a CDATA object. 
    Example:
        GET /objects/employee/fields
        
        Returns:
        {
            "object_name": "employee",
            "field_count": 45,
            "fields": [
                {
                    "fieldName": "empno",
                    "label": "Emp No",
                    "fieldType": "string",
                    ...
                },
                ...
            ]
        }
    """
    try:
        logger.info(f"API request: Get fields for object '{object_name}")
        
        # Validate object name
        if not object_name or not object_name.strip():
            raise HTTPException(
                status_code=400,
                detail="object_name cannot be empty"
            )
        
        # Fetch raw fields from CDATA
        raw_fields = fetch_object_data(object_name)

        formatted_fields = format_fields(raw_fields)
        


        logger.info(f"Successfully retrieved and formatted {len(formatted_fields)} fields for '{object_name}'")
        return {
            "object_name": object_name,
            "field_count": len(formatted_fields),
            "fields": formatted_fields
        }
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except CDataAPIError as e:
        logger.error(f"CDATA API error: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch fields from CDATA API: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )