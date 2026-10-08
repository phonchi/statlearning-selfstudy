from pathlib import Path
import re,json,hashlib,sys,subprocess,collections
from bs4 import BeautifulSoup
root=Path('/home/phonchi/statlearning-selfstudy');evidence=root/'tools/verification/lecture-alignment-20261008';manifest=json.loads((evidence/'source_manifest.json').read_text())
sys.dont_write_bytecode=True;sys.path.insert(0,str(root/'tools/enrich'))
from lib import splice_section
from reader_sources import fragment
modules={5:'enrich_resampling',6:'enrich_modelsel',7:'enrich_nonlin',8:'enrich_trees',9:'enrich_svm',12:'enrich_unsup'}
report=[]
for item in manifest['chapters']:
 ch=item['chapter'];name=item['html'];actual=(root/name).read_text();baseline=(evidence/'inputs'/(name.removesuffix('.html')+'.baseline.html')).read_text()
 before=BeautifulSoup(baseline,'html.parser');after=BeautifulSoup(actual,'html.parser')
 for filename,digest in item['source_sha256'].items():
  assert hashlib.sha256((Path('/home/phonchi/nsysu-math524/static_files/presentations')/filename).read_bytes()).hexdigest()==digest
 ids_before={n['id'] for n in before.select('[id]')};ids_after={n['id'] for n in after.select('[id]')}
 assert ids_before<=ids_after,(ch,'removed ids',ids_before-ids_after)
 ids_list=[n['id'] for n in after.select('[id]')];assert len(ids_list)==len(set(ids_list)),(ch,'duplicate id')
 for pattern in [r'<!-- PAGEJS:BEGIN -->.*?<!-- PAGEJS:END -->',r'<!-- DATA:BEGIN -->.*?<!-- DATA:END -->',r'<!-- GEN:BEGIN .*?<!-- GEN:END .*?-->']:
  assert re.findall(pattern,actual,re.S)==re.findall(pattern,baseline,re.S),(ch,'protected generated payload changed')
 def payload(soup,selector):return collections.Counter(n.get_text() for n in soup.select(selector))
 for selector in ['.pseudo-code','.expected-out pre']:
  assert not payload(before,selector)-payload(after,selector),(ch,'old lab payload lost',selector)
 mod=__import__(modules[ch]); rebuilt=actual
 for sid,body in mod.BODIES.items():
  if sid=='exercises' and 'id="exercises"' not in rebuilt:continue
  rebuilt=splice_section(rebuilt,sid,fragment(body))
 assert rebuilt==actual,(ch,'generator parity/idempotence')
 if ch==5:
  pat=r'<!-- GEN:END sec:bootstrap -->.*?\n</section>'
  assert re.sub(pat,'BOOTSTRAP',actual,flags=re.S)==re.sub(pat,'BOOTSTRAP',baseline,flags=re.S)
 changed=[]
 for d in after.select('details.reading-detail'):
  old=before.find(id=d.get('id'))
  if old is None or old.get_text(' ',strip=True)!=d.get_text(' ',strip=True):
   changed.append({'id':d.get('id'),'summary':d.summary.get_text(' ',strip=True),'text_chars':len(d.get_text(' ',strip=True))})
 r=subprocess.run([sys.executable,str(root/'tools/validate.py'),'--page',name.removesuffix('.html')],capture_output=True,text=True)
 (evidence/f'ch{ch}'/'final-validate.log').write_text(r.stdout+r.stderr)
 assert r.returncode==0,(ch,r.stdout,r.stderr)
 row={'chapter':ch,'html':name,'source_bytes_preserved':True,'all_old_ids_preserved':True,'GEN_PAGEJS_DATA_preserved':True,'old_code_blocks':sum(payload(before,'.pseudo-code').values()),'old_outputs':sum(payload(before,'.expected-out pre').values()),'old_lab_payload_preserved':True,'generator_parity_and_idempotence':True,'changed_details':changed,'html_sha256':hashlib.sha256(actual.encode()).hexdigest()}
 report.append(row)
 print(ch,name,'PASS; changed details',len(changed))
(evidence/'global-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
