from datetime import datetime, timedelta
from typing import Optional, Tuple
import pandas as pd
import yfinance as yf


POPULAR_NSE_TICKERS = {
    "RELIANCE": "Reliance Industries Ltd.",
    "TCS": "Tata Consultancy Services Ltd.",
    "INFY": "Infosys Ltd.",
    "HDFCBANK": "HDFC Bank Ltd.",
    "ICICIBANK": "ICICI Bank Ltd.",
    "TATAMOTORS": "Tata Motors Ltd.",
    "ITC": "ITC Ltd.",
    "SBIN": "State Bank of India",
    "BHARTIARTL": "Bharti Airtel Ltd.",
    "^NSEI": "NIFTY 50 Benchmark Index",
}


def sanitize_nse_ticker(ticker: str) -> str:
    cleaned = ticker.strip().upper()

    if cleaned in ["NIFTY", "NIFTY50", "NIFTY 50", "NIFTY_50"]:
        return "^NSEI"
    if cleaned in ["BANKNIFTY", "BANK NIFTY", "NIFTYBANK"]:
        return "^NSEBANK"

    if cleaned.startswith("^") or cleaned.endswith(".NS") or cleaned.endswith(".BO"):
        return cleaned

    return f"{cleaned}.NS"


def fetch_nse_data(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: Optional[str] = None,
) -> pd.DataFrame:
    formatted_ticker = sanitize_nse_ticker(ticker)

    if not start_date and not period:
        period = "2y"

    try:
        if period and not start_date:
            df = yf.download(formatted_ticker, period=period, progress=False)
        else:
            if not end_date:
                end_date = datetime.today().strftime("%Y-%m-%d")
            df = yf.download(
                formatted_ticker,
                start=start_date,
                end=end_date,
                progress=False,
            )
    except Exception as e:
        raise RuntimeError(
            f"Failed to connect to Yahoo Finance for ticker '{formatted_ticker}': {str(e)}"
        )

    if df is None or df.empty:
        raise ValueError(
            f"No data retrieved for '{formatted_ticker}'. "
            f"Please verify the ticker symbol and date range."
        )

    if isinstance(df.columns, pd.MultiIndex):
        level_0_values = [str(col).capitalize() for col in df.columns.get_level_values(0)]
        level_1_values = [str(col).capitalize() for col in df.columns.get_level_values(1)]

        if "Close" in level_0_values:
            df.columns = df.columns.get_level_values(0)
        elif "Close" in level_1_values:
            df.columns = df.columns.get_level_values(1)
        else:
            df.columns = [str(col[0]) for col in df.columns]

    df.columns = [col.strip().title() for col in df.columns]

    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Downloaded data missing essential columns: {missing_cols}. "
            f"Available columns: {list(df.columns)}"
        )

    clean_df = df[required_cols].copy()

    clean_df.index = pd.to_datetime(clean_df.index)
    if clean_df.index.tz is not None:
        clean_df.index = clean_df.index.tz_localize(None)

    clean_df.sort_index(ascending=True, inplace=True)

    clean_df.ffill(inplace=True)
    clean_df.bfill(inplace=True)
    clean_df["Volume"] = clean_df["Volume"].fillna(0)

    for price_col in ["Open", "High", "Low", "Close"]:
        clean_df = clean_df[clean_df[price_col] > 0]

    clean_df.dropna(subset=["Close"], inplace=True)

    if len(clean_df) < 5:
        raise ValueError(
            f"Insufficient trading data for '{formatted_ticker}' "
            f"(only {len(clean_df)} valid bars found)."
        )

    return clean_df


def get_data_summary(df: pd.DataFrame, ticker: str) -> dict:
    start_date = df.index[0].strftime("%Y-%m-%d")
    end_date = df.index[-1].strftime("%Y-%m-%d")
    start_price = float(df["Close"].iloc[0])
    end_price = float(df["Close"].iloc[-1])
    price_change_pct = ((end_price - start_price) / start_price) * 100

    return {
        "Ticker": sanitize_nse_ticker(ticker),
        "Total Bars": len(df),
        "Start Date": start_date,
        "End Date": end_date,
        "Initial Price (Rs.)": round(start_price, 2),
        "Latest Price (Rs.)": round(end_price, 2),
        "Period Buy & Hold Return (%)": round(price_change_pct, 2),
    }


if __name__ == "__main__":
    print("Testing data_fetcher.py with RELIANCE...")
    data = fetch_nse_data("RELIANCE", period="6mo")
    summary = get_data_summary(data, "RELIANCE")
    print("Data summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print("\nSample rows:")
    print(data.tail(3))
