"""Test script for /speak endpoint.

This script tests if the /speak endpoint works correctly when the bot is running.
"""
import requests
import time

def test_speak_endpoint(url="http://localhost:8080"):
    """Test the /speak endpoint."""
    print(f"Testing /speak endpoint at {url}")
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        resp = requests.get(f"{url}/health", timeout=5)
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Speak endpoint without bot (should fail gracefully)
    print("\n2. Testing /speak endpoint (without running bot)...")
    try:
        resp = requests.post(
            f"{url}/speak",
            json={"text": "teste"},
            timeout=5
        )
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Missing text field
    print("\n3. Testing /speak with missing 'text' field...")
    try:
        resp = requests.post(
            f"{url}/speak",
            json={},
            timeout=5
        )
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    test_speak_endpoint(url)
