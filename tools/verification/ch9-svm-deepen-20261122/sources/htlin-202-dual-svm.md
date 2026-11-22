# 林軒田《機器學習技法》Lecture 2: Dual Support Vector Machine（handout）
- URL: https://www.csie.ntu.edu.tw/~htlin/mooc/doc/202_handout.pdf
- 講義頁: p.17（林軒田 Dual SVM handout 連結）
- 抓取狀態: OK（curl，HTTP 200，application/pdf，592,436 bytes；`pdftotext -layout` 轉文字；公式頁 p.5、p.6、p.11–13 另以 `pdftoppm` 渲染成圖核對）
- 讀取日期: 2026-11-22

頁碼慣例：「PDF p.X」為 PDF 實體頁；括號內為投影片頁尾編號（如 5/23）。Fun Time 題目與解答各佔一個 PDF 頁、頁尾編號相同。
記號對照：本講義 N = 樣本數、d̃ = 轉換後特徵維度、zₙ = Φ(xₙ)、(b, w)；source_brief 問題所用記號為 n、p、xᵢ、(β₀, β)。所問的「p+1 個變數、n 個限制式」即本講義的「d̃ + 1 variables and N constraints」。
公式轉寫：PDF p.5、p.6、p.11–13 依渲染圖；其餘依 `pdftotext -layout` 版面轉寫。英文引句只取自文字條列。

## 重點（中文撰寫，術語保留原文）

### 動機：primal 與 dual 的變數／限制式數目
- Primal hard-margin SVM：min ½wᵀw s.t. yₙ(wᵀzₙ + b) ≥ 1；「QP with d̃ + 1 variables and N constraints」，並註明「challenging if d̃ large, or infinite?!」（PDF p.3，2/23）。
- 「‘Equivalent’ SVM」：「(convex) QP of N variables, N + 1 constraints」，對比原 SVM「d̃ + 1 variables, N constraints」（PDF p.4，3/23）。dual 的 N+1 個限制式＝N 個 αₙ ≥ 0 加 1 個等式 Σyₙαₙ = 0（PDF p.16，13/23：「(convex) QP of N variables & N + 1 constraints, as promised」）。
- 總結頁（PDF p.24，20/23）並列兩形式：primal「d̃ + 1 variables, N constraints —suitable when d̃ + 1 small」；dual「N variables, N + 1 simple constraints —suitable when N small」。primal 的物理意義「locate specially-scaled (b, w)」，dual 為「locate SVs (zₙ, yₙ) & their αₙ」；「both eventually result in optimal (b, w) for fattest hyperplane」。
- 但 dual 並非真的完全不依賴 d̃：q_{n,m} = yₙyₘzₙᵀzₘ 是「inner product in R^d̃ —O(d̃) via naïve computation!」，要靠下一講的 kernel 避免（PDF p.25，21/23）。
- 實務記憶體：「if N = 30, 000, dense Q_D (N by N symmetric) takes > 3G RAM」，所以需要不存整個 Q_D 的特殊 solver（PDF p.18，15/23）。

### Lagrange multiplier：λ 與 C 的類比（PDF p.5，4/23）
- 先用正則化回顧：min E_in(w) s.t. wᵀw ≤ C 等價於 min E_in(w) + (λ/N)wᵀw，「C equivalent to some λ ≥ 0 by checking optimality condition」（最佳性條件轉寫：∇E_in(w) + (2λ/N)w = 0）。
- 「regularization: view λ as given parameter instead of C」；「dual SVM: view λ’s as unknown given the constraints, and solve them as variables instead」；乘數個數「N—one per constraint」。
- 注意：此頁的 C 是「wᵀw ≤ C」的**預算**，與 soft-margin 的懲罰權重 C 不同（見 htlin-205 筆記 PDF p.6 用兩種顏色區分兩個 C）。

### 為何乘數必須 ≥ 0（PDF p.6，5/23；已看渲染圖）
- Lagrange function（轉寫）：L(b, w, α) = ½wᵀw + Σₙ αₙ(1 − yₙ(wᵀzₙ + b))。投影片原先寫「Lagrange multipliers λₙ」再刪去改成 αₙ。
- Claim（轉寫）：SVM ≡ min_{b,w} ( max_{all αₙ ≥ 0} L(b, w, α) ) = min_{b,w} (∞ if violate；½wᵀw if feasible)。
  - 違反限制的 (b, w)：某個 (1 − yₙ(...)) > 0，「max(□ + Σₙ αₙ(some positive)) → ∞」。
  - 可行的 (b, w)：所有 (1 − yₙ(...)) ≤ 0，「max(□ + Σₙ αₙ(all non-positive)) = □」（最大值取 αₙ = 0）。
  - 「constraints now hidden in max」。
- 推論（本筆記整理，非原文字句）：正是因為 αₙ 只能 ≥ 0，「乘上非正數」的最大值才會是 0、乘上正數才會趨於 ∞；若 αₙ 可為負，可行點也會被推到 ∞，這個等價就失效。限制是 **≥ 0（不是 > 0）**：αₙ = 0 是允許且常見的（非支持向量）。

### min–max 交換（weak / strong duality）（PDF p.9–10，7/23–8/23）
- 對任意固定 α′ ≥ 0：min max L ≥ min L(b, w, α′)，「because max ≥ any」；取最好的 α′ 得 min max L ≥ max min L，右邊即「Lagrange dual problem」（PDF p.9）。
- 「‘≥’: weak duality」；「‘=’: strong duality, true for QP if」convex primal、feasible primal（true if Φ-separable）、linear constraints，「—called constraint qualification」（PDF p.10）。

### 代入 w = Σαyz 後 −½‖w‖² 的由來（PDF p.11–12，9/23–10/23；已看渲染圖）
- 對 b 微分：∂L/∂b = 0 = −Σₙ αₙyₙ，加入限制 Σ αₙyₙ = 0 後含 b 的項被消掉（「but wait, b can be removed」，PDF p.11）。
- 對 wᵢ 微分：∂L/∂wᵢ = 0 = wᵢ − Σₙ αₙyₙzₙ,ᵢ，於是 w = Σ αₙyₙzₙ（PDF p.12）。
- 投影片轉寫：代入後 ½wᵀw + Σαₙ(1 − yₙwᵀzₙ) 變成 ½wᵀw + Σαₙ − wᵀw，再寫成 −½‖Σₙ αₙyₙzₙ‖² + Σₙ αₙ（PDF p.12）。
- 推論（本筆記補一行代數）：Σₙ αₙyₙwᵀzₙ = wᵀ(Σₙ αₙyₙzₙ) = wᵀw，所以 ½wᵀw − wᵀw = −½wᵀw；負號來自「原本的 ½‖w‖²」與「乘數項貢獻的 −‖w‖²」相加。
- 改寫成 min 形式（PDF p.16，13/23）：min_α ½ΣΣ αₙαₘyₙyₘzₙᵀzₘ − Σαₙ s.t. Σyₙαₙ = 0、αₙ ≥ 0。

### KKT 條件（PDF p.13，11/23；PDF p.19，16/23）
- primal feasible：yₙ(wᵀzₙ + b) ≥ 1；dual feasible：αₙ ≥ 0；dual-inner optimal：Σyₙαₙ = 0、w = Σαₙyₙzₙ；primal-inner optimal：αₙ(1 − yₙ(wᵀzₙ + b)) = 0（complementary slackness）。
- 原文：「called Karush-Kuhn-Tucker (KKT) conditions, necessary for optimality [& sufficient here]」。
- 求 b：「a range from primal feasible & equality from comp. slackness if one αₙ > 0 ⇒ b = yₙ − wᵀzₙ」；「αₙ > 0 ⇒ on fat boundary (SV!)」（PDF p.19）。

### 支持向量（PDF p.22–23，18/23–19/23）
- 「call αₙ > 0 examples (zₙ, yₙ) support vectors」；「SV (positive αₙ) ⊆ SV candidates (on boundary)」——落在邊界上但 αₙ = 0 的點存在，只是「候選」。
- 「only SV needed to compute w」、「only SV needed to compute b」（PDF p.22）。
- Fun Time（PDF p.26–27，22/23）：「# SVs ≤ # SV candidates ≤ N」。
- w 是 yₙzₙ 的線性組合：「also true for GD/SGD-based LogReg/LinReg when w₀ = 0」；「SVM: represent w by SVs only」（PDF p.23，19/23）。

## 與下列問題的關聯
- Q1：dual 的大小只依 N（d̃ 只經內積進來）；w、b 只需 SV（PDF p.22–24）。原文未直接討論 p > n 或與 KNN／LR 的效率比較。
- Q5：primal「suitable when d̃ + 1 small」、dual「suitable when N small」（PDF p.24）；−½‖w‖² 的推導（PDF p.12）；乘數條件是 αₙ ≥ 0（PDF p.6、p.13），αₙ > 0 只用來定義 SV。
- Q6：PDF p.5 的 λ ↔ C（此 C 為預算）是「把限制換成乘數」的直覺，但不是 soft-margin C 的身分說明。
- Q10：SV 必在 fat boundary 上（hard-margin）；SV ⊆ SV candidates（PDF p.22）。
