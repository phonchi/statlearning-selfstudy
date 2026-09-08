"""Final local source/assembly checks. Browser and network logs are separate."""
import hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
files=[*sorted(ROOT.glob('*.html')),ROOT/'README.md']
def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
before=hashes()
with (HERE/'run.log').open('w') as log:
    for tool in ['rebuild_content.py','inject_data.py','build_page.py','build_index.py','check_reader_contract.py','check_lab_rendered.py','test_reader_sources.py','test_statistics_contract.py','check_visual_claims.py','validate.py']:
        command=[sys.executable,'tools/'+tool]
        log.write('\nCOMMAND '+ ' '.join(command)+'\n');log.flush()
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    subprocess.run(['git','diff','--check'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    after=hashes();changed=[p for p in before if before[p]!=after[p]]
    log.write('\nIdempotent full rebuild: '+str(not changed)+'; changed='+str(changed)+'\n')
    if changed:raise SystemExit('Unexpected rebuild drift: '+str(changed))
(HERE/'idempotence.json').write_text(json.dumps({'checked_files':len(files),'changed':changed,'sha256':after},indent=2)+'\n')
(HERE/'final-manifest.json').write_text(json.dumps({'git_root':str(ROOT),'base_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'course_commit':'7c215512b38ed57a98d3289d83030c582a03eeb4','generated_sha256':after,'source_hashes':'sources.json'},indent=2)+'\n')
print('PASS final local checks; 28 generated files rebuild identically; git diff --check clean.')
