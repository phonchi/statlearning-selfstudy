# Why there are two different logistic loss formulation / notations?（Cross Validated Q229645）
- URL: https://stats.stackexchange.com/questions/229645/why-there-are-two-different-logistic-loss-formulation-notations
- 講義頁: p.30（錨文字：未提供）
- 抓取狀態: 部分。網頁直連 curl 回 HTTP 403。改用 API `api.stackexchange.com/2.3/questions/229645?site=stats&filter=withbody` 與 `/answers`，HTTP 200，has_more=false，共 2 則回答全數取得。第二則回答的圖（https://i.sstatic.net/J3hYr.png）已下載目視。留言未讀。
- 讀取日期: 2026-11-22

## 重點（中文撰寫，術語保留原文）
- **提問（score 31）**列出兩種寫法：
  - 寫法 1，y∈{0,1}：L = −y log p − (1−y) log(1−p)，p = 1/(1+exp(−βᵀx))。
  - 寫法 2，y∈{−1,+1}：L = log(1+exp(−y·βᵀx))。
  - 提問者說兩者 "identical, the only difference is the definition of the label y"，並猜測 "statistics community likes the first notation and computer science community likes the second"。另說第二種 "more easy to compare with hinge loss or 0-1 loss"。
- **回答 231994（score 13，採納）**："The short version: Yes, Yes"，即同意上述兩點。
  - 寫法 1 來自 Bernoulli 模型：P(Y=y|p)=pʸ(1−p)^{1−y}，加上 logit p = βᵀx，於是 "minimizing log-loss over {0, 1} is equivalent to maximum likelihood estimation of a Bernoulli model"。並指出這是 GLM 的特例。
  - 對寫法 2，回答者坦言 "Actually.. I'm not familiar with Formula 2."，只說 {−1,1} 是 SVM 的標準標籤。
  - **原文用詞錯誤，照錄不改**：寫成 "Fitting an SVM corresponds to maximizing max({0, 1 − yβᵀx}) + λ‖β‖²"。應為 minimizing；式中也少了對樣本的加總。
  - 把這個式子稱為 "the Lagrangian form of a constrained optimization problem"，並一般化為 ℓ(y,β)+λ‖β‖²。hinge 只是 ℓ 的 "drop-in possibilities" 之一，寫法 2 的 logistic loss 也可以放進去。
- **回答 232119（score 9，未採納，提問者自答）**：寫成 L(y,ŷ)=log(1+exp(−y·ŷ))，ŷ 為實數（可來自 βᵀx）。說這種寫法 "removes the "probability interpretation details""，方便與其他 loss 比較：
  - L_01 = I[y·ŷ > 0]，L_hinge = (1−y·ŷ)₊，L_logistic = log(1+exp(−y·ŷ))。
  - **原文的 0-1 loss 式子方向寫反**：應為 I[y·ŷ ≤ 0]（或 < 0）。同一則回答附的圖中，0-1 loss 在 y·ŷ<0 時為 1、>0 時為 0（目視確認），與文字式子不符。
  - 圖（x 軸為 y·ŷ，範圍 −5 到 5）：hinge 在 −5 處約為 6，在 y·ŷ=1 處降為 0；logistic 在 −5 處約為 5，在 0 處約 0.7（與 ln 2 相符），之後平滑趨近 0 但不等於 0。
- 兩則回答都**沒有**談「SVM 較像 L2 正則化的 LR」或 ESL 12.1。只有採納回答的「ℓ+λ‖β‖² 框架」間接支持這個比較。

## 與下列問題的關聯（只寫有關的題號）
- 第 11 題（核心：兩種 logistic loss 寫法的等價與由來；hinge 與 logistic 都屬於「loss + λ‖β‖²」框架；圖中 hinge 與 logistic 的形狀對照）
