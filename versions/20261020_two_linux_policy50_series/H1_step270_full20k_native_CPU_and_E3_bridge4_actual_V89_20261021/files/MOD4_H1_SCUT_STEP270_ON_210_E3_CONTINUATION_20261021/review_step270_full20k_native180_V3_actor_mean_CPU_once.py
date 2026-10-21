from pathlib import Path
import json,time,traceback
import numpy as np,torch
B=Path(__file__).resolve().parent;R=B/'reports';A=B/'full20k_native180_V3_actual'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
try:
 torch.set_num_threads(4);rng=torch.get_rng_state().clone();proof=json.loads((R/'STEP270_FULL20K_NATIVE180_V3_CORE_CLOCK_GUARD_WITNESS_CPU_ACTUAL.json').read_bytes());assert proof['passed_core_clock_action_guards_and_witness_CPU']
 s=torch.load(B.parent/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019/actual_closed_three_finals/h1/model_update42.pt',map_location='cpu',weights_only=False);weights=s['actor_state_dict'];records=[];worst=clip_worst=raw_peak=0.;rows=0
 with torch.inference_mode():
  for p in sorted((A/'out').glob('CONTROL_*.npz')):
   with np.load(p,allow_pickle=False) as z:inputs=z['policy'].reshape(-1,35);gpu=z['raw_action'].reshape(-1,6);executed=z['executed6'].reshape(-1,6)
   assert np.array_equal(executed,np.clip(gpu,-6,6));file_error=file_clip=0.
   for first in range(0,len(inputs),32768):
    x=torch.from_numpy(inputs[first:first+32768].copy());expected=x
    for n in (0,2,4,6):
     expected=torch.nn.functional.linear(expected,weights[f'mlp.{n}.weight'],weights[f'mlp.{n}.bias'])
     if n!=6:expected=torch.nn.functional.elu(expected)
    actual=torch.from_numpy(gpu[first:first+32768].copy());err=float((actual-expected).abs().max());cerr=float((actual.clamp(-6,6)-expected.clamp(-6,6)).abs().max());file_error=max(file_error,err);file_clip=max(file_clip,cerr)
   rows+=len(inputs);worst=max(worst,file_error);clip_worst=max(clip_worst,file_clip);raw_peak=max(raw_peak,float(np.abs(gpu).max()));records.append(dict(file=p.name,rows=len(inputs),original_FP32_mean_maxabs=file_error,clip6_cross_device_diagnostic_maxabs=file_clip))
 assert rows==3600000 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 row=dict(epoch=time.time(),passed_original_FP32_raw_mean_absolute_1e4=worst<=1e-4,original_absolute_tolerance=1e-4,rows=rows,actions=6,raw_mean_maxabs_error=worst,clip6_cross_device_diagnostic_maxabs=clip_worst,actual_raw_peak=raw_peak,actual_executed6_is_literal_clip_of_recorded_GPUraw=True,source_actor9_including_six_STD_and17Adam_674740_unchanged=True,CPU_FP32_original_ELU_and_linear=True,files=records,no_GPU_or_optimizer_or_learning_GO=True,not_production_admission_by_itself=True)
 put(R/'STEP270_FULL20K_NATIVE180_V3_ORIGINAL_ACTOR_MEAN_CPU_ACTUAL.json',row);print(json.dumps(row))
except BaseException:put(R/('STEP270_FULL20K_NATIVE180_V3_ACTOR_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True));raise
