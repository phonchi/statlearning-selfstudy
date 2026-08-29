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

]
print("\n".join(out))

print("\n/* 檢查：表 4.1 β = ({:.4f}, {:.6f})　表 4.3 = {}\n"
      "   LDA@0.5 = {}　LDA@0.2 = {}　AUC(LDA) = {:.4f}\n"
      "   AUC 四方法 = {}\n"
      "   線性配適 <0 的區間 = balance < {:.0f}（資料最大 {:.0f}）*/".format(
          gb0, gb1, m3, cm50.tolist(), cm20.tolist(), auc_lda, aucs,
          zero_at, bal.max()), file=sys.stderr)
