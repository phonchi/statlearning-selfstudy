# DART（XGBoost 官方教學）
- URL: https://xgboost.readthedocs.io/en/stable/tutorials/dart.html
- 講義頁: p.60
- 抓取狀態: OK（"DART — xgboost 3.4.2 documentation"）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- 動機（首段）："XGBoost mostly combines a huge number of regression trees with a small learning rate."；"trees added early are significant and trees added late are unimportant."
- 來源：Rashmi Korlakai Vinayak, Ran Gilad-Bachrach, "DART: Dropouts meet Multiple Additive Regression Trees"（PMLR / arXiv）；"add dropout techniques from the deep neural net community to boosted trees, and reported better results in some situations."
- 現況："Dropout is controlled by parameters like rate_drop. The legacy dart booster name remains available for compatibility."
- Features："Drop trees in order to solve the over-fitting."；"Trivial trees (to correct trivial errors) may be prevented."
- 代價："Training can be slower than gbtree because the random dropout prevents usage of the prediction buffer."；"The early stop might not be stable, due to the randomness."
- **How it works**：第 m 輪丟掉 k 棵樹，$D=\sum_{i\in\mathbf K}F_i$ 為被丟樹的葉分數，新樹 $F_m=\eta\tilde F_m$。目標
  $$\mathrm{Obj}=\sum_{j=1}^nL\big(y_j,\hat y_j^{m-1}-D_j+\tilde F_m\big)+\Omega(\tilde F_m)$$
  原文："$D$ and $F_m$ are overshooting, so using scale factor"
  $$\hat y_j^m=\sum_{i\notin\mathbf K}F_i+a\Big(\sum_{i\in\mathbf K}F_i+bF_m\Big)$$
- `normalize_type`：
  - `tree`（預設）："New trees have the same weight of each of dropped trees."；推導得 $a=\frac{k}{k+\eta}$（$b=1/k$）。
  - `forest`："New trees have the same weight of sum of dropped trees (forest)."；$a=\frac{1}{1+\eta}$（$b=1$）。
  - 參數頁對應說法：tree 時 "Weight of new trees are 1 / (k + learning_rate)"、被丟樹乘 "k / (k + learning_rate)"；forest 時新樹 $1/(1+\eta)$、被丟樹 $1/(1+\eta)$。
- 其他參數：`sample_type`（uniform 預設／weighted "in proportion to weight"）、`rate_drop` [0,1]、`skip_drop` [0,1]（"If a dropout is skipped, new trees are added in the same manner as gbtree."）；"Dropout uses the same tree parameters as gbtree, such as eta, gamma, max_depth"。
- 範例參數：`max_depth=5, learning_rate=0.1, objective='binary:logistic', rate_drop=0.1, skip_drop=0.5, num_round=50`。

## 可用的算例或圖解想法
- 以 k=1、η=0.1、tree normalize 手算：$a=1/1.1$，被丟的那棵樹縮成 0.909 倍，新樹（已乘 η）再乘 $a/k=0.909$，合計約等於原本那一棵（推導步驟頁面以 "$\sim a(1+\eta/k)D=D$" 表示，假設 $\tilde F_m\approx D$）。
- 與神經網路 dropout 類比：隨機拿掉部分已建樹，強迫新樹不要只修補最後幾棵的小錯（"Trivial trees ... may be prevented"）。

## 與下列問題的關聯（只寫有關的）
- boosting 的過擬合控制：DART 是 shrinkage／subsampling 之外的另一種正則化。
- 早停：頁面明說隨機性使 early stop 可能不穩。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 推導中 "$\sim a(1+\eta/k)D$" 隱含 $\tilde F_m\approx D$ 的近似，頁面未明說；教學時應補一句（推論）。
- `booster='dart'` 已成 legacy 名稱；新版建議直接在 gbtree 設 dropout 參數。舊教材若寫「必須設 booster=dart」屬過時寫法（但仍相容）。
- 參數頁與本頁對 tree 正規化的描述角度不同（一個講 $1/(k+\eta)$、一個講 $a=k/(k+\eta)$），代數上一致：$a\cdot\frac1k=\frac{1}{k+\eta}$（推論，已核算）。
