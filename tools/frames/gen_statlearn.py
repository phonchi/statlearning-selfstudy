#!/usr/bin/env python3
"""產生 statistical_learning.html 需要的烘焙資料（FRAMES_w02*）。

第 2 章的 lab（Ch02-statlearn-lab-zh.ipynb）是 Python 入門，沒有任何統計學習的
數字可以抄，所以本頁所有圖表的資料都在這裡從模擬產生——固定種子、固定環境，
可重生也可 diff。四組資料：

  1. FRAMES_w02flex  ISLP 圖 2.9：同一組點的三種擬合 + 訓練／測試 MSE 曲線
  2. FRAMES_w02bv    ISLP 圖 2.12：偏差²、變異、Var(ε)、總測試 MSE（蒙地卡羅 M=300）
  3. FRAMES_w02knn   ISLP 圖 2.15–2.16：KNN 決策區域（K = 1/10/100）+ Bayes 邊界
  4. FRAMES_w02kerr  ISLP 圖 2.17：訓練／測試錯誤率對 1/K

彈性度一律用「樣條自由度 df」＝配適時估的參數個數（含截距）：
  df = 2/3/4 → 一次／二次／三次多項式
  df ≥ 5     → 三次迴歸樣條，節點依 van der Corput 順序逐一加入（巢狀！）
               節點集合巢狀 ⇒ 模型空間巢狀 ⇒ 訓練 MSE 與偏差² 保證單調不上升
               rank([1|X]) 實測恰好等於 df

跑法（用 pinned 環境，數字才可重現）：
  conda run -n m524 python tools/frames/gen_statlearn.py > /tmp/w02.js

輸出是可以直接貼進頁面的 JS literal。
"""
import json
import sys

import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import SplineTransformer

VERSIONS = f"numpy {np.__version__} · pandas {pd.__version__} · scikit-learn {sklearn.__version__}"
GEN = "tools/frames/gen_statlearn.py"

# ── 共用設定 ────────────────────────────────────────────────────────────
DFS = [2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 18, 22, 25]
N_TRAIN = 50
SIGMA = 1.0
X_LO, X_HI = 0.0, 100.0
X_TRAIN = np.linspace(X_LO, X_HI, N_TRAIN)          # 固定的訓練 x（只有 ε 在變）
X_GRID = np.linspace(X_LO, X_HI, 101)               # 畫曲線用
X_TEST = np.linspace(X_LO, X_HI, 201)               # 算 bias²／variance 的測試點

SCEN = {
    "A": ("中度非線性（對照圖 2.9）", lambda x: 6.0 + 2.6 * np.sin(x / 14.0) + 0.022 * x),
    "B": ("接近線性（對照圖 2.10）", lambda x: 2.4 + 0.085 * x + 0.45 * np.sin(x / 42.0)),
    "C": ("高度非線性（對照圖 2.11）",
          lambda x: 8.0 + 13.0 * np.exp(-((x - 28.0) / 9.0) ** 2)
          - 9.0 * np.exp(-((x - 68.0) / 7.0) ** 2) + 0.02 * x),
}


def _vdc(n):
    """van der Corput（base 2）：0.5, 0.25, 0.75, 0.125, 0.625, … 愈加愈細且巢狀。"""
    out, i = [], 1
    while len(out) < n:
        k, f, v = i, 0.5, 0.0
        while k:
            v += (k & 1) * f
            k >>= 1
            f /= 2
        if 0.0 < v < 1.0 and v not in out:
            out.append(v)
        i += 1
    return out


KNOT_ORDER = [round(X_LO + (X_HI - X_LO) * v, 6) for v in _vdc(max(DFS))]


def design(d, xs):
    """df = d 的設計矩陣（不含截距）。節點集合巢狀，所以模型空間也巢狀。"""
    if d in (2, 3, 4):
        return np.column_stack([xs ** k for k in range(1, d)])
    knots = np.array(sorted([X_LO, X_HI] + KNOT_ORDER[:d - 4])).reshape(-1, 1)
    st = SplineTransformer(knots=knots, degree=3, include_bias=False)
    st.fit(np.array([[X_LO], [X_HI]]))
    return st.transform(xs.reshape(-1, 1))


def fit_predict(d, xtr, ytr, xnew):
    m = LinearRegression().fit(design(d, xtr), ytr)
    return m.predict(design(d, xtr)), m.predict(design(d, xnew))


def r(a, k=4):
    return [round(float(v), k) for v in np.asarray(a).ravel()]


# ══ 1. ISLP 圖 2.9：同一組點的三種擬合 ═════════════════════════════════
FLEX_SHOW = [2, 6, 25]
name_A, f_A = SCEN["A"]
rng = np.random.default_rng(2)
y_one = f_A(X_TRAIN) + SIGMA * rng.standard_normal(N_TRAIN)

# 大量獨立測試樣本（同一個 f 與 σ），用來算誠實的測試 MSE
x_big = np.linspace(X_LO, X_HI, 4001)
y_big = f_A(x_big) + SIGMA * rng.standard_normal(x_big.size)

flex_fits, flex_train, flex_test = {}, [], []
for d in DFS:
    tr_hat, big_hat = fit_predict(d, X_TRAIN, y_one, x_big)
    flex_train.append(float(np.mean((y_one - tr_hat) ** 2)))
    flex_test.append(float(np.mean((y_big - big_hat) ** 2)))
    if d in FLEX_SHOW:
        flex_fits[str(d)] = r(fit_predict(d, X_TRAIN, y_one, X_GRID)[1], 3)

# ══ 2. ISLP 圖 2.12：偏差–變異拆解（蒙地卡羅）════════════════════════════
M = 300
bv = {}
for key, (label, f) in SCEN.items():
    grng = np.random.default_rng(524)
    eps = SIGMA * grng.standard_normal((M, N_TRAIN))     # 三個情境共用同一組噪音
    ftrue_test = f(X_TEST)
    ftrue_train = f(X_TRAIN)
    bias2, var, train_mse = [], [], []
    for d in DFS:
        preds = np.empty((M, X_TEST.size))
        tr_err = np.empty(M)
        for m in range(M):
            y = ftrue_train + eps[m]
            tr_hat, te_hat = fit_predict(d, X_TRAIN, y, X_TEST)
            preds[m] = te_hat
            tr_err[m] = np.mean((y - tr_hat) ** 2)
        bias2.append(float(np.mean((preds.mean(0) - ftrue_test) ** 2)))
        var.append(float(np.mean(preds.var(0, ddof=1))))
        train_mse.append(float(tr_err.mean()))
    total = [b + v + SIGMA ** 2 for b, v in zip(bias2, var)]
    bv[key] = {
        "label": label, "bias2": r(bias2), "var": r(var),
        "total": r(total), "train": r(train_mse),
        "argmin": int(np.argmin(total)),
    }

# ══ 3. ISLP 圖 2.13／2.15／2.16：二維兩類資料、KNN 決策區域、Bayes 邊界 ══
SD = 0.80
C0 = np.array([[-1.30, 0.60], [1.30, -1.10]])      # 類別 0（藍）的兩個成分中心
C1 = np.array([[0.10, 1.70], [2.30, 0.30]])        # 類別 1（橘）的兩個成分中心


def mix_density(P, cs):
    """等權重的兩成分等向常態混合密度（未乘先驗）。"""
    out = np.zeros(len(P))
    for c in cs:
        d2 = ((P - c) ** 2).sum(1)
        out += 0.5 * np.exp(-d2 / (2 * SD ** 2)) / (2 * np.pi * SD ** 2)
    return out


def p_orange(P):
    d0, d1 = mix_density(P, C0), mix_density(P, C1)
    return d1 / (d0 + d1)


def draw(n, seed):
    g = np.random.default_rng(seed)
    lab = g.integers(0, 2, n)
    comp = g.integers(0, 2, n)
    cen = np.where(lab[:, None] == 1, C1[comp], C0[comp])
    return cen + SD * g.standard_normal((n, 2)), lab


Xtr, ytr = draw(200, 11)
Xte, yte = draw(5000, 77)
bayes_err = float(np.mean(np.minimum(p_orange(Xte), 1 - p_orange(Xte))))

pad = 0.55
xd = [float(Xtr[:, 0].min() - pad), float(Xtr[:, 0].max() + pad)]
yd = [float(Xtr[:, 1].min() - pad), float(Xtr[:, 1].max() + pad)]

G = 30
gx = np.linspace(xd[0], xd[1], G)
gy = np.linspace(yd[0], yd[1], G)
GX, GY = np.meshgrid(gx, gy)
GP = np.column_stack([GX.ravel(), GY.ravel()])

KSHOW = [1, 10, 100]
regions, kerr = {}, {}
for k in KSHOW:
    kn = KNeighborsClassifier(n_neighbors=k).fit(Xtr, ytr)
    regions[str(k)] = "".join(str(int(v)) for v in kn.predict(GP))   # row-major，先掃 y 再掃 x
    kerr[str(k)] = {"train": round(float(1 - kn.score(Xtr, ytr)), 4),
                    "test": round(float(1 - kn.score(Xte, yte)), 4)}

# Bayes 邊界：對 p(x) − 0.5 做 marching squares，輸出線段
FG = 90
fx = np.linspace(xd[0], xd[1], FG)
fy = np.linspace(yd[0], yd[1], FG)
FX, FY = np.meshgrid(fx, fy)
Z = (p_orange(np.column_stack([FX.ravel(), FY.ravel()])) - 0.5).reshape(FG, FG)

segs = []
for i in range(FG - 1):
    for j in range(FG - 1):
        cell = [(Z[i, j], fx[j], fy[i], Z[i, j + 1], fx[j + 1], fy[i]),          # 下
                (Z[i, j + 1], fx[j + 1], fy[i], Z[i + 1, j + 1], fx[j + 1], fy[i + 1]),  # 右
                (Z[i + 1, j + 1], fx[j + 1], fy[i + 1], Z[i + 1, j], fx[j], fy[i + 1]),  # 上
                (Z[i + 1, j], fx[j], fy[i + 1], Z[i, j], fx[j], fy[i])]          # 左
        pts = []
        for za, xa, ya, zb, xb, yb in cell:
            if (za > 0) != (zb > 0):
                t = za / (za - zb)
                pts.append((xa + t * (xb - xa), ya + t * (yb - ya)))
        if len(pts) == 2:
            segs.append([round(pts[0][0], 3), round(pts[0][1], 3),
                         round(pts[1][0], 3), round(pts[1][1], 3)])
        elif len(pts) == 4:                      # 鞍點：配成兩段
            for a, b in ((0, 1), (2, 3)):
                segs.append([round(pts[a][0], 3), round(pts[a][1], 3),
                             round(pts[b][0], 3), round(pts[b][1], 3)])

# ══ 4. ISLP 圖 2.17：訓練／測試錯誤率對 1/K ═════════════════════════════
KS = [1, 2, 3, 4, 5, 7, 10, 13, 17, 25, 35, 50, 70, 100, 150]
ktrain, ktest = [], []
for k in KS:
    kn = KNeighborsClassifier(n_neighbors=k).fit(Xtr, ytr)
    ktrain.append(round(float(1 - kn.score(Xtr, ytr)), 4))
    ktest.append(round(float(1 - kn.score(Xte, yte)), 4))
best_k = KS[int(np.argmin(ktest))]


# ══ 輸出 ═══════════════════════════════════════════════════════════════
def js(name, obj, src, seed, note=""):
    meta = {"src": src, "seed": seed, "versions": VERSIONS, "gen": GEN}
    if note:
        meta["note"] = note
    return (f"const {name} = " + json.dumps({"meta": meta, **obj},
                                            ensure_ascii=False, separators=(",", ":")) + ";")


out = [
    js("FRAMES_w02flex",
       {"x": r(X_TRAIN, 2), "y": r(y_one, 3), "grid": r(X_GRID, 2),
        "truef": r(f_A(X_GRID), 3), "dfs": DFS, "show": FLEX_SHOW, "fits": flex_fits,
        "trainMse": r(flex_train), "testMse": r(flex_test), "sigma2": SIGMA ** 2,
        "nTrain": N_TRAIN, "nTest": int(x_big.size)},
       "自行模擬（對照 ISLP 圖 2.9：同一份資料的三種擬合與訓練／測試 MSE）",
       "np.random.default_rng(2)",
       "真實 f(x) = 6 + 2.6 sin(x/14) + 0.022 x，σ = 1；測試 MSE 用 4001 筆獨立樣本"),
    js("FRAMES_w02bv",
       {"dfs": DFS, "sigma2": SIGMA ** 2, "M": M, "nTrain": N_TRAIN, "scen": bv},
       "自行模擬（對照 ISLP 圖 2.12 的三個面板；拆解式見 ISLP 式 2.7／ESL 式 7.9）",
       "np.random.default_rng(524)，M = 300 組訓練集",
       "三個情境共用同一組 ε，所以曲線的差異只來自真實 f 的形狀"),
    js("FRAMES_w02knn",
       {"x1": r(Xtr[:, 0], 3), "x2": r(Xtr[:, 1], 3),
        "y": [int(v) for v in ytr], "xd": [round(v, 3) for v in xd],
        "yd": [round(v, 3) for v in yd], "g": G, "ks": KSHOW,
        "regions": regions, "err": kerr, "bayesSeg": segs,
        "bayesErr": round(bayes_err, 4), "nTrain": int(len(ytr)), "nTest": int(len(yte))},
       "自行模擬的兩類高斯混合（對照 ISLP 圖 2.13／2.15／2.16）",
       "np.random.default_rng(11) 訓練、default_rng(77) 測試",
       "Bayes 邊界是 p(橘|x) = 0.5 的等高線，由 90×90 格點做 marching squares 取出"),
    js("FRAMES_w02kerr",
       {"ks": KS, "invk": [round(1 / k, 5) for k in KS],
        "train": ktrain, "test": ktest,
        "bayesErr": round(bayes_err, 4), "bestK": int(best_k)},
       "同上那份模擬資料（對照 ISLP 圖 2.17）",
       "np.random.default_rng(11) 訓練、default_rng(77) 測試",
       "x 軸是 1/K：往右愈有彈性。訓練錯誤率在 K = 1 必定為 0"),
]
print("\n".join(out))

# ── 自我檢查（寫到 stderr，不進頁面）────────────────────────────────────
e = sys.stderr
print("\n/* ── 自我檢查 ─────────────────────────────── */", file=e)
print(f"df 清單 = {DFS}", file=e)
argmins = {}
for key in ("A", "B", "C"):
    s = bv[key]
    i = s["argmin"]
    argmins[key] = DFS[i]
    print(f"情境 {key} {s['label']}：test MSE 最低在 df = {DFS[i]}"
          f"（{s['total'][i]:.3f}）· df2 = {s['total'][0]:.3f} · df25 = {s['total'][-1]:.3f}"
          f" · bias² {s['bias2'][0]:.3f}→{s['bias2'][-1]:.3f}"
          f" · var {s['var'][0]:.3f}→{s['var'][-1]:.3f}", file=e)
    assert s["train"][0] >= s["train"][-1] - 1e-9, f"情境 {key} 訓練 MSE 不是單調下降"
    # bias² 允許 ±0.3 的節點對位抖動，但整體必須大幅下降
    for a, b in zip(s["bias2"], s["bias2"][1:]):
        assert b <= a + 0.3, f"情境 {key} 的 bias² 出現明顯上升（{a} → {b}）"
assert argmins["B"] == DFS[0], "情境 B（接近線性）的最佳 df 應該是最小的那個"
assert argmins["A"] > argmins["B"], "情境 A 的最佳 df 應該高於情境 B"
assert argmins["C"] > argmins["A"], "情境 C 的最佳 df 應該高於情境 A"
print(f"三個情境的最佳 df = {argmins}（ISLP 圖 2.12 的重點：最佳彈性隨真實 f 而異）", file=e)
print(f"變異曲線三個情境完全相同（線性平滑器的 Var 只看設計矩陣與 σ²）："
      f"{bv['A']['var'] == bv['B']['var'] == bv['C']['var']}", file=e)
print(f"單一資料集（情境 A）：訓練 MSE {flex_train[0]:.3f} → {flex_train[-1]:.3f}"
      f"；測試 MSE {flex_test[0]:.3f} → {flex_test[-1]:.3f}"
      f"，最低在 df = {DFS[int(np.argmin(flex_test))]}", file=e)
assert flex_train[0] > flex_train[-1], "單一資料集的訓練 MSE 應該隨 df 下降"
assert all(a >= b - 1e-9 for a, b in zip(flex_train, flex_train[1:])), "訓練 MSE 不是單調下降"
assert np.argmin(flex_test) not in (0, len(DFS) - 1), "測試 MSE 的最低點應該落在中間（U 型）"
print(f"KNN：Bayes 錯誤率 = {bayes_err:.4f}；"
      + "；".join(f"K={k} 訓練 {kerr[str(k)]['train']:.4f} / 測試 {kerr[str(k)]['test']:.4f}"
                  for k in KSHOW), file=e)
assert kerr["1"]["train"] == 0.0, "K = 1 的訓練錯誤率必須是 0"
assert kerr["10"]["test"] < kerr["1"]["test"], "K=10 應該比 K=1 好"
assert kerr["10"]["test"] < kerr["100"]["test"], "K=10 應該比 K=100 好"
assert min(ktest) >= bayes_err, "任何 K 的測試錯誤率都不該低於 Bayes 錯誤率"
assert ktrain[0] == 0.0 and ktest[0] > bayes_err, "圖 2.17 的左端應該是訓練 0、測試偏高"
print(f"1/K 曲線：測試錯誤率最低在 K = {best_k}（{min(ktest):.4f}）；"
      f"K=150 測試 {ktest[-1]:.4f}；Bayes 邊界線段 {len(segs)} 段", file=e)
print(f"訓練錯誤率 {ktrain}", file=e)
print(f"測試錯誤率 {ktest}", file=e)
print("全部檢查通過。", file=e)
