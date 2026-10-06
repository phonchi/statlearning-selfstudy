#!/usr/bin/env python3
"""Screenshot new/changed elements at 1440/390 px; fail on MathJax errors, page errors, overflow.

usage: shots.py <stem> <id>[:action] ...   <id or @css>[|action]; action: open (details) or a js expression run before shot
"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / 'shots'; OUT.mkdir(exist_ok=True)
stem, targets = sys.argv[1], sys.argv[2:]
report, bad = [], []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox'])
    for width in (1440, 390):
        pg = b.new_page(viewport={'width': width, 'height': 1000})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto((ROOT / f'{stem}.html').as_uri(), wait_until='networkidle', timeout=90000)
        pg.evaluate('async()=>{await MathJax.startup.promise;await document.fonts.ready;}')
        for t in targets:
            tid, _, act = t.partition('|')
            el = pg.locator(tid[1:]).first if tid.startswith('@') else pg.locator('#' + tid)
            fname = tid.strip('@').replace('#', '').replace(' ', '_').replace(':', '').replace('(', '').replace(')', '').replace('.', '')[:60]
            if el.count() == 0:
                bad.append(f'{width} missing #{tid}'); continue
            if act == 'open':
                if el.evaluate('e=>e.tagName') == 'DETAILS' and el.get_attribute('open') is None:
                    el.locator('summary').first.click()
            elif act:
                pg.evaluate(act)
            pg.evaluate('async()=>{await MathJax.startup.promise; if (window.MathJax && MathJax.typesetPromise) await MathJax.typesetPromise();}')
            pg.wait_for_timeout(300)
            if el.locator('mjx-merror').count():
                bad.append(f'{width} #{tid} has mjx-merror')
            el.scroll_into_view_if_needed()
            el.screenshot(path=str(OUT / f'{stem}-{fname}-{width}.png'))
            report.append({'width': width, 'id': tid, 'formulas': el.locator('mjx-container').count()})
        if pg.locator('mjx-merror').count():
            bad.append(f'{width} page has {pg.locator("mjx-merror").count()} mjx-merror')
        if not pg.evaluate('document.documentElement.scrollWidth <= innerWidth+1'):
            bad.append(f'{width} horizontal page overflow')
        bad += [f'{width} pageerror {e}' for e in errs]
        pg.close()
    b.close()
(OUT / f'{stem}-report.json').write_text(json.dumps({'report': report, 'problems': bad}, ensure_ascii=False, indent=1))
print('\n'.join(bad) if bad else f'PASS {stem}: {len(report)} shots, no MathJax error, no page error, no overflow')
sys.exit(1 if bad else 0)
