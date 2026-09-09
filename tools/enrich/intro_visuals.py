"""Five introductory data-reading examples; no model fitting lesson or decorative controls."""
import subprocess
from pathlib import Path

from lib import card, info_card, lab_code, lab_output, quiz, svg as _svg, viz

LAB_URL = "https://github.com/phonchi/nsysu-math524/blob/main/static_files/presentations/Ch01-lab-zh.ipynb"


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
         '三張圖的薪資單位都是<strong>千美元</strong>。年齡與年份圖都畫全部3000人的觀測值，線條呈現薪資的整體趨勢。淡色區域是平均薪資的95%信賴區間：區域越寬，表示平均薪資的估計越不確定。它不表示個人薪資會落在哪裡，區間的詳細意義會在後續章節介紹。'),
         info_card('第一次讀箱形圖',
         '箱子下緣是第1四分位數（Q1），上緣是第3四分位數（Q3），中線是中位數。'
         '鬚延伸到Q1−1.5×IQR與Q3+1.5×IQR內最遠的觀測值（IQR＝Q3−Q1）；外面的點另外畫出，不代表輸入錯誤。'),
         info_card('不同人之間的比較',
         '各年齡、年份與教育組都是不同人的資料。看到薪資分布不同，還不能說是年齡或教育造成的。')],
        'w01ivWageStatus', '曲線描述平均薪資與輸入的關係；散點呈現同一年齡或年份中個人的差異。', '',
        provenance=('course-data', 'Wage，全部3000筆資料；依第一章lab的圖形繪製。'))
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
        provenance=('course-data', 'Smarket，全部1250筆資料；依第一章lab的箱形圖與相關係數圖繪製。'))
    nci = viz(svg('w01ivNci', 470) + svg('w01ivNci3', 340),
        [info_card('一點代表一個細胞株',
         '每筆原本有6830個基因表現值，兩張圖分別看第一、第二主成分與第一、第三主成分。現在只要懂「把高維資料畫在平面上」，PCA的推導留到非監督式學習章。'),
         info_card('位置先算，顏色後加',
         '投影只用基因表現量，沒有使用癌症型別。顏色保留全部14種原始型別，供事後對照。第一張圖依lab將第二主成分乘上−1；主成分符號可反轉，不改變距離或解釋變異。'
         '部分同色點靠近，部分仍混在一起；平面也會遺失資訊。')],
        'w01ivNciStatus', '64個細胞株、6830個基因；型別未參與投影計算。', '',
        provenance=('course-data', 'NCI60，64個細胞株的基因資料；依第一章lab的投影圖繪製。'))
    auto = viz(svg('w01ivAutoHist', 290) + svg('w01ivAutoJoint', 380) + svg('w01ivAutoPairs', 650),
        [info_card('單一變數與兩個變數',
         '直方圖回答「mpg通常落在哪裡」：縱軸是密度，各柱面積加總為1，橘線是核密度估計（KDE）。分箱與平滑設定沿用lab的seaborn預設值。聯合圖也畫出汽缸數與mpg各自的邊際直方圖。成對散佈圖回答「馬力與mpg如何一起變動」：一點是一輛車。'
         'mpg是每加侖可行駛的英里數，數值高表示較省油。'),
         info_card('完整成對關係',
         '成對圖比較mpg、排氣量、馬力與車重，以汽缸數上色。對角線是各汽缸組的KDE，其他格是一對變數的散佈圖；'
         '完整成對圖可幫助找出候選關係；因果判斷還需要研究設計與其他證據。')],
        'w01ivAutoStatus', '392筆車輛、8個資料欄；name是列索引。直方圖與散佈圖回答不同問題。', '',
        provenance=('course-data', 'Auto，全部392筆資料；依第一章lab的分布圖與散佈圖繪製。'))
    bike = viz(svg('w01ivBikeMonth', 300) + svg('w01ivBike', 320),
        [info_card('先看哪些月份、時段較高',
         '這兩張圖來自第四章的自行車租借例子。模型同時考慮月份、時段、是否為工作日、溫度與天氣。比較曲線高低時，假設其他條件相同；曲線越高，模型估計的租借量就越多。'),
         info_card('縱軸的0是比較基準',
         '月份圖以模型中各月份的平均水準為基準，時段圖則以各時段的平均水準為基準。正值表示高於基準，負值表示低於基準。負值不代表租借量是負數。'
         '這裡畫的是模型估計的差異，不能直接當成各月、各時段的實際平均租借量。')],
        'w01ivBikeStatus', '先比較曲線的高低，觀察哪些月份、時段的租借量較多。模型如何計算，第四章再介紹。', '',
        provenance=('course-data', 'Bikeshare，全部8645筆資料；依第四章lab的線性迴歸結果繪製。'))
    auto_code = lab_code(1, 175) + '\n\n' + lab_code(1, 176)
    return f'''
<p>先用五份真實資料練習讀圖：看清一點、一個箱子或一條線代表什麼，再判斷圖能回答哪個問題。</p>
<h3 id="dx-wage">Wage：薪資與年齡、年份、教育程度</h3>
<p>資料含3000位男性的薪資與人口特徵。若把wage當預測目標，這是一個迴歸問題；先看分布，還不用急著選模型。</p>
{wage}
{card('課程lab · 2004年的平均薪資', lab_code(1, 148), lab_output(1, 148), src=_src(148), note='111.16的單位是千美元，約為11.12萬美元。這是2004年原始樣本平均；年份圖的直線則是使用所有年份共同擬合的趨勢。')}
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
{card('課程lab · 從直方圖到完整pairplot', auto_code, None, src=_src(175, 176), note=f'上方重建相同的密度圖與成對圖；可在<a href="{LAB_URL}" target="_blank" rel="noopener">課程lab</a>操作原始程式。')}
{_quiz('Auto', '散佈圖中，馬力較大的車通常落在較低mpg的位置。哪個解讀合理？', '樣本中馬力與mpg呈負向關係，其他車輛特徵仍可能影響這個關係', '對。散佈圖描述觀察到的關係，不直接證明因果。', 'mpg愈低代表車愈省油', '不對。mpg是每加侖行駛英里數，愈高才表示較省油。', '直方圖的柱高就是每輛車的馬力', '不對。這張直方圖的柱高是密度；柱高乘上箱寬才是該區間的樣本比例。')}
<h3 id="dx-bike">Bikeshare：哪些月份、時段租借較多？</h3>
<p>bikers記錄每小時的租借量。先看下面兩張圖，找出一年中、一天中租借量較高的時候。這一章先練習讀圖，模型的詳細說明放在<a href="classification.html#poisson">第四章的Bikeshare例子</a>。</p>
{bike}
{_quiz('Bikeshare', '時段圖中，某時段的位置較高，表示什麼？', '其他條件相同時，模型估計該時段的租借量較多', '對。這張圖讓我們在其他條件相同時比較不同時段；它沒有證明時間本身造成租借量改變。', '圖上的數字就是該時段實際平均租借了幾輛車', '圖上畫的是模型估計的相對差異，已考慮月份、工作日、溫度與天氣。', '曲線低於0，表示該時段的租借量是負數', '0是比較基準；負值表示低於基準，不是租借量為負數。')}
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
  let s=w01ivAxes('w01ivWageAge',[16,82],[0,340],'年齡：全部觀測與四次多項式擬合','年齡（歲）','薪資（千美元）',300,6);
  w01ivDots(s,f.scatter,'rgba(95,100,105,.1)',2);
  w01ivFit(s,f.ageFit,'#c45e14');
  s=w01ivAxes('w01ivWageYear',[2003,2009],[0,340],'年份：全部觀測與一次線性擬合','年份','薪資（千美元）',270,6);
  w01ivDots(s,f.yearScatter,'rgba(95,100,105,.1)',2);
  w01ivFit(s,f.yearFit,'#2c3e7a');
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
function w01ivFit(s,f,color) {
  s.add('polygon',{points:f.band.map(p=>s.X(p[0])+','+s.Y(p[1])).join(' '),stroke:'none',fill:color,cls:'w01iv-band','fill-opacity':.18});
  s.poly(f.line,{stroke:color,sw:2.6,fill:'none',cls:'w01iv-line'});
}
function w01ivNciDraw() {
  const f=FRAMES_w01nci, groups=[...new Set(f.pts.map(p=>p.g))];
  const pal=['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf','#393b79','#637939','#8c6d31','#843c39'];
  ['y','z'].forEach((key,k)=>{
    const xs=f.pts.map(p=>p.x),ys=f.pts.map(p=>p[key]);
    const s=HC.svg(k?'w01ivNci3':'w01ivNci',{xd:[Math.min(...xs)-5,Math.max(...xs)+5],yd:[Math.min(...ys)-5,Math.max(...ys)+5],w:620,h:k?340:470,pad:{l:60,r:20,t:k?30:145,b:46}});
    s.clear();s.grid(5,4,{xtitle:'Z1（第一主成分）',ytitle:k?'Z3（第三主成分）':'Z2（第二主成分反向）',xdec:0,ydec:0});
    if(!k)groups.forEach((name,i)=>{const x=65+(i%3)*180,y=20+Math.floor(i/3)*23;s.add('circle',{cx:x,cy:y,r:4,fill:pal[i]});w01ivText(s,x+10,y+4,name,{'font-size':12});});
    f.pts.forEach(p=>s.dot(p.x,p[key],{r:4.4,fill:pal[groups.indexOf(p.g)],stroke:'#fff',sw:1,cls:'w01iv-nci-point'}).setAttribute('opacity','.5'));
  });
}
function w01ivAutoDraw() {
  const f=FRAMES_w01auto, max=Math.max(...f.hist.map(p=>p[2]),...f.kde.map(p=>p[1]));
  let s=w01ivAxes('w01ivAutoHist',[5,50],[0,max*1.15],'mpg密度直方圖與核密度估計','mpg（英里／加侖）','密度',290,9);
  s.clear();s.grid(9,4,{xtitle:'mpg（英里／加侖）',ytitle:'密度',xdec:0,ydec:2});
  w01ivText(s,68,22,'mpg密度直方圖與核密度估計',{'font-size':15,'font-weight':600});
  f.hist.forEach(b=>s.box(b[0],0,b[1],b[2],{fill:'#2c3e7a',stroke:'#fff',sw:1,cls:'w01iv-hist'}));
  s.poly(f.kde,{stroke:'#c45e14',sw:2.6,fill:'none',cls:'w01iv-line'});
  s=HC.svg('w01ivAutoJoint',{w:620,h:380});s.clear();
  const px=v=>65+(v-2.5)/6*415,py=v=>310-(v-5)/45*215;
  s.add('rect',{x:65,y:95,width:415,height:215,fill:'none',stroke:HC.tok.muted});
  f.pairData.forEach(r=>s.add('circle',{cx:px(r[4]),cy:py(r[0]),r:2.5,fill:'#2c3e7a',opacity:.45}));
  const mx=Math.max(...f.jointX.map(b=>b[2])),my=Math.max(...f.jointY.map(b=>b[2]));
  f.jointX.forEach(b=>s.add('rect',{x:px(b[0]),y:85-b[2]/mx*55,width:px(b[1])-px(b[0]),height:b[2]/mx*55,fill:'#2c3e7a',stroke:'#fff'}));
  f.jointY.forEach(b=>s.add('rect',{x:490,y:py(b[1]),width:b[2]/my*70,height:py(b[0])-py(b[1]),fill:'#2c3e7a',stroke:'#fff'}));
  [3,4,5,6,8].forEach(v=>w01ivText(s,px(v),332,String(v),{'text-anchor':'middle'}));
  [10,20,30,40].forEach(v=>w01ivText(s,55,py(v)+4,String(v),{'text-anchor':'end'}));
  w01ivText(s,180,360,'cylinders（汽缸數）');w01ivText(s,12,205,'mpg');w01ivText(s,70,18,'聯合散佈圖與邊際筆數直方圖',{'font-size':15});
  s=HC.svg('w01ivAutoPairs',{w:620,h:650});s.clear();
  const pal=['#440154','#3b528b','#21918c','#5ec962','#fde725'];
  f.pairGroups.forEach((g,i)=>{s.add('circle',{cx:75+i*100,cy:20,r:4,fill:pal[i]});w01ivText(s,85+i*100,24,g+' 汽缸',{'font-size':11});});
  const ranges=f.pairColumns.map((_,j)=>{const a=f.pairData.map(r=>r[j]);return [Math.min(...a),Math.max(...a)];});
  for(let y=0;y<4;y++)for(let x=0;x<4;x++){
    const l=68+x*133,t=48+y*143,w=122,h=126,xd=f.pairLimits[y][x].x,yd=f.pairLimits[y][x].y;
    const X=v=>l+(v-xd[0])/(xd[1]-xd[0])*w,Y=v=>t+h-(v-yd[0])/(yd[1]-yd[0])*h;
    s.add('rect',{x:l,y:t,width:w,height:h,fill:'none',stroke:HC.tok.muted,'stroke-width':.5});
    if(x===y){
      const polys=f.pairKdes[x],low=xd[0],high=xd[1],peak=Math.max(...polys.flatMap(a=>a.map(p=>p[1])));
      polys.forEach((a,i)=>s.add('polygon',{points:a.map(p=>(l+(p[0]-low)/(high-low)*w)+','+(t+h-p[1]/peak*h)).join(' '),fill:pal[pal.length-1-i],opacity:.25,stroke:pal[pal.length-1-i],'stroke-width':1}));
    }else f.pairData.forEach(r=>s.add('circle',{cx:X(r[x]),cy:Y(r[y]),r:1.5,fill:pal[f.pairGroups.indexOf(r[4])],opacity:.45}));
    if(y===3){w01ivText(s,l+w/2,t+h+16,f.pairColumns[x],{'text-anchor':'middle','font-size':11});w01ivText(s,l,t+h+32,xd[0].toFixed(0),{'font-size':10});w01ivText(s,l+w,t+h+32,xd[1].toFixed(0),{'font-size':10,'text-anchor':'end'});}
    if(x===0){w01ivText(s,19,t+h/2,f.pairColumns[y],{'text-anchor':'middle','font-size':11,transform:'rotate(-90 19 '+(t+h/2)+')'});if(y!==x){w01ivText(s,62,t+10,yd[1].toFixed(0),{'text-anchor':'end','font-size':9});w01ivText(s,62,t+h,yd[0].toFixed(0),{'text-anchor':'end','font-size':9});}}
  }
}
function w01ivBikeDraw() {
  const f=FRAMES_w01bike;
  [['w01ivBikeMonth',f.monthCoefs,'月份','月份',300],['w01ivBike',f.hourCoefs,'小時（0–23時）','時段',320]].forEach(([id,values,label,title,height])=>{
    const isMonth=id==='w01ivBikeMonth';
    const s=w01ivAxes(id,[0,values.length-1],[Math.floor(Math.min(...values)/20)*20,Math.ceil(Math.max(...values)/20)*20],title+'：租借量的相對差異',label,'租借量差異',height,6);
    w01ivLine(s,values.map((v,i)=>[i,v]),'#2c3e7a');
    if(isMonth){s.clear();s.grid(6,4,{xtitle:'月份',ytitle:'租借量差異',xfmt:()=>'',ydec:0});w01ivText(s,68,22,title+'：租借量的相對差異',{'font-size':15});w01ivLine(s,values.map((v,i)=>[i,v]),'#2c3e7a');values.forEach((_,i)=>w01ivText(s,s.X(i),s.H-s.pad.b+18,String(i+1),{'text-anchor':'middle','font-size':12}));}
    s.seg(0,0,values.length-1,0,{stroke:HC.tok.muted,sw:1,cls:'w01iv-zero'});
    w01ivText(s,s.pad.l-8,s.Y(0)+4,'0',{'text-anchor':'end','font-size':12,fill:HC.tok.muted});
  });
}
w01ivWageDraw();
w01ivSmarketDraw();
w01ivNciDraw();
w01ivAutoDraw();
w01ivBikeDraw();
"""
