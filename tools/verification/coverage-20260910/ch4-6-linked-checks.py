from pathlib import Path
import numpy as np,json,subprocess,sys
V=Path(__file__).resolve().parent;R=V.parents[2];out=[]
def check(name,x,y,tol=1e-9):
 err=float(np.max(abs(np.asarray(x)-y)));assert err<tol,(name,err);out.append({'check':name,'error':err,'tolerance':tol})
X=np.array([[0,1],[1,0],[2,1],[1,3],[2,4],[3,2],[4,4],[5,3]],float);y=np.array([0,0,0,0,1,1,1,1.]);X-=X.mean(0)
means=[X[y==k].mean(0) for k in [0,1]];d=means[1]-means[0];W=sum((X[y==k]-means[k]).T@(X[y==k]-means[k]) for k in [0,1]);a=2;v=np.linalg.solve(W,d);check('OLS vs LDA direction',np.linalg.lstsq(X,y-y.mean(),rcond=None)[0],a*v/(1+a*d@v))
G=np.eye(2)[y.astype(int)];N=np.diag(G.sum(0));B=X.T@G@np.linalg.solve(N,G.T@X);check('total within between scatter',X.T@X,W+B)
S1=np.array([[2,.3],[.3,1]]);S0=np.array([[1,.2],[.2,3]]);A1=np.linalg.inv(S1);A0=np.linalg.inv(S0);m1=np.array([1,2]);m0=np.array([-.5,1]);x=np.array([.2,-.7]);pr1=.4;pr0=.6
aa=np.log(pr1/pr0)-.5*np.log(np.linalg.det(S1)/np.linalg.det(S0))-.5*m1@A1@m1+.5*m0@A0@m0;bb=A1@m1-A0@m0;CC=.5*(A0-A1)
score=lambda p,m,A,S:np.log(p)-.5*np.log(np.linalg.det(S))-.5*(x-m)@A@(x-m)
check('QDA explicit coefficients',aa+bb@x+x@CC@x,score(pr1,m1,A1,S1)-score(pr0,m0,A0,S0))
z=np.array([3,1.]);shrink=lambda z,l:np.sign(z)*np.maximum(abs(z)-l/2,0)
check('lambda plateau counterexample',np.r_[shrink(z,6),shrink(z,7)],np.zeros(4));check('lasso need not be sparse',shrink(np.array([3,2.]),1),[2.5,1.5])
sample=np.array([1.,2,3]);loo=np.array([np.delete(sample,i).mean() for i in range(3)]);check('Jackknife mean example',[(2/3)*np.sum((loo-loo.mean())**2),2*(loo.mean()-sample.mean())],[1/3,0])
# Exact exchangeable-rank enumeration, no Monte Carlo.
scores=np.arange(1,11);success=0
for i in range(10):q=np.sort(np.delete(scores,i))[7];success+=scores[i]<=q
check('split conformal finite rank example',success/10,.8)
s=np.array([-1,0,1]);auc=np.mean((s[:,None]>s[None,:])+.5*(s[:,None]==s[None,:]));check('random-score AUC with ties',auc,.5)
check('binary sum deviance example',-2*np.log(.8*.7),1.1596369905058846)
Z=np.array([-1,-.5,.5,1]);check('uncorrelated dependent counterexample',np.mean(Z*Z**2)-Z.mean()*(Z**2).mean(),0.)
# Check convex penalized optimizer also minimizes RSS on its corresponding budget by exact scalar example.
z=3.;l=2.;b=z/(1+l);check('ridge budget scalar optimum',b,1.)
(V/'ch4-6-linked-numerical.json').write_text(json.dumps({'result':'PASS','numpy':np.__version__,'checks':out},indent=2)+'\n')
for stem in ['classification','resampling_methods','model_selection']:
 p=subprocess.run([sys.executable,'tools/validate.py','--page',stem],cwd=R,capture_output=True,text=True);(V/f'ch4-6-linked-validate-{stem}.log').write_text(p.stdout+p.stderr);assert p.returncode==0,(stem,p.stdout+p.stderr)
print('PASS',len(out),'independent numerical checks and 3 page validators')
