# 補充、課前與 Python 附錄：來源教學清理

2026-09-10。16 頁母檔已完成組裝及局部生成；未重跑 Lab、模型、隨機模擬或 FRAMES。最終全站 build / browser 由主代理統整。以下是實際範圍，不宣稱刪盡所有自行撰寫文字：保留來源概念的中文教學、概念互動及無須自訂資料計算的觀念題。

## 可審查的精確變更

- `quiz-cleanup-review.md`、`quiz-cleanup-proposal.diff`：逐項來源核對後刪 46 個非來源數值計算題，機器清單 `supplements-removed-questions.json`。不是依 quiz ID 或數字有無判定。
- `examples-cleanup-review.md`、`examples-cleanup-proposal.diff`：逐一列出移除片段、原母檔行號及保留一般公式的理由。人工 backprop 更新、額外 Lipschitz 下降定理、指定自訂統計手算与三段 P2 自訂程式已移除。
- `supplements-deduplication.json`：重複 DataFrame 卡、重複或整份長輸出、P6 跨章完整 Ridge Pipeline 的來源與保留位置。
- 原始完整備份僅供本機還原，不應發布。兩次初始寬預案被自動審查拒絕；改為附全文精確 diff 與來源核對的預案後均已核准套用。没有未解的審批阻礙。

## 逐頁結果

| 頁面 / 母檔（tools/enrich/） | 本次刪除 / 整理 | 核實保留的教學與來源 |
|---|---|---|
| deep_learning / enrich_deeplearning.py | 人工 x=2,y=1 權重更新、額外 L-Lipschitz 定理與 proof；移除製作報告；更新收合標題，不再聲稱含手算更新 | ISLP Ch10 §10.7.1–10.7.4 梯度/鏈式法則/正則化、官方 Ch10 Lab；qEx1–4 均對應原書網路參數、softmax/CNN 或原 Lab 結果，全部保留 |
| 00a_why_code / enrich_00a_why_code.py | 無已核實需要刪的原 Lab 教學；共用製作報告清空 | Ch01/02 原 Lab 的讀 code / 執行 / 解讀輸出路徑；沒有冒稱此頁有獨立課程 PDF |
| 00b_setup / enrich_00b_setup.py | 刪製作報告，保留安裝資訊 | 課程指定環境、本機安裝、套件版本及 kernel 核對是操作教學，不是研究重現報告；原 imports 與資料讀取路徑保留 |
| 00c_ai_assisted / enrich_00c_ai_assisted.py | 沒有核實需刪的原 Lab 片段 | 程式協作、提供錯誤情境與驗證結果是此課前頁主題；Ch01/03/05 原 Lab 作為驗證對象；不假裝 AI 協作流程出自統計講義 |
| s1_probability / enrich_s1_probability.py | 通勤五筆資料的手算/表、獎勵仿射數值例、方差單位換算數值例、9 次測量 SE 算例及指定自訂題 | Seeing Theory Ch1/PDF：機率、期望、變異與一致性；一般期望/變異法則及證明保留，必要概念圖保留 |
| s2_conditional / enrich_s2_conditional.py | 1%/90%/5% 篩檢、五人班長副班長數值段/表及其自訂計算題；修正殘留「四題」來源說明 | Seeing Theory Ch2/PDF pp.19–30：條件機率、Bayes、全機率、排列/組合公式及證明保留；基準率概念題保留 |
| s3_distributions / enrich_s3_distributions.py | λ=2 的 Poisson/等待時間額外數值計算、指定自訂題；修正殘留「四題」說明 | Seeing Theory Ch3/PDF pp.31–40：PMF/PDF、分布族、抽樣平均、CLT/LLN；Poisson/Exponential 一般公式/推導完整保留；骰子同源示例保留 |
| s4_inference / enrich_s4_inference.py | mean52/sigma10/n25 的 CI 手算、[2,4,4,8] 五次 bootstrap 表及其懸空指涉，指定計算题 | Seeing Theory Frequentist Inference 網頁/PDF：SE、CI、檢定/錯誤、bootstrap 定義/一般式；保留核心概念題。頻率學派 CI 解讀題的端點只是已知前提，不要求計算已刪算例 |
| s5_bayesian / enrich_s5_bayesian.py | 7 正 3 反 MLE/Beta 手算、Beta(20,20) 比較表及相關自訂計算題 | Seeing Theory Ch5：概似、先驗/後驗、Beta 密度/正規化/共軛更新、後驗平均的一般公式及推導保留；概念互動保留 |
| s6_regression / enrich_s6_regression.py | 五點 OLS/殘差靜態手算、三組 A/B/C 人工 ANOVA 表与指定計算題；EX 清空 | Seeing Theory Ch6/PDF pp.55–66：相關、OLS/RSS、ANOVA 平方和、F 統計與條件、一般證明保留。必要 OLS 拖曳圖的五點示意資料保留；不當作原書實驗 |
| p1_python_basics / enrich_p1_python_basics.py | 新添 mse=25.5738 f-string 小例，非來源資料計算題；重複完整 DataFrame 卡（原 Ch01 cell26 留在 P4） | 原 Lab 數值與結果：Ch05 cell20 MSE25.573878…、Ch02 cell244 16.54% 格式化題；Series 字典範例保留 |
| p2_flow_functions / enrich_p2_flow_functions.py | 三段自訂 mpg if/values loop/above_threshold 程式、新添 above() 前言、自訂 scope 題；修正「上面的 if」懸空指涉 | Ch02 cell240 原 zip 加權和、Ch05 cells24/26 evalMSE、cell59 boot_SE 原函式與英文 code、原 lambda/錯誤訊息保留；沒有重跑 |
| p3_numpy / enrich_p3_numpy.py | 自訂陣列/broadcast/seed 計算題；只去掉 column-mean 卡重複完整矩陣 output | Ch02 cells54/61 reshape/view、138/158 索引、89/91 axis mean、原 RNG/seed 語法均保留；真实 X/A 原例題保留 |
| p4_pandas / enrich_p4_pandas.py | 自訂混合 frame/join 計算題；去掉 huge unique 與完整 Auto 表的重複輸出，code/來源連結保留 | Ch01 Series/DataFrame/groupby（cell78）、Ch02 Auto/缺值、真实 loc/iloc 原例与必要短結果保留 |
| p5_visualization / enrich_p5_visualization.py | 去掉 reading helper 新造的通用 savefig 前言；其餘已核實為原 Lab，沒有因長度任意刪 | Ch01 cells88–138 seaborn、Ch02 cells96–125 matplotlib，savefig/contour/imshow 原 Lab 範例保留於收合中 |
| p6_modeling_api / enrich_p6_modeling_api.py | 新添通用 API 前言、自訂數值比較題、重複 Ch06 Ridge Pipeline 區塊 | Ch03/05 原 API、模型 summary、evalMSE/LOOCV/CV code/output 保留；Ch06 cells122/124 的原 Ridge 實作仍在 enrich_modelsel.py |

## 明確保留、尚不能據此聲稱完全來源原例的範圍

- S4 一樣本 t 區間仍明列為連接 ISLP §3.1.2 的先備補充；不是 Seeing Theory 原 PDF 段落。按主代理「來源不確定或可能必要先備先保留」指示未刪。
- S3 骰子 CLT、S6 概念 OLS 圖及 DL 依 ISLP 圖10.20/10.21 的既有雙下降圖保留；沒有重跑模擬。必要概念圖示意資料與原 Lab 結果的來源標記不同。
- 本次沒有新增任何算例/模型比較/題目；未把整本外部教材搬入，沒有新增外鏈研究。
- `.ver-note` 的實際顯示由 root 共用 helper 清空；S1–S6 手寫同類 HTML 已移除。課程原 seed code、00b 安裝版本、官方 Lab URL 中版本錨定仍保留，不用關鍵字誤刪。

## 生成與验證

- `generate-supplements.py` / `supplements-generate.log`：16 頁均生成成功，從既有 HTML 擷取 FRAMES；未呼叫 frame generator。
- 生成前唯讀組裝：16/16 成功。保留 quiz 數量依序為 11,8,10,9,3,2,5,9,2,3,5,9,8,6,12,6；沒有題數配額。
- 唯一空 EX 為 `s6_regression`；root 已設 `show_exercises=False`，母檔 `BODIES['exercises']` 也已實際清空。
- 原 `HC.onDetail('w15detail-function-lab', {close...})` 停 timer / 同步按鈕的 hook 保留；沒有新增動畫或模擬播放。
- 最終全站 build、原 Lab 逐字檢查與 browser 結果由 root 整合補入；此檔不把尚未完成的最終驗收寫成通過。

## 最後可見文字核對

- 00b qFix：25.57 與 23.80 是 Ch05 不同流程的原結果，但「兩同學跑同碼」不是來源原例。依主代理核定改為無數字的執行差異檢查概念題，保留 kernel/資料/seed 檢查。
- P3「三格併一張卡，輸出仍逐字」屬製作編排報告，已刪 note；原 cells38/40/48 code/output 不變。兩頁已局部再生成。

## 最終瀏覽器結果

- `supplements-browser.log`：16 頁完整測試完成；15 頁 OK，DL 首輪 Puppeteer 曾報「控制鈕無法操作：回到 256／128」，沒有 JS/pageerror 或公式排版錯誤。保留原失敗 log，未掩蓋。
- `browser-supplements-diagnostic.js` 只在既有 checker 副本加上 exception/祖先 details/位置診斷，未改共用 checker。`supplements-browser-final.log`：最後修文的 00b/P3 加上 DL 同流程補測，3 頁均 0 問題；首輪 DL click 失敗沒有復現。因此只能判定為暫發、未重現，不能宣稱已找到確切競態原因。
- `check-dl-reset.js` / `dl-reset.log`：在參數量收合區展開後，先把 h1/h2 改為16/8，再用實際 pointer click 按原 reset 按鈕，3 次均回到 256/128，總參數 235,146。未修改已正常的 reset 函式。
- 已實看 DL 預設桌面閱讀全頁、S4 手機全頁，並檢視原尺寸局部：公式、段落、框線可讀，無明顯遮擋或裁切。大尺寸完整互動截圖在 `supplements-shots/`，僅本機留存；正式全站27頁截圖由 root 的 `final-views/` 統整。
- 主代理回報本輪全站結構/原 Lab 逐字驗證：215 Lab、0 failure；全27頁最後 capture 0錯誤、hash一致。以上全站數字由主代理執行，本代理獨立執行的是本節16頁browser、3頁必要補測與DL reset斷言。
- 所有所屬內容與報告至此凍結；未 commit/push，交由主代理處理。
