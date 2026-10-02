from pathlib import Path
import json
import numpy as np
from scipy.linalg import expm
import pymupdf

HERE=Path(__file__).resolve().parent
S=json.loads((HERE/'results/summary.json').read_text(encoding='utf8'))
P=json.loads((HERE/'mod4_extracted_parameters.json').read_text(encoding='utf8'))
N=S['nominal_system'];A=np.array(N['A']);B=np.array(N['B']);Ad=np.array(N['Ad']);Bd=np.array(N['Bd']);K=np.array(N['K'])
checks={}
aug=np.block([[A,B],[np.zeros((4,14))]])
exact=expm(aug*N['Ts'])
checks['independent_exact_discretization_error']=float(max(np.max(abs(exact[:10,:10]-Ad)),np.max(abs(exact[:10,10:]-Bd))))
assert checks['independent_exact_discretization_error']<1e-10
rho=float(np.max(abs(np.linalg.eigvals(Ad-Bd@K))))
checks['independent_closed_loop_spectral_radius']=rho
assert rho<1 and abs(rho-N['max_discrete_pole'])<1e-10
trim=np.zeros(10);trim[[4,6]]=N['trim']
res=A@trim+B@np.array(N['Ud'])+np.array(N['zero_offset_acceleration'])
checks['trim_state_space_residual']=float(np.max(abs(res)))
assert checks['trim_state_space_residual']<1e-10
valid=json.loads((HERE/'results/feasible_gain_schedule.json').read_text(encoding='utf8'))
assert len(valid)==S['schedule_feasibility']['valid']
assert all(r['trim_within_motor_limits'] for r in valid)
assert all(np.all(np.array(r['trim_motor_positions_rad'])>=np.array([-.5,-1.2,-.5,-1.2])-1e-10) and np.all(np.array(r['trim_motor_positions_rad'])<=np.array([.5,.9,.5,.9])+1e-10) for r in valid)
checks['gain_points_total']=len(S['schedule']);checks['gain_points_within_reference_motor_limits']=len(valid)
assert len(S['cases'])==6 and len(S['robustness_trials'])==120 and len(S['gas_height_study']['cases'])==10
assert S['simulink_cross_check']['pass'] and S['simulink_cross_check']['max_state_difference']<1e-8
assert all(p['effective_vertical_inertia_kg']>0 for p in P['poses'])
assert all(np.max(abs(np.array(c['peak_motor_torque_nm'])[2:]))<=40+1e-8 for c in S['cases'])
assert all(np.max(abs(np.array(c['peak_motor_torque_nm'])[:2]))<=P['motor_parameters']['wheel_motor']['peak_torque_nm']+1e-8 for c in S['cases'])
checks['simulink_state_crosscheck']=S['simulink_cross_check']['max_state_difference']
armature=json.loads((HERE/'results/armature_audit.json').read_text(encoding='utf8'))
assert armature['pass'];checks['relative_rotor_inertia_algebra']=armature
pdf=HERE/'MOD4_MATLAB_WBR仿真报告_20260917.pdf'
d=pymupdf.open(pdf)
checks['pdf_pages']=len(d);checks['replacement_glyphs']=sum(p.get_text().count('\ufffd') for p in d)
assert checks['pdf_pages']==17 and checks['replacement_glyphs']==0
assert all(len(p.get_text())>200 for p in d)
for page in d:
    for block in page.get_text('blocks'):
        assert block[0]>=0 and block[1]>=0 and block[2]<=page.rect.width+1 and block[3]<=page.rect.height+1
status={'status':'PASS_REPRODUCIBLE_REDUCED_MODEL','scope':'Numerical, reference-joint-limit and PDF structure checks; no full-contact/RL/real-robot certification.','checks':checks}
(HERE/'results/verification.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(status,ensure_ascii=True))
