"""Audit existing8 paired rate6 reports and the separate physical8 rejection."""
import hashlib,json,sys
from pathlib import Path
D=Path(__file__).resolve().parent;E=D/'completed_outcomes'
sys.path.insert(0,str(D));sys.path.insert(1,str(D.parent/'MOD4_SCUT_STYLE_RATE_CONTINUE_20261004'));sys.path.insert(1,str(D.parent/'MOD4_RATE6_SLIP_REPAIR_20261003'))
from scut_style_gate_v2 import assess,assess_flat,VERSION
try:from autonomy_policy import safety_veto
except ModuleNotFoundError:from autonomy_policy_actual import safety_veto
read=lambda n:json.loads((E/n).read_text())
paired=read('auto_0072_scut_style_v2_latest6_multiseed_cap6_white_v2_paired_decision.json')
assert paired['pass_'] and paired['acceptance_version']==VERSION
rows=[];spin_count=flat_trained=0
for seed in (20261002,20261003):
    for kind in ('flat','spin'):
        names=[f'auto_0072_scut_style_v2_latest6_multiseed_cap6_white_v2_{kind}_{profile}_{seed}.json' for profile in ('nominal','white_v2')]
        reports=[read(n) for n in names]
        assert all(reports[0][k]==reports[1][k] for k in ('reset_joint_pos_before_physics','reset_root_before_physics'))
        for name,r in zip(names,reports):
            verdict=assess_flat(r) if kind=='flat' else assess(r)
            assert verdict['pass_'] and safety_veto(r)
            if kind=='flat':
                trained=[row['env'] for row in verdict['individual']]
                assert len(trained)==64 and all(r['per_environment']['alive'][i] for i in trained)
                flat_trained+=len(trained);worst=None
            else:
                assert all(r['alive']) and len(r['alive'])==88;spin_count+=len(r['alive'])
                pe=r['per_environment'];ids=[i for i,gid in enumerate(r['group_ids']) if r['groups'][gid]['profile']=='spin' and abs(r['groups'][gid]['wz'])==6]
                worst={k:max(pe[k][i] for i in ids) for k in ['peak_tilt','maximum_gap_m','longest_both_low_s','spin_translation_speed','left_slip','right_slip']}
                worst['yaw_by_direction']={str(sign):sum(pe['yaw_rate'][i] for i in ids if r['groups'][r['group_ids'][i]]['wz']==sign)/8 for sign in (6.,-6.)}
            rows.append(dict(name=name,sha256=hashlib.sha256((E/name).read_bytes()).hexdigest(),versioned_pass=True,severe_veto_pass=True,initial_root_q_exact=True,original_flat=verdict['prior_original_flat_admission']['eligible_for_mild_dr_trial'] if kind=='flat' else None,original_mesh=r.get('spin_skill_pass'),legacy=r.get('spin_skill_pass_legacy_reference'),pure6_worst=worst))
six=dict(version=VERSION,checkpoint=paired['checkpoint'],paired_actual_receipt=paired,rows=rows,spin_alive_count=spin_count,flat_trained_alive_count=flat_trained,new_replays_performed_for_review=False)
(D/'MODEL19975_PAIRED6_COMPLETED_REVIEW.json').write_text(json.dumps(six,indent=2),encoding='utf8')
r=read('auto_0074_rolling_rate_short_cap8_white_v2.json');pe=r['per_environment']
assert r['target_rate_rad_s']==8 and not r['physical_smoke_pass'] and not r['ppo_performed'] and r['seconds']==3 and not r['nonfinite']
individual=[]
for i,gid in enumerate(r['group_ids']):
    if gid<7:continue
    g=r['groups'][gid]
    individual.append(dict(env=i,group_id=gid,target=g['wz'],profile=g['profile'],metrics={k:pe[k][i] for k in ['yaw_rate','yaw_error','tilt','peak_tilt','height_error','delta','d2','maximum_gap_m','longest_both_low_s','spin_translation_speed','wheel_rating_clip','leg_rating_clip','peak_wheel_speed_rad_s']}))
eight=dict(checkpoint=r['checkpoint'],seconds=r['seconds'],seed=r['seed'],profile=r['profile'],alive_count=sum(r['alive']),environment_count=len(r['alive']),physical_smoke_pass=False,no_20k_or_PPO_started=True,slip_not_the_rejection_basis=True,nonfinite=False,max_closure_m=r['max_closure_m'],max_mimic_rad=r['max_mimic_rad'],individual_high_rate_samples=individual,reason='Positive8 short physical posture regression, then bounded controller returned to paired6 repair_hold; independent source has not been trained at8.')
(D/'RATE8_SHORT_REJECTION_REVIEW.json').write_text(json.dumps(eight,indent=2),encoding='utf8')
print(json.dumps(dict(paired6=True,spin_alive=spin_count,flat_trained_alive=flat_trained,physical8=False,worst8_peaktilt=max(pe['peak_tilt']),worst8_gap_m=max(pe['maximum_gap_m']),worst8_bothlow_s=max(pe['longest_both_low_s']),samples=individual),ensure_ascii=False))
