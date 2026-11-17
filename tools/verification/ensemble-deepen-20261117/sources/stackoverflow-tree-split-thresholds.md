# Decision trees. Choosing thresholds to split objects（Stack Overflow Q45513511）
- URL: https://stackoverflow.com/questions/45513511/decision-trees-choosing-thresholds-to-split-objects
- 講義頁: p.56
- 抓取狀態: 部分（網頁直接抓取回 HTTP 403 / Cloudflare 挑戰頁；改用公開 Stack Exchange API 取得問題、2 則回答與留言原文。採納回答引用的投影片 PDF 未抓取。）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **問題**（Nikita，2017-08-04，score 4）：用 impurity function $H(\cdot)$ 比較特徵 $x_j$ 與門檻 $t_m$ 來分裂，但 "there is an infinite number of ways we can choose tm so we can't just compute H() function for each possibility."
- **採納回答**（geledek，2019-01-29，score 3）：引 "Page 18 of these slides"（連結為 https://courses.cs.washington.edu/courses/cse446/13sp/slides/decision-trees-boosting-annotated.pdf ，本次未讀）：
  - Method 1："Sort data according to X into {x_1, ..., x_m}"；"Consider split points of the form x_i + (x_{i+1} - x_i)/2"（相鄰排序值的中點）。
  - Method 2：定義 $IG(Y|X:t)=H(Y)-H(Y|X:t)$，$H(Y|X:t)=H(Y|X<t)P(X<t)+H(Y|X\ge t)P(X\ge t)$，$IG^*(Y|X)=\max_t IG(Y|X:t)$；"For each real-valued attribute, use IG*(Y|X) for assessing its suitability as a split"；"may split on an attribute multiple times, with different thresholds"。
- **另一回答**（William Hammond，score 0）："There isn't really an infinite number of ways of choosing tm."；在 "a reasonable range of thresholds" 內逐一試、取最佳。
- **留言**：Quetzalcoatl（score 2）指出 Method 2 沒說 t 如何取、"Method 1 seems to provide an answer the OP's question"；提問者追問 "How can I estimate a "reasonable range"?"（無人回覆）。

## 可用的算例或圖解想法
- 關鍵觀念（推論，綜合 Method 1）：n 筆資料、某特徵有 u 個相異值時，所有門檻只會產生 u−1 種不同的左右分組，所以「無限多個 t」等價於「u−1 個中點」——這正是 XGBoost 論文 Alg.1 依排序後逐點累加 $G_L,H_L$ 的依據。
- 小例：x = (1, 3, 4, 8)，候選門檻 2, 3.5, 6；任何 t∈(1,3) 的分法都相同。
- 從 exact（所有中點）到 approx/hist（只試分位數切點）的過渡：當 u 很大時改成只試 bins 邊界。

## 與下列問題的關聯（只寫有關的）
- 決策樹與階梯函數、門檻如何選：Method 1 給出「排序 + 相鄰中點」的標準答案。
- **優先查證 1**：排序是 exact 搜尋的前提（本頁）；XGBoost 透過 pre-sorted block 只排序一次（論文 §4.1）。本頁沒有談每節點是否要重排。
- quantile sketch 與直方圖：本頁未提，但可作為「為何需要近似」的起點。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 採納回答只轉述投影片，Method 2 沒有說明 t 的候選集合（留言已指出）。
- 另一回答的「reasonable range」說法模糊；正確說法應是「相異值之間的中點」即足夠（推論，與 Method 1 一致）。