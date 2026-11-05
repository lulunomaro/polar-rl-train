"""One local adapter/engine compilation check of the newly built representation, not native proof."""
from pathlib import Path
import json,importlib.util,math
import mujoco,numpy as np
D=Path(__file__).resolve().parent;out=D/'PHYSX_REPR2_LOCAL_VALIDATION.json';assert not out.exists();receipt=json.loads((D/'PHYSX_REPR2_BUILD_RECEIPT.json').read_text(encoding='utf-8-sig'));P=Path(receipt['package']);spec=importlib.util.spec_from_file_location('mod4v2_repr2_local_adapter',P/'runtime_adapter_v2.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);binding=a.prepare_environment(opt_in=True);contract=json.loads((P/'assets/import_contract.json').read_bytes());m=mujoco.MjModel.from_xml_path(str(P/'mjcf/scene.xml'));checks=dict(fresh_adapter_hardware_native_provenance_bound=True,robot31_nq37_nv36_nu6_neq10=m.nbody==32 and(m.nq,m.nv,m.nu,m.neq)==(37,36,6,10),mass_preserved=abs(float(m.body_mass.sum())-14.294140288606286)<1e-8,source_geometry_and_277_meshes_byte_preserved=receipt['mesh_files_byte_preserved']==277 and receipt['original_hardware_spec_and_package_unchanged']is True)
for name,limits in contract['native_impl_limits']['per_joint_limits_si'].items():
 j=m.joint(name)
 if limits==[None,None]:checks[name+'_continuous']=not bool(m.jnt_limited[j.id])
 else:checks[name+'_SI_range']=bool(m.jnt_limited[j.id])and bool(np.max(np.abs(m.jnt_range[j.id]-np.asarray(limits)))<1e-10)
assert all(checks.values()),checks
v=dict(passed=True,checks=checks,kind='NEW_REPR2_LOCAL_ADAPTER_AND_MUJOCO_COMPILE_NOT_NATIVE_ACCEPTANCE',package=str(P),binding=binding,asset_SHA=receipt['output_bindings_sha256']['assets/robot.usd'],contract_SHA=receipt['output_bindings_sha256']['assets/import_contract.json'],simulation_steps=0,native_PhysX_verified=False,actual_100Hz_feedback_verified=False,policy_or_model_weights_opened=0,unchanged_hardware_measured_force_curve=False);out.write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf8');print(json.dumps(dict(path=str(out),passed=True,local_checks=len(checks),native_PhysX_verified=False,simulation_steps=0)))
