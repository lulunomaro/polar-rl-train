from pathlib import Path
import ast,hashlib,json,shutil,time
T=Path(__file__).resolve().parent;N=T/'H1_STEP270_E3_PAIR_V10_20261022';R=T/'reports';p=N/'review_pair_complete_models_original_cost_CPU_once.py';old=p.read_text('utf8');oldSHA=hashlib.sha256(p.read_bytes()).hexdigest()
assert not (N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').exists()
history=N/'reserved_history';history.mkdir(exist_ok=True);saved=history/'review_pair_complete_models_original_cost_CPU_V1_UNUSED_NO_EPISODE_METADATA.py';assert not saved.exists();shutil.copy2(p,saved)
needle="        models[key]=dict(final=final,updates=updates,Adam=Adam,counts=counts,all17_changed=changed,actual_cost=cost,source_SHA=q['specs'][key]['source_SHA'])\n";assert old.count(needle)==1
extra="""        if key=='h1':
            state=s['H1_step270_task_state']['phase'];t=state['tensors'];g=state['goal']
            models[key]['H1_current_episode_snapshot']=dict(
                scope='Only per-environment currently retained episode state at FINAL; selected resets erase earlier events. Not whole-window totals, lifetime maximum, frozen evaluation, or graduation.',
                environments=state['num_envs'],takeoff_count_sum=int(t['takeoff_count'].sum()),
                landing_count_sum=int(t['landing_count'].sum()),recovery_count_sum=int(t['recovery_count'].sum()),
                goal_launched_envs=int(g['launched'].sum()),goal_landed_envs=int(g['landed'].sum()),
                goal_success_envs=int(g['success'].sum()),both_wheels_crossed_envs=int(t['crossed'].all(-1).sum()),
                max_retained_episode_both_wheel_bottom_peak_world_z_m=float(t['peak'].max()),
                retained_episode_peak_positive_envs=int((t['peak']>0).sum()),
                age_control_min=int(t['age_control'].min()),age_control_max=int(t['age_control'].max()),
                descriptive_only_no_new_admission_or_skill_threshold=True)
"""
s=old.replace(needle,needle+extra);assert s.replace(extra,'')==old;ast.parse(s);p.write_text(s,encoding='utf8')
v=dict(epoch=time.time(),only_unused_reader_descriptive_metadata=True,original_source=str(saved),original_SHA=oldSHA,new_source=str(p),new_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),all_existing_guards_and_source_AST_after_removing_append_exact=True,no_extra_checkpoint_load=True,no_actor_forward_optimizer_GPU_raw_download_hash_or_new_criterion=True,scope='Summarize the same already-loaded final H1 task per-episode tensors; resets mean these are not entire-window totals or skill evaluation')
with (R/'V101_UNUSED_CPU_READER_NON_GATING_EPISODE_METADATA_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(unused_reader_metadata_only=True,old_guards_exact=True,no_extra_PT_load=True)))
