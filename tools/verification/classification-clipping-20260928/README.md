# Classification 公式裁切與閱讀修正

## 原因與修正

原有行內MathJax規則 `overflow-x:auto; overflow-y:hidden` 裁切了超出基線容器的帽子、分數及上下標。前次檢查只抓解析錯誤與頁面橫向溢出，未檢查字形被容器裁切。
本次使用分類頁的 `page_css` 解除行內公式裁切；長推導改用原有可橫向捲動的獨立公式。其他章節樣式未改動。

## 驗證

- 同一回歸腳本，1280px與390px在修正前各抓到58個裁切容器，修正後均為0。
- 正文、全部收合區及43個測驗選項回饋均檢查；修正後無字形裁切、MathJax錯誤或未容納的長行內公式。
- 頁面無橫向溢出；長獨立公式在自己的容器內捲動。
- LDA互動覆蓋處處平手及先驗不同的全域勝者。
- 標準瀏覽器互動驗收0問題；12段Lab程式、11段輸出與所有烘焙資料不變。
- 獨立重算一維／多變數判別式展開，以及Caravan同一測試集的比較。
- 重建冪等、分類頁結構驗證0錯誤及0警告。SHA256見 `provenance.json`。
- 已目視公式速查、判別推導與生成式用途的桌面／手機截圖。

三路讀者全文審讀及修正對照見 `reader-audit.md`。最終內容仍限classification；來源為 `tools/enrich/enrich_classification.py`、`tools/pages.py`。

## 重跑

```bash
python tools/validate.py --page classification
python tools/verification/classification-clipping-20260928/content_check.py
node tools/verification/classification-clipping-20260928/check_formula_clipping.js
```

重現舊版可將基準commit的classification.html匯出為檔案，作為JS腳本第一參數，第二參數指定 `before`；舊版預期exit code為1。內容檢查預設由Git取得基準版，亦可將基準HTML路徑作為第一參數。
