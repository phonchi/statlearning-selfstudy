#!/usr/bin/env python3
"""Recompute the introductory EDA figures from ISLP data, without running labs."""
import json
import sys
import seaborn as sns
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm
from ISLP.models import ModelSpec as MS, contrast
from scipy.stats import gaussian_kde

import numpy as np
import pandas as pd
import sklearn
from ISLP import load_data
from sklearn.decomposition import PCA

VERSIONS = f"numpy {np.__version__} · pandas {pd.__version__} · scikit-learn {sklearn.__version__} · seaborn {sns.__version__} · matplotlib {matplotlib.__version__} · statsmodels {sm.__version__}"
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
def regression_frame(x, y, order):
    # Same seaborn estimator and 95% percentile bootstrap as the course lab.
    # The lab does not set its bootstrap seed; pin only that randomness here.
    fig, ax = plt.subplots()
    sns.regplot(x=x, y=y, order=order, truncate=True, scatter=False, seed=0, ax=ax)
    line = rounded(np.column_stack(ax.lines[0].get_data()), 6)
    band = rounded(ax.collections[0].get_paths()[0].vertices, 6)
    plt.close(fig)
    return {"line": line, "band": band}

age_fit = regression_frame(age, wage, 4)
year_fit = regression_frame(np.asarray(Wage.year, float), wage, 1)
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
pca = PCA(svd_solver="full")
Z = pca.fit_transform(Xs)
nci = [{"x": round(float(z[0]), 6), "y": round(float(-z[1]), 6),
        "z": round(float(z[2]), 6), "g": label} for z, label in zip(Z, labels)]

Auto = load_data("Auto")
fig, ax = plt.subplots()
sns.histplot(x="mpg", kde=True, stat="density", data=Auto, ax=ax)
hist = [[float(p.get_x()), float(p.get_x()+p.get_width()), float(p.get_height())] for p in ax.patches]
kde = rounded(np.column_stack(ax.lines[0].get_data()), 7)
plt.close(fig)
pair_columns = ["mpg", "displacement", "horsepower", "weight"]
pair_groups = sorted(Auto.cylinders.unique().tolist())
pair_kdes = []
# Seaborn pairplot excludes numeric hue from axes and uses KDE on the diagonal.
# Extract its exact KDE supports, bandwidth, and common normalization.
grid = sns.pairplot(Auto.loc[:, pair_columns + ["cylinders"]], hue="cylinders")
for ax in grid.diag_axes:
    pair_kdes.append([rounded(c.get_paths()[0].vertices, 7) for c in ax.collections])
pair_limits = [[{ "x": list(ax.get_xlim()), "y": list(ax.get_ylim())} for ax in row] for row in grid.axes]
plt.close(grid.fig)
joint = sns.jointplot(x="cylinders", y="mpg", data=Auto)
joint_x = [[float(p.get_x()),float(p.get_x()+p.get_width()),float(p.get_height())] for p in joint.ax_marg_x.patches]
joint_y = [[float(p.get_y()),float(p.get_y()+p.get_height()),float(p.get_width())] for p in joint.ax_marg_y.patches]
plt.close(joint.fig)
Bikeshare = load_data("Bikeshare")
Xbike = MS([contrast("mnth", "sum"), contrast("hr", "sum"),
            "workingday", "temp", "weathersit"]).fit_transform(Bikeshare)
model = sm.OLS(Bikeshare.bikers, Xbike).fit()
month_coefs = model.params[model.params.index.str.contains('mnth')].tolist()
month_coefs.append(-sum(month_coefs))
hour_coefs = [float(model.params[f'hr[{h}]']) for h in range(23)]
hour_coefs.append(-sum(hour_coefs))
assert Auto.shape == (392, 8) and Bikeshare.shape == (8645, 15) and X.shape == (64, 6830)
assert len(age_fit['line']) == 100 and len(year_fit['line']) == 100
assert abs(sum((hi-lo)*v for lo,hi,v in hist)-1) < 1e-12
assert abs(sum(month_coefs)) < 1e-10 and abs(sum(hour_coefs)) < 1e-10

print("\n".join([
    js("FRAMES_w01wage", {"scatter": rounded(np.column_stack([age, wage]), 6),
        "yearScatter": rounded(Wage[["year", "wage"]], 6), "ageFit": age_fit, "yearFit": year_fit, "eduBox": edu_box,
        "n": len(Wage), "cols": len(Wage.columns), "mean2004": float(Wage.loc[Wage.year == 2004, "wage"].mean())},
       "ISLP Wage；課程 Ch01 lab 儲存格145–155", "seaborn bootstrap seed=0; n_boot=1000; ci=95",
       "薪資單位千美元；全部3000筆；年齡四次多項式、年份一次線性迴歸及seaborn百分位bootstrap 95%信賴帶。箱形圖使用1.5IQR觀測值鬚與全部離群值。"),
    js("FRAMES_w01smarket", {"lagBox": lag_box, "corrNames": list(corr.columns), "corr": rounded(corr),
        "n": len(Smarket), "cols": len(Smarket.columns)}, "ISLP Smarket；課程 Ch01 lab 儲存格157–162",
       note="Lag1–3依當天Direction分組；Tukey箱形圖。Pearson相關只計算8個數值欄，Direction不在矩陣內。"),
    js("FRAMES_w01nci", {"pts": nci, "pve": rounded(pca.explained_variance_ratio_, 6),
        "n": X.shape[0], "cols": X.shape[1], "nTypes": len(set(labels))},
       "ISLP NCI60；課程 Ch01 lab 儲存格164–170", "無隨機性：標準化後以full SVD完整PCA，呈現PC1對-PC2與PC1對PC3",
       "位置只由基因資料決定；型別事後上色，保留全部14種原始型別。"),
    js("FRAMES_w01auto", {"hist": hist, "kde": kde, "pairColumns": pair_columns, "pairGroups": pair_groups, "pairKdes": pair_kdes, "pairLimits": pair_limits, "pairData": rounded(Auto[pair_columns + ["cylinders"]],6), "jointX": joint_x, "jointY": joint_y, "scatter": rounded(Auto[["horsepower", "mpg"]]),
        "n": len(Auto), "cols": len(Auto.columns)}, "ISLP Auto；課程 Ch01 lab 儲存格172–176",
       note="與lab相同seaborn預設分箱、density與KDE；含jointplot和完整四變數pairplot（cylinders為hue）；392筆全數使用。name是索引，不是資料欄。"),
    js("FRAMES_w01bike", {"monthCoefs": rounded(month_coefs,6), "hourCoefs": rounded(hour_coefs,6), "n": len(Bikeshare), "cols": len(Bikeshare.columns)},
       "ISLP Bikeshare；導論講義Bikeshare圖；Ch04 lab 線性與Poisson迴歸段落",
       note="OLS：bikers ~ mnth + hr + workingday + temp + weathersit；月份和小時用sum contrasts，最後係數為其餘係數負和。"),
    js("FRAMES_w01shapes", {"sets": [{"name": name, "n": len(data), "cols": len(data.columns)}
        for name, data in [("Wage", Wage), ("Smarket", Smarket), ("Auto", Auto), ("Bikeshare", Bikeshare)]]
        + [{"name": "NCI60", "n": X.shape[0], "cols": X.shape[1]}]}, "ISLP資料表形狀；cols為欄數，不是預測變數個數p"),
]))
print(f"Wage n={len(Wage)}; year/age bootstrap=1000 seed=0; "
      f"Auto density area={sum((hi-lo)*v for lo,hi,v in hist)}; "
      f"NCI types={len(set(labels))}, points={len(nci)}; "
      f"Bike January={month_coefs[0]:.9f}, hour0={hour_coefs[0]:.9f}", file=sys.stderr)
