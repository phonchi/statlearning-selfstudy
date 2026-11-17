# Introduction to Boosted Trees（XGBoost 官方文件教學）
- URL: https://xgboost.readthedocs.io/en/latest/tutorials/model.html
- 講義頁: p.53
- 抓取狀態: OK（WebFetch 讀渲染頁；逐字內容另以原始檔 https://raw.githubusercontent.com/dmlc/xgboost/master/doc/tutorials/model.rst 核對，HTTP 200，272 行；假設 "latest" 對應 master 分支，未核對，但兩者公式與 WebFetch 讀到的渲染頁一致）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
章節順序：Elements of Supervised Learning（Model and Parameters／Objective Function: Training Loss + Regularization／Why introduce the general principle?）→ Decision Tree Ensembles → Tree Boosting（Additive Training／Model Complexity／The Structure Score／Learn the tree structure）→ Final words on XGBoost。

### 目標函數
- $\mathrm{obj}(\theta)=L(\theta)+\Omega(\theta)$。原文："The **regularization term** is what people usually forget to add."（Objective Function 節）
- 平方損失 $L=\sum_i(y_i-\hat y_i)^2$（**無 ½**）；logistic loss $L=\sum_i[y_i\ln(1+e^{-\hat y_i})+(1-y_i)\ln(1+e^{\hat y_i})]$（同節）。
- 樹集成：$\hat y_i=\sum_{k=1}^K f_k(x_i)$，$f_k\in\mathcal F$（所有 CART 的集合）；$\mathrm{obj}=\sum_i l(y_i,\hat y_i)+\sum_k\omega(f_k)$（Decision Tree Ensembles 節）。
- 原文："random forests and boosted trees are really the same models; the difference arises from how we train them."（同節）

### Additive training
- $\hat y_i^{(0)}=0$，$\hat y_i^{(t)}=\hat y_i^{(t-1)}+f_t(x_i)$。
- $\mathrm{obj}^{(t)}=\sum_i l(y_i,\hat y_i^{(t-1)}+f_t(x_i))+\omega(f_t)+\text{constant}$。
- 平方損失展開：$\sum_i[2(\hat y_i^{(t-1)}-y_i)f_t(x_i)+f_t(x_i)^2]+\omega(f_t)+\text{const}$。原文："a first order term (usually called the residual) and a quadratic term."
- 一般損失取二階 Taylor 展開：
  $\mathrm{obj}^{(t)}=\sum_i[l(y_i,\hat y_i^{(t-1)})+g_if_t(x_i)+\tfrac12h_if_t^2(x_i)]+\omega(f_t)+\text{const}$，
  $g_i=\partial_{\hat y_i^{(t-1)}}l(y_i,\hat y_i^{(t-1)})$，$h_i=\partial^2_{\hat y_i^{(t-1)}}l(y_i,\hat y_i^{(t-1)})$。
- 去常數後：$\sum_i[g_if_t(x_i)+\tfrac12h_if_t^2(x_i)]+\omega(f_t)$。原文："the value of the objective function only depends on g_i and h_i. This is how XGBoost supports custom loss functions."

### Model complexity
- $f_t(x)=w_{q(x)}$，$w\in\mathbb R^T$，$q:\mathbb R^d\to\{1,\dots,T\}$；$T$ 為葉數。
- $\omega(f)=\gamma T+\tfrac12\lambda\sum_{j=1}^T w_j^2$。原文："there is more than one way to define the complexity, but this one works well in practice."

### Structure score
- $\mathrm{obj}^{(t)}\approx\sum_i[g_iw_{q(x_i)}+\tfrac12h_iw_{q(x_i)}^2]+\gamma T+\tfrac12\lambda\sum_jw_j^2=\sum_j[(\sum_{i\in I_j}g_i)w_j+\tfrac12(\sum_{i\in I_j}h_i+\lambda)w_j^2]+\gamma T$，$I_j=\{i\mid q(x_i)=j\}$。
- $G_j=\sum_{i\in I_j}g_i$，$H_j=\sum_{i\in I_j}h_i$：$\mathrm{obj}^{(t)}=\sum_j[G_jw_j+\tfrac12(H_j+\lambda)w_j^2]+\gamma T$。
- 各 $w_j$ 互相獨立、為二次式，故
  $w_j^*=-\dfrac{G_j}{H_j+\lambda}$，$\mathrm{obj}^*=-\tfrac12\sum_j\dfrac{G_j^2}{H_j+\lambda}+\gamma T$。原文："The last equation measures *how good* a tree structure q(x) is."
- 原文（圖 struct_score.png 說明）："This score is like the impurity measure in a decision tree, except that it also takes the model complexity into account."

### Learn the tree structure
- 一次只把一片葉切成兩片：
  $\mathrm{Gain}=\tfrac12\Big[\dfrac{G_L^2}{H_L+\lambda}+\dfrac{G_R^2}{H_R+\lambda}-\dfrac{(G_L+G_R)^2}{H_L+H_R+\lambda}\Big]-\gamma$；四項分別為新左葉分數、新右葉分數、原葉分數、新增葉的正則化。
- 原文："if the gain is smaller than γ, we would do better not to add that branch. This is exactly the **pruning** techniques"。
- 連續特徵：原文："we place all the instances in sorted order"，以及 "A left to right scan is sufficient to calculate the structure score of all possible split solutions"。
- 限制註記："Limitation of additive tree learning"：一次只加一個分裂、一次只看一個特徵維度，某些邊緣情況會得到退化模型（連結到 "Can Gradient Boosting Learn Simple Arithmetic?"）。

## 可用的算例或圖解想法
- 推論（我自己算的二元 logistic 小例，全 log-odds、$y\in\{0,1\}$）：一片葉有 3 筆，$y=(1,0,1)$，目前 $\hat y^{(t-1)}=0$ 即 $p=0.5$。
  $g=p-y=(-0.5,0.5,-0.5)$，$G=-0.5$；$h=p(1-p)=0.25$，$H=0.75$。
  λ=1：$w^*=0.5/1.75\approx0.286$；λ=0：$w^*=0.5/0.75\approx0.667=\sum(y-p)/\sum p(1-p)$（與 ESL 習題 10.8 式 10.57 在 K=2 時一致）。
  若切成 L={y=1,y=0}、R={y=1}，λ=1、γ=0：$G_L=0,H_L=0.5$；$G_R=-0.5,H_R=0.25$；Gain $=\tfrac12[0+0.25/1.25-0.25/1.75]\approx0.0286$。
  λ 的直覺：分母加 λ → 葉值向 0 收縮，H 小（樣本少或 p 接近 0/1）時收縮最明顯。
- 平方損失（文件版，無 ½）：推論 $g_i=2(\hat y_i-y_i)$、$h_i=2$，λ=0 時 $w^*=\sum(y_i-\hat y_i)/n_j$＝葉內殘差平均；若損失取 $\tfrac12(y-\hat y)^2$ 則 $g=\hat y-y$、$h=1$，結論相同。
- 「push g_i、h_i 到葉、加總、套公式」可做成表格動畫。

## 與下列問題的關聯
- XGBoost 葉輸出與 p、p₀、log-odds 的關係：本頁的 $\hat y$ 是 raw score（logistic loss 寫成 $\ln(1+e^{-\hat y})$，所以 $\hat y$ 在 log-odds 尺度）；$w^*$ 加到 log-odds 上（推論：由本頁 logistic loss 形式推得）。本頁把初值設為 $\hat y^{(0)}=0$。
- λ 的直覺：$w_j^*=-G_j/(H_j+\lambda)$。
- 為何以 Hessian 當權重／分類時 h=p(1−p)：本頁只給一般 $h_i$ 定義；$h=p(1-p)$ 是推論（sympy：對 $F$ 微分 logistic loss 得 $g=p-y$、$h=p(1-p)$）。
- gradient 與殘差：平方損失一次項原文稱 "usually called the residual"。
- 直方圖對誰切、quantile sketch、缺失值方向、min_child_weight、tree_method／grow_policy：**此來源未提**。
- 優先查證 1（排序成本）：本頁只說 "place all the instances in sorted order" 加左到右掃描，未談 pre-sorted block 或每節點是否重排。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- "if the gain is smaller than γ" 與 Gain 公式已減 γ 略不一致：嚴格說是方括號那項（½[…]）小於 γ，即 Gain<0 時不切（推論）。
- $\hat y^{(0)}=0$ 是教學簡化；實際函式庫的初始分數此頁未提（推論：函式庫另有初始分數參數，非本批來源、未核對），不可據此教學。
- 平方損失沒有 ½，所以 $g$、$h$ 帶因子 2；與 ESL 表 10.2（有 ½）比較時注意。
- 這裡的 λ 是 L2 正則化，與 ISLP 的 λ（shrinkage）不同；γ 是每片葉的懲罰（同時是分裂門檻），與 ESL 的葉值 γ_jm 同名不同義。
- 同一推導中 Taylor 展開那式用 "="，Structure score 那式用 "≈"，符號不一致（無實質錯誤）。
