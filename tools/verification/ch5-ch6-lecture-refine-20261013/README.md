# 第 5、6 章依講義修訂（2026-10-13）驗證紀錄

範圍：使用者 15 點意見（第 5 章 bootstrap／CV 模擬、第 6 章講義對齊、概念問答嵌入、兩章數學全面改 LaTeX）。
決策見 HANDOFF.md §22。

| 檔案 | 內容 |
|---|---|
| `run.log` | 完整建置與檢查輸出（兩輪：初版、Codex 複查修正後） |
| `misuse_code.py`／`misuse_code.log` | 頁面 `w05-detail-misuse-code` 的程式原樣；m524（numpy 1.24.4、sklearn 1.6.1）重跑得 0.001／0.501，與 `FRAMES_w05misuse` 一致 |
| `verify_math.py`／`verify_math.log` | 新增數值與性質的獨立核對（α 最小值、計數、正交時 RSS 可加與 best subset＝forward、固定設計樂觀差 $2d\sigma^2$、$\chi^2_1$、0.0025 vs 0.01、$E[\mathrm{RSS}]=(n-d-1)\sigma^2$、adj $R^2$ 等價式、軟門檻例）：全數 PASS |
| `mathscan.py` | 可見文字中非 `$...$` 數學的啟發式掃描；兩章由 228／476 處降到 33／27，剩餘為 JS 寫入文字、程式、術語與誤判 |
| `detail_shots.js`／`detail_shots.log` | 打開新增收合區、1440／390 px 截圖；mjx-merror 0、無橫向捲動。截圖在 session scratchpad（不入 repo） |

結果摘要：`validate.py` 兩頁 0 失敗（全站 `--net` 只有其他章既有的 4 個外部連結失敗）；FRAMES diff 0；
`check_*`、coverage_check 全過；`browser_check.js` 兩頁 0 問題；`check_lab_rendered` 與 `test_reader_fixes`
的輸出（2 failures）在 HEAD worktree 上相同，屬既存狀況。

Codex（claude-codex-collab，唯讀）job `db56457b-2c3b-4e0a-a6da-9179af2ccdaa`：4 項中度問題全數核實並修正
（軟門檻詞卡補 $X^\top X=I$；adj $R^2$ 不保證因無用變數下降；$\chi^2_1$ 需事先指定、秩加一；bootstrap 尾端分位數失效說法收斂並補矩條件），
另修正既存詞卡「Credit 從大小 3 分歧」為講義的「四變數開始分歧」。紀錄在 `~/.local/share/claude-codex-collab/runs/`（不入 repo）。
