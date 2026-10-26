from pathlib import Path
import ast,datetime,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
A=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026/agent_three_gpu86b_closing_CPU_protocol_20261026'
H=lambda b:hashlib.sha256(b).hexdigest()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def main():
 proof=json.loads((R/'THREE_GPU86B_FIRST_GO_PPO_NATIVE_POLICY_PHASE_ACTUAL.json').read_bytes())
 assert proof['passed'] and proof['actual_finite_returned'] and proof['phase_exposure_observed']
 rows=[]
 for name in ('collect_three_gpu86b_finals_actual_cost_unused_once.py','review_three_gpu86b_finals_CPU_unused_once.py','three_gpu86b_closing_protocol_v1.py','three_gpu86b_close_readonly_remote_v1.py'):
  raw=(A/name).read_bytes();ast.parse(raw);target=N/name
  with target.open('xb') as f:f.write(raw)
  rows.append(dict(path=str(target),bytes=len(raw),SHA=H(raw),source_path=str(A/name),exact_frozen_copy=True))
 collect='''from pathlib import Path
import runpy,sys
N=Path(__file__).resolve().parent
sys.path.insert(0,str(N))
sys.argv=[str(N/'collect_three_gpu86b_finals_actual_cost_unused_once.py'),'--stage',str(N),'--go-report',str(N/'reports/THREE_GPU86B_FIRST_GO_PPO_NATIVE_POLICY_PHASE_ACTUAL.json')]
runpy.run_path(sys.argv[0],run_name='__main__')
'''
 review='''from pathlib import Path
import runpy,sys
N=Path(__file__).resolve().parent
sys.path.insert(0,str(N))
sys.argv=[str(N/'review_three_gpu86b_finals_CPU_unused_once.py'),'--stage',str(N)]
runpy.run_path(sys.argv[0],run_name='__main__')
'''
 for name,source in [('close_actual_three86B_original_cost_fixed_paths_unused_once.py',collect),('review_actual_three86B_typed_fullstate_fixed_paths_CPU_unused_once.py',review)]:
  ast.parse(source)
  with (N/name).open('x',encoding='utf8',newline='\n') as f:f.write(source)
 base=T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v177.py'
 s=base.read_text('utf8');needle="        'collect_three_gpu86B_missing_target_identity_loader_argv_V3_once.py',"
 assert s.count(needle)==1
 s=s.replace(needle,needle+"\n        'close_actual_three86B_original_cost_fixed_paths_unused_once.py',",1)
 needle='    module, previous = install()'
 guard='''    if target.name=='close_actual_three86B_original_cost_fixed_paths_unused_once.py':
        import json,time
        expected=Path(__file__).resolve().parent.parent/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026'
        assert target.resolve()==(expected/target.name).resolve() and len(sys.argv)==2
        observed=json.loads((expected/'reports/THREE_GPU86B_FIRST_GO_PPO_NATIVE_POLICY_PHASE_ACTUAL.json').read_bytes())
        assert observed['passed'] and observed['actual_finite_returned']
        original_go=observed['go']
        assert set(original_go)=={'h1','e2','recovery'}
        assert max(x['nominal_end_epoch'] for x in original_go.values())-time.time()<=900, 'Original local900 gate before secret recovery retained'
'''
 assert s.count(needle)==1;s=s.replace(needle,guard+needle,1);ast.parse(s)
 transport=base.with_name('same_authorized_session_compressed_transport_v178.py')
 with transport.open('x',encoding='utf8',newline='\n') as f:f.write(s)
 go=proof['go'];tz=datetime.timezone(datetime.timedelta(hours=8))
 stamp=lambda epoch:datetime.datetime.fromtimestamp(epoch,tz).isoformat()
 gate=max(x['nominal_end_epoch'] for x in go.values())-900
 work=dict(schema='mod4.actual86b.resumed_native_phase72.three_go.v1',epoch=time.time(),run_id=proof['run_id'],
  actual_three_installed_source_SDK_fullstate_and_GO_first_updates_passed=True,first_proof=str(R/'THREE_GPU86B_FIRST_GO_PPO_NATIVE_POLICY_PHASE_ACTUAL.json'),
  roles=dict(h1='normal H1 PPO on single210',e2='Fudan-reference native H1 SuperMimic on dual72 GPU16828, not normal E2',recovery='normal E3 PPO on dual72 GPUc27'),
  restored_native=dict(iteration=68,world_updates=680,policy_updates=58,three_optimizers=True,new_episode=True,replay_restored=False,fresh_refill48=True),
  first_new_native=dict(before_control=72,cumulative_world_updates=690,cumulative_policy_updates=59,no_new_fresh_ten_world_only_wait=True),
  cached_phase_snapshot=proof['targets']['e2']['phase'],
  no_verified_step_success_or_convergence_claim=True,snapshot_not_continuous_alive=True,current_final_and_fees_pending=True,
  original_go=go,closing_earliest_BJT=stamp(gate),save_deadlines_BJT={k:stamp(v['save_deadline']) for k,v in go.items()},nominal_end_BJT={k:stamp(v['nominal_end_epoch']) for k,v in go.items()},
  only_unused_collector=str(N/'close_actual_three86B_original_cost_fixed_paths_unused_once.py'),transport=str(transport),
  only_unused_initial_CPU_reviewer=str(N/'review_actual_three86B_typed_fullstate_fixed_paths_CPU_unused_once.py'),frozen_close_source_copies=rows,
  authority72='sole finite canonical; old210 authority stays retired and fenced; no new writer, extension, refund or ledger copy',
  qualified_sources=dict(normal_H1='83B / 829700 / 8bb9869ac683550c1e7be1c9dffae9a5eac022e0de0fc8f251cd2005cfa6d4c6',normal_E2='83B retained, native slot is not E2 production',native_H1='formal85 / 68 iterations / 680WM / 58Pi / 94e7f272176b4a7c485b50c1ac61f95a3ecd4460ee6a73034f9e7a47a57045af',normal_E3='85 / 862540 / 7f8f270c84b7e3d9e7efd0b1bd29d10d430a51bb976e1689222859f24e714d59'),
  original_errors_retained=['N86 control deps home filesystem free0; expanded-volume isolated deps succeeded','N86 native SDK preGO rich path omission; N86B actual SDK passed in new namespace','normal payload local keyword TypeError preserved','observer V1 embedded syntax error before metadata','observer V2 successful owner snapshot then wrong direct-python argv expectation; V3 missing-target-only loader-prefix validation passed','one subagent capacity error resumed in same helper, no extra or nested agent'],
  root_filesystem_zero_and_expanded_NTFS_healthy_snapshot=True,no_cleanup_or_mount_changes=True,
  all_current_helpers_frozen=True,at_most_one_future_subagent_no_parallel_or_nested=True,
  current_training_not_hotpatched=True,physical_reward_actor_command_physics_save_success_unchanged=True,
  further_work='Close original three-slot run at original900 boundary, initial typed CPU review once, inspect completed-control events and optional phase exposure; do not infer skill from losses or phase coverage.')
 put('CURRENT_ACTUAL86B_NATIVE85_RESUMED_PHASE72_THREE_GO_WORK_ORDER.json',work)
 put('FROZEN_CLOSE_SOURCE_COPIES_FIXED_WRAPPERS_AND_TRANSPORT178_ACTUAL.json',dict(epoch=time.time(),copies=rows,transport_path=str(transport),transport_SHA=H(transport.read_bytes()),wrappers_compiled=True,no_actual_close_or_model_read=True))
 print(json.dumps(dict(passed=True,closing_earliest_BJT=work['closing_earliest_BJT'],source_copies=len(rows),no_close_executed=True)))
if __name__=='__main__':main()
