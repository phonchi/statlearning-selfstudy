"""Independent checks for newly introduced mathematical examples; no Lab execution."""
import math,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
checks=[]
def check(name,got,want,tol=1e-8):
 assert abs(got-want)<=tol,(name,got,want)
 checks.append({'check':name,'actual':got,'expected':want,'tolerance':tol})
def loss(t):
 b,beta,c,w=t
 return .5*(b+beta*max(0,c+2*w)-1)**2
p=[.1,.4,0,.5]; analytic=[-.5,-.5,-.2,-.4]
for j,g in enumerate(analytic):
 a=p.copy();b=p.copy();a[j]+=1e-6;b[j]-=1e-6
 check('DL gradient '+str(j),(loss(a)-loss(b))/2e-6,g,1e-7)
new=[x-.1*g for x,g in zip(p,analytic)]
check('DL loss before',loss(p),.125)
check('DL loss after',loss(new),.0630125)
check('Binomial 3,0.5 P(2)',math.comb(3,2)*.5**3,3/8)
check('Poisson rate2 normalization',sum(math.exp(-2)*2**k/math.factorial(k) for k in range(30)),1)
check('Poisson rate2 mean',sum(k*math.exp(-2)*2**k/math.factorial(k) for k in range(30)),2)
check('Poisson rate2 variance',sum((k-2)**2*math.exp(-2)*2**k/math.factorial(k) for k in range(30)),2)
check('Exponential rate2 survival1',math.exp(-2),.1353352832366127)
check('t interval approximate margin',2.262*3/math.sqrt(10),2.146,1e-3)
check('Beta posterior mean',9/14,.6428571428571429)
# OLS example: independently compute coefficients from raw data, then identities.
x=[0,1,2,3,4];y=[1,2,2,4,5];mx=sum(x)/len(x);my=sum(y)/len(y)
slope=sum((a-mx)*(b-my) for a,b in zip(x,y))/sum((a-mx)**2 for a in x)
bias=my-slope*mx;e=[b-bias-slope*a for a,b in zip(x,y)]
check('OLS slope',slope,1);check('OLS intercept',bias,.8);check('OLS residual sum',sum(e),0)
check('OLS RSS',sum(z*z for z in e),.8)
check('OLS SS identity',sum((b-my)**2 for b in y)-sum(z*z for z in e)-sum((bias+slope*a-my)**2 for a in x),0)
# Actual example: all supported GD step sizes satisfy L=1 descent bound, sampled across domain.
max_violation=-math.inf
for k in range(401):
 b=-20+k*.1;g=math.cos(b)+.1;old=math.sin(b)+b/10
 for lr in [.02,.1,.5,1,1.2,1.6]:
  nxt=b-lr*g;observed=math.sin(nxt)+nxt/10
  bound=old-lr*(1-lr/2)*g*g
  max_violation=max(max_violation,observed-bound)
assert max_violation<1e-12,max_violation
checks.append({'check':'GD L=1 descent bound, 401 points x 6 steps','max_violation':max_violation})
# Softmax cross entropy gradient, independent finite differences.
z=[.2,-.3,.7];target=1
ps=[math.exp(a)/sum(math.exp(t) for t in z) for a in z]
def ce(a): return math.log(sum(math.exp(t) for t in a))-a[target]
for j in range(3):
 a=z.copy();b=z.copy();a[j]+=1e-6;b[j]-=1e-6
 check('softmax CE gradient '+str(j),(ce(a)-ce(b))/2e-6,ps[j]-(j==target),1e-7)
for c in checks: print(json.dumps(c,ensure_ascii=False))
print('PASS',len(checks),'independent numerical checks; original Labs were not run.')
