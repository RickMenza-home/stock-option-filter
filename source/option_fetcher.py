import yfinance as yf
from tkinter import messagebox

def fetch_options(symbol, target_strike, range_val, expiration_filter, option_type="put"):
    symbol = symbol.upper()
    
    try:
        ticker = yf.Ticker(symbol)
        exp_dates = ticker.options
        if not exp_dates:
            messagebox.showerror("Error", "No options data found")
            return []
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching data: {e}")
        return []

    options_data = []

    for exp in exp_dates:
        if expiration_filter and exp != expiration_filter:
            continue
        opt_chain = ticker.option_chain(exp)
        options_df = opt_chain.puts if option_type == "put" else opt_chain.calls

        filtered = options_df[
            (options_df['strike'] >= target_strike - range_val) &
            (options_df['strike'] <= target_strike + range_val)
        ]

        for _, row_data in filtered.iterrows():
            strike = row_data['strike']
            last_price = row_data['lastPrice'] or 0
            bid = row_data['bid'] or 0
            ask = row_data['ask'] or 0
            mid_price = (bid + ask) / 2 if (bid and ask) else last_price
            volume = row_data['volume'] or 0
            premium = mid_price * 100

            if option_type == "put":
                margin = strike * 100
            else:
                try:
                    current_price = ticker.history(period="1d")["Close"].iloc[-1]
                except:
                    current_price = strike
                margin = current_price * 100

            profit_percent = (premium / margin) * 100 if margin else 0

            options_data.append({
                'contractSymbol': row_data['contractSymbol'],
                'strike': strike,
                'expiration': exp,
                'lastPrice': last_price,
                'bid': bid,
                'ask': ask,
                'midPrice': mid_price,
                'premium': premium,
                'volume': volume,
                'margin': margin,
                'profitPercent': profit_percent
            })

    return options_data

def fetch_put_options(symbol, target_strike, range_val, expiration_filter):
    return fetch_options(symbol, target_strike, range_val, expiration_filter, option_type="put")

def fetch_call_options(symbol, target_strike, range_val, expiration_filter):
    return fetch_options(symbol, target_strike, range_val, expiration_filter, option_type="call")