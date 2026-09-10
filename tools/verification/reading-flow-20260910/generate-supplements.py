"""Generate owned reading-flow pages without running labs or frame generators."""
from pathlib import Path
import re,runpy,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/enrich'))
import lib
original_apply=lib.apply
lib.apply=lambda *args,**kwargs:None
names=['deeplearning','00a_why_code','00b_setup','00c_ai_assisted','s1_probability','s2_conditional','s3_distributions','s4_inference','s5_bayesian','s6_regression','p1_python_basics','p2_flow_functions','p3_numpy','p4_pandas','p5_visualization','p6_modeling_api']
for name in names:
 stem='deep_learning' if name=='deeplearning' else name
 old=(ROOT/(stem+'.html')).read_text()
 frame_lines=re.findall(r'^const FRAMES_\w+ = .*?;\s*$',old,re.M)
 d=runpy.run_path(str(ROOT/'tools/enrich'/('enrich_'+name+'.py')),run_name='reading_owned_content')
 original_apply(stem,d['BODIES'],d['PAGEJS'],'\n'.join(frame_lines))
