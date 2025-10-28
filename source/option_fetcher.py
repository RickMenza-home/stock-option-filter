import yfinance as yf
from typing import List, Dict

def fetch_options(symbol, strike_price, price_range, expiry_date, option_type="put") -> List[Dict]:  
    try:
        target_strike = float(strike_price)
        range_val = float(price_range)
        expiration_filter = expiry_date   # YYYY-MM-DD or empty
    except Exception as exc:
        raise ValueError("Please enter valid numeric values") from exc

    try:
        ticker = yf.Ticker(symbol)
        exp_dates = ticker.options
        if not exp_dates:
            raise RuntimeError("No options data found for symbol: " + symbol)
    except Exception:
        # Let callers handle network / yfinance errors
        raise

    results: List[Dict] = []
    for exp in exp_dates:
        if expiry_date and exp != expiry_date:
            continue
        opt_chain = ticker.option_chain(exp)
        options_df = opt_chain.puts if option_type == "put" else opt_chain.calls

        filtered = options_df[
            (options_df['strike'] >= target_strike - range_val) &
            (options_df['strike'] <= target_strike + range_val)
        ]

        for _, row in filtered.iterrows():
            strike = row.get('strike', 0)
            last_price = row.get('lastPrice') or 0
            bid = row.get('bid') or 0
            ask = row.get('ask') or 0
            mid_price = (bid + ask) / 2 if (bid and ask) else last_price
            volume = row.get('volume') or 0
            premium = mid_price * 100

            if option_type == "put":
                margin = strike * 100
            else:
                try:
                    current_price = ticker.history(period="1d")["Close"].iloc[-1]
                except Exception:
                    current_price = strike
                margin = current_price * 100

            profit_percent = (premium / margin) * 100 if margin else 0

            results.append({
                "contractSymbol": row.get('contractSymbol'),
                "strike": strike,
                "expiration": exp,
                "lastPrice": last_price,
                "bid": bid,
                "ask": ask,
                "midPrice": mid_price,
                "premium": premium,
                "volume": volume,
                "margin": margin,
                "profitPercent": profit_percent
            })

    return results