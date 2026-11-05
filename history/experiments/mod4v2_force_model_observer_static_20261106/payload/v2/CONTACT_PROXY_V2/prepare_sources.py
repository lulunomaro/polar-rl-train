"""New public-parameter export and narrowly derived runtime; no simulator/QA."""
from pathlib import Path
import ast,hashlib,json,traceback
import export_public_nominal as export
D=Path(__file__).resolve().parent
OLD=D.parent.parent/'mod4v1_lqr_mpc_robust_20261102/CONTACT_PROXY_NOMINAL_V1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fresh(p,s):
    with p.open('x',encoding='utf-8',newline='\n')as f:f.write(s)
def replace(s,a,b):
    assert s.count(a)==1,('Source anchor mismatch',a,s.count(a))
    return s.replace(a,b,1)
def main():
    assert not (D/'PREPARATION_PREEXEC.json').exists(),'Preparation already consumed; inspect evidence'
    roots=[D/'prepare_sources.py',D/'export_public_nominal.py',OLD/'nominal_model.py',OLD/'contact_proxy.py']
    export.new_json(D/'PREPARATION_PREEXEC.json',dict(sources=[dict(path=str(p),SHA=sha(p))for p in roots],static_pose_limit=3,physics_steps_allowed=0,old_QA_run=False))
    export.main();constant_sha=sha(D/'PUBLIC_NOMINAL_CONSTANTS.json')
    s=(OLD/'nominal_model.py').read_text(encoding='utf-8')
    s=replace(s,"14c38264568f8859ba86b567509318a125355bbd24fe9d35aefa6e9354ea900f",constant_sha)
    s=replace(s,"0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324",export.XML_SHA)
    s=replace(s,"    try:a=np.asarray(x,dtype=float)","    try:\n        raw=np.asarray(x)\n        if raw.dtype.kind not in 'fiu':raise ModelDomainError(label+' real numeric vector, no bool/object')\n        a=np.asarray(raw,dtype=float)")
    s=replace(s,"self.hinges=np.array([j['type']=='hinge' for j in self.joints])", "self.hinges=np.array([j['type']=='hinge' and j['name'].endswith(('_rocker_pin','_coupler_pin','_knee','_distal_pin','_gas_pin')) for j in self.joints])")
    begin=s.index('    def leg_values(');end=s.index('    def fk(',begin)
    s=s[:begin]+'''    def leg_values(self,h,c,side):
        # Exact hip-local/delta source branch of actual P0 kinematics_v2.
        # Active output coordinates and drive followers keep their full lift.
        p=self.pins[side];delta=c-h;L=lambda a,b:float(np.linalg.norm(p[a]-p[b]))
        points={k:v.copy() for k,v in p.items()};points['A']=ry2(p['A'],delta)
        points['B']=intersect(points['A'],L('A','B'),points['P'],L('B','P'),math.copysign(1.,cross2(p['P']-p['A'],p['B']-p['A'])))
        rocker=angle2(p['B']-p['P'],points['B']-points['P'])
        points['C']=p['P']+ry2(p['C']-p['P'],rocker)
        points['D']=intersect(p['K'],L('K','D'),points['C'],L('C','D'),math.copysign(1.,cross2(p['C']-p['K'],p['D']-p['K'])))
        shin=angle2(p['D']-p['K'],points['D']-points['K'])
        for key in ('W','T'):points[key]=p['K']+ry2(p[key]-p['K'],shin)
        values=dict(hip=h,crank=c,drive_hip_spin=h,drive_input_spin=c,wheel_spin=0.,
            rocker_pin=rocker,coupler_pin=angle2(p['B']-p['A'],points['B']-points['A'])-delta,
            knee=shin,distal_pin=angle2(p['D']-p['C'],points['D']-points['C'])-rocker,
            gas_pin=angle2(p['T']-p['S'],points['T']-points['S']),gas_slide=float(np.linalg.norm(points['T']-points['S']))-L('T','S'))
        for key in ('rocker_pin','coupler_pin','knee','distal_pin','gas_pin'):values[key]=float(wrap(values[key]))
        return values
    def joint_values(self,q4,check_limits=True):
        q4=vec(q4,4,'absolute continuous q4');values={}
        for i,side in enumerate(('left','right')):
            h,c=q4[2*i:2*i+2];bounds=self.public['mechanical_delta_boundaries'][side]
            if check_limits and not bounds['delta_min_rad']-1e-9<=c-h<=bounds['delta_max_rad']+1e-9:
                raise ModelDomainError(side+' outside neutral-connected P0 delta branch; no legacy active window')
            values.update({side+'_'+k:v for k,v in self.leg_values(h,c,side).items()})
        out=np.array([values.get(j['name'],0.) for j in self.joints])
        if check_limits:
            for j,v in zip(self.joints,out):
                low,high=j['range_rad_or_m']
                if j['limited'] and ((low is not None and v<low-1e-9) or (high is not None and v>high+1e-9)):
                    raise ModelDomainError('outside public P0 physical joint bounds: '+j['name'])
        return out
''' +s[end:]
    old="        return {'force_body_xz_N2':np.array(forces),'rhs4':rhs,'condition2':conditions,'solve_residual_Nm2':np.array(residual)}"
    new="""        axes=[self.leg_coordinates(terms,i,F) for i,F in enumerate(forces)]
        return {'force_body_xz_N2':np.array(forces),'rhs4':rhs,'condition2':conditions,'solve_residual_Nm2':np.array(residual),
            'leg_axial_compression_N2':[v['axial_compression_N']for v in axes],
            'leg_Tp_y_Nm2':[v['Tp_y_Nm']for v in axes],'leg_coordinates2':axes}
    def leg_coordinates(self,terms,side,force_xz):
        # Sagittal wheel-center load equivalent, not measured axial force/contact.
        p=terms['jacobians']['pose'];body=self.body_index[('left','right')[side]+'_thigh']
        r=(p['wheel_B'][side]-p['body_B'][body])[[0,2]];length=float(np.linalg.norm(r))
        if length<=1e-9:raise ModelDomainError('leg-axis length singular')
        F=vec(force_xz,2,'wheel-center force xz');J=terms['Jwheel_xz2'][side]
        axial=-float(F@r)/length;tp=float(r[1]*F[0]-r[0]*F[1])
        taskJ=np.vstack((r@J/length,np.array([r[1],-r[0]])@J/(length*length)))
        return dict(axial_compression_N=axial,Tp_y_Nm=tp,length_m=length,
            J_length_theta=taskJ,sign_contract='J_Ltheta.T @ [-Fcompression,Tp_y] == Jwheel_xz.T @ F_xz',
            generalized_reconstruction_Nm=taskJ.T@np.array([-axial,tp]))"""
    s=replace(s,old,new);ast.parse(s);fresh(D/'nominal_model.py',s)
    p=(OLD/'contact_proxy.py').read_text(encoding='utf-8')
    p=replace(p,"ROLE='proposed_engineering_nominal_model_not_measured_calibration'","ROLE='v2_HW300N60_public_nominal_proxy_not_measured_calibration'")
    p=replace(p,"<=self.nominal_model_confidence_cap<=1:","<=self.nominal_model_confidence_cap<=.55:")
    p=replace(p,"abs(wrap(q-old[1])-(v+old[2])*.5*dt)","abs((q-old[1])-(v+old[2])*.5*dt)")
    p=replace(p,"common=['PUBLIC_NOMINAL_PARAMETERS_NOT_EPISODE_DR'", "common=['HW300N60_300N_FORCE_CURVE_AND_DAMPING_NOT_MEASURED','GUIDE_SPIN_AND_SOFT_CLOSURE_LOAD_UNOBSERVED','PUBLIC_NOMINAL_PARAMETERS_NOT_EPISODE_DR'")
    p=replace(p,"    threshold_role: str=ROLE", "    threshold_role: str=ROLE\n    leg_axial_compression_proxy_N2: tuple=(None,None)\n    leg_Tp_y_proxy_Nm2: tuple=(None,None)")
    p=replace(p,"        return Result(t,tuple(normals),tuple(confidence),tuple(sigmas),tuple(model_forces),tuple(why2),tuple(common),debug)","""        axial=[None,None];tp=[None,None]
        for i,F in enumerate(model_forces):
            if normals[i] is not None:
                axes=self.model.leg_coordinates(terms,i,F)
                axial[i]=axes['axial_compression_N'];tp[i]=axes['Tp_y_Nm']
        debug['axial_Tp_are_same_planar_load_reexpression_not_additional_sensors']=True
        return Result(t,tuple(normals),tuple(confidence),tuple(sigmas),tuple(model_forces),tuple(why2),tuple(common),clean_debug(debug),
            leg_axial_compression_proxy_N2=tuple(axial),leg_Tp_y_proxy_Nm2=tuple(tp))""")
    ast.parse(p);fresh(D/'contact_proxy.py',p)
    export.new_json(D/'SOURCE_DERIVATION.json',dict(parent_runtime_sources=[dict(path=str(x),SHA=sha(x))for x in roots[2:]],
        new_runtime=[dict(path=str(D/n),SHA=sha(D/n))for n in ('nominal_model.py','contact_proxy.py')],
        constants_SHA=constant_sha,source_XML_SHA=export.XML_SHA,
        changed=['BODY inertia from actual source principal MCI','P0 hip-local branch; continuous absolute active/drive lift',
            'passive-only derivative wrapping; direct active-angle temporal consistency','None for infinite passive bound endpoints',
            'HW300N60 gas/physical limits/cylinder identity','hard <=.55 confidence cap','planar axial/Tp sign-explicit reexpression'],
        simulator_calls=0,old_tests_run=False,old_files_written=False,parent_controller_connected=False))
    print('NEW_CONTACT_PROXY_V2_RUNTIME_SOURCES_READY_NO_SIMULATOR')
if __name__=='__main__':
    try:main()
    except BaseException:
        if not (D/'PREPARATION_ERROR.txt').exists():fresh(D/'PREPARATION_ERROR.txt',traceback.format_exc())
        raise
