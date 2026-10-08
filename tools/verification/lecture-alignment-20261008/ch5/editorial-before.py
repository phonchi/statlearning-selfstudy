"""第五章後半的講義主題與延伸閱讀；保留原 Lab、動畫及錨點。"""
from bs4 import BeautifulSoup
from lib import detail, hl, table

PORTFOLIO_CODE = """import numpy as np
from ISLP import load_data

Portfolio = load_data("Portfolio")
xy = Portfolio[["X", "Y"]].to_numpy()

def alpha(data):
    cov = np.cov(data, rowvar=False, ddof=1)
    denominator = cov[0, 0] + cov[1, 1] - 2 * cov[0, 1]
    if denominator <= 0:
        raise ValueError("X-Y 沒有變異，最小風險權重無法唯一決定")
    return (cov[1, 1] - cov[0, 1]) / denominator

rng = np.random.default_rng(0)
B = 1000
estimates = np.empty(B)
for b in range(B):
    index = rng.choice(len(xy), size=len(xy), replace=True)
    estimates[b] = alpha(xy[index])  # X、Y 必須用同一組索引

estimate = alpha(xy)
se = estimates.std(ddof=1)
q05, q95 = np.quantile(estimates, [0.05, 0.95])
print("估計權重與 bootstrap SE", estimate, se)
print("90% percentile CI", q05, q95)
print("90% basic CI", 2 * estimate - q95, 2 * estimate - q05)
"""

PREDICTION_CODE = """import numpy as np
import statsmodels.api as sm
from ISLP import load_data

Auto = load_data("Auto")
X = sm.add_constant(Auto[["horsepower"]].to_numpy())
y = Auto["mpg"].to_numpy()
fit = sm.OLS(y, X).fit()
x0 = np.array([1.0, 100.0])
mu0 = x0 @ fit.params

# 固定 X、獨立且同變異誤差的殘差 bootstrap。
leverage = fit.get_influence().hat_matrix_diag
residual = fit.resid / np.sqrt(1 - leverage)
residual = residual - residual.mean()
rng = np.random.default_rng(0)
B = 1000
mean_draws = np.empty(B)
prediction_errors = np.empty(B)
for b in range(B):
    y_star = X @ fit.params + rng.choice(residual, len(y), replace=True)
    fit_star = sm.OLS(y_star, X).fit()
    mean_draws[b] = x0 @ fit_star.params
    new_error = rng.choice(residual)
    prediction_errors[b] = mu0 - mean_draws[b] + new_error

print("100 horsepower 的平均預測", mu0)
print("平均曲線的近似 percentile CI",
      np.quantile(mean_draws, [0.025, 0.975]))
print("新車 mpg 的近似 prediction interval",
      mu0 + np.quantile(prediction_errors, [0.025, 0.975]))
"""

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
<h4>重抽的單位是「一筆完整觀測」</h4>
<p>Portfolio 的一列是同一期的兩個報酬 $(X_i,Y_i)$。同一期兩個資產的共同漲跌決定共變異數，因此不能把 X 與 Y 分別洗牌或分別重抽；那會破壞原本的配對，回答另一個問題。每次抽的是列索引，兩欄一起跟著走。Lab 的 <code>alpha_func(data, idx)</code> 正是先取同一組 <code>idx</code>，再算兩欄的樣本共變異數。</p>
<p>權重公式的分母是 $\operatorname{Var}(X-Y)=\sigma_X^2+\sigma_Y^2-2\sigma_{XY}$。它為正時，風險是嚴格凸的二次函數，最小值唯一；分母為零時兩個報酬的差是常數，不能直接除以零。公式原本允許任意實數權重。若另要求不放空、$0\le\alpha\le1$，則把無限制的最小點投影到 $[0,1]$；這是額外限制，不是 bootstrap 自動加上的條件。</p>
<p>三筆觀測的重抽例子也要區分「位置」與「不同資料」：索引 $(3,1,3)$ 仍有三筆，但第三列出現兩次，第二列完全沒出現。對樣本平均數可列出全部 $3^3=27$ 個等機率索引組合；對 Portfolio 權重，若重抽後全是同一列，樣本共變異數可能退化，估計量便未必有定義。這提醒我們：bootstrap 的有效性還取決於統計量與資料，不能只問程式是否能抽出索引。</p>
<p><strong>B 是電腦重抽的次數，不是資料筆數。</strong>增加 B 可降低重抽分位數與標準誤計算的 Monte Carlo 波動，卻不會增加原始資料的資訊，也不會修復不適合的抽樣單位。Lab 的 B=1000 是示範；實務上可比較不同種子與較大的 B，確認尾端分位數是否穩定。</p>
"""

CI = r"""
<h4>標準誤與信賴區間，描述的是兩件相連但不同的事</h4>
<p>bootstrap 標準誤是重抽估計值的標準差，描述估計量的散布；信賴區間則要決定如何用這個散布涵蓋未知參數。講義的 90% 百分位區間 $(0.43,0.72)$ 是其模擬資料的結果，不能直接搬成 Portfolio 這份資料的區間。對手上的資料，要由自己的重抽估計值重算分位數。</p>
<p>令 $q_a^*$ 為 bootstrap 估計值的第 $a$ 分位數，$\hat\theta$ 為原始估計值。兩個常見選擇是</p>
$$\text{percentile}:\ [q_{\alpha/2}^*,q_{1-\alpha/2}^*],\qquad
\text{basic}:\ [2\hat\theta-q_{1-\alpha/2}^*,2\hat\theta-q_{\alpha/2}^*].$$
<p>basic 區間的方向可從估計誤差推回來：若 $\hat\theta^*-\hat\theta$ 模仿 $\hat\theta-\theta$，取這個誤差的中央區間後，解出 $\theta$，就要把兩端減回去並交換順序。percentile 則直接取估計值分布的分位數。兩者都只是依 bootstrap 近似建構，並非任何樣本、任何統計量都精確涵蓋。</p>
<p>例如 $\hat\theta=10$，重抽的 2.5% 與 97.5% 分位數為 8、13。percentile 是 $[8,13]$；basic 是 $[7,12]$。若重抽分布向右偏，兩個區間不必同中心；所以不能把「畫出分位數」與「已處理估計偏差」視為同一件事。</p>
<p>BCa（bias-corrected and accelerated）進一步調整所取的百分位位置，使用偏差校正與 jackknife 資訊來反映不對稱；studentized bootstrap 則重抽近似的標準化誤差，需要每次估計標準誤。它們增加計算與條件，也不是萬用保證。SciPy 的 <code>bootstrap</code> 提供 percentile、basic、BCa；講義這裡使用的是最容易解讀的 percentile。</p>
<h4>沿用 Portfolio，自己算出兩種區間</h4>
<p>下面延伸 Lab 的配對重抽，增加區間計算。使用 <code>default_rng</code> 的固定種子，與原 Lab 的亂數呼叫方式不同，因此不要求數值逐位等於原 Lab 已存輸出。真正要對照的是：同列索引、共變異數估法，以及重抽估計值的標準差與分位數。</p>
""" + hl(PORTFOLIO_CODE, block_id='w05-alignment-portfolio-code') + refs(
    ('SciPy：bootstrap 的區間方法與配對抽樣', 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html'),
    ('Ch05 中文 Lab：Portfolio', 'https://github.com/phonchi/nsysu-math524/blob/main/static_files/presentations/Ch05-resample-lab-zh.ipynb'))

BLOCK = r"""
<h4>為什麼不能把時間序列的每筆觀測獨立重抽？</h4>
<p>假設每天的溫度有正向自我相關，今天偏高，明天也往往偏高。逐筆重抽會把連續的高溫段打散，重抽序列便不再有同樣的相依性。對平均數，差別可以直接從變異數展開看見：</p>
$$\operatorname{Var}(\bar X)=\frac1{n^2}\left[\sum_i\operatorname{Var}(X_i)+2\sum_{i<j}\operatorname{Cov}(X_i,X_j)\right].$$
<p>正共變異數增加平均數的變異；當相依結構被打散，逐筆 bootstrap 可能漏掉這部分。方向仍取決於相依型態與統計量，不能斷言所有相依資料的標準誤都必定偏小。</p>
<p><strong>移動區塊 bootstrap</strong>先取長度 l 的所有連續區塊，起點可為 1 到 $n-l+1$；再有放回抽區塊、按抽到的順序串接，直到至少 n 筆，最後裁成 n 筆。區塊內原本的先後與相關被保留，區塊接縫則不保留原序列的全部相依性。非重疊區塊、循環區塊與隨機區塊長度是不同版本，使用時要說清楚。</p>
<p>例如序列 1 到 8、區塊長度 3，移動區塊有 $(1,2,3),(2,3,4),\ldots,(6,7,8)$。抽到起點 4、1、5，串成 $(4,5,6,1,2,3,5,6,7)$，裁前 8 筆後才重算估計量。重複的是整個步驟，不是只拿一次亂序結果當作所有樣本。</p>
<p>區塊太短可能保留不了主要相依；太長又讓可重新組合的單位太少，估計不穩。平穩性、長期趨勢與季節性也會影響做法：若資料生成方式隨時間改變，單純抽區塊並不能自動處理。先決定要保留何種相依，再選區塊版本與長度，並比較合理範圍內結果的敏感程度。</p>
<p>群組資料也有相同的抽樣單位問題。例如病人內重複觀測相關、病人之間可視為獨立，就可考慮抽整位病人而非逐次就診；是否還要在病人內重抽，取決於研究的抽樣設計。bootstrap 的重抽單位與前面 GroupKFold 的群組界線都來自資料結構，但兩者的目的不同：一個估不確定性，一個評估未見群組的預測。</p>
""" + refs(
    ('講義的區塊 bootstrap 討論', 'https://stats.stackexchange.com/questions/25706/how-do-you-do-bootstrapping-with-time-series-data'),
    ('講義的區塊抽樣應用文獻', 'https://www.sciencedirect.com/science/article/pii/S0003267000008503'))

PREDICTION = r"""
<h4>平均曲線的不確定性，不等於新觀測的不確定性</h4>
<p>講義先將觀測 $(x_i,y_i)$ 配對重抽、每次重新擬合，再在同一組 x-grid 評估曲線。每個 grid 點的重抽分位數描述平均曲線的估計不確定性，屬於逐點區間。它不涵蓋新觀測本身的誤差，也不是整條曲線同時涵蓋的區間。</p>
<p>用車子資料想：我們問「100 horsepower 的車平均 mpg 大約多少」，與「下一台 100 horsepower 的車會有多少 mpg」，後者還有個別車輛的變動。即使平均曲線估得很準，新車的 mpg 仍會分散。Bootstrap 只重抽係數或擬合線，再取曲線的分位數，便漏掉這個新誤差。</p>
<p>固定設計的線性模型 $y=X\beta+\varepsilon$ 下，令原始係數為 $\hat\beta$。先以適當處理的殘差近似誤差分布，產生 $y^*=X\hat\beta+\varepsilon^*$，並重新估 $\hat\beta^*$；再獨立抽一個新誤差 $\varepsilon_{new}^*$。若用這個 bootstrap 世界模仿「新觀測減去估計預測」，則</p>
$$\Delta^*=x_0^\mathsf{T}(\hat\beta-\hat\beta^*)+\varepsilon_{new}^*.$$
<p>所以近似預測區間是原始預測 $x_0^\mathsf{T}\hat\beta$ 加上 $\Delta^*$ 的兩個尾端分位數。這裡係數差的方向不能隨意交換：在 bootstrap 世界，$\hat\beta$ 扮演真係數，$\hat\beta^*$ 扮演重新估出的係數。</p>
<h4>沿用 Auto，對照 CI 與 PI</h4>
<p>下面只延伸 Lab 已使用的 horsepower 線性模型。殘差除以 $\sqrt{1-h_i}$ 近似修正擬合造成的縮小，再中心化；這不是任何資料都有效的處理，而是以獨立、同變異且模型合理為前提的近似。若有異質變異、時間相依或模型型態錯誤，應換符合資料結構的方法，不能照貼這段。</p>
""" + hl(PREDICTION_CODE, block_id='w05-alignment-prediction-code') + r"""
<p>請比較兩個區間的寬度。它們的中心與端點不必恰好對稱；但新觀測區間包含新誤差，在這個同變異線性例子中通常明顯較寬。變更 <code>x0</code> 也可以觀察遠離常見 horsepower 時，係數估計不確定性如何增加。這段不使用未來車子的標籤估任何參數。</p>
<p>講義連到的 MAPIE 是預測區間與保形預測工具。Split conformal 的想法是另留校準資料，以未參與訓練的殘差決定區間寬度；在交換性等條件下提供邊際涵蓋控制，不等於每個 horsepower 都有相同的條件涵蓋率。它與殘差 bootstrap 的建構及假設不同，不能只因都輸出區間就把保證混在一起。套件各版本的 API 不同，實作應依使用版本的官方文件。</p>
""" + refs(
    ('statsmodels：重抽 LOWESS 曲線的逐點區間', 'https://www.statsmodels.org/stable/examples/notebooks/generated/lowess.html'),
    ('講義的 bootstrap 預測區間討論', 'https://stats.stackexchange.com/questions/226565/bootstrap-prediction-interval'),
    ('MAPIE 官方文件：預測區間與保形方法', 'https://mapie.readthedocs.io/en/latest/index.html'))

JACKKNIFE = r"""
<h4>刪掉一筆，量出估計量對每筆資料的敏感度</h4>
<p>Jackknife 不用隨機重抽，而是第 i 次刪掉第 i 筆資料，得到 $\hat\theta_{(-i)}$，總共 n 次。令刪一估計的平均為 $\bar\theta_{(-)}$，其標準誤估計為</p>
$$\widehat{SE}_{jack}=\sqrt{\frac{n-1}{n}\sum_{i=1}^n(\hat\theta_{(-i)}-\bar\theta_{(-)})^2}.$$
<p>前面的 $(n-1)/n$ 是關鍵。各次只刪一筆，刪一估計值的變動通常比 n 筆樣本重新抽出的變動小，不能直接把 n 個刪一估計的普通標準差當標準誤。</p>
<p>樣本平均數能精確驗算：$\bar x_{(-i)}=(n\bar x-x_i)/(n-1)$，刪一估計的平均仍是 $\bar x$。代入上式得到 $\widehat{SE}_{jack}=s/\sqrt n$，與獨立觀測的樣本平均數標準誤一致。例如資料 $(2,4,9)$，平均 5，$s^2=13$，標準誤是 $\sqrt{13/3}\approx2.082$。</p>
<p>同一組資料的非參數 bootstrap，條件於這份資料的平均數變異為 $13\times2/9=26/9$，標準差約 1.700：有限樣本的經驗分布變異與不偏樣本變異差一個因子，兩種重抽結果不必恰好相同。這不是哪個程式算錯，而是小樣本近似與估計方法的差別。</p>
<p>Jackknife 常適用於對單筆資料影響平滑的統計量，也用於偏差修正和 BCa 的加速項；中位數、樣本最大值等非平滑或端點問題不能一概套用。與 bootstrap 相比，它只有 n 個決定性的刪一樣本，常較省計算，但不會給出同樣豐富的重抽分布。下方原有推導進一步說明偏差修正的成立條件。</p>
""" + table(['方法','每次怎麼產生樣本','主要用途與限制'],[
    ['Bootstrap','從 n 筆有放回抽 n 筆，重複 B 次','近似估計量抽樣分布；必須選對重抽單位'],
    ['Jackknife','逐次刪一筆，得到 n 份大小 n−1 的樣本','估標準誤與平滑偏差；對非平滑統計量有限制'],
    ['Permutation','依虛無假設允許的交換方式重排標籤或觀測','近似虛無分布與 p-value；交換性與設計必須合理'],
]) + refs(
    ('講義的 Jackknife 說明', 'https://en.wikipedia.org/wiki/Jackknife_resampling'),
    ('講義的 Jackknife 與 bootstrap 比較', 'https://stats.stackexchange.com/questions/249333/comparison-of-the-jacknife-vs-the-bootstrap'))

PERMUTATION = r"""
<h4>重抽分布，與虛無分布，不是一回事</h4>
<p>Bootstrap 通常從經驗分布重抽，問估計量在重複抽樣時如何波動；置換檢定則依虛無假設，把允許交換的部分重排，問「如果沒有這個關係，會得到多極端的統計量」。兩者都重複計算，但起點與要近似的分布不同。</p>
<p>例如兩組的平均數差，先固定每組筆數並計算觀測差 $T_{obs}$。若虛無假設使觀測在兩組間可交換，就把組別標籤重排、重新計算差 T。隨機做 B 次雙尾置換，可用</p>
$$\hat p=\frac{1+\sum_{b=1}^B I(|T_b|\ge |T_{obs}|)}{B+1}.$$
<p>雙尾時兩邊都要取絕對值；只寫 $T_b\ge |T_{obs}|$ 會漏掉負方向的極端結果。加一是隨機置換常用的 Monte Carlo 校正，使原始排列也被計入比較；完整枚舉所有允許排列時，則直接以其精確比例計算。B=199 的隨機置換最小 p-value 是 1/200，不可能宣稱得到了 0。</p>
<p>置換要求的是<strong>虛無假設下的交換性</strong>。同一病人的重複紀錄、配對實驗、時間序列不能任意逐筆洗牌；應尊重配對、區塊或隨機分派設計。兩組平均相同也不必表示整個分布相同，因此簡單重排標籤檢定的條件，比「只要平均相同」更強。</p>
<h4>分類器：標籤重排後，完整重新訓練</h4>
<p>講義的分類例子保留 X、重排 y。原始資料先得到交叉驗證分數；每次置換標籤後，重新擬合每一折的模型、重新得到 CV 分數，形成模型在這套虛無機制下的參考分布。不能只洗牌已算好的預測值，或固定原始資料訓練好的分類器，因為那沒有重做學習程序。</p>
<p>sklearn 的 score 一律愈大愈好，所以 <code>permutation_test_score</code> 比較置換分數是否<strong>大於或等於</strong>原始分數。若使用負 MSE，也依這個方向比較，不另把 MSE 的「小才好」直接貼到 score 上。前處理包進 Pipeline；若原始程序含調參或特徵選擇，置換時也要重新執行同樣的選擇程序。</p>
""" + hl(PERMUTATION_CODE, block_id='w05-alignment-permutation-code') + r"""
<p>這個例子沿用官方分類器示範的 Iris，用分層 CV 和線性 SVM；是講義附錄的延伸，而不是 Portfolio 重抽 Lab 的結果。低 p-value 表示觀測分數相對於這套置換程序很不尋常，支持特徵與標籤之間存在模型能利用的關係；不表示分數一定足夠高、模型一定適合部署，也不是虛無假設為真的機率。高 p-value 也可能是模型沒利用到關係或檢定力不足，不能證明完全沒有關係。</p>
""" + refs(
    ('講義：Permutation test', 'https://en.wikipedia.org/wiki/Permutation_test'),
    ('scikit-learn：分類分數的置換檢定示範', 'https://scikit-learn.org/stable/auto_examples/feature_selection/plot_permutation_test_for_classification.html#test-with-permutations-the-significance-of-a-classification-score'),
    ('permutation_test_score：分數、群組與 p-value', 'https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.permutation_test_score.html'))

OOB = r"""
<h4>為什麼「bootstrap 訓練、原始資料驗證」會重疊？</h4>
<p>每份重抽資料雖有 n 筆，但平均只有約 0.632n 筆不同觀測；原始資料若全部拿來驗證，其中很大一部分曾參與這次訓練。把訓練過的資料算進測試誤差，便會混入樂觀的訓練表現。重抽出不同排列，不等於有了獨立測試資料。</p>
<p>一次抽籤沒抽到第 i 筆的機率是 $1-1/n$，連抽 n 次都沒抽到的機率是 $(1-1/n)^n\to e^{-1}\approx0.368$。這些完全沒出現的觀測稱為 out-of-bag（OOB）。用這次訓練好的模型，對它自己的 OOB 資料預測，才能避開直接的觀測重疊。</p>
<p>例如原始索引 1 到 5，抽到 $(1,1,3,4,4)$，這次的 OOB 是 2、5。下一次抽到 $(2,3,3,5,5)$，OOB 是 1、4。各次可評估的資料與數目都不同；同一觀測會在多個重抽模型的 OOB 出現，模型也不是彼此獨立的。</p>
<p>OOB 解決的是訓練／評估重疊，並沒有讓 bootstrap 訓練集等同於 n 筆獨立的新觀測。不同訓練規模、重複列、調參使用 OOB 以及如何平均分數，都會影響估計的解讀。講義因此以 CV 作為本章預測誤差評估的主線；第八章 bagging／random forest 再使用 OOB 對集成程序做內部評估。</p>
<p>也要分清楚「逐模型的 OOB 損失」與「先把同筆觀測的多個 OOB 預測平均，再算集成損失」：後者評估的是集成模型，非線性指標下兩種平均更不會相同。OOB 的名稱不代表額外收集了一份外部測試集。</p>
""" + refs(('講義：為何 bootstrap 樣本約含三分之二的不同觀測', 'https://stats.stackexchange.com/questions/88980/why-on-average-does-each-bootstrap-sample-contain-roughly-two-thirds-of-observat'))


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
    ciheading.insert_before(BeautifulSoup(detail('w05-detail-bootstrap-ci-methods', '計算細節：percentile、basic 區間與 Portfolio 實作', CI), 'html.parser'))
    node = soup.find(id='w05-detail-two-thirds')
    node.insert_after(BeautifulSoup(detail('w05-detail-bootstrap-oob', '延伸閱讀：重抽重疊、OOB 與預測誤差', OOB), 'html.parser'))
    node = soup.find(id='w05-detail-bootstrap-prediction')
    if node is not None:
        node.summary.string = '延伸閱讀：預測誤差、預測區間與相依資料的分工'
        content = node.find(class_='detail-body', recursive=False)
        content.clear()
        content.append(BeautifulSoup(r"""
<h4>先分清楚要估的對象，再決定怎麼重抽</h4>
<p><strong>標準誤與信賴區間</strong>問的是「由這份訓練資料估出的量有多不穩」；<strong>預測區間</strong>問的是「一筆新觀測可能落在哪裡」；<strong>預測誤差</strong>則問學習程序對新資料的損失。它們可用相同資料作起點，但需要不同的重抽與評估步驟。</p>
<p>沿用 Auto：重抽訓練資料後，每次算 horsepower 的係數，可以估係數標準誤；每次對 100 horsepower 算平均曲線值，可以估平均曲線的不確定性；再加入獨立新誤差，才得到新車 mpg 的預測區間。若想估整個程序的 MSE，則要對未參與該次訓練與選模的觀測算平方誤差，例如 CV 或适當的 OOB 評估，而不是把上述係數的標準差叫作預測誤差。</p>
<p>有些方法利用 bootstrap 同時模擬新資料與估計程序，建立預測區間或校正樂觀誤差；這並不推翻講義的提醒。問題在於是否正確分離訓練與評估、是否保留真實資料的結構，以及所模仿的生成模型是否合理。只要把原始資料全當驗證集，仍會遇到與重抽訓練資料重疊的問題。</p>
<p>同樣地，將逐筆重抽換成區塊重抽，是為了保留時間相依的部分結構；它本身沒有決定要估的是係數、區間還是預測損失。應先說清楚統計量和目標，再設計重抽單位、區塊長度及新觀測的生成方式。</p>
<p>完整殘差 bootstrap 的假設、誤差方向與程式，見<a href="#w05-detail-bootstrap-intervals">預測區間收合區</a>；訓練／評估重疊與 OOB 的解讀，見<a href="#w05-detail-bootstrap-oob">OOB 收合區</a>。</p>
""".replace('适當', '適當'), 'html.parser'))
    result['bootstrap'] = str(soup)
    return result
