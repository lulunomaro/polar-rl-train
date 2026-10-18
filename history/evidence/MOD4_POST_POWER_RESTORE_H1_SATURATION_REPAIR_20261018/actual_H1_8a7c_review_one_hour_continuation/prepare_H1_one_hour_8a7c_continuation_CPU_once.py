"""Requested hour blocks: save after3600s, reserve300s for close, remove24update cutoff."""
from pathlib import Path
import os,json,time,hashlib,shutil,ast,copy,importlib.util,sys,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
P=Path(__file__).resolve().parent;W=P.parent;N=P/'resumed_ce3_original_fp32_v1';B=P/'hour1_h1_8a7c_v1';Q=B/'payload/h1';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 with Path(p).open('x',encoding='utf8') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2))
def main():
 assert not B.exists();(B/'reports').mkdir(parents=True);torch.set_num_threads(2);rng=torch.get_rng_state().clone();closed=json.loads((N/'reports/CE3_ORIGINAL_FP32_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json').read_bytes());assert closed['passed_whole_final_model_local_CPU'] and closed['updates']==24 and closed['all17Adam_after']==646580 and closed['actual_original_owner_node_all_children_out']
 oldQ=N/'payload/h1';oldm=json.loads((oldQ/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());shutil.copytree(oldQ,Q,ignore=shutil.ignore_patterns('__pycache__','THREE_SLOT_COMPLETE_MANIFEST_V1.json','*.pt'))
 source=Q/'job0/source/H1_8a7c_closed24.pt';source.parent.mkdir(exist_ok=True);shutil.copy2(closed['complete_final']['local_path'],source);assert H(source)==closed['complete_final']['SHA']
 worker=(oldQ/'h1_prelaunch_v2_production_worker_v1.py').read_text(encoding='utf8').replace('H1_ce3_public4_closed24.pt','H1_8a7c_closed24.pt').replace('646100','646580').replace("go['max_parent_seconds']==1800","go['max_parent_seconds']==3900").replace('max_completed_updates=24','max_completed_updates=None')
 (Q/'h1_prelaunch_v2_production_worker_v1.py').write_text(worker,encoding='utf8')
 native=(P/'proposal_ce3_same_candidate_finite_v1/payload/h1/h1_ground_prelaunch_v2_native_worker_v1.py').read_text(encoding='utf8').replace('H1_ce3_public4_closed24.pt','H1_8a7c_closed24.pt').replace('646100','646580');(Q/'h1_ground_prelaunch_v2_native_worker_v1.py').write_text(native,encoding='utf8')
 reader=(P/'proposal_ce3_same_candidate_finite_v1/review_ce3_native_original_FP32_reference_allrows_CPU_once.py').read_text(encoding='utf8').replace('H1_ce3_public4_closed24.pt','H1_8a7c_closed24.pt').replace('646100','646580').replace('H1_CE3_ORIGINAL_FP32_NATIVE180_ALL_ROWS_CPU_ACTUAL.json','H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json')
 (Q/'review_H1_prelaunch_v2_native_allrows_CPU_v1.py').write_text(reader,encoding='utf8')
 # Native-stage controller is the original spawn-native chain, not the prior ce3 reuse selector.
 shutil.copy2(P/'proposal_ce3_same_candidate_finite_v1/payload/h1/three_slot_finite_node_v1.py',Q/'three_slot_finite_node_v1.py')
 common=(oldQ/'three_slot_common_v1.py').read_text(encoding='utf8');assert "CAPS={'h1':1800" in common;common=common.replace("CAPS={'h1':1800","CAPS={'h1':3900");(Q/'three_slot_common_v1.py').write_text(common,encoding='utf8')
 storage=(oldQ/'own_H1_storage_finite_guard_v1.py').read_text(encoding='utf8');assert 'H1_MAX_COMPLETE_UPDATES=24' in storage and 'completed>=H1_MAX_COMPLETE_UPDATES or ' in storage;storage=storage.replace('H1_MAX_COMPLETE_UPDATES=24','H1_MAX_COMPLETE_UPDATES=None').replace('completed>=H1_MAX_COMPLETE_UPDATES or ','');(Q/'own_H1_storage_finite_guard_v1.py').write_text(storage,encoding='utf8')
 task=json.loads((Q/'job0/TASK.json').read_bytes());write(Q/'job0/PREVIOUS_30MIN_CE3_TASK_HISTORY.json',task)
 task.update(id='H1_8A7C_ONE_HOUR_TIMED_CONTINUATION_20261018',source_SHA=closed['complete_final']['SHA'],source_filename=source.name,source_Adamstep=646580,source_H1_actual_latest_Adamstep=646580,source_owned_completed_updates=24,source_owned_updates=24,max_parent_seconds=3900,exit_headroom_seconds=300,training_block_seconds_before_save=3600,max_completed_updates=None,one_hour_then_behavior_audit=True,no_24update_early_stop=True,same_source_backend_native_reused_not_replayed=False,own_new_native_for_actual_new_weights_required=True,new_target_native180_and_full_CPU_required=True,source_H1_actual_latest_completed_updates=24,reference_protocol='original_formal_20k_native_FP32_same_absolute1e-4; separate frozen80 audits use existing V3 FP64 references')
 (Q/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
 mf=dict(oldm,source_SHA=task['source_SHA'],source_filename=source.name,source_Adamstep=646580,source_schema_counts=[199,105]);mf.pop('H1_same_source_backend_native_reuse',None)
 mf['files']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
 for p in Q.rglob('*.py'):ast.parse(p.read_text(encoding='utf8'))
 write(Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',mf)
 spec=copy.deepcopy(json.loads((N/'reports/CE3_ORIGINAL_FP32_NATIVE_REUSE_PAYLOAD_CPU_ACTUAL.json').read_bytes())['specs']);spec['h1'].update(source_SHA=task['source_SHA'],source_filename=source.name,source_Adamstep=646580,manifest_SHA=H(Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),max_parent_seconds=3900,exit_headroom_seconds=300,previous_runtime_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1cr_1810p3',execution_backend='target72')
 ns={};exec(compile(storage,'own_H1_storage_finite_guard_v1.py','exec'),ns)
 for completed in (0,1,23,24,25,100,10000):assert not ns['should_save_stop']('production',completed,9*1024**3)
 assert ns['should_save_stop']('production',1,8*1024**3-1) and not ns['should_save_stop']('production',1,8*1024**3)
 rejected=[]
 for vals in [('unknown',1,9*1024**3),('production',-1,9*1024**3),('production',1,float('nan')),('production',1,-1)]:
  try:ns['should_save_stop'](*vals)
  except ValueError:rejected.append(vals[0]+':'+str(vals[1]))
  else:raise AssertionError(vals)
 assert len(rejected)==4 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 write(B/'reports/H1_ONE_HOUR_SOURCE_TIMING_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),actual_human_request='每次训练时长增长到一个小时后再审计，半个小时我觉得很难出什么有效成果',passed_CPU_only=True,specs=spec,source=closed['complete_final'],source_Adam646580=True,training_block_GO_to_save_seconds=3600,total_cap_including_exit_reserve_seconds=3900,exit_headroom_seconds=300,arbitrary24_update_stop_removed=True,complete_update_storage8GiB_and_start25GiB_guards_unchanged=True,old_24_and_25_100_10000_updates_no_early_stop_tested=True,invalid_storage_states_rejected=rejected,original_PPO_LR_STD_reward_command_DR_physics_hardware_unchanged=True,only_block_duration_and_update_cutoff_changed=True,own20k_native180_and_original_CPU_before_production=True,behavior_frozen_evaluation_only_after_whole_hour_saved_stop=True,no_increased_canonical_total_budget=True,actual_target_dispatch_not_yet=True,CPU_RNG_unchanged0CUDA0optimizer=True,lookup_misses_retained=['storage guard not under job0/runtime/isaac/mod4 or lib; actual root module found with rg --files']))
 print(json.dumps(dict(hour_block_CPU_ready=True,save_after_GO_seconds=3600,total_lifecycle_cap=3900,old24_update_limit_removed=True,source_Adam=646580)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (P/'reports'/('ONE_HOUR_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_budget_action=True),f,indent=2)
  raise
