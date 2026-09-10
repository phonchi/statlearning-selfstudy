"""Record source provenance, page text coverage and PDF links without changing sources."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,re,sys
import pymupdf as fitz

ROOT=Path('/home/phonchi/statlearning-selfstudy')
COURSE=Path('/home/phonchi/nsysu-math524/static_files/presentations')
OUT=ROOT/'tools/verification/coverage-20260910'
sys.path.insert(0,str(ROOT/'tools'))
from pages import PAGES

def main():
    files=list(dict.fromkeys([p.deck for p in PAGES if p.deck]+['01-06_Recap.pdf']))
    sources=[]
    sparse=[]
    for name in files:
        path=COURSE/name
        doc=fitz.open(path)
        rows=[]
        for idx,page in enumerate(doc):
            text=page.get_text()
            annotations=[l['uri'] for l in page.get_links() if l.get('uri')]
            visible=re.findall(r'https?://[^\s<>]+',text)
            links=list(dict.fromkeys(annotations+visible))
            rows.append({'page':idx+1,'text_characters':len(text.strip()),
                         'title':next(iter(text.strip().splitlines()),''),
                         'links':links,'text_sha256':hashlib.sha256(text.encode()).hexdigest(),
                         'image_objects':len(page.get_images()),
                         'review':'assigned_chapter_review'})
            if len(text.strip())<120 and (page.get_images() or page.get_drawings()):
                sparse.append((name,idx+1))
        sources.append({'file':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'pages':len(doc),'page_inventory':rows})
    (OUT/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
    assignments={}
    for p in PAGES:
        team='ch1-6' if p.islp in range(1,7) and p.group=='core' else 'ch7-8-12' if p.islp in [7,8,12] and p.group=='core' else 'svm' if p.islp==9 else 'supplements'
        assignments[p.stem]={'team':team,'lecture':p.deck or None,'source_mode':p.grounding_mode}
    (OUT/'page-assignments.json').write_text(json.dumps(assignments,ensure_ascii=False,indent=2)+'\n')
    (OUT/'image-pages.json').write_text(json.dumps(sparse,ensure_ascii=False,indent=2)+'\n')
    print(f'Indexed {len(sources)} PDFs, {sum(s["pages"] for s in sources)} pages, {len(assignments)} site pages; {len(sparse)} low-text illustrated pages need visual review.')

if __name__=='__main__': main()
