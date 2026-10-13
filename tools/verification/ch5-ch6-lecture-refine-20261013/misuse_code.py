import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, cross_val_score

n_obs, p_all, k_sel = 50, 5000, 100   # 講義的 50 筆、5000 個變數、挑 100 個

def abs_corr(X, y):
    # 每個變數與 0/1 類別的相關係數絕對值
    xc, yc = X - X.mean(axis=0), y - y.mean()
    den = np.sqrt((xc * xc).sum(axis=0) * float(yc @ yc))
    return np.abs((xc.T @ yc) / np.where(den == 0, 1, den))

def cv_misuse_once(seed):
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n_obs, p_all))
    y = rng.integers(0, 2, n_obs)              # 類別與 X 完全無關
    kf = KFold(n_splits=5, shuffle=True, random_state=seed)

    # 錯誤流程：先用全部資料（含之後的驗證折）挑變數，再只對分類器做 CV
    top = np.argsort(-abs_corr(X, y))[:k_sel]
    wrong = 1 - cross_val_score(LogisticRegression(max_iter=2000),
                                X[:, top], y, cv=kf).mean()

    # 正確流程：挑變數也放進每一折，只看該折的訓練部分
    acc = []
    for tr, te in kf.split(X):
        sel = np.argsort(-abs_corr(X[tr], y[tr]))[:k_sel]
        model = LogisticRegression(max_iter=2000).fit(X[tr][:, sel], y[tr])
        acc.append(model.score(X[te][:, sel], y[te]))
    right = 1 - np.mean(acc)
    return wrong, right

res = np.array([cv_misuse_once(7000 + i) for i in range(100)])
print("錯誤流程的平均 CV 錯誤率", res[:, 0].mean().round(3))
print("正確流程的平均 CV 錯誤率", res[:, 1].mean().round(3))
