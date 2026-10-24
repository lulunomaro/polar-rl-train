from pathlib import Path
import hashlib,json,sys,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import hashlib,json,time
root=Path('/home/egde/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab')
paths=[root/'envs/mdp/actions/joint_actions.py',root/'managers/action_manager.py',root/'assets/articulation/articulation_data.py']
out=[]
for p in paths:
 raw=p.read_bytes();out.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8')))
print(json.dumps(dict(epoch=time.time(),sources=out,source_text_only=True,no_import_PhysX_GPU_model_or_budget_write=True)))
'''
try:
 put('SDK_ACTION_SOURCE_READ_STARTED_ACTUAL.json',dict(epoch=time.time(),user_request='继续看回放修复上台阶',purpose='Verify delayed joint action raw/scale/offset and authored position limit APIs for reward-only airborne infeasible-target penalty',no_training_launch_or_new_skill_threshold=True))
 c=d.t.connect()
 try:out=d.code(c,d.t.PY,CODE,{},timeout=45)
 finally:c.close()
 put('ACTUAL_INSTALLED_JOINT_ACTION_AND_LIMIT_SDK_SOURCE_ACTUAL.json',out)
 print(json.dumps(dict(passed=True,sources=[{k:r[k] for k in ('path','bytes','SHA')} for r in out['sources']])))
except BaseException:
 put('SDK_ACTION_SOURCE_READ_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise

