"""Audit valid D4 flat/spin baselines and reject the old world branch as D4 evidence."""
from pathlib import Path
import json,hashlib,time,ast,sys,math,statistics
D=Path(__file__).resolve().parent;R=D/'reports';P=D.parent/'MOD4_D4_FULL_CONTRACT_20261008'
sys.path.insert(0,str(D.parent/'MOD4_S1A_MATCHED_EVALUATION_20261007/review_contracts'))
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
original=D.parent/'MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/review_block1_matched_scope.py'
tree=ast.parse(original.read_text(encoding='utf8'));only=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='facts'],type_ignores=[]);exec(compile(only,str(original),'exec'))
read=lambda p:json.loads(p.read_text(encoding='utf8'))
files=read(P/'reports/D4_EXISTING_BASELINE_FILES.json')
valid={};large=[]
for kind in ('flat','spin','world'):
    job='clk2500-closure-episode-d3-40-d4-anchor-'+kind;folder=P/'reports/windows'/job
    p=read(folder/'probe.json');m=read(folder/'manifest.json');result=read(folder/'result.json')
    assert result['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']=='ded074be755d5320a4050f69753163800a409d6eaf077fb3b990b686d9547a61'
    assert result['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']=='74200ad6e080c0483f8af95307ae385111a99f54e528ec359a29fcc834d93e18'
    assert result['exit_code']==0 and p['steps']==m['steps']==1500 and p['seed']==m['seed']==20261002
    for name in ('probe.json','result.json'):
        index=next(row for row in files['jobs'] if row['id']==job)['files'][name]
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==index['sha256']
        large.append(dict(job=job,name=name,**index))
    f=facts(p,kind)
    if kind=='world':
        assert 'physical_action_delay_audit' not in p and 'physical_action_delay_recipe' not in p
        valid['old_world']=dict(facts=f,only_D3_feedback_scope=True,D4_action_delay_evidence_accepted=False,reason='Frozen standalone world module still imported DelaySensorMod4Env; not ActionDelayMod4Env',original_result_and_flags_unchanged=True)
        continue
    a=p['physical_action_delay_audit'];recipe=p['physical_action_delay_recipe'];initial=p['physical_action_initial_episode_assignments'];final=p['physical_action_final_episode_assignments']
    assert p['D4_closed_loop_actual_physical_target_delay'] and recipe['profile']=='physical_target_0_2500_5000us_v1'
    assert recipe['actual_transition_delay_us']==[0,2500,5000] and a['callback_counts']=={'legs':6000,'wheels':6000} and a['application_formula_max_error']==0
    n=m['num_envs'];assert all(len(initial[g]['delay_us'])==n for g in ('legs','wheels'))
    assert initial==final and all(x in (0,2500,5000) for g in initial.values() for x in g['delay_us'])
    valid[kind]=dict(facts=f,actual_action_delay_recipe=recipe,initial_final_assignments_exact=True,actual_apply_callbacks_per_group=6000,actual_target_formula_error=0)
review=dict(epoch=time.time(),scope='Existing same3060/seed20261002/white_v3/noisebias/0-10msfeedback; true D4 flat-spin only',valid=valid,original_case_source_module_sha256=read(R/'WORLD_DISPATCH_PACKAGE.json')['world_before_sha256'],large_raw_files_index=large,decision=dict(existing_D4_flat_spin_contract_scope_accepted=True,old_world_not_D4_evidence=True,corrected_actual_action_delayed_world_pending=True,no_old_result_overwrite=True,no_duplicate_flat_spin_evaluation=True,production243_unmodified=True,no_new_PPO_or_budget_write=True))
(R/'D4_EXISTING_BASELINE_SCOPE_REVIEW.json').write_text(json.dumps(review,indent=2),encoding='utf8')
print(json.dumps(dict(flat=valid['flat']['facts']['straight'],spin=valid['spin']['facts']['pure4pi'],oldworld=valid['old_world']['facts']['passed'],decision=review['decision'])))
