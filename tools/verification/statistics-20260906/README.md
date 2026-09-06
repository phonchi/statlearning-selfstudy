# 統計先備教材驗收（2026-09-06）

本機完成；未 commit、push 或發布。起始 HEAD 為 `27837a7`，起始工作樹乾淨。

## 成品

- 六頁統計先備教材，28 個主節、8 個原生 SVG 互動、52 題三選一自測、122 張詞彙卡。
- 首頁獨立統計區位於課前與正課之間；S1–S4 核心路徑，S2 計數／S5–S6 選讀，不列入評分。
- `manifest.json` 記錄六頁 SHA-256 與精確內容數量；既有 20 份教學 HTML 與 HEAD 逐 byte 相同。

## 最終驗證

| 檢查 | 結果 | 紀錄 |
|---|---|---|
| 全站結構與來源 | 26 頁，0 失敗／0 警告 | `structure.log` |
| 概念／lab 模式回歸 | 9 個測試通過，涵蓋錯章連結與未核對輸出 | `contract.log` |
| 既有視覺數值 | 通過 | `visual-claims.log` |
| 外部連結 | 180 個，0 失敗；兩個既有 Colab HEAD 405 警告 | `links.log` |
| 六頁桌面／手機／CDN 降級 | 0 問題；含按鈕、參數、詞彙卡與自測 | `browser-final.log` |
| 最後 S4／S6 刻度修正 | 0 問題 | `browser-axis-final.log` |
| 獨立數值與 SVG 幾何 | 六頁全部通過 | `independent-numerical.log` |

瀏覽器條件：1280×900 桌面，390×844 手機；以本機 HTML 測試，並攔截 CDN 模擬依賴失效。
全文截圖在 `/tmp/statistics-20260906/all/`，逐互動截圖在 `/tmp/statistics-20260906/review/`。
主 agent 已實際檢視八組互動截圖；子 agent 另檢視各頁桌面與手機結果。依 repo 契約，圖片不放入版本庫。
各頁子目錄留存分工驗證，其中較早的紀錄可能早於最終視覺修訂；以上表列根目錄紀錄與 manifest 為交付狀態。

## 獨立核對與已修正問題

- Bernoulli 邊界 p=0/1、固定種子重現；條件機率預設值及零分母。
- 二項 PMF 總和、平均、變異數；均勻區間 3/8、常態區間 0.682689492；窄區間仍畫出正確面積。
- CI 半寬與逐條涵蓋判定；雙尾各自成多邊形，不橫跨中心；右尾 z<-4 時填滿可見曲線。
- Beta 密度以獨立整數階乘公式對照，數值積分為 1；端點、零資料與後驗更新；無資料時 MLE 不唯一。
- OLS b0=0.8、b1=1、RSS=0.8、R²=25/27；極端參數下平方誤差仍在圖窗內，刻度標籤對應真實座標。
- 主審修正未教先考的變異數縮放、補齊 CDF 與離散左端點規則；修正深色底文字對比與圖說色彩。
- Source validator 現在比對 metadata 章節與 PDF 章節範圍，並保留既有 lab 的逐字核對。

## 重跑

```bash
python3 tools/test_statistics_contract.py
python3 tools/validate.py --net
python3 tools/check_visual_claims.py
node tools/check_statistics_browser.js
SHOT_DIR=/tmp/statistics-20260906/all node tools/browser_check.js s1_probability s2_conditional s3_distributions s4_inference s5_bayesian s6_regression
```
