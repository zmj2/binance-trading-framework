from dataclasses import dataclass
from abc import ABC

@dataclass
class StrategyParameters(ABC):
    pass

@dataclass
class DualEMAParameters(StrategyParameters):
    fast: int = 20
    slow: int = 50

    def __post_init__(self):
        if self.fast >= self.slow:
            raise ValueError("fast must be < slow")

@dataclass
class YourStrategyParameters(StrategyParameters):
    '''
    Example:
    
    fast = 20
    slow = 50
    
    '''