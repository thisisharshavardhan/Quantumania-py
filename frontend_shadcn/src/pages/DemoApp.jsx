import React, { useEffect, useState, useRef } from 'react'
import { RefreshCw } from 'lucide-react'

// Simple utility components reused
const Card = ({ title, children, className='' }) => <div className={`bg-card/60 backdrop-blur-sm border border-border/60 rounded-xl p-4 flex flex-col gap-2 shadow-sm card-modern ${className}`}>
  {title && <h3 className="text-[11px] font-semibold tracking-wide text-muted-foreground uppercase">{title}</h3>}
  {children}
</div>

function useAnimatedNumber(value, duration=600){
  const [display,setDisplay] = useState(value)
  const fromRef = useRef(value)
  const startRef = useRef(null)
  useEffect(()=>{
    if(typeof value !== 'number'){ setDisplay(value); fromRef.current=value; return }
    const from = fromRef.current
    const to = value
    if(from===to) return
    fromRef.current = to
    startRef.current = null
    let raf
    const step=(ts)=>{
      if(startRef.current==null) startRef.current=ts
      const p=Math.min(1,(ts-startRef.current)/duration)
      const eased = p<0.5? 2*p*p : -1+(4-2*p)*p
      const cur = from + (to - from)*eased
      setDisplay(cur)
      if(p<1) raf=requestAnimationFrame(step)
    }
    raf=requestAnimationFrame(step)
    return ()=> cancelAnimationFrame(raf)
  },[value,duration])
  return typeof display === 'number'? Math.round(display): display
}

const Stat = ({ label, value, note }) => {
  const v = useAnimatedNumber(typeof value==='number'? value : value)
  return <div className="flex flex-col">
    <span className="text-[11px] uppercase tracking-wide text-muted-foreground font-medium">{label}</span>
    <span className="text-2xl font-semibold leading-tight tabular-nums">{v}</span>
    {note && <span className="text-xs text-muted-foreground mt-0.5">{note}</span>}
  </div>
}

const Pill = ({ children, tone='default' }) => <span className={`px-2 py-0.5 rounded-full text-[11px] font-medium ${tone==='ok'?'bg-emerald-500/15 text-emerald-400':tone==='warn'?'bg-amber-500/15 text-amber-400':tone==='err'?'bg-red-500/15 text-red-400':'bg-muted text-muted-foreground'}`}>{children}</span>

const Table = ({ columns, rows, keyField }) => <div className="overflow-x-auto">
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

const rand = (min,max)=> Math.floor(Math.random()*(max-min+1))+min
const pick = arr => arr[Math.floor(Math.random()*arr.length)]
const statuses = ['RUNNING','QUEUED','DONE','ERROR','CANCELLED']

function generateDemoState(seed){
  const total_backends = 12
  const operational = rand(8,12)
  const simulators = rand(2,4)
  const real_devices = total_backends - simulators
  const jobStats = {
    total_jobs: seed*25 + rand(900,1200),
    running_jobs: rand(10,60),
    queued_jobs: rand(50,180),
    completed_jobs: rand(800,1100),
    error_jobs: rand(5,40),
    cancelled_jobs: rand(0,20),
    average_queue_time: rand(40,400),
    average_execution_time: rand(20,200)
  }
  const backendStats = {
    total_backends,
    operational_backends: operational,
    maintenance_backends: total_backends-operational-rand(0,1),
    offline_backends: rand(0,2),
    simulators,
    real_devices,
    total_qubits: real_devices * rand(27,127),
    average_queue_length: rand(2,18)
  }
  const recent_jobs = Array.from({length:10}).map(()=>{
    const status = pick(statuses)
    return {
      job_id: 'job_'+Math.random().toString(36).slice(2,10),
      status,
      backend_name: 'ibm_'+pick(['oslo','kyiv','torino','sherbrooke','nairobi','perth']),
      shots: pick([1024,2048,4096,8192]),
      created_at: new Date(Date.now()-rand(0,3600*1000)).toISOString()
    }
  })
  const queue_info = Array.from({length: total_backends}).map((_,i)=>{
    const name = 'ibm_'+pick(['oslo','kyiv','torino','sherbrooke','nairobi','perth','quito','geneva'])
    const pending = rand(0,40)
    return {
      backend_name: name,
      queue_length: pending + rand(0,10),
      pending_jobs: pending,
      running_jobs: rand(0,10),
      average_wait_time: rand(30,300),
      estimated_wait_time: rand(30,600),
      status: pick(['operational','maintenance','off'])
    }
  })
  const system_status = [
    { service_name:'ibm_quantum_api', status:'healthy', response_time: Math.random()*0.4, last_check: new Date().toISOString() },
    { service_name:'database', status:'healthy', response_time: Math.random()*0.2, last_check: new Date().toISOString() },
    { service_name:'sync_worker', status: pick(['healthy','degraded']), response_time: Math.random()*0.6, last_check: new Date().toISOString() },
  ]
  const weekly_utilization = Array.from({length: real_devices+simulators}).map(()=>({
    backend: 'ibm_'+pick(['oslo','kyiv','torino','sherbrooke','nairobi','perth','quito','geneva']),
    job_count: rand(5,120),
    total_shots: rand(5e3,2e5)
  }))
  const performance = {
    success_rate: +(100 - (jobStats.error_jobs/jobStats.total_jobs)*100).toFixed(2),
    system_availability: +(backendStats.operational_backends/backendStats.total_backends*100).toFixed(2),
    average_queue_time: jobStats.average_queue_time,
    average_execution_time: jobStats.average_execution_time,
    total_quantum_time: jobStats.completed_jobs * jobStats.average_execution_time,
    throughput: { jobs_per_day: +(jobStats.total_jobs/30).toFixed(2), jobs_per_hour: +(jobStats.total_jobs/(30*24)).toFixed(2) }
  }
  const status_distribution = statuses.map(s=>({
    status: s,
    count: jobStats[(s.toLowerCase()+ '_jobs').replace('running_jobs','running_jobs').replace('queued_jobs','queued_jobs').replace('done_jobs','completed_jobs')] || rand(1,50)
  }))
  const totalDist = status_distribution.reduce((a,b)=>a+b.count,0)
  status_distribution.forEach(d=> d.percentage = d.count/totalDist*100)
  const backend_comparison = weekly_utilization.slice(0,8).map(u=>({
    name: u.backend,
    n_qubits: rand(5,127),
    status: pick(['operational','maintenance','off']),
    simulator: Math.random()<0.3,
    job_count: u.job_count,
    total_shots: u.total_shots,
    queue_length: rand(0,50),
    pending_jobs: rand(0,40),
    estimated_wait_time: rand(20,800)
  }))
  return { jobStats, backendStats, recent_jobs, queue_info, system_status, backend_utilization:{weekly_utilization}, performance, status_distribution, backend_comparison }
}

function timeAgo(ts){ if(!ts) return '—'; const d=new Date(ts); const diff=(Date.now()-d.getTime())/1000; if(diff<60) return Math.floor(diff)+'s'; if(diff<3600) return Math.floor(diff/60)+'m'; if(diff<86400) return Math.floor(diff/3600)+'h'; return d.toLocaleDateString(); }

function sortableHeader(label,key,state,setState){
  const active = state.key===key
  const dir = active? state.dir: undefined
  return <span className="th-sortable" data-active={active? 'true':'false'} data-dir={dir} onClick={()=> setState(s=> s.key===key? {key,dir:s.dir==='asc'?'desc':'asc'}:{key,dir:'asc'})}>{label}</span>
}


export default function DemoApp(){
  const [seed,setSeed] = useState(1)
  const [data,setData] = useState(()=>generateDemoState(seed))
  const [auto,setAuto] = useState(true)
  const [search,setSearch] = useState('')
  const [backendSort,setBackendSort] = useState({key:'backend',dir:'asc'})
  const [backendPage,setBackendPage] = useState(1)
  const backendsPerPage = 15
  const [queueSort,setQueueSort] = useState({key:'backend_name',dir:'asc'})
  const [queuePage,setQueuePage] = useState(1)
  const queuePerPage = 15
  // no chart history needed after removing graphs

  useEffect(()=>{ setData(generateDemoState(seed)) },[seed])
  useEffect(()=>{ if(!auto) return; const id=setInterval(()=> setSeed(s=>s+1), 6000); return ()=>clearInterval(id)},[auto])
  // removed history tracking

  const s = search.trim().toLowerCase()
  let backends = data.backend_utilization.weekly_utilization
  if(s) backends = backends.filter(b=> [b.backend,b.job_count,b.total_shots].some(x=> String(x).toLowerCase().includes(s)))
  backends = [...backends].sort((a,b)=>{ const k=backendSort.key; const av=a[k]??''; const bv=b[k]??''; if(av<bv) return backendSort.dir==='asc'?-1:1; if(av>bv) return backendSort.dir==='asc'?1:-1; return 0 })
  const backendTotalPages = Math.max(1, Math.ceil(backends.length/backendsPerPage))
  const backendPageSafe = Math.min(backendPage, backendTotalPages)
  const backendSlice = backends.slice((backendPageSafe-1)*backendsPerPage, backendPageSafe*backendsPerPage)

  let queues = data.queue_info
  if(s) queues = queues.filter(q=> [q.backend_name,q.status].some(x=> String(x).toLowerCase().includes(s)))
  queues = [...queues].sort((a,b)=>{ const k=queueSort.key; const av=a[k]??''; const bv=b[k]??''; if(av<bv) return queueSort.dir==='asc'?-1:1; if(av>bv) return queueSort.dir==='asc'?1:-1; return 0 })
  const queueTotalPages = Math.max(1, Math.ceil(queues.length/queuePerPage))
  const queuePageSafe = Math.min(queuePage, queueTotalPages)
  const queueSlice = queues.slice((queuePageSafe-1)*queuePerPage, queuePageSafe*queuePerPage)

  return <div className="min-h-screen flex flex-col">
  <header className="border-b border-border/60 px-6 py-4 flex flex-wrap gap-4 items-center justify-between glass">
  <div className="flex items-center gap-4">
  <h1 className="text-lg font-semibold tracking-tight text-foreground">Quantum Dashboard Demo</h1>
    <span className="text-xs text-muted-foreground">Synthetic rotating data</span>
      </div>
      <div className="flex items-center gap-3 text-xs">
  <input value={search} onChange={e=>{setSearch(e.target.value); setBackendPage(1); setQueuePage(1)}} placeholder="Search..." className="bg-muted/60 border border-border/60 rounded-md px-2 py-1 text-xs" />
  <button onClick={()=>setSeed(s=>s+1)} className="btn-modern"><RefreshCw className="w-3.5 h-3.5"/>Refresh</button>
        <label className="flex items-center gap-1 cursor-pointer select-none">
          <input type="checkbox" checked={auto} onChange={e=>setAuto(e.target.checked)} /> Auto
        </label>
      </div>
    </header>
  <main className="flex-1 overflow-y-auto p-6 space-y-8 compact-gap">
      {/* All Stats Section */}
      <section className="space-y-6" id="all-stats">
        <h2 className="text-xl font-semibold tracking-tight text-foreground">📊 System Overview</h2>
        
        {/* Job Stats */}
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-muted-foreground mb-3">Job Statistics</h3>
          <div className="grid gap-4 grid-cols-1 md:grid-cols-4">
            <Card><Stat label="Total Jobs" value={data.jobStats.total_jobs} note={`Running ${data.jobStats.running_jobs} / Queued ${data.jobStats.queued_jobs}`} /></Card>
            <Card><Stat label="Completed" value={data.jobStats.completed_jobs} note={`Errors ${data.jobStats.error_jobs}`} /></Card>
            <Card><Stat label="Avg Queue (s)" value={data.jobStats.average_queue_time} note={`Exec ${data.jobStats.average_execution_time}s`} /></Card>
            <Card><Stat label="Op Backends" value={data.backendStats.operational_backends} note={`${data.backendStats.total_backends} total`} /></Card>
          </div>
        </div>

        {/* Backend Stats */}
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-muted-foreground mb-3">Backend Statistics</h3>
          <div className="grid gap-4 grid-cols-1 md:grid-cols-4">
            <Card><Stat label="Total" value={data.backendStats.total_backends} note={`Sim ${data.backendStats.simulators} / Real ${data.backendStats.real_devices}`} /></Card>
            <Card><Stat label="Qubits" value={data.backendStats.total_qubits} note={`Avg Queue ${data.backendStats.average_queue_length?.toFixed?.(1)}`}/></Card>
            <Card><Stat label="Maint" value={data.backendStats.maintenance_backends} note={`Offline ${data.backendStats.offline_backends}`} /></Card>
            <Card><Stat label="Throughput/day" value={data.performance.throughput.jobs_per_day} note={`per hour ${data.performance.throughput.jobs_per_hour}`} /></Card>
          </div>
        </div>

        {/* Performance Analytics */}
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-muted-foreground mb-3">Performance Analytics</h3>
          <div className="grid gap-4 grid-cols-1 md:grid-cols-5">
            <Card><Stat label="Success %" value={data.performance.success_rate} note={`Avail ${data.performance.system_availability}%`} /></Card>
            <Card><Stat label="Avg Queue" value={data.performance.average_queue_time} note="seconds" /></Card>
            <Card><Stat label="Avg Exec" value={data.performance.average_execution_time} note="seconds" /></Card>
            <Card><Stat label="Quantum Time" value={data.performance.total_quantum_time} note="accumulated" /></Card>
            <Card><Stat label="Jobs/hr" value={data.performance.throughput.jobs_per_hour} note="throughput" /></Card>
          </div>
        </div>

        {/* System Status */}
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-muted-foreground mb-3">System Status</h3>
          <div className="grid gap-4 grid-cols-1 md:grid-cols-3 lg:grid-cols-4">
            {data.system_status.map(s=> <Card key={s.service_name} title={s.service_name}>
              <div className="flex items-center justify-between">
                <Pill tone={s.status==='healthy'?'ok':s.status==='degraded'?'warn':'err'}>{s.status}</Pill>
                <span className="text-[10px] text-muted-foreground">{(s.response_time*1000).toFixed(0)} ms</span>
              </div>
              <span className="text-[10px] text-muted-foreground">Updated {timeAgo(s.last_check)}</span>
            </Card>)}
          </div>
        </div>

        {/* Status Distribution */}
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-muted-foreground mb-3">Job Status Distribution</h3>
          <Card>
            <div className="flex flex-wrap gap-2">
              {data.status_distribution.map(d=> <Pill key={d.status}>{d.status}: {d.count} ({d.percentage.toFixed(1)}%)</Pill>)}
            </div>
          </Card>
        </div>
      </section>

      {/* All Tables Section */}
      <section className="space-y-8" id="all-tables">
        <h2 className="text-xl font-semibold tracking-tight text-foreground">📋 Data Tables</h2>
        
        {/* Recent Jobs Table */}
        <div className="space-y-3 compact-table">
          <h3 className="text-sm font-semibold tracking-wide">Recent Jobs</h3>
          <div className="table-wrapper">
            <Table keyField="job_id" rows={data.recent_jobs} columns={[
              { key:'job_id', header:'ID', render: r=> <code className="text-[11px] font-mono">{r.job_id}</code> },
              { key:'status', header:'Status', render: r=> <Pill tone={r.status==='DONE'?'ok':r.status==='ERROR'?'err':r.status==='RUNNING'?'warn':'default'}>{r.status}</Pill> },
              { key:'backend_name', header:'Backend' },
              { key:'shots', header:'Shots' },
              { key:'created_at', header:'Created', render: r=> timeAgo(r.created_at) },
            ]} />
          </div>
        </div>

        {/* Queue Table */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold tracking-wide">Queue Status</h3>
          <div className="flex items-center justify-between text-[10px] text-muted-foreground mb-1">
            <span>Page {queuePageSafe}/{queueTotalPages}</span>
            <div className="flex gap-1">
              <button disabled={queuePageSafe<=1} onClick={()=>setQueuePage(p=>Math.max(1,p-1))} className="px-2 py-0.5 rounded bg-muted/50 disabled:opacity-30">Prev</button>
              <button disabled={queuePageSafe>=queueTotalPages} onClick={()=>setQueuePage(p=>Math.min(queueTotalPages,p+1))} className="px-2 py-0.5 rounded bg-muted/50 disabled:opacity-30">Next</button>
            </div>
          </div>
          <div className="table-wrapper">
            <Table keyField="backend_name" rows={queueSlice} columns={[
              { key:'backend_name', header:'Backend', render: r=> <code className="text-[11px] font-mono">{r.backend_name}</code> },
              { key:'queue_length', header: sortableHeader('Queue','queue_length',queueSort,setQueueSort) },
              { key:'pending_jobs', header: sortableHeader('Pending','pending_jobs',queueSort,setQueueSort) },
              { key:'running_jobs', header: sortableHeader('Running','running_jobs',queueSort,setQueueSort) },
              { key:'average_wait_time', header: sortableHeader('Avg Wait','average_wait_time',queueSort,setQueueSort), render: r=> <span className="tabular-nums text-muted-foreground">{r.average_wait_time}s</span> },
              { key:'estimated_wait_time', header: sortableHeader('Est Wait','estimated_wait_time',queueSort,setQueueSort), render: r=> <span className="tabular-nums font-medium text-amber-400">{r.estimated_wait_time}s</span> },
              { key:'status', header:'Status', render: r=> <Pill tone={r.status==='operational'?'ok':r.status==='maintenance'?'warn':'err'}>{r.status}</Pill> },
            ]} />
          </div>
        </div>

        {/* Backend Utilization Table */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold tracking-wide">Weekly Utilization (jobs / shots)</h3>
          <div className="flex items-center justify-between text-[10px] text-muted-foreground mb-1">
            <span>Page {backendPageSafe}/{backendTotalPages}</span>
            <div className="flex gap-1">
              <button disabled={backendPageSafe<=1} onClick={()=>setBackendPage(p=>Math.max(1,p-1))} className="px-2 py-0.5 rounded bg-muted/50 disabled:opacity-30">Prev</button>
              <button disabled={backendPageSafe>=backendTotalPages} onClick={()=>setBackendPage(p=>Math.min(backendTotalPages,p+1))} className="px-2 py-0.5 rounded bg-muted/50 disabled:opacity-30">Next</button>
            </div>
          </div>
          <div className="table-wrapper">
            <Table keyField="backend" rows={backendSlice} columns={[
              { key:'backend', header: sortableHeader('Backend','backend',backendSort,setBackendSort), render: r=> <code className="text-[11px] font-mono">{r.backend}</code> },
              { key:'job_count', header: sortableHeader('Jobs','job_count',backendSort,setBackendSort) },
              { key:'total_shots', header: sortableHeader('Shots','total_shots',backendSort,setBackendSort) },
            ]} />
          </div>
        </div>

        {/* Backend Comparison Table */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold tracking-wide">Backend Comparison</h3>
          <div className="table-wrapper">
            <Table keyField="name" rows={data.backend_comparison} columns={[
              { key:'name', header:'Name', render: r=> <code className="text-[11px] font-mono">{r.name}</code> },
              { key:'n_qubits', header:'Qubits' },
              { key:'status', header:'Status', render: r=> <Pill tone={r.status==='operational'?'ok':r.status==='maintenance'?'warn':'err'}>{r.status}</Pill> },
              { key:'simulator', header:'Type', render: r=> r.simulator?'Sim':'Real' },
              { key:'job_count', header:'Jobs' },
              { key:'total_shots', header:'Shots' },
              { key:'pending_jobs', header:'Pending' },
              { key:'estimated_wait_time', header:'Est Wait', render: r=> <span className="tabular-nums font-medium text-amber-400">{r.estimated_wait_time}s</span> },
            ]} />
          </div>
        </div>
      </section>
    </main>
    <footer className="px-6 py-4 text-[10px] text-muted-foreground border-t border-border">Demo Mode • Synthetic data - no IBM API calls</footer>
  </div>
}
