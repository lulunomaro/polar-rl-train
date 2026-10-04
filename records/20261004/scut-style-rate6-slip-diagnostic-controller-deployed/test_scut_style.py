"""Verify diagnostic-only slip does not bypass physical/data-quality failures."""
import argparse,copy,json
from pathlib import Path
from scut_style_gate import assess
D=Path(__file__).resolve().parent
Q=D.parent/'MOD4_SPIN_CONTACT_GATE_CALIBRATION_20261004'
p=argparse.ArgumentParser();p.add_argument('--report');args=p.parse_args()
r=json.loads((Path(args.report) if args.report else Q/'continuation_receipts/production/auto_0064_contact_assessment_cap6_white_v2_rate.json').read_text())
before=copy.deepcopy(r)
a=assess(r)
assert a['pass_'] and a['prior_loaded015_assessment']['pass_'] is False
assert r==before,'Never modify old reports'
assert len([x for x in a['individual'] if x['slip_diagnostic_reasons']])==2
checks=['existing19234 reclassified, prior failure retained, raw unchanged']
def failure(name,edit):
    q=copy.deepcopy(r);edit(q);assert not assess(q)['pass_'],name;checks.append(name)
failure('single dead environment veto',lambda q:q['alive'].__setitem__(0,False))
failure('single nonfinite contact veto',lambda q:q['substep_contact_readback']['per_environment']['loaded_impulse_weighted_tangent_speed'][0].__setitem__(1,float('nan')))
failure('missing contact veto',lambda q:q['substep_contact_readback']['per_environment']['loaded_samples'][0].__setitem__(1,0))
failure('incomplete callback evidence',lambda q:q['substep_contact_readback'].__setitem__('callbacks',29999))
failure('normal force consistency veto',lambda q:q['substep_contact_readback']['per_environment']['mean_normal_force_N'][0].__setitem__(1,0))
failure('closure unchanged',lambda q:q.__setitem__('max_closure_m',.0021))
failure('parameter readback unchanged',lambda q:q['final_parameter_audit'].__setitem__('actual_parameters_pass',False))
failure('XY drift group limit unchanged',lambda q:q['per_environment'].__setitem__('spin_translation_speed',[.13]*88))
failure('yaw tracking unchanged',lambda q:q['per_environment'].__setitem__('yaw_error',[5.]*88))
failure('wheel mean load unchanged',lambda q:q['per_environment'].__setitem__('right_fz',[1.]*88))
failure('tilt severe individual unchanged',lambda q:q['per_environment']['peak_tilt'].__setitem__(0,16.))
failure('both low severe individual unchanged',lambda q:q['per_environment']['longest_both_low_s'].__setitem__(0,.021))
q=copy.deepcopy(r)
q['substep_contact_readback']['per_environment']['longest_loaded_over015_s'][0][1]=.020
assert assess(q)['pass_'] and not assess(q)['prior_loaded015_assessment']['pass_']
checks.append('sustained slip shadow preserved without new safety certification')
receipt=dict(pass_=True,checks=checks,check_count=len(checks),scope='CPU acceptance contracts, not new physical evidence')
(D/'CPU_VERIFIED.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
