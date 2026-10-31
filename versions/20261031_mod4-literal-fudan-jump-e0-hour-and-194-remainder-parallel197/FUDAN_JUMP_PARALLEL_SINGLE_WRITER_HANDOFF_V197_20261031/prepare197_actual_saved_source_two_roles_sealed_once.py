from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
O=T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031'
E=T/'E0_82_LITERAL_FUDAN_JUMP72_ONE_HOUR_SOURCE_V198_20261031'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
c=json.loads((R/'ROOT197_HANDOFF_SOURCE194_COMPLETE_SAVED_PREFIX_RETURNED_ACTUAL.json').read_bytes())
cpu=json.loads((R/'ROOT197_SAVED194_INITIAL_CPU_RETURNED_ACTUAL.json').read_bytes())
admit=json.loads((E/'reports/ACTUAL198_TARGET72_CPU_NATIVE64_ADMISSION_RETURNED.json').read_bytes())
assert c['passed_collection'] and c['source_node']['qualified_formal'] and c['owner_closed']['canonical_None'] and c['source_node']['private_EX_free'] and cpu['passed']
assert admit['passed_execution'] and admit['all_own_children_waited'] and admit['private_EX_released']
a=admit['admission'];assert a['source_SHA']=='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a'
oldgo=c['owner_closed']['original_GO'];f=c['source_node']['formal']
used=f['epoch']-oldgo['learning_started_epoch'];remaining=7200.-used
assert 0<remaining<7200,'This two-role handoff requires a real remaining194 window; no padding'
J='/mnt/mod4_linux_durable_20261013/MOD4_JUMP194_REMAINING_PARALLEL_20261031v197/h1_210'
EJ='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_82_FUDAN_JUMP72_400N50_20261031v198/e0_72'
OWNER='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_PARALLEL197_194REMAIN_E0JUMP_2610v197/owner'
D=N/'primary_package';shutil.copytree(O/'train_package',D)
(D/'run194_literal_jump_plane_worker.py').unlink();(D/'TASK194.json').unlink()
shutil.copyfile(N/'run197_resume194_literal_JUMP_worker.py',D/'run197_resume194_literal_JUMP_worker.py')
task=json.loads((O/'train_package/TASK194.json').read_bytes())
task.update(schema='mod4.saved194.literalJUMP.remaining_primary.two-role197',source_kind='ACTUAL194_QUALIFIED_SAVED_PREFIX',
 source_SHA=c['formal']['SHA'],source_bytes=c['formal']['bytes'],formal_source_model=c['formal']['source'],
 source_iteration=cpu['saved_iteration'],source_Adam_step=cpu['Adam_step'],source_trained_policy_hz=50,source_gas_nominal_k=2000,
 source_fullstate_CPU_report=str(R/'ROOT197_SAVED194_INITIAL_CPU_RETURNED_ACTUAL.json'),source_fullstate_CPU_report_SHA=H(R/'ROOT197_SAVED194_INITIAL_CPU_RETURNED_ACTUAL.json'),
 maximum_parent_seconds=remaining+300.,save_deadline_seconds=remaining,exit_headroom_seconds=300,
 old194_original_GO=oldgo,old194_original_requested_seconds=7200.,old194_used_window_seconds=used,remaining_primary_seconds=remaining,
 original_delivery_SHA='5932295297ed93b65fd88fe142d6fc66099c0a936f23091a79a3b2752c51dfa4',
 full_actor_critic_STD_17Adam_and_global_CPU_CUDA_sampling_RNG_restore=True,
 source_adaptive_LR=cpu['optimizer_LR'],fresh_physics_DR_episodes_queues_history=True,
 no_exact_PhysX_episode_or_contact_history_resume=True,
 duration_authority='Human requested parallel E0 one-hour; use one new owner and preserve actual remainder of original194 two-hour window.')
task.pop('learned_STD6',None)
(D/'TASK197.json').write_text(json.dumps(task,indent=2),encoding='utf8')
known={r['relative']:r for r in json.loads((O/'TRAIN194_COMPLETE_MANIFEST.json').read_bytes())['files']}
rows=[]
for p in sorted(D.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(D).as_posix()
 if p.suffix.lower() in ('.usd','.usda','.npz','.npy'):
  r=known[rel];assert p.stat().st_size==r['bytes'];sha=r['SHA']
 else:
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if p.suffix=='.py':ast.parse(raw)
 rows.append(dict(relative=rel,local_relative='primary_package/'+rel,bytes=p.stat().st_size,SHA=sha))
(N/'PRIMARY197_COMPLETE_MANIFEST.json').write_text(json.dumps(dict(files=rows,model_files=0),indent=2),encoding='utf8')
mh=H(N/'PRIMARY197_COMPLETE_MANIFEST.json');emh=H(E/'PACKAGE198_MANIFEST.json')
base=dict(num_envs=20000,seed=27,exit_headroom_seconds=300,literal_original_fudan_JUMP=True,no_reward_or_physics_change=True)
h=dict(base,key='h1_210',execution_backend='source210',GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',max_parent_seconds=remaining+300.,
 remaining_primary_seconds=remaining,old194_requested_seconds=7200.,old194_used_seconds=used,
 source_SHA=task['source_SHA'],source_Adamstep=task['source_Adam_step'],source_iteration=task['source_iteration'],
 manifest_file='PRIMARY197_COMPLETE_MANIFEST.json',manifest_SHA=mh,job_root=J,python='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',
 private_lock='/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock',worker_script='run197_resume194_literal_JUMP_worker.py')
e=dict(base,key='e0_72',execution_backend='target72',GPU_UUID=a['selected_GPU'],max_parent_seconds=3900,
 source_SHA=a['source_SHA'],source_Adamstep=641200,source_iteration=31984,manifest_file='PACKAGE198_MANIFEST.json',manifest_SHA=emh,
 job_root=EJ,python='/home/lc01/Zonglin Li/zonglin2/run-python.sh',private_lock=a['resource']['private_lock'],worker_script='run198_E0_JUMP72_400N50_worker.py')
schedule=dict(schema='mod4.parallel197.single_original_writer.two_genuine_PPO_roles',experts=dict(h1_210=h,e0_72=e),old194_original_GO=oldgo,
 old194_full_close_CPU_passed=True,owner_root=OWNER,source_handoff_report_SHA=H(R/'ROOT197_HANDOFF_SOURCE194_COMPLETE_SAVED_PREFIX_RETURNED_ACTUAL.json'),source_E0_admission_report_SHA=H(E/'reports/ACTUAL198_TARGET72_CPU_NATIVE64_ADMISSION_RETURNED.json'))
import sys;sys.path.insert(0,str(N));import parallel197_protocol as protocol
assert protocol.validate_schedule(schedule)
(N/'SCHEDULE_PUBLIC.json').write_text(json.dumps(schedule,indent=2),encoding='utf8')
old0pt=json.loads((O/'reports/ROOT194ADMITV2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json').read_bytes());assert old0pt['passed_execution'] and old0pt['returncode']==0 and old0pt['private_EX_released']
for key,spec in schedule['experts'].items():
 v=dict(passed=True,kind='LITERAL_JUMP_PARALLEL197_READY',source_SHA=spec['source_SHA'],source_iteration=spec['source_iteration'],Adam_step=spec['source_Adamstep'],
  all_actor_critic_optimizer_tensors_finite=True,actual_35_38_6_shapes=True,actual_original_JUMP19_text_identity=True,source_fullstate_CPU_passed=True,
  actual_target0PT_waited_RC=0,actual_target0PT_controls=8,actual_target0PT_physics=64,actual_target0PT_feedback=16,target0PT_private_EX_released=True,manifest_SHA=spec['manifest_SHA'],
  physical_source_admission_report_SHA=H(E/'reports/ACTUAL198_TARGET72_CPU_NATIVE64_ADMISSION_RETURNED.json') if key=='e0_72' else H(O/'reports/ROOT194ADMITV2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json'),
  fullstate_CPU_scope='Existing exact E0 whole-state qualification' if key=='e0_72' else 'One NEW actual completed194 saved-prefix whole-state CPU qualification',
  no_new_target_model_decode_before_actual_GO=True)
 (N/('ADMISSION197_READY_'+key+'.json')).write_text(json.dumps(v,indent=2),encoding='utf8')
 node_row=dict(key=key,phase='ready',manifest_SHA=spec['manifest_SHA'],original_error=False,closed_source_CPU=dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()))
 assert protocol.valid_ready(node_row,spec)
rows=[dict(relative=p.name,local_path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted((N/'control').iterdir()) if p.is_file()]
(N/'CONTROL197_MANIFEST.json').write_text(json.dumps(dict(files=rows),indent=2),encoding='utf8')
put('ROOT197_ACTUAL_SAVED_SOURCE_AND_TWO_GENUINE_ROLES_SEALED.json',dict(epoch=time.time(),passed=True,old194_saved_iteration=cpu['saved_iteration'],old194_Adam=cpu['Adam_step'],
 old194_one_raw_fee=c['owner_closed']['raw_fee_sum_once'],old194_used_window_seconds=used,remaining_primary_seconds=remaining,
 E0_one_hour_seconds=3600,one_owner_sum_distinct_actual_fees=True,old194_source_or_E0_model_not_changed=True,
 primary_manifest_SHA=mh,E0_manifest_SHA=emh,schedule_SHA=H(N/'SCHEDULE_PUBLIC.json'),no_canonical_or_model_content_read_here=True))
print(json.dumps(dict(sealed=True,old194_saved_iteration=cpu['saved_iteration'],remaining_primary_seconds=remaining,E0_GPU=e['GPU_UUID'],old_fee=c['owner_closed']['raw_fee_sum_once'])))
