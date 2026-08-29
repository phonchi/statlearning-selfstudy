#!/usr/bin/env python3
"""產生 tree_based_methods.html 需要的烘焙資料（FRAMES_w09*）。

只有三件事在這裡算：
  1. 剪枝路徑（訓練／CV／測試誤差 vs 葉子數）——需要 sklearn 的
     cost_complexity_pruning_path，50 行 JS 寫不出來。
  2. Random Forest 的 m 效應與「樹之間的相關」——需要真的長森林。
  3. 變數重要度（不純度下降 vs permutation）——同上。

其餘元件（樹的生長、不純度曲線、投票、bagging 抽樣、梯度提升、AdaBoost）
都是機制本身，在 JS 裡即時算，不在這裡烘焙。

凡是 lab notebook 已經有輸出的數字，頁面上一律逐字抄 lab，這裡只用來對照。

跑法（用 pinned 環境，數字才可重現）：
  conda run -n m524 python tools/frames/gen_trees.py > /tmp/w09.js
"""
import json
import sys

import numpy as np
import pandas as pd
from ISLP import load_data
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import KFold, train_test_split
from sklearn.tree import DecisionTreeRegressor

VERSIONS = "numpy {} · pandas {} · scikit-learn {}".format(
    np.__version__, pd.__version__, __import__("sklearn").__version__)
GEN = "tools/frames/gen_trees.py"


def mse(a, b):
    return float(np.mean((np.asarray(a) - np.asarray(b)) ** 2))


# ══════════════════════════════════════════════════════════════════════
# 1. 剪枝路徑：Hitters（ISLP §8.1.1、圖 8.5）
#    照課本：去掉 Salary 缺失、log(Salary)、132 訓練／131 測試、六折 CV。
# ══════════════════════════════════════════════════════════════════════
HIT_FEATS = ["Years", "Hits", "RBI", "Walks", "Runs", "PutOuts",
             "AtBat", "HmRun", "Assists"]                    # 課本說「用了九個特徵」

Hitters = load_data("Hitters").dropna(subset=["Salary"])
Xh = np.asarray(Hitters[HIT_FEATS], dtype=float)
yh = np.log(np.asarray(Hitters["Salary"], dtype=float))
Xh_tr, Xh_te, yh_tr, yh_te = train_test_split(Xh, yh, train_size=132, random_state=8)

full = DecisionTreeRegressor(random_state=0, min_samples_leaf=5).fit(Xh_tr, yh_tr)
path = full.cost_complexity_pruning_path(Xh_tr, yh_tr)
kf6 = KFold(n_splits=6, shuffle=True, random_state=8)        # 132 = 6 × 22

rows = {}
for a in path.ccp_alphas:
    t = DecisionTreeRegressor(random_state=0, min_samples_leaf=5, ccp_alpha=a).fit(Xh_tr, yh_tr)
    leaves = int(t.tree_.n_leaves)
    if leaves < 1 or leaves > 12 or leaves in rows:           # 圖 8.5 只畫到 |T| = 10 附近
        continue
    tr = mse(yh_tr, t.predict(Xh_tr))
    te = mse(yh_te, t.predict(Xh_te))
    cv_parts = []
    for itr, ite in kf6.split(Xh_tr):
        m = DecisionTreeRegressor(random_state=0, min_samples_leaf=5,
                                  ccp_alpha=a).fit(Xh_tr[itr], yh_tr[itr])
        cv_parts.append(mse(yh_tr[ite], m.predict(Xh_tr[ite])))
    rows[leaves] = {"alpha": float(a), "train": tr, "cv": float(np.mean(cv_parts)),
                    "cvSe": float(np.std(cv_parts, ddof=1) / np.sqrt(6)), "test": te}

leaf_list = sorted(rows)
prune = {
    "leaves": leaf_list,
    "alpha": [round(rows[k]["alpha"], 5) for k in leaf_list],
    "train": [round(rows[k]["train"], 4) for k in leaf_list],
    "cv": [round(rows[k]["cv"], 4) for k in leaf_list],
    "cvSe": [round(rows[k]["cvSe"], 4) for k in leaf_list],
    "test": [round(rows[k]["test"], 4) for k in leaf_list],
    "nTrain": int(len(yh_tr)), "nTest": int(len(yh_te)), "p": len(HIT_FEATS),
}
prune["cvBest"] = int(leaf_list[int(np.argmin(prune["cv"]))])
prune["testBest"] = int(leaf_list[int(np.argmin(prune["test"]))])


# ══════════════════════════════════════════════════════════════════════
# 2. Random Forest 的 m：測試誤差 vs 樹的棵數 ＋ 樹之間的平均相關
#    (a) Boston（lab 儲存格 64–70 的同一份切分）
#    (b) 模擬：1 個強變數 ＋ 30 個彼此相關的中等變數（ISLP §8.2.2 描述的情境）
# ══════════════════════════════════════════════════════════════════════
B_GRID = list(range(1, 21)) + [25, 30, 40, 50, 60, 80, 100, 125, 150, 175,
                              200, 225, 250, 275, 300]     # 35 個點，夠看收斂


def rf_curve(Xtr, ytr, Xte, yte, m, n_trees=300, seed=0):
    """回傳 (每個 B 的測試 MSE, 樹與樹之間的平均相關)。

    B 的曲線是「前 B 棵樹的平均預測」，跟 RandomForest 的定義一致。
    """
    rf = RandomForestRegressor(n_estimators=n_trees, max_features=m,
                               random_state=seed, n_jobs=-1).fit(Xtr, ytr)
    P = np.array([t.predict(Xte) for t in rf.estimators_])   # (n_trees, n_test)
    csum = np.cumsum(P, axis=0)
    curve = [round(mse(yte, csum[b - 1] / b), 4) for b in B_GRID]
    C = np.corrcoef(P[:60])                                   # 60 棵夠估平均相關
    rho = float((C.sum() - np.trace(C)) / (C.shape[0] * (C.shape[0] - 1)))
    return curve, round(rho, 4), round(float(np.mean(np.var(P, axis=0))), 4)


# (a) Boston：跟 lab 完全同一個切分（test_size=0.3, random_state=0）
Boston = load_data("Boston")
Xb = np.asarray(Boston.drop(columns=["medv"]), dtype=float)
yb = np.asarray(Boston["medv"], dtype=float)
Xb_tr, Xb_te, yb_tr, yb_te = train_test_split(Xb, yb, test_size=0.3, random_state=0)
P_BOSTON = Xb.shape[1]

boston_ms = [P_BOSTON, 6, 4, 2]
boston = {"p": P_BOSTON, "ms": boston_ms, "curves": [], "rho": [], "treeVar": [],
          "n": int(len(yb_tr)), "nTest": int(len(yb_te))}
for m in boston_ms:
    c, r, v = rf_curve(Xb_tr, yb_tr, Xb_te, yb_te, m)
    boston["curves"].append(c)
    boston["rho"].append(r)
    boston["treeVar"].append(v)

# 單一棵樹（剪枝後）的測試 MSE：lab 儲存格 59 是 28.07
single = DecisionTreeRegressor(max_depth=3, random_state=0).fit(Xb_tr, yb_tr)
boston["singleTree"] = round(mse(yb_te, single.predict(Xb_te)), 4)

# (b) 模擬：ISLP §8.2.2 描述的情境——一個很強的變數 ＋ 一堆中等強度且彼此相關的變數。
#     bagging 的每棵樹都會拿那個強變數當根節點，於是樹跟樹長得幾乎一樣。
rng = np.random.default_rng(524)
n_sim, p_sim = 400, 30
Z = rng.standard_normal((2 * n_sim, 1))                       # 共同因子 → 特徵彼此相關
Xs = 0.8 * Z + 0.6 * rng.standard_normal((2 * n_sim, p_sim))
beta = np.zeros(p_sim)
beta[0] = 2.0                                                 # 一個強變數
beta[1:21] = 0.9                                              # 20 個中等強度的變數
ys = Xs @ beta + rng.standard_normal(2 * n_sim) * 2.0
Xs_tr, Xs_te, ys_tr, ys_te = Xs[:n_sim], Xs[n_sim:], ys[:n_sim], ys[n_sim:]

sim_ms = [p_sim, 15, 5, 2]                                    # 5 ≈ √30
sim = {"p": p_sim, "ms": sim_ms, "curves": [], "rho": [], "treeVar": [],
       "n": n_sim, "nTest": n_sim,
       "xCorr": round(float(np.mean(np.abs(np.corrcoef(Xs.T)[np.triu_indices(p_sim, 1)]))), 3)}
for m in sim_ms:
    c, r, v = rf_curve(Xs_tr, ys_tr, Xs_te, ys_te, m)
    sim["curves"].append(c)
    sim["rho"].append(r)
    sim["treeVar"].append(v)
sim["singleTree"] = round(mse(ys_te, DecisionTreeRegressor(random_state=0)
                              .fit(Xs_tr, ys_tr).predict(Xs_te)), 4)


# ══════════════════════════════════════════════════════════════════════
# 3. 變數重要度：Boston 上的 RF（m = 6, random_state = 0）——就是 lab 儲存格 70／72
# ══════════════════════════════════════════════════════════════════════
rf6 = RandomForestRegressor(max_features=6, random_state=0, n_jobs=-1).fit(Xb_tr, yb_tr)
names = list(Boston.drop(columns=["medv"]).columns)
imp = rf6.feature_importances_
perm = permutation_importance(rf6, Xb_te, yb_te, n_repeats=30, random_state=0,
                              scoring="r2", n_jobs=-1)

order = np.argsort(-imp)
vimp = {
    "names": [names[i] for i in order],
    "impurity": [round(float(imp[i]), 6) for i in order],
    "permutation": [round(float(perm.importances_mean[i]), 4) for i in order],
    "permSd": [round(float(perm.importances_std[i]), 4) for i in order],
    "testMse": round(mse(yb_te, rf6.predict(Xb_te)), 4),
}


# ══════════════════════════════════════════════════════════════════════
def js(name, obj, src, seed, note=""):
    meta = {"src": src, "seed": seed, "versions": VERSIONS, "gen": GEN}
    if note:
        meta["note"] = note
    return (f"const {name} = " + json.dumps({"meta": meta, **obj},
                                            ensure_ascii=False, separators=(",", ":")) + ";")


print("\n".join([
    js("FRAMES_w09prune", prune,
       "ISLP Hitters（§8.1.1、圖 8.5 的設定：去掉 Salary 缺失、log Salary、九個特徵）",
       "train_test_split(train_size=132, random_state=8)；KFold(6, shuffle=True, random_state=8)",
       f"CV 最低在 {prune['cvBest']} 個葉子、測試最低在 {prune['testBest']} 個葉子；"
       "課本圖 8.5 的 CV 最低點是 3 個葉子。分割不同數字不會一樣，形狀才是重點。"),
    js("FRAMES_w09rf", {"B": B_GRID, "boston": boston, "sim": sim},
       "ISLP Boston（與 Ch08-baggboost-lab-zh.ipynb 儲存格 52 同一切分）＋ 一份標明是模擬的資料",
       "train_test_split(test_size=0.3, random_state=0)；RandomForestRegressor(random_state=0)；"
       "模擬用 np.random.default_rng(524)",
       f"Boston 上 m=p 的 B=100 測試 MSE = {boston['curves'][0][B_GRID.index(100)]}"
       f"（lab 儲存格 66 是 14.6347）、m=6 是 {boston['curves'][1][B_GRID.index(100)]}"
       f"（lab 儲存格 70 是 20.0428）"),
    js("FRAMES_w09vimp", vimp,
       "ISLP Boston · RandomForestRegressor(max_features=6, random_state=0)"
       "（＝lab 儲存格 70／72 的同一個模型；Heart 不在 ISLP 0.4.0 裡，所以改用 Boston）",
       "random_state=0；permutation_importance(scoring='r2', n_repeats=30, random_state=0)",
       f"不純度下降的第一名是 {vimp['names'][0]} = {vimp['impurity'][0]}"
       f"（lab 儲存格 72 是 lstat 0.356203）"),
]))

i100 = B_GRID.index(100)
print(f"""
/* ── 對照 lab 的錨點 ──────────────────────────────────────────────
   Boston 單一剪枝樹測試 MSE  自算 {boston['singleTree']}      lab 儲存格 59  28.0699
   Boston bagging (m=12,B=100) 自算 {boston['curves'][0][i100]}   lab 儲存格 66  14.6347
   Boston RF      (m=6, B=100) 自算 {boston['curves'][1][i100]}   lab 儲存格 70  20.0428
   Boston 重要度第一名          自算 {vimp['names'][0]} {vimp['impurity'][0]}   lab 儲存格 72  lstat 0.356203
   Hitters 剪枝 CV 最低葉子數   自算 {prune['cvBest']}          ISLP 圖 8.5  3
   樹間平均相關 ρ̄（Boston）      m=12 {boston['rho'][0]} → m=2 {boston['rho'][3]}
   樹間平均相關 ρ̄（模擬）        m=30 {sim['rho'][0]} → m=2 {sim['rho'][3]}
   模擬資料的特徵間平均 |相關|   {sim['xCorr']}
   ─────────────────────────────────────────────────────────────── */""",
      file=sys.stderr)
