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
from app.core.config import config
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/ai_import",
    tags=["import"]
)


def parse_csv_columns(file_path: Path) -> list[str]:
    """
    Parse CSV file to extract column names from the header row.

    """
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)  # Get first row
            
            # Strip whitespace from column names
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
    This endpoint handles the complete workflow:
    1. Validates and saves the CSV file
    2. Parses columns from the CSV header
    3. Fetches object field definitions from CDATA
    4. Formats the fields into a clean structure
    5. Uses AI to map CSV columns to fields
    6. Returns the complete mapping information
    
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
        
        # Step 5: Run AI mapping
        logger.info("Step 5: Running AI mapping agent...")
        final_mappings, ref_mappings = await run_parent_mapping(
            columns=columns,
            fields=formatted_fields
        )
        logger.info(f"AI generated {len(final_mappings)} final mappings and {len(ref_mappings)} reference mappings")
        
        # Step 6: Build response
        mappings_dict = {
            m["column"]: {
                "column": m["column"],
                "fieldName": m["fieldName"],
                "fieldType": m["fieldType"]
            }
            for m in final_mappings
        }
        
        logger.info("Step 6: Building response...")
        response = ImportParamsResponse(
            object_name=object_name,
            file_name=file.filename,
            columns=columns,
            fields=formatted_fields,
            mappings=mappings_dict,
            ref_obj_fields={},  
            ref_obj_ai_mappings={},  
            import_params={"params": {}},  
            field_count=len(formatted_fields),
            mapping_count=len(final_mappings)
        )
        
        logger.info(f"Successfully processed import for {object_name}")
        logger.info(f"Total mappings: {response.mapping_count}")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
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
        # Close the uploaded file
        if file:
            await file.close()