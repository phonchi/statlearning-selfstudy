# XGBoost Part 4 (of 4): Crazy Cool Optimizations（StatQuest with Josh Starmer）
- URL: https://www.youtube.com/watch?v=oRrKeUCEbq8
- 講義頁: p.54–55
- 抓取狀態: OK（YouTube 自動字幕 `auto`，英文；**字幕品質差**：無標點，且有誤聽，如「stack west」= StatQuest、「XG booze」= XGBoost、「Kasia where」= cache-aware、「blocks four out of core」= blocks for out-of-core。以下引句已依上下文更正拼字，標「[更正]」。只有語音，畫面未擷取。影片 24:27，上傳 2020-03-02）
- 讀取日期: 2026-11-17
- 原始逐字稿：`~/.local/share/youtube-read/oRrKeUCEbq8/transcript.md`

## 重點（以中文撰寫，術語保留原文）
- 前三集講 XGBoost 如何擬合與預測，本集講針對大型資料集的優化：approximate greedy algorithm、parallel learning、weighted quantile sketch、sparsity-aware split finding、cache-aware access、blocks for out-of-core computation（描述欄；[00:46]–[01:14]）。
- **Greedy**：選 gain 最大的切點時不考慮之後葉子怎麼切，所以是貪婪演算法，因此建樹快。["XGBoost uses a greedy algorithm to build trees" [更正]]（[02:12]–[02:40]）
- **貪婪法的限制**：資料多時仍要檢查每個可能切點；多變數時檢查每個變數的每個切點會「take forever」。（[03:24]–[03:52]）
- **Approximate greedy**：不測所有切點，把資料分成 quantiles，只以 quantile 當候選切點；quantile 越多預測越準，但建樹越久。["instead of testing all possible thresholds we only test the quantiles"]（[04:02]–[05:56]）
- 作者說 approximate greedy 預設用「大約 33 個 quantiles」。["by default the approximate greedy algorithm uses about 33 quantiles"]（[05:56]）——見注意。
- **Quantile sketch／parallel learning**：資料大到放不進記憶體時，排序與求 quantile 都變慢；sketch 類演算法可快速得近似解。資料分散到網路上多台電腦，quantile sketch 合併各台的值成**近似直方圖**，再由它算近似 quantile。["The quantile sketch algorithm combines the values from each computer to make an approximate histogram"]（[06:33]–[07:55]）。作者說 sketch 細節超出本片範圍（[07:01]）。
- **Weighted quantile**：一般 quantile 每格觀測數相同；weighted quantile 是每格的「權重和」相同。["the sum of the weights are the same in each quantile"]（[08:12]–[09:09]）
- **權重 = Hessian（cover）**：權重來自 cover，即每個觀測值的 loss 二階導數；迴歸權重全為 1（等同一般 quantile），分類權重為 $p(1-p)$，p 為先前預測機率。["the weight for each observation is the second derivative of the loss function"]（[09:09]–[09:39]）
- 權重在**每建完一棵樹後**重新計算。["in practice weights are calculated after building each tree"]（[11:05]）
- **為何用 Hessian 加權（影片給的理由）**：p 接近 0.5（低信心）時權重大，p 接近 0 或 1（高信心）時權重小；加權分位讓低信心觀測落在較小的格，避免一正一負殘差被併在同一格而互相抵銷、難以改善。["the advantage of using the weighted quantile sketch is that we get smaller quantiles when we need them"]（[13:27]–[14:52]）
- 作者說：只有訓練資料很大時才用 approximate greedy、parallel learning、weighted quantile sketch；小資料時用一般 greedy。["when the training data sets are small... XGBoost just uses a normal everyday greedy algorithm" [更正]]（[15:47]）——見注意。
- **Sparsity-aware split finding（缺失值）**：
  1. 有缺失值仍可算殘差（[16:13]）。
  2. 把資料分成「有 dosage」與「缺 dosage」兩張表，只排序有值的那張（[17:09]–[17:35]）。
  3. 每個候選切點算兩個 gain：缺失值全放左葉（Gain_left）與全放右葉（Gain_right）（[18:03]–[18:31]）。
  4. 選所有切點、兩方向中最大的 gain；該方向就是未來缺失值的**預設路徑**。["will be the default path for all future observations that are missing dosage values"]（[19:26]–[19:55]）
- **Cache-aware access**：CPU cache 最快、主記憶體次之、硬碟最慢；XGBoost 把 gradients 與 Hessians 放進 cache，以快速計算 similarity 與 output value。["XGBoost puts the gradients and Hessians in the cache" [更正]]（[20:34]–[21:31]）
- **Blocks for out-of-core computation**：資料放不進 cache 與主記憶體時，XGBoost 壓縮資料以減少硬碟讀寫（解壓比讀硬碟快），多顆硬碟時用 **sharding** 讓各碟同時讀取。["XGBoost uses a database technique called sharding to speed up disk access" [更正]]（[21:42]–[22:36]）
- **Random subsets**：XGBoost 也可只用隨機子樣本建每棵樹，以及分裂時只看隨機子集特徵。["only looking at a random subset of features when deciding how to split" [更正]]（[23:01]）
- 結語：cache-aware access 等理由與統計無關，所以「machine learning is more than just applied statistics」（[23:32]）。

## 可用的算例或圖解想法
影片的例子（口述，[10:08]–[14:52]）：分類，6 個 dosage，依 dosage 排序的先前預測機率為 0.1, 0.1, 0.9, 0.9, 0.6, 0.4（字幕口述順序；畫面上的實際排列未擷取）。
- 權重：0.1 → 0.09、0.9 → 0.09、0.6 → 0.24、0.4 → 0.24（字幕在 [12:32] 把 0.24 誤聽為「0.2 for」）。
- 等數量 quantile 會把最後兩點（0.6、0.4，一正一負殘差）併成一格；weighted quantile 分成 {0.09+0.09=0.18}、{0.18}、{0.24}、{0.24}，把兩個低信心點分開。

自行核算（推論）：0.1×0.9 = 0.09；0.9×0.1 = 0.09；0.6×0.4 = 0.24；0.4×0.6 = 0.24；總權重 0.84，四格 0.18/0.18/0.24/0.24 ✓。注意這四格的權重和「相近」而非完全相等（影片也說「similar sum of weights」[13:56]）。

缺失值例：候選切點 7.5、15.5、23（相鄰 dosage 平均）；最佳為 dosage < 15.5 且缺失值走左（Gain_left）（[17:35]–[19:26]）。殘差與 gain 數值字幕未口述，**無法重算**。

互動元件想法（推論）：
1. p 滑桿 → $h=p(1-p)$ 曲線；6 點條狀圖顯示等數量 vs 等權重分格的切法差異。
2. 缺失值：對每個切點並排顯示 Gain_left／Gain_right，選中後畫出預設方向箭頭。

## 與下列問題的關聯（只寫有關的）
- **quantile sketch 與近似直方圖**：影片明說 sketch 合併各機資料成「approximate histogram」再求近似 quantile（[07:29]–[07:55]、[15:21]）。
- **直方圖對誰切**：影片的 quantile 是對**特徵值**（dosage）排序後切，權重是每個觀測的 Hessian（[09:09]、[13:27]）。影片未提「每格累加 g/h 統計量」這件事（推論：需對照論文／LightGBM 文件）。
- **為何以 Hessian 當權重**：影片只給直覺（低信心觀測權重大 → 格子較細）（[13:27]–[14:52]），**沒有**論文中把目標改寫成以 $h_i$ 加權的平方損失那段推導。
- **分類時 h=p(1−p)**：[09:39]、[11:34]–[12:59]。
- **缺失值的預設方向**：[16:13]–[20:25]，即優先查證 #5 的直覺版本。
- **優先查證 #1（精確貪婪的成本／pre-sorted column block）**：本片**沒有**提到 pre-sorted column block 或「只排序一次」；「blocks」一節只講壓縮與 sharding（[21:42]–[22:36]）。本片也沒有說「每個節點都要重新排序」。缺失值一節只說「we need to sort the dosages from low to high」（[16:41]）。
- **min_child_weight**：本片未提。
- random subspace vs random forest：影片提到 XGBoost 可抽樣列與欄（[23:01]），未區分 per-tree 與 per-split。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 「about 33 quantiles」：作者未說明來源。推論：可能對應舊版 `sketch_eps`（約 1/0.03）；新版 approx／hist 改以 `max_bin` 控制——**版本相依，需以官方文件核對**，不在此斷言。
- 「只有資料很大時才用 approximate greedy，小資料用 exact greedy」：反映舊版 `tree_method='auto'` 的行為（推論）；新版預設 `tree_method` 可能已改（優先查證 #4）——**需以官方文件核對**。
- 「Cache-aware access = 把 gradients 與 Hessians 放進 cache」是簡化說法；論文是針對 block 結構的非連續存取，用 prefetch buffer 收集 gradient 統計量（推論，需對照論文 Sec. 4.2 原文）。
- 「Blocks for out-of-core」只講 compression 與 sharding，略去論文的 column block（CSC、預排序）核心概念，學生若只看影片會誤以為 block 只與硬碟有關（推論）。
- 初始預測「by default is 0.5」（[01:43]）同 Part 1，版本相依。
- 字幕無標點、誤聽多，引句已更正；精確措辭請以 `transcript.json` 的時間點回聽確認。
