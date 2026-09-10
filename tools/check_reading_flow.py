"""Structural guards for the approved reading layers; semantic review is recorded separately."""
from pathlib import Path
import json,re,subprocess
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'tools/verification/teaching-scope-20260910'
failures=[];pages=[]

def main_text(doc):
    for el in doc.select('script,style,details'):el.decompose()
    container=doc.select_one('.container') or doc
    return container.get_text(' ',strip=True)

for path in sorted(ROOT.glob('*.html')):
    if path.stem=='index':continue
    text=path.read_text();doc=BeautifulSoup(text,'html.parser')
    units=doc.select('details.reading-detail')
    for d in units:
        if d.has_attr('open'):failures.append(f'{path.name}: open detail {d.get("id")}')
        if not d.get('id') or not d.find('summary',recursive=False):failures.append(f'{path.name}: unlabelled detail')
    for d in doc.select('details'):
        if len(d.find_parents('details'))>1:failures.append(f'{path.name}: >2 disclosure levels at {d.get("id")}')
    ids=[e['id'] for e in doc.select('[id]')]
    if len(ids)!=len(set(ids)):failures.append(f'{path.name}: duplicate IDs')
    visible_quiz=[q for q in doc.select('.quiz-box') if not q.find_parent('details')]
    baseline=subprocess.check_output(['git','show',f'HEAD:{path.name}'],cwd=ROOT).decode()
    # The teaching-scope cleanup explicitly removes unsupported examples and
    # their anchors. Validate remaining links, not a quota of historical IDs.
    from urllib.parse import unquote
    for link in doc.select('a[href^="#"]'):
        target=unquote(link['href'][1:])
        if target and target not in ids:
            failures.append(f'{path.name}: unresolved current link #{target}')
    before=len(main_text(BeautifulSoup(baseline,'html.parser')))
    after=len(main_text(BeautifulSoup(text,'html.parser')))
    pages.append({'page':path.stem,'details':len(units),'main_text_characters_before':before,
                  'main_text_characters_after':after,'visible_core_quizzes':len(visible_quiz),
                  'detail_titles':[d.find('summary',recursive=False).get_text(' ',strip=True) for d in units]})

intro=(ROOT/'introduction.html').read_text()
for title in ['同一組資料，親手比較摘要','中位數的穩健性與相對效率','資料表的形狀與合併鍵','w01proofMedianEfficiency']:
    if title in intro:failures.append('Explicitly deleted intro content restored: '+title)
if '先用摘要統計量認識資料' not in intro:failures.append('Missing concise EDA introduction')
curse=BeautifulSoup((ROOT/'statistical_learning.html').read_text(),'html.parser').select_one('#curse')
for n in curse.find_all(string=True):
    if any(s in str(n) for s in ['\\Gamma','Stirling','V_{\\text{ball}}']):
        if not n.find_parent('details',class_='reading-detail'):
            failures.append('High-dimensional geometry remains on main reading path: '+str(n)[:80])
OUT.mkdir(exist_ok=True,parents=True)
(OUT/'reading-inventory.json').write_text(json.dumps({'pages':pages,'failures':failures},ensure_ascii=False,indent=2)+'\n')
for e in failures:print('FAIL',e)
print(f'{len(pages)} pages; {sum(p["details"] for p in pages)} reading details; {len(failures)} failures')
raise SystemExit(bool(failures))
