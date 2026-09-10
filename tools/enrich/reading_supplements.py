"""Reading layers for the sixteen supplement/prerequisite pages.

Source strings are preserved verbatim inside named details. This module is private
content composition, not a shared renderer; the public detail/lifecycle contract
remains in lib and shared.js. No HTML parser dependency or source rewriting.
"""
import html
import re
from lib import detail


def _inside(body, pos):
    prefix = body[:pos]
    return len(re.findall(r'<details\b', prefix)) > len(re.findall(r'</details\s*>', prefix))


def _end(body, start, tag='div'):
    depth = 0
    for m in re.finditer(r'</?' + tag + r'\b[^>]*>', body[start:]):
        depth += -1 if m.group().startswith('</') else 1
        if depth == 0:
            return start + m.end()
    raise ValueError('Unclosed content element: ' + body[start:start + 80])


def _title(raw):
    return html.unescape(re.sub(r'<[^>]*>', '', raw)).strip()


def _quiz(body, qid):
    marker = 'id="' + qid + 'Options"'
    pos = body.find(marker)
    if pos < 0:
        if qid in {'qBayes','qEx4'}: return body, ''
        raise ValueError('Missing quiz: ' + qid)
    start = body.rfind('<div class="quiz-box">', 0, pos)
    assert start >= 0, qid
    end = _end(body, start)
    return body[:start] + body[end:], body[start:end]


def _take_quizzes(bodies, section, ids):
    units = []
    for qid in ids:
        bodies[section], q = _quiz(bodies[section], qid)
        units.append(q)
    return '\n'.join(units)


def _heading(body, title, pid, label, *, through_end=False, suffix=''):
    hs = [m for m in re.finditer(r'<h[34]\b[^>]*>.*?</h[34]>', body, re.S)
          if not _inside(body, m.start())]
    candidates = [m for m in hs if _title(m.group()) == title]
    if not candidates: return body
    if len(candidates) != 1:
        raise ValueError('Heading not unique: ' + title)
    m = candidates[0]
    following = [h.start() for h in hs if h.start() > m.start()]
    following += [d.start() for d in re.finditer(r'<details[^>]*reading-detail[^>]*>', body)
                  if d.start() > m.start() and not _inside(body, d.start())]
    following.sort()
    end = len(body) if through_end or not following else following[0]
    return body[:m.start()] + detail(pid, label, body[m.start():end] + suffix) + body[end:]


def _between(body, start_text, end_text, pid, label, *, suffix=''):
    if start_text not in body or end_text not in body: return body
    a = body.index(start_text)
    a = body.rfind('<p', 0, a + 1)
    b = body.index(end_text, a)
    b = body.rfind('<', a, b + 1)
    assert a >= 0 and b > a, (start_text, end_text)
    return body[:a] + detail(pid, label, body[a:b] + suffix) + body[b:]


def _cards(body, names, pid, label):
    selected = []
    for m in re.finditer(r'<div class="deck-extra">', body):
        if _inside(body, m.start()):
            continue
        end = _end(body, m.start())
        raw = body[m.start():end]
        title = re.search(r'<div class="dx-label">(.*?)</div>', raw, re.S)
        assert title
        if names is None or any(s in _title(title[1]) for s in names):
            selected.append((m.start(), end, raw))
    if not selected:
        raise ValueError('No cards matched: ' + str(names))
    replacement = detail(pid, label, '\n'.join(s[2] for s in selected))
    for i, (a, b, _) in reversed(list(enumerate(selected))):
        body = body[:a] + (replacement if i == 0 else '') + body[b:]
    return body


def _tables(body, pid, label):
    chunks = []
    for m in re.finditer(r'<div class="table-wrap">', body):
        if not _inside(body, m.start()):
            end = _end(body, m.start())
            chunks.append((m.start(), end, body[m.start():end]))
    # Some older table helpers use a table-container; preserve those too.
    if not chunks:
        for m in re.finditer(r'<table\b[^>]*>', body):
            if not _inside(body, m.start()):
                end = _end(body, m.start(), 'table')
                chunks.append((m.start(), end, body[m.start():end]))
    for i, (a, b, raw) in reversed(list(enumerate(chunks))):
        body = body[:a] + detail(pid + '-' + str(i + 1), label, raw) + body[b:]
    return body


def _outputs(body, prefix):
    chunks = []
    for m in re.finditer(r'<div class="expected-out">', body):
        if _inside(body, m.start()):
            continue
        end = _end(body, m.start())
        raw = body[m.start():end]
        # Only long stored outputs: never hide the first short result by default.
        if len(_title(raw)) > 260:
            chunks.append((m.start(), end, raw))
    for i, (a, b, raw) in reversed(list(enumerate(chunks))):
        body = body[:a] + detail(prefix + '-out-' + str(i + 1), '查看完整 Lab 輸出', raw) + body[b:]
    return body


def _widget(body, widget_id, pid, label, suffix=''):
    at = body.index('id="' + widget_id + '"')
    starts = [m.start() for m in re.finditer(r'<div class="viz-layout"[^>]*>', body[:at])]
    assert starts, widget_id
    a = starts[-1]
    b = _end(body, a)
    return body[:a] + detail(pid, label, body[a:b] + suffix) + body[b:]


def _section(bodies, key, pid, label, intro, keep_quizzes=(), extra=''):
    quizzes = _take_quizzes(bodies, key, keep_quizzes) if keep_quizzes else ''
    bodies[key] = intro + detail(pid, label, bodies[key] + extra) + quizzes


def _paragraph(body, contains, pid, label):
    for m in re.finditer(r'<p\b[^>]*>.*?</p>', body, re.S):
        if contains in m.group() and not _inside(body, m.start()):
            return body[:m.start()] + detail(pid, label, m.group()) + body[m.end():]
    return body  # The specifically audited authored example was removed.


def _math(body, contains, pid, label):
    for m in re.finditer(r'\$\$.*?\$\$', body, re.S):
        if contains in m.group() and not _inside(body, m.start()):
            return body[:m.start()] + detail(pid, label, m.group()) + body[m.end():]
    raise ValueError('Math not found: ' + contains)


def apply_reading(stem, bodies, pagejs):
    """Mutate owned page bodies, return page JS with any required lifecycle hook."""
    n = {'deep_learning':11,'00a_why_code':12,'00b_setup':13,'00c_ai_assisted':20,
         's1_probability':21,'s2_conditional':22,'s3_distributions':23,
         's4_inference':24,'s5_bayesian':25,'s6_regression':26,
         'p1_python_basics':14,'p2_flow_functions':15,'p3_numpy':16,
         'p4_pandas':17,'p5_visualization':18,'p6_modeling_api':19}[stem]
    p = 'w' + str(n).zfill(2) + 'detail-'

    if stem == 'deep_learning':
        ex1 = _take_quizzes(bodies, 'exercises', ['qEx1','qEx2'])
        ex3 = _take_quizzes(bodies, 'exercises', ['qEx3'])
        ex4 = _take_quizzes(bodies, 'exercises', ['qEx4'])
        qp = _take_quizzes(bodies, 'multi', ['qParam'])
        bodies['single'] = _heading(bodies['single'], '官方 lab §10.9.1：先把線性基準立起來', p+'hitters', '完整實作：Hitters 的基準、網路與結果比較', through_end=True, suffix=ex4)
        bodies['multi'] = _widget(bodies['multi'], 'w11paramSvg', p+'parameters', '延伸計算：網路參數量與 softmax 性質', qp+ex1)
        bodies['multi'] = _heading(bodies['multi'], '官方 lab §10.9.2：MNIST 上的兩層網路', p+'mnist', '完整實作：MNIST 網路與比較', through_end=True)
        bodies['cnn'] = _heading(bodies['cnn'], '資料增強與移轉學習', p+'transfer', '進一步應用：資料增強與移轉學習', through_end=True)
        bodies['cnn'] = _heading(bodies['cnn'], '官方 lab §10.9.3：CIFAR-100 上的 CNN', p+'cifar', '完整實作與計算：CNN、參數量及預訓練模型', suffix=ex3)
        bodies['rnn'] = _heading(bodies['rnn'], '將時間序列整理成訓練樣本', p+'sequence-data', '延伸：時間序列輸入、落後期與評估', through_end=True)
        bodies['rnn'] = _heading(bodies['rnn'], '官方 lab §10.9.6：LSTM 與時間序列', p+'lstm', '完整實作：LSTM、NYSE 與模型表現比較')
        bodies['rnn'] = _cards(bodies['rnn'], ['詞袋 ＋'], p+'bow', '完整實作：詞袋網路')
        bodies['fitting'] = _heading(bodies['fitting'], '反向傳播：每一個參數要往哪裡更新？', p+'gradients', '計算細節：反向傳播與正則化', through_end=True)
        bodies['fitting'] = _widget(bodies['fitting'], 'w11gdChart', p+'gd-experiment', '數值實驗：起點與步長如何影響梯度下降')
        _section(bodies, 'doubledesc', p+'double-descent', '進階：內插、最小範數與雙下降', '<p>模型更大時，測試誤差不一定只升不降；但模型大小也不能代替驗證。先建立簡單基準，再用獨立資料判斷增加複雜度是否有幫助。</p>')
        bodies['exercises'] += '<p>參數計算、softmax 性質與模型結果的練習，已放在各節相應的收合延伸中。第一輪先確認你能說明各種架構保留什麼資訊，以及訓練和驗證各負責什麼。</p>'

    elif stem == '00a_why_code':
        bodies['habits'] = _cards(bodies['habits'], ['練習讀表'], p+'table-reading', '再練一次：讀取另一份示範資料')

    elif stem == '00b_setup':
        bodies['prologue'] = _tables(bodies['prologue'], p+'environments', '比較其他執行環境')
        bodies['imports'] = _cards(bodies['imports'], ['第 1 章的 imports'], p+'imports-alternative', '另一份筆記本的完整匯入清單')
        bodies['imports'] = _tables(bodies['imports'], p+'packages', '查閱：套件分工與附錄位置')
        # The default Ch02 imports and Auto/Drive path remain directly usable.
        _section(bodies, 'local', p+'local-setup', '本機練習：版本、安裝指令與 kernel 設定', '<p>期中使用電腦教室電腦。本機練習請依課程版本建立獨立環境，並確認 Jupyter 選用同一環境的 kernel；詳細步驟可在需要時展開。</p>', ['qLocal'])
        _section(bodies, 'trouble', p+'troubleshooting', '遇到問題再查：症狀、原因與排解步驟', '<p>先讀錯誤訊息最後一行，確認套件、資料路徑與正在使用的 kernel。重啟後由上到下執行，可檢查筆記本是否依賴先前殘留狀態。</p>', ['qFix'])

    elif stem == '00c_ai_assisted':
        for key, label in [('triage','詳細比較：不同任務的驗證方式'),('context','提示五要素的完整對照'),('iterate','查閱：每輪交付物與檢查項目'),('record','查閱：完整重現紀錄清單')]:
            bodies[key] = _tables(bodies[key], p+key, label)

    elif stem == 's1_probability':
        bodies['expectation'] = _heading(bodies['expectation'], '加總與加權平均', p+'expectation-rules', '計算延伸：期望值的加法規則', through_end=True)
        bodies['variation'] = _heading(bodies['variation'], '加總後的變異數，以及平均為什麼較穩定', p+'variance-rules', '計算延伸：共變異數、樣本平均與機率界限', through_end=True)
        bodies['variation'] = _math(bodies['variation'], 'E[X^2]', p+'variance-formula', '查公式：變異數的兩種寫法')
        # Unit scaling is still needed for the short public quiz/exercise.
        bodies['variation'] = _between(bodies['variation'], '手上若只有樣本', '<p><strong>大數法則', p+'sample-variance', '查公式：樣本變異數、n−1 與適用條件')

    elif stem == 's2_conditional':
        bodies['events'] = _heading(bodies['events'], '集合條件如何展開與取反', p+'set-laws', '延伸：分配律、De Morgan 與條件取反', through_end=True)
        qb = _take_quizzes(bodies, 'bayes', ['qBayes'])
        # Move the complete longer worked example and its dependent quiz together.
        bodies['bayes'] = _between(bodies['bayes'], '<strong>數值例。</strong>', '<div class="info-box', p+'bayes-example', '算一次：陽性結果與基準率', suffix=qb)
        extra = _take_quizzes(bodies, 'exercises', ['qEx4'])
        _section(bodies,'counting',p+'counting','選讀：排列、組合與完整計數練習','<p>當結果等可能，機率可以用符合條件的結果數除以全部結果數。更多計數技巧可在需要時再讀。</p>',extra=extra)

    elif stem == 's3_distributions':
        bodies['families'] = _heading(bodies['families'], '計數與等待：Poisson、Exponential', p+'count-wait', '延伸：Poisson 計數與指數等待時間', through_end=True)
        bodies['families'] = _heading(bodies['families'], '從公式算出每根柱與每一段面積', p+'distribution-formulas', '查公式與算例：各分布的 PMF／PDF')
        bodies['families'] = _tables(bodies['families'], p+'distribution-table', '查閱：四種分布的平均與變異數')
        bodies['sampling'] = _between(bodies['sampling'], '<strong>數值例。</strong>', '<div style="overflow-x', p+'sampling-example', '完整算例：25 顆骰子的平均')
        bodies['clt'] = _math(bodies['clt'], '\\xrightarrow', p+'clt-notation', '查看中央極限定理的標準化寫法')

    elif stem == 's4_inference':
        bodies['intervals'] = _heading(bodies['intervals'], '母體標準差未知：t 區間', p+'t-interval', '延伸：未知標準差的 t 區間與推導', through_end=True)
        # Keep all core definitions, SE formula and the confidence-interval interaction.
        qe = _take_quizzes(bodies,'errors',['qErrors'])
        bodies['errors'] = _heading(bodies['errors'], '算一次：同一個 5% 檢定的型二錯誤', p+'power-calculation','完整計算：型二錯誤與檢定力',through_end=True) + qe
        bodies['testing'] = _paragraph(bodies['testing'], 'z=(54.4', p+'tails-calculation', '完整算例：單尾與雙尾的 p 值')
        bodies['testing'] = bodies['testing'].replace('算一次：單尾與雙尾問的是不同問題', '用圖看單尾與雙尾')
        bodies['bootstrap'] = _math(bodies['bootstrap'], '\\widehat', p+'bootstrap-se', '查公式：由多份重抽結果計算標準誤')

    elif stem == 's5_bayesian':
        bodies['posterior'] = _heading(bodies['posterior'], '一般的更新公式與正規化', p+'bayes-density', '計算細節：一般 Bayes 密度與共軛推導', through_end=True)
        bodies['posterior'] = _between(bodies['posterior'], 'Beta 分布常用來', '<p>Beta 先驗可用', p+'beta-density', '查公式：Beta 先驗密度、正規化與更新')
        bodies['influence'] = _math(bodies['influence'], 'E[p', p+'posterior-weights', '查看後驗平均的加權分解')
        bodies['influence'] = _tables(bodies['influence'], p+'prior-comparison', '完整比較：不同先驗強度與資料量')
        bodies['likelihood']=_between(bodies['likelihood'],'假設每次投擲互相獨立','<div class="info-box',p+'likelihood-calculation','完整計算：二項概似與相對支持度')
        # The short count-update and next-trial mean remain public for qPosterior and EX4.

    elif stem == 's6_regression':
        bodies['covariance'] = _math(bodies['covariance'], 's_{xy}', p+'correlation-formula', '查公式：共變異數與相關係數')
        bodies['least_squares'] = _math(bodies['least_squares'], '\\hat b_1', p+'ols-coefficients', '查看最小平方斜率與截距公式')
        bodies['covariance']=_paragraph(bodies['covariance'],'<strong>算例。</strong>',p+'correlation-example','完整算例：從中心化乘積算相關係數')
        bodies['least_squares']=_paragraph(bodies['least_squares'],'<strong>算例。</strong>',p+'ols-example','完整算例：五筆資料的最小平方解')
        bodies['residuals']=_paragraph(bodies['residuals'],'<strong>算例。</strong>',p+'residual-example','完整算例：逐筆殘差與平方和')
        extra=_take_quizzes(bodies,'exercises',['qEx4'])
        _section(bodies,'anova',p+'anova','延伸：ANOVA 的平方和與 F 檢定','<p>比較多組平均時，需要把組間差異與組內變動一起考慮。ANOVA 的完整做法放在這裡供需要時查閱。</p>',extra=extra)

    elif stem == 'p1_python_basics':
        for key,names,label in [('slice',['slice 物件'],'另一種寫法：slice 物件'),('dict',['用字典建'],'課程應用：以字典建立 pandas 資料'),('str',['format 與格式規格','迴圈裡的格式化'],'完整實作：逐欄格式化與迴圈輸出')]:
            bodies[key]=_cards(bodies[key],names,p+key+'-lab',label)

    elif stem == 'p2_flow_functions':
        bodies['cond']=_cards(bodies['cond'],['& 與 | 混用'],p+'compound-filter','跨章應用：混合多種資料篩選條件')
        bodies['loop']=_cards(bodies['loop'],['巢狀迴圈'],p+'nested-loop','延伸：巢狀迴圈的加總')
        qf=_take_quizzes(bodies,'func',['qFunc'])
        bodies['func']=_heading(bodies['func'],'lambda 是只有一個運算式的函式',p+'lambda','跨套件應用：lambda 與資料篩選',through_end=True)
        a=bodies['func'].index('<p>假設你要比較')
        # Separate the lambda detail, so no reading-detail nests inside another.
        b=bodies['func'].index('<details class="qa-item reading-detail"',a)
        bodies['func']=bodies['func'][:a]+detail(p+'function-lab','完整應用：模型評估函式、資料流與重用',bodies['func'][a:b])+bodies['func'][b:]+qf
        bodies['func']='<p>函式用 <code>return</code> 交回結果；沒有寫 return 時，回傳 <code>None</code>，不會自動取最後一行。</p>'+bodies['func']
        bodies['scope']=_between(bodies['scope'],'這個進階應用同樣在重抽樣方法','<div class="viz-layout"',p+'bootstrap-function','跨章應用：boot_SE 的預設引數與執行準備')
        bodies['err']=_cards(bodies['err'],None,p+'traceback','查看課程中的完整錯誤訊息')
        pagejs += r'''
HC.onDetail('w15detail-function-lab', {close() {
  if (w15fnTimer) { clearTimeout(w15fnTimer); w15fnTimer = null; }
  document.querySelectorAll('#w15detail-function-lab button[onclick="w15fnPlay()"]')
    .forEach(button => { button.textContent = '▶ 重新播放'; button.setAttribute('aria-pressed', 'false'); });
}});
'''

    elif stem == 'p3_numpy':
        for key,names,label in [('reshape',['改 reshape 出來'],'完整實驗：修改共用資料前後的輸出'),('index',['長度不一樣','真的要子矩陣','等距切片'],'延伸：索引錯誤與其他子矩陣寫法'),('bool',['布林也能配 np.ix_'],'延伸：布林遮罩與子矩陣'),('agg',['變異數的三種'],'完整實作：變異數的三種等價計算'),('rand',['相關係數矩陣'],'跨章應用：相關係數矩陣')]:
            bodies[key]=_cards(bodies[key],names,p+key+'-lab',label)
        bodies['index']='<p>記憶體也有差別：基本切片可共享原陣列，整數陣列的進階索引會建立複本。對本頁連續儲存的 A，reshape 可以共享資料；需要獨立修改時應明確複製。</p>'+bodies['index']
        # The paired-index counterexample stays open; so do axis and broadcast examples.

    elif stem == 'p4_pandas':
        for number,(title,label) in enumerate([('讀入與輸出資料表','延伸：Excel／CSV 輸出與完整參數'),('摘要、逐元素運算與累積量','延伸：對齊、逐元素計算與累積量'),('依標籤或資料值排序','延伸：標籤排序與資料值排序')]):
            bodies['view']=_heading(bodies['view'],title,p+'view-'+str(number),label)
        bodies['select']=_heading(bodies['select'],'把車名設成索引，以及重複標籤',p+'named-index','延伸：車名索引、重複標籤與完整輸出',through_end=True)
        bodies['na']=_heading(bodies['na'],'數字儲存，不代表一定當連續量分析',p+'categorical','跨章應用：category 與模型中的類別效果',through_end=True)
        bodies['na']=_cards(bodies['na'],['reindex 也'],p+'reindex-missing','延伸：重新索引產生的缺值')
        bodies['join']=_cards(bodies['join'],['切成三塊'],p+'concat-pieces','查看完整分塊與中間輸出')

    elif stem == 'p5_visualization':
        qa=_take_quizzes(bodies,'anat',['qAnat'])
        bodies['anat']=_heading(bodies['anat'],'把目前這張 Figure 保存下來',p+'save-figures','延伸：多種檔案格式、dpi 與修改後另存',through_end=True)
        bodies['anat']=_heading(bodies['anat'],'Seaborn 函式地圖：先選問題，再選控制層級',p+'function-map','完整函式地圖與選項練習')+qa
        bodies['anat']=_cards(bodies['anat'],['2×3 的子圖'],p+'subplot-grid','延伸：完整子圖網格')
        bodies['model']=_heading(bodies['model'],'函數曲面：等高線與色塊',p+'function-grid','跨章應用：函數網格、contour 與 imshow',through_end=True)
        for key,names,label in [('dist',['依類別分色與堆疊'],'更多畫法：分色與堆疊'),('rel',['用點的大小','joint 與 pair'],'更多畫法：大小編碼、joint 與 pair'),('cat',['點估計圖'],'另一種畫法：點估計與誤差線')]:
            bodies[key]=_cards(bodies[key],names,p+key+'-more',label)

    elif stem == 'p6_modeling_api':
        bodies['cv']=_heading(bodies['cv'],'把標準化與模型交給同一條 Pipeline',p+'ridge-pipeline','跨章完整實作：Hitters、Ridge 與 Pipeline',through_end=True)
        bodies['cv']=_cards(bodies['cv'],['留一交叉驗證','重複切分'],p+'cv-lab','完整實作：留一法與重複切分的分數')
        bodies['summary']=_cards(bodies['summary'],['完整的 summary'],p+'full-summary','查閱完整模型報表')
        bodies['split']=_cards(bodies['split'],['三種常見','三個次數'],p+'metric-comparison','完整比較：誤差指標與多項式次數')
        bodies['split']=_widget(bodies['split'],'w19cvChart',p+'cv-comparison','跨章例子：三種多項式的驗證誤差')
        bodies['skl']=_cards(bodies['skl'],['評分'],p+'score-metrics','完整輸出：多種評分指標')
        bodies['cv']='<p>比較兩個模型，先讓它們使用相同切分，再看每次分數的配對差異。各自的平均和標準差可以摘要結果，但不足以單獨判定哪個模型較好。</p>'+bodies['cv']

    # Long stored outputs are independently optional; short runnable examples stay visible.
    if stem.startswith('p'):
        for key in bodies:
            if key != 'reference':
                bodies[key] = _outputs(bodies[key], p+key)
    # Generated bibliography links remain in GEN. Only the authored long lookup body folds.
    bodies['reference'] = '<p>需要核對完整公式、比較表或實作時，再展開下方速查。</p>' + detail(p+'reference','查閱完整速查與延伸提醒',bodies['reference'])
    return pagejs
