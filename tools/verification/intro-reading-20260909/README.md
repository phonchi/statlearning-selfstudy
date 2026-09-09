# 導論讀圖說明、信賴區間與詞彙卡修正

基準提交：`099e445ec0f6a216ce6d15e35a9498abd35743b3`。

## 完成內容

- 對照第四章 Bikeshare lab，導論改為先看月份、時段的租借量高低，說明圖上是其他條件相同時的模型估計差異。移除導論的編碼、係數補齊與 GLM 細節，連到第四章再學。
- 兩圖明確標出 0 比較基準；負值表示低於基準，不是負租借量。圖形保留相同資料，沒有改成原始分組平均。
- 全站讀者文字、圖說、按鈕、自測與詞卡統一使用「信賴區間」；保留逐點與同時涵蓋、平均反應與個別觀測預測區間的差別。導論不再提前解釋 bootstrap。
- 第四章補清楚 Poisson 係數位於對數尺度，係數差取指數才是預測平均租借量比值；避免直接解讀成租借量差。
- 詞彙卡只保留統計或機器學習常用專有名詞。刪除論文標題、閱讀提示、一般描述，以及純 Python／環境操作詞卡，不以改名包裝或湊數補卡。

## 全部詞卡審核

| 範圍 | 原有 | 保留 | 刪除 |
|---|---:|---:|---:|
| ch1–ch5 | 137 | 114 | 23 |
| ch6–ch10、ch12 | 169 | 163 | 6 |
| 課前、Python 與統計附錄 | 335 | 155 | 180 |
| 合計 | **641** | **432** | **209** |

導論剩 7 張。00C「AI 輔助統計分析」、P1「Python 基礎」、P2「流程與函式」沒有合適詞卡，因此移除卡片區塊與相關導覽；正文、練習題與互動保留。

完整逐卡索引、原文、KEEP／REMOVE 理由及保留卡的定義修正：

- [ch1–ch5](cards-core.json)
- [進階章節](cards-advanced.json)
- [課前與附錄](cards-appendices.json)

另修正保留卡中的定義問題，例如偏依賴圖、MAR／MCAR／MNAR、五數摘要、標準誤及模型假設。未新增卡片。資料檔與逐卡決策精確比對通過：[card-decisions-check.log](card-decisions-check.log)。

產生器支援空詞卡陣列與重新加入第一張合適詞卡；移除原先最低張數建議。`FLASHCARD-SYNC` 核對頁面與資料檔，`FLASHCARD-TERM` 阻擋已審核排除的標題回流。新詞卡仍須由作者判斷是否為正式術語。

## 驗證

- **確認無誤**：26 頁結構與來源驗證，0 失敗；[validate.log](validate.log)。
- **確認無誤**：全站桌面、手機、按鈕、滑桿、自測、翻卡、MathJax、Chart.js／SVG 與 CDN 失效驗收，0 問題；[browser.log](browser.log)。
- **確認無誤**：Bikeshare 圖說、導論詞卡、空卡片頁與信賴區間文字的實際看圖驗收；[visual-reading.log](visual-reading.log)。0 參考線補齊後再驗收：[bike-final.log](bike-final.log)。
- **確認無誤**：232 張 lab 程式碼卡的程式與保存輸出仍符合來源；[lab-code.log](lab-code.log)。
- **確認無誤**：所有 FRAMES 與基準版逐位元相同，未重新計算模型；[data-protection.log](data-protection.log)。
- **確認無誤**：空詞卡區塊移除／恢復的 4 項測試，及既有用語、來源、統計模式檢查；[card-ui-tests.log](card-ui-tests.log)、[run.log](run.log)。
- **確認無誤**：27 個 HTML 加 README 共 28 個產物完整重建後逐位元不變；[final-manifest.json](final-manifest.json)。

仍有三項既有檔案大小提醒（導論、非線性、非監督式），沒有驗證失敗。原始來源、歷史證據與非讀者用的 FRAMES 來源資料保留原文。

[全教學頁首屏總覽](all-pages-overview.png)；完整頁面與指定區段截圖在 [screenshots](screenshots/)。文字修改對照：[reader-edits.jsonl](reader-edits.jsonl)、[用語替換紀錄](terminology-edits.jsonl)。

重跑本機驗證：

```bash
python3 tools/verification/intro-reading-20260909/run_checks.py
```
