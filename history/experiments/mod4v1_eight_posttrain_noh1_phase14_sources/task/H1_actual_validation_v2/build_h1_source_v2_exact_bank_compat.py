"""Authorized minimal H1 V2 resetbank identity composition; pure local source/JSON."""
from pathlib import Path
import ast,hashlib,json,math,difflib
B=Path(__file__).resolve().parent;T=B.parent;V1=T/'staged_sources/H1_NORMAL_MOD4V1_SOURCE_V1';V2=T/'staged_sources/H1_NORMAL_MOD4V1_SOURCE_V2';RT='job0/runtime/isaac/mod4/'
manifest=json.loads((V1/'MOTHER453_INPUT_MANIFEST.json').read_text(encoding='utf-8'));by={r['relative']:r for r in manifest['files']}
assert not V2.exists();V2.mkdir()
# Copy only source/runtime overlays and provenance; old V1 remains immutable.
for p in V1.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(V1).as_posix()
 if rel.startswith('FINAL_') or rel=='INDEPENDENT_STATIC_REVIEW_v1.json':continue
 assert p.suffix.lower() in ('.py','.json','.md','.patch')
 dst=V2/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 with dst.open('xb') as f:f.write(p.read_bytes())
helper=Path(by[RT+'gas400_reset_bank_exact_compatibility_v1.py']['local_path']);bank=Path(by[RT+'reset_bank.json']['local_path']);old700=Path(by[RT+'RESET_BANK_700N_ORIGINAL_IMPORT_CONTRACT_EXACT.json']['local_path']);old400=Path(by['job0/assets/import_contract.json']['local_path']);new=Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1\assets\import_contract.json')
refs=[]
def read(p,expected=None):
 assert p.suffix in ('.json','.py');raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
 if expected:assert sha==expected,str(p)
 refs.append(dict(path=str(p),bytes=len(raw),SHA=sha));return raw
helperraw=read(helper,by[RT+'gas400_reset_bank_exact_compatibility_v1.py']['SHA']);bankraw=read(bank,by[RT+'reset_bank.json']['SHA']);r=json.loads(bankraw);a=json.loads(read(old700,'cbcdacdf2b15d6a5fb1e5650e418443ff376ee23334e47e1ef36fcb79c32719f'));mraw=read(old400,'517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49');m=json.loads(mraw);z=json.loads(read(new,'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'))
# Pure original helper declarations only: hashlib/json/math, no Torch/SDK/model imports.
ns={'__name__':'H1_exact_original_bank_CPU_source_proof','__file__':str(helper)};exec(compile(helperraw,str(helper),'exec'),ns)
four=ns['validate_four_gas_scalars'](a,m);ranges=ns['pose_gas_ranges'](r,z);assert ranges['all_poses']==133 and ranges['original_height_filter_selected_poses']==74
assert m['gas_springs']==z['gas_springs'] and m['joints']==z['joints']
allowed_top={'bodies','enhancement','leg_motor','wheel_motor','physics_dt_s'}
assert all(m[k]==z[k] for k in m if k not in allowed_top)
changed=[n for n in m['bodies'] if m['bodies'][n]!=z['bodies'][n]];assert set(changed)=={'chassis','left_shin','right_shin'}
allowed_body={'mass_kg','com_m','diagonal_inertia_kg_m2','principal_axes_wxyz','enhancement_mass_basis'}
for n in changed:
 for key in set(m['bodies'][n])|set(z['bodies'][n]):
  if key not in allowed_body:assert m['bodies'][n].get(key)==z['bodies'][n].get(key)
code='''"""H1 exact700->517c gas proof +517c->bae threebody nominal identity composition.
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

def require_mod4v1_h1_reset_bank(bank_path,new_contract_path,raw,*,actual_contract_SHA=None):
 here=Path(__file__).resolve().parent;bank_path=Path(bank_path).resolve();contract=Path(new_contract_path).resolve()
 require(bank_path==here/'reset_bank.json' and not bank_path.is_symlink(),'Exact original adjacent H1 bank')
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
 return dict(kind='H1_MOD4V1_EXACT_COMPOSED_RESETBANK_COMPATIBILITY_V2',new_contract_SHA=identity.contract_sha256,new_USD_SHA=identity.usd_sha256,original_bank_SHA=BANK_SHA,original700_SHA=OLD_CONTRACT_SHA,typed400_SHA=OLD400_SHA,original_four_gas_scalar_proof=four,authorized_changed_bodies=changed,pose_ranges=ranges,geometry_joint_order_frames_and_fixedSI_unchanged=True,original_selector_q_rng_and_single_reset_unchanged=True,not_old517_pass_relabelled=True,actual_SDK_or_skill_qualification=False)
'''
ast.parse(code)
p=V2/(RT+'mod4v1_h1_reset_bank_compat.py');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(code,encoding='utf-8')
(V2/(RT+'H1_TYPED400_ORIGINAL_IMPORT_CONTRACT_EXACT.json')).write_bytes(mraw)
source=Path(by[RT+'scut_flat_rescue.py']['local_path']);old=read(source,by[RT+'scut_flat_rescue.py']['SHA']).decode('utf-8');s=old
s=s.replace('from gas400_reset_bank_exact_compatibility_v1 import require_exact_gas400_reset_bank','from mod4v1_h1_reset_bank_compat import require_mod4v1_h1_reset_bank')
s=s.replace("require_exact_gas400_reset_bank(source,task.MOD4_ISAAC/'import_contract.json',raw,actual_contract_SHA=actual)","env._mod4v1_h1_bank_compatibility=require_mod4v1_h1_reset_bank(source,task.MOD4_ISAAC/'import_contract.json',raw,actual_contract_SHA=actual)")
assert s!=old;ast.parse(s);(V2/(RT+'scut_flat_rescue.py')).write_text(s,encoding='utf-8',newline='')
# Reverse only adapter import/call destination + diagnostic assignment -> original AST.
reverse=s.replace('from mod4v1_h1_reset_bank_compat import require_mod4v1_h1_reset_bank','from gas400_reset_bank_exact_compatibility_v1 import require_exact_gas400_reset_bank').replace('env._mod4v1_h1_bank_compatibility=require_mod4v1_h1_reset_bank(','require_exact_gas400_reset_bank(')
assert ast.dump(ast.parse(reverse),include_attributes=False)==ast.dump(ast.parse(old),include_attributes=False)
proof=dict(kind='H1_SOURCE_V2_BANK_COMPATIBILITY_CPU_SOURCE_PROOF',original_four_gas_scalar_proof=four,new3body_names=changed,new400_gas_joints_unchanged=True,pose_ranges=ranges,source_Scuts_reverse_adapter_AST_exact=True,original133_74_selector_q_RNG_unchanged=True,PT_SDK_GPU_operations=0,input_texts=refs,prior_failure=str(B/'H1_FRESH_ATTEMPT2_BANK_COMPAT_FAILURE.json'))
(V2/'H1_BANK_COMPAT_SOURCE_PROOF_V2.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
(V2/'H1_V2_MINIMAL_BANK_DIFF.patch').write_text(''.join(difflib.unified_diff(old.splitlines(keepends=True),s.splitlines(keepends=True),fromfile='actual453/scut_flat_rescue.py',tofile='V2/scut_flat_rescue.py')),encoding='utf-8')
outputs=[]
for p in sorted(V2.rglob('*')):
 if not p.is_file():continue
 raw=p.read_bytes();row=dict(relative=p.relative_to(V2).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
 if p.suffix=='.py':tree=ast.parse(raw);compile(tree,str(p),'exec');row['AST_SHA']=hashlib.sha256(ast.dump(tree,include_attributes=False).encode()).hexdigest()
 outputs.append(row)
index=dict(kind='H1_NORMAL_MOD4V1_SOURCE_V2_EXACT_BANK_COMPOSITION',parent_V1_index_path=str(V1/'FINAL_SOURCE_INDEX.json'),parent_V1_index_SHA=hashlib.sha256((V1/'FINAL_SOURCE_INDEX.json').read_bytes()).hexdigest(),actualmother453_manifest_SHA='97cdcde4a891359a5f1209fdad1614bf87629e0c3d3a40ce9018dc1fe9e2426b',minimal_changes=[RT+'scut_flat_rescue.py',RT+'mod4v1_h1_reset_bank_compat.py',RT+'H1_TYPED400_ORIGINAL_IMPORT_CONTRACT_EXACT.json'],original_H1_for24_phase_geometry_reward_physics_sources_unchanged=True,static_proof=proof,outputs=outputs,PT_SDK_operations=0,actualFresh80_not_yet_passed=True,oldV1_and_run_cases_unmodified=True)
(V2/'FINAL_SOURCE_INDEX.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
print(json.dumps(dict(source_v2=str(V2),index_SHA=hashlib.sha256((V2/'FINAL_SOURCE_INDEX.json').read_bytes()).hexdigest(),outputs=len(outputs),CPU_composed133_74_pass=True,PT_SDK_operations=0),indent=2))
