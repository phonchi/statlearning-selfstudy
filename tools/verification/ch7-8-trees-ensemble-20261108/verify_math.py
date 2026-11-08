#!/usr/bin/env python3
"""獨立核算第 7、8 章本次新增的數字與論斷。純 Python 標準函式庫，固定種子。

用法：python3 verify_math.py   （全部 PASS 才算過）
"""
import itertools
import math
import random

OK = True


def check(name, cond, detail=""):
    global OK
    OK &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def lpmf(k, n, p):
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
            + k * math.log(p) + (n - k) * math.log(1 - p))


def tail(n, p, k0):
    return sum(math.exp(lpmf(k, n, p)) for k in range(k0, n + 1))


def Phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


# ── 1. 多數決的精確機率（motive 正文、收合與元件卡片） ──────────────────
gt = tail(1000, .51, 501)
ge = tail(1000, .51, 500)
check("M=1000 嚴格過半 72.6%", round(gt * 100, 1) == 72.6, f"{gt:.5f}")
check("M=1000 平手擲硬幣 73.6%", round((gt + ge) / 2 * 100, 1) == 73.6, f"{(gt + ge) / 2:.5f}")
check("M=1000 平手算答對 74.7%", round(ge * 100, 1) == 74.7, f"{ge:.5f}")
a1001 = tail(1001, .51, 501)
check("M=1001 為 73.7%", round(a1001 * 100, 1) == 73.7, f"{a1001:.5f}")
a10001 = tail(10001, .51, 5001)
check("M=10001 為 97.7%", round(a10001 * 100, 1) == 97.7, f"{a10001:.5f}")
b1001 = tail(1001, .49, 501)
check("p=0.49、M=1001 為 26.3%", round(b1001 * 100, 1) == 26.3, f"{b1001:.5f}")
check("p=0.5、奇數 M 正確率恆為 1/2", abs(tail(101, .5, 51) - .5) < 1e-12)
# 常態近似 Φ(√M (p−½)/√(p(1−p)))
z1, z2 = math.sqrt(1000) * .01 / math.sqrt(.51 * .49), math.sqrt(10000) * .01 / math.sqrt(.51 * .49)
check("常態近似 M=1000：z≈0.63、Φ≈73.6%", abs(z1 - .63) < .005 and round(Phi(z1) * 100, 1) == 73.6,
      f"z={z1:.4f} Φ={Phi(z1):.4f}")
check("常態近似 M=10000：z≈2.0、Φ≈97.7%", abs(z2 - 2.0) < .005 and round(Phi(z2) * 100, 1) == 97.7,
      f"z={z2:.4f} Φ={Phi(z2):.4f}")
# Hoeffding：p>½ 時答錯機率 ≤ exp(−2M(p−½)²)；p<½ 時答對機率 ≤ exp(−2M(½−p)²)
ok = True
for M in (11, 101, 1001, 10001):
    for p in (.51, .55, .6, .7):
        ok &= (1 - tail(M, p, (M + 1) // 2)) <= math.exp(-2 * M * (p - .5) ** 2) + 1e-12
        q = 1 - p
        ok &= tail(M, q, (M + 1) // 2) <= math.exp(-2 * M * (.5 - q) ** 2) + 1e-12
check("Hoeffding 兩個方向的上界都成立", ok)

# ── 2. 相關平均的變異 ρσ² + (1−ρ)σ²/B（蒙地卡羅） ─────────────────────
rng = random.Random(20261108)
rho, B, reps = .5, 20, 40000
vals = []
for _ in range(reps):
    c = rng.gauss(0, 1)
    xs = [math.sqrt(rho) * c + math.sqrt(1 - rho) * rng.gauss(0, 1) for _ in range(B)]
    vals.append(sum(xs) / B)
m = sum(vals) / reps
v = sum((x - m) ** 2 for x in vals) / (reps - 1)
check("ρ=0.5、B=20 的平均變異 ≈ 0.525", abs(v - (rho + (1 - rho) / B)) < .015, f"模擬 {v:.4f}")
check("ρ=0.5、B=100 元件數值 0.505", abs(rho + (1 - rho) / 100 - .505) < 1e-12)

# ── 3. Gini／交叉熵的 70/30 算例 ──────────────────────────────────────
def gini(a, b):
    p = a / (a + b)
    return 1 - p * p - (1 - p) ** 2


def ent(a, b):
    p = a / (a + b)
    return -sum(x * math.log(x) for x in (p, 1 - p) if x > 0)


def err(a, b):
    return min(a, b) / (a + b)


par = (70, 30)
s1 = [(35, 15), (35, 15)]
s2 = [(40, 10), (30, 20)]


def w(f, s):
    n = sum(a + b for a, b in s)
    return sum((a + b) / n * f(a, b) for a, b in s)


check("父節點 E=0.30、G=0.42", abs(err(*par) - .3) < 1e-12 and abs(gini(*par) - .42) < 1e-12)
check("分法一：E 0.30、G 0.42、D 0.611", abs(w(err, s1) - .3) < 1e-12 and abs(w(gini, s1) - .42) < 1e-12
      and round(w(ent, s1), 3) == .611)
check("分法二：E 0.30、G 0.40、D 0.587（以 e 為底）",
      abs(w(err, s2) - .3) < 1e-12 and abs(w(gini, s2) - .40) < 1e-12 and round(w(ent, s2), 3) == .587,
      f"D={w(ent, s2):.4f}")
check("分法二子節點 Gini 0.32、0.48", abs(gini(40, 10) - .32) < 1e-12 and abs(gini(30, 20) - .48) < 1e-12)

# ── 4. weakest-link 算例：窮舉所有剪枝子樹 ─────────────────────────────
# 子樹：(RSS, 葉數)
subtrees = {"T0": (10 + 18, 4), "剪A": (16 + 18, 3), "剪B": (10 + 22, 3), "剪AB": (16 + 22, 2), "根": (60, 1)}
inner = {"T0": {"根", "A", "B"}, "剪A": {"根", "B"}, "剪B": {"根", "A"}, "剪AB": {"根"}, "根": set()}
check("g(A)=6、g(B)=4、g(根)=32/3", (16 - 10) / 1 == 6 and (22 - 18) / 1 == 4 and abs((60 - 28) / 3 - 32 / 3) < 1e-12)
check("剪 B 後根的 g 重算為 14", (60 - (10 + 22)) / (3 - 1) == 14)
check("最後一步 α₃=22", (60 - 38) / (2 - 1) == 22)
best_seq, prev = [], None
breaks = []
grid = [i / 100 for i in range(0, 3001)]
for al in grid:
    cost = {k: r + al * L for k, (r, L) in subtrees.items()}
    mn = min(cost.values())
    best = min((k for k in cost if abs(cost[k] - mn) < 1e-9), key=lambda k: subtrees[k][1])
    if best != prev:
        breaks.append(al)
        best_seq.append(best)
        prev = best
check("最佳子樹序列 T0→剪B→剪AB→根，斷點 4、6、22",
      best_seq == ["T0", "剪B", "剪AB", "根"] and breaks[1:] == [4.0, 6.0, 22.0], f"{best_seq} {breaks}")
check("序列巢狀（內部節點集合遞減）",
      all(inner[best_seq[i + 1]] <= inner[best_seq[i]] for i in range(len(best_seq) - 1)))
lines = [(100, 6), (110, 4), (130, 2)]
b1 = (110 - 100) / (6 - 4)
b2 = (130 - 110) / (4 - 2)
check("下包絡的斷點 α=5、10", b1 == 5 and b2 == 10)
# 巢狀性質：對所有對祖先封閉的內部節點集合，在隨機 d_t 下檢查最佳解巢狀
rng = random.Random(7)
parent = {1: None, 2: 1, 3: 1, 4: 2, 5: 2, 6: 3, 7: 3}  # 7 個內部節點的完全二元樹


def closed(S):
    return all(parent[t] is None or parent[t] in S for t in S)


family = [set(c) for r in range(0, 8) for c in itertools.combinations(parent, r) if closed(set(c))]
ok = True
for _ in range(300):
    d = {t: rng.uniform(0, 10) for t in parent}
    prevS = None
    for al in [i / 10 for i in range(0, 120)]:
        val = lambda S: sum(al - d[t] for t in S)  # noqa: E731
        mn = min(val(S) for S in family)
        S = min((S for S in family if abs(val(S) - mn) < 1e-9), key=len)
        if prevS is not None:
            ok &= S <= prevS
        prevS = S
check("隨機 d_t 下最佳子樹隨 α 巢狀（300 組）", ok)

# ── 5. 類別分割數 ───────────────────────────────────────────────────────
levels = "ABCD"
parts = set()
for r in range(1, 4):
    for c in itertools.combinations(levels, r):
        left = frozenset(c)
        parts.add(frozenset([left, frozenset(levels) - left]))
ovr = {frozenset([frozenset(x), frozenset(levels) - frozenset(x)]) for x in levels}
check("4 個水準有 2^(4−1)−1=7 種二分法", len(parts) == 7 == 2 ** 3 - 1)
check("one-versus-rest 只有 4 種且漏掉 {A,B}|{C,D}",
      len(ovr) == 4 and frozenset([frozenset("AB"), frozenset("CD")]) not in ovr)

# ── 6. 貪婪搜尋的盲點：Y = X₁X₂ ────────────────────────────────────────
rng = random.Random(11)
n = 4000
X = [(rng.uniform(-1, 1), rng.uniform(-1, 1)) for _ in range(n)]
Y = [a * b + rng.gauss(0, .05) for a, b in X]


def rss(ys):
    if not ys:
        return 0.0
    mu = sum(ys) / len(ys)
    return sum((y - mu) ** 2 for y in ys)


tot = rss(Y)
best1 = 0.0
for j in (0, 1):
    order = sorted(range(n), key=lambda i: X[i][j])
    ys = [Y[i] for i in order]
    pre, pre2 = [0.0], [0.0]
    for y in ys:
        pre.append(pre[-1] + y)
        pre2.append(pre2[-1] + y * y)
    for k in range(20, n - 20):
        l = pre2[k] - pre[k] ** 2 / k
        r = (pre2[n] - pre2[k]) - (pre[n] - pre[k]) ** 2 / (n - k)
        best1 = max(best1, tot - l - r)
quad = [[Y[i] for i in range(n) if (X[i][0] < 0) == s and (X[i][1] < 0) == u] for s in (0, 1) for u in (0, 1)]
gain2 = tot - sum(rss(q) for q in quad)
check("單一刀的 RSS 降幅 < 1%，四象限（3 刀）降幅 > 50%",
      best1 / tot < .01 and gain2 / tot > .5, f"一刀 {best1 / tot:.4f}，三刀 {gain2 / tot:.3f}")

# 完全對稱的四點：任何單一刀的 RSS 降幅恰為 0
pts = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
ys4 = [a * b for a, b in pts]
gains = []
for j in (0, 1):
    left = [y for (x, y) in zip(pts, ys4) if x[j] < 0]
    right = [y for (x, y) in zip(pts, ys4) if x[j] >= 0]
    gains.append(rss(ys4) - rss(left) - rss(right))
check("對稱四點 Y=X₁X₂：單一刀降幅恰為 0", all(abs(g) < 1e-12 for g in gains), str(gains))

# ── 7. 局部直線在邊界的等價權重可為負 ─────────────────────────────────
xs = [i / 20 for i in range(21)]
x0, h = 0.0, 0.5


def tricube(u):
    return (1 - abs(u) ** 3) ** 3 if abs(u) < 1 else 0.0


wts = [tricube((x - x0) / h) for x in xs]
s0 = sum(wts)
s1 = sum(wv * (x - x0) for wv, x in zip(wts, xs))
s2 = sum(wv * (x - x0) ** 2 for wv, x in zip(wts, xs))
eq = [wv * (s2 - s1 * (x - x0)) / (s0 * s2 - s1 * s1) for wv, x in zip(wts, xs)]
check("邊界點 x₀=0 的局部直線等價權重總和為 1、有負值",
      abs(sum(eq) - 1) < 1e-12 and min(eq) < 0, f"最小 {min(eq):.4f}")

print("\n全部通過" if OK else "\n有失敗")
raise SystemExit(0 if OK else 1)
