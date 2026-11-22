"""第 9 章加深內容的數學核算（2026-11-22）。conda run -n m524 python verify_svm.py"""
import math
from itertools import combinations_with_replacement

import numpy as np
from sklearn.svm import SVC

ok = 0
def check(name, cond, info=""):
    global ok
    if not cond:
        raise SystemExit(f"FAIL {name} {info}")
    ok += 1
    print(f"PASS {name} {info}")

rng = np.random.default_rng(20261122)

# 1. 點到超平面距離 = 帶號純量投影；向量投影
b = np.array([2.0, 3.0]); b0 = 1.0; x0 = np.array([1.5, -0.7])
d_formula = (b @ x0 + b0) / np.linalg.norm(b)
t = (b @ x0 + b0) / (b @ b); foot = x0 - t * b
check("distance_foot_on_plane", abs(b @ foot + b0) < 1e-12)
check("distance_signed_scalar_projection", abs(abs(d_formula) - np.linalg.norm(x0 - foot)) < 1e-12, f"{d_formula:.6f}")
p0 = -b0 * b / (b @ b)                     # 平面上一點
check("scalar_proj_of_x0_minus_p0", abs((x0 - p0) @ b / np.linalg.norm(b) - d_formula) < 1e-12)
vproj = ((x0 - p0) @ b) / (b @ b) * b
check("vector_proj_length", abs(np.linalg.norm(vproj) - abs(d_formula)) < 1e-12)

# 2. 超平面的方向空間是 p-1 維線性子空間；β0≠0 時不含原點
p = 5; beta = rng.normal(size=p); beta0 = 0.8
_, s, Vt = np.linalg.svd(beta[None, :])
null = Vt[1:]
check("direction_space_dim", null.shape[0] == p - 1 and np.allclose(null @ beta, 0))
xa = -beta0 * beta / (beta @ beta)
pts = xa + rng.normal(size=(3, p - 1)) @ null
check("affine_points_on_plane", np.allclose(pts @ beta + beta0, 0))
check("affine_not_closed_under_sum", abs((pts[0] + pts[1]) @ beta + beta0) > 1e-6)
check("affine_closed_under_affine_comb", abs((0.3 * pts[0] + 0.7 * pts[1]) @ beta + beta0) < 1e-12)

# 3. 縮放不變性：同乘 a，邊界與幾何距離不變、函數間隔乘 a
X = rng.normal(size=(20, 2)); y = np.where(X[:, 0] + 0.5 * X[:, 1] > 0, 1, -1)
X[y == 1] += 0.6; X[y == -1] -= 0.6
clf = SVC(kernel="linear", C=1e8).fit(X, y)
w = clf.coef_[0]; c = clf.intercept_[0]
func = y * (X @ w + c)
check("hard_margin_functional_min_is_1", abs(func.min() - 1) < 1e-3, f"min y f = {func.min():.6f}")
M = 1 / np.linalg.norm(w)
geo = func / np.linalg.norm(w)
check("M_equals_1_over_norm", abs(geo.min() - M) < 1e-3, f"M = {M:.6f}")
for a in (0.5, 3.0):
    fa = y * (X @ (a * w) + a * c)
    check(f"scale_{a}_functional_scales", np.allclose(fa, a * func))
    check(f"scale_{a}_geometric_same", np.allclose(fa / np.linalg.norm(a * w), geo))
    check(f"scale_{a}_signs_same", np.array_equal(np.sign(X @ (a * w) + a * c), np.sign(X @ w + c)))
# unit-norm 版本的 β 與 M：β/‖β‖ 讓 y f 直接等於距離
u = w / np.linalg.norm(w); u0 = c / np.linalg.norm(w)
check("unit_norm_margin_is_M", abs((y * (X @ u + u0)).min() - M) < 1e-3)

# 4. slack 在三式中不變：ε_i = 1 - y f /(M‖β‖) 與尺度無關（軟邊界）
Xs = rng.normal(size=(40, 2)); ys = np.where(Xs[:, 0] + Xs[:, 1] + 0.7 * rng.normal(size=40) > 0, 1, -1)
sc = SVC(kernel="linear", C=0.5).fit(Xs, ys); ws = sc.coef_[0]; cs = sc.intercept_[0]
eps_pen = np.maximum(0, 1 - ys * (Xs @ ws + cs))            # 懲罰形式（M‖β‖=1）
Ms = 1 / np.linalg.norm(ws); u = ws / np.linalg.norm(ws); u0 = cs / np.linalg.norm(ws)
eps_unit = np.maximum(0, 1 - ys * (Xs @ u + u0) / Ms)         # ‖β‖=1 形式：y f ≥ M(1-ε)
check("slack_same_across_forms", np.allclose(eps_pen, eps_unit))
for a in (0.2, 7.0):
    ua = a * u; ua0 = a * u0
    eps_a = np.maximum(0, 1 - ys * (Xs @ ua + ua0) / (Ms * np.linalg.norm(ua)))
    check(f"slack_scale_{a}", np.allclose(eps_a, eps_unit))

# 5. 硬邊界 dual：代入 w=Σαyx 後 L = Σα - ½‖w‖²，且 primal = dual
alpha = np.zeros(len(y)); alpha[clf.support_] = np.abs(clf.dual_coef_[0])
w_from_alpha = (alpha * y) @ X
check("w_equals_sum_alpha_y_x", np.allclose(w_from_alpha, w, atol=1e-3))
check("sum_alpha_y_zero", abs(alpha @ y) < 1e-3)
L = 0.5 * w @ w + np.sum(alpha * (1 - y * (X @ w + c)))
D = alpha.sum() - 0.5 * w_from_alpha @ w_from_alpha
check("lagrangian_equals_dual_at_opt", abs(L - D) < 1e-2, f"L={L:.5f} D={D:.5f}")
check("strong_duality", abs(0.5 * w @ w - D) < 1e-2, f"P={0.5*w@w:.5f}")
cross = -np.sum(alpha * y * (X @ w_from_alpha))
check("cross_term_is_minus_norm_sq", abs(cross + w_from_alpha @ w_from_alpha) < 1e-9)
check("alpha_nonneg", alpha.min() >= 0)
check("complementary_slackness", np.all(alpha * (y * (X @ w + c) - 1) < 1e-3))

# 6. 預算夠大一定可行：任意 β、β0，令 ε_i = max(0, 1 - y f / M) 即滿足限制
bb = rng.normal(size=2); bb /= np.linalg.norm(bb); bb0 = 0.3; Mv = 0.5
epsv = np.maximum(0, 1 - ys * (Xs @ bb + bb0) / Mv)
check("any_beta_feasible_with_budget", np.all(ys * (Xs @ bb + bb0) >= Mv * (1 - epsv) - 1e-12) and epsv.sum() > 0,
      f"所需預算 {epsv.sum():.3f}")
check("misclassified_have_eps_gt_1", np.all(epsv[ys * (Xs @ bb + bb0) < 0] > 1))

# 7. 多項式特徵維度與二次核
def n_terms(p, d):
    return sum(math.comb(p + k - 1, k) for k in range(1, d + 1))
check("cubic_2vars_9", n_terms(2, 3) == 9)
check("binom_formula", n_terms(2, 3) == math.comb(5, 3) - 1)
check("p100_d3", n_terms(100, 3) == math.comb(103, 3) - 1, f"{n_terms(100,3)}")
a_, b_ = rng.normal(size=2), rng.normal(size=2)
phi = lambda v: np.array([np.sqrt(2) * v[0] * v[1], v[0] ** 2, v[1] ** 2])
check("quadratic_kernel_identity", abs(phi(a_) @ phi(b_) - (a_ @ b_) ** 2) < 1e-12)

# 8. RBF 一維泰勒特徵：截斷內積收斂到核值；Gram 半正定
g = 0.7; xx, zz = 0.9, -0.4
def feat(v, m):
    return np.array([math.exp(-g * v * v) * math.sqrt((2 * g) ** k / math.factorial(k)) * v ** k for k in range(m)])
target = math.exp(-g * (xx - zz) ** 2)
errs = [abs(feat(xx, m) @ feat(zz, m) - target) for m in (2, 5, 10, 20)]
check("rbf_taylor_converges", errs[-1] < 1e-12 and errs == sorted(errs, reverse=True), str([f"{e:.1e}" for e in errs]))
Z = rng.normal(size=(30, 3))
K = np.exp(-0.5 * ((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1))
check("rbf_gram_psd", np.linalg.eigvalsh(K).min() > -1e-10)
check("rbf_gram_full_rank_distinct_points", np.linalg.matrix_rank(K) == 30)
# γ 大 → 核值隨距離下降得快
dists = np.array([0.5, 1.0])
check("gamma_larger_faster_decay", np.all(np.exp(-5 * dists ** 2) < np.exp(-0.5 * dists ** 2)))
check("gamma_sigma", abs(math.exp(-g * 1.3 ** 2) - math.exp(-1.3 ** 2 / (2 * (1 / math.sqrt(2 * g)) ** 2))) < 1e-15)

# 9. kernel ridge：X^T(XX^T+λI)^{-1} = (X^TX+λI)^{-1}X^T；預測只用內積
n, p = 15, 40; Xr = rng.normal(size=(n, p)); yr = rng.normal(size=n); lam = 0.3; xs = rng.normal(size=p)
b_primal = np.linalg.solve(Xr.T @ Xr + lam * np.eye(p), Xr.T @ yr)
b_dual = Xr.T @ np.linalg.solve(Xr @ Xr.T + lam * np.eye(n), yr)
check("push_through_identity", np.allclose(b_primal, b_dual))
check("kernel_ridge_prediction", abs(xs @ b_primal - (Xr @ xs) @ np.linalg.solve(Xr @ Xr.T + lam * np.eye(n), yr)) < 1e-10)
# λ=0：p>n 列滿秩時 X^T(XX^T)^{-1}y 是最小範數解，XᵀX 不可逆
b0 = Xr.T @ np.linalg.solve(Xr @ Xr.T, yr)
check("lambda0_min_norm", np.allclose(b0, np.linalg.pinv(Xr) @ yr) and np.linalg.matrix_rank(Xr.T @ Xr) == n)
# p<n 時 XX^T 奇異
Xt = rng.normal(size=(30, 4))
check("XXt_singular_when_p_lt_n", np.linalg.matrix_rank(Xt @ Xt.T) == 4)

# 10. dual PCA：置中後 XX^T 的特徵向量換回載荷
Xp = rng.normal(size=(12, 30)); Xc = Xp - Xp.mean(0)
lam_u, U = np.linalg.eigh(Xc @ Xc.T); lam_v, V = np.linalg.eigh(Xc.T @ Xc)
nz_u = np.sort(lam_u[lam_u > 1e-9])[::-1]; nz_v = np.sort(lam_v[lam_v > 1e-9])[::-1]
check("same_nonzero_eigs", len(nz_u) == 11 and np.allclose(nz_u, nz_v), f"非零個數 {len(nz_u)}（置中後秩 n-1）")
u1 = U[:, -1]; l1 = lam_u[-1]; v1 = Xc.T @ u1 / math.sqrt(l1)
check("loading_unit_norm", abs(np.linalg.norm(v1) - 1) < 1e-10)
check("loading_is_top_eigvec", abs(abs(v1 @ V[:, -1]) - 1) < 1e-10)
check("scores_equal_sqrt_lambda_u", np.allclose(Xc @ v1, math.sqrt(l1) * u1))

# 11. C 增大 → 總 hinge 不增、‖w‖ 不減（固定資料）
prev_H, prev_R = None, None
for Cv in (0.01, 0.1, 1, 10):
    m = SVC(kernel="linear", C=Cv, tol=1e-8).fit(Xs, ys)
    H = np.maximum(0, 1 - ys * m.decision_function(Xs)).sum(); R = np.linalg.norm(m.coef_[0])
    if prev_H is not None:
        check(f"C{Cv}_hinge_nonincreasing", H <= prev_H + 1e-4, f"H={H:.4f}")
        check(f"C{Cv}_norm_nondecreasing", R >= prev_R - 1e-4, f"‖w‖={R:.4f}")
    prev_H, prev_R = H, R

# 12. primal/dual 變數與限制計數（講義 p.17–18）
p_, n_ = 7, 50
check("hard_counts", (p_ + 1, n_) == (8, 50) and (n_, n_ + 1) == (50, 51))
check("soft_counts", (p_ + 1 + n_, 2 * n_) == (58, 100) and (n_, 2 * n_ + 1) == (50, 101))

print(f"\n{ok} 項 PASS")
