# 現行教材對齊與全站驗收

已完成首頁、26 個教學頁面與 README 的本機修正。以遠端 `phonchi/nsysu-math524` commit `7c215512b38ed57a98d3289d83030c582a03eeb4` 為教材基準；來源 PDF／notebook 的 SHA256 見 [sources.json](sources.json)。原課程目錄有未提交的導論 PDF，實作使用獨立遠端快照，保留原有修改。

網站 Git root 為 `/home/phonchi/statlearning-selfstudy`，本次基準 HEAD 為 `ee5df3cfee4bbf105a5f47db193cb45d7b0fe240`。本報告記錄提交前的驗收快照，發布狀態以 Git 記錄為準；最終產物雜湊見 [final-manifest.json](final-manifest.json)。

## 完成項目

| 要求 | 結果 |
|---|---|
| 課程實例完整貼合 lab | Wage 使用全部 3000 筆、年齡四次／年份一次配適與信賴帶；NCI60 保留全部 14 類及兩個投影視角；Auto 補齊密度、KDE、jointplot、完整 pairplot；Bikeshare 改回月份／小時模型係數。非線性 Wage 不再抽樣或排除高收入者，digits 使用全部 1797 筆，重抽樣圖採 lab 的 OLS 與 degree 1–5。 |
| 移除講義頁碼及 lab cell 定位 | 學生可見正文、來源、回饋、詞卡及連結均清除；程式和原始保存輸出保持原文。內部來源屬性仍能核對完整引用。 |
| 改用現行課程連結 | 共用設定、個別課程連結、Colab、資料下載及 README 已更新，現行課程入口使用無年份網站。資料中的真實年份保留。 |
| 補齊 LDA／Fisher 及講義內容 | 補白化、Mahalanobis 距離與先驗、W/B、廣義特徵值、二類方向、多類秩上限、降秩限制及 Iris 實算；逐章補齊其他講義主題。 |
| 移除內容量介紹 | 移除節數、圖數、題數與詞彙卡數量標語；實際自測、詞彙卡與操作進度保留。 |

逐章來源到網站落點、數學修正及核對範圍：

- [導論與先備附錄](intro-appendices.md)
- [統計學習、迴歸、分類、重抽樣](classification-core.md)
- [模型選擇、非線性、非監督式、樹、SVM、深度學習](advanced-core.md)

講義的學期行政／評分資訊不複製到自學正文；重複主題整合於同一段落。深度學習維持官方 lab 補充單元。正確且有教學用途的概念互動保留。

## 驗證結果

| 檢查 | 結果與證據 |
|---|---|
| 全站來源／結構／生成規則 | **確認無誤**：26 頁、0 失敗；[run.log](run.log)、[validate.log](validate.log) |
| 可見定位、舊連結與學習功能 | **確認無誤**：[reader-contract.log](reader-contract.log) |
| 完整程式與輸出引用 | **確認無誤**：232 張呈現後程式碼卡均對回最新引用 cells；[rendered-lab.log](rendered-lab.log) |
| 現行外部連結 | **確認無誤**：154 個連結、0 失敗；不支援 HEAD 的端點以 GET 再查；[validate-network-final.log](validate-network-final.log) |
| 來源規則與統計模式測試 | **確認無誤**：4 + 9 項測試；[reader-tests.log](reader-tests.log)、[statistics-contract.log](statistics-contract.log) |
| 統計先備獨立數值／幾何 | **確認無誤**：六頁的機率、區間、Beta 正規化、OLS、零分母及種子重現；[statistics-browser.log](statistics-browser.log) |
| 圖表數值與新增公式 | **確認無誤**：[intro/numerical.log](intro/numerical.log)、[fisher-run.log](fisher-run.log)、[advanced-numerical.log](advanced-numerical.log)、[resampling-run.log](resampling-run.log) |
| 重建一致性 | **確認無誤**：27 個 HTML 加 README 共 28 個產物完整重建後位元不變；[idempotence.json](idempotence.json) |
| 差異格式 | **確認無誤**：`git diff --check` 通過，記錄於 run.log。 |

瀏覽器使用本機 Chromium，以 1280px 桌面及 390px 手機檢查全站，涵蓋滑桿、按鈕、自測回饋、翻卡、Chart.js、SVG、MathJax 與 CDN 失效。首頁另檢查兩種尺寸、全部章節卡及實際進入章節的導覽。

[首輪全站 log](browser.log) 保留原始 7 個問題：安裝頁執行序號 DOM 被誤刪，以及導論使用尚未更新完成的 FRAMES。修正後的指定重測為 0 問題，見 [安裝頁](intro/setup-browser-fixed.log)、[導論診斷](intro/browser-diagnosis.log)、[最終圖表逐項檢查](intro/section-capture-final.log)、[非線性／非監督式](browser-frames-final.log) 與 [首頁](home-browser.log)。初次失敗紀錄沒有刪除，也不把它寫成全綠。

看圖另修正了原本不可見的 Wage 信賴帶、Fisher 表格擠字及手機長公式，並修正浮動導覽遮住正文；[Fisher 最終視覺驗收](visual-review/fisher-visual-review.md) 包含截圖與 1360／1361／1440px 邊界檢查。手機 pairplot 可捲至右端，頁面本體溢出為 0。

## 圖像與重現

- [導論全部 12 張圖總覽](intro-all-plots.png)；完整局部截圖在 [visual-review](visual-review/)。
- [首頁與全部 26 個教學頁的首屏總覽](all-pages-overview.png)；完整長頁截圖在 [screenshots](screenshots/)。總覽只截取各頁開頭，不能替代完整頁面與互動檢查。
- 新圖完整數值、來源、種子與版本保存在 `intro/frames.js`、`resampling-frames.js`、`frames/nonlin.js`、`frames/unsup.js`；產生器及完整 log 均保留。
- 可執行的獨立數值核對為 `intro/check_numerical.py`、`check_fisher.py`、`check_advanced.py`，精確命令見各章報告。

重新執行本機來源／組裝檢查：

```bash
python3 tools/verification/course-alignment-20260908/run_checks.py
```

若重新計算圖表，須先在 `m524` 環境執行相應產生器；保存的新資料可用 `tools/rebuild_content.py --frames-file STEM=PATH` 組裝。不得只改文字而保留已失效的舊 FRAMES。將來同步教材時，指定新快照的 `M524_COURSE`、重建來源索引並重新核對引用。

## 限制

- 三頁因保留完整資料超過原先 300 KB 建議：導論約 477 KB、非監督式約 344 KB、非線性約 336 KB；屬檔案大小提醒，渲染與互動已通過。
- 原 lab 的 bootstrap 圖未指定種子；本站使用相同方法並固定 seed=0，信賴帶不宣稱與原 notebook 隨機結果逐像素相同。
- 大型神經網路、森林與 boosting 實驗沒有全部重新訓練；其引用程式及保存輸出已完整核對。逐章報告區分數值重算、來源核對與原創概念模擬。
