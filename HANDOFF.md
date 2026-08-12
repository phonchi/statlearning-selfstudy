# 交接說明

這份給接手維護的人（含未來的自己）。**先讀這份，再讀 [`tools/STYLE_CONTRACT.md`](tools/STYLE_CONTRACT.md)。**

---

## 1. 現狀

十一章全部完成並上線：**https://phonchi.github.io/statlearning-selfstudy/**

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
