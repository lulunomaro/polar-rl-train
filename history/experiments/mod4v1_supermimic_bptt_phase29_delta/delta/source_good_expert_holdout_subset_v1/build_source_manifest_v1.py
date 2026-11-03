"""Build small SOURCE metadata only; no stage/executor and no native/model/raw IO.
Reads explicitly indexed Python/JSON/text and writes only NEW metadata here.
"""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
R = HERE.parent
T = R.parent / 'mod4v1_experts_fulldr_rm70_20261101'
OLD = R / 'source_frozen_embedded_teacher_native_v1'
E1 = T / 'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR'
N80 = T / 'NINE_N80_PARALLEL_SOURCE_V8'
PLAN = T / 'reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json'
ROLES = ('E3', 'W35', 'CURB_INDEPENDENT113', 'CURB_PROTECTED878', 'SLOPE135', 'SLOPE_INDEPENDENT50', 'E0', 'E2')
REQUESTED = ('CURB_PROTECTED878', 'SLOPE135')
CONTROLS = dict(E0=1000, E2=1200, E3=160, W35=1600, CURB_PROTECTED878=750, CURB_INDEPENDENT113=750, SLOPE135=750, SLOPE_INDEPENDENT50=1000)


def raw(path):
    path = Path(path)
    assert path.suffix.lower() in ('.py', '.json', '.md'), 'SOURCE text only'
    return path.read_bytes()


def identity(path):
    value = raw(path)
    if Path(path).suffix == '.py':
        ast.parse(value)
    return dict(path=str(path), bytes=len(value), SHA256=hashlib.sha256(value).hexdigest())


def put(name, value):
    path = HERE / name
    value = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    if path.exists():
        assert path.read_text(encoding='utf-8') == value, 'existing source metadata differs; review targeted edits'
        return
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(value)


def make_index():
    before = json.loads(raw(OLD / 'EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json'))
    replacements = {
        'single_gpu_e3_w35_embedded_teacher_parent_v1.py': ('single_gpu_good_expert_holdout_parent_v1.py', HERE / 'single_gpu_good_expert_holdout_parent_v1.py'),
        'frozen_embedded_teacher_native_runtime_v1.py': ('good_expert_holdout_runtime_v1.py', HERE / 'good_expert_holdout_runtime_v1.py'),
        'worker_sources/e1/e1_parallel_worker_safe.py': ('worker_sources/e1/e1_parallel_worker_safe.py', HERE / 'e1_good_expert_holdout_worker_v1.py'),
        'worker_sources/e1/e1_fresh_runtime_bridge.py': ('worker_sources/e1/e1_fresh_runtime_bridge.py', HERE / 'e1_good_expert_holdout_bridge_v1.py'),
    }
    entries = []
    for row in before['entries']:
        original = identity(Path(row['path']))
        assert (original['bytes'], original['SHA256']) == (row['bytes'], row['SHA256']), 'original sealed source changed'
        if row['relative'] == 'worker_sources/parent/worker_five_original_n80.py':
            continue  # No formal E0/E2/E3/W35 worker is the requested E1 entry.
        relative, path = replacements.get(row['relative'], (row['relative'], Path(row['path'])))
        entries.append(dict(relative=relative, **identity(path)))
    for relative, path in (
        ('worker_sources/e1/e1_route80_factories.py', HERE / 'e1_good_expert_holdout_factories_v1.py'),
        ('worker_sources/e1/worker_curb878_n80.py', E1 / 'worker_curb878_n80.py'),
        ('worker_sources/e1/worker_slope135_n80.py', E1 / 'worker_slope135_n80.py'),
        ('worker_sources/e1/e1_endpoint_predicate.py', E1 / 'e1_endpoint_predicate.py'),
        ('worker_sources/e1/ROLE_CONTRACTS.json', E1 / 'ROLE_CONTRACTS.json'),
    ):
        entries.append(dict(relative=relative, **identity(path)))
    assert len(entries) == len({row['relative'] for row in entries}) == 20
    by = {row['relative']: row for row in entries}
    assert by['a1_frozen_eval_runtime_v2.py']['SHA256'] == '7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e'
    assert by['resume_runtime_contracts_v3.py']['SHA256'] == 'dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7'
    original_plan = json.loads(raw(PLAN))
    inherited = []
    for row in original_plan['worker_files']:
        relative = row['relative']
        if relative.startswith('worker_sources/parent/'):
            path = N80 / Path(relative).name
        elif relative.startswith('worker_sources/e1/'):
            path = E1 / Path(relative).name
        else:
            continue  # Asset files are metadata-only requirements, never read here.
        info = identity(path)
        assert (info['bytes'], info['SHA256']) == (row['bytes'], row['SHA']), 'original V8 worker source pin differs: ' + relative
        inherited.append(dict(relative=relative, overwritten_by_NEW_overlay=relative in by, **info))
    return dict(kind='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_C878_S135_INDEX_V1', enabled=False, staged=False, dispatched=False,
        native_measurement=False, overlay_entries=entries, inherited_original_worker_source_entries=inherited,
        provenance=[identity(path) for path in (
            OLD / 'EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json',
            R / 'source_stage_a1_microbatch_eval_v2/MICROBATCH_STAGE_INDEX_V2.json',
            R / 'source_a1_frozen_eval_integration_v2/FROZEN_EVAL_SEALED_SOURCE_INDEX_V2.json',
            N80 / 'PARENT_FIVE_SOURCE_INDEX_V8.json', PLAN)],
        original_group_id=original_plan['group_id'],
        required_original_runtime_rows=[row for row in original_plan['roles'] if row['role'] in REQUESTED],
        required_original_pinned_assets=[row for row in original_plan['worker_files'] if row['relative'].startswith('pinned_assets/')],
        full_materialization_requirements=dict(
            original_worker_sources='retain every original V8 worker source/dependency outside exact NEW overlays; not only import slices',
            runtime_rows='bind each selected task.runtime_root to its original V8 role tree and E1_CANONICAL_SOURCE_METADATA canonical role; all permitted original static banks/deps retained',
            known_factory_imports=['mod4_task', 'e1_reset_evidence_training_env', 'e1_terrain_training_health', 'e1_full_pose_reset', 'mod4v1_fresh_dr_guard', 'curb20_geometry', 'slope5_geometry', 'curb_worldmesh_query_contract_v1'],
            static_banks='retain complete original selected-role source/static-bank tree without slicing N20k histories; raw banks are not inspected/copied in this SOURCE task',
            vendor='retain full original seven-file supermimic_vendor_v2, SHA tree ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0; three pinned imports here are not the whole vendor',
            producer='bind original actual0 producer TASK/INSTALL_MANIFEST/FINAL and exact full guard sources before select_requested_roles; no metadata boolean fallback',
            physical_containment='unchanged FrozenA1CheckpointCache checks exact own physical checkpoint containment only after future original resource admission',
            ready_for_native_dispatch=False, original_runtime_tree_materialized_here=False,
            old_stage_kind_reusable=False, overlay_alone_is_complete_native_runtime=False),
        source_state=dict(resources_acquired=0, canonical_ledger_operations=0, checkpoint_opens=0, mother_checkpoint_opens=0, SDK_imports=0, parent_launches=0))


def contract():
    purposes = {str(seed): 'GOOD_EXPERT_HOLDOUT_C878_S135_SEED' + str(seed) + '_V1' for seed in (20260929, 20260930)}
    return dict(kind='SOURCE_GOOD_EXPERT_HOLDOUT_SUBSET_INTERFACE_V1', enabled=False, staged=False, dispatched=False,
        scope=dict(role_catalog=list(ROLES), requested_roles=list(REQUESTED), deferred_roles=[role for role in ROLES if role not in REQUESTED], H1='frozen_absent_not_constructed'),
        plan_kind='GOOD_EXPERT_HOLDOUT_C878_S135_PLAN_V1', task_kind='GOOD_EXPERT_HOLDOUT_C878_S135_N80_TASK_V1',
        seeds=[20260929, 20260930], distinct_purposes=purposes, published_baseline_seed=20260928,
        independent_group_per_seed=True, original_seed_reassessment_is_new_evidence=False,
        original_scope=dict(num_envs=80, controls_per_role=750, cohorts=dict(ascending=27, descending=27, stand=26),
            all_catalog_controls=CONTROLS, policy_hz=50, feedback_hz=100, physics_dt=.0025, physics_callbacks=6000, feedback_samples=1500,
            TGS=[32, 4], gas_N=400, stiffness_N_m=2000, damping_Ns_m=3., closure_m=.01, mimic_rad=.01, D0_D7='original_unchanged'),
        exact_interfaces=[
            'select_requested_roles(plan) -> [CURB_PROTECTED878_row, SLOPE135_row]',
            'make_task(role, plan, deadline, fds) -> original_task_fields_plus_seed_bound_subset',
            'wait_group_start(task, group, maximum_seconds=900) -> exact_two_member_same_seed_start',
            'build_original_route80(role, descriptor, case, identity, torch, np, wp, tensor) -> original_bundle',
            'attach_fresh_guard(env, identity, torch_module, tensor) -> original_guard_before_one_reset',
            'OriginalA1NoResetDecisionVec.step(action) -> original_observation_reward_(terminated|truncated)_extra; caller_observes_separate_true_flags',
            'evaluate_waited_eval_case(case, returncode, role_entry, group_id) -> metadata_semantic_after_actual_p_wait',
            'summarize_independent_seed_results(results) -> conditional_direction_or_standing_counts_not_native_proof'],
        future_plan_required_fields=['kind','policy_variant','batch_purpose','seed','holdout_protocol','requested_roles','deferred_roles','overall_eight_pass_rate=null','comparison=null','roles=complete8','worker_files=complete_original_plus_NEW','group_id','GPU_UUID','asset_SHA','contract_SHA','paired_reset_protocol'],
        selected_row_required_evidence=['role','controls','worker','a1_producer=actual_success_FINAL_descriptor','policy_variant','actor_semantics','actor_container_identity','original_bootstrap_teacher','producer_teacher_freeze_evidence=rederived_actual_sources'],
        original_acceptance=dict(CURB_PROTECTED878_endpoint_edge_m=.275, SLOPE135_endpoint_edge_m=1.2,
            predicate='original_e1_endpoint_predicate_unchanged', stand='existing_assessor_no_failure; crossing_not_required',
            no_new_E0_or_S50_predicates=True, new_thresholds=None),
        statistics=dict(per_seed_direction_denominators=[27,27], per_seed_standing_denominator=26,
            across_two_seeds_direction_denominator=54, across_two_seeds_standing_denominator=52,
            interval='descriptive_Wilson95_not_IID_or_cluster_adjusted_or_noninferiority', whole_skill90_claim=None, pooled_skill_rate=None, measured_new_quality=False),
        original_resource_contract=dict(private_GPU_EX=True, global_finite_EX=True, canonical_readonly=True, minimum_empty_GPU_MiB=23500,
            minimum_RAM_GiB=96, minimum_disk_GiB=25, resource_wait_seconds=1800, ready_wait_seconds=900, worker_deadline_seconds=2400,
            close='whole_original_AST', actual_p_wait_before_semantics=True, finally_wait_before_unlock=True),
        unresolved_before_materialization=['original_remote_runtime_tree_and_full_staticbanks/deps','producer_actual_TASK_INSTALL_MANIFEST_FINAL/source_bytes_at_selected_original_ownjob','new_reviewed_stage_binding_distinct_kind_not_legacy_E3_W35_stager'],
        source_templates_are_not_executable_GROUP_PLAN=True)


if __name__ == '__main__':
    put('GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json', make_index())
    put('API_CONTRACT_GOOD_EXPERT_HOLDOUT_V1.json', contract())
    print(json.dumps(dict(kind='SOURCE_METADATA_BUILT_NOT_STAGE', enabled=False, staged=False, dispatched=False)))
