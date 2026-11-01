"""E1 original full-collider NPZbank identity composition, sourceonly.
Do not touch/load/hash/stat NPZ now; runtime helper is future separately admitted.
"""
from pathlib import Path
import ast,hashlib,json,difflib,time,traceback
B=Path(__file__).resolve().parent;T=B.parent.parent;RT='runtime/isaac/mod4/'

def main():
 for name,files in [('CURB141',['e1_full_pose_reset.py','curb20_entry_v3_full_pose_reset.py']),('SLOPE135',['e1_full_pose_reset.py'])]:
  root=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V1');meta=root/(RT+'MOD4_RESET_COLLISION_BANK.json');raw=meta.read_bytes();m=json.loads(raw);metaSHA=hashlib.sha256(raw).hexdigest()
  assert m['usd_sha256']=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87' and m['contract_sha256']=='cbcdacdf2b15d6a5fb1e5650e418443ff376ee23334e47e1ef36fcb79c32719f' and m['poses']==133 and m['bodies']==31
  template='''"""Original E1collider bank exactasset identity composition only.
Current generation/import is no I/O. Future call checks oldmetadata and exact
NPZSHA without modifying/rebuilding arrays; original np.load/q/argmin/posewrites
remain in the original E1 reset function. Not SDKgeometry/skill graduation.
"""
from pathlib import Path
import hashlib,json
from mod4v1_e1_reset_bank_compat import require_mod4v1_e1_reset_bank
META_SHA=__META_SHA__
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
'''.replace('__META_SHA__',repr(metaSHA))
  ast.parse(template);helper=root/(RT+'mod4v1_e1_collision_bank_compat.py')
  with helper.open('x',encoding='utf-8') as f:f.write(template)
  rows=[]
  for filename in files:
   p=root/(RT+filename);old=p.read_text(encoding='utf-8');a="        assert hashlib.sha256(Path(task.USD_PATH).read_bytes()).hexdigest() == meta['usd_sha256']\n        assert hashlib.sha256((task.MOD4_ISAAC / 'import_contract.json').read_bytes()).hexdigest() == meta['contract_sha256']"
   z="        from mod4v1_e1_collision_bank_compat import require_mod4v1_e1_collision_bank\n        env._mod4v1_e1_collision_bank_compatibility=require_mod4v1_e1_collision_bank(A/'MOD4_RESET_COLLISION_BANK.json',task.MOD4_ISAAC)"
   assert old.count(a)==1;new=old.replace(a,z,1);compile(new,str(p),'exec');reverse=new.replace(z,a,1);assert ast.dump(ast.parse(reverse),include_attributes=False)==ast.dump(ast.parse(old),include_attributes=False)
   p.write_text(new,encoding='utf-8',newline='');patch=''.join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='original/'+filename,tofile='new_composed_identity/'+filename));(root/(filename+'.IDENTITY_ONLY.patch')).write_text(patch,encoding='utf-8')
   rows.append(dict(relative=RT+filename,old_SHA=hashlib.sha256(old.encode()).hexdigest(),derived_SHA=hashlib.sha256(new.encode()).hexdigest(),reverse_identity_adapter_AST_exact=True,original_np_load_argmin_permutation_tangentclearance_q_root_writes_unchanged=True))
  with (root/'E1_COLLISION_BANK_SOURCE_ONLY_COMPOSITION_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='SOURCE_ONLY_ROUGH_BANK_COMPOSITION_NOT_NPZ_OR_SDK_PASS',checks=rows,metadata_SHA=metaSHA,NPZ_saved_original_SHA='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83',NPZ_not_statted_or_read_or_hashed_now=True,future_NPZ_exactbytes_and_actualSDK_pending=True,no_new_geometry_or_physics_precision_gate=True,helper_SHA=hashlib.sha256(helper.read_bytes()).hexdigest(),PT_SDK_SSH_GPU_budget_operations=0),f,indent=2)
  print(name,'rough collider banksource identityadapter prepared; originalpose selection/writes AST retained; NPZnotread')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('E1_ROUGH_BANK_GENERATOR_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),NPZ_PT_SDK_operations=0),f,indent=2)
  raise
