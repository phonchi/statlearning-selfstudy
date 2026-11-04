# 00C 改版與 Ch05 bootstrap 修正（2026-11-04）

| 檔案 | 內容 |
|---|---|
| `rerun_boot_se.py` → `outputs.json`、`run.log` | 原樣重跑 Ch05 lab 儲存格 59/65/67/71/75：依標籤抽樣得 0.731/0.00609（一份重抽 690 列，Auto 有 147 列同名）；依位置抽樣得 0.848807/0.007352，與 ISLP 書印出的 0.8488/0.0074 相同 |
| `check_fix.py` → `check_fix.json` | 只改儲存格 59 時，55、61、69 的輸出不變 |
| `check_alpha_iloc.py` → `check_alpha_iloc.json` | `alpha_func` 改 `.iloc` 後，55、57、61 的輸出不變 |
| `patch_lab.py`、`patch_alpha_iloc.py` | 修改 `~/nsysu-math524/static_files/presentations/Ch05-resample-lab-zh.ipynb`：儲存格 53、59 程式，72 文字，補存 61/71/75 輸出 |
| `env.txt` | 重跑環境（Python 3.13.12、ISLP 0.4.0、statsmodels 0.15.0、scikit-learn 1.8.0、scipy 1.17.1；numpy 2.4.3、pandas 3.0.2）。與課程 Colab 不同，獨立佐證是逐位重現 ISLP 書中數字 |
| `capture_sections.cjs` → `sections/` | 00C 每節展開全部收合後的桌機（1280）與手機（390）截圖；兩者皆無水平溢出 |
| `shots/` | `node tools/browser_check.js 00c_ai_assisted resampling_methods`：0 個問題 |
