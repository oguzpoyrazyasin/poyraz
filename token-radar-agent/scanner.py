from __future__ import annotations

import json, math, os, sys, time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

DEX_BASE="https://api.dexscreener.com"
PAPRIKA_BASE="https://api.coinpaprika.com/v1"
GH_API="https://api.github.com"
REPORT_TITLE="[Token Radar] Latest scan"
UA="poyraz-token-radar/0.1"

@dataclass
class Cfg:
    max_dex:int=40
    max_market:int=25
    min_liq:float=25000.0
    min_vol:float=10000.0
    min_age_h:float=6.0
    max_fdv_liq:float=500.0
    timeout:int=25
    retries:int=3

@dataclass
class Dex:
    chain:str; address:str; symbol:str; name:str; url:str; dex:str
    price:float|None; liquidity:float; volume24h:float; buys:int; sells:int
    age_h:float|None; fdv:float|None; market_cap:float|None; boosts:int
    signal:float; risk:float; priority:float; status:str
    reasons:list[str]; risks:list[str]

def now(): return datetime.now(timezone.utc)
def num(v,d=0.0):
    try: return float(v) if v not in (None,"") else d
    except (TypeError,ValueError): return d
def integer(v,d=0):
    try: return int(v)
    except (TypeError,ValueError): return d

def get_json(url,cfg):
    last=None
    for i in range(cfg.retries):
        try:
            req=Request(url,headers={"Accept":"application/json","User-Agent":UA})
            with urlopen(req,timeout=cfg.timeout) as r: return json.loads(r.read().decode())
        except HTTPError as e:
            last=e
            if e.code not in {429,500,502,503,504}: break
        except (URLError,TimeoutError,json.JSONDecodeError) as e: last=e
        time.sleep(1+i)
    raise RuntimeError(f"request failed {url}: {last}")

def gh(method,path,token,payload=None):
    h={"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","Authorization":f"Bearer {token}","User-Agent":UA}
    data=None if payload is None else json.dumps(payload).encode()
    if data is not None: h["Content-Type"]="application/json"
    with urlopen(Request(GH_API+path,data=data,headers=h,method=method),timeout=30) as r:
        raw=r.read().decode()
        return json.loads(raw) if raw else None

def pair_age(ms):
    x=num(ms)
    if x<=0: return None
    return max(0.0,(now()-datetime.fromtimestamp(x/1000,tz=timezone.utc)).total_seconds()/3600)

def logpts(v,floor,cap):
    if v<=0:return 0.0
    return min(cap,cap*math.log10(max(1.0,v/max(floor,1e-9))+1)/3)

def score_pair(p,boosted,cfg):
    b=p.get("baseToken") or {}
    chain,address=str(p.get("chainId") or ""),str(b.get("address") or "")
    if not chain or not address:return None
    liq=num((p.get("liquidity") or {}).get("usd")); vol=num((p.get("volume") or {}).get("h24"))
    t=(p.get("txns") or {}).get("h24") or {}; buys,sells=integer(t.get("buys")),integer(t.get("sells"))
    age=pair_age(p.get("pairCreatedAt")); ch=p.get("priceChange") or {}
    p1,p24=abs(num(ch.get("h1"))),abs(num(ch.get("h24")))
    fdv=num(p.get("fdv")) or None; mcap=num(p.get("marketCap")) or None; boosts=integer((p.get("boosts") or {}).get("active"))
    signal=logpts(liq,cfg.min_liq,28)+logpts(vol,cfg.min_vol,24)+min(16,math.log10(max(1,buys+sells)+1)*5)
    risk=0.0; reasons=[]; risks=[]
    if liq>=cfg.min_liq: reasons.append(f"liquidity USD {liq:,.0f}")
    else: risk+=28; risks.append(f"thin liquidity USD {liq:,.0f}")
    if vol>=cfg.min_vol: reasons.append(f"24h volume USD {vol:,.0f}")
    else: risk+=15; risks.append(f"low 24h volume USD {vol:,.0f}")
    if age is None: risk+=8; risks.append("pair age unknown")
    elif age<cfg.min_age_h: risk+=28; risks.append(f"very new pair {age:.1f}h")
    elif age<24: risk+=12
    else: signal+=min(12,math.log10(age+1)*4)
    if p1>=80:risk+=18; risks.append(f"1h move {p1:.0f}%")
    elif p1>=30:risk+=7
    if p24>=180:risk+=14; risks.append(f"24h move {p24:.0f}%")
    elif p24>=80:risk+=6
    if fdv and liq>0:
        ratio=fdv/liq
        if ratio>cfg.max_fdv_liq:risk+=22; risks.append(f"FDV/liquidity {ratio:.0f}x")
        elif ratio>100:risk+=8
    if buys+sells>=20 and abs(buys-sells)/max(1,buys+sells)<.75: signal+=8; reasons.append(f"24h tx {buys+sells:,}")
    if boosted or boosts:risk+=4; reasons.append("paid/boosted visibility")
    signal=min(100,max(0,signal)); risk=min(100,max(0,risk))
    priority=round(signal*(1-.72*risk/100),1)
    status="REJECT" if liq<2500 or vol<1000 or risk>=75 else ("REVIEW" if risk>=45 or priority<30 else "OBSERVE")
    return Dex(chain,address,str(b.get("symbol") or "?"),str(b.get("name") or ""),str(p.get("url") or ""),str(p.get("dexId") or ""),num(p.get("priceUsd")) or None,round(liq,2),round(vol,2),buys,sells,round(age,2) if age is not None else None,fdv,mcap,boosts,round(signal,1),round(risk,1),priority,status,reasons[:5],risks[:5])

def seeds(cfg):
    out={}
    for path,boosted in [("/token-profiles/latest/v1",False),("/token-boosts/latest/v1",True),("/token-boosts/top/v1",True)]:
        try: rows=get_json(DEX_BASE+path,cfg)
        except Exception as e: print("WARN",path,e,file=sys.stderr); continue
        for r in rows if isinstance(rows,list) else []:
            c,a=str(r.get("chainId") or ""),str(r.get("tokenAddress") or "")
            if c and a: out[(c,a)]=out.get((c,a),False) or boosted
    return [(c,a,b) for (c,a),b in out.items()]

def scan_dex(cfg):
    out=[]
    for chain,address,boosted in seeds(cfg)[:cfg.max_dex*3]:
        try:
            rows=get_json(f"{DEX_BASE}/token-pairs/v1/{quote(chain,safe='')}/{quote(address,safe='')}",cfg)
            if not isinstance(rows,list) or not rows: continue
            item=score_pair(max(rows,key=lambda p:num((p.get("liquidity") or {}).get("usd"))),boosted,cfg)
            if item and item.status!="REJECT":out.append(item)
        except Exception as e: print("WARN enrich",chain,address,e,file=sys.stderr)
        if len(out)>=cfg.max_dex:break
        time.sleep(.05)
    out.sort(key=lambda x:(x.status=="OBSERVE",x.priority,x.liquidity),reverse=True)
    return out

def scan_market(cfg):
    try:data=get_json(PAPRIKA_BASE+"/tickers?quotes=USD",cfg)
    except Exception as e: print("WARN CoinPaprika",e,file=sys.stderr);return []
    out=[]
    for r in data if isinstance(data,list) else []:
        u=(r.get("quotes") or {}).get("USD") or {}; cap=num(u.get("market_cap")); vol=num(u.get("volume_24h"))
        if cap<=0 or vol<=0:continue
        change=num(u.get("percent_change_24h")); activity=min(100,35*math.log10(1+vol/100000)+min(35,(vol/cap)*100))
        if abs(change)>80:activity*=.65
        out.append({"id":r.get("id"),"symbol":r.get("symbol"),"name":r.get("name"),"rank":r.get("rank"),"price":u.get("price"),"market_cap":round(cap,2),"volume24h":round(vol,2),"change24h":round(change,2),"activity":round(activity,1)})
    out.sort(key=lambda x:(x["activity"],x["volume24h"]),reverse=True)
    return out[:cfg.max_market]

def markdown(dex,market):
    lines=[f"# Token Radar — {now().strftime('%Y-%m-%d %H:%M UTC')}","","Read-only discovery. Not a buy/sell recommendation. No custody, private-key search, third-party claims or exploit automation.","","## New / emerging DEX tokens","","|Priority|Risk|Status|Token|Chain|Liquidity|24h volume|Age|","|---:|---:|---|---|---|---:|---:|---:|"]
    for x in dex[:20]:
        token=f"[{x.symbol}]({x.url})" if x.url else x.symbol; age=f"{x.age_h:.1f}h" if x.age_h is not None else "?"
        lines.append(f"|{x.priority:.1f}|{x.risk:.1f}|{x.status}|{token}|{x.chain}|USD {x.liquidity:,.0f}|USD {x.volume24h:,.0f}|{age}|")
    lines+=["","## Broad market activity","","|Activity|Asset|Rank|Market cap|24h volume|24h change|","|---:|---|---:|---:|---:|---:|"]
    for x in market[:20]:lines.append(f"|{x['activity']:.1f}|{x['symbol']} — {x['name']}|{x['rank'] or '—'}|USD {x['market_cap']:,.0f}|USD {x['volume24h']:,.0f}|{x['change24h']:+.1f}%|")
    lines+=["","## Guardrails","","- OBSERVE is an investigation state, not an investment instruction.","- REVIEW requires manual verification.","- Paid boosts never increase trust.","- No seed/private-key discovery, abandoned-wallet sweeping, unauthorized claims, sybil farming, exploit automation, front-running, wash trading, custody or trading is implemented."]
    return "\n".join(lines)+"\n"

def html(payload):
    cards=[]
    for x in payload["dex"]:
        link=f'<a href="{x["url"]}">DEX pair</a>' if x.get("url") else ""
        cards.append(f'<div class="card"><b>{x["symbol"]}</b> <span>{x["chain"]}</span><h3>{x["priority"]} priority</h3><p>{x["risk"]} risk · USD {x["liquidity"]:,.0f} liquidity · USD {x["volume24h"]:,.0f} volume</p>{link}</div>')
    return '<!doctype html><meta charset="utf-8"><title>Token Radar</title><style>body{font-family:system-ui;background:#0b0f14;color:#e7edf5;max-width:1180px;margin:auto;padding:28px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}.card{background:#121923;border:1px solid #263244;border-radius:16px;padding:16px}a{color:#7dd3fc}</style><h1>Token Radar</h1><p>Read-only discovery</p><div class="grid">'+"".join(cards)+"</div>"

def publish(token,repo,body):
    issues=gh("GET",f"/repos/{repo}/issues?state=open&per_page=100",token)
    cur=next((i for i in issues if i.get("title")==REPORT_TITLE and "pull_request" not in i),None)
    payload={"title":REPORT_TITLE,"body":body[:60000]}
    if cur:gh("PATCH",f"/repos/{repo}/issues/{cur['number']}",token,payload)
    else:gh("POST",f"/repos/{repo}/issues",token,payload)

def main():
    cfg=Cfg(); dex=scan_dex(cfg); market=scan_market(cfg)
    out=Path(__file__).resolve().parent/"output"; out.mkdir(exist_ok=True)
    payload={"generated_at":now().isoformat(),"version":"0.1","dex":[asdict(x) for x in dex],"market":market}
    (out/"latest.json").write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding="utf-8")
    md=markdown(dex,market); (out/"LATEST.md").write_text(md,encoding="utf-8"); (out/"dashboard.html").write_text(html(payload),encoding="utf-8")
    token,repo=os.getenv("GITHUB_TOKEN"),os.getenv("GITHUB_REPOSITORY")
    if token and repo and os.getenv("PUBLISH_ISSUE","true").lower()=="true":publish(token,repo,md)
    print(f"dex={len(dex)} market={len(market)}")
    return 0

if __name__=="__main__":raise SystemExit(main())
