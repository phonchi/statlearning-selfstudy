"""Guard explicitly removed report content; source/scope judgments are in the audit."""
from pathlib import Path
import json,re
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'tools/verification/teaching-scope-20260910'
bad=[];rows=[]
REPORT_TERMS=['老師在課程環境實跑','本頁逐格重現','本頁模擬跑出來的數字',
              '延伸閱讀：重現方式與環境版本','本頁「預期輸出」逐字取自','tools/frames/']
SPECIFIC={
 'introduction':['同一組資料，親手比較摘要','中位數的穩健性與相對效率','資料表的形狀與合併鍵'],
 'statistical_learning':['蒙地卡羅的重現性','用等高線圖看一個指定的 f(x, y)',
   '雜訊讓相關係數到不了 1','讀 Auto 並處理遺漏值','樣本平均本身還不是',
   '本頁模擬的完整數字']
}
for p in sorted(ROOT.glob('*.html')):
 d=BeautifulSoup(p.read_text(),'html.parser')
 for el in d.select('script,style'):el.decompose()
 text=d.get_text(' ',strip=True)
 if d.select('.ver-note'):bad.append(f'{p.name}: production ver-note still rendered')
 for token in REPORT_TERMS+SPECIFIC.get(p.stem,[]):
  if token in text:bad.append(f'{p.name}: removed report/example still visible: {token}')
 for detail in d.select('details.reading-detail'):
  body=detail.select_one('.detail-body')
  if body is None or not body.get_text(' ',strip=True) and not body.select('svg,canvas,input,button,#fcGrid,#bqBox'):
   bad.append(f'{p.name}: empty detail {detail.get("id")}')
 rows.append({'page':p.stem,'lab_cards':len(d.select('.deck-extra')),'proofs':len(d.select('details.proof')),
              'reading_details':len(d.select('details.reading-detail')),'quiz_count':len(d.select('.quiz-box'))})
svm=BeautifulSoup((ROOT/'support_vector_machines.html').read_text(),'html.parser')
for anchor in ['w10-primal-dual','w10-soft-dual','w10-proof-hard-dual','w10-proof-soft-dual']:
 if not svm.find(id=anchor):bad.append('Required lecture SVM math missing: '+anchor)
idx=BeautifulSoup((ROOT/'index.html').read_text(),'html.parser')
order=[a['href'] for a in idx.select('#core .ch-card')]
if order.index('unsupervised_learning.html')!=order.index('support_vector_machines.html')+1:
 bad.append('Lecture order changed')
OUT.mkdir(exist_ok=True,parents=True)
(OUT/'scope-check.json').write_text(json.dumps({'pages':rows,'failures':bad},ensure_ascii=False,indent=2)+'\n')
for x in bad:print('FAIL',x)
print(f'{len(rows)} HTML pages; {len(bad)} teaching-scope failures')
raise SystemExit(bool(bad))
