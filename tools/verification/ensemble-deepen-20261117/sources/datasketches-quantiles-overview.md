# Apache DataSketches — Introduction to the Quantile Sketches（Quantiles Overview）
- URL: https://datasketches.apache.org/docs/Quantiles/QuantilesOverview.html
- 講義頁: p.54
- 抓取狀態: 部分（講義原網址回 **HTTP 404**。改讀：①現行搬移後頁面 https://datasketches.apache.org/docs/QuantilesAll/QuantilesOverview.html（HTTP 200，內容與舊頁同一篇、略有更新）；②Wayback 快照 http://web.archive.org/web/20240809085029/https://datasketches.apache.org/docs/Quantiles/QuantilesOverview.html（2024-08-09）。以下以①為主，必要處註明②差異。）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- 函式庫有四類 quantile sketch：原文 "Three of the quantile sketches have mathematically provable error bounds while the fourth is an empirical algorithm."（Introduction 首段）
  - 有可證誤差界的三種：Classic quantile sketch family、KLL quantile sketch family、REQ quantile sketch。
  - 經驗法：T-Digest；"has no mathematical basis for estimating its error and its results are dependent on the input data."
- **誤差界是對 rank 而非對 quantile**：原文 "The mathematical error bounds of the Classic, KLL and REQ sketches are specified with respect to rank and not with respect to quantiles."
- Classic 與 KLL：rank 上下界之差 "is a 99% confidence interval and is an additive constant for all normalized ranks between 0.0 and 1.0."；誤差是參數 K 的函數。例：rank error 1% 時，rank .01 與 .99 的誤差都是 ±.01（99% 信心）。
- REQ（Relative Error Quantiles）：誤差相對於 rank 本身，可選高端（HRA）或低端（LRA）高精度，例如 "99.999%ile quantiles"（現行頁 REQ Key Features）。
- **rank 誤差小不保證 quantile 值誤差小**：原文 "there could be step function in the values"，使 ranks .49 與 .51 對應的 quantile 差 "as large as the the entire dynamic range of all quantiles."
- KLL："Near optimal accuracy per sketch size compared to other constant accuracy quantiles sketches."
- 現行頁：QuantileSearchCriteria 預設為 Inclusive，Exclusive "compatible with older Quantiles Sketch"（Wayback 版的列法順序不同，當時未標預設）。

## 可用的算例或圖解想法
- 用「rank 誤差 ε」對應 XGBoost 論文 Eq.9 的 $|r_k(s_{k,j})-r_k(s_{k,j+1})|<\epsilon$：兩者都是在 **rank 空間**控制誤差，候選切點約 $1/\epsilon$ 個（連結屬推論；本頁未提 XGBoost）。
- 「rank .49–.51 對應的值可能跨整個範圍」的例子，可說明為何直方圖分箱（依分位數）在有大量重複值或跳躍時，箱寬會很不均勻（推論）。

## 與下列問題的關聯（只寫有關的）
- quantile sketch 與近似直方圖：本頁提供「sketch 只保證 rank 近似」這個一般概念與術語（Classic、KLL、REQ、T-Digest）。
- **優先查證 2**：本頁**完全沒有**談加權（weighted）分位數，也沒有提 XGBoost 或 Hessian；XGBoost 加權 sketch 的權重與理由只能引論文 §3.3（見 xgboost-paper 筆記）。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 講義連結已失效（404），應更新為 `/docs/QuantilesAll/QuantilesOverview.html`。
- 現行頁 T-Digest 段落的 Java Package 與 C++ Directory 寫成 `org.apache.datasketches.req`／`req`，看似從 REQ 段複製的錯誤（頁面原樣如此，未查證實際套件名）。
- 頁面有多處拼字錯誤（implentations、accuacy、spcific、"the the"），不影響內容。
