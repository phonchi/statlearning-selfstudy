#!/usr/bin/env python3
"""產生 linear_regression.html 需要的烘焙資料（FRAMES_w03*）。

只有「要對到課本／講義的數字」或「需要一整條曲線」的圖才在這裡產生；
凡是 lab notebook 裡已經有輸出的數字，頁面上一律逐字抄 lab（見 lib.lab_output），
不在這裡重算。

Advertising 為什麼寫在這支裡：ISLP 的 Python 套件沒有附 Advertising（只有 Boston、
Carseats、Credit、Auto…），而 ISLP 第 3 章的表 3.1／3.3／3.4／3.6／3.9 全部建立在
它上面。為了讓產生器不依賴網路又能重生，200 列原始資料直接以字面值嵌在下面
（來源 https://www.statlearning.com/s/Advertising.csv）。stderr 會印出與課本各表的
逐位對照，任何一位對不上都看得見。

跑法（用 pinned 環境，數字才可重現）：
  conda run -n m524 python tools/frames/gen_regression.py > /tmp/w03.js

輸出是可以直接貼進頁面的 JS literal。
"""
import json
import sys
from io import StringIO

import numpy as np
import pandas as pd
import statsmodels.api as sm
from ISLP import load_data
from sklearn.neighbors import KNeighborsRegressor
from statsmodels.stats.outliers_influence import variance_inflation_factor as VIF

VERSIONS = "numpy {} · pandas {} · statsmodels {} · scikit-learn {}".format(
    np.__version__, pd.__version__, sm.__version__, __import__("sklearn").__version__)
GEN = "tools/frames/gen_regression.py"

# ── Advertising（200 列 × 4 欄，每行放 4 筆以求緊湊）────────────────────────
ADV_RAW = """
230.1,37.8,69.2,22.1 44.5,39.3,45.1,10.4 17.2,45.9,69.3,9.3 151.5,41.3,58.5,18.5
180.8,10.8,58.4,12.9 8.7,48.9,75,7.2 57.5,32.8,23.5,11.8 120.2,19.6,11.6,13.2
8.6,2.1,1,4.8 199.8,2.6,21.2,10.6 66.1,5.8,24.2,8.6 214.7,24,4,17.4
23.8,35.1,65.9,9.2 97.5,7.6,7.2,9.7 204.1,32.9,46,19 195.4,47.7,52.9,22.4
67.8,36.6,114,12.5 281.4,39.6,55.8,24.4 69.2,20.5,18.3,11.3 147.3,23.9,19.1,14.6
218.4,27.7,53.4,18 237.4,5.1,23.5,12.5 13.2,15.9,49.6,5.6 228.3,16.9,26.2,15.5
62.3,12.6,18.3,9.7 262.9,3.5,19.5,12 142.9,29.3,12.6,15 240.1,16.7,22.9,15.9
248.8,27.1,22.9,18.9 70.6,16,40.8,10.5 292.9,28.3,43.2,21.4 112.9,17.4,38.6,11.9
97.2,1.5,30,9.6 265.6,20,0.3,17.4 95.7,1.4,7.4,9.5 290.7,4.1,8.5,12.8
266.9,43.8,5,25.4 74.7,49.4,45.7,14.7 43.1,26.7,35.1,10.1 228,37.7,32,21.5
202.5,22.3,31.6,16.6 177,33.4,38.7,17.1 293.6,27.7,1.8,20.7 206.9,8.4,26.4,12.9
25.1,25.7,43.3,8.5 175.1,22.5,31.5,14.9 89.7,9.9,35.7,10.6 239.9,41.5,18.5,23.2
227.2,15.8,49.9,14.8 66.9,11.7,36.8,9.7 199.8,3.1,34.6,11.4 100.4,9.6,3.6,10.7
216.4,41.7,39.6,22.6 182.6,46.2,58.7,21.2 262.7,28.8,15.9,20.2 198.9,49.4,60,23.7
7.3,28.1,41.4,5.5 136.2,19.2,16.6,13.2 210.8,49.6,37.7,23.8 210.7,29.5,9.3,18.4
53.5,2,21.4,8.1 261.3,42.7,54.7,24.2 239.3,15.5,27.3,15.7 102.7,29.6,8.4,14
131.1,42.8,28.9,18 69,9.3,0.9,9.3 31.5,24.6,2.2,9.5 139.3,14.5,10.2,13.4
237.4,27.5,11,18.9 216.8,43.9,27.2,22.3 199.1,30.6,38.7,18.3 109.8,14.3,31.7,12.4
26.8,33,19.3,8.8 129.4,5.7,31.3,11 213.4,24.6,13.1,17 16.9,43.7,89.4,8.7
27.5,1.6,20.7,6.9 120.5,28.5,14.2,14.2 5.4,29.9,9.4,5.3 116,7.7,23.1,11
76.4,26.7,22.3,11.8 239.8,4.1,36.9,12.3 75.3,20.3,32.5,11.3 68.4,44.5,35.6,13.6
213.5,43,33.8,21.7 193.2,18.4,65.7,15.2 76.3,27.5,16,12 110.7,40.6,63.2,16
88.3,25.5,73.4,12.9 109.8,47.8,51.4,16.7 134.3,4.9,9.3,11.2 28.6,1.5,33,7.3
217.7,33.5,59,19.4 250.9,36.5,72.3,22.2 107.4,14,10.9,11.5 163.3,31.6,52.9,16.9
197.6,3.5,5.9,11.7 184.9,21,22,15.5 289.7,42.3,51.2,25.4 135.2,41.7,45.9,17.2
222.4,4.3,49.8,11.7 296.4,36.3,100.9,23.8 280.2,10.1,21.4,14.8 187.9,17.2,17.9,14.7
238.2,34.3,5.3,20.7 137.9,46.4,59,19.2 25,11,29.7,7.2 90.4,0.3,23.2,8.7
13.1,0.4,25.6,5.3 255.4,26.9,5.5,19.8 225.8,8.2,56.5,13.4 241.7,38,23.2,21.8
175.7,15.4,2.4,14.1 209.6,20.6,10.7,15.9 78.2,46.8,34.5,14.6 75.1,35,52.7,12.6
139.2,14.3,25.6,12.2 76.4,0.8,14.8,9.4 125.7,36.9,79.2,15.9 19.4,16,22.3,6.6
141.3,26.8,46.2,15.5 18.8,21.7,50.4,7 224,2.4,15.6,11.6 123.1,34.6,12.4,15.2
229.5,32.3,74.2,19.7 87.2,11.8,25.9,10.6 7.8,38.9,50.6,6.6 80.2,0,9.2,8.8
220.3,49,3.2,24.7 59.6,12,43.1,9.7 0.7,39.6,8.7,1.6 265.2,2.9,43,12.7
8.4,27.2,2.1,5.7 219.8,33.5,45.1,19.6 36.9,38.6,65.6,10.8 48.3,47,8.5,11.6
25.6,39,9.3,9.5 273.7,28.9,59.7,20.8 43,25.9,20.5,9.6 184.9,43.9,1.7,20.7
73.4,17,12.9,10.9 193.7,35.4,75.6,19.2 220.5,33.2,37.9,20.1 104.6,5.7,34.4,10.4
96.2,14.8,38.9,11.4 140.3,1.9,9,10.3 240.1,7.3,8.7,13.2 243.2,49,44.3,25.4
38,40.3,11.9,10.9 44.7,25.8,20.6,10.1 280.7,13.9,37,16.1 121,8.4,48.7,11.6
197.6,23.3,14.2,16.6 171.3,39.7,37.7,19 187.8,21.1,9.5,15.6 4.1,11.6,5.7,3.2
93.9,43.5,50.5,15.3 149.8,1.3,24.3,10.1 11.7,36.9,45.2,7.3 131.7,18.4,34.6,12.9
172.5,18.1,30.7,14.4 85.7,35.8,49.3,13.3 188.4,18.1,25.6,14.9 163.5,36.8,7.4,18
117.2,14.7,5.4,11.9 234.5,3.4,84.8,11.9 17.9,37.6,21.6,8 206.8,5.2,19.4,12.2
215.4,23.6,57.6,17.1 284.3,10.6,6.4,15 50,11.6,18.4,8.4 164.5,20.9,47.4,14.5
19.6,20.1,17,7.6 168.4,7.1,12.8,11.7 222.4,3.4,13.1,11.5 276.9,48.9,41.8,27
248.4,30.2,20.3,20.2 170.2,7.8,35.2,11.7 276.7,2.3,23.7,11.8 165.6,10,17.6,12.6
156.6,2.6,8.3,10.5 218.5,5.4,27.4,12.2 56.2,5.7,29.7,8.7 287.6,43,71.8,26.2
253.8,21.3,30,17.6 205,45.1,19.6,22.6 139.5,2.1,26.6,10.3 191.1,28.7,18.2,17.3
286,13.9,3.7,15.9 18.7,12.1,23.4,6.7 39.5,41.1,5.8,10.8 75.5,10.8,6,9.9
17.2,4.1,31.6,5.9 166.8,42,3.6,19.6 149.7,35.6,6,17.3 38.2,3.7,13.8,7.6
94.2,4.9,8.1,9.7 177,9.3,6.4,12.8 283.6,42,66.2,25.5 232.1,8.6,8.7,13.4
"""
Adv = pd.read_csv(StringIO("TV,radio,newspaper,sales\n"
                           + "\n".join(ADV_RAW.split())), dtype=float)
assert Adv.shape == (200, 4), Adv.shape
ADV_VARS = ["TV", "radio", "newspaper"]
YA = Adv["sales"]


def r(v, d=4):
    return None if v is None or (isinstance(v, float) and not np.isfinite(v)) else round(float(v), d)


def arr(a, d=3):
    return [round(float(v), d) for v in np.asarray(a, dtype=float)]


def fit_block(df, cols, ycol):
    """回傳一個子集的完整迴歸摘要（給 w03tf 用）。"""
    y = df[ycol]
    if cols:
        X = sm.add_constant(df[list(cols)], has_constant="add")
    else:
        X = pd.DataFrame({"const": np.ones(len(df))}, index=df.index)
    m = sm.OLS(y, X).fit()
    tss = float(((y - y.mean()) ** 2).sum())
    rss = float(m.ssr)
    p = len(cols)
    return {
        "vars": list(cols),
        "names": list(X.columns),
        "coef": [r(v, 4) for v in m.params],
        "se": [r(v, 4) for v in m.bse],
        "t": [r(v, 2) for v in m.tvalues],
        "p": [r(v, 5) for v in m.pvalues],
        "F": r(m.fvalue, 2) if p else None,
        "Fp": r(m.f_pvalue, 6) if p else None,
        "r2": r(m.rsquared, 4),
        "rse": r(np.sqrt(m.scale), 4),
        "rss": r(rss, 2), "tss": r(tss, 2), "df": int(m.df_resid),
    }


# ── 1. w03tf：Advertising 的 8 個子集（ISLP 表 3.1／3.3／3.4／3.6）──────────
subsets = []
for mask in range(8):
    cols = [v for i, v in enumerate(ADV_VARS) if mask & (1 << (2 - i))]
    b = fit_block(Adv, cols, "sales")
    b["key"] = "".join("1" if v in cols else "0" for v in ADV_VARS)
    subsets.append(b)

adv_corr = Adv.corr().round(4).values.tolist()
Xfull = sm.add_constant(Adv[ADV_VARS])
adv_vif = [r(VIF(Xfull.values, i), 3) for i in range(1, 4)]
mfull = sm.OLS(YA, Xfull).fit()
adv_ci = [[r(a, 3), r(b, 3)] for a, b in np.asarray(mfull.conf_int())]

# 交互作用（ISLP 表 3.9）
Xint = sm.add_constant(pd.DataFrame({
    "TV": Adv.TV, "radio": Adv.radio, "TVxradio": Adv.TV * Adv.radio}))
mint = sm.OLS(YA, Xint).fit()
adv_inter = {"names": ["intercept", "TV", "radio", "TV×radio"],
             "coef": [r(v, 4) for v in mint.params], "se": [r(v, 4) for v in mint.bse],
             "t": [r(v, 2) for v in mint.tvalues], "p": [r(v, 6) for v in mint.pvalues],
             "r2": r(mint.rsquared, 4), "rse": r(np.sqrt(mint.scale), 4)}

# ── 2. w03rss：Advertising sales~TV 的 RSS 等高線（ISLP 圖 3.2）──────────────
mtv = sm.OLS(YA, sm.add_constant(Adv[["TV"]])).fit()
sxx = float(((Adv.TV - Adv.TV.mean()) ** 2).sum())
rss_ref = {"b0": r(mtv.params.iloc[0], 4), "b1": r(mtv.params.iloc[1], 6),
           "rssMin": r(mtv.ssr, 2), "n": 200,
           "sumX": r(Adv.TV.sum(), 2), "sumX2": r((Adv.TV ** 2).sum(), 2), "sxx": r(sxx, 2)}

# ── 3. w03diag：五組診斷資料（residual / QQ / scale-location / leverage）────
def diag_block(x, y, label, note, xname, yname):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = sm.OLS(y, sm.add_constant(x)).fit()
    infl = m.get_influence()
    return {"label": label, "note": note, "xname": xname, "yname": yname,
            "n": int(len(y)), "b0": r(m.params[0], 4), "b1": r(m.params[1], 5),
            "rse": r(np.sqrt(m.scale), 4), "r2": r(m.rsquared, 4),
            "x": arr(x, 3), "fit": arr(m.fittedvalues, 3), "res": arr(m.resid, 3),
            "lev": arr(infl.hat_matrix_diag, 5)}


rng = np.random.default_rng(3)
NS = 100
xs = np.sort(rng.uniform(0, 10, NS))
eps = rng.standard_normal(NS)

good = diag_block(xs, 2 + 3 * xs + 2.0 * eps, "① 乾淨的線性資料",
                  "四張圖都沒有結構：這就是「沒問題」長什麼樣。",
                  "x", "y")

Auto = load_data("Auto")
nonlin = diag_block(np.asarray(Auto["horsepower"], dtype=float),
                    np.asarray(Auto["mpg"], dtype=float),
                    "② 非線性（Auto：mpg~horsepower）",
                    "殘差對配適值呈明顯的 U 形，正是 ISLP 圖 3.9 左的病徵。",
                    "horsepower", "mpg")

hetero = diag_block(xs, 2 + 3 * xs + (0.35 + 0.55 * xs) * eps, "③ 異質變異（漏斗形）",
                    "殘差的散佈隨配適值變大而張開，scale-location 的紅趨勢往上爬。",
                    "x", "y")

y_out = 2 + 3 * xs + 2.0 * eps
y_out[68] += 26.0
outlier = diag_block(xs, y_out, "④ 離群值（unusual y）",
                     "第 69 筆的 y 被拉高 26：studentized 殘差衝出 ±3，但槓桿值不高。",
                     "x", "y")

x_lev = xs.copy()
x_lev[NS - 1] = 26.0
y_lev = 2 + 3 * xs + 2.0 * eps
y_lev[NS - 1] = 2 + 3 * 26.0 - 30.0
lever = diag_block(x_lev, y_lev, "⑤ 高槓桿點（unusual x）",
                   "最後一筆的 x 遠離其他點，一個點就把整條線扳過去。",
                   "x", "y")

# ── 4. w03vif：Credit 的共線性（ISLP 表 3.11 與 §3.3.3 的 VIF）──────────────
Credit = load_data("Credit")
CB = Credit["Balance"]


def credit_block(cols):
    X = sm.add_constant(Credit[cols])
    m = sm.OLS(CB, X).fit()
    return {"vars": cols, "names": list(X.columns),
            "coef": [r(v, 4) for v in m.params], "se": [r(v, 4) for v in m.bse],
            "t": [r(v, 3) for v in m.tvalues], "p": [r(v, 5) for v in m.pvalues],
            "r2": r(m.rsquared, 4)}


cred_m1 = credit_block(["Age", "Limit"])
cred_m2 = credit_block(["Rating", "Limit"])
X3 = sm.add_constant(Credit[["Age", "Rating", "Limit"]])
cred_vif3 = [r(VIF(X3.values, i), 2) for i in range(1, 4)]
cred_r2_3 = r(sm.OLS(CB, X3).fit().rsquared, 4)
cred_corr = {"limitRating": r(Credit["Limit"].corr(Credit["Rating"]), 4),
             "limitAge": r(Credit["Limit"].corr(Credit["Age"]), 4)}
se_ratio = r(cred_m2["se"][2] / cred_m1["se"][2], 2)

# ── 5. w03inter：Credit 的 income × student（ISLP 圖 3.7）────────────────────
stu = (Credit["Student"].astype(str) == "Yes").astype(float)
Xa = sm.add_constant(pd.DataFrame({"income": Credit["Income"], "student": stu}))
ma = sm.OLS(CB, Xa).fit()
Xb = sm.add_constant(pd.DataFrame({"income": Credit["Income"], "student": stu,
                                   "income_student": Credit["Income"] * stu}))
mb = sm.OLS(CB, Xb).fit()
cred_inter = {
    "n": int(len(CB)), "incomeRange": [r(Credit["Income"].min(), 2), r(Credit["Income"].max(), 2)],
    "balRange": [int(CB.min()), int(CB.max())],
    "income": arr(Credit["Income"], 1), "bal": [int(v) for v in CB],
    "stu": [int(v) for v in stu], "tss": r(((CB - CB.mean()) ** 2).sum(), 1),
    "add": {"names": ["intercept", "income", "student"],
            "coef": [r(v, 4) for v in ma.params], "se": [r(v, 4) for v in ma.bse],
            "t": [r(v, 2) for v in ma.tvalues], "r2": r(ma.rsquared, 4)},
    "inter": {"names": ["intercept", "income", "student", "income×student"],
              "coef": [r(v, 4) for v in mb.params], "se": [r(v, 4) for v in mb.bse],
              "t": [r(v, 2) for v in mb.tvalues], "p": [r(v, 5) for v in mb.pvalues],
              "r2": r(mb.rsquared, 4)},
}

# 三個水準的質性變數（ISLP 表 3.8 用 region，ISLP 的 Python Credit 沒有這一欄，
# 改用同資料集的 Ethnicity，三個水準、baseline 是第一個水準）
eth = pd.get_dummies(Credit["Ethnicity"], drop_first=True, dtype=float)
Xe = sm.add_constant(eth)
me = sm.OLS(CB, Xe).fit()
cred_eth = {"levels": [str(v) for v in Credit["Ethnicity"].cat.categories],
            "names": ["intercept"] + [f"Ethnicity[{c}]" for c in eth.columns],
            "coef": [r(v, 3) for v in me.params], "se": [r(v, 3) for v in me.bse],
            "t": [r(v, 3) for v in me.tvalues], "p": [r(v, 4) for v in me.pvalues],
            "F": r(me.fvalue, 4), "Fp": r(me.f_pvalue, 4), "r2": r(me.rsquared, 5),
            "means": {str(k): r(v, 2) for k, v in CB.groupby(Credit["Ethnicity"],
                                                            observed=True).mean().items()}}
Xs2 = sm.add_constant(pd.DataFrame({"student": stu}))
ms2 = sm.OLS(CB, Xs2).fit()
cred_student = {"names": ["intercept", "Student[Yes]"],
                "coef": [r(v, 3) for v in ms2.params], "se": [r(v, 3) for v in ms2.bse],
                "t": [r(v, 3) for v in ms2.tvalues], "p": [r(v, 6) for v in ms2.pvalues],
                "means": {"No": r(CB[stu == 0].mean(), 2), "Yes": r(CB[stu == 1].mean(), 2)}}

# ── 6. w03knn：線性迴歸 vs KNN（ISLP 圖 3.19–3.20 的設定重做）───────────────
KS = [1, 2, 3, 4, 5, 7, 9, 12, 16, 20, 25]


SIG = 0.1


def knn_curve(fun, p_extra, n=50, reps=80, seed=11):
    """回傳 (KNN 各 K 的測試 MSE, 線性迴歸的測試 MSE)。測試集不加噪音，量的是對 f 的誤差。"""
    g = np.random.default_rng(seed)
    knn = np.zeros(len(KS))
    lin = 0.0
    for _ in range(reps):
        Xtr = g.uniform(-1, 1, (n, 1 + p_extra))
        Xte = g.uniform(-1, 1, (500, 1 + p_extra))
        ytr = fun(Xtr[:, 0]) + g.normal(0, SIG, n)
        yte = fun(Xte[:, 0])
        lin += float(np.mean((yte - sm.OLS(ytr, sm.add_constant(Xtr)).fit()
                              .predict(sm.add_constant(Xte))) ** 2))
        for j, k in enumerate(KS):
            m = KNeighborsRegressor(n_neighbors=min(k, n)).fit(Xtr, ytr)
            knn[j] += float(np.mean((yte - m.predict(Xte)) ** 2))
    return arr(knn / reps, 5), r(lin / reps, 5)


F_LIN = lambda x: 2.0 + 1.5 * x                                       # noqa: E731
F_MILD = lambda x: 2.0 + 1.5 * x + 0.35 * x ** 2                      # noqa: E731
F_STRONG = lambda x: 2.0 + 0.9 * np.sin(2.6 * x) + 0.55 * x ** 2      # noqa: E731

knn_shape = {}
for name, f in (("linear", F_LIN), ("mild", F_MILD), ("strong", F_STRONG)):
    kmse, lmse = knn_curve(f, 0)
    knn_shape[name] = {"knn": kmse, "lin": lmse,
                       "best": r(min(kmse), 5), "bestK": KS[int(np.argmin(kmse))]}

PS = [1, 2, 3, 4, 10, 20]
knn_dim = {}
for pex in PS:
    kmse, lmse = knn_curve(F_STRONG, pex - 1)
    knn_dim[str(pex)] = {"knn": kmse, "lin": lmse,
                         "best": r(min(kmse), 5), "bestK": KS[int(np.argmin(kmse))]}


# ── 輸出 ────────────────────────────────────────────────────────────────
def js(name, obj, src, seed, note=""):
    meta = {"src": src, "seed": seed, "versions": VERSIONS, "gen": GEN}
    if note:
        meta["note"] = note
    return (f"const {name} = " + json.dumps({"meta": meta, **obj},
                                            ensure_ascii=False, separators=(",", ":")) + ";")


out = [
    js("FRAMES_w03tf",
       {"n": 200, "vars": ADV_VARS, "subsets": subsets, "corr": adv_corr,
        "vif": adv_vif, "ci": adv_ci, "inter": adv_inter,
        "ybar": r(YA.mean(), 4), "ysd": r(YA.std(ddof=1), 4)},
       "Advertising（statlearning.com）· statsmodels OLS 自算",
       "無隨機（純最小平方，資料固定）",
       "對照 ISLP 表 3.1／3.3（單變數）、表 3.4／3.6（三變數）、表 3.9（交互作用）"),
    js("FRAMES_w03rss", rss_ref,
       "Advertising sales~TV（ISLP 圖 3.2 的等高線就是這一組）",
       "無隨機",
       "RSS 是 (b0,b1) 的二次式，等高線是精確的橢圓，頁面上直接用解析式畫"),
    js("FRAMES_w03diag",
       {"panels": {"good": good, "nonlin": nonlin, "hetero": hetero,
                   "outlier": outlier, "lever": lever},
        "order": ["good", "nonlin", "hetero", "outlier", "lever"]},
       "② 為 ISLP Auto（mpg~horsepower，＝圖 3.9 左）；其餘四組為模擬",
       "np.random.default_rng(3)，n = 100",
       "頁面只用 fit／res／lev／rse 四樣，studentized 殘差與 QQ 分位數在瀏覽器裡算"),
    js("FRAMES_w03vif",
       {"m1": cred_m1, "m2": cred_m2, "vif3": cred_vif3, "r2three": cred_r2_3,
        "corr": cred_corr, "seRatio": se_ratio, "n": int(len(CB))},
       "ISLP Credit（ISLP 表 3.11 與 §3.3.3 的 VIF 1.01／160.67／160.59）",
       "無隨機"),
    js("FRAMES_w03inter",
       {"credit": cred_inter, "adv": adv_inter, "eth": cred_eth, "student": cred_student},
       "ISLP Credit（圖 3.7 的 income × student）與 Advertising（表 3.9）",
       "無隨機",
       "ISLP 的 Python Credit 沒有 own／region 兩欄，三水準的例子改用同資料集的 Ethnicity"),
    js("FRAMES_w03knn",
       {"ks": KS, "shape": knn_shape, "ps": PS, "dim": knn_dim, "sigma": SIG},
       "以 ISLP 圖 3.19／3.20 的設定重做的模擬（課本未公布產生資料的函數）",
       "np.random.default_rng(11)，n = 50，80 次重複，測試集 500 筆",
       "線性 f = 2 + 1.5x；輕微非線性 + 0.35x²；強非線性 f = 2 + 0.9sin(2.6x) + 0.55x²；"
       "p 增加時額外的變數都是純噪音，維度掃描用強非線性那一組"),
]
print("\n".join(out))

s0, s1, s2 = subsets[0b100], subsets[0b010], subsets[0b001]
full = subsets[0b111]
print("\n/* 對照課本：", file=sys.stderr)
print(f"   表 3.1  TV      coef={s0['coef']} se={s0['se']} t={s0['t']}"
      f"   （書上 7.0325／0.0475、0.4578／0.0027、15.36／17.67）", file=sys.stderr)
print(f"   表 3.2  RSE={s0['rse']} R2={s0['r2']} F={s0['F']}"
      f"   （書上 3.26／0.612／312.1）", file=sys.stderr)
print(f"   表 3.3  radio   coef={s1['coef']} t={s1['t']}   （書上 9.312／0.203、16.54／9.92）",
      file=sys.stderr)
print(f"   表 3.3  news    coef={s2['coef']} t={s2['t']}   （書上 12.351／0.055、19.88／3.30）",
      file=sys.stderr)
print(f"   表 3.4  full    coef={full['coef']} se={full['se']} t={full['t']}"
      f"   （書上 2.939／0.046／0.189／−0.001）", file=sys.stderr)
print(f"   表 3.6  RSE={full['rse']} R2={full['r2']} F={full['F']}"
      f"   （書上 1.686／0.897／570）", file=sys.stderr)
print(f"   表 3.9  inter   coef={adv_inter['coef']} t={adv_inter['t']} R2={adv_inter['r2']}"
      f"   （書上 6.7502／0.0191／0.0289／0.0011、R2 0.968）", file=sys.stderr)
print(f"   §3.4    VIF={adv_vif}  CI={adv_ci[1:]}"
      f"   （書上 1.005／1.145／1.145；TV (0.043,0.049)、radio (0.172,0.206)）", file=sys.stderr)
print(f"   表 3.11 m1 se(limit)={cred_m1['se'][2]} m2 se(limit)={cred_m2['se'][2]}"
      f" 倍數={se_ratio}   （書上 0.005／0.064，12 倍）", file=sys.stderr)
print(f"   §3.3.3  VIF(age,rating,limit)={cred_vif3}   （書上 1.01／160.67／160.59）",
      file=sys.stderr)
print(f"   §3.3.3  R2 三變數={cred_r2_3} → 去掉 rating={cred_m1['r2']}"
      f"   （書上 0.754 → 0.75）", file=sys.stderr)
print(f"   圖 3.9  Auto b0={nonlin['b0']} b1={nonlin['b1']} R2={nonlin['r2']}"
      f"   （ISLP 表 3.10：39.94／−0.158）", file=sys.stderr)
print("*/", file=sys.stderr)
