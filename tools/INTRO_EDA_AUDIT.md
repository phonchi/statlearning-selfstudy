# 第一章：統計學習導論與 EDA

更新：2026-09-05。基準提交：8cff7d5。只重寫第一章，並更新首頁與相鄰頁的章名導覽。

## 教材與內容

內容依使用者指定的 `nsysu-math524/static_files/presentations/01_Introduction.pdf` 新版 39 頁；
SHA256 為 `f4d025d510add4184d032000f170885916fd3e1c80fce0d2057cc9abd89b6e91`。
該檔仍是課程 repo 未提交的變更，本次不發布此 PDF。公開連結固定到 a0c8b9910a450ae2328adff5f8d8665479be71f5 的 42 頁舊版，
頁面已說明版本與新舊頁次對照。

| 段落 | 新版講義頁次 | 修訂 |
|---|---|---|
| 開場 | 6、21 | 以理解任務、建模與解讀為目標 |
| 新聞 | 9–15 | 保留歷史案例與年份，按應用分組 |
| 相關領域 | 7、16–19 | 說明統計、ML、AI、資料探勘與資料科學的重疊及側重 |
| 基本學習問題 | 20–22 | 精簡 X/Y、監督／非監督、迴歸／分類、預測／推論 |
| 推薦系統 | 23–24 | Netflix 評分矩陣；區分應用名稱與學習設定 |
| 十個想法 | 25 | 原序、作者與年份、每項一句目的；長篇著作名留講義 |
| EDA | 26–29 | 資料表、摘要統計、依問題選圖 |
| 資料集與讀圖 | 30–35 | 完整總表與五組資料讀圖例子 |
| 繼續學習 | 36、38–39 | Lab、Python 附錄及資料入口 |

排除行政、評分及考試日期。原先冗長的公式、模型比較與安裝說明改連相關章節。
保留 introduction.html，以及 regcls、predinfer、notation、dx-wage、dx-smarket、dx-nci 等既有書籤。

## 資料集總表

22 筆、五欄：名稱、簡介、N、P、資料性質。依講義原序列出。
合成共 6 筆：Advertising、Carseats、Credit、Default、Fund、Portfolio；其餘 16 筆為真實資料。
Advertising 依使用者明確確認標為合成，連至使用者指定的 Kaggle 頁；其餘提供官方資料說明連結。
Credit 簡介修正為 400 位顧客。N/P 沿用講義資料版本，附索引、Fund 轉置與 Khan 訓練／測試等短註。
沒有增列分析用途欄，完整官方總覽連結保留。

## 圖形與自測

五組共九張圖，均使用原生 SVG，沒有增加無教學用途的播放控制。

- Wage：600 筆固定抽樣散點、全體 3000 筆的四歲分箱平均、各年平均與教育組 Tukey 箱形圖。薪資單位為千美元。
- Smarket：三個 Lag 的漲跌分組箱形圖，以及八個數值欄的 Pearson 相關熱圖。
- NCI60：先以基因資料做二維投影，再用癌症型別上色；不把標籤放進降維。
- Auto：392 筆的 mpg 直方圖及馬力／mpg 散點，區分原始 CSV 與套件版資料。
- Bikeshare：按 0–23 時分組的原始租借量平均，明標本站 EDA 補充，不當成講義中的迴歸係數。

箱形圖改用 Q1/Q3、1.5 IQR 範圍內的實際觀測值鬚及離群點。
表格與圖形在手機可橫向滑動，避免直排文字或縮到無法閱讀。
16 題自測的答案位置分散為 A 5 題、B 6 題、C 5 題，題目與回饋保持綁定；26 張詞彙卡同步重寫。

## 驗證

記錄位於 `verification/intro-eda-20260905/`：來源與表格數量、數值核對、全站結構、視覺主張、
連結、第一章桌面／手機及離線顯示、完整資料表與舊書籤檢查。
全站結構 20 頁零失敗；115 個外部連結零失敗、2 個 Colab HEAD 405 警告（一般 GET 已在前輪確認可開啟）。
第一章瀏覽器驗收零問題；自測正解位置與移動版的旁欄寬度另外核對。
Kaggle 的 HEAD 回應為 404，但一般 GET 為 200；連結驗證器對 HEAD 404 補做 GET，再判定是否失敗。

重建第一章：

```bash
python3 tools/build_page.py introduction
python3 tools/enrich/enrich_intro.py
python3 tools/inject_data.py introduction
python3 tools/build_page.py
python3 tools/build_index.py
python3 tools/validate.py
python3 tools/check_visual_claims.py
node tools/browser_check.js introduction
```

正文在 enrich_intro.py，完整資料表在 intro_catalog.py，讀圖區在 intro_visuals.py；
frames() 使用 m524 的 Python 執行 gen_intro.py，主建置用系統 python3。
只在需要重新建立章節骨架時才使用 `build_page.py introduction --force`，隨後必須重跑 enrich 與 inject。
