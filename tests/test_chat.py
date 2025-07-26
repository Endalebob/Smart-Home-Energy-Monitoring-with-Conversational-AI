#!/usr/bin/env python3
"""
Test script for the Conversational AI service
Demonstrates natural language queries for energy monitoring
"""

import requests
import json
import time

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

def test_chat_query(token, query, description):
    """Test a chat query and display results"""
    headers = {"Authorization": f"Bearer {token}"}
    
    chat_data = {
        "query": query
    }
    
    print(f"\n{'='*60}")
    print(f"Test: {description}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/chat/query", json=chat_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response:")
            print(f"Chat ID: {result['chat_id']}")
            print(f"Answer: {result['answer']}")
            if result.get('data'):
                print(f"Data: {json.dumps(result['data'], indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_chat_examples(token):
    """Test various chat examples"""
    print("🤖 Testing Conversational AI for Smart Home Energy Monitoring")
    print("This demonstrates natural language queries about energy usage")
    
    # Test examples
    test_cases = [
        ("Hello", "Greeting"),
        ("How much energy did my fridge use yesterday?", "Energy usage for specific device"),
        ("Which of my devices are using the most power?", "Top energy consumers"),
        ("Show me my energy summary for today", "Energy summary"),
        ("List my devices", "Device listing"),
        ("Compare energy usage between my devices", "Device comparison"),
        ("What's the power consumption of my AC today?", "Specific device energy query"),
        ("Show me the most efficient devices", "Efficiency comparison"),
        ("How much energy did I use last month?", "Historical energy summary"),
        ("Thank you", "Gratitude"),
        ("What can you help me with?", "Capability inquiry")
    ]
    
    for query, description in test_cases:
        test_chat_query(token, query, description)
        time.sleep(1)  # Small delay between requests

def test_chat_capabilities(token):
    """Test chat capabilities endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n{'='*60}")
    print("Testing Chat Capabilities")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/chat/capabilities", headers=headers)
        
        if response.status_code == 200:
            capabilities = response.json()
            print("✅ Chat Capabilities:")
            print(json.dumps(capabilities, indent=2))
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_chat_examples_endpoint(token):
    """Test chat examples endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n{'='*60}")
    print("Testing Chat Examples Endpoint")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/chat/examples", headers=headers)
        
        if response.status_code == 200:
            examples = response.json()
            print("✅ Chat Examples:")
            print(json.dumps(examples, indent=2))
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    print("🚀 Starting Conversational AI Test")
    print("Make sure the API is running and you have some devices and telemetry data")
    
    # Login
    token = login_admin()
    if not token:
        print("❌ Failed to login. Exiting.")
        return
    
    print("✅ Logged in successfully")
    
    # Test chat capabilities
    test_chat_capabilities(token)
    
    # Test chat examples endpoint
    test_chat_examples_endpoint(token)
    
    # Test various chat queries
    test_chat_examples(token)
    
    print(f"\n{'='*60}")
    print("🎉 Conversational AI Test Complete!")
    print("The system can now understand natural language queries about energy usage")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 