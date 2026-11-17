# 第 8 章集成學習全面加深加廣：驗證紀錄（2026-11-17）

決策與實作摘要見 `HANDOFF.md` §31。基準 HEAD：`2025639`。

## 素材

| 路徑 | 內容 |
|---|---|
| `consult/deck08.txt` | 現行講義 `~/nsysu-math524/static_files/presentations/08_Tree-Based_Methods.pdf` 的 `pdftotext -layout`；集成部分 p.30–62、附錄 p.63–80 |
| `consult/chatgpt_msgs.txt`（不入 repo） | 使用者提供的 ChatGPT 分享對話（`chatgpt.com/share/6afbd835-…`），從分享頁 HTML 的 `streamController.enqueue` 資料解出、去重；37 個使用者提問。只當「學生會問的問題」清單，技術論斷一律回到論文與官方文件 |
| `consult/source_brief.md`、`sources/*.md`、`sources/INDEX.md` | 講義 p.31–80 的約 40 個連結＋當學期條目（`_lectures/11_week11.md`）的 AI-Assisted Statistics 第 6 章與 StatQuest XGBoost，共 55 份來源筆記（五個 subagent 並行讀取），每份記抓取狀態、原文短引句與位置 |
| `consult/ch8_ensemble_current.txt` | 改寫前六節的學生可見文字 |
| `consult/ch8_ensemble_r2.txt` | 改寫後十節的學生可見文字（`consult/sec_text.py` 產生） |

抓取失敗（只列在延伸閱讀，不引用內容）：Medium 三篇與 TDS（403）、Taylor & Francis 的 Fisher 1958（403，只有書目）、neptune.ai（TLS 憑證過期）。部分取得：Stack Exchange 各題（網頁 403，改用官方 API）、IEEE Ho 1998（只有摘要）、Springer random patches（改讀作者 OA 版）、PSU（憑證鏈錯誤，改讀 Wayback）、datasketches（講義網址 404，改用現行網址，頁面上的連結已更新）。`validate --net` 的 4 個連結失敗（neptune、PSU、另兩個在第 7、3／4 章）在 HEAD 上就存在。

## 諮詢與審查（Herdr pane，紀錄在 `~/.local/share/claude-codex-collab/herdr-runs/`）

| 審稿人 | job ID | 輪次與原文 |
|---|---|---|
| Gemini（`agy`，`gemini-3.8-flash-high`） | `0deb8067-0c13-436a-96de-b3bce886aac8` | `consult/gemini_arch.md` → `gemini_review.md` → `gemini_recheck.md` |
| Astra（Codex gpt-6-astra） | `81bb9169-f106-4288-9fde-f46511cff316` | `consult/astra_arch.md` → `astra_review.md` → `astra_recheck.md` |
| Fable（Claude Fable 5.1） | `c5b4346b-83d0-4959-b0e0-ccc0ced37c07` | `consult/fable_arch.md` → `fable_review.md` → `fable_recheck.md` |

同一個 pane 連續三輪（架構諮詢 `consult/brief_arch.md`、成稿審查 `brief_review.md`、複核 `brief_recheck.md`）。三方架構意見的綜合與採納理由在 `consult/synthesis.md`；成稿審查意見的處理逐條列在 `consult/brief_recheck.md`。三方複核結論：Fable、Gemini「確認無誤」；Astra 另提 3 處未同步（重要度正文的「只是換尺度」、successors 開頭「每一刀都挑增益最大」、比較表的 MVS 預設條件），已修正。

使用者指示「三方意見有共識就直接寫」，分節依共識與二比一多數定案，未再回問。

## 撰寫方式

主線寫 `ensemble_deepen.py`（組裝與殘留字串檢查）、`ens_common.py`、預覽工具 `ens_snapshot.py`／`ens_preview.py`，並更新 `pages.py`、詞彙卡、題庫；三個 fork 分支分別寫 `ens_a.py`（why、bagging、rf、importance）、`ens_b.py`（boosting、modern、splitsearch＋元件 w09xgb、w09split）、`ens_c.py`（categorical、successors、stacking＋元件 w09stack）。分支 A 曾把 2026-09 依講義刪除的置換重要度切換（generator 自算數字）放回，主線依規範撤回。

## 驗證

| 檔案 | 結果 |
|---|---|
| `verify/verify_a.py` | 17 項 PASS：OOB 有限樣本比例、軟投票例、9/13、ESL 圖 15.7 超幾何機率、0-1 損失反例、lab 14.63→14.61 |
| `verify/verify_b.py` | 78 項 PASS：StatQuest 增益與葉值（λ=0、1）、一步 Newton、g／h 數值微分、AdaBoost η=½ 與 ESL 10.1 等價、加權分位例、元件 w09split 的 LCG 重算、22 個 lab 輸出字串逐字比對 |
| `verify/verify_c.py` | 23 項 PASS：講義目標編碼表、留一反例、CatBoost 官方 rock 表逐列、類別排序增益、GOSS 補權、BART 葉數先驗與 σ_μ、速度倍數 |
| `validate_final.log` | 0 失敗（SIZE 警告：本頁 456 KB，超過 300 KB 建議上限；契約 §11 允許不因警告刪必要教材） |
| `checks_final.log` | reader_contract、reading_flow、teaching_scope、taiwan_wording、visual_claims、contrast 全過；`check_lab_rendered` 8 個失敗（model_selection 2、p2 1、resampling 5）與 HEAD 相同，第 8 章程式卡全部通過 |
| `browser_final.log` | 全站 browser_check 0 問題 |
| `shots.js`、`shots_final.log`（截圖不入 repo） | 展開全部收合：桌面 1440 與手機 390 皆 mjx-merror 0、無橫向捲動、無 pageerror。手機上「超出寬度」的元素經 `wide.js`／`wide2.js` 確認為 MathJax 隱藏輔助標記與可橫向捲動表格內的公式；唯一真正被截斷的 ESL 演算法 10.3 行內長式已改成獨立公式 |
| `shots_widgets/` | 三個新元件預設狀態截圖，讀值與核算一致 |

## speak-human-tw（使用者已核准「直接潤稿」，跳過事前確認）

掃描新寫的約 5 萬字：破折號 2 處、無套話與「不是 A，而是 B」句型。多數「……，不是……」是在澄清常見誤解，屬必要的邏輯否定而保留。修改 6 處：

| 原句 | 為什麼改 | 改成 |
|---|---|---|
| scikit-learn 的 random forest 分類器就是平均機率，不是數票。 | 修辭性對比 | scikit-learn 的 random forest 分類器用的就是平均機率。 |
| 差距並不大；這裡要看的是流程，不是排名。 | 修辭性對比 | 差距並不大；這個例子用來看流程，排名不足為據。 |
| 預設值是起點，不是答案。 | 格言式對比 | 預設值只是起點。 |
| 真正有用的是「對很多棵樹」取平均 | 強調墊字 | 有用的是「對很多棵樹」取平均 |
| …只是 AdaBoost 一次加進一個新的分類器，不是調整同一個模型的參數。 | 修辭性對比 | …差別在 AdaBoost 每一輪加進一個新的分類器，梯度下降則是調整同一個模型的參數。 |
| 精確搜尋真正的成本是每一層仍要掃過所有資料。 | 強調墊字 | 精確搜尋的主要成本是每一層仍要掃過所有資料。 |

## 已知、刻意未處理

- 沿用的 AdaBoost 元件：data-source-note 寫 16 點、狀態列寫「1/18」，是上游既有的不一致（本次未動元件 JS）。
- XGBoost 元件不實作 `min_child_weight` 門檻，側欄明寫示意設定相當於 0。
- CatBoost `border_count` 的預設值沒有在來源中核對，比較表只列參數名。
