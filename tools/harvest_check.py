"""Tax-loss harvest + wash-sale check (research only; you decide every trade).

Finds TAXABLE holdings with a loss worth taking, then checks the 30-day wash-sale window across EVERY account
(retirement accounts and a spouse's count too: a rebuy in an IRA makes the loss permanently lost).

  python3 tools/harvest_check.py --dir demo --prices demo/prices_down_day.csv --today 2026-10-14
  python3 tools/harvest_check.py --dir my_data --prices my_data/prices.csv --min-loss 1000 --rate 0.40

Files in --dir (see demo/ for the format):
  lots.csv          taxable open lots: account,ticker,date,shares,cost
  buys.csv          every buy in the last ~60 days in ANY account (incl. dividend reinvestments): date,account,ticker,shares,drip
  losses_taken.csv  losses you already took: date,account,ticker,loss   -> no rebuy anywhere for 31 days
  plan.csv          planned buy dates: date,what  (a ticker named in `what` counts as a future buy)
--prices: ticker,price (or holdings.csv, which has a price column).

Statuses: CLEAN NOW · WAIT until <date> (bought in the last 30 days, any account) · BLOCKED by planned buy <date>.
Not tax advice: check with a tax professional. "Substantially identical" funds (e.g. two S&P 500 funds, two gold
funds) can also trigger the rule; list them with --twins "IVV=VOO=SPLG,GLD=IAU=GLDM".
"""
import argparse, csv, os, datetime as dt

ap = argparse.ArgumentParser()
ap.add_argument('--dir', default='demo'); ap.add_argument('--prices', required=True)
ap.add_argument('--today'); ap.add_argument('--min-loss', type=float, default=300)
ap.add_argument('--rate', type=float, default=0.30, help='your tax rate on the gains the loss would offset (e.g. 0.30)')
ap.add_argument('--twins', default='')
a = ap.parse_args()
D = dt.date.fromisoformat
today = D(a.today) if a.today else dt.date.today()
rd = lambda f: list(csv.DictReader(open(os.path.join(a.dir, f)))) if os.path.exists(os.path.join(a.dir, f)) else []
lots, buys, losses, plan = rd('lots.csv'), rd('buys.csv'), rd('losses_taken.csv'), rd('plan.csv')
px = {r['ticker']: float(r['price']) for r in csv.DictReader(open(a.prices)) if r.get('price')}
fam = {}
for grp in filter(None, a.twins.split(',')):
    names = grp.split('=')
    for n in names: fam[n] = set(names)
F = lambda t: fam.get(t, {t})
day = dt.timedelta(days=1)
recent = [b for b in buys if today - 30 * day <= D(b['date']) <= today]
upcoming = [p for p in plan if today < D(p['date']) <= today + 30 * day]

print(f"HARVEST CHECK {today} · min loss ${a.min_loss:,.0f} · tax value ≈ {a.rate:.0%} of the loss")
rows = []
for tk in sorted({l['ticker'] for l in lots}):
    if tk not in px: continue
    sell = [l for l in lots if l['ticker'] == tk and px[tk] < float(l['cost'])]
    loss = sum(float(l['shares']) * (px[tk] - float(l['cost'])) for l in sell)
    if not sell or -loss < a.min_loss / 2: continue
    sold = {(l['account'], l['date']) for l in sell}
    block = [b for b in recent if b['ticker'] in F(tk) and (b['account'], b['date']) not in sold]
    fut = [p['date'] for p in upcoming if any(t in p['what'] for t in F(tk))]
    clean = max(D(b['date']) for b in block) + 31 * day if block else today
    status = f"BLOCKED by planned buy {', '.join(fut)}" if fut else (f"WAIT until {clean}" if clean > today else "CLEAN NOW")
    size = 'HARVEST' if -loss >= a.min_loss else 'NEAR'
    drip = [b['account'] for b in buys if b['ticker'] == tk and b.get('drip', '').lower() in ('yes', 'true', '1')]
    rows.append(loss)
    print(f"  {size:7} {tk:6} loss ${-loss:,.0f} ≈ ${-loss * a.rate:,.0f} tax · {status}"
          + (f" · recent buys: {', '.join(b['account'] + ' ' + b['date'] for b in block)}" if block else '')
          + (f" · sell all {len(sell)} lots the same day" if len(sell) > 1 else '')
          + (f" · turn off dividend reinvest ({', '.join(set(drip))})" if drip else '')
          + f" · if sold, next buy in ANY account from {max(today, clean) + 31 * day}")
if not rows: print("  nothing worth harvesting today")
for x in losses:
    until = D(x['date']) + 31 * day
    if until > today:
        hits = [p['date'] for p in plan if today <= D(p['date']) < until and any(t in p['what'] for t in F(x['ticker']))]
        print(f"  WASH GUARD {x['ticker']}: loss taken {x['date']} -> no buy in ANY account before {until}"
              + (f" · CONFLICT with planned buy {', '.join(hits)}" if hits else ''))
print("Research only. Not tax advice.")
