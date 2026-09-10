# Ch1–6 教材覆蓋審查與補文（2026-09-10）

> 續作更新：本文保留第一輪逐章盤點快照。最終外鏈閱讀狀態與第二輪新增內容，以 `audit-links-ch1-3.md`、`audit-ch4-6-links-final.md` 及主代理合併後台帳為準；以下第一輪未讀數量不是最終狀態。

本組只修改六章母檔、生成HTML與Ch6詞卡。未重跑lab、未commit/push。來源指紋見共用 sources.json。所有新增數值均為公式手算/固定數值核對，不宣稱重新實驗。

## 主題對照

|章|PDF頁|站內section|核對／補完結果|
|---|---|---|---|
|1|9–25|news/slvsml/supervised/recommendation/ideas|既有主線確認；歷史新聞不新增未核實當代主張|
|1|26–29|eda|補截尾平均、兩種絕對離差、分位數慣例及手算|
|1|30–39|datasets/toolchain|既有五組資料與工具鏈確認；31/32/34圖已看|
|2|5–12|irreducible/regfunc|原完整證明保留並改正式預設收合proof|
|2|13–23|curse/parametric/tradeoff|既有球/立方體與彈性讀圖確認；19/23圖已看|
|2|24–30|mse/biasvar|原期望風險與偏差變異證明保留，修正式proof標記|
|2|31–38|bayes|保留Bayes/分類穩健性證明；補KNN迴歸df=n/K條件與證明|
|2|40–41|tradeoff|補model bias/optimization/overfitting/mismatch診斷|
|3|4–6,16–17|slr/mlr|補normal equations/唯一性/殘差正交/RSS曲面完整證明|
|3|7–13,23–24|inference|補係數共變異/常態t推導、CI/PI完整條件與算例|
|3|20–22|mlr|補部分F公式、受限模型/自由度/F=t²完整證明與算例|
|3|25–36|qualitative|既有類別/交互作用/非線性主線保留；35圖已看|
|3|37–58|problems/vsknn|既有六類診斷/KNN比較保留|
|3|61–70|mlr/inference|補FWL完整證明；既有逐步選擇/CCPR/CI/因果限制保留|
|4|7–13,55|logistic/multinomial|補binary/softmax概似、score/Hessian/IRLS、information/SE/識別性及證明|
|4|15–28,56–60|lda|補MLE與pooled分母、Gaussian展開與Fisher完整證明；既有Iris圖表保留|
|4|29–45|qda/threshold/compare|既有QDA/NB/ROC比較保留；修正0.5門檻母體與有限測試差別|
|4|46–55|poisson|補Poisson估計/offset/GLM變異；補Bikeshare係數表與量尺讀法|
|4|61及直接連結|logistic|補機率CI/delta/probit/LR檢定；來源錯例不照抄|
|5|4–18|loocv/kbias|補PRESS證明與刪除後滿秩条件；平均相關誤差變異公式及限制|
|5|19–21|cvwrong|既有分層/群組/時序/重複切分已覆盖；圖像核對|
|5|22–36|bootstrap|補Portfolio最小變異權重推導與限制；63.2%完整期望推導收合|
|5|38–42|bootstrap|既有PI/Jackknife/置換與雙尾方向保留；分類置換圖已看|
|6|6–24|subset/criteria/cv|補Cp完整風險目標/截距常數/搜尋偏差；AIC/BIC量尺條件同步詞卡|
|6|26–39|ridge/lasso|補Ridge/SVD/正交Lasso/座標下降/KKT/MAP完整問題及證明|
|6|40–58,65–69|pcr/pls|補PCA變異/重建/白化證明、PCR秩條件、PLS1訓練和新資料預測算法|
|6|59–64|highdim/reference|既有高維限制保留；補係數平面各路徑讀法|
|6|70|lasso/criteria|補LAR/Lasso路徑區分、Group Lasso完整loss/組別與sparse-group差別；deviance既有|
|recap|1–6|Python附錄/課程入口|已核對PDF文字/直接URL清單；不把外部整書當本章必須重寫的主題|

## 母檔證據

- Ch1: `tools/enrich/enrich_intro.py:395–408`；原有正文逐段修正亦保留於同一母檔。
- Ch2: `tools/enrich/enrich_statlearn.py:1532–1560`；原有正文逐段修正亦保留於同一母檔。
- Ch3: `tools/enrich/enrich_regression.py:1110–1150`；原有正文逐段修正亦保留於同一母檔。
- Ch4: `tools/enrich/enrich_classification.py:1038–1112`；原有正文逐段修正亦保留於同一母檔。
- Ch5: `tools/enrich/enrich_resampling.py:607–630`；原有正文逐段修正亦保留於同一母檔。
- Ch6: `tools/enrich/enrich_modelsel.py:825–897`；原有正文逐段修正亦保留於同一母檔。

## 外鏈與圖像閱讀界線

`ch1-6-links.json` 逐URL記錄PDF頁碼、來源角色、實際閱讀狀態及受阻原因。**未讀原文不等於完成外鏈閱讀**；未讀討論的同題內容即使已由講義/主要教材/獨立推導覆蓋，仍保留未讀標記。資料集、行政、整書入口及背景故事不自動變成新統計單元。

本次PDF清單中URL紀錄（依PDF去重）263筆；狀態統計：`{'教材/行政/課程入口，未全文閱讀': 21, '案例/領域背景來源，未全文閱讀': 27, '資料/影片/背景資源，未全文閱讀': 17, '原文未讀；來源角色及講義主題已盤點': 152, '已核對直接相關段落': 17, '来源受阻，已有同題替代': 4, '參考工具/教材入口，未全文閱讀': 25}`。

`ch1-6-image-review.json` 記錄38個共用低文字圖頁候選，其中27頁已實際看渲染（含1頁導論封面），其餘11頁文字確定為封面／Appendix分隔。圖片在 `ch1-6-images/board-1.png` 至 `board-5.png`。

來源修正：arXiv:1906.02590 v1 的式25把逆矩陣差誤寫成矩陣差的逆；使用獨立高斯展開與官方LDA/QDA文件。來源頁自身有錯不能藉來源徽章變成正確。講義PCA附錄的1/n與以n−1定義的S也須一致；本站統一用每列觀察與n−1样本共變異。

## 驗證

- `ch1-6-checks.py`：20項獨立數值等式，輸出 `ch1-6-numerical.json`／`.log`；六頁validator log按頁保存。
- `ch1-6-browser.log`：完整六頁瀏覽器驗收；第一次僅PRESS所在頁的另一條求和公式裸小於號被HTML解析，已改為LaTeX `\lt`，只重驗受影響頁。
- 圖像與瀏覽器檢查的完成狀態以實際log為準；來源索引、關鍵字、來源徽章本身均不構成內容完整性證明。
