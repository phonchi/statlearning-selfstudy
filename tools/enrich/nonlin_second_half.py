"""第 7 章後半（平滑樣條之後）依講義與教學對話再修訂，並接到第 8 章。

在 nonlin_lecture_notes 之後套用；替換字串都要恰好出現一次，上游改了會直接報錯。
"""
from trees_lecture_notes import block, cut, rep
from lib import detail


def smooth(b):
    rep(b, "smooth", "每個刻度對應一個 λ，df 較容易用來比較複雜度。",
        "每個刻度對應一個 λ，df 較容易用來比較複雜度。"
        "課本圖 7.8 比較 16 df 與留一交叉驗證選出的 6.8 df 兩條曲線，在這份資料上兩者差別不大。")


LOESS_MOTIVE = r"""<p>放回本章的兩條主線看。基底展開走到這裡變成<strong>局部</strong>的：每個 $x_0$ 各用一組以自己為中心的基底 $1,(x-x_0)$（演算法 7.1 寫成 $\beta_0+\beta_1x$，只是參數化不同），係數 $\hat\beta(x_0)$ 隨目標點改變；迴歸樣條則是整條曲線共用同一組係數。線性平滑器那條線照樣成立：權重只看距離、不看 $y$，所以擬合值仍是 $y$ 的線性組合，$\hat y=Ly$，自由度是 $\operatorname{tr}L$，跨距扮演平滑樣條裡 $\lambda$ 的角色（前提是固定跨距、不做穩健化）。</p>"""


def loess(b):
    rep(b, "loess", "<p>這裡沒有一組全域基底：每個 $x_0$ 各用自己的局部基底 $1,(x-x_0)$。不過擬合值仍是 $y$ 的線性組合，所以它還是線性平滑器。</p>",
        LOESS_MOTIVE)
    rep(b, "loess", "所以局部迴歸主要用在 1～2 維，或者當 GAM 的單變數積木。",
        "所以局部迴歸主要用在 1～2 維，或者當 GAM 的單變數積木。"
        '第 8 章的樹換一種方式定義「附近」：由資料決定怎麼切，同一片葉子裡的點就是鄰居。')
    rep(b, "loess", "下一個目標點要重新選鄰居、權重和局部係數。",
        "下一個目標點要重新選鄰居、權重和局部係數。"
        "擬合值剛好等於截距，是因為基底以 $x_0$ 為中心：其他基底在 $x=x_0$ 都是 0。"
        "把 $\\hat f(x_0)$ 展開成 $\\sum_i w_i^*(x_0)\\,y_i$，這些等價權重不一定等於原本的核權重，也不一定全是正的；"
        "局部直線在邊界會給某些點負權重，用來修正鄰居只在單側造成的偏差。")


GAM_MOTIVE = r"""
  <p>兩條主線在這裡會合。走基底展開那條路：每個 $f_j$ 展開成一組基底，橫向疊成一個大設計矩陣，一次最小平方（或加懲罰）就擬合完。走平滑器那條路：把一維平滑器輪流套在<strong>偏殘差</strong>上，一次更新一個 $f_j$，這叫 backfitting。GAM 指的是加法結構本身，這兩種只是估計方法；固定基底、二次懲罰時，兩者的答案也一樣。代價是<strong>加法</strong>本身：$f_j$ 之間不會自己長出交互作用，要就得自己指定。自動找交互作用是<a href="tree_based_methods.html#motive">第 8 章的樹</a>擅長的事。</p>
"""

EFFECT_EXTRA = r"""<p><strong>名字對照。</strong>偏殘差圖（partial residual plot）也叫 component-plus-residual plot（CR 圖，statsmodels 叫 CCPR），兩者是同一種圖。部分迴歸圖（partial regression plot）又叫 added-variable plot（AV 圖），兩軸都是殘差，是不同的圖。ISLP 圖 7.11–7.13 只畫中心化的 $\hat f_j$ 和 ±2 個標準誤，沒有畫殘差點，所以是成分圖。</p>
<p><strong>偏殘差圖會誤導的時候。</strong>$r_{ij}=y_i-\hat\beta_0-\sum_{k\ne j}\hat f_k(x_{ik})$ 扣掉的只是<strong>模型估出來的</strong>其他效果。預測變數彼此高度相關，或模型漏了交互作用時，扣錯的部分會留在圖上，看起來像是 $x_j$ 的效果。backfitting 每一步拿去平滑的，就是這張圖上的 $(x_j,r_j)$：圖是用眼睛看，backfitting 是真的拿去擬合。</p>
<p><strong>PDP 的用途。</strong>模型擬合之後，PDP 回答「平均而言，這個特徵怎麼影響預測」，讀法類似迴歸係數，可以套在任何模型上。例如房價模型裡經緯度與房價的關係，或某種飲食對健康指標的平均影響。目標特徵和其他特徵高度相關時，PDP 會拿去評估資料裡很少出現的組合，解讀要小心，下面會再說明。</p>
"""


def gam(b):
    g = b["gam"]
    i = g.index('<span class="info-label">模型定義和估計方法是兩回事</span>')
    a = g.rindex('<div class="info-box warm">', 0, i)
    z = g.index("</div>", i) + len("</div>")
    b["gam"] = g[:a] + g[z:].lstrip("\n")
    # A11：「各自擬合、再加起來」會被讀成各自對 y 做單變數迴歸
    rep(b, "gam", "每個 $f_j$ 各自擬合、再加起來。",
        "估計時每個 $f_j$ 都要考慮其他成分，不是各自對 $y$ 做單變數迴歸再加總。")
    rep(b, "gam", r"""+ f_p(x_{ip}) + \varepsilon_i \tag{7.15}$$
""", r"""+ f_p(x_{ip}) + \varepsilon_i \tag{7.15}$$
""" + GAM_MOTIVE)
    # 合併 backfit 收合裡重複的兩套更新步驟：留下有編號的版本
    cut(b, "gam", '<div class="detail-body"><div class="info-box">\n  <span class="info-label">逆向擬合在做什麼</span>',
        "<h3>讓加法成分可識別的 backfitting</h3>", '<div class="detail-body">')
    rep(b, "gam", "再循環更新每一個 $j$：</p>",
        "再循環更新每一個 $j$。好處是只要有一維的擬合工具，就能擬合任意多變數的加法模型；"
        "ISLP §7.9 第 11、12 題用線性迴歸版本讓你手動跑一遍。</p>")
    rep(b, "gam", "不能直接對 $0/1$ 反應套普通 backfitting。</p>",
        "不能直接對 $0/1$ 反應套普通 backfitting。</p>"
        "<p>那什麼時候真的需要 backfitting？自然樣條這類固定基底，直接聯合最小平方最簡單；"
        "局部迴歸沒有一組全域基底，沒辦法橫向疊成設計矩陣，這時 backfitting 最方便。"
        "現代套件如 R 的 <code>mgcv</code> 用懲罰迴歸樣條做聯合估計，非高斯反應則用懲罰的 IRLS（PIRLS）。</p>")
    rep(b, "gam", "這是圖 7.12。</p>",
        "這是圖 7.12。</p>\n<p>講義的設定是 year 用 4 df、age 用 5 df；"
        "換成同樣自由度的平滑樣條，在這個例子裡兩種 GAM 的結果差別很小。</p>")
    rep(b, "gam", "每一張都是一個 $\\hat f_k$ 的<strong>偏依賴圖</strong>",
        "每一張都是一個 $\\hat f_k$ 的<strong>成分圖</strong>（加法模型裡，它和偏依賴圖只差一個常數）")
    # 效果圖：從薄板收合拆出來，放到 GAM 三張圖後面
    a, z = block(b["gam"], "w08-detail-gam-thinplate")
    tp = b["gam"][a:z]
    s = tp.index("<h3>四種效果圖如何回答不同問題？</h3>")
    _, pz = block(tp, "w08proof-fwl")
    effect = tp[s + len("<h3>四種效果圖如何回答不同問題？</h3>"):pz]
    tp = tp[:s] + tp[pz:]
    tp = tp.replace("<summary>延伸：薄板樣條、效果圖與部分迴歸</summary>",
                    "<summary>延伸：薄板樣條與二維交互作用</summary>")
    b["gam"] = b["gam"][:a] + tp + b["gam"][z:]
    new = detail("w08-detail-gam-effects", "效果圖怎麼讀：成分圖、偏殘差圖、部分迴歸圖與 PDP",
                 effect.replace("<p><strong>PDP</strong> 每次固定目標特徵值", EFFECT_EXTRA + "<p><strong>PDP</strong> 每次固定目標特徵值"))
    mark = '<div style="overflow-x:auto;"><table class="cmp-table" style="width:100%;font-size:.85rem;">\n  <thead><tr><th>GAM 的優點 ✔</th>'
    rep(b, "gam", mark, new + "\n" + mark)
    rep(b, "gam", "<div class=\"detail-body\"><p>ISLP 圖 7.13 對 <code>Wage</code> 擬合 $I(\\text{wage} > 250)$，",
        "<div class=\"detail-body\"><p>講義的模型是 $\\operatorname{logit}P(\\text{wage}&gt;250)=\\beta_0+\\beta_1\\,\\text{year}+f_2(\\text{age})+f_3(\\text{education})$："
        "year 只用線性項，$f_2$ 是 5 df 的平滑樣條，$f_3$ 是每個學歷一個常數的階梯函數。</p>"
        "<p>ISLP 圖 7.13 對 <code>Wage</code> 擬合 $I(\\text{wage} > 250)$，")
    rep(b, "gam", "先檢查列聯表中的類別計數。</strong></p></div></details>",
        "先檢查列聯表中的類別計數。</strong>重配之後，age 與 education 對高收入機率的影響遠大於 year。</p></div></details>")


def augment(bodies):
    smooth(bodies)
    loess(bodies)
    gam(bodies)
    return bodies
