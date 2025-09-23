#!/usr/bin/env python3
"""
Test script to verify RootSource AI functionality
"""
import requests
import json
import time
import sys

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✓ Health endpoint: {response.status_code}")
        print(f"  Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Health endpoint failed: {e}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint"""
    try:
        payload = {"message": "Hello, tell me about crops"}
        response = requests.post(
            "http://localhost:8000/chat", 
            json=payload,
            timeout=10
        )
        print(f"✓ Chat endpoint: {response.status_code}")
        result = response.json()
        print(f"  Response preview: {result.get('reply', '')[:100]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Chat endpoint failed: {e}")
        return False

def test_main_page():
    """Test the main page"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✓ Main page: {response.status_code}")
        content = response.text
        if "RootSource" in content:
            print("  ✓ Contains RootSource branding")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Main page failed: {e}")
        return False

def main():
    print("🌾 RootSource AI - Functionality Test")
    print("=" * 40)
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Main Page", test_main_page), 
        ("Chat Endpoint", test_chat_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! RootSource AI is fully functional!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())