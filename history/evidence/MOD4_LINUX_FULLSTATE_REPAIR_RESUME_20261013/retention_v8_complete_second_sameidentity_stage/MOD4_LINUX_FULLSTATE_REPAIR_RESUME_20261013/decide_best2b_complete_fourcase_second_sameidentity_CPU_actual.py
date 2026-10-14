"""Independent root scope decision from complete evidence, no dispatch or budget."""
from pathlib import Path
import hashlib,json,time,math
D=Path(__file__).resolve().parent;W=D.parent
SOURCE='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'

def H(p):
    digest=hashlib.sha256()
    with Path(p).open('rb') as f:
        while block:=f.read(4*1024*1024):digest.update(block)
    return digest.hexdigest()

def indexed(p):
    return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=H(p))

def main():
    out=D/'reports/BEST2B_COMPLETE_FOURCASE_SECOND_SAMEIDENTITY_SCOPE_DECISION_ACTUAL.json'
    assert not out.exists()
    files={
        'own_CPU':D/'reports/LEFT_FORMAL_FINAL_LOCAL_CPU_AND_FROZEN80_CANDIDATE_PREPARED.json',
        'own_closeout':D/'reports/LEFT_FORMAL_FINAL_ACTUAL_COLLECTION.json',
        'own_fulltrace':D/'reports/LEFT_FORMAL_FINAL_FULLTRACE_CPU_ACTUAL_1791944915897783800.json',
        'wave_complete':W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014/reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json',
        'wave_direct':W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014/reports/LEFT_REPAIR_DIRECT_ORIGINAL_FULL80_PREFIX_ACTUAL_REVIEW.json',
        'three_pairs':W/'MOD4_3060_LEFT_REPAIR_RETENTION_20261014/reports/RETENTION_V8_THREE_PAIRS_COMPLETE_ACTUAL_CPU_REVIEW.json',
        'rejected_factors':D/'reports/TWO_MEAN_ONLY_FACTORS_COMPLETE_AND_PRODUCTION_REJECTED_ACTUAL.json',
    }
    values={k:json.loads(p.read_text(encoding='utf8')) for k,p in files.items()}
    own=values['own_CPU'];assert own['passed'] and own['whole107finite'] and own['thirteen_CPUCUDA_sameidentity_verified'] and own['actual_exit_idle']
    assert own['own_final_source']['sha256']==SOURCE and own['updates']==189 and own['actor9changed_Adam3780']
    model=Path(own['own_final_source']['local_path']);assert model.stat().st_size==19044152 and H(model)==SOURCE
    close=values['own_closeout']['actual_remote_review']
    assert close['passed'] and close['sourcefreeze_all_bytes_actual_verified'] and close['sourcefreeze_count']==522
    assert close['actual_parent_child_guardian_exit_twofcntlFree_idle'] and close['no_budget_mutation']
    wrap=values['own_fulltrace'];assert wrap['code']==0
    trace=json.loads(wrap['stdout']);assert trace['passed'] and trace['own_final_SHA']==SOURCE
    assert trace['controls']==4536 and trace['envsteps']==90720000 and trace['callbacks']==18144
    assert trace['reset_teleport_excluded'] and trace['reason_coverage_exact'] and trace['truncation_coverage_exact']
    assert len(trace['full_trace'])==9 and trace['total_trace_bytes']==2640276618
    wave=values['wave_complete'];assert wave['passed'] and wave['source_SHA']==SOURCE and wave['raw']['remote_local_byteSHA_exact']
    direct=values['wave_direct'];assert direct['passed']
    aggregate=values['three_pairs']['result']
    assert aggregate['all_three_pairs_actual_complete'] and not aggregate['actual_pending']
    assert set(aggregate['full_pairs'])=={'flat','spin','world'}
    for kind,pair in aggregate['full_pairs'].items():
        assert pair['source_Dll_actor_root_q30_parameters_recipes_RNG_queues_exact']
        for label in ('baseline_provenance','candidate_provenance'):
            provenance=pair[label];data=provenance['data_audit']
            for flag in ('all_controls_and_substeps_finite','actual_q30_policy35_action6_exact','no_reset_teleport_credit','DC_hardware_actual_bounds_exact','COM_frame_original1e5_passed','actual_represented_plane_query_1e6_passed','complete_data_contract'):
                assert data[flag] is True,(kind,label,flag)
        assert pair['candidate_provenance']['source_actor_SHA']==SOURCE
    rejected=values['rejected_factors'];assert rejected['original_best_source_sha256']==SOURCE
    assert all(not v['production_adopted'] for v in rejected['factors'].values())
    flat=aggregate['full_pairs']['flat'];spin=aggregate['full_pairs']['spin'];world=aggregate['full_pairs']['world']
    assert all(row['candidate_minus_baseline_error']<0 for row in flat['comparison'])
    assert flat['baseline_provenance']['reset_counts']['ordinary']==flat['candidate_provenance']['reset_counts']['ordinary']==0
    assert spin['baseline_provenance']['reset_counts']['ordinary']==spin['candidate_provenance']['reset_counts']['ordinary']==1
    assert world['baseline_provenance']['reset_counts']['ordinary']==world['candidate_provenance']['reset_counts']['ordinary']==0
    wc=world['comparison'];assert (wc['baseline_count'],wc['candidate_count'],wc['sample_count'])==(62,61,64)
    negative=[x for x in spin['comparison'] if x['command_yaw_rad_s']<0][0]
    assert all(x['candidate_minus_baseline_absolute_error']>0 for x in negative['per_paired_sample'])
    result=dict(
        epoch=time.time(),decision_id='whole20k2b_fourcase_complete_second_and_last_sameidentity_learning',
        selected_source_SHA=SOURCE,selected_source=indexed(model),
        whole20k2b_source_actual_CPU_verified=True,first_formal_fulltrace_actual_reviewed=True,
        four_frozen_cases_actual_complete=True,physical_source_query_contact_COMhardware_all_raw_admitted=True,
        sameidentity_second3600_reasonable=True,no_new_policy_axis=True,
        center_near_candidates_rejected_not_source=True,second_and_last_block_before_full_audit=True,
        scope_learning_block_index=2,max_blocks_same_axis=2,first_seconds=3600,second_seconds=3600,total_planned_seconds=7200,
        evidence={k:indexed(p) for k,p in files.items()},
        first_formal_actual_parent_unique_cost_seconds=own['actual_parent_unique_seconds'],
        retention_actual_unique_zero_PPO_cost_seconds=aggregate['actual_zero_PPO_cost_total_seconds'],
        observations=dict(terrain_forward_before=7,terrain_forward_after=22,terrain_reverse_before=27,terrain_reverse_after=25,
            terrain_ordinary=0,flat_comparison=flat['comparison'],spin_ordinary_before=1,spin_ordinary_after=1,
            negative4pi_all_eight_yaw_error_regressed=True,
            negative4pi_per_env_additional_error_rad_s=[x['candidate_minus_baseline_absolute_error'] for x in negative['per_paired_sample']],
            world_original_target_before=62,world_original_target_after=61,world_samples=64,
            world_improved_envs=wc['improved_envs'],world_regressed_envs=wc['regressed_envs'],world_ordinary_before=0,world_ordinary_after=0),
        independent_root_reasoning=[
            'Terrain forward has substantial observed improvement with15 paired improvements and no forward regression;5forward2reverse failures remain. This motivates bounded additional learning, not graduation.',
            'Complete inherited behavior audit reveals improved straight tracking, slower negative high-rate spin and minor world-progress regressions. Those regressions and all original strictfalse flags are preserved; no claim of all skills retained or permanent anti-forgetting.',
            'Ordinary event counts did not increase across the three paired skills; all complete physical/query/contact/COM/hardware data and valid prefixes are admitted. A second and last sameidentity block is a controlled continuation within the already authorized2h/max2 scope, not an automatic success-count threshold.',
            'Keep both baseline1aa and best2b immutable as comparison checkpoints. Do not adopt rejected mean-copy factors, override other experts, train gate, change geometry/reset/commands/DR/reward/LR/hardware/clock, or promote70.',
            'After the second block, require its own whole10799/sourcefreeze/13restore/actorAdam/health/unique parent cost and natural exit/two locks idle; then full trace and all four actual frozen cases including direct2b prefix comparison. No third blind duration-only block.',
        ],
        qualified50=False,qualified70=False,all_skills_accepted=False,global_optimum_claimed=False,
        original_flags_preserved={k:v['legacy_false_preserved'] for k,v in aggregate['full_pairs'].items()},
        represented_native_plane_reference_limits_preserved=True,original_V6_failure_unchanged=True,
        no_mechanical_graduation_score=True,no_new_GPU_PPO_or_budget_transaction_by_this_CPU_decision=True,
        second_target_CPU_sourcefreeze_resource_and_actual_GPU_startup_still_required=True,
    )
    out.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(dict(decision=str(out),four_cases_actual_complete=True,selected_source_SHA=SOURCE,sameidentity_second3600_reasonable=True,qualification_claimed=False,negative_spin_and_world_regressions_preserved=True)))

if __name__=='__main__':main()
