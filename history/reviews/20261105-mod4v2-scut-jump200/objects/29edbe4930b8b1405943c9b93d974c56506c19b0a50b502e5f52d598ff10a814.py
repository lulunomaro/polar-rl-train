"""Bounded actual SDK check of v2 one-axis D6; zero policy/checkpoint operations."""
from pathlib import Path
import fcntl,hashlib,json,math,os,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parent
BASE=Path('/home/lc01/Zonglin Li/zonglin2')
C=BASE/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
TARGET=ROOT/'NATIVE_REPRESENTATION_RESULT.json'

def put(name,value):
    (ROOT/name).write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf8')

if __name__=='__main__':
    locks=[];app=sim=None;error=None
    try:
        for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'finite_environment_validation.lock',C.parent.parent/'three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock']:
            f=p.open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
        c=json.loads(C.read_bytes());assert c['active_segment']is None
        assert c['remaining_training_seconds']>86412.86069250107+3900
        from isaaclab.app import AppLauncher
        launcher=AppLauncher(headless=True,device='cuda:0',enable_cameras=False,livestream=0)
        app=launcher.app
        import torch,warp as wp
        import isaaclab.sim as sim_utils
        from isaaclab_physx.physics import PhysxCfg
        from pxr import UsdGeom,UsdPhysics,Gf
        tensor=lambda x:x if torch.is_tensor(x)else wp.to_torch(x)
        sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=.0025,device='cuda:0',physics=PhysxCfg(solver_type=1)))
        stage=sim.stage
        robot=UsdGeom.Xform.Define(stage,'/World/Robot')
        robot.GetPrim().GetReferences().AddReference(str(ROOT/'physx_representation.usda'))
        robot.AddTranslateOp().Set(Gf.Vec3d(0,0,.38))
        sim.reset()
        av=sim.physics_sim_view.create_articulation_view('/World/Robot/links/chassis')
        native_names=list(av.shared_metatype.dof_names)
        names=[name.removesuffix(':0')for name in native_names]
        bodies=list(av.shared_metatype.link_names)
        actual=tensor(av.get_dof_limits()).clone()
        contract=json.loads((ROOT/'hardware/assets/import_contract.json').read_bytes())
        rows=[]
        for name in names:
            limits=contract['joints'][name]['limits_si']
            if limits is None:continue
            value=actual[0,names.index(name)];okay=[]
            for i,want in enumerate(limits):
                x=float(value[i]);okay.append((x< -1e7 if i==0 else x>1e7)if want is None else abs(x-want)<1e-6)
            rows.append(dict(name=name,actual=[float(x)if math.isfinite(float(x))else str(float(x))for x in value],expected=limits,passed=all(okay)))
        put('NATIVE_REPRESENTATION_LIMITS.json',dict(body_count=len(bodies),DOF=len(names),names=native_names,rows=rows,passed=all(r['passed']for r in rows)))
        assert len(names)==30 and all(r['passed']for r in rows)
        poses=tensor(av.get_link_transforms()).clone();initial=tensor(av.get_dof_positions()).clone()
        for _ in range(20):sim.step(render=False)
        q=tensor(av.get_dof_positions()).clone()
        mimic=max(float((q[:,names.index(side+'_drive_'+axis+'_spin')]-q[:,names.index(side+'_'+joint)]).abs().max())for side in ['left','right']for axis,joint in [('hip','hip'),('input','crank')])
        assert bool(torch.isfinite(q).all())and mimic<.01
        put(TARGET.name,dict(epoch=time.time(),passed=True,body_count=len(bodies),DOF=len(names),
            limits=rows,mimic_max_rad=mimic,physics_steps=20,physics_dt=.0025,
            policy_calls=0,model_reads=0,canonical_writes=0,new_finite_angular_boxes=False))
    except BaseException:
        error=traceback.format_exc();put('NATIVE_REPRESENTATION_ERROR.json',dict(epoch=time.time(),error=error));raise
    finally:
        if sim is not None:sim.clear_instance()
        put('NATIVE_REPRESENTATION_CLOSE_INTENT.json',dict(epoch=time.time(),error=error))
        if app is not None:
            try:app.close()
            except SystemExit:pass
        for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
