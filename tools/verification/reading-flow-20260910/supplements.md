# 補充章與兩組附錄：閱讀主線整理

已完成批准的 16 頁閱讀精簡。內容母檔仍保留完整講義／Lab／公式／算例；將成套細節移入預設收合的 `details.qa-item.reading-detail`，沒有重跑 Lab 或烘焙資料，也沒有修改導論頁、共享樣板、pages、builder、validator、browser_check 或任何評分規則。

## 內容與來源

- 本組組裝器：`tools/enrich/reading_supplements.py`。16 個既有 enrich 母檔在最後呼叫 `apply_reading(stem, BODIES, PAGEJS)`；以指定段名、卡名或已核對的片段邊界組裝，沒有把所有程式碼一律隱藏。
- 重建入口：`generate-supplements.py`。逐頁從原 HTML 保留 `FRAMES_*`，載入母檔後只寫回所屬頁。
- 完整 ID、summary 和每題所屬閱讀層：`supplements-structure.json`。所有內容 ID 保留；原技術題移位後仍在相同頁，深連結由共用機制揭露收合祖先。
- 原 proof 可以位於一個主題 detail 內；最深為兩層。沒有三層巢狀，也沒有靠展開狀態實現預設隱藏。

## 逐頁完成內容

| 頁面 | 正文保留 | 收合內容 |
|---|---|---|
| deep_learning | 非線性、架構、前向／卷積互動、訓練／驗證、SGD概念題 | 成套Lab、參數量、backprop/手算/正則化/收斂條件、GD數值實驗、時間序列構造、移轉應用、雙下降；相關技術題及EX一起移位 |
| 00a_why_code | Auto學習迴圈、責任判斷、短例與概念題 | 另一份資料的完整讀表例與長速查；不擴寫既有主線 |
| 00b_setup | 可完成的Colab/Auto預設路徑、Ch02必要imports與讀圖命令、runtime/kernel提醒 | 替代環境比較、另一章完整imports、套件長表、本機版本與安裝、詳細排錯 |
| 00c_ai_assisted | 清理小任務、短完整提示、執行／核對／保存與概念題 | 分級、五要素、逐輪交付物與重現紀錄的完整對照表；既有進階統計解讀維持收合 |
| s1_probability | 母體／樣本、機率與頻率、期望、變異直覺、單位縮放短例與LLN概念 | 期望加法證明、變異數等價公式、樣本變異數/n−1整組、共變異數/不等式/LLN計算延伸 |
| s2_conditional | 條件機率、Bayes核心式、四格互動、獨立／互斥 | 集合定律、完整基準率算例連qBayes、counting整組連qCount/EX4 |
| s3_distributions | 分布用途、柱／面積、互動、抽樣分布、SE=σ/√n短例、CLT直覺與條件 | PMF/PDF總表、Poisson/Exponential、矩表、骰子完整算例、標準化極限記號 |
| s4_inference | SE核心式、CI/p值互動、兩類錯誤、基本重抽與概念題 | t區間、單雙尾完整數值算例、型二錯誤/檢定力計算、bootstrap SE公式 |
| s5_bayesian | 概似方向、Beta計數更新短規則、後驗互動、先驗強度、下一次預測均值 | 密度/正規化整組、共軛推導、概似比長算例、後驗加權分解及完整比較表 |
| s6_regression | 相關直覺、OLS拖曳、RSS/R²必要式、殘差診斷 | 相關與OLS係數公式、三組長手算、ANOVA整節連qAnova/EX4 |
| p1_python_basics | print、別名、索引／切片、字典、最小f-string與短輸出 | pandas字典應用、slice物件、逐欄格式化與完整迴圈輸出 |
| p2_flow_functions | 純Python if/for/def/return/default短例、核心迴圈與作用域互動、None規則 | 複合篩選、巢狀迴圈、evalMSE完整應用與timer、lambda/loc、boot_SE及準備步驟、完整traceback |
| p3_numpy | shape、reshape、成對索引反例、布林、廣播、axis、種子與短code/結果 | 長共享資料實驗、替代子矩陣寫法、完整錯誤、進階布林索引、變異數多寫法、相關矩陣與長輸出；保留共享/複本規則供EX |
| p4_pandas | DataFrame/Series、loc/iloc、讀檔缺值規則、groupby/concat與短實作 | 排序/累積/完整I/O、車名索引與長表、category、reindex、分塊中間輸出、其他長Lab輸出 |
| p5_visualization | 依問題選圖、Figure/Axes/ax關係、短畫圖code、基本存圖、誤差線判讀 | 完整函式地圖連細節題、子圖網格、多格式/dpi、更多圖法、函數網格與contour/imshow |
| p6_modeling_api | 最小fit/predict/score、設計矩陣、截距、切分/前處理、配對比較概念 | 完整summary、多指標/多項式比較、CV圖與完整程式、Ch06 Ridge/Pipeline跨章實作 |

各頁 authored reference 長速查也收合。共用 builder 另外處理書目、詞彙卡與題庫，本組沒有直接改寫 GEN。

## 動畫生命週期

只有 P2 的 evalMSE 連續播放新移入收合：

- detail ID：`w15detail-function-lab`。
- `HC.onDetail(...).close` 直接清除 `w15fnTimer` 並設為 null；不呼叫 reset、不呼叫 play、不改 `w15fnI`。
- 按鈕改為「▶ 重新播放」且 `aria-pressed=false`，符合原按鈕重新起跑的行為；重開不自動播放。
- `check-supplements-lifecycle.js` 實際確認：播放到 frame 1，收合後仍 frame 1、timer null；等待後不前進；重開仍停住，單步能接續。log 無 pageerror。
- P1讀程式、P2基本迴圈、P4 groupby、P6 fit/predict 等核心計時互動仍在正文，沒有為收合而改其行為。

## 驗證

- `supplements-generate.log`：16頁生成成功；已保留既有FRAMES，不執行任何Lab或frame generator。
- `supplements-structure.json`：16頁預設closed、無重複ID、最大details深度≤2；包含技術自測移位清單。
- `supplements-validate.log`：共用build後16頁全部0失敗、0警告。
- `supplements-browser.log`：16頁全部OK、0個問題，exec session `20053` 已 exit 0。包含預設閱讀、展開公式／圖表、按鈕、手機版、CDN失效。
- `supplements-lifecycle.log`：專項生命週期檢查通過，exec session `82935` 已 exit 0。
- `supplements-shots/`：各頁reading、全部展開桌面與手機截圖；供主代理合併全站montage與最終目視確認。

母檔與生成頁已凍結，無進行中的本組程序；未commit或push。
