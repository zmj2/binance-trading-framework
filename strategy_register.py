from typing import Callable, Dict
import pandas as pd
from .params import StrategyParameters

_registry: Dict[str, Callable[[pd.DataFrame, StrategyParameters], pd.DataFrame]] = {}

def register_strategy(name: str):
    def wrapper(fn: Callable[[pd.DataFrame, StrategyParameters], pd.DataFrame]):
        _registry[name] = fn
        return fn
    return wrapper

def get_strategy(name: str) -> Callable[[pd.DataFrame, StrategyParameters], pd.DataFrame]:
    if name not in _registry:
        raise ValueError(f"Strategy '{name}' is not registered.")
    return _registry[name]

def list_strategies() -> list[str]:
    return list(_registry.keys())
