"""Independent small numerical checks for the authored SVM examples (not course Lab reruns)."""
import json
from pathlib import Path
import numpy as np
import sklearn
from sklearn.svm import SVC,SVR
from sklearn.metrics import roc_auc_score

out=Path(__file__).resolve().parent
rows=[]
def check(name,ok,**evidence):
    assert bool(ok),(name,evidence)
    rows.append(dict(name=name,status='PASS',**evidence))

X=np.array([[-1.],[1.]])
y=np.array([-1.,1.])
for C in [.25,1.,100.]:
    m=SVC(C=C,kernel='linear',tol=1e-10).fit(X,y)
    signed=np.zeros(2);signed[m.support_]=m.dual_coef_[0]
    a=signed*y
    w=m.coef_[0]
    margins=y*m.decision_function(X)
    xi=np.maximum(0,1-margins)
    primal=.5*(w@w)+C*sum(xi)
    dual=sum(a)-.5*(signed@(X@X.T)@signed)
    expected=2*min(C,.5)
    check(f'two-point C={C}',abs(w[0]-expected)<1e-8 and abs(primal-dual)<1e-8,
          w=w.tolist(),alpha=a.tolist(),slack=xi.tolist(),primal=float(primal),dual=float(dual))
    check(f'KKT C={C}',np.all(a>=-1e-9) and np.all(a<=C+1e-9)
          and abs(signed.sum())<1e-9 and np.max(np.abs(a*(1-xi-margins)))<1e-8
          and np.max(np.abs((C-a)*xi))<1e-8)

# The saturated solution has no free SV and an interval of optimal intercepts.
for b in [-.5,-.2,0,.2,.5]:
    margin=y*(.5*X[:,0]+b)
    xi=np.maximum(0,1-margin)
    check(f'no-free-SV intercept b={b}',abs(.125+.25*xi.sum()-.375)<1e-12)

Z=np.zeros((2,1))
m=SVC(C=.7,kernel='linear',tol=1e-10).fit(Z,y)
check('nonseparable coincident points',np.max(abs(m.coef_))<1e-12 and np.allclose(abs(m.dual_coef_),.7),
      note='Soft margin feasible; hard margin impossible; geometric 1/||w|| is not used at w=0.')

gram=X@X.T
check('PSD permits zero eigenvalues',np.allclose(np.linalg.eigvalsh(gram),[0,2]))
a=np.array([2.,-1.]);b=np.array([3.,4.])
phi=lambda x:np.array([np.sqrt(2)*x[0]*x[1],x[0]**2,x[1]**2])
check('quadratic feature identity',np.isclose(phi(a)@phi(b),(a@b)**2))

svr=SVR(kernel='linear',C=3,epsilon=.1,tol=1e-10).fit(np.array([[0.],[1.],[2.]]),np.array([0.,1.,2.]))
sx=np.array([[0.],[1.],[2.]])
sy=np.array([0.,1.,2.])
d=np.zeros(3);d[svr.support_]=svr.dual_coef_[0]
reg_primal=.5*float(svr.coef_[0]@svr.coef_[0])+3*np.maximum(0,abs(sy-svr.predict(sx))-.1).sum()
reg_dual=-.5*d@(sx@sx.T)@d-.1*abs(d).sum()+sy@d
check('SVR dual and recovery',abs(d.sum())<1e-9 and abs(reg_primal-reg_dual)<1e-7,
      coefficient=svr.coef_.tolist(),intercept=svr.intercept_.tolist(),primal=float(reg_primal),dual=float(reg_dual))
check('ROC example AUC',roc_auc_score([1,0,1,0],[.8,.5,.2,-.4])==.75)
for label in [0,1]:
    for score in [-3.,0.,2.]:
        p=1/(1+np.exp(-score))
        nll=-label*np.log(p)-(1-label)*np.log(1-p)
        check(f'logistic coding z={label},f={score}',np.isclose(nll,np.logaddexp(0,-(2*label-1)*score)))

# Kernel ridge equality and normalized one-class dual convention.
rx=np.array([[-1.,0.],[0.,1.],[1.,0.]])
ry=np.array([-1.,.2,1.]);lam=.7
coef=np.linalg.solve(rx@rx.T+lam*np.eye(3),ry)
primal_w=np.linalg.solve(rx.T@rx+lam*np.eye(2),rx.T@ry)
check('kernel ridge representer equality',np.allclose(rx.T@coef,primal_w))
from sklearn.svm import OneClassSVM
ox=np.array([[-1.],[-.2],[.3],[1.]])
nu=.5
oc=OneClassSVM(nu=nu,gamma=.4,tol=1e-10).fit(ox)
oa=np.zeros(len(ox));oa[oc.support_]=oc.dual_coef_[0]/(nu*len(ox))
rho=-oc.intercept_[0]/(nu*len(ox))
ok=np.exp(-.4*(ox-ox.T)**2)
xi=np.maximum(0,rho-ok@oa)
pp=.5*oa@ok@oa+xi.sum()/(nu*len(ox))-rho
dd=-.5*oa@ok@oa
check('one-class normalized dual',abs(oa.sum()-1)<1e-8 and np.all(oa<=1/(nu*len(ox))+1e-8) and abs(pp-dd)<1e-7,
      primal=float(pp),dual=float(dd),note='LIBSVM stored coefficients divided by nu*n for the unit-sum mathematical convention.')

payload={'purpose':'original didactic examples only; no course Lab rerun',
         'versions':{'numpy':np.__version__,'sklearn':sklearn.__version__},'checks':rows}
(out/'svm-numerical.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print(f'{len(rows)} independent SVM numerical checks PASS')
for row in rows: print(json.dumps(row,ensure_ascii=False))
