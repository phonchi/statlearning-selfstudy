import numpy as np
import statsmodels.api as sm
from ISLP import load_data

Auto = load_data("Auto")
X = sm.add_constant(Auto[["horsepower"]].to_numpy())
y = Auto["mpg"].to_numpy()
fit = sm.OLS(y, X).fit()
x0 = np.array([1.0, 100.0])
mu0 = x0 @ fit.params

# 固定 X、獨立且同變異誤差的殘差 bootstrap。
leverage = fit.get_influence().hat_matrix_diag
residual = fit.resid / np.sqrt(1 - leverage)
residual = residual - residual.mean()
rng = np.random.default_rng(0)
B = 1000
mean_draws = np.empty(B)
prediction_errors = np.empty(B)
for b in range(B):
    y_star = X @ fit.params + rng.choice(residual, len(y), replace=True)
    fit_star = sm.OLS(y_star, X).fit()
    mean_draws[b] = x0 @ fit_star.params
    new_error = rng.choice(residual)
    prediction_errors[b] = mu0 - mean_draws[b] + new_error

print("100 horsepower 的平均預測", mu0)
print("平均曲線的近似 percentile CI",
      np.quantile(mean_draws, [0.025, 0.975]))
print("新車 mpg 的近似 prediction interval",
      mu0 + np.quantile(prediction_errors, [0.025, 0.975]))
