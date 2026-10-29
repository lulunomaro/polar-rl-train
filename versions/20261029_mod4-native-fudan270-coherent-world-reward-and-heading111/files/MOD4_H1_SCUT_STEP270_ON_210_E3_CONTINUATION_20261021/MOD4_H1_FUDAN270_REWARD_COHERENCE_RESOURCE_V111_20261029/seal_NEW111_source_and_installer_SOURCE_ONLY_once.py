from pathlib import Path
import ast,copy,hashlib,json,runpy,sys,time
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
prep=read(R/'TWO111_SOURCE_PAYLOADS_PREPARED_NO_GO_ACTUAL.json');assert prep['passed'];checks={}
for mode,spec in prep['payloads'].items():
 B=Path(spec['payload']);sys.path[:0]=[str(B),str(B/'source')]
 for name in ('native_flat90_source_guard_v1','native88C_to_flat_migration_v1','native111_coherent_reward_pins_v1'):sys.modules.pop(name,None)
 from native_flat90_source_guard_v1 import validate_task_go
 from native111_coherent_reward_pins_v1 import FLAT_OBJECTIVE_CONTRACT,NATIVE_CONTRACT
 task=spec['task'];go=copy.deepcopy(task);go.update(payload_manifest_SHA=spec['manifest_SHA'],num_envs=4096,max_parent_seconds=3900,exit_headroom_seconds=300)
 validate_task_go(task,go,spec['manifest_SHA'])
 negatives=[]
 for kind in ('source_SHA','source_progress','native_seed','native_learning_seed','reference','reward_SHA','heading','platform'):
  bad=copy.deepcopy(go)
  if kind=='source_SHA':bad['source_SHA']='0'*64
  elif kind=='source_progress':bad['source_progress']['world_updates']+=1
  elif kind=='native_seed':bad['native_seed']=99
  elif kind=='native_learning_seed':bad['native_learning_seed']=28
  elif kind=='reference':bad['native_reference_SHA']='0'*64
  else:
   key={'reward_SHA':'reward_SHA','heading':'heading_slot','platform':'platform_XY'}[kind]
   bad['fudan_step_task']['reward_coherence'][key]='WRONG'
  try:validate_task_go(task,bad,spec['manifest_SHA'])
  except (ValueError,AssertionError):negatives.append(kind)
  else:raise AssertionError('Typed source negative admitted '+kind)
 values={x.arg:x.value.value for x in ast.walk(ast.parse((B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py').read_bytes())) if isinstance(x,ast.keyword) and x.arg in ('private_phase_frame_source_SHA','real_callback_counter_source_SHA','source_reference_artifact_SHA') and isinstance(x.value,ast.Constant)}
 assert values['private_phase_frame_source_SHA']==FLAT_OBJECTIVE_CONTRACT['private_phase_frame_source_SHA']==H(B/'source/private_phase_frame_v1.py')
 assert values['real_callback_counter_source_SHA']==FLAT_OBJECTIVE_CONTRACT['real_callback_counter_source_SHA']==H(B/'h1_step270_sdk_runtime_candidate.py')
 assert values['source_reference_artifact_SHA']=='1a03883127eae81ef815fbb6f7450bdee68f489561cd16a9d4b193a48243153e'
 assert NATIVE_CONTRACT['fudan_step_task']==task['fudan_step_task']
 checks[mode]=dict(positive=True,negative_fields_rejected=negatives,actual_producer_three_source_literals=values,no_model_read=True,no_actual_signed_GO=True)
put('SOURCE111_PREINSTALL_TASK_GO_SOURCE_BINDING_CPU_ACTUAL.json',dict(passed=True,epoch=time.time(),roles=checks,kind='PURE_METADATA_NO_GO_MODEL_OR_GPU'))
PRE=r'''
from pathlib import Path,PurePosixPath
import fcntl,hashlib,json,psutil,shutil,subprocess,time
owned=Path('/home/lc01/Zonglin Li/zonglin2/tasks');B=Path(v['root']);old=owned/'MOD4_H1_FUDAN270_EPISODE20_2610v107CPUv2/seed27';stage=owned/'MOD4_TWO107_FUDAN270_EPISODE20_2610v106'
assert B.resolve().is_relative_to(owned.resolve()) and not B.exists()
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
assert c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[] and c['remaining_training_seconds']>86412.86069250107
cohort=json.loads((stage/'owner/COHORT_FINAL.json').read_bytes());ending=json.loads((stage/'owner/OWNER_EXIT_ACTUAL.json').read_bytes());assert cohort['original_cost_settled'] and ending['original_cost_settled'] and set(cohort['go'])=={'h1','h1_seed28'}
assert all(g['original_owner_pid']==630841 and g['original_owner_creation']==1793213510.36 for g in cohort['go'].values())
segments=[x for x in c['completed_segments'] if x['owner_parent_pid']==630841 and set(x['experts'])=={'h1','h1_seed28'} and all(x['experts'][k]['started_epoch']==cohort['go'][k]['learning_started_epoch'] for k in ('h1','h1_seed28'))]
assert len(segments)==1 and segments[0]['charged_expert_seconds']==7229.854897737503
assert segments[0]['experts']['h1']['charged_seconds']==3613.4053947925568 and segments[0]['experts']['h1_seed28']['charged_seconds']==3616.4495029449463
for pid,created in ((630841,1793213510.36),(630857,1793213511.01),(630876,1793213511.66)):
 try:
  q=psutil.Process(pid)
  if q.create_time()==created:assert q.status()==psutil.STATUS_ZOMBIE,'known107 still executing'
 except psutil.NoSuchProcess:pass
gpu=v['GPU'];assert gpu in ('GPU-c27eecbd-6838-7290-1cd2-37e34522213d','GPU-16828f91-2b45-b646-8dc0-9481138e2842')
for p in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/('three_expert_v2_'+gpu+'.lock'),C.parent.parent/'finite_environment_validation.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(owned).free>25*1024**3
oldrows={r['relative']:r for r in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']};B.mkdir(parents=True);need=[];copied=0
for row in v['manifest']['files']:
 rel=row['relative'];r=PurePosixPath(rel);dest=B/rel;src=old/rel;previous=oldrows.get(rel)
 assert not r.is_absolute() and '..' not in r.parts and '\\' not in rel and dest.resolve().is_relative_to(B.resolve())
 dest.parent.mkdir(parents=True,exist_ok=True)
 if rel==v['new_native_relative']:
  native=Path(v['native_source_path']);assert native==old/'job0/production/native_supermimic_H1_final.pt' and not native.is_symlink() and native.stat().st_size==row['bytes'];shutil.copy2(native,dest);copied+=1
 elif previous and previous['bytes']==row['bytes'] and previous['SHA']==row['SHA'] and src.is_file() and not src.is_symlink() and src.stat().st_size==row['bytes']:shutil.copy2(src,dest);copied+=1
 else:need.append(row)
for name in ('home','tmp','cache','config','data'):(B/'job0'/name).mkdir(exist_ok=True)
assert shutil.disk_usage(B).free>25*1024**3 and C.read_bytes()==raw
print(json.dumps(dict(root=str(B),need_upload=need,files_reused=copied,C_SHA=hashlib.sha256(raw).hexdigest(),remaining_snapshot=c['remaining_training_seconds'],resource=dict(GPU_UUID=gpu,CPU_only_not_GPU_admission=True,RAM_available=psutil.virtual_memory().available,disk_after_copy=shutil.disk_usage(B).free),original107_fees_allout_CNone_readonly=True,no_account_write=True,no_GO=True)))
'''
old=T/'MOD4_H1_FUDAN270_EPISODE20_RESOURCE_V106_20261029/install_TWO106_new20s_source_SDK_fullstate_CPU_UNUSED_once.py'
s=old.read_text(encoding='utf8');tree=ast.parse(s);node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='PRE' for x in n.targets));lines=s.splitlines(keepends=True)
s=''.join(lines[:node.lineno-1])+'PRE='+repr(PRE)+'\n'+''.join(lines[node.end_lineno:])
s=s.replace('TWO106_COHERENT20S_SEALED_PAYLOADS_ACTUAL.json','TWO111_SOURCE_PAYLOADS_PREPARED_NO_GO_ACTUAL.json').replace('SOURCE106_COHERENT20S_CLOCK_AND_INVERSE_DELTAS_CPU_ACTUAL.json','SOURCE111_PREINSTALL_TASK_GO_SOURCE_BINDING_CPU_ACTUAL.json')
s=s.replace('TWO106','TWO111').replace('NATIVE106_V3','NATIVE111_V1')
dest=N/'install_TWO111_task_coherence_source_SDK_fullstate_CPU_UNUSED_once.py';ast.parse(s);dest.write_text(s,encoding='utf8',newline='\n')
put('FROZEN_SOURCE111_PREINSTALL_INDEX_ACTUAL.json',dict(epoch=time.time(),status='FROZEN_NEW111_UNUSED_TARGET_CPU_SOURCE',entry=str(dest),entry_SHA=H(dest),source_metadata_CPU_passed=True,source_coherence_CPU_path=str(L/'native111_coherent_world_task_reward_source_v3'),payloads={k:dict(root=v['job_root'],manifest_SHA=v['manifest_SHA'],source_contract_SHA=v['source_contract_SHA']) for k,v in prep['payloads'].items()},no_model_or_remote_or_GO_yet=True))
print(json.dumps(dict(passed=True,payloads=2,negative_checks=16,entry=str(dest),entry_SHA=H(dest))))
