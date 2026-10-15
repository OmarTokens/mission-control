# Daily emails: Morning Brief + Close Recap (scheduled task, weekdays)

> Morning (about 8:40 ET, right after the 8:30 data): "Run the Mission Control **Morning Brief** from `prompts/daily-scan.md` in this project. Research only."
> After the close (about 4:20 ET): "Run the Mission Control **Close Recap** from `prompts/daily-scan.md` in this project. Research only."

The daily emails prepare you for **the market**, not for rebalancing. Mix vs target and drift live in the Friday email (`prompts/weekly.md`).

---

## Agent: both emails

1. **Trading day?** If US markets are closed today, stop (the morning email may send one line: "market closed today").
2. **Read the tracker.** Download the Google Sheet as .xlsx (Google Drive connector). Holdings change only when the user reports a trade or sends a screenshot.
3. **Prices.** Pre-market (morning) or after-hours (evening) quotes for the S&P 500 (SPY), Nasdaq-100 (QQQ) and every held ticker, from a market-data connector if you have one (e.g. Interactive Brokers, read-only). If you can't get them, say so in one line. Never guess a price.
4. **Research** with web search (dated sources, never invent a number):
   - Morning: what moved markets yesterday/overnight and why; today's economic calendar with times and consensus (and the 8:30 numbers if already out, plus how futures reacted); earnings today/tonight that matter for held names or their sector; one line of news for any held name moving ±3% pre-market.
   - Evening: why the market moved today; after-the-bell earnings/news hitting held names; tomorrow's calendar.
5. **Plan check** (from `my_data/plan.csv`, the user's buy dates):
   - Is today a buy date? Show what's on it. Otherwise: "No buy today. Next: <date>: <what>".
   - **Dip rule:** if the S&P closed at least the Control Center "Dip rule" % below its high, say so at the top: "pull the next buy date forward". Pull forward one date per drop.
   - **Wash-sale guard:** run `python3 tools/harvest_check.py --dir my_data --prices <today's prices csv>`. Never list a buy of a ticker under a WASH GUARD, in any account. Mention a harvest only on a down day (S&P −2% or the dip rule) when one says CLEAN NOW.
6. **Email** (HTML, inline styles, only to the user's saved address). Model it on `docs/demo/morning_brief.html`:
   - **Morning Brief**:
     1. headline + lede (the day's main driver; is it a buy date?)
     2. What's driving the market (3 bullets + one line of index moves)
     3. Today's calendar (ET)
     4. Your money: value, last session $/% vs the S&P, exposure to today's theme (e.g. "chips = 8% of the household"), pre-market moves on held names in $, and "every 5% move in <theme> ≈ $X"
     5. Today's plan (buy date, dip rule, tax line if relevant)
     6. Your agent's take (one short paragraph)
     7. On my radar (≤3 bullets)
   - **Close Recap**:
     1. headline
     2. why the market moved (3 bullets + index line)
     3. your day in $ vs the S&P/Nasdaq with top 3 gainers/losers
     4. after the bell
     5. tomorrow
     6. tax/wash flags only if any
   - End: links to the live snapshot and tracker, then "Research only — you decide every trade."
7. **Write to the sheet** (optional): one JSON into `_inbox!A1`, then **Mission Control → Apply inbox**. The evening run adds a `history` entry with the S&P close.

## Guardrails
- Never place, queue or stage trades, order instructions or alerts.
- No sell advice in the daily emails. Never invent a number; if data is missing, say so.
- Respect the user's exclusions and standing preferences saved in the project.
