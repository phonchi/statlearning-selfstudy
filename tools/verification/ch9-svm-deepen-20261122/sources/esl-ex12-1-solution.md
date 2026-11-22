# A Solution Manual for ESL — Ex. 12.1（Yuhang Zhou）
- URL: https://yuhangzhou88.github.io/ESL_Solution/ESL-Solution/_12-Flexible-Discriminants/ex12-01/
- 講義頁: p.30（ESL 習題 12.1 解答連結）
- 抓取狀態: OK（curl，HTTP 200，text/html，76,082 bytes；去標籤後閱讀 MathJax 原始 LaTeX）
- 讀取日期: 2026-11-22

此頁沒有頁碼或式號，以下以頁內問題名稱 P₁、P₂′、P₂ 指稱。頁面只寫「Show that the criteria (12.25) and (12.8) are equivalent.」，**沒有重述 ESL 式 (12.25) 原文**；本筆記不憑記憶補 ESL 原式，只轉寫此頁自己的式子。
記號：β, β₀ = 係數；f(xᵢ) = βᵀxᵢ + β₀；ξᵢ, ηᵢ = slack；[·]₊ = max(·, 0)。

## 重點（中文撰寫，術語保留原文）
- P₁（此頁對 ESL (12.8) 的寫法，轉寫）：min_{β,β₀} ½‖β‖² + CΣξᵢ s.t. ξᵢ ≥ 0、ξᵢ ≥ 1 − yᵢf(xᵢ)。
- P₂′（此頁對 ESL (12.25) 的寫法）：「with λ = 1/C」，min (1/C)[½‖β‖² + CΣηᵢ] s.t. ηᵢ = [1 − yᵢf(xᵢ)]₊。
- 本筆記代數（非原文）：P₂′ 的目標展開為 Σηᵢ + (1/(2C))‖β‖²，也就是 hinge loss 總和加上 (λ/2)‖β‖²、λ = 1/C 的形式。
- 「The objective functions for both problems are the same, up to constant 1/C.」——乘上正常數不改變最小解，故改寫為 P₂：min ½‖β‖² + CΣηᵢ s.t. ηᵢ = [1 − yᵢf(xᵢ)]₊。
- 方向一：P₂ 的最佳解滿足 P₁ 的限制，因為 η̂ᵢ = [1 − yᵢf̂(xᵢ)]₊ ≥ 0 且 ≥ 1 − yᵢf̂(xᵢ)；所以 P₂ 的最佳值 ≥ P₁ 的最佳值。
- 方向二：引用「(12.10) - (12.16) in the text」（ESL 的 KKT 條件）論證：若 ξ̂ᵢ > 1 − yᵢf̂(xᵢ)，則 α̂ᵢ = 0（引 (12.14)），「and C − μᵢ = 0 by (12.12)」，該點不是 support vector；因而「the focus is on ξ̂ᵢ = 1 − yᵢf̂(xᵢ) = [1 − yᵢf̂(xᵢ)]₊ = η̂ᵢ」。結論「the two problems have the same solution」。
- 本筆記評註（非原文）：方向二的寫法較簡略（依賴 ESL 的 KKT 式號，此頁未列出原式）。另一個更直接、不需 KKT 的論證是：P₁ 的目標對每個 ξᵢ 單調遞增（C > 0），最佳時 ξᵢ 必取下界 max(0, 1 − yᵢf(xᵢ)) = [1 − yᵢf(xᵢ)]₊，P₁ 因此化為 P₂。
- λ 與 C 的關係：此頁只給 **λ = 1/C**（對應「(λ/2)‖β‖²」的寫法）。對照：林軒田 Lecture 5 用「(λ/N)wᵀw」寫法，得到 C ↔ 1/(2λ)（見 htlin-205 筆記 PDF p.8）。兩者差別只在正則項前的係數慣例（½ 與 1/N），本質都是 C 與 λ 成反比。
- 此頁**沒有**討論預算形式（Σξ ≤ const）或 const 與 C 的關係，也沒有討論 hinge 轉折點為何在 1、logistic loss 的兩種寫法。

## 與下列問題的關聯
- Q11：hinge + ridge 改寫的等價證明，λ = 1/C（此頁慣例）。
- Q6：C 與 λ 成反比（此頁慣例 λ = 1/C）；const（預算）與 C 的關係原文未涵蓋。
