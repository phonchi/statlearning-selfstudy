from pathlib import Path
import re,hashlib,subprocess,json,sys
import numpy as np
from bs4 import BeautifulSoup
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
meta=json.loads((out/'provenance.json').read_text())
before=(Path(sys.argv[1]).read_text() if len(sys.argv)>1 else subprocess.check_output(['git','show',meta['baseline_commit']+':classification.html'],cwd=root,text=True))
a=BeautifulSoup(before,'html.parser',preserve_whitespace_tags={'pre','span','div'})
text=(root/'classification.html').read_text();b=BeautifulSoup(text,'html.parser',preserve_whitespace_tags={'pre','span','div'})
for sel in ['.pseudo-code','.expected-out']:
 x=sorted(n.get_text() for n in a.select(sel));y=sorted(n.get_text() for n in b.select(sel));assert x==y;print('PASS',sel,len(x),'unchanged')
frames=lambda s:dict(re.findall(r'^const (FRAMES_\w+)\s*=\s*(.*?);\s*$',s,re.M))
assert frames(before)==frames(text);print('PASS all frames unchanged')
ids=[n['id'] for n in b.select('[id]')];assert len(ids)==len(set(ids))
assert all(n['href'][1:] in ids for n in b.select('a[href^="#"]') if n['href'][1:]);print('PASS IDs and links')
for ident in ['w04-detail-lda-discriminant-1d','w04-detail-lda-discriminant-multi','w04-detail-generative-uses']:
 d=b.select_one('#'+ident);assert d and not d.has_attr('open') and not d.find_parent('details');print('PASS independent disclosure',ident)
assert max(len(n.find_parents('details')) for n in b.select('details'))<=1
logistic=b.select_one('#logistic').get_text();assert logistic.index('準完全分離')<logistic.index('摘要表為什麼用 z');print('PASS separation defined before use')
assert '平平均' not in text and '$\\Sigma$_j' not in text
# Recompute the log-density identities, independently of page rendering.
x=.3;mu=np.array([-1.,2.]);v=1.7;prior=np.array([.4,.6])
logweighted=np.log(prior)-.5*np.log(2*np.pi*v)-(x-mu)**2/(2*v)
delta=x*mu/v-mu**2/(2*v)+np.log(prior)
constant=-.5*np.log(2*np.pi*v)-x*x/(2*v)
assert np.allclose(logweighted,delta+constant);print('PASS one-dimensional discriminant expansion')
x=np.array([.3,-.8]);means=np.array([[-1.,.2],[2.,1.1]]);cov=np.array([[1.7,.4],[.4,.9]])
inv=np.linalg.inv(cov);d=x-means
logweighted=np.log(prior)-len(x)/2*np.log(2*np.pi)-.5*np.linalg.slogdet(cov)[1]-.5*np.einsum('ij,jk,ik->i',d,inv,d)
delta=means@inv@x-.5*np.einsum('ij,jk,ik->i',means,inv,means)+np.log(prior)
constant=-len(x)/2*np.log(2*np.pi)-.5*np.linalg.slogdet(cov)[1]-.5*x@inv@x
assert np.allclose(logweighted,delta+constant);print('PASS multivariate discriminant expansion')
assert round((9/29)/.067,1)==4.6;print('PASS same-test-set Caravan ratio 4.6')
old=hashlib.sha256((root/'classification.html').read_bytes()).hexdigest()
for cmd in [['python','tools/build_page.py','classification'],['python','tools/rebuild_content.py','classification'],['python','tools/inject_data.py','classification']]:subprocess.run(cmd,cwd=root,check=True)
new=hashlib.sha256((root/'classification.html').read_bytes()).hexdigest();assert old==new;print('PASS idempotent rebuild',new)
