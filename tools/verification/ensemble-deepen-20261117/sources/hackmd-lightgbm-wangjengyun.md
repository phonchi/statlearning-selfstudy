# LightGBM（HackMD 筆記，WangJengYun）
- URL: https://hackmd.io/@WangJengYun/HyLtemyxI
- 講義頁: p.56
- 抓取狀態: 部分（HTML 內嵌的 Markdown 原文完整取得，約 11.8k 字元；文中所有演算法與示意圖為外部 PNG（GitHub `WangJengYun/ML-DL-notes`），**未讀取圖片**，因此演算法虛擬碼細節未查證。頁面無撰寫日期。）
- 讀取日期: 2026-11-17

本筆記為中文二手整理（非官方），引文為中文原句。

## 重點（以中文撰寫，術語保留原文）
- 定位："LightGBM是在2017年Microsoft所提出基於gradient boosting的輕量級演算法，相對於之前所提到的XGBoost的缺點進行優化"（首段）。
- **GOSS**：依梯度絕對值排序，保留前 $a\%$ 大梯度樣本，對其餘隨機抽 $b\%$，計算資訊增益時對小梯度抽樣樣本乘 $\frac{1-a}{b}$；原文 "GOSS 是一種抽樣的演算法，保留較大梯度值樣本同時對梯度較小的樣本以隨機抽樣的方式來減少計算成本"。建樹用 "Variance Gain"。
- **Histogram-based Algorithm**：
  - 對 XGBoost 的描述："在之前XGBoost主要使用預排序(pre-sorted)的方式來處理分割點"；split gain 計算量 $O(\#data\times\#feature)$。
  - 直方圖法：連續特徵離散化成 bins，"此過程不需要事先排序，因為在分段時，就已經定義數值之間的順序"，split gain 計算量 "減少成 $O(\#bin\times\#feature)$"，並減少記憶體。
  - 每個 bin 記錄 "累加一階梯度值、二階梯度值與樣本各個數" 來算增益，"此過程類似之前XGB的準則"。
  - 作者主張離散化 "會有正規化的效果，有效避免overfiting"（無引用實驗）。
  - "然而這個方法在XGB也可以被選擇"。
- **Tree growth**：
  - "Level-wise tree growth : 大多決策樹都採用這個策略"；"Leaf-wise tree growth : LightGBM採用此策略，每次分割增益最大的葉子節點"。
  - "之前所提到XGB是採用Level-wise生長策略"。
  - Leaf-wise "再分裂數目相同時，Leaf-wise 是可以降低更多的loss"，但 "在資料量小時，會容易overfitting，所以LightGBM增加最大深度的限制"。
- **類別特徵**：LightGBM 以 many-to-many 方式把類別分成兩組；依 $\frac{\sum gradient}{\sum hessian}$ 對直方圖排序後找最佳切點。指出 one-hot 對樹的兩個問題：不平衡切分增益小、預測力被拆散導致重要度被低估。
- **EFB**：把互斥（不同時非零）的稀疏特徵合併成 bundle；Greedy Bundling 視為圖著色（NP-hard）；允許少量衝突，精度影響至多 $O([(1-\gamma)n]^{-2/3})$（γ 為最大衝突率）；合併時以 offset 擴展 bin 範圍（例：feature1 範圍 1–4、feature2 範圍 1–2 → 新特徵 1–6）。掃描成本由 $O(\#data)$ 降為 $O(\#non\_zero\_data)$。

## 可用的算例或圖解想法
- $O(\#data\times\#feature)$ vs $O(\#bin\times\#feature)$ 的對比可做成表；但應補上：建直方圖本身仍需把每筆資料加進 bin，即 $O(\#data\times\#feature)$；省下的是「列舉切點」那一步（推論）。
- EFB 的 1–4、1–2 合併成 1–6 小例可直接畫。
- 類別特徵依 $\sum g/\sum h$ 排序：與 XGBoost 官方 Categorical 頁「sort the gradient histogram」、以及論文 Eq.5 的葉值 $-G/(H+\lambda)$ 同一想法（推論）。

## 與下列問題的關聯（只寫有關的）
- **優先查證 1**：此筆記說 XGBoost 用 pre-sorted、直方圖法「不需要事先排序」。與論文對照：XGBoost exact 的 pre-sorted block 只排序一次（§4.1），筆記沒有說「每節點重排」，但也沒提一次性排序成本。
- **優先查證 4（LightGBM 部分）**：此筆記稱 LightGBM 採 leaf-wise 並加最大深度限制——**二手來源**，需以 LightGBM 官方文件或論文佐證；本筆記**未提 CatBoost**（對稱／oblivious 樹不在本來源）。
- leaf-wise vs level-wise、直方圖以 g/h 統計：有直接中文說明。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **過時**："XGB是採用Level-wise生長策略"——現行 XGBoost 預設 `grow_policy=depthwise`，但 hist/approx 下可設 `lossguide`（每次分 "nodes with highest loss change"；視為 leaf-wise 屬推論），見參數頁。
- **過時**："之前XGB是不支援類別特徵(category feature)的處理"——XGBoost 自 1.5 起支援類別特徵，1.6 起支援 optimal partitioning（官方 Categorical Data 頁）。
- 「XGBoost 主要使用預排序」：只對 exact 成立；現行 XGBoost 預設 `tree_method=auto`＝`hist`，官方 Tree Methods 頁稱 hist 是 "An approximation tree method used in LightGBM"。
- 「直方圖法不需要事先排序」：分箱邊界本身仍需分位數（XGBoost hist 是在訓練前 sketch 一次），只是不需逐節點排序（推論）。
- 「離散化有正規化效果、結果甚至更好」為作者主張，無出處。
- 文中錯字（DBDT、使又、彙編差 等）不影響主旨。
