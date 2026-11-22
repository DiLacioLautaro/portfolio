from decimal import Decimal

import pytest

from portfolio import Portfolio, Stock


def stocks(**prices):
    return {s: Stock(s, lambda p=p: p) for s, p in prices.items()}


def weights(p):
    total = p.total_value()
    return {s: p.value_of(s) / total for s in p.allocation}


def test_example_from_the_exercise_40_meta_60_aapl():
    p = Portfolio(
        allocation={"META": "0.4", "AAPL": "0.6"},
        stocks=stocks(META=100, AAPL=200),
        holdings={"META": 5, "AAPL": 2},  # 500 + 400 = 900
    )
    orders = p.rebalance()
    # Target: META 360 (3.6 sh), AAPL 540 (2.7 sh)
    assert [(o.action, o.symbol, o.shares) for o in orders] == [
        ("SELL", "META", Decimal("1.4")),
        ("BUY", "AAPL", Decimal("0.7")),
    ]
    p.apply(orders)
    assert weights(p) == {"META": Decimal("0.4"), "AAPL": Decimal("0.6")}


def test_already_balanced_means_no_orders():
    p = Portfolio({"A": "0.5", "B": "0.5"}, stocks(A=10, B=10), {"A": 10, "B": 10})
    assert p.rebalance() == []


def test_cash_is_invested():
    p = Portfolio({"A": "1"}, stocks(A=50), {}, cash=1000)
    [o] = p.rebalance()
    assert (o.action, o.shares) == ("BUY", Decimal("20"))


def test_stock_not_in_allocation_is_fully_sold():
    p = Portfolio({"A": "1"}, stocks(A=10, X=5), {"A": 10, "X": 20})
    orders = p.rebalance()
    assert ("SELL", "X", Decimal("20")) in [(o.action, o.symbol, o.shares) for o in orders]


def test_whole_shares_never_spend_more_than_available():
    p = Portfolio({"A": "0.5", "B": "0.5"}, stocks(A=30, B=70), {}, cash=1000)
    orders = p.rebalance(allow_fractional=False)
    p.apply(orders)  # would raise if it overspent
    assert p.cash >= 0
    assert all(q == q.to_integral_value() for q in p.holdings.values())


def test_tolerance_skips_small_trades():
    p = Portfolio({"A": "0.5", "B": "0.5"}, stocks(A=10, B=10), {"A": 51, "B": 49})
    assert p.rebalance(tolerance="0.05") == []
    assert len(p.rebalance(tolerance="0.005")) == 2


def test_sells_come_before_buys():
    p = Portfolio({"A": "0.5", "B": "0.5"}, stocks(A=10, B=10), {"A": 0, "B": 100})
    assert [o.action for o in p.rebalance()] == ["SELL", "BUY"]


@pytest.mark.parametrize("alloc", [{"A": "0.5"}, {"A": "1.2", "B": "-0.2"}, {}])
def test_invalid_allocation_is_rejected(alloc):
    with pytest.raises(ValueError):
        Portfolio(alloc, stocks(A=1, B=1))


def test_non_positive_price_is_rejected():
    p = Portfolio({"A": "1"}, stocks(A=0), {"A": 1})
    with pytest.raises(ValueError):
        p.rebalance()
