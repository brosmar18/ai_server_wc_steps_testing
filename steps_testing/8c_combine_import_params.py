import sys
from pathlib import Path
from datetime import datetime
import json

# -------------------------------------------------------------------
# Ensure project root is on PYTHONPATH
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# -------------------------------------------------------------------
# Result Builder
# -------------------------------------------------------------------

def build_step_8c_result() -> dict:
    return {
        "step": "Step 8c: Combine into Final Import Params",
        "step_number": "8c",
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "errors": [],
    }

# -------------------------------------------------------------------
# Load & Validate Step 8b
# -------------------------------------------------------------------

def load_step_8b_results(step_8b_file: Path) -> dict:
    print("\nLoading Step 8b results...")
    print(f"Step 8b results path: {step_8b_file}")

    if not step_8b_file.exists():
        raise FileNotFoundError(f"Step 8b results not found: {step_8b_file}")

    with open(step_8b_file, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_step_8b_success(step8b_data: dict, result: dict) -> None:
    print("\nValidating Step 8b success status...")

    if not step8b_data.get("success"):
        error = "Step 8b did not complete successfully"
        result["errors"].append(error)
        print(f"Validation failed: {error}")
        return

    print("Step 8b completed successfully.")

# -------------------------------------------------------------------
# Core Logic: Import Params Assembly
# -------------------------------------------------------------------

def build_import_params(field_overrides: list, import_metadata: dict) -> dict:
    """
    Assemble the final CDATA import params structure.

    Exact CDATA shape:
    {
      "params": {
        "fieldOverrides": [...],
        <import metadata keys>
      }
    }
    """
    print("\nBuilding import params structure...")

    params = {
        "params": {
            "fieldOverrides": field_overrides,
            **import_metadata,
        }
    }

    print("Import params structure built.")
    print(f"  Field Overrides: {len(field_overrides)}")
    print(f"  Metadata keys: {list(import_metadata.keys())}")

    return params

# -------------------------------------------------------------------
# Integration
# -------------------------------------------------------------------

def integrate_step_8c_data(step8b_data: dict, result: dict) -> None:
    data = step8b_data["data"]

    columns = data["columns"]
    field_overrides = data["field_overrides"]
    import_metadata = data["import_metadata"]

    # HARD INVARIANT — NO EXTRA COLUMNS
    if len(columns) != len(field_overrides):
        raise ValueError(
            f"Final import params mismatch: "
            f"{len(columns)} columns but {len(field_overrides)} field overrides"
        )

    import_params = build_import_params(
        field_overrides=field_overrides,
        import_metadata=import_metadata,
    )

    # Carry forward ALL data from Step 8b (maintains linear pipeline)
    result["data"] = dict(step8b_data["data"])

    # Add Step 8c outputs
    result["data"].update({
        "import_params": import_params,
        "params_keys": list(import_params["params"].keys()),
    })

# -------------------------------------------------------------------
# Finalization
# -------------------------------------------------------------------

def finalize_step_8c_success(result: dict) -> None:
    result["success"] = len(result["errors"]) == 0


def save_result_to_json(result: dict, output_file: Path) -> None:
    print("\nSaving Step 8c results...")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Results saved to: {output_file}")
    print(f"File size: {output_file.stat().st_size} bytes")

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main() -> int:
    print("=" * 80)
    print("TESTING STEP 8c: COMBINE INTO FINAL IMPORT PARAMS")
    print("PHASE 2: MANUAL PARAMS ASSEMBLY")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_8b_results = project_root / "test_results" / "step_8b_import_metadata.json"
    output_file = project_root / "test_results" / "step_8c_import_params.json"

    result = build_step_8c_result()

    try:
        step8b_data = load_step_8b_results(step_8b_results)
        validate_step_8b_success(step8b_data, result)

        if not result["errors"]:
            integrate_step_8c_data(step8b_data, result)

    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Unexpected error: {exc}")

    finalize_step_8c_success(result)
    save_result_to_json(result, output_file)

    print("\nFinal Step 8c result:")
    print(f"  Success: {result['success']}")
    print(f"  Params keys: {result['data'].get('params_keys')}")
    print(f"  Field overrides: {result['data'].get('field_overrides_count')}")
    print(f"  Errors: {result['errors']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
