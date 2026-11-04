"""Actual nominal MuJoCo behavior, not native/fullDR or original-74 acceptance.
A derived pi-only export is not a training/resume checkpoint. No source model reopens for status.
"""
from pathlib import Path
import argparse,hashlib,io,json,math,sys,time
import numpy as np
import torch
from torch import nn
import mujoco

D=Path(__file__).resolve().parent
PLAYER=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023\player')
sys.path.insert(0,str(PLAYER));import sim_runtime as rt
sys.path.insert(0,str(D/'source_fudan_frozen_native_eval_v4_fresh1cd_timeout8'))
from frozen_sequence_mean import _PiOnly
MOTHER_SHA='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8'
torch.set_num_threads(1)


def decode_once(path,expected_sha,expected_bytes=None):
    raw=Path(path).read_bytes();digest=hashlib.sha256(raw).hexdigest()
    assert digest==expected_sha and(expected_bytes is None or len(raw)==expected_bytes)
    return torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False),dict(path=str(Path(path).resolve()),bytes=len(raw),sha256=digest,physical_reads=1,SHA_calculations=1,CPU_decodes=1)


class PiExport:
    def __init__(self,path):
        receipt=json.loads(Path(path).with_name('pi_export_receipt.json').read_bytes());assert receipt['kind']=='FDN_PI_ONLY_EXPORT_RECEIPT_V1'and receipt['complete']is True
        self.root,self.io=decode_once(path,receipt['artifact']['sha256'],receipt['artifact']['bytes']);r=self.root
        assert r['source']==receipt['source'] and receipt['pi_tensor_count']==14 and receipt['pi_numel']==82505
        assert r['kind']=='FDN_PI_ONLY_EXPORT_FOR_NOMINAL_MUJOCO_V1' and r['not_a_full_training_resume_checkpoint']is True
        assert r['source']['source_training_execution_qualified']is True
        p=r['source_provenance'];assert p['schema_version']==4 and p['training_num_envs']==20000 and p['window_counters']['updates']>0
        assert r['source']['sha256']not in(MOTHER_SHA,'47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d','8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78','3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e')
        with torch.random.fork_rng(devices=[]):
            self.network=_PiOnly();self.network.load_state_dict(r['pi_state_dict'],strict=True)
        self.network.eval().requires_grad_(False);assert len(self.network.state_dict())==14
        assert all(v.device.type=='cpu' and v.dtype==torch.float32 and torch.isfinite(v).all()for v in self.network.state_dict().values())
        self.input_width=35;self.history=None
    def reset_history(self,frame):
        x=torch.as_tensor(np.asarray(frame,dtype=np.float32).copy()).reshape(1,1,35)
        self.history=x.repeat(1,5,1)
    def __call__(self,frame):
        x=torch.as_tensor(np.asarray(frame,dtype=np.float32).copy()).reshape(1,1,35)
        if self.history is None:self.reset_history(frame)
        else:self.history=torch.cat((self.history[:,1:],x),dim=1)
        with torch.inference_mode():a=self.network(self.history).clamp(-6,6)[0].numpy().astype(np.float64)
        assert np.isfinite(a).all();return a


class MotherMean:
    def __init__(self,path):
        self.root,self.io=decode_once(path,MOTHER_SHA);assert self.io['sha256']==MOTHER_SHA
        s=self.root['actor_state_dict'];assert set(s)=={f'mlp.{i}.{kind}'for i in(0,2,4,6)for kind in('weight','bias')}|{'distribution.std_param'}
        with torch.random.fork_rng(devices=[]):
            layers=[]
            for i in(0,2,4,6):
                w=s[f'mlp.{i}.weight'];layers.append(nn.Linear(w.shape[1],w.shape[0]))
                if i!=6:layers.append(nn.ELU())
            self.network=nn.Module();self.network.add_module('mlp',nn.Sequential(*layers))
        self.network.load_state_dict({k:v for k,v in s.items()if k.startswith('mlp.')},strict=True)
        self.network.eval().requires_grad_(False);self.input_width=35
    def reset_history(self,frame):pass
    def __call__(self,frame):
        with torch.inference_mode():a=self.network.mlp(torch.as_tensor(np.asarray(frame,dtype=np.float32).copy()).reshape(1,35)).clamp(-6,6)[0].numpy().astype(np.float64)
        assert np.isfinite(a).all();return a


def body_contact_forces(sim):
    force=np.zeros((sim.model.nbody,3),dtype=np.float64)
    for i in range(sim.data.ncon):
        contact=sim.data.contact[i];wrench=np.zeros(6);mujoco.mj_contactForce(sim.model,sim.data,i,wrench)
        world=np.asarray(contact.frame).reshape(3,3).T@wrench[:3]
        b1=int(sim.model.geom_bodyid[contact.geom1]);b2=int(sim.model.geom_bodyid[contact.geom2])
        force[b1]-=world;force[b2]+=world
    return np.linalg.norm(force,axis=1)


def reset_pose(sim,pose,policy):
    mujoco.mj_resetData(sim.model,sim.data);sim.data.qpos[:3]=(0,0,.1781);sim.data.qpos[3:7]=(1,0,0,0);sim.data.qpos[7:]=0
    for side,values in pose['joint_values'].items():
        for name,value in values.items():sim.data.qpos[sim.model.jnt_qposadr[sim._joint(side+'_'+name)]]=value
    sim.data.qvel[:]=0;sim.data.ctrl[:]=0;sim.data.xfrc_applied[:]=0;sim.data.qfrc_applied[:]=0
    sim.command=rt.UserCommand(vx=0,vy=0,wz=0,height=.25,mode=3,auto_mode=False)
    sim.last_action[:]=0;sim.control_steps=0;sim.max_closure_error=0.;sim.max_mimic_error=0.;sim.max_abs_torque[:]=0
    mujoco.mj_forward(sim.model,sim.data);policy.history=None if isinstance(policy,PiExport)else getattr(policy,'history',None)
    frame=sim.observation_frame();policy.reset_history(frame)
    return dict(root_height_m=float(sim.data.qpos[2]),closure_error_m=sim.closure_error(),mimic_error_rad=sim.mimic_error(),clean_raw35=frame.tolist())


def run_case(sim,policy,pose,index):
    initial=reset_pose(sim,pose,policy);stable=0;ever=False;first_credit=None;max_height=float(sim.data.qpos[2]);final={};err=None
    wheel_ids=[sim._body(x)for x in('left_wheel','right_wheel')]
    # The original native control is 50 Hz with two 100 Hz PD samples and eight physics steps.
    try:
        for step in range(400):
            a=policy(sim.observation_frame());sim.last_action[:]=a
            for sub in range(8):
                if sub%4==0:
                    tau=sim.action_to_torque(a);sim.data.ctrl[:]=tau;sim.max_abs_torque=np.maximum(sim.max_abs_torque,np.abs(tau))
                sim.data.xfrc_applied[:]=0;sim.data.qfrc_applied[:]=0;mujoco.mj_step(sim.model,sim.data)
            assert np.isfinite(sim.data.qpos).all()and np.isfinite(sim.data.qvel).all()
            sim.control_steps+=1;sim.max_closure_error=max(sim.max_closure_error,sim.closure_error());sim.max_mimic_error=max(sim.max_mimic_error,sim.mimic_error())
            g=sim.data.xmat[sim.chassis_id].reshape(3,3).T@np.array([0.,0.,-1.]);h=float(sim.data.qpos[2]);v=float(np.linalg.norm(sim.data.qvel[:3]));om=float(np.linalg.norm(sim.data.qvel[3:6]));f=body_contact_forces(sim)
            good=h>=.23 and g[2]<-.984807753 and v<.03 and om<.2 and bool((f[wheel_ids]>1.).all())and f[sim.chassis_id]<1.
            stable=stable+1 if good else 0
            if stable>=25 and not ever:ever=True;first_credit=(step+1)*.02
            max_height=max(max_height,h)
            final=dict(height_m=h,tilt_deg=math.degrees(math.acos(float(np.clip(-g[2],-1,1)))),root_speed_m_s=v,angular_speed_rad_s=om,wheel_net_contact_force_N=f[wheel_ids].tolist(),chassis_net_contact_force_N=float(f[sim.chassis_id]),stable_at_end_seconds=stable*.02,root_xy_m=sim.data.qpos[:2].tolist())
    except Exception as e:err=type(e).__name__+': '+str(e)
    return dict(pose_index=index,initial=initial,controls=sim.control_steps,physics_steps=sim.control_steps*8,feedback_samples=sim.control_steps*2,finite_execution_error=err,credited_by_same_engineering_predicate=ever,first_credit_seconds=first_credit,credited_and_stable_at_end=ever and stable>=25 and err is None and sim.control_steps==400,max_height_m=max_height,final=final,max_closure_error_m=sim.max_closure_error,max_mimic_error_rad=sim.max_mimic_error,max_abs_motor_torque_Nm=sim.max_abs_torque.tolist(),no_external_lift_yaw_or_animation=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--pi-export',required=True);ap.add_argument('--baseline',default=str(D.parent/'mod4v1_e3_mujoco_view_20261104/current_E3.pt'));ap.add_argument('--output',default=str(D/'FDN_FRESH1CD_MUJOCO31_LOWRise_RESULT.json'));args=ap.parse_args()
    output=Path(args.output);marker=output.with_name(output.stem+'_ONCE.json');assert not output.exists() and not marker.exists();poses=json.loads((D/'CONTRACT_PARITY_AND_POSE_V2.json').read_bytes())['best_candidates'];assert len(poses)==5
    with marker.open('x',encoding='utf8')as stream:json.dump(dict(epoch=time.time(),pi_export=args.pi_export,baseline=args.baseline,output=str(output),actual_behavior_not_synthetic_fixture=True),stream,indent=2)
    assert hashlib.sha256((D/'source_fudan_frozen_native_eval_v4_fresh1cd_timeout8/frozen_sequence_mean.py').read_bytes()).hexdigest()=='b183b7d3b0e168220ffdbdfb9d25187266ee8e62e9b289ce41af59ebc405ea0f'
    candidate=PiExport(args.pi_export);mother=MotherMean(args.baseline);rows={}
    cfg=rt.RuntimeConfig(leg_kp=60,leg_kd=2,wheel_kd=.6,crank_scale=.5,hip_scale=.5,wheel_scale=10,policy_hz=50,yaw_assist_gain=0)
    for name,policy in(('candidate',candidate),('frozen_mother',mother)):
        rt.OnnxPolicy=lambda _path:policy
        sim=rt.Mod4Sim(D/'contract_parity_mujoco_v1/scene.xml',args.pi_export,cfg)
        assert sim.model.nbody==32 and sim.model.nq==37 and sim.model.nv==36 and sim.model.nu==6 and sim.model.neq==10 and abs(sim.model.body_mass.sum()-14.294140288606286)<1e-8
        sim.model.opt.timestep=.0025;sim.decimation=8
        for name0 in('left_gas_slide','right_gas_slide'):
            j=sim._joint(name0);assert abs(sim.model.jnt_stiffness[j]-2000)<1e-8 and abs(sim.model.dof_damping[sim.model.jnt_dofadr[j]]-3)<1e-8
        rows[name]=[run_case(sim,policy,pose,index)for index,pose in enumerate(poses)]
    result=dict(kind='NOMINAL_MUJOCO31_FIVE_LEGAL_POSE_BEHAVIOR_NOT_NATIVE_ORIGINAL74_ACCEPTANCE',epoch=time.time(),policy_hz=50,feedback_hz=100,physics_dt=.0025,duration_per_case_seconds=8,poses=5,whole_leg_same_end_video_pose=False,torch_version=torch.__version__,mujoco_version=mujoco.__version__,seed_randomization=None,clean_observation_not_native_noisy_delayed_sensor=True,full_DR=False,backend_contact_or_hardware_parity_claim=False,original74_skill_graduation_claim=False,training_or_optimization_steps=0,source_export=candidate.root['source'],candidate_export_io=candidate.io,mother_io=mother.io,configuration=vars(cfg),nominal_mass_kg=14.294140288606286,rows=rows)
    output.write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf8');print(json.dumps(dict(output=str(output),candidate_credited_in_complete_finite_cases=sum(r['credited_by_same_engineering_predicate']and r['finite_execution_error']is None and r['controls']==400 for r in rows['candidate']),mother_credited_in_complete_finite_cases=sum(r['credited_by_same_engineering_predicate']and r['finite_execution_error']is None and r['controls']==400 for r in rows['frozen_mother']),denominator_each=5,native_skill_claim=False),indent=2))


if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        error_path=D/('FDN_FRESH1CD_MUJOCO31_ERROR_'+str(time.time_ns())+'.json')
        error_path.write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc(),no_success_claim=True),indent=2),encoding='utf8')
        raise
