"""第五章後半的講義主題與延伸閱讀；保留原 Lab、動畫及錨點。"""
from bs4 import BeautifulSoup
from lib import detail, hl, table

PERMUTATION_CODE = """from sklearn.datasets import load_iris
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, permutation_test_score

# 承接講義的分類器置換檢定；此例是延伸實作，不是 Ch05 原 Lab。
X, y = load_iris(return_X_y=True)
model = make_pipeline(StandardScaler(), SVC(kernel="linear", C=1))
cv = StratifiedKFold(5, shuffle=True, random_state=0)
score, null_scores, p_value = permutation_test_score(
    model, X, y, cv=cv, scoring="accuracy",
    n_permutations=199, random_state=0, n_jobs=1)
print("原始標籤的 CV accuracy", score)
print("置換標籤後的平均 accuracy", null_scores.mean())
print("置換檢定 p-value", p_value)
"""


def refs(*pairs):
    return '<p>延伸來源：' + '／'.join(
        f'<a href="{url}" target="_blank" rel="noopener">{name}</a>'
        for name, url in pairs) + '</p>'


PAIRING = r"""
<h4>配對資料要一起重抽</h4>
<p>Portfolio 的一列是同一期的兩個報酬 $(X_i,Y_i)$。同一期兩個資產的共同漲跌決定共變異數，因此不能把 $X$ 與 $Y$ 分別洗牌或分別重抽；那會破壞原本的配對，回答另一個問題。每次抽的是列索引，兩欄一起跟著走。Lab 的 <code>alpha_func(data, idx)</code> 正是先取同一組 <code>idx</code>，再算兩欄的樣本共變異數。</p>
<p>權重公式的推導與分母為正的條件，見本節開頭 $\alpha$ 公式下方的證明。</p><p>三筆觀測的重抽例子也要區分「位置」與「不同資料」：索引 $(3,1,3)$ 仍有三筆，但第三列出現兩次，第二列完全沒出現。對樣本平均數可列出全部 $3^3=27$ 個等機率索引組合；對 Portfolio 權重，若重抽後全是同一列，樣本共變異數可能退化，估計量便未必有定義。抽出索引後，還要確認重抽資料能不能算出要研究的統計量；資料退化時，bootstrap 估計也可能失去定義。</p>
"""

WHY_REPLACE = r"""
<h4>把樣本當成母體：plug-in 的想法</h4>
<p>我們想知道的是：如果能從母體 $P$ 一再抽出大小 $n$ 的新資料，估計量 $\hat\theta$ 會怎麼波動。$P$ 未知，bootstrap 就用手上資料的<strong>經驗分布</strong> $\hat P$（每筆機率 $1/n$）代替它，這叫 plug-in 原則。接下來在 bootstrap 世界裡照做一次「抽樣 → 估計」：</p>
$$\text{真實世界：}\ P\ \xrightarrow{\text{抽 }n\text{ 筆}}\ Z\ \to\ \hat\theta,\qquad
\text{bootstrap 世界：}\ \hat P\ \xrightarrow{\text{有放回抽 }n\text{ 筆}}\ Z^{*}\ \to\ \hat\theta^{*}.$$
<p>直覺是：$\hat\theta^{*}$ 在 $\hat\theta$ 周圍的散布，模仿 $\hat\theta$ 在真值 $\theta$ 周圍的散布。所以 $\hat\theta^{*}$ 的標準差可以拿來估 $\mathrm{SE}(\hat\theta)$。</p>
<h4>為什麼要放回</h4>
<ul>
<li><strong>模擬獨立抽樣。</strong>原資料被假設成從 $P$ 獨立抽出的 $n$ 筆。從 $\hat P$ 抽一筆，就是在 $n$ 筆中等機率挑一筆；放回之後下一次抽籤面對的仍是同一個 $\hat P$，所以 $n$ 次抽籤互相獨立、同分布，結構和真實世界的抽樣一樣。</li>
<li><strong>不放回就沒有變異。</strong>不放回地抽滿 $n$ 筆，得到的永遠是原資料的某種排列；平均數、$\hat\alpha$ 這類與順序無關的統計量每次都相同，量不出任何抽樣變異。</li>
<li><strong>重複與缺席正是變異的來源。</strong>有放回時，有的觀測出現兩三次、有的沒出現，每份 $Z^{*}$ 的組成都不同，就像真實世界每次抽樣都會抽到不同的人。</li>
</ul>
<h4>這個近似成立需要什麼條件</h4>
<ul>
<li><strong>觀測彼此獨立且同分布（iid）。</strong>逐筆重抽假設每一筆是獨立的抽樣單位。時間序列、同一病人的重複測量、群集抽樣等資料，要改抽區塊或群組，讓重抽單位對應真正獨立的單位（見下方區塊 bootstrap）。</li>
<li><strong>樣本要能代表母體的變異。</strong>$\hat P$ 只會產生原資料裡出現過的值。樣本太小、或抽樣本身有偏差（例如只調查某一群人），$\hat P$ 就不像 $P$；bootstrap 只能重現手上資料的樣子，無法補救不具代表性的樣本，增加 $B$ 也沒用。</li>
<li><strong>估計量對分布的變化要夠平滑。</strong>平均數、迴歸係數、$\hat\alpha$ 這類量通常沒問題；樣本最大值這類端點統計量常不適用：bootstrap 樣本的最大值永遠不超過原資料最大值。尾端分位數在尾端觀測太少，或分位位置隨樣本量逼近端點時，近似也可能失準（見下方「bootstrap 什麼時候會失效？」）。</li>
</ul>
<p>這些條件說的是「bootstrap 世界和真實世界夠像」。在這些條件，加上適當的矩條件（例如平均數需要有限變異數；$\hat\alpha$ 還要求分母不退化）成立時，bootstrap 不必假設常態，也不必推導 $\mathrm{SE}$ 的公式；條件不成立時，程式照樣算得出數字，但它不再描述估計量真正的波動。</p>
"""

BLOCK = r"""
<h4>為什麼不能把時間序列的每筆觀測獨立重抽？</h4>
<p>假設每天的溫度有正向自我相關，今天偏高，明天也往往偏高。逐筆重抽會把連續的高溫段打散，重抽序列便不再有同樣的相依性。對平均數，差別可以直接從變異數展開看見：</p>
$$\operatorname{Var}(\bar X)=\frac1{n^2}\left[\sum_i\operatorname{Var}(X_i)+2\sum_{i\lt j}\operatorname{Cov}(X_i,X_j)\right].$$
<p>正共變異數增加平均數的變異；逐筆 bootstrap 打散相依結構後，可能漏掉這部分變異。方向仍取決於相依型態與統計量，不能斷言所有相依資料的標準誤都必定偏小。</p>
<p><strong>移動區塊 bootstrap</strong>先取長度 $l$ 的所有連續區塊，起點可為 1 到 $n-l+1$；再有放回抽區塊、按抽到的順序串接，直到至少 $n$ 筆，最後裁成 $n$ 筆。區塊內原本的先後與相關被保留，區塊接縫則不保留原序列的全部相依性。非重疊區塊、循環區塊與隨機區塊長度是不同版本，使用時要交代採用哪一種。</p>
<p>例如序列 1 到 8、區塊長度 3，移動區塊有 $(1,2,3),(2,3,4),\ldots,(6,7,8)$。抽到起點 4、1、5，串成 $(4,5,6,1,2,3,5,6,7)$，裁前 8 筆後才重算估計量。重複的是整個步驟，不是只拿一次亂序結果當作所有樣本。</p>
<p>區塊太短可能保留不了主要相依；太長又讓可重新組合的單位太少，估計不穩。平穩性、長期趨勢與季節性也會影響做法：若資料生成方式隨時間改變，單純抽區塊並不能自動處理。先判斷資料有哪些相依關係，再選區塊版本與長度，並檢查改變長度時結果是否穩定。</p>
<p>群組資料同樣要先決定重抽的單位。例如病人內重複觀測相關、病人之間可視為獨立，就可考慮抽整位病人而非逐次就診；是否還要在病人內重抽，取決於研究的抽樣設計。bootstrap 的重抽單位與前面 GroupKFold 的群組界線都來自資料結構，但兩者的目的不同：一個估不確定性，一個評估未見群組的預測。</p>
""" + refs(
    ('講義的區塊 bootstrap 討論', 'https://stats.stackexchange.com/questions/25706/how-do-you-do-bootstrapping-with-time-series-data'),
    ('講義的區塊抽樣應用文獻', 'https://www.sciencedirect.com/science/article/pii/S0003267000008503'),
    ('arch 官方範例：時間相依資料的區塊與區間', 'https://arch.readthedocs.io/en/latest/bootstrap/bootstrap_examples.html'))

PREDICTION = r"""
<h4>平均曲線的不確定性，不等於新觀測的不確定性</h4>
<p>講義先將觀測 $(x_i,y_i)$ 配對重抽、每次重新擬合，再在同一組 $x$-grid 評估曲線。每個 grid 點的重抽分位數描述平均曲線的估計不確定性，屬於逐點區間。它不涵蓋新觀測本身的誤差，也不是整條曲線同時涵蓋的區間。</p>
<p>用車子資料想：我們問「100 horsepower 的車平均 mpg 大約多少」，與「下一台 100 horsepower 的車會有多少 mpg」，後者還有個別車輛的變動。即使平均曲線估得很準，新車的 mpg 仍會分散。如果只重抽係數或擬合線，再取曲線的分位數，就會漏掉新觀測的誤差。</p>
<p>要得到新觀測的預測區間，必須在係數的重抽變異之外，再加入新觀測本身的誤差。講義附錄只列出連結，建構方法（殘差 bootstrap、保形預測等）可從下方連結延伸閱讀。</p>
""" + refs(
    ('statsmodels：重抽 LOWESS 曲線的逐點區間', 'https://www.statsmodels.org/stable/examples/notebooks/generated/lowess.html'),
    ('講義的 bootstrap 預測區間討論', 'https://stats.stackexchange.com/questions/226565/bootstrap-prediction-interval'),
    ('MAPIE 官方文件：預測區間與保形方法', 'https://mapie.readthedocs.io/en/latest/index.html'))

JACKKNIFE = r"""
<h4>刪掉一筆，量出估計量對每筆資料的敏感度</h4>
<p>Jackknife 不用隨機重抽，而是第 $i$ 次刪掉第 $i$ 筆資料，得到 $\hat\theta_{(-i)}$，總共 $n$ 次。令刪一估計的平均為 $\bar\theta_{(-)}$，其標準誤估計為</p>
$$\widehat{SE}_{jack}=\sqrt{\frac{n-1}{n}\sum_{i=1}^n(\hat\theta_{(-i)}-\bar\theta_{(-)})^2}.$$
<p>公式前面的 $(n-1)/n$ 用來校正刪一估計值的變動量。各次只刪一筆，刪一估計值的變動通常比 $n$ 筆樣本重新抽出的變動小，不能直接把 $n$ 個刪一估計的普通標準差當標準誤。</p>
<p>樣本平均數能精確驗算：$\bar x_{(-i)}=(n\bar x-x_i)/(n-1)$，刪一估計的平均仍是 $\bar x$。代入上式得到 $\widehat{SE}_{jack}=s/\sqrt n$，與獨立觀測的樣本平均數標準誤一致。例如資料 $(2,4,9)$，平均 5，$s^2=13$，標準誤是 $\sqrt{13/3}\approx2.082$。</p>
<p>Jackknife 常適用於對單筆資料影響平滑的統計量；中位數、樣本最大值等非平滑或端點問題不能一概套用。與 bootstrap 相比，它只有 $n$ 個決定性的刪一樣本，常較省計算，但不會給出同樣豐富的重抽分布。</p>
""" + table(['方法','每次怎麼產生樣本','主要用途與限制'],[
    ['Bootstrap','從 $n$ 筆有放回抽 $n$ 筆，重複 $B$ 次','近似估計量抽樣分布；必須選對重抽單位'],
    ['Jackknife','逐次刪一筆，得到 $n$ 份大小 $n-1$ 的樣本','估標準誤；對非平滑統計量有限制'],
    ['Permutation','依虛無假設允許的交換方式重排標籤或觀測','近似虛無分布與 p-value；交換性與設計必須合理'],
]) + refs(
    ('講義的 Jackknife 說明', 'https://en.wikipedia.org/wiki/Jackknife_resampling'),
    ('講義的 Jackknife 與 bootstrap 比較', 'https://stats.stackexchange.com/questions/249333/comparison-of-the-jacknife-vs-the-bootstrap'))

PERMUTATION = r"""
<h4>Bootstrap 與置換檢定各在近似什麼分布？</h4>
<p>Bootstrap 通常從經驗分布重抽，問估計量在重複抽樣時如何波動；置換檢定則依虛無假設，把允許交換的部分重排，問「如果沒有這個關係，會得到多極端的統計量」。兩者都會重複計算；讀結果之前，先確認近似的是抽樣分布還是虛無分布。</p>
<p>例如兩組的平均數差，先固定每組筆數並計算觀測差 $T_{obs}$。若虛無假設使觀測在兩組間可交換，就把組別標籤重排、重新計算差 $T$。隨機做 $B$ 次雙尾置換，可用</p>
$$\hat p=\frac{1+\sum_{b=1}^B I(|T_b|\ge |T_{obs}|)}{B+1}.$$
<p>雙尾時兩邊都要取絕對值；只寫 $T_b\ge |T_{obs}|$ 會漏掉負方向的極端結果。加一是隨機置換常用的 Monte Carlo 校正，使原始排列也被計入比較；完整枚舉所有允許排列時，則直接以其精確比例計算。$B=199$ 的隨機置換最小 p-value 是 1/200，不可能宣稱得到了 0。</p>
<p>置換要求的是<strong>虛無假設下的交換性</strong>。同一病人的重複紀錄、配對實驗、時間序列不能任意逐筆洗牌；應尊重配對、區塊或隨機分派設計。兩組平均相同也不必表示整個分布相同，因此簡單重排標籤檢定的條件，比「只要平均相同」更強。</p>
<h4>分類器：標籤重排後，完整重新訓練</h4>
<p>講義的分類例子保留 $X$、重排 $y$。原始資料先得到交叉驗證分數；每次置換標籤後，重新擬合每一折的模型、重新得到 CV 分數，形成模型在虛無假設下的分數分布。不能只洗牌已算好的預測值，或固定原始資料訓練好的分類器，因為那沒有重做學習程序。</p>
<p>sklearn 的 score 一律愈大愈好，所以 <code>permutation_test_score</code> 比較置換分數是否<strong>大於或等於</strong>原始分數。若使用負 MSE，也依這個方向比較，不另把 MSE 的「小才好」直接貼到 score 上。前處理包進 Pipeline；若原始程序含調參或特徵選擇，置換時也要重新執行同樣的選擇程序。</p>
""" + hl(PERMUTATION_CODE, block_id='w05-alignment-permutation-code') + r"""
<p>這個例子沿用官方分類器示範的 Iris，用分層 CV 和線性 SVM；是講義附錄的延伸，而不是 Portfolio 重抽 Lab 的結果。低 p-value 表示觀測分數相對於這套置換程序很不尋常，支持特徵與標籤之間存在模型能利用的關係；不表示分數一定足夠高、模型一定適合部署，也不是虛無假設為真的機率。高 p-value 也可能是模型沒利用到關係或檢定力不足，不能證明完全沒有關係。</p>
""" + refs(
    ('講義：Permutation test', 'https://en.wikipedia.org/wiki/Permutation_test'),
    ('scikit-learn：分類分數的置換檢定示範', 'https://scikit-learn.org/stable/auto_examples/feature_selection/plot_permutation_test_for_classification.html#test-with-permutations-the-significance-of-a-classification-score'),
    ('permutation_test_score：分數、群組與 p-value', 'https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.permutation_test_score.html'))

OOB = r"""
<h4>為什麼「bootstrap 訓練、原始資料驗證」會重疊？</h4>
<p>上方的推導已說明：每份重抽資料平均只含約三分之二的不同觀測，所以「重抽資料訓練、全部原始資料驗證」有大量重疊。補救的方向是只對這次沒抽到的 OOB 觀測預測，避開直接的觀測重疊。</p>
<p>例如原始索引 1 到 5，抽到 $(1,1,3,4,4)$，這次的 OOB 是 2、5。下一次抽到 $(2,3,3,5,5)$，OOB 是 1、4。各次可評估的資料與數目都不同；同一觀測會在多個重抽模型的 OOB 出現，模型也不是彼此獨立的。</p>
<p>OOB 解決的是訓練／評估重疊，並沒有讓 bootstrap 訓練集等同於 $n$ 筆獨立的新觀測。不同訓練規模、重複列、調參使用 OOB 以及如何平均分數，都會影響估計的解讀。講義因此以 CV 作為本章預測誤差評估的主線；第八章 bagging／random forest 再使用 OOB 對集成程序做內部評估。</p>
"""


def augment(bodies):
    result = dict(bodies)
    soup = BeautifulSoup(result['bootstrap'], 'html.parser')
    for anchor, body in [
        ('w05-detail-block-bootstrap', BLOCK),
        ('w05-detail-bootstrap-intervals', PREDICTION),
        ('w05-detail-jackknife-se', JACKKNIFE),
        ('w05-detail-permutation', PERMUTATION),
    ]:
        node = soup.find(id=anchor)
        if node is None:
            raise ValueError('Missing teaching anchor: ' + anchor)
        content = node.find(class_='detail-body', recursive=False)
        content.clear()
        content.append(BeautifulSoup(body, 'html.parser'))
    node = soup.find(id='w05-detail-lab-bootstrap-1')
    if node is None:
        raise ValueError('Missing Portfolio lab block')
    node.insert_before(BeautifulSoup(detail('w05-detail-bootstrap-pairing', '延伸閱讀：配對重抽、退化樣本與重抽次數', PAIRING), 'html.parser'))
    ciheading = soup.find(id='w05-boot-ci')
    if ciheading is None:
        raise ValueError('Missing bootstrap CI heading')
    ciheading.insert_before(BeautifulSoup(detail('w05-detail-boot-why-replace', '延伸閱讀：為什麼要有放回重抽？直覺與前提', WHY_REPLACE), 'html.parser'))
    node = soup.find(id='w05-detail-two-thirds')
    if node is None:
        raise ValueError('Missing two-thirds derivation')
    node.insert_after(BeautifulSoup(detail('w05-detail-bootstrap-oob', '延伸閱讀：重抽重疊、OOB 與預測誤差', OOB), 'html.parser'))
    # 延伸收合放回各自對應的講義小節，不全部堆在節末。
    block = soup.find(id='w05-boot-block')
    node = soup.find(id='w05-detail-bootstrap-intervals')
    if block is None or node is None:
        raise ValueError('Missing interval detail or block heading')
    block.insert_before(node.extract())
    node = soup.find(id='w05-detail-jackknife-se')
    if node is None:
        raise ValueError('Missing jackknife detail')
    node.insert_before(BeautifulSoup('<h3 id="w05-boot-appendix">講義附錄：其他重抽樣方法</h3>\n<p>講義最後的附錄列出 jackknife 與置換檢定，作為 bootstrap 以外的重抽樣工具；兩者都是選讀，可展開閱讀。</p>', 'html.parser'))
    result['bootstrap'] = str(soup)
    return result
