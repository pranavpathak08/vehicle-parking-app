"""
Test script to verify caching is working properly
"""
import requests
import time
import json

BASE_URL = "http://localhost:5000"

# Colors for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def login_as_admin():
    """Login as admin and return token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print_success(f"Logged in as admin")
        return token
    else:
        print_error("Failed to login as admin")
        return None

def login_as_user(username="pranav", password="prnv"):
    """Login as user and return token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print_success(f"Logged in as {username}")
        return token
    else:
        print_error(f"Failed to login as {username}")
        return None

def test_endpoint_caching(endpoint, token, test_name):
    """Test if an endpoint uses caching by checking response times"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n{YELLOW}Testing: {test_name}{RESET}")
    print(f"Endpoint: {endpoint}")
    
    # First request - should hit database (slower)
    start = time.time()
    response1 = requests.get(endpoint, headers=headers)
    time1 = (time.time() - start) * 1000
    
    if response1.status_code != 200:
        print_error(f"Request failed: {response1.status_code}")
        return
    
    print(f"  1st request (DB hit): {time1:.2f}ms")
    
    # Second request - should hit cache (faster)
    start = time.time()
    response2 = requests.get(endpoint, headers=headers)
    time2 = (time.time() - start) * 1000
    
    print(f"  2nd request (Cache): {time2:.2f}ms")
    
    # Calculate speedup
    speedup = time1 / time2 if time2 > 0 else 0
    improvement = ((time1 - time2) / time1 * 100) if time1 > 0 else 0
    
    if time2 < time1:
        print_success(f"  Cache is working! {speedup:.1f}x faster ({improvement:.1f}% improvement)")
    elif time2 == time1:
        print_warning(f"  Similar response times - cache might not be active")
    else:
        print_warning(f"  2nd request was slower - unexpected")
    
    # Verify data consistency
    if response1.json() == response2.json():
        print_success(f"  Data consistency: OK")
    else:
        print_error(f"  Data mismatch between cached and fresh requests!")

def test_cache_invalidation(admin_token, user_token):
    """Test that cache is invalidated after data changes"""
    print_header("Testing Cache Invalidation")
    
    # Get initial data
    response1 = requests.get(f"{BASE_URL}/api/user/lots", headers={"Authorization": f"Bearer {user_token}"})
    data1 = response1.json()
    
    print(f"Initial lots count: {len(data1)}")
    
    # Create a new lot (should invalidate cache)
    print("\nCreating new parking lot...")
    create_response = requests.post(
        f"{BASE_URL}/api/admin/lots",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Cache Lot",
            "price_per_hour": 50,
            "number_of_spots": 5,
            "address": "Test Address",
            "pincode": "110001"
        }
    )
    
    if create_response.status_code == 201:
        print_success("Parking lot created")
        lot_id = create_response.json()["lot_id"]
        
        # Get data again (should see new lot)
        response2 = requests.get(f"{BASE_URL}/api/user/lots", headers={"Authorization": f"Bearer {user_token}"})
        data2 = response2.json()
        
        print(f"Lots count after creation: {len(data2)}")
        
        if len(data2) > len(data1):
            print_success("Cache was properly invalidated!")
        else:
            print_error("Cache invalidation failed - new lot not visible")
        
        # Clean up - delete the test lot
        print("\nCleaning up test lot...")
        delete_response = requests.delete(
            f"{BASE_URL}/api/admin/lots/{lot_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if delete_response.status_code == 200:
            print_success("Test lot deleted")
    else:
        print_error(f"Failed to create test lot: {create_response.status_code}")

def test_dashboard_caching(admin_token):
    """Test expensive dashboard stats endpoint caching"""
    print_header("Testing Dashboard Stats Caching")
    
    endpoint = f"{BASE_URL}/api/admin/dashboard/stats"
    
    # Multiple rapid requests
    times = []
    for i in range(5):
        start = time.time()
        response = requests.get(endpoint, headers={"Authorization": f"Bearer {admin_token}"})
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        print(f"  Request {i+1}: {elapsed:.2f}ms")
    
    avg_time = sum(times) / len(times)
    first_vs_avg = times[0] / avg_time if avg_time > 0 else 0
    
    print(f"\n  First request: {times[0]:.2f}ms")
    print(f"  Average time: {avg_time:.2f}ms")
    
    if times[0] > avg_time * 1.5:
        print_success(f"  Dashboard caching is effective! First request {first_vs_avg:.1f}x slower")
    else:
        print_warning(f"  Dashboard caching might not be very effective")

def main():
    print_header("Parking App Cache Testing Suite")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print_error("Server is not responding correctly")
            return
        print_success("Server is running")
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to server at {BASE_URL}")
        print("Make sure Flask app is running: python app.py")
        return
    
    # Login
    print_header("Authenticating Users")
    admin_token = login_as_admin()
    user_token = login_as_user()
    
    if not admin_token or not user_token:
        print_error("Authentication failed. Exiting.")
        return
    
    # Test 1: User lots endpoint
    print_header("Test 1: User Lots Endpoint Caching")
    test_endpoint_caching(f"{BASE_URL}/api/user/lots", user_token, "Available Parking Lots")
    
    # Test 2: Admin lots endpoint
    print_header("Test 2: Admin Lots Endpoint Caching")
    test_endpoint_caching(f"{BASE_URL}/api/admin/lots", admin_token, "Admin Parking Lots List")
    
    # Test 3: User reservations endpoint
    print_header("Test 3: User Reservations Caching")
    test_endpoint_caching(f"{BASE_URL}/api/user/my_reservations", user_token, "My Reservations")
    
    # Test 4: Dashboard stats (expensive queries)
    test_dashboard_caching(admin_token)
    
    # Test 5: Cache invalidation
    test_cache_invalidation(admin_token, user_token)
    
    print_header("Cache Testing Complete")
    print("\n📊 Summary:")
    print("  • Tested endpoint caching and performance")
    print("  • Verified cache invalidation on data changes")
    print("  • Checked dashboard stats aggregation caching")
    print("\n💡 Recommendations:")
    print("  • Monitor cache hit rates in production")
    print("  • Adjust timeout values based on usage patterns")
    print("  • Consider Redis persistence for production")

if __name__ == "__main__":
    main()