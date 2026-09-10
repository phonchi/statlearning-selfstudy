from pathlib import Path
import re,sys
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root/'tools/enrich'))
import enrich_svm as m
old=(root/'support_vector_machines.html').read_text()
js=re.search(r'<!-- PAGEJS:BEGIN -->\s*<script>(.*?)</script>\s*<!-- PAGEJS:END -->',old,re.S).group(1)
frames=js[:js.index('/* ===== support_vector_machines')].strip()
m.apply('support_vector_machines',m.BODIES,m.PAGEJS,frames)
print('Preserved existing FRAMES; no course Lab or baked model rerun.')
