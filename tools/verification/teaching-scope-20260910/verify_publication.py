"""Compare every published HTML byte-for-byte with the committed local pages."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[3]
BASE='https://phonchi.github.io/statlearning-selfstudy/'
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
def one(p):
 expected=hashlib.sha256(p.read_bytes()).hexdigest()
 url=BASE+p.name+'?revision='+commit
 with urlopen(Request(url,headers={'Cache-Control':'no-cache'}),timeout=60) as r:
  actual=hashlib.sha256(r.read()).hexdigest();status=r.status
 return {'page':p.name,'status':status,'local_sha256':expected,'online_sha256':actual,'match':expected==actual}
with ThreadPoolExecutor(max_workers=4) as pool:
 rows=list(pool.map(one,sorted(ROOT.glob('*.html'))))
out=Path(__file__).parent/'shots/publication.json';out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({'commit':commit,'base_url':BASE,'checked_unix':time.time(),'pages':rows},indent=2)+'\n')
print(commit,len(rows),'pages;',sum(not x['match'] for x in rows),'mismatches')
raise SystemExit(any(not x['match'] for x in rows))
