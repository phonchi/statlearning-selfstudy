# XGBoost: A Scalable Tree Boosting System (Chen & Guestrin, KDD 2016)
- URL: https://arxiv.org/pdf/1603.02754.pdf （arXiv:1603.02754v3, 10 Jun 2016，共 13 頁）
- 講義頁: p.52
- 抓取狀態: OK（PDF 下載成功，以 `pdftotext` 抽文字；第 4 頁另行渲染成圖核對 §3.3 公式）
- 讀取日期: 2026-11-17

頁碼以 arXiv PDF 頁碼計：§2.1–2.2 在 p.2；Alg.1、Alg.2、§2.3、§3.1、§3.2 起頭在 p.3；§3.3、§3.4 在 p.4；Alg.3、§4.1 在 p.5；Time Complexity Analysis 與 §4.2 在 p.6；§4.3 在 p.7；附錄 A（weighted quantile sketch）在 p.11–13。

> 節號提醒：委派說明寫「§2.2 正則化目標」，但論文中 **§2.1 = Regularized Learning Objective（Eq.1–2）**，**§2.2 = Gradient Tree Boosting（Eq.3–7，含 Eq.5/6/7）**。以下依論文實際節號。

## 重點（以中文撰寫，術語保留原文）

### §2.1 正則化目標（p.2）
- 模型是 K 棵回歸樹相加：$\hat y_i=\phi(x_i)=\sum_{k=1}^K f_k(x_i),\ f_k\in\mathcal F$，其中 $\mathcal F=\{f(x)=w_{q(x)}\}$，$q:\mathbb R^m\to T$ 把樣本映到葉索引，$w\in\mathbb R^T$ 是葉分數。（Eq.1）
  - 原文："Unlike decision trees, each regression tree contains a continuous score on each of the leaf"（§2.1）
- 正則化目標：$\mathcal L(\phi)=\sum_i l(\hat y_i,y_i)+\sum_k\Omega(f_k)$，$\Omega(f)=\gamma T+\tfrac12\lambda\lVert w\rVert^2$。（Eq.2）
  - 原文："The additional regularization term helps to smooth the final learnt weights to avoid over-fitting."（§2.1）
  - 原文："When the regularization parameter is set to zero, the objective falls back to the traditional gradient tree boosting."（§2.1）
  - 論文要求 $l$ 為 "a differentiable convex loss function"（§2.1）。

### §2.2 Gradient Tree Boosting（p.2–3）
- 加法訓練：第 t 輪最小化 $\mathcal L^{(t)}=\sum_i l\big(y_i,\hat y_i^{(t-1)}+f_t(x_i)\big)+\Omega(f_t)$；"we greedily add the $f_t$ that most improves our model"（§2.2）。
- 二階近似，$g_i=\partial_{\hat y^{(t-1)}}l(y_i,\hat y^{(t-1)})$、$h_i=\partial^2_{\hat y^{(t-1)}}l(y_i,\hat y^{(t-1)})$；去掉常數得
  $$\tilde{\mathcal L}^{(t)}=\sum_{i=1}^n\Big[g_if_t(x_i)+\tfrac12h_if_t^2(x_i)\Big]+\Omega(f_t)\quad\text{(Eq.3)}$$
  原文："first and second order gradient statistics on the loss function"（§2.2）；二階法來源標為 Friedman et al. [12]。
- 令 $I_j=\{i\mid q(x_i)=j\}$，展開 Ω：
  $$\tilde{\mathcal L}^{(t)}=\sum_{j=1}^T\Big[\big(\textstyle\sum_{i\in I_j}g_i\big)w_j+\tfrac12\big(\sum_{i\in I_j}h_i+\lambda\big)w_j^2\Big]+\gamma T\quad\text{(Eq.4)}$$
- **固定樹結構下的最佳葉權重**（Eq.5）：
  $$w_j^*=-\frac{\sum_{i\in I_j}g_i}{\sum_{i\in I_j}h_i+\lambda}$$
- **結構分數**（Eq.6）：
  $$\tilde{\mathcal L}^{(t)}(q)=-\frac12\sum_{j=1}^T\frac{(\sum_{i\in I_j}g_i)^2}{\sum_{i\in I_j}h_i+\lambda}+\gamma T$$
  原文："This score is like the impurity score for evaluating decision trees, except that it is derived for a wider range of objective functions."（§2.2）
- **分裂增益**（Eq.7），$I=I_L\cup I_R$：
  $$\mathcal L_{split}=\frac12\left[\frac{(\sum_{I_L}g_i)^2}{\sum_{I_L}h_i+\lambda}+\frac{(\sum_{I_R}g_i)^2}{\sum_{I_R}h_i+\lambda}-\frac{(\sum_{I}g_i)^2}{\sum_{I}h_i+\lambda}\right]-\gamma$$
  原文："A greedy algorithm that starts from a single leaf and iteratively adds branches to the tree is used instead."（§2.2）

### §2.3 Shrinkage 與 column subsampling（p.3）
- Shrinkage：原文 "Shrinkage scales newly added weights by a factor η after each step of tree boosting."；"shrinkage reduces the influence of each individual tree and leaves space for future trees to improve the model."（§2.3）
- Column subsampling 借自 RandomForest；原文："using column sub-sampling prevents over-fitting even more so than the traditional row sub-sampling"（§2.3，論文自述依據是 "According to user feedback"，非實驗）。另說它 "also speeds up computations of the parallel algorithm"。

### §3.1 Exact greedy（Algorithm 1，p.3）
- 原文："a split finding algorithm enumerates over all the possible splits on all the features. We call this the exact greedy algorithm."（§3.1）
- 原文："the algorithm must first sort the data according to feature values and visit the data in sorted order to accumulate the gradient statistics"（§3.1）
- Alg.1 輸入是「current node 的 instance set $I$」，對每個特徵 k 執行 `for j in sorted(I, by x_jk)`，累加 $G_L,H_L$，$G_R=G-G_L$、$H_R=H-H_L$，score $=\frac{G_L^2}{H_L+\lambda}+\frac{G_R^2}{H_R+\lambda}-\frac{G^2}{H+\lambda}$ 取最大。即**演算法寫法本身是對每個節點的樣本集排序**；預排序的最佳化放在 §4.1。

### §3.2 Approximate（Algorithm 2，p.3–4）
- 原文："the algorithm first proposes candidate splitting points according to percentiles of feature distribution"；之後 "maps the continuous features into buckets split by these candidate points, aggregates the statistics"（§3.2）。
- Alg.2：$G_{kv}=\sum_{j:\,s_{k,v}\ge x_{jk}>s_{k,v-1}}g_j$，$H_{kv}$ 同理；只在提議切點中找最大 score。
- **Global vs local**：原文 "The global variant proposes all the candidate splits during the initial phase of tree construction"；"The local variant re-proposes after each split."（§3.2）
  - "usually more candidate points are needed for the global proposal because candidates are not refined after each split."
  - "The global proposal can be as accurate as the local one given enough candidates."
- Fig.3（Higgs 10M，test AUC）：exact greedy、local eps=0.3、global eps=0.05 三條幾乎重疊，global eps=0.3 明顯較低。圖說："This roughly translates to 1 / eps buckets in the proposal."
- 原文："it is also possible to directly construct approximate histograms of gradient statistics [22]"（§3.2）——論文當時把直方圖法列為其他系統的作法之一。

### §3.3 Weighted Quantile Sketch（p.4；附錄 A p.11–13）
- 定義 $\mathcal D_k=\{(x_{1k},h_1),\dots,(x_{nk},h_n)\}$，以 $h$ 加權的 rank 函數（Eq.8）：
  $$r_k(z)=\frac{1}{\sum_{(x,h)\in\mathcal D_k}h}\sum_{(x,h)\in\mathcal D_k,\ x<z}h$$
- 目標切點（Eq.9）：$|r_k(s_{k,j})-r_k(s_{k,j+1})|<\epsilon$，$s_{k1}=\min_i x_{ik}$，$s_{kl}=\max_i x_{ik}$；"there is roughly $1/\epsilon$ candidate points."
- **為什麼以 $h_i$ 為權重**，原文："Here each data point is weighted by $h_i$. To see why $h_i$ represents the weight, we can rewrite Eq (3) as"
  $$\sum_{i=1}^n\tfrac12h_i\big(f_t(x_i)-g_i/h_i\big)^2+\Omega(f_t)+\text{constant}$$
  原文："which is exactly weighted squared loss with labels $g_i/h_i$ and weights $h_i$."（§3.3，p.4，已對照渲染頁面確認印刷內容）
  - **注意符號（推論，已自行展開核對）**：$\tfrac12h(f+g/h)^2=\tfrac12hf^2+gf+g^2/(2h)$ 才與 Eq.3 的 $+g_if_t$ 一致；論文印的 $(f-g/h)^2$ 會得到 $-g f$。所以正確標籤應是 $-g_i/h_i$（與 Eq.5 的負號一致），權重 $h_i$ 的結論不受影響。
- 原文："When every instance has equal weights, an existing algorithm called quantile sketch [14, 24] solves the problem."；"there is no existing quantile sketch for the weighted datasets."（§3.3）
- 論文提出的 sketch 支援 merge 與 prune："with each operation proven to maintain a certain accuracy level"（§3.3）。附錄 A：merge 兩個 $\epsilon_1,\epsilon_2$-approximate summary 得 $\max(\epsilon_1,\epsilon_2)$（Theorem A.1）；prune 把元素數降到 $b+1$，誤差由 $\epsilon$ 變為 $\epsilon+1/b$（附錄 A 前言）。附錄以 GK algorithm [14] 為基礎。

### §3.4 Sparsity-aware split finding（Algorithm 3，p.4–5）
- 稀疏來源三種："1) presence of missing values in the data; 2) frequent zero entries in the statistics; and, 3) artifacts of feature engineering such as one-hot encoding."（§3.4）
- 原文："we propose to add a default direction in each tree node"；"When a value is missing in the sparse matrix x, the instance is classified into the default direction."（§3.4）
- 原文："The optimal default directions are learnt from the data."；"The key improvement is to only visit the non-missing entries $I_k$."（§3.4）
- **Alg.3 的具體做法**：$G=\sum_{i\in I}g_i$、$H=\sum_{i\in I}h_i$ 用**全部**樣本（含缺失）；對每個特徵只掃 $I_k=\{i\in I\mid x_{ik}\ne\text{missing}\}$，做兩趟：
  1. 依 $x_{jk}$ 遞增累加到 $G_L,H_L$，$G_R=G-G_L$ ⇒ 缺失值全落在**右**（註解 "enumerate missing value goto right"）；
  2. 依 $x_{jk}$ 遞減累加到 $G_R,H_R$，$G_L=G-G_R$ ⇒ 缺失值全落在**左**（"enumerate missing value goto left"）；
  取兩趟所有候選中 gain 最大者，輸出 "Split and default directions with max gain"。
- 也適用 approximate："only collect statistics of non-missing entries into buckets"（Alg.3 註）。
- 複雜度與 Fig.5：原文 "our method exploits the sparsity to make computation complexity linear to number of non-missing entries in the input."；Allstate-10K 上 "the sparsity aware algorithm runs 50 times faster than the naive version."（§3.4）
- Fig.4 示意：Age 缺失的 X1、Gender 缺失的 X2 都走 default 箭頭。

### §4.1 Column Block（p.5–6）
- 原文："The most time consuming part of tree learning is to get the data into sorted order."（§4.1）
- 原文："Data in each block is stored in the compressed column (CSC) format, with each column sorted by the corresponding feature value."（§4.1）
- 原文："This input data layout only needs to be computed once before training, and can be reused in later iterations."（§4.1）
- 原文："We do the split finding of all leaves collectively"；"one scan over the block will collect the statistics of the split candidates in all leaf branches."（§4.1，exact greedy 時整份資料放單一 block）
- Approximate 時：多個 block，每個是部分列；"the quantile finding step becomes a linear scan over the sorted columns"；"especially valuable for local proposal algorithms"；"The binary search in histogram aggregation also becomes a linear time merge style algorithm."
- 並行與 column subsampling："Collecting statistics for each column can be parallelized"；"the column block structure also supports column subsampling"。
- **Time Complexity Analysis（p.6）**，$d$=最大深度、$K$=樹數、$\lVert x\rVert_0$=非缺失元素數、$q$=候選數、$B$=每 block 最大列數：
  | 情境 | 原始做法 | 用 block |
  |---|---|---|
  | exact greedy | $O(Kd\lVert x\rVert_0\log n)$ | $O(Kd\lVert x\rVert_0+\lVert x\rVert_0\log n)$ |
  | approximate | $O(Kd\lVert x\rVert_0\log q)$（binary search） | $O(Kd\lVert x\rVert_0+\lVert x\rVert_0\log B)$ |
  - 原文："Here $O(\lVert x\rVert_0\log n)$ is the one time preprocessing cost that can be amortized."；"the block structure helps to save an additional log n factor"；"While q is usually between 32 and 100, the log factor still introduces overhead."

### §4.2 Cache-aware access（p.6–7）
- 原文："the new algorithm requires indirect fetches of gradient statistics by row index, since these values are accessed in order of feature."；"This is a non-continuous memory access."（§4.2）
- 原文："This slows down split finding when the gradient statistics do not fit into CPU cache and cache miss occur."
- Exact greedy 的解法：每個 thread 配 internal buffer，先 prefetch 梯度統計再 "perform accumulation in a mini-batch manner"；"cache-aware implementation of the exact greedy algorithm runs twice as fast as the naive version when the dataset is large."（Fig.7，10M 筆時效果明顯）
- Approximate 的解法是選 block size：太小 → "inefficient parallelization"；太大 → "cache misses, as the gradient statistics do not fit into the CPU cache"；實驗結論 "choosing $2^{16}$ examples per block balances the cache property and parallelization."（Fig.9）

### §4.3 Out-of-core：block compression 與 sharding（p.7）
- 用獨立 thread 預取 block 到記憶體緩衝，但 "the disk reading takes most of the computation time"。
- **Block Compression**：按欄壓縮、載入時由獨立 thread 解壓；row index 減去 block 起始 index 後用 16-bit 整數存 offset，"This requires $2^{16}$ examples per block"；"we achieve roughly a 26% to 29% compression ratio."
- **Block Sharding**：把資料交錯分到多顆磁碟，每顆磁碟一個 pre-fetcher thread，"This helps to increase the throughput of disk reading when multiple disks are available."

### 其他
- Table 1（p.7）：XGBoost 同時支援 exact greedy、approximate global、approximate local、out-of-core、sparsity aware、parallel；scikit-learn 與 R GBM 只有 exact greedy（R GBM sparsity "partially"）。
- §1：2015 年 Kaggle blog 上 29 個冠軍解中 17 個用 XGBoost（p.1）。

## 可用的算例或圖解想法
- **Eq.5 代入 logistic loss（推論，非論文內容）**：$l=-[y\log p+(1-y)\log(1-p)]$、$p=\sigma(\hat y)$ ⇒ $g_i=p_i-y_i$、$h_i=p_i(1-p_i)$，故 $w_j^*=\frac{\sum(y_i-p_i)}{\sum p_i(1-p_i)+\lambda}$，正是 StatQuest 的 Output value；$p_i$ 為上一輪預測機率（第一輪即 $p_0$），葉值加在 log-odds 尺度上（再乘 η）。
- **平方損失（推論）**：$l=\tfrac12(y-\hat y)^2$ ⇒ $g=\hat y-y$、$h=1$ ⇒ $w_j^*=\frac{\sum_{I_j}(y_i-\hat y_i)}{|I_j|+\lambda}$，λ=0 時就是葉內殘差平均；λ>0 把平均往 0 縮。此時所有 $h_i=1$，加權 sketch 退化為一般分位數。
- **λ 的直覺**：Eq.5 分母 $H+\lambda$，樣本少（H 小）的葉被縮得多；Eq.7 中 λ 也降低小葉子的 gain。γ 是 Eq.7 末項，直接當分裂門檻（推論，由式子讀出）。
- **Alg.3 手算**：取 5 筆、其中 2 筆缺失，列出遞增掃描（缺失→右）與遞減掃描（缺失→左）兩張表，比較最大 gain，示範 default direction 怎麼被選出。
- **複雜度對照圖**：「naive：每層對每個節點重排 → $\log n$ 乘在 $Kd$ 上」vs「block：排序一次 $\lVert x\rVert_0\log n$，之後每層一次線性掃描，所有葉一起收集統計」。
- **Fig.3** 可直接用來說明 global/local proposal 與 ε（候選數 ≈ 1/ε）的取捨。

## 與下列問題的關聯（只寫有關的）
- **優先查證 1（精確貪婪成本／是否每節點重排）**：Alg.1 的寫法是 `sorted(I, by x_jk)`，I 為當前節點樣本——若照字面實作，確實每節點（等價於每層）都要排序，成本 $O(Kd\lVert x\rVert_0\log n)$。但 XGBoost 的實作用 §4.1 的 pre-sorted column block，"only needs to be computed once before training"，成本降為 $O(Kd\lVert x\rVert_0+\lVert x\rVert_0\log n)$，且一次掃描同時處理同層所有葉。結論：「exact greedy 每個節點都要重新排序」只對 naive 實作成立，對論文的 XGBoost 不成立；但每層仍須線性掃過所有非缺失元素，這是它比直方圖法慢的原因（直方圖法掃的是 bins，不是 rows；這個比較論文沒有直接寫，屬推論，見 hackmd 筆記與 tree-methods 筆記）。
- **優先查證 2（weighted quantile sketch 的權重）**：權重是 $h_i$；理由是 Eq.3 可改寫為以 $h_i$ 加權、標籤 $g_i/h_i$（實應為 $-g_i/h_i$）的平方損失。要讓每個 bucket 對目標的「份量」相近，就要按 $h$ 的累積比例切。注意：現行 `hist`（預設）不用 Hessian 加權，見 xgboost-tree-methods 筆記。
- **優先查證 5（缺失值預設方向）**：見 §3.4 / Alg.3：兩趟掃描，比較「缺失全右」與「缺失全左」的 gain，選大的；每個節點各自學。
- gradient 與殘差、分類 h=p(1−p)、葉輸出與 p、p₀、log-odds：Eq.3、Eq.5 為依據，代入部分見上方推論。
- 直方圖對誰切：Alg.2 是對**特徵值**切 bucket，bucket 內累加的是 $g$、$h$ 統計。
- `min_child_weight`：論文無此參數名；Eq.5 分母的 $\sum h_i$ 就是官方所說 "sum of instance weight (hessian)"（連結屬推論）。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **§3.3 改寫式符號錯誤（推論，已代數核對）**：印刷的 $\tfrac12h_i(f_t(x_i)-g_i/h_i)^2$ 與 Eq.3 不符，應為 $(f_t(x_i)+g_i/h_i)^2$，即標籤 $-g_i/h_i$。教學時宜指出，否則與 Eq.5 的負號衝突。
- **Algorithm 1/3 的印刷瑕疵**：初始化寫 `gain ← 0` 卻更新 `score`；輸入寫 `d, feature dimension` 但迴圈用 `m`；score 式省略了 Eq.7 的 ½ 與 −γ（對 argmax 無影響，但與 Eq.7 數值不同）。
- **論文與現行實作的術語差異**：論文的 approximate 有 global / local 兩種；現行官方文件中 `approx` 是「每棵樹之前」重做 sketch（相當於 global），per-node 的 local 版本（`grow_local_histmaker`）已移除；現行預設 `hist` 只在訓練前 sketch 一次且不以 Hessian 加權。見 xgboost-tree-methods 筆記。
- "using column sub-sampling prevents over-fitting even more so than the traditional row sub-sampling" 的依據是 "According to user feedback"，非系統實驗。
- 論文寫「single machine version of XGBoost support the exact greedy algorithm」，現行預設已改為 `hist`（`auto: Same as the hist tree method`，見參數筆記）。
