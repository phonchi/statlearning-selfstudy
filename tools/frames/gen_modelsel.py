#!/usr/bin/env python3
"""產生 model_selection.html 需要的烘焙資料（FRAMES_w06*）。

只有「需要一整條曲線」或「要對上課本圖」的圖才在這裡產生；凡是 lab 裡已經有
輸出的數字，頁面上一律逐字抄 lab（lab_output()），不在這裡重算。

四組輸出資料：
  1. FRAMES_w06lat    Credit 取 4 個變數的完整子集格圖（16 個 RSS）
                      → 用真實資料證明 forward stepwise 會錯過最佳子集
  2. FRAMES_w06ridge  Credit 的 Ridge 係數路徑（ISLP 圖 6.4）
  3. FRAMES_w06lasso  Credit 的 Lasso 係數路徑與存活變數（ISLP 圖 6.6）
  4. FRAMES_w06hd     p 逼近 n：訓練 R² → 1 而測試 MSE 爆炸（ISLP 圖 6.23）

跑法（用 pinned 環境，數字才可重現）：
  conda run -n m524 python tools/frames/gen_modelsel.py > /tmp/w06.js

輸出是可以直接貼進頁面的 JS literal。
"""
import itertools
import json
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
from ISLP import load_data
from sklearn.linear_model import Lasso, LassoCV, LinearRegression, Ridge, lasso_path
from sklearn.model_selection import KFold

VERSIONS = "numpy {} · pandas {} · scikit-learn {} · statsmodels {}".format(
    np.__version__, pd.__version__, __import__("sklearn").__version__, sm.__version__)
GEN = "tools/frames/gen_modelsel.py"

# ── Credit：跟 ISLP §6.1 的圖用同一份資料 ────────────────────────────────
Credit = load_data("Credit").drop(columns=["ID"])
YC = np.asarray(Credit["Balance"], dtype=float)
XC_df = pd.get_dummies(Credit.drop(columns=["Balance"]), drop_first=True).astype(float)
XC = np.asarray(XC_df)
NC, PC = XC.shape                                   # 400 × 11（Ethnicity 佔兩個虛擬變數）
COLS = list(XC_df.columns)
ZH = {"Income": "Income", "Limit": "Limit", "Rating": "Rating", "Cards": "Cards",
      "Age": "Age", "Education": "Education", "Gender_Female": "Gender[F]",
      "Student_Yes": "Student[Y]", "Married_Yes": "Married[Y]",
      "Ethnicity_Asian": "Ethn[Asian]", "Ethnicity_Caucasian": "Ethn[Cauc]"}
SHORT = [ZH[c] for c in COLS]
TSS = float(((YC - YC.mean()) ** 2).sum())


def rss_of(X, y, idx):
    """含截距的最小平方 RSS。idx 是欄位索引 list。"""
    A = np.column_stack([np.ones(len(y))] + [X[:, j] for j in idx]) if idx \
        else np.ones((len(y), 1))
    b, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ b
    return float(r @ r)


def best_subset(X, y, k, universe=None):
    """窮舉大小為 k 的所有子集，回傳 (RSS, 欄位索引 tuple)。"""
    pool = universe if universe is not None else range(X.shape[1])
    return min((rss_of(X, y, list(c)), c) for c in itertools.combinations(pool, k))


def forward_path(X, y, universe=None):
    """forward stepwise：每一步加一個讓 RSS 降最多的變數。"""
    pool = list(universe) if universe is not None else list(range(X.shape[1]))
    sel, out = [], []
    while pool:
        r, j = min((rss_of(X, y, sel + [j]), j) for j in pool)
        sel = sel + [j]
        pool.remove(j)
        out.append((r, tuple(sel)))
    return out


# ── 1. 子集格圖：Credit 取 4 個變數 ─────────────────────────────────────
LAT_NAMES = ["Limit", "Rating", "Cards", "Student_Yes"]
LAT_SHORT = ["Limit", "Rating", "Cards", "Student"]
lat_idx = [COLS.index(c) for c in LAT_NAMES]
lat_rss = []
for mask in range(16):
    idx = [lat_idx[b] for b in range(4) if mask >> b & 1]
    lat_rss.append(round(rss_of(XC, YC, idx) / 1e6, 4))

# 驗證：forward 在某個大小上真的錯過最佳子集（不然這個元件就沒故事可講）
_lat_best, _lat_fwd, _cur = {}, {}, 0
for size in range(1, 5):
    _lat_best[size] = min((lat_rss[m], m) for m in range(16) if bin(m).count("1") == size)
    _cur = min((lat_rss[_cur | 1 << b], _cur | 1 << b) for b in range(4) if not _cur >> b & 1)[1]
    _lat_fwd[size] = _cur
LAT_DIVERGE = [s for s in range(1, 5) if _lat_fwd[s] != _lat_best[s][1]]
assert LAT_DIVERGE == [3], f"格圖的分歧點變了：{LAT_DIVERGE}"

# ── 五準則自我檢查（不輸出）：Credit 的最佳子集前緣 ─────────────────────
sigma2 = rss_of(XC, YC, list(range(PC))) / (NC - PC - 1)

front = {}                                          # size → (rss, cols)
for k in range(1, PC + 1):
    front[k] = best_subset(XC, YC, k)

fwd_all = forward_path(XC, YC)

sizes = list(range(1, PC + 1))
crit = {"rss": [], "cp": [], "bic": [], "aic": [], "adjr2": [], "r2": [],
        "vars": [], "fwdVars": [], "fwdRss": []}
for k in sizes:
    r, cols = front[k]
    A = sm.add_constant(np.column_stack([XC[:, j] for j in cols]))
    fit = sm.OLS(YC, A).fit()
    crit["rss"].append(round(r / 1e6, 4))
    crit["r2"].append(round(1 - r / TSS, 4))
    crit["cp"].append(round((r + 2 * k * sigma2) / NC, 1))
    crit["bic"].append(round((r + np.log(NC) * k * sigma2) / NC, 1))
    crit["aic"].append(round(float(fit.aic), 1))     # statsmodels 的 log-likelihood 版
    crit["adjr2"].append(round(1 - (r / (NC - k - 1)) / (TSS / (NC - 1)), 5))
    crit["vars"].append([ZH[COLS[j]] for j in cols])
    crit["fwdVars"].append([ZH[COLS[j]] for j in fwd_all[k - 1][1]])
    crit["fwdRss"].append(round(fwd_all[k - 1][0] / 1e6, 4))

# 10-fold CV：每一折內重跑最佳子集（不然就洩漏了）
kf = KFold(n_splits=10, shuffle=True, random_state=0)
cv_raw = np.zeros((PC, 10))
for f, (tr, te) in enumerate(kf.split(XC)):
    for k in sizes:
        _, cols = best_subset(XC[tr], YC[tr], k)
        A = sm.add_constant(np.column_stack([XC[tr][:, j] for j in cols]))
        b, *_ = np.linalg.lstsq(A, YC[tr], rcond=None)
        At = sm.add_constant(np.column_stack([XC[te][:, j] for j in cols]))
        cv_raw[k - 1, f] = float(np.mean((YC[te] - At @ b) ** 2))
cv_mean = cv_raw.mean(1)
cv_se = cv_raw.std(1, ddof=1) / np.sqrt(10)

ARG = {"cp": int(np.argmin(crit["cp"])) + 1, "bic": int(np.argmin(crit["bic"])) + 1,
       "aic": int(np.argmin(crit["aic"])) + 1, "adjr2": int(np.argmax(crit["adjr2"])) + 1,
       "cv": int(np.argmin(cv_mean)) + 1}
# one-standard-error 規則：最小的那個大小，使 CV 誤差 ≤ 最小值 + 1 SE
_lo = cv_mean[ARG["cv"] - 1] + cv_se[ARG["cv"] - 1]
ARG["ose"] = int(next(k for k in sizes if cv_mean[k - 1] <= _lo))
assert (ARG["cp"], ARG["bic"], ARG["adjr2"]) == (6, 4, 7), \
    f"與 ISLP 圖 6.2 不符：Cp={ARG['cp']} BIC={ARG['bic']} adjR2={ARG['adjr2']}"

# ── 2. Ridge 係數路徑（輸出）＋ bias/variance 自我檢查（不輸出）─────────
Xs = (XC - XC.mean(0)) / XC.std(0)                   # 標準化：懲罰項對單位敏感
ols_full = LinearRegression().fit(Xs, YC)
norm_ols2 = float(np.linalg.norm(ols_full.coef_))

rlam = np.logspace(-2, 5, 40)
rcoefs = []
for lam in rlam:
    rcoefs.append(Ridge(alpha=lam).fit(Xs, YC).coef_)
rcoefs = np.array(rcoefs)                            # 40 × 11
r_l2ratio = np.linalg.norm(rcoefs, axis=1) / norm_ols2

# 模擬：n=50、p=45，所有係數都非零（跟 ISLP 圖 6.5 同設定）
rng = np.random.default_rng(6)
n_sim, p_sim, reps, n_test = 50, 45, 300, 400
Xtr = rng.standard_normal((n_sim, p_sim))
Xte = rng.standard_normal((n_test, p_sim))
beta_true = rng.standard_normal(p_sim) * 0.7
f_true = Xte @ beta_true
sd_eps = 3.0
blam = np.logspace(-1, 4, 26)
preds = np.zeros((len(blam), reps, n_test))
for b in range(reps):
    ytr = Xtr @ beta_true + sd_eps * rng.standard_normal(n_sim)
    for i, lam in enumerate(blam):
        preds[i, b] = Ridge(alpha=lam).fit(Xtr, ytr).predict(Xte)
bias2 = ((preds.mean(1) - f_true) ** 2).mean(1)
varc = preds.var(1, ddof=1).mean(1)
mse = bias2 + varc + sd_eps ** 2

# ── 3. Lasso 係數路徑（ISLP 圖 6.6）────────────────────────────────────
# sklearn 的 Lasso 目標是 (1/2n)·RSS + α‖β‖₁，課本式 6.7 是 RSS + λ‖β‖₁，
# 所以 λ = 2n·α。頁面上標的都是 λ。
lalphas, lcoefs, _ = lasso_path(Xs, YC - YC.mean(), n_alphas=40, eps=1e-4)
lcoefs = lcoefs.T                                    # 40 × 11
llam = 2 * NC * lalphas
norm_ols1 = float(np.abs(ols_full.coef_).sum())
l_l1ratio = np.abs(lcoefs).sum(1) / norm_ols1
l_nz = (np.abs(lcoefs) > 1e-8).sum(1)

lcv = LassoCV(cv=kf, n_alphas=100, random_state=0).fit(Xs, YC)
lcv_lam = 2 * NC * float(lcv.alpha_)
lcv_nz = int((np.abs(lcv.coef_) > 1e-8).sum())

# ── 4. p 逼近 n（輸出）＋圖 6.24 維度詛咒自我檢查（不輸出）──────────────
rng2 = np.random.default_rng(20260810)
n_hd, reps_hd, ps_hd = 20, 400, list(range(1, 20))   # p = 19 時參數個數 = n，訓練誤差歸零
tr_r2, tr_mse, te_mse = [], [], []
for p in ps_hd:
    a, b, c = [], [], []
    for _ in range(reps_hd):
        Xh = rng2.standard_normal((n_hd, p))
        yh = rng2.standard_normal(n_hd)              # y 與 X 完全無關
        Xh_te = rng2.standard_normal((400, p))
        yh_te = rng2.standard_normal(400)
        m = LinearRegression().fit(Xh, yh)
        pred = m.predict(Xh)
        a.append(1 - float(((yh - pred) ** 2).sum()) / float(((yh - yh.mean()) ** 2).sum()))
        b.append(float(np.mean((yh - pred) ** 2)))
        c.append(float(np.mean((yh_te - m.predict(Xh_te)) ** 2)))
    tr_r2.append(round(float(np.mean(a)), 4))
    # 對數軸畫不出 0：p = n − 1 時訓練 MSE 是 1e-30 級的數，夾在 1e-4 才畫得出來
    tr_mse.append(max(round(float(np.mean(b)), 4), 1e-4))
    te_mse.append(round(float(np.median(c)), 3))     # 用中位數：p≈n 時偶爾會爆到天上去

# 維度詛咒：n=100、20 個真訊號、p = 20／50／2000（ISLP 圖 6.24）
rng3 = np.random.default_rng(24)
curse = {}
for p in (20, 50, 2000):
    errs, dfs = [], []
    for _ in range(12):
        Xc = rng3.standard_normal((100, p))
        bt = np.zeros(p)
        bt[:20] = rng3.standard_normal(20) * 1.2
        yc = Xc @ bt + rng3.standard_normal(100)
        Xc_te = rng3.standard_normal((400, p))
        yc_te = Xc_te @ bt + rng3.standard_normal(400)
        cv = LassoCV(cv=5, n_alphas=40, random_state=0, max_iter=5000).fit(Xc, yc)
        m = Lasso(alpha=cv.alpha_, max_iter=5000).fit(Xc, yc)
        errs.append(float(np.mean((yc_te - m.predict(Xc_te)) ** 2)))
        dfs.append(int((np.abs(m.coef_) > 1e-8).sum()))
    curse[str(p)] = {"mse": round(float(np.median(errs)), 2),
                     "df": int(np.median(dfs))}


# ── 輸出 ────────────────────────────────────────────────────────────────
def js(name, obj, src, seed, note=""):
    meta = {"src": src, "seed": seed, "versions": VERSIONS, "gen": GEN}
    if note:
        meta["note"] = note
    return (f"const {name} = " + json.dumps({"meta": meta, **obj},
                                            ensure_ascii=False, separators=(",", ":")) + ";")


def r3(a, d=3):
    return [round(float(v), d) for v in a]


out = [
    js("FRAMES_w06lat",
       {"names": LAT_SHORT, "rss": lat_rss, "n": NC, "unit": "百萬",
        "diverge": LAT_DIVERGE},
       "ISLP Credit（Balance ~ Limit + Rating + Cards + Student）· 自算",
       "無隨機性（窮舉 2⁴ 個子集的最小平方 RSS）",
       f"forward stepwise 在大小 {LAT_DIVERGE} 上選到的子集與最佳子集不同"),

    js("FRAMES_w06ridge",
       {"names": SHORT, "lambdas": r3(rlam, 4),
        "l2ratio": r3(r_l2ratio, 4),
        "coefs": [r3(rcoefs[:, j], 2) for j in range(PC)],
        "olsNorm": round(norm_ols2, 2)},
       "ISLP Credit 標準化後的 Ridge 係數路徑（ISLP 圖 6.4）",
       "無隨機性（資料與 lambda 網格固定）",
       "sklearn Ridge 的 alpha 就是式 6.5 的 λ（目標函數是 RSS + λ‖β‖²）"),

    js("FRAMES_w06lasso",
       {"names": SHORT, "lambdas": r3(llam, 3), "l1ratio": r3(l_l1ratio, 4),
        "coefs": [r3(lcoefs[:, j], 2) for j in range(PC)],
        "nz": [int(v) for v in l_nz], "olsNorm1": round(norm_ols1, 2),
        "cvLambda": round(lcv_lam, 3), "cvNz": lcv_nz,
        "cvCoefs": r3(lcv.coef_, 2)},
       "ISLP Credit 標準化後的 Lasso 路徑（ISLP 圖 6.6）",
       "lasso_path(n_alphas=40)；LassoCV 用 KFold(10, shuffle=True, random_state=0)",
       "課本式 6.7 的 λ = 2n × sklearn 的 alpha，頁面上標的都是 λ"),

    js("FRAMES_w06hd",
       {"ps": ps_hd, "n": n_hd, "trainR2": tr_r2, "trainMse": tr_mse,
        "testMse": te_mse, "reps": reps_hd},
       "純噪音模擬：n=20，加入 p 個與 y 完全無關的變數（ISLP 圖 6.23）",
       "np.random.default_rng(20260810)",
       "測試 MSE 取 400 次重複的中位數（p 接近 n 時偶爾會爆到極大值）"),
]
print("\n".join(out))

print(f"\n/* 檢查："
      f"Cp→{ARG['cp']} BIC→{ARG['bic']} AIC→{ARG['aic']} adjR²→{ARG['adjr2']} "
      f"CV→{ARG['cv']} one-SE→{ARG['ose']}（ISLP 書上 6／4／—／7） · "
      f"格圖分歧於大小 {LAT_DIVERGE} · "
      f"σ̂²={sigma2:.0f} · "
      f"最佳 4 變數={crit['vars'][3]} vs forward={crit['fwdVars'][3]} · "
      f"Ridge λ=1e5 時 ‖β‖₂/‖β̂‖₂={r_l2ratio[-1]:.4f} · "
      f"Lasso CV λ={lcv_lam:.2f}（{lcv_nz}/{PC} 個非零） · "
      f"bias² {bias2[0]:.2f}→{bias2[-1]:.2f}，var {varc[0]:.2f}→{varc[-1]:.2f} · "
      f"訓練 R² p=1→{tr_r2[0]:.3f} p=18→{tr_r2[-1]:.3f}，"
      f"測試 MSE {te_mse[0]:.2f}→{te_mse[-1]:.1f} · "
      f"curse {curse} */", file=sys.stderr)
