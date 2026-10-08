from pathlib import Path
import json
from playwright.sync_api import sync_playwright
root=Path('/home/phonchi/statlearning-selfstudy'); out=root/'tools/verification/cv-details-20261008'
report=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True)
 for width in [1440,390]:
  page=b.new_page(viewport={'width':width,'height':1000})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto((root/'resampling_methods.html').as_uri(),wait_until='networkidle')
  page.wait_for_function('window.MathJax && MathJax.typesetPromise',timeout=30000)
  for did in ['w05-detail-splitters','w05-detail-nested-cv']:
   d=page.locator('#'+did)
   assert not d.evaluate('(e)=>e.open')
   d.locator('summary').click();assert d.evaluate('(e)=>e.open')
   page.evaluate('()=>MathJax.typesetPromise()')
   assert page.locator('mjx-merror').count()==0
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(width,did,'page overflow')
   d.locator('summary').screenshot(path=str(out/(did+'-'+str(width)+'-summary.png')))
   # 詳細內容較長，分別保存收合区頂端與比較表。
   page.screenshot(path=str(out/(did+'-'+str(width)+'-open.png')))
   if did=='w05-detail-nested-cv':
    d.locator('table').screenshot(path=str(out/('nested-table-'+str(width)+'.png')))
    assert d.locator('tbody tr').count()==11
   d.locator('summary').click();assert not d.evaluate('(e)=>e.open')
   report.append({'width':width,'detail':did,'collapse':'PASS','overflow':'PASS','mathjax':'PASS'})
  assert not errors,errors
  page.close()
 b.close()
(out/'browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
