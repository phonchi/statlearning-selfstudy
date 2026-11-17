# BART: Bayesian additive regression trees（Hedibert F. Lopes & Paulo Marques 講義投影片）
- URL: http://hedibert.org/wp-content/uploads/2018/06/BART.pdf
- 講義頁: p.75
- 抓取狀態: OK（PDF 共 45 頁投影片，pdftotext 抽取，第 20–23、25 頁另轉成圖片目視核對。這是投影片，不是論文；部分頁面的文字因圖層重疊而抽取錯亂）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **出處**：投影片註明多數內容由 Rob McCulloch 提供，依據 Chipman, George & McCulloch (2010), *Annals of Applied Statistics* 4(1), 266–298。（第 1 頁）
- **模型**（第 20 頁）：$Y=g(x;T_1,M_1)+\dots+g(x;T_m,M_m)+\sigma z$，$z\sim N(0,1)$。$E(Y\mid x,\theta)$ 是各樹落點底節點 $\mu$ 的總和；$m=200,1000,\dots$。原文："Such a model combines additive and interaction effects."
- **單棵樹就是階梯函數**（第 19 頁）：原文 "Easy to see that g(x; θ) is just a step function."
- **正則化先驗的三個目標**（第 21 頁）：原文 "Each T small."、"Each µ small."、"“nice” σ (smaller than least squares estimate)."；並說明 "We refer to π as a regularization prior because it keeps the overall fit small."
- **$\mu$ 的先驗**（第 22 頁）：$\mu_i\stackrel{iid}{\sim}N(0,\sigma_\mu^2)$，因此 $f(x\mid\theta)\sim N(0,m\sigma_\mu^2)$。先把資料置中，再選 $\sigma_\mu$ 讓 $f(x\mid\theta)$ 以高機率落在 $(y_{min},y_{max})$，得到 $\sigma_\mu^2\propto 1/m$。原文："In practice we often, unabashadly, use the data by first centering"。
- **MCMC**（第 23 頁）：這是一個 "simple" Gibbs sampler，依序抽 $(T_i,M_i)\mid$（其他樹、$\sigma$），再抽 $\sigma\mid$（所有樹）。
  - 抽 $(T_i,M_i)$ 時，從兩邊扣掉其他樹的貢獻，得到單棵樹模型。原文："we subract the contributions of the other trees from both sides to get a simple one-tree model."
  - 先把 $M$ 積分掉來抽 $T$，再抽 $M\mid T$。
- **樹的抽樣**（第 24–25 頁）：用 Metropolis–Hastings 提議局部修改，關鍵是 birth-death 步。第 25 頁的圖（取自 Pratola 的講義）另示 change、swap、restructure 等移動。
- **與其他方法的關聯**（第 26–27 頁）：
  - BART 會收縮到「additive 加上少量交互作用」的模型。
  - 與 boosting 類似，整體擬合是許多 weak learner 的累積。
  - 原文："BART is NOT Bayesian model averaging of single tree model."；"Unlike boosting and random forests, BART updates a set of m trees over and over, stochastic search."
  - $m$ 大適合預測，$m$ 小適合變數選擇。原文："fewer trees forces the x’s to compete for entry."
- **42 個資料集比較**（第 11–14 頁）：$p=3$–$65$，$n=100$–$7{,}000$，每個資料集 20 次 5/6 訓練、1/6 測試。BART-cv 最好，BART-default（不調參）也表現很好。相對 RMSE > 1.5 的比例：Lasso 29.5%、RF 16.2%、NN 9.0%、Boosting 13.6%、BART-cv 9.0%、BART-default 11.8%。
- **Friedman 模擬**（第 28–33 頁）：$g(x)=10\sin(\pi x_1x_2)+20(x_3-0.5)^2+10x_4+5x_5$，加 5 個無關變數，$n=100$。90% 後驗區間的頻率覆蓋率：樣本內 87%、樣本外 93%。$n=100$、$p=1000$ 時仍得到 "reasonable" 的結果。
- **二元 $y$**（第 36 頁）：原文 "Easy to extend BART to binary y using Albert & Chib."

## 可用的算例或圖解想法
- 第 19 頁「樹 ↔ 座標平面上的矩形分割」的對照圖（深度 2 樹，$\mu_1=-2,\mu_2=5,\mu_3=7$），可以直接用來說明「決策樹是階梯函數」。
- 用 backfitting 對照 boosting：BART 每輪對「扣掉其他 $m-1$ 棵樹的部分殘差」重抽一棵樹，並且反覆循環；boosting 則依序新增新樹、不回頭修改。這與第 27 頁 "updates a set of m trees over and over" 的說法一致。

## 與下列問題的關聯（只寫有關的）
- **決策樹與階梯函數**：第 19 頁原文直接可用。
- **BART 的先驗**（委派要求的項目）：此投影片**沒有**寫出樹深先驗 $\alpha(1+d)^{-\beta}$、$\sigma$ 的 inverse chi-square 先驗、$\nu, q, k$ 等超參數。只有質性的 "each T small / each µ small / nice σ"，以及 $\sigma_\mu^2\propto 1/m$。這些公式已另從原論文取得，見 `bart-cgm2010-paper.md`。
- **gradient boosting 與 shrinkage**：$\sigma_\mu^2\propto 1/m$ 讓每棵樹的貢獻變小，作用類似 boosting 的 shrinkage。（推論；原論文 §2.2.3 明白寫了這個對應，見另一份筆記。）

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 投影片部分頁面文字疊印，pdftotext 抽出的內容錯亂（例如第 23 頁）。本筆記已對照圖片核對引用內容。
- 投影片的程式範例使用 R 套件 `BayesTree`（大綱列有 "R package BayesTree"）。這個套件目前的維護狀態本次未查證，講義若要附程式，需另行確認。
- 投影片說的 "nice σ (smaller than least squares estimate)"，在原論文中是 $P(\sigma<\hat\sigma)=q$ 的設定，$\hat\sigma$ 可取樣本標準差或線性迴歸殘差標準差，並不是要求 $\sigma$ 一定小於 LS 估計。
