"""Retained-condition and real-failure contracts; no simulation/PPO."""
import argparse,copy,json,sys,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--reports',type=Path,required=True);a=p.parse_args()
sys.path.insert(0,str(D))
sys.path.insert(1,str(D.parent/'MOD4_SCUT_STYLE_RATE_CONTINUE_20261004'))
sys.path.insert(1,str(D.parent/'MOD4_RATE6_SLIP_REPAIR_20261003'))
from scut_style_gate_v2 import assess,assess_flat,VERSION
try:from autonomy_policy import safety_veto
except ModuleNotFoundError:from autonomy_policy_actual import safety_veto
read=lambda n:json.loads((a.reports/n).read_text())
name='auto_0067_scut_style_latest6_multiseed_cap6_white_v2_flat_white_v2_20261002.json'
r=read(name);before=copy.deepcopy(r);result=assess_flat(r)
assert result['pass_'] and not result['prior_original_flat_admission']['eligible_for_mild_dr_trial']
assert r==before and [v['env'] for v in result['individual'] if v['slip_diagnostics']]==[3,53]
assert safety_veto(r)
contracts=['exact real 19575 flat slip-only failure reclassified without report mutation']
for key,value in [('vel_error',.26),('tilt',8.1),('max_tilt',12.1),('height_error',.031),
                  ('delta',.181),('d2',.251),('guide_force',1.1),('base_force',1.1),
                  ('left_mean_fz_substep',9.9),('right_mean_fz_substep',9.9),
                  ('longest_both_low_force_s_substep',.0151),('left_gap_max_control_m',.0021),('right_gap_max_control_m',.0021)]:
    v=copy.deepcopy(r)
    for i in (3,53):v['per_environment'][key][i]=value
    assert not assess_flat(v)['pass_'],key
    contracts.append('retained '+key)
v=copy.deepcopy(r)
for i in (6,56):v['per_environment']['stop_abs_speed'][i]=.121
assert not assess_flat(v)['pass_'];contracts.append('retained stopping')
v=copy.deepcopy(r)
for i in (3,53):v['per_environment']['alive'][i]=False
assert not assess_flat(v)['pass_'];contracts.append('retained survival')
for key in ('left_support_slip_control','right_support_slip_control'):
    for mode in ('nonfinite','missing'):
        v=copy.deepcopy(r)
        if mode=='nonfinite':
            for i in (3,53):v['per_environment'][key][i]=float('nan')
        else:del v['per_environment'][key]
        assert not assess_flat(v)['pass_'];contracts.append('retained '+key+' '+mode)
v=copy.deepcopy(r)
for i in (3,53):v['per_environment']['vel_error'][i]=float('nan')
assert not assess_flat(v)['pass_'];contracts.append('retained nonfinite tracking')
for key,value in [('nonfinite',True),('physics_pass',False),('seconds',14.99),('max_closure_after_grace_m',.0021),('max_mimic_after_grace_rad',.0101)]:
    v=copy.deepcopy(r);v[key]=value;assert not assess_flat(v)['pass_'];contracts.append('retained '+key)
v=copy.deepcopy(r);v['per_environment']['max_tilt'][3]=15.1
assert not safety_veto(v);contracts.append('retained individual severe veto despite 7/8 group')
v=copy.deepcopy(r)
for i in (3,53):v['per_environment']['left_support_slip_control'][i]=3.
assert assess_flat(v)['pass_'] and assess_flat(v)['prior_original_flat_admission']['eligible_for_mild_dr_trial'] is False
contracts.append('finite slip values diagnostic regardless of uncalibrated magnitude')
reclassified=[]
for seed in (20261002,20261003):
    for kind in ('flat','spin'):
        reports=[read(f'auto_0067_scut_style_latest6_multiseed_cap6_white_v2_{kind}_{profile}_{seed}.json') for profile in ('nominal','white_v2')]
        assert all(reports[0][k]==reports[1][k] for k in ('reset_joint_pos_before_physics','reset_root_before_physics'))
        gs=[assess_flat(v)['pass_'] if kind=='flat' else assess(v)['pass_'] for v in reports]
        assert all(gs) and all(safety_veto(v) for v in reports)
        reclassified.append(dict(seed=seed,kind=kind,initial_root_q_exact=True,versioned_gates=gs))
contracts.append('all eight real 19575 paired reports and severe checks pass prospective v2')
for prefix in ('auto_0066_contact_assessment_cap6_white_v2','auto_0069_contact_assessment_cap6_white_v2'):
    assert assess_flat(read(prefix+'_flat.json'))['pass_'] and assess(read(prefix+'_rate.json'))['pass_']
contracts.append('two different actual formal policies19575/19732 qualify without new replay claims')
out=dict(pass_=True,acceptance_version=VERSION,contract_count=len(contracts),contracts=contracts,
         real19575_paired_reclassification=reclassified,old_reports_changed=False,new_simulation_performed=False,
         prior_slip_failures_preserved=True)
print(json.dumps(out))
