"""第 7 章依講義與教學筆記再修訂：基底展開與線性平滑器兩條主線。

在 reading_flow、teaching_scope、lecture_alignment 之後才套用，所以比對的是已收合的段落。
每個替換都要求比對字串恰好出現一次，上游文字改了會直接報錯，不會靜默失效。
"""
import re

from lecture_alignment_ch7 import extend
from lib import detail, info, info_card, rows_card, svg, table, viz


def rep(bodies, sec, old, new):
    n = bodies[sec].count(old)
    if n != 1:
        raise ValueError(f"{sec}: 比對到 {n} 次：{old[:50]}")
    bodies[sec] = bodies[sec].replace(old, new)


def cut(bodies, sec, start, end, new=""):
    """把 start（含）到 end（不含）之間換成 new。"""
    b = bodies[sec]
    if b.count(start) != 1:
        raise ValueError(f"{sec}: 起點比對到 {b.count(start)} 次：{start[:50]}")
    a = b.index(start)
    z = b.find(end, a + len(start))
    if z < 0:
        raise ValueError(f"{sec}: 找不到終點：{end[:50]}")
    bodies[sec] = b[:a] + new + b[z:]


# ── 開場：兩條主線 ─────────────────────────────────────────────────────
def prologue(b):
    rep(b, "prologue", "<strong>把 x 換成一組事先選好的固定轉換</strong>",
        "<strong>把 x 換成一組在估係數之前就決定好的轉換</strong>")
    rep(b, "prologue", """所以第 3 章那一整套
  最小平方、標準誤、F 檢定，全部可以照用，只是預測變數換人了。""",
        """所以第 3 章的最小平方可以照用，只是預測變數換人了。""")
    rep(b, "prologue", "六條路線，一個框架", "六條路線，兩條主線")
    cut(b, "prologue", "前四個是同一個<strong>基底函數</strong>框架的特例", "</div>",
        r"""<strong>主線一：基底展開。</strong>前四個都是選好基底，再用最小平方估係數（§7.3）。平滑樣條用的也是基底，只是多了懲罰；GAM 則是每個變數各一組基底，再加起來（§7.7）。<br>
  <strong>主線二：線性平滑器。</strong>固定調整參數時，六種方法的擬合值都能寫成 $\hat y=Sy$，自由度都用 $\operatorname{tr}S$ 衡量（穩健化的局部迴歸除外）。局部迴歸沒有一組全域基底，但也屬於這一條。
""")
    rep(b, "prologue", "非線性模型的共同框架與選擇依據", "如何在這些方法之間選擇")
    cut(b, "prologue", "<p>「對變數非線性」不代表「對係數非線性」。", "<p>先問三件事：")


# ── §7.1：信賴區間 ─────────────────────────────────────────────────────
CI_COMPARE = table(
    ["", "多元線性迴歸", "多元 logistic 迴歸"],
    [["估計目標", r"$E[Y\mid x_0]$", r"$\pi_0=P(Y=1\mid x_0)$"],
     ["線性預測量", r"$\hat\eta_0=x_0^{\mathsf T}\hat\beta$", r"$\hat\eta_0=x_0^{\mathsf T}\hat\beta$（logit 尺度）"],
     ["標準誤", r"$\sqrt{x_0^{\mathsf T}\hat Vx_0}$", r"$\sqrt{x_0^{\mathsf T}\hat Vx_0}$"],
     [r"$\hat V=\widehat{\operatorname{Cov}}(\hat\beta)$", r"$\hat\sigma^2(X^{\mathsf T}X)^{-1}$，$\hat\sigma^2=\mathrm{RSS}/(n-q)$",
      r"$(X^{\mathsf T}\hat WX)^{-1}$，$\hat W=\operatorname{diag}\{\hat\pi_i(1-\hat\pi_i)\}$"],
     ["區間的分位數", "$t_{n-q}$（常態誤差下是精確的）", "標準常態，1.96（大樣本近似）"],
     ["最後一步", "不用轉換", "兩端各代入 inverse logit"]])

CI_NOTES = r"""<h3>兩種迴歸共用同一個骨架</h3>
<p>令 $x_0=(1,x_{01},\ldots,x_{0p})^{\mathsf T}$；多項式與樣條只是把它換成基底向量 $b(x_0)$。兩種迴歸都先估線性預測量 $\hat\eta_0=x_0^{\mathsf T}\hat\beta$。它是係數的線性組合，所以 $\operatorname{Var}(\hat\eta_0)=x_0^{\mathsf T}\operatorname{Cov}(\hat\beta)x_0$，標準誤也就有了。不同的只有三處：係數的共變異數矩陣、用哪個分位數、最後要不要轉回機率。這裡 $q$ 是含截距的係數個數。</p>
""" + CI_COMPARE + r"""
<p>線性迴歸需要常態、等變異、獨立誤差與滿秩設計。只有一個預測變數時，矩陣式化簡成常見的</p>
$$\hat y_0\pm t\,\hat\sigma\sqrt{\frac1n+\frac{(x_0-\bar x)^2}{\sum_i(x_i-\bar x)^2}},$$
<p>它只是兩欄設計的特例，不能原封不動套到四次模型。要預測一個新觀測值，根號內再加 1，因為新觀測自己也有誤差。</p>
<h3>從 logit 的信賴區間回到機率</h3>
<p>logistic 函數嚴格遞增，所以把 logit 尺度的兩端點 $L=\hat\eta_0-1.96\,\mathrm{SE}$、$U=\hat\eta_0+1.96\,\mathrm{SE}$ 各自轉回去就好：</p>
$$\left[\frac1{1+e^{-L}},\ \frac1{1+e^{-U}}\right].$$
<p>舉例：$\hat\eta_0=1$、$\mathrm{SE}=0.3$，則 $\hat\pi_0\approx0.731$。logit 尺度的區間是 $[0.412,1.588]$，轉回機率是 $[0.602,0.830]$。端點一定落在 0 到 1 之間，而且區間不對稱：下方差 0.129，上方差 0.099。</p>
""" + info("標準誤是哪個尺度的？",
           r"""這個標準誤屬於 logit 尺度，大於 1 也不奇怪（講義連結的討論串就有 6.14），不能直接拿去和機率相加減。另外，區間估的是條件機率 $\pi_0$。個別的 $Y_0$ 只會是 0 或 1，不能說它有 95% 的機率落在 $[0.602,0.830]$。小樣本、稀有事件或完全分離時，常態近似也可能失準。""",
           "warm") + r"""
<h3>另外兩件要分清楚的事</h3>
<p><strong>係數的區間與機率的區間不同。</strong>單一係數用 $\hat\beta_j\pm1.96\,\mathrm{SE}(\hat\beta_j)$，取指數後是 odds ratio 的區間 $\left[e^{\hat\beta_j-1.96\,\mathrm{SE}},\ e^{\hat\beta_j+1.96\,\mathrm{SE}}\right]$；機率的區間則要用整個 $x_0^{\mathsf T}\hat Vx_0$。</p>
<p><strong>逐點區間不保證整條曲線。</strong>圖 7.1 的虛線在每個固定的 $x_0$ 各有約 95% 的涵蓋率；要讓整條曲線同時被涵蓋，區間必須更寬，不能在每個點都用 1.96。</p>
<p>實作上，Lab 對線性模型用 <code>get_prediction</code>；logistic 可以用 <code>cov_params()</code> 與 <code>scipy.special.expit</code> 手算，也可以改用 Binomial GLM 的 <code>get_prediction</code>。</p>
"""


def poly(b):
    rep(b, "poly", "深入計算：係數、基底與信賴區間", "深入計算：係數、基底與標準誤")
    cut(b, "poly", r"$$\widehat{\operatorname{Var}}\{\hat f(x_0)\}=b(x_0)^T", "<p>Lab 的 <code>plot_wage_fit</code>",
        "<p>區間的完整推導，以及線性和 logistic 的對照，放在本節最後的收合。</p>\n")
    rep(b, "poly", r"再畫 $\hat f\pm2s_f$。", r"再畫 $\hat f\pm2\,\mathrm{SE}$。")
    rep(b, "poly", "機率的信賴區間：logit 轉換", "信賴區間的推導：線性迴歸與 logistic 迴歸")
    cut(b, "poly", "<h3>從 logit 的信賴區間回到機率</h3>", '<details class="qa-item proof" id="w08proof-logit">', CI_NOTES)


# ── §7.2：階梯函數 ─────────────────────────────────────────────────────
def step(b):
    rep(b, "step", "例如把年齡分成四段，就得到四個段內平均。</p>",
        "例如把年齡分成四段，就得到四個段內平均。讀課本圖 7.2 時留意：切點處那段短斜線只是畫圖時把相鄰格點連起來的視覺效果。模型本身在切點是垂直跳躍，虛線的信賴區間也一樣。</p>")
    rep(b, "step", r"""\tag{7.5}$$
""", r"""\tag{7.5}$$

  <p>為什麼 $C_0$ 要丟？每個 $X$ 恰好落在一段裡，所以 $\sum_{j=0}^{K}C_j(X)=1$，而右邊的 1 正是截距那一欄。把截距和全部 $K+1$ 個指示變數一起放進去，設計矩陣就完全共線，係數無法唯一估計。以切點 35、50、65 為例：</p>
""" + table(["區間", "$X&lt;35$", r"$35\le X&lt;50$", r"$50\le X&lt;65$", r"$X\ge65$"],
            [["預測平均", r"$\beta_0$", r"$\beta_0+\beta_1$", r"$\beta_0+\beta_2$", r"$\beta_0+\beta_3$"]]) + "\n")
    cut(b, "step", "<p>若保留所有組別的 indicator，就不另加截距", "<p>Lab 的四個年齡區段分別估計平均薪資。")
    rep(b, "step", "這是在加入可解讀的交互作用，並不會讓分段常數自動變得連續。</p>",
        """這是在加入可解讀的交互作用，並不會讓分段常數自動變得連續。</p>
<p>自己畫圖時，用 <code>plt.step(x_grid, y_pred, where="post")</code>，並讓格點包含切點，跳躍才會落在正確位置。同一區間內的基底向量都一樣，所以預測值和逐點標準誤也都是常數，信賴區間同樣呈階梯狀。</p>""")


# ── §7.3：基底函數 ─────────────────────────────────────────────────────
BASIS_TABLE = table(
    ["方法", "基底或特徵", "怎麼決定"],
    [["Taylor 展開", "$(x-a)^k$", "形式固定；係數由 $a$ 點的導數決定"],
     ["多項式", "$x^k$", "形式固定；係數由資料估"],
     ["Fourier", r"$\sin kx,\ \cos kx$", "形式固定；適合週期函數"],
     ["Wavelet", r"$\psi_{j,k}(x)$", "形式固定；不同位置與尺度，適合局部特徵"],
     ["Spline", "$b_k(x)$", "形式固定；節點常依分位數放"],
     ["PCR", r"$Z_k=a_k^{\mathsf T}X$", "從 $X$ 學方向"],
     ["PLS", r"$Z_k=w_k^{\mathsf T}X$", "從 $X$ 與 $Y$ 學方向"],
     ["神經網路隱藏層", r"$\sigma(w_k^{\mathsf T}X+c_k)$", "和輸出層一起訓練；對 $X$ 是非線性的"]])

BASIS_DETAIL = detail("w08-detail-basis-fixed-learned", "基底可以固定，也可以學：從 Taylor 到 PCR、PLS", r"""
<p>這些方法都先把原始變數換成新特徵 $\phi_1(X),\ldots,\phi_K(X)$，再擬合</p>
$$Y=\beta_0+\sum_{k=1}^{K}\theta_k\phi_k(X)+\varepsilon.$$
<p>模型對係數 $\theta_k$ 是線性的，對 $X$ 則可以是非線性的。差別在於特徵從哪裡來。</p>
""" + BASIS_TABLE + r"""
<p><strong>Taylor 展開是最熟悉的例子。</strong>對在 $a$ 附近等於自身 Taylor 級數的函數，$f(x)=\sum_{k=0}^{\infty}f^{(k)}(a)(x-a)^k/k!$，也就是用多項式基底表示函數，只是係數來自導數。截到有限項後只是近似，而且離 $a$ 愈遠通常愈差。迴歸改用整批資料估係數，但全域多項式在遠處失控的毛病還在，這正是接下來改用分段多項式的理由。<a href="classification.html#w04-detail-logistic-fit">第 4 章的 logistic 擬合</a>用過一次 Taylor 線性化，下一節則用它解釋樣條的連續條件。</p>
<p><strong>兩種「基底」的數學意義不同。</strong>Taylor、Fourier、Wavelet、Spline 是在函數空間裡選一組積木；<a href="model_selection.html#pcr">PCR</a>、<a href="model_selection.html#pls">PLS</a> 是在預測變數空間裡換座標。例如 $Z_1=0.6X_1+0.8X_2$：即使方向是學來的，$\beta Z_1$ 對 $X_1,X_2$ 仍是線性的，所以<strong>學到特徵不等於模型變成非線性</strong>。要讓學到的特徵也對 $X$ 非線性，就得像<a href="deep_learning.html#single">神經網路</a>那樣加上非線性的激活函數。</p>
<p>PCR 和 PLS 的得分通常同時依賴多個 $X_j$，因此也不具備 GAM 的 $f_1(X_1)+\cdots+f_p(X_p)$ 結構。特徵是看同一份資料學來的話，把它當成固定基底算標準誤也會太樂觀。</p>
<p>一個模型可以拆成三層來看：</p>
<ul>
<li><strong>特徵表示：</strong>怎麼表示原始資料，例如多項式、樣條、PCR、PLS。</li>
<li><strong>模型結構：</strong>怎麼組合特徵，例如線性、加法、含交互作用。</li>
<li><strong>估計：</strong>怎麼估係數，例如 OLS、MLE、懲罰最小平方。</li>
</ul>
<p>GAM 主要是在第二層指定加法結構，通常在第一層用樣條基底，在第三層用懲罰避免過度擬合。</p>
""")


def basis(b):
    rep(b, "basis", """<p>關鍵是 $b_1(\\cdot), \\ldots, b_K(\\cdot)$ <strong>事先選定、固定、已知</strong>。
  它們不含要估的參數。於是 (7.7) 就是一個以 $b_1(x_i), \\ldots, b_K(x_i)$ 為預測變數的
  標準線性模型，最小平方、標準誤、F 檢定原封不動搬過來。</p>""",
        """<p>關鍵是 $b_1(\\cdot), \\ldots, b_K(\\cdot)$ <strong>在估係數之前就固定了，本身不含要估的參數</strong>。
  於是 (7.7) 就是一個以 $b_1(x_i), \\ldots, b_K(x_i)$ 為預測變數的標準線性模型，
  最小平方可以照搬，分類時則沿用 GLM。基底沒有依同一份資料反覆挑選時，標準誤與 F 檢定也一樣成立。</p>

  <p>「把 x 換成新特徵，再做線性模型」你已經見過。Taylor 展開用的是固定的多項式基底；第 6 章的 PCR、PLS 則先從資料學出新特徵，再做迴歸。這一章的基底大多固定，學出來的版本放在下面的收合對照。</p>""")
    rep(b, "basis", """  換基底就換方法，但擬合方法（最小平方）從頭到尾沒換過。
  小波（wavelet）與傅立葉級數也是合法的選擇，只是這一章不講。""",
        "  換基底就換方法，但擬合方法（最小平方）從頭到尾沒換過。")
    sandbox = '<details class="qa-item reading-detail" id="w08-detail-basis-sandbox">'
    rep(b, "basis", sandbox, BASIS_DETAIL + "\n" + sandbox)
    rep(b, "basis", "基底函數框架要求 $b_1(\\cdot), \\ldots, b_K(\\cdot)$ 必須「事先選定、固定且已知」。",
        "基底函數框架要求 $b_1(\\cdot), \\ldots, b_K(\\cdot)$ 在估係數之前就固定，本身不含要估的參數。")


# ── §7.4：樣條 ─────────────────────────────────────────────────────────
DERIVE_NOTES = r"""
<h3>截斷冪基底從哪裡來？</h3>
<p>它可以由連續條件直接推出來。設節點 $c$ 左右是兩個至多三次的多項式 $p_1,p_2$，令 $q=p_2-p_1$。連續條件要求 $q(c)=q'(c)=q''(c)=0$，也就是 $c$ 至少是 $q$ 的三重根。$q$ 至多三次，所以只能是 $q(x)=\gamma(x-c)^3$，於是</p>
$$f(x)=p_1(x)+\gamma(x-c)_+^3.$$
<p>這條式子是精確的改寫，沒有近似。有多個節點時，每過一個節點就多一項，係數</p>
$$\gamma_j=\frac{f'''(c_j^+)-f'''(c_j^-)}{3!}$$
<p>控制三階導數在該節點跳多少。</p>
<h3>把限制放進模型的兩種做法</h3>
<p>以單一節點為例，把兩段都寫成 $(x-c)$ 的多項式，係數分別是 $a_0,\ldots,a_3$ 與 $b_0,\ldots,b_3$。連續條件就是 $a_0=b_0$、$a_1=b_1$、$a_2=b_2$，所以 $8-3=5$ 個自由參數，只有最高次係數可以不同。</p>
<p><strong>做法一：限制式最小平方。</strong>解 $\min_\beta\|Y-Z\beta\|^2$，受限於 $A\beta=0$。用 Lagrange 乘數得到下面的線性系統：</p>
$$\begin{pmatrix}Z^{\mathsf T}Z&amp;A^{\mathsf T}\\A&amp;0\end{pmatrix}\begin{pmatrix}\hat\beta\\\hat\nu\end{pmatrix}=\begin{pmatrix}Z^{\mathsf T}Y\\0\end{pmatrix}.$$
<p><strong>做法二：換基底。</strong>令 $\gamma=b_3-a_3$，模型變成 $a_0+a_1(x-c)+a_2(x-c)^2+a_3(x-c)^3+\gamma(x-c)_+^3$。不管係數估出來是多少，連續條件都自動成立，所以直接做 OLS 就好。</p>
<p>解唯一時，兩種做法給出同一條擬合曲線。實務上幾乎都用第二種：<strong>基底函數就是把連續限制寫進模型的參數化</strong>。節點有 $K$ 個時，$4(K+1)-3K=K+4$，剛好等於截斷冪基底的個數。</p>
"""

WHY_D1 = r"""<p>再看多一階。$d$ 次多項式在 $c$ 的 Taylor 展開是精確的：$p(x)=\sum_{k=0}^{d}p^{(k)}(c)(x-c)^k/k!$。所以兩個至多 $d$ 次的多項式若在 $c$ 的第 $0$ 到第 $d$ 階導數全部相同，Taylor 係數就全部相同，<strong>兩段其實是同一個多項式</strong>，節點等於不存在。</p>
     <p>只要求到第 $d-1$ 階時，最高次係數還能不同：$p_2(x)=p_1(x)+a(x-c)^d$。這一項在 $c$ 的前 $d-1$ 階導數都是 0，不破壞連續；第 $d$ 階導數則可以改變，留下彈性。這就是「導數連續到 $d-1$ 階」的來源：<strong>它是還能保留彈性的最高要求</strong>。這是標準樣條的定義，數學上並非只能如此：只要求到較低階也可行，重複節點就會降低連續性。</p>
""" + table(["樣條次數", "0", "1", "2", "3", "$d$"],
            [["連續性", "不要求（階梯函數）", "$C^0$", "$C^1$", "$C^2$", "$C^{d-1}$"]]) + r"""
     <p>"""


def splines(b):
    rep(b, "splines", "含截距時共有 K＋4 個自由度。</p>", r"""含截距時共有 K＋4 個自由度。</p>
<p>為什麼要接起來？<strong>節點是我們為了建模選的位置，不代表真實函數在那裡會突然改變。</strong>如果相信 $E[Y\mid X=x]$ 是平滑的，就不該讓人為的切點造成跳躍或折角。但母體的迴歸函數不一定連續：假如 65 歲才開始領補助，平均收入就可能在 65 歲跳一格，即使年齡本身是連續變數。這種已知的門檻，保留跳躍才合理。</p>
<p>連續條件也不必另外解。換一組自動滿足條件的基底，問題就變回普通最小平方；實務上用的是數值比截斷冪穩定的 B-spline。</p>""")
    cut(b, "splines", "<p>再看多一階。三次多項式的三階導數是常數", "書上還補了一句很實用的話：", WHY_D1)
    rep(b, "splines", "Q：為什麼三次樣條剛好要求到<strong>二階</strong>導數連續？多一階或少一階會怎樣？",
        "Q：為什麼三次樣條剛好要求到<strong>二階</strong>導數連續？少一階或多一階會怎樣？")
    rep(b, "splines", '<h3>一次樣條與一般次數</h3>', DERIVE_NOTES + '<h3>一次樣條與一般次數</h3>')


PRACTICE_NOTES = r"""
<h3>實務上用的樣條家族</h3>
""" + table(["名稱", "基底", "複雜度怎麼控制", "在哪裡會遇到"],
            [["迴歸樣條", "截斷冪或 B-spline", "節點數", "<code>bs()</code>"],
             ["自然樣條", "B-spline 加邊界條件，或以節點上的值參數化", "節點數", "<code>ns()</code>、patsy <code>cr()</code>"],
             ["平滑樣條", "每個相異 $x$ 一個節點", r"$\lambda$", "精確解的理論形式"],
             ["P-spline", "較多的等距 B-spline", r"$\lambda$，懲罰係數的差分", "pyGAM 的 <code>s()</code>（預設 20 個基底）"]]) + r"""
<p>P-spline（Eilers 與 Marx）解 $\min_\beta\|y-B\beta\|^2+\lambda\|D\beta\|^2$，$D$ 是相鄰係數的差分。它用較多節點，不必細選位置，再靠懲罰控制彎曲；差分懲罰近似曲率懲罰，不是同一個量。mgcv 也採類似框架，自動選各項的 $\lambda$。</p>
<p><strong>連續性限制和平滑懲罰是兩回事</strong>：前者由基底保證，讓各段在節點接得平滑；後者控制整條曲線彎多少，用來避免過度擬合。</p>
"""

FIG76_NOTES = r"""<h3>圖 7.6 的 df 為什麼從 1 開始？</h3>
<p>$K$ 個內部節點的立方樣條有 $K+4$ 個自由度，最少也是 4，但圖上兩個面板的橫軸都從 1 起算。主要原因是這張圖的 df <strong>不含截距</strong>：</p>
""" + table(["模型", "總自由度", "不含截距"],
            [["線性迴歸", "2", "1"], ["三次多項式", "4", "3"],
             ["立方樣條（$K$ 個內部節點）", "$K+4$", "$K+3$"],
             ["自然樣條（$K$ 個內部節點）", "$K+2$", "$K+1$"]]) + r"""
<p>截距只把曲線上下平移，所有模型都有，不增加函數形狀的彈性，所以比較彈性時常把它扣掉。估變異數時它仍然要算進去：簡單線性迴歸的 $\hat\sigma^2$ 分母是 $n-2$。例如 <code>lm(y ~ bs(x, df=5))</code> 的基底有 5 欄，加上截距共 6 個係數。</p>
<p>扣掉截距後，自然樣條最少是 1（沒有內部節點時就是直線），但立方樣條最少還是 3。所以右圖的 df = 1、2 不可能是完整的立方樣條。課本只明說 df = 1 是線性迴歸；df = 2 大概是二次多項式，這是推論，書上沒有交代。</p>
"""


def natural(b):
    rep(b, "natural", "立方樣條的 K + 4 個參數因此減為自然立方樣條的 <strong>K + 2</strong> 個。</p>",
        "立方樣條的 K + 4 個參數因此減為自然立方樣條的 <strong>K + 2</strong> 個，等於少了兩個基底。</p>")
    rep(b, "natural", "<h3>對照 Lab 的七欄與六欄</h3>", FIG76_NOTES + "<h3>對照 Lab 的七欄與六欄</h3>")
    rep(b, "natural", '<p class="source-links">本主題的講義來源與延伸閱讀：<a href="https://stats.stackexchange.com/questions/233232',
        PRACTICE_NOTES + '<p class="source-links">本主題的講義來源與延伸閱讀：<a href="https://stats.stackexchange.com/questions/233232')


# ── §7.5：平滑樣條 ─────────────────────────────────────────────────────
SHRINK_MAIN = r"""
  <p>所以平滑樣條同樣是基底展開。把 $g$ 寫成 $\sum_j\beta_jb_j$ 代回 (7.11)，就得到</p>
  $$\min_\beta\ \|y-B\beta\|^2+\lambda\beta^{\mathsf T}\Omega\beta,\qquad \Omega_{jk}=\int b_j''(t)b_k''(t)\,dt,$$
  <p>解是 $\hat\beta=(B^{\mathsf T}B+\lambda\Omega)^{-1}B^{\mathsf T}y$，形式上就是廣義的<a href="model_selection.html#ridge">脊迴歸</a>。差別在 $\Omega$ 不懲罰常數與直線；脊迴歸的單位矩陣則對每個方向都懲罰。</p>
""" + info("「收縮版」到底縮了什麼？", r"""不是把整條曲線乘上一個小於 1 的常數。把 $y$ 拆到一組由平滑排到彎曲的方向後，第 $k$ 個方向乘上 $1/(1+\lambda d_k)$：<br>
  <strong>$d_1=d_2=0$：</strong>常數與直線完全保留。<br>
  <strong>$d_k$ 愈大：</strong>愈彎曲的方向，縮得愈多。<br>
  把這些因子加起來就是<strong>有效自由度</strong>。迴歸樣條靠基底的<em>個數</em>控制複雜度；平滑樣條留著基底，靠 $\lambda$ 調整每個基底方向留下<em>多少</em>。""", "warm") + "\n"


COMPARE_DETAIL = detail("w08-detail-spline-compare", "迴歸樣條與平滑樣條怎麼選？", r"""
<p>兩者都能得到三次樣條，差別在怎麼控制彈性：迴歸樣條限制模型能用多少個方向；平滑樣條允許很多方向，但限制每個方向能發揮多少。</p>
""" + table(["", "迴歸樣條", "平滑樣條", "懲罰迴歸樣條（P-spline 等）"],
            [["控制彈性靠", "節點的數量與位置", r"$\lambda$", r"有限個基底＋$\lambda$"],
             ["目標", r"$\min_\beta\|y-B\beta\|^2$", r"$\min_g\sum_i(y_i-g(x_i))^2+\lambda\int g''^2$", r"$\min_\beta\|y-B\beta\|^2+\lambda\beta^{\mathsf T}\Omega\beta$"],
             ["適合", "已知轉折點、想要低維又簡單的模型", "不想決定節點，讓 $\\lambda$ 決定平滑程度", "多變數或大型模型，如現代 GAM"],
             ["要選什麼", "節點數或 df，用 CV", r"$\lambda$，用 CV 或 GCV", r"基底數上限，$\lambda$ 由 GCV 或 REML 選"]]) + r"""
<p>這是一般傾向，不是絕對規則：迴歸樣條也能加懲罰，一維的平滑樣條也有高效率演算法。兩種方法可以調到相同的有效自由度，但限制函數的方式不同，曲線不會一樣。在 Wage 上，節點放在分位數的 5 節點立方樣條（9 個參數）和 $\mathrm{df}_\lambda=9$ 的平滑樣條，擬合值最多差約 5.6 千美元。mgcv 的 <code>s(x, bs="cr", k=20)</code> 裡，<code>k</code> 只是基底維度的上限，最後的有效自由度仍由懲罰決定。</p>
""")


def shrink_viz(slider):
    return viz(svg("w08shrinkSvg", 300),
               [info_card("怎麼看這張圖",
                          '每根長條是一個方向留下的比例 1/(1+λdₖ)，由最平滑排到最彎曲，只畫前 12 個。'
                          '前兩根是常數與直線，λ 再大也不縮。'
                          '和<a href="model_selection.html#w06-detail-ridge-pcr">第 6 章 Ridge 的收縮因子</a>是同一個想法。', "LIVE"),
                rows_card("目前的收縮",
                          [("λ", "—", "w08shrinkLam"), ("有效自由度", "—", "w08shrinkDf"),
                           ("其中前 12 個方向", "—", "w08shrinkHead"), ("其餘方向合計", "—", "w08shrinkTail")]),
                info_card("這個 λ 的尺度",
                          '這裡的 λ 是精確平滑樣條、年齡以歲計的值，'
                          '和上面 df 滑桿那張圖（pyGAM）的 λ 尺度不同；比較時請看有效自由度。')],
               "w08shrinkStatus", "推動 λ，看哪些方向先被壓下去，有效自由度又怎麼變。",
               slider("w08shrinkSl", "log₁₀ λ", 0, 40, 1, 20, "—", "w08shrinkDraw()", "260px"),
               provenance=("course-data", "Wage 的 61 個相異年齡；由加權自然樣條懲罰矩陣算出的特徵值，見 generator。"))


G_SPACE_NOTES = r"""<h3>$g$ 在哪裡找？為什麼解是三次？</h3>
<p>(7.11) 不是對所有函數求最小，$g$ 要夠光滑，懲罰項才有定義。直觀的設定是 $C^2[a,b]$（二階導數存在且連續）。嚴格一點用 Sobolev 空間 $H^2[a,b]=\{g:g,g',g''\in L^2[a,b]\}$，導數以弱導數理解，二階導數不必處處存在。兩者的最佳解相同，而且解本身是 $C^2$ 的。</p>
<p>解的形狀可以由變分推出來。令 $g_\varepsilon=g+\varepsilon h$，其中 $h$ 只在相鄰資料點之間 $(x_i,x_{i+1})$ 不為零。因為沒有動到任何 $g(x_i)$，RSS 不變，所以最佳解要讓 $\int[g'']^2$ 在這個擾動下不再下降：</p>
$$\left.\frac{d}{d\varepsilon}\int[g_\varepsilon'']^2\right|_{\varepsilon=0}=2\int g''h''=2\int g^{(4)}h=0.$$
<p>第二個等號分部積分兩次，邊界項因 $h$ 在區間兩端附近為零而消失。對所有這樣的 $h$ 都成立，所以兩點之間 $g^{(4)}=0$，也就是三次多項式。為零的是<strong>四階導數</strong>：三次多項式的三階導數是常數，不一定是 0。穿過資料點時，RSS 那一項讓三階導數可以跳，因此節點就落在資料點；端點的斜率不受資料約束，又給出 $g''(a)=g''(b)=0$，這正是自然邊界條件。</p>
""" + table(["懲罰", r"$\int[g']^2$", r"$\int[g'']^2$", r"$\int[g''']^2$", r"$\int[g^{(m)}]^2$"],
            [["節點間滿足", "$g''=0$", "$g^{(4)}=0$", "$g^{(6)}=0$", "$g^{(2m)}=0$"],
             ["節點間的次數", "1", "3", "5", "$2m-1$"]]) + r"""
<p>我們沒有事先假設 $g$ 是樣條，三次與節點位置都是最佳化導出來的。</p>
"""

ENERGY_PROOF = r"""<p><strong>為何無限維問題可限制在自然樣條？</strong>這是自然樣條的最小彎曲能量性質。設 $s$ 為通過所有 $g(x_i)$ 的自然立方插值樣條，令 $h=g-s$，故 $h(x_i)=0$，而且</p>
$$\int(g'')^2=\int(s'')^2+2\int s''h''+\int(h'')^2.$$
<p>在每一段上分部積分兩次：$\int_{x_i}^{x_{i+1}}s''h''=[s''h']_{x_i}^{x_{i+1}}-[s'''h]_{x_i}^{x_{i+1}}+\int_{x_i}^{x_{i+1}}s^{(4)}h$。三個條件讓它們全部消失：$h(x_i)=0$ 與 $s^{(4)}=0$ 消去後兩項；$s''$ 連續使內部節點的 $s''h'$ 互相抵消；自然邊界 $s''(a)=s''(b)=0$ 消去兩端。於是交叉項為零，得到類似畢氏定理的等式</p>
$$\int(g'')^2=\int(s'')^2+\int\big((g-s)''\big)^2\ge\int(s'')^2.$$
<p>$s$ 和 $g$ 在資料點的值相同，RSS 也相同，所以不管最佳解的擬合值 $z_i=g(x_i)$ 是多少，用自然樣條連接都不會變差。至少有兩個相異 $x_i$ 且 $\lambda>0$ 時，等號只在 $h\equiv0$ 成立，最佳解唯一；$\lambda=0$ 時只約束觀測位置，不能聲稱整個函數唯一。</p>"""

DF_NOTES = r"""
<h3>為什麼跡可以叫自由度？</h3>
<p>OLS 的擬合值是 $\hat y=Hy$，$H=X(X^{\mathsf T}X)^{-1}X^{\mathsf T}$ 是投影矩陣，$H^2=H$，特徵值只有 0 和 1，所以 $\operatorname{tr}H$ 恰好等於參數個數 $p$。平滑矩陣 $S_\lambda$ 不是投影，特徵值落在 $[0,1]$。例如特徵值是 $1,1,0.8,0.3,0.1$ 時，$\mathrm{df}_\lambda=3.2$：有 5 個方向，但有的只留下一部分，所以自由度可以不是整數。</p>
<p>也可以從敏感度來看。因為 $\hat g_\lambda(x_i)=\sum_j\{S_\lambda\}_{ij}y_j$，所以</p>
$$\{S_\lambda\}_{ii}=\frac{\partial\hat g_\lambda(x_i)}{\partial y_i},\qquad \mathrm{df}_\lambda=\sum_{i=1}^{n}\frac{\partial\hat g_\lambda(x_i)}{\partial y_i}.$$
<p>$\{S_\lambda\}_{ii}$ 衡量第 $i$ 個擬合值對自己觀測值的敏感度。擬合值愈依賴自己的 $y_i$，模型在那裡就愈有彈性，加總起來就是模型對資料的總敏感度。固定 $\lambda$ 時，$S_\lambda$ 只由 $x_i$ 與基底決定，和 $y$ 無關；若 $\lambda$ 是看資料選的，整個程序就不再是 $y$ 的線性函數。</p>
""" + table(["", "線性迴歸", "平滑樣條"],
            [["擬合值", r"$\hat y=Hy$", r"$\hat g=S_\lambda y$"],
             ["矩陣性質", "投影，特徵值 0 或 1", "收縮，特徵值在 $[0,1]$"],
             ["自由度", r"$\operatorname{tr}H=p$，一定是整數", r"$\operatorname{tr}S_\lambda$，通常不是整數"],
             ["複雜度怎麼控制", "變數或基底的個數", r"$\lambda$"]]) + r"""
<p>兩端的極限：$x$ 全部相異時，$\lambda\to0^+$ 有 $S_\lambda\to I$、$\mathrm{df}_\lambda\to n$，有重複位置時則趨近相異位置數 $m$；$\lambda\to\infty$ 時 $S_\lambda$ 趨近直線迴歸的 $H$，$\mathrm{df}_\lambda\to2$。常看到的「下限是 1」只是不算截距的計數慣例，所以 lab 呼叫 <code>approx_lam(..., df+1)</code>，圖上標 df = 1 的其實是直線。</p>
"""


def smooth(b, slider):
    rep(b, "smooth", "它是那個自然樣條的<strong>收縮版</strong>，收縮的程度由 λ 決定。</p>",
        "它是那個自然樣條的<strong>收縮版</strong>，收縮的程度由 λ 決定。</p>\n" + SHRINK_MAIN)
    rep(b, "smooth", '<div class="qa-box">', shrink_viz(slider) + "\n" + COMPARE_DETAIL + '\n<div class="qa-box">')
    b["smooth"] = extend(b["smooth"], "w08-detail-smoothing-df", DF_NOTES)
    rep(b, "smooth", "深入計算：平滑矩陣、交叉驗證與 IRLS", "深入計算：函數空間、平滑矩陣、交叉驗證與 IRLS")
    cut(b, "smooth", "<h3>平滑矩陣與邏輯斯平滑</h3>", "<h3>由曲率懲罰到可計算的線性系統</h3>", G_SPACE_NOTES)
    cut(b, "smooth", "<p>為何無限維問題可限制在自然樣條？", "</div></details>", ENERGY_PROOF)
    rep(b, "smooth", r"<h3>二元反應的懲罰 IRLS</h3><p>令 $\eta=B\beta$",
        r"<h3>二元反應的懲罰 IRLS</h3><p>同樣的想法可以搬到 logistic 迴歸：把 $g(x)$ 放進 logit，最大化 $\sum_i\{y_ig(x_i)-\log(1+e^{g(x_i)})\}-\frac\lambda2\int g''(t)^2dt$，最佳的 $g$ 仍是節點在資料點的自然樣條。令 $\eta=B\beta$")
    cut(b, "smooth", r"<p>固定 $\lambda$ 時，$S_\lambda$ 決定觀測如何互相影響", "<p>LOOCV 捷徑使用")
    cut(b, "smooth", "<h3>由曲率矩陣連到二元分類</h3>", "<p>講義連結的 Bone Mineral Density notebook")
    rep(b, "smooth", "Lab 的 <code>pyGAM</code> 使用具有平滑懲罰的樣條項，與精確自然平滑樣條屬於相關但不同的參數化；",
        "Lab 的 <code>pyGAM</code> 用的是 P-spline，與每個 $x$ 都放節點的精確平滑樣條屬於相關但不同的參數化；")


# ── §7.6：局部迴歸 ─────────────────────────────────────────────────────
LOCAL_DF = r"""<h3>局部迴歸的自由度怎麼估？</h3>
<p>權重只看距離、不看 $y$，所以每個目標點的擬合值都是 $y$ 的線性組合：$\hat f(x_0)=\ell(x_0)^{\mathsf T}y$，其中 $\ell(x_0)^{\mathsf T}=e_1^{\mathsf T}(B_0^{\mathsf T}W_0B_0)^{-1}B_0^{\mathsf T}W_0$，$e_1$ 取出截距。把各訓練點的 $\ell(x_i)^{\mathsf T}$ 疊成矩陣 $L$，就有 $\hat y=Ly$，自由度和平滑樣條一樣定義成 $\operatorname{tr}L$（ESL §6.2）。跨距愈大，鄰居愈多，$\operatorname{tr}L$ 愈小。在 Wage 上用局部線性、tricube、不做穩健化實算，span 0.2、0.5、0.7、1.0 分別約是 10.6、4.9、3.7、2.4；span = 1.0 仍依距離加權，所以不會剛好是 2。</p>
<p><code>statsmodels</code> 的 <code>lowess</code> 不提供自由度，也沒有回傳 $L$，要自己依上式計算。穩健化迭代（<code>it&gt;0</code>）的權重會依殘差而變，擬合就不再是 $y$ 的線性函數，$\operatorname{tr}L$ 只能當近似。</p>
<p>自由度的定義不只一種，比較時要看清楚。課本圖 7.10 的圖例標 16.4 與 5.3，文字說是局部線性，但上面的 $\operatorname{tr}L$ 只有 10.6 與 3.7。改算<strong>局部二次的 $\operatorname{tr}(LL^{\mathsf T})$</strong> 則得 16.6 與 5.3。R 的 <code>loess</code> 預設二次，回報的 <a href="https://github.com/wch/r-source/blob/trunk/src/library/stats/R/loess.R">enp</a> 就是這個量，所以圖例很可能來自這個設定。這是本頁的推測，課本沒有交代。</p>
"""


def loess(b):
    cut(b, "loess", "<p>要做的選擇有三個：權重函數 K 怎麼定", "<div class=\"viz-layout\" data-provenance=\"course-data\" data-source-note=\"Wage 全部 3000 筆；tricube",
        r"""<p>這裡沒有一組全域基底：每個 $x_0$ 各用自己的局部基底 $1,(x-x_0)$。不過擬合值仍是 $y$ 的線性組合，所以它還是線性平滑器。</p>

  <p>局部迴歸其實分兩步：先<strong>選鄰域</strong>，決定哪些點參與；再<strong>依距離給權重</strong>，決定每個點有多少影響力。權重帶來兩個好處。第一，離 $x_0$ 愈近的點愈能代表 $x_0$ 的情況，影響就該愈大。第二，如果鄰域內一律等權重（方框），點一進出鄰域擬合值就會跳；tricube 讓鄰域邊緣的權重平滑降到 0，曲線隨 $x_0$ 移動時也比較平順。下面的元件可以切換兩種權重，比較淡紅曲線的鋸齒：span = 0.3 時，方框的最大折動約 1.06，tricube 只有約 0.39。</p>

  <p>要做的選擇有三個：權重函數 K、第 3 步擬合常數／直線／二次、以及<strong>跨距</strong>（span）s。它們彼此獨立：同一種權重可以配不同次數的局部多項式。平滑的權重函數之間差異通常不大，最關鍵的是 s：
  <strong>它控制平滑程度，作用類似平滑樣條的 λ</strong>。
  s 小則鄰域窄、曲線抖；s 大則鄰域寬、接近全域擬合。s 一樣可以用交叉驗證選。</p>

""")
    rep(b, "loess", r"當 $B_0^TW_0B_0$ 可逆，", r"當 $B_0^TW_0B_0$ 可逆（局部設計滿秩），")
    cut(b, "loess", "<p>多變數時可在 $(x_1,x_2)$ 的鄰域擬合局部平面", "<p>局部常數只做加權平均", LOCAL_DF + "<h3>局部的次數與穩健化</h3>\n")
    rep(b, "loess", r"<p>講義延伸的變係數模型把「附近」改為時間附近：在每個目標時間內擬合薪資對其他變數的係數，得到 $\beta_j(t)$。",
        r"<p>講義延伸的變係數模型把「附近」改為時間附近：在每個目標時間內擬合薪資對其他變數的係數，得到 $\beta_j(t)$，例如 $E(Y\mid x,t)=\beta_0(t)+\beta_1(t)x$。")
    rep(b, "loess", "局部加權擬合與多變數延伸", "局部加權擬合、自由度與多變數延伸")
    rep(b, "loess", "$\\hat\\beta=(B_0^TW_0B_0)^{-1}B_0^TW_0y$，而 $\\hat f(x_0)=\\hat\\beta_0$。",
        "$\\hat\\beta=(B_0^TW_0B_0)^{-1}B_0^TW_0y$，而 $\\hat f(x_0)=\\hat\\beta_0$；下一個目標點要重新選鄰居、權重和局部係數。")


# ── §7.7：GAM ──────────────────────────────────────────────────────────
GAM_BASIS = r"""
  <p>接回基底展開：把每個未知函數展開成基底，$f_j(x)\approx\sum_{k=1}^{K_j}\beta_{jk}b_{jk}(x)$，代回 (7.15) 得到</p>
  $$y_i\approx\beta_0+\sum_{j=1}^{p}\sum_{k=1}^{K_j}\beta_{jk}b_{jk}(x_{ij})+\varepsilon_i.$$
  <p>於是 GAM 就是一個大一點的迴歸。什麼時候可以寫等號？若先假設 $f_j$ 就屬於指定的樣條空間，等號成立；若 $f_j$ 是一般的光滑函數，有限個基底通常只是近似。</p>
""" + info("模型定義和估計方法是兩回事", r"""GAM 的定義是<strong>加法結構</strong>，不是基底展開。基底展開只是最常見的估計方式，因為它把函數估計變成係數估計；同一個模型也可以用 backfitting 搭配局部迴歸來估。""", "warm") + "\n"


def gam(b):
    rep(b, "gam", "三者的貢獻相加得到薪資預測。</p>", "三者的貢獻相加得到薪資預測。</p>\n" + GAM_BASIS)
    rep(b, "gam", r"""+ \cdots + f_p(X_p) \tag{7.18}$$
""", r"""+ \cdots + f_p(X_p) \tag{7.18}$$

  <p>一般寫成 $g\left(E[Y\mid X]\right)=\beta_0+\sum_{j=1}^{p}f_j(X_j)$：加法結構放在連結函數 $g$ 上，而不是加性誤差。</p>
""")
    rep(b, "gam", "需要懲罰時，則在相同目標中加入各平滑項的曲率成本。",
        r"需要懲罰時，則在相同目標中加入各平滑項的曲率成本，即 $\min\|y-\beta_01-B\beta\|^2+\sum_j\lambda_j\beta_j^{\mathsf T}S_j\beta_j$，這也是 mgcv 的估計框架。")


# ── 速查 ───────────────────────────────────────────────────────────────
def reference(b):
    rep(b, "reference", "以等效 df 表示", r"$\operatorname{tr}L$（連續）")


# ── 第二輪：兩位讀者複查後的去重 ──────────────────────────────────────
def dedupe(b):
    # 自然樣條的兩種 K 只留「先數內部節點」
    cut(b, "natural", "<p>自然樣條則固定兩個邊界節點，內部 $K$ 個節點給 $K+2$ 維空間。", "<p>來源：")
    # 分類 GAM 留「稀有事件算例」，這裡只留兩句
    cut(b, "gam", "<h3>分類 GAM 為何在最低教育組不穩定？</h3>", '<p class="source-links">本主題的講義來源與延伸閱讀：<a href="https://stats.stackexchange.com/questions/279576',
        r"""<p>若年齡效果隨教育改變，單一 $f_2(age)$ 不足以表示，要明確加入交互作用或二維平滑項，並重新驗證；不能把任何殘差結構都當成該增加平滑項。</p>
""")
    # 薄板與效果圖：留「完整表示」「四種效果圖」與證明
    cut(b, "gam", "<h3>二維平滑與效果圖的讀法</h3>", "<h3>薄板樣條的完整表示</h3>")
    rep(b, "gam", "<h3>薄板樣條的完整表示</h3>", "<h3>薄板樣條的完整表示</h3><p>薄板樣條把一維曲率懲罰推廣到平面，最小化 $\\sum_i(y_i-g(x_{i1},x_{i2}))^2+\\lambda J(g)$。把這類 $g(x_j,x_k)$ 加入 GAM 可以表示交互作用，複雜度也必須另外控制。</p>")
    rep(b, "gam", r"\begin{pmatrix}K+\lambda I&P\\P^T&0\end{pmatrix}", r"\begin{pmatrix}K+\lambda I&amp;P\\P^T&amp;0\end{pmatrix}")
    cut(b, "gam", "<h3>區分四種效果圖</h3>", '<details class="qa-item proof" id="w08proof-fwl">')
    cut(b, "gam", "<h3>OLS 殘差為何加總為零？</h3>", '<p class="source-links">本主題的講義來源與延伸閱讀：<a href="https://en.wikipedia.org/wiki/Partial_regression_plot')
    rep(b, "gam", "這是擬合後樣本內的代數限制，並沒有證明誤差與解釋變數獨立。",
        "這是擬合後樣本內的代數限制，並沒有證明誤差與解釋變數獨立；沒有截距、帶懲罰或用新資料時也不能原樣套用。")
    rep(b, "gam", r"<strong>PDP</strong>每次固定目標特徵值，把其餘特徵依訓練樣本逐列帶入模型，再平均預測。",
        r"<strong>PDP</strong> 每次固定目標特徵值，把其餘特徵依訓練樣本逐列帶入模型，再平均預測：$\hat f_S(x_S)=n^{-1}\sum_i\hat f(x_S,x_C^{(i)})$。把其他特徵固定在平均值只是一個切片，對非線性模型兩者不同。")
    # 把四種效果圖移到證明之前
    b_gam = b["gam"]
    p = b_gam.index('<details class="qa-item proof" id="w08proof-fwl">')
    q = b_gam.index("<h3>四種效果圖如何回答不同問題？</h3>")
    z = b_gam.index('<p class="source-links">本主題的講義來源與延伸閱讀：<a href="https://en.wikipedia.org/wiki/Partial_regression_plot')
    b["gam"] = b_gam[:p] + b_gam[q:z] + b_gam[p:q] + b_gam[z:]
    rep(b, "smooth", r"若 $M$ 的特徵值是 $\mu_j\ge0$", r"若 $M$ 的特徵值是 $d_j\ge0$")
    b["smooth"] = b["smooth"].replace(r"\mu_j", "d_j")
    # 局部迴歸的 lab 收合移到演算法之後，span 先定義再用
    src = b["loess"]
    a = src.index('<details class="qa-item reading-detail" id="w08-detail-lowess-lab-plot">')
    depth, end = 0, None
    for m in re.finditer(r"<details\b|</details>", src[a:]):
        depth += -1 if m.group()[1] == "/" else 1
        if depth == 0:
            end = a + m.end()
            break
    block = src[a:end]
    src = src[:a] + src[end:]
    mark = '<div class="viz-layout" data-provenance="course-data" data-source-note="Wage 全部 3000 筆；tricube'
    if src.count(mark) != 1:
        raise ValueError("loess viz 比對失敗")
    b["loess"] = src.replace(mark, block + "\n" + mark)


def augment(bodies, slider):
    prologue(bodies)
    poly(bodies)
    step(bodies)
    basis(bodies)
    splines(bodies)
    natural(bodies)
    smooth(bodies, slider)
    loess(bodies)
    gam(bodies)
    reference(bodies)
    dedupe(bodies)
    return bodies
