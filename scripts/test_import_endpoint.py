"""
Test script to verify the upload-and-process endpoint works.

This demonstrates:
- How to call the upload-and-process endpoint
- That the full flow works (upload → parse → fetch → format → AI map)
- That the response matches expected structure
"""

import sys
from pathlib import Path
import json
import httpx
from io import BytesIO

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger("test_import_endpoint")

API_BASE = "http://localhost:8000"


def create_test_csv() -> BytesIO:
    """Create a test CSV file in memory"""
    csv_content = """Employee Number,First Name,Last Name,Email
001,John,Doe,john.doe@example.com
002,Jane,Smith,jane.smith@example.com
003,Bob,Johnson,bob.johnson@example.com
"""
    return BytesIO(csv_content.encode('utf-8'))


def test_upload_and_process_endpoint():
    """Test the upload-and-process endpoint"""
    print("\n" + "="*60)
    print("Testing Upload and Process Endpoint")
    print("="*60 + "\n")
    
    try:
        # Create test CSV
        logger.info("Creating test CSV file...")
        csv_file = create_test_csv()
        
        # Prepare multipart form data
        files = {
            'file': ('test_employees.csv', csv_file, 'text/csv')
        }
        
        data = {
            'object_name': 'employee'
        }
        
        logger.info(f"Testing with object: {data['object_name']}")
        logger.info(f"File: test_employees.csv")
        
        # Call the endpoint
        logger.info("Calling upload-and-process endpoint...")
        response = httpx.post(
            f"{API_BASE}/ai_import/upload-and-process",
            files=files,
            data=data,
            timeout=60.0  # AI calls can take a while
        )
        
        # Check response
        response.raise_for_status()
        data_response = response.json()
        
        logger.info(f"✓ Request successful")
        
        # Verify response structure
        assert "object_name" in data_response
        assert "file_name" in data_response
        assert "columns" in data_response
        assert "fields" in data_response
        assert "mappings" in data_response
        assert "field_count" in data_response
        assert "mapping_count" in data_response
        
        logger.info(f"✓ Response structure valid")
        
        # Display results
        print("\n" + "-"*60)
        print("Response Summary:")
        print("-"*60)
        print(f"Object: {data_response['object_name']}")
        print(f"File: {data_response['file_name']}")
        print(f"Columns: {len(data_response['columns'])}")
        print(f"Fields: {data_response['field_count']}")
        print(f"Mappings: {data_response['mapping_count']}")
        
        print("\n" + "-"*60)
        print("Columns Detected:")
        print("-"*60)
        for col in data_response['columns']:
            print(f"  - {col}")
        
        print("\n" + "-"*60)
        print("AI Mappings:")
        print("-"*60)
        for column, mapping in data_response['mappings'].items():
            print(f"{column} → {mapping['fieldName']} ({mapping['fieldType']})")
        
        print("\n" + "="*60)
        print("✓ Upload and process endpoint test completed successfully")
        print("="*60 + "\n")
        
        return True
        
    except httpx.HTTPStatusError as e:
        print(f"\n✗ HTTP error: {e.response.status_code}")
        print(f"Response: {e.response.text}\n")
        return False
        
    except AssertionError as e:
        print(f"\n✗ Response validation failed: {e}\n")
        return False
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Upload and Process Endpoint Test")
    print("="*60)
    print("\nMake sure the server is running: python main.py")
    print("="*60)
    
    success = test_upload_and_process_endpoint()
    sys.exit(0 if success else 1)