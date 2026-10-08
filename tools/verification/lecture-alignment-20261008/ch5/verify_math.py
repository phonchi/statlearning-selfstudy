import itertools, numpy as np
from scipy.optimize import minimize_scalar
x=np.array([2.,4.,9.]);jack=np.array([np.delete(x,i).mean() for i in range(len(x))]);
jackse=np.sqrt((len(x)-1)/len(x)*np.sum((jack-jack.mean())**2))
assert np.isclose(jackse,np.sqrt(13/3))
boot=np.array([np.mean(a) for a in itertools.product(x,repeat=3)])
assert np.isclose(boot.var(),26/9)
assert np.isclose(boot.std(),1.699673171197595)
v=lambda a:a*a+(1-a)**2*1.25+2*a*(1-a)*.5
opt=minimize_scalar(v);assert np.isclose(opt.x,.6)
assert np.allclose([2*10-13,2*10-8],[7,12])
assert (1+0)/(199+1)==.005
print('Jackknife SE:',jackse)
print('Enumerated n=3 bootstrap mean SD:',boot.std())
print('Portfolio analytic/numeric alpha:',.6,opt.x)
print('Basic CI reflection, Monte Carlo p-value bound: PASS')
