import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import numpy as np
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- EXPECTED MOVE CALCULATIONS ---

def calculate_expected_move(symbol, expiration=None):
    """
    Option AI style:
    Uses ATM call+put mid-prices for nearest expiration.
    """
    ticker = yf.Ticker(symbol)
    exp_dates = ticker.options
    if not exp_dates:
        return None, None, None

    exp = expiration if expiration in exp_dates else exp_dates[0]
    opt_chain = ticker.option_chain(exp)

    stock_price = ticker.history(period="1d")["Close"].iloc[-1]

    strikes = opt_chain.calls["strike"]
    atm_strike = strikes.iloc[(strikes - stock_price).abs().argsort().iloc[0]]

    call_row = opt_chain.calls[opt_chain.calls["strike"] == atm_strike].iloc[0]
    put_row = opt_chain.puts[opt_chain.puts["strike"] == atm_strike].iloc[0]

    call_mid = (call_row["bid"] + call_row["ask"]) / 2
    put_mid = (put_row["bid"] + put_row["ask"]) / 2
    expected_move = call_mid + put_mid
    expected_move_pct = (expected_move / stock_price) * 100

    lower = stock_price - expected_move
    upper = stock_price + expected_move
    return expected_move, expected_move_pct, (lower, upper)


def calculate_expected_move_barchart(symbol, expiration=None):
    """
    Barchart style:
    Also uses ATM straddle, same math but displayed differently.
    """
    ticker = yf.Ticker(symbol)
    exp_dates = ticker.options
    if not exp_dates:
        return None, None, None

    exp = expiration if expiration in exp_dates else exp_dates[0]
    opt_chain = ticker.option_chain(exp)

    stock_price = ticker.history(period="1d")["Close"].iloc[-1]

    strikes = opt_chain.calls["strike"]
    atm_strike = strikes.iloc[(strikes - stock_price).abs().argsort().iloc[0]]

    call_row = opt_chain.calls[opt_chain.calls["strike"] == atm_strike].iloc[0]
    put_row = opt_chain.puts[opt_chain.puts["strike"] == atm_strike].iloc[0]

    call_mid = (call_row["bid"] + call_row["ask"]) / 2
    put_mid = (put_row["bid"] + put_row["ask"]) / 2
    expected_move = call_mid + put_mid
    expected_move_pct = (expected_move / stock_price) * 100

    lower = stock_price - expected_move
    upper = stock_price + expected_move
    return expected_move, expected_move_pct, (lower, upper)


# --- OPTION FETCHING LOGIC ---

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

        puts_filtered = puts[
            (puts['strike'] >= target_strike - range_val) & 
            (puts['strike'] <= target_strike + range_val)
        ]

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


# --- SORTING FUNCTION ---

def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col).replace('$','').replace(',',''), k) for k in tv.get_children('')]
    try:
        l.sort(key=lambda t: float(t[0]), reverse=reverse)
    except ValueError:
        l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


# --- EXPECTED MOVE DISPLAY AND CHART ---

def show_expected_move(style):
    symbol = symbol_entry.get().upper()
    expiration_filter = expiration_entry.get() or None

    try:
        if style == "ai":
            expected_move, expected_move_pct, (lower, upper) = calculate_expected_move(symbol, expiration_filter)
            label_text = f"[Option AI] ±${expected_move:.2f} ({expected_move_pct:.2f}%) → Range: ${lower:.2f} – ${upper:.2f}"

        else:
            expected_move, expected_move_pct, (lower, upper) = calculate_expected_move_barchart(symbol, expiration_filter)
            label_text = f"[Barchart] ±${expected_move:.2f} ({expected_move_pct:.2f}%) → Range: ${lower:.2f} – ${upper:.2f}"

        expected_move_label.config(text=label_text)
        draw_expected_move_chart(symbol, lower, upper)

    except Exception as e:
        expected_move_label.config(text=f"Error: {e}")


def draw_expected_move_chart(symbol, lower, upper):
    for widget in chart_frame.winfo_children():
        widget.destroy()

    ticker = yf.Ticker(symbol)
    stock_price = ticker.history(period="1d")["Close"].iloc[-1]

    fig = Figure(figsize=(5, 1.5), dpi=100)
    ax = fig.add_subplot(111)

    ax.axvline(stock_price, color='blue', linestyle='--', label="Current Price")
    ax.axvspan(lower, upper, color='orange', alpha=0.3, label="Expected Move Range")

    # Ensure minimum x-axis width
    width = max(upper - lower, stock_price * 0.1)  # at least 10% of stock price
    ax.set_xlim(stock_price - width, stock_price + width)

    ax.set_xlabel("Price ($)")
    ax.set_yticks([])
    ax.legend(loc="upper right", fontsize=8)
    ax.set_title(f"Expected Move Range: {symbol}", fontsize=10)

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


# --- GUI SETUP ---

columns = ("Symbol", "Strike", "Expiration", "Last Price", "Bid", "Ask", 
           "Mid Price", "Premium", "Volume", "Margin", "Profit %")

col_widths = {
    "Symbol": 140, "Strike": 70, "Expiration": 100, "Last Price": 70,
    "Bid": 70, "Ask": 70, "Mid Price": 70, "Premium": 70,
    "Volume": 70, "Margin": 100, "Profit %": 70
}

window_width = sum(col_widths.values()) + 40
window = tk.Tk()
window.title("Options Analyzer (Put Finder + Expected Move Visualizer)")
window.geometry(f"{window_width}x700")
window.eval('tk::PlaceWindow . center')

# --- INPUTS ---
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

# --- BUTTONS ---
fetch_button = tk.Button(window, text="Fetch Put Options", command=fetch_options)
fetch_button.pack(pady=5)

fetch_ai_button = tk.Button(window, text="Expected Move (Option AI Style)", command=lambda: show_expected_move("ai"))
fetch_ai_button.pack(pady=3)

fetch_barchart_button = tk.Button(window, text="Expected Move (Barchart Style)", command=lambda: show_expected_move("barchart"))
fetch_barchart_button.pack(pady=3)

expected_move_label = tk.Label(window, text="", font=("Segoe UI", 10, "bold"), fg="blue")
expected_move_label.pack(pady=5)

# --- TABLE ---
tree = ttk.Treeview(window, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(tree, _col, False))
    tree.column(col, width=col_widths[col], minwidth=col_widths[col], stretch=False)
tree.pack(expand=True, fill="both", padx=10, pady=10)

# --- CHART FRAME ---
chart_frame = tk.Frame(window, height=150)
chart_frame.pack(fill="x", padx=10, pady=5)

window.mainloop()
