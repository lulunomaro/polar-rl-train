"""New E2 sole-role SOURCE API/AST+refusals only. No old fixture or model."""
from pathlib import Path
import ast,copy,hashlib,json,time,traceback

N=Path(__file__).resolve().parent
T=N.parent


def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


def main():
 purpose=json.loads((N/'reports/CPU_E2_SOLO_PURPOSE_FROZEN.json').read_bytes())
 put(N/'reports/CPU_E2_SOLO_ONCE_CONSUMED.json',dict(ID=purpose['ID'],epoch=time.time()))
 texts={}
 for row in purpose['sources']:
  p=Path(row['path']);raw=p.read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA']
  ast.parse(raw,filename=str(p));texts[p.relative_to(N).as_posix()]=raw.decode()
 import e2_solo_contract as c
 import e2_solo_protocol as protocol
 cpu_path=T/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028/reports/E2_93_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V1.json'
 q,qr=c.metadata(cpu_path);c.qualified_cpu(q,qr['SHA'])
 base=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/E2_PPO50_gas400_source_preparation_20261028'
 env=c.metadata(base/'original_run_manifest.json')[0]['env']
 assert env['RM_SPIN_STAGE']=='world_directional_v1' and env['RM_SPIN_WORLD_PROGRESS_M_S']=='0.5' and env['RM_KEEP_STD']=='1'
 assert env['RM_PURE_SPIN_FRACTION']=='.30' and env['RM_MOVING_SPIN_FRACTION']=='.20' and env['RM_SPIN_TRANSITION_WITHIN_PURE']=='0.3333333333333333'
 task=c.task_base();task.update(run_id='SYNTHETIC_NEW_E2_SOURCE_API_ONLY',GPU_UUID=sorted(c.GPUS)[0],worker_SHA='a'*64)
 assert c.validate_task(task)
 refusals=[]
 for label,key,value in [('wrong_sender_role','role_key','e2_72'),('W35_source','source_SHA','343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'),
  ('wrong_Adam','source_Adam_step',648360),('wrong_LR','source_LR',.00011390625),('STD_reset','preserve_learned_STD',False),
  ('smaller_envs','num_envs',4096),('changed_physics','physics_dt',.001),('changed_world_goal','world_progress_goal',.15)]:
  bad=copy.deepcopy(task);bad[key]=value
  try:c.validate_task(bad)
  except ValueError:refusals.append(label)
  else:raise AssertionError(label)
 spec=dict(key='e2',execution_backend='target72',GPU_UUID=task['GPU_UUID'],num_envs=20000,source_SHA=c.SHA,
  source_iteration=c.ITER,source_Adamstep=c.ADAM,source_LR=c.LR,source_kind=c.KIND,max_parent_seconds=3900,
  exit_headroom_seconds=300,no_physics_change=True,prelaunch_control_snapshot_id='SYNTHETIC_SOURCE_ONLY',manifest_SHA='b'*64,launch_evidence_SHA='c'*64)
 assert protocol.validate_schedule(dict(experts={'e2':spec},deferred_experts=[]))
 go=protocol.flat_go_fields(spec);assert go['role_key']=='e2' and go['source_model_SHA']==c.SHA and go['genuine_original_E2_WORLD_MOVING_SIGNED4']
 ready=dict(passed=True,kind=c.KIND,source_SHA=c.SHA,source_iteration=c.ITER,Adam_step=c.ADAM,source_LR=c.LR,
  source_saved_fullstate_CPU_SHA=c.CPU_SHA,source_fullstate_CPU_passed=True,original232_scoped_fullrestore_native24_reused=True,
  original232_outer_false_preserved=True,all_actor_critic_optimizer_tensors_finite=True,actual_35_38_6_shapes=True,
  fresh_CNone_CIM_resources_passed=True,manifest_SHA=spec['manifest_SHA'],launch_evidence_SHA=spec['launch_evidence_SHA'])
 row=dict(key='e2',phase='ready',manifest_SHA=spec['manifest_SHA'],original_error=False,
  closed_source_CPU=dict(value=ready,SHA=c.ready_SHA(ready),actual_CPU_waited_EXIT0=True))
 assert protocol.valid_ready(row,spec)
 bad=copy.deepcopy(row);bad['closed_source_CPU']['SHA']=c.CPU_SHA;assert not protocol.valid_ready(bad,spec);refusals.append('old_CPU_SHA_is_not_wholeReady_SHA')
 worker=texts['worker_e2_original_fullPPO.py']
 assert "PinnedSource213(torch,source,SHA,BYTES)" in worker and "'E2_moving4_command_state' in full" in worker
 assert "state['iter']=ITER+completed" in worker and 'ADAM+20*completed' in worker
 assert worker.index("put('E2_SOURCE_SELECTED_FINAL_READ_COUNTS.json'")<worker.index("ns['app'].close()")
 assert 'init_at_random_ep_len=True' in worker and 'rescue_training.learn=work' in worker
 assert 'E2_WORLD_MOVING_SIGNED4' in worker and "original['RM_KEEP_STD']=='1'" in worker
 sender=texts['control_e2_solo/forwarded_original_owner_control_v1.py'];assert "'e2'" in sender
 assert 'genuine_original_E2_WORLD_MOVING_SIGNED4' in texts['control_e2_solo/e2_solo_fullstate_slot_node.py']
 assert 'genuine_W35_full_original_RM70_course' not in texts['control_e2_solo/e2_solo_fullstate_slot_node.py']
 for rel,text in texts.items():
  if rel.endswith('worker_e2_original_fullPPO.py'):
   for node in ast.walk(ast.parse(text)):
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):assert node.func.attr not in ('terminate','kill','send_signal','killpg')
 put(N/'reports/CPU_E2_SOLO_NEW_INTERFACE_ACTUAL.json',dict(passed=True,ID=purpose['ID'],source_AST_count=len(purpose['sources']),
  groups=3,new_rejection_cases=refusals,rejection_count=len(refusals),synthetic_interface_only=True,
  actual_fresh_Task_Ready_or_GO_generated=False,saved_qualified_CPU_metadata=qr,
  profile='originalworld_directional_v1 +.5/.30pure/.20moving/1of3transition/restoriginalmix',
  first_expected_iteration=42823,first_expected_Adam17=859320,first_expected_PPO_transitions=480000,
  selected_source_byte_read_decode_planned=[1,1],actual_model_reads=0,
  old_fixture_replays=0,PT_NPZ_USD_actualraw_Torch_SDK_GPU_network_Git_calls=0,
  actual_target_fullrestore_native24_FIRST_and_learning='PENDING_ROOT_NEW_PURPOSE'))


if __name__=='__main__':
 try:main()
 except BaseException:
  put(N/'reports/CPU_E2_SOLO_ORIGINAL_ERROR.json',dict(passed=False,error=traceback.format_exc(),no_automatic_retry=True));raise
