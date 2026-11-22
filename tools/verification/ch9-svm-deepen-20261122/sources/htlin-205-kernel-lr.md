# 林軒田《機器學習技法》Lecture 5: Kernel Logistic Regression（handout）
- URL: https://www.csie.ntu.edu.tw/~htlin/mooc/doc/205_handout.pdf
- 講義頁: **非講義直接連結**；經 p.36 的課程索引頁（https://www.csie.ntu.edu.tw/~htlin/mooc/）連到
- 抓取狀態: OK（curl，HTTP 200，application/pdf，574,172 bytes；`pdftotext -layout`；PDF p.5、6、8、11、21 另以 `pdftoppm` 渲染核對）
- 讀取日期: 2026-11-22

頁碼慣例：「PDF p.X」為 PDF 實體頁；括號內為投影片頁尾編號（x/20）。注意原文 Fun Time 說的「page 4 of the slides」是頁尾編號 4/20，即 PDF p.5。
記號對照：N = 樣本數、zₙ = Φ(xₙ)、s = wᵀzₙ + b（score）、θ = logistic function。公式轉寫：已渲染頁依渲染圖，其餘依 `pdftotext -layout` 版面。

## 重點（中文撰寫，術語保留原文）

### 回顧（PDF p.3，2/20）
- 並列 hard／soft-margin 的 primal 與 dual；soft-margin dual 只多了 0 ≤ αₙ ≤ C。「soft-margin preferred in practice; linear: LIBLINEAR; non-linear: LIBSVM」。

### Soft-margin SVM = L2 正則化 + hinge loss
- ξₙ = margin violation = max(1 − yₙ(wᵀzₙ + b), 0)；「‘unconstrained’ form of soft-margin SVM」：min ½wᵀw + CΣmax(1 − yₙ(wᵀzₙ + b), 0)（PDF p.4，3/20）。
- 與 L2 正則化對照：min (λ/N)wᵀw + (1/N)Σerr，「just L2 regularization」、「with shorter w, another parameter, and special err」；不直接解此式是因為「not QP, no (?) kernel trick」、「max(·, 0) not differentiable」（PDF p.5，4/20）。
- 表格（PDF p.6，5/20；已渲染）：regularization by constraint = minimize E_in s.t. wᵀw ≤ C；hard-margin SVM = minimize wᵀw s.t. E_in = 0；L2 regularization = (λ/N)wᵀw + E_in；soft-margin SVM = ½wᵀw + C·N·Ê_in。
- 「large margin ⇔ fewer hyperplanes ⇔ L2 regularization of short w」；「soft margin ⇔ special err」。
- 「larger C or C ⇔ smaller λ ⇔ less regularization」：渲染圖中**兩個 C 顏色不同**——藍色 C 是「wᵀw ≤ C」的預算，紅色 C 是 soft-margin 的懲罰權重。兩者放大都等於 λ 變小、正則化變弱。
- Fun Time（PDF p.7–8，6/20）：larger C ⇒ smaller λ, weaker regularization；「Comparing the formulations on page 4 of the slides, we see that C corresponds to 1/(2λ).」（1/(2λ) 依渲染圖確認）。對照：ESL 習題 12.1 解答採「λ = 1/C」慣例（見 esl-ex12-1-solution 筆記），差別在正則項係數寫法。

### Hinge loss 與 logistic loss（PDF p.9–12）
- err₀/₁(s, y) = ⟦ys ≤ 0⟧；err̂_SVM(s, y) = max(1 − ys, 0)：「upper bound of err₀/₁ —often called hinge error measure」；「algorithmic error measure by convex upper bound of err₀/₁」（PDF p.9–10，7/20）。
- Fun Time（PDF p.13–14，10/20）：hinge 與 0/1 相等「if and only if ys ≥ 1」，此時兩者皆為 0。
- errSCE(s, y) = log₂(1 + exp(−ys))：「another upper bound of err₀/₁ used in logistic regression」（PDF p.11，8/20；已渲染）。用 log₂（scaled cross-entropy）是為了讓它在 ys = 0 時等於 1、成為 0/1 error 的上界（本筆記推論：log₂(1 + e⁰) = 1）。
- 漸近比較（PDF p.11）：ys → −∞ 時 err̂_SVM ≈ −ys、(ln 2)·errSCE ≈ −ys；ys → +∞ 時 err̂_SVM = 0、(ln 2)·errSCE ≈ 0。
- 結論：「SVM ≈ L2-regularized logistic regression」（PDF p.11）；「regularized LogReg ⇒ approximate SVM」、「SVM ⇒ approximate LogReg (?)」（PDF p.12，9/20）。

### Probabilistic SVM（Platt’s model，PDF p.15–19）
- 兩層學習：g(x) = θ(A·(w_SVMᵀΦ(x) + b_SVM) + B)；A 縮放、B 平移；「often A > 0 if w_SVM reasonably good」、「often B ≈ 0 if b_SVM reasonably good」（PDF p.16，12/20）。
- 「Platt’s Model of Probabilistic SVM」：先跑 SVM 得分數 z′ₙ，再對 {(z′ₙ, yₙ)} 跑 LogReg 求 (A, B)；「actual model adds some special regularization here」；「soft binary classifier not having the same boundary as SVM classifier —because of B」（PDF p.17，13/20）。

### Representer theorem 與 kernel logistic regression（PDF p.20–25）
- SVM、PLA、SGD LogReg 的 w 都是 Σ(αₙyₙ)zₙ（PDF p.20，15/20）。
- Representer theorem（PDF p.21，16/20；已渲染）：「claim: for any L2-regularized linear model」min (λ/N)wᵀw + (1/N)Σerr(yₙ, wᵀzₙ)，最佳 w* = Σβₙzₙ。證明：把 w* 拆成 w∥（在 span(zₙ) 中）+ w⊥；w∥ 有相同 err（因 w⊥ᵀzₙ = 0）、較小正則項（原文 w*ᵀw* = w∥ᵀw∥ + 2w∥ᵀw⊥ + w⊥ᵀw⊥ > w∥ᵀw∥，其中交叉項 2w∥ᵀw⊥ = 0），矛盾，所以 w⊥ = 0。「any L2-regularized linear model can be kernelized!」
- KLR：min_β (λ/N)ΣΣβₙβₘK(xₙ, xₘ) + (1/N)Σlog(1 + exp(−yₙΣβₘK(xₘ, xₙ)))，用「GD/SGD/... for unconstrained optimization」（PDF p.22，17/20）。
- 另一觀點：ΣΣβₙβₘK = βᵀKβ 是「a special regularizer」；「KLR = linear model of β with kernel as transform & kernel regularizer」（PDF p.23，18/20）。
- 「warning: unlike coefficients αₙ in SVM, coefficients βₙ in KLR often non-zero!」（PDF p.23）。
- Fun Time（PDF p.24–25，19/20）：KLR 作為 β 的線性模型時，轉換後資料 (K(x₁, x), …, K(x_N, x)) 為 **N 維**。

## 與下列問題的關聯
- Q1：KLR 的 β 通常稠密 vs SVM 的 α 稀疏（PDF p.23）。
- Q6：C ↔ 1/(2λ)（PDF p.8）；藍 C（預算）與紅 C（懲罰）放大都代表正則化變弱（PDF p.6）。
- Q8：kernel 想法用於 LR（KLR）；representer theorem 適用於任何 L2 正則化線性模型（PDF p.21–23）。
- Q11：hinge 轉折與 ys ≥ 1（PDF p.9、p.14）；scaled cross-entropy log₂(1 + exp(−ys))；「SVM ≈ L2-regularized logistic regression」（PDF p.11）。
- Q13：Platt’s probabilistic SVM（PDF p.16–17）；「linear: LIBLINEAR; non-linear: LIBSVM」（PDF p.3）。
