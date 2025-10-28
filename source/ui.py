import tkinter as tk
from tkinter import ttk, messagebox
from option_fetcher import fetch_put_options, fetch_call_options

def create_ui(window):
    window_width = 800
    window = tk.Tk()
    window.title("Secured Put / Covered Call Option Finder")
    window.geometry(f"{window_width}x500")

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

    button_frame = tk.Frame(window)
    button_frame.pack(pady=5)

    fetch_put_button = tk.Button(button_frame, text="Fetch Put Options", command=lambda: fetch_put_options(symbol_entry, strike_entry, range_entry, expiration_entry))
    fetch_put_button.pack(side="left", padx=5)

    fetch_call_button = tk.Button(button_frame, text="Fetch Covered Calls", command=lambda: fetch_call_options(symbol_entry, strike_entry, range_entry, expiration_entry))
    fetch_call_button.pack(side="left", padx=5)

    columns = (
        "Symbol", "Strike", "Expiration", "Last Price", "Bid", "Ask", 
        "Mid Price", "Premium", "Volume", "Margin", "Profit %"
    )
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

    tree = ttk.Treeview(window, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=col_widths[col], minwidth=col_widths[col], stretch=False)
    tree.pack(expand=True, fill="both", padx=10, pady=10)

    return window, tree, symbol_entry, strike_entry, range_entry, expiration_entry

def run_app():
    window, tree, symbol_entry, strike_entry, range_entry, expiration_entry = create_ui()
    window.mainloop()