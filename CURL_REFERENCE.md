# Quantum Jobs Tracker API - cURL Quick Reference

Base URL: `http://localhost:8000`
API Base: `http://localhost:8000/api/v1`

## 🔍 Basic Endpoints

```bash
# Root endpoint - API information
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health

# API documentation
curl http://localhost:8000/docs
curl http://localhost:8000/openapi.json
```

## 💼 Jobs API

### Basic Job Operations
```bash
# Get all jobs (paginated)
curl http://localhost:8000/api/v1/jobs/

# Get recent jobs
curl http://localhost:8000/api/v1/jobs/recent

# Get recent jobs (limited)
curl http://localhost:8000/api/v1/jobs/recent?limit=5

# Get specific job
curl http://localhost:8000/api/v1/jobs/{job_id}

# Sync jobs from IBM Quantum
curl -X POST http://localhost:8000/api/v1/jobs/sync

# Sync limited jobs
curl -X POST "http://localhost:8000/api/v1/jobs/sync?limit=10"
```

### Job Statistics & Trends
```bash
# Get job statistics
curl http://localhost:8000/api/v1/jobs/stats/overview

# Get daily job trends
curl http://localhost:8000/api/v1/jobs/trends/daily

# Get job trends (specific days)
curl "http://localhost:8000/api/v1/jobs/trends/daily?days=7"
```

### Job Filtering
```bash
# Filter by status
curl http://localhost:8000/api/v1/jobs/by-status/DONE
curl http://localhost:8000/api/v1/jobs/by-status/RUNNING
curl http://localhost:8000/api/v1/jobs/by-status/QUEUED

# Filter by backend
curl http://localhost:8000/api/v1/jobs/by-backend/ibm_sherbrooke
curl http://localhost:8000/api/v1/jobs/by-backend/ibmq_qasm_simulator

# Advanced filtering with parameters
curl "http://localhost:8000/api/v1/jobs/?status=DONE&per_page=10&page=1"
curl "http://localhost:8000/api/v1/jobs/?backend=ibm_kyiv&status=RUNNING"
```

## 🖥️ Backends API

### Basic Backend Operations
```bash
# Get all backends
curl http://localhost:8000/api/v1/backends/

# Get specific backend
curl http://localhost:8000/api/v1/backends/ibm_sherbrooke
curl http://localhost:8000/api/v1/backends/ibmq_qasm_simulator

# Sync backends from IBM Quantum
curl -X POST http://localhost:8000/api/v1/backends/sync
```

### Backend Statistics & Utilization
```bash
# Get backend statistics
curl http://localhost:8000/api/v1/backends/stats/overview

# Get weekly utilization
curl http://localhost:8000/api/v1/backends/utilization/weekly
```

### Backend Filtering
```bash
# Get operational backends only
curl http://localhost:8000/api/v1/backends/filter/operational

# Get simulators only
curl http://localhost:8000/api/v1/backends/filter/simulators

# Get real quantum devices only
curl http://localhost:8000/api/v1/backends/filter/real-devices
```

### Backend Queue Information
```bash
# Get queue info for specific backend
curl http://localhost:8000/api/v1/backends/ibm_sherbrooke/queue
```

## ⏳ Queue API

```bash
# Get all queue information
curl http://localhost:8000/api/v1/queue/

# Get queue summary
curl http://localhost:8000/api/v1/queue/summary

# Get backends with longest wait times
curl http://localhost:8000/api/v1/queue/longest-wait

# Get backends with shortest wait times
curl http://localhost:8000/api/v1/queue/shortest-wait

# Get queue info for specific backend
curl http://localhost:8000/api/v1/queue/by-backend/ibm_sherbrooke
```

## 📊 Dashboard API

```bash
# Get complete dashboard data
curl http://localhost:8000/api/v1/dashboard/

# Get job statistics for dashboard
curl http://localhost:8000/api/v1/dashboard/stats/jobs

# Get backend statistics for dashboard
curl http://localhost:8000/api/v1/dashboard/stats/backends

# Get system status
curl http://localhost:8000/api/v1/dashboard/system-status

# Get dashboard health
curl http://localhost:8000/api/v1/dashboard/health

# Get detailed metrics
curl http://localhost:8000/api/v1/dashboard/metrics

# Refresh dashboard data
curl -X POST http://localhost:8000/api/v1/dashboard/refresh
```

## 📈 Analytics API

### Job Analytics
```bash
# Get job trends
curl http://localhost:8000/api/v1/analytics/job-trends

# Get job trends (specific period)
curl "http://localhost:8000/api/v1/analytics/job-trends?days=30"

# Get job status distribution
curl http://localhost:8000/api/v1/analytics/status-distribution
```

### Backend Analytics
```bash
# Get backend utilization
curl http://localhost:8000/api/v1/analytics/backend-utilization

# Get backend comparison
curl http://localhost:8000/api/v1/analytics/backend-comparison
```

### Performance & Business Analytics
```bash
# Get performance metrics
curl http://localhost:8000/api/v1/analytics/performance-metrics

# Get cost analysis
curl http://localhost:8000/api/v1/analytics/cost-analysis

# Get user activity
curl http://localhost:8000/api/v1/analytics/user-activity

# Get regional statistics
curl http://localhost:8000/api/v1/analytics/regional-stats
```

## 🔌 WebSocket Endpoints

**Note**: These require a WebSocket client, not cURL. Use with JavaScript or tools like `websocat`.

```bash
# Real-time dashboard updates
ws://localhost:8000/api/v1/ws/dashboard

# Real-time job updates
ws://localhost:8000/api/v1/ws/jobs

# Real-time queue updates
ws://localhost:8000/api/v1/ws/queue
```

### WebSocket Testing with JavaScript
```javascript
// Dashboard WebSocket
const dashboardWs = new WebSocket('ws://localhost:8000/api/v1/ws/dashboard');
dashboardWs.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Dashboard update:', data);
};

// Jobs WebSocket
const jobsWs = new WebSocket('ws://localhost:8000/api/v1/ws/jobs');
jobsWs.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Job update:', data);
};
```

## 🧪 Advanced Testing

### Error Testing
```bash
# Test non-existent endpoints
curl http://localhost:8000/api/v1/jobs/nonexistent_job
curl http://localhost:8000/api/v1/backends/nonexistent_backend
curl http://localhost:8000/api/v1/invalid_endpoint
```

### Parameter Testing
```bash
# Complex filtering
curl "http://localhost:8000/api/v1/jobs/?status=DONE&backend=ibm_sherbrooke&page=1&per_page=5"

# Large pagination
curl "http://localhost:8000/api/v1/jobs/?page=1&per_page=100"

# Date range filtering (URL encode dates)
curl "http://localhost:8000/api/v1/jobs/?start_date=2024-01-01T00:00:00Z&end_date=2024-12-31T23:59:59Z"
```

### Performance Testing
```bash
# Time a request
curl -w "Time: %{time_total}s\nStatus: %{http_code}\n" http://localhost:8000/api/v1/dashboard/stats/jobs

# Multiple requests for performance testing
for i in {1..5}; do
  curl -w "Request $i - Time: %{time_total}s\n" -s http://localhost:8000/api/v1/jobs/recent > /dev/null
done
```

## 🔧 Common Use Cases

### Building a Dashboard
```bash
# Get all data needed for a dashboard
curl http://localhost:8000/api/v1/dashboard/
curl http://localhost:8000/api/v1/jobs/recent?limit=10
curl http://localhost:8000/api/v1/queue/summary
curl http://localhost:8000/api/v1/analytics/status-distribution
```

### Monitoring System Health
```bash
# Check system status
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/dashboard/system-status
curl http://localhost:8000/api/v1/dashboard/metrics
```

### Analyzing Performance
```bash
# Performance analysis
curl http://localhost:8000/api/v1/analytics/performance-metrics
curl http://localhost:8000/api/v1/analytics/backend-utilization
curl http://localhost:8000/api/v1/jobs/trends/daily?days=30
```

### Finding Best Backends
```bash
# Find best backends to use
curl http://localhost:8000/api/v1/backends/filter/operational
curl http://localhost:8000/api/v1/queue/shortest-wait
curl http://localhost:8000/api/v1/analytics/backend-comparison
```

## 📱 Quick Test Commands

### Test Everything Script
```bash
# Run comprehensive tests
./test_endpoints.sh

# Run simple tests
./test_simple.sh
```

### One-liner Tests
```bash
# Quick health check
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ API is running" || echo "❌ API has issues"

# Quick data check
curl -s http://localhost:8000/api/v1/jobs/stats/overview | grep -q "total_jobs" && echo "✅ Data is available" || echo "❌ No data found"

# Quick backend check
curl -s http://localhost:8000/api/v1/backends/ | grep -q "name" && echo "✅ Backends loaded" || echo "❌ No backends found"
```

## 🚀 Getting Started

1. **Start the server**:
   ```bash
   python run.py
   ```

2. **Test basic connectivity**:
   ```bash
   curl http://localhost:8000/health
   ```

3. **Load initial data**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/backends/sync
   curl -X POST http://localhost:8000/api/v1/jobs/sync?limit=20
   ```

4. **View documentation**:
   ```bash
   # Open in browser: http://localhost:8000/docs
   ```

5. **Run comprehensive tests**:
   ```bash
   ./test_endpoints.sh
   ```

Happy testing! 🧪✨
