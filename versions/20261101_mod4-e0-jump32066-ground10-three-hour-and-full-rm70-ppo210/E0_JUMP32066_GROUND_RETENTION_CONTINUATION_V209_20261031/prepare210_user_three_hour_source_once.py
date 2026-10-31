"""Human changed209 before GO to one uninterrupted three-hour window.
New namespace; retain the unused one-hour source and actual2090PT evidence.
"""
from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
S=Path(__file__).resolve().parent;T=S.parent
N=T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031';P=N/'package';C=N/'control';R=N/'reports'

def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
def read(p):return json.loads(p.read_bytes())
def put(n,v):write(R/n,json.dumps(v,indent=2,allow_nan=False,ensure_ascii=False))

def main():
 assert not (S/'reports/ROOT209_START_ONCE_CONSUMED_BEFORE_NETWORK.json').exists(),'209 already launched, no authority to pretend pre-GO change'
 assert not N.exists();N.mkdir();R.mkdir();C.mkdir();shutil.copytree(S/'package',P)
 put('ROOT210_THREE_HOUR_SOURCE_ONCE_CONSUMED.json',dict(epoch=time.time(),user_exact='要训一口气训3个小时',old209_GO_and_training=0,new_learning_seconds=10800,new_max_parent_seconds=11100,extra_exit_seconds=300,model_GPU_remote_reads=0))
 task=read(P/'TASK209.json');task['kind']='E0_JUMP32066_ORIGINAL_E0_GROUND10_LITERAL_JUMP90_400N50_THREE_HOUR_V210'
 task.pop('one_hour_learning_seconds');task['learning_seconds']=10800;task['max_parent_seconds']=11100
 task['user_three_hour_request']=True
 write(P/'TASK210.json',json.dumps(task,indent=2))
 protocol=(P/'mixed209_task_protocol.py').read_text('utf8').replace('E0_JUMP32066_ORIGINAL_E0_GROUND10_LITERAL_JUMP90_400N50_V209',task['kind'])
 protocol=protocol.replace("go['max_parent_seconds']==3900","go['max_parent_seconds']==11100")
 protocol=protocol.replace("go['learning_started_epoch']+3600","go['learning_started_epoch']+10800").replace("go['learning_started_epoch']+3900","go['learning_started_epoch']+11100")
 write(P/'mixed210_task_protocol.py',protocol)
 worker=(P/'run209_mixed_E0_JUMP_worker.py').read_text('utf8')
 for a,b in [('TASK209.json','TASK210.json'),('mixed209_task_protocol','mixed210_task_protocol'),('source209_config_only_no_old_main','source210_config_only_no_old_main'),('typed_MIX209_task','typed_MIX210_task'),('ACTUAL209','ACTUAL210'),('ACTUAL_SOURCE209','ACTUAL_SOURCE210')]:worker=worker.replace(a,b)
 write(P/'run210_mixed_E0_JUMP_worker.py',worker)
 assert H(P/'mixed209_sdk.py')==H(S/'package/mixed209_sdk.py')
 for name in ('literal_original_methods.py','literal_original_config.py','jump194_sdk.py','jump194_boundary.py'):
  assert H(P/name)==H(S/'package'/name)
 schedule=read(S/'SCHEDULE_PUBLIC.json');spec=schedule['experts']['e0_72']
 spec.update(max_parent_seconds=11100,worker_script='run210_mixed_E0_JUMP_worker.py',manifest_file='PACKAGE210_MANIFEST.json',
  job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_JUMP32066_GROUND10_THREE_HOUR_20261031v210/e0_72')
 schedule['kind']='ONE210_STATIC_GENUINE_MIXED_PPO_THREE_HOUR'
 schedule['owner_root']='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_ONE210_E0_GROUND10_JUMP90_THREE_HOUR_2610v210/owner'
 for name in ('forwarded_original_owner_control_v1.py','single_writer72_authority_V85M_source.py'):shutil.copyfile(S/'control'/name,C/name)
 common=(S/'control/three_slot_common_v1.py').read_text('utf8').replace('owner209_protocol','owner210_protocol')
 write(C/'three_slot_common_v1.py',common)
 owner=(S/'control/mixed209_finite_owner_authority72.py').read_text('utf8').replace('owner209_protocol','owner210_protocol')
 owner=owner.replace('human_requested_E0_latest_branch_mixed_one_hour','human_requested_E0_latest_branch_mixed_three_hour')
 owner=owner.replace('Linux_MIX209_E0_GROUND10_JUMP90_','Linux_MIX210_E0_GROUND10_JUMP90_THREE_HOUR_')
 owner=owner.replace('time.time()-started>10800','time.time()-started>max(s[\'max_parent_seconds\'] for s in specs.values())+120')
 write(C/'mixed210_finite_owner_authority72.py',owner)
 node=(S/'control/mixed209_fullstate_slot_node.py').read_text('utf8').replace('ADMISSION209_READY.json','ADMISSION210_READY.json')
 node=node.replace('time.time()-begin>10800','time.time()-begin>spec["max_parent_seconds"]+120')
 write(C/'mixed210_fullstate_slot_node.py',node)
 ownerproto=(S/'owner209_protocol.py').read_text('utf8').replace("e['max_parent_seconds']==3900","e['max_parent_seconds']==11100").replace("v.get('kind')=='MIX209_READY'","v.get('kind')=='MIX210_READY'")
 write(C/'owner210_protocol.py',ownerproto)
 old={r['relative']:r for r in read(S/'PACKAGE209_MANIFEST.json')['files']};rows=[]
 for p in sorted(P.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(P).as_posix()
  if p.suffix.lower() in ('.usd','.usda','.usdc','.npz','.npy','.stl','.pt'):
   assert rel in old and p.stat().st_size==old[rel]['bytes'];sha=old[rel]['SHA'];kind='existing_producer_no_binary_rehash'
  else:sha=H(p);kind='source_or_small_metadata'
  rows.append(dict(relative=rel,local_relative='package/'+rel,bytes=p.stat().st_size,SHA=sha,index_kind=kind))
 write(N/'PACKAGE210_MANIFEST.json',json.dumps(dict(kind='FROZEN_MIX210_COMPLETE_PACKAGE_THREE_HOUR',files=rows),indent=2))
 spec['manifest_SHA']=H(N/'PACKAGE210_MANIFEST.json')
 write(N/'SCHEDULE_PUBLIC.json',json.dumps(schedule,indent=2))
 ready=read(S/'ADMISSION209_READY.json');ready.update(kind='MIX210_READY',manifest_SHA=spec['manifest_SHA'],
  actual0PT_scope='Reused actual20980env8control result: byte-identical robot/SDK/commands/reward/guards; only TaskGO/window/namespace changed',
  actual0PT_selected_SDK_SHA=H(P/'mixed209_sdk.py'),actual0PT_replayed=False,user_authorized_learning_seconds=10800)
 write(N/'ADMISSION210_READY.json',json.dumps(ready,indent=2))
 write(N/'CONTROL210_MANIFEST.json',json.dumps(dict(files=[dict(relative=p.name,local_path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(C.glob('*.py'))]),indent=2))
 for p in list(P.rglob('*.py'))+list(C.glob('*.py')):ast.parse(p.read_bytes(),filename=str(p))
 # Raw charge, request HMAC, and authority modules remain unchanged. Only the
 # human-authorized temporal guard extends from one to three hours.
 def fn(p,name):return ast.dump(next(n for n in ast.parse(p.read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name==name))
 for name in ('charge_values','authenticated_row','terminal'):assert fn(C/'three_slot_common_v1.py',name)==fn(S/'control/three_slot_common_v1.py',name)
 assert H(C/'forwarded_original_owner_control_v1.py')==H(S/'control/forwarded_original_owner_control_v1.py')
 put('FROZEN210_THREE_HOUR_SCOPE_AND209_ACTUAL_0PT_REUSE.json',dict(epoch=time.time(),passed_source_only=True,user_requested_seconds=10800,max_parent_seconds=11100,
  adapter_rewards_commands_robot_DR_physics_identical=True,actual2090PT_reused_not_rerun=True,source_model_reads=0,new_GPU_remote=0,
  no_new_grant_or_charge_function_change=True,old209_one_hour_launch_UNUSED_superseded=True,
  package_manifest_SHA=H(N/'PACKAGE210_MANIFEST.json'),control_manifest_SHA=H(N/'CONTROL210_MANIFEST.json'),
  target_postcopy_AND_new_actual_fullstate_CUDA_restore_and_FIRST_still_required=True))
 print(json.dumps(dict(passed=True,new_root=str(N),learning_seconds=10800,max_parent=11100)))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(parents=True,exist_ok=True);put('ROOT210_SOURCE_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
