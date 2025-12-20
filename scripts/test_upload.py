"""
Test script to verify CSV upload endpoint works.

This demonstrates:
- How to create a test CSV file
- How to upload it using httpx
- That validation works correctly
"""

import sys
from pathlib import Path
import httpx
from io import BytesIO

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger("test_upload")

API_BASE = "http://localhost:8000"


def create_test_csv() -> BytesIO:
    """Create a simple test CSV in memory"""
    csv_content = """Employee Number,First Name,Last Name,Job Title
001,John,Doe,Software Engineer
002,Jane,Smith,Product Manager
003,Bob,Johnson,Designer
"""
    return BytesIO(csv_content.encode('utf-8'))


def test_upload_csv():
    """Test uploading a valid CSV file"""
    print("\n" + "="*60)
    print("Testing CSV Upload Endpoint")
    print("="*60 + "\n")
    
    try:
        logger.info("Creating test CSV file...")
        csv_file = create_test_csv()
        
        logger.info("Uploading CSV file...")
        
        # Upload the file
        files = {
            'file': ('test_employees.csv', csv_file, 'text/csv')
        }
        
        response = httpx.post(
            f"{API_BASE}/upload/csv",
            files=files,
            timeout=30.0
        )
        
        # Check response
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"✓ Upload successful: {data['filename']}")
        logger.info(f"✓ File saved to: {data['path']}")
        
        print("\n" + "-"*60)
        print("Upload Response:")
        print("-"*60)
        print(f"Message: {data['message']}")
        print(f"Filename: {data['filename']}")
        print(f"Path: {data['path']}")
        
        print("\n" + "="*60)
        print("✓ CSV upload test completed successfully")
        print("="*60 + "\n")
        
        return True
        
    except httpx.HTTPStatusError as e:
        print(f"\n✗ Upload failed with HTTP error: {e.response.status_code}")
        print(f"Response: {e.response.text}\n")
        return False
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_upload_non_csv():
    """Test that non-CSV files are rejected"""
    print("\n" + "="*60)
    print("Testing Non-CSV File Rejection")
    print("="*60 + "\n")
    
    try:
        logger.info("Attempting to upload non-CSV file...")
        
        # Create a fake Excel file
        fake_file = BytesIO(b"fake excel content")
        
        files = {
            'file': ('test.xlsx', fake_file, 'application/vnd.ms-excel')
        }
        
        response = httpx.post(
            f"{API_BASE}/upload/csv",
            files=files,
            timeout=30.0
        )
        
        # This should fail
        if response.status_code == 400:
            logger.info("✓ Non-CSV file correctly rejected")
            print("\n" + "="*60)
            print("✓ Non-CSV rejection test completed successfully")
            print("="*60 + "\n")
            return True
        else:
            print(f"✗ Expected 400 error, got {response.status_code}")
            return False
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("CSV Upload Endpoint Tests")
    print("="*60)
    print("\nMake sure the server is running: python main.py")
    print("="*60)
    
    # Run both tests
    test1_success = test_upload_csv()
    test2_success = test_upload_non_csv()
    
    overall_success = test1_success and test2_success
    sys.exit(0 if overall_success else 1)