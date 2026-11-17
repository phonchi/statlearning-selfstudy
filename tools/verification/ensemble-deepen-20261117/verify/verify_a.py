"""分支 A（why、bagging、rf、importance）的數字核算，純標準函式庫。"""
import math
from math import comb
ok = bad = 0
def chk(name, got, want, tol=5e-3):
    global ok, bad
    good = abs(got - want) <= tol * max(1, abs(want))
    ok += good; bad += not good
    print('PASS' if good else 'FAIL', name, round(got, 6), 'vs', want)

chk('OOB n=20', (1 - 1/20) ** 20, 0.3585)
chk('OOB n=100', (1 - 1/100) ** 100, 0.3660)
chk('OOB n=1000', (1 - 1/1000) ** 1000, 0.3677)
chk('1/e', math.exp(-1), 0.3679)
chk('bootstrap 含相異觀測比例 ≈ 63%', 1 - math.exp(-1), 0.632)
chk('軟投票 0.51/0.52/0.01 平均', (0.51 + 0.52 + 0.01) / 3, 0.347)
chk('quiz 0.9/0.45/0.45 平均 > 0.5', (0.9 + 0.45 + 0.45) / 3, 0.6)
chk('Heart 看不到指定變數的分裂比例 9/13', 9 / 13, 0.692)
chk('sqrt(13)≈4', round(math.sqrt(13)), 4)
# ESL 圖 15.7：p 個變數中 2 個有用、每次抽 m=floor(sqrt(p)) 個，至少抽到一個有用的機率
def hyp(j, noise):
    p = j + noise; m = int(math.floor(math.sqrt(p)))
    return 1 - comb(noise, m) / comb(p, m)
for noise, want in [(5, 0.524), (25, 0.342), (50, 0.253), (100, 0.187), (150, 0.152)]:
    chk(f'ESL 15.7 j=2 noise={noise}', hyp(2, noise), want)
chk('ESL 15.7 j=6 noise=100', hyp(6, 100), 0.457)
# ESL §8.7 反例：單一分類器錯誤率 0.6，多數決 → 1.0
M = 1001
chk('0-1 損失反例：多數決判 0 的機率', sum(comb(M, k) * 0.6**k * 0.4**(M-k) for k in range(M//2 + 1, M + 1)), 1.0, 1e-6)
# lab bagging B=100 → 500
chk('bagging MSE 14.63 → 14.61', 14.634700151315787 - 14.605662565263161, 0.029, 0.05)
print(f'{ok} PASS, {bad} FAIL')
raise SystemExit(bad > 0)
