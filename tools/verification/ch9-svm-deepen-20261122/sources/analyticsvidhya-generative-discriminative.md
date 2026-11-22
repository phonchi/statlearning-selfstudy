# Decoding Generative and Discriminative Models（Analytics Vidhya, Chirag Goyal）
- URL: https://www.analyticsvidhya.com/blog/2021/07/deep-understanding-of-discriminative-and-generative-models-in-machine-learning/
- 講義頁: p.2（錨文字：未提供）
- 抓取狀態: OK（curl，HTTP 200；HTML 轉純文字閱讀。文中的 Bayes 公式與兩張示意圖為圖片，未讀）
- 讀取日期: 2026-11-22
- 版本: datePublished 2021-07-19，dateModified 2024-12-13（取自頁面 JSON-LD）

## 重點（中文撰寫，術語保留原文）
- 生成式模型的做法：先估 prior P(Y) 與 likelihood P(X|Y)，再用 Bayes 定理得 posterior。原文："they estimate the prior probability P(Y) and likelihood probability P(X|Y)"（〈The Approach of Generative Models〉）。
- 判別式模型的做法：直接假設 P(Y|X) 的函數形式再估參數。原文："they directly assume some functional form for P(Y|X)"（〈The Approach of Discriminative Models〉）。
- 判別式模型的例子列出 SVM：「Logistic regression, Support vector machines(SVMs), … Nearest neighbor, … Decision Trees and Random Forest」（〈Examples of Discriminative Models〉）。
- 數學上的對照："discriminative … maximize the conditional probability P(Y∣X) … generative … maximizing the joint probability of P(X, Y)"（〈Difference Between…〉）。
- 其他宣稱（文章未提供證據或引用）：判別式模型對 outlier 較穩健、計算較便宜；生成式模型「need fewer data to train … since generative models are more biased」，並能以邊際化處理缺失值（〈Application Based Differences〉）。

### 需留意的問題（照原文標記，不代為修正）
- 生成式例子中的「Latent Dirichlet Allocation (LDA)」是主題模型，**不是**課程裡的 linear discriminant analysis。課程的 LDA 雖然也是生成式分類器，但本文沒有提到它。
- 文章前後不一致。一處說判別式模型 "separate classes instead of modeling the conditional probability"（〈What Are Discriminative Models?〉），另一處說它 "maximize the conditional probability P(Y∣X)"，又稱之為 "conditional models"。SVM 實際上不建模 P(Y|X)，但本文沒有區分「機率型判別式」（LR）與「純決策邊界型」（SVM）。
- 〈The Mathematics of Generative Models〉的開頭句 "estimating a function f: X -> Y, or probability P(Y|X)" 與判別式那段用字相同。差別在後續步驟，生成式是經 P(Y)、P(X|Y) 再用 Bayes 求 P(Y|X)。
- 本文沒有提到 SVM 的效率、p>n 或支持向量。

## 與下列問題的關聯（只寫有關的題號）
- 間接關聯第 11 題：SVM 被歸為判別式模型，與 LR 同類。但本文不討論 loss，也沒有比較 SVM 與 LR。其餘題號皆無關。
