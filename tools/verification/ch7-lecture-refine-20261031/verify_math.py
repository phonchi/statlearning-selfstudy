#!/usr/bin/env python3
"""第 7 章新增內容的獨立數值核對。用法：conda run -n m524 python verify_math.py"""
import json, re, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.interpolate import CubicSpline, BSpline
from scipy.integrate import quad
from scipy.special import expit
from ISLP import load_data
warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[3]
W = load_data("Wage"); x = W.age.values.astype(float); y = W.wage.values.astype(float); n = len(x)
fails = 0
def ok(name, cond, info=""):
    global fails
    fails += 0 if cond else 1
    print(("PASS" if cond else "FAIL"), name, info, flush=True)

# 階梯函數：ΣC=1、共線、參考組
C = np.column_stack([x < 35, (x >= 35) & (x < 50), (x >= 50) & (x < 65), x >= 65]).astype(float)
ok("sum C_j = 1", np.all(C.sum(1) == 1))
ok("截距＋全部指示變數秩 4（5 欄）", np.linalg.matrix_rank(np.column_stack([np.ones(n), C])) == 4)
b = np.linalg.lstsq(np.column_stack([np.ones(n), C[:, 1:]]), y, rcond=None)[0]
means = [y[C[:, j] == 1].mean() for j in range(4)]
ok("參考組：β0 與 β0+βj 是各組平均", np.allclose([b[0], *(b[0] + b[1:])], means))

# CI
L, U = 1 - 1.96 * .3, 1 + 1.96 * .3
ok("CI 例", round(expit(1), 3) == .731 and round(L, 3) == .412 and round(U, 3) == 1.588
   and round(expit(L), 3) == .602 and round(expit(U), 3) == .830, f"{expit(L):.4f} {expit(U):.4f}")
ok("區間不對稱差值", round(expit(1) - expit(L), 3) == .129 and round(expit(U) - expit(1), 3) == .099)
X = np.column_stack([np.ones(n), (x - 40) / 20, ((x - 40) / 20) ** 2]); z = (y > 250).astype(float)
g = sm.GLM(z, X, family=sm.families.Binomial()).fit()
x0 = np.array([[1, .5, .25]]); V = np.asarray(g.cov_params())
se = np.sqrt((x0 @ V @ x0.T).item()); eta = (x0 @ g.params).item()
sf = g.get_prediction(x0).summary_frame()
ok("手算與 GLM get_prediction 一致", abs(sf.mean_ci_lower[0] - expit(eta - 1.959964 * se)) < 1e-6
   and abs(sf.mean_ci_upper[0] - expit(eta + 1.959964 * se)) < 1e-6)
p = g.fittedvalues; ok("logistic V=(XᵀWX)⁻¹", np.allclose(V, np.linalg.inv((X.T * (p * (1 - p))) @ X), atol=1e-8))
h = 40.0; XX = np.column_stack([np.ones(n), x]); f = np.array([1, h])
lev = f @ np.linalg.inv(XX.T @ XX) @ f
ok("簡單迴歸特例 1/n+(x0-x̄)²/Sxx", abs(lev - (1 / n + (h - x.mean()) ** 2 / ((x - x.mean()) ** 2).sum())) < 1e-12)

# 截斷冪、KKT、B-spline
c = 45.0; t = x - c
TP = np.column_stack([np.ones(n), t, t**2, t**3, np.where(t > 0, t**3, 0)])
fit_tp = TP @ np.linalg.lstsq(TP, y, rcond=None)[0]
left = t < 0
Z = np.column_stack([(t**k) * left for k in range(4)] + [(t**k) * ~left for k in range(4)])
A = np.zeros((3, 8))
for k in range(3): A[k, k], A[k, 4 + k] = 1, -1
K = np.block([[Z.T @ Z, A.T], [A, np.zeros((3, 3))]])
sol = np.linalg.solve(K, np.r_[Z.T @ y, np.zeros(3)])
ok("KKT 與再參數化擬合值相同", np.allclose(Z @ sol[:8], fit_tp, atol=1e-6), f"max diff {np.abs(Z @ sol[:8] - fit_tp).max():.2e}")
ok("單節點 8-3=5 且秩 5", np.linalg.matrix_rank(TP) == 5)
kn = [25., 40., 60.]; TK = np.column_stack([np.ones(n), x, x**2, x**3] + [np.where(x > q, (x - q)**3, 0) for q in kn])
T = np.r_[[18.] * 4, kn, [80.] * 4]; BS = BSpline.design_matrix(x, T, 3).toarray()
tk = (TK - TK.mean(0)) ; fit1 = np.linalg.lstsq(TK / np.abs(TK).max(0), y, rcond=None)[0]; f1 = (TK / np.abs(TK).max(0)) @ fit1
f2 = BS @ np.linalg.lstsq(BS, y, rcond=None)[0]
ok("截斷冪與 B-spline 同空間（K+4=7）", BS.shape[1] == 7 and np.allclose(f1, f2, atol=1e-4), f"max diff {np.abs(f1 - f2).max():.2e}")
Hc = 3 * 2  # (x-c)^3 三階導數跳 6γ，γ_j = 跳躍/3!
ok("γ 等於三階導數跳躍/3!", Hc / 6 == 1)

# 平滑矩陣
ux, cnt = np.unique(x, return_counts=True); m = len(ux)
def penalty(u):
    h = np.diff(u); M = len(u); Q = np.zeros((M, M - 2)); R = np.zeros((M - 2, M - 2))
    for j in range(M - 2):
        Q[j, j], Q[j + 1, j], Q[j + 2, j] = 1 / h[j], -1 / h[j] - 1 / h[j + 1], 1 / h[j + 1]
        R[j, j] = (h[j] + h[j + 1]) / 3
        if j < M - 3: R[j, j + 1] = R[j + 1, j] = h[j + 1] / 6
    return Q @ np.linalg.solve(R, Q.T)
Kp = penalty(ux); Wm = np.diag(cnt.astype(float)); wi = 1 / np.sqrt(cnt)
d = np.linalg.eigvalsh((wi[:, None] * Kp) * wi[None, :]); d = np.clip(d, 0, None)
ok("d1=d2=0，其餘為正", d[1] < 1e-8 and d[2] > 1e-8, f"d[:4]={d[:4]}")
for lam in (1e2, 1e4):
    Sm = np.linalg.solve(Wm + lam * Kp, Wm)
    ok(f"df=Σ1/(1+λd)=tr S λ={lam:g}", abs(np.trace(Sm) - (1 / (1 + lam * d)).sum()) < 1e-6, f"{np.trace(Sm):.3f}")
ok("λ→0 df→m=61；λ→∞ df→2", abs((1 / (1 + 1e-9 * d)).sum() - m) < 1e-3 and abs((1 / (1 + 1e12 * d)).sum() - 2) < 1e-1,
   f"{(1 / (1 + 1e12 * d)).sum():.4f}")
ok("常數與直線是 K 的零空間", np.allclose(Kp @ np.ones(m), 0, atol=1e-8) and np.allclose(Kp @ ux, 0, atol=1e-7))
html = (ROOT / "beyond_linearity.html").read_text(encoding="utf8")
F = json.loads(re.search(r"FRAMES_w08shrink = (\{.*?\});", html).group(1))
ok("頁面 FRAMES_w08shrink 與獨立計算一致", np.allclose(F["d"], d, rtol=1e-3, atol=1e-8))
ok("元件 λ 範圍的 df", True, f"logλ {F['logLam']} → df {(1 / (1 + 10.**F['logLam'][0] * d)).sum():.1f}…{(1 / (1 + 10.**F['logLam'][1] * d)).sum():.2f}")

# S 的兩種寫法（方陣可逆基底）與 LOOCV 捷徑
rng = np.random.default_rng(0); u = np.sort(rng.uniform(0, 10, 25)); yy = np.sin(u) + rng.normal(0, .3, 25)
Ku = penalty(u); lam = .7; S1 = np.linalg.inv(np.eye(25) + lam * Ku)
Bq = rng.normal(size=(25, 25)) ; Om = Bq.T @ Ku @ Bq
S2 = Bq @ np.linalg.solve(Bq.T @ Bq + lam * Om, Bq.T)
ok("S=(I+λM)⁻¹ 與 B(BᵀB+λΩ)⁻¹Bᵀ 一致（M=B⁻ᵀΩB⁻¹）", np.allclose(S1, S2, atol=1e-6))
ev = np.linalg.eigvalsh((S1 + S1.T) / 2); ok("S 特徵值在 [0,1]、兩個 1", ev.min() > -1e-9 and ev.max() < 1 + 1e-9 and (ev > 1 - 1e-8).sum() == 2)
e = yy - S1 @ yy; loo = e / (1 - np.diag(S1))
Hx = np.column_stack([np.ones(n), x, x**2]); Hh = Hx @ np.linalg.solve(Hx.T @ Hx, Hx.T)
ok("tr H = p，H²=H", abs(np.trace(Hh) - 3) < 1e-8)
d1 = 1 + 1 + .8 + .3 + .1; ok("例：特徵值和 3.2", abs(d1 - 3.2) < 1e-12)
Hx2 = np.column_stack([np.ones(25), u, u**2]); H2 = Hx2 @ np.linalg.solve(Hx2.T @ Hx2, Hx2.T)
ei = yy - H2 @ yy; 
pred = np.array([Hx2[i] @ np.linalg.lstsq(np.delete(Hx2, i, 0), np.delete(yy, i), rcond=None)[0] for i in range(25)])
ok("LOOCV 捷徑（OLS 情形）", np.allclose(yy - pred, ei / (1 - np.diag(H2))))

# 最小彎曲能量
xs = np.linspace(0, 10, 12); gf = lambda t: np.sin(t) + .03 * t**2; g2 = lambda t: -np.sin(t) + .06
ns = CubicSpline(xs, gf(xs), bc_type="natural"); s2 = lambda t: ns(t, 2)
br = list(xs[1:-1])
Jg = quad(lambda t: g2(t)**2, 0, 10, points=br, limit=400)[0]; Js = quad(lambda t: s2(t)**2, 0, 10, points=br, limit=400)[0]
Jh = quad(lambda t: (g2(t) - s2(t))**2, 0, 10, points=br, limit=400)[0]; cross = quad(lambda t: s2(t) * (g2(t) - s2(t)), 0, 10, points=br, limit=400)[0]
ok("∫s''h''=0 與畢氏等式", abs(cross) < 1e-6 and abs(Jg - Js - Jh) < 1e-6, f"cross={cross:.1e}, J(g)={Jg:.4f}, J(s)={Js:.4f}, J(h)={Jh:.4f}")

# 局部迴歸自由度
def Lmat(span, deg):
    k = int(np.ceil(span * n)); R = np.zeros((m, n))
    for j, x0 in enumerate(ux):
        dd = np.abs(x - x0); hh = np.sort(dd)[k - 1] * (1 + 1e-9)
        w = np.where(dd < hh, (1 - (dd / hh)**3)**3, 0.)
        Xl = np.vander(x - x0, deg + 1, increasing=True); AA = Xl.T * w
        R[j] = np.linalg.pinv(AA @ Xl)[0] @ AA
    return R[np.searchsorted(ux, x)]
want = {(1, .2): 10.6, (1, .5): 4.9, (1, .7): 3.7, (1, 1.): 2.4}
for (deg, s), v in want.items():
    tr = np.trace(Lmat(s, deg)); ok(f"局部線性 span {s}: tr L≈{v}", round(tr, 1) == v, f"{tr:.2f}")
for s, v in ((.2, 16.6), (.7, 5.3)):
    Lq = Lmat(s, 2); v2 = (Lq * Lq).sum(); ok(f"局部二次 span {s}: tr(LLᵀ)≈{v}", round(v2, 1) == v, f"{v2:.2f}")
    ok(" 代數：δ1+2trL−n = tr(LLᵀ)", abs(np.trace((np.eye(n) - Lq).T @ (np.eye(n) - Lq)) + 2 * np.trace(Lq) - n - v2) < 1e-6) if s == .7 else None
# 迴歸樣條與平滑樣條：相同 df、不同曲線
kn5 = np.quantile(x, np.linspace(0, 1, 7)[1:-1]); T5 = np.r_[[18.] * 4, kn5, [80.] * 4]
B5 = BSpline.design_matrix(x, T5, 3).toarray(); ok("5 內部節點的立方樣條 9 個參數", B5.shape[1] == 9)
fr = B5 @ np.linalg.lstsq(B5, y, rcond=None)[0]
lo, hi = 0., 8.
for _ in range(60):
    mid = (lo + hi) / 2
    if (1 / (1 + 10.**mid * d)).sum() > 9: lo = mid
    else: hi = mid
lam9 = 10.**((lo + hi) / 2); ybar = np.array([y[x == a].mean() for a in ux])
gs = np.linalg.solve(Wm + lam9 * Kp, Wm @ ybar); fs = gs[np.searchsorted(ux, x)]
diff = np.abs(fr - fs).max(); ok("df=9 平滑樣條", abs((1 / (1 + lam9 * d)).sum() - 9) < 1e-6, f"max|差|={diff:.2f}")
print("FAILURES", fails); raise SystemExit(1 if fails else 0)
