"""One parent administrative JSON reconciliation; no physics/raw/asset/imported project execution."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
D=R.parent/'repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase7_SOURCE_PREPARATION'
p=D/'CASE_RECONCILIATION.json';raw=p.read_bytes();v=json.loads(raw)
cases=v['cases'];assert len(cases)==51 and len({z['case']for z in cases})==51
assert all(type(z['controls'])is int and z['controls']>0 and z['physics_steps']==20*z['controls']for z in cases)
assert sum(z['controls']for z in cases)==46200
assert sum(z['physics_steps']for z in cases)==924000
assert all(z['complete']is True and z['stop']=='complete'for z in cases)
expected={54:4,55:8,56:2,57:8,58:2,59:8,60:16,61:3}
summary={}
for n,count in expected.items():
    zs=[z for z in cases if z['round']==n];assert len(zs)==count
    group=v['round_groups_not_poolable'][str(n)]
    actual=dict(n=len(zs),controls=sum(z['controls']for z in zs),physics_steps=sum(z['physics_steps']for z in zs),
        local_pass_n=sum(z['local_firstbar_gate']is True for z in zs),
        mainfirstflight_nonempty_n=sum(z['main_firstflight_rear_crossing_s']is not None for z in zs),
        spin_composite_pass_n=sum(z['spin_composite_gate']is True for z in zs))
    assert all(group[k]==value for k,value in actual.items()),(n,actual,group)
    summary[str(n)]=actual
for n,lp,fp in ((55,6,4),(57,6,7),(59,7,7),(60,10,16)):
    assert summary[str(n)]['local_pass_n']==lp and summary[str(n)]['mainfirstflight_nonempty_n']==fp
fresh=[z for z in cases if z['round']==60]
fails=[z for z in fresh if z['local_firstbar_gate']is False]
assert {z['seed']for z in fails}=={4601,4603,4605,4606,4609,4614}
assert all(z['guide_ticks']>0 for z in fails)
assert [(z['seed'],z['hard_ticks'])for z in fresh if z['hard_ticks']>0]==[(4606,5)]
spin=[z for z in cases if z['round']==61]
assert {z['seed']for z in spin}=={0,201,202}
assert all(z['spin_composite_gate']is False and z['spin_original_screen_gate']is False for z in spin)
assert summary['61']['spin_composite_pass_n']==0
# These are saved reconciliation entries, not re-executed episodes or newly observed raw values.
a=dict(status='PARENT_JSON_RECONCILIATION_PASS_NO_PHYSICS',case_source=str(p),case_source_SHA=hashlib.sha256(raw).hexdigest(),
       physical_saved_result_entries=51,controls=46200,physics_steps=924000,rounds_separate_not_poolable=summary,
       R60_failures=[dict(seed=z['seed'],guide=z['guide_ticks'],hard=z['hard_ticks'])for z in fails],
       R61_seed_composite=[dict(seed=z['seed'],composite=z['spin_composite_gate'],screen=z['spin_original_screen_gate'])for z in spin],
       checks_include_original_result_field_types_and_complete=True,not_new_robot_samples=True,
       old_raw_asset_model_compile_core_QA_or_Git_calls=0,source_prep_immutable=True,
       parent_smallfile_SHA_and_Git_state_check='Separate pwsh output: six review files + original helper SHA, HEAD4e7a3fb, own branch, tracked/stage empty, no PH7 localtag',
       full_gaps_and_qualification_read_by_parent=True)
out=R/'PH7_PARENT_NUMERIC_CHECK.json';assert not out.exists();out.write_text(json.dumps(a,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps(a,ensure_ascii=False,indent=2,allow_nan=False))
