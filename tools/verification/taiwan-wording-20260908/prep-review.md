# 導論與先備頁台灣用語完整檢查

已依 speak-human-tw 逐頁閱讀正文、解說、表格、題目、圖說、互動狀態與詞彙卡。先採用使用者指定的「擬合」，再依語境修正台灣用語與生硬翻譯。

本分工檢查 34 個母檔／詞彙卡檔案；記錄 103 次行級修改，涉及 30 個檔案。完整原句、改句與原因見 prep-edits.jsonl。

確認無誤：Python AST 與 JSON 可解析；逐筆修改前後的數字、公式片段、href 字串一致。沒有重新產生資料或改動計算。網站重建與瀏覽器驗收由主代理執行。

保留：機率質量函數與質量的數學意義、水平線的幾何意義、Colab 原選單文字「在雲端硬碟中儲存副本」、lab 程式原文與輸出。母檔中的內部來源索引未修改；對外定位由既有共用 renderer 處理。

| 檔案 | 檢查結果 |
|---|---|
| `data/flashcards_zh/ch1.json` | 已修正；1 次行級記錄 |
| `data/flashcards_zh/prep_00a_why_code.json` | 已修正；1 次行級記錄 |
| `data/flashcards_zh/prep_00b_setup.json` | 已修正；3 次行級記錄 |
| `data/flashcards_zh/prep_00c_ai_assisted.json` | 已修正；1 次行級記錄 |
| `data/flashcards_zh/prep_p1_python_basics.json` | 已修正；2 次行級記錄 |
| `data/flashcards_zh/prep_p2_flow_functions.json` | 已修正；3 次行級記錄 |
| `data/flashcards_zh/prep_p3_numpy.json` | 確認無誤；本輪未新增修改 |
| `data/flashcards_zh/prep_p4_pandas.json` | 確認無誤；本輪未新增修改 |
| `data/flashcards_zh/prep_p5_visualization.json` | 已修正；2 次行級記錄 |
| `data/flashcards_zh/prep_p6_modeling_api.json` | 已修正；2 次行級記錄 |
| `data/flashcards_zh/stats_s1_probability.json` | 確認無誤；本輪未新增修改 |
| `data/flashcards_zh/stats_s2_conditional.json` | 已修正；4 次行級記錄 |
| `data/flashcards_zh/stats_s3_distributions.json` | 已修正；1 次行級記錄 |
| `data/flashcards_zh/stats_s4_inference.json` | 已修正；2 次行級記錄 |
| `data/flashcards_zh/stats_s5_bayesian.json` | 已修正；1 次行級記錄 |
| `data/flashcards_zh/stats_s6_regression.json` | 已修正；1 次行級記錄 |
| `tools/enrich/enrich_00a_why_code.py` | 已修正；2 次行級記錄 |
| `tools/enrich/enrich_00b_setup.py` | 已修正；17 次行級記錄 |
| `tools/enrich/enrich_00c_ai_assisted.py` | 已修正；11 次行級記錄 |
| `tools/enrich/enrich_intro.py` | 已修正；4 次行級記錄 |
| `tools/enrich/enrich_p1_python_basics.py` | 已修正；1 次行級記錄 |
| `tools/enrich/enrich_p2_flow_functions.py` | 已修正；5 次行級記錄 |
| `tools/enrich/enrich_p3_numpy.py` | 已修正；3 次行級記錄 |
| `tools/enrich/enrich_p4_pandas.py` | 已修正；2 次行級記錄 |
| `tools/enrich/enrich_p5_visualization.py` | 已修正；8 次行級記錄 |
| `tools/enrich/enrich_p6_modeling_api.py` | 已修正；5 次行級記錄 |
| `tools/enrich/enrich_s1_probability.py` | 已修正；1 次行級記錄 |
| `tools/enrich/enrich_s2_conditional.py` | 已修正；3 次行級記錄 |
| `tools/enrich/enrich_s3_distributions.py` | 已修正；3 次行級記錄 |
| `tools/enrich/enrich_s4_inference.py` | 已修正；4 次行級記錄 |
| `tools/enrich/enrich_s5_bayesian.py` | 已修正；7 次行級記錄 |
| `tools/enrich/enrich_s6_regression.py` | 已修正；1 次行級記錄 |
| `tools/enrich/intro_catalog.py` | 已修正；2 次行級記錄 |
| `tools/enrich/intro_visuals.py` | 確認無誤；本輪未新增修改 |
