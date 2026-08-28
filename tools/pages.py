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

# 產生 frames 用的環境（conda env m524）。與課程 packages.txt 對齊之處與差異都記在這裡。
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
    nav_next: str = ""          # 覆寫 chapter-nav 的下一頁 stem（prep 末頁接回正課）

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


PAGES = [
    Page(
        n=1, stem="introduction", slug="INTRODUCTION", title_en="Introduction",
        h1='什麼是<span class="blue">統計學習</span>？',
        plain="統計學習導論",
        subtitle="ISLP 第 1 章 — 對應講義 01",
        formula="監督式｜非監督式｜迴歸 vs 分類｜預測 vs 推論｜n 與 p｜Wage｜Smarket｜NCI60",
        deck="01_Introduction.pdf", deck_pages=42, lab="Ch01-lab-zh.ipynb",
        islp=1, islp_label="ISLP Ch.1", esl_label="",
        playlist="PLHNZtBNWQ-85VI_x3duODyfYm4r3pOl3e",
        hero_svg=_svg_map(),
        secs=[
            Sec("prologue", "課程地圖", "十章方法一次看懂：這門課到底在教什麼",
                "講義 01 · p.9–11", kicker="PROLOGUE · 開場"),
            Sec("supervised", "監督式與非監督式", "有沒有 <span class=\"orange\">y</span>：監督式與非監督式的分界",
                "ISLP §1.1|講義 01 · p.23–27"),
            Sec("regcls", "迴歸與分類", "輸出是數字還是類別：迴歸與分類", "ISLP §1.1|講義 01 · p.33"),
            Sec("predinfer", "預測與推論", "你要的是<strong>準</strong>還是<strong>懂</strong>：預測與推論",
                "ISLP §2.1.1|講義 01 · p.24"),
            Sec("notation", "符號約定", "n、p 與矩陣寫法：先把符號講清楚", "ISLP §1.2"),
            Sec("datasets", "資料集巡禮", "課本三大資料集：Wage、Smarket、NCI60",
                "ISLP §1.1|講義 01 · p.34–38"),
            Sec("slvsml", "統計學習與機器學習", "統計學習、機器學習、資料科學差在哪？",
                "講義 01 · p.19–22"),
            Sec("toolchain", "Python 工具鏈", "動手前的準備：Python 生態與 lab 導覽",
                "講義 01 · p.6–7、41"),
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
        secs=[
            Sec("prologue", "為什麼要估計 f", "把「學習」寫成一條式子：Y = f(X) + ε",
                "ISLP §2.1|講義 02 · p.2–9", kicker="PROLOGUE · 開場"),
            Sec("irreducible", "兩種誤差", "可縮減與<strong>不可縮減</strong>誤差：努力的上限在哪",
                "ISLP §2.1.1|講義 02 · p.10–15"),
            Sec("parametric", "參數式與非參數式", "先假設形狀，還是讓資料自己長？", "ISLP §2.1.2|講義 02 · p.16–21"),
            Sec("tradeoff", "彈性與可解釋性", "彈性換來準度，也換掉了解釋力", "ISLP §2.1.3|講義 02 · p.22–26"),
            Sec("mse", "訓練與測試 MSE", "訓練 MSE 一路往下，測試 MSE 是 U 型", "ISLP §2.2.1|講義 02 · p.27–29"),
            Sec("biasvar", "偏差–變異拆解", "把測試 MSE 拆成三塊：偏差²、變異、不可縮減誤差",
                "ISLP §2.2.2|ESL §7.3 · 進階"),
            Sec("bayes", "Bayes 分類器與 KNN", "分類設定：最好能做到多好，KNN 又靠 K 做什麼",
                "ISLP §2.2.3|講義 02 · p.31–41"),
        ],
    ),
    Page(
        n=3, stem="linear_regression", slug="LINEAR REGRESSION", title_en="Linear Regression",
        h1='<span class="blue">線性迴歸</span>：最老也最有用的模型',
        plain="線性迴歸",
        subtitle="ISLP 第 3 章 — 對應講義 03",
        formula="β̂ = (XᵀX)⁻¹Xᵀy｜RSS｜SE 與 t 檢定｜F 檢定｜R² 與 RSE｜交互作用｜VIF",
        deck="03_Regression.pdf", deck_pages=70, lab="Ch03-linreg-lab-zh.ipynb",
        islp=3, islp_label="ISLP Ch.3", esl_label="ESL §3.1–3.3",
        playlist="PLHNZtBNWQ-87GVk0NXHo19GPagNc7g-ba",
        hero_svg=_svg_scatter(), bankquiz=True,
        secs=[
            Sec("prologue", "四個老問題", "Advertising 資料要回答的四件事",
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
            Sec("vsknn", "與 KNN 的比較", "什麼時候線性模型會輸給 KNN", "ISLP §3.5|講義 03 · p.53–58"),
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
        secs=[
            Sec("prologue", "為什麼不用迴歸", "把類別編成 1、2、3 會出什麼事",
                "ISLP §4.2|講義 04 · p.2–6", kicker="PROLOGUE · 開場"),
            Sec("logistic", "邏輯斯迴歸", "勝算、log-odds 與那條 S 形曲線", "ISLP §4.3|講義 04 · p.7–13"),
            Sec("multinomial", "多元與多類別", "多個預測變數、多於兩類要怎麼做",
                "ISLP §4.3.4–4.3.5|講義 04 · p.11–13"),
            Sec("lda", "LDA", "換個方向想：先建各類的機率模型再用 Bayes 定理",
                "ISLP §4.4.1–4.4.3|講義 04 · p.14–29"),
            Sec("qda", "QDA 與 Naive Bayes", "共變異數要不要共用？獨立假設又幫了什麼",
                "ISLP §4.4.4–4.4.5|講義 04 · p.30–37"),
            Sec("threshold", "閾值、混淆矩陣與 ROC", "0.5 不是天經地義：把閾值當旋鈕",
                "ISLP §4.4.2|講義 04 · p.20–23"),
            Sec("compare", "方法的解析比較", "五種方法在什麼假設下等價、什麼時候會分家",
                "ISLP §4.5|講義 04 · p.38–48"),
            Sec("poisson", "Poisson 迴歸與 GLM", "計數資料：把線性模型推廣成 GLM",
                "ISLP §4.6|講義 04 · p.49–56", eslx=True),
        ],
    ),
    Page(
        n=5, stem="resampling_methods", slug="RESAMPLING", title_en="Resampling Methods",
        h1='<span class="green">重抽樣</span>：用手上的資料造出更多資料',
        plain="重抽樣方法",
        subtitle="ISLP 第 5 章 — 對應講義 05",
        formula="驗證集｜LOOCV｜k-fold CV｜偏差–變異取捨｜Bootstrap｜1−(1−1/n)ⁿ → 0.632",
        deck="05_Resampling_Methods.pdf", deck_pages=42, lab="Ch05-resample-lab-zh.ipynb",
        islp=5, islp_label="ISLP Ch.5", esl_label="ESL §7.1–7.4、7.10–7.11",
        playlist="PLHNZtBNWQ-84VdV4eQXOMacVAIF065luN",
        hero_svg=_svg_folds(),
        secs=[
            Sec("prologue", "訓練誤差會騙人", "為什麼要重抽樣：訓練誤差不是測試誤差",
                "ISLP §5 開頭|講義 05 · p.2–6", kicker="PROLOGUE · 開場"),
            Sec("validation", "驗證集法", "隨手一切兩半：簡單，但答案會跳",
                "ISLP §5.1.1|講義 05 · p.7–9"),
            Sec("loocv", "LOOCV", "一次只留一個：沒有隨機性，而且有捷徑",
                "ISLP §5.1.2|講義 05 · p.10–12"),
            Sec("kfold", "k-fold CV", "折成 k 份輪流當驗證集", "ISLP §5.1.3|講義 05 · p.13–15"),
            Sec("kbias", "k 該取多少", "k 的偏差–變異取捨：為什麼實務上取 5 或 10",
                "ISLP §5.1.4|講義 05 · p.16"),
            Sec("cvclass", "分類問題上的 CV", "把 MSE 換成錯誤率，其餘一樣",
                "ISLP §5.1.5|講義 05 · p.17–18"),
            Sec("cvwrong", "CV 的對與錯", "先用全資料選特徵再 CV：一個很常見的致命錯誤",
                "ISLP §5.1.4|講義 05 · p.19–21"),
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
        secs=[
            Sec("prologue", "為什麼要動手術", "最小平方法什麼時候會不夠用",
                "ISLP §6 開頭|講義 06 · p.2–5", kicker="PROLOGUE · 開場"),
            Sec("subset", "子集選擇", "2^p 個模型跑不完：最佳子集與逐步選擇",
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
            Sec("highdim", "高維度的陷阱", "p 逼近 n 時 R² 會騙你騙得很徹底",
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
        secs=[
            Sec("prologue", "沒有標準答案", "非監督式學習的挑戰：沒有 y 就沒有對錯",
                "ISLP §12.1|講義 12 · p.2–6", kicker="PROLOGUE · 開場"),
            Sec("pca", "主成分是什麼", "第一主成分：變異最大的那個方向",
                "ISLP §12.2.1|講義 12 · p.7–12"),
            Sec("biplot", "Biplot 怎麼讀", "USArrests：一張圖同時放州與變數",
                "ISLP §12.2.2|講義 12 · p.13–16"),
            Sec("lowrank", "另一種解釋", "主成分也是「最佳低維近似」", "ISLP §12.2.2|講義 12 · p.17–19"),
            Sec("pve", "PVE 與 scree plot", "要留幾個主成分？先看解釋了多少變異",
                "ISLP §12.2.3|講義 12 · p.20–22"),
            Sec("scaling", "尺度化與符號", "沒標準化就等於在比單位；符號翻掉不影響結論",
                "ISLP §12.2.3|講義 12 · p.23–28"),
            Sec("completion", "矩陣補全", "把缺失值當成主成分問題解", "ISLP §12.3|講義 12 · p.30–38"),
            Sec("kmeans", "K-means", "指派、更新、再指派：目標函數單調下降",
                "ISLP §12.4.1|講義 12 · p.54–66"),
            Sec("hclust", "階層式分群", "不用先決定 K：dendrogram 與四種 linkage",
                "ISLP §12.4.2|講義 12 · p.67–90"),
            Sec("practical", "分群的實務問題", "要不要標準化、離群值怎麼辦、結果穩不穩",
                "ISLP §12.4.3|講義 12 · p.91–98"),
            Sec("manifold", "流形學習與 t-SNE", "非線性降維：t-SNE 好用但很會騙人",
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
        secs=[
            Sec("prologue", "線性不夠用", "放寬線性假設，但不要放棄可解釋性",
                "ISLP §7 開頭|講義 07 · p.2–4", kicker="PROLOGUE · 開場"),
            Sec("poly", "多項式迴歸", "加高次項：好用，但邊界會爆", "ISLP §7.1|講義 07 · p.5–7"),
            Sec("step", "階梯函數", "把 x 切段，每段給一個常數", "ISLP §7.2|講義 07 · p.8–10"),
            Sec("basis", "基底函數框架", "多項式與階梯其實是同一件事的兩個特例",
                "ISLP §7.3|講義 07 · p.10"),
            Sec("splines", "迴歸樣條", "分段三次多項式，在節點上接得平滑",
                "ISLP §7.4.1–7.4.3|講義 07 · p.11–20"),
            Sec("natural", "自然樣條", "在兩端加線性約束，邊界的變異就收斂了",
                "ISLP §7.4.4–7.4.5|講義 07 · p.21–23"),
            Sec("smooth", "平滑樣條", "換個想法：直接懲罰彎曲程度，用有效自由度描述複雜度",
                "ISLP §7.5|講義 07 · p.24–27"),
            Sec("loess", "局部迴歸", "只看附近的點，加權配一條線", "ISLP §7.6|講義 07 · p.28–33"),
            Sec("gam", "GAM", "每個變數各配一條曲線，再加起來", "ISLP §7.7|講義 07 · p.34–48"),
        ],
    ),
    Page(
        n=9, stem="tree_based_methods", slug="TREES & ENSEMBLES", title_en="Tree-Based Methods & Ensembles",
        h1='一棵<span class="green">樹</span>不夠，就種一座<span class="green">森林</span>',
        plain="樹狀方法與集成學習",
        subtitle="ISLP 第 8 章 — 對應講義 08（含集成學習那一週）",
        formula="遞迴二元分裂｜成本複雜度剪枝｜Gini 與交叉熵｜Bagging｜OOB｜Random Forest｜Boosting｜XGBoost",
        deck="08_Tree-Based_Methods.pdf", deck_pages=80, lab="Ch08-baggboost-lab-zh.ipynb",
        islp=8, islp_label="ISLP Ch.8",
        esl_label="ESL §9.2、§8.7–8.8、§10.1–10.14、§15.1–15.3",
        playlist="PLHNZtBNWQ-87ZC7BDwkB-bgSbqggcWp6T,PLHNZtBNWQ-84JjvtG4zgpxTPF3HDJBnfR",
        hero_svg=_svg_tree(), bankquiz=True,
        secs=[
            Sec("prologue", "樹在幹什麼", "把特徵空間切成方塊，每塊給一個預測值",
                "ISLP §8.1|講義 08 · p.2–9", kicker="PROLOGUE · 開場"),
            Sec("grow", "迴歸樹的生長", "遞迴二元分裂：每一刀都選讓 RSS 掉最多的那一刀",
                "ISLP §8.1.1|講義 08 · p.10–14"),
            Sec("prune", "剪枝", "先長太大再剪：成本複雜度與 α", "ISLP §8.1.1|講義 08 · p.15–21"),
            Sec("classtree", "分類樹", "Gini 指數與交叉熵：為什麼不用錯誤率當分裂準則",
                "ISLP §8.1.2|講義 08 · p.22–27"),
            Sec("vslinear", "樹 vs 線性模型", "哪一種對，看真實邊界長什麼樣",
                "ISLP §8.1.3–8.1.4|講義 08 · p.28–29"),
            Sec("why", "為什麼要集成", "投票與大數法則：一群弱分類器怎麼變強",
                "講義 08 · p.30–31|ESL §16.1 · 進階"),
            Sec("bagging", "Bagging 與 OOB", "重抽樣造很多棵樹再平均；順手拿到免費的驗證集",
                "ISLP §8.2.1|講義 08 · p.32–37"),
            Sec("rf", "Random Forest", "每次分裂只看 m 個變數：去相關才是關鍵",
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
    # ── 補充章：本課沒教 ISLP 第 10 章，所以沒有講義、沒有中文 lab、沒有課程錄影。
    #    「補充」由 plain 與 islp_label 承載，會一路帶到 index 卡片、TOC、
    #    chapter-nav、footer 與 README。出處改用課本官方的英文 lab（見
    #    tools/extract_lab.py 的 OFFICIAL）。務必 append 不要插中間：n 同時是
    #    頁面的 ID 前綴（w11），改動它等於要把後面每一章的 id 全部改名。
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
        secs=[
            Sec("prologue", "先看它跟迴歸的關係", "神經網路不是新東西：從線性模型長出隱藏層",
                "ISLP §10 開頭", kicker="PROLOGUE · 開場"),
            Sec("single", "單層神經網路", "一層隱藏層：非線性怎麼進來的",
                "ISLP §10.1|ESL §11.3"),
            Sec("multi", "多層與 MNIST", "疊第二層之後：softmax 與 235,146 個參數",
                "ISLP §10.2|ESL §11.4–11.6"),
            Sec("cnn", "卷積神經網路", "把「哪裡」的資訊丟掉一部分：卷積與池化",
                "ISLP §10.3"),
            Sec("rnn", "文件分類與 RNN", "順序有意義的時候：詞袋不夠用",
                "ISLP §10.4|ISLP §10.5"),
            Sec("fitting", "怎麼配適", "反向傳播、SGD、dropout：非凸問題怎麼還是解得動",
                "ISLP §10.7|ESL §11.4 · 進階"),
            Sec("doubledesc", "雙下降與該不該用", "參數比樣本多還會變好？以及什麼時候該收手",
                "ISLP §10.8|ISLP §10.6"),
        ],
    ),
    # ── 先備入口層（kind="prep"，n=12 起）────────────────────────────────
    Page(
        n=16, stem="p3_numpy", slug="NUMPY", title_en="NumPy Arrays",
        h1='把資料裝進<span class="blue">陣列</span>：NumPy',
        plain="NumPy 陣列",
        subtitle="先備知識 P3 — 選讀，不列入評分",
        formula="ndarray｜shape 與 ndim｜reshape 是檢視不是複製｜布林索引｜廣播｜axis=0 是往下摺｜default_rng(種子)",
        deck="", deck_pages=0, lab="",
        islp=0, islp_label="先備 · NumPy 陣列", esl_label="",
        playlist="",
        hero_svg=_svg_grid(),
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
            Sec("index", "索引、切片與子矩陣", "A[[1,3],[0,2]] 為什麼不是你以為的那四格",
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
        formula="Figure 與 Axes｜subplots 網格｜histplot 的 bins｜kdeplot 的頻寬｜relplot 與 catplot｜regplot｜heatmap｜截斷的 y 軸會說謊",
        deck="", deck_pages=0, lab="",
        islp=0, islp_label="先備 · 視覺化", esl_label="",
        playlist="",
        hero_svg=_svg_chart(),
        kind="prep", data_key="prep_p5_visualization", src_labs=(1, 2),
        ex_links=[("🔗 seaborn 教學", "https://seaborn.pydata.org/tutorial.html"),
                  ("🔗 Matplotlib 快速入門",
                   "https://matplotlib.org/stable/users/explain/quick_start.html"),
                  ("📓 Ch01 中文 Lab", "https://github.com/phonchi/nsysu-math524-2025/blob/main/"
                   "static_files/presentations/Ch01-lab-zh.ipynb")],
        secs=[
            Sec("prologue", "為什麼要先畫圖", "摘要統計一樣，圖可以完全不一樣",
                "課程 Lab Ch1 · 儲存格 88", kicker="PROLOGUE · 開場"),
            Sec("anat", "Figure 與 Axes", "一張圖的解剖：Figure 是畫布，Axes 才是座標系",
                "課程 Lab Ch2 · 儲存格 96–114"),
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
]
# ⚠️ 只能 append，永遠不要在中間插頁。
# w<NN> 的 NN 就是這裡的 n（validate.py 的 ID-PREFIX 檢查），十一支 enrich 腳本裡
# 寫死了 w01–w11；中間插一頁會讓後面每一頁的前綴位移，整批元件的 id 與 JS 宣告全部失效。
# 先備入口層從 n=12 起跳，正是為了避開這件事。

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
    out.append((Sec("reference", "總覽比較", "", ""), "REF", "REFERENCE · 總覽"))
    if page.bankquiz:
        out.append((Sec("bankquiz", "自我檢測", "", ""), "QUIZ", "QUIZ · 自我檢測"))
    out.append((Sec("cards", "關鍵詞彙卡", "", ""), "CARD", "CARDS · 關鍵詞彙卡"))
    return out


def neighbours(page: Page):
    """chapter-nav 的前後鄰居。

    在**同 kind 的頁面**裡依 n 排序後取前後，不要用 n±1：
    1. 先備入口層是另一條獨立的閱讀線，不該讓正課第 11 章長出「下一章」
       （那會改到它的 chapternav GEN 區段 sha256）。
    2. 分期實作時 n 會有洞（先寫 16 再寫 12），排序法不受影響。
    正課 n=1–11 連續，排序法的輸出與舊的 n±1 完全相同。
    """
    fam = sorted((q for q in PAGES if q.kind == page.kind), key=lambda q: q.n)
    i = fam.index(page)
    prev = fam[i - 1] if i > 0 else None
    nxt = fam[i + 1] if i + 1 < len(fam) else None
    if nxt is None and page.nav_next:
        nxt = BY_STEM.get(page.nav_next)
    return prev, nxt


if __name__ == "__main__":
    print(f"{len(PAGES)} 章\n")
    for p in PAGES:
        toks = tokens(p)
        parts = sum(1 for _, t, _ in toks if t.startswith("P") and t != "P00")
        print(f"{p.n:02d} {p.file:32s} {p.plain:12s} 講義 {p.deck_no:>5s}({p.deck_pages:3d}p) "
              f"ISLP ch{p.islp:<2d} {parts} PART{' +QUIZ' if p.bankquiz else ''}")
        print(f"   {'  '.join(t for _, t, _ in toks)}")
