"""New display-reader candidate: preserve original [age] tensor serialization.

V1 failed its scalar-age assumption after one controls read, before any model.
No old once is rerun; this exact single-line reader correction is separately recorded.
"""
from pathlib import Path
import hashlib,json,time,traceback
HERE=Path(__file__).resolve().parent
old=(HERE/'prepare_user_visualization.py').read_bytes()
a="require([r['age_for_action'] for r in records]==list(range(2000)),'unaltered original action clock')"
b="require([r['age_for_action'] for r in records]==[[i] for i in range(2000)],'unaltered original one-element tensor action clock')"
s=old.decode('utf8');assert s.count(a)==1;s=s.replace(a,b)
ns=dict(__name__='new_visualization_v2_reader',__file__=str(HERE/'prepare_user_visualization.py'))
exec(compile(s,str(HERE/'prepare_user_visualization_v2.py'),'exec'),ns)
ns['R']=HERE/'reports/preparation_v2';ns['R'].mkdir(exist_ok=True)
ns['put']('V2_EXACT_READER_CORRECTION_BEFORE_READ.json',dict(original_source_SHA=hashlib.sha256(old).hexdigest(),candidate_source_SHA=hashlib.sha256(s.encode()).hexdigest(),old=a,new=b,prior_visualization_attempt_controls_reads=1,prior_visualization_checkpoint_decodes=0,original_recorded_age_is_one_element_tensor=True))
try:
    ns['main']()
    p=ns['R']/'USER_DISPLAY_DATA_COMPLETE.json';v=json.loads(p.read_bytes())
    assert v['passed'] and v['read_counts']['checkpoint_decodes']==1
    out=HERE/'reports/USER_DISPLAY_DATA_COMPLETE.json';assert not out.exists();out.write_bytes(p.read_bytes())
except BaseException:
    ns['put']('V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),counts=ns['COUNTS']));raise
