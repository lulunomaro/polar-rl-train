"""Exactly nine new static counterfactual rows; no integration/controller/DR/QA."""
from pathlib import Path
import datetime,hashlib,json,math,sys,traceback
D=Path(__file__).resolve().parent;T=D.parent;OLD=T.parent/'traditional_control_20261101'
N=dict(model_compile_attempts=0,model_compiles_completed=0,mj_forward_total=0,mj_forward_completed=0,setup_forward_calls=0,kinematic_set_configuration_calls=0,leg_configuration_branch_calls=0,candidate_rows_completed=0,integrator_attempts=0,explicit_RNE_attempts=0,controller_DR_oldQA_Git_agents_calls=0,raw_hashes=0)
ROWS=[];CURRENT='setup'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def main():
    global CURRENT
    assert not(D/'SOURCE_PREEXEC.json').exists(),'Consumed once-only grant: inspect prefix, never replay'
    scope=load(D/'PARENT_SCOPE.json');method=load(D/'METHOD.json')
    assert scope['budgets']['new_model_compiles']==1 and scope['budgets']['mj_forward_total_max']==12 and scope['budgets']['candidate_rows_max']==9
    inputs=[D/'PARENT_SCOPE.json',D/'METHOD.json',Path(__file__),T/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml',T/'physics_bridge.py',T/'sensor_core.py',OLD/'control_core.py',OLD/'full_lqr.py',OLD/'kinematics.py',OLD/'model_parameters.json',OLD/'reports/model_manifest.json',OLD/'dr_components.py',T/'PRIVATE_COLLISION_SUPPORT_V1/support.py',T/'PRIVATE_COLLISION_SUPPORT_V1/INDEX.json',T/'STARTUP_STAND_V1/controller.py',T/'TALL_ROUGH_BANK_V1/gain_delta0.json',T/'TALL_ROUGH_BANK_V1/gain_delta20.json',T/'STARTUP_STAND_V1/passive_settle001/front_rest_065/result.json']
    before=[dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p))for p in inputs]
    assert sha(T/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml')==scope['robot_SHA']==method['model_SHA']
    assert sha(T/'PRIVATE_COLLISION_SUPPORT_V1/support.py')==method['compiled_support_source_SHA']
    new(D/'SOURCE_PREEXEC.json',dict(status='METHOD_SOURCE_AND_BUDGET_LOCK_BEFORE_MODEL_IMPORT_OR_NEW_QUERIES',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sources=before,method=method,parent_scope=scope,counts_before=N.copy(),no_old_case_raw_or_QA=True))
    (D/'SOURCE_PREEXEC_RUNNER.py').write_bytes(Path(__file__).read_bytes())
    import numpy as np
    import mujoco
    originals={};original_model=mujoco.MjModel
    def forward(name,fn):
        def call(*a,**kw):
            assert N['mj_forward_total']<12,'Forward budget stop BEFORE extra call'
            N['mj_forward_total']+=1
            if CURRENT=='setup':N['setup_forward_calls']+=1
            out=fn(*a,**kw);N['mj_forward_completed']+=1;return out
        return call
    def forbidden(name,rne=False):
        def call(*a,**kw):
            N['explicit_RNE_attempts'if rne else'integrator_attempts']+=1
            raise AssertionError('Forbidden new study API: '+name)
        return call
    class ModelGate:
        @staticmethod
        def from_xml_string(*a,**kw):
            assert N['model_compile_attempts']<1,'Compile budget stop BEFORE extra call'
            N['model_compile_attempts']+=1
            out=original_model.from_xml_string(*a,**kw);N['model_compiles_completed']+=1;return out
        @staticmethod
        def from_xml_path(*a,**kw):raise AssertionError('Only inspected original factory from_xml_string allowed')
        @staticmethod
        def from_binary_path(*a,**kw):raise AssertionError('No binary model loading')
    original_set=None;original_leg=None;kin=None
    try:
        for name in ('mj_forward','mj_forwardSkip'):
            if hasattr(mujoco,name):originals[name]=getattr(mujoco,name);setattr(mujoco,name,forward(name,originals[name]))
        for name in ('mj_step','mj_step1','mj_step2','mj_Euler','mj_RungeKutta','mj_implicit'):
            if hasattr(mujoco,name):originals[name]=getattr(mujoco,name);setattr(mujoco,name,forbidden(name))
        for name in ('mj_rne','mj_rnePostConstraint'):
            if hasattr(mujoco,name):originals[name]=getattr(mujoco,name);setattr(mujoco,name,forbidden(name,True))
        mujoco.MjModel=ModelGate
        sys.path.insert(0,str(T));sys.path.insert(0,str(OLD))
        from physics_bridge import model_factory
        import kinematics as kin
        from PRIVATE_COLLISION_SUPPORT_V1.support import CompiledCollisionSupport
        m=model_factory(step=False);d=mujoco.MjData(m)
        cache=CompiledCollisionSupport(m)
        original_set=kin.set_configuration;original_leg=kin.leg_configuration
        def set_config(*a,**kw):N['kinematic_set_configuration_calls']+=1;return original_set(*a,**kw)
        def leg_config(*a,**kw):N['leg_configuration_branch_calls']+=1;return original_leg(*a,**kw)
        kin.set_configuration=set_config;kin.leg_configuration=leg_config
        fixture=load(T/scope['initial_fixture']);qp=np.asarray(fixture['final_qpos'],float);qv=np.asarray(fixture['final_qvel'],float)
        assert qp.shape==(m.nq,)and qv.shape==(m.nv,)and np.isfinite(qp).all()and np.isfinite(qv).all()
        quat=qp[3:7];assert abs(float(quat@quat)-1.)<=1e-12
        w,x,y,z=quat
        R=np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],[2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
        init_pitch=math.atan2(-R[2,0],math.hypot(R[0,0],R[1,0]));assert abs(init_pitch-fixture['final_rpy_rad'][1])<=1e-12
        names=('left_hip','left_crank','right_hip','right_crank');qids=np.array([m.joint(n).qposadr[0]for n in names])
        initial_q=qp[qids].copy();qmin=np.array([m.jnt_range[m.joint(n).id,0]for n in names]);qmax=np.array([m.jnt_range[m.joint(n).id,1]for n in names])
        expected_min=np.array([-.5000000058364024,-1.2000000140073657]*2);expected_max=np.array([.5000000058364024,.8999999772160105]*2)
        assert np.array_equal(qmin,expected_min)and np.array_equal(qmax,expected_max),'Current compiled active mapping not original startup boxes'
        projected=np.clip(initial_q,qmin,qmax)
        for i in(0,2):projected[i+1]=np.clip(projected[i+1],max(qmin[i+1],projected[i]-1.0843),min(qmax[i+1],projected[i]+.85))
        def gainq(p):
            a=np.asarray(load(p)['gain']['q'],float);assert a.shape==(7,)and np.isfinite(a).all();return np.array([a[3],a[3]+a[4],a[5],a[5]+a[6]])
        nominal=gainq(T/'TALL_ROUGH_BANK_V1/gain_delta0.json');tall=gainq(T/'TALL_ROUGH_BANK_V1/gain_delta20.json')
        specs=[('INITIAL_SAVED_FIXTURE',None,None)]
        for key,q in(('NOMINAL_Q',nominal),('PUBLIC_DELTA20_Q',tall)):
            specs.extend([(key+'_PITCH0',q,0.),(key+'_PITCH_INIT',q,init_pitch),(key+'_PITCH_0p60',q,.60)])
        specs.extend([('PUBLIC_DELTA20_COMMON_PLUS_INIT_PITCH_AT_INIT_PITCH',tall+init_pitch,init_pitch),('PUBLIC_DELTA20_COMMON_MINUS_INIT_PITCH_AT_INIT_PITCH',tall-init_pitch,init_pitch)])
        assert [a for a,b,c in specs]==method['cases_in_order']and len(specs)==9
        pairs=[('left_proximal_a','left_proximal_b'),('left_distal_a','left_distal_b'),('left_gas_end','left_gas_mount'),('right_proximal_a','right_proximal_b'),('right_distal_a','right_distal_b'),('right_gas_end','right_gas_mount')]
        chassis=m.body('chassis').id;wheelids=[m.body(s+'_wheel').id for s in('left','right')];tireids=[m.geom(s+'_tire').id for s in('left','right')]
        phase_names=['left_wheel_spin','right_wheel_spin']+['guide_roller_%02d'%i for i in range(8)]
        def limits():
            bad=[]
            for jid in range(m.njnt):
                if not m.jnt_limited[jid]:continue
                value=float(d.qpos[m.jnt_qposadr[jid]]);lo,hi=map(float,m.jnt_range[jid]);excess=max(0.,lo-value,value-hi)
                if excess>0.:bad.append(dict(joint=m.joint(jid).name,value=value,minimum=lo,maximum=hi,excess=excess,unit='m'if int(m.jnt_type[jid])==2 else'rad'))
            qa=d.qpos[qids].copy();delta=qa[[1,3]]-qa[[0,2]]
            return dict(all_compiled_limited_joints_legal_exact=not bad,violations=bad,active_absolute_limits_min_rad=qmin.tolist(),active_absolute_limits_max_rad=qmax.tolist(),active_absolute_legal_exact=bool(np.all(qa>=qmin)and np.all(qa<=qmax)),driver_delta_rad=delta.tolist(),driver_delta_box_rad=[-1.0843,.85],driver_delta_legal_exact=bool(np.all(delta>=-1.0843)and np.all(delta<=.85)),legacy_kinematics_operating_delta_box_NOT_current_driver=kin.PARAMS['limits'],no_input_or_limit_projected=True)
        def group(per,kind,dz=0.):
            a=[e for e in per if ('tire'if e['geom_name']in('left_tire','right_tire')else'guide'if e['geom_name'].startswith('guide_wheel_')else'hard')==kind]
            assert a,'Unbound collision group '+kind
            zlo=min(a,key=lambda e:e['min_xyz_m'][2]);return dict(minZ_m=float(zlo['min_xyz_m'][2]+dz),arggeom=zlo['geom_name'],arggeom_id=zlo['geom_id'],geom_count=len(a))
        for number,(name,q,pitch)in enumerate(specs,1):
            CURRENT=name;start_forward=N['mj_forward_total'];mujoco.mj_resetData(m,d)
            if q is None:
                d.qpos[:]=qp;d.qvel[:]=qv;mujoco.mj_forward(m,d)
                phase='Exact saved fixture passive/active/wheel/guide phase and qvel, no closure rewrite'
            else:
                d.qpos[:3]=m.qpos0[:3];d.qpos[3:7]=[math.cos(pitch/2),0.,math.sin(pitch/2),0.]
                kin.set_configuration(m,d,(float(q[0]),float(q[1]-q[0])),(float(q[2]),float(q[3]-q[2])),check_limits=False)
                phase='Canonical zero independent wheel+guide phases, original closed-chain branch; synthetic fixture only'
            assert N['mj_forward_total']==start_forward+1 and float(d.time)==0.
            bounds=cache.bounds(d,stage_time_s=float(d.time));per=bounds['per_geom'];assert len(per)==34
            tire=[next(e for e in per if e['geom_id']==i)for i in tireids];tires_min=np.array([e['min_xyz_m'][2]for e in tire]);dz=-float(tires_min.min())
            shift=np.array([0.,0.,dz]);com=np.asarray(d.subtree_com[chassis]).copy();mid=np.mean(np.asarray(d.geom_xpos)[tireids],axis=0);axle=np.mean(np.asarray(d.xpos)[wheelids],axis=0)
            active=d.qpos[qids].copy();signed=active-initial_q;ref_signed=active-projected
            peak=np.abs(signed)*1.875/2.;ref_peak=np.abs(ref_signed)*1.875/2.
            lim=limits();closure={a+'__'+b:float(np.linalg.norm(d.site(a).xpos-d.site(b).xpos))for a,b in pairs}
            mimic={s:dict(hip=float(d.joint(s+'_drive_hip_spin').qpos[0]-d.joint(s+'_hip').qpos[0]),crank=float(d.joint(s+'_drive_input_spin').qpos[0]-d.joint(s+'_crank').qpos[0]))for s in('left','right')}
            phase_q={n:float(d.joint(n).qpos[0])for n in phase_names}
            actual_pitch=math.atan2(-d.xmat[chassis].reshape(3,3)[2,0],math.hypot(d.xmat[chassis].reshape(3,3)[0,0],d.xmat[chassis].reshape(3,3)[1,0]))
            row=dict(case=name,counts_after_row=N.copy(),kind='NEW_STATIC_COUNTERFACTUAL_NOT_MEASURED_OR_SUPPORTED_STATE',data_time_s=float(d.time),initial_fixture_row=q is None,requested_pitch_rad=pitch,actual_cached_pitch_rad=actual_pitch,requested_absolute_q4_rad=None if q is None else q.tolist(),actual_geometric_absolute_q4_rad=active.tolist(),geometric_joint_qpos={m.joint(j).name:float(d.qpos[m.jnt_qposadr[j]])for j in range(m.njnt)if int(m.jnt_type[j])in(2,3)},limits=lim,geometry_status='COMPUTED_LIMITS_VALID'if not lim['violations']and lim['driver_delta_legal_exact']else'COMPUTED_LIMITS_INVALID_NO_SILENT_PROJECTION',phase_choice=phase,independent_wheel_guide_phase_rad=phase_q,closure_site_residual_m=closure,max_closure_site_residual_m=max(closure.values()),mimic_joint_residual_rad=mimic,current_world_root_xyz_m=d.qpos[:3].tolist(),current_world_root_quaternion_wxyz=d.qpos[3:7].tolist(),main_tire_minZ_before_m2=tires_min.tolist(),guide_before=group(per,'guide'),hard_before=group(per,'hard'),whole_COM_world_before_m3=com.tolist(),analytic_common_translation_dz_m=dz,hypothetical_rootXYZ_after_seating_m3=(d.qpos[:3]+shift).tolist(),hypothetical_rootZ_after_seating_m=float(d.qpos[2]+dz),main_tire_minZ_after_common_translation_m2=(tires_min+dz).tolist(),guide_after=group(per,'guide',dz),hard_after=group(per,'hard',dz),whole_COM_world_after_analytic_translation_m3=(com+shift).tolist(),main_tire_geom_origin_midpoint_world_after_m3=(mid+shift).tolist(),wheel_body_axle_midpoint_world_after_m3=(axle+shift).tolist(),COMx_minus_main_tire_geom_origin_midpoint_m=float(com[0]-mid[0]),COMx_minus_wheel_body_axle_midpoint_m=float(com[0]-axle[0]),per_collision_geom_raw_bounds=per,source_contact_margins_not_included=True,outward_numeric_padding_from_library_m=bounds['numeric_padding_m'],initial_actual_q4_rad=initial_q.tolist(),initial_reference_only_projected_q4_rad=projected.tolist(),reference_start_projection_delta_rad=(projected-initial_q).tolist(),reference_rate=dict(initial_actual_to_goal_signed_difference_rad=signed.tolist(),initial_reference_projected_to_goal_signed_difference_rad=ref_signed.tolist(),two_second_quintic_peak_actual_start_rad_s4=peak.tolist(),two_second_quintic_peak_reference_start_rad_s4=ref_peak.tolist(),max_peak_reference_rad_s=float(ref_peak.max()),minimum_duration_reference_speed_le_1rad_s=float(1.875*np.abs(ref_signed).max()),two_second_speed_feasible=bool(ref_peak.max()<=1.),target_active_driver_legal_exact=bool(lim['active_absolute_legal_exact']and lim['driver_delta_legal_exact']),fixture_row_is_not_a_selected_target=q is None,endpoint_only_not_swept_path=True),no_actual_support_force_or_stability_or_new_target_claim=True)
            ROWS.append(row);N['candidate_rows_completed']+=1;row['counts_after_row']=N.copy()
            new(D/'rows'/('%02d_%s.json'%(number,name)),row)
        assert(N['model_compiles_completed'],N['candidate_rows_completed'])==(1,9)and N['mj_forward_total']<=12
        assert N['mj_forward_completed']==N['mj_forward_total']==9 and N['setup_forward_calls']==0
        assert N['integrator_attempts']==N['explicit_RNE_attempts']==0
        assert all(sha(Path(e['path']))==e['SHA']for e in before),'Pinned small source/input changed'
        result=dict(status='NINE_PARENT_SPECIFIED_STATIC_GEOMETRY_ROWS_COMPLETE_NOT_SUPPORT_OR_STANDUP_PROOF',counts=N,engine_version=mujoco.__version__,source_small_before_after_equal=True,initial_pitch_from_saved_unit_quaternion_rad=init_pitch,root_quaternion_convention=method['root_convention'],all_rows=ROWS,robot_source_SHA=scope['robot_SHA'],old_score_or_sources_or_model_options_modified=False,contact_forces_or_ncon_not_used_as_observation=True,not_controller_input=True,static_endpoint_only_not_a_trajectory_or_phase_certificate=True,no_future_controller_or_PHY_permission=True,excluded_from_current_PH10_cutoff=True)
        new(D/'RESULT.json',result)
        lines=['# 新静态支撑几何：9指定counterfactual，不是起立/承载证明',f"实际计数1 compile / {N['mj_forward_total']} total mj_forward（setup {N['setup_forward_calls']}，public setter内部8+fixture1），0积分/显式RNE/controller/DR/旧QA。初姿pitch由saved wxyz求得{init_pitch:.12g}rad。",'原robot及34碰撞shape不改；compiled mesh vertex支撑/primitive解析极值，仅读同次forward缓存。public轮/guide相位0，fixture保持saved相位；不含contact shell/载荷/稳定性。','|case|假想轮底seating rootZ m|guide minZ/arg m|hard minZ/arg m|COMx−tireMid m|2s peak rad/s|limit合法|','|---|---|---|---|---|---|---|']
        for r in ROWS:lines.append(f"|{r['case']}|{r['hypothetical_rootZ_after_seating_m']:.6f}|{r['guide_after']['minZ_m']:.6f}/{r['guide_after']['arggeom']}|{r['hard_after']['minZ_m']:.6f}/{r['hard_after']['arggeom']}|{r['COMx_minus_main_tire_geom_origin_midpoint_m']:.6f}|{r['reference_rate']['max_peak_reference_rad_s']:.6f}|{r['geometry_status']}|")
        lines.extend(['最低主轮minZ的common dz只解析平移缓存，不再forward/改data；左右轮剩余gap另存，非强迫两轮同时承载。COMx相对cached tire geom-origin midpoint，另列wheel-axle参考，不是支撑多边形证书。','完整all-joint/driver边界、6对closure/mimic残差、q/phase/per-geom/2s速度在数值JSON。初姿实际软限越界原样记录，不投影测量；reference-only投影与其delta另列。速度仅端点quintic max，不证中间闭链/碰撞/driver可达。','正guide/hard间隙≠真实卸载或站稳；负值是该轮底放平假想姿态的几何干涉，不等于观测到真实接触力。不同pitch/δ/common shift仅诊断，不选V4目标/gain/时间。','[METHOD](<METHOD.json>) · [source锁](<SOURCE_PREEXEC.json>) · [9行数值](<RESULT.json>)。旧fixture/gate/模型/分数不改；当前PH10cutoff外新研究，后续controller/PHY须另批。'])
        assert len(lines)<=30
        with(D/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write('\n'.join(lines)+'\n')
        rec=dict(status=result['status'],UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),counts=N,report_lines=len(lines),sources_before_after_equal=True,source_preexec_SHA=sha(D/'SOURCE_PREEXEC.json'),result_SHA=sha(D/'RESULT.json'),report_SHA=sha(D/'REPORT.md'),no_new_synthetic_controller_or_physics_or_DR_or_oldQA_or_Git_agents=True,no_old_raw_or_asset_rehash=True,not_actual_support_stability_or_hardware_phase_binding=True,no_automatic_retry_or_followup_permission=True,excluded_from_current_PH10_cutoff=True)
        new(D/'RECEIPT.json',rec)
        compact=[dict(case=r['case'],rootZ=r['hypothetical_rootZ_after_seating_m'],guide=r['guide_after'],hard=r['hard_after'],COMx=r['COMx_minus_main_tire_geom_origin_midpoint_m'],ref2s_peak=r['reference_rate']['max_peak_reference_rad_s'],minimum_duration=r['reference_rate']['minimum_duration_reference_speed_le_1rad_s'],geometry_status=r['geometry_status'],closure=r['max_closure_site_residual_m'])for r in ROWS]
        print(json.dumps(dict(status=result['status'],counts=N,rows=compact,report_SHA=rec['report_SHA'],receipt_SHA=sha(D/'RECEIPT.json')),ensure_ascii=True))
    finally:
        for name,fn in originals.items():setattr(mujoco,name,fn)
        mujoco.MjModel=original_model
        if kin is not None and original_set is not None:kin.set_configuration=original_set
        if kin is not None and original_leg is not None:kin.leg_configuration=original_leg
if __name__=='__main__':
    try:main()
    except BaseException:
        e=traceback.format_exc();print(e)
        if not(D/'FAILURE.txt').exists():(D/'FAILURE.txt').write_text(e,encoding='utf-8')
        if not(D/'FAILURE_SOURCE.py').exists():(D/'FAILURE_SOURCE.py').write_bytes(Path(__file__).read_bytes())
        if not(D/'FAILURE_RECEIPT.json').exists():new(D/'FAILURE_RECEIPT.json',dict(status='STOP_FIRST_ERROR_NO_CORRECTIVE_RERUN',counts=N,candidate_rows_saved=len(ROWS),last_context=CURRENT,error=e,source_SHA=sha(Path(__file__)),integrator_or_controller_permission=False))
        raise
