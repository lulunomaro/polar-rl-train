"""SRC_ONLY evidence collection: OpenUSD read-only + CPU MJCF compile only.
No project/robot SDK import, no MjData, mj_forward, mj_step, renderer, or network.
All outputs are confined to the script's MODEL_AUDIT directory.
"""
from pathlib import Path
import sys, json, hashlib, traceback, datetime, xml.etree.ElementTree as ET
import importlib.metadata
import numpy as np
from pxr import Usd, UsdGeom, UsdPhysics, UsdShade, UsdUtils, Sdf
import mujoco

OUT = Path(__file__).resolve().parent
OLD = Path(r'F:\RMPOLAR-RL\traditional_control_20261101')
V1 = Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1')
MJ = Path(r'C:\Users\lulu\Desktop\claude\mjcf')

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def serial(v):
    if v is None or isinstance(v, (str, int, float, bool)): return v
    if hasattr(v, 'GetReal'): return [float(v.GetReal()), *map(float, v.GetImaginary())]
    if isinstance(v, np.generic): return v.item()
    if isinstance(v, dict): return {k: serial(x) for k,x in v.items()}
    try: return [serial(x) for x in v]
    except TypeError: return str(v)
def rot(q):
    q=np.asarray(serial(q),float); q=q/np.linalg.norm(q)
    w,x,y,z=q
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                     [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                     [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def tensor(d,q):
    R=rot(q); return R@np.diag(d)@R.T

def main():
    p_out=OUT/'SOURCE_AUDIT_DATA.json'
    assert not p_out.exists(), 'Preserve previous collection; use another name for another attempt'
    contract=json.loads((V1/'assets/import_contract.json').read_text(encoding='utf-8'))
    candidates=[OLD/'model/mod4_400N.xml', OLD/'model/source_rolling_model_original.xml',
                MJ/'mod4-onnx-mujoco-launcher/model/source_rolling_model.xml',
                MJ/'chassis_mod4/robot_hifi.xml', MJ/'chassis_mod4/scene.xml',
                MJ/'chassis_mod4/scene_headless.xml', MJ/'chassis_mod4/scene_training.xml',
                MJ/'chassis_mod4_work/folded_pose_sim/scene_tunnel_247p2_drive.xml',
                MJ/'chassis_mod4_work/folded_pose_sim/scene_hard_stop_audit.xml']
    source_files=[V1/'assets/robot.usd', V1/'assets/import_contract.json', V1/'body_mass_changes.json',
                  V1/'body_parameters.csv', V1/'BUILD_RECEIPT.json', V1/'README.md',
                  V1/'baseline/import_contract.json', V1/'baseline/robot.usd',
                  V1/'baseline/source_700N/robot.usd', OLD/'MODEL_PROVENANCE.json',
                  OLD/'model_parameters.json', OLD/'reports/model_manifest.json',
                  OLD/'RESULTS_20261101.md', OLD/'prepare_model.py', OLD/'control_core.py']+candidates
    rows=[]
    for p in source_files:
        row={'path':str(p), 'exists':p.is_file()}
        if p.is_file(): row.update(bytes=p.stat().st_size,sha256=sha(p))
        if p in candidates and p.is_file():
            r=ET.parse(p).getroot()
            row.update(body_count=len(r.findall('.//body')), robot_inertial_mass_sum_kg=sum(float(x.get('mass')) for x in r.findall('.//body/inertial')),
                       option=r.find('option').attrib, compiler=r.find('compiler').attrib,
                       matches_historical_contract_source_sha256=sha(p)==contract['source_mjcf_sha256'],
                       has_v1_corrected_chassis_mass=any(x.get('name')=='chassis' and abs(float(x.find('inertial').get('mass'))-contract['bodies']['chassis']['mass_kg'])<1e-7 for x in r.findall('.//body')))
        rows.append(row)
    assert sha(V1/'assets/robot.usd')=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
    assert sha(V1/'assets/import_contract.json')=='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
    data={'mode':'SRC_ONLY','no_time_advancement':True,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'python':sys.executable,'python_version':sys.version,'versions':{n:importlib.metadata.version(n) for n in ['numpy','mujoco','usd-core']},
          'source_files':rows,'source_scope':'Only the explicitly supplied USD/v1 and traditional-control trees and provenance-linked MJCF source files; no global disk search.'}
    stage=Usd.Stage.Open(str(V1/'assets/robot.usd')); assert stage
    cache=UsdGeom.XformCache();base=stage.GetPrimAtPath('/Robot/links/chassis'); inv_base=cache.GetLocalToWorldTransform(base).GetInverse()
    usd={'meters_per_unit':UsdGeom.GetStageMetersPerUnit(stage),'kilograms_per_unit':UsdPhysics.GetStageKilogramsPerUnit(stage),'up_axis':UsdGeom.GetStageUpAxis(stage),'bodies':{},'joints':{},'geometry':{},'materials':{}}
    prims=list(Usd.PrimRange(stage.GetPseudoRoot(),Usd.TraverseInstanceProxies()))
    for p in prims:
        if p.HasAPI(UsdPhysics.RigidBodyAPI):
            a=UsdPhysics.MassAPI(p);q=a.GetPrincipalAxesAttr().Get(); diag=a.GetDiagonalInertiaAttr().Get()
            mat=np.asarray(cache.GetLocalToWorldTransform(p)*inv_base,float)
            usd['bodies'][p.GetName()]={'path':str(p.GetPath()),'mass_kg':float(a.GetMassAttr().Get()),'com_m':serial(a.GetCenterOfMassAttr().Get()),
                 'diagonal_inertia_kg_m2':serial(diag),'principal_axes_wxyz':serial(q),'full_inertia_kg_m2':serial(tensor(diag,q)),
                 'base_relative_position_m':mat[3,:3].tolist(),'base_relative_rotation_col':mat[:3,:3].T.tolist(),
                 'world_transform_row':serial(cache.GetLocalToWorldTransform(p)),
                 'rigid_body_attrs':{x.GetName():serial(x.Get()) for x in p.GetAttributes() if x.GetName().startswith(('physxRigidBody:','physxArticulation:'))}}
        if p.IsA(UsdPhysics.Joint):
            j=UsdPhysics.Joint(p)
            usd['joints'][p.GetName()]={'path':str(p.GetPath()),'type':p.GetTypeName(), 'body0':serial(j.GetBody0Rel().GetTargets()),'body1':serial(j.GetBody1Rel().GetTargets()),
                'attrs':{a.GetName():serial(a.Get()) for a in p.GetAttributes()},'rels':{r.GetName():serial(r.GetTargets()) for r in p.GetRelationships()}}
        if p.IsA(UsdGeom.Gprim):
            attrs={}
            for key in ['radius','height','size','axis','extent','xformOp:translate','xformOp:orient','xformOp:scale']:
                a=p.GetAttribute(key)
                if a: attrs[key]=serial(a.Get())
            local=np.asarray(UsdGeom.Xformable(p).GetLocalTransformation(),float)
            mtl=''
            if p.HasAPI(UsdPhysics.CollisionAPI):
                mat,rel=UsdShade.MaterialBindingAPI(p).ComputeBoundMaterial(materialPurpose='physics')
                mtl=str(mat.GetPath()) if mat else ''
            usd['geometry'][p.GetName()]={'path':str(p.GetPath()),'type':p.GetTypeName(),'collision':p.HasAPI(UsdPhysics.CollisionAPI),'attrs':attrs,
                'local_transform_row':local.tolist(),'physics_material':mtl}
        if p.HasAPI(UsdPhysics.MaterialAPI):
            usd['materials'][str(p.GetPath())]={a.GetName():serial(a.Get()) for a in p.GetAttributes() if a.GetName().startswith('physics:')}
    deps=UsdUtils.ComputeAllDependencies(Sdf.AssetPath(str(V1/'assets/robot.usd')))
    usd['dependencies']={'layers':[l.realPath for l in deps[0]],'assets':serial(deps[1]),'unresolved':serial(deps[2])}
    data['usd']=usd
    (OUT/'USD_STATIC_DATA.json').write_text(json.dumps(usd,ensure_ascii=False,indent=2),encoding='utf-8')
    print('USD static read: bodies',len(usd['bodies']),'joints',len(usd['joints']),'geometry',len(usd['geometry']),flush=True)
    try:
        # CPU compilation creates only MjModel. No state container and no integration APIs.
        model=mujoco.MjModel.from_xml_path(str(OLD/'model/mod4_400N.xml'))
        compiled={'status':'PASS_COMPILE_ONLY','engine_version':mujoco.__version__,'nbody':model.nbody,'robot_bodies':model.nbody-1,'njnt':model.njnt,'nq':model.nq,'nv':model.nv,'nu':model.nu,'ngeom':model.ngeom,'neq':model.neq,
                  'mass_sum_kg':float(model.body_mass.sum()), 'timestep_s':model.opt.timestep,'bodies':{},'joints':{},'actuators':[],'geometry':{}}
        for i in range(1,model.nbody):
            b=model.body(i); q=model.body_iquat[i];diag=model.body_inertia[i]
            compiled['bodies'][b.name]={'id':i,'parent':model.body(int(model.body_parentid[i])).name,'parent_relative_position_m':model.body_pos[i].tolist(),'parent_relative_quat_wxyz':model.body_quat[i].tolist(),
                'mass_kg':float(model.body_mass[i]),'com_m':model.body_ipos[i].tolist(),'diagonal_inertia_kg_m2':diag.tolist(),'principal_axes_wxyz':q.tolist(),'full_inertia_kg_m2':tensor(diag,q).tolist()}
        for i in range(model.njnt):
            j=model.joint(i);v=int(model.jnt_dofadr[i]);q=int(model.jnt_qposadr[i]); bid=int(model.jnt_bodyid[i])
            compiled['joints'][j.name]={'id':i,'body':model.body(bid).name,'type':int(model.jnt_type[i]),'pos_m':model.jnt_pos[i].tolist(),'axis':model.jnt_axis[i].tolist(),'range':model.jnt_range[i].tolist(),'limited':bool(model.jnt_limited[i]),'dofadr':v,'qposadr':q,'armature':float(model.dof_armature[v]),'damping_si':float(model.dof_damping[v]),'stiffness':float(model.jnt_stiffness[i]),'springref':float(model.qpos_spring[q])}
        for i in range(model.nu):
            compiled['actuators'].append({'id':i,'name':model.actuator(i).name,'joint':model.joint(int(model.actuator_trnid[i,0])).name,'gear':model.actuator_gear[i].tolist(),'ctrlrange':model.actuator_ctrlrange[i].tolist(),'forcerange':model.actuator_forcerange[i].tolist(),'ctrl_limited':bool(model.actuator_ctrllimited[i]),'force_limited':bool(model.actuator_forcelimited[i])})
        for i in range(model.ngeom):
            g=model.geom(i)
            compiled['geometry'][g.name]={'id':i,'body':model.body(int(model.geom_bodyid[i])).name,'type':int(model.geom_type[i]),'size':model.geom_size[i].tolist(),'position_m':model.geom_pos[i].tolist(),'quat_wxyz':model.geom_quat[i].tolist(),'friction':model.geom_friction[i].tolist(),'contype':int(model.geom_contype[i]),'conaffinity':int(model.geom_conaffinity[i]),'condim':int(model.geom_condim[i])}
        data['old_compile']=compiled
        print('Old MJCF CPU compile-only:', {k:v for k,v in compiled.items() if k not in ['bodies','joints','geometry','actuators']},flush=True)
    except Exception:
        data['old_compile']={'status':'FAILED_COMPILE_ONLY','error':traceback.format_exc()}
        print(data['old_compile']['error'],flush=True)
    data['all_source_hashes_still_unchanged']=all(not r['exists'] or sha(r['path'])==r['sha256'] for r in rows)
    p_out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    summary={'source_xml_candidates':[r for r in rows if r['path'].endswith('.xml')], 'usd_mass_sum_kg':sum(x['mass_kg'] for x in usd['bodies'].values()),'compiled_old_mass_sum_kg':data['old_compile'].get('mass_sum_kg'), 'unchanged':data['all_source_hashes_still_unchanged']}
    (OUT/'SOURCE_COLLECTION_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    try: main()
    except Exception:
        text=traceback.format_exc()
        (OUT/'SOURCE_COLLECTION_FAILURE_001.txt').write_text(text,encoding='utf-8')
        raise
