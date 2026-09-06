# 撰寫契約

由 pilot 頁 `resampling_methods.html` 凍結。寫任何一章之前先讀完這份，
寫完必須 `tools/validate.py --page <stem>` 與 `node tools/browser_check.js <stem>` 都全綠。

**唯一的參考範例：`tools/enrich/enrich_resampling.py`。** 有疑問就照它做。

---

## 0. 工作流程（一定照這個順序）

```bash
# 1) 讀來源（都在 data/source_index/，不要憑印象寫）
cat data/source_index/deck_NN.tsv        # 講義大綱 → 決定 PART 清單與順序
less data/source_index/lab_chN.md        # lab 的程式碼與實跑輸出（逐字抄用）
grep -P "^N\t" data/source_index/islp_chapters.tsv   # 該章的 PDF 頁範圍
pdftotext -f <pdf_from> -l <pdf_to> -layout ~/statslearning/ISLP_website.pdf -

# 2) 需要圖表資料就寫產生器，用 pinned 環境跑
conda run -n m524 python tools/frames/gen_<page>.py

# 3) 寫 tools/enrich/enrich_<page>.py，然後
python3 tools/enrich/enrich_<page>.py
python3 tools/inject_data.py <stem>
python3 tools/validate.py --page <stem>
node tools/browser_check.js <stem>
```

**不要手改 `.html`。** 內容寫在 `tools/enrich/enrich_<page>.py`，骨架由 `tools/build_page.py` 管。
`<!-- GEN:BEGIN … -->` 區段動了 validator 會失敗。

---

## 1. 出處紀律（grounded）

| 規則 | 為什麼 |
|---|---|
| 每個 `<h2>` 至少一個 `.sec-badge`；書籍標記顯示中文來源角色／主題與章節，可跳到同頁完整書目 | `pages.py` 保存節號，`sources.py` 統一呈現；不要在內文手加不明縮寫 |
| 每張 `.deck-extra` 一定要 `.dx-src`，內容是 `<code>ChNN-…-zh.ipynb</code> · 儲存格 k` | 可機器檢查 |
| `.expected-out` 一律 `lab_output(CH, cell)` 逐字取，**不要自己打字、不要重跑** | 本機環境與課程環境不同；notebook 裡已經是老師本人跑的結果 |
| 程式碼一律 `lab_code(CH, cell)` 取，或至少能對回某一格 | 同上 |
| 自己產生的圖表資料一定放 `FRAMES_w<NN>*`，`meta` 要有 `src` / `seed` / `versions` / `gen` | 任何數字都要能重生與 diff |
| 引用課本圖要指名（`ISLP 圖 5.2 右`），**絕不嵌原圖**（repo 不放任何圖檔） | 版權；也逼我們從資料重畫 |
| REF 區放一次 `ver_note()` | 記錄環境版本 |

`lab_output()` 找不到輸出會直接報錯——這是刻意的。該格沒存輸出就別引用它，改寫產生器自己算並在 `meta.note` 說明。

---

## 2. 命名（validator 強制）

- **`w<NN>` 前綴**：`NN` 是站內序號（`pages.py` 的 `n`，零補兩位）。頁面裡**每一個** `id`、
  每一個頂層 JS 宣告都要含這個前綴。69 個元件共用同一個全域命名空間，前綴是唯一的防撞機制。
  - 例外（不需前綴）：quiz id `q[A-Z]…`、deck-extra 錨點 `dx-…`、骨架 id
    （`fcGrid` `fcShuffle` `fcFlipAll` `fcUnflip` `bqBox` `floatNav` `top`）、section id。
  - 函式內的區域變數不必加前綴（只查第 0 欄的宣告）。
- **quiz id**：`q` + 大寫開頭的短名（`qVal` `qLoo` `qEx1`）。`lib.quiz()` 會自動產生
  `<id>Options` / `<id>Feedback` 與 `onclick`，不要自己拼。
- **deck-extra 錨點**：`<h3 id="dx-短名">`，2–5 個字元。

---

## 3. MathJax 四條鐵律

1. **LaTeX 只放靜態 HTML。任何 JS 字串裡不得出現 `$`**（validator 會抓）。
2. 寫入含數學的 `innerHTML` 之後立刻 `HC.retype(el)`。
3. `.status-banner` 的旁白**不放數學**，用 Unicode：`β̂ σ² R² ε Σ x̄ α̂ λ ρ ≈ ≤ ×`。
   這是最熱的 innerHTML 路徑，免得每次都要 retype。
4. Chart.js 的軸標籤是 canvas 繪製的，**不可能**放 LaTeX，同樣用 Unicode。

在 Python f-string 裡寫 LaTeX：`\\` 要寫成 `\\\\`，`{` `}` 要寫成 `{{` `}}`。
`\\text{{第 }} i \\text{{ 筆}}` ← 注意每個大括號都要成對加倍。

`.qa-item`（`<details>`）裡的數學靠 shared.js 的 `toggle` 委派事件在首次展開時重排，
不需要自己處理。

---

## 4. 每一節的建議順序

```
PART 內部：
  1. 1–2 段導入散文（第二人稱、直接、口語一點）
  2. info(...)          一句話重點；警告用 info(..., "warm")
  3. $$…$$              行間公式（靜態 HTML）
  4. viz(...)           只有真的需要操作或空間關係時才放；沒有教學增益就省略
  5. qa(...)            觀念釐清 Q&A（0–2 則）
  6. card(...)          .deck-extra 講義完整實作 + 預期輸出
  7. quiz(...)          三選一自測（每節至少一個）
  8. table(...)         需要時的比較表
```

**EX 區**：4 個 `quiz()`，`.quiz-label` 用 `EXERCISE n · ISLP N.4 第 m 題`，題號要真
（去 `pdftotext` 讀該章習題確認）。解答 pill 排由 `build_page.py` 產生，不要自己寫。

**重點速查與來源區**（原 REF）：只留有查閱用途的比較表、必要提醒與 `ver_note()`；不再完整重講正文。
完整書目由共用產生器放入，不必在內文重複列一次。各頁首次導讀介紹完整書名，章節標記可直接跳到書目。

**CARDS 區**：整段由 `build_page.py` 產生。你只要寫 `data/flashcards_zh/chN.json`。

---

## 5. 元件（widget）規則

- **沒有最低數量，也不以精簡為目的。**判準只有一個：操作後是否能看見文字、表格或程式輸出
  無法同樣清楚表達的機制、幾何、隨機變動或資料狀態。真正有價值的保留；純播放、固定詞條切換、
  與鄰近表格重複或只有裝飾作用的移除。
- **`.viz-panel` 的結構**：stage → `.status-banner` → `.controls-bar` → `.viz-source`。
  每個 `viz()` 必須標示 provenance：`course-data`、`book-redraw`、`simulation` 或 `illustrative`。
  `illustrative` 必須明說不是課本或實證數值；`simulation` 必須有固定種子。
- 按鈕一律用變體：`.btn .btn-play`（▶ 開始）、`.btn .btn-step`（→ 單步）、
  `.btn .btn-reset`（重置）、`.btn .btn-toggle`。
- **SVG 元件的初始化一律放在 `HC.ready()` 外面。** Chart.js 從 CDN 載不到時 `HC.ready()`
  不會執行；SVG 元件放進去會跟著死掉，就白費了單檔自足的設計。
  `HC.line/bar/scatter` 在 Chart 未載入時本來就安全地回傳 null。
- **SVG 的 `viewBox` 寬度統一用 620**（`HC.svg` 的預設）。自己 `setAttribute('viewBox', …)`
  時也要用 620——viewBox 窄而元素被拉寬，字會跟著等比放大。
- **Player 的 reset frame 要防守**。`i = -1` 之類的哨兵值不要拿去索引陣列，
  否則會畫出 `x1="NaN"`（pilot 犯過這個錯）。
- `.chart-fallback` 的文字要寫**該圖的一句話結論**，不要只寫「圖表載入失敗」——
  CDN 掛掉時教學主張還要活著。

### Chart.js 的三條硬規則（都是踩過才知道的）

1. **參考線一律用 `HC.refs(chartId, [HC.vline(...), HC.hline(...)])`。**
   Chart.js 4 的 `Config.prototype.plugins` 只有 getter 沒有 setter，所以
   `chart.config.plugins = [...]` **靜默失效**——不報錯，線也不見。
   全站八章 19 個呼叫點曾經全部無效。validator 的 FORBIDDEN 會攔下這個賦值。
   `HC.vline/hline` 的第 4 個參數 `row` 可以把靠得近的標籤往下錯開一列。
2. **顏色不要寫 `var(--x)`，要用 `HC.tok.*`。**
   canvas 不認得 CSS 變數，傳進去會靜默變成黑色（第 6 章五條準則線曾經全黑）。
   `HC.base` 現在會在建構前把顏色欄位解析掉，但仍然要寫 `HC.tok.accent2`——
   validator 會擋 `borderColor: 'var(--…)'` 這種寫法。
3. **markers 不要放進 `options.plugins.*`。** Chart.js 會對 plugin options 走一輪
   key 解析，裡面有陣列時會對數字鍵呼叫 `.startsWith` 而爆掉。`HC.refs` 把它們掛在
   `chart.$hcRef` 上，全域註冊的 plugin 不需要 options 就會啟用。

### live 還是 baked

> **數字必須跟權威來源對上 → baked；重點是機制本身 → live。**

Baked（任一成立）：(a) 要重現 ISLP／ESL／講義／lab 的圖或數字且要對到小數位；
(b) 忠實配適需要無法用 50 行 JS 重寫的套件（glmnet 路徑、`SVC` 軟邊界、`scipy` linkage、
GAM、平滑樣條 GCV、RF、大規模 GBDT）；(c) 每 frame 超過 2000 次運算或 n > 500。

其餘一律 live。「拖動它、看它反應」這種連續互動只要有閉式解就**必須** live。
Hybrid 最好：烘焙老師的資料，即時重算上層（`w04thr` 就是這樣）。

`HC.stat` 已經有 `ols` `rss` `mean` `variance` `sd` `lcg` `normal` `pnorm` `dnorm`
`quantile` `seq`——不要重寫。隨機一律用 `HC.stat.lcg(固定種子)`，
**不要用 `Math.random()`**（頁面重載結果會變，學生對不上你的說明）。

---

## 6. 文字

- 使用自然、直接的繁體中文。先說明定義、操作、觀察或成立條件，讓學生看得出每段的用途。
- 修辭性的「不是 A，而是 B」「把它當成 A，不把它當成 B」「不只是……更是……」改為直述；也檢查拆成兩句的同類寫法。
- 移除沒有教學資訊的宣示、誇張比喻與編修歷史。數字、公式、程式、真實引文與必要的邏輯否定要保留，語氣調整不能改變結論與限制。
- 全形標點 `，。：；「」（）`；`｜` 只用在 `.big-formula`；`·` 當標籤分隔。
- 術語第一次出現寫**中文（English）**，識別字放 `<code>`。
- **禁止中國用語**：軟件→軟體、函數（可）／函式（可）但同頁一致、缺省→預設、
  信息→資訊、數據（可）但偏好資料、算法→演算法、優化→最佳化／優化（統計脈絡可）、
  歸一化→正規化、標籤（可）、隊列→佇列、內存→記憶體、字符→字元、
  默認→預設、複雜度（可）、擬合（可）／配適（可）但同頁一致。
- Emoji 只當標籤前綴：📌 📑 📓 📖 📗 🏠 🔗 ▶ 🔀。
- 每個 quiz 的錯選項都要解釋原因，直接指出需要修正的推論或使用條件。保留題目的真偽與答案位置。

### 30 詞術語表（同一頁內用詞要一致）

迴歸 · 分類 · 變異數 · 標準差 · 標準誤 · 常態分佈 · 期望值 · 偏差 · 變異 ·
過度配適 · 配適 · 殘差 · 槓桿值 · 共線性 · 交叉驗證 · 折 · 重抽樣 · 自助法 ·
正則化 · 收縮 · 稀疏 · 調整參數 · 超參數 · 決策邊界 · 混淆矩陣 · 靈敏度 ·
特異度 · 主成分 · 負荷量 · 分群 · 樣條 · 節點 · 平滑 · 集成 · 提升 · 袋外樣本

---

## 7. 尺寸與預算

| 項目 | 目標 |
|---|---|
| 單頁 | 130–240 KB（>300 KB validator 會警告） |
| PART 數 | 照 `pages.py`，不要自己增減 |
| 視覺元件 | 無固定數量；只保留有明確教學增益者 |
| `.quiz-box` | 每 PART 一個 + EX 區 4 個 |
| Q&A | 3–4 則（第 3 章 6 則） |
| `.deck-extra` | 8–12 張 |
| 詞彙卡 | 20–28 張 |

---

## 8. 不要重複 pilot 犯過的錯

1. `HC.ready()` 裡放 SVG 初始化 → CDN 掛掉整組元件死掉。
2. Player 的 reset frame 用 `i = -1` 去索引陣列 → SVG 屬性 NaN。
3. SVG `viewBox` 寬度不是 620 → 字被等比放大。
4. reset 狀態顯示「第 0 折」→ 哨兵值要另外處理顯示文字。
5. `.pseudo-code` 與行間公式在窄螢幕撐爆版面 → 已在 `stats.css` 用
   `overflow-x:auto` 與 `mjx-container[display="true"]` 修掉，不要覆蓋掉。
6. `HC.initFlashcards()` 不要寫在 PAGEJS 裡——`inject_data.py` 會在資料之後呼叫。
7. **`.info-card .ic-title` 有 `text-transform:uppercase`**，會把小寫希臘字母與帶帽符號
   變形（α→Α、p̂→P̂）。側欄卡的標題不要放這些符號，放進 `.ic-row` 的內容裡沒問題。
8. **`.viz-svg .fit` 與 `.viz-svg .resid` 是 CSS 宣告，會蓋掉 SVG 的 `stroke` 呈現屬性。**
   `HC.svg` 的 `poly`/`seg` 預設 `cls` 就是 `fit`/`resid`，所以要畫多色曲線時
   必須自己傳一個 CSS 裡沒有定義的 class，否則顏色參數會被忽略。
9. **驗證不要只看「有沒有掛上」，要看截圖。** 參考線那個 bug 之所以活了八章，
   就是因為程式碼看起來對、也沒有錯誤訊息。`browser_check.js` 會存全頁截圖，
   要真的用 Read 讀過。

---

## 9. 先備入口層（`kind="prep"`）增補條款

由 pilot 頁 `p3_numpy.html`（n=16）凍結。**這一節只適用於 `pages.py` 裡 `kind="prep"` 的頁面**，
正課十一章完全不受影響。

### 9.1 Python／課前頁出處（`grounding_mode="lab"`）

課程 lab 本身就是 Python 教材——`lab_ch2.md` 的「實驗：Python 入門」（儲存格 21–176）
涵蓋 list／ndarray／索引／布林索引／字串格式化／for 迴圈，`lab_ch1.md` 涵蓋 pandas 與
seaborn 的整套用法，`lab_ch5.md`／`lab_ch6.md` 有自訂函式與預設引數。所以：

| 情況 | 做法 |
|---|---|
| 能對回 lab | `card(label, C(k), O(k), src=S(k))`，`.dx-src` 標儲存格 |
| lab 有程式碼但沒存輸出（繪圖格） | `card(..., output=None, note=…)`，`.dx-src` 照標 |
| lab 完全沒有 | **不要做成 `.deck-extra`**。改用行內 `hl()` 片段，不宣稱有實跑輸出，該節徽章掛 `<套件> 文件 · …` |

**一張卡可以併好幾格**（lab 常把一件事拆成連續幾格）。`.expected-out` 允許的形式只有兩種：
某一格的輸出，或這些格**依引用順序串接**——兩種都是逐字。`check_prep_grounding` 會逐字比對，
不符就 FAIL。不要自己打字，不要重跑。

在 enrich 腳本頂端定義三個小工具，其他先備頁照抄：

```python
CH = 2
LAB = "Ch02-statlearn-lab-zh.ipynb"
def C(*ks): return "\n".join(lab_code(CH, k) for k in ks)
def O(k):   return lab_output(CH, k)
def S(*ks): return f'<code>{LAB}</code> · 儲存格 ' + "、".join(str(k) for k in ks)
```

### 9.2 徽章

`BADGE_RE` 為先備頁追加了四個前綴，**其中第一個是可機器驗證的**：

| 徽章 | 用在哪 | 會不會被驗 |
|---|---|---|
| `課程 Lab ChN · 儲存格 k` 或 `… 儲存格 a–b` | 節標題的主要徽章 | **會**，儲存格必須真的存在於 `lab_chN.md` |
| `Python／NumPy／pandas／Matplotlib／seaborn／SciPy／statsmodels／scikit-learn／Colab／conda 文件 · …` | lab 沒有的語法點 | 否 |
| `先備 · …` | `islp_label`、EX 區徽章 | 否 |
| `AI-Stats §N`（僅內部鍵） | 顯示「參考：中文主題（第 N 章）」並連完整書目；不搬原書文字、圖與數字 | SOURCE-CLARITY 核對呈現與定位 |

引用的章號必須列在 `Page.src_labs` 裡，否則 FAIL。

### 教學精簡與難度

- 保留授課章序。課前核心自測不預設已懂模型、檢定或交叉驗證；進階案例明標延伸並連相關章節。
- 同一概念的正文、自測回饋、詞彙卡、題庫與圖旁文字必須同步修訂。
- 重複語法連回 Python 附錄；PCA 幾何、低秩近似與補值等不同角度的必要遞進應保留。
- 不以固定表格、程式碼卡或字數目標塞滿頁面；刪除無教學用途的重複內容時仍保留有效來源。

### 9.3 Page 的登記

```python
Page(n=16, stem="p3_numpy", …,
     islp=0, islp_label="先備 · NumPy 陣列", esl_label="",
     deck="", deck_pages=0, lab="", playlist="",
     kind="prep", data_key="prep_p3_numpy", src_labs=(2, 1),
     ex_links=[("🔗 官方文件", "…")],
     secs=[…])
```

- **n 只能往後加**，永遠不要在中間插頁（`w<NN>` 前綴由 n 決定）。
- `islp=0`：先備頁沒有 ISLP 章號。`data_key` 因此必填，不然詞彙卡會去撞 `ch0.json`。
- `bankquiz=False`：每節一個 quiz ＋ EX 四題已足夠，不另開題庫。
- `nav_next` 只有先備層最後一頁要填，用來接回 `introduction`。

### 9.4 元件

先備頁與正課採同一判準：不設最低數量，也不硬設每頁上限。語法、固定命令、錯誤類型與查表資訊
通常用真實 code/output 或表格更清楚；alias、slice、矩陣索引、broadcasting 等需要觀察狀態或空間
關係的題目則可以保留互動。不得為了讓每節「看起來有元件」加入播放、切換或拖曳。

其餘規則與正課完全相同，特別是這三條：SVG 初始化放在 `HC.ready()` 外面、
`viewBox` 寬度 620、隨機一律 `HC.stat.lcg(固定種子)`。

`HC.stat.normal(rand)` **回傳一個數字**，不是產生器——寫 `out.push(HC.stat.normal(rand))`，
不要 `const nrm = HC.stat.normal(rand)` 再呼叫它（pilot 犯過，browser_check 抓到）。

### 9.5 掛鉤方框

每頁至少一個 `hook(標題, 內容)`，說明「這在本站哪一章會用到」並連到正課的具體錨點。
它內部就是既有的 `.info-box.purple`，**不要為它新增 CSS**——`base.css` 被整份塞進每頁的
head GEN 區段，動它一個 byte 十一章的 sha256 全部失效。

### 9.6 文字

錯選項的回饋**不要自己開頭寫「不對」**，引擎已經會印「不對 ✗」（正解則是「正確 ✓」＋「對。」）。
其餘照 §6。

### 9.7 每頁完成的檢查

```bash
python3 tools/enrich/enrich_<page>.py
python3 tools/inject_data.py <stem>
python3 tools/build_page.py      # 十一章必須全印「無變化」
python3 tools/build_index.py
python3 tools/validate.py        # 全站 0 失敗
node tools/browser_check.js <stem>
# 然後用 Read 真的看截圖（§8.9）
```

## 10. 統計先備知識（2026-09-06）

依使用者確認新增獨立的 `group="statistics"`，顯示於課前準備與正課之間。
六頁皆為 `kind="prep", grounding_mode="concept"`；既有頁面維持預設的 `"lab"`。
S1–S4 為核心查閱路徑，S2 計數選讀；S5–S6 為選讀延伸。全區不列入評分，無 Python 或微積分先備要求。

- 來源為 Seeing Theory 網站與 2018 年 PDF 草稿；`sources.py` 登記完整書目，
  `statistics_pages.py` 登記六頁與節次。每節另附實際網頁主題／PDF 頁碼連結。
  網站與 PDF 內容不同，不能把網頁的 CI／bootstrap 說成 PDF 的對應段落。
- 概念頁不放 `.deck-extra`、`.expected-out` 或課程 lab 執行指示；
  `.ver-note` 說明自訂算例、模型條件、模擬種子與數值核對。
  不使用既有 `ver_note()` 的 lab 文案；既有 lab 頁逐字驗證規則維持。
- 使用原創解說與算例，獨立核對公式、機率方向與成立條件。
  不複製原站程式或圖片；自訂模型標 `illustrative`，抽樣模型標 `simulation` 並固定種子。
- 每主節至少一題三選一自測，EX 四題。自測、詞彙卡、公式與圖旁解說的條件須一致。
  動態圖需區分密度與機率、單側與雙側區域、固定參數與抽樣結果；曲線區域不可越界或錯誤串接。
- 用 `python3 tools/test_statistics_contract.py` 核對來源模式隔離，
  用 `node tools/check_statistics_browser.js` 獨立核對機率、CI、Beta 與 OLS 數值／幾何，
  再跑既有全站驗證與各頁 browser check。
- 瀏覽器截圖放 `/tmp/statistics-20260906/` 並實際檢視；文字驗證結果放
  `tools/verification/statistics-20260906/`。全站所有教學視覺仍是 inline，repo 不放圖檔。


## 11. 讀者審查後的組裝檢查

- 詞彙卡 JSON 的 front/back 都是純文字，不放 `<code>`、`<b>` 或 `&lt;` 等 entity；
  rich HTML 只用在原本支援它的正文與 quiz 回饋。不要為了卡片格式直接移除共用 escape。
- 傳入 quiz/card/table 的普通 Python 字串，不需要為外層 f-string 再加一次大括號或反斜線。
  生成後須核對學生看見的語法；合併 lab 儲存格使用真正的換行分隔。
- 修改結論時，同步檢查正文、圖說／JS 狀態、Q&A、速查、詞卡與題庫；
  期望風險、有限測試誤差，以及程式實際使用的 CV 層次不可混寫。
- 只改文字可用 `tools/rebuild_content.py` 保留既有 FRAMES；刻意改數值時另走 pinned 產生器與數值驗證。
