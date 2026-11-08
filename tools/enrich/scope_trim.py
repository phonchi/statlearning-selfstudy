"""第 7、8 章的範圍修剪與符號補定義（2026-11-08，使用者依 Astra／Fable 審查拍板）。

規則（HANDOFF §23、STYLE_CONTRACT §13）：講義只列名或一句帶過的主題，留 1–2 句概念加連結，
刪公式、推導與多段操作；收合 id 保留。自行算出的實測數字刪除；使用者提出過的主題保留。
每個替換都要恰好比對一次，上游改了會報錯。
"""
import re

from trees_lecture_notes import block, cut, rep


def inner(b, sec, pid, new, summary=None):
    """把收合 pid 的內文換成 new（保留它自己的來源連結段）；可同時改摘要。"""
    s = b[sec]
    a, z = block(s, pid)
    d = s[a:z]
    head = d.index('<div class="detail-body">') + len('<div class="detail-body">')
    src = re.search(r'<p class="source-links">.*?</p>(?=</div></details>$)', d, re.S)
    tail = (src.group(0) if src else "") + "</div></details>"
    if summary:
        d = re.sub(r"<summary>.*?</summary>", f"<summary>{summary}</summary>", d, count=1)
        head = d.index('<div class="detail-body">') + len('<div class="detail-body">')
    b[sec] = s[:a] + d[:head] + new + tail + s[z:]


def drop_p(b, sec, start):
    """刪掉以 start 開頭的那一整段 <p>…</p>。"""
    s = b[sec]
    if s.count(start) != 1:
        raise ValueError(f"{sec}: 段落起點比對到 {s.count(start)} 次：{start[:40]}")
    a = s.index(start)
    z = s.index("</p>", a) + len("</p>")
    b[sec] = s[:a] + s[z:].lstrip("\n")


# ══ 第 8 章 ════════════════════════════════════════════════════════════
XGB = r"""<p>XGBoost 每一輪用損失的一階與二階導數近似目標函數，講義說這和 Newton 法的想法相近。有了這個近似，每片葉的最佳輸出值和一刀分裂的淨收益都有公式可算；收益扣掉 $\gamma$ 之後不為正，就不切。推導細節見 <a href="https://xgboost.readthedocs.io/en/latest/tutorials/model.html" target="_blank" rel="noopener">XGBoost 官方的樹提升推導</a>。</p>"""

ENGINEERING = r"""<p>講義對這些機制各用一句話帶過，這裡也只列概念，細節見下方連結。</p>
<div style="overflow-x:auto;"><table class="cmp-table" style="width:100%;font-size:.85rem;">
  <thead><tr><th>套件</th><th>機制</th><th>一句話</th></tr></thead>
  <tbody>
  <tr><td>XGBoost</td><td>加權分位數草圖</td><td>只在少數代表性的切點上找最佳分裂，減少候選數。</td></tr>
  <tr><td>XGBoost</td><td>稀疏感知搜尋</td><td>每個節點學一個「缺失值往哪邊走」的預設方向。</td></tr>
  <tr><td>LightGBM</td><td>直方圖分箱</td><td>先把連續值分成少數幾箱，搜尋只掃過各箱，不必每次排序全部資料。</td></tr>
  <tr><td>LightGBM</td><td>Leaf-wise 生長</td><td>每次挑目前收益最大的葉繼續長，要搭配葉數或深度限制。</td></tr>
  <tr><td>LightGBM</td><td>GOSS（Gradient-based One-Side Sampling）</td><td>保留梯度大的樣本，從梯度小的樣本中抽樣並補權重。</td></tr>
  <tr><td>LightGBM</td><td>EFB（Exclusive Feature Bundling）</td><td>把很少同時非零的稀疏特徵綁成一欄。</td></tr>
  <tr><td>CatBoost</td><td>對稱樹</td><td>同一層的節點共用同一個分裂條件，推論很快。</td></tr>
  <tr><td>CatBoost</td><td>有序目標統計</td><td>每筆資料的類別編碼，只用排在它前面的資料計算，避免自己的目標洩漏進來。</td></tr>
  <tr><td>CatBoost</td><td>Ordered boosting</td><td>這筆資料的預測由只看過前面資料的模型產生，梯度再用它自己的標籤計算，避免訓練時的預測太樂觀。</td></tr>
  <tr><td>CatBoost</td><td>MVS（Minimal Variance Sampling）</td><td>依梯度大小做重要性抽樣，和 GOSS 的目的類似。</td></tr>
  <tr><td>XGBoost 等</td><td>DART</td><td>像神經網路的 dropout：每一輪暫時拿掉部分舊樹再長新樹，避免後面的樹過度依賴少數舊樹。</td></tr>
  </tbody>
</table></div>
<p>直方圖的好處可以用計算量說明：建箱只要掃一次資料，之後每個節點的搜尋量和箱數成正比，不必像精確搜尋那樣每次排序全部資料。Lab 比較三個套件在分類、迴歸、速度與 Melbourne 類別資料上的表現；不同套件同名的參數（例如最少葉內資料量）意義未必相同，要對照各自的文件。</p>
"""

BART_STEP = r"""<p>每一輪依序更新 K 棵樹：先扣掉其他 K−1 棵樹的預測，得到這棵樹要負責的偏殘差；再對這棵樹做一個小擾動（長一刀、剪一刀，或改葉值），是否接受由 MCMC 決定。正則化來自偏好小樹、把每棵樹的葉值往 0 收縮的先驗，所以每棵樹只負責一小部分訊號。完整的後驗推導超出課本範圍（ISLP 也這麼說），見下方 BART 教材。</p>
"""


def ch8(b):
    # modern：正文的編碼小節與收合重複，縮成一段並指向收合
    cut(b, "modern", "<h3>類別特徵如何編碼</h3>", '<p class="source-links">',
        "<h3>類別特徵如何編碼</h3><p>講義比較三種做法：one-hot 用指示欄表示每個水準；"
        "label encoding 把水準編成整數，只有水準本身有順序時才合理；target encoding 用各類別的目標平均取代類別，"
        '但要小心目標洩漏。細節見下方<a href="#w09-detail-category-encoding">「類別編碼」</a>收合。</p>\n\n')
    rep(b, "modern", "$|T|$ 是葉子數、$w_m$ 是葉子的輸出值。",
        "$|T|$ 是葉子數、$w_m$ 是葉子的輸出值；這裡的 $\\lambda$ 是葉值的 L2 懲罰強度，不是 boosting 一節的學習率。")
    inner(b, "modern", "w09-detail-xgboost-math", XGB, "XGBoost 的二階近似（概念）")
    inner(b, "modern", "w09-detail-boost-engineering", ENGINEERING, "搜尋加速、CatBoost 與 DART：各一句話")
    cut(b, "modern", "平滑 $(n_c\\bar y_c+a\\bar y)/(n_c+a)$ 讓稀有組向整體平均收縮，但<strong>只有平滑仍沒有移除自己的目標</strong>。</p>",
        "<p>Melbourne Lab",
        "</p>\n<p>所以編碼對照只能用訓練資料估計；訓練資料本身也要用折外的方式編碼（講義的 K-fold target encoding），"
        "不能讓一筆資料的目標進入它自己的編碼。CatBoost 的有序目標統計是另一種避開洩漏的做法。</p>\n")

    # boosting：SAMME 與重複的「從殘差更新到損失函式的選擇」
    drop_p(b, "boosting", "<p>SAMME 的多類別寫法")
    cut(b, "boosting", "<h3>從殘差更新到損失函式的選擇</h3>", "<p>Lab 的 <code>GradientBoostingRegressor</code>")
    s = b["boosting"]
    n = len(re.findall(r"，不能直接稱為 SAMME；", s))
    if n != 1:
        raise ValueError(f"boosting: SAMME 句比對到 {n} 次")
    b["boosting"] = s.replace("，不能直接稱為 SAMME；", "；")
    rep(b, "boosting", "第 $m$ 輪在目前預測上算負梯度",
        "第 $m$ 輪（對應演算法 8.2 的第 $b$ 棵）在目前預測上算負梯度")
    rep(b, "boosting", "負梯度為 $y-p$，", "負梯度為 $y-p$（$p=1/(1+e^{-F})$），")
    rep(b, "boosting", "$0&lt;\\nu\\le1$ 是學習率", "$0&lt;\\nu\\le1$ 是學習率（演算法 8.2 的 $\\lambda$）")
    rep(b, "boosting", "<h3>AdaBoost 的權重尺度</h3><p>",
        "<h3>AdaBoost 的權重尺度</h3><p>這裡用 $m$ 當輪次，$a_m$ 就是上面 AdaBoost 收合裡的 $\\alpha_j$。")

    # stacking：BART 後驗推導、置換重要度
    cut(b, "stacking", "<h3>BART 每一輪究竟更新什麼</h3>", "<h3>樹數 K 與抽樣輪數 B 不要混成同一個參數</h3>",
        "<h3>BART 每一輪做什麼</h3>" + BART_STEP)
    drop_p(b, "stacking", "<p>Lab 的 <code>ISLP.bart.BART</code>")
    drop_p(b, "stacking", "<p>BART 的每次後驗抽樣")
    rep(b, "stacking", "每個保留輪的 $f^{(b)}(x)$ 已經把 K 棵樹加總", "每個保留輪的 $\\hat f^b(x)$ 已經把 K 棵樹加總")
    rep(b, "stacking", "<summary>BART 的完整模型、實作與後驗更新</summary>", "<summary>BART 的模型、演算法與參數</summary>")
    drop_p(b, "stacking", "<p>樹結構的提議可能被拒絕")
    rep(b, "stacking", "\\sum_{b = L+1}^{B} \\hat f^b(x)$$",
        "\\sum_{b = L+1}^{B} \\hat f^b(x)$$\n  <p>其中 $\\hat f^b$ 是第 $b$ 輪 K 棵樹的總和。</p>")
    drop_p(b, "stacking", "<p>置換重要度在指定評估資料上")
    drop_p(b, "stacking", "<p>高度相關的替代特徵可以彼此補償")
    rep(b, "stacking", "更不表示因果影響。</p>",
        "更不表示因果影響。</p>\n<p>另一種常見做法是<strong>置換重要度</strong>：在驗證資料上把某個變數的值打亂，"
        "看預測表現掉多少。它問的是「模型多依賴這個變數」，但同樣會被高度相關的變數互相稀釋。</p>")
    rep(b, "stacking", "（要方向請用 partial dependence 或 SHAP）",
        '（要看方向，得另外畫<a href="beyond_linearity.html#w08-detail-gam-effects">偏依賴圖</a>）')
    rep(b, "stacking", "<summary>如何讀變數重要度與置換重要度</summary>", "<summary>如何讀變數重要度</summary>")

    # 符號補定義
    rep(b, "prologue", "<p>對照線性迴歸的",
        "<p>其中 $M$ 是葉子數、$c_m$ 是第 $m$ 片葉的預測值；$\\mathbf{1}(X\\in R_m)$ 在 $X$ 落在 $R_m$ 時是 1，否則是 0。</p>\n\n  <p>對照線性迴歸的")
    rep(b, "grow", "<p>問題是——", "<p>其中 $\\hat y_{R_j}$ 是第 $j$ 塊內訓練資料 $y$ 的平均。問題是——")
    rep(b, "grow", "目前葉子數 |T|", "目前葉子數")
    rep(b, "grow", "若有 $m$ 個相異值，最多有 $m-1$ 個候選門檻值", "若有 $u$ 個相異值，最多有 $u-1$ 個候選門檻值")
    rep(b, "prune", "找讓下式最小的子樹 $T \\subset T_0$</p>",
        "找讓下式最小的子樹 $T \\subset T_0$（$T_0$ 是先長出來的那棵大樹）</p>")
    rep(b, "prune", "<h3>weakest-link 的臨界值</h3><p>把節點 $t$ 以下的整棵子樹 $T_t$ 收成一片葉",
        "<h3>weakest-link 的臨界值</h3><p>以內部節點 $t$ 為根的子樹記為 $T_t$，$|T_t|$ 是它的葉數，"
        "$R(\\cdot)$ 是訓練 RSS（分類樹則是對應的不純度）。把 $T_t$ 收成一片葉")
    rep(b, "prune", "對內部節點 $t$ 令 $d_t=R(t)-R(t_L)-R(t_R)$",
        "對內部節點 $t$ 令 $d_t=R(t)-R(t_L)-R(t_R)$（$t_L$、$t_R$ 是 $t$ 的左右子節點）")
    rep(b, "classtree", "是第 $m$ 個節點裡屬於第 $k$ 類的比例。",
        "是第 $m$ 個節點裡屬於第 $k$ 類的比例，$K$ 是類別數。")
    rep(b, "classtree", "accuracy 或 AUC 選", "accuracy 或 AUC（ROC 曲線下面積）選")
    rep(b, "bagging", "<p>分類問題就把平均換成",
        "<p>其中 $\\hat f^{*b}$ 是用第 $b$ 份 bootstrap 樣本長出來的樹。分類問題就把平均換成")
    s = b["boosting"]
    i = s.index("\\alpha_j = \\eta \\log")
    z = s.index("$$", i) + 2  # AdaBoost 更新式的結尾
    b["boosting"] = (s[:z] + "\n  <p>其中 $w_j(i)$ 是第 $j$ 輪第 $i$ 筆資料的權重，$\\eta$ 是控制更新幅度的係數；"
                     "這裡的 $\\alpha_j$ 和剪枝的 $\\alpha$ 無關。下面最終預測式裡的 $h_j(x)$ 是第 $j$ 個分類器的預測類別。</p>" + s[z:])


# ══ 第 7 章 ════════════════════════════════════════════════════════════
def ch7(b):
    # 自行實測的數字與推測
    rep(b, "loess", "比較淡紅曲線的鋸齒：span = 0.3 時，方框的最大折動約 1.06，tricube 只有約 0.39。",
        "比較淡紅曲線的鋸齒。")
    rep(b, "loess", "在 Wage 上用局部線性、tricube、不做穩健化實算，span 0.2、0.5、0.7、1.0 分別約是 10.6、4.9、3.7、2.4；span = 1.0 仍依距離加權，所以不會剛好是 2。",
        "span = 1.0 仍依距離加權，所以自由度不會剛好是 2。")
    cut(b, "loess", "<p>自由度的定義不只一種，比較時要看清楚。", "<h3>",
        "<p>自由度的定義不只一種，例如 $\\operatorname{tr}L$ 與 $\\operatorname{tr}(LL^{\\mathsf T})$；"
        "比較不同軟體或課本圖上標的自由度時，要先確認用的是哪一種。</p>\n")
    rep(b, "smooth", "在 Wage 上，節點放在分位數的 5 節點立方樣條（9 個參數）和 $\\mathrm{df}_\\lambda=9$ 的平滑樣條，擬合值最多差約 5.6 千美元。", "")
    rep(b, "smooth", "GCV 或 REML 選", "GCV（廣義交叉驗證）或 REML（限制最大概似）選")
    s = b["gam"]
    i = s.index('<div class="ic-title">加 df 換到多少</div>')
    z = s.index("</div>", s.index("</div>", i) + 6)
    b["gam"] = (s[:i] + '<div class="ic-title">year 需要非線性嗎</div>\n      '
                "lab 用 ANOVA 檢定 year 需不需要非線性項，結論是「year 需要線性項（p ≈ 0.002）但不需要非線性（p ≈ 0.435）」；"
                "同一套檢定用在 age，則顯示 age 明顯需要非線性（p ≈ 5.7e−07）。\n    " + s[z:])

    # 符號補定義
    rep(b, "smooth", "第 $k$ 個方向乘上 $1/(1+\\lambda d_k)$：",
        "第 $k$ 個方向乘上 $1/(1+\\lambda d_k)$，其中 $d_k\\ge0$ 衡量這個方向有多彎曲，愈彎曲愈大：")
    rep(b, "smooth", "<p>解是 $\\hat\\beta=", "<p>這裡 $B$ 的第 $i$ 列第 $j$ 行是 $b_j(x_i)$。解是 $\\hat\\beta=")
    rep(b, "smooth", "{1 - \\{S_\\lambda\\}_{ii}}\\right]^2$$",
        "{1 - \\{S_\\lambda\\}_{ii}}\\right]^2$$\n  <p>$\\hat g_\\lambda^{(-i)}$ 是拿掉第 $i$ 筆後重新擬合的函數。</p>")
    rep(b, "smooth", "pyGAM 以 20 個基底的 P-spline 近似平滑樣條", "pyGAM 以 20 個基底的 P-spline（懲罰樣條）近似平滑樣條")
    rep(b, "loess", "s = k/n 比例的訓練點。", "s = k/n 比例的訓練點（k 是鄰域點數、n 是總筆數）。")
    rep(b, "loess", "$\\hat y=Ly$，自由度是", "$\\hat y=Ly$（$L$ 的第 $i$ 列是第 $i$ 個點的局部權重組合），自由度是")
    rep(b, "loess", "令 $W_0=\\operatorname{diag}(K_{i0})$。",
        "令 $B_0$ 是以 $b_i^{\\mathsf T}$ 為各列的矩陣、$W_0=\\operatorname{diag}(K_{i0})$。")
    rep(b, "gam", "\\sum_j\\lambda_j\\beta_j^{\\mathsf T}S_j\\beta_j$，",
        "\\sum_j\\lambda_j\\beta_j^{\\mathsf T}\\Omega_j\\beta_j$（$\\Omega_j$ 是第 $j$ 項的曲率懲罰矩陣），")
    rep(b, "gam", "<strong>偏殘差圖</strong>把 $e_i+\\hat f_j(x_{ij})$ 對",
        "<strong>偏殘差圖</strong>把 $e_i+\\hat f_j(x_{ij})$（$e_i$ 是完整模型的殘差）對")
    rep(b, "gam", "完整 OLS 正常方程給 $X^Te=0$", "完整 OLS 正常方程給 $X^Te=0$（$e$ 是殘差向量）")
    rep(b, "gam", "+\\lambda_jJ(f_j)$", "+\\lambda_jJ(f_j)$（$J$ 是粗糙度懲罰，例如 $\\int f_j''^2$）")
    rep(b, "gam", "J(g)=\\iint(g_{11}^2+2g_{12}^2+g_{22}^2)\\,dx_1dx_2$。",
        "J(g)=\\iint(g_{11}^2+2g_{12}^2+g_{22}^2)\\,dx_1dx_2$，$g_{ab}$ 是對 $x_a$、$x_b$ 的二階偏導數。")
    rep(b, "gam", "$\\hat f_S(x_S)=n^{-1}\\sum_i\\hat f(x_S,x_C^{(i)})$。",
        "$\\hat f_S(x_S)=n^{-1}\\sum_i\\hat f(x_S,x_C^{(i)})$，其中 $S$ 是要看的特徵，$C$ 是其餘特徵，$x_C^{(i)}$ 是第 $i$ 筆資料的其餘特徵值。")
    rep(b, "gam", "加法結構放在連結函數 $g$ 上，而不是加性誤差。",
        "加法結構放在連結函數 $g$ 上，而不是加性誤差（這個 $g$ 和平滑樣條的 $g$ 無關）。")
    rep(b, "smooth", "g''\\in L^2[a,b]\\}$", "g''\\in L^2[a,b]\\}$（$L^2$ 指平方可積）")
    rep(b, "smooth", "<p>我們沒有事先假設 $g$ 是樣條", "<p>表中的 $m$ 是導數的階數，和前面的相異設計點數 $m$ 無關。我們沒有事先假設 $g$ 是樣條")
    rep(b, "gam", "令 $K_{ij}=\\eta(\\|x_i-x_j\\|)$", "令 $K_{ij}=\\eta(\\|x_i-x_j\\|)$（這個 $K$ 是核矩陣，和局部迴歸的權重 $K$ 無關）")
    rep(b, "gam", "<p><strong>PDP 的用途。</strong>", "<p><strong>偏依賴圖（partial dependence plot, PDP）的用途。</strong>")
    rep(b, "gam", "<summary>效果圖怎麼讀：成分圖、偏殘差圖、部分迴歸圖與 PDP</summary>",
        "<summary>效果圖怎麼讀：成分圖、偏殘差圖、部分迴歸圖與偏依賴圖</summary>")
