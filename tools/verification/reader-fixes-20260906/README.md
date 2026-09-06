# 讀者審查修訂驗收

日期：2026-09-06。修訂對照見 `../../READER_FIXES.md`。

- 全站結構：26 頁，0 失敗／0 警告。
- 讀者問題回歸：9 個測試通過。P1 直接執行顯示的字典與格式化；PCA 以新合成資料完成 fit→transform；GridSearchCV 概念範例的 scaler 在 15 個候選／折配適中都只見 8 筆訓練資料，最後 refit 才見全部 10 筆。
- 統計來源契約：9 個測試通過。
- 原有視覺主張、六頁統計獨立數值／幾何：通過。
- 桌面／390×844 手機／CDN 失效／詞卡文字：26 頁完成。課前與統計九頁、Python 六頁各為 0 問題；正課首次通過九頁，深度學習公式補修後與統計學習一併複驗為 0 問題。詳見 browser-entry、browser-python、browser-core 與 browser-final 日誌。
- 外連：180 個，0 失敗；2 個既有 Colab HEAD 405 警告。
- 保留 26 份來源索引、42 個 FRAMES 與 187 份保存輸出，雜湊回歸比對通過。
- 原 125 張含標籤／entity 的詞卡全部修正：其中一張在內容修訂時改成純文，其餘 124 張的轉換記錄見 card-normalization.json。
- 已實際檢視 P1 格式化／翻面卡、PCA 程式卡與來源標籤，白字／背景對比約 13.47:1。完整截圖留在 `/tmp/reader-fixes-20260906/`。

`browser-core.log` 保留第一輪發現的兩個深度學習 MathJax 錯誤；它們已在 `browser-final.log` 對應的修訂中解決。該頁組合儲存格的字面換行也已修正，13 張程式卡均通過保留縮排的 Python AST 語法檢查；此項不宣稱所有神經網路訓練都重新執行。

`final-manifest.json` 是本輪本機成品雜湊。部署版本以推送後 main 的 commit 與 GitHub Pages build 記錄核對。
