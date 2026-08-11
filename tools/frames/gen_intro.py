#!/usr/bin/env python3
"""產生 introduction.html 需要的烘焙資料（FRAMES_w01*）。

只烘焙「要重現課本圖或要對到真實數字」的部分；課程地圖、預測vs推論分流器、
n×p 示意圖都是即時算的，不在這裡。

跑法：conda run -n m524 python tools/frames/gen_intro.py
"""
import json
import sys

import numpy as np
from ISLP import load_data
from sklearn.decomposition import PCA

VERSIONS = "numpy {} · pandas {} · scikit-learn {}".format(
    np.__version__, __import__("pandas").__version__, __import__("sklearn").__version__)
GEN = "tools/frames/gen_intro.py"
rng = np.random.default_rng(0)


def r(a, d=3):
    return [round(float(x), d) for x in np.asarray(a).ravel()]


# ── 1. Wage：ISLP 圖 1.1 的三個面板 ─────────────────────────────────────
Wage = load_data("Wage")
age = np.asarray(Wage["age"], dtype=float)
wage = np.asarray(Wage["wage"], dtype=float)
year = np.asarray(Wage["year"], dtype=float)

# 散佈圖只取 600 點（3000 點畫在 canvas 上是一團黑，也讓頁面變大）
idx = np.sort(rng.choice(len(age), 600, replace=False))
scatter = [[round(float(age[i]), 1), round(float(wage[i]), 2)] for i in idx]

# 年齡的分箱平均（就是圖 1.1 左的那條藍線）
bins = np.arange(18, 82, 4)
who = np.digitize(age, bins)
age_curve = []
for b in range(1, len(bins)):
    m = who == b
    if m.sum() >= 10:
        age_curve.append([round(float(age[m].mean()), 1), round(float(wage[m].mean()), 2),
                          int(m.sum())])

# 年份的平均與線性趨勢（圖 1.1 中）
yrs = sorted(set(year.astype(int).tolist()))
year_mean = [[int(y), round(float(wage[year == y].mean()), 2), int((year == y).sum())] for y in yrs]
slope, intercept = np.polyfit(year, wage, 1)

# 教育程度的分佈（圖 1.1 右的箱形圖，這裡給五數綜合）
edu_order = ["1. < HS Grad", "2. HS Grad", "3. Some College",
             "4. College Grad", "5. Advanced Degree"]
edu = Wage["education"].astype(str)
edu_box = []
for lab in edu_order:
    v = wage[np.asarray(edu == lab)]
    q = np.percentile(v, [5, 25, 50, 75, 95])
    edu_box.append({"label": lab.split(". ")[1], "n": int(len(v)),
                    "lo": round(float(q[0]), 1), "q1": round(float(q[1]), 1),
                    "med": round(float(q[2]), 1), "q3": round(float(q[3]), 1),
                    "hi": round(float(q[4]), 1), "mean": round(float(v.mean()), 2)})

# lab 儲存格 148 的實跑數字，頁面上要對得起來
wage_2004_mean = round(float(wage[year == 2004].mean()), 5)

# ── 2. Smarket：ISLP 圖 1.2——Lag 幾乎分不出漲跌 ────────────────────────
Smarket = load_data("Smarket")
direction = np.asarray(Smarket["Direction"].astype(str))
lag_box = []
for k in (1, 2, 3):
    col = np.asarray(Smarket[f"Lag{k}"], dtype=float)
    row = {"lag": k}
    for d in ("Down", "Up"):
        v = col[direction == d]
        q = np.percentile(v, [10, 25, 50, 75, 90])
        row[d] = {"n": int(len(v)), "lo": round(float(q[0]), 3), "q1": round(float(q[1]), 3),
                  "med": round(float(q[2]), 3), "q3": round(float(q[3]), 3),
                  "hi": round(float(q[4]), 3), "mean": round(float(v.mean()), 4)}
    lag_box.append(row)

# ── 3. NCI60：ISLP 圖 1.4——PC1/PC2 上癌症型別會分群 ────────────────────
NCI60 = load_data("NCI60")
X = np.asarray(NCI60["data"], dtype=float)
labels = [str(x) for x in np.asarray(NCI60["labels"]).ravel()]
Xs = (X - X.mean(0)) / np.where(X.std(0) == 0, 1, X.std(0))
Z = PCA(n_components=2, random_state=0).fit_transform(Xs)
pve = PCA(n_components=5, random_state=0).fit(Xs).explained_variance_ratio_
# 只標出樣本數 >= 5 的型別，其餘歸「其他」，不然圖例會爆
from collections import Counter  # noqa: E402
big = {k for k, v in Counter(labels).items() if v >= 5}
nci = [{"x": round(float(Z[i, 0]), 2), "y": round(float(Z[i, 1]), 2),
        "g": labels[i] if labels[i] in big else "其他"} for i in range(len(labels))]

# ── 4. 五個課程資料集的真實形狀 ────────────────────────────────────────
shapes = []
for name in ("Wage", "Smarket", "Auto", "Bikeshare", "Boston"):
    d = load_data(name)
    shapes.append({"name": name, "n": int(d.shape[0]), "p": int(d.shape[1])})
shapes.append({"name": "NCI60", "n": int(X.shape[0]), "p": int(X.shape[1])})


def js(name, obj, src, seed, note=""):
    meta = {"src": src, "seed": seed, "versions": VERSIONS, "gen": GEN}
    if note:
        meta["note"] = note
    return (f"const {name} = "
            + json.dumps({"meta": meta, **obj}, ensure_ascii=False, separators=(",", ":")) + ";")


print("\n".join([
    js("FRAMES_w01wage",
       {"scatter": scatter, "ageCurve": age_curve, "yearMean": year_mean,
        "trend": [round(float(intercept), 3), round(float(slope), 4)],
        "eduBox": edu_box, "n": int(len(age)), "mean2004": wage_2004_mean},
       "ISLP Wage（ISLP 圖 1.1）· Ch01-lab-zh.ipynb 儲存格 145–155",
       "np.random.default_rng(0) 抽 600 點畫散佈圖",
       f"2004 年的平均薪資 {wage_2004_mean}，與 lab 儲存格 148 的 "
       f"np.float64(111.15999687022256) 相符"),
    js("FRAMES_w01smarket", {"lagBox": lag_box, "n": int(len(direction)),
                             "nUp": int((direction == "Up").sum())},
       "ISLP Smarket（ISLP 圖 1.2）· Ch01-lab-zh.ipynb 儲存格 157–158", "無隨機性"),
    js("FRAMES_w01nci", {"pts": nci, "pve": r(pve, 4), "n": int(X.shape[0]),
                         "p": int(X.shape[1]), "nTypes": len(set(labels))},
       "ISLP NCI60（ISLP 圖 1.4）· Ch01-lab-zh.ipynb 儲存格 164",
       "PCA(random_state=0)，先對每個基因標準化"),
    js("FRAMES_w01shapes", {"sets": shapes}, "ISLP 套件的資料集實際形狀", "無隨機性"),
]))

print(f"\n/* 檢查：Wage n={len(age)}、2004 平均 {wage_2004_mean}（lab 111.15999687022256）· "
      f"年份趨勢每年 +{slope:.4f} · Smarket n={len(direction)} 其中 Up {int((direction=='Up').sum())} · "
      f"Lag1 的 Down 平均 {lag_box[0]['Down']['mean']} vs Up {lag_box[0]['Up']['mean']}"
      f"（幾乎一樣，這就是圖 1.2 的重點）· "
      f"NCI60 {X.shape[0]}×{X.shape[1]}，{len(set(labels))} 種型別，PC1+PC2 解釋 "
      f"{100*(pve[0]+pve[1]):.1f}% */", file=sys.stderr)
