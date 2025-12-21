"""
Test script to verify the upload-and-process endpoint works with reference mappings.
"""

import sys
from pathlib import Path
import json
import httpx
from io import BytesIO

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger("test_import_endpoint")

API_BASE = "http://localhost:8000"


def create_test_csv_with_references() -> BytesIO:
    """Create a test CSV file with reference field columns"""
    csv_content = """Employee Number,First Name,Last Name,Email,Primary Job Title,Department
001,John,Doe,john.doe@example.com,Software Engineer,Engineering
002,Jane,Smith,jane.smith@example.com,Product Manager,Product
003,Bob,Johnson,bob.johnson@example.com,Designer,Design
"""
    return BytesIO(csv_content.encode('utf-8'))


def test_upload_and_process_endpoint():
    """Test the upload-and-process endpoint with reference fields"""
    print("\n" + "="*60)
    print("Testing Upload and Process Endpoint (with References)")
    print("="*60 + "\n")
    
    try:
        logger.info("Creating test CSV file with reference fields...")
        csv_file = create_test_csv_with_references()
        
        files = {
            'file': ('test_employees.csv', csv_file, 'text/csv')
        }
        
        data = {
            'object_name': 'employee'
        }
        
        logger.info(f"Testing with object: {data['object_name']}")
        
        logger.info("Calling upload-and-process endpoint...")
        response = httpx.post(
            f"{API_BASE}/ai_import/upload-and-process",
            files=files,
            data=data,
            timeout=120.0  # Longer timeout for reference processing
        )
        
        response.raise_for_status()
        data_response = response.json()
        
        logger.info(f"✓ Request successful")
        
        # Display results
        print("\n" + "-"*60)
        print("Response Summary:")
        print("-"*60)
        print(f"Object: {data_response['object_name']}")
        print(f"File: {data_response['file_name']}")
        print(f"Columns: {len(data_response['columns'])}")
        print(f"Fields: {data_response['field_count']}")
        print(f"Total Mappings: {data_response['mapping_count']}")
        
        print("\n" + "-"*60)
        print("Columns Detected:")
        print("-"*60)
        for col in data_response['columns']:
            print(f"  - {col}")
        
        print("\n" + "-"*60)
        print("AI Mappings:")
        print("-"*60)
        for column, mapping in data_response['mappings'].items():
            if mapping.get('lookupFieldName'):
                print(f"{column} → {mapping['fieldName']} (reference: {mapping['refObjectName']}.{mapping['lookupFieldName']})")
            else:
                print(f"{column} → {mapping['fieldName']} ({mapping['fieldType']})")
        
        # Display reference object info
        if data_response.get('ref_obj_fields'):
            print("\n" + "-"*60)
            print("Reference Objects Processed:")
            print("-"*60)
            for ref_obj, fields in data_response['ref_obj_fields'].items():
                print(f"{ref_obj}: {len(fields)} fields")
        
        if data_response.get('ref_obj_ai_mappings'):
            print("\n" + "-"*60)
            print("Reference Object AI Mappings:")
            print("-"*60)
            for column, ref_mapping in data_response['ref_obj_ai_mappings'].items():
                print(f"{column}:")
                print(f"  Parent Field: {ref_mapping['parent_field_name']}")
                print(f"  Lookup Field: {ref_mapping['ref_object_name']}.{ref_mapping['field_name']}")
        
        print("\n" + "="*60)
        print("✓ Upload and process endpoint test completed successfully")
        print("="*60 + "\n")
        
        return True
        
    except httpx.HTTPStatusError as e:
        print(f"\n✗ HTTP error: {e.response.status_code}")
        print(f"Response: {e.response.text}\n")
        return False
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Upload and Process Endpoint Test (Phase 10)")
    print("="*60)
    print("\nMake sure the server is running: python main.py")
    print("="*60)
    
    success = test_upload_and_process_endpoint()
    sys.exit(0 if success else 1)