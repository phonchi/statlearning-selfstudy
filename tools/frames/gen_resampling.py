#!/usr/bin/env python3
"""產生 resampling_methods.html 需要的烘焙資料（FRAMES_w05*）。

只有「lab notebook 沒有存下輸出」或「需要一整條曲線」的圖才在這裡產生；
凡是 lab 裡已經有輸出的數字，頁面上一律逐字抄 lab，不在這裡重算。

跑法（用 pinned 環境，數字才可重現）：
  conda run -n m524 python tools/frames/gen_resampling.py > /tmp/w05.js

輸出是可以直接貼進頁面的 JS literal。
"""
import json
import sys

import numpy as np
from ISLP import load_data
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, LeaveOneOut, cross_val_score, train_test_split

VERSIONS = ("numpy {} · pandas {} · scikit-learn {}".format(
    np.__version__, __import__("pandas").__version__, __import__("sklearn").__version__))
GEN = "tools/frames/gen_resampling.py"
MAXDEG = 10

Auto = load_data("Auto")
H = np.asarray(Auto["horsepower"], dtype=float)
Y = np.asarray(Auto["mpg"], dtype=float)
N = len(Y)


def poly_design(h, d):
    """1, h, h², …, h^d。與 lab 的 np.power.outer(H, np.arange(d+1)) 同構。"""
    return np.power.outer(h, np.arange(d + 1))[:, 1:]      # sklearn 自帶 intercept


def mse(a, b):
    return float(np.mean((a - b) ** 2))


# ── 1. 驗證集法：10 種不同切分 × degree 1..10（ISLP 圖 5.2 右）────────────
val_curves = []
for seed in range(10):
    tr, te = train_test_split(np.arange(N), test_size=196, random_state=seed)
    row = []
    for d in range(1, MAXDEG + 1):
        X = poly_design(H, d)
        m = LinearRegression().fit(X[tr], Y[tr])
        row.append(round(mse(Y[te], m.predict(X[te])), 4))
    val_curves.append(row)

# lab 儲存格 26 / 28 的兩組真實數字，頁面上要對得起來
lab_split_rng42 = [25.57387819, 22.21802005, 22.66767544]
lab_split_seed3 = [20.75540796, 16.94510676, 16.97437833]

# ── 2. LOOCV 與 10-fold，degree 1..10（lab 儲存格 37 / 41 沒存輸出）──────
loocv, kf10 = [], []
loo = LeaveOneOut()
kf = KFold(n_splits=10, shuffle=True, random_state=0)      # 與 lab 同設定
for d in range(1, MAXDEG + 1):
    X = poly_design(H, d)
    loocv.append(round(-cross_val_score(LinearRegression(), X, Y, cv=loo,
                                        scoring="neg_mean_squared_error").mean(), 4))
    kf10.append(round(-cross_val_score(LinearRegression(), X, Y, cv=kf,
                                       scoring="neg_mean_squared_error").mean(), 4))

# ── 3. 每一折的 MSE（degree 2），給分割動畫器右側的累計表 ────────────────
fold_detail = {}
for k in (2, 5, 10):
    X = poly_design(H, 2)
    kfk = KFold(n_splits=k, shuffle=True, random_state=0)
    per = []
    for tr, te in kfk.split(X):
        m = LinearRegression().fit(X[tr], Y[tr])
        per.append({"n_train": int(len(tr)), "n_held": int(len(te)),
                    "mse": round(mse(Y[te], m.predict(X[te])), 4)})
    fold_detail[str(k)] = per

# ── 4. Bootstrap：Portfolio 的 α（ISLP §5.2）────────────────────────────
Portfolio = load_data("Portfolio")
PX, PY = np.asarray(Portfolio["X"], dtype=float), np.asarray(Portfolio["Y"], dtype=float)


def alpha_hat(x, y):
    sx, sy = np.var(x, ddof=1), np.var(y, ddof=1)
    sxy = np.cov(x, y, ddof=1)[0, 1]
    return float((sy - sxy) / (sx + sy - 2 * sxy))


rng = np.random.default_rng(0)
n = len(PX)
boot = [alpha_hat(*(lambda i: (PX[i], PY[i]))(rng.integers(0, n, n))) for _ in range(1000)]
boot_hist, boot_edges = np.histogram(boot, bins=24)

# ── 5. CV 的錯用 vs 正用：p 遠大於 n 的純噪音資料 ────────────────────────
rng2 = np.random.default_rng(7)
n_obs, p_all, k_sel = 50, 500, 10
Xn = rng2.standard_normal((n_obs, p_all))
yn = rng2.integers(0, 2, n_obs)                 # 與 X 完全無關
corr = np.array([abs(np.corrcoef(Xn[:, j], yn)[0, 1]) for j in range(p_all)])
top = np.argsort(-corr)[:k_sel]                 # 先用全部資料挑特徵 ← 錯的做法
kf5 = KFold(n_splits=5, shuffle=True, random_state=0)
from sklearn.linear_model import LogisticRegression  # noqa: E402

wrong = 1 - cross_val_score(LogisticRegression(max_iter=2000), Xn[:, top], yn, cv=kf5).mean()
right_scores = []
for tr, te in kf5.split(Xn):
    c = np.array([abs(np.corrcoef(Xn[tr, j], yn[tr])[0, 1]) for j in range(p_all)])
    sel = np.argsort(-c)[:k_sel]                # 在每個 fold 內才挑 ← 對的做法
    m = LogisticRegression(max_iter=2000).fit(Xn[tr][:, sel], yn[tr])
    right_scores.append(m.score(Xn[te][:, sel], yn[te]))
right = 1 - float(np.mean(right_scores))

# ── 輸出 ────────────────────────────────────────────────────────────────
def js(name, obj, src, seed, note=""):
    meta = {"src": src, "seed": seed, "versions": VERSIONS, "gen": GEN}
    if note:
        meta["note"] = note
    return (f"const {name} = " + json.dumps({"meta": meta, **obj},
                                            ensure_ascii=False, separators=(",", ":")) + ";")


out = [
    js("FRAMES_w05val", {"degrees": list(range(1, MAXDEG + 1)), "curves": val_curves,
                         "labRng42": lab_split_rng42, "labSeed3": lab_split_seed3},
       "ISLP Auto · 自算（對照 Ch05-resample-lab-zh.ipynb 儲存格 26／28）",
       "train_test_split(test_size=196, random_state=0..9)"),
    js("FRAMES_w05cv", {"degrees": list(range(1, MAXDEG + 1)), "loocv": loocv, "kfold10": kf10},
       "Ch05-resample-lab-zh.ipynb 儲存格 37／41（該格未存輸出，用同設定重算）",
       "KFold(n_splits=10, shuffle=True, random_state=0)",
       f"degree 1 的 LOOCV = {loocv[0]}，與 lab 儲存格 32 的 24.2315 相符"),
    js("FRAMES_w05fold", {"detail": fold_detail, "n": N, "degree": 2},
       "ISLP Auto · degree 2 · 自算", "KFold(shuffle=True, random_state=0)"),
    js("FRAMES_w05boot", {"n": n, "alphaHat": round(alpha_hat(PX, PY), 6),
                          "bootMean": round(float(np.mean(boot)), 6),
                          "bootSE": round(float(np.std(boot, ddof=1)), 6),
                          "hist": boot_hist.tolist(),
                          "edges": [round(float(e), 4) for e in boot_edges]},
       "ISLP Portfolio（ISLP §5.2 的 α 範例）", "np.random.default_rng(0)，B = 1000"),
    js("FRAMES_w05misuse", {"n": n_obs, "p": p_all, "kSel": k_sel,
                            "wrongErr": round(float(wrong), 4),
                            "rightErr": round(float(right), 4)},
       "純噪音模擬（y 與 X 完全獨立）", "np.random.default_rng(7)",
       "正確做法的錯誤率應該接近 0.5"),
]
print("\n".join(out))

print(f"\n/* 檢查：LOOCV degree1={loocv[0]}（lab 24.2315）· "
      f"驗證集 seed0 degree1..3={val_curves[0][:3]} · "
      f"alpha_hat={alpha_hat(PX, PY):.4f}（ISLP 書上 0.5758）· "
      f"bootSE={np.std(boot, ddof=1):.4f}（ISLP 書上約 0.089）· "
      f"誤用 CV 錯誤率={wrong:.3f} vs 正用={right:.3f} */", file=sys.stderr)
