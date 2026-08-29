#!/usr/bin/env python3
"""由 tools/pages.py 與 data/ 產生 index.html 與 README.md 的章節表。冪等。

卡片上的「N 節互動」「N 張詞彙卡」都是算出來的，不是手打的，
所以不可能跟實際頁面或母檔不一致。
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_page as B  # noqa: E402
import pages as P  # noqa: E402
from paths import FLASHCARDS, QUESTIONS, ROOT, TEMPLATE  # noqa: E402


def counts(p: P.Page):
    parts = sum(1 for _, t, _ in P.tokens(p) if t.startswith("P"))
    cards = B.data_count("flashcards", p)
    qs = B.data_count("questions", p)
    html = ROOT / p.file
    widgets = 0
    if html.exists():
        s = html.read_text(encoding="utf-8")
        widgets = len(re.findall(r'class="chart-wrap', s)) + len(re.findall(r'<svg class="viz-svg"', s))
    return parts, cards, qs, widgets


def meta_line(p: P.Page):
    parts, cards, qs, widgets = counts(p)
    bits = [f"{parts} 節"]
    if widgets:
        bits.append(f"{widgets} 個互動元件")
    bits.append(f"題庫自測 {qs} 題" if qs else "每節 quiz")
    bits.append(f"{cards} 張詞彙卡" if cards else "詞彙卡待補")
    return " · ".join(bits)


def card(p: P.Page, seq: int):
    """seq 是**區內**序號（1 起算）。刻意不用 p.n —— 重排三區之後 n 與顯示順序脫鉤，
    印 n 會變成「12 · WHY CODE、01 · INTRODUCTION」這種讀不懂的東西。"""
    return (f'      <a class="ch-card" href="{p.file}">\n'
            f'        <span class="ch-num">{seq:02d} · {p.slug}</span>\n'
            f'        <h3>{p.plain}</h3>\n'
            f'        <span class="ch-badge">{p.islp_label}'
            f'{" ／ " + p.esl_label if p.esl_label else ""}</span>\n'
            f'        <div class="ch-meta">{meta_line(p)}</div>\n'
            f'      </a>')


def build_html():
    css = (TEMPLATE / "base.css").read_text(encoding="utf-8").rstrip() + "\n\n" \
        + (TEMPLATE / "stats.css").read_text(encoding="utf-8").rstrip() + "\n\n" \
        + (TEMPLATE / "index.css").read_text(encoding="utf-8").rstrip()
    watermark = ("from ISLP import load_data\n"
                 "from sklearn.model_selection import KFold\n\n"
                 "Auto = load_data('Auto')\n"
                 "cv   = KFold(10, shuffle=True,\n"
                 "             random_state=0)\n"
                 "# 交叉驗證估預測誤差\n"
                 "# bootstrap 估不確定性")
    # 三區，順序＝PAGES 字面值順序（check_index 比對的就是攤平後的整份順序）
    pre = [q for q in P.PAGES if q.grp == "pre"]
    core = [q for q in P.PAGES if q.grp == "core"]
    app = [q for q in P.PAGES if q.grp == "appendix"]
    cards = "\n".join(card(q, i) for i, q in enumerate(core, 1))
    total_cards = sum(B.data_count("flashcards", q) for q in core)
    total_widgets = sum(counts(q)[3] for q in core)

    pre_block = ""
    if pre:
        pre_cards = "\n".join(card(q, i) for i, q in enumerate(pre, 1))
        pre_widgets = sum(counts(q)[3] for q in pre)
        pre_block = f"""  <section id="pre">
    <h2>課前準備</h2>
    <p>三頁，讀完大概一小時。先建立<strong>AI 時代的資料分析學習迴圈</strong>、
    把環境弄好、再學會怎麼跟 AI 協作而不把判斷外包。
    這三頁不需要任何程式基礎，選讀，不列入評分。
    共 {len(pre)} 頁、{pre_widgets} 個互動元件。</p>
    <div class="ch-grid">
{pre_cards}
    </div>
  </section>

"""

    app_block = ""
    if app:
        app_cards = "\n".join(card(q, i) for i, q in enumerate(app, 1))
        app_widgets = sum(counts(q)[3] for q in app)
        app_block = f"""

  <section id="appendix">
    <h2>附錄 · Python 先備知識</h2>
    <p>沒寫過 Python，或只會一點點？這六頁把正課會用到的語法與套件講一遍，
    程式碼全部逐字取自課程 lab notebook。<strong>查閱用</strong>——
    正課讀到卡住再回來翻，不必先讀完。選讀，不列入評分。
    共 {len(app)} 頁、{app_widgets} 個互動元件。</p>
    <div class="ch-grid">
{app_cards}
    </div>
  </section>"""

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="統計學習與資料探勘（ISLP）互動自學網站：三頁課前準備、十一章互動教材、六頁 Python 先備知識附錄，每節都能動手操作、預測、驗證。NSYSU MATH524 課程配套。">
<title>統計學習 × Python 互動自學網站 — NSYSU MATH524</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700;900&family=Noto+Sans+TC:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
<div class="hero" id="top">
  <div class="hero-grid"></div>
  <div class="hero-code">{watermark}</div>
  <div class="hero-content">
    <h1>統計學習 <span class="green">×</span> <span class="blue">Python</span><br>互動自學網站</h1>
    <div class="subtitle">NSYSU MATH524 統計學習與資料探勘 · 依 ISLP 與課程講義編寫</div>
    <div class="big-formula">迴歸｜分類｜重抽樣｜模型選擇｜非監督式｜樣條與 GAM｜樹與集成｜SVM｜深度學習</div>
    <div class="scroll-hint">從課前準備開始<span>↓</span></div>
  </div>
</div>

<div class="container">
  <section>
    <div class="loop-box">
      <div class="lb-title">📌 建議學習迴圈（每一章都照這個節奏）</div>
      <p>這個網站是課程講義的互動版配套：<strong>講義給完整程式與推導，這裡給你「動手驗證直覺」的空間。</strong>
      每頁的 §徽章都標了 ISLP 節號與講義頁碼，方便左右對照；程式碼與「預期輸出」都逐字取自課程 lab 的實跑結果。<br>
      最後一章標了「補充」——本課沒有教 ISLP 第 10 章，那一頁的出處改用課本官方的英文 lab，其餘規格相同。<br>
      <strong>不知道從哪開始？</strong>先看<a href="#pre">課前準備</a>那三頁（一小時，不需要程式基礎）；
      <strong>沒寫過 Python？</strong>正課讀到卡住就翻<a href="#appendix">附錄</a>。兩區都是選讀，不列入評分。</p>
      <div class="loop-steps">
        <div class="step"><b>① READ &amp; PLAY</b>逐節閱讀，動手操作互動元件：先預測結果，再按按鈕驗證。</div>
        <div class="step"><b>② CROSS-CHECK</b>對照講義 PDF 與 ISLP 原文，把完整程式看懂、抄一遍、跑一遍。</div>
        <div class="step"><b>③ QUIZ</b>每節 quiz 立刻自測：答錯就回頭重讀該節，不要往下跳。</div>
        <div class="step"><b>④ FLASHCARDS &amp; REF</b>翻完詞彙卡、掃過 REF 速查表，能不看答案講出定義才算過關。</div>
      </div>
    </div>
  </section>

{pre_block}  <section id="core">
    <h2>正課 · 十一章</h2>
    <p>順序照課堂進度，不是 ISLP 的章號順序——非監督式學習（第 12 章）排在超越線性（第 7 章）之前。
    共 {len(core)} 章、{total_widgets} 個互動元件、{total_cards} 張詞彙卡。</p>
    <div class="ch-grid">
{cards}
    </div>
  </section>{app_block}

  <section>
    <h2>配套資源</h2>
    <div class="res-list">
      <div class="res-card"><b>📖 教科書 ISLP</b>An Introduction to Statistical Learning with
      Applications in Python（James、Witten、Hastie、Tibshirani、Taylor）。頁上的 §徽章都對應此書節號。<br>
      <a href="{P.BOOK_ISLP}" target="_blank" rel="noopener">statlearning.com（可免費下載）</a></div>
      <div class="res-card"><b>📗 進階參考 ESL</b>The Elements of Statistical Learning。
      標「ESL 進階」的段落對應這本，課堂沒細講，第一輪可略過。<br>
      <a href="{P.BOOK_ESL}" target="_blank" rel="noopener">hastie.su.domains/ElemStatLearn</a></div>
      <div class="res-card"><b>📑 課程講義與 Lab</b>每章「講義 PDF」與「中文 Lab」都連到課程 repo 的
      投影片與 notebook，是本站內容的完整版來源。<br>
      <a href="https://github.com/{P.COURSE_REPO}" target="_blank" rel="noopener">{P.COURSE_REPO.split("/")[1]}</a></div>
      <div class="res-card"><b>🔗 習題解答</b>課本課後習題的參考解答，EX 區每章都有連結。<br>
      <a href="https://botlnec.github.io/islp/" target="_blank" rel="noopener">botlnec.github.io/islp</a> ·
      <a href="https://github.com/Mohamed-Badry/islp-solutions" target="_blank" rel="noopener">islp-solutions</a> ·
      <a href="https://yuhangzhou88.github.io/ESL_Solution/" target="_blank" rel="noopener">ESL_Solution</a></div>
    </div>
  </section>
</div>

<footer>
  統計學習 × Python 互動自學網站 · 依 ISLP 教科書與 NSYSU MATH524 課程講義編寫<br>
  <span style="font-family:'JetBrains Mono',monospace;font-size:.78rem;color:var(--accent3);">Interactive Statistical Learning Self-Study · NSYSU</span>
</footer>
</body></html>
"""


def build_readme():
    rows = []
    for p in [q for q in P.PAGES if q.kind == "core"]:
        parts, cards, qs, widgets = counts(p)
        對應 = p.islp_label + (f"／{p.esl_label}" if p.esl_label else "")
        講義 = f"講義 {p.deck_no}" if p.deck else "—"     # 補充章沒有講義
        rows.append(f"| {p.n:02d} | [{p.plain}]({p.file}) | {對應} | {講義} | "
                    f"{parts} 節 · {widgets} 元件 · {cards} 張卡 |")
    table = "\n".join(rows)

    def side_table(grp):
        out = []
        for i, q in enumerate([x for x in P.PAGES if x.grp == grp], 1):
            parts, cards, _qs, widgets = counts(q)
            widget_label = "動態元件" if q.stem in {"00a_why_code", "00c_ai_assisted"} else "元件"
            out.append(f"| {i} | [{q.plain}]({q.file}) | {q.islp_label} | "
                       f"{parts} 節 · {widgets} {widget_label} · {cards} 張卡 |")
        return "\n".join(out)

    pre_table = side_table("pre")
    app_table = side_table("appendix")
    return f"""# 統計學習 × Python 互動自學網站

NSYSU MATH524「統計學習與資料探勘」的互動自學配套網站，分成三區：

1. **課前準備**（3 頁）——AI 時代的資料分析學習迴圈、環境安裝、AI 輔助統計分析。不需要程式基礎。
2. **正課**（11 章）——每一節都能動手操作、預測、驗證，配上每節 quiz、觀念釐清 Q&A、
   關鍵詞彙卡與 REF 速查表。
3. **附錄：Python 先備知識**（6 頁）——正課會用到的語法與套件，查閱用。

課前準備與附錄都是選讀，不列入評分。

- 線上閱讀：{P.SITE_URL}
- 教科書：[ISLP — An Introduction to Statistical Learning with Applications in Python]({P.BOOK_ISLP})
- 進階參考：[ESL — The Elements of Statistical Learning]({P.BOOK_ESL})
- 課程講義：[{P.COURSE_REPO.split("/")[1]}](https://github.com/{P.COURSE_REPO})（各頁「講義 PDF」與「中文 Lab」連結來源）

## 課前準備（選讀，不列入評分）

三頁，讀完大概一小時，不需要任何程式基礎。

| # | 頁面 | 對應 | 內容量 |
|---|------|------|--------|
{pre_table}

## 正課 · 十一章（授課順序）

| # | 頁面 | 對應 | 講義 | 內容量 |
|---|------|------|------|--------|
{table}

順序照課堂進度，不是 ISLP 的章號順序——非監督式學習（第 12 章）排在超越線性（第 7 章）之前，
集成學習那一週折進「樹狀方法與集成學習」。

## 附錄：Python 先備知識（選讀，不列入評分）

沒寫過 Python，或只會一點點？這六頁把正課會用到的語法與套件講一遍，
程式碼一樣逐字取自課程 lab notebook。**查閱用**——正課讀到卡住再回來翻，不必先讀完。

| # | 頁面 | 對應 | 內容量 |
|---|------|------|--------|
{app_table}

真的想先打底再進正課的話：P1 → P2 → P3 → P4 → P5 → P6；
寫過程式、只是沒碰過資料科學套件的，從 P3 開始就好。

## 內容出處

每頁的 §徽章都標了 ISLP 節號與講義頁碼。`.deck-extra` 卡片裡的程式碼與「預期輸出」
**逐字取自課程 lab notebook**（老師在課程環境實跑的結果），卡片下方的「來源」標了儲存格編號。
圖表用的烘焙資料由 `tools/frames/` 在固定種子下產生，環境為 {P.ENV_NOTE}。

第 11 頁「深度學習」是**補充章**——本課沒有教 ISLP 第 10 章，所以沒有講義也沒有中文 lab。
那一章的程式碼與輸出改為逐字取自[課本官方的英文 lab](https://github.com/intro-stat-learning/ISLP_labs)
（BSD 2-Clause，釘 commit `6bf6160`），「逐字引用、絕不重跑」的紀律不變。

## 技術

每頁皆為單檔自足 HTML。外部依賴只有三個：MathJax 3、Google Fonts、
Chart.js {P.CHARTJS_VER}（釘版本並附 SRI）。手寫的 SVG 元件是原生 JS，
Chart.js 載不到時只有圖表退回一句話結論，其餘互動照常運作。

## 開發

```bash
python3 tools/build_page.py        # 骨架與 GEN 區段（三處編號、prev/next 由 tools/pages.py 產生）
python3 tools/enrich/enrich_*.py   # 各章內容
python3 tools/inject_data.py       # 詞彙卡與題庫（母檔在 data/）
python3 tools/build_index.py       # 本檔與 index.html
python3 tools/validate.py --net    # 19 項具名檢查
node tools/browser_check.js        # 瀏覽器逐項（含手機版與 CDN 失效）
```

`.html` 全部是產物，**不要手改**——`validate.py` 會用 sha256 比對 GEN 區段並報錯。

維護與交接說明看 [`HANDOFF.md`](HANDOFF.md)；撰寫規則看 [`tools/STYLE_CONTRACT.md`](tools/STYLE_CONTRACT.md)。
"""


if __name__ == "__main__":
    (ROOT / "index.html").write_text(build_html(), encoding="utf-8")
    (ROOT / "README.md").write_text(build_readme(), encoding="utf-8")
    print(f"  index.html   {(ROOT / 'index.html').stat().st_size / 1024:.0f} KB"
          f"（{len(P.PAGES)} 張卡片）")
    print(f"  README.md    {(ROOT / 'README.md').stat().st_size} bytes")
