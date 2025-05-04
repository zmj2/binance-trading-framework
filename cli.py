import argparse, asyncio
from .data import fetch_historic_klines
from .backtest import tune_dual_ema_parameters, optuna_optimize_dual_ema_parameters
from .params import DualEMAParameters
from .live import LiveTrader
from .strategy_register import list_strategies

def _parse_args():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    bt = sub.add_parser("backtest", help="Run backtest & parameter tuning")
    bt.add_argument("--strategy", required=True, help="Strategy name. Available: " + ", ".join(list_strategies()))
    bt.add_argument("--start", required=True)
    bt.add_argument("--end", required=True)
    bt.add_argument("--fast-range", type=str, default="10,30", help="fast parameter range (e.g. 10,30)")
    bt.add_argument("--slow-range", type=str, default="40,90", help="slow parameter range (e.g. 40,90)")
    bt.add_argument("--method", choices=["grid", "optuna"], default="grid", help="Tuning method")

    tr = sub.add_parser("trade", help="Run live trading")
    tr.add_argument("--strategy", required=True, help="Strategy name. Available: " + ", ".join(list_strategies()))
    tr.add_argument("--fast", type=int, required=True)
    tr.add_argument("--slow", type=int, required=True)
    tr.add_argument("--qty", type=float, required=True)
    tr.add_argument("--mode", choices=["live", "paper"], default="paper")

    return p.parse_args()

def _parse_range(s: str) -> tuple[int, int]:
    try:
        parts = list(map(int, s.split(",")))
        assert len(parts) == 2 and parts[0] < parts[1]
        return tuple(parts)
    except Exception:
        raise ValueError(f"Invalid range format: '{s}'. Expected format like '10,30'.")
    
def main():
    ns = _parse_args()
    
    if ns.cmd == "backtest":
        df = fetch_historic_klines(ns.start, ns.end)
        fast_range = _parse_range(ns.fast_range)
        slow_range = _parse_range(ns.slow_range)

        if ns.method == "grid":
            fast_list = list(range(fast_range[0], fast_range[1] + 1, 5))
            slow_list = list(range(slow_range[0], slow_range[1] + 1, 10))
            best = tune_dual_ema_parameters(df, ns.strategy, fast_list, slow_list)
        else:
            best = optuna_optimize_dual_ema_parameters(df, ns.strategy, fast_range, slow_range, n_trials=50)

        print("Best Params:", best.params, "\tPNL:", f"{best.pnl:.2%}")

    elif ns.cmd == "trade":
        trader = LiveTrader(ns.strategy, DualEMAParameters(ns.fast, ns.slow), ns.qty, ns.mode, 10)
        asyncio.run(trader.run())

if __name__ == "__main__":
    main()
