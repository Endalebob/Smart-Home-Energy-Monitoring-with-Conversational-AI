#!/usr/bin/env python3
"""
Telemetry Simulation Script
Generates sample telemetry data for testing the API
"""

import requests
import random
import time
import uuid
from datetime import datetime, timedelta
import json

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@smart-home.com"
ADMIN_PASSWORD = "admin123"

def login_admin():
    """Login as admin and get access token"""
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def create_test_devices(token):
    """Create test devices for the admin user"""
    headers = {"Authorization": f"Bearer {token}"}
    
    devices = [
        {"name": "Kitchen Fridge", "device_type": "refrigerator"},
        {"name": "Living Room AC", "device_type": "air_conditioner"},
        {"name": "TV", "device_type": "television"},
        {"name": "Washing Machine", "device_type": "appliance"},
        {"name": "Dishwasher", "device_type": "appliance"}
    ]
    
    created_devices = []
    for device_data in devices:
        response = requests.post(f"{BASE_URL}/api/devices/", json=device_data, headers=headers)
        if response.status_code == 201:
            device = response.json()
            created_devices.append(device)
            print(f"Created device: {device['name']} (ID: {device['device_id']})")
        else:
            print(f"Failed to create device {device_data['name']}: {response.text}")
    
    return created_devices

def generate_telemetry_data(device_id, hours=24):
    """Generate telemetry data for a device"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Different power ranges for different device types
    power_ranges = {
        "refrigerator": (50, 150),
        "air_conditioner": (1000, 3000),
        "television": (50, 200),
        "appliance": (200, 800)
    }
    
    # Get device type to determine power range
    response = requests.get(f"{BASE_URL}/api/devices/{device_id}")
    if response.status_code == 200:
        device_type = response.json()["device_type"]
        min_power, max_power = power_ranges.get(device_type, (50, 300))
    else:
        min_power, max_power = 50, 300
    
    telemetry_data = []
    
    for i in range(hours * 60):  # One reading per minute
        timestamp = start_time + timedelta(minutes=i)
        
        # Add some realistic variation
        base_power = random.uniform(min_power, max_power)
        # Add some noise and time-based patterns
        noise = random.uniform(-0.1, 0.1) * base_power
        time_factor = 1.0 + 0.2 * abs((timestamp.hour - 12) / 12)  # Higher usage during day
        
        energy_watts = max(0, base_power + noise) * time_factor
        
        telemetry_data.append({
            "device_id": device_id,
            "timestamp": timestamp.isoformat() + "Z",
            "energy_watts": round(energy_watts, 2)
        })
    
    return telemetry_data

def send_telemetry_data(telemetry_data, token):
    """Send telemetry data to the API"""
    headers = {"Authorization": f"Bearer {token}"}
    
    success_count = 0
    for data in telemetry_data:
        response = requests.post(f"{BASE_URL}/api/telemetry/ingest", json=data, headers=headers)
        if response.status_code == 201:
            success_count += 1
        else:
            print(f"Failed to send telemetry: {response.text}")
    
    return success_count

def main():
    print("Starting telemetry simulation...")
    
    # Login as admin
    token = login_admin()
    if not token:
        print("Failed to login. Exiting.")
        return
    
    print("✅ Logged in successfully")
    
    # Create test devices
    print("\nCreating test devices...")
    devices = create_test_devices(token)
    
    if not devices:
        print("No devices created. Exiting.")
        return
    
    print(f"✅ Created {len(devices)} devices")
    
    # Generate and send telemetry data
    print("\nGenerating telemetry data...")
    total_sent = 0
    
    for device in devices:
        print(f"Generating data for {device['name']}...")
        telemetry_data = generate_telemetry_data(device['device_id'], hours=24)
        
        print(f"Sending {len(telemetry_data)} telemetry records...")
        sent_count = send_telemetry_data(telemetry_data, token)
        total_sent += sent_count
        
        print(f"✅ Sent {sent_count} records for {device['name']}")
        time.sleep(0.1)  # Small delay between devices
    
    print(f"\n🎉 Simulation complete!")
    print(f"Total telemetry records sent: {total_sent}")
    print(f"Devices created: {len(devices)}")
    print(f"Time period: 24 hours")
    
    # Show some sample queries
    print("\n📊 Sample API queries you can try:")
    print(f"GET {BASE_URL}/api/telemetry/summary")
    print(f"GET {BASE_URL}/api/telemetry/top-consuming")
    print(f"GET {BASE_URL}/api/telemetry/my-devices")
    print(f"GET {BASE_URL}/api/devices/")

if __name__ == "__main__":
    main() 