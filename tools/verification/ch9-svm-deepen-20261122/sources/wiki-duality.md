# Duality (optimization)（Wikipedia）
- URL: https://en.wikipedia.org/wiki/Duality_(optimization)
- 講義頁: p.17（錨文字：未提供）
- 抓取狀態: OK（curl `action=raw` wikitext，HTTP 200；revid 1306932479，2025-08-20T14:42:39Z；全文已讀）
- 讀取日期: 2026-11-22

## 重點（中文撰寫，術語保留原文）
- **Weak duality**（導言）：primal 是 min 時，dual 是 max。"Any feasible solution to the primal (minimization) problem is at least as large as any feasible solution to the dual"，也就是 dual 給出 primal 的下界。
- **Strong duality**（導言）："For convex optimization problems, the duality gap is zero under a constraint qualification condition."
- **Lagrangian dual 的構造**（〈Dual problem〉）："forming the Lagrangian of a minimization problem by using nonnegative Lagrange multipliers to add the constraints"。接著對 primal 變數取極小，把 primal 變數寫成乘數的函數，最後對 dual variables 求極大，"(including at least the nonnegativity constraints)"。
- **乘數符號慣例**（〈The strong Lagrange principle〉）：標準形式是 min f₀(x)，限制為 fᵢ(x) ≤ 0 與 hᵢ(x)=0，Lagrangian 為 𝓛(x,λ,ν)=f₀+∑λᵢfᵢ+∑νᵢhᵢ。不等式乘數 λ ≥ 0，等式乘數 ν 不限號："for any λ ≥ 0 and any ν we have g(λ,ν) ≤ p*"。
  - **頁內用詞不一致，照錄**：〈Lagrange duality〉的 Motivation 段把指標函數 I[u] 近似為 λu，"where λ is a positive constant"（正數）。但同段後面的式子與其他各節都寫成 max over λ ≥ 0（允許 =0）。
  - 同段證明說明為何允許 λ=0："If x satisfies all constraints … L(x, λ) is maximized when taking λ = 0"。也就是說，可行點上不起作用的限制，最佳乘數取 0。
- **Dual function 必為 concave**："The dual function g is concave, even when the initial problem is not convex"，因為它是 affine 函數的逐點下確界（〈The strong Lagrange principle〉）。
- **Slater 條件與 strong duality**（〈Lagrange duality〉）："If the primal problem is convex and bounded from below, and there exists a point in which all nonlinear constraints are strictly satisfied (Slater's condition)"，則 dual 最佳值等於 primal 最佳值。此時可先解出 λ*，再解 min_x L(x,λ*)。
- **Saddle point**："(x*, λ*) is a saddle point of … L if and only if x* is an optimal solution to the primal, λ* … to the dual"，且兩者最佳值相等。
- **Wolfe dual**（〈Convex problems〉）：若 f、gᵢ 連續可微，inf 發生在梯度為 0 處，於是把 ∇f+∑uⱼ∇gⱼ=0 當作限制。（推論，頁面沒有寫：這對應 SVM 推導中「對 β 偏微分令其為 0，再代回 Lagrangian」的步驟。）原文："the infimum occurs where the gradient is equal to zero"。
- **KKT**（〈Nonlinear case〉）只提到 "They provide necessary conditions for identifying local optima"，**沒有寫出 complementary slackness**。
- **SVM**（〈Applications〉）只有一句，分兩段引用："formulating the primal problem of SVMs as the dual problem can be used to implement the Kernel trick"，後接 "but the latter has higher time complexity in the historical cases."（"the latter" 指涉不明確，較可能指 dual／kernel trick 形式；原文未附來源）

### 本頁未提及
- ½‖β‖² 代入後出現負號的計算、SVM 的 C、p 與 n 哪個小時該用 primal 或 dual、complementary slackness 的具體式子：本頁皆未提及。

## 與下列問題的關聯（只寫有關的題號）
- 第 5 題（核心：weak/strong duality、Slater、乘數 λ ≥ 0 的慣例與「可為 0」的理由、Wolfe dual 的「梯度為 0 再代回」）
- 第 6 題（間接：本頁的乘數是由限制產生的 dual 變數，與目標函數中使用者設定的係數不同。本頁沒有談 C，「C 不是 Lagrange multiplier」是推論）
- 第 1 題（極間接：只有 Applications 那一句提到 kernel trick 與時間複雜度，沒有談 p>n）
