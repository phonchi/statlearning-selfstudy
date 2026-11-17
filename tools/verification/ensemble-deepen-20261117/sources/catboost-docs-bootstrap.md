# Bootstrap options（CatBoost 官方文件）
- URL: https://catboost.ai/en/docs/concepts/algorithm-main-stages_bootstrap-options
- 講義頁: p.59
- 抓取狀態: OK（curl 取得 HTML，`yfm-latex` 公式已解碼）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **`bootstrap_type` 的兩個目的**：
  1. 正則化：在不同分割步或不同樹之間改變樣本權重，但同一個分割的各候選之間權重不變。原文："the weight of each training example is varied over steps of choosing different splits"。
  2. 加速：只用部分樣本為候選分割評分。評分成本為 $O(|C|\cdot n)$，"Usually, this computation dominates over all other steps"。
- **Bayesian**：權重 $w=a^{t}$，其中 $a=-\log(\psi)$，$\psi\sim\text{Uniform}[0,1]$，$t$ 為 `bagging_temperature`。相當於 Rubin (1981) 的 Bayesian bootstrap。
  - 原文："The Bayesian bootstrap serves only for the regularization, not for speeding up."
  - `bagging_temperature=1` 時權重服從指數分佈；`=0` 時權重全為 1；值越大 bagging 越強。
- **Bernoulli**：即 Stochastic Gradient Boosting（Friedman）。每個樣本以 `subsample` 機率獨立被選中，選中者權重相等。原文："it speeds up calculations almost (1/subsample) times."
- **MVS（Minimum Variance Sampling）**：一種重要性抽樣。
  - 梯度為 $g_i=\partial L(y_i,z)/\partial z\,|_{z=M(i)}$。$|g_i|$ 最大的樣本以機率 $p_i=1$ 選入，其他樣本以機率 $|g_i|/\mu$ 選入，$\mu$ 是「大梯度」的門檻。
  - 期望梯度的估計為
$$\widehat{E\,g}=\frac{\sum_{i\in\text{sampled}} g_i/p_i}{\sum_{i\in\text{sampled}} 1/p_i}$$
    分子是梯度和的不偏估計，分母是樣本數的不偏估計。
  - 理論性質：在固定期望抽樣數 $s=\sum_i p_i$ 下，MVS 給出 L2 split score 的最小變異估計。
  - `mvs_reg` 在重要性抽樣（0）與 Bernoulli（∞）之間調整；未設定時依當輪梯度分佈自動決定。
  - **與 GOSS 的比較**：原文 "MVS can be considered as an improved version of the Gradient-based One-Side Sampling (GOSS ...) implemented in LightGBM"。GOSS 對其餘樣本用「相同的固定機率」抽樣，原文 "MVS provides a lower variance of the estimate $\hat{E\,g}$ than GOSS."
  - 注意事項原文："MVS may not be the best choice for regularization, since sampled examples and their weights are similar for close iterations."
- **Poisson**（僅 GPU）：權重 i.i.d. 抽自參數為 $-\log(1-subsample)$ 的 Poisson 分佈。`subsample=0.66` 時近似經典 bootstrap。
- **No**：所有樣本等權。
- **重抽頻率** `sampling_frequency`：`PerTree`（每棵樹前）或 `PerTreeLevel`（每選一個分割前）。
- **頁尾建議**：原文 "It is recommended to use MVS when speeding up is an important issue and regularization is not."

## 可用的算例或圖解想法
- **MVS 與 GOSS 對照**（推論，用 LightGBM 論文 Alg. 2 的設定）：
  - GOSS 對前 $a$ 比例取機率 1，其餘一律以相同機率抽樣，再乘 $(1-a)/b$。
  - MVS 對其餘樣本以 $|g_i|/\mu$ 的機率抽樣，再用 $1/p_i$ 加權（Horvitz–Thompson 形式）。
  - 可以畫一張「抽樣機率 vs $|g|$」的圖：GOSS 是兩段的階梯，MVS 是先線性上升、再截在 1。
- **Bayesian bootstrap 權重的直覺**：`bagging_temperature=1` 時 $w\sim\text{Exp}(1)$。可以與經典 bootstrap 的 Poisson(1) 計數權重並列成直方圖比較。（推論）

## 與下列問題的關聯（只寫有關的）
- **bagging 與 boosting 的結合**：CatBoost 每棵樹（甚至每層）都重抽權重，屬於隨機梯度提升。這裡的權重抽樣是為了正則化與加速，與 random forest 中 bagging 降低變異的目的不完全相同。（推論）
- **Hessian／gradient 當權重**：MVS 用 $|g_i|$ 決定抽樣機率，與 XGBoost 加權分位草圖用 $h_i$ 當權重不同，兩者目的也不同。（推論）

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **文件 typo**：Bernoulli 與 Poisson 小節的 `subsample` 參數下，"Command-line version" 寫成 `--bagging-temperature`。官方參數頁的正確寫法是 `--subsample`（見 `catboost-training-parameters.md`）。
- **預設值說法有歧義**：`bagging_temperature` 的說明寫 "It is used by default in classification and regression modes."，容易讓人以為 Bayesian 是預設。但官方參數頁寫：非 MultiClass、CPU、`sampling_unit=Object` 時，預設是 MVS（subsample 0.8），其餘情況才是 Bayesian。教學應以參數頁為準。
- NeurIPS 2018 論文只描述 Bayesian bootstrap，沒有提到 MVS。教學時不要把論文的設定當成現行預設。
