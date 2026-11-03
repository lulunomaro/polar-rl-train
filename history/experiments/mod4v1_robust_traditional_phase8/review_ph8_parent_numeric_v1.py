"""Parent numeric review of saved PH8 metadata and six small snapshots only."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;REPO=R.parent/'repo-lqr-robust';S=REPO/'history/experiments/mod4v1_robust_traditional_phase8_SOURCE_PREPARATION'
def load(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
c=load(S/'CASE_RECONCILIATION.json');k=load(S/'FINAL_CONSISTENCY_RECEIPT.json');g=load(S/'FINAL_GAPS_AND_EXCLUSIONS.json')
rows=c['actual_cases'];assert len(rows)==6 and len({x['case']for x in rows})==6
controls=steps=0;nom=paired=0;actual=[]
for row in rows:
    p=S/'snapshot/results'/row['case']/'result.json';x=load(p)
    assert sha(p)==row['result_source_SHA']and x['config']['case_id']==row['case']
    assert x['complete']is True and x['controls']==800 and x['physics_steps']==20*x['controls']==16000
    main=bool(x['maximum_main_mesh_clearance_during_full_air_m']>=.08 and x['guide_contact_physics_ticks']==0 and x['hard_contact_physics_ticks']==0 and x['end_stable_s']>=2 and x['max_abs_world_y_m']<=.3 and x['forward_progress_m']>=.5)
    local=bool(x['config']['scene']=='rm'and main and x['conservative_final_robot_all_collision_behind_bar']and x['conservative_front_never_reached_next_bar'])
    assert x['proposed_manual_first_bar_clear_stop_v1']==local
    flag=bool(main if x['config']['scene']=='flat'else local)
    assert flag==row['original_scene_gate']
    if x['config']['nominal']:nom+=flag
    else:paired+=flag
    controls+=x['controls'];steps+=x['physics_steps'];actual.append(dict(case=row['case'],gate=flag))
assert (controls,steps,nom,paired)==(4800,96000,2,1)
baselines=[]
for z in c['existing_baseline_Git_references']:
    p=REPO/z['existing_Git_path'];old=load(p);assert sha(p)==z['SHA']
    assert old['proposed_manual_first_bar_clear_stop_v1']==z['original_local_gate'];baselines.append(z['original_local_gate'])
assert len(baselines)==4 and sum(baselines)==2
assert k['summary']['text_SHA_pairs_verified']==1360 and k['source_before_after_all_equal']is True
assert g['unique_missing_smalltext_version_count']==2 and g['binary_distinct_artifacts']==2 and len(g['current_raw_unknowns'])==2
files=[S/n for n in('REVIEW_HANDOFF.md','REVIEW_INDEX.json','CASE_RECONCILIATION.json','FINAL_GAPS_AND_EXCLUSIONS.json','QUALIFICATION_BOUNDARIES.json','FINAL_CONSISTENCY_RECEIPT.json')]
out=dict(status='PASS_PARENT_SIX_SAVED_SMALL_RESULTS_AND_GAPS_RECONCILIATION',physical_cases=6,actual_controls=controls,actual_physics_steps=steps,
    nominal_pass=nom,selected_TRAIN_pass=paired,same_four_old_baseline_pass=sum(baselines),actual=actual,
    unique_smalltext_saved_version_gaps=2,conflicting_binary_current_unknowns=2,review_files=[dict(path=str(p),SHA=sha(p))for p in files],
    source_snapshot_SHA_verification_is_child_saved_receipt_not_parent_rehash_all=True,
    new_physics_or_models_or_core_QA_or_raw_assets_read=0,Git_write_authorized_by_this_check=False)
with(R/'PH8_PARENT_NUMERIC_CHECK.json').open('x',encoding='utf-8')as f:json.dump(out,f,indent=2,allow_nan=False)
print(json.dumps(out,indent=2))
