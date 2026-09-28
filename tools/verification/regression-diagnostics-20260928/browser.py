from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path('/home/phonchi/statlearning-selfstudy');OUT=ROOT/'tools/verification/regression-diagnostics-20260928';SHOTS=OUT/'shots';SHOTS.mkdir(exist_ok=True)
ids=json.loads((OUT/'supplement_ids.json').read_text());reports=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
 for width in [1440,390]:
  page=browser.new_page(viewport={'width':width,'height':1000},device_scale_factor=1)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto((ROOT/'linear_regression.html').as_uri(),wait_until='networkidle',timeout=60000)
  page.evaluate('async()=>{await MathJax.startup.promise;await document.fonts.ready;}')
  assert page.locator('mjx-container').count()>0
  assert page.locator('mjx-merror').count()==0
  for id in ids:
   d=page.locator('#'+id);assert d.get_attribute('open') is None
   d.locator('summary').click();assert d.get_attribute('open') is not None
   page.evaluate('async()=>{await MathJax.startup.promise;}')
   assert d.locator('mjx-container').count()>0,id
   assert d.locator('mjx-merror').count()==0,id
   box=d.bounding_box();assert box['x']>=-1 and box['x']+box['width']<=width+1,(id,box)
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),('Page overflow',width,id)
   d.screenshot(path=str(SHOTS/f'{id}-{width}.png'))
   reports.append({'width':width,'id':id,'formulas':d.locator('mjx-container').count(),'bounds':box})
   d.locator('summary').click();assert d.get_attribute('open') is None
  # Existing diagnosis controls must still change actual chart data.
  page.locator('#w03diagSel').select_option('autocorr')
  page.locator('button[onclick="w03diagView(1)"]').click()
  assert page.locator('#w03diagStatus').inner_text().strip()
  page.locator('#w03diagSel').select_option('lever')
  page.locator('button[onclick="w03diagView(3)"]').click()
  assert 'NaN' not in page.locator('#w03diagStatus').inner_text()
  page.locator('#w03vifRho').evaluate("e=>{e.value='800';e.dispatchEvent(new Event('input',{bubbles:true}));}")
  assert abs(float(page.locator('#w03vifVif').inner_text())-1/(1-.8**2))<.02
  page.locator('button[onclick="w03vifHome()"]').click();assert page.locator('#w03vifVif').inner_text()=='1.00'
  page.locator('#vsknn').screenshot(path=str(SHOTS/f'knn-{width}.png'))
  assert not errors,errors
  print('PASS browser:',width,'8 disclosures, MathJax, no page overflow, diagnosis controls and VIF slider.',flush=True)
  page.close()
 browser.close()
(OUT/'browser.json').write_text(json.dumps(reports,indent=2)+'\n')
