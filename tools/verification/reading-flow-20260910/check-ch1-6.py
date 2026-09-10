"""Reading-flow checks. No lab/FRAMES regeneration, no source writes."""
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib,json,re,sys,subprocess
V=Path(__file__).resolve().parent
R=V.parents[2]
baseline=json.loads((V/'ch1-6-before.json').read_text())
# The old snapshot used the default HTML parser and normalized indentation.
# It is not an authoritative code baseline. Use the unmodified course checker.
canonical = subprocess.run([sys.executable, 'tools/check_lab_rendered.py'], cwd=R,
                           capture_output=True, text=True)
(V/'ch1-6-canonical-lab.log').write_text(canonical.stdout + canonical.stderr)
assert canonical.returncode == 0, canonical.stdout + canonical.stderr
PRESERVE = {'pre', 'textarea', 'span', 'div'}
result=[]
for stem,old in baseline.items():
    raw=(R/f'{stem}.html').read_text();s=BeautifulSoup(raw,'html.parser',preserve_whitespace_tags=PRESERVE)
    # Full code cards were checked against the original cited lab cells above.
    assert [n.get_text() for n in s.select('.expected-out')]==old['expected_output'],(stem,'saved output')
    frames=hashlib.sha256('\n'.join(re.findall(r'^const FRAMES_.*$',raw,re.M)).encode()).hexdigest()
    assert frames==old['frames_sha256'],(stem,'frames')
    for title in s.select('h3,h4'):
        if title.get_text(' ',strip=True) in ['蒙地卡羅的重現性','本頁模擬跑出來的數字','公式速查']:
            assert title.find_parent('details',class_='reading-detail'),(stem,'ungrouped detail heading',title.get_text())
    for note in s.select('.ver-note'):
        assert note.find_parent('details',class_='reading-detail'),(stem,'visible environment note')
    details=s.select('details.reading-detail')
    assert details and all(not d.has_attr('open') for d in details),(stem,'default closed')
    assert all(len(d.find_parents('details'))<=1 for d in s.select('details')),(stem,'depth')
    allids=[n['id'] for n in s.select('[id]')];assert len(allids)==len(set(allids)),(stem,'duplicate id')
    # Core quizzes stay outside details; only explicitly advanced exercises move.
    folded=[]
    for q in s.select('section .quiz-box'):
        d=q.find_parent('details',class_='reading-detail')
        if d and not d.get('id','').endswith(('-bank','bankquiz')):
            label=q.select_one('.quiz-label').get_text(' ',strip=True)
            assert label.startswith('延伸自測'),(stem,d.get('id'),label)
            folded.append(label)
    controls=[]
    for d in details:
        for btn in d.select('button[onclick]'):
            action=btn.get('onclick','')
            assert not re.search(r'(?:Player|\.play\(|setInterval|Many\()',action),(stem,d.get('id'),action)
            controls.append({'detail':d.get('id'),'action':action})
    result.append({'page':stem,'canonical_lab_code_and_output_pass':True,'all_saved_output_identical':True,'frames_sha256':frames,'detail_count':len(details),'folded_quizzes':folded,'folded_buttons':controls})
intro=BeautifulSoup((R/'introduction.html').read_text(),'html.parser')
for unwanted in ['同一組資料，親手比較摘要','中位數的穩健性與相對效率','資料表的形狀、合併鍵與來源','w01proofMedianEfficiency']:
    assert unwanted not in str(intro),unwanted
eda=intro.select_one('#eda');core=BeautifulSoup(str(eda),'html.parser')
for d in core.select('details'):d.decompose()
for term in ['平均數','中位數','截尾平均數','眾數','變異數','平均絕對離差','中位絕對離差','四分位距']:
    assert term in core.get_text(),('intro missing core statistic',term)
st=BeautifulSoup((R/'statistical_learning.html').read_text(),'html.parser');core=BeautifulSoup(str(st.select_one('#curse')),'html.parser')
assert st.select_one('#w02-detail-geometry #w02curChart')
for d in core.select('details'):d.decompose()
for advanced in ['Gamma','Stirling','\\Gamma','99.5%','89%','89.1%']:
    assert advanced not in str(core),('geometry leaked',advanced)
assert core.select_one('#qCurOptions') and '有效維度' in core.get_text()
(V/'ch1-6-static.json').write_text(json.dumps({'result':'PASS','pages':result},ensure_ascii=False,indent=2)+'\n')
print('PASS: 6 chapters; original lab/output/FRAMES retained; deleted Ch1 topics absent; core statistics and qCur visible; details closed and depth <= 2')
