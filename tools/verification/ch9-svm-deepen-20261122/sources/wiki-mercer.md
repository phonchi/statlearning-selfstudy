# Mercer's theorem（Wikipedia）
- URL: https://en.wikipedia.org/wiki/Mercer%27s_theorem
- 講義頁: p.26（錨文字：未提供）
- 抓取狀態: OK（curl `action=raw` wikitext，HTTP 200；revid 1370093161，2026-08-19T02:14:46Z；全文已讀）。頁首有 {{More footnotes needed|date=December 2024}}，兩個推廣定理標有 {{citation needed|date=February 2026}}。
- 讀取日期: 2026-11-22

## 重點（中文撰寫，術語保留原文）
### 主定理（〈Introduction〉，特例形式）
- **定義域**：閉區間 [a,b]。kernel 是 "a symmetric continuous function K: [a,b] × [a,b] → ℝ"，且 K(x,y)=K(y,x)。
- **正定性的定義（實為半正定）**：對任意有限點列 x₁…xₙ ∈ [a,b] 與任意實數 c₁…cₙ，∑ᵢ∑ⱼ K(xᵢ,xⱼ)cᵢcⱼ ≥ 0。頁面明說："the term "positive-definite" is well-established in literature despite the weak inequality in the definition."
- **積分算子**：[T_K φ](x) = ∫ₐᵇ K(x,s)φ(s) ds，φ ∈ L²[a,b]，測度為 Lebesgue。頁面在括號中說 "Hilbert–Schmidt integral operator when the interval is compact"。
- **定理敘述**："Suppose K is a continuous symmetric positive-definite kernel." 結論是：存在由 T_K 的 eigenfunctions 構成的 L²[a,b] **orthonormal basis** {eᵢ}，對應 eigenvalues {λᵢ} 非負；非零 eigenvalue 對應的 eigenfunction 在 [a,b] 上連續；而且
  K(s,t) = ∑_{j=1}^∞ λⱼ eⱼ(s) eⱼ(t)，"where the convergence is absolute and uniform."
- **假設清單**：連續、對稱、半正定（文中稱 positive-definite），定義在緊緻區間 [a,b] 上，配 Lebesgue 測度。
### 證明架構（〈Details〉）
- T_K 是 "non-negative symmetric compact operator on L²[a,b]"，並且 K(x,x) ≥ 0。緊緻性來自 Ascoli 定理，eigen 分解來自緊算子的 spectral theorem。
- 一致收斂的關鍵界：∑ λᵢ |eᵢ(t)eᵢ(s)| ≤ sup_{x∈[a,b]} |K(x,x)|。
- eigenvalue 非負的理由是 λ⟨f,f⟩ = ⟨f, T_K f⟩，再以 Riemann 和逼近，由正定性得 ≥0。
### Trace（〈Trace〉）
- ∫ₐᵇ K(t,t) dt = ∑ᵢ λᵢ，所以 T_K 是 trace class。
### 推廣（〈Generalizations〉）
- 有限維版本："any symmetric positive-semidefinite matrix is the Gramian matrix of a set of vectors"。
- 推廣一 [citation needed]：把 [a,b] 換成任意 **compact Hausdorff space** X，測度換成 Borel 上的有限可數可加測度 μ，且 support 為整個 X，"μ(U) > 0 for any nonempty open subset U"。
- 推廣二 [citation needed]：X 為 first-countable 拓撲空間，μ 為 Borel（complete）測度，X 是 μ 的 support，每點有有限測度的開鄰域，並且要求 κ(x)=K(x,x) ∈ L¹_μ(X)。結論變成 **orthonormal set**（不再是 basis），收斂 "absolute and uniform on compact subsets of X"。
- 可測（L²）kernel 版本：σ-finite 測度空間，K ∈ L²(X×X)，只得到 L² 收斂。原文："when continuity of the kernel is not assumed, the expansion no longer converges uniformly."
### Mercer's condition（〈Mercer's condition〉）
- 對所有平方可積的 g，∬ g(x)K(x,y)g(y) dx dy ≥ 0。〈Discrete analog〉把它類比為半正定矩陣 gᵀKg ≥ 0。
- 平穩 kernel K(x−y) 由 Bochner 定理刻畫：連續的 K(x−y) 為正定，當且僅當它是某個有限非負測度的 Fourier transform（〈Introduction〉）。

### 本頁未提及
- 沒有提到 RBF/Gaussian kernel 本身，也沒有談 ℝᵖ（非緊緻）上的 RBF 該套用哪個版本、γ 的意義，或「特徵空間無窮維」的說法。導言只說 Mercer 在 RKHS 理論中 "characterizes a symmetric positive-definite kernel as a reproducing kernel"。

## 與下列問題的關聯（只寫有關的題號）
- 第 9 題（核心：Mercer 的精確假設與 eigen 展開。由 K(s,t)=∑λⱼeⱼ(s)eⱼ(t) 可推出特徵映射 φ(x)=(√λⱼ eⱼ(x))ⱼ，非零 eigenvalue 無窮多時即為無窮維。這一步是推論，頁面沒有寫出 φ）
- 第 8 題（間接：Gram 矩陣半正定是 kernel 合法的有限維條件）
