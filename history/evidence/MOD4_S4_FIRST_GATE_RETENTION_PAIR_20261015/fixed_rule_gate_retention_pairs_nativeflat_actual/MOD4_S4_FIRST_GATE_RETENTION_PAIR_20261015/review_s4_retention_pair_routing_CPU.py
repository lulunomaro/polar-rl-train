"""Whole saved tick routing/source/history review; no connection or learning."""
from pathlib import Path
import argparse,hashlib,json,os,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
import torch
from torch.nn import functional as F
D=Path(__file__).resolve().parent;R=D/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);a=p.parse_args()
    j=json.loads(sorted(R.glob(a.case+'_CURRENT_ACTUAL_*.json'))[-1].read_bytes());files=j['collected_files']
    assert j['shared_OS_lock_free'] and all(not x['actual_alive'] for x in j['actual_PID_identities'])
    for row in files:assert Path(row['local_path']).stat().st_size==row['bytes'] and H(row['local_path'])==row['sha256']
    def path(name):return Path(next(v['local_path'] for v in files if v['relative']=='attempts/'+a.case+'/output/'+name))
    complete=j['outputs']['COMPLETE_ACTUAL.json'];S=complete['steps'];N=complete['num_envs'];kind=complete['kind']
    src=json.loads(path('S4_FROZEN_PAIR_SOURCE_ACTUAL.json').read_bytes());route=json.loads(path('S4_ROUTER_NATIVE_CONTROL_ACTUAL.json').read_bytes())
    gate=json.loads((D/'payload/S4_TRAINED_GATE_SOURCE_MANIFEST.json').read_bytes())
    mode=j['outputs']['STARTED.json']['case']['router_mode']
    assert mode in ('rule_eval','gate_eval') and src['router_mode']==route['router_mode']==mode
    assert src['gate_source']==route['gate_source']==gate
    assert src['all18_actor_weight_and_std_GPU_tensors_source_exact'] and route['source_all18_weights_std_unchanged']
    exact=json.loads(path('S4_GATE_INITIAL_FINAL_TENSORS_EXACT.json').read_bytes())
    assert exact['all6_initial_final_source_exact'] is True and exact['source_SHA']==gate['sha256'] and exact['router_mode']==mode
    assert src['gate_proof']['training_updates']==148 and src['optimizer_updates']==route['gate_optimizer_updates']==route['critic_optimizer_updates']==0
    assert src['no_CPU_or_CUDA_rng_draw_from_pair_construction'] and route['optional_hysteresis_disabled_for_first_stateless_native']
    with np.load(path('S4_ROUTING_FULL_CONTROL_ACTUAL.npz'),allow_pickle=False) as z:b={k:z[k] for k in z.files}
    with np.load(path('retention_full_control_substep_actual.npz'),allow_pickle=False) as z:data={k:z[k] for k in z.files}
    assert S==route['controls']==route['feedback_provider_calls'] and b['shared_obs'].shape==(S,N,35)
    assert np.array_equal(b['shared_obs'],data['policy_obs']) and np.array_equal(b['shared_obs'][...,:3],data['command'])
    assert all(np.isfinite(v).all() for v in b.values())
    normal=np.zeros((S,N,7),np.float32);normal[...,0]=1;assert np.array_equal(b['shared_obs'][...,28:35],normal)
    cmd=b['shared_obs'][...,:3]
    if mode=='rule_eval':
        choice=((abs(cmd[...,0])>0)&(abs(cmd[...,0])<=.300001)&(abs(cmd[...,1:3]).max(-1)<=1e-6)).astype(int)
        assert np.array_equal(b['probabilities'],np.stack((1-choice,choice),-1))
    else:
        choice=b['logits'].argmax(-1)
        assert np.allclose(b['probabilities'],torch.from_numpy(b['logits']).softmax(-1).numpy(),atol=2e-7,rtol=2e-6)
    assert np.array_equal(choice,b['z'])
    selected=np.take_along_axis(b['expert_means'],choice[...,None,None],axis=2).squeeze(2)
    assert np.array_equal(selected,b['raw_action']) and np.array_equal(selected,data['raw_actor_action'])
    assert np.array_equal(np.clip(selected,-6,6),data['vec_clipped_action']) and np.array_equal(data['vec_clipped_action'],data['processed_action'])
    previous=np.zeros((N,6),np.float32);last=np.full(N,-1);switches=0;done=data['terminated']|data['truncated']
    for t in range(S):
        assert np.array_equal(b['shared_obs'][t,:,22:28],previous)
        switches+=int(((last>=0)&(last!=choice[t])).sum());last=choice[t].copy();last[done[t]]=-1
        previous=data['processed_action'][t].copy();previous[done[t]]=0
    assert switches==route['switches']
    gatefile=D/'payload/source/S4_gate_first_final.pt';assert H(gatefile)==gate['sha256']
    state=torch.load(gatefile,map_location='cpu',weights_only=False)['actor_state_dict']
    torch.set_num_threads(4);rng=torch.get_rng_state().clone();flat=b['shared_obs'].reshape(-1,35);gate_error=mean_error=0.
    with torch.inference_mode():
        for start in range(0,len(flat),4096):
            x=torch.from_numpy(flat[start:start+4096].copy())
            logits=F.linear(F.elu(F.linear(F.elu(F.linear(x,state['gate.w1'],state['gate.b1'])),state['gate.w2'],state['gate.b2'])),state['gate.w3'],state['gate.b3'])
            target=b['logits'].reshape(-1,2)[start:start+len(x)]
            gate_error=max(gate_error,float(abs(logits.numpy()-target).max()));assert np.allclose(logits.numpy(),target,atol=1e-4,rtol=3e-5)
            for e in range(2):
                mean=x
                for i in (1,3,5,7):
                    mean=F.linear(mean,state[f'experts.{e}.frozen_{i}'],state[f'experts.{e}.frozen_{i+1}'])
                    if i!=7:mean=F.elu(mean)
                target=b['expert_means'].reshape(-1,2,6)[start:start+len(x),e]
                mean_error=max(mean_error,float(abs(mean.numpy()-target).max()));assert np.allclose(mean.numpy(),target,atol=1e-4,rtol=3e-5)
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    jumps=np.max(abs(np.diff(data['processed_action'],axis=0)),axis=-1);valid=~done[:-1]
    effort=data['substep_actual_applied_effort']
    result=dict(epoch=time.time(),passed=True,case=a.case,kind=kind,mode=mode,steps=S,envs=N,callbacks=S*4,
        gate_source_SHA=gate['sha256'],all24_initial_final_source_exact=True,same35_once_previous_actual_action_selectedreset_whole6_exact=True,
        GPU_choice_from_declared_mode_exact=True,no_blend_teacher_or_hysteresis=True,
        all_saved_CPU_source_gate_logits_expert_means_recomputed=True,CPU_GPU_logit_error=gate_error,CPU_GPU_mean_error=mean_error,CPU_GPU_not_bitexact=True,
        selected_E0_W35_envcontrols=np.bincount(choice.ravel(),minlength=2).tolist(),switches=switches,
        actual_control_action_jump_max_abs=float(jumps[valid].max()) if valid.any() else None,
        actual_substep_effort_jump_max_abs=float(abs(np.diff(effort,axis=0)).max()),jumps_descriptive_no_new_threshold=True,
        latency_ms=route['inference_chain_latency_ms'],not_board_deadline=True,
        current_eval_optimizer_updates=0,original_gate_training_updates=148,source_checkpoint_argument_is_W35_scene_anchor=True,
        missing_EXIT_NATURAL_preserved=j['outputs']['EXIT_NATURAL.json'] is None,actual_parent_child_out_sharedOSlockfree=True,
        no_GPU_PPO_or_budget_action_by_reader=True,qualification_claimed=False)
    out=R/(a.case+'_S4_ROUTING_CPU_ADMITTED.json');assert not out.exists();out.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(dict(passed=True,case=a.case,selected=result['selected_E0_W35_envcontrols'],switches=switches)))

if __name__=='__main__':main()
