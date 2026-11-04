"""Static functional model-correspondence check; no checkpoint/SDK/native episode."""
from pathlib import Path
import json,hashlib,math
import mujoco,numpy as np
D=Path(__file__).resolve().parent;M=Path('C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4');C=D.parent/'mod4_usd_scut_fudan_20261101/candidates/v1/assets/import_contract.json';c=json.loads(C.read_bytes());m=mujoco.MjModel.from_xml_path(str(M/'scene.xml'));bodies=[];joints=[]
def rot(q):out=np.empty(9);mujoco.mju_quat2Mat(out,np.asarray(q,dtype=float));return out.reshape(3,3)
for name,v in c['bodies'].items():
 try:i=m.body(name).id
 except KeyError:continue
 R=rot(m.body_iquat[i]);S=rot(v['principal_axes_wxyz']);a=R@np.diag(m.body_inertia[i])@R.T;b=S@np.diag(v['diagonal_inertia_kg_m2'])@S.T
 bodies.append(dict(name=name,local_mass_kg=float(m.body_mass[i]),native_contract_mass_kg=v['mass_kg'],mass_delta_kg=float(m.body_mass[i]-v['mass_kg']),com_delta_norm_m=float(np.linalg.norm(m.body_ipos[i]-v['com_m'])),full_inertia_delta_max_kg_m2=float(np.max(np.abs(a-b)))))
for name,v in c['joints'].items():
 try:i=m.joint(name).id
 except KeyError:continue
 if v['limits_si']is not None:
  local=m.jnt_range[i].tolist();expected=v['limits_si']
  if max(abs(x-y)for x,y in zip(local,expected))>1e-8:joints.append(dict(name=name,local_limits=local,native_contract_limits=expected))
xml=[]
for p in M.glob('*.xml'):
 raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest();xml.append(dict(path=str(p),bytes=len(raw),SHA=h,matches_native_source_mjcf_SHA=h==c['source_mjcf_sha256']))
result=dict(kind='STATIC_LOCAL_DEMO_VS_SELECTED_NATIVE_CONTRACT_NOT_RUNTIME_VALIDATION',local_scene=str(M/'scene.xml'),native_contract=str(C),native_source_mjcf_SHA=c['source_mjcf_sha256'],matched_body_count=len(bodies),local_total_body_mass_kg=float(m.body_mass.sum()),native_total_body_mass_kg=sum(v['mass_kg']for v in c['bodies'].values()),body_parameter_differences=[r for r in bodies if abs(r['mass_delta_kg'])>1e-5 or r['com_delta_norm_m']>1e-5 or r['full_inertia_delta_max_kg_m2']>1e-5],joint_limit_differences=joints,top_level_XML_fingerprints=xml,original_sources_modified=False,models_raw_SDK_GPU_or_budget_operations=0,geometry_joint_frame_and_runtime_equivalence_not_claimed=True)
(D/'LOCAL_NATIVE_MODEL_CORRESPONDENCE.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
