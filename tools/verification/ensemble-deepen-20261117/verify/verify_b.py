"""分支 B 的數字核算（純標準函式庫）。逐項列出文字與元件用到的數字並與獨立計算比對。"""
import math, re, sys
ok = 0; bad = 0
def chk(name, got, want, tol=5e-3):
    global ok, bad
    good = abs(got - want) <= tol * max(1, abs(want))
    ok += good; bad += (not good)
    print(('PASS' if good else 'FAIL'), name, round(got, 6), 'vs', want)

# 1. StatQuest XGBoost 第 1 集：殘差 −10.5、6.5、7.5、−7.5，平方損失 g=−r、h=1
r = [-10.5, 6.5, 7.5, -7.5]
def sim(rs, lam): return sum(rs) ** 2 / (len(rs) + lam)
def sq_gain(k, lam): return sim(r[:k], lam) + sim(r[k:], lam) - sim(r, lam)
chk('SQ gain x<15 λ=0', sq_gain(1, 0), 120.33)
chk('SQ gain x<22.5 λ=0', sq_gain(2, 0), 4.0)
chk('SQ gain x<30 λ=0', sq_gain(3, 0), 56.33)
chk('論文式 gain x<15 λ=0', 0.5 * sq_gain(1, 0), 60.17)
chk('左葉 w* λ=0', sum(r[:1]) / (1 + 0), -10.5)
chk('右葉 w* λ=0', sum(r[1:]) / (3 + 0), 2.17)
chk('左葉 w* λ=1', sum(r[:1]) / (1 + 1), -5.25)
chk('SQ gain x<15 λ=1', sq_gain(1, 1), 62.49)
chk('論文式 gain x<15 λ=1', 0.5 * sq_gain(1, 1), 31.24)
chk('第一筆新預測 η=0.3', 0.5 + 0.3 * (-10.5), -2.65)

# 2. logistic 一步 Newton 例：y=(1,1,0)、p=0.5
y = [1, 1, 0]; p = [0.5] * 3
gam = sum(yi - pi for yi, pi in zip(y, p)) / sum(pi * (1 - pi) for pi in p)
chk('一步 Newton 葉值', gam, 0.667)
chk('對應機率', 1 / (1 + math.exp(-gam)), 0.661)
chk('logistic h 最大值 p=0.5', 0.25, 0.25)
chk('min_child_weight=1 在 p=0.5 需要的筆數', 1 / 0.25, 4)
# g、h 的數值微分檢查
def ll(F, yv): q = 1 / (1 + math.exp(-F)); return -(yv * math.log(q) + (1 - yv) * math.log(1 - q))
F0, eps = 0.3, 1e-4; q0 = 1 / (1 + math.exp(-F0))
chk('g = p − y（數值微分）', (ll(F0 + eps, 1) - ll(F0 - eps, 1)) / (2 * eps), q0 - 1, 1e-6)
chk('h = p(1−p)（數值微分）', (ll(F0 + eps, 1) - 2 * ll(F0, 1) + ll(F0 - eps, 1)) / eps ** 2, q0 * (1 - q0), 1e-4)

# 3. AdaBoost：對稱式 η=½ 與 ESL 演算法 10.1 的權重比相同
for e in (0.1, 0.2, 0.35):
    a_half = 0.5 * math.log((1 - e) / e)
    ratio_sym = math.exp(2 * a_half)              # 答錯/答對（對稱更新）
    ratio_esl = math.exp(math.log((1 - e) / e))   # 只放大答錯者
    chk(f'η=½ 權重比 = ESL 10.1（e={e}）', ratio_sym, ratio_esl, 1e-9)
    # 指數損失最小值
    Z = lambda b: (1 - e) * math.exp(-b) + e * math.exp(b)
    chk(f'β 是 Z 的極小（e={e}）', min(Z(a_half - 1e-3), Z(a_half + 1e-3)) - Z(a_half) > 0, 1)

# 4. StatQuest 第 4 集加權分位例
ps = [0.1, 0.1, 0.9, 0.9, 0.6, 0.4]
w = [q * (1 - q) for q in ps]
for got, want in zip(w, [0.09, 0.09, 0.09, 0.09, 0.24, 0.24]): chk('權重 p(1−p)', got, want, 1e-9)
chk('前兩箱 0.18', w[0] + w[1], 0.18, 1e-9); chk('次兩箱 0.18', w[2] + w[3], 0.18, 1e-9)

# 5. 延遲表倍數、提前停止準確率
chk('主記憶體/L1', 100 / 0.5, 200)
chk('提前停止準確率', 1 - 0.15789, 0.8421, 1e-4)

# 6. Lab 輸出逐字核對
from pathlib import Path
_R = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(_R / 'tools/enrich'), str(_R / 'tools')]
from lib import lab_output
for cell, s in [(124, 'Accuracy mean: 0.79'), (130, "{'learning_rate': 0.5}"), (130, '0.79557'),
                (134, "{'max_depth': 3}"), (134, '0.81197'), (138, "{'gamma': 0.1}"), (142, "{'min_child_weight': 4}"),
                (145, "{'subsample': 0.5}"), (145, '0.81536'), (149, "{'colsample_bytree': 0.7}"), (149, '0.80552'),
                (153, "{'n_estimators': 400}"), (153, '0.79541'), (162, 'Accuracy: 84.21%'), (162, '0.15789'),
                (80, '14.481405918831591'), (82, '14.501514553719565'), (113, '624.8339729309082'), (114, '24.28720998764038'),
                (113, '0.9874213836477987'), (114, '0.9913522012578616'), (124, '[0.82 0.75 0.74 0.82 0.8 ]')]:
    good = s in lab_output(8, cell); ok += good; bad += (not good)
    print('PASS' if good else 'FAIL', f'lab 儲存格 {cell} 含 {s}')

# 7. 切點搜尋元件：重算 LCG 資料與三種方法
def lcg(seed):
    st = [seed & 0xffffffff or 1]
    def f():
        st[0] = (st[0] * 1664525 + 1013904223) & 0xffffffff
        return st[0] / 4294967296
    return f
rand = lcg(26117)
xs = sorted(math.floor((0.2 + 9.6 * rand()) * 10 + 0.5) / 10 for _ in range(40))
ys = [1 if rand() < 1 / (1 + math.exp(-1.8 * (x - 4))) else 0 for x in xs]
def probs(mode):
    if mode == 'flat': return [0.5] * 40
    c, a = (6, 1.4) if mode == 'wrong' else (4, 2.2)
    return [1 / (1 + math.exp(-a * (x - c))) for x in xs]
def gain_at(g, h, k):
    G, H, GL, HL = sum(g), sum(h), sum(g[:k]), sum(h[:k])
    return 0.5 * (GL * GL / HL + (G - GL) ** 2 / (H - HL) - G * G / H)
def cands(meth, h, K):
    n = 40; ok_ = lambda k: 0 < k < n and xs[k] > xs[k - 1]
    if meth == 'exact': return [k for k in range(1, n) if ok_(k)]
    wts = h if meth == 'wq' else [1] * n
    tot = sum(wts); acc = 0; j = 1; out = []
    for k in range(n):
        if j >= K: break
        acc += wts[k]
        while j < K and acc >= tot * j / K - 1e-12:
            kk = k + 1
            while kk < n and not ok_(kk): kk += 1
            if kk < n and kk not in out: out.append(kk)
            j += 1
    return out
def run(meth, mode, K):
    p = probs(mode); g = [pi - yi for pi, yi in zip(p, ys)]; h = [pi * (1 - pi) for pi in p]
    c = cands(meth, h, K); gs = [gain_at(g, h, k) for k in c]
    i = max(range(len(gs)), key=lambda t: gs[t]); k = c[i]
    ex = max(gain_at(g, h, kk) for kk in cands('exact', h, K))
    return len(c), (xs[k - 1] + xs[k]) / 2, gs[i], 1 - gs[i] / ex
for args, want in [(('exact', 'mid', 8), (33, 4.55, 3.861, 0)), (('hist', 'mid', 8), (7, 3.75, 2.470, 0.36)),
                   (('wq', 'mid', 8), (6, 4.55, 3.861, 0)), (('wq', 'wrong', 8), (7, 5.55, 1.155, 0.822)),
                   (('hist', 'wrong', 8), (7, 3.75, 6.482, 0)), (('hist', 'flat', 8), (7, 4.95, 12.80, 0.034))]:
    n, bx, bg, loss = run(*args)
    chk(f'{args} 候選數', n, want[0], 0); chk(f'{args} 最佳 x', bx, want[1], 1e-6)
    chk(f'{args} 最佳增益', bg, want[2]); chk(f'{args} 損失比例', loss, want[3], 0.01)
print(f'{ok} PASS, {bad} FAIL'); sys.exit(bool(bad))
