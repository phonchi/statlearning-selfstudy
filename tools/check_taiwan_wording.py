"""Reader terminology guard; preserve technical uses and original lab quotations."""
import json,re
from pathlib import Path
from html.parser import HTMLParser
from check_reader_contract import Visible
from rebuild_content import frame_declarations
from validate import js_strings, pagejs
ROOT=Path(__file__).resolve().parent.parent
# Explicit house terminology and clearly inappropriate UI words, not a blanket
# ban on valid technical terms (e.g. 機率質量, 水平線, 正則化).
UNWANTED=re.compile(r'配適|擬和|拟合|閾值|似然|靈敏度|視頻|信息|軟件|硬件|內存|屏幕|鼠標|打印|默認|網絡|反饋|置信區間|貝葉斯|概率|工作流|烘焙資料|嵌套')

def check_words(source):
    visible=Visible();visible.feed(source)
    parts=list(visible.text)
    for m in re.finditer(r'const (?:FLASHCARDS|BANKQUIZ) = ',source):
        payload,_=json.JSONDecoder().raw_decode(source[m.end():]);parts.append(json.dumps(payload,ensure_ascii=False))
    # FRAMES is historical scientific provenance, not reader copy. All other
    # per-page Chinese messages may appear only after an interaction.
    js=pagejs(source)
    for declaration in frame_declarations(js).splitlines():js=js.replace(declaration,'')
    parts.extend(s for s,_ in js_strings(js))
    return sorted(set(UNWANTED.findall('\n'.join(parts))))

if __name__=='__main__':
    failures=[]
    for path in sorted(ROOT.glob('*.html')):
        words=check_words(path.read_text())
        if words:failures.append(f'{path.name}: {", ".join(words)}')
    if UNWANTED.search((ROOT/'README.md').read_text()):failures.append('README.md: house terminology violation')
    if failures:raise SystemExit('\n'.join(failures))
    print('PASS Taiwan reader terminology across 27 pages, dynamic messages, quizzes/cards and README.')
