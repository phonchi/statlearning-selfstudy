# Boosting（Danny Friedman, *Machine Learning from Scratch*, Ch. 6 Concept）
- URL: https://dafriedman97.github.io/mlbook/content/c6/s1/boosting.html
- 講義頁: p.44–45
- 抓取狀態: OK（WebFetch 讀取；AdaBoost 的 α、權重更新、標籤編碼、AdaBoost.R2 迴圈條件、加權中位數等關鍵句另以 curl 取原始 HTML（HTTP 200）逐字核對）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
章節：Boosting → AdaBoost for Binary Classification（Weighted Classification Trees／The Discrete AdaBoost Algorithm）→ AdaBoost For Regression。

- Boosting 的定位：依序訓練 weak learners。原文："trains these weak learners *sequentially*, each one learning from the mistakes of the last."

### 加權分類樹
- 節點內類別比例改為加權：$\hat p_{mk}=\dfrac{\sum_{n\in\mathcal N_m}w_nI(y_n=k)}{\sum_{n\in\mathcal N_m}w_n}$；Gini $\sum_k\hat p_{mk}(1-\hat p_{mk})$、cross-entropy $-\sum_k\hat p_{mk}\log\hat p_{mk}$ 照常計算。
- 原文："This forces the tree to prioritize isolating the classes that were poorly classified by previous learners."

### Discrete AdaBoost（逐字核對過）
- 標籤：原文 "Define the target variable to be $y_n\in\{-1,+1\}$"。
- 初始化 $w_n^1=1/N$。
- 每輪 t：以權重 $\mathbf w^t$ 建 weak learner；$I_n^t=1$ 若誤分；
  加權誤差 $\epsilon^t=\dfrac{\sum_n w_n^tI_n^t}{\sum_n w_n^t}$；
  accuracy measure $\alpha^t=\log\!\big(\tfrac{1-\epsilon^t}{\epsilon^t}\big)$（**無 ½**，與 ESL 演算法 10.1 相同）；
  權重更新 $w_n^{t+1}=w_n^t\exp(\alpha^tI_n^t)$（**無正規化步驟**）。
- 最終 $\hat y_n=\mathrm{sign}\big(\sum_t\alpha^tf^t(\mathbf x_n)\big)$。原文："a weighted vote of all the individual fitted values where higher-performing learners are given more weight."
- 原文（權重直覺）："the weight for a correctly-classified observation does not change while the weight for a misclassified observation increases"。
- 頁面**沒有**解釋 α 為何取此形式，也沒有提到 exponential loss 或 forward stagewise additive modeling（原始 HTML grep `exponential|stagewise` 0 筆；"normaliz" 3 筆全在 AdaBoost.R2 的 $Z^t$ 與加權中位數段落）。

### AdaBoost.R2（迴歸）
- 不把權重放進損失，而是依 $w_n^t$ 機率**有放回重抽** N 筆再擬合，在原樣本上評估。
- 迴圈原文："For $t=1,2,\dots,T$ or while $\bar L^t$, as defined below, is less than or equal to 0.5"。
- 損失（只給 linear loss）：$D^t=\max_n|y_n-f^t(\mathbf x_n)|$，$L_n^t=|y_n-f^t(\mathbf x_n)|/D^t$；模型誤差 $\bar L^t=\sum_nL_n^tw_n^t$；若 $\bar L^t\ge0.5$ 停止並令 $T=t-1$。
- $\beta^t=\bar L^t/(1-\bar L^t)$，原文："The lower $\beta^t$, the greater our confidence in the model."
- $Z^t=\sum_nw_n^t(\beta^t)^{1-L_n^t}$，$w_n^{t+1}=w_n^t(\beta^t)^{1-L_n^t}/Z^t$；原文："which increases the weight for observations with a greater error $L^t_n$"。
- 最終預測：各 $f^t(\mathbf x_n)$ 以 $\log(1/\beta^t)$ 為權重的 **weighted median**。定義：權重正規化、依值排序，取累積權重首次 ≥0.5 的值；例：$\mathbf v=\{10,30,20,40\}$、$\mathbf s=\{0.4,0.6,0.2,0.8\}$ → 中位數 30。
- 原文："iteratively fit a weak learner, see where the learner struggles, and emphasize the observations where it failed."

## 可用的算例或圖解想法
- 推論（我自己核對加權中位數例）：正規化後排序為 v=(10,20,30,40)、s=(0.2,0.1,0.3,0.4)，累積 0.2, 0.3, 0.6 → 第三個 30，正確。
- 可做「AdaBoost 一輪」小表：5–10 筆、一個 stump，算 ε、α、更新後權重；再對照 ESL 10.12 的 β=α/2。

## 與下列問題的關聯
- AdaBoost 的 α 與權重更新：本頁給出與 ESL 演算法 10.1 相同的形式（α=log((1−ε)/ε)、無正規化），但不提推導；推導需改引 ESL §10.4。
- base learner 選擇：Discrete AdaBoost 用決策樹（"decision trees in our case"）；AdaBoost.R2 註明"many other weak learners may be used"（WebFetch 回報）。頁面未要求 stump 或限制深度。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- α 用 log 而非 ½log，與 ESL 10.12 的 β 差 2 倍；兩者只差尺度，sign 分類結果相同（見 `esl-ch10-boosting.md`）。教學引用時須說明。
- AdaBoost.R2 迴圈寫「while $\bar L^t\le0.5$」、停止條件寫「$\bar L^t\ge0.5$」：方向一致（WebFetch 摘要稱「看似顛倒」是誤讀），只有恰好 =0.5 的邊界重疊，影響可忽略。
- AdaBoost.R2 的來源論文本頁未引用（推論，非本批來源、未核對：通常歸於 Drucker 1997）；且只給 linear loss，未提 square／exponential 版本。
- Discrete AdaBoost 的演算法步驟中未見 ε=0 或 ε≥0.5 的處理（推論：此時 α 無定義或 ≤0）。
