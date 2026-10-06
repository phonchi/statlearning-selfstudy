#!/usr/bin/env python3
"""產生 classification.html 需要的烘焙資料（FRAMES_w04*）。

只有「要跟課本的圖或數字對到小數位」或「需要一整條曲線」的才在這裡產生；
凡是 lab notebook 裡已經有輸出的數字，頁面上一律逐字抄 lab，不在這裡重算。

兩組輸出資料都建在 ISLP 的 `Default`（n = 10000）上，因為 ISLP 第 4 章的
表 4.1／4.3／4.4／4.5 與圖 4.2／4.7／4.8 全部用這份資料，可以逐項對上：
  · 表 4.1 邏輯斯（balance）    β₀ = −10.6513、β₁ = 0.0055
  · 表 4.3 多元邏輯斯          −10.8690 / 0.0057 / 0.0030 / −0.6468
  · 表 4.4 LDA 閾值 0.5        9644 / 23 / 252 / 81，錯誤率 2.75%
  · 表 4.5 LDA 閾值 0.2        9432 / 235 / 138 / 195，錯誤率 3.73%
  · 圖 4.8 LDA 的 AUC          0.95

跑法（用 pinned 環境，數字才可重現）：
  conda run -n m524 python tools/frames/gen_classification.py > /tmp/w04.js

輸出是可以直接貼進頁面的 JS literal（stdout 只有 JS，檢查訊息走 stderr）。
"""
import json
import sys

import numpy as np
import statsmodels.api as sm
from ISLP import load_data
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis as QDA
from sklearn.metrics import auc, confusion_matrix, roc_curve
from sklearn.naive_bayes import GaussianNB

VERSIONS = "numpy {} · pandas {} · scikit-learn {} · statsmodels {}".format(
    np.__version__, __import__("pandas").__version__,
    __import__("sklearn").__version__, sm.__version__)
GEN = "tools/frames/gen_classification.py"
SEED = 20260810
NBINS = 200                      # 閾值滑桿的格子寬度 = 1/200 = 0.005

# ── 載入 Default ────────────────────────────────────────────────────────
D = load_data("Default")
y = (D["default"] == "Yes").astype(int).to_numpy()
bal = D["balance"].to_numpy(dtype=float)
inc = D["income"].to_numpy(dtype=float)
stu = (D["student"] == "Yes").astype(int).to_numpy()
N = len(y)
NPOS, NNEG = int(y.sum()), int((1 - y).sum())

# ── 1. 為什麼不用線性迴歸（ISLP 圖 4.2）────────────────────────────────
X1 = sm.add_constant(bal)
logit1 = sm.GLM(y, X1, family=sm.families.Binomial()).fit()
ols1 = sm.OLS(y, X1).fit()
lb0, lb1 = float(ols1.params[0]), float(ols1.params[1])
gb0, gb1 = float(logit1.params[0]), float(logit1.params[1])
zero_at = -lb0 / lb1                                  # 線性配適穿過 0 的 balance
one_at = (1.0 - lb0) / lb1                            # 線性配適穿過 1 的 balance

assert abs(gb0 + 10.6513) < 5e-4, f"表 4.1 的 β₀ 對不上：{gb0}"
assert abs(gb1 - 0.0055) < 5e-5, f"表 4.1 的 β₁ 對不上：{gb1}"

# 給 SVG 的 rug：分層抽樣，兩類都看得到（固定種子）
rng = np.random.default_rng(SEED)
idx_pos = rng.choice(np.flatnonzero(y == 1), size=70, replace=False)
idx_neg = rng.choice(np.flatnonzero(y == 0), size=170, replace=False)
pts = [[int(round(bal[i])), int(y[i])] for i in np.sort(np.concatenate([idx_pos, idx_neg]))]

# 表 4.3 的多元邏輯斯（頁面上引用，順便驗證）
X3 = sm.add_constant(np.column_stack([bal, inc / 1000.0, stu]))
logit3 = sm.GLM(y, X3, family=sm.families.Binomial()).fit()
m3 = [round(float(v), 6) for v in logit3.params]
assert abs(m3[3] + 0.6468) < 5e-4, f"表 4.3 的 student[Yes] 對不上：{m3}"

# ── 2. 閾值 / 混淆矩陣 / ROC：LDA on (balance, student)（ISLP 表 4.4–4.5）─
XL = np.column_stack([bal, stu])
lda = LDA().fit(XL, y)
p_lda = lda.predict_proba(XL)[:, 1]

cm50 = confusion_matrix(y, (p_lda > 0.5).astype(int))   # [[TN, FP], [FN, TP]]
cm20 = confusion_matrix(y, (p_lda > 0.2).astype(int))
assert cm50.tolist() == [[9644, 23], [252, 81]], f"表 4.4 對不上：{cm50.tolist()}"
assert cm20.tolist() == [[9432, 235], [138, 195]], f"表 4.5 對不上：{cm20.tolist()}"

# 直方圖：bin j 收 p ∈ [j/200, (j+1)/200)。閾值只走 0.005 的倍數，
# 所以「bin ≥ k 的總數」＝「p > k/200 的總數」，是精確的，不是近似。
bidx = np.clip((p_lda * NBINS).astype(int), 0, NBINS - 1)
hist_yes = np.bincount(bidx[y == 1], minlength=NBINS).tolist()
hist_no = np.bincount(bidx[y == 0], minlength=NBINS).tolist()


def cm_from_hist(k):
    """從直方圖累加回推 (TN, FP, FN, TP)，k 是 bin 起點（閾值 = k/200）。"""
    tp = int(sum(hist_yes[k:]))
    fp = int(sum(hist_no[k:]))
    return NNEG - fp, fp, NPOS - tp, tp


for t, want in ((0.5, cm50), (0.2, cm20)):
    got = cm_from_hist(int(round(t * NBINS)))
    exp = (int(want[0, 0]), int(want[0, 1]), int(want[1, 0]), int(want[1, 1]))
    assert got == exp, f"閾值 {t} 的直方圖累加不精確：{got} ≠ {exp}"

fpr_l, tpr_l, _ = roc_curve(y, p_lda)
auc_lda = float(auc(fpr_l, tpr_l))
assert round(auc_lda, 2) == 0.95, f"圖 4.8 的 AUC 對不上：{auc_lda}"

# ── 3. 四方法 ROC 自我檢查（不輸出；同一組預測變數才比得公平）──────────
logit_l = sm.GLM(y, sm.add_constant(XL), family=sm.families.Binomial()).fit()
models = {
    "logit": logit_l.predict(sm.add_constant(XL)),
    "lda": p_lda,
    "qda": QDA().fit(XL, y).predict_proba(XL)[:, 1],
    "nb": GaussianNB().fit(XL, y).predict_proba(XL)[:, 1],
}


def thin(fpr, tpr, m=48):
    """沿曲線等距取 m 個點，頭尾一定留著。"""
    keep = np.unique(np.linspace(0, len(fpr) - 1, min(m, len(fpr))).astype(int))
    return [[round(float(fpr[i]), 5), round(float(tpr[i]), 5)] for i in keep]


curves, aucs, cms = {}, {}, {}
for name, pr in models.items():
    f, t, _ = roc_curve(y, pr)
    curves[name] = thin(f, t)
    aucs[name] = round(float(auc(f, t)), 4)
    c = confusion_matrix(y, (pr > 0.5).astype(int))
    cms[name] = [int(c[0, 0]), int(c[0, 1]), int(c[1, 0]), int(c[1, 1])]



# ── 4. ISLP §4.5.2 六個模擬情境（示意重現；書上未給的參數在 SCEN_NOTE 標明）──
from scipy import stats as _st  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.model_selection import GridSearchCV, StratifiedKFold  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier  # noqa: E402

SCEN_SEED = 20261006
SCEN_REPS = 100
SCEN_NTEST = 2000                       # 每類測試點數
SCEN_MU = np.array([1.0, 1.0])          # 第 2 類平均；第 1 類在原點
SCEN_NOTE = ("ISLP 只描述各情境的分布、相關與每類筆數；平均差 (1,1)、t 分布自由度 3、"
             "情境 4 與 5 每類筆數、情境 5 的非線性函數、情境 6 的對角變異數，以及測試集大小，"
             "都是本頁為了示意自選的設定。因此只比較方法的相對排序，不對照書上的錯誤率數字。")
R_NEG = np.array([[1.0, -0.5], [-0.5, 1.0]])
R_POS = np.array([[1.0, 0.5], [0.5, 1.0]])


def _mvn(rng, mu, cov, n):
    return rng.multivariate_normal(mu, cov, size=n)


def _mvt(rng, mu, shape, n, df=3):
    return _st.multivariate_t(loc=mu, shape=shape, df=df).rvs(size=n, random_state=rng).reshape(n, 2)


def _two_class(rng, gen1, gen2, n1, n2):
    X = np.vstack([gen1(rng, n1), gen2(rng, n2)])
    return X, np.r_[np.zeros(n1, int), np.ones(n2, int)]


def _scen5_eta(X):
    return 2 * (X[:, 0] + X[:, 1]) + np.where(X[:, 0] * X[:, 1] > 0, 1.5, -1.5) + 0.8 * X[:, 0] ** 2


def _scen5(rng, n):
    X = rng.standard_normal((n, 2))
    y = (rng.random(n) < 1 / (1 + np.exp(-_scen5_eta(X)))).astype(int)
    return X, y


I2 = np.eye(2)
S6A, S6B = np.diag([1.0, 4.0]), np.diag([4.0, 1.0])
SCENARIOS = [
    ("情境 1", lambda r, n: _two_class(r, lambda g, m: _mvn(g, [0, 0], I2, m),
                                       lambda g, m: _mvn(g, SCEN_MU, I2, m), n, n), 20, True),
    ("情境 2", lambda r, n: _two_class(r, lambda g, m: _mvn(g, [0, 0], R_NEG, m),
                                       lambda g, m: _mvn(g, SCEN_MU, R_NEG, m), n, n), 20, True),
    ("情境 3", lambda r, n: _two_class(r, lambda g, m: _mvt(g, [0, 0], R_NEG, m),
                                       lambda g, m: _mvt(g, SCEN_MU, R_NEG, m), n, n), 50, True),
    ("情境 4", lambda r, n: _two_class(r, lambda g, m: _mvn(g, [0, 0], R_POS, m),
                                       lambda g, m: _mvn(g, SCEN_MU, R_NEG, m), n, n), 50, False),
    ("情境 5", lambda r, n: _scen5(r, 2 * n), 50, False),
    ("情境 6", lambda r, n: _two_class(r, lambda g, m: _mvn(g, [0, 0], S6A, m),
                                       lambda g, m: _mvn(g, [0.5, 0.5], S6B, m), n, n), 6, False),
]
SCEN_METHODS = ["KNN-1", "KNN-CV", "LDA", "Logistic", "NBayes", "QDA"]


def _fit_predict(name, Xtr, ytr, Xte):
    if name == "KNN-1":
        m = KNeighborsClassifier(n_neighbors=1)
    elif name == "KNN-CV":
        kmax = max(1, min(15, int(min(np.bincount(ytr)) * 4 / 5 * 2) - 1))
        cv = StratifiedKFold(n_splits=min(5, int(min(np.bincount(ytr)))), shuffle=True, random_state=0)
        m = GridSearchCV(KNeighborsClassifier(), {"n_neighbors": list(range(1, kmax + 1))}, cv=cv)
    elif name == "LDA":
        m = LDA()
    elif name == "Logistic":
        m = LogisticRegression(C=1e6, max_iter=5000)
    elif name == "NBayes":
        m = GaussianNB()
    else:
        m = QDA(reg_param=1e-6)
    return m.fit(Xtr, ytr).predict(Xte)


scen_rows = []
for si, (label, gen, n_per, linear) in enumerate(SCENARIOS):
    srng = np.random.default_rng(SCEN_SEED + si)
    errs = {mname: [] for mname in SCEN_METHODS}
    for _ in range(SCEN_REPS):
        while True:
            Xtr, ytr = gen(srng, n_per)
            if min(np.bincount(ytr, minlength=2)) >= 3:
                break
        Xte, yte = gen(srng, SCEN_NTEST)
        for mname in SCEN_METHODS:
            errs[mname].append(float(np.mean(_fit_predict(mname, Xtr, ytr, Xte) != yte)))
    box = {}
    for mname, v in errs.items():
        q = np.quantile(v, [0, 0.25, 0.5, 0.75, 1.0])
        box[mname] = [round(float(t), 4) for t in q]
    n_text = f"共 {2 * n_per} 筆，各類筆數隨機" if label == "情境 5" else f"每類 {n_per} 筆"
    scen_rows.append({"label": label, "nPerClass": n_per, "nText": n_text, "linear": linear, "box": box})

# ── 輸出 ────────────────────────────────────────────────────────────────
def js(name, obj, src, seed, note=""):
    meta = {"src": src, "seed": seed, "versions": VERSIONS, "gen": GEN}
    if note:
        meta["note"] = note
    return (f"const {name} = " + json.dumps({"meta": meta, **obj},
                                            ensure_ascii=False, separators=(",", ":")) + ";")


out = [
    js("FRAMES_w04why",
       {"n": N, "rate": round(float(y.mean()), 4),
        "lin": {"b0": round(lb0, 7), "b1": round(lb1, 9)},
        "logit": {"b0": round(gb0, 5), "b1": round(gb1, 8)},
        "multi": {"b0": m3[0], "balance": m3[1], "income": m3[2], "student": m3[3]},
        "zeroAt": round(float(zero_at), 1), "oneAt": round(float(one_at), 1),
        "balMax": round(float(bal.max()), 1), "pts": pts},
       "ISLP Default（ISLP 圖 4.2、表 4.1、表 4.3）",
       f"rug 用 np.random.default_rng({SEED}) 分層抽 70 + 170 筆",
       f"邏輯斯係數 {round(gb0, 4)} / {round(gb1, 4)} 與 ISLP 表 4.1 的 −10.6513 / 0.0055 相符；"
       f"線性配適在 balance < {zero_at:.0f} 會給負機率，要到 balance ≈ {one_at:.0f} 才超過 1，"
       f"已經在資料範圍（最大 {bal.max():.0f}）之外"),

    js("FRAMES_w04thr",
       {"n": N, "nPos": NPOS, "nNeg": NNEG, "nbins": NBINS, "step": 1.0 / NBINS,
        "histYes": hist_yes, "histNo": hist_no,
        "auc": round(auc_lda, 4),
        "ref": {"t50": [int(cm50[0, 0]), int(cm50[0, 1]), int(cm50[1, 0]), int(cm50[1, 1])],
                "t20": [int(cm20[0, 0]), int(cm20[0, 1]), int(cm20[1, 0]), int(cm20[1, 1])]}},
       "ISLP Default · LDA(balance, student)（ISLP 表 4.4、表 4.5、圖 4.7、圖 4.8）",
       "無隨機性：LDA 是閉式解，直方圖是全部 10000 筆的後驗機率",
       "直方圖每格寬 0.005，閾值只走 0.005 的倍數，所以 JS 累加出來的 2×2 表是精確值："
       "閾值 0.5 得 9644/23/252/81（表 4.4）、閾值 0.2 得 9432/235/138/195（表 4.5）"),

    js("FRAMES_w04scen",
       {"reps": SCEN_REPS, "nTestPerClass": SCEN_NTEST, "methods": SCEN_METHODS, "rows": scen_rows},
       "依 ISLP §4.5.2 六情境的文字描述自行模擬（示意，非書上原始資料）",
       f"np.random.default_rng({SCEN_SEED}+情境序號)，每情境 {SCEN_REPS} 組訓練集",
       SCEN_NOTE),
]
print("\n".join(out))

print("\n/* 檢查：表 4.1 β = ({:.4f}, {:.6f})　表 4.3 = {}\n"
      "   LDA@0.5 = {}　LDA@0.2 = {}　AUC(LDA) = {:.4f}\n"
      "   AUC 四方法 = {}\n"
      "   線性配適 <0 的區間 = balance < {:.0f}（資料最大 {:.0f}）*/".format(
          gb0, gb1, m3, cm50.tolist(), cm20.tolist(), auc_lda, aucs,
          zero_at, bal.max()), file=sys.stderr)
