"""
Formatters for CDATA API responses.
This module handles: 
- Normalizing raw CDATA field defs into consistent structure
- Extracting reference object information
- Flattening nested response structures
"""
from typing import List, Dict, Any
from app.core.logging_config import get_logger

logger = get_logger(__name__)

def format_fields(raw_fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format CDATA advancedFilter/simpleFilters field definitions into a normalized structure that we will use for the request we send the AI.
    Transforms raw CDATA response into a clean, consistent format: 
    - Standarizes field names (fieldName -> field_name)
    - Extracts help text (whats_this) from nested options
    - Identifies and extracts reference object info when applicable.
    - Flattens nested structures

    Arguments: 
        raw_fields: Raw field defs from CDATA API

    Returns:
        List ofnormaized field dictionaries with structure: 
        {
            "field_name": str,        # The field's API name
            "field_label": str,       # Human-readable label
            "field_type": str,        # Field type (string, number, reference, etc.)
            "whats_this": str,        # Help/description text
            "ref_object_name": str    # (Optional) For reference fields only
        }

    Example:
        Input (raw CDATA):
        [
            {
                "fieldName": "empno",
                "label": "Emp No",
                "fieldType": "string",
                "options": {
                    "title": "Employee Number",
                    "altVarName": "",
                    "fieldOrVar": "field",
                    "length": 26,
                    "required": true,
                }
            }
        ]
        
        Output (formatted):
        [
            {
                "field_name": "empno",
                "field_label": "Emp No",
                "field_type": "string",
                "whats_this": "Employee Number"
            }
        ]
    """
    if not isinstance(raw_fields, list):
        logger.error(f"Expected list of fields, got {type(raw_fields)}")
        raise ValueError(f"raw_fields must be a list, got {type(raw_fields)}")
    
    if len(raw_fields) == 0:
        logger.info("No fields to format (empty list)")
        return []
    formatted: List[Dict[str, Any]] = []

    for field in raw_fields:
            format_obj: Dict[str, Any] = {
                "field_name": field.get("fieldName"),
                "field_label": field.get("label"),
                "field_type": field.get("fieldType"),
                "whats_this": field.get("options", {}).get("title")
            }

            if field.get("fieldType") == "reference":
                ref_objs = field.get("options", {}).get("refObjects", [])
                if ref_objs and len(ref_objs) > 0:
                    format_obj["ref_object_name"] = ref_objs[0].get("name")

            formatted.append(format_obj)
        

    logger.info(f"Succesfully formatted {len(formatted)} fields")
    return formatted
    
    
    
def format_object_data(raw_fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convenience function that delegates to format_fields.
    Exists for semantic clarity when formatting entire object schemas
    """
    return format_fields(raw_fields)

