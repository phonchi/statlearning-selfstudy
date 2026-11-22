# 第 9 章（支持向量機）全章稽核與加深：驗證紀錄（2026-11-22）

決策與實作摘要見 `HANDOFF.md` §32。基準 HEAD：`c009049`。

## 講義更新

- 課程網站 `phonchi/nsysu-math524`：commit `110d1b8` 上線 08（2026-11-17 版）與 09（2026-11-22 版）講義。依使用者指示只 stage 這兩個 PDF。09 新檔 sha256 前 16 碼 `a5f1bb8edb238bd1`。
- 新舊 09 都是 40 頁；`pdftotext` 比對後，文字只差 5 頁，記錄在下方表格。
- 重跑 `tools/index_deck.py 08 09`，`deck_08.tsv`、`deck_09.tsv` 都無變化。

| 頁 | 變更 |
|---|---|
| p.19 | "won't work, no matter what value of const" 改為 "won't find a suitable solution" |
| p.23 | 決策函數改用 $\hat\alpha_i$ |
| p.24 | 改的是二次映射展開式的排版位置，數學內容不變 |
| p.25 | 只有排版差異 |
| p.34 | 刪除 SVR 那一句；"regression" 仍連到林軒田 206 handout |

## 素材

| 路徑 | 內容 |
|---|---|
| `consult/deck09.txt` | 新版講義的 `pdftotext -layout` |
| `consult/deck09_links.tsv` | 講義的 22 個內嵌連結（以 PyMuPDF 抽出） |
| `consult/chatgpt_msgs.txt`（不入 repo） | 使用者提供的 ChatGPT 分享對話（`chatgpt.com/share/6b027cee-…`，標題「SVM優點解釋」），從分享頁 HTML 的 `streamController.enqueue` 資料解出並去重。共 30 個使用者區塊，其中 1 個是系統替代文字，實際 29 問。只當作「學生會問的問題」清單 |
| `sources/*.md`、`sources/INDEX_{A,B,C}.md` | 講義連結的閱讀筆記，由三個 subagent 並行讀取，共 24 份。Stack Exchange 三頁的網頁回 403，改用官方 API 讀取；Medium（講義 p.33）被 Cloudflare 擋下回 403，未讀，頁面不引用其內容 |
| `consult/audit.md` | 全章逐段稽核與改寫規格，含 30 題的逐題處置 |
| `consult/ch9_before.txt`、`ch9_after_r1.txt`、`ch9_after_r2.txt` | 改寫前、第一輪、第二輪的學生可見文字（`consult/sec_text.py` 產生） |
| `consult/old_bodies.json`（不入 repo） | 上游各層的 BODIES 快照 |

## 範圍規則（使用者定案）

| 來源 | 可放的位置 |
|---|---|
| 講義文字、ISLP 第 9 章、課程中文 Lab | 正文 |
| 講義內嵌連結 | 範圍內，但只放收合 |
| 以上皆無 | 只放收合 |

這條規則套用到全章既有正文，逐段稽核，不是只管新增內容。不加新元件，改加題目與詞彙卡。

## 稽核發現的既有問題

- **核心公式被收進收合**：上游的閱讀層把講義的核心內容包進了收合，這次全部提回正文。受影響的有：
  - ISLP 式 9.9–9.11
  - ISLP 式 9.12–9.15
  - 式 9.25
  - 講義的二次映射例
  - 講義 p.31 的四句比較
- **multiclass 節描述早已移除的元件**：有三句提到不存在的元件，已刪除。
- **SVR 收合的排版錯誤**：`&y;`、`&w;` 是 §27 記錄過的 `&`＋字母問題，已修正。
- **多類別表格有無出處的列**：「K 很大時考慮 OVA」沒有來源，已刪除。

## 撰寫方式

- **新層 `tools/enrich/svm_deepen.py`**：掛在 `enrich_svm.py` 最後，整節覆寫七節。內容分在三個模組，由三個 fork 並行撰寫：
  - `svm_a.py`：prologue、maxmargin
  - `svm_b.py`：soft、hinge
  - `svm_c.py`：kernel、multiclass、vslogit
- **共用工具 `svm_common.py`**：`grab_*` 系列從上游取出既有元件、收合與 quiz，id 一律不變。
- **組裝層的兩份清單**：`STALE` 檢查舊句不得殘留；`FIXES` 更正沿用的上游段落，每個字串必須恰好出現一次。
- **`SVM_SKIP=1`**：讓 `enrich_svm.py` 略過新層，取上游快照時使用。

## 驗證

| 檔案 | 結果 |
|---|---|
| `verify/verify_svm.py`、`verify_svm.log` | 54 項 PASS：距離與投影、仿射方向空間、縮放不變性、slack 三式不變、dual 代入與強對偶、預算可行性、多項式維度、二次核、RBF 泰勒、Gram 半正定、核嶺恆等式、λ=0 最小範數、dual PCA、C 單調性、變數與限制計數 |
| `build_r4.log` | 建置成功（最終版） |
| `validate_r4.log` | 4 個失敗，都是其他章既有的外部連結（PSU、neptune、causeweb、含空格的 GitHub 網址），§31 也有記錄；本頁只有 SIZE 警告（約 330 KB） |
| `checks_r4.log` | reader_contract、reading_flow、teaching_scope、taiwan_wording、visual_claims、contrast 全過 |
| `check_lab_rendered.log` | 8 個失敗（model_selection 2、p2 1、resampling 5），與 HEAD 相同，第 9 章程式卡全部通過 |
| `browser_r4.log`、`browser_full_r2.log` | 第 9 章與全站的 browser_check 都是 0 問題 |
| `shots.js`、`shots_r2.log`、`shots_r3.log`（截圖不入 repo） | 展開全部收合後：桌面 1440 與手機 390 的 mjx-merror 都是 0、沒有橫向捲動、沒有 pageerror。手機上的「超出寬度」是長公式在公式框內水平捲動（STYLE_CONTRACT §11 允許） |

## 審閱（同一份只含素材的 brief：`consult/brief_review.md`）

| 審稿人 | job ID／方式 | 第一輪 | 複核 |
|---|---|---|---|
| Astra（Codex `gpt-6-astra`，`collab.py`，唯讀） | 第一輪 `72e22753-eca1-4209-bfa7-cd30ad939d7f`；複核 `89cfb9f3-4a2b-4968-ab81-732d6fc778f1`；第 3 輪 `ac7b3d94-2caf-4ce9-bb8c-c4b27907d912`（皆以 `--resume-job` 續接同一 session） | `consult/astra_review.md`：15 條（1 嚴重、10 中、4 輕） | `consult/astra_recheck.md`：需再修（5 條，含退化等號、錯誤的逐點單調句、表格「幾乎可分」、RBF 元件沒有虛線、qSv 題幹）→ `consult/brief_recheck2.md` 處理 → `consult/astra_recheck2.md`：**可定稿**、無新發現 |
| Fable（Claude Fable 5.1，Agent `model: "fable"`） | 同一個 subagent 續問 | `consult/fable_review.md`：6 中、11 輕 | `consult/fable_recheck.md`：**可定稿**，4 條輕微意見已在第 3 輪一併處理 |

第一次送 Astra 時，`--add-dir` 的路徑打錯，supervisor 在啟動前就回報 failed，Codex 沒有執行。修正路徑後重送，即上表的 job。

意見的處理逐條列在 `consult/brief_recheck.md`（第 2 輪）與 `consult/brief_recheck2.md`（第 3 輪）。有兩條不採納：

- **A9「三個等價式移進收合」**：講義 p.15 本身就列出這三式，屬於可放正文的講義文字。Astra 第 2 輪仍認為正文過長，第 3 輪確認內容正確；是否再縮短交由使用者決定。
- **F17 的兩句正文小句**：都是講義文字的直接解釋。

## 已知、刻意未處理

- 本頁 327 KB，超過 300 KB 的 SIZE 建議上限；依契約 §11，不因警告刪除必要教材。
- Medium 那篇（講義 p.33 機率估計）未讀，頁面只引 scikit-learn 文件的 Platt 說明。
- 講義 p.38 感知器的更新式方向相反，頁面已說明，但尚未回報老師改講義。
