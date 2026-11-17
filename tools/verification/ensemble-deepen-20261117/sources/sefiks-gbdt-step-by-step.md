# A Step by Step Gradient Boosting Decision Tree Example（Sefik Ilkin Serengil, sefiks.com）
- URL: https://sefiks.com/2018/10/04/a-step-by-step-gradient-boosting-decision-tree-example/
- 講義頁: p.45
- 抓取狀態: 部分（WebFetch 兩次讀取成功，但內容經 WebFetch 摘要模型轉述；直接 curl 回 HTTP 406，未取得原始 HTML。第 1–3 輪數值我已獨立重算，與轉述一致；第 4–5 輪規則未示，未核對）
- 讀取日期: 2026-11-17（文章 2018-10-04 發表，頁面顯示 2021-12-26 更新）

## 重點（以中文撰寫，術語保留原文）
- 損失：原文 "we will use mean squared error as loss function"，寫成 $loss=\tfrac12(y-y')^2$，$\partial loss/\partial y'=y'-y$。
- learning rate：原文 "I set α to 1 to make formula simpler."，於是更新量即殘差 $y-y'$。程式碼：`gradient = actual - prediction`。
- 第一棵樹直接擬合原始目標：原文 "We initially create a decision tree for the raw data set."（沒有以平均數作初始常數）。
- 樹演算法：沿用作者前一篇 regression tree 文章（https://sefiks.com/2018/08/28/a-step-by-step-regression-decision-tree-example/），本文未說明分裂準則；樹為**多路類別分裂**（Outlook 分三支、Temperature 分三支）。
- 共 5 輪（epoch）；文中只展開第 1–2 輪規則，第 3–5 輪只給預測值。原文："learning rate (α) and number of iterations (epoch) should be tuned for different problems."

### 資料（14 筆，類別特徵 Outlook／Temp.／Humidity／Wind，數值目標）
| Day | Outlook | Temp | Humidity | Wind | y |
|---|---|---|---|---|---|
|1|Sunny|Hot|High|Weak|25|
|2|Sunny|Hot|High|Strong|30|
|3|Overcast|Hot|High|Weak|46|
|4|Rain|Mild|High|Weak|45|
|5|Rain|Cool|Normal|Weak|52|
|6|Rain|Cool|Normal|Strong|23|
|7|Overcast|Cool|Normal|Strong|43|
|8|Sunny|Mild|High|Weak|35|
|9|Sunny|Cool|Normal|Weak|38|
|10|Rain|Mild|Normal|Weak|46|
|11|Sunny|Mild|Normal|Strong|48|
|12|Overcast|Mild|High|Strong|52|
|13|Overcast|Hot|Normal|Weak|44|
|14|Rain|Mild|High|Strong|30|

### 第 1 輪（rules0：Outlook → Rain 再分 Wind、Sunny 再分 Temp）
葉值：Rain+Weak 47.667、Rain+Strong 26.5、Sunny+Hot 27.5、Sunny+Mild 41.5、Sunny+Cool 38、Overcast 46.25。原文例："the error (or residual) is 25 – 27.5 = -2.5 for day 1."

### 第 2 輪（rules1：Wind → Temp），擬合第 1 輪殘差
下表 r 值為我重算後四捨五入到 3 位；文章（經 WebFetch 轉述）多為截尾值，如 Day 3 r₂=1.416、Day 4 r₁=−2.66、Day 8 r₂=−2.888、Day 10 r₁=−1.66。
葉值：Weak+Hot −1.667、Weak+Mild −3.611、Weak+Cool 2.167、Strong+Mild 5.25、Strong+Cool −3.375、Strong+Hot 2.5。

| Day | r₁ | 第1輪預測 | 第2輪預測 | r₂ |
|---|---|---|---|---|
|1|−2.5|27.5|−1.667|−0.833|
|2|2.5|27.5|2.5|0|
|3|−0.25|46.25|−1.667|1.417|
|4|−2.667|47.667|−3.611|0.944|
|5|4.333|47.667|2.167|2.167|
|6|−3.5|26.5|−3.375|−0.125|
|7|−3.25|46.25|−3.375|0.125|
|8|−6.5|41.5|−3.611|−2.889|
|9|0|38|2.167|−2.167|
|10|−1.667|47.667|−3.611|1.944|
|11|6.5|41.5|5.25|1.25|
|12|5.75|46.25|5.25|0.5|
|13|−2.25|46.25|−1.667|−0.583|
|14|3.5|26.5|5.25|−1.75|

### 第 3–5 輪與結果（文章給的值）
- 第 3 棵樹葉值：Rain+Weak 1.685、Rain+Strong −0.9375、Sunny+Weak −1.963、Sunny+Strong 0.625、Overcast 0.3646；第 4–5 輪規則未示。
- 文章報告的每輪 "mean absolute error"：3.011111、1.112963、0.599383、0.48669、0.406115。原文："We can definitely say that boosting works well."

## 可用的算例或圖解想法

### 我的核算（推論，Python 重算）
- 第 1 輪每片葉 = 葉內 y 平均：例如 Overcast（Day 3,7,12,13）=(46+43+52+44)/4=46.25；Rain+Weak（Day 4,5,10）=143/3=47.667。全部 6 片葉與文章一致。
- 第 3 輪（Outlook → Rain/Sunny 再分 Wind）每片葉 = 葉內 r₂ 平均：重算得 Rain+Weak 1.6852、Rain+Strong −0.9375、Sunny+Weak −1.963、Sunny+Strong 0.625、Overcast 0.3646，與文章一致。
- 第 2 輪每片葉 = 葉內 r₁ 平均：例如 Weak+Hot（Day 1,3,13）=(−2.5−0.25−2.25)/3=−1.667；Weak+Mild（Day 4,8,10）=(−2.667−6.5−1.667)/3=−3.611；Strong+Mild（Day 11,12,14）=(6.5+5.75+3.5)/3=5.25。全部 6 片葉與文章一致。→ 直接印證「平方損失下每片葉的 argmin 是葉內殘差平均，各葉不同」。
- **MAE 的分母疑似錯誤**：第 1 輪 $\sum|r_1|=45.167$，除以 14 得 **3.2262**，除以 15 才得文章的 3.0111；第 2 輪 $\sum|r_2|=16.694$，/14=**1.1925**，/15=1.1130（文章 1.112963）。第 3 輪 $\sum|r_3|/15=0.599383$（=文章值），/14=**0.6422**。三輪報告值都等於 $\sum|r|/15$，n 卻是 14；文中未示 MAE 程式碼，無法確定原因（可能 off-by-one）。
- 等價關係：$f_0=0$、learning rate=1 的設定與 ISLP 演算法 8.2 取 λ=1 相同；與 ESL 演算法 10.3 的差別在於 ESL 以 $f_0=\bar y=39.786$ 起始。

### 可否當教學算例
- **可以**用來示範「擬合殘差 → 每片葉取殘差平均 → 疊加」這個機制，前兩輪全部可手算驗證。
- **不適合**直接當「好的 boosting 範例」：learning rate=1（無 shrinkage）；14 筆資料配 6 片葉的多路分裂樹，有單筆葉（Day 9 的 Sunny+Cool、Day 2 的 Strong+Hot），等於記住訓練資料；只報訓練誤差，且 MAE 分母疑似錯誤；第一棵樹就擬合原始 y 而非以常數起始。
- 建議改編（推論）：保留資料，改為 $f_0=\bar y$、ν=0.1、depth-1/2 二元分裂，並用 /14 的 MAE；或只取第 2 輪那張表示範「葉值＝殘差平均」。

## 與下列問題的關聯
- 平方損失下葉值等於殘差平均、各葉不同：第 2 輪 6 片葉值都是各自葉內殘差平均（已核算）。
- gradient 與殘差：文章用 $\tfrac12(y-y')^2$，負梯度即殘差 $y-y'$。
- 決策樹與階梯函數：類別特徵的多路分裂，每片葉一個常數。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- MAE 數值疑似除以 15（見上）。
- 第 2 輪表格標題標成 "Golf Players"，實際內容是殘差（WebFetch 回報）。
- 第 5 輪出現 5.55E-17、1.39E-17 等浮點雜訊值，表示該輪多數葉值實際為 0。
- 文章自稱 "mean squared error as loss" 但報告的是 MAE；loss 帶 ½ 也非「mean」。
- 只有訓練誤差，沒有測試／驗證，無法說明 boosting 的泛化。
