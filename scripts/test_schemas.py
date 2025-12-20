"""
Test script to verify Pydantic schemas work correctly.

This demonstrates:
- How to create and validate schema instances
- That validation catches invalid data
- That schemas serialize/deserialize correctly
"""

import sys
from pathlib import Path
import json

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging_config import setup_logging, get_logger
from app.schemas.import_params import ImportParamsRequest, ImportParamsResponse
from pydantic import ValidationError

setup_logging()
logger = get_logger("test_schemas")


def test_import_params_request():
    """Test ImportParamsRequest validation"""
    print("\n" + "="*60)
    print("Testing ImportParamsRequest Schema")
    print("="*60 + "\n")
    
    try:
        # Test 1: Valid request
        logger.info("Test 1: Valid request...")
        valid_request = ImportParamsRequest(
            object_name="employee",
            file_name="employees.csv",
            columns=["Employee Number", "First Name", "Last Name"]
        )
        logger.info(f"✓ Valid request created: {valid_request.object_name}")
        
        # Verify data
        assert valid_request.object_name == "employee"
        assert valid_request.file_name == "employees.csv"
        assert len(valid_request.columns) == 3
        
        # Test JSON serialization
        json_str = valid_request.model_dump_json()
        logger.info(f"✓ JSON serialization works")
        
        # Test JSON deserialization
        parsed = ImportParamsRequest.model_validate_json(json_str)
        assert parsed.object_name == valid_request.object_name
        logger.info(f"✓ JSON deserialization works")
        
        print("\n" + "-"*60)
        print("Valid Request JSON:")
        print("-"*60)
        print(json.dumps(json.loads(json_str), indent=2))
        
        # Test 2: Invalid - empty object_name
        logger.info("\nTest 2: Invalid empty object_name...")
        try:
            ImportParamsRequest(
                object_name="   ",
                file_name="test.csv",
                columns=["col1"]
            )
            print("✗ Should have raised validation error for empty object_name")
            return False
        except ValidationError as e:
            logger.info(f"✓ Correctly rejected empty object_name")
        
        # Test 3: Invalid - non-CSV file
        logger.info("Test 3: Invalid file extension...")
        try:
            ImportParamsRequest(
                object_name="employee",
                file_name="employees.xlsx",
                columns=["col1"]
            )
            print("✗ Should have raised validation error for non-CSV file")
            return False
        except ValidationError as e:
            logger.info(f"✓ Correctly rejected non-CSV file")
        
        # Test 4: Invalid - empty columns
        logger.info("Test 4: Invalid empty columns...")
        try:
            ImportParamsRequest(
                object_name="employee",
                file_name="test.csv",
                columns=[]
            )
            print("✗ Should have raised validation error for empty columns")
            return False
        except ValidationError as e:
            logger.info(f"✓ Correctly rejected empty columns")
        
        # Test 5: Whitespace trimming
        logger.info("Test 5: Whitespace trimming...")
        trimmed_request = ImportParamsRequest(
            object_name="  employee  ",
            file_name="  test.csv  ",
            columns=["  col1  ", "  col2  "]
        )
        assert trimmed_request.object_name == "employee"
        assert trimmed_request.file_name == "test.csv"
        assert trimmed_request.columns == ["col1", "col2"]
        logger.info(f"✓ Whitespace trimming works")
        
        print("\n" + "="*60)
        print("✓ ImportParamsRequest tests completed successfully")
        print("="*60 + "\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ Test assertion failed: {e}\n")
        return False
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_import_params_response():
    """Test ImportParamsResponse validation"""
    print("\n" + "="*60)
    print("Testing ImportParamsResponse Schema")
    print("="*60 + "\n")
    
    try:
        # Test: Valid response
        logger.info("Test: Valid response...")
        valid_response = ImportParamsResponse(
            object_name="employee",
            file_name="employees.csv",
            columns=["Employee Number", "First Name"],
            fields=[
                {
                    "field_name": "empno",
                    "field_label": "Emp No",
                    "field_type": "string",
                    "whats_this": "Employee Number"
                },
                {
                    "field_name": "fname",
                    "field_label": "First Name",
                    "field_type": "string",
                    "whats_this": "Employee first name"
                }
            ],
            mappings={
                "Employee Number": {
                    "column": "Employee Number",
                    "field_name": "empno",
                    "field_type": "string"
                },
                "First Name": {
                    "column": "First Name",
                    "field_name": "fname",
                    "field_type": "string"
                }
            },
            field_count=45,
            mapping_count=2
        )
        
        logger.info(f"✓ Valid response created")
        
        # Verify data
        assert valid_response.object_name == "employee"
        assert valid_response.field_count == 45
        assert valid_response.mapping_count == 2
        assert len(valid_response.fields) == 2
        assert len(valid_response.mappings) == 2
        
        # Test JSON serialization
        json_str = valid_response.model_dump_json()
        logger.info(f"✓ JSON serialization works")
        
        print("\n" + "-"*60)
        print("Valid Response JSON (first 500 chars):")
        print("-"*60)
        print(json_str[:500] + "...")
        
        print("\n" + "="*60)
        print("✓ ImportParamsResponse tests completed successfully")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run both tests
    test1_success = test_import_params_request()
    test2_success = test_import_params_response()
    
    overall_success = test1_success and test2_success
    sys.exit(0 if overall_success else 1)