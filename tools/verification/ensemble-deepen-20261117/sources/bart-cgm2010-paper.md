# BART: Bayesian Additive Regression Trees（Chipman, George & McCulloch, AoAS 2010）— 補充來源
- URL: https://arxiv.org/pdf/0806.3286 （arXiv v2，2010-10-07；期刊版 DOI 10.1214/09-AOAS285）
- 講義頁: 無（講義 p.75 連到 Lopes 的投影片，投影片沒有先驗公式，因此補抓原論文）
- 抓取狀態: OK（PDF 共 35 頁，pdftotext 抽取；只讀了 §2.2–§3.1）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **先驗分解**：$p((T_1,M_1),\dots,(T_m,M_m),\sigma)=\big[\prod_j p(M_j\mid T_j)p(T_j)\big]p(\sigma)$，其中 $p(M_j\mid T_j)=\prod_i p(\mu_{ij}\mid T_j)$。各樹之間、各樹與 $\sigma$ 之間獨立。（§2.2.1，式 (5)(6)）
- **樹結構先驗 $p(T_j)$**（§2.2.2）：深度 $d$ 的節點為 nonterminal 的機率是
$$\alpha(1+d)^{-\beta},\qquad \alpha\in(0,1),\ \beta\in[0,\infty)$$
  - 分裂變數用均勻先驗，分裂值用「可用值」上的均勻先驗。
  - 預設 $\alpha=0.95$、$\beta=2$。在此設定下，葉數為 1、2、3、4、≥ 5 的先驗機率分別為 0.05、0.55、0.28、0.09、0.03。原文："trees with 1, 2, 3, 4 and ≥5 terminal nodes receive prior probability of 0.05, 0.55, 0.28, 0.09 and 0.03"
  - 資料需要時仍可長大樹：在 $m=1$ 的模擬中，觀察到相當的後驗機率落在 17 片葉的樹上。
- **葉值先驗**（§2.2.3）：$\mu_{ij}\mid T_j\sim N(\mu_\mu,\sigma_\mu^2)$（共軛，可積分掉）。誘導出 $E(Y\mid x)\sim N(m\mu_\mu, m\sigma_\mu^2)$。
  - 先把 $Y$ 平移縮放到 $[-0.5,0.5]$，再取 $\mu_\mu=0$、$k\sqrt m\,\sigma_\mu=0.5$，即
$$\mu_{ij}\sim N(0,\sigma_\mu^2),\qquad \sigma_\mu=\frac{0.5}{k\sqrt m}$$
  - $k=2$ 時，$E(Y\mid x)$ 落在 $(y_{min},y_{max})$ 的先驗機率約 95%。$k$ 取 1–3 效果都好，推薦預設 $k=2$。
  - **與 boosting shrinkage 的對應**：原文 "Prior shrinkage on the µij’s is the counterpart of the shrinkage parameter in Friedman’s (2001) gradient boosting algorithm."
  - 不需要轉換預測變數，因為樹的分裂規則對 $x$ 的單調轉換不變。
- **$\sigma$ 先驗**（§2.2.4）：$\sigma^2\sim\nu\lambda/\chi^2_\nu$（inverse chi-square，共軛）。
  - 以粗略高估值 $\hat\sigma$（$Y$ 的樣本標準差，或線性迴歸的殘差標準差）校準：$\nu$ 取 3–10，$\lambda$ 取使 $P(\sigma<\hat\sigma)=q$ 的值。
  - 三組設定 $(\nu,q)=(10,0.75)$、$(3,0.90)$、$(3,0.99)$ 分別稱為 conservative、default、aggressive。推薦 $(3,0.90)$，不建議 $\nu<3$，因為那會過擬合。
- **樹的數量 $m$**（§2.2.5）：預設 $m=200$。原文："the predictive performance of BART improves dramatically until at some point it levels off and then begins to very slowly degrade for large values of m."
- **Bayesian backfitting MCMC**（§3.1）：
  - Gibbs sampler 依序抽 $(T_j,M_j)\mid T_{(j)},M_{(j)},\sigma,y$（$j=1..m$），再抽 $\sigma$（inverse gamma）。
  - 條件只透過部分殘差 $R_j=y-\sum_{k\ne j}g(x;T_k,M_k)$ 依賴其他樹，所以等價於單棵樹模型 $R_j=g(x;T_j,M_j)+\varepsilon$。
  - 先用 MH 抽 $T_j$（$M_j$ 積分掉），再抽 $M_j$（獨立常態）。
  - MH 的四種移動與提議機率：grow 0.25、prune 0.25、change 0.40、swap 0.10。
  - 因為 $M_j$ 被積分掉，不需要 reversible jump。
  - 這個名稱沿用 Hastie & Tibshirani (2000) 的 Bayesian backfitting。

## 可用的算例或圖解想法
- **驗算樹大小先驗**（我依式 (7) 自行計算）：
  - 根節點分裂機率 0.95，所以 1 片葉的機率為 0.05。
  - 深度 1 的節點分裂機率 $0.95/4=0.2375$。2 片葉 $=0.95\times(1-0.2375)^2\approx0.552$。
  - 3 片葉 $=0.95\times 2(0.2375)(0.7625)\times(1-0.95/9)^2\approx0.275$。
  - 結果與論文的 0.55、0.28 一致，可做成教學表格。
- **$\sigma_\mu=0.5/(k\sqrt m)$ 的數值**：$m=200$、$k=2$ 時 $\sigma_\mu\approx0.0177$（$Y$ 已縮放到 $[-0.5,0.5]$），每棵樹的葉值都很小，對應 boosting 的小學習率。（推論）

## 與下列問題的關聯（只寫有關的）
- **BART 先驗**（委派指定）：樹深先驗 $\alpha(1+d)^{-\beta}$（0.95, 2）、葉值先驗 $N(0,(0.5/(k\sqrt m))^2)$（$k=2$）、$\sigma^2\sim\nu\lambda/\chi^2_\nu$（$(\nu,q)=(3,0.9)$）、backfitting MCMC，以上全部有原文出處。
- **interaction depth d**：BART 不直接設深度，而是用 $\beta$ 讓深節點越來越不可能分裂，先驗使大部分機率集中在 2–3 片葉，與 boosting 常用的淺樹相呼應。（推論）
- **bagging 為何不易因 B 增加而過擬合（對照）**：BART 的 $m$ 增加時，預測先大幅改善再趨平，非常大時才緩慢變差，這與 RF 的 B 行為不同。（推論；論文只描述 BART 的現象。）

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 這是補充來源，不在講義連結中。引用時請標示原論文。
- 以上預設值是論文（2010）的建議值；各軟體套件（如 BayesTree、dbarts、BART）的預設可能不同，本次未查證。
