# 全站台灣教學用語修正

依使用者確認，fitting 統一使用「擬合」，並使用 speak-human-tw 逐段檢查首頁、26 個教學頁、動態提示、自測、題庫、詞彙卡與 README。基準版本為 `9aa7a1cf5d847606b5ba46c645f5e458b3bc804e`。

## 修正內容

- 統一「擬合、過度擬合、欠擬合、擬合值」，連同「配出來、重配、配一棵樹」等省略說法一起修正。
- 統一「最大概似／對數概似／條件概似、敏感度、門檻值、巢狀、遺漏值、樣本數、指派、本機、目前、操作流程」等用語。
- 改寫生硬翻譯、誇張比喻與沒有具體資訊的教學旁白；將「算力」依語境寫成運算成本或運算資源。
- 「五分位」改為符合實際輸出的「五數摘要」；分箱平均殘差線不再聲稱與課本紅線完全相同，數值與繪圖方法保留。
- 保留有精確意思的學科名詞，例如機率質量、水平線、正則化與正規化；不因套用詞表而改壞語意。
- 撰寫規則改為單一術語標準，`validate.py` 新增 `WORDING-TW`，會檢查正文、動態字串、題目回饋及詞彙卡，攔下舊用語。

[完整修改紀錄](edits.jsonl) 共 **956 筆逐行修改紀錄、57 個內容母檔**。同一行若先改術語再改句子，保留兩筆紀錄，不把紀錄數當成獨立句數。每筆都有檔案、行號、原句、改後句與原因。[統計](edit-summary.json)

逐頁閱讀紀錄：[導論與先備頁](prep-review.md)、[統計學習／迴歸／分類／重抽樣](core-review.md)、[進階章節](advanced-review.md)。

## 驗證

- **確認無誤**：全部 27 頁與 README 的指定用語掃描通過，包含互動後才出現的字串；[wording-scan.log](wording-scan.log)。
- **確認無誤**：232 張 lab 程式碼卡的完整程式與保存輸出對回原始來源；[lab-code.log](lab-code.log)。
- **確認無誤**：所有 FRAMES 逐位元不變，數字、連結、ID、題目正確答案與順序保留；[preservation.log](preservation.log)、[preservation.json](preservation.json)。
- **確認無誤**：JavaScript AST 保真；只允許中文顯示字串變動，數值常值、識別字、運算與程式結構保留；[js-preservation.log](js-preservation.log)。
- 三段中文演算法示意與一個公式的中文標籤也改為「擬合」；保真檢查逐項列出這四個允許差異，沒有略過原始 lab 程式或數學運算。
- **確認無誤**：新增用語規則 5 項測試，以及既有來源 4 項、統計模式 9 項測試通過；[wording-tests.log](wording-tests.log)、[reader-source-tests.log](reader-source-tests.log)、[statistics-contract.log](statistics-contract.log)。
- **確認無誤**：全站 26 頁桌面／手機、自測、翻卡、滑桿、按鈕、SVG、Chart.js、MathJax 與 CDN 失效檢查，0 個問題；[browser.log](browser.log)。
- **確認無誤**：首頁、Wage 圖說、分類門檻及模型比較表另外做桌面／手機看圖驗收；[visual-reading.log](visual-reading.log)。手機比較表擠字已改為保留可讀寬度、在容器內橫向捲動，重測無頁面溢出；[model-table-final.log](model-table-final.log)。
- **確認無誤**：完整重建後 28 個產物逐位元相同；[run.log](run.log)、[final-manifest.json](final-manifest.json)。

驗證器維持 0 失敗；三項既有頁面大小提醒來自上輪保留完整圖表資料，這次未重新產生統計資料。[validate.log](validate.log)

[全部教學頁首屏總覽](all-pages-overview.png)。完整長頁與指定區段截圖存於 [screenshots](screenshots/)，總覽只用於查找頁面，不能代替長頁及互動檢查。

## 重跑

```bash
python3 tools/verification/taiwan-wording-20260908/run_checks.py
node --expose-internals tools/verification/taiwan-wording-20260908/check_js.cjs
```

用語規則以學生可見內容為範圍。原始來源、舊驗收報告、修改前後紀錄及測試中的錯誤範例保留原文，不把歷史證據改寫成新用詞。
