"""第 9 章整節重寫 A：prologue（開場、為什麼用 SVM、超平面）與 maxmargin（最大邊界、primal／dual）。

正文來源：講義 09、ISLP §9.1、課程 Lab；講義連結與其他補充只放收合。規格見
tools/verification/ch9-svm-deepen-20261122/consult/audit.md。
"""
from svm_common import (URL, detail, grab_details, grab_qa, grab_quiz, grab_viz, links, qa_wrap,
                        quiz, table)


# ───────────────────────────── prologue ─────────────────────────────

def _prologue(old):
    B = old["prologue"]
    hyper_viz = grab_viz(B, "w10hyperSvg")
    lab_detail = grab_details(B, "w10-detail-prologue-lab")
    proof_distance = grab_details(B, "w10-proof-distance")
    q_hyp = grab_quiz(B, "qHyp")

    opening = r'''
  <p>前面幾章介紹了不同的分類方式。講義把它們分成兩類：<strong>生成式</strong>方法先為每一類建模
  $\Pr(X \mid Y)$，再用貝氏定理翻成 $\Pr(Y \mid X)$，LDA 就是這樣；<strong>判別式</strong>方法直接建模
  $\Pr(Y \mid X)$，例如邏輯斯迴歸。這一章走得更直接：
  <strong>直接在特徵空間裡找一片把兩類分開的平面</strong>。不估機率、不假設分佈，就是幾何。</p>
'''

    gen_detail = detail("w10-detail-generative-discriminative", "生成式與判別式：SVM 到底學了什麼？", r'''
<p>生成式方法把貝氏定理用在每一類的特徵分布上；SVM 只看帶正負號的決策分數 $f(x)$：</p>
$$P(Y=k\mid x)=\frac{\pi_k p(x\mid Y=k)}{\sum_\ell\pi_\ell p(x\mid Y=\ell)},\qquad \hat y_{\rm SVM}=\operatorname{sign}(f(x)).$$
<p>生成式方法的問題是「每類通常會產生怎樣的資料？」判別式方法的問題是「給定這筆資料，類別應該怎麼分？」SVM 進一步把學習問題寫成「保留間隔，同時付出多少違反間隔的成本？」因此不需要假設每一類都是 Gaussian，也不能從沒有 Gaussian 假設推論 SVM 一定更準。</p>
<p>講義附錄以回應／特徵的資料型態整理統計方法，那是選方法的起點。LDA 需要檢查類別條件分布及共變異數假設；邏輯斯迴歸不要求特徵為非 Gaussian，也可以處理 Gaussian 特徵。ANOVA 與迴歸也不是互斥的工具：類別特徵可以透過指示碼進入迴歸。</p>
<p>講義在這裡連到 Analytics Vidhya 的一篇介紹文。讀的時候注意兩點：文中「生成式模型」例子裡的 LDA 是主題模型 Latent Dirichlet Allocation，不是第 4 章的線性判別分析；文章把 SVM 歸為判別式，但沒有區分「估 $\Pr(Y\mid X)$ 的判別式」（邏輯斯迴歸）與「只學分界的判別式」（SVM）。</p>
''' + links([(URL["vidhya"], "Analytics Vidhya：生成式與判別式模型"),
              ("https://scikit-learn.org/1.6/modules/lda_qda.html", "scikit-learn：LDA／QDA 的機率模型")]))

    structure = r'''
  <p>講義整理了本章的思路：先試著找一片<strong>分得開</strong>的平面；
  如果找不到，往兩個方向想辦法。<strong>把「分開」的定義放鬆</strong>（軟邊界），
  以及<strong>把特徵空間變大</strong>（核）。這兩招合起來就是支持向量機。</p>

<div class="info-box">
  <span class="info-label">三層結構，一層一層加東西</span>
  <strong>1. 最大邊界分類器（maximal margin classifier）：</strong>
  資料完全分得開時，選離兩邊都最遠的那一刀。<br>
  <strong>2. 支持向量分類器（support vector classifier）：</strong>允許少數點犯規，
  用一個調整參數決定容忍度。也叫軟邊界分類器。<br>
  <strong>3. 支持向量機（support vector machine, SVM）：</strong>把內積換成核，
  邊界就彎起來了。<br>
  三者是<strong>逐步擴充的三個層次</strong>。最外面那層用線性核時
  就得到線性的支持向量分類器，仍然是第二層的軟邊界；線性核本身不會移除容錯懲罰。
</div>
'''

    why = r'''
  <h3 id="w10-why-svm">為什麼用 SVM？</h3>
  <p>講義用一個問題開場：做分類時，我們其實只需要知道那片分界超平面，何必先建一個完整的機率模型？
  SVM 就是只學分界的方法。講義列了它的優點與缺點：</p>
''' + table(["", "講義的說法", "怎麼讀"], [
        ["✓", "特徵數 p 大於樣本數 n 時仍然有效",
         "p &gt; n 時資料很容易被某個超平面分開；SVM 在可行的分界中挑間隔最大的，再用軟邊界的調整參數控制彈性。"],
        ["✓", "決策函數只用到一部分訓練點（支持向量），所以省記憶體與預測時間",
         "ISLP 的說法是：分類規則只依賴可能很少的一群支持向量，其他點不影響它。"],
        ["✓", "用途廣：決策函數可以換不同的核，也能自訂核", '見本頁的<a href="#kernel">核技巧</a>一節。'],
        ["✗", "不直接提供機率估計", '要機率得另外校準，見<a href="#vslogit">與邏輯斯迴歸的關係</a>一節。'],
        ["✗", "p ≫ n 時正則化非常關鍵", "ISLP 也警告：p 很大時最大邊界分類器會過度擬合。"],
    ]) + r'''
  <p>第二點最容易讀錯。它說的是擬合<strong>之後</strong>的決策函數：ISLP 強調分類規則只依賴可能很少的一群支持向量。
  訓練時並不知道誰會是支持向量，仍要用全部資料求解。講義與 ISLP 沒有說「省」是跟哪個方法比，
  下面的收合整理了幾種讀法。</p>
'''

    why_detail = detail("w10-detail-why-svm", "SVM 的優點要怎麼讀：比較對象、p &gt; n 與計算成本", r'''
<p>講義這張投影片的優缺點清單，跟 scikit-learn SVM 使用手冊開頭的清單幾乎逐字相同。手冊原句只寫「省記憶體」，沒有說跟哪個方法比，也沒有解釋為什麼 p &gt; n 仍然有效。下面是本頁的解讀，不是來源原文。</p>
<h3>效率是跟誰比？</h3>
<p>核 SVM 的預測式是 $f(x)=\hat\beta_0+\sum_{i\in S}\hat\alpha_i y_iK(x,x_i)$，只需要保存支持向量集合 $S$ 及其係數；預測一筆新資料的計算量大約是「支持向量個數 × 一次核計算」。</p>
''' + table(["方法", "擬合後要保存什麼", "預測一筆的主要成本"], [
        ["KNN", "整份訓練資料", "與全部 n 筆計算距離"],
        ["邏輯斯迴歸、LDA", "係數（LDA 另有各類平均與共變異）", "與 p 成正比"],
        ["線性 SVM", "可把 $\\sum_i\\hat\\alpha_iy_ix_i$ 合併成 $\\hat\\beta$，只存係數", "與 p 成正比"],
        ["核 SVM", "支持向量與 $\\hat\\alpha_i$", "與支持向量個數成正比"],
    ]) + r'''
<p>從這張表看，「只用支持向量」的節省，是相對於預測時要用到全部訓練點的方法：例如 KNN，或同樣用核、但每個訓練點都有非零係數的核嶺迴歸與核邏輯斯迴歸（林軒田的講義指出它們的係數是稠密的，SVM 的則是稀疏的；見<a href="#vslogit">與邏輯斯迴歸的關係</a>一節的收合）。和只存係數的線性方法相比，就談不上省。若大多數訓練點都成了支持向量（例如 C 很小、類別重疊嚴重），核 SVM 的預測就不再便宜。訓練成本另計，見與邏輯斯迴歸的關係一節的收合<a href="#w10-detail-model-comparison">「對照表背後的幾件事」</a>。</p>
<h3>p &gt; n 為什麼仍然有效？</h3>
<p>這句話有兩層意思，要分開看。</p>
<ul>
<li><strong>泛化：</strong>講義在不可分資料那一頁說，除非 $n\lt p$，資料通常分不開；反過來，$p\gt n$ 時很容易找到把訓練資料完全分開的超平面。最大邊界在無限多個可行分界中挑間隔最大的那片，但 ISLP 警告它在 p 大時會過度擬合，所以實務上靠軟邊界的調整參數（正則化）控制彈性。手冊的缺點「p ≫ n 時正則化非常關鍵」講的正是這件事。</li>
<li><strong>計算：</strong>對偶問題只有 n 個變數、n+1 條限制，林軒田的講義稱它「適合 N 小」的情形；p 只經由內積進來。不過對偶的每個元素仍是一次 p 維內積，而且 n×n 的矩陣很佔記憶體：林軒田的講義舉例 n = 30,000 時，稠密矩陣要 3 GB 以上，所以需要專門的求解器。</li>
</ul>
<p>前者回答「為什麼不會一碰到 p &gt; n 就失效」，後者回答「為什麼算得動」。兩者都不保證 p &gt; n 時測試誤差一定小；Lab 的 Khan 基因資料就是訓練誤差為 0、測試仍有錯分的例子。</p>
''' + links([(URL["sksvm"], "scikit-learn：SVM 的優點與缺點"),
              (URL["h202"], "林軒田：Dual SVM（primal 與 dual 的變數個數）")]))

    q_why = quiz("qWhy", "QUIZ · 為什麼用 SVM",
                 "講義說 SVM 的決策函數只用到一部分訓練點（支持向量）。下面哪一句正確？",
                 [(True, "擬合完成後，分類規則只依賴支持向量；移動嚴格在 margin 正確一側的點不改變分類器",
                   "對。這是 ISLP 強調的性質：決策函數只由支持向量組成，其餘點只要留在 margin 正確一側，怎麼動都不影響它。"),
                  (False, "訓練時也只需要支持向量，所以 SVM 的訓練一定比邏輯斯迴歸快",
                   "不對。訓練前不知道誰會是支持向量，求解時仍要處理全部資料；核 SVM 的訓練成本還會隨樣本數快速增加。"),
                  (False, "支持向量一定只占少數，所以預測永遠很便宜",
                   "不對。支持向量的多寡跟調整參數與資料有關；類別重疊嚴重或間隔很寬時，大多數點都可能成為支持向量。")])

    hyper = r'''
  <p>起點是<strong>超平面</strong>（hyperplane）。p 維空間裡的超平面是一個 p − 1 維的
  平坦仿射子空間；p = 2 就是一條線，p = 3 就是一個平面。它的方程式是：</p>

  $$\beta_0 + \beta_1 X_1 + \beta_2 X_2 + \cdots + \beta_p X_p = 0$$

  <p>「仿射」表示它不一定通過原點：$\beta_0 = 0$ 時超平面通過原點，否則就是平移過的。
  「平坦」表示它不彎曲。</p>
'''

    affine_detail = detail("w10-detail-affine", "平坦仿射子空間是什麼？線性子空間、仿射與 flat", r'''
<p><strong>線性子空間</strong> $V\subseteq\mathbb R^p$ 必須包含零向量，而且對加法與純量乘法封閉：$u,v\in V$ 時，任何 $au+bv$ 也在 $V$ 裡。過原點的直線、過原點的平面都是例子。</p>
<p><strong>仿射子空間</strong>是把某個線性子空間整體平移：
$$A=x_0+V=\{x_0+v: v\in V\}.$$
它的維度就是 $V$ 的維度。仿射子空間不要求含原點；不含原點時，它對加法與純量乘法都不封閉（含原點時就是線性子空間）。但它一定對「權重和為 1 的組合」封閉：$u,v\in A$ 時，$tu+(1-t)v\in A$。</p>
<p><strong>flat</strong> 在幾何裡就是仿射子空間的另一個名字，強調它是「平的」：點、直線、平面以及更高維的類比都是 flat。ISLP 把兩個詞連用，是在強調同一件事。</p>
<h3>超平面為什麼是 p − 1 維？</h3>
<p>設 $\beta=(\beta_1,\dots,\beta_p)\ne 0$，超平面 $H=\{x:\beta_0+\beta^Tx=0\}$。取 $H$ 上的一點 $x_0=-\beta_0\beta/\|\beta\|^2$，則</p>
$$H=x_0+V,\qquad V=\{v:\beta^Tv=0\}.$$
<p>$V$ 是由一條線性方程式定義的線性子空間（$1\times p$ 矩陣 $\beta^T$ 的零空間），維度是 $p-1$。法向量 $\beta$ 與 $V$ 裡的每個方向都垂直。$\beta_0\ne0$ 時原點不在 $H$ 上，兩個 $H$ 上的點相加也不在 $H$ 上，所以 $H$ 只是仿射子空間，不是線性子空間。</p>
<p>例：ISLP 圖 9.1 的 $1+2X_1+3X_2=0$ 是 $\mathbb R^2$ 裡的一條線（1 維），不過原點；它的方向空間是 $\{v:2v_1+3v_2=0\}$，也就是過原點、斜率 $-2/3$ 的那條線。</p>
''')

    distance = r'''
  <p>寫成 $f(X) = \beta_0 + \beta^{\top} X$。滿足 $f(X) = 0$ 的點在超平面上，
  $f(X) > 0$ 的點在一側、$f(X) &lt; 0$ 的點在另一側。所以<strong>只要看 $f(X)$ 的正負號，
  就知道一個點站在哪一邊</strong>，分類問題被壓成一次算術。</p>

  <p>而且 $f(X)$ 的<strong>大小</strong>也有意思。向量 $\beta = (\beta_1,\dots,\beta_p)$
  是超平面的<strong>法向量</strong>（normal vector），指向與超平面垂直的方向；
  點 $x$ 到超平面的垂直距離正好是</p>

  $$\text{距離} = \frac{|f(x)|}{\lVert \beta \rVert},
    \qquad \lVert \beta \rVert = \sqrt{\beta_1^2 + \cdots + \beta_p^2}$$

  <p>拿掉絕對值的 $f(x)/\lVert\beta\rVert$ 帶有正負號，講義稱它為<strong>純量投影</strong>（scalar projection）：
  大小是距離，正負號說明點在哪一側。
  所以 $|f(x)|$ 大就是離邊界遠、這個判斷有把握；$|f(x)|$ 接近 0 就是貼在邊界上、
  隨時可能翻盤。這個「離邊界多遠 ＝ 多有把握」的直覺，是整章的地基。</p>
'''

    distance_detail = detail("w10-detail-distance", "計算：點到超平面的距離、純量投影與向量投影", r'''<h3 id="w10-distance-normal">點到超平面的距離</h3>
<p>對 $w\ne0$，點 $x$ 到 $w^Tz+b=0$ 的距離為 $|w^Tx+b|/\|w\|$。
若 $w=0$，就不是這裡所說的超平面，不能除以 $\|w\|$。</p>
''' + proof_distance + r'''
<h3>純量投影與向量投影</h3>
<p>把向量 $a$ 投影到非零向量 $b$ 的方向上，有兩種說法：</p>
$$\underbrace{s=\frac{a^Tb}{\|b\|}}_{\text{純量投影}},\qquad
\underbrace{\operatorname{proj}_b a=\frac{a^Tb}{\|b\|^2}\,b=s\,\frac{b}{\|b\|}}_{\text{向量投影}}.$$
<p>純量投影是一個數：投影的長度，方向與 $b$ 相反時帶負號。向量投影是一個向量：沿 $b$ 方向走 $s$ 單位。兩者的關係是 $|s|=\|\operatorname{proj}_b a\|$，再乘上單位向量 $b/\|b\|$ 就從純量投影變成向量投影。</p>
<p>回到超平面。任取超平面上一點 $x_H$（滿足 $\beta^Tx_H=-\beta_0$），令 $a=x-x_H$、$b=\beta$：</p>
$$s=\frac{\beta^T(x-x_H)}{\|\beta\|}=\frac{\beta^Tx+\beta_0}{\|\beta\|}=\frac{f(x)}{\|\beta\|}.$$
<p>所以講義說的「純量投影」就是帶正負號的距離，它跟選哪一個 $x_H$ 無關。對應的向量投影 $\dfrac{f(x)}{\|\beta\|^2}\beta$ 則是從垂足指向 $x$ 的那段位移；上面證明裡的 $tw$ 就是它。</p>
''' + links([(URL["dist"], "Wikipedia：點到直線的距離"), (URL["proj"], "Wikipedia：純量投影")]))

    separating = r'''
  <p>有了超平面，分類規則就寫完了：把 $y_i$ 編碼成 $\pm 1$，
  <strong>分離超平面</strong>（separating hyperplane）就是滿足</p>

  $$y_i\left(\beta_0 + \beta_1 x_{i1} + \cdots + \beta_p x_{ip}\right) > 0
    \qquad \text{對每一筆 } i = 1, \dots, n$$

  <p>的那些超平面（ISLP 式 9.8）。這一個式子把「藍色的要 $f > 0$、紫色的要 $f &lt; 0$」
  兩條規則合成一條，因為 $y_i$ 自己會把符號翻過來。這個 $y_i f(x_i)$ 之後會一直出現，
  它就是<strong>「這一筆分對了嗎、有多篤定」</strong>的度量。</p>
'''

    body = (opening + gen_detail + structure + why + why_detail + q_why + hyper + affine_detail
            + distance + distance_detail + "\n" + hyper_viz + "\n" + separating + "\n  " + lab_detail
            + "\n" + q_hyp + "\n")
    return body


# ───────────────────────────── maxmargin ─────────────────────────────

def _maxmargin(old):
    B = old["maxmargin"]
    margin_viz = grab_viz(B, "w10marginSvg")
    proof_hard = grab_details(B, "w10-proof-hard-dual")
    q_max = grab_quiz(B, "qMax")
    perceptron = grab_details(B, "w10-detail-perceptron")
    qa_large = grab_qa(B, "Q：margin 大在測試資料上真的比較好嗎？")

    intro = r'''
  <p>如果資料真的分得開，麻煩來了：<strong>分離超平面有無限多個</strong>。
  隨便一條分得開的線，都可以稍微平移一點、旋轉一點，還是分得開（ISLP 圖 9.2 左畫了三條）。
  無限多個候選，總得有個挑法。</p>

  <p>挑法很自然：<strong>選離兩邊都最遠的那一條</strong>。先算每個訓練點到超平面的垂直距離，
  其中<strong>最小</strong>的那個距離叫做<strong>邊界</strong>（margin，ISLP 記為 M）；
  邊界最大的那個分離超平面就是<strong>最大邊界超平面</strong>（maximal margin hyperplane，
  也叫最佳分離超平面）。用它做分類就是<strong>最大邊界分類器</strong>。</p>

<div class="info-box">
  <span class="info-label">一句話的幾何直覺</span>
  最大邊界超平面就是<strong>能塞進兩類之間那塊最寬「板子」的中線</strong>。
  板子有多寬由最擠的地方決定，所以答案只跟「最擠的那幾個點」有關。這件事後面會一再用到。
</div>

  <p>寫成最佳化問題（ISLP 式 9.9–9.11）：</p>

  $$\begin{aligned}
    &\underset{\beta_0,\beta_1,\dots,\beta_p,\,M}{\text{maximize}} \quad M \\
    &\text{subject to} \quad \sum_{j=1}^{p} \beta_j^2 = 1, \\
    &\qquad\qquad\quad\; y_i\left(\beta_0 + \beta_1 x_{i1} + \cdots + \beta_p x_{ip}\right)
      \ge M \quad \forall\, i
  \end{aligned}$$

  <p>兩個限制式各有分工。係數整組縮放不會改變超平面，所以 $\sum \beta_j^2 = 1$ 不是在限制超平面，
  而是挑出一組代表；在這組代表下，<strong>$y_i f(x_i)$ 正好是第 i 筆到超平面的垂直距離</strong>。
  於是第二條 $y_i f(x_i) \ge M$ 說的是「每一筆都在正確一側，而且至少離 M 遠」；只要 $M>0$，
  這比單純分對多要求了一段緩衝。M 就是邊界，目標函數就是把它推到最大。</p>
'''

    after_viz = r'''
  <p>虛線上的點叫做<strong>支持向量</strong>（support vector）：它們是 p 維空間裡的向量，而且「撐住」了超平面，
  稍微移動它們，最大邊界超平面就會跟著動。移動其他點則不影響超平面，只要那個點沒有越過 margin。
  （這是講義與 ISLP 的幾何定義。推導時還有一個對偶定義：乘子 $\hat\alpha_i>0$ 的點。兩者只在資料退化時不同，虛線上的點可能乘子為 0，見下方推導收合。）
  ISLP 對這個性質的說明是：</p>

<div class="info-box warm">
  <span class="info-label">最大邊界超平面只依賴支持向量，不依賴其他觀測值</span>
  這是本章反覆出現的主題。
  好處是<strong>對離邊界很遠的點非常穩健</strong>：LDA 的規則要用到每一類的平均與整體共變異，
  換掉一個遠處的點就會動；最大邊界超平面不會。<br>
  壞處是<strong>對支持向量非常敏感</strong>。ISLP 圖 9.5 就是這個代價：右圖只多加一個藍點，
  最大邊界超平面就大幅轉向，而且 margin 縮到極窄。只靠三個點決定的分類器，
  下一節會用軟邊界改善這種敏感性。
</div>

  <p><strong>ISLP §9.7 第 3 題就是這個元件的手算版</strong>。它給你 7 個點，
  答案是 $X_2 = X_1 - 0.5$，支持向量是第 2、3、5、6 筆，$M = 1/(2\sqrt{2}) \approx 0.354$；
  第 (f) 小題問「第 7 筆稍微移動會不會影響超平面」。你在上面拖過就知道答案了。
  本頁練習區的第 3 題會再問一次。</p>
'''

    primal_dual = r'''
  <h3 id="w10-primal-dual">怎麼解：primal 與 dual</h3>
  <p>上面的寫法很直觀，卻不好直接求解。講義把它改寫成兩個等價的問題。第一步是換一組代表：
  不再要求 $\lVert\beta\rVert = 1$，而是縮放係數，讓最靠近的那幾點剛好有 $y_i f(x_i) = 1$。
  這時邊界就是 $M = 1/\lVert\beta\rVert$，<strong>最大化 M 等於最小化 $\lVert\beta\rVert$</strong>。
  這個換法為什麼合法、β 為什麼會變而邊界不變，下一節的<a href="#soft">三個等價式</a>會一步一步說明
  （硬邊界就是其中所有 $\epsilon_i = 0$ 的情形）。</p>

  <p><strong>原始問題（primal）</strong>直接求超平面的係數：</p>
  $$\min_{\beta_0,\beta}\ L_P=\frac12\lVert\beta\rVert^2
    \qquad\text{subject to}\quad y_i\left(x_i^T\beta+\beta_0\right)\ge 1,\quad i=1,\dots,n.$$
  <p>它有 $p+1$ 個變數、$n$ 條限制，<strong>適合 p 小</strong>的情形。</p>

  <p><strong>對偶問題（dual）</strong>改成替每一筆資料找一個權重 $\alpha_i$：</p>
  $$\max_{\alpha}\ L_D=\sum_{i=1}^{n}\alpha_i-\frac12\sum_{i=1}^{n}\sum_{i'=1}^{n}\alpha_i\alpha_{i'}y_iy_{i'}\,x_i^Tx_{i'}
    \qquad\text{subject to}\quad \alpha_i\ge 0,\quad \sum_{i=1}^{n}\alpha_iy_i=0.$$
  <p>它有 $n$ 個變數、$n+1$ 條限制，<strong>適合 n 小</strong>的情形。更重要的是，資料只以內積
  $x_i^Tx_{i'}$ 的形式出現，這正是後面<a href="#kernel">核技巧</a>的入口。解出 $\hat\alpha$ 之後，
  係數是 $\hat\beta=\sum_i\hat\alpha_iy_ix_i$；只有支持向量的 $\hat\alpha_i$ 不是 0，
  所以 $\hat\beta$ 只由支持向量組成。</p>
'''

    hard_detail = detail("w10-detail-hard-dual", "推導：Lagrangian、對偶與 KKT", r'''
<p>以下沿用講義連結的寫法，令標籤 $y_i\in\{-1,+1\}$，$f(x)=b+w^Tx$（即 $\beta_0$、$\beta$），兩類都至少有一筆，並假設訓練資料線性可分。縮放後最近點的<strong>函數間隔</strong> $y_if(x_i)$ 等於 1，此時幾何半寬是 $1/\|w\|$，整條間隔帶寬是 $2/\|w\|$。對偶問題裡令 $K_{ij}=x_i^Tx_j$：</p>
$$\max_{\alpha\in\mathbb R^n}\ D(\alpha)
=\sum_i\alpha_i-\frac12\sum_{i,j}\alpha_i\alpha_jy_iy_jK_{ij},
\qquad \alpha_i\ge0,\quad \sum_i\alpha_i y_i=0.$$
<p>等式限制不能省略：它來自未受懲罰的截距 $b$。求得 $\hat\alpha$ 後，
$\hat w=\sum_i\hat\alpha_i y_i x_i$；對任何 $\hat\alpha_s&gt;0$ 的點，
$\hat b=y_s-\hat w^Tx_s$。這些點才是這個對偶解的支持向量。
位於間隔邊界是必要條件，但退化時，邊界上的點也可能有 $\alpha_i=0$。</p>
''' + proof_hard + r'''
<h3>$-\tfrac12$ 是從哪裡來的？</h3>
<p>常見的疑問是：$\tfrac12\|w\|^2$ 明明是正的，代入後怎麼變成減掉 $\tfrac12\|\cdot\|^2$？負號不是 $\tfrac12\|w\|^2$ 自己變出來的，而是整個 Lagrangian 合併的結果。把 $w=\sum_i\alpha_iy_ix_i$ 與 $\sum_i\alpha_iy_i=0$ 代入</p>
$$L=\frac12\|w\|^2+\sum_i\alpha_i-\sum_i\alpha_iy_i\,w^Tx_i-b\sum_i\alpha_iy_i .$$
<p>最後一項是 0。中間的交叉項是 $w^T\!\left(\sum_i\alpha_iy_ix_i\right)=w^Tw=\|w\|^2$，所以</p>
$$L=\frac12\|w\|^2+\sum_i\alpha_i-\|w\|^2=\sum_i\alpha_i-\frac12\Big\|\sum_i\alpha_iy_ix_i\Big\|^2 .$$
<p>也就是「原本的 $+\tfrac12\|w\|^2$」加上「乘子項貢獻的 $-\|w\|^2$」。</p>
<h3>乘子要 ≥ 0，不必 &gt; 0</h3>
<p>不等式限制 $1-y_if(x_i)\le0$ 的乘子必須<strong>非負</strong>。林軒田的講義用一個 max 說明原因：對一組 $(w,b)$，若某條限制被違反，$1-y_if(x_i)&gt;0$，讓對應的 $\alpha_i\to\infty$ 會使 $\max_{\alpha\ge0}L$ 變成無限大；若全部限制都成立，每一項 $\alpha_i[1-y_if(x_i)]\le0$，最大值在 $\alpha_i=0$ 取得，剛好等於 $\tfrac12\|w\|^2$。限制就這樣「藏進 max 裡」。如果允許 $\alpha_i&lt;0$，可行點也會被推到無限大，這個等價就不成立。</p>
<p>$\alpha_i=0$ 是允許的，而且最常見：互補鬆弛 $\alpha_i[1-y_if(x_i)]=0$ 讓所有嚴格在間隔外的點乘子為 0。「&gt; 0」只用來<strong>定義</strong>支持向量：$\alpha_i&gt;0$ 的點必在間隔邊界上，反過來，邊界上的點只是「候選」，乘子仍可能是 0。</p>
<h3>primal 與 dual 的取捨</h3>
<p>Primal 有 $p+1$ 個主要未知數；dual 有 $n$ 個。但 dual 並沒有完全擺脫 $p$：每個 $K_{ij}$ 仍是一次 $p$ 維內積，而且 $n\times n$ 的矩陣很佔記憶體，所以實務上的求解器不會把整個矩陣存下來。Dual 真正的好處是只透過內積接觸特徵，可以直接換成核函數。計算速度還受資料稀疏度與求解器影響，不能只由未知數數量判斷。</p>
<p>弱對偶表示任何可行 dual 值都是 primal 最小值的下界。線性可分時，縮放一個分隔面可使所有間隔限制嚴格成立（Slater 條件）；在這個凸問題下強對偶成立，最適值相等。實際讀解時依序檢查：$y_if(x_i)\ge1$、$\alpha_i\ge0$、$\sum_i\alpha_i y_i=0$、$w=\sum_i\alpha_i y_ix_i$，最後檢查 $\alpha_i[y_if(x_i)-1]=0$。</p>
<p>線性可分時，硬邊界的最佳超平面 $(w,b)$ 是唯一的（目標對 $w$ 嚴格凸，兩類各有取等號的限制把截距固定）；退化時不唯一的是乘子 $\alpha$。軟邊界的截距則可能落在一個區間。不可分時硬邊界問題沒有可行解，要改用下一節的軟邊界。</p>
''' + links([(URL["h202"], "林軒田：Dual SVM"), (URL["duality"], "Wikipedia：最佳化的對偶"),
              (URL["cs229"], "Stanford CS229：SVM 講義")]))

    qa_sv = r'''  <details class="qa-item"><summary>Q：為什麼叫「支持向量」？為什麼只有它們影響解？</summary>
    <div class="qa-a"><p>先說「向量」：在 p 維空間裡，一筆觀測值 $x_i$ 就是一個 p 維向量，所以這些點本來就是向量。「支持」則是力學的比喻：它們撐住了超平面，移動其中一點，最佳邊界可能跟著動。</p><p><strong>從最佳化的角度看：</strong>最大邊界問題的限制式是 $y_i f(x_i) \ge M$。在最佳解上，只有<strong>取等號</strong>的那些限制式是「緊的」（active）；取嚴格大於的限制式仍有餘裕，把它整條刪掉，解一模一樣。對偶解把這件事寫成乘子：鬆的限制乘子為 0，只有乘子為正的點出現在 $\hat\beta=\sum_i\hat\alpha_iy_ix_i$ 裡。邊界上的點可能有零乘子，所以「取等號」與「乘子為正」不是雙向等價。</p><p><strong>從損失函數的角度看：</strong><a href="#hinge">Hinge loss 一節</a>會說明支持向量分類器等價於最小化 hinge loss 加上 ridge 懲罰。$y_i f(x_i) > 1$ 的點落在損失曲線的平坦區，不影響目前的最佳解；$y_i f(x_i) = 1$ 的點雖然損失也是 0，卻位於折角，仍可能是支撐解的支持向量。</p></div>
  </details>'''

    body = (intro + "\n" + margin_viz + "\n" + after_viz + primal_dual + hard_detail + "\n"
            + qa_wrap("觀念釐清", [qa_sv, "  " + qa_large]) + "\n" + q_max + "\n" + perceptron + "\n")
    return body


def build(old):
    return {"prologue": _prologue(old), "maxmargin": _maxmargin(old)}
