# Decision trees: leaf-wise (best-first) and level-wise tree traverse（Data Science StackExchange Q26699）
- URL: https://datascience.stackexchange.com/questions/26699/decision-trees-leaf-wise-best-first-and-level-wise-tree-traverse
- 講義頁: p.57
- 抓取狀態: 部分。網頁直接抓取回 HTTP 403（curl 與 WebFetch 皆同），改用官方公開 Stack Exchange API（`api.stackexchange.com/2.3/questions/26699` 與 `/answers`，`filter=withbody`）取得問題與全部回答的本文。問題中引用的 LightGBM 示意圖片未取得。
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **提問**（使用者 kkk，score 24，2018-01）引用 LightGBM 文件問了四件事：
  1. 哪些演算法是 level-wise。提問者認為 C4.5、CART 用 DFS，XGBoost 用 BFS。
  2. level-wise 的樹是否所有葉都等深。
  3. 若不是，兩種方式長完後是否相同。
  4. 那為何 leaf-wise "can reduce more loss"。
- **唯一回答**（David Marx，score 26，被採納）：
  - **長滿的樹相同，差在展開順序**：原文 "If you grow the full tree, best-first (leaf-wise) and depth-first (level-wise) will result in the same tree."
  - **順序之所以重要，是因為實務上會提早停止或剪枝**：原文 "application of early stopping criteria and pruning methods can result in very different trees."
  - **leaf-wise 依對整體 loss 的貢獻挑分裂**，所以同樣葉數下通常較好。原文 "for a given number of leaves, leaf-wise will probably out-perform level-wise."
  - **不加停止條件時兩者終將收斂**：原文 "without stopping or pruning they will converge to the same performance"。
  - **C4.5 與 CART 屬於 depth-first，不是 best-first**：原文 "both C4.5 and CART are depth-first examples, not best-first."
- **回答引用 Shi (2007) 碩士論文 *Best-first Decision Tree Learning*（Waikato）§1.2**：
  - 標準 C4.5／CART 以 depth-first 展開，每步用 divide-and-conquer。
  - best-first 每步加入「在所有可分裂節點中最能降低 impurity」的節點。原文 "The 'best' node is the node that maximally reduces impurity among all nodes available for splitting"。
  - 兩者長滿後相同，但 best-first 方便以 cross-validation 選展開次數，做 pre-pruning 或 post-pruning。
  - 這種作法「目前只在 boosting 中被評估過」（引 Friedman et al., 2000）。
  - LightGBM Features 頁的 leaf-wise 也引用同一篇 Shi (2007)（文獻 [7]）。

## 可用的算例或圖解想法
- 同一組 7 個候選分裂，各標上 gain。分別依「depth-first（固定左到右）」「level-wise（逐層）」「best-first（全域 gain 最大者優先）」的順序編號，再設「只能分 3 次」的預算，看三種方式選到的分裂集合有何不同。重點是：預算有限時順序決定結果，預算無限時三者長成同一棵樹。
- 回答 Q2：level-wise 不保證所有葉等深，因為節點可能因純度或停止條件提早成為葉。（推論，回答本身沒有直接回應 Q2。）

## 與下列問題的關聯（只寫有關的）
- **leaf-wise vs level-wise**：這是最直接的說明。差別在「展開順序」加上「預算或停止條件」。leaf-wise 的優勢只有在固定葉數（如 LightGBM 的 `num_leaves`）時才有意義。
- **interaction depth d／max_depth**：level-wise 用深度控制複雜度，leaf-wise 用葉數控制。（推論）

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **術語混用**：回答第一句寫 "depth-first (level-wise)"，把 depth-first 與 level-wise 當成同義詞。嚴格說，level-wise 是逐層（breadth-first）展開，depth-first 是沿一條分支先往下展開，兩者不同；提問者自己就區分了 DFS 與 BFS。不過不加限制時，三種順序長出的完整樹都相同，所以回答的核心結論（長滿相同、順序在有預算時才重要）不受影響。教學時應改寫成「best-first vs 固定順序（depth-first 或 level-wise）」。
- 回答沒有處理 XGBoost 是否為 BFS 的問題，也沒有談 `max_depth` 在 leaf-wise 下的角色。
- 這是 2018 年的社群問答，不是官方文件。
