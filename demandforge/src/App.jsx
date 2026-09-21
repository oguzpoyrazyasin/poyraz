import React, { useMemo, useState } from 'react';
import { agents, compileIntent, dashboard, supplierScore, suppliers } from './demoEngine.js';

const money=n=>new Intl.NumberFormat('en-DE',{style:'currency',currency:'EUR'}).format(n);
function Badge({children,tone='neutral'}){return <span className={'badge '+tone}>{children}</span>;}

export default function App(){
  const [query,setQuery]=useState('I want a minimalist personalized rechargeable table lamp under €50, 50 pcs, delivered to Germany within 10 days.');
  const [result,setResult]=useState(()=>compileIntent(query));
  const [loading,setLoading]=useState(false);
  function compile(){setLoading(true);setTimeout(()=>{setResult(compileIntent(query));setLoading(false);},250);}
  const metrics=useMemo(()=>[
    ['Active sourcing',dashboard.activeSourcingJobs],
    ['Supplier response',Math.round(dashboard.supplierResponseRate*100)+'%'],
    ['RFQ→Offer',dashboard.medianRfqToOfferHours+'h'],
    ['Expected CM',Math.round(dashboard.expectedContributionMargin*100)+'%'],
    ['Orders at risk',dashboard.ordersAtRisk],
    ['Approvals',dashboard.approvalBacklog]
  ],[]);
  return <div className="shell">
    <aside className="sidebar">
      <div className="brand">DemandForge<span>AI</span></div>
      <div className="tagline">Autonomous Demand-to-Factory Commerce OS</div>
      <nav>
        <a className="active">Commerce Studio</a><a>Supplier Intelligence</a><a>RFQ Control</a><a>Orders</a><a>Policy & Approvals</a><a>Agent Control</a><a>Audit</a>
      </nav>
      <div className="safe">LIVE DEMO<br/><b>No real purchase, payment or supplier commitment.</b></div>
    </aside>
    <main>
      <header>
        <div><p className="eyebrow">INTENT → SPEC → FACTORY → QUOTE → COMMERCE</p><h1>What are you trying to create?</h1><p className="muted">Describe the outcome. DemandForge compiles it into a Product Genome and commercial scenarios.</p></div>
        <Badge tone="green">GITHUB PAGES DEMO</Badge>
      </header>
      <section className="composer card">
        <textarea value={query} onChange={e=>setQuery(e.target.value)} />
        <div className="composerFooter"><span className="muted">Natural language • market • budget • SLA • quantity • customization</span><button onClick={compile} disabled={loading}>{loading?'Compiling…':'Compile Product Genome'}</button></div>
      </section>
      <section className="metrics">{metrics.map(([k,v])=><div className="metric card" key={k}><span>{k}</span><strong>{v}</strong></div>)}</section>
      <section className="grid2">
        <div className="card"><div className="sectionTitle"><h2>Product Genome</h2><Badge tone="blue">source of truth</Badge></div><pre>{JSON.stringify(result.genome,null,2)}</pre></div>
        <div className="card"><div className="sectionTitle"><h2>Optimization controls</h2><Badge>live constraints</Badge></div>{['Price ↔ Quality','Delivery ↔ Cost','Custom ↔ Standard','Low MOQ ↔ Scale'].map((x,i)=><label className="slider" key={x}>{x}<input type="range" defaultValue={[48,62,72,35][i]} /></label>)}<p className="note">Demo mode keeps all calculations local in your browser. Production mode will recalculate live supplier, logistics and compliance data.</p></div>
      </section>
      <section>
        <div className="sectionTitle"><h2>Pareto commercial options</h2><span className="muted">Trade-offs stay explicit.</span></div>
        <div className="options">{result.options.map(o=><article className={'option card '+o.tier.toLowerCase()} key={o.tier}>
          <div className="sectionTitle"><h3>{o.tier}</h3><Badge tone={o.complianceStatus==='PASS'?'green':'amber'}>{o.complianceStatus}</Badge></div>
          <div className="price">{money(o.retail)}</div>
          <div className="rows">
            <div><span>Landed cost</span><b>{money(o.landed)}</b></div><div><span>Expected margin</span><b>{o.expectedMargin}%</b></div><div><span>Lead time</span><b>{o.leadDays} days</b></div><div><span>Supplier score</span><b>{o.supplierScore}/100</b></div><div><span>Delivery confidence</span><b>{Math.round(o.deliveryConfidence*100)}%</b></div><div><span>Quality confidence</span><b>{Math.round(o.qualityConfidence*100)}%</b></div>
          </div><div className="supplierName">{o.supplier.name}</div><button className="secondary">Inspect scenario</button>
        </article>)}</div>
      </section>
      <section className="grid2 lower">
        <div className="card"><div className="sectionTitle"><h2>Factory Intelligence</h2><Badge>{suppliers.length} candidates</Badge></div>{suppliers.map(s=><div className="supplier" key={s.id}><div><b>{s.name}</b><small>{s.location} • MOQ {s.moq}</small></div><div className="right"><b>{supplierScore(s)}</b><Badge tone={s.riskFlags.length?'amber':'green'}>{s.riskFlags.length?'REVIEW':'LOW RISK'}</Badge></div></div>)}</div>
        <div className="card"><div className="sectionTitle"><h2>Agent Control Plane</h2><Badge tone="blue">{agents.length} agents</Badge></div><div className="agentGrid">{agents.slice(0,10).map(a=><div className="agent" key={a.name}><b>{a.name}</b><span>{a.autonomy} • {a.status}</span></div>)}</div></div>
      </section>
    </main>
  </div>;
}