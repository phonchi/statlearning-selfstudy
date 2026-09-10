"""Deterministic algebra checks for the coverage additions; never execute course labs."""
import json, hashlib, subprocess, sys
from pathlib import Path
import numpy as np
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[3]
assert (R/'tools/enrich').is_dir(), R
V=Path(__file__).resolve().parent
log=[]
def check(name,actual,expected,tol=1e-9):
 err=float(np.max(np.abs(np.asarray(actual)-expected)))
 assert err<tol,(name,err)
 log.append({'check':name,'max_absolute_error':err,'tolerance':tol})
x=np.array([1.,2,3,4,20]);check('Ch1 mean/MAD/variance',[x.mean(),abs(x-x.mean()).mean(),np.median(abs(x-np.median(x))),x.var(ddof=1)],[6,5.6,1,62.5])
X=np.column_stack([np.ones(8),np.arange(8),np.array([1,0,2,1,4,0,2,3])]);y=np.array([1.,4,2,6,4,7,9,8]);b=np.linalg.lstsq(X,y,rcond=None)[0];H=X@np.linalg.solve(X.T@X,X.T);e=y-X@b
check('Ch3 residual orthogonality',X.T@e,np.zeros(3));d=np.array([.3,-.1,.7]);check('Ch3 RSS quadratic identity',np.sum((y-X@(b+d))**2),e@e+d@X.T@X@d)
Z=X[:,:2];M=np.eye(8)-Z@np.linalg.solve(Z.T@Z,Z.T);check('Ch3 partial regression slope',X[:,2]@M@y/(X[:,2]@M@X[:,2]),b[2])
rss0=np.sum((M@y)**2);s2=e@e/5;F=(rss0-e@e)/s2;t2=b[2]**2/(s2*np.linalg.inv(X.T@X)[2,2]);check('Ch3 F equals t squared',F,t2);check('Ch3 partial F numeric example',((150-100)/2)/(100/26),6.5)
press=[]
for i in range(8):
 mask=np.arange(8)!=i;bm=np.linalg.lstsq(X[mask],y[mask],rcond=None)[0];press.append(y[i]-X[i]@bm)
check('Ch5 PRESS direct refits vs shortcut',np.array(press),e/(1-np.diag(H)))
# Gradients independently checked through finite differences.
beta=np.array([-.7,.15,-.2]);yb=np.array([0,0,1,0,1,0,1,1.]);eta=X@beta;p=1/(1+np.exp(-eta));w=p*(1-p)
def ll(v):
 z=X@v;return yb@z-np.logaddexp(0,z).sum()
h=1e-5;eye=np.eye(3);gd=np.array([(ll(beta+h*a)-ll(beta-h*a))/(2*h) for a in eye]);check('Ch4 logistic score finite difference',gd,X.T@(yb-p),1e-7)
def score(v):return X.T@(yb-1/(1+np.exp(-(X@v))))
Hd=np.column_stack([(score(beta+h*a)-score(beta-h*a))/(2*h) for a in eye]);check('Ch4 Hessian finite difference',Hd,-X.T@(w[:,None]*X),1e-7)
z=eta+(yb-p)/w;new=np.linalg.solve(X.T@(w[:,None]*X),X.T@(w*z));new2=beta+np.linalg.solve(X.T@(w[:,None]*X),X.T@(yb-p));check('Ch4 IRLS equals Newton',new,new2)
check('Ch4 intercept MLE',[np.log(7/3),(7-5)/2.5],[.8472978603872037,.8]);check('Ch4 probability CI',1/(1+np.exp(-np.array([-.392,.392]))),[.403236,.596764],1e-6)
yc=np.array([0,1,0,3,1,2,4,2.]);mu=np.exp(eta)
def pois(v):return yc@(X@v)-np.exp(X@v).sum()
pd=np.array([(pois(beta+h*a)-pois(beta-h*a))/(2*h) for a in eye]);check('Ch4 Poisson score',pd,X.T@(yc-mu),1e-7)
check('Ch6 ridge orthogonal example',np.array([3,-.4,0])/3,[1,-.13333333333333333,0]);zv=np.array([3,-.4,0]);soft=np.sign(zv)*np.maximum(abs(zv)-1,0);check('Ch6 lasso soft threshold',soft,[2,0,0])
check('Ch6 Cp complete/constant dropped',[(90+2*4)/100,(90+2*3)/100],[.98,.96])
A=X[:,1:]-X[:,1:].mean(0);U,D,VT=np.linalg.svd(A,full_matrices=False);Vm=VT.T[:,:1];check('Ch6 PCA reconstruction identity',np.linalg.norm(A-A@Vm@Vm.T)**2,np.linalg.norm(A)**2-np.linalg.norm(A@Vm)**2)
S=A.T@A/7;evals,Q=np.linalg.eigh(S);wh=A@Q@np.diag(evals**-.5);check('Ch6 whitening covariance',wh.T@wh/7,np.eye(2))
# PLS training decomposition and the out-of-sample recursion are separate computations.
Ar=A/A.std(0,ddof=1);yr=y-y.mean();orig=Ar.copy();ts=[];ws=[];ps=[];qs=[]
for m in range(2):
 wv=Ar.T@yr;wv/=np.linalg.norm(wv);tv=Ar@wv;pv=Ar.T@tv/(tv@tv);qv=yr@tv/(tv@tv);ws.append(wv);ps.append(pv);qs.append(qv);ts.append(tv);Ar=Ar-np.outer(tv,pv);yr=yr-tv*qv
pred=[]
for row in orig:
 row=row.copy();v=y.mean()
 for wv,pv,qv in zip(ws,ps,qs):t=row@wv;v+=t*qv;row-=t*pv
 pred.append(v)
check('Ch6 PLS prediction recursion',pred,y.mean()+np.column_stack(ts)@qs);check('Ch6 PLS full rank OLS prediction',pred,X@b)
stems=['introduction','statistical_learning','linear_regression','classification','resampling_methods','model_selection']
states=[]
for stem in stems:
 soup=BeautifulSoup((R/f'{stem}.html').read_text(),'html.parser');proofs=soup.select('details.proof');assert not any(p.has_attr('open') for p in proofs)
 ids=[p['id'] for p in proofs];assert len(ids)==len(set(ids));states.append({'page':stem,'proof_count':len(proofs),'all_default_collapsed':True})
 result=subprocess.run([sys.executable,'tools/validate.py','--page',stem],cwd=R,capture_output=True,text=True);(V/f'ch1-6-validate-{stem}.log').write_text(result.stdout+result.stderr);assert result.returncode==0,stem
(V/'ch1-6-numerical.json').write_text(json.dumps({'numpy':np.__version__,'checks':log,'pages':states},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'result':'PASS','numeric_checks':len(log),'pages':states},ensure_ascii=False,indent=2))
