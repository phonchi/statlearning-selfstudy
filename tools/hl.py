#!/usr/bin/env python3
"""把 Python 原始碼變成本站的 .pseudo-code 標記，並組出 .deck-extra 卡。

為什麼要有這支：頁面上的程式碼是手寫 token span（沒有 Prism、沒有 highlight.js，
單檔自足），手工上色又慢又會錯。這支用 pygments 產生，十頁共用同一套配色。

當函式庫用：
    from hl import hl, card
    print(card("講義 05 · LOOCV", CODE, OUT, src="Ch05-resample-lab-zh.ipynb · 儲存格 32"))

當 CLI 用：
    python3 tools/hl.py --id w05code --fontsize .78rem < snippet.py
"""
import html
import sys

from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Comment, Keyword, Name, Number, Operator, String

# token → base.css 的 class（.kw 粉、.fn 綠、.num 紫、.com 灰藍斜體、.str 黃）
CLS = [
    (Comment, "com"),
    (String, "str"),
    (Number, "num"),
    (Keyword.Constant, "num"),      # True / False / None 跟數字同色
    (Operator.Word, "kw"),          # and / or / not / in / is
    (Keyword, "kw"),
    (Name.Builtin.Pseudo, "kw"),    # self
    (Name.Decorator, "fn"),
    (Name.Function, "fn"),
    (Name.Class, "fn"),
]


def _cls(tok):
    for t, c in CLS:
        if tok in t:
            return c
    return None


def hl(code, block_id=None, fontsize=None, lines_with_data_l=None):
    """回傳 <div class="pseudo-code">…</div>。

    lines_with_data_l：要讓 JS 高亮的行號集合（1-based）。只有這些行帶 data-l，
    其餘不帶——data-l 是契約不是裝飾，validate.py 會檢查它對得上 hlLine()。
    """
    want = set(lines_with_data_l or ())
    # 先切成 [(class, 文字)] 的每行清單，再把相鄰同 class 的片段併起來，
    # 否則一個字串常值會被 pygments 切成三段 span，標記很雜。
    rows_raw, cur = [], []
    for tok, text in lex(code.rstrip("\n"), PythonLexer()):
        c = _cls(tok)
        for i, part in enumerate(text.split("\n")):
            if i:
                rows_raw.append(cur)
                cur = []
            if part:
                cur.append((c if part.strip() else None, part))
    rows_raw.append(cur)

    out_lines = []
    for row in rows_raw:
        merged = []
        for c, part in row:
            if merged and merged[-1][0] == c:
                merged[-1][1] += part
            else:
                merged.append([c, part])
        out_lines.append("".join(
            f'<span class="{c}">{html.escape(t, quote=True)}</span>' if c
            else html.escape(t, quote=True) for c, t in merged))
    while out_lines and not out_lines[-1].strip():
        out_lines.pop()

    rows = []
    for n, body in enumerate(out_lines, start=1):
        attr = f' data-l="{n}"' if n in want else ""
        rows.append(f'<span class="line"{attr}>{body or " "}</span>')

    attrs = ""
    if block_id:
        attrs += f' id="{block_id}"'
    if fontsize:
        attrs += f' style="font-size:{fontsize};"'
    return f'<div class="pseudo-code"{attrs}>\n' + "\n".join(rows) + "</div>"


def card(label, code, output=None, src=None, note=None, fontsize=".78rem",
         out_tag="預期輸出"):
    """組出「講義／lab 完整實作 + 預期輸出」卡。

    src 是 .dx-src 的出處字串，validate.py 會要求每張 .deck-extra 都有。
    output 必須是逐字從 lab 抄來的實跑結果，不要自己編。
    """
    parts = [f'<div class="deck-extra">',
             f'  <div class="dx-label">{label}</div>',
             "  " + hl(code, fontsize=fontsize).replace("\n", "\n  ")]
    if output is not None:
        parts.append(f'  <div class="expected-out"><span class="eo-tag">{out_tag}</span>'
                     f'<pre>{html.escape(output.rstrip())}</pre></div>')
    if note:
        parts.append(f'  <p class="dx-note">{note}</p>')
    if src:
        parts.append(f'  <span class="dx-src">來源：{src}</span>')
    parts.append("</div>")
    return "\n".join(parts)


if __name__ == "__main__":
    argv = sys.argv[1:]
    bid = argv[argv.index("--id") + 1] if "--id" in argv else None
    fs = argv[argv.index("--fontsize") + 1] if "--fontsize" in argv else None
    dl = argv[argv.index("--data-l") + 1] if "--data-l" in argv else ""
    want = [int(x) for x in dl.split(",") if x.strip()]
    print(hl(sys.stdin.read(), block_id=bid, fontsize=fs, lines_with_data_l=want))
