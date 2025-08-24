# Quantum Jobs Tracker Backend

A comprehensive Python backend for tracking live/public quantum computing jobs from IBM Quantum. Built for hackathons and quantum computing research.

## ⚠️ IMPORTANT: REAL DATA ONLY

This application exclusively uses **REAL IBM Quantum data** - no mock data or fallbacks are provided. You must have:
- A valid IBM Quantum account
- An active IBM Quantum API token
- Proper network connectivity to IBM Quantum services

**The application will fail to start without proper IBM Quantum credentials.** This ensures data authenticity and prevents mock data confusion.

## Features

### 🚀 Core Functionality
- **Real-time Job Tracking**: Monitor live quantum computing jobs from IBM Quantum
- **Backend Information**: Comprehensive data on all available quantum backends
- **Queue Management**: Real-time queue information and wait time estimates
- **Analytics Dashboard**: Performance metrics, trends, and insights
- **WebSocket Support**: Real-time updates for dashboard components

### 📊 API Endpoints

#### Jobs API (`/api/v1/jobs`)
- `GET /` - Get paginated jobs with filtering
- `GET /recent` - Get recently created jobs
- `GET /{job_id}` - Get specific job details
- `POST /sync` - Sync jobs from IBM Quantum
- `GET /stats/overview` - Job statistics
- `GET /trends/daily` - Job trends over time
- `GET /by-backend/{backend_name}` - Jobs by backend
- `GET /by-status/{status}` - Jobs by status

#### Backends API (`/api/v1/backends`)
- `GET /` - Get all quantum backends
- `GET /{backend_name}` - Get specific backend details
- `POST /sync` - Sync backends from IBM Quantum
- `GET /stats/overview` - Backend statistics
- `GET /utilization/weekly` - Backend utilization data
- `GET /filter/operational` - Only operational backends
- `GET /filter/simulators` - Only simulators
- `GET /filter/real-devices` - Only real quantum devices

#### Queue API (`/api/v1/queue`)
- `GET /` - Get queue info for all backends
- `GET /summary` - Queue statistics summary
- `GET /longest-wait` - Backends with longest wait times
- `GET /shortest-wait` - Backends with shortest wait times
- `GET /by-backend/{backend_name}` - Queue info for specific backend

#### Dashboard API (`/api/v1/dashboard`)
- `GET /` - Complete dashboard data
- `GET /stats/jobs` - Job statistics
- `GET /stats/backends` - Backend statistics
- `GET /system-status` - System status information
- `POST /refresh` - Refresh all dashboard data
- `GET /health` - Service health check
- `GET /metrics` - Detailed metrics

#### Analytics API (`/api/v1/analytics`)
- `GET /job-trends` - Job trends analysis
- `GET /backend-utilization` - Backend utilization analytics
- `GET /status-distribution` - Job status distribution
- `GET /backend-comparison` - Compare backends
- `GET /performance-metrics` - Performance KPIs
- `GET /cost-analysis` - Cost analysis data
- `GET /user-activity` - User activity analytics
- `GET /regional-stats` - Regional usage statistics

#### WebSocket Endpoints
- `WS /api/v1/ws/dashboard` - Real-time dashboard updates
- `WS /api/v1/ws/jobs` - Real-time job updates
- `WS /api/v1/ws/queue` - Real-time queue updates

## Installation & Setup

### Prerequisites
- Python 3.8+
- **IBM Quantum account and API token** (REQUIRED - no mock data available)
- Virtual environment (recommended)

### Quick Start

1. **Clone and setup environment**:
```bash
cd /path/to/project
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment variables**:
   - Copy `.env.example` to `.env` and add your IBM Quantum token:
```bash
cp .env.example .env
# Edit .env file with your actual IBM Quantum token
IBM_QUANTUM_TOKEN=your_actual_token_here
IBM_QUANTUM_CHANNEL=ibm_quantum
```

**⚠️ CRITICAL**: Without a valid IBM Quantum token, the application will fail to start. No mock data is provided.

3. **Run the server**:
```bash
python run.py
```

4. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - ReDoc Documentation: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## Architecture

### Project Structure
```
app/
├── api/                 # API route handlers
│   ├── jobs.py         # Job-related endpoints
│   ├── backends.py     # Backend endpoints
│   ├── queue.py        # Queue management
│   ├── dashboard.py    # Dashboard data
│   ├── analytics.py    # Analytics endpoints
│   └── websockets.py   # WebSocket handlers
├── core/               # Core configuration
│   ├── config.py       # Settings and configuration
│   └── database.py     # Database setup
├── models/             # Database models
│   └── quantum_models.py
├── schemas/            # Pydantic schemas
│   └── quantum_schemas.py
├── services/           # Business logic
│   ├── quantum_service.py    # IBM Quantum integration
│   ├── database_service.py   # Database operations
│   └── data_sync_service.py  # Background sync
├── utils/              # Utility functions
│   └── helpers.py
└── main.py            # FastAPI application
```

### Database Schema
- **QuantumJob**: Complete job information and metadata
- **QuantumBackend**: Backend specifications and status
- **JobQueue**: Real-time queue information
- **SystemStatus**: Service health monitoring
- **UserSession**: Session management

### Key Features for Hackathons

#### 🔥 Rich Data Access
- **Comprehensive Job Data**: Status, timing, costs, results, errors
- **Backend Specifications**: Qubit counts, gate sets, coupling maps
- **Real-time Metrics**: Queue lengths, wait times, utilization
- **Historical Trends**: Job patterns, performance analytics

#### ⚡ Real-time Updates
- WebSocket connections for live data
- Background sync services
- Automatic data refresh

#### 📈 Analytics Ready
- Pre-built analytics endpoints
- Trend analysis and comparisons
- Performance metrics and KPIs
- Cost analysis data

#### 🛠 Developer Friendly
- Comprehensive API documentation
- Consistent REST API design
- Proper error handling
- CORS enabled for frontend integration

## Integration Examples

### Frontend Integration
```javascript
// Fetch recent jobs
const response = await fetch('http://localhost:8000/api/v1/jobs/recent?limit=10');
const jobs = await response.json();

// WebSocket for real-time updates
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/dashboard');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateDashboard(data);
};
```

### Data Analysis
```python
import requests

# Get job statistics
stats = requests.get('http://localhost:8000/api/v1/dashboard/stats/jobs').json()
print(f"Total jobs: {stats['total_jobs']}")

# Get backend utilization
utilization = requests.get('http://localhost:8000/api/v1/analytics/backend-utilization').json()
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `IBM_QUANTUM_TOKEN` | Your IBM Quantum API token | Required |
| `IBM_QUANTUM_INSTANCE` | IBM Quantum instance | ibm_quantum |
| `DATABASE_URL` | Database connection string | sqlite:///./quantum_jobs.db |
| `API_HOST` | API server host | 0.0.0.0 |
| `API_PORT` | API server port | 8000 |
| `DEBUG` | Enable debug mode | True |
| `LOG_LEVEL` | Logging level | INFO |

## API Authentication

Currently configured for public access. For production deployments, consider:
- JWT token authentication
- API key validation
- Rate limiting
- CORS policy updates

## Performance & Scaling

### Current Configuration
- SQLite database (development)
- Single-worker FastAPI server
- In-memory caching
- Background sync tasks

### Production Recommendations
- PostgreSQL/MySQL database
- Redis for caching and queues
- Multiple worker processes
- Load balancing
- Docker containerization

## Contributing

This backend is designed to be hackathon-ready with extensive data access and real-time capabilities. Key areas for extension:

1. **Additional Data Sources**: Integrate more quantum computing providers
2. **Enhanced Analytics**: Machine learning predictions, anomaly detection
3. **Notification System**: Alerts for job completion, queue changes
4. **User Management**: Authentication and personalized dashboards
5. **Export Features**: Data export in various formats

## Troubleshooting

### Common Issues

1. **IBM Quantum Connection**:
   - Verify your API token is correct
   - Check network connectivity
   - Ensure sufficient IBM Quantum credits

2. **Database Issues**:
   - Check file permissions for SQLite
   - Verify database path in configuration

3. **Port Conflicts**:
   - Change `API_PORT` in `.env` if 8000 is occupied

4. **Import Errors**:
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

## License

Built for hackathon use - feel free to modify and extend as needed!

---

**Happy Hacking! 🚀**

This backend provides everything you need to build an amazing quantum computing dashboard. The API is comprehensive, real-time capable, and ready for your frontend magic!
