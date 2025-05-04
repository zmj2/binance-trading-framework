import os
from binance import Client, AsyncClient
from dotenv import load_dotenv

load_dotenv()

SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_30MINUTE
FEE_PCT = 0.0004

def _env(key: str, default: str | None = None) -> str:
    value = os.getenv(key, default)
    if value is None:
        raise RuntimeError(f"Missing env var: {key}")
    return value

def client_factory(testnet: bool = False) -> Client:
    api_key = _env("BINANCE_API_KEY", "")
    api_secret = _env("BINANCE_API_SECRET", "")
    return Client(api_key, api_secret, testnet=testnet)

async def async_client_factory(testnet: bool = False) -> AsyncClient:
    api_key = _env("BINANCE_API_KEY", "")
    api_secret = _env("BINANCE_API_SECRET", "")
    http_proxy = "http://127.0.0.1:7890"
    return await AsyncClient.create(api_key, api_secret, testnet=testnet, https_proxy=http_proxy)
