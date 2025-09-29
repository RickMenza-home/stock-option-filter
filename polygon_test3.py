import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime

# --- CONFIG ---
API_KEY = "E92jK6Mj9DkjlOQcSzAtA1ktV5epG6L1"  # Replace with your Polygon.io API key

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

    url = "https://api.polygon.io/v3/reference/options/contracts"
    params = {
        "underlying_ticker": symbol,
        "contract_type": "put",
        "limit": 1000,
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        messagebox.showerror("Error", f"API Error: {response.status_code}")
        return

    data = response.json()
    results = data.get("results", [])

    # Clear previous table
    for row in tree.get_children():
        tree.delete(row)

    for option in results:
        strike = option.get("strike_price", 0)
        exp_date = option.get("expiration_date", "")
        last_price = option.get("last_price", 0)
        bid = option.get("bid", 0)
        ask = option.get("ask", 0)
        mid_price = (bid + ask)/2 if (bid and ask) else last_price

        # Filter by strike range
        if not (target_strike - range_val <= strike <= target_strike + range_val):
            continue

        # Filter by expiration if provided
        if expiration_filter:
            try:
                exp_dt = datetime.strptime(exp_date, "%Y-%m-%d")
                filter_dt = datetime.strptime(expiration_filter, "%Y-%m-%d")
                if exp_dt != filter_dt:
                    continue
            except:
                continue

        # Profit potential = premium received (mid_price) * 100 shares
        premium = mid_price * 100
        margin = strike * 100  # cash required if assigned
        profit_percent = (premium / margin) * 100 if margin != 0 else 0

        tree.insert("", "end", values=(
            option.get("symbol"),
            strike,
            exp_date,
            f"${last_price:,.2f}",
            f"${bid:,.2f}",
            f"${ask:,.2f}",
            f"${mid_price:,.2f}",
            f"${premium:,.2f}",
            f"${margin:,.2f}",
            f"{profit_percent:.2f}%"
        ))

# Sorting function for table columns
def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col).replace('$','').replace(',',''), k) for k in tv.get_children('')]
    try:
        l.sort(key=lambda t: float(t[0]), reverse=reverse)
    except ValueError:
        l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

# --- GUI SETUP ---
window = tk.Tk()
window.title("Secured Put Option Finder")
window.geometry("1000x500")

# Inputs
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

# Table
columns = ("Symbol", "Strike", "Expiration", "Last Price", "Bid", "Ask", "Mid Price", "Premium", "Margin", "Profit %")
tree = ttk.Treeview(window, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(tree, _col, False))
tree.pack(expand=True, fill="both", padx=10, pady=10)

window.mainloop()
