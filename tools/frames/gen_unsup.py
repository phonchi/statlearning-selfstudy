#!/usr/bin/env python3
"""產生 unsupervised_learning.html 需要的烘焙資料（FRAMES_w07*）。

只有「要對上課本／lab 的數字」或「忠實配適需要套件」的圖才烘焙：
  · USArrests 的 biplot（標準化／未標準化）→ ISLP 圖 12.1 與 12.4
  · USArrests 的 PVE 與累積 PVE → ISLP 圖 12.3（對 lab 儲存格 37／39）
  · 標準化後的 USArrests 資料矩陣 → 前端即時跑演算法 12.1（M = 1 的秩一近似）
  · scipy 的四種 linkage matrix → 前端只負責畫樹（ISLP 圖 12.11–12.14）
  · digits 的 PCA 與 t-SNE 嵌入 → 對 lab 儲存格 74／75
K-means 逐步器與 spin 元件完全即時，不在這裡烘焙。

跑法（用 pinned 環境，數字才可重現）：
  conda run -n m524 python tools/frames/gen_unsup.py > /tmp/w07.js
"""
import json
import sys

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from statsmodels.datasets import get_rdataset

VERSIONS = ("numpy {} · pandas {} · scikit-learn {} · scipy {} · statsmodels {}".format(
    np.__version__, pd.__version__, __import__("sklearn").__version__,
    __import__("scipy").__version__, __import__("statsmodels").__version__))
GEN = "tools/frames/gen_unsup.py"

# ── USArrests（跟 lab 一樣用 get_rdataset，不用 load_data）─────────────────
US = get_rdataset("USArrests").data
COLS = list(US.columns)                       # Murder Assault UrbanPop Rape
STATES = list(US.index)
ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI",
    "Wyoming": "WY",
}
TAGS = [ABBR[s] for s in STATES]
# 課本正文點名的州（圖 12.1 的解讀），只有這幾個在圖上寫字
CALLOUT = ["California", "Nevada", "Florida", "North Dakota", "Mississippi",
           "Hawaii", "Indiana", "Alaska"]


def sign_fix(load, scores):
    """符號正規化：PC1 讓負荷量總和為正、PC2 讓 UrbanPop 的負荷量為正。

    這樣就跟 ISLP 表 12.1／圖 12.1（以及 lab 儲存格 29 未翻號的那組）一致。
    主成分只在正負號上不唯一，選一個固定的約定才能重現課本的圖。
    """
    up = COLS.index("UrbanPop")
    for m, positive in ((0, load[0].sum() > 0), (1, load[1][up] > 0)):
        if not positive:
            load[m] = -load[m]
            scores[:, m] = -scores[:, m]
    return load, scores


def biplot(scale: bool):
    X = US.values.astype(float)
    Z = StandardScaler().fit_transform(X) if scale else X - X.mean(0)
    p = PCA()
    scores = p.fit_transform(Z)
    load, scores = sign_fix(p.components_.copy(), scores)
    lim = float(np.abs(scores[:, :2]).max()) * 1.12
    # 箭頭長度：讓最長的負荷量佔軸長的 0.78，兩種模式看起來才一樣清楚
    amax = float(np.abs(load[:2, :]).max())
    return {
        "scores": [[round(float(a), 3), round(float(b), 3)] for a, b in scores[:, :2]],
        "load": [[round(float(load[0, j]), 4), round(float(load[1, j]), 4)]
                 for j in range(len(COLS))],
        "lim": round(lim, 2),
        "arrow": round(lim * 0.78 / amax, 3),
        "pve": [round(float(v), 4) for v in p.explained_variance_ratio_],
    }


BI = {"scaled": biplot(True), "unscaled": biplot(False)}

# ── PVE（對 lab 儲存格 35／37／39）────────────────────────────────────────
Xs = StandardScaler().fit_transform(US.values.astype(float))
pca = PCA().fit(Xs)
PVE = [round(float(v), 6) for v in pca.explained_variance_ratio_]
CUM = [round(float(v), 6) for v in np.cumsum(pca.explained_variance_ratio_)]
EVAR = [round(float(v), 6) for v in pca.explained_variance_]
SDEV = [round(float(v), 6) for v in np.sqrt(pca.explained_variance_)]

# ── 矩陣補全用的標準化資料矩陣（前端即時跑演算法 12.1）────────────────────
MC = {
    "cols": COLS,
    "tags": TAGS,
    "X": [[round(float(v), 4) for v in row] for row in Xs],
    "labCorr": 0.7113567434297361,      # lab 儲存格 66
    "labSoft": 0.7120562258475328,      # lab 儲存格 69
    "labMss": 0.381,                    # lab 儲存格 64 最後一輪
}

# ── Dendrogram：三群結構的模擬資料 + 四種 linkage 的 linkage matrix ───────
rng = np.random.default_rng(12)
CEN = np.array([[-3.4, 2.6], [-0.8, -1.3], [2.5, 1.0]])
NPG = 10
# 群間有點重疊是刻意的：太乾淨的話 single linkage 也會分對，看不出鏈狀的毛病
DP = np.vstack([c + rng.normal(scale=1.2, size=(NPG, 2)) for c in CEN])
DG = {"pts": [[round(float(a), 3), round(float(b), 3)] for a, b in DP],
      "truth": [k for k in range(3) for _ in range(NPG)], "n": int(len(DP)),
      "trees": {}}
for meth in ("complete", "average", "single", "centroid"):
    L = linkage(DP, method=meth, metric="euclidean")
    d = dendrogram(L, no_plot=True)
    DG["trees"][meth] = {
        "Z": [[int(a), int(b), round(float(h), 4), int(c)] for a, b, h, c in L],
        "order": [int(i) for i in d["leaves"]],
        "hmax": round(float(L[:, 2].max()), 4),
    }

# ── digits：PCA 與兩種 perplexity 的 t-SNE（對 lab 儲存格 71–75）──────────
dig = load_digits()
DX = dig.images.reshape(-1, dig.images.shape[1] * dig.images.shape[2])
sub = np.random.default_rng(0).choice(len(DX), 500, replace=False)
sub.sort()
DXs, DYs = DX[sub], dig.target[sub]


def norm2d(E):
    E = np.asarray(E, dtype=float)
    E = E - E.mean(0)
    E = E / np.abs(E).max()
    return [[round(float(a), 3), round(float(b), 3)] for a, b in E]


EMB = {"labels": [int(v) for v in DYs], "n": int(len(sub)),
       "views": {"pca": {"name": "PCA（線性投影）", "xy": norm2d(PCA(n_components=2).fit_transform(DXs))}}}
for perp in (5, 30):
    t = TSNE(n_components=2, perplexity=perp, init="pca",
             learning_rate="auto", random_state=0)
    EMB["views"][f"tsne{perp}"] = {"name": f"t-SNE（perplexity = {perp}）",
                                   "xy": norm2d(t.fit_transform(DXs))}

# ── 襪子與電腦：ISLP 圖 12.16 的三種尺度（課本沒給數值，照圖形自訂）──────
SHOP = {
    "socks": [8, 11, 7, 6, 5, 6, 7, 8],
    "comp": [0, 0, 0, 0, 1, 1, 1, 1],
    "priceSock": 2.0, "priceComp": 1400.0,
}

# ── 輸出 ────────────────────────────────────────────────────────────────
def js(name, obj, src, seed, note=""):
    meta = {"src": src, "seed": seed, "versions": VERSIONS, "gen": GEN}
    if note:
        meta["note"] = note
    return (f"const {name} = " + json.dumps({"meta": meta, **obj},
                                            ensure_ascii=False, separators=(",", ":")) + ";")


out = [
    js("FRAMES_w07bi", {"cols": COLS, "tags": TAGS,
                        "callout": [TAGS[STATES.index(s)] for s in CALLOUT],
                        "vars": {c: round(float(US[c].var(ddof=1)), 4) for c in COLS},
                        **BI},
       "USArrests（statsmodels get_rdataset）· ISLP 圖 12.1 與圖 12.4",
       "無隨機（PCA 是確定性的）",
       "負荷量與 lab 儲存格 29 的 components_ 逐位相同（PC1 全正、PC2 的 UrbanPop 為正）"),
    js("FRAMES_w07pve", {"pve": PVE, "cum": CUM, "evar": EVAR, "sdev": SDEV,
                         "n": int(len(US)), "p": len(COLS)},
       "USArrests 標準化後的 PCA · ISLP 圖 12.3（對 lab 儲存格 35／37／39）",
       "無隨機",
       f"PVE = {PVE}，與 lab 儲存格 39 的 explained_variance_ratio_ 相符"),
    js("FRAMES_w07mc", MC,
       "USArrests 標準化後的資料矩陣 · ISLP §12.3 演算法 12.1（lab 儲存格 48–66）",
       "無隨機（缺失位置由前端的 HC.stat.lcg 決定）",
       "前端即時跑演算法 12.1，缺失位置與 lab 的 np.random.seed(15) 不同，"
       "所以相關係數不會剛好是 0.7114；lab 的數字只出現在 .deck-extra 卡"),
    js("FRAMES_w07dendro", DG,
       "三群結構的模擬資料（比照 ISLP 圖 12.10 的形狀）· "
       "linkage matrix 由 scipy.cluster.hierarchy.linkage 算出",
       "np.random.default_rng(12)，3 群 × 10 點，scale = 1.2",
       "四種 linkage 的 Z 矩陣格式為 [i, j, 高度, 群大小]，與 scipy 一致；"
       "切 3 群時 complete 的 ARI = 0.90、single 只有 0.49（鏈狀效應）"),
    js("FRAMES_w07tsne", EMB,
       "sklearn load_digits 隨機取 500 筆 · 對 lab 儲存格 71–75（TSNE init='pca'）",
       "取樣 np.random.default_rng(0)；TSNE(random_state=0)",
       "座標各自平移到中心並除以最大絕對值，只保留形狀（t-SNE 的座標本身沒有意義）"),
    js("FRAMES_w07shop", SHOP,
       "ISLP 圖 12.16（襪子與電腦）· 課本沒有給數值，照圖形的形狀自訂",
       "手動指定，無隨機",
       "三種尺度（原始次數／標準化／花費金額）下的 K-means 由前端即時計算"),
]
print("\n".join(out))

print(f"\n/* 檢查：PC1 負荷量={BI['scaled']['load'][0][0]:.6f}（lab 儲存格 29 是 0.53589947）· "
      f"PVE[0]={PVE[0]}（lab 儲存格 39 是 0.62006039）· "
      f"前兩個累積 PVE={CUM[1]:.4f}（課本說約 87%）· "
      f"未標準化時 Assault 的 PC1 負荷量={BI['unscaled']['load'][1][0]:.4f}（應接近 1）· "
      f"dendro hmax(single)={DG['trees']['single']['hmax']} */", file=sys.stderr)
assert abs(BI["scaled"]["load"][0][0] - 0.53589947) < 1e-6, "PC1 負荷量對不上 lab 儲存格 29"
assert abs(PVE[0] - 0.62006039) < 1e-6, "PVE 對不上 lab 儲存格 39"
assert abs(BI["unscaled"]["load"][1][0]) > 0.99, "未標準化時 Assault 應主宰 PC1"
