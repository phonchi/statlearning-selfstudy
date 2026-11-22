# SVM as a Convex Optimization Problem（Leon Gu, CSD, CMU；10-701 2008 spring recitation）
- URL: https://www.cs.cmu.edu/~epxing/Class/10701-08s/recitation/svm.pdf
- 講義頁: p.18（CMU SVM recitation 連結）
- 抓取狀態: OK（curl，HTTP 200，application/pdf，142,458 bytes，共 10 頁；`pdftotext -layout`）
- 讀取日期: 2026-11-22

頁碼為 PDF 實體頁（此份無頁尾編號）。式號為原文 (1)–(20)。
記號對照：原文 N = 樣本數、β, β₀ = 係數（與 source_brief 問題記號相同）；原文的 **C 是 margin**（相當 source_brief Q4 的 M，不是 cost），**Z 是 slack 總預算**（相當 source_brief Q6 的 const）；dual 上界記為 γ。
標題中的「10-701 2008 spring」是依 URL 路徑 `10701-08s` 推斷，PDF 本身只寫作者與單位。
公式為本筆記轉寫。

## 重點（中文撰寫，術語保留原文）

### Hard margin：從 ‖β‖ = 1 到 min ‖β‖（PDF p.3–4）
- 超平面 {x : f(x) = βᵀx + β₀ = 0}，其中 ‖β‖ = 1；「f(x) is the sign distance to the hyperplane」（p.3）。
- margin 定義為 C = minᵢ yᵢf(xᵢ)；問題：max_{β,β₀,‖β‖=1} C s.t. yᵢ(βᵀxᵢ + β₀) ≥ C（p.3）。
- 「We can get rid of the norm constraint on β」：改寫為 (1/‖β‖)yᵢ(βᵀxᵢ + β₀) ≥ C，「and arbitrarily set ‖β‖ = 1/C」，得 min ‖β‖ s.t. yᵢ(βᵀxᵢ + β₀) ≥ 1；「This is a convex optimization problem.」（p.4）。

### Soft margin：預算形式（PDF p.5、p.9）
- 式 (4)–(6)：minimize ‖β‖ s.t. yᵢ(βᵀxᵢ + β₀) ≥ 1 − ξᵢ；ξᵢ ≥ 0；Σξᵢ ≤ Z（p.5）。
- 「ξᵢ > 1 – misclassification」；「ξᵢ > 0 – the data is correctly classified but lies in the margin.」；「Z is a tuning parameter.」（p.5）。
- 注意：此處是**預算形式**（Σξ ≤ Z，目標為 ‖β‖），不是「½‖β‖² + CΣξ」的懲罰形式。原文**沒有**寫出懲罰形式，也沒有說明 Z 與懲罰權重的關係。

### Lagrangian 與 dual（PDF p.6–8）
- Lagrangian：L(x, λ, ν) = f₀(x) + Σλᵢfᵢ(x) + Σνᵢhᵢ(x)，「λ, ν are free parameters called Lagrange multipliers」（p.6）。
- Dual function g(λ, ν) = inf_x L(x, λ, ν)；dual problem 式 (10)–(11)：maximize g(λ, ν) s.t. **λ > 0**（p.7，原文寫嚴格不等號）。
- 「The weak duality theorem says g(λ, ν) ≤ f₀(x*) for all λ and ν」（p.7）。
- 原文另寫「(Note that g(λ, ν) is piecewise linear and convex)」（p.7）。本筆記標記為**原文疑誤**：dual function 一般是 concave（為 affine 函數的 infimum），且不一定 piecewise linear；此句不宜直接引用給學生。
- KKT（p.8）：「Slater’s Theorem (Strong Duality Theorem) says: if the constraint functions are affine, the duality gap is zero.」；條件列表中為 **λ*ᵢ ≥ 0**（「dual constraints」）、λ*ᵢfᵢ(x*) = 0（complementary slackness）。「Remarks: complementary slackness conditions are directly related to support vectors.」
- 不一致記錄（不在此解決）：p.7 的 dual 限制寫 λ > 0，p.8 的 KKT 寫 λ* ≥ 0。

### Soft-margin dual（PDF p.9–10）
- p.9 只列三個步驟：「Define Lagrange primal function」、「Take the first-order derivatives w.r.t. β, β₀ and ξᵢ, and set to zero」、「Substitute the results into the primal function」——**推導未實際展開**；並宣稱「Obviously strong duality holds.」
- p.10 dual（式 15–17，轉寫）：maximize L_D = Σαᵢ − ½ΣΣαᵢαᵢ′yᵢyᵢ′⟨xᵢ, xᵢ′⟩ s.t. **0 ≤ αᵢ ≤ γ**、Σαᵢyᵢ = 0。
- **γ 在原文中沒有定義**，也沒有說明它與 Z（預算）或懲罰權重的關係。推論（本筆記判斷，非原文）：p.9 的 primal 目標為 ‖β‖ 且帶預算 Σξ ≤ Z，而 p.10 的 dual 形式看起來對應的是 ½‖β‖² + γΣξ 的懲罰版本；原文未交代兩者如何銜接。
- 解：β̂ = Σα̂ᵢyᵢxᵢ（式 19）；f(x) = Σα̂ᵢyᵢ⟨xᵢ, x⟩ + β₀（式 20）。
- 「Sparse representation: the separating hyperplane f(x) is spanned those data points i where αᵢ ≠ 0, called Support Vectors.」；「Both the estimation and the evaluation of f(x) only involve dot product.」（p.10）。

### 對 focus「C 是 Lagrange-like 權重還是約束預算」
- 原文未涵蓋 C 作為懲罰權重的討論。只能說：原文用 Z 作預算、用 γ 作 dual 上界，但沒有連結兩者。

## 與下列問題的關聯
- Q4：p.3–4 的「arbitrarily set ‖β‖ = 1/C」（此 C 為 margin）正是 max M s.t. ‖β‖ = 1 → min ‖β‖ 的改寫。
- Q5：dual 的 λ 條件，p.7 寫 > 0、p.8 KKT 寫 ≥ 0（原文自身不一致）；complementary slackness 連結到 SV（p.8、p.10）。
- Q6：預算形式 Σξ ≤ Z（p.5）與 dual 上界 γ（p.10）；原文未說明 γ 與 Z 的關係，不能拿來回答「C 與 const 反比」。
- Q10：αᵢ ≠ 0 的點為 SV；ξ > 0 在 margin 內、ξ > 1 被誤分（p.5、p.10）。
