"""One fresh P0 static/14state-DARE generation. No integration, no old test/case."""
from pathlib import Path
import hashlib,json,os,sys,traceback
for name in('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
import numpy as np
import mujoco
from v2_linearization import V2LinearPlant,PACKAGE,OLD,kin_v2
import xml.etree.ElementTree as ET
D=Path(__file__).resolve().parent
PUBLISHED_SCENE_SHA='c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125'
CALLS={};STAGE='before_model'
def serial(x):
    if isinstance(x,np.ndarray):
        if np.iscomplexobj(x):return [[float(z.real),float(z.imag)]for z in x]
        return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return{k:serial(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return[serial(v)for v in x]
    return x
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n')as f:json.dump(serial(x),f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def counted(name,original):
    def call(*args,**kwargs):CALLS[name]=CALLS.get(name,0)+1;return original(*args,**kwargs)
    return call
def forbidden(name):
    def call(*args,**kwargs):CALLS[name]=CALLS.get(name,0)+1;raise RuntimeError('Forbidden integration/legacy-kin call: '+name)
    return call

def main():
    global STAGE
    target=D/'nominal_gain_v2.json';assert not target.exists(),'gain already exists; no overwrite'
    out=D/'nominal_generation_attempt001';out.mkdir(exist_ok=False)
    for name in('mj_step','mj_step1','mj_step2','mj_Euler','mj_RungeKutta','mj_implicit'):
        if hasattr(mujoco,name):CALLS[name]=0;setattr(mujoco,name,forbidden(name))
    mujoco.mj_forward=counted('mj_forward',mujoco.mj_forward)
    kin_v2.set_configuration=counted('P0_set_configuration_absolute',kin_v2.set_configuration)
    # Importing old method definitions is permitted; actually invoking legacy
    # set_configuration would fail rather than use its old operating window.
    import control_core
    control_core.kin.set_configuration=forbidden('legacy_set_configuration')
    scene=PACKAGE/'mjcf/scene.xml';raw=scene.read_bytes();actual=hashlib.sha256(raw).hexdigest();assert actual==PUBLISHED_SCENE_SHA
    root=ET.fromstring(raw);original_option=dict(root.find('option').attrib)
    meshdir=(scene.parent/root.find('compiler').get('meshdir','')).resolve()
    if not meshdir.is_dir():raise FileNotFoundError(str(meshdir))
    root.find('compiler').set('meshdir',str(meshdir))
    root.find('option').set('timestep','.0005');root.find('option').set('iterations','100')
    if root.find('option').get('integrator')!='implicitfast'or root.find('option').get('solver')!='Newton':raise ValueError('Unexpected original integration/solver')
    source=dict(asset_package=str(PACKAGE),scene_path=str(scene),scene_published_SHA256=PUBLISHED_SCENE_SHA,scene_loaded_small_XML_SHA256=actual,release_report=str(PACKAGE.parents[2]/'MOD4V2_P0_RELEASE_REPORT_V1.md'),parameters_path=str(PACKAGE/'model_parameters.json'),kinematics_path=str(PACKAGE/'kinematics_v2.py'),kinematics_API='ABSOLUTE hip/crank; q_from adapts chart delta to hip+delta; public check_limits=True',original_projection_sources=[str(OLD/'control_core.py'),str(OLD/'full_lqr.py')],mesh_payload_hashing=0,source_assets_written=0)
    save(out/'START.json',dict(stage=STAGE,source=source,physics_steps=0,original_option=original_option,runtime_XML_copy_changes={'meshdir':str(meshdir),'timestep':.0005,'iterations':100},delta=-.2,control_dt=.01,force_curve_calibrated=False,extra_flat_linearization_fixture_NOT_CAD_skill=True))
    STAGE='compile_same_P0_flat_fixture';m=mujoco.MjModel.from_xml_string(ET.tostring(root,encoding='unicode'));p=V2LinearPlant(m)
    assert(m.nbody,m.nq,m.nv,m.nu,m.neq)==(32,37,36,6,10)
    assert abs(p.radius-.0625)<1e-12 and abs(m.opt.timestep-.0005)<1e-15 and m.opt.iterations==100
    gas={}
    for side in('left','right'):
        j=m.joint(side+'_gas_slide');ji=j.id;di=int(m.jnt_dofadr[ji]);qi=int(m.jnt_qposadr[ji])
        assert m.jnt_stiffness[ji]==2000. and m.dof_damping[di]==3.
        gas[side]=dict(k_N_m=float(m.jnt_stiffness[ji]),d_Ns_m=float(m.dof_damping[di]),slide_range_m=m.jnt_range[ji].tolist(),springref=float(m.qpos_spring[qi]))
    STAGE='static_equilibrium_delta_minus_point2';base,tau3,res=p.equilibrium(-.2)
    save(out/'STATIC_PREFIX.json',dict(stage=STAGE,q4=base,tau3_per_side=tau3,projected_residual_norm=res,radius=p.radius,mass=p.mass,gas=gas,physics_steps=0,calls=CALLS))
    print('STATIC_PREFIX',json.dumps(serial(dict(q4=base,tau3=tau3,residual=res,radius=p.radius,mass=p.mass))),flush=True)
    STAGE='inherited_full_lqr_14state_DARE';g=p.full_lqr(-.2)
    M,f,B=p.full_reduced(g['q']);residual=B@g['tau']+f
    S=g['R']+g['Bd'].T@g['P']@g['Bd']
    dare=g['Ad'].T@g['P']@g['Ad']-g['P']-g['Ad'].T@g['P']@g['Bd']@np.linalg.solve(S,g['Bd'].T@g['P']@g['Ad'])+g['Q']
    spectrum=float(np.max(np.abs(g['eigenvalues'])))
    assert all(np.isfinite(g[k]).all()for k in('q','tau','K','A','B','Ad','Bd','P','Q','R','eigenvalues'))
    assert spectrum<1.,'Closed-loop local linear model is not Schur stable'
    assert all(CALLS.get(n,0)==0 for n in('mj_step','mj_step1','mj_step2','mj_Euler','mj_RungeKutta','mj_implicit','legacy_set_configuration'))
    d=p.tmp;closure=max(float(np.linalg.norm(d.site_xpos[a]-d.site_xpos[b]))for a,b in p.pairs)
    mimic=max(abs(float(d.joint(s+'_drive_'+a+'_spin').qpos[0]-d.joint(s+'_'+b).qpos[0]))for s in('left','right')for a,b in(('hip','hip'),('input','crank')))
    g['static_residual']=float(np.linalg.norm(residual))
    result=dict(kind='MOD4V2_P0_HW300N60_NOMINAL_STATIC_AND_LOCAL14STATE_DARE_ZERO_INTEGRATION_NOT_TASK_QUALIFICATION',model_SHA=actual,gain=g,source=source,model=dict(nbody=m.nbody,nq=m.nq,nv=m.nv,nu=m.nu,neq=m.neq,total_mass_kg=p.mass,tire_geometry='P0 cylinders, not old v1 USD tire mesh',tire_radius_m=p.radius,original_option=original_option,loaded_option=dict(timestep=float(m.opt.timestep),integrator='implicitfast',solver='Newton',iterations=int(m.opt.iterations)),gas=gas,active_axes='continuous',mechanical_delta_bounds={s:kin_v2.mechanical_delta_bounds(s)for s in('left','right')}),statics=dict(symmetric_q4=base,symmetric_projected_residual_norm=res,full_projected_residual=residual,full_projected_residual_norm=float(np.linalg.norm(residual)),static_torque_Nm=g['tau'],COM_root_bracket_rad=[-np.pi/2,np.pi/2],bracket_is_NOT_actuator_limit=True),numeric=dict(closedloop_spectral_radius=spectrum,DARE_residual_fro=float(np.linalg.norm(dare)),DARE_relative_residual=float(np.linalg.norm(dare)/max(1.,np.linalg.norm(g['P']))),P_symmetry_fro=float(np.linalg.norm(g['P']-g['P'].T)),closure_m=closure,mimic_rad=mimic,projected_mass_condition=float(np.linalg.cond(M))),linearization=dict(state_order='x,yaw,pitch,Lhip,Lcrank-minus-hip,Rhip,Rcrank-minus-hip,then7rates',motor_rows='LH LC LW RH RC RW',control_dt_s=.01,method='Original AsymmetricPlant.full_chart/full_reduced/full_lqr + Plant.chart/reduced; only v2 kinematic chart and selected upright COM root replaced',projection='local circular wheel no-slip ground chart; not hybrid/soft-contact or CAD terrain closed-loop certificate',same_original_Q_R_ZOH_DARE=True),counts=dict(physics_steps=0,mj_step_calls=0,direct_API=CALLS),force_curve_calibrated=False,k2000_d3_unmeasured_approximation_kept=True,nominal_only_no_DR_or_jump_or_hardware=True,methods_for_parent_binding=dict(names=['q_from','q_from_full'],required_self_fields=['m','tmp','wheels','radius'],extra_custom_self_fields_required=False))
    STAGE='save_complete_gain';save(target,result)
    print('GAIN_COMPLETE',json.dumps(serial(dict(path=str(target),q=g['q'],tau=g['tau'],radius=p.radius,static_residual=g['static_residual'],spectral_radius=spectrum,DARE_relative_residual=result['numeric']['DARE_relative_residual'],physics_steps=0,counts=CALLS))),flush=True)

if __name__=='__main__':
    try:main()
    except BaseException:
        failure=D/'nominal_generation_attempt001/FIRST_ERROR.json'
        if failure.parent.exists()and not failure.exists():save(failure,dict(stage=STAGE,error=traceback.format_exc(),calls=CALLS,physics_steps=0,no_blind_retry=True))
        raise
