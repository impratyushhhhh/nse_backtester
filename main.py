import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from datetime import datetime, timedelta
from data_fetcher import fetch_nse_data, get_data_summary, sanitize_nse_ticker, POPULAR_NSE_TICKERS
from strategy import SingleSMAStrategy, SMACrossoverStrategy, get_strategy_stats
from backtester import BacktestEngine


SEPARATOR = "-" * 60


def print_header():
    print()
    print("=" * 60)
    print("       NSE BACKTESTER - Quantitative Trading Tool")
    print("       Interactive Stock Analysis & Backtest Engine")
    print("=" * 60)
    print()


def print_popular_tickers():
    print("  Popular NSE tickers you can try:")
    for ticker, name in POPULAR_NSE_TICKERS.items():
        display_ticker = ticker if ticker.startswith("^") else f"{ticker}.NS"
        print(f"    {display_ticker:<18} {name}")
    print()


def get_ticker_input():
    print_popular_tickers()
    while True:
        raw = input("  Enter stock ticker (e.g. RELIANCE, TCS.NS, NIFTY): ").strip()
        if raw:
            formatted = sanitize_nse_ticker(raw)
            print(f"  -> Resolved ticker: {formatted}")
            return raw, formatted
        print("  [!] Ticker cannot be empty. Please try again.\n")


def get_days_input():
    print()
    print("  How many days of historical data do you want to analyse?")
    print("  Examples: 30, 60, 90, 180, 365, 730")
    while True:
        raw = input("  Enter number of days: ").strip()
        try:
            days = int(raw)
            if days < 10:
                print("  [!] Minimum 10 days required for meaningful analysis.\n")
                continue
            if days > 3650:
                print("  [!] Maximum 3650 days (10 years). Yahoo Finance may not have older data.\n")
                continue
            return days
        except ValueError:
            print("  [!] Please enter a valid whole number.\n")


def get_strategy_input(days):
    print()
    print(SEPARATOR)
    print("  Select a trading strategy:")
    print()
    print("    [1] Single SMA Trend Following")
    print("        (BUY when price crosses above SMA, SELL when below)")
    print()
    print("    [2] Dual SMA Crossover (Golden Cross / Death Cross)")
    print("        (BUY when fast SMA crosses above slow SMA, SELL on reverse)")
    print()

    while True:
        choice = input("  Your choice (1 or 2) [default: 1]: ").strip()
        if choice in ("", "1"):
            window = get_sma_window_input("SMA", default=50, max_allowed=days)
            return SingleSMAStrategy(window=window)
        elif choice == "2":
            print()
            fast = get_sma_window_input("Fast SMA", default=20, max_allowed=days)
            slow = get_sma_window_input("Slow SMA", default=50, max_allowed=days, min_allowed=fast + 1)
            return SMACrossoverStrategy(fast_window=fast, slow_window=slow)
        else:
            print("  [!] Invalid choice. Enter 1 or 2.\n")


def get_sma_window_input(label, default, max_allowed, min_allowed=2):
    while True:
        raw = input(f"  Enter {label} window period in days [default: {default}]: ").strip()
        if raw == "":
            val = default
        else:
            try:
                val = int(raw)
            except ValueError:
                print("  [!] Please enter a valid whole number.\n")
                continue

        if val < min_allowed:
            print(f"  [!] {label} window must be at least {min_allowed}.\n")
            continue
        if val >= max_allowed:
            print(f"  [!] {label} window ({val}) must be less than total days ({max_allowed}).\n")
            continue
        return val


def get_capital_input():
    print()
    while True:
        raw = input("  Enter initial investment capital in Rs. [default: 100000]: ").strip()
        if raw == "":
            return 100000.0
        try:
            val = float(raw.replace(",", ""))
            if val <= 0:
                print("  [!] Capital must be a positive number.\n")
                continue
            return val
        except ValueError:
            print("  [!] Please enter a valid number.\n")


def display_data_summary(summary):
    print()
    print(SEPARATOR)
    print("  DATA SUMMARY")
    print(SEPARATOR)
    for k, v in summary.items():
        print(f"    {k:<32} {v}")


def display_strategy_stats(stats, strategy_name):
    print()
    print(SEPARATOR)
    print(f"  STRATEGY: {strategy_name}")
    print(SEPARATOR)
    for k, v in stats.items():
        print(f"    {k:<32} {v}")


def display_metrics(metrics):
    print()
    print(SEPARATOR)
    print("  BACKTEST PERFORMANCE METRICS")
    print(SEPARATOR)
    for k, v in metrics.items():
        print(f"    {k:<32} {v}")


def display_trades(trades_df):
    print()
    print(SEPARATOR)
    print("  TRADE LOG")
    print(SEPARATOR)
    if trades_df.empty:
        print("    No trades were executed during this period.")
        print("    (The SMA window may be too large relative to the data range,")
        print("     or the stock stayed on one side of the indicator the whole time.)")
    else:
        cols_to_show = [
            "trade_num", "entry_date", "exit_date", "shares",
            "entry_price", "exit_price", "net_pnl", "return_pct",
            "holding_days", "outcome"
        ]
        available = [c for c in cols_to_show if c in trades_df.columns]
        print(trades_df[available].to_string(index=False))


def main():
    print_header()

    raw_ticker, formatted_ticker = get_ticker_input()
    days = get_days_input()
    strategy = get_strategy_input(days)
    capital = get_capital_input()

    print()
    print(SEPARATOR)
    print(f"  Downloading {days} days of data for {formatted_ticker}...")

    end_date = datetime.today()
    start_date = end_date - timedelta(days=int(days * 1.6))

    try:
        full_data = fetch_nse_data(
            raw_ticker,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )
    except (ValueError, RuntimeError) as e:
        print(f"\n  [ERROR] {e}")
        sys.exit(1)

    data = full_data.tail(days)
    print(f"  Retrieved {len(data)} trading sessions.")

    if len(data) < 10:
        print("  [ERROR] Not enough trading data. Try a larger day range or different ticker.")
        sys.exit(1)

    summary = get_data_summary(data, raw_ticker)
    display_data_summary(summary)

    print(f"\n  Applying strategy: {strategy.name}...")
    full_with_signals = strategy.run(full_data)
    data_with_signals = full_with_signals.tail(days)

    stats = get_strategy_stats(data_with_signals)
    display_strategy_stats(stats, strategy.name)

    print(f"\n  Running backtest simulation with Rs. {capital:,.0f} capital...")
    engine = BacktestEngine(initial_capital=capital, commission_rate=0.001)

    try:
        engine.run(data_with_signals, ticker=formatted_ticker)
    except Exception as e:
        print(f"\n  [ERROR] Backtest failed: {e}")
        sys.exit(1)

    display_metrics(engine.metrics)
    display_trades(engine.get_trades_df())

    safe_name = formatted_ticker.replace("^", "").replace(".NS", "").replace(".BO", "")
    chart_filename = f"backtest_{safe_name}_{days}d.png"
    chart_path = str(current_dir / chart_filename)

    try:
        saved = engine.plot_results(ticker=formatted_ticker, save_path=chart_path, show=True)
        print(f"\n  Chart saved to: {saved}")
    except Exception as e:
        print(f"\n  [WARNING] Could not generate chart: {e}")

    print()
    print("=" * 60)
    print("  Backtest complete. Thank you for using NSE Backtester!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
