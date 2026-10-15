"""Every actual saved decision, source9/STD, last executed action and reset."""
from pathlib import Path
import argparse,hashlib,json,os,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,torch
from torch.nn import functional as F
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);a=p.parse_args();assert a.case in tuple(f's5_single_W35_{k}_{n}_v1' for k in ('flat','spin','world') for n in (120,1500))
 j=json.loads(sorted(R.glob(a.case+'_CURRENT_ACTUAL_*.json'))[-1].read_bytes());assert j['shared_OS_lock_free'] and all(not x['actual_alive'] for x in j['actual_PID_identities'])
 files=j['collected_files']
 def path(name):return Path(next(x['local_path'] for x in files if x['relative'].endswith('/'+name)))
 for x in files:assert Path(x['local_path']).stat().st_size==x['bytes'] and H(x['local_path'])==x['sha256']
 route=json.loads(path('S5_SINGLE_POLICY_CONTROL_ACTUAL.json').read_bytes());src=json.loads(path('S5_SINGLE_POLICY_SOURCE_ACTUAL.json').read_bytes());S=route['controls'];N=80 if '_flat_' in a.case else 88
 assert route['all9_initial_final_actor_STD_exact'] and route['only_single_actor_forward'] and route['no_gate_or_other_expert_forward'] and route['optimizer_updates']==0 and src['no_construction_CPUCUDA_RNG_draw']
 assert route['source_SHA']==src['source_SHA']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
 with np.load(path('S5_SINGLE_FULL_CONTROL_ACTUAL.npz')) as z:b={k:z[k] for k in z.files}
 with np.load(path('retention_full_control_substep_actual.npz')) as z:d={k:z[k] for k in ('policy_obs','raw_actor_action','processed_action','terminated','truncated')}
 assert b['shared_obs'].shape==(S,N,35) and np.array_equal(b['shared_obs'],d['policy_obs']) and np.array_equal(b['raw_action'],d['raw_actor_action']) and np.array_equal(b['clipped_action'],d['processed_action'])
 normal=np.zeros((S,N,7),np.float32);normal[...,0]=1;assert np.array_equal(normal,b['shared_obs'][...,28:35])
 last=np.zeros((N,6),np.float32)
 for t in range(S):
  assert np.array_equal(last,b['shared_obs'][t,:,22:28]);last=d['processed_action'][t].copy();last[d['terminated'][t]|d['truncated'][t]]=0
 source=D/'payload/source/E1_WAVE35_frozen_source.pt';assert H(source)==route['source_SHA'];state=torch.load(source,map_location='cpu',weights_only=False)['actor_state_dict'];rng=torch.get_rng_state().clone();torch.set_num_threads(4)
 error=0.;flat=b['shared_obs'].reshape(-1,35)
 with torch.inference_mode():
  for i in range(0,len(flat),4096):
   mean=torch.from_numpy(flat[i:i+4096].copy())
   for layer in (0,2,4,6):
    mean=F.linear(mean,state[f'mlp.{layer}.weight'],state[f'mlp.{layer}.bias'])
    if layer!=6:mean=F.elu(mean)
   target=b['raw_action'].reshape(-1,6)[i:i+len(mean)];error=max(error,float(abs(mean.numpy()-target).max()));assert np.allclose(mean.numpy(),target,atol=1e-4,rtol=3e-5)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 v=dict(epoch=time.time(),passed=True,case=a.case,controls=S,num_envs=N,callbacks=S*4,source_SHA=route['source_SHA'],source9_STD_initial_final_exact=True,all_saved_CPU_means_reconstructed=True,CPU_GPU_mean_max_error=error,not_bitexact=True,once_per_tick_shared35_previous_actual_action_selectedreset_whole6_exact=True,no_truth_teacher_or_live_correction=True,only_single_actor_forward=True,gate_or_other_expert_forward=False,optimizer_updates=0,latency_ms=route['latency_ms'],not_board_deadline=True,original_EXIT_NATURAL_missing_preserved=j['outputs']['EXIT_NATURAL.json'] is None,no_GPU_PPO_or_budget=True)
 out=R/(a.case+'_S5_SINGLE_CONTROL_CPU_ADMITTED.json');assert not out.exists();out.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(passed=True,case=a.case,CPU_GPU_mean_error=error)))
if __name__=='__main__':main()
