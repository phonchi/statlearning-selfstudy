"""獨立核對 w06-detail-criteria-origins 的數學（2026-10-14）。"""
import numpy as np
from scipy.special import gammaln
rng = np.random.default_rng(0)
ok = lambda name, cond, info="": print(("PASS" if cond else "FAIL"), name, info)

# 1. Cp：E[測試 RSS]-E[訓練 RSS]=2rσ²，含近似偏差（μ 不在欄空間內）
n, r, s2, R = 60, 4, 2.0, 40000
X = np.c_[np.ones(n), rng.normal(size=(n, r - 1))]
mu = X @ np.array([1, 2, -1, .5]) + np.sin(3 * rng.normal(size=n))  # 有偏差
H = X @ np.linalg.solve(X.T @ X, X.T)
E1 = rng.normal(scale=np.sqrt(s2), size=(R, n)); E2 = rng.normal(scale=np.sqrt(s2), size=(R, n))
fit = (mu + E1) @ H
gap = (((mu + E2) - fit) ** 2).sum(1).mean() - (((mu + E1) - fit) ** 2).sum(1).mean()
ok("Cp optimism = 2rσ²", abs(gap - 2 * r * s2) < .3, f"{gap:.3f} vs {2*r*s2}")

# 2. AIC：E[ℓ_train(θ̂)]-E[ℓ_new(θ̂)] → k（高斯迴歸，σ² 也估，k=r+1）
def opt(n, r, R=20000):
    X = np.c_[np.ones(n), rng.normal(size=(n, r - 1))]; H = X @ np.linalg.solve(X.T @ X, X.T)
    Y = rng.normal(size=(R, n)); F = Y @ H  # 真值 μ=0、σ²=1
    sh = ((Y - F) ** 2).sum(1) / n
    lt = -n / 2 * np.log(2 * np.pi * sh) - n / 2
    # 新資料取條件期望：E‖y_new − F‖² = n + ‖F‖²（壓掉新資料的蒙地卡羅雜訊）
    ln = -n / 2 * np.log(2 * np.pi * sh) - (n + (F ** 2).sum(1)) / (2 * sh)
    d = lt - ln
    return d.mean(), d.std() / np.sqrt(R)
exact = lambda n, r: (n + r) / 2 * n / (n - r - 2) - n / 2  # n·σ̂²~χ²_{n−r}
for nn in (50, 400, 4000):
    g, se = opt(nn, 3); print(f"   n={nn}: optimism {g:.3f} ± {se:.3f} (MC SE), exact {exact(nn, 3):.3f} (k=4)")
    ok(f"AIC optimism within 3 SE of exact, n={nn}", abs(g - exact(nn, 3)) < 3 * se)
ok("AIC optimism → k", abs(exact(4000, 3) - 4) < .01, f"{exact(4000,3):.4f}")

# 2b. σ² 已知時 −2ℓ 的樂觀差恰為 2r（＝Cp 的 2rσ²/σ²）
ok("known σ²: −2ℓ gap = 2r", abs(gap / s2 - 2 * r) < .15, f"{gap/s2:.3f}")

# 3. BIC：共軛先驗的精確 log 邊際概似 vs ℓ̂ − (k/2) log n，差值應為 O(1)
def logml(y, X, tau2=4.0):  # β~N(0,τ²I)，σ²=1 已知 → y~N(0, I+τ²XXᵀ)
    n = len(y); C = np.eye(n) + tau2 * X @ X.T
    sign, ld = np.linalg.slogdet(C)
    return -0.5 * (n * np.log(2 * np.pi) + ld + y @ np.linalg.solve(C, y))
diffs = []
for nn in (100, 400, 1600):
    X = np.c_[np.ones(nn), rng.normal(size=(nn, 2))]; y = X @ np.array([.5, 1, -1]) + rng.normal(size=nn)
    b = np.linalg.lstsq(X, y, rcond=None)[0]; lhat = -nn / 2 * np.log(2 * np.pi) - ((y - X @ b) ** 2).sum() / 2
    d = logml(y, X) - (lhat - 3 / 2 * np.log(nn)); diffs.append(d); print(f"   n={nn}: logML − (ℓ̂ − k/2 log n) = {d:.3f}")
ok("BIC remainder O(1)", max(diffs) - min(diffs) < 0.5)

# 4. 表格數值
for nn, want in [(8, "2.08 1.04"), (100, "4.61 2.30"), (400, "5.99 3.00"), (10000, "9.21 4.61")]:
    got = f"{np.log(nn):.2f} {np.log(nn)/2:.2f}"; ok(f"log n table n={nn}", got == want, got)
ok("e^2 < 8", np.exp(2) < 8, f"{np.exp(2):.3f}")
