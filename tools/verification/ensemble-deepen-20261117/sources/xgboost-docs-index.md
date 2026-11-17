# XGBoost Documentation（文件首頁，latest）
- URL: https://xgboost.readthedocs.io/en/latest/
- 講義頁: p.48
- 抓取狀態: OK（"XGBoost Documentation — xgboost 3.5.0-dev documentation"；首頁僅為目錄與一段簡介）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- 定位（首頁簡介）："XGBoost is an optimized distributed gradient boosting library designed to be highly efficient, flexible and portable."
- "XGBoost provides a parallel tree boosting (also known as GBDT, GBM) that solve many data science problems in a fast and accurate way."
- "The same code runs on major distributed environment (Hadoop, SGE, MPI) and can solve problems beyond billions of examples."
- 目錄中與本單元相關的頁：Introduction to Boosted Trees、DART、Monotonic Constraints、Feature Interaction Constraints、Categorical Data、Multiple Outputs、Random Forests(TM) in XGBoost、Notes on Parameter Tuning、Custom Objective and Evaluation Metric、Intercept、FAQ、XGBoost Parameters、Tree Methods。
- Release notes 列表最新正式版：3.4.1 Patch Release (Aug 14, 2026)、3.4.0 (Aug 4, 2026)；latest 文件為 3.5.0-dev；stable 文件為 3.4.2（見其他筆記頁首）。

## 可用的算例或圖解想法
- 首頁本身無算例。可提示學生：參數直覺（λ、γ 對應 Eq.2）在「Introduction to Boosted Trees」頁（參數頁 `lambda`/`gamma` 皆寫 "described in the Introduction to Boosted Trees"）；該頁本次未抓取。

## 與下列問題的關聯（只寫有關的）
- 僅提供入口；實質內容見 xgboost-parameters、xgboost-tree-methods、xgboost-faq-missing-values、xgboost-categorical、xgboost-dart 筆記。
- 「GBDT, GBM」是官方對 gradient boosting 的別稱（與論文腳註 1 一致：GBM／GBRT）。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 講義連的是 `/en/latest/`（開發版 3.5.0-dev），其餘筆記用 `/en/stable/`（3.4.2）。本次只抓了 latest 的首頁，未抓 latest 的參數頁，兩版預設值**未比對**；引用時宜固定到 stable 並寫版本。
- 首頁說 "Random Forests(TM) in XGBoost"——XGBoost 可用 `num_parallel_tree` 等訓練隨機森林（參數頁原文 "used to support boosted random forest"）；該教學頁本次未讀。
