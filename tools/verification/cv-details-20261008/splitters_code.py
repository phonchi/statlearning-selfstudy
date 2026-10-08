import numpy as np
from sklearn.model_selection import (
    StratifiedKFold, GroupKFold, StratifiedGroupKFold
)

# 12 位病人，每人 5 筆觀測；6 位為負例、6 位為正例。
groups = np.repeat(np.arange(12), 5)
y = np.repeat([0] * 6 + [1] * 6, 5)
X = np.arange(60).reshape(-1, 1)

splitters = {
    "分層": StratifiedKFold(
        n_splits=3, shuffle=True, random_state=42),
    "分組": GroupKFold(n_splits=3),
    "分層且分組": StratifiedGroupKFold(n_splits=3),
}
for name, cv in splitters.items():
    folds = (cv.split(X, y) if name == "分層"
             else cv.split(X, y, groups=groups))
    for fold, (train, valid) in enumerate(folds, 1):
        shared = np.intersect1d(groups[train], groups[valid])
        print(name, fold, "驗證正例比例", y[valid].mean(),
              "兩側共用病人數", len(shared))
