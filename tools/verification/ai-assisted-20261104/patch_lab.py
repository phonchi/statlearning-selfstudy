"""Fix Ch05 lab cell 59 (positional bootstrap draws), correct cell 72, and store
outputs for cells 61, 71, 75 computed with the fixed code.  Usage:
  ENV/bin/python patch_lab.py /path/to/Ch05-resample-lab-zh.ipynb
"""
import json, sys
from functools import partial
import numpy as np, statsmodels.api as sm
from sklearn.base import clone
from ISLP import load_data
from ISLP.models import ModelSpec as MS, poly

path = sys.argv[1]
raw = open(path, encoding="utf-8").read()
nb = json.loads(raw)
cells = nb["cells"]

OLD59 = '        idx = rng.choice(D.index,\n'
assert OLD59 in cells[59]["source"], "cell 59 changed unexpectedly"
i = cells[59]["source"].index(OLD59)
cells[59]["source"][i:i + 1] = [
    '        # 依「列的位置」抽樣：Auto 的 index 是車名且有重複，\n',
    '        # 若用 D.index 抽標籤，D.loc 會把同名的車一次全部取出，重抽樣本會多於 n 列\n',
    '        idx = rng.choice(D.shape[0],\n',
]

OLD72 = "這表示 ${\\rm SE}(\\hat{\\beta}_0)$ 的 bootstrap 估計為 0.73，而 ${\\rm SE}(\\hat{\\beta}_1)$ 的 bootstrap 估計為 0.00609。"
NEW72 = "這表示 ${\\rm SE}(\\hat{\\beta}_0)$ 的 bootstrap 估計為 0.85，而 ${\\rm SE}(\\hat{\\beta}_1)$ 的 bootstrap 估計為 0.0074。"
src72 = "".join(cells[72]["source"])
assert OLD72 in src72, "cell 72 text changed unexpectedly"
cells[72]["source"] = [l for l in src72.replace(OLD72, NEW72).splitlines(keepends=True)]

# --- recompute with the fixed cell 59 ---
from tqdm import trange
def boot_SE(func, D, n=None, B=1000, seed=0):
    rng = np.random.default_rng(seed)
    first_, second_ = 0, 0
    n = n or D.shape[0]
    for _ in trange(B):
        idx = rng.choice(D.shape[0], n, replace=True)
        value = func(D, idx)
        first_ += value
        second_ += value**2
    return np.sqrt(second_ / B - (first_ / B)**2)

def alpha_func(D, idx):
    cov_ = np.cov(D[['X','Y']].loc[idx], rowvar=False)
    return ((cov_[1,1] - cov_[0,1]) / (cov_[0,0]+cov_[1,1]-2*cov_[0,1]))

def boot_OLS(model_matrix, response, D, idx):
    idx = np.asarray(idx)
    if np.issubdtype(idx.dtype, np.integer):
        D_ = D.iloc[idx]
    else:
        D_ = D.loc[idx]
    Y_ = D_[response]
    X_ = clone(model_matrix).fit_transform(D_)
    return sm.OLS(Y_, X_).fit().params

Portfolio, Auto = load_data('Portfolio'), load_data('Auto')
alpha_SE = boot_SE(alpha_func, Portfolio, B=1000, seed=0)
hp_func = partial(boot_OLS, MS(['horsepower']), 'mpg')
hp_se = boot_SE(hp_func, Auto, B=1000, seed=10)
quad_model = MS([poly('horsepower', 2, raw=True)])
quad_func = partial(boot_OLS, quad_model, 'mpg')
quad_se = boot_SE(quad_func, Auto, B=1000)

def result(text):
    return [{"output_type": "execute_result", "metadata": {}, "execution_count": None,
             "data": {"text/plain": text.splitlines(keepends=True)}}]

for k, v in [(61, repr(alpha_SE)), (71, repr(hp_se)), (75, repr(quad_se))]:
    assert cells[k]["cell_type"] == "code" and cells[k]["outputs"] == [], k
    cells[k]["outputs"] = result(v)
    print(f"cell {k}:\n{v}\n")

open(path, "w", encoding="utf-8").write(json.dumps(nb, ensure_ascii=False, separators=(",", ":")))

# --- 2026-11-04 follow-up (review): cell 53 alpha_func indexes by position too ---
# Applied separately by patch_alpha_iloc.py after check_alpha_iloc.py confirmed
# cells 55, 57 and 61 keep their saved outputs.
