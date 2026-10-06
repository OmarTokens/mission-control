# Daily scan prompt (use as a scheduled task: weekdays, once after the open and once after the close)

> Run the Mission Control daily scan from `prompts/daily-scan.md` in this project. Research only.

---

## Agent: each scan

1. **Trading day?** If US markets are closed today, stop.
2. **Read the tracker.** Download the Google Sheet as .xlsx (Google Drive connector) or read it in Chrome. Live prices come from its GOOGLEFINANCE formulas. Holdings (shares, avg cost) change only when the user reports a trade or sends a screenshot.
3. **Snapshot.** `python3 snapshot/build_snapshot.py --xlsx tracker.xlsx --out out/snapshot.html --png out/snapshot.png --title "<name>"`. If an artifact for the snapshot already exists, republish it to the same link.
4. **What changed.** For the household and each account: the day's move, the biggest movers, and anything with news (earnings, guidance, big headlines). Cite sources with dates.
5. **Decisions to surface** (never more than 6, most important first):
   - Sleeves outside the drift band (Control Center). Give **2 options**: A) sell the overweight sleeve (retirement accounts first, so no tax), B) fund the gap with new money. Add tax notes for taxable sales (gains, holding period, 30-day wash-sale rule across all accounts).
   - Value Sleeve rows flagged IN ZONE or HARVEST?.
   - Watchlist names newly in VALUE ZONE (never shrink the user's watchlist).
   - Cash sitting idle.
   - **Satellites:** if a [Twin Turbo](https://github.com/OmarTokens/twin-turbo-trader) sandbox row exists, update its value from the user's latest number and show it as one satellite; never second-guess its rules here.
6. **Write to the sheet.** Paste one JSON object into the hidden `_inbox` tab, cell A1, then run **Mission Control → Apply inbox** (format in `tracker/apps_script/MissionControl.gs`). The after-close scan also adds a `history` entry with the benchmark close.
7. **Email** (only to the user's saved address): the snapshot's email block (`out/snapshot_email.html`) on top, then the decisions with plain-word reasons, then risks. One-line disclaimer at the end: research only, you decide every trade.

## Guardrails
- Never place, queue or stage trades, order instructions or alerts.
- No unsolicited sell advice beyond the drift options above. Never invent a number; if data is missing, say so.
- Respect the user's exclusions and standing preferences saved in the project.
