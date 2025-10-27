import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
from datetime import datetime

# --- FUNCTIONS ---
def fetch_put_options():
    fetch_options(option_type="put")

def fetch_call_options():
    fetch_options(option_type="call")

def fetch_options(option_type="put"):
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
        options_df = opt_chain.puts if option_type == "put" else opt_chain.calls

        # Filter by strike range
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

            # Margin: for puts = strike*100; for calls = underlying price * 100
            if option_type == "put":
                margin = strike * 100
            else:
                try:
                    current_price = ticker.history(period="1d")["Close"].iloc[-1]
                except:
                    current_price = strike
                margin = current_price * 100

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

    msg = "Put Options" if option_type == "put" else "Covered Calls"
    window.title(f"{msg} - {symbol}")


# Sorting function
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

window_width = sum(col_widths.values()) + 20
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

# --- Keyboard bindings ---
def on_enter_key(event):
    widget = window.focus_get()
    if widget == fetch_put_button:
        fetch_put_options()
    elif widget == fetch_call_button:
        fetch_call_options()

window.bind("<Return>", on_enter_key)

# Buttons for PUTs and CALLs
button_frame = tk.Frame(window)
button_frame.pack(pady=5)

fetch_put_button = tk.Button(button_frame, text="Fetch Put Options", command=fetch_put_options)
fetch_put_button.pack(side="left", padx=5)

fetch_call_button = tk.Button(button_frame, text="Fetch Covered Calls", command=fetch_call_options)
fetch_call_button.pack(side="left", padx=5)

tree = ttk.Treeview(window, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(tree, _col, False))
    tree.column(col, width=col_widths[col], minwidth=col_widths[col], stretch=False)
tree.pack(expand=True, fill="both", padx=10, pady=10)

window.mainloop()
