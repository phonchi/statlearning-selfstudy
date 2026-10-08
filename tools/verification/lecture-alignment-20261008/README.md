# 第五章後半與第6、7、8、9、12章：講義對齊驗收

完成範圍：第五章PDF第22–42頁，以及後續五份正式講義。以第三、四章教學深度為參考，依主題整理收合說明；深度學習補充、先備附錄與第五章前半未改。

## 決定與來源

- 採正式講義範圍、依主題合併教學連結、完整自學深度。
- 主來源為當前課程PDF 與中文Lab；原檔雜湊與本次基準HEAD見 `source_manifest.json`。
- `coverage-final.json`：371個範圍內PDF頁面、181個跨文件去重的原註解URL，全部都有教學錨點。各章紀錄另外包含從正文發現的網址。
- 每章資料夾保存頁面／主題／Lab對照、原網址處理狀態及替代來源。受限或錯誤轉址的來源未冒稱讀過。
- 原始來源閱讀快取與基準HTML位於本專案的忽略目錄；公開證據提供來源、hash、對照與自寫驗證，不轉載外部全文。

## 教學與潤稿

- 新內容由 `tools/enrich/lecture_alignment_chN.py` 增補在既有閱讀整理之後；主章節與收合區相互銜接。
- 依使用者要求直接套用 speak-human-tw：完整逐句／逐段修改報告保存在各章；潤稿階段的公式、數字、程式、網址、id保護比對通過。
- 潤稿之後的讀者技術修正另記於 `reader-review.json`，不混作風格改寫。
- 三組獨立讀者全篇唯讀檢查連續性、一致性與正確性；20項具體發現逐項修正並複核關閉。根代理實際看圖另修正SVM預算符號的橋接，讀者亦確認無誤。

## 驗證

- `global-checks.json`：來源原檔hash、全部原錨點、原Lab程式／輸出、GEN/PAGEJS/DATA、生成器同步及冪等通過。
- 各章數學紀錄包含獨立推導或數值重算。新Portfolio、Auto殘差預測區間、分類置換檢定皆已實跑；原Lab已存輸出未重跑覆寫。
- 本機數值環境是 Python3.11.15、sklearn1.6.1、numpy1.24.4、scipy1.13.1；課堂清單是Python3.9.13。新增獨立範例已核對Python3.9語法相容，沒有宣稱在教室Python3.9實跑。
- 六章 validate 均0失敗；較長頁面有既有大小建議門檻的提醒，未為消除提醒刪減必要教學。
- `browser-report.json`：1440/390寬度，78個新增／改寫收合區的展開與收合、MathJax、無整頁橫向溢出、保留元件基本操作均通過。
- `browser/index.html`：全部156張展開截圖的可點選總覽。

## 重現入口

```bash
python tools/verification/lecture-alignment-20261008/source_inventory.py
python tools/verification/lecture-alignment-20261008/global_checks.py
python tools/verification/lecture-alignment-20261008/coverage_check.py
python tools/verification/lecture-alignment-20261008/browser_acceptance.py
```

來源索引以實際課程路徑為準。要重建歷史驗收，使用 `source_manifest.json` 的 baseline_head 與 source_sha256；已保存的 `inputs/` 不應以新的HEAD覆蓋後再當作原基準。
