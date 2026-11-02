"""Compute source nominal gains without stepping and compare exact source equations."""
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
