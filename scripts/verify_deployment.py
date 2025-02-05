import requests
import time
import os

def test_api_endpoints():
    """Tests various API endpoints to ensure they are working correctly."""
    base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")  # Default to localhost if not set

    endpoints_to_test = [
        ("/health", 200),  # Example health check endpoint
        ("/api/auth/protected", 401),  # Example protected endpoint (should be unauthorized without token)
        # Add more endpoints to test here
    ]

    for endpoint, expected_status in endpoints_to_test:
        full_url = f"{base_url}{endpoint}"
        try:
            response = requests.get(full_url)
            if response.status_code == expected_status:
                print(f"API Endpoint {full_url} - PASSED (Status: {response.status_code})")
            else:
                print(f"API Endpoint {full_url} - FAILED (Expected: {expected_status}, Got: {response.status_code})")
                return False  # Fail fast on API failures
        except requests.exceptions.ConnectionError:
            print(f"API Endpoint {full_url} - FAILED (Connection Error)")
            return False
        except Exception as e:
            print(f"API Endpoint {full_url} - FAILED (Error: {e})")
            return False

    return True

def test_frontend():
    """Simulates basic frontend checks by requesting the main page."""
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")  # Default frontend URL

    try:
        response = requests.get(frontend_url)
        if response.status_code == 200:
            print(f"Frontend {frontend_url} - PASSED (Status: {response.status_code})")
        else:
            print(f"Frontend {frontend_url} - FAILED (Status: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"Frontend {frontend_url} - FAILED (Connection Error)")
        return False
    except Exception as e:
        print(f"Frontend {frontend_url} - FAILED (Error: {e})")
        return False
    return True

def main():
    """Main function to run the deployment verification tests."""

    print("Waiting for services to be ready...")
    time.sleep(30)
    print("Starting Deployment Verification...")

    api_passed = test_api_endpoints()
    frontend_passed = test_frontend()

    if api_passed and frontend_passed:
        print("Deployment Verification - PASSED")
        return 0  # Success
    else:
        print("Deployment Verification - FAILED")
        return 1  # Failure

if __name__ == "__main__":
    exit(main())