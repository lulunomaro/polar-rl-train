"""H1 exact700->517c gas proof +517c->bae threebody nominal identity composition.
No hash bypass; no bank/q/filter/RNG/setter/physics/recipe edit.
"""
from pathlib import Path
import hashlib,json
from mod4v1_fresh_dr_guard import read_asset_identity
from gas400_reset_bank_exact_compatibility_v1 import BANK_SHA,BANK_BYTES,OLD_CONTRACT_SHA,OLD_CONTRACT_COPY,validate_four_gas_scalars,pose_gas_ranges
OLD400_SHA='517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49'
NEW_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'

def require(v,m):
 if not v:raise RuntimeError(m)

def require_mod4v1_e1_reset_bank(bank_path,new_contract_path,raw,*,actual_contract_SHA=None):
 here=Path(__file__).resolve().parent;bank_path=Path(bank_path).resolve();contract=Path(new_contract_path).resolve()
 require(bank_path==here/'reset_bank.json' and not bank_path.is_symlink(),'Exact original adjacent E1 bank')
 b=bank_path.read_bytes();require(len(b)==BANK_BYTES and hashlib.sha256(b).hexdigest()==BANK_SHA,'Original133 bank bytes changed')
 require(json.loads(b)==raw and raw['contract_sha256']==OLD_CONTRACT_SHA,'Exact original700 bank provenance')
 oldraw=(here/OLD_CONTRACT_COPY).read_bytes();midraw=(here/'H1_TYPED400_ORIGINAL_IMPORT_CONTRACT_EXACT.json').read_bytes()
 require(hashlib.sha256(oldraw).hexdigest()==OLD_CONTRACT_SHA and hashlib.sha256(midraw).hexdigest()==OLD400_SHA,'Exact old700 and typed400 evidence')
 identity=read_asset_identity(contract.parent);require(contract==Path(identity.contract_path) and actual_contract_SHA==identity.contract_sha256==NEW_SHA,'Only exact2c/bae actualtask identity')
 old,mid,new=json.loads(oldraw),json.loads(midraw),identity.contract;four=validate_four_gas_scalars(old,mid)
 require(mid['gas_springs']==new['gas_springs'] and mid['joints']==new['joints'],'400gas/joints/limits unchanged')
 allowed={'bodies','enhancement','leg_motor','wheel_motor','physics_dt_s'}
 require(all(mid[k]==new[k] for k in mid if k not in allowed),'Other originalcontract geometry/interface changed')
 require(set(mid['bodies'])==set(new['bodies']),'Original31 bodies retained')
 changed=[n for n in mid['bodies'] if mid['bodies'][n]!=new['bodies'][n]];require(set(changed)=={'chassis','left_shin','right_shin'},'Only authorized threebody nominaldelta')
 bodyfields={'mass_kg','com_m','diagonal_inertia_kg_m2','principal_axes_wxyz','enhancement_mass_basis'}
 for name in changed:
  require(all(mid['bodies'][name].get(k)==new['bodies'][name].get(k) for k in set(mid['bodies'][name])|set(new['bodies'][name]) if k not in bodyfields),'Bodygeometry/neutralframe changed')
 ranges=pose_gas_ranges(raw,new);require(ranges['all_poses']==133 and ranges['original_height_filter_selected_poses']==74,'Original133->74 selection retained')
 return dict(kind='E1_MOD4V1_EXACT_COMPOSED_RESETBANK_COMPATIBILITY_V1',new_contract_SHA=identity.contract_sha256,new_USD_SHA=identity.usd_sha256,original_bank_SHA=BANK_SHA,original700_SHA=OLD_CONTRACT_SHA,typed400_SHA=OLD400_SHA,original_four_gas_scalar_proof=four,authorized_changed_bodies=changed,pose_ranges=ranges,geometry_joint_order_frames_and_fixedSI_unchanged=True,original_selector_q_rng_and_single_reset_unchanged=True,not_old517_pass_relabelled=True,actual_SDK_or_skill_qualification=False)
