"""
Parent object mapping logic.

This module handles running the AI agent to map CSV columns
to parent object fields.
"""

from typing import List, Dict
from agents import Runner, trace
from app.schemas.mapping_agent import Mapping, MappingObject
from app.services.mapping.ai_agent import create_mapping_agent, build_prompt
from app.core.logging_config import get_logger
import json

logger = get_logger(__name__)


def build_final_mappings(mappings: List[Mapping]) -> List[Dict]:
    """
    Extract non-reference field mappings.
    
    Filters the AI's mappings to get only direct (non-reference) field mappings.
    
    Args:
        mappings: List of all mappings from AI
        
    Returns:
        List of non-reference field mappings
    """
    try:
        results: List[Dict] = []
        
        for m in mappings:
            if m.fieldType != "reference":
                results.append({
                    "column": m.column,
                    "fieldName": m.fieldName,
                    "fieldType": m.fieldType
                })
        
        logger.info(f"Built {len(results)} non-reference mappings")
        return results
        
    except Exception as e:
        logger.error(f"Failed to build final mappings: {e}")
        raise


def build_ref_obj_mappings(mappings: List[Mapping]) -> List[Dict]:
    """
    Extract reference field mappings.
    
    Filters the AI's mappings to get only reference field mappings
    that need additional processing.
    
    Args:
        mappings: List of all mappings from AI
        
    Returns:
        List of reference field mappings
    """
    try:
        results: List[Dict] = []
        
        for m in mappings:
            if m.fieldType == "reference" and m.refObjectName:
                results.append({
                    "column": m.column,
                    "parent_field_name": m.fieldName,
                    "field_type": m.fieldType,
                    "ref_obj_name": m.refObjectName
                })
        
        logger.info(f"Built {len(results)} reference mappings")
        return results
        
    except Exception as e:
        logger.error(f"Failed to build reference mappings: {e}")
        raise


async def run_parent_mapping(
    columns: List[str],
    fields: List[Dict]
) -> tuple[List[Dict], List[Dict]]:
    """
    Run AI mapping for parent object.
    
    Uses the AI agent to map CSV columns to CDATA fields.
    Separates the results into non-reference and reference field mappings.
    
    Args:
        columns: List of CSV column names
        fields: List of formatted CDATA field definitions
        
    Returns:
        Tuple of (final_mappings, ref_obj_mappings)
        - final_mappings: Non-reference field mappings
        - ref_obj_mappings: Reference field mappings that need additional processing
        
    Raises:
        Exception: If AI agent fails or returns invalid data
    """
    try:
        logger.info(f"Running parent mapping for {len(columns)} columns")
        
        # Create agent
        agent = create_mapping_agent()
        
        # Build prompt
        prompt = build_prompt(columns, fields)
        
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        # Run agent with tracing
        with trace("Parent Object: Column -> Field Mapping"):
            result = await Runner.run(agent, prompt)
            parent_obj_ai_resp: MappingObject = result.final_output
            
            # Convert to dicts for logging
            all_mappings_dicts = [m.model_dump() for m in parent_obj_ai_resp.mappings]
            
            logger.info(f"AI returned {len(all_mappings_dicts)} total mappings")
            logger.debug(f"All mappings: {json.dumps(all_mappings_dicts, indent=2)}")
            
            # Separate into final and reference mappings
            final_mapping_data = build_final_mappings(parent_obj_ai_resp.mappings)
            ref_obj_mapping_data = build_ref_obj_mappings(parent_obj_ai_resp.mappings)
            
            logger.info(f"Separated into {len(final_mapping_data)} final and {len(ref_obj_mapping_data)} reference mappings")
        
        return final_mapping_data, ref_obj_mapping_data
        
    except Exception as e:
        logger.error(f"Parent mapping failed: {e}")
        raise