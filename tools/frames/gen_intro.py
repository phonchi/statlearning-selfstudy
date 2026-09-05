#!/usr/bin/env python3
"""Recompute the introductory EDA figures from ISLP data, without running labs."""
import json
import sys
from collections import Counter

import numpy as np
import pandas as pd
import sklearn
from ISLP import load_data
from sklearn.decomposition import PCA

VERSIONS = f"numpy {np.__version__} · pandas {pd.__version__} · scikit-learn {sklearn.__version__}"
GEN = "tools/frames/gen_intro.py"
rng = np.random.default_rng(0)


def rounded(values, digits=4):
    return np.round(np.asarray(values, dtype=float), digits).tolist()


def tukey(values):
    """Linear quartiles; whiskers end at observations inside the 1.5 IQR fences."""
    v = np.asarray(values, dtype=float)
    q1, med, q3 = np.quantile(v, [.25, .5, .75], method="linear")
    iqr = q3 - q1
    inside = v[(v >= q1 - 1.5 * iqr) & (v <= q3 + 1.5 * iqr)]
    outside = v[(v < q1 - 1.5 * iqr) | (v > q3 + 1.5 * iqr)]
    return {"n": len(v), "q1": round(float(q1), 4), "med": round(float(med), 4),
            "q3": round(float(q3), 4), "lo": round(float(inside.min()), 4),
            "hi": round(float(inside.max()), 4), "outliers": rounded(np.sort(outside)),
            "mean": round(float(v.mean()), 4)}


def js(name, obj, src, seed="無隨機性", note=""):
    meta = {"src": src, "seed": seed, "versions": VERSIONS, "gen": GEN, "note": note}
    return "const " + name + " = " + json.dumps({"meta": meta, **obj}, ensure_ascii=False,
                                                 separators=(",", ":"), allow_nan=False) + ";"


Wage = load_data("Wage")
age, wage = np.asarray(Wage.age, float), np.asarray(Wage.wage, float)
idx = np.sort(rng.choice(len(Wage), 600, replace=False))
# Four-year bins cover every observation, including age 80; the final bin includes its right edge.
edges = np.arange(18, 83, 4)
age_curve = []
for i, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
    mask = (age >= lo) & ((age <= hi) if i == len(edges) - 2 else (age < hi))
    if mask.any():
        age_curve.append([round(float(age[mask].mean()), 3), round(float(wage[mask].mean()), 4),
                          int(mask.sum()), int(lo), int(hi)])
year_mean = [[int(y), round(float(g.wage.mean()), 4), len(g)] for y, g in Wage.groupby("year")]
edu_box = [{"label": str(label).split(". ", 1)[1], **tukey(g.wage)}
           for label, g in Wage.groupby("education", observed=True)]

Smarket = load_data("Smarket")
lag_box = [{"lag": k, **{d: tukey(Smarket.loc[Smarket.Direction == d, f"Lag{k}"])
                         for d in ["Down", "Up"]}} for k in [1, 2, 3]]
corr = Smarket.corr(numeric_only=True)

NCI60 = load_data("NCI60")
X = np.asarray(NCI60["data"], dtype=float)
labels = [str(x) for x in np.asarray(NCI60["labels"]).ravel()]
Xs = (X - X.mean(0)) / np.where(X.std(0) == 0, 1, X.std(0))
# Full SVD matches the lab's deterministic PCA convention; labels are not an input.
pca = PCA(n_components=2, svd_solver="full")
Z = pca.fit_transform(Xs)
big = {label for label, count in Counter(labels).items() if count >= 5}
nci = [{"x": round(float(z[0]), 4), "y": round(float(z[1]), 4),
        "g": label if label in big else "其他型別"} for z, label in zip(Z, labels)]

Auto = load_data("Auto")
auto_edges = np.arange(5, 51, 5)
counts, _ = np.histogram(Auto.mpg, bins=auto_edges)
hist = [[int(lo), int(hi), int(count)] for lo, hi, count in zip(auto_edges[:-1], auto_edges[1:], counts)]
Bikeshare = load_data("Bikeshare")
# hr is categorical in ISLP: convert explicitly so the graph follows clock order.
bike = Bikeshare.assign(hour=Bikeshare.hr.astype(int))
hour_mean = [[int(hr), round(float(g.bikers.mean()), 4), len(g)]
             for hr, g in bike.groupby("hour", sort=True)]
assert Auto.shape == (392, 8) and Bikeshare.shape == (8645, 15) and X.shape == (64, 6830)
assert sum(row[2] for row in age_curve) == len(Wage)
assert sum(counts) == len(Auto) and sum(row[2] for row in hour_mean) == len(Bikeshare)

print("\n".join([
    js("FRAMES_w01wage", {"scatter": rounded(np.column_stack([age[idx], wage[idx]])),
        "ageCurve": age_curve, "yearMean": year_mean, "eduBox": edu_box,
        "n": len(Wage), "cols": len(Wage.columns), "mean2004": float(Wage.loc[Wage.year == 2004, "wage"].mean())},
       "ISLP Wage；課程 Ch01 lab 儲存格145–155", "default_rng(0) 抽600點；彙總使用全部3000筆",
       "薪資單位千美元；年齡線為本站4歲分箱平均，不是lab多項式線。箱形圖使用1.5IQR觀測值鬚與全部離群值。"),
    js("FRAMES_w01smarket", {"lagBox": lag_box, "corrNames": list(corr.columns), "corr": rounded(corr),
        "n": len(Smarket), "cols": len(Smarket.columns)}, "ISLP Smarket；課程 Ch01 lab 儲存格157–162",
       note="Lag1–3依當天Direction分組；Tukey箱形圖。Pearson相關只計算8個數值欄，Direction不在矩陣內。"),
    js("FRAMES_w01nci", {"pts": nci, "pve": rounded(pca.explained_variance_ratio_, 6),
        "n": X.shape[0], "cols": X.shape[1], "nTypes": len(set(labels))},
       "ISLP NCI60；課程 Ch01 lab 儲存格164–170", "無隨機性：標準化後以full SVD取2D投影",
       "位置只由基因資料決定；型別事後上色，樣本少於5的型別合併為其他型別。"),
    js("FRAMES_w01auto", {"hist": hist, "scatter": rounded(Auto[["horsepower", "mpg"]]),
        "n": len(Auto), "cols": len(Auto.columns)}, "ISLP Auto；課程 Ch01 lab 儲存格172–176",
       note="本站直方圖每箱5 mpg、縱軸為車輛筆數，不含lab的KDE；392筆全數使用。name是索引，不是資料欄。"),
    js("FRAMES_w01bike", {"hourMean": hour_mean, "n": len(Bikeshare), "cols": len(Bikeshare.columns)},
       "ISLP Bikeshare；課程 Ch01 lab 儲存格178–179所載資料，本站EDA補充",
       note="將所有日期按hr分組，取bikers算術平均；不是講義p35的模型係數曲線，不控制工作日或天氣。"),
    js("FRAMES_w01shapes", {"sets": [{"name": name, "n": len(data), "cols": len(data.columns)}
        for name, data in [("Wage", Wage), ("Smarket", Smarket), ("Auto", Auto), ("Bikeshare", Bikeshare)]]
        + [{"name": "NCI60", "n": X.shape[0], "cols": X.shape[1]}]}, "ISLP資料表形狀；cols為欄數，不是預測變數個數p"),
]))
print(f"Wage 2004 mean={Wage.loc[Wage.year == 2004, 'wage'].mean():.12f}; "
      f"Auto={Auto.shape}; Bike={Bikeshare.shape}; NCI={X.shape}; "
      f"hour counts={sum(row[2] for row in hour_mean)}; histogram total={sum(counts)}", file=sys.stderr)
