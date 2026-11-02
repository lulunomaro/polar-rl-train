"""Freeze source MPC phase logic and gains for current-state finite control comparison."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess,sys,textwrap,time
P=Path(__file__).resolve().parent;T=P.parent
S=Path('F:/RMPOLAR-RL/traditional_control_20261101');F=S/'results/FINAL_EVIDENCE_V2'
D=T/'MPC_CURRENT_STATE_EVENT_BRIDGE_V353_20261102';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,indent=2,allow_nan=False)
D.mkdir(exist_ok=False);(D/'source').mkdir();(D/'reports').mkdir();(D/'source/reports').mkdir()
manifest=json.loads((F/'manifest.json').read_bytes())
for name in('control_core.py','full_lqr.py','linear_mpc.py','hybrid_trial.py','kinematics.py'):
    assert H(F/name)==manifest['source_sha256'][name];shutil.copyfile(F/name,D/'source'/name)
for name in('model_parameters.json','reports/model_manifest.json'):shutil.copyfile(S/name,D/'source'/name)
shutil.copyfile(F/'fullDR_mpc/config.json',D/'source/config353.json')
hybrid=(F/'hybrid_trial.py').read_text('utf8');start=hybrid.index('        if launch_time is None and');end=hybrid.index('        p.torque_control(tau)',start)
phaseblock=textwrap.dedent(hybrid[start:end])
bridge='''"""Source MPC state/event controller, unchanged phase equations; no simulator import.

This is a diagnostic current-state controller, not a learned/deployable depth policy.
The current target interface remains50Hz; source controller was100Hz. Two10ms MPC
prediction transitions per20ms command are not claimed or silently introduced.
"""
import math,numpy as np
from linear_mpc import LinearMPC

class SourceEventMPC353:
    def __init__(self,bundle):
        self.cfg=dict(bundle['config']);self.g={k:np.array(v,float)for k,v in bundle['g'].items()};self.gn={k:np.array(v,float)for k,v in bundle['gn'].items()}
        self.ref=np.r_[self.g['q'],np.zeros(7)];self.ref[0]=self.cfg['start_x']
        self.mpc=LinearMPC(self.g,horizon=self.cfg.get('horizon',15))
        self.launch_time=None;self.launch_pose=None;self.launch_velocity=None;self.top=False;self.land_x=None;self.top_time=None;self.top_state=None;self.top_x=None;self.last_phase=None;self.calls=0
    def command(self,t,x,q6,v6):
        cfg=self.cfg;g=self.g;gn=self.gn;ref=self.ref;mpc=self.mpc
        launch_time=self.launch_time;launch_pose=self.launch_pose;launch_velocity=self.launch_velocity
        top=self.top;land_x=self.land_x;top_time=self.top_time;top_state=self.top_state;top_x=self.top_x
        push_at=cfg.get('push_at',.6);push_for=cfg.get('push_for',.14);pushdelta=cfg.get('push_delta',.4);launch_x=cfg.get('launch_x',None)
'''+textwrap.indent(phaseblock,'        ')+'''
        self.launch_time=launch_time;self.launch_pose=launch_pose;self.launch_velocity=launch_velocity;self.mpc=mpc;self.last_phase=phase;self.calls+=1
        target=np.array(q6,float)+(tau+2.*np.array(v6,float))/60.
        for i in(2,5):target[i]=v6[i]+tau[i]/.6
        raw=target.copy();target[[0,1,3,4]]=np.clip(target[[0,1,3,4]],-3.,3.)
        for i in(0,3):target[i+1]=np.clip(target[i+1],target[i]-1.0843,target[i]+.85)
        target[[2,5]]=np.clip(target[[2,5]],-60.,60.)
        return dict(tau=tau,processed_target=target,raw_inversePD_target=raw,phase=phase,launch_time=launch_time,mpc_log=self.mpc.last_log if phase in('approach','recover')else None)
    def observe_top(self,t,x,actual_x,actual_vx,takeoff_observed,both_top):
        if takeoff_observed and both_top and not self.top:
            cfg=self.cfg;self.land_x=float(np.clip(actual_x+cfg.get('capture_time',.3)*max(actual_vx,0)+cfg.get('landing_offset',.1),cfg.get('landing_min_x',.35),2.5))
            self.top_time=t;self.top_state=x.copy();self.top_x=float(x[0]);self.top=True

def state_and_inverse_feedback353(root13,default_joint_pos,policy,legjoint_ids,wheeljoint_ids,origin,edge_x):
    """Use actual original D1-D3 policy feedback plus declared privileged translation/yaw."""
    # policy unscaled slicing supplied explicitly by runtime adapter, no guessed35 ABI.
    x,y,z,w=root13[3:7];R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    omega=policy['base_ang_vel'];gravity=policy['projected_gravity'];lq=policy['leg_pos']+default_joint_pos[legjoint_ids];lv=policy['leg_vel'];wv=policy['wheel_vel']
    predict_s=.005;lq=lq+predict_s*lv;gravity=gravity-predict_s*np.cross(omega,gravity)
    roll=math.atan2(-gravity[1],-gravity[2]);pitch=math.atan2(gravity[0],math.hypot(gravity[1],gravity[2]));yaw=math.atan2(R[1,0],R[0,0])
    state=np.array([root13[0]-origin[0]-edge_x,yaw,pitch,lq[1],lq[0]-lq[1],lq[3],lq[2]-lq[3],root13[7],(omega[1]*math.sin(roll)+omega[2]*math.cos(roll))/max(math.cos(pitch),.15),omega[1]*math.cos(roll)-omega[2]*math.sin(roll),lv[1],lv[0]-lv[1],lv[3],lv[2]-lv[3]])
    q6=np.array([lq[1],lq[0],0.,lq[3],lq[2],0.]);v6=np.array([lv[1],lv[0],wv[0],lv[3],lv[2],wv[1]])
    assert np.isfinite(state).all()and np.isfinite(q6).all()and np.isfinite(v6).all()
    return state,q6,v6
'''
ast.parse(bridge);(D/'source/source_event_mpc353.py').write_text(bridge,encoding='utf8')
check=r'''"""Compute source nominal gains without stepping and compare exact source equations."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
from pathlib import Path
import ast,copy,hashlib,json,sys,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,v):
    with(R/name).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
try:
    assert not(R/'CPU353_ONCE_CONSUMED.json').exists()
    for row in json.loads((N/'INDEX353_SOURCE_FROZEN.json').read_bytes())['files']:
        p=Path(row['path']);assert p.stat().st_size==row['bytes']and H(p)==row['SHA']
    put('CPU353_ONCE_CONSUMED.json',dict(epoch=time.time(),models=0,physics_steps=0,SDK=0,network=0,optimizer=0))
    import numpy as np,mujoco
    physics_calls=[0]
    def forbidden(*a,**kw):physics_calls[0]+=1;raise AssertionError('This gain extraction cannot advance physics')
    originalstep=mujoco.mj_step;mujoco.mj_step=forbidden
    sys.path.insert(0,str(N/'source'));import control_core as core
    core.ROOT=Path('F:/RMPOLAR-RL/traditional_control_20261101')
    from full_lqr import AsymmetricPlant
    from source_event_mpc353 import SourceEventMPC353
    cfg=json.loads((N/'source/config353.json').read_bytes());plant=AsymmetricPlant(True)
    g=plant.full_lqr(cfg['start_delta']);gn=plant.full_lqr(cfg['landing_delta'])
    def pack(gain):return{k:v.tolist()for k,v in gain.items()if k in('q','tau','K','A','B','Ad','Bd','P','Q','R')}
    bundle=dict(epoch=time.time(),config=cfg,g=pack(g),gn=pack(gn),source_engine=mujoco.__version__,physics_steps=0,nominal_source_gains_not_current_PhysX_identification=True,actuator_order=list(core.ORDER))
    put('SOURCE353_NOMINAL_MPC_GAINS_AND_CONFIG.json',bundle)
    ctrl=SourceEventMPC353(bundle)
    # Compare source branch from actual successful controller with identical inputs.
    original=(N/'source/hybrid_trial.py').read_text('utf8');a=original.index('        if launch_time is None and');b=original.index('        p.torque_control(tau)',a)
    import textwrap
    block=compile(textwrap.dedent(original[a:b]),'original_successful_hybrid_phase_block','exec')
    fixtures=[]
    for j,(t,px,vx,top)in enumerate(((0.,-.8,0.,False),(.66,-.49,1.4,False),(.70,-.44,1.4,False),(.88,-.2,1.4,False),(1.05,.08,1.3,False),(1.25,.32,.8,True),(1.5,.55,.2,True))):
        x=np.r_[g['q'],np.zeros(7)];x[0]=px;x[7]=vx
        q6=np.array([x[3],x[3]+x[4],0.,x[5],x[5]+x[6],0.]);v6=np.zeros(6)
        if top:ctrl.observe_top(t-.01,x,px,vx,True,True)
        context=dict(np=np,cfg=cfg,g=g,gn=gn,ref=ctrl.ref.copy(),mpc=copy.deepcopy(ctrl.mpc),launch_time=ctrl.launch_time,launch_pose=None if ctrl.launch_pose is None else ctrl.launch_pose.copy(),launch_velocity=None if ctrl.launch_velocity is None else ctrl.launch_velocity.copy(),top=ctrl.top,land_x=ctrl.land_x,top_time=ctrl.top_time,top_state=ctrl.top_state,top_x=ctrl.top_x,push_at=cfg['push_at'],push_for=cfg['push_for'],pushdelta=cfg['push_delta'],launch_x=cfg['launch_x'],t=t,x=x,q6=q6,v6=v6)
        exec(block,context);actual=ctrl.command(t,x,q6,v6)
        err=float(np.max(np.abs(actual['tau']-context['tau'])));assert err<1e-10
        fixtures.append(dict(time=t,phase=actual['phase'],max_tau_error=err))
    assert physics_calls[0]==0
    put('CPU353_SOURCE_PHASE_BRIDGE_NO_STEP.json',dict(epoch=time.time(),passed=True,physics_steps=0,models=0,SDK=0,network=0,fixtures=fixtures,gain_SHA=H(R/'SOURCE353_NOMINAL_MPC_GAINS_AND_CONFIG.json'),original_phase_equations_reused=True,current50Hz_execution_not_yet_validated=True,source100Hz_model_dt=.01,originalphysics2500us_unchanged=True))
    print(json.dumps(dict(passed=True,physics_steps=0,fixtures=fixtures,gainSHA=H(R/'SOURCE353_NOMINAL_MPC_GAINS_AND_CONFIG.json'))))
except BaseException:
    put('CPU353_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_replay_once=True));raise
'''
ast.parse(check);(D/'extract353_gains_and_verify_bridge_CPU_once.py').write_text(check,encoding='utf8')
files=[p for p in sorted(D.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
put(D/'INDEX353_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
print(json.dumps(dict(prepared=True,root=str(D),INDEX_SHA=H(D/'INDEX353_SOURCE_FROZEN.json'),physics=0,SDK=0,NN=0)))
