import tkinter as tk
from tkinter import ttk, messagebox
import requests

# polygon.io key
API_KEY = "E92jK6Mj9DkjlOQcSzAtA1ktV5epG6L1"  # Replace with your Polygon.io API key

def fetch_options():
    symbol = symbol_entry.get().upper()
    min_strike = strike_entry.get()
    
    try:
        min_strike = float(min_strike)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid strike price")
        return
    
    url = f"https://api.polygon.io/v3/reference/options/contracts?underlying_ticker={symbol}&contract_type=put&limit=100&apiKey={API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        messagebox.showerror("Error", f"API Error: {response.status_code}")
        return
    
    data = response.json()
    results = data.get("results", [])
    
    # Clear previous table
    for row in tree.get_children():
        tree.delete(row)
    
    # Filter and insert into table
    for option in results:
        strike = option.get("strike_price", 0)
        if strike >= min_strike:
            tree.insert("", "end", values=(
                option.get("symbol"),
                strike,
                option.get("expiration_date"),
                option.get("last_price")
            ))

# --- GUI Setup ---
window = tk.Tk()
window.title("Secured Put Option Finder")
window.geometry("700x400")

tk.Label(window, text="Stock Symbol:").pack(pady=5)
symbol_entry = tk.Entry(window)
symbol_entry.pack(pady=5)

tk.Label(window, text="Minimum Strike Price:").pack(pady=5)
strike_entry = tk.Entry(window)
strike_entry.pack(pady=5)

fetch_button = tk.Button(window, text="Fetch Put Options", command=fetch_options)
fetch_button.pack(pady=10)

# Table
columns = ("Symbol", "Strike", "Expiration", "Last Price")
tree = ttk.Treeview(window, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(tree, _col, False))
tree.pack(expand=True, fill="both", padx=10, pady=10)

# --- Table Sorting Function ---
def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    try:
        l.sort(key=lambda t: float(t[0]), reverse=reverse)
    except ValueError:
        l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

window.mainloop()
