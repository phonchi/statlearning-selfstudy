# Chapter 6: Statistical Machine Learning — AI-Assisted Statistics for Data Scientists（Bruce, Bruce & Gedeck，Python 程式碼頁）
- URL: https://gedeck.github.io/ai-assisted-statistics-for-data-scientists/docs/python/ch06.html
- 講義頁: 當學期閱讀
- 抓取狀態: OK（curl，HTTP 200）。**注意：此頁是書的配套 notebook 渲染結果，只有程式碼、輸出與小節標題，沒有作者的說明文字**；頁中長串參數說明是 scikit-learn／XGBoost 的 docstring（fitted-estimator HTML repr），不是作者寫的。頁尾標 "2019-2026 Peter C. Bruce, Andrew Bruce, Peter Gedeck"。
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
### 頁面小節（目錄原文）
Statistical Machine Learning → K-Nearest Neighbors（A Small Example: Predicting Loan Default；Standardization；KNN as a Feature Engine）→ Tree Models（A Simple Example）→ **Bagging and the Random Forest**（Random Forest；Variable Importance）→ **Boosting**（XGBoost；Regularization: Avoiding Overfitting；Hyperparameters and Cross-Validation）→ Supplementary Material（Figure 6-2、6-4、6-5）。

### 集成相關程式範例
- **Random Forest**（`loan3000.csv`，兩個 predictor `borrower_score`, `payment_inc_ratio`）：`RandomForestClassifier(n_estimators=500, random_state=1, oob_score=True, n_jobs=4)`。
- **OOB 對樹數**：迴圈 `n_estimators` 由 20 到 500（步長 5），`criterion="entropy", max_depth=5, oob_score=True`，收集 `rf.oob_score_` 畫 `oobScore` 對 `n` 的折線。
- **RF 預測的決策區域散佈圖**：依 `rf.predict(X)` 把點分 "paid off"／"default" 畫在兩特徵平面。
- **Variable Importance**：用 `loan_data` 的 17 個 predictor（`pd.get_dummies(..., drop_first=True)`）配 `rf_all = RandomForestClassifier(n_estimators=500, random_state=1, n_jobs=4)`；比較 `rf_all.feature_importances_`（標為 "Gini decrease"）與自寫的 permutation 法（"Accuracy decrease"）：3 次 `train_test_split(test_size=0.3)`，在 validation 集逐欄 `rng.permutation`，記錄 `(acc - shuff_acc) / acc`，取平均，畫左右兩張橫條圖。
- **XGBoost 基本**：`XGBClassifier(objective="binary:logistic", subsample=0.63)`（`y` 轉成 0/1）。
- **Regularization**：`XGBClassifier(n_estimators=250, max_depth=6, reg_lambda=0, learning_rate=0.3, subsample=1)` vs `reg_lambda=1000, learning_rate=0.1, subsample=0.63`；validation 誤分率輸出 default 0.364、penalty 0.3274（`test_size=10000`）。再用 `predict_proba(..., iteration_range=[1, k+1])` 對 $k=1..249$ 畫 train／test 誤差曲線。
- **Hyperparameters and Cross-Validation**：`eta ∈ {0.1,0.5,0.9}` × `max_depth ∈ {3,6,9}` 的 5-fold 手寫 CV（fold 由 `rng.choice(range(5), size=len(X), replace=True)` 指派），輸出 avg_error：eta=0.1 時 0.329／0.336／0.347（depth 3／6／9），eta=0.9、depth 6 最高 0.386。

### 沒有涵蓋的集成主題（就此頁而言）
- 沒有以下主題的程式範例：voting（hard／soft）、stacking、AdaBoost、sklearn `GradientBoosting*`／`HistGradientBoosting*`、LightGBM、CatBoost、BART、Extra-Trees、`BaggingClassifier`。以不分大小寫 grep 頁面文字：LightGBM、BART、ExtraTrees／Extra-Trees、AdaBoost、stacking、voting 皆 0 次；"CatBoost" 只出現 1 次，位於 XGBoost docstring 內（"(cf. CatBoost)"），不是作者內容。

## 可用的算例或圖解想法
- OOB score 對樹數的曲線：可直接改成本課資料，示範「$B$ 增加後 OOB 誤差穩定、不回升」。
- Gini vs permutation importance 並排橫條圖：對應 ESL Fig 15.5（Gini vs randomization）。
- `reg_lambda=0` vs `1000` 的 train／test 曲線：λ 直覺的實作示範。
- eta × max_depth 的 CV 熱度表：學習率與樹深的交互。

## 與下列問題的關聯（只寫有關的）
- 變數重要度：有 MDI 與 permutation 兩法的對照程式。
- bagging／RF 不因 $B$ 增加而過擬合：OOB 對 `n_estimators` 曲線。
- λ 的直覺、學習率與樹深：XGBoost regularization 與 CV 範例。

## 注意：來源中可疑、過時或與官方文件矛盾之處（多為推論，根據程式碼閱讀）
- Variable Importance 圖混用兩個模型：Gini decrease 來自在**全部資料**上訓練的 `rf_all`，Accuracy decrease 來自在 3 個不同訓練切分上重訓的 `rf`；兩欄並非同一模型的兩種重要度。
- permutation 程式只在每個 validation 集上洗牌一次（無重複洗牌），估計雜訊較大。
- 5-fold 是用有放回的隨機 fold 標籤指派，各 fold 大小不相等（非標準 `KFold`）。
- 誤差以 `abs(y - p) > 0.5` 計算，等同 0.5 門檻的誤分率。
- 數值輸出依賴資料與套件版本；頁面未標版本。
- 本書 PDF 在本機 `~/statslearning/` 也有一份，但依任務範圍本筆記只記錄網頁內容；作者對方法的文字解說需讀書本。
