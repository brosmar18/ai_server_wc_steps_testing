"""
Step 10: Build Final Response

This script tests building the final ImportParamsResponse that gets returned to
the user, containing all mapping information and import results.

This corresponds to lines 265-278 in app/api/routers/import_builder.py:
    response = ImportParamsResponse(
        object_name=object_name,
        file_name=file.filename,
        columns=columns,
        fields=formatted_fields,
        mappings=all_mappings_dict,
        ref_obj_fields=ref_obj_fields,
        ref_obj_ai_mappings=ref_obj_ai_mappings,
        import_params=import_params,
        import_result=import_result,
        field_count=len(formatted_fields),
        mapping_count=len(all_mappings_dict)
    )

Requirements:
    - Step 9 results (import_result and all previous data)

Outputs:
    - Complete ImportParamsResponse Pydantic model with:
      * object_name, file_name, columns
      * fields (formatted CDATA fields)
      * mappings (complete mapping dictionary)
      * ref_obj_fields (reference object schemas)
      * ref_obj_ai_mappings (reference lookup mappings)
      * import_params (complete CDATA import configuration)
      * import_result (result of CDATA import creation)
      * field_count, mapping_count (summary counts)
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.import_params import ImportParamsResponse
from app.core.logging_config import get_logger, setup_logging
import logging

# Setup logging
setup_logging(level=logging.INFO)
logger = get_logger(__name__)


def main():
    """
    Main test function for Step 10: Build Final Response
    """
    print("\n" + "="*60)
    print("Step 10: Build Final Response")
    print("="*60 + "\n")

    # Define paths
    test_results_dir = Path(__file__).parent.parent / "test_results"
    step9_results_file = test_results_dir / "step_9_cdata_import.json"
    step10_results_file = test_results_dir / "step_10_final_response.json"

    # We also need data from earlier steps for formatted_fields and ref_obj_fields
    step5d_results_file = test_results_dir / "step_5d_mappings_separated.json"
    step6b_results_file = test_results_dir / "step_6b_reference_mappings.json"
    step7_results_file = test_results_dir / "step_7_final_mappings.json"

    # Ensure test_results directory exists
    test_results_dir.mkdir(exist_ok=True)

    # Initialize result structure
    result = {
        "step": "Step 10: Build Final Response",
        "step_number": "10",
        "success": False,
        "timestamp": "",
        "data": {},
        "errors": []
    }

    try:
        # ============================================================
        # Load Step 9 Results
        # ============================================================
        print("Loading Step 9 results...")
        logger.info("Loading Step 9 results")

        if not step9_results_file.exists():
            raise FileNotFoundError(
                f"Step 9 results not found at {step9_results_file}. "
                "Please run 9_create_import_in_cdata.py first."
            )

        with open(step9_results_file, 'r') as f:
            step9_data = json.load(f)

        if not step9_data.get('success'):
            raise ValueError("Step 9 did not complete successfully")

        print(f"✓ Loaded Step 9 results")
        logger.info("Step 9 results loaded successfully")

        # ============================================================
        # Load Additional Data from Earlier Steps
        # ============================================================
        print("Loading additional data from earlier steps...")
        logger.info("Loading additional data from earlier steps")

        # Load Step 5d for formatted_fields
        with open(step5d_results_file, 'r') as f:
            step5d_data = json.load(f)

        # Load Step 6b for ref_obj_fields
        with open(step6b_results_file, 'r') as f:
            step6b_data = json.load(f)

        # Load Step 7 for all_mappings_dict
        with open(step7_results_file, 'r') as f:
            step7_data = json.load(f)

        print(f"✓ Loaded data from Steps 5d, 6b and 7")
        logger.info("Loaded data from Steps 5d, 6b and 7")

        # ============================================================
        # Extract All Required Data
        # ============================================================
        print("\nExtracting all data for final response...")
        logger.info("Extracting all data for final response")

        object_name = step9_data['data']['object_name']
        file_name = step9_data['data']['file_name']
        columns = step9_data['data']['columns']
        import_params = step9_data['data']['import_params']
        import_result = step9_data['data']['import_result']

        # From Step 5d
        formatted_fields = step5d_data['data']['formatted_fields']

        # From Step 6b
        ref_obj_fields = step6b_data['data']['ref_schemas']
        ref_obj_ai_mappings = step6b_data['data']['ref_obj_ai_mappings']

        # From Step 7
        all_mappings_dict = step7_data['data']['all_mappings_dict']

        print(f"✓ Object: {object_name}")
        print(f"✓ File: {file_name}")
        print(f"✓ Columns: {len(columns)}")
        print(f"✓ Fields: {len(formatted_fields)}")
        print(f"✓ Mappings: {len(all_mappings_dict)}")
        logger.info(f"Extracted all data for {object_name}")

        # ============================================================
        # Step 10: Build Final Response
        # ============================================================
        print("\nBuilding final ImportParamsResponse...")
        logger.info("Building final ImportParamsResponse")

        # This matches lines 266-278 in import_builder.py
        response = ImportParamsResponse(
            object_name=object_name,
            file_name=file_name,
            columns=columns,
            fields=formatted_fields,
            mappings=all_mappings_dict,
            ref_obj_fields=ref_obj_fields,
            ref_obj_ai_mappings=ref_obj_ai_mappings,
            import_params=import_params,
            import_result=import_result,
            field_count=len(formatted_fields),
            mapping_count=len(all_mappings_dict)
        )

        print(f"✓ Built final response")
        print(f"  Field Count: {response.field_count}")
        print(f"  Mapping Count: {response.mapping_count}")
        logger.info(f"Built final response with {response.mapping_count} mappings")

        # Convert Pydantic model to dict for storage
        response_dict = response.model_dump()

        # ============================================================
        # Store Results
        # ============================================================
        print("\nStoring final response...")
        logger.info("Storing final response")

        # Store the complete response
        result["data"] = {
            # The complete final response (all fields)
            "final_response": response_dict,
            # Summary statistics
            "object_name": object_name,
            "file_name": file_name,
            "field_count": response.field_count,
            "mapping_count": response.mapping_count,
            "reference_object_count": len(ref_obj_fields),
            "import_created": import_result.get('success', False) if import_result else False
        }

        result["success"] = True
        result["timestamp"] = datetime.now().isoformat()

        # Save results to JSON file
        with open(step10_results_file, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"✓ Results saved to {step10_results_file}")
        logger.info(f"Results saved to {step10_results_file}")

        # ============================================================
        # Display Summary
        # ============================================================
        print("\n" + "="*80)
        print("Step 10 Summary - FINAL RESPONSE")
        print("="*80)
        print(f"Success: {result['success']}")
        print(f"Object: {object_name}")
        print(f"File: {file_name}")
        print(f"Total Columns: {len(columns)}")
        print(f"Total Fields: {response.field_count}")
        print(f"Total Mappings: {response.mapping_count}")
        print(f"Reference Objects: {list(ref_obj_fields.keys())}")
        print(f"Import Created in CDATA: {import_result.get('success', False) if import_result else False}")

        print("\n" + "="*80)
        print("Final Response Structure")
        print("="*80)
        print("Top-level keys:")
        for key in response_dict.keys():
            value = response_dict[key]
            if isinstance(value, dict):
                print(f"  - {key}: dict with {len(value)} keys")
            elif isinstance(value, list):
                print(f"  - {key}: list with {len(value)} items")
            else:
                print(f"  - {key}: {type(value).__name__}")

        print("\nResponse Contents:")
        print("-" * 80)
        print(f"object_name: {response.object_name}")
        print(f"file_name: {response.file_name}")
        print(f"columns: {len(response.columns)} columns")
        print(f"fields: {len(response.fields)} CDATA fields")
        print(f"mappings: {len(response.mappings)} column-to-field mappings")
        print(f"ref_obj_fields: {len(response.ref_obj_fields)} reference object schemas")
        print(f"ref_obj_ai_mappings: {len(response.ref_obj_ai_mappings)} reference mappings")
        print(f"import_params: {len(response.import_params.get('params', {}).get('fieldOverrides', []))} field overrides")
        print(f"import_result: {'Success' if response.import_result and response.import_result.get('success') else 'Failed/None'}")
        print(f"field_count: {response.field_count}")
        print(f"mapping_count: {response.mapping_count}")

        print("-" * 80)
        print(f"\n✓ Step 10 completed successfully!")
        print("\nThis ImportParamsResponse contains everything needed for the import:")
        print("  • AI-generated field mappings")
        print("  • CDATA import configuration")
        print("  • Reference object schemas and lookups")
        print("  • CDATA import creation result")
        print("="*80 + "\n")

        logger.info("Step 10 completed successfully")

    except FileNotFoundError as e:
        result["success"] = False
        result["timestamp"] = datetime.now().isoformat()
        result["errors"].append(str(e))
        print(f"\n✗ Error: {e}")
        logger.error(f"File not found: {e}")

        # Save error result
        with open(step10_results_file, 'w') as f:
            json.dump(result, f, indent=2)

        sys.exit(1)

    except Exception as e:
        result["success"] = False
        result["timestamp"] = datetime.now().isoformat()
        result["errors"].append(str(e))
        print(f"\n✗ Error in Step 10: {e}")
        logger.error(f"Step 10 failed: {e}", exc_info=True)

        # Save error result
        with open(step10_results_file, 'w') as f:
            json.dump(result, f, indent=2)

        raise


if __name__ == "__main__":
    main()