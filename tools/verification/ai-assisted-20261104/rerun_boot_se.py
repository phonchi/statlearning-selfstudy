"""Re-run Ch05-resample-lab-zh.ipynb bootstrap cells 59, 65, 67, 71, 75 verbatim (ISLP 0.4.0).

The saved notebook has no output for cells 71 and 75, and its markdown cell 72
states 0.73 / 0.00609 while the ISLP book prints 0.8488 / 0.0074.  Variant B
repeats the same bootstrap with positional row sampling, because Auto's index is
car names (duplicated), so ``D.loc[labels]`` can return more than n rows.
Run:  python3 -m venv --system-site-packages ENV && ENV/bin/pip install --no-deps ISLP==0.4.0 statsmodels patsy tqdm
      ENV/bin/python rerun_boot_se.py > outputs.json 2> run.log
"""
import json, platform, sys
from functools import partial
import numpy as np, pandas as pd, statsmodels.api as sm, sklearn
from sklearn.base import clone
from ISLP import load_data
from ISLP.models import ModelSpec as MS, summarize, poly
from tqdm import trange
import ISLP

out = {"python": sys.version.split()[0], "platform": platform.platform(),
       "numpy": np.__version__, "pandas": pd.__version__, "statsmodels": sm.__version__ if hasattr(sm,'__version__') else None,
       "sklearn": sklearn.__version__, "ISLP": getattr(ISLP, "__version__", "0.4.0 (pinned)")}

# cell 13
Auto = load_data('Auto')
out["shape"] = Auto.shape
out["index_unique"] = bool(Auto.index.is_unique)
out["n_duplicate_labels"] = int(Auto.index.duplicated(keep=False).sum())

# cell 59 (verbatim)
def boot_SE(func, D, n=None, B=1000, seed=0):
    rng = np.random.default_rng(seed)
    first_, second_ = 0, 0
    n = n or D.shape[0]
    for _ in trange(B):
        idx = rng.choice(D.index, n, replace=True)
        value = func(D, idx)
        first_ += value
        second_ += value**2
    return np.sqrt(second_ / B - (first_ / B)**2)

# cell 65 (verbatim)
def boot_OLS(model_matrix, response, D, idx):
    idx = np.asarray(idx)
    if np.issubdtype(idx.dtype, np.integer):
        D_ = D.iloc[idx]
    else:
        D_ = D.loc[idx]
    Y_ = D_[response]
    X_ = clone(model_matrix).fit_transform(D_)
    return sm.OLS(Y_, X_).fit().params

# diagnostic: how many rows does one label-based resample really contain?
rng = np.random.default_rng(10)
lab = rng.choice(Auto.index, Auto.shape[0], replace=True)
out["rows_in_one_label_resample"] = int(Auto.loc[lab].shape[0])

# cell 67, 71 (verbatim)
hp_func = partial(boot_OLS, MS(['horsepower']), 'mpg')
hp_se = boot_SE(hp_func, Auto, B=1000, seed=10)
out["A_cell71_hp_se"] = hp_se.round(6).to_dict()

# cell 75 (verbatim; seed defaults to 0)
quad_model = MS([poly('horsepower', 2, raw=True)])
quad_func = partial(boot_OLS, quad_model, 'mpg')
out["A_cell75_quad_se"] = boot_SE(quad_func, Auto, B=1000).round(6).to_dict()

# Variant B: same code, but rows drawn by position (integer index -> iloc in boot_OLS)
AutoB = Auto.reset_index(drop=True)
out["B_positional_hp_se"] = boot_SE(hp_func, AutoB, B=1000, seed=10).round(6).to_dict()
out["B_positional_quad_se"] = boot_SE(quad_func, AutoB, B=1000).round(6).to_dict()

# formula SEs (cells 73, 77) for comparison, unrounded
out["formula_hp_se"] = sm.OLS(Auto['mpg'], MS(['horsepower']).fit_transform(Auto)).fit().bse.round(6).to_dict()
out["formula_quad_se"] = sm.OLS(Auto['mpg'], quad_model.fit_transform(Auto)).fit().bse.round(6).to_dict()

print(json.dumps(out, indent=2, ensure_ascii=False))
