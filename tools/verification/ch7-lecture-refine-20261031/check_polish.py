#!/usr/bin/env python3
"""比對潤稿前後未變動的受保護片段：含數學、數字、網址或程式的非中文連續片段。用法：check_polish.py before.py after.py"""
import re,sys,collections as C
def toks(p):
    s=open(p,encoding='utf8').read()
    run=re.split(r'[　-〿一-鿿＀-￯]+',s)
    return C.Counter(x.strip() for x in run if re.search(r'[\\$0-9]|https?:|<code>|w08',x))
a,b=toks(sys.argv[1]),toks(sys.argv[2])
print('少了',dict(a-b));print('多了',dict(b-a))
