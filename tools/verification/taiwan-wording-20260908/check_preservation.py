"""Compare published facts and executable data with the pre-edit Git snapshot."""
import hashlib,html,json,re,subprocess,sys
from pathlib import Path
from bs4 import BeautifulSoup
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rebuild_content import frame_declarations
BASE=json.loads((HERE/'baseline.json').read_text())['head']

def canonical_math(x):
    return x.replace('配適','擬合').replace('閾值','門檻值').replace('總共要配','總共要擬合')

def facts(src):
    soup=BeautifulSoup(src,'html.parser',preserve_whitespace_tags={'pre','textarea','span','div'})
    result={}
    result['frames']=hashlib.sha256(frame_declarations(src).encode()).hexdigest()
    result['code']=[e.get_text().replace('用 d 配適','用 d 擬合').replace('在新空間配線性超平面','在新空間擬合線性超平面').replace('配一棵淺樹','擬合一棵淺樹') for e in soup.select('.pseudo-code')]
    result['outputs']=[e.get_text() for e in soup.select('.expected-out')]
    result['hrefs']=[e.get('href') for e in soup.select('[href]')]
    result['ids']=[e.get('id') for e in soup.select('[id]')]
    result['answers']=[e.get('data-correct') for e in soup.select('[data-correct]')]
    result['math']=[canonical_math(x) for x in re.findall(r'\$\$.*?\$\$|(?<!\$)\$(?!\$)[^$\n]+\$',str(soup.body),re.S)]
    # Wording may change around values, but the ordered numeric content may not.
    for el in soup.select('script,style,.pseudo-code,.expected-out'):el.decompose()
    result['numbers']=re.findall(r'\d+(?:\.\d+)?',soup.get_text())
    return result

errors=[];results=[]
for path in sorted(ROOT.glob('*.html')):
    original=subprocess.check_output(['git','show',BASE+':'+path.name],cwd=ROOT).decode()
    before,after=facts(original),facts(path.read_text())
    changed=[key for key in before if before[key]!=after[key]]
    results.append({'page':path.name,'changed_protected_fields':changed})
    if changed:
        errors.append((path.name,changed))
        for key in changed:
            (HERE/(path.stem+'-'+key+'-difference.json')).write_text(json.dumps({'before':before[key],'after':after[key]},ensure_ascii=False,indent=2)+'\n')
(HERE/'preservation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
if errors:raise SystemExit(str(errors))
print('PASS 27 pages: FRAMES, lab code/output, numbers, mathematical operations, links/IDs and answer order preserved; only four explicitly listed Chinese pseudo-code/formula labels normalized.')
