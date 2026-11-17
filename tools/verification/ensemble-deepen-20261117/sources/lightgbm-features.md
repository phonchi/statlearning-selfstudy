# LightGBM Features（官方文件 "Features" 頁）
- URL: https://lightgbm.readthedocs.io/en/latest/Features.html
- 講義頁: p.56
- 抓取狀態: OK（curl 直接取得 HTML；頁內示意圖為圖片，未讀取）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **直方圖法取代 pre-sort**：LightGBM 把連續特徵值分桶成離散 bins。原文："LightGBM uses histogram-based algorithms[4, 5, 6], which bucket continuous feature (attribute) values into discrete bins."（§Optimization in Speed and Memory Usage）
- **成本比較**：pre-sort 求 gain 為 $O(\#data)$；建直方圖也是 $O(\#data)$ 但只是累加，建好後找分割只要 $O(\#bins)$。原文："Once the histogram is constructed, a histogram-based algorithm has time complexity O(#bins)"（同節，"Reduced cost of calculating the gain for each split"）
- **直方圖相減（histogram subtraction）**：兄弟葉的直方圖 = 父節點直方圖 − 本葉直方圖，因此每次只需對資料較少的那片葉建直方圖。原文："use the histogram subtraction of its parent and its neighbor"（同節）
- **省記憶體**：bins 少時可用 `uint8_t` 存資料，也不必儲存 pre-sort 的額外資訊。（同節 "Reduce memory usage"）
- **稀疏最佳化**：稀疏特徵建直方圖只需 $O(2\cdot\#non\_zero\_data)$。（同節 "Sparse Optimization"）
- **Leaf-wise（best-first）生長**（優先查證 4）：每次挑「max delta loss」最大的葉來分裂。原文："LightGBM grows trees leaf-wise (best-first)[7]. It will choose the leaf with max delta loss to grow."（§Optimization in Accuracy → Leaf-wise (Best-first) Tree Growth）
- **固定葉數時 leaf-wise loss 較低**：原文："Holding #leaf fixed, leaf-wise algorithms tend to achieve lower loss than level-wise algorithms."（同節）
- **過擬合風險與 max_depth**：資料少時 leaf-wise 可能過擬合，可用 `max_depth` 限制，但就算設了 `max_depth` 仍是 leaf-wise 生長。原文："trees still grow leaf-wise even when max_depth is specified."（同節）
- **頁面把 level-wise 稱為多數演算法的作法**：原文："Most decision tree learning algorithms grow trees by level (depth)-wise"（同節）
- **類別特徵最佳分割**：one-hot 對樹不理想，高基數時樹會不平衡、需要長很深。最佳作法是把 $k$ 個類別分成兩個子集，共有 $2^{k-1}-1$ 種分法；對回歸樹有 $O(k\log k)$ 的有效解（引用 [8] Fisher 1958）。原文："If the feature has k categories, there are 2^(k-1) - 1 possible partitions."；"It needs about O(k * log(k)) to find the optimal partition."（§Optimal Split for Categorical Features）
- **排序鍵是 sum_gradient / sum_hessian**：LightGBM 依每個類別累積的 $\sum g / \sum h$ 排序直方圖，再在排序後的直方圖上找最佳切點。原文："sorts the histogram (for a categorical feature) according to its accumulated values (sum_gradient / sum_hessian)"（同節）
- **GOSS／EFB 不在此頁**：以 grep 搜尋 "goss"、"EFB"、"Exclusive Feature"、"one-side"，命中 0 次。此頁只在參考文獻 [1] 列出 Ke et al. 2017 論文。GOSS 與 EFB 要看參數頁（`data_sample_strategy=goss`、`enable_bundle`）或原論文。
- **分散式學習有三種**：Feature Parallel、Data Parallel、Voting Parallel（§Optimization in Distributed Learning）。
  - Feature parallel：LightGBM 的作法與傳統不同，每個 worker 持有完整資料，因此不必傳送分割結果。原文："instead of partitioning data vertically, every worker holds the full data."
  - Data parallel：先用 "Reduce Scatter" 合併不同特徵的直方圖，再結合直方圖相減。原文："data parallel in LightGBM has time complexity O(0.5 * #feature * #bin)."
  - Voting parallel：用兩階段投票把通訊成本降成常數。原文："Voting parallel further reduces the communication cost in Data Parallel to constant cost."
  - 頁面建議：#data 大時改用 data parallel。原文："it will be better to use data parallel when #data is large."
- **其他**：內建 path-dependent SHAP（`pred_contrib=True`），計算採 QuadratureTreeSHAP（文獻 [13]，2026 年 arXiv）；"Other Features" 列表含 DART、L1/L2、bagging、column sub-sample、early stopping 等。

## 可用的算例或圖解想法
- 直方圖相減：畫父節點 255 個 bin 的 $(\sum g,\sum h)$；左子節點只掃自己的資料建直方圖，右子節點用逐 bin 相減求得。這可以直接回答「直方圖對誰切」：bin 是依特徵值切的，每個 bin 累計的是 $g$ 與 $h$。
- 類別分割：假設某類別特徵有 4 個值，算出每類的 $\sum g/\sum h$（即該類的牛頓葉值的負號形式）並排序，只需比較 3 個切點，不必枚舉 $2^{3}-1=7$ 種分法。（推論：$\sum g/\sum h$ 與 XGBoost 葉值 $-G/(H+\lambda)$ 同形，不含 λ。此對應不在頁面上。）
- Leaf-wise 與 level-wise：固定 4 片葉，畫兩棵樹做對照，一棵平衡、一棵偏斜。

## 與下列問題的關聯（只寫有關的）
- **leaf-wise vs level-wise**：官方明說 LightGBM 是 leaf-wise（best-first），挑 max delta loss 的葉分裂，`max_depth` 只限制深度，不改變生長方式。
- **直方圖對誰切**：bins 依特徵值切；分類特徵的直方圖累計 sum_gradient 與 sum_hessian。
- **精確貪婪 vs 直方圖（優先查證 1）**：此頁只說 pre-sort 求 gain 為 $O(\#data)$，直方圖為 $O(\#bins)$。頁面沒有提到「每個節點都要重新排序」。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 頁首寫 pre-sort-based algorithms 是 "e.g. default algorithm in xgboost"。依兄弟筆記 `xgboost-parameters.md`，現行 XGBoost 的 `tree_method` 預設為 `auto`，而 "auto: Same as the hist tree method."。因此這句對現行 XGBoost 已過時，教學引用時要加註版本。（本筆記未自行抓取 XGBoost 文件，以兄弟筆記為準。）
- "Most decision tree learning algorithms grow trees by level (depth)-wise" 的說法有爭議。StackExchange 的回答（見 `se-leafwise-levelwise.md`）指出 C4.5／CART 傳統上是 depth-first 展開。教學時避免說「多數演算法是 level-wise」。
- 頁面說 $O(k\log k)$ 的有效解是 "for regression trees"，而 LightGBM 實際的排序鍵是 $\sum g/\sum h$。兩者之間的對應頁面沒有說明，Fisher 1958 原文本次也未讀到（見 `fisher-1958-grouping.md`），引用時不要說成「Fisher 證明了 LightGBM 的作法」。
- 參數頁另有 `max_cat_to_onehot`（預設 4）：類別數 ≤ 4 時改用 one-vs-other 分割，此頁沒有提到。
