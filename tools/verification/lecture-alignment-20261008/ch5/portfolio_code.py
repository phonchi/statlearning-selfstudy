import numpy as np
from ISLP import load_data

Portfolio = load_data("Portfolio")
xy = Portfolio[["X", "Y"]].to_numpy()

def alpha(data):
    cov = np.cov(data, rowvar=False, ddof=1)
    denominator = cov[0, 0] + cov[1, 1] - 2 * cov[0, 1]
    if denominator <= 0:
        raise ValueError("X-Y 沒有變異，最小風險權重無法唯一決定")
    return (cov[1, 1] - cov[0, 1]) / denominator

rng = np.random.default_rng(0)
B = 1000
estimates = np.empty(B)
for b in range(B):
    index = rng.choice(len(xy), size=len(xy), replace=True)
    estimates[b] = alpha(xy[index])  # X、Y 必須用同一組索引

estimate = alpha(xy)
se = estimates.std(ddof=1)
q05, q95 = np.quantile(estimates, [0.05, 0.95])
print("估計權重與 bootstrap SE", estimate, se)
print("90% percentile CI", q05, q95)
print("90% basic CI", 2 * estimate - q95, 2 * estimate - q05)
