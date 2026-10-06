// Mission Control helpers for the tracker Google Sheet.
// Install: open your tracker in Google Sheets -> Extensions -> Apps Script -> paste this file -> Save.
// Then reload the sheet: a "Mission Control" menu appears. Run "Set up charts" once.
// Bound to the sheet it lives in (no IDs, no tokens, no web app). Nothing here places trades.

function onOpen() {
  SpreadsheetApp.getUi().createMenu('Mission Control')
    .addItem('Set up charts + tab order', 'mcSetup')
    .addItem('Apply inbox (_inbox!A1 JSON)', 'mcInbox')
    .addItem('Add today to History', 'mcHistoryToday')
    .addToUi();
}

function mcSetup() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const d = ss.getSheetByName('Dashboard');
  const h = ss.getSheetByName('History');
  const last = d.getRange('N17:N40').getValues().filter(function (r) { return r[0] !== ''; }).length + 16;
  d.getCharts().forEach(function (c) { d.removeChart(c); });
  const opt = function (b, title) {
    return b.setOption('title', title).setOption('width', 560).setOption('height', 300)
      .setOption('legend', { position: 'right' }).setOption('backgroundColor', '#ffffff');
  };
  const top = last + 14;
  d.insertChart(opt(d.newChart().setChartType(Charts.ChartType.PIE).addRange(d.getRange('N16:O' + last))
    .setNumHeaders(1).setOption('pieHole', 0.5).setPosition(top, 1, 0, 0), 'Household mix now').build());
  d.insertChart(opt(d.newChart().setChartType(Charts.ChartType.BAR).addRange(d.getRange('N16:P' + last))
    .setNumHeaders(1).setPosition(top, 8, 0, 0), 'Now vs target ($)').build());
  d.insertChart(opt(d.newChart().setChartType(Charts.ChartType.COLUMN).addRange(d.getRange('N16:N' + last))
    .addRange(d.getRange('Q16:R' + last)).setNumHeaders(1).setOption('isStacked', true)
    .setPosition(top + 17, 1, 0, 0), 'Taxable vs retirement by sleeve ($)').build());
  d.insertChart(opt(d.newChart().setChartType(Charts.ChartType.LINE).addRange(h.getRange('A3:A400'))
    .addRange(h.getRange('D3:E400')).setNumHeaders(1).setPosition(top + 17, 8, 0, 0),
    'You vs benchmark (start = 100)').build());
  ['Dashboard', 'Holdings', 'Value Sleeve', 'Watchlist', 'Daily Log', 'History', 'Control Center']
    .forEach(function (n, i) { const s = ss.getSheetByName(n); if (s) { ss.setActiveSheet(s); ss.moveActiveSheet(i + 1); } });
  ss.setActiveSheet(d);
}

// Your agent (e.g. Claude in Chrome) pastes one JSON object into _inbox!A1, then runs mcInbox:
// {"daily":{"date":"2026-10-05","scan":"AM","headline":"...","ideas":"...","zones":"...","rebalance":"...","risks":"..."},
//  "history":{"date":"2026-10-05","bench":123.45,"note":"..."},
//  "watchnotes":{"NVDA":"note"}}
function mcInbox() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let ib = ss.getSheetByName('_inbox');
  if (!ib) { ib = ss.insertSheet('_inbox'); ib.hideSheet(); return 'created _inbox; paste JSON into A1'; }
  const raw = ib.getRange('A1').getValue();
  if (!raw) return 'inbox empty';
  const res = mcWrite(JSON.parse(raw));
  ib.getRange('A1').clearContent();
  ib.getRange('A2').setValue(new Date() + ' ' + res);
  return res;
}

function mcWrite(p) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const out = [];
  if (p.daily) {
    const s = ss.getSheetByName('Daily Log'), x = p.daily;
    s.insertRowBefore(5);
    s.getRange(5, 1, 1, 7).setValues([[new Date(x.date + 'T12:00:00'), x.scan, x.headline, x.ideas, x.zones, x.rebalance, x.risks]])
      .setWrap(true).setVerticalAlignment('top').setFontSize(9).setBackground(null).setFontWeight('normal');
    s.getRange(5, 1).setNumberFormat('yyyy-mm-dd').setFontSize(10);
    s.getRange(5, 3).setFontWeight('bold');
    s.setRowHeight(5, 80);
    out.push('daily');
  }
  if (p.history) { out.push(mcHistory(p.history.date, p.history.bench, p.history.note)); }
  if (p.watchnotes) {
    const w = ss.getSheetByName('Watchlist');
    const t = w.getRange('A5:A400').getValues();
    w.getRange(5, 12, t.length, 1).setValues(t.map(function (r) { return [p.watchnotes[r[0]] || '']; }));
    out.push('watchnotes');
  }
  return 'ok: ' + out.join(', ');
}

// Appends (or overwrites same-day) a History row using the live Dashboard total.
function mcHistory(date, bench, note) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const h = ss.getSheetByName('History'), d = ss.getSheetByName('Dashboard');
  const col = h.getRange('A4:A400').getValues();
  let r = 4; while (r - 4 < col.length && col[r - 4][0] !== '') r++;
  const dt = date ? new Date(date + 'T12:00:00') : new Date();
  if (r > 4 && col[r - 5][0] instanceof Date && col[r - 5][0].toDateString() === dt.toDateString()) r--;
  h.getRange(r, 1, 1, 3).setValues([[dt, d.getRange('A5').getValue(), bench || '']]);
  h.getRange(r, 6).setValue(note || '');
  return 'history row ' + r;
}

function mcHistoryToday() {
  const spy = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Watchlist');
  let bench = '';
  const t = spy.getRange('A5:D400').getValues();
  for (let i = 0; i < t.length; i++) if (t[i][0] === 'SPY') { bench = t[i][3]; break; }
  return mcHistory(null, bench, 'manual');
}
