"""Actual prior-report and safety-boundary contracts for the gate-only change."""
import argparse,copy,hashlib,json,math,sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--code',required=True);p.add_argument('--reports',required=True);a=p.parse_args()
    sys.path.insert(0,a.code)
    from scut_style_gate_v2 import assess as old,assess_flat as oldflat
    from scut_style_gate_v3 import assess,assess_flat,VERSION
    folder=Path(a.reports);checks=[];policy=[]
    def check(name,passed):
        assert passed,name
        checks.append(name)
    for n in (82,85):
        stem=f'auto_{n:04d}_scut_style_v2_assessment_cap7_white_v2'
        r=json.loads((folder/(stem+'_rate.json')).read_text());original=copy.deepcopy(r)
        v2=old(r);v3=assess(r)
        check(f'{n}: inherited original v2 still fails',not v2['pass_'])
        check(f'{n}: new finite-mean-speed diagnosis passes',v3['pass_'])
        check(f'{n}: original report unchanged',r==original)
        check(f'{n}: prior verdict retained',v3['prior_v2_assessment']==v2)
        check(f'{n}: only intended reason removed',all(set(before['reasons'])-set(after['reasons'])<= {'spin_translation_speed'} for before,after in zip(v2['individual'],v3['individual'])))
        check(f'{n}: all actual groups retained',len(v3['groups'])==11 and all(g['passing']==8 for g in v3['groups']))
        f=json.loads((folder/(stem+'_flat.json')).read_text())
        check(f'{n}: flat semantics exact',assess_flat(f)['prior_v2_flat_assessment']==oldflat(f))
        policy.append(dict(checkpoint=r['checkpoint'],report=stem,report_sha256=hashlib.sha256((folder/(stem+'_rate.json')).read_bytes()).hexdigest(),prior_v2_pass=False,new_v3_pass=True,reclassification_not_new_replay=True))
    r=json.loads((folder/'auto_0085_scut_style_v2_assessment_cap7_white_v2_rate.json').read_text())
    ids=[i for i,g in enumerate(r['group_ids']) if g==7]
    for key,value in [('peak_tilt',13.),('maximum_gap_m',.003),('longest_both_low_s',.016),('left_fz',9.),('yaw_error',2.),('speed_error',.13),('height_error',.04),('delta',.19),('d2',.26),('base_force',2.),('wheel_rating_clip',.21)]:
        x=copy.deepcopy(r)
        for i in ids:x['per_environment'][key][i]=value
        check('retained '+key,not assess(x)['pass_'])
    for value in (float('nan'),float('inf')):
        x=copy.deepcopy(r);x['per_environment']['spin_translation_speed'][ids[0]]=value
        check('nonfinite horizontal evidence '+str(value),not assess(x)['pass_'])
    x=copy.deepcopy(r);del x['per_environment']['spin_translation_speed']
    check('missing mean-speed evidence',not assess(x)['pass_'])
    x=copy.deepcopy(r);x['substep_contact_readback']['callbacks']-=1
    check('missing callback',not assess(x)['pass_'])
    x=copy.deepcopy(r);x['max_closure_m']=.003
    check('closure failure',not assess(x)['pass_'])
    x=copy.deepcopy(r);x['max_mimic_rad']=.011
    check('mimic failure',not assess(x)['pass_'])
    x=copy.deepcopy(r);x['alive'][ids[0]]=False;x['first_failure_step'][ids[0]]=10
    check('single severe survival veto',not assess(x)['pass_'])
    x=copy.deepcopy(r);x['initial_parameter_audit']['actual_parameters_pass']=False
    check('parameter audit failure',not assess(x)['pass_'])
    x=copy.deepcopy(r);x['substep_contact_readback']['per_environment']['loaded_samples'][ids[0]][0]=0
    check('missing bearing evidence',not assess(x)['pass_'])
    x=copy.deepcopy(r)
    for i in ids[:2]:x['per_environment']['yaw_error'][i]=2.
    check('80percent group threshold preserved',not assess(x)['pass_'])
    check('different formal policies retained',policy[0]['checkpoint']!=policy[1]['checkpoint'])
    print(json.dumps(dict(pass_=True,contract_count=len(checks),checks=checks,acceptance_version=VERSION,existing_policy_review=policy),ensure_ascii=False))

if __name__=='__main__':main()
