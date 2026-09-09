# 第 1–5 章詞彙卡逐卡檢查

完整讀取 137 張卡片正反面，保留 114 張，刪除 23 張。每張卡的原始索引、正反面、決策及理由保存在 `cards-core.json`。

| 章別 | 已檢查 | 保留 | 刪除 |
|---|---:|---:|---:|
| ch1 | 26 | 7 | 19 |
| ch2 | 26 | 26 | 0 |
| ch3 | 29 | 29 | 0 |
| ch4 | 31 | 29 | 2 |
| ch5 | 25 | 23 | 2 |

刪除導讀標題、一般提醒、作者與論文介紹，以及無法獨立作為通用術語的標題。未把這些標題改名救回，未新增卡片。正式統計方法的標準人名命名（例如 Bayes、Fisher、Poisson）保留。

另校正 44 張保留卡片中已確認過度絕對或錯誤的定義，包含 ch2 殘留講義頁碼、條件變異、t／F 的模型假設、基準水準、QDA 參數總數、等成本分類門檻值、CV 與自助法的適用條件。逐卡 old/new/reason 保存在 JSON 的 `wording_change`。未新增卡片或更動實驗數值。

交叉核對來源：[scikit-learn 交叉驗證官方文件](https://scikit-learn.org/stable/modules/cross_validation.html)、[LDA／QDA 官方文件](https://scikit-learn.org/stable/modules/lda_qda.html)。其餘公式按條件平均與最小平方法定義核對。原有 Advertising、Default 數值未在此有界子任務中重算，HTML 產生與瀏覽器驗收由主代理整合。

原本已是正式術語的 `Multinomial Logistic Regression` 中文由「多元」校正為「多類別」，避免與 multiple logistic regression 混淆；記錄在 JSON 的 `term_correction`。
