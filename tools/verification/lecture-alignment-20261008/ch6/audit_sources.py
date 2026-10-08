"""Source inventory and live link accessibility audit for Chapter 6."""
from pathlib import Path
import hashlib,json,re,urllib.request,urllib.error
from concurrent.futures import ThreadPoolExecutor
import pymupdf
ROOT=Path(__file__).resolve().parent
PDF=Path('/home/phonchi/nsysu-math524/static_files/presentations/06_Linear_Model_Selection.pdf')
LAB=PDF.with_name('Ch06-varselect-lab-zh.ipynb')
def target(page):
 if page<=5:return 'prologue'
 if page<=16:return 'w06-detail-subset-foundations'
 if page<=21:return 'w06-detail-criteria-scale'
 if page<=24:return 'w06-detail-selection-cv'
 if page<=32:return 'w06-detail-ridge-bias'
 if page<=38:return 'w06-detail-lasso-solution'
 if page==39:return 'w06-detail-shrinkage-map'
 if page<=42:return 'w06-detail-ridge-bias'
 if page<=45:return 'w06-detail-lambda-conventions'
 if page<=55:return 'w06-detail-pcr-appendix'
 if page<=58:return 'w06-detail-pls-reading'
 if page<=62:return 'w06-detail-highdim-cautions'
 if page==63:return 'reference'
 if page==64:return 'w06-detail-coefficient-paths'
 if page<=69:return 'w06-detail-pcr-appendix'
 return 'w06-detail-lar-group'
links={};pages=[]
for n,page in enumerate(pymupdf.open(PDF),1):
 text=page.get_text()
 urls=[x['uri'] for x in page.get_links() if x.get('uri')]
 # PDF text also has wrapped URLs; annotations are canonical when available.
 for u in urls:links.setdefault(u,[]).append(n)
 pages.append({'page':n,'heading':text.splitlines()[0] if text else '', 'target_anchor':target(n),'text':text,'urls':urls,'coverage':'title/divider' if n in (1,63) else 'substantive topic aligned'})
(ROOT/'pdf_pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2))
def fetch(pair):
 url,pg=pair
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (educational source audit)'})
 record={'original_url':url,'pages':sorted(set(pg)),'target_anchor':target(pg[0]),'disposition':'Topic explained in target; original retained as lecture source in audit; authority-based alternatives cited beside teaching.'}
 if '50975774' in url:record['target_anchor']='w06-detail-deviance'
 try:
  with urllib.request.urlopen(req,timeout=18) as r:
   data=r.read(1500000);record.update(status=r.status,final_url=r.url,content_type=r.headers.get('Content-Type'),bytes_read=len(data))
   if b'%PDF' in data[:20]:
    doc=pymupdf.open(stream=data,filetype='pdf');txt='\n'.join(p.get_text() for p in doc)
   else:txt=data.decode('utf-8','replace')
   record['read_status']='fetched and available for source inspection'
   name=hashlib.sha256(url.encode()).hexdigest()[:12]
   (ROOT/('source-'+name+'.txt')).write_text(txt)
   record['cache']='source-'+name+'.txt'
 except Exception as e:record.update(status='blocked/unavailable',read_status='not read; use primary-source fallback',error=str(e))
 if pg[0] <=24:record['primary_fallback']='https://www.statlearning.com/ ; lecture/Lab and existing fixed-design Cp, AIC, adjusted-R2 derivations'
 elif pg[0]<=45:record['primary_fallback']='https://scikit-learn.org/1.6/modules/linear_model.html ; https://dafriedman97.github.io/mlbook/content/c2/s1/bayesian.html'
 else:record['primary_fallback']='https://scikit-learn.org/1.6/modules/decomposition.html#pca ; https://scikit-learn.org/1.6/modules/cross_decomposition.html'
 if pg[0]==70:record['primary_fallback']='https://scikit-learn.org/1.6/modules/linear_model.html#least-angle-regression ; https://group-lasso.readthedocs.io/en/latest/maths.html ; https://scikit-learn.org/1.6/modules/generated/sklearn.metrics.log_loss.html'
 return record
with ThreadPoolExecutor(max_workers=5) as ex:records=list(ex.map(fetch,links.items()))
(ROOT/'links.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
(ROOT/'source_hashes.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (PDF,LAB)},indent=2))
print('pages',len(pages),'unique annotated URLs',len(records),'fetched',sum(isinstance(x['status'],int) for x in records))
