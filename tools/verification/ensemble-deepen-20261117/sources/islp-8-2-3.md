# ISLP (An Introduction to Statistical Learning with Applications in Python), §8.2.3 Boosting 與 §8.2.5 Summary
- URL: 本機 `~/statslearning/ISLP_website.pdf`
- 講義頁: （課本，非講義連結；講義 08 的主教材）
- 抓取狀態: OK（`pdftotext -layout`；書頁 = PDF 頁 − 7，例如書 p.349 = PDF p.356）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- Boosting 與 bagging 一樣是通用方法，本書只在決策樹脈絡下討論（§8.2.3，p.347）。
- 與 bagging 的差別：樹依序生長、每棵用前面樹的資訊；**不使用 bootstrap 抽樣**。原文（p.348）："Boosting does not involve bootstrap sampling; instead each tree is fit on a modified version of the original data set."
- 「慢慢學」的直覺：對目前模型的殘差擬合小樹。原文（p.348）："Given the current model, we fit a decision tree to the residuals from the model." 以及 "In general, statistical learning approaches that learn slowly tend to perform well."
- 分類的 boosting 細節略過：原文（p.348）："Boosting classification trees proceeds in a similar but slightly more complex way, and the details are omitted here."

### 演算法 8.2 Boosting for Regression Trees（p.349）
1. 設 $\hat f(x)=0$，$r_i=y_i$。
2. 對 $b=1,\dots,B$：(a) 以 $(X,r)$ 擬合一棵有 $d$ 次分裂（$d+1$ 個終端節點）的樹 $\hat f^b$；(b) $\hat f(x)\leftarrow\hat f(x)+\lambda\hat f^b(x)$（8.10）；(c) $r_i\leftarrow r_i-\lambda\hat f^b(x_i)$（8.11）。
3. 輸出 $\hat f(x)=\sum_{b=1}^B\lambda\hat f^b(x)$（8.12）。
- 推論：步驟 2(a) 用平方誤差擬合迴歸樹，葉值就是葉內 $r_i$ 的平均，與 ESL 演算法 10.3 在平方損失下（且初值為 0、乘上 shrinkage）相同；ISLP 沒有獨立的「葉值 argmin」步驟，也沒有像 ESL 那樣用最佳常數 $f_0=\bar y$ 初始化。

### 三個調參（p.349）
1. **B（樹數）**：原文："Unlike bagging and random forests, boosting can overfit if B is too large, although this overfitting tends to occur slowly if at all." 用 CV 選 B。
2. **λ（shrinkage）**："a small positive number"，典型 0.01 或 0.001；λ 很小時需要很大的 B。
3. **d（每棵樹分裂次數）**：原文："Often d = 1 works well, in which case each tree is a stump"；d=1 時是加法模型。原文："More generally d is the interaction depth, and controls the interaction order of the boosted model, since d splits can involve at most d variables."

### 圖 8.11（p.350）
- 15 類基因表現資料，任務改為 cancer vs normal；比較 boosting depth=1、depth=2（λ=0.01）與 random forest $m=\sqrt p$。
- 正文（p.349）："simple stumps with an interaction depth of one perform well if enough of them are included." 接著 "This model outperforms the depth-two model, and both outperform a random forest."
- 圖說（p.350）卻說差異不顯著："the standard errors are around 0.02, making none of these differences significant." 單一樹測試誤差 24%。
- 解釋（p.349–350）：因後面的樹考慮了已長出的樹，"smaller trees are typically sufficient"；stump 帶來加法模型，利於解釋。

### §8.2.5 Summary of Tree Ensemble Methods（p.353–354）
- 樹作為 weak learner 的理由：彈性、能處理混合型預測變數（p.353–354）。
- Bagging：樹獨立生長、彼此相似，原文（p.354）："bagging can get caught in local optima and can fail to thoroughly explore the model space."
- Random forests：每次分裂只用隨機特徵子集 → 去相關。
- Boosting：原文（p.354）："each new tree is fit to the signal that is left over from the earlier trees, and shrunken down before it is used."
- BART：只用原始資料、依序生長，但每棵樹被擾動以避免局部極小。

## 可用的算例或圖解想法
- 演算法 8.2 可直接配平方損失的小資料逐步算例：每輪「擬合殘差 → 乘 λ → 更新殘差」（可搭配 sefiks 的例子，見 `sefiks-gbdt-step-by-step.md`，其相當於 λ=1）。
- d=1 → 加法模型、d=2 → 二變數交互的圖示，可接 ESL §10.11 的 ANOVA 展開。

## 與下列問題的關聯
- interaction depth d：p.349 原文定義；與 ESL 的 J 對應為 $d=J-1$（推論）。
- 梯度提升平方損失下葉值等於殘差平均：ISLP 沒有明寫，但演算法 8.2 擬合殘差的迴歸樹即如此（推論）。
- bagging 為何不易因 B 增加而過擬合（對照）：p.347 "random forests will not overfit if we increase B"；boosting 則"can overfit if B is too large"（p.349）。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **符號衝突**：ISLP 的 λ 是 shrinkage／learning rate；XGBoost 官方教學的 λ 是葉權重的 L2 正則化（見 `xgboost-docs-tree-boosting-tutorial.md`）。教學時要明確區分。（參數名 `reg_lambda`／`eta` 為非本批來源、未核對。）
- ISLP 用 B 代表樹數（ESL 用 M）、d 代表分裂數（ESL 用終端節點數 J）。
- 「Boosting does not involve bootstrap sampling」只對演算法 8.2 成立；ESL §10.12.2 的 stochastic gradient boosting 每輪會不放回抽樣子集。
- 圖 8.11 正文說 "outperforms"，圖說說差異不顯著，引用時兩者都要交代。
- 演算法 8.2 只涵蓋迴歸（平方損失）；分類 boosting 的細節 ISLP 自己說略過。
