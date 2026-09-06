#!/usr/bin/env python3
"""站台的唯一真實來源。

十一章的順序、標題、講義與 lab 對應、每一節的 id / 徽章都只寫在這裡。
build_page.py 由此產生 float-nav、TOC、每節的 .section-number、chapter-nav、
index.html 卡片與 README 章節表——所以三處編號不可能不同步。

兩條命名法（不要動）：
1. data/*/chN.json 的 N ＝ ISLP 章號，不是站內序號。授課順序與 ISLP 章號不同
   （站內第 07 頁對應 ISLP 第 12 章），用 ISLP 章號才跟徽章、講義檔名、lab 檔名一致。
2. 頁面檔名是小寫 snake_case 的英文主題字根，不編號。順序只由本表承載。
"""
from dataclasses import dataclass, field

COURSE_REPO = "phonchi/nsysu-math524-2025"   # 凍結的封存 repo，連結不會爛
SITE_REPO = "phonchi/statlearning-selfstudy"
SITE_URL = "https://phonchi.github.io/statlearning-selfstudy/"
CLASSROOM_PACKAGES = "https://github.com/phonchi/nsysu-math524/blob/main/static_files/presentations/packages.txt"

CHARTJS_VER = "4.5.1"
# 實算：curl -sL <url> | openssl dgst -sha384 -binary | openssl base64 -A
CHARTJS_SRI = "sha384-jb8JQMbMoBUzgWatfe6COACi2ljcDdZQ2OxczGA3bGNeWe+6DChMTBJemed7ZnvJ"

BOOK_ISLP = "https://www.statlearning.com/"
BOOK_ESL = "https://hastie.su.domains/ElemStatLearn/"
# 各章課後習題的真實節號。實測自 ISLP PDF 的 "N.x Exercises" 標題——
# 不要假設一律是 N.4，只有第 2、5、8 章剛好是（Ch3 是 3.7、Ch4 是 4.8、
# Ch6 是 6.6、Ch7 是 7.9、Ch9 是 9.7、Ch12 是 12.6）。第 1 章沒有習題。
EX_SEC = {2: "2.4", 3: "3.7", 4: "4.8", 5: "5.4", 6: "6.6",
          7: "7.9", 8: "8.4", 9: "9.7", 10: "10.10", 12: "12.6"}


def sol_links(ch: int):
    """該章實際存在的解答連結。已逐一 HEAD 驗證過覆蓋範圍：
    botlnec 只有第 2–9 章；Mohamed-Badry 只有第 2–13 章；
    ISLP 第 1 章本來就沒有課後習題，所以兩邊都沒有。"""
    out = []
    if 2 <= ch <= 9:
        out.append(("🔗 ISLP 解答（botlnec）",
                    f"https://botlnec.github.io/islp/sols/chapter{ch}/exercise1"))
    if 2 <= ch <= 13:
        out.append(("🔗 ISLP 解答（Mohamed-Badry）",
                    "https://github.com/Mohamed-Badry/islp-solutions/blob/main/"
                    f"Exercises_ch{ch:02d}.ipynb"))
    out.append(("🔗 ESL 解答（YuhangZhou88）", "https://yuhangzhou88.github.io/ESL_Solution/"))
    return out

# 網站既有 frames 的生成環境，保留歷史數值來源；考前準備以 CLASSROOM_PACKAGES 為準。
ENV_NOTE = ("numpy 1.24.4 · pandas 2.3.2 · scikit-learn 1.6.1 · scipy 1.13.1 · "
            "statsmodels 0.14.2 · ISLP 0.4.0 · pygam 0.10.1")


@dataclass
class Sec:
    """一個 <section>。token 與 .section-number 由 build_page 依順序產生。"""
    id: str
    short: str                 # nav / TOC 用的中文短名
    h2: str                    # 標題（可含 <span> 上色）
    badge: str                 # .sec-badge 內容；多個徽章用 |
    eslx: bool = False         # 標成「ESL 進階」可略過
    kicker: str = ""           # 覆寫 .section-number 的詞（預設 PART NN）


@dataclass
class Page:
    n: int                     # 站內序號（授課順序）
    stem: str                  # 檔名（不含 .html）
    slug: str                  # .ch-num 用的英文大寫短名
    title_en: str
    h1: str                    # hero 的 h1（含 span 上色）
    plain: str                 # 純文字標題（index 卡片、chapter-nav、README）
    subtitle: str
    formula: str               # .big-formula，｜分隔，只用 Unicode 不用 $
    deck: str                  # 講義 PDF 檔名（補充章沒有講義，留空字串）
    deck_pages: int
    lab: str                   # lab notebook 檔名（補充章沒有中文 lab，留空字串）
    islp: int                  # ISLP 章號（＝ data/*/chN.json 的 N）
    islp_label: str
    esl_label: str
    playlist: str              # YouTube 課程錄影 playlist id（可多個逗號分隔；沒有就留空）
    hero_svg: str              # hero 裝飾 SVG 的內容
    secs: list = field(default_factory=list)
    bankquiz: bool = False
    # study-guide 上額外的連結 pill，[(標籤, 網址), ...]。補充章用它掛官方 lab；
    # 既有章留空，studyguide() 的輸出 byte 不變。
    extra_pills: list = field(default_factory=list)

    # ── 先備入口層（n=12 起）用的欄位。全部有預設值，既有十一章的 Page(...) 字面值
    #    一字不動，GEN 區段 byte 不變。─────────────────────────────────────
    kind: str = "core"          # "core"＝正課十一章；"prep"＝課前準備與先備知識
    data_key: str = ""          # 詞彙卡／題庫的檔名鍵；空字串→沿用 ch{islp}
    src_labs: tuple = ()        # 本頁允許引用的 lab 章號，如 (2, 1)；空→(islp,)
    ex_links: list = field(default_factory=list)   # prep 頁 EX 區的 pill（官方文件）
    nav_next: str = ""          # 覆寫 chapter-nav 的下一頁 stem（區與區之間的接縫）
    nav_prev: str = ""          # 覆寫 chapter-nav 的上一頁 stem（同上，反方向）
    # 顯示分區。空字串→退回 kind。"pre"（課前準備）、"statistics"（統計附錄）、"core"（正課）、
    # "appendix"（Python 先備）。kind 管教學文案，grounding_mode 管來源檢查；group 管位置。
    # （prep 頁要過 check_prep_grounding），group 管的是「這頁排在哪一區」。
    group: str = ""
    deck_url: str = ""         # 單頁引用的講義版本；空字串沿用課程封存站
    deck_label: str = ""
    deck_note: str = ""
    legacy_anchors: tuple = ()  # 重排後保留在小標題上的既有書籤
    page_css: str = ""         # 僅此頁需要的閱讀版面，避免影響其他章
    grounding_mode: str = "lab"  # lab：課程程式與輸出；concept：書目、算例與模擬

    @property
    def grp(self) -> str:
        """顯示分區。沒指定就退回 kind。"""
        return self.group or self.kind

    @property
    def dkey(self) -> str:
        """data/*_zh/<dkey>.json 的檔名鍵。正課沿用 ISLP 章號，先備頁自訂。"""
        return self.data_key or f"ch{self.islp}"

    @property
    def deck_no(self) -> str:
        return self.deck.split("_")[0]

    @property
    def file(self) -> str:
        return self.stem + ".html"

    @property
    def blob(self) -> str:
        return f"https://github.com/{COURSE_REPO}/blob/main/static_files/presentations/"


# ── hero 裝飾 SVG（各章一個，opacity 由 CSS 給，≤900px 隱藏）─────────────

def _svg_grid():
    """先備 P3：一塊 4×4 的陣列，右下角被切出一個子矩陣。"""
    cells = "".join(
        f'<rect x="{40 + c * 58}" y="{50 + r * 42}" width="50" height="34" rx="4"/>'
        for r in range(4) for c in range(4))
    hi = "".join(
        f'<rect x="{40 + c * 58}" y="{50 + r * 42}" width="50" height="34" rx="4"/>'
        for r in (1, 3) for c in (0, 2))
    return (f'<g fill="#fff" opacity=".28">{cells}</g>'
            f'<g fill="#fff" opacity=".95">{hi}</g>'
            '<g stroke="#fff" stroke-width="3" fill="none" opacity=".8">'
            '<path d="M26 40 H26 V228 H26"/><path d="M20 40 H32"/><path d="M20 228 H32"/></g>')


def _svg_scatter():
    pts = [(30, 210), (58, 190), (72, 200), (95, 168), (118, 172), (140, 148),
           (162, 136), (185, 142), (208, 112), (230, 100), (252, 96), (275, 74)]
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="6"/>' for x, y in pts)
    return (f'<g fill="#fff" opacity=".92">{dots}</g>'
            '<g stroke="#fff" stroke-width="3" fill="none" opacity=".85">'
            '<path d="M22 224 L292 66"/><path d="M22 240 H300"/><path d="M22 240 V40"/></g>')


def _svg_tree():
    return ('<g stroke="#fff" stroke-width="3" fill="none" opacity=".85">'
            '<path d="M160 40 V70"/><path d="M160 70 L95 110"/><path d="M160 70 L225 110"/>'
            '<path d="M95 110 L60 165"/><path d="M95 110 L130 165"/>'
            '<path d="M225 110 L195 165"/><path d="M225 110 L262 165"/></g>'
            '<g fill="#fff" opacity=".92">'
            '<rect x="140" y="20" width="40" height="22" rx="4"/>'
            '<rect x="75" y="98" width="40" height="22" rx="4"/>'
            '<rect x="205" y="98" width="40" height="22" rx="4"/>'
            '<circle cx="60" cy="180" r="12"/><circle cx="130" cy="180" r="12"/>'
            '<circle cx="195" cy="180" r="12"/><circle cx="262" cy="180" r="12"/></g>')


def _svg_folds():
    rects = ""
    for r in range(5):
        for c in range(5):
            fill = "#fff" if r == c else "none"
            op = ".9" if r == c else ".45"
            rects += (f'<rect x="{40 + c * 48}" y="{50 + r * 38}" width="42" height="30" rx="4" '
                      f'fill="{fill}" opacity="{op}" stroke="#fff" stroke-width="2"/>')
    return f'<g>{rects}</g>'


def _svg_boundary():
    return ('<g stroke="#fff" stroke-width="3" fill="none" opacity=".8">'
            '<path d="M30 210 Q110 60 290 90"/></g>'
            '<g fill="#fff" opacity=".9">'
            '<circle cx="70" cy="90" r="7"/><circle cx="110" cy="60" r="7"/>'
            '<circle cx="150" cy="52" r="7"/><circle cx="205" cy="55" r="7"/></g>'
            '<g fill="none" stroke="#fff" stroke-width="2.5" opacity=".9">'
            '<rect x="62" y="182" width="14" height="14"/><rect x="122" y="205" width="14" height="14"/>'
            '<rect x="186" y="160" width="14" height="14"/><rect x="240" y="140" width="14" height="14"/></g>')


def _svg_curves():
    return ('<g stroke="#fff" fill="none" stroke-width="3" opacity=".85">'
            '<path d="M25 200 Q90 60 160 150 T295 80"/></g>'
            '<g stroke="#fff" fill="none" stroke-width="2" opacity=".45" stroke-dasharray="6 5">'
            '<path d="M25 170 L295 110"/></g>'
            '<g stroke="#fff" stroke-width="2" opacity=".5">'
            '<path d="M90 40 V230"/><path d="M160 40 V230"/><path d="M230 40 V230"/></g>')


def _svg_shrink():
    return ('<g stroke="#fff" fill="none" stroke-width="3" opacity=".85">'
            '<path d="M40 60 Q150 130 285 132"/><path d="M40 120 Q150 132 285 133"/>'
            '<path d="M40 205 Q150 140 285 134"/><path d="M40 165 Q150 138 285 133"/></g>'
            '<g stroke="#fff" stroke-width="2" opacity=".5" stroke-dasharray="5 4">'
            '<path d="M30 133 H295"/></g>'
            '<g fill="none" stroke="#fff" stroke-width="2.5" opacity=".8">'
            '<path d="M200 40 L235 75 L200 110 L165 75 Z"/></g>')


def _svg_cluster():
    g1 = [(70, 70), (95, 55), (105, 88), (78, 100)]
    g2 = [(210, 70), (240, 58), (250, 92), (218, 98)]
    g3 = [(140, 185), (168, 172), (178, 205), (146, 212)]
    dots = ""
    for grp in (g1, g2, g3):
        dots += "".join(f'<circle cx="{x}" cy="{y}" r="7"/>' for x, y in grp)
    return (f'<g fill="#fff" opacity=".9">{dots}</g>'
            '<g fill="none" stroke="#fff" stroke-width="2.5" opacity=".55">'
            '<ellipse cx="88" cy="78" rx="42" ry="38"/><ellipse cx="230" cy="79" rx="42" ry="38"/>'
            '<ellipse cx="158" cy="193" rx="42" ry="38"/></g>')


def _svg_margin():
    return ('<g stroke="#fff" stroke-width="3" opacity=".9"><path d="M40 220 L280 70"/></g>'
            '<g stroke="#fff" stroke-width="2" opacity=".45" stroke-dasharray="7 5">'
            '<path d="M40 180 L280 30"/><path d="M40 260 L280 110"/></g>'
            '<g fill="#fff" opacity=".92"><circle cx="105" cy="90" r="7"/>'
            '<circle cx="160" cy="70" r="7"/><circle cx="95" cy="140" r="7"/></g>'
            '<g fill="none" stroke="#fff" stroke-width="2.5" opacity=".92">'
            '<rect x="150" y="185" width="14" height="14"/><rect x="215" y="145" width="14" height="14"/>'
            '<rect x="100" y="215" width="14" height="14"/></g>')


def _svg_map():
    cells = ""
    for i in range(3):
        for j in range(4):
            cells += (f'<rect x="{30 + j * 70}" y="{50 + i * 62}" width="56" height="46" rx="6" '
                      f'fill="none" stroke="#fff" stroke-width="2.5" opacity=".7"/>')
    return (f'<g>{cells}</g>'
            '<g fill="#fff" opacity=".85"><rect x="30" y="50" width="56" height="46" rx="6"/>'
            '<rect x="170" y="112" width="56" height="46" rx="6"/></g>')


def _svg_bias():
    return ('<g stroke="#fff" fill="none" stroke-width="3" opacity=".85">'
            '<path d="M35 90 Q120 235 285 205"/></g>'
            '<g stroke="#fff" fill="none" stroke-width="2.5" opacity=".55">'
            '<path d="M35 225 Q140 205 285 60"/></g>'
            '<g stroke="#fff" fill="none" stroke-width="3.5" opacity=".95">'
            '<path d="M35 70 Q140 210 285 55"/></g>'
            '<g fill="#fff" opacity=".95"><circle cx="152" cy="176" r="8"/></g>'
            '<g stroke="#fff" stroke-width="2" opacity=".4" stroke-dasharray="4 4">'
            '<path d="M152 176 V245"/></g>')


def _svg_net():
    """4 → 5 → 3 → 1 的前饋網路。層與層之間全連接，正好對上第 10 章的主角。"""
    x1, x2, x3, x4 = 42, 128, 214, 288
    l1, l2, l3 = [60, 110, 160, 210], [45, 90, 135, 180, 225], [85, 135, 185]
    edges = "".join(f'<path d="M{x1} {a} L{x2} {b}"/>' for a in l1 for b in l2)
    edges += "".join(f'<path d="M{x2} {a} L{x3} {b}"/>' for a in l2 for b in l3)
    edges += "".join(f'<path d="M{x3} {a} L{x4} 135"/>' for a in l3)
    nodes = "".join(f'<circle cx="{x1}" cy="{y}" r="9"/>' for y in l1)
    nodes += "".join(f'<circle cx="{x2}" cy="{y}" r="9"/>' for y in l2)
    nodes += "".join(f'<circle cx="{x3}" cy="{y}" r="9"/>' for y in l3)
    nodes += f'<circle cx="{x4}" cy="135" r="11"/>'
    return (f'<g stroke="#fff" stroke-width="1.5" fill="none" opacity=".35">{edges}</g>'
            f'<g fill="#fff" opacity=".92">{nodes}</g>')


# ── 十一章（前十章是授課順序，第 11 頁是課程沒教的補充章）──────────────────
def _svg_table():
    """先備 P4：一張表，表頭與一個欄位被選中。"""
    head = "".join(f'<rect x="{40 + c * 72}" y="46" width="64" height="26" rx="4"/>'
                   for c in range(4))
    body = "".join(f'<rect x="{40 + c * 72}" y="{80 + r * 32}" width="64" height="24" rx="3"/>'
                   for r in range(5) for c in range(4))
    col = "".join(f'<rect x="{40 + 2 * 72}" y="{80 + r * 32}" width="64" height="24" rx="3"/>'
                  for r in range(5))
    return (f'<g fill="#fff" opacity=".9">{head}</g>'
            f'<g fill="#fff" opacity=".26">{body}</g>'
            f'<g fill="#fff" opacity=".85">{col}</g>')


def _svg_chart():
    """先備 P5：一組長條與一條曲線。"""
    bars = "".join(f'<rect x="{44 + i * 46}" y="{210 - h}" width="34" height="{h}" rx="3"/>'
                   for i, h in enumerate([60, 96, 138, 170, 132, 88]))
    return (f'<g fill="#fff" opacity=".55">{bars}</g>'
            '<path d="M44 176 C 110 150, 150 92, 200 66 S 280 78, 316 118" '
            'stroke="#fff" stroke-width="3.5" fill="none" opacity=".95"/>'
            '<g stroke="#fff" stroke-width="3" opacity=".8">'
            '<path d="M34 214 H330"/><path d="M34 214 V40"/></g>')


def _svg_pipe():
    """先備 P6：資料流過三個方塊。"""
    boxes = "".join(f'<rect x="{34 + i * 106}" y="112" width="86" height="52" rx="8"/>'
                    for i in range(3))
    arrows = "".join(f'<path d="M{124 + i * 106} 138 H{136 + i * 106}"/>' for i in range(2))
    return (f'<g fill="#fff" opacity=".78">{boxes}</g>'
            f'<g stroke="#fff" stroke-width="3.5" opacity=".9">{arrows}</g>'
            '<g stroke="#fff" stroke-width="3" fill="none" opacity=".7">'
            '<path d="M356 138 H392"/><path d="M392 138 l-12 -8 v16 z" fill="#fff"/></g>'
            '<g fill="#fff" opacity=".5">'
            '<circle cx="60" cy="70" r="7"/><circle cx="88" cy="58" r="7"/>'
            '<circle cx="116" cy="76" r="7"/></g>')


def _svg_code():
    """先備 P1：幾行長短不一的程式碼。"""
    lines = [(46, 210), (66, 150), (66, 176), (46, 128), (46, 232), (66, 168)]
    rows = "".join(
        f'<rect x="{x}" y="{54 + i * 30}" width="{w}" height="14" rx="7"/>'
        for i, (x, w) in enumerate(lines))
    return (f'<g fill="#fff" opacity=".62">{rows}</g>'
            '<g fill="#fff" opacity=".9">'
            '<rect x="46" y="234" width="96" height="14" rx="7"/></g>'
            '<g stroke="#fff" stroke-width="3" opacity=".5">'
            '<path d="M30 40 V262"/></g>')


def _svg_flow():
    """先備 P2：一個判斷、兩條分支、一個迴圈。"""
    return ('<g stroke="#fff" stroke-width="3" fill="none" opacity=".85">'
            '<path d="M180 46 V78"/><path d="M120 108 H80 V160"/>'
            '<path d="M240 108 H280 V160"/><path d="M180 138 V240"/>'
            '<path d="M80 190 H280 V190"/></g>'
            '<g fill="#fff" opacity=".9">'
            '<path d="M180 78 L240 108 L180 138 L120 108 Z"/>'
            '<rect x="52" y="160" width="56" height="30" rx="5"/>'
            '<rect x="252" y="160" width="56" height="30" rx="5"/>'
            '<circle cx="180" cy="252" r="13"/></g>')


def _svg_gear():
    """課前準備 00B：一個齒輪與一個核取清單。"""
    teeth = "".join(
        f'<rect x="{158 + 0}" y="{40}" width="18" height="26" rx="3" '
        f'transform="rotate({i * 45} 167 140)"/>' for i in range(8))
    return (f'<g fill="#fff" opacity=".8">{teeth}'
            '<circle cx="167" cy="140" r="58"/></g>'
            '<circle cx="167" cy="140" r="28" fill="#2b3a67" opacity=".9"/>'
            '<g stroke="#fff" stroke-width="4" fill="none" opacity=".9">'
            '<path d="M250 96 l 16 16 l 30 -32"/>'
            '<path d="M250 156 l 16 16 l 30 -32"/>'
            '<path d="M250 216 l 16 16 l 30 -32"/></g>')


def _svg_spark():
    """課前準備 00A：一顆腦與一個問號。"""
    return ('<g stroke="#fff" stroke-width="3.5" fill="none" opacity=".85">'
            '<path d="M120 96 C 96 96, 84 118, 92 138 C 76 152, 84 180, 106 184 '
            'C 110 206, 142 212, 156 196 L 156 96 Z"/>'
            '<path d="M156 96 C 180 96, 192 118, 184 138 C 200 152, 192 180, 170 184 '
            'C 166 206, 156 208, 156 196"/>'
            '<path d="M124 128 h 22 M132 158 h 20 M170 128 h 14"/></g>'
            '<g fill="#fff" opacity=".92">'
            '<path d="M248 108 c 0 -18 30 -18 30 0 c 0 14 -15 12 -15 28 h -12 '
            'c 0 -22 15 -18 15 -28 c 0 -8 -18 -8 -18 0 z"/>'
            '<circle cx="257" cy="156" r="7"/></g>')


def _svg_dialog():
    """先備 P7：兩個對話框，一個被打勾、一個被畫叉。"""
    return ('<g fill="#fff" opacity=".8">'
            '<path d="M40 60 h 180 a 8 8 0 0 1 8 8 v 56 a 8 8 0 0 1 -8 8 h -140 '
            'l -24 22 v -22 h -16 a 8 8 0 0 1 -8 -8 v -56 a 8 8 0 0 1 8 -8 z"/></g>'
            '<g fill="#fff" opacity=".55">'
            '<path d="M120 168 h 180 a 8 8 0 0 1 8 8 v 56 a 8 8 0 0 1 -8 8 h -16 '
            'l -24 22 v -22 h -140 a 8 8 0 0 1 -8 -8 v -56 a 8 8 0 0 1 8 -8 z"/></g>'
            '<g stroke="#2b3a67" stroke-width="5" fill="none" stroke-linecap="round">'
            '<path d="M74 92 l 14 14 l 28 -30"/></g>'
            '<g stroke="#2b3a67" stroke-width="5" fill="none" stroke-linecap="round">'
            '<path d="M244 190 l 30 30 M274 190 l -30 30"/></g>')


PAGES = [
    # ── 課前準備（group="pre"）：定位、環境、AI 協作 ────────
    Page(
        n=12, stem="00a_why_code", slug="LEARNING WITH AI", title_en="Learning with AI",
        h1='和 <span class="orange">AI 一起學資料分析</span>',
        plain="AI 時代的資料分析學習迴圈",
        subtitle="課前準備 A — 選讀，不列入評分",
        formula="提出想法｜動手嘗試｜觀察證據｜修正理解｜AI 協助學習｜練習自己的判斷",
        deck="", deck_pages=0, lab="",
        islp=0, islp_label="課前 · AI 學習迴圈", esl_label="",
        playlist="",
        hero_svg=_svg_spark(),
        group="pre",
        kind="prep", data_key="prep_00a_why_code", src_labs=(1,),
        ex_links=[("🔗 本站章節總覽", "index.html"),
                  ("🔗 AI 協作實務", "00c_ai_assisted.html"),
                  ("🔗 CHIWORK 2024 研究", "https://www.microsoft.com/en-us/research/publication/its-like-a-rubber-duck-that-talks-back-understanding-generative-ai-assisted-data-analysis-workflows-through-a-participatory-prompting-study/")],
        secs=[
            Sec("prologue", "AI 協助資料分析", "AI 在資料分析流程中能提供哪些協助",
                "先備 · AI 與資料分析", kicker="PROLOGUE · 開場"),
            Sec("loop", "學習迴圈", "從想法到嘗試，觀察證據並修正理解",
                "先備 · 學習迴圈"),
            Sec("workflow", "每一步都能請 AI 幫忙", "從找資料到報告草稿，安排你與 AI 的分工",
                "先備 · 資料分析流程"),
            Sec("judgment", "練習資料判斷", "理解資料的意義，檢查分析流程",
                "AI-Stats §11"),
            Sec("habits", "把 AI 留在迴圈裡", "五個練習習慣，幫助你理解 AI 提供的建議",
                "先備 · 學習策略"),
        ],
    ),
    Page(
        n=13, stem="00b_setup", slug="SETUP", title_en="Setup",
        h1='把<span class="blue">環境</span>準備好：跑出第一張圖',
        plain="環境安裝",
        subtitle="課前準備 B — 選讀，不列入評分",
        formula="平時可用 Colab｜期中使用電腦教室電腦｜本機版本對齊教室｜確認 kernel 與資料路徑｜考前完整重跑練習",
        deck="", deck_pages=0, lab="",
        islp=0, islp_label="課前 · 環境安裝", esl_label="",
        playlist="",
        hero_svg=_svg_gear(),
        group="pre",
        kind="prep", data_key="prep_00b_setup", src_labs=(1, 2),
        ex_links=[("🔗 電腦教室版本清單", CLASSROOM_PACKAGES),
                  ("🔗 Google Colab", "https://colab.research.google.com/"),
                  ("🔗 conda 環境管理",
                   "https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html"),
                  ("🔗 ISLP 套件", "https://islp.readthedocs.io/")],
        secs=[
            Sec("prologue", "完成第一個練習", "從開啟筆記本到跑出第一張圖",
                "課程 Lab Ch1 · 儲存格 3–5", kicker="PROLOGUE · 開場"),
            Sec("colab", "Colab 工作流", "筆記本會保存，執行階段會回收",
                "課程 Lab Ch1 · 儲存格 3–4"),
            Sec("imports", "匯入套件", "先執行本份筆記本的匯入程式",
                "課程 Lab Ch2 · 儲存格 3–8"),
            Sec("data", "資料放哪裡", "掛 Drive、或直接讀網址",
                "課程 Lab Ch2 · 儲存格 183–187"),
            Sec("local", "本機與考前準備", "期中使用電腦教室電腦，本機練習建議對齊版本",
                "conda 文件 · 環境管理"),
            Sec("trouble", "跑不動的時候", "四種常見執行問題與檢查方法",
                "Python 文件 · 例外"),
        ],
    ),
    Page(
        n=20, stem="00c_ai_assisted", slug="AI-ASSISTED STATISTICS", title_en="AI-Assisted Statistics",
        h1='用 <span class="orange">AI</span> 做統計分析：從提問到核對結果',
        plain="AI 輔助統計分析：從提問到驗證",
        subtitle="課前準備 C — 選讀，不列入評分",
        formula="任務分流｜補足脈絡｜拆成小步｜執行與核對｜檢查假設與反例｜留下可重現紀錄",
        deck="", deck_pages=0, lab="",
        islp=0, islp_label="課前 · AI 協作", esl_label="",
        playlist="",
        hero_svg=_svg_dialog(),
        group="pre",
        kind="prep", data_key="prep_00c_ai_assisted", src_labs=(1, 3, 5),
        nav_next="introduction",
        ex_links=[("🔗 本站章節總覽", "index.html"),
                  ("🔗 資料分析學習迴圈", "00a_why_code.html"),
                  ("🔗 AI 協作參考書：作者程式與資料", "https://github.com/gedeck/ai-assisted-statistics-for-data-scientists")],
        secs=[
            Sec("prologue", "責任界線", "AI 協作中的統計判斷與責任",
                "AI-Stats §Preface", kicker="PROLOGUE · 開場"),
            Sec("triage", "先做任務分流", "依任務的驗證方式與所需判斷安排分工",
                "AI-Stats §11"),
            Sec("context", "說清楚分析問題", "方向、格式、例子、資料脈絡與驗收標準",
                "AI-Stats §10"),
            Sec("iterate", "小步生成與修正", "一次做一件可執行、可檢查的事",
                "AI-Stats §11"),
            Sec("verify", "核對統計解讀", "查定義、單位、假設、不確定性與資料流程",
                "AI-Stats §11"),
            Sec("record", "反駁、紀錄與資料安全", "留下能重現、能追責的分析紀錄",
                "AI-Stats §11"),
        ],
    ),
    # ── 正課十一章（group="core"，依授課順序） ────────────────
    Page(
        n=1, stem="introduction", slug="INTRODUCTION & EDA", title_en="Introduction to Statistical Learning and EDA",
        h1='<span class="blue">統計學習導論</span>與 <span class="green">EDA</span>',
        plain="統計學習導論與 EDA",
        subtitle="從新聞與核心想法，到探索式資料分析 — 對應講義 01",
        formula="新聞與應用｜領域區別｜推薦系統｜10 個重要想法｜先看資料再建模｜22 個資料集",
        deck="01_Introduction.pdf", deck_pages=39, lab="Ch01-lab-zh.ipynb",
        islp=1, islp_label="ISLP Ch.1", esl_label="",
        playlist="PLHNZtBNWQ-85VI_x3duODyfYm4r3pOl3e",
        hero_svg=_svg_map(),
        group="core",
        nav_prev="00c_ai_assisted",
        deck_url="https://github.com/phonchi/nsysu-math524/blob/main/static_files/presentations/01_Introduction.pdf",
        legacy_anchors=("regcls", "predinfer", "notation"),
        page_css=".w01-catalog{min-width:660px;} .w01-ideas{min-width:640px;} #datasets .viz-layout>div{min-width:0;} .w01-catalog th{white-space:nowrap;} .w01-figure-scroll{overflow-x:auto;max-width:100%;} .w01-figure-scroll .viz-svg{min-width:620px;height:auto;} .w01-figure-scroll .axlab{font-size:12px;} .w01-figure-scroll .axtitle{font-size:13px;}",
        secs=[
            Sec("prologue", "這門課的重點", "先理解問題，再用資料檢查想法",
                "講義 01 · p.6、21", kicker="PROLOGUE · 開場"),
            Sec("news", "新聞與應用", "從新聞看統計學習能完成的工作", "講義 01 · p.9–15"),
            Sec("slvsml", "相關領域的分工", "統計、機器學習與資料科學：重疊中的不同側重", "講義 01 · p.7、16–19"),
            Sec("supervised", "基本學習問題", "先問：有什麼資料，想回答什麼？", "講義 01 · p.20–22|ISLP §2.1"),
            Sec("recommendation", "推薦系統", "Netflix：推薦系統是一種應用任務", "講義 01 · p.23–24"),
            Sec("ideas", "10 個重要想法", "從統計到 AI：十個想法各解決什麼問題？", "講義 01 · p.25"),
            Sec("eda", "EDA 入門", "先看資料：資料表、摘要與選圖", "講義 01 · p.26–29"),
            Sec("datasets", "22 個資料集與讀圖", "課程資料集總表與五組讀圖練習", "講義 01 · p.30–35|ISLP Ch.1"),
            Sec("toolchain", "繼續學習", "從這一頁走向 Lab 與後續章節", "講義 01 · p.36、38–39"),
        ],
    ),
    Page(
        n=2, stem="statistical_learning", slug="STATISTICAL LEARNING", title_en="Statistical Learning",
        h1='<span class="blue">f</span> 是什麼、<span class="orange">誤差</span>從哪來',
        plain="統計學習的基本框架",
        subtitle="ISLP 第 2 章 — 對應講義 02",
        formula="Y = f(X) + ε｜可縮減 vs 不可縮減｜訓練 MSE vs 測試 MSE｜偏差² + 變異 + Var(ε)｜Bayes 分類器｜KNN",
        deck="02_Statistical_Learning.pdf", deck_pages=41, lab="Ch02-statlearn-lab-zh.ipynb",
        islp=2, islp_label="ISLP Ch.2", esl_label="ESL Ch.2",
        playlist="PLHNZtBNWQ-87OBZ1ggt-ZMj3gK2LfUufD",
        hero_svg=_svg_bias(),
        group="core",
        secs=[
            Sec("prologue", "為什麼要估計 f", "把「學習」寫成一條式子：Y = f(X) + ε",
                "ISLP §2.1|講義 02 · p.2–9", kicker="PROLOGUE · 開場"),
            Sec("irreducible", "兩種誤差", "可縮減與<strong>不可縮減</strong>誤差的來源",
                "ISLP §2.1.1|講義 02 · p.10–15"),
            Sec("parametric", "參數式與非參數式", "參數式與非參數式方法如何描述資料關係", "ISLP §2.1.2|講義 02 · p.16–21"),
            Sec("tradeoff", "彈性與可解釋性", "模型彈性、預測表現與可解釋性", "ISLP §2.1.3|講義 02 · p.22–26"),
            Sec("mse", "訓練與測試 MSE", "用訓練 MSE 與測試 MSE 比較模型彈性", "ISLP §2.2.1|講義 02 · p.27–29"),
            Sec("biasvar", "偏差–變異拆解", "把測試 MSE 拆成三塊：偏差²、變異、不可縮減誤差",
                "ISLP §2.2.2|ESL §7.3 · 進階"),
            Sec("bayes", "Bayes 分類器與 KNN", "分類設定：Bayes 錯誤率與 KNN 的 K 如何影響預測",
                "ISLP §2.2.3|講義 02 · p.31–41"),
        ],
    ),
    Page(
        n=3, stem="linear_regression", slug="LINEAR REGRESSION", title_en="Linear Regression",
        h1='<span class="blue">線性迴歸</span>：從基本模型理解變數關係',
        plain="線性迴歸",
        subtitle="ISLP 第 3 章 — 對應講義 03",
        formula="β̂ = (XᵀX)⁻¹Xᵀy｜RSS｜SE 與 t 檢定｜F 檢定｜R² 與 RSE｜交互作用｜VIF",
        deck="03_Regression.pdf", deck_pages=70, lab="Ch03-linreg-lab-zh.ipynb",
        islp=3, islp_label="ISLP Ch.3", esl_label="ESL §3.1–3.3",
        playlist="PLHNZtBNWQ-87GVk0NXHo19GPagNc7g-ba",
        hero_svg=_svg_scatter(), bankquiz=True,
        group="core",
        secs=[
            Sec("prologue", "四個分析問題", "Advertising 資料要回答的四件事",
                "ISLP §3 開頭|講義 03 · p.2–3", kicker="PROLOGUE · 開場"),
            Sec("slr", "簡單線性迴歸", "最小平方法：讓 RSS 最小的那條線",
                "ISLP §3.1.1|講義 03 · p.4–6"),
            Sec("inference", "係數的不確定性", "SE、信賴區間與 t 檢定：這個斜率可信嗎",
                "ISLP §3.1.2|講義 03 · p.7–11"),
            Sec("accuracy", "模型準確度", "RSE 與 R²：擬合得好不好", "ISLP §3.1.3|講義 03 · p.12–13"),
            Sec("mlr", "多元迴歸與 F 檢定", "同時放進多個變數：F 檢定在問什麼",
                "ISLP §3.2|講義 03 · p.15–24"),
            Sec("qualitative", "質性變數與交互作用", "類別變數怎麼進模型，交互作用又是什麼",
                "ISLP §3.3.1–3.3.2|講義 03 · p.25–36"),
            Sec("problems", "六個潛在問題", "非線性、殘差相關、異質變異、離群、高槓桿、共線性",
                "ISLP §3.3.3|講義 03 · p.37–52"),
            Sec("vsknn", "與 KNN 的比較", "比較線性模型與 KNN 的適用情境", "ISLP §3.5|講義 03 · p.53–58"),
        ],
    ),
    Page(
        n=4, stem="classification", slug="CLASSIFICATION", title_en="Classification",
        h1='<span class="orange">分類</span>：從機率到決策邊界',
        plain="分類",
        subtitle="ISLP 第 4 章 — 對應講義 04",
        formula="logit(p) = β₀ + βᵀx｜勝算比｜Bayes 定理｜LDA｜QDA｜Naive Bayes｜混淆矩陣｜ROC 與 AUC",
        deck="04_Classification.pdf", deck_pages=61, lab="Ch04-classification-lab-zh.ipynb",
        islp=4, islp_label="ISLP Ch.4", esl_label="ESL §4.1–4.4",
        playlist="PLHNZtBNWQ-86o54cIAZDsEQH85i1Sf8XT",
        hero_svg=_svg_boundary(), bankquiz=True,
        group="core",
        secs=[
            Sec("prologue", "為什麼不用迴歸", "把類別編成 1、2、3 會出什麼事",
                "ISLP §4.2|講義 04 · p.2–6", kicker="PROLOGUE · 開場"),
            Sec("logistic", "邏輯斯迴歸", "勝算、log-odds 與那條 S 形曲線", "ISLP §4.3|講義 04 · p.7–13"),
            Sec("multinomial", "多元與多類別", "多個預測變數、多於兩類要怎麼做",
                "ISLP §4.3.4–4.3.5|講義 04 · p.11–13"),
            Sec("lda", "LDA", "換個方向想：先建各類的機率模型再用 Bayes 定理",
                "ISLP §4.4.1–4.4.3|講義 04 · p.14–29"),
            Sec("qda", "QDA 與 Naive Bayes", "共變異數要不要共用？獨立假設又幫了什麼",
                "ISLP §4.4.3–4.4.4|講義 04 · p.30–37"),
            Sec("threshold", "閾值、混淆矩陣與 ROC", "調整 0.5 閾值，觀察各類錯誤如何改變",
                "ISLP §4.4.2|講義 04 · p.20–23"),
            Sec("compare", "方法的解析比較", "五種分類方法的假設與函數形式",
                "ISLP §4.5|講義 04 · p.38–48"),
            Sec("poisson", "Poisson 迴歸與 GLM", "計數資料：把線性模型推廣成 GLM",
                "ISLP §4.6|講義 04 · p.49–56", eslx=True),
        ],
    ),
    Page(
        n=5, stem="resampling_methods", slug="RESAMPLING", title_en="Resampling Methods",
        h1='<span class="green">重抽樣</span>：用切分與重抽評估模型及估計量',
        plain="重抽樣方法",
        subtitle="ISLP 第 5 章 — 對應講義 05",
        formula="驗證集｜LOOCV｜k-fold CV｜偏差–變異取捨｜Bootstrap｜1−(1−1/n)ⁿ → 0.632",
        deck="05_Resampling_Methods.pdf", deck_pages=42, lab="Ch05-resample-lab-zh.ipynb",
        islp=5, islp_label="ISLP Ch.5", esl_label="ESL §7.1–7.4、7.10–7.11",
        playlist="PLHNZtBNWQ-84VdV4eQXOMacVAIF065luN",
        hero_svg=_svg_folds(),
        group="core",
        secs=[
            Sec("prologue", "訓練與測試誤差", "用重抽樣評估模型在新資料上的表現",
                "ISLP §5 開頭|講義 05 · p.2–6", kicker="PROLOGUE · 開場"),
            Sec("validation", "驗證集法", "驗證集法：觀察資料切分帶來的變動",
                "ISLP §5.1.1|講義 05 · p.7–9"),
            Sec("loocv", "LOOCV", "每次保留一筆資料的交叉驗證",
                "ISLP §5.1.2|講義 05 · p.10–12"),
            Sec("kfold", "k-fold CV", "折成 k 份輪流當驗證集", "ISLP §5.1.3|講義 05 · p.13–15"),
            Sec("kbias", "k 該取多少", "k 的偏差–變異取捨：為什麼實務上取 5 或 10",
                "ISLP §5.1.4|講義 05 · p.16"),
            Sec("cvclass", "分類問題上的 CV", "把 MSE 換成錯誤率，其餘一樣",
                "ISLP §5.1.5|講義 05 · p.17–18"),
            Sec("cvwrong", "CV 的對與錯", "特徵選擇與交叉驗證的正確順序",
                "ESL §7.10.2|講義 05 · p.19–21"),
            Sec("bootstrap", "Bootstrap", "有放回地重抽：直接把標準誤算出來",
                "ISLP §5.2|講義 05 · p.22–35"),
        ],
    ),
    Page(
        n=6, stem="model_selection", slug="MODEL SELECTION", title_en="Model Selection & Regularization",
        h1='變數該<span class="orange">選</span>，還是該<span class="purple">縮</span>？',
        plain="線性模型選擇與正則化",
        subtitle="ISLP 第 6 章 — 對應講義 06",
        formula="最佳子集｜逐步選擇｜Cp｜AIC｜BIC｜調整後 R²｜Ridge L2｜Lasso L1｜PCR｜PLS",
        deck="06_Linear_Model_Selection.pdf", deck_pages=70, lab="Ch06-varselect-lab-zh.ipynb",
        islp=6, islp_label="ISLP Ch.6", esl_label="ESL §3.3–3.6、§7.1–7.7",
        playlist="PLHNZtBNWQ-86msOZdtaMyKHwk2mWpOWmu",
        hero_svg=_svg_shrink(),
        group="core",
        secs=[
            Sec("prologue", "變數多時的模型選擇", "最小平方法什麼時候會不夠用",
                "ISLP §6 開頭|講義 06 · p.2–5", kicker="PROLOGUE · 開場"),
            Sec("subset", "子集選擇", "如何比較 2^p 個候選模型：最佳子集與逐步選擇",
                "ISLP §6.1|講義 06 · p.6–14"),
            Sec("criteria", "選模型的準則", "Cp、AIC、BIC、調整後 R²：懲罰項在做什麼",
                "ISLP §6.1.3|講義 06 · p.15–24"),
            Sec("onese", "用 CV 選模型", "驗證與交叉驗證，以及 one-standard-error 規則",
                "ISLP §6.1.3|講義 06 · p.22–24"),
            Sec("ridge", "Ridge 迴歸", "把係數往零壓：L2 懲罰與係數路徑",
                "ISLP §6.2.1|講義 06 · p.25–32"),
            Sec("lasso", "Lasso 與稀疏性", "L1 為什麼會把係數壓成剛好 0", "ISLP §6.2.2|講義 06 · p.33–41"),
            Sec("lambda", "怎麼選 λ", "調整參數也要用 CV 選", "ISLP §6.2.3|講義 06 · p.42–45"),
            Sec("pcr", "主成分迴歸 PCR", "先降維再迴歸：方向由 X 自己決定",
                "ISLP §6.3.1|講義 06 · p.46–55"),
            Sec("pls", "偏最小平方 PLS", "讓 y 也參與挑方向", "ISLP §6.3.2|講義 06 · p.56–58"),
            Sec("highdim", "高維度的陷阱", "p 逼近 n 時，如何判讀訓練 R²",
                "ISLP §6.4|講義 06 · p.59–66"),
        ],
    ),
    Page(
        n=7, stem="unsupervised_learning", slug="UNSUPERVISED", title_en="Unsupervised Learning",
        h1='沒有 <span class="orange">y</span> 的時候，還能學到什麼？',
        plain="非監督式學習",
        subtitle="ISLP 第 12 章 — 對應講義 12",
        formula="PCA｜負荷量與得分｜PVE｜Scree plot｜Biplot｜矩陣補全｜K-means｜階層式分群｜Dendrogram",
        deck="12_Unsupervised_learning.pdf", deck_pages=106, lab="Ch12-unsup-lab-zh.ipynb",
        islp=12, islp_label="ISLP Ch.12", esl_label="ESL §13.1–13.3、§14.1–14.3、§14.5–14.9",
        playlist="PLHNZtBNWQ-85BiSie5BdC-ElKcRw37fs1,PLHNZtBNWQ-87wNMJFe_UQj_DzsiHVZWkx",
        hero_svg=_svg_cluster(),
        group="core",
        secs=[
            Sec("prologue", "沒有標準答案", "沒有現成標籤，該怎麼評估找到的結構？",
                "ISLP §12.1|講義 12 · p.2–6", kicker="PROLOGUE · 開場"),
            Sec("pca", "主成分是什麼", "第一主成分：變異最大的那個方向",
                "ISLP §12.2.1|講義 12 · p.7–12"),
            Sec("biplot", "Biplot 怎麼讀", "USArrests：一張圖同時放州與變數",
                "ISLP §12.2.2|講義 12 · p.13–16"),
            Sec("lowrank", "另一種解釋", "主成分也是「最佳低維近似」", "ISLP §12.2.2|講義 12 · p.17–19"),
            Sec("pve", "PVE 與 scree plot", "要留幾個主成分？先看解釋了多少變異",
                "ISLP §12.2.3|講義 12 · p.20–22"),
            Sec("scaling", "尺度化與符號", "沒標準化就等於在比單位；符號翻掉不影響結論",
                "ISLP §12.2.4|講義 12 · p.23–28"),
            Sec("completion", "矩陣補全", "把缺失值當成主成分問題解", "ISLP §12.3|講義 12 · p.30–38"),
            Sec("kmeans", "K-means", "指派、更新、再指派：目標函數單調下降",
                "ISLP §12.4.1|講義 12 · p.54–66"),
            Sec("hclust", "階層式分群", "不用先決定 K：dendrogram 與四種 linkage",
                "ISLP §12.4.2|講義 12 · p.67–90"),
            Sec("practical", "分群的實務問題", "要不要標準化、離群值怎麼辦、結果穩不穩",
                "ISLP §12.4.3|講義 12 · p.91–98"),
            Sec("manifold", "流形學習與 t-SNE", "非線性降維：t-SNE 的讀圖方式與解讀範圍",
                "講義 12 · p.39–53|ESL §14.9 · 進階", eslx=True),
        ],
    ),
    Page(
        n=8, stem="beyond_linearity", slug="BEYOND LINEARITY", title_en="Moving Beyond Linearity",
        h1='<span class="purple">彎</span>得剛剛好：從多項式到 GAM',
        plain="超越線性",
        subtitle="ISLP 第 7 章 — 對應講義 07",
        formula="多項式｜階梯函數｜基底函數｜迴歸樣條｜自然樣條｜平滑樣條｜局部迴歸｜GAM",
        deck="07_Moving_Beyond_Linearity.pdf", deck_pages=54, lab="Ch07-nonlin-lab-zh.ipynb",
        islp=7, islp_label="ISLP Ch.7", esl_label="ESL §5.1–5.7、§6.1–6.3、§9.1",
        playlist="PLHNZtBNWQ-87lLBZoc83Gwofk8a1gkvfu",
        hero_svg=_svg_curves(),
        group="core",
        secs=[
            Sec("prologue", "線性不夠用", "以可解讀的函數描述非線性關係",
                "ISLP §7 開頭|講義 07 · p.2–4", kicker="PROLOGUE · 開場"),
            Sec("poly", "多項式迴歸", "高次多項式的配適與邊界變動", "ISLP §7.1|講義 07 · p.5–7"),
            Sec("step", "階梯函數", "把 x 切段，每段給一個常數", "ISLP §7.2|講義 07 · p.8–10"),
            Sec("basis", "基底函數框架", "用基底函數表示多項式與階梯函數",
                "ISLP §7.3|講義 07 · p.10"),
            Sec("splines", "迴歸樣條", "分段三次多項式，在節點上接得平滑",
                "ISLP §7.4.1–7.4.3|講義 07 · p.11–20"),
            Sec("natural", "自然樣條", "自然樣條：以線性約束處理兩端的配適",
                "ISLP §7.4.4–7.4.5|講義 07 · p.21–23"),
            Sec("smooth", "平滑樣條", "換個想法：直接懲罰彎曲程度，用有效自由度描述複雜度",
                "ISLP §7.5|講義 07 · p.24–27"),
            Sec("loess", "局部迴歸", "只看附近的點，加權配一條線", "ISLP §7.6|講義 07 · p.28–33"),
            Sec("gam", "GAM", "每個變數各配一條曲線，再加起來", "ISLP §7.7|講義 07 · p.34–48"),
        ],
    ),
    Page(
        n=9, stem="tree_based_methods", slug="TREES & ENSEMBLES", title_en="Tree-Based Methods & Ensembles",
        h1='從<span class="green">決策樹</span>到<span class="green">集成模型</span>',
        plain="樹狀方法與集成學習",
        subtitle="ISLP 第 8 章 — 對應講義 08（含集成學習那一週）",
        formula="遞迴二元分裂｜成本複雜度剪枝｜Gini 與交叉熵｜Bagging｜OOB｜Random Forest｜Boosting｜XGBoost",
        deck="08_Tree-Based_Methods.pdf", deck_pages=80, lab="Ch08-baggboost-lab-zh.ipynb",
        islp=8, islp_label="ISLP Ch.8",
        esl_label="ESL §9.2、§8.7–8.8、§10.1–10.14、§15.1–15.3",
        playlist="PLHNZtBNWQ-87ZC7BDwkB-bgSbqggcWp6T,PLHNZtBNWQ-84JjvtG4zgpxTPF3HDJBnfR",
        hero_svg=_svg_tree(), bankquiz=True,
        group="core",
        secs=[
            Sec("prologue", "樹如何預測", "把特徵空間切成方塊，每塊給一個預測值",
                "ISLP §8.1|講義 08 · p.2–9", kicker="PROLOGUE · 開場"),
            Sec("grow", "迴歸樹的生長", "遞迴二元分裂：每次選擇讓 RSS 降低最多的分裂",
                "ISLP §8.1.1|講義 08 · p.10–14"),
            Sec("prune", "剪枝", "先長太大再剪：成本複雜度與 α", "ISLP §8.1.1|講義 08 · p.15–21"),
            Sec("classtree", "分類樹", "Gini 指數與交叉熵：為什麼不用錯誤率當分裂準則",
                "ISLP §8.1.2|講義 08 · p.22–27"),
            Sec("vslinear", "樹 vs 線性模型", "哪一種對，看真實邊界長什麼樣",
                "ISLP §8.1.3–8.1.4|講義 08 · p.28–29"),
            Sec("why", "為什麼要集成", "投票與大數法則：一群弱分類器怎麼變強",
                "講義 08 · p.30–31|ESL §16.1 · 進階"),
            Sec("bagging", "Bagging 與 OOB", "重抽樣造很多棵樹再平均；利用袋外樣本評估",
                "ISLP §8.2.1|講義 08 · p.32–37"),
            Sec("rf", "Random Forest", "每次分裂只看 m 個變數：觀察樹間相關與預測表現",
                "ISLP §8.2.2|講義 08 · p.38–42"),
            Sec("boosting", "Boosting", "慢慢學：AdaBoost 與梯度提升",
                "ISLP §8.2.3|講義 08 · p.43–51|ESL §10.1–10.10 · 進階"),
            Sec("modern", "XGBoost 與後繼者", "XGBoost、LightGBM、CatBoost 與該調的超參數",
                "講義 08 · p.52–61|ESL §10.10–10.14 · 進階", eslx=True),
            Sec("stacking", "Stacking 與 BART", "變數重要度、堆疊法，以及貝氏版的加法樹",
                "ISLP §8.2.4|講義 08 · p.66–79", eslx=True),
        ],
    ),
    Page(
        n=10, stem="support_vector_machines", slug="SVM", title_en="Support Vector Machines",
        h1='<span class="blue">最大邊界</span>與<span class="purple">核技巧</span>',
        plain="支持向量機",
        subtitle="ISLP 第 9 章 — 對應講義 09",
        formula="超平面｜最大邊界｜支持向量｜軟邊界 C｜Hinge loss｜核技巧｜多項式核｜RBF 核",
        deck="09_Support_Vector_Machines.pdf", deck_pages=40, lab="Ch09-svm-lab-zh.ipynb",
        islp=9, islp_label="ISLP Ch.9", esl_label="ESL §6.6–6.9、§12.1–12.3",
        playlist="PLHNZtBNWQ-87bbEwPnJsJirQbdJpfPD5O",
        hero_svg=_svg_margin(),
        group="core",
        secs=[
            Sec("prologue", "用一刀分開", "超平面：把分類問題變成幾何問題",
                "ISLP §9.1|講義 09 · p.2–7", kicker="PROLOGUE · 開場"),
            Sec("maxmargin", "最大邊界分類器", "能分開的話，選離兩邊都最遠的那一刀",
                "ISLP §9.1.3–9.1.4|講義 09 · p.8–11"),
            Sec("soft", "軟邊界與 C", "不能完全分開時：允許犯錯，用 C 決定容忍度",
                "ISLP §9.2|講義 09 · p.12–23"),
            Sec("hinge", "Hinge loss", "為什麼只有支持向量會影響答案",
                "ISLP §9.5|ESL §12.3.2 · 進階"),
            Sec("kernel", "核技巧", "不用真的升維也能畫出彎的邊界", "ISLP §9.3|講義 09 · p.24–33"),
            Sec("multiclass", "多類別", "OVO 與 OVA：兩類的方法怎麼推廣", "ISLP §9.4|講義 09 · p.34–36"),
            Sec("vslogit", "與邏輯斯迴歸的關係", "兩個損失函數其實很像，差別在哪",
                "ISLP §9.5|講義 09 · p.37–39"),
        ],
    ),
    Page(
        n=11, stem="deep_learning", slug="DEEP LEARNING", title_en="Deep Learning",
        h1='<span class="orange">神經網路</span>：把非線性一層一層疊起來',
        plain="深度學習（補充）",
        subtitle="ISLP 第 10 章 — 本課未授課，補充自學",
        formula="隱藏層｜ReLU｜softmax｜卷積與池化｜RNN｜反向傳播＋SGD｜dropout｜雙下降",
        deck="", deck_pages=0, lab="",
        islp=10, islp_label="ISLP Ch.10 · 補充", esl_label="ESL Ch.11",
        playlist="",
        extra_pills=[("📓 ISLP 官方 Lab",
                      "https://github.com/intro-stat-learning/ISLP_labs/blob/"
                      "6bf6160a3dd180c6651ba06655b453e81f91dc20/Ch10-deeplearning-lab.ipynb")],
        hero_svg=_svg_net(),
        group="core",
        secs=[
            Sec("prologue", "先看它跟迴歸的關係", "從線性模型理解神經網路的隱藏層",
                "ISLP §10 開頭", kicker="PROLOGUE · 開場"),
            Sec("single", "單層神經網路", "一層隱藏層：非線性怎麼進來的",
                "ISLP §10.1|ESL §11.3"),
            Sec("multi", "多層與 MNIST", "疊第二層之後：softmax 與 235,146 個參數",
                "ISLP §10.2|ESL §11.4–11.6"),
            Sec("cnn", "卷積神經網路", "把「哪裡」的資訊丟掉一部分：卷積與池化",
                "ISLP §10.3"),
            Sec("rnn", "文件分類與 RNN", "文件分類中的詞袋表示與順序資訊",
                "ISLP §10.4|ISLP §10.5"),
            Sec("fitting", "怎麼配適", "反向傳播、SGD、dropout：神經網路的訓練流程",
                "ISLP §10.7|ESL §11.4 · 進階"),
            Sec("doubledesc", "雙下降與該不該用", "參數比樣本多還會變好？以及如何評估模型",
                "ISLP §10.8|ISLP §10.6"),
        ],
    ),
    # ── 附錄：Python 先備知識（group="appendix"，選讀查閱用） ────
    Page(
        n=14, stem="p1_python_basics", slug="PYTHON BASICS", title_en="Python Basics",
        h1='看得懂一段<span class="blue">統計程式</span>：Python 基礎',
        plain="Python 基礎",
        subtitle="先備知識 P1 — 選讀，不列入評分",
        formula="變數名稱與物件參照｜int float str bool｜串列與索引｜切片含頭不含尾｜字典是鍵值對｜f-string 與 format",
        deck="", deck_pages=0, lab="",
        islp=0, islp_label="先備 · Python 基礎", esl_label="",
        playlist="",
        hero_svg=_svg_code(),
        group="appendix",
        kind="prep", data_key="prep_p1_python_basics", src_labs=(2, 1),
        ex_links=[("🔗 Python 官方教學（中文）", "https://docs.python.org/zh-tw/3/tutorial/"),
                  ("🔗 內建型別", "https://docs.python.org/zh-tw/3/library/stdtypes.html"),
                  ("📓 Ch02 中文 Lab", "https://github.com/phonchi/nsysu-math524-2025/blob/main/"
                   "static_files/presentations/Ch02-statlearn-lab-zh.ipynb")],
        secs=[
            Sec("prologue", "第一行程式", "先讓一段課程 lab 的程式碼變得看得懂",
                "課程 Lab Ch2 · 儲存格 12–18", kicker="PROLOGUE · 開場"),
            Sec("var", "變數與型別", "變數名稱如何參照資料物件",
                "課程 Lab Ch2 · 儲存格 16–23"),
            Sec("list", "串列", "一排有順序的東西，從 0 開始數",
                "課程 Lab Ch2 · 儲存格 21–23"),
            Sec("slice", "切片", "起:迄:步長，而且<strong>迄不包含</strong>",
                "課程 Lab Ch2 · 儲存格 132–134"),
            Sec("dict", "字典", "透過鍵取得字典中的值",
                "課程 Lab Ch1 · 儲存格 19–26"),
            Sec("str", "字串與格式化", "把數字變成人看得懂的一行字",
                "課程 Lab Ch2 · 儲存格 236–244"),
        ],
    ),
    Page(
        n=15, stem="p2_flow_functions", slug="FLOW & FUNCTIONS", title_en="Flow and Functions",
        h1='讓程式<span class="orange">重複</span>與<span class="blue">分岔</span>：流程與函式',
        plain="流程與函式",
        subtitle="先備知識 P2 — 選讀，不列入評分",
        formula="if elif else｜& 與 and 不一樣｜for 與 zip｜def 與 return｜預設引數｜作用域｜讀懂 traceback",
        deck="", deck_pages=0, lab="",
        islp=0, islp_label="先備 · 流程與函式", esl_label="",
        playlist="",
        hero_svg=_svg_flow(),
        group="appendix",
        kind="prep", data_key="prep_p2_flow_functions", src_labs=(2, 5),
        ex_links=[("🔗 Python 控制流程",
                   "https://docs.python.org/zh-tw/3/tutorial/controlflow.html"),
                  ("🔗 例外處理", "https://docs.python.org/zh-tw/3/tutorial/errors.html"),
                  ("📓 Ch05 中文 Lab", "https://github.com/phonchi/nsysu-math524-2025/blob/main/"
                   "static_files/presentations/Ch05-resample-lab-zh.ipynb")],
        secs=[
            Sec("prologue", "為什麼要寫函式", "同一段程式碼貼三次，就是三個等著出錯的地方",
                "課程 Lab Ch5 · 儲存格 24–26", kicker="PROLOGUE · 開場"),
            Sec("cond", "條件與布林", "<code>&amp;</code> 與 <code>and</code> 的運算對象",
                "課程 Lab Ch2 · 儲存格 226–232"),
            Sec("loop", "迴圈", "for、range 與 zip：把同一件事做很多次",
                "課程 Lab Ch2 · 儲存格 236–240"),
            Sec("func", "函式", "def、參數、return：把一段流程封起來",
                "課程 Lab Ch5 · 儲存格 24–26"),
            Sec("scope", "預設引數與作用域", "函式裡看得到外面，外面看不到裡面",
                "課程 Lab Ch5 · 儲存格 59–61"),
            Sec("err", "讀懂錯誤訊息", "traceback 要從<strong>最後一行</strong>開始讀",
                "課程 Lab Ch2 · 儲存格 152"),
        ],
    ),
    Page(
        n=16, stem="p3_numpy", slug="NUMPY", title_en="NumPy Arrays",
        h1='把資料裝進<span class="blue">陣列</span>：NumPy',
        plain="NumPy 陣列",
        subtitle="先備知識 P3 — 選讀，不列入評分",
        formula="ndarray｜shape 與 ndim｜reshape 與資料共用｜布林索引｜廣播｜axis=0 是往下摺｜default_rng(種子)",
        deck="", deck_pages=0, lab="",
        islp=0, islp_label="先備 · NumPy 陣列", esl_label="",
        playlist="",
        hero_svg=_svg_grid(),
        group="appendix",
        kind="prep", data_key="prep_p3_numpy", src_labs=(2, 1),
        ex_links=[("🔗 NumPy 官方教學", "https://numpy.org/doc/stable/user/absolute_beginners.html"),
                  ("🔗 NumPy 廣播規則", "https://numpy.org/doc/stable/user/basics.broadcasting.html"),
                  ("📓 Ch02 中文 Lab", "https://github.com/phonchi/nsysu-math524-2025/blob/main/"
                   "static_files/presentations/Ch02-statlearn-lab-zh.ipynb")],
        secs=[
            Sec("prologue", "為什麼不用串列", "串列加串列是接起來，陣列加陣列才是逐元素相加",
                "課程 Lab Ch2 · 儲存格 21–34", kicker="PROLOGUE · 開場"),
            Sec("create", "建立陣列與 shape", "ndim、dtype、shape：一個陣列的三個身分證欄位",
                "課程 Lab Ch2 · 儲存格 36–48"),
            Sec("reshape", "reshape 與轉置", "reshape 給的是<strong>同一塊資料的另一種看法</strong>",
                "課程 Lab Ch2 · 儲存格 50–66"),
            Sec("index", "索引、切片與子矩陣", "用 A[[1,3],[0,2]] 理解成對索引",
                "課程 Lab Ch2 · 儲存格 138–158"),
            Sec("bool", "布林索引", "用一排 True／False 挑列：統計程式最常見的選取法",
                "課程 Lab Ch2 · 儲存格 162–176"),
            Sec("bcast", "廣播", "形狀不一樣也能相加：右對齊、補 1、拉伸",
                "NumPy 文件 · 廣播規則|課程 Lab Ch2 · 儲存格 68–72"),
            Sec("agg", "彙總與 axis", "axis=0 是往下摺、axis=1 是往右摺",
                "課程 Lab Ch2 · 儲存格 85–93"),
            Sec("rand", "亂數與模擬", "default_rng(種子)：讓別人跑得出跟你一樣的結果",
                "課程 Lab Ch2 · 儲存格 74–84"),
        ],
    ),
    Page(
        n=17, stem="p4_pandas", slug="PANDAS", title_en="pandas DataFrames",
        h1='一張表就是一次<span class="orange">分析</span>：pandas',
        plain="pandas 資料框",
        subtitle="先備知識 P4 — 選讀，不列入評分",
        formula="Series 與 DataFrame｜head describe shape｜loc 靠名字 iloc 靠位置｜? 要在讀檔時就處理｜dropna 397→392｜groupby 拆分-套用-合併｜concat",
        deck="", deck_pages=0, lab="",
        islp=0, islp_label="先備 · pandas 資料框", esl_label="",
        playlist="",
        hero_svg=_svg_table(),
        group="appendix",
        kind="prep", data_key="prep_p4_pandas", src_labs=(1, 2),
        ex_links=[("🔗 pandas 十分鐘入門",
                   "https://pandas.pydata.org/docs/user_guide/10min.html"),
                  ("🔗 索引與選取資料",
                   "https://pandas.pydata.org/docs/user_guide/indexing.html"),
                  ("📓 Ch01 中文 Lab", "https://github.com/phonchi/nsysu-math524-2025/blob/main/"
                   "static_files/presentations/Ch01-lab-zh.ipynb")],
        secs=[
            Sec("prologue", "Series 與 DataFrame", "一欄是 Series，一張表是 DataFrame",
                "課程 Lab Ch1 · 儲存格 17–28", kicker="PROLOGUE · 開場"),
            Sec("view", "先看，再算", "拿到資料的前五分鐘：head、describe、shape",
                "課程 Lab Ch1 · 儲存格 31–38"),
            Sec("select", "選取列與欄", "<code>loc</code> 靠名字、<code>iloc</code> 靠位置",
                "課程 Lab Ch1 · 儲存格 45–56"),
            Sec("na", "遺漏值", "Auto 的 horsepower 為什麼是字串？397 筆怎麼變成 392 筆",
                "課程 Lab Ch2 · 儲存格 185–199"),
            Sec("group", "分組彙總", "拆分 → 套用 → 合併：groupby 的三個動作",
                "課程 Lab Ch1 · 儲存格 76–78"),
            Sec("join", "串接與讀寫", "concat 把切開的表接回去；讀檔的參數決定後面有多痛",
                "課程 Lab Ch1 · 儲存格 71–72"),
        ],
    ),
    Page(
        n=18, stem="p5_visualization", slug="VISUALIZATION", title_en="Visualization",
        h1='先<span class="blue">畫</span>再算：matplotlib 與 seaborn',
        plain="視覺化",
        subtitle="先備知識 P5 — 選讀，不列入評分",
        formula="Figure 與 Axes｜Seaborn 圖族與層級｜relplot／displot／catplot｜分布與關係｜迴歸與矩陣圖｜選對圖再解讀",
        deck="", deck_pages=0, lab="",
        islp=0, islp_label="先備 · 視覺化", esl_label="",
        playlist="",
        hero_svg=_svg_chart(),
        group="appendix",
        kind="prep", data_key="prep_p5_visualization", src_labs=(1, 2),
        extra_pills=[("📑 導論講義", "https://github.com/phonchi/nsysu-math524/blob/main/static_files/presentations/01_Introduction.pdf"),
                     ("🔗 Seaborn 圖形分類", "https://seaborn.pydata.org/tutorial/function_overview.html")],
        page_css=".w18-function-map{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;margin:1.2rem 0;} .w18-function-family{min-width:0;padding:1rem;border:1px solid var(--card-border);border-radius:10px;background:var(--card);} .w18-level-head{padding:.8rem;margin-bottom:1rem;border-radius:8px;line-height:1.6;} .w18-function-family:nth-child(1) .w18-level-head{background:#eaf0fc;color:#233666;} .w18-function-family:nth-child(2) .w18-level-head{background:#fff0e7;color:#8c380f;} .w18-function-family:nth-child(3) .w18-level-head{background:#e8f3e8;color:#175c30;} .w18-function-family ul{padding-left:1.2rem;} .w18-function-family li{margin:.45rem 0;} .w18-function-family code{overflow-wrap:anywhere;} @media(max-width:760px){.w18-function-map{grid-template-columns:1fr;}}",
        ex_links=[("🔗 seaborn 教學", "https://seaborn.pydata.org/tutorial.html"),
                  ("🔗 Matplotlib 快速入門",
                   "https://matplotlib.org/stable/users/explain/quick_start.html"),
                  ("📓 Ch01 中文 Lab", "https://github.com/phonchi/nsysu-math524-2025/blob/main/"
                   "static_files/presentations/Ch01-lab-zh.ipynb")],
        secs=[
            Sec("prologue", "為什麼要先畫圖", "摘要統計一樣，圖可以完全不一樣",
                "課程 Lab Ch1 · 儲存格 88", kicker="PROLOGUE · 開場"),
            Sec("anat", "圖形層級與 Seaborn 分類", "Figure、Axes 與 Seaborn 的圖形分類",
                "講義 01 · p.29|課程 Lab Ch2 · 儲存格 96–114|seaborn 文件 · 圖形分類"),
            Sec("dist", "看一個變數的分布", "直方圖的 bins 與密度圖的頻寬會改變你的結論",
                "課程 Lab Ch1 · 儲存格 105–111"),
            Sec("rel", "看兩個變數的關係", "散佈圖、折線圖、joint 與 pair",
                "課程 Lab Ch1 · 儲存格 91–117"),
            Sec("cat", "類別變數的圖", "盒鬚圖、長條圖、計數圖：各自在講什麼",
                "課程 Lab Ch1 · 儲存格 120–130"),
            Sec("model", "把模型畫進圖裡", "regplot 與相關係數熱圖",
                "課程 Lab Ch1 · 儲存格 133–138"),
        ],
    ),
    Page(
        n=19, stem="p6_modeling_api", slug="MODELING API", title_en="Modeling APIs",
        h1='兩套 <span class="orange">API</span>、兩種目的：statsmodels 與 scikit-learn',
        plain="建模 API",
        subtitle="先備知識 P6 — 選讀，不列入評分",
        formula="MS 設計矩陣｜sm.OLS(y, X).fit()｜summarize 的四欄｜fit-predict-score｜train_test_split｜cross_validate｜先切分再標準化",
        deck="", deck_pages=0, lab="",
        islp=0, islp_label="先備 · 建模 API", esl_label="",
        playlist="",
        hero_svg=_svg_pipe(),
        group="appendix",
        kind="prep", data_key="prep_p6_modeling_api", src_labs=(3, 5),
        ex_links=[("🔗 statsmodels 快速入門",
                   "https://www.statsmodels.org/stable/gettingstarted.html"),
                  ("🔗 scikit-learn 估計器介面",
                   "https://scikit-learn.org/stable/developers/develop.html"),
                  ("📓 Ch03 中文 Lab", "https://github.com/phonchi/nsysu-math524-2025/blob/main/"
                   "static_files/presentations/Ch03-linreg-lab-zh.ipynb")],
        secs=[
            Sec("prologue", "兩套 API 的分工", "要看係數用 statsmodels，要做預測用 scikit-learn",
                "課程 Lab Ch3 · 儲存格 22–26", kicker="PROLOGUE · 開場"),
            Sec("design", "設計矩陣", "把資料整理成設計矩陣 X",
                "課程 Lab Ch3 · 儲存格 30–39"),
            Sec("summary", "讀 summary 表", "四個欄位：係數、標準誤、t 值、p 值",
                "課程 Lab Ch3 · 儲存格 35–37"),
            Sec("skl", "scikit-learn 的三個動詞", "fit、predict、score：每個模型都長一樣",
                "課程 Lab Ch3 · 儲存格 110–114"),
            Sec("split", "切分訓練與測試", "分開訓練與測試資料，評估對新資料的預測",
                "課程 Lab Ch5 · 儲存格 16–26"),
            Sec("cv", "交叉驗證與資料洩漏", "在每次切分的訓練資料內估計前處理參數",
                "課程 Lab Ch5 · 儲存格 34–46"),
        ],
    ),

]
# ⚠️ 兩條規矩，分清楚：
#
# 1. **既有頁面的 n 一旦定了就不能改。** w<NN> 的 NN 就是這裡的 n
#    （validate.py 的 ID-PREFIX 檢查），二十支 enrich 腳本裡寫死了 w01–w20；
#    改一頁的 n 就要跟著改那一頁所有的 id 與頂層 JS 宣告（單頁 200–600 處）。
#    新增頁面一律取沒用過的最大值。
#
# 2. **顯示順序看的是這個列表的字面值順序，跟 n 無關。** index、README 與
#    chapter-nav 三處都由它決定（validate.py 的 INDEX-SYNC 比對的就是攤平後的整份順序）。
#    2026-08 重排成三區之後 n 已經與順序脫鉤：課前準備是 12、13、20，
#    正課是 1–11，附錄是 14–19。要調整順序就搬字面值，不要動 n。
#
# 分區用 group（"pre"／"core"／"appendix"），不要用 kind——kind 管的是
# 「這頁受哪一套檢查」（prep 頁要過 check_prep_grounding），兩者刻意分開。

from statistics_pages import make_pages as _statistics_pages

# 統計與 Python 都是正課後的查閱附錄；保留各自的區內導覽。
_appendix_start = next(i for i, p in enumerate(PAGES) if p.grp == "appendix")
PAGES[_appendix_start:_appendix_start] = _statistics_pages(Page, Sec)

BY_STEM = {p.stem: p for p in PAGES}
BY_N = {p.n: p for p in PAGES}


def tokens(page: Page):
    """回傳 [(section, token, section_number_text), ...]，含 EX / REF / QUIZ / CARD。"""
    out, part = [], 0
    for s in page.secs:
        if s.kicker:
            out.append((s, "P00", s.kicker))
        else:
            part += 1
            out.append((s, f"P{part:02d}", f"PART {part:02d} · {s.short}"))
    out.append((Sec("exercises", "練習題", "", ""), "EX", "EXERCISES · 練習"))
    out.append((Sec("reference", "重點速查與來源", "", ""), "速查", "重點速查與來源"))
    if page.bankquiz:
        out.append((Sec("bankquiz", "自我檢測", "", ""), "QUIZ", "QUIZ · 自我檢測"))
    out.append((Sec("cards", "關鍵詞彙卡", "", ""), "CARD", "CARDS · 關鍵詞彙卡"))
    return out


def neighbours(page: Page):
    """chapter-nav 的前後鄰居。

    在**同一個 group 裡、依 PAGES 字面值的順序**取前後。

    刻意不用 n 排序：重排三區之後 n 已經與顯示順序脫鉤
    （課前準備是 12、13、20，正課是 1–11，附錄是 14–19）。
    字面值順序才是唯一的真實來源，index、README 與 chapter-nav 三處都看它。

    區與區之間的接縫用 nav_next／nav_prev 明寫：
    課前準備末頁 → introduction，introduction ← 課前準備末頁。
    正課末章刻意不接附錄——附錄是選讀查閱用的。
    """
    fam = [q for q in PAGES if q.grp == page.grp]
    i = fam.index(page)
    prev = fam[i - 1] if i > 0 else None
    nxt = fam[i + 1] if i + 1 < len(fam) else None
    if nxt is None and page.nav_next:
        nxt = BY_STEM.get(page.nav_next)
    if prev is None and page.nav_prev:
        prev = BY_STEM.get(page.nav_prev)
    return prev, nxt


if __name__ == "__main__":
    print(f"{len(PAGES)} 章\n")
    for p in PAGES:
        toks = tokens(p)
        parts = sum(1 for _, t, _ in toks if t.startswith("P") and t != "P00")
        print(f"{p.n:02d} {p.file:32s} {p.plain:12s} 講義 {p.deck_no:>5s}({p.deck_pages:3d}p) "
              f"ISLP ch{p.islp:<2d} {parts} PART{' +QUIZ' if p.bankquiz else ''}")
        print(f"   {'  '.join(t for _, t, _ in toks)}")
