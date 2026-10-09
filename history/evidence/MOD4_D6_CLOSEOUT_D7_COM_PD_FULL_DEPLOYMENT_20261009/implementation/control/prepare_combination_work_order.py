"""Plan the next approved verification; no new range, learning or launch."""
from pathlib import Path
import json,time
D=Path(__file__).resolve().parent;R=D/'reports';v=dict(id='NEXT-D9-APPROVED-COMBINATION-WORK-ORDER-001',epoch=time.time(),existing_approved_S2_scope=True,
 master_SHA_unchanged='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b',D7_learning_current=True,D9_not_graduated=True,D8_load_perturbation_not_deployed=True,D8_actual_load_mass_inertia_position_force_point_duration_sources_required=True,
 D6_joint_static_dynamic_viscous_friction_actual_zero=True,absolute_friction_range_missing=True,hardware_force_stroke_not_calibrated=True,
 approved_combination_only=['D0 mass/inertia/outputgain/groundmu','D1-D2 actornoise/fourlegbias','D3 feedback0-10ms','D4 targetfirstdelay0-2.5-5ms','D5 stiffness3150-3850N/m','D6 gasdamping2.7-3.3Ns/m','D7 chassislocalxyz5mm/explicitPD095-105'],
 no_legacybundle_or_larger_ranges=True,actual_combined_D7_scope_native_PPO_and_paired_skills_required=True,
 next_required=[
 'Review actual D7 own full saves, ordinary event rates and same-platform baseline-candidate flat/spin/trueworld complete signed circles; do not select maxiter or reward.',
 'Use actually behavior-reviewed D7 source. Reuse exactly matched cases; extend development seeds20261002/3 and D0nominal/white_v2/white_v3 with D1-D7 on to complete18 conditions. These are development, not heldout/clean distribution.',
 'For nominal D0 preserve actual mild observer lifecycle; reuse the existing nominal repair logic by AST/source proof and verify new COM-PD expected observers before launching its immutable new-scope case. Do not silently disable required managers.',
 'Separately audit independence/correlation, nominal fraction and approved corner assignments with actual parameter readback/RNG/reset. Changing existing individual distributions or introducing new bounds requires its own approved-range contract, not legacyDR.',
 'Do not repeat healthy clock45min, same-scope PPO or an entire D0-D7 course. Only a genuinely new combined distribution needs its targeted contract and discarded fullPPO once on canonical.',
 'Preserve explicit old launch retirement, actual children exits/fullsave/unique settlement/two locks. Stable blocks<=2h and parallel3060 eval; no double20k or active clearing.',
 'After adequate E0 combination evidence freeze its own fullsource and proceed approved S3 independent E1 shallow terrain with same deployed interface/DR. Reuse math/SDK exactSHA while acquiring actual task behavior for E1.',
 'Read actual remaining B, reserve min(18h,.13B) and protect expert/gate comparison time; no every-expert D0-D9 full retraining or indefinite extra E0 loops.',
 'D8 unmeasured loads and S8 dangerous reset remain pending sources/specific later approval; gate currently untrained.'
 ],learning_executor_deployed=False,GPU_PPO_canonical_transactions=0)
(R/'NEXT_D9_COMBINATION_WORK_ORDER.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(prepared=True,learning_executor=False,new_budget=0)))
