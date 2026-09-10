#!/usr/bin/env python3
"""各章 enrich 腳本的共用工具。冪等。

每章一支 tools/enrich/enrich_<page>.py，內容都是純字串，跑完把 section 內文與
本頁元件 JS 換掉。GEN 區段（head / nav / TOC / 標題列 / chapter-nav / footer /
shared.js）由 build_page.py 管，enrich 不碰。

為什麼用腳本而不是直接改 HTML：內容要重跑、要 diff、程式碼區塊要用 hl() 上色，
而且十章由不同人（或不同 agent）寫時，同一支 lib 保證組裝方式一致。
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from hl import card, hl  # noqa: E402,F401  （給各章 enrich 腳本 re-export）
from reader_sources import fragment, prose
from paths import ROOT, SRC_INDEX  # noqa: E402

GEN_END = "<!-- GEN:END sec:{sid} -->"


def splice_section(src: str, sid: str, body: str) -> str:
    """把 <!-- GEN:END sec:sid --> 到 </section> 之間換成 body。"""
    pat = re.compile(re.escape(GEN_END.format(sid=sid)) + r"(.*?)\n</section>", re.S)
    if not pat.search(src):
        raise SystemExit(f"找不到 section #{sid} 的插入點（先跑 tools/build_page.py）")
    return pat.sub(lambda _m: GEN_END.format(sid=sid) + "\n" + body.rstrip() + "\n</section>",
                   src, count=1)


def splice_pagejs(src: str, js: str) -> str:
    pat = re.compile(r"<!-- PAGEJS:BEGIN -->.*?<!-- PAGEJS:END -->", re.S)
    if not pat.search(src):
        raise SystemExit("找不到 PAGEJS 區段")
    return pat.sub(lambda _m: "<!-- PAGEJS:BEGIN -->\n<script>\n" + js.strip()
                   + "\n</script>\n<!-- PAGEJS:END -->", src, count=1)


def apply(stem: str, bodies: dict, pagejs: str, frames: str = ""):
    """把 bodies / pagejs 寫進 <stem>.html，回報改了哪些節。"""
    dest = ROOT / f"{stem}.html"
    src = dest.read_text(encoding="utf-8")
    before = src
    from pages import BY_STEM
    for sid, body in bodies.items():
        if sid == "exercises" and not BY_STEM[stem].show_exercises:
            continue
        src = splice_section(src, sid, fragment(body))
    pagejs = prose(pagejs)
    src = splice_pagejs(src, (frames + "\n\n" + pagejs) if frames else pagejs)
    if src != before:
        dest.write_text(src, encoding="utf-8")
    kb = dest.stat().st_size / 1024
    print(f"  {stem}.html  {len(bodies)} 節寫入  {kb:.0f} KB"
          + ("  （無變化）" if src == before else ""))


def lab_output(ch: int, cell: int) -> str:
    """從 data/source_index/lab_chN.md 逐字取出某個儲存格的輸出。

    絕不重跑：本機環境跟課程環境不同，而 notebook 裡已經是老師本人跑的結果。
    """
    text = (SRC_INDEX / f"lab_ch{ch}.md").read_text(encoding="utf-8")
    m = re.search(rf"^## 儲存格 {cell} \[code\]\n(.*?)(?=^## 儲存格 |\Z)", text, re.S | re.M)
    if not m:
        raise SystemExit(f"lab_ch{ch}.md 沒有儲存格 {cell}")
    o = re.search(r"\*\*輸出\*\*\n\n```\n(.*?)\n```", m.group(1), re.S)
    if not o:
        raise SystemExit(f"lab_ch{ch}.md 儲存格 {cell} 沒有存下輸出")
    return o.group(1)


def lab_code(ch: int, cell: int) -> str:
    text = (SRC_INDEX / f"lab_ch{ch}.md").read_text(encoding="utf-8")
    m = re.search(rf"^## 儲存格 {cell} \[code\]\n\n```python\n(.*?)\n```", text, re.S | re.M)
    if not m:
        raise SystemExit(f"lab_ch{ch}.md 沒有儲存格 {cell} 的程式碼")
    return m.group(1)


# ── 小組件 ──────────────────────────────────────────────────────────────
def info(label, body, kind=""):
    k = f" {kind}" if kind else ""
    return f'<div class="info-box{k}">\n  <span class="info-label">{label}</span>\n  {body}\n</div>'


def qa(head, items):
    """觀念釐清 Q&A。items = [(問題, 答案 HTML), ...]"""
    out = [f'<div class="qa-box">', f'  <div class="qa-head">{head}</div>']
    for q, a in items:
        out.append(f'  <details class="qa-item"><summary>{q}</summary>\n'
                   f'    <div class="qa-a">{a}</div>\n  </details>')
    out.append("</div>")
    return "\n".join(out)


def proof(pid, title, body):
    """完整證明預設收合；結果與條件由正文先交代。"""
    return (f'<details class="qa-item proof" id="{pid}"><summary>證明：{title}</summary>\n'
            f'<div class="qa-a">{body}</div></details>')


def detail(pid, title, body):
    """完整教學細節預設收合；正文保留概念、必要公式與短例。"""
    return (f'<details class="qa-item reading-detail" id="{pid}"><summary>{title}</summary>\n'
            f'<div class="detail-body">{body}</div></details>')


def quiz(qid, label, question, options):
    """三選一 quiz。options = [(是否正解, 選項 HTML, 為什麼), ...]，錯的也要寫為什麼。"""
    letters = "ABC"
    opts = []
    for i, (ok, text, why) in enumerate(options):
        why = why.replace("&", "&amp;").replace('"', "&quot;")
        opts.append(f'<div class="quiz-opt" data-correct="{str(ok).lower()}" data-fb="{why}" '
                    f'onclick="quizCheck(\'{qid}\', this)">'
                    f'<span class="opt-letter">({letters[i]})</span> {text}</div>')
    return (f'<div class="quiz-box">\n  <div class="quiz-label">{label}</div>\n'
            f'  <p>{question}</p>\n'
            f'  <div class="quiz-options" id="{qid}Options">{"".join(opts)}</div>\n'
            f'  <div class="quiz-feedback" id="{qid}Feedback"></div>\n</div>')


def table(headers, rows, cls="cmp-table", fontsize=".85rem"):
    keep = [i for i, h in enumerate(headers) if h.strip() not in {"儲存格", "lab 儲存格", "Lab cell"}]
    headers = [headers[i] for i in keep]
    rows = [[row[i] for i in keep] for row in rows]
    th = "".join(f"<th>{h}</th>" for h in headers)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return (f'<div style="overflow-x:auto;"><table class="{cls}" '
            f'style="width:100%;font-size:{fontsize};">\n'
            f"  <thead><tr>{th}</tr></thead>\n  <tbody>{tr}</tbody>\n</table></div>")


PROVENANCE_LABELS = {
    "course-data": "課程／lab 資料",
    "book-redraw": "講義／課本重繪",
    "simulation": "模擬示意",
    "illustrative": "概念示意",
}


def viz(stage, side_cards, status_id, status_text, controls, provenance):
    """.viz-layout：stage → status → controls → provenance ＋右側說明。

    provenance = (kind, detail)，kind 必須是 PROVENANCE_LABELS 的鍵。
    """
    cards = "\n".join(side_cards)
    kind, detail = provenance
    if kind not in PROVENANCE_LABELS:
        raise ValueError(f"未知的視覺 provenance：{kind}")
    attr = f' data-provenance="{kind}"'
    from html import escape
    attr += f' data-source-note="{escape(detail, quote=True)}"'
    source = f'\n      <div class="viz-source"><span>{PROVENANCE_LABELS[kind]}</span></div>'
    return f"""<div class="viz-layout"{attr}>
  <div>
    <div class="viz-panel">
{stage}
      <div class="status-banner" id="{status_id}"><span class="status-icon">›</span><span class="status-text">{status_text}</span></div>
      <div class="controls-bar">{controls}</div>{source}
    </div>
  </div>
  <div class="side-panel">
{cards}
  </div>
</div>"""


def info_card(title, body, badge=""):
    if badge.strip().upper() in {"LIVE", "BAKED", "LIVE + BAKED", "BAKED + LIVE", "CODE", "DATA", "LAB", "SIMULATION", "REPLAY"}:
        badge = ""
    b = f' <span class="ic-badge">{badge}</span>' if badge else ""
    return (f'    <div class="info-card">\n      <div class="ic-title">{title}{b}</div>\n'
            f'      {body}\n    </div>')


def rows_card(title, rows, badge=""):
    body = "".join(f'<div class="ic-row"><span class="ic-label">{k}</span>'
                   f'<span class="ic-value" id="{i}">{v}</span></div>'
                   for k, v, i in rows)
    return info_card(title, body, badge)


def chart(cid, klass="", fallback=""):
    k = f" {klass}" if klass else ""
    return (f'      <div class="chart-wrap{k}"><canvas id="{cid}"></canvas>\n'
            f'        <div class="chart-fallback"><div><b>圖表需要連網載入 Chart.js</b>{fallback}</div></div>\n'
            f'      </div>')


def svg(sid, height=340):
    return f'      <svg class="viz-svg" id="{sid}" height="{height}"></svg>'


def ver_note(labs=(), include_frames=True):
    """Compatibility entrypoint: production/version reports are not lesson content."""
    return ""


def hook(title, body):
    """「這在本站哪一章會用到」的掛鉤方框。

    用既有的 .info-box.purple，不新增任何 CSS——base.css 被整份塞進每頁的 head
    GEN 區段，動它一個 byte 就會讓十一章的 sha256 全部失效。
    """
    return info(f"🔗 {title}", body, "purple")
