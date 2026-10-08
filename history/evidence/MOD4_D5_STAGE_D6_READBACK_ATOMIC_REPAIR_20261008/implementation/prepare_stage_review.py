"""Summarize measured D5 stage, D6 preparation and evaluator repair evidence."""
from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';F=D.parent/'MOD4_D5_FULL_CONTRACT_20261008';read=lambda p:json.loads(p.read_text(encoding='utf8'))
a=read(F/'reports/D5_BLOCKS_ACTUAL_VERIFIED.json');b=a['complete_blocks']['1'];h=b['health'];s=b['unique_completed_segment'];assert len(s)==1
elapsed=s[0]['ended_epoch']-s[0]['started_epoch'];assert b['actual_updates']==960 and b['actual_environment_steps']==460800000
sdk=read(R/'D6_NOMINAL_ACTUAL_JOINT_SDK_REVIEW.json');w=read(R/'ATOMIC_RETRY_WORKER_CURRENT_ACTUAL.json');native=read(R/'NATIVE_WINDOWS_RECEIPT_SHARING_PASSED.json')
assert sdk['SDK_read_only_parameter_scope_accepted'] and native['passed'] and not w['current_attention']
scope=read(F/'reports/D5_ACTUAL_BASELINE_SCOPE_REVIEW.json');base=scope['cases']['70-d5-anchor']
v=dict(epoch=time.time(),D5_actual=a,D5_first_block_unique_charged_seconds=elapsed,D5_same_platform_behavior=scope,
 D6_actual_source_parameters=sdk,D6_CPU_component_only=read(R/'GAS_DAMPING_CPU_PASSED.json'),
 actual_frozen_evaluator_repair=w,actual_native_Windows_sharing_fixture=native,
 no_new_GPU_PPO_preflight_or_clock_trial_this_turn=True,no_4090_source_runtime_or_canonical_mutation=True,new_budget_seconds=0,
 source_indexes=[dict(local_name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in sorted((D/'reviewed_sources').glob('*.py'))],
 D6_learning_executor_not_deployed=True,D6_randomized_actual_SDK_native20k_PPO_checkpoint_pending=True,all_courses_finished=False)
(R/'D5_BLOCK1_D6_SOURCE_AND_EVALUATOR_REPAIR_REVIEW.json').write_text(json.dumps(v,indent=2),encoding='utf8')
work=read(F/'reports/ACTUAL_NEXT_D6_DAMPING_FRICTION_WORK_ORDER.json')
work.update(epoch=time.time(),actual_source_review='D6_NOMINAL_ACTUAL_JOINT_SDK_REVIEW.json',actual_nominal_SDK_completed=True,
 CPU_first_gas_damping_component_passed=9,CPU_root='/home/egde/rl_candidates/MOD4_D6_DAMPING_SOURCE_PREPARE_20261008',
 first_verified_subset='Gas damping only, independent left/right episode3Ns/m*.9-1.1=2.7-3.3Ns/m; D5 stiffness and D0-D4 remain.',
 actual_PD_and_passive_damping_must_not_be_conflated=True,actual_leg_wheel_PhysX_damping_zero=True,actual_explicit_PD_derivative_2_and_point6=True,
 actual_joint_static_dynamic_viscous_friction_all_zero=True,static_dynamic_units='N*m for revolute; N for prismatic, current IsaacSim6 installedSDK',
 viscous_units='N*m*s/rad or N*s/m',absolute_friction_bound_source_available=False,
 legacy_point10_point02_bounds_are_engineering_code_not_hardware_measurement=True,
 nominal_SDK_proves_readback_not_randomized_setter=True,new_component_has_no_GPU_PPO_launch_authority=True,
 new_actual_setter_SDK_pending=True,complete_checkpoint_and_newscope_native20k_PPO_pending=True,
 next_required=[
  'Isolated D6 adapter updates actual gas PhysX damping, Articulation buffer and ImplicitActuator model together; never change explicit motor PD here.',
  'Verify unchanged passive joints, stiffness from independent D5 state, preload/cap/armature/friction and all remaining D0-D5 parameters.',
  'Verify independent D6 private episode RNG, selected reset without other-row/global-stream/tick changes and actualCUDA state+next draw disk roundtrip.',
  'Make existing D5 fixed-damping and D0 PD auditors parameter-aware only after independently verifying actual D6 state, restoring original references in finally; no ignored checks or looser tolerances.',
  'Full gas-damping state/optimizer/sensor/feedback/action/pressure/global and named RNG checkpoint, exact startup restore then one explicitly new physical episode/queue rebase.',
  'Actual20k complete callback/parameters/integral/target/hardware and genuinely new128x2/20kx4 fullPPO discard charged once; no repeated clock45min.',
  'Choose actual complete behavior-reviewed D5 source from receipts after same-platform3 skill comparison; no directorymax/preflight/unreviewed candidate.',
  'Safe new unique bounded entry only after fullsave/old launch closed/actual children exit/two locks/active settled; D5 active training continues independently.',
  'Resolve zero joint friction absolute range through a defensible engineering/hardware source separately; do not claim zero-times-factor gives friction DR or fullD6 completion.'
 ])
(R/'NEXT_D6_DAMPING_FRICTION_WORK_ORDER.json').write_text(json.dumps(work,indent=2),encoding='utf8')
note=f'''D5 first2h naturally saved model30649, SHA{b['checkpoint']['sha256']}, ownCPU89/255-source/31snapshots verified. 960 actualupdates,23040 control steps,460800000 environment-policy steps and92160 callbacks exact. Three bad_orientation single-episode resets; closure/integrity/unknown0,nonfinitefalse,closure peak1.907896mm. One canonical segment charged{elapsed:.9f}s by the existing parent; no repeated charge. The controller automatically began block2 from its own fullsave, restoring D5 factors/twoCUDA RNG plus all D1-D4/optimizer/global/named streams before one new physical episode. No PhysX exactresume claim, no3060wait, no repeated45min clock trial.

All three same3060 D5 baseline cases actually completed with stiffness pressure, physical action delay and feedback delay. Firstseed20261002/white_v3 scope only: world63/64/maxabsnetcross.101767m/s, pure+4pi7/8 and negative8/8, straight negativeerror.016159 and positive.027840. Original flags/raw preserved; this is a stressbaseline rather than the newly trained D5 policy. New30649 candidate flat completed and paired, errors.022988/.037939; full spin/world comparison remains pending at this snapshot. No graduation or architecture selection inferred.

D6 actual frozen-plant/installedSDK review plus one new read-only3060 tenenv300control SDK confirmed gas damping3Ns/m in actual PhysX, buffer and Implicit model,1200 contact and1200 callbacks for each action group. All actual static/dynamic/viscous joint friction values were zero. InstalledSDK6 units are static/dynamic effort N orNm, viscous Ns/m orNm*s/rad. Explicit motor PD derivatives are legs2 and wheels.6 while their PhysX damping is zero: sourceUSD damping and actual motor control must not be conflated. New private-RNG gas-only .9-1.1 component passed9 targetTorch2.10 CPU checks without CUDA initialization. Actual randomized damping setter/SDK/fullcheckpoint/native20k/PPO/controller remain pending. No invented absolute friction bound or hardware calibration; currentD5 source/parameters untouched.

The3060 evaluator exited at a Windows WinError5 replacing its polling JSON. Real priorworker+children exit, demandtaskReady and free sharedGPUlock were verified before a new authority. Preserved all original files/attention/results/XML, disabled old demandtask and launched one new demandtask with no periodic/boot trigger. Unique temporary receipts and bounded retry for Windows5/32/33 prevent transient read-sharing from ending evaluation; persistent/unrelated errors still raise and retain evidence. Target CPU injection proved transient/persistent/unrelated behavior. Actual native Windows deny-delete reader produced four real WinError5 failures and the new writer succeeded after the reader released in.375s. New actual worker identity/source/task/children verified and it resumed pending candidate jobs without replaying completed ones.4090 training never stopped and canonical writes were0.

Master plan v1.5 SHA unchanged. Six authorized budget extensions remain exactly once, newbudget0. Weights/large probes/USD/NPZ only SHA-indexed. No all-course completion, no MoEgate, no hardware certification.
'''
(R/'D5_BLOCK1_D6_SOURCE_AND_EVALUATOR_REPAIR_REPORT.md').write_text(note,encoding='utf8')
print(json.dumps(dict(D5_block1_seconds=elapsed,D5_current_block=a['current']['block'] if a['current'] else None,D6_first_subset=work['first_verified_subset'],actual_evaluator_PID=w['own_actual_identity']['ProcessId'])))
