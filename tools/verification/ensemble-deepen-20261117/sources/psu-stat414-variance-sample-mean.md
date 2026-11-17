# 24.4 - Mean and Variance of Sample Mean（PSU STAT 414, Lesson 24）
- URL: https://online.stat.psu.edu/stat414/lesson/24/24.4
- 講義頁: p.32
- 抓取狀態: 部分（原站 TLS 憑證鏈驗證失敗：curl "unable to get local issuer certificate"、WebFetch "unable to verify the first certificate"；改讀 Wayback Machine 2025-11-21 快照 http://web.archive.org/web/20251121052744/https://online.stat.psu.edu/stat414/lesson/24/24.4 ，HTTP 200，正文完整）
- 讀取日期: 2026-11-17（快照日期 2025-11-21）

## 重點（以中文撰寫，術語保留原文）
- 設定：$X_1,\dots,X_n$ 為來自平均 $\mu$、變異 $\sigma^2$ 母體的隨機樣本（頁面兩個例題的開頭）。
- 期望值：由期望值的線性與同分布，$E(\bar X)=\frac1n[n\mu]=\mu$。
- 變異數：把 $\bar X$ 寫成 $\sum \frac1n X_i$，套用「前一頁的定理」得（推論：該定理為獨立變數線性組合的變異公式，見下方說明）
  $$\operatorname{Var}(\bar X)=\frac{1}{n^2}\sum_{i=1}^n\operatorname{Var}(X_i)=\frac{\sigma^2}{n}.$$
- 解讀："as the sample size \(n\) increases, the variance of the sample mean decreases"（第二例題末段）；並提到樣本越大成本越高，"There is always a trade-off!"
- 本頁只寫 "applying the theorem on the last page"，未在本頁重述該定理；本次沒有讀 24.3。推論：該定理是獨立隨機變數線性組合的變異公式，依賴 random sample 的獨立性；本頁沒有處理相關情形。

## 可用的算例或圖解想法
- 作為 bagging 動機的第一步：$B$ 個獨立、變異 $\sigma^2$ 的預測取平均，變異為 $\sigma^2/B$。再接 ESL (15.1)：若兩兩相關 $\rho>0$，變異為 $\rho\sigma^2+\frac{1-\rho}{B}\sigma^2$，$B\to\infty$ 時只剩 $\rho\sigma^2$。兩個公式並列，正好說明 random forest 為何要降低 $\rho$。

## 與下列問題的關聯（只寫有關的）
- bagging 為何不易因 $B$ 增加而過擬合：$\sigma^2/B$ 對 $B$ 單調遞減；推廣到相關情形（ESL 15.1）仍單調遞減到 $\rho\sigma^2$，不會回升（推論，配合 ESL §15.3.4 的 (15.3)）。
- 為何 RF 取較小的 $m$：本頁只給獨立情形，相關情形需引 ESL §15.2。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 無錯誤。限制：只涵蓋 i.i.d. 情形；bagged trees 是同分布但**不獨立**，直接套 $\sigma^2/n$ 會高估 bagging 的降變異效果（ESL p.588 明確區分 i.i.d. 與 i.d.）。
- 原站憑證問題可能讓學生瀏覽器出現警告（推論：此為抓取時的環境觀察，學生端未驗證）。
