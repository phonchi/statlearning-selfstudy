"""Independent content/numeric acceptance for this chapter revision; no source writes."""
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib, json, math, re, sys
import numpy as np
root=Path(__file__).resolve().parents[3]
html=(root/'classification.html').read_text()
soup=BeautifulSoup(html,'html.parser',preserve_whitespace_tags={'pre','span','div'})
main=BeautifulSoup(html,'html.parser')
for n in main.select('details,script,style'):n.decompose()
text=main.get_text(' ',strip=True)
checks={
 'bernoulli_natural':'單次的 0／1 結果' in text and 'Bernoulli' in text,
 'conditional_mean':'E(Y\\mid X=x)' in text,
 'variance':'p(x)\\{1-p(x)\\}' in text,
 'linear_classifier':'分類是根據' in text and '線性函數來決定' in text,
 'mle_z':'MLE 的大樣本常態近似' in text,
 'categorical_predictors':'indicator' in text and 'J-1' in text,
 'categorical_response':'\\operatorname{Categorical}' in text,
 'generative_discriminative':'discriminative model' in text and 'generative model' in text,
 'lda_estimates':'\\hat\\pi_k=\\frac{n_k}{n}' in text and '\\hat\\Sigma=\\frac1{n-K}' in text,
 'lda_linear':'c_{k0}+c_{k1}x_1' in text,
 'poisson_not_automatic':'計數不一定服從 Poisson' in text,
 'glm_g_eta':r'g\big(\mathbb{E}(Y\mid X)\big) = \eta(X)' in html,
 'removed_ovr':not soup.select('#w04-detail-ovr-ovo'),
 'removed_gamma':not any('Gamma' in n.get_text() for n in soup.select('#poisson p,#poisson table')),
}
for id_ in ['w04-detail-odds','w04-detail-z-t','w04-detail-multinomial-fit','w04-detail-fisher','w04proofGenerative','w04proofOlsLda','w04proofLogistic']:
 checks[id_]=bool(soup.select('#'+id_))
ids=[n['id'] for n in soup.select('[id]')];checks['unique_ids']=len(ids)==len(set(ids))
checks['detail_depth']=max(len(n.find_parents('details')) for n in soup.select('details'))<=1
checks['default_collapsed']=not soup.select('details[open]')
checks['internal_links']=all(not n['href'][1:] or n['href'][1:] in ids for n in soup.select('a[href^="#"]'))
checks['lecture_order']=[n['id'] for n in soup.select('section[id]')][:8]==['prologue','logistic','multinomial','lda','threshold','qda','compare','poisson']
# Numeric checks independent of page widget code.
checks['categorical_example']=math.isclose(.7*.7*.6,.294)
checks['odds']=math.isclose(.37/(1+.37),.27007299270072993)
checks['binary_variance']=all(math.isclose(p*(1-p)**2+(1-p)*p*p,p*(1-p)) for p in [.01,.2,.5,.8,.99])
X=np.array([[-2.,0.],[-1.,1.],[0.,0.],[2.,1.],[3.,2.],[4.,1.]])
y=np.array([0,0,0,1,1,1]);mu=np.array([X[y==k].mean(axis=0) for k in range(2)])
W=sum((X[y==k]-mu[k]).T@(X[y==k]-mu[k]) for k in range(2));S=W/4
v,U=np.linalg.eigh(S);whitener=U@np.diag(1/np.sqrt(v))@U.T
priors=np.array([.4,.6]);x=np.array([.7,2.3]);z=whitener@x;m=mu@whitener.T
scores=mu@np.linalg.solve(S,x)-.5*np.einsum('ij,ij->i',mu,mu@np.linalg.inv(S))+np.log(priors)
dist=-.5*np.sum((m-z)**2,axis=1)+np.log(priors)
direction=m[1]-m[0];direction/=np.linalg.norm(direction)
zproj=m[0]+direction*np.dot(z-m[0],direction)
projected=-.5*np.sum((m-zproj)**2,axis=1)+np.log(priors)
checks['lda_score_distance']=np.allclose(scores-scores[0],dist-dist[0])
checks['whitening']=np.allclose(whitener@S@whitener.T,np.eye(2))
checks['affine_projection']=np.allclose(dist-dist[0],projected-projected[0])
eta=np.array([[.3,.7,-.2],[-1.2,.1,.4]])
softmax=lambda a:np.exp(a-a.max(axis=1,keepdims=True))/np.exp(a-a.max(axis=1,keepdims=True)).sum(axis=1,keepdims=True)
checks['softmax_baseline']=np.allclose(softmax(eta),softmax(eta-eta[:,-1:]))
# Compare original by file passed at invocation; no need to depend on Git state.
if len(sys.argv)>1:
 old=Path(sys.argv[1]).read_text();orig=BeautifulSoup(old,'html.parser',preserve_whitespace_tags={'pre','span','div'})
 for selector in ['.pseudo-code','.expected-out']:
  checks[selector+' unchanged']=sorted(n.get_text() for n in orig.select(selector))==sorted(n.get_text() for n in soup.select(selector))
 frames=lambda t:dict(re.findall(r'^const (FRAMES_\w+)\s*=\s*(.*?);\s*$',t,re.M))
 checks['frames unchanged']=frames(old)==frames(html)
for k,v in checks.items():print(('PASS' if v else 'FAIL')+' '+k)
print('SHA256',hashlib.sha256(html.encode()).hexdigest())
raise SystemExit(not all(checks.values()))
