from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class BaseStrategy(ABC):

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        df = self.calculate_indicators(data)
        df = self.generate_signals(df)
        return df


class SingleSMAStrategy(BaseStrategy):

    def __init__(self, window: int = 50):
        super().__init__(name=f"{window}-Day SMA Trend Following")
        if window < 2:
            raise ValueError("SMA window must be at least 2 trading sessions.")
        self.window = window
        self.sma_col = f"SMA_{self.window}"

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df[self.sma_col] = df["Close"].rolling(window=self.window, min_periods=self.window).mean()
        df[f"{self.sma_col}_Dist_Pct"] = ((df["Close"] - df[self.sma_col]) / df[self.sma_col]) * 100
        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        if self.sma_col not in df.columns:
            df = self.calculate_indicators(df)

        df["Position"] = np.where(df["Close"] > df[self.sma_col], 1, 0)
        df["Position"] = df["Position"].fillna(0).astype(int)

        df["Signal"] = df["Position"].diff().fillna(0).astype(int)

        return df


class SMACrossoverStrategy(BaseStrategy):

    def __init__(self, fast_window: int = 20, slow_window: int = 50):
        super().__init__(name=f"Dual SMA Crossover ({fast_window}/{slow_window})")
        if fast_window >= slow_window:
            raise ValueError(
                f"Fast SMA window ({fast_window}) must be strictly less than Slow SMA window ({slow_window})."
            )
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.fast_col = f"SMA_{self.fast_window}"
        self.slow_col = f"SMA_{self.slow_window}"

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df[self.fast_col] = df["Close"].rolling(window=self.fast_window, min_periods=self.fast_window).mean()
        df[self.slow_col] = df["Close"].rolling(window=self.slow_window, min_periods=self.slow_window).mean()
        df["SMA_Spread"] = df[self.fast_col] - df[self.slow_col]
        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        if self.fast_col not in df.columns or self.slow_col not in df.columns:
            df = self.calculate_indicators(df)

        df["Position"] = np.where(df[self.fast_col] > df[self.slow_col], 1, 0)
        df["Position"] = df["Position"].fillna(0).astype(int)

        df["Signal"] = df["Position"].diff().fillna(0).astype(int)

        return df


def get_strategy_stats(df_with_signals: pd.DataFrame) -> Dict[str, Any]:
    total_bars = len(df_with_signals)
    buy_signals = int((df_with_signals["Signal"] == 1).sum())
    sell_signals = int((df_with_signals["Signal"] == -1).sum())
    days_invested = int((df_with_signals["Position"] == 1).sum())
    market_exposure_pct = (days_invested / total_bars * 100) if total_bars > 0 else 0.0

    return {
        "Total Sessions": total_bars,
        "Buy Triggers": buy_signals,
        "Sell Triggers": sell_signals,
        "Sessions in Market": days_invested,
        "Market Exposure (%)": round(market_exposure_pct, 2),
    }


def create_strategy(strategy_type: str = "single_sma", **kwargs) -> BaseStrategy:
    st_type = strategy_type.lower().strip()
    if st_type in ["single_sma", "50_sma", "sma"]:
        window = kwargs.get("window", 50)
        return SingleSMAStrategy(window=window)
    elif st_type in ["sma_crossover", "crossover", "golden_cross"]:
        fast = kwargs.get("fast_window", 20)
        slow = kwargs.get("slow_window", 50)
        return SMACrossoverStrategy(fast_window=fast, slow_window=slow)
    else:
        raise ValueError(
            f"Unknown strategy type '{strategy_type}'. "
            f"Available types: 'single_sma', 'sma_crossover'"
        )


if __name__ == "__main__":
    import sys
    from pathlib import Path

    current_dir = Path(__file__).resolve().parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

    from data_fetcher import fetch_nse_data

    print("Fetching sample data for INFY...")
    df = fetch_nse_data("INFY", period="1y")

    print("\nApplying 50-Day Single SMA Strategy...")
    strat = SingleSMAStrategy(window=50)
    result_df = strat.run(df)

    stats = get_strategy_stats(result_df)
    print("Strategy Diagnostics:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    signals_subset = result_df[result_df["Signal"] != 0][["Close", "SMA_50", "Signal"]]
    print("\nGenerated Buy/Sell Signals:")
    print(signals_subset.tail(6))
