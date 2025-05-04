import matplotlib.pyplot as plt
import pandas as pd

def plot_equity_curve(equity: pd.Series, title: str = "Equity Curve"):
    plt.figure(figsize=(14, 7))
    equity.plot()
    plt.title(title)
    plt.ylabel("Equity")
    plt.xlabel("Date")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_dual_ema_signals(df: pd.DataFrame, title: str = "Signals"):
    plt.figure(figsize=(14, 6))
    df["close"].plot(label="Close", color="gray", alpha=0.5)
    if "fast_ema" in df:
        df["fast_ema"].plot(label="Fast Line", linestyle="--")
    if "slow_ema" in df:
        df["slow_ema"].plot(label="Slow Line", linestyle="-")

    buy_signals = df[df["signal"].str.contains("BUY", na=False)]
    sell_signals = df[df["signal"].str.contains("SELL", na=False)]

    plt.scatter(buy_signals.index, buy_signals["close"], marker="^", color="green", label="BUY", zorder=5)
    plt.scatter(sell_signals.index, sell_signals["close"], marker="v", color="red", label="SELL", zorder=5)

    plt.legend()
    plt.title(title)
    plt.grid()
    plt.tight_layout()
    plt.show()
