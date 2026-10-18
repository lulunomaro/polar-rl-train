"""Read only the complete saved model and source; counters are current-episode snapshots."""
from pathlib import Path
import os,json,time,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;W=B.parent;C=W/'MOD4_SCUT_FUDAN_THIRD_HOUR_20261019';R=B/'reports';torch.set_num_threads(2)
proof=json.loads((C/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed_all_three_whole_final_models_CPU'];row=proof['experts']['h1']['final'];s=torch.load(row['local_path'],map_location='cpu',weights_only=False);wrapper=s['H1_public_request_phase_state'];state=wrapper['phase'];t=state['tensors'];assert state['num_envs']==20000
def summary(a):
 if isinstance(a,dict):return {k:summary(v) for k,v in a.items()}
 assert torch.is_tensor(a) and torch.isfinite(a).all()
 return dict(shape=list(a.shape),dtype=str(a.dtype),nonzero=int(torch.count_nonzero(a)),min=float(a.min()),max=float(a.max()),mean=float(a.double().mean()))
snap={k:summary(v) for k,v in t.items()};age=t['age_control'];masks={'before_request':age<100,'request_window':(age>=100)&(age<180),'after_request':age>=180};cross={k:dict(environments=int(mask.sum()),attempt=int((mask&t['attempt']).sum()),ready=int((mask&t['ready']).sum()),launched=int((mask&t['launched']).sum()),landed=int((mask&t['landed']).sum()),recovered=int((mask&t['recovered']).sum())) for k,mask in masks.items()}
local=json.loads((W/'MOD4_LOCAL_MUJOCO_DRIVE_20261008/runtime_config.json').read_bytes());pd=s['chassis_PD_recipe'];assert pd['leg_kp_nominal']==local['leg_kp'] and pd['leg_kd_nominal']==local['leg_kd'] and pd['wheel_kd_nominal']==local['wheel_kd']
pdstate=s['chassis_PD_state'];command=wrapper['external_command'];assert torch.equal(command['vel_command_b'],torch.zeros_like(command['vel_command_b']))
source=C/'payload/h1/job0/runtime/isaac/mod4/mod4_task.py';text=source.read_text('utf8');assert '_f("RM_NOMINAL_HEIGHT", .25)' in text and '_f("RM_HEIGHT_MIN", 0.18)' in text and '_f("RM_HEIGHT_MAX", 0.34)' in text
out=dict(epoch=time.time(),source=row,current_episode_phase_tensor_summary=snap,current_episode_schedule_cross_tab=cross,current_counts_not_cumulative_training_or_frozen_success=True,episode_resets_clear_counts=True,phase_profile=state['profile'],zero_twist_command_snapshot_exact=True,saved_training_PD_recipe=pd,local_runtime_config=local,nominal_PD_kp_kd_wheelkd_equal=True,training_PD_factors=summary(pdstate['PD']['factor']),training_COM_delta_m=summary(pdstate['COM']['delta_m']),height_source=dict(path=str(source),SHA=hashlib.sha256(source.read_bytes()).hexdigest(),nominal=.25,configured_range=[.18,.34],local_command=.25,per_environment_saved_height_commands_not_in_this_phase_wrapper=True,not_an_actual_loaded_height_readback=True),limitations=['Saved phase values cover only each current episode; resets erase earlier events. They cannot measure training jump success or compare frozen80env scores.','Local deterministic nominal PD/reset and MuJoCo .5ms differ from saved20k randomized PhysX runtime; equal nominal gains do not prove backend equivalence.','No actor input, reward, STD, LR, CAD, physics, success threshold or live player was changed.'],CPU_only_no_CUDA_optimizer_GPU_or_canonical_write=True)
with (R/'THIRD_CLOSED_H1_PHASE_AND_LOCAL_ADAPTER_SOURCE_CPU_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(dict(current_episode_cross_tab=cross,nominal_PD_match=True,PD_factor_groups=summary(pdstate['PD']['factor']),not_skill_success=True),indent=2))
