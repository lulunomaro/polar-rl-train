"""Static FK/forward tests only. No physics steps, controller or rollout imports.
Independent oracle: extracted body-frame STL transformed with body_xmat/xpos;
step-prism extrema checked by independent convex-hull linear programs.
"""
from pathlib import Path
import hashlib, importlib.util, json, math, struct, time, traceback
import numpy as np
import mujoco
from scipy.spatial import cKDTree,ConvexHull
from scipy.optimize import linprog
from mesh_support import TireMeshSupport,StepPatch
HERE=Path(__file__).resolve().parent
AUDIT=HERE.parent
MODEL=AUDIT/'mod4v1_usd_source_aligned.xml'
KIN=Path(r'F:\RMPOLAR-RL\traditional_control_20261101\kinematics.py')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def quat(roll,pitch,yaw):
    cr,sr=math.cos(roll/2),math.sin(roll/2);cp,sp=math.cos(pitch/2),math.sin(pitch/2);cy,sy=math.cos(yaw/2),math.sin(yaw/2)
    return [cy*cp*cr+sy*sp*sr,cy*cp*sr-sy*sp*cr,sy*cp*sr+cy*sp*cr,sy*cp*cr-cy*sp*sr]
def plain(x):
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [plain(v) for v in x]
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    return x

def lp_z_interval(v,step):
    e,f,l=step.frame();eq=ConvexHull(v).equations;half=step.width_m/2
    A=np.vstack([eq[:,:3],np.r_[-f,0.],np.r_[f,0.],np.r_[-l,0.],np.r_[l,0.]])
    b=np.r_[-eq[:,3],-f@e,step.depth_m+f@e,half-l@e,half+l@e]
    lo=linprog([0,0,1],A_ub=A,b_ub=b,bounds=[(None,None)]*3,method='highs')
    if lo.status==2:return None
    if not lo.success:raise ValueError(lo.message)
    hi=linprog([0,0,-1],A_ub=A,b_ub=b,bounds=[(None,None)]*3,method='highs')
    if not hi.success:raise ValueError(hi.message)
    return [float(lo.fun),float(-hi.fun)]


def main():
    assert not (HERE/'STATIC_FORWARD_RESULTS.json').exists(),'Preserve the prior attempt'
    assert sha(MODEL)=='0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324'
    counts={'mj_forward_calls':0,'physics_step_calls':0}
    old_forward=mujoco.mj_forward
    def forward(m,d):counts['mj_forward_calls']+=1;return old_forward(m,d)
    def forbidden_step(*args,**kwargs):counts['physics_step_calls']+=1;raise AssertionError('Physics stepping is prohibited in static helper tests')
    mujoco.mj_forward=forward
    for name in ['mj_step','mj_step1','mj_step2']:setattr(mujoco,name,forbidden_step)
    spec=importlib.util.spec_from_file_location('readonly_mod4_FK',KIN);kin=importlib.util.module_from_spec(spec);spec.loader.exec_module(kin)
    model=mujoco.MjModel.from_xml_path(str(MODEL));support=TireMeshSupport(model)
    freeadr=int(model.joint('floating_base').qposadr[0])
    wq={s:int(model.joint(s+'_wheel_spin').qposadr[0]) for s in ['left','right']}
    oracle={}
    for side in ['left','right']:
        p=AUDIT/'usd_meshes'/(side+'_tire.stl');raw=p.read_bytes();num=struct.unpack_from('<I',raw,80)[0];dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])
        oracle[side+'_tire']=np.unique(np.frombuffer(raw,dtype=dt,count=num,offset=84)['v'].reshape(-1,3),axis=0).astype(float)
    cases=[
      {'name':'neutral_vertex','left':(0,0),'right':(0,0),'wheel':(0,0),'rpy':(0,0,0),'xy':(-.3,0),'plane':0.},
      {'name':'neutral_half_facet','left':(0,0),'right':(0,0),'wheel':(math.pi/16,math.pi/16),'rpy':(0,0,0),'xy':(-.3,0),'plane':0.},
      {'name':'neutral_quarter_facet','left':(0,0),'right':(0,0),'wheel':(math.pi/32,-math.pi/32),'rpy':(0,0,0),'xy':(-.3,0),'plane':0.},
      {'name':'folded','left':(.30,-.25),'right':(.30,-.25),'wheel':(.3,.3),'rpy':(0,0,0),'xy':(-.3,0),'plane':0.},
      {'name':'pitched','left':(-.10,.15),'right':(-.10,.15),'wheel':(1.2,-.8),'rpy':(0,.18,.1),'xy':(-.3,0),'plane':0.},
      {'name':'rolled','left':(.15,-.10),'right':(.15,-.10),'wheel':(.6,-.4),'rpy':(.15,-.05,0),'xy':(-.3,0),'plane':0.},
      {'name':'asymmetric','left':(.15,-.25),'right':(-.10,.05),'wheel':(.2,1.1),'rpy':(-.12,-.10,.4),'xy':(-.3,0),'plane':0.},
      {'name':'full_on_step','left':(0,0),'right':(0,0),'wheel':(.12,.31),'rpy':(0,0,.15),'xy':(.35,0),'plane':.27},
      {'name':'straddle_edge_on_top','left':(0,0),'right':(0,0),'wheel':(.4,.7),'rpy':(0,.1,.2),'xy':(0,0),'plane':.27},
      {'name':'partial_corner','left':(0,-.10),'right':(0,-.10),'wheel':(.7,-.3),'rpy':(.12,-.1,.25),'xy':(.025,.97),'plane':0.},
      {'name':'outside_lateral','left':(0,0),'right':(0,0),'wheel':(.1,.3),'rpy':(.03,.04,0),'xy':(.30,1.30),'plane':0.}]
    rows=[];max_oracle=0.;max_lp=0.;max_floor=0.;failures=[];all_times=[]
    for case in cases:
      try:
        data=mujoco.MjData(model)
        data.qpos[freeadr:freeadr+3]=[*case['xy'],.45];data.qpos[freeadr+3:freeadr+7]=quat(*case['rpy'])
        kin.set_configuration(model,data,left=case['left'],right=case['right'],check_limits=False)
        for side,angle in zip(['left','right'],case['wheel']):data.qpos[wq[side]]=angle
        mujoco.mj_forward(model,data)
        q0=data.qpos.copy();v0=data.qvel.copy();t0=float(data.time)
        env=support.envelopes(data);hint=support.root_z_translation(data,case['plane']);grade0=support.step_envelope(data)
        assert np.array_equal(data.qpos,q0) and np.array_equal(data.qvel,v0) and data.time==t0
        per={}
        for name,en in env.items():
            side=name.split('_')[0];bid=int(model.geom_bodyid[model.geom(name).id]);R=np.array(data.xmat[bid]).reshape(3,3);p=np.array(data.xpos[bid]);direct=oracle[name]@R.T+p
            err=max(cKDTree(direct).query(en['world_vertices'])[0].max(),cKDTree(en['world_vertices']).query(direct)[0].max());max_oracle=max(max_oracle,float(err))
            assert err<1e-7,(case['name'],name,'PCA/world oracle',err)
            meshid=int(model.geom_dataid[model.geom(name).id]);per[name]={'world_oracle_max_error_m':float(err),'before_min_xyz_m':en['min_xyz_m'],'before_max_xyz_m':en['max_xyz_m'],
                'mesh_PCA_pos':np.array(model.mesh_pos[meshid]),'mesh_PCA_quat_wxyz':np.array(model.mesh_quat[meshid]),
                'exact_vertical_support_from_wheel_body_center_m':float(data.xpos[bid,2]-en['lowest_z_m']),
                'center_minus_circumradius_low_z_error_m':float((data.xpos[bid,2]-.06369999796152115)-en['lowest_z_m'])}
        data.qpos[freeadr+2]+=hint['root_dz_m'];mujoco.mj_forward(model,data)
        after=support.envelopes(data);minz=min(en['lowest_z_m'] for en in after.values());max_floor=max(max_floor,abs(minz-case['plane']));assert abs(minz-case['plane'])<1e-10
        grade=support.step_envelope(data)
        # Partial and rotated finite-footprint queries: independent 3D convex LP.
        lpchecks=[]
        for step in [StepPatch(),StepPatch(edge_xy=(.05,.02),forward_xy=(math.cos(.3),math.sin(.3)),width_m=.31,depth_m=.4)]:
            graded=support.step_envelope(data,step)
            for name,en in after.items():
                interval=lp_z_interval(en['world_vertices'],step);gg=graded['per_tire'][name]
                if interval is None:
                    assert not gg['overlaps_top_projection'],(case['name'],name,'unexpected overlap')
                    lpchecks.append({'tire':name,'interval':None})
                else:
                    assert gg['overlaps_top_projection'],(case['name'],name,'missing overlap')
                    err=max(abs(interval[0]-gg['z_min_over_top_footprint_m']),abs(interval[1]-gg['z_max_over_top_footprint_m']));max_lp=max(max_lp,err);assert err<1e-7,(case['name'],name,'clip vs LP',err)
                    lpchecks.append({'tire':name,'LP_interval_m':interval,'clip_LP_max_error_m':err})
        closure=[]
        for side in ['left','right']:
            for aa,bb in [('proximal_a','proximal_b'),('distal_a','distal_b'),('gas_end','gas_mount')]:closure.append(float(np.linalg.norm(data.site(side+'_'+aa).xpos-data.site(side+'_'+bb).xpos)))
        outside=[]
        for j in range(model.njnt):
            if model.jnt_limited[j]:
                value=float(data.qpos[int(model.jnt_qposadr[j])]);lo,hi=model.jnt_range[j]
                if value<lo or value>hi:outside.append({'joint':model.joint(j).name,'q':value,'range':[float(lo),float(hi)]})
        assert data.time==0.;all_times.append(float(data.time))
        rows.append(dict(case,root_z_hint=hint,per_tire=per,root_z_after_m=float(data.qpos[freeadr+2]),lowest_z_after_m=minz,step_grade_after=grade,LP_checks=lpchecks,closure_max_m=max(closure),joint_limit_outside=outside))
      except Exception:
        failures.append({'case':case,'error':traceback.format_exc()})
    # One closed-chain neutral FK, then static independent wheel angle scans.
    data=mujoco.MjData(model);kin.set_configuration(model,data,check_limits=False);scan=[]
    for angle in np.linspace(0,2*math.pi,65)[:-1]:
        for side in ['left','right']:data.qpos[wq[side]]=angle
        mujoco.mj_forward(model,data);en=support.envelopes(data);bid=model.body('left_wheel').id
        scan.append({'wheel_angle_rad':float(angle),'vertical_support_m':float(data.xpos[bid,2]-en['left_tire']['lowest_z_m'])})
        assert data.time==0.
    tstart=time.perf_counter()
    for _ in range(100):support.envelopes(data);support.root_z_translation(data);support.step_envelope(data)
    mean_ms=(time.perf_counter()-tstart)*10
    summary={'status':'PASS_STATIC_FORWARD_ONLY' if not failures else 'FAIL_STATIC_FORWARD_CASES','mujoco':mujoco.__version__,'model_sha256':sha(MODEL),'helper_sha256':sha(HERE/'mesh_support.py'),
        'static_pose_cases':len(rows),'requested_pose_cases':len(cases),'wheel_angle_scan_samples':len(scan),**counts,'physics_time_advanced_s':0.,'all_data_time_zero':all(t==0 for t in all_times),
        'world_vertex_vs_STL_body_transform_max_error_m':max_oracle,'step_clip_vs_independent_LP_max_error_m':max_lp,'root_Z_lowest_plane_residual_max_m':max_floor,
        'neutral_wheel_rotation_exact_vertical_support_range_m':[min(x['vertical_support_m'] for x in scan),max(x['vertical_support_m'] for x in scan)],
        'nominal_circumradius_m':.06369999796152115,'combined_3_query_mean_ms_100_calls':mean_ms,'benchmark_is_not_realtime_guarantee':True,
        'source_kinematics_sha256':sha(KIN),'no_parent_source_edits':True,'acceptance_thresholds_added':False,'helper_observation_role':'initialization/grading truth geometry only, never deployable sensor observations','failures':failures}
    (HERE/'STATIC_FORWARD_RESULTS.json').write_text(json.dumps(plain({'summary':summary,'cases':rows,'neutral_wheel_rotation_scan':scan}),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    (HERE/'QUICK_TEST_SUMMARY.json').write_text(json.dumps(plain(summary),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps(plain(summary),ensure_ascii=False,indent=2))
    assert not failures, 'Preserved static-pose errors in STATIC_FORWARD_RESULTS.json'
if __name__=='__main__':
    try:main()
    except Exception:
        (HERE/'TEST_FAILURE_001.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
