"""Review metadata only; production D5 authority and canonical remain untouched."""
from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';F=D.parent/'MOD4_D5_FULL_CONTRACT_20261008'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'D5_MATCHED_D6_DAMPING_SDK_REVIEW.json').exists()
actual=read(F/'reports/D5_BLOCKS_ACTUAL_VERIFIED.json');matched=read(F/'reports/D5_MODEL30649_MATCHED_REVIEW.json')
sdk=read(R/'D6_GAS_DAMPING_ACTUAL_SDK_REVIEW.json')
assert actual['attention'] is None and sdk['SDK_limited_damping_parameter_lifecycle_scope_accepted']
first=actual['complete_blocks']['1'];second=actual['complete_blocks']['2']
assert first['checkpoint']['sha256']=='9f865a7a75ed62d8fa704cae4dbe320f310f15e79269fd10ed84aa5462515b98'
assert first['actual_updates']==960 and len(first['unique_completed_segment'])==1
assert second['actual_updates']==962 and second['health']['integrity_task_reset_events']==second['health']['unknown_task_reset_events']==0
assert not second['health']['nonfinite_observed'] and second['health']['stop_reason'] is None
source=dict(epoch=time.time(),checkpoint=first['checkpoint'],health=first['health'],run=first['run'],
    own_PID_bound_receipt=first['own_PID_bound_receipt'],unique_completed_segment=first['unique_completed_segment'],
    behavior_scope_accepted=True,behavior_report_SHA=sha(F/'reports/D5_MODEL30649_MATCHED_REVIEW.json'),
    protocol='Same3060/seed20261002/white_v3/A0/D0-D5, flat80/spin88/world88 each1500control15s',
    practical_selection_not_full_DR_graduation=True,world_boundary_residual_preserved=True,
    not_selected_by_highest_iteration=True,preflight_weights_not_selected=True)
(R/'SELECTED_D5_BEHAVIOR_SOURCE.json').write_text(json.dumps(source,indent=2),encoding='utf8')
old=read(R/'NEXT_D6_DAMPING_FRICTION_WORK_ORDER.json')
work=dict(old,epoch=time.time(),revision='actual_damping_setter_and_state_review',
    new_actual_setter_SDK_pending=False,actual_gas_damping_SDK_accepted=True,adapter_target_CPU_passed=13,
    checkpoint_target_CPU_passed=10,actual_CUDA_gas_factor_episode_two_RNG_disk_roundtrip_verified_in_SDK=True,
    complete_PPO_resume_and_newscope_native20k_PPO_pending=True,learning_executor_deployed=False,
    source_receipt=str(D/'reports/SELECTED_D5_BEHAVIOR_SOURCE.json'),source_SHA=source['checkpoint']['sha256'],
    original_80_off_index_reader_error_retained=True,original_80_on_never_run=True,
    next_required=[
        'Copy exact actual255 production source into a new isolated D6 authority; preserve all original255 files and add new gas worker/checkpoint/controller.',
        'Integrate gas_damping_checkpoint install/resume wrappers with D5 train entry; snapshot/source_map must include real new worker and all gas modules.',
        'First D5-to-D6 explicitly has no predecessor gas state; later actualCUDA gas factor/episode/two RNG must restore exactly before one new physical episode.',
        'Existing complete D1-D5 actor/critic/std/optimizer, sensor-feedback-action-pressure/global and named streams remain verified by original resume contract.',
        'Create correct D6 flat/spin/world frozen dispatchers using GasDampingMod4Env; reuse original immutable assets and no worker reinstall unless actual failure.',
        'At actual natural D5 fullsave/parent-guardian-children exit/active settled/two original locks, run genuinely new20k callback/readback then128x2/20kx4 fullPPO discard, charged once.',
        'Through preflight actualCUDA fullPPO startup/save/readback first, then directly bounded<=2h learning and parallel3060 retention. No repeated45minclock.',
        'Use this fully matched30649 receipt or another later actually fully paired D5 receipt; never choose unreviewed current save/maxiter/preflight.',
        'Zero nominal joint friction has no defensible absolute stress bounds yet; gas-only subset cannot be called fullD6 friction completion.'
    ])
(R/'NEXT_D6_FULL_LEARNING_WORK_ORDER.json').write_text(json.dumps(work,indent=2),encoding='utf8')
review=dict(epoch=time.time(),D5_matched_source=source,D5_current_actual_summary=dict(epoch=actual['epoch'],phase=actual['phase'],
    actual_owner=actual['actual_owner'],actual_guardian=actual['actual_guardian'],actual_child=actual['actual_child'],
    completed_second_block=second,own_current_save=actual['current']['checkpoint'] if actual['current'] else None,
    remaining_snapshot_seconds=actual['actual_tail_adjusted_remaining_seconds']),
    D5_full_first_candidate_behavior=matched,D6_actual_SDK=sdk,D6_target_CPU_contracts=dict(adapter=13,checkpoint=10),
    D6_new_work_order=work,D6_learning_deployed=False,new_budget_seconds=0,production_D5_unchanged=True,
    original_scope_raw_flags_and_failed80_preserved=True)
(R/'D5_MATCHED_D6_DAMPING_SDK_REVIEW.json').write_text(json.dumps(review,indent=2),encoding='utf8')
report='''# D5 complete matched behavior and D6 actual gas damping interface

D5 model30649 is the first complete healthy own255-source/CPU89 checkpoint:960 actual updates,460.8M environment policy steps and92160 physical callbacks. All three same3060/seed20261002/white_v3/D0-D5 flat80/spin88/world88 cases completed15s with full initial root/30q/parameters/recipes/assignments paired and12 automatically returned probe/result JSON bytes verified.

World complete-circle targets remain63/64 while worst absolute signed netcross improves .101767379 to .032305670m/s. The sole candidate residual is along .550196368m/s, .000196368 beyond the original .55 upper bound. Pure positive4pi improves7/8 to8/8; negative remains8/8. Straight errors worsen mildly from negative .016159253/positive .027840473 to .022987774/.037939243. Original strict flags/raw remain. This is a practical matched source in the firstseed-white3 protocol, not allDR/dual-seed graduation or isolated causal attribution.

D5 block2 naturally saved31610, SHA3a27d1dc300f2240320a0230a5eb7b9687bec603326562654b6384085ad5d8f9:962 updates/461.76M policy steps/92352 callbacks. Three ordinary events were two bad_orientation and one closure. The closure peak2.030361909mm remains legacyfalse; only that environment reset, no integrity/nonfinite/unknown/globalSTOP. Original parent uniquely settled7222.934006s and automatically began block3 from31610. No budget settlement repeated and no training pause for evaluation.

D6 first subset independently randomizes left/right gas damping .9-1.1 times nominal3Ns/m (2.7-3.3). The targetTorch2.10 CPU adapter13 and complete checkpoint schema10 checks pass without CUDA initialization. Two actual3060 off/on10env300control3s cases completed1200 integrated-contact and1200 each legs/wheels action callbacks. Actual PhysX damping, Articulation buffer and ImplicitActuator model match privateD6 state; selected reset, independent global streams/clocks, actualCUDA disk state roundtrip/nextdraw and same-tick actor/joint state pass. On observed2.717124462-3.256442785Ns/m; closure off/on .583233545/.583197630mm. Initial root/30q/D0-D5 parameters and assignments exactly match; final dynamics need not match. Four returned JSON byte hashes verified. SDK effort remains an estimate; no hardware force/friction calibration and no fullD6 friction claim.

The first immutable80-off proof reader incorrectly indexed a PhysX CPU tensor with a CUDA index after101 controls. It was retained as failed;80-on never ran. A separate index-reviewed81 off/on proof completed. Previous evaluator and children actually exited and sharedlock was free before the old demand task was disabled and a new no-trigger gas-review evaluator started. Its current attention is null. Existing jobs/packages/results and bounded JSON-sharing retry remain; valid jobs are not repeated. This did not alter/pause4090 production or physics.

D6 full PPO startup, native20k/newscope fullPPO and learning executor are still pending. The complete checkpoint component is prepared and CPU-tested; real fullPPO restore cannot be inferred from its fixture. Continue actual D5 block3; prepare the unique D6 authority at the natural fully settled save/two-lock boundary using actual matched30649 or a later genuinely matched source. No repeated45min clock test, no hotpatch, no double20k, no canonical clear or extra budget. Zero nominal joint friction needs a sourced absolute range separately.
'''
(R/'D5_MATCHED_D6_DAMPING_SDK_REPORT.md').write_text(report,encoding='utf8')
print(json.dumps(dict(D5_complete_first_matched_source=source['checkpoint']['sha256'],D5_block2_complete=True,D6_SDK_accepted=True,D6_learning=False,new_budget=0)))
