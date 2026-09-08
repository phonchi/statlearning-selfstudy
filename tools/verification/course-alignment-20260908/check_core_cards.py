"""Verify every code line and saved output against cited current notebook cells."""
import importlib,sys,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'enrich'))
import lib
orig=lib.card
records=[]
def capture(label,code,output=None,src=None,**kwargs):
 records.append((label,code,output,src))
 return orig(label,code,output,src,**kwargs)
lib.card=capture
for ch,name in [(2,'statlearn'),(3,'regression'),(4,'classification'),(5,'resampling')]:
 records.clear();importlib.import_module('enrich_'+name)
 for label,code,out,src in records:
  cells=[int(v) for v in re.findall(r'\d+',src.split('儲存格')[-1])]
  codes=[];outputs=[]
  for c in cells:
   try:codes.append(lib.lab_code(ch,c))
   except SystemExit:pass
   try:outputs.append(lib.lab_output(ch,c))
   except SystemExit:pass
  # Exact ordered complete-cell chunks, skipping additional context-only references.
  rem=code.strip()
  for c in codes:
   if rem.startswith(c.strip()):rem=rem[len(c.strip()):].strip()
  codeok=not rem
  outok=out is None or out.strip() in [v.strip() for v in outputs]
  print(ch,label,'cells',cells,'CODE',codeok,'OUTPUT',outok, 'UNMATCHED '+repr(rem[:150]) if not codeok else '')
