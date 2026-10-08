from ISLP import load_data
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import (
    KFold, GridSearchCV, cross_val_score, cross_validate
)

# 沿用 Ch05 Lab：以 horsepower 預測 Auto 的 mpg。
Auto = load_data("Auto")
X = Auto[["horsepower"]].to_numpy()
y = Auto["mpg"].to_numpy()
model = make_pipeline(PolynomialFeatures(degree=2, include_bias=False),
                      LinearRegression())

# 對齊 Lab 的 10-fold 切法，評估事先固定的二次模型。
cv = KFold(10, shuffle=True, random_state=0)
fixed_scores = cross_val_score(
    model, X, y, cv=cv, scoring="neg_mean_squared_error")
print("固定二次模型 CV MSE", -fixed_scores.mean())

# 延伸：自動比較 Lab 的 1 到 5 次多項式。
inner = KFold(3, shuffle=True, random_state=1)
outer = KFold(5, shuffle=True, random_state=2)
search = GridSearchCV(
    model, {"polynomialfeatures__degree": [1, 2, 3, 4, 5]},
    cv=inner, scoring="neg_mean_squared_error", refit=True)
search.fit(X, y)
print("完整資料的最佳次數", search.best_params_)
print("用來選次數的 CV MSE", -search.best_score_)

# Nested CV：每次只用 outer 訓練部分執行完整搜尋。
result = cross_validate(search, X, y, cv=outer,
                        scoring="neg_mean_squared_error",
                        return_estimator=True)
print("Nested CV 外層 MSE", -result["test_score"])
print("Nested CV 外層平均 MSE", -result["test_score"].mean())
print("各 outer fold 選的次數",
      [est.best_params_ for est in result["estimator"]])

# 評估完成後，在全部可用訓練資料重新搜尋並 refit。
# 若另有 external test set，X、y 在此只包含 training data。
search.fit(X, y)
final_model = search.best_estimator_
