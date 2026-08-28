#!/usr/bin/env python3
"""全站驗證器。每條斷言都有名字，失敗訊息直接指到檔案與問題。

姊妹站（ds-python-selfstudy）沒有驗證器，結果三處編號不同步、`.btn` 沒顏色
之類的缺陷傳染到每一頁。這裡把每一條一致性要求都變成機器檢查。

用法：
  python3 tools/validate.py                       # 結構檢查（不連網）
  python3 tools/validate.py --page linear_regression
  python3 tools/validate.py --net                 # 加上外部連結 HEAD 檢查
  python3 tools/validate.py --net --base https://phonchi.github.io/statlearning-selfstudy/
"""
import hashlib
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_page as B  # noqa: E402
import pages as P  # noqa: E402
from paths import FLASHCARDS, QUESTIONS, ROOT, SRC_INDEX  # noqa: E402

FAIL, WARN = [], []


def fail(check, where, msg):
    FAIL.append(f"[{check}] {where}: {msg}")


def warn(check, where, msg):
    WARN.append(f"[{check}] {where}: {msg}")


# 共用 JS 的頂層宣告：不需要 w<NN> 前綴
SHARED_JS_NAMES = {
    "$", "HC", "NS", "Player", "quizCheck", "hlLine", "setStatus",
    "FLASHCARDS", "QUESTIONS", "BANKQUIZ",
}
# 骨架固定的 id：不需要 w<NN> 前綴
SKELETON_IDS = {"floatNav", "top", "fcGrid", "fcShuffle", "fcFlipAll", "fcUnflip", "bqBox",
                "MathJax-script"}

# XML 命名空間 URI 不是網路請求，不受 https-only 規則管
NS_URIS = ("http://www.w3.org/",)

# 先備入口層的四個徽章前綴是追加的（正則只會變寬鬆，對正課十一章零影響）：
#   課程 Lab ChN · 儲存格 k   ← 可機器驗證，check_prep_grounding 會核對儲存格存不存在
#   <套件> 文件 · …           ← lab 裡沒有的語法點才用
#   先備 · …                  ← islp_label 與 EX 徽章
#   AI-Stats §N               ← 只指名參考書概念，不引用其內容
BADGE_RE = re.compile(
    r"^(ISLP §|ISLP Ch\.|ESL §|ESL Ch\.|講義 \d[\d_]* · p\.|課程題庫"
    r"|課程 Lab Ch\d+ · "
    r"|(?:Python|NumPy|pandas|Matplotlib|seaborn|SciPy|statsmodels|scikit-learn"
    r"|Colab|conda) 文件 · "
    r"|先備 · |AI-Stats §)")


class Ids(HTMLParser):
    """收集 id、section 順序、h2 內容、in-page 錨點。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.sections, self.anchors = [], [], []
        self.h2s, self._h2, self._depth = [], None, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "section" and a.get("id"):
            self.sections.append(a["id"])
        if tag == "a" and (a.get("href") or "").startswith("#"):
            self.anchors.append(a["href"][1:])
        if tag == "h2":
            self._h2, self._depth = "", 1
        elif self._h2 is not None:
            self._h2 += f"<{tag}>"

    def handle_endtag(self, tag):
        if tag == "h2" and self._h2 is not None:
            self.h2s.append(self._h2)
            self._h2 = None

    def handle_data(self, data):
        if self._h2 is not None:
            self._h2 += data


def region(src, k):
    m = re.search(re.escape(B.BEGIN.format(k=k)) + r"(.*?)" + re.escape(B.END.format(k=k)),
                  src, re.S)
    return m.group(1).strip("\n") if m else None


def pagejs(src):
    m = re.search(r"<!-- PAGEJS:BEGIN -->(.*?)<!-- PAGEJS:END -->", src, re.S)
    return m.group(1) if m else ""


def js_strings(js):
    """粗略取出 JS 字串常值（單引號、雙引號、反引號）。註解不算。"""
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    js = re.sub(r"(?<![:/])//[^\n]*", "", js)
    out = []
    for m in re.finditer(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"|`((?:[^`\\]|\\.)*)`", js):
        out.append((m.group(1) or m.group(2) or m.group(3) or "", m.start()))
    return out


# ── 逐頁檢查 ────────────────────────────────────────────────────────────
def check_page(p: P.Page):
    dest = ROOT / p.file
    w = p.file
    if not dest.exists():
        fail("STRUCT", w, "檔案不存在（先跑 tools/build_page.py）")
        return
    src = dest.read_text(encoding="utf-8")
    ids = Ids()
    ids.feed(src)

    # STRUCT：單例區塊
    for tag, n in [("</head>", 1), ("</body>", 1), ('<div class="container">', 1),
                   ('id="floatNav"', 1), ('class="toc-grid"', 1),
                   ('class="chapter-nav"', 1), ("<footer>", 1)]:
        got = src.count(tag)
        if got != n:
            fail("STRUCT", w, f"{tag} 出現 {got} 次，應為 {n}")

    # NAV-SYNC：三處編號同步
    want = P.tokens(p)
    want_ids = [s.id for s, _, _ in want]
    nav = re.findall(r'data-target="([^"]+)"', region(src, "floatnav") or "")
    nav_tok = re.findall(r'class="fn-num">([^<]+)<', region(src, "floatnav") or "")
    nav_tok = [t for t in nav_tok if t != "↑ TOP"]
    toc_ids = re.findall(r'href="#([^"]+)"', region(src, "toc") or "")
    toc_tok = re.findall(r'class="toc-num">([^<]+)<', region(src, "toc") or "")
    want_tok = [t for _, t, _ in want]
    if nav != want_ids:
        fail("NAV-SYNC", w, f"float-nav 的 data-target 序列 {nav} ≠ 表 {want_ids}")
    if toc_ids != want_ids:
        fail("NAV-SYNC", w, f"TOC 序列 {toc_ids} ≠ 表 {want_ids}")
    if ids.sections != want_ids:
        fail("NAV-SYNC", w, f"<section> 序列 {ids.sections} ≠ 表 {want_ids}")
    if nav_tok != want_tok or toc_tok != want_tok:
        fail("NAV-SYNC", w, f"編號 token 不一致：nav {nav_tok} / toc {toc_tok} / 表 {want_tok}")
    for s, tok, number in want:
        r = region(src, f"sec:{s.id}")
        if r is None:
            fail("NAV-SYNC", w, f"缺少 sec:{s.id} 的 GEN 區段")
        elif number and number not in r:
            fail("NAV-SYNC", w, f"#{s.id} 的 .section-number 不是「{number}」")

    # ORDER：cards 一定最後
    if ids.sections and ids.sections[-1] != "cards":
        fail("ORDER", w, f"最後一節是 {ids.sections[-1]}，應為 cards")

    # ANCHOR：id 唯一、錨點可解析
    dup = [k for k, v in Counter(ids.ids).items() if v > 1]
    if dup:
        fail("ANCHOR", w, f"重複的 id：{dup}")
    dangling = sorted({a for a in ids.anchors if a and a not in set(ids.ids)})
    if dangling:
        fail("ANCHOR", w, f"指向不存在 id 的錨點：{dangling}")

    # BADGE：每個 h2 至少一個合格徽章
    badge_per_h2 = re.findall(r"<h2>(.*?)</h2>", src, re.S)
    for h in badge_per_h2:
        bs = re.findall(r'class="sec-badge">(.*?)</span>', h, re.S)
        title = re.sub(r"<[^>]+>", "", h).strip()[:40]
        if not bs:
            fail("BADGE", w, f"h2「{title}」沒有 .sec-badge")
        for b in bs:
            b = re.sub(r"<[^>]+>", "", b).strip()
            if not BADGE_RE.match(b):
                fail("BADGE", w, f"徽章格式不合：「{b}」（h2「{title}」）")

    # QUIZ-TRIPLE（只掃 HTML；<script> 內的 JS 字串會有 id="bq' + i + 'Options" 這種樣子）
    html_only = re.sub(r"<script\b.*?</script>", "", src, flags=re.S)
    for qid in sorted(set(re.findall(r"quizCheck\('([^']+)'", html_only))):
        for suf in ("Options", "Feedback"):
            if f'id="{qid}{suf}"' not in html_only:
                fail("QUIZ-TRIPLE", w, f"quizCheck('{qid}') 缺少 #{qid}{suf}")
    # 選項區塊內有巢狀 </div>，所以用「到 #<qid>Feedback 為止」界定，不用第一個 </div>
    for m in re.finditer(r'id="([^"]+)Options"(.*?)id="\1Feedback"', html_only, re.S):
        qid, block = m.group(1), m.group(2)
        # data-fb 的值裡允許 <strong> 等標記，所以不能用 [^>]*；用 onclick 當結束錨點
        opts = re.findall(r'<div class="quiz-opt"(.*?)onclick="quizCheck\(', block, re.S)
        if len(opts) != 3:
            fail("QUIZ-TRIPLE", w, f"#{qid} 有 {len(opts)} 個選項，應為 3")
        ncorrect = sum(1 for o in opts if 'data-correct="true"' in o)
        if ncorrect != 1:
            fail("QUIZ-TRIPLE", w, f"#{qid} 有 {ncorrect} 個正解，應為 1")
        for o in opts:
            if "data-correct=" not in o:
                fail("QUIZ-TRIPLE", w, f"#{qid} 有選項缺 data-correct")
            fb = re.search(r'data-fb="(.*?)"\s', o, re.S)
            if not fb or not fb.group(1).strip():
                fail("QUIZ-TRIPLE", w, f"#{qid} 有選項缺 data-fb（錯的選項也要寫錯在哪）")

    # DATA-L：hlLine 引用的行號必須存在
    for m in re.finditer(r"hlLine\('([^']+)',\s*(\d+)\)", src):
        rid, n = m.group(1), m.group(2)
        blk = re.search(r'id="' + re.escape(rid) + r'"(.*?)</div>', src, re.S)
        if not blk:
            fail("DATA-L", w, f"hlLine('{rid}') 指向不存在的區塊")
        elif f'data-l="{n}"' not in blk.group(1):
            fail("DATA-L", w, f"hlLine('{rid}', {n}) 找不到 data-l=\"{n}\"")

    # ID-PREFIX：69 個元件共用全域，前綴是唯一的防撞機制
    pref = f"w{p.n:02d}"
    for i in ids.ids:
        if i in SKELETON_IDS or i in want_ids:
            continue
        if re.match(r"^(q[A-Z]|dx-)", i):     # quiz id 與 deck-extra 錨點另有規則
            continue
        if not i.startswith(pref):
            fail("ID-PREFIX", w, f"id=\"{i}\" 沒有 {pref} 前綴")
    js = pagejs(src)
    # 只查真正的頂層宣告（第 0 欄）；函式內的區域變數不會相撞
    for m in re.finditer(r"^(?:function|const|let|var|class)\s+([A-Za-z_$][\w$]*)", js, re.M):
        name = m.group(1)
        if name in SHARED_JS_NAMES or pref in name:
            continue
        fail("ID-PREFIX", w, f"本頁 JS 頂層宣告 `{name}` 沒有 {pref} 前綴")

    # GEN-REGION：產生區段必須與樣板算出的一致
    expect = {"head": B.head(p), "floatnav": B.floatnav(p), "hero": B.hero(p),
              "studyguide": B.studyguide(p), "toc": B.toc(p),
              "chapternav": B.chapternav(p), "footer": B.footer(p), "sharedjs": B.sharedjs(p)}
    for k, body in expect.items():
        got = region(src, k)
        if got is None:
            fail("GEN-REGION", w, f"缺少 GEN 區段 {k}")
        elif hashlib.sha256(got.encode()).hexdigest() != hashlib.sha256(body.encode()).hexdigest():
            fail("GEN-REGION", w, f"{k} 與樣板不一致（跑 tools/build_page.py 重繪，不要手改）")

    # FORBIDDEN
    for bad, why in [("polyfill.io", "2024 年被投毒的 CDN"),
                     ("cdn.tailwindcss.com", "會跟本站設計 token 打架")]:
        if bad in src:
            fail("FORBIDDEN", w, f"出現 {bad}（{why}）")
    insecure = [m.group(0) for m in re.finditer(r"http://[^\s\"'<>)]+", src)
                if not m.group(0).startswith(NS_URIS)]
    if insecure:
        fail("FORBIDDEN", w, f"出現非 https 連結：{sorted(set(insecure))[:3]}")
    if f"chart.js@{P.CHARTJS_VER}" not in src:
        fail("FORBIDDEN", w, f"Chart.js 必須釘在 @{P.CHARTJS_VER}")
    if P.CHARTJS_SRI not in src:
        fail("FORBIDDEN", w, "Chart.js 缺少或不符實算的 integrity")
    if re.search(r"<img\s", src):
        fail("FORBIDDEN", w, "出現 <img>：所有視覺都要是 inline SVG / canvas，不放圖檔")
    # Chart.js 4 的 Config.prototype.plugins 只有 getter，建構後賦值會靜默失效
    # （參考線畫不出來而且不報錯）。要設參考線一律用 HC.refs()。
    js_nocomment = re.sub(r"/\*.*?\*/", "", pagejs(src), flags=re.S)
    js_nocomment = re.sub(r"(?<![:/])//[^\n]*", "", js_nocomment)
    if "config.plugins =" in js_nocomment:
        fail("FORBIDDEN", w, "本頁 JS 有 `config.plugins =` 賦值——那是靜默失效的，改用 HC.refs()")
    # canvas 不認得 var(--x)：Chart.js 的顏色欄位放 CSS 變數會靜默變黑，要用 HC.tok.*
    bad_col = re.findall(r"(?:border|background|point[A-Za-z]*|hover[A-Za-z]*)Color:\s*'var\(--[^']+'",
                         js_nocomment)
    if bad_col:
        fail("FORBIDDEN", w, f"Chart.js 顏色用了 CSS 變數（canvas 不認得，會變黑）：{sorted(set(bad_col))[:3]}")

    # MATHJAX：數學不進 JS 字串；注入含數學的 innerHTML 要 retype
    for s, pos in js_strings(js):
        if re.search(r"\$(?!\{)", s):
            line = js[:pos].count("\n") + 1
            fail("MATHJAX", w, f"本頁 JS 第 {line} 行的字串含 $：數學請放靜態 HTML")
    for m in re.finditer(r"(innerHTML\s*=|insertAdjacentHTML\()", js):
        seg = js[m.start():m.start() + 900]
        if re.search(r"\\\(|\\\[", seg.split("\n")[0]) and "HC.retype(" not in seg:
            fail("MATHJAX", w, "innerHTML 寫入含數學但附近沒有 HC.retype()")
    for m in re.finditer(r'class="status-banner"[^>]*>(.*?)</div>', src, re.S):
        if re.search(r"\$(?!\{)", m.group(1)):
            fail("MATHJAX", w, ".status-banner 預設文字含 $（旁白依規定不放數學）")

    # FRAMES-META：烘焙資料要能追出處
    for m in re.finditer(r"const\s+(FRAMES_\w+)\s*=\s*\{", src):
        name = m.group(1)
        seg = src[m.start():m.start() + 3000]
        for key in ("src", "seed", "versions", "gen"):
            if f'"{key}"' not in seg and f"{key}:" not in seg:
                fail("FRAMES-META", w, f"{name} 的 meta 缺 {key}")

    # GROUNDING
    # 用「切到下一張卡為止」而不是固定字元視窗：長輸出會把 .dx-src 推到視窗外
    chunks = src.split('<div class="deck-extra"')[1:]
    for i, seg in enumerate(chunks):
        if 'class="dx-src"' not in seg.split('<div class="deck-extra"')[0]:
            lab = re.search(r'class="dx-label">(.*?)<', seg)
            fail("GROUNDING", w,
                 f".deck-extra 缺 .dx-src 出處標記（第 {i + 1} 張"
                 f"{'：' + lab.group(1) if lab else ''}）")
    # 來源 lab 可以有多份（先備頁一頁會引用 lab_ch1 與 lab_ch2）。
    # 檔案不存在一律 fail —— 舊版是靜默跳過，等於整段檢查無聲失效。
    src_chs = p.src_labs or (p.islp,)
    parts = []
    for ch in src_chs:
        lab = SRC_INDEX / f"lab_ch{ch}.md"
        if not lab.exists():
            fail("GROUNDING", w, f"來源索引 {lab.name} 不存在（跑 tools/extract_lab.py）")
            continue
        parts.append(lab.read_text(encoding="utf-8"))
    labtext = "\n".join(parts)
    labs_note = "／".join(f"lab_ch{c}.md" for c in src_chs)
    for m in re.finditer(r'<div class="expected-out">.*?<pre>(.*?)</pre>', src, re.S):
        body = re.sub(r"<[^>]+>", "", m.group(1))
        for a, b in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'),
                     ("&#x27;", "'"), ("&#39;", "'"), ("&amp;", "&")):
            body = body.replace(a, b)
        body = body.strip()
        head = next((ln.strip() for ln in body.splitlines() if ln.strip()), "")
        if head and labtext and head not in labtext:
            warn("GROUNDING", w, f"預期輸出的首行在 {labs_note} 找不到：「{head[:60]}」")
    if not re.search(r'class="ver-note"', src):
        warn("GROUNDING", w, "REF 區缺 .ver-note 環境版本註記")

    # GROUNDING-PREP：先備頁的出處要求比正課更硬（fail 等級）。
    # 整段被 kind=="prep" 包住，正課十一章一行都不會執行，所以不可能製造新的 warn。
    if p.kind == "prep":
        check_prep_grounding(p, w, src, labtext)

    # SIZE
    kb = dest.stat().st_size / 1024
    if kb > 300:
        warn("SIZE", w, f"{kb:.0f} KB，超過 300 KB 建議上限")

    # TODO 殘留
    n_todo = src.count("TODO")
    if n_todo:
        warn("TODO", w, f"還有 {n_todo} 處 TODO")


# ── 先備入口層的出處檢查 ────────────────────────────────────────────────
DX_SRC_RE = re.compile(r'class="dx-src">來源：<code>Ch(\d+)-[^<]*\.ipynb</code> · 儲存格 ([^<]+)')
CELL_RE = re.compile(r"\d+")
PREP_BADGE_RE = re.compile(r"課程 Lab Ch(\d+) · 儲存格 ([^<]+)")


def _lab_cells(ch: int) -> dict:
    """lab_chN.md 的 {儲存格編號: 該格的輸出（沒有輸出就是 None）}。"""
    f = SRC_INDEX / f"lab_ch{ch}.md"
    if not f.exists():
        return {}
    text = f.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"^## 儲存格 (\d+) \[code\]\n(.*?)(?=^## 儲存格 |\Z)",
                         text, re.S | re.M):
        o = re.search(r"\*\*輸出\*\*\n\n```\n(.*?)\n```", m.group(2), re.S)
        out[int(m.group(1))] = o.group(1) if o else None
    return out


def _unescape(t: str) -> str:
    for a, b in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'),
                 ("&#x27;", "'"), ("&#39;", "'"), ("&amp;", "&")):
        t = t.replace(a, b)
    return t


def check_prep_grounding(p, w, src, labtext):
    """先備頁專用（fail 等級）。正課頁不會走到這裡。

    1. 每張 .deck-extra 的 .dx-src 要能解析成「ChNN 某個 lab · 儲存格 k」，
       章號必須在 Page.src_labs 裡，儲存格必須真的存在於該 lab。
    2. 有 .expected-out 的卡，內容必須逐字等於該格的實跑輸出（不是「首行找得到」）。
    3. 一頁至少要有一張 lab 引用卡，否則這一頁等於沒有出處。
    4. 「課程 Lab ChN · 儲存格 k」徽章所指的儲存格也要存在——徽章從自由文字
       升級成可驗證的交叉引用。
    """
    cells = {ch: _lab_cells(ch) for ch in (p.src_labs or (p.islp,))}
    n_cited = 0
    for i, seg in enumerate(src.split('<div class="deck-extra"')[1:]):
        seg = seg.split('<div class="deck-extra"')[0]
        m = DX_SRC_RE.search(seg)
        if not m:
            if 'class="dx-src"' in seg:
                fail("GROUNDING-PREP", w,
                     f"第 {i + 1} 張 .deck-extra 的 .dx-src 不符文法"
                     "（要「來源：<code>ChNN-….ipynb</code> · 儲存格 k」）")
            continue
        ch = int(m.group(1))
        ks = [int(x) for x in CELL_RE.findall(m.group(2))]
        if ch not in cells:
            fail("GROUNDING-PREP", w,
                 f"第 {i + 1} 張引用 Ch{ch:02d}，但它不在 Page.src_labs={p.src_labs}")
            continue
        missing = [k for k in ks if k not in cells[ch]]
        if missing:
            fail("GROUNDING-PREP", w,
                 f"第 {i + 1} 張引用 lab_ch{ch}.md 不存在的儲存格 {missing}")
            continue
        n_cited += 1
        eo = re.search(r'<div class="expected-out">.*?<pre>(.*?)</pre>', seg, re.S)
        if eo:
            got = _unescape(re.sub(r"<[^>]+>", "", eo.group(1))).rstrip()
            want = [cells[ch][k].rstrip() for k in ks if cells[ch].get(k) is not None]
            if not want:
                fail("GROUNDING-PREP", w,
                     f"第 {i + 1} 張有預期輸出，但 lab_ch{ch}.md 儲存格 {ks} 沒存輸出")
            elif got not in want:
                fail("GROUNDING-PREP", w,
                     f"第 {i + 1} 張的預期輸出與 lab_ch{ch}.md 儲存格 {ks} 不逐字相同")
    if not n_cited:
        fail("GROUNDING-PREP", w, "整頁沒有任何引用課程 lab 的 .deck-extra")
    for m in PREP_BADGE_RE.finditer(src):
        ch = int(m.group(1))
        if ch not in cells:
            fail("GROUNDING-PREP", w, f"徽章指向 Ch{ch:02d}，但它不在 Page.src_labs")
            continue
        bad = [k for k in (int(x) for x in CELL_RE.findall(m.group(2)))
               if k not in cells[ch]]
        if bad:
            fail("GROUNDING-PREP", w, f"徽章指向 lab_ch{ch}.md 不存在的儲存格 {bad}")


# ── 全站檢查 ────────────────────────────────────────────────────────────
def check_flashcards():
    for p in P.PAGES:
        f = FLASHCARDS / f"{p.dkey}.json"
        if not f.exists():
            warn("FLASHCARD", f.name, "尚未撰寫")
            continue
        try:
            cards = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fail("FLASHCARD", f.name, f"JSON 解析失敗：{e}")
            continue
        if not isinstance(cards, list) or not cards:
            fail("FLASHCARD", f.name, "必須是非空的 list")
            continue
        fronts = []
        for i, c in enumerate(cards):
            if not isinstance(c, dict) or "front" not in c or "back" not in c:
                fail("FLASHCARD", f.name, f"第 {i} 張缺 front/back")
                continue
            if not str(c["back"]).strip():
                fail("FLASHCARD", f.name, f"第 {i} 張 back 是空的")
            fronts.append(str(c["front"]))
        dup = [k for k, v in Counter(fronts).items() if v > 1]
        if dup:
            fail("FLASHCARD", f.name, f"重複的正面：{dup}")
        withen = sum(1 for x in fronts if re.match(r"^[^（]+（[^）]+）$", x))
        if fronts and withen / len(fronts) < 0.8:
            warn("FLASHCARD", f.name,
                 f"只有 {withen}/{len(fronts)} 張正面是「中文（English）」格式")
        if not (18 <= len(cards) <= 34):
            warn("FLASHCARD", f.name, f"{len(cards)} 張，建議 20–28 張")


def check_questions():
    for p in P.PAGES:
        f = QUESTIONS / f"{p.dkey}.json"
        if not p.bankquiz:
            continue
        if not f.exists():
            warn("BANKQUIZ", f.name, "這頁有題庫區但母檔尚未撰寫")
            continue
        try:
            qs = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fail("BANKQUIZ", f.name, f"JSON 解析失敗：{e}")
            continue
        for i, q in enumerate(qs):
            for k in ("q", "options", "answer", "why"):
                if k not in q:
                    fail("BANKQUIZ", f.name, f"第 {i} 題缺 {k}")
            if "options" not in q or "why" not in q:
                continue
            if len(q["options"]) != len(q["why"]):
                fail("BANKQUIZ", f.name, f"第 {i} 題 options 與 why 長度不符")
            if not isinstance(q.get("answer"), int) or not (0 <= q["answer"] < len(q["options"])):
                fail("BANKQUIZ", f.name, f"第 {i} 題的 answer 不是合法索引")
            for j, wy in enumerate(q["why"]):
                if not str(wy).strip():
                    fail("BANKQUIZ", f.name, f"第 {i} 題第 {j} 個選項沒寫為什麼")


def check_index():
    f = ROOT / "index.html"
    if not f.exists():
        warn("INDEX-SYNC", "index.html", "尚未產生")
        return
    src = f.read_text(encoding="utf-8")
    cards = re.findall(r'<a class="ch-card" href="([^"]+)"', src)
    want = [p.file for p in P.PAGES]
    if cards != want:
        fail("INDEX-SYNC", "index.html", f"卡片順序 {cards} ≠ 表 {want}")
    for href in cards:
        if not (ROOT / href).exists():
            fail("INDEX-SYNC", "index.html", f"卡片指向不存在的 {href}")
    for p in P.PAGES:
        fc = FLASHCARDS / f"{p.dkey}.json"
        if not fc.exists():
            continue
        n = len(json.loads(fc.read_text(encoding="utf-8")))
        m = re.search(re.escape(p.file) + r'".*?class="ch-meta">([^<]*)', src, re.S)
        if m and f"{n} 張詞彙卡" not in m.group(1):
            fail("INDEX-SYNC", "index.html",
                 f"{p.file} 的 .ch-meta「{m.group(1)}」與 {p.dkey}.json 的 {n} 張不符")


def check_repo():
    for bad in ("_config.yml", "Gemfile", "LICENSE"):
        if (ROOT / bad).exists():
            fail("FORBIDDEN", "repo", f"不該有 {bad}（純靜態站）")
    if not (ROOT / ".nojekyll").exists():
        fail("FORBIDDEN", "repo", "缺 .nojekyll，GitHub Pages 會用 Jekyll 建置")
    for f in ROOT.rglob("*"):
        if f.is_file() and f.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
            fail("FORBIDDEN", "repo", f"出現圖檔 {f.relative_to(ROOT)}：所有視覺都要 inline")
        # 素材不進 repo：教科書 PDF 放 ~/statslearning，notebook 只留 data/source_index/ 的 .md
        if f.is_file() and f.suffix.lower() in {".pdf", ".ipynb"}:
            fail("FORBIDDEN", "repo",
                 f"出現素材檔 {f.relative_to(ROOT)}：PDF／notebook 放 repo 外（見 .gitignore）")


def check_links(base=None):
    import urllib.error
    import urllib.request
    urls = set()
    for p in P.PAGES:
        f = ROOT / p.file
        if not f.exists():
            continue
        for m in re.finditer(r'href="(https?://[^"]+)"', f.read_text(encoding="utf-8")):
            urls.add(m.group(1))
    if (ROOT / "index.html").exists():
        for m in re.finditer(r'href="(https?://[^"]+)"',
                             (ROOT / "index.html").read_text(encoding="utf-8")):
            urls.add(m.group(1))
    print(f"\nLINKS：檢查 {len(urls)} 個外部連結…")
    for u in sorted(urls):
        try:
            req = urllib.request.Request(u, method="HEAD",
                                         headers={"User-Agent": "Mozilla/5.0 link-check"})
            code = urllib.request.urlopen(req, timeout=25).status
            if code >= 400:
                fail("LINKS", u, f"HTTP {code}")
        except urllib.error.HTTPError as e:
            if e.code in (403, 405, 429):        # 有些站不接受 HEAD
                warn("LINKS", u, f"HTTP {e.code}（可能只是不接受 HEAD）")
            else:
                fail("LINKS", u, f"HTTP {e.code}")
        except Exception as e:
            fail("LINKS", u, f"{type(e).__name__}: {e}")


def main(argv):
    only = None
    if "--page" in argv:
        only = argv[argv.index("--page") + 1]
    targets = [P.BY_STEM[only]] if only else P.PAGES
    for p in targets:
        check_page(p)
    if not only:
        check_flashcards()
        check_questions()
        check_index()
        check_repo()
    if "--net" in argv:
        check_links()

    print()
    for x in WARN:
        print("  warn  " + x)
    for x in FAIL:
        print("  FAIL  " + x)
    print(f"\n{len(FAIL)} 個失敗，{len(WARN)} 個警告"
          f"（檢查了 {len(targets)} 頁）")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
