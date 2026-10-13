"""本次第 5、6 章新增數值與數學性質的獨立核對（numpy 模擬／精確計算）。"""
import itertools, math
import numpy as np

ok = []
def check(name, cond, detail=""):
    ok.append(bool(cond)); print(("PASS" if cond else "FAIL"), name, detail)

# 第 5 章：alpha 最小變異權重
sx2, sy2, sxy = 1.0, 1.25, 0.5
a = (sy2 - sxy) / (sx2 + sy2 - 2 * sxy)
V = lambda t: t*t*sx2 + (1-t)**2*sy2 + 2*t*(1-t)*sxy
grid = np.linspace(-1, 2, 300001)
check("alpha 解析解 = 數值最小", abs(grid[np.argmin(V(grid))] - a) < 1e-4, f"{a:.4f}")
# 不放回抽 n 筆只是重排：統計量不變
rng = np.random.default_rng(1); x = rng.normal(size=20)
check("不放回重抽 n 筆平均不變", all(abs(rng.permutation(x).mean() - x.mean()) < 1e-12 for _ in range(50)))

# 第 6 章：計數
check("2^10=1024, 5 折 5120", 2**10 == 1024 and 1024*5 == 5120)
check("p=4 前向 11 個、全子集 16、順序 24", 1+4+3+2+1 == 11 == 1+4*5//2 and 2**4 == 16 and math.factorial(4) == 24)
check("p=20：211 與 1,048,576", 1+20*21//2 == 211 and 2**20 == 1048576)
# p=4 每個子集都是某種順序的前段
reach = {frozenset(o[:k]) for o in itertools.permutations(range(4)) for k in range(5)}
check("p=4 所有 16 子集都可能被前向法走到", len(reach) == 16)

# 正交特徵：RSS 可加且 best subset = forward
rng = np.random.default_rng(6)
n, p = 60, 5
Q, _ = np.linalg.qr(np.column_stack([np.ones(n), rng.normal(size=(n, p))]))
X = Q[:, 1:] * rng.uniform(1, 3, p)        # 與常數欄正交 → 已中心化且兩兩正交
y = 3 + X @ rng.normal(size=p) + rng.normal(size=n)
yc = y - y.mean()
def rss(S):
    A = np.column_stack([np.ones(n)] + [X[:, j] for j in S])
    b = np.linalg.lstsq(A, y, rcond=None)[0]; return float(((y - A @ b)**2).sum())
TSS = float((yc**2).sum()); contrib = (X.T @ yc)**2 / (X**2).sum(0)
diff = max(abs(rss(S) - (TSS - contrib[list(S)].sum())) for k in range(p+1) for S in itertools.combinations(range(p), k))
check("正交時 RSS(S)=TSS−Σ貢獻", diff < 1e-6 * TSS, f"max diff {diff:.2e}, TSS {TSS:.1f}")
best = [min(itertools.combinations(range(p), k), key=rss) for k in range(1, p+1)]
cur = []
fwd = []
for k in range(p):
    j = min((j for j in range(p) if j not in cur), key=lambda j: rss(cur+[j])); cur.append(j); fwd.append(tuple(sorted(cur)))
check("正交時 best subset 與 forward 每個 k 相同", [tuple(sorted(b)) for b in best] == fwd)

# Cp：固定設計 E[test RSS]−E[train RSS]=2dσ²（含模型偏差）
rng = np.random.default_rng(7); n, d, s2 = 50, 4, 2.0
Xd = np.column_stack([np.ones(n), rng.normal(size=(n, d-1))])
mu = np.sin(Xd[:, 1]) * 3 + Xd[:, 2]**2           # 非線性 → 有近似偏差
H = Xd @ np.linalg.solve(Xd.T @ Xd, Xd.T)
R = 200000
E = rng.normal(scale=math.sqrt(s2), size=(R, n)); En = rng.normal(scale=math.sqrt(s2), size=(R, n))
Y = mu + E; fit = Y @ H.T
gap = ((mu + En - fit)**2).sum(1).mean() - ((Y - fit)**2).sum(1).mean()
check("固定設計樂觀差 ≈ 2dσ²（含偏差）", abs(gap - 2*d*s2) < 0.3, f"{gap:.3f} vs {2*d*s2}")
# 無關變數 ΔRSS/σ² ~ χ²₁（平均 1）
rng = np.random.default_rng(8); n = 40; s2 = 4.0
X0 = np.column_stack([np.ones(n), rng.normal(size=n)]); z = rng.normal(size=n); X1 = np.column_stack([X0, z])
P0 = X0 @ np.linalg.pinv(X0); P1 = X1 @ np.linalg.pinv(X1)
Y = (X0 @ [1, 2]) + rng.normal(scale=2, size=(100000, n))
dr = (((Y - Y @ P0.T)**2).sum(1) - ((Y - Y @ P1.T)**2).sum(1)) / s2
check("ΔRSS/σ² 平均 ≈ 1、變異 ≈ 2（χ²₁）", abs(dr.mean()-1) < 0.02 and abs(dr.var()-2) < 0.06, f"{dr.mean():.3f}, {dr.var():.3f}")
check("σ̂²=1,4,9,16 時 12 是否超過 2σ̂²", [12 > 2*v for v in (1, 4, 9, 16)] == [True, True, False, False])

# AIC/BIC 例：0.05² 與 σ²/n
rng = np.random.default_rng(9); n = 100; reps = 20000
X = rng.normal(size=(reps, n, 2)); y = 2*X[..., 0] + 0.05*X[..., 1] + rng.normal(size=(reps, n))
x0 = rng.normal(size=(reps, 2)); y0 = 2*x0[:, 0] + 0.05*x0[:, 1] + rng.normal(size=reps)
b2 = np.linalg.solve(np.einsum('rni,rnj->rij', X, X), np.einsum('rni,rn->ri', X, y)[..., None])[..., 0]
b1 = np.einsum('rn,rn->r', X[..., 0], y) / np.einsum('rn,rn->r', X[..., 0], X[..., 0])
m2 = ((y0 - (x0 * b2).sum(1))**2).mean(); m1 = ((y0 - x0[:, 0]*b1)**2).mean()
check("n=100 時不含 X2 的預測誤差較小（約 0.0025 vs 0.01 的差）", m1 < m2, f"含 X2 {m2:.4f}，不含 {m1:.4f}")

# adjusted R²：>0 等價式；E[RSS]=(n-d-1)σ²
rng = np.random.default_rng(10); n, d = 30, 3
Xa = np.column_stack([np.ones(n), rng.normal(size=(n, d))])
Ha = Xa @ np.linalg.solve(Xa.T @ Xa, Xa.T)
Y = Xa @ [1, .5, -.2, 0] + rng.normal(size=(100000, n))
rssv = ((Y - Y @ Ha.T)**2).sum(1); tssv = ((Y - Y.mean(1, keepdims=True))**2).sum(1)
check("E[RSS]=(n−d−1)σ²", abs(rssv.mean() - (n-d-1)) < 0.1, f"{rssv.mean():.3f}")
adj = 1 - (rssv/(n-d-1))/(tssv/(n-1))
check("adj R²>0 ⇔ RSS/(n−d−1)<TSS/(n−1)", np.array_equal(adj > 0, rssv/(n-d-1) < tssv/(n-1)))

# 對角設計：Ridge y/(1+λ)，Lasso 軟門檻 λ/2；例 λ=2
def lasso1(y, lam):
    g = np.linspace(-10, 10, 2000001); return g[np.argmin((y-g)**2 + lam*np.abs(g))]
check("軟門檻例：λ=2, y=0.8→0, y=3→2", abs(lasso1(0.8, 2)) < 1e-4 and abs(lasso1(3, 2) - 2) < 1e-4)
check("Ridge 例：0.8/3≈0.27, 3/3=1", round(0.8/3, 2) == 0.27 and 3/(1+2) == 1)
print("ALL PASS" if all(ok) else f"{ok.count(False)} FAIL")
