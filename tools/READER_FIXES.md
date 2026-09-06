# 獨立讀者審查修正（2026-09-06）

依 `READER_AUDIT.md` 的 F01–F20 與 S01–S05 修訂。四區、授課章序與選讀定位保留；同次發布包含先前新增的 Seeing Theory 六頁統計先備教材。

## 修正對照

| 報告 | 已完成修訂 |
|---|---|
| F01 | P1 普通字串中的雙大括號改為實際 Python 寫法；字典、百分比、f-string 與速查同步，補正未指定精度時的六位小數說明。 |
| F02 | PCA 引用新增既有 cell 23，順序為建立→fit→transform→components_，來源編號同步。 |
| F03 | 自然樣條固定 K=內部節點、含截距，由 K+4 扣兩個自然邊界條件得 K+2；正文、回饋、速查、詞卡一致。另釐清 d 次多項式含截距有 d+1 參數。 |
| F04 | 交代外層 scaler 與 RidgeCV／ElasticNetCV 內層 CV 的界線；新增無假輸出的 GridSearchCV(Pipeline) 概念範例，以折內標準化與 MSE 選 α。刪除 RidgeCV 的 warm-start 歸因。 |
| F05 | Smarket 全資料探索後的 2005 比較明標為教材示範，不當成選模後獨立測試證據；保留原始數字。 |
| F06 | 全章與詞卡區分期望風險下限和有限測試集的觀察誤差，包括圖說、JS 狀態與速查。 |
| F07 | 速查／詞卡補巢狀模型、正殘差自由度、含截距、滿秩與訓練 OLS 等條件；單一 PVE 與累積 PVE 分開。 |
| F08 | KNN 自測修正「兩個一定」的判斷；非參數、距離／尺度、重複 X、零訓練誤差及相對彈性指標均加上正確範圍。 |
| F09 | S4 速查修正為 SE 恆等式不要求研究者已知 σ；未知時以 s/√n 估計。 |
| F10 | RSE 估 σ，RSE² 估 σ²。 |
| F11 | 測試 R² 的 TSS 基準改為這批測試反應值的平均。 |
| F12 | 獨立與不相關分開；相關誤差不預斷 SE 偏差方向；補正確條件平均及 E[ε｜X]=0。 |
| F13 | 正課標準化洩漏自測與 P6 一致：流程有問題，分數方向與大小依資料／模型決定。 |
| F14 | 區分嚴格逐折剪枝路徑與 lab 的外層訓練候選格點；題庫／詞卡同步。圖形出處亦核對為 Hitters。 |
| F15 | Hitters 明載固定 50 epochs、ErrorTracker 只記錄；移除不存在的早停及單一成因歸因。 |
| F16 | 卡片維持安全的純文字渲染。原 125 張問題卡中，一張隨內容修訂成純文，另 124 張統一移除格式標籤／解碼 entity；全站卡片皆符合純文字契約。 |
| F17 | 白字來源標籤移到共用 CSS，移除六頁專用覆寫，統一新舊頁面的可讀性。 |
| F18 | pandas 字串可能直接串接且沒有警告，numeric_only 的正文／詞卡同步。 |
| F19 | P5 改教兩組差值的不確定性，自測不再以各組 CI 是否重疊作充分判準；新增 S4 回補連結。 |
| F20 | 線性／分類係數以條件關聯或模型平均差解讀；首次解釋與詞卡同步區分因果推論。 |

## 閱讀銜接與精簡

- S01：正課 Bayes、係數推論、bootstrap 增加直達 S2／S4 的可選回補連結，保留直接進正課的路徑。
- S02：P3 的 reshape 指向 P6 實際操作；P5 分別連到雙標圖與樹狀圖。
- S03：P3 亂數示範與詞卡不再暗示每次平均都更接近，並連到 S3／S4 分清 LLN 與重抽樣。
- S04：S5 篩檢回顧縮為一段並連回 S2；S3 相鄰 LLN 提醒合併，保留自測。
- S05：00B 統一完整 traceback；S2 計數 EX4 標選讀；P1／P2 補程式變數、資料欄、索引與兩種參數的語境。

## 驗證時補修的同類字串問題

完整瀏覽器檢查發現深度學習公式速查的 LaTeX 被多跳脫一層，兩式產生 `Missing open brace for subscript`，其餘部分指令也未正確呈現。已修正整張公式表，並修正組合 lab 儲存格時被顯示成字面 `\n\n` 的分隔符。僅修組裝，未改原始儲存格或保存輸出。

## 驗證與重現

紀錄位於 `tools/verification/reader-fixes-20260906/`：

- `structure.log`：26 頁結構、來源、錨點、詞卡與題庫檢查。
- `reader-regression.log`：頁面上顯示的 P1 程式、PCA 呼叫順序及合成資料執行、正確 GridSearchCV 範例的折內 scaler、卡片純文字、資料保留、深度學習程式組裝。
- `statistics-contract.log`、`statistics-numerical.log`：六頁來源模式及獨立數值／圖形核對。
- `visual-claims.log`：原有高風險視覺數值檢查。
- `browser-entry.log`、`browser-python.log`：課前／統計先備與 Python 附錄。
- `browser-core.log` 是首次十一章檢查，記錄兩處深度學習公式問題；`browser-final.log` 是補修後的深度學習與統計學習複驗。其餘正課頁在首次檢查已通過。
- `links.log`：外部來源檢查。兩個既有 Colab 網址會對 HEAD 回 405，獨立記錄為警告。
- `baseline.json` 保存修訂前的 26 份來源索引、42 個 FRAMES 物件與 187 份保存輸出雜湊；回歸測試確認逐一保留。
- 截圖在 `/tmp/reader-fixes-20260906/`，依專案規範不把圖片加入 repo。

```bash
python3 tools/rebuild_content.py       # 文字修訂：重用現有 FRAMES，不呼叫數值產生器
python3 tools/inject_data.py
python3 tools/build_page.py
python3 tools/build_index.py
python3 tools/test_reader_fixes.py
python3 tools/test_statistics_contract.py
python3 tools/check_visual_claims.py
python3 tools/validate.py --net
node tools/check_statistics_browser.js
SHOT_DIR=/tmp/reader-fixes-20260906/all node tools/browser_check.js
```

`test_reader_fixes.py` 使用本站 Python 與 BeautifulSoup；PCA／GridSearchCV 的合成資料驗證子程序使用既有 m524 Python，可用 `M524_PYTHON` 覆寫位置。它的資料保留檢查針對本輪文字修訂快照；日後若刻意重算圖表，應另外建立該次數值驗證，不能把歷史 baseline 當成永久禁止更新。

發布分支是 `main`，GitHub Pages 從根目錄建置。推送後以 Pages build 的 commit 與線上頁面確認發布，非只確認本機產物。
