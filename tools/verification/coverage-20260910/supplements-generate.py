"""Regenerate owned pages; preserve existing DL frames, never rerun a lab."""
from pathlib import Path
import subprocess,sys,re,runpy
ROOT=Path(__file__).resolve().parents[3]
FILES=['s1_probability','s2_conditional','s3_distributions','s4_inference','s5_bayesian','s6_regression','p1_python_basics','p2_flow_functions','p3_numpy','p4_pandas','p5_visualization','p6_modeling_api']
for name in FILES:
 r=subprocess.run([sys.executable,'-B',str(ROOT/'tools/enrich'/('enrich_'+name+'.py'))],cwd=ROOT)
 if r.returncode: raise SystemExit(r.returncode)
# Read the exact pre-existing baked data before importing any generating code.
html=(ROOT/'deep_learning.html').read_text()
frames=re.findall(r'^const FRAMES_w11\w+ = .*?;\s*$',html,re.M)
assert frames,'Missing existing DL frames; do not trigger expensive regeneration.'
d=runpy.run_path(str(ROOT/'tools/enrich/enrich_deeplearning.py'),run_name='supplements_content')
d['apply']('deep_learning',d['BODIES'],d['PAGEJS'],'\n'.join(frames))
