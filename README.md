# 統計學習 × Python 互動自學網站

NSYSU MATH524「統計學習與資料探勘」的互動自學配套網站：十章互動教材，
每一節都能動手操作、預測、驗證，配上每節 quiz、觀念釐清 Q&A、關鍵詞彙卡與 REF 速查表。

- 線上閱讀：https://phonchi.github.io/statlearning-selfstudy/
- 教科書：[ISLP — An Introduction to Statistical Learning with Applications in Python](https://www.statlearning.com/)
- 進階參考：[ESL — The Elements of Statistical Learning](https://hastie.su.domains/ElemStatLearn/)
- 課程講義：[nsysu-math524-2025](https://github.com/phonchi/nsysu-math524-2025)（各頁「講義 PDF」與「中文 Lab」連結來源）

## 章節（授課順序）

| # | 頁面 | 對應 | 講義 | 內容量 |
|---|------|------|------|--------|
| 01 | [統計學習導論](introduction.html) | ISLP Ch.1 | 講義 01 | 8 節 · 0 元件 · 0 張卡 |
| 02 | [統計學習的基本框架](statistical_learning.html) | ISLP Ch.2／ESL Ch.2 | 講義 02 | 7 節 · 8 元件 · 26 張卡 |
| 03 | [線性迴歸](linear_regression.html) | ISLP Ch.3／ESL §3.1–3.3 | 講義 03 | 8 節 · 9 元件 · 28 張卡 |
| 04 | [分類](classification.html) | ISLP Ch.4／ESL §4.1–4.4 | 講義 04 | 8 節 · 7 元件 · 28 張卡 |
| 05 | [重抽樣方法](resampling_methods.html) | ISLP Ch.5／ESL §7.1–7.4、7.10–7.11 | 講義 05 | 8 節 · 8 元件 · 23 張卡 |
| 06 | [線性模型選擇與正則化](model_selection.html) | ISLP Ch.6／ESL §3.3–3.6、§7.1–7.7 | 講義 06 | 10 節 · 10 元件 · 27 張卡 |
| 07 | [非監督式學習](unsupervised_learning.html) | ISLP Ch.12／ESL §13.1–13.3、§14.1–14.3、§14.5–14.9 | 講義 12 | 11 節 · 9 元件 · 30 張卡 |
| 08 | [超越線性](beyond_linearity.html) | ISLP Ch.7／ESL §5.1–5.7、§6.1–6.3、§9.1 | 講義 07 | 9 節 · 12 元件 · 28 張卡 |
| 09 | [樹狀方法與集成學習](tree_based_methods.html) | ISLP Ch.8／ESL §9.2、§8.7–8.8、§10.1–10.14、§15.1–15.3 | 講義 08 | 11 節 · 0 元件 · 0 張卡 |
| 10 | [支持向量機](support_vector_machines.html) | ISLP Ch.9／ESL §6.6–6.9、§12.1–12.3 | 講義 09 | 7 節 · 0 元件 · 0 張卡 |

順序照課堂進度，不是 ISLP 的章號順序——非監督式學習（第 12 章）排在超越線性（第 7 章）之前，
集成學習那一週折進「樹狀方法與集成學習」。

## 內容出處

每頁的 §徽章都標了 ISLP 節號與講義頁碼。`.deck-extra` 卡片裡的程式碼與「預期輸出」
**逐字取自課程 lab notebook**（老師在課程環境實跑的結果），卡片下方的「來源」標了儲存格編號。
圖表用的烘焙資料由 `tools/frames/` 在固定種子下產生，環境為 numpy 1.24.4 · pandas 2.3.2 · scikit-learn 1.6.1 · scipy 1.13.1 · statsmodels 0.14.2 · ISLP 0.4.0 · pygam 0.10.1。

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
python3 tools/validate.py --net    # 17 項具名檢查
node tools/browser_check.js        # 瀏覽器逐項（含手機版與 CDN 失效）
```

寫任何一章之前先讀 [`tools/STYLE_CONTRACT.md`](tools/STYLE_CONTRACT.md)。
