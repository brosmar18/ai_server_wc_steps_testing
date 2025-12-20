"""
Test script to verify field formatting works correctly.

This demonstrates:
- How to use format_fields function
- That raw CDATA data is normalized correctly
- That reference fields are handled properly
- That error handling works
"""

import sys
from pathlib import Path
import json

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging_config import setup_logging, get_logger
from app.clients.cdata.formatters import format_fields

setup_logging()
logger = get_logger("test_formatters")


def test_format_fields():
    """Test formatting with sample CDATA data"""
    print("\n" + "="*60)
    print("Testing Field Formatting")
    print("="*60 + "\n")
    
    try:
        # Sample raw CDATA field data (mimics actual API response)
        raw_fields = [
            {
                "fieldName": "empno",
                "label": "Emp No",
                "fieldType": "string",
                "options": {
                    "title": "Employee Number"
                }
            },
            {
                "fieldName": "fname",
                "label": "First Name",
                "fieldType": "string",
                "options": {
                    "title": "Enter the employee's first name"
                }
            },
            {
                "fieldName": "lname",
                "label": "Last Name",
                "fieldType": "string",
                "options": {
                    "title": "Enter the employee's last name"
                }
            },
            {
                "fieldName": "emptitle",
                "label": "Primary Job Title",
                "fieldType": "reference",
                "options": {
                    "title": "Select the Job Title for this employee.",
                    "refObjects": [
                        {"name": "jobtitle"}
                    ]
                }
            },
            {
                "fieldName": "department",
                "label": "Department",
                "fieldType": "reference",
                "options": {
                    "title": "Select department",
                    "refObjects": [
                        {"name": "dept"}
                    ]
                }
            }
        ]
        
        logger.info("Formatting sample CDATA fields...")
        
        # Format the fields
        formatted = format_fields(raw_fields)
        
        # Verify results
        assert isinstance(formatted, list), "Result should be a list"
        assert len(formatted) == 5, f"Expected 5 fields, got {len(formatted)}"
        
        logger.info(f"✓ Successfully formatted {len(formatted)} fields")
        
        # Display results
        print("\n" + "-"*60)
        print("Formatted Fields:")
        print("-"*60)
        print(json.dumps(formatted, indent=2))
        
        # Verify structure of first field (string type)
        first_field = formatted[0]
        assert first_field["field_name"] == "empno"
        assert first_field["field_label"] == "Emp No"
        assert first_field["field_type"] == "string"
        assert first_field["whats_this"] == "Employee Number"
        assert "ref_object_name" not in first_field
        logger.info("✓ String field formatted correctly")
        
        # Verify structure of reference field
        ref_field = formatted[3]
        assert ref_field["field_name"] == "emptitle"
        assert ref_field["field_type"] == "reference"
        assert ref_field["ref_object_name"] == "jobtitle"
        logger.info("✓ Reference field formatted correctly")
        
        print("\n" + "="*60)
        print("✓ Field formatting test completed successfully")
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


def test_error_handling():
    """Test that error handling works correctly"""
    print("\n" + "="*60)
    print("Testing Formatter Error Handling")
    print("="*60 + "\n")
    
    try:
        # Test with invalid input (not a list)
        logger.info("Test: Invalid input type...")
        try:
            format_fields("not a list")
            print("✗ Should have raised ValueError for non-list input")
            return False
        except ValueError as e:
            logger.info(f"✓ Correctly raised ValueError: {e}")
        
        # Test with empty list
        logger.info("Test: Empty list...")
        result = format_fields([])
        assert isinstance(result, list), "Result should be a list"
        assert result == [], "Empty list should return empty list"
        logger.info("✓ Empty list handled correctly")
        
        # Test with malformed field (missing fieldName)
        logger.info("Test: Malformed field...")
        malformed = [{"label": "Test", "fieldType": "string"}]
        result = format_fields(malformed)
        
        # Verify it's a list
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 1, "Should still process malformed field"
        
        # Check the result
        field = result[0]
        assert isinstance(field, dict), "Field should be a dict"
        assert field["field_name"] is None, "Missing fieldName should be None"
        assert field["field_label"] == "Test", "Label should be preserved"
        logger.info("✓ Malformed field handled gracefully")
        
        print("\n" + "="*60)
        print("✓ Error handling test completed successfully")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error handling test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run both tests
    test1_success = test_format_fields()
    test2_success = test_error_handling()
    
    overall_success = test1_success and test2_success
    sys.exit(0 if overall_success else 1)