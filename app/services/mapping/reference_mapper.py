"""
Reference object mapping logic with parallel processing.

This module handles mapping CSV columns to fields in reference objects
using asyncio.gather for true parallel execution.
"""

import asyncio
from typing import List, Dict, Tuple
from agents import Runner, trace, Agent
from app.schemas.mapping_agent import MappingObject
from app.services.mapping.ai_agent import create_mapping_agent, build_prompt
from app.clients.cdata.object_operations import fetch_object_data
from app.clients.cdata.formatters import format_fields
from app.core.logging_config import get_logger

logger = get_logger(__name__)


async def fetch_all_reference_schemas(
    ref_mappings: List[Dict]
) -> Dict[str, List[Dict]]:
    """
    Fetch schemas for all unique reference objects.
    
    Args:
        ref_mappings: List of reference mappings from parent AI
        
    Returns:
        Dictionary mapping ref_object_name to its formatted fields
        {
            "jobtitle": [{field}, {field}, ...],
            "department": [{field}, {field}, ...]
        }
    """
    # Get unique reference object names
    unique_ref_objects = set(rm["ref_obj_name"] for rm in ref_mappings)
    
    logger.info(f"Fetching schemas for {len(unique_ref_objects)} reference objects")
    
    ref_schemas: Dict[str, List[Dict]] = {}
    
    for ref_obj_name in unique_ref_objects:
        logger.info(f"Fetching fields for reference object: {ref_obj_name}")
        raw_fields = fetch_object_data(ref_obj_name)
        formatted_fields = format_fields(raw_fields)
        ref_schemas[ref_obj_name] = formatted_fields
        logger.info(f"✓ Fetched {len(formatted_fields)} fields for {ref_obj_name}")
    
    return ref_schemas


async def run_all_ref_mappings(
    mapping_agent: Agent,
    ref_objects_list: List[Dict],
    ref_schemas: Dict[str, List[Dict]],
) -> Dict[str, Dict]:
    """
    Run all reference object mappings in parallel using asyncio.gather.
    
    Each reference field gets its own AI call, and all calls run concurrently.
    
    Args:
        mapping_agent: The AI agent for mapping
        ref_objects_list: List of reference mappings from parent AI
            [
                {
                    "column": "Primary Job Title",
                    "parent_field_name": "emptitle",
                    "ref_obj_name": "jobtitle"
                },
                ...
            ]
        ref_schemas: Dictionary of reference object schemas
            {
                "jobtitle": [{field}, {field}, ...],
                ...
            }
        
    Returns:
        Dictionary mapping column name to reference mapping:
        {
            "Primary Job Title": {
                "column": "Primary Job Title",
                "parentFieldName": "emptitle",
                "fieldName": "title",
                "fieldType": "string",
                "refObjectName": "jobtitle"
            },
            ...
        }
    """
    logger.info(f"Preparing {len(ref_objects_list)} parallel reference mappings")
    
    # Build metadata and prompts for all reference mappings
    ref_meta: List[Tuple[str, str, str]] = []
    prompts: List[str] = []

    for ref_obj in ref_objects_list:
        ref_name = ref_obj["ref_obj_name"]
        column_name = ref_obj["column"]
        parent_field_name = ref_obj["parent_field_name"]

        # Get the reference object's fields
        ref_fields = ref_schemas.get(ref_name, [])
        if not ref_fields:
            logger.warning(f"No fields found for reference object: {ref_name}")
            continue

        # Store metadata for this mapping
        ref_meta.append((column_name, ref_name, parent_field_name))

        # Build a single-column prompt for this reference field
        prompt = build_prompt([column_name], ref_fields)
        prompts.append(prompt)
        
        logger.debug(f"Prepared prompt for: {column_name} → {ref_name}")

    if not prompts:
        logger.warning("No valid prompts to process")
        return {}

    logger.info(f"Running {len(prompts)} reference mappings in parallel...")
    
    # Run all AI calls in parallel using asyncio.gather
    with trace("Parallel Reference Object Mapping"):
        results = await asyncio.gather(
            *[Runner.run(mapping_agent, prompt) for prompt in prompts]
        )

    logger.info(f"✓ Completed {len(results)} parallel AI calls")

    # Build final mapping dictionary
    mapping_by_column: Dict[str, Dict] = {}

    # Combine metadata with results
    for (column_name, ref_name, parent_field_name), result in zip(ref_meta, results):
        result_obj: MappingObject = result.final_output

        if not result_obj.mappings:
            logger.warning(f"No mappings returned for {column_name} → {ref_name}")
            continue

        # Only one mapping because we sent only one column per prompt
        m = result_obj.mappings[0]

        mapping_by_column[column_name] = {
            "column": column_name,
            "parent_field_name": parent_field_name,  # Changed from parentFieldName for consistency
            "field_name": m.fieldName,  # Changed from fieldName for consistency
            "field_type": m.fieldType,  # Changed from fieldType for consistency
            "ref_object_name": ref_name  # Changed from refObjectName for consistency
        }
        
        logger.debug(f"✓ Mapped: {column_name} → {ref_name}.{m.fieldName}")

    logger.info(f"✓ Successfully mapped {len(mapping_by_column)} reference fields")
    
    return mapping_by_column


async def process_all_reference_mappings(
    ref_mappings: List[Dict]
) -> Tuple[Dict[str, List[Dict]], Dict[str, Dict]]:
    """
    Process all reference field mappings using parallel AI calls.
    
    This is the main entry point for reference object processing.
    
    Args:
        ref_mappings: List of reference mappings from parent object AI
            [
                {
                    "column": "Primary Job Title",
                    "parent_field_name": "emptitle",
                    "field_type": "reference",
                    "ref_obj_name": "jobtitle"
                },
                ...
            ]
        
    Returns:
        Tuple of (ref_obj_fields, ref_obj_ai_mappings):
        
        ref_obj_fields: Dictionary of reference object fields
        {
            "jobtitle": [
                {"field_name": "title", "field_label": "Title", ...},
                ...
            ],
            ...
        }
        
        ref_obj_ai_mappings: Dictionary of AI-generated reference mappings
        {
            "Primary Job Title": {
                "column": "Primary Job Title",
                "parent_field_name": "emptitle",
                "field_name": "title",
                "field_type": "string",
                "ref_object_name": "jobtitle"
            },
            ...
        }
    """
    try:
        logger.info(f"Processing {len(ref_mappings)} reference mappings (PARALLEL MODE)")
        
        # Step 1: Fetch all reference object schemas
        logger.info("Step 1: Fetching all reference object schemas...")
        ref_schemas = await fetch_all_reference_schemas(ref_mappings)
        logger.info(f"✓ Fetched schemas for {len(ref_schemas)} reference objects")
        
        # Step 2: Create mapping agent
        logger.info("Step 2: Creating AI mapping agent...")
        mapping_agent = create_mapping_agent()
        logger.info("✓ AI mapping agent created")
        
        # Step 3: Run all reference mappings in parallel
        logger.info("Step 3: Running parallel reference mappings...")
        ref_obj_ai_mappings = await run_all_ref_mappings(
            mapping_agent=mapping_agent,
            ref_objects_list=ref_mappings,
            ref_schemas=ref_schemas
        )
        logger.info(f"✓ Completed {len(ref_obj_ai_mappings)} reference mappings")
        
        # Return both the schemas and the AI mappings
        logger.info("=" * 60)
        logger.info("REFERENCE PROCESSING SUMMARY:")
        logger.info(f"  Reference objects fetched: {list(ref_schemas.keys())}")
        logger.info(f"  Reference mappings created: {len(ref_obj_ai_mappings)}")
        for col, mapping in ref_obj_ai_mappings.items():
            logger.info(f"    {col} → {mapping['ref_object_name']}.{mapping['field_name']}")
        logger.info("=" * 60)
        
        return ref_schemas, ref_obj_ai_mappings
        
    except Exception as e:
        logger.error(f"Failed to process reference mappings: {e}")
        import traceback
        traceback.print_exc()
        raise