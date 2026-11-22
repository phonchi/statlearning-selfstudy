# Kernels and Feature maps: Theory and intuition（Xavier Bourret Sicotte, Data Blog, 2018-06-28）
- URL: https://xavierbourretsicotte.github.io/Kernel_feature_map.html
- 講義頁: p.24（Kernel feature map 部落格連結）
- 抓取狀態: OK（curl，HTTP 200，text/html，444,747 bytes；以 Python 去標籤轉文字閱讀全文。**頁內圖片（標為 [IMG]）未檢視**，以下不描述圖的內容）
- 讀取日期: 2026-11-22

記號對照：原文 **n = 輸入維度、m = 樣本數**（課程講義為 p 與 n）；φ = feature map；G = Gram matrix（m×m）。
英文引句為原文逐字（含原文拼字）；數學式為本筆記轉寫自原文 LaTeX。

## 重點（中文撰寫，術語保留原文）

### Kernel 定義與二次映射例子（小節 “Kernels: definition and example”）
- 定義 K(x, z) = φ(x)ᵀφ(z)；「the kernel may be very inexpensive to calculate, and may correspond to a mapping in very high dimensional space」。
- 例：K(x, z) = (xᵀz)²，展開為 Σ_{i,j}(xᵢxⱼ)(zᵢzⱼ)；n = 2 時原文給的 φ(x) = (x₁x₁, x₁x₂, x₂x₁, x₂x₂)，**四個分量，含重複的 x₁x₂ 與 x₂x₁**。
- 「Calculating the feature mapping is of complexity O(n²) due to the number of features, whereas calculating K(x,z) is of complexity O(n)」。

### 帶常數的多項式 kernel 與維度敘述
- 原文：K(x, z) = (xᵀz + c)² = Σ_{i,j}(xᵢxⱼ)(zᵢzⱼ) + Σᵢ(√(2c)xᵢ)(√(2c)xᵢ) + c²，對應 φ(x) = (x₁x₁, x₁x₂, x₂x₁, x₂x₂, √(2c)x₁, √(2c)x₂)。
- 「so the parameter c controls the relative weighting of the first and second order polynomials」。
- 維度：原文說 (xᵀz + c)ᵈ 對應到維度為 C(n+d, d)（原文 LaTeX `\binom{n + d}{d}`，此為轉寫）的特徵空間，「corresponding to all monomials that are up to order d」；並說「Despite working in this O(n^d) dimensional space」，「computing K(x,z) is of order O(n)」。
- 本筆記核算（非原文）：n = 2、d = 2 時 C(4, 2) = 6，對應不重複單項式 {1, x₁, x₂, x₁², x₁x₂, x₂²}。這與原文 6 分量的 φ（含重複 x₁x₂/x₂x₁、缺常數項）數目巧合相同，但內容不同。

### 第二個二次映射（小節 “A visual example to help intuition” 與 “Feature map n. 3”）
- 映射 z₁ = √2·x₁x₂、z₂ = x₁²、z₃ = x₂²，對應 K(x, x′) = (xᵀx′)² 在 n = 2、d = 2 的情形；φ(x) = (√2x₁x₂, x₁², x₂²)，**三個分量（把 x₁x₂ 與 x₂x₁ 合併成 √2x₁x₂）**。
- 流程：「Map the original features to the higher, transformer space」、「Perform linear SVM in this higher space」、「Map this hyperplane back into the original 2D space to obtain a non linear decision boundary」。
- 程式例：make_circles 資料，三種 feature map 以自訂 kernel 給 sklearn SVC，訓練準確率皆印出 1.0。

### Mercer 條件、Gram matrix（小節 “Necessary and sufficient conditions”、“Gram Matrix vs Feature Map”）
- 「the kernel matrix G is symmetric, positive semi-definite」；「This is both a necessary and sufficient condition … and is called Mercer's theorem.」
- 「feature maps may require infinite dimensional space (e.g. Gaussian Kernel) which requires approximation」。
- Gram matrix 為 transformed space 的外積：G = X̃X̃ᵀ（小節 “From Feature Maps to Kernels”）。
- 取捨：「the Gram matrix may be impossible to hold in memory for large m」；經驗法則「When the number of examples is very large, feature maps are better」、「When transformed features have high dimensionality, Grams matrices are better」。
- Gaussian kernel：「the value is close to 1 when they are similar and close to 0 when they are not」；isotropic RBF「σ² is known as the bandwidth parameter」。

### 原文疑誤（本筆記核對，非原文所述）
1. 小節 “Polynomial kernel” 與 “Feature map n. 3” 的展開第一行寫成 (x₁x₂′ + x₂x₂′)²，應為 (x₁x₁′ + x₂x₂′)²（下一行的展開結果是對的）。
2. (xᵀz + c)² 的展開中，一次項寫成 (√(2c)xᵢ)(√(2c)xᵢ)，第二個因子應為 zᵢ；且列出的 φ(x) **缺少常數分量 c**（c² 項需要 φ 中有一個常數 c 分量才能由內積產生）。
3. “Common Kernels” 中 “Cosine” 的公式與 “Laplace” 完全相同（exp(−β|x − y|)），應為複製錯誤。
4. 一般 Gaussian kernel 寫成 exp(−½(x − x′)ᵀΣ(x − x′))；與其後對角情形 1/σⱼ² 的寫法比對，矩陣應為 Σ⁻¹（本筆記判斷）。
5. 4 分量（含重複）的 φ 與 3 分量（√2 合併）的 φ 給出相同的 kernel 值，但維度不同；而 C(n+d, d) 計數的是不重複單項式。三者不要混為一談。

## 與下列問題的關聯
- Q8：Gram matrix G = X̃X̃ᵀ（樣本×樣本）與 feature map 的取捨；可作為 dual／kernel 形式依賴 XXᵀ 的佐證。原文未談 PCA 或 ridge。
- Q9：Mercer’s theorem 的敘述（Gram matrix 對稱半正定為充要條件）；Gaussian kernel 對應無窮維、需近似。原文未討論 γ 大小的效果。
- Q5、Q1（間接）：樣本數極大時用 feature map（primal 類），轉換後維度很高時用 Gram matrix（dual 類）。
