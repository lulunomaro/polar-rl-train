"""SOURCE-only lifecycle metadata contracts; definitions perform no lifecycle work.

No root-prefix convention is introduced. A materialized stage is not native GO.
The original full parent owns resource admission, worker waits and both EX scopes.
"""
from pathlib import PurePosixPath
import hashlib
import json
import re

BASE = '/home/lc01/Zonglin Li/zonglin2'
SEEDS = (20260929, 20260930)
ROLES = ('E3', 'W35', 'CURB_INDEPENDENT113', 'CURB_PROTECTED878', 'SLOPE135', 'SLOPE_INDEPENDENT50', 'E0', 'E2')
REQUESTED = ('CURB_PROTECTED878', 'SLOPE135')
DEFERRED = tuple(r for r in ROLES if r not in REQUESTED)
CONTROLS = dict(E0=1000, E2=1200, E3=160, W35=1600, CURB_PROTECTED878=750, CURB_INDEPENDENT113=750, SLOPE135=750, SLOPE_INDEPENDENT50=1000)
POLICY = 'ORIGINAL_EMBEDDED_TEACHER_MEAN_FROM_FULL_A1_V1'
PLAN_KIND = 'GOOD_EXPERT_HOLDOUT_C878_S135_PLAN_V1'
STAGE_NAME = 'STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json'
STAGE_KIND = 'SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V3'
PARENT_NAME = 'single_gpu_good_expert_holdout_parent_v1.py'
PARENT_PIN = (9679, 'fc4458431d375c2b44c063b3f5a8d4ad83ecc6e21d6684625898f7991c51f0ff')
RUNTIME_PIN = (56370, '4ea1470d0255bf172a8bc2e16ce70ceae45a91e32ad622e8df6119f4f8ba0c9f')
INDEX_PIN = (21075, '6f2fb9a4c3ad145620e1bb1b9748ae3848ef1287129aa5970dacee22502a128e')
ORIGINAL_GROUP_ID = 'MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700'
ORIGINAL_PLAN_PIN = (14385, '54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0')
USD = '2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT = 'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
PLAN_MAX = 262144  # Unchanged original materializer/core metadata bound.
GROUP_MAX = 8 * 1024 * 1024  # Original closed-reference group reader bound.
EXPORT_MAX = 16 * 1024 * 1024
STAGER_SOURCE_PINS = {
    'source': dict(path='F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/stage_good_expert_holdout_v3.py', bytes=53062, SHA256='a7eca32d8efc510ba4529b8be7c2b64d7de936f110a4eff4d847925024f43b11'),
    'index': dict(path='F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/SOURCE_INDEX.json', bytes=24749, SHA256='cdc0b918df0be5d1e4e3b4d008f21491446659f30146d490edff68c1df7b61df'),
    'seal': dict(path='F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/SOURCE_SEAL.json', bytes=2034, SHA256='0777c2e284d339ffc9c658a92188ee8c2ebb491c82d4124330a794f68654f426'),
    'mirror': dict(path='F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/SOURCE_MIRROR_INPUTS.json', bytes=20429, SHA256='1e0f1ac5e2c95ff097001553138c8d8bcad54134a814535cce3c31224918aebf'),
    'content_root_SHA256': '1cdd8c72dfdc9fbb3b75f4068f53e8f489d7d558c79a637f39597efae8e765cd'}
CONTROLLER_SOURCE_PIN = (5170, '4cb6994a9afa0b399598f9af012529c9cd06bf6a8ad2e91c7d34f1c8496399c0')
OVERLAY_PINS = {'worker_sources/e1/e1_parallel_worker_safe.py': (14129, '20068d302d713e9826ba4ea4ae9f44708d8cfd2f4965e8b29d16181d4bda9f3e'), 'worker_sources/e1/e1_fresh_runtime_bridge.py': (3552, '603ee68ffa3dd46d2b5d14d26497aa4ad6ebbf4371548f8eede14fa5e5555f26'), 'a1_frozen_eval_runtime_v2.py': (37927, '7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e'), 'frozen_a1_raw35_v1.py': (19226, '1ea4bcfa1081d63d0da2136fedf8c9fafa508d7bb2155095352da496327e4a21'), 'pose_cache_runtime_adapter_v3.py': (18161, '7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f'), 'app_close_semantics_v5.py': (27769, '3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39'), 'native_supermimic_bridge.py': (13125, '8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29'), 'supermimic_vendor_v2/networks.py': (8609, 'c7829e6a1bb9166d724a931858b76424439f371669dfb4bb534b9e76c5c74706'), 'supermimic_vendor_v2/geometry.py': (6960, '89ac3b9470fd6f041fd418365283355a07ad96c4bf38740cf3c5d2d98acb7787'), 'supermimic_vendor_v2/contract.py': (2517, 'd756f2a102a81b2f16295dad66f46e9783b42a3f67e7416360fcf136c2ff06ce'), 'single_gpu_good_expert_holdout_parent_v1.py': (9679, 'fc4458431d375c2b44c063b3f5a8d4ad83ecc6e21d6684625898f7991c51f0ff'), 'good_expert_holdout_runtime_v1.py': (56370, '4ea1470d0255bf172a8bc2e16ce70ceae45a91e32ad622e8df6119f4f8ba0c9f'), 'resume_runtime_contracts_v3.py': (22337, 'dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7'), 'embedded_teacher_reference_v1.py': (16333, '400e06ea2c04edaab8330022a53455e13629b7f35d3ac7066f51df1acfcd0407'), 'producer_teacher_guard_v1.py': (8902, '855e13c931eb8b8711a15b829a4ca95b10692f11b6a68df73a1dece18f98ecf0'), 'worker_sources/e1/e1_route80_factories.py': (23877, 'e4f7b5464e8bb26a0222bae2c367e02aee86db48bbbd2ff6c31a4fcfeeaa23e5'), 'worker_sources/e1/worker_curb878_n80.py': (103, 'd40ab8c4c76234fd1869acfe3d4a23646ca18195bd349d0b14a240b24da4a793'), 'worker_sources/e1/worker_slope135_n80.py': (94, '2568ae5ab0f8db24e6cdd8b9f368ec881b099bf3750215c5e9aa83ec4dc03e42'), 'worker_sources/e1/e1_endpoint_predicate.py': (2504, 'c6bfc7832226963daee96ed9c7f7d6fb989a87a6f8bc5f21d77a85bc69fd0361'), 'worker_sources/e1/ROLE_CONTRACTS.json': (40841, '07b902c0ae3a496e6431ee7413c2256a84f701791fb90af3f57be17af8263218')}  # Complete fixed SOURCE mappings, not native bindings.
STARTED = 'GOOD_HOLDOUT_PARENT_CONTROLLER_STARTED_V1.json'
DISPATCH = 'GOOD_HOLDOUT_PARENT_DISPATCH_RECEIPT_V1.json'
WAITED = 'GOOD_HOLDOUT_PARENT_WAITED_ACTUAL_V1.json'
ERROR = 'GOOD_HOLDOUT_PARENT_CONTROLLER_ERROR_V1.json'
GRADE = 'REFERENCE_GROUP_CLOSED_SOURCE_GRADE_V1.json'
STARTED_KIND = 'OWN_GOOD_HOLDOUT_PARENT_ACTUAL_WAIT_CONTROLLER_V1'
DISPATCH_KIND = 'ONE_ORIGINAL_GOOD_HOLDOUT_PARENT_POPEN_NOT_RESOURCE_ADMISSION_V1'
WAITED_KIND = 'ACTUAL_EXTERNAL_PARENT_POPEN_WAIT_GOOD_HOLDOUT_V1'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def H(raw):
    return hashlib.sha256(raw).hexdigest()


def purpose(seed):
    need(type(seed) is int and seed in SEEDS, 'exact independent holdout seed required')
    return 'GOOD_EXPERT_HOLDOUT_C878_S135_SEED' + str(seed) + '_V1'


def protocol(seed):
    return dict(kind='INDEPENDENT_GOOD_EXPERT_HOLDOUT_SEED_PROTOCOL_V1', seed=seed,
        purpose=purpose(seed), published_baseline_seed=20260928,
        historical_seed_reassessment_counts_as_new_evidence=False,
        independent_group_per_seed=True, paired_effect_claim=False,
        cohort='original_env_id_mod3_ascending27_descending27_stand26',
        controls_per_role=750, num_envs=80, original_acceptance_unchanged=True)


def require_final_pins():
    need(type(STAGER_SOURCE_PINS) is dict and STAGER_SOURCE_PINS,
         'PENDING_FINAL_D664_MATERIALIZER_SOURCE_PINS')
    for key in ('source', 'index', 'seal', 'mirror'):
        row = STAGER_SOURCE_PINS.get(key)
        need(type(row) is dict and type(row.get('bytes')) is int and row['bytes'] > 0
             and sha(row.get('SHA256')) and type(row.get('path')) is str,
             'PENDING_FINAL_D664_' + key.upper() + '_PIN')
    need(type(CONTROLLER_SOURCE_PIN) is tuple and len(CONTROLLER_SOURCE_PIN) == 2
         and type(CONTROLLER_SOURCE_PIN[0]) is int and CONTROLLER_SOURCE_PIN[0] > 0
         and sha(CONTROLLER_SOURCE_PIN[1]), 'PENDING_FINAL_CONTROLLER_SOURCE_PIN')
    need(type(OVERLAY_PINS) is dict and len(OVERLAY_PINS) == 20, 'fixed whole good20 required')
    return True


def root_identity(root, group_id, seed, gpu_uuid):
    """Lexical only: no stat/resolve/model/canonical access and no PREFIX gate."""
    purpose(seed)
    need(type(root) is str and type(group_id) is str, 'explicit absolute root/group required')
    path = PurePosixPath(root)
    need(path.is_absolute() and str(path) == root and '..' not in path.parts
         and path.is_relative_to(PurePosixPath(BASE) / 'tasks'), 'own explicit tasks root required')
    need(group_id == path.name and group_id != ORIGINAL_GROUP_ID and str(seed) in group_id
         and re.fullmatch('[A-Za-z0-9_]+', group_id) is not None,
         'original explicit seed-tagged root/group rule differs')
    need(type(gpu_uuid) is str and re.fullmatch('GPU-[0-9a-f-]+', gpu_uuid) is not None,
         'original explicit GPU UUID rule differs')
    return path


def file_table(plan):
    rows = plan.get('worker_files')
    need(type(rows) is list and rows, 'whole original worker-file table required')
    result = {}
    for row in rows:
        need(type(row) is dict, 'worker-file row required')
        rel = row.get('relative')
        need(type(rel) is str and rel and not rel.startswith('/') and '\\' not in rel and ':' not in rel
             and all(p not in ('', '.', '..') for p in rel.split('/')), 'own relative SOURCE alias required')
        need(rel not in result and type(row.get('bytes')) is int and row['bytes'] > 0
             and sha(row.get('SHA')), 'unique full SOURCE byte pin required')
        result[rel] = (row['bytes'], row['SHA'])
    need(type(OVERLAY_PINS) is dict and len(OVERLAY_PINS) == 20, 'fixed good20 is pending')
    need(all(result.get(rel) == tuple(pin) for rel, pin in OVERLAY_PINS.items()),
         'whole fixed good20 byte metadata differs')
    need(result.get(PARENT_NAME) == PARENT_PIN and result.get('good_expert_holdout_runtime_v1.py') == RUNTIME_PIN,
         'original full parent/runtime identity differs')
    return result


def plan_identity(plan, root, group_id, seed, gpu_uuid, *, runtime):
    root_identity(root, group_id, seed, gpu_uuid)
    need(type(plan) is dict and plan.get('kind') == PLAN_KIND, 'good holdout plan kind required')
    need(plan.get('group_id') == group_id and type(plan.get('seed')) is int and plan['seed'] == seed
         and plan.get('GPU_UUID') == gpu_uuid and plan.get('batch_purpose') == purpose(seed),
         'plan root/group/GPU/seed/purpose binding differs')
    need(plan.get('enabled') is runtime and plan.get('staged') is runtime,
         'runtime plan flags differ from requested layer')
    need(plan.get('source_native_enabled') is False and plan.get('dispatched') is False,
         'SOURCE layer flags must retain original false semantics')
    need(plan.get('policy_variant') == POLICY and plan.get('requested_roles') == list(REQUESTED)
         and plan.get('deferred_roles') == list(DEFERRED) and plan.get('holdout_protocol') == protocol(seed),
         'only independent original-teacher C878/S135 scope is accepted')
    need(plan.get('asset_SHA') == USD and plan.get('contract_SHA') == CONTRACT,
         'original asset/contract identity differs')
    for key in ('comparison', 'relative_improvement', 'paired_actual_reference', 'UID_alignment',
                'reference_cache_match', 'reward_effect_identification', 'overall_eight_pass_rate'):
        need(key in plan and plan[key] is None, 'no new matched/eight-role quality claim: ' + key)
    rows = plan.get('roles')
    need(type(rows) is list and len(rows) == 8 and all(type(r) is dict for r in rows)
         and {r.get('role') for r in rows} == set(ROLES), 'full original eight-role non-H1 catalog required')
    for row in rows:
        need(type(row.get('controls')) is int and row['controls'] == CONTROLS[row['role']],
             'original role controls differ')
    file_table(plan)
    return [next(r for r in rows if r['role'] == role) for role in REQUESTED]


def validate_stage(stage_raw, plan_raw, parent_raw, *, root, group_id, seed, gpu_uuid, stage_sha):
    """Bind the actually published raw plan, not old V8 original_plan_SHA.

    receipt.staged stays False. Only its hash-bound runtime plan has the two True
    flags. This predicate does not perform materialization, publication or approval.
    """
    require_final_pins()
    need(type(stage_raw) is bytes and len(stage_raw) <= GROUP_MAX and sha(stage_sha)
         and H(stage_raw) == stage_sha, 'whole actual materialization receipt SHA differs')
    stage = json.loads(stage_raw)
    need(type(stage) is dict and stage.get('kind') == STAGE_KIND
         and type(stage.get('source_derivation_version')) is int and stage['source_derivation_version'] == 3,
         'only final V3 materialization receipt kind accepted')
    need(stage.get('materialized') is True and type(stage.get('parent_launches')) is int
         and stage['parent_launches'] == 0, 'actual materialization before one Popen is required')
    need(all(stage.get(k) is False for k in ('source_native_enabled', 'staged', 'dispatched')),
         'original SOURCE receipt layer flags differ')
    need(stage.get('root') == root and stage.get('group_id') == group_id
         and type(stage.get('seed')) is int and stage['seed'] == seed
         and stage.get('purpose') == purpose(seed) and stage.get('requested_roles') == list(REQUESTED),
         'materialization root/group/seed/purpose differs')
    need(type(plan_raw) is bytes and 0 < len(plan_raw) <= PLAN_MAX
         and type(stage.get('GROUP_PLAN_bytes')) is int and stage['GROUP_PLAN_bytes'] == len(plan_raw)
         and sha(stage.get('GROUP_PLAN_SHA256')) and stage['GROUP_PLAN_SHA256'] == H(plan_raw),
         'exact final raw GROUP_PLAN bytes/SHA required')
    plan = json.loads(plan_raw)
    plan_identity(plan, root, group_id, seed, gpu_uuid, runtime=True)
    validation = stage.get('metadata_validation')
    need(type(validation) is dict and validation.get('kind') == 'GOOD_EXPERT_HOLDOUT_REAL_COMPLETE_METADATA_CLOSURE_CHECK_V1'
         and validation.get('passed') is True
         and validation.get('full_modules_not_AST_cropped_or_stubbed') is True
         and validation.get('requested_roles') == list(REQUESTED)
         and type(validation.get('seed')) is int and validation['seed'] == seed
         and validation.get('purpose') == purpose(seed)
         and validation.get('actual_parent_or_worker_main_executed') is False,
         'whole original stage metadata closure receipt differs')
    need(all(type(stage.get(k)) is int and stage[k] == 0 for k in ('model_stat_hash_open_decode', 'C_lock_SDK_GPU_GO_operations'))
         and all(k in stage and stage[k] is None for k in ('resource_admission', 'actual_frozen_evaluation', 'comparison', 'overall_eight_pass_rate')),
         'materialization SOURCE receipt is not native admission or quality evidence')
    need(type(parent_raw) is bytes and (len(parent_raw), H(parent_raw)) == PARENT_PIN,
         'complete original parent byte identity differs')
    need(stage.get('original_plan_SHA') == ORIGINAL_PLAN_PIN[1] and stage['original_plan_SHA'] != stage['GROUP_PLAN_SHA256'],
         'old original-plan provenance is not the new runtime plan hash')
    return stage, plan


def process_identity(row, label):
    need(type(row) is dict and type(row.get('pid')) is int and row['pid'] > 0
         and type(row.get('linux_start_ticks')) is str and row['linux_start_ticks'].isdigit(),
         label + ' actual pid/startticks identity required')
    return row


def validate_dispatch(value):
    require_final_pins()
    need(type(value) is dict and value.get('kind') == DISPATCH_KIND, 'typed own good holdout dispatch required')
    root_identity(value.get('root'), value.get('group_id'), value.get('seed'), value.get('GPU_UUID'))
    need(value.get('evaluation_purpose') == purpose(value['seed'])
         and value.get('parent_source_SHA') == PARENT_PIN[1]
         and value.get('controller_source_SHA') == CONTROLLER_SOURCE_PIN[1], 'dispatch exact source/seed/purpose differs')
    process_identity(value.get('controller'), 'controller'); process_identity(value.get('parent'), 'parent')
    need(type(value.get('actual_native_parent_Popen_calls')) is int and value['actual_native_parent_Popen_calls'] == 1
         and value.get('SDK_scene_or_skill_admission') is False, 'only one original parent Popen receipt accepted')
    need(sha(value.get('stage_receipt_SHA256')) and sha(value.get('GROUP_PLAN_SHA256'))
         and type(value.get('GROUP_PLAN_bytes')) is int and 0 < value['GROUP_PLAN_bytes'] <= PLAN_MAX,
         'dispatch must bind the complete materialized receipt and final plan')
    return value


def nullable_count(value):
    return value if type(value) is int and value >= 0 else None
