# The Elements of Statistical Learning (2nd ed., 12th printing), Chapter 10: Boosting and Additive Trees
- URL: 本機 `~/statslearning/ESLII_print12.pdf`（Hastie, Tibshirani & Friedman）
- 講義頁: （課本，非講義連結；供 p.44–53 的 AdaBoost／GBM 段落對照）
- 抓取狀態: OK（`pdftotext -layout` 抽取；書頁 = PDF 頁 − 19，例如書 p.339 = PDF p.358）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）

### §10.1 AdaBoost.M1（書 p.337–340）
- 二元問題編碼 $Y\in\{-1,1\}$；最終分類器為加權多數決 $G(x)=\mathrm{sign}\big(\sum_{m=1}^M \alpha_m G_m(x)\big)$（式 10.1，p.338）。原文："give higher influence to the more accurate classifiers in the sequence"（p.338）。
- 演算法 10.1（p.339）逐步：
  1. $w_i=1/N$。
  2. 對 $m=1..M$：(a) 以權重 $w_i$ 擬合 $G_m$；(b) $\mathrm{err}_m=\dfrac{\sum_i w_i I(y_i\ne G_m(x_i))}{\sum_i w_i}$；(c) $\alpha_m=\log\big((1-\mathrm{err}_m)/\mathrm{err}_m\big)$；(d) $w_i\leftarrow w_i\exp[\alpha_m I(y_i\ne G_m(x_i))]$。
  3. 輸出 $\mathrm{sign}\big[\sum_m \alpha_m G_m(x)\big]$。
- 演算法 10.1 **沒有**權重正規化步驟；err_m 本身是比值，所以不需要（推論：整體縮放不影響 err_m 與下一輪的加權擬合）。
- 原文（p.339）："Observations misclassified by Gm(x) have their weights scaled by a factor exp(αm)"。
- AdaBoost.M1 又稱 "Discrete AdaBoost"（Friedman et al. 2000）；基學習器輸出實數時有 "Real AdaBoost"（p.339）。
- 模擬例（式 10.2）：10 個獨立標準常態特徵，$Y=1$ 若 $\sum X_j^2>\chi^2_{10}(0.5)=9.34$；2000 筆訓練、10,000 筆測試；stump 單獨測試誤差 45.8%，boosting 400 輪降到 5.8%，單一 244 節點樹 24.7%（p.339–340，圖 10.2）。

### §10.2–10.3 Forward stagewise additive modeling（p.341–343）
- 基底展開 $f(x)=\sum_m \beta_m b(x;\gamma_m)$（10.3）；演算法 10.2：$f_0=0$，每步解 $(\beta_m,\gamma_m)=\arg\min_{\beta,\gamma}\sum_i L(y_i,f_{m-1}(x_i)+\beta b(x_i;\gamma))$，不回頭修改已加入的項。原文："Previously added terms are not modified."（p.342）
- 平方損失下 $L=(r_{im}-\beta b(x_i;\gamma))^2$，$r_{im}=y_i-f_{m-1}(x_i)$ 為殘差（10.7，p.343）：每步就是「擬合目前殘差」。

### §10.4 指數損失與 AdaBoost（p.343–344）——α 從何而來
- 損失 $L(y,f)=\exp(-yf)$（10.8）。代入 forward stagewise 得 $(\beta_m,G_m)=\arg\min\sum_i w_i^{(m)}\exp(-\beta y_i G(x_i))$，$w_i^{(m)}=\exp(-y_i f_{m-1}(x_i))$（10.9）。
- 對任意 $\beta>0$，$G_m=\arg\min_G\sum_i w_i^{(m)} I(y_i\ne G(x_i))$（10.10）——即最小化加權誤分率。理由：準則可寫成 $(e^\beta-e^{-\beta})\sum_i w_i^{(m)}I(y_i\ne G(x_i))+e^{-\beta}\sum_i w_i^{(m)}$（10.11）。
- 解出 $\beta_m=\tfrac12\log\dfrac{1-\mathrm{err}_m}{\mathrm{err}_m}$（10.12，p.344）。
- 權重更新 $w_i^{(m+1)}=w_i^{(m)}e^{-\beta_m y_iG_m(x_i)}$（10.14）；用 $-y_iG_m(x_i)=2I(y_i\ne G_m(x_i))-1$ 化為 $w_i^{(m+1)}=w_i^{(m)}e^{\alpha_m I(\cdot)}e^{-\beta_m}$（10.15），**其中 $\alpha_m=2\beta_m$**。原文："The factor e−βm in (10.15) multiplies all weights by the same value, so it has no effect."（p.344）
- **½ 與無 ½ 的差別（重點）**：演算法 10.1 的 $\alpha_m=\log((1-\mathrm{err})/\mathrm{err})$ 恰好是 forward-stagewise 係數 $\beta_m$ 的兩倍。因為最終分類用 $\mathrm{sign}(\cdot)$，所有係數同乘 2 不改變分類結果；權重更新中多出的 $e^{-\beta_m}$ 是共同因子，正規化後消失。差別只在 $f$ 的尺度：用 $\beta_m$ 時 $f$ 估計的是 ½ log-odds（見 10.16）。（推論：同乘 2 不影響 sign 這一點書中未逐字寫出，但由 10.1 與 10.15 直接可得。）
- 我的核算（推論，sympy）：對 $(e^b-e^{-b})e+e^{-b}$ 對 $b$ 微分求根，得 $b^*=\tfrac12\log((1-e)/e)$，與 10.12 一致。
- 結論句（p.344）："AdaBoost.M1 minimizes the exponential loss criterion (10.8) via a forward-stagewise additive modeling approach."
- 圖 10.3：訓練誤分率約 250 輪降到 0，但平均指數損失持續下降；測試誤分率在 250 輪後仍改善（p.344–345）。

### §10.5 為何是指數損失（p.345–346）
- 族群最小化子 $f^*(x)=\arg\min_f E_{Y|x}e^{-Yf(x)}=\tfrac12\log\dfrac{\Pr(Y=1|x)}{\Pr(Y=-1|x)}$（10.16）。原文："the additive expansion produced by AdaBoost is estimating one-half the log-odds of P(Y = 1|x)."（p.346）
- 二項 deviance 用 **½ log-odds 參數化**：$p(x)=1/(1+e^{-2f(x)})$（10.17），$-l(Y,f)=\log(1+e^{-2Yf})$（10.18）；與指數損失有相同族群最小化子。
- 注意尺度：ESL 這裡的 $f$ 是 ½ log-odds、$Y\in\{-1,1\}$。我的核算（推論）：$-\partial/\partial f\,\log(1+e^{-2Yf})=2Y/(1+e^{2Yf})=2(y'-p)$，$y'=(Y+1)/2$。若改用全 log-odds $F$ 與 $y\in\{0,1\}$（XGBoost 慣例），則 $g=p-y$、$h=p(1-p)$——**兩種尺度不可混用**。
- 原文（p.345）："The principal attraction of exponential loss in the context of additive modeling is computational"。

### §10.6 損失函數與穩健性（p.346–350）
- 分類以 margin $yf(x)$ 表示；圖 10.4 比較 misclassification、exponential $\exp(-yf)$、binomial deviance $\log(1+\exp(-2yf))$、squared error $(y-f)^2$、SVM hinge $(1-yf)_+$（p.347）。
- 原文（p.347）："The penalty associated with binomial deviance increases linearly for large increasingly negative margin"；指數損失則指數增長 → deviance "far more robust in noisy settings"，AdaBoost 在標籤錯誤時"dramatically degrade"（p.348）。
- 平方損失對分類不好：族群解 $2\Pr(Y=1|x)-1$（10.19），且對 $yf>1$ 二次增加、不是 margin 的單調遞減函數（p.348）。
- K 類：multinomial deviance（10.22），$p_k=e^{f_k}/\sum_l e^{f_l}$（10.21），對稱約束 $\sum_k f_k=0$（p.348–349）。
- 迴歸：平方損失族群解為 $E(Y|x)$，絕對損失為 $\mathrm{median}(Y|x)$；Huber 損失（10.23，p.349）：
  $L=[y-f]^2$ 若 $|y-f|\le\delta$；否則 $2\delta|y-f|-\delta^2$。圖 10.5 比較三者（p.350）。
- 原文（p.349）："squared-error loss places much more emphasis on observations with large absolute residuals"。

### §10.7 off-the-shelf（p.350–352）
- 表 10.1：Trees 在 mixed data、缺失值、輸入空間離群值、單調轉換不變、可擴展性、無關輸入方面為「good」，但 Predictive power 為「poor」（p.351）。原文："boosting decision trees improves their accuracy, often dramatically."（p.352）

### §10.9 Boosting trees（p.353–358）
- 樹：$T(x;\Theta)=\sum_{j=1}^J\gamma_j I(x\in R_j)$（10.25）。給定區域時 $\hat\gamma_j$ 通常是區內 $\bar y_j$（p.356）。
- 提升樹 $f_M=\sum_m T(x;\Theta_m)$（10.28），每步解 10.29。**給定區域後葉值**：$\hat\gamma_{jm}=\arg\min_{\gamma}\sum_{x_i\in R_{jm}}L(y_i,f_{m-1}(x_i)+\gamma)$（10.30，p.357）——每片葉各自一個 argmin。
- **平方損失下葉值 = 該葉殘差平均**。原文（p.357）："γ̂jm is the mean of these residuals in each corresponding region."
- 指數損失、無 ±1 限制時，葉值為加權 log-odds 的一半：$\hat\gamma_{jm}=\tfrac12\log\dfrac{\sum_{R_{jm}}w_i^{(m)}I(y_i=1)}{\sum_{R_{jm}}w_i^{(m)}I(y_i=-1)}$（10.32，p.357）。
- 絕對損失時葉值是區內殘差中位數；其他準則有快速迭代解，原文（p.358）："usually their faster “single-step” approximations are adequate."

### §10.10 Gradient boosting（p.358–361）
- 把 $\mathbf f=(f(x_1),\dots,f(x_N))$ 當參數；steepest descent $\mathbf h_m=-\rho_m\mathbf g_m$，$g_{im}=\partial L(y_i,f(x_i))/\partial f(x_i)|_{f=f_{m-1}}$（10.35），步長 $\rho_m$ 由 line search（10.36）。
- 關鍵類比（p.359）：10.30 是 line search 的對應，但"performs a separate line search for those components of tm that correspond to each separate terminal region"。→ 這就是「每片葉各自 argmin」的理由。
- 梯度只定義在訓練點上，為了泛化，用最小平方把樹擬合到負梯度：$\tilde\Theta_m=\arg\min_\Theta\sum_i(-g_{im}-T(x_i;\Theta))^2$（10.37，p.359）。之後再用 10.30 算葉值（p.360）。
- 表 10.2（p.360）負梯度：
  | 損失 | $-\partial L/\partial f$ |
  |---|---|
  | $\tfrac12[y-f]^2$ | $y-f$ |
  | $|y-f|$ | $\mathrm{sign}[y-f]$ |
  | Huber | $y-f$ 若 $|y-f|\le\delta_m$；否則 $\delta_m\,\mathrm{sign}[y-f]$，$\delta_m=\alpha$th-quantile$\{|y_i-f(x_i)|\}$ |
  | Deviance（K 類） | 第 k 分量 $I(y_i=G_k)-p_k(x_i)$ |
  表 10.2 沒有獨立列出二元 logistic；二元時只需一棵樹（Ex. 10.10）。
- 演算法 10.3（p.361）：
  1. $f_0(x)=\arg\min_\gamma\sum_i L(y_i,\gamma)$（最佳常數）；
  2. 對 $m=1..M$：(a) $r_{im}=-[\partial L(y_i,f(x_i))/\partial f(x_i)]_{f=f_{m-1}}$；(b) 對 $r_{im}$ 擬合迴歸樹得 $R_{jm}$；(c) $\gamma_{jm}=\arg\min_\gamma\sum_{x_i\in R_{jm}}L(y_i,f_{m-1}(x_i)+\gamma)$；(d) $f_m=f_{m-1}+\sum_j\gamma_{jm}I(x\in R_{jm})$。
  3. 輸出 $f_M$。偽殘差原文："referred to as generalized or pseudo residuals"（p.360）。
- 原實作名 MART；R `gbm` 套件（p.361）。

### 葉值一步 Newton 近似的出處（特別確認 c）
- **第 10 章正文（已讀 p.337–373，另 grep p.374–380 的 `newton|single-step|one-step` 為 0 筆）沒有寫出 Σr/Σp(1−p)**；正文只在 p.358 說 "single-step" 近似通常足夠。
- 明確公式在 **Exercise 10.8(b)，式 10.57（p.386）**：K 類、$y_{ik}\in\{0,1\}$、只用 Hessian 對角、從 $\gamma_k=0$ 出發的一步近似 Newton：
  $\gamma_k^1=\dfrac{\sum_{x_i\in R}(y_{ik}-p_{ik})}{\sum_{x_i\in R}p_{ik}(1-p_{ik})}$，$k=1,\dots,K-1$。
  10.58 再對稱化：$\hat\gamma_k=\frac{K-1}{K}\big(\gamma_k^1-\frac1K\sum_\ell\gamma_\ell^1\big)$。
- **演算法 10.4（K 類 gradient boosting，p.387）** 步驟 2(b)iii：$\gamma_{jkm}=\dfrac{K-1}{K}\dfrac{\sum_{x_i\in R_{jkm}}r_{ikm}}{\sum_{x_i\in R_{jkm}}|r_{ikm}|(1-|r_{ikm}|)}$，$r_{ikm}=y_{ik}-p_k(x_i)$。
- 推論：因 $r=y-p$ 且 $y\in\{0,1\}$，$|r|(1-|r|)=p(1-p)$ 恆成立（y=1 時 $|r|=1-p$；y=0 時 $|r|=p$）。K=2、固定 $f_2$ 時 10.57 即全 log-odds 下的二元公式 $\sum(y-p)/\sum p(1-p)$；10.58／演算法 10.4 的 $(K-1)/K=\tfrac12$ 是對稱參數化把 log-odds 改變量平分到 $f_1,f_2$ 兩邊所致。
- Friedman (2001) 原文本次**未取得**（jerryfriedman.su.domains 憑證過期、statweb.stanford.edu DNS 失敗、Project Euclid 只回空殼），其 LK_TreeBoost 公式未核對。

### §10.11 Right-sized trees（p.361–363）
- 每棵樹獨立剪枝 "implicitly that each tree is the last one in the expansion"——除最後一棵外是很差的假設，導致樹太大（p.362）。策略：所有樹同大小 $J_m=J$。
- ANOVA 展開 $\eta(X)=\sum_j\eta_j(X_j)+\sum_{jk}\eta_{jk}+\sum_{jkl}\eta_{jkl}+\cdots$（10.40）。
- 原文（p.362）："no interaction effects of level greater than J − 1 are possible." J=2（stump）只有主效應；J=3 允許二變數交互。
- 圖 10.9：生成模型為加法模型，stumps 最佳；J>2 只增加變異（p.363）。原文（p.363）："Experience so far indicates that 4 ≤ J ≤ 8 works well"，且很少比 J≈6 有顯著改善；"it is unlikely that J > 10 will be required."
- 與 ISLP 的對應（推論）：J 個終端節點 = J−1 次分裂；ISLP 的 d（splits）= J−1，故 ESL「交互階數 ≤ J−1」與 ISLP「d splits 最多涉及 d 個變數」一致。

### §10.12 Regularization（p.364–367）
- M 用驗證集 early stopping 選（p.364）。
- Shrinkage：$f_m=f_{m-1}+\nu\sum_j\gamma_{jm}I(x\in R_{jm})$，$0<\nu<1$（10.41）；ν 是 learning rate。原文（p.365）："the best strategy appears to be to set ν to be very small (ν < 0.1) and then choose M by early stopping." ν 與 M 存在取捨。
- 圖 10.11：shrinkage 的好處對 deviance 尤其明顯（p.366）。
- Subsampling（stochastic gradient boosting，Friedman 1999）：每輪**不放回**抽比例 η 的觀測值；典型 η=½，大 N 時可更小（p.365）。原文（p.365）："in many cases it actually produces a more accurate model." 圖 10.12：sampling＋shrinkage 略優；無 shrinkage 的 subsampling 表現差（p.365–367）。
- 四個參數 J, M, ν, η；通常先定 J, ν, η，M 為主要參數（p.367）。

### §10.13.1 Relative importance（p.367–368）
- 單棵樹（Breiman et al. 1984）：$\mathcal I_\ell^2(T)=\sum_{t=1}^{J-1}\hat\imath_t^2 I(v(t)=\ell)$（10.42），對以 $X_\ell$ 分裂的內部節點加總平方誤差改善量。
- 提升樹：對 M 棵**平均** $\mathcal I_\ell^2=\frac1M\sum_m\mathcal I_\ell^2(T_m)$（10.43）。原文（p.368）："Due to the stabilizing effect of averaging, this measure turns out to be more reliable than is its counterpart (10.42)"。且因 shrinkage，相關變數互相 masking 較不嚴重。
- 10.42/10.43 是平方 relevance，實際值取平方根；習慣把最大者設為 100（p.368）。K 類：先對 M 平均（10.45）再對 K 類平均（10.46）。

## 可用的算例或圖解想法
- AdaBoost 的 α：用 10.11 畫「準則 vs β」曲線，最小點 = ½log((1−err)/err)；再並列演算法 10.1 的 α=2β 說明只差尺度。
- 「每片葉獨立 line search」：用 p.359 的類比畫 steepest descent（單一 ρ）vs gradient tree boosting（每葉一個 γ_jm）。
- J 與交互：圖 10.9（stumps vs 10/100 節點）＋10.40 ANOVA 展開。
- shrinkage／subsampling：圖 10.11、10.12。

## 與下列問題的關聯
- AdaBoost 的 α 與權重更新從何而來：§10.4（10.9–10.15）完整推導，α=2β。
- 梯度提升為何對每片葉取 argmin、平方損失下葉值等於殘差平均：10.30、p.357、p.359、演算法 10.3(c)。
- gradient 與殘差：表 10.2 平方損失負梯度即殘差；p.360 "pseudo residuals"。
- interaction depth：§10.11（J−1）。
- 變數重要度為何對 B 棵平均：10.43 及 "stabilizing effect of averaging"。
- 分類時 h=p(1−p)：Ex. 10.8／10.57、演算法 10.4 的分母。
- 決策樹與階梯函數：10.25 與 p.372 "Decision trees produce discontinuous piecewise constant models"。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- ESL 二元 deviance 用 ½ log-odds 與 $Y\in\{\pm1\}$，XGBoost／多數教學用全 log-odds 與 $y\in\{0,1\}$；直接搬 ESL 的梯度會差常數 2（Hessian 差 4）。
- 演算法 10.1 的 α 與 10.12 的 β 相差 2 倍，教學時須明說是同一件事的兩種尺度。
- ESL 的 subsampling 是不放回抽樣，與 bagging 的 bootstrap 不同。
- ESL p.358 的「single-step 近似」沒在正文寫出公式，公式藏在習題 10.8 與演算法 10.4；引用時要標習題出處。
