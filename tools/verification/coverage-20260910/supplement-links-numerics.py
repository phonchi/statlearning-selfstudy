"""Independent calculations for Ch1-3 link-closure additions; no notebook execution."""
import math
import numpy as np

def check(name,got,want,tol=1e-9):
 err=float(np.max(np.abs(np.asarray(got)-np.asarray(want))))
 assert err<=tol,(name,got,want)
 print(name,'PASS','max_error',err)
check('normal median ARE',2/math.pi,.6366197723675814)
check('shell 2d',1-.9**2,.19)
check('shell 10d',1-.9**10,.6513215599)
check('shell 50d',1-.9**50,.9948462247926799)
check('studentization stated example',2*math.sqrt(9/6),math.sqrt(6))
check('duplicated sample SE ratio',math.sqrt(18/38),.6882472016116853)
y=np.array([1,2,3.]);pred=y+10
check('R2 uncalibrated',1-np.sum((y-pred)**2)/np.sum((y-y.mean())**2),-149)
check('correlation uncalibrated',np.corrcoef(y,pred)[0,1]**2,1)
# Distinct data from page: independently refit each deleted sample and compare identities.
x=np.array([-2,-1,0,1,2,3.]);y=np.array([-.5,1,1.8,2.7,2.3,5.2]);X=np.column_stack([np.ones(len(x)),x]);n,m=X.shape
beta=np.linalg.lstsq(X,y,rcond=None)[0];e=y-X@beta;rss=e@e;H=X@np.linalg.solve(X.T@X,X.T);nu=n-m;s2=rss/nu
for i in range(n):
 keep=np.arange(n)!=i;b=np.linalg.lstsq(X[keep],y[keep],rcond=None)[0];ed=y[keep]-X[keep]@b
 check('deleted RSS '+str(i),ed@ed,rss-e[i]**2/(1-H[i,i]))
 ext=e[i]/math.sqrt((ed@ed)/(nu-1)*(1-H[i,i]));ri=e[i]/math.sqrt(s2*(1-H[i,i]))
 check('studentization identity '+str(i),ext,ri*math.sqrt((nu-1)/(nu-ri**2)))
check('residual fitted covariance algebra',(np.eye(n)-H)@H,np.zeros((n,n)))
a,b=1.3,-.7;co=[2,-1,3,.8]
for x,z in [(-1,2),(0,.3),(4,-2)]:
 u,v=x-a,z-b
 lhs=co[0]+co[1]*x+co[2]*z+co[3]*x*z
 rhs=co[0]+a*co[1]+b*co[2]+a*b*co[3]+(co[1]+b*co[3])*u+(co[2]+a*co[3])*v+co[3]*u*v
 check('center interaction '+str((x,z)),lhs,rhs)
print('All link-closure numerical checks passed.')
