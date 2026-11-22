"""第 9 章 soft（軟邊界與 C）與 hinge（Hinge loss）兩節整節重寫（2026-11-22）。

規格：tools/verification/ch9-svm-deepen-20261122/consult/audit.md 的 soft、hinge 兩段。
正文只用講義 09、ISLP §9.1.5、§9.2、§9.5 與課程 Lab；講義連結的內容放收合。
預算一律寫成講義的 const（ISLP 記作 C），懲罰權重寫成 C（講義第二種寫法與 scikit-learn）。
"""
from svm_common import (URL, detail, grab_details, grab_quiz, grab_viz, info,
                        links, proof, qa_wrap, quiz, table)


def _h3(hid, text):
    return f'<h3 id="{hid}">{text}</h3>'


# ───────────────────────── soft ─────────────────────────

def _soft_intro():
    return r'''
  <p>上一節結尾留下兩個問題。第一，<strong>資料常常無法用一個超平面完全分開</strong>；
  講義的說法是：除非 n &lt; p，通常都分不開。這時最大邊界問題找不到 $M&gt;0$ 的解，
  最大邊界分類器根本用不上（ISLP 圖 9.4）。第二，<strong>就算分得開，硬要全部分對也可能是壞主意</strong>：
  ISLP 圖 9.5 只多加一個藍點，最大邊界超平面就大幅轉向，margin 縮到極窄。
  分類器對單一觀測值這麼敏感，表示它可能已經過度擬合訓練資料。</p>

  <p>解法是<strong>把「分開」的定義放鬆</strong>：允許少數點跑到 margin 錯誤的一側，
  甚至跑到超平面錯誤的一側。換來兩個好處：<strong>對個別觀測值更穩健</strong>，
  以及<strong>大多數訓練觀測值分得更好</strong>。也就是說，故意分錯幾筆訓練資料，
  換取其餘資料分得更好，可能是划算的。這個分類器叫<strong>支持向量分類器</strong>
  （support vector classifier），也叫<strong>軟邊界分類器</strong>（soft margin classifier）；
  margin 之所以「軟」，是因為它可以被部分觀測值違反。</p>

  <p>支持向量分類器是下面這個最佳化問題的解（ISLP 式 9.12–9.15）：</p>

  $$\begin{aligned}
    &\underset{\beta_0,\beta_1,\dots,\beta_p,\,\epsilon_1,\dots,\epsilon_n,\,M}{\text{maximize}}
      \quad M \\
    &\text{subject to} \quad \sum_{j=1}^{p} \beta_j^2 = 1, \\
    &\qquad\qquad\quad\; y_i\left(\beta_0 + \beta_1 x_{i1} + \cdots + \beta_p x_{ip}\right)
      \ge M\left(1 - \epsilon_i\right), \\
    &\qquad\qquad\quad\; \epsilon_i \ge 0, \quad \sum_{i=1}^{n} \epsilon_i \le \text{const}
  \end{aligned}$$

  <p>跟最大邊界問題相比只多了<strong>鬆弛變數</strong>（slack variable）$\epsilon_1,\dots,\epsilon_n$，
  以及它們的總量上限 const（ISLP 把這個上限記作 $C$；本頁用講義的 const，
  把 $C$ 留給後面的懲罰權重）。擬合完成後，新觀測值 $x^*$ 一樣看 $f(x^*)$ 的正負號分類。
  $\epsilon_i$ 告訴你第 i 筆相對於 margin 與超平面站在哪裡：</p>
''' + table(["εᵢ 的值", "第 i 筆在哪裡", "訓練資料上分對了嗎"], [
        ["εᵢ = 0", "在 margin 正確的一側（或剛好在 margin 上）", "是"],
        ["0 &lt; εᵢ &lt; 1", "違反 margin，但仍在超平面正確的一側", "是"],
        ["εᵢ = 1", "恰好在超平面上", "落在分界上，類別由平手規則決定"],
        ["εᵢ &gt; 1", "跑到超平面<strong>錯誤</strong>的一側", "<strong>否</strong>"],
    ]) + r'''
  <p>最後一條 $\sum_i\epsilon_i\le\text{const}$ 把 const 變成<strong>違反 margin 的總預算</strong>。
  const = 0 時沒有預算，所有 $\epsilon_i$ 只能是 0，問題退回最大邊界超平面
  （當然，前提是兩類分得開）。const &gt; 0 時，跑到超平面錯誤一側的點每一個都要花掉超過 1 單位的預算，
  所以<strong>最多只有 const 個觀測值會被分錯</strong>。const 小，就是要一條很少被違反的窄 margin；
  const 大，margin 變寬，容許更多違反。實務上 const 是調整參數，用交叉驗證選；
  它控制偏差與變異的取捨：const 小的分類器貼著資料擬合，偏差低、變異高；
  const 大則反過來。</p>

  <p>這個問題有一個關鍵性質：<strong>只有剛好落在 margin 上、或違反 margin 的觀測值會影響超平面</strong>。
  這些點叫做<strong>支持向量</strong>（support vector）。嚴格位在 margin 正確一側的點，
  只要它還留在那一側，怎麼移動都不會改變分類器。
  這是講義與 ISLP 的幾何定義；後面的對偶推導另用「乘子 $\hat\alpha_i>0$」定義支持向量，
  兩者只在資料退化時不同：剛好在 margin 上的點，乘子可能是 0。</p>
'''


def _soft_three_forms():
    return _h3("w10-soft-three-forms", "同一個問題的三種寫法：β 會變，邊界不會") + r'''
  <p>講義把上面的問題連續改寫兩次，三個式子的限制都還保留 $\epsilon_i\ge0$ 與
  $\sum_i\epsilon_i\le\text{const}$：</p>

  $$\begin{aligned}
  \text{(1)}\quad &\max_{\beta_0,\beta,\,\|\beta\|=1,\,\epsilon}\ M
    &&\text{使得}\ \ y_i(x_i^{T}\beta+\beta_0)\ge M(1-\epsilon_i)\\
  \text{(2)}\quad &\max_{\beta_0,\beta,\,\epsilon}\ M
    &&\text{使得}\ \ \frac{1}{\|\beta\|}\,y_i(x_i^{T}\beta+\beta_0)\ge M(1-\epsilon_i)\\
  \text{(3)}\quad &\min_{\beta_0,\beta,\,\epsilon}\ \|\beta\|
    &&\text{使得}\ \ y_i(x_i^{T}\beta+\beta_0)\ge 1-\epsilon_i
  \end{aligned}$$

  <p>直覺分三步：</p>
  <ol>
    <li><strong>(1) → (2)：</strong>同一個超平面有無限多組係數，整組乘上 $a&gt;0$，
    超平面一動也不動。$\|\beta\|=1$ 只是從中挑出一組代表，讓 $y_if(x_i)$ 剛好等於距離。
    (2) 改成先除以 $\|\beta\|$，左邊不管 β 多長都是點到超平面的距離，
    所以 $\|\beta\|=1$ 這條限制可以拿掉。</li>
    <li><strong>(2) → (3)：</strong>既然 β 的長度可以自由挑，就挑讓 $M\|\beta\|=1$ 的那一組，
    也就是令 $M=1/\|\beta\|$。限制兩邊同乘 $\|\beta\|$，右邊的 $M$ 就消失了，
    「最大化 $M$」變成「最大化 $1/\|\beta\|$」，也就是<strong>最小化 $\|\beta\|$</strong>。</li>
    <li><strong>為什麼「β 短」等於「margin 寬」：</strong>在 (3) 的尺度下，
    margin 的兩條邊界是 $f(x)=\pm1$。函數值 $f$ 沿著法向量每走 1 單位距離只增加 $\|\beta\|$，
    所以從超平面走到 $f=1$ 要走 $1/\|\beta\|$ 那麼遠。β 愈短，帶子愈寬。</li>
  </ol>

  <p>所以三個式子解出來的<strong>超平面相同</strong>，係數卻不同：(3) 的係數是 (1) 的係數除以 $M$。
  $\epsilon_i$ 則三式都一樣，因為它衡量的是「違反了幾個 margin 寬度」這種相對量，
  係數整組縮放時兩邊一起縮放，$\epsilon_i$ 不受影響。</p>

  <p>最小化 $\|\beta\|$ 為什麼不會一路縮到 0、預算太大時又會發生什麼事，下面的推導收合有說明。</p>
'''


def _soft_penalty():
    return r'''
  <p>講義接著寫出更常見的<strong>懲罰形式</strong>：把違反量放進目標函數，
  用權重 $C$ 決定違反一單位要付多少代價。式 (3) 的 $\|\beta\|$ 換成等價、比較好算的
  $\tfrac12\|\beta\|^2$：</p>

  $$\min_{\beta_0,\beta,\epsilon}\ \frac12\|\beta\|^2 + C\sum_{i=1}^{n}\epsilon_i
    \qquad \text{使得}\ \ \epsilon_i\ge0,\ \ y_i(x_i^{T}\beta+\beta_0)\ge1-\epsilon_i$$

  <p>這個 primal 問題有 $p+1+n$ 個變數、$2n$ 條限制。它的 dual 和最大邊界的 dual 幾乎一樣，
  唯一的差別是每個乘子多了上界 $C$：</p>

  $$\max_{\alpha}\ \sum_{i=1}^{n}\alpha_i-\frac12\sum_{i=1}^{n}\sum_{i'=1}^{n}
    \alpha_i\alpha_{i'}y_iy_{i'}x_i^{T}x_{i'}
    \qquad \text{使得}\ \ 0\le\alpha_i\le C,\ \ \sum_{i=1}^{n}\alpha_iy_i=0$$

  <p>共 $n$ 個變數、$2n+1$ 條限制，解出來的係數是 $\hat\beta=\sum_i\hat\alpha_iy_ix_i$，
  只有 $\hat\alpha_i&gt;0$ 的點（支持向量）有貢獻。</p>

  <p>講義特別註明 <strong>C 與 const 成反比</strong>。意思是兩者方向相反：
  const 大表示預算多、容許更多違反；$C$ 大表示每單位違反罰得重、容許更少違反。
  不過這個對應要由實際的最佳解決定，並沒有一條對所有資料都成立的 $C=1/\text{const}$ 公式。
  scikit-learn 的 <code>SVC(C=…)</code> 用的就是這個懲罰形式。</p>
'''


def _soft_c_box():
    return info("先辨認 C 是預算還是懲罰", r'''
  ISLP 的 $C$（本頁寫成 const）是違反量總和的上限；
  講義後半與 scikit-learn 的 <code>SVC(C=…)</code> 是目標函數裡違反量的懲罰權重。
  兩者調整方向相反，但<strong>沒有普遍的倒數公式</strong>。
  下面的元件與 Lab 都用 scikit-learn 的 C。''', "warm")


def _soft_after_widget():
    return r'''
  <p>這張圖顯示固定資料下，C 改變時邊界、支持向量數與誤差的變化。
  它不是跨訓練樣本的偏差／變異分解，不能從支持向量數直接推出偏差或變異。
  C 控制懲罰強度，實際泛化表現仍需交叉驗證評估。</p>
''' + _h3("w10-soft-read-sv", "在圖上認出支持向量") + r'''
  <p>判斷的依據是點和<strong>虛線（margin）</strong>的相對位置，跟它離實線（超平面）近不近無關。
  ISLP 圖 9.6 左圖是一個小例子：紫色的第 3、4、5、6 筆在 margin 正確的一側，第 2 筆剛好在 margin 上，
  第 1 筆在 margin 錯誤的一側；藍色的第 7、10 筆在 margin 正確的一側，第 9 筆在 margin 上，
  第 8 筆在 margin 錯誤的一側。所以支持向量是第 1、2、8、9 筆。
  右圖多加的第 11、12 筆跑到超平面錯誤的一側，當然也違反了 margin，兩者也都是支持向量。</p>

  <p>兩個容易看錯的地方。第一，剛好落在虛線上的點離超平面有一整個 margin 那麼遠，依幾何定義仍是支持向量
  （少數退化情形下它的乘子可能是 0）；第二，分錯、而且離超平面很遠的點也是支持向量，因為它嚴重違反了 margin。
  只有嚴格待在 margin 正確一側的點不是支持向量，把它拖到再遠的地方，分類器也完全不變。</p>

  <p>核 SVM 的圖若畫出了 margin，虛線就是 $f(x)=\pm1$ 的等高線，
  可以彎曲，甚至在個別點旁圍成小圈。判斷規則不變：落在虛線上或虛線錯誤一側（$y_if(x_i)\le1$）的點是支持向量。</p>

  <p>支持向量的多寡跟預算一起變。ISLP 圖 9.7 用四個預算值擬合同一份資料：
  預算最大的左上圖 margin 很寬，很多點違反 margin，支持向量很多，這樣的分類器變異低、但偏差可能高；
  預算最小的右下圖只剩八個支持向量。Lab 用 scikit-learn 的 C 示範同一件事：
  在分得開的資料上，<code>C=1e5</code> 只用了三個支持向量，而且三點都在 margin 上；
  <code>C=0.1</code> 一樣沒有訓練誤差，但 margin 更寬、用了十二個支持向量，
  由較多的點共同決定方向，所以比較穩定。</p>
''' + quiz("qSv", "QUIZ · 認出支持向量",
           "支持向量分類器擬合完成後，依講義與 ISLP 的幾何定義，下面哪一組點全部都是支持向量？", [
               (False, "離超平面（實線）最近、但仍在 margin 正確一側之外的那幾個點",
                "嚴格在 margin 正確一側的點不影響解，不管它離實線多近都不是支持向量。判斷要看虛線，不看實線。"),
               (True, "剛好落在 margin（虛線）上的點，以及跑進 margin 帶內或分錯的點",
                "對。這是講義與 ISLP 的幾何定義：落在 margin 上、或在 margin 錯誤一側的觀測值；分錯的點一定也違反 margin。若改用對偶定義（乘子大於 0），帶內與分錯的點一定是支持向量，剛好在 margin 上的點在退化時可能乘子為 0。"),
               (False, "只有被分錯、跑到超平面錯誤一側的點",
                "漏掉了兩種點：剛好在 margin 上的點，以及進入 margin 帶但仍分對的點。依幾何定義它們也是支持向量；其中剛好在 margin 上的點，在退化時乘子可能是 0。"),
           ])


def _soft_three_forms_detail():
    body = r'''
<p>下面把正文的三步寫完整，並說明為什麼係數會變、$\epsilon_i$ 卻不變。
記 $f(x)=x^T\beta+\beta_0$，$m_i=y_if(x_i)$。</p>

<h4>函數間隔與幾何間隔</h4>
<p>$m_i=y_if(x_i)$ 叫<strong>函數間隔</strong>（functional margin），
$m_i/\|\beta\|$ 叫<strong>幾何間隔</strong>（geometric margin），後者才是點到超平面的帶號距離。
把 $(\beta_0,\beta)$ 換成 $(a\beta_0,a\beta)$、$a&gt;0$：</p>
$$\frac{y_i\big(x_i^T(a\beta)+a\beta_0\big)}{\|a\beta\|}
=\frac{a\,y_if(x_i)}{a\,\|\beta\|}=\frac{y_if(x_i)}{\|\beta\|}.$$
<p>函數間隔跟著乘 $a$，幾何間隔與正負號都不變，所以超平面與分類結果都不變。
Stanford CS229 的說法是：因為幾何間隔有這種尺度不變性，可以對係數加上任何一種尺度限制，
不會改變任何重要的東西。$\|\beta\|=1$ 與「把兩條參考邊界固定在 $f(x)=\pm1$」都只是這種限制。硬邊界時，後者就是「最近點的函數間隔等於 1」；軟邊界時最近的點可以在帶內甚至分錯，$f=\pm1$ 只是兩條參考邊界。</p>
''' + proof("w10-proof-three-forms", "三個式子的最佳超平面相同", r'''
<p><strong>(1) ⇔ (2)。</strong>(1) 的任一可行解 $(\beta_0,\beta,\epsilon,M)$ 有 $\|\beta\|=1$，
直接滿足 (2) 的限制。反過來，(2) 的任一可行解除以 $\|\beta\|$ 得到
$(\beta_0/\|\beta\|,\beta/\|\beta\|)$，由上面的不變性，同一組 $\epsilon,M$ 仍滿足 (1) 的限制。
兩者可行集合在「超平面＋$\epsilon$＋$M$」的層次上相同，目標都是 $M$，最佳值相同。</p>
<p><strong>(2) ⇔ (3)。</strong>設最佳的 $M$ 有限且 $M&gt;0$（因此 $\beta\ne0$）。(2) 的限制兩邊同除以 $M$：
$$y_i\Big(x_i^T\tfrac{\beta}{M\|\beta\|}+\tfrac{\beta_0}{M\|\beta\|}\Big)\ge1-\epsilon_i .$$
令 $\tilde\beta=\beta/(M\|\beta\|)$、$\tilde\beta_0=\beta_0/(M\|\beta\|)$，就得到 (3) 的限制，
而且 $\|\tilde\beta\|=1/M$。所以 (2) 的每個可行點對應 (3) 的可行點，目標值滿足 $\|\tilde\beta\|=1/M$；
反過來，(3) 的可行點 $(\tilde\beta_0,\tilde\beta,\epsilon)$ 令 $M=1/\|\tilde\beta\|$ 就回到 (2)。
最大化 $M$ 等於最小化 $1/M=\|\tilde\beta\|$，兩題的最佳解是同一個超平面。</p>
<p><strong>為什麼最小化 $\|\beta\|$ 不會縮到 0。</strong>$\beta=0$ 時 $f(x)=\beta_0$ 是常數，所有點被分到同一類。在 (3) 的限制下，正類需要 $\epsilon_i\ge1-\beta_0$、負類需要 $\epsilon_i\ge1+\beta_0$，總量至少是 $n_+(1-\beta_0)_++n_-(1+\beta_0)_+$，在 $\beta_0=\pm1$ 取到最小值 $2\min(n_+,n_-)$。所以 const 小於這個量時，$\beta=0$ 根本不可行，最佳解一定有非零的 $\beta$。</p>
<p><strong>退化的情形。</strong>若 const $\ge 2\min(n_+,n_-)$（$n_\pm$ 是兩類的筆數），在 (3) 取 $\beta=0$、$\beta_0=\pm1$（取多數類的符號），少數類每筆 $\epsilon_i=2$、其餘為 0，總量剛好是 $2\min(n_+,n_-)$，目標值為 0，所以 (3) 的最佳解是 $\beta=0$，沒有超平面。同時，(1) 可以把超平面推到所有資料的同一側（$\beta_0$ 取得很大、多數類在正確一側）：$M$ 愈大，多數類的 $\epsilon_i$ 是 0，少數類的 $\epsilon_i$ 從上方趨近 2，總量趨近 $2\min(n_+,n_-)$。所以 const <strong>嚴格大於</strong>這個門檻時，$M$ 可以任意大，沒有最大值；剛好等於門檻時要看資料，(1) 甚至可能沒有 $M&gt;0$ 的可行解。上面的等價只在門檻以下成立。</p>
<p><strong>$\epsilon_i$ 不變。</strong>上面的換算只縮放 $(\beta_0,\beta)$，沒有動 $\epsilon_i$。
從 (1) 看，$\epsilon_i=\max\big(0,1-y_if(x_i)/M\big)$ 是「違反了多少個 margin 寬度」；
分子分母都以同一個比例縮放，比值不變。三個式子的 const 限制也因此完全相同。</p>
<p><strong>為什麼換成 $\tfrac12\|\beta\|^2$。</strong>$\|\beta\|\ge0$，平方是嚴格遞增的轉換，
最小化 $\|\beta\|$ 與最小化 $\tfrac12\|\beta\|^2$ 的解相同；後者可微、是凸二次函數，
可用二次規劃求解。$\tfrac12$ 只是讓微分時係數乾淨。</p>
''') + r'''
<h4>三個式子的係數差多少</h4>
<p>(3) 的係數是 (1) 的係數除以 $M$：$\beta^{(3)}=\beta^{(1)}/M$，$\|\beta^{(3)}\|=1/M$。
例如 (1) 解出 $M=0.5$，(3) 的係數就是 (1) 的兩倍長，兩者畫出同一條超平面；
(3) 的 margin 邊界是 $f^{(3)}(x)=\pm1$，(1) 的 margin 邊界是 $f^{(1)}(x)=\pm0.5$。</p>
<p>CMU 的 SVM 講義用同樣的步驟處理可分的情形：去掉 $\|\beta\|=1$，
令 $\|\beta\|$ 等於 margin 的倒數，得到凸最佳化問題。</p>
''' + links([(URL["cs229"], "Stanford CS229：functional／geometric margin 與最佳間隔分類器"),
             (URL["cmu"], "CMU：SVM as a Convex Optimization Problem")])
    return detail("w10-detail-three-forms", "推導：三個等價式、尺度不變性與 slack", body)


def _soft_dual_detail(old_soft):
    old = grab_details(old_soft, "w10-detail-soft-dual")
    # 舊收合內的可重用片段
    mult_table = old[old.index('<div style="overflow-x:auto;"><table class="cmp-table" style="width:100%;font-size:.85rem;">\n  <thead><tr><th>乘子</th>'):]
    mult_table = mult_table[:mult_table.index("</table></div>") + len("</table></div>")]
    proof_soft = grab_details(old, "w10-proof-soft-dual")
    q_dual = grab_quiz(old, "qDualBounds")
    k = old.index("<h4>回復截距與核對答案</h4>")
    intercept = old[k:old.index('<div class="quiz-box">', k)]
    k = old.index("<h3>預算、懲罰與錯分數不是同一個量</h3>")
    budget = old[k:old.index("<p>閱讀：", k)]
    budget = budget[:budget.index("<p>講義的 <code>const</code>")] + budget[budget.index("<p>若 $\\epsilon_i>1$"):]

    body = _h3("w10-soft-dual", "對偶：為什麼乘子多了一個上界？") + r'''
<p>以下 $C&gt;0$ 一律是<strong>懲罰權重</strong>；需要談預算時，把講義的 const 簡記為 $B$。
推導時把係數記成 $w,b$、slack 記成 $\xi_i$，對應正文懲罰形式的 $\beta,\beta_0,\epsilon_i$；
把 dual 裡的內積 $x_i^Tx_j$ 換成 $K_{ij}$，就是下一節的核版本。
對 $C&gt;0$ 的最佳解，$\xi_i=\max(0,1-y_if(x_i))$。
KKT 條件把點分成三類，表中邊界等號都要保留：</p>
''' + mult_table + proof_soft + intercept + q_dual + r'''
<h3 id="w10-soft-c-multiplier">C 也是一種 Lagrange 乘子嗎？</h3>
<p>在懲罰形式裡，<strong>被解出來的 Lagrange 乘子是 $\alpha_i$ 與 $\mu_i$</strong>（都限制為非負），
$C$ 是使用者事先給定的權重。對 $\xi_i$ 微分得到 $C-\alpha_i-\mu_i=0$，
$C$ 因此在 dual 裡變成每個 $\alpha_i$ 的上界。林軒田的講義直接說 $C$ 恰好就是 $\alpha_n$ 的上界：
把 $C$ 加 2，dual 的上界就加 2。Stanford CS229 也明寫：乘子是 $\alpha_i$ 與 $r_i$，限制為非負。</p>
<p>它和乘子的關係出現在<strong>預算形式</strong>。把正文式 (3) 的 $\|\beta\|$ 換成 $\tfrac12\|\beta\|^2$，
預算限制 $\sum_i\xi_i\le B$ 配上乘子 $\nu\ge0$：</p>
$$L=\frac12\|w\|^2+\nu\Big(\sum_i\xi_i-B\Big)+\cdots
=\frac12\|w\|^2+\nu\sum_i\xi_i-\nu B+\cdots .$$
<p>$-\nu B$ 是常數，固定 $\nu$ 時對 $(w,b,\xi)$ 最小化，與 $C=\nu$ 的懲罰形式是同一個問題。
限制全是線性的凸問題只要可行就有強對偶，所以在最佳乘子 $\nu^*$ 下，預算形式的解也是
$C=\nu^*$ 時懲罰形式的解。換句話說，<strong>懲罰形式的 $C$ 相當於預算形式在最佳解上那條預算限制的乘子值</strong>
（預算沒有用滿時這個乘子是 0，對應 $C=0$，已經落在懲罰形式 $C&gt;0$ 的範圍外）。差別在角色：預算形式先給 $B$、解出乘子；懲罰形式先給 $C$、解出用了多少預算。</p>
<p>這也說明「C 與 const 反比」的確切意思。令 $p(B)$ 為預算 $B$ 時的最小目標值，
它是 $B$ 的凸、非遞增函數（預算愈多，可行集合愈大），最佳乘子是它的斜率大小 $\nu(B)=-p'(B)$（不可微處取次梯度）。
凸函數的斜率遞增，所以 $\nu(B)$ 隨 $B$ <strong>不增</strong>：預算愈大，對應的 $C$ 愈小或不變。
方向確定，但沒有 $C=1/B$ 這種公式；$p(B)$ 的形狀由資料決定，也可能有一段平坦。</p>

<h3 id="w10-soft-feasible">預算夠大，一定有可行解，但不一定有合適的解</h3>
<p>把預算形式的限制寫成 $y_if(x_i)\ge M(1-\epsilon_i)$。任取一個超平面（$\|\beta\|=1$）與任一個 $M&gt;0$，
令 $\epsilon_i=\max\big(0,\,1-y_if(x_i)/M\big)$，每條限制都成立；這組 $\epsilon$ 的總和是有限的數，
只要 const 不小於它，就是可行解。所以<strong>const 夠大時，軟邊界問題一定可行</strong>。
懲罰形式的 $\xi_i$ 沒有總量上限，更是永遠可行；林軒田的講義稱軟邊界的 primal 與 dual 永遠可解。</p>
<p>可行不代表有好的解。預算再大下去，最佳解甚至會退化：const 達到 $2\min(n_+,n_-)$ 時，式 (3) 的最佳解是 $\beta=0$；超過它時，式 (1) 的 $M$ 沒有上限（見三個等價式的收合）。
懲罰形式在 $C&gt;0$ 時一定有最佳解，但 $C$ 很小時同樣可能得到幾乎是常數的分類器。
若真正的邊界是彎的（例如一類在中間、另一類分在兩端），任何直線都得付出大量違反量；
這就是講義說的「線性邊界找不到合適的解」。下一節的核方法處理的就是這種情形。</p>
''' + budget + r'''
''' + links([(URL["h204"], "林軒田：Soft-Margin SVM"),
             (URL["cs229"], "Stanford CS229：Regularization and the non-separable case"),
             (URL["cmu"], "CMU：SVM as a Convex Optimization Problem")])
    return detail("w10-detail-soft-dual", "推導：軟邊界的對偶、KKT 與截距", body)


def _soft_qa(old_soft):
    qa1 = r'''  <details class="qa-item"><summary>Q：C 到底是「容忍度」還是「懲罰」？我每次都搞反。</summary>
    <div class="qa-a"><p>兩個都對，因為那是<strong>兩個不同的 C</strong>。記一個口訣：<strong>預算在限制式裡，懲罰在目標函數裡。</strong></p><p><strong>預算（ISLP 的 $C$，講義的 const）：</strong>$\sum_i \epsilon_i \le \text{const}$。它站在不等式右邊，是「最多可以違反多少」的<strong>預算</strong>。預算多，違反多，margin 寬。預算為 0 就是一點都不准違反，退回最大邊界分類器。</p><p><strong>懲罰（講義的懲罰形式與 scikit-learn 的 <code>C</code>）：</strong>$\min \frac12\lVert\beta\rVert^2 + C\sum_i \epsilon_i$。$C$ 站在目標函數裡乘著違反總量，是<strong>每單位違反的罰款</strong>。罰得重，違反少，margin 窄。Lab 在分得開的資料上用 <code>C=1e5</code>，結果只剩三個支持向量、全都落在 margin 上，幾乎就是最大邊界的解。</p><p>講義說兩者成反比，意思是方向相反；精確的對應要由最佳解決定。實務上你摸到的幾乎都是 scikit-learn 那個，記住<strong>「C 大 ＝ 擬合得緊 ＝ 容易過度擬合」</strong>就好。它跟 ridge 的 λ 方向相反（λ 大 ＝ 擬合得鬆），下一節 hinge 的式子裡會看到 λ 與預算同向。</p></div>
  </details>'''
    qa2 = r'''  <details class="qa-item"><summary>Q：SVM 需要標準化嗎？</summary>
    <div class="qa-a"><p>需要。講義說得很直接：SVM 的演算法不具尺度不變性，所以強烈建議先把資料縮放。</p><p>理由在這一章的起點：SVM 從頭到尾都在算<strong>距離</strong>與<strong>內積</strong>。一個以「元」為單位的收入變數（範圍幾十萬）和一個以「年」為單位的年齡變數（範圍幾十），放進 $\lVert\beta\rVert$ 與 margin 之後，收入那一維會主導邊界的方向，年齡幾乎被忽略。RBF 核也一樣，$\exp(-\gamma \sum_j (x_{ij}-x_{i'j})^2)$ 裡的平方距離會被尺度大的那一維決定。</p><p>交叉驗證時怎麼把縮放放進流程，見下面「跟著 Lab 選 C」的收合。</p></div>
  </details>'''
    return qa_wrap("觀念釐清", [qa1, qa2])


def _tuning_detail(old_soft):
    old = grab_details(old_soft, "w10-detail-tuning-practice")
    k = old.index("<p>線性模型若需標準化")
    z = old.index("</p>", k) + 4
    new = (r'''<p>需要標準化時，做法跟第 5 章一樣：把 <code>StandardScaler</code> 和 <code>SVC</code> 包進同一個 <code>Pipeline</code>，再把整個 <code>Pipeline</code> 交給 <code>GridSearchCV</code>。這樣每一折都只用自己的訓練部分估計平均與標準差，驗證折的資訊不會洩漏到縮放步驟；完整訓練後的測試資料沿用同一組轉換，不再自行估計尺度。原模擬範例的兩個座標使用同一尺度；處理真實資料時仍要先檢查尺度。</p>''')
    return old[:k] + new + old[z:]


def soft(old):
    s = old["soft"]
    return "".join([
        _soft_intro(),
        _soft_three_forms(),
        quiz("qScale", "QUIZ · 三種寫法",
             "講義的式 (1) 解出 $\\beta^{(1)}$、$\\beta_0^{(1)}$ 與 $M=0.5$。改用式 (3) 求解時，會得到什麼？", [
                 (True, "係數變成原來的兩倍（除以 $M$），超平面與每個 $\\epsilon_i$ 都不變",
                  "對。三個式子挑的是同一個超平面的不同代表；(3) 的係數是 (1) 的係數除以 $M$，而 $\\epsilon_i$ 是相對於 margin 寬度的違反量，不受縮放影響。"),
                 (False, "係數完全相同，因為三個式子等價",
                  "等價指的是最佳超平面相同。式 (1) 要求 $\\|\\beta\\|=1$，式 (3) 的解滿足 $\\|\\beta\\|=1/M=2$，係數必然不同。"),
                 (False, "超平面會平移，因為 $M$ 被設成 $1/\\|\\beta\\|$",
                  "整組係數（含截距）一起縮放，超平面的位置與方向都不變；令 $M=1/\\|\\beta\\|$ 只是挑選尺度。"),
             ]),
        _soft_three_forms_detail(),
        _soft_penalty(),
        _soft_dual_detail(s),
        _soft_c_box(),
        "\n" + grab_viz(s, "w10softSvg") + "\n",
        _soft_after_widget(),
        "\n" + grab_details(s, "w10-detail-soft-lab") + "\n",
        _soft_qa(s),
        "\n" + grab_quiz(s, "qSoft") + "\n",
        _tuning_detail(s),
    ])


# ───────────────────────── hinge ─────────────────────────

def _hinge_main():
    return r'''
  <p>前面的支持向量分類器是一個帶限制式的最佳化問題。ISLP 與講義指出，它可以改寫成一個
  <strong>完全等價</strong>、看起來卻完全不同的形式（ISLP 式 9.25，即 ESL 習題 12.1）：</p>

  $$\underset{\beta_0,\beta_1,\dots,\beta_p}{\text{minimize}}
    \left\{ \sum_{i=1}^{n} \max\left[0,\; 1 - y_i f(x_i)\right]
    \; + \; \lambda \sum_{j=1}^{p} \beta_j^2 \right\}$$

  <p>這就是全書一直出現的<strong>「損失＋懲罰」</strong>格式（ISLP 式 9.26）。
  後面那一項是第 6 章的 ridge 懲罰，在這裡同樣負責控制偏差與變異的取捨。前面那一項叫
  <strong>hinge loss</strong>（鉸鏈損失，因為圖形像門的鉸鏈）：</p>

  $$L\left(X, y, \beta\right) = \sum_{i=1}^{n}
    \max\left[0,\; 1 - y_i\left(\beta_0 + \beta_1 x_{i1} + \cdots + \beta_p x_{ip}\right)\right]$$

  <p>λ 的方向和預算 const 相同。λ 大時 $\beta_1,\dots,\beta_p$ 被壓得小，容許更多 margin 違反，
  得到變異低、偏差高的分類器；λ 小時違反很少，變異高、偏差低。講義的說法是 λ 與 const 成正比，
  ISLP 則說 λ 小對應預算小。注意這個寫法下 <strong>margin 固定對應到數值 1</strong>（$y_if(x_i)=1$），
  margin 的實際寬度由 $\sqrt{\sum_j\beta_j^2}$ 決定，所以調 λ 就是在調 margin 的寬度。</p>
''' + info("λ、預算與 scikit-learn 的 C", r'''
  λ 大 → β 小 → margin 寬 → 容忍更多違反。
  所以 <strong>λ 大對應預算 const 大</strong>，也就是 scikit-learn 的 C 小。
  ISLP 也提醒：支持向量分類器剛問世時，常有人以為這個調整參數不重要，設成預設值 1 就好；
  「損失＋懲罰」的寫法說明它決定了模型會欠擬合還是過度擬合，必須認真選。
  講義後面說 scikit-learn 的 C 預設為 1「是合理的起點」，兩句並不衝突：預設值可以當起點，但仍要用交叉驗證調。''') + r'''
'''


LOOK = "\n  <p>現在看那條曲線。橫軸是 $y_i f(x_i)$：分對了是正的，愈大愈篤定；分錯了是負的。</p>\n"


def _hinge_after_widget():
    return r'''
  <p>關鍵在<strong>平坦區與折角的差別</strong>。hinge loss 對 $y_i f(x_i) \ge 1$ 的觀測值恰好是 0，
  這些點都在 margin 正確的一側。當 $y_i f(x_i) &gt; 1$，損失在附近恆為 0，
  刪去該點不影響目前的最佳解；$y_i f(x_i) = 1$ 正好在折角上，
  損失雖然是 0，仍可能支撐解。依 $y_if(x_i)$ 可以分成三區：</p>
''' + table(["yᵢf(xᵢ)", "位置", "對解的作用"], [
        ["&gt; 1", "在 margin 正確的一側之外", "在損失平坦區，不是支持向量"],
        ["= 1", "剛好在 margin 上", "損失為 0，但位於折角，可能是支持向量"],
        ["&lt; 1", "違反 margin", "損失大於 0，是支持向量"],
    ]) + r'''
  <p>這就是「只有支持向量影響分類器」的原因。對照之下，邏輯斯迴歸的損失沒有任何地方恰好是 0，
  只是對離決策邊界很遠的點非常小；每一筆資料都在微弱地拉扯答案，所以它沒有支持向量的概念。
  兩個損失的形狀很接近，邏輯斯迴歸與支持向量分類器因此常給出非常相似的結果（下一節）。</p>

  <p>按「顯示 0–1 損失」會加上分類錯誤的判定標準：分錯是 1、分對是 0 的階梯函數。
  hinge 與邏輯斯損失可以看成這個階梯的替代品，細節在上面的推導收合。</p>
'''


def _loss_detail(old_hinge):
    old = grab_details(old_hinge, "w10-detail-loss-normalization")
    k = old.index('<h3 id="w10-penalty-normalization">')
    core = old[k:old.index("<!-- lecture-alignment-ch9:w10-detail-loss-normalization")]
    k2 = old.index("<h3>為什麼 hinge 的轉折在 1？</h3>")
    why1 = old[k2:old.index("<p>閱讀：", k2)]
    a = why1.index("<p>兩種標籤編碼也要先統一")
    why1 = why1[:a] + why1[why1.index("</p>", a) + 4:]
    body = core + why1 + r'''
<p>Math Stack Exchange 上的一則回答用縮放說明這件事：只看 hinge 的總和時，把轉折點 1 換成 80，
最佳解就變成原來的 $(80w,80b)$，決策邊界的位置不變。加上懲罰項後，同樣的換算等於把 λ 乘上 80，
也就是換一個調整參數；所以固定在 1 不失一般性（後半句是依目標函數推得的，該回答沒有討論懲罰項）。</p>

<h4>係數慣例：λ = 1/C 還是 1/(2C)？</h4>
<p>ESL 習題 12.1 的解答把懲罰寫成 $\tfrac{\lambda}{2}\|\beta\|^2$，於是 $\lambda=1/C$；
本頁把懲罰寫成 $\lambda\|\beta\|^2$，於是 $\lambda=1/(2C)$。差別只在懲罰項前面的常數，
兩種慣例都說 λ 與懲罰權重 $C$ 成反比。該解答先指出兩個目標函數只差正的常數倍 $1/C$，再論證兩題的解相同；
更直接的看法就是上面的證明：$C&gt;0$ 時 slack 在最佳解上必然取到下界 $[1-y_if(x_i)]_+$。</p>

<h4>0–1 損失與代理損失</h4>
<p>0–1 損失不連續也不凸，直接最佳化很困難，所以常改用容易最佳化的<strong>凸代理損失</strong>
（convex surrogate loss）。林軒田的講義把 hinge 稱為 0–1 錯誤的凸上界：
$\max(0,1-ys)\ge[\![ys\le0]\!]$；$ys\ge1$ 時兩邊都是 0。
邏輯斯損失若改用以 2 為底的對數 $\log_2(1+e^{-ys})$，在 $ys=0$ 時等於 1，也成為 0–1 錯誤的上界；
本頁圖中未縮放的 $\log(1+e^{-ys})$ 在 $ys\le0$ 的部分則不一定在階梯之上。</p>
''' + links([(URL["esl121"], "ESL 習題 12.1 解答"),
             (URL["hinge1"], "Math Stack Exchange：hinge loss 為什麼是 1"),
             (URL["logloss"], "Cross Validated：兩種 logistic loss 寫法"),
             ("https://www.csie.ntu.edu.tw/~htlin/mooc/doc/205_handout.pdf", "林軒田：Kernel Logistic Regression"),
             (URL["sgd"], "scikit-learn：SGD 的損失與正則化")])
    return detail("w10-detail-loss-normalization", "推導：slack 消去、λ 與 C 的換算、兩種 logistic 寫法", body)


def _l2_logistic_detail():
    body = r'''
<p>把三個目標函數並排看就清楚了（$f(x)=\beta_0+x^T\beta$，標籤 $y_i\in\{-1,+1\}$）：</p>
$$\begin{aligned}
\text{支持向量分類器：}\quad &\sum_{i}\max\big[0,\,1-y_if(x_i)\big]+\lambda\sum_j\beta_j^2\\
\text{L2 邏輯斯迴歸：}\quad &\sum_{i}\log\big(1+e^{-y_if(x_i)}\big)+\lambda\sum_j\beta_j^2\\
\text{原本的邏輯斯迴歸：}\quad &\sum_{i}\log\big(1+e^{-y_if(x_i)}\big)
\end{aligned}$$
<p>支持向量分類器和 <strong>L2 邏輯斯迴歸</strong>只差損失那一項，懲罰項一模一樣；
原本的邏輯斯迴歸（最大概似）連懲罰都沒有。所以結構上它比較像加了 ridge 懲罰的邏輯斯迴歸。
講義拿來比較的也是這一個：類別重疊時，加 ridge 懲罰的邏輯斯迴歸與支持向量分類器非常相似。
林軒田的講義用同樣的對照得出「SVM 近似於 L2 正則化的邏輯斯迴歸」，
他用的是以 2 為底的交叉熵 $\log_2(1+e^{-ys})$，只差一個常數倍。</p>

<h4>沒有懲罰時，可分資料會出什麼事</h4>
<p>講義說類別（幾乎）分得開時，支持向量分類器比邏輯斯迴歸好。原因之一在原本的邏輯斯迴歸：
若某個 $(\beta_0,\beta)$ 讓每一筆都有 $y_if(x_i)&gt;0$，把它整組乘上 $a&gt;1$，
每一項 $\log(1+e^{-a\,y_if(x_i)})$ 都嚴格變小，而且 $a\to\infty$ 時總和趨近 0。
目標函數的下確界 0 永遠達不到，<strong>最大概似估計不存在</strong>，演算法只會讓係數一直變大。
加上 $\lambda\sum_j\beta_j^2$（λ &gt; 0）後，係數變大要付出無上限的代價，解就存在了。
這一段是依目標函數直接推得的，講義與 ISLP 第 9 章沒有展開；第 4 章提過類別分得很開時邏輯斯迴歸的估計不穩定。</p>
<p>反過來，hinge 只要 $y_if(x_i)\ge1$ 就停在 0，不會為了「分得更篤定」而無止境放大係數，
所以可分資料對支持向量分類器沒有這個問題。</p>
''' + links([("https://www.csie.ntu.edu.tw/~htlin/mooc/doc/205_handout.pdf", "林軒田：Kernel Logistic Regression（SVM 與 L2 邏輯斯迴歸）"),
             (URL["logloss"], "Cross Validated：兩種 logistic loss 寫法")])
    return detail("w10-detail-l2-logistic", "SVM 比較像加 L2 懲罰的邏輯斯迴歸，還是原本的邏輯斯迴歸？", body)


def hinge(old):
    h = old["hinge"]
    return "".join([
        _hinge_main(),
        _loss_detail(h),
        LOOK,
        "\n" + grab_viz(h, "w10lossChart") + "\n",
        _hinge_after_widget(),
        _l2_logistic_detail(),
        "\n" + grab_details(h, "w10-detail-hinge-lab") + "\n",
        "\n" + grab_quiz(h, "qHinge") + "\n",
    ])


def build(old):
    return {"soft": soft(old), "hinge": hinge(old)}
