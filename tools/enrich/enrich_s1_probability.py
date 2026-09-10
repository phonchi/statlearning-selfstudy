#!/usr/bin/env python3
"""Original S1 examples and seeded Bernoulli experiment; no course lab output."""
from lib import apply, hook, info, info_card, qa, quiz, rows_card, svg, table, viz


def source(page, label):
    return (f'<p class="source-note">延伸閱讀：<a href="https://seeing-theory.brown.edu/doc/seeing-theory.pdf#page={page}" '
            f'target="_blank" rel="noopener">Seeing Theory 講義 p.{page} · {label}</a>。</p>')


BODIES = {}
BODIES['population'] = r'''
<p>你想知道全班每天平均花多少時間通勤，卻只問了坐在附近的五位同學。
這五個答案可以描述受訪者；要用它們推測全班，還需要考慮誰有機會被問到。
統計的起點是說清楚<strong>想了解誰，以及手上觀察到誰</strong>。</p>
<p><strong>母體（population）</strong>是研究想涵蓋的全部對象；<strong>樣本（sample）</strong>是實際觀察到的部分。
母體的數值特徵叫<strong>參數（parameter）</strong>，例如全班平均通勤時間 μ。
由樣本算出的數值叫<strong>統計量（statistic）</strong>，例如五位同學的平均值。</p>



''' + '' + info('樣本數與代表性',
    '多問一些人可減少某些隨機波動，但若始終只問同一類人，抽樣偏差仍可能存在。') + '' + source(16, 'Estimation：由樣本了解母體') + hook('銜接正課',
    '正課的<a href="introduction.html#eda">探索式資料分析</a>會進一步用摘要與圖形了解資料。這裡先分清描述樣本與推論母體。')

BODIES['chance'] = r'''
<p>投擲一枚硬幣之前，結果尚未確定。我們用<strong>樣本空間（sample space）</strong>列出所有可能結果，
用<strong>事件（event）</strong>表示其中想觀察的一組結果。一次投擲的樣本空間可寫成 Ω = {正面，反面}；事件 A 是「出現正面」。</p>
<p>機率 P(A) 是模型為事件指定的數值，介於 0 和 1 之間。所有可能結果合起來的機率為 1。
若模型假設硬幣公平，正反面機率各為 0.5；機率相等需要理由，不能只因為有兩種結果就各分一半。</p>
$$0\le P(A)\le 1,\qquad P(\Omega)=1,\qquad P(A^c)=1-P(A).$$
<p>這裡 Aᶜ 表示「A 沒有發生」。例如公平骰子出現偶數的機率為 3/6 = 1/2；出現非偶數的機率也為 1/2。</p>
<p>假設連續投擲硬幣 10 次，有 7 次正面。<strong>觀察比例</strong>是 7/10 = 0.7，
它是這次資料的摘要；模型中的正面機率 p 可以仍是 0.5。有限樣本會有波動。</p>
''' + viz(svg('w21coin', 320), [info_card('先預測再操作',
    '把正面機率設為 0.5，先猜投 10 次會不會剛好一半，再增加到 100 次。藍色實線是累積觀察比例，虛線是模型機率。'),
    rows_card('模型與這次樣本', [('投擲次數', '0', 'w21n'), ('正面次數', '0', 'w21heads'), ('觀察比例', '尚無樣本', 'w21proportion'),
                                 ('期望值（下一節說明）', '0.500', 'w21mean'), ('變異數（第四節說明）', '0.250', 'w21variance')]),
    info_card('條件保持一致', '每次投擲獨立、p 固定。調整 p 會清空舊樣本，讓新實驗維持同一個機率模型。')],
    'w21status', '尚未投擲；先選 p，再按一次或十次。',
    '<label for="w21p">正面機率 p <output id="w21pValue">0.50</output></label>'
    '<input id="w21p" type="range" min="0" max="1" step="0.05" value="0.5" oninput="w21Change()">'
    '<button class="btn btn-step" onclick="w21Toss(1)">投擲一次</button>'
    '<button class="btn btn-step" onclick="w21Toss(10)">投擲十次</button>'
    '<button class="btn btn-step" onclick="w21Toss(100)">投擲一百次</button>'
    '<button class="btn btn-reset" onclick="w21Reset()">重置</button>',
    provenance=('simulation', '本站 Bernoulli 模擬，固定種子 2106；每次最多累積 500 筆。理論值由 p 與 p(1−p) 計算，非課本實測資料。')) + qa('再想一步', [
    ('前九次都反面，第十次正面的機率會增加嗎？', '在每次獨立且 p 不變的模型下，第十次仍是 p。硬幣不會為了補回比例而改變機率。'),
    ('觀察比例會每一步都更靠近 p 嗎？', '可能暫時更遠。長期穩定不代表每一步都改善，也不保證有限次投擲恰好等於 p。')]) + quiz('qChance', 'PART 02 · 自我檢測',
    '公平硬幣投 10 次出現 7 次正面，這表示什麼？', [
    (True, '這次的觀察比例是 0.7，仍可能來自 p = 0.5 的模型。', '模型機率描述隨機機制；觀察比例會隨樣本改變。'),
    (False, '硬幣不可能公平。', '公平模型允許 7 次正面，不能只憑一次比例不同就排除模型。'),
    (False, '接下來三次必須都是反面。', '獨立投擲不會補償先前的結果；每次正面機率仍為 0.5。')]) + source(5, 'Chance Events')

BODIES['expectation'] = r'''
<p>要對硬幣結果算平均，先把正面記為 1、反面記為 0。這個把結果轉成數字的規則叫
<strong>隨機變數（random variable）</strong>，記作 X。擲出來的某次結果 x 則是它的一個觀察值。</p>
<p><strong>期望值（expectation）</strong>把每個可能值乘上出現機率，再全部相加。
下式的 Σ 表示加總；例如可能值只有 0 和 1，就只加這兩項。這裡先處理有限多個可能值。</p>
$$E[X]=\sum_x xP(X=x).$$
<p>正面機率 p = 0.3 時，E[X] = 0 × 0.7 + 1 × 0.3 = 0.3。
每次只能得到 0 或 1，但長期平均可以接近 0.3。期望值不必是一次實驗能得到的值。</p>
<p>公平骰子的期望值同樣是加權平均：</p>
$$E[X]=1\cdot\frac16+2\cdot\frac16+\cdots+6\cdot\frac16=\frac{21}{6}=3.5.$$

''' + info('樣本平均與期望值', '樣本平均使用已觀察的值，期望值使用機率模型。上方硬幣實驗的觀察比例也就是 0／1 資料的樣本平均。') + quiz('qExpectation', 'PART 03 · 自我檢測',
    '公平骰子的期望值為 3.5，正確解讀是？', [
    (False, '下一次最可能擲出 3.5。', '骰子只有 1 到 6 點，單次不可能得到 3.5。'),
    (False, '任意六次投擲的平均必須是 3.5。', '六次仍有隨機波動，不保證六種點數各一次。'),
    (True, '許多次獨立投擲的平均會趨近 3.5。', '在同一公平模型下，期望值是長期平均的目標；單次或有限次結果可以不同。')]) + source(10, 'Expectation')

BODIES['variation'] = r'''
<p>兩個分布都可能平均為 3，波動卻不同。若 X 等機率取 2 或 4，離平均的距離都是 1；
若 Y 等機率取 0 或 6，距離都是 3。只報平均無法呈現這個差異。</p>
<p><strong>變異數（variance）</strong>是偏離期望值的平方之期望。
直接把正負偏差平均會相互抵銷，平方能保留偏離的大小。
<strong>標準差（standard deviation）</strong>是變異數的平方根，單位回到原本的測量單位。</p>
$$\operatorname{Var}(X)=E[(X-E[X])^2]=E[X^2]-(E[X])^2,\qquad \sigma=\sqrt{\operatorname{Var}(X)}.$$
<p>上述 X 的變異數是 (1² + 1²)/2 = 1，Y 的變異數是 (3² + 3²)/2 = 9，標準差分別為 1 與 3。
對 0／1 硬幣，X² = X，所以 Var(X) = p − p² = p(1−p)。
p = 0.5 時是 0.25；p = 0 或 1 時結果固定，變異數為 0。可回上方滑桿核對。</p>
<p>把所有數值換成 Y = aX + b 時，平移 b 不改變每個值與平均的距離；乘上 a 則使偏差乘上 a，平方偏差因此乘上 a²：</p>
$$E[Y]=aE[X]+b,\qquad \operatorname{Var}(Y)=a^2\operatorname{Var}(X).$$

<p>手上若只有樣本，常用以下公式估計母體變異數（n ≥ 2）：</p>
$$s^2=\frac{1}{n-1}\sum_{i=1}^n(x_i-\bar{x})^2.$$
<p>用 n−1 作分母，能在獨立同分布、有限變異數的抽樣下得到母體變異數的不偏估計。
若只是描述手上 n 筆資料的平均平方偏差，也可以除以 n，但要說清楚目的。
例如樣本 {2, 4} 的樣本平均為 3，s² = 2；這與上面「完整機率分布」的變異數 1 使用不同資訊及分母。</p>
<p><strong>大數法則（law of large numbers）</strong>說明：在獨立同分布且期望值存在等條件下，
樣本平均會隨樣本數增加而趨近母體期望值。本頁的有限值硬幣模型符合條件。
觀察平均更穩定，並不代表每一次投擲本身變得更穩定；單次變異數仍為 p(1−p)。</p>
''' + '' + source(12, 'Variance') + source(17, 'Consistency of Estimators：長期穩定的例子，推導續於 p.18')

BODIES['exercises'] = ''.join([
    '',
    '',
    '',
    quiz('qEx4', 'EXERCISE 4', '從 100 次增加到 200 次獨立公平投擲，哪件事有理論保證？', [
        (False, '這一次的比例誤差一定更小。', '某次序列仍可能暫時偏離更多，長期性質不代表每一步改善。'),
        (True, '每一次投擲的正面機率仍為 0.5。', '模型條件保持固定。樣本平均更穩定是抽樣分布的性質。'),
        (False, '累積正面數一定為 100。', '期望正面數為 100；實際次數會波動。')])])
BODIES['reference'] = table(['概念', '怎麼算／怎麼讀'], [
    ('樣本平均', '把已觀察的數值加總後除以 n。'), ('期望值', '把模型中每個可能值乘上機率後加總。'),
    ('變異數', 'E[(X−E[X])²] = E[X²] − (E[X])²。'), ('標準差', '變異數開平方根，單位與原資料相同。'),
    ('樣本變異數', '估計母體變異數時常用 Σ(xᵢ−x̄)²／(n−1)，n ≥ 2。'),
    ('大數法則', '合適抽樣條件下，樣本平均隨 n 增加而趨近期望值；不保證每一步更接近。')]) + '''

<p>接著讀<a href="s2_conditional.html">條件機率與獨立</a>；若已熟悉這些概念，可<a href="introduction.html">直接進入正課</a>。</p>'''

PAGEJS = r'''
let w21Rand = HC.stat.lcg(2106);
let w21Values = [];
function w21Model(p) { return {mean:p, variance:p*(1-p)}; }
function w21Render() {
  const p = Number(document.getElementById('w21p').value);
  const s = HC.svg('w21coin', {h:320, xd:[0,Math.max(10,w21Values.length)], yd:[0,1], pad:{l:52,r:18,t:20,b:44}});
  s.clear(); s.grid(5,4,{ydec:2,xtitle:'累積投擲次數',ytitle:'正面比例'});
  s.poly([[0,p],[Math.max(10,w21Values.length),p]],{cls:'w21theory',stroke:HC.tok.accent3,sw:2,dash:'6 4'});
  let heads = 0;
  const points = w21Values.map((x,i)=>{heads+=x;return [i+1,heads/(i+1)];});
  if (points.length > 1) s.poly(points,{cls:'w21observed',stroke:HC.tok.accent2,sw:2});
  if (points.length) s.dot(points[points.length-1][0],points[points.length-1][1],{fill:HC.tok.accent2});
  const model = w21Model(p);
  document.getElementById('w21pValue').textContent = p.toFixed(2);
  document.getElementById('w21n').textContent = w21Values.length;
  document.getElementById('w21heads').textContent = heads;
  document.getElementById('w21proportion').textContent = points.length ? (heads/points.length).toFixed(3) : '尚無樣本';
  document.getElementById('w21mean').textContent = model.mean.toFixed(3);
  document.getElementById('w21variance').textContent = model.variance.toFixed(3);
  setStatus('w21status', points.length ? '累積 '+points.length+' 次，正面 '+heads+' 次。藍色實線可上下波動；虛線 p 固定。'+(points.length===500?'已達 500 次，重置可重做。':'') : '尚未投擲。虛線顯示模型機率 p，沒有樣本時不計觀察比例。');
}
function w21Toss(count) {
  const p = Number(document.getElementById('w21p').value);
  const add = Math.min(count,500-w21Values.length);
  for(let i=0;i<add;i++) w21Values.push(w21Rand()<p?1:0);
  w21Render();
}
function w21Change() { w21Rand=HC.stat.lcg(2106);w21Values=[];w21Render(); }
function w21Reset() { document.getElementById('w21p').value='0.5';w21Change(); }
w21Render();
'''

# Coverage completion 2026-09-10
from lib import proof

BODIES['expectation'] += r"""
<h3>加總與加權平均</h3>
<p>只要相關期望值存在，期望值具有線性性，<strong>不需要獨立</strong>：</p>
$$E[aX+bY+c]=aE[X]+bE[Y]+c.$$
<p>例如兩天各有期望通勤時間 20 分鐘，總時間的期望是 40 分鐘；即使兩天都受同一交通狀況影響，這個加法仍成立。</p>
""" + proof('w21proof-linearity', '期望值的線性性', r"""
<p>以有限離散分布為例，對所有可能的配對加總：</p>
$$E[aX+bY+c]=\sum_{x,y}(ax+by+c)P(X=x,Y=y)
=a\sum_x xP(X=x)+b\sum_y yP(Y=y)+c.$$
<p>這裡只用了邊際機率等於聯合機率的加總，沒有將聯合機率拆成乘積。</p>
""")
BODIES['variation'] += r"""
<h3>加總後的變異數，以及平均為什麼較穩定</h3>
<p>期望值可以直接相加，變異數則要考慮變數是否一起波動。定義
$\operatorname{Cov}(X,Y)=E[(X-E[X])(Y-E[Y])]$，有限二階動差下有：</p>
$$\operatorname{Var}(aX+bY)=a^2\operatorname{Var}(X)+b^2\operatorname{Var}(Y)+2ab\operatorname{Cov}(X,Y).$$
<p>獨立會使共變異數為 0。因此，若 $X_1,\ldots,X_n$ 獨立同分布，平均為 μ、有限變異數為 σ²，</p>
$$E[\bar X]=\mu,\qquad \operatorname{Var}(\bar X)=\frac{\sigma^2}{n}.$$

""" + proof('w21proof-varsum', '變異數加法與樣本平均的變異數', r"""
<p>把 $a(X-E[X])+b(Y-E[Y])$ 平方後取期望，平方項給出兩個變異數，交叉項給出 $2ab\operatorname{Cov}(X,Y)$。
獨立時 $E[XY]=E[X]E[Y]$，所以交叉項為 0。於是</p>
$$\operatorname{Var}\!\left(\frac1n\sum_iX_i\right)=\frac1{n^2}\sum_i\sigma^2=\frac{\sigma^2}{n}.$$
""") + proof('w21proof-unbiased', '樣本變異數為什麼除以 n−1', r"""
<p>在上述獨立同分布、有限變異數的條件下，</p>
$$\sum_i(X_i-\bar X)^2=\sum_i(X_i-\mu)^2-n(\bar X-\mu)^2.$$
<p>兩邊取期望，右邊是 $n\sigma^2-n\operatorname{Var}(\bar X)=(n-1)\sigma^2$。
因此 $n\ge2$ 時，$E[s^2]=\sigma^2$。</p>
""") + r"""
<h3>延伸：把「越來越穩定」寫成機率界限</h3>
<p>Markov 不等式適用於非負 X 與 $a&gt;0$；Chebyshev 不等式適用於有限變異數的 X 與 $\varepsilon&gt;0$：</p>
$$P(X\ge a)\le\frac{E[X]}a,\qquad
P(|X-\mu|\ge\varepsilon)\le\frac{\sigma^2}{\varepsilon^2}.$$
<p>套在樣本平均，可得 $P(|\bar X-\mu|\ge\varepsilon)\le\sigma^2/(n\varepsilon^2)$。
這個界限隨 n 趨近 0，說明有限變異數、獨立同分布情況下的弱大數法則；它不要求每一次新抽樣都比前一次接近 μ。</p>
""" + proof('w21proof-lln', 'Markov、Chebyshev 與弱大數法則', r"""
<p>因為 $X\ge a\mathbf1_{\{X\ge a\}}$，取期望得 $E[X]\ge aP(X\ge a)$，這就是 Markov 不等式。
再把非負變數 $(X-\mu)^2$ 與門檻 $\varepsilon^2$ 代入，得到 Chebyshev 不等式。
最後代入 $\operatorname{Var}(\bar X)=\sigma^2/n$；固定 $\varepsilon&gt;0$ 時右邊隨 n 增大而趨近 0。</p>
""") + source(10,'期望值與變異數性質') + source(14,'Markov 與 Chebyshev 不等式；一致性見 pp.17–18')


# Reading flow: short main text with complete optional details.
from reading_supplements import apply_reading
PAGEJS = apply_reading('s1_probability', BODIES, PAGEJS)

if __name__ == '__main__':
    apply('s1_probability', BODIES, PAGEJS)
