"""Original E1collider bank exactasset identity composition only.
Current generation/import is no I/O. Future call checks oldmetadata and exact
NPZSHA without modifying/rebuilding arrays; original np.load/q/argmin/posewrites
remain in the original E1 reset function. Not SDKgeometry/skill graduation.
"""
from pathlib import Path
import hashlib,json
from mod4v1_e1_reset_bank_compat import require_mod4v1_e1_reset_bank
META_SHA='7d79108982c8e0c146a5a5440160e61c0e6a0675f6b668577babb9aff4a570e7'
NPZ_SHA='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'

def require_mod4v1_e1_collision_bank(meta_path,asset_dir):
 here=Path(__file__).resolve().parent;meta_path=Path(meta_path).resolve();asset=Path(asset_dir).resolve()
 if meta_path!=here/'MOD4_RESET_COLLISION_BANK.json':raise ValueError('Exact original E1collider bank metadata path')
 meta_raw=meta_path.read_bytes()
 if hashlib.sha256(meta_raw).hexdigest()!=META_SHA:raise ValueError('Original collider metadata bytes changed')
 meta=json.loads(meta_raw)
 if meta['usd_sha256']!='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87' or meta['contract_sha256']!='cbcdacdf2b15d6a5fb1e5650e418443ff376ee23334e47e1ef36fcb79c32719f':raise ValueError('Original700 geometry-bank identity')
 if meta['poses']!=133 or meta['bodies']!=31 or meta['tree_joints']!=30:raise ValueError('Original full133/31body/30joint bank scope')
 flat=here/'reset_bank.json';raw=json.loads(flat.read_bytes());actual=hashlib.sha256((asset/'import_contract.json').read_bytes()).hexdigest()
 composed=require_mod4v1_e1_reset_bank(flat,asset/'import_contract.json',raw,actual_contract_SHA=actual)
 # FUTURE actual non-PT dependency proof; NEVER called in source-only generation.
 npz=here/'MOD4_RESET_COLLISION_BANK.npz'
 with npz.open('rb') as f:actual_npz_sha=hashlib.file_digest(f,'sha256').hexdigest()
 if actual_npz_sha!=NPZ_SHA:raise ValueError('Exact original collisionbank NPZSHA required; no substitute/reshape')
 return dict(kind='E1_MOD4V1_EXACT_COLLIDER_BANK_ASSET_COMPOSITION',original_meta_SHA=META_SHA,original_NPZ_SHA=NPZ_SHA,original_meta_left_with_original700identity=True,newactual_USD_SHA=composed['new_USD_SHA'],newactual_contract_SHA=composed['new_contract_SHA'],exact_composed_geometry_proof=composed,rough_selection='Original argmin(abs(root_height-.25)); NOT flat74filter',q_root_jointorder_neutralgeometry_and_points_unchanged=True,original_np_load_and_posewrites_unchanged=True,no_old700_or517_pass_relabelled=True,actual_SDK_or_birthinertia_or_skill_qualification=False)
