"""Fixed public nominal static design correction at reference q4; NOT force feedback.
Only sealed SDK-free terms/solve_terms. No new FK/derivative implementation.
"""
from pathlib import Path
import os,sys,json,traceback
for _k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[_k]='1'
ROOT=Path(__file__).resolve().parents[1];D=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import numpy as np
from CONTACT_PROXY_V2.nominal_model import NominalModel,XML_SHA,CONSTANTS_SHA
class NominalStaticReferenceFF:
    def __init__(self):
        g=json.loads((ROOT/'nominal_gain_v2.json').read_text(encoding='utf-8'))
        if g['model_SHA']!=XML_SHA:raise ValueError('Public nominal gain/P0 identity mismatch')
        g=g['gain'];self.q0=np.array([g['q'][3],g['q'][3]+g['q'][4],g['q'][5],g['q'][5]+g['q'][6]])
        self.tau0=np.asarray(g['tau'],float)[[0,1,3,4]];self.model=NominalModel()
        self.internal_fk_calls=0;self.target_terms_calls=0;original_fk=self.model.fk
        def counted(*a,**kw):
            self.internal_fk_calls+=1;return original_fk(*a,**kw)
        self.model.fk=counted
        self.base_terms=self._terms(self.q0)
        self.F0=self.model.solve_terms(self.base_terms,self.tau0)['force_body_xz_N2'].copy()
        self.F0.flags.writeable=False;self.q0.flags.writeable=False;self.tau0.flags.writeable=False
        self.base_tau_reconstructed=self._tau(self.base_terms)
        self.base_design=dict(q0=self.q0.tolist(),trim_tau4_Nm=self.tau0.tolist(),F0_xz_N2=self.F0.tolist(),
            roll_pitch_rad=[0.,0.],proper_BODY_m_s2=[0.,0.,9.81],qd_qdd_omega_alpha='zero STATIC assumption',
            design_not_measured_contact=True,source_model_SHA=XML_SHA,public_constants_SHA=CONSTANTS_SHA)
        self.last_terms=self.base_terms
    def _terms(self,q_ref4):
        self.target_terms_calls+=1;z=np.zeros(4);w=np.zeros(3)
        return self.model.terms(q_ref4,z,z,[0.,0.,9.81],w,w)
    def _tau(self,t):
        return t['load4']-t['tauGas4']-t['tauOtherPassive4']-np.concatenate([J.T@F for J,F in zip(t['Jwheel_xz2'],self.F0)])
    def correction(self,q_ref4):
        """Return output Nm [LH,LC,RH,RC] at reference, not current actual q.
        F0 stays the design load from existing trim. No measured/proxy Fn or DR.
        """
        self.last_terms=self._terms(q_ref4)
        return self._tau(self.last_terms)-self.tau0

def plain(v):
    if isinstance(v,dict):return {k:plain(x)for k,x in v.items()}
    if isinstance(v,(tuple,list)):return [plain(x)for x in v]
    return v.tolist()if hasattr(v,'tolist')else v

def new(name,v):
    with (D/name).open('x',encoding='utf-8')as f:json.dump(plain(v),f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

def main():
    if (D/'PREEXEC.json').exists():raise RuntimeError('Two-target design already consumed; inspect saved result, no replay')
    dq=np.array([.02,-.02,-.02,.02])
    new('PREEXEC.json',dict(kind='TWO_TARGET_STATIC_REFERENCE_FORMULA_NOT_NEW_CASE',source_model_SHA=XML_SHA,
        public_constants_SHA=CONSTANTS_SHA,nominal_gain_path=str(ROOT/'nominal_gain_v2.json'),dq_absolute4_rad=dq,
        expected_target_terms_calls=2,internal_finite_difference_FK='sealed implementation, expected18; report actual',
        fixed_proper=[0.,0.,9.81],motion_roll_pitch='zero fixed STATIC design',
        design_F0='natural existing-trim inverse, separately per wheel, never fixed mg/2 or measured Fn',
        analytic_draft='design_static_ff.py is UNEXECUTED; not imported, replaced by reuse-only static_ff.py',
        simulator_compile_forward_step_DARE_static_optimization_oldQA_raw_hardware_Git_agent_calls=0))
    f=NominalStaticReferenceFF();delta=f.correction(f.q0+dq);a,b=f.base_terms,f.last_terms
    dg=b['load4']-a['load4'];ds=-(b['tauGas4']-a['tauGas4'])
    de=-np.concatenate([(J1-J0).T@F for J0,J1,F in zip(a['Jwheel_xz2'],b['Jwheel_xz2'],f.F0)])
    common=(delta[:2]+delta[2:])/2;diff=(delta[:2]-delta[2:])/2
    projected=np.concatenate([diff,-diff]);den=float(dq@dq)
    slope={k:float(v@dq/den)for k,v in dict(total=delta,gravity=dg,minus_gas=ds,minus_JTF0=de).items()}
    slope.update(old_PD_Kp_Nm_per_rad=120.,directional_restoring_coefficient_120_plus_static_secant=120.+slope['total'])
    r=dict(status='COMPLETE_TWO_TARGET_STATIC_DESIGN_ONLY_NOT_ROOT_CAUSE_OR_CONTROL_VALIDATION',base_design=f.base_design,
        q1_absolute4_rad=f.q0+dq,dq_absolute4_rad=dq,tau_static_q1_Nm4=f.tau0+delta,
        q0_trim_consistency_max_Nm=float(np.max(abs(f.base_tau_reconstructed-f.tau0))),
        delta_required_tau_Nm4=delta,delta_common_Nm2=common,delta_differential_Nm2=diff,
        differential_only_projection_Nm4=projected,old_PD_reference_step_120dq_Nm4=120*dq,
        required_static_error_equivalent_delta_over120_rad4=delta/120.,
        decomposition_delta_Nm4=dict(gravity=dg,minus_gas=ds,minus_JTF0=de),directional_secant_Nm_per_rad=slope,
        counts=dict(target_configurations=f.target_terms_calls,internal_SDKfree_FK=f.internal_fk_calls,
                    simulator_compile_forward_step_DARE_static_optimization_oldQA_raw_hardware_Git_agent=0),
        interpretation='Two-point secant only along this coupled dq, not diagonal stiffness or4x4 Hessian; negative static required-torque slope reduces the quasistatic PD restoring projection120+k. No dynamic or contact claim.',
        gas_curve_k2000_d3_not_measured=True,unknown_true_Fn_or_alpha_or_sampledDR_not_inputs=True,
        controller_model_CONTACT_or_old_validator_modified=False,analytic_draft_executed=False)
    new('RESULT.json',r)
    if r['q0_trim_consistency_max_Nm']>1e-10 or np.max(abs(delta-dg-ds-de))>1e-9:raise ValueError('Static formula consistency failure')
    if f.target_terms_calls!=2 or f.internal_fk_calls!=18:raise ValueError('Unexpected sealed terms evaluation count; stop without extra calls')
    print(json.dumps(plain(r),ensure_ascii=True))
if __name__=='__main__':
    try:main()
    except BaseException:
        if not (D/'ERROR.json').exists():new('ERROR.json',dict(error=traceback.format_exc(),no_automatic_retry=True))
        raise
