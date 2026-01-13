import sys
from pathlib import Path
from datetime import datetime
import json
import csv


def build_step_2_result() -> dict:
    return {
        "step": "Step 2: CSV Column Parsing",
        "step_number": 2,
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "errors": [],
    }


def load_step_1_results(step_1_file: Path) -> dict:
    print("\nLoading Step 1 results...")
    print(f"Step 1 results path: {step_1_file}")

    if not step_1_file.exists():
        raise FileNotFoundError(f"Step 1 results not found: {step_1_file}")

    with open(step_1_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Step 1 results loaded successfully.")
    return data


def validate_step_1_success(step1_data: dict, result: dict) -> None:
    print("\nValidating Step 1 success status...")

    if not step1_data.get("success"):
        error = "Step 1 did not complete successfully"
        result["errors"].append(error)
        print(f"Validation failed: {error}")
        return

    print("Step 1 completed successfully.")

def parse_csv_columns(csv_file_path: Path) -> list[str]:

    print("\nParsing CSV header...")
    print(f"CSV FIle path: {csv_file_path}")

    try: 
        with open(csv_file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)

        columns = [col.strip() for col in header if col.strip()]

        if not columns:
            raise ValueError("CSV file has not valid columns")
        
        print(f"Parsed {len(columns)} columns:")
        print(columns)

        return columns
    


    except StopIteration:
        raise ValueError("CSV File is empty")
    except Exception as exc:
        raise ValueError(f"Failed to parse CSV: {exc}")

def integrate_step_2_data(step1_data: dict, columns: list[str], result: dict) -> None:

    result["data"] = {
        "object_name": step1_data["data"]["object_name"],
        "file_name": step1_data["data"]["file_name"],
        "file_path": step1_data["data"]["file_path"],
        "columns": columns
    }

    print("\nIntegrated Step 2 data:")
    print(f"  Object Name: {result['data']['object_name']}")
    print(f"  File Name: {result['data']['file_name']}")
    print(f"  File Path: {result['data']['file_path']}")
    print(f"  Columns ({len(columns)}): {columns}")


def finalize_step_suecess(result: dict) -> None:
    result["success"] = len(result["errors"]) == 0


def save_result_to_json(result: dict, output_file: Path) -> None:
    print("\nSaving Step 2 results to JSON...")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Result saved to: {output_file}")
    print(f"File Size: {output_file.stat().st_size} bytes")



def main() -> None:
    print("=" * 80)
    print("TESTING STEP 2: CSV COLUMN PARSING")
    print("=" * 80)

    project_root = Path(__file__).parent.parent
    step_1_results = project_root / "test_results" / "step_1_file_upload.json"
    output_file = project_root / "test_results" / "step_2_csv_parsing.json"

    result = build_step_2_result()

    try:
        step1_data = load_step_1_results(step_1_results)
        validate_step_1_success(step1_data, result)

        if not result["errors"]:
            csv_path = Path(step1_data["data"]["file_path"])
            columns = parse_csv_columns(csv_path)
            integrate_step_2_data(step1_data, columns, result)


    except Exception as exc:
        result["errors"].append(str(exc))
        print(f"Unexpected error: {exc}")

    finalize_step_suecess(result)
    save_result_to_json(result, output_file)

    print("\nFinal Step 2 result:")
    print(f"  Success: {result['success']}")
    print(f"  Errors: {result['errors']}")

if __name__ == "__main__":
    main()
    sys.exit(0)
