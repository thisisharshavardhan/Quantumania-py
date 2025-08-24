import React, { useState, useEffect, useCallback, useRef } from 'react'
import { RefreshCw } from 'lucide-react'

// API helper (assumes backend on :8000)
const API = (p) => `${location.origin.replace(/:\d+$/, ':8000')}/api/v1${p}`
// TEMP user id (replace with real auth integration). Leave blank to hide My Jobs stat.
const DEMO_USER_ID = 'user_1'

// Reusable components
function Card({ title, children, className='' }) {
  return <div className={`card-modern p-4 flex flex-col gap-3 ${className}`}>
    {title && <h3 className="text-[11px] font-semibold tracking-wide text-muted-foreground uppercase opacity-70">{title}</h3>}
    {children}
  </div>
}

function useAnimatedNumber(value, duration=600){
  const [display,setDisplay] = useState(value)
  const fromRef = useRef(value)
  const startRef = useRef(null)
  useEffect(()=>{
    if(typeof value !== 'number'){ setDisplay(value); fromRef.current = value; return }
    const from = fromRef.current
    const to = value
    if(from === to) return
    fromRef.current = to
    startRef.current = null
    let raf
    const step = (ts)=>{
      if(startRef.current==null) startRef.current = ts
      const p = Math.min(1, (ts - startRef.current)/duration)
      const eased = p<0.5? 2*p*p : -1 + (4 - 2*p)*p // easeInOutQuad
      const current = from + (to - from)*eased
      setDisplay(Number.isFinite(current)? current : to)
      if(p<1) raf = requestAnimationFrame(step)
    }
    raf = requestAnimationFrame(step)
    return ()=> cancelAnimationFrame(raf)
  },[value,duration])
  return typeof display === 'number'? Math.round(display) : display
}

function Stat({ label, value, note }) {
  const animated = useAnimatedNumber(typeof value === 'number'? value : value)
  return <div className="flex flex-col group">
    <span className="text-[11px] uppercase tracking-wide text-muted-foreground font-semibold opacity-80 mb-1">{label}</span>
    <span className="text-3xl font-bold leading-tight tabular-nums stat-accent bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">{animated ?? '—'}</span>
    {note && <span className="text-xs text-muted-foreground mt-1 opacity-75">{note}</span>}
  </div>
}

function Table({ columns, rows, keyField }) {
  return <div className="overflow-x-auto">
    <table className="w-full text-sm border-collapse">
      <thead>
        <tr className="text-[11px] uppercase tracking-wide text-muted-foreground">
          {columns.map(c => <th key={c.key} className="text-left font-medium py-2 px-2 border-b border-border">{c.header}</th>)}
        </tr>
      </thead>
      <tbody>
        {rows?.length ? rows.map(r => (
          <tr key={r[keyField] || Math.random()} className="hover:bg-muted/40">
            {columns.map(c => <td key={c.key} className="py-1.5 px-2 align-top border-b border-border/60">{c.render ? c.render(r) : r[c.key]}</td>)}
          </tr>
        )) : <tr><td colSpan={columns.length} className="py-6 text-center text-muted-foreground text-xs">No data</td></tr>}
      </tbody>
    </table>
  </div>
}

const Pill = ({ children, tone='default' }) => {
  const toneClasses = {
    'ok': 'status-done',
    'warn': 'status-running', 
    'err': 'status-error',
    'default': 'status-queued'
  }
  return <span className={`status-indicator ${toneClasses[tone]}`}>{children}</span>
}

function sortableHeader(label,key,state,setState){
  const active = state.key===key
  const dir = active? state.dir: undefined
  return <span className="th-sortable" data-active={active? 'true':'false'} data-dir={dir} onClick={()=> setState(s=> s.key===key? {key,dir:s.dir==='asc'?'desc':'asc'}:{key,dir:'asc'})}>{label}</span>
}

function timeAgo(ts){ if(!ts) return '—'; const d=new Date(ts); const diff=(Date.now()-d.getTime())/1000; if(diff<60) return Math.floor(diff)+'s'; if(diff<3600) return Math.floor(diff/60)+'m'; if(diff<86400) return Math.floor(diff/3600)+'h'; return d.toLocaleDateString(); }

export default function App(){
  // Unified state
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [dashboard, setDashboard] = useState(null)
  const [backendStats, setBackendStats] = useState(null)
  const [backendList, setBackendList] = useState([])
  const [jobsPage, setJobsPage] = useState(null)
  const [jobsFilters, setJobsFilters] = useState({ status:'', backend:'', page:1 })
  const [queueData, setQueueData] = useState([])
  const [perf, setPerf] = useState(null)
  const [statusDist, setStatusDist] = useState(null)
  const [backendComp, setBackendComp] = useState(null)
  const [myJobCount,setMyJobCount] = useState(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshTick, setRefreshTick] = useState(0)
  // Lists UX
  const [backendSort,setBackendSort] = useState({key:'name',dir:'asc'})
  const [backendPage,setBackendPage] = useState(1)
  const backendsPerPage = 25
  const [queueSort,setQueueSort] = useState({key:'backend_name',dir:'asc'})
  const [queuePage,setQueuePage] = useState(1)
  const queuePerPage = 20
  const [globalSearch, setGlobalSearch] = useState('')
  const [openSections, setOpenSections] = useState({
    overview: true,
    jobs: true,
  backends: true,
    queue: false,
    analytics: false,
  })
  // Removed tabbed view state (reverting to separate sections)
  // unified theme: no selection needed

  const fetchJSON = async (url) => {
    const r = await fetch(url)
    if(!r.ok) throw new Error(r.status+' '+r.statusText)
    return r.json()
  }

  const loadCore = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const [dash, bStats, bList, queue, perfM, dist, comp] = await Promise.all([
        fetchJSON(API('/dashboard')),
        fetchJSON(API('/backends/live-metrics')),
        fetchJSON(API('/backends')),
        fetchJSON(API('/queue')),
        fetchJSON(API('/analytics/performance-metrics')),
        fetchJSON(API('/analytics/status-distribution')),
        fetchJSON(API('/analytics/backend-comparison'))
      ])
      setDashboard(dash)
      setBackendStats(bStats)
      setBackendList(bList)
      setQueueData(queue)
      setPerf(perfM)
      setStatusDist(dist)
      setBackendComp(comp)
      // fetch my jobs count only if user id defined
      if(DEMO_USER_ID){
        try {
          const my = await fetchJSON(API(`/jobs?per_page=1&page=1&user_id=${encodeURIComponent(DEMO_USER_ID)}`))
          setMyJobCount(my.total || my.total_items || my.total_jobs || my.count || my.items?.length || 0)
        } catch { setMyJobCount(null) }
      }
    } catch(e){ setError(e.message) }
    finally { setLoading(false) }
  }, [])

  const loadJobs = useCallback(async () => {
    try {
      const qp = new URLSearchParams({ per_page:'25', page:String(jobsFilters.page) })
      if(jobsFilters.status) qp.append('status', jobsFilters.status)
      if(jobsFilters.backend) qp.append('backend', jobsFilters.backend)
      const data = await fetchJSON(API('/jobs?'+qp.toString()))
      setJobsPage(data)
    } catch(e){ /* silent job load error */ }
  }, [jobsFilters])

  // Initial + periodic refresh
  useEffect(()=>{ loadCore(); loadJobs(); }, [loadCore, loadJobs, refreshTick])
  useEffect(()=>{ loadJobs(); }, [jobsFilters, loadJobs])

  useEffect(()=>{
    if(!autoRefresh) return
    const id = setInterval(()=> setRefreshTick(t=>t+1), 30000)
    return ()=> clearInterval(id)
  }, [autoRefresh])

  const setFilter = (k,v)=> setJobsFilters(f=>({...f, page: k==='status'||k==='backend'?1:f.page, [k]:v }))
  const toggleSection = id => setOpenSections(s=>({...s, [id]: !s[id]}))

  // Derived filtered data (simple substring case-insensitive)
  const search = globalSearch.trim().toLowerCase()
  const filteredRecentJobs = search && dashboard? dashboard.recent_jobs.filter(j=> [j.job_id,j.backend_name,j.status].some(x=> String(x).toLowerCase().includes(search))) : dashboard?.recent_jobs
  let filteredBackends = search? backendList.filter(b=> [b.name,b.status,b.n_qubits].some(x=> String(x).toLowerCase().includes(search))) : backendList
  // Sorting backends
  filteredBackends = [...filteredBackends].sort((a,b)=>{
    const k = backendSort.key
    const av = a[k] ?? ''
    const bv = b[k] ?? ''
    if(av < bv) return backendSort.dir==='asc'? -1:1
    if(av > bv) return backendSort.dir==='asc'? 1:-1
    return 0
  })
  const backendTotalPages = Math.max(1, Math.ceil(filteredBackends.length / backendsPerPage))
  const backendPageSafe = Math.min(backendPage, backendTotalPages)
  const backendSlice = filteredBackends.slice((backendPageSafe-1)*backendsPerPage, backendPageSafe*backendsPerPage)

  let filteredQueue = search? queueData.filter(q=> [q.backend_name,q.status].some(x=> String(x).toLowerCase().includes(search))) : queueData
  filteredQueue = [...filteredQueue].sort((a,b)=>{
    const k = queueSort.key
    const av = a[k] ?? ''
    const bv = b[k] ?? ''
    if(av < bv) return queueSort.dir==='asc'? -1:1
    if(av > bv) return queueSort.dir==='asc'? 1:-1
    return 0
  })
  const queueTotalPages = Math.max(1, Math.ceil(filteredQueue.length / queuePerPage))
  const queuePageSafe = Math.min(queuePage, queueTotalPages)
  const queueSlice = filteredQueue.slice((queuePageSafe-1)*queuePerPage, queuePageSafe*queuePerPage)
  const filteredComp = search && backendComp? { backends: backendComp.backends.filter(b=> [b.name,b.status].some(x=> String(x).toLowerCase().includes(search))) } : backendComp

  return <div className="min-h-screen flex flex-col">
    <header className="glass sticky top-0 z-40 px-6 py-4 flex flex-wrap gap-4 items-center justify-between">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-blue-100 to-blue-200 bg-clip-text text-transparent">⚛️ Quantum Dashboard</h1>
        {loading && <span className="text-xs text-muted-foreground flex items-center gap-2">
          <div className="w-3 h-3 border border-primary border-t-transparent rounded-full animate-spin"></div>
          Loading...
        </span>}
        {error && <span className="text-xs text-red-400 bg-red-500/10 px-2 py-1 rounded">{error}</span>}
      </div>
      <div className="flex items-center gap-3 text-xs">
        <input value={globalSearch} onChange={e=>setGlobalSearch(e.target.value)} placeholder="🔍 Search jobs, backends…" className="glass-subtle rounded-lg px-3 py-2 text-xs w-64 focus:outline-none focus:ring-2 focus:ring-primary/50" />
        <button onClick={()=>{setRefreshTick(t=>t+1)}} className="btn-modern"><RefreshCw className="w-3.5 h-3.5"/>Refresh</button>
        <label className="flex items-center gap-2 cursor-pointer select-none text-muted-foreground">
          <input type="checkbox" checked={autoRefresh} onChange={e=>setAutoRefresh(e.target.checked)} className="accent-primary" /> Auto-refresh
        </label>
        <span className="pill-soft">Modern Dark</span>
      </div>
    </header>
    <main className="flex-1 overflow-y-auto p-6 space-y-8">
      {globalSearch && <div className="glass-subtle p-3 rounded-lg text-sm">
        <span className="text-muted-foreground">🔍 Filtering results for:</span> 
        <span className="text-primary font-semibold ml-2">{globalSearch}</span>
      </div>}
      
      {/* Overview Section */}
      {openSections.overview && <section id="overview" className="space-y-6">
        <div className="section-header">
          <h2 className="section-title">📊 System Overview</h2>
          <button onClick={()=>toggleSection('overview')} className="text-xs text-muted-foreground hover:text-foreground transition-colors">Collapse</button>
        </div>
        {dashboard && <>
          <div className="grid-auto-fit">
            {loading ? Array.from({length:5}).map((_,i)=> <Card key={i}><div className="skeleton h-16 w-full"/></Card>) : <>
              {myJobCount!=null && <Card><Stat label="My Jobs" value={myJobCount} note={`Of ${dashboard.job_stats.total_jobs} total`} /></Card>}
              <Card><Stat label={myJobCount!=null? 'Public Jobs':'Total Jobs'} value={myJobCount!=null? (dashboard.job_stats.total_jobs - myJobCount): dashboard.job_stats.total_jobs} note={`✅ ${dashboard.job_stats.completed_jobs} • 🏃 ${dashboard.job_stats.running_jobs}`} /></Card>
              <Card><Stat label="Queued Jobs" value={dashboard.job_stats.queued_jobs} note={`❌ ${dashboard.job_stats.error_jobs} errors`}/></Card>
              <Card><Stat label="Backends" value={dashboard.backend_stats.total_backends} note={`🟢 ${dashboard.backend_stats.operational_backends} active`}/></Card>
              <Card><Stat label="Avg Queue Time" value={dashboard.job_stats.average_queue_time? Number(dashboard.job_stats.average_queue_time).toFixed(0)*1:0} note={`⚡ ${(dashboard.job_stats.average_execution_time||0).toFixed?.(1)}s exec`} /></Card>
            </>}
          </div>
          <div className="space-y-4">
            <div className="subsection-title">
              <span>⏱️ Recent Activity</span>
              {search && <span className='text-muted-foreground font-normal text-sm'>(filtered)</span>}
              <span className="ml-auto text-xs text-muted-foreground">{filteredRecentJobs?.length || 0} jobs</span>
            </div>
            <div className="table-wrapper"> 
              <div className="compact-table">
                <Table keyField="job_id" rows={loading? []: filteredRecentJobs} columns={[
                  { key:'job_id', header:'Job ID', render: r=> <code className="text-[11px] font-mono bg-muted/30 px-1 py-0.5 rounded">{r.job_id}</code> },
                  { key:'status', header:'Status', render: r=> <Pill tone={r.status==='DONE'?'ok':r.status==='ERROR'?'err':r.status==='RUNNING'?'warn':'default'}>{r.status}</Pill> },
                  { key:'backend_name', header:'Backend', render: r=> <span className="font-medium">{r.backend_name}</span> },
                  { key:'shots', header:'Shots', render: r=> <span className="tabular-nums">{r.shots?.toLocaleString()}</span> },
                  { key:'created_at', header:'Created', render: r=> <span className="text-muted-foreground">{timeAgo(r.created_at)}</span> },
                ]} />
                {loading && <div className="p-6 space-y-3">{Array.from({length:6}).map((_,i)=><div key={i} className="skeleton h-8 w-full"/> )}</div>}
              </div>
            </div>
          </div>
        </>}
      </section>}

      {/* Backends Section */}
      {openSections.backends && <section id="backends" className="space-y-6">
        <div className="section-header">
          <h2 className="section-title">🖥️ Quantum Backends</h2>
          <button onClick={()=>toggleSection('backends')} className="text-xs text-muted-foreground hover:text-foreground transition-colors">Collapse</button>
        </div>
        {backendStats && <div className="grid-auto-fit">
          <Card>{loading? <div className="skeleton h-16"/>:<Stat label="Total Backends" value={backendStats.total_backends} note={`🟢 ${backendStats.operational_backends} operational`} />}</Card>
          <Card>{loading? <div className="skeleton h-16"/>:<Stat label="Total Qubits" value={backendStats.total_qubits} note={`📊 ${(backendStats.average_qubits||0).toFixed(1)} avg per backend`} />}</Card>
          <Card>{loading? <div className="skeleton h-16"/>:<Stat label="Pending Jobs" value={backendStats.total_pending_jobs} note={`📋 ${backendStats.backends_with_queues} backends with queues`} />}</Card>
          <Card>{loading? <div className="skeleton h-16"/>:<Stat label="Simulators" value={backendStats.simulators} note={`⚡ ${backendStats.real_devices} real devices`} />}</Card>
        </div>}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="subsection-title">
              <span>🔧 Backend Details</span>
              {search && <span className='text-muted-foreground font-normal text-sm'>(filtered)</span>}
            </div>
            <span className="text-xs text-muted-foreground">{filteredBackends.length} backends</span>
          </div>
          <div className="pagination-controls">
            <span>Page {backendPageSafe} of {backendTotalPages}</span>
            <div className="flex gap-2">
              <button disabled={backendPageSafe<=1} onClick={()=>setBackendPage(p=>Math.max(1,p-1))} className="pagination-btn">← Prev</button>
              <button disabled={backendPageSafe>=backendTotalPages} onClick={()=>setBackendPage(p=>Math.min(backendTotalPages,p+1))} className="pagination-btn">Next →</button>
            </div>
          </div>
          <div className="table-wrapper">
            <div className="compact-table">
              <Table keyField="name" rows={backendSlice} columns={[
                { key:'name', header: sortableHeader('Backend Name','name',backendSort,setBackendSort), render: r=> <span className="font-mono text-primary">{r.name}</span> },
                { key:'n_qubits', header: sortableHeader('Qubits','n_qubits',backendSort,setBackendSort), render: r=> <span className="font-bold tabular-nums">{r.n_qubits}</span> },
                { key:'status', header: sortableHeader('Status','status',backendSort,setBackendSort), render: r=> <Pill tone={r.status==='available'?'ok':'default'}>{r.status}</Pill> },
                { key:'simulator', header:'Type', render: r=> <span className={`pill-soft ${r.simulator?'text-info':'text-warning'}`}>{r.simulator?'🖥️ Sim':'⚛️ Real'}</span> },
                { key:'pending_jobs', header: sortableHeader('Queue','pending_jobs',backendSort,setBackendSort), render: r=> <span className="tabular-nums">{r.pending_jobs}</span> },
              ]} />
              {loading && <div className="p-6 space-y-3">{Array.from({length:8}).map((_,i)=><div key={i} className="skeleton h-8"/> )}</div>}
            </div>
          </div>
        </div>
      </section>}

      {/* Jobs Section */}
      {openSections.jobs && <section id="jobs" className="space-y-6">
        <div className="section-header">
          <div className="flex items-center gap-3">
            <h2 className="section-title">📋 Job Management</h2>
            <div className="flex items-center gap-2">
              <select value={jobsFilters.status} onChange={e=> setFilter('status', e.target.value)} className="glass-subtle rounded-md px-3 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-primary/50">
                <option value="">All Statuses</option>
                {['RUNNING','QUEUED','DONE','ERROR','CANCELLED'].map(s=> <option key={s}>{s}</option>)}
              </select>
              <input value={jobsFilters.backend} onChange={e=> setFilter('backend', e.target.value)} placeholder="Filter by backend" className="glass-subtle rounded-md px-3 py-1 text-xs w-32 focus:outline-none focus:ring-2 focus:ring-primary/50" />
            </div>
          </div>
          <button onClick={()=>toggleSection('jobs')} className="text-xs text-muted-foreground hover:text-foreground transition-colors">Collapse</button>
        </div>
        {jobsPage && <div className="space-y-4">
          <div className="pagination-controls">
            <span>Page {jobsPage.page} of {jobsPage.pages}</span>
            <div className="flex gap-2">
              <button disabled={jobsFilters.page<=1} onClick={()=> setJobsFilters(f=>({...f, page:f.page-1}))} className="pagination-btn">← Prev</button>
              <button disabled={jobsFilters.page>=jobsPage.pages} onClick={()=> setJobsFilters(f=>({...f, page:f.page+1}))} className="pagination-btn">Next →</button>
            </div>
          </div>
          <div className="table-wrapper">
            <div className="compact-table">
              <Table keyField="job_id" rows={jobsPage.items} columns={[
                { key:'job_id', header:'Job ID', render: r=> <code className="text-[11px] font-mono bg-muted/30 px-1 py-0.5 rounded">{r.job_id}</code> },
                { key:'status', header:'Status', render: r=> <Pill tone={r.status==='DONE'?'ok':r.status==='ERROR'?'err':r.status==='RUNNING'?'warn':'default'}>{r.status}</Pill> },
                { key:'backend_name', header:'Backend', render: r=> <span className="font-medium text-primary">{r.backend_name}</span> },
                { key:'shots', header:'Shots', render: r=> <span className="tabular-nums font-medium">{r.shots?.toLocaleString()}</span> },
                { key:'queue_time', header:'Queue Time', render: r=> <span className="tabular-nums text-muted-foreground">{r.queue_time}s</span> },
                { key:'run_time', header:'Runtime', render: r=> <span className="tabular-nums text-muted-foreground">{r.run_time}s</span> },
                { key:'created_at', header:'Created', render: r=> <span className="text-muted-foreground">{timeAgo(r.created_at)}</span> },
              ]} />
              {!jobsPage.items?.length && loading && <div className="p-6 space-y-3">{Array.from({length:12}).map((_,i)=><div key={i} className="skeleton h-8"/> )}</div>}
            </div>
          </div>
        </div>}
      </section>}

      {/* Queue Section */}
      {openSections.queue && <section id="queue" className="space-y-6">
        <div className="section-header">
          <h2 className="section-title">📊 Queue Status</h2>
          <button onClick={()=>toggleSection('queue')} className="text-xs text-muted-foreground hover:text-foreground transition-colors">Collapse</button>
        </div>
        <div className="space-y-4">
          <div className="pagination-controls">
            <span>Page {queuePageSafe} of {queueTotalPages}</span>
            <div className="flex gap-2">
              <button disabled={queuePageSafe<=1} onClick={()=>setQueuePage(p=>Math.max(1,p-1))} className="pagination-btn">← Prev</button>
              <button disabled={queuePageSafe>=queueTotalPages} onClick={()=>setQueuePage(p=>Math.min(queueTotalPages,p+1))} className="pagination-btn">Next →</button>
            </div>
          </div>
          <div className="table-wrapper">
            <div className="compact-table">
              <Table keyField="backend_name" rows={queueSlice} columns={[
                { key:'backend_name', header:'Backend', render: r=> <code className="text-[11px] font-mono text-primary">{r.backend_name}</code> },
                { key:'queue_length', header: sortableHeader('Queue Length','queue_length',queueSort,setQueueSort), render: r=> <span className="font-bold tabular-nums">{r.queue_length}</span> },
                { key:'pending_jobs', header: sortableHeader('Pending','pending_jobs',queueSort,setQueueSort), render: r=> <span className="tabular-nums">{r.pending_jobs}</span> },
                { key:'running_jobs', header: sortableHeader('Running','running_jobs',queueSort,setQueueSort), render: r=> <span className="tabular-nums text-warning">{r.running_jobs}</span> },
                { key:'average_wait_time', header: sortableHeader('Avg Wait','average_wait_time',queueSort,setQueueSort), render: r=> <span className="tabular-nums text-muted-foreground">{r.average_wait_time}s</span> },
                { key:'estimated_wait_time', header: sortableHeader('Est Wait','estimated_wait_time',queueSort,setQueueSort), render: r=> <span className="tabular-nums text-muted-foreground">{r.estimated_wait_time}s</span> },
                { key:'status', header:'Status', render: r=> <Pill tone={r.status==='available'?'ok':'default'}>{r.status}</Pill> },
              ]} />
              {loading && <div className="p-6 space-y-3">{Array.from({length:8}).map((_,i)=><div key={i} className="skeleton h-8"/> )}</div>}
            </div>
          </div>
        </div>
      </section>}

      {/* Analytics Section */}
      {openSections.analytics && <section id="analytics" className="space-y-6">
        <div className="section-header">
          <h2 className="section-title">📈 Analytics & Insights</h2>
          <button onClick={()=>toggleSection('analytics')} className="text-xs text-muted-foreground hover:text-foreground transition-colors">Collapse</button>
        </div>
        {perf && <div className="space-y-6">
          <div>
            <div className="subsection-title">⚡ Performance Metrics</div>
            <div className="grid-auto-fit">
              <Card><Stat label="Success Rate" value={`${perf.success_rate}%`} note={`🟢 ${perf.system_availability}% system availability`} /></Card>
              <Card><Stat label="Avg Queue Time" value={`${perf.average_queue_time}s`} note="⏱️ time in queue" /></Card>
              <Card><Stat label="Avg Execution" value={`${perf.average_execution_time}s`} note="⚡ processing time" /></Card>
              <Card><Stat label="Quantum Time" value={perf.total_quantum_time} note="🔬 total accumulated" /></Card>
            </div>
          </div>
        </div>}
        {statusDist && <Card title="📊 Job Status Distribution" className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {statusDist.distribution?.map(d=> <div key={d.status} className="pill-soft flex items-center gap-2">
              <span>{d.status}</span>
              <span className="font-bold">{d.count}</span>
              <span className="text-muted-foreground">({d.percentage.toFixed(1)}%)</span>
            </div>)}
          </div>
        </Card>}
        {filteredComp && <div className="space-y-4">
          <div className="subsection-title">🔍 Backend Comparison</div>
          <div className="table-wrapper">
            <div className="compact-table">
              <Table keyField="name" rows={filteredComp.backends?.slice(0,50) || []} columns={[
                { key:'name', header:'Backend', render: r=> <code className="text-[11px] font-mono text-primary">{r.name}</code> },
                { key:'n_qubits', header:'Qubits', render: r=> <span className="font-bold tabular-nums">{r.n_qubits}</span> },
                { key:'status', header:'Status', render: r=> <Pill tone={r.status==='available'?'ok':'default'}>{r.status}</Pill> },
                { key:'simulator', header:'Type', render: r=> <span className={`pill-soft ${r.simulator?'text-info':'text-warning'}`}>{r.simulator?'🖥️ Sim':'⚛️ Real'}</span> },
                { key:'job_count', header:'Jobs', render: r=> <span className="tabular-nums">{r.job_count}</span> },
                { key:'total_shots', header:'Total Shots', render: r=> <span className="tabular-nums">{r.total_shots?.toLocaleString()}</span> },
                { key:'pending_jobs', header:'Queue', render: r=> <span className="tabular-nums">{r.pending_jobs}</span> },
                { key:'estimated_wait_time', header:'Est Wait', render: r=> <span className="tabular-nums text-muted-foreground">{r.estimated_wait_time}s</span> },
              ]} />
            </div>
          </div>
        </div>}
      </section>}
    </main>
    <footer className="glass-subtle px-6 py-3 text-xs text-muted-foreground flex items-center justify-between">
      <span>⚛️ Quantum Jobs Monitor • Enhanced Dashboard v2.0</span>
      <span className="text-primary">Built with React + Tailwind</span>
    </footer>
  </div>
}
