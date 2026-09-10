from pathlib import Path
import numpy as np
from math import exp,log
from scipy.interpolate import BSpline
R=Path('/home/phonchi/statlearning-selfstudy')
rows=[]
def check(name,a,b,tol=1e-9):
 err=float(np.max(np.abs(np.asarray(a)-np.asarray(b))));assert err<tol,(name,err,a,b);rows.append((name,err))
x=np.array([-1,0,1.]);y=np.array([1,2,4.]);B=np.c_[np.ones(3),x];W=np.diag([.5,1,.5]);check('local WLS',np.linalg.solve(B.T@W@B,B.T@W@y),[2.25,1.5])
bs=BSpline.basis_element([0,1,2]);check('B-spline degree1',bs([.5,1,1.5]),[.5,1,.5])
check('logit CI',[1/(1+exp(2.98)),1/(1+exp(1.02))],[.0483,.2650],6e-5)
B=np.c_[np.ones(5),np.linspace(-1,1,5),np.linspace(-1,1,5)**2];O=np.diag([0,0,8]);lam=.3;y=np.array([1,0,1,3,2.]);A=B.T@B+lam*O;S=B@np.linalg.solve(A,B.T);loo=[]
for i in range(5):
 keep=np.arange(5)!=i;beta=np.linalg.solve(B[keep].T@B[keep]+lam*O,B[keep].T@y[keep]);loo.append(y[i]-B[i]@beta)
check('penalized LOOCV vs independent deleted fits',loo,(y-S@y)/(1-np.diag(S)))
G=np.array([2,-2]);H=np.array([1,2]);l=1.;gam=.1;w=-G/(H+l);gain=.5*np.sum(G**2/(H+l))-gam
check('XGBoost leaf values',w,[-1,2/3]);check('XGBoost gain',gain,47/30)
e=.25;a=.5*log((1-e)/e);check('AdaBoost relative reweight',exp(2*a),3.)
X=np.array([[-1.,-1],[0,0],[1,1]]);eig,V=np.linalg.eigh(X.T@X/2);check('PCA eigenvalues',eig,[0,2]);check('PCA projection residual',np.linalg.norm(X-X@V[:,-1:]@V[:,-1:].T),0)
a=np.array([0,2]);b=np.array([5,7]);sse=lambda v:np.sum((v-v.mean())**2);check('Ward merge SSE identity',sse(np.r_[a,b])-sse(a)-sse(b),25)
v=1/(2+1);check('BART posterior mean variance',[v*4,v],[4/3,1/3]);p=1/(1+exp(-2));check('GMM one EM mean update',[(1-p)*2,p*2],[.23840584404423537,1.7615941559557646])
# t-SNE full ordered-pair normalization and finite difference gradient
z=np.array([[0.,0.],[1.,.3],[3.,-.2]]);P=np.array([[0,.2,.1],[.2,0,.2],[.1,.2,0]])
def cost(z):
 d=z[:,None,:]-z[None,:,:];w=1/(1+np.sum(d*d,axis=2));np.fill_diagonal(w,0);q=w/w.sum();m=P>0;return np.sum(P[m]*np.log(P[m]/q[m]))
d=z[:,None,:]-z[None,:,:];w=1/(1+np.sum(d*d,axis=2));np.fill_diagonal(w,0);q=w/w.sum();grad=4*np.sum(((P-q)*w)[:,:,None]*d,axis=1);num=np.zeros_like(z)
for i in range(3):
 for j in range(2):
  zp=z.copy();zm=z.copy();zp[i,j]+=1e-6;zm[i,j]-=1e-6;num[i,j]=(cost(zp)-cost(zm))/2e-6
check('t-SNE gradient vs finite differences',grad,num,2e-8)
check('t-SNE ordered probability sum',q.sum(),1.)
for name,err in rows:print(f'PASS {name}: max_error={err:.3g}')
print(f'{len(rows)} independent numeric checks passed')
