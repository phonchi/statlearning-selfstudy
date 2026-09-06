# 統計先備教材：教學與驗證記錄

日期：2026-09-06。實作前工作樹乾淨，基準 commit `27837a7`。

## 使用者確認的範圍

完整入門，分核心路徑與選讀；本站提供核心互動，Seeing Theory 提供延伸。
首頁獨立統計區放在課前準備與正課之間。六頁均不需要 Python 或微積分，選讀、不計分。
主 agent 決定教學結構、來源介面及統計審查；GPT-5.6-sol 分工製作 S2–S6 與例行檢查。

| 頁面 | 主題 | 原始參考 |
|---|---|---|
| S1 | 機率、期望、變異；母體與樣本 | [Basic Probability](https://seeing-theory.brown.edu/basic-probability/index.html)、PDF pp.5–18 |
| S2 | 集合、條件機率、獨立、Bayes、計數 | [Compound Probability](https://seeing-theory.brown.edu/compound-probability/index.html)、PDF pp.19–30 |
| S3 | 離散／連續、抽樣分布、CLT | [Probability Distributions](https://seeing-theory.brown.edu/probability-distributions/index.html)、PDF pp.31–40 |
| S4 | 點估計、SE、CI、檢定、bootstrap | [Frequentist Inference](https://seeing-theory.brown.edu/frequentist-inference/index.html)、PDF pp.41–48 |
| S5 | 概似、Beta 先驗與後驗 | [Bayesian Inference](https://seeing-theory.brown.edu/bayesian-inference/index.html)、PDF pp.49–54 |
| S6 | 相關、OLS、殘差、ANOVA | [Regression Analysis](https://seeing-theory.brown.edu/regression-analysis/index.html)、PDF pp.55–66 |

[Seeing Theory PDF](https://seeing-theory.brown.edu/doc/seeing-theory.pdf) 是 2018 草稿，66 頁。
頁碼使用 PDF 閱讀器的一基頁碼，與本檔引用的印刷頁一致。
S4 網站主題是點估計、CI、bootstrap；PDF 的同名章另講檢定與錯誤率，不能一一對換。
網站／PDF 提供概念依據，本站算例、解說及視覺程式自行編寫，沒有引入原圖或原始程式碼。

## 決策與審查重點

- S1 有限樣本觀察比例與理論 p 分開；長期收斂不宣稱每一步誤差都下降。
- S2 不把條件機率方向倒置；零分母顯示未定義，互斥與獨立分開。
- S3 區分 PMF、PDF、CDF；連續區域使用真實端點；CLT 說明 i.i.d. 與正的有限變異數。
- S4 只在常態、已知 σ 條件下展示精確 z 區間／檢定；雙尾陰影分開繪製，參數與區間涵蓋定義一致。
- S5 先驗與後驗顯示正規化密度，概似單獨顯示峰值為 1 的相對曲線；無資料時所有 p 都最大化概似，MLE 不唯一。
- S6 OLS 以同一小資料集合重算，畫面包含極端參數的殘差；相關不代表因果，ANOVA 不宣稱每組都不同。

## 重現與驗收

- `test_statistics_contract.py`：概念來源有效／缺失／錯章／超界／偽輸出，既有 lab 必要性，獨立選讀導覽，首頁捷徑與卡片分離。
- `check_statistics_browser.js`：瀏覽器實際函式與 DOM 對照獨立數值，包括二項分布總質量／矩、均勻與常態區間機率、CI 寬度／涵蓋、雙尾幾何、Beta 整數正規化、OLS 解與極端殘差平方。
- `validate.py`、`check_visual_claims.py` 與 `browser_check.js`：原有結構、數值與手機／CDN 降級檢查。
- 日誌在 `verification/statistics-20260906/`；視覺截圖放 `/tmp/statistics-20260906/`，不把圖檔加入 inline-only repo。

所有改動從母檔重建 HTML。保留原有正課與 Python 教材、lab 引用及歷史 FRAMES；初稿完成時尚未發布；後續讀者審查修正及發布方式見 [READER_FIXES.md](READER_FIXES.md)。
