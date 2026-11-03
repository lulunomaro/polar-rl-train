"""One approved public-nominal centroidal run: max27 NumPy FK /60 body-sum traversals."""
from pathlib import Path
import datetime,hashlib,json,os,sys,traceback
R=Path(__file__).resolve().parent;TASK=R.parent
COUNTS={'FK_top_level':0,'FK_recursive':0,'FK_all_entries':0,'momentum_body_sum_evaluations':0,'separate_coefficient_assembly_sweeps':0,'centroidal_COM_JCOM_reductions':0,'nominal_constants_objects':0,'SDK_modelboot_forward_RNE_integrator_runtime':0}
PARTIAL=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new(p,v):
    assert not p.exists(),str(p)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def rawnew(p,b):
    assert not p.exists(),str(p)
    p.write_bytes(b)
def main():
    global np
    assert not (R/'SOURCE_PREEXEC.json').exists(),'Consumed once-only prototype; inspect saved output, never replay'
    method=json.loads((R/'METHOD.json').read_text(encoding='utf-8'))
    assert method['FK_budget']['top_level_max']==27 and method['momentum_sum_budget']['evaluations_max']==60
    inputs=[Path(__file__),R/'METHOD.json',TASK/'CONTACT_PROXY_NOMINAL_V1/nominal_model.py',TASK/'CONTACT_PROXY_NOMINAL_V1/PUBLIC_NOMINAL_CONSTANTS.json',TASK/'JUMP270_V1/GAIN_BANK.json',TASK/'TALL_ROUGH_BANK_V1/gain_delta20.json',TASK/'TALL_ROUGH_BANK_V1/gain_delta0.json',TASK/'AIR_PITCH_AUTHORITY_V1/REPORT.md']
    before=[{'path':str(p),'bytes':p.stat().st_size,'SHA':sha(p)}for p in inputs]
    assert before[2]['SHA']=='d7d6092292e71bd3f028ce3dcd365e171b0c32b68030b460aec1d65bd6dc9323'
    assert before[3]['SHA']=='14c38264568f8859ba86b567509318a125355bbd24fe9d35aefa6e9354ea900f'
    rawnew(R/'PREEXEC_SOURCE.py',Path(__file__).read_bytes())
    new(R/'SOURCE_PREEXEC.json',{'status':'SOURCE_BUDGET_AND_FIXED_ALGEBRA_CASES_LOCKED_BEFORE_NUMPY_MODEL_OR_FK','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':before,'method':method,'counters_before':dict(COUNTS),'no_old_QA_or_physics_or_raw':True})
    for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
    import numpy as np
    sys.path.insert(0,str(TASK))
    from CONTACT_PROXY_NOMINAL_V1.nominal_model import NominalModel,axis_R
    class CountedModel(NominalModel):
        def __init__(self):
            COUNTS['nominal_constants_objects']+=1;self._fk_depth=0
            super().__init__(fd_rad=method['central_difference_epsilon_rad'])
        def fk(self,*a,**kw):
            assert COUNTS['FK_all_entries']<27,'FK budget exceeded: stop before evaluating'
            COUNTS['FK_all_entries']+=1
            COUNTS['FK_recursive' if self._fk_depth else 'FK_top_level']+=1;self._fk_depth+=1
            try:return super().fk(*a,**kw)
            finally:self._fk_depth-=1
    model=CountedModel();assert len(model.bodies)==31 and len(model.joints)==30
    poses=[]
    for spec in method['poses']:
        value=json.loads((TASK/spec['path']).read_text(encoding='utf-8'))
        for key in spec['gain_key'].split('.'):value=value[key]
        q=value['q'];poses.append((spec['name'],np.array([q[3],q[3]+q[4],q[5],q[5]+q[6]],float)))
    wheel_names=['left_wheel_spin','right_wheel_spin'];guide_names=[f'guide_roller_{i:02d}' for i in range(8)];spin_names=wheel_names+guide_names
    atol=method['comparison']['abs_SI'];rtol=method['comparison']['rel']
    def check_pair(a,b,label):
        a=np.asarray(a,float);b=np.asarray(b,float);err=np.abs(a-b);allow=atol+rtol*np.maximum(np.abs(a),np.abs(b));ok=bool(np.all(err<=allow))
        record={'test':label,'passed':ok,'max_abs_SI':float(err.max(initial=0.)),'allowed_rule':'1e-8abs+1e-10rel in declared quantity SI, algebra only'}
        assert ok,json.dumps(record);return record
    def crossmat(x):
        x,y,z=x;return np.array([[0.,-z,y],[z,0.,-x],[-y,x,0.]])
    def descend(i,ancestor):
        while True:
            if i==ancestor:return True
            parent=model.bodies[i]['parent']
            if parent is None:return False
            i=model.body_index[parent]
    def prepare_data(d):
        p=d['pose'];com=p['com_B'];rot=p['R_body_B'];m=model.mass
        Jv=np.zeros((31,3,14));Jw=Jv.copy();Jv[:,:,:4]=d['Jcom'];Jw[:,:,:4]=d['Jrot'];analytic=[]
        for k,name in enumerate(spin_names,4):
            joint=model.joints[model.joint_index[name]];bid=model.body_index[joint['body']]
            assert joint['type']=='hinge'
            axis=rot[bid]@np.asarray(joint['axis'],float);axis/=np.linalg.norm(axis)
            pivot=p['body_B'][bid]+rot[bid]@np.asarray(joint['pos_m'],float);ids=[]
            for i in range(31):
                if descend(i,bid):Jw[i,:,k]=axis;Jv[i,:,k]=np.cross(axis,com[i]-pivot);ids.append(model.bodies[i]['name'])
            analytic.append({'joint':name,'axis_B3':axis.tolist(),'pivot_B3':pivot.tolist(),'descendants':ids,'phase_fixture_rad':0.,'independent_rate_not_filled_zero':True})
        inertia=rot@model.I_local@np.transpose(rot,(0,2,1));M=float(m.sum());center=np.einsum('n,ni->i',m,com)/M;Jcenter=np.einsum('n,nik->ik',m,Jv)/M
        COUNTS['centroidal_COM_JCOM_reductions']+=2
        return {'mass':m,'com':com,'IB':inertia,'Jv':Jv,'Jw':Jw,'center':center,'Jcenter':Jcenter},analytic
    def body_sum(data,v,collect=False):
        assert COUNTS['momentum_body_sum_evaluations']<60,'Body-sum budget exceeded: stop'
        COUNTS['momentum_body_sum_evaluations']+=1
        omega=v[:3];rates=v[3:];G=data['center'];VG=np.cross(omega,G)+data['Jcenter']@rates;H=np.zeros(3);C=np.zeros((3,17)) if collect else None;balance=np.zeros(3)
        for i in range(31):
            mass=data['mass'][i];r=data['com'][i];rho=r-G;I=data['IB'][i];Jv=data['Jv'][i];Jw=data['Jw'][i]
            vi=np.cross(omega,r)+Jv@rates;wi=omega+Jw@rates
            H+=I@wi+np.cross(rho,mass*(vi-VG))
            if collect:
                C[:,:3]+=I+mass*((rho@rho)*np.eye(3)-np.outer(rho,rho))
                C[:,3:]+=I@Jw+mass*crossmat(rho)@(Jv-data['Jcenter']);balance+=mass*rho
        return H,C,balance
    mixed=np.array(method['fixed_mixed']['omega_B3']+method['fixed_mixed']['qdot4']+method['fixed_mixed']['wheel2']+method['fixed_mixed']['guide00_to07'],float)
    Q=axis_R([0,0,1],.2)@axis_R([0,1,0],-.4)@axis_R([1,0,0],.3)
    for name,q in poses:
        start=dict(COUNTS);d=model.derivatives(q);data,analytic=prepare_data(d)
        zero,C,balance=body_sum(data,np.zeros(17),True);I=C[:,:3];A=C[:,3:];tests=[check_pair(zero,np.zeros(3),'zero_momentum'),check_pair(I,I.T,'locked_inertia_symmetry'),check_pair(balance,np.zeros(3),'centroidal_first_moment_kg_m')]
        eig=np.linalg.eigvalsh((I+I.T)/2);assert bool(np.all(eig>0.)),'Locked inertia not SPD';np.linalg.cholesky((I+I.T)/2)
        basis=[]
        for k,label in enumerate(method['velocity_columns']):
            v=np.zeros(17);v[k]=1.;H,_,_=body_sum(data,v);tests.append(check_pair(H,C@v,'basis_directsum_'+label));basis.append({'input':label,'H_direct3_kg_m2_s':H.tolist()})
        H,_,_=body_sum(data,mixed);tests.append(check_pair(H,C@mixed,'fixed_mixed_directsum_vs_matrix'))
        rotated={'mass':data['mass'],'com':data['com']@Q.T,'IB':Q[None,:,:]@data['IB']@Q.T[None,:,:],'Jv':np.einsum('ab,nbk->nak',Q,data['Jv']),'Jw':np.einsum('ab,nbk->nak',Q,data['Jw']),'center':Q@data['center'],'Jcenter':Q@data['Jcenter']}
        vm=mixed.copy();vm[:3]=Q@vm[:3];HQ,_,_=body_sum(rotated,vm);covpred=(Q@I@Q.T)@vm[:3]+(Q@A)@vm[3:]
        tests.extend([check_pair(HQ,Q@H,'constant_basis_covariance_directsum'),check_pair(HQ,covpred,'constant_basis_covariance_matrix')])
        Aq=A[:,:4];Aw=A[:,4:6];Ag=A[:,6:];Ac=Aq@np.ones(4);Ad=Aq@np.array([0.,1.,0.,1.]);guard=1e-8+1e-10*max(float(np.linalg.norm(Ac)),float(np.linalg.norm(Ad)))
        ratio={'status':'UNKNOWN_SMALL_DENOMINATOR','value':None}if abs(Ac[1])<=guard else {'status':'NOMINAL_Y_ROW_ALGEBRAIC_RATIO_NOT_PATH_OR_GAIN','value':float(-Ad[1]/Ac[1])}
        ratio.update(denominator_Ac_y=float(Ac[1]),denominator_guard_kg_m2=guard)
        used={k:COUNTS[k]-start[k]for k in COUNTS};assert used['FK_top_level']==used['FK_all_entries']==9 and used['FK_recursive']==0 and used['momentum_body_sum_evaluations']==20
        PARTIAL.append({'pose':name,'q4_absolute_rad':q.tolist(),'r_COM_B3_m':data['center'].tolist(),'total_mass_kg':float(model.mass.sum()),'I_locked_B_kg_m2':I.tolist(),'Aq_B_kg_m2':Aq.tolist(),'Awheel_B_kg_m2':Aw.tolist(),'Aguide_B_kg_m2':Ag.tolist(),'Ac_B_kg_m2':Ac.tolist(),'Adelta_B_kg_m2':Ad.tolist(),'minus_Adelta_y_over_Ac_y':ratio,'locked_inertia_eigenvalues_kg_m2':eig.tolist(),'SPD':True,'analytic_independent_spin_columns':analytic,'basis_momenta':basis,'mixed_velocity17':mixed.tolist(),'mixed_H_B3_kg_m2_s':H.tolist(),'rotated_mixed_H3_kg_m2_s':HQ.tolist(),'tests':tests,'evaluation_counts':used,'no_armature_rotor_or_episode_override_added':True,'phase_zero_is_synthetic_fixture_only':True})
    assert COUNTS['FK_top_level']==COUNTS['FK_all_entries']==27 and COUNTS['FK_recursive']==0 and COUNTS['momentum_body_sum_evaluations']==60
    assert all(sha(Path(x['path']))==x['SHA']for x in before),'Pinned small input/source changed'
    result={'status':'PUBLIC_NOMINAL_3D_CENTROIDAL_COEFFICIENT_ALGEBRA_PASS_NOT_PLANT_OR_CONTROL_VALIDATION','method_SHA':sha(R/'METHOD.json'),'source_preexec_SHA':sha(R/'SOURCE_PREEXEC.json'),'counts':COUNTS,'body_count':31,'shape_rate_order':['Lhip','Lcrank','Rhip','Rcrank']+spin_names,'base_angular_velocity_order':['x','y','z'],'I_and_A_units':'kg*m^2, joint angles rad; H kg*m^2/s','Q':Q.tolist(),'poses':PARTIAL,'coordinate_and_H_definition':'wholeCOM momentum, regular chassis BODY, full3D; unknown inertial H0/external torque not zeroed','missing_model_bindings':method['unknowns'],'not_included':'joint armature/physical rotor reflection or controller/plant contact/PD/D4','not_independent_validation':'same public nominal pose/rate data; separate matrix vs vector body formulas and coordinate transform, no SDK massmatrix or dynamics oracle','old_raw_DR_H5_mesh_Git_agents_oldQA_reads_or_calls':False,'PH8pending':True}
    new(R/'RESULT.json',result)
    rows=['# AIR_CENTROIDAL_COEFFICIENT_V1 — 一次public nominal代数prototype','','3个旧public pose；全31body COM转动+轨道动量，不调用旧terms，不删wheel rotational；phase0只是synthetic fixture，2wheel/8guide独立rate列按axis/tree解析。','', '|pose|I_locked yy kg·m²|Ac_y kg·m²|Adelta_y kg·m²|−Adelta_y/Ac_y|','|---|---:|---:|---:|---:|']
    for p in PARTIAL:rows.append('|'+p['pose']+'|'+format(p['I_locked_B_kg_m2'][1][1],'.12g')+'|'+format(p['Ac_B_kg_m2'][1],'.12g')+'|'+format(p['Adelta_B_kg_m2'][1],'.12g')+'|'+str(p['minus_Adelta_y_over_Ac_y']['value'])+'|')
    rows+=['','所有pose I_locked对称/SPD、zero、17basis/directsum、固定mixed及同mixed常坐标旋转协变均通过预锁1e−8abs+1e−10rel（各自SI单位）代数自洽预算，非实际物理误差界。','实际27top-level FK、0recursive、27all-FK；60whole-body momentum evaluations，每pose20，zero同一遍历组装I/A，无额外coefficient sweep；另外每pose2次COM/JCOM聚合如预锁。0SDK modelboot/forward/RNE/step/runtime。','完整逐pose I_locked3x3/Aq3x4/Awheel3x2/Aguide3x8/Ac/Adelta、Y行ratio/guard、basis/mixed/残差见[RESULT](<RESULT.json>)；[预执行锁](<SOURCE_PREEXEC.json>)、[固定方法预算](<METHOD.json>)和[receipt](<RECEIPT.json>)。','unknownH0/guide及wheel实际自旋/phase、外接触、softpassive、physicalrotor/armature仍缺绑；未加armature/DR，不代表全plant总动量或实际反作用可消。ratio不是路径/gain，不选h第三range。','零积分器自洽≠独立plant/dynamic验证、未知接触/landing稳定性/驱动可达性/wholeRM/270/hardware资格。未控制、未改旧source或oldscore，PH8pending。']
    text='\n'.join(rows)+'\n';assert len(rows)<=70;rawnew(R/'REPORT.md',text.encode('utf-8'))
    receipt={'status':result['status'],'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'SOURCE_PREEXEC_SHA':sha(R/'SOURCE_PREEXEC.json'),'METHOD_SHA':sha(R/'METHOD.json'),'RESULT_SHA':sha(R/'RESULT.json'),'REPORT_SHA':sha(R/'REPORT.md'),'counts':COUNTS,'all_small_source_before_after_SHA_equal':before,'old_source_or_score_changed':False,'independent_plant_or_dynamic_validation':False,'new_controller_or_range_or_gain_selected':False,'report_lines':len(rows),'stop_after_this_once_run':True,'PH8pending':True}
    rawnew(R/'RECEIPT.json',(json.dumps(receipt,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8'))
    print(json.dumps({'status':result['status'],'counts':COUNTS,'poses':[{'name':p['pose'],'Iyy':p['I_locked_B_kg_m2'][1][1],'Ac_y':p['Ac_B_kg_m2'][1],'Adelta_y':p['Adelta_B_kg_m2'][1],'ratio':p['minus_Adelta_y_over_Ac_y'],'SPD':p['SPD'],'max_algebra_abs_SI':max(t['max_abs_SI']for t in p['tests'])}for p in PARTIAL],'RESULT_bytes':(R/'RESULT.json').stat().st_size,'REPORT_SHA':receipt['REPORT_SHA'],'RECEIPT_SHA':sha(R/'RECEIPT.json'),'report_lines':len(rows)},ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except BaseException:
        err=traceback.format_exc();print(err,file=sys.stderr)
        if not (R/'FAILURE.txt').exists():(R/'FAILURE.txt').write_text(err,encoding='utf-8')
        if not (R/'FAILURE_SOURCE.py').exists():(R/'FAILURE_SOURCE.py').write_bytes(Path(__file__).read_bytes())
        if not (R/'FAILURE_RECEIPT.json').exists():new(R/'FAILURE_RECEIPT.json',{'status':'STOPPED_NO_RETRY_OR_THRESHOLD_BUDGET_CHANGE','counts':COUNTS,'partial_pose_results':PARTIAL,'source_SHA':sha(Path(__file__)),'physics_Git_oldQA':False})
        raise
