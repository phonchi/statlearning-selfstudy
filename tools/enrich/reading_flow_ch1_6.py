"""Chapter-owned reading organization; preserves lesson bodies and lab payloads.

Detailed blocks are assembled from the real generated content, not linked to an
unrendered appendix. Core bridges appear before the original concept quizzes.
"""
from bs4 import BeautifulSoup, Tag, NavigableString
from lib import detail, quiz
import re


def fragment(html):
    return BeautifulSoup(html, 'html.parser',
                         preserve_whitespace_tags={'pre', 'textarea', 'span', 'div'})


def meaningful(soup):
    return [n for n in soup.contents if isinstance(n, Tag)]


def wrap(soup, nodes, pid, title):
    nodes = [n for n in nodes if n.parent is soup]
    if not nodes:
        raise ValueError(f'Empty reading group: {pid}')
    body = ''.join(str(n) for n in nodes)
    outer = fragment(detail(pid, title, body)).details
    nodes[0].insert_before(outer)
    for n in nodes:
        n.extract()
    return outer


def heading(soup, text):
    return next((n for n in meaningful(soup) if n.name in ('h3','h4')
                 and n.get_text(' ', strip=True) == text), None)


def fold_heading(soup, text, pid, title, stop_core=False):
    start = heading(soup, text)
    if start is None:
        raise ValueError(f'Missing heading for {pid}: {text}')
    nodes = []
    for n in [start, *list(start.next_siblings)]:
        if isinstance(n, Tag) and n is not start:
            if n.name == 'h3':
                break
            if stop_core and any(c in n.get('class', []) for c in ('quiz-box','qa-box','viz-layout','info-box','reading-detail')):
                break
        nodes.append(n)
    return wrap(soup, nodes, pid, title)


def before_quiz(soup, html):
    nodes = list(fragment(html).contents)
    target = next((n for n in meaningful(soup) if 'quiz-box' in n.get('class', [])), None)
    for n in nodes:
        if target:
            target.insert_before(n)
        else:
            soup.append(n)


def fold_labs(soup, prefix, section):
    """Keep each uninterrupted sequence of complete code/output cards together."""
    count = 0
    while True:
        card = next((n for n in meaningful(soup) if 'deck-extra' in n.get('class', [])), None)
        if card is None:
            return
        count += 1
        nodes = [card]
        prev = card.previous_sibling
        blanks = []
        while prev is not None and not isinstance(prev, Tag):
            blanks.insert(0, prev)
            prev = prev.previous_sibling
        if isinstance(prev, Tag) and prev.name in ('h3','h4') and '完整實作' in prev.get_text():
            nodes = [prev, *blanks, card]
        nxt = card.next_sibling
        pending = []
        while nxt is not None:
            if not isinstance(nxt, Tag):
                pending.append(nxt)
            elif 'deck-extra' in nxt.get('class', []):
                nodes.extend(pending + [nxt]); pending = []
            else:
                break
            nxt = nxt.next_sibling
        title_node = card.select_one('.dx-label') or card.select_one('.dx-title')
        title = title_node.get_text(' ',strip=True) if title_node else section
        title = title.replace('講義完整實作：','').replace('課程lab · ','')
        title = re.sub(r'^講義\s*\d+\s*·\s*', '', title)
        wrap(soup, nodes, f'{prefix}-detail-lab-{section}-{count}', f'完整實作：{title}')


GROUPS = {2: {'bayes': [('KNN 的彈性與有效自由度', 'knn-df', '計算細節：KNN 迴歸的有效自由度')]},
 3: {'slr': [('解釋變數一定要是隨機變數嗎？', 'fixed-x', '延伸閱讀：固定設計與隨機解釋變數')],
     'inference': [('用 bootstrap 建立迴歸曲線的信賴區間', 'bootstrap-ci', '延伸閱讀：用 bootstrap 建立曲線區間'),
                   ('公式的條件與平均反應／新觀測', 'matrix-intervals', '計算細節：係數共變異數與 CI／PI')],
     'accuracy': [('相關係數平方不能取代任意預測的 R²', 'r2-counterexample', '計算細節：R² 與相關係數的反例')],
     'mlr': [('逐步選擇：如何形成候選模型？', 'stepwise', '延伸閱讀：逐步選擇候選模型'),
             ('控制其他變數：CCPR 與部分迴歸圖', 'partial-plots', '延伸閱讀：CCPR、部分迴歸圖與 FWL'),
             ('一次檢定一組係數：部分 F 檢定', 'partial-f', '計算細節：部分 F 檢定')],
     'qualitative': [('中心化會改變哪個係數的意義？', 'centering', '計算細節：中心化與交互作用係數')],
     'problems': [('內部與外部學生化殘差', 'studentization', '計算細節：內部與外部學生化殘差'),
                  ('殘差為什麼對擬合值畫？', 'residual-geometry', '計算細節：殘差圖與投影幾何')],
     'reference': [('Advertising 的迴歸結果', 'advertising-numbers', '計算細節：Advertising 完整數值對照')]},
 4: {'logistic': [('從觀測到估計：完整的最大概似問題', 'logistic-fit', '計算細節：概似、Newton／IRLS 與標準誤'),
                  ('預測機率的區間與模型比較', 'probability-intervals', '延伸閱讀：預測機率的區間與模型比較'),
                  ('反應誤差、潛在變數與完全分離', 'latent-logistic', '延伸閱讀：反應誤差、潛在變數與分離')],
     'multinomial': [('多類別模型如何估計？', 'multinomial-fit', '計算細節：多類別概似與識別限制'),
                     ('二元分類器如何組成多類別分類？', 'ovr-ovo', '延伸閱讀：OVR 與 OVO 的組合規則')],
     'lda': [('LDA 與 Fisher LDA：分類規則與判別方向', 'fisher', '延伸閱讀：Fisher 判別方向與 Iris 投影'),
             ('把生成式模型的參數估出來', 'generative-fit', '計算細節：生成式模型的參數與共變異數'),
             ('為什麼二類的最小平方與 LDA 方向有關？', 'ols-lda', '延伸閱讀：OLS、LDA 與降秩迴歸')],
     'threshold': [('F1 與隨機分數的 AUC 基準', 'f1-auc', '延伸閱讀：F1 與隨機分數的 AUC 基準')],
     'compare': [('QDA log-odds 中的係數到底是什麼？', 'qda-coefficients', '計算細節：QDA log-odds 的完整係數')],
     'poisson': [('Poisson 的估計與 GLM 的變異數', 'glm-fit', '計算細節：Poisson 估計與 GLM 指數族'),
                 ('Bikeshare：同一特徵，兩種係數量尺', 'bikeshare-table', '計算細節：Bikeshare 兩種模型的係數對照')],
     'reference': [('Default 的分類結果', 'default-numbers', '計算細節：Default 完整數值對照')]},
 5: {'loocv': [('LOOCV 捷徑何時可用？', 'press', '計算細節：LOOCV 捷徑與槓桿值')],
     'cvwrong': [('分折也要反映未來的預測情境', 'splits', '延伸閱讀：群組、時間與重複切分'),
                 ('調參、外層評估與折外預測', 'nested-cv', '延伸閱讀：巢狀 CV 與折外預測')],
     'bootstrap': [('從標準誤到信賴區間與預測區間', 'bootstrap-intervals', '延伸閱讀：bootstrap 信賴區間與預測區間'),
                   ('Jackknife：逐筆刪除，估計量會變多少？', 'jackknife-se', '延伸閱讀：Jackknife 的標準誤'),
                   ('Permutation test：假如 X 與標籤沒有關聯？', 'permutation', '延伸閱讀：置換檢定與分類器評估'),
                   ('Jackknife也能估計偏差', 'jackknife-bias', '計算細節：Jackknife 的偏差修正'),
                   ('固定設計下用bootstrap估預測誤差', 'bootstrap-prediction', '計算細節：重抽預測誤差與區塊自助法')]},
 6: {'criteria': [('分類模型的模型選擇', 'classification-selection', '延伸閱讀：分類模型的選擇'),
                  ('Cp 的風險目標、常數與選模', 'cp-risk', '計算細節：Cp 的風險目標與常數'),
                  ('分類離差的數值如何對回軟體？', 'deviance', '完整實作：分類離差與軟體量尺')],
     'ridge': [('中心化後的 Ridge 解', 'ridge-solution', '計算細節：Ridge 的矩陣解與方向收縮')],
     'lasso': [('收縮的貝氏解讀與延伸', 'shrinkage-map', '延伸閱讀：收縮的貝氏解讀'),
               ('Lasso 的零係數條件與座標更新', 'lasso-solution', '計算細節：Lasso 的零點與座標下降'),
               ('最小角度迴歸與 Group Lasso', 'lar-group', '延伸閱讀：LAR 與 Group Lasso'),
               ('限制式與懲罰式：如何對應？', 'penalty-constraint', '計算細節：限制式與懲罰式的對應')],
     'pcr': [('從共變異數到白化', 'whitening', '計算細節：共變異數、SVD 與白化'),
             ('PCA 的最大變異與最小重建誤差', 'pca-objectives', '計算細節：PCA 變異與重建目標'),
             ('正交、不相關與獨立是三件事', 'uncorrelated', '延伸閱讀：正交、不相關與獨立')],
     'pls': [('PLS1：從方向到可用於新資料的預測', 'pls-algorithm', '計算細節：PLS1 的訓練與新資料預測'),
             ('PLS最大化共變異，並非直接最大化相關', 'pls-covariance', '計算細節：PLS 的共變異目標')],
     'reference': [('在係數平面比較方法', 'coefficient-paths', '延伸閱讀：在係數平面比較方法')]}}

BRIDGES = {
    3: {
        'inference': r'<p>區間的用途要分清楚：平均反應的 CI 衡量平均曲線估計的不確定性；新觀測的 PI 還包含新觀測自己的雜訊，所以通常更寬。以下一般 t／F 推論使用線性條件平均、獨立常態且同變異的誤差，以及滿欄秩和正殘差自由度；只有計算最小平方係數則不需要常態假設。</p>',
        'mlr': r'<p>整體 F 檢定問所有斜率是否同時為零；部分 F 則比較同一批資料上的兩個巢狀模型，一次檢定一組係數。係數仍描述控制模型內其他變數後的條件關聯，不能直接當成因果效果。</p>',
        'accuracy': r'<p>本節 0≤R²≤1 與相關係數平方的性質，使用含截距、在訓練資料上做普通最小平方的設定；任意預測或測試資料的 R² 可以為負。判斷預測好壞仍要使用獨立資料。</p>',
    },
    4: {
        'logistic': r'<p>給定 X，模型假設各 Yᵢ 獨立且為 Bernoulli。係數用最大概似估計：找出讓已觀測標籤最可能的一組 β。完整的估計目標是</p>$$\max_\beta L(\beta)=\prod_i p_i^{y_i}(1-p_i)^{1-y_i},\qquad p_i=\sigma(x_i^T\beta).$$<p>這與最小化負對數概似相同。完全或準完全分離時，無懲罰模型可能沒有有限的最大概似解；係數的 z 檢定使用大樣本近似，不是一般有限樣本精確 t 檢定。</p>',
        'multinomial': r'<p>多類別 logistic 用同一個 softmax 給出加總為 1 的類別機率。選一個基準類是為了識別係數；換基準類不改變預測機率。OVR／OVO 則是把多類別任務拆成多個二元模型的其他做法，完整規則可展開查閱。</p>',
        'threshold': r'<p>敏感度描述真實正類中抓到多少；精確率描述預測正類中有多少是真的。AUC 衡量分數的排序能力；與類別獨立的同分布隨機分數，其母體 AUC 為 0.5。降低門檻值不保證提高精確率或總正確率。</p>',
        'poisson': r'<p>Poisson 迴歸模型化的是給定 X 的計數分布：條件平均與變異數都等於 μ，log μ 才是線性預測量。它不是先對觀測計數取 log 再做普通最小平方。係數每增加一單位使平均計數乘上 eᵝ；比較前須先確認變數的原始單位。</p>',
    },
    5: {
        'cvwrong': r'<p>分割方式須配合預測情境：同一受試者的資料通常一起分組，時間資料用較早訓練、較晚驗證。調參和最終評估也要分開；內層 CV 選模型，外層 CV 或保留測試集評估整個選模流程。</p>',
        'bootstrap': r'<p>bootstrap 的主線是：以觀測為單位有放回重抽、每次重算同一估計量，再由這些估計值的散布估標準誤。平均曲線的信賴區間和新觀測的預測區間不同，後者還要包含新觀測雜訊。下面的延伸各自說明區間、其他重抽樣方法。</p>',
    },
    6: {
        'criteria': r'<p>比较準則前須使用同一候選集合並確認量尺。Cp 的完整風險式要把截距也算入參數個數；各模型共用 σ̂² 時，可以省掉共同常數作排序，但省略後的分數不再是完整風險值。下面 BIC／Cp 的懲罰比較採這個共同變異數的設定；軟體各自估變異數的概似版本須另外對照。</p>',
        'lasso': r'<p>λ 控制懲罰強度，s 控制圖中的約束範圍；兩者可用適當值得到同一個解，但一般不是一對一。Lasso 允許係數精確歸零，並不保證任何正 λ 都會產生零係數；Ridge／Lasso 的勝負仍須以相同評估流程比較。</p>',
        'pcr': r'<p>PCR 的方向由 X 決定，不使用 y；保留 X 的高變異方向不保證保留最有用的預測訊號。成分數 M 與原始變數數不同，少量成分仍可能用到許多原始欄位；滿欄秩且保留全部方向時，擬合值回到普通最小平方。</p>',
        'pls': r'<p>PLS 用 X 與 y 的共變動挑方向，所以 y 改變時方向也可能改變。它仍然是降維後迴歸，不是 Lasso 那種原始變數選擇；成分數和前處理一樣要在訓練折內選定，沒有一致勝過 PCR 的保證。</p>',
    },
}


def organize(ch, bodies, pagejs):
    """Return chapter content with complete, chapter-specific detail groups."""
    prefix = f'w{ch:02d}'
    soups = {k: fragment(v) for k,v in bodies.items()}
    if ch == 1:
        for card in list(soups['datasets'].select('.deck-extra')):
            label = card.select_one('.dx-label').get_text(' ', strip=True)
            if label in {'課程lab · 2004年的平均薪資', '課程lab · 投影的輸入'}:
                card.decompose()
    # Long outputs were removed at their original card calls. Do not leave
    # explanations pointing to a table that is no longer embedded.
    for soup in soups.values():
        for card in soup.select('.deck-extra'):
            label = card.select_one('.dx-label').get_text(' ', strip=True)
            if not card.select_one('.expected-out'):
                for note in card.select('.dx-note'):
                    if any(t in note.get_text() for t in ('這段輸出','這一張表','這張表','左上','以下輸出')):
                        note.clear()
                        note.append('完整結果可在原課程 Lab 查閱。')
    if ch == 1:
        # These are explicit removals, not candidates for restoration in details.
        visible = ''.join(bodies.values())
        for forbidden in ('同一組資料，親手比較摘要','中位數的穩健性與相對效率','資料表的形狀、合併鍵與來源'):
            assert forbidden not in visible, forbidden
        s = soups['ideas']
        wrap(s, list(s.contents), 'w01-detail-statistical-ideas', '延伸閱讀：十個統計思想的背景與用途')
        s.insert(0, fragment('<p>統計學習的工具各自解決不同問題：EDA 幫我們先認識資料，bootstrap 描述估計的不確定性，正則化則調整模型的彈性。先理解眼前要回答的問題，再選擇合適的工具；各思想的歷史可展開閱讀。</p>').p)
        for sec, pid, title in [('datasets','w01-detail-dataset-catalog','延伸閱讀：完整資料集總表'),('toolchain','w01-detail-resources','延伸閱讀：資料平台與工具資源')]:
            s=soups[sec]
            for n in list(meaningful(s)):
                if n.name=='div' and n.find('table'):
                    wrap(s,[n],pid,title);break
    if ch == 2:
        old=soups['curse']
        q=old.select_one('#qCurOptions').find_parent(class_='quiz-box');q.extract()
        # Retain the numerical material beginning at the geometry setup; the
        # empirical low-dimensional slogan and duplicate conclusion are omitted.
        start=next(n for n in old.find_all('p',recursive=False) if '那麼問題變成' in n.get_text())
        earlier=list(start.previous_siblings)
        for n in earlier:n.extract()
        for n in old.find_all('div',class_='info-box',recursive=False):n.extract()
        main=r'''<p>維度增加後，資料會更難在每個方向上都靠得很近。為了湊到足夠的鄰居，往往需要擴大鄰域；鄰域太大時，就不能期待裡面的 f 幾乎不變。</p>

<p>實際表現還取決於資料量、有效維度、分布及 f 的形狀。更多同類資料可能讓我們用較小比例的鄰域估計；因此要共同選擇鄰居數或寬度，不能只看「樣本數很多」就認為局部估計一定可靠。</p>'''
        main += quiz('qCur','QUIZ · 維度詛咒','資料有許多預測變數。使用 KNN 時，為什麼不能只因為樣本數很多，就直接認定「最近鄰」一定夠局部？',[
            (True,'高維時，湊到足夠鄰居可能需要較寬的範圍；還要評估有效維度、鄰居數與資料分布','對。鄰域內資料多可降低平均的不穩定性，但範圍太寬可能混合不同的反應關係。應用驗證資料選擇鄰居數，而不是用單一維度或樣本數門檻斷言。'),
            (False,'只要超過四個變數，KNN 就必定不能使用','四維不是普遍的失效門檻；資料可能有低維結構，表現也取決於分布、樣本數與目標函數。'),
            (False,'KNN 只能分類，不能用來迴歸','KNN 迴歸就是對鄰居的反應值取平均；這裡的問題是鄰域是否適合，與能否定義迴歸方法不同。')])
        soups['curse']=fragment(main+detail('w02-detail-geometry','計算細節：高維球體、球殼與鄰域半徑',str(old)))
        pagejs += "\nHC.onDetail('w02-detail-geometry', { open: () => { w02curDraw(); } });\n"
    if ch == 3:
        s=soups['slr'];start=next(n for n in s.find_all('p',recursive=False) if '接著把同一件事換個角度看' in n.get_text())
        end=heading(s,'講義完整實作：建立並擬合 OLS 模型');nodes=[]
        for n in [start,*list(start.next_siblings)]:
            if n is end:break
            nodes.append(n)
        outer=wrap(s,nodes,'w03-detail-rss-surface','計算細節：RSS 參數曲面與最小平方解')
        p=s.select_one('#w03proofOls')
        if p:outer.select_one('.detail-body').append(p.extract())
        p=soups['mlr'].select_one('#w03proofFWL')
        target=heading(soups['mlr'],'一次檢定一組係數：部分 F 檢定')
        if p and target:target.insert_before(p.extract())
        pagejs += "\nHC.onDetail('w03-detail-rss-surface', { open: () => { w03rssRender(); } });\n"
    if ch == 4:
        p=soups['lda'].select_one('#w04proofFisher');target=heading(soups['lda'],'把生成式模型的參數估出來')
        if p and target:target.insert_before(p.extract())
    if ch == 5:
        s=soups['bootstrap']
        # Keep each proof beside its own subject, rather than hiding unrelated
        # portfolio algebra inside the permutation/conformal groups.
        for pid,title in [('w05proofPortfolio','計算細節：投資組合權重與重抽樣唯一筆數')]:
            p=s.select_one('#'+pid)
            if p:
                q=s.select_one('#qBootOptions').find_parent(class_='quiz-box')
                q.insert_after(p.extract())
        p=s.select_one('#w05proofJackknife');target=heading(s,'固定設計下用bootstrap估預測誤差')
        if p and target:target.insert_before(p.extract())
    if ch == 6:
        s=soups['lasso'];p=s.select_one('#w06proofMAP');target=heading(s,'Lasso 的零係數條件與座標更新')
        if p and target:target.insert_before(p.extract())
        # The safe Pipeline principle stays visible; the actual full code is optional.
        fold_heading(soups['ridge'],'折內標準化的概念寫法','w06-detail-scaling-code','完整實作：折內標準化的 Pipeline',stop_core=True)
    for sec, html in BRIDGES.get(ch,{}).items():
        before_quiz(soups[sec],html.replace('比较','比較'))
    # An earlier heading stops at the still-visible next heading; never wrap
    # an already-folded sibling group inside another reading-detail.
    for sec, groups in GROUPS.get(ch,{}).items():
        for text, slug, title in groups:
            fold_heading(soups[sec],text,f'{prefix}-detail-{slug}',title)
    for sec,s in soups.items():
        fold_labs(s,prefix,sec)
        # Complete lookup/provenance topics are grouped by meaning, never row count.
        if sec == 'reference':
            if heading(s, '公式速查'):
                fold_heading(s, '公式速查', f'{prefix}-detail-formula-reference', '計算細節：完整公式速查', stop_core=True)
            notes = [n for n in meaningful(s) if 'ver-note' in n.get('class', [])]
            if notes:
                wrap(s, notes, f'{prefix}-detail-reproducibility', '延伸閱讀：重現方式與環境版本')
        for label in s.select('details.reading-detail .quiz-label'):
            text = label.get_text(' ', strip=True)
            if text.startswith('QUIZ'):
                label.string = text.replace('QUIZ', '延伸自測', 1)
        for d in s.select('details.reading-detail'):
            assert not d.has_attr('open')
            assert len(d.find_parents('details')) == 0, d.get('id')
        for d in s.select('details'):
            assert len(d.find_parents('details')) <= 1, (ch,sec,d.get('id'))
    return {k:str(s) for k,s in soups.items()},pagejs
