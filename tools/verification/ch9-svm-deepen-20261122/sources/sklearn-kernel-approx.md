# scikit-learn User Guide 6.7. Kernel Approximation（stable 編號為 8.7）
- URL: https://scikit-learn.org/stable/modules/kernel_approximation.html（講義連結）；實際依網站版本讀 https://scikit-learn.org/1.6/modules/kernel_approximation.html
- 講義頁: p.32（錨文字未提供；本 subagent 未開講義）
- 抓取狀態: OK（curl；1.6 頁 HTTP 200、/stable/（1.9.1）HTTP 200；pandoc 轉純文字，兩版 diff）
- 讀取日期: 2026-11-22

## 重點（中文撰寫，術語保留原文）

### 頁首定位
- 此子模組「approximate the feature mappings that correspond to certain kernels」，產生可供線性分類器使用的非線性轉換。
- 與 kernel trick 的對比：「explicit mappings can be better suited for online learning and can significantly reduce the cost of learning with very large datasets」。
- 「Standard kernelized SVMs do not scale well to large datasets」；但用 approximate kernel map「it is possible to use much more efficient linear SVMs」。
- **與 SGD 的搭配**：「In particular, the combination of kernel map approximations with SGDClassifier can make non-linear learning on large datasets possible.」
- 提醒：因實證研究不多，「it is advisable to compare results against exact kernel methods when possible」。

### Nystroem（6.7.1）
- 「a general method for reduced rank approximations of kernels」，對 kernel 計算的資料列／行「subsampling without replacement」。
- 複雜度：精確法 O(n_samples³)，近似 O(n_components² · n_samples)，n_components ≪ n_samples 時表現下降不大 [WS2001]。
- 推導：K = UΛUᵀ 分塊，未抽樣部分 U₂ΛU₂ᵀ ≈ K₂₁K₁₁⁻¹K₂₁ᵀ = (K₂₁K₁₁^{−½})(K₂₁K₁₁^{−½})ᵀ；fit 時算 K₁₁^{−½}（`normalization_`），transform 時算新資料對 `components_` 的 kernel 再乘上它。
- 預設 rbf kernel，但可用任何 kernel 或 precomputed；`n_components`＝抽樣數＝輸出特徵維度。

### RBFSampler（6.7.2）
- 「The RBFSampler constructs an approximate mapping for the radial basis function kernel, also known as Random Kitchen Sinks [RR2007]」；參考文獻 [RR2007] 為 Rahimi & Recht「Random features for large-scale kernel machines」(2007)。**本頁沒有使用「random Fourier features」這個詞**（Fourier 一詞只出現在 chi² 與 TensorSketch 段）。
- 用法範例：`RBFSampler(gamma=1).fit_transform(X)` 後接 `SGDClassifier`，「prior to applying a linear algorithm, for example a linear SVM」。
- 「The mapping relies on a Monte Carlo approximation to the kernel values」；fit 做抽樣、transform 做映射；結果隨 fit 呼叫而異。
- fit「does not actually depend on the data given to the fit function. Only the dimensionality of the data is used」。
- n_components 越大近似越好，越接近 kernel SVM 的結果。
- 「For a given value of n_components RBFSampler is often less accurate as Nystroem. RBFSampler is cheaper to compute, though」。

### 其他近似（6.7.3–6.7.5）
- AdditiveChi2Sampler（確定性 Fourier 取樣）、SkewedChi2Sampler（Monte Carlo）、PolynomialCountSketch（TensorSketch，近似 (γxᵀy+c₀)^d）：多項式核特徵空間「consists of all possible degree-d products among input features」，可表達特徵交互作用。

### Mathematical Details（6.7.6）（Q8、Q9）
- 開頭：「Kernel methods like support vector machines or kernelized PCA rely on a property of reproducing kernel Hilbert spaces」。
- 「For any positive definite kernel function k (a so called Mercer kernel)」，保證存在映射 φ 到 Hilbert space H 使 k(x,y)=⟨φ(x),φ(y)⟩。**用詞：sklearn 說 positive definite kernel；CS229 說 kernel matrix symmetric positive semi-definite。頁面未說明兩種用語的關係。**（推論／非原文：文獻中「positive definite kernel」常指所有 Gram matrix 皆 PSD，即與 CS229 同一類函數。）
- 若演算法「such as a linear support vector machine or PCA, relies only on the scalar product of data points」，即可改用 k(xᵢ,xⱼ)——明確點名 **PCA**，且前句直接寫「kernelized PCA」。
- 好處：φ 不需明算，「allowing for arbitrary large features (even infinite)」。
- 缺點：需存大量 kernel 值；預測新資料要對許多訓練點算 k(xᵢ, yⱼ)。本模組的近似可「obviates the need to apply the kernel or store training examples」。

### 1.6 與 /stable/ 差異
- 小節號 6.7.x → 8.7.x；「significative」→「significant」；stable 在 Nystroem 與 RBF 段各加一行指向「Nystroem vs RBFSampler」比較範例。內容無實質差異。

## 與下列問題的關聯（只寫有關的題號）
- Q8：6.7.6（只用內積的演算法如 linear SVM、PCA 都可換成 kernel）。
- Q9：6.7.6（Mercer kernel 保證存在 Hilbert 空間映射、可無窮維）；RBF 近似。
- Q13：頁首與 6.7.2（kernel approximation＋SGDClassifier 做大規模非線性學習；RBFSampler vs Nystroem）。
