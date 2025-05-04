from dataclasses import dataclass, field
from typing import List
import numpy as np
import pandas as pd
import optuna
from .params import DualEMAParameters
from .strategy_register import get_strategy
from .config import FEE_PCT

@dataclass
class BacktestResult:
    params: DualEMAParameters
    pnl: float
    trades: int
    equity_curve: pd.Series = field(repr=False)
    df_with_signals: pd.DataFrame = field(repr=False)

def backtest(df: pd.DataFrame, strategy_name: str, params: DualEMAParameters, fee_pct: float = FEE_PCT) -> BacktestResult:
    strategy_fn = get_strategy(strategy_name)
    df_with_signals = strategy_fn(df, params)
    pos = df_with_signals["position"]
    ret = df["close"].pct_change().fillna(0)
    strat_ret = pos.shift(1) * ret - fee_pct * np.abs(pos.diff().fillna(0))
    equity = (1 + strat_ret).cumprod()
    return BacktestResult(params, equity.iloc[-1] - 1, int(np.abs(pos.diff()).sum()), equity, df_with_signals)

# Grid Search Tuning
def tune_dual_ema_parameters(df: pd.DataFrame, 
                            fast_grid: List[int], 
                            slow_grid: List[int]) -> BacktestResult:
    best: BacktestResult | None = None
    for f in fast_grid:
        for s in slow_grid:
            if f >= s:
                continue
            r = backtest(df, "dual_ema", DualEMAParameters(f, s))
            if (best is None) or (r.pnl > best.pnl):
                best = r
    assert best is not None
    return best

# Optuna Optimization Tuning
def optuna_optimize_dual_ema_parameters(
    df: pd.DataFrame,
    fast_range: tuple[int, int] = (5, 50),
    slow_range: tuple[int, int] = (10, 100),
    n_trials: int = 50
) -> BacktestResult:
    """
    Use Optuna to perform Bayesian optimization for strategy parameters.

    Args:
        df: Input historical price data.
        strategy_name: Name of the registered strategy.
        fast_range: Search range for 'fast' parameter.
        slow_range: Search range for 'slow' parameter.
        n_trials: Number of optimization trials.

    Returns:
        BacktestResult with best parameters and performance.
    """
    def objective(trial: optuna.Trial) -> float:
        fast = trial.suggest_int("fast", fast_range[0], fast_range[1])
        slow = trial.suggest_int("slow", slow_range[0], slow_range[1])
        if fast >= slow:
            raise optuna.exceptions.TrialPruned()

        try:
            result = backtest(df, "dual_ema", DualEMAParameters(fast=fast, slow=slow))
            return result.pnl  # Maximize PnL
        except Exception:
            raise optuna.exceptions.TrialPruned()

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)

    best_params = study.best_params
    return backtest(df, "dual_ema", DualEMAParameters(**best_params))