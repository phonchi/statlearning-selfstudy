# CatBoost tutorial: Categorical features parameters（catboost/tutorials GitHub notebook）
- URL: https://github.com/catboost/tutorials/blob/master/categorical_features/categorical_features_parameters.ipynb
- 講義頁: p.59
- 抓取狀態: OK（從 raw.githubusercontent.com 取得 .ipynb JSON，讀取全部 markdown、code cell 與已存的輸出。輸出顯示執行於 2020-05，catboost 0.23）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **常見類別編碼的整理**（cell 0）：One-hot、Label、Hash、Frequency、Target Encoding。
  - Target Encoding 分為 Greedy、Holdout、K-Fold、Leave-One-Out。
  - Greedy 的缺點原文："this method leads to target leakage and overfitting."
  - K-Fold 原文："in each fold we replace the categorical feature values with the target statistics for the category calculated on the other folds."
  - LOO 是 $K=n$ 的特例。
- **K-Fold／LOO 也會過擬合**（cell 0 的例子）：單一類別值，5 個 0 類、6 個 1 類。LOO 後 0 類樣本編碼為 0.6，1 類為 0.5，切在 0.55 即可在訓練集達到 100% 準確率。原文："This will allow a decision tree classifier to choose a split at 0.55 and achieve 100% accuracy on the training set."
- **Ordered Target Encoding**：隨機排列後，只用排在目前物件之前的物件做 target encoding。原文："using only the objects that are placed before the current object"。
- **排列數量**（notebook 的說法）：建立 4 個排列、各訓練一個模型，3 個用於選樹結構，第 4 個計算最終模型的葉值。每輪隨機挑 3 個之一選結構，再為 4 個模型計算葉值。原文："CatBoost creates four permutations of the training objects and for each permutation, a separate model is trained."
- **預設的類別編碼**（cell 63 與輸出 cell 64）：
  - `Borders`：TargetBorderCount=1、CtrBorderCount=15，Prior 取 0/1、0.5/1、1/1 三種。
  - `Counter`：CtrBorderCount=15，Prior=0/1。
  - 所以每個類別特徵預設產生 4 種編碼。輸出原文：`'Borders:CtrBorderCount=15:CtrBorderType=Uniform:TargetBorderCount=1:TargetBorderType=MinEntropy:Prior=0/1:Prior=0.5/1:Prior=1/1'`。
- **新類別與缺失值**（cell 60）：
  - 測試集出現新類別時 countInClass=0，編碼為 $ctr_i=\frac{prior}{totalCount+1}$。
  - 類別缺失值會換成 `"None"` 字串，當成一個新類別。
- **實驗**（二手車價格回歸，3-fold CV，n_estimators=4500，lr=0.1）：
  - 預設：R² 0.9340、RMSE 1652。
  - `one_hot_max_size=2000`（所有類別都 one-hot，最大基數 1118）：R² 0.9392、RMSE 1584（−4.5%）。原文："As can be seen on our dataset it works quite well."
  - `has_time=True`（不排列）：RMSE 1847（+11.3%）。
  - `max_ctr_complexity=0`（不做組合）：RMSE +3.4%；模型大小約為 `max_ctr_complexity=6` 時的 1/6.4。
  - `model_size_reg=1` 的模型約比 `=0` 小 12.7 倍（輸出 12.69）。
  - `ctr_leaf_count_limit=5`：RMSE +60.4%，R² 降到 0.8278。
- **使用建議**：原文 "Generally, it is recommended to use `Borders` for the regression task and `Buckets` for the multiclassification task."；多類別時不建議 `FloatTargetMeanValue`／`BinarizedTargetMeanValue`，因為類別沒有自然順序。

## 可用的算例或圖解想法
- LOO 洩漏的 5/6 例：可以直接用，而且與論文 §3.2 的常數類別例相同（$n^+=6$，$n=11$，$a=0$）。我自行驗算：0 類為 $6/10=0.6$，1 類為 $5/10=0.5$，吻合。
- `has_time=True` 讓 RMSE 上升 11%：這是「排列很重要」的實證小例，但只是單一資料集、3-fold 的結果。
- 「全部 one-hot 反而最好」的結果可以用來提醒學生：ordered TS 不一定在每個資料集都勝出，基數 ≤ 約 1000 時 one-hot 仍可行。（推論）

## 與下列問題的關聯（只寫有關的）
- **類別編碼與 target leakage**：Greedy → Holdout → K-Fold／LOO → Ordered 的演進，以及 LOO 仍會洩漏的反例。
- **stacking vs voting（間接）**：K-Fold target encoding 與 stacking 的 OOF 預測是同一種技巧。（推論）

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **Borders／Buckets 範例的分母少了 +1**：cell 55 的 sun/moon 例子算 $\frac{2+0.5}{3}=0.83$，分母用的是 totalCount（3），但同一 notebook 與官方文件的公式是 $\frac{countInClass+prior}{totalCount+1}$。照公式應為 $2.5/4=0.625$。notebook 也註明這只是示意，且「用全資料」計算，非 ordered，所以只能用來說明 Borders 與 Buckets 的差異，數值不要照抄。
- cell 54 寫 Borders 與 Buckets 都是 "$i\in[0,k-1]$"。依官方文件，Buckets 應為 $i\in[0,k]$，同一 cell 下文也說 Buckets "creates $k+1$ buckets"，所以前句是 typo。
- cell 70/71 印出 "RMSE=2817626"，但程式呼叫 `mean_squared_error` 時沒有加 `squared=False`，印的其實是 MSE，標籤錯誤。
- 「4 個排列、3 個選結構」只是教學文的說法，論文只寫 $s+1$ 個排列。現行預設 `boosting_type=Plain`（CPU），ordered 支援模型的細節可能不同。
- notebook 使用 2020 年的 catboost 0.23；`df.drop([...], 1)` 這種位置參數寫法在新版 pandas 已不可用。部分預設值（如 `ctr_target_border_count`、`max_ctr_complexity=4`）需以現行文件核對。
