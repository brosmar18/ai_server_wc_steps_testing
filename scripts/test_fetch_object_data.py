"""
Test script to verify CDATA API object data fetching works.

This demonstrates:
- How to use fetch_object_data function directly
- That the API connection works
- That error handling works correctly
"""

import sys
from pathlib import Path
import json

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging_config import setup_logging, get_logger
from app.clients.cdata.object_operations import fetch_object_data, CDataAPIError

setup_logging()
logger = get_logger("test_fetch_object_data")


def test_fetch_object_data():
    """Test fetching object data from CDATA API"""
    print("\n" + "="*60)
    print("Testing CDATA API - Fetch Object Data")
    print("="*60 + "\n")
    
    try:
        # Test with a real object name
        # Change this to an object that exists in your CDATA system
        object_name = "employee"  # Common object - change if needed
        
        logger.info(f"Testing fetch_object_data with object: {object_name}")
        
        # Fetch the data
        fields = fetch_object_data(object_name)
        
        # Verify we got data
        assert isinstance(fields, list), "Response should be a list"
        assert len(fields) > 0, f"No fields returned for object: {object_name}"
        
        logger.info(f"✓ Successfully fetched {len(fields)} fields")
        
        # Display first few fields
        print("\n" + "-"*60)
        print(f"First 3 fields from '{object_name}':")
        print("-"*60)
        for i, field in enumerate(fields[:3], 1):
            print(f"\nField {i}:")
            print(json.dumps(field, indent=2))
        
        print("\n" + "="*60)
        print("✓ Fetch object data test completed successfully")
        print("="*60 + "\n")
        
        return True
        
    except CDataAPIError as e:
        print(f"\n✗ CDATA API error: {e}")
        print("\nPossible issues:")
        print("  - Check your .env file has correct CDATA_API_BASE")
        print("  - Check your CDATA_USERNAME and CDATA_PASSWORD")
        print("  - Check that the object name exists in your system")
        print("  - Check network connectivity to CDATA server\n")
        return False
        
    except ValueError as e:
        print(f"\n✗ Validation error: {e}\n")
        return False
        
    except AssertionError as e:
        print(f"\n✗ Test assertion failed: {e}")
        print(f"Try a different object name (current: {object_name})\n")
        return False
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_fetch_object_data()
    sys.exit(0 if success else 1)