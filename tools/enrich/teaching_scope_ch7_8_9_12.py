"""限定四章學生內容；保留原 Lab 的連續片段，不重算任何資料。"""
import re
from html import unescape
from html.parser import HTMLParser
from lib import card, lab_code, lab_output

VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class Tree(HTMLParser):
    def __init__(self,src):
        super().__init__(convert_charrefs=False);self.src=src;self.lines=[0]+[m.end() for m in re.finditer('\n',src)];self.stack=[];self.nodes=[]
        self.feed(src);self.close()
    def pos(self):
        a,b=self.getpos();return self.lines[a-1]+b
    def handle_starttag(self,tag,attrs):
        a=self.pos();n={'a':a,'b':a+len(self.get_starttag_text()),'inner':a+len(self.get_starttag_text()),'end':None,'tag':tag,'attrs':dict(attrs),'parent':self.stack[-1] if self.stack else None};self.nodes.append(n)
        if tag not in VOID:self.stack.append(n)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:
            n=self.stack.pop();n['end']=n['b']
    def handle_endtag(self,tag):
        if not self.stack:return
        if self.stack[-1]['tag']!=tag:return
        n=self.stack.pop();n['end']=self.pos();n['b']=self.src.index('>',self.pos())+1
    def raw(self,n):return self.src[n['a']:n['b']]

def text(s):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]+>',' ',s))).strip()
def has(n,c):return c in n['attrs'].get('class','').split()
def ancestor(n,c):
    while n is not None:
        if has(n,c):return n
        n=n['parent']

def change(src,edits):
    accepted=[]
    for a,b,v in sorted(edits,key=lambda e:(e[0],-e[1])):
        if not accepted or a>=accepted[-1][1]:accepted.append((a,b,v))
    for a,b,v in reversed(accepted):src=src[:a]+v+src[b:]
    return src

def drop(src,predicate,up=None):
    tr=Tree(src);out=[]
    for n in tr.nodes:
        if n['end'] is None and n['tag'] not in VOID:continue
        if predicate(n,tr.raw(n)):
            target=ancestor(n,up) if up else n
            if target:out.append((target['a'],target['b'],''))
    return change(src,out)

def drop_unit(src,title):
    tr=Tree(src);heads=[n for n in tr.nodes if n['tag'] in ('h3','h4')]
    for n in heads:
        if text(tr.raw(n))==title:
            nexthead=next((h for h in heads if h['a']>n['a'] and h['parent'] is n['parent']),None)
            end=nexthead['a'] if nexthead else n['parent']['end'] if n['parent'] else len(src)
            return src[:n['a']]+src[end:]
    return src

def paragraphs(src,phrases):
    return drop(src,lambda n,r:n['tag']=='p' and not ancestor(n,'deck-extra') and any(p in text(r) for p in phrases))

NAMES={7:'Ch07-nonlin-lab-zh.ipynb',8:'Ch08-baggboost-lab-zh.ipynb',9:'Ch09-svm-lab-zh.ipynb',12:'Ch12-unsup-lab-zh.ipynb'}
def chunk(ch,cell,start=None,end=None):
    s=lab_code(ch,cell)
    if start is not None:s=s[s.index(start):]
    if end is not None:s=s[:s.index(end)]
    return s.rstrip()
# Key = original card's first cited cell. Values are exact source-cell excerpts.
KEEP={
7:{14:('擬合多項式',[(14,None,'\nsummarize')],None),26:('比較多項式次數',[(26,None,None)],None),33:('多項式邏輯斯迴歸',[(33,None,'\nsummarize')],None),39:('切段與虛擬變數',[(39,None,'\nsummarize')],None),44:('擬合立方樣條',[(46,None,'\nsummarize')],None),56:('擬合自然樣條',[(56,None,'\nsummarize')],None),124:('局部迴歸的跨距',[(125,'    fitted = lowess','\n    ax.plot')],None),82:('擬合加法模型',[(82,None,None)],None)},
8:{50:('擬合迴歸樹',[(54,None,'\nax =')],None),57:('以交叉驗證選剪枝參數',[(57,None,None)],None),15:('擬合分類樹',[(17,None,None)],None),237:('組合多個分類器投票',[(238,'clf1 =','\nk =')],None),64:('Bagging',[(64,None,None)],None),70:('隨機森林與變數重要度',[(70,None,'\ny_hat_RF'),(72,None,None)],None),76:('梯度提升',[(76,None,None)],None),119:('XGBoost 的分類目標',[(124,'model =','\n# Obtain')],None),240:('Stacking 合併器',[(240,None,'\n\nprint')],None),86:('BART 模型',[(86,None,None)],None)},
9:{14:('線性支持向量分類器',[(16,None,None)],None),21:('辨認支持向量',[(22,None,None),(23,None,None)],None),31:('交叉驗證選 C',[(31,None,'\ngrid.best_params_')],None),95:('以 hinge loss 擬合線性分類器',[(95,'clf = SGDClassifier','\n# plot')],None),51:('特徵映射與自訂核',[(51,None,None)],None),53:('用自訂核擬合',[(53,'clf2 =','\n# predict')],None),57:('RBF 核分類器',[(61,'svm_rbf =',None)],None),67:('同時選 C 與核參數',[(67,None,'\ngrid.best_params_')],None),96:('用隨機 Fourier 特徵近似 RBF',[(97,None,'\nclf.score')],None)},
12:{19:('置中、標準化與 PCA 得分',[(19,None,None),(21,None,None),(23,None,None),(27,None,None)],None),48:('以 SVD 計算主成分',[(48,None,'\nU.shape')],None),35:('解釋變異比例',[(39,None,None)],39),56:('以低秩近似反覆補值',[(60,None,None),(62,None,None),(64,None,'\n    print')],None),103:('K-means 分群',[(105,None,None)],None),117:('建立階層式分群',[(117,None,None)],None),71:('t-SNE 的設定與嵌入',[(74,None,None),(75,None,None)],None)}
}

def clean_labs(src,ch):
    tr=Tree(src);edits=[]
    for n in tr.nodes:
        if not has(n,'deck-extra'):continue
        raw=tr.raw(n);m=re.search(r'data-lab-cells="([\d,]+)"',raw);key=int(m[1].split(',')[0]);spec=KEEP[ch].get(key)
        if spec is None:replacement=''
        else:
            label,parts,out=spec;code='\n\n'.join(chunk(ch,*p) for p in parts);cells='、'.join(str(p[0]) for p in parts)
            if len(parts)>1 and any(a is not None or z is not None for _,a,z in parts):
                purpose={(8,72):'讀取分裂重要度',(12,60):'以欄平均初始化缺值',(12,62):'設定補值迭代的停止條件',(12,64):'依低秩近似更新缺值'}
                replacement='\n'.join(card(purpose.get((ch,c),label),chunk(ch,c,a,z),None,src=f'<code>{NAMES[ch]}</code> · 儲存格 {c}') for c,a,z in parts)
            else:
                replacement=card(label,code,lab_output(ch,out) if out else None,src=f'<code>{NAMES[ch]}</code> · 儲存格 {cells}')
        edits.append((n['a'],n['b'],replacement))
    return change(src,edits)

def trim_empty(src):
    # Remove obsolete Lab headings; retained cards carry their own purpose and source link.
    src=drop(src,lambda n,r:n['tag'] in ('h3','h4') and '講義完整實作' in text(r))
    for _ in range(3):
        tr=Tree(src);edits=[]
        for n in tr.nodes:
            if n['tag']!='details' or n['end'] is None:continue
            raw=tr.raw(n);body=re.sub(r'<summary\b.*?</summary>','',raw,flags=re.S)
            body=re.sub(r'<h[34]\b.*?</h[34]>','',body,flags=re.S)
            if not text(body):edits.append((n['a'],n['b'],''))
        new=change(src,edits)
        if new==src:break
        src=new
    return src

# Delete only these independently invented numerical examples, never all '例如' clauses.
DROP_P={
7:['用節點 $(0,1,2)$','例如 $g(x)=1+2x_1-x_2$'],
8:['例如某三葉子樹的 RSS 為 10','算例：平方損失','例如 $g=(1,4)$','例如殘差為 $(-4,1,3)$','同一份系外行星資料','625 秒 vs 13 秒'],
9:['可自行算完的例子','接續兩點例子','半正定檢查例','本站算例','按表中次序連線的梯形面積'],
12:['例：$X=','一輪 K-means 與停止條件這','對一維資料 $(0,1,4,5)$','一維兩群 $A=(0,2)$','例如三個低維點 $(0,1,3)$','如果只知道對角線','初始化也可用 K-means++']}

# Exact-span cuts within paragraphs preserve the mathematical statement beside the example.
CUTS={
7:[(r'例如 \$\\hat\\eta=-2\$.*?這是固定', '這是固定'),(r'例如 \$f\(x\)=1\+2x.*?一般 degree', '一般 degree'),(r'例如 \$\(10,2,3,-1\)\$.*?切段可以','切段可以'),(r'例如在正交座標中.*?GCV 則把','GCV 則把'),(r'例如一筆 \$y=1\$.*?若更新','若更新'),(r'例如 \$x=\(-1,0,1\)\$.*?權重不是','權重不是'),(r'例如 \$y=\(2,4,6\)\$.*?對 Gaussian GAM','對 Gaussian GAM'),(r'模型 \$\\hat f\(x_1,x_2\)=2x_1\+x_2\^2\$.*?若模型是加法形式','若模型是加法形式')],
8:[(r'例如水準 A、B、C.*?排序使用','排序使用'),(r'例如 \$y=\(0,2,4\)\$.*?二元 logistic','二元 logistic'),(r'例如 \$e=1/4\$.*?SAMME','SAMME'),(r'例如四箱梯度和.*?箱數越少','箱數越少'),(r'例如兩個互斥的 0/1 欄.*?類別分裂','類別分裂'),(r'；若 \$a=0\.2,b=0\.1\$.*?。','。'),(r'若依序同類的反應.*?Ordered boosting','Ordered boosting'),(r'若連續兩層分別判斷.*?這種受限結構','這種受限結構'),(r'若 \$k=2,\\eta=0\.1\$.*?其他正規化模式','其他正規化模式'),(r'例如 \$r=\(1,3\)\$.*?不是直接把葉值設為樣本平均 2。','')],
9:[(r'例如直線 \$3z_1.*?若 \$w=0\$','若 $w=0$'),(r'。例如 \$\\varepsilon=0\.2\$.*?；\$\\varepsilon\$','。$\\varepsilon$'),(r'固定亂數種子才能重現同一組近似。',''),(r'例如分數為 0\.5.*?間隔上的折角','間隔上的折角')],
12:[(r'若奇異值為 \$\(3,1\)\$.*?若矩陣全為 0','若矩陣全為 0'),(r'例如主成分共變異數是.*?ZCA 乘回','ZCA 乘回'),(r'例：兩點距離 0\.2.*?連結強度。',''),(r'例如資料 \$\(0,0\.1,0\.2,1\)\$.*?若邊界點','若邊界點'),(r'對平坦鄰域的示意例.*?不同初值','不同初值'),(r'例：一維兩個等權.*?等權球狀混合','等權球狀混合'),(r'例：數值差為 2.*?FAMD','FAMD'),(r'如果兩個鄰居各有機率.*?鄰居距離完全相等','鄰居距離完全相等'),(r'若兩個鄰居各有機率.*?鄰居距離完全相等','鄰居距離完全相等'),(r'PHATE 以擴散.*?若把降維','若把降維'),(r'另一種方法先建立最小生成樹.*?它也會受細長鏈與離群邊影響。','')]}

REMOVE_HEADINGS={
7:['Wage 上的實測數字（本頁元件用的就是這些）'],
8:['lab 在 Boston 上的實測數字（同一份 70/30 切分）'],
9:['lab 上的實測數字（全部逐字取自 Ch09-svm-lab-zh.ipynb ）'],
12:['USArrests 的實測數字','混合資料的其他比較基準']}

REPLACE_TITLES={
'機率的信賴區間：logit 轉換與算例':'機率的信賴區間：logit 轉換',
'局部加權擬合的算例與多變數延伸':'局部加權擬合與多變數延伸',
'白化算例與零特徵值':'白化與零特徵值',
'補值驗證、可識別性算例與單調性推導':'補值驗證、可識別性與單調性推導',
'從 logit 的信賴區間回到機率':'從 logit 的信賴區間回到機率',
'局部加權擬合的一次計算':'局部加權擬合',
'用一個小例子區分四種效果圖':'區分四種效果圖',
'主成分的完整條件與可重算例子':'主成分的完整條件',
'合併距離的一次手算':'連結方式的比較',
'一輪 K-means 與停止條件':'K-means 的停止條件',
'核 Ridge 與單類別邊界':'單類別邊界',
'核 Ridge 的解與單類別對偶':'單類別 SVM 的對偶',
'分裂式與最小生成樹的具體步驟':'分裂式階層分群',
'Python 實作與完整輸出':'方法示範與原 Lab',
'完整比較表、公式與實測結果':'方法與公式速查',
'套件實作、超參數與實測比較':'套件方法與超參數',
'GAM 模型規格、Python 實作與完整輸出':'GAM 模型規格與原 Lab',
'實作、圖表資料來源與完整輸出':'原 Lab',
'完整硬邊界問題：primal、dual、KKT 與算例':'完整硬邊界問題：primal、dual 與 KKT',
'深入核函數：特徵映射、Gram 矩陣與合法條件':'深入核函數：特徵映射、Gram 矩陣與合法條件',
'完整 PCA：限制式、矩陣算例與特徵推導':'完整 PCA：限制式與特徵推導',
'完整 K-means：平方和、算例、停止條件與證明':'完整 K-means：平方和、停止條件與證明',
'深入階層方法：Ward 算例、分裂式與 MST':'深入階層方法：Ward 與分裂式',
'完整 t-SNE：鄰居機率、參數、梯度與算例':'完整 t-SNE：鄰居機率、參數與梯度',
'算例：用 SVM 決策分數畫 ROC':'用 SVM 決策分數畫 ROC',
'延伸：核 Ridge 與單類別 SVM':'延伸：單類別 SVM',
}

def teaching_scope(stem,bodies):
    ch={'beyond_linearity':7,'tree_based_methods':8,'support_vector_machines':9,'unsupervised_learning':12}[stem]
    for sec,src in bodies.items():
        src=clean_labs(src,ch)
        src=paragraphs(src,DROP_P[ch])
        # Paragraph edits avoid source code and saved outputs entirely.
        tr=Tree(src);edits=[]
        for n in tr.nodes:
            if n['tag']!='p' or ancestor(n,'deck-extra'):continue
            raw=tr.raw(n);v=raw
            for pat,rep in CUTS[ch]:v=re.sub(pat,lambda m,rep=rep:rep,v,flags=re.S)
            if v!=raw:edits.append((n['a'],n['b'],v))
        src=change(src,edits)
        for title in REMOVE_HEADINGS[ch]:src=drop_unit(src,title)
        src=drop(src,lambda n,r:has(n,'ver-note'))
        for old,new in REPLACE_TITLES.items():src=src.replace(old,new)
        bodies[sec]=trim_empty(src)
    return bodies

# Additional scope rules act on fully assembled (and TeX-protected) source fragments.
def finalize_scope(stem,bodies):
    ch={'beyond_linearity':7,'tree_based_methods':8,'support_vector_machines':9,'unsupervised_learning':12}[stem]
    teaching_scope(stem,bodies)
    for sec,src in bodies.items():
        if ch==7:
            src=drop(src,lambda n,r:has(n,'quiz-box') and 'id="qDegOptions"' in r)
            src=drop(src,lambda n,r:n['tag']=='svg' and n['attrs'].get('id')=='w08polyMse')
            src=drop(src,lambda n,r:n['attrs'].get('id') in {'w08polyTrain','w08polyCv','w08polyWl','w08polyWr','w08polyWm','w08natWl','w08natWr','w08lamGcv','w08lamR2','w08gamR2','w08gamGcv'},up='ic-row')
            src=drop(src,lambda n,r:has(n,'info-card') and any(t in text(r) for t in ['重點在兩端的帶寬','gridsearch 選出來的是什麼']))
            src=drop(src,lambda n,r:n['tag']=='button' and n['attrs'].get('id')=='w08lamPickBtn')
            src=paragraphs(src,['個別的 $\\hat\\beta_j$ 沒有解讀價值','上表的 16.4 與 5.3'])
            for old,new in [
              ('下圖：訓練 MSE（藍）一路往下，10-fold CV MSE（紅）在 d = 4 觸底之後回頭往上。',''),
              ('實測（Wage 全體 n = 3000）','樣條設定'),
              ('回到 lab 的設定','重置'),
              ('實測：80 歲那端的帶寬從 65.8 降到 37.1。',''),
              ('自然樣條再加兩個自然邊界條件，實測把 80 歲那端的信賴區間從 65.8 砍到 37.1。','自然樣條以兩個自然邊界條件限制尾端的形狀。'),
            ]:src=src.replace(old,new)
        elif ch==8:
            # This widget compared a new simulated dataset against Boston model scores.
            src=drop(src,lambda n,r:has(n,'viz-layout') and 'id="w09rfChart"' in r)
            src=drop(src,lambda n,r:n['tag']=='div' and re.match(r'<div\b[^>]*>\s*<table',r) and not has(n,'viz-layout') and (('在 lab 的實測' in text(r)) or ('最佳 CV 正確率' in text(r))))
            src=drop(src,lambda n,r:n['tag']=='div' and re.match(r'<div\b[^>]*>\s*<table',r) and '切法 A' in text(r) and '300' in text(r))
            src=paragraphs(src,['下面這個例子把問題','兩種切法都是 200','同一份系外行星資料','625 秒 vs 13 秒'])
            src=src.replace('可展開本節的完整算例比較兩種分裂。','可從節點純度理解為何錯誤率無法辨別所有分裂。')
            # Keep the lecture's impurity importance plot, remove the new permutation experiment.
            src=drop(src,lambda n,r:n['tag']=='option' and n['attrs'].get('value')=='permutation')
            src=drop(src,lambda n,r:n['attrs'].get('id') in {'w09vimpTop1','w09vimpTop2','w09vimpShare','w09vimpMse'},up='ic-row')
            src=drop(src,lambda n,r:has(n,'info-card') and ('兩種重要度差在哪裡' in text(r)))
            src=src.replace('換一種重要度的定義，看排名會不會變。','依各變數的分裂純度下降量解讀其在模型中的作用。')
        elif ch==9:
            src=drop(src,lambda n,r:n['tag']=='div' and re.match(r'<div\b[^>]*>\s*<table',r) and '大於 0.8' in text(r))
            src=paragraphs(src,['Nyström 則選','核 Ridge 使用平方損失','把 $w$ 分成訓練特徵張成空間'])
            src=src.replace('林軒田 Support Vector Regression 中的 Kernel Ridge Regression；','')
            src=src.replace('固定亂數種子才能重現同一組近似。','')
            src=src.replace('；<code>Nystroem</code> 選訓練資料中的代表點近似 Gram 矩陣。','。')
            src=src.replace('代表點選取、標準化與後續模型','特徵近似、標準化與後續模型')
            src=src.replace('（lab 儲存格 53 實測都是 1.0）','')
        else:
            src=drop(src,lambda n,r:n['tag']=='p' and text(r).startswith('輪廓係數以'))
            src=paragraphs(src,['初始化也可用 K-means++'])
            src=src.replace('固定種子可讓別人重現這組數字。','')
            src=drop(src,lambda n,r:has(n,'info-card') and any(t in text(r) for t in ['跟 lab 一模一樣嗎','為什麼不是 0.711','為什麼數字不一樣']))
        # Report-style phrases are prose only, never altered inside retained source code.
        tr=Tree(src);edits=[]
        for n in tr.nodes:
            if n['tag']!='p' or ancestor(n,'deck-extra'):continue
            raw=tr.raw(n);new=raw
            pats=[]
            if ch==7:pats=[(r'例如在正交座標中.*?GCV 則把','GCV 則把')]
            if ch==12:pats=[(r'rank-1 小例：.*?推薦系統','推薦系統'),(r'例：數值差為 2.*?結果就會由數值欄主導。','')]
            for pat,rep in pats:new=re.sub(pat,lambda m,rep=rep:rep,new,flags=re.S)
            if new!=raw:edits.append((n['a'],n['b'],new))
        src=change(src,edits)
        bodies[sec]=trim_empty(src)
    return bodies

def student_ui(stem,bodies):
    finalize_scope(stem,bodies)
    for sec,src in bodies.items():
        if stem=='beyond_linearity':
            src=drop(src,lambda n,r:has(n,'info-card') and any(t in text(r) for t in ['GRIDSEARCH 選出來的是什麼','gridsearch 選出來的是什麼','與 lab 的差異']))
            src=src.replace('這個次數的成績','目前設定').replace('這個 DF 的成績','目前設定').replace('這個 df 的成績','目前設定').replace('（λ = 5.2×10⁹ 對上 df = 2）','')
            src=src.replace('。此圖的重點：同樣三個節點（25／40／60），立方樣條在 80 歲那端的 95% 信賴區間寬 65.8，自然樣條只有 37.1——線性約束把邊界的變異砍掉一半。','比較立方樣條與具有線性尾端的自然樣條。')
            src=src.replace('。此圖的重點：df = 2 幾乎是直線，df = 19 有明顯起伏；pygam 依 GCV 選出 df = 5.64，跟課本圖 7.8 用 LOOCV 選出的 6.8 很接近。','比較不同平滑程度下的曲線。')
        elif stem=='tree_based_methods':
            src=drop(src,lambda n,r:n['tag']=='select' and n['attrs'].get('id')=='w09vimpSel')
            src=drop(src,lambda n,r:has(n,'info-card') and any(t in text(r) for t in ['兩種重要度','排列重要度','Permutation 重要度']))
            src=src.replace('。此圖的重點：lstat 與 rm 兩個變數就吃掉近 70% 的不純度下降總量，其餘十個變數加起來還不到三分之一。','由分裂造成的純度下降衡量變數重要度。')
        elif stem=='support_vector_machines':
            src=drop(src,lambda n,r:n['tag']=='canvas' and n['attrs'].get('id')=='w10rbfChart',up='chart-wrap')
            src=drop(src,lambda n,r:n['attrs'].get('id') in {'w10rbfTr','w10rbfTe'},up='ic-row')
            src=drop(src,lambda n,r:has(n,'info-card') and '兩組資料在教什麼' in text(r))
            src=drop(src,lambda n,r:has(n,'info-card') and '交叉驗證選出來的是哪一組' in text(r))
            src=src.replace('（<strong>預先計算的 40×40 格點</strong>）','').replace('上圖：填色是 RBF','填色是 RBF')
            src=re.sub(r'<strong>在 C=1 下看 γ = 50</strong>.*?下圖：C = 1 固定，γ 從 0.25 掃到 50 的訓練與測試錯誤率。','',src,flags=re.S)
            src=src.replace('這一組的出處','參數的意義')

            src=src.replace('（固定種子的模擬）','（示意）')
        else:
            src=drop(src,lambda n,r:n['attrs'].get('id')=='w07mcCorr',up='ic-row')
            src=drop(src,lambda n,r:has(n,'info-card') and ('0.7114' in text(r) or 'np.random.seed(15)' in text(r)))
        # Delete side cards left with a title but no rows after removal of reports.
        src=drop(src,lambda n,r:has(n,'info-card') and 'id=' not in r and 'ic-row' not in r and not re.search(r'<(?:p|ul|ol|svg|canvas)\b',r) and len(text(re.sub(r'<[^>]+class="[^"]*ic-title.*?</[^>]+>','',r,flags=re.S)))<3)
        src=src.replace('講義完整實作','方法示範').replace('完整輸出','方法示範').replace('固定種子模擬','示意')
        bodies[sec]=trim_empty(src)
    return bodies


def replace_function(js,name,fn):
    pat=r'function '+re.escape(name)+r'\([^\n]*?\)\s*\{.*?^\}'
    m=re.search(pat,js,re.S|re.M)
    if not m:raise ValueError('Missing function '+name)
    old=m.group();new=fn(old) if callable(fn) else fn
    return js[:m.start()]+new+js[m.end():]

def clean_pagejs(stem,js):
    if stem=='beyond_linearity':
        js=js.replace(', w08polyMseSvc = null','')
        js=replace_function(js,'w08polySetup',lambda f:f[:f.index('  const F = FRAMES_w08poly;')]+'}')
        def poly(f):
            f=f[:f.index('  /* 下面那張 MSE-vs-degree 小圖 */')]
            return f+"  $('w08polySlVal').textContent = String(d);\n  $('w08polyDeg2').textContent = String(d);\n  setStatus('w08polyStatus', 'degree ' + d + '：觀察曲線與兩端信賴區間的變化。');\n}"
        js=replace_function(js,'w08polyDraw',poly)
        def natural(f):
            f=re.sub(r"  \$\('w08natW[lr]'\)\.textContent = .*?;\n",'',f,flags=re.S)
            k=f.index("  setStatus('w08natStatus'")
            return f[:k]+"  setStatus('w08natStatus', '比較相同內部節點下的立方樣條與自然樣條；注意邊界形狀。');\n}"
        js=replace_function(js,'w08natDraw',natural)
        js=js.replace('let w08lamShowPick = true;','')
        def smooth(f):
            f=re.sub(r'  if \(w08lamShowPick\) \{.*?\n  \}\n','',f,flags=re.S)
            f=re.sub(r"  \$\('w08lam(?:Gcv|R2)'\)\.textContent = .*?;\n",'',f)
            k=f.index('  const best =')
            return f[:k]+"  setStatus('w08lamStatus', 'df = ' + HC.fmt(df, 1) + '：有效自由度較大時，曲線可以有更多起伏。');\n}"
        js=replace_function(js,'w08lamDraw',smooth)
        js=replace_function(js,'w08lamTogglePick','')
        def gam(f):
            f=re.sub(r"  \$\('w08gam(?:R2|Gcv)'\)\.textContent = .*?;\n",'',f)
            k=f.index("  setStatus('w08gamStatus'")
            return f[:k]+"  setStatus('w08gamStatus', '比較各個加法成分的形狀，以及改變平滑程度後的效果。');\n}"
        js=replace_function(js,'w08gamDraw',gam)
    elif stem=='tree_based_methods':
        js=replace_function(js,'w09rfDraw','function w09rfDraw() {}')
        def imp(f):
            k=f.index('  const tot =')
            return f[:k]+"  setStatus('w09vimpStatus', '長條表示分裂造成的純度下降總量；重要度沒有方向，也不等同因果效果。');\n}"
        js=replace_function(js,'w09vimpDraw',imp)
    elif stem=='support_vector_machines':
        js=replace_function(js,'w10rbfChart','function w10rbfChart() {}')
        def rbf(f):
            f=re.sub(r"  \$\('w10rbf(?:Tr|Te)'\)\.textContent = .*?;\n",'',f)
            f=f.replace("  $('w10rbfWhy').textContent = fr.why;", "  $('w10rbfWhy').textContent = 'γ 控制核的局部程度；C 控制違反間隔的懲罰。';")
            k=f.index("  setStatus('w10rbfStatus'")
            return f[:k]+"  setStatus('w10rbfStatus', 'γ = ' + fr.gamma + '、C = ' + fr.C + '：觀察核的局部程度與邊界形狀。');\n}"
        js=replace_function(js,'w10rbfDraw',rbf)
    elif stem=='unsupervised_learning':
        js=re.sub(r"  \$\('w07mcCorr'\)\.textContent = .*?;\n",'',js)
        js=js.replace("      + '。橘框裡是補出來的值，跟真值的相關係數 ' + HC.fmt(r, 3)","      + '。橘框裡是以低秩近似補出的值。'")
    js=js.replace('固定種子的模擬','示意').replace('（固定種子）','')
    return js

# End-user text cleanups that are independent of the retained numerical data.
def remove_report_remainders(stem,bodies):
    for sec,src in bodies.items():
        if stem=='beyond_linearity':
            src=src.replace('（6.8、5.64 都合法）','（例如講義的 6.8）')
        if stem=='tree_based_methods':
            src=src.replace('資料是固定種子的合成資料','資料為合成示意').replace('好處是快到可以在幾毫秒內算完。這是能夠實用的唯一理由。','貪婪搜尋降低了計算成本。')
            src=src.replace('箱數、類別支援與預設值會隨版本和估計器而不同；255 是常見設定，並非所有模式的不可突破上限。','箱數是可調參數，255 並非所有模式的不可突破上限。').replace('預測時依官方版本設定使用完整樹範圍','預測時使用所選的完整樹範圍')
            src=drop(src,lambda n,r:has(n,'quiz-box') and 'id="qVoteOptions"' in r)
            src=src.replace('（固定種子的模擬，所以你重新載入頁面看到的是同一組）','（示意）')
        if stem=='support_vector_machines':
            src=drop(src,lambda n,r:has(n,'quiz-box') and 'id="qKernOptions"' in r)
            src=re.sub(r'對，這正是 lab 儲存格 43–49 演示的事：.*?ISLP §9\.6\.1 的評語', 'ISLP §9.6.1 的評語',src,flags=re.S)
        if stem=='unsupervised_learning':
            src=src.replace('不同套件計算近鄰數是否含自身可能不同，重現時需核對。','近鄰數是否包含樣本本身，須與方法的定義一致。')
            src=re.sub(r'而且 SVC 的正確率從 0\.62 拉到 0\.98。','',src)
            src=re.sub(r'<p>常見的內部指標（silhouette、Calinski–Harabasz、gap statistic）.*?</p>','',src,flags=re.S)
        bodies[sec]=trim_empty(src)
    return bodies
