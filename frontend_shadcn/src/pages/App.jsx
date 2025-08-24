import React, { useState, useEffect, useCallback, useRef } from 'react'
import { RefreshCw } from 'lucide-react'

// API helper (assumes backend on :8000)
const API = (p) => `${location.origin.replace(/:\d+$/, ':8000')}/api/v1${p}`
// TEMP user id (replace with real auth integration). Leave blank to hide My Jobs stat.
const DEMO_USER_ID = 'user_1'

// Reusable components
function Card({ title, children, className='' }) {
  return <div className={`bg-card/60 backdrop-blur-sm border border-border/60 rounded-xl p-4 flex flex-col gap-2 shadow-sm card-modern ${className}`}>
    {title && <h3 className="text-[11px] font-semibold tracking-wide text-muted-foreground uppercase">{title}</h3>}
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
  return <div className="flex flex-col">
    <span className="text-[11px] uppercase tracking-wide text-muted-foreground font-medium">{label}</span>
    <span className="text-2xl font-semibold leading-tight tabular-nums transition-colors duration-300">{animated ?? '—'}{(typeof value==='string' && /%$/.test(value))? '' : ''}</span>
    {note && <span className="text-xs text-muted-foreground mt-0.5">{note}</span>}
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

const Pill = ({ children, tone='default' }) => <span className={`px-2 py-0.5 rounded-full text-[11px] font-medium ${tone==='ok'?'bg-emerald-500/15 text-emerald-400':tone==='warn'?'bg-amber-500/15 text-amber-400':tone==='err'?'bg-red-500/15 text-red-400':'bg-muted text-muted-foreground'}`}>{children}</span>

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
    <header className="border-b border-border/60 px-6 py-3 flex flex-wrap gap-4 items-center justify-between glass sticky top-0 z-40">
      <div className="flex items-center gap-4">
  <h1 className="text-lg font-semibold tracking-tight text-foreground">Quantum Unified Dashboard</h1>
        {loading && <span className="text-xs text-muted-foreground">Loading...</span>}
        {error && <span className="text-xs text-red-400">{error}</span>}
      </div>
      <div className="flex items-center gap-2 text-xs">
        <input value={globalSearch} onChange={e=>setGlobalSearch(e.target.value)} placeholder="Search jobs, backends…" className="bg-muted/60 border border-border/60 rounded-md px-2 py-1 text-xs w-56" />
  <button onClick={()=>{setRefreshTick(t=>t+1)}} className="btn-modern"><RefreshCw className="w-3.5 h-3.5"/>Refresh</button>
        <label className="flex items-center gap-1 cursor-pointer select-none">
          <input type="checkbox" checked={autoRefresh} onChange={e=>setAutoRefresh(e.target.checked)} className="accent-primary" /> Auto-refresh
        </label>
  <span className="text-[11px] px-2 py-1 rounded bg-muted/40 border border-border/50">Dark Theme</span>
      </div>
    </header>
    <main className="flex-1 overflow-y-auto p-6 space-y-6 compact-gap">
      {globalSearch && <div className="text-[11px] text-muted-foreground">Filtering results for: <span className="text-foreground font-medium">{globalSearch}</span></div>}
      {/* Overview Section */}
      {openSections.overview && <section id="overview" className="space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold tracking-tight text-foreground">Overview</h2>
          <button onClick={()=>toggleSection('overview')} className="text-[11px] text-muted-foreground hover:text-foreground">Collapse</button>
        </div>
        {dashboard && <>
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-5">
            {loading ? Array.from({length:5}).map((_,i)=> <Card key={i}><div className="skeleton h-14 w-full"/></Card>) : <>
              {myJobCount!=null && <Card><Stat label="My Jobs" value={myJobCount} note={"Of total " + dashboard.job_stats.total_jobs} /></Card>}
              <Card><Stat label={myJobCount!=null? 'Public Jobs':'Total Jobs'} value={myJobCount!=null? (dashboard.job_stats.total_jobs - myJobCount): dashboard.job_stats.total_jobs} note={`Done ${dashboard.job_stats.completed_jobs} • Run ${dashboard.job_stats.running_jobs}`} /></Card>
              <Card><Stat label="Queued" value={dashboard.job_stats.queued_jobs} note={`Error ${dashboard.job_stats.error_jobs}`}/></Card>
              <Card><Stat label="Backends" value={dashboard.backend_stats.total_backends} note={`Op ${dashboard.backend_stats.operational_backends}`}/></Card>
              <Card><Stat label="Avg Queue (s)" value={dashboard.job_stats.average_queue_time? Number(dashboard.job_stats.average_queue_time).toFixed(0)*1:0} note={`Exec ${(dashboard.job_stats.average_execution_time||0).toFixed?.(0)}s`} /></Card>
            </>}
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold tracking-wide">Recent Jobs {search && <span className='text-muted-foreground font-normal'>(filtered)</span>}</h3>
              <span className="text-[10px] text-muted-foreground">Showing {filteredRecentJobs?.length || 0}</span>
            </div>
            <div className="max-h-60 overflow-auto rounded-lg border border-border/50 compact-table"> 
              <Table keyField="job_id" rows={loading? []: filteredRecentJobs} columns={[
                { key:'job_id', header:'ID', render: r=> <code className="text-[11px] font-mono">{r.job_id}</code> },
                { key:'status', header:'Status', render: r=> <Pill tone={r.status==='DONE'?'ok':r.status==='ERROR'?'err':r.status==='RUNNING'?'warn':'default'}>{r.status}</Pill> },
                { key:'backend_name', header:'Backend' },
                { key:'shots', header:'Shots' },
                { key:'created_at', header:'Created', render: r=> timeAgo(r.created_at) },
              ]} />
              {loading && <div className="p-4 space-y-2">{Array.from({length:6}).map((_,i)=><div key={i} className="skeleton h-6 w-full"/> )}</div>}
            </div>
          </div>
        </>}
      </section>}

      {/* Backends Section */}
      {openSections.backends && <section id="backends" className="space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold tracking-tight text-foreground">Backends</h2>
          <button onClick={()=>toggleSection('backends')} className="text-[11px] text-muted-foreground hover:text-foreground">Collapse</button>
        </div>
        {backendStats && <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
          <Card>{loading? <div className="skeleton h-14"/>:<Stat label="Total" value={backendStats.total_backends} note={`Op ${backendStats.operational_backends}`} />}</Card>
          <Card>{loading? <div className="skeleton h-14"/>:<Stat label="Qubits" value={backendStats.total_qubits} note={`Avg Q ${(backendStats.average_qubits||0).toFixed(1)}`} />}</Card>
          <Card>{loading? <div className="skeleton h-14"/>:<Stat label="Pending" value={backendStats.total_pending_jobs} note={`Queues ${backendStats.backends_with_queues}`} />}</Card>
          <Card>{loading? <div className="skeleton h-14"/>:<Stat label="Sim / Real" value={backendStats.simulators} note={`Real ${backendStats.real_devices}`} />}</Card>
        </div>}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold tracking-wide">Backends {search && <span className='text-muted-foreground font-normal'>(filtered)</span>}</h3>
            <span className="text-[10px] text-muted-foreground">{filteredBackends.length} items</span>
          </div>
          <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
            <span>Page {backendPageSafe}/{backendTotalPages}</span>
            <div className="flex gap-1">
              <button disabled={backendPageSafe<=1} onClick={()=>setBackendPage(p=>Math.max(1,p-1))} className="px-2 py-0.5 rounded bg-muted/50 disabled:opacity-30">Prev</button>
              <button disabled={backendPageSafe>=backendTotalPages} onClick={()=>setBackendPage(p=>Math.min(backendTotalPages,p+1))} className="px-2 py-0.5 rounded bg-muted/50 disabled:opacity-30">Next</button>
            </div>
          </div>
          <div className="max-h-64 overflow-auto rounded-lg border border-border/50 compact-table">
            <Table keyField="name" rows={backendSlice} columns={[
              { key:'name', header: sortableHeader('Name','name',backendSort,setBackendSort) },
              { key:'n_qubits', header: sortableHeader('Qubits','n_qubits',backendSort,setBackendSort) },
              { key:'status', header: sortableHeader('Status','status',backendSort,setBackendSort) },
              { key:'simulator', header:'Type', render: r=> r.simulator?'Sim':'Real' },
              { key:'pending_jobs', header: sortableHeader('Pending','pending_jobs',backendSort,setBackendSort) },
            ]} />
            {loading && <div className="p-4 space-y-2">{Array.from({length:8}).map((_,i)=><div key={i} className="skeleton h-6"/> )}</div>}
          </div>
        </div>
      </section>}

      {/* Jobs Section */}
      {openSections.jobs && <section id="jobs" className="space-y-5">
        <div className="flex items-center gap-4 flex-wrap">
          <h2 className="text-xl font-semibold tracking-tight text-foreground">Jobs</h2>
          <select value={jobsFilters.status} onChange={e=> setFilter('status', e.target.value)} className="bg-muted border border-border rounded-md px-2 py-1 text-xs">
            <option value="">All Statuses</option>
            {['RUNNING','QUEUED','DONE','ERROR','CANCELLED'].map(s=> <option key={s}>{s}</option>)}
          </select>
          <input value={jobsFilters.backend} onChange={e=> setFilter('backend', e.target.value)} placeholder="Backend" className="bg-muted border border-border rounded-md px-2 py-1 text-xs" />
          <div className="flex items-center gap-2 text-xs text-muted-foreground">Page {jobsPage?.page} / {jobsPage?.pages}</div>
          <div className="flex gap-2">
            <button disabled={!jobsPage || jobsFilters.page<=1} onClick={()=> setJobsFilters(f=>({...f, page:f.page-1}))} className="px-2 py-1 rounded-md bg-muted/70 text-xs disabled:opacity-30">Prev</button>
            <button disabled={!jobsPage || jobsFilters.page>=jobsPage.pages} onClick={()=> setJobsFilters(f=>({...f, page:f.page+1}))} className="px-2 py-1 rounded-md bg-muted/70 text-xs disabled:opacity-30">Next</button>
          </div>
          <button onClick={()=>toggleSection('jobs')} className="ml-auto text-[11px] text-muted-foreground hover:text-foreground">Collapse</button>
        </div>
        {jobsPage && <div className="max-h-[460px] overflow-auto rounded-lg border border-border/50 relative compact-table">
          <Table keyField="job_id" rows={jobsPage.items} columns={[
            { key:'job_id', header:'ID', render: r=> <code className="text-[11px] font-mono">{r.job_id}</code> },
            { key:'status', header:'Status', render: r=> <Pill tone={r.status==='DONE'?'ok':r.status==='ERROR'?'err':r.status==='RUNNING'?'warn':'default'}>{r.status}</Pill> },
            { key:'backend_name', header:'Backend' },
            { key:'shots', header:'Shots' },
            { key:'queue_time', header:'Queue (s)' },
            { key:'run_time', header:'Run (s)' },
            { key:'created_at', header:'Created', render: r=> timeAgo(r.created_at) },
          ]} />
          {!jobsPage.items?.length && loading && <div className="p-4 space-y-2">{Array.from({length:12}).map((_,i)=><div key={i} className="skeleton h-6"/> )}</div>}
        </div>}
      </section>}

      {/* Queue Section */}
      {openSections.queue && <section id="queue" className="space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold tracking-tight text-foreground">Queue</h2>
          <button onClick={()=>toggleSection('queue')} className="text-[11px] text-muted-foreground hover:text-foreground">Collapse</button>
        </div>
        <div className="flex items-center justify-between text-[10px] text-muted-foreground">
          <span>Page {queuePageSafe}/{queueTotalPages}</span>
          <div className="flex gap-1">
            <button disabled={queuePageSafe<=1} onClick={()=>setQueuePage(p=>Math.max(1,p-1))} className="px-2 py-0.5 rounded bg-muted/50 disabled:opacity-30">Prev</button>
            <button disabled={queuePageSafe>=queueTotalPages} onClick={()=>setQueuePage(p=>Math.min(queueTotalPages,p+1))} className="px-2 py-0.5 rounded bg-muted/50 disabled:opacity-30">Next</button>
          </div>
        </div>
        <div className="max-h-64 overflow-auto rounded-lg border border-border/50 compact-table">
        <Table keyField="backend_name" rows={queueSlice} columns={[
          { key:'backend_name', header:'Backend', render: r=> <code className="text-[11px] font-mono">{r.backend_name}</code> },
          { key:'queue_length', header: sortableHeader('Queue','queue_length',queueSort,setQueueSort) },
          { key:'pending_jobs', header: sortableHeader('Pending','pending_jobs',queueSort,setQueueSort) },
          { key:'running_jobs', header: sortableHeader('Running','running_jobs',queueSort,setQueueSort) },
          { key:'average_wait_time', header: sortableHeader('Avg Wait','average_wait_time',queueSort,setQueueSort) },
          { key:'estimated_wait_time', header: sortableHeader('Est Wait','estimated_wait_time',queueSort,setQueueSort) },
          { key:'status', header:'Status' },
        ]} />
        {loading && <div className="p-4 space-y-2">{Array.from({length:8}).map((_,i)=><div key={i} className="skeleton h-6"/> )}</div>}
        </div>
      </section>}

      {/* Analytics Section */}
      {openSections.analytics && <section id="analytics" className="space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold tracking-tight text-foreground">Analytics</h2>
          <button onClick={()=>toggleSection('analytics')} className="text-[11px] text-muted-foreground hover:text-foreground">Collapse</button>
        </div>
        {perf && <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
          <Card><Stat label="Success %" value={perf.success_rate} note={`Avail ${perf.system_availability}%`} /></Card>
          <Card><Stat label="Avg Queue" value={perf.average_queue_time} note="s" /></Card>
          <Card><Stat label="Avg Exec" value={perf.average_execution_time} note="s" /></Card>
          <Card><Stat label="Quantum Time" value={perf.total_quantum_time} note="accumulated" /></Card>
        </div>}
        {statusDist && <Card title="Status Distribution">
          <div className="flex flex-wrap gap-2">
            {statusDist.distribution?.map(d=> <Pill key={d.status}>{d.status}: {d.count} ({d.percentage.toFixed(1)}%)</Pill>)}
          </div>
        </Card>}
        {filteredComp && <div className="space-y-2">
          <h3 className="text-sm font-semibold tracking-wide">Backend Comparison</h3>
          <div className="max-h-64 overflow-auto rounded-lg border border-border/50 compact-table">
          <Table keyField="name" rows={filteredComp.backends?.slice(0,80) || []} columns={[
            { key:'name', header:'Name', render: r=> <code className="text-[11px] font-mono">{r.name}</code> },
            { key:'n_qubits', header:'Qubits' },
            { key:'status', header:'Status' },
            { key:'simulator', header:'Type', render: r=> r.simulator?'Sim':'Real' },
            { key:'job_count', header:'Jobs' },
            { key:'total_shots', header:'Shots' },
            { key:'pending_jobs', header:'Pending' },
            { key:'estimated_wait_time', header:'Est Wait' },
          ]} />
          </div>
        </div>}
      </section>}
    </main>
    <footer className="px-6 py-4 text-[10px] text-muted-foreground border-t border-border">IBM Quantum Jobs Monitor • Single Page View</footer>
  </div>
}
