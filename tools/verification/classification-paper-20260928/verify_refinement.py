from pathlib import Path
from bs4 import BeautifulSoup
import hashlib,json,re,subprocess,sys
import numpy as np
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
original=Path(sys.argv[1]).read_text();current=(root/'classification.html').read_text()
opts={'preserve_whitespace_tags':{'pre','span','div'}}
a=BeautifulSoup(original,'html.parser',**opts);b=BeautifulSoup(current,'html.parser',**opts)
for sel in ['.pseudo-code','.expected-out']:
 assert sorted(n.get_text() for n in a.select(sel))==sorted(n.get_text() for n in b.select(sel));print('PASS unchanged',sel,len(a.select(sel)))
proofs=lambda s:{d['id']:str(d) for d in s.select('details.proof')}
assert proofs(a)==proofs(b);print('PASS all original proof blocks unchanged',len(proofs(a)))
frames=lambda s:dict(re.findall(r'^const (FRAMES_\w+)\s*=\s*(.*?);\s*$',s,re.M))
assert frames(original)==frames(current);print('PASS baked frames unchanged')
assert current.count('$$')-original.count('$$')==2;print('PASS one added display formula (softmax)')
assert len(json.loads((root/'data/flashcards_zh/ch4.json').read_text()))==29
ids=[n['id'] for n in b.select('[id]')];assert len(ids)==len(set(ids));assert all(n['href'][1:] in ids for n in b.select('a[href^="#"]') if n['href'][1:]);print('PASS anchors')
assert not b.select('details[open]');assert max(len(d.find_parents('details')) for d in b.select('details'))<=1;print('PASS reading layers')
# Independent Bayes/softmax and whitening check.
means=np.array([[-1.,.2],[.5,1.2],[1.7,-.9]]);cov=np.array([[2.,.5],[.5,1.]]);prior=np.array([.2,.3,.5]);x=np.array([.4,-.7]);inv=np.linalg.inv(cov)
delta=means@inv@x-.5*np.einsum('ij,jk,ik->i',means,inv,means)+np.log(prior)
prob=np.exp(delta-delta.max());prob/=prob.sum()
diff=x-means;weighted=prior*np.exp(-.5*np.einsum('ij,jk,ik->i',diff,inv,diff))/np.sqrt(np.linalg.det(cov));weighted/=weighted.sum()
assert np.allclose(prob,weighted);print('PASS LDA softmax recovers Bayes posterior')
v,U=np.linalg.eigh(cov);A=U@np.diag(1/np.sqrt(v))@U.T
assert np.allclose(A@cov@A.T,np.eye(2));assert np.allclose(np.sum((diff@A.T)**2,axis=1),np.einsum('ij,jk,ik->i',diff,inv,diff));print('PASS shared whitening and Mahalanobis interpretation')
h=hashlib.sha256((root/'classification.html').read_bytes()).hexdigest()
for cmd in [['python','tools/build_page.py','classification'],['python','tools/rebuild_content.py','classification'],['python','tools/inject_data.py','classification']]:subprocess.run(cmd,cwd=root,check=True)
assert h==hashlib.sha256((root/'classification.html').read_bytes()).hexdigest();print('PASS idempotent rebuild',h)
