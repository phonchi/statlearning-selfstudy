# 第 4 章後半與第 5 章對齊講義（2026-10-06）

範圍：講義 04 p.22–61（p.1–21 只補連結與 logit⇄logistic 一句）、講義 05 全 42 頁，並嵌入使用者指定的 16 則概念問答。
決策與內容摘要見 `HANDOFF.md` §21。

## 檔案
- `deck_links.json`：兩份講義 PDF 的全部超連結（PyMuPDF 抽出，頁碼＋URL）。
- `verify_math.py`：新公式與數字的數值核對（seed 20261006；`conda run -n m524 python verify_math.py`）。
- `verify.py <rev>`：與基準版比對——既有 `FRAMES_w04*`／`FRAMES_w05*` 逐 byte 相同（只允許新增 `FRAMES_w04scen`、`FRAMES_w05sim` 與重產 `FRAMES_w05misuse`）、既有 lab 程式與輸出文字仍在、講義每個連結都出現在頁面（兩個確認 404 的連結除外）、id 不重複、沒有預設展開的 details。
- `shots.py <stem> <id|@css>[|action] ...`：Playwright 1440／390 px 截圖，檢查 MathJax 錯誤、頁面錯誤與橫向溢出；截圖在 `shots/`。
- `run.log`：最終一輪完整檢查輸出。

注意：`verify.py` 的 lab 文字檢查是「基準版的每段程式／輸出仍是新版某張卡的子字串」，以容許本次把儲存格 53 併入 55 的卡片；它比 aadb695 的 `verify_refinement.py`（逐字相等）寬鬆，無法偵測「被截短後仍是別張卡子字串」的情形。

## commit 對應
- 第 4 章 commit：`classification.html`、`tools/enrich/enrich_classification.py`、`tools/frames/gen_classification.py`、`tools/enrich/reading_flow_ch1_6.py`（GROUPS[4] 的 fisher 移除與兩個附錄群組）、`data/flashcards_zh/ch4.json`、`shots/classification-*`。此 commit 單獨可建置。
- 第 5 章＋共同檔 commit：`resampling_methods.html`、`tools/enrich/enrich_resampling.py`、`tools/frames/gen_resampling.py`、`data/flashcards_zh/ch5.json`、`tools/STYLE_CONTRACT.md`、`HANDOFF.md`、`index.html`／`README.md`（若有變）、本目錄其餘檔案，以及 `check_teaching_scope.py` 重寫的 `tools/verification/teaching-scope-20260910/*.json`（只是依目前頁面重算的清單與計數）。

## 已知、非本次造成
- `validate.py --net`：causeweb 連結因伺服器憑證鏈不完整而 SSL 驗證失敗（第 3 章自 2026-09-22 起即用同一網址）；GitHub 連結偶發逾時。其餘外部連結 403 僅警告。
- `test_reader_fixes.py` 兩個失敗在 HEAD 同樣存在（2026-09-06 基準檔過期；測試遇到第一個不符頁面即中止）。
- 講義連結確認失效（HEAD 與 GET 皆 404，2026-10-06）而未放入：`web.stanford.edu/class/stats191/notebooks/Logistic.html`（04 p.61）、`www.saattrupdan.com/2020-03-01-bootstrap-prediction`（05 p.38）。
