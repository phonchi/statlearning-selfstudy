# 林軒田《機器學習技法》Lecture 6: Support Vector Regression（handout）
- URL: https://www.csie.ntu.edu.tw/~htlin/mooc/doc/206_handout.pdf
- 講義頁: p.34（林軒田 SVR handout 連結）
- 抓取狀態: OK（curl，HTTP 200，application/pdf，770,247 bytes；`pdftotext -layout`。注意：文字抽取遺失所有 ε 符號與部分 ≫，因此 PDF p.5、6、10–15、17、18、19 另以 `pdftoppm` 渲染核對）
- 讀取日期: 2026-11-22

頁碼慣例：「PDF p.X」為 PDF 實體頁；括號內為投影片頁尾編號（x/23）。
記號對照：N = 樣本數、d = 原始維度、d̃ = 轉換後維度、K = N×N kernel 矩陣、ε = tube 寬度。
公式轉寫：上列已渲染頁依渲染圖（ε 由圖補回）；其餘依 `pdftotext -layout` 版面轉寫。英文引句只取自文字條列。

## 重點（中文撰寫，術語保留原文）

### Representer theorem → kernel ridge regression
- 「for any L2-regularized linear model」min (λ/N)wᵀw + (1/N)Σ err(yₙ, wᵀzₙ)，最佳解 w* = Σ βₙzₙ；「—any L2-regularized linear model can be kernelized!」（PDF p.3，2/23）。證明在 Lecture 5（見 htlin-205 筆記）。
- 代入 w = Σβₙzₙ 後成為 β 的問題（轉寫）：(λ/N)βᵀKβ + (1/N)(βᵀKᵀKβ − 2βᵀKᵀy + yᵀy)；第一項為「regularization of β on K-based regularizer」，第二項為「linear regression of β on K-based features」（PDF p.4，3/23）。
- 解（PDF p.5，4/23，已渲染）：∇E_aug(β) = (2/N)Kᵀ((λI + K)β − y)，令其為 0 得 **β = (λI + K)⁻¹y**；「(·)⁻¹ always exists for λ > 0, because K positive semi-definite (Mercer’s condition…)」；「time complexity: O(N³) with simple dense matrix inversion」。
- 預測：g(x) = Σₙ βₙK(xₙ, x)（Fun Time，PDF p.7–8，6/23）。
- 線性 vs kernel ridge（PDF p.6，5/23，已渲染）：linear ridge w = (λI + XᵀX)⁻¹Xᵀy，「O(d³ + d²N) training; O(d) prediction —efficient when N ≫ d」；kernel ridge β = (λI + K)⁻¹y，「O(N³) training; O(N) prediction —hard for big data」；「trade-off between efficiency and flexibility」。

### Dense vs sparse
- LSSVM（least-squares SVM）＝kernel ridge regression 用於分類：「similar boundary, many more SVs ⇒ slower prediction, dense β」；「dense β: LSSVM, kernel LogReg; sparse α: standard SVM」（PDF p.9，7/23）。

### Tube／ε-insensitive loss（PDF p.10–11）
- err(y, s) = max(0, |s − y| − ε)：「within a tube: no error」、「outside a tube: error by distance to tube」；「usually called ε-insensitive error with ε > 0」（PDF p.10，8/23；ε 依渲染圖補回）。
- 與平方誤差比較：「tube ≈ squared when |s − y| small & less affected by outliers」（PDF p.11，9/23）。
- 直接用 representer 處理 L2-regularized tube regression：「unconstrained, but max not differentiable」、「no obvious sparsity」；改仿 standard SVM：「dual to kernelize, KKT conditions ⇒ sparsity」（PDF p.12，10/23）。

### SVR primal（PDF p.13–14）
- 轉寫：min ½wᵀw + C Σ(ξₙ∨ + ξₙ∧) s.t. −ε − ξₙ∨ ≤ yₙ − wᵀzₙ − b ≤ ε + ξₙ∧，ξₙ∨, ξₙ∧ ≥ 0；「minimize regularizer + (upper tube violations ξₙ∧ & lower violations ξₙ∨)」（PDF p.13，11/23）。
- 「parameter C: trade-off of regularization & tube violation」；「parameter ε: vertical tube width —one more parameter to choose!」；「QP of d̃ + 1 + 2N variables, 2N + 2N constraints」（PDF p.14，12/23）。
- Fun Time（PDF p.15–16，13/23）：ε = 0.05、wᵀz₁ + b = 1.234、y₁ = 1.126 ⇒ ξ₁∨ = 0.058、ξ₁∧ = 0（下方違反時上方必無違反）。

### SVR dual 與稀疏性（PDF p.17–21）
- 乘數 αₙ∧、αₙ∨；KKT：w = Σ(αₙ∧ − αₙ∨)zₙ，其中 βₙ = αₙ∧ − αₙ∨；∂L/∂b = 0 ⇒ Σ(αₙ∧ − αₙ∨) = 0；complementary slackness αₙ∧(ε + ξₙ∧ − yₙ + wᵀzₙ + b) = 0、αₙ∨(ε + ξₙ∨ + yₙ − wᵀzₙ − b) = 0（PDF p.17，14/23）。
- SVR dual（轉寫）：min ½ΣΣ(αₙ∧ − αₙ∨)(αₘ∧ − αₘ∨)k_{n,m} + Σ((ε − yₙ)αₙ∧ + (ε + yₙ)αₙ∨) s.t. Σ(αₙ∧ − αₙ∨) = 0、0 ≤ αₙ∧ ≤ C、0 ≤ αₙ∨ ≤ C；「similar QP, solvable by similar solver」（PDF p.18，15/23）。
- 稀疏：「strictly within tube |wᵀzₙ + b − yₙ| < ε」⇒ ξ 皆 0 ⇒ 兩乘數皆 0 ⇒ βₙ = 0；「SVs (βₙ ≠ 0): on or outside tube」；「SVR: allows sparse β」（PDF p.19，16/23）。
- dual 變數個數為 2N（Fun Time，PDF p.20–21，17/23）。

### Kernel 模型總覽（PDF p.22–25）
- 線性模型列：「linear soft-margin SVM」、「linear ridge regression」、「regularized logistic regression」；「second row: popular in LIBLINEAR」（PDF p.22，18/23）。
- kernel 列：SVM、SVR、probabilistic SVM「fourth row: popular in LIBSVM」；kernel ridge regression／kernel logistic regression「third row: less used due to dense β」（PDF p.23–24）。

## 與下列問題的關聯
- Q1：linear ridge 的 O(d) 預測 vs kernel ridge 的 O(N) 預測；SVM 的 α 稀疏、只用 SV（PDF p.6、p.9）。
- Q8：kernel ridge regression 的閉式解 β = (λI + K)⁻¹y 與 linear ridge 的對照（PDF p.5–6），以及 representer theorem「any L2-regularized linear model can be kernelized」（PDF p.3）。dual PCA 原文未涵蓋。
- Q9：K 半正定（Mercer’s condition）保證 λ > 0 時反矩陣存在（PDF p.5）。
- Q12：SVR、ε-insensitive loss、tube 內點 βₙ = 0（PDF p.10–19）。
- Q13：linear 模型「popular in LIBLINEAR」、kernel SVM／SVR／probabilistic SVM「popular in LIBSVM」（PDF p.22–23）。
