"""ens_c 用到的每個數字的獨立核算（純標準函式庫）。"""
from itertools import combinations
ok = []
def chk(name, cond): ok.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ') + name)
# 講義 p.72 目標編碼
y = {'Cat': [1, 0, 1], 'Hamster': [0, 1], 'Dog': [0, 0]}
te = {k: sum(v) / len(v) for k, v in y.items()}
chk('TE Cat 0.67', round(te['Cat'], 2) == 0.67); chk('TE Hamster 0.50', te['Hamster'] == 0.5); chk('TE Dog 0', te['Dog'] == 0)
# 極端例一：(y+ap)/(1+a), a=1, p=0.5
chk('greedy TS 0.75/0.25', (1 + .5) / 2 == .75 and (0 + .5) / 2 == .25)
# LOO 5/6 例
n, npos = 11, 6
chk('LOO y=1 -> 0.5', (npos - 1) / (n - 1) == 0.5); chk('LOO y=0 -> 0.6', (npos - 0) / (n - 1) == 0.6)
# rock/indie/pop
seq = [('rock', 0), ('indie', 0), ('rock', 1), ('rock', 1), ('pop', 1), ('indie', 1), ('rock', 0)]
exp = [0.05, 0.05, 0.025, 0.35, 0.05, 0.025, 0.5125]
got = []
for k, (c, yy) in enumerate(seq):
    prev = [v for (cc, v) in seq[:k] if cc == c]
    got.append((sum(prev) + 0.05) / (len(prev) + 1))
chk('ordered TS table ' + str([round(g, 4) for g in got]), all(abs(a - b) < 1e-12 for a, b in zip(got, exp)))
# 類別排序示意
G = {'A': -6, 'B': 2, 'C': -1, 'D': 4}; H = {'A': 3, 'B': 4, 'C': 2, 'D': 2}
order = sorted(G, key=lambda c: -G[c] / H[c]); chk('sorted order D,B,C,A', order == ['D', 'B', 'C', 'A'])
sc = lambda S: sum(G[c] for c in S) ** 2 / sum(H[c] for c in S)
par = sc('ABCD')
gain = lambda L: 0.5 * (sc(L) + sc([c for c in 'ABCD' if c not in L]) - par)
cuts = [round(gain(order[:i]), 2) for i in (1, 2, 3)]
chk('contiguous gains 5.34/7.85/7.52 ' + str(cuts), cuts == [5.34, 7.85, 7.52])
allp = {}
for r in (1, 2):
    for L in combinations('ABCD', r):
        if r == 2 and 'A' not in L: continue
        allp[L] = gain(L)
chk('7 partitions', len(allp) == 7)
best = max(allp, key=allp.get); chk('best partition {A,C}|{B,D} = 7.85', set(best) == {'A', 'C'} and round(allp[best], 2) == 7.85)
chk('2^(k-1)-1 for k=10 is 511', 2 ** 9 - 1 == 511)
# 生長順序示意
chk('growth example totals 12/2.5/13 (+root)', (2 + 10, 2 + .5, 10 + 3) == (12, 2.5, 13))
# GOSS
nn, a, b = 1000, .2, .1
chk('GOSS keep 200 sample 100 weight 8 -> 800', nn * a == 200 and nn * b == 100 and abs((1 - a) / b - 8) < 1e-12 and 100 * 8 == nn * (1 - a))
# 對稱樹
chk('depth 6 oblivious: 64 leaves, 6 conditions', 2 ** 6 == 64)
# DART k=1 eta=0.1
chk('DART 1/(1+0.1)=0.909', round(1 / 1.1, 3) == 0.909 and round(1 / 1.1, 3) == round(1 * 1 / 1.1, 3))
# 速度
t = {'gbc': 624.8339729309082, 'xgb': 24.28720998764038, 'lgb': 13.139190673828125, 'cat': 15.102735042572021}
r = sorted(round(t['gbc'] / t[k], 1) for k in ('xgb', 'lgb', 'cat'))
chk('speedups ~26-48x ' + str(r), r[0] >= 25.5 and r[-1] <= 48)
chk('3197*255 = 815235', 3197 * 255 == 815235)
chk('positive share 26/3815 < 0.7%', 26 / 3815 < .007 and round(3789 / 3815, 3) == .993)
# MAE 範圍
mae = [163165.1377008556, 165007.46639148306, 160827.54657606702, 163529.3517553931, 164721.46472522244,
       164993.47954656056, 166920.94141120723, 168168.9386958123, 166281.68070428775]
chk('MAE spread 4.6%', round((max(mae) - min(mae)) / min(mae) * 100, 1) == 4.6)
# BART 先驗
al, be = .95, 2
ps = lambda d: al * (1 + d) ** -be
p1 = 1 - ps(0); p2 = ps(0) * (1 - ps(1)) ** 2; p3 = ps(0) * 2 * ps(1) * (1 - ps(1)) * (1 - ps(2)) ** 2
chk('BART leaves 1/2/3 = 0.05/0.55/0.28 ' + str((round(p1, 3), round(p2, 3), round(p3, 3))), round(p1, 2) == .05 and round(p2, 2) == .55 and round(p3, 2) == .28)
chk('sigma_mu K=200 k=2 ~ 0.018', round(.5 / (2 * 200 ** .5), 3) == .018)
# stacking lab
chk('stacking 0.81 > members 0.78/0.73/0.79', .81 > max(.78, .73, .79))
print(sum(o for _, o in ok), '/', len(ok), 'PASS')
