"""Record measured frame-factor inference bounds, no production adoption."""
from pathlib import Path
import json,time,hashlib
P=Path(__file__).resolve().parent;R=P/'reports';D=P.parent/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
full=R/'YAWPI_OWN_FULL1500_ACTUAL_CPU_ADMITTED_V4.json';direct=R/'YAWPI_FULL1500_DIRECT_SAME_WORLD_E3_ACTUAL_CPU_REVIEW_V4.json'
a=read(full);b=read(direct)
assert a['passed_actual_data_and_factor_admission'] and b['passed_actual_sameWORLD_pair']
assert [b['baseline_WORLD_forward'],b['baseline_WORLD_reverse']]==[24,26]
assert [b['factor_WORLD_forward'],b['factor_WORLD_reverse']]==[27,25]
assert b['per_WORLD_group']['0']['improved']==[6,15,69] and b['per_WORLD_group']['0']['regressed']==[]
assert b['per_WORLD_group']['1']['regressed']==[64] and b['per_WORLD_group']['1']['failed_both']==[67]
assert a['ordinary']==0 and a['controls']==1500 and a['callbacks']==6000
proof=read(a['collector']['path']);end=proof['states']['PARENT_EXIT_RECEIPT.json']
assert end['exit_code']==0 and end['no_PPO'] and not end['canonical_budget_written'] and end['complete_data_contract_present'] and not end['original_error_present']
assert proof['shared_actual_OS_lock_free'] and all(not r['running'] for r in proof['actual_PID_identities'])
moving=[abs(z) for i,z in enumerate(a['actual_declared_safe_Z_delta_m']) if i%3!=2]
report=dict(epoch=time.time(),actual_factor_complete=True,current_plan_stage='S3/E1 Wave50 traversal and inherited-skill repair',
 unchanged_trained_candidate=dict(model=32825,sha256=a['source_SHA'],original_source_protocol_forward=24,original_source_protocol_reverse=26),
 actual_factor_only_result=dict(WORLD_forward_BODY_reverse=27,WORLD_reverse_BODY_forward=25,ordinary=0,improved_original_forward_envs=[6,15,69],regressed_original_reverse_envs=[64],persistent_reverse_failed_envs=[67],standing26_no_transit_requirement=True),
 actual_frozen_parent_seconds=end['unique_actual_parent_load_run_save_exit_seconds'],no_PPO_or_canonical_charge=True,
 actual_parent_child_out_and_shared_OS_lock_free=True,missing_EXIT_NATURAL_preserved=True,
 physical_query_contact_COM_hardware_all_original_tolerances_passed=True,all_1500controls_6000callbacks_and_valid_failed_prefixes_retained=True,
 q30_XY_fullparams_staticrecipes_capturedRNGqueues_exact=True,
 root_quaternion_pi_and_safe_Z_explicit_change_NOT_root30_byteexact=True,moving_cohort_initial_safe_Z_max_abs_delta_m=max(moving),
 interpretation='With unchanged weights and WORLD path/cohorts, reversing body heading and BODY command resolves all three prior forward residuals but introduces reverse64 failure; body-frame dependence is experimentally supported. Terrain-entry direction alone is insufficient to explain the original asymmetry.',
 limitations=['This is a combined declared body-heading/BODY-command frame factor with necessary full-footprint safeZ. It does not uniquely distinguish learned policy, chassis/contact geometry or their interaction.','Original trained source remains24/26 at its original initialization; factor27/25 is not a newly trained checkpoint or50mm/70mm qualification.','Inherited positive high-rate spin regression and its command-domain gap remain; no change to production command/DR/reward/hardware or claim allskills improved.'],
 next_authorized_work=['Read approved S3 and existing entry/direction-source identities before implementation. Prepare one explicit orientation/exposure repair axis from whole source e3 under standing repair authorization.','CPU preparation must disclose new entry/direction/reset identity only after strict old fullstate restoration, preserve full20k actorcriticstdoptimizer D0D7 globalnamed/privateCPUCUDA, fixed commands/clock/reward/hardware; no source512/128 splicing or initializer repetition.','Do not change running/old source, repeat these GPU tasks, or start a third duration-only same-axis PPO. Any new learning requires its own declared scope, CPU negative tests, resource/sourcefreeze, native/fullstate and exact budget admission and bounded full audit.','No liveheading/position correction, teacher, truth-gate, weakened query/contact/COM or70mm escalation. Preserve E0/35/CURB/SLOPE and gate status.'],
 S4_gate_not_trained=True,qualified50=False,qualified70=False,allskills_accepted=False,global_best_claimed=False,
 evidence={k:dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=H(p)) for k,p in [('whole_full1500_review',full),('sameWORLD_direct_pair',direct)]},Git_ordinary_supplement_pending=True)
p=R/'YAWPI_FULL1500_COMPLETE_SCOPE_DECISION_CPU_ACTUAL.json';assert not p.exists();p.write_bytes(json.dumps(report,ensure_ascii=False,indent=2).encode())
w=P/'NEXT_E3_FRAME_FACTOR_COMPLETE_AND_DECLARED_SINGLE_AXIS_REPAIR_CPU_WORK_ORDER.json';assert not w.exists();w.write_bytes(json.dumps(report,ensure_ascii=False,indent=2).encode())
print(json.dumps(dict(actual_frozen_factor_complete=True,original_trained_source=[24,26],factor_sameWORLD=[27,25],ordinary=0,original_source_unchanged=True,whole_raw=a['raw'],sameWORLD_group_changes=b['per_WORLD_group'],max_moving_safeZ_delta_m=max(moving)),ensure_ascii=False))
