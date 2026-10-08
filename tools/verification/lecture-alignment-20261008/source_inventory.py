from pathlib import Path
import json,hashlib,subprocess,re
import pymupdf
course=Path('/home/phonchi/nsysu-math524/static_files/presentations');root=Path('/home/phonchi/statlearning-selfstudy');out=root/'tools/verification/lecture-alignment-20261008';(out/'inputs').mkdir(parents=True,exist_ok=True)
items=[(5,'05_Resampling_Methods.pdf','Ch05-resample-lab-zh.ipynb','resampling_methods'),(6,'06_Linear_Model_Selection.pdf','Ch06-varselect-lab-zh.ipynb','model_selection'),(7,'07_Moving_Beyond_Linearity.pdf','Ch07-nonlin-lab-zh.ipynb','beyond_linearity'),(8,'08_Tree-Based_Methods.pdf','Ch08-baggboost-lab-zh.ipynb','tree_based_methods'),(9,'09_Support_Vector_Machines.pdf','Ch09-svm-lab-zh.ipynb','support_vector_machines'),(12,'12_Unsupervised_learning.pdf','Ch12-unsup-lab-zh.ipynb','unsupervised_learning')]
manifest_path=out/'source_manifest.json'
previous=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
baseline_head=previous.get('baseline_head') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
# 歷史驗收只能使用同一批來源，不能把後來的PDF／Lab冒充原始輸入。
for item in previous.get('chapters',[]):
    for name,expected in item['source_sha256'].items():
        actual=hashlib.sha256((course/name).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit('Historical source mismatch: '+name)
manifest={'baseline_head':baseline_head,'chapters':[]}
for ch,pdf,lab,stem in items:
 doc=pymupdf.open(course/pdf);pages=[]
 for i,p in enumerate(doc):
  text=p.get_text();urls=sorted({l['uri'] for l in p.get_links() if l.get('uri')})
  pages.append({'page':i+1,'text':text,'annotated_urls':urls})
 (out/'inputs'/f'lecture_ch{ch}.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2))
 baseline=subprocess.check_output(['git','show',baseline_head+':'+stem+'.html'],cwd=root)
 (out/'inputs'/f'{stem}.baseline.html').write_bytes(baseline)
 nb=json.loads((course/lab).read_text())
 hashes={n:hashlib.sha256((course/n).read_bytes()).hexdigest() for n in [pdf,lab]}
 manifest['chapters'].append({'chapter':ch,'pdf':pdf,'pdf_pages':len(doc),'lab':lab,'lab_cells':len(nb['cells']),'source_sha256':hashes,'html':stem+'.html','baseline_sha256':hashlib.sha256(baseline).hexdigest(),'pdf_scope_start':22 if ch==5 else 1})
(out/'source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Snapshots and source hashes saved for all six chapters')
