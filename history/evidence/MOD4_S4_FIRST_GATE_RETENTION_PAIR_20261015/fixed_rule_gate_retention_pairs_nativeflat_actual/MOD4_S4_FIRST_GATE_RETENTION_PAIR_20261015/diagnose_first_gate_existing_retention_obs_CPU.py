"""New fixed gate on existing raw35 inputs only, without physical replay."""
from pathlib import Path
import os,hashlib,json,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
import torch
from torch.nn import functional as F
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
OLD=W/'MOD4_3060_BODYFRAME_PHASE_FINAL_RETENTION_20261015'
G=W/'MOD4_S4_GATE_FIRST_FINAL_FROZEN35_20261015/payload/source/S4_gate_first_final.pt'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    R.mkdir(exist_ok=True);assert H(G)=='02718c74024508c50ff559be2fa6351b7f63046afeb4ee3fd7c51ad6160ae1f3'
    state=torch.load(G,map_location='cpu',weights_only=False)['actor_state_dict']
    torch.set_num_threads(4);rng=torch.get_rng_state().clone();rows=[]
    for kind in ('flat','spin','world'):
        case='retention_bodyframe_phase_final_cf_'+kind+'_1500_v8'
        p=sorted((OLD/'reports').glob(case+'_CURRENT_ACTUAL_*.json'))[-1]
        saved=json.loads(p.read_bytes());raw=next(v for v in saved['collected_files'] if v['relative'].endswith('/retention_full_control_substep_actual.npz'))
        assert H(raw['local_path'])==raw['sha256']
        with np.load(raw['local_path'],allow_pickle=False) as z:x=z['policy_obs'].copy();command=z['command'].copy()
        assert x.shape[0]==1500 and x.shape[2]==35 and np.array_equal(x[...,:3],command)
        expected=np.zeros_like(x[...,28:35]);expected[...,0]=1;assert np.array_equal(x[...,28:35],expected)
        flat=x.reshape(-1,35);choice=[];margin=[]
        with torch.inference_mode():
            for i in range(0,len(flat),8192):
                a=torch.from_numpy(flat[i:i+8192])
                logits=F.linear(F.elu(F.linear(F.elu(F.linear(a,state['gate.w1'],state['gate.b1'])),state['gate.w2'],state['gate.b2'])),state['gate.w3'],state['gate.b3'])
                assert torch.isfinite(logits).all();choice.append(logits.argmax(-1).numpy());margin.append(abs(logits[:,0]-logits[:,1]).numpy())
        choice=np.concatenate(choice);margin=np.concatenate(margin)
        command=command.reshape(-1,3);rule=((abs(command[:,0])>0)&(abs(command[:,0])<=.300001)&(abs(command[:,1:3]).max(-1)<=1e-6)).astype(int)
        pure=abs(command[:,2])>2.000001
        rows.append(dict(kind=kind,actual_saved_input_source='cfce original full1500, not a new S4 physical trace',
            raw=raw,inputs=len(flat),normal_mode35_exact=True,
            new_fixed_gate_E0_W35_counts=np.bincount(choice,minlength=2).tolist(),
            normal_command_rule_E0_W35_counts=np.bincount(rule,minlength=2).tolist(),
            choice_disagreement_count=int((choice!=rule).sum()),
            abs_gate_logit_gap_range=[float(margin.min()),float(margin.max())],
            yaw_abs_above_first_gate_training_max2_rows=int(pure.sum()),
            high_yaw_gate_E0_W35=np.bincount(choice[pure],minlength=2).tolist()))
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    result=dict(epoch=time.time(),passed_saved_input_CPU_math=True,gate_source_SHA=H(G),rows=rows,
        no_new_GPU_physics_PPO_native_or_fullrestore=True,no_original_obs_command_DR_RNG_change=True,
        fixed_input_counterfactual_not_samecontrol_GPU_physical_behavior_or_causal_proof=True,
        new_frozen_rule_vs_gate_full_retention_pairs_still_required=True)
    p=R/'FIRST_GATE_FIXED_SOURCE_EXISTING_RAW35_RETENTION_RESPONSE_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(dict(passed=True,rows=[{k:r[k] for k in ('kind','new_fixed_gate_E0_W35_counts','choice_disagreement_count','high_yaw_gate_E0_W35')} for r in rows])))

if __name__=='__main__':main()
