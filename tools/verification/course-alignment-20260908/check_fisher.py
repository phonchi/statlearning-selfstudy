"""Independent checks of lecture Fisher geometry, Iris counts, and binary equivalence."""
import json
import numpy as np
from scipy.linalg import eigh
from sklearn.datasets import load_iris
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import confusion_matrix
X,y=load_iris(return_X_y=True)
mu=X.mean(0); means=np.array([X[y==k].mean(0) for k in range(3)])
W=sum((X[y==k]-means[k]).T@(X[y==k]-means[k]) for k in range(3))
B=sum(sum(y==k)*np.outer(means[k]-mu,means[k]-mu) for k in range(3))
e,A=eigh(B,W); A=A[:,::-1]; e=e[::-1]
assert np.allclose(A.T@W@A,np.eye(4))
assert np.linalg.matrix_rank(B)==2
lda=LinearDiscriminantAnalysis().fit(X,y)
cm=confusion_matrix(y,lda.predict(X))
assert cm.tolist()==[[50,0,0],[0,48,2],[0,1,49]]
# A is W-normalized; multiply by sqrt(n-K) for pooled-covariance whitening.
Z=X@A[:,:2]*np.sqrt(147); cent=means@A[:,:2]*np.sqrt(147)
dist=((Z[:,None]-cent[None])**2).sum(2)/2-np.log(lda.priors_)
assert np.array_equal(dist.argmin(1),lda.predict(X))
keep=y!=0; xb=X[keep];yb=y[keep]; mb=[xb[yb==k].mean(0) for k in (1,2)]
wb=sum((xb[yb==k]-mb[k-1]).T@(xb[yb==k]-mb[k-1]) for k in (1,2))
f=np.linalg.solve(wb,mb[1]-mb[0]); coef=LinearDiscriminantAnalysis().fit(xb,yb).coef_[0]
assert np.allclose(f/np.linalg.norm(f),coef/np.linalg.norm(coef))
print(json.dumps(dict(n=len(y),counts=np.bincount(y).tolist(),eigenvalues=e.tolist(),confusion=cm.tolist(),training_accuracy=float(np.trace(cm)/len(y)),W_orthogonality_max_error=float(abs(A.T@W@A-np.eye(4)).max()),full_projection_matches=True,binary_direction_matches=True),indent=2))
