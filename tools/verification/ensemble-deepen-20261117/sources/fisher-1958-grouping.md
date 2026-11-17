# On Grouping for Maximum Homogeneity（Walter D. Fisher, JASA 1958）
- URL: https://www.tandfonline.com/doi/abs/10.1080/01621459.1958.10501479
- 講義頁: p.57
- 抓取狀態: 失敗（Taylor & Francis 頁面 HTTP 403，curl 與 WebFetch 皆同）。只透過 Crossref 公開 API（`api.crossref.org/works/10.1080/01621459.1958.10501479`）取得書目資料，Crossref 沒有收錄摘要。論文本身的內容一概未讀。
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **書目（Crossref）**：Walter D. Fisher, "On Grouping for Maximum Homogeneity", *Journal of the American Statistical Association*, Vol. 53, No. 284, pp. 789–798（1958）。DOI 10.1080/01621459.1958.10501479。與 LightGBM Features 頁參考文獻 [8] 的書目一致。
- **唯一可歸屬的論斷來自 LightGBM 文件，不是 Fisher 原文**：Features 頁引用 [8]，說回歸樹的類別最佳二分有效解約需 $O(k\log k)$，基本想法是 "sort the categories according to the training objective at each split"（見 `lightgbm-features.md`）。
- **CatBoost 論文 §3.1 的相關說法**：所有類別二分中，以 logloss、Gini 或 MSE 衡量的最佳分割，可以在數值化的 target statistic 的閾值中找到，引用 [4, §4.2.2] 與 [11, §9.2.4]。依該論文的參考文獻表，[4] 是 Breiman, Friedman, Stone & Olshen, *Classification and regression trees*（1984），[11] 是 Friedman, Hastie & Tibshirani, *The elements of statistical learning*（2001）。CatBoost 論文沒有引用 Fisher。

## 可用的算例或圖解想法
- （推論，非 Fisher 原文）用 4 個類別 A–D 的平均 $y$ 排序，只檢查 3 個「前綴 vs 後綴」切點，並與窮舉 $2^{3}-1=7$ 種分法比較。這需要另行以 ESL §9.2.4 或 CART 書查證後再寫進教材。

## 與下列問題的關聯（只寫有關的）
- LightGBM 類別分割的理論來源。但「為何依平均值排序後只需看連續切點」的證明，本次沒有讀到原文，不能引用。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 未讀到原文，無法確認 Fisher 1958 實際證明了什麼，也無法確認它與 LightGBM 所說的「類別依目標排序」是否為同一個結果。教學時建議改引 CatBoost 論文所引的 ESL §9.2.4 或 Breiman et al. (1984) §4.2.2，並在引用前核對原文。
