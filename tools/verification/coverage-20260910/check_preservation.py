"""Verify that adding teaching text did not silently replace baked experiments or Lab sources."""
from pathlib import Path
import hashlib,json,re,subprocess

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent

def frames(s):
    found={}
    for m in re.finditer(r'(?:const|let|var)\s+(FRAMES_\w+)\s*=\s*',s):
        obj,_=json.JSONDecoder().raw_decode(s[m.end():])
        found[m.group(1)]=hashlib.sha256(json.dumps(obj,sort_keys=True).encode()).hexdigest()
    return found

rows=[]
for p in sorted(ROOT.glob('*.html')):
    old=subprocess.check_output(['git','show',f'HEAD:{p.name}'],cwd=ROOT).decode()
    before=frames(old);after=frames(p.read_text())
    assert before==after,('baked frames changed',p.name)
    rows.append({'page':p.name,'baked_frames':len(before),'status':'unchanged'})
for p in sorted((ROOT/'data/source_index').glob('lab_ch*.md')):
    rel=p.relative_to(ROOT)
    before=subprocess.check_output(['git','show',f'HEAD:{rel}'],cwd=ROOT)
    assert before==p.read_bytes(),('Lab index changed',str(rel))
    rows.append({'source':str(rel),'sha256':hashlib.sha256(before).hexdigest(),'status':'unchanged'})
(OUT/'preservation.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('PASS: every baked FRAMES object and all existing Lab source indexes match HEAD.')
print('Pages:',sum('page' in r for r in rows),'frame objects:',sum(r.get('baked_frames',0) for r in rows),
      'Lab indexes:',sum('source' in r for r in rows))
