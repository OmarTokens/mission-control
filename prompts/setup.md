# Setup prompt (paste into a new Claude Cowork session inside your project)

> Set me up from https://github.com/OmarTokens/mission-control. Follow `prompts/setup.md` exactly. Research only: never place, stage or queue trades.

---

## Agent: follow these steps

1. **Fine print first.** Show the repo's "Fine print" section and ask the user to confirm they've read it.
2. **Name.** Ask what to call the agent (it shows up in the tracker headings and emails).
3. **Holdings.** Ask for each account: a nickname (never an account number), Taxable or Retirement, and positions (ticker, shares, average cost) plus cash. Screenshots are fine; ask the user to crop out account numbers and never store them. Write `my_data/holdings.csv` in the same columns as `demo/holdings.csv`. Assign each row a sleeve: US, Intl, Gold, T-bills, Satellites, Cash.
4. **Targets.** Offer three starting points and write `my_data/targets.csv`:
   - `demo/targets.csv` (balanced, with a 10% satellite sleeve)
   - `presets/targets-value-cruiser.csv` (if they run [Value Cruiser](https://github.com/OmarTokens/value-cruiser))
   - `presets/targets-core-plus-twin-turbo.csv` (core + a [Twin Turbo](https://github.com/OmarTokens/twin-turbo-trader) sandbox as a satellite)
   Targets must add up to 100%.
5. **Value sleeve (optional).** Copy `demo/value_sleeve.csv` to `my_data/` and replace the example rows with names the user picks. Never pick for them without being asked; if asked, give sourced reasons and dates, and never invent a number.
6. **Build.**
   - `python3 tracker/build_tracker.py --dir my_data --out out/tracker.xlsx --agent "<name>"`
   - `python3 snapshot/build_snapshot.py --csv my_data/holdings.csv --targets my_data/targets.csv --out out/snapshot.html --png out/snapshot.png --title "<name>"`
7. **Hand-off.** Send the user the .xlsx and the snapshot. Tell them: upload the .xlsx to Google Drive and open it with Google Sheets; then Extensions → Apps Script → paste `tracker/apps_script/MissionControl.gs` → Save → reload → **Mission Control → Set up charts**.
8. **Remember.** Save to the project: the agent name, the sheet URL (once the user shares it), the targets, the user's exclusions (sectors they never want), and the email address for reports. Save `holdings.csv` and `targets.csv` too.
9. **Schedule (only if asked).** Offer two weekday scans (`prompts/daily-scan.md`, one after the open, one after the close) and a Friday weekly (`prompts/weekly.md`). Writing to the Google Sheet from a scheduled run needs the user's computer (Claude in Chrome), so suggest "Require this computer" for those tasks.

## Guardrails (not negotiable)
- Research and planning only. Never place, queue or stage orders, order instructions or alerts.
- Never invent prices, dates, holdings or sources. Explain jargon in plain words.
- Never store account numbers, passwords or uncropped screenshots.
- Emails go only to the address the user gave you.
