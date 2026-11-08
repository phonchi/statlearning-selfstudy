# 架構諮詢：強化 ISLR 自學網站第 7 章後半與第 8 章

你是獨立審稿人，**唯讀**：不要修改任何檔案，只回報建議。請以繁體中文回答，技術詞彙保留英文。

## 背景
- Repo：`/home/phonchi/statlearning-selfstudy`，繁體中文 ISLR／ISLP 自學網站（教學對象：大學部統計學習課學生）。
- `.html` 是產物；真正的來源：`tools/pages.py`（章節 `Sec` 清單，第 7 章 line 674–702、第 8 章 707–741）、`tools/enrich/enrich_trees.py`（第 8 章 BODIES 與 PAGEJS）、`tools/enrich/enrich_nonlin.py` 與最後一層 `tools/enrich/nonlin_lecture_notes.py`（第 7 章）、`tools/enrich/lib.py`（`info`/`detail`/`proof`/`qa`/`quiz`/`viz` 輔助）。寫作規範在 `tools/STYLE_CONTRACT.md`，交接說明在 `HANDOFF.md`（§5 來源紀律、§27 第 7 章前次充實的做法）。
- 已建好的頁面可直接讀：`beyond_linearity.html`（第 7 章）、`tree_based_methods.html`（第 8 章）。
- 課程講義（英文 PDF，用 `pdftotext -layout` 讀）：`/home/phonchi/nsysu-math524/static_files/presentations/07_Moving_Beyond_Linearity.pdf`、`08_Tree-Based_Methods.pdf`。
- 使用者提供的兩份素材（已複製）：
  - `/home/phonchi/statlearning-selfstudy/tools/verification/ch7-8-trees-ensemble-20261108/consult/coin.html`：51% 硬幣多數決、CLT 常態近似、Condorcet 陪審團定理、連到集成學習。
  - `/home/phonchi/statlearning-selfstudy/tools/verification/ch7-8-trees-ensemble-20261108/consult/chatgpt_msgs.txt`：使用者與 ChatGPT 的教學對話（倒序排列，以 `======== [index]` 分隔；每輪回答常有兩份重複版本）。主題：局部迴歸是「係數隨 x₀ 改變的局部基底展開」；GAM 是模型、backfitting 是演算法、基底展開是表示法，以及 joint fit 與 backfitting 何時同解；partial residual／CR／added-variable／ISLR 成分圖的區別；平滑樣條＝多節點＋曲率懲罰；為什麼用樹（自動抓非線性與交互作用、單調轉換不變、單樹不穩定）；top-down 與 greedy 各省了什麼；類別變數 2^{K−1}−1 與依目標平均排序；Gini 與錯誤率的 70/30 例子；cost-complexity pruning 的 g(t) 數值例與 nested 證明；長樹與剪樹用不同準則。**對話完全沒有談 bagging／RF／boosting。**

## 使用者的要求
全面強化第 7 章後半（smoothing 以後的 loess、gam）與第 8 章；**開頭要強調為什麼要用 tree，以及 ensemble 的直覺**；對話沒提到的就對照講義補遺漏；之後會用「說人話」風格潤稿。

## 已和使用者定案的決策
1. coin.html 改寫成站內 SVG 元件（不用外部 CDN），用精確二項機率；另做 ρ 元件。注意 coin.html 有錯：「Bagging 創造獨立性」「只要 i.i.d. 錯誤率指數下降」，但 bagged trees 高度相關。
2. 第 8 章新增開頭節，放在現有 prologue（把特徵空間切成方塊，Hitters 例）之前，五步主線：①樹做得到什麼（Y=X₁X₂ 兩刀切出交互作用、單調轉換不變、好解釋）②代價：單棵樹不穩定 ③51% 硬幣：獨立投票的放大（元件 A）④相關的代價 Var(平均) = ρσ² + (1−ρ)σ²/B（元件 B）⑤本章路線圖（單樹 → bagging → RF → boosting → BART）。
3. 現有 `why` 小節（投票與大數法則，內容全在收合 `w09-detail-voting-probability`，含舊元件 `w09voteSvg`／`w09voteChart`）的舊元件移除，由開頭元件取代；`why` 保留硬／軟投票、多樣性來源與 VotingClassifier lab。
4. 對話中單棵樹內容全部併入 grow／prune／classtree 既有收合。
5. 第 7 章 loess、gam 各補可見的動機段，對話四項併入既有收合。
6. bagging／RF／boosting 各加一段可見直覺，回扣硬幣與 ρ；不加新數字或新實驗。
7. 講義逐頁比對出的遺漏要補（摘要）：Heart 資料描述與 `Thal:a` 這類質性分割讀法；基因表達例的數字（4,718 基因、349 人、15 類、單樹 45.7%、boosting 深度 1 略勝深度 2 且都勝 RF、單樹 24%）；分類 GAM 規格（year 線性、age 5 df、education 階梯）；圖 8.13 BART vs boosting；圖 8.8 圖例（虛線＝單樹、OOB 碰巧較低）；Wage GAM 4／5 df 與兩種 GAM 差異小；單樹停止規則；講義結論（RF／GBDT 為表格資料先試模型）；RF 小 m 適用強相關預測變數；未剪枝大樹圖 8.4；AdaBoost 與 gradient descent 類比；BART 初值；PDP 用途；圖 7.8 16 df vs 6.8 df；以及數項一句話帶過的小點。
   已知已存在、只需補缺的：類別分割 2^{K−1}−1 與排序證明（`w09-detail-split-search`、`w09proof-leaf`）、g(t) 與巢狀（`w09proof-prune`）、PR／AV／成分圖（`w08-detail-gam-thinplate`）、backfitting 與聯合求解（`w08-detail-gam-backfit`）、ρ 公式已出現在 bagging Q&A、RF 收合、`w09proof-forest-var`、速查表四處。

## 請你回答（架構層級，不必寫成稿）
1. 第 8 章開頭節的編排：放在 Hitters prologue 之前是否合理？讀者還不知道「樹」長怎樣就談 X₁X₂ 兩刀，會不會跳太快？建議的段落順序、哪些正文可見、哪些收合。
2. 兩個元件（硬幣多數決、ρ 地板）的設計建議：參數範圍、平手處理（講義寫「1000 個 51% 分類器 → 約 75%」，精確計算嚴格過半 72.6%、平手算一半 73.6%、≥ 半數 74.7%）、該顯示什麼、怎麼避免學生誤以為 bagging 的樹是獨立的。
3. 冗餘風險：開頭節、`why`、bagging、RF 四處都可能重講 ρ 公式與投票；第 7 章 backfitting／效果圖已有收合。請具體指出哪些既有段落應該刪、改成連結或保留。
4. 第 7 章後半的動機段要怎麼寫才接得上前半（基底展開、線性平滑器 Sy 兩條主線）和第 8 章？
5. 講義遺漏清單裡，有哪些你認為不值得加（太細、會打斷閱讀），或應該放在不同位置？
6. 其他你看到的教學缺口或正確性問題（含 coin.html 與 ChatGPT 對話中的錯誤說法）。

回覆格式：依 1–6 編號，每點給具體建議與理由，引用檔案路徑、section id 或收合 id；總長約 1,000–1,500 字。
