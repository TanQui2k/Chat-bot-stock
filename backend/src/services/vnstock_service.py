from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta
from time import monotonic
from typing import Any, Optional


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StockPrice:
    symbol: str
    price: float
    currency: str = "VND"
    as_of: Optional[str] = None
    source: str = "vnstock"


class VnStockPriceService:
    """
    Thin wrapper around `vnstock` with best-effort compatibility across versions.
    Returns the latest known price (match/close/last) for a VN ticker.
    """

    _cache: dict[str, tuple[float, StockPrice]] = {}
    _ttl_seconds: int = 20

    def get_latest_price(self, symbol: str) -> StockPrice:
        symbol = symbol.upper().strip()
        if not symbol:
            raise ValueError("symbol is required")

        now = monotonic()
        cached = self._cache.get(symbol)
        if cached:
            ts, value = cached
            if now - ts <= self._ttl_seconds:
                return value

        # vnstock v3+: use Quote API
        try:
            from vnstock.api.quote import Quote  # type: ignore
        except ImportError as e:
            logger.error("vnstock is not installed or failed to import: %s", e)
            raise RuntimeError(
                "vnstock is not installed. Please install it with: pip install vnstock"
            ) from e
        except Exception as e:
            logger.error("Failed to import vnstock: %s", e)
            raise RuntimeError(
                "Failed to import vnstock module. Please ensure vnstock is installed correctly."
            ) from e

        df = None
        try:
            df = Quote(symbol=symbol).intraday(page_size=50)
            logger.debug("Successfully fetched intraday data for %s", symbol)
        except Exception as e:
            logger.warning("Intraday fetch failed for %s: %s. Trying historical data...", symbol, e)
            df = None

        if df is None:
            try:
                end = date.today()
                start = end - timedelta(days=10)
                df = Quote(symbol=symbol).history(
                    start=start.strftime("%Y-%m-%d"),
                    end=end.strftime("%Y-%m-%d"),
                )
                logger.debug("Successfully fetched historical data for %s", symbol)
            except Exception as e:
                logger.error("Historical data fetch failed for %s: %s", symbol, e)
                raise RuntimeError(
                    f"Failed to fetch price data for {symbol}. Please check if the ticker symbol is correct."
                ) from e

        # Extract last row price from common columns
        row = _last_row_as_dict(df)
        if not row:
            logger.error("No data returned from vnstock for %s", symbol)
            raise RuntimeError(
                f"No price data available for {symbol}. The ticker may be delisted or inactive."
            )

        price = _pick_first_number(row, ["price", "match_price", "last", "close", "adj_close", "value"])
        if price is None:
            logger.error(
                "Could not extract price from vnstock data columns for %s. Available columns: %s",
                symbol,
                list(row.keys()),
            )
            raise RuntimeError(
                f"Could not extract price from vnstock data for {symbol}. Available columns: {list(row.keys())}"
            )

        as_of = _pick_first_str(row, ["time", "datetime", "date", "trading_date"])
        value = StockPrice(symbol=symbol, price=float(price), as_of=as_of)
        self._cache[symbol] = (now, value)
        return value


def _last_row_as_dict(df: Any) -> dict[str, Any]:
    # vnstock typically returns a pandas DataFrame, but we avoid hard dependency here.
    if hasattr(df, "tail") and hasattr(df, "to_dict"):
        last = df.tail(1)
        records = last.to_dict(orient="records")
        if records:
            return records[0]
    if isinstance(df, list) and df:
        last = df[-1]
        if isinstance(last, dict):
            return last
    if isinstance(df, dict):
        return df
    return {}


def _pick_first_number(row: dict[str, Any], keys: list[str]) -> Optional[float]:
    for k in keys:
        if k in row and row[k] is not None:
            try:
                return float(row[k])
            except Exception:
                continue
    return None


def _pick_first_str(row: dict[str, Any], keys: list[str]) -> Optional[str]:
    for k in keys:
        if k in row and row[k] is not None:
            return str(row[k])
    return None

