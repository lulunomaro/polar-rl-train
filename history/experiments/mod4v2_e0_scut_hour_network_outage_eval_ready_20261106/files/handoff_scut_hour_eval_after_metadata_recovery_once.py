"""Wait only for recovered actual closure; one independent eval after qualified release, no training replay."""
from pathlib import Path
import json,time,hashlib,subprocess,sys,traceback
D=Path(__file__).resolve().parent
mark=D/'SCUT_HOUR_EVAL_RECOVERED_HANDOFF_ONCE.json';result=D/'SCUT_HOUR_EVAL_RECOVERED_HANDOFF_RESULT.json'
assert not mark.exists()and not result.exists()
root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_SCUT_HOUR_FULL_LEARNER_MIGRATION_20261106_062902_1793917742719982000'
pointer=D/'E0_SCUT_HOUR_CLOSED_RESULT_PATH.json'
cli=['SCUT_E0_HOUR_FROZEN_stage.py','SCUT_E0_HOUR_FROZEN_dispatch_once.py','SCUT_E0_HOUR_FROZEN_collect_once.py']
pins={name:hashlib.sha256((D/name).read_bytes()).hexdigest()for name in cli}
mark.write_text(json.dumps(dict(epoch=time.time(),training_root=root,only_actual_qualified_post_close_evaluation=True,source_pins=pins,training_launch_or_stop_or_model_or_canonical_operations=0),indent=2),encoding='utf8')
state=dict(started_epoch=time.time(),phase='WAIT_RECOVERED_ORIGINAL_TRAINING_CLOSED_METADATA',training_root=root,steps=[],goal_complete=False,skill_graduation=None,training_relaunches=0,other_experts_scheduled=False)
def put():
 p=result.with_suffix('.partial');p.write_text(json.dumps(state,indent=2,allow_nan=False),encoding='utf8');p.replace(result)
def run(name,args):
 assert hashlib.sha256((D/name).read_bytes()).hexdigest()==pins[name]
 row=dict(entry=name,started_epoch=time.time(),new_purpose_only=True);state['steps'].append(row);state['phase']='RUN_'+name;put()
 p=subprocess.run([sys.executable,'-B',str(D/name),*args],cwd=D)
 row.update(returncode=p.returncode,actual_wait_returned=True,ended_epoch=time.time());put();p.check_returncode()
try:
 put();deadline=time.monotonic()+3600
 while not pointer.exists():
  network=D/'E0_SCUT_HOUR_NETWORK_RECOVERY2_RESULT.json'
  if network.exists()and json.loads(network.read_bytes()).get('host72_SSH_TCP_reachable')is False:
   state['phase']='DEFERRED_HOST72_NETWORK_UNREACHABLE_REMOTE_TRAINING_STATE_UNKNOWN';put();break
  if time.monotonic()>=deadline:raise TimeoutError('Bounded local closure wait expired; no training replay or inference')
  time.sleep(15)
 else:
  p=json.loads(pointer.read_bytes());closed=json.loads(Path(p['path']).read_bytes());assert p['root']==closed['root']==root
  m=closed['metadata'];end=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];case=closed['cases']['E0']
  assert closed['closed']is closed['all_selected_execution_qualified']is True
  assert all(end[k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released'))and end['errors']==[]
  assert outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0
  q=case['PARENT_WAITED_ACTUAL.json']['semantic_qualification'];f=case['V2_MIGRATION_FINAL.json'];initial=case['SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json']
  assert q['qualified']is True and all(q['checks'].values())and case['ERROR_JSON']=={}
  assert f['window_mode']=='SCUT_V14_ORIGINAL_FINITE_WALL_CLOCK_HOUR'and f['completed_actual_updates']>0
  assert f['latest_complete_save']==f['fullsave']['latest_complete_save']
  assert initial['passed']is True and all(initial[k]is True for k in('actor_exact','critic_exact','normalization_exact','learned_STD_exact','Adam17_exact','LR_exact','iteration_exact'))
  state.update(actual_closed_path=p['path'],actual_training_updates=f['completed_actual_updates'],training_latest_complete=f['latest_complete_save']);put()
  run(cli[0],['--closed',str(pointer)]);run(cli[1],[]);run(cli[2],['--seconds','4500'])
  state['phase']='EVALUATION_ENTRY_SEQUENCE_ACTUALLY_WAITED_NOT_SKILL_ACCEPTANCE';put()
except BaseException:
 state.update(phase='RETAINED_HANDOFF_ERROR_NO_AUTOMATIC_RETRY',error=traceback.format_exc());put();raise
