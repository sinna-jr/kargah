import requests

url = "https://api.wallex.ir/v1/markets"
response = requests.get(url)
data = response.json()
markets = data['result']['symbols']
result = {}

FEE_PERCENT = 0.001 

for symbol, info in markets.items():
    stats = info.get('stats', {})
    try:
        bid = float(stats.get('bidPrice', 0))
        ask = float(stats.get('askPrice', 0))
        vol_tmn = float(stats.get('24h_tmnVolume', 0)) 
        
        result[symbol] = {'bid': bid, 'ask': ask, 'vol_tmn': vol_tmn}
    except (ValueError, TypeError):
        continue

usdt_tmn = result.get('USDTTMN', {'bid': 1, 'ask': 1})
usdt_avg_bid = usdt_tmn['bid'] or 1
usdt_avg_ask = usdt_tmn['ask'] or 1

print("=" * 80)
for key, val in result.items():
    if key.endswith('TMN') and key != 'USDTTMN':
        symbol = key[:-3]
        other_key = symbol + 'USDT'
        
        if other_key in result:
            tmn_bid, tmn_ask = val['bid'], val['ask']
            usdt_bid, usdt_ask = result[other_key]['bid'], result[other_key]['ask']
            
            volume_in_usd = val['vol_tmn'] / usdt_avg_bid
            
            usdt_bid_tmn = usdt_bid * usdt_avg_bid
            usdt_ask_tmn = usdt_ask * usdt_avg_ask
            
            delta_tmn_first  = ((usdt_bid_tmn / tmn_ask - 1) - (2 * FEE_PERCENT)) * 100
            delta_usdt_first = ((tmn_bid / usdt_ask_tmn - 1) - (2 * FEE_PERCENT)) * 100

            if (delta_usdt_first > -0.1 or delta_tmn_first > -0.1):
                print(f"{symbol} (Volume: {volume_in_usd:,.2f} USDT):")
                print(f"  TMN Ask = {tmn_ask:,.3f} IRR || TMN bid = {tmn_bid:,.3f} IRR")
                print(f"  USDT Ask × Tether = {usdt_ask_tmn:,.3f} IRR ||  USDT bid × Tether = {usdt_bid_tmn:,.3f} IRR")
                print(f"  delta_tmn_first =  {delta_tmn_first:.2f}  ||  delta_usdt_first = {delta_usdt_first:.2f} ")
                print("=" * 80)