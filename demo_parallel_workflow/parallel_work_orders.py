"""
Fleet Management - Parallel Work Order Processing Demo

This demo shows how to process multiple work orders in parallel using asyncio.gather().
Instead of processing each work order sequentially (slow), we process all of them
at the same time (fast).

Concept:
- We have 5 vehicles that need maintenance
- Each work order requires: checking parts, finding a technician, and estimating time
- By processing them in parallel, we save significant time
"""

import asyncio
import time
from datetime import datetime


# ============================================================
# Simulated Async Operations (like API calls in real app)
# ============================================================

async def check_parts_availability(vehicle_id: str, parts_needed: list) -> dict:
    """
    Simulate checking if parts are available in inventory.
    In a real app, this would be an API call to inventory system.
    """
    print(f"  [{vehicle_id}] Checking parts availability...")
    await asyncio.sleep(1)  # Simulate network delay

    return {
        "vehicle_id": vehicle_id,
        "parts_available": True,
        "parts_list": parts_needed,
        "warehouse": "Main Warehouse"
    }


async def find_available_technician(vehicle_id: str, service_type: str) -> dict:
    """
    Simulate finding an available technician for the job.
    In a real app, this would query scheduling system.
    """
    print(f"  [{vehicle_id}] Finding available technician...")
    await asyncio.sleep(1.2)  # Simulate network delay

    # Simple logic to assign technicians
    technicians = ["Mike", "Sarah", "Carlos", "Jenny", "Tom"]
    assigned = technicians[hash(vehicle_id) % len(technicians)]

    return {
        "vehicle_id": vehicle_id,
        "technician": assigned,
        "specialty": service_type
    }


async def estimate_completion_time(vehicle_id: str, service_type: str) -> dict:
    """
    Simulate estimating how long the work will take.
    In a real app, this might use historical data or AI prediction.
    """
    print(f"  [{vehicle_id}] Estimating completion time...")
    await asyncio.sleep(0.8)  # Simulate computation delay

    # Simple estimation based on service type
    estimates = {
        "Oil Change": 1.0,
        "Brake Service": 2.5,
        "Tire Rotation": 1.5,
        "Engine Diagnostic": 3.0,
        "Transmission Service": 4.0
    }

    return {
        "vehicle_id": vehicle_id,
        "estimated_hours": estimates.get(service_type, 2.0),
        "service_type": service_type
    }


# ============================================================
# Main Work Order Processing
# ============================================================

async def process_work_order(work_order: dict) -> dict:
    """
    Process a single work order by performing all required checks in parallel.

    This function uses asyncio.gather() to run multiple async operations
    at the same time, which is faster than running them one after another.
    """
    vehicle_id = work_order["vehicle_id"]
    service_type = work_order["service_type"]
    parts_needed = work_order["parts_needed"]

    print(f"\n[{vehicle_id}] Starting work order processing...")

    # ⭐ KEY PATTERN: Use asyncio.gather() to run operations in parallel
    # Instead of awaiting each one sequentially, we await all at once
    parts_result, tech_result, time_result = await asyncio.gather(
        check_parts_availability(vehicle_id, parts_needed),
        find_available_technician(vehicle_id, service_type),
        estimate_completion_time(vehicle_id, service_type)
    )

    # Combine all results into final work order
    result = {
        "vehicle_id": vehicle_id,
        "service_type": service_type,
        "status": "Ready to Start",
        "parts": parts_result,
        "technician": tech_result,
        "estimate": time_result,
        "total_cost": time_result["estimated_hours"] * 85  # $85/hour labor rate
    }

    print(f"[{vehicle_id}] ✓ Work order complete!")
    return result


async def process_all_work_orders_parallel(work_orders: list) -> list:
    """
    Process ALL work orders in parallel using asyncio.gather().

    This is the main parallel pattern:
    - Create a task for each work order
    - Use gather() to run them all at the same time
    - Get all results back when they're all done
    """
    print("\n" + "="*80)
    print("PROCESSING ALL WORK ORDERS IN PARALLEL")
    print("="*80)

    start_time = time.time()

    # ⭐ KEY PATTERN: Create tasks for all work orders and run in parallel
    tasks = [process_work_order(wo) for wo in work_orders]
    results = await asyncio.gather(*tasks)

    elapsed = time.time() - start_time

    print("\n" + "="*80)
    print(f"✓ ALL WORK ORDERS COMPLETED in {elapsed:.2f} seconds")
    print("="*80)

    return results


async def process_all_work_orders_sequential(work_orders: list) -> list:
    """
    Process work orders ONE AT A TIME (sequential) for comparison.
    This is slower but shows the difference parallel processing makes.
    """
    print("\n" + "="*80)
    print("PROCESSING ALL WORK ORDERS SEQUENTIALLY (for comparison)")
    print("="*80)

    start_time = time.time()

    results = []
    for wo in work_orders:
        result = await process_work_order(wo)
        results.append(result)

    elapsed = time.time() - start_time

    print("\n" + "="*80)
    print(f"✓ ALL WORK ORDERS COMPLETED in {elapsed:.2f} seconds")
    print("="*80)

    return results


# ============================================================
# Demo Runner
# ============================================================

async def main():
    """
    Main demo function that shows the difference between parallel and sequential processing.
    """
    print("\n" + "="*80)
    print("FLEET MANAGEMENT - PARALLEL WORK ORDER PROCESSING DEMO")
    print("="*80)

    # Sample work orders for 5 different vehicles
    work_orders = [
        {
            "vehicle_id": "TRUCK-001",
            "service_type": "Oil Change",
            "parts_needed": ["Oil Filter", "5W-30 Oil"]
        },
        {
            "vehicle_id": "VAN-042",
            "service_type": "Brake Service",
            "parts_needed": ["Brake Pads", "Brake Fluid"]
        },
        {
            "vehicle_id": "TRUCK-018",
            "service_type": "Tire Rotation",
            "parts_needed": []
        },
        {
            "vehicle_id": "SUV-305",
            "service_type": "Engine Diagnostic",
            "parts_needed": ["Spark Plugs", "Air Filter"]
        },
        {
            "vehicle_id": "TRUCK-127",
            "service_type": "Transmission Service",
            "parts_needed": ["Transmission Fluid", "Filter"]
        }
    ]

    print(f"\nProcessing {len(work_orders)} work orders...\n")

    # ============================================================
    # RUN IN PARALLEL (FAST) ⚡
    # ============================================================
    parallel_results = await process_all_work_orders_parallel(work_orders)

    print("\n\n")

    # ============================================================
    # RUN SEQUENTIALLY (SLOW) 🐌 - For comparison only
    # ============================================================
    sequential_results = await process_all_work_orders_sequential(work_orders)

    # ============================================================
    # Show Final Results
    # ============================================================
    print("\n" + "="*80)
    print("FINAL WORK ORDER SUMMARY")
    print("="*80)

    for result in parallel_results:
        print(f"\n{result['vehicle_id']} - {result['service_type']}")
        print(f"  Technician: {result['technician']['technician']}")
        print(f"  Estimated Time: {result['estimate']['estimated_hours']} hours")
        print(f"  Total Cost: ${result['total_cost']:.2f}")
        print(f"  Status: {result['status']}")

    print("\n" + "="*80)
    print("KEY TAKEAWAY:")
    print("Parallel processing is ~3x faster than sequential!")
    print("This pattern is used throughout the CSV import app for AI agent calls.")
    print("="*80 + "\n")


# ============================================================
# Run the Demo
# ============================================================

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
