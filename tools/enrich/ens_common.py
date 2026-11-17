"""集成各節（ensemble_deepen）共用的小工具。

`old` 一律是上游各層（enrich_trees 本體 → … → scope_trim）跑完後的 BODIES 快照；
這裡的函式只從裡面「取出」可重用的元件與段落，不修改它。
"""
import re

from lib import card, detail, info, info_card, lab_code, lab_output, proof, qa, quiz, rows_card, svg, table, viz  # noqa: F401

LAB = "Ch08-baggboost-lab-zh.ipynb"


def _div_block(s, start):
    """從 s[start] 的 <div ...> 開始，回傳對應 </div> 的結尾位置。"""
    depth = 0
    for t in re.finditer(r"<div\b|</div>", s[start:]):
        depth += -1 if t.group().startswith("</") else 1
        if depth == 0:
            return start + t.end()
    raise ValueError("div 沒有結束")


def grab_viz(body, inner_id):
    """回傳含有 id=inner_id 的整個 <div class="viz-layout" …>…</div>。"""
    k = body.find(f'id="{inner_id}"')
    if k < 0:
        raise ValueError("找不到元件：" + inner_id)
    a = body.rfind('<div class="viz-layout"', 0, k)
    if a < 0:
        raise ValueError("元件不在 viz-layout 裡：" + inner_id)
    z = _div_block(body, a)
    if z < k:
        raise ValueError("viz-layout 範圍不含 " + inner_id)
    return body[a:z]


def grab_details(body, pid):
    """回傳 id=pid 的整個 <details>…</details>（含巢狀）。"""
    m = re.search(r'<details\b[^>]*\bid="' + re.escape(pid) + r'"[^>]*>', body)
    if not m:
        raise ValueError("找不到收合：" + pid)
    depth = 0
    for t in re.finditer(r"<details\b|</details>", body[m.start():]):
        depth += -1 if t.group().startswith("</") else 1
        if depth == 0:
            return body[m.start():m.start() + t.end()]
    raise ValueError("收合沒有結束：" + pid)


def chunk(cell, start=None, end=None):
    s = lab_code(8, cell)
    if start is not None:
        s = s[s.index(start):]
    if end is not None:
        s = s[:s.index(end)]
    return s.rstrip()


def lab(label, cell, out=None, start=None, end=None, note=None):
    """一張 lab 程式卡：程式逐字取自儲存格 cell（可截 start…end），輸出逐字取自儲存格 out。"""
    return card(label, chunk(cell, start, end), lab_output(8, out) if out else None,
                note=note, src=f"<code>{LAB}</code> · 儲存格 {cell}")


def links(items):
    """「本主題的講義來源與延伸閱讀」：items = [(url, 中文標籤), ...]。"""
    a = "、".join(f'<a href="{u}" target="_blank" rel="noopener">{t}</a>' for u, t in items)
    return f'<p class="source-links">本主題的講義來源與延伸閱讀：{a}。</p>'


def slider(sid, label, lo, hi, step, val, valtext, oninput, basis="230px"):
    return (f'<span class="slider-row" style="margin-bottom:0;flex:1 1 {basis};min-width:0;">'
            f'<span class="slider-label">{label}</span>'
            f'<input type="range" id="{sid}" min="{lo}" max="{hi}" step="{step}" value="{val}" '
            f'oninput="{oninput}" aria-label="{label}">'
            f'<span class="slider-val" id="{sid}Val">{valtext}</span></span>')


def btn(kind, label, onclick, bid=None):
    """kind ∈ play／step／reset／toggle。"""
    i = f' id="{bid}"' if bid else ""
    return f'<button class="btn btn-{kind}"{i} onclick="{onclick}">{label}</button>'


def select(sid, label, options, onchange):
    """options = [(value, 顯示文字), ...]，第一個是預設。"""
    o = "".join(f'<option value="{v}">{t}</option>' for v, t in options)
    return (f'<span class="slider-row" style="margin-bottom:0;flex:1 1 200px;min-width:0;">'
            f'<span class="slider-label">{label}</span>'
            f'<select id="{sid}" onchange="{onchange}" aria-label="{label}">{o}</select></span>')
