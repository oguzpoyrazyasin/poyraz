import express from 'express';
import cors from 'cors';
import { v4 as uuid } from 'uuid';
import { z } from 'zod';
import { suppliers, agents, compileIntent, supplierScore, landedCost, commercialOptions } from './domain.js';

const app = express();
app.use(cors());
app.use(express.json());

const audit = [];
const rfqs = [];

function record(event, actor='system', evidence=[], confidence=1) {
  const row = {id: uuid(), event, actor, evidence, confidence, timestamp:new Date().toISOString()};
  audit.unshift(row);
  return row;
}

app.get('/api/health', (_,res)=>res.json({ok:true, service:'demandforge-api'}));

app.get('/api/dashboard', (_,res)=>res.json({
  activeSourcingJobs: 4,
  supplierResponseRate: 0.78,
  medianRfqToOfferHours: 5.6,
  expectedContributionMargin: 0.34,
  ordersAtRisk: 1,
  approvalBacklog: 2
}));

app.get('/api/suppliers', (_,res)=>res.json(suppliers.map(s=>({...s, score:supplierScore(s)}))));
app.get('/api/agents', (_,res)=>res.json(agents));
app.get('/api/audit', (_,res)=>res.json(audit));

app.post('/api/compile-intent', (req,res)=>{
  const body = z.object({text:z.string().min(3)}).parse(req.body);
  const genome = compileIntent(body.text);
  record('INTENT_COMPILED','Intent Agent',[body.text],0.96);
  res.json({genome, options:commercialOptions(genome)});
});

app.post('/api/landed-cost', (req,res)=>{
  const result = landedCost(req.body || {});
  record('LANDED_COST_CALCULATED','Pricing Agent',[],0.94);
  res.json(result);
});

app.post('/api/rfqs', (req,res)=>{
  const body = z.object({
    supplierId:z.string(),
    product:z.string(),
    quantity:z.number().int().positive(),
    destination:z.string().min(2)
  }).parse(req.body);
  const rfq = {
    id:'RFQ-' + Date.now(),
    ...body,
    status:'SENT_MOCK',
    binding:false,
    createdAt:new Date().toISOString()
  };
  rfqs.unshift(rfq);
  record('RFQ_SENT_MOCK','RFQ Agent',[rfq.id],0.99);
  res.status(201).json(rfq);
});

app.get('/api/rfqs', (_,res)=>res.json(rfqs));

app.post('/api/approvals/check', (req,res)=>{
  const {action, amount=0} = req.body || {};
  const limits = {sample_order:100, ad_test:50, refund:40, purchase_order:0, supplier_change:0};
  const limit = limits[action] ?? 0;
  res.json({
    action,
    amount,
    autoApproved: amount <= limit && limit > 0,
    requiresHumanApproval: !(amount <= limit && limit > 0),
    threshold: limit
  });
});

app.use((err, req, res, next)=>{
  console.error(err);
  res.status(400).json({error:err?.message || 'Bad request'});
});

const port = process.env.PORT || 8787;
app.listen(port, ()=>console.log('DemandForge API listening on :' + port));