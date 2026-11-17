# Categorical Data（XGBoost 官方教學）
- URL: https://xgboost.readthedocs.io/en/stable/tutorials/categorical.html
- 講義頁: p.53
- 抓取狀態: OK（"Categorical Data — xgboost 3.4.2 documentation"）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- 起始版本與切分形式（開頭段）："Since version 1.5, XGBoost has support for categorical data."；數值特徵 split 是 $value<threshold$；partition-based 是 $value\in categories$；one-hot 是 $value==category$。
- 使用方式：pandas 欄位轉 `category` dtype，並設 `enable_categorical=True`；程式註解 "Supported tree methods are `approx` and `hist`."；參數頁亦說 "The exact tree method is not supported for categorical features."
- 序列化："Must use JSON/UBJSON for serialization, otherwise the information is lost."
- **Optimal Partitioning**（1.6 加入）：
  - 依據 Fisher (1958)："one only needs to look at sorted partitions instead of enumerating all possible permutations."（Optimal Partitioning 節第一段）。
  - 原文："In the context of decision trees, the discrete values are categories, and the measure is the output leaf value."
  - 原文："During split finding, we first sort the gradient histogram to prepare the contiguous partitions then enumerate the splits according to these sorted values."
  - 歷史：此法 "is used in decision trees [2]"（ESL），"later LightGBM [3] brought it to the context of gradient boosting trees"。
  - `max_cat_to_onehot` 控制每個特徵用 one-hot 還是 partitioning（門檻：類別數少於門檻用 one-hot）。
- **Vector Leaf**（3.4.0 加入）：純量葉時 optimal partitioning "avoids enumerating all $2^{k-1}-1$ binary partitions of $k$ categories."；向量葉則把每個類別的權重投影到父節點 Newton 方向 $u_p=w_p/\lVert w_p\rVert_2$，$s_c=u_p^\top w_c$ 排序，頁面自承 "In general, however, it is an approximation"。
- `feature_types`：`"q"` 數值、`"c"` 類別。
- **Auto-recoding**（3.1 起，僅 Python 介面）：可記住 dataframe 的類別編碼，在推論與續訓時自動 re-code；R 尚不支援，需自行固定 factor levels。
- 未見類別："The best and simplest approach is to re-train the model since a new category represents a new type of data."
- Miscellaneous：預設類別碼為 $[0,n\_categories)$ 的整數；無效值 "During training this is validated but for prediction it’s treated as the same as not-chosen category"。

## 可用的算例或圖解想法
- $k$ 個類別的二分法有 $2^{k-1}-1$ 種；例如 $k=10$ 有 511 種，排序後只需試 $k-1=9$ 個切點——用來說明為何要先依（梯度統計推得的）葉值排序。排序鍵「output leaf value」可連到論文 Eq.5 的 $-G/(H+\lambda)$（推論：頁面只說 "sort the gradient histogram"，未給排序式）。
- R factor 編碼錯位例（a,b,c → 測試集只有 a,c 時編碼變 1,2）可直接當「訓練／測試前處理不一致」的教材。

## 與下列問題的關聯（只寫有關的）
- 直方圖對誰切：類別特徵是先把各類別的梯度直方圖排序，再在排序後找連續切點。
- 缺失值：本頁 Miscellaneous 只說預測時的無效類別碼 "treated as the same as not-chosen category"。它與一般缺失值的 default direction 是否相同，頁面未說明（推論：兩者可能不同，需另查）。
- base learner／one-hot 與樹：本頁給 one-hot 與 partition 兩種切法的官方定義。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 本頁與參數頁皆**未給出 `max_cat_to_onehot` 的預設值**，不要自行補。
- 舊教材（含講義 p.56 的 HackMD 筆記）說「XGB 不支援類別特徵」——自 1.5 起已不成立。
- 範例程式用 `device="cuda"`，在無 GPU 環境需改為 CPU。
