"""Compose a NEW private nominal400 USD layer using actual72 USD CPU only."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
S=Path(__file__).resolve().parent;L=S.parent;T=L.parent;W=T.parent;R=S/'reports'
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'
H=L/'HARDWARE_GAS_SPRING_400N_L200_S60_HUMAN_20261027/agent_nominal400_target_source_candidate_v1/isolated_text_overlay_NOT_A_PAYLOAD'
D='/home/lc01/Zonglin Li/zonglin2/staging/MOD4_NATIVE88_GAS400_ASSET_CPU_20261027'
hashfile=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
PREP=r"""from pathlib import Path
import os,sys,json,hashlib,shutil,psutil,importlib.util,time
q=v['q'];root=Path(q['root']);owned=Path('/home/lc01/Zonglin Li/zonglin2/staging')
assert root.resolve().is_relative_to(owned.resolve()) and not root.exists()
c=json.loads(Path(q['canonical']).read_bytes());assert c['active_segment'] is None and c['remaining_training_seconds']==569553.363275528
assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
spec=importlib.util.find_spec('pxr')
assert spec is not None,'actual target pxr USD CPU package not on original interpreter path; no App/GPU fallback'
source=Path(q['source_asset']);assert source.is_file()
assert hashlib.sha256(source.read_bytes()).hexdigest()==q['source_asset_SHA'] and source.stat().st_size==q['source_asset_bytes']
assert json.loads((Path(q['closed_recovery_root'])/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
root.mkdir();(root/'assets/source_700N').mkdir(parents=True)
shutil.copy2(source,root/'assets/source_700N/robot.usd')
identity=psutil.Process(os.getpid())
print(json.dumps(dict(new_root=str(root),old_asset_copied_readonly=True,source_SHA=q['source_asset_SHA'],actual_pxrspec_origin=spec.origin,identity=dict(pid=identity.pid,creation=identity.create_time(),exe=identity.exe(),argv=identity.cmdline(),cwd=identity.cwd()),no_SDK_App_scene_GPU_model_or_account_write=True)))
"""
COMPOSE=r"""from pathlib import Path
import os,json,hashlib,psutil,time
from pxr import Usd,UsdPhysics,Sdf
q=v['q'];root=Path(q['root']);H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
C=Path(q['canonical']);before=C.read_bytes();assert json.loads(before)['active_segment'] is None
for row in q['new_inputs']:
 p=root/row['relative'];assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
base=root/'assets/source_700N/robot.usd';layer=root/'assets/robot.usd';assert H(base)==q['source_asset_SHA']
raw=layer.read_bytes();assert raw.startswith(b'#usda 1.0\n') and b'\\n' not in raw
layer_spec=Sdf.Layer.FindOrOpen(str(layer));assert layer_spec is not None and list(layer_spec.subLayerPaths)==['source_700N/robot.usd']
opinions=[]
def walk(spec):
 for prop in spec.properties:opinions.append(str(prop.path))
 for child in spec.nameChildren:walk(child)
for prim in layer_spec.rootPrims:walk(prim)
expected={f'/Robot/joints/{name}.{attr}' for name in ('left_gas_slide','right_gas_slide') for attr in ('drive:linear:physics:stiffness','physics:upperLimit')}
assert set(opinions)==expected and len(opinions)==4
old=Usd.Stage.Open(str(base),Usd.Stage.LoadAll);new=Usd.Stage.Open(str(layer),Usd.Stage.LoadAll)
assert old is not None and new is not None
assert str(old.GetDefaultPrim().GetPath())==str(new.GetDefaultPrim().GetPath())=='/Robot'
oldpaths={str(p.GetPath()):str(p.GetTypeName()) for p in old.Traverse()};newpaths={str(p.GetPath()):str(p.GetTypeName()) for p in new.Traverse()};assert oldpaths==newpaths
rows=[];changes=[]
for path in oldpaths:
 a=old.GetPrimAtPath(path);b=new.GetPrimAtPath(path)
 aa={x.GetName():x for x in a.GetAttributes()};bb={x.GetName():x for x in b.GetAttributes()}
 assert set(aa)==set(bb) and a.GetAppliedSchemas()==b.GetAppliedSchemas()
 for name in aa:
  av=aa[name].Get();bv=bb[name].Get()
  # Same authored geometry/frames evaluated within one CPU USD library; not a physics numeric gate.
  if av!=bv:
   key=path+'.'+name;assert key in expected,key
   changes.append(dict(path=path,attribute=name,old_value=av,new_value=bv))
assert {x['path']+'.'+x['attribute'] for x in changes}==expected
contract=json.loads((root/'assets/import_contract.json').read_bytes())
for name in ('left_gas_slide','right_gas_slide'):
 path='/Robot/joints/'+name;op=old.GetPrimAtPath(path);np=new.GetPrimAtPath(path)
 assert np.IsA(UsdPhysics.PrismaticJoint)
 k0=op.GetAttribute('drive:linear:physics:stiffness').Get();k=np.GetAttribute('drive:linear:physics:stiffness').Get()
 lo=np.GetAttribute('physics:lowerLimit').Get();hi=np.GetAttribute('physics:upperLimit').Get()
 assert k0==3500 and k==2000 and abs(hi-.020639440248416612)<1e-8 and abs(lo-(-.0267046843609))<1e-8
 assert k==contract['gas_springs'][name]['stiffness_n_m']
 assert abs(hi-contract['joints'][name]['limits_si'][1])<1e-8
 rows.append(dict(name=name,nominal_k_N_m=k,hard_q_lower_m=lo,hard_q_upper_m=hi,other_original_target_damping_maxforce_unchanged=True))
assert H(base)==q['source_asset_SHA'] and C.read_bytes()==before
identity=psutil.Process(os.getpid())
report=dict(epoch=time.time(),actual_private_USD_CPU_composition_passed=True,parameter_source_contract_SHA=H(root/'NOMINAL400_PARAMETER_SOURCE_CONTRACT.json'),base_asset_SHA=H(base),new_layer_SHA=H(layer),asset_contract_SHA=H(root/'assets/import_contract.json'),private_root=str(root),new_asset=str(layer),new_base_asset=str(base),new_source_contract=str(root/'assets/import_contract.json'),only_four_authored_attribute_changes=changes,all_prim_types_paths_and_other_attribute_values_appliedschemas_same=True,actual_gas_authored_values=rows,nominal_force_400N_at200mm_only_approximation=True,actual_force_curve_or_damping_not_measured=True,actual_PhysX_runtime_parameter_admission=False,actual_SDK_App_scene_GPU_or_policy_run=False,originals_retained_unmodified=True,canonical_bytes_unchanged=True,no_account_writer_or_Task_GO=True,actual_CPU_identity=dict(pid=identity.pid,creation=identity.create_time(),exe=identity.exe(),argv=identity.cmdline(),cwd=identity.cwd()))
p=root/'ASSET_COMPOSITION_CPU_ACTUAL.json'
with p.open('x',encoding='utf8') as f:json.dump(report,f,indent=2,allow_nan=False)
print(json.dumps(dict(report=report,producer=dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)),asset_producers=[dict(path=str(x),bytes=x.stat().st_size,SHA=H(x)) for x in (base,layer,root/'assets/import_contract.json')])))
"""
def main():
 R.mkdir(exist_ok=True)
 put('NEW_ASSET_CPU_FINITE_CONSUMED_BEFORE_REMOTE_ACTUAL.json',dict(epoch=time.time(),no_training_or_model_or_GPU=True))
 detached=json.loads((N/'reports/AVAILABLE_TWO_NATIVE87R5_ACTUAL_OWNER_NODES_DETACHED.json').read_bytes())
 root=detached['roots']['recovery'];manifest=json.loads((N/'payloads_r5/recovery/THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
 asset=next(x for x in manifest['files'] if x['relative']=='job0/assets/robot.usd')
 source_layer=H/'job0/assets/NOMINAL400_GAS_ONLY_OVERLAY_NOT_ADMITTED.usda';source_contract=H/'job0/assets/import_contract.json'
 assert source_layer.read_bytes().count(b'\n')>10 and b'\\n' not in source_layer.read_bytes()
 param=dict(schema='mod4.nominal400_gas_parameter_source.v1',human_selected_force_each_N=400,extended_eye_m=.2,physical_stroke_m=.06,compressed_eye_derived_m=.14,q_eye_offset_m=.1793605597515834,q_lower_preserved_m=-.0267046843609,q_upper_m=.020639440248416612,k_N_m=2000,preload_q_target_preserved=[.22063944109012937,.2206394410901294],damping3Ns_m_unmeasured_engineering_assumption=True,force_progression_at140mm_520N_is_engineering_model_not_measurement=True,reference9223_gas_length_already_fits200=True,source_old_asset_SHA=asset['SHA'],source_changed_contract_SHA=hashfile(source_contract),not_same700N_physics=True)
 parameter=S/'NOMINAL400_PARAMETER_SOURCE_CONTRACT.json'
 with parameter.open('x',encoding='utf8') as f:json.dump(param,f,indent=2)
 inputs=[dict(local=str(source_layer),relative='assets/robot.usd'),dict(local=str(source_contract),relative='assets/import_contract.json'),dict(local=str(parameter),relative=parameter.name)]
 for x in inputs:x.update(bytes=Path(x['local']).stat().st_size,SHA=hashfile(x['local']))
 q=dict(root=D,canonical='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json',source_asset=root+'/'+asset['relative'],source_asset_SHA=asset['SHA'],source_asset_bytes=asset['bytes'],closed_recovery_root=root,new_inputs=inputs)
 with (S/'BOUND_ASSET_CPU_INPUTS.json').open('x',encoding='utf8') as f:json.dump(q,f,indent=2)
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('asset88_same_authorized_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 secret=m.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  pre=d.code(c,d.PY72,PREP,dict(q=q),timeout=60);put('ACTUAL_PRIVATE_ASSET_CPU_PREFLIGHT_RETURNED.json',pre)
  sf=c.open_sftp();sf.get_channel().settimeout(60)
  try:
   for row in inputs:sf.put(row['local'],D+'/'+row['relative'])
  finally:sf.close()
  value=d.code(c,d.PY72,COMPOSE,dict(q=q),timeout=120);put('ASSET_COMPOSITION_CPU_REMOTE_RETURNED_ACTUAL.json',value)
  p=S/'ASSET_COMPOSITION_CPU_ACTUAL.json'
  sf=c.open_sftp()
  try:sf.get(value['producer']['path'],str(p))
  finally:sf.close()
  assert p.stat().st_size==value['producer']['bytes'] and hashfile(p)==value['producer']['SHA']
  put('ACTUAL_PRIVATE_GAS400_USD_CPU_TWOHOST_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,actual_finite_returned=True,report_path=str(p),report_SHA=hashfile(p),report_bytes=p.stat().st_size,asset_producers=value['asset_producers'],no_PhysX_or_runtime_SDK_or_GPU_claim=True,no_account_or_Task_GO=True))
  print(json.dumps(dict(passed=True,actual_private_USD_CPU_composed=True,report_SHA=hashfile(p),changed_attributes=len(value['report']['only_four_authored_attribute_changes']),runtime_PhysX_pending=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True)
  put('NEW_ASSET_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_namespace_retry=True,no_training_fee=True));raise
