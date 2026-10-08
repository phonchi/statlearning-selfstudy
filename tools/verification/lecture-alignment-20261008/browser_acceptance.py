import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path('/home/phonchi/statlearning-selfstudy');OUT=ROOT/'tools/verification/lecture-alignment-20261008'
ROWS=json.loads((OUT/'global-checks.json').read_text())
async def inspect(browser,row,width):
 page=await browser.new_page(viewport={'width':width,'height':1000})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 await page.goto((ROOT/row['html']).as_uri(),wait_until='networkidle')
 await page.wait_for_function('window.MathJax && MathJax.typesetPromise',timeout=30000)
 await page.evaluate('()=>MathJax.typesetPromise()')
 assert await page.locator('mjx-merror').count()==0,(row['chapter'],width,'initial MathJax error')
 assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(row['chapter'],width,'initial overflow')
 tested=[];shots=OUT/'browser';shots.mkdir(exist_ok=True)
 for i,item in enumerate(row['changed_details']):
  d=page.locator('#'+item['id']);summary=d.locator(':scope > summary')
  assert not await d.evaluate('(e)=>e.open'),(item['id'],'not default collapsed')
  # 數學與DOM檢查以開啟後的實際內容為準。
  await summary.click()
  assert await d.evaluate('(e)=>e.open'),item['id']
  await page.evaluate('()=>MathJax.typesetPromise()')
  assert await page.locator('mjx-merror').count()==0,(row['chapter'],width,item['id'],'MathJax error')
  assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(row['chapter'],width,item['id'],'overflow')
  # 每個被改寫區段都留實際展開截圖，避免只有語法驗證。
  await summary.scroll_into_view_if_needed()
  await page.screenshot(path=str(shots/f'ch{row["chapter"]}-{width}-{item["id"]}.png'))
  await summary.click();assert not await d.evaluate('(e)=>e.open')
  tested.append(item['id'])
 # 保留元件的基本操作：第一個可見重置按鈕及首個range，檢查頁面執行不出錯。
 button=page.locator('button:visible').filter(has_text='重置').first
 if await button.count():await button.click()
 slider=page.locator('input[type=range]:visible').first
 if await slider.count():
  await slider.evaluate('(e)=>{e.value=e.max;e.dispatchEvent(new Event("input",{bubbles:true}));e.value=e.min;e.dispatchEvent(new Event("input",{bubbles:true}));}')
 assert not errors,(row['chapter'],width,errors)
 canvases=await page.locator('.chart-wrap.ready').count()
 svgs=await page.locator('svg').count()
 await page.close()
 return {'chapter':row['chapter'],'width':width,'changed_details_tested':tested,'collapse_and_expand':'PASS','MathJax':'PASS','page_overflow':'PASS','visible_control_smoke':'PASS','ready_charts':canvases,'svg_count':svgs,'page_errors':errors}
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True)
  sem=asyncio.Semaphore(3)
  async def guarded(row,width):
   async with sem:return await inspect(browser,row,width)
  results=await asyncio.gather(*(guarded(row,width) for row in ROWS for width in [1440,390]))
  await browser.close()
 (OUT/'browser-report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
 for row in results:print(row['chapter'],row['width'],'PASS',len(row['changed_details_tested']),'details; charts',row['ready_charts'],'SVG',row['svg_count'])
asyncio.run(main())
