# ID3 algorithm（Wikipedia）
- URL: https://en.wikipedia.org/wiki/ID3_algorithm
- 講義頁: p.64–65
- 抓取狀態: OK（curl 取得 HTML 並轉純文字）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **定義**：ID3（Iterative Dichotomiser 3）是 Ross Quinlan 提出的貪婪演算法，也是 C4.5 的前身。名稱中的 3 代表第三次嘗試。"dichotomiser" 其實是誤稱，因為 ID3 可以做多值分裂。原文："the term dichotomiser is a misnomer as it implies a binary split, but the ID3 algorithm can split on multi-valued attributes."
- **演算法**：從根節點的資料集 $S$ 開始，對每個未使用的屬性計算 entropy 或 information gain，選 entropy 最小（gain 最大）的屬性分割，再對子集遞迴。**每個屬性只用一次**。原文："considering only attributes never selected before."
- **停止條件**：
  1. 子集全屬同一類，該節點成為葉。
  2. 沒有屬性可用，以多數類別作為葉。
  3. 子集為空，以父節點的多數類別作為葉。
- **性質**：
  - 不保證最佳解，可能陷入局部最佳。原文："It uses a greedy strategy by selecting the locally best attribute"。
  - 可能過擬合，應偏好較小的樹。
  - 用在連續資料較困難，因為切點太多。
- **Entropy**：$H(S)=\sum_{x\in X}-p(x)\log_2 p(x)$，$H(S)=0$ 表示完全分類。
- **Information gain**：$IG(S,A)=H(S)-\sum_{t\in T}p(t)H(t)=H(S)-H(S\mid A)$。

## 可用的算例或圖解想法
- 經典的 play-tennis／golf 資料（Outlook、Temperature、Humidity、Wind）可以手算根節點的 IG。chefboost README 的範例輸出正好就是這組資料的 C4.5 規則（見 `chefboost-readme.md`），可以前後呼應。
- 對照 CART：ID3 做多路分裂，而且每個屬性只用一次；CART 做二元分裂，同一特徵可以重複使用、選不同門檻。這說明為何 CART 能逼近任意階梯函數。（推論）

## 與下列問題的關聯（只寫有關的）
- **決策樹與階梯函數**：ID3 只處理類別屬性，討論不到「階梯」；CART 的二元門檻分裂才產生軸對齊的階梯函數。（推論）
- **base learner 怎麼選**：ID3 長滿的樹屬於低偏差、高變異，頁面也提到 "ID3 can overfit the training data."

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **"best-first" 用語衝突**：頁面寫 "ID3 is a greedy heuristic performing a best-first search for locally optimal entropy values."。這裡的 best-first 指「每步選局部最佳屬性」（貪婪），與 LightGBM／Shi (2007) 所說的 best-first（leaf-wise，跨節點挑全域 gain 最大的葉）意義不同。教學時不要混用。ID3 的節點展開順序是遞迴（depth-first）。
- 頁面寫「計算每個屬性的 entropy H(S)，選 entropy 最小者」，嚴格說應是「分割後的條件 entropy $H(S\mid A)$ 最小」。頁面後文的 IG 公式才是正確的表述。
- 頁面有 "[further explanation needed]" 標記，屬於維基條目品質提示。
