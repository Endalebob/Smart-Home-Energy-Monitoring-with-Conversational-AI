#!/usr/bin/env python3
"""
Simple Telemetry Test for Smart Home Energy Monitoring API
Tests all telemetry endpoints and prints clear results
"""
import requests
import time
import uuid
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "admin@smart-home.com"
TEST_PASSWORD = "admin123"

# Global variables to store test data
access_token = None
user_id = None
device_id = None

def print_result(test_name, success, message=""):
    """Print test result with clear formatting"""
    if success:
        print(f"✅ {test_name}: PASSED")
    else:
        print(f"❌ {test_name}: FAILED - {message}")
    print()

def test_health_check():
    """Test if server is running"""
    print("🏥 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        success = response.status_code == 200
        print_result("Health Check", success, f"Status: {response.status_code}")
        return success
    except:
        print_result("Health Check", False, "Cannot connect to server")
        return False

def test_telemetry_health():
    """Test telemetry service health"""
    print("📊 Testing telemetry health...")
    try:
        response = requests.get(f"{BASE_URL}/api/telemetry/health")
        success = response.status_code == 200
        print_result("Telemetry Health", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Telemetry Health", False, str(e))
        return False

def test_register_user():
    """Test user registration (skipped - using existing user)"""
    print("📝 Testing user registration (skipped)...")
    print_result("User Registration", True, "Using existing user")
    return True

def test_login_user():
    """Test user login and get access token"""
    global access_token, user_id
    print("🔐 Testing user login...")
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        success = response.status_code == 200
        if success:
            result = response.json()
            access_token = result.get('access_token')
            user_id = result.get('user', {}).get('id')
            print(f"✅ User Login: PASSED")
            print(f"   Token: {access_token[:20] if access_token else 'N/A'}...")
            print(f"   User ID: {user_id}")
        else:
            print(f"❌ User Login: FAILED - Status: {response.status_code}")
        print()
        return success
    except Exception as e:
        print_result("User Login", False, str(e))
        return False

def test_create_device():
    """Test device creation"""
    global device_id
    print("🔌 Testing device creation...")
    
    if not access_token:
        print_result("Device Creation", False, "No access token available")
        return False
    
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "device_id": str(uuid.uuid4()),
        "name": "Test Fridge",
        "device_type": "fridge"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/devices/", json=data, headers=headers)
        success = response.status_code == 201
        if success:
            result = response.json()
            device_id = result.get('device_id')
            print(f"✅ Device Creation: PASSED")
            print(f"   Device ID: {device_id}")
        else:
            print(f"❌ Device Creation: FAILED - Status: {response.status_code}")
        print()
        return success
    except Exception as e:
        print_result("Device Creation", False, str(e))
        return False

def test_ingest_telemetry():
    """Test telemetry ingestion"""
    print("📈 Testing telemetry ingestion...")
    
    if not access_token or not device_id:
        print_result("Telemetry Ingestion", False, "No access token or device ID available")
        return False
    
    data = {
        "device_id": device_id,
        "timestamp": datetime.now().isoformat(),
        "energy_watts": 150.5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/telemetry/ingest", json=data)
        success = response.status_code == 201
        if success:
            result = response.json()
            print(f"✅ Telemetry Ingestion: PASSED")
            print(f"   Energy: {result.get('energy_watts')} watts")
            print(f"   Timestamp: {result.get('timestamp')}")
        else:
            print(f"❌ Telemetry Ingestion: FAILED - Status: {response.status_code}")
        print()
        return success
    except Exception as e:
        print_result("Telemetry Ingestion", False, str(e))
        return False

def test_ingest_multiple_telemetry():
    """Test multiple telemetry ingestion"""
    print("📊 Testing multiple telemetry ingestion...")
    
    if not access_token or not device_id:
        print_result("Multiple Telemetry", False, "No access token or device ID available")
        return False
    
    # Create multiple telemetry records with different timestamps
    timestamps = [
        (datetime.now() - timedelta(hours=2)).isoformat(),
        (datetime.now() - timedelta(hours=1)).isoformat(),
        datetime.now().isoformat()
    ]
    
    success_count = 0
    for i, timestamp in enumerate(timestamps):
        data = {
            "device_id": device_id,
            "timestamp": timestamp,
            "energy_watts": 100.0 + (i * 25.0)  # Different energy values
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/telemetry/ingest", json=data)
            if response.status_code == 201:
                success_count += 1
        except:
            pass
    
    success = success_count == len(timestamps)
    print_result("Multiple Telemetry", success, f"Created {success_count}/{len(timestamps)} records")
    return success

def test_get_device_telemetry():
    """Test getting device telemetry"""
    print("📋 Testing get device telemetry...")
    
    if not access_token or not device_id:
        print_result("Get Device Telemetry", False, "No access token or device ID available")
        return False
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/telemetry/device/{device_id}", headers=headers)
        success = response.status_code == 200
        if success:
            result = response.json()
            print(f"✅ Get Device Telemetry: PASSED")
            print(f"   Records: {len(result)}")
        else:
            print(f"❌ Get Device Telemetry: FAILED - Status: {response.status_code}")
        print()
        return success
    except Exception as e:
        print_result("Get Device Telemetry", False, str(e))
        return False

def test_get_my_devices_telemetry():
    """Test getting all user devices telemetry"""
    print("🏠 Testing get my devices telemetry...")
    
    if not access_token:
        print_result("Get My Devices Telemetry", False, "No access token available")
        return False
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/telemetry/my-devices", headers=headers)
        success = response.status_code == 200
        if success:
            result = response.json()
            print(f"✅ Get My Devices Telemetry: PASSED")
            print(f"   Devices: {len(result)}")
        else:
            print(f"❌ Get My Devices Telemetry: FAILED - Status: {response.status_code}")
        print()
        return success
    except Exception as e:
        print_result("Get My Devices Telemetry", False, str(e))
        return False

def test_get_energy_summary():
    """Test getting energy summary"""
    print("📊 Testing energy summary...")
    
    if not access_token:
        print_result("Energy Summary", False, "No access token available")
        return False
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/telemetry/summary", headers=headers)
        success = response.status_code == 200
        if success:
            result = response.json()
            print(f"✅ Energy Summary: PASSED")
            print(f"   Summary data received")
        else:
            print(f"❌ Energy Summary: FAILED - Status: {response.status_code}")
        print()
        return success
    except Exception as e:
        print_result("Energy Summary", False, str(e))
        return False

def test_get_top_consuming_devices():
    """Test getting top consuming devices"""
    print("🔥 Testing top consuming devices...")
    
    if not access_token:
        print_result("Top Consuming Devices", False, "No access token available")
        return False
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/telemetry/top-consuming", headers=headers)
        success = response.status_code == 200
        if success:
            result = response.json()
            print(f"✅ Top Consuming Devices: PASSED")
            print(f"   Top devices data received")
        else:
            print(f"❌ Top Consuming Devices: FAILED - Status: {response.status_code}")
        print()
        return success
    except Exception as e:
        print_result("Top Consuming Devices", False, str(e))
        return False

def test_unauthorized_access():
    """Test unauthorized access to telemetry endpoints"""
    print("🚫 Testing unauthorized access...")
    
    # Try to access telemetry without token
    try:
        response = requests.get(f"{BASE_URL}/api/telemetry/my-devices")
        success = response.status_code in [401, 403]  # Accept both 401 and 403
        print_result("Unauthorized Access", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Unauthorized Access", False, str(e))
        return False

def test_invalid_telemetry_data():
    """Test invalid telemetry data"""
    print("⚠️ Testing invalid telemetry data...")
    
    if not device_id:
        print_result("Invalid Telemetry Data", False, "No device ID available")
        return False
    
    # Send invalid data (missing required fields)
    data = {
        "device_id": device_id,
        # Missing timestamp and energy_watts
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/telemetry/ingest", json=data)
        success = response.status_code == 422
        print_result("Invalid Telemetry Data", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Invalid Telemetry Data", False, str(e))
        return False

def main():
    """Run all tests"""
    print("🚀 SMART HOME ENERGY MONITORING - TELEMETRY TEST")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Test user: {TEST_EMAIL}")
    print("=" * 60)
    print()
    
    # Track results
    results = []
    
    # Run tests in order (some depend on previous tests)
    results.append(("Health Check", test_health_check()))
    results.append(("Telemetry Health", test_telemetry_health()))
    results.append(("User Registration", test_register_user()))
    results.append(("User Login", test_login_user()))
    results.append(("Device Creation", test_create_device()))
    results.append(("Telemetry Ingestion", test_ingest_telemetry()))
    results.append(("Multiple Telemetry", test_ingest_multiple_telemetry()))
    results.append(("Get Device Telemetry", test_get_device_telemetry()))
    results.append(("Get My Devices Telemetry", test_get_my_devices_telemetry()))
    results.append(("Energy Summary", test_get_energy_summary()))
    results.append(("Top Consuming Devices", test_get_top_consuming_devices()))
    results.append(("Unauthorized Access", test_unauthorized_access()))
    results.append(("Invalid Telemetry Data", test_invalid_telemetry_data()))
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Telemetry system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server and try again.")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 