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

BADGE_RE = re.compile(r"^(ISLP §|ISLP Ch\.|ESL §|ESL Ch\.|講義 \d[\d_]* · p\.|課程題庫)")


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

    # QUIZ-TRIPLE
    for qid in sorted(set(re.findall(r"quizCheck\('([^']+)'", src))):
        for suf in ("Options", "Feedback"):
            if f'id="{qid}{suf}"' not in src:
                fail("QUIZ-TRIPLE", w, f"quizCheck('{qid}') 缺少 #{qid}{suf}")
    for m in re.finditer(r'<div class="quiz-options"[^>]*id="([^"]+)Options"[^>]*>(.*?)</div>\s*\n?\s*<div class="quiz-feedback"',
                         src, re.S):
        qid, block = m.group(1), m.group(2)
        opts = re.findall(r'<div class="quiz-opt"([^>]*)>', block)
        if len(opts) != 3:
            fail("QUIZ-TRIPLE", w, f"#{qid} 有 {len(opts)} 個選項，應為 3")
        ncorrect = sum(1 for o in opts if 'data-correct="true"' in o)
        if ncorrect != 1:
            fail("QUIZ-TRIPLE", w, f"#{qid} 有 {ncorrect} 個正解，應為 1")
        for o in opts:
            if "data-correct=" not in o:
                fail("QUIZ-TRIPLE", w, f"#{qid} 有選項缺 data-correct")
            fb = re.search(r'data-fb="([^"]*)"', o)
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
    for m in re.finditer(r"^\s*(?:function|const|let|var|class)\s+([A-Za-z_$][\w$]*)", js, re.M):
        name = m.group(1)
        if name in SHARED_JS_NAMES or name.startswith(pref):
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
        for key in ("src:", "seed:", "versions:", "gen:"):
            if key not in seg:
                fail("FRAMES-META", w, f"{name} 的 meta 缺 {key}")

    # GROUNDING
    for m in re.finditer(r'<div class="deck-extra"', src):
        seg = src[m.start():m.start() + 6000]
        if 'class="dx-src"' not in seg:
            fail("GROUNDING", w, ".deck-extra 缺 .dx-src 出處標記")
    lab = SRC_INDEX / f"lab_ch{p.islp}.md"
    labtext = lab.read_text(encoding="utf-8") if lab.exists() else ""
    for m in re.finditer(r'<div class="expected-out">.*?<pre>(.*?)</pre>', src, re.S):
        body = re.sub(r"<[^>]+>", "", m.group(1))
        body = (body.replace("&lt;", "<").replace("&gt;", ">")
                    .replace("&quot;", '"').replace("&amp;", "&")).strip()
        head = next((ln.strip() for ln in body.splitlines() if ln.strip()), "")
        if head and labtext and head not in labtext:
            warn("GROUNDING", w, f"預期輸出的首行在 lab_ch{p.islp}.md 找不到：「{head[:60]}」")
    if not re.search(r'class="ver-note"', src):
        warn("GROUNDING", w, "REF 區缺 .ver-note 環境版本註記")

    # SIZE
    kb = dest.stat().st_size / 1024
    if kb > 300:
        warn("SIZE", w, f"{kb:.0f} KB，超過 300 KB 建議上限")

    # TODO 殘留
    n_todo = src.count("TODO")
    if n_todo:
        warn("TODO", w, f"還有 {n_todo} 處 TODO")


# ── 全站檢查 ────────────────────────────────────────────────────────────
def check_flashcards():
    for p in P.PAGES:
        f = FLASHCARDS / f"ch{p.islp}.json"
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
        fc = FLASHCARDS / f"ch{p.islp}.json"
        if not fc.exists():
            continue
        n = len(json.loads(fc.read_text(encoding="utf-8")))
        m = re.search(re.escape(p.file) + r'".*?class="ch-meta">([^<]*)', src, re.S)
        if m and f"{n} 張詞彙卡" not in m.group(1):
            fail("INDEX-SYNC", "index.html",
                 f"{p.file} 的 .ch-meta「{m.group(1)}」與 ch{p.islp}.json 的 {n} 張不符")


def check_repo():
    for bad in ("_config.yml", "Gemfile", "LICENSE"):
        if (ROOT / bad).exists():
            fail("FORBIDDEN", "repo", f"不該有 {bad}（純靜態站）")
    if not (ROOT / ".nojekyll").exists():
        fail("FORBIDDEN", "repo", "缺 .nojekyll，GitHub Pages 會用 Jekyll 建置")
    for f in ROOT.rglob("*"):
        if f.is_file() and f.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
            fail("FORBIDDEN", "repo", f"出現圖檔 {f.relative_to(ROOT)}：所有視覺都要 inline")


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
