from pathlib import Path
import ast,hashlib,json,shutil,time
S=Path(__file__).resolve().parent;T=S.parent;R=S/'reports'
old=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V67_20261024'
N=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025'
assert not N.exists();shutil.copytree(old,N)
for p in N.rglob('*'):
 if p.is_file() and p.suffix in ('.py','.json'):
  a=p.read_text('utf8');b=a.replace(old.name,N.name).replace('H1step270_reward_tuckclear4_2410v67','H1step270_reward_airfeasible5_2510v67')
  if b!=a:p.write_text(b,encoding='utf8')
candidate=S/'reward_candidate_V5_V2';repair=N/'repair_sources'
a=(candidate/'h1_step270_path_reward_v1.py').read_text('utf8')
a=a.replace('No action, command, physics, termination, success contract, RNG or optimizer\naccess.','No action, command, physics, termination, success contract, RNG or optimizer\nwrites. The new cost reads only the already delayed leg target.')
(repair/'h1_step270_path_reward_v1.py').write_text(a,encoding='utf8')
shutil.copy2(candidate/'step270_reward_installed_CPU_v1.py',repair/'step270_reward_installed_CPU_v1.py')
# Pure CPU contract validation already passed; live installed SDK integration is required by the original deployer before owner launch.
auth=json.loads((repair/'H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json').read_bytes())
prior=json.loads((old/'repair_sources/H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json').read_bytes())
cpu=json.loads((R/'V5_V2_NEW_AIRBORNE_TARGET_REWARD_SYNTHETIC_CPU_ACTUAL.json').read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
auth.update(epoch=time.time(),human_request='继续看回放修复上台阶；继续',scope='Reward-only measured airborne infeasible delayed leg-target residual. Original V4 tuck1.7/.22, request.8/100..179, phase, goal270mm/200callbacks, mesh/physics/PPO/17Adam/STD/account/save remain unchanged. Actual installed SDK reward compute must pass before new owner launch.',replay_report=str(R/'LATEST65_AIRBORNE_EXTENSION_AND_ACTION_SATURATION_DESCRIPTIVE_ACTUAL.json'),reward_CPU=cpu,integration_CPU=dict(cpu,scope='Local synthetic wrapper integration; actual SDK compute pending original installed CPU gate'),new_reward_module_SHA=H(repair/'h1_step270_path_reward_v1.py'),original_reward_module_SHA='42a6a4bf690d474dcb2359609dfcb189df2b7aaf0ee229f74a286fcc3a9bda76',installed_reward_checker_SHA=H(repair/'step270_reward_installed_CPU_v1.py'),new_reward_recipe_version='step270_airborne_feasible_target_v5',previous_v4_auth_preserved_path=str(old/'repair_sources/H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json'),previous_v4_passed_CPU_evidence=prior['reward_CPU'],human_reply_auth=str(R/'USER_REPLAY_REPAIR_AUTHORIZATION_AND_SCOPE_ACTUAL.json'))
(repair/'H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json').write_text(json.dumps(auth,ensure_ascii=False,indent=2),encoding='utf8')
preparer=N/'prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py'
a=preparer.read_text('utf8').replace("reward_recipe_version='step270_current_clearance_airborne_tuck_v4'","reward_recipe_version='step270_airborne_feasible_target_v5'")
preparer.write_text(a,encoding='utf8')
for p in N.rglob('*.py'):ast.parse(p.read_bytes())
# Normalize only the declared new reward nodes/docstring to compare all old V4 methods/config.
def normalize(s,new):
 t=ast.parse(s)
 if isinstance(t.body[0],ast.Expr) and isinstance(t.body[0].value,ast.Constant):t.body.pop(0)
 if new:
  t.body=[n for n in t.body if not isinstance(n,ast.FunctionDef) or n.name not in ('infeasible_leg_target_cost','airborne_leg_target_overdrive_rate')]
  for n in ast.walk(t):
   if isinstance(n,ast.Constant) and n.value=='step270_airborne_feasible_target_v5':n.value='step270_current_clearance_airborne_tuck_v4'
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='dict':n.keywords=[q for q in n.keywords if q.arg!='airborne_leg_target_overdrive_weight']
   if isinstance(n,ast.FunctionDef) and n.name=='configure':n.body=[q for q in n.body if not isinstance(q,ast.Assign) or not any(isinstance(x,ast.Attribute) and x.attr=='h1_step270_airborne_leg_target_overdrive' for x in q.targets)]
 return ast.dump(t)
assert normalize((old/'repair_sources/h1_step270_path_reward_v1.py').read_text('utf8'),False)==normalize((repair/'h1_step270_path_reward_v1.py').read_text('utf8'),True)
assert H(repair/'h1_step270_sdk_runtime_candidate.py')=='0ec7db1fc55ca0d552341e24237048a916d1cbb6b125905eb22b0001b60a8e34'
assert H(repair/'target_H1_step270_closed_source_sdk_cpu_review_v1.py')==auth['target_CPU_SHA']
for mode in ('paired_controllers','h1_only_controllers'):
 for p in (old/mode).glob('*.py'):assert p.read_bytes()==(N/mode/p.name).read_bytes()
report=dict(epoch=time.time(),passed=True,candidate_root=str(N),old_unused_V4_root_preserved=str(old),latest_source_required='closed66_LISTENER_V2 full models/Adam/wholeCPU/original cost',new_reward_SHA=auth['new_reward_module_SHA'],new_checker_SHA=auth['installed_reward_checker_SHA'],same_original_runtime_SHA=auth['new_runtime_SHA'],all_previous_V4_reward_AST_exact=True,controllers_PPO_save_account_exact=True,doc_only_correction_from_tested_V2=True,no_payload_or_Task_GO_fee_yet=True,new_owner_budget_total=2268000,extensions=9,guard=82512.86069250107,original_listener_bounded_wait_inherited=True)
with (R/'V5_NEW67_NAMESPACE_REWARD_AUTH_AND_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report))

