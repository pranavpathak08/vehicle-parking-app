"""
Quick script to verify cache is working correctly
Run this after starting the Flask app
"""
from app import create_app, cache

app = create_app()

with app.app_context():
    print("Testing cache setup...")
    print(f"Cache type: {type(cache)}")
    print(f"Cache config: {app.config.get('CACHE_TYPE')}")
    
    # Test basic cache operations
    print("\n1. Setting a test value...")
    cache.set("test_key", {"message": "Hello from cache!"}, timeout=60)
    print("   ✓ Set successful")
    
    print("\n2. Getting the test value...")
    result = cache.get("test_key")
    print(f"   Retrieved: {result}")
    
    if result and result.get("message") == "Hello from cache!":
        print("   ✓ Cache is working correctly!")
    else:
        print("   ✗ Cache retrieval failed")
    
    print("\n3. Deleting the test value...")
    cache.delete("test_key")
    print("   ✓ Delete successful")
    
    print("\n4. Verifying deletion...")
    result = cache.get("test_key")
    if result is None:
        print("   ✓ Key successfully deleted")
    else:
        print(f"   ✗ Key still exists: {result}")
    
    print("\n" + "="*50)
    print("Cache verification complete!")
    print("="*50)