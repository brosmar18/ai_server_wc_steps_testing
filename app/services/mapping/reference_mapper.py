"""
Reference object mapping logic.

This module handles mapping CSV columns to fields in reference objects.
For example, if a CSV column "Job Title" maps to employee.emptitle (a reference field),
this determines which field in the 'jobtitle' object should be used for lookup.
"""

from typing import List, Dict
from agents import Runner, trace
from app.schemas.mapping_agent import MappingObject
from app.services.mapping.ai_agent import create_mapping_agent, build_prompt
from app.clients.cdata.object_operations import fetch_object_data
from app.clients.cdata.formatters import format_fields
from app.core.logging_config import get_logger
import json

logger = get_logger(__name__)


async def run_reference_mapping(
    column: str,
    parent_field_name: str,
    ref_object_name: str
) -> Dict:
    """
    Run AI mapping for a reference object field.
    
    When a CSV column maps to a reference field in the parent object,
    we need to determine which field in the referenced object should
    be used for the lookup.

    """
    try:
        logger.info(f"Running reference mapping for column '{column}' → {ref_object_name}")
        
        # Step 1: Fetch reference object fields
        logger.info(f"Fetching fields for reference object: {ref_object_name}")
        raw_fields = fetch_object_data(ref_object_name)
        logger.info(f"Fetched {len(raw_fields)} raw fields from {ref_object_name}")
        
        # Step 2: Format the fields
        formatted_fields = format_fields(raw_fields)
        logger.info(f"Formatted {len(formatted_fields)} fields for {ref_object_name}")
        
        # Step 3: Run AI mapping
        # We're mapping a single column to determine the lookup field
        logger.info(f"Running AI to determine lookup field in {ref_object_name}")
        
        agent = create_mapping_agent()
        prompt = build_prompt([column], formatted_fields)
        
        with trace(f"Reference Object ({ref_object_name}): Lookup Field Mapping"):
            result = await Runner.run(agent, prompt)
            ref_obj_ai_resp: MappingObject = result.final_output
            
            if not ref_obj_ai_resp.mappings:
                logger.warning(f"No mappings returned for reference object {ref_object_name}")
                # Return a default mapping to the first string field
                first_string_field = next(
                    (f for f in formatted_fields if f.get("field_type") == "string"),
                    formatted_fields[0] if formatted_fields else None
                )
                
                if first_string_field:
                    logger.info(f"Using fallback field: {first_string_field['field_name']}")
                    return {
                        "column": column,
                        "parent_field_name": parent_field_name,
                        "field_name": first_string_field["field_name"],
                        "field_type": first_string_field["field_type"],
                        "ref_object_name": ref_object_name
                    }
                else:
                    raise Exception(f"No suitable fields found in {ref_object_name}")
            
            # Get the first mapping (we only sent one column)
            mapping = ref_obj_ai_resp.mappings[0]
            
            logger.info(f"AI mapped '{column}' to {ref_object_name}.{mapping.fieldName}")
            
            return {
                "column": column,
                "parent_field_name": parent_field_name,
                "field_name": mapping.fieldName,
                "field_type": mapping.fieldType,
                "ref_object_name": ref_object_name
            }
        
    except Exception as e:
        logger.error(f"Reference mapping failed for {column} → {ref_object_name}: {e}")
        raise


async def process_all_reference_mappings(
    ref_mappings: List[Dict]
) -> tuple[Dict[str, List[Dict]], Dict[str, Dict]]:
    """
    Process all reference field mappings.
    
    For each reference field mapping from the parent object,
    fetch the reference object's fields and determine the lookup field.

    """
    try:
        logger.info(f"Processing {len(ref_mappings)} reference mappings")
        
        ref_obj_fields: Dict[str, List[Dict]] = {}
        ref_obj_ai_mappings: Dict[str, Dict] = {}
        
        for ref_mapping in ref_mappings:
            column = ref_mapping["column"]
            parent_field_name = ref_mapping["parent_field_name"]
            ref_obj_name = ref_mapping["ref_obj_name"]
            
            logger.info(f"Processing reference: {column} → {ref_obj_name}")
            
            # Fetch and cache reference object fields (avoid duplicate fetches)
            if ref_obj_name not in ref_obj_fields:
                logger.info(f"Fetching fields for new reference object: {ref_obj_name}")
                raw_fields = fetch_object_data(ref_obj_name)
                formatted_fields = format_fields(raw_fields)
                ref_obj_fields[ref_obj_name] = formatted_fields
                logger.info(f"Cached {len(formatted_fields)} fields for {ref_obj_name}")
            
            # Run AI mapping to determine lookup field
            ref_ai_mapping = await run_reference_mapping(
                column=column,
                parent_field_name=parent_field_name,
                ref_object_name=ref_obj_name
            )
            
            ref_obj_ai_mappings[column] = ref_ai_mapping
            logger.info(f"Mapped {column} to {ref_obj_name}.{ref_ai_mapping['field_name']}")
        
        logger.info(f"Completed processing {len(ref_mappings)} reference mappings")
        logger.info(f"Reference objects fetched: {list(ref_obj_fields.keys())}")
        logger.info(f"Reference mappings created: {list(ref_obj_ai_mappings.keys())}")
        
        return ref_obj_fields, ref_obj_ai_mappings
        
    except Exception as e:
        logger.error(f"Failed to process reference mappings: {e}")
        raise