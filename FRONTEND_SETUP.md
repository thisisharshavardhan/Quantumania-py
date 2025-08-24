# Quantumania - Complete Quantum Jobs Tracker

A full-stack application for tracking live IBM Quantum computing jobs with a Python FastAPI backend and React frontend.

## 🏗️ Project Structure

```
Quantumania-py/
├── 🐍 Backend (Python FastAPI)
│   ├── app/
│   │   ├── api/                 # API route handlers
│   │   ├── core/               # Core configuration
│   │   ├── models/             # Database models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic
│   │   ├── utils/              # Utility functions
│   │   └── main.py            # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── run.py                 # Server startup script
│   └── .env                   # Environment variables
│
└── ⚛️ Frontend (React + TypeScript)
    ├── src/
    │   ├── components/         # React components
    │   │   ├── ui/            # ShadCN UI components
    │   │   ├── DashboardOverview.tsx
    │   │   ├── JobsTable.tsx
    │   │   └── BackendsGrid.tsx
    │   ├── lib/               # Utility functions
    │   ├── types/             # TypeScript definitions
    │   ├── App.tsx            # Main app component
    │   └── main.tsx          # App entry point
    ├── package.json           # Node dependencies
    ├── vite.config.ts        # Vite configuration
    ├── tailwind.config.js    # Tailwind CSS config
    └── setup.sh              # Setup script
```

## 🚀 Quick Start

### 1. Backend Setup (Already Running)
Your Python backend is configured and ready with real IBM Quantum data:

```bash
cd /home/harshavardhan/Documents/Projects/Quantumania-py
python run.py
```

### 2. Frontend Setup (New)
```bash
cd frontend
./setup.sh
npm run dev
```

## 🌟 Features

### Backend (Real IBM Quantum Data)
- ✅ **60+ API Endpoints** for comprehensive quantum data access
- ✅ **Real IBM Quantum Integration** - no mock data
- ✅ **WebSocket Support** for real-time updates
- ✅ **SQLite Database** with automatic sync
- ✅ **Comprehensive Testing** with cURL scripts

### Frontend (Modern React Dashboard)
- ✅ **Real-time Dashboard** with live data updates
- ✅ **ShadCN UI Components** for beautiful, accessible interface
- ✅ **TypeScript** for type-safe development
- ✅ **Tailwind CSS** for responsive design
- ✅ **Auto-refresh** every 15-30 seconds

## 📊 Dashboard Features

### Dashboard Overview Cards
- Total jobs count with active jobs indicator
- Completed jobs with success rate percentage
- Operational vs total backends ratio
- System status with color-coded health indicators

### Jobs Table
- Recent quantum jobs list with real-time updates
- Status badges (queued, running, completed, error)
- Backend information and execution details
- Queue positions and estimated wait times

### Backends Grid
- All available IBM Quantum backends
- Real-time status indicators (operational, maintenance, offline)
- Backend specifications (qubits, gates, location)
- Queue lengths and utilization metrics

## 🔌 API Integration

The frontend automatically connects to your backend on `http://localhost:8000`:

- **Dashboard Data**: `/api/v1/dashboard`
- **Jobs**: `/api/v1/jobs`
- **Backends**: `/api/v1/backends`
- **Queue Info**: `/api/v1/queue`
- **Analytics**: `/api/v1/analytics`

## 🎨 UI Components

Built with modern, accessible components:
- **Cards**: Dashboard metrics and information panels
- **Badges**: Status indicators with color coding
- **Tables**: Responsive data display
- **Loading States**: Skeleton loaders for smooth UX
- **Error Handling**: Graceful error display with retry options

## ⚡ Performance Features

- **Auto-refresh**: Data updates every 15-30 seconds
- **Error Recovery**: Automatic retry on API failures
- **Loading States**: Skeleton animations during data fetch
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Type Safety**: Full TypeScript coverage

## 🔐 Data Authenticity

- **Real IBM Quantum Data Only**: No mock data fallbacks
- **Live Updates**: Fresh data from IBM Quantum platform
- **Authentication Required**: Valid IBM Quantum token needed
- **Error Transparency**: Clear messages when data unavailable

## 🛠️ Development

### Running Both Services
1. **Backend** (Terminal 1):
   ```bash
   cd /home/harshavardhan/Documents/Projects/Quantumania-py
   /home/harshavardhan/Documents/Projects/Quantumania-py/.venv/bin/python run.py
   ```

2. **Frontend** (Terminal 2):
   ```bash
   cd frontend
   npm run dev
   ```

### Access Points
- **Frontend Dashboard**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000/health

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🎯 Next Steps

1. **Start Frontend**: Run `cd frontend && npm run dev`
2. **Open Dashboard**: Visit http://localhost:3000
3. **Explore Data**: View real IBM Quantum jobs and backends
4. **Customize**: Modify components in `src/components/`
5. **Deploy**: Use `npm run build` for production

Your quantum jobs tracker is ready to visualize real IBM Quantum computing data! 🚀
