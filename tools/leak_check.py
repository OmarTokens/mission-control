"""Leak check: scan a folder before you publish it.

Your private terms live in a file OUTSIDE the repo (never commit it):
    python3 tools/leak_check.py --root . --terms ~/private/leak_terms.txt [--numbers ~/private/numbers.txt]

leak_terms.txt : one term per line (names, emails, account nicknames, sheet IDs, tokens). Case-insensitive.
                 Lines starting with "allow:" are exact strings that may appear (e.g. "allow:YourGitHubName").
numbers.txt    : one number per line (balances, share counts, cost bases). Each is searched in several formats
                 (1234567.89 / 1,234,567.89 / 1,234,568 / $1,234.6K / 1.23M).
Also flags, with no terms file: email addresses, long Google-style IDs, API-key-looking strings, account-number
patterns ("···" or "ending in" followed by 4 digits).
Scans text files, and the XML inside .xlsx/.docx/.pptx, plus raw bytes of images (metadata). Exit code 1 if anything is found.
"""
import argparse, os, re, sys, zipfile

ap = argparse.ArgumentParser()
ap.add_argument('--root', default='.'); ap.add_argument('--terms'); ap.add_argument('--numbers')
a = ap.parse_args()

terms, allow, nums = [], [], []
if a.terms:
    for ln in open(a.terms, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln.strip() or ln.startswith('#'): continue
        (allow.append(ln[6:]) if ln.startswith('allow:') else terms.append(ln.strip()))
if a.numbers:
    nums = [float(x) for x in (l.strip().replace(',', '').replace('$', '') for l in open(a.numbers)) if x and not x.startswith('#')]

def num_forms(v):
    f = set()
    if v != int(v):
        f |= {f"{v:.2f}", f"{v:,.2f}"}
    f |= {f"{round(v):,}", f"{v/1000:,.1f}K"}
    if round(v) >= 10000: f.add(str(round(v)))
    if v >= 1e6: f.add(f"{v/1e6:.2f}M")
    return {x for x in f if len(x.replace(',', '').replace('.', '')) >= 4}

PATTERNS = {
    'email address': re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'),
    'long Google-style ID': re.compile(r'\b[A-Za-z0-9_-]{40,}\b'),
    'API key / token': re.compile(r'(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|trig_[A-Za-z0-9]{10,})'),
    'account number pattern': re.compile(r'(···|\.\.\.|x|ending in |acct ?#? ?)\d{4}\b', re.I),
}
SAFE_EMAILS = {'you@example.com', 'noreply@anthropic.com'}
TEXT_EXT = {'.md', '.py', '.gs', '.js', '.html', '.css', '.csv', '.json', '.txt', '.svg', '.yml', '.yaml', '.toml', '.gitignore', ''}

def chunks(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.xlsx', '.docx', '.pptx'):
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                yield f"{path}!{n}", z.read(n).decode('utf-8', 'ignore')
    elif ext in TEXT_EXT or os.path.basename(path).startswith('.'):
        yield path, open(path, encoding='utf-8', errors='ignore').read()
    else:
        yield path, open(path, 'rb').read().decode('latin-1')

hits = []
files = 0
for dp, dn, fn in os.walk(a.root):
    dn[:] = [d for d in dn if d not in ('.git', 'out', 'my_data', '__pycache__', 'node_modules')]
    for f in fn:
        files += 1
        for where, txt in chunks(os.path.join(dp, f)):
            clean = txt
            for s in allow: clean = clean.replace(s, '')
            low = clean.lower()
            for t in terms:
                if t.lower() in low: hits.append((where, 'private term', t))
            for v in nums:
                for form in num_forms(v):
                    for m in re.finditer(re.escape(form), clean):
                        before = clean[m.start()-1:m.start()] if m.start() else ''
                        after = clean[m.end():m.end()+1]
                        if not (before.isdigit() or after.isdigit()):
                            hits.append((where, 'private number', form)); break
            for name, rx in PATTERNS.items():
                for m in rx.finditer(clean):
                    s = m.group(0)
                    if name == 'email address' and s.lower() in SAFE_EMAILS: continue
                    if name == 'long Google-style ID' and (s.startswith('data:') or re.fullmatch(r'[A-Za-z]+', s) or 'base64' in clean[max(0, m.start()-40):m.start()]): continue
                    hits.append((where, name, s[:60]))

seen = set()
for h in hits:
    if h in seen: continue
    seen.add(h); print(f"LEAK? {h[1]:<24} {h[2]!r:<40} in {h[0]}")
print(f"\nScanned {files} files with {len(terms)} private terms and {len(nums)} private numbers: "
      + ("PASS - nothing found" if not seen else f"FAIL - {len(seen)} finding(s) to review"))
sys.exit(1 if seen else 0)
