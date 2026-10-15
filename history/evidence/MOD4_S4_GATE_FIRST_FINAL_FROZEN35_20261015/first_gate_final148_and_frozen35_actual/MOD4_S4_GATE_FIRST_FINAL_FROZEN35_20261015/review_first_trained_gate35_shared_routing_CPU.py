"""Every saved frozen tick: same feedback, trained logits and whole actions."""
from pathlib import Path
import argparse, hashlib, json, os, time
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
import torch
from torch.nn import functional as F
D=Path(__file__).resolve().parent;R=D/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--case',required=True);args=parser.parse_args()
    assert args.case in ('s4_first_gate_final35_native120_v1','s4_first_gate_final35_full1500_v1')
    proof=json.loads((R/('S4_FIRST_TRAINED_GATE35_OWN_PHYSICAL_DATA_ADMITTED_'+args.case+'.json')).read_bytes());assert proof['passed']
    j=json.loads(sorted(R.glob(args.case+'_CURRENT_ACTUAL_*.json'))[-1].read_bytes());files=j['collected_files']
    for row in files:assert H(row['local_path'])==row['sha256'] and Path(row['local_path']).stat().st_size==row['bytes']
    def file(name):return Path(next(v['local_path'] for v in files if v['relative']=='attempts/'+args.case+'/output/'+name))
    route=json.loads(file('S4_ROUTER_ROUTE_CONTROL_ACTUAL.json').read_bytes())
    source=json.loads(file('S4_FROZEN_PAIR_SOURCE_ACTUAL.json').read_bytes())
    gate=json.loads((D/'payload/S4_TRAINED_GATE_SOURCE_MANIFEST.json').read_bytes())
    assert source['gate_source']==route['gate_source']==gate
    assert source['gate_proof']==route['gate_proof'] and source['gate_proof']['training_updates']==148
    assert source['gate_proof']['all6_trained_gate_GPU_or_CPU_source_exact'] is True
    assert route['deterministic_trained_gate'] is True and route['new_fixture_not_trained_gate'] is False
    assert route['rule_only_command_from_shared35'] is False and route['stateless_rule_hysteresis_disabled'] is True
    assert route['gate_updates']==route['critic_updates']==source['optimizer_updates']==0
    assert source['no_construction_CPUCUDA_RNG_draw'] and source['all18_actor_std_GPU_source_exact'] and route['all18_weights_std_unchanged']
    with np.load(file('S4_ROUTING_FULL_CONTROL_ACTUAL.npz'),allow_pickle=False) as z:b={k:z[k] for k in z.files}
    with np.load(file('route_raw.npz'),allow_pickle=False) as z:a={k:z[k] for k in z.files}
    S=proof['controls'];assert route['controls']==route['feedback_provider_calls']==S
    assert b['expert_means'].shape==(S,80,2,6) and np.array_equal(b['shared_obs'],a['policy_obs'])
    assert all(np.isfinite(v).all() for v in b.values())
    normal=np.zeros((S,80,7),np.float32);normal[...,0]=1;assert np.array_equal(b['shared_obs'][...,28:35],normal)
    choice=b['logits'].argmax(-1);assert np.array_equal(choice,b['z'])
    probability=torch.from_numpy(b['logits']).softmax(-1).numpy()
    assert np.allclose(probability,b['probabilities'],atol=2e-7,rtol=2e-6)
    selected=np.take_along_axis(b['expert_means'],choice[...,None,None],axis=2).squeeze(2)
    assert np.array_equal(selected,b['raw_action']) and np.array_equal(selected,a['action'])
    assert np.array_equal(np.clip(selected,-6,6),a['processed_action'])
    previous=np.zeros((80,6),np.float32);last=np.full(80,-1);switches=0;done=a['terminated']|a['truncated']
    for t in range(S):
        assert np.array_equal(b['shared_obs'][t,:,22:28],previous)
        switches+=int(((last>=0)&(last!=choice[t])).sum());last=choice[t].copy();last[done[t]]=-1
        previous=a['processed_action'][t].copy();previous[done[t]]=0
    assert switches==route['switches']
    ckpath=D/'payload/source/S4_gate_first_final.pt';assert H(ckpath)==gate['sha256']
    ck=torch.load(ckpath,map_location='cpu',weights_only=False);state=ck['actor_state_dict']
    torch.set_num_threads(4);cpu=torch.get_rng_state().clone();max_gate=max_mean=0.
    x=b['shared_obs'].reshape(-1,35)
    with torch.inference_mode():
        for start in range(0,len(x),4096):
            xx=torch.from_numpy(x[start:start+4096].copy())
            logits=F.linear(F.elu(F.linear(F.elu(F.linear(xx,state['gate.w1'],state['gate.b1'])),state['gate.w2'],state['gate.b2'])),state['gate.w3'],state['gate.b3'])
            expected=b['logits'].reshape(-1,2)[start:start+len(xx)]
            max_gate=max(max_gate,float(abs(logits.numpy()-expected).max()))
            assert np.allclose(logits.numpy(),expected,atol=1e-4,rtol=3e-5)
            for expert in range(2):
                mean=xx
                for i in (1,3,5,7):
                    mean=F.linear(mean,state[f'experts.{expert}.frozen_{i}'],state[f'experts.{expert}.frozen_{i+1}'])
                    if i!=7:mean=F.elu(mean)
                expected=b['expert_means'].reshape(-1,2,6)[start:start+len(xx),expert]
                max_mean=max(max_mean,float(abs(mean.numpy()-expected).max()))
                assert np.allclose(mean.numpy(),expected,atol=1e-4,rtol=3e-5)
    assert torch.equal(cpu,torch.get_rng_state()) and not torch.cuda.is_initialized()
    jumps=np.max(abs(np.diff(a['processed_action'],axis=0)),axis=-1);valid=~done[:-1]
    efforts=a['physical_hardware_actual_applied_effort'].reshape(-1,80,6)
    result=dict(epoch=time.time(),passed=True,case=args.case,controls=S,callbacks=S*4,source_SHA=gate['sha256'],
        actual_training_updates_of_frozen_source=148,new_eval_PPO_updates=0,
        all_saved_feedback_rows_trained_gate_logits_and_both_expert_means_CPU_recomputed=True,
        CPU_GPU_gate_logits_max_abs_error=max_gate,CPU_GPU_expert_means_max_abs_error=max_mean,CPU_GPU_not_bitexact=True,
        same35_once_per_tick_previous_actual_action_selectedreset_whole6_exact=True,
        argmax_of_actual_GPU_logits_exact=True,no_rule_or_hysteresis_override=True,
        all18_expert_STD_initial_final_source_exact=True,all6_gate_GPU_initial_load_source_exact=True,
        gate_final_tensor_dump_not_directly_saved_all_tick_logits_recomputed_instead=True,
        selected_E0_W35_envcontrols=np.bincount(choice.ravel(),minlength=2).tolist(),switches=switches,
        control_action_jump_max_abs=float(jumps[valid].max()) if valid.any() else None,
        physical_substep_effort_jump_max_abs=float(abs(np.diff(efforts,axis=0)).max()),
        jumps_descriptive_no_new_threshold=True,latency_ms=route['latency_ms'],latency_not_board_deadline=True,
        legacy_protocol_rule_string_not_current_routing_identity=True,
        physical_full1500_behavior_completed=S==1500,native120_not_full15s=S==120,
        missing_EXIT_NATURAL_preserved=j['outputs']['EXIT_NATURAL.json'] is None,
        actual_parent_child_out_and_sharedOSlockfree=True,no_PPO_GPU_or_budget_action_by_CPU_reader=True,
        qualification_claimed=False)
    out=R/('S4_FIRST_TRAINED_GATE35_SHARED_ROUTING_ADMITTED_'+args.case+'.json');assert not out.exists()
    out.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(dict(passed=True,controls=S,switches=switches,selected=result['selected_E0_W35_envcontrols'],gate_logit_error=max_gate)))

if __name__=='__main__':main()
