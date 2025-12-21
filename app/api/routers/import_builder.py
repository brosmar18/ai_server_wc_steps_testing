"""
Import builder endpoint.

This router provides the main AI-powered import mapping endpoint
that handles CSV upload and mapping in a single request.
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import Dict, Any
from pathlib import Path
import shutil
import csv
from app.schemas.import_params import ImportParamsResponse
from app.clients.cdata.object_operations import fetch_object_data, CDataAPIError
from app.clients.cdata.formatters import format_fields
from app.services.mapping.parent_mapper import run_parent_mapping
from app.services.mapping.reference_mapper import process_all_reference_mappings
from app.services.import_config.params_builder import build_import_params  # NEW
from app.core.config import config
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/ai_import",
    tags=["import"]
)


def parse_csv_columns(file_path: Path) -> list[str]:
    """Parse CSV file to extract column names from the header row."""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            columns = [col.strip() for col in header if col.strip()]
            
            if not columns:
                raise ValueError("CSV file has no valid columns")
            
            logger.info(f"Parsed {len(columns)} columns from CSV")
            return columns
            
    except StopIteration:
        raise ValueError("CSV file is empty")
    except Exception as e:
        logger.error(f"Failed to parse CSV columns: {e}")
        raise ValueError(f"Failed to parse CSV: {str(e)}")


@router.post("/upload-and-process")
async def upload_and_process(
    file: UploadFile = File(...),
    object_name: str = Form(...)
) -> ImportParamsResponse:
    """
    Upload CSV and generate AI-powered import mappings in a single request.
    
    This endpoint handles the complete workflow:
    1. Validates and saves the CSV file
    2. Parses columns from the CSV header
    3. Fetches object field definitions from CDATA
    4. Formats the fields into a clean structure
    5. Uses AI to map CSV columns to fields
    6. Processes reference field mappings
    7. Builds import configuration (NEW in Phase 11)
    8. Returns the complete mapping information
    """
    temp_file_path = None
    
    try:
        logger.info(f"Upload and process request for object: {object_name}")
        
        # Validate inputs
        if not object_name or not object_name.strip():
            raise HTTPException(status_code=400, detail="object_name is required")
        
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="CSV file is required")
        
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        object_name = object_name.strip()
        logger.info(f"File: {file.filename}")
        
        # Step 1: Save the CSV file
        logger.info("Step 1: Saving CSV file...")
        upload_dir = Path(config.UPLOAD_DIRECTORY)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        temp_file_path = file_path
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved: {file_path}")
        
        # Step 2: Parse columns from CSV
        logger.info("Step 2: Parsing CSV columns...")
        columns = parse_csv_columns(file_path)
        logger.info(f"Parsed columns: {columns}")
        
        # Step 3: Fetch object fields from CDATA
        logger.info("Step 3: Fetching object fields from CDATA...")
        raw_fields = fetch_object_data(object_name)
        logger.info(f"Fetched {len(raw_fields)} raw fields")
        
        # Step 4: Format the fields
        logger.info("Step 4: Formatting fields...")
        formatted_fields = format_fields(raw_fields)
        logger.info(f"Formatted {len(formatted_fields)} fields")
        
        # Step 5: Run AI mapping for parent object
        logger.info("Step 5: Running AI mapping agent for parent object...")
        final_mappings, ref_mappings = await run_parent_mapping(
            columns=columns,
            fields=formatted_fields
        )
        logger.info(f"AI generated {len(final_mappings)} final mappings and {len(ref_mappings)} reference mappings")
        
        # Step 6: Process reference field mappings
        ref_obj_fields = {}
        ref_obj_ai_mappings = {}
        
        if ref_mappings:
            logger.info("Step 6: Processing reference object mappings...")
            ref_obj_fields, ref_obj_ai_mappings = await process_all_reference_mappings(ref_mappings)
            logger.info(f"Processed {len(ref_obj_ai_mappings)} reference object mappings")
        else:
            logger.info("Step 6: No reference mappings to process")
        
        # Step 7: Build final mappings dictionary
        logger.info("Step 7: Building final mappings...")
        
        # Combine final and reference mappings
        all_mappings_dict = {}
        
        # Add non-reference mappings
        for m in final_mappings:
            all_mappings_dict[m["column"]] = {
                "column": m["column"],
                "fieldName": m["fieldName"],
                "fieldType": m["fieldType"]
            }
        
        # Add reference mappings with lookup field info
        for column, ref_mapping in ref_obj_ai_mappings.items():
            all_mappings_dict[column] = {
                "column": column,
                "fieldName": ref_mapping["parent_field_name"],
                "fieldType": "reference",
                "refObjectName": ref_mapping["ref_object_name"],
                "lookupFieldName": ref_mapping["field_name"]
            }
        
        # Step 8: Build import params configuration (NEW!)
        logger.info("Step 8: Building import params configuration...")
        import_params = build_import_params(
            object_name=object_name,
            file_name=file.filename,
            columns=columns,
            mappings=all_mappings_dict,
            ref_obj_ai_mappings=ref_obj_ai_mappings
        )
        logger.info("Import params configuration built successfully")
        
        # Step 9: Build response
        logger.info("Step 9: Building response...")
        response = ImportParamsResponse(
            object_name=object_name,
            file_name=file.filename,
            columns=columns,
            fields=formatted_fields,
            mappings=all_mappings_dict,
            ref_obj_fields=ref_obj_fields,
            ref_obj_ai_mappings=ref_obj_ai_mappings,
            import_params=import_params,  # Now populated!
            field_count=len(formatted_fields),
            mapping_count=len(all_mappings_dict)
        )
        
        logger.info(f"Successfully processed import for {object_name}")
        logger.info(f"Total mappings: {response.mapping_count}")
        logger.info(f"Reference objects: {list(ref_obj_fields.keys())}")
        logger.info(f"Import params: {import_params['params']['importName']}")
        
        return response
        
    except HTTPException:
        raise
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except CDataAPIError as e:
        logger.error(f"CDATA API error: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch data from CDATA API: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    
    finally:
        if file:
            await file.close()