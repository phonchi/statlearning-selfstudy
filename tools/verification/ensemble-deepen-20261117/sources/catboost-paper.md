# CatBoost: unbiased boosting with categorical features（Prokhorenkova et al., NeurIPS 2018）
- URL: https://proceedings.neurips.cc/paper/2018/file/14491b756b3a51daac41c24863285549-Paper.pdf
- 講義頁: p.58
- 抓取狀態: OK（PDF 共 11 頁，用 pdftotext 抽取；補充材料未抓。表格被逐欄抽出，數字已逐列核對對齊）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **核心問題：prediction shift 來自一種 target leakage**。boosting 若干步後的模型 $F$ 依賴所有訓練樣本的 target，所以訓練樣本上 $F(x_k)\mid x_k$ 的分佈與測試樣本上 $F(x)\mid x$ 的分佈不同。原文："This finally leads to a prediction shift of the learned model."（§1）
- **Greedy target statistic（式 4）**：用同類別樣本的平均 $y$ 取代類別，並以先驗 $p$ 平滑：
$$\hat x^i_k=\frac{\sum_{j=1}^n \mathbb 1\{x^i_j=x^i_k\}\,y_j+a\,p}{\sum_{j=1}^n \mathbb 1\{x^i_j=x^i_k\}+a},\qquad a>0$$
  原文："A common setting for p is the average target value in the dataset"（§3.2）
- **greedy TS 的洩漏與極端例**：
  - 問題在於 $\hat x^i_k$ 的計算用到了自己的 $y_k$，造成 conditional shift。
  - 極端例：每個類別都只出現一次，且 $P(y=1\mid x^i)=0.5$。此時訓練集上 $\hat x^i_k=\frac{y_k+ap}{1+a}$，一刀切在 $t=\frac{0.5+ap}{1+a}$ 就能完美分類訓練資料；但測試時 TS 全等於 $p$，準確率只有 0.5。
  - 由此提出期望性質 **P1**：$E(\hat x^i\mid y=v)=E(\hat x^i_k\mid y_k=v)$。
- **一般解法是排除自己（式 5）**：用 $D_k\subset D\setminus\{x_k\}$ 計算
$$\hat x^i_k=\frac{\sum_{x_j\in D_k}\mathbb 1\{x^i_j=x^i_k\}\,y_j+a\,p}{\sum_{x_j\in D_k}\mathbb 1\{x^i_j=x^i_k\}+a}$$
- **Holdout TS**：滿足 P1，但浪費資料，違反 **P2**（"Effective usage of all training data for calculating TS features and for learning a model."）。
- **Leave-one-out TS 仍然洩漏**：當類別特徵為常數時，$\hat x^i_k=\frac{n^+-y_k+ap}{n-1+a}$，一刀切在 $t=\frac{n^+-0.5+ap}{n-1+a}$ 即可完美分開。原文："Surprisingly, it does not prevent target leakage."（§3.2）
- **Ordered TS**：取一個隨機排列 $\sigma$ 當作人工「時間」，訓練樣本只用排在它前面的樣本，即 $D_k=\{x_j:\sigma(j)<\sigma(k)\}$；測試樣本用全部訓練資料 $D_k=D$。這同時滿足 P1 與 P2。
  - 單一排列會讓排在前面的樣本 TS 變異很大，所以不同 boosting 步使用不同排列。
- **prediction shift 的理論（Thm 1）**：平方損失、兩個 Bernoulli(1/2) 特徵、$y=c_1x^1+c_2x^2$、兩步 stump、步長 1。
  - 兩步用獨立資料時：$E F^2(x)=f^*(x)+O(2^{-n})$。
  - 兩步用同一份資料時：$E F^2(x)=f^*(x)-\frac{1}{n-1}c_2\big(x^2-\tfrac12\big)+O(2^{-n})$，偏誤與 $n$ 成反比。
- **Ordered boosting（Alg. 1）**：維護 $n$ 個支援模型 $M_i$，$M_i$ 只用排列中前 $i$ 個樣本訓練；樣本 $j$ 的殘差用 $M_{j-1}$ 計算。
  - 直接實作需要 $n$ 個模型，不可行。原文："this algorithm is not feasible in most practical tasks due to the need of training n different models"（§4.2）
  - TS 與 boosting 必須用同一排列（$\sigma_{cat}=\sigma_{boost}$）。
- **實作的兩種模式**：原文 "CatBoost has two boosting modes, Ordered and Plain."（§5）Plain 是標準 GBDT 加上內建 ordered TS。
- **使用 $s+1$ 個排列**：$\sigma_1..\sigma_s$ 用來評估分割、決定樹結構，$\sigma_0$ 用來決定最終葉值。
- **Oblivious trees（對稱樹，優先查證 4）**：CatBoost 的 base predictor 是 oblivious decision trees，又稱 decision tables。原文："Term oblivious means that the same splitting criterion is used across an entire level of the tree."（§5 "Building a tree"）論文接著說這種樹平衡、較不易過擬合，並且能大幅加速測試時的執行。
- **選分割的準則（Alg. 2）**：以葉內平均梯度構成的向量 $\Delta$ 與梯度向量 $G$ 的 cosine similarity 評分。Ordered 模式只平均「排列中在前」的樣本梯度。
- **複雜度**：實作時只存 $M'_{r,j}(i)=M_{r,2^j}(i)$，把支援預測的數量從 $O(sn^2)$ 降到 $O(sn)$。Table 1 顯示 ordered boosting 與「標準 GBDT 加 ordered TS」有相同的漸近複雜度。
- **類別特徵組合**：貪婪地把樹中已用過的類別特徵（及其組合）與資料中所有類別特徵串接，並即時轉成 TS。
- **Bayesian bootstrap**：樣本權重 $w_i=a_i^t$，依 Bayesian bootstrap 產生（引 Rubin）。這些權重乘在梯度上。
- **捨棄排列開頭**：排在排列前面的樣本梯度變異大，計算 cosine 時會丟掉這些分量。
- **實驗（Table 2）**：CatBoost（Ordered 模式）在 9 個資料集的 logloss 與 zero-one loss 都最好。例如 Amazon 上 LightGBM 與 XGBoost 的 logloss 都高出 +17%；Epsilon 上 XGBoost 高 +11%。除 Appetency、Churn、Upselling 外，改善都顯著（p ≪ 0.01）。
- **Ordered vs Plain（Table 3、Fig. 2）**：Ordered 對小資料集特別有用。Adult 與 Internet 的訓練集都不到 40K 筆。Ordered 模式約比 Plain 慢 1.7 倍；在 Epsilon 上，Plain 與 LightGBM 最快。
- **TS 比較（Table 4）**：ordered TS 明顯勝過 greedy、holdout、leave-one-out；在基線中，holdout 在多數資料集最好。原文："the greedy TS suffer from low-frequency categories, while the leave-one-out TS suffer also from high-frequency ones"（§6）
- **對 LightGBM 類別處理的評語**（§3.1）：LightGBM 每步把類別轉成 gradient statistics，計算與記憶體成本高，並且把尾端類別併成一群而損失資訊。

## 可用的算例或圖解想法
- **Greedy TS 洩漏的極端例**：每個 ID 只出現一次，$a=1$，$p=0.5$。訓練集 TS 為 $(y_k+0.5)/2\in\{0.25,0.75\}$，切在 0.5 就完美分類；測試集 TS 全為 0.5。這個例子可直接畫成兩條數線。
- **LOO 洩漏例**：常數類別，$n=11$，$n^+=6$，取 $a=0$。$y=1$ 的樣本 TS 為 $5/10=0.5$，$y=0$ 的樣本為 $6/10=0.6$，兩群完全分開。這與 CatBoost 教學 notebook 的 5/6 例吻合（見 `catboost-tutorial-categorical-params.md`）。
- **Ordered TS 表**：可直接採用官方文件 rock/indie/pop 的 7 列例子（見 `catboost-docs-cat-to-numeric.md`，已逐格驗算）。
- **對稱樹圖**：深度 3 的 oblivious tree 每層只有一個條件，8 片葉可以用 3 個位元索引（推論：預測時直接把 3 個比較結果組成葉索引，這正是測試加速的原因；論文只寫 "speeding up execution at testing time"）。

## 與下列問題的關聯（只寫有關的）
- **CatBoost 對稱樹（優先查證 4）**：論文 §5 明寫 base predictor 是 oblivious decision trees，同一層使用同一個分裂條件。官方參數頁也寫 `grow_policy` 預設為 `SymmetricTree`，但另有 `Depthwise` 與 `Lossguide` 可選（見 `catboost-training-parameters.md`）。所以「CatBoost 用對稱樹」正確的說法是「預設」，而不是唯一選項。
- **gradient 與殘差**：§4.1 在平方損失下把負梯度寫成殘差 $r^{t-1}=y_k-F^{t-1}(x_k)$，並註明去掉了係數 2。
- **bagging／OOB**：論文提到 Breiman 的 iterated bagging 以 OOB 殘差建模，但補充材料證明這種殘差估計仍有偏移。
- **stacking vs voting（間接）**：把 TS 當特徵用，本質上是用另一個模型的輸出當特徵，所以必須用 out-of-fold 或依序的方式避免洩漏。這個道理與 stacking 必須用 OOF 預測相同。（推論）

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **TS 公式在論文與官方文件不同**：論文式 (4)/(5) 為 $(\sum y+a\,p)/(\text{count}+a)$。官方文件為 $(\text{countInClass}+\text{prior})/(\text{totalCount}+1)$，等同 $a=1$，且 prior 直接扮演 $a\cdot p$ 的角色。教學時要說明兩者的對應關係。
- **預設值與論文實驗設定不同**：
  - 論文實驗採 Ordered 模式，但官方參數頁寫 CPU 上 `boosting_type` 預設為 `Plain`，Ordered 只在 GPU 且資料 ≤ 50K 筆（非多類別）時才是預設（見 `catboost-training-parameters.md`）。
  - 論文描述用 Bayesian bootstrap，但現行 CPU、非多類別、`sampling_unit=Object` 的預設是 MVS（subsample 0.8）。
  - 所以「CatBoost 預設用 ordered boosting」在 CPU 上不正確。
- **與 LightGBM／XGBoost 的比較有前提**：論文寫 "For all learning algorithms, we preprocess categorical features using the ordered TS method"（§6）。也就是說，Table 2 中 LightGBM 與 XGBoost 也用了 CatBoost 的 ordered TS，比較的是 boosting 本身，而不是各套件原生的類別處理。
- 論文未說明 $s$ 的實際預設值。CatBoost 教學 notebook 說「四個排列、三個用於選結構」，但這屬於教學文的說法，未在論文中出現。
