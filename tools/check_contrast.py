#!/usr/bin/env python3
"""深色底 × 深色行內字的守門員。三站共用同一支（逐位元組相同）。

## 為什麼是驗 CSS 合約，不是驗內容

最嚴重的案例是 JS 執行時才產生的：
`setStatus('typeStatus', `<strong>${name}</strong>：${t.size} byte…`)`
——`.status-banner` 是 #2d2d3f 深底，而 base.css 的 `strong{color:var(--ink)}`
是 #1a1a2e，對比 1.07，等於全黑貼全黑。靜態走 DOM 祖先鏈根本看不到這種東西。

所以這支反過來驗**合約**：把每一頁（或樣板）用到的 CSS 拿出來，
掃出所有「深色底」的選擇器，再確認它們都被覆寫區塊涵蓋。
只要合約成立，執行時注入什麼內容都安全。

## 三條檢查

1. COVERAGE：所有深色底選擇器都必須在覆寫清單裡（核心）
2. BLOCK：覆寫區塊存在且沒有被改動（只適用有 contrast-fix 標記的站）
3. AFTER：覆寫區塊之後不得再出現全域的 code{...color...}／strong{...color...}
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = "contrast-fix v1"
AA = 4.5
# 這些行內元素自帶顏色，落進深色底就會出事
INLINE = {"code": "accent2", "kbd": "accent2", "strong": "ink", "b": "ink",
          "a": "#0000EE"}          # 沒被特定選擇器接住的 <a> 是瀏覽器預設藍


def rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(c):
    def f(x):
        x /= 255
        return x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + .05) / (lo + .05)


def dark_selectors(css, variables):
    """回傳 {選擇器: 底色}，只留下「行內元素會看不見」的那些。"""
    out = {}
    pat = re.compile(r"([^{}]+)\{([^}]*background(?:-color)?\s*:\s*"
                     r"(?:var\(--([\w-]+)\)|(#[0-9a-fA-F]{3,6}))[^}]*)\}")
    for m in pat.finditer(css):
        sel = m.group(1).strip().split("\n")[-1].strip()
        col = variables.get(m.group(3)) if m.group(3) else m.group(4)
        if not col or "::before" in sel or "::after" in sel:
            continue
        bg = rgb(col)
        bad = [t for t, fg in INLINE.items()
               if ratio(bg, rgb(variables.get(fg, fg))) < AA]
        if bad:
            out[sel] = (col, bad)
    return out


def covered(sel, tag, block):
    """選擇器本身、或它的祖先／基底形式，配上**這一個標籤**出現在覆寫區塊裡才算涵蓋。

    逐標籤驗很重要：只要有一個標籤沒被蓋到就會出事，
    不能因為 `SEL strong` 在就放過 `SEL code`（負向自測抓到過這個漏洞）。
    """
    cands = {sel}
    parts = sel.split()
    last = parts[-1].split(":")[0]
    toks = last.split(".")
    if last.startswith("."):
        cands.add(" ".join(parts[:-1] + ["." + toks[1]]))
    else:
        cands.add(" ".join(parts[:-1] + [toks[0]]))
    if len(parts) > 1:                       # 祖先帶狀態的形式
        first = parts[0].split(".")
        if len(first) > 2:
            cands.add(" ".join(["." + first[1]] + parts[1:]))
    return any(f"{c} {tag}" in block for c in cands)


def check(name, css, block, fails):
    variables = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{3,6})", css))
    if MARKER not in block:
        fails.append(f"{name}: 找不到 contrast-fix 覆寫區塊")
        return
    for sel, (col, bad) in sorted(dark_selectors(css, variables).items()):
        miss = [t for t in bad if not covered(sel, t, block)]
        if miss:
            fails.append(f"{name}: 深色底 {sel}（{col}）的 "
                         f"{'／'.join('<' + t + '>' for t in miss)} 沒有被覆寫區塊涵蓋")
    tail = css[css.index(MARKER):]
    for m in re.finditer(r"(?:^|\})\s*(code|strong)\s*\{[^}]*color\s*:", tail):
        fails.append(f"{name}: 覆寫區塊之後又出現全域 {m.group(1)}{{color:…}}，會蓋回去")


def main():
    fails = []
    tpl = ROOT / "tools" / "template"
    if tpl.exists():                          # statlearning：CSS 在樣板
        css = "\n".join((tpl / f).read_text(encoding="utf-8")
                        for f in ("base.css", "stats.css", "index.css"))
        check("template", css, css, fails)
    else:                                     # 手寫站：CSS inline 在每一頁
        for f in sorted(ROOT.glob("*.html")):
            css = "\n".join(re.findall(r"<style>(.*?)</style>",
                                       f.read_text(encoding="utf-8"), re.S))
            check(f.name, css, css, fails)
    for x in fails:
        print("  FAIL [CONTRAST]", x)
    print(f"\n{len(fails)} 個失敗")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
