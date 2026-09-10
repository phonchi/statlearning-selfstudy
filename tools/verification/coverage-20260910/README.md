# 全站教材補完與來源核驗（2026-09-10）

已盤點 **26 個教材頁＋首頁**，補寫 **23 頁**；共有 **91 則正式證明預設收合**。正文保留定義、完整公式與條件、演算法、直覺及可自行計算的例子。三個課前頁核對指定內容後保留。

本輪以 **11 份講義／Recap，共609頁**、Lab、指定課本及直接相關外部教材為來源。來源圖像頁亦已檢視，沒有把標題索引、名詞出現或HTTP200當成內容完整的證據。基準Git HEAD為 `837109b12c0b90f66d6048fa25abbfcc7b09a3a8`；本報告記錄發布前驗證；正式發布狀態以 GitHub Pages 的部署紀錄為準。

## 成果入口

- [網站首頁](../../../index.html)
- [SVM完整primal／dual](../../../support_vector_machines.html#w10-primal-dual)
- [全部27頁截圖總覽](all-pages-overview.png)；[最終截圖與雜湊](final-reading.json)
- [最終逐來源台帳](source-links-final.json)：418筆逐頁／逐URL紀錄，包含跨頁重複及文字截斷；不等於418份不同全文。
- [最終檔案、證明數及驗證清單](final-manifest.json)

## 各組來源與補完紀錄

- 第1–6章第一輪：[audit-ch1-6.md](audit-ch1-6.md)。其中外鏈未讀的舊快照已由下列終表取代，不能單讀舊表判斷現況。
- 第1–3章外鏈終表：[audit-links-ch1-3.md](audit-links-ch1-3.md)、[逐URL結果](supplement-links-ch1-3.json)。
- 第4–6章外鏈終表：[audit-ch4-6-links-final.md](audit-ch4-6-links-final.md)。
- 第7／8／12章：[audit-ch7-8-12.md](audit-ch7-8-12.md)。
- SVM：[audit-svm.md](audit-svm.md)。
- 深度學習、課前、統計與Python附錄：[audit-supplements.md](audit-supplements.md)。
- [講義來源定位修正](source-locator-fixes.md)、[609頁來源指紋及頁面清單](sources.json)。

最終台帳已結清所有原先未分類的直接教學連結。資料、行政、歷史背景、整書／整課入口按講義用途界定，不把整套外部網站全部重寫為教材。受阻原文保留實際錯誤與權威替代，**不宣稱已閱讀無法取得的原文**。

## 驗證結果

- `validate-all.log`：26頁，**0失敗**。三個SIZE建議警告為導論476KB、非監督372KB、超越線性350KB；它們在基準版已超過300KB，未為消除警告刪教材。
- `reader.log`、`visual-claims.log`、`wording.log`：閱讀契約、圖表數值不變量與台灣術語檢查通過。
- `lab-rendered.log`：**245張**Lab程式／輸出卡逐字核對，**0失敗**。`preservation.json`確認43個既有FRAMES及11份Lab來源索引與HEAD相同，沒有重跑Lab。
- 各組`*numer*.log/json`及`numeric-ch7-8-12.log`保存獨立驗算：有限差分梯度、OLS/FWL/F檢定、PRESS、PCA/PLS、GMM、XGBoost、SVM/SVR等。
- 各組最新browser log均為**0問題**。第二輪新增內容使用`ch4-6-linked-browser.log`及`audit-links-ch1-3.md`指向的最新結果，取代第一輪相應快照。
- `final-reading.log/json`：最後27頁重新載入、91個proof預設均關閉，沒有JS錯誤或頁面橫向溢位；桌面、證明展開、手機截圖保存在`final-reading/`。主代理已實際查看三個全頁分板及代表性的長證明與手機畫面。
- 全站目前197個外鏈。`network-links.log`中的三個NTU PDF在Python嚴格TLS出現Missing Subject Key Identifier；`network-browser.json`以Chrome確認三者皆HTTP200且為PDF，**沒有忽略憑證錯誤**。其餘原檢查及新增MAPIE的GET通過。原始失敗記錄保留，不偽造Python全綠。
- `git diff --check`的新增尾端空白出現在逐字保存的Lab表格輸出，依原始輸出保留；非HTML來源另行檢查。

## 閱讀與維護

來源母檔及資料母檔已更新，HTML仍由原有工具生成；SVM較長補文在`tools/enrich/svm_completion.py`。共用`lib.proof(pid,title,body)`沿用現有details樣式與MathJax展開重排。全站使用方式已告知證明可按需展開，來源定位與相應詞卡／題目已同步。

`run.log`彙整各項命令結果；初輪發現後已修的失敗與最後通過結果分別保留。最終檔案以`final-manifest.json`及`final-reading.json`的雜湊為準。

## 版本保存範圍

教材、母檔、台帳、驗算與檢查腳本、log、最終 `final-reading/` 截圖及全頁總覽納入版本保存。第三方原文快取、原講義渲染和重複的中間截圖保留在本機，未隨網站發布；報告中對這些本機證據的歷史路徑仍保留。
