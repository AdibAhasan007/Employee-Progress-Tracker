#!/usr/bin/env python
"""Test the task update API endpoint"""
import requests
import json

API_URL = "http://127.0.0.1:8000"

# Test data
user_id = 2
active_token = "b2811cdd-1cc2-4d22-b960-12ecafb9086e"
task_id = 1
new_status = "DONE"

payload = {
    "task_id": task_id,
    "status": new_status,
    "id": user_id,
    "active_token": active_token
}

print(f"Testing task update endpoint...")
print(f"Payload: {json.dumps(payload, indent=2)}")
print(f"URL: {API_URL}/tasks/update")
print()

try:
    response = requests.post(
        f"{API_URL}/tasks/update",
        json=payload,
        timeout=5
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS: Task updated successfully!")
    else:
        print(f"\n❌ ERROR: Task update failed with status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
