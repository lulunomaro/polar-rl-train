"""Continue original H1 hourly cadence from the actual complete71 model, with no parameter reset."""
from pathlib import Path
import os,json,time,hashlib,shutil,ast,copy,sys,traceback
os.environ['CUDA_VISIBLE_DEVICES']='';import torch
B=Path(__file__).resolve().parent;W=B.parent;P=W/'MOD4_POST_POWER_RESTORE_H1_SATURATION_REPAIR_20261018';OLD=P/'hour1_h1_8a7c_v1';N=P/'hour2_h1_fe778_v1';Q=N/'payload/h1';R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 proof=json.loads((OLD/'reports/H1_ONE_HOUR_8A7C_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json').read_bytes());assert proof['passed_whole_final_model_local_CPU'] and proof['actual_duration_bound_passed'] and proof['actual_original_owner_node_all_children_out'] and proof['original_canonicalNone_two_real_fcntlFree_and_target_GPU_private_shared_free'];assert proof['updates']==71 and proof['all17Adam_after']==648000
 assert not N.exists();(N/'reports').mkdir(parents=True);rng=torch.get_rng_state().clone();oldQ=OLD/'payload/h1';oldm=json.loads((oldQ/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());shutil.copytree(oldQ,Q,ignore=shutil.ignore_patterns('__pycache__','THREE_SLOT_COMPLETE_MANIFEST_V1.json','*.pt'));source=Q/'job0/source/H1_fe778_closed71.pt';shutil.copy2(proof['complete_final']['local_path'],source);assert H(source)==proof['complete_final']['SHA']
 for name in ('h1_ground_prelaunch_v2_native_worker_v1.py','h1_prelaunch_v2_production_worker_v1.py','review_H1_prelaunch_v2_native_allrows_CPU_v1.py'):
  p=Q/name;s=p.read_text('utf8').replace('H1_8a7c_closed24.pt','H1_fe778_closed71.pt').replace('646580','648000');p.write_text(s,encoding='utf8')
 task=json.loads((Q/'job0/TASK.json').read_bytes());(Q/'job0/PREVIOUS_HOUR1_TASK_HISTORY.json').write_text(json.dumps(task,indent=2));task.update(id='H1_FE778_ACTUAL_CLOSED71_NEXT_ONE_HOUR_20261018',source_SHA=proof['complete_final']['SHA'],source_filename=source.name,source_Adamstep=648000,source_H1_actual_latest_Adamstep=648000,source_owned_completed_updates=71,source_owned_updates=71,source_H1_actual_latest_completed_updates=71,max_parent_seconds=3900,exit_headroom_seconds=300,training_block_seconds_before_save=3600,max_completed_updates=None,previous_one_hour_actual_cost=proof['actual_cost_seconds'],own_new_source_native_required=True);(Q/'job0/TASK.json').write_text(json.dumps(task,indent=2))
 from importlib.util import spec_from_file_location,module_from_spec
 sp=spec_from_file_location('next_hour_same_storage_guard',Q/'own_H1_storage_finite_guard_v1.py');m=module_from_spec(sp);sp.loader.exec_module(m);assert m.H1_MAX_COMPLETE_UPDATES is None and all(not m.should_save_stop('production',i,9*1024**3) for i in (24,25,71,1000)) and m.should_save_stop('production',72,8*1024**3-1)
 for p in Q.rglob('*.py'):ast.parse(p.read_text('utf8'))
 manifest=dict(oldm,source_SHA=task['source_SHA'],source_filename=source.name,source_Adamstep=648000,source_schema_counts=[199,105]);manifest['files']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts];mp=Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';mp.write_text(json.dumps(manifest,indent=2));prep=json.loads((OLD/'reports/H1_ONE_HOUR_SOURCE_TIMING_CPU_PREPARED_ACTUAL.json').read_bytes());specs=copy.deepcopy(prep['specs']);specs['h1'].update(source_SHA=task['source_SHA'],source_filename=source.name,source_Adamstep=648000,manifest_SHA=H(mp),previous_runtime_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1h1_1810p4')
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 report=dict(prep,epoch=time.time(),specs=specs,source=proof['complete_final'],source_Adam648000=True,source_actual_closed71=True,source_Adam646580=False,original_whole_model_CPU_cost_and_real_handoff_proof=str(OLD/'reports/H1_ONE_HOUR_8A7C_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json'),not_extending_old_hour_or_increasing_total_budget=True,actual_target_dispatch_not_yet=True)
 with (N/'reports/H1_ONE_HOUR_SOURCE_TIMING_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 with (R/'H1_NEXT_HOUR_FE778_CLOSED71_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),payload=str(Q),source_SHA=task['source_SHA'],source_Adam648000=True,source_owned71=True,save_after_true_GO3600_cap3900_exit300=True,no24_cutoff=True,all_PPO_reward_STD_LR_DR_physics_and_original_budget_unchanged=True,no_target_dispatch_yet=True),f,indent=2)
 print(json.dumps(dict(next_H1_hour_CPU_ready=True,source_SHA=task['source_SHA'],source_Adam=648000,source_updates=71,no_GPU_yet=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('NEXT_H1_HOUR_CPU_PREPARE_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_budget_change=True),f,indent=2)
  raise
