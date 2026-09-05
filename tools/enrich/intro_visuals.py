"""Five introductory data-reading examples; no model fitting lesson or decorative controls."""
import subprocess
from pathlib import Path

from lib import card, info_card, lab_code, lab_output, quiz, svg as _svg, viz

LAB_URL = "https://github.com/phonchi/nsysu-math524-2025/blob/main/static_files/presentations/Ch01-lab-zh.ipynb"


def svg(sid, height):
    return '<div class="w01-figure-scroll">' + _svg(sid, height) + '</div>'


def frames():
    generator = Path(__file__).resolve().parents[1] / "frames" / "gen_intro.py"
    python = Path.home() / "miniconda3/envs/m524/bin/python"
    result = subprocess.run([str(python), str(generator)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def _src(*cells):
    return '<code>Ch01-lab-zh.ipynb</code> · 儲存格 ' + '、'.join(map(str, cells))


def _quiz(name, question, correct, feedback, wrong1, fb1, wrong2, fb2):
    options = [(True, correct, feedback), (False, wrong1, fb1), (False, wrong2, fb2)]
    offset = {'Wage': 1, 'Smarket': 2, 'NCI60': 0, 'Auto': 1, 'Bikeshare': 2}[name]
    options = options[-offset:] + options[:-offset]
    return quiz('qIntro' + name, '讀圖自測 · ' + name, question,
                options)


def dataset_examples():
    wage = viz(svg('w01ivWageAge', 300) + svg('w01ivWageYear', 270) + svg('w01ivWageEdu', 320),
        [info_card('先看座標，再看分布',
         '三張圖的薪資單位都是<strong>千美元</strong>。年齡圖的灰點固定抽600人，橘線用全部3000人的4歲分箱平均；它<strong>不是lab的多項式配適線</strong>。年份圖也只畫各年平均。'),
         info_card('第一次讀箱形圖',
         '箱子下緣是第1四分位數（Q1），上緣是第3四分位數（Q3），中線是中位數。'
         '鬚延伸到Q1−1.5×IQR與Q3+1.5×IQR內最遠的觀測值（IQR＝Q3−Q1）；外面的點另外畫出，不代表輸入錯誤。'),
         info_card('不同人之間的比較',
         '各年齡、年份與教育組都是不同人的資料。看到薪資分布不同，還不能說是年齡或教育造成的。')],
        'w01ivWageStatus', '看中央趨勢，也看同組內的差異：一條平均線不能代表每個人。', '',
        provenance=('course-data', 'Wage，對照講義p31與Ch01 lab儲存格145–155；本站計算分箱平均、年份平均與Tukey箱形圖。'))
    smarket = viz(svg('w01ivSmarketBox', 320) + svg('w01ivSmarketCorr', 470),
        [info_card('箱子依當天的漲跌分組',
         'Lag1、Lag2、Lag3分別是前1、2、3個交易日的報酬（%）。每一組比較<strong>當天跌（紅）／當天漲（綠）</strong>；箱子與鬚沿用上面的定義。'),
         info_card('熱圖是什麼數字',
         '每格是兩個數值欄的Pearson相關係數，範圍−1到1；紅為負、藍為正、接近白色表示線性相關接近0。'
         '對角線比較同一欄，所以是1。Direction是類別，沒有放進這個矩陣。'),
         info_card('讀圖的界線',
         '箱子大量重疊，只表示這些單一變數沒有明顯分開兩組；不能證明完全無法預測。'
         'Today是當天報酬，與Direction同時才知道，不能拿它預測當天漲跌。')],
        'w01ivSmarketStatus', '先讀分布，再讀線性相關；預測能力還要用未見資料檢查。', '',
        provenance=('course-data', 'Smarket，對照講義p32與Ch01 lab儲存格157–162；箱形圖使用1.5IQR鬚，熱圖使用numeric_only的Pearson相關。'))
    nci = viz(svg('w01ivNci', 390),
        [info_card('一點代表一個細胞株',
         '每筆原本有6830個基因表現值，這裡壓成兩個座標方便閱讀。現在只要懂「把高維資料畫在平面上」，PCA的推導留到非監督式學習章。'),
         info_card('位置先算，顏色後加',
         '投影只用基因表現量，沒有使用癌症型別。顏色是事後對照；少於5筆的型別合稱「其他型別」，不表示它們原本是一類。'
         '部分同色點靠近，部分仍混在一起；平面也會遺失資訊。')],
        'w01ivNciStatus', '64個細胞株、6830個基因；型別未參與投影計算。', '',
        provenance=('course-data', 'NCI60，對照講義p33與Ch01 lab儲存格164–170；每個基因標準化後取前兩個主成分，最後才按型別上色。'))
    auto = viz(svg('w01ivAutoHist', 290) + svg('w01ivAutoScatter', 300),
        [info_card('單一變數與兩個變數',
         '直方圖回答「mpg通常落在哪裡」：每箱寬5 mpg，縱軸是車輛筆數。散佈圖回答「馬力與mpg如何一起變動」：一點是一輛車。'
         'mpg是每加侖可行駛的英里數，數值高表示較省油。'),
         info_card('回lab看完整pairplot',
         '這裡只取horsepower與mpg這一對。lab儲存格176另比較排氣量、車重與汽缸數；'
         '完整成對圖可幫助找出候選關係；因果判斷還需要研究設計與其他證據。')],
        'w01ivAutoStatus', '392筆車輛、8個資料欄；name是列索引。直方圖與散佈圖回答不同問題。', '',
        provenance=('course-data', 'Auto，對照講義p34與Ch01 lab儲存格172–176；全部392筆，本站直方圖畫筆數，不含lab的密度曲線。'))
    bike = viz(svg('w01ivBike', 300),
        [info_card('先讀原始資料的平均',
         '將8645筆每小時紀錄按hr（0到23時）分組，每組計算bikers的算術平均。不同小時的紀錄數可能不同。'),
         info_card('這條線呈現各小時的平均租借量',
         '這是<strong>本站EDA補充</strong>，沒有控制工作日、天氣或季節。講義p35畫的是模型中的小時效果，兩者不能互換解讀。')],
        'w01ivBikeStatus', '橫軸是一天中的小時，縱軸是該小時的平均租借量；不是同一天的24小時紀錄。', '',
        provenance=('course-data', 'Bikeshare，Ch01 lab儲存格178–179所載資料；本站依hr分組平均的EDA補充，不是講義p35的模型係數線。'))
    auto_code = lab_code(1, 175) + '\n\n' + lab_code(1, 176)
    return f'''
<p>先用五份真實資料練習讀圖：看清一點、一個箱子或一條線代表什麼，再判斷圖能回答哪個問題。</p>
<h3 id="dx-wage">Wage：薪資與年齡、年份、教育程度</h3>
<p>資料含3000位男性的薪資與人口特徵。若把wage當預測目標，這是一個迴歸問題；先看分布，還不用急著選模型。</p>
{wage}
{card('課程lab · 2004年的平均薪資', lab_code(1, 148), lab_output(1, 148), src=_src(148), note='111.16的單位是千美元，約為11.12萬美元。請在年份圖找到2004年的位置。')}
{_quiz('Wage', '教育程度較高的組，薪資中位數也較高。這張圖支持哪個說法？', '樣本中不同教育組的薪資分布不同；教育的因果效果仍須其他研究證據', '對。箱形圖比較組間與組內差異，並未控制其他因素。', '同一教育組的人薪資都相同', '不對。箱子、鬚與外面的點正是在呈現組內差異。', '多讀一個教育階段，每個人的薪資都會增加固定金額', '不對。這些是不同人的比較，且教育組之間的差距也不固定。')}
<h3 id="dx-smarket">Smarket：前幾天的報酬與當天漲跌</h3>
<p>1250個交易日、9個資料欄。目標Direction是當天漲或跌，屬於分類問題；先比較過去報酬在兩組中的分布。</p>
{smarket}
{card('課程lab · 數值欄的相關熱圖', lab_code(1, 162), None, src=_src(162), note='numeric_only=True只取數值欄。上面的熱圖讀法相同，本站另印出每格數值方便對照。')}
{_quiz('Smarket', 'Lag1的漲跌兩組箱子大量重疊，熱圖中的某些相關也接近0。下一步應如何判斷預測能力？', '這些圖沒有顯示明顯的單變數分離，仍需用未見資料評估模型', '對。箱形圖與線性相關無法排除非線性或多變數訊號。', '因此所有方法都不可能預測Direction', '不對。描述圖不能證明所有模型都沒有預測能力。', '把Today加入模型，因為它最接近Direction', '不對。Today與當天Direction同時才知道，用它預測當天漲跌會洩漏答案。')}
<h3 id="dx-nci">NCI60：把6830個基因畫成兩個座標</h3>
<p>投影使用基因表現量探索結構；資料另附的癌症型別供投影完成後上色對照，未作為訓練目標y。</p>
{nci}
{card('課程lab · 投影的輸入', lab_code(1, 169), None, src=_src(165, 169), note='X是標準化後的基因表現矩陣；fit_transform只接收X，沒有接收型別標籤。')}
{_quiz('NCI60', '圖上的一些同色點靠在一起。癌症型別在這張圖扮演什麼角色？', '投影完成後才上色，供我們對照探索出的結構', '對。位置只根據基因表現量計算；顏色不是用來訓練投影的答案。', '投影先按照癌症型別把點排在一起', '不對。計算位置時沒有傳入型別標籤。', '同色點必須全部重疊，才算正確的投影', '不對。同型別仍有差異，而且2D投影只呈現部分資訊。')}
<h3 id="dx-auto">Auto：油耗分布與馬力的關係</h3>
<p>先用直方圖看mpg的分布，再看馬力與mpg的散佈圖。這兩種圖分別回答「單一變數如何分布」與「兩個變數有什麼關係」。</p>
{auto}
{card('課程lab · 從直方圖到完整pairplot', auto_code, None, src=_src(175, 176), note=f'完整成對圖請回<a href="{LAB_URL}" target="_blank" rel="noopener">課程lab儲存格176</a>閱讀；本站保留一對關係作為入門示範。')}
{_quiz('Auto', '散佈圖中，馬力較大的車通常落在較低mpg的位置。哪個解讀合理？', '樣本中馬力與mpg呈負向關係，其他車輛特徵仍可能影響這個關係', '對。散佈圖描述觀察到的關係，不直接證明因果。', 'mpg愈低代表車愈省油', '不對。mpg是每加侖行駛英里數，愈高才表示較省油。', '直方圖的柱高就是每輛車的馬力', '不對。這張直方圖的柱高是落在該mpg區間的車輛筆數。')}
<h3 id="dx-bike">Bikeshare：一天中哪些時段租借較多？</h3>
<p>bikers是每小時的租借量，可以作為迴歸目標。現在先做原始資料的分組摘要，了解一天中的租借形狀。</p>
{bike}
{_quiz('Bikeshare', '曲線在某些小時較高，這些點代表什麼？', '跨不同日期、同一小時的租借量平均', '對。這是按hr分組的原始平均，不是某一天的紀錄或控制其他變數後的效果。', '這是講義模型控制其他變數後的小時係數', '不對。本站這條EDA補充線沒有配適模型，不能當成講義p35的係數線。', '每天到了這個小時都會出現完全相同的租借量', '不對。平均值概括許多天，每一天仍可能受天氣、工作日與季節影響。')}
'''


PAGEJS = r"""
/* Introductory EDA: all SVGs initialize without Chart.js. */
function w01ivText(s, x, y, text, attrs) {
  const node=s.add('text',Object.assign({x:x,y:y,fill:HC.tok.ink,'font-size':13,'font-family':'sans-serif'},attrs || {}));
  node.textContent=text;
  return node;
}
function w01ivAxes(id, xd, yd, title, xtitle, ytitle, h, xticks) {
  const s = HC.svg(id, {xd:xd, yd:yd, w:620, h:h, pad:{l:66,r:22,t:43,b:58}});
  s.clear();
  s.grid(xticks || 5, 4, {xtitle:xtitle, ytitle:ytitle, xdec:0, ydec:0});
  w01ivText(s,68, 22, title, {fill:HC.tok.ink, 'font-size':15, 'font-weight':600});
  return s;
}
function w01ivDots(s, data, color, radius) {
  const g = s.layer('w01iv-points');
  data.forEach(p => s.dot(p[0],p[1],{r:radius || 2.4, fill:color, cls:'w01iv-point', stroke:'none'},g));
}
function w01ivLine(s, data, color) {
  s.poly(data.map(p=>[p[0],p[1]]), {stroke:color,sw:2.6,fill:'none',cls:'w01iv-line'});
  w01ivDots(s,data,color,3.2);
}
function w01ivBox(s, b, x, width, color) {
  const a={stroke:color,sw:1.5,cls:'w01iv-box-line'};
  s.seg(x,b.lo,x,b.hi,a);
  s.seg(x-width*.65,b.lo,x+width*.65,b.lo,a);
  s.seg(x-width*.65,b.hi,x+width*.65,b.hi,a);
  s.box(x-width,b.q1,x+width,b.q3,{fill:color,stroke:color,cls:'w01iv-box'}).setAttribute('fill-opacity','.25');
  s.seg(x-width,b.med,x+width,b.med,{stroke:'#222',sw:2.2,cls:'w01iv-median'});
  b.outliers.forEach((v,i)=>s.dot(x+((i%5)-2)*width*.1,v,{r:2,fill:color,cls:'w01iv-outlier',stroke:'none'}));
}
function w01ivWageDraw() {
  const f=FRAMES_w01wage;
  let s=w01ivAxes('w01ivWageAge',[16,82],[0,340],'年齡：個別觀測與4歲分箱平均','年齡（歲）','薪資（千美元）',300,6);
  w01ivDots(s,f.scatter,'rgba(95,100,105,.35)',2);
  w01ivLine(s,f.ageCurve,'#c45e14');
  s=w01ivAxes('w01ivWageYear',[2003,2009],[0,140],'年份：各年平均薪資','年份','平均薪資（千美元）',270,6);
  w01ivLine(s,f.yearMean,'#2c3e7a');
  s=w01ivAxes('w01ivWageEdu',[-.6,4.6],[0,340],'教育程度：薪資分布','教育程度','薪資（千美元）',320,5);
  // Replace numeric x ticks with short educational categories.
  const names=['高中以下','高中','大學未畢','大學畢業','研究所'];
  s.clear();
  s.grid(4,4,{xtitle:'教育程度',ytitle:'薪資（千美元）',xfmt:()=>'',ydec:0});
  w01ivText(s,68,22,'教育程度：薪資分布',{fill:HC.tok.ink,'font-size':15,'font-weight':600});
  f.eduBox.forEach((b,i)=>{w01ivBox(s,b,i,.24,'#2c3e7a');s.txt(i,-26,names[i],{'font-size':13});});
}
function w01ivSmarketDraw() {
  const f=FRAMES_w01smarket;
  const all=f.lagBox.flatMap(b=>['Down','Up'].flatMap(k=>[b[k].lo,b[k].hi,...b[k].outliers]));
  const lim=Math.ceil(Math.max(...all.map(Math.abs)));
  const s=w01ivAxes('w01ivSmarketBox',[-.6,2.6],[-lim,lim],'過去報酬：依當天Direction分組','','過去報酬（%）',320,3);
  s.clear();s.grid(4,4,{xtitle:'紅：當天跌　　綠：當天漲',ytitle:'過去報酬（%）',xfmt:()=>'',ydec:1});
  w01ivText(s,68,22,'過去報酬：依當天Direction分組',{'font-size':15,'font-weight':600});
  f.lagBox.forEach((b,i)=>{w01ivBox(s,b.Down,i-.16,.12,'#c0392b');w01ivBox(s,b.Up,i+.16,.12,'#1a6b4a');s.txt(i,-lim*1.14,'Lag'+b.lag,{'font-size':14});});
  const h=HC.svg('w01ivSmarketCorr',{w:620,h:470});h.clear();
  w01ivText(h,90,23,'數值欄的Pearson相關（−1 到 1）',{'font-size':15,'font-weight':600});
  const n=f.corrNames.length, size=43, left=133, top=70;
  f.corrNames.forEach((name,i)=>{
    w01ivText(h,left+i*size+size/2,55,name,{'text-anchor':'middle','font-size':12});
    w01ivText(h,left-10,top+i*size+size/2+4,name,{'text-anchor':'end','font-size':13});
    f.corr[i].forEach((v,j)=>{
      const t=Math.abs(v), base=v<0?[192,57,43]:[44,62,122];
      const color='rgb('+base.map(c=>Math.round(250*(1-t)+c*t)).join(',')+')';
      h.add('rect',{x:left+j*size,y:top+i*size,width:size,height:size,fill:color,stroke:'#fff'});
      w01ivText(h,left+j*size+size/2,top+i*size+size/2+4,v.toFixed(2),{'text-anchor':'middle','font-size':12,fill:t>.55?'#fff':'#222'});
    });
  });
  w01ivText(h,left,440,'紅：負相關　　白：接近0　　藍：正相關',{'font-size':13});
}
function w01ivNciDraw() {
  const f=FRAMES_w01nci, xs=f.pts.map(p=>p.x),ys=f.pts.map(p=>p.y);
  const s=HC.svg('w01ivNci',{xd:[Math.min(...xs)-5,Math.max(...xs)+5],yd:[Math.min(...ys)-5,Math.max(...ys)+5],w:620,h:390,pad:{l:60,r:20,t:102,b:46}});
  s.clear();s.grid(5,4,{xtitle:'投影座標1',ytitle:'投影座標2',xdec:0,ydec:0});
  const groups=[...new Set(f.pts.map(p=>p.g))],pal=['#2c3e7a','#c0392b','#1a6b4a','#8e44ad','#b66c00','#167c85','#873b1a','#567b13','#777'];
  groups.forEach((name,i)=>{const x=65+(i%3)*180,y=20+Math.floor(i/3)*23;s.add('circle',{cx:x,cy:y,r:4,fill:pal[i]});w01ivText(s,x+10,y+4,name,{'font-size':12});});
  f.pts.forEach(p=>s.dot(p.x,p.y,{r:4.4,fill:pal[groups.indexOf(p.g)],stroke:'#fff',sw:1,cls:'w01iv-nci-point'}));
}
function w01ivAutoDraw() {
  const f=FRAMES_w01auto, max=Math.max(...f.hist.map(p=>p[2]));
  let s=w01ivAxes('w01ivAutoHist',[5,50],[0,Math.ceil(max/10)*10],'mpg直方圖：每箱5 mpg','mpg（英里／加侖）','車輛筆數',290,9);
  f.hist.forEach(b=>s.box(b[0],0,b[1],b[2],{fill:'#2c3e7a',stroke:'#fff',sw:1,cls:'w01iv-hist'}));
  s=w01ivAxes('w01ivAutoScatter',[40,240],[0,50],'馬力與mpg：全部392筆車輛','horsepower（馬力）','mpg（英里／加侖）',300,5);
  w01ivDots(s,f.scatter,'rgba(26,107,74,.5)',2.7);
}
function w01ivBikeDraw() {
  const f=FRAMES_w01bike, max=Math.max(...f.hourMean.map(p=>p[1]));
  const s=w01ivAxes('w01ivBike',[0,23],[0,Math.ceil(max/50)*50],'原始資料依小時平均：本站EDA補充','hr（0–23時）','平均每小時租借量',300,6);
  s.grid(6,4,{xtitle:'hr（0–23時）',ytitle:'平均每小時租借量',xfmt:()=>'',ydec:0});
  [0,4,8,12,16,20,23].forEach(hr=>w01ivText(s,s.X(hr),s.H-s.pad.b+18,String(hr),{'text-anchor':'middle'}));
  w01ivLine(s,f.hourMean,'#c45e14');
}
w01ivWageDraw();
w01ivSmarketDraw();
w01ivNciDraw();
w01ivAutoDraw();
w01ivBikeDraw();
"""
