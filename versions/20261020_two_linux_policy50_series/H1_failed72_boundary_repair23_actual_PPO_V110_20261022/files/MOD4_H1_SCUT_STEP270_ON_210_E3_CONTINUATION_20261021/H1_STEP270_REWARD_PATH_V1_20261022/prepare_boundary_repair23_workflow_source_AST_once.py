"""Fresh namespace and narrow runtime admission for actual failed21; no remote work."""
from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';OLD=T/'H1_STEP270_REWARD_RESOURCE_BRANCH_V22_20261022';F=T/'H1_STEP270_REWARD_BOUNDARY_REPAIR_RESOURCE_V23_20261022'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CHECKER=r'''
from pathlib import Path
import ast,hashlib,json,types
import torch
def check(B):
 B=Path(B);auth=json.loads((B/'H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json').read_bytes());repair=auth['arena_boundary_repair_CPU'];p=B/'h1_step270_sdk_runtime_candidate.py';old=B/'boundary_reference_sources/h1_step270_sdk_runtime_original.py'
 H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 assert H(p)==repair['candidate_runtime']['SHA'] and H(old)==repair['old_runtime']['SHA']=='5106639e761abfb51d0ea4a2be3249895f6eb502c2e030c0a1f56565d914f36d'
 a=ast.parse(old.read_text('utf8'));b=ast.parse(p.read_text('utf8'));strip=lambda t:ast.dump(ast.Module(body=[n for n in t.body if not(isinstance(n,ast.FunctionDef) and n.name=='out_of_authored_floor')],type_ignores=[]),include_attributes=False)
 assert strip(a)==strip(b)
 fn=next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name=='out_of_authored_floor');ns={'torch':torch,'tensor':lambda x:x,'wheel_bounds':lambda e:(e.lo,e.hi)};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(p),'exec'),ns)
 class Scene(dict):pass
 origins=torch.tensor([[-176.25,-175.],[176.25,175.]])
 def env(root,lo,hi):
  scene=Scene(robot=types.SimpleNamespace(data=types.SimpleNamespace(root_pos_w=root)));scene.env_origins=origins;return types.SimpleNamespace(scene=scene,lo=lo,hi=hi)
 rng=torch.get_rng_state().clone();root=torch.zeros(20000,3);lo=torch.full((20000,2,3),-.1);hi=torch.full((20000,2,3),.1);f=ns['out_of_authored_floor'];assert not f(env(root,lo,hi)).any()
 hi[11843,1,1]=177.50027465820312;v=f(env(root,lo,hi));assert int(v.sum())==1 and bool(v[11843])
 hi[11843,1,1]=177.5;assert not f(env(root,lo,hi)).any()
 hi[0,0,0]=float('nan')
 try:f(env(root,lo,hi))
 except RuntimeError:pass
 else:raise AssertionError('Nonfinite footprint not rejected')
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 return dict(passed=True,actual_installed_boundary_function_CPU=True,all_other_runtime_AST_exact=True,missing_queries_still_rejected_no_flat_fallback=True,ordinary_per_environment_exit_only=True,no_Kit_PhysX_GPU_actor_optimizer_RNG=True,not_future_GPU_success=True)
'''
def main():
 repair=read(R/'V110_WHEEL_FOOTPRINT_BOUNDARY_REPAIR_CANDIDATE_CPU_ACTUAL.json');failure=read(R/'V110_FAILED21_ORIGINAL_COST_ALL_OUT_HEALTH_AND_RETENTION_CPU_ACTUAL.json');assert repair['passed'] and failure['passed_only_failed_closure_cost_allout_diagnostic_scope'] and not failure['qualified_FINAL']
 assert not F.exists();F.mkdir();(F/'reports').mkdir();D=F/'repair_sources';D.mkdir();(D/'boundary_reference_sources').mkdir()
 for kind in ('paired_controllers','h1_only_controllers'):shutil.copytree(OLD/kind,F/kind)
 flows=[p for p in OLD.glob('*.py') if 'UNEXECUTED' not in p.name and 'UNUSED_OLD' not in p.name]
 for p in flows:
  text=p.read_text('utf8').replace('H1step270_reward_resource_2210v22','H1step270_reward_boundary_2210v23')
  (F/p.name).write_text(text,encoding='utf8')
 shutil.copy2(repair['candidate_runtime']['path'],D/'h1_step270_sdk_runtime_candidate.py');shutil.copy2(repair['old_runtime']['path'],D/'boundary_reference_sources/h1_step270_sdk_runtime_original.py')
 (D/'step270_boundary_installed_CPU_v1.py').write_text(CHECKER,encoding='utf8')
 target=(B/'target_H1_step270_reward_path_closed_source_sdk_cpu_review_v1.py').read_text('utf8');needle="v['reward_runtime_SHA']=H(B/'h1_step270_sdk_runtime_candidate.py')";assert target.count(needle)==1
 target=target.replace(needle,"from step270_boundary_installed_CPU_v1 import check as boundary_check\nv['boundary_repair_integration_CPU']=boundary_check(B)\n"+needle)
 (D/'target_H1_step270_closed_source_sdk_cpu_review_v1.py').write_text(target,encoding='utf8')
 auth=read(R/'HUMAN_REWARD_CHANGE_AND_SOURCE_CPU_AUTH_ACTUAL.json');auth.update(original_reward_auth_historical_exact_path=str(R/'HUMAN_REWARD_CHANGE_AND_SOURCE_CPU_AUTH_ACTUAL.json'),ordinary_wheel_floor_boundary_repair_not_new_reward_recipe=True,arena_boundary_repair_CPU=repair,original_runtime_SHA=repair['old_runtime']['SHA'],new_runtime_SHA=repair['candidate_runtime']['SHA'],target_CPU_SHA=H(D/'target_H1_step270_closed_source_sdk_cpu_review_v1.py'),boundary_checker_SHA=H(D/'step270_boundary_installed_CPU_v1.py'))
 (D/'H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json').write_text(json.dumps(auth,indent=2),encoding='utf8')
 loader=(B/'closed_step270_reward_migration_owner_schema_source_CPU_v2.py').read_text('utf8');needle="assert reward['approved'] and reward['reward_CPU']['passed'] and reward['integration_CPU']['passed']";assert loader.count(needle)==1
 loader=loader.replace(needle,needle+"\n    assert reward['arena_boundary_repair_CPU']['passed'] and H(B/'step270_boundary_installed_CPU_v1.py')==reward['boundary_checker_SHA']")
 needle="assert cpu['new_reward_integration_CPU']['passed']";assert loader.count(needle)==1
 loader=loader.replace(needle,"assert cpu['boundary_repair_integration_CPU']['passed'] and cpu['boundary_repair_integration_CPU']['all_other_runtime_AST_exact']\n    "+needle)
 (D/'closed_production_continuation_CPU_v2.py').write_text(loader,encoding='utf8')
 # This new preparer uses qualified full20, separately binds failed21 closure/cost,
 # and always names failed21 as the just-exited owner. No failed21 model is promoted.
 p=F/'prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py';s=p.read_text('utf8')
 s=s.replace("P=T/'H1_STEP270_REWARD_RESOURCE_BRANCH_V21_20261022';E=", "P=T/'H1_STEP270_REWARD_H1_ONLY_V20_20261022';FAILED=T/'H1_STEP270_REWARD_RESOURCE_BRANCH_V21_20261022';E=")
 needle="assert proof['remaining_actual_snapshot']>82512.86069250107";assert s.count(needle)==1
 s=s.replace(needle,"failed=read(T/'H1_STEP270_REWARD_PATH_V1_20261022/reports/V110_FAILED21_ORIGINAL_COST_ALL_OUT_HEALTH_AND_RETENTION_CPU_ACTUAL.json')\n assert failed['passed_only_failed_closure_cost_allout_diagnostic_scope'] and not failed['qualified_FINAL'] and failed['all_owner_nodes_children_actual_out'] and failed['original_canonical_cost_settled']\n proof.update(remaining_actual_snapshot=failed['remaining_actual_snapshot'],qualified_fallback_after_actual_failed21=True,current_failed21_original_cost=failed['actual_cost'],current_failed21_cost_already_settled_not_refunded=True)\n "+needle)
 needle="rec.update(remaining_after=proof['remaining_actual_snapshot']";s=s.replace(needle,"rec.update(current_failed21_cost_settled=failed['actual_cost'],remaining_after=proof['remaining_actual_snapshot']")
 needle="shutil.copy2(reward_stage/'reports/HUMAN_REWARD_CHANGE_AND_SOURCE_CPU_AUTH_ACTUAL.json',dest/'H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json')";assert s.count(needle)==1
 s=s.replace(needle,"repair=N/'repair_sources'\n   for name in ('h1_step270_sdk_runtime_candidate.py','closed_production_continuation_CPU_v2.py','target_H1_step270_closed_source_sdk_cpu_review_v1.py','step270_boundary_installed_CPU_v1.py','H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json'):shutil.copy2(repair/name,dest/name)\n   shutil.copytree(repair/'boundary_reference_sources',dest/'boundary_reference_sources')")
 s=s.replace("read(P/'reports/H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['owner_root']","read(FAILED/'reports/H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['owner_root']")
 needle="both_latest_complete_model_CPU_original_cost_allout=True";s=s.replace(needle,"previous_failed_H1_root=read(FAILED/'reports/H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['roots']['h1'],qualified_complete20_fallback_after_actual_failed21=True,"+needle)
 s=s.replace("qualified_source_fallback_after_failed_pair7=False","qualified_source_fallback_after_failed21=True,ordinary_wheel_floor_boundary_repair=True,qualified_source_fallback_after_failed_pair7=False")
 p.write_text(s,encoding='utf8')
 # Probe only fresh resource components after independently verified failed closure.
 p=F/'read_E3_resource_only_after_actual_H1_closed_CPU_once.py';s=p.read_text('utf8');start=s.index(" proof=json.loads(");end=s.index(" q=json.loads(",start)
 s=s[:start]+" proof=json.loads((B/'reports/V110_FAILED21_ORIGINAL_COST_ALL_OUT_HEALTH_AND_RETENTION_CPU_ACTUAL.json').read_bytes());assert proof['passed_only_failed_closure_cost_allout_diagnostic_scope'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']\n"+s[end:];p.write_text(s,encoding='utf8')
 # Before any new root is installed, also recheck the actual failed H1 node root.
 p=F/'deploy_selected_H1_only_unused_once.py';s=p.read_text('utf8');needle="assert not B.exists();B.mkdir\"\"\")";assert s.count(needle)==1
 s=s.replace(needle,"failed=Path(v['previous_failed_h1']);assert json.loads((failed/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']\nassert not any(p.pid!=os.getpid() and any(x.startswith(str(failed)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))\n"+needle)
 s=s.replace("previous_owner=q['previous_owner_root']),timeout=120)","previous_owner=q['previous_owner_root'],previous_failed_h1=q['previous_failed_H1_root']),timeout=120)")
 p.write_text(s,encoding='utf8')
 files=[]
 for p in F.rglob('*.py'):ast.parse(p.read_text('utf8'));files.append(dict(path=str(p),SHA=H(p)))
 put('V110_BOUNDARY_REPAIR23_UNUSED_WORKFLOW_SOURCE_AST_ACTUAL.json',dict(epoch=time.time(),passed_AST=True,stage=str(F),files=files,qualified_H1_source='actual complete20 a4ae3f80ffb6a4204d369f6d473fe6f14ce215076ba09ca1b8b18525abc1490d/698920; failed21 explicitly rejected',no_remote_Task_or_GO_or_future_payload_prepared=True,new_runtime_SHA=repair['candidate_runtime']['SHA'],reward_module_unchanged=True,ordinary_physical_footprint_boundary_only=True,paired_branch_requires_additional_fresh_failed_root_install_binding_before_use=True))
 print(json.dumps(dict(stage=str(F),source_AST=True,no_remote_or_payload=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('V110_REPAIR_WORKFLOW_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
