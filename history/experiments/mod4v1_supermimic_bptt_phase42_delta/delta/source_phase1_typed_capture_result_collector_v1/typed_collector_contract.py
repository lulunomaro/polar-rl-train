"""NEW typed collector metadata contract. Stdlib definitions; no collection on import.

The 34 finite bindings never stand in for the original complete static baseline.
The materializer's SOURCE flags remain false even after actual materialization.
"""
from pathlib import PurePosixPath
import hashlib
import json
import re

SOURCE_VERSION = 1
SCHEMA = 'PHASE1_TYPED_NATIVE_PRODUCER_ABI_V1'
PURPOSE = 'NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN'
TASK_KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_E3_N80_TASK_V1'
PLAN_KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_E3_ONLY_PLAN_V1'
FINAL_KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_E3_N80_FINAL_V1'
GROUP_FINAL_KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_GROUP_FINAL_V1'
COMMON_START_KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_COMMON_START_V1'
GRADE_KIND = 'PHASE1_TYPED_NATIVE_CLOSED_SOURCE_GRADE_V1'
STAGE_KIND = 'SOURCE_PHASE1_TYPED_CAPTURE_MATERIALIZED_NOT_ADMISSION_V1'
METADATA_KIND = 'REAL_WHOLE_SAFE_TYPED_CAPTURE_METADATA_IMPORT_CHECK_V1'
COMPLETE = 'STAGE_COMPLETE_PHASE1_CAPTURE_V1.json'
INDEX_SHA = '92da4a44ca9b7b6246c82d4dd281b73fa176bc1bdfbac981aa3403e43d7873d8'
INDEX_BYTES = 148229
ABI_PIN = (9441, 'e805ecb63aa61c81324c62488981a49973a99381dc14cc4d37b911c4a70f696a')
PRODUCER_SEAL_PIN = (3503, 'f92384f7943d27a4d588316cfba129011ca47851571ff252040df4c740424966')
PRODUCER_ROOT = 'e7ff849c171f2eddc1053c5d1fc0779c31d6f8df73937616a7482abb85e8b897'
FINITE_PIN = (11663, '5b633338090b8801282e8b2ee824d74d413495efa39f93708cda44bff2222155')
MATERIALIZER_PINS = {
    'stage_phase1_typed_capture_v1.py': (48397, '0fbaad211b341c0d5cce5a429a1832c02230b2cfdfc15fb9100576514477c00b'),
    'typed_source_support_v1.py': (13308, '6390b2235b416406ac8a6cb21aaf4f1fc2eb6adfe95e50cafbfe234610cbb575'),
    'SOURCE_INDEX.json': (23560, '3ca53da2954e78300026eeb3d51e26a629fd7daac0e919be96e042214920c84d'),
    'SOURCE_MIRROR_INPUTS.json': (93889, 'c47b837bce45d3fa3c917db437181ee83814feef0ca0c2b67df4f0c6f49d9d90'),
    'SOURCE_SEAL.json': (5312, 'e9edbf414c5c386236a1eccb0b35d2e525a9339a4dd93d6365e6d645b5c9ebda'),
}
MATERIALIZER_ROOT = '4348259257b4a20dcddb41ad9d0f4f022657d08d33440a9ae41a66947a064413'
# Exact whole frozen FINITE_SOURCE_BUNDLE rows, filled by the author from pinned bytes.
FINITE_ROWS = ({'SHA256': '0e85c472e4e3fe60a434e7b7c9844fc81356a5f66cce7013f4c105a44ac05ba8',
  'bytes': 16164,
  'relative': 'worker_sources/e1/e1_parallel_worker_safe.py'},
 {'SHA256': 'be442b02a606be9bd17a3ae996e52978057a778d8e593df64fc8c5b0ea9dde8b',
  'bytes': 3451,
  'relative': 'worker_sources/e1/e1_fresh_runtime_bridge.py'},
 {'SHA256': '7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e',
  'bytes': 37927,
  'relative': 'a1_frozen_eval_runtime_v2.py'},
 {'SHA256': '1ea4bcfa1081d63d0da2136fedf8c9fafa508d7bb2155095352da496327e4a21',
  'bytes': 19226,
  'relative': 'frozen_a1_raw35_v1.py'},
 {'SHA256': '7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f',
  'bytes': 18161,
  'relative': 'pose_cache_runtime_adapter_v3.py'},
 {'SHA256': '3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39',
  'bytes': 27769,
  'relative': 'app_close_semantics_v5.py'},
 {'SHA256': '8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29',
  'bytes': 13125,
  'relative': 'native_supermimic_bridge.py'},
 {'SHA256': 'c7829e6a1bb9166d724a931858b76424439f371669dfb4bb534b9e76c5c74706',
  'bytes': 8609,
  'relative': 'supermimic_vendor_v2/networks.py'},
 {'SHA256': '89ac3b9470fd6f041fd418365283355a07ad96c4bf38740cf3c5d2d98acb7787',
  'bytes': 6960,
  'relative': 'supermimic_vendor_v2/geometry.py'},
 {'SHA256': 'd756f2a102a81b2f16295dad66f46e9783b42a3f67e7416360fcf136c2ff06ce',
  'bytes': 2517,
  'relative': 'supermimic_vendor_v2/contract.py'},
 {'SHA256': '63eaa4b04ee085a1efbbbc72a4d0756036faa7928af01e19713e6871925d0e80',
  'bytes': 9348,
  'relative': 'single_gpu_e3_w35_bound_only_parent_v1.py'},
 {'SHA256': 'e6b64b0757c97f02a9df936fe6d8edfd9e99914fb3d372c9021eb301d700d30f',
  'bytes': 40234,
  'relative': 'bound_only_native_runtime_v1.py'},
 {'SHA256': 'd558cb899115f0082a0671a265cd9ea179e3cc91608d8b412a39b73abf1c2642',
  'bytes': 15267,
  'relative': 'worker_sources/parent/worker_five_original_n80.py'},
 {'SHA256': 'dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7',
  'bytes': 22337,
  'relative': 'resume_runtime_contracts_v3.py'},
 {'SHA256': '3375168c0d11fe349c8428cb81bb343a90d1520feb90c1e034f829f98ef4a0c9',
  'bytes': 19233,
  'relative': 'bound_only_native_helper_v1.py'},
 {'SHA256': 'a840746e22eab3a55781069521b77ba92f67427baae1001b117d732453c76f1e',
  'bytes': 9754,
  'relative': 'producer_bound_probe_guard_v1.py'},
 {'SHA256': '0f241475909a7c84e325416f2f6530f7ad912526ff41d7779f5ac0bcb2c87458',
  'bytes': 3378,
  'relative': 'bound_only_native_route_v1.py'},
 {'SHA256': 'cc85300dfe62fbb33bb7c072b2adbc40d865c08ac45df663425ca658bd74e0a3',
  'bytes': 10906,
  'relative': 'phase1_capture_contract.py'},
 {'SHA256': '944c6e0cbc91e881c8c205bc78ee3b1aecf8ade877b7b97711dd6acebe93569e',
  'bytes': 16708,
  'relative': 'phase1_capture_observer.py'},
 {'SHA256': '5495edd4704f67bd77226e895d33cdd4d96c0c51621b962e95e2af1a23431faa',
  'bytes': 19099,
  'relative': 'phase1_capture_runtime.py'},
 {'SHA256': '448929f7574eea90a323935684b67501927896de10f6518987c4ad783898f941',
  'bytes': 20227,
  'relative': 'worker_passive_interface_v1.py'},
 {'SHA256': 'd5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41',
  'bytes': 9336,
  'relative': 'single_gpu_passive_capture_parent_v1.py'},
 {'SHA256': 'a334766d6a9ca88d02d682e73d70a15e9098f1e77d1aa7a45e6d0154a4b73b62',
  'bytes': 31456,
  'relative': 'phase1_deps/sensor/source_api.py'},
 {'SHA256': 'ef4d1895e06087db023d55aa58203bd5b58f915fa71f65ade541e8ae588a61d4',
  'bytes': 3327,
  'relative': 'phase1_deps/sensor/field_snapshot.py'},
 {'SHA256': '799569719f570bf94d6d9ab9fd10d4e3006471990a0a433a51a0ab16026c5f68',
  'bytes': 9827,
  'relative': 'phase1_deps/sensor/dependency_contract.py'},
 {'SHA256': 'ddead70de7cb1e01acc79899320c0aaadd9c217cd7ba35e9e9f4a00f03c54745',
  'bytes': 37157,
  'relative': 'phase1_deps/sensor/passive_capture.py'},
 {'SHA256': '5cd6c770c7f3541308201389f721b43f9e7c681199443c9a2f80d2f80347e452',
  'bytes': 19153,
  'relative': 'phase1_deps/sensor/CODEC_SOURCE_PINS.json'},
 {'SHA256': '2801135d1ff028f09a5eb7cd571cc3ca90694b60340d17e62374a42cbe60eaca',
  'bytes': 336133,
  'relative': 'phase1_deps/sensor/SOURCE_API_MANIFEST.json'},
 {'SHA256': '9ff7f0fca2eace46289144d22f0508599d967a7cd5ac194ab05977648b551d07',
  'bytes': 39150,
  'relative': 'phase1_deps/actuation/SOURCE_PINS.json'},
 {'SHA256': '77c007fb0b17088b54bb0c115913159c7a9bf99f50f29a0b203dea483f0d1ee4',
  'bytes': 22318,
  'relative': 'phase1_deps/codec/typed_capture_codec.py'},
 {'SHA256': 'ec10b09b77548c560611e641d685e2cee029c9778ff8c8852a8bf070243bd95d',
  'bytes': 20859,
  'relative': 'phase1_deps/actuation_c2/actuation_tap_v2.py'},
 {'SHA256': 'e40b51db4bca2f322cc2c9b4b0fe011eed292ae605f4f175f268a5bf90326047',
  'bytes': 117,
  'relative': 'worker_sources/parent/launch_storage_contract.py'},
 {'SHA256': 'ab26d1b22557e6a85231795cd41c52aa53b81e69661c8a62f4c72118a62c74cc',
  'bytes': 653,
  'relative': 'worker_sources/parent/n80_gpu_capacity.py'},
 {'SHA256': 'e805ecb63aa61c81324c62488981a49973a99381dc14cc4d37b911c4a70f696a',
  'bytes': 9441,
  'relative': 'PRODUCER_ABI.json'})
BIG_LIMIT = 64*1024*1024
PLAN_LIMIT = 8*1024*1024
SMALL_LIMIT = 2*1024*1024
EXPORT_LIMIT = 16*1024*1024
REMOVAL_PATHS = (
    'sensor.control_ledger.controls',
    'sensor.incomplete_current_control',
    'typed_pending_control',
    'actuation.windows.first',
    'actuation.windows.last',
    'bounded_trace.initial_sensor_memory',
    'bounded_trace.initial_actor_original_buffer',
)
SOURCE_DERIVATION = dict(
    kind='PHASE1_TYPED_CAPTURE_RESULT_COLLECTOR_SOURCE_DERIVATION_V1',
    base_collector_source_version=4,
    producer_source_version=1, typed_producer_schema=SCHEMA,
    producer_index_SHA256=INDEX_SHA, producer_seal_SHA256=PRODUCER_SEAL_PIN[1],
    producer_root_SHA256=PRODUCER_ROOT,
    materializer_seal_SHA256=MATERIALIZER_PINS['SOURCE_SEAL.json'][1],
    materializer_root_SHA256=MATERIALIZER_ROOT,
    wire_V1_namespace_preserved=True, ROOT_PREFIX_V1_preserved=True,
    full_safe_module_imports=True, no_AST_cropped_runtime_or_stub=True,
    producer_grade_preserved=True, binding_epoch_not_removed=True,
    full_static_baseline_is_not_34_aliases=True,
    science_consumer_enabled=False, actual_SDK_native_executed=False)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def finite_rows(index, abi):
    """Check 32 overlay + 2 independent bootstrap whole-source identities, not a baseline."""
    need(type(index) is dict and index.get('typed_producer_schema') == SCHEMA,
         'typed producer index required; old27 does not qualify')
    rows = index.get('original17', [])+index.get('new_sources', [])+index.get('dependency_sources', [])
    need(len(rows) == 31 and len(index.get('bootstrap_original_sources', [])) == 2,
         'typed31 plus independent bootstrap2 and ABI1 required')
    observed = {}
    for row in rows+index['bootstrap_original_sources']+[index.get('producer_abi', {})]:
        alias = row.get('install_relative')
        need(type(alias) is str and alias and ':' not in alias and '\\' not in alias
             and not alias.startswith('/') and all(v not in ('', '.', '..') for v in alias.split('/')),
             'exact finite relative alias required')
        need(alias not in observed and type(row.get('bytes')) is int and row['bytes'] > 0
             and digest(row.get('SHA256')), 'duplicate or incomplete finite source identity')
        observed[alias] = (row['bytes'], row['SHA256'])
    expected = {row['relative']: (row['bytes'], row['SHA256']) for row in FINITE_ROWS}
    need(len(expected) == 34 and observed == expected, 'whole typed34 finite closure differs')
    need(type(abi) is dict and abi.get('kind') == SCHEMA, 'whole typed ABI kind differs')
    return observed


def complete_info(info, *, maximum):
    return (type(info) is dict and info.get('status') == 'READ'
            and type(info.get('bytes')) is int and 0 < info['bytes'] <= maximum
            and type(info.get('read_count')) is int and info['read_count'] == 1
            and info.get('whole_JSON_read') is True and digest(info.get('SHA256')))


def validate_baseline_metadata(inv):
    """Published independent-origin consistency only; no static payload is reopened."""
    proof = inv.get('baseline_provenance', {})
    need(type(proof) is dict and proof.get('kind') == 'INDEPENDENT_COMPLETE_INPUT_TREE_BYTE_INVENTORY_V1',
         'independent complete origin metadata required, not two equal subset arrays')
    origin = proof.get('original_logical_rows'); moves = proof.get('source_to_retained')
    need(type(origin) is list and origin and type(moves) is dict
         and type(proof.get('all_original_input_files_read')) is int
         and proof['all_original_input_files_read'] == len(origin), 'whole original origin count required')
    logical = [{k: row[k] for k in ('relative','bytes','SHA256')} for row in origin]
    need(len({r['relative'] for r in logical}) == len(logical)
         and logical == sorted(logical, key=lambda r:r['relative'])
         and set(moves) <= {r['relative'] for r in logical}, 'original logical inventory or relocation domain differs')
    def canonical(rows):
        return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    need(proof.get('original_logical_tree_SHA256') == canonical(logical), 'independent original logical SHA differs')
    expected = []
    for row in origin:
        alias = moves.get(row['relative'], row['relative'])
        need(row['relative'] not in moves or alias == 'worker_sources/phase1_retained_original/'+row['relative'],
             'original retained namespace differs')
        need(type(row.get('input_path')) is str and bool(row['input_path'])
             and type(row.get('bytes_read')) is int and row['bytes_read'] == row['bytes']
             and type(row['bytes']) is int and row['bytes'] >= 0 and digest(row['SHA256']),
             'complete original path/read-byte metadata required')
        expected.append(dict(relative=alias, bytes=row['bytes'], SHA256=row['SHA256']))
    expected.sort(key=lambda r:r['relative'])
    need(inv.get('baseline') == inv.get('installed') == expected
         and inv.get('SHA256') == canonical(expected), 'installed bytes metadata differs from original full origin')
    return True


def validate_materialization(stage, plan, infos, dispatch):
    """Validate only actual published metadata bound to original cached raw JSON hashes."""
    need(type(stage) is dict and type(plan) is dict, 'complete materialization and plan required')
    need(complete_info(infos.get(COMPLETE), maximum=SMALL_LIMIT)
         and complete_info(infos.get('GROUP_PLAN.json'), maximum=PLAN_LIMIT),
         'materialization/plan whole cached byte evidence required')
    need(infos[COMPLETE]['SHA256'] == dispatch.get('stage_receipt_SHA256'),
         'original materialization receipt SHA differs')
    need(type(stage.get('GROUP_PLAN_bytes')) is int
         and stage['GROUP_PLAN_bytes'] == infos['GROUP_PLAN.json']['bytes']
         and stage.get('GROUP_PLAN_SHA256') == infos['GROUP_PLAN.json']['SHA256'],
         'original full raw GROUP_PLAN bytes/SHA binding differs')
    need(stage.get('kind') == STAGE_KIND and stage.get('typed_producer_schema') == SCHEMA
         and stage.get('purpose') == PURPOSE and stage.get('materialized') is True
         and type(stage.get('parent_launches')) is int and stage['parent_launches'] == 0,
         'typed actual materialization is not parent admission')
    for key in ('source_native_enabled', 'staged', 'dispatched', 'actual_SDK_executed',
                'capture_interface_passed', 'exact', 'stage2_GO'):
        need(stage.get(key) is False, 'materialization SOURCE flag differs: '+key)
    need(stage.get('gate1') == 'UNKNOWN' and all(type(stage.get(k)) is int and stage[k] == 0
         for k in ('model_reads', 'resource_operations')), 'materialization flags or operations differ')
    need(stage.get('group_id') == dispatch.get('group_id') and stage.get('root') == dispatch.get('root')
         and stage.get('requested_roles') == ['E3'], 'materialization own root/group differs')
    need(plan.get('kind') == PLAN_KIND and plan.get('typed_producer_schema') == SCHEMA
         and plan.get('batch_purpose') == PURPOSE and plan.get('group_id') == dispatch.get('group_id')
         and plan.get('requested_roles') == ['E3'], 'typed purpose/root plan differs')
    need(type(plan.get('capture_controls')) is int and plan['capture_controls'] in (64, 128)
         and type(stage.get('capture_controls')) is int and stage['capture_controls'] == plan['capture_controls'],
         'typed controls must be exact64/128')
    need(type(stage.get('files')) is int and stage['files'] >= 34, 'actual materialized file count missing')
    inv = plan.get('retained_static_inventory', {})
    need(type(inv) is dict and type(inv.get('baseline')) is list and bool(inv['baseline'])
         and inv.get('installed') == inv['baseline']
         and inv.get('installed_status') == 'ACTUAL_STREAM_HASH_VERIFIED_STATIC_FILES'
         and digest(inv.get('SHA256')) and stage.get('baseline_SHA256') == inv['SHA256'],
         'full independent static baseline and observed installed metadata required, not finite34')
    provenance = inv.get('baseline_provenance', {})
    need(type(provenance) is dict and stage.get('source_to_retained') == provenance.get('source_to_retained')
         and type(stage.get('source_to_retained')) is dict,
         'original source-to-retained provenance required')
    validate_baseline_metadata(inv)
    meta = stage.get('metadata_validation', {})
    need(type(meta) is dict and meta.get('kind') == METADATA_KIND
         and type(meta.get('source_derivation_version')) is int and meta['source_derivation_version'] == 1
         and meta.get('typed_producer_schema') == SCHEMA and meta.get('passed') is True
         and meta.get('ROOT_equals_HERE') is True and meta.get('purpose') == PURPOSE
         and meta.get('requested_roles') == ['E3'] and meta.get('task_controls') == plan['capture_controls']
         and meta.get('canonical7a092_whole_module') is True, 'whole typed metadata import receipt differs')
    active = meta.get('active_bindings', {})
    need(type(active) is dict and all(type(active.get(k)) is int and active[k] == v for k, v in
         dict(complete_bindings=34, overlay_bindings=32, independent_original_bootstrap_bindings=2).items())
         and active.get('all_complete_source_bytes_verified') is True, 'actual typed34 import receipt differs')
    close = meta.get('complete_AppV6_Base', {})
    need(type(close) is dict and close.get('kind') == 'REAL_COMPLETE_APP_V6_CONTRACTS_IMPORT_CHECK_V2'
         and close.get('passed') is True and close.get('helper_base_is_actual_imported_contracts') is True,
         'actual whole AppV6/Base source import receipt required')
    need(meta.get('native_worker_main_executed') is False and meta.get('actual_SDK_binding') is None
         and all(type(meta.get(k)) is int and meta[k] == 0 for k in ('resource_operations', 'model_reads')),
         'metadata import is not SDK execution')
    return dict(typed_materialization_raw_plan_binding=True, observed_static_inventory_is_not_independently_rehashed=True,
                materialization_is_not_SDK_admission=True)
