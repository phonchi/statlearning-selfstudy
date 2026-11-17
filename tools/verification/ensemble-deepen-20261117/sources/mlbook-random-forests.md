# Random Forests — Machine Learning from Scratch（Danny Friedman, §6.1 Tree Ensemble Methods）
- URL: https://dafriedman97.github.io/mlbook/content/c6/s1/random_forests.html
- 講義頁: p.38–39
- 抓取狀態: OK（curl 取得靜態 HTML，HTTP 200；無程式碼、無數值例）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- 定位："A random forest is a slight extension to the bagging approach for decision trees"，可進一步降低 overfitting（首段）。並說 "Unlike bagging, random forests are exclusively designed for decision trees"。
- 與 bagging 唯一差異：每棵樹仍用 bootstrap 樣本，但 "at each split within each tree, we only consider splitting a randomly-chosen subset of the predictors"（第二段）。
- 為何要限制特徵：若 base learners 太相似，平均就沒有收穫；"Randomly choosing eligible predictors at each split de-correlates the trees"（第三段）。
- 程序（"Random Forest Procedure"）：predictors 為 $D$ 維；對 $b=1..B$ 抽 $\mathcal D^*_b$、建樹 $T^*_b$，每個 split 只考慮 $D$ 個 predictor 中的 $C$ 個（$C\le D$）；預測時合併 $\hat y^*_{tb}$。
- "If \(C = D\), there is no difference between these two approaches."（程序後一段）——$C=D$ 即 bagging。
- 總結：兩個隨機來源——bootstrap 抽觀測、每個 split 抽 predictor（末段）。

## 可用的算例或圖解想法
- 頁面本身無算例。可沿用其符號 $C$ of $D$ 與 ESL／ISLP 的 $m$ of $p$ 對照（講義宜統一用 $m,p$）。

## 與下列問題的關聯（只寫有關的）
- random subspace vs random forest：此頁明確寫「每個 split」抽 predictor（對照 Ho 的每棵樹抽一次，見 `louppe-geurts-2012-random-patches.md` §2.3）。
- 為何 RF 取 $m\approx\sqrt p$：**此頁沒有給任何建議值或理由**；需引 ESL §15.2–15.3（$\sqrt p$ 或 $\lfloor\sqrt p\rfloor$，迴歸 $\lfloor p/3\rfloor$）與 ISLP §8.2.2。
- base learner：此頁說 RF 只為決策樹設計。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- "further decrease overfitting" 的說法較籠統：依 ESL (15.1)／§15.4，RF 的改善來自降低樹間相關 $\rho$ 以降變異，同時偏差通常略升（ESL p.601）；此頁沒提偏差代價。
- 「de-correlates the trees」只有直覺說明，沒有變異公式；教學時要接 ESL (15.1)。
- 頁面版權標 2020，內容沒有涉及 OOB、變數重要度或實作參數。
