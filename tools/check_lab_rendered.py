"""Independently compare full rendered code/output cards to current cited labs."""
import html
import re
from pathlib import Path
from bs4 import BeautifulSoup
from paths import ROOT, SRC_INDEX


def cells(ch):
    text = (SRC_INDEX / f'lab_ch{ch}.md').read_text()
    out = {}
    for m in re.finditer(r'^## 儲存格 (\d+) \[code\]\n(.*?)(?=^## 儲存格 |\Z)', text, re.S | re.M):
        code = re.search(r'```python\n(.*?)\n```', m[2], re.S)
        value = re.search(r'\*\*輸出\*\*\n\n```\n(.*?)\n```', m[2], re.S)
        out[int(m[1])] = (code[1] if code else '', value[1] if value else None)
    return out

failures = []
count = 0
cache = {}
for path in sorted(ROOT.glob('*.html')):
    soup = BeautifulSoup(path.read_text(), 'html.parser', preserve_whitespace_tags={'pre', 'textarea', 'span', 'div'})
    for card in soup.select('.deck-extra'):
        count += 1
        label = card.select_one('.dx-label').get_text()
        src = card.select_one('.dx-src')
        if not src or not src.get('data-lab-cells'):
            failures.append(f'{path.name}: {label}: missing internal provenance')
            continue
        ch = int(src['data-lab-ch'])
        if ch not in cache:
            cache[ch] = cells(ch)
        keys = [int(x) for x in src['data-lab-cells'].split(',')]
        if any(k not in cache[ch] for k in keys):
            failures.append(f'{path.name}: {label}: unknown code cell {keys}')
            continue
        rendered = '\n'.join(x.get_text().rstrip() for x in card.select('.pseudo-code .line')).strip()
        remainder = rendered
        for k in keys:
            code = '\n'.join(line.rstrip() for line in cache[ch][k][0].splitlines()).strip()
            if code and remainder.startswith(code):
                remainder = remainder[len(code):].strip()
        # A card may quote a contiguous excerpt rather than an entire cell.
        code_ok = not remainder or any(rendered in cache[ch][k][0] for k in keys)
        output = card.select_one('.expected-out pre')
        output_ok = True
        if output is not None:
            want = [cache[ch][k][1].rstrip() for k in keys if cache[ch][k][1] is not None]
            output_ok = output.get_text().rstrip() in want + ['\n'.join(want)]
        if not code_ok or not output_ok:
            failures.append(f'{path.name}: {label}: code={code_ok}, output={output_ok}')
        print(f'{path.name}: {label}: code={code_ok}, output={output_ok}')
print(f'Checked {count} full rendered lab cards; failures={len(failures)}')
if failures:
    raise SystemExit('\n'.join(failures))
