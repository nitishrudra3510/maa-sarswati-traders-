#!/usr/bin/env python3
"""
Simple API Test Script
Tests the Video Recommendation Engine API endpoints
"""

import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Video Recommendation Engine API")
    print("=" * 50)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Test Health Endpoint
    print("\n1. Testing Health Endpoint:")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print("   ✅ Health check passed!")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Test Personalized Feed
    print("\n2. Testing Personalized Feed:")
    try:
        response = requests.get(f"{base_url}/api/v1/feed?username=testuser", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        print("   ✅ Personalized feed working!")
    except Exception as e:
        print(f"   ❌ Personalized feed failed: {e}")
    
    # Test Category Feed
    print("\n3. Testing Category Feed:")
    try:
        response = requests.get(f"{base_url}/api/v1/feed/category?username=testuser&project_code=fitness", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        print("   ✅ Category feed working!")
    except Exception as e:
        print(f"   ❌ Category feed failed: {e}")
    
    # Test API Documentation
    print("\n4. Testing API Documentation:")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"   Status: {response.status_code}")
        print("   ✅ API docs accessible!")
        print(f"   📖 Visit: {base_url}/docs")
    except Exception as e:
        print(f"   ❌ API docs failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")
    print(f"🌐 Server running at: {base_url}")
    print(f"📖 API Documentation: {base_url}/docs")

if __name__ == "__main__":
    test_api()
