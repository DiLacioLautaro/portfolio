# Portfolio rebalancing — Fintual exercise

`Portfolio` with a collection of `Stock`s, a target allocation (e.g. 40% META / 60% AAPL)
and a `rebalance()` method that returns which stocks to sell and which to buy.

```bash
pip install pytest
python -m pytest -q      # 11 tests
```

```python
from portfolio import Portfolio, Stock

stocks = {"META": Stock("META", lambda: 100), "AAPL": Stock("AAPL", lambda: 200)}
p = Portfolio({"META": "0.4", "AAPL": "0.6"}, stocks, holdings={"META": 5, "AAPL": 2})
for o in p.rebalance():
    print(o.action, o.symbol, o.shares)
# SELL META 1.4
# BUY AAPL 0.7
```

## Decisions
- `Decimal` for money, no floats.
- Orders come back SELLs first, then BUYs (selling funds the buys). `rebalance()` doesn't mutate; `apply()` does.
- Fractional shares by default; `allow_fractional=False` rounds buys down so we never overspend (leftover stays as cash).
- `tolerance` skips trades when a position is already close to its target.
- Stocks held but not in the allocation are sold completely. Cash inside the portfolio is invested.
- Out of scope: fees, taxes, minimum order sizes, short selling.

## AI usage (as the exercise asks)
This solution was written with Claude (Anthropic's AI), working at Lautaro Di Lacio's request.
The conversation is in [CONVERSATION.md](CONVERSATION.md).
