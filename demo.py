#!/usr/bin/env python3
"""
Quantum Jobs Tracker Demo Script
Demonstrates all API endpoints and features
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print('='*60)

def print_response(response, title="Response"):
    """Print a formatted response"""
    print(f"\n📊 {title}:")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print(json.dumps(data, indent=2, default=str)[:1000] + "..." if len(str(data)) > 1000 else json.dumps(data, indent=2, default=str))
        except:
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
    else:
        print(f"Error: {response.text}")

def demo_basic_endpoints():
    """Demo basic API endpoints"""
    print_section("Basic API Endpoints")
    
    # Root endpoint
    print("🏠 Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "Root Endpoint")
    
    # Health check
    print("\n❤️ Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")

def demo_backends():
    """Demo backend endpoints"""
    print_section("Backend Management")
    
    # Sync backends
    print("🔄 Syncing backends from IBM Quantum...")
    response = requests.post(f"{BASE_URL}/api/v1/backends/sync")
    print_response(response, "Backend Sync")
    
    # Wait for sync
    time.sleep(2)
    
    # Get all backends
    print("\n🖥️ Getting all backends...")
    response = requests.get(f"{BASE_URL}/api/v1/backends/")
    print_response(response, "All Backends")
    
    # Get backend statistics
    print("\n📈 Getting backend statistics...")
    response = requests.get(f"{BASE_URL}/api/v1/backends/stats/overview")
    print_response(response, "Backend Stats")
    
    # Get operational backends only
    print("\n✅ Getting operational backends...")
    response = requests.get(f"{BASE_URL}/api/v1/backends/filter/operational")
    print_response(response, "Operational Backends")

def demo_jobs():
    """Demo job endpoints"""
    print_section("Job Management")
    
    # Sync jobs
    print("🔄 Syncing jobs from IBM Quantum...")
    response = requests.post(f"{BASE_URL}/api/v1/jobs/sync?limit=20")
    print_response(response, "Job Sync")
    
    # Wait for sync
    time.sleep(2)
    
    # Get recent jobs
    print("\n💼 Getting recent jobs...")
    response = requests.get(f"{BASE_URL}/api/v1/jobs/recent?limit=5")
    print_response(response, "Recent Jobs")
    
    # Get jobs with pagination
    print("\n📋 Getting paginated jobs...")
    response = requests.get(f"{BASE_URL}/api/v1/jobs/?page=1&per_page=5")
    print_response(response, "Paginated Jobs")
    
    # Get job statistics
    print("\n📊 Getting job statistics...")
    response = requests.get(f"{BASE_URL}/api/v1/jobs/stats/overview")
    print_response(response, "Job Statistics")

def demo_queue():
    """Demo queue management"""
    print_section("Queue Management")
    
    # Get queue summary
    print("⏳ Getting queue summary...")
    response = requests.get(f"{BASE_URL}/api/v1/queue/summary")
    print_response(response, "Queue Summary")
    
    # Get all queue info
    print("\n📊 Getting all queue information...")
    response = requests.get(f"{BASE_URL}/api/v1/queue/")
    print_response(response, "Queue Information")
    
    # Get shortest wait times
    print("\n⚡ Getting backends with shortest wait times...")
    response = requests.get(f"{BASE_URL}/api/v1/queue/shortest-wait")
    print_response(response, "Shortest Wait Times")

def demo_dashboard():
    """Demo dashboard features"""
    print_section("Dashboard Features")
    
    # Get complete dashboard data
    print("📊 Getting complete dashboard data...")
    response = requests.get(f"{BASE_URL}/api/v1/dashboard/")
    print_response(response, "Dashboard Data")
    
    # Get system status
    print("\n🔍 Getting system status...")
    response = requests.get(f"{BASE_URL}/api/v1/dashboard/system-status")
    print_response(response, "System Status")
    
    # Get metrics
    print("\n📈 Getting detailed metrics...")
    response = requests.get(f"{BASE_URL}/api/v1/dashboard/metrics")
    print_response(response, "Detailed Metrics")
    
    # Refresh dashboard data
    print("\n🔄 Refreshing dashboard data...")
    response = requests.post(f"{BASE_URL}/api/v1/dashboard/refresh")
    print_response(response, "Dashboard Refresh")

def demo_analytics():
    """Demo analytics features"""
    print_section("Analytics & Insights")
    
    # Get job status distribution
    print("📊 Getting job status distribution...")
    response = requests.get(f"{BASE_URL}/api/v1/analytics/status-distribution")
    print_response(response, "Status Distribution")
    
    # Get backend comparison
    print("\n🔍 Getting backend comparison...")
    response = requests.get(f"{BASE_URL}/api/v1/analytics/backend-comparison")
    print_response(response, "Backend Comparison")
    
    # Get performance metrics
    print("\n⚡ Getting performance metrics...")
    response = requests.get(f"{BASE_URL}/api/v1/analytics/performance-metrics")
    print_response(response, "Performance Metrics")
    
    # Get job trends
    print("\n📈 Getting job trends...")
    response = requests.get(f"{BASE_URL}/api/v1/analytics/job-trends?days=7")
    print_response(response, "Job Trends")
    
    # Get cost analysis
    print("\n💰 Getting cost analysis...")
    response = requests.get(f"{BASE_URL}/api/v1/analytics/cost-analysis")
    print_response(response, "Cost Analysis")
    
    # Get user activity
    print("\n👥 Getting user activity...")
    response = requests.get(f"{BASE_URL}/api/v1/analytics/user-activity")
    print_response(response, "User Activity")

def demo_advanced_features():
    """Demo advanced features"""
    print_section("Advanced Features")
    
    # Filter jobs by status
    print("🔍 Filtering jobs by status (DONE)...")
    response = requests.get(f"{BASE_URL}/api/v1/jobs/by-status/DONE?per_page=3")
    print_response(response, "Jobs by Status")
    
    # Filter jobs by backend
    print("\n🖥️ Filtering jobs by backend...")
    response = requests.get(f"{BASE_URL}/api/v1/jobs/by-backend/ibm_sherbrooke?per_page=3")
    print_response(response, "Jobs by Backend")
    
    # Get backend utilization
    print("\n📊 Getting backend utilization...")
    response = requests.get(f"{BASE_URL}/api/v1/backends/utilization/weekly")
    print_response(response, "Backend Utilization")
    
    # Get regional statistics
    print("\n🌍 Getting regional statistics...")
    response = requests.get(f"{BASE_URL}/api/v1/analytics/regional-stats")
    print_response(response, "Regional Statistics")

def main():
    """Main demo function"""
    print("🌟 QUANTUM JOBS TRACKER API DEMO")
    print("=" * 60)
    print("This demo showcases all the features of the Quantum Jobs Tracker API")
    print("Make sure the server is running on http://localhost:8000")
    print()
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
        return
    
    print("✅ Server is running! Starting demo...")
    
    # Run all demos
    demo_basic_endpoints()
    demo_backends()
    demo_jobs()
    demo_queue()
    demo_dashboard()
    demo_analytics()
    demo_advanced_features()
    
    print_section("Demo Complete!")
    print("🎉 Congratulations! You've seen all the major features of the Quantum Jobs Tracker API.")
    print()
    print("📚 Next Steps:")
    print("- Open http://localhost:8000/docs for interactive API documentation")
    print("- Add your IBM Quantum token to .env for real quantum data")
    print("- Build a frontend dashboard using these APIs")
    print("- Use WebSocket endpoints for real-time updates")
    print("- Extend the analytics for your specific use case")
    print()
    print("🚀 Happy hacking!")

if __name__ == "__main__":
    main()
