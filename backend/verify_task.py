#!/usr/bin/env python
"""Verify the tasks were updated"""
import requests

API_URL = "http://127.0.0.1:8000/api"
user_id = 2
active_token = "b2811cdd-1cc2-4d22-b960-12ecafb9086e"

response = requests.post(
    f"{API_URL}/tasks/get",
    json={"id": user_id, "active_token": active_token},
    timeout=5
)

if response.status_code == 200:
    data = response.json()
    print("\nTasks for User 2:")
    print("=" * 40)
    for task in data['data']:
        status_symbol = "✓" if task['status'] == 'DONE' else "○"
        print(f"  {status_symbol} {task['title']} [{task['status']}]")
    print("=" * 40)
else:
    print(f"Error: {response.status_code}")
    print(response.text)
