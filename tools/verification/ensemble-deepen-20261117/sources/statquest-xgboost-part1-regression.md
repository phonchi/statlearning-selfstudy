# XGBoost Part 1 (of 4): Regression（StatQuest with Josh Starmer）
- URL: https://www.youtube.com/watch?v=OtD8wVaFm6E
- 講義頁: 當學期閱讀（非講義特定頁）
- 抓取狀態: OK（YouTube 自動字幕 `auto`，英文；只有語音，畫面上的散佈圖、樹圖與公式未擷取。影片 25:46，上傳 2019-12-16；描述欄附作者更正兩則）
- 讀取日期: 2026-11-17
- 原始逐字稿：`~/.local/share/youtube-read/OtD8wVaFm6E/transcript.md`

## 重點（以中文撰寫，術語保留原文）
- 初始預測可以是任何值，但預設 0.5，迴歸與分類皆然。["by default, it is 0.5, regardless of whether you're using XGBoost for regression or classification"]（[02:35]）
- XGBoost 對殘差擬合的是作者稱為「XGBoost tree」的特殊迴歸樹，不是一般 off-the-shelf 迴歸樹。["XGBoost uses a unique regression tree that I call an XGBoost tree"]（[03:11]）
- Similarity score（迴歸）：
  $$\text{Similarity}=\frac{(\sum_i r_i)^2}{n+\lambda}$$
  ["The similarity score equals the sum of the residuals squared over the number of residuals plus lambda"]（[04:07]）——注意是「先加總再平方」，正負殘差會互相抵銷（[04:36]）。
- 殘差相近或只有一個時 similarity 大；殘差差異大時互相抵銷、similarity 小。["when the residuals in a node are very different, they cancel each other out"]（[07:54]）
- Gain = Similarity(左) + Similarity(右) − Similarity(根)。["Gain is equal to the similarity score for the leaf on the left plus..."]（[08:23]）
- 候選切點為相鄰兩觀測值的平均，取 gain 最大者（貪婪）。["we will use the threshold that gave us the largest gain"]（[10:25]）
- 範例深度限制 2 層；作者說預設允許至 6 層。["the default is to allow up to six levels"]（[12:24]–[12:53]）
- 剪枝：選一數 γ（gamma）；由最低的分支起，若 Gain − γ < 0 就移除，否則保留；若子分支被保留，父分支即使 Gain < γ 也不移除。["If the difference between the gain and gamma is negative, we will remove the branch"]（[13:02]–[14:00]）
- γ = 0 不等於關閉剪枝：gain 本身可為負，γ=0 時仍會剪。["setting gamma equal to zero does not turn off pruning"]（[18:35]）
- λ 是正則化參數，用來降低預測對個別觀測值的敏感度。["it is intended to reduce the prediction sensitivity to individual observations"]（[15:15]）
- λ > 0 使 similarity 變小，且葉中殘差越少減幅越大；因此 gain 變小、較容易剪枝。["when lambda is greater than 0, it is easier to prune leaves"]（[16:13]、[17:35]）
- Output value（迴歸）：
  $$O=\frac{\sum_i r_i}{n+\lambda}$$
  ["The output value equals the sum of the residuals divided by the number of residuals plus lambda"]（[19:29]）；λ=0 時就是葉內殘差平均（[20:56]）。
- 預測 = 初始預測 + η × 樹輸出；XGBoost 稱 learning rate 為 eta，預設 0.3。["XG boost calls the learning rate eta, and the default value is 0.3"]（[21:40]–[22:07]）
- 之後持續以新殘差建樹，直到殘差夠小或達到最大樹數。（[23:39]）

## 可用的算例或圖解想法
影片的例子（口述）：4 個觀測值，初始預測 0.5 下殘差依 dosage 由小到大為 **−10.5, 6.5, 7.5, −7.5**（口述見 [04:36]–[05:02]，順序由後續切點推得）。

影片口述的數值與自行核算（推論，用 Python 重算；$S=(\sum r)^2/(n+\lambda)$）：

| 項目 | 影片 λ=0 | 自算 λ=0 | 影片 λ=1 | 自算 λ=1 |
|---|---|---|---|---|
| 根 {−10.5, 6.5, 7.5, −7.5} | 4 | 4 | 3.2 | 3.2 |
| 左 {−10.5} | 110.25 | 110.25 | 55.12 | 55.125 |
| 右 {6.5, 7.5, −7.5} | 14.08 | 14.083 | 10.56 | 10.5625 |
| Gain（dosage < 15） | 120.33 | 120.333 | 「66」→描述更正 62.48 | 62.4875 |
| Gain（dosage < 22.5） | 4 | 4 | — | 2.133（推論） |
| Gain（dosage < 30） | 56.33 | 56.333 | — | 27.988（推論） |
| 第二層 {6.5}｜{7.5, −7.5}（< 22.5） | 28.17 | 28.167 | — | 10.5625（推論） |
| 第二層 {6.5, 7.5}｜{−7.5}（< 30） | 140.17 | 140.167 | 「smaller than before」 | 82.896（推論） |
| 假想再切 {6.5}｜{7.5}：父 / 左 / 右 / Gain | — | 98 / 42.25 / 56.25 / 0.5（推論） | 65.3 / 21.12 / 28.12 / −16.06 | 65.333 / 21.125 / 28.125 / −16.083 |
| Output {−10.5} | −10.5 | −10.5 | −5.25 | −5.25 |
| Output {6.5, 7.5} | 7 | 7 | — | 4.667（推論） |
| Output {−7.5} | −7.5 | −7.5 | — | −3.75（推論） |

- 剪枝例（影片）：γ=130 → 140.17 − 130 > 0 保留下層分支，因而根（120.33）也保留；γ=150 → 兩個分支都剪掉，只剩初始預測（[13:31]–[14:56]）。λ=1 時兩個 gain 都 < 130，整棵樹被剪掉（[17:07]–[17:35]）。自算 62.49、82.90 皆 < 130 ✓（推論）。
- 預測（影片）：dosage = 10 的樣本 0.5 + 0.3 × (−10.5) = −2.65；dosage = 20 的樣本 = 2.6（[22:07]–[22:41]）。自算 0.5 + 0.3 × 7 = 2.6 ✓（推論）。
- 推論（非影片口述）：由切點 15、22.5、30 及口述的 dosage 10、20，四點 dosage 可推為 10、20、25、35；由初始預測 0.5 推得 y = −10, 7, 8, −7；第一輪後預測 −2.65, 2.6, 2.6, −1.75，新殘差 −7.35, 4.4, 5.4, −5.25（全部比原殘差小，與 [23:11] 口述一致）。
- λ 對 similarity 的縮小比例為 $n/(n+\lambda)$：n=1 → 1/2、n=3 → 3/4、n=4 → 4/5（推論；與影片口述的「half」「3/4」「8/10」相符）。

互動元件想法（推論）：
1. 四個殘差 + 切點滑桿 + λ 滑桿，即時顯示三個 similarity、gain、葉輸出；可重現上表。
2. γ 滑桿：由下而上剪枝，讓學生看到「子分支保留則父分支不剪」與「λ 變大使 gain 變小 → 更容易剪」。
3. 第二層 {6.5}｜{7.5} 假想切分在 λ=1 時 gain 為負，示範 γ=0 仍會剪。

## 與下列問題的關聯（只寫有關的）
- λ 的直覺：降低對單一觀測值的敏感度；n 越小縮越多；同時壓低 gain（更易剪）與葉輸出（[15:15]–[20:27]、[24:52]）。
- XGBoost 葉輸出（Output value）：迴歸為 $\sum r/(n+\lambda)$；λ=0 時等於殘差平均（[19:29]、[20:56]）。
- 初始預測 p₀：影片說預設 0.5（[02:35]）——見下方注意。
- 平方損失下葉值等於殘差平均：λ=0 的 XGBoost output 即殘差平均（[20:56]）。
- 決策樹與階梯函數：dosage 單變數樹的輸出是分段常數（推論，可作圖；影片畫面未擷取）。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **λ 的預設值**：影片 [20:27] 說「let lambda equal zero, because this is the default value」。這與我們對 XGBoost 官方參數文件的認知（`lambda`/`reg_lambda` 預設為 1）不一致——**需以官方 parameter 頁核對**，未在本筆記中查證。
- **初始預測 0.5**：影片時代（2019）的 `base_score` 預設；新版 XGBoost 可能會自動估計截距——**版本相依，需以官方文件核對**，此處不斷言。
- **max_depth 預設 6**、**eta 預設 0.3**：影片說法，需與官方文件核對（推論：可能仍成立）。
- 作者在描述欄更正：16:50 的「66」應為 62.48（自算 62.4875 ✓）；22:03 原始文件以 ε 表示 learning rate，實作參數為 `eta`。
- 18:04 的 −16.06 是以四捨五入後的 65.3、21.12、28.12 計算，精確值為 −16.083（推論）。
- 「amount of decrease is inversely proportional to the number of residuals」（[16:13]）是鬆散說法；精確的減幅比例是 $\lambda/(n+\lambda)$（推論）。
- Similarity 與 gain 的式子是 XGBoost 實作版本，省略論文的 1/2 係數與 −γ（見 Part 3 筆記 [22:54]）；影片把 γ 描述成「事後剪枝」，論文則把 γ 放進目標函數與分裂增益（推論，需對照論文）。
