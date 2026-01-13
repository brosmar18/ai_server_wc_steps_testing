"""
Step 1: File Upload and Validation

Tests the CSV file upload and validation logic from the import workflow. 

This script validates: 
- Object name is provided and not empty
- File exits and is readable
- File has a .csv extension
- File can be copied to upload directory. 
"""
import sys
from pathlib import Path
from datetime import datetime
import shutil
import json


def build_step_1_result() -> dict:
     return {
         "step": "Step 1: File Upload and Validation",
         "step_number": 1,
         "success": False,
         "timestamp": datetime.now().isoformat(),
         "data": {},
         "errors": []
     }

def validate_object_name(object_name: str, result: dict) -> None:
    """
    Validate the object name.
    Rules: 
    - Must be provided.
    - Must not be empty after stripping.
    """
    if not object_name or not object_name.strip():
        error = "object_name is required"
        result["errors"].append(error)
        print(f"Validation failed: {error}")
        return
    
    cleaned_name = object_name.strip()
    result["data"]["object_name"] = cleaned_name
    print(f"Object name validated: {cleaned_name}")

def validate_csv_file_exists(csv_file_path: Path, result: dict) -> None:
    """
    Validate that the csv file exists at the given path.
    """
    print("\nValidating CSV file existance...")
    print(f"CSV path: {csv_file_path}")

    if not csv_file_path.exists():
        error = f"CSV file not found: {csv_file_path}"
        result["errors"].append(error)
        print(f"Validation failed: {error}")

    result["data"]["file_name"] = csv_file_path.name
    print("CSV file exists.")

def validate_csv_extension(csv_file_path: Path, result: dict) -> None:
    """
    Validates that the file has a .csv extension
    """
    print("\nValidating CSV file extension....")
    if not csv_file_path.name.lower().endswith(".csv"):
        error = "Only CSV files are allowed"
        result["errors"].append(error)
        print(f"Validation failed: {error}")

    print("CSV file extension validated.")


def validate_csv_file_readable(csv_file_path: Path, result: dict) -> None:
    """ 
    Validate that the cssv file can be opened and read.
    """

    try:
        with open(csv_file_path, "r", encoding="utf-8") as f:
            f.read(1)
        print("CSV file is readable")
    except Exception as exc:
        error = f"File is not readable: {exc}"
        result["errors"].append(error)
        print(f"Validation failed: {error}")


def ensure_upload_directory(upload_dir: Path, result: dict) -> None:
    """
    Ensure the upload directory exists. 
    """
    print("\nEnsuring upload directory exists...")
    try:
        upload_dir.mkdir(parents=True, exist_ok=True)
        result["data"]["upload_directory"] = str(upload_dir)
        print(f"Upload directory ready: {upload_dir}")


    except Exception as exc:
        error = f"Failed to create upload directory: {exc}"
        result["errors"].append(error)
        print(f"Directory creation failed: {error}")

def copy_csv_to_upload_dir(
        csv_file_path: Path, upload_dir: Path, result: dict
) -> None: 
    # Copy the csv file into the upload directory
    print("\nCopying CSV file to upload directory")

    try: 
        destination = upload_dir / csv_file_path.name
        shutil.copy2(csv_file_path, destination)

        result["data"]["file_path"] = str(destination)

        print(f"File copied to: {destination}")
        
    except Exception as exc:
        error = f"Failed to copy file: {exc}"
        result["errors"].append(error)
        print(f"File copy failed: {error}")


def finalize_step_success(result: dict) -> None:
    result["success"] = len(result["errors"]) == 0

def save_result_to_json(result: dict, output_file: Path) -> None:
    """
    Persist the Step 1 result to disk as JSON.
    """
    print("\nSaving Step 1 result to JSON...")

    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print(f"Result saved to: {output_file}")
        print(f"File size: {output_file.stat().st_size} bytes")
    except Exception as exc:
        print(f"Failed to save result file: {exc}")




def main() -> int:
    print("=" * 80)
    print("TESTING STEP 1: FILE UPLOAD & VALIDATION")
    print("=" * 80)
    
    project_root = Path(__file__).parent.parent
    csv_file = project_root / "test_data" / "sample_employees.csv"
    object_name = "emplolyee"
    upload_dir = project_root / "uploads"
    output_file = project_root / "test_results" / "step_1_file_upload.json"

    # Build Result
    result = build_step_1_result()

    # Apply single validation rule
    validate_object_name(object_name, result)
    validate_csv_file_exists(csv_file, result)
    validate_csv_extension(csv_file, result)
    validate_csv_file_readable(csv_file, result)

    if not result["errors"]:
        ensure_upload_directory(upload_dir, result)

    if not result["errors"]:
        copy_csv_to_upload_dir(csv_file, upload_dir, result)

    finalize_step_success(result)

    save_result_to_json(result, output_file)


    print("\nCurrent result state:")
    print(f"  Data: {result['data']}")
    print(f"  Errors: {result['errors']}")
    print(f"  Success: {result['success']}")

    return 0 if result["success"] else 1


if __name__=="__main__":
    exit_code = main()
    sys.exit(exit_code)