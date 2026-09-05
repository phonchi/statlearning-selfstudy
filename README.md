# 統計學習 × Python 互動自學網站

NSYSU MATH524「統計學習與資料探勘」的互動自學配套網站，分成三區：

1. **課前準備**（3 頁）——AI 時代的資料分析學習迴圈、環境安裝、AI 輔助統計分析。不需要程式基礎。
2. **正課**（11 章）——每一節都有可核對的例子或自測，必要處保留互動，並配上 quiz、觀念釐清 Q&A、
   關鍵詞彙卡與重點速查表。
3. **附錄：Python 先備知識**（6 頁）——正課會用到的語法與套件，查閱用。

課前準備與附錄都是選讀，不列入評分。

- 線上閱讀：https://phonchi.github.io/statlearning-selfstudy/
- 教科書：[ISLP — An Introduction to Statistical Learning with Applications in Python](https://www.statlearning.com/)
- 進階參考：[ESL — The Elements of Statistical Learning](https://hastie.su.domains/ElemStatLearn/)
- 課程講義：[nsysu-math524-2025](https://github.com/phonchi/nsysu-math524-2025)（各頁「講義 PDF」與「中文 Lab」連結來源）

## 課前準備（選讀，不列入評分）

三頁，可依需要選讀，不需要任何程式基礎。

**期中考使用電腦教室的電腦。** 本機練習建議依[課程提供的版本清單](https://github.com/phonchi/nsysu-math524/blob/main/static_files/presentations/packages.txt)
對齊教室的 Python 與套件版本；平時可用 Colab，考前仍應熟悉教室環境。
安裝與核對步驟見[環境安裝：本機與考前準備](00b_setup.html#local)。

| # | 頁面 | 對應 | 內容量 |
|---|------|------|--------|
| 1 | [AI 時代的資料分析學習迴圈](00a_why_code.html) | 課前 · AI 學習迴圈 | 5 節 · 0 視覺區塊 · 18 張卡 |
| 2 | [環境安裝](00b_setup.html) | 課前 · 環境安裝 | 6 節 · 1 視覺區塊 · 24 張卡 |
| 3 | [AI 輔助統計分析：從提問到驗證](00c_ai_assisted.html) | 課前 · AI 協作 | 6 節 · 0 視覺區塊 · 18 張卡 |

## 正課 · 十一章（授課順序）

| # | 頁面 | 對應 | 講義 | 內容量 |
|---|------|------|------|--------|
| 01 | [統計學習導論與 EDA](introduction.html) | ISLP Ch.1 | 講義 01 | 9 節 · 5 視覺區塊 · 26 張卡 |
| 02 | [統計學習的基本框架](statistical_learning.html) | ISLP Ch.2／ESL Ch.2 | 講義 02 | 7 節 · 5 視覺區塊 · 26 張卡 |
| 03 | [線性迴歸](linear_regression.html) | ISLP Ch.3／ESL §3.1–3.3 | 講義 03 | 8 節 · 6 視覺區塊 · 28 張卡 |
| 04 | [分類](classification.html) | ISLP Ch.4／ESL §4.1–4.4 | 講義 04 | 8 節 · 5 視覺區塊 · 28 張卡 |
| 05 | [重抽樣方法](resampling_methods.html) | ISLP Ch.5／ESL §7.1–7.4、7.10–7.11 | 講義 05 | 8 節 · 4 視覺區塊 · 23 張卡 |
| 06 | [線性模型選擇與正則化](model_selection.html) | ISLP Ch.6／ESL §3.3–3.6、§7.1–7.7 | 講義 06 | 10 節 · 6 視覺區塊 · 27 張卡 |
| 07 | [非監督式學習](unsupervised_learning.html) | ISLP Ch.12／ESL §13.1–13.3、§14.1–14.3、§14.5–14.9 | 講義 12 | 11 節 · 8 視覺區塊 · 30 張卡 |
| 08 | [超越線性](beyond_linearity.html) | ISLP Ch.7／ESL §5.1–5.7、§6.1–6.3、§9.1 | 講義 07 | 9 節 · 8 視覺區塊 · 28 張卡 |
| 09 | [樹狀方法與集成學習](tree_based_methods.html) | ISLP Ch.8／ESL §9.2、§8.7–8.8、§10.1–10.14、§15.1–15.3 | 講義 08 | 11 節 · 9 視覺區塊 · 30 張卡 |
| 10 | [支持向量機](support_vector_machines.html) | ISLP Ch.9／ESL §6.6–6.9、§12.1–12.3 | 講義 09 | 7 節 · 6 視覺區塊 · 26 張卡 |
| 11 | [深度學習（補充）](deep_learning.html) | ISLP Ch.10 · 補充／ESL Ch.11 | — | 7 節 · 5 視覺區塊 · 27 張卡 |

章節依課堂進度排列：非監督式學習（第 12 章）排在超越線性（第 7 章）之前，
集成學習那一週折進「樹狀方法與集成學習」。

## 附錄：Python 先備知識（選讀，不列入評分）

沒寫過 Python，或只會一點點？這六頁把正課會用到的語法與套件講一遍，
程式碼一樣逐字取自課程 lab notebook。**查閱用**——正課讀到卡住再回來翻，不必先讀完。

| # | 頁面 | 對應 | 內容量 |
|---|------|------|--------|
| 1 | [Python 基礎](p1_python_basics.html) | 先備 · Python 基礎 | 6 節 · 6 視覺區塊 · 24 張卡 |
| 2 | [流程與函式](p2_flow_functions.html) | 先備 · 流程與函式 | 6 節 · 6 視覺區塊 · 25 張卡 |
| 3 | [NumPy 陣列](p3_numpy.html) | 先備 · NumPy 陣列 | 8 節 · 7 視覺區塊 · 26 張卡 |
| 4 | [pandas 資料框](p4_pandas.html) | 先備 · pandas 資料框 | 6 節 · 7 視覺區塊 · 25 張卡 |
| 5 | [視覺化](p5_visualization.html) | 先備 · 視覺化 | 6 節 · 7 視覺區塊 · 28 張卡 |
| 6 | [建模 API](p6_modeling_api.html) | 先備 · 建模 API | 6 節 · 6 視覺區塊 · 25 張卡 |

想先練習 Python 再進正課，可以依序閱讀：P1 → P2 → P3 → P4 → P5 → P6；
寫過程式、只是沒碰過資料科學套件的，從 P3 開始就好。

## 內容出處

每頁的中文來源標記提供課本節號或講義頁碼，並可跳至同頁完整書目。`.deck-extra` 卡片裡的程式碼與「預期輸出」
**逐字取自課程 lab notebook**（老師在課程環境實跑的結果），卡片下方的「來源」標了儲存格編號。
圖表用的烘焙資料由 `tools/frames/` 在固定種子下產生，環境為 numpy 1.24.4 · pandas 2.3.2 · scikit-learn 1.6.1 · scipy 1.13.1 · statsmodels 0.14.2 · ISLP 0.4.0 · pygam 0.10.1。
每個正文視覺另標示它屬於課程資料、講義／課本重繪、固定種子模擬或自訂概念示意；
自訂值不得解讀成課本或實證結果。

第 11 頁「深度學習」是**補充章**——本課沒有教 ISLP 第 10 章，所以沒有講義也沒有中文 lab。
那一章的程式碼與輸出改為逐字取自[課本官方的英文 lab](https://github.com/intro-stat-learning/ISLP_labs)
（BSD 2-Clause，釘 commit `6bf6160`），「逐字引用、絕不重跑」的紀律不變。

## 技術

每頁皆為單檔自足 HTML。外部依賴只有三個：MathJax 3、Google Fonts、
Chart.js 4.5.1（釘版本並附 SRI）。手寫的 SVG 元件是原生 JS，
Chart.js 載不到時只有圖表退回一句話結論，其餘互動照常運作。

## 開發

```bash
python3 tools/build_page.py        # 骨架與 GEN 區段（三處編號、prev/next 由 tools/pages.py 產生）
python3 tools/enrich/enrich_*.py   # 各章內容
python3 tools/inject_data.py       # 詞彙卡與題庫（母檔在 data/）
python3 tools/build_index.py       # 本檔與 index.html
python3 tools/check_visual_claims.py  # 高風險視覺的來源與數值不變量
python3 tools/validate.py --net    # 19 項具名檢查
node tools/browser_check.js        # 瀏覽器逐項（含手機版與 CDN 失效）
```

`.html` 全部是產物，**不要手改**——`validate.py` 會用 sha256 比對 GEN 區段並報錯。

維護與交接說明看 [`HANDOFF.md`](HANDOFF.md)；撰寫規則看 [`tools/STYLE_CONTRACT.md`](tools/STYLE_CONTRACT.md)。
