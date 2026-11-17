# The Random Subspace Method for Constructing Decision Forests（Tin Kam Ho, 1998）
- URL: https://ieeexplore.ieee.org/document/709601
- 講義頁: p.34
- 抓取狀態: 部分（IEEE Xplore 回 HTTP 202、內容為空的 JS 殼；書目資料取自 Crossref API（DOI 10.1109/34.709601），摘要由 OpenAlex `abstract_inverted_index` 重組；Semantic Scholar 顯示摘要被出版商隱藏、非 open access。**只有摘要，未讀全文**）
- 讀取日期: 2026-11-17

## 書目（Crossref）
- Tin Kam Ho, "The random subspace method for constructing decision forests," *IEEE Transactions on Pattern Analysis and Machine Intelligence*, vol. 20, no. 8, pp. 832–844, 1998. DOI: 10.1109/34.709601

## 重點（以中文撰寫，術語保留原文；全部來自摘要）
- 動機：作者認為過去對決策樹的研究聚焦在 splitting criteria 與樹大小最佳化，"The dilemma between overfitting and achieving maximum accuracy is seldom resolved."（摘要）
- 方法：由多棵樹組成的分類器，樹是 "constructed systematically by pseudorandomly selecting subsets of components of the feature vector"，也就是 "trees constructed in randomly chosen subspaces"（摘要）。
- 宣稱性質：此分類器 "maintains highest accuracy on training data and improves on generalization accuracy as it grows in complexity"（摘要）。
- 實驗：與單樹分類器及其他 forest 建構法在公開資料集上比較，作者稱其 superiority 得到驗證。
- 摘要最後提到討論 "independence between trees in a forest" 及其與組合分類準確度的關係。

## 可用的算例或圖解想法
- 與 random patches（`louppe-geurts-2012-random-patches.md`）合用：Ho 的 random subspace 是「每棵樹整棵只用一組隨機特徵子集」，對照 RF「每個節點重抽特徵」。可畫三格示意：Bagging（抽列）／Random Subspace（抽欄、每樹一次）／RF（抽列＋每節點抽欄）。
- 在 scikit-learn 中可用 `BaggingClassifier(bootstrap=False, max_features<1.0)` 實作 random subspace（`max_features` 是「每個 base estimator 抽多少特徵」，見 `sklearn-ensemble-guide.md`）。

## 與下列問題的關聯（只寫有關的）
- random subspace vs random forest：摘要只說「在隨機子空間建樹」；「每棵樹抽一次 vs 每個 split 抽一次」的對比，可引用的出處是 Louppe & Geurts 2012 §2.3："In RP, the subset of features is selected globally once and for all, prior to the construction of the tree." 與 "By contrast, in RF (resp. in ET) subsets of features are drawn locally at each node."（兩句相連）。
- 歷史：ESL p.602 Bibliographic Notes 說 "Ho (1995) introduced the term “random forest,” and used a consensus of trees grown in random subspaces of the features."（注意是 Ho **1995**，與本篇 1998 不同）。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 未讀全文：Ho 每棵樹抽多少特徵、是否也做 bootstrap、樹是否完全長滿等細節**不可**由本筆記推斷；若講義要寫，須另找全文。
- 摘要說「training accuracy 維持最高、generalization 隨複雜度提升」是作者在其實驗上的主張，不是一般定理。
