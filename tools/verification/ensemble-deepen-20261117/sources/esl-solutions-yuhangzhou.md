# A Solution Manual for ESL（Yuhang Zhou, GitHub Pages）
- URL: https://yuhangzhou88.github.io/ESL_Solution/
- 講義頁: p.37
- 抓取狀態: OK（首頁目錄與下列各題頁面皆以 curl 取得，HTTP 200。完整讀過的解答：Ex. 8.4、10.1、10.2、10.6、10.7、10.8、10.10、10.11、10.12、15.1、15.3–15.7、16.1–16.3；Ex. 8.1–8.3、8.5–8.7、10.3–10.5、10.9 只讀到輸出截斷處（約前 1,300 字）；含圖的題目只讀文字，圖未檢視）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
### 目錄中與集成相關的習題（依首頁連結；標 TODO 者網站未解）
- 第 15 章 Random Forests：15.1、15.2 **(TODO)**、15.3、15.4、15.5、15.6、15.7。
- 第 10 章 Boosting：10.1–10.12 皆有頁面。
- 第 8 章：8.4（bagging 線性平滑器）、8.5（多類損失）有關；8.1–8.3、8.6、8.7 是 EM／Gibbs／spline 信賴帶，與集成無關。
- 第 16 章 Ensemble Learning：16.1、16.2、16.3、16.4 **(TODO)**。

### 可直接用於教學的解答
- **Ex. 15.1**（推導 ESL (15.1)）：
  $$\operatorname{Var}\Big(\tfrac1B\textstyle\sum X_i\Big)=\frac{\sigma^2}{B}+\frac{B-1}{B}\sigma^2\rho=\rho\sigma^2+\frac{1-\rho}{B}\sigma^2 .$$
  並說明 $\rho$ 為負時隱含 $\rho\ge-\frac{1}{B-1}$（變異非負）。原句："When \(B\) is large, this (negative) lower bound is close to zero."
- **Ex. 15.4**（bootstrap 樣本平均的相關）：令兩組 bootstrap 抽樣 $\hat x_i,\tilde x_i$，得 $\operatorname{cov}(\bar x^*_1,\bar x^*_2)=\sigma^2/n$、$\operatorname{var}(\bar x^*_1)=\frac{(2n-1)\sigma^2}{n^2}$，故 $\operatorname{corr}=\frac{n}{2n-1}\approx50\%$；bagged mean 的變異為 $\frac{(2n-1)+(B-1)n}{Bn^2}\sigma^2$。（ESL 題目原句："bagging produces no reduction in variance for linear statistics."）
- **Ex. 15.5**（RF 樹間相關的條件變異分解）：利用 $\Theta_1,\Theta_2$ 給定 $\mathbf Z$ 時獨立，條件共變為 0，故分子 $=\operatorname{Var}_{\mathbf Z}[E_{\Theta|\mathbf Z}T(x;\Theta(\mathbf Z))]$，分母由 ESL (15.9) 得出：
  $$\rho(x)=\frac{\operatorname{Var}_{\mathbf Z}[E_{\Theta|\mathbf Z}T]}{\operatorname{Var}_{\mathbf Z}[E_{\Theta|\mathbf Z}T]+E_{\mathbf Z}\operatorname{Var}_{\Theta|\mathbf Z}[T]} .$$
- **Ex. 15.6**（spam 資料 OOB vs test 對 $m$）：$m$ 取 1 到 $\sqrt p\approx8$；原句："We see that OOB errors are consistent greater than test errors but have a similar trend."（僅此一次模擬的觀察）
- **Ex. 15.7**（permutation importance 在線性迴歸）：證明 $E_P[RSS^*_j-RSS]=2\hat\beta_j^2$。
- **Ex. 10.1**（AdaBoost 的 $\beta$）：對 $\beta$ 微分並設為 0，得 $e^{2\beta}=\frac{1-\text{err}_m}{\text{err}_m}$，即 $\beta=\frac12\log\frac{1-\text{err}_m}{\text{err}_m}$（ESL p.344 在 (10.15) 後註明 "where αm = 2βm is the quantity defined at line 2(c) of AdaBoost.M1"，本次於本機 PDF 核對）。
- **Ex. 10.2**：指數損失的母體最小化者為 $f^*(x)=\frac12\log\frac{P(Y=1|x)}{P(Y=-1|x)}$（半個 log-odds）。
- **Ex. 10.7**（指數損失下每片葉的最佳值）：$\hat\gamma_{jm}=\frac12\log\frac{\sum_{x_i\in R_{jm}}w_i^{(m)}\mathbb 1(y_i=1)}{\sum_{x_i\in R_{jm}}w_i^{(m)}\mathbb 1(y_i=-1)}$，$w_i^{(m)}=e^{-y_if_{m-1}(x_i)}$。
- **Ex. 10.8**（題目，取自頁面）：多類 deviance 下以 Hessian 對角近似做一步 Newton，葉值 $\gamma_k^1=\frac{\sum_{x_i\in R}(y_{ik}-p_{ik})}{\sum_{x_i\in R}p_{ik}(1-p_{ik})}$——分子是梯度（殘差）和、分母是 $p(1-p)$ 和。**題目敘述可用，但網站的解答有符號錯誤，不宜直接引用**（見「注意」）。
- **Ex. 10.9**：利用 $|r_{ikm}|(1-|r_{ikm}|)=p_k(x_i)(1-p_k(x_i))$ 推出 ESL Algorithm 10.4 的葉值更新。
- **Ex. 10.10**：$K=2$ 時兩類的負梯度互為相反數，所以每輪只需長一棵樹。
- **Ex. 10.6**（McNemar）：spam 測試集 GAM 5.5% vs GBM 4.5%，$\chi^2=\frac{(33-18)^2}{33+18}\approx4.41$，$p=0.036$（ESL p.590 比較 RF 與 bagging 時引用此檢定）。
- **Ex. 8.4**：B-spline 平滑器 $\hat f=Sy$、$S^2=S$，以參數 bootstrap 做 bagging，$\hat f_{\text{bag}}=Sy+S\big(\frac1B\sum\epsilon_b\big)\to Sy$——對線性平滑器 bagging 沒有效果。
- **Ex. 16.1**：ESL §16.2.3 區塊相關模擬資料的生成方式。

## 可用的算例或圖解想法
- Ex. 15.1 → 「$B$ 增加時變異下降到 $\rho\sigma^2$ 的地板」曲線，正好回答「為何 $B$ 大不會過擬合、但也有極限」。
- Ex. 15.4 → 簡單模擬：對樣本平均做 bagging，變異幾乎不變（對照樹）。
- Ex. 10.1／10.7 → AdaBoost 的 $\alpha$ 與葉值都是「對指數損失逐步做 argmin」。
- Ex. 10.8／10.9 → 「葉值 = 梯度和／Hessian 和」，$h=p(1-p)$；可直接接到 XGBoost 葉權重 $-G/(H+\lambda)$ 的教學（推論：XGBoost 公式本身不在此來源中）。

## 與下列問題的關聯（只寫有關的）
- bagging 為何不因 $B$ 增加而過擬合／為何 RF 要降 $\rho$：Ex. 15.1、15.5。
- OOB 為何近似 LOOCV：對應的 **Ex. 15.2 網站標 TODO，沒有解答**；本批來源中沒有任何一處給出證明。
- 變數重要度：Ex. 15.7（permutation importance 的線性迴歸版本）。
- AdaBoost 的 α 與權重更新：Ex. 10.1、10.2、10.7。
- 梯度提升葉值 argmin、分類時 $h=p(1-p)$：Ex. 10.8、10.9。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **Ex. 10.2 有符號錯誤**：解答把一階條件寫成 $P(Y=1|x)e^{-z}+P(Y=-1|x)e^{z}=0$（原始 HTML 第 3685 行確認），正確應為 $-P(Y=1|x)e^{-z}+P(Y=-1|x)e^{z}=0$；兩個正項相加不可能為 0。最後答案（半個 log-odds）正確。
- **Ex. 10.8 解答錯誤（自行核對，推論）**：(a) 一階導數寫成 $\sum_{k=1}^K\mathbb 1(y=G_k)-p_k$，多了對 $k$ 的加總，應為 $\mathbb 1(y=G_k)-p_k$；(a) 對 log-likelihood 的二階導數寫成 $+\big(p_k-p_k^2\big)$，正確應為 $-p_k(1-p_k)$；因此 (b) 最後得到 $\gamma_k^1=-\frac{\sum(y_{ik}-p_{ik})}{\sum p_{ik}(1-p_{ik})}$，與題目要證的式子差一個負號。用正確的二階導數代入 Newton 步 $\gamma^1=\gamma^0-\ell'/\ell''$ 即得題目的正號結果。(c) 只說可乘任意 $\alpha>0$，沒有用到題目要求的 symmetry argument 推出 $\frac{K-1}{K}$。
- **Ex. 15.7 額外假設**：解答說 "We need to assume that \(\bb{X}^T\bb{X}=\bb{I}.\)"，這不是題目給的條件（題目只說變數標準化為平均 0、標準差 1，且 RSS 是 mean-squared residual）；證明因此只在此附加假設下成立，常數尺度也需對照題目定義重新檢查。
- Ex. 15.6 的「OOB 一律高於 test」只是單次模擬觀察；ISLP Fig 8.8 的 Heart 資料反而是 OOB "by chance — considerably lower"。不可一般化。
- 這是個人整理的非官方解答，網站有多題 TODO；引用前應自行核算。
