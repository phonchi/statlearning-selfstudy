# Ch4–6 直接外鏈第二輪核對完成紀錄

所有93筆來源紀錄均已逐一分類，沒有尚未分類或僅以同名詞判定的項目。統計：`{'資料集文件；維持來源與既有資料': 4, '已讀直接相關教學段落': 80, '背景故事/漫畫；排除全文擴寫': 3, '來源受阻；有權威替代與內容核對': 5, '舊路徑失效；已讀現行官方對應頁': 1}`。逐URL與頁碼見 ch1-6-links.json；HTTP回應證據見 ch1-6-fetch.json/快取，web替代原頁段落見 ch4-6-web-fallback.json。

## 外鏈帶來的新增教材

- Ch4：OLS/LDA與降秩indicator回歸、反應誤差與latent logistic、分離時的概似極限、資訊等式與MLE極限、OVR/OVO、QDA log-odds完整a/b/C、F1與隨機AUC。
- Ch5：nested CV、OOF指標合併、CV變異不普遍單調、Jackknife偏差修正與均值驗算、固定設計bootstrap預測誤差方向、block bootstrap、MAPIE split conformal及有限樣本順位/邊際涵蓋證明。
- Ch6：懲罰/限制式KKT與非一對一反例、正交/不相關/獨立、PLS共變異目標/斜率量尺、sum deviance與predict_proba/normalize=False。

## 原來源仍受阻與可核查替代

|原來源|實際障礙|替代與內容範圍|
|---|---|---|
|Math.SE 913918|requests403；web Cache miss|同頁直接相關4612174原答案已讀，另以Gaussian log density獨立展開QDA a/b/C；新增數值檢查|
|Stanford stats191舊Logistic.html|web拒绝開啟舊URL|官方Stanford stats200 Lecture26.pdf已讀；stats191 Python直接連結亦已讀，採正確機率CI/SE推導|
|Stats.SE310687|requests403、web長短URL均Internal Error|Ch1–3代理獨立確認同題；條件風險/MSE_PROOF及主要教材既有證明|
|ScienceDirect S0003267000008503|requests及web均403|區塊重抽樣部分以已讀Stats.SE25706相關段與獨立說明補齐；原論文全文未取得，不宣稱逐條閱讀|
|Saattrup bootstrap-prediction舊文|requests404；web只得空標題|已讀直接連結Stats.SE226565的Davidson–Hinkley預測誤差演算法；MAPIE官方理論已讀，補有限樣本conformal替代|

舊sklearn permutation例子已找到現行官方同題頁並讀完相關示例，故不再列「未讀受阻」。

## 來源自身問題與採用原則

二手討論只用來辨識問題，最終數學由主要教材與獨立推導核對。沒有照抄下列過強或錯誤敘述：Lasso只漸近歸零；Laplace先驗賦予exact-zero機率；CV變異必隨k增加；資訊矩陣等於Hessian的逆；QDA的逆矩陣差寫成矩陣差的逆；每個logistic誤差都同分布；不論情境估σ就必為精確t。

## 最後驗證

第一輪20項數值核對與六頁browser（重抽樣求和裸<已修）已完成。第二輪11項數值驗算PASS，見ch4-6-linked-numerical.json。最後三頁validator/browser依主代理GEN同步後的log為準。證明新增格式仍由lib.proof統一產生，預設收合；正文保留完整公式、條件、算法及算例。
