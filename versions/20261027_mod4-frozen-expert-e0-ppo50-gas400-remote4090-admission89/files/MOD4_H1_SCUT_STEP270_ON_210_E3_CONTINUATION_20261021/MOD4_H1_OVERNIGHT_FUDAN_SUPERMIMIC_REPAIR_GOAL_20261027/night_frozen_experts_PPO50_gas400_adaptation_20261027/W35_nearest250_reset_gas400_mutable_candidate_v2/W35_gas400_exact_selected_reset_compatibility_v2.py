"""W35 exact used-bank compatibility; no flat74 assumption, no pose/RNG/physics edit."""
from pathlib import Path
import hashlib,json,numpy as np
from gas400_reset_bank_exact_compatibility_v1 import validate_four_gas_scalars
PIN = {'old_meta_SHA': '7d79108982c8e0c146a5a5440160e61c0e6a0675f6b668577babb9aff4a570e7', 'old_contract_SHA': 'cbcdacdf2b15d6a5fb1e5650e418443ff376ee23334e47e1ef36fcb79c32719f', 'new_contract_SHA': '517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49', 'nominal400_layer_SHA': 'bce9a7740fd9a2e2252d34a09c1fef7dab70e2a65f9d0ee2e422cec5f12c60e4', 'old_USD_SHA': '694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87', 'witness': {'fields': ['points_root', 'collider_ids', 'q', 'joint_names', 'root_height'], 'joint_names': ['left_hip', 'left_rocker_pin', 'left_distal_pin', 'left_knee', 'left_wheel_spin', 'left_gas_pin', 'left_gas_slide', 'left_crank', 'left_coupler_pin', 'left_drive_hip_spin', 'left_drive_input_spin', 'right_hip', 'right_rocker_pin', 'right_distal_pin', 'right_knee', 'right_wheel_spin', 'right_gas_pin', 'right_gas_slide', 'right_crank', 'right_coupler_pin', 'right_drive_hip_spin', 'right_drive_input_spin', 'guide_roller_00', 'guide_roller_01', 'guide_roller_02', 'guide_roller_03', 'guide_roller_04', 'guide_roller_05', 'guide_roller_06', 'guide_roller_07'], 'pick': 34, 'root_height_m': 0.252, 'root_height_array': {'shape': [133], 'dtype': '<f8', 'SHA': '1c2b6cd02b1f037e7186ff22aa1199c16455013acad3a5cc7dc14ae56f339128'}, 'selected_q': {'shape': [30], 'dtype': '<f8', 'SHA': '739662501f2791e502bbec95d6d73f0ffad02b6dcaa13a24454703beaa411d69'}, 'selected_points_root': {'shape': [25200, 3], 'dtype': '<f8', 'SHA': '5885beee8fdc0f470f1e749338ab97f7bca2e1d662fd292648cf0386028081d5'}, 'selected_gas_q_m': {'left_gas_slide': -0.017186211577957116, 'right_gas_slide': -0.017186211577954556}, 'all_poses': 133, 'npz_file_bytes': 32022178, 'npz_producer_SHA': '78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83', 'original_npz_not_rehashed': True, 'no_pose_edit_clamp_or_resampling': True}}
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(v,m):
 if not v:raise RuntimeError(m)
def digest(a):
 a=np.ascontiguousarray(a)
 return dict(shape=list(a.shape),dtype=a.dtype.str,SHA=hashlib.sha256(a.tobytes()).hexdigest())
def require_W35_exact_four_scalar_asset(meta,meta_path,usd_path,contract_path):
 here=Path(__file__).resolve().parent;meta_path=Path(meta_path);usd_path=Path(usd_path);contract_path=Path(contract_path)
 require(meta_path.resolve()==here/'MOD4_RESET_COLLISION_BANK.json','exact adjacent W35 metadata required')
 require(H(meta_path)==PIN['old_meta_SHA'] and json.loads(meta_path.read_bytes())==meta,'original W35 metadata bytes changed')
 require(meta['usd_sha256']==PIN['old_USD_SHA'] and meta['contract_sha256']==PIN['old_contract_SHA'],'original W35 producer identity mismatch')
 old=here/'RESET_BANK_700N_ORIGINAL_IMPORT_CONTRACT_EXACT.json'
 require(H(old)==PIN['old_contract_SHA'] and H(contract_path)==PIN['new_contract_SHA'],'only exact old700/new400 contracts admitted')
 require(H(usd_path)==PIN['nominal400_layer_SHA'],'only the independently CPU-composed exact nominal400 layer admitted')
 require((usd_path.parent/'source_700N/robot.usd').is_file(),'original geometry dependency missing')
 changes=validate_four_gas_scalars(json.loads(old.read_bytes()),json.loads(contract_path.read_bytes()))
 return dict(schema='mod4.W35.nearest250.reset.gas400.exact_asset.v1',authorized_four_scalar_changes=changes,
             original_geometry_dependency_SHA=PIN['old_USD_SHA'],actual_original_dependency_install_receipt_required_from_caller=True,
             selected_reset_inputs_verified=False,actual_SDK_or_GPU_qualification=False)
def verify_original_W35_selected_bank(bank,pick):
 w=PIN['witness'];names=[str(x) for x in bank['joint_names']]
 require(list(bank.files)==w['fields'] and names==w['joint_names'],'original W35 bank fields/joint order changed')
 require(int(np.argmin(abs(bank['root_height']-.25)))==pick==w['pick'],'original nearest .25 selection changed')
 require(digest(bank['root_height'])==w['root_height_array'],'original root-height selector inputs changed')
 require(digest(bank['q'][pick])==w['selected_q'] and digest(bank['points_root'][pick])==w['selected_points_root'],'original selected pose/full collider footprint changed')
 return dict(schema='mod4.W35.nearest250.reset.gas400.used_inputs.v1',selected_pose_index=pick,
             root_height_m=w['root_height_m'],selected_gas_q_m=w['selected_gas_q_m'],
             original_nearest250_sampler_q_all30_full_points_joint_order_unchanged=True,
             old_npz_fullSHA=w['npz_producer_SHA'],old_npz_fullSHA_not_rehashed=True,
             no_pose_edit_clamp_RNG_reset_or_physical_gate_change=True,actual_SDK_or_GPU_qualification=False)
