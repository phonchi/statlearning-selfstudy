#!/usr/bin/env python3
"""產生 deep_learning.html 需要的烘焙資料（FRAMES_w11*）。

這一章只烘焙一樣東西：**雙下降**（ISLP §10.8、圖 10.20 與 10.21）。

為什麼它一定要烘焙：d > n 時最小平方解不唯一，課本取的是「係數平方和最小」
的最小範數解，那需要 SVD（np.linalg.lstsq 的 rank-deficient 分支）。
自然樣條基底加 SVD 不是 50 行 JS 寫得出來的，符合撰寫契約的 baked 條件 (b)。

其餘元件全部 live：activation、前向傳播、卷積與池化、參數量、梯度下降軌跡
都有閉式解或只是幾十次四則運算，照契約必須即時算。

課本的設定逐字照做（§10.8 第 432 頁）：
  n = 20，Y = sin(X) + ε，X ~ U[−5, 5]，ε ~ N(0, σ²) 且 σ = 0.3
  自然樣條，節點取訓練資料的 d 個等機率分位數（d > n 時以內插求分位數）
  d > n 用最小範數解

**誤差曲線是 50 組重抽樣的平均，不是單一次模擬。** 原因是實測出來的：n 只有 20，
單一次抽樣的曲線完全被「這 20 個 x 剛好擠成幾叢」主宰——擠在一起的分位數節點
會讓基底幾乎退化，尖峰因此跑到 d = 16～18 而不是內插門檻 d = n = 20，
第二段下降也被雜訊蓋掉。（試過用 rcond 砍小奇異值，沒有用：基底是滿秩的，
是內插曲線本身在狂震。）平均之後尖峰回到門檻上，兩段下降都乾淨。

圖 10.21 的四個面板用第 0 組（種子 SEED 本身），不是另外挑的。

跑法（用 pinned 環境，數字才可重現）：
  conda run -n m524 python tools/frames/gen_deeplearning.py > /tmp/w11.js
"""
import json
import sys

import numpy as np
from ISLP.transforms import NaturalSpline

VERSIONS = "numpy {} · pandas {} · scikit-learn {} · ISLP {}".format(
    np.__version__, __import__("pandas").__version__,
    __import__("sklearn").__version__, __import__("ISLP").__version__)
GEN = "tools/frames/gen_deeplearning.py"
BOOK = "ISLP §10.8（圖 10.20 與 10.21 的模擬設定）"

N = 20                 # 課本的訓練樣本數
SIGMA = 0.3            # 課本的雜訊標準差
N_TEST = 2000          # 課本沒說測試集多大；用大樣本讓測試誤差穩定
REPS = 50              # 重抽樣組數（見檔頭：單一次抽樣看不出雙下降）
SEED = 100

DS = [2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 19, 20, 21, 22, 24, 26, 28,
      30, 34, 38, 42, 46, 50, 56, 62, 70, 80, 90, 100]
GRID = np.linspace(-5, 5, 121)
PANELS = [8, 20, 42, 80]


def draw(seed):
    rng = np.random.default_rng(seed)
    xt = np.sort(rng.uniform(-5, 5, N))
    yt = np.sin(xt) + SIGMA * rng.standard_normal(N)
    xe = rng.uniform(-5, 5, N_TEST)
    ye = np.sin(xe) + SIGMA * rng.standard_normal(N_TEST)
    return xt, yt, xe, ye


def fit_ns(xt, yt, d, xs):
    """配 d 個自由度的自然樣條，回傳 (在 xs 上的預測, 訓練預測, 係數平方和)。

    d > n 時 lstsq 走 rank-deficient 分支，回的正是課本要的最小範數解。

    邊界釘在 X 的定義域 ±5，不是訓練資料的 min/max：否則落在訓練範圍外的測試點
    會走 splev 的外插分支，B 樣條在那裡是多項式外插、會炸開（第一版 d = 80 的
    測試 MSE 因此變成 1161，雙下降的第二段完全被外插雜訊蓋掉）。
    """
    ns = NaturalSpline(df=d, intercept=True,
                       lower_bound=-5.0, upper_bound=5.0).fit(xt.reshape(-1, 1))
    B = np.asarray(ns.transform(xt.reshape(-1, 1)))
    beta, *_ = np.linalg.lstsq(B, yt, rcond=None)
    pred = np.asarray(ns.transform(np.asarray(xs).reshape(-1, 1))) @ beta
    return pred, B @ beta, float(beta @ beta)


# ── 誤差曲線：REPS 組重抽樣的平均 ────────────────────────────────────────
train_mse = np.zeros(len(DS))
test_mse = np.zeros(len(DS))
for r in range(REPS):
    xt, yt, xe, ye = draw(SEED + r)
    for i, d in enumerate(DS):
        pred_te, pred_tr, _ = fit_ns(xt, yt, d, xe)
        train_mse[i] += np.mean((yt - pred_tr) ** 2)
        test_mse[i] += np.mean((ye - pred_te) ** 2)
train_mse /= REPS
test_mse /= REPS

# ── 圖 10.21 的四個面板：第 0 組資料，d = 8 / 20 / 42 / 80 ─────────────────
x_train, y_train, _, _ = draw(SEED)
fits = {}
for d in PANELS:
    pred, _, l2 = fit_ns(x_train, y_train, d, GRID)
    fits[str(d)] = {"y": [round(float(v), 3) for v in pred], "l2": round(l2, 1)}

# 訊噪比 Var(f(X))/σ²，課本 §10.8 說是 5.9
snr = np.var(np.sin(np.random.default_rng(0).uniform(-5, 5, 200000))) / SIGMA ** 2


def js(name, obj, src, seed, note=""):
    meta = {"src": src, "seed": seed, "versions": VERSIONS, "gen": GEN}
    if note:
        meta["note"] = note
    return (f"const {name} = " + json.dumps({"meta": meta, **obj},
                                            ensure_ascii=False, separators=(",", ":")) + ";")


out = js(
    "FRAMES_w11dd",
    {
        "n": N, "sigma": SIGMA, "thr": N, "snr": round(float(snr), 2), "reps": REPS,
        "ds": DS,
        "train": [round(float(v), 4) for v in train_mse],
        "test": [round(float(v), 3) for v in test_mse],
        "xtr": [round(float(v), 3) for v in x_train],
        "ytr": [round(float(v), 3) for v in y_train],
        "grid": [round(float(v), 3) for v in GRID],
        "truth": [round(float(np.sin(v)), 3) for v in GRID],
        "panels": PANELS,
        "fits": fits,
    },
    BOOK,
    f"np.random.default_rng({SEED}…{SEED + REPS - 1})，n={N}、σ={SIGMA}、測試集 {N_TEST} 筆",
    f"依課本 §10.8 的設定重跑，不是圖 10.20 的逐點複製。誤差曲線是 {REPS} 組重抽樣的平均"
    f"（單一次抽樣時 n = 20 的分位數節點常擠在一起，尖峰會跑掉）；"
    f"面板用第 0 組。課本沒有公佈亂數種子，所以高低會有差，"
    f"但兩段下降與 d = {N} 那根尖峰的位置一致。",
)
print(out)

# ── 自我對照（印到 stderr，不進頁面）───────────────────────────────────
p = lambda s: print(s, file=sys.stderr)  # noqa: E731
at = lambda d: test_mse[DS.index(d)]     # noqa: E731
p(f"訊噪比 Var(f)/σ² = {snr:.2f}（課本 §10.8 說 5.9）")
p(f"d = {N}（內插門檻）訓練 MSE = {train_mse[DS.index(N)]:.2e}（課本說降到 0）")
p(f"測試 MSE：d=8 → {at(8):.2f}　d=19 → {at(19):.1f}　d=20 → {at(20):.1f} ←尖峰"
  f"　d=42 → {at(42):.2f} ←第二段下降　d=100 → {at(100):.2f}")
p(f"尖峰落在 d = {DS[int(np.argmax(test_mse))]}（應該等於 n = {N} 附近）")
p("面板的係數平方和 Σβ²：" + "、".join(f"d={d} → {fits[str(d)]['l2']}" for d in PANELS)
  + "  ← d=20 內插得最狂，加到 42 之後反而收斂")
p(f"輸出 {len(out) / 1024:.1f} KB")
