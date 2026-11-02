"""E2-specific unchanged flat133/height-filter74 reset bank with new nominal."""
from pathlib import Path
import hashlib,json,os
from mod4v1_fresh_dr_guard import read_asset_identity
from gas400_reset_bank_exact_compatibility_v1 import BANK_SHA,BANK_BYTES,OLD_CONTRACT_SHA,pose_gas_ranges

def require(value,message):
 if not value:raise RuntimeError(message)

def require_mod4v1_flat_reset_bank(bank_path,new_contract_path,raw,*,actual_contract_SHA=None):
 bank_path=Path(bank_path).resolve();contract=Path(new_contract_path).resolve()
 require(bank_path==Path(__file__).resolve().parent/'reset_bank.json','Original adjacent E2 bank required')
 b=bank_path.read_bytes();require(len(b)==BANK_BYTES and hashlib.sha256(b).hexdigest()==BANK_SHA,'Original E2 bank bytes changed')
 require(json.loads(b)==raw and raw['contract_sha256']==OLD_CONTRACT_SHA,'Original E2 geometry producer identity')
 identity=read_asset_identity(contract.parent)
 require(contract==Path(identity.contract_path),'Actual new E2 contract path')
 require(actual_contract_SHA==identity.contract_sha256,'Caller must identify new contract, not old517')
 diff=json.loads((Path(os.environ['MOD4V1_E2_JOB_ROOT'])/'MOD4V1_ASSET_DIFF.json').read_bytes())
 require(diff['new_contract_SHA']==identity.contract_sha256 and diff['new_USD_SHA']==identity.usd_sha256,'Declared new model DIFF')
 require(set(diff['changed_body_names'])=={'chassis','left_shin','right_shin'} and diff['contract_geometry_unchanged'],'Only declared mass/COM/I changes reuse E2 geometric bank')
 ranges=pose_gas_ranges(raw,identity.contract)
 require(ranges['all_poses']==133 and ranges['original_height_filter_selected_poses']==74,'Original E2 height population, NOT W35 pose34')
 return dict(schema='mod4v1.E2.flat133.filtered74.bank_geometry.v1',new_USD_SHA=identity.usd_sha256,
  new_contract_SHA=identity.contract_sha256,original_bank_SHA=BANK_SHA,pose_ranges=ranges,
  original_filter_random_selector_q_root_writes_unchanged=True,authorized_changed_bodies=diff['changed_body_names'],
  no_old_four_scalar_pass_relabelled=True,actual_SDK_or_expert_adaptation_validated=False)
