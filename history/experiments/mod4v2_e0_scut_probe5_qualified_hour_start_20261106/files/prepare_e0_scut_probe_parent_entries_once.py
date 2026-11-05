"""A new E0-only SCUT recipe/native/initial-checkpoint + one-PPO purpose, never an hour launch."""
from pathlib import Path
import ast,json
D=Path(__file__).resolve().parent
v=json.loads(Path(json.loads((D/'E0_HOUR_WINDOW_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());m=v['metadata'];end=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];assert v['closed']is True and all(end[k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released'))and end['errors']==[] and outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0
MODE='SCUT_V14_NATIVE_AND_ONE_PPO_PROBE_NOT_HOUR';WORKER='worker_e0_scut_v14_probe_v1.py';STAGER='stage_e0_scut_probe_nonpt_v1.py';assert(D/WORKER).is_file()
outputs={};old=(D/'source_owner_e0_hour_v1/migration_nine_original_owner_v1.py').read_text(encoding='utf8');s=old.replace("e['max_additional_updates']==1000000","e['max_additional_updates']==1")
s=s.replace('max_additional_updates=1000000','max_additional_updates=1').replace('ORIGINAL_FINITE_WALL_CLOCK_HOUR',MODE).replace('_FULL20K_ORIGINAL_HOUR_','_SCUT_NATIVE_INITIAL_AND_ONE_UPDATE_')
lines=s.splitlines(keepends=True);i=next(i for i,x in enumerate(lines)if "checks['finite_hour_actual']="in x);lines[i]="  checks['finite_probe_actual']=f.get('completed_actual_updates')==1 and f.get('actual_optimizer_steps')==20 and f.get('actual_rollout_controls')==24 and f.get('window_mode')=="+repr(MODE)+" and f.get('requested_update_quota')==1 and f.get('hour_not_started')is True\n";s=''.join(lines)
a="  ip=job/'production/V2_APP_CLOSE_INTENT.json'\n";assert s.count(a)==1;s=s.replace(a,"  ap=job/'production/SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json';initial=json.loads(ap.read_bytes())if ap.exists()else{}\n  checks['initial_actor_norm_complete_acceptance']=initial.get('passed')is True and initial.get('source_SHA')==e['source_SHA'] and all(initial.get(k)is True for k in('actor_exact','critic_exact','normalization_exact','learned_STD_exact','Adam17_exact','LR_exact','iteration_exact'))\n  checks['runtime_recipe_receipt_present']=(job/'production/SCUT_RECIPE_BINDING.json').is_file()\n"+a)
outputs[D/'source_owner_e0_scut_probe_v1/migration_nine_original_owner_v1.py']=s
s=(D/'stage_e0_hour_nonpt_runtime_v1.py').read_text(encoding='utf8').replace('stage_e0_hour_nonpt_runtime_v1.py',STAGER).replace('worker_mod4v2_expert_migration_hour_v5.py',WORKER);a="'V2_LOCAL_VALIDATION.json'):";assert s.count(a)==1;s=s.replace(a,"'V2_LOCAL_VALIDATION.json', 'scut_v14_flat_reward_adapter_v2.py', 'scut_v14_flat_command_termination_adapter_v1.py'):");outputs[D/STAGER]=s
for oldname,newname in [('stage_e0_hour_window_once.py','stage_e0_scut_probe_once.py'),('dispatch_e0_hour_window_once.py','dispatch_e0_scut_probe_once.py'),('collect_e0_hour_window_once.py','collect_e0_scut_probe_once.py')]:
 s=(D/oldname).read_text(encoding='utf8').replace('E0_HOUR_WINDOW','E0_SCUT_PROBE').replace('ORIGINAL_FINITE_WALL_CLOCK_HOUR',MODE).replace('worker_mod4v2_expert_migration_hour_v5.py',WORKER).replace('stage_e0_hour_nonpt_runtime_v1.py',STAGER).replace('source_owner_e0_hour_v1','source_owner_e0_scut_probe_v1').replace('max_additional_updates=1000000','max_additional_updates=1')
 if oldname.startswith('stage_'):
  a="payload['SOURCE_PLAN.json']=json.dumps(plan,indent=2).encode();";assert s.count(a)==1;s=s.replace(a,"payload['scut_v14_flat_reward_adapter_v2.py']=(D/'scut_v14_flat_reward_adapter_v2.py').read_bytes();payload['scut_v14_flat_command_termination_adapter_v1.py']=(D/'scut_v14_flat_command_termination_adapter_v1.py').read_bytes();plan.update(reference_task='Robotics-Wheelbipe-V14-Flat-v0',reference_HEAD='b8ff79f3df855faf9dc92f4a282bd80c42649466',probe_only=True,hour_not_started=True);"+a)
 if oldname.startswith('collect_'):
  a="'V2_NATIVE_INITIALIZED.json'";assert a in s;s=s.replace(a,"'SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json','SCUT_RECIPE_BINDING.json','V2_NATIVE_INITIALIZED.json'",1)
 outputs[D/newname]=s
for p,s in outputs.items():assert not p.exists();ast.parse(s);compile(s,str(p),'exec')
# Original resource admission/accounting/wait/cleanup functions remain unchanged.
t0=ast.parse(old);t1=ast.parse(outputs[D/'source_owner_e0_scut_probe_v1/migration_nine_original_owner_v1.py'])
for name in('gpu','account','environment','main'):
 a=next(x for x in t0.body if isinstance(x,ast.FunctionDef)and x.name==name);b=next(x for x in t1.body if isinstance(x,ast.FunctionDef)and x.name==name);assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False),name
for p,s in outputs.items():p.parent.mkdir(exist_ok=True);p.write_text(s,encoding='utf8',newline='\n')
print('New source-only SCUT probe parent/stager/entries: exactly E0/N20000/T24/1update; original resource/account/actualwait/main unchanged; no launch')
