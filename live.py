import asyncio
import datetime as dt
import pandas as pd
from binance import AsyncClient, BinanceSocketManager
from .config import SYMBOL, INTERVAL, async_client_factory
from .data import fetch_historic_klines
from .params import YourStrategyParameters
from .strategy_register import get_strategy

class LiveTrader:
    def __init__(self, strategy_name: str, params: YourStrategyParameters, qty: float, mode: str = "paper", leverage: int = 10):
        self.strategy_name = strategy_name
        self.strategy_fn = get_strategy(strategy_name)
        self.params = params
        self.qty = qty
        self.mode = mode
        self.leverage = leverage
        self.client: AsyncClient | None = None
        self.df: pd.DataFrame | None = None
        self.last_position: int = 0

    async def _ensure_client(self):
        if self.client is None:
            self.client = await async_client_factory()
            try:
                await self.client.futures_change_leverage(symbol=SYMBOL, leverage=self.leverage)
                mode_info = await self.client.futures_get_position_mode()
                if mode_info["dualSidePosition"]:
                    await self.client.futures_change_position_mode(dualSidePosition=False)
                    print("[INFO] One-way position mode is enabled")
            except Exception as e:
                print(f"[WARN] Initialization failed: {e}")
    
    async def _update_bar(self, msg):
        if not isinstance(msg, dict) or "k" not in msg:
            print(f"[WARN] Invalid message format: {msg}")
            return
        k = msg["k"]
        if not k["x"]:
            return
        ts = pd.to_datetime(k["t"], unit="ms", utc=True)
        row = {c: float(k[v]) for c, v in zip(("open", "high", "low", "close", "volume"), ("o", "h", "l", "c", "v"))}
        if self.df is None:
            self.df = fetch_historic_klines(ts - dt.timedelta(days=1), ts)
        self.df.loc[ts] = row
        self._check_signal()

    def _check_signal(self):
        result_df = self.strategy_fn(self.df, self.params)
        pos = int(result_df["position"].iloc[-1])
        if pos != self.last_position:
            print(f"[SIGNAL] {self.last_position} -> {pos} @ {self.df.index[-1]}")
            if self.mode == "live":
                asyncio.create_task(self._exec_order(pos))
            self.last_position = pos

    async def _exec_order(self, target_pos: int):
        await self._ensure_client()
        side = "BUY" if target_pos > self.last_position else "SELL"
        try:
            await self.client.futures_create_order(
                symbol=SYMBOL, side=side, type="MARKET", quantity=self.qty
            )
        except Exception as e:
            print(f"[ERROR]", e)

    async def run(self):
        await self._ensure_client()
        bm = BinanceSocketManager(self.client)
        async with bm.kline_futures_socket(symbol=SYMBOL.lower(), interval=INTERVAL) as stream:
            try:
                while True:
                    msg = await stream.recv()
                    await self._update_bar(msg)
            except Exception as e:
                print(f"[WEBSOCKET ERROR] {e}")
            finally:
                await self.client.close_connection()
