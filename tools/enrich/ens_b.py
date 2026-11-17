"""集成各節 B：boosting、modern（XGBoost）、splitsearch（切點搜尋）。

依據：ISLP §8.2.3、ESL §10.1–10.12、XGBoost 論文（arXiv 1603.02754）與官方文件、StatQuest 影片、
講義 08 p.43–56、68–69；來源筆記在 tools/verification/ensemble-deepen-20261117/sources/。
沿用上游的兩個元件（w09gbSvg、w09adaSvg，id 不變）；新增 w09xgb*（葉值與增益）與 w09split*（切點搜尋）。
"""
import re

from ens_common import (btn, card, chunk, detail, grab_details, grab_viz, info, info_card, lab, links,
                        proof, qa, quiz, rows_card, select, slider, svg, table, viz, LAB)
from lib import lab_output

SECS = ["boosting", "modern", "splitsearch"]


def _wide(sel):
    """讓下拉選單獨佔控制列的一整列。"""
    sel = sel.replace("flex:1 1 200px", "flex:1 1 100%", 1)
    return sel.replace("<select ", '<select style="max-width:100%;min-width:0;flex:1 1 auto;" ', 1)


def _rep(s, old, new):
    if s.count(old) != 1:
        raise ValueError(f"比對到 {s.count(old)} 次：{old[:40]}")
    return s.replace(old, new)


# ══ boosting ══════════════════════════════════════════════════════════════
ALGO82 = r"""<div class="info-box">
  <span class="info-label">迴歸樹的提升法，ISLP 演算法 8.2</span>
  <strong>1.</strong> 令 $\hat f(x) = 0$，殘差 $r_i = y_i$。<br>
  <strong>2.</strong> 對 $b = 1, 2, \dots, B$：<br>
  &nbsp;&nbsp;&nbsp;(a) 用 $(X, r)$ 擬合一棵只有 $d$ 次分裂（$d+1$ 個葉子）的<strong>小樹</strong> $\hat f^b$；<br>
  &nbsp;&nbsp;&nbsp;(b) 把收縮後的它加進去：$\hat f(x) \leftarrow \hat f(x) + \lambda \hat f^b(x)$；<br>
  &nbsp;&nbsp;&nbsp;(c) 更新殘差：$r_i \leftarrow r_i - \lambda \hat f^b(x_i)$。<br>
  <strong>3.</strong> 輸出 $\hat f(x) = \sum_{b=1}^{B} \lambda \hat f^b(x)$。
</div>"""

PARAMS = table(
    ["參數", "意思", "常見取法", "調錯會怎樣"],
    [["<strong>B</strong>（樹的棵數）", "跑幾輪", "用交叉驗證或提前停止（early stopping）選",
      "太大會過度擬合，只是通常發生得很慢；bagging 與 random forest 加樹不會有這個問題"],
     ["<strong>λ</strong>（收縮、學習率）", "每棵樹只採用 λ 倍", "0.01 或 0.001 這類小數",
      "λ 愈小，需要的 B 愈大；兩者要一起選，沒有固定的換算比例"],
     ["<strong>d</strong>（每棵樹的分裂次數）", "交互作用深度（interaction depth）", "常常 d = 1 就夠",
      "d 次分裂最多牽涉 d 個變數，所以 d 決定模型能有幾階交互作用；d = 1 的 stump 得到加法模型"]])

ADA_FORMULA = r"""<p><strong>AdaBoost</strong> 是更早的提升法。它不改目標，改<strong>每一筆資料的權重</strong>：這一輪答錯的點，下一輪權重變大，下一個分類器就會特別在意它們。講義的寫法是</p>
$$\alpha_j = \eta \log \frac{1 - e_j}{e_j}, \qquad
  w_{j+1}(i) = \begin{cases}
    w_j(i) \cdot e^{-\alpha_j} & \text{答對} \\
    w_j(i) \cdot e^{+\alpha_j} & \text{答錯}
  \end{cases}, \qquad
  \hat y = \arg\max_k \sum_{j:\, h_j(x) = k} \alpha_j .$$
<p>$w_j(i)$ 是第 $j$ 輪第 $i$ 筆資料的權重，$e_j$ 是第 $j$ 個分類器 $h_j$ 的<strong>加權</strong>錯誤率，$\eta$ 控制更新幅度（這裡的 $\alpha_j$ 和剪枝的 $\alpha$ 無關）。$\alpha_j$ 有兩個用途：它決定下一輪權重放大多少，也是 $h_j$ 在最後投票裡的份量。錯誤率愈低，$\alpha_j$ 愈大，票愈重；$e_j$ 要小於 0.5，$\alpha_j$ 才是正的。</p>
<p>講義附錄用 moons 資料畫出連續五個分類器的決策邊界：第一個分類器答錯很多點，這些點的權重被放大，第二個就把它們分得比較好，依此類推。講義右邊的圖把學習率減半，每一輪的權重調整比較溫和，決策邊界的變化也比較慢。這和梯度下降很像，差別在 AdaBoost 每一輪加進一個新的分類器，梯度下降則是調整同一個模型的參數。</p>"""

ADA_ETA = r"""<p><strong>η 取 ½ 還是 1？</strong>講義的更新是對稱的：答對乘 $e^{-\alpha_j}$、答錯乘 $e^{\alpha_j}$。一輪之後，答錯者相對答對者的權重比是 $e^{2\alpha_j}=\big((1-e_j)/e_j\big)^{2\eta}$。取 $\eta=\tfrac12$ 時這個比值是 $(1-e_j)/e_j$，和 ESL 演算法 10.1（只把答錯者乘上 $e^{\alpha_m}$，$\alpha_m=\log\frac{1-\mathrm{err}_m}{\mathrm{err}_m}$）以及 Freund 與 Schapire 原版的權重更新完全相同，正規化之後一樣；投票份量只差一個共同的 2 倍，取 argmax 的結果不變。若在這組對稱式裡取 $\eta=1$，比值會變成平方，是更激進的另一種更新。下面的元件取 $\eta=\tfrac12$。</p>"""

ADA_PROOF = proof("w09proof-adaboost", "AdaBoost 的 α 是指數損失下的最佳步長",
    r"""<p>令二元標籤 $y_i\in\{-1,1\}$、分類器輸出 $h(x)\in\{-1,1\}$，目前的模型是 $F_{m-1}$。ESL §10.4 把 AdaBoost 看成在<strong>指數損失</strong> $L(y,F)=e^{-yF}$ 下一次加一項的前向逐步擬合（forward stagewise）。加入 $\beta h_m$ 後的損失是</p>
$$\sum_i e^{-y_i(F_{m-1}(x_i)+\beta h_m(x_i))}=\sum_i w_i\,e^{-\beta y_ih_m(x_i)},\qquad w_i=e^{-y_iF_{m-1}(x_i)}.$$
<p>把權重正規化成總和 1，令 $e=\sum_iw_iI(y_i\ne h_m(x_i))$，損失變成 $Z(\beta)=(1-e)e^{-\beta}+e\,e^{\beta}$。對 $\beta$ 微分令其為 0：$e\,e^{\beta}=(1-e)e^{-\beta}$，所以</p>
$$\beta_m=\tfrac12\log\frac{1-e}{e}.$$
<p>二階導數為正，這是極小值。下一輪的權重是 $w_i e^{-\beta_m y_ih_m(x_i)}$：答對乘 $e^{-\beta_m}$、答錯乘 $e^{\beta_m}$，正是講義 $\eta=\tfrac12$ 的對稱式。因為 $-y_ih_m(x_i)=2I(y_i\ne h_m(x_i))-1$，同一個更新也可以寫成「只把答錯者乘上 $e^{2\beta_m}$，所有人再乘共同的 $e^{-\beta_m}$」；共同因子在正規化時消失，所以 ESL 演算法 10.1 的 $\alpha_m=2\beta_m=\log\frac{1-e}{e}$ 與它等價（ESL 式 10.15）。</p>
<p>指數損失的族群最佳解是 $F^*(x)=\tfrac12\log\frac{P(Y=1\mid x)}{P(Y=-1\mid x)}$（ESL 式 10.16），所以 AdaBoost 加總出來的分數是在估計<strong>一半的</strong>對數勝算（log-odds）。這和後面 logistic 損失用的完整 log-odds 差一個 2 倍，兩種尺度不要混用。</p>""")


def _ada_detail(old):
    d = grab_details(old["boosting"], "w09-detail-adaboost-demo")
    v = grab_viz(d, "w09adaSvg")
    v = re.sub(r'<div class="info-card">\s*<div class="ic-title">為什麼 boosting 的樹要很淺.*?</div>\s*</div>',
               lambda _m: info_card("為什麼 boosting 的樹可以很淺",
                   '每一棵只要修掉前面還沒處理好的一小塊，所以小樹就夠用（ISLP §8.2.3）。'
                   '但小樹也有代價：stump 只用一個變數，很多棵 stump 加起來仍是<strong>加法模型</strong>，'
                   '要表示交互作用就得讓 d 大於 1。'), v, count=1, flags=re.S)
    if "為什麼 boosting 的樹可以很淺" not in v:
        raise ValueError("AdaBoost 元件的側欄卡沒有換到")
    return detail("w09-detail-adaboost-demo", "AdaBoost：權重怎麼更新、α 從哪裡來",
                  '<h4 id="dx-ada">AdaBoost 的權重更新</h4>' + ADA_ETA + v + ADA_PROOF)


GRADIENT_DETAIL = r"""<h4>ESL 演算法 10.3：一般損失的梯度提升</h4>
<ol>
<li>$f_0(x)=\arg\min_\gamma\sum_iL(y_i,\gamma)$，先用最好的常數。</li>
<li>對 $m=1,\dots,M$：
 <ol type="a">
 <li>算偽殘差 $r_{im}=-\left[\dfrac{\partial L(y_i,f(x_i))}{\partial f(x_i)}\right]_{f=f_{m-1}}$；</li>
 <li>用最小平方對 $r_{im}$ 擬合一棵迴歸樹，得到葉區域 $R_{jm}$，$j=1,\dots,J_m$；</li>
 <li>每一片葉各自求 $$\gamma_{jm}=\arg\min_\gamma\sum_{x_i\in R_{jm}}L\big(y_i,f_{m-1}(x_i)+\gamma\big);$$</li>
 <li>$f_m(x)=f_{m-1}(x)+\nu\sum_j\gamma_{jm}I(x\in R_{jm})$。</li>
 </ol></li>
<li>輸出 $f_M$。</li>
</ol>
<p>$\nu$ 是學習率，就是演算法 8.2 的 $\lambda$；ESL 的 $M$ 是樹數，對應 ISLP 的 $B$。ESL 的樹用終端節點數 $J$ 描述大小，$J$ 片葉就是 $J-1$ 次分裂，所以 ISLP 的 $d$ 等於 $J-1$；ESL §10.11 的經驗是 $4\le J\le8$ 通常就夠。</p>
<h4>各種損失的負梯度與葉值</h4>
""" + table(
    ["損失", "負梯度（偽殘差）", "每片葉的 γ"],
    [[r"平方 $\tfrac12(y-f)^2$", "$y-f$（就是殘差）", "葉內殘差的平均"],
     [r"絕對 $|y-f|$", r"$\operatorname{sign}(y-f)$", "葉內殘差的中位數"],
     ["Huber", r"$|y-f|\le\delta$ 時是 $y-f$，否則 $\delta\operatorname{sign}(y-f)$", "沒有閉式解，用迭代或近似"],
     ["二元 logistic（完整 log-odds）", "$y-p$", r"沒有閉式解；一步 Newton 得 $\sum(y-p)/\sum p(1-p)$"],
     ["多類別 deviance", r"第 $k$ 個分數是 $I(y=k)-p_k$", "對每一類各長一棵樹，各自近似"]]) + r"""
<p>Huber 損失對小殘差用平方、對大殘差改用線性，負梯度被截在 $\pm\delta$，極端值的影響因此有上限（ESL §10.6 與表 10.2）。</p>
<p><strong>一步 Newton 的葉值。</strong>logistic 損失對 log-odds 的一階、二階導數是 $g_i=p_i-y_i$、$h_i=p_i(1-p_i)$。從 $\gamma=0$ 出發走一步 Newton 法，</p>
$$\gamma_j\approx-\frac{\sum_{i\in R_j}g_i}{\sum_{i\in R_j}h_i}=\frac{\sum_{i\in R_j}(y_i-p_i)}{\sum_{i\in R_j}p_i(1-p_i)},$$
<p>就是 ESL 習題 10.8 的式 10.57（多類別版本是演算法 10.4）。XGBoost 的葉值只是在分母多加一個 $\lambda$，見 <a href="#modern">XGBoost 一節</a>。</p>
<p><strong>兩種 log-odds 尺度。</strong>ESL §10.5 為了和 AdaBoost 對齊，把 logistic 寫成 $Y\in\{-1,1\}$、$p=1/(1+e^{-2f})$，此時 $f$ 是一半的 log-odds，負梯度是 $2(y'-p)$（$y'=(Y+1)/2$）。scikit-learn 與 XGBoost 用 $y\in\{0,1\}$ 與完整 log-odds $F$，負梯度是 $y-p$、二階導數是 $p(1-p)$。兩者差常數倍，看公式時先確認是哪一種。</p>
""" + proof("w09proof-gradient", "擬合負梯度就是往損失下降的方向走",
    r"""<p>把訓練點上的預測看成向量 $F=(F(x_1),\dots,F(x_n))$。對小步長 $\epsilon$，$L(F+\epsilon h)=L(F)+\epsilon\nabla L(F)^{\mathsf T}h+O(\epsilon^2)$。選 $h=-\nabla L(F)$ 時一階變化是 $-\epsilon\|\nabla L(F)\|^2\le0$，這是最陡下降方向。梯度只在訓練點上有定義，所以用最小平方把負梯度近似成一棵小樹，新資料也能用；葉值再用每片葉的 argmin 決定步長。樹只是近似，擬合得不好時，不能光憑名稱保證每一步都下降，所以學習率要小。</p>""")


BOOST_QA = qa("觀念釐清", [
    ("平方損失下，每片葉的修正量會不會退化成「全部區域同一個修正」？",
     r"""<p>不會。演算法 10.3 的第 (c) 步對<strong>每一片葉</strong>各自求 argmin。平方損失時，第 $j$ 片葉的解是落在這片葉裡的殘差平均，每片葉各有自己的值（ESL §10.9 式 10.30）。</p>
<p>「單一修正量」是另一件事：一般的最陡下降法沿整個負梯度向量只找一個步長 $\rho_m$。梯度提升在樹的每個終端區域各做一次一維搜尋（ESL §10.10），所以比單一步長更細。平方損失下這兩者剛好接得起來：樹本身擬合殘差，葉值就是殘差平均，全域步長取 1 即可。</p>"""),
    ("Boosting 有袋外（OOB）樣本嗎？",
     r"""<p>演算法 8.2 不做 bootstrap，每棵樹都看全部資料，所以沒有 OOB。隨機梯度提升（stochastic gradient boosting）是例外：它每一輪不放回地抽一部分資料（ESL §10.12 建議常用一半）來長樹，沒被抽到的就能用來算 OOB 改善量，scikit-learn 的 <code>oob_improvement_</code> 就是它。官方文件提醒這個估計通常偏悲觀，選樹數仍建議用交叉驗證。</p>"""),
])

BOOST_QUIZ = quiz("qBoost", "QUIZ · Boosting",
    "用平方損失做梯度提升時，第 m 輪長好樹之後，某一片葉的修正量 γ 該取什麼？",
    [(False, "所有葉共用同一個修正量，用整體的一維搜尋決定",
      "那是一般最陡下降法沿整個梯度向量找單一步長。梯度提升對每片葉各做一次 argmin，所以每片葉有自己的值。"),
     (True, "落在這片葉裡的殘差的平均",
      "對。平方損失下，葉內 argmin 的解就是葉內殘差平均（ESL 式 10.30）；每片葉的平均不同，修正量也不同。"),
     (False, "落在這片葉裡的原始 y 的平均",
      "那是單棵迴歸樹的葉值。提升法的新樹修正的是目前模型還沒解釋的部分，所以用的是殘差，不是 y。")])


def boosting(old):
    gb = grab_viz(old["boosting"], "w09gbSvg")
    return "\n".join([
        r"""<p>Bagging 與 random forest 是<strong>並行</strong>的：B 棵樹互不參照，可以同時長。Boosting 正好相反，樹是<strong>一棵接一棵</strong>長出來的，每一棵都依前面那些樹的結果決定自己要修什麼。演算法 8.2 也不做 bootstrap，每棵樹都看全部資料，只是要擬合的目標換成了還沒解釋掉的部分（ISLP §8.2.3）。講義說 bagging 的每棵樹「各自建立在自己的 bootstrap 樣本上」，指的是建樹時互不參照，不是說樹的預測彼此獨立。</p>
<p>因為每一棵新樹都考慮了已經長好的樹，boosting 主要在<strong>降低偏差</strong>，小樹就夠用。Bagging 則反過來，拿低偏差、高變異的深樹去平均，壓的是變異。</p>""",
        r"""<p><strong>從階梯函數看 boosting。</strong>一棵只用一個變數、切 $d$ 刀的樹，畫出來是有 $d+1$ 階的階梯函數；多個變數時是把特徵空間切成方塊、每塊一個常數（分段常數函數）。Boosting 把很多棵這種小樹乘上 $\lambda$ 再相加，結果仍是分段常數，但階梯可以細到逼近平滑的曲線。如果每棵都是 stump（$d=1$），每棵只碰一個變數，加總以後就是 $\hat f(x)=\sum_j f_j(x_j)$ 的<strong>加法模型</strong>；$d=2$ 才開始出現兩個變數的交互作用。</p>""",
        r"<p>講義的梯度提升連著三頁：先用一個逐步算例（每一輪擬合殘差、全部採用，等於學習率 1 的特例）說明想法，接著列出 ISLP 演算法 8.2，最後解釋它為什麼「學得慢」。演算法 8.2 只有三步：</p>",
        ALGO82,
        r"""<p>步驟 (a) 擬合的是<strong>目前模型的殘差 $r$</strong>：第一棵樹抓走一部分結構，剩下沒解釋掉的變成新的目標，第二棵樹再去抓它。$\lambda$ 讓每一棵只採用一小部分，ISLP 的說法是 boosting <strong>學得很慢</strong>，而在統計學習裡，學得慢的方法往往表現得好。</p>""",
        gb,
        r"<p>Boosting 有三個要調的參數。和 bagging 不同，它<strong>真的會過度擬合</strong>：</p>",
        PARAMS,
        r"""<p>Lab 與上面的元件用 <code>max_depth</code> 限制最大深度，這裡記為 $D$，它和課本的分裂次數 $d$ 不同：最大深度 $D$ 的二元樹最多有 $2^D$ 片葉，實際可以更少；$d$ 次分裂則一定有 $d+1$ 片葉。</p>
<p>講義用同一份基因表達資料改做二元分類（癌症或正常），比較 boosting 與 random forest（ISLP 圖 8.11）。兩個 boosting 模型都用 $\lambda=0.01$。正文說深度 1 的樹勝過深度 2，兩者又都勝過 random forest；圖說則說明標準誤約 0.02，<strong>這些差異都不顯著</strong>。單棵樹的測試錯誤率是 24%。這是二元問題，和 random forest 一節 15 類、單棵樹 45.7% 的問題不同，兩個數字不能直接比。</p>""",
        detail("w09-detail-boosting-lab", "Lab：Boston 上的梯度提升與兩種學習率",
               lab("梯度提升", 76, 76)
               + card("測試誤差隨樹數變化，以及最終的測試 MSE",
                      chunk(78) + "\n\n" + chunk(80), lab_output(8, 80), src=f"<code>{LAB}</code> · 儲存格 78、80")
               + lab("把學習率改成 0.2", 82, 82)),
        r"""<p>Lab（程式與輸出在上面的收合）在 Boston 資料上用 <code>learning_rate=0.001</code> 得到測試 MSE 14.48，改成 0.2 得到 14.50。這只說明在這一次切分、5000 棵深度 3 的樹之下兩組設定差不多；換一份資料或少一些樹，結果可能不同，所以 $B$、$\lambda$、$d$ 仍要一起用驗證資料選。</p>""",
        r"""<h3>從殘差到一般損失：梯度提升</h3>
<p>演算法 8.2 擬合殘差，是因為平方損失 $\tfrac12(y-f)^2$ 對預測值 $f$ 的負梯度正好是 $y-f$，也就是殘差。換成別的損失，只要把「殘差」換成<strong>負梯度</strong>：</p>
$$r_{i}=-\left.\frac{\partial L(y_i,f)}{\partial f}\right|_{f=f_{m-1}(x_i)} .$$
<p>這叫偽殘差（pseudo-residual）。用小樹擬合它，得到葉區域 $R_j$；接著<strong>每一片葉各自</strong>找最好的修正量</p>
$$\gamma_j=\arg\min_{\gamma}\sum_{x_i\in R_j}L\big(y_i,\,f_{m-1}(x_i)+\gamma\big).$$
<p>為什麼還要 argmin？樹只告訴我們「怎麼分區、每區大概往哪個方向修」，但每一區該走多遠要看損失本身。平方損失下這一步的解就是葉內殘差平均，各葉不同；其他損失沒有這麼簡單。</p>
<p><strong>分類用 logistic 損失。</strong>模型輸出的是 log-odds $F$，機率 $p=1/(1+e^{-F})$。對 $F$ 微分，梯度是 $p-y$，負梯度是 $y-p$：所以「梯度就是殘差」不精確，梯度是<strong>負的</strong>殘差，負梯度才是殘差，而且這個殘差是機率尺度的 $y-p$，修正量卻加在 log-odds 上。葉值沒有閉式解，常用一步 Newton 近似 $\gamma_j\approx\sum(y_i-p_i)/\sum p_i(1-p_i)$。例如第一輪所有 $p=0.5$，某片葉有三筆、$y=(1,1,0)$：分子 $0.5$、分母 $0.75$，葉值約 $0.667$，對應的機率是 $1/(1+e^{-0.667})\approx0.661$（還沒乘學習率）。</p>""",
        detail("w09-detail-gradient-general", "梯度提升的完整演算法、各種損失與兩種 log-odds 尺度", GRADIENT_DETAIL),
        r"""<h3>AdaBoost：不改目標，改權重</h3>""",
        ADA_FORMULA,
        _ada_detail(old),
        BOOST_QA,
        BOOST_QUIZ,
        links([("https://dafriedman97.github.io/mlbook/content/c6/s1/boosting.html", "提升法推導"),
               ("https://sefiks.com/2018/10/04/a-step-by-step-gradient-boosting-decision-tree-example/", "梯度提升逐步算例"),
               ("https://www.youtube.com/watch?v=3CC4N4z3GJc", "StatQuest：梯度提升（迴歸）"),
               ("https://yuhangzhou88.github.io/ESL_Solution/", "ESL 習題解答")]),
    ])


# ══ modern（XGBoost）═════════════════════════════════════════════════════
XGB_VIZ = viz(
    svg("w09xgbSvg", 360),
    [rows_card("左葉", [("G（梯度和）", "—", "w09xgbGL"), ("H（Hessian 和）", "—", "w09xgbHL"),
                        ("葉值 w*", "—", "w09xgbWL")]),
     rows_card("右葉", [("G（梯度和）", "—", "w09xgbGR"), ("H（Hessian 和）", "—", "w09xgbHR"),
                        ("葉值 w*", "—", "w09xgbWR")]),
     rows_card("這一刀", [("增益（論文式，含 ½、扣 γ）", "—", "w09xgbGain"),
                          ("StatQuest 的 Gain（不含 ½、未扣 γ）", "—", "w09xgbSq"),
                          ("切不切", "—", "w09xgbKeep"),
                          ("第 1 筆的新預測（η = 0.3）", "—", "w09xgbPred")]),
     info_card("怎麼看",
               '上圖的柱子是每筆資料的負梯度 −g（迴歸時就是殘差），圓點愈大代表 Hessian h 愈大；虛線是目前的切點。'
               '下圖左邊是兩片葉的葉值：空心框是 λ = 0 時的值，實心是目前 λ 下的值，λ 愈大，實心柱縮得愈多。'
               '右邊是這一刀的增益，那條直線是 γ；增益超過這條線才切。'
               '<br>迴歸模式用 StatQuest XGBoost 第 1 集的四筆資料（初始預測 0.5，殘差 −10.5、6.5、7.5、−7.5）。'
               '影片的 γ 是拿不含 ½ 的 Gain 比，換成論文式要除以 2。'
               '<br>這個示意沒有設 <code>min_child_weight</code>（相當於 0）。分類模式每片葉的 H 都小於官方預設的 1，真的用預設值訓練時，這些切法都會被擋下。'
               '「不切」時，第 1 筆的新預測改用不分裂的單一葉值。')],
    "w09xgbStatus", "換切點、拖 λ 與 γ，看兩片葉的值與這一刀的增益怎麼變。",
    _wide(select("w09xgbMode", "損失", [("reg", "迴歸（平方損失）"), ("cls1", "分類：第一輪，p 全是 0.5"),
                                  ("cls2", "分類：已有預測，有篤定也有猶豫")], "w09xgbSetMode()"))
    + slider("w09xgbSlCut", "切點", 1, 3, 1, 1, "x &lt; 15", "w09xgbSet()", "100%")
    + slider("w09xgbSlLam", "λ", 0, 20, 1, 0, "0", "w09xgbSet()", "100%")
    + slider("w09xgbSlGam", "γ", 0, 80, 1, 0, "0", "w09xgbSet()", "100%"),
    provenance=("illustrative", "四筆示意資料：迴歸模式取自講義連結的 StatQuest XGBoost 影片例；分類模式為自選標籤與機率。G、H、葉值與增益依 XGBoost 論文式 (5)–(7) 即時計算。"))

XGB_DERIV = proof("w09proof-xgb-leaf", "二階展開後，每片葉的最佳值是 −G/(H+λ)，分裂增益是兩個結構分數的差",
    r"""<p>第 $t$ 輪的目標是 $\sum_i l\big(y_i,\hat y_i^{(t-1)}+f_t(x_i)\big)+\Omega(f_t)$。把損失在目前預測 $\hat y_i^{(t-1)}$ 附近做二階泰勒展開：</p>
$$l\big(y_i,\hat y_i^{(t-1)}+f\big)\approx l\big(y_i,\hat y_i^{(t-1)}\big)+g_if+\tfrac12h_if^2 .$$
<p>第一項和新樹無關，丟掉。樹把每筆資料送到某一片葉，同一片葉 $j$ 的所有資料得到同一個值 $w_j$。把求和依葉重組（$I_j$ 是落在葉 $j$ 的資料，$G_j=\sum_{i\in I_j}g_i$、$H_j=\sum_{i\in I_j}h_i$，$T$ 是葉數）：</p>
$$\tilde{\mathcal L}=\sum_{j=1}^{T}\Big[G_jw_j+\tfrac12(H_j+\lambda)w_j^2\Big]+\gamma T .$$
<p>各葉互不干擾，每一項是 $w_j$ 的開口向上拋物線。配平方：</p>
$$G_jw_j+\tfrac12(H_j+\lambda)w_j^2=\tfrac12(H_j+\lambda)\Big(w_j+\frac{G_j}{H_j+\lambda}\Big)^2-\frac12\frac{G_j^2}{H_j+\lambda},$$
<p>所以最低點在 $w_j^*=-G_j/(H_j+\lambda)$，最低值是 $-\tfrac12G_j^2/(H_j+\lambda)$。$\lambda=0$ 時 $w_j^*=-G_j/H_j$，正是 Newton 法的一步；$\lambda>0$ 等於在 Newton 步上加了嶺迴歸式的收縮。</p>
<p>把一片葉切成左右兩片，葉數多 1，目標值的下降量就是</p>
$$\text{Gain}=\frac12\left[\frac{G_L^2}{H_L+\lambda}+\frac{G_R^2}{H_R+\lambda}-\frac{(G_L+G_R)^2}{H_L+H_R+\lambda}\right]-\gamma .$$
<p>Gain 不大於 0 就不值得切（論文式 5–7）。StatQuest 影片的 similarity score 是 $G^2/(H+\lambda)$，省略了 ½；只拿來互相比較時，同乘 2 不影響哪一刀最好，但和 γ 比的時候要用同一個尺度。</p>""")

XGB_LOGISTIC = detail("w09-detail-xgb-logistic", "logistic 損失的 g 與 h，以及影片裡的 O、p、p₀",
    r"""<p>二元分類 $y\in\{0,1\}$，模型輸出 log-odds $F$，$p=1/(1+e^{-F})$，損失是 $l=-[y\log p+(1-y)\log(1-p)]$。因為 $dp/dF=p(1-p)$，</p>
$$g=\frac{\partial l}{\partial F}=p-y,\qquad h=\frac{\partial^2 l}{\partial F^2}=p(1-p).$$
<p>所以 $g$ 是負的殘差，$-g=y-p$ 才是殘差；$h$ 在 $p=0.5$ 時最大，等於 0.25，$p$ 接近 0 或 1 時趨近 0。代入葉值公式：</p>
$$w^*=\frac{\sum_{i}(y_i-p_i)}{\sum_i p_i(1-p_i)+\lambda}.$$
<p><strong>對照 StatQuest 第 3 集。</strong>影片把新樹的葉輸出叫 output value，記作 $O$，它就是這裡的 $w^*$。影片的 $p_i$ 是<strong>上一輪</strong>對第 $i$ 筆預測的機率，$p^0$ 是第一輪之前的初始預測；兩者在第一輪是同一個數，之後 $p_i$ 會隨每一輪更新。$O$ 的單位是 log-odds，所以新預測要在 log-odds 上相加再換回機率：</p>
$$\log\frac{p_i^{\text{new}}}{1-p_i^{\text{new}}}=\log\frac{p_i}{1-p_i}+\eta\,O .$$
<p>不能把 $O$ 直接加到機率上。影片的初始預測 0.5 對應 log-odds 0，這是當時 <code>base_score</code> 的預設；新版 XGBoost 的截距處理會依版本與目標函數而不同，以官方文件為準。迴歸用平方損失時 $g=-(y-\hat y)$、$h=1$，葉值是 $\sum r_i/(n+\lambda)$，$\lambda=0$ 時就是葉內殘差平均，和 Boosting 一節的梯度提升一致。</p>""")

XGB_GUARDS = detail("w09-detail-xgb-guards", "min_child_weight、max_delta_step 與缺失值的演算法",
    r"""<p><strong><code>min_child_weight</code></strong>：官方定義是「子節點所需的樣本權重（Hessian）總和下限」，預設 1；分裂後任一子節點的 $H$ 小於它就不切。平方損失下 $h_i=1$，它就等於每個子節點的最少筆數。logistic 損失下 $h_i=p_i(1-p_i)\le0.25$，預設值 1 至少需要 4 筆最猶豫（$p=0.5$）的資料；若葉裡都是已經被預測得很篤定的點，需要的筆數更多。這個限制擋住的是「$H$ 很小、葉值 $-G/(H+\lambda)$ 卻可能很大」的葉。LightGBM 也有同名參數，它是 <code>min_sum_hessian_in_leaf</code> 的別名，預設只有 0.001，LightGBM 主要靠 <code>min_data_in_leaf</code>（預設 20 筆）控制葉的大小。</p>
<p><strong><code>max_delta_step</code></strong>：限制每片葉輸出的絕對值，預設 0 表示不限制。官方說它在類別極度不平衡的 logistic 迴歸可能有幫助，建議值 1 到 10；理由同上，$H$ 很小時葉值容易暴衝。</p>
<p><strong>缺失值的預設方向（論文演算法 3）。</strong>在某個節點評估特徵 $x_k$ 時，$G$、$H$ 用節點內全部資料計算，但只掃 $x_k$ 不缺失的那些資料，而且掃兩趟：第一趟依 $x_k$ 由小到大累加左邊，缺失的資料自動落在右邊；第二趟由大到小累加右邊，缺失的落在左邊。兩趟所有候選切點中增益最大的那一個，同時決定切點與<strong>預設方向</strong>。之後預測時，這個特徵缺失的資料就走預設方向。每個節點各自學一個方向，而且只掃非缺失值，計算量和非缺失值的個數成正比。</p>
<p>要小心「缺失」的定義：<code>missing</code> 預設是 NaN；用 scipy 稀疏矩陣餵資料時，沒有存的 0 也會被當成缺失（官方 FAQ），這和密集矩陣裡的 0 是不同的值。</p>""")

XGB_QA = qa("觀念釐清", [
    ("XGBoost 的 λ 和 ISLP 演算法 8.2 的 λ 一樣嗎？",
     r"""<p>不一樣。ISLP 的 $\lambda$ 是學習率（收縮），每棵樹只採用 $\lambda$ 倍；XGBoost 的學習率叫 $\eta$（參數 <code>eta</code>，預設 0.3）。XGBoost 的 $\lambda$（參數 <code>lambda</code>，預設 1）是葉值的 L2 懲罰，出現在葉值與增益的分母裡。兩者都讓模型保守一點，但作用的地方不同：$\eta$ 在整棵樹算好之後打折，$\lambda$ 在算葉值時就把它往 0 拉。StatQuest 第 1 集說 $\lambda$ 預設是 0，那是舊的說法，現行官方文件是 1。</p>"""),
    ("XGBoost 切分的時候，是對負梯度或 Hessian 切嗎？",
     r"""<p>不是。切分永遠是對<strong>特徵</strong> $x$ 切，例如「$x_k&lt;15$」。每筆資料的 $g_i$、$h_i$ 只是拿來算每一個候選切點的 $G_L,H_L,G_R,H_R$ 與增益的統計量。新樹擬合的是負梯度這件事，表現在增益公式裡：葉值 $-G/(H+\lambda)$ 往負梯度的方向走，增益衡量的是這樣分組能讓二階近似的損失降多少。</p>"""),
])

XGB_QUIZ = quiz("qModern", "QUIZ · XGBoost",
    "二元分類用 logistic 損失時，XGBoost 的 <code>min_child_weight=1</code> 限制的是什麼？",
    [(False, "每個子節點至少要有 1 筆資料",
      "那只在平方損失時成立，因為每筆的 Hessian 都是 1。logistic 損失下每筆的 Hessian 是 p(1−p)，最多 0.25。"),
     (True, "每個子節點裡 p(1−p) 的總和至少要 1",
      "對。官方定義是子節點 Hessian 總和的下限；最猶豫的點 p = 0.5 每筆貢獻 0.25，所以至少要 4 筆，篤定的點需要更多。"),
     (False, "每個子節點裡梯度和的絕對值至少要 1",
      "限制的是 Hessian 和 H，不是梯度和 G。G 可正可負、可以很小，它決定的是葉值方向與大小。")])

HEART_TABLE = table(
    ["這次只搜的參數", "候選值", "最佳值", "最佳 CV 準確率"],
    [["<code>learning_rate</code>", "0.01–0.5", "0.5", "0.79557"],
     ["<code>max_depth</code>", "2, 3, 5, 6, 8", "3", "0.81197"],
     ["<code>gamma</code>", "0–2", "0.1", "0.81197"],
     ["<code>min_child_weight</code>", "1–5", "4", "0.81197"],
     ["<code>subsample</code>", "0.5–1", "0.5", "0.81536"],
     ["<code>colsample_bytree</code>", "0.5–1", "0.7", "0.80552"],
     ["<code>n_estimators</code>", "100, 200, 400, 800", "400", "0.79541"]])

HEART_DETAIL = detail("w09-detail-xgb-lab", "Lab：heart_disease 上的 XGBoost 調參與提前停止",
    r"""<p>Lab 在 303 筆、13 個特徵的 <code>heart_disease.csv</code> 上，先用預設設定與分層 5 折交叉驗證得到基準準確率 0.79，各折在 0.74 到 0.82 之間。</p>"""
    + lab("基準：預設 XGBoost 的交叉驗證準確率", 124, 124)
    + lab("每次只搜一個參數的 grid_search", 126)
    + r"""<p><code>grid_search</code> 每次都新建一個模型，<strong>只搜傳進去的那一個參數，其他參數都維持預設</strong>。所以下表各列彼此獨立，不是逐步累加的調參；也不能把最好的幾個值湊在一起，就假設會更好。</p>"""
    + HEART_TABLE
    + lab("只搜 max_depth", 134, 134)
    + lab("只搜 subsample", 145, 145)
    + lab("只搜 n_estimators", 153, 153)
    + r"""<p>讀這張表的方式：<code>max_depth</code> 從預設 6 降到 3、或把 <code>subsample</code> 降到 0.5，交叉驗證準確率約 0.81 到 0.82，比基準高約 2 個百分點，方向都是讓模型簡單一點。<code>n_estimators</code> 最好的是 400，得 0.79541，和基準相當，Lab 的說法是「並未帶來更好的結果」。各折之間的差距本來就有 0.08，這些 0.01 到 0.02 的差別要保守看待。Lab 文字寫 <code>max_depth</code>「從 6 改為 2」，但輸出的最佳值是 3，以輸出為準。</p>"""
    + lab("提前停止：設定 early_stopping_rounds=10", 162, 162)
    + r"""<p>驗證集的錯誤率在第 0 輪最低（0.15789），lab 保存的紀錄列到第 9 輪，之後各輪都沒有更低；只看保存的輸出，無法確定實際在哪一輪停止。最後的準確率 84.21% 等於 1 − 0.15789，也就是用了錯誤率最低那一輪的模型。這個 Lab 把<strong>測試集</strong>當成 <code>eval_set</code> 來決定何時停止，等於用測試集選了樹數，這個準確率會偏樂觀；實務上要另外切一份驗證集。</p>""")


def modern(old):
    return "\n".join([
        r"""<p><strong>XGBoost</strong>（Extreme Gradient Boosting）是梯度提升的一個實作，講義的說法是「內建正則化的梯度提升，加上很大的速度改進」。這一節講統計上的部分：目標函數、葉值、分裂增益與缺失值；速度上的部分（切點怎麼找、直方圖、平行化）放在下一節。和所有樹模型一樣，它只看特徵的大小順序，所以不必先標準化。</p>""",
        r"""<p>第 $t$ 輪要加一棵新樹 $f_t$。XGBoost 的目標除了損失，還加了一項對這棵樹本身的懲罰：</p>
$$\text{Obj}^{(t)}=\sum_{i=1}^{n}l\big(y_i,\ \hat y_i^{(t-1)}+f_t(x_i)\big)+\gamma T+\tfrac12\lambda\sum_{j=1}^{T}w_j^2 .$$
<p>$T$ 是葉子數，$w_j$ 是第 $j$ 片葉的輸出值。$\gamma$ 是「多開一片葉要付的代價」，$\lambda$ 是葉值的 L2 懲罰。這裡的 $\lambda$ 不是 ISLP 的學習率，XGBoost 的學習率另外叫 $\eta$。</p>""",
        r"""<p><strong>二階近似。</strong>對每一筆資料，把損失在上一輪的預測附近展開到二階，只需要兩個數：一階導數 $g_i$ 與二階導數（Hessian）$h_i$。同一片葉的資料得到同一個值，所以把葉 $j$ 裡的 $g_i$、$h_i$ 加起來記成 $G_j$、$H_j$，每片葉的目標就成了一條拋物線 $G_jw_j+\tfrac12(H_j+\lambda)w_j^2$。拋物線的最低點與一刀的增益是</p>
$$w_j^*=-\frac{G_j}{H_j+\lambda},\qquad
\text{Gain}=\frac12\left[\frac{G_L^2}{H_L+\lambda}+\frac{G_R^2}{H_R+\lambda}-\frac{(G_L+G_R)^2}{H_L+H_R+\lambda}\right]-\gamma .$$
<p>講義說這是「類似 Newton 法的近似」：沒有 $\lambda$ 時 $w^*=-G/H$ 就是 Newton 法的一步。</p>""",
        table(["損失", "$g_i$", "$h_i$", "葉值 $w^*$"],
              [[r"平方 $\tfrac12(y-\hat y)^2$", r"$\hat y_i-y_i$（負的殘差）", "1", r"$\dfrac{\sum r_i}{n+\lambda}$，$\lambda=0$ 時是葉內殘差平均"],
               ["logistic（log-odds 尺度）", "$p_i-y_i$", "$p_i(1-p_i)$", r"$\dfrac{\sum(y_i-p_i)}{\sum p_i(1-p_i)+\lambda}$"]]),
        r"""<p>logistic 的葉值和 <a href="#boosting">Boosting 一節</a>的一步 Newton 葉值只差分母裡的 $\lambda$。StatQuest 影片裡的 output value $O$ 就是 $w^*$：$p_i$ 是上一輪預測的機率，$O$ 的單位是 log-odds，乘上學習率 $\eta$ 之後加在 log-odds 上，再換回機率。</p>""",
        r"""<p><strong>λ 的直覺。</strong>葉值 $-G/(H+\lambda)$ 會縮成 $\lambda=0$ 時的 $H/(H+\lambda)$ 倍。$H$ 大的葉（資料多，或分類時有很多猶豫的點）幾乎不受影響；$H$ 小的葉（只有一兩筆，或都是預測得很篤定的點）被往 0 拉得最多。$\lambda$ 也出現在增益的分母，會壓低小葉子帶來的增益，使它們比較不容易被切出來。效果和嶺迴歸一樣：不讓少數幾筆資料決定一片葉的輸出。</p>
<p><strong>γ 的直覺。</strong>Gain 已經扣掉 $\gamma$，所以 $\gamma$ 是一刀至少要帶來的下降量。它和剪枝一節成本複雜度剪枝的「每片葉付 $\alpha$」是同一個想法，但流程不同：$\gamma$ 直接進入每一刀的增益，增益扣掉 $\gamma$ 後不為正的切法就不採用。StatQuest 影片描述的是「先長到 <code>max_depth</code>，再由下往上剪掉 Gain 為負的分支，子分支保留時父分支也保留」；現行預設的 <code>hist</code> 在展開節點時就會依增益、深度與葉數限制決定要不要切，不保證先長滿再剪。不論哪種流程，$\gamma$ 都是同一個門檻。$\lambda>0$ 時，未扣 $\gamma$ 的增益本身也可能是負的，所以 $\gamma=0$ 不等於不剪。</p>""",
        XGB_VIZ,
        r"""<p>迴歸模式的預設狀態就是影片的例子：切在 $x&lt;15$ 時，左葉只有殘差 −10.5，右葉是 6.5、7.5、−7.5。$\lambda=0$ 時兩片葉的值是 −10.5 與 2.17，StatQuest 的 Gain 是 120.33（論文式含 ½ 是 60.17）。換到另外兩個切點，Gain 只有 4 與 56.33，所以第一刀切在 15。在 $\lambda=0$ 下乘上 $\eta=0.3$，第一筆的預測從 0.5 變成 $0.5+0.3\times(-10.5)=-2.65$。把 $\lambda$ 拉到 1，左葉的值減半成 −5.25，StatQuest 的 Gain 降到 62.49（論文式 31.24），第一筆的預測則變成 $0.5+0.3\times(-5.25)=-1.075$。</p>""",
        r"""<p><strong><code>min_child_weight</code>。</strong>這個參數限制的是子節點的 <strong>Hessian 總和</strong> $H$，預設 1，不是梯度、也不一定是筆數。平方損失下 $h_i=1$，它就是最少筆數；logistic 損失下最猶豫的點每筆只貢獻 0.25，篤定的點更少，所以分類時它要求的筆數會比 1 多很多。切到分類模式，拖切點時可以看到篤定的點（小圓點）對 $H$ 幾乎沒有貢獻。</p>
<p><strong>缺失值。</strong>講義說 XGBoost 會自己處理缺失值。做法是在每個節點把缺失的資料分別全部丟到左邊、全部丟到右邊各算一次增益，選增益大的方向當這個節點的<strong>預設方向</strong>；之後預測時，缺失值就走這條路。這裡的缺失是<strong>特徵 $x$ 缺失、$y$ 有值</strong>：有 $y$ 才算得出 $g_i$、$h_i$，這筆資料才能參與訓練。$y$ 缺失的資料不能拿來做監督式訓練，只能先移除，或在建模前另外處理。</p>""",
        XGB_DERIV,
        XGB_LOGISTIC,
        XGB_GUARDS,
        XGB_QA,
        HEART_DETAIL,
        XGB_QUIZ,
        links([("https://arxiv.org/pdf/1603.02754.pdf", "XGBoost 原論文"),
               ("https://xgboost.readthedocs.io/en/latest/tutorials/model.html", "XGBoost 官方的提升樹推導"),
               ("https://stats.stackexchange.com/questions/202858/xgboost-loss-function-approximation-with-taylor-expansion", "二階泰勒近似的討論"),
               ("https://www.youtube.com/watch?v=OtD8wVaFm6E", "StatQuest：XGBoost 第 1 集（迴歸）"),
               ("https://www.youtube.com/watch?v=ZVFeW798-2I", "StatQuest：XGBoost 第 3 集（數學細節）"),
               ("https://xgboost.readthedocs.io/en/stable/parameter.html", "XGBoost 參數說明"),
               ("https://xgboost.readthedocs.io/en/stable/faq.html#how-to-deal-with-missing-values", "XGBoost 缺失值處理"),
               ("https://stats.stackexchange.com/questions/353462/what-are-the-implications-of-scaling-the-features-to-xgboost", "樹模型與特徵尺度"),
               ("https://xgboost.readthedocs.io/en/latest/", "XGBoost 官方文件")]),
    ])


# ══ splitsearch ══════════════════════════════════════════════════════════
SPLIT_VIZ = viz(
    svg("w09splitSvg", 360),
    [rows_card("這個方法", [("候選切點數", "—", "w09splitCands"), ("最佳切點 x", "—", "w09splitBest"),
                            ("最佳增益", "—", "w09splitGain")]),
     rows_card("和精確搜尋比", [("精確搜尋的最佳增益", "—", "w09splitExact"),
                                ("少掉的增益", "—", "w09splitLoss"),
                                ("各箱 h 總和（最小～最大）", "—", "w09splitBins")]),
     info_card("怎麼看",
               '上圖每個點是一筆資料，上排 y = 1、下排 y = 0，圓點愈大代表 h = p(1−p) 愈大，也就是上一輪的預測愈猶豫。'
               '底下的刻度是這個方法的候選切點，交錯的色塊是分箱。'
               '下圖灰線是精確搜尋時每個切點的增益，彩色點是這個方法實際會試的切點，大圓圈是它選中的那一個。'
               '<br>分箱的對象永遠是特徵值 x；箱子裡累加的是 g 與 h。這裡 λ 取 0，只比較候選切點的位置。')],
    "w09splitStatus", "切換方法與箱數，看候選切點落在哪裡、少掉多少增益。",
    _wide(select("w09splitMeth", "方法", [("exact", "精確搜尋（相鄰值中點）"),
                                    ("hist", "等頻分箱（hist）"),
                                    ("wq", "Hessian 加權分位（approx）")], "w09splitSet()"))
    + _wide(select("w09splitPMode", "上一輪預測", [("mid", "兩端篤定、中間猶豫"),
                                              ("wrong", "有一段篤定地預測錯"),
                                              ("flat", "第一輪：p 全是 0.5")], "w09splitSet()"))
    + slider("w09splitSlK", "箱數", 4, 32, 1, 8, "8", "w09splitSet()", "180px"),
    provenance=("illustrative", "40 筆固定種子示意資料；上一輪的機率為自選函數。g = p − y、h = p(1 − p)，增益依 XGBoost 論文式 (7)、λ = 0 即時計算；不代表任何套件的實際分箱程式。"))

SPLIT_SYS = detail("w09-detail-split-system", "系統面：快取、壓縮與分片，以及論文的複雜度",
    r"""<p>講義列了 XGBoost 在系統上的幾個設計，這些和統計無關，但決定了它在大資料上的速度。</p>
<p><strong>column block（只排序一次）。</strong>論文 §4.1 說，樹學習最花時間的是把資料排好序。XGBoost 在訓練前把每一個特徵欄排好序，存成壓縮欄格式（CSC）的區塊，之後每一層只要線性掃一次，就能同時收集同一層所有葉的候選切點統計量。設 $K$ 是樹數、$d$ 是最大深度、$\|x\|_0$ 是非缺失值的個數、$n$ 是資料筆數，論文的複雜度是</p>
""" + table(["做法", "原本", "用 column block"],
            [["精確搜尋", r"$O(Kd\|x\|_0\log n)$", r"$O(Kd\|x\|_0+\|x\|_0\log n)$"],
             ["近似搜尋（$q$ 個候選、區塊最多 $B$ 列）", r"$O(Kd\|x\|_0\log q)$", r"$O(Kd\|x\|_0+\|x\|_0\log B)$"]]) + r"""
<p>$\|x\|_0\log n$ 是一次性的排序成本，可以攤到所有輪次上。</p>
<p><strong>快取感知存取（cache-aware access）。</strong>依特徵值的順序掃描時，每一步要去拿那一筆資料的 $g_i$、$h_i$，而它們是依列的順序存放，所以是跳著讀記憶體。統計量放不進 CPU 快取時，每次讀取都可能要到主記憶體去拿。講義附的延遲表（約 2012 年的數字）是：讀一次 L1 快取約 0.5 ns，讀一次主記憶體約 100 ns，相差約 200 倍。XGBoost 的做法是每個執行緒先把要用到的梯度統計量預先搬到自己的緩衝區，再成批累加；近似搜尋則把每個區塊的大小定在 $2^{16}$ 筆，讓統計量放得進快取（論文 §4.2）。</p>
<p><strong>區塊壓縮與分片（block compression、sharding）。</strong>資料大到放不進記憶體時，要從硬碟讀區塊。依延遲表，從硬碟循序讀 1 MB 約 20 ms，是記憶體的 80 倍，而壓縮 1 KB 只要約 3 µs，所以 XGBoost 把區塊壓縮後再存（論文報告壓縮率約 26% 到 29%），用解壓的計算換讀硬碟的時間；有多顆硬碟時把資料交錯分到各顆，同時讀取（論文 §4.3）。</p>
<p><strong>隨機抽樣。</strong>XGBoost 也能對每棵樹抽樣部分資料（<code>subsample</code>）與部分特徵（<code>colsample_bytree</code>、<code>colsample_bylevel</code>、<code>colsample_bynode</code>），既能減少過度擬合，也減少計算。</p>""")


SPLIT_QUIZ = quiz("qSplit", "QUIZ · 切點搜尋",
    "直方圖法（例如 XGBoost 的 <code>hist</code> 或 LightGBM）裡的「直方圖」是對什麼分箱？",
    [(False, "對每筆資料的梯度 g 分箱，切點落在梯度的分位數上",
      "切點永遠是特徵的門檻值。梯度只是累加在箱子裡的統計量，不是被分箱的對象。"),
     (True, "對特徵值 x 分箱，每個箱子累加落在裡面的 g 與 h",
      "對。分箱把連續的 x 換成箱子編號，每個節點只要累加各箱的 Σg、Σh，再掃過箱子的邊界算增益。"),
     (False, "對 Hessian h 分箱，h 大的資料自成一箱",
      "h 只在加權分位草圖裡當權重，用來決定箱子邊界放在 x 的哪裡；分箱的對象仍是 x。")])


def splitsearch(old):
    return "\n".join([
        r"""<p>上一節的增益公式告訴我們「某一刀好不好」，這一節回答另一個問題：<strong>要試哪些刀？</strong>對連續特徵，門檻值有無限多個，但把資料依 $x$ 排序後，相鄰兩個相異值之間的任何門檻都分出同一組左右，所以只要試相鄰相異值的中點。$u$ 個相異值只有 $u-1$ 個候選。排序後由小到大掃一次，邊掃邊累加左邊的 $G_L$、$H_L$，右邊用總和減，就算得出每個候選的增益。這叫<strong>精確貪婪搜尋</strong>（exact greedy）。</p>""",
        r"""<p><strong>排序要做幾次？</strong>照字面實作，每個節點都對自己的資料重新排序，每個特徵每個節點要花 $O(n\log n)$。scikit-learn 傳統的 <code>GradientBoostingClassifier</code> 就是這樣，官方文件說它要「在每個節點、對每個特徵排序」。XGBoost 論文 §4.1 改成在訓練前把每個特徵欄排序一次，存成區塊，之後每一層線性掃一次就收集到所有葉的統計量。所以「XGBoost 每個節點都要重新排序」並不正確；精確搜尋的主要成本是每一層仍要掃過所有資料。</p>""",
        r"""<h3>近似搜尋：只試分位點</h3>
<p>資料很多時，連「每層掃過所有資料」都嫌慢。近似搜尋先依特徵的分位數挑出少數候選切點，把資料歸進這些切點隔出來的箱子，只在箱子邊界上找最好的一刀。論文用一個參數 $\epsilon$ 控制分位點的密度，候選大約 $1/\epsilon$ 個。</p>
<p><strong>為什麼要用 Hessian 加權？</strong>二階近似的目標可以改寫成</p>
$$\sum_{i}\tfrac12 h_i\Big(f(x_i)-\big(-g_i/h_i\big)\Big)^2+\Omega(f)+\text{常數},$$
<p>也就是以 $h_i$ 為權重、以 $-g_i/h_i$ 為標籤的加權最小平方。每筆資料對損失的份量和 $h_i$ 成正比，所以論文（§3.3）讓每個箱子分到大致相同的 <strong>$h$ 總和</strong>，而不是相同的筆數。論文印的標籤是 $g_i/h_i$，展開核對後應是 $-g_i/h_i$，權重是 $h_i$ 的結論不受影響。</p>
<p>迴歸用平方損失時 $h_i=1$，加權分位就是普通的分位數。分類時 $h_i=p_i(1-p_i)$：預測得很篤定的點 $h$ 小，猶豫的點 $h$ 大，所以猶豫的區域會切得比較細。StatQuest 第 4 集的例子：六筆資料上一輪的機率是 0.1、0.1、0.9、0.9、0.6、0.4，權重是 0.09、0.09、0.09、0.09、0.24、0.24，分成 0.18、0.18、0.24、0.24 四箱，兩個猶豫的點各自一箱，不會一正一負的殘差被併在同一箱裡互相抵銷。</p>""",
        r"""<p><strong>直方圖對誰切？</strong>分箱的對象永遠是<strong>特徵值 $x$</strong>，切點也永遠是「$x_k$ 小於某個門檻」。每個箱子裡累加的是落在裡面的 $\sum g$ 與 $\sum h$；算增益時，從左到右把箱子的 $G$、$H$ 累加起來就好。XGBoost 不是對梯度或 Hessian 切，Hessian 只在加權分位裡用來決定箱子的邊界。</p>""",
        SPLIT_VIZ,
        r"""<p>預設是精確搜尋：33 個候選，最好的一刀在 $x=4.55$。切到等頻分箱、8 箱，只剩 7 個候選，最好的一刀落在 3.75，增益少了 36%；改成 Hessian 加權分位，6 個候選就找到和精確搜尋同一刀，「各箱 h 總和」也從 0～0.97 拉近到 0.17～0.49。</p>
<p>把上一輪預測換成「有一段篤定地預測錯」，結果反過來：$x$ 在 4 到 6 之間的 $y=1$ 被篤定地預測成 0，這些點的 $h$ 很小、$|g|$ 卻很大。加權分位在那一段放的切點太少，8 箱時少了 82% 的增益，等頻分箱反而找得到。加權的依據是二階近似裡每筆資料的份量，並不保證每次都切得比較好。換成「第一輪：p 全是 0.5」，所有 $h_i$ 都是 0.25，兩種分箱的切點完全一樣。</p>""",
        r"""<h3>直方圖法</h3>
<p>LightGBM 與現行 XGBoost 的預設 <code>hist</code> 走得更遠：<strong>訓練前</strong>就把每個連續特徵分成固定的箱子（XGBoost 的 <code>max_bin</code> 預設 256，LightGBM 預設 255），之後每個節點只做兩件事：掃過節點內的資料，把 $g$、$h$ 累加到各箱；再掃過箱子的邊界找最好的一刀。第二步的工作量是箱數，不再是資料筆數。兩個兄弟節點的直方圖加起來等於父節點的直方圖，所以只要對資料較少的那一邊建直方圖，另一邊用父節點減掉就好（直方圖相減）。整數的箱子編號也比浮點數省記憶體、存取更連續。</p>
<p>講義說建箱只要 $O(n)$、免去排序的 $O(n\log n)$，單一節點的成本從 $O(\text{特徵數}\times n\log n)$ 降到 $O(\text{特徵數}\times n)$。這是 scikit-learn 文件拿傳統 GBDT（每個節點都排序）和直方圖版 HGBT 比較的說法；和 XGBoost 只排序一次的精確搜尋比，直方圖法的好處主要是每個節點掃箱子而不是掃資料。講義說箱數「不能超過 255」也是 scikit-learn HGBT 的限制，LightGBM 的 <code>max_bin</code> 可以調得更大。</p>""",
        table(["XGBoost 的 <code>tree_method</code>", "候選切點何時決定", "分位的權重", "對應論文"],
              [["<code>exact</code>", "不用決定，試所有相異值", "—", "精確貪婪＋只排序一次的區塊"],
               ["<code>approx</code>", "每棵樹開始前，用全部資料重做", "Hessian $h_i$", "近似搜尋的全域提案"],
               ["<code>hist</code>（<code>auto</code> 等於它，是預設）", "訓練前做一次", "只用使用者給的樣本權重", "官方說是 LightGBM 的做法"]]),
        r"""<p>所以「XGBoost 用 Hessian 加權分位草圖」指的是論文與 <code>tree_method='approx'</code>。論文另有每個節點都重做分位的局部提案，現行版本已經移除。官方建議：平方損失的 Hessian 是常數，加權沒有意義，直接用 <code>hist</code>；用其他損失時 <code>approx</code> 有時比較準但比較慢，多數情況把 <code>hist</code> 的 <code>max_bin</code> 調大就能達到相近的準確度。</p>""",
        r"""<h3>平行計算後怎麼合併</h3>
<p>資料分散在多個核心或多台機器時，每個工作者只看自己那一份資料。直方圖法的合併很簡單：大家用同一組箱子邊界，各自累加自己資料的 $\sum g$、$\sum h$，再把各箱的數字<strong>相加</strong>，結果和一台機器算的完全一樣，之後照常掃箱子邊界找最好的一刀。LightGBM 的資料平行也是這樣，用歸約（reduce）把各機的直方圖加起來。</p>
<p>分位草圖（quantile sketch）解決的是前一步：<strong>箱子邊界放哪裡</strong>。要算精確的分位數得把全部資料排序，資料分散時代價很高；草圖讓每台機器先各自做一份小摘要，再把摘要合併，得到誤差有上界（排名誤差約 $\epsilon$）的近似分位數。論文的貢獻是做出能處理<strong>加權</strong>資料、而且可以合併與精簡的草圖。所以兩種合併不同：草圖合併得到的是近似的邊界，直方圖相加得到的是精確的統計量。</p>""",
        r"""<p>這些設計省下多少時間？Lab 在系外行星資料上比較了 scikit-learn 傳統的梯度提升、XGBoost、LightGBM 與 CatBoost 的訓練時間，程式與輸出放在 <a href="#w09-detail-speed-lab">LightGBM 與 CatBoost 一節的收合</a>：同樣 100 棵深度 2 的樹，傳統實作要幾百秒，三個現代套件都在半分鐘以內。</p>""",
        SPLIT_SYS,
        SPLIT_QUIZ,
        links([("https://stackoverflow.com/questions/45513511/decision-trees-choosing-thresholds-to-split-objects", "候選門檻值怎麼選"),
               ("https://arxiv.org/pdf/1603.02754.pdf", "XGBoost 原論文"),
               ("https://xgboost.readthedocs.io/en/stable/treemethod.html", "XGBoost 的三種 tree method"),
               ("https://www.youtube.com/watch?v=oRrKeUCEbq8", "StatQuest：XGBoost 第 4 集（加速技巧）"),
               ("https://datasketches.apache.org/docs/QuantilesAll/QuantilesOverview.html", "分位草圖概觀"),
               ("https://gist.github.com/jboner/2841832", "記憶體存取延遲表"),
               ("https://hackmd.io/@WangJengYun/HyLtemyxI", "LightGBM 原理筆記"),
               ("https://lightgbm.readthedocs.io/en/latest/Features.html", "LightGBM 的直方圖與平行化")]),
    ])


def build(old):
    return {"boosting": boosting(old), "modern": modern(old), "splitsearch": splitsearch(old)}


# ══ 新元件 JS ════════════════════════════════════════════════════════════
JS = r"""
/* ---------- XGBoost 葉值與增益（w09xgb） ---------- */
const w09xgbX = [10, 20, 25, 35];
const w09xgbCuts = [15, 22.5, 30];
const w09xgbData = {
  reg:  { y: [-10, 7, 8, -7], p: [0.5, 0.5, 0.5, 0.5], cls: false, gmax: 80, gstep: 1 },
  cls1: { y: [0, 1, 1, 0], p: [0.5, 0.5, 0.5, 0.5], cls: true, gmax: 1, gstep: 0.01 },
  cls2: { y: [0, 1, 1, 0], p: [0.1, 0.9, 0.6, 0.4], cls: true, gmax: 1, gstep: 0.01 }
};
let w09xgbMode = 'reg';

function w09xgbStats(mode) {
  const d = w09xgbData[mode];
  /* 平方損失 ½(y−ŷ)²：g = ŷ − y、h = 1；logistic：g = p − y、h = p(1 − p) */
  const g = d.y.map((y, i) => d.p[i] - y);
  const h = d.p.map(p => (d.cls ? p * (1 - p) : 1));
  return { g: g, h: h };
}
function w09xgbSim(G, H, lam) { return G * G / (H + lam); }
function w09xgbEval(mode, cut, lam, gam) {
  const s = w09xgbStats(mode);
  let GL = 0, HL = 0, GR = 0, HR = 0;
  w09xgbX.forEach((x, i) => {
    if (x < w09xgbCuts[cut]) { GL += s.g[i]; HL += s.h[i]; } else { GR += s.g[i]; HR += s.h[i]; }
  });
  const G = GL + GR, H = HL + HR;
  const sq = w09xgbSim(GL, HL, lam) + w09xgbSim(GR, HR, lam) - w09xgbSim(G, H, lam);
  return { s: s, GL: GL, HL: HL, GR: GR, HR: HR,
           wL: -GL / (HL + lam), wR: -GR / (HR + lam),
           wL0: HL > 0 ? -GL / HL : 0, wR0: HR > 0 ? -GR / HR : 0,
           sq: sq, gain: 0.5 * sq - gam };
}
function w09xgbFmt(v) {
  const a = Math.abs(v);
  return HC.fmt(v, a >= 10 ? 2 : (a >= 1 ? 3 : 4));
}
function w09xgbRead() {
  const cut = parseInt(document.getElementById('w09xgbSlCut').value, 10) - 1;
  const lam = parseInt(document.getElementById('w09xgbSlLam').value, 10) / 2;
  const gEl = document.getElementById('w09xgbSlGam');
  const gam = parseFloat(gEl.value);
  return { cut: cut, lam: lam, gam: gam };
}
function w09xgbSetMode() {
  w09xgbMode = document.getElementById('w09xgbMode').value;
  const d = w09xgbData[w09xgbMode], gEl = document.getElementById('w09xgbSlGam');
  gEl.max = String(d.gmax); gEl.step = String(d.gstep); gEl.value = '0';
  w09xgbSet();
}
function w09xgbSet() {
  const r = w09xgbRead(), d = w09xgbData[w09xgbMode];
  document.getElementById('w09xgbSlCutVal').textContent = 'x < ' + w09xgbCuts[r.cut];
  document.getElementById('w09xgbSlLamVal').textContent = HC.fmt(r.lam, 1);
  document.getElementById('w09xgbSlGamVal').textContent = HC.fmt(r.gam, d.cls ? 3 : 0);
  w09xgbDraw(r);
}
function w09xgbDraw(r) {
  const host = w09frame('w09xgbSvg', 360);
  if (!host) return;
  const d = w09xgbData[w09xgbMode], e = w09xgbEval(w09xgbMode, r.cut, r.lam, r.gam);
  const L = 56, R = 600, T = 26, H1 = 140;
  const rmax = d.cls ? 0.6 : 12;
  const xs = x => L + (R - L) * (x - 5) / 35;
  const yr = v => T + H1 / 2 - (H1 / 2) * v / rmax;
  w09mk(host, 'text', { x: L, y: 16, cls: 'axtitle' }, d.cls ? '每筆的負梯度 −g = y − p（機率尺度）' : '每筆的負梯度 −g（就是殘差）');
  w09mk(host, 'line', { x1: L, y1: yr(0), x2: R, y2: yr(0), stroke: 'var(--card-border)' });
  [-1, 1].forEach(sg => w09mk(host, 'text', { x: L - 6, y: yr(sg * rmax * 0.8) + 4, 'text-anchor': 'end',
    fill: 'var(--muted)', style: w09MONO + 'font-size:10px' }, HC.fmt(sg * rmax * 0.8, d.cls ? 2 : 1)));
  w09xgbCuts.forEach((c, k) => w09mk(host, 'line', { x1: xs(c), y1: T, x2: xs(c), y2: T + H1,
    stroke: k === r.cut ? 'var(--ink)' : 'var(--card-border)', 'stroke-width': k === r.cut ? 2 : 1,
    'stroke-dasharray': '5 4' }));
  w09xgbX.forEach((x, i) => {
    const v = -e.s.g[i], left = x < w09xgbCuts[r.cut];
    const col = left ? 'var(--accent)' : 'var(--accent2)';
    w09mk(host, 'line', { x1: xs(x), y1: yr(0), x2: xs(x), y2: yr(v), stroke: col, 'stroke-width': 3 });
    const rad = d.cls ? 4 + 36 * e.s.h[i] : 6;
    w09mk(host, 'circle', { cx: xs(x), cy: yr(v), r: rad, fill: col, 'fill-opacity': 0.55, stroke: col });
    w09mk(host, 'text', { x: xs(x), y: T + H1 + 14, 'text-anchor': 'middle', fill: 'var(--muted)',
      style: w09MONO + 'font-size:10px' }, 'x=' + x);
    w09mk(host, 'text', { x: xs(x) + 10, y: yr(v) + (v >= 0 ? -6 : 14), fill: 'var(--ink)',
      style: w09MONO + 'font-size:10px' }, HC.fmt(v, d.cls ? 2 : 1) + (d.cls ? '  h=' + HC.fmt(e.s.h[i], 2) : ''));
  });
  /* 下半：兩片葉的葉值（空心 = λ = 0；實心 = 目前 λ） */
  const T2 = 216, H2 = 110, LX = 60, BW = 70;
  const wmax = Math.max(1e-9, Math.abs(e.wL0), Math.abs(e.wR0));
  const yw = v => T2 + H2 / 2 - (H2 / 2 - 6) * v / wmax;
  w09mk(host, 'text', { x: LX - 10, y: T2 - 10, cls: 'axtitle' }, d.cls ? '葉值 w*（log-odds）' : '葉值 w*');
  w09mk(host, 'line', { x1: LX - 10, y1: yw(0), x2: LX + 2 * BW + 70, y2: yw(0), stroke: 'var(--card-border)' });
  [['左葉', e.wL0, e.wL, 'var(--accent)', 0], ['右葉', e.wR0, e.wR, 'var(--accent2)', 1]].forEach(a => {
    const x0 = LX + a[4] * (BW + 40);
    w09mk(host, 'rect', { x: x0, y: Math.min(yw(0), yw(a[1])), width: BW, height: Math.abs(yw(a[1]) - yw(0)),
      fill: 'none', stroke: a[3], 'stroke-dasharray': '4 3' });
    w09mk(host, 'rect', { x: x0 + 12, y: Math.min(yw(0), yw(a[2])), width: BW - 24,
      height: Math.max(1, Math.abs(yw(a[2]) - yw(0))), fill: a[3], 'fill-opacity': 0.8 });
    w09mk(host, 'text', { x: x0 + BW / 2, y: T2 + H2 + 14, 'text-anchor': 'middle', fill: 'var(--ink)',
      style: w09MONO + 'font-size:10px' }, a[0] + ' ' + w09xgbFmt(a[2]));
  });
  /* 右下：增益 vs γ */
  const GX = 360, GW = 230, GY = T2 + 30;
  const gref = d.cls ? 1 : 80;
  const gx = v => GX + GW * Math.max(0, Math.min(1, v / gref));
  w09mk(host, 'text', { x: GX, y: T2 - 10, cls: 'axtitle' }, '這一刀的增益（未扣 γ，論文式）');
  w09mk(host, 'rect', { x: GX, y: GY, width: GW, height: 26, fill: 'none', stroke: 'var(--card-border)' });
  const g0 = 0.5 * e.sq;
  w09mk(host, 'rect', { x: GX, y: GY, width: Math.max(0, gx(g0) - GX), height: 26,
    fill: g0 - r.gam > 0 ? 'var(--accent2)' : 'var(--muted)', 'fill-opacity': 0.8 });
  w09mk(host, 'line', { x1: gx(r.gam), y1: GY - 8, x2: gx(r.gam), y2: GY + 34, stroke: 'var(--accent3)', 'stroke-width': 2 });
  w09mk(host, 'text', { x: gx(r.gam), y: GY + 48, 'text-anchor': 'middle', fill: 'var(--ink)',
    style: w09MONO + 'font-size:10px' }, 'γ = ' + HC.fmt(r.gam, d.cls ? 3 : 0));
  w09mk(host, 'text', { x: GX, y: GY + 72, fill: 'var(--ink)', style: w09MONO + 'font-size:11px' },
    '增益 ' + w09xgbFmt(g0) + (g0 < 0 ? '（未扣 γ 已經是負的）' : ''));
  /* 讀值 */
  const set = (id, v) => { document.getElementById(id).textContent = v; };
  set('w09xgbGL', w09xgbFmt(e.GL)); set('w09xgbHL', w09xgbFmt(e.HL)); set('w09xgbWL', w09xgbFmt(e.wL));
  set('w09xgbGR', w09xgbFmt(e.GR)); set('w09xgbHR', w09xgbFmt(e.HR)); set('w09xgbWR', w09xgbFmt(e.wR));
  set('w09xgbGain', w09xgbFmt(e.gain)); set('w09xgbSq', w09xgbFmt(e.sq));
  const keep = e.gain > 1e-9;
  set('w09xgbKeep', keep ? '切' : '不切');
  /* 不切時，這個節點就是一片葉，用父節點的葉值 −G/(H+λ) */
  const wPar = -(e.GL + e.GR) / (e.HL + e.HR + r.lam);
  const w1 = keep ? (w09xgbX[0] < w09xgbCuts[r.cut] ? e.wL : e.wR) : wPar, eta = 0.3;
  if (d.cls) {
    const lo = Math.log(d.p[0] / (1 - d.p[0])) + eta * w1, pn = 1 / (1 + Math.exp(-lo));
    set('w09xgbPred', 'p：' + HC.fmt(d.p[0], 3) + ' → ' + HC.fmt(pn, 3));
  } else {
    set('w09xgbPred', HC.fmt(0.5, 2) + ' → ' + HC.fmt(0.5 + eta * w1, 3));
  }
  setStatus('w09xgbStatus', '切在 x < ' + w09xgbCuts[r.cut] + '：左葉 ' + w09xgbFmt(e.wL) + '、右葉 ' + w09xgbFmt(e.wR)
    + '；增益 ' + w09xgbFmt(e.gain) + (keep ? '，大於 0，這一刀保留。' : '，不大於 0，這一刀不切。')
    + (r.lam > 0 ? ' λ = ' + HC.fmt(r.lam, 1) + ' 把兩片葉都往 0 拉，H 小的那片拉得最多。' : ''));
}

/* ---------- 切點搜尋：精確、等頻分箱、Hessian 加權分位（w09split） ---------- */
const w09splitN = 40, w09splitLam = 0;
const w09splitData = (() => {
  const rand = HC.stat.lcg(26117), xs = [];
  for (let i = 0; i < w09splitN; i++) xs.push(Math.round((0.2 + 9.6 * rand()) * 10) / 10);
  xs.sort((a, b) => a - b);
  /* 真實機率在 x ≈ 4 附近上升。上一輪模型：mid 的轉折也在 4（兩端篤定、中間猶豫）；
     wrong 的轉折放在 6，x 在 4～6 的 y = 1 被篤定地預測錯 */
  const y = xs.map(x => (rand() < 1 / (1 + Math.exp(-1.8 * (x - 4))) ? 1 : 0));
  return { x: xs, y: y };
})();
function w09splitProbs(mode) {
  if (mode === 'flat') return w09splitData.x.map(() => 0.5);
  const c = mode === 'wrong' ? 6 : 4, a = mode === 'wrong' ? 1.4 : 2.2;
  return w09splitData.x.map(x => 1 / (1 + Math.exp(-a * (x - c))));
}
/* 在已排序的資料上，回傳「切在第 k 筆之前」的增益（論文式含 ½，λ = 0，未扣 γ） */
function w09splitGainAt(g, h, k) {
  let GL = 0, HL = 0, G = 0, H = 0;
  for (let i = 0; i < g.length; i++) { G += g[i]; H += h[i]; if (i < k) { GL += g[i]; HL += h[i]; } }
  const lam = w09splitLam, GR = G - GL, HR = H - HL;
  return 0.5 * (GL * GL / (HL + lam) + GR * GR / (HR + lam) - G * G / (H + lam));
}
/* 候選切點：以「切在第 k 筆之前」表示，k 只取 x 真的變動的位置 */
function w09splitCands(meth, h, K) {
  const x = w09splitData.x, n = x.length, out = [];
  const ok = k => k > 0 && k < n && x[k] > x[k - 1];
  if (meth === 'exact') { for (let k = 1; k < n; k++) if (ok(k)) out.push(k); return out; }
  const w = meth === 'wq' ? h : h.map(() => 1);
  const tot = w.reduce((a, b) => a + b, 0);
  let acc = 0, j = 1;
  for (let k = 0; k < n && j < K; k++) {
    acc += w[k];
    while (j < K && acc >= tot * j / K - 1e-12) {
      let kk = k + 1;
      while (kk < n && !ok(kk)) kk++;
      if (kk < n && out.indexOf(kk) < 0) out.push(kk);
      j++;
    }
  }
  return out;
}
function w09splitSet() {
  const meth = document.getElementById('w09splitMeth').value;
  const pm = document.getElementById('w09splitPMode').value;
  const K = parseInt(document.getElementById('w09splitSlK').value, 10);
  document.getElementById('w09splitSlKVal').textContent = meth === 'exact' ? '—' : String(K);
  w09splitDraw(meth, pm, K);
}
function w09splitDraw(meth, pm, K) {
  const host = w09frame('w09splitSvg', 360);
  if (!host) return;
  const x = w09splitData.x, y = w09splitData.y, n = x.length;
  const p = w09splitProbs(pm);
  const g = p.map((pi, i) => pi - y[i]), h = p.map(pi => pi * (1 - pi));
  const L = 50, R = 600;
  const xs = v => L + (R - L) * v / 10;
  const cut = k => (x[k - 1] + x[k]) / 2;
  const all = w09splitCands('exact', h, K), cand = w09splitCands(meth, h, K);
  const gainsAll = all.map(k => w09splitGainAt(g, h, k));
  const gains = cand.map(k => w09splitGainAt(g, h, k));
  /* 上半：資料點與分箱 */
  const T = 22, yRow = [T + 86, T + 30];
  w09mk(host, 'text', { x: L, y: 14, cls: 'axtitle' }, '資料與候選切點（圓點大小 ∝ h = p(1 − p)）');
  if (meth !== 'exact') {
    const edges = [x[0] - 0.1].concat(cand.map(cut)).concat([x[n - 1] + 0.1]);
    for (let b = 0; b + 1 < edges.length; b++) w09mk(host, 'rect', { x: xs(edges[b]), y: T + 8,
      width: Math.max(0, xs(edges[b + 1]) - xs(edges[b])), height: 112,
      fill: b % 2 ? 'var(--card-border)' : 'none', 'fill-opacity': 0.35 });
  }
  w09mk(host, 'text', { x: L - 6, y: yRow[1] + 4, 'text-anchor': 'end', fill: 'var(--muted)', style: w09MONO + 'font-size:10px' }, 'y=1');
  w09mk(host, 'text', { x: L - 6, y: yRow[0] + 4, 'text-anchor': 'end', fill: 'var(--muted)', style: w09MONO + 'font-size:10px' }, 'y=0');
  x.forEach((v, i) => w09mk(host, 'circle', { cx: xs(v), cy: yRow[y[i]], r: 2 + 16 * h[i],
    fill: y[i] ? 'var(--accent2)' : 'var(--accent)', 'fill-opacity': 0.5, stroke: y[i] ? 'var(--accent2)' : 'var(--accent)' }));
  const axY = T + 128;
  w09mk(host, 'line', { x1: L, y1: axY, x2: R, y2: axY, stroke: 'var(--ink)' });
  [0, 2, 4, 6, 8, 10].forEach(v => w09mk(host, 'text', { x: xs(v), y: axY + 14, 'text-anchor': 'middle',
    fill: 'var(--muted)', style: w09MONO + 'font-size:10px' }, String(v)));
  cand.forEach(k => w09mk(host, 'line', { x1: xs(cut(k)), y1: axY - 7, x2: xs(cut(k)), y2: axY + 3,
    stroke: 'var(--ink)', 'stroke-width': 1.5 }));
  /* 下半：增益 */
  const T2 = 196, H2 = 130;
  const gmax = Math.max(1e-9, ...gainsAll);
  const yg = v => T2 + H2 - H2 * Math.max(0, v) / gmax;
  w09mk(host, 'text', { x: L, y: T2 - 8, cls: 'axtitle' }, '每個候選切點的增益（灰線 = 精確搜尋）');
  w09mk(host, 'line', { x1: L, y1: T2 + H2, x2: R, y2: T2 + H2, stroke: 'var(--card-border)' });
  w09mk(host, 'path', { d: all.map((k, i) => (i ? 'L' : 'M') + xs(cut(k)).toFixed(1) + ',' + yg(gainsAll[i]).toFixed(1)).join(' '),
    fill: 'none', stroke: 'var(--muted)', 'stroke-width': 1.4 });
  let bi = 0;
  gains.forEach((v, i) => { if (v > gains[bi]) bi = i; });
  let be = 0;
  gainsAll.forEach((v, i) => { if (v > gainsAll[be]) be = i; });
  cand.forEach((k, i) => w09mk(host, 'circle', { cx: xs(cut(k)), cy: yg(gains[i]), r: 3.5, fill: 'var(--accent2)' }));
  w09mk(host, 'circle', { cx: xs(cut(all[be])), cy: yg(gainsAll[be]), r: 9, fill: 'none', stroke: 'var(--muted)', 'stroke-dasharray': '3 2' });
  if (cand.length) w09mk(host, 'circle', { cx: xs(cut(cand[bi])), cy: yg(gains[bi]), r: 7, fill: 'none', stroke: 'var(--accent2)', 'stroke-width': 2.5 });
  /* 各箱 h 總和 */
  let binTxt = '—';
  if (meth !== 'exact') {
    const ks = [0].concat(cand).concat([n]), sums = [];
    for (let b = 0; b + 1 < ks.length; b++) { let s = 0; for (let i = ks[b]; i < ks[b + 1]; i++) s += h[i]; sums.push(s); }
    binTxt = HC.fmt(Math.min(...sums), 2) + '～' + HC.fmt(Math.max(...sums), 2);
  }
  const best = cand.length ? gains[bi] : 0, ex = gainsAll[be];
  const set = (id, v) => { document.getElementById(id).textContent = v; };
  set('w09splitCands', String(cand.length));
  set('w09splitBest', cand.length ? HC.fmt(cut(cand[bi]), 2) : '—');
  set('w09splitGain', HC.fmt(best, 3));
  set('w09splitExact', HC.fmt(ex, 3));
  set('w09splitLoss', HC.pct(ex > 0 ? 1 - best / ex : 0, 1));
  set('w09splitBins', binTxt);
  const name = meth === 'exact' ? '精確搜尋' : (meth === 'hist' ? '等頻分箱' : 'Hessian 加權分位');
  setStatus('w09splitStatus', name + '試了 ' + cand.length + ' 個切點，選在 x = ' + (cand.length ? HC.fmt(cut(cand[bi]), 2) : '—')
    + (meth === 'exact' ? '；這就是要比的基準。' : '，比精確搜尋（x = ' + HC.fmt(cut(all[be]), 2) + '）少了 ' + HC.pct(ex > 0 ? 1 - best / ex : 0, 1) + ' 的增益。')
    + (pm === 'flat' && meth !== 'exact' ? ' 第一輪所有 h 都是 0.25，加權與不加權的切點相同。' : ''));
}

w09xgbSet();
w09splitSet();
"""
