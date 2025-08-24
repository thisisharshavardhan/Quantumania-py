#!/bin/bash

# Quantum Jobs Tracker API - Complete cURL Testing Script
# This script tests all available endpoints in the Quantum Jobs Tracker API
# Make sure the server is running on http://localhost:8000

BASE_URL="http://localhost:8000"
API_BASE="${BASE_URL}/api/v1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}🚀 $1${NC}"
    echo -e "${BLUE}================================================${NC}"
}

# Function to print test headers
print_test() {
    echo -e "\n${YELLOW}📋 Testing: $1${NC}"
    echo -e "${YELLOW}Endpoint: $2${NC}"
    echo "---"
}

# Function to make curl request with formatting
curl_test() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4
    
    print_test "$description" "$endpoint"
    
    if [ "$method" = "GET" ]; then
        curl -s -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
             -H "Content-Type: application/json" \
             "$endpoint" | jq '.' 2>/dev/null || curl -s "$endpoint"
    elif [ "$method" = "POST" ]; then
        if [ -n "$data" ]; then
            curl -s -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
                 -X POST \
                 -H "Content-Type: application/json" \
                 -d "$data" \
                 "$endpoint" | jq '.' 2>/dev/null || curl -s -X POST "$endpoint"
        else
            curl -s -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
                 -X POST \
                 -H "Content-Type: application/json" \
                 "$endpoint" | jq '.' 2>/dev/null || curl -s -X POST "$endpoint"
        fi
    fi
    
    echo -e "\n"
}

# Check if server is running
echo -e "${GREEN}🔍 Checking if server is running...${NC}"
if ! curl -s "$BASE_URL/health" > /dev/null; then
    echo -e "${RED}❌ Server is not running on $BASE_URL${NC}"
    echo -e "${YELLOW}Please start the server with: python run.py${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Server is running!${NC}"
echo -e "${GREEN}🧪 Starting comprehensive API testing...${NC}"

# =============================================================================
# BASIC ENDPOINTS
# =============================================================================
print_section "Basic API Endpoints"

curl_test "GET" "$BASE_URL/" "Root endpoint - API information"
curl_test "GET" "$BASE_URL/health" "Health check endpoint"

# =============================================================================
# JOBS API ENDPOINTS
# =============================================================================
print_section "Jobs API Endpoints"

# Basic job endpoints
curl_test "GET" "$API_BASE/jobs/" "Get all jobs (paginated)"
curl_test "GET" "$API_BASE/jobs/?page=1&per_page=5" "Get jobs with pagination"
curl_test "GET" "$API_BASE/jobs/recent" "Get recent jobs"
curl_test "GET" "$API_BASE/jobs/recent?limit=3" "Get recent jobs (limited)"

# Job sync and statistics
curl_test "POST" "$API_BASE/jobs/sync" "Sync jobs from IBM Quantum"
curl_test "POST" "$API_BASE/jobs/sync?limit=10" "Sync limited jobs from IBM Quantum"
curl_test "GET" "$API_BASE/jobs/stats/overview" "Get job statistics overview"
curl_test "GET" "$API_BASE/jobs/trends/daily" "Get daily job trends"
curl_test "GET" "$API_BASE/jobs/trends/daily?days=7" "Get job trends (7 days)"

# Job filtering
curl_test "GET" "$API_BASE/jobs/by-status/DONE" "Get jobs by status (DONE)"
curl_test "GET" "$API_BASE/jobs/by-status/RUNNING" "Get running jobs"
curl_test "GET" "$API_BASE/jobs/by-status/QUEUED" "Get queued jobs"
curl_test "GET" "$API_BASE/jobs/by-backend/ibm_sherbrooke" "Get jobs by backend"
curl_test "GET" "$API_BASE/jobs/by-backend/ibmq_qasm_simulator" "Get simulator jobs"

# Advanced job filtering
curl_test "GET" "$API_BASE/jobs/?status=DONE&per_page=3" "Filter jobs by status with pagination"
curl_test "GET" "$API_BASE/jobs/?backend=ibm_kyiv&page=1" "Filter jobs by backend"

# =============================================================================
# BACKENDS API ENDPOINTS
# =============================================================================
print_section "Backends API Endpoints"

# Basic backend endpoints
curl_test "GET" "$API_BASE/backends/" "Get all quantum backends"
curl_test "POST" "$API_BASE/backends/sync" "Sync backends from IBM Quantum"
curl_test "GET" "$API_BASE/backends/stats/overview" "Get backend statistics"
curl_test "GET" "$API_BASE/backends/utilization/weekly" "Get weekly backend utilization"

# Backend filtering
curl_test "GET" "$API_BASE/backends/filter/operational" "Get operational backends only"
curl_test "GET" "$API_BASE/backends/filter/simulators" "Get simulator backends only"
curl_test "GET" "$API_BASE/backends/filter/real-devices" "Get real quantum devices only"

# Individual backend info (we'll try common backend names)
curl_test "GET" "$API_BASE/backends/ibm_sherbrooke" "Get specific backend (ibm_sherbrooke)"
curl_test "GET" "$API_BASE/backends/ibmq_qasm_simulator" "Get specific backend (simulator)"
curl_test "GET" "$API_BASE/backends/ibm_kyiv" "Get specific backend (ibm_kyiv)"

# Backend queue info
curl_test "GET" "$API_BASE/backends/ibm_sherbrooke/queue" "Get backend queue info"

# =============================================================================
# QUEUE API ENDPOINTS
# =============================================================================
print_section "Queue API Endpoints"

curl_test "GET" "$API_BASE/queue/" "Get all queue information"
curl_test "GET" "$API_BASE/queue/summary" "Get queue summary statistics"
curl_test "GET" "$API_BASE/queue/longest-wait" "Get backends with longest wait times"
curl_test "GET" "$API_BASE/queue/shortest-wait" "Get backends with shortest wait times"
curl_test "GET" "$API_BASE/queue/by-backend/ibm_sherbrooke" "Get queue info for specific backend"

# =============================================================================
# DASHBOARD API ENDPOINTS
# =============================================================================
print_section "Dashboard API Endpoints"

curl_test "GET" "$API_BASE/dashboard/" "Get complete dashboard data"
curl_test "GET" "$API_BASE/dashboard/stats/jobs" "Get dashboard job statistics"
curl_test "GET" "$API_BASE/dashboard/stats/backends" "Get dashboard backend statistics"
curl_test "GET" "$API_BASE/dashboard/system-status" "Get system status information"
curl_test "GET" "$API_BASE/dashboard/health" "Get dashboard health status"
curl_test "GET" "$API_BASE/dashboard/metrics" "Get detailed dashboard metrics"
curl_test "POST" "$API_BASE/dashboard/refresh" "Refresh dashboard data"

# =============================================================================
# ANALYTICS API ENDPOINTS
# =============================================================================
print_section "Analytics API Endpoints"

# Job analytics
curl_test "GET" "$API_BASE/analytics/job-trends" "Get job trends analysis"
curl_test "GET" "$API_BASE/analytics/job-trends?days=7" "Get job trends (7 days)"
curl_test "GET" "$API_BASE/analytics/job-trends?days=30" "Get job trends (30 days)"

# Backend analytics
curl_test "GET" "$API_BASE/analytics/backend-utilization" "Get backend utilization analytics"
curl_test "GET" "$API_BASE/analytics/backend-comparison" "Get backend comparison data"

# Status and performance analytics
curl_test "GET" "$API_BASE/analytics/status-distribution" "Get job status distribution"
curl_test "GET" "$API_BASE/analytics/performance-metrics" "Get performance metrics and KPIs"

# Business analytics
curl_test "GET" "$API_BASE/analytics/cost-analysis" "Get cost analysis data"
curl_test "GET" "$API_BASE/analytics/user-activity" "Get user activity analytics"
curl_test "GET" "$API_BASE/analytics/regional-stats" "Get regional usage statistics"

# =============================================================================
# ERROR TESTING - Test non-existent endpoints
# =============================================================================
print_section "Error Handling Tests"

curl_test "GET" "$API_BASE/jobs/nonexistent_job_id" "Test non-existent job ID"
curl_test "GET" "$API_BASE/backends/nonexistent_backend" "Test non-existent backend"
curl_test "GET" "$API_BASE/queue/by-backend/nonexistent" "Test non-existent backend queue"
curl_test "GET" "$API_BASE/invalid_endpoint" "Test invalid endpoint"

# =============================================================================
# ADVANCED PARAMETER TESTING
# =============================================================================
print_section "Advanced Parameter Testing"

# Complex job filtering
curl_test "GET" "$API_BASE/jobs/?status=DONE&page=1&per_page=2" "Complex job filtering"
curl_test "GET" "$API_BASE/jobs/?backend=ibm_sherbrooke&status=RUNNING" "Multi-parameter filtering"

# Date range testing (using URL encoding for dates)
current_date=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
week_ago=$(date -u -d '7 days ago' +"%Y-%m-%dT%H:%M:%SZ")
curl_test "GET" "$API_BASE/jobs/?start_date=${week_ago}&end_date=${current_date}&per_page=5" "Date range filtering"

# Pagination edge cases
curl_test "GET" "$API_BASE/jobs/?page=999&per_page=10" "Large page number test"
curl_test "GET" "$API_BASE/jobs/?page=1&per_page=1" "Minimal page size test"
curl_test "GET" "$API_BASE/jobs/?page=1&per_page=100" "Large page size test"

# =============================================================================
# WEBSOCKET TESTING PLACEHOLDER
# =============================================================================
print_section "WebSocket Information"

echo -e "${YELLOW}📡 WebSocket Endpoints (require WebSocket client):${NC}"
echo -e "   • Dashboard updates: ws://localhost:8000/api/v1/ws/dashboard"
echo -e "   • Job updates: ws://localhost:8000/api/v1/ws/jobs" 
echo -e "   • Queue updates: ws://localhost:8000/api/v1/ws/queue"
echo -e "${YELLOW}   Use a WebSocket client like websocat or browser JavaScript to test these.${NC}"

# =============================================================================
# PERFORMANCE TESTING
# =============================================================================
print_section "Performance Testing"

echo -e "${YELLOW}🚀 Running performance tests...${NC}"

# Time multiple requests to the same endpoint
print_test "Performance test - Multiple dashboard requests" "$API_BASE/dashboard/stats/jobs"
for i in {1..5}; do
    echo -e "${GREEN}Request $i:${NC}"
    curl -s -w "Response Time: %{time_total}s, Status: %{http_code}\n" "$API_BASE/dashboard/stats/jobs" > /dev/null
done

# =============================================================================
# API DOCUMENTATION ENDPOINTS
# =============================================================================
print_section "API Documentation"

curl_test "GET" "$BASE_URL/docs" "OpenAPI documentation (Swagger)"
curl_test "GET" "$BASE_URL/redoc" "ReDoc documentation"
curl_test "GET" "$BASE_URL/openapi.json" "OpenAPI specification JSON"

# =============================================================================
# SUMMARY
# =============================================================================
print_section "Testing Complete!"

echo -e "${GREEN}✅ All API endpoints have been tested!${NC}"
echo -e "${BLUE}📊 Summary of tested endpoints:${NC}"
echo -e "   • Basic endpoints: 2"
echo -e "   • Jobs API: 15+ endpoints"
echo -e "   • Backends API: 10+ endpoints"
echo -e "   • Queue API: 5 endpoints"
echo -e "   • Dashboard API: 7 endpoints"
echo -e "   • Analytics API: 9 endpoints"
echo -e "   • Error handling: 4 tests"
echo -e "   • Advanced parameters: 6 tests"
echo -e "   • Performance tests: 5 requests"
echo -e "   • Documentation: 3 endpoints"

echo -e "\n${GREEN}🎉 Total: 60+ endpoint tests completed!${NC}"

echo -e "\n${BLUE}📚 Next steps:${NC}"
echo -e "   • Visit ${YELLOW}http://localhost:8000/docs${NC} for interactive API documentation"
echo -e "   • Test WebSocket endpoints with a WebSocket client"
echo -e "   • Add your IBM Quantum token to .env for real data"
echo -e "   • Build your frontend application using these APIs"

echo -e "\n${GREEN}🚀 Happy hacking!${NC}"
