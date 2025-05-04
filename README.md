# BinanceTradingFramework

A lightweight, modular cryptocurrency trading framework based on Binance Futures API. It is built with inspiration from **TradingView's Pine Script editor** and uses a **Dual EMA crossover strategy** as its example.

The framework is designed for **medium- to long-term trend-following strategies**, but is fully extensible — you can register and test your own custom strategies.

---

## 📌 Key Highlights

- ✅ Dual EMA crossover strategy as default example
- ✅ Strategy design mimics TradingView's Pine Editor
- ✅ Ideal for trend-following strategies
- ✅ Modular and customizable strategy registration system
- ✅ Backtesting with grid search or Bayesian optimization (Optuna)
- ✅ Real-time trading support (paper or live mode)
- ✅ Equity curve and signal visualization

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

---

## 📁 Project Structure

```csharp
binance_trading_framework/
├── backtest.py             # Backtesting logic + parameter tuning (grid/optuna)
├── cli.py                  # Command-line interface
├── config.py               # API key and connection setup
├── data.py                 # Kline data retrieval
├── live.py                 # Real-time trading logic
├── params.py               # Abstract base + parameter templates
├── strategy.py             # Dual EMA example strategy (or implement your own)
├── strategy_register.py    # Strategy registry system
├── visualize.py            # Chart plotting utilities
└── README.md
```

---

## 🚀 Quick Start

### 1. Example: Dual EMA Strategy

In `strategy.py`:

```python
@register_strategy("dual_ema")
def dual_ema(df: pd.DataFrame, params: YourStrategyParameters) -> pd.DataFrame:
    fast_ema = df["close"].ewm(span=params.fast, adjust=False).mean()
    slow_ema = df["close"].ewm(span=params.slow, adjust=False).mean()
    
    # Signal logic
    df["position"] = (fast_ema > slow_ema).astype(int).replace({0: -1})
    df["signal"] = ""
    df.loc[(df["position"].diff() == 2), "signal"] = "BUY"
    df.loc[(df["position"].diff() == -2), "signal"] = "SELL"

    return df
```


This function must return a DataFrame containing:

* `position`: 1 = long, -1 = short, 0 = neutral
* `signal`: e.g. `"BUY"`, `"SELL"`, `"BUY+SELL"` etc.

---

### 2. Write Your Own Strategy

You can define your own strategies by following the same structure:

```python
@register_strategy("your_strategy")
def your_strategy(df: pd.DataFrame, params: YourStrategyParameters) -> pd.DataFrame:
    # Implement your signal logic
    return df_with_signals
```

---

### 3. Run Backtest & Optimization

#### 🔢 Grid Search

```bash
python -m binance_trading_framework.cli backtest \
  --strategy dual_ema \
  --start 2024-01-01 \
  --end 2024-03-01 \
  --fast-range 10,30 \
  --slow-range 40,90 \
  --method grid
```

#### 🤖 Bayesian Optimization (Optuna)

```bash
python -m binance_trading_framework.cli backtest \
  --strategy dual_ema \
  --start 2024-01-01 \
  --end 2024-03-01 \
  --fast-range 5,20 \
  --slow-range 25,60 \
  --method optuna
```

> `--fast-range` and `--slow-range` format: `"min,max"`
> (e.g. `--fast-range 5,20` means values from 5 to 20)

---

### 4. Start Live or Paper Trading

```bash
python -m quant_trading_framework.cli trade \
  --strategy dual_ema \
  --fast 10 \
  --slow 30 \
  --qty 0.01 \
  --mode paper
```

---


## 🧪 Environment Variables

Create a `.env` file in the root directory:

```
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
```

---

## 📈 Visualization

```python
from visualize import plot_equity_curve, plot_signals

plot_equity_curve(result.equity_curve)
plot_signals(result.df_with_signals)
```

---

## ⚠️ Limitations

* Only one strategy can be run at a time in live trading mode.

* Multi-symbol or multi-timeframe strategies are not yet supported.

* No built-in risk management or position sizing logic — must be implemented per strategy.

---

## 📄 License

MIT License.

---

## 👤 Author

**Barry Chao**

Undergraduate Student in Artificial Intelligence

Xiamen University, China

💬 For quantitative trading discussions, feel free to connect:

* 📧 Email: [barryjoth@gmail.com](mailto:barryjoth@gmail.com)
* 🧠 WeChat: `zmj_418`
* 🌐 GitHub: [github.com/zmj2](https://github.com/zmj2)







