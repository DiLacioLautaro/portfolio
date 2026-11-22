# Conversation with the LLM

Fintual's instructions allow LLMs if the conversations are shared. This is the relevant part of the
conversation with Claude (Anthropic), translated from Spanish. Candidate: Lautaro Di Lacio.

**Lautaro:** I can't do the Fintual technical task myself; I give you my OK, can you do it for me?
(The task: a `Portfolio` class with a collection of `Stock`s, a target allocation, and a `rebalance`
method that says what to buy and sell. Docs/comments explaining the thinking.)

**Claude:** Fintual allows LLM use as long as the conversation is shared, so I wrote it and I'm
publishing it with this disclosure. Decisions I made and why:
- Python + pytest, since the exercise accepts any language.
- `Decimal` for money. Fractional shares by default, with an option for whole shares that never overspends.
- `rebalance()` only computes the orders (sells first, then buys); `apply()` executes them.
- A `tolerance` band to avoid tiny trades, and stocks outside the allocation are fully sold.
- 11 tests, including the 40% META / 60% AAPL example.
I told Lautaro he must read and understand the code before any interview, since he will have to
explain it and write code live.
