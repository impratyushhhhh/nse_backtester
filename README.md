<h1 align="center">📈 NSE Backtester</h1>
<p align="center">
  <b>Quantitative Trading Strategy Backtesting Tool for the Indian Stock Market</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/yfinance-Live%20Data-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/matplotlib-Charts-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?style=for-the-badge" />
</p>

---

## 🧠 What Is This?

**NSE Backtester** is an interactive Python tool that lets you:

1. Pick any **NSE stock** (Reliance, TCS, Infosys, NIFTY 50, etc.)
2. Choose **how many days** of history you want to analyze
3. Apply a **trading strategy** (Simple Moving Average based)
4. Simulate a **realistic portfolio** with brokerage fees & slippage
5. See whether the strategy **beat the market** (Buy & Hold benchmark)

Everything runs from the **terminal** — just type `python main.py` and follow the prompts.

---

## 📸 Sample Output

<p align="center">
  <img src="sample_output.png" alt="Backtest Chart - RELIANCE.NS" width="850"/>
</p>

```
------------------------------------------------------------
  BACKTEST PERFORMANCE METRICS
------------------------------------------------------------
    Ticker                           RELIANCE.NS
    Initial Capital (Rs.)            100000.0
    Final Capital (Rs.)              98542.30
    Strategy Total Return (%)        -1.46
    Benchmark Return (%)             -5.23
    Alpha vs Benchmark (%)           3.77
    Sharpe Ratio                     0.42
    Strategy Max Drawdown (%)        -8.12
    Win Rate (%)                     50.0
```

---

## 🗂️ Project Structure

```
nse_backtester/
│
├── main.py              # Entry point — takes user input & runs everything
├── data_fetcher.py      # Downloads & cleans Yahoo Finance data
├── strategy.py          # SMA indicator calculation & signal generation
├── backtester.py        # Portfolio simulation engine & performance metrics
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore rules
└── README.md            # You are here
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10** or higher
- Internet connection (to download live stock data)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/nse-backtester.git
cd nse-backtester

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

The program will interactively prompt you for:

| Prompt | Example Input | Default |
|---|---|---|
| Stock ticker | `RELIANCE`, `TCS`, `INFY`, `NIFTY` | — |
| Number of days | `30`, `90`, `180`, `365` | — |
| Strategy type | `1` (Single SMA) or `2` (Crossover) | `1` |
| SMA window | `20`, `50`, `100` | `50` |
| Initial capital (Rs.) | `100000`, `500000` | `100000` |

---

## ⚙️ Features

### 📡 Live Market Data
- Fetches real OHLCV data from **Yahoo Finance** via `yfinance`
- Supports all **NSE stocks** (`.NS` suffix auto-added) and indices (`NIFTY 50`, `Bank NIFTY`)
- Handles `yfinance` v1.2+ MultiIndex column format automatically

### 📊 Trading Strategies

| Strategy | Logic | Best For |
|---|---|---|
| **Single SMA** | BUY when price > SMA, SELL when price < SMA | Trend following |
| **Dual SMA Crossover** | BUY on Golden Cross, SELL on Death Cross | Reducing false signals |

### 💰 Realistic Portfolio Simulation
- Tracks **cash balance** and **share holdings** bar-by-bar
- Applies **0.1% brokerage** (STT + exchange fees) on every trade
- Models **0.05% slippage** (market impact)
- Logs every trade: entry/exit price, P&L, holding period, outcome

### 📈 Performance Metrics

| Metric | Description |
|---|---|
| Total Return (%) | Net portfolio gain/loss |
| CAGR (%) | Compound Annual Growth Rate |
| Sharpe Ratio | Risk-adjusted return (vs 6% risk-free rate) |
| Sortino Ratio | Downside-risk-adjusted return |
| Max Drawdown (%) | Worst peak-to-trough decline |
| Alpha (%) | Outperformance vs Buy & Hold |
| Win Rate (%) | Percentage of profitable trades |
| Profit Factor | Gross profits / Gross losses |

### 📉 3-Panel Visualization
1. **Price Action** — Close price + SMA lines + BUY/SELL markers
2. **Equity Curve** — Strategy portfolio vs Buy & Hold benchmark
3. **Drawdown Profile** — Underwater equity chart showing risk

---

## 🧩 Module Details

### `data_fetcher.py`
Downloads historical stock data and handles all the messy cleanup:
- Auto-appends `.NS` for NSE tickers, resolves aliases (`NIFTY` → `^NSEI`)
- Flattens yfinance MultiIndex columns
- Forward-fills/back-fills missing prices, removes bad ticks
- Validates minimum data requirements

### `strategy.py`
Implements trading strategies using an **abstract base class** pattern:
- `SingleSMAStrategy` — Price vs N-day SMA crossover
- `SMACrossoverStrategy` — Fast SMA vs Slow SMA crossover (Golden/Death Cross)
- Outputs `Position` (1 = invested, 0 = cash) and `Signal` (+1 = BUY, -1 = SELL)

### `backtester.py`
The simulation engine that turns signals into a portfolio track record:
- Executes trades with transaction costs and slippage
- Computes daily mark-to-market equity values
- Calculates all quantitative performance metrics
- Generates publication-quality matplotlib charts

### `main.py`
Interactive CLI that ties everything together:
- Input validation with sensible defaults and error messages
- Downloads extra data for SMA warm-up, then trims to the user's exact day count
- Displays formatted metrics table + full trade log
- Saves the chart as a PNG file

---

## 🔧 Tech Stack

| Library | Purpose |
|---|---|
| `pandas` | Data manipulation and time-series handling |
| `yfinance` | Yahoo Finance API for live market data |
| `matplotlib` | Chart generation and visualization |
| `numpy` | Numerical computations (returns, ratios) |

---

## 📝 Key Concepts Demonstrated

- **Financial Data Acquisition** — Fetching and cleaning real market data via APIs
- **Technical Analysis** — Computing indicators (SMA) on time-series data
- **Algorithmic Trading** — Rule-based signal generation from quantitative models
- **Portfolio Simulation** — Tracking cash flows, holdings, and equity over time
- **Risk Management** — Measuring drawdowns, volatility, and risk-adjusted returns
- **Object-Oriented Design** — Abstract base classes for extensible strategy architecture
- **Data Visualization** — Multi-panel charts for performance analysis

---

## ⚠️ Limitations

- Uses **daily closing prices** only (no intraday)
- Executes at close price (no limit/stop orders)
- Does not account for corporate actions (stock splits, dividends, bonuses)
- Single-stock analysis only (no multi-asset portfolio optimization)
- Slippage is a flat percentage estimate

---

## 📄 License

This project is developed for **academic and educational purposes**.

---

<p align="center">
  Made with ❤️ in Python
</p>
