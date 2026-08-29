#!/usr/bin/env python3
"""產生 support_vector_machines.html 需要的烘焙資料（FRAMES_w10*）。

只有「JS 重寫不划算」或「要對上 lab 實跑數字」的圖才在這裡烘焙：
軟邊界是一個二次規劃（QP），RBF 的決策邊界要在格點上逐點算 decision_function，
兩者都不該用 50 行 JS 重寫。超平面、最大邊界（凸包最近點對）、hinge loss、
OVO／OVA 的投票規則都有閉式解，一律在前端 live 算，不在這裡。

關鍵設計：**重播 Ch09-svm-lab-zh.ipynb 的隨機數序列**。
lab 從 np.random.default_rng(1) 依序抽 50×2（儲存格 14）、20×2（儲存格 35）、
200×2（儲存格 57），所以只要照同樣順序抽，就能拿到與老師實跑完全相同的資料，
烘焙出來的支持向量個數／係數／最佳參數都能逐字對回 lab 的輸出。
檔尾的「檢查」行把這些對照印到 stderr。

跑法（用 pinned 環境，數字才可重現）：
  conda run -n m524 python tools/frames/gen_svm.py > /tmp/w10.js

輸出是可以直接貼進頁面的 JS literal。
"""
import json
import sys

import numpy as np
import sklearn.model_selection as skm
from sklearn.datasets import make_circles
from sklearn.svm import SVC

VERSIONS = "numpy {} · pandas {} · scikit-learn {}".format(
    np.__version__, __import__("pandas").__version__, __import__("sklearn").__version__)
GEN = "tools/frames/gen_svm.py"
LAB = "Ch09-svm-lab-zh.ipynb"
NGRID = 40                      # 決策區域的格點解析度（前端用 <rect> 填色）

# ── 重播 lab 的隨機數序列 ────────────────────────────────────────────────
rng = np.random.default_rng(1)
X50 = rng.standard_normal((50, 2))          # 儲存格 14
y50 = np.array([-1] * 25 + [1] * 25)
X50[y50 == 1] += 1
X20 = rng.standard_normal((20, 2))          # 儲存格 35（測試集，只用來算錯誤率）
y20 = np.array([-1] * 10 + [1] * 10)
X20[y20 == 1] += 1
X50s = X50.copy()                           # 儲存格 41：X[y==1] += 1.9 → 剛好可分開
X50s[y50 == 1] += 1.9
X200 = rng.standard_normal((200, 2))        # 儲存格 57
X200[:100] += 2
X200[100:150] -= 2
y200 = np.array([1] * 150 + [2] * 50)


def rd(v, d=4):
    return round(float(v), d)


def pts(X, y):
    """[[x1, x2, y], …]，前端直接畫點用。"""
    return [[rd(a, 3), rd(b, 3), int(c)] for (a, b), c in zip(X, y)]


def bounds(X, pad=0.6):
    return [rd(X[:, 0].min() - pad, 2), rd(X[:, 0].max() + pad, 2),
            rd(X[:, 1].min() - pad, 2), rd(X[:, 1].max() + pad, 2)]


def sign_rows(model, bb, n=NGRID):
    """把決策函數的正負號烘成 n 列字串（由上而下），每列 n 個 '0'/'1'。

    存符號而不存 decision_function 的值：前端只要填色，字串比浮點陣列小十幾倍。
    """
    x0, x1, y0, y1 = bb
    xs = np.linspace(x0, x1, n)
    rows = []
    for yv in np.linspace(y1, y0, n):
        d = model.decision_function(np.column_stack([xs, np.full(n, yv)]))
        rows.append("".join("1" if v > 0 else "0" for v in d))
    return rows


def linear_fit(X, y, C):
    """線性 SVC 的一次配適 → 頁面畫邊界與 margin 帶需要的每一個數。"""
    m = SVC(C=C, kernel="linear").fit(X, y)
    b1, b2 = m.coef_[0]
    b0 = float(m.intercept_[0])
    nrm = float(np.hypot(b1, b2))
    f = m.decision_function(X)
    yf = np.where(y == m.classes_[1], 1, -1) * f
    return {
        "C": C, "b0": rd(b0, 5), "b1": rd(b1, 5), "b2": rd(b2, 5),
        "margin": rd(1.0 / nrm, 4),                       # 半寬 1/‖β‖
        "nsv": int(m.support_.size),
        "nsvEach": [int(v) for v in m.n_support_],
        "sv": [int(i) for i in m.support_],
        "nViol": int(np.sum(yf < 1 - 1e-9)),               # 違反 margin
        "nWrong": int(np.sum(yf < 0)),                     # 落在超平面錯的一側
    }


# ── 1. 軟邊界：sklearn 的 C 掃過幾個值（ISLP 圖 9.7）──────────────────────
SOFT_C_NONSEP = [0.001, 0.01, 0.1, 1, 10, 100]
SOFT_C_SEP = [0.01, 0.1, 1, 10, 1000, 100000]
soft = {
    "nonsep": {"pts": pts(X50, y50), "bb": bounds(X50),
               "fits": [linear_fit(X50, y50, C) for C in SOFT_C_NONSEP]},
    "sep": {"pts": pts(X50s, y50), "bb": bounds(X50s),
            "fits": [linear_fit(X50s, y50, C) for C in SOFT_C_SEP]},
}

# ── 2. 交叉驗證選 C（lab 儲存格 31／33）──────────────────────────────────
CV_C = [0.001, 0.01, 0.1, 1, 5, 10, 100]
kfold = skm.KFold(5, random_state=0, shuffle=True)
gridC = skm.GridSearchCV(SVC(C=10, kernel="linear"), {"C": CV_C},
                         refit=True, cv=kfold, scoring="accuracy").fit(X50, y50)
cv_acc = [rd(v, 4) for v in gridC.cv_results_["mean_test_score"]]
best_C = float(gridC.best_params_["C"])

# ── 3. RBF：γ 與 C 的幾組組合（ISLP 圖 9.9）───────────────────────────────
Xtr, Xte, ytr, yte = skm.train_test_split(X200, y200, test_size=0.5, random_state=0)
RBF_BB = bounds(X200, pad=0.8)
RBF_CFG = [                                  # (C, gamma, 這一組在 lab 的出處)
    (1, 0.5, "γ 比較；儲存格 67 交叉驗證選出的最佳組合"),
    (1, 1, "γ／C 比較的共同基準；儲存格 61"),
    (1, 50, "γ 比較；儲存格 75 的 svm_flex"),
    (0.1, 1, "C 比較；固定 γ=1 的額外可重現配適"),
    (100000, 1, "C 比較；儲存格 65"),
]
rbf_frames = []
for C, g, why in RBF_CFG:
    m = SVC(kernel="rbf", C=C, gamma=g).fit(Xtr, ytr)
    rbf_frames.append({
        "C": C, "gamma": g, "why": why,
        "nsv": int(m.support_.size),
        "trainErr": rd(1 - m.score(Xtr, ytr), 4),
        "testErr": rd(1 - m.score(Xte, yte), 4),
        "rows": sign_rows(m, RBF_BB),
    })

RBF_GAMMAS = [0.25, 0.5, 1, 2, 3, 4, 10, 25, 50]
rbf_curve = {"gammas": RBF_GAMMAS, "trainErr": [], "testErr": [], "nsv": []}
for g in RBF_GAMMAS:
    m = SVC(kernel="rbf", C=1, gamma=g).fit(Xtr, ytr)
    rbf_curve["trainErr"].append(rd(1 - m.score(Xtr, ytr), 4))
    rbf_curve["testErr"].append(rd(1 - m.score(Xte, yte), 4))
    rbf_curve["nsv"].append(int(m.support_.size))

gridRBF = skm.GridSearchCV(SVC(kernel="rbf", gamma=1, C=1),
                           {"C": [0.1, 1, 10, 100, 1000], "gamma": [0.5, 1, 2, 3, 4]},
                           refit=True, cv=kfold, scoring="accuracy").fit(Xtr, ytr)
rbf_best = {"C": float(gridRBF.best_params_["C"]),
            "gamma": float(gridRBF.best_params_["gamma"])}

# ── 4. 核技巧：同心圓 + 二次映射（lab 儲存格 51–54）───────────────────────
Xc, yc = make_circles(100, factor=.1, noise=.1, random_state=0)


def feature_map_1(X):
    return np.asarray((np.sqrt(2) * X[:, 0] * X[:, 1], X[:, 0] ** 2, X[:, 1] ** 2)).T


def my_kernel_1(X, Y):
    return np.dot(feature_map_1(X), feature_map_1(Y).T)


Zc = feature_map_1(Xc)
clf_lin3 = SVC(C=1, kernel="linear").fit(Zc, yc)          # 在三維的 Z 空間配線性超平面
clf_ker = SVC(kernel=my_kernel_1).fit(Xc, yc)             # 同一件事，只用核
KERN_BB = bounds(Xc, pad=0.4)
kern = {
    "pts": pts(Xc, yc),
    "bb": KERN_BB,
    "w": [rd(v, 6) for v in clf_lin3.coef_.flatten()],
    "b": rd(clf_lin3.intercept_.flatten()[0], 6),
    "accKernel": rd(clf_ker.score(Xc, yc), 4),
    "accFeatureMap": rd(clf_lin3.score(Zc, yc), 4),
    "nsv": int(clf_ker.support_.size),
    "rows": sign_rows(clf_ker, KERN_BB),
    # 側欄要顯示「半徑」的分佈：兩類在 x₁²+x₂² 上完全分開，一維就夠
    "r2": {"inner": [rd(v, 4) for v in np.sort((Xc[yc == 1] ** 2).sum(1))[[0, -1]]],
           "outer": [rd(v, 4) for v in np.sort((Xc[yc == 0] ** 2).sum(1))[[0, -1]]]},
}

# ── 輸出 ────────────────────────────────────────────────────────────────
def js(name, obj, src, seed, note=""):
    meta = {"src": src, "seed": seed, "versions": VERSIONS, "gen": GEN}
    if note:
        meta["note"] = note
    return (f"const {name} = " + json.dumps({"meta": meta, **obj},
                                            ensure_ascii=False, separators=(",", ":")) + ";")


out = [
    js("FRAMES_w10soft", {"csNonsep": SOFT_C_NONSEP, "csSep": SOFT_C_SEP, **soft},
       f"{LAB} 儲存格 14（不可分開）與 41（剛好可分開），SVC(kernel='linear')",
       "np.random.default_rng(1)，重播 lab 的抽樣順序",
       f"C=10 有 {soft['nonsep']['fits'][4]['nsv']} 個支持向量（lab 儲存格 22／23）、"
       f"C=0.1 是 {soft['nonsep']['fits'][2]['nsvEach']}（儲存格 27）；"
       f"可分開的資料 C=1e5 用 {soft['sep']['fits'][5]['nsv']} 個、"
       f"C=0.1 用 {soft['sep']['fits'][1]['nsv']} 個（ISLP §9.6.1 的 3 與 12）"),
    js("FRAMES_w10cvc", {"cs": CV_C, "acc": cv_acc, "best": best_C},
       f"{LAB} 儲存格 31／33（GridSearchCV 選 C）",
       "KFold(5, shuffle=True, random_state=0)",
       f"mean_test_score = {cv_acc}，最佳 C = {best_C}（與 lab 逐字相符）"),
    js("FRAMES_w10rbf", {"bb": RBF_BB, "n": NGRID,
                         "trainPts": pts(Xtr, ytr), "frames": rbf_frames,
                         "gammaFrames": [0, 1, 2], "cFrames": [3, 1, 4],
                         "curve": rbf_curve, "best": rbf_best},
       f"{LAB} 儲存格 57／61／65／67／75，SVC(kernel='rbf')",
       "train_test_split(test_size=0.5, random_state=0)",
       f"交叉驗證最佳組合 C={rbf_best['C']}、gamma={rbf_best['gamma']}（lab 儲存格 67）；"
       f"決策區域是 {NGRID}×{NGRID} 格點上 decision_function 的正負號"),
    js("FRAMES_w10kern", {"n": NGRID, **kern},
       f"{LAB} 儲存格 51–54，make_circles(100, factor=.1, noise=.1, random_state=0)",
       "random_state=0",
       f"Z 空間的線性超平面 w={kern['w']}、b={kern['b']}（lab 儲存格 52 逐字相符）"),
]
print("\n".join(out))

# ── 檢查：每一個數字都要對得回 lab 的實跑輸出 ────────────────────────────
f = soft["nonsep"]["fits"]
fs = soft["sep"]["fits"]
print("\n/* 檢查（左邊是本檔算的，括號是 lab 實跑）：\n"
      f"   不可分開 C=10  支持向量 {f[4]['nsv']} / 各類 {f[4]['nsvEach']}"
      "  （儲存格 22：29 個、儲存格 23：[15 14]）\n"
      f"   不可分開 C=0.1 各類 {f[2]['nsvEach']}  （儲存格 27：[18 18]）\n"
      f"   coef_ = [{f[4]['b1']}, {f[4]['b2']}]  （儲存格 29：[1.17303943 0.77348227]）\n"
      f"   GridSearchCV best C = {best_C}  （儲存格 31：1）\n"
      f"   mean_test_score = {cv_acc}  （儲存格 33：[0.46 0.46 0.72 0.74 0.74 0.74 0.74]）\n"
      f"   可分開 C=1e5 支持向量 {fs[5]['nsv']}、C=0.1 支持向量 {fs[1]['nsv']}"
      "  （ISLP §9.6.1：three 與 twelve）\n"
      f"   RBF 最佳 {rbf_best}  （儲存格 67：{{'C': 1, 'gamma': 0.5}}）\n"
      f"   核映射 w={kern['w']} b={kern['b']}"
      "  （儲存格 52：w= [-0.05481854 -2.53191791 -2.52028513] b= [1.14976292]）\n"
      f"   核映射訓練準確率 {kern['accKernel']} / {kern['accFeatureMap']}"
      "  （儲存格 53：1.0 與 1.0）\n"
      f"   RBF γ=1,C=1 訓練錯誤 {rbf_frames[1]['trainErr']}、測試錯誤 {rbf_frames[1]['testErr']}\n"
      f"   RBF 最佳組合的測試錯誤 {rbf_frames[0]['testErr']}  （儲存格 69／70：12%）\n"
      "*/", file=sys.stderr)
