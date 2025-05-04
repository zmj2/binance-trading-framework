from .strategy_register import register_strategy
import pandas as pd
import numpy as np
from .params import DualEMAParameters, YourStrategyParameters

@register_strategy("dual_ema")
def dual_ema_strategy(df: pd.DataFrame, params: DualEMAParameters) -> pd.DataFrame:
    fast_ema = df['close'].ewm(span=params.fast, adjust=False).mean()
    slow_ema = df['close'].ewm(span=params.slow, adjust=False).mean()
    sig = np.where(fast_ema > slow_ema, 1, -1)

    df_out = df.copy()
        
    df_out["fast_ema"] = fast_ema
    df_out["slow_ema"] = slow_ema
    df_out["position"] = pd.Series(sig, index=df.index).shift(1).fillna(0).astype(int)
    df_out["prev_pos"] = df_out["position"].shift(1).fillna(0).astype(int)
    df_out["signal"] = ""

    df_out.loc[(df_out["prev_pos"] == 0) & (df_out["position"] == 1), "signal"] = "BUY"
    df_out.loc[(df_out["prev_pos"] == 1) & (df_out["position"] == 0), "signal"] = "SELL"
    df_out.loc[(df_out["prev_pos"] == 1) & (df_out["position"] == -1), "signal"] = "SELL+BUY"
    df_out.loc[(df_out["prev_pos"] == 0) & (df_out["position"] == -1), "signal"] = "SELL"
    df_out.loc[(df_out["prev_pos"] == -1) & (df_out["position"] == 0), "signal"] = "BUY"
    df_out.loc[(df_out["prev_pos"] == -1) & (df_out["position"] == 1), "signal"] = "BUY+SELL"
    
    return df_out


@register_strategy("your_strategy")
def your_strategy(df: pd.DataFrame, params: YourStrategyParameters) -> pd.DataFrame:
    """
    Template strategy function, users need to implement it by themselves.
    The returned DataFrame should include:
        - position: current position direction (1: long position, -1: short position, 0: short position)
        - signal: trading signal, such as "BUY", "SELL"
    """
    raise NotImplementedError("Please implement your strategy logic")
