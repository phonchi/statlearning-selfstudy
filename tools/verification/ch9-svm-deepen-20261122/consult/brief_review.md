# 成稿審查：自學網站第 9 章（支持向量機）改寫

你是獨立審稿人，只讀不改。repo 根目錄：`/home/phonchi/statlearning-selfstudy`（靜態教學網站，繁體中文，給統計系大學部學生自學）。

## 背景與規則（使用者定案）
- 老師 2026-11-22 更新了講義 09。使用者要求依「講義為黃金標準」全章稽核並加深第 9 章頁面，並把一段學生與 ChatGPT 的課後問答（30 題）中的疑問補進頁面。
- 範圍規則：**講義文字、ISLP 第 9 章、課程中文 Lab** 可以放正文；**講義內嵌的連結**（筆記在 `sources/`）算範圍內但只能放在收合（`<details>`）；三者都沒有的內容也只能放收合。講義已有的主題：正文 2–4 句直覺，推導與定義放收合。
- 學生文字不寫講義頁碼與 Lab 儲存格編號；用語依台灣教學習慣（擬合、概似、雜訊…）。

## 材料（全部在 repo 內，路徑相對 `tools/verification/ch9-svm-deepen-20261122/`）
- `consult/deck09.txt`：新版講義全文（pdftotext）。`consult/deck09_links.tsv`：講義內嵌連結。
- `sources/*.md`：各連結的閱讀筆記（含原文短引句與抓取狀態；Medium 那篇未讀到）。
- ISLP 第 9 章原書：`~/statslearning/ISLP_website.pdf` 的 PDF 第 375–405 頁（可用 `pdftotext -f 375 -l 405 -layout` 讀）。
- 課程 Lab 文字與輸出索引：`data/source_index/lab_ch9.md`。
- `consult/chatgpt_msgs.txt`：學生問答原文（只當作「學生會問的問題」清單，其中的技術說法不一定正確）。
- `consult/ch9_before.txt`：改寫前七節的學生可見文字；`consult/ch9_after_r1.txt`：改寫後的學生可見文字（收合內容也展開在內，`###` 是標題或收合摘要）。
- 實際頁面：`support_vector_machines.html`（產物）；產生器：`tools/enrich/svm_deepen.py`、`svm_a.py`、`svm_b.py`、`svm_c.py`、`svm_common.py`；詞彙卡 `data/flashcards_zh/ch9.json`；題庫 `data/questions_zh/ch9.json`。
- `consult/audit.md`：改寫規格（作者的計畫，可用來對照有沒有做到，但請自行判斷規格本身是否合理）。
- `verify/verify_svm.py`：作者自己的數值核算。

## 請審查
1. **數學與統計正確性**：公式、推導、條件（例如 primal／dual、KKT、三個等價式與縮放、C 與預算的關係、hinge 與 λ 的換算、Mercer、RBF、核嶺迴歸、dual PCA、SVR、Platt）。指出錯誤、遺漏的條件或過度宣稱。
2. **來源與範圍**：正文裡有沒有只在講義連結或完全沒有來源支持的內容（應放收合或刪除）；收合裡對連結內容的轉述是否忠於 `sources/` 筆記與原文；有沒有把來源的錯誤照抄。
3. **講義對齊**：新版講義的內容（含 p.4 優缺點、p.5 仿射、p.15 三個等價式、p.17–18 primal／dual 與 C、p.19 新措辭、p.26 γ 與 Mercer、p.30–34、附錄 p.37–40）有沒有遺漏或誤讀。
4. **30 題學生問題**：每題頁面是否有正確回答；哪些答得不清楚或答錯。
5. **教學品質**：重複、前後矛盾、引用不存在的元件或段落、讀不懂的地方；詞彙卡與題庫（含答案與回饋）是否正確。

## 回覆格式
用繁體中文。依嚴重度排序列出發現，每條：`[嚴重/中/輕] 位置（節 id 或收合 id＋引句） — 問題 — 證據（來源檔與位置） — 建議修法`。最後一段寫「確認無誤的部分」，列出你實際核對過且沒問題的項目。不要修改任何檔案。
