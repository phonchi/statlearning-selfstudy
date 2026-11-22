# 林軒田《機器學習技法》Lecture 3: Kernel Support Vector Machine（handout）
- URL: https://www.csie.ntu.edu.tw/~htlin/mooc/doc/203_handout.pdf
- 講義頁: **非講義直接連結**；經 p.36 的課程索引頁（https://www.csie.ntu.edu.tw/~htlin/mooc/）連到
- 抓取狀態: OK（curl，HTTP 200，application/pdf，1,232,047 bytes；`pdftotext -layout`；PDF p.15 另以 `pdftoppm` 渲染核對）
- 讀取日期: 2026-11-22

頁碼慣例：「PDF p.X」為 PDF 實體頁；括號內為投影片頁尾編號（x/22）。
記號對照：N = 樣本數、d = 原始維度、d̃ = 轉換後維度、Φ = feature transform。公式轉寫：PDF p.15 依渲染圖，其餘依 `pdftotext -layout` 版面。

## 重點（中文撰寫，術語保留原文）

### Kernel trick
- 目標：dual 中 q_{n,m} = yₙyₘzₙᵀzₘ 需要「zₙᵀzₘ = Φ(xₙ)ᵀΦ(xₘ) calculated faster than O(d̃)」（PDF p.3，2/22）。
- 二次轉換 Φ₂(x) = (1, x₁, …, x_d, x₁², x₁x₂, …, x_d²)（「include both x₁x₂ & x₂x₁ for ‘simplicity’」），其內積 = 1 + xᵀx′ + (xᵀx′)²；「for Φ₂, transform + inner product can be carefully done in O(d) instead of O(d²)」（PDF p.4，3/22）。
- 「kernel trick: plug in efficient kernel function to avoid dependence on d̃」；b 與 g_SVM 都只需 K(xₙ, x)（PDF p.5，4/22）。
- 演算法成本：建 Q_D「O(N²) · (kernel evaluation)」；「QP with N variables and N + 1 constraints」；求 b 與預測「O(#SV) · (kernel evaluation)」；「use computational shortcut to avoid d̃ & predict with SV only」（PDF p.6，5/22）。

### Polynomial kernel
- 對 Φ₂ 的分量縮放（√2、√(2γ)、γ）得 K₂(x, x′) = (1 + γxᵀx′)²；「Φ₂ and Φ₂ [兩種縮放]: equivalent power, different inner product ⇒ different geometry」（PDF p.9，7/22）。
- 「change of kernel ⇔ change of margin definition」（PDF p.10，8/22）。
- 一般式 K_Q(x, x′) = (ζ + γxᵀx′)^Q，γ > 0、ζ ≥ 0（PDF p.11，9/22）。Fun Time 答案：(ζ + γxᵀx′)² 對應 Φ(x) = (ζ, √(2γζ)x₁, …, √(2γζ)x_d, γx₁², …, γx_d²)（PDF p.13–14，11/22）。
- K₁ = linear kernel，「can be solved (often in primal form) efficiently」（PDF p.12，10/22）。

### Gaussian kernel：為何是無窮維（PDF p.15，12/22；已渲染）
- 一維、γ = 1 的例子：K(x, x′) = exp(−(x − x′)²) = exp(−x²)exp(−x′²)exp(2xx′)，以 Taylor 展開 exp(2xx′) = Σᵢ (2xx′)ⁱ/i!，得 Φ(x) = exp(−x²)·(1, √(2/1!)x, √(2²/2!)x², …)，為**無窮維**向量。
- 「infinite dimensional Φ(x)? Yes, if K(x, x′) efficiently computable!」；一般式 K(x, x′) = exp(−γ‖x − x′‖²)，γ > 0。
- g_SVM 為「linear combination of Gaussians centered at SVs xₙ」，「also called Radial Basis Function (RBF) kernel」（PDF p.16，13/22）。
- 「infinite-dimensional linear classification, with generalization ‘guarded by’ large-margin」（PDF p.17，14/22）。

### γ 的效果
- 三圖 γ = 1、10、100：「large γ ⇒ sharp Gaussians ⇒ ‘overfit’?」；「warning: SVM can still overfit」；「Gaussian SVM: need careful selection of γ」（PDF p.18，15/22）。
- Fun Time（PDF p.19–20，16/22）：γ → ∞ 時 K 收斂到 ⟦x = x′⟧，「Thus, K_lim is an impulse function, which is an extreme case of how the Gaussian gets sharper when γ → ∞.」

### Kernel 比較與 Mercer’s condition
- Linear：「safe」、「fast—with special QP solver in primal」、「very explainable—w and SVs say something」（PDF p.21）。
- Polynomial：大 Q 有數值困難（|ζ + γxᵀx′| < 1 時 K → 0；> 1 時 K → big）；三個參數較難選（PDF p.22）。
- Gaussian：「mysterious—no w」、「slower than linear」、「too powerful?!」；「bounded—less numerical difficulty than poly.」、「one parameter only」（PDF p.23）。
- Mercer’s condition（PDF p.24，20/22）：「necessary & sufficient conditions for valid kernel」：symmetric，且 kernel 矩陣 K = ZZᵀ「must always be positive semi-definite」；「define your own kernel: possible, but hard」。
- Fun Time（PDF p.25–26）：(−1 + xᵀx′)² 在 x₁ = (1)、x₂ = (−1) 時 kernel 矩陣非半正定，故不是合法 kernel。

## 與下列問題的關聯
- Q1：預測只需 SV，成本 O(#SV)·kernel evaluation（PDF p.6、p.17）。
- Q8：kernel 矩陣 K = ZZᵀ（樣本×樣本，PDF p.24）。
- Q9：Mercer’s condition（PDF p.24）；Gaussian kernel 無窮維的 Taylor 展開（PDF p.15）；γ 大 ⇒ 尖銳 Gaussian、可能 overfit、極限為 impulse（PDF p.18–20）。
