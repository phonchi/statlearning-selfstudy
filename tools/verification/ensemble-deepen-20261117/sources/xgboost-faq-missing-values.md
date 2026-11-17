# Frequently Asked Questions — How to deal with missing values（XGBoost 官方 FAQ）
- URL: https://xgboost.readthedocs.io/en/stable/faq.html
- 講義頁: p.53
- 抓取狀態: OK（"Frequently Asked Questions — xgboost 3.4.2 documentation"）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **How to deal with missing values** 節：
  - "XGBoost supports missing values by default. In tree algorithms, branch directions for missing values are learned during training."
  - "Note that the gblinear booster treats missing values as zeros."
  - 指定 `missing` 參數時，"values in the input predictor that is equal to missing will be treated as missing and removed."；"By default it’s set to NaN."
- **Why do I see different results with sparse and dense data?** 節：
  - "“Sparse” elements are treated as if they were “missing” by the tree booster, and as zeros by the linear booster."
  - "sparse matrix implementations like scipy treats 0 as missing, while 0 is a valid split value for XGBoost decision trees."
- **Slightly different result between runs**："due to non-determinism in floating point summation order and multi-threading."
- **I have a big dataset**："Usually it can handle problems as long as the data fits into your memory. This usually means millions of instances."；否則改用 distributed 或 external memory。
- **How to handle categorical feature?**：只導向 Categorical Data 教學頁。

## 可用的算例或圖解想法
- 同一筆資料分別以 dense（NaN 表缺失）與 scipy sparse（未存的 0 視為缺失）餵入，展示 0 被當成「值」或「缺失」時切點不同（依 FAQ 的說法設計；需實跑驗證）。
- 與論文 Alg.3 合起來講：FAQ 只說方向「learned during training」，怎麼學看論文 §3.4。

## 與下列問題的關聯（只寫有關的）
- **優先查證 5（缺失值預設方向）**：官方 FAQ 原文 "branch directions for missing values are learned during training."（How to deal with missing values 節）。學法細節（兩趟掃描比較 gain）出自論文 §3.4 Algorithm 3，FAQ 本身未描述演算法。
- `missing` 參數預設 NaN；稀疏矩陣的隱含 0 也被當成缺失——教學時是常見陷阱。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- FAQ 未說明預測時遇到「訓練時從未缺失的特徵」出現缺失會走哪邊（推論：論文 Alg.3 仍會為每個 split 選一個 default direction，但本頁未證實）。
- `gblinear` 在參數頁已標 deprecated（3.3.0），FAQ 仍以現行語氣描述其缺失值處理。
