#!/usr/bin/env python
"""
Test script for the threading-based agent scheduler
"""

import time
from agent_scheduler import scheduler

def test_scheduler():
    print("🧪 Testing Threading Agent Scheduler...")

    # Test 1: Check scheduler status
    print("\n1. Checking scheduler status...")
    status = scheduler.get_scheduler_status()
    print(f"Status: {status}")

    # Test 2: Start threading scheduler
    print("\n2. Starting threading scheduler...")
    started = scheduler.start_threading_scheduler()
    print(f"Started: {started}")

    # Test 3: Trigger manual task
    print("\n3. Triggering manual task (predictions update)...")
    result = scheduler.trigger_manual_task('daily_predictions_update')
    print(f"Manual task result: {result}")

    # Wait a bit for task to complete
    print("\n4. Waiting for task completion...")
    time.sleep(5)

    # Test 4: Check status again
    print("\n5. Checking final status...")
    final_status = scheduler.get_scheduler_status()
    print(f"Final status: {final_status}")

    # Test 5: Stop scheduler
    print("\n6. Stopping scheduler...")
    stopped = scheduler.stop_threading_scheduler()
    print(f"Stopped: {stopped}")

    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_scheduler()
