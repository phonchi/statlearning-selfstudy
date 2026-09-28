# Classification 修訂驗證（2026-09-28）

修訂範圍：classification 章節、生成器、Ch4 詞彙卡與題庫；沒有 commit、push 或發布。
基準 commit 與 HTML SHA256 見 `provenance.json`。

## 內容

- 正文補 Bernoulli、條件平均等於機率、非同變異的反應誤差、logistic 的值域與線性分類器。
- 正文說明 MLE 的 z 近似、類別解釋變數、多類別 categorical／softmax，以及轉向生成式模型的動機。
- 收合補公平賠率與勝算、z/t 差異、多類別概似與識別限制。
- LDA 正文加入一維與多維封閉解，區分 n 與 n−K 分母，明寫判別函數的線性形式。
- 保留講義相關的概似、標準誤、OLS–LDA、QDA、FLDA、白化與判別子空間推導及來源連結。
- QDA、Naive Bayes、Poisson、GLM 補明條件分布及額外假設；統一 g 與 η。
- 順序對齊講義，移除 OVR／OVO 獨立長篇與 Gamma 表格，簡化重複及不必要的模型比較。
- 全文、互動提示、回饋與29張卡片潤稿；保留原Lab的程式和輸出。
- 靜態公式使用 MathJax；修正 flex 容器把行內公式當成獨立項目擠壓的手機顯示問題。

## 確認無誤

- `validate.log`：classification 結構／來源／公式／錨點檢查，0 failures、0 warnings。
- `content-numeric.log`：36項內容與獨立數值核對；含 Bernoulli variance、softmax baseline、LDA距離、白化及投影。
- `lab-rendered.log`：既有全站Lab來源檢查通過；本章12段程式與11段輸出與修訂前逐字相同。
- `rebuild.log`：重建三步後 SHA256 不變。
- `browser.log`：圖表、5 SVG、11按鈕、29張詞彙卡、收合／鍵盤與離線fallback檢查，0個問題。
- `browser-details.json`：MathJax無錯誤、無殘留原始公式字串、手機頁面無橫向溢出。
- 已目視 `screenshots/` 的模型、MLE、FLDA及手機測驗局部截圖；長矩陣公式依既有頁面樣式在公式容器內橫向捲動。

## 重跑

在專案根目錄執行：

```bash
python tools/build_page.py classification
python tools/rebuild_content.py classification
python tools/inject_data.py classification
python tools/validate.py --page classification
python tools/verification/classification-20260928/verify_content.py
node tools/verification/classification-20260928/inspect_browser.js
SHOT_DIR=tools/verification/classification-20260928/screenshots node tools/browser_check.js classification
```

`verify_content.py` 可選擇傳入修訂前HTML，核對Lab與FRAMES不變；原版可從 `provenance.json` 的基準commit取得。
只改文字與排版，使用 `rebuild_content.py` 保留既有烘焙資料，不須重跑模型。

## 寫回專案後

六個檔案已寫入實際專案並逐位元核對，實際路徑上的內容與結構檢查再次通過，見 `installed-checks.log`。
`git diff --check` 指出兩行移動後的 Lab 表格有行尾空白；這是原始 `Predicted` 輸出，依教材逐字保留要求維持不變。
