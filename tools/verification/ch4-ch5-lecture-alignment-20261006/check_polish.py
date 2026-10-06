#!/usr/bin/env python3
"""Polishing guard: math, numbers, URLs, ids and code must be identical before/after prose polishing.
usage: check_polish.py <before.py> <after.py>"""
import re, sys
from collections import Counter
a, b = (open(f).read() for f in sys.argv[1:3])
pats = {
    'display math': r'\$\$.*?\$\$',
    'inline math': r'(?<!\$)\$(?!\$)[^$\n]+?\$(?!\$)',
    'urls': r'https?://[^\s"\'<>)]+',
    'ids': r'id="[^"]+"|detail\("[^"]+"|proof\(\'[^\']+\'',
    'code': r'<code>.*?</code>',
    'numbers': r'(?<![\w.])\d+(?:\.\d+)?%?',
    'quiz truth': r'\((True|False),',
}
bad = 0
for name, pat in pats.items():
    ca, cb = Counter(re.findall(pat, a, re.S)), Counter(re.findall(pat, b, re.S))
    if ca != cb:
        bad += 1
        print(f'DIFF {name}: removed {list((ca - cb).elements())[:6]} added {list((cb - ca).elements())[:6]}')
    else:
        print(f'same {name}: {sum(ca.values())}')
sys.exit(1 if bad else 0)
