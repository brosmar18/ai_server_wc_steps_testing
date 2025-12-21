"""
Test script to verify AI mapping agent works correctly.

This demonstrates:
- How to create the AI agent
- How to run mappings with test data
- That the agent returns valid structured output
"""

import sys
from pathlib import Path
import json
import asyncio

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging_config import setup_logging, get_logger
from app.services.mapping.parent_mapper import run_parent_mapping

setup_logging()
logger = get_logger("test_mapping_agent")


async def test_mapping_agent():
    """Test AI mapping agent with sample data"""
    print("\n" + "="*60)
    print("Testing AI Mapping Agent")
    print("="*60 + "\n")
    
    try:
        # Sample CSV columns (like what we'd get from a real CSV)
        columns = [
            "Employee Number",
            "First Name",
            "Last Name",
            "Job Title",
            "Department"
        ]
        
        # Sample CDATA fields (like what we'd get from format_fields)
        fields = [
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
                "whats_this": "Enter the employee's first name"
            },
            {
                "field_name": "lname",
                "field_label": "Last Name",
                "field_type": "string",
                "whats_this": "Enter the employee's last name"
            },
            {
                "field_name": "emptitle",
                "field_label": "Primary Job Title",
                "field_type": "reference",
                "whats_this": "Select the Job Title for this employee.",
                "ref_object_name": "jobtitle"
            },
            {
                "field_name": "dept",
                "field_label": "Department",
                "field_type": "reference",
                "whats_this": "Select department",
                "ref_object_name": "department"
            }
        ]
        
        logger.info(f"Testing with {len(columns)} columns and {len(fields)} fields")
        
        print("\nInput Data:")
        print("-" * 60)
        print(f"Columns: {columns}")
        print(f"\nFields: {json.dumps(fields, indent=2)}")
        
        # Run the mapping
        logger.info("Running AI mapping agent...")
        final_mappings, ref_mappings = await run_parent_mapping(columns, fields)
        
        # Display results
        print("\n" + "="*60)
        print("AI Mapping Results")
        print("="*60)
        
        print("\n1. Non-Reference Field Mappings:")
        print("-" * 60)
        print(json.dumps(final_mappings, indent=2))
        
        print("\n2. Reference Field Mappings:")
        print("-" * 60)
        print(json.dumps(ref_mappings, indent=2))
        
        # Verify results
        total_mappings = len(final_mappings) + len(ref_mappings)
        assert total_mappings == len(columns), f"Expected {len(columns)} mappings, got {total_mappings}"
        
        logger.info("✓ All columns were mapped")
        
        # Verify specific mappings
        final_map_dict = {m["column"]: m for m in final_mappings}
        ref_map_dict = {m["column"]: m for m in ref_mappings}
        
        # Check non-reference mapping
        assert "Employee Number" in final_map_dict
        assert final_map_dict["Employee Number"]["fieldName"] == "empno"
        logger.info("✓ Non-reference mapping correct")
        
        # Check reference mapping
        assert "Job Title" in ref_map_dict
        assert ref_map_dict["Job Title"]["ref_obj_name"] == "jobtitle"
        logger.info("✓ Reference mapping correct")
        
        print("\n" + "="*60)
        print("✓ AI Mapping Agent test completed successfully")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mapping_agent())
    sys.exit(0 if success else 1)