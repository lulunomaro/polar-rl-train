"""NEW asset/bank geometry admission. Never returns the obsolete four-scalar pass."""
from pathlib import Path
import hashlib
import json
import os
from mod4v1_fresh_dr_guard import read_asset_identity
from W35_gas400_exact_selected_reset_compatibility_v2 import (
    PIN as HISTORICAL_BANK_PIN, verify_original_W35_selected_bank,
)

CHANGED_BODIES = {'chassis', 'left_shin', 'right_shin'}


def require(value, message):
    if not value:
        raise RuntimeError(message)


def H(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require_mod4v1_asset_and_original_bank_geometry(meta, meta_path, usd_path, contract_path):
    """Declared source DIFF != target SDK qualification. Preserve original pose34 witness."""
    here = Path(__file__).resolve().parent
    meta_path, usd_path, contract_path = map(Path, (meta_path, usd_path, contract_path))
    require(meta_path.resolve() == here / 'MOD4_RESET_COLLISION_BANK.json', 'Exact original adjacent bank metadata')
    require(H(meta_path) == HISTORICAL_BANK_PIN['old_meta_SHA'], 'Original bank metadata changed')
    require(json.loads(meta_path.read_bytes()) == meta, 'Bank metadata object/file mismatch')
    require(meta['usd_sha256'] == HISTORICAL_BANK_PIN['old_USD_SHA'] and
            meta['contract_sha256'] == HISTORICAL_BANK_PIN['old_contract_SHA'],
            'Bank remains historical 700N geometry provenance, not a new asset producer')
    identity = read_asset_identity(usd_path.parent)
    require(Path(identity.usd_path) == usd_path.resolve() and Path(identity.contract_path) == contract_path.resolve(),
            'New imported USD/JSON disagree with actual reset task')
    job = Path(os.environ['MOD4_NEW208_JOB_ROOT'])
    diff = json.loads((job / 'MOD4V1_ASSET_DIFF.json').read_bytes())
    require(diff['old_400N_contract_SHA'] == '517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49',
            'Wrong historical 400N basis')
    require(diff['new_contract_SHA'] == identity.contract_sha256 and diff['new_USD_SHA'] == identity.usd_sha256,
            'New authorization DIFF does not identify the loaded candidate')
    require(set(diff['changed_body_names']) == CHANGED_BODIES and diff['contract_geometry_unchanged'] is True,
            'Only declared three-body mass/COM/inertia update may reuse this geometry bank')
    return dict(schema='mod4v1.W35.nearest250.bank_geometry_reuse.v1',
        new_USD_SHA=identity.usd_sha256, new_contract_SHA=identity.contract_sha256,
        authorized_changed_bodies=sorted(CHANGED_BODIES),
        authorized_body_differences=diff['body_changes'],
        declared_contract_geometry_unchanged=True,
        original_bank_producer_USD_SHA=HISTORICAL_BANK_PIN['old_USD_SHA'],
        original_bank_producer_contract_SHA=HISTORICAL_BANK_PIN['old_contract_SHA'],
        legacy_four_scalar_asset_admission_replaced_not_relabelled=True,
        original_pose34_q_joint_order_and_footprint_check_still_required=True,
        actual_SDK_or_GPU_qualification=False, complete_expert_adaptation=False)


def record_historical_source_metadata(state, source):
    """Own NEW saved checkpoint only; immutable source dictionary/PT stays untouched."""
    keys = ('PPO50_gas400_adaptation', 'PPO50_gas400_new_updates', 'PPO50_gas400_clock',
            'typed_W35_RM70_task', 'RM70_full208_lineage')
    state['historical_source_400N50_and_RM70_provenance'] = {k: source[k] for k in keys if k in source}
    for key in ('PPO50_gas400_adaptation', 'PPO50_gas400_new_updates', 'PPO50_gas400_clock'):
        state.pop(key, None)
    state['mod4v1_asset_identity'] = dict(USD_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',
        contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',
        closure_episode_m=.01, mimic_rad=.01, D6_scope='original_gas_damping_not_all_joint_friction',
        actual_SDK_or_skill_pass_not_inferred_from_metadata=True)
