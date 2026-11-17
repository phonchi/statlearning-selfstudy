第 8 章「集成學習」十節教材成稿審查報告

本審查針對已渲染文本（ch8_ensemble_new.txt）、生成程式（ens_a.py、ens_b.py、ens_c.py）、互動元件（w09xgb、w09split、w09stack）以及完整頁面 tree_based_methods.html，對照講義
08、lab 索引、來源筆記（sources/）與 STYLE_CONTRACT.md 進行獨立核對。

整體而言，成稿品質極高：
1. 架構嚴謹：將原 6 節平滑重組成 10 節（why、bagging、rf、boosting、importance、modern、splitsearch、categorical、successors、stacking），既有章節 ID 完整保留，BART
依指示收斂於附錄收合。
2. 正文與收合分工貫徹：正文主打「幾何直覺＋核心公式＋具體短例」，推導（如 AdaBoost 等價性、Taylor 二階展開、Fisher 分割定理、BART 完整 MCMC 等）皆收納於預設收合中。
3. 數值精準：StatQuest 算例、CatBoost 官方 Ordered TS 算例、Fisher 類別投影算例皆經過精確數值驗證。
4. 完整覆蓋學生疑惑：學生問答的 37 個核心問題均在相應章節的正文或收合中獲得正面解答。

以下依嚴重度條列待修正項目，並附上確認無誤的重點清單。
──────
## 一、錯誤（嚴重度：高）

### 1. boosting 節推導收合中的跨節前向參照錯誤
• 位置：boosting（PART 09）的 GRADIENT_DETAIL 收合內，原句開頭：「XGBoost 的葉值只是在分母多加一個 λ，見下一節。」
• 問題：在本次十節架構中，boosting 的「下一節」是 PART 10 importance（變數重要度），而非 XGBoost（PART 11 modern）。這會導致讀者跳至下一節時撲空，造成閱讀混亂。
• 證據：synthesis.md 第 1 節已確定順序：boosting（PART 09）→ importance（PART 10）→ modern（PART 11）。
• 建議改法：將「見下一節」改為「見後續 XGBoost 一節」或「見現代 GBDT（XGBoost）一節」。

### 2. modern 節正文與收合中的跨節後向參照錯誤

• 位置：
1. modern（PART 11）主文段落，原句開頭：「logistic 的葉值和上一節的一步 Newton 葉值只差分母裡的 λ。」
2. modern 收合 XGB_LOGISTIC 內，原句開頭：「λ = 0 時就是葉內殘差平均，和上一節的梯度提升一致。」
• 問題：此處「上一節」直接指向了 PART 10 importance，但「一步 Newton 葉值」與「梯度提升的一般損失框架」實際上位於 PART 09 boosting。
• 證據：Newton-Raphson 一步更新公式 γⱼₘ = ∑ r/ ∑ p(1 - p) 出現在 boosting 的 GRADIENT_DETAIL 收合中，importance 全文並無該公式。
• 建議改法：
• 主文改為：「logistic 的葉值和 Boosting 一節 的一步 Newton 葉值只差分母裡的 λ。」
• 收合內改為：「λ = 0 時就是葉內殘差平均，和 Boosting 一節的梯度提升一致。」

### 3. importance 節主文的時序參照瑕疵

• 位置：importance（PART 10）主文段落，原句開頭：「下一節之後的 boosting 模型也用同樣的方式讀重要度；BART 另有...」
• 問題：Boosting 的基本概念與 AdaBoost/GBDT 在前一節（PART 09 boosting）已經講述完畢；此處要指涉的是後續登場的現代 GBDT 套件（XGBoost、LightGBM、CatBoost）。用「下一節之後的
boosting 模型」語意略顯倒置且易引發疑惑。
• 證據：講義 p.45–46 先講 boosting，p.50 講 feature importance，p.51 起進入現代套件。
• 建議改法：改為：「後續介紹的現代 GBDT 模型（XGBoost、LightGBM、CatBoost）也沿用同樣的邏輯讀取重要度；BART 另有...」。
──────
## 二、誤導（嚴重度：中）
### 1. modern 節在 λ = 0 與 λ = 1 計算數值的接續誤導

• 位置：modern（PART 11）接在互動元件 w09xgb 下方的主文，原句開頭：「把 λ 拉到 1，左葉的值減半成 −5.25，StatQuest 的 Gain 降到 62.49（論文式 31.24）。乘上 η = 0.3
之後，第一筆的預測從 0.5 變成 0.5 + 0.3 × (-10.5) = -2.65。」
• 問題：前一句才說明將 λ 拉到 1，左葉值變為 -5.25；緊接著下一句算式卻使用 -10.5（這是 λ = 0 的左葉值）。依序閱讀的學生會直覺認為是接續 λ = 1 進行預測更新，因而誤算為 0.5 + 0.3 ×
(-5.25) = -1.075，產生認知斷層與混亂。
• 證據：若 λ = 0，w_L^* = -10.5 ⟹ ŷ = 0.5 + 0.3 × (-10.5) = -2.65；若 λ = 1，w_L^* = -5.25 ⟹ ŷ = 0.5 + 0.3 × (-5.25) = -1.075。
• 建議改法：明確標記情境，拆開說明：
「（回到預設 λ = 0）乘上 η = 0.3 之後，第一筆的預測從 0.5 更新為 0.5 + 0.3 × (-10.5) = -2.65；若在 λ = 1 下，則更新為 0.5 + 0.3 × (-5.25) = -1.075。」
### 2. splitsearch 節前端 JS 變數名稱與 DOM ID 衝突隱患
• 位置：tools/enrich/ens_b.py 第 303 行（HTML）與第 520 行（JS）：
• HTML：<span id="w09splitN">—</span>
• JS：const w09splitN = 40; 與 set('w09splitN', String(cand.length));
• 問題：JS 頂層常數 w09splitN 代表樣本總數 N = 40，但 DOM 元素 ID 也被命名為 w09splitN，且 JS 內將此 span 賦值為候選切點數量（cand.length，即 33、7 或 6）。雖然現代瀏覽器透過
document.getElementById 能運作，但變數命名高度重疊且語意不合（用代表 N 的 ID 裝切點數），未來維護極易誤踩全域變數覆蓋 bug。
• 證據：ens_b.py 第 303 行顯示「切點數：w09splitN」，第 520 行將候選數寫入此 span。
• 建議改法：將該 span 的 ID 與 JS 賦值改為 w09splitCands 或 w09splitNumCands，明確與樣本數常數 w09splitN 區隔。
──────
## 三、冗餘與順序（嚴重度：低）
### 1. bagging 節側欄說明卡與相鄰正文段落完全重複
• 位置：bagging（PART 07）元件 w09bagSvg 側欄卡片 vs 相鄰主文段落：
• 側欄卡片原句開頭：「OOB 誤差怎麼算 ISLP §8.2.1: 對第 i 筆資料，把「所有沒用到它的那些樹」找出來（大約 B/3 棵）...」
• 相鄰正文原句開頭：「OOB 誤差怎麼算。對第 i 筆，找出所有沒用到它的樹（大約 B/3 棵），用它們預測第 i 筆再平均（或投票）...」
• 問題：側欄資訊卡逐字重複了正文對 OOB 計算流程與「B 夠大時幾乎等於 LOOCV」的描述，違反了 STYLE_CONTRACT.md §5「側欄與正文不要重複，側欄專注於引導互動操作」的原則。
• 建議改法：
• 側欄卡片簡化，專注引導讀者觀察元件動態：「怎麼看這張圖：觀察上方 10 個 bootstrap 重抽樣樣本中，紅色小球（未被抽中的樣本）如何自然形成每棵樹的 OOB
子集；右側即時統計其佔比是否接近理論值 1/e ≈ 36.8%。」
• 正文保留完整的理論定義與 LOOCV 等價條件。
──────
## 四、文字與用詞（嚴重度：低）

### 1. 繁體中文術語與流暢度微調

• importance 節：
• 原句：「置換重要度（Permutation Importance）由 Breiman 提出...」
• 建議：可於首次提及時加註常見別名「PFI（Permutation Feature Importance）」，有助於對接 scikit-learn API permutation_importance。
• successors 節：
• 原句：「CatBoost 雖然也有 feature subsampling，但預設全開（1.0）...」
• 建議：在中文語境中，「全開」有時會被誤解為「特徵子抽樣功能啟動」；建議微調為「預設抽樣比例為 1.0（即使用全部特徵，不進行子抽樣）」，表達更為精準。

──────
## 五、互動元件深度核對（Widgets Audit）
本審查針對三個全新設計的互動元件進行了原始碼（JS）與物理渲染行為比對：
### 1. w09xgb（XGBoost 葉值與增益互動計算）
• 核對項目：
• 支援「迴歸（平方損失）」與「二元分類（Logistic 損失）」切換。
• 切換至分類模式時，hᵢ = pᵢ(1 - pᵢ) 正確計算；當基底預測 p = 0.5 時，hᵢ = 0.25。
• 增益公式嚴格符合 Chen & Guestrin (2016) Eq. 7；側欄清楚標示 StatQuest（無 1/2）與論文（有 1/2）的 2 倍轉換關係。
• γ（分裂門檻）的扣減邏輯正確：Gain > 0 亮綠燈代表允許分裂，否則亮橘燈代表被剪枝。
• 結論：完全正確，無邏輯漏洞。
### 2. w09split（直方圖 vs 加權分位切點模擬）

• 核對項目：
• 內建 40 筆混合分佈資料（密集區＋稀疏極值區）。
• 精確排序（Exact）：在 x = 4.55 處找到最佳切點，最大 Gain 為 3.861。
• 直方圖法（Histogram, 8 bins）：切點 x = 3.75，Gain 為 2.470（損失 36.02%）。
• 加權分位草圖（Quantile, 8 bins）：切點精準命中 x = 4.55，Gain 為 3.861（損失 0%）。
• 切換「權重不均時若未用 Hessian 加權」情境：加權草圖的損失激增至 82.19%，直觀展示了「為什麼必須用二階導 hᵢ 作為分位草圖權重」。
• 結論：數值完全收斂，教育展示效果顯著。
### 3. w09stack（Stacking 折外預測與中繼特徵流程）

• 核對項目：
• 清楚展示 3-fold 交叉驗證產生 Z ∈ ℝ^{n×M} 的動態過程。
• 側欄與主文嚴正警告「絕對不能用全資料訓練基底模型來預測訓練集（否則產生 Target Leakage）」。
• 測試集特徵矩陣 Z_{test} 正確展示為各折模型預測的平均（Blending 模式）。
• 結論：流程與教學圖解完全吻合。
──────
## 六、確認無誤的重點項目（核對無誤清單）

以下為審核過程中逐一驗算或對照原始文獻／Lab 輸出，確認完全正確無誤的關鍵內容：

1. StatQuest XGBoost Regression 數值完全吻合：
• 樹根 Gain：λ = 0 ⟹ 120.33（論文式 60.17）；λ = 1 ⟹ 62.49（論文式 31.24）。
• 左葉值：λ = 0 ⟹ -10.5；λ = 1 ⟹ -5.25。
• 右葉值：λ = 0 ⟹ 2.17；λ = 1 ⟹ 1.625。
• 其他候選切點 Gain：Dosage < 14 ⟹ 4.0；Dosage < 22.5 ⟹ 56.33。
2. CatBoost Ordered Target Statistics 官方算例：
• 公式：x̂ᵢᵏ = (∑{j<i,xⱼᵏ=xᵢᵏ} yⱼ + a · p)/(∑{j<i,xⱼᵏ=xᵢᵏ} 1 + a)，設定 a = 1, p = 0.05。
• 第 4 列（rock）：(1 + 0.05)/(2 + 1) = 1.05/3 = 0.35。
• 第 6 列（indie）：(0 + 0.05)/(1 + 1) = 0.05/2 = 0.025。
• 第 7 列（rock）：(2 + 0.05)/(3 + 1) = 2.05/4 = 0.5125。數值完全無誤。
3. Fisher 類別最佳分割定理數值算例：
• 四個類別 D、B、C、A 依一階與二階導比值 -G/H ∈ {-2, -0.5, 0.5, 2} 排序。
• 排序後 3 個連續切點之 Gain 分別為 5.34、7.85、7.52。
• 窮舉 2⁴⁻¹ - 1 = 7 種子集劃分，最大值精確落在 {D, B} 的 7.85，數值完美呼應定理。
4. AdaBoost 學習率 η = 1/2 與 1 等價性推導：
• w09proof-adaboost 嚴密證明了在權重每輪標準化（∑ wᵢ = 1）的前提下，基學習器權重縮放 2 倍不影響樹的擬合與最終符號決策 sign(∑ αₘhₘ(x))，釐清了課本與 ESL Algorithm 10.1
的符號差異。
5. Lab 程式碼與輸出忠實度：
• Heart 資料集 XGBoost 網格搜尋：三組獨立單變數微調的測試準確率記錄為：subsample=0.5 為 0.81536；n_estimators=400 為 0.79541；max_depth=3 為 0.81197。與 lab cell 124–165
輸出逐字一致。
• Carseats 資料集 Stacking 輸出解讀：正文正確指出了 lab 第 238 格印出的報表誤植（將 VotingClassifier 標籤印在 StackingClassifier 的結果上），並如實還原了 lab
原始輸出的實相與學生可能產生的困惑。
6. 學生問答 37 題覆蓋度：
• 涵蓋袋裝抽樣極限推導、RF 中 m ≈ √p 的幾何與方差權衡、GBDT 負梯度即殘差的二階與一階意義、XGBoost 的 Cover（即 H = ∑ hᵢ）與 min_child_weight 的關係、LightGBM leaf-wise
生長與深度失控問題、CatBoost 避免目標洩漏的順序原則、BART 的樹總數預設 200 棵與先驗正則化等，無一遺漏。
7. HTML 結構與輔助功能驗證：
• 執行 tools/validate.py --page tree_based_methods，通過全部靜態檢查（0 errors，僅有正常的 HTML 檔案大小提醒）。全站 10 節的 quiz 選項與正解回饋皆完整無訛。

──────
## 審查總結

本次成稿在統計學習的廣度與數學推導的深度上達到了極佳的平衡，三個互動元件的加入大幅強化了學習體驗。僅需將上述第一、二項中的「跨節前後引用標籤（#modern、#boosting）」與「λ
算例接續標記」進行微調修正，即可成為正式發布的高品質教材。