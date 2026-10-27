"""New purpose: unchanged small reset-bank JSON compatibility. No PT/USD/raw."""
from pathlib import Path
import sys,ast,json,hashlib,copy,traceback,importlib.util,types
from unittest.mock import patch
import numpy as np
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent
B=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027/payloads/h1'
OLD=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027/payloads_r5/h1/job0/runtime/isaac/mod4/import_contract.json'
RT=B/'job0/runtime/isaac/mod4'
def H(raw):return hashlib.sha256(raw).hexdigest()
def write(p,value):
 p.parent.mkdir(parents=True,exist_ok=True);raw=value if isinstance(value,bytes) else json.dumps(value,indent=2,allow_nan=False).encode()
 with p.open('xb') as f:f.write(raw)
 return H(raw)
def module(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m);return m
def main():
 checks=[]
 def ok(name,fn):
  v=fn();checks.append(dict(name=name,passed=True));return v
 def no(name,fn):
  try:fn()
  except (RuntimeError,ValueError,KeyError,TypeError,AssertionError) as e:checks.append(dict(name=name,passed=True,rejected=str(e)));return
  raise AssertionError('bad case accepted '+name)
 old_bytes=OLD.read_bytes();new_bytes=(RT/'import_contract.json').read_bytes();bank_bytes=(RT/'reset_bank.json').read_bytes();original=(RT/'scut_flat_rescue.py').read_bytes()
 helper=module('reset_compat_source_definition',D/'gas400_reset_bank_exact_compatibility_v1.py')
 assert H(old_bytes)==helper.OLD_CONTRACT_SHA and H(new_bytes)==helper.NEW_CONTRACT_SHA and H(bank_bytes)==helper.BANK_SHA and len(bank_bytes)==helper.BANK_BYTES
 manifest=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());rows={r['relative']:r for r in manifest['files']}
 for name,raw in [('reset_bank.json',bank_bytes),('import_contract.json',new_bytes),('scut_flat_rescue.py',original)]:
  r=rows['job0/runtime/isaac/mod4/'+name];assert H(raw)==r['SHA'] and len(raw)==r['bytes']
 checks.append(dict(name='real small bank and actual contracts match producer/source manifest pins',passed=True))
 old=json.loads(old_bytes);new=json.loads(new_bytes);bank=json.loads(bank_bytes)
 changes=ok('exactly four authorized gas scalars and no other contract change',lambda:helper.validate_four_gas_scalars(old,new))
 ranges=ok('all133 poses inside new gas bounds; original74 selection',lambda:helper.pose_gas_ranges(bank,new))
 assert ranges['all_poses']==133 and ranges['original_height_filter_selected_poses']==74
 bad=copy.deepcopy(new);bad['joints']['left_gas_slide']['local_pos0'][0]+=.001
 no('extra CAD joint-frame change',lambda:helper.validate_four_gas_scalars(old,bad))
 bad=copy.deepcopy(new);bad['joints']['left_gas_slide']['limits_si'][0]-=.001
 no('lower limit widening',lambda:helper.validate_four_gas_scalars(old,bad))
 bad=copy.deepcopy(new);bad['gas_springs']['left_gas_slide']['stiffness_n_m']=400.
 no('400N cannot become400N/m',lambda:helper.validate_four_gas_scalars(old,bad))
 bad=copy.deepcopy(bank);bad['poses'][0]['joint_pos']['left_gas_slide']=helper.UPPER+1e-9
 no('gas pose exceeds new upper, no clamp',lambda:helper.pose_gas_ranges(bad,new))
 bad=copy.deepcopy(bank);bad['poses'][0]['joint_pos']['right_gas_slide']=float('nan')
 no('nonfinite gas pose',lambda:helper.pose_gas_ranges(bad,new))
 # Derive one guard branch only; preserve every original statement afterward.
 needle=b"        if actual!=raw['contract_sha256']:raise RuntimeError('reset-bank contract hash mismatch')"
 assert original.count(needle)==1
 nl=b'\r\n' if b'\r\n' in original else b'\n'
 replacement=nl.join([b"        if actual!=raw['contract_sha256']:",b"            from gas400_reset_bank_exact_compatibility_v1 import require_exact_gas400_reset_bank",b"            require_exact_gas400_reset_bank(source,task.MOD4_ISAAC/'import_contract.json',raw,actual_contract_SHA=actual)"])
 candidate=original.replace(needle,replacement);C=D/'candidate_runtime_NOT_A_PAYLOAD'
 write(C/'scut_flat_rescue.py',candidate);write(C/'gas400_reset_bank_exact_compatibility_v1.py',(D/'gas400_reset_bank_exact_compatibility_v1.py').read_bytes())
 write(C/helper.OLD_CONTRACT_COPY,old_bytes)
 # Unchanged byteidentical small source fixtures, not replacement assets.
 write(C/'reset_bank.json',bank_bytes);write(C/'import_contract.json',new_bytes)
 orig_tree=ast.parse(original);new_tree=ast.parse(candidate)
 functions=lambda tree:{n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
 of=functions(orig_tree);nf=functions(new_tree);assert set(of)==set(nf)
 assert all(ast.dump(of[k])==ast.dump(nf[k]) for k in of if k!='consistent_reset')
 og=copy.deepcopy(of['consistent_reset']);ng=copy.deepcopy(nf['consistent_reset'])
 def without_admission(tree):
  class Remove(ast.NodeTransformer):
   def visit_If(self,node):
    if ast.unparse(node.test)=="actual != raw['contract_sha256']":return None
    return self.generic_visit(node)
  return Remove().visit(tree)
 assert ast.dump(without_admission(og))==ast.dump(without_admission(ng))
 checks.append(dict(name='all reset selection/cache/targets/writes/RNG and other functions AST exact except typed hash branch',passed=True))
 freeze_bytes=(B/'job0/runtime/reports/SOURCE_FREEZE.json').read_bytes();freeze=json.loads(freeze_bytes)
 assert freeze['sha256']['isaac/mod4/scut_flat_rescue.py']==H(original)
 assert freeze_bytes.count(H(original).encode())==1
 newfreeze=freeze_bytes.replace(H(original).encode(),H(candidate).encode())
 assert json.loads(newfreeze)==dict(freeze,sha256=dict(freeze['sha256'],**{'isaac/mod4/scut_flat_rescue.py':H(candidate)}))
 write(D/'candidate_SOURCE_FREEZE.json',newfreeze);checks.append(dict(name='SOURCE_FREEZE only original scut row replacement',passed=True))
 sys.path.insert(0,str(C));compat=module('gas400_reset_bank_exact_compatibility_v1',C/'gas400_reset_bank_exact_compatibility_v1.py')
 compatibility=ok('real unchanged bank installed-path CPU compatibility',lambda:compat.check_runtime_source(C))
 no('caller wrong actual hash',lambda:compat.require_exact_gas400_reset_bank(C/'reset_bank.json',C/'import_contract.json',bank,actual_contract_SHA=helper.OLD_CONTRACT_SHA))
 badraw=copy.deepcopy(bank);badraw['poses'][0]['joint_pos']['left_gas_slide']=helper.UPPER+1.
 no('decoded pose mutation cannot masquerade as original bank',lambda:compat.require_exact_gas400_reset_bank(C/'reset_bank.json',C/'import_contract.json',badraw))
 # Existing original FK code, no from_sources/IK/USD calls. All133 input poses
 # are transformed once from authored frames and original X-axis convention.
 J=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026'
 sys.path.insert(0,str(J/'agent_reference_retarget_cpu'))
 from own_usd_closed_chain_ik_v1 import OwnUsdKinematics,transform
 from supermimic_reference_adapter_v1 import quat_to_mat
 conv_path=L/'agent_MOD4_step_reference_conversion_candidate_v1/mod4_step_reference_conversion_v1.py'
 conv=module('recorded_kinematics_for_new_reset_purpose',conv_path)
 geo_path=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027/DERIVED_GEOMETRY_20260928.json';geometry=json.loads(geo_path.read_bytes())
 assert H(geo_path.read_bytes())=='461f6b44e6014c72a755a0db5136fa8d45bd5b53b6318ee4b38221a4c597bc4d'
 kin=conv.build_recorded_kinematics(new,geometry,OwnUsdKinematics,transform,quat_to_mat)
 closure=[]
 for i,pose in enumerate(bank['poses']):
  q=np.array([pose['joint_pos'].get(name,0.) for name in kin.joint_names]);poses=kin.forward(q,enforce_transmission=False)
  residual=np.linalg.norm(kin.closure_vectors(poses),axis=-1)
  closure.append(dict(pose=i,root_height_m=pose['root_height_m'],selected=.24<=pose['root_height_m']<=.272,max_closure_m=float(residual.max()),per_closure_m=residual.tolist(),original_claimed_closure_m=pose.get('closure_m')))
 assert max(r['max_closure_m'] for r in closure)<=.002
 checks.append(dict(name='all133 unchanged bank poses original2mm closure source check',passed=True))
 # Execute the real original and candidate reset FUNCTIONS on fake write-only
 # robots, never an SDK scene. Same RNG state gives identical selections.
 import torch
 from types import SimpleNamespace as S
 torch.set_num_threads(2);native_contract=json.loads((B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json').read_bytes());names=native_contract['expected_runtime_joint_names']
 class Scene(dict):pass
 class Robot:
  def __init__(self,n):self.joint_names=names;self.data=S(root_state_w=torch.arange(n*13,dtype=torch.float32).reshape(n,13));self.writes=[]
  def write_joint_state_to_sim(self,q,v,env_ids):self.writes.append(('joint',q.clone(),v.clone(),env_ids.clone()))
  def write_root_state_to_sim(self,root,env_ids):self.writes.append(('root',root.clone(),env_ids.clone()))
 def environment():
  scene=Scene(robot=Robot(4));scene.env_origins=torch.arange(12,dtype=torch.float32).reshape(4,3)*.01
  return S(num_envs=4,device='cpu',scene=scene,height=torch.zeros(4))
 legacy=D/'legacy_contract_CPU_fixture';write(legacy/'import_contract.json',old_bytes)
 original_module=module('original_scut_reset_for_new_CPU_purpose',RT/'scut_flat_rescue.py');candidate_module=module('candidate_scut_reset_for_new_CPU_purpose',C/'scut_flat_rescue.py')
 task=S(TERRAIN='flat',MOD4_ISAAC=legacy,height_cmd=lambda env:env.height)
 rng=torch.random.get_rng_state().clone()
 try:
  for label,ids in [('selected',torch.tensor([0,2])),('all',None),('empty',torch.empty(0,dtype=torch.long))]:
   torch.manual_seed(20261027);a=environment();task.MOD4_ISAAC=legacy
   with patch.dict(sys.modules,{'mod4_task':task}):original_module.consistent_reset(a,ids)
   torch.manual_seed(20261027);b=environment();task.MOD4_ISAAC=C
   with patch.dict(sys.modules,{'mod4_task':task}):candidate_module.consistent_reset(b,ids)
   assert len(a.scene['robot'].writes)==len(b.scene['robot'].writes)
   for x,y in zip(a.scene['robot'].writes,b.scene['robot'].writes):assert x[0]==y[0] and all(torch.equal(u,v) for u,v in zip(x[1:],y[1:]))
   assert torch.equal(a.height,b.height)
   if hasattr(a,'_rescue_reset_q'):assert torch.equal(a._rescue_reset_q,b._rescue_reset_q)
   checks.append(dict(name='actual reset function CPU duck '+label+' writes literalexact original',passed=True))
  # Original cached path remains the original cached path: selected rows only.
  before=b.scene['robot'].writes[:] if hasattr(b,'_rescue_reset_bank') else []
 finally:torch.random.set_rng_state(rng)
 changeset=dict(source_only=True,reset_bank_original_bytes_unchanged=True,reset_algorithm_and_original_perenv2mm_guard_unchanged=True,
  replacements=[dict(relative='job0/runtime/isaac/mod4/scut_flat_rescue.py',old_SHA=H(original),new_SHA=H(candidate),bytes=len(candidate)),dict(relative='job0/runtime/reports/SOURCE_FREEZE.json',old_SHA=H(freeze_bytes),new_SHA=H(newfreeze),bytes=len(newfreeze))],
  additions=[dict(relative='job0/runtime/isaac/mod4/'+name,SHA=H((C/name).read_bytes()),bytes=(C/name).stat().st_size) for name in ('gas400_reset_bank_exact_compatibility_v1.py',helper.OLD_CONTRACT_COPY)],
  unchanged_bank=dict(relative='job0/runtime/isaac/mod4/reset_bank.json',SHA=H(bank_bytes),bytes=len(bank_bytes)),unchanged_new400_contract_SHA=H(new_bytes),
  actual_SDK_scene_reset_or_training_passed=False,Task_GO_or_payload_generated=False)
 write(D/'EXACT_COMPATIBILITY_SOURCE_CHANGESET_NOT_ADMITTED.json',changeset)
 write(D/'ALL133_RESET_POSE_CLOSURE_AND_GAS_RANGE_SOURCE_CPU_ACTUAL.json',dict(passed=True,new_purpose='gas400 unchanged flat reset-bank source compatibility',pose_count=len(closure),selected_pose_count=74,pose_gas_ranges=ranges,closure=closure,max_closure_m=max(x['max_closure_m'] for x in closure),
  original_2mm_per_environment_reset_guard_unchanged=True,no_new_FP64_worldpoint_or_1um_training_gate=True,not_actual_PhysX_or_hardware_admission=True))
 write(D/'RESET_BANK_EXACT_COMPATIBILITY_SOURCE_CPU_ACTUAL.json',dict(passed=True,count=len(checks),checks=checks,compatibility=compatibility,changeset=changeset,
  no_model_PT_USD_raw_actor_or_physics_read_or_run=True,no_old160k_or_IK_fixture_rerun=True,no_GPU_or_remote_or_Git=True,
  sources=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p.read_bytes())) for p in (OLD,RT/'import_contract.json',RT/'reset_bank.json',RT/'scut_flat_rescue.py',B/'job0/runtime/reports/SOURCE_FREEZE.json',geo_path,conv_path,J/'agent_reference_retarget_cpu/own_usd_closed_chain_ik_v1.py')]))
 print(json.dumps(dict(passed=True,count=len(checks),poses=len(closure),selected=74,max_closure_m=max(x['max_closure_m'] for x in closure))))
if __name__=='__main__':
 try:main()
 except BaseException:
  write(D/'RESET_BANK_COMPATIBILITY_SOURCE_CPU_V1_ORIGINAL_ERROR.json',dict(passed=False,error=traceback.format_exc(),no_actual_SDK_or_model_execution=True));raise
