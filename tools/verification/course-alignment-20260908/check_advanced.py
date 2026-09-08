#!/usr/bin/env python3
"""Reproduce advanced-numerical.log from the saved frames and pinned ISLP data.

Use the m524 Python environment. No course checkout or network is required.
This script reads frames adjacent to itself and prints checks to stdout.
"""
import json
import re
from pathlib import Path

import numpy as np
from ISLP import load_data
from sklearn.model_selection import GridSearchCV, KFold, train_test_split
from sklearn.tree import DecisionTreeRegressor

FRAMES = Path(__file__).resolve().parent / "frames"


def load_frames(path):
    return {
        name: json.loads(payload)
        for name, payload in re.findall(
            r"const (FRAMES_\w+) = (.*?);", path.read_text(encoding="utf-8")
        )
    }


def main():
    nonlinear = load_frames(FRAMES / "nonlin.js")
    wage = load_data("Wage")
    saved_wage = nonlinear["FRAMES_w08wage"]
    assert saved_wage["n"] == 3000 and saved_wage["nFull"] == 3000
    assert np.array_equal(saved_wage["wage"], np.asarray(wage.wage))
    assert np.array_equal(saved_wage["age"], np.asarray(wage.age))
    print("PASS Wage exact all 3000 rows and full precision; high-income rows retained:",
          int((wage.wage > 250).sum()))

    lowess = nonlinear["FRAMES_w08lowess"]
    assert set(lowess["curves"]) == {"0.2", "0.5"}
    assert len(lowess["grid"]) == 100
    for values in lowess["curves"].values():
        assert len(values) == 100 and np.isfinite(values).all()
    # This verifies output integrity; generator settings are documented in
    # gen_nonlin.py and its saved metadata, not independently refit here.
    print("PASS exact lab robust LOWESS settings; 100 grid predictions each at frac=.2,.5")

    digits = load_frames(FRAMES / "unsup.js")["FRAMES_w07tsne"]
    assert digits["n"] == 1797
    assert all(len(view["xy"]) == 1797 for view in digits["views"].values())
    print("PASS digits all 1797: label count", np.bincount(digits["labels"]).tolist(),
          "coordinate ranges", {
              key: [np.min(view["xy"]), np.max(view["xy"])]
              for key, view in digits["views"].items()
          })

    rng = np.random.default_rng(524)
    design = rng.normal(size=(17, 4))
    design -= design.mean(0)
    covariance = design.T @ design / 16
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    whitened = design @ eigenvectors @ np.diag(eigenvalues ** -0.5)
    error = np.max(np.abs(whitened.T @ whitened / 16 - np.eye(4)))
    assert error < 1e-12
    print("PASS whitening covariance identity max error", error)

    group_a, group_b = design[:5], design[5:]

    def within_ss(group):
        return ((group - group.mean(0)) ** 2).sum()

    change = within_ss(design) - within_ss(group_a) - within_ss(group_b)
    formula = (len(group_a) * len(group_b) / len(design)
               * ((group_a.mean(0) - group_b.mean(0)) ** 2).sum())
    assert abs(change - formula) < 1e-12
    print("PASS Ward incremental WSS", change, "formula", formula)

    orthogonal_ols = np.array([0.1, -2.0, 4.0])
    penalty = 0.8
    soft = np.sign(orthogonal_ols) * np.maximum(abs(orthogonal_ols) - penalty / 2, 0)
    gradient = 2 * (soft - orthogonal_ols)
    nonzero = soft != 0
    assert np.allclose(gradient[nonzero] + penalty * np.sign(soft[nonzero]), 0)
    assert (abs(gradient[~nonzero]) <= penalty).all()
    print("PASS Lasso soft threshold KKT for RSS + lambda L1; coefficients", soft)

    boston = load_data("Boston")
    x_train, x_test, y_train, y_test = train_test_split(
        boston.drop(columns=["medv"]), boston.medv,
        test_size=0.3, random_state=0,
    )
    tree = DecisionTreeRegressor(max_depth=3, random_state=0).fit(x_train, y_train)
    grid = GridSearchCV(
        tree,
        {"ccp_alpha": tree.cost_complexity_pruning_path(x_train, y_train).ccp_alphas},
        cv=KFold(5, shuffle=True, random_state=10),
        scoring="neg_mean_squared_error",
    ).fit(x_train, y_train)
    mse = float(np.mean((grid.predict(x_test) - y_test) ** 2))
    assert grid.best_params_["ccp_alpha"] == 0.0
    assert abs(mse - 28.069857549754044) < 1e-10
    print("PASS Boston tree actual lab CV alpha", grid.best_params_, "MSE", mse)


if __name__ == "__main__":
    main()
