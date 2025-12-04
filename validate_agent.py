import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def print_result(test_name, success, details=None):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"   {details}")

def test_health():
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200 and response.json().get("status") == "healthy":
            print_result("Health Check", True)
            return True
        else:
            print_result("Health Check", False, f"Status: {response.status_code}, Body: {response.text}")
            return False
    except Exception as e:
        print_result("Health Check", False, str(e))
        return False

def test_context_aware_query():
    url = f"{BASE_URL}/query"
    payload = {
        "query": "What is the current temperature?",
        "entity_context": {
            "entity_id": 40976504,
            "entity_name": "Heat Exchanger HX00-A3",
            "entity_type": "HeatExchanger"
        }
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            # Check if response contains reasonable text
            if "response" in data and len(data["response"]) > 10:
                 print_result("Context-Aware Query", True)
                 return True
            else:
                print_result("Context-Aware Query", False, f"Invalid response format: {data}")
                return False
        else:
            print_result("Context-Aware Query", False, f"Status: {response.status_code}, Body: {response.text}")
            return False
    except Exception as e:
        print_result("Context-Aware Query", False, str(e))
        return False

def test_historical_query():
    url = f"{BASE_URL}/query"
    payload = {
        "query": "What was the average temperature last week?",
        "entity_context": {
            "entity_id": 40976504,
            "entity_name": "Heat Exchanger HX00-A3",
            "entity_type": "HeatExchanger"
        }
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                 print_result("Historical Data Query", True)
                 return True
            else:
                print_result("Historical Data Query", False, f"Invalid response format: {data}")
                return False
        else:
            print_result("Historical Data Query", False, f"Status: {response.status_code}, Body: {response.text}")
            return False
    except Exception as e:
        print_result("Historical Data Query", False, str(e))
        return False

def test_error_handling():
    url = f"{BASE_URL}/query"
    # Invalid entity ID
    payload = {
        "query": "What is the status?",
        "entity_context": {
            "entity_id": 999999999, 
            "entity_name": "NonExistent",
            "entity_type": "Unknown"
        }
    }
    try:
        response = requests.post(url, json=payload)
        # The agent might return 200 with a "I don't know" message, or a 404/500 depending on implementation.
        # We'll assume a 200 OK with a polite refusal is the desired behavior for a chat agent, 
        # but if it crashes (500), that's a fail.
        if response.status_code == 200:
             print_result("Error Handling (Non-existent Entity)", True, "Handled gracefully")
             return True
        elif response.status_code == 404:
             print_result("Error Handling (Non-existent Entity)", True, "Returned 404 as expected")
             return True
        else:
            print_result("Error Handling (Non-existent Entity)", False, f"Status: {response.status_code}, Body: {response.text}")
            return False
    except Exception as e:
        print_result("Error Handling", False, str(e))
        return False

if __name__ == "__main__":
    print("Starting Validation Tests...")
    results = [
        test_health(),
        test_context_aware_query(),
        test_historical_query(),
        test_error_handling()
    ]
    
    if all(results):
        print("\nAll tests passed! 🚀")
        sys.exit(0)
    else:
        print("\nSome tests failed.")
        sys.exit(1)
