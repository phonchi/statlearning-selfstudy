# 設計稿 v1（綜合 Astra 與 Fable 第一輪建議後）——請挑毛病

你是唯讀審稿人，不要修改任何檔案。背景同前一份 brief：
`/home/phonchi/statlearning-selfstudy/tools/verification/ch7-8-trees-ensemble-20261108/consult/brief_arch.md`
（Repo `/home/phonchi/statlearning-selfstudy`；第 8 章 `tree_based_methods.html`、第 7 章 `beyond_linearity.html`；來源 `tools/enrich/enrich_trees.py`、`tools/enrich/nonlin_lecture_notes.py`、`tools/pages.py`。）
講義文字已抽成純文字：`/home/phonchi/statlearning-selfstudy/tools/verification/ch7-8-trees-ensemble-20261108/consult/deck07.txt`、`deck08.txt`（每頁以 form feed 分隔）。

使用者已拍板：新節放在 Hitters `prologue` **之後**、`grow` 之前。

## 第 8 章

**新節 `motive`**（h2 暫定「樹抓得到交互作用，卻不穩定：為什麼要種一片森林」），全部正文可見，推導收合：
1. 樹做得到什麼：回扣 Hitters（Hits 只在 Years ≥ 4.5 時有作用 → 自動的交互作用）；階梯近似非線性；單調轉換不變（X<10 ⇔ Z<(10−μ)/σ）；類別水準分組；好解釋。接著兩個限制：X₁X₂ 的四象限正負號要深度 2（3 次分裂、4 葉），而且 X₁、X₂ 獨立對稱時，第一刀單看 X₁ 或 X₂ 都沒有 RSS 改善（E[X₁X₂|X₁]=0），greedy 可能根本不切；平滑關係要很多刀；GAM 要自己指定交互作用（連第 7 章 gam）。原 prologue 的 `w09-detail-tree-compare` 表移到這裡。
2. 代價：單棵樹不穩定（上層分裂一換，下面全換）、外插差、準確度通常輸給最好的方法（講義 p.3）。原 prologue 最後那段「最後那一列是…後六節」刪掉，改一句接到本節。
3. 硬幣與獨立投票（元件 A `w09coinSvg`）：正文顯示二項尾機率公式。p 滑桿 0.30–0.70；M 只取奇數，1–10001，用對數刻度滑桿＋「M=1001」「M=10001」快捷鈕。上圖：答對票比例 k/M 的二項 PMF 長條加 0.5 過半線（看分佈變窄）；下圖：集成正確率對 M（對數軸），畫目前 p、鏡像 1−p，以及 ρ=1（完全相同的分類器）停在 p 的水平線。講義的「1000 個約 75%」：M=1001 為 73.7%，正文一句說明 M=1000 時嚴格過半 72.6%、平手擲硬幣 73.6%，講義的 75% 是概數。收合：CLT 的 z=√M(0.5−p)/√(p(1−p))、Condorcet 陪審團定理、Hoeffding 上界 exp(−2M(p−½)²)，以及 coin.html 的兩個錯誤前提。provenance `illustrative`。
4. 相關的代價（元件 B `w09rhoSvg`）：正文顯示 Var(平均)=ρσ²+(1−ρ)σ²/B（固定 x、等變異、等相關）。ρ 滑桿 0–1、B 滑桿 1–1000（對數）；畫 Var/σ² 對 B（對數軸）、ρ 地板虛線、ρ=0 參考曲線。旁邊直接寫：bootstrap 不會產生新的獨立資料；A 是 ρ=0 的理想；兩兩相關係數不足以決定投票正確率，所以 B 只講平均預測的變異。
5. 路線圖（小表）：bagging 壓 (1−ρ)σ²/B、RF 壓 ρ、boosting 走另一條路（序列、小樹、修正殘差，主要降偏差，不是平均同分佈的預測器）、BART。收尾一句：講義結論，RF 與 GBDT 是表格資料應先試的模型。

**其他節**
- `prologue`：刪結尾那段與比較表（移走），修「PART 05」為節名連結。
- `why`：h2 改「多樣性從哪裡來：不同演算法、投票與軟投票」。刪公式、舊元件 `w09voteSvg`/`w09voteChart`（含 PAGEJS）、75% 段、獨立性 info 的重複部分；四種多樣性來源 ①–④ 升為正文（用節名連結取代 PART 編號）；「投票改善需要錯誤不完全同步」只留硬／軟投票段，收合改名「硬投票與軟投票的細節」；加講義 p.30「集成常在專案尾聲使用、競賽冠軍多半是集成」一句。
- `grow`：正文補 top-down 與 greedy 的區別（真正省計算的是 greedy）；停止規則（每區不超過 5 筆）；區域理論上可以任意形狀，選方塊是為了好算好解釋。`w09-detail-split-search` 去掉重複的兩段（類別分割與 ID3/C4.5 各講兩次），補 K=4 的 7 種分法與 one-versus-rest 只看 K 種會漏掉 {A,B}|{C,D}。
- `prune`：「這個解法是錯的」改成有條件；補直接限制深度／葉大小（講義 p.15）一句；演算法 8.1 步驟 1 補停止條件；收合補 g(t) 數值例（A：16/10/2 葉、B：22/18/2 葉、root：60/28/4 葉 → g=6, 4, 32/3，先剪 B α₁=4；root 重算 14；剪 A α₂=6；最後 α₃=22）；「最小化 g(t) 不等於固定 α 下最小化成本差」；分類樹剪枝可改用錯誤率（ISLP）。`w09proof-prune` 補巢狀證明：令 d_t=R(t)−R(t_L)−R(t_R)，C_α(T)=R(root)+α+Σ_{t∈I(T)}(α−d_t)，I(T) 是對祖先封閉的內部節點集合；I₁、I₂ 各為 α₁<α₂ 的最佳解，由模函數性與 I₁∪I₂、I₁∩I₂ 仍合法，推出 I₂⊆I₁。「可預測」＝每棵子樹的成本是 α 的直線，下包絡只有有限個斷點。
- `classtree`：正文補加權不純度一般式；收合補 70/30 例（E 0.30→0.30、G 0.42→0.40、熵以 e 為底 0.611→0.587）、Heart 資料描述（303 人、HD、13 個預測變數、CV 選 6 葉）、`Thal:a`/`ChestPain:bc` 的讀法、兩者皆可微一句。
- `bagging`：正文開頭改成回連 motive，不重講 σ²/n；「B 個無偏估計的平均還是無偏」改「偏差不變」；「B 太小才會欠擬合」改「變異還沒壓下來」；「不必再做交叉驗證」改有條件；圖 8.8 圖說補：虛線是單棵樹的測試誤差、RF 用 m=√p、OOB 誤差這次碰巧明顯較低。
- `rf`：修 `w09-detail-extra-trees` 開頭（「原因很具體：」後面接不上，公式重貼刪除）；刪「減少 max_features…清楚表示」那段重複；正文補 Heart 13 取 4、大量強相關預測變數時小 m 有幫助；收合補基因表達例（4,718 基因、349 人、15 類、取變異最大的 500 個、單樹錯誤率 45.7%）。
- `boosting`：正文一段對比直覺；講義「each tree is … independent of the other trees」譯成「各自建立」而非「獨立」；`w09-detail-boost-parameters` 補二元基因例（癌 vs 正常、λ=0.01、深度 1 略勝深度 2、都勝 RF、單樹 24%），明寫與 RF 那個 15 類例子不是同一個問題。
- `stacking`（BART 收合）：圖 8.13 一句（BART 過 100 輪 burn-in 後穩定、boosting 數百輪後開始過擬合）；BART 初值一句。
- 全章 PART 編號改節名連結。

## 第 7 章
- `smooth`：一句「平滑樣條＝很多節點＋曲率懲罰」，df 滑桿說明補圖 7.8 的 16 df vs LOOCV 6.8 df 差異不大。
- `loess`：開頭動機 3–4 句（基底線走到極端：係數 β(x₀) 隨位置變；平滑器線：ŷ=Ly、df=tr L，span 扮演 λ；固定 span、非穩健版才成立）；結尾一句接第 8 章（高維鄰域沒點；樹改由資料決定鄰域）。`w08-detail-local-calculation` 補等價權重 w*_i(x₀) 可為負、f̂(x₀)=β̂₀(x₀)。
- `gam`：開頭動機 3–4 句（兩條線會合：固定基底串接＝聯合最小平方；任何一維平滑器輪流擬合偏殘差＝backfitting；代價是加法、沒有交互作用→第 8 章）。合併 `w08-detail-gam-backfit` 裡重複的兩套更新步驟；把「四種效果圖」從 `w08-detail-gam-thinplate` 拆成獨立收合放到 GAM 圖旁，補 partial residual＝CR plot、AV plot 不同、ISLR 圖是成分圖、相關預測變數時會誤導、PDP 的用途；修 GAM 圖說把成分圖叫「偏依賴圖」。`w08-detail-gam-classification` 補 year 線性、age 5 df 平滑樣條、education 階梯，以及「age、education 的效果遠大於 year」；`w08-detail-gam-lab` 補 year 4 df、age 5 df，與這個例子裡平滑樣條版和自然樣條版差異很小。

## 請你回答
只回覆你**不同意或擔心**的點（每點一句理由＋建議），以及你認為遺漏的高優先項；同意的不用列。300–600 字。
