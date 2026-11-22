# Why Gaussian radial basis function maps the examples into an infinite-dimensional space?（Stack Overflow Q23581508）
- URL: https://stackoverflow.com/questions/23581508/why-gaussian-radial-basis-function-maps-the-examples-into-an-infinite-dimensiona
- 講義頁: p.26（錨文字：未提供）
- 抓取狀態: 部分。網頁直連 curl 回 HTTP 403。改用官方 API：`api.stackexchange.com/2.3/questions/23581508?site=stackoverflow&filter=withbody` 與 `/answers?…&sort=votes`，皆 HTTP 200，has_more=false，共 3 則回答全數取得。回答 23581657 的公式原為 GIF 圖（https://i.sstatic.net/HDO5y.gif），已下載並以目視轉錄。留言（comments）未讀。
- 讀取日期: 2026-11-22

## 重點（中文撰寫，術語保留原文）
- **提問（2014-05）**：既然 landmarks 就是 m 個訓練樣本，每個樣本得到 m 個相似度，特徵空間應該是 m 維，為何說無窮維？引用 Wikipedia："the corresponding feature space is a Hilbert space of infinite dimensions."
- **三則回答意見不一，照分數與採納狀態記錄，不代為裁決：**
  1. 回答 23581657（score 17，**未採納**，最高票）：dual 只依賴內積，可換成 "well-behaved" 的相似度，並說 "it should be positive-definite, it's needed to preserve convexity, as well as enables Mercer's theorem"。RBF 是某個無窮維空間中的 scalar product。圖中公式（自 GIF 轉錄）：
     exp(−½‖x−y‖²) = exp(−½‖x‖²) · exp(−½‖y‖²) · ∑_{k=0}^∞ (x,y)ᵏ/k! = ∑_{k=0}^∞ ⟨ (c(x)/k!)^{1/k} x, (c(y)/k!)^{1/k} y ⟩ᵏ，其中 c(x)=exp(−½‖x‖²)。
     結論句："Thus RBF is kind of a union of polynomial kernels of all possible degrees."
     - 註：GIF 中的根號為 k 次方根，我讀作 (·)^{1/k}。式中 exp 指數固定為 −½‖x−y‖²，**相當於 γ=½，沒有討論 γ**。
     - **核對（本筆記自行驗算，非來源內容）**：前兩個等號正確，因為 exp(−½‖x−y‖²)=c(x)c(y)exp(x·y)，而 exp(x·y)=∑(x·y)ᵏ/k!。**最後一個等號照原式不成立**：⟨a x, b y⟩ᵏ = aᵏbᵏ(x·y)ᵏ，其中 aᵏ = c(x)/k!、bᵏ = c(y)/k!，乘起來得 c(x)c(y)/(k!)²，多了一個 1/k!。另外 k=0 時 0 次方根沒有定義。引用時只引中間的級數式，不引最後一步。
  2. 回答 23588558（score 13，**採納**）：同意提問者的看法。"If you have m distinct training points then the gaussian radial basis kernel makes the SVM operate in an m dimensional space." 之所以說無窮維，是因為 "you can make m as large as you want and the space it operates in keeps growing without bound"。並對比多項式 kernel：1000 個 2D 樣本用 ⟨x,y⟩² 時只在 3 維空間運作。
  3. 回答 23581581（score 7，未採納）：無窮維只是理論證明的一部分，"of no practical importance. You never actually touch an infinite-dimensional space"。用來說明 RBF 等同某向量空間的內積，因此 SVM 理論仍成立。
- 3 則回答都**沒有**解釋 γ 的大小代表什麼。

## 與下列問題的關聯（只寫有關的題號）
- 第 9 題（核心：RBF 無窮維的級數展開論證與「實際上只在 m 維 span 中運作」的另一觀點；positive-definite 與 Mercer 的關係。γ 在此頁未提及）
- 第 8 題（間接：「dual 只依賴內積 → 換成 kernel」是 kernel 化的一般原則）
