"""New W35 reset qualification: read its used NPZ fields once, preserve sampler/pose."""
from pathlib import Path
import ast, hashlib, importlib.util, json, time, traceback

HERE=Path(__file__).resolve().parent;W=HERE.parents[2]
BASE=W/'MOD4_S4_GATE_FIRST_FINAL_FROZEN35_20261015/payload/runtime/isaac/mod4'
FROZEN=HERE/'E0_runtime50_gas400_candidate_v1'
DEST=HERE/'W35_nearest250_reset_gas400_mutable_candidate_v1'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(array):
 import numpy as np
 a=np.ascontiguousarray(array)
 return dict(shape=list(a.shape),dtype=a.dtype.str,SHA=hashlib.sha256(a.tobytes()).hexdigest())
def main():
 assert not DEST.exists();DEST.mkdir()
 import numpy as np
 meta_path=BASE/'MOD4_RESET_COLLISION_BANK.json';meta=json.loads(meta_path.read_bytes())
 assert meta['contract_sha256']=='cbcdacdf2b15d6a5fb1e5650e418443ff376ee23334e47e1ef36fcb79c32719f'
 assert meta['usd_sha256']=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
 bank_path=BASE/'MOD4_RESET_COLLISION_BANK.npz';before=bank_path.stat()
 # Actual purpose is new400N hard-limit feasibility of the exact USED reset
 # inputs. The existing producer fullSHA is reused, not recomputed for Git.
 with np.load(bank_path,allow_pickle=False) as bank:
  fields=list(bank.files);names=[str(x) for x in bank['joint_names']];heights=bank['root_height'];pick=int(np.argmin(abs(heights-.25)))
  q=bank['q'][pick];points=bank['points_root'][pick]
  assert len(names)==len(set(names))==len(q)==30 and np.isfinite(q).all() and np.isfinite(points).all()
  gas={name:float(q[names.index(name)]) for name in ('left_gas_slide','right_gas_slide')}
  lower=-.0267046843609;upper=.020639440248416612
  assert all(lower<=value<=upper for value in gas.values())
  witness=dict(fields=fields,joint_names=names,pick=pick,root_height_m=float(heights[pick]),
   root_height_array=digest(heights),selected_q=digest(q),selected_points_root=digest(points),selected_gas_q_m=gas,
   all_poses=len(heights),npz_file_bytes=before.st_size,npz_producer_SHA='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83',
   original_npz_not_rehashed=True,no_pose_edit_clamp_or_resampling=True)
 after=bank_path.stat();assert before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns
 new_contract=FROZEN/'assets/import_contract.json';old_contract=FROZEN/'isaac/mod4/RESET_BANK_700N_ORIGINAL_IMPORT_CONTRACT_EXACT.json'
 spec=importlib.util.spec_from_file_location('exact_four_scalar_contract_only',FROZEN/'isaac/mod4/gas400_reset_bank_exact_compatibility_v1.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 changes=module.validate_four_gas_scalars(json.loads(old_contract.read_bytes()),json.loads(new_contract.read_bytes()))
 assert len(changes)==4
 constants=dict(old_meta_SHA=H(meta_path),old_contract_SHA=H(old_contract),new_contract_SHA=H(new_contract),
                nominal400_layer_SHA=H(FROZEN/'assets/robot.usd'),old_USD_SHA=meta['usd_sha256'],witness=witness)
 helper='''"""W35 exact used-bank compatibility; no flat74 assumption, no pose/RNG/physics edit."""
from pathlib import Path
import hashlib,json,numpy as np
from gas400_reset_bank_exact_compatibility_v1 import validate_four_gas_scalars
PIN = __PIN__
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
             original_geometry_dependency_SHA=PIN['old_USD_SHA'],actual_original_dependency_fullSHA_from_install_receipt=True,
             selected_reset_inputs_verified=False,actual_SDK_or_GPU_qualification=False)
def verify_original_W35_selected_bank(bank,pick):
 w=PIN['witness'];names=[str(x) for x in bank['joint_names']]
 require(list(bank.files)==w['fields'] and names==w['joint_names'],'original W35 bank fields/joint order changed')
 require(int(np.argmin(abs(bank['root_height']-.25)))==pick==w['pick'],'original nearest .25 selection changed')
 require(digest(bank['root_height'])==w['root_height_array'],'original root-height selector inputs changed')
 require(digest(bank['q'][pick])==w['selected_q'] and digest(bank['points_root'][pick])==w['selected_points_root'],'original selected pose/full collider footprint changed')
 require(bank.zip.fp is not None,'original np.load bank must remain open for caller')
 return dict(schema='mod4.W35.nearest250.reset.gas400.used_inputs.v1',selected_pose_index=pick,
             root_height_m=w['root_height_m'],selected_gas_q_m=w['selected_gas_q_m'],
             original_nearest250_sampler_q_all30_full_points_joint_order_unchanged=True,
             old_npz_fullSHA=w['npz_producer_SHA'],old_npz_fullSHA_not_rehashed=True,
             no_pose_edit_clamp_RNG_reset_or_physical_gate_change=True,actual_SDK_or_GPU_qualification=False)
'''.replace('__PIN__',repr(constants))
 hp=DEST/'W35_gas400_exact_selected_reset_compatibility_v1.py';hp.write_text(helper,encoding='utf8');ast.parse(helper)
 source=(BASE/'e1_full_pose_reset.py').read_text('utf8')
 old="        assert hashlib.sha256(Path(task.USD_PATH).read_bytes()).hexdigest() == meta['usd_sha256']\n        assert hashlib.sha256((task.MOD4_ISAAC / 'import_contract.json').read_bytes()).hexdigest() == meta['contract_sha256']"
 new="        actual_usd_sha=hashlib.sha256(Path(task.USD_PATH).read_bytes()).hexdigest()\n        actual_contract_sha=hashlib.sha256((task.MOD4_ISAAC / 'import_contract.json').read_bytes()).hexdigest()\n        if actual_usd_sha != meta['usd_sha256'] or actual_contract_sha != meta['contract_sha256']:\n            from W35_gas400_exact_selected_reset_compatibility_v1 import require_W35_exact_four_scalar_asset\n            env._w35_gas400_asset_compatibility = require_W35_exact_four_scalar_asset(meta, A/'MOD4_RESET_COLLISION_BANK.json', task.USD_PATH, task.MOD4_ISAAC/'import_contract.json')"
 assert source.count(old)==1;source=source.replace(old,new)
 old="        pick = int(np.argmin(abs(bank['root_height'] - .25)))"
 new=old+"\n        if hasattr(env, '_w35_gas400_asset_compatibility'):\n            from W35_gas400_exact_selected_reset_compatibility_v1 import verify_original_W35_selected_bank\n            env._w35_gas400_selected_bank_compatibility = verify_original_W35_selected_bank(bank,pick)"
 assert source.count(old)==1;source=source.replace(old,new)
 patched=DEST/'e1_full_pose_reset.py';patched.write_text(source,encoding='utf8');ast.parse(source)
 # Compile source and exercise only the used-input identity helper on the one
 # loaded original bank, independently of any simulator or physical episode.
 sys_path=__import__('sys').path;sys_path.insert(0,str(FROZEN/'isaac/mod4'))
 sp=importlib.util.spec_from_file_location('W35_actual_used_inputs_CPU',hp);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 with np.load(bank_path,allow_pickle=False) as bank:checked=m.verify_original_W35_selected_bank(bank,int(np.argmin(abs(bank['root_height']-.25))))
 report=dict(attempt_id='W35_NEAREST250_GAS400_RESET_SOURCE_CPU_20261027_V1',epoch=time.time(),source_meta=dict(path=str(meta_path),SHA=H(meta_path)),
  source_bank=dict(path=str(bank_path),bytes=before.st_size,SHA=witness['npz_producer_SHA'],SHA_reused_from_existing_receipt=True),
  actual_used_inputs=witness,contract_exact_four_changes=changes,CPU_helper_used_input_check=checked,
  old_source=dict(path=str(BASE/'e1_full_pose_reset.py'),SHA=H(BASE/'e1_full_pose_reset.py')),
  helper=dict(path=str(hp),SHA=H(hp)),candidate_reset=dict(path=str(patched),SHA=H(patched)),
  preserves_original_sampler_RNG_reset_order_pose_mesh_and_perenv2mm_guard=True,no_new_physical_gate=True,
  source_mutable_pending=True,E0_frozen_unchanged=True,actual_GPU_or_PPO_or_target_SDK=False,Git_status='pending_root_ordinary_supplement')
 with (HERE/'reports/W35_NEAREST250_EXACT_GAS400_RESET_SOURCE_CPU_ACTUAL_V1.json').open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(selected_pose=pick,root_height_m=witness['root_height_m'],gas_q=gas,candidate=str(DEST),actual_GPU=False)))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/('reports/W35_SELECTED_RESET_SOURCE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc(),no_GPU=True,partial_candidate_retained=True),indent=2),encoding='utf8');raise
