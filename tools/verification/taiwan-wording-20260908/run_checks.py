"""Repeat local wording/provenance checks and verify idempotent assembly."""
from pathlib import Path
import hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
files=[*sorted(ROOT.glob('*.html')),ROOT/'README.md']
def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
before=hashes()
with (HERE/'run.log').open('w') as log:
 for name in ['rebuild_content.py','inject_data.py','build_page.py','build_index.py','check_taiwan_wording.py','check_lab_rendered.py','test_taiwan_wording.py','test_reader_sources.py','test_statistics_contract.py','check_reader_contract.py','check_visual_claims.py','validate.py']:
  cmd=[sys.executable,'tools/'+name];print('COMMAND',' '.join(cmd),file=log,flush=True);subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 subprocess.run([sys.executable,str(HERE/'check_preservation.py')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 after=hashes();changed=[f for f in before if before[f]!=after[f]]
 print('Idempotent rebuild:',not changed,file=log)
 if changed:raise SystemExit(changed)
(HERE/'final-manifest.json').write_text(json.dumps({'base':json.loads((HERE/'baseline.json').read_text())['head'],'generated_sha256':after,'idempotent':not changed},indent=2)+'\n')
print('PASS: all local checks and idempotent rebuild.')
