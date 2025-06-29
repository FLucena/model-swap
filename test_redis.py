#!/usr/bin/env python3
"""
Test script to verify Redis connectivity for Flask-Limiter
"""
import os
import redis  # type: ignore[import]
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_redis_connection():
    """Test Redis connection"""
    redis_url = os.environ.get('REDIS_URL')
    
    if not redis_url:
        print("❌ No REDIS_URL environment variable found")
        return False
    
    try:
        # Create Redis client
        r = redis.from_url(redis_url)  # type: ignore[attr-defined]
        if r is None:
            print("❌ Could not create Redis client")
            return False
        # Test connection
        if hasattr(r, 'ping'):
            r.ping()  # type: ignore[attr-defined]
            print("✅ Redis connection successful")
        else:
            print("❌ Redis client does not have 'ping' method")
            return False
        # Test basic operations
        if hasattr(r, 'set') and hasattr(r, 'get') and hasattr(r, 'delete'):
            r.set('test_key', 'test_value')  # type: ignore[attr-defined]
            value = r.get('test_key')  # type: ignore[attr-defined]
            r.delete('test_key')  # type: ignore[attr-defined]
            if value == b'test_value':
                print("✅ Redis read/write operations successful")
                return True
            else:
                print("❌ Redis read/write operations failed")
                return False
        else:
            print("❌ Redis client missing set/get/delete methods")
            return False
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Redis connection for Flask-Limiter...")
    success = test_redis_connection()
    
    if success:
        print("\n🎉 Redis is ready for Flask-Limiter!")
    else:
        print("\n⚠️  Redis connection failed. Flask-Limiter will use in-memory storage.") 