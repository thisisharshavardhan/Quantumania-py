#!/usr/bin/env python3
"""
Test script for Quantum Jobs Tracker API
"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_api_endpoints():
    """Test all major API endpoints"""
    
    async with httpx.AsyncClient() as client:
        print("🧪 Testing Quantum Jobs Tracker API")
        print("=" * 50)
        
        # Test root endpoint
        print("1. Testing root endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/")
            print(f"   ✅ Root: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   📦 Version: {data.get('version', 'unknown')}")
        except Exception as e:
            print(f"   ❌ Root: {e}")
        
        # Test health check
        print("\n2. Testing health check...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"   ✅ Health: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   🔌 Status: {data.get('status', 'unknown')}")
        except Exception as e:
            print(f"   ❌ Health: {e}")
        
        # Test dashboard
        print("\n3. Testing dashboard...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/dashboard/stats/jobs")
            print(f"   ✅ Dashboard stats: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   📊 Total jobs: {data.get('total_jobs', 0)}")
        except Exception as e:
            print(f"   ❌ Dashboard: {e}")
        
        # Test backends sync
        print("\n4. Testing backends sync...")
        try:
            response = await client.post(f"{BASE_URL}/api/v1/backends/sync")
            print(f"   ✅ Backend sync: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   🔄 Message: {data.get('message', 'unknown')}")
        except Exception as e:
            print(f"   ❌ Backend sync: {e}")
        
        # Wait a moment for sync to process
        await asyncio.sleep(2)
        
        # Test backends list
        print("\n5. Testing backends list...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/backends/")
            print(f"   ✅ Backends list: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   🖥️  Backends count: {len(data)}")
                if data:
                    print(f"   🔧 First backend: {data[0].get('name', 'unknown')}")
        except Exception as e:
            print(f"   ❌ Backends list: {e}")
        
        # Test jobs sync
        print("\n6. Testing jobs sync...")
        try:
            response = await client.post(f"{BASE_URL}/api/v1/jobs/sync?limit=10")
            print(f"   ✅ Job sync: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   🔄 Message: {data.get('message', 'unknown')}")
        except Exception as e:
            print(f"   ❌ Job sync: {e}")
        
        # Wait a moment for sync to process
        await asyncio.sleep(2)
        
        # Test jobs list
        print("\n7. Testing jobs list...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/jobs/?per_page=5")
            print(f"   ✅ Jobs list: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   💼 Total jobs: {data.get('total', 0)}")
                print(f"   📄 Items in page: {len(data.get('items', []))}")
        except Exception as e:
            print(f"   ❌ Jobs list: {e}")
        
        # Test queue info
        print("\n8. Testing queue info...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/queue/summary")
            print(f"   ✅ Queue summary: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ⏳ Queued jobs: {data.get('total_queued_jobs', 0)}")
        except Exception as e:
            print(f"   ❌ Queue info: {e}")
        
        # Test analytics
        print("\n9. Testing analytics...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/analytics/status-distribution")
            print(f"   ✅ Analytics: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   📈 Distribution items: {len(data.get('distribution', []))}")
        except Exception as e:
            print(f"   ❌ Analytics: {e}")
        
        # Test dashboard refresh
        print("\n10. Testing dashboard refresh...")
        try:
            response = await client.post(f"{BASE_URL}/api/v1/dashboard/refresh")
            print(f"   ✅ Dashboard refresh: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   🔄 Message: {data.get('message', 'unknown')}")
        except Exception as e:
            print(f"   ❌ Dashboard refresh: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 API testing completed!")
        print("\nNext steps:")
        print("- Open http://localhost:8000/docs for interactive API docs")
        print("- Use WebSocket endpoints for real-time updates")
        print("- Add your IBM Quantum token to .env for real data")

async def test_websocket():
    """Test WebSocket connection"""
    print("\n🔌 Testing WebSocket connection...")
    try:
        import websockets
        
        uri = "ws://localhost:8000/api/v1/ws/dashboard"
        async with websockets.connect(uri) as websocket:
            print("   ✅ WebSocket connected successfully")
            
            # Wait for a message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                data = json.loads(message)
                print(f"   📨 Received: {data.get('type', 'unknown')} message")
            except asyncio.TimeoutError:
                print("   ⏰ No message received (timeout - this is normal)")
    except ImportError:
        print("   ⚠️  websockets package not available - skipping WebSocket test")
    except Exception as e:
        print(f"   ❌ WebSocket test failed: {e}")

def main():
    """Main test function"""
    print("Starting Quantum Jobs Tracker API Tests")
    print("Make sure the server is running on http://localhost:8000")
    print()
    
    asyncio.run(test_api_endpoints())
    asyncio.run(test_websocket())

if __name__ == "__main__":
    main()
