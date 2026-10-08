"""Independent algebra and numerical consistency checks, not student examples."""
import numpy as np
from sklearn.linear_model import Ridge,Lasso,ElasticNet
from sklearn.decomposition import PCA
rng=np.random.default_rng(6006)
X=rng.normal(size=(40,6));X-=X.mean(0);y=rng.normal(size=40);y-=y.mean()
a=.35;n=len(y)
r=Ridge(alpha=n*a,fit_intercept=False).fit(X,y)
e=ElasticNet(alpha=a,l1_ratio=0,fit_intercept=False,tol=1e-12,max_iter=100000).fit(X,y)
assert np.allclose(r.coef_,e.coef_,atol=1e-8)
# Orthogonal design matches the deck's RSS + lambda L1 threshold.
q,_=np.linalg.qr(X);z=q.T@y;lam=.8
fit=Lasso(alpha=lam/(2*n),fit_intercept=False,tol=1e-13,max_iter=10000).fit(q,y)
assert np.allclose(fit.coef_,np.sign(z)*np.maximum(abs(z)-lam/2,0),atol=1e-9)
u,d,vt=np.linalg.svd(X,full_matrices=False)
S=X.T@X/(n-1);Z=X@vt.T
assert np.allclose(Z.T@Z/(n-1),np.diag(d*d/(n-1)))
W=Z/np.sqrt(d*d/(n-1))
assert np.allclose(W.T@W/(n-1),np.eye(6))
for m in range(1,7):
 V=vt[:m].T;recon=X@V@V.T
 assert np.allclose(np.sum((X-recon)**2),np.sum(X**2)-(n-1)*np.trace(V.T@S@V))
 # Whitened and ordinary retained scores span same regression space.
 assert np.allclose(Z[:,:m]@np.linalg.lstsq(Z[:,:m],y,rcond=None)[0],W[:,:m]@np.linalg.lstsq(W[:,:m],y,rcond=None)[0])
# Added-variable adjusted-R2 criterion agrees with F>1 for positive residual dfs.
for nu in (3,10,35):
 for R1 in (.1,2.,9.,9.9):
  R0=10.
  assert (R1/(nu-1)<R0/nu)==((R0-R1)>R0/nu)
  assert (R1/(nu-1)<R0/nu)==(((R0-R1)/(R1/(nu-1)))>1)
# Mean minimizes squared error decomposition.
c=.7
assert np.allclose(np.sum((y-c)**2),np.sum((y-y.mean())**2)+n*(c-y.mean())**2)
print('PASS: Ridge/ElasticNet alpha mapping; Lasso lambda/(2n); PCA covariance/SVD/reconstruction/whitening; PCR scaling invariance; adjusted-R2 threshold; optimal constant.')
import sys,sklearn
print('Python',sys.version.split()[0],'sklearn',sklearn.__version__)
