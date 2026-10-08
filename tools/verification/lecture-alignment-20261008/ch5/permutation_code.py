from sklearn.datasets import load_iris
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, permutation_test_score

# 承接講義的分類器置換檢定；此例是延伸實作，不是 Ch05 原 Lab。
X, y = load_iris(return_X_y=True)
model = make_pipeline(StandardScaler(), SVC(kernel="linear", C=1))
cv = StratifiedKFold(5, shuffle=True, random_state=0)
score, null_scores, p_value = permutation_test_score(
    model, X, y, cv=cv, scoring="accuracy",
    n_permutations=199, random_state=0, n_jobs=1)
print("原始標籤的 CV accuracy", score)
print("置換標籤後的平均 accuracy", null_scores.mean())
print("置換檢定 p-value", p_value)
