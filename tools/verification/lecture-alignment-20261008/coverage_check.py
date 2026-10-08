from pathlib import Path
import json,collections
from bs4 import BeautifulSoup
root=Path('/home/phonchi/statlearning-selfstudy');base=root/'tools/verification/lecture-alignment-20261008';manifest=json.loads((base/'source_manifest.json').read_text());result=[];overall=set()
for item in manifest['chapters']:
 ch=item['chapter'];pages=json.loads((base/'inputs'/f'lecture_ch{ch}.json').read_text())[item['pdf_scope_start']-1:]
 actual_urls={u for p in pages for u in p['annotated_urls']};overall|=actual_urls
 if ch==5:
  rows=json.loads((base/'ch5/coverage.json').read_text())['links'];mapped={r['url']:[r['target_anchor']] for r in rows}
 elif ch==6:
  rows=json.loads((base/'ch6/links.json').read_text());mapped={r['original_url']:[r['target_anchor']] for r in rows}
 elif ch in [7,8]:
  rows=json.loads((base/f'ch{ch}'/'links.json').read_text());mapped={u:[r['anchor']] for u,r in rows.items()}
 else:
  rows=json.loads((base/f'ch{ch}'/'link-disposition.json').read_text());mapped={r['url']:r['targets'] for r in rows}
 assert actual_urls<=set(mapped),(ch,'unmapped original URLs',actual_urls-set(mapped))
 soup=BeautifulSoup((root/item['html']).read_text(),'html.parser')
 for u in actual_urls:
  assert mapped[u],(ch,u,'no target')
  assert all(soup.find(id=a) for a in mapped[u]),(ch,u,mapped[u])
 result.append({'chapter':ch,'scope_page_count':len(pages),'original_annotation_unique_urls':len(actual_urls),'every_original_url_mapped':True,'all_target_anchors_exist':True,'additional_text_url_entries':len(mapped)-len(actual_urls)})
 print(ch,len(pages),'pages;',len(actual_urls),'original URLs covered')
(base/'coverage-final.json').write_text(json.dumps({'chapters':result,'unique_original_annotation_urls_in_scope':len(overall),'scope_page_count':sum(r['scope_page_count'] for r in result)},ensure_ascii=False,indent=2))
print('All',sum(r['scope_page_count'] for r in result),'scoped PDF pages and',len(overall),'global unique annotated URLs mapped')
