import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf

from datetime import datetime

# --- FUNCTIONS ---
def fetch_options():
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
            mid_price = (bid + ask)/2 if (bid and ask) else last_price

            premium = mid_price * 100
            margin = strike * 100
            profit_percent = (premium / margin) * 100 if margin else 0

            tree.insert("", "end", values=(
                row_data['contractSymbol'],
                strike,
                exp,
                f"${last_price:,.2f}",
                f"${bid:,.2f}",
                f"${ask:,.2f}",
                f"${mid_price:,.2f}",
                f"${premium:,.2f}",
                f"${margin:,.2f}",
                f"{profit_percent:.2f}%"
            ))

# Sorting function
def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col).replace('$','').replace(',',''), k) for k in tv.get_children('')]
    try:
        l.sort(key=lambda t: float(t[0]), reverse=reverse)
    except ValueError:
        l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

# --- GUI ---
window = tk.Tk()
window.title("Secured Put Option Finder (Yahoo Finance)")
window.geometry("1000x500")

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

fetch_button = tk.Button(window, text="Fetch Put Options", command=fetch_options)
fetch_button.pack(pady=5)

columns = ("Symbol", "Strike", "Expiration", "Last Price", "Bid", "Ask", "Mid Price", "Premium", "Margin", "Profit %")
tree = ttk.Treeview(window, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(tree, _col, False))
tree.pack(expand=True, fill="both", padx=10, pady=10)

window.mainloop()
