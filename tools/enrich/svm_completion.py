"""講義 09 與直接連結教材的完整最佳化補充。"""
from lib import proof, quiz, table


def insert_before_quiz(body, addition):
    marker = '<div class="quiz-box">'
    return body.replace(marker, addition + '\n' + marker, 1)


def complete(bodies):
    hard = r'''
<h3 id="w10-primal-dual">把最大邊界寫成可求解的問題</h3>
<p>以下令標籤 $y_i\in\{-1,+1\}$，$f(x)=b+w^Tx$，兩類都至少有一筆。
先假設訓練資料線性可分。前面的 $\|\beta\|=1$ 固定方向長度、最大化幾何邊界 $M$；
現在同時縮放係數與截距，使最近點的<strong>函數間隔</strong> $y_i f(x_i)$ 等於 1。
此時幾何半寬是 $1/\|w\|$，整條間隔帶寬是 $2/\|w\|$。</p>
<p><strong>原始問題（primal）</strong>直接求超平面的係數：</p>
$$\min_{w,b}\ \frac12\|w\|^2\qquad
\text{使得 }y_i(w^Tx_i+b)\ge1\quad(i=1,\ldots,n).$$
<p><strong>對偶問題（dual）</strong>改求每個限制式的非負乘子。令 $K_{ij}=x_i^Tx_j$：</p>
$$\max_{\alpha\in\mathbb R^n}\ D(\alpha)
=\sum_i\alpha_i-\frac12\sum_{i,j}\alpha_i\alpha_jy_iy_jK_{ij},
\qquad \alpha_i\ge0,\quad \sum_i\alpha_i y_i=0.$$
<p>等式限制不能省略：它來自未受懲罰的截距 $b$。求得 $\hat\alpha$ 後，
$\hat w=\sum_i\hat\alpha_i y_i x_i$；對任何 $\hat\alpha_s&gt;0$ 的點，
$\hat b=y_s-\hat w^Tx_s$。這些點才是這個對偶解的支持向量。
位於間隔邊界是必要條件，但退化時，邊界上的點也可能有 $\alpha_i=0$。</p>
'''
    hard += proof('w10-proof-hard-dual', '硬邊界的 Lagrangian、對偶與 KKT', r'''
<p>從單位長度的表示令 $w=\beta/M$、$b=\beta_0/M$，就有
$\|w\|=1/M$ 與 $y_i(w^Tx_i+b)\ge1$。最大化 $M&gt;0$ 等價於最小化
$\|w\|$，也等價於最小化其平方的一半。</p>
<p>把限制寫成 $1-y_i(w^Tx_i+b)\le0$，Lagrangian 為</p>
$$L(w,b,\alpha)=\frac12\|w\|^2+
\sum_i\alpha_i[1-y_i(w^Tx_i+b)],\qquad \alpha_i\ge0.$$
<p>對固定的非負 $\alpha$，$g(\alpha)=\inf_{w,b}L$ 是原始最小值的下界，
所以對偶是最大化這個下界。先對原始變數求最小：</p>
$$\nabla_w L=w-\sum_i\alpha_i y_i x_i=0,\qquad
\frac{\partial L}{\partial b}=-\sum_i\alpha_i y_i=0.$$
<p>若第二式不成立，線性項可隨 $b$ 趨向負無限，$g(\alpha)=-\infty$；因此必須保留等式限制。
代入第一式，$\sum_i\alpha_i y_iw^Tx_i=\|w\|^2$，便得到</p>
$$g(\alpha)=\sum_i\alpha_i-\frac12\left\|\sum_i\alpha_i y_ix_i\right\|^2
=D(\alpha).$$
<p>可分時可把分離超平面放大到所有限制均嚴格成立，因此滿足 Slater 條件。
這是凸問題，故原始與對偶最佳值相同。其 KKT 條件完整列為</p>
$$\begin{aligned}
y_i(w^Tx_i+b)&\ge1 &&\text{原始可行},\\
\alpha_i&\ge0 &&\text{對偶可行},\\
w=\sum_i\alpha_i y_ix_i,\quad\sum_i\alpha_i y_i&=0 &&\text{stationarity},\\
\alpha_i[1-y_i(w^Tx_i+b)]&=0 &&\text{互補鬆弛}.
\end{aligned}$$
<p>最後一式使 $\alpha_s&gt;0$ 的點滿足 $y_sf(x_s)=1$，且 $y_s^2=1$，
所以 $b=y_s-w^Tx_s$。嚴格位於間隔外的點必有零乘子；反向推論需注意等號與退化情況。</p>
<p>來源：講義 09 第 15、17 頁；
<a href="https://www.csie.ntu.edu.tw/~htlin/mooc/doc/202_handout.pdf#page=6">林軒田：Dual SVM，PDF 第 6–21 頁</a>。</p>
''')
    hard += r'''
<p><strong>可自行算完的例子。</strong>只有兩點 $(x_1,y_1)=(-1,-1)$、$(x_2,y_2)=(1,1)$。
等式限制給 $\alpha_1=\alpha_2=a$，對偶化成 $\max_{a\ge0}(2a-2a^2)$。
最大值在 $a=1/2$，得到 $w=1,b=0$。原始值 $w^2/2=1/2$ 與對偶值相等，
兩點的函數間隔都為 1，幾何半寬也為 1。</p>
'''
    bodies['maxmargin'] = insert_before_quiz(bodies['maxmargin'], hard)

    soft = r'''
<h3 id="w10-soft-dual">軟邊界：為什麼乘子多了一個上界？</h3>
<p>從此處起以 $C&gt;0$ 表示<strong>懲罰權重</strong>，另以 $B$ 表示違反量預算，避免兩者混淆。
軟邊界容許 $\xi_i\ge0$，原始問題為</p>
$$\min_{w,b,\xi}\frac12\|w\|^2+C\sum_i\xi_i,
\quad y_i(w^Tx_i+b)\ge1-\xi_i,\quad\xi_i\ge0.$$
<p>對偶的目標與硬邊界相同，但每個乘子現在都受 $C$ 限制：</p>
$$\max_{\alpha}\ \sum_i\alpha_i-\frac12\sum_{i,j}\alpha_i\alpha_jy_iy_jK_{ij},
\qquad 0\le\alpha_i\le C,\quad\sum_i\alpha_i y_i=0.$$
<p>對 $C&gt;0$ 的最佳解，$\xi_i=\max(0,1-y_if(x_i))$。
KKT 條件把點分成三類，表中邊界等號都要保留：</p>
'''
    soft += table(['乘子','最佳解上的位置','如何解讀'],[
        [r'$\alpha_i=0$',r'$\xi_i=0,\ y_if(x_i)\ge1$','該對偶解不使用此點；退化時仍可能恰好在間隔上'],
        [r'$0&lt;\alpha_i&lt;C$',r'$\xi_i=0,\ y_if(x_i)=1$','自由支持向量，可用來回復截距'],
        [r'$\alpha_i=C$',r'$y_if(x_i)=1-\xi_i\le1$','有上界的支持向量；可能在間隔上、帶內或分錯，不等同於一定分錯']])
    soft += proof('w10-proof-soft-dual','軟邊界對偶的盒狀限制與完整 KKT',r'''
<p>對 margin 限制引入 $\alpha_i\ge0$，對 $-\xi_i\le0$ 引入 $\mu_i\ge0$：</p>
$$L=\frac12\|w\|^2+C\sum_i\xi_i+
\sum_i\alpha_i[1-\xi_i-y_i(w^Tx_i+b)]-\sum_i\mu_i\xi_i.$$
<p>對 $w,b$ 的導數與硬邊界相同，對每個 $\xi_i$ 則有</p>
$$C-\alpha_i-\mu_i=0\quad\Longrightarrow\quad0\le\alpha_i\le C.$$
<p>代入後含 $\xi_i$ 的項消失，留下正文的對偶目標。所有最佳化條件為</p>
$$\begin{gathered}
\xi_i\ge0,\quad y_if(x_i)\ge1-\xi_i,\quad\alpha_i\ge0,\quad\mu_i\ge0,\\
w=\sum_i\alpha_i y_ix_i,\quad\sum_i\alpha_iy_i=0,\quad C-\alpha_i-\mu_i=0,\\
\alpha_i[1-\xi_i-y_if(x_i)]=0,\qquad \mu_i\xi_i=0.
\end{gathered}$$
<p>$\alpha_i&lt;C$ 時 $\mu_i&gt;0$，因此 $\xi_i=0$；若又有 $\alpha_i&gt;0$，
第一個互補式迫使 $y_if(x_i)=1$。$\alpha_i=C$ 時只能由第一個互補式得到
$y_if(x_i)=1-\xi_i\le1$。這導出正文三類，而不是「支持向量都剛好在邊界上」。</p>
<p>即使不可分，取 $w=b=0$、所有 $\xi_i&gt;1$ 也嚴格可行，所以此凸問題仍有強對偶。
數值求解時另以可行殘差與 primal–dual gap 判斷精度，不能要求浮點數恰好等於零。</p>
<p>來源：講義 09 第 18 頁；
<a href="https://www.csie.ntu.edu.tw/~htlin/mooc/doc/204_handout.pdf">林軒田：Soft-Margin SVM</a>；
<a href="https://www.cs.cmu.edu/~epxing/Class/10701-08s/recitation/svm.pdf">CMU：SVM as a Convex Optimization Problem</a>。</p>
''')
    soft += r'''
<h4>回復截距與核對答案</h4>
<p>有 $0&lt;\alpha_s&lt;C$ 時，取 $b=y_s-\sum_i\alpha_i y_iK(x_i,x_s)$；
數值計算通常平均多個這類點的估計。若沒有自由支持向量，不能除以它們的數量，
也不能任取一個 $\alpha_s=C$ 的點套用等式。令 $g_i=\sum_j\alpha_jy_jK(x_j,x_i)$，
從零乘子的 $y_i(g_i+b)\ge1$ 及上界乘子的 $y_i(g_i+b)\le1$，
分別得到 $b$ 的上下界，選其可行區間內的值。</p>
<p><strong>接續兩點例子。</strong>設 $C=1/4$，則 $0\le a\le1/4$，最佳 $a=1/4$，
$w=1/2$。取 $b=0$，兩筆 $\xi_i=1/2$，原始值是
$1/8+(1/4)(1/2+1/2)=3/8$，對偶值亦為 $2(1/4)-2(1/4)^2=3/8$。
這裡兩點都達乘子上界，沒有自由支持向量；$b\in[-1/2,1/2]$ 都可行且最佳。
所以凸性不代表每個截距與每個對偶乘子都唯一。</p>
'''
    soft += quiz('qDualBounds','自我檢測 · 對偶與支持向量',
        r'在軟邊界最佳解中，$\alpha_i=C$ 能推出哪件事？',[
        (False,'此點一定被錯誤分類','上界乘子也可能對應間隔上的點，或分對但位於間隔帶內的點。'),
        (True,r'$y_if(x_i)\le1$，但不一定分錯',r'由互補鬆弛有 $y_if(x_i)=1-\xi_i$，且 $\xi_i\ge0$。分錯還要 $y_if(x_i)&lt;0$。'),
        (False,'可以無條件用 $b=y_i-w^Tx_i$ 求截距',r'這個等式需要 $\xi_i=0$。自由支持向量可保證它，上界支持向量則不能。')])
    bodies['soft'] = insert_before_quiz(bodies['soft'],soft)

    hinge = r'''
<h3 id="w10-penalty-normalization">把違反量消去：損失、懲罰與預算</h3>
<p>固定 $w,b$ 時，把每個 slack 選成最小可行值就得到</p>
$$\min_{w,b}\frac12\|w\|^2+C\sum_i[1-y_if(x_i)]_+,
\qquad [u]_+=\max(0,u).$$
<p>若損失寫成<strong>總和</strong> $\sum_i[1-y_if(x_i)]_++\lambda\|w\|^2$，
精確對應是 $\lambda=1/(2C)$；若寫成<strong>平均</strong>
$n^{-1}\sum_i[1-y_if(x_i)]_++\lambda\|w\|^2$，則為 $\lambda=1/(2nC)$。
截距在這些式子裡都不受懲罰。</p>
<p>違反量<strong>預算</strong> $B$ 與懲罰 $C$ 的對應則取決於資料與最佳解。
對應預算可由 $B(C)=\sum_i\hat\xi_i(C)$ 取得，可能有平坦區，不能套用 $C=1/B$。
固定資料、核與相同目標正規化時，增大 $C$ 會使最佳總 hinge loss 不增加、
$\|w\|$ 不減少；支持向量數、0–1 訓練錯誤與測試誤差則沒有同樣的普遍單調保證。</p>
'''
    hinge += proof('w10-proof-hinge','slack 消去及調整參數的精確對應',r'''
<p>限制給 $\xi_i\ge\max(0,1-y_if(x_i))$。因 $C&gt;0$，目標隨 slack 嚴格增加，
固定 $w,b$ 的最小值必在等號處，代入即為 hinge 形式。
將整個目標除以 $C$ 或 $nC$，就得到正文的兩種 $\lambda$。</p>
<p>考慮限制問題 $\min R(w)$ 使得 $H(w,b)\le B$，其中 $R=\|w\|^2/2$、
$H=\sum_i[1-y_if(x_i)]_+$。它對預算的 Lagrange 乘子是 $C\ge0$，
最小化 $R+C(H-B)$ 對固定 $C,B$ 等價於最小化 $R+CH$。
互補式 $C(H-B)=0$ 不會給出 $C=1/B$；要由實際最佳解連同可行與正則條件判定對應。</p>
<p>令 $C_2&gt;C_1&gt;0$，其最佳解有 $(R_1,H_1)$、$(R_2,H_2)$。
最佳性分別給 $R_1+C_1H_1\le R_2+C_1H_2$ 與
$R_2+C_2H_2\le R_1+C_2H_1$。相加得 $(C_2-C_1)(H_2-H_1)\le0$，
再代回第一式得 $R_1\le R_2$。這只能控制這兩項，不能推出支持向量數或測試誤差的單調性。</p>
<p>來源：講義 09 第 18、30 頁；ESL 習題 12.1；
<a href="https://scikit-learn.org/1.6/modules/svm.html#mathematical-formulation">scikit-learn 1.6 的數學定義</a>。</p>
''')
    bodies['hinge'] = insert_before_quiz(bodies['hinge'],hinge)

    kernel = r'''
<h3 id="w10-kernel-validity">可用的核與完整 Gram 矩陣</h3>
<p>核不能只是任意相似度。作為內積核，$K(x,z)=\langle\phi(x),\phi(z)\rangle$，
任意有限資料的 Gram 矩陣 $K$ 必須對稱且<strong>半正定</strong>：
$c^TKc\ge0$ 對所有向量 $c$ 成立。訓練也需要對角項 $K(x_i,x_i)$，
不是只算 $\binom n2$ 個不同點配對就夠。</p>
<p>以 $\alpha_i\ge0$ 表示 Lagrange 乘子時，完整預測式為</p>
$$f(x)=b+\sum_{i\in S}\alpha_i y_iK(x_i,x).$$
<p>ISLP 也把 $a_i=\alpha_i y_i$ 合併成帶正負號的係數，寫成
$b+\sum_i a_iK(x_i,x)$。兩種記號都可用，但不可把 $a_i$ 再當成非負乘子。
二元 <code>SVC.dual_coef_</code> 儲存的是帶標籤的係數；多類別的排列另外遵循成對分類器規則。</p>
'''
    kernel += proof('w10-proof-kernels','核的半正定性與 RBF 的特徵展開',r'''
<p>若 $K_{ij}=\langle\phi(x_i),\phi(x_j)\rangle$，則
$c^TKc=\|\sum_i c_i\phi(x_i)\|^2\ge0$。以此核取代內積後，對偶的二次矩陣為
$Q=\operatorname{diag}(y)K\operatorname{diag}(y)$，仍半正定，故最大化的對偶目標仍為凹函數。</p>
<p>以一維 RBF 為例，對 $\gamma&gt;0$，</p>
$$e^{-\gamma(x-z)^2}=e^{-\gamma x^2}e^{-\gamma z^2}e^{2\gamma xz}
=\sum_{m=0}^{\infty}
\left[e^{-\gamma x^2}\sqrt{\frac{(2\gamma)^m}{m!}}x^m\right]
\left[e^{-\gamma z^2}\sqrt{\frac{(2\gamma)^m}{m!}}z^m\right].$$
<p>中括號就是一組可明確寫出的無限特徵座標；多維可用多重指標展開。
因此困難在於不能逐一計算無限多個座標，並非特徵映射根本無法寫出。
實際上只計算左邊的一個核值即可。</p>
<p>來源：講義 09 第 24–26 頁；
<a href="https://cs229.stanford.edu/notes2021fall/cs229-notes3.pdf">Stanford CS229：Kernels and SVM</a>。</p>
''')
    kernel += r'''
<p><strong>半正定檢查例。</strong>對 $x=-1,1$ 的線性核，
$K=\begin{pmatrix}1&-1\\-1&1\end{pmatrix}$，其特徵值為 0、2。
零特徵值是允許的：合法核只需半正定，不必嚴格正定。
完整 Gram 矩陣通常需 $O(n^2)$ 儲存；大資料可考慮線性求解器或核近似。</p>
'''
    bodies['kernel'] = insert_before_quiz(bodies['kernel'],kernel)

    extra = r'''
<h3 id="w10-svr-complete">延伸：支持向量迴歸的管狀損失</h3>
<p>迴歸的 $y_i$ 是實數，$\varepsilon\ge0$ 是可接受的絕對誤差。
損失為 $[|y_i-f(x_i)|-\varepsilon]_+$。例如 $\varepsilon=0.2$，
殘差 0.1、0.5 的損失分別為 0、0.3；$\varepsilon$ 控制管寬，$C$ 控制超出管子的懲罰。</p>
$$\begin{aligned}
\min_{w,b,\xi,\xi^*}\quad&\frac12\|w\|^2+C\sum_i(\xi_i+\xi_i^*)\\
\text{使得}\quad&y_i-w^T\phi(x_i)-b\le\varepsilon+\xi_i,\\
&w^T\phi(x_i)+b-y_i\le\varepsilon+\xi_i^*,\quad\xi_i,\xi_i^*\ge0.
\end{aligned}$$
<p>令 $d_i=\alpha_i-\alpha_i^*$，其對偶與預測式為</p>
$$\max_{\alpha,\alpha^*}\ -\frac12\sum_{i,j}d_id_jK_{ij}
-\varepsilon\sum_i(\alpha_i+\alpha_i^*)+\sum_i y_i d_i,
\quad0\le\alpha_i,\alpha_i^*\le C,\quad\sum_i d_i=0,$$
$$f(x)=b+\sum_i d_iK(x_i,x).$$
<p>這裡係數不乘分類標籤 $y_i$。嚴格在管內的點兩個乘子均為零。
有 $0&lt;\alpha_i&lt;C$ 時用 $b=y_i-\varepsilon-\sum_jd_jK(x_j,x_i)$；
有 $0&lt;\alpha_i^*&lt;C$ 時用 $b=y_i+\varepsilon-\sum_jd_jK(x_j,x_i)$。
沒有這類點時也要從 KKT 不等式決定截距區間。</p>
'''
    extra += proof('w10-proof-svr','SVR 的兩組乘子如何產生對偶',r'''
<p>分別以 $\alpha_i,\alpha_i^*$ 乘上兩個管狀限制左側減右側，再以
$\mu_i,\mu_i^*$ 乘上 $-\xi_i,-\xi_i^*$。對 $w,b,\xi,\xi^*$ 求 stationarity 得</p>
$$w=\sum_i(\alpha_i-\alpha_i^*)\phi(x_i),\quad
\sum_i(\alpha_i-\alpha_i^*)=0,\quad
C-\alpha_i-\mu_i=C-\alpha_i^*-\mu_i^*=0.$$
<p>故兩組乘子都介於 0 與 $C$。代回 Lagrangian，$w$ 項合為
$-\|w\|^2/2$，常數項為 $\sum_i y_i(\alpha_i-\alpha_i^*)-
\varepsilon\sum_i(\alpha_i+\alpha_i^*)$，slack 項消失，得到正文對偶。
自由乘子所對應的 slack 為零，且管狀限制取等號，便得到兩種截距回復式。</p>
<p>來源：講義 09 第 34 頁直接連結的
<a href="https://www.csie.ntu.edu.tw/~htlin/mooc/doc/206_handout.pdf">林軒田：Support Vector Regression</a>。</p>
''')
    extra += r'''
<h3 id="w10-solvers">從公式選擇實作</h3>
<p><code>SVC(kernel='linear')</code> 與 <code>LinearSVC</code> 都可給線性邊界，
但後者預設使用 squared hinge，且截距的正則化處理也不同，不能期待相同 C 一定得同一解。
<code>NuSVC</code> 改以 $\nu$ 控制另一種限制，不是把參數 C 改名。</p>
<p>對二元訓練資料，在其可行設定下 $\nu$ 給訓練 margin error 比例的上界與支持向量比例的下界。
類別不平衡會限制可行 $\nu$；分類正負號、容差與 margin error 的定義須依求解器核對。
<code>OneClassSVM</code> 則主要用一類正常資料學習邊界，預測新點是否在正常區域；
訓練資料受污染及特徵尺度都會改變結果，不能把它直接當成有標籤二元 SVC。</p>
<p>核近似把輸入變成有限特徵，再交給線性模型。<code>RBFSampler</code> 用隨機 Fourier 特徵
近似 RBF 內積；<code>Nystroem</code> 選訓練資料中的代表點近似 Gram 矩陣。
代表點選取、標準化與後續模型都放在訓練折內；近似維度越大通常成本越高，精度需由驗證資料評估。</p>
<p>需要機率時，Platt scaling 擬合 $P(Y=1\mid f)=1/[1+\exp(Af+B)]$，
使用訓練資料的交叉驗證分數校準；測試標籤不能參與。
因此 <code>predict</code> 與 <code>predict_proba</code> 的最大機率類別可能不一致，
而 <code>decision_function</code> 分數本身也不是校準機率。</p>
<p>來源：講義 09 第 32–34 頁；
<a href="https://scikit-learn.org/1.6/modules/svm.html">scikit-learn 1.6 SVM</a>、
<a href="https://scikit-learn.org/1.6/modules/kernel_approximation.html">Kernel Approximation</a>。</p>
'''
    bodies['vslogit'] = insert_before_quiz(bodies['vslogit'],extra)
    bodies['reference'] += r'''
<h3>對偶限制與記號速查</h3>
<p>硬邊界：$\alpha_i\ge0,\ \sum_i\alpha_i y_i=0$。
軟邊界：$0\le\alpha_i\le C,\ \sum_i\alpha_i y_i=0$。
兩者預測皆用 $b+\sum_i\alpha_i y_iK(x_i,x)$；若合併 $a_i=\alpha_i y_i$，
則 $a_i$ 可以是負的。SVR 改用 $d_i=\alpha_i-\alpha_i^*$，不再乘 $y_i$。
總和 hinge 損失搭配 $\lambda\|w\|^2$ 時 $\lambda=1/(2C)$；預算 B 則需由最佳解求對應。</p>
'''


    geometry = r'''
<h3 id="w10-distance-normal">點到超平面的距離</h3>
<p>對 $w\ne0$，點 $x$ 到 $w^Tz+b=0$ 的距離為 $|w^Tx+b|/\|w\|$。
例如直線 $3z_1+4z_2-5=0$ 到原點的距離是 $5/5=1$。
若 $w=0$，就不是這裡所說的超平面，不能除以 $\|w\|$。</p>
'''
    geometry += proof('w10-proof-distance','垂直投影得到距離公式',r'''
<p>沿法向量移動到 $z=x-tw$，要求 $w^Tz+b=0$，解得
$t=(w^Tx+b)/\|w\|^2$。因此垂足與原來的點 $x$ 的距離是
$\|x-z\|=|t|\|w\|=|w^Tx+b|/\|w\|$。
對平面內任何另一點，其與垂足的差垂直於 $w$，畢氏定理保證距離不會更短。
來源：講義 09 第 6 頁的點線距離與 scalar projection 連結。</p>
''')
    bodies['prologue'] = insert_before_quiz(bodies['prologue'],geometry)
    roc = r'''
<h3 id="w10-svm-roc">用決策分數畫 ROC</h3>
<p>講義第 27、28 頁分別用 Heart 訓練集與測試集比較 ROC。
對每個門檻 $t$，以 $f(x)\ge t$ 判為正類，計算
$\mathrm{TPR}=\mathrm{TP}/(\mathrm{TP}+\mathrm{FN})$ 與
$\mathrm{FPR}=\mathrm{FP}/(\mathrm{FP}+\mathrm{TN})$。
畫 ROC 只需要排序分數，不需要先把分數變成機率；若某個評估集只有單一類別，其中一個分母為零，ROC 不適用。</p>
<p><strong>本站算例。</strong>四筆標籤是 $+1,-1,+1,-1$，對應分數 $0.8,0.5,0.2,-0.4$。</p>
'''
    roc += table(['門檻 t','FPR','TPR'],[['大於 0.8','0','0'],['0.8','0','1/2'],['0.5','1/2','1/2'],['0.2','1/2','1'],['−0.4','1','1']])
    roc += r'''
<p>按表中次序連線的梯形面積是 $\mathrm{AUC}=3/4$，也等於正負樣本四種配對中，
正類分數較大的三對所占比例。重複分數應一起跨過門檻。
模型及 C、核參數先在訓練／驗證資料決定，最後才用保留測試集評估；
不能因為測試 ROC 看起來較好就反覆選模型。此小例是自訂分數，不是 Heart 的實測數字。</p>
'''
    bodies['kernel'] = insert_before_quiz(bodies['kernel'],roc)
    approx = r'''
<h4>核近似實際計算什麼？</h4>
<p>RBF 隨機 Fourier 特徵抽取 $\omega_j\sim N(0,2\gamma I)$、
$b_j\sim U(0,2\pi)$，令 $z_j(x)=\sqrt{2/m}\cos(\omega_j^Tx+b_j)$。
於是用長度 $m$ 的 $z(x)$ 擬合線性模型，$z(x)^Tz(x')$ 近似 RBF 核。
固定亂數種子才能重現同一組近似。</p>
<p>Nyström 則選 $m$ 個代表點 $\tilde x_j$，令
$A_{ij}=K(x_i,\tilde x_j)$、$W_{jk}=K(\tilde x_j,\tilde x_k)$，
使用 $Z=AW^{\dagger/2}$ 得 $ZZ^T=AW^\dagger A^T\approx K$。
上標 $\dagger$ 表示廣義逆，只在保留的正特徵值方向取逆平方根；這也說明為何退化代表點要做數值截斷。</p>
'''
    approx += proof('w10-proof-rff','隨機 Fourier 特徵的期望等於 RBF',r'''
<p>對均勻隨機相位，$E_b[2\cos(u+b)\cos(v+b)]=\cos(u-v)$。
再對高斯 $\omega$ 取期望，利用其特徵函數得到
$E_\omega\cos(\omega^T(x-x'))=\exp[-\gamma\|x-x'\|^2]$。
對 m 個獨立特徵平均仍有同一個期望；有限 m 的一次抽樣則有近似誤差。
來源：講義 09 第 32 頁連結的 scikit-learn Kernel Approximation。</p>
''')
    bodies['vslogit'] = insert_before_quiz(bodies['vslogit'],approx)


    logistic = r"""
+<h4>兩種標籤寫法的 logistic loss</h4>
+<p>若 $z\in\{0,1\}$ 且 $p=\sigma(f)$，單筆負對數概似為
+$-z\log p-(1-z)\log(1-p)$。改記 $y=2z-1\in\{-1,+1\}$ 後，
+同一個損失就是 $\log(1+e^{-yf})$。比較 hinge 與 logistic 時，先確認標籤編碼與是否另外乘了常數。</p>
+""".replace('\n+','\n')
    logistic += proof('w10-proof-logistic-coding','0／1 與正負一標籤的損失相同',r"""
+<p>$z=1$ 時 $y=1$，$-\log\sigma(f)=\log(1+e^{-f})$。
+$z=0$ 時 $y=-1$，$-\log[1-\sigma(f)]=\log(1+e^f)$。
+兩種情形合成 $\log(1+e^{-yf})$。來源：Stanford CS229 的 logistic regression 概似定義。</p>
+""".replace('\n+','\n'))
    bodies['hinge'] = insert_before_quiz(bodies['hinge'],logistic)

    more = r'''
<h4>核 Ridge 與單類別邊界</h4>
<p>核 Ridge 使用平方損失，與 SVR 的管狀損失不同。對已中心化、此處不另設截距的模型，
最小化 $\sum_i[y_i-w^T\phi(x_i)]^2+\lambda\|w\|^2$（$\lambda&gt;0$）可取
$c=(K+\lambda I)^{-1}y$，預測 $f(x)=\sum_i c_iK(x_i,x)$。
係數通常不稀疏；要加截距時需一致地中心化訓練核及新點的核，或聯合估計截距。</p>
<p>單類別 SVM 使用未標記的正常訓練樣本，$0&lt;\nu\le1$。其問題為</p>
$$\min_{w,\rho,\xi}\frac12\|w\|^2+\frac1{\nu n}\sum_i\xi_i-\rho,
\quad w^T\phi(x_i)\ge\rho-\xi_i,\quad\xi_i\ge0.$$
<p>對偶最小化 $\alpha^TK\alpha/2$，限制是
$0\le\alpha_i\le1/(\nu n)$、$\sum_i\alpha_i=1$。
用 $f(x)=\sum_i\alpha_iK(x_i,x)-\rho$ 的正負判斷正常區域；
它給的是邊界分數，並不是積分為 1 的機率密度。
有自由乘子時，以 $\rho=\sum_j\alpha_jK(x_j,x_i)$ 回復門檻。
在常用的非退化解讀下，ν控制訓練異常比例的上界及支持向量比例的下界；尺度與污染程度仍須驗證。</p>
'''
    more += proof('w10-proof-kernel-ridge-oneclass','核 Ridge 的解與單類別對偶',r'''
<p>把 $w$ 分成訓練特徵張成空間內的部分與正交部分。正交部分不改變訓練預測，
卻增加正則項，所以可以取 $w=\sum_i c_i\phi(x_i)$。
目標變成 $\|y-Kc\|^2+\lambda c^TKc$，其導數為
$2K[(K+\lambda I)c-y]$。正文的 c 使導數為零，凸性保證是最小解。
即使 K 奇異，$K+\lambda I$ 仍正定；不同係數表示可能對應相同的 w。</p>
<p>單類別問題的 Lagrangian 對 $w,\rho,\xi_i$ 求 stationarity 分別得到
$w=\sum_i\alpha_i\phi(x_i)$、$\sum_i\alpha_i=1$、
$\alpha_i+\mu_i=1/(\nu n)$。代入留下最大化 $-\alpha^TK\alpha/2$，
等價於正文的最小化形式。自由乘子的 slack 為零，互補鬆弛給出門檻回復式。</p>
<p>來源：林軒田 Support Vector Regression 中的 Kernel Ridge Regression；
<a href="https://scikit-learn.org/1.6/modules/svm.html#density-estimation-novelty-detection">scikit-learn 單類別 SVM</a>。</p>
''')
    bodies['vslogit'] = insert_before_quiz(bodies['vslogit'],more)
