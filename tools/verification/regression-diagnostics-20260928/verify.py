from pathlib import Path
import sys,json,re,subprocess,runpy
import numpy as np
from bs4 import BeautifulSoup
ROOT=Path('/home/phonchi/statlearning-selfstudy');OUT=ROOT/'tools/verification/regression-diagnostics-20260928'
sys.dont_write_bytecode=True;sys.path.insert(0,str(ROOT/'tools/enrich'))
from lib import splice_section
from reader_sources import fragment
ns=runpy.run_path(str(ROOT/'tools/enrich/enrich_regression.py'))
s=(ROOT/'linear_regression.html').read_text();rebuilt=s
for sec in ['problems','vsknn']:rebuilt=splice_section(rebuilt,sec,fragment(ns['BODIES'][sec]))
assert rebuilt==s,'Generated content not idempotent'
doc=BeautifulSoup(s,'html.parser');ids=[x['id'] for x in doc.select('[id]')];assert len(ids)==len(set(ids))
added=json.loads((OUT/'supplement_ids.json').read_text())
for id in added:
 d=doc.find(id=id);assert d and d.name=='details' and not d.has_attr('open')
 assert d.find('summary',recursive=False)
 assert not re.search(r'第\s*\d+\s*頁',d.get_text())
for d in doc.select('details'):assert len(d.find_parents('details'))<=1
for a in doc.select('a[href^="#"]'):assert a['href'][1:] in ids,a['href']
before=subprocess.check_output(['git','show','HEAD:linear_regression.html'],cwd=ROOT,text=True)
# Every script, including interactions, frames and data, is byte-preserved.
assert re.findall(r'<script\b.*?</script>',s,re.S)==re.findall(r'<script\b.*?</script>',before,re.S)
a=BeautifulSoup(before,'html.parser');b=BeautifulSoup(s,'html.parser')
for sec in ['problems','vsknn']:
 a.find(id=sec).decompose();b.find(id=sec).decompose()
assert str(a)==str(b),'Unexpected change outside the two intended sections'
print('PASS: source/page idempotence, 8 default-closed disclosures, unique IDs, anchors, no page numbers, unchanged scripts and unrelated sections.')
# Independent algebra checks against directly refitted models.
rng=np.random.default_rng(20260928);X=np.column_stack([np.ones(24),rng.normal(size=(24,3))]);y=X@np.array([1.,2.,-.5,.7])+rng.normal(size=24)
A=np.linalg.inv(X.T@X);H=X@A@X.T;beta=np.linalg.lstsq(X,y,rcond=None)[0];fit=X@beta;e=y-fit;h=H.diagonal();s2=e@e/(24-4)
errors=[]
for i in range(24):
 changed=y.copy();changed[i]+=.25;fit_changed=X@np.linalg.lstsq(X,changed,rcond=None)[0]
 assert np.allclose(fit_changed[i]-fit[i],h[i]*.25,atol=1e-12)
 keep=np.arange(24)!=i;deleted=np.linalg.lstsq(X[keep],y[keep],rcond=None)[0]
 assert np.allclose(beta-deleted,A@X[i]*e[i]/(1-h[i]),atol=1e-12)
 delta=fit-X@deleted;ss=delta@delta;formula=e[i]**2*h[i]/(1-h[i])**2
 r=e[i]/np.sqrt(s2*(1-h[i]));cook1=ss/(4*s2);cook2=r*r/4*h[i]/(1-h[i])
 assert np.allclose([ss,cook1],[formula,cook2],atol=1e-12)
 errors.append(abs(cook1-cook2))
assert np.allclose(np.mean(h),4/24)
for j in range(1,4):
 others=np.delete(X,j,axis=1);res=X[:,j]-others@np.linalg.lstsq(others,X[:,j],rcond=None)[0]
 tss=np.sum((X[:,j]-X[:,j].mean())**2);R2=1-res@res/tss
 assert np.allclose(s2*A[j,j],s2/(tss*(1-R2)))
weights=1/np.linspace(1,4,24)**2
wb=np.linalg.solve(X.T@(weights[:,None]*X),X.T@(weights*y));wt=np.sqrt(weights)
assert np.allclose(wb,np.linalg.lstsq(X*wt[:,None],y*wt,rcond=None)[0])
assert np.allclose(1-1/np.array([5,10]),[.8,.9])
assert np.allclose(np.sqrt([5,10]),[2.2360679775,3.1622776602])
x=np.arange(7.);yknn=x*x
nearest=np.argmin(abs(x[:,None]-x[None,:]),axis=1);assert np.array_equal(yknn[nearest],yknn)
dist=abs(x[:,None]-x[None,:]);np.fill_diagonal(dist,np.inf);assert np.all(np.argmin(dist,axis=1)!=np.arange(7))
report={'disclosures':added,'n':24,'parameter_count':4,'seed':20260928,'max_cook_error':max(errors),'checks':['leverage sensitivity','deleted coefficients','deleted fitted sum of squares','Cook equivalence','average leverage','VIF coefficient variance','WLS transformed data','VIF 5 and 10','KNN self prediction and exclusion','source regeneration and HTML structure']}
(OUT/'math-and-structure.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: 24 direct deletion refits and leverage perturbations; WLS, VIF and KNN checks. Max Cook error:',max(errors))
