"""Validate the reader simplification and audited vocabulary selection."""
import hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rebuild_content import frame_declarations
base=json.loads((HERE/'baseline.json').read_text())['head']
files=[*sorted(ROOT.glob('*.html')),ROOT/'README.md']
def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
before=hashes()
with (HERE/'run.log').open('w') as log:
 for tool in ['build_page.py','rebuild_content.py','inject_data.py','build_index.py','check_taiwan_wording.py','check_reader_contract.py','check_lab_rendered.py','test_flashcard_scope.py','test_taiwan_wording.py','test_reader_sources.py','test_statistics_contract.py','check_visual_claims.py','validate.py']:
  cmd=[sys.executable,'tools/'+tool];print('COMMAND',' '.join(cmd),file=log,flush=True);subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 subprocess.run([sys.executable,str(HERE/'check_card_decisions.py')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 for p in ROOT.glob('*.html'):
  old=subprocess.check_output(['git','show',base+':'+p.name],cwd=ROOT,text=True)
  assert frame_declarations(old)==frame_declarations(p.read_text()),p.name
 print('PASS all FRAMES unchanged; no statistical model regenerated.',file=log)
 after=hashes();assert before==after,'Rebuild drift'
 print('PASS 28 generated files rebuild identically.',file=log)
 subprocess.run(['git','diff','--check'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
(HERE/'final-manifest.json').write_text(json.dumps({'base':base,'generated_sha256':after,'idempotent':True},indent=2)+'\n')
print('PASS: final checks, all source/array protection and idempotent rebuild.')
