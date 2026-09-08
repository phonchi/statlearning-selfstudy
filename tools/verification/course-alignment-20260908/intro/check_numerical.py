"""Independent array checks against complete course data and alternate model designs."""
from pathlib import Path
import json
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.linalg import svd
from ISLP import load_data

root=Path(__file__).parent
frames={line.split(' = ',1)[0].split()[1]:json.loads(line.split(' = ',1)[1][:-1]) for line in (root/'frames.js').read_text().splitlines()}
w=load_data('Wage');f=frames['FRAMES_w01wage']
assert len(f['scatter'])==3000 and len(f['yearScatter'])==3000
np.testing.assert_allclose(f['scatter'],w[['age','wage']],atol=5.1e-7)
for col,order,key in [('age',4,'ageFit'),('year',1,'yearFit')]:
    xs=np.asarray(w[col]); xc=xs.mean(); scale=xs.std()
    design=np.vander((xs-xc)/scale,order+1,increasing=True)
    fit=sm.OLS(w.wage,design).fit()
    line=np.asarray(f[key]['line']); pred=fit.predict(np.vander((line[:,0]-xc)/scale,order+1,increasing=True))
    np.testing.assert_allclose(line[:,1],pred,atol=4e-6)
    assert len(f[key]['band'])==203
    print(f'PASS Wage {col} degree={order}, all 3000 observations, centered OLS max error={max(abs(line[:,1]-pred)):.3g}; bootstrap polygon 203 vertices')
a=load_data('Auto');af=frames['FRAMES_w01auto']
h,e=np.histogram(a.mpg,bins='auto',density=True)
np.testing.assert_allclose(np.asarray(af['hist'])[:,0],e[:-1]);np.testing.assert_allclose(np.asarray(af['hist'])[:,2],h)
np.testing.assert_allclose(af['pairData'],a[af['pairColumns']+['cylinders']],atol=5.1e-7)
assert len(af['pairKdes'])==4 and all(len(p)==5 for p in af['pairKdes'])
assert sum(x[2] for x in af['jointX'])==392 and sum(x[2] for x in af['jointY'])==392
print('PASS Auto density bins/area, all 392 rows/five cylinder groups, four diagonal KDE groups, both marginal totals')
n=load_data('NCI60');nf=frames['FRAMES_w01nci'];X=np.asarray(n['data']); X=(X-X.mean(0))/X.std(0)
U,d,V=svd(X-X.mean(0),full_matrices=False); ref=U[:,:3]*d[:3]
pts=np.array([[p['x'],-p['y'],p['z']] for p in nf['pts']]);np.testing.assert_allclose(np.abs(pts),np.abs(ref),atol=5.1e-7)
assert [p['g'] for p in nf['pts']]==list(n['labels'].label)
assert len({p['g'] for p in nf['pts']})==14
print('PASS NCI60 independently decomposed 64x6830 matrix, all 3 axes and all 14 unchanged labels')
b=load_data('Bikeshare');bf=frames['FRAMES_w01bike'];model=smf.ols('bikers ~ C(mnth, Sum) + C(hr, Sum) + workingday + temp + C(weathersit)',b).fit()
for field,levels,key in [('mnth',list(b.mnth.cat.categories),'monthCoefs'),('hr',list(b.hr.cat.categories),'hourCoefs')]:
    cs=[model.params[f'C({field}, Sum)[S.{v}]'] for v in levels[:-1]];cs.append(-sum(cs))
    np.testing.assert_allclose(bf[key],cs,atol=5.1e-7)
print('PASS Bikeshare alternate patsy design, all 12 month/24 hour sum-contrast coefficients')
print('Numerical verification complete. Bootstrap seed is pinned because source lab leaves it unspecified; stochastic band pixels need not match its saved run.')
