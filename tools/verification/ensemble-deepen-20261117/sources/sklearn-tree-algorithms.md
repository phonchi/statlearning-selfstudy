# scikit-learn User Guide 1.10 Decision Trees — §1.10.6 Tree algorithms: ID3, C4.5, C5.0 and CART
- URL: https://scikit-learn.org/stable/modules/tree.html#tree-algorithms-id3-c4-5-c5-0-and-cart
- 講義頁: p.64–65
- 抓取狀態: OK（頁面標題 "1.10. Decision Trees — scikit-learn 1.9.1 documentation"；另讀了 §1.10.8 Missing Values Support）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **ID3**（Quinlan 1986）：建立 multiway tree，每個節點貪婪地選出對類別目標 information gain 最大的類別特徵；樹長到最大後通常再剪枝。原文："The algorithm creates a multiway tree"；"the categorical feature that will yield the largest information gain"。
- **C4.5**：ID3 的後繼版本。把數值變數動態離散化成區間，取消了「特徵必須是類別」的限制；把樹轉成 if-then 規則集，依準確率排序規則，並以「移除規則前提」的方式剪枝。原文："removed the restriction that features must be categorical"。
- **C5.0**：Quinlan 的最新版本，採專有授權。原文："uses less memory and builds smaller rulesets than C4.5 while being more accurate."
- **CART**：與 C4.5 很像，差別在支援數值目標（回歸）、不產生規則集，並且建立二元樹。原文："CART constructs binary trees using the feature and threshold that yield the largest information gain at each node."
- **scikit-learn 用的是最佳化版 CART**，而且目前不支援類別變數。原文："scikit-learn uses an optimized version of the CART algorithm; however, the scikit-learn implementation does not support categorical variables for now."
- **缺失值（§1.10.8）**：`DecisionTreeClassifier`／`DecisionTreeRegressor` 在 `splitter='best'` 時內建支援缺失值。
  - 對每個候選門檻，把所有缺失值分別送往左、右兩邊各評估一次。原文："the splitter will evaluate the split with all the missing values going to the left node or the right node."
  - 兩邊評分相同時，預測時的缺失值走右邊。
  - 另外也會檢查「缺失值全走一邊、非缺失值全走另一邊」的分割。
  - 訓練時某特徵沒有出現過缺失值的話，預測時遇到缺失值就送往樣本數較多的子節點。
- **頁面版本註記**：§1.10.7 提到 MAE 準則 "3–6× slower to fit than the MSE criterion as of version 1.8"。

## 可用的算例或圖解想法
- 四種演算法的比較表（依本頁；「—」表示本頁沒有寫，標「推論」的格子是我補上的）：

| | 分裂型態 | 特徵 | 目標 | 輸出 |
|---|---|---|---|---|
| ID3 | 多路（multiway tree） | 類別 | 類別 | 樹 |
| C4.5 | —（推論：多路） | 類別＋數值（動態離散化） | — | 規則集 |
| C5.0 | — | — | — | 更小的規則集 |
| CART | 二元 | —（sklearn 實作不支援類別） | 類別或數值 | 樹（不產生規則集） |

- 缺失值「左右各試一次」的示意：與 XGBoost 的 sparsity-aware default direction 概念相同，可並列比較。（推論，XGBoost 部分請見兄弟筆記 `xgboost-paper.md`。）

## 與下列問題的關聯（只寫有關的）
- **缺失值的預設方向（優先查證 5 的對照）**：sklearn 的作法是在訓練時對每個門檻比較「缺失值全走左」與「全走右」，選較佳的方向，並記錄下來供預測使用；沒見過缺失值時則走樣本較多的一側。這與 XGBoost 的作法結構相同。（推論：兩者都是「把缺失值當成一整群，試兩個方向」。）
- **決策樹與階梯函數**：此節未直接討論。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **CART 的描述不精確**：頁面說 CART 用 "the largest information gain" 選分割，但同一頁 §1.10.7 列出的分類準則有 Gini 與 Log Loss/Entropy，回歸準則有 Mean Squared Error、Poisson deviance、Mean Absolute Error 等（已 grep 確認）。所以這裡的 "information gain" 只能理解為廣義的 impurity 減少量，不是特指 entropy。教學時應改寫。（「CART 標準上用 Gini」屬一般知識，不是本頁的說法。）
- 「C4.5 converts the trained trees (i.e. the output of the ID3 algorithm) into sets of if-then rules」這句把 C4.5 的樹稱為 "the output of the ID3 algorithm"，寫法含糊。
- 「scikit-learn 不支援類別變數」這句出現在決策樹頁，指的是 `DecisionTree*`。其他估計器（如 HistGradientBoosting）是否支援類別變數，本頁沒有說明，需另查。
