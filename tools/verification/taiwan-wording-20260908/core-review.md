# Ch2–5 台灣用語與語感檢驗

已逐節閱讀四章的正文、公式周圍解說、程式卡說明、測驗與回答、速查表、圖表標籤、互動提示，以及對應詞彙卡與題庫。使用 speak-human-tw、taiwan-localization、protected-list 與 patterns。

- `tools/enrich/enrich_statlearn.py`：修改 46 行。
- `tools/enrich/enrich_regression.py`：修改 51 行。
- `tools/enrich/enrich_classification.py`：修改 121 行。
- `tools/enrich/enrich_resampling.py`：修改 38 行。
- `data/flashcards_zh/ch2.json`：修改 2 行。
- `data/flashcards_zh/ch3.json`：修改 2 行。
- `data/flashcards_zh/ch4.json`：修改 11 行。
- `data/flashcards_zh/ch5.json`：修改 5 行。
- `data/questions_zh/ch3.json`：修改 2 行。
- `data/questions_zh/ch4.json`：修改 8 行。

保留所有數字、數學公式、程式與輸出、連結與 ID、選項順序及正確答案；未改變任何統計演算法。僅調整作者撰寫的文字，不修改 lab 的原始程式碼。正則化沒有誤換為正規化；水平線、機率、變異數、矩陣等正常專業用語保留。

額外術語確認：`describe()` 顯示 min、25%、50%、75%、max，原「五分位」改為「五數摘要」。`enrich_regression.py` 的 `w03diagDraw()` 用 `w03binMean(P.fit, P.res, 12)` 畫殘差趨勢線，將「分箱平均（＝課本的紅線）」改為「分箱平均（觀察殘差趨勢）」；不再聲稱分箱平均等於課本的平滑曲線。未改演算法或圖表數字。

確認無誤：修改後四份 Python 皆可用 AST 解析、六份 JSON 皆可解析。全站重建與瀏覽器驗收由主代理統一執行。

保真回讀：每筆修改的阿拉伯數字 token、美元符號圈起的數學式、href、完整 inline code 均逐項比對一致（0 個差異）。第二輪回讀已修正替換導致的標點與句子銜接，最終變更 286 行。

跨章統一：以「概似」（包含最大概似與條件概似）及「敏感度」對應 likelihood 與 sensitivity；未動原始 lab 程式與輸出。
