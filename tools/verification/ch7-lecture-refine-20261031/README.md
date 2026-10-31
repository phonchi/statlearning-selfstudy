# 第 7 章依講義與教學筆記充實（2026-10-31）驗證紀錄

決策見 `HANDOFF.md` §27。

| 檔案 | 內容 |
|---|---|
| `verify_math.py`／`.log` | 新增內容的獨立數值核對（m524）：階梯函數共線、CI 例與 `get_prediction`、KKT 與換基底、截斷冪與 B-spline、Reinsch 懲罰矩陣與 `FRAMES_w08shrink`、$S$ 的兩種寫法、最小彎曲能量、局部迴歸 $\operatorname{tr}L$ 與 $\operatorname{tr}(LL^T)$。全數 PASS |
| `check_polish.py`／`.log` | 潤稿前後比對數學、數字、網址、id、`<code>`；唯一差異是一條行內公式改成獨立顯示（手機版過長） |
| `detail_shots.js`／`.log` | 展開全部收合，1440／390 px：mjx-merror 0、無橫向捲動；W2 與 W3 的實際數值 |

諮詢與複查（紀錄在 `~/.local/share/claude-codex-collab/runs/`，不入 repo）：
- 收合取捨：GPT-6 job `76e9faf1-d330-4c4b-9504-9e929292153b`，加上 Fable。
- 獨立讀者：GPT-6 job `f2c82b94-1a7a-41b0-8827-fa6b2361ed5b`，加上 Fable。Fable 的兩項未採納，都已核實：薄板樣條確實在講義第 49 頁（它的 PDF 文字抽取沒抓到）；方框折動 1.06 以元件實際演算法為準（它用不同的端點與取整算得 1.21）。

未驗證：Stack Exchange 與 Math.SE 的連結擋抓取，未讀原文，相關內容依使用者筆記、ESL 與官方文件。圖 7.10 圖例來自局部二次 $\operatorname{tr}(LL^T)$ 是推測，頁面已明寫。
