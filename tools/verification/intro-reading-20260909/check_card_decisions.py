"""Every source card must be reviewed; published cards must be exactly KEEP."""
import json,subprocess
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
base=json.loads((HERE/'baseline.json').read_text())['head']
by_file=defaultdict(list)
core=json.loads((HERE/'cards-core.json').read_text())
for r in core['cards']:
    new={'front':r['front'],'back':r.get('wording_change',{}).get('after',r['back'])}
    if 'term_correction' in r:
        fix=r['term_correction'];new['front']=fix.get('after',fix.get('new',r['front']))
    by_file[r['file']].append((r,new))
advanced=json.loads((HERE/'cards-advanced.json').read_text())
for r in advanced['records']:
    by_file[r['file']].append((r,r.get('edit',{}).get('new',{'front':r['front'],'back':r['back']})))
appendices=json.loads((HERE/'cards-appendices.json').read_text())
for p in appendices['pages']:
    for r in p['cards']:
        new={'front':r.get('front_edit',{}).get('new',r['front']),
             'back':r.get('definition_edit',{}).get('new',r['back'])}
        by_file[p['file']].append((r,new))
checked=removed=kept=0
for f,rows in sorted(by_file.items()):
    original=json.loads(subprocess.check_output(['git','show',base+':'+f],cwd=ROOT,text=True))
    rows.sort(key=lambda x:x[0]['original_index'])
    assert [r['original_index'] for r,_ in rows]==list(range(1,len(original)+1)),f
    want=[new for r,new in rows if r['decision']=='KEEP']
    got=json.loads((ROOT/f).read_text())
    assert got==want,f
    for r,_ in rows:
        assert r['reason'].strip(),f
        assert r['decision'] in ('KEEP','REMOVE'),f
    checked+=len(rows);kept+=len(want);removed+=len(rows)-len(want)
assert len(by_file)==26
print(f'PASS: {checked} individually reviewed; {removed} removed; {kept} kept; all 26 files exactly match audited decisions.')
