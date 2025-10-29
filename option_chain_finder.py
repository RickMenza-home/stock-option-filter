import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
from datetime import datetime
import numpy as np
from scipy.interpolate import interp1d

# --- FUNCTIONS ---

def fetch_put_options():
    symbol = symbol_entry.get().upper()

    # Validate inputs
    try:
        target_strike = float(strike_entry.get())
        range_val = float(range_entry.get())
        expiration_filter = expiration_entry.get()  # YYYY-MM-DD or empty
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values")
        return

    try:
        ticker = yf.Ticker(symbol)
        exp_dates = ticker.options
        if not exp_dates:
            messagebox.showerror("Error", "No options data found")
            return
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching data: {e}")
        return

    # Clear previous table
    for row in tree.get_children():
        tree.delete(row)

    for exp in exp_dates:
        if expiration_filter and exp != expiration_filter:
            continue
        opt_chain = ticker.option_chain(exp)
        puts = opt_chain.puts

        # Filter by strike range
        puts_filtered = puts[(puts['strike'] >= target_strike - range_val) &
                             (puts['strike'] <= target_strike + range_val)]

        for _, row_data in puts_filtered.iterrows():
            strike = row_data['strike']
            last_price = row_data['lastPrice'] or 0
            bid = row_data['bid'] or 0
            ask = row_data['ask'] or 0
            mid_price = (bid + ask) / 2 if (bid and ask) else last_price
            volume = row_data['volume'] or 0
            premium = mid_price * 100
            margin = strike * 100
            profit_percent = (premium / margin) * 100 if margin else 0

            tree.insert("", "end", values=(
                row_data['contractSymbol'],
                f"${strike:,.2f}",
                exp,
                f"${last_price:,.2f}",
                f"${bid:,.2f}",
                f"${ask:,.2f}",
                f"${mid_price:,.2f}",
                f"${premium:,.2f}",
                volume,
                f"${margin:,.2f}",
                f"{profit_percent:.2f}%"
            ))


def fetch_optionai_move():
    symbol = symbol_entry.get().upper()
    expiration_filter = expiration_entry.get().strip()

    if not symbol:
        messagebox.showerror("Error", "Please enter a stock symbol.")
        return

    try:
        ticker = yf.Ticker(symbol)
        current_price = ticker.history(period="1d")['Close'].iloc[-1]
        exp_dates = ticker.options
        if not exp_dates:
            messagebox.showerror("Error", "No options data found.")
            return
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching data: {e}")
        return

    exp_date = expiration_filter if expiration_filter else exp_dates[0]
    opt_chain = ticker.option_chain(exp_date)
    calls = opt_chain.calls
    puts = opt_chain.puts

    # Calculate days to expiration
    dte = (datetime.strptime(exp_date, "%Y-%m-%d") - datetime.today()).days
    if dte <= 0:
        messagebox.showerror("Error", "Expiration date must be in the future.")
        return

    # Compute average IV near ATM
    near_calls = calls[(calls['strike'] >= current_price * 0.95) & (calls['strike'] <= current_price * 1.05)]
    near_puts = puts[(puts['strike'] >= current_price * 0.95) & (puts['strike'] <= current_price * 1.05)]

    if near_calls.empty or near_puts.empty:
        messagebox.showerror("Error", "No near-ATM options found.")
        return

    call_iv = np.nanmean(near_calls['impliedVolatility'])
    put_iv = np.nanmean(near_puts['impliedVolatility'])

    # Expected move up/down
    expected_move_up = current_price * call_iv * np.sqrt(dte / 365)
    expected_move_down = current_price * put_iv * np.sqrt(dte / 365)

    upper = current_price + expected_move_up
    lower = current_price - expected_move_down

    expected_move_label.config(
        text=f"{symbol} {exp_date}\n"
             f"Current Price: ${current_price:,.2f}\n"
             f"Expected Move (68%): ${lower:,.2f} → ${upper:,.2f}\n"
             f"(Up IV: {call_iv:.2%}, Down IV: {put_iv:.2%}, DTE: {dte} days)"
    )


def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col).replace('$', '').replace(',', ''), k) for k in tv.get_children('')]
    try:
        l.sort(key=lambda t: float(t[0]), reverse=reverse)
    except ValueError:
        l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


# --- GUI ---

columns = ("Symbol", "Strike", "Expiration", "Last Price", "Bid", "Ask", "Mid Price",
           "Premium", "Volume", "Margin", "Profit %")
col_widths = {
    "Symbol": 140,
    "Strike": 70,
    "Expiration": 100,
    "Last Price": 70,
    "Bid": 70,
    "Ask": 70,
    "Mid Price": 70,
    "Premium": 70,
    "Volume": 70,
    "Margin": 100,
    "Profit %": 70
}

window_width = sum(col_widths.values()) + 40
window = tk.Tk()
window.title("Options Analyzer (Yahoo Finance)")
window.geometry(f"{window_width}x600")

tk.Label(window, text="Stock Symbol:").pack(pady=2)
symbol_entry = tk.Entry(window)
symbol_entry.pack(pady=2)

tk.Label(window, text="Target Strike Price:").pack(pady=2)
strike_entry = tk.Entry(window)
strike_entry.pack(pady=2)

tk.Label(window, text="Strike Range (±):").pack(pady=2)
range_entry = tk.Entry(window)
range_entry.pack(pady=2)

tk.Label(window, text="Expiration Date (YYYY-MM-DD, optional):").pack(pady=2)
expiration_entry = tk.Entry(window)
expiration_entry.pack(pady=2)

# Buttons
fetch_put_button = tk.Button(window, text="Fetch Put Options", command=fetch_put_options)
fetch_put_button.pack(pady=5)

fetch_move_button = tk.Button(window, text="Expected Move (OptionAI Style)", command=fetch_optionai_move)
fetch_move_button.pack(pady=5)

# Expected move display label
expected_move_label = tk.Label(window, text="", font=("Arial", 11), fg="blue", justify="center")
expected_move_label.pack(pady=10)

# Tree table
tree = ttk.Treeview(window, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(tree, _col, False))
    tree.column(col, width=col_widths[col], minwidth=col_widths[col], stretch=False)
tree.pack(expand=True, fill="both", padx=10, pady=10)

# Bind Enter key to trigger focused button
def on_enter_key(event):
    widget = window.focus_get()
    if isinstance(widget, tk.Button):
        widget.invoke()

window.bind("<Return>", on_enter_key)

window.mainloop()
