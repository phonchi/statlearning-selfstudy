#!/usr/bin/env python3
"""Numerical checks for the new ch4/ch5 claims (seed 20261006)."""
import numpy as np
from scipy import stats
rng = np.random.default_rng(20261006)
ok = []
def check(name, cond):
    ok.append((name, bool(cond))); print(('PASS' if cond else 'FAIL'), name)

# 1. Mahalanobis: eigen form and whitening
A = rng.standard_normal((3, 3)); S = A @ A.T + 0.5 * np.eye(3)
x, mu = rng.standard_normal(3), rng.standard_normal(3)
d2 = (x - mu) @ np.linalg.solve(S, x - mu)
lam, Q = np.linalg.eigh(S); y = Q.T @ (x - mu)
Sm12 = Q @ np.diag(lam ** -0.5) @ Q.T; z = Sm12 @ (x - mu)
check('Mahalanobis eigen form', np.isclose(d2, np.sum(y ** 2 / lam)))
check('Mahalanobis = |Sigma^-1/2 (x-mu)|^2', np.isclose(d2, z @ z))
check('1-D Mahalanobis = |x-mu|/sigma', np.isclose(np.sqrt((7 - 3) ** 2 / 4.0), abs(7 - 3) / 2))

# 2. Var(a^T X) = a^T Sigma a ; diag(4,1) example
Sig = np.diag([4.0, 1.0]); a = np.array([1, 1]) / np.sqrt(2)
check('a^T Sigma a = 2.5', np.isclose(a @ Sig @ a, 2.5))
X = rng.multivariate_normal([0, 0], Sig, size=400000)
check('Var(a^T X) MC ~ 2.5', abs(np.var(X @ a) - 2.5) < 0.03)
xv = np.array([3.0, 4.0]); e1 = np.array([1.0, 0.0]); b = np.array([2.0, 0.0])
check('projection coordinate 3', np.isclose(e1 @ xv, 3))
check('projection vector general a', np.allclose((b @ xv) / (b @ b) * b, [3, 0]))

# 3. t classes, same Sigma, same nu: equal prior linear, unequal prior quadratic
nu, p = 5, 2
Sig2 = np.array([[1, -0.5], [-0.5, 1]]); m1, m2 = np.array([0., 0.]), np.array([1., 1.])
def logt(xx, m):
    return stats.multivariate_t(loc=m, shape=Sig2, df=nu).logpdf(xx)
def boundary_pts(pi1):
    pts = []
    for u in np.linspace(-3, 4, 15):
        f = lambda v: np.log(pi1) + logt([u, v], m1) - np.log(1 - pi1) - logt([u, v], m2)
        vs = np.linspace(-15, 15, 6001); fv = np.array([f(v) for v in vs])
        idx = np.where(np.sign(fv[:-1]) != np.sign(fv[1:]))[0]
        if len(idx): pts.append((u, vs[idx[0]]))
    return np.array(pts)
P = boundary_pts(0.5); coef = np.polyfit(P[:, 0], P[:, 1], 1)
check('t equal prior boundary linear', np.max(np.abs(np.polyval(coef, P[:, 0]) - P[:, 1])) < 0.01)
P = boundary_pts(0.8); coef = np.polyfit(P[:, 0], P[:, 1], 1)
check('t unequal prior boundary not linear', np.max(np.abs(np.polyval(coef, P[:, 0]) - P[:, 1])) > 0.05)

# 4. LOOCV shortcut and yhat_(i) formula
n = 40; Xd = np.column_stack([np.ones(n), rng.standard_normal(n), rng.standard_normal(n)])
yy = Xd @ [1, 2, -1] + rng.standard_normal(n)
H = Xd @ np.linalg.solve(Xd.T @ Xd, Xd.T); h = np.diag(H); e = yy - H @ yy; yhat = H @ yy
loo = []; yhat_i = []
for i in range(n):
    m = np.arange(n) != i
    bi = np.linalg.lstsq(Xd[m], yy[m], rcond=None)[0]
    yhat_i.append(Xd[i] @ bi); loo.append(yy[i] - Xd[i] @ bi)
check('LOOCV residual = e/(1-h)', np.allclose(loo, e / (1 - h)))
check('yhat_(i) = yhat_i - h/(1-h) e_i', np.allclose(yhat_i, yhat - h / (1 - h) * e))
check('h=0.8 inflates 5x', np.isclose(1 / (1 - 0.8), 5))

# 5. parameter counts p=100, K=3
p_, K = 100, 3
lda = K * p_ + p_ * (p_ + 1) // 2; qda = K * p_ + K * p_ * (p_ + 1) // 2; nb = 2 * K * p_
check('counts 5350/15450/600 (no prior)', (lda, qda, nb) == (5350, 15450, 600))

# 6. NB toy example (deck 04 p.36)
num1 = 0.5 * 0.368 * 0.484 * 0.226; num2 = 0.5 * 0.030 * 0.130 * 0.616
check('NB toy posterior 0.944', round(num1 / (num1 + num2), 3) == 0.944)

# 7. PR example: 1000 neg / 10 pos, TP=8, FP=12
check('PR example', (8 / 10, 8 / 20, 12 / 1000) == (0.8, 0.4, 0.012))

# 8. Portfolio alpha truth
sx, sy, sxy = 1.0, 1.25, 0.5
check('alpha = 0.6', np.isclose((sy - sxy) / (sx + sy - 2 * sxy), 0.6))

# 9. logit/logistic inverse
zz = np.linspace(-5, 5, 11); pp = 1 / (1 + np.exp(-zz))
check('logit(logistic(z)) = z', np.allclose(np.log(pp / (1 - pp)), zz))

# 10. average of correlated errors
v, rho, k = 1.0, 0.9, 10
C = v * (rho * np.ones((k, k)) + (1 - rho) * np.eye(k)); w = np.ones(k) / k
check('Var(mean) = v/k + (k-1) rho v / k', np.isclose(w @ C @ w, v / k + (k - 1) * rho * v / k))
print(f"{sum(c for _, c in ok)}/{len(ok)} checks passed")
raise SystemExit(0 if all(c for _, c in ok) else 1)
