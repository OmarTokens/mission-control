# Weekly prompt: the learning loop (scheduled task, Fridays after the close)

> Run the Mission Control weekly review from `prompts/weekly.md` in this project. Research only.

Every week: what happened, what did we learn, and what one thing should we improve. If you can't find anything to improve, research harder before saying "nothing".

---

## Agent: each Friday

1. **The week in markets.** 3 bullets: what drove the market and what's next.
2. **Report card.** The household's week from **price moves only** (so deposits don't distort it) vs the S&P (and the Nasdaq if the user holds a lot of tech). Best 3 and worst 3 holdings in $. Since-start from the History tab.
3. **Grade the buys.** For each buy on the plan since last Friday:
   - did the user do it? (ask if you don't know)
   - the price change since.
   Say plainly which calls helped and which hurt.
4. **What we learned.** Max 3 bullets, each tied to a number above.
5. **One improvement.** One concrete change to the agent or the plan, for the user to accept or reject. Check before saying "none":
   - the plan against what was actually done,
   - idle cash,
   - drift,
   - signals that never turned into a decision,
   - tax deadlines.
6. **Mix.** Each sleeve vs target and the drift band (this is the only email that shows it). If something is outside the band, give 2 options:
   - A) sell inside retirement accounts first (no tax),
   - B) point new money at the gap.
7. **Tax check.** Run `tools/harvest_check.py`.
   - List HARVEST/NEAR names, their status and any wash guard.
   - From Dec 1, add: "last trade date for this tax year is Dec 31".
8. **Plug-ins.**
   - [Value Cruiser](https://github.com/OmarTokens/value-cruiser): its Friday logbook line.
   - [Twin Turbo](https://github.com/OmarTokens/twin-turbo-trader): its Pit Report line and current value as a satellite.
9. **Next week.**
   - The next buy date and what's on it.
   - Earnings for held and value-sleeve names.
   - Fed/CPI dates.
   - Ask for one fresh holdings screenshot so the plan-vs-done check stays current.
10. Email it (only to the saved address) with the snapshot block on top. Append the week to a `learning-log.md` in the project (newest first).

Guardrails: same as the daily emails.
