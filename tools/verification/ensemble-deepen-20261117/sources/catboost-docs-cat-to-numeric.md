# Transforming categorical features to numerical features（CatBoost 官方文件）
- URL: https://catboost.ai/en/docs/concepts/algorithm-main-stages_cat-to-numberic
- 講義頁: p.29／p.59
- 抓取狀態: OK（curl 取得 HTML。公式以 `yfm-latex` 的 `data-content` 屬性存放，已解碼成 LaTeX；範例表格已轉成純文字）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **類別特徵在每次選分割前才轉成數值**，而且會用類別特徵之間的組合，以及類別與數值特徵的組合。原文："Before each split is selected in the tree (see Choosing the tree structure), categorical features are transformed to numerical."
- **轉換分三步**：
  1. 隨機排列輸入樣本。
  2. 把 label 轉成整數：回歸做分桶量化，分類為 0/1，多類別用類別編號。
  3. 用下列其中一種 ctr 公式編碼。
- **Borders**：對第 $i$ 個門檻（$i\in[0,k-1]$），
$$ctr_i=\frac{countInClass+prior}{totalCount+1}$$
  其中 countInClass 是「label 超過 $i$」的次數，只計算已處理過的物件（依洗牌後的順序）。原文："It only counts objects that already have this value calculated (calculations are made in the order of the objects after shuffling)."
- **Buckets**：公式相同，但 countInClass 改成「label 等於 $i$」的次數；$i\in[0,k]$，共產生 $k+1$ 個特徵。
- **BinarizedTargetMeanValue**：公式相同，countInClass 為 label 值總和除以最大 label 整數 $k$。
- **Counter**：$ctr=\dfrac{curCount+prior}{maxCount+1}$，即頻率編碼，不使用 label。原文："This ctr does not depend on the label value."
  - 驗證集的計數方式有兩種：`Full` 合併訓練與驗證集計數，`SkipTest` 只用訓練集。
- **分類任務的公式**：
$$avg\_target=\frac{countInClass+prior}{totalCount+1}$$
  原文說明："prior is the preliminary value for the numerator."；"totalCount is the total number of objects (up to the current one)"。
  - 註記原文："These values are calculated individually for each object using data from previous objects."
- **官方範例（prior = 0.05）**：洗牌後依序為 rock/0、indie/0、rock/1、rock/1、pop/1、indie/1、rock/0，編碼結果依序為 0.05、0.05、0.025、0.35、0.05、0.025、0.5125。
- **one-hot**：`one_hot_max_size` 指定門檻。類別數 ≤ 該值時改用 one-hot，且 "Ctrs are not calculated for such features."
- **特徵組合範例**：musical genre × musical style 可組成 "dance rock" 等新特徵。原文："Any number of features can be combined."

## 可用的算例或圖解想法
- **逐列驗算官方範例**（我依公式 $(countInClass+0.05)/(totalCount+1)$ 自行重算，全部吻合）：

| 序 | 類別 | y | 之前同類 (count, total) | 編碼 |
|---|---|---|---|---|
| 1 | rock | 0 | (0, 0) | 0.05/1 = 0.05 |
| 2 | indie | 0 | (0, 0) | 0.05 |
| 3 | rock | 1 | (0, 1) | 0.05/2 = 0.025 |
| 4 | rock | 1 | (1, 2) | 1.05/3 = 0.35 |
| 5 | pop | 1 | (0, 0) | 0.05 |
| 6 | indie | 1 | (0, 1) | 0.025 |
| 7 | rock | 0 | (2, 3) | 2.05/4 = 0.5125 |

  教學重點：第 4 列自己的 $y=1$ 沒有計入，這就是 ordered TS 避免 target leakage 的方式。
- 可以把同一筆資料換一個排列再算一次，說明單一排列下排在前面的樣本 TS 變異大，因此需要多個排列。

## 與下列問題的關聯（只寫有關的）
- **類別編碼／target leakage**：這是官方對 ordered target statistics 的實作描述，可與論文式 (5) 對照。
- **缺失值**：此頁說數值特徵允許 NaN 表示缺失，但未說明類別特徵的缺失如何處理。教學 notebook 說缺失會被當成 "None" 字串類別，那是教學文的說法。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **與論文公式的對應**：論文是 $(\sum y+a\,p)/(n+a)$，文件是 $(countInClass+prior)/(totalCount+1)$，等於固定 $a=1$、$prior=a\cdot p=p$。若照文件把 prior 設 0.05，相當於先驗平均 $p=0.05$、權重 $a=1$。這個對應是我的推論。
- 文件說 prior 是 "a number (constant) defined by the starting parameters"，但沒有在此頁寫出預設值。教學 notebook 寫預設使用 Prior=0/1、0.5/1、1/1 三種（Borders），以及 Counter 的 Prior=0/1。
- 範例表的數字用逗號作小數點（"0,05"），屬於排版格式，不是錯誤。
