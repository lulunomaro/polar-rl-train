"""New model-free MOD4v1 target-SDK probe: no checkpoint, policy, PPO or ledger I/O."""
from pathlib import Path
import argparse,json,hashlib,os,time,traceback,sys

def put(path,value):
    with Path(path).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)

def main():
    p=argparse.ArgumentParser();p.add_argument('--task',required=True,type=Path);a=p.parse_args();task=json.loads(a.task.read_bytes());out=a.task.parent
    assert task['kind']=='MOD4V1_NEW_NATIVE_NO_PT' and os.environ['CUDA_VISIBLE_DEVICES']==task['GPU_UUID']
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==task['worker_sha256']
    asset=Path(task['asset']);contract_path=asset.with_name('import_contract.json')
    assert hashlib.sha256(asset.read_bytes()).hexdigest()==task['asset_sha256']
    assert hashlib.sha256(contract_path.read_bytes()).hexdigest()==task['contract_sha256']
    c=json.loads(contract_path.read_bytes());app=None;sim=None;view=None;av=None
    try:
        from isaaclab.app import AppLauncher
        class OwnedLauncher(AppLauncher):
            def _create_app(self):
                self._sim_app_config['enable_crashreporter']=False
                self._sim_app_config['extra_args']=['--/crashreporter/enabled=false','--/app/renderer/enabled=false','--/renderer/enabled=false','--/app/window/enabled=false']
                super()._create_app()
        launcher=OwnedLauncher(headless=True,device='cuda:0',enable_cameras=False,livestream=0,enable_crashreporter=False);app=launcher.app
        import torch,warp as wp,isaaclab.sim as sim_utils
        from isaaclab_physx.physics import PhysxCfg
        from pxr import UsdGeom,UsdPhysics,Gf
        def tensor(x):
            if isinstance(x,torch.Tensor):return x.clone()
            return wp.to_torch(x).clone()
        sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=.0025,device='cuda:0',physx=PhysxCfg(solver_type=1)))
        stage=sim.stage;UsdGeom.SetStageMetersPerUnit(stage,1.);UsdGeom.SetStageUpAxis(stage,'Z')
        ground=UsdGeom.Cube.Define(stage,'/World/Mod4v1ProbeGround');ground.CreateSizeAttr(1.);ground.AddTranslateOp().Set(Gf.Vec3d(0,0,-.05));ground.AddScaleOp().Set(Gf.Vec3f(10,10,.1));UsdPhysics.CollisionAPI.Apply(ground.GetPrim())
        robot=UsdGeom.Xform.Define(stage,'/World/Robot');robot.GetPrim().GetReferences().AddReference(str(asset));robot.AddTranslateOp().Set(Gf.Vec3d(0,0,float(c['spawn_height_m'])))
        sim.reset();view=sim.physics_sim_view;assert view.cuda_context is not None
        av=view.create_articulation_view('/World/Robot/links/chassis')
        names=list(av.shared_metatype.link_names);dof_names=list(av.shared_metatype.dof_names)
        assert len(names)==31 and len(dof_names)==30
        mass=tensor(av.get_masses());com=tensor(av.get_coms());inertia=tensor(av.get_inertias());pose=tensor(av.get_link_transforms())
        assert pose.is_cuda and all(bool(torch.isfinite(x).all()) for x in (mass,com,inertia,pose))
        assert set(names)==set(c['bodies'])
        mass_error={n:abs(float(mass[0,i])-float(c['bodies'][n]['mass_kg'])) for i,n in enumerate(names)}
        com_error={n:float(torch.max(torch.abs(com[0,i,:3].cpu()-torch.tensor(c['bodies'][n]['com_m'])))) for i,n in enumerate(names)}
        assert max(mass_error.values())<1e-5 and max(com_error.values())<1e-5
        spheres=[]
        for prim in stage.Traverse():
            if prim.IsA(UsdPhysics.SphericalJoint):
                j=UsdPhysics.Joint(prim);assert j.GetExcludeFromArticulationAttr().Get();b0=stage.GetPrimAtPath(j.GetBody0Rel().GetTargets()[0]).GetName();b1=stage.GetPrimAtPath(j.GetBody1Rel().GetTargets()[0]).GetName();spheres.append((prim.GetName(),names.index(b0),names.index(b1),list(j.GetLocalPos0Attr().Get()),list(j.GetLocalPos1Attr().Get())))
        assert len(spheres)==6
        def rotate(q,v):
            xyz=q[...,:3];w=q[...,3:4];return v+2*torch.cross(xyz,torch.cross(xyz,v,dim=-1)+w*v,dim=-1)
        def gaps(current):
            result={}
            for name,i0,i1,p0,p1 in spheres:
                x0=current[:,i0,:3]+rotate(current[:,i0,3:],torch.tensor(p0,device=current.device).expand(current.shape[0],3));x1=current[:,i1,:3]+rotate(current[:,i1,3:],torch.tensor(p1,device=current.device).expand(current.shape[0],3));result[name]=float(torch.linalg.vector_norm(x0-x1,dim=-1).max())
            return result
        initial_gaps=gaps(pose)
        for _ in range(8):sim.step(render=False)
        final_pose=tensor(av.get_link_transforms());final_vel=tensor(av.get_link_velocities());torch.cuda.synchronize()
        assert bool(torch.isfinite(final_pose).all()) and bool(torch.isfinite(final_vel).all())
        import subprocess
        clean={k:v for k,v in os.environ.items() if k not in ('LD_LIBRARY_PATH','LD_PRELOAD','PYTHONHOME','PYTHONPATH')}
        nv=subprocess.run(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],capture_output=True,text=True,env=clean,check=True)
        own=[line for line in nv.stdout.splitlines() if line.strip() and line.split(',')[1].strip()==str(os.getpid())]
        assert own and all(line.split(',')[0].strip()==task['GPU_UUID'] for line in own)
        put(out/'NATIVE_DATA_COMPLETE.json',dict(passed=True,scope='asset import and8native physics steps only; not fullDR or policy adaptation',worker_pid=os.getpid(),physical_GPU_UUID=task['GPU_UUID'],actual_own_compute_rows=own,body_names=names,dof_names=dof_names,masses_kg=mass.cpu().tolist(),com_pose_raw=com.cpu().tolist(),SDK_inertia_raw=inertia.cpu().tolist(),mass_max_error_kg=max(mass_error.values()),COM_max_error_m=max(com_error.values()),initial_closure_gap_m=initial_gaps,final_closure_gap_m=gaps(final_pose),physics_steps=sim.get_physics_step_count(),physics_dt_s=sim.get_physics_dt(),actual_CUDA_pose=True,model_opens=0,actor_calls=0,optimizer_updates=0,full_DR_or_frozen_expert_adaptation_passed=False))
        av=None;view=None;pose=None;final_pose=None;sim.stop();sim_utils.SimulationContext.clear_instance();sim=None
    except BaseException:
        put(out/('NATIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),{'error':traceback.format_exc(),'model_opens':0,'optimizer_updates':0});raise
    finally:
        if app is not None:
            put(out/'APP_CLOSING.json',{'epoch':time.time(),'calling_original_App_close':True})
            app.close()
if __name__=='__main__':main()
