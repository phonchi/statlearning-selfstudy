"""3D 統計學習知識群島（island/index.html）專用的文案。

章節順序、標題與分區一律取自 tools/pages.py；這裡只放島上才需要的東西：
  landmark — 島上那棟建築的名字
  blurb    — 面板與 2D 卡片上的一兩句簡介
  refs     — 正課頁「需要時可查閱」的先備頁 stem（只是查閱建議，不是必讀前置）

build_island.py 會比對這裡的 stem 與 PAGES：缺頁、多頁或 refs 指到不存在的頁都會報錯。
"""

# 四座島。鍵＝Page.grp；順序＝島嶼列表與 2D 地圖的順序（與首頁四區一致）。
ISLES = {
    "pre": dict(name="啟航島", sub="課前準備 · 選讀", note="港口與燈塔：先把學習方法與環境準備好。"),
    "core": dict(name="統計學習主島", sub="正課 11 章", note="沿著環島小徑依授課順序排列，可自由進入任何一章。"),
    "statistics": dict(name="統計森林島", sub="統計先備 · 查閱用", note="正課讀到卡住時再來這片樹林查閱，不必先讀完。"),
    "appendix": dict(name="Python 工坊島", sub="Python 先備 · 查閱用", note="正課會用到的語法與套件，需要時再進工坊。"),
}

META = {
    # ── 啟航島 ─────────────────────────────────────────────
    "00a_why_code": dict(
        landmark="燈塔",
        blurb="資料分析的學習迴圈：提出想法、動手嘗試、觀察證據、修正理解，並讓 AI 留在迴圈裡協助你練習判斷。"),
    "00b_setup": dict(
        landmark="補給碼頭",
        blurb="從 Colab 到本機環境，跑出第一張圖；期中考使用電腦教室，考前用相同版本完整重跑一次。"),
    "00c_ai_assisted": dict(
        landmark="領航站",
        blurb="用 AI 輔助統計分析：先分流任務、補足脈絡、小步生成，再核對統計解讀並留下可重現紀錄。"),
    # ── 統計學習主島（正課）─────────────────────────────────
    "introduction": dict(
        landmark="觀測塔",
        blurb="統計學習在做什麼、和相關領域如何分工；先看資料再建模，從探索式資料分析（EDA）讀懂 22 個資料集。",
        refs=["s1_probability", "p4_pandas", "p5_visualization"]),
    "statistical_learning": dict(
        landmark="訓練／測試分岔路",
        blurb="Y = f(X) + ε 的基本框架：可縮減與不可縮減誤差、彈性與可解釋性、偏差–變異取捨，以及 Bayes 分類器與 KNN。",
        refs=["s1_probability", "s3_distributions", "p3_numpy"]),
    "linear_regression": dict(
        landmark="迴歸斜坡",
        blurb="簡單與多元線性迴歸：係數的標準誤與 t 檢定、F 檢定、R²，以及質性變數、交互作用與共線性等常見問題。",
        refs=["s4_inference", "s6_regression", "p6_modeling_api"]),
    "classification": dict(
        landmark="雙色分類城門",
        blurb="邏輯斯迴歸、LDA、QDA 與 Naive Bayes；用混淆矩陣、ROC 與 AUC 比較分類結果，並延伸到 Poisson 迴歸。",
        refs=["s2_conditional", "s3_distributions", "s5_bayesian", "p6_modeling_api"]),
    "resampling_methods": dict(
        landmark="Bootstrap 噴泉",
        blurb="驗證集法、LOOCV 與 k-fold 交叉驗證估計測試誤差；Bootstrap 重抽樣衡量估計量的不確定性。",
        refs=["s3_distributions", "s4_inference", "p6_modeling_api"]),
    "model_selection": dict(
        landmark="修剪花園",
        blurb="變數很多時如何選模型：子集選擇與 Cp／AIC／BIC，Ridge 與 Lasso 正則化，以及 PCR 與 PLS 降維迴歸。",
        refs=["s6_regression", "p3_numpy", "p6_modeling_api"]),
    "beyond_linearity": dict(
        landmark="樣條拱橋",
        blurb="線性不夠用時：多項式、階梯函數、迴歸樣條、平滑樣條、局部迴歸，最後組成廣義可加模型（GAM）。",
        refs=["s6_regression", "p5_visualization"]),
    "tree_based_methods": dict(
        landmark="決策樹森林",
        blurb="迴歸樹與分類樹的分裂與剪枝；再用 Bagging、隨機森林與 Boosting 把許多棵樹集成為更穩定的預測。",
        refs=["s3_distributions", "p6_modeling_api"]),
    "support_vector_machines": dict(
        landmark="最大間隔圍牆",
        blurb="用超平面把兩群資料分開：最大邊界、軟邊界與 C、hinge loss，以及透過核技巧處理非線性邊界。",
        refs=["p3_numpy", "p6_modeling_api"]),
    "unsupervised_learning": dict(
        landmark="群聚星球廣場",
        blurb="沒有標準答案的學習：主成分分析（PCA）、矩陣補全，以及 K-means 與階層式分群。",
        refs=["s1_probability", "p3_numpy", "p5_visualization"]),
    "deep_learning": dict(
        landmark="神經網路高塔",
        blurb="補充章：從單層到多層神經網路、卷積與循環網路，以及模型如何擬合與雙下降現象。本課未授課，供自學延伸。",
        refs=["p3_numpy", "p6_modeling_api"]),
    # ── 統計森林島 ─────────────────────────────────────────
    "s1_probability": dict(
        landmark="機率樹屋",
        blurb="母體與樣本、事件與機率、隨機變數的期望值與變異數。"),
    "s2_conditional": dict(
        landmark="條件樹屋",
        blurb="條件機率、獨立與互斥，以及 Bayes 公式。"),
    "s3_distributions": dict(
        landmark="分布樹屋",
        blurb="常用分布與抽樣分布，大數法則與中央極限定理。"),
    "s4_inference": dict(
        landmark="推論樹屋",
        blurb="點估計、標準誤、信賴區間、假設檢定與 p 值，以及 Bootstrap 入門。"),
    "s5_bayesian": dict(
        landmark="貝氏樹屋",
        blurb="選讀：概似與最大概似，從先驗到後驗的更新。"),
    "s6_regression": dict(
        landmark="相關樹屋",
        blurb="選讀：共變異數與相關、最小平方法與殘差的解讀限制。"),
    # ── Python 工坊島 ──────────────────────────────────────
    "p1_python_basics": dict(
        landmark="基礎工坊",
        blurb="變數與型別、串列與切片、字典、字串格式化。"),
    "p2_flow_functions": dict(
        landmark="流程工坊",
        blurb="條件、迴圈、函式與作用域，以及如何讀懂錯誤訊息。"),
    "p3_numpy": dict(
        landmark="NumPy 工坊",
        blurb="ndarray 的 shape、索引、布林索引、廣播、axis 與亂數模擬。"),
    "p4_pandas": dict(
        landmark="pandas 工坊",
        blurb="Series 與 DataFrame、loc／iloc、遺漏值、groupby 與資料串接。"),
    "p5_visualization": dict(
        landmark="視覺化工坊",
        blurb="Matplotlib 與 Seaborn：先畫圖看分布與關係，再把模型畫進圖裡。"),
    "p6_modeling_api": dict(
        landmark="建模工坊",
        blurb="statsmodels 與 scikit-learn：設計矩陣、fit／predict、訓練測試切分與交叉驗證。"),
}

# ── 正課各章的代表互動圖 ─────────────────────────────────
# fig  — 教材頁裡互動圖的元素 id：面板縮圖截的是 #fig 所在的 .viz-panel，「去操作這張圖」連到 頁面.html#fig
# whole — 預設 True 截整個 .viz-panel（圖＋控制列）；False 只截圖本身（一個 panel 裡有好幾張圖時）
# prep — 截圖前在教材頁執行的 JS（例如先跑到收斂），wait 為之後等待的毫秒數
# 縮圖由 tools/build_island_figs.js 產生到 island/figs/<stem>.webp；教材改版後重跑一次。
FIGS = {
    "introduction": dict(fig="w01ivWageAge", whole=False,
                         caption="Wage 資料：薪資隨年齡先升後降，先看資料再決定模型。"),
    "statistical_learning": dict(fig="w02bvChart", caption="測試 MSE 拆成偏差²、變異與不可縮減誤差，彈性越大，偏差越小、變異越大。"),
    "linear_regression": dict(fig="w03dragSvg", caption="拖動直線，看殘差平方和怎麼變；最小平方線讓它最小。"),
    "classification": dict(fig="w04shapeSvg", caption="調整 β₀、β₁，看 logistic 函數怎麼把線性分數轉成 0～1 的機率。"),
    "resampling_methods": dict(fig="w05bootChart", caption="有放回地重抽 200 次，估計量的分布直接給出標準誤。",
                               prep="w05bootMany()", wait=6000),
    "model_selection": dict(fig="w06geomSvg", caption="L1 的菱形限制區碰到等高線時，容易落在角上，把係數壓成剛好 0。"),
    "beyond_linearity": dict(fig="w08polySvg", caption="提高多項式次數，曲線更貼資料，但兩端的信賴區間會急速變寬。"),
    "tree_based_methods": dict(fig="w09growSvg", caption="遞迴二元分裂：每一刀都把特徵空間切成更純的長方形。",
                               prep="w09growStart()", wait=9000),
    "support_vector_machines": dict(fig="w10marginSvg", caption="最大間隔分類器：只有落在邊界上的支持向量決定那一刀。"),
    "unsupervised_learning": dict(fig="w07kmSvg", caption="K-means 反覆「指派、更新中心」，直到分群不再改變。",
                                  prep="w07kmRun()", wait=6000),
    "deep_learning": dict(fig="w11fwdSvg", caption="一層隱藏層的前向傳播：每個單元先做線性組合，再經 ReLU 等激活函數，非線性就從這裡進來。"),
}

# ── 嚮導「維導」的導覽 ───────────────────────────────────
# GUIDE — 維導到每一站時說的話（1～2 句，和 blurb 不重複）；路線 ①＋③ 涵蓋全部頁面，所以每頁都要有。
GUIDE = {
    "00a_why_code": "這座燈塔照的是學習方法：先提出想法、動手試、看證據，再修正。之後每一章都會用到這個迴圈。",
    "00b_setup": "出海前先補給！在這裡把 Colab 或本機環境準備好，跑出你的第一張圖。",
    "00c_ai_assisted": "AI 是很好的副手，但方向盤要握在自己手上。這一站教你怎麼問、怎麼驗證它給的答案。",
    "introduction": "歡迎登上主島！第一站先別急著建模，從觀測塔看清楚資料長什麼樣子。",
    "statistical_learning": "這條分岔路是整趟旅程的地圖：模型越有彈性，偏差越小、變異越大。之後每一章都在這條取捨上找平衡。",
    "linear_regression": "沿著迴歸斜坡往上走：一條直線看似簡單，係數、標準誤和檢定都從這裡開始。",
    "classification": "答案從數字變成類別時，就來到雙色城門。先看 logistic 曲線怎麼把分數變成機率。",
    "resampling_methods": "噴泉裡的水一直重新落下，就像重抽樣：手上只有一份資料，也能估計測試誤差與不確定性。",
    "model_selection": "變數太多會長得太茂盛，這座花園教你修剪：挑變數、加懲罰，或先降維。",
    "beyond_linearity": "走過這座樣條拱橋，直線就能彎了：多項式、樣條，一路組成 GAM。",
    "tree_based_methods": "森林裡每棵樹都在把資料一刀一刀切開；很多棵樹一起投票，預測就穩多了。",
    "support_vector_machines": "這道圍牆想離兩邊都越遠越好：最大間隔、軟邊界，再用核技巧讓牆轉彎。",
    "unsupervised_learning": "廣場上沒有標準答案，只能讓資料自己聚成群。PCA 和分群都在這裡。",
    "deep_learning": "最後一站在高地上：神經網路高塔。這章是補充，有興趣再慢慢爬上去。",
    "s1_probability": "森林的第一間樹屋：母體、樣本、期望值和變異數。正課讀到這些詞卡住時，回來這裡。",
    "s2_conditional": "「已知 A，B 的機率是多少？」條件機率和 Bayes 公式，分類那章會常常用到。",
    "s3_distributions": "常態、t、二項……各種分布都住在這裡，中央極限定理也是。",
    "s4_inference": "從樣本推回母體：標準誤、信賴區間和 p 值。迴歸係數的檢定就是靠它們。",
    "s5_bayesian": "選讀小屋：先驗加上資料，更新成後驗。想多了解貝氏觀點再進來看看。",
    "s6_regression": "選讀小屋：共變異數、相關與最小平方法，是線性迴歸那章的前奏。",
    "p1_python_basics": "Python 工坊從最基本的工具開始：變數、串列、字典和字串。",
    "p2_flow_functions": "條件、迴圈和函式；看不懂錯誤訊息時，也可以來這間工坊問問。",
    "p3_numpy": "NumPy 是做數值計算的車床：shape、廣播和亂數模擬都在這裡練。",
    "p4_pandas": "pandas 工坊專門整理資料表：選欄、處理遺漏值、分組統計。",
    "p5_visualization": "畫圖的工坊：先畫出分布和關係，再把模型疊上去看。",
    "p6_modeling_api": "最後一間工坊：statsmodels 和 scikit-learn 的 fit、predict 和交叉驗證，正課的實作都靠它們。",
}

# TOUR — 開場時讓學生選的路線（順序就是按鈕順序）與維導的台詞
TOUR = dict(
    name="維導",
    hello="嗨，我是維導，要我帶你逛嗎？",
    short="維導帶路",
    ask="想怎麼逛？我可以照你的需要選一條路線。",
    resume="上次我們走到第 {n} 站「{title}」，要接著走嗎？",
    bye="這條路線走完了！之後想去哪座島，直接點它就好；需要我時再按「維導帶路」。",
    routes=[
        dict(key="first", label="第一次來", note="啟航島 3 站，再照授課順序走正課 11 章",
             stems=["00a_why_code", "00b_setup", "00c_ai_assisted", "introduction", "statistical_learning",
                    "linear_regression", "classification", "resampling_methods", "model_selection",
                    "beyond_linearity", "tree_based_methods", "support_vector_machines",
                    "unsupervised_learning", "deep_learning"]),
        dict(key="core", label="照正課走", note="正課 11 章，每站都能看代表互動圖",
             stems=["introduction", "statistical_learning", "linear_regression", "classification",
                    "resampling_methods", "model_selection", "beyond_linearity", "tree_based_methods",
                    "support_vector_machines", "unsupervised_learning", "deep_learning"]),
        dict(key="prereq", label="補先備", note="統計森林島 6 站，再到 Python 工坊島 6 站",
             stems=["s1_probability", "s2_conditional", "s3_distributions", "s4_inference", "s5_bayesian",
                    "s6_regression", "p1_python_basics", "p2_flow_functions", "p3_numpy", "p4_pandas",
                    "p5_visualization", "p6_modeling_api"]),
    ],
)
