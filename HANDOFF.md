# 交接說明

這份給接手維護的人（含未來的自己）。**先讀這份，再讀 [`tools/STYLE_CONTRACT.md`](tools/STYLE_CONTRACT.md)。**

**2026-09-06 最新定位：**目前共 26 頁。首頁順序為課前準備 → 正課 → 統計附錄 → Python 附錄；
兩組先備知識均為查閱用、選讀、不列入評分。最新位置調整見 §17；前文保留各階段記錄。

---

## 1. 現狀

十一章全部完成並上線：**https://phonchi.github.io/statlearning-selfstudy/**

2026-08 起多了一層**先備入口**（`kind="prep"`，n=12 起），給沒寫過 Python 的人先讀。
九頁全部完成，並於 2026-08-29 **重排成三區**（見 §9.1）。
它跟正課的差別、以及工具鏈為它做了哪些擴充，全部寫在 §9；撰寫規格在
[`tools/STYLE_CONTRACT.md`](tools/STYLE_CONTRACT.md) §9。

| 頁面 | ISLP | 大小 | 圖表 | SVG 元件 | 詞彙卡 | 題庫 |
|---|---|---|---|---|---|---|
| `introduction` | Ch.1 | 160 KB | 1 | 3 | 23 | — |
| `statistical_learning` | Ch.2 | 191 KB | 2 | 6 | 26 | — |
| `linear_regression` | Ch.3 | 261 KB | 4 | 5 | 28 | 6 |
| `classification` | Ch.4 | 218 KB | 2 | 5 | 28 | 6 |
| `resampling_methods` | Ch.5 | 162 KB | 5 | 3 | 23 | — |
| `model_selection` | Ch.6 | 205 KB | 6 | 4 | 27 | — |
| `unsupervised_learning` | Ch.12 | 255 KB | 3 | 6 | 30 | — |
| `beyond_linearity` | Ch.7 | 245 KB | 5 | 7 | 28 | — |
| `tree_based_methods` | Ch.8 | 257 KB | 4 | 6 | 30 | 6 |
| `support_vector_machines` | Ch.9 | 240 KB | 3 | 6 | 26 | — |
| `deep_learning` | **Ch.10 · 補充** | 210 KB | 2 | 4 | 27 | — |

合計 2.3 MB · 37 個 Chart.js 圖表 · 55 個手寫 SVG 元件 · 296 張詞彙卡 · 18 題題庫 · 約 125 個 quiz。

章節順序是**授課順序**，不是 ISLP 章號順序——非監督式（Ch.12）排在超越線性（Ch.7）之前，
集成學習那一週折進「樹狀方法與集成學習」。順序只由 [`tools/pages.py`](tools/pages.py) 承載。

**第 11 頁是補充章。** 本課沒有教 ISLP 第 10 章（第 10 週的 `10_GAM.md` 是 GAM，屬第 7 章），
所以那一章沒有講義 PDF、沒有中文 lab、沒有課程錄影。它的定位、出處與其他章不同，
細節見 §5.1。「補充」兩個字不是寫死在標題裡的，由 `pages.py` 的 `plain`
（`深度學習（補充）`）與 `islp_label`（`ISLP Ch.10 · 補充`）承載，
一路帶到 index 卡片、TOC、chapter-nav、footer 與 README 五處。

---

## 2. 最重要的一件事：`.html` 全部是產物

**不要手改任何 `.html`。** 它們由工具產生，`validate.py` 會用 sha256 比對 GEN 區段並報錯。

| 你要改什麼 | 改哪個檔 |
|---|---|
| 某一節的文字、公式、quiz、Q&A、程式碼卡 | `tools/enrich/enrich_<page>.py` |
| 圖表用的資料（數字） | `tools/frames/gen_<page>.py` |
| 詞彙卡、題庫 | `data/flashcards_zh/chN.json`、`data/questions_zh/chN.json`（**N 是 ISLP 章號**） |
| 章節順序、標題、徽章、prev/next、習題節號 | `tools/pages.py`（唯一真實來源） |
| 樣式 | `tools/template/stats.css`（`base.css` 是沿用的共用系統，別動） |
| 共用 JS（`HC.*`、`Player`、quiz、scroll-spy） | `tools/template/shared.js` |
| landing page 與 README 的章節表 | 不用改，`tools/build_index.py` 會算出來 |

改完一律跑這一串（改了 `pages.py` 或 `template/` 就不要加 `<stem>`，要全跑）：

```bash
cd ~/statlearning-selfstudy
python3 tools/enrich/enrich_<page>.py     # 內容 → HTML（會順便重跑該章的 frames 產生器）
python3 tools/inject_data.py <stem>       # 詞彙卡／題庫 → DATA 區段
python3 tools/build_page.py               # GEN 區段（head/nav/TOC/標題列/chapter-nav/footer/shared.js）
python3 tools/build_index.py              # index.html 與 README 章節表
python3 tools/validate.py --net           # 19 項具名檢查
node    tools/browser_check.js            # 瀏覽器逐項
git add -A && git commit && git push      # Pages 會自動重建
```

`<stem>` 是頁面檔名去掉 `.html`；`enrich_*.py` 的檔名不一定等於 stem
（例如 `enrich_nonlin.py` → `beyond_linearity`），對照表在 `tools/pages.py`。

---

## 3. 本機依賴（不在 repo 裡，換機器要重建）

### 3.1 `m524` conda 環境 — 產生圖表資料用

版本刻意對齊課程的 `packages.txt`，數字才可重現。

```bash
conda create -n m524 python=3.11 -y
conda run -n m524 pip install numpy==1.24.4 pandas==2.3.2 scikit-learn==1.6.1 \
  scipy==1.13.1 statsmodels==0.14.2 matplotlib==3.8.4 seaborn==0.13.2 \
  ISLP==0.4.0 pygam==0.10.1
```

注意：`statsmodels` 課程環境是 0.13.2，但它在 Python 3.11 沒有 wheel，所以用 0.14.2
（本課用到的 OLS／GLM 摘要沒有差異）。`load_data('USArrests')` 與 `load_data('Heart')`
在 ISLP 0.4.0 會 `FileNotFoundError`——USArrests 要照 lab 用
`statsmodels.datasets.get_rdataset('USArrests').data`。

### 3.2 puppeteer + Chrome — 跑 `browser_check.js`

裝在 repo 外面（repo 不放 `node_modules`）：

```bash
mkdir -p ~/.cache/selfstudy-node && cd ~/.cache/selfstudy-node
npm init -y && npm i puppeteer-core
npx puppeteer browsers install chrome
```

Chrome 版本不用寫死，`browser_check.js` 會抓 `~/.cache/puppeteer/chrome` 底下最新的。
截圖會存在 `~/.cache/selfstudy-node/shots/`。

### 3.3 素材來源

`tools/paths.py` 用環境變數覆寫，預設值是：

- `M524_COURSE` → `~/nsysu-math524-2025`（講義 PDF 與中文 lab notebook）
  ：`gh repo clone phonchi/nsysu-math524-2025 ~/nsysu-math524-2025`
- `M524_BOOKS` → `~/statslearning`（`ISLP_website.pdf`、`ESLII_print12.pdf`）
- `M524_LAB_CACHE` → `~/.cache/selfstudy-labs`（官方 ISLP lab 的下載快取，只有第 10 章用，
  會自己抓，不用預先準備；見 §5.1）

還需要 `pdftotext`（poppler）。

`data/source_index/` 是這些素材抽出來的索引，**已 commit**，所以平常維護不需要重跑。
真要重建：`python3 tools/index_deck.py && python3 tools/index_book.py all && python3 tools/extract_lab.py`。

`index_book.py` 有一張 `MANUAL` 補丁表：ESL 第 11 章（Neural Networks）的 verso 頁首
只印章名、沒有「11.」前綴，自動偵測抓不到，重跑索引時整章會從 `esl_chapters.tsv` 消失。
手改 tsv 會被下一次重跑蓋掉，所以釘在程式裡。

---

## 4. 兩道品質關卡

### `tools/validate.py` — 19 項具名檢查（純 stdlib，不用裝東西）

`STRUCT` 單例區塊 · `NAV-SYNC` 三處編號與 section 順序同步 · `ANCHOR` id 唯一且錨點可解析 ·
`ORDER` cards 一定最後 · `BADGE` 每個 h2 至少一個合格徽章 · `QUIZ-TRIPLE` 三選一、
恰好一個正解、**每個選項都要有 `data-fb`** · `DATA-L` `hlLine()` 對得上 `data-l` ·
`ID-PREFIX` 每個 id 與頂層 JS 宣告都含 `w<NN>` · `GEN-REGION` sha256 比對 ·
`FORBIDDEN`（無 polyfill.io／tailwind CDN、Chart.js 必須釘 4.5.1 + SRI、無 `<img>`、
無圖檔、無 `config.plugins =` 賦值、Chart.js 顏色不可用 `var(--x)`）·
`MATHJAX`（JS 字串內無 `$`、含數學的 innerHTML 附近要有 `HC.retype`）·
`FRAMES-META` 烘焙資料要有 src/seed/versions/gen · `GROUNDING` 每張 `.deck-extra` 要有
`.dx-src`、預期輸出要能在 lab 索引裡找到 · `INDEX-SYNC` 卡片與母檔數字一致 ·
`FLASHCARD` / `BANKQUIZ` 母檔格式 · `SIZE` · `LINKS`（`--net`）。

### `tools/browser_check.js` — 真的開瀏覽器

console 無錯 · 按下每個按鈕、推每個滑桿與 select 到底 · 點每個 quiz 確認有回饋 ·
翻詞彙卡／洗牌／全部翻面 · 每個 Chart.js canvas 要真的畫出來 · 每個 SVG 元件不能是空的 ·
Q&A 展開後數學要排版 · **390×844 手機版頁面本體不得橫向滾動** ·
**攔掉 cdn.jsdelivr.net 重載**（模擬 CDN 失效）：圖表要退回 `.chart-fallback`
而手寫 SVG 元件必須仍然活著 · 全頁截圖。

> **驗證不要只看「有沒有掛上」，要看截圖。** 參考線那個 bug 之所以活了八章，
> 就是因為程式碼看起來對、console 也乾淨。用 Read 工具讀 PNG。

---

## 5. 內容出處紀律

這是這個站最重要的性質，改內容時不要破壞：

- `.deck-extra` 裡的程式碼與「預期輸出」一律用 `lab_code(CH, cell)` / `lab_output(CH, cell)`
  **逐字取自課程 lab**，並用 `.dx-src` 標儲存格編號。**絕不重跑、絕不自己打數字**——
  你的環境跟課程環境不同，而 notebook 裡已經是老師本人跑出來的結果。
  `lab_output()` 找不到輸出會直接報錯，那是刻意的。

### 5.1 補充章（`deep_learning`）的出處為什麼不一樣

本課沒有教 ISLP 第 10 章，所以 `data/source_index/` 裡沒有 `deck_10.tsv`、
也沒有中文 lab。那一章改用**課本官方的英文 lab** 當出處：
`intro-stat-learning/ISLP_labs` 的 `Ch10-deeplearning-lab.ipynb`（BSD 2-Clause），
**釘 commit `6bf6160a3dd180c6651ba06655b453e81f91dc20`**——不釘的話上游一改，
站上引用的儲存格編號就會錯位。

`tools/extract_lab.py` 的 `OFFICIAL` 表管這件事：它會把 notebook 抓到
`~/.cache/selfstudy-labs/`（**repo 不放 notebook**，那份有 600 KB 且含 base64 圖），
再用同一個 `extract()` 產生 `data/source_index/lab_ch10.md`。只有這份 `.md` 進 repo。

所以 `lab_code(10, cell)` / `lab_output(10, cell)` 照常運作，紀律一模一樣。
**這一步不能省**：沒有 `lab_ch10.md` 時 `validate.py` 的 GROUNDING 第二段會因為
`labtext` 是空字串而**整段靜默跳過，連 warn 都不會有**，`.expected-out` 等於零檢驗。

兩個衍生的差異：官方 lab 的註解是英文，所以那一章的程式碼**不翻譯**，
中文解說一律寫在卡片外面；`lib.ver_note()` 的文字寫死「逐字取自課程 lab notebook」
對這一章是假話，REF 區改成手寫的 `<p class="ver-note">`。

還有一件會咬人的事：**課本表格的數字跟官方 lab 跑出來的不一樣**
（Hitters 的 MAE 課本是 254.7／252.3／257.4，lab 是 259.7／235.7／221.8；
MNIST 錯誤率課本 1.8%，lab 3.8%），因為切分、epoch 數與套件版本都不同。
頁面上兩組都標清楚是誰的，還拿這個落差當了一則 quiz。改內容時不要把它們混著講。
- 自己算的圖表資料放在 `tools/frames/gen_*.py`，固定種子，`meta` 要有
  `src` / `seed` / `versions` / `gen`，而且產生器的 stderr 會印一行自我對照
  （例如 LOOCV degree 1 = 24.2315 對上 lab 儲存格 32 的 `np.float64(24.23151351792922)`）。
- 引用課本圖只**指名**（「ISLP 圖 5.2 右」），**絕不嵌原圖**——repo 裡完全沒有圖檔，
  每張圖都是從資料或參數重畫的。這同時解決了版權問題。

---

## 6. 已知的坑

全部寫在 [`tools/STYLE_CONTRACT.md`](tools/STYLE_CONTRACT.md) §5 與 §8，這裡只列最會咬人的四個：

1. **`chart.config.plugins = [...]` 靜默失效**（Chart.js 4 的 Config 只有 getter）。
   參考線一律用 `HC.refs(id, [HC.vline(...), HC.hline(...)])`。validator 會擋。
2. **Chart.js 顏色不能寫 `var(--x)`**，canvas 不認得，會靜默變黑。用 `HC.tok.*`。validator 會擋。
3. **SVG 元件的初始化一律放在 `HC.ready()` 外面**，否則 Chart.js 載不到時它們會跟著死。
4. **MathJax 的行間公式**要 `max-width:100%!important` **加上** `min-width:0!important`
   才不會在窄螢幕撐爆版面（它的樣式表是 runtime 注入的，而 `\tag{}` 會設 inline `min-width`）。

---

## 7. 還沒做的事

- ~~`speak-human-tw` 逐頁檢查~~ **已完成（十一頁全跑過）**。做了三件事，每一頁一個 commit：
  - **破折號密度**是全站唯一嚴重的 AI 痕跡，原本每 169–249 字就一個，
    skill 建議 300–500。降到每 274–456 字一次，語意沒動，只把不做事的破折號
    降級成逗號或句號（`——但` → `，但`、`——這` → `。這` 這一類）。
  - **`噪音` 統一成 `雜訊`**（43 處）。六個檔案原本兩種寫法混用，違反契約 §6 的「同頁一致」，
    而且統計脈絡在台灣是用雜訊。
  - 三處零星修正：`落地`→`實際導入`、`同一個算法`→`同一套演算法`、
    `（假陽率, 真陽率）`的半形逗號、`第 7 題（b)(c)` 的全半形括號混用。

  值得記下來的是**沒查到什麼**：套話（「值得注意的是」「綜上所述」）與立場真空
  （「各有優缺點」「因人而異」）**全站零命中**，中國用語掃描的命中也幾乎都是誤判
  （「演算法」含「算法」、「變數組合」含「數組」、「水平邊緣」是方向不是水準）。
  這個站的散文本來就有主張、也沒有罐頭句。以後再跑只要盯破折號密度就好。
- 題庫（`bankquiz`）目前只有第 3、4、8 章。要加就寫 `data/questions_zh/chN.json`
  並在 `pages.py` 把那一章的 `bankquiz=True`。第 10 章是補充章，沒有題庫。
- `data/questions_zh/` 的題目是四選一，`.quiz-box` 的是三選一——兩套引擎不同，這是刻意的
  （題庫由 `inject_data.py` 在前端產生，不受 `QUIZ-TRIPLE` 檢查管）。

---

## 8. 相關 repo

| repo | 是什麼 |
|---|---|
| `phonchi/nsysu-math524` | 課程網站（live，Fall 2026 待更新）。`materials.md` 已連到本站 |
| `phonchi/nsysu-math524-2025` | Fall 2025 封存站。本站的「講義 PDF」與「中文 Lab」都指向這裡（凍結，連結不會爛） |
| `phonchi/ds-python-selfstudy` 等 | 同系列的自學站。本站的設計系統沿用它的 `base.css` |

**課程網站還需要老師決定的**（跟本站無關）：`course_semester` 改 Fall 2026、
`_data/hw_policy.yml` 的 elearn 課程 ID（現為 Fall 2025 的 `20328`）、新學期助教、
`_lectures/*.md` 的上課日期、要不要把 `Mid_term_2025.zip` 補進歷年期中考清單。

封存站有 3 個改不動的舊網址：`01_Introduction.pdf` 內嵌 2 個、`01-06_Recap.pdf` 內嵌 1 個
（PDF 二進位註解物件），會指向 live 站。除非重出投影片，否則接受它。


---

## 9. 先備入口層（2026-08 新增）

### 9.1 它是什麼

正課十一章預設你已經會 Python。先備入口層補的就是這一段：

**九頁全部完成，並重排成三區。**

站台現在的順序是 **課前準備 → 正課十一章 → 附錄：Python 先備知識**。
分區由 `Page.group`（`"pre"`／`"core"`／`"appendix"`）承載，
**顯示順序看的是 `PAGES` 字面值的排列，跟 `n` 無關**——重排之後 n 已經與順序脫鉤
（課前準備是 12、13、20，正課 1–11，附錄 14–19）。`group` 刻意與 `kind` 分開：
`kind="prep"` 管的是「這頁要過 `check_prep_grounding` 那層檢查」，九頁都維持不變。

區與區之間的接縫用 `nav_next`／`nav_prev` 明寫：`00c_ai_assisted → introduction`。
**正課末章刻意不接附錄**——附錄是查閱用的，不該把讀完正課的人導過去。

`p7_ai_assisted` 已改名為 `00c_ai_assisted`（舊網址會 404，站台當時上線一天）。

| n | stem | 出處 lab | 規模 |
|---|---|---|---|
| 12 | `00a_why_code`（AI 時代的資料分析學習迴圈）·**課前準備** | Ch1 | 106 KB · 0 動態元件 · 18 卡 |
| 13 | `00b_setup`（環境安裝，Colab 為主）·**課前準備** | Ch1、Ch2 | 141 KB · 6 元件 · 24 卡 |
| 14 | `p1_python_basics` | Ch2、Ch1 | 121 KB · 6 元件 · 24 卡 |
| 15 | `p2_flow_functions` | Ch2、Ch5 | 138 KB · 6 元件 · 25 卡 |
| **16** | **`p3_numpy`**（pilot，規格由它凍結） | Ch2、Ch1 | 150 KB · 7 元件 · 26 卡 |
| 17 | `p4_pandas` | Ch1、Ch2 | 138 KB · 7 元件 · 25 卡 |
| 18 | `p5_visualization` | Ch1、Ch2 | 140 KB · 7 元件 · 24 卡 |
| 19 | `p6_modeling_api`（statsmodels 與 sklearn） | Ch3、Ch5 | 139 KB · 6 元件 · 25 卡 |
| 20 | `00c_ai_assisted`（AI 輔助統計分析：從提問到驗證）·**課前準備** | Ch1、Ch3、Ch5 | 113 KB · 0 動態元件 · 18 卡 |

一般先備頁沿用正課的元件與自測規格；`00a`、`00c` 是概念型例外，
不設動態元件下限，詞彙卡各 18 張，每主節一題 quiz、EX 三題（見 STYLE_CONTRACT 9.4）。

`00a` 與 `00c` 的分工：**00A 講「如何在 AI 時代完成資料分析學習迴圈」**，
AI 可參與找資料、清理、EDA、文字探勘、建模與溝通，但不能替學生跳過想法、嘗試、證據與修正；
**00C 講「如何實際執行 AI-assisted statistical workflow」**，涵蓋任務分流、脈絡、
小步執行、統計核對、反駁、重現性與資料安全。書籍內容只做短幅轉述，程式與輸出仍回到課程 lab。

### 9.2 工具鏈為它做了什麼（commit `494d293`）

`Page` 多了五個有預設值的欄位，既有十一章的字面值一字未動：

| 欄位 | 用途 |
|---|---|
| `kind` | `"core"`／`"prep"`。分流 EX 區、footer、cards、study-guide 四處文案 |
| `data_key` | 詞彙卡／題庫的檔名鍵。先備頁 `islp=0`，**沒有它會去撞 `ch0.json`** |
| `src_labs` | 本頁允許引用的 lab 章號。GROUNDING 對這組檔案的聯集比對 |
| `ex_links` | EX 區的 pill（官方文件），取代正課的 ISLP 解答站 |
| `nav_next` | 先備層最後一頁用來接回 `introduction` |

**`neighbours()` 也改了，這一條最容易踩。** 舊版是 `BY_N.get(n±1)`，只要註冊 n=12，
`deep_learning`（n=11）就會長出「下一章」，它的 `chapternav` GEN 區段 sha256 立刻改變。
現在是「同 `kind` 依 `n` 排序取前後」——正課 n=1–11 連續，輸出與舊版逐 byte 相同。

`validate.py` 這邊：`BADGE_RE` 追加四個前綴、GROUNDING 的來源改成聯集、
**來源索引不存在從「靜默跳過」改成 `fail()`**（§5.1 警告過的那個坑，順手填了），
另加 `check_prep_grounding()`——fail 等級，整段被 `kind=="prep"` 包住，正課一行都不會執行。

### 9.3 出處：先備頁不需要新來源

課程 lab 本身就是 Python 教材。`lab_ch2.md` 儲存格 21–176 那一整段標題就叫
「實驗：Python 入門」，涵蓋 list／ndarray／索引與子矩陣／布林索引／字串格式化／for 迴圈；
`lab_ch1.md` 的 181 格是完整的 pandas 與 seaborn 用法。所以先備頁照樣走
`lab_code()`／`lab_output()` 逐字引用，**不新建任何外部來源**。

這也順便解掉了授權問題：規劃時參考的
`gedeck/ai-assisted-statistics-for-data-scientists` 是 **GPL-3.0**，
它的 notebook 程式碼一行都不能進這個 repo。參考書
《AI-Assisted Statistics for Data Scientists》(O'Reilly 2026) 只提供概念與章節架構，
用 `AI-Stats §N` 徽章指名，不搬文字、圖與數字。書的 PDF 放 `~/statslearning/`，
`.gitignore` 已擋 `*.pdf`，`check_repo` 也會擋。

`check_prep_grounding` 對 `.dx-src` 的要求比正課硬：儲存格必須真的存在於該 `lab_chN.md`、
`.expected-out` 必須**逐字等於**該格輸出（或所引數格依序串接）、一頁至少一張 lab 引用卡、
`課程 Lab ChN · 儲存格 k` 徽章所指的儲存格也要存在。

### 9.4 index 與 README

`build_index.py` 把 core 與 prep 拆成兩區，先備區折在正課下方。
**一頁 prep 都沒有時整區不輸出**，所以 Phase 0 那次 commit 的 `index.html` 與舊版逐 byte 相同。

### 9.5 寫下一頁的時候

先讀 `tools/STYLE_CONTRACT.md` §9，再抄 `tools/enrich/enrich_p3_numpy.py` 的骨架
（頂端那三個小工具 `C()`／`O()`／`S()` 直接照抄，只換 `CH` 與 `LAB`）。
**n 只能往後加**，中間插頁會讓 `w<NN>` 前綴整批位移。

### 9.6 實作過程中被工具鏈擋下來的四件事

這四個都是真的錯，記下來給下一個人：

1. **併格卡的輸出寫成字面 `\n`**（p3，18 處）→ `GROUNDING-PREP` 的逐字比對擋下。
   順手把該檢查放寬成「某一格的輸出，或這些格依引用順序串接」，兩種都仍是逐字。
2. **`build_index` 的 prep 區塊 f-string 用了雙大括號**，先備卡片整區沒輸出 → `INDEX-SYNC` 擋下。
3. **`ID-PREFIX` 是區分大小寫的**（00a）：`W12_TRUTH` 這種全大寫常數不算含有 `w12`，
   要寫成 `w12Truth`。
4. **`HC.stat.normal(rand)` 回傳的是一個數字，不是產生器**（p3）→ `browser_check` 抓到 pageerror。

另外有一次流程失誤值得記：**p1 與 p2 是同一次註冊的**，所以 commit `a2be187` 只有 p1 有內容時，
`validate` 會因為 p2 還是空骨架而報 1 個失敗。§9.5 說的「只註冊正在寫的頁」是對的，照做。

已知還沒做的：`p3_numpy` 的廣播元件在 stage 上緣留白偏多（不影響閱讀，沒動）。
`p1`／`p2`／`00a`／`00b` 沒有 Chart.js 圖表（純機制頁，契約 §9.4 允許 0–2 個）。

---

## 10. 2026-08-29 全站視覺稽核

完整決策見 `tools/VISUAL_AUDIT.md`。本輪不設定「每頁應有幾張圖」，也不以總數愈少愈好；
判準改成視覺是否真的呈現幾何、隨機變動、資料狀態或參數效果。正文視覺區塊由 125 組降為
106 組，主要移除 00B 重複導覽、假量化方法地圖、重複 ROC/KNN 圖與固定折分播放器。

每個 `viz()` 現在必須帶 `provenance=(kind, detail)`，kind 只能是 `course-data`、
`book-redraw`、`simulation`、`illustrative`；HTML 會顯示 `.viz-source`，`validate.py`
以 `VIZ-PROVENANCE` 檢查數量與類型。講義／ISLP／ESL 是概念黃金標準，lab 是精確數字來源；
合成與自訂資料必須讓學生一眼看出不是課本實證。

高風險修正包括：不可縮減誤差改用獨立 test 網格；LDA/QDA 固定同一資料比較；bootstrap
統一使用 Portfolio α；Lasso geometry 改解析/KKT 解；P5 改 canonical Anscombe；截斷軸與
boxplot 共用同一資料；P6 刪除虛構 leakage MSE；RBF 分開 γ/C；刪除合成 OVO 7% 與手寫
情感規則假 RNN；permutation importance 改報測試 R² decrease mean±SD。

除一般驗證外，必跑：

```bash
python3 tools/check_visual_claims.py
python3 tools/validate.py --net
node tools/browser_check.js
```

---

## 11. 2026-09-05 教學與來源修訂

完整決策與驗證記錄見 [`tools/TEACHING_AUDIT.md`](tools/TEACHING_AUDIT.md)。
三區與授課章序保留；修正正文、自測、詞彙卡與題庫的錯誤通則，精簡 00A／00C 重複清單，
補齊 00B 起步路徑與 P2 前置概念。既有 lab 引用與烘焙數值保留。

`tools/sources.py` 將 `pages.py` 內部書籍鍵轉成中文來源標記，提供同頁完整書目與定位。
來源書名在導讀首次介紹，`AI-Stats §N` 不再直接顯示給學生。
`validate.py` 新增 SOURCE-CLARITY 與跨頁錨點檢查；更新書目後需重跑 `build_page.py`。

**期中使用電腦教室電腦。** 學生本機練習建議以 `pages.CLASSROOM_PACKAGES` 指向的
現行課程版本清單對齊教室。2026-09-05 清單中的 Python 為 3.9.13、statsmodels 為 0.13.2、
Matplotlib 為 3.5.2；清單若更新，需核對 00B 的日期、版本表、安裝範例與詞彙卡。
`pages.ENV_NOTE` 是本站既有圖表的歷史生成環境，不是考前安裝版本依據，不要為了更新教室版本改掉它。

## 12. 第一章改為「統計學習導論與 EDA」

決策與驗證見 [`tools/INTRO_EDA_AUDIT.md`](tools/INTRO_EDA_AUDIT.md)。正文按新版講義重排為
新聞、領域分工、基本學習問題、推薦系統、十個想法、EDA、資料集與後續入口。
資料總表完整 22 筆、五欄，6 合成／16 真實；Advertising 依使用者確認列合成。

第一章講義依使用者指示同步至現行課程 repo，連結使用 main 分支，按鈕不加版本標註。
`Page.deck_url/deck_label/deck_note` 支援單頁來源版本，
`legacy_anchors` 保留重排後的舊書籤，`page_css` 僅供本章表格與圖形閱讀版面。

正文與自測在 `enrich_intro.py`；總表在 `intro_catalog.py`；五組九張 SVG 在 `intro_visuals.py`。
圖形資料由 `gen_intro.py` 重算，`frames()` 使用既有 m524 環境，主 enrich 用系統 python3。
沒有重跑或改寫保存的 lab 輸出。不要把 N/P 總表、模型 p、索引欄與圖形矩陣欄數混為一談。

## 13. P5 補入 Seaborn 函式分類（講義第 29 頁）

`p5_visualization.html#w18seaborn` 以三欄分類卡呈現關係、分布、類別家族，以及 Figure-level／Axes-level。
手機改為單欄排列；第一章 EDA 段落直接連到此處。另整理 jointplot／pairplot、迴歸圖與矩陣圖。
修正以名稱結尾判斷層級、Figure-level 直接回傳 Figure 等說法，說明 kind 與 row／col 分工及 rug=True。
新增兩題自測與四張詞彙卡（P5 共 28 張）。

依據：01 講義 p.29 與 Seaborn 0.13.2 官方 function_overview／API 文件。
驗證記錄在 `tools/verification/seaborn-map-20260905/`：全站結構通過、P5 瀏覽器與新題回饋通過，
139 個外部連結零失敗（2 個既有 Colab HEAD 405 警告）。以少量自訂資料核對 API 控制層級，未重跑課程 lab。

## 14. 全站 speak-human-tw 改寫

詳見 [`tools/HUMANIZE_AUDIT.md`](tools/HUMANIZE_AUDIT.md)。已同步處理 20 頁教材、首頁、
標題、圖說、旁白、自測、詞卡與題庫，完整原句／改後句／原因在 `tools/verification/humanize-20260905/`。

新聞以統計學習的應用能力帶出共同基礎。後續撰寫直接說明定義、操作與證據，避免再次加入
修辭性否定對比、維護歷史與誇大比喻。邏輯否定、公式及資料來源界線保持清楚。
本輪保留 b93f4be 的 FRAMES 物件，沒有重算資料；所有新文案仍以 enrich／pages／data 母檔為準。

## 15. Seeing Theory 統計先備六頁（2026-09-06）

首頁順序為 **課前準備 → 統計先備知識 → 正課 → Python 附錄**。
S1 機率、S2 條件機率、S3 分布、S4 推論為核心查閱路徑；S2 計數與 S5 貝氏、S6 迴歸選讀。
全區選讀、不列入評分，不需要 Python 或微積分基礎。課前準備仍可直接進正課，六個統計頁也各有捷徑。

`tools/statistics_pages.py` 由 `pages.py` 在正課前加入六頁，保留既有 n=1–20，新增 n=21–26。
各頁母檔為 `tools/enrich/enrich_s1_probability.py` 至 `enrich_s6_regression.py`，
詞彙卡在 `data/flashcards_zh/stats_s*.json`。共用來源由 `tools/sources.py` 處理。

`Page.grounding_mode` 預設 `lab`，僅新概念頁明設 `concept`，不再強制課程 lab 卡。
新的 `GROUNDING-CONCEPT` 檢查逐節來源與自測、PDF 頁碼、四題 EX、來源註記，並拒絕未核對的程式輸出卡。
原有 `GROUNDING-PREP` 仍會核對既有先備頁的每個 lab 儲存格。
首頁 INDEX-SYNC 已限定真實 `.ch-card`，不會把「直接進正課」捷徑當作章節卡。

六頁的生成：

```bash
python3 tools/build_page.py
for script in tools/enrich/enrich_s[1-6]_*.py; do python3 "$script"; done
python3 tools/inject_data.py
python3 tools/build_page.py
python3 tools/build_index.py
python3 tools/test_statistics_contract.py
python3 tools/check_visual_claims.py
python3 tools/validate.py --net
node tools/check_statistics_browser.js
SHOT_DIR=/tmp/statistics-20260906/all node tools/browser_check.js s1_probability s2_conditional s3_distributions s4_inference s5_bayesian s6_regression
```

教學與來源決策見 `tools/STATISTICS_PREREQUISITES.md`，驗證文字紀錄在
`tools/verification/statistics-20260906/`。截圖依 inline-only 契約放 `/tmp/statistics-20260906/`。
六頁初稿先完成本機驗證；後續讀者審查修訂與發布方式見 §16。


## 16. 全站獨立讀者修訂（2026-09-06）

審查快照在 `tools/READER_AUDIT.md`，F01–F20、S01–S05 的修正與驗證在
`tools/READER_FIXES.md`。保留四區與授課順序，統一正文／回饋／速查／詞卡的條件，
修正 P1 字串與 PCA 步驟，說清 CV 示範的內外層界線。來源索引、42 個 FRAMES、187 份保存輸出保持原樣。

詞彙卡母檔現在一律是純文字，`validate.py` 會攔截格式標籤與 entity；`shared.js` 仍維持 escape。
來源類型標籤的白字修正已放入共用 stats.css。全站 browser check 新增詞卡實際文字與 MathJax error 檢查。

文字修訂可用 `python3 tools/rebuild_content.py [stem ...]` 重用現有 FRAMES；
若改圖表數字，仍須跑一般 enrich／frames 產生流程。新 regression suite 是 `tools/test_reader_fixes.py`，
詳細執行環境見修正紀錄。所有輸出由母檔生成，仍不可手改 HTML。

本次依使用者要求將統計先備六頁與讀者修正一併提交至 main 並推送；GitHub Pages 由 main 根目錄建置。


## 17. 統計先備移至附錄（2026-09-06）

依使用者指示，統計先備與 Python 採相同的查閱附錄定位。首頁順序改為
課前準備 → 正課十一章 → 附錄：統計先備知識 → 附錄：Python 先備知識。
移除首頁的統計「核心路徑」宣示與 S1–S4 對應徽章；頁面提示正課需要時查閱、不必先讀完。
S6 頁尾與 P6 相同，不再把正課導論標成「下一章」；正課回補連結仍保留。
頁面網址、n 編號、正文、自測與數值資料保持原樣，位置由 pages.py 與 build_index.py 生成。
