"""Only completed new1ms SDK evidence; no simulation or budget writes."""
from pathlib import Path
import json,sys,hashlib,time,collections
D=Path(__file__).resolve().parent;R=D/'reports';OLD=D.parent/'MOD4_DT2500_LONGRUN_INTEGRITY_REVIEW_20261008/reports/windows'
read=lambda p:json.loads(p.read_text(encoding='utf8'));assert not (R/'D3_1MS_ACTUAL_SDK_REVIEW.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval();returned=[];cases={}
try:
 with c.open_sftp() as sf:
  for label in ('00-off','01-on'):
   job='clk1000-recovery-d3-sdk-'+label;folder=OLD/job
   for name in ('probe.json','result.json','manifest.json'):
    raw=(folder/name).read_bytes();actual=sf.open('D:/MOD4_async_eval/sensor_recovery_clock1000_v15/jobs/'+job+'/'+name).read();assert raw==actual
    returned.append(dict(job=job,file=name,sha256=hashlib.sha256(raw).hexdigest(),returned_bytes_exact=True))
   p=read(folder/'probe.json');r=read(folder/'result.json');m=read(folder/'manifest.json')
   assert r['exit_code']==0 and not r['errors'] and p['resets']==0 and not p['nonfinite'] and p['steps']==300
   assert p['actual_physics_dt_s']==.001 and p['actual_decimation']==10 and p['actual_physics_callbacks']==p['expected_physics_callbacks']==3000
   assert p['max_closure_after_grace_m']<=.002 and p['max_mimic_after_grace_rad']<=.01 and p['mild_initial_parameters']['actual_parameters_pass'] and p['mild_final_parameters']['actual_parameters_pass']
   assert p['feedback_delay_selected_reset']['other_rows_exact'] and p['SDK_fixed_clean_action_input']
   assert p['sensor_actual_manager_audit']['critic38_clean'] and p['sensor_actual_manager_audit']['command_lastaction_mode_wheel_slots_exact']
   cases[label]=dict(probe=p,result=r,manifest=m)
finally:c.close()
b,n=cases['00-off']['probe'],cases['01-on']['probe']
pair={k:b[k]==n[k] for k in ('reset_root_before_physics','reset_joint_pos_before_physics','mild_initial_parameters','mild_final_parameters','final_root_state','final_joint_pos')};assert all(pair.values())
assert n['feedback_delay_CUDA_disk_roundtrip']['all_queue_and_RNG_exact'] and n['feedback_delay_CUDA_disk_roundtrip']['actor_same_tick_exact']
rows=n['sensor_platform_sdk']['rows'];assert len(rows)==300
counts={}
for key in n['feedback_delay_recipe']['actor_feedback_channels']:
 ages=[age for row in rows for age in row['actual_feedback_sample_apply'][key]['actual_age_us']];assert len(ages)==3000 and set(ages)<={0,10000}
 counts[key]=dict(collections.Counter(ages))
error=max(row['formula_max_error'] for row in rows)
out=dict(epoch=time.time(),passed=True,scope='1ms/16-4/3060 actual actor manager0/10ms queue + CUDA disk roundtrip; fixed clean-policy action SDK only, not D3 skill or PPO',source_sha256=cases['01-on']['result']['checkpoint']['sha256'],returned_files=returned,pairing_exact=pair,age_counts_by_channel=counts,callback_count_each=3000,manager_formula_max_error=error,selected_reset=n['feedback_delay_selected_reset'],CUDA_queue_roundtrip=n['feedback_delay_CUDA_disk_roundtrip'],closure_mm_each={label:case['probe']['max_closure_after_grace_m']*1000 for label,case in cases.items()},mimic_rad_each={label:case['probe']['max_mimic_after_grace_rad'] for label,case in cases.items()},cost=dict(process_wall_seconds=sum(x['result']['physics_process_wall_seconds'] for x in cases.values()),sampled_peak_MiB=max(x['result']['observed_GPU_memory_mib'] for x in cases.values()),continuous_peak_claimed=False),recipe=n['feedback_delay_recipe'],SDK_does_not_certify_closed_loop_skills=True)
(R/'D3_1MS_ACTUAL_SDK_REVIEW.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
