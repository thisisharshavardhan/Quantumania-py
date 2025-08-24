#!/bin/bash

# Simple cURL Testing Script for Quantum Jobs Tracker API
# Usage: ./test_simple.sh
# Make sure the server is running on http://localhost:8000

BASE_URL="http://localhost:8000"
API_BASE="${BASE_URL}/api/v1"

echo "=============================================="
echo "🧪 Testing Quantum Jobs Tracker API"
echo "=============================================="

# Check if server is running
echo "🔍 Checking server status..."
curl -s "$BASE_URL/health" > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ Server is not running. Start with: python run.py"
    exit 1
fi
echo "✅ Server is running!"
echo

# =============================================================================
# BASIC ENDPOINTS
# =============================================================================
echo "📋 BASIC ENDPOINTS"
echo "-------------------"

echo "1. Root endpoint:"
curl -s "$BASE_URL/" | head -10
echo -e "\n"

echo "2. Health check:"
curl -s "$BASE_URL/health"
echo -e "\n\n"

# =============================================================================
# JOBS API
# =============================================================================
echo "💼 JOBS API"
echo "------------"

echo "3. Sync jobs from IBM Quantum:"
curl -s -X POST "$API_BASE/jobs/sync?limit=10"
echo -e "\n"

echo "4. Get recent jobs:"
curl -s "$API_BASE/jobs/recent?limit=3"
echo -e "\n"

echo "5. Get job statistics:"
curl -s "$API_BASE/jobs/stats/overview"
echo -e "\n"

echo "6. Get jobs with pagination:"
curl -s "$API_BASE/jobs/?page=1&per_page=5"
echo -e "\n"

echo "7. Get jobs by status (DONE):"
curl -s "$API_BASE/jobs/by-status/DONE?per_page=3"
echo -e "\n\n"

# =============================================================================
# BACKENDS API
# =============================================================================
echo "🖥️ BACKENDS API"
echo "---------------"

echo "8. Sync backends from IBM Quantum:"
curl -s -X POST "$API_BASE/backends/sync"
echo -e "\n"

echo "9. Get all backends:"
curl -s "$API_BASE/backends/" | head -20
echo -e "\n"

echo "10. Get backend statistics:"
curl -s "$API_BASE/backends/stats/overview"
echo -e "\n"

echo "11. Get operational backends only:"
curl -s "$API_BASE/backends/filter/operational" | head -15
echo -e "\n"

echo "12. Get simulators only:"
curl -s "$API_BASE/backends/filter/simulators"
echo -e "\n\n"

# =============================================================================
# QUEUE API
# =============================================================================
echo "⏳ QUEUE API"
echo "------------"

echo "13. Get queue summary:"
curl -s "$API_BASE/queue/summary"
echo -e "\n"

echo "14. Get all queue information:"
curl -s "$API_BASE/queue/" | head -20
echo -e "\n"

echo "15. Get shortest wait times:"
curl -s "$API_BASE/queue/shortest-wait"
echo -e "\n\n"

# =============================================================================
# DASHBOARD API
# =============================================================================
echo "📊 DASHBOARD API"
echo "----------------"

echo "16. Get dashboard job stats:"
curl -s "$API_BASE/dashboard/stats/jobs"
echo -e "\n"

echo "17. Get dashboard backend stats:"
curl -s "$API_BASE/dashboard/stats/backends"
echo -e "\n"

echo "18. Get system status:"
curl -s "$API_BASE/dashboard/system-status"
echo -e "\n"

echo "19. Refresh dashboard data:"
curl -s -X POST "$API_BASE/dashboard/refresh"
echo -e "\n\n"

# =============================================================================
# ANALYTICS API
# =============================================================================
echo "📈 ANALYTICS API"
echo "----------------"

echo "20. Get job status distribution:"
curl -s "$API_BASE/analytics/status-distribution"
echo -e "\n"

echo "21. Get backend comparison:"
curl -s "$API_BASE/analytics/backend-comparison" | head -20
echo -e "\n"

echo "22. Get performance metrics:"
curl -s "$API_BASE/analytics/performance-metrics"
echo -e "\n"

echo "23. Get cost analysis:"
curl -s "$API_BASE/analytics/cost-analysis"
echo -e "\n"

echo "24. Get user activity:"
curl -s "$API_BASE/analytics/user-activity"
echo -e "\n\n"

# =============================================================================
# SUMMARY
# =============================================================================
echo "=============================================="
echo "🎉 Testing Complete!"
echo "=============================================="
echo "✅ Tested 24 major endpoints"
echo "📚 View full documentation at: http://localhost:8000/docs"
echo "🌐 WebSocket endpoints available at:"
echo "   • ws://localhost:8000/api/v1/ws/dashboard"
echo "   • ws://localhost:8000/api/v1/ws/jobs"
echo "   • ws://localhost:8000/api/v1/ws/queue"
echo "🚀 Ready for frontend development!"
