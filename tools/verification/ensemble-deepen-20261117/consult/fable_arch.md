1. 分節方案：集成部分 6 節拆成 10 節，依講義頁序，既有 id 全留給前半

┌─────┬──────────────────────┬─────────────────────────────────┬────────────────────────────────────────────────────────────────────┬─────────────────┐
#  │          id          │             短標題              │                              一句副標                              │     講義頁
├─────┼──────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────────────┼─────────────────┤
1   │ why（留）            │ 投票分類器                      │ 多樣性從哪裡來：異質演算法、硬投票與軟投票                         │ p.30–31
├─────┼──────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────────────┼─────────────────┤
2   │ bagging（留）        │ Bagging 與 OOB                  │ 平均深樹壓變異；袋外樣本為什麼近似 LOOCV                           │ p.32–37
├─────┼──────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────────────┼─────────────────┤
3   │ rf（留）             │ Random Forest 與變數重要度      │ 每刀只看 m 個變數；重要度怎麼讀、怎麼誤讀                          │ p.38–42、51、67
├─────┼──────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────────────┼─────────────────┤
4   │ boosting（留）       │ Boosting                        │ 慢慢學：AdaBoost 與演算法 8.2                                      │ p.43–50、68
├─────┼──────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────────────┼─────────────────┤
5   │ gbm（新）            │ 一般損失的梯度提升              │ 負梯度當目標、每片葉各自 argmin、logistic 的一步牛頓               │ p.45–48、69
├─────┼──────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────────────┼─────────────────┤
6   │ modern（留）         │ XGBoost：目標函數與一棵樹怎麼長 │ 二階近似、葉值、增益、λ 與 γ、缺失值方向                           │ p.52–53
├─────┼──────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────────────┼─────────────────┤
7   │ fastgbdt（新）       │ 切點搜尋、LightGBM 與 CatBoost  │ 精確、分位草圖、直方圖；leaf-wise、GOSS、對稱樹與 ordered boosting │ p.54–59
├─────┼──────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────────────┼─────────────────┤
8   │ tuning（新）         │ 超參數、類別編碼與套件選擇      │ 三套件參數對照、lab 網格與 early stopping、target encoding 的洩漏  │ p.60–62、70–73
├─────┼──────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────────────┼─────────────────┤
9   │ stacking（留）       │ Stacking                        │ 用模型學合併；折外預測                                             │ p.66
├─────┼──────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────────────┼─────────────────┤
10  │ bart（新，整節收合） │ BART                            │ 貝氏版加法樹：先驗、MCMC、K／B／L                                  │ p.74–79
└─────┴──────────────────────┴─────────────────────────────────┴────────────────────────────────────────────────────────────────────┴─────────────────┘

- 為什麼這樣切：boosting 現在 6 千字且 quiz 之後還掛三個收合，是讀者負擔最重的一節；把「一般損失」獨立成 gbm 後，modern 的二階近似才有前置（g、h 的定義、每葉 argmin）。modern
現在混了 XGBoost 統計、三套件機制、超參數表與編碼四件事；拆成「一棵樹怎麼長」「切點怎麼找」「怎麼調」三節，三個新元件各有歸宿：(a) 在 modern，(b) 在 fastgbdt，(c) 在 stacking。
- 合併而非拆開：變數重要度不另立節，併入 rf 尾段。它現在放在 stacking 是錯位，講義 p.51 緊接 boosting，lab 的重要度圖又是 RF 產生的。bart
獨立是為了讓「整節收合」在版面上成立，正文只留兩句定位。
- 若要少兩節：gbm 併回 boosting、tuning 併入 fastgbdt，代價是這兩節各回到 5 千字以上。我不建議。

2. 每節正文 vs 收合（★＝學生問答落點）

- why 正文：集成的兩個任務（造成員、合併）；硬投票與軟投票的定義與一個反例，三個模型對類別 1 給 0.51、0.52、0.01，硬投票選 1、軟投票平均 0.347 選 0 ★#5；base learner
怎麼挑，bagging 要強而不穩的、boosting 要簡單的、stacking 要異質互補 ★#0 #3；lab 的 Carseats 投票卡。收合：「0-1 損失下 bagging 爛分類器會更爛」ESL §8.7 的 0.4／0.6 例；「bagging
對線性估計量無效」ESL Ex 8.4、15.4；「加權軟投票是受限的 stacking」ESL §8.8 非負權重和為 1。
- bagging 正文：σ²/B 與 ρσ²+(1−ρ)σ²/B；深樹不剪枝；OOB 定義與 1/e；B 大不過擬合的正確說法 ★#9 #11：加樹只是對 E_Θ T(x;Θ)
的蒙地卡羅估計更準，模型容量不變；但極限本身可能因樹太深而過擬合，ESL §15.3.4。收合：「OOB 為什麼近似 LOOCV」★#15，條件於第 i 筆落袋外時其餘抽樣等於從 n−1 筆有放回抽 n 次，所以
OOB 預測在 B→∞ 時趨近「對 D₋ᵢ 做 bagging」，差別在抽 n 次不是 n−1 次，且只用約 B/3 棵樹，所以要 B 大，兩本書都只斷言未證明；「stochastic boosting 的 OOB」。
- rf 正文：m 與每刀重抽；√p 是發明者建議值、該當調整參數 ★#19，附 ESL 圖 15.3 的 m=6 勝 ⌊8/3⌋ 與 sklearn 迴歸預設 1.0 等於 bagging；random subspace 是每棵樹抽一次、RF
是每個節點抽一次 ★#13；重要度兩種：不純度下降對 B 棵平均 ★#38，平均是為了跨 B 可比與穩定，ESL (10.43)；置換重要度問的是「模型多依賴它」。收合：ρ(x) 的真正意義與偏差上升，ESL
§15.4；Extra-trees 與 random patches；基因表達例；高基數偏好與相關稀釋。
- boosting 正文：序列、無 bootstrap；演算法 8.2 逐步；B、λ、d 與「d 刀最多涉及 d 個變數」★#36；AdaBoost 的 α 與權重 ★#23，正文只說「α 是指數損失下的最佳步長，答錯的權重乘
e^α」；講義 p.45–47 三張圖的關係是「擬合殘差的特例、演算法、為何學得慢」★#30。收合：指數損失推導與 α=2β，ESL §10.4；AdaBoost 元件；learning rate 減半的 moons 例，p.68。
- gbm 正文：樹是階梯函數的和 ★#28；把預測向量當參數、負梯度當偽殘差，平方損失下負梯度恰等於殘差 ★#78；每片葉各自做一維 line search 的理由，ESL p.359 ★#32 #34；表 10.2；logistic
的一步牛頓葉值 Σ(y−p)/Σp(1−p) ★#76；shrinkage 與不放回子抽樣。收合：負梯度是下降方向的證明（既有）；Huber、絕對損失、多類 deviance（既有）；ESL ½ log-odds 與 XGBoost 全 log-odds
的尺度差。
- modern 正文：Obj=Σl+γT+½λΣw²；二階展開只剩 g、h ★#40；w*=−G/(H+λ)、結構分數、Gain=½[…]−γ；O 就是 w*、p_i 是上一輪預測機率、p₀ 是初始預測、O 加在 log-odds 上 ★#44–#52；λ
把葉值縮向 0 且 H 小時縮得最多；min_child_weight 是子節點 Hessian 和的下限 ★#94；缺失值兩趟掃描選預設方向，X 缺、y 在 ★#82 #84；元件 (a)。收合：Eq.3 改寫成以 h
加權的平方損失；Alg.3 手算；γ=0 仍會剪；max_delta_step。
- fastgbdt 正文：精確法只需在相異值中點上掃，排序一次即可；近似法把候選切點縮成分位點，候選數約 1/ε ★#54；加權分位草圖的權重是 h ★#68；直方圖是對特徵值分箱、箱內累加 Σg 與 Σh ★#58
#62 #64 #80；成本對比 ★#72；leaf-wise 與 depthwise 長滿相同、有預算才有差 ★#86 #90；元件 (b)。收合：XGBoost 三種 tree_method 的現行差異；GOSS 的
(1−a)/b；EFB；直方圖相減；LightGBM 類別最佳分割以 Σg/Σh 排序；CatBoost 對稱樹、ordered TS、ordered boosting 的 prediction shift、MVS；DART；cache-aware 與 out-of-core，p.54–55。
- tuning 正文：三組目的的參數對照表（既有）；lab heart 網格的正確讀法；early stopping；one-hot、ordinal、target encoding 與洩漏；講義 p.62 的套件選擇。收合：K-fold target
encoding；LOO 仍洩漏的 5／6 例；CatBoost 官方 rock／indie／pop 逐列表；Melbourne 三套件原生類別處理的 lab 卡；Grinsztajn 2022 三個發現。
- stacking 正文：voting 固定規則、stacking 學規則 ★#7；折外預測為什麼必要；元件 (c)；lab 兩張卡。收合：sklearn 機制，cv、prefit、passthrough、stack_method；外層 CV 評估整個流程；與
K-fold TE、ordered boosting 是同一種「別用自己的 y」。
- bart 正文兩句定位。收合全部：模型與演算法 8.3；先驗 α(1+d)^−β 的 0.95、2 與葉數機率 0.05／0.55／0.28；σ_μ=0.5/(k√m) 對應 shrinkage；ν、q；backfitting MCMC 四種移動；K、B、L；lab
的 22.15 與 variable_inclusion_。

3. 三個元件的設計

- (a) XGBoost 葉值與分裂增益。控制項：損失切換（平方／logistic）、λ 滑桿 0–10、γ 滑桿、切點滑桿、logistic 模式下各點的上一輪 p 與標籤 y 可改。資料：StatQuest 的四點，殘差
−10.5、6.5、7.5、−7.5，標「概念示意、取自講義連結」。畫面：上半是依特徵排序的點與目前切點，每點標 g、h；下半畫左葉的目標二次式對 w
的拋物線與最低點。讀值：G_L、H_L、G_R、H_R、兩個 w*、Gain 論文版與實作版、「切或不切」。教學目標：λ 讓最低點往 0 靠且 H 小時最明顯；γ 是門檻；logistic 下
h=p(1−p)，篤定的點份量小，min_child_weight 限制的就是 H。易誤導：g 的正負號，g=ŷ−y 所以 w*=Σ(y−p)/(Σp(1−p)+λ)，StatQuest 的「殘差和」是 −G；logistic 的 w* 是 log-odds
增量，不能直接加到 p；實作版 similarity 是論文結構分數的 2 倍；官方教學的平方損失沒有 ½ 所以 g、h 都乘 2 但 w* 不變；λ 不是 ISLP 的學習率；初始 0.5 是舊版
base_score，不要當通則。
- (b) 精確排序 vs 直方圖 vs Hessian 加權分位。控制項：n 點（固定種子 LCG，30–60）、方法三選一、箱數 4–32、logistic 模式下「上一輪 p
的分佈」切換（均勻／兩端篤定／中間猶豫）。畫面：特徵軸上畫所有候選切點的刻度，精確法是每對相異值的中點，直方圖是等頻分位邊界，加權版是 h
累積比例的分位邊界；下方畫各候選的增益曲線與被選中的切點；h 以點的高度表示。讀值：候選數、三法各自的最佳增益、相對精確法損失多少。教學目標：精確法候選數是 u−1
而非無限，排序一次即可；直方圖把每節點的工作量從資料數變成箱數；加權分位讓猶豫區切得細，避免正負殘差被併進同一箱。易誤導：分箱對象是特徵值，箱裡累加的是 g 與 h，不是對 g 或 h
分箱；現行 XGBoost 預設 hist 不用 Hessian 加權，只有 approx 用；「直方圖 O(n) vs 排序 O(n log n)」是 sklearn 經典 GBDT 的對比，不是 XGBoost 論文的
exact；分位邊界是等頻不是等寬；本元件的增益只算一個節點，看不到直方圖相減。
- (c) Stacking 折外預測流程。控制項：K 折 3／5、基模型數 2／3、「單步」逐折推進、「錯誤做法」開關改用訓練內預測。畫面：左邊 n×1 的資料條，目前折反白；右邊 n×M 的 Z
矩陣，每步填入該折的一列區塊；K 步後 Z 填滿，出現合併器訓練；最後一步基模型用全部資料重擬合，供預測新資料。讀值：Z 填充進度、合併器權重（示意），錯誤做法下深樹那欄權重近 1
且訓練內準確率 1.0。教學目標：每筆的 Z 值都來自沒看過它的基模型；內層 CV 只為造 Z，整個流程的效能要外層 CV。易誤導：Z 不是新資料、沒有放大樣本；內層折與第 5 章 nested CV
的內層用途不同；合併器用邏輯斯迴歸權重可為負，ESL 建議非負和為 1；cv='prefit' 等於錯誤做法；lab 第一段迴圈的標籤把 VotingClassifier 印成 StackingClassifier，逐字引用時要加註。

4. 易錯論斷

- 排序成本：「精確貪婪每個節點都要重排 O(n log n)」只對樸素實作與 sklearn 的 GradientBoosting* 成立，sklearn §1.11.1.1.8 自述每節點排序；XGBoost 論文 §4.1 的 pre-sorted CSC block
只排序一次，複雜度 O(Kd‖x‖₀+‖x‖₀ log n)。講義 p.56 的 O(n log n) vs O(n) 要標明對象。
- 加權分位草圖的權重：是 h_i，論文 §3.3 Eq.8，理由是 Eq.3 可改寫成權重 h、標籤 −g/h 的加權平方損失；論文印成 +g/h 是筆誤。現行 Tree Methods 頁：只有 approx 以 Hessian
加權且每棵樹前重做，預設 hist 只用使用者權重。
- min_child_weight：官方定義「子節點 instance weight (hessian) 和的下限」，預設 1；平方損失 h=1 才等於樣本數；logistic 下 h≤0.25，預設 1 約等於至少 4 筆最猶豫的樣本。LightGBM
同名參數是 min_sum_hessian_in_leaf 的別名、預設 1e-3；CatBoost 的 min_data_in_leaf 是筆數且只在非對稱策略有效。
- leaf-wise 預設：LightGBM 是 leaf-wise，max_depth 設了仍 leaf-wise；XGBoost grow_policy 預設 depthwise，lossguide 限 hist／approx；CatBoost 預設
SymmetricTree。不加停止條件時三種展開順序長出同一棵樹，Shi 2007；「多數決策樹是 level-wise」不成立，CART、C4.5 是 depth-first。
- AdaBoost 的 η：η=½ 是 ESL (10.12) 的 β_m，估的是 ½ log-odds；η=1 是演算法 10.1 的 α_m=2β_m，ESL p.344。兩者 sign 分類相同，差在 f 的尺度。現有「η=1
會加倍經典係數」的說法反了方向，經典 AdaBoost.M1 本來就是無 ½ 的版本。
- OOB≈LOOCV：ISLP p.345「B 夠大時幾乎等價」、ESL p.593 指向 Ex.15.2，兩本都沒給證明，Zhou 的解答該題標 TODO。條件是 B 大、且把 LOOCV 那邊的 bagging 也視為抽 n
次；不能寫「已證明」。
- √p 的理由：ESL p.592 明說是發明者建議、應當調整參數；ISLP 只說「通常」；sklearn 稱「經驗上好的預設」，迴歸預設 1.0。沒有任何來源推導 √p。
- 「boosting 沒有 bootstrap 所以沒有 OOB」：只對演算法 8.2 成立；stochastic GB、subsample、bagging_fraction 都抽樣，sklearn 的 oob_improvement_ 存在但官方說偏悲觀。
- XGBoost 預設：tree_method='auto' 等於 hist；lambda 預設 1，StatQuest 說預設 0 是錯的；類別特徵自 1.5 起原生支援、1.6 起 optimal partitioning，講義 p.53、lab 儲存格 168
的「實驗性、建議自己編碼」已過時。
- GOSS 與 CatBoost 預設：GOSS 現在是 data_sample_strategy='goss'，4.0 起；補權 (1−a)/b 的 b 相對全體資料，論文 §3.2 寫法自相矛盾。CatBoost CPU 預設 boosting_type=Plain、抽樣預設
MVS，「預設 ordered boosting」不對；ordered TS 不受 boosting_type 影響。
- 梯度等於殘差：只在平方損失且損失帶 ½ 時成立；logistic 的負梯度是 y−p，在 log-odds 尺度；ESL 的 ½ log-odds 參數化會讓梯度差 2、Hessian 差 4。
- 直方圖箱數：講義 p.56「預設 255 且不能更高」是 sklearn HistGradientBoosting 的限制；LightGBM max_bin 預設 255 但可調高，XGBoost 預設 256。
- 圖 8.11：正文說 stump 勝 depth-2 勝 RF，圖說卻說標準誤約 0.02、差異不顯著，兩者都要講。
- target encoding：leave-one-out 仍會洩漏，CatBoost 論文 §3.2 與教學的 5／6 例；K-fold 或 ordered 才解決。

5. 現有內容的問題

- boosting「下面的元件取 η=½，那正是 Freund–Schapire 原版…η=1 代入這組對稱更新會加倍經典二元係數」：方向錯，見上。
- boosting quiz 之後還有「一般負梯度、AdaBoost 尺度與不同損失」三個收合：順序不佳，quiz 應在節尾；這批內容搬到 gbm。
- boosting Q「Bagging 與 Boosting 如何組合樹？」：第三次重複 motive 路線圖與本節開頭的偏差變異對比，刪或縮成三行。
- boosting「深度 1 的樹略勝深度 2，兩者都勝過 random forest」：補圖說的不顯著。
- modern「lab 在 heart_disease.csv…一個一個網格搜過去…subsample 降到 0.5 又多賺一點…把樹加到 800 棵反而變差」：lab 每次 grid_search
都是獨立的新模型、只搜一個參數，不是累積調參；subsample=0.5 單獨得 0.815；n_estimators 最佳是 400、0.795，與基準相當，lab 原話是「並未帶來更好的結果」，不是變差。
- modern「形式上跟本頁剪枝一節的成本複雜度剪枝一模一樣」：同一個想法但不是同一套流程，γ 進入每刀的增益，改「同一個想法」。
- modern 開頭三段互相重複，且「第一輪讀可以整節略過」與這次加深的決定衝突；stacking 開頭同樣兩段。
- modern 來源列表 23 項含重複的「Boosting 套件選擇背景」兩次；Medium 三篇 403、neptune 憑證過期、datasketches 舊址 404，依規範應換成現行網址或移除。
- modern「直方圖的好處…不必像精確搜尋那樣每次排序全部資料」與一句話表的 LightGBM 列：改成「每節點掃箱數而非資料數」。
- rf 開頭「Bagging 的樹若經常依賴同一組特徵…」與下一段「如果資料裡有一個特別強的變數…」重複。
- rf Q「本頁的相關數字是同一次擬合中、各棵樹跨測試樣本預測向量的平均相關」：頁上已無這些數字，是舊投票元件的遺留。
- rf 收合「證明：平均樹的變異與相關性」與 motive 的 w09-detail-rho-floor 是同一證明兩份；motive 寫「推導見 random forest 一節」、bagging 寫「推導在開頭那節」互相指。留 motive
一份。
- bagging「boosting 沒有 bootstrap，所以沒有 OOB」：加限定。
- bagging 收合「重抽樣、OOB 與平均機率是三個步驟」重述正文的 OOB，末段「不能把…讀成訓練流程無須驗證」是沒有內容的告誡。
- stacking 的重要度段：「最大的陷阱：相關的變數會互相稀釋」與「③ 相關變數會互相稀釋。上面那張側欄卡講的就是這件事」重複；三步驟清單在正文與收合各寫一次。
- stacking lab 卡只引了 sclf = … 一行，沒有輸出；voting 卡缺 0.82 vs 0.81 的輸出與標籤錯誤的註記。
- why「ISLP 第 16.1 節」徽章實為 ESL §16.1，pages.py 寫對了，渲染字串要核對。

6. 講義或連結有教、網站漏掉的主題

- 講義 p.54–55 的系統面：cache-aware、block compression、sharding，連結 latency gist；現在零句。
- p.57 LightGBM 類別特徵以 Σg/Σh 排序後找切點、max_cat_to_onehot；p.56 EFB 與 one-hot／label 的關係只有一句。
- p.58 ordered boosting 的 prediction shift 是一種 target leakage，CatBoost 論文 Thm 1 的 1/(n−1) 偏差；可和 stacking、K-fold TE 串成同一主題。
- p.62 結論的套件選擇與 Grinsztajn 2022 的三個發現；p.68 AdaBoost 的 learning rate 減半。
- Lab 大段未用：exoplanet 速度比較 624 秒對 24、13、15 秒；early stopping 儲存格 155–164；bagging 500 棵 14.61；boosting staged_predict 曲線；BART 的 22.15 與
variable_inclusion_；LightGBM／CatBoost 的 Melbourne 原生類別處理與 CatBoost 的 one_hot_max_size=500、model_size_reg、max_ctr_complexity、Counter／Borders／Buckets 系列。
- 原論文的 BART 先驗與 MCMC 移動機率，講義只連 Lopes 投影片，投影片沒有公式。
- p.64–65 ID3／C4.5／C5.0／CART 屬單棵樹附錄，本次不動，建議另案補在 grow。
- 置換重要度與不純度重要度的高基數偏好，ESL §15.3.2、sklearn §1.11.2.5。