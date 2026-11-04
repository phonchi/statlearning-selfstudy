"""Cell 53 alpha_func with .iloc: cells 55, 57, 61 must keep their outputs."""
import json, numpy as np
from ISLP import load_data
P = load_data('Portfolio')
f = lambda D, idx: (lambda c: (c[1,1]-c[0,1])/(c[0,0]+c[1,1]-2*c[0,1]))(np.cov(D[['X','Y']].iloc[idx], rowvar=False))
def boot_SE(func, D, n=None, B=1000, seed=0):
    rng = np.random.default_rng(seed); a = b = 0; n = n or D.shape[0]
    for _ in range(B):
        v = func(D, rng.choice(D.shape[0], n, replace=True)); a += v; b += v**2
    return np.sqrt(b/B - (a/B)**2)
rng = np.random.default_rng(0)
print(json.dumps({"cell55": float(f(P, range(100))), "cell57": float(f(P, rng.choice(100, 100, replace=True))),
                  "cell61": float(boot_SE(f, P, B=1000, seed=0))}))
