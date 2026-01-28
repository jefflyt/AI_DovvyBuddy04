#!/usr/bin/env python3
"""Test lead capture API endpoint."""
import requests
import json
import time

# Wait for server to be ready
time.sleep(3)

# Test data
lead_data = {
    "type": "training",
    "data": {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "location": "Kuala Lumpur",
        "message": "Interested in Open Water certification"
    }
}

print("Testing lead capture endpoint...")
print(f"Sending: {json.dumps(lead_data, indent=2)}")

try:
    response = requests.post(
        "http://localhost:8000/api/leads",
        json=lead_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        print("\n✅ SUCCESS! Lead captured successfully.")
        print("Check your email at jeff.mailme@gmail.com for the notification.")
    else:
        print("\n❌ FAILED!")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
