export const suppliers = [
  {
    id: 'SZ-LUMEN-01',
    name: 'Shenzhen LumenWorks',
    location: 'Shenzhen, China',
    verified: true,
    capabilities: ['LED assembly','USB-C','laser engraving','custom packaging'],
    moq: 50,
    responseHours: 4,
    otif: 0.962,
    defectRate: 0.011,
    compliance: ['RoHS','CE technical file'],
    priceCompetitiveness: 0.90,
    riskFlags: []
  },
  {
    id: 'DG-NOVA-07',
    name: 'Dongguan Nova Lighting',
    location: 'Dongguan, China',
    verified: true,
    capabilities: ['LED assembly','aluminium','custom color','OEM packaging'],
    moq: 100,
    responseHours: 8,
    otif: 0.941,
    defectRate: 0.016,
    compliance: ['RoHS','EMC test report'],
    priceCompetitiveness: 0.95,
    riskFlags: []
  },
  {
    id: 'GZ-VELA-12',
    name: 'Guangzhou Vela Home',
    location: 'Guangzhou, China',
    verified: false,
    capabilities: ['LED assembly','plastic molding','printing'],
    moq: 30,
    responseHours: 11,
    otif: 0.887,
    defectRate: 0.031,
    compliance: ['RoHS'],
    priceCompetitiveness: 0.98,
    riskFlags: ['MISSING_EU_TECHNICAL_FILE']
  }
];

export const agents = [
  ['Intent Agent','A4',['compile_intent']],
  ['Product Architect','A3',['build_spec']],
  ['Discovery Agent','A4',['search_candidates']],
  ['Factory Agent','A3',['match_factory']],
  ['RFQ Agent','A3',['draft_rfq','send_mock_rfq']],
  ['Quote Parser','A4',['normalize_quote']],
  ['Negotiation Agent','A2',['draft_counter_offer']],
  ['Compliance Agent','A2',['compliance_gate']],
  ['Logistics Agent','A3',['estimate_route']],
  ['Pricing Agent','A4',['landed_cost','margin_simulation']],
  ['Creative Agent','A3',['draft_creative']],
  ['Order Agent','A1',['prepare_po']],
  ['QC Agent','A2',['assess_qc']],
  ['Support Agent','A3',['draft_support']],
  ['Risk Agent','A4',['score_supplier']],
  ['Optimization Agent','A3',['scenario_recommendations']]
].map(([name, autonomy, actions]) => ({name, autonomy, actions, status:'READY'}));

export function compileIntent(text='') {
  const lower = text.toLowerCase();
  return {
    category: lower.includes('lamp') || lower.includes('lamba') ? 'lighting.table_lamp' : 'custom_product',
    market: lower.includes('germany') || lower.includes('almanya') ? 'DE' : 'EU',
    targetRetailPrice: Number((text.match(/(?:€|eur\\s?)(\\d+)/i)||[])[1] || 50),
    quantity: Number((text.match(/(\\d+)\\s*(?:pcs|adet)/i)||[])[1] || 50),
    maxMoq: 100,
    targetGrossMargin: 0.40,
    maxDeliveryDays: Number((text.match(/(\\d+)\\s*(?:day|gün)/i)||[])[1] || 10),
    style: lower.includes('minimal') ? ['minimalist'] : ['modern'],
    features: {
      rechargeable: /recharge|şarj|usb/i.test(text),
      personalized: /personal|kişisel|logo|isim/i.test(text)
    },
    complianceMarket: 'EU'
  };
}

export function supplierScore(s) {
  const quality = 1 - Math.min(s.defectRate * 8, 1);
  const delivery = s.otif;
  const compliance = s.compliance.length >= 2 ? 1 : 0.55;
  const responsiveness = Math.max(0.4, 1 - s.responseHours / 48);
  const verification = s.verified ? 1 : 0.45;
  const price = s.priceCompetitiveness;
  const hardGate = s.riskFlags.some(x => ['SANCTIONS','IDENTITY_MISMATCH','BANK_MISMATCH'].includes(x)) ? 0 : 1;
  const score = hardGate * (0.20*quality + 0.20*delivery + 0.20*compliance + 0.10*responsiveness + 0.15*verification + 0.15*price);
  return Math.round(score*100);
}

export function landedCost(input={}) {
  const c = {
    product: Number(input.product ?? 14.9),
    customization: Number(input.customization ?? 0.7),
    packaging: Number(input.packaging ?? 0.6),
    toolingAmortization: Number(input.toolingAmortization ?? 0.3),
    qc: Number(input.qc ?? 0.4),
    chinaFreight: Number(input.chinaFreight ?? 0.6),
    exportCharges: Number(input.exportCharges ?? 0.25),
    internationalFreight: Number(input.internationalFreight ?? 4.2),
    insurance: Number(input.insurance ?? 0.15),
    duty: Number(input.duty ?? 1.0),
    vatTax: Number(input.vatTax ?? 3.1),
    handling: Number(input.handling ?? 0.7),
    payment: Number(input.payment ?? 0.45),
    fx: Number(input.fx ?? 0.35),
    fulfillment: Number(input.fulfillment ?? 1.3),
    returnsReserve: Number(input.returnsReserve ?? 1.1)
  };
  const expected = Object.values(c).reduce((a,b)=>a+b,0);
  return {
    components: c,
    expected: Number(expected.toFixed(2)),
    p50: Number((expected*0.98).toFixed(2)),
    p90: Number((expected*1.13).toFixed(2))
  };
}

export function commercialOptions(genome) {
  const base = landedCost().expected;
  return [
    {tier:'Budget', supplier:suppliers[2], landed:base-3.1, retail:genome.targetRetailPrice-5, leadDays:12, deliveryConfidence:0.72, qualityConfidence:0.74},
    {tier:'Balanced', supplier:suppliers[0], landed:base, retail:genome.targetRetailPrice, leadDays:9, deliveryConfidence:0.90, qualityConfidence:0.92},
    {tier:'Premium', supplier:suppliers[1], landed:base+5.0, retail:genome.targetRetailPrice+9, leadDays:7, deliveryConfidence:0.95, qualityConfidence:0.95}
  ].map(o => ({
    ...o,
    supplierScore: supplierScore(o.supplier),
    expectedMargin: Number((((o.retail-o.landed)/o.retail)*100).toFixed(1)),
    complianceStatus: o.supplier.riskFlags.length ? 'REVIEW' : 'PASS'
  }));
}