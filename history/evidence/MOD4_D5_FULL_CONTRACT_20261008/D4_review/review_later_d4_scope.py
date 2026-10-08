"""Compare actually complete D4 later blocks with exact baseline/first-block evidence."""
from pathlib import Path
import runpy,json,time
D=Path(__file__).resolve().parent;R=D/'reports';read=lambda p:json.loads(p.read_text(encoding='utf8'))
ctx=runpy.run_path(str(D/'review_true_d4_scope.py'))
later=read(R/'LATER_D4_SCOPE_FILES.json');ctx['case'].__globals__['jobs'].update({r['id']:r for r in later['jobs']})
actual=read(D.parent/'MOD4_D4_FULL_CONTRACT_20261008/reports/D4_BLOCKS_ACTUAL_VERIFIED.json')
out={}
for b in (2,3):
    own=actual['complete_blocks'].get(str(b))
    if not own:continue
    sha=own['checkpoint']['sha256'];cases={k:ctx['case'](f'55-d4world-b{b}' if k=='world' else f'50-d4-b{b}',k,sha) for k in ('flat','spin','world')}
    if not all(cases.values()):continue
    pairs=[]
    for k,c in cases.items():
        bp=ctx['baseline'][k]['probe'];cp=c['probe']
        p=dict(kind=k,root_exact=bp['reset_root_before_physics']==cp['reset_root_before_physics'],q_exact=bp['reset_joint_pos_before_physics']==cp['reset_joint_pos_before_physics'],
            initial_parameters_exact=ctx['params'](bp)==ctx['params'](cp),runtime_exact=ctx['baseline'][k]['manifest']['artifacts']['runtime']==c['manifest']['artifacts']['runtime'],
            sensor_recipe_exact=bp['sensor_recipe']==cp['sensor_recipe'],feedback_recipe_exact=bp['feedback_delay_recipe']==cp['feedback_delay_recipe'],
            action_recipe_exact=bp['physical_action_delay_recipe']==cp['physical_action_delay_recipe'],action_assignment_exact=bp['physical_action_initial_episode_assignments']==cp['physical_action_initial_episode_assignments'],
            feedback_age_exact=bp['sensor_actual_manager_audit']['actual_feedback_sample_apply']==cp['sensor_actual_manager_audit']['actual_feedback_sample_apply'])
        assert all(v for n,v in p.items() if n!='kind'),p
        pairs.append(p)
    out[str(b)]=dict(checkpoint=own['checkpoint'],health=own['health'],actual_updates=own['actual_updates'],actual_steps=own['actual_environment_steps'],
        unique_completed_segment=own['unique_completed_segment'],cases=ctx['compact'](cases),pairs=pairs)
v=dict(epoch=time.time(),scope=ctx['v']['scope'],baseline=ctx['compact'](ctx['baseline']),first_block=ctx['compact'](ctx['candidate']),later_blocks=out,
    returned_JSON_files=later,no_GPU_PPO_or_budget_writes=True,all_raw_flags_preserved=True,dualseed_allprofile_graduation=False)
(R/'D4_LATER_BLOCKS_MATCHED_REVIEW.json').write_text(json.dumps(v,indent=2),encoding='utf8')
print(json.dumps({b:{k:c['facts'] for k,c in r['cases'].items()} for b,r in out.items()}))
