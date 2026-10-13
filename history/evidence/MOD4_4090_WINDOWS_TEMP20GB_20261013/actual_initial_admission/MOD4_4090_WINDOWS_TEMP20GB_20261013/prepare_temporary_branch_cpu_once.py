"""New authorized <=20GB Windows branch. Build only; no GPU/network/import SDK."""
from pathlib import Path
import ast,json,hashlib,shutil,time,zipfile,sys
W=Path(__file__).resolve().parent.parent
D=Path(__file__).resolve().parent
B=W/'MOD4_4090_WINDOWS_REPAIR_20261013/repair_payload/v6a_audited_cpu_payload'
Q=D/'payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
N=2048
def emit(name,s):
 p=Q/name;assert not p.exists();p.write_text(s,encoding='utf8')
 if p.suffix=='.py':compile(s,str(p),'exec')
def facade(name):
 t=ast.parse((B/name).read_text(encoding='utf8'));t.body=[x for x in t.body if not (isinstance(x,ast.Expr) and isinstance(x.value,ast.Call) and isinstance(x.value.func,ast.Name) and x.value.func.id=='run_closed') and not isinstance(x,ast.If)]
 ns={};sys.path.insert(0,str(B));exec(compile(t,str(B/name),'exec'),ns);return ns['transform']
class Small(ast.NodeTransformer):
 def visit_Constant(self,n):
  if type(n.value) is int and n.value==20000:return ast.copy_location(ast.Constant(N),n)
  if isinstance(n.value,str):
   swaps={'WINDOWS4090_FULL20K_BACKEND_BINDING':'WINDOWS4090_TEMPORARY_BACKEND_BINDING','windows4090_training_runtime_audited_v6':'temporary_training_runtime','windows4090_training_runtime':'temporary_training_runtime','windows4090_probe_contract_audited_v6':'temporary_probe_contract','windows4090_probe_contract':'temporary_probe_contract','windows20k_fullstate_binding':'temporary_state_binding'}
   if n.value in swaps:n.value=swaps[n.value]
   n.value=n.value.replace('actual_API_offset_all20000_exact','actual_API_offset_all_selected_exact').replace('actual_full20k_origin_entry_assignment_exact','actual_selected_origin_entry_assignment_exact')
  return n
 def visit_ImportFrom(self,n):
  replacements={'windows4090_training_runtime_audited_v6':'temporary_training_runtime','windows4090_training_runtime':'temporary_training_runtime','windows20k_fullstate_binding':'temporary_state_binding','windows4090_probe_contract_audited_v6':'temporary_probe_contract','windows4090_probe_contract':'temporary_probe_contract'}
  n.module=replacements.get(n.module,n.module);return n
def rendered(t):return ast.unparse(ast.fix_missing_locations(Small().visit(t)))+'\n'
def main():
 assert not Q.exists();Q.mkdir(parents=True);(D/'reports').mkdir(exist_ok=True)
 emit('original_full20k_binding.py',(B/'windows20k_fullstate_binding.py').read_text(encoding='utf8'))
 # Selection/reset module reuses the proven deterministic algorithm, with a new
 # donor binding and explicit per-state metadata allowlist below.
 local=ast.parse((W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/local_state_projection.py').read_text(encoding='utf8'))
 functions=[x for x in local.body if isinstance(x,ast.FunctionDef) and x.name in ('select','project_tree','bind_selected_entry','selected_entry')]
 emit('selected_source_projection.py',"from pathlib import Path\nimport torch,numpy as np,copy,json,hashlib\nSOURCE={'sha256':'d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'}\n"+ast.unparse(ast.Module(body=functions,type_ignores=[]))+'\n')
 runtime=facade('windows4090_training_runtime_audited_v6.py')(ast.parse((B/'windows4090_training_runtime.py').read_text(encoding='utf8')))
 # Original initializer remains one-time after complete selected-state restore.
 emit('temporary_training_runtime.py',rendered(runtime))
 probe=ast.parse((B/'windows4090_probe_contract.py').read_text(encoding='utf8'))
 emit('temporary_probe_contract_base.py',rendered(probe))
 facade_text=(B/'windows4090_probe_contract_audited_v6.py').read_text(encoding='utf8').replace('from windows4090_probe_contract import','from temporary_probe_contract_base import')
 emit('temporary_probe_contract.py',facade_text)
 observer=(B/'windows4090_substep_readback_v6.py').read_text(encoding='utf8').replace('self.N in (10,20000)','self.N in (10,2048)')
 emit('windows4090_substep_readback_v6.py',observer)
 repair=(B/'left_head_offset_aware_migration_v3.py').read_text(encoding='utf8').replace('from windows20k_fullstate_binding import','from temporary_state_binding import').replace('expected_num_envs=20000','expected_num_envs=2048').replace('expected_num_envs==20000','expected_num_envs==2048')
 emit('left_head_offset_aware_migration_v3.py',repair)
 worker=facade('windows4090_repair_worker_audited_v6.py')(ast.parse((B/'windows4090_repair_worker.py').read_text(encoding='utf8')))
 s=rendered(worker)
 s=s.replace("cfg = task.Mod4EnvCfg()", "cfg = task.Mod4EnvCfg()")
 anchor="capacities = {k: getattr(cfg.sim.physx, k) for k in capacity_names}"
 assert s.count(anchor)==1
 s=s.replace(anchor,"original_capacities = {k: getattr(cfg.sim.physx, k) for k in capacity_names}\n    for k,v in manifest['temporary_small_batch_capacities'].items():\n        setattr(cfg.sim.physx,k,v)\n    "+anchor)
 # Preserve all dynamics/thresholds; only bounded capacity allocations change.
 s=s.replace('capacity_overrides_applied=False','capacity_overrides_applied=True').replace('small128_caps_not_used=True','temporary2048_capacity_disclosed=True').replace('original20k_task_constructor_no_capacity_overrides_retained=True','original_defaults_retained_in_report=True')
 anchor="env.reset()\n    placement = None"
 assert s.count(anchor)==1
 s=s.replace(anchor,"env.reset()\n    if args.mode != 'sdk':\n        from temporary_state_binding import initialize_selected_env\n        initialize_selected_env(env,args)\n    placement = None")
 emit('temporary_worker.py',s)
 for name in ('windows4090_demand_task_wrapper_audited_v6.ps1','register_windows4090_demand_task_audited_v6_once.ps1'):
  s=(B/name).read_text(encoding='utf8').replace('run_windows4090_stage_audited_v6_once.py','temporary_parent.py')
  emit(name,s)
 rows=[dict(archive=p.name,sha256=H(p),bytes=p.stat().st_size) for p in Q.iterdir() if p.is_file()]
 report=dict(epoch=time.time(),prepared_only=True,source_num_envs=20000,temporary_num_envs=N,requested_memory_bytes=20000000000,soft_save_stop_RSS_bytes=18000000000,hard_job_private_commit_bytes=20000000000,full20k_scope_not_modified=True,geometry_solver_clock_reward_DR_thresholds_unchanged=True,files=rows,CPU_target_and_GPU_pending=True)
 (D/'reports/TEMP20GB_SOURCE_BUILD_CPU_PREPARED.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(dict(prepared=True,files=len(rows),GPU=False)))
if __name__=='__main__':main()
