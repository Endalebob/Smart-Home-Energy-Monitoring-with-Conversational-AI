#!/usr/bin/env python3
"""
Simple Auth Test for Smart Home Energy Monitoring API
Tests all auth endpoints and prints clear results
"""
import requests
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"testuser_{int(time.time())}@example.com"
TEST_USERNAME = f"testuser_{int(time.time())}"
TEST_PASSWORD = "testpassword123"

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

def test_register():
    """Test user registration"""
    print("📝 Testing user registration...")
    data = {
        "email": TEST_EMAIL,
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
        success = response.status_code == 201
        print_result("User Registration", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("User Registration", False, str(e))
        return False

def test_duplicate_register():
    """Test duplicate registration (should fail)"""
    print("🔄 Testing duplicate registration...")
    data = {
        "email": TEST_EMAIL,
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
        success = response.status_code == 400
        print_result("Duplicate Registration", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Duplicate Registration", False, str(e))
        return False

def test_login():
    """Test user login"""
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
            print(f"✅ User Login: PASSED")
            print(f"   Token: {result.get('access_token', 'N/A')[:20]}...")
            print(f"   User: {result.get('user', {}).get('email', 'N/A')}")
        else:
            print(f"❌ User Login: FAILED - Status: {response.status_code}")
        print()
        return success
    except Exception as e:
        print_result("User Login", False, str(e))
        return False

def test_wrong_password():
    """Test login with wrong password (should fail)"""
    print("🔒 Testing wrong password login...")
    data = {
        "email": TEST_EMAIL,
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        success = response.status_code == 401
        print_result("Wrong Password Login", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Wrong Password Login", False, str(e))
        return False

def test_nonexistent_user():
    """Test login with non-existent user (should fail)"""
    print("👻 Testing non-existent user login...")
    data = {
        "email": "nonexistent@example.com",
        "password": "anypassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        success = response.status_code == 401
        print_result("Non-existent User Login", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Non-existent User Login", False, str(e))
        return False

def test_invalid_email():
    """Test registration with invalid email (should fail)"""
    print("🚫 Testing invalid email registration...")
    data = {
        "email": "invalid-email",
        "username": "testuser",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
        success = response.status_code == 422
        print_result("Invalid Email Registration", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Invalid Email Registration", False, str(e))
        return False

def main():
    """Run all tests"""
    print("🚀 SMART HOME ENERGY MONITORING - AUTH TEST")
    print("=" * 50)
    print(f"Testing against: {BASE_URL}")
    print(f"Test user: {TEST_EMAIL}")
    print("=" * 50)
    print()
    
    # Track results
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("User Registration", test_register()))
    results.append(("Duplicate Registration", test_duplicate_register()))
    results.append(("User Login", test_login()))
    results.append(("Wrong Password", test_wrong_password()))
    results.append(("Non-existent User", test_nonexistent_user()))
    results.append(("Invalid Email", test_invalid_email()))
    
    # Summary
    print("=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Authentication is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server and try again.")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 