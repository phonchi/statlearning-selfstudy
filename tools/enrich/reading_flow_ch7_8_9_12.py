"""本組閱讀分層。只包裝原始片段，不重寫 Lab 程式、輸出或既有錨點。"""
import re
from html import unescape
from html.parser import HTMLParser
from lib import detail

VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class Blocks(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source=source; self.lines=[0]
        for m in re.finditer('\n',source): self.lines.append(m.end())
        self.stack=[];self.items=[];self.current=None
        protected=[(m.start(),m.end()) for m in re.finditer(r'<pre\b.*?</pre>',source,re.S)]
        def mask(m):
            if any(a<m.end() and b>m.start() for a,b in protected):return m.group()
            return ''.join('\n' if c=='\n' else 'm' for c in m.group())
        masked=re.sub(r'\$\$.*?\$\$|\$[^$]*?\$',mask,source,flags=re.S)
        self.feed(masked);self.close()
        if self.stack: raise ValueError('Unclosed source tags: '+str(self.stack))
        self.items.sort(key=lambda x:x['a'])
    def pos(self):
        line,col=self.getpos();return self.lines[line-1]+col
    def handle_starttag(self,tag,attrs):
        a=self.pos();b=a+len(self.get_starttag_text())
        if not self.stack:self.current={'a':a,'b':b,'tag':tag,'attrs':dict(attrs)}
        if tag not in VOID:self.stack.append(tag)
        elif not self.stack:self.items.append(self.current);self.current=None
    def handle_startendtag(self,tag,attrs):
        if not self.stack:
            a=self.pos();self.items.append({'a':a,'b':a+len(self.get_starttag_text()),'tag':tag,'attrs':dict(attrs)})
    def handle_endtag(self,tag):
        if tag in VOID:return
        if not self.stack or self.stack[-1]!=tag:raise ValueError('Unexpected end tag '+tag+' '+str(self.stack[-4:]))
        self.stack.pop()
        if not self.stack:
            self.current['b']=self.source.index('>',self.pos())+1;self.items.append(self.current);self.current=None
    def handle_data(self,data):
        if not self.stack and data.strip():
            a=self.pos();self.items.append({'a':a,'b':a+len(data),'tag':'text','attrs':{}})
    def raw(self,n):return self.source[n['a']:n['b']]

def words(s):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]+>',' ',s))).strip()
def klass(n,c):
    classes=n['attrs'].get('class','').split()
    return c in classes or (c=='viz-panel' and 'viz-layout' in classes)
def quiz(n,raw,q):return klass(n,'quiz-box') and f'id="{q}Options"' in raw

def wrap_range(body,pid,title,start=None,end=None):
    """Bounds are predicates on direct children. None means fragment edge."""
    p=Blocks(body);nodes=p.items
    a=0 if start is None else next((i for i,n in enumerate(nodes) if start(n,p.raw(n))),None)
    if a is None:raise ValueError('Missing start: '+pid)
    b=len(nodes) if end is None else next((i for i in range(a+1,len(nodes)) if end(nodes[i],p.raw(nodes[i]))),None)
    if b is None:raise ValueError('Missing end: '+pid)
    lo=0 if start is None else nodes[a]['a'];hi=len(body) if b==len(nodes) else nodes[b]['a']
    return body[:lo]+detail(pid,title,body[lo:hi])+body[hi:]

def heading(name):return lambda n,r:n['tag'] in ('h3','h4') and words(r)==name
def contains(s):return lambda n,r:s in words(r)
def cls(c):return lambda n,r:klass(n,c)
def qid(q):return lambda n,r:quiz(n,r,q)

def collect(body,pid,title,predicate):
    """Move selected whole direct-child units into one detail at the first unit."""
    p=Blocks(body);chosen=[n for n in p.items if predicate(n,p.raw(n))]
    if not chosen:return body
    content='\n'.join(p.raw(n) for n in chosen);first=chosen[0]['a']
    for n in reversed(chosen):body=body[:n['a']]+body[n['b']:]
    return body[:first]+detail(pid,title,content)+body[first:]

def labs(body,pid):
    return collect(body,pid,'Python 實作與完整輸出',lambda n,r:klass(n,'deck-extra') or (n['tag'] in ('h3','h4') and '講義完整實作' in words(r)))

def tables(body,pid,title,extra_quiz=None):
    return collect(body,pid,title,lambda n,r: (n['tag']=='div' and '<table' in r and not klass(n,'viz-panel')) or (extra_quiz and quiz(n,r,extra_quiz)))

def one_viz(body,pid,title,canvas):
    return collect(body,pid,title,lambda n,r:klass(n,'viz-panel') and f'id="{canvas}"' in r)

def finish(bodies,prefix):
    for sec in list(bodies):
        if sec in ('reference','exercises'):continue
        bodies[sec]=labs(bodies[sec],f'{prefix}-detail-{sec}-lab')
    # The common template owns the bibliography, quiz bank and flashcard scaffold.
    bodies['reference']=detail(f'{prefix}-detail-reference','完整比較表、公式與實測結果',bodies['reference'])
    bodies['exercises']=detail(f'{prefix}-detail-exercises','進一步練習：計算與推理題',bodies['exercises'])


def nonlin(b):
    b['prologue']=tables(b['prologue'],'w08-detail-method-table','比較各種方法的彈性、邊界與調整參數')
    b['poly']=wrap_range(b['poly'],'w08-detail-poly-ci','計算擬合曲線的標準誤與信賴區間',contains('信賴區間怎麼來的'),cls('viz-panel'))
    b['poly']=wrap_range(b['poly'],'w08-detail-logit-ci','機率的信賴區間：logit 轉換與算例',heading('從 logit 的信賴區間回到機率'))
    b['step']=wrap_range(b['step'],'w08-detail-step-interaction','延伸：切段後的交互作用',heading('用切段建立可解讀的交互作用'))
    b['basis']=one_viz(b['basis'],'w08-detail-basis-sandbox','操作比較：勾選基底、組合曲線','w08basisFn')
    b['splines']=wrap_range(b['splines'],'w08-detail-spline-general','一次樣條、一般次數與自由度計算',heading('一次樣條與一般次數'))
    b['splines']=tables(b['splines'],'w08-detail-spline-count','比較連續性限制與參數個數')
    b['natural']=wrap_range(b['natural'],'w08-detail-natural-basis','深入基底：自然樣條與 B-spline 的計算',heading('自然樣條與 B-spline 基底'))
    b['smooth']=wrap_range(b['smooth'],'w08-detail-smoothing-computation','深入計算：平滑矩陣、交叉驗證與 IRLS',heading('平滑矩陣與邏輯斯平滑'))
    b['smooth']=wrap_range(b['smooth'],'w08-detail-smoothing-df','有效自由度與留一法的完整公式',contains('既然每個點都是節點'),cls('viz-panel'))
    b['loess']=one_viz(b['loess'],'w08-detail-lowess-lab-plot','課程資料比較：兩個跨距的 LOWESS 曲線','w08lowessLab')
    b['loess']=wrap_range(b['loess'],'w08-detail-local-calculation','局部加權擬合的算例與多變數延伸',heading('局部加權擬合的一次計算'))
    b['loess']=tables(b['loess'],'w08-detail-span-table','對照不同跨距的有效自由度')
    # The appended blocks share one coherent implementation/interpretation extension.
    b['gam']=wrap_range(b['gam'],'w08-detail-gam-geometry','延伸：二維平滑、效果圖與部分迴歸',heading('二維平滑與效果圖的讀法'),heading('讓加法成分可識別的 backfitting'))
    b['gam']=wrap_range(b['gam'],'w08-detail-gam-backfit','完整演算法：可識別的 backfitting',heading('讓加法成分可識別的 backfitting'),heading('薄板樣條的完整表示'))
    b['gam']=wrap_range(b['gam'],'w08-detail-gam-thinplate','薄板樣條的完整式與效果圖算例',heading('薄板樣條的完整表示'))
    b['gam']=collect(b['gam'],'w08-detail-backfit-intro','計算加法成分：偏殘差如何輪流更新',lambda n,r:klass(n,'info-box') and '逆向擬合在做什麼' in words(r))
    finish(b,'w08')
    return ''


def trees(b):
    b['prologue']=tables(b['prologue'],'w09-detail-tree-compare','比較樹與線性模型的性質')
    b['grow']=wrap_range(b['grow'],'w09-detail-split-search','深入搜尋：連續切點、類別分割與樹演算法',heading('連續切點與類別分割如何搜尋'))
    # Candidate-count question belongs with the detailed search, not the core reading quiz.
    p=Blocks(b['grow']);q=next(n for n in p.items if quiz(n,p.raw(n),'qGrow'));raw=p.raw(q)
    b['grow']=b['grow'][:q['a']]+b['grow'][q['b']:]
    marker='id="w09-detail-split-search"'
    parser=Blocks(b['grow']);unit=next(n for n in parser.items if marker in parser.raw(n));r=parser.raw(unit);r=r.rsplit('</div></details>',1)[0]+raw+'</div></details>';b['grow']=b['grow'][:unit['a']]+r+b['grow'][unit['b']:]
    b['prune']=wrap_range(b['prune'],'w09-detail-prune-compute','計算 weakest-link 臨界值與剪枝路徑',heading('weakest-link 的臨界值'))
    b['classtree']=tables(b['classtree'],'w09-detail-impurity-calculation','算例：同樣錯誤率，為何分裂選擇不同？')
    b['why']=collect(b['why'],'w09-detail-voting-probability','深入投票：二項機率與分類器多樣性',lambda n,r:klass(n,'viz-panel') or (n['tag']=='text' and '$$' in r) or quiz(n,r,'qVote'))
    # Keep the ordinary residual-learning widget; AdaBoost is an optional complete unit.
    b['boosting']=wrap_range(b['boosting'],'w09-detail-adaboost-demo','延伸：AdaBoost 如何重新分配權重',heading('AdaBoost：不改目標，改權重'),heading('講義完整實作：Boston 上的梯度提升'))
    b['boosting']=wrap_range(b['boosting'],'w09-detail-gradient-general','一般負梯度、AdaBoost 尺度與不同損失',heading('從擬合殘差到一般負梯度'))
    b['boosting']=tables(b['boosting'],'w09-detail-boost-parameters','對照樹數、學習率與深度')
    b['rf']=wrap_range(b['rf'],'w09-detail-extra-trees','延伸：Extra-trees、抽樣層次與變異公式',heading('Extra-trees、random subspaces 與 random patches'))
    b['modern']=wrap_range(b['modern'],'w09-detail-modern-comparison','套件實作、超參數與實測比較',None,heading('XGBoost：本輪的目標、葉值與分裂增益'))
    b['modern']=wrap_range(b['modern'],'w09-detail-xgboost-math','XGBoost 的完整目標、葉值與分裂增益',heading('XGBoost：本輪的目標、葉值與分裂增益'),heading('大型資料如何減少搜尋量'))
    b['modern']=wrap_range(b['modern'],'w09-detail-boost-engineering','搜尋加速、CatBoost 順序與 DART',heading('大型資料如何減少搜尋量'))
    b['modern']=r'<p>XGBoost、LightGBM 與 CatBoost 都以提升樹為基礎，分別加入正則化、搜尋加速或類別處理。選擇時先看資料型態、運算成本與驗證表現；以下可依需要查完整方法和實作。</p>'+b['modern']
    b['stacking']=wrap_range(b['stacking'],'w09-detail-importance','如何讀變數重要度與置換重要度',heading('變數重要度：輔助解讀集成模型'),heading('Stacking：不用投票，訓練一個模型來合併'))
    b['stacking']=wrap_range(b['stacking'],'w09-detail-stacking','Stacking 的折外預測與完整實作',heading('Stacking：不用投票，訓練一個模型來合併'),heading('BART：貝氏版的加法樹'))
    b['stacking']=wrap_range(b['stacking'],'w09-detail-bart','BART 的模型、後驗更新與實作',heading('BART：貝氏版的加法樹'),qid('qStack'))
    b['stacking']=wrap_range(b['stacking'],'w09-detail-bart-posterior','BART 的完整更新與葉值推導',heading('BART 每一輪究竟更新什麼'))
    # Merge the two BART pieces into one sibling entry rather than two near-duplicate summaries.
    b['stacking']=collect(b['stacking'],'w09-detail-stacking-check','自我檢查：折外預測與重要度',lambda n,r:quiz(n,r,'qStack'))
    b['stacking']=r'<p>集成模型還能用重要度輔助解讀，也能再學一個模型合併預測。重要度不代表因果；stacking 的合併器必須使用折外預測。BART 則以貝氏抽樣表示樹與預測的不確定性。</p>'+b['stacking']
    finish(b,'w09')
    return """\nHC.onDetail('w09-detail-adaboost-demo', {close: () => {
  if (w09adaPlayer) w09adaPlayer.stop();
  const unit=document.getElementById('w09-detail-adaboost-demo');
  const button=unit?.querySelector('button.btn-play');
  if (button) { button.textContent='▶ 開始'; button.setAttribute('aria-pressed','false'); }
}});\n"""


def svm(b):
    b['prologue']=wrap_range(b['prologue'],'w10-detail-distance','計算：點到超平面的距離',heading('點到超平面的距離'),qid('qHyp'))
    b['maxmargin']=wrap_range(b['maxmargin'],'w10-detail-hard-dual','完整硬邊界問題：primal、dual、KKT 與算例',heading('把最大邊界寫成可求解的問題'),qid('qMax'))
    b['maxmargin']=wrap_range(b['maxmargin'],'w10-detail-perceptron','延伸：從感知器到最大邊界',heading('從感知器到最大邊界'))
    b['soft']=wrap_range(b['soft'],'w10-detail-soft-dual','完整軟邊界對偶：限制、KKT、截距與算例',heading('軟邊界：為什麼乘子多了一個上界？'),qid('qSoft'))
    b['soft']=tables(b['soft'],'w10-detail-slack-table','對照違反量、分類結果與支持向量')
    b['hinge']=wrap_range(b['hinge'],'w10-detail-loss-normalization','完整尺度對照：slack、懲罰、預算與標籤',heading('把違反量消去：損失、懲罰與預算'),qid('qHinge'))
    b['hinge']=tables(b['hinge'],'w10-detail-hinge-cases','對照分數的位置與支持向量')
    b['kernel']=wrap_range(b['kernel'],'w10-detail-kernel-validity','深入核函數：Gram 矩陣與半正定條件',heading('可用的核與完整 Gram 矩陣'),heading('用決策分數畫 ROC'))
    b['kernel']=wrap_range(b['kernel'],'w10-detail-score-roc','算例：用 SVM 決策分數畫 ROC',heading('用決策分數畫 ROC'),qid('qKern'))
    b['multiclass']=tables(b['multiclass'],'w10-detail-multiclass-table','比較 OVO／OVA 的規模、資料與決策')
    b['vslogit']=wrap_range(b['vslogit'],'w10-detail-svr','延伸：SVR 的管狀損失與完整對偶',heading('延伸：支持向量迴歸的管狀損失'),heading('從公式選擇實作'))
    b['vslogit']=wrap_range(b['vslogit'],'w10-detail-solvers','大規模求解、隨機 Fourier 特徵與核近似',heading('從公式選擇實作'),heading('核 Ridge 與單類別邊界'))
    b['vslogit']=wrap_range(b['vslogit'],'w10-detail-kernel-extensions','延伸：核 Ridge 與單類別 SVM',heading('核 Ridge 與單類別邊界'),qid('qVs'))
    b['vslogit']=tables(b['vslogit'],'w10-detail-model-comparison','完整對照：SVM、邏輯斯迴歸與 LDA')
    finish(b,'w10')
    return ''


def unsup(b):
    for sec,name,title in [
      ('pca','主成分的完整條件與可重算例子','PCA 的完整條件、矩陣算例與特徵推導'),
      ('lowrank','最佳低秩近似的解與不唯一性','最佳低秩近似、因子不唯一性與 SVD 計算'),
      ('scaling','從共變異數到白化','深入計算：共變異數、白化與零特徵值'),
      ('completion','矩陣補全要驗證什麼','補值驗證、可識別性算例與單調性推導'),
      ('kmeans','一輪 K-means 與停止條件','計算一輪 K-means：初始化、停止條件與證明'),
      ('hclust','Ward 與階層假設','深入階層方法：Ward 算例、分裂式與 MST'),
    ]:b[sec]=wrap_range(b[sec],f'w07-detail-{sec}-advanced',title,heading(name))
    b['pve']=wrap_range(b['pve'],'w07-detail-pca-rank-selection','深入選維度：驗證目標與資訊準則',heading('用什麼目的選 PCA 的維度'))
    b['practical']=wrap_range(b['practical'],'w07-detail-cluster-methods-intro','延伸方法的概觀與使用情境',heading('密度分群：DBSCAN、OPTICS 與 HDBSCAN'),heading('從密度鄰域到 HDBSCAN 的階層'))
    b['practical']=wrap_range(b['practical'],'w07-detail-density','密度分群的完整流程：DBSCAN、HDBSCAN 與 Mean shift',heading('從密度鄰域到 HDBSCAN 的階層'),heading('高斯混合模型與 EM 的完整更新'))
    b['practical']=wrap_range(b['practical'],'w07-detail-mixtures','混合模型：EM、責任值與變分貝氏',heading('高斯混合模型與 EM 的完整更新'),heading('譜分群：從圖走到可分群的座標'))
    b['practical']=wrap_range(b['practical'],'w07-detail-spectral','譜分群的圖、嵌入與數學條件',heading('譜分群：從圖走到可分群的座標'),heading('混合型資料的距離與可驗證的群'))
    b['practical']=wrap_range(b['practical'],'w07-detail-mixed-clustering','混合資料、其他分群方法與評估指標',heading('混合型資料的距離與可驗證的群'))
    b['manifold']=wrap_range(b['manifold'],'w07-detail-manifold-overview','延伸方法與調整參數的概觀',heading('t-SNE 的目標與調整參數'),heading('SNE、crowding 與 t-SNE 的完整機率'))
    b['manifold']=wrap_range(b['manifold'],'w07-detail-tsne-algorithm','t-SNE 完整演算法：機率、perplexity、梯度與算例',heading('SNE、crowding 與 t-SNE 的完整機率'),heading('其他流形方法各自保留什麼'))
    b['manifold']=wrap_range(b['manifold'],'w07-detail-manifold-extensions','其他流形方法、張量、自監督與新資料映射',heading('其他流形方法各自保留什麼'))
    # Keep PCA/centroid/neighborhood demonstrations and their conceptual checks visible.
    finish(b,'w07')
    return ''

ROUTES={'beyond_linearity':nonlin,'tree_based_methods':trees,'support_vector_machines':svm,'unsupervised_learning':unsup}

def add_before(body,pid,summary):
    p=Blocks(body);n=next(n for n in p.items if n['attrs'].get('id')==pid)
    return body[:n['a']]+summary+body[n['a']:]

def condense(body,pid,title,start,end,summary):
    return add_before(wrap_range(body,pid,title,start,end),pid,summary)

def merge_entries(body,ids,pid,title,extra=None):
    p=Blocks(body);ns=[n for n in p.items if n['attrs'].get('id') in ids or (extra and extra(n,p.raw(n)))]
    if not ns:raise ValueError('No entries to merge '+pid)
    chunks=[]
    for n in ns:
        raw=p.raw(n)
        if n['attrs'].get('id') in ids:
            raw=raw.split('<div class="detail-body">',1)[1].rsplit('</div></details>',1)[0]
        chunks.append(raw)
    first=ns[0]['a']
    for n in reversed(ns):body=body[:n['a']]+body[n['b']:]
    return body[:first]+detail(pid,title,'\n'.join(chunks))+body[first:]

def polish(stem,b):
    if stem=='beyond_linearity':
        b['poly']=collect(b['poly'],'w08-detail-poly-coefficients','讀懂多項式係數與基底選擇',lambda n,r:n['tag']=='p' and '係數照樣用最小平方估' in words(r))
        b['poly']=add_before(b['poly'],'w08-detail-poly-coefficients','<p>多項式對係數仍是線性的。解讀時看整條擬合曲線：個別係數會隨基底選擇改變，曲線與預測才是這裡的重點。</p>')
        b['poly']=merge_entries(b['poly'],['w08-detail-poly-coefficients','w08-detail-poly-ci'],'w08-detail-poly-calculation','深入計算：係數、基底與信賴區間')
        b['step']=condense(b['step'],'w08-detail-step-coding','階梯函數的完整編碼與係數解讀',contains('做法是選切點'),cls('viz-panel'),r'<p>選好切點後，每段各給一個常數；只有這個預測變數、以平方損失擬合時，該常數就是段內反應的平均。例如把年齡分成四段，就得到四個段內平均。</p>')
        b['basis']=merge_entries(b['basis'],['w08-detail-basis-sandbox'],'w08-detail-basis-sandbox','操作比較：勾選基底、組合曲線',extra=lambda n,r:n['tag']=='p' and '下面的元件讓你組合不同基底' in words(r))
        b['splines']=condense(b['splines'],'w08-detail-spline-constraints','分段係數與連續性限制如何計數',None,cls('viz-panel'),r'<p>樣條在不同區段使用低次多項式，再於節點上接合。三次樣條要求函數值、一階與二階導數連續，因此能彎曲而不出現斷裂或折角；K 個內部節點、含截距時共有 K＋4 個自由度。</p>')
        b['splines']=wrap_range(b['splines'],'w08-detail-truncated-power','用截斷冪基底實作三次樣條',contains('那要怎麼真的把約束擬合進去'),cls('qa-box'))
        b['splines']=merge_entries(b['splines'],['w08-detail-spline-constraints','w08-detail-truncated-power','w08-detail-spline-count','w08-detail-spline-general'],'w08-detail-spline-calculation','完整計算：樣條基底、連續性與自由度')
        b['loess']=merge_entries(b['loess'],['w08-detail-span-table','w08-detail-lowess-lab-plot'],'w08-detail-lowess-lab-plot','課程 LOWESS、跨距與實作差異',extra=lambda n,r:n['tag']=='p' and '上表的 16.4 與 5.3' in words(r))
        b['gam']=merge_entries(b['gam'],['w08-detail-backfit-intro','w08-detail-gam-backfit'],'w08-detail-gam-backfit','完整演算法：偏殘差與可識別的 backfitting')
        b['gam']=merge_entries(b['gam'],['w08-detail-gam-geometry','w08-detail-gam-thinplate'],'w08-detail-gam-thinplate','延伸：薄板樣條、效果圖與部分迴歸')
        b['gam']=collect(b['gam'],'w08-detail-gam-classification','分類 GAM 的稀有事件算例',lambda n,r:n['tag']=='p' and 'ISLP 圖 7.13' in words(r))
        b['prologue']=b['prologue'].replace('本章依照上表介紹各種方法','本章依照這些路線介紹各種方法')
    elif stem=='tree_based_methods':
        b['prune']=condense(b['prune'],'w09-detail-prune-path','剪枝路徑、折內演算法與 Lab 實作差異',lambda n,r:klass(n,'info-box') and 'α 一動' in words(r),cls('viz-panel'),'<p>用交叉驗證比較不同複雜度，選好參數後再以完整訓練資料擬合。下方互動可觀察剪枝如何改變樹的大小與誤差。</p>')
        b['prune']=merge_entries(b['prune'],['w09-detail-prune-path','w09-detail-prune-compute'],'w09-detail-prune-compute','完整剪枝：臨界值、路徑與交叉驗證')
        b['why']=merge_entries(b['why'],['w09-detail-voting-probability'],'w09-detail-voting-probability','深入投票：二項機率、獨立條件與算例',extra=lambda n,r:(n['tag']=='p' and ('二項分' in words(r) or '1000 個只有 51%' in words(r))) or (klass(n,'info-box') and '投票公式的獨立性假設' in words(r)))
        b['why']=add_before(b['why'],'w09-detail-voting-probability','<p>最簡單的做法是讓每個分類器投一票，票多的類別勝出。有效的集成需要成員有一定預測能力，也要讓錯誤不完全重疊；模型多並不自動代表預測更好。</p>')
        b['rf']=condense(b['rf'],'w09-detail-rf-correlation','平均預測的變異與相關性公式',None,contains('如果資料裡有一個'),'<p>Bagging 的樹若經常依賴同一組特徵，預測也容易一起出錯；單靠增加樹數，無法消除這部分共同變動。</p>')
        b['rf']=merge_entries(b['rf'],['w09-detail-rf-correlation','w09-detail-extra-trees'],'w09-detail-extra-trees','深入隨機化：相關性公式、Extra-trees 與抽樣層次')
        b['stacking']=merge_entries(b['stacking'],['w09-detail-bart','w09-detail-bart-posterior'],'w09-detail-bart','BART 的完整模型、實作與後驗更新')
    elif stem=='support_vector_machines':
        b['maxmargin']=wrap_range(b['maxmargin'],'w10-detail-margin-normalization','最大化間隔的尺度與限制',contains('寫成最佳化問題'),cls('viz-panel'))
        b['maxmargin']=merge_entries(b['maxmargin'],['w10-detail-margin-normalization','w10-detail-hard-dual'],'w10-detail-hard-dual','完整硬邊界問題：primal、dual、KKT 與算例',extra=lambda n,r:n['tag']=='p' and '順便說一句' in words(r))
        b['soft']=wrap_range(b['soft'],'w10-detail-budget-slack','預算形式與違反量的完整定義',lambda n,r:n['tag']=='text' and r'\epsilon_1' in r,lambda n,r:klass(n,'info-box') and '先辨認 C' in words(r))
        b['soft']=merge_entries(b['soft'],['w10-detail-budget-slack','w10-detail-slack-table','w10-detail-soft-dual'],'w10-detail-soft-dual','完整軟邊界對偶：slack、限制、KKT 與截距')
        # Keep the notation warning before the detail, so the C slider is self-contained.
        b['soft']=add_before(b['soft'],'w10-detail-soft-dual',r'<p>下方互動採用 SVC 的懲罰權重 C：較大 C 更重視減少違反間隔的損失；較小 C 容許更多違反，以換取較寬的間隔。正文用 B 表示違反量預算，兩者沒有普遍的倒數換算。</p>')
        b['hinge']=condense(b['hinge'],'w10-detail-hinge-objective','展開 hinge 目標與 λ／C 記號',contains('前面把支持向量分類器'),contains('現在看那條曲線'),r'<p>Hinge loss 以帶標籤分數 $y f(x)$ 衡量違反間隔的程度：</p>$$\ell(y,f(x))=\max(0,1-yf(x)).$$<p>例如分數為 0.5 時損失為 0.5，分數超過 1 後損失為 0；間隔上的折角仍可能對解有影響。擬合時把這個損失與係數的平方懲罰相加。</p>')
        b['hinge']=merge_entries(b['hinge'],['w10-detail-hinge-objective','w10-detail-loss-normalization'],'w10-detail-loss-normalization','完整目標與尺度：hinge、slack、預算及標籤')
        b['kernel']=wrap_range(b['kernel'],'w10-detail-polynomial-map','算例：二次映射的內積與核函數',contains('講義第 24 頁的例子'),cls('viz-panel'))
        b['kernel']=merge_entries(b['kernel'],['w10-detail-polynomial-map','w10-detail-kernel-validity'],'w10-detail-kernel-validity','深入核函數：特徵映射、Gram 矩陣與合法條件')
        # Full predictor stays outside its mathematical-validity expansion.
        b['kernel']=add_before(b['kernel'],'w10-detail-kernel-validity',r'<p>核 SVM 的預測可以寫成 $f(x)=b+\sum_{i\in S}\alpha_i y_iK(x_i,x)$，其中 S 是此解使用的支持向量、$\alpha_i$ 是其非負權重。核值代表特徵空間的內積；使用者不必把所有擴張特徵實際列出。</p>')
        b['vslogit']=condense(b['vslogit'],'w10-detail-loss-compare','比較兩個模型的完整損失與懲罰',contains('拆解的關鍵'),lambda n,r:n['attrs'].get('id')=='w10-detail-model-comparison',r'<p>SVM 與加了平方懲罰的邏輯斯迴歸，都平衡分類損失和模型複雜度。Hinge loss 在足夠大的正確分數後變成 0；logistic loss 則平滑下降。因此兩者常能給出相近分類結果，但機率輸出與校準需求不同。</p>')
        b['vslogit']=merge_entries(b['vslogit'],['w10-detail-loss-compare','w10-detail-model-comparison'],'w10-detail-model-comparison','完整對照：SVM、邏輯斯損失與 LDA')
    elif stem=='unsupervised_learning':
        b['prologue']=wrap_range(b['prologue'],'w07-detail-other-goals','延伸用途：密度估計與異常偵測',heading('降維、分群以外的兩個目標'))
        b['pca']=condense(b['pca'],'w07-detail-pca-optimization','最大變異的完整限制式與負荷量計算',contains('那些係數'),contains('下面這個元件'),r'<p>係數稱為負荷量，合起來描述投影軸；把每筆置中資料投影到這個軸，所得座標稱為得分。限制方向長度為 1，才能公平比較不同方向的變異。</p>')
        b['pca']=merge_entries(b['pca'],['w07-detail-pca-optimization','w07-detail-pca-advanced'],'w07-detail-pca-advanced','完整 PCA：限制式、矩陣算例與特徵推導')
        b['pca']=b['pca'].replace('把上面那個最佳化問題「用手轉一遍」','把「找最大變異方向」這件事用手轉一遍')
        b['lowrank']=condense(b['lowrank'],'w07-detail-lowrank-objective','低秩最佳化與變異分解的完整式',contains('把「最近」寫成最佳化'),lambda n,r:klass(n,'info-box'),r'<p>對置中矩陣，前 M 個主成分保留的變異越多，重建誤差就越小：</p>$$\text{總平方和}=\text{保留的平方和}+\text{重建誤差平方和}.$$<p>這把「投影後散得最開」連到「用低維資料近似得最好」，也為下一節的 PVE 提供解讀。</p>')
        b['lowrank']=merge_entries(b['lowrank'],['w07-detail-lowrank-objective','w07-detail-lowrank-advanced'],'w07-detail-lowrank-advanced','完整低秩計算：SVD、變異分解與不唯一性')
        b['kmeans']=condense(b['kmeans'],'w07-detail-kmeans-identity','群內兩兩距離與群心平方和的換算',None,lambda n,r:klass(n,'info-box'),r'<p>K-means 希望每個群內的點靠近自己的群心，常用的目標是</p>$$\sum_k\sum_{i\in C_k}\|x_i-\mu_k\|^2.$$<p>反覆做兩步：先把點指派給最近群心，再把每群中心更新為平均。不同初始值可能得到不同的最終分群。</p>')
        b['kmeans']=merge_entries(b['kmeans'],['w07-detail-kmeans-identity','w07-detail-kmeans-advanced'],'w07-detail-kmeans-advanced','完整 K-means：平方和、算例、停止條件與證明')
        b['hclust']=tables(b['hclust'],'w07-detail-linkage-table','查閱四種 linkage 的完整定義')
        b['hclust']=b['hclust'].replace('四種常見的定義在下面那張表','完整定義可在本節的查閱表展開')
        b['practical']=merge_entries(b['practical'],['w07-detail-cluster-methods-intro','w07-detail-density'],'w07-detail-density','延伸方法概觀與密度分群的完整流程')
        b['manifold']=merge_entries(b['manifold'],['w07-detail-manifold-overview','w07-detail-tsne-algorithm'],'w07-detail-tsne-algorithm','完整 t-SNE：鄰居機率、參數、梯度與算例')
        b['manifold']=collect(b['manifold'],'w07-detail-embedding-software','延伸實作：新資料映射、UMAP 與套件差異',lambda n,r:klass(n,'info-box') and 't-SNE 的使用範圍' in words(r))
        b['manifold']=merge_entries(b['manifold'],['w07-detail-embedding-software','w07-detail-manifold-extensions'],'w07-detail-manifold-extensions','延伸方法、套件用途與理論保證範圍')
    # Keep implementation provenance inside the relevant implementation entry.
    if stem=='beyond_linearity':
        b['gam']=merge_entries(b['gam'],['w08-detail-gam-lab'],'w08-detail-gam-lab','GAM 模型規格、Python 實作與完整輸出',extra=lambda n,r:n['tag']=='p' and '其中 education 是類別變數' in words(r))
        b['gam']=add_before(b['gam'],'w08-detail-gam-lab','<p>例如年齡與年份各用一條平滑曲線，學歷則用每個水準的一個效果；三者的貢獻相加得到薪資預測。</p>')
    elif stem=='tree_based_methods':
        b['classtree']=merge_entries(b['classtree'],['w09-detail-impurity-calculation'],'w09-detail-impurity-calculation','完整算例：錯誤率相同，為何分裂選擇不同？',extra=lambda n,r:n['tag']=='p' and any(t in words(r) for t in ['下面這個例子把問題','兩種切法都是 200','ISLP 圖 8.6 的 Heart']))
        b['classtree']=b['classtree'].replace('下面那張表是最經典的例子。','可展開本節的完整算例比較兩種分裂。')
        b['rf']=b['rf'].replace('與上式固定 x 的理論 ρ 定義不同','與深入計算中固定 x 的理論 ρ 定義不同')
        b['classtree']=merge_entries(b['classtree'],['w09-detail-classtree-lab'],'w09-detail-classtree-lab','分類樹的分裂、剪枝與 Python 實作',extra=lambda n,r:klass(n,'info-box') and '剪枝的時候可以換回錯誤率' in words(r))
    elif stem=='support_vector_machines':
        b['multiclass']=merge_entries(b['multiclass'],['w10-detail-multiclass-table'],'w10-detail-multiclass-table','OVO／OVA 完整比較與 SVC 介面',extra=lambda n,r:klass(n,'info-box') and 'decision_function_shape' in words(r))
    elif stem=='unsupervised_learning':
        b['practical']=merge_entries(b['practical'],['w07-detail-practical-lab'],'w07-detail-practical-lab','實作、圖表資料來源與完整輸出',extra=lambda n,r:n['tag']=='p' and '課本提供概念' in words(r))
        b['manifold']=merge_entries(b['manifold'],['w07-detail-manifold-extensions'],'w07-detail-manifold-extensions','延伸方法、套件用途與理論保證範圍',extra=lambda n,r:n['tag']=='p' and '這一節是課堂沒細講' in words(r))
    return b

# One entrypoint, invoked only after each chapter has assembled its full material.
def apply_reading_flow(stem,bodies):
    js=ROUTES[stem](bodies)
    polish(stem,bodies)
    # TeX comparison signs are text, never HTML tags. Preserve every code/output byte.
    for sec,body in bodies.items():
        protected=[(m.start(),m.end()) for m in re.finditer(r'<(?:pre|code)\b.*?</(?:pre|code)>',body,re.S)]
        def escape_math(match):
            if any(a<match.end() and z>match.start() for a,z in protected):return match.group()
            return match.group().replace('<','&lt;')
        bodies[sec]=re.sub(r'\$\$.*?\$\$|\$[^$]*?\$',escape_math,body,flags=re.S)
    from teaching_scope_ch7_8_9_12 import student_ui, remove_report_remainders
    student_ui(stem, bodies)
    remove_report_remainders(stem, bodies)
    return js
