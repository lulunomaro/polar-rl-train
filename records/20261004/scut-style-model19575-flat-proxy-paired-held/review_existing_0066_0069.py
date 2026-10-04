"""Audit completed real reports with the actual version; no simulation or mutation."""
import json,hashlib,sys,math
from pathlib import Path
D=Path(__file__).resolve().parent
E=D/'existing_assessments_0066_0069'
sys.path.insert(0,str(D));from scut_style_gate import assess as spin_assess
sys.path.insert(0,str(D.parent/'MOD4_RATE6_SLIP_REPAIR_20261003'))
from admission_gate import assess as flat_assess
from autonomy_policy_actual import safety_veto
def read(n):return json.loads((E/n).read_text())
def sha(n):return hashlib.sha256((E/n).read_bytes()).hexdigest()
def flat_review(n):
    r=read(n);p=r['per_environment'];a=flat_assess(r);fail=[]
    trained=[i for i,gid in enumerate(p['group_ids']) if abs(r['groups'][gid]['command_vx'])<=1.5]
    for i in trained:
        gid=p['group_ids'][i];g=r['groups'][gid];cmd=g['command_vx']
        limits={'vel_error':max(.12,.25*abs(cmd)),'tilt':8,'max_tilt':12,'height_error':.03,
                'delta':.18,'d2':.25,'guide_force':1,'base_force':1,
                'longest_both_low_force_s_substep':.01501,'left_gap_max_control_m':.002,
                'right_gap_max_control_m':.002,'left_support_slip_control':.15,'right_support_slip_control':.15}
        if g['profile']=='ramp_brake_reverse':limits['stop_abs_speed']=.12
        reasons={k:dict(value=p[k][i],limit=v) for k,v in limits.items() if p[k][i]>v}
        if not p['alive'][i]:reasons['alive']=False
        for k in ('left_mean_fz_substep','right_mean_fz_substep'):
            if p[k][i]<10:reasons[k]=dict(value=p[k][i],minimum=10)
        if reasons:fail.append(dict(env=i,group_id=gid,command_vx=cmd,profile=g['profile'],reasons=reasons,
                                    peak_tilt_deg=p['max_tilt'][i],bothlow_s=p['longest_both_low_force_s_substep'][i]))
    return dict(file=n,sha256=sha(n),checkpoint=r['checkpoint'],seed=r['seed'],seconds=r['seconds'],
                admission=a,severe_pass=safety_veto(r),trained_count=len(trained),
                trained_alive=sum(bool(p['alive'][i]) for i in trained),failed_samples=fail,
                strict_pass_window=r['strict_pass_window'],old_flat_slip_gate_retained=True)
def spin_review(n):
    r=read(n);a=spin_assess(r);p=r['per_environment'];cp=r['substep_contact_readback']['per_environment'];rows=[]
    for g in r['groups']:
        ids=[i for i,gid in enumerate(r['group_ids']) if gid==g['group_id']]
        pure=g['profile']=='spin' and abs(g['wz'])==6
        row=dict(group_id=g['group_id'],vx=g['vx'],wz=g['wz'],profile=g['profile'],
                 alive=sum(r['alive'][i] for i in ids),count=len(ids),
                 versioned_passing=sum(v['pass_'] for v in a['individual'] if v['env'] in ids),
                 mean_yaw=sum(p['yaw_rate'][i] for i in ids)/len(ids),
                 peak_tilt_deg=max(p['peak_tilt'][i] for i in ids),
                 max_environment_mean_xy_speed=max(p['spin_translation_speed'][i] for i in ids))
        if pure:
            row.update(max_gap_m=max(p['maximum_gap_m'][i] for i in ids),bothlow_s=max(p['longest_both_low_s'][i] for i in ids),
                       per_environment_slip={str(i):dict(left_mesh=p['left_slip'][i],right_mesh=p['right_slip'][i],
                           loaded_time_mean=cp['loaded_time_mean_tangent_speed'][i],
                           loaded_impulse_mean=cp['loaded_impulse_weighted_tangent_speed'][i],
                           longest_loaded_over015_s=cp['longest_loaded_over015_s'][i]) for i in ids})
        rows.append(row)
    return dict(file=n,sha256=sha(n),checkpoint=r['checkpoint'],seed=r['seed'],profile=r['profile'],
                seconds=r['seconds'],alive=sum(r['alive']),count=len(r['alive']),nonfinite=r['nonfinite'],
                version=a['version'],versioned_pass=a['pass_'],original_mesh_pass=r['spin_skill_pass'],
                legacy_pass=r['spin_skill_pass_legacy_reference'],prior_loaded015_pass=a['prior_loaded015_assessment']['pass_'],
                complete_evidence=a['complete_evidence'],parameter_readbacks=a['actual_parameters_pass'],
                severe_individual_veto=a['severe_individual_veto'],groups=rows,
                closure_m=r['max_closure_m'],mimic_rad=r['max_mimic_rad'])
pairname='auto_0067_scut_style_latest6_multiseed_cap6_white_v2_paired_decision.json'
pair=read(pairname);checks=[];flat=[];spin=[]
for seed in (20261002,20261003):
    for kind in ('flat','spin'):
        ns=[f'auto_0067_scut_style_latest6_multiseed_cap6_white_v2_{kind}_{profile}_{seed}.json' for profile in ('nominal','white_v2')]
        rs=[read(n) for n in ns]
        exact=all(rs[0][k]==rs[1][k] for k in ('reset_joint_pos_before_physics','reset_root_before_physics'))
        assert exact
        reviews=[flat_review(n) if kind=='flat' else spin_review(n) for n in ns]
        (flat if kind=='flat' else spin).extend(reviews)
        results=[(v['admission']['eligible_for_mild_dr_trial'] and v['severe_pass']) if kind=='flat' else v['versioned_pass'] for v in reviews]
        recorded=next(v for v in pair['pairs'] if v['seed']==seed and v['kind']==kind)
        assert results==recorded['versioned_gates'] and all(recorded['actual_parameter_readbacks'])
        checks.append(dict(seed=seed,kind=kind,initial_root_q_exact=exact,versioned_gates=results))
assert pair['pass_'] is False
assert all(v['versioned_pass'] for v in spin)
assert len([v for v in flat if not v['admission']['eligible_for_mild_dr_trial']])==1
first=spin_review('auto_0066_contact_assessment_cap6_white_v2_rate.json')
second=spin_review('auto_0069_contact_assessment_cap6_white_v2_rate.json')
assert first['versioned_pass'] and second['versioned_pass']
rs=[read(v['file']) for v in (first,second)]
assert all(rs[0][k]==rs[1][k] for k in ('reset_joint_pos_before_physics','reset_root_before_physics','probe_sha256','seed','steps','seconds','profile'))
secondflat=flat_review('auto_0069_contact_assessment_cap6_white_v2_flat.json')
assert secondflat['admission']['eligible_for_mild_dr_trial'] and secondflat['severe_pass']
health=json.loads((D/'HEALTH_HEARTBEAT_20261004_1922.json').read_text())
assert health['SCUT_STYLE_STATE']['consecutive']==1 and health['SCUT_STYLE_STATE']['failed_blocks']==0
assert health['own_checkpoint']['finite_tensors']==68 and health['run_manifest']['start_iteration']==19732
review=dict(version='scut_style_nonslip_gate_v1',read_only=True,
            source_index=read('SOURCE_INDEX.json'),mature_rate6_accepted=False,eight_started=False,
            current_actual_parent=health['parent'],current_actual_guardian=health['guardian'],
            current_actual_trainer=health['processes']['training'],own_checkpoint=health['own_checkpoint'],
            current_progress=dict(consecutive=1,failed_blocks=0,cap=6,profile='white_v2'),
            remaining_at_snapshot=health['budget']['remaining_training_seconds'],
            latest19575_single_assessment=first,latest19575_pair_result=pair,
            independently_verified_pair_rows=checks,latest19575_pair_flat=flat,latest19575_pair_spin=spin,
            model19732_single_assessment=second,model19732_flat=secondflat,
            initial_root_q_same19575_19732=True,probe_seed_protocol_same=True,
            interpretation='Latest19575 spin passed all four pairs; only original 1m/s white_v2 flat slip proxy failed 6/8. Other criteria passed. Original flat gate is retained as authorized. 19732 single-protocol flat/spin passed; after failed pairs it is the first consecutive new-policy pass. No physical/dynamics cause or slip elimination is inferred.')
(D/'SCUT_STYLE_19575_PAIR_AND_19732_REVIEW.json').write_text(json.dumps(review,indent=2),encoding='utf8')
print(json.dumps(dict(pair_pass=False,failed_flat=[v for v in flat if not v['admission']['eligible_for_mild_dr_trial']],
                     model19732_pure_groups=[{k:v for k,v in g.items() if k!='per_environment_slip'} for g in second['groups'] if g['profile']=='spin' and abs(g['wz'])==6],
                     closure_m=second['closure_m'],mimic_rad=second['mimic_rad'],original_mesh=second['original_mesh_pass'],legacy=second['legacy_pass'],prior_loaded015=second['prior_loaded015_pass'])))
