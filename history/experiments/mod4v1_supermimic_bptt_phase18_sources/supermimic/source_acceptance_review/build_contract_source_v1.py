"""Build a SOURCE_ONLY contract from a closed, explicit local text allowlist.
No imports from runtime/SDK, no checkpoint/raw input, no physical execution.
Every output is exclusive-create; keep old source attempts and receipts.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'mod4v1_experts_fulldr_rm70_20261101'
OUT = Path(__file__).resolve().parent
V8 = BASE / 'NINE_N80_PARALLEL_SOURCE_V8'
E1 = BASE / 'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR'
PT = BASE / 'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102'
REF = BASE / 'acceptance_contract_sourceonly_v1/original_reference_text'
S50 = BASE / 'staged_sources/E1_SLOPE_INDEPENDENT50_40050_MOD4V1_SOURCE_V2'
E3 = BASE / 'staged_sources/E3_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4'

# Only files already inspected as source/published metadata during this review.
SOURCES = {
 'final_report': (BASE/'MOD4V1_EIGHT_EXPERTS_POSTTRAIN_FINAL_V1.md', '1-78'),
 'progress22': (BASE/'CURRENT_PROGRESS_v22_EIGHT_TRAINED_ASSESSED_FINAL_ARCHIVE_PENDING.md', '15-45'),
 'registry12': (BASE/'EXPERT_NORMALIZATION_REGISTRY_v12.json', '1-240;344-535'),
 'historical_matrix_summary': (BASE/'acceptance_contract_sourceonly_v1/ACCEPTANCE_CONTRACT_MATRIX_SOURCE_ONLY_FINAL_V3.md', '6-26;82-85'),
 'e0_catalog': (REF/'E0_CATALOG__e0_original_profile_catalog_v1.py', '1-20'),
 'e0_metrics': (REF/'E0_METRICS__e0_long_command_domain_telemetry_v1.py', '32-94;157-181;199-206'),
 'five_worker': (V8/'worker_five_original_n80.py', '50-53;67-116'),
 'e2_bridge': (V8/'minimal_e2_cycles_bridge.py', '5-20'),
 'e2_cycles': (V8/'e2_cycles213.py', '44-127'),
 'e2_catalog': (V8/'e2_original_profile_catalog_candidate_v1.py', '1-20'),
 'w35_intervals': (V8/'rm70_intervals227.py', '36-107;108-190'),
 'w35_split_observer': (PT/'source_assess_pair4_v1/observer_w35_split_v1/rm70_published_split_observer_v1.py', '1-37'),
 'role_contracts': (E1/'ROLE_CONTRACTS.json', '234-255;490-511;743-764;998-1015'),
 'e1_endpoint': (E1/'e1_endpoint_predicate.py', '1-31'),
 'e1_worker': (E1/'e1_parallel_worker_safe.py', '23-42;51-106'),
 'e1_factories': (E1/'e1_route80_factories.py', '50-105;149-201;240-291'),
 'curb878_original': (REF/'CURB878_PREDICATE__review_curb878_actual_physical_source_route_CPU.py', '15-18;35-46'),
 'curb113_original': (REF/'CURB113_PREDICATE__review_curb113_actual_physical_source_route_CPU.py', '1-51'),
 's135_original': (REF/'SLOPE135_PREDICATE__review_slope135_actual.py', '6-30;64-65'),
 's135_scope_decision': (REF/'SLOPE135_ACCEPTED__SLOPE135_COMPLETE_SCOPE_DECISION.json', '48-73'),
 'e3_phase': (E3/'e3_public_recovery_phase_v1.py', '3-19'),
 'e3_runtime': (E3/'e3_recovery_runtime_v1.py', '9-25;39-66'),
 'e3_recipe_geometry': (E3/'e3_reset_bank_cache_v1.py', '34-48;94-101'),
 's50_axis': (S50/'producer/independent_expert_axis_v1.py', '4-43'),
 's50_geometry': (S50/'runtime/isaac/mod4/slope5_geometry.py', '1-39'),
 's50_retention': (S50/'runtime/isaac/mod4/slope5_retention_runtime.py', '1-19'),
 's50_trace': (S50/'runtime/isaac/mod4/retention_learning_env.py', '6-21'),
 's50_own_metadata': (BASE/'E1_three_variants_GPU_actual_v1/SLOPE_INDEPENDENT50_ACTUAL_TYPED_SOURCE_V1/E1_CANONICAL_SOURCE_METADATA.json', '108-120'),
 'pair1_assessor': (PT/'assess_pair1_retention_closed_metadata_v1.py', '15-37'),
 'pair2_assessor': (PT/'source_assess_pair2_v1/assess_pair2_retention_closed_metadata_v1.py', '17-23;49-74'),
 'pair3_assessor': (PT/'source_assess_pair3_v1/assess_pair3_retention_closed_metadata_v1.py', '16-44;69-90'),
 'pair4_assessor_v4': (PT/'source_assess_pair4_v4/assess_pair4_retention_closed_metadata_v4.py', '15-16;29-114'),
 'published_v8': (BASE/'reports/NINE_V8_COMPACT_FIRSTHAND_SKILL_FACTS.json', '1-140'),
}

def refs(*ids):
    return list(ids)

ROLE_ORDER = ['E0', 'E2', 'E3', 'W35', 'CURB_PROTECTED878', 'CURB_INDEPENDENT113', 'SLOPE135', 'SLOPE_INDEPENDENT50']

contract = {
 'schema': 'mod4v1.eight_experts.original_acceptance_contract.source.v1',
 'status': 'SOURCE_ONLY_NO_NEW_PHYSICAL_RESULTS_NO_90_PERCENT_CLAIM',
 'role_order': ROLE_ORDER,
 'excluded_roles': ['H1'],
 'capability_selection': {'available_skills': ['diagnose-windows-sandbox-acl', 'office', 'office-docx', 'office-export-pdf', 'office-pptx', 'office-recalculate', 'office-render', 'office-xlsx'], 'matching_skill': None, 'host_connector_directory_checked': True, 'matching_RL_MCP_found': False, 'method': 'Local FS source/published metadata + optional stdlib CPU synthetic tests'},
 'authority': {'parent_owns': ['two-GPU resources', 'original canonical budget owner', 'all actual policy/WM training', 'future physical validation', 'model choice'], 'this_review_owns': ['new local SOURCE_ONLY files only'], 'existing_consumer_source_modified': False, 'task_artifact_reads_forbidden': ['PT/checkpoints', 'old raw trajectories', 'NPZ', 'JSONL', 'SSH', 'SDK execution', 'GPU', 'C: task files', 'Git'], 'no_runtime_source_module_imports': True},
 'new_user_target_not_an_old_graduation_rule': {
  'intermediate_point_target': 0.80, 'final_point_target': 0.90,
  'target_application': 'Apply only as a separately named NEW USER outer reporting target to unchanged, source-proven atomic predicates and predeclared necessary groups. No historical aggregate graduation rule is retroactively invented.',
  'joint_eight_expert_status': 'PENDING_NOT_MEASURED',
  'actual_new_rates': None,
  'no_macro_pooling': 'Eight experts and each required group must be shown separately; easy standing or other roles cannot offset moving/rescue/ascending failures.',
  'training_receipts': 'Parent must prove at least several thousand actual policy optimization updates per expert. Suggested scheduling floor 3000 is a plan only, not a result. WM-only optimization, rollouts, minibatches, old PPO20 and source saved-iteration arithmetic do not satisfy it.',
  'source_gap_behavior': 'Keep predicate/rate null when the original binary rule is absent or reference/getter/cohort is unvalidated. Do not replace it with reward, MAE, no-fall, current boundary counts or WM predicted success.'
 },
 'denominator_policy': {
  'source_native_first': 'Retain the exact source denominator and its incomplete/terminal categories; never silently turn an incomplete into source false or source true.',
  'fixed_cohort_roles': 'For endpoint/rescue cohorts, all predeclared eligible initial environments remain in denominator. No credit or incomplete observation yields zero numerator; missing evidence remains unknown, not success. E3 normal recipe12 is not eligible rescue.',
  'event_roles': 'E2 denominator is every sampled complete signed2pi event, including term/timeout-at-complete false events. W35 denominator is every natural complete nonterminal command interval; partial/reset/window-ended/start-unobserved segments are outside this conditional denominator and MUST be reported separately.',
  'anti_survivor_outer_summary': 'If a NEW USER all-started-cohort lower bound is wanted, preregister exposure/attempt units before any policy outcome. Report success/(success+source_false+incomplete+unknown) with mutually exclusive outcome bins only, separately labelled conservative attempt credit, never call it the original complete-event rate. Do not count zero-control rows as attempts, double count split segments, or infer missing attempts from environment-controls.',
  'coverage_gate': 'No final 90 assertion from conditional event rates alone with unknown/missing exposure. Source-unit ledger + group exposures + censored fractions are required. New aggregation status is not original historical graduation.',
  'missing_group': 'No exposure or absent predicate is pending, not 0/0=100%; group denominator may be 0 but rate is null.',
  'ordinary_vs_truncation': 'Ordinary/integrity reasons and declared rough_route_boundary/time_out are separate. Boundary/timeout never relabelled as falls. No cross-reset stitching.',
  'technical_incompleteness': 'Capacity error, retention-limited producer, missing ticks, unknown reset, missing fields or unvalidated coordinate point invalidate the evidence scope; do not prune bad rows and publish a rate.'
 },
 'training_masks_and_getter_rules': [
  {'id': 'episode_gradient', 'rule': 'Terminal transition reward remains a real transition; stop recurrent/BPTT gradient and sequence joins at ANY reset/terminated/truncated/UID-incompatible gap. Bootstrap only under original algorithm semantics using real pre-reset terminal state, never autoreset observation. Episode UID is part of every acceptance unit.'},
  {'id': 'e3_soft_mask', 'rule': 'E3 bad_orientation/base_contact are already soft-masked for recipe!=12 and age<300. Use actual original tm.terminated/time_outs for trajectory done. recovery_original_soft flags remain diagnostics, not invented resets/done. Height-family masked rewards are also source behavior.'},
  {'id': 'e3_credit_mask', 'rule': 'Recovery score is cumulative recovery.credited AND initial first_episode_live, not recovery.delta (which includes peak-upright increments). Exclude recipe12. Capture before first reset; age100Hz+=2 at each50Hz control.'},
  {'id': 'coordinate_phase', 'rule': 'begin and pre-reset terminal must sample the same declared physical reference point after exactly8 physical substeps, heading and position at consistent phase; validate root-link vs root-COM and quaternion convention independently in parent runtime. Do not presume root_pos_w and frame[root] semantics match.'},
  {'id': 'no_tuning_metric', 'rule': 'E2/W35 existing world getter gaps are not evidence for changing .5, .05, .2, max(.03,.1v), acceleration cap, x8 scaling or swapping in body diagnostics. Preserve old observer/predicate, add provenance-bound future observation adapter only after validation.'},
  {'id': 'boundary_domains', 'rule': 'Historical E0/E2 .002 closure/.05 mimic and approved MOD4v1 .01/.01 are distinct physical gates. Keep original-prefix cutoff/censoring for historical comparison; do not hotpatch actual done to emulate old gates. Current gate-first censor is incomplete, old gate-first prefix is retained; no stitching.'},
 ],
 'experts': {},
}

contract['experts']['E0'] = {
 'skill_scope': 'Original flat standing, signed straight, pure spin, transition spin and moving-world profiles; 20s1000policy controls.',
 'original_atomic_predicate': None,
 'original_metric_not_a_pass': 'E0Book reports per-profile body-forward/yaw/height MAE, live sampled signed2pi windows and moving projected progress; summary explicitly no_graduation_threshold_invented. N80 worker adds full-window vx/vy/yaw MAE, not per-command Boolean skill success.',
 'original_denominator_unit': {'diagnostics': 'per phase/profile population_controls, unique exposed env reported separately', 'cycle': 'same commandUID/profile/episode/phase live sampled window; not all moving elapsed time', 'commands': 'resample-to-resample full command instances separate from reset-ended, left/right-censored and zero-control rows', 'binary_success_denominator': None},
 'necessary_groups': ['standing', 'straight_negative', 'straight_positive', 'straight_zero_if_naturally_exposed_else_pending', 'pure_negative', 'pure_positive', 'transition_initial_negative_all_12s_bins', 'transition_initial_positive_all_12s_bins', 'moving_yaw_negative_abs1_to2', 'moving_yaw_positive_abs1_to2'],
 'failure_incomplete_denominator': 'Keep ordinary flags, reset-ended and window-ended commands distinct. Zero-control rows have no positive evidence. No binary success numerator/90% rate is defined by the joined source.',
 'published_baseline_not_new_result': 'Posttrain old finite20 selected by all3 body MAE nonworse+ordinary failure nonincrease; no original fullskill pass.',
 'target90_measurability': 'SOURCE_BINARY_PREDICATE_GAP',
 'gaps': ['Original binary pass threshold and accepted cohort for all original profiles are not joined.', 'V8 only reports overall body diagnostics, not original profile/complete-command accepted booleans.', 'Transition all12s coverage and continuous zero atom remain exposure issues, not automatic failures.'],
 'exact_future_getter_or_observer_points': [{'source': 'e0_metrics', 'function': 'E0Panel.begin/terminal/finish', 'lines': '161-181;199-206', 'action': 'Reuse original profile classification and complete-instance UID book, publish bounded aggregate counters in the same source writer. Obtain original acceptance authority before any binary label; never borrow E2 thresholds.'}, {'source': 'five_worker', 'function': 'terminal/skill', 'lines': '80-84;107', 'action': 'Current full-window integrated body errors are diagnostic only; do not use this path as success rate. Match old/current boundary domains separately.'}],
 'source_refs': refs('e0_catalog', 'e0_metrics', 'five_worker', 'pair1_assessor', 'historical_matrix_summary'),
}

contract['experts']['E2'] = {
 'skill_scope': 'Own E2_WORLD_MOVING_SIGNED4; 24s1200 controls, sampled same-UID signed2pi world cycles.',
 'original_atomic_predicate': {'selection_mask': 'key in {8,9}; original moving flag and signed_yaw sign', 'span_identity': ['same profile', 'episode_uid', 'command_uid', 'world_direction', 'signed_yaw sign', 'consecutive controls / exactly8 substeps each'], 'completion': 'actual_signed_yaw * sign >= 2*pi; sampled endpoint, no interpolation, overshoot not carried', 'joint': 'seconds>0 AND complete AND NOT terminated AND NOT truncated AND abs(along_speed-.5)<=.05 AND abs(cross_speed)<=.05 AND abs((actual_turn-commanded_yaw_integral)/seconds)<=.2', 'point_or_phase_rule': 'Warmup/steady crossing is recorded, NOT a new span break; original direction projection for displacement.'},
 'original_denominator_unit': 'Every complete sampled signed2pi event (repeated cycles per env possible), NOT initial80envs and NOT environment-controls.',
 'necessary_groups': ['moving_yaw_minus4 (profile8)', 'moving_yaw_plus4 (profile9)'],
 'failure_incomplete_denominator': 'term/timeout on complete endpoint stays in complete denominator and source false; term/reset/resample/direction/sign/UID change/window-end before2pi is incomplete, outside original complete denominator and explicitly counted separately. Parent must preregister an all-started attempt ledger before any conservative outer90 lower bound.',
 'published_baseline_not_new_result': {'source_v8': {'complete': 187, 'false': 187, 'true': 0, 'incomplete': 43}, 'posttrain20_complete_true': '0/187; not graduation'},
 'target90_measurability': 'ATOMIC_RULE_JOINED_GETTER_PHASE_REFERENCE_AND_GROUP_COVERAGE_PENDING',
 'gaps': ['No original overall graduation/cohort rule, but the atomic numeric rule IS present (do not repeat old18s gap as if24s lacks numbers).', 'Reference point / getter cache phase independently unvalidated.', 'Published counters lack per-sign initial-exposure/attempt distributions and multi-seed coverage.', 'Producer old b3 label is not actual candidate actor identity.'],
 'exact_future_getter_or_observer_points': [{'source': 'e2_bridge', 'function': 'E2FreshCycleBridge.begin/terminal', 'lines': '15-18', 'action': 'Replace only future observation adapter after validation: before_xy/root_pos_w+heading at begin and after position/heading at termination before autoreset must be same point and8physics later. Bind point name, root-link/COM transform, quaternion ordering, tick stamps; no source command/RNG/action writes.'}, {'source': 'e2_cycles', 'function': 'E2Cycles213.begin/observe/emit/finish', 'lines': '44-127', 'action': 'Keep predicate/UID logic exact; append per-sign complete/false/incomplete+close reason/attempt identity in same writer, retain phase-cross flag, use actual actor SHA as separate provenance field.'}],
 'source_refs': refs('e2_bridge', 'e2_cycles', 'e2_catalog', 'five_worker', 'pair2_assessor', 'published_v8', 'historical_matrix_summary'),
}

contract['experts']['E3'] = {
 'skill_scope': 'Original fixed13-recipe recovery owner: recipe0..5 roll and6..11 pitch at angles[-90,-60,-30,30,60,90]deg; recipe12 normal. 3.2s160controls observation.',
 'original_atomic_predicate': {'request': '(recipe!=12) & (age<300)', 'good': 'gravity_z < -0.984807753 AND norm(root_state_w velocity[7:10]) < .03 AND norm(angular_velocity[10:13]) < .2 AND request', 'stable_update': 'stable = good ? stable+2 : 0; age +=2 each50Hz control; event=(stable>=50)&~credited; credited|=event', 'success_field': 'first_episode_original_stable_credit := ever(recovery.credited & first_episode_live)', 'not_success_field': 'delta is peak-upright change PLUS event, not a binary credit', 'duration': '50 public100Hz ticks=.5s=25policycontrols; request300=3s'},
 'original_denominator_unit': 'One initial rescue environment / recipe; 74 requested initial envs for N80, normal6 excluded. Later reset episodes do not create extra first-episode successes.',
 'necessary_groups': ['recipe'+str(i) for i in range(12)],
 'normal_retention_group': {'recipe': 12, 'N80_initial_envs': 6, 'scored_as_rescue': False, 'requirement': 'Report original ordinary flags separately; no added rescue credit from normal standing.'},
 'failure_incomplete_denominator': 'All initial rescue74 remain denominator. No credit before first episode ends/request expires is zero success. Early reset/timeout/missing observation remains failed-or-incomplete/unknown with zero numerator, never delete env or stitch to later credit. Original source separately retains first_episode_physical_terminated; credited prefix may coexist with later termination and is not silently revoked.',
 'published_baseline_not_new_result': 'Original posttrain firstepisodecredit0/74 ->1/74, ordinary terminal events25->27; mother retained, no graduation.',
 'target90_measurability': 'ORIGINAL_OWNER_CREDIT_JOINED_NOT_GLOBAL_FULLSKILL_RULE',
 'gaps': ['Multi-seed per-recipe sample sizes and actual pre-reset first-episode evidence required.', 'Original complete global E3 graduation authority not joined; user90 is separately labelled owner-credit target.', 'Recovery original soft flags and actual masked done differ.'],
 'exact_future_getter_or_observer_points': [{'source': 'e3_runtime', 'function': 'masked_termination/termination/place_declared_fall/step', 'lines': '10-25;39-66', 'action': 'Keep source soft masks, stable/age clocks, zero commands and fixed bank geometry. Read credited after original RecoveryEnv termination update but before reset; use actual masked terminal vectors, not recovery_original_soft.'}, {'source': 'five_worker', 'function': 'terminal and first_recipe reporting', 'lines': '67-68;85-96;108-112', 'action': 'Publish per-initial-env recipe/episode/firstcredit/firstterm/firsttimeout/requestdeadline and missing-observation counts in the same observer writer; never infer from delta.'}],
 'source_refs': refs('e3_phase', 'e3_runtime', 'e3_recipe_geometry', 'five_worker', 'pair3_assessor'),
}

contract['experts']['W35'] = {
 'human_alias': 'W25 confirmed as W35',
 'skill_scope': 'Original RM70 natural BODY command intervals,32s1600controls; not a catalog goal task and not an E2 world2pi task.',
 'original_atomic_predicate': {'fixed_axis': 'original sampled _command_heading + pi if BODY vx<0; NOT random unused cmd.direction', 'nominal_v': 'abs(sampled BODY vx)', 'kinematic': 'abs(along_speed-v)<=max(.03,.1*v) AND abs(cross_speed)<=max(.03,.1*v) AND abs((turn-integral_commanded_yaw)/seconds)<=.2', 'complete': 'natural outer resample timer<=0 AND start_observed AND NOT terminated AND NOT truncated, with count>0; source parameter/episode changes close a partial segment', 'accepted': 'natural_complete_nonterminal_interval & original_kinematic_bounds_met', 'grouping': 'original standing Boolean at open/row write; no speed-derived proxy'},
 'original_denominator_unit': 'Natural complete nonterminal same-UID command intervals, separately moving and standing. Different from initial80 or all route episodes.',
 'necessary_groups': ['moving_complete', 'standing_complete'],
 'failure_incomplete_denominator': 'Every natural complete interval contributes true/false; partial, unknown start, reset, terminal, timeout, source-parameter break and window-end remain outside the original conditional denominator but retain explicit group/reason counts. A declared attempt ledger is needed for any outer all-started90 measure; do not drop these silently.',
 'published_baseline_not_new_result': {'old': {'moving_true': 18, 'moving_complete': 61, 'standing_true': 26, 'standing_complete': 26, 'all_complete': 87}, 'posttrain20': {'moving_true': 18, 'moving_complete': 64, 'standing_true': 26, 'standing_complete': 26, 'all_complete': 90}, 'warning': '44/87 or44/90 is not moving skill success; numerator equality does not prove matched UID cohort or unchanged denominator.'},
 'target90_measurability': 'ATOMIC_RULE_JOINED_REFERENCE_PHASE_AND_EXPOSURE_PENDING',
 'gaps': ['Mixed root_pos_w begin versus frame[root] terminal needs same-point/linkCOM/cachephase validation.', 'Natural resets make command populations policy-dependent; matched count alone is not matched UID.', 'Original full RM70/high-speed or flat/world/pure/transition expert acceptance not proved by this window.', 'catalog goal0 is observer-only, not a new failure gate.'],
 'exact_future_getter_or_observer_points': [{'source': 'five_worker', 'function': 'book.begin and terminal(book.terminal)', 'lines': '76;103', 'action': 'Verify before root_pos_w/heading and pre-reset env._e1_pre_reset_frame[root] share point and phase; add provenance-bound future getter adapter only, no acceleration .04 cap orx8 correction.'}, {'source': 'w35_intervals', 'function': 'open/begin/terminal/close', 'lines': '76-107;108-170', 'action': 'Keep sampled axis, natural timer, source_E1_episode/UID and original boundaries. Publish original standing/complete/accepted split and partial-reason totals in same writer. Preserve original consumers and oldV8.'}, {'source': 'pair4_assessor_v4', 'function': 'compare_w35', 'lines': '61-81', 'action': 'Future strict scope may bind command_uid_population_SHA, original_acceptance_predicate_SHA, reference_frame_and_sample_phase_validated and original_interval_boundaries_unchanged; these are missing evidence, not booleans to fabricate.'}],
 'source_refs': refs('w35_intervals', 'w35_split_observer', 'five_worker', 'pair4_assessor_v4', 'final_report'),
}

def endpoint_role(role, edge, geometry, baseline, factory_lines, original_id):
 return {
  'skill_scope': geometry + '; own mirrored80 cohort,15s750policycontrols, 6000physical/1500feedback.',
  'original_atomic_predicate': {'canonical_wheel_coordinate': '(body_link_pos_w[wheel,x]-own_tile_center_x)*orientation', 'ascending_before': 'max(two_wheel_u)<-'+str(edge), 'ascending_after': 'min(two_wheel_u)>'+str(edge), 'descending_before': 'min(two_wheel_u)>'+str(edge), 'descending_after': 'max(two_wheel_u)<-'+str(edge), 'ordered_contact': 'Within ONE episode and before first ordinary failure: before and after at controls b<a, with BOTH wheel control-mean positive vertical forces>1N at both endpoints.', 'contact_integration': 'sum8(max(Fz,0))*.0025/.02>1N; not force norm, not a single physics callback, not actor-rate assumed100Hz', 'stand': 'No crossing required; source ordinary-free initial standing cohort reported separately, not counted as traversal.', 'late_failure_semantics': 'EndpointPredicate retains a successful prefix before later ordinary failure; report later full-window failure separately, do not rewrite the original prefix predicate.'},
  'original_denominator_unit': {'ascending': '27 initial envs; all failed/incomplete included', 'descending': '27 initial envs; all failed/incomplete included', 'stand': '26 initial envs, separate original standing-retention diagnostic'},
  'necessary_groups': ['ascending', 'descending', 'stand_retention_reported_separately'],
  'geometry_requirements': {'mirrors': '40+orientation and40-orientation; preserve source group placement and distinct tile assignments', 'manual_commands': '[.3,-.3,0][env%3]*orientation BODYvx; vy/yaw=0; own nominalheight.25', 'fixed_window': '15s, not native24/.48s', 'not_other_terrain': 'No RM70 height/stairs/hardware/general SLOPE qualification inferred.'},
  'failure_incomplete_denominator': 'All assigned27/27 stay in their group denominator, no valid endpoint/contact gives zero numerator. Only same-episode segments before firstordinary failure can contribute; declared truncation partitions episodes and never allows stitching. Window end with no accepted endpoint is incomplete, not removed. Standing26 not traversals.',
  'published_baseline_not_new_result': baseline,
  'target90_measurability': 'ORIGINAL_SCOPED_ENDPOINT_CONTACT_RULE_JOINED_NOT_FULL_EXPERT_GRADUATION',
  'gaps': ['Independent multi-seed geometry/group evidence and exact actor/eval identity needed.', 'This prefix traversal rule is not complete broad-expert, hardware or permanent retention graduation.'],
  'exact_future_getter_or_observer_points': [{'source': 'e1_worker', 'function': '_run_loop.terminal and EndpointPredicate.observe', 'lines': '62-64;87-97', 'action': 'Use pre-reset body_link_pos_w named left/right wheels plus independently integrated8substep positiveFz. Keep actual episode assignment and firstordinary cutoff; variable COM_link_pos is a historical label, not permission to swap link point to COM.'}, {'source': 'e1_factories', 'function': 'own _factory_'+role.lower(), 'lines': factory_lines, 'action': 'Keep own geometry, starts,40/40mirror, group%3, commands and height. Bind authored mesh query receipt, not boundary/no-fall proxy.'}],
  'source_refs': refs('e1_endpoint','e1_worker','e1_factories',original_id,'role_contracts','final_report'),
 }

contract['experts']['CURB_PROTECTED878'] = endpoint_role('CURB_PROTECTED878',.275,'Own vertical20mm curb,150mmstrip,200mm beyond-support endpoints', 'Up22/27->26/27; down27/27 and standing26/26 retained in published posttrain20.', '50-105','curb878_original')
contract['experts']['CURB_INDEPENDENT113'] = endpoint_role('CURB_INDEPENDENT113',.275,'Own independent113 vertical20mm curb,150mmstrip,200mm beyond-support endpoints', 'Up22/27 unchanged; down27/27 and standing26/26 retained in published posttrain20.', '149-201','curb113_original')
contract['experts']['SLOPE135'] = endpoint_role('SLOPE135',1.2,'Own continuous5degree2m ramp,[-1,+1]m ramp and200mm beyond flat supports, no vertical riser', 'Own up25/27->27/27; down27/27 and standing26/26 retained. Historical scoped5degree accepted, not fullSLOPE.', '240-286','s135_original')
contract['experts']['SLOPE135']['source_refs'].append('s135_scope_decision')

contract['experts']['SLOPE_INDEPENDENT50'] = {
 'skill_scope': 'Independent later50-update SLOPE5 full_ramp_and_both_flat_supports OWN training axis; normal natural commands/DR/RNG.20s1000controls.',
 'original_atomic_predicate': None,
 'source_rules_found_not_acceptance': {'geometry': 'Own slope5_profile5deg/2m mirrored continuous ramp', 'axis_target': 'retention_family code4 random_uniform_for_rm only; own40x40tile-center layout', 'boundary': 'For target-family only: abs(root_xy-tile_center).x>3.5 OR y>3; original other-family boundary unchanged; rough_route_boundary.time_out=True', 'episode_time_limit': '20s', 'trace': 'pre-reset command prefixes with BODY command/mode/termination; complete_cycles_not_claimed_from_truncated_prefixes=True'},
 'original_denominator_unit': None,
 'necessary_groups': ['ORIGINAL_ACCEPTED_FULLRAMP_COHORT_NOT_JOINED', 'preserve targetfamily vs retained otherfamilies', 'bothmirror/ascending/descending and supports to be joined from OWN original authority, not inherited fromS135'],
 'failure_incomplete_denominator': 'Current boundary/timeouts/ordinary counts are descriptive events, not a denominator for a missing accepted route Boolean. Keep all counts and missing-cohort status; no invented success/(80-boundaries). Future real original accepted units must retain failed/incomplete cohort members.',
 'published_baseline_not_new_result': 'Ownaxis ordinaryfail0; boundary41->46 and timeout47->43 after20PPO. This is not a fullramp acceptance result.',
 'target90_measurability': 'SOURCE_BINARY_PREDICATE_AND_ACCEPTED_COHORT_GAP',
 'gaps': ['No OWN original complete accepted fullramp predicate/cohort found in examined source/ROLE_CONTRACTS/published metadata.', 'Axis, geometry and widerboundary are executable training rules but contain no ordered completion/contact/velocity acceptance predicate.', 'BorrowingS135edge1.2,27/27 or a new boundary/no-fall rule would change task acceptance.'],
 'exact_future_getter_or_observer_points': [{'source': 's50_axis', 'function': 'configure_route/cache/layout/bind_after_restore', 'lines': '4-43', 'action': 'Preserve exact target mask, tile centers and own axis state. Join original independent_expert_task_contract/scope authority via already-published text if available; do not reopen checkpoint to infer a pass rule.'}, {'source': 'e1_worker', 'function': 'build_slope50_training_axis_factory and _run_loop descriptive branch', 'lines': '23-42;103-105', 'action': 'Explicitly retains acceptedcohortpredicateGAP. Once original OWN predicate is located, future observation-only adapter attaches to pre-reset frame/body_link_pos/Fz/UID source, not EndpointPredicate(1.2) unless original own authority proves that same rule.'}, {'source': 's50_trace', 'function': 'RetentionLearningEnv.step', 'lines': '9-21', 'action': 'Already available pre-reset root/command/mode/terminated/truncated can support exposure accounting only, not fullramp success by themselves.'}],
 'lookup_boundary': 'Searched own producer source, own slope geometry/retention/axis/trace, own canonical metadata, ROLE_CONTRACTS and posttrain assessor. Local F source join only; no C/raw/PT/SSH. Absence conclusion bounded to this examined set, not all remote or historic files.',
 'source_refs': refs('s50_axis','s50_geometry','s50_retention','s50_trace','s50_own_metadata','role_contracts','e1_worker','pair4_assessor_v4'),
}

contract['validation_plan_suggestion_not_executed'] = {
 'purpose': 'Future parent-owned true physical frozen validation of actual trained policy; NOT WM imagined rollout acceptance.',
 'policy_updates': 'Per expert at least several thousand real BPTT policy optimizer updates, independently identified from model-only updates, save actual update counters and fullstate provenance; none verified here.',
 'development_vs_final': 'Use separate development cohorts for tuning; pin final policy SHA BEFORE final held-out seeds. Do not select checkpoint on repeated final-cohort outcomes.',
 'seed_suggestion': {'development': [20260928,20261002,20261102], 'final_held_out': [20261103,20261107,20261111,20261117,20261123,20261129,20261201,20261207,20261211,20261213], 'numbers_are_seed_values_not_execution_dates': True, 'planned_runs_executed': 0},
 'per_seed': 'Keep own N80 setup/windows/clocks/DR and original command sampling; E3recipe74+6, E1groups27/27/26 and40/40mirrors. Additional protocols only separately labelled, not replacing original.',
 'required_outputs': ['per expert/seed/necessary group true,false,incomplete,unknown + source-native unit denominator', 'event unit UID/episode/close reason provenance and source predicate SHA', 'freshD0D7 before/after actual parameters metadata', 'actor SHA + actual learnedSTD action mode/clip identity and controls/physics/feedback counts', 'same reference point/cachephase proof forE2/W35', 'ordinary/truncation and integrity errors separately', 'median/minimum/per-seed and micro/macro group estimates; Wilson intervals with explicit cluster caveat'],
 'statistics': 'User80/90 are point targets, not historical source thresholds. Report binomial Wilson95% as descriptive uncertainty plus between-seed variation / seed-cluster interval where possible; repeated command events in same env are correlated, so do not call event-count Wilson an independent-env proof. If asserting population>=90% with confidence, explicitly preregister that stronger lower-bound rule and obtain sufficient independent seeds, rather than retroactively interpreting90%point asconfidence.',
 'necessary_group_rule_suggestion': 'No role or required moving/sign/rescue/route-direction group may be hidden by a pooled mean. Intermediate80 and final90 are evaluated separately. Standing is not crossing. Unexposed groups remain pending. E0/S50 stay pending binary authority until original rule is joined.',
 'finite_scope': 'No actual evaluation, newphysicalpurpose, ownership action or resource/canonical access initiated by this review.',
}

contract['lookup_notes'] = [
 {'attempt': 1, 'query': 'ROOT/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102', 'outcome': 'Missing at ROOT; corrected to BASE/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102 from final report. No source modified.'},
 {'attempt': 2, 'query': 'glob *Registry*v12*', 'outcome': 'Case/path pattern returned none; report provided exact EXPERT_NORMALIZATION_REGISTRY_v12.json. Read exact text.'},
 {'attempt': 3, 'query': 'staged_sources/E2_MOD4V1_SOURCE_FINAL', 'outcome': 'Missing; located E2_MOD4V1_SOURCE_V1/train entry. Its imported e2_h1_flat_environment_v1 implementation was not present in that local tree.'},
 {'attempt': 4, 'query': 'F discovery copy of e2_h1_flat_environment_v1.py', 'outcome': 'Read empty0-line text; not used as authoritative source. Getter independent validation remains a real gap.'},
 {'attempt': 5, 'query': 'observer_w35_split_v1/rm70_intervals227.py', 'outcome': 'Missing basename; glob located rm70_intervals227_split_metadata_v1.py + split observer. OriginalV8 interval source and pair4V4 consumed for contract; no old files edited.'},
 {'attempt': 6, 'query': 'S50 own producer acceptance/full_ramp source scan', 'outcome': 'Only fullramp training-axis declaration found, no own accepted fullroute predicate. Geometry/retention/trace and role metadata corroborate descriptive-only status; source search bounds retained.'},
]

manifest = {}
for key, (path, lines) in SOURCES.items():
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(ROOT) or resolved.suffix.lower() not in {'.py','.md','.json'}:
        raise ValueError('Source allowlist escaped F workspace or text schema: '+str(path))
    raw = resolved.read_bytes()
    manifest[key] = {'path': str(resolved), 'bytes':len(raw), 'SHA256':hashlib.sha256(raw).hexdigest(), 'reviewed_line_ranges':lines, 'source_or_published_metadata_only': True}
contract['sources'] = manifest
assert list(contract['experts']) == ROLE_ORDER
assert len(contract['experts']) == 8 and 'H1' not in contract['experts']
assert contract['actual_new_rates'] is None if 'actual_new_rates' in contract else True
p = OUT/'EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json'
with p.open('x', encoding='utf-8') as f:
    json.dump(contract, f, ensure_ascii=False, indent=2, allow_nan=False)
    f.write('\n')
print(str(p))
print(json.dumps({'status':contract['status'], 'experts':len(contract['experts']), 'text_source_refs':len(manifest), 'actual_physical_results_generated':0}, ensure_ascii=False))
