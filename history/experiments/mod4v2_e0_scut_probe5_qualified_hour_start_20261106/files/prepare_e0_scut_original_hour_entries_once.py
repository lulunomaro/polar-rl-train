"""Publish NEW finite-hour entries only after the third source probe truly closed and qualified."""
from pathlib import Path
import ast,json,hashlib
D=Path(__file__).resolve().parent
pointer=json.loads((D/'E0_SCUT_PROBE_ADMISSION4_CLOSED_RESULT_PATH.json').read_bytes());path=Path(pointer['path']);closed=json.loads(path.read_bytes());m=closed['metadata'];case=closed['cases']['E0'];end=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];q=case['PARENT_WAITED_ACTUAL.json']['semantic_qualification'];f=case['V2_MIGRATION_FINAL.json'];initial=case['SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json']
assert closed['closed']is True and all(end[k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released'))and end['errors']==[] and outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0
assert q['qualified']is True and all(q['checks'].values())and f['completed_actual_updates']==1 and f['actual_optimizer_steps']==20 and f['actual_rollout_controls']==24 and f['window_mode']=='SCUT_V14_NATIVE_AND_ONE_PPO_PROBE_NOT_HOUR'and f['hour_not_started']is True
assert initial['passed']is True and initial['source_SHA']=='6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693'and all(initial[k]is True for k in('actor_exact','critic_exact','normalization_exact','learned_STD_exact','Adam17_exact','LR_exact','iteration_exact'))
MODE='SCUT_V14_ORIGINAL_FINITE_WALL_CLOCK_HOUR';WORKER='worker_e0_scut_v14_hour_v1.py';STAGER='stage_e0_scut_hour_nonpt_v1.py';assert(D/WORKER).is_file()
old=(D/'source_owner_e0_scut_probe_v1/migration_nine_original_owner_v1.py').read_text(encoding='utf8');s=old.replace("e['max_additional_updates']==1 ","e['max_additional_updates']==1000000 ").replace('max_additional_updates=1,','max_additional_updates=1000000,').replace('SCUT_V14_NATIVE_AND_ONE_PPO_PROBE_NOT_HOUR',MODE).replace('_SCUT_NATIVE_INITIAL_AND_ONE_UPDATE_','_SCUT_NATIVE_U000_AND_ORIGINAL_HOUR_')
lines=s.splitlines(keepends=True)
for i,line in enumerate(lines):
 if "checks['finite_probe_actual']="in line:
  indent=line[:len(line)-len(line.lstrip())];lines[i]=indent+"u=f.get('completed_actual_updates',0);checks['finite_SCUT_hour_actual']=0<u<=1000000 and f.get('actual_optimizer_steps')==20*u and f.get('actual_rollout_controls')==24*u and f.get('window_mode')=="+repr(MODE)+" and f.get('requested_update_quota')is None and f.get('hour_not_started')is False and f.get('stop_reason')in('STOP_SAVE','save_deadline')\n";break
else:raise AssertionError('Actual probe qualification line absent')
s=''.join(lines);outputs={D/'source_owner_e0_scut_hour_v1/migration_nine_original_owner_v1.py':s}
a=ast.parse(old);b=ast.parse(s)
for name in('gpu','account','environment','main'):
 x=next(n for n in a.body if isinstance(n,ast.FunctionDef)and n.name==name);y=next(n for n in b.body if isinstance(n,ast.FunctionDef)and n.name==name);assert ast.dump(x,include_attributes=False)==ast.dump(y,include_attributes=False),name
s=(D/'stage_e0_scut_probe_nonpt_v3.py').read_text(encoding='utf8').replace('worker_e0_scut_v14_probe_v3.py',WORKER).replace('stage_e0_scut_probe_nonpt_v3.py',STAGER);outputs[D/STAGER]=s
ready_name='E0_SCUT_THIRD_PROBE_ACTUAL_QUALIFIED_HOUR_READINESS.json'
for kind in('stage','dispatch','collect'):
 s=(D/(kind+'_e0_scut_probe_admission3_once.py')).read_text(encoding='utf8').replace('E0_SCUT_PROBE_ADMISSION4_','E0_SCUT_HOUR_').replace('e0_scut_probe_admission3_','e0_scut_hour_').replace('worker_e0_scut_v14_probe_v3.py',WORKER).replace('stage_e0_scut_probe_nonpt_v3.py',STAGER).replace('source_owner_e0_scut_probe_v1','source_owner_e0_scut_hour_v1').replace('SCUT_V14_NATIVE_AND_ONE_PPO_PROBE_NOT_HOUR',MODE).replace('max_additional_updates=1,','max_additional_updates=1000000,').replace('probe_only=True,hour_not_started=True','probe_only=False,hour_not_started=False')
 if kind=='stage':
  anchor='D=Path(__file__).resolve().parent;';assert s.count(anchor)==1;s=s.replace(anchor,anchor+"accepted=json.loads((D/'"+ready_name+"').read_bytes());assert accepted['actual_closed_probe_qualified']is True and accepted['initial_checkpoint_all_exact']is True and accepted['probe_actual_updates']==1 and accepted['hour_not_yet_started']is True;")
 outputs[D/(kind+'_e0_scut_hour_once.py')]=s
for p,s in outputs.items():assert not p.exists();ast.parse(s);compile(s,str(p),'exec')
ready=D/ready_name;assert not ready.exists()
for p,s in outputs.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8',newline='\n')
ready.write_text(json.dumps(dict(kind='ACTUAL_SCUT_PROBE_CLOSED_QUALIFIED_INITIAL_ALL_EXACT_NOT_SKILL_GRADUATION',root=closed['root'],closed_path=str(path),closed_SHA=hashlib.sha256(path.read_bytes()).hexdigest(),actual_closed_probe_qualified=True,initial_checkpoint_all_exact=True,probe_actual_updates=1,probe_optimizer_steps=20,probe_rollout_controls=24,original_owner_exit=end,actual_outer_wait=outer,qualification=q,initial_checkpoint_acceptance=initial,hour_not_yet_started=True,hour_source_and_candidate_choice='Formal6cd same original learner, not failed candidates; no update-count splice from independent probe',hour_update_quota=None,original_save_total_headroom_preGO=[3600,3900,300,1800],no_additional_budget_or_refund=True,other_experts_scheduled=False,goal_complete=False),indent=2,allow_nan=False),encoding='utf8')
print('SCUT E0 hour sources published after ACTUAL probe+U000 exact+one update+full close; original resource/account/main unchanged; no stage/dispatch/SDK/model execution.')
