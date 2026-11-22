# CS229 Lecture Notes, Part V Kernel Methods ＋ Part VI Support Vector Machines（Andrew Ng，Tengyu Ma 2019 更新版）
- URL: https://cs229.stanford.edu/notes2021fall/cs229-notes3.pdf
- 講義頁: p.25、p.36（錨文字未提供；本 subagent 未開講義）
- 抓取狀態: OK（curl，HTTP 200，application/pdf，231,832 bytes，30 頁；`pdftotext -layout` 轉文字；p.8、p.25 另以 `pdftoppm` 渲染核對公式）
- 讀取日期: 2026-11-22

頁碼說明：本 PDF 的 PDF 頁碼＝印刷頁碼。式號沿用原文 (1)–(34)。檔案內容其實是 **Part V Kernel Methods（§1，p.1–11）＋ Part VI SVM（§2–9，p.11–30）**；與 `notes2022fall/main_notes.pdf` 第 5、6 章文字幾乎逐字相同（見 `cs229-main-notes-ch5-6.md`）。

## 重點（中文撰寫，術語保留原文）

### 函數間隔、幾何間隔與縮放不變性（§4，p.13–15）
- 標籤改用 y∈{−1,1}，分類器 h_{w,b}(x)=g(wᵀx+b)，g 只看正負號；直接輸出 ±1，不先估 p(y=1)（§3，p.13）。
- functional margin：γ̂⁽ⁱ⁾ = y⁽ⁱ⁾(wᵀx⁽ⁱ⁾+b)；「a large functional margin represents a confident and a correct prediction」（p.13）。
- 縮放問題：把 (w,b) 換成 (2w,2b) 不改變 h_{w,b}，但 functional margin 變 2 倍——「we can make the functional margin arbitrarily large without really changing anything meaningful」（p.14）。因此提出正規化如 ‖w‖₂=1。
- 資料集的 functional margin 定義為各點最小值 γ̂ = minᵢ γ̂⁽ⁱ⁾（p.14）。
- geometric margin 推導：w 與超平面正交；點 A=x⁽ⁱ⁾ 沿 w/‖w‖ 方向退 γ⁽ⁱ⁾ 到邊界點 B=x⁽ⁱ⁾−γ⁽ⁱ⁾w/‖w‖，代入 wᵀx+b=0 得 γ⁽ⁱ⁾=(w/‖w‖)ᵀx⁽ⁱ⁾+b/‖w‖；一般式乘上 y⁽ⁱ⁾（p.14–15）。（推論／非原文：此即點到超平面距離，可視為 x 在單位法向量 w/‖w‖ 上的 scalar projection 加上 b/‖w‖。）
- 兩者關係與不變性：「if ||w|| = 1, then the functional margin equals the geometric margin」；「the geometric margin is invariant to rescaling of the parameters」（p.15）。
- 關鍵句（Q4）：因縮放不變，「we can impose an arbitrary scaling constraint on w without changing anything important」，例如 ‖w‖=1、|w₁|=5 或 |w₁+b|+|w₂|=2 皆可靠重新縮放 w、b 達成（p.15）。

### 最佳間隔分類器的三步改寫（§5，p.16–17）——對應講義 p.15 的 M=1/‖β‖
1. 原始問題：max_{γ,w,b} γ s.t. y⁽ⁱ⁾(wᵀx⁽ⁱ⁾+b) ≥ γ，‖w‖=1（p.16）。‖w‖=1 讓 functional＝geometric margin。缺點：「the "||w|| = 1" constraint is a nasty (non-convex) one」（p.16）。
2. 第二式：max_{γ̂,w,b} γ̂/‖w‖ s.t. y⁽ⁱ⁾(wᵀx⁽ⁱ⁾+b) ≥ γ̂（p.16）。因 γ=γ̂/‖w‖，去掉了 ‖w‖=1，但目標函數仍非凸。
3. 第三式：加入縮放約束「the functional margin of w, b with respect to the training set must be 1」，即 γ̂=1；「this is indeed a scaling constraint, and can be satisfied by rescaling w, b」（p.17）。最大化 γ̂/‖w‖=1/‖w‖ 等價於 min ½‖w‖² s.t. y⁽ⁱ⁾(wᵀx⁽ⁱ⁾+b) ≥ 1。「convex quadratic objective and only linear constraints」，可用 QP 求解（p.17）。
- 對 Q4 的意義：被固定的是 (w,b) 的「尺度」這個自由度，不是邊界本身；同一條超平面有無窮多組 (w,b) 表示，γ̂=1 只是從中挑一組代表。注意：此段只處理可分情形，未談 slack 在縮放下的行為。

### Lagrange duality（§6，p.17–20，標「optional reading」）
- primal：min f(w) s.t. gᵢ(w) ≤ 0（i=1..k）、hᵢ(w)=0（i=1..l）；generalized Lagrangian L(w,α,β)=f+Σαᵢgᵢ+Σβᵢhᵢ（p.18）。
- θ_P(w)=max_{α,β: αᵢ≥0} L；違反約束時為 ∞（式 13–14），否則等於 f(w)，所以 min_w θ_P 就是原問題（p.18–19）。**αᵢ ≥ 0 是不等式約束乘數的定義域**（式 13 下標「α,β : αᵢ ≥ 0」）；等式約束的 βᵢ 不限號。
- dual：max_{α,β: αᵢ≥0} min_w L；weak duality d* ≤ p*（「max min ... always being less than or equal to the "min max."」，p.19）。
- 強對偶條件：f、gᵢ 凸、hᵢ affine、gᵢ strictly feasible ⇒ 存在 w*,α*,β* 使 p*=d*=L(w*,α*,β*)，且滿足 KKT（式 15–19，p.20）：梯度為零、αᵢ*gᵢ(w*)=0（式 17，dual complementarity）、gᵢ(w*) ≤ 0、αᵢ* ≥ 0（式 19）。
- 式 17 的含義：「if αᵢ* > 0, then gᵢ(w*) = 0」（p.20）——這是「支持向量很少」的來源。**註：KKT 只要求 ≥0；>0 只出現在「若 αᵢ>0 則約束為 active」的蘊涵中，不是要求。**
- 註腳 7（p.20）：affine「means the same thing as linear, except that we also allow the extra intercept term bᵢ」（可用於 Q2 flat/affine 用語）。

### SVM 的對偶形式（§7，p.20–24）
- 約束寫成 gᵢ(w) = −y⁽ⁱ⁾(wᵀx⁽ⁱ⁾+b)+1 ≤ 0；由 KKT，「αᵢ > 0 only for the training examples that have functional margin exactly equal to one」（p.21），這些點稱 support vectors；「the number of support vectors can be much smaller than the size the training set」（p.21）。
- Lagrangian（式 21，p.22）：L(w,b,α)=½‖w‖² − Σαᵢ[y⁽ⁱ⁾(wᵀx⁽ⁱ⁾+b)−1]。只有 α 沒有 β，因為只有不等式約束。**負號來源**：約束是 gᵢ = −(…−1)，所以 +αᵢgᵢ 展開成 −αᵢ[…]（Q5）。
- ∇_w L=0 ⇒ w=Σαᵢy⁽ⁱ⁾x⁽ⁱ⁾（式 22）；∂L/∂b=0 ⇒ Σαᵢy⁽ⁱ⁾=0（式 23）（p.22）。
- 代回後：L = Σαᵢ − ½Σᵢⱼ y⁽ⁱ⁾y⁽ʲ⁾αᵢαⱼ(x⁽ⁱ⁾)ᵀx⁽ʲ⁾ − bΣαᵢy⁽ⁱ⁾，最後一項由式 23 為 0（p.22）。原文只說「plug that back into the Lagrangian ... and simplify」。（推論／非原文：½‖w‖² 代入得 +½ΣΣ，−Σαᵢyᵢwᵀxᵢ 代入得 −ΣΣ，合併為 −½ΣΣ。）
- dual（式 24，p.23）：max_α W(α)=Σαᵢ − ½Σ y⁽ⁱ⁾y⁽ʲ⁾αᵢαⱼ⟨x⁽ⁱ⁾,x⁽ʲ⁾⟩ s.t. αᵢ ≥ 0、Σαᵢy⁽ⁱ⁾=0。
- 截距（式 25）：b* = −[max_{i:y=−1} w*ᵀx⁽ⁱ⁾ + min_{i:y=1} w*ᵀx⁽ⁱ⁾]/2（p.23；soft-margin 時不再成立，p.25）。
- 預測（式 26–27，p.23–24）：wᵀx+b = Σαᵢy⁽ⁱ⁾⟨x⁽ⁱ⁾,x⟩+b；αᵢ 除支持向量外皆為 0，「we really need to find only the inner products between x and the support vectors」（p.24）（Q1 記憶體／預測成本）。
- **原文沒有**「p 小用 primal、n 小用 dual」的說法；notes3 只說 dual 讓我們能套 kernel，並能導出比通用 QP 更有效率的演算法（p.17、p.24）。

### Regularization 與不可分情形（§8，p.24–26，optional）
- 動機：資料可能不可分；且 hard margin 對 outlier 敏感，單一 outlier 讓邊界「make a dramatic swing」（p.24）。
- primal（「using ℓ1 regularization」，p.24–25）：min ½‖w‖² + CΣξᵢ s.t. y⁽ⁱ⁾(wᵀx⁽ⁱ⁾+b) ≥ 1−ξᵢ、ξᵢ ≥ 0。（原文下標寫 min_{γ,w,b}，γ 為筆誤殘留。）
- C 的角色：「C controls the relative weighting between the twin goals」：讓 ‖w‖² 小（margin 大）與「ensuring that most examples have functional margin at least 1」（p.25）。
- Lagrangian：L(w,b,ξ,α,r)=½wᵀw + CΣξᵢ − Σαᵢ[y⁽ⁱ⁾(xᵀw+b)−1+ξᵢ] − Σrᵢξᵢ；「the αᵢ's and rᵢ's are our Lagrange multipliers (constrained to be ≥ 0)」（p.25）。**故 C 是事先給定的權重，不是 Lagrange multiplier；乘數是 αᵢ、rᵢ**（Q6）。
- dual：同式 24，但約束變 0 ≤ αᵢ ≤ C；「the only change to the dual problem is that ... 0 ≤ αᵢ has now become 0 ≤ αᵢ ≤ C」（p.25）。
- KKT（式 28–30，p.26）：αᵢ=0 ⇒ yᵢf ≥ 1；αᵢ=C ⇒ yᵢf ≤ 1；0<αᵢ<C ⇒ yᵢf = 1（方向是由 α 推 margin）。（推論／非原文，取逆否：yᵢf>1 ⇒ αᵢ=0；yᵢf<1 ⇒ αᵢ=C；恰在 margin 上 yᵢf=1 的點 αᵢ 可為 [0,C] 中任何值。）
- 未見：此節沒有討論「預算（ISLR 的 C）夠大時是否必有可行解」；CS229 的 soft-margin 用懲罰式，ξᵢ 無上限，所以永遠可行（此為推論，原文未明寫）。

### SMO（§9，p.26–30，optional）
- 因 Σαᵢy⁽ⁱ⁾=0，不能只動一個 α，至少同時動兩個（p.28）；收斂以 KKT（式 28–30）在 tol 內檢查，tol 約 0.01–0.001（p.28）。

### Kernel methods（Part V §1，p.1–11）
- feature map φ、attributes vs features（§1.1，p.1–2）。
- LMS with features：θ := θ + αΣ(y⁽ⁱ⁾−θᵀφ(x⁽ⁱ⁾))φ(x⁽ⁱ⁾)（式 3，p.2）。
- **kernel trick 用在線性迴歸（LMS 梯度下降）**（§1.3，p.2–6）：設 θ 初值為 0，歸納證明「at any time, θ can be represented as a linear combination of the vectors φ(x⁽¹⁾), ..., φ(x⁽ⁿ⁾)」（p.3），θ=Σβᵢφ(x⁽ⁱ⁾)（式 6）；更新 βᵢ := βᵢ + α(y⁽ⁱ⁾ − Σⱼβⱼ K(x⁽ⁱ⁾,x⁽ʲ⁾))（式 11），向量式 β := β + α(y − Kβ)（p.5）；預測 θᵀφ(x)=ΣβᵢK(x⁽ⁱ⁾,x)（式 12，p.6）。每次更新 O(n)。
  - **只做梯度下降版**；全文未出現 normal equation、kernel ridge regression、kernel PCA、kernel logistic regression 的推導。
- degree ≤3 單項式的例子：維度 1+d+d²+d³（含重複，註 1，p.3），d=1000 時約 10⁹ 維；⟨φ(x),φ(z)⟩ = 1+⟨x,z⟩+⟨x,z⟩²+⟨x,z⟩³（式 9，p.5），O(d) 可算。
- K(x,z)=(xᵀz)²：對應 φ(x)=(xᵢxⱼ)_{i,j}，φ 需 O(d²) 但 K 只需 O(d)（p.6–7）。
- K(x,z)=(xᵀz+c)²：多出 √(2c)xᵢ 與 c 兩類分量，「the parameter c controls the relative weighting between the xᵢ (first order) and the xᵢxⱼ (second order) terms」（p.8）。
- **多項式核特徵數**（p.8，已渲染核對）：「the kernel K(x,z)=(xᵀz+c)^k corresponds to a feature mapping to an (d+k choose k) feature space」，即所有「up to order k」的單項式；在 O(d^k) 維空間但 K 仍只需 O(d)。**符號對照：CS229 用 d＝輸入維度、k＝次方；sklearn 用 degree＝d。**
- Gaussian kernel：K(x,z)=exp(−‖x−z‖²/(2σ²))，「close to 1 when x and z are close, and near 0 when ... far apart」（p.8）；「corresponds to an infinite dimensional feature mapping φ」（p.9）。**原文只陳述無窮維，未給出展開證明，也沒有談 γ（或 σ）大小的意義**（Q9）。
- kernels as similarity metrics（p.8），作者自註「there are things wrong with this intuition, but nevermind」。
- 必要條件（p.9）：對任意有限點集（「not necessarily the training set」），kernel matrix K 對稱且 zᵀKz=Σ_k(Σᵢzᵢφ_k(x⁽ⁱ⁾))² ≥ 0，故 PSD。
- **Mercer 定理（p.10，原文表述，節錄）**：K: ℝᵈ×ℝᵈ→ℝ 為 valid (Mercer) kernel，「it is necessary and sufficient that for any {x⁽¹⁾, …, x⁽ⁿ⁾}, (n < ∞), the corresponding kernel matrix is symmetric positive semi-definite」。前一段（p.10 開頭）也說此條件「not only a necessary, but also a sufficient, condition」。註 3：許多教科書用 L² 函數的較複雜形式，「when the input attributes take values in ℝᵈ, the version given here is equivalent」。
- 其他例：16×16 手寫數字用 polynomial 或 Gaussian kernel 表現極好；字串 k-gram kernel 26^k 維可用動態規劃算（p.10）。
- 一般化（p.11）：「if you have any learning algorithm that you can write in terms of only inner products ⟨x, z⟩ … replacing this with K(x, z)」即可在高維特徵空間運作；例：kernel perceptron（Q8）。

## 與下列問題的關聯（只寫有關的題號）
- Q1：p.21、p.23–24（只需與支持向量的內積；支持向量數可遠小於 n）。未提 p>n。
- Q2：p.20 註 7（affine＝linear＋截距）。
- Q3：p.14–15（geometric margin 推導，沿單位法向量投影）。
- Q4：p.13–17（縮放不變、γ̂=1、三步改寫）。
- Q5：p.18–23（αᵢ ≥ 0、KKT、式 21 的負號、代入得 −½）。
- Q6：p.25（C 是權重；乘數是 αᵢ、rᵢ）。
- Q7：p.24–25（soft margin 動機；可行性未明寫）。
- Q8：p.2–6、p.11（LMS 梯度下降的 kernel 化、kernel perceptron；無 kernel ridge／PCA）。
- Q9：p.8–10（Gaussian kernel 無窮維、Mercer 定理原文）。
- Q10：p.21、p.26（αᵢ>0 的點；式 28–30）。
- Q13：p.26–30（SMO）。
