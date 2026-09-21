from scanner import Cfg, score_pair
def run():
    cfg=Cfg()
    p={"chainId":"solana","dexId":"raydium","url":"https://dexscreener.com/solana/example","baseToken":{"address":"ABC","name":"Example","symbol":"EX"},"priceUsd":"0.1","liquidity":{"usd":250000},"volume":{"h24":300000},"txns":{"h24":{"buys":1200,"sells":1000}},"priceChange":{"h1":4,"h24":12},"fdv":5000000,"marketCap":4000000,"pairCreatedAt":1700000000000,"boosts":{"active":0}}
    x=score_pair(p,False,cfg); assert x and x.priority>20
    p["liquidity"]={"usd":1000}; p["volume"]={"h24":300}; assert score_pair(p,False,cfg).status=="REJECT"
    print("token radar tests passed")
if __name__=="__main__":run()
