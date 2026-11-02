"""Run with stdlib only. Read known .py/.json source/evidence; write child-only.
No PT path is opened, stat'ed, hashed, decoded or globbed. No task/GO is emitted.
"""
from pathlib import Path
import ast
import hashlib
import json
import sys
import traceback

B = Path(__file__).resolve().parent
T = B.parent.parent
sys.path.insert(0, str(B))
from posttrain_fullstate_common_v1 import EXPERTS, POSTTRAIN_KIND, ADMISSION_KIND, USD_SHA, CONTRACT_SHA, COMMON_RECEIPTS, LIVE_KEYS
STAGES = {'E0': 'E0_MOD4V1_SOURCE_FINAL', 'E2': 'E2_MOD4V1_SOURCE_V1', 'E3': 'E3_MOD4V1_SOURCE_FINAL'}
OLD_TRAINERS = {'E0': 'train_chassis_pd_resume_ppo.py', 'E2': 'train_E2_full_resume_v1.py', 'E3': 'train_E3_fullstate_v1.py'}
REPORT_DIR = {'E0': 'E0_a92_no_update_final_20261102_022955', 'E2': 'E2_b3_no_update_final_20261102_024838', 'E3': 'E3_1cd_no_update_final_20261102_031620'}
HELPER_FUNCTIONS = {
    'sensor_resume_contract.py': ('resume_sensor_new_episode', 'restore_sensor', 'restore_named'),
    'sensor_a0_runtime.py': ('install_sensor_save_contract', 'state'),
    'feedback_delay_checkpoint.py': ('resume_delay_new_episode', 'restore_delay_exact', 'install_delay_save_contract'),
    'action_delay_checkpoint.py': ('restore_action_before_new_episode', 'resume_action_new_episode', 'install_action_save_contract', 'append_action_state'),
    'spring_pressure_checkpoint.py': ('resume_spring_new_episode', 'install_spring_save_contract'),
    'gas_damping_checkpoint.py': ('resume_damping_new_episode', 'install_damping_save_contract'),
    'chassis_pd_checkpoint.py': ('resume_chassis_pd_new_episode', 'install_chassis_pd_save_contract', 'current_state'),
    'rescue_training.py': ('install', 'learn'),
}
ROLE_HELPERS = {'E0': {}, 'E2': {'e2_command_checkpoint_v1.py': ('resume_e2_new_episode', 'install_e2_save_contract', 'current', 'load')},
                'E3': {'e3_fullstate_checkpoint_v1.py': ('resume', 'install', 'state')}}


def read_known(path):
    p = Path(path)
    assert p.suffix.lower() in ('.py', '.json', '.md'), 'Only declared text sources/evidence'
    raw = p.read_bytes()
    return raw, dict(path=str(p), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest())


def read_json(path):
    raw, _ = read_known(path)
    return json.loads(raw)


def put(name, value):
    p = B / name
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
    return str(p)


def source_functions(path, names):
    raw, row = read_known(path)
    tree = ast.parse(raw.decode('utf-8-sig'))
    definitions = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    row['functions'] = []
    for name in names:
        n = definitions[name]
        row['functions'].append(dict(name=name, signature=name + '(' + ast.unparse(n.args) + ')',
            start_line=n.lineno, end_line=n.end_lineno,
            original_calls=[ast.unparse(c.func) for c in ast.walk(n) if isinstance(c, ast.Call)]))
    return row, tree


def main():
    roles = {}
    for role, cfg in EXPERTS.items():
        stage = T / 'staged_sources' / STAGES[role]
        index = read_json(stage / 'MOD4V1_DERIVATION_INDEX.json')
        assert index['source_model_metadata']['SHA'] == cfg['source_SHA']
        original = Path(index['original_' + role + '_runtime'])
        original_mod = original / 'isaac/mod4'
        mod = stage / 'runtime/isaac/mod4'
        original_trainer, original_ast = source_functions(original_mod / OLD_TRAINERS[role], ('build_env', 'runner_config', 'main'))
        derived_trainer, trainer_ast = source_functions(mod / ('train_mod4v1_' + role.lower() + '.py'), ('build_env', 'runner_config', 'main'))
        cfg_functions = lambda tree: next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'runner_config')
        assert ast.dump(cfg_functions(original_ast), include_attributes=False) == ast.dump(cfg_functions(trainer_ast), include_attributes=False), 'Original PPO config must be identical'
        helper_rows = {}
        for name, methods in dict(HELPER_FUNCTIONS, **ROLE_HELPERS[role]).items():
            path = mod / name
            # The sealed role package is an overlay, not a fabricated full runtime.
            # Exact originals supply non-overridden dependencies at parent stage.
            if name in ('sensor_a0_runtime.py', 'rescue_training.py'):
                path = original_mod / name
            helper_rows[name], _ = source_functions(path, methods)
        bounded_text = (original_mod / 'rescue_training.py').read_text(encoding='utf-8-sig')
        assert 'init_at_random_ep_len=True' in bounded_text and 'install(runner,log_dir)' in bounded_text
        proof_root = T / 'reports' / REPORT_DIR[role]
        proof_index = read_json(proof_root / 'ORIGINAL_HELPER_JSON_PROOFS/JSON_PROOF_INDEX.json')
        # Preserve exact prior actual proof locators + hashes without reopening any source PT.
        proof_rows = [r for r in proof_index['files'] if r['source_SHA'] == cfg['source_SHA']]
        assert len(proof_rows) == (6 if role == 'E0' else 7)
        collection = read_json(proof_root / 'COLLECTION.json')
        assert collection['files']['FINAL.json']['passed']
        assert collection['files']['PARENT_EXIT_SCOPE.json']['all_own_children_waited']
        runtime_job = collection['remote_root']
        derive_info = read_json(stage / 'MOD4V1_DERIVATION_INDEX.json')
        metadata = derive_info['source_model_metadata']
        assert metadata['iteration'] == cfg['source_iteration'] and metadata['Adam17'] == cfg['source_Adam_step']
        assert metadata['LR'] == cfg['source_LR']
        protocol_raw, protocol_row = read_known(mod / ('mod4v1_' + role.lower() + '_protocol.py'))
        protocol_tree = ast.parse(protocol_raw.decode('utf-8-sig'))
        constants = {n.targets[0].id: ast.literal_eval(n.value) for n in protocol_tree.body if isinstance(n, ast.Assign)
                     and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Constant)}
        assert constants['KIND'] == cfg['original_kind'] and constants['SOURCE_SHA'] == cfg['source_SHA']
        wrapper_name = 'worker_posttrain_' + role.lower() + '_v1.py'
        (B / wrapper_name).write_text('"""SOURCE ONLY. Parent actual EIGHT admission/GO required; no local execution."""\n'
            'from posttrain_fullstate_common_v1 import main\n\nif __name__ == "__main__":\n    main(' + repr(role) + ')\n', encoding='utf-8')
        descriptor = dict(status='SOURCE_ONLY_NOT_ADMISSION_NOT_GO', expert=role, posttrain_kind=POSTTRAIN_KIND,
            parent_admission_kind=ADMISSION_KIND, pinned_source=cfg,
            num_envs=20000, seed=20260928, steps_per_env=24, H1_training_enabled=False, max_additional_updates_upper_bound=20,
            max_parent_seconds_upper_bound=3900, exit_headroom_seconds_minimum=300,
            native24_prep_segment_replayed=False, original_bounded_learn_preserved=True,
            original_init_at_random_ep_len=True, next_new_update_label_convention='Original source runner live label increments once before original bounded learn; saved iter/Adam/LR are read live, never rewritten to a formula',
            interface=dict(actor_obs=35, critic_obs=38, actions=6, hidden_dims=[256, 128, 64], activation='elu', STD='original learned scalar std_param six channels'),
            clock=dict(policy_hz=50, feedback_hz=100, physics_dt=.0025, decimation=8, TGS=[32, 4]),
            gas=dict(preload_each_N=400, stiffness_N_m=2000, damping_N_s_m=3),
            current_thresholds=dict(closure_m=.01, mimic_rad=.01), assets=dict(USD_SHA=USD_SHA, contract_SHA=CONTRACT_SHA),
            production=dict(worker=wrapper_name, common='posttrain_fullstate_common_v1.py', out='production',
                startup='own_startup0_complete.pt', final='model_final_complete.pt', overwrite_mother=False,
                preservation='All original helper live save roots required; recursive union of omitted root/nested dict fields; lists/tuples/tensors atomic, no slice/repeat',
                no_PhysX_exactresume_claim=True),
            exact_original_runtime=str(original), exact_sealed_overlay=str(stage),
            historical_actual_full20k_stage_without_models=runtime_job,
            stage_cautions=['Use original full20k runtime with sealed overlay, not N80 bootstrap/capacity preset',
                'Keep MOD4V1_ASSET_DIFF.json at actual job OWNER ROOT, plus MOD4V1_DERIVATION_INDEX.json and original_run_manifest.json',
                'Actual own Kit path must be jobroot/kit_isolation before AppLauncher; never use evaluator subroot for JOB_ROOT',
                'This package has no G4 import; do not import unrelated CURB dependency chains',
                'FeedbackDelay.delay is the original 100Hz sample-tick accessor; no lag_steps alias',
                'No task/GO/SDK Ready/owner/canonical writer is generated by this child'],
            live_save_required_root_keys=list(LIVE_KEYS) + (['E2_moving4_command_state'] if role == 'E2' else ['E3_public_recovery_state', 'E3_reset_contract'] if role == 'E3' else []),
            exact_source_API=dict(original_trainer=original_trainer, mod4v1_trainer=derived_trainer, helpers=helper_rows,
                external_original_rsl_entry='rsl_rl.runners.OnPolicyRunner.load / save / learn; source file is installed in parent remote runtime, not imported by this child',
                rsl_live_restore_proof='Original SENSOR_RESUME_STARTUP_VERIFIED.json validates live actor/critic/STD/optimizer/iter against cached selected source before the ONE reset'),
            prior_actual_proof_refs=dict(collection=str(proof_root / 'COLLECTION.json'), original_helper_index=str(proof_root / 'ORIGINAL_HELPER_JSON_PROOFS/JSON_PROOF_INDEX.json'), original_helper_rows=proof_rows,
                reuse_boundary='Prior actual full20k/native24 zero-update is reusable historical source evidence, NOT a receipt for this new PPO window'),
            pending_actual=['Original owner resource/budget/GO admission', 'New live whole20k fullrestore and own complete startup save',
                'Original PPO updates (up to20), current complete final save, SDKclose/parentwait/terminalaccounting',
                'Independent skill retention replay using original predicates; no fabricated full-skill graduation'])
        descriptor_path = put(role + '_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json', descriptor)
        roles[role] = dict(descriptor=descriptor_path, entry=str(B / wrapper_name),
            original_trainer=original_trainer, derived_trainer=derived_trainer, helper_API=helper_rows,
            prior_actual_proof_refs=descriptor['prior_actual_proof_refs'], historical_remote_nonmodel_runtime=runtime_job)
    summary = read_json(T / 'reports/SINGLE_GPU_NINE_FINAL_SUMMARY_V1.json')
    baseline = {r['role']: r for r in summary['rows'] if r['role'] in EXPERTS}
    put('SOURCE_API_AND_ACTUAL_PROOF_INDEX_V1.json', dict(kind='SOURCE_ONLY_E0_E2_E3_EXACT_API_ACTUAL_OLD_PROOF_REFERENCES',
        roles=roles, H1_excluded=True, new_model_PT_reads=0, model_PT_stats=0, model_decodes=0,
        actual_new_training_or_SDK_validation=False, canonical_access=False,
        skill_baselines=baseline,
        skill_semantics=dict(E0='N80 diagnostic no ordinary fall/reset; vxMAE .03950337095 and yawMAE .10586447895, no original aggregate graduation rule',
            E2='0/187 current world2pi joint bounds is retained with independent world getter timing/reference-point gap. Body vxMAE about .0455 is distinct. Do not turn the unresolved metric into a new reward',
            E3='0/74 first-episode stable credited, normal6 excluded. stable>=50 public100Hz age units=.5s at50Hz(+2), request<300=3s, 13fixedrecipes. delta>0 is not stable credit'),
        capability_selection=dict(catalog_checked=True, skills_available=['Office family', 'Windows ACL diagnosis'],
            matched_skill=None, reason='RL/SSH/source preparation has no matching Office or ACL task; no denial occurred',
            used_host_tools=['working_directory', 'read', 'glob', 'grep', 'write', 'edit', 'pwsh stdlib Python', 'load_workspace_dependencies'],
            unrelated_DSH_plugin_used=False, child_agents_started=0)))
    put('SOURCE_REVIEW_HISTORY_V1.json', dict(status='SOURCE_ONLY_REVIEW_FIXES_NO_SDK_OR_PT_RUN', events=[
        dict(kind='DISCOVERY_ONLY', detail='Output root absent on first glob; created only child-owned source tree. Initial E[023] path glob had no match; explicit per-role directory glob found Python sources.'),
        dict(kind='SOURCE_DRAFT_CORRECTION', detail='Before validation/execution, E2/E3 legacy kind literals corrected against exact sealed protocol source. No old protocol was edited.'),
        dict(kind='DIRECT_PARENT_REQUIREMENT_APPLIED', detail='Parent clarified original rescue_training.install/learn and init_at_random_ep_len=True. Initial child draft direct-learn/False was replaced before any executable worker use; original bounded learn now invoked unchanged.'),
        dict(kind='ACTUAL_ADMISSION_CONTRACT_UPDATE', detail='Old per-role protocol only accepts old role admission kinds. New child read-only metadata validator uses parent-specified ROOT_MOD4V1_EIGHT_POSTTRAIN_ACTUAL_ADMISSION_V1; no fake old Ready or canonical writer.'),
        dict(kind='LIVE_COUNTER_PROVENANCE_REVIEW', detail='Removed draft temporary arithmetic iteration normalization. Current save reads original runner iter and actual saved17Adam/LR, using arithmetic only as consistency assertions. Original next-new-label convention retained.'),
        dict(kind='LOCAL_EDIT_TOOL_INPUT_ERROR', detail='One edit call had identical old/new strings and an unused mistyped root; tool rejected before any file access/write. All delivered edits are inside the designated child root.')],
        sealed_sources_edited=False, original_once_replayed=False, parent_files_edited=False))
    print(json.dumps(dict(status='SOURCE_DESCRIPTORS_AND_API_INDEX_CREATED', roles=list(roles), child_root=str(B), PT_opens=0, SDK_calls=0), indent=2))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        with (B / 'SOURCE_BUILDER_ORIGINAL_ERROR_V1.json').open('x', encoding='utf-8') as f:
            json.dump(dict(status='SOURCE_BUILDER_ERROR_NO_PT_SDK', traceback=traceback.format_exc()), f, indent=2)
        raise
