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
