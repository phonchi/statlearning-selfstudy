# 續作說明

**十章全部完成**，`validate.py` 0 失敗 0 警告、`browser_check.js` 0 問題。
這份檔案只剩「上線之後」的清單與後續維護指引。

## 狀態

| 頁面 | 大小 | 元件 | 詞彙卡 | 題庫 |
|---|---|---|---|---|
| `introduction`（ch1） | 155 KB | 4 | 23 | — |
| `statistical_learning`（ch2） | 191 KB | 8 | 26 | — |
| `linear_regression`（ch3） | 261 KB | 9 | 28 | 6 |
| `classification`（ch4） | 218 KB | 7 | 28 | 6 |
| `resampling_methods`（ch5, pilot） | 162 KB | 8 | 23 | — |
| `model_selection`（ch6） | 205 KB | 10 | 27 | — |
| `beyond_linearity`（ch7） | 245 KB | 12 | 28 | — |
| `tree_based_methods`（ch8） | 256 KB | 10 | 30 | 6 |
| `support_vector_machines`（ch9） | 240 KB | 9 | 26 | — |
| `unsupervised_learning`（ch12） | 255 KB | 9 | 30 | — |

## 續作步驟

```bash
cd ~/statlearning-selfstudy
# 1) 先讀契約
cat tools/STYLE_CONTRACT.md
# 2) 讀唯一的參考範例（pilot，已通過所有檢查）
less tools/enrich/enrich_resampling.py
# 3) 讀該章的來源（都已抽好，不要憑印象寫）
cat  data/source_index/deck_NN.tsv     # 講義大綱 → 決定 PART 清單
less data/source_index/lab_chN.md      # lab 的程式碼與老師實跑的輸出
grep -P "^N\t" data/source_index/islp_chapters.tsv   # 該章 PDF 頁範圍
# 4) 寫 tools/enrich/enrich_<page>.py 與（需要時）tools/frames/gen_<page>.py
# 5) 套用並驗收（兩個都要全綠）
python3 tools/enrich/enrich_<page>.py
python3 tools/inject_data.py <stem>
python3 tools/build_page.py <stem>
python3 tools/validate.py --page <stem>
node    tools/browser_check.js <stem>
```

## 已完成七章的共同作法（新章照這個模式）

每章一支 `tools/enrich/enrich_<page>.py`（內容）＋ 一支 `tools/frames/gen_<page>.py`
（烘焙資料，用 pinned 環境 `conda run -n m524` 跑）＋ `data/flashcards_zh/chN.json`。
`.html` 全部由工具產生，**不要手改**。

## 已上線

- 自學站：https://phonchi.github.io/statlearning-selfstudy/ （repo `phonchi/statlearning-selfstudy`，
  public、`main` / root、有 `.nojekyll`、無 LICENSE 無 `_config.yml`，比照 `ds-python-selfstudy`）
- 課程網站 `nsysu-math524` 已加：`_data/previous_offering.yml` 的 Fall 2025 →
  `nsysu-math524-2025`，以及 `materials.md` 的自學站連結
- 封存站：https://phonchi.github.io/nsysu-math524-2025/
- 上線後 `validate.py --net` 56 個外部連結全通；十頁互連在 GitHub Pages
  （大小寫敏感）上也全部 200

## 後續維護

改內容一律改 `tools/enrich/enrich_<page>.py` 或 `data/*.json`，然後：

```bash
python3 tools/enrich/enrich_<page>.py     # 內容
python3 tools/inject_data.py <stem>       # 詞彙卡／題庫
python3 tools/build_page.py               # GEN 區段（改了 pages.py 或 template/ 就要全跑）
python3 tools/build_index.py              # index.html 與 README 章節表
python3 tools/validate.py --net           # 20 項具名檢查
node    tools/browser_check.js            # 瀏覽器逐項（含手機版與 CDN 失效）
```

`.html` 是產物，**不要手改**——`build_page.py` 會用 sha256 比對 GEN 區段並報錯。

還沒做的一件事：對每頁散文跑 `speak-human-tw` 檢查去 AI 味與中國用語。

## 還需要老師提供才能做的（跟自學站無關，屬課程網站）

- `nsysu-math524/_config.yml` 的 `course_semester` 改 Fall 2026
- `_data/hw_policy.yml` 的 elearn 課程 ID（現在是 Fall 2025 的 `course/20328`）
- `_data/people.yml` 的新學期助教
- `_lectures/*.md` 的新學期上課日期
- 要不要把 `Mid_term_2025.zip` 補進 `_lectures/06_week6.md` 的歷年期中考清單
