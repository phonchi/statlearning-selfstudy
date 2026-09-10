import concurrent.futures,hashlib,json,re,time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pymupdf
V=Path('/home/phonchi/statlearning-selfstudy/tools/verification/coverage-20260910');D=V/'ch1-6-link-text';D.mkdir(exist_ok=True)
ledger=json.loads((V/'ch1-6-links.json').read_text())
pending=[x for x in ledger if x['status'].startswith('原文未讀')]
unique={re.sub('#.*','',x['url']):x for x in pending}
def get(item):
 u,x=item;key=hashlib.sha256(u.encode()).hexdigest()[:14];meta={'url':u,'file':key+'.txt','pdf':x['pdf'],'pages':x['pages']}
 try:
  r=requests.get(u,timeout=22,headers={'User-Agent':'Mozilla/5.0 (compatible; educational-source-verification)'});meta.update(status_code=r.status_code,final_url=r.url,content_type=r.headers.get('content-type',''))
  if r.status_code>=400:meta['status']='blocked_http';text=r.text[:700]
  elif r.content.startswith(b'%PDF'):
   doc=pymupdf.open(stream=r.content,filetype='pdf');text='\n'.join(f'PDF PAGE {i+1}\n'+pg.get_text() for i,pg in enumerate(doc));meta.update(status='fetched_unreviewed',pdf_pages=len(doc))
  else:
   soup=BeautifulSoup(r.content,'html.parser');title=soup.title.get_text(' ',strip=True) if soup.title else '';meta['title']=title
   if any(z.lower() in title.lower() for z in ['Just a moment','Access Denied','Attention Required','Captcha']):meta['status']='blocked_challenge';text=soup.get_text(' ',strip=True)[:700]
   else:
    for e in soup.select('script,style,nav,footer,header,aside'):e.decompose()
    if 'stackexchange.com' in u or 'stackoverflow.com' in u:
     nodes=soup.select('.question .s-prose,.answer .s-prose,.question .post-text,.answer .post-text');text='\n\n'.join(n.get_text(' ',strip=True) for n in nodes)
    else:
     node=soup.select_one('main,article,#mw-content-text,#main-content,.document') or soup;text=node.get_text('\n',strip=True)
    meta['status']='fetched_unreviewed' if len(text)>120 else 'blocked_empty'
  meta['chars']=len(text);(D/meta['file']).write_text(text)
 except Exception as e:meta.update(status='blocked_error',error=str(e))
 return meta
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
 results=list(ex.map(get,unique.items()))
(V/'ch1-6-fetch.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
from collections import Counter
print(Counter(x['status'] for x in results))
for i,x in enumerate(results):print(i,x['status'],x.get('status_code'),x.get('chars'),x['url'])
