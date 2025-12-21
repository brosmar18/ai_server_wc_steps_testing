"""
Test script to verify the upload-and-process endpoint works with import params.
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
    """Test the upload-and-process endpoint with import params"""
    print("\n" + "="*60)
    print("Testing Upload and Process Endpoint (Full Import Config)")
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
            timeout=120.0
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
        print("AI Mappings:")
        print("-"*60)
        for column, mapping in data_response['mappings'].items():
            if mapping.get('lookupFieldName'):
                print(f"{column} → {mapping['fieldName']} (reference: {mapping['refObjectName']}.{mapping['lookupFieldName']})")
            else:
                print(f"{column} → {mapping['fieldName']} ({mapping['fieldType']})")
        
        # Display import params (with safety check)
        import_params = data_response.get('import_params')
        if import_params and import_params.get('params'):  
            params = import_params['params']
            
            print("\n" + "-"*60)
            print("Import Configuration:")
            print("-"*60)
            print(f"Name: {params.get('importName', 'N/A')}")
            print(f"Description: {params.get('importDescription', 'N/A')}")
            
            if params.get('fieldOverrides'):
                print(f"\nField Overrides ({len(params['fieldOverrides'])} fields):")
                for override in params['fieldOverrides']:
                    col_num = override['col']
                    field_name = override['fieldName']
                    
                    if override.get('lookupRefObject'):
                        print(f"  Col {col_num}: {field_name} → {override['lookupRefObject']}.{override['lookupFieldName']}")
                    else:
                        print(f"  Col {col_num}: {field_name}")
            
            # Print full JSON
            print("\n" + "-"*60)
            print("Full Import Params JSON:")
            print("-"*60)
            print(json.dumps(import_params, indent=2))
        else:
            print("\n" + "-"*60)
            print("⚠ Import params not found in response")
            print("-"*60)
            print("Response keys:", list(data_response.keys()))
        
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
    print("Upload and Process Endpoint Test (Phase 11)")
    print("="*60)
    print("\nMake sure the server is running: python main.py")
    print("="*60)
    
    success = test_upload_and_process_endpoint()
    sys.exit(0 if success else 1)