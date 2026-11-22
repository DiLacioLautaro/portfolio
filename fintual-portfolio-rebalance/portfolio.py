"""Portfolio rebalancing module (Fintual take-home exercise).

Problem
-------
A Portfolio holds Stocks. Every Stock can tell its "current price". The
Portfolio also has a target allocation (e.g. 40% META, 60% AAPL). We need a
`rebalance` method that says which stocks to sell and which to buy so the
portfolio matches the target allocation.

How I thought about it
----------------------
1. Total value = sum(shares * price) of everything we hold, plus cash we
   decide to keep in the portfolio (we model the cash explicitly so that the
   method never invents money: buys are paid by sells and available cash).
2. Target value of a stock = total value * target weight.
3. Difference = target value - current value.
   - positive -> BUY  difference / price shares
   - negative -> SELL |difference| / price shares
4. Shares can be fractional (like Fintual-style investing apps) or whole
   (`allow_fractional=False`). With whole shares we round DOWN the buys and
   round the sells to the nearest whole share, so we never spend more than we
   have; the leftover stays as cash.
5. A `tolerance` band avoids noisy trades: if a position is already within
   `tolerance` (relative to the total value) of its target, we do nothing.

Money is handled with `Decimal` to avoid floating point surprises.

Assumptions (kept simple on purpose)
------------------------------------
- Allocation weights must be > 0 and add up to exactly 1 (100%).
- Every stock in the allocation has a price > 0.
- Stocks we hold but are NOT in the allocation have a target of 0%, so they
  are fully sold.
- No fees, taxes or minimum order sizes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from typing import Callable, Dict, List, Mapping, Union

Number = Union[int, float, str, Decimal]


def _d(value: Number) -> Decimal:
    """Convert to Decimal going through str so 0.1 stays 0.1."""
    return value if isinstance(value, Decimal) else Decimal(str(value))


@dataclass(frozen=True)
class Stock:
    """A stock identified by its symbol.

    `price_provider` returns the last available price. In production it would
    call a market data service; in tests we just pass a lambda.
    """

    symbol: str
    price_provider: Callable[[], Number] = field(repr=False, compare=False)

    def current_price(self) -> Decimal:
        price = _d(self.price_provider())
        if price <= 0:
            raise ValueError(f"{self.symbol}: price must be positive, got {price}")
        return price


@dataclass(frozen=True)
class Order:
    """One thing to do to rebalance: BUY or SELL `shares` of `symbol`."""

    action: str  # "BUY" | "SELL"
    symbol: str
    shares: Decimal
    price: Decimal

    @property
    def amount(self) -> Decimal:
        return (self.shares * self.price).quantize(Decimal("0.01"), ROUND_HALF_UP)


class Portfolio:
    def __init__(
        self,
        allocation: Mapping[str, Number],
        stocks: Mapping[str, Stock],
        holdings: Mapping[str, Number] | None = None,
        cash: Number = 0,
    ) -> None:
        """
        allocation: target weights by symbol, e.g. {"META": 0.4, "AAPL": 0.6}.
        stocks:     every Stock we know about (held or targeted), by symbol.
        holdings:   shares currently owned by symbol (can be fractional).
        cash:       uninvested money inside the portfolio.
        """
        self.allocation: Dict[str, Decimal] = {s: _d(w) for s, w in allocation.items()}
        self.stocks = dict(stocks)
        self.holdings: Dict[str, Decimal] = {s: _d(q) for s, q in (holdings or {}).items()}
        self.cash = _d(cash)
        self._validate()

    # -- validation --------------------------------------------------------
    def _validate(self) -> None:
        if not self.allocation:
            raise ValueError("allocation cannot be empty")
        if any(w <= 0 for w in self.allocation.values()):
            raise ValueError("every allocation weight must be > 0")
        if sum(self.allocation.values()) != Decimal(1):
            raise ValueError(
                f"allocation must add up to 1 (100%), got {sum(self.allocation.values())}"
            )
        if self.cash < 0 or any(q < 0 for q in self.holdings.values()):
            raise ValueError("cash and holdings cannot be negative")
        for symbol in set(self.allocation) | set(self.holdings):
            if symbol not in self.stocks:
                raise ValueError(f"unknown stock: {symbol}")

    # -- valuation ---------------------------------------------------------
    def value_of(self, symbol: str) -> Decimal:
        return self.holdings.get(symbol, Decimal(0)) * self.stocks[symbol].current_price()

    def total_value(self) -> Decimal:
        invested = sum((self.value_of(s) for s in self.holdings), Decimal(0))
        return invested + self.cash

    # -- the main method ---------------------------------------------------
    def rebalance(
        self,
        allow_fractional: bool = True,
        tolerance: Number = 0,
    ) -> List[Order]:
        """Return the orders needed to reach the target allocation.

        Orders are returned SELLs first, then BUYs, because selling frees the
        cash that the buys need. This method does NOT change the portfolio; use
        `apply` to execute the orders on it.

        tolerance: skip a position if |target - current| <= tolerance * total.
        """
        total = self.total_value()
        tol = _d(tolerance)
        orders: List[Order] = []

        for symbol in sorted(set(self.allocation) | set(self.holdings)):
            price = self.stocks[symbol].current_price()
            target_value = total * self.allocation.get(symbol, Decimal(0))
            diff = target_value - self.value_of(symbol)
            if abs(diff) <= tol * total:
                continue

            shares = diff / price
            if allow_fractional:
                shares = shares.quantize(Decimal("0.000001"), ROUND_HALF_UP)
            elif shares > 0:
                shares = shares.to_integral_value(ROUND_DOWN)  # never overspend
            else:
                shares = -((-shares).to_integral_value(ROUND_HALF_UP))
            # Never sell more than we own (rounding can push us over a bit).
            if shares < 0:
                shares = max(shares, -self.holdings.get(symbol, Decimal(0)))
            if shares == 0:
                continue

            action = "BUY" if shares > 0 else "SELL"
            orders.append(Order(action, symbol, abs(shares), price))

        orders.sort(key=lambda o: (o.action != "SELL", o.symbol))
        return orders

    def apply(self, orders: List[Order]) -> None:
        """Execute orders on this portfolio (updates holdings and cash)."""
        for o in orders:
            if o.action == "SELL":
                self.holdings[o.symbol] = self.holdings.get(o.symbol, Decimal(0)) - o.shares
                self.cash += o.shares * o.price
            else:
                cost = o.shares * o.price
                if cost > self.cash:
                    raise ValueError(f"not enough cash to buy {o.shares} {o.symbol}")
                self.holdings[o.symbol] = self.holdings.get(o.symbol, Decimal(0)) + o.shares
                self.cash -= cost
