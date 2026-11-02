"""Exact700→nominal400 source compatibility for the unchanged flat reset bank.

Not a general hash bypass. No pose edit/clamp, random draw, SDK/physics setter,
model, USD or environment restore. Original per-environment2mm guard remains.
"""
from pathlib import Path
import hashlib,json,math
OLD_CONTRACT_SHA='cbcdacdf2b15d6a5fb1e5650e418443ff376ee23334e47e1ef36fcb79c32719f'
NEW_CONTRACT_SHA='517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49'
BANK_SHA='48be349c9bae1ec089b8bfb46ccc79085576e14bf373f6cb514027c3c155e50f'
BANK_BYTES=157944
OLD_CONTRACT_COPY='RESET_BANK_700N_ORIGINAL_IMPORT_CONTRACT_EXACT.json'
GAS=('left_gas_slide','right_gas_slide')
LOWER=-.0267046843609
UPPER=.020639440248416612
def require(value,message):
 if not value:raise RuntimeError(message)
def H(raw):return hashlib.sha256(raw).hexdigest()
def differences(a,b,path=()):
 require(type(a) is type(b),'contract type changed '+repr(path))
 if isinstance(a,dict):
  require(set(a)==set(b),'contract keys changed '+repr(path));result=[]
  for key in a:result.extend(differences(a[key],b[key],path+(key,)))
  return result
 if isinstance(a,list):
  require(len(a)==len(b),'contract list width changed '+repr(path));result=[]
  for i,(x,y) in enumerate(zip(a,b)):result.extend(differences(x,y,path+(i,)))
  return result
 return [] if a==b else [(path,a,b)]
def validate_four_gas_scalars(old,new):
 expected={}
 for name in GAS:
  expected[('gas_springs',name,'stiffness_n_m')]=(3500.,2000.)
  expected[('joints',name,'limits_si',1)]=(.0352033350025,UPPER)
 found=differences(old,new)
 require(len(found)==4 and {row[0] for row in found}==set(expected),'only authorized gas2k +2upper changes permitted')
 for path,a,b in found:require((a,b)==expected[path],'unauthorized gas scalar '+repr(path))
 for name in GAS:require(new['joints'][name]['limits_si']==[LOWER,UPPER],'original lower and exact new200mm cap')
 return [dict(path=list(path),old_value=a,new_value=b) for path,a,b in found]
def pose_gas_ranges(raw,new):
 poses=raw['poses'];require(isinstance(poses,list) and poses,'nonempty exact flat reset poses')
 ranges={name:dict(min_q_m=float('inf'),max_q_m=float('-inf')) for name in GAS};selected=0
 for i,pose in enumerate(poses):
  height=pose['root_height_m'];require(type(height) in (int,float) and math.isfinite(height),'finite reset rootheight')
  selected+=int(.24<=height<=.272)
  for name in GAS:
   require(name in pose['joint_pos'],'reset bank gas coordinate missing '+name)
   q=pose['joint_pos'][name];require(type(q) in (int,float) and math.isfinite(q),'finite reset gas coordinate')
   lo,hi=new['joints'][name]['limits_si'];require(lo<=q<=hi,'unchanged bank gas pose outside new hard limits: pose'+str(i)+' '+name)
   r=ranges[name];r['min_q_m']=min(r['min_q_m'],q);r['max_q_m']=max(r['max_q_m'],q)
 for name,r in ranges.items():r.update(new_lower_q_m=new['joints'][name]['limits_si'][0],new_upper_q_m=new['joints'][name]['limits_si'][1],lower_margin_m=r['min_q_m']-new['joints'][name]['limits_si'][0],upper_margin_m=new['joints'][name]['limits_si'][1]-r['max_q_m'])
 return dict(all_poses=len(poses),original_height_filter_selected_poses=selected,gas_ranges=ranges,poses_changed_or_clamped=False)
def require_exact_gas400_reset_bank(bank_path,new_contract_path,raw,*,actual_contract_SHA=None):
 """Called only when the original exact old hash comparison does not match."""
 here=Path(__file__).resolve().parent;bank_path=Path(bank_path).resolve();new_contract_path=Path(new_contract_path).resolve()
 require(bank_path.parent==here and bank_path.name=='reset_bank.json' and not bank_path.is_symlink(),'exact adjacent original bank only')
 require(new_contract_path.name=='import_contract.json' and not new_contract_path.is_symlink(),'actual task contract required')
 bank_bytes=bank_path.read_bytes();require(len(bank_bytes)==BANK_BYTES and H(bank_bytes)==BANK_SHA,'reset bank original producer bytes/SHA changed')
 require(json.loads(bank_bytes)==raw and raw['contract_sha256']==OLD_CONTRACT_SHA,'decoded bank/old contract provenance mismatch')
 old_path=here/OLD_CONTRACT_COPY;require(not old_path.is_symlink(),'old contract evidence must be regular')
 old_bytes=old_path.read_bytes();new_bytes=new_contract_path.read_bytes()
 require(H(old_bytes)==OLD_CONTRACT_SHA and H(new_bytes)==NEW_CONTRACT_SHA,'only pinned original700 and authorized nominal400 contracts compatible')
 if actual_contract_SHA is not None:require(actual_contract_SHA==NEW_CONTRACT_SHA,'caller actual contract hash differs')
 old=json.loads(old_bytes);new=json.loads(new_bytes);changes=validate_four_gas_scalars(old,new);ranges=pose_gas_ranges(raw,new)
 require(ranges['all_poses']==133 and ranges['original_height_filter_selected_poses']==74,'exact original133 bank /74 filtered population')
 return dict(schema='mod4.gas400.flat_reset_bank.exact_compatibility.v1',passed=True,source_only=True,
  old_contract_SHA=OLD_CONTRACT_SHA,new_contract_SHA=NEW_CONTRACT_SHA,reset_bank_SHA=BANK_SHA,
  authorized_four_scalar_changes=changes,pose_ranges=ranges,
  geometry_joint_frames_joint_order_all_other_contract_fields_unchanged=True,
  original_reset_selection_writes_RNG_cache_and_perenv2mm_guard_unchanged=True,
  actual_SDK_scene_reset_or_PhysX_validated=False,hardware_force_curve_calibrated=False)
def check_runtime_source(runtime_dir):
 """Target CPU entry hook; small JSON/hash/range checks, no SDK scene/model."""
 runtime=Path(runtime_dir).resolve();require(runtime==Path(__file__).resolve().parent,'exact installed runtime helper directory')
 source=runtime/'reset_bank.json';raw=json.loads(source.read_bytes())
 return require_exact_gas400_reset_bank(source,runtime/'import_contract.json',raw,actual_contract_SHA=NEW_CONTRACT_SHA)
