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
<p>假設取得的通勤時間是 10、15、15、20、40 分鐘。樣本平均數為：</p>
$$\bar{x}=\frac{10+15+15+20+40}{5}=20\text{ 分鐘}.$$
<p>排序後居中的值是中位數 15 分鐘。40 分鐘拉高了平均數；兩者描述的中心位置有所不同。
這些數字是本站自訂的算例。全班的 μ 仍未知，不能直接宣稱也是 20 分鐘。</p>
''' + table(['問題', '例子'], [('母體是誰？', '這一班所有同學。'), ('樣本是誰？', '受訪的五位同學。'),
    ('樣本怎麼來？', '只問附近同學可能漏掉其他座位或缺席的人。'), ('推論需要什麼？', '清楚的抽樣方式，以及對代表性與誤差的說明。')]) + info('樣本數與代表性',
    '多問一些人可減少某些隨機波動，但若始終只問同一類人，抽樣偏差仍可能存在。') + quiz('qPopulation', 'PART 01 · 自我檢測',
    '上述五位同學平均通勤 20 分鐘，哪個說法成立？', [
    (False, '全班平均一定是 20 分鐘。', '20 是五人的樣本平均；沒有觀察全班，也尚未交代抽樣代表性。'),
    (True, '20 分鐘是樣本統計量，可作為推論全班的起點。', '先描述樣本，再考慮抽樣方式及不確定性，才能討論母體。'),
    (False, '只要增加樣本數，就一定消除抽樣偏差。', '只增加同一類受訪者，可能保留原本的選取偏差。')]) + source(16, 'Estimation：由樣本了解母體') + hook('銜接正課',
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
    (False, '接下來三次必須都是反面。', '獨立投擲沒有補償義務；每次正面機率仍為 0.5。')]) + source(5, 'Chance Events')

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
<p>若把每次獎勵定為 Y = 2X + 10，平均獎勵是 E[Y] = 2E[X] + 10。
以骰子為例，期望獎勵為 17。公式先對每個可能結果套用同一個換算，再取加權平均。</p>
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
<p>例如 X 的變異數為 1，Y = 3X + 10 的變異數就是 9，標準差是 3。
做單位換算時也一樣：乘數在變異數裡要平方，標準差則乘上乘數的絕對值。</p>
<p>手上若只有樣本，常用以下公式估計母體變異數（n ≥ 2）：</p>
$$s^2=\frac{1}{n-1}\sum_{i=1}^n(x_i-\bar{x})^2.$$
<p>用 n−1 作分母，能在獨立同分布、有限變異數的抽樣下得到母體變異數的不偏估計。
若只是描述手上 n 筆資料的平均平方偏差，也可以除以 n，但要說清楚目的。
例如樣本 {2, 4} 的樣本平均為 3，s² = 2；這與上面「完整機率分布」的變異數 1 使用不同資訊及分母。</p>
<p><strong>大數法則（law of large numbers）</strong>說明：在獨立同分布且期望值存在等條件下，
樣本平均會隨樣本數增加而趨近母體期望值。本頁的有限值硬幣模型符合條件。
觀察平均更穩定，並不代表每一次投擲本身變得更穩定；單次變異數仍為 p(1−p)。</p>
''' + quiz('qVariance', 'PART 04 · 自我檢測',
    'X 等機率取 2 或 4，Y 等機率取 0 或 6。哪個說法正確？', [
    (False, '平均相同，所以變異數相同。', '兩者平均都是 3，但偏離平均的距離分別是 1 與 3。'),
    (True, 'Y 的變異數是 X 的 9 倍。', 'X 的變異數為 1，Y 為 9，平方使三倍的偏離對應九倍變異數。'),
    (False, 'Y 的標準差是 X 的 9 倍。', '標準差取平方根，因此 Y 的標準差是 X 的 3 倍。')]) + source(12, 'Variance') + source(17, 'Consistency of Estimators：長期穩定的例子，推導續於 p.18')

BODIES['exercises'] = ''.join([
    quiz('qEx1', 'EXERCISE 1', '公平骰子出現至少 5 點的機率是多少？', [
        (False, '1/6', '有 5 和 6 兩個符合的結果，要把兩者機率相加。'),
        (True, '1/3', '2 個結果各占 1/6，合計 2/6 = 1/3。'),
        (False, '5/6', '這是出現至多 5 點的機率；至少 5 點只包含 5 與 6。')]),
    quiz('qEx2', 'EXERCISE 2', 'X 以 0.75 的機率取 0，以 0.25 的機率取 8。E[X] 是多少？', [
        (True, '2', '0 × 0.75 + 8 × 0.25 = 2。'),
        (False, '4', '直接平均 0 和 8 忽略了兩者不同的機率。'),
        (False, '8', '8 只在四分之一的機率下出現，需乘上機率。')]),
    quiz('qEx3', 'EXERCISE 3', '通勤時間由分鐘換成秒，變異數如何換算？', [
        (False, '乘上 60', '標準差乘 60；變異數的單位是時間平方。'),
        (False, '不變', '單位換算會改變變異數的數值與單位。'),
        (True, '乘上 3600', 'Var(60X) = 60² Var(X)，變異數單位由分鐘平方換成秒平方。')]),
    quiz('qEx4', 'EXERCISE 4', '從 100 次增加到 200 次獨立公平投擲，哪件事有理論保證？', [
        (False, '這一次的比例誤差一定更小。', '某次序列仍可能暫時偏離更多，長期性質不代表每一步改善。'),
        (True, '每一次投擲的正面機率仍為 0.5。', '模型條件保持固定。樣本平均更穩定是抽樣分布的性質。'),
        (False, '累積正面數一定為 100。', '期望正面數為 100；實際次數會波動。')])])
BODIES['reference'] = table(['概念', '怎麼算／怎麼讀'], [
    ('樣本平均', '把已觀察的數值加總後除以 n。'), ('期望值', '把模型中每個可能值乘上機率後加總。'),
    ('變異數', 'E[(X−E[X])²] = E[X²] − (E[X])²。'), ('標準差', '變異數開平方根，單位與原資料相同。'),
    ('樣本變異數', '估計母體變異數時常用 Σ(xᵢ−x̄)²／(n−1)，n ≥ 2。'),
    ('大數法則', '合適抽樣條件下，樣本平均隨 n 增加而趨近期望值；不保證每一步更接近。')]) + '''
<p class="ver-note">通勤與二點分布為本站自訂算例。硬幣互動使用本站固定種子模擬（2106），
採獨立且固定機率的 Bernoulli 模型；重置會回到同一序列。正文公式與算例獨立計算，未引用課程 lab 的執行輸出。</p>
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

if __name__ == '__main__':
    apply('s1_probability', BODIES, PAGEJS)
