#!/usr/bin/env python3
"""產生 beyond_linearity.html 需要的烘焙資料（FRAMES_w08*）。

比照 tools/frames/gen_resampling.py：只有「lab notebook 沒有存下輸出」或
「需要一整條曲線／一整個信賴帶」的圖才在這裡產生；凡是 lab 裡已經有輸出的
數字，頁面上一律逐字抄 lab，不在這裡重算。

站內序號 08 但 ISLP 章號 7：id 前綴用 w08，資料檔用 ch7。

跑法（用 pinned 環境，數字才可重現）：
  conda run -n m524 python tools/frames/gen_nonlin.py > /tmp/w08.js

輸出是可以直接貼進頁面的 JS literal。
"""
import json
import sys
import warnings

import numpy as np
import statsmodels.api as sm
from ISLP import load_data
from ISLP.models import ModelSpec as MS
from ISLP.models import poly
from ISLP.pygam import approx_lam, degrees_of_freedom
from ISLP.transforms import BSpline, NaturalSpline
from pygam import LinearGAM
from pygam import f as f_gam
from pygam import s as s_gam
from sklearn.model_selection import KFold

warnings.filterwarnings("ignore")

VERSIONS = ("numpy {} · pandas {} · scikit-learn {} · statsmodels {} · pygam {}".format(
    np.__version__, __import__("pandas").__version__, __import__("sklearn").__version__,
    sm.__version__, __import__("pygam").__version__))
GEN = "tools/frames/gen_nonlin.py"
LAB = "Ch07-nonlin-lab-zh.ipynb"

Wage = load_data("Wage")
AGE = np.asarray(Wage["age"], dtype=float)
Y = np.asarray(Wage["wage"], dtype=float)
YEAR = np.asarray(Wage["year"], dtype=float)
N = len(Y)
A0, A1 = float(AGE.min()), float(AGE.max())          # 18, 80


def r(a, d=1):
    """四捨五入成 list（頁面大小預算：曲線一律 1 位小數就夠畫）。"""
    return [round(float(v), d) for v in np.asarray(a).ravel()]


def k(v):
    """字典鍵：用 %g 讓 5.0 變 "5"、6.8 還是 "6.8"。

    這是為了跟 JS 的 String(Number) 對得上——JSON 的 5.0 到瀏覽器就是 5，
    String(5) 是 "5" 不是 "5.0"，鍵用 str(5.0) 會查不到。
    """
    return "%g" % float(v)


# ══════════════════════════════════════════════════════════════════════
# 0. 共用的 Wage 子樣本：step / basis / knot / loess 四個 live 元件都用它
#    （ISLP 圖 7.3 也是「a subset of the Wage data」）
# ══════════════════════════════════════════════════════════════════════
rng_sub = np.random.default_rng(524)
POOL = np.flatnonzero(Y <= 250)          # 排除 79 筆 wage>250 的高收入者（ISLP §7.1 說那是另一群）
SUB = np.sort(rng_sub.choice(POOL, size=90, replace=False))
sub_age, sub_y = AGE[SUB], Y[SUB]


# ══════════════════════════════════════════════════════════════════════
# 1. 多項式次數 1..15：配適曲線 + 95% 信賴帶 + 訓練 MSE + 10-fold CV MSE
#    （ISLP 圖 7.1 是 degree 4；圖 7.7 用 degree 15 示範邊界暴衝）
# ══════════════════════════════════════════════════════════════════════
DEGS = list(range(1, 16))
PGRID = np.linspace(A0, A1, 40)


def tscale(a):
    """把 age 壓到 [-1,1] 再取冪次。與正交多項式張出同一個空間，
    但避免 80^15 這種天文數字把設計矩陣的條件數毀掉。"""
    return 2 * (np.asarray(a, dtype=float) - A0) / (A1 - A0) - 1


def pdesign(a, d):
    t = tscale(a)
    return np.column_stack([t ** k for k in range(1, d + 1)])


kf10 = KFold(n_splits=10, shuffle=True, random_state=0)   # 各 degree 共用同一組分割
poly_fit, poly_lo, poly_hi, poly_train, poly_cv = {}, {}, {}, [], []
for d in DEGS:
    X = sm.add_constant(pdesign(AGE, d))
    M = sm.OLS(Y, X).fit()
    pr = M.get_prediction(sm.add_constant(pdesign(PGRID, d)))
    band = pr.conf_int(alpha=0.05)
    poly_fit[str(d)] = r(pr.predicted_mean)
    poly_lo[str(d)] = r(band[:, 0])
    poly_hi[str(d)] = r(band[:, 1])
    poly_train.append(round(float(np.mean(M.resid ** 2)), 2))
    errs = []
    for tr, te in kf10.split(X):
        m = sm.OLS(Y[tr], X[tr]).fit()
        errs.append(float(np.mean((Y[te] - m.predict(X[te])) ** 2)))
    poly_cv.append(round(float(np.mean(errs)), 2))

# 對帳：degree 4 的配適值要跟 lab 儲存格 14 的正交多項式配適完全一樣
_chk = MS([poly("age", degree=4)]).fit(Wage)
_chk_fit = sm.OLS(Y, _chk.transform(Wage)).fit()
POLY_MAXDIFF = float(np.max(np.abs(
    _chk_fit.predict(_chk.transform(Wage)) - sm.OLS(Y, sm.add_constant(pdesign(AGE, 4)))
    .fit().predict(sm.add_constant(pdesign(AGE, 4))))))


# ══════════════════════════════════════════════════════════════════════
# 2. 立方樣條 vs 自然樣條：同樣三個內部節點，比兩端的信賴帶（ISLP 圖 7.4）
# ══════════════════════════════════════════════════════════════════════
KNOTS = [25.0, 40.0, 60.0]
SGRID = np.linspace(A0, A1, 80)


def spline_fit(trans):
    t = trans.fit(AGE)
    X = sm.add_constant(t.transform(AGE))
    M = sm.OLS(Y, X).fit()
    pr = M.get_prediction(sm.add_constant(t.transform(SGRID)))
    b = pr.conf_int(alpha=0.05)
    return {"fit": r(pr.predicted_mean), "lo": r(b[:, 0]), "hi": r(b[:, 1]),
            "df": int(X.shape[1])}, b


cubic, cub_b = spline_fit(BSpline(internal_knots=KNOTS, intercept=False))
natural, nat_b = spline_fit(NaturalSpline(internal_knots=KNOTS))
CUB_W = [round(float(cub_b[i, 1] - cub_b[i, 0]), 2) for i in (0, -1)]
NAT_W = [round(float(nat_b[i, 1] - nat_b[i, 0]), 2) for i in (0, -1)]


# ══════════════════════════════════════════════════════════════════════
# 3. 平滑樣條：以有效自由度 df_λ 為刻度（ISLP 圖 7.8）
#    df_λ 用 ISLP.pygam.degrees_of_freedom 定義（含未懲罰的截距，所以下限是 2）
# ══════════════════════════════════════════════════════════════════════
XA = AGE.reshape(-1, 1)
_g = LinearGAM(s_gam(0, lam=0.6)).fit(XA, Y)
ATERM = _g.terms[0]
DFS = [2.0, 3.0, 4.0, 5.0, 6.8, 8.0, 10.0, 13.0, 16.0, 19.0]
lam_curves, lam_vals, lam_gcv, lam_r2 = {}, {}, {}, {}
for d in DFS:
    ATERM.lam = approx_lam(XA, ATERM, d)
    g = LinearGAM(ATERM).fit(XA, Y)
    key = k(d)
    lam_curves[key] = r(g.predict(SGRID))
    lam_vals[key] = float("%.4g" % ATERM.lam)
    lam_gcv[key] = round(float(g.statistics_["GCV"]), 2)
    lam_r2[key] = round(float(g.statistics_["pseudo_r2"]["explained_deviance"]), 4)
    lam_dfchk = round(float(degrees_of_freedom(XA, ATERM)), 3)

_gs = LinearGAM(s_gam(0)).fit(XA, Y).gridsearch(XA, Y, progress=False)
PICK = {"lam": float("%.5g" % float(np.asarray(_gs.terms[0].lam).ravel()[0])),
        "df": round(float(_gs.statistics_["edof"]), 2),
        "gcv": round(float(_gs.statistics_["GCV"]), 2)}
PICK["curve"] = r(_gs.predict(SGRID))


# ══════════════════════════════════════════════════════════════════════
# 4. GAM 三面板（ISLP 圖 7.11–7.12）
#    照 lab 儲存格 82／86：Xgam = [age, year, education.cat.codes]，
#    s(0) + s(1, n_splines=7) + f(2, lam=0)，age／year 的 lam 用 approx_lam 定 df。
# ══════════════════════════════════════════════════════════════════════
XGAM = np.column_stack([AGE, YEAR, Wage["education"].cat.codes])
EDU_LABELS = [c.split(". ", 1)[1] for c in Wage["education"].cat.categories]
AGE_DFS = [2.0, 3.0, 4.0, 5.0, 7.0, 10.0]
YEAR_DFS = [2.0, 3.0, 4.0, 5.0, 6.0]
REF_AGE_DF, REF_YEAR_DF = 5.0, 5.0            # lab 用 df=4+1（含截距）
GAGE = np.linspace(A0, A1, 60)
GYEAR = np.linspace(float(YEAR.min()), float(YEAR.max()), 60)


def gam_spec():
    return LinearGAM(s_gam(0) + s_gam(1, n_splines=7) + f_gam(2, lam=0))


# approx_lam 需要 term 已經編譯過（edge_knots_ 是 fit 時才有的），所以先配一次預設模型，
# 再反解各個 df 對應的 lam——跟 lab 儲存格 82（先 fit）→ 86（設 lam 再 fit）同一個順序。
_gtmp = gam_spec().fit(XGAM, Y)
LAM_AGE = {a: approx_lam(XGAM, _gtmp.terms[0], a) for a in AGE_DFS}
LAM_YEAR = {v: approx_lam(XGAM, _gtmp.terms[1], v) for v in YEAR_DFS}


def gam_fit(age_df, year_df):
    m = gam_spec()
    m.terms[0].lam = LAM_AGE[age_df]
    m.terms[1].lam = LAM_YEAR[year_df]
    return m.fit(XGAM, Y)


def partial(g, term, grid):
    """偏依賴曲線。跟 lab 儲存格 78／80 一樣減掉自己的平均（centering），
    三個面板才能放在同一把縱軸尺上比高低（ISLP 圖 7.11／7.12 就是這樣畫的）。"""
    XX = g.generate_X_grid(term=term, n=len(grid))
    XX[:, term] = grid
    pd_, ci = g.partial_dependence(term=term, X=XX, width=0.95)
    c = float(np.mean(pd_))
    return {"fit": r(pd_ - c), "lo": r(ci[:, 0] - c), "hi": r(ci[:, 1] - c)}


gam_age, gam_year, gam_grid = {}, {}, {}
gam_edu = None
for a in AGE_DFS:
    for yy in YEAR_DFS:
        g = gam_fit(a, yy)
        # 高斯 GAM 的 deviance 就是 RSS（pygam 的 statistics_['deviance'] 不是這個量，
        # 它跟 lab 儲存格 96 的 anova_gam deviance 欄對不起來，所以自己算）
        gam_grid[f"{k(a)}|{k(yy)}"] = {
            "r2": round(float(g.statistics_["pseudo_r2"]["explained_deviance"]), 4),
            "dev": round(float(np.sum((Y - g.predict(XGAM)) ** 2)), 0),
            "edof": round(float(g.statistics_["edof"]), 2),
            "gcv": round(float(g.statistics_["GCV"]), 1)}
        if yy == REF_YEAR_DF:
            gam_age[k(a)] = partial(g, 0, GAGE)
        if a == REF_AGE_DF:
            gam_year[k(yy)] = partial(g, 1, GYEAR)
        if a == REF_AGE_DF and yy == REF_YEAR_DF:
            XX = g.generate_X_grid(term=2)
            pd_, ci = g.partial_dependence(term=2, X=XX, width=0.95)
            codes = np.asarray(XX[:, 2])
            idx = [int(np.argmin(np.abs(codes - lv))) for lv in range(len(EDU_LABELS))]
            cen = float(np.mean(pd_[idx]))
            gam_edu = {"fit": r(pd_[idx] - cen), "lo": r(ci[idx, 0] - cen),
                       "hi": r(ci[idx, 1] - cen)}

# 三個面板共用的縱軸範圍：要能比高低，就必須同一把尺
_allv = []
for _d in list(gam_age.values()) + list(gam_year.values()) + [gam_edu]:
    _allv += _d["lo"] + _d["hi"]
GAM_YR = [float(np.floor(min(_allv) / 10) * 10), float(np.ceil(max(_allv) / 10) * 10)]


# ══════════════════════════════════════════════════════════════════════
# 輸出
# ══════════════════════════════════════════════════════════════════════
def js(name, obj, src, seed, note=""):
    meta = {"src": src, "seed": seed, "versions": VERSIONS, "gen": GEN}
    if note:
        meta["note"] = note
    return (f"const {name} = " + json.dumps({"meta": meta, **obj},
                                            ensure_ascii=False, separators=(",", ":")) + ";")


out = [
    js("FRAMES_w08wage",
       {"n": len(SUB), "age": r(sub_age, 0), "wage": r(sub_y, 1),
        "ageMin": A0, "ageMax": A1, "nFull": N, "nPool": int(len(POOL))},
       f"ISLP Wage（{LAB} 儲存格 11 的同一份資料）的 90 筆隨機子樣本",
       "np.random.default_rng(524)，size=90, replace=False",
       "只從 wage ≤ 250 的 2921 筆抽——ISLP 圖 7.3／7.4 用的子集也在這個範圍內，"
       "另外 79 筆 wage>250 的高收入者依 §7.1 是另一群母體。"
       "step／basis／knot／loess 四個 live 元件都在這 90 點上即時重算，"
       "所以拖動時看到的數字是瀏覽器算的，不是這裡烘焙的"),
    js("FRAMES_w08poly",
       {"grid": r(PGRID, 1), "degrees": DEGS, "fit": poly_fit, "lo": poly_lo, "hi": poly_hi,
        "trainMSE": poly_train, "cvMSE": poly_cv},
       f"ISLP Wage age–wage · 自算（對照 {LAB} 儲存格 14 的 degree 4）",
       "KFold(n_splits=10, shuffle=True, random_state=0)，各 degree 共用同一組分割",
       f"age 先線性壓到 [-1,1] 再取冪次；與 poly() 的正交基底張出同一空間，"
       f"degree 4 的配適值最大差 {POLY_MAXDIFF:.2e}"),
    js("FRAMES_w08nat",
       {"grid": r(SGRID, 1), "knots": KNOTS, "cubic": cubic, "natural": natural,
        "widthCubic": CUB_W, "widthNatural": NAT_W},
       "ISLP 圖 7.4 · Wage 全體 n=3000，兩者都用內部節點 25／40／60",
       "無隨機性（最小平方閉式解）",
       f"立方樣條 {cubic['df']} 個參數、自然樣條 {natural['df']} 個參數；"
       f"BSpline／NaturalSpline 取自 ISLP.transforms（{LAB} 儲存格 44、56 用的同一組）"),
    js("FRAMES_w08lam",
       {"grid": r(SGRID, 1), "dfs": DFS, "curves": lam_curves, "lams": lam_vals,
        "gcv": lam_gcv, "r2": lam_r2, "pick": PICK},
       f"ISLP 圖 7.8 · pygam LinearGAM(s(0)) on Wage age（{LAB} 儲存格 71、73）",
       "無隨機性；lam 由 ISLP.pygam.approx_lam 反解到指定的 df",
       "df_λ 用 degrees_of_freedom() 的定義（含未懲罰的截距，下限 2）。"
       "pygam 預設 n_splines=20，所以 df 上限約 19，不是課本說的 n。"
       "PICK 是 pygam gridsearch 依 GCV 選出來的，不是課本圖 7.8 的 LOOCV"),
    js("FRAMES_w08gam",
       {"ageGrid": r(GAGE, 1), "yearGrid": r(GYEAR, 2), "eduLabels": EDU_LABELS,
        "ageDfs": AGE_DFS, "yearDfs": YEAR_DFS, "refAgeDf": REF_AGE_DF,
        "refYearDf": REF_YEAR_DF, "ageCurves": gam_age, "yearCurves": gam_year,
        "edu": gam_edu, "grid": gam_grid, "yRange": GAM_YR},
       f"ISLP 圖 7.11–7.12 · {LAB} 儲存格 82／86 的同一個模型規格",
       "無隨機性；age／year 的 lam 由 approx_lam 反解到指定的 df",
       "曲線是切片：age 曲線固定 year df=5、year 曲線固定 age df=5（偏依賴曲線"
       "幾乎不受另一項的 lam 影響）；R²／deviance／EDoF 則是每一組 (age df, year df) "
       "真的配出來的。education 是 f(2, lam=0) 的類別項，沒有 df 可調"),
]
print("\n".join(out))

REF = f"{k(REF_AGE_DF)}|{k(REF_YEAR_DF)}"
print(f"\n/* 檢查：degree 4 配適值 vs poly() 最大差 {POLY_MAXDIFF:.3e}（應該 ~1e-9）· "
      f"degree 1／4／15 的 CV MSE = {poly_cv[0]}／{poly_cv[3]}／{poly_cv[14]}"
      f"（訓練 {poly_train[0]}／{poly_train[3]}／{poly_train[14]}）· "
      f"立方樣條兩端信賴帶寬 {CUB_W} vs 自然樣條 {NAT_W} · "
      f"平滑樣條 df 檢核 {lam_dfchk} · gridsearch 選出 df={PICK['df']}（課本圖 7.8 的 LOOCV 是 6.8）· "
      f"GAM 參考組 ({k(REF_AGE_DF)},{k(REF_YEAR_DF)}) R²={gam_grid[REF]['r2']}、EDoF={gam_grid[REF]['edof']}、"
      f"GCV={gam_grid[REF]['gcv']}、deviance={gam_grid[REF]['dev']:.0f}"
      f"（lab 儲存格 98 是 EDoF 12.9927／GCV 1246.1129／Pseudo R² 0.2928，"
      f"儲存格 96 的 gam_full deviance 是 3.693143e+06）*/", file=sys.stderr)
