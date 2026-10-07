"""Review completed actual manager SDK, never call it a learned delay expert."""
from pathlib import Path
import sys,json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';OLD=D.parent/'MOD4_E0_DT2500_ENV20K_CONTINUATION_20261007'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
assert not (R/'D3_ACTUAL_MANAGER_SDK_REVIEW.json').exists()
published=read(R/'D3_SDK_IMMUTABLE_PUBLISHED.json');cpu=read(R/'ADAPTER_CPU_PASSED.json')
snapshot=read(OLD/'reports/CLOCK2500_EVALUATOR_CURRENT_ACTUAL.json');jobs={j['id']:j for j in snapshot['jobs']}
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
transport=[];cases={};c=connect_eval()
try:
 with c.open_sftp() as ftp:
  for label in ('00-off','01-on'):
   job='clk2500-solver32-70-d3-sdk-'+label;folder=OLD/'reports/windows'/job
   raw,res,m=read(folder/'probe.json'),read(folder/'result.json'),read(folder/'manifest.json')
   assert jobs[job]['complete'] and jobs[job]['probe']==raw and jobs[job]['result']==res
   assert res['exit_code']==0 and not res['errors'] and not res['new_learning'] and res['num_envs']==10 and res['steps']==300
   assert res['checkpoint']['sha256']==published['source']['sha256']
   assert raw['physics_pass'] and not raw['nonfinite'] and raw['resets']==0
   assert raw['max_closure_after_grace_m']<.002 and raw['max_mimic_after_grace_rad']<.01
   assert raw['SDK_fixed_clean_action_input'] and raw['frozen_architecture_audit']['optimizer_updates']==0
   assert raw['clock2500_actual_solver']['enabled_closed_loops']==60 and raw['clock2500_actual_solver']['all_position32_velocity4']
   assert raw['feedback_delay_selected_reset']['other_rows_exact']
   rows=raw['sensor_platform_sdk']['rows'];assert len(rows)==300 and [r['tick'] for r in rows]==list(range(1,301))
   assert all(r['actor35'] and r['critic38_clean'] and r['command_lastaction_mode_wheel_slots_exact'] and r['same_tick_draws_unchanged'] and r['formula_max_error']<=2e-6 for r in rows)
   for name in ('probe.json','result.json','manifest.json'):
    data=(folder/name).read_bytes();returned=ftp.open('D:/MOD4_async_eval/sensor_clock2500_solver32_v15/jobs/'+job+'/'+name).read();assert data==returned
    transport.append(dict(job=job,file=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),returned_bytes_exact=True))
   cases[label]=dict(raw=raw,result=res,manifest=m)
finally:c.close()
off,on=cases['00-off']['raw'],cases['01-on']['raw'];channels=['base_ang_vel','projected_gravity','leg_pos','leg_vel','wheel_vel'];ages={k:{'0us':0,'10000us':0,'warmup0us':0} for k in channels}
for row in on['sensor_platform_sdk']['rows']:
 assert set(row['actual_feedback_sample_apply'])==set(channels)
 for key,q in row['actual_feedback_sample_apply'].items():
  assert q['apply_tick']==row['tick'] and q['control_period_us']==10000
  for requested,sampled,age,ready in zip(q['requested_delay_us'],q['actual_sample_tick'],q['actual_age_us'],q['warmup_valid']):
   assert requested in (0,10000) and age in (0,10000) and (q['apply_tick']-sampled)*10000==age
   assert age==requested if ready else age==0
   ages[key]['0us' if age==0 else '10000us']+=1
   ages[key]['warmup0us']+=int(not ready and age==0)
assert all(counts['10000us']>0 and counts['0us']>0 and counts['warmup0us']==3 for counts in ages.values())
pair={key:off[key]==on[key] for key in ('reset_root_before_physics','reset_joint_pos_before_physics','mild_initial_parameters','mild_final_parameters','final_root_state','final_joint_pos')}
assert all(pair.values())
report=dict(epoch=time.time(),candidate_root='/home/egde/rl_candidates/MOD4_D3_ACTOR_DELAY_SDK_PREPARE_20261008',source_count=221,
            CPU=cpu,source=published['source'],SDK_actual_manager_pass=True,SDK_scope='3060 actual manager only:10env300control3s each off/on, fixed clean actor action input',
            actual_age_counts_by_channel=ages,selected_reset_ids=[1,4,7],selected_reset_other_rows_exact=True,
            noise_bias_then_queue_before_original_scale=True,clean38critic=True,actor35=True,commands_lastaction_height_mode_wheel_positions_exact=True,
            sample_BODY_components_not_rotated_into_apply_frame=True,no_50Hz_or_action_delay_claim=True,
            on_off_fixed_clean_action_plant_exact=pair,
            max_manager_formula_error=max(r['formula_max_error'] for v in cases.values() for r in v['raw']['sensor_platform_sdk']['rows']),
            physics_max_closure_mm={k:v['raw']['max_closure_after_grace_m']*1000 for k,v in cases.items()},
            physics_max_mimic_rad={k:v['raw']['max_mimic_after_grace_rad'] for k,v in cases.items()},returned_files=transport,
            cost=dict(process_wall_seconds=sum(v['result']['physics_process_wall_seconds'] for v in cases.values()),transfer_seconds=sum(v['result']['transfer_seconds'] for v in cases.values()),sampled_peak_MiB=max(v['result']['observed_GPU_memory_mib'] for v in cases.values()),continuous_peak_claimed=False),
            missing_evidence=['No native4090 D3 fullscale callback/20k readback yet','No D3 fulloptimizer/RNG/new-episode resume contract yet','No D3 full PPO preflight or learned skill regression yet'],
            SDK_does_not_prove_D3_learning_or_closed_loop_delay_robustness=True,callback_count_not_recorded_in_this_probe_no_1200_claim=True,
            production_training_unchanged=True,no_new_PPO_or_canonical_write=True)
(R/'D3_ACTUAL_MANAGER_SDK_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:report[k] for k in ('SDK_actual_manager_pass','actual_age_counts_by_channel','on_off_fixed_clean_action_plant_exact','max_manager_formula_error','physics_max_closure_mm','cost','missing_evidence')}))
