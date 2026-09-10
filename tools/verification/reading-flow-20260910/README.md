# 全站閱讀層次整理（2026-09-10）

26個教材頁已依「直覺＋核心公式＋短例」整理。完整計算、長表、Lab／輸出、進階方法與相關練習依主題收合，正文保留主要互動及概念自測。新增365個reading-detail包含各頁的書目、複習卡等入口；一般開頁均關閉，最多兩層。

## 使用者指定內容

- 導論的「同一組資料，親手比較摘要」「中位數的穩健性與相對效率」及其證明、「資料表的形狀與合併鍵」與來源說明全部刪除，不放回收合區。EDA保留八種統計量的直覺與用途。
- 第2章正文保留維度詛咒的直覺與短例；球殼、球／立方體體積、Gamma／Stirling、半徑計算、長表及互動圖收進同一個計算細節入口。
- SVM完整primal–dual／KKT、各章進階估計／演算法仍可展開取得。原錨點與課程內容保留，依使用者指示刪除的導論證明例外。

## 逐頁紀錄與畫面

- [第1–6章](ch1-6.md)
- [第7／8／9／12章](ch7-8-9-12.md)
- [課前、統計／Python附錄與深度學習](supplements.md)
- [全26頁的收合標題、自測與文字清單](reading-inventory.json)
- [全27頁含首頁的畫面總覽](all-pages-overview.png)
- [最終瀏覽器畫面與檔案雜湊](final-views.json)，完整畫面在final-views/；三個review-board已實際檢視。

## 驗證結果

- 全站validator：26頁0失敗；4個SIZE建議警告（收合不等於刪除HTML內容）。
- 閱讀層次檢查：預設關閉、層級不超過二、原錨點保留、核心自測與導論指定刪除均通過。
- 26頁完整browser_check通過，涵蓋展開後真正操作所有控件、MathJax、Chart尺寸、手機版與CDN失效；最後27頁閱讀畫面檢查亦0問題。
- 深連結能打開目標祖先；Ch2／Ch3圖表重開保留滑桿；AdaBoost及P2 evalMSE播放中收合會停止、保留畫面，重開不自動播放；都有獨立專項結果。
- 原有245張Lab程式／輸出卡，最終逐字檢查0失敗。43個FRAMES與11份Lab索引相對基準完全一致，沒有重新跑Lab或烘焙實驗。
- 閱讀契約、視覺數值不變量與台灣術語檢查通過。

## 此輪修復的驗收問題

原生HTML解析會把部分TeX中的裸小於號誤作標籤；相關章節已在解析前處理數學區的比較符號，保護pre/code原文。原始失敗與修復後browser log都保留。

Ch1–6初版組裝使用BeautifulSoup預設空白處理，使10張程式卡縮排受到壓縮。已改為preserve_whitespace_tags，從原enrich BODIES重建，沒有修改Lab或放寬原checker。lab-rendered.log保留當時10個失敗；最終以[lab-rendered-after-whitespace-fix.log](lab-rendered-after-whitespace-fix.log)的245張全通過為準。受影響程式卡的瀏覽器與四空格縮排亦已核對。

## 實作與保存

共用入口是lib.detail與HC.onDetail；MathJax排版依序執行，展開後更新圖表尺寸，收合時呼叫所屬停止回呼。各章的閱讀組裝分別保存在reading_flow_ch1_6.py、reading_flow_ch7_8_9_12.py與reading_supplements.py；enrich已接入。Ch1–6組裝使用既有工具環境的beautifulsoup4。

此報告為發布前驗證快照；部署狀態另由GitHub Pages紀錄確認。腳本、台帳、log、最終畫面與總覽納入版本；重複中間截圖與隔離試頁保留本機。所有歷史失敗須配合後續修復紀錄閱讀，不能拿早期log判斷最終版本。
