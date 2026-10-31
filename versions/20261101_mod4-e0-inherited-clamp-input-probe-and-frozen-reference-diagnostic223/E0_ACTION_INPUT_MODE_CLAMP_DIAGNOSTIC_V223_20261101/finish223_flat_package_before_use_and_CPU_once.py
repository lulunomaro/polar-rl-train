"""Before-use flat-package import correction and bounded synthetic source tests."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,time
N=Path(__file__).resolve().parent;S=N/'source';R=N/'reports';D=N/'drafts_before_use_flat_import';D.mkdir(exist_ok=False)
def put(p,v):
 with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False)
changed=[]
for name,old,new in [('target223_single_N1_parent_UNUSED.py',"sys.path.insert(0,str(N/'source'))","sys.path.insert(0,str(N))"),('evaluate223_input_mode_clamp_UNUSED_once.py',"sys.path.insert(0,str(Path(__file__).resolve().parent/'source'))","sys.path.insert(0,str(Path(__file__).resolve().parent))")]:
 p=S/name;raw=p.read_bytes();(D/name).write_bytes(raw);text=raw.decode('utf8');assert old in text;text=text.replace(old,new,1);ast.parse(text);p.write_text(text,encoding='utf8');changed.append(dict(path=name,original_SHA=hashlib.sha256(raw).hexdigest(),corrected_SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
p=S/'contract223.py';p.write_text(p.read_text('utf8').replace(" assert t['eval_yaw_range']==[0.,0.]and t['current_authority_binding']['kind']=='FRESH_CNONE'", " assert t['eval_yaw_range']==[0.,0.]and t['current_authority_binding']['kind']=='FRESH_CNONE'\n assert t['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'and t['target_host']=='72'\n assert t['model_path']=='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_JUMP32066_GROUND10_THREE_HOUR_20261031v210/e0_72/production/model_final_complete.pt'"),encoding='utf8')
task=json.loads((S/'TASK223.json').read_bytes());task['worker_SHA']=hashlib.sha256((S/'evaluate223_input_mode_clamp_UNUSED_once.py').read_bytes()).hexdigest();(S/'TASK223.json').write_text(json.dumps(task,indent=2),encoding='utf8')
caller=N/'run_ROOT223_input_mode_action_flow_once.py';raw=caller.read_bytes();(D/caller.name).write_bytes(raw)
text=raw.decode('utf8').replace('current219 authority/readcounts.','fresh CNone, fixedSI35/mode action-flow/readcounts.').replace('source_asset_POSTCOPY_passes=1','source_package_POSTCOPY_passes=1,asset_copies=0')
needle="task=read(S/'TASK223.json');pack=read(S/'PACKAGE223_SOURCE_AND_TASK.json')"
assert needle in text
text=text.replace(needle,needle+"\n q=read(T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/reports/ROOT210_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')\n assert q['passed']and q['roles']['e0_72']['SHA']==task['model_SHA']and q['roles']['e0_72']['save_at_or_after_requested_deadline']\n assert read(T/'W35_SOLO_INSTALL_FIRST_AND_CLOSED_READERS_SOURCE_V219_20261101/reports/ROOT219V3_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')['owner_closed']['canonical_None']")
ast.parse(text);caller.write_text(text,encoding='utf8')
put(R/'ROOT223_FLAT_PACKAGE_IMPORT_BEFORE_USE_REPAIR.json',dict(epoch=time.time(),source_before_use_only=True,changes=changed,original_drafts_retained=str(D),no_network_model_or_SDK_executed=True,original220_unreachable_post_App_marker_false_retained=True))
put(R/'ROOT223_LOCAL_CPU_PURPOSE_ONCE_CONSUMED.json',dict(epoch=time.time(),synthetic_only=True,models_raw_NPZ_SDK_GPU_remote_calls=0))
sys.path.insert(0,str(S));import torch
assert not torch.cuda.is_initialized()
rng=torch.random.get_rng_state().clone()
from input_counterfactual223 import diagnose
from contract223 import validate_task
assert validate_task(task)
rejected=0
for key,value in [('kind','old220'),('controls_max',1000),('GPU_UUID','unknown'),('num_envs',20000),('model_iteration',32066),('current_authority_binding',{'kind':'EXACT_ORIGINAL219_OWNER_GO'}),('training_reward_changed',True),('model_byte_reads',2)]:
 x=copy.deepcopy(task);x[key]=value
 try:validate_task(x)
 except(AssertionError,KeyError):rejected+=1
 else:raise AssertionError('Accepted bad task '+key)
with torch.random.fork_rng(devices=[]):
 actor=torch.nn.Sequential(torch.nn.Linear(35,6,bias=False))
 with torch.no_grad():
  actor[0].weight.zero_();actor[0].weight[0,22]=2.;actor[0].weight[0,28]=3.;actor[0].weight[0,29]=5.
 x=torch.zeros(2,35);x[:,22]=1.;x[:,29]=1.;original=x.clone();out=diagnose(actor,x,gradient=True)
 assert out['actual_mean'][0][0]==7. and out['counterfactual_mode0_mean'][0][0]==5. and out['counterfactual_mode1_mean'][0][0]==7. and out['counterfactual_previous_action_zero_mean'][0][0]==5.
 assert torch.equal(x,original)and out['first_state_d_left_crank_mean_d_fixedSI35'][0][22]==2.
 try:diagnose(actor,torch.full((1,35),float('nan')))
 except ValueError:pass
 else:raise AssertionError('Nonfinite observation accepted')
assert torch.equal(rng,torch.random.get_rng_state())and not torch.cuda.is_initialized()
for p in [*S.glob('*.py'),caller]:ast.parse(p.read_text('utf8'))
parent=(S/'target223_single_N1_parent_UNUSED.py').read_text('utf8');assert "read(out/'APP223_CLOSED.json')"not in parent and 'APP223_CLOSE_REQUESTED.json'in parent and 'ENV223_CLOSE_RETURNED.json'in parent
put(R/'ROOT223_LOCAL_SOURCE_COUNTERFACTUAL_TASK_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,groups=3,task_rejections=rejected,synthetic_rows=2,exact_counterfactual_and_gradient=True,input_immutable=True,global_RNG_unchanged=True,CUDA_initialized=False,model_raw_NPZ_SDK_GPU_remote_calls=0))
manifest=dict(epoch=time.time(),purpose=task['kind'],files=[dict(relative=p.name,bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(S.iterdir())if p.is_file()and p.name!='PACKAGE223_SOURCE_AND_TASK.json'])
(S/'PACKAGE223_SOURCE_AND_TASK.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
rows=[dict(path=str(p.relative_to(N)),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(N.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
put(N/'INDEX223_FROZEN.json',dict(epoch=time.time(),status='FROZEN_SOURCE_CPU_NOT_ACTUAL',files=rows,CPU_groups=3,CPU_rejections=rejected,necessary_new32control_purpose=True,original220_221_consumed_never_reexecuted=True))
print(json.dumps(dict(passed=True,groups=3,rejections=rejected,index_files=len(rows),no_actual_model_or_SDK_read=True)))
