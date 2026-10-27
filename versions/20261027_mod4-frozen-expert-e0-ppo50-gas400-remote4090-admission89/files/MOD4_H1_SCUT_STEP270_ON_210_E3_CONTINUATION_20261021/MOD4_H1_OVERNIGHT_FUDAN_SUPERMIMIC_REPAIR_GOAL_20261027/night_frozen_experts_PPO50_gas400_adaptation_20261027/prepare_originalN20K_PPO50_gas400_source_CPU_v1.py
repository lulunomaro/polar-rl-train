"""New4090 source fork keeps the original20k population, all core/state/RNG bytes."""
from pathlib import Path
import copy, json, time, traceback
from prepare_typed_E0_W35_N256_fork_CPU_v1 import HERE, ORIGINAL, SPEC, H, exact

def main():
    import torch
    torch.set_num_threads(2)
    rng = torch.get_rng_state().clone()
    out = HERE / "typed_originalN20K_sources_v1"
    assert not out.exists()
    out.mkdir()
    rows = {}
    for role, (name, sha, iteration, adam) in SPEC.items():
        path = ORIGINAL / name
        assert H(path) == sha
        ck = torch.load(path, map_location="cpu", weights_only=False)
        assert ck['iter'] == iteration and ck['spring_pressure_state']['n'] == 20000
        assert {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()} == {adam}
        value = copy.deepcopy(ck)
        before = dict(control_us=value['physical_action_delay_state']['control_us'],
                      recipe_control_us=value['physical_action_delay_recipe']['control_period_us'],
                      nominal_k=value['spring_pressure_recipe']['nominal_stiffness_N_m'],
                      k_bounds=value['spring_pressure_recipe']['actual_stiffness_bounds_N_m'])
        assert before == dict(control_us=10000, recipe_control_us=10000, nominal_k=3500, k_bounds=[3150,3850])
        value['physical_action_delay_state']['control_us'] = 20000
        value['physical_action_delay_recipe']['control_period_us'] = 20000
        value['spring_pressure_recipe']['nominal_stiffness_N_m'] = 2000
        value['spring_pressure_recipe']['actual_stiffness_bounds_N_m'] = [1800,2200]
        # Invert the four declared scalars to prove the entire original state
        # (including all old queues/factors/global and private RNG) was retained.
        witness = copy.deepcopy(value)
        witness['physical_action_delay_state']['control_us'] = before['control_us']
        witness['physical_action_delay_recipe']['control_period_us'] = before['recipe_control_us']
        witness['spring_pressure_recipe']['nominal_stiffness_N_m'] = before['nominal_k']
        witness['spring_pressure_recipe']['actual_stiffness_bounds_N_m'] = before['k_bounds']
        assert exact(witness, ck, torch)
        meta = dict(schema='mod4.frozen_expert.originalN20K.PPO50_gas400.v1',role=role,
                    original_source_path=str(path),original_source_SHA=sha,original_iteration=iteration,
                    original_Adam_step=adam,original_population=20000,target_population=20000,
                    actor35_critic38_original=True,core_STD_optimizer_LR_D1_D7_private_global_RNG_literal_original=True,
                    four_recipe_scalars_changed_only=True,original_queue_history_not_rescaled=True,
                    source_history_restore_then_one_new_actual_episode_required=True,
                    policy_hz=50,physics_dt_s=.0025,decimation=8,solver='TGS32/4',
                    gas_force_N_each=400,gas_nominal_k_N_m=2000,gas_upper_q_m=.020639440248416612,
                    gas_lower_q_m=-.0267046843609,gas_damping_Ns_m=3,hardware_force_curve_calibrated=False,
                    same_PhysX_resume=False,new_adaptation_skill_qualified=False,original_frozen_label_unchanged=True,
                    target_CUDA_restore_and_GPU_training_admitted=False,producer_path=str(Path(__file__).resolve()),producer_SHA=H(__file__))
        value['PPO50_gas400_adaptation'] = meta
        target = out / (role+'_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt')
        torch.save(value, target)
        assert exact(torch.load(target,map_location='cpu',weights_only=False),value,torch)
        rows[role] = dict(original=meta,new_source=dict(path=str(target),bytes=target.stat().st_size,SHA=H(target)),
                          entire_original_state_inverse_four_scalar_proof=True,saved_roundtrip=True)
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    report=HERE/'reports/ORIGINAL_N20K_PPO50_GAS400_SOURCE_CPU_ACTUAL_V1.json'
    with report.open('x',encoding='utf8') as f:
        json.dump(dict(attempt_id='E0_W35_ORIGINAL_N20K_PPO50_GAS400_SOURCE_CPU_20261027_V1',epoch=time.time(),sources=rows,
                       previous_N256_forks_preserved_not_deployed=True,new_user_4090_only=True,no_GPU_remote_budget=True,
                       Git_status='pending_root_ordinary_supplement'),f,ensure_ascii=False,indent=2)
    print(json.dumps(dict(report=str(report),sources={k:v['new_source'] for k,v in rows.items()})))

if __name__=='__main__':
    try:main()
    except Exception:
        (HERE/('reports/N20K_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc(),no_GPU=True),indent=2),encoding='utf8')
        raise
