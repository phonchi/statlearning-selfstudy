"""Check a one-line fix to cell 59 (draw row positions) against cells 61 and 69."""
import json
from functools import partial
import numpy as np, statsmodels.api as sm
from sklearn.base import clone
from ISLP import load_data
from ISLP.models import ModelSpec as MS

def boot_SE(func, D, n=None, B=1000, seed=0, positional=False):
    rng = np.random.default_rng(seed)
    first_, second_ = 0, 0
    n = n or D.shape[0]
    for _ in range(B):
        idx = rng.choice(D.shape[0] if positional else D.index, n, replace=True)
        value = func(D, idx)
        first_ += value
        second_ += value**2
    return np.sqrt(second_ / B - (first_ / B)**2)

def alpha_func(D, idx):  # cell 53 of the course lab
    cov_ = np.cov(D[['X','Y']].loc[idx], rowvar=False)
    return ((cov_[1,1] - cov_[0,1]) / (cov_[0,0]+cov_[1,1]-2*cov_[0,1]))

def boot_OLS(model_matrix, response, D, idx):  # cell 65
    idx = np.asarray(idx)
    D_ = D.iloc[idx] if np.issubdtype(idx.dtype, np.integer) else D.loc[idx]
    return sm.OLS(D_[response], clone(model_matrix).fit_transform(D_)).fit().params

Portfolio = load_data('Portfolio'); Auto = load_data('Auto')
out = {"cell55_alpha_all": float(alpha_func(Portfolio, range(100))),
       "cell61_original": float(boot_SE(alpha_func, Portfolio, B=1000, seed=0)),
       "cell61_positional": float(boot_SE(alpha_func, Portfolio, B=1000, seed=0, positional=True))}
hp_func = partial(boot_OLS, MS(['horsepower']), 'mpg')
rng = np.random.default_rng(0)
out["cell69_first_row"] = hp_func(Auto, rng.choice(392, 392, replace=True)).round(8).tolist()
out["cell71_positional"] = boot_SE(hp_func, Auto, B=1000, seed=10, positional=True).round(6).to_dict()
print(json.dumps(out, indent=2))
