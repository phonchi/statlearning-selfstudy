"""第 9 章 kernel、multiclass、vslogit 三節整節重寫（2026-11-22，HANDOFF §32）。

正文只用講義 09、ISLP 第 9 章與課程中文 Lab；講義連結（tools/verification/ch9-svm-deepen-20261122/sources/）
與其他補充只放收合。規格見同目錄 consult/audit.md。
"""
from svm_common import (A, URL, detail, grab_details, grab_qa, grab_quiz, grab_viz, info, lab, links,
                        proof, qa_wrap, quiz, table)


# ───────────────────────────── kernel ─────────────────────────────

def _kernel(old):
    b = old["kernel"]
    kern_viz = grab_viz(b, "w10kernSvg")
    kern_lab = grab_details(b, "w10-detail-kernel-lab")
    rbf_viz = grab_viz(b, "w10rbfSvg")
    proof_poly = grab_details(b, "w10-proof-polynomial")
    proof_kern = grab_details(b, "w10-proof-kernels")
    roc = grab_details(b, "w10-detail-score-roc")
    qa_lift = grab_qa(b, "Q：核技巧「不用真的升維」")

    validity = detail("w10-detail-kernel-validity", "深入核函數：Gram 矩陣、記號與維度", r'''
<h3 id="w10-kernel-validity">可用的核與完整 Gram 矩陣</h3>
<p>核不能只是任意相似度。作為內積核，$K(x,z)=\langle\phi(x),\phi(z)\rangle$，
任意有限資料的 Gram 矩陣 $K$ 必須對稱且<strong>半正定</strong>：
$c^TKc\ge0$ 對所有向量 $c$ 成立。講義說估計時需要所有訓練點兩兩之間的內積；
實際求解還會用到對角項 $K(x_i,x_i)$，所以完整的 Gram 矩陣是 $n\times n$。</p>
<p>以 $\hat\alpha_i\ge0$ 表示 Lagrange 乘子時，完整預測式為</p>
$$f(x)=\beta_0+\sum_{i\in S}\hat\alpha_i y_iK(x,x_i).$$
<p>ISLP 把 $a_i=\alpha_i y_i$ 合併成帶正負號的係數，寫成
$\beta_0+\sum_i a_iK(x,x_i)$。兩種記號都可用，但不可把 $a_i$ 再當成非負乘子。
二元 <code>SVC.dual_coef_</code> 儲存的是帶標籤的係數 $y_i\hat\alpha_i$；多類別的排列另外遵循成對分類器規則。</p>
''' + proof_kern + r'''
<h3>次數、維度與核矩陣如何對回講義？</h3>
<p>兩個變數的三次多項式展開有九個非截距項：一階兩個、二階三個、三階四個。
一般來說，$p$ 個變數做到 $d$ 次（含所有低次項、不含常數）共有 $\binom{p+d}{d}-1$ 個特徵；
CS229 講義把含常數的 $(x^Tz+c)^d$ 對應到 $\binom{p+d}{d}$ 維的特徵空間，差的那一維就是常數項。
$p=100$、$d=3$ 時已有 176,850 個特徵，但核值 $(1+x^Tz)^3$ 仍只需要一次 $p$ 維內積。</p>
<p>$d$ 次核中的 $d$ 是多項式次數，不是特徵空間只有 $d$ 維。含常數的 $(1+x^Tu)^d$ 與齊次的 $(x^Tu)^d$ 也不是同一個核：前者包含低階項。
講義的二次映射與 Lab 的 <code>my_kernel_1</code> 都是齊次二次核。sklearn 內建多項式核為 $(\gamma x^Tu+\mathrm{coef0})^d$；若沒有核對 <code>gamma</code> 與 <code>coef0</code>，不能直接聲稱它與自訂核完全相同。</p>
<p>核函數傳入兩個資料矩陣 $X$ 與 $Y$，回傳的矩陣形狀必須是「X 的樣本數 × Y 的樣本數」。訓練時計算 train–train，預測時計算 test–train；不能對測試資料改算成 test–test。核技巧省掉顯式的高維特徵，但沒有消除樣本數平方級矩陣可能帶來的負擔。</p>
''' + links([(URL["bourret"], "Bourret：核映射的展開"), (URL["cs229"], "Stanford CS229：Kernels"),
             (URL["sksvm"] + "#kernel-functions", "scikit-learn 1.6 核函數介面")]))

    mercer = detail("w10-detail-mercer", "Mercer 定理在說什麼？", r'''
<p>講義在 RBF 核旁邊提到 Mercer 定理。這個定理回答的問題是：
<strong>什麼樣的函數 $K$，真的等於某個特徵空間裡的內積 $\Phi(x)^T\Phi(z)$？</strong>
只有這種 $K$ 才能放心代進 SVM 的對偶問題。</p>
<h3>有限樣本的版本（CS229、林軒田的寫法）</h3>
<p>$K:\mathbb R^p\times\mathbb R^p\to\mathbb R$ 是合法核的充分必要條件是：
對<strong>任何</strong>有限個點 $x^{(1)},\dots,x^{(m)}$，核矩陣 $[K(x^{(i)},x^{(j)})]$ 都對稱且半正定。
必要性一行就證得出來：若 $K_{ij}=\Phi(x^{(i)})^T\Phi(x^{(j)})$，則
$c^TKc=\|\sum_i c_i\Phi(x^{(i)})\|^2\ge0$。CS229 說明，輸入在 $\mathbb R^p$ 時這個版本與教科書的函數版本等價。</p>
<p>反例（林軒田講義的小題）：$K(x,x')=(-1+xx')^2$ 在一維的兩點 $x_1=1$、$x_2=-1$ 上，
核矩陣是 $\begin{pmatrix}0&amp; 4\\4&amp; 0\end{pmatrix}$，特徵值有 $-4$，不是半正定，所以它不是合法的核。</p>
<h3>連續函數的版本（Wikipedia 的寫法）</h3>
<p>在緊緻區間 $[a,b]$ 上，若 $K$ 連續、對稱、半正定，則存在非負的 $\lambda_j$ 與一組正交基底函數 $e_j$，使</p>
$$K(s,t)=\sum_{j=1}^{\infty}\lambda_j\,e_j(s)\,e_j(t),$$
<p>而且級數絕對且一致收斂。把它讀成內積，就得到特徵映射
$\Phi(x)=\big(\sqrt{\lambda_1}e_1(x),\sqrt{\lambda_2}e_2(x),\dots\big)$；
若非零的 $\lambda_j$ 有無窮多個，這個特徵空間就是無窮維。拿掉連續性後，就不能再保證一致收斂（適當條件下仍有平方可積意義下的收斂）。</p>
<h3>講義說「確切的 Φ 難以處理」是什麼意思？</h3>
<p>Mercer 定理只保證這樣的展開<strong>存在</strong>，並沒有給一套好算的 $e_j$。
SVM 也不需要它：訓練與預測只用到核值 $K(x_i,x_j)$，所以只要確認 $K$ 合法，就能在看不見的特徵空間裡做線性分類。
RBF 核另有一組可以直接寫出的無窮多個座標（上一個收合的泰勒展開），但同樣不可能逐一算完。</p>
''' + links([(URL["mercer"], "Wikipedia：Mercer's theorem"), (URL["cs229"], "Stanford CS229：Kernels（Mercer 定理）"),
             (URL["htlin"], "林軒田：Kernel SVM 講義（課程首頁）")]))

    gamma = detail("w10-detail-gamma", "γ 越大代表什麼？用頻寬來想", r'''
<p>RBF 核也常寫成 $\exp\!\big(-\|x-x'\|^2/(2\sigma^2)\big)$，對照可知 $\gamma=1/(2\sigma^2)$：
$\gamma$ 大就是頻寬 $\sigma$ 小。scikit-learn 文件的說法是，$\gamma$ 決定單一訓練點的影響範圍，
$\gamma$ 越大，其他點必須離它越近才會受它影響。</p>
<p>所以 $\gamma$ 大時，每個支持向量周圍是一個很尖的高斯山丘，決策邊界可以繞著個別訓練點彎折，
林軒田的講義用 $\gamma=1,10,100$ 三張圖示範：$\gamma$ 越大越容易過度擬合。
極端情形 $\gamma\to\infty$ 時，$K(x,x')$ 只在 $x=x'$ 時等於 1，其餘趨近 0，模型幾乎只會記住訓練點。
這就是講義那句「過度擬合時把 γ 調小」的由來。$\gamma$ 與 $C$ 都在控制彈性，Lab 用網格搜尋一起選。</p>
''' + links([(URL["sksvm"] + "#parameters-of-the-rbf-kernel", "scikit-learn 1.6：RBF 核的參數"),
             (URL["htlin"], "林軒田：Kernel SVM 講義（課程首頁）"), (URL["so_rbf"], "Stack Overflow：RBF 為何是無窮維")]))

    q_kern = quiz("qKern2", "QUIZ · 核與 γ",
                  "RBF 核 SVM 在訓練資料上幾乎全對，測試資料卻明顯變差。依講義的建議，γ 應該怎麼調？",
                  [(True, "把 γ 調小，讓每個支持向量的影響範圍變大、邊界變平滑",
                    "對。講義說 γ 也是正則化參數，過度擬合時應該調小。γ 小表示核值隨距離衰減得慢，邊界不會繞著個別訓練點打轉；實際數值仍要和 C 一起用交叉驗證選。"),
                   (False, "把 γ 調大，讓模型更專注在每個點附近",
                    "方向反了。γ 大時核值隨距離衰減得很快，每個支持向量只影響身邊一小塊，邊界更破碎，這正是過度擬合的來源。"),
                   (False, "γ 不影響彈性，應該改用更高次的多項式核",
                    "γ 本身就控制 RBF 的彈性。換成高次多項式核通常讓模型更有彈性，對過度擬合沒有幫助；講義也提醒高次多項式核有數值上的困難。")])

    kernel_table = table(["核", "優點", "缺點", "講義的建議"], [
        ["線性核", "安全、快；可直接看 $w$ 與支持向量解讀", "受限制，資料不一定線性可分", "基本工具，先試它"],
        ["多項式核", "比線性核有彈性；次數有明確的意義", "次數大時有數值困難", "大概只用小次數"],
        ["高斯（RBF）核", "比前兩者更有彈性；值有界，數值上比多項式核穩定；只有一個參數要選",
         "神祕（沒有 $w$ 可看）、比線性核慢、容易過度擬合", "很常用，但要小心使用"],
    ])

    body = r'''
  <p>軟邊界允許違反間隔，但邊界仍是一條直線（超平面）。講義那張圖是一類點集中在中間、另一類分在左下與右上兩端。
  軟邊界可以容忍違反，得到的卻還是一條直線，把兩類切得亂七八糟。
  ISLP 對這種資料的結論是：支持向量分類器或任何線性分類器都會表現很差。
  講義的說法是線性邊界「找不到合適的解」：問題不在算不算得出來，而在<strong>線性邊界本身就不合適</strong>
  （預算夠大時問題一定可行，細節見軟邊界一節的推導收合）。</p>

  <p>第 7 章遇過一模一樣的問題，答案是<strong>特徵擴張</strong>（feature expansion）：
  把 $X_1^2, X_2^2, X_1X_2, X_1^3, \dots$ 加進特徵裡，在放大的空間擬合支持向量分類器，
  映射回原空間就變成彎的邊界。講義的例子是用 $(X_1, X_2, X_1^2, X_2^2, X_1X_2)$ 取代 $(X_1, X_2)$，邊界變成</p>

  $$\beta_0 + \beta_1 X_1 + \beta_2 X_2 + \beta_3 X_1^2 + \beta_4 X_2^2
    + \beta_5 X_1 X_2 = 0$$

  <p>這在放大的空間裡是<strong>線性</strong>的，在原空間裡是二次曲線（圓、橢圓、雙曲線這類圓錐曲線）。
  講義接著做到三次多項式：兩個變數就變成九個特徵。
  講義的提醒是，多項式（尤其變數多的時候）很快就失控；
  用<strong>核</strong>引入非線性，是更優雅、也更好控制的做法。</p>

  <p>核的主要想法寫成一行：</p>

  $$x \;\longrightarrow\; \Phi(x)=\big(\varphi_1(x),\varphi_2(x),\varphi_3(x),\dots\big),
    \qquad \Phi(x)^T\Phi(u) = K(x,u)$$

  <p>$K$ 叫做<strong>核</strong>（kernel），是衡量兩筆觀測值有多像的函數。
  <strong>核技巧</strong>（kernel trick）是說：我們不需要真的知道 $\Phi(x)$，
  只要在原空間用核函數計算就好。這之所以行得通，是因為下面這件事。</p>

<div class="info-box">
  <span class="info-label">關鍵事實：解與預測只用得到內積</span>
  兩筆觀測值的內積是 $\langle x_i, x_{i'} \rangle = \sum_{j=1}^{p} x_{ij} x_{i'j}$。
  線性的支持向量分類器可以寫成
  $$f(x) = \beta_0 + \sum_{i=1}^{n} \hat\alpha_i y_i \langle x, x_i \rangle .$$
  要估計 $\alpha_1,\dots,\alpha_n$ 與 $\beta_0$，只需要<strong>所有訓練點兩兩之間的內積</strong>，用不到觀測值本身。<br>
  而且大部分的 $\hat\alpha_i$ 都是 0，只有支持向量例外。令 $S$ 是 $\hat\alpha_i&gt;0$ 的那些 $i$（支持集合），
  $$f(x) = \beta_0 + \sum_{i\in S} \hat\alpha_i y_i \langle x, x_i \rangle ,$$
  和式的項數通常遠少於 $n$。
</div>

  <p>講義用一個二次映射把「換掉內積」說得很具體。取</p>

  $$\Phi(x) = \begin{pmatrix}\sqrt{2}\,x_1 x_2\\ x_1^2\\ x_2^2\end{pmatrix},
    \qquad
    \Phi(a)^T\Phi(b) = 2a_1a_2b_1b_2 + a_1^2b_1^2 + a_2^2b_2^2 = (a_1b_1+a_2b_2)^2 = (a^Tb)^2 .$$

  <p>左邊要先把兩個點搬到三維再做內積；右邊只要在原來的二維算內積再平方。
  兩邊數值完全相同，所以「在三維空間擬合線性分類器」可以全程留在二維完成。
  Lab 的 <code>feature_map_1</code> 與 <code>my_kernel_1</code> 就是這個例子。</p>
''' + proof_poly + kern_viz + kern_lab + r'''
  <p>只要算得出觀測值之間的內積，就能擬合支持向量分類器。<strong>支持向量機</strong>（SVM）
  就是把內積換成核的支持向量分類器；反過來說，支持向量分類器就是使用<strong>線性核</strong>的 SVM：</p>

  $$K(x_i, x_{i'}) = \sum_{j=1}^{p} x_{ij} x_{i'j}$$

  <p>其他特別的核也很有用。<strong>d 次多項式核</strong>（ISLP 式 9.22）加上常數 1，
  所以展開後同時保留常數、變數本身與各階交互項，算的正是 d 次多項式空間裡的內積：</p>

  $$K(x_i, x_{i'}) = \left(1 + \sum_{j=1}^{p} x_{ij} x_{i'j}\right)^{d}$$

  <p>此時解的形式變成</p>

  $$f(x) = \beta_0 + \sum_{i\in S} \hat\alpha_i y_i K(x, x_i).$$

  <p><strong>徑向基核</strong>（radial basis kernel，RBF；ISLP 式 9.24）依兩點間的平方距離定義：</p>

  $$K(x_i, x_{i'}) = \exp\left(-\gamma \sum_{j=1}^{p}
    \left(x_{ij} - x_{i'j}\right)^2\right), \qquad \gamma > 0$$

  <p>RBF 的行為非常<strong>局部</strong>：如果測試點 $x^*$ 離訓練點 $x_i$ 很遠，
  平方距離很大、指數很小、$K(x^*, x_i)$ 幾乎是 0，於是 $x_i$ 在 $f(x^*)$ 裡幾乎沒有發言權。
  <strong>只有附近的訓練點會影響一個測試點的預測。</strong>講義的說法是：RBF 把大多數方向上的影響壓得很小，藉此控制變異。
  兩個重點也出自講義：</p>
  <ul>
    <li><strong>$\gamma$ 也是一個正則化參數</strong>：$\gamma$ 決定「附近」有多近。過度擬合時應該把 $\gamma$ 調小。</li>
    <li><strong>特徵空間是隱含的，而且是無窮維</strong>：講義引 Mercer 定理說明，確切的 $\Phi$ 難以處理。
    ISLP 也說，對 RBF 核我們本來就不可能在那個空間裡做計算，只能透過核值間接使用它。</li>
  </ul>
''' + validity + mercer + gamma + rbf_viz + q_kern + r'''
  <p>三種核各有取捨。講義附錄把它們的優缺點整理如下：</p>
''' + kernel_table + r'''
  <p>講義用 Heart 資料示範怎麼比較：把分類門檻從 0 改成 $t$，以 $\hat f(X)\ge t$ 判為有心臟病，
  讓 $t$ 變動並記錄偽陽性率與真陽性率，就得到 ROC 曲線。ISLP 的結果很值得記住：
  在訓練資料上，$\gamma=10^{-1}$ 的 RBF SVM 幾乎是完美的 ROC 曲線；
  換到 90 筆測試資料，它卻是所有模型裡最差的，$\gamma=10^{-2}$、$10^{-3}$ 則與支持向量分類器差不多。
  彈性越大，訓練誤差越低，但不保證測試表現變好。</p>
''' + roc + qa_wrap("觀念釐清", [qa_lift])
    return body


# ───────────────────────────── multiclass ─────────────────────────────

def _multiclass(old):
    b = old["multiclass"]
    q_multi = grab_quiz(b, "qMulti").replace("不過分類器多不等於慢：OVO 的每個問題只用兩類的資料，所以總計算量常常還是比 OVA 少。", "")
    khan = grab_details(b, "w10-detail-khan-lab")
    old_tbl = grab_details(b, "w10-detail-multiclass-table")
    # 只沿用兩張表格；說明文字重寫，不再提到已移除的元件。
    tables = old_tbl[old_tbl.index('<div style="overflow-x:auto;">'):old_tbl.index('<div class="info-box warm">')]
    # 「K 很大時考慮 OVA」沒有來源（講義與 ISLP 只說 K 不太大時用 OVO），整列刪除。
    row = "<tr><td>ISLP 的建議</td><td><strong>K 不太大就用這個</strong></td><td>K 很大時考慮</td></tr>"
    if tables.count(row) != 1:
        raise ValueError("多類別表格的建議列已改變")
    tables = tables.replace(row, "")

    mtable = detail("w10-detail-multiclass-table", "OVO／OVA 完整比較與 SVC 的介面", tables + r'''
<p>OVO 的每個分類器只用兩類的資料，問題比較小；兩類是否平衡、能否分開，仍取決於資料。
OVA 的每個分類器要面對把好幾類混在一起的「其餘」，正負兩邊的樣本數通常差很多，
那一團的形狀也可能無法用一個超平面分開。OVO 投票可能平手，實作時要明訂平手的處理規則；
OVO 與 OVA 也可能給出不同答案，差異多大取決於資料、分類器與調整參數。</p>
<div class="info-box warm">
  <span class="info-label">decision_function_shape 不改變訓練方式</span>
  scikit-learn 的 <code>SVC</code> 與 <code>NuSVC</code> 一律用 OVO 訓練 $K(K-1)/2$ 個分類器。
  <code>decision_function_shape</code> 只決定 <code>decision_function()</code> 輸出的形狀：
  設成 <code>'ovr'</code>（預設）時，是把 OVO 的結果單調地換算成 $K$ 個分數。
  Lab 的說明把 <code>'ovo'</code>／<code>'ovr'</code> 講成兩種訓練策略，讀程式時要依估計器的實際行為區分。
  真的想要「訓練 $K$ 個一對其餘分類器」，要用 <code>OneVsRestClassifier(SVC(...))</code> 包起來；
  <code>LinearSVC</code> 則本來就是一對其餘。
</div>
''' + lab("原 Lab：三類資料的 RBF SVM", 84) + links([(URL["sksvm"] + "#multi-class-classification",
                                                     "scikit-learn 1.6：SVC 的多類別訓練與輸出")]))

    return r'''
  <p>到這裡整章都在講兩類。K &gt; 2 怎麼辦？ISLP §9.4 的說明是：
  <strong>分離超平面這個概念本身沒辦法自然地推廣到多類別</strong>。
  提過的做法很多，最常見的兩個都是「把多類別問題拆成一堆兩類問題」。</p>

  <p><strong>一對一</strong>（one-versus-one，OVO，也叫 all-pairs）：擬合
  $\binom{K}{2} = K(K-1)/2$ 個分類器，每個只比較<strong>兩個</strong>類別
  （第 k 類編成 +1、第 k′ 類編成 −1）。
  測試點交給每一個分類器投一票，<strong>得票最多的類別勝出</strong>。</p>

  <p><strong>一對其餘</strong>（one-versus-all，OVA，也叫 one-versus-rest、OVR）：擬合 K 個分類器，
  第 k 個把第 k 類編成 +1、<strong>其餘 K − 1 類全部</strong>編成 −1。
  測試點指派給 $f_k(x^*) = \beta_{0k} + \beta_{1k}x_1^* + \cdots + \beta_{pk}x_p^*$
  <strong>最大</strong>的那一類，因為那代表最有信心屬於第 k 類。</p>

<div class="info-box">
  <span class="info-label">兩者怎麼選</span>
  分類器的個數：OVO 是 K(K−1)/2，OVA 是 K。K = 3 時兩者都是 3；K = 10 時是 <strong>45 對 10</strong>。<br>
  講義的建議：<strong>K 不太大就用 OVO</strong>。
</div>
''' + mtable + q_multi + r'''
  <p>Lab 最後用 Khan 基因表現資料示範多類別：四種小圓藍細胞腫瘤，每個樣本有 2,308 個基因的測量值，
  訓練集 63 筆、測試集 20 筆。變數遠多於樣本，ISLP 因此建議用線性核，因為多項式或 RBF 核多出來的彈性用不到。
  結果訓練資料沒有任何錯分，這並不意外：變數這麼多，很容易找到完全分開各類的超平面。
  真正要看的是測試資料，<code>C=10</code> 時有兩筆分錯。</p>
''' + khan


# ───────────────────────────── vslogit ─────────────────────────────

def _vslogit(old):
    b = old["vslogit"]
    vs_lab = grab_details(b, "w10-detail-vslogit-lab")
    proof_svr = grab_details(b, "w10-proof-svr")
    proof_rff = grab_details(b, "w10-proof-rff")
    oneclass = grab_details(b, "w10-detail-kernel-extensions")

    cmp_table = table(["", "支持向量分類器／SVM", "邏輯斯迴歸（加 ridge 懲罰）"], [
        ["損失函數", "hinge：$\\max(0,\\,1 - y f)$", "$\\log(1 + e^{-y f})$"],
        ["在 $y f \\ge 1$ 時的損失", "<strong>恰好 0</strong>", "很小，但不是 0"],
        ["解由誰決定", "<strong>只有支持向量</strong>", "全部資料（離邊界遠的點影響很小）"],
        ["機率輸出", "不直接提供", "<strong>直接就有</strong>"],
        ["類別（幾乎）分得開時", "講義：<strong>常表現較好</strong>（LDA 也是）", "與適當正則化的邏輯斯迴歸相比，優劣要驗證（原因見下方收合）"],
        ["類別重疊很多時", "與邏輯斯迴歸非常相似", "常被優先採用"],
        ["非線性邊界", "<strong>核 SVM 很普及</strong>", "也能用核，但計算較貴"],
    ])

    comparison = detail("w10-detail-model-comparison", "對照表背後的幾件事", r'''
<p><strong>為什麼可分資料對邏輯斯迴歸不利？</strong>資料完全可分時，把係數整組放大，
每一筆的 $\log(1+e^{-y_if(x_i)})$ 都會繼續變小，最大概似估計不存在，係數會一路往無窮大走。
這個問題只出在<strong>未加懲罰</strong>的邏輯斯迴歸；加上 ridge 懲罰後解就存在。所以講義「可分時 SVC 比 LR 好」是傾向，和適當正則化的邏輯斯迴歸比誰好，仍要用驗證資料判斷。細節見 hinge loss 一節的收合「SVM 比較像加 L2 懲罰的邏輯斯迴歸，還是原本的邏輯斯迴歸？」。</p>
<p><strong>LDA 呢？</strong>LDA 估的是每一類的平均與共同共變異矩陣，規則由全部資料決定，
同樣直接給出類別機率。講義把它與支持向量分類器並列為「類別幾乎可分時表現好」的方法。</p>
<p><strong>$p\gg n$ 時</strong>：scikit-learn 文件把這列為 SVM 的注意事項，特徵數遠大於樣本數時，
要小心選核，正則化也特別重要。Khan 資料就是這種情形。</p>
<p><strong>計算量</strong>：libsvm 的二次規劃求解器，計算量大約介於 $O(p\,n^2)$ 與 $O(p\,n^3)$ 之間，
計算與儲存需求都隨訓練樣本數快速增加；liblinear 版的 <code>LinearSVC</code> 則幾乎能隨樣本數線性擴充到百萬筆。
樣本數上萬時，常改用 <code>LinearSVC</code>、<code>SGDClassifier</code> 或核近似。</p>
''' + links([(URL["sksvm"] + "#complexity", "scikit-learn 1.6：SVM 的計算複雜度"),
             (URL["htlin"], "林軒田：Kernel Logistic Regression 講義（課程首頁）")]))

    kernel_beyond = detail("w10-detail-kernel-beyond", "核技巧不只用在 SVM：normal equation、邏輯斯迴歸與 PCA", r'''
<p>任何只透過內積 $x_i^Tx_j$ 接觸資料的方法，都可以把內積換成核。林軒田的講義把這件事寫成
<strong>表示定理</strong>（representer theorem）：對任何加了 L2 懲罰的線性模型，
最佳係數一定可以寫成訓練資料的線性組合 $\beta=\sum_i c_i x_i$。
證明的想法是把 $\beta$ 拆成落在 $\{x_i\}$ 張成空間的部分與垂直的部分；
垂直部分不改變任何 $x_i^T\beta$，只會讓懲罰變大，所以最佳解裡它是 0。</p>

<h3>線性迴歸的 normal equation：核嶺迴歸</h3>
<p>嶺迴歸的 normal equation 解可以換個寫法（$X$ 是 $n\times p$；為了讓式子乾淨，這裡用不含截距、也不先置中的模型）：</p>
$$\hat\beta=(X^TX+\lambda I_p)^{-1}X^Ty=X^T(XX^T+\lambda I_n)^{-1}y .$$
<p>等號成立是因為 $(X^TX+\lambda I_p)X^T=X^T(XX^T+\lambda I_n)$，兩邊各乘上對應的反矩陣即得。
右邊只用到 $n\times n$ 的 $XX^T$，它的每個元素都是內積。預測一個新點 $x_*$：</p>
$$\hat y_*=x_*^T\hat\beta=k_*^T(K+\lambda I)^{-1}y,\qquad K=XX^T,\quad k_*=Xx_* .$$
<p>把 $K$ 與 $k_*$ 換成核值，就是<strong>核嶺迴歸</strong>（kernel ridge regression）：
係數 $c=(\lambda I+K)^{-1}y$，預測 $\sum_i c_iK(x_i,x_*)$。
$K$ 半正定，所以 $\lambda&gt;0$ 時 $\lambda I+K$ 一定可逆。代價是訓練要解 $n\times n$ 的線性系統（直接求反矩陣約 $O(n^3)$），
預測要算 $n$ 個核值；線性嶺迴歸則是 $O(p)$ 預測。</p>
<p>如果 $\lambda=0$（普通最小平方），右邊的寫法需要 $XX^T$ 可逆，也就是 $p\ge n$ 且各筆資料線性獨立；
這時 $X^T(XX^T)^{-1}y$ 是讓訓練資料完全被擬合的解中長度最短的那一個。
$p&lt;n$ 時 $XX^T$ 一定奇異；資料若先做欄置中，$XX^T\mathbf 1=0$，不論 $p$ 多大都奇異。這些情形要改用虛反矩陣，
而 $\lambda&gt;0$ 則保證 $\lambda I+K$ 可逆，這是核嶺迴歸保留 $\lambda$ 的理由之一。
模型要含不受懲罰的截距時，不能只把置中後的 $X$ 換成核值：要在特徵空間把訓練與測試的核值都置中，預測時再加回 $\bar y$，細節超出本頁。
CS229 講義則示範另一條路：用梯度下降做最小平方，係數從 0 出發，之後始終可以寫成 $\sum_i c_i\phi(x_i)$，
更新式 $c\leftarrow c+\eta\,(y-Kc)$ 也只用到核矩陣。</p>

<h3>邏輯斯迴歸：核邏輯斯迴歸</h3>
<p>套用表示定理，加 L2 懲罰的邏輯斯迴歸變成對 $c$ 的問題</p>
$$\min_{c}\ \frac{\lambda}{n}\,c^TKc+\frac1n\sum_{i=1}^{n}\log\!\Big(1+\exp\big(-y_i\textstyle\sum_{j}c_jK(x_j,x_i)\big)\Big),$$
<p>可以用梯度下降求解。差別在於它的 $c_i$ <strong>通常全部不是 0</strong>，
不像 SVM 只有支持向量的 $\alpha_i$ 非零；預測一個點就要算 $n$ 個核值。
這是核邏輯斯迴歸計算較貴的原因之一。</p>

<h3>PCA：用 $XX^T$ 也算得出來</h3>
<p>這一段是本頁補的推導，講義連結沒有直接寫出。先把 $X$ 的每一欄置中。第 12 章的主成分是 $X^TX$（$p\times p$）的特徵向量；
$XX^T$（$n\times n$）與它有相同的非零特徵值。若 $XX^Tu=\mu u$、$\|u\|=1$，則</p>
$$v=\frac{X^Tu}{\sqrt{\mu}}$$
<p>是單位長度的載荷向量，而且 $X^TXv=\mu v$；主成分得分是 $Xv=\sqrt{\mu}\,u$。
所以 $p\gg n$ 時，可以改解小的 $n\times n$ 問題，這叫 dual PCA。
因為只用到內積，把 $XX^T$ 換成核矩陣就是核主成分分析（kernel PCA）。
這時置中要在特徵空間做：令 $H=I-\tfrac1n\mathbf 1\mathbf 1^T$，改用 $HKH$。</p>
''' + links([(URL["h206"], "林軒田：Support Vector Regression（含核嶺迴歸）"),
             (URL["htlin"], "林軒田：Kernel Logistic Regression 講義（課程首頁）"),
             (URL["cs229main"], "Stanford CS229 第 5 章：Kernel Methods"),
             (URL["kapprox"], "scikit-learn 1.6：核近似（提到 kernelized PCA）"),
             ("unsupervised_learning.html#pca", "第 12 章：主成分")]))

    svr = detail("w10-detail-svr", "延伸：SVR 的管狀損失與完整對偶", r'''<h3 id="w10-svr-complete">支持向量迴歸的管狀損失</h3>
<p><code>SVC</code> 是分類器，不能直接拿來做迴歸；迴歸要用支持向量迴歸，scikit-learn 對應的估計器是
<code>SVR</code>（以及 <code>NuSVR</code>、<code>LinearSVR</code>）。
迴歸的 $y_i$ 是實數，$\varepsilon\ge0$ 是可接受的絕對誤差。損失為</p>
$$[\,|y_i-f(x_i)|-\varepsilon\,]_+ ,$$
<p>也叫 ε-不敏感損失（ε-insensitive loss）。誤差落在寬 $2\varepsilon$ 的「管子」裡就不計損失，
超出時按超出的距離計算。林軒田的講義拿它和平方損失比較：殘差小時兩者的損失都小，殘差大時它只線性增加，受離群值的影響較小。兩者形狀並不相同，管內的損失恰好是 0。
$\varepsilon$ 控制管寬，$C$ 控制超出管子的懲罰：</p>
$$\begin{aligned}
\min_{w,b,\xi,\xi^*}\quad&amp; \frac12\|w\|^2+C\sum_i(\xi_i+\xi_i^*)\\
\text{使得}\quad&amp; y_i-w^T\phi(x_i)-b\le\varepsilon+\xi_i,\\
&amp; w^T\phi(x_i)+b-y_i\le\varepsilon+\xi_i^*,\quad\xi_i,\xi_i^*\ge0.
\end{aligned}$$
<p>令 $d_i=\alpha_i-\alpha_i^*$，其對偶與預測式為</p>
$$\max_{\alpha,\alpha^*}\ -\frac12\sum_{i,j}d_id_jK_{ij}
-\varepsilon\sum_i(\alpha_i+\alpha_i^*)+\sum_i y_i d_i,
\quad0\le\alpha_i,\alpha_i^*\le C,\quad\sum_i d_i=0,$$
$$f(x)=b+\sum_i d_iK(x_i,x).$$
<p>這裡係數不乘分類標籤 $y_i$。<strong>嚴格在管內的點兩個乘子都是 0</strong>，所以解和分類一樣是稀疏的；
在管子邊上或管外的點才是支持向量。
有 $0\lt\alpha_i\lt C$ 時用 $b=y_i-\varepsilon-\sum_jd_jK(x_j,x_i)$；
有 $0\lt\alpha_i^*\lt C$ 時用 $b=y_i+\varepsilon-\sum_jd_jK(x_j,x_i)$。
沒有這類點時也要從 KKT 不等式決定截距區間。</p>
''' + proof_svr + links([(URL["h206"], "林軒田：Support Vector Regression"),
                         (URL["sksvm"] + "#regression", "scikit-learn 1.6：SVR")]))

    solvers = detail("w10-detail-solvers", "大規模求解、機率估計與核近似", r'''<h3 id="w10-solvers">從公式選擇實作</h3>
<p><code>SVC(kernel='linear')</code> 與 <code>LinearSVC</code> 都可給線性邊界，
但後者預設使用 squared hinge，且 liblinear 會連截距一起正則化，不能期待相同 C 一定得同一解。
<code>NuSVC</code> 改以 $\nu$ 控制另一種限制，是 C 版本的重新參數化，不是把參數 C 改名。
對二元訓練資料，在其可行設定下 $\nu$ 給訓練 margin error 比例的上界與支持向量比例的下界；
類別不平衡會限制可行的 $\nu$。</p>
<h3>機率估計：Platt scaling</h3>
<p>講義說 SVM 也可以估計機率。做法是在 SVM 的分數 $f$ 之上，另外擬合一個邏輯斯模型
$P(Y=1\mid f)=1/[1+\exp(Af+B)]$，$A,B$ 用訓練資料上的額外交叉驗證估計，測試標籤不能參與。
scikit-learn 文件提醒三件事：這個交叉驗證在大資料上很貴；Platt 的方法本身有理論上的問題；
<code>predict</code> 與 <code>predict_proba</code> 的結果可能不一致。只需要排序或信心分數時，
直接用 <code>decision_function</code> 即可，它本身不是校準過的機率。</p>
<h3>核近似實際計算什麼？</h3>
<p>核近似把輸入變成有限個特徵，再交給線性模型。<code>RBFSampler</code>（Random Kitchen Sinks）
抽取 $\omega_j\sim N(0,2\gamma I)$、$b_j\sim U(0,2\pi)$，令 $z_j(x)=\sqrt{2/m}\cos(\omega_j^Tx+b_j)$；
用長度 $m$ 的 $z(x)$ 擬合線性模型，$z(x)^Tz(x')$ 近似 RBF 核。
特徵近似、標準化與後續模型都放在訓練折內；近似維度越大通常成本越高，精度需由驗證資料評估。</p>
''' + proof_rff + r'''
<h3>核近似為什麼可以接上 SGD？</h3>
<p>原 Lab 以 <code>RBFSampler</code> 產生有限個隨機特徵，再以線性的 <code>SGDClassifier(loss="hinge")</code> 擬合。此時真正儲存的是有限長度的特徵與線性係數，並不需要保留完整的訓練核矩陣。近似特徵數增加可改善核近似，但同時增加時間與記憶體；近似好壞仍不是測試誤差的保證。</p>
<p>SGD 每次用一筆或小批資料估計更新方向。hinge 在 $yf\lt1$ 時，對 $w$ 的次梯度包含 $-yx$；在 $yf>1$ 時，這筆資料的 hinge 梯度為零，但正則化仍可縮小係數。特徵尺度、步長與迭代次數都影響是否充分收斂。這是在近似後的特徵空間解線性問題，得到的是近似核模型，與精確的 RBF SVC 有別。</p>
<p>線性 SVC、LinearSVC 與 SGDClassifier 的預設損失、截距處理及求解策略不同。比較時先對齊目標再比較泛化；不能以「三個都畫直線」推成三者必定得到一樣答案。</p>
''' + links([(URL["sksvm"], "scikit-learn 1.6：SVM"), (URL["sgd"], "scikit-learn 1.6：SGD"),
             (URL["kapprox"], "scikit-learn 1.6：核近似")]))

    qa_choose = r'''<details class="qa-item"><summary>Q：SVM 與邏輯斯迴歸該選哪一個？</summary>
    <div class="qa-a"><p><strong>需要類別機率時，選邏輯斯迴歸。</strong>講義把「不直接提供機率」列為 SVM 的缺點，
    也說想估機率時 LR 是首選。ROC 或排序門檻只需要分數，SVM 的 <code>decision_function</code> 就夠用。</p>
    <p>不要機率的話，看類別分得多開。ISLP 的說法是：<strong>類別分得很開時，SVM 通常表現較好；重疊較多時，常偏好邏輯斯迴歸。</strong>
    重疊的中間地帶兩者結果會很像，因為損失函數很像。</p>
    <p>另外兩個實務考量。<strong>樣本很多</strong>：講義建議大規模問題改用 <code>SGDClassifier</code> 搭配 hinge loss，
    非線性時可先做核近似。<strong>要看變數的作用</strong>：線性核有 $w$ 可以看，RBF 核沒有，講義附錄把這列為高斯核的缺點：「神祕」。</p></div>
  </details>'''
    qa_why = r'''<details class="qa-item"><summary>Q：為什麼核方法特別常用於 SVM？</summary>
    <div class="qa-a"><p>ISLP 的回答很直接：<strong>歷史原因</strong>。邏輯斯迴歸與本書許多分類方法也都能用非線性核，
    但核在 SVM 的脈絡裡遠比其他地方普及。</p>
    <p>也有計算上的理由。SVM 的解是<strong>稀疏</strong>的：只有支持向量的 $\hat\alpha_i$ 非零，預測時只要算 $|S|$ 個核值。
    核邏輯斯迴歸的係數通常全部非零，預測一個點要算 $n$ 個核值（推導見上面的收合）。
    hinge loss 在 $y f\ge1$ 時剛好等於 0，換來的正是這種稀疏性。</p></div>
  </details>'''

    q_vs = quiz("qVs", "QUIZ · SVM vs 邏輯斯迴歸",
                "一份資料的兩個類別重疊得相當厲害，而且你需要輸出每一筆的違約機率。該選哪個？",
                [(True, "邏輯斯迴歸（加 ridge 懲罰）：重疊時兩者表現相近，而機率輸出是它直接就有的",
                  "對，兩個條件都指向邏輯斯迴歸。ISLP 說類別重疊較多時常偏好邏輯斯迴歸；講義也說想估機率就選 LR，並把「不直接提供機率」列為 SVM 的缺點。"),
                 (False, "SVM 使用 RBF 核：它比較有彈性，機率可以用 SVC(probability=True) 拿到",
                  "這條路繞遠了。probability=True 是在 SVM 分數之上另外擬合一個機率模型，需要額外的交叉驗證；既然重疊時兩者的分類結果相近，直接用邏輯斯迴歸更簡單。"),
                 (False, "SVM 擬合線性核：類別重疊正是 hinge loss 的強項，因為它會忽略遠處的點",
                  "把強項說反了。類別分得很開才是 SVM 的強項；重疊時大部分點都在間隔內，都是支持向量，hinge 的稀疏性優勢消失。")])

    return r'''
  <p>SVM 在 1990 年代中期出場時很轟動：找一片盡量分開資料的超平面、允許少數違反、
  用核擴張特徵空間。這套說法看起來跟邏輯斯迴歸、LDA 完全是兩個世界的東西。
  ISLP §9.5 的任務就是把這個神祕感拆掉。</p>

  <p>拆解的關鍵是 hinge loss 一節的改寫：支持向量分類器等價於</p>

  $$\underset{\beta_0,\dots,\beta_p}{\text{minimize}} \left\{
    \underbrace{\sum_{i=1}^{n} \max\left[0, 1 - y_i f(x_i)\right]}_{\text{hinge loss}}
    + \lambda \underbrace{\sum_{j=1}^{p} \beta_j^2}_{\text{ridge 懲罰}} \right\}$$

  <p>而講義說 hinge loss 很像邏輯斯迴歸的「損失」，也就是負對數概似。加了 ridge 懲罰的邏輯斯迴歸是</p>

  $$\underset{\beta_0,\dots,\beta_p}{\text{minimize}} \left\{
    \sum_{i=1}^{n} \log\left(1 + e^{-y_i f(x_i)}\right)
    + \lambda \sum_{j=1}^{p} \beta_j^2 \right\}$$

  <p><strong>只有損失函數換了一項，其他一模一樣。</strong>hinge loss 在 $y_if(x_i)\ge1$ 時恰好是 0，
  這些點在間隔正確的一側；邏輯斯迴歸的損失在哪裡都不是 0，但離邊界很遠的點損失非常小。
  兩個損失的形狀相近，所以 ISLP 的結論是：<strong>邏輯斯迴歸與支持向量分類器常常給出非常相似的結果</strong>。</p>
''' + cmp_table + comparison + r'''
<div class="info-box">
  <span class="info-label">怎麼選？講義的四句話</span>
  <strong>① 類別（幾乎）可分開時，SVC 往往比邏輯斯迴歸好，LDA 也好。</strong>這是傾向，不是保證；和適當正則化的邏輯斯迴歸比，仍要用驗證資料判斷。<br>
  <strong>② 類別重疊時，加了 ridge 懲罰的邏輯斯迴歸與 SVC 非常相似。</strong><br>
  <strong>③ 想要估計機率，就選邏輯斯迴歸。</strong>SVM 只以 $f(x)$ 的正負號決定類別。<br>
  <strong>④ 非線性邊界時，核 SVM 很普及。</strong>
  邏輯斯迴歸與 LDA 也能使用核，只是計算比較貴。ISLP 補充：本書許多分類方法都能用非線性核，
  核在 SVM 特別普及主要是歷史原因。
</div>
''' + kernel_beyond + r'''
  <p>講義最後幾頁談計算。<strong>隨機梯度下降</strong>（SGD）是擬合線性分類器的簡單又有效率的方法，
  適用於線性 SVM、邏輯斯迴歸這類凸損失；它對特徵尺度敏感，可以搭配核近似處理非線性。
  問題規模很大時，講義建議試試 <code>SGDClassifier</code> 搭配 hinge loss。</p>

  <ul>
    <li><strong>要先縮放資料</strong>：SVM 的演算法不具尺度不變性。</li>
    <li><strong>線性情形</strong>用 <code>LinearSVC</code>（liblinear 實作，不接受 <code>kernel</code> 參數）；
    <strong>非線性情形</strong>用 <code>SVC</code>（libsvm）或 <code>NuSVC</code>，兩者相近，只是參數組不同。
    liblinear 與 libsvm 都是林智仁團隊開發的高效率函式庫。</li>
    <li>SVM 也可以估計機率（細節見下方收合）。</li>
    <li><strong>C 預設是 1</strong>，是合理的起點；雜訊多的話應該調小，C 小代表更多正則化。</li>
  </ul>

  <p>講義用一段話總結 SVM 的關鍵特色：使用<strong>核</strong>、<strong>不會卡在局部極小</strong>
  （最佳化問題是凸的，任何局部最佳解都是全域最佳）、<strong>解是稀疏的</strong>（只有支持向量有作用），
  以及<strong>以最大化間隔來控制模型容量</strong>。SVM 也能延伸到迴歸、密度估計與新穎偵測。</p>

  <p>迴歸的延伸叫<strong>支持向量迴歸</strong>（support vector regression）。最小平方法讓每一筆殘差都計入損失；
  支持向量迴歸<strong>只讓絕對值超過某個正常數的殘差計入</strong>，等於把間隔的概念搬到迴歸。
</p>
''' + vs_lab + qa_wrap("觀念釐清", [qa_choose, qa_why]) + svr + solvers + oneclass + q_vs


def build(old):
    return {"kernel": _kernel(old), "multiclass": _multiclass(old), "vslogit": _vslogit(old)}
