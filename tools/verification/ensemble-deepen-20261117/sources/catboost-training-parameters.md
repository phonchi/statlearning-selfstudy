# Common training parameters（CatBoost 官方參數頁）— 補充來源
- URL: https://catboost.ai/en/docs/references/training-parameters/common
- 講義頁: 無（講義未連結，為查證優先項目 4 而自行補抓）
- 抓取狀態: OK（curl 取得 HTML 並轉純文字；`boosting_type` 的預設表另以原始 HTML 核對巢狀結構）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **`grow_policy` 預設 `SymmetricTree`**（優先查證 4）：
  - SymmetricTree：逐層生長到指定深度，產生的結構永遠對稱。原文："all leaves from the last tree level are split with the same condition."
  - **Depthwise**：逐層生長，每片葉各自選最佳分割。原文："Each leaf is split by condition with the best loss improvement."
  - **Lossguide**：逐葉生長，直到達到最大葉數。原文："non-terminal leaf with the best loss improvement is split."
  - 後兩者的限制：不能用 PredictionDiff 特徵重要度，且只能匯出 json/cbm。
- **`depth`**（alias `max_depth`）：預設 6；`grow_policy=Lossguide` 時預設 16。CPU 上最多 16。
- **`max_leaves`**（alias `num_leaves`）：預設 31，只在 Lossguide 時可用。原文："It is not recommended to use values greater than 64"。
- **`min_data_in_leaf`**（alias `min_child_samples`）：預設 1，只在 Lossguide 與 Depthwise 時可用（對稱樹不適用）。
- **`l2_leaf_reg`**（alias `reg_lambda`）：預設 3.0。原文："Coefficient at the L2 regularization term of the cost function."
- **`iterations`**：預設 1000。**`learning_rate`**：對 Logloss、MultiClass、RMSE 會依迭代數自動決定，其他情況預設 0.03。
- **`boosting_type`**：
  - CPU 預設 **Plain**。
  - GPU：MultiClass 或 MultiClassOneVsAll 時為 Plain；超過 50K 筆時為 Plain；≤ 50K 筆且非多類別時為 **Ordered**。
  - Ordered 的說明原文："Usually provides better quality on small datasets, but it may be slower than the Plain scheme."
- **`bootstrap_type` 預設依情況而定**：
  - 目標為 QueryCrossEntropy、YetiRankPairwise、PairLogitPairwise 且未設 bagging_temperature 時：Bernoulli（subsample 0.5）。
  - 非 MultiClass／MultiClassOneVsAll、`task_type=CPU`、`sampling_unit=Object` 時：**MVS（subsample 0.8）**。
  - 其他情況：Bayesian。
- **`subsample`**：少於 100 筆時預設 1；否則 Poisson 與 Bernoulli 為 0.66，MVS 為 0.8。
- **`sampling_frequency`**：預設 `PerTreeLevel`。
- **`one_hot_max_size`**：一般情況預設 2；Ranking 為 10；GPU 且所選 ctr 需要訓練時拿不到的 target 時為 255；CPU 的 Pairwise scoring 下不適用（N/A）。
- **`has_time`**：預設 False。設為 True 時不做隨機排列，直接使用資料原本的順序。
- **`rsm`**（alias `colsample_bylevel`）：原文 "Random subspace method."，預設 1。

## 可用的算例或圖解想法
- 三套件的生長策略與預設對照表：
  - XGBoost `grow_policy=depthwise`（兄弟筆記）
  - LightGBM leaf-wise，`num_leaves=31`
  - CatBoost `SymmetricTree`，`depth=6`
  - 補充：CatBoost 也可以設成 `Lossguide`（`max_leaves=31`）或 `Depthwise`。
- 深度 6 的對稱樹有 $2^6=64$ 片葉，但只有 6 個不同的分裂條件。相比之下，LightGBM 的 31 葉樹有 30 個分裂條件。（推論：這可以說明對稱樹的「結構正則化」。）

## 與下列問題的關聯（只寫有關的）
- **CatBoost 對稱樹（優先查證 4）**：官方預設是 SymmetricTree，與論文 §5 的 oblivious trees 一致，但它不是唯一選項。
- **min_child_weight**：CatBoost 的 `min_data_in_leaf` 是樣本數下限，不是 Hessian 和，且只在非對稱的生長策略下才有作用。
- **λ 的直覺**：`l2_leaf_reg` 預設 3.0，三套件的預設各不相同（LightGBM 0，XGBoost 1，見其他筆記）。
- **random subspace vs RF**：CatBoost 把 `rsm` 直接稱為 "Random subspace method"，每次選分割時重新抽特徵的比例。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 與論文設定的差異：論文實驗用 Ordered 模式與 Bayesian bootstrap，現行 CPU 預設卻是 Plain 與 MVS。「CatBoost 預設用 ordered boosting」在 CPU 上不正確，但 ordered TS（類別編碼）不受 `boosting_type` 影響。（後半句是推論：論文 §5 說 Plain 模式是 "standard GBDT algorithm with inbuilt ordered TS"。）
- 這是線上 `en/docs` 的現行文件，沒有標示版本號，預設值未來可能改變。
