export const suppliers = [
  { id:'SZ-LUMEN-01', name:'Shenzhen LumenWorks', location:'Shenzhen, China', verified:true, moq:50, responseHours:4, otif:0.962, defectRate:0.011, compliance:['RoHS','CE technical file'], priceCompetitiveness:0.90, riskFlags:[] },
  { id:'DG-NOVA-07', name:'Dongguan Nova Lighting', location:'Dongguan, China', verified:true, moq:100, responseHours:8, otif:0.941, defectRate:0.016, compliance:['RoHS','EMC test report'], priceCompetitiveness:0.95, riskFlags:[] },
  { id:'GZ-VELA-12', name:'Guangzhou Vela Home', location:'Guangzhou, China', verified:false, moq:30, responseHours:11, otif:0.887, defectRate:0.031, compliance:['RoHS'], priceCompetitiveness:0.98, riskFlags:['MISSING_EU_TECHNICAL_FILE'] }
];

export const agents = [
  ['Intent Agent','A4'],['Product Architect','A3'],['Discovery Agent','A4'],['Factory Agent','A3'],
  ['RFQ Agent','A3'],['Quote Parser','A4'],['Negotiation Agent','A2'],['Compliance Agent','A2'],
  ['Logistics Agent','A3'],['Pricing Agent','A4'],['Creative Agent','A3'],['Order Agent','A1'],
  ['QC Agent','A2'],['Support Agent','A3'],['Risk Agent','A4'],['Optimization Agent','A3']
].map(([name,autonomy])=>({name,autonomy,status:'READY'}));

export const dashboard = {
  activeSourcingJobs:4,
  supplierResponseRate:0.78,
  medianRfqToOfferHours:5.6,
  expectedContributionMargin:0.34,
  ordersAtRisk:1,
  approvalBacklog:2
};

export function supplierScore(s){
  const quality=1-Math.min(s.defectRate*8,1);
  const delivery=s.otif;
  const compliance=s.compliance.length>=2?1:0.55;
  const responsiveness=Math.max(0.4,1-s.responseHours/48);
  const verification=s.verified?1:0.45;
  return Math.round((0.20*quality+0.20*delivery+0.20*compliance+0.10*responsiveness+0.15*verification+0.15*s.priceCompetitiveness)*100);
}

export function compileIntent(text=''){
  const lower=text.toLowerCase();
  const targetRetailPrice=Number((text.match(/(?:€|eur\s?)(\d+)/i)||[])[1]||50);
  const genome={
    category:lower.includes('lamp')||lower.includes('lamba')?'lighting.table_lamp':'custom_product',
    market:lower.includes('germany')||lower.includes('almanya')?'DE':'EU',
    targetRetailPrice,
    quantity:Number((text.match(/(\d+)\s*(?:pcs|adet)/i)||[])[1]||50),
    maxMoq:100,
    targetGrossMargin:0.40,
    maxDeliveryDays:Number((text.match(/(\d+)\s*(?:day|gün)/i)||[])[1]||10),
    style:lower.includes('minimal')?['minimalist']:['modern'],
    features:{rechargeable:/recharge|şarj|usb/i.test(text),personalized:/personal|kişisel|logo|isim/i.test(text)},
    complianceMarket:'EU'
  };
  const base=30.15;
  const options=[
    {tier:'Budget',supplier:suppliers[2],landed:base-3.1,retail:targetRetailPrice-5,leadDays:12,deliveryConfidence:0.72,qualityConfidence:0.74},
    {tier:'Balanced',supplier:suppliers[0],landed:base,retail:targetRetailPrice,leadDays:9,deliveryConfidence:0.90,qualityConfidence:0.92},
    {tier:'Premium',supplier:suppliers[1],landed:base+5,retail:targetRetailPrice+9,leadDays:7,deliveryConfidence:0.95,qualityConfidence:0.95}
  ].map(o=>({...o,supplierScore:supplierScore(o.supplier),expectedMargin:Number((((o.retail-o.landed)/o.retail)*100).toFixed(1)),complianceStatus:o.supplier.riskFlags.length?'REVIEW':'PASS'}));
  return {genome,options};
}