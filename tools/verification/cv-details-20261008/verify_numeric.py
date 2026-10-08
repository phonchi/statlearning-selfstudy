import numpy as np
import statsmodels.api as sm
import sklearn
from ISLP import load_data
from sklearn.model_selection import KFold, StratifiedKFold, GroupKFold, StratifiedGroupKFold
from sklearn.metrics import mean_squared_error
print('sklearn', sklearn.__version__)
Auto=load_data('Auto'); H=Auto.horsepower.to_numpy(); y=Auto.mpg.to_numpy()
X=np.power.outer(H,np.arange(3))
mse=[]
for train,valid in KFold(10,shuffle=True,random_state=0).split(X):
 fit=sm.OLS(y[train],X[train]).fit()
 mse.append(mean_squared_error(y[valid],fit.predict(X[valid])))
assert np.isclose(np.mean(mse),19.1853314193751,rtol=1e-10)
print('Independent statsmodels 10-fold quadratic MSE',np.mean(mse))
assert 5*3*5+5+5*3+1==96
print('Nested CV fit-count arithmetic: 96 PASS')
groups=np.repeat(np.arange(12),5); y=np.repeat([0]*6+[1]*6,5); X=np.arange(60).reshape(-1,1)
for splitter in [GroupKFold(3),StratifiedGroupKFold(3)]:
 seen=[]
 for train,valid in splitter.split(X,y,groups):
  assert set(groups[train]).isdisjoint(groups[valid])
  seen.extend(np.unique(groups[valid]))
 assert sorted(seen)==list(range(12))
print('Group separation and each group validates once: PASS')
for _,valid in StratifiedKFold(3,shuffle=True,random_state=42).split(X,y): assert y[valid].mean()==0.5
print('Stratified example ratio: PASS')
