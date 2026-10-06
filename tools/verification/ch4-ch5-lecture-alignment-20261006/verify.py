#!/usr/bin/env python3
"""Regression + coverage checks for the ch4/ch5 lecture alignment (2026-10-06).

1. Existing FRAMES_w04*/w05* bytes equal HEAD~ baseline, except the intended new/changed ones.
2. Every lab code/output text present at baseline is still present (possibly inside a longer card).
3. Every deck hyperlink is linked from the page (arXiv /pdf/ is accepted as /abs/).
4. New ids exist, are unique, and no <details> is open by default.
usage: verify.py <baseline-git-rev>
"""
import json, re, subprocess, sys
from pathlib import Path
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[3]; HERE = Path(__file__).resolve().parent
base = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
ALLOWED = {'classification': {'FRAMES_w04scen'}, 'resampling_methods': {'FRAMES_w05sim', 'FRAMES_w05misuse'}}
DECK = {'classification': '04_Classification.pdf', 'resampling_methods': '05_Resampling_Methods.pdf'}
links = json.loads((HERE / 'deck_links.json').read_text())
# Deck links confirmed dead (HTTP 404 on HEAD and GET, 2026-10-06); intentionally not linked.
DEAD = {'https://web.stanford.edu/class/stats191/notebooks/Logistic.html',
        'https://www.saattrupdan.com/2020-03-01-bootstrap-prediction'}
fails, notes = [], []
def frames(txt): return {m[1]: m[0] for m in re.finditer(r'^const (FRAMES_\w+) = .*;$', txt, re.M)}
for stem in DECK:
    new = (ROOT / f'{stem}.html').read_text()
    old = subprocess.run(['git', 'show', f'{base}:{stem}.html'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    fo, fn = frames(old), frames(new)
    for k, v in fo.items():
        if k in ALLOWED[stem]: notes.append(f'{stem}: {k} intentionally regenerated'); continue
        if fn.get(k) != v: fails.append(f'{stem}: {k} changed')
    for k in fn.keys() - fo.keys():
        (notes if k in ALLOWED[stem] else fails).append(f'{stem}: new {k}')
    so, sn = BeautifulSoup(old, 'html.parser'), BeautifulSoup(new, 'html.parser')
    newtexts = {e.get_text() for e in sn.select('.pseudo-code, .expected-out pre')}
    for e in so.select('.pseudo-code, .expected-out pre'):
        if not any(e.get_text().strip() in t for t in newtexts): fails.append(f'{stem}: lab text lost: {e.get_text()[:50]!r}')
    hrefs = {a.get('href') for a in sn.select('a[href]')}
    for page, url in links[DECK[stem]]:
        if url in DEAD: notes.append(f'{stem}: deck p.{page} dead link omitted {url}'); continue
        cand = {url, url.replace('/pdf/1906.02590.pdf', '/abs/1906.02590')}
        if not cand & hrefs: fails.append(f'{stem}: deck p.{page} link missing {url}')
    ids = [e['id'] for e in sn.select('[id]')]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup: fails.append(f'{stem}: duplicate ids {sorted(dup)[:5]}')
    if sn.select('details[open]'): fails.append(f'{stem}: details open by default')
    notes.append(f'{stem}: {len(sn.select("details"))} details, {len(re.findall(r"\$\$", new))//2} display formulas, '
                 f'{len(sn.select(".viz-layout"))} widgets, {len(sn.select(".deck-extra"))} lab cards')
for n in notes: print('NOTE', n)
for f in fails: print('FAIL', f)
print(f'{"PASS" if not fails else "FAIL"}: {len(fails)} failures')
sys.exit(1 if fails else 0)
