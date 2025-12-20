"""
CSV file upload endpoint. 
This router handles uploading CSV files that will be used for import operations. 
Files are saved to a dir accessible by the CDATA system. 
"""
import os
import shutil
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict, Any
from app.core.config import config
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

@router.post("/csv")
async def upload_csv(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload a CSV file for import operations.
    
    The file will be saved to the configured upload directory where
    the CDATA system can access it for imports.
    
    Args:
        file: The CSV file to upload
        
    Returns:
        Dictionary containing:
        - message: Success message
        - filename: The uploaded filename
        - path: Full path where file was saved
        
    Raises:
        HTTPException 400: If file is not a CSV
        HTTPException 500: If file upload fails
        
    Example:
        POST /upload/csv
        Content-Type: multipart/form-data
        
        Response:
        {
            "message": "File uploaded successfully",
            "filename": "employees.csv",
            "path": "C:\\...\\ImportFiles\\employees.csv"
        }
    """
    try: 
        # Validate file exits
        if not file:
            raise HTTPException(
                status_code=400, 
                detail="No file provided"
            )
        
        # Validate filename exists
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="File must have filename"
            )
        
        if not file.filename.lower().endswith('.csv'):
            logger.warning(f"Rejected non-CSV file: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are allowed"
            )
        
        logger.info(f"Uploading CSV file: {file.filename}")

        # Ensure upload directory exists
        upload_dir = Path(config.UPLOAD_DIRECTORY)
        # Ensure upload directory exists
        upload_dir = Path(config.UPLOAD_DIRECTORY)
        try:
            upload_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Upload directory ready: {upload_dir}")
        except Exception as e:
            logger.error(f"Failed to create upload directory: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create upload directory: {str(e)}"
            )
        
        # Create full file path
        file_path = upload_dir / file.filename

        # Check if file already exists
        if file_path.exists():
            logger.warning(f"FIle already exists, will overwrite: {file_path}")

        # Save the file
        try: 
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            logger.info(f"FIle saved successfully: {file_path}")

            return {
                "message": "File uploaded successfully",
                "filename": file.filename,
                "path": str(file_path)
            }
        
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error during file upload: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )
    finally: 
        # Always close the file
        if file:
            await file.close()