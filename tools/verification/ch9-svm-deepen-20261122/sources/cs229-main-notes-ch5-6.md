# CS229 Lecture Notes（2022 Fall main_notes），Chapter 5 Kernel methods 與 Chapter 6 Support vector machines
- URL: https://cs229.stanford.edu/notes2022fall/main_notes.pdf
- 講義頁: p.36（錨文字未提供；本 subagent 未開講義）
- 抓取狀態: OK（curl，HTTP 200，application/pdf，3,253,492 bytes，216 頁；`pdftotext -layout`）。只讀第 5、6 章（PDF p.50–80；PDF p.81 為 Part II 扉頁）。
- 讀取日期: 2026-11-22

頁碼說明：**本檔 PDF 頁碼＝印刷頁碼＋1**（PDF p.50 頁尾印「49」）。下文一律寫「PDF p.X（印 p.X−1）」。式號用原文 (5.x)、(6.x)。

## 與 cs229-notes3.pdf 的關係（已用文字 diff 核對）
- 我把 notes3 的 Part V 與本檔第 5 章、notes3 的 Part VI 與本檔第 6 章做了空白正規化後的逐字 diff（difflib，比對時去掉式號）：相似度分別約 0.97 與 0.96，差異只有：章節／式號重新編號（§1→5.x、§2–9→6.x；式 (13)–(34)→(6.1)–(6.22)）、6.2、6.3、6.4、6.6 標題加註「(option reading)」（6.5 在 notes3 已標 optional reading）、6.6 標題改為「Optimal margin classifiers: the dual form」、註腳重新編號、刪去 SMO 節「Some details will be left to the homework…」一句，其餘為 pdftotext 排版差異。**沒有新增內容**。因此逐條細節與引文見 `cs229-notes3.md`，以下只列重點與本檔的位置。

## 重點（中文撰寫，術語保留原文）

### 第 5 章 Kernel methods（PDF p.50–60）
- 5.1 Feature maps（PDF p.50）：cubic 例子 φ(x)=(1,x,x²,x³)，θᵀφ(x)（式 5.1）。
- 5.2 LMS with features（PDF p.51）：θ := θ + αΣ(y⁽ⁱ⁾−θᵀφ(x⁽ⁱ⁾))φ(x⁽ⁱ⁾)（式 5.3），SGD 版（式 5.4）。
- **5.3 LMS with the kernel trick（PDF p.51–55）——講義對「kernel trick 用在線性迴歸」的完整說法**：
  - 問題：degree ≤3 單項式特徵約 d³ 維；d=1000 時每次更新要存 10⁹ 維向量（PDF p.52）。
  - 關鍵觀察：「For simplicity, we assume the initialize the value θ = 0」，並歸納證明「at any time, θ can be represented as a linear combination of the vectors φ(x⁽¹⁾), …, φ(x⁽ⁿ⁾)」（PDF p.52）；θ=Σβᵢφ(x⁽ⁱ⁾)（式 5.6）。
  - 係數更新：βᵢ := βᵢ + α(y⁽ⁱ⁾ − Σⱼβⱼ⟨φ(x⁽ʲ⁾),φ(x⁽ⁱ⁾)⟩)（PDF p.53）；兩個要點：可預先算好所有 pairwise 內積，且 ⟨φ(x),φ(z)⟩=1+⟨x,z⟩+⟨x,z⟩²+⟨x,z⟩³（式 5.9，PDF p.54），O(d) 可得。
  - 定義 K(x,z) ≜ ⟨φ(x),φ(z)⟩（式 5.10）；最終演算法 βᵢ := βᵢ + α(y⁽ⁱ⁾ − ΣⱼβⱼK(x⁽ⁱ⁾,x⁽ʲ⁾))（式 5.11），向量式「β := β + α(y⃗ − Kβ)」，每次更新 O(n)（PDF p.54）。
  - 預測：θᵀφ(x)=ΣβᵢK(x⁽ⁱ⁾,x)（式 5.12，PDF p.55）；「all we need to know about the feature map φ(·) is encapsulated in the corresponding kernel function K(·,·)」（PDF p.55）。
  - **確切範圍**：只把「批次梯度下降的 LMS」kernel 化（從 θ=0 出發，以 β 表示 θ）。本章**沒有**寫 normal equation／closed form、kernel ridge regression（沒有 (K+λI)⁻¹y）、正則化項、kernel PCA、kernel logistic regression。
- 5.4 Properties of kernels（PDF p.55–60）：(xᵀz)²、(xᵀz+c)²、(xᵀz+c)^k 對應「(d+k choose k)」維、「up to order k」單項式的特徵空間（PDF p.57）；Gaussian kernel exp(−‖x−z‖²/(2σ²))「corresponds to an infinite dimensional feature mapping φ」（PDF p.58）；kernel matrix 必對稱 PSD（PDF p.58）；Mercer 定理：「necessary and sufficient that for any {x⁽¹⁾, …, x⁽ⁿ⁾}, (n < ∞), the corresponding kernel matrix is symmetric positive semi-definite」（PDF p.59）。
- 應用段（PDF p.60）：「We've seen the application of kernels to linear regression」；任何只用內積 ⟨x,z⟩ 寫成的演算法都可替換成 K(x,z)，例：「kernel perceptron algorithm」。

### 第 6 章 Support vector machines（PDF p.61–80）
- 6.1 Margins: intuition（PDF p.61–63）；6.2 Notation（PDF p.63）：y∈{−1,1}、h_{w,b}(x)=g(wᵀx+b)。
- 6.3 Functional and geometric margins（PDF p.63–65）：functional margin 會因 (w,b)→(2w,2b) 加倍；geometric margin「invariant to rescaling」，所以「we can impose an arbitrary scaling constraint on w without changing anything important」（PDF p.65）。
- 6.4 The optimal margin classifier（PDF p.65–67）：‖w‖=1 版（非凸約束）→ max γ̂/‖w‖（非凸目標）→ 令 γ̂=1，「this is indeed a scaling constraint, and can be satisfied by rescaling w, b」，得 min ½‖w‖² s.t. y⁽ⁱ⁾(wᵀx⁽ⁱ⁾+b) ≥ 1（PDF p.66–67）。
- 6.5 Lagrange duality（PDF p.67–70）：θ_P(w)=max_{α,β: αᵢ≥0} L（式 6.1–6.2）；d* ≤ p*；強對偶下 KKT 式 6.3–6.7（PDF p.70），其中 αᵢ*gᵢ(w*)=0（式 6.5）、αᵢ* ≥ 0（式 6.7）。
- 6.6 The dual form（PDF p.70–73）：L(w,b,α)=½‖w‖² − Σαᵢ[y⁽ⁱ⁾(wᵀx⁽ⁱ⁾+b)−1]（式 6.9）；w=Σαᵢy⁽ⁱ⁾x⁽ⁱ⁾（式 6.10）；Σαᵢy⁽ⁱ⁾=0（式 6.11）；dual（式 6.12）：max Σαᵢ − ½Σy⁽ⁱ⁾y⁽ʲ⁾αᵢαⱼ⟨x⁽ⁱ⁾,x⁽ʲ⁾⟩，αᵢ ≥ 0；預測只需與支持向量的內積（式 6.14–6.15，PDF p.73）。
- 6.7 Regularization and the non-separable case（PDF p.74–75）：min ½‖w‖²+CΣξᵢ；αᵢ、rᵢ 為乘數「(constrained to be ≥ 0)」；dual 約束變 0 ≤ αᵢ ≤ C；KKT 式 6.16–6.18（PDF p.75）。
- 6.8 SMO（PDF p.75–80）：coordinate ascent、成對更新 α、clipping 到 [L,H]。
- **第 6 章本身沒有「kernel 化 SVM」的獨立小節**；kernel 只在 6.6 結尾以「write the entire algorithm in terms of only inner products」帶過（PDF p.73），以及第 5 章結尾的總述。

## 與下列問題的關聯（只寫有關的題號）
- Q1：PDF p.71、p.73（支持向量數可遠少於 n；預測只需與支持向量內積）。
- Q3：PDF p.64–65（geometric margin 推導）。
- Q4：PDF p.63–67（縮放不變、γ̂=1）。
- Q5：PDF p.67–73（αᵢ ≥ 0、KKT、dual 推導）。
- Q6：PDF p.74–75（C 是權重，乘數是 αᵢ、rᵢ）。
- Q8：PDF p.51–55、p.60（**kernel trick 用於線性迴歸＝LMS 梯度下降的 β 表示**；無 kernel ridge／PCA）。
- Q9：PDF p.57–59（多項式核維度、Gaussian 無窮維、Mercer）。
- Q10：PDF p.71、p.75（αᵢ>0 的點、KKT 式 6.16–6.18）。
