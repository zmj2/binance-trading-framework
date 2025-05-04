import datetime as dt
import pandas as pd
from binance.enums import HistoricalKlinesType
from .config import SYMBOL, INTERVAL, client_factory

def _to_milliseconds(ts: str | dt.datetime) -> int:
    if isinstance(ts, str):
        ts = pd.to_datetime(ts, utc=True)
    return int(ts.timestamp() * 1000)

def fetch_historic_klines(start: str | dt.datetime, end: str | dt.datetime) -> pd.DataFrame:
    client = client_factory()
    start_ts = _to_milliseconds(start)
    end_ts = _to_milliseconds(end)

    all_klines = []
    limit = 500

    while start_ts < end_ts:
        klines = client.futures_klines(
            symbol=SYMBOL,
            interval=INTERVAL,
            startTime=start_ts,
            endTime=end_ts,
            limit=limit,
            klines_type=HistoricalKlinesType.FUTURES,
        )
        if not klines:
            break

        all_klines.extend(klines)
        last_open_time = klines[-1][0]
        start_ts = last_open_time + 1

        if len(klines) < limit:
            break

    if not all_klines:
        return pd.DataFrame()

    columns = [
        "open_time", "open", "high", "low", "close", "volume", 
        "close_time", "quote_asset_volume", "num_trades", "taker_base_vol",
        "taker_quote_vol", "ignore"
    ]
    df = pd.DataFrame(all_klines, columns=columns)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df.set_index("open_time", inplace=True)
    return df[["open", "high", "low", "close", "volume"]].astype(float)
