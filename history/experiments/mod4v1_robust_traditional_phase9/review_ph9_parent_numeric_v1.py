"""Independent parent check: six small saved R63 result snapshots, no replay."""
from pathlib import Path
import hashlib,json,math
R=Path(__file__).resolve().parent;REPO=R.parent/'repo-lqr-robust';S=REPO/'history/experiments/mod4v1_robust_traditional_phase9_SOURCE_PREPARATION'
def load(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
c=load(S/'CASE_RECONCILIATION.json');k=load(S/'FINAL_CONSISTENCY_RECEIPT.json');g=load(S/'FINAL_GAPS_AND_EXCLUSIONS.json')
rows=c['rows'];assert len(rows)==6 and len({x['case']for x in rows})==6
controls=steps=nom=paired=firstflight=0;actual=[]
for row in rows:
    p=S/'snapshot/results'/row['case']/'result.json';x=load(p)
    assert sha(p)==row['result_source_SHA']and x['config']['case_id']==row['case']
    assert x['complete']is True and (x['controls'],x['physics_steps'])==(800,16000)
    assert x['spring_release_enabled']is True and x['nominal_gas_endpoint_data_SHA']=='1b47bb7d75205c907f9116cb658adbb2922e82decee2c9b19c2fab8d86db762e'
    main=bool(x['maximum_main_mesh_clearance_during_full_air_m']>=.08 and x['guide_contact_physics_ticks']==0 and x['hard_contact_physics_ticks']==0 and x['end_stable_s']>=2 and x['max_abs_world_y_m']<=.3 and x['forward_progress_m']>=.5)
    local=bool(x['config']['scene']=='rm'and main and x['conservative_final_robot_all_collision_behind_bar']and x['conservative_front_never_reached_next_bar'])
    assert x['proposed_manual_first_bar_clear_stop_v1']==local
    assert x['proposed_moving_flat_air80_stop_v1']==bool(x['config']['scene']=='flat'and main)
    flag=bool(main if x['config']['scene']=='flat'else local);assert flag==row['original_scene_gate']
    if x['config']['nominal']:nom+=flag
    else:
        paired+=flag;cross=x['first_flight_main_rear_crossing_bar_back_s'];firstflight+=type(cross)in(int,float)and math.isfinite(cross)and cross>=0
    controls+=x['controls'];steps+=x['physics_steps'];actual.append(dict(case=row['case'],gate=flag,guide=x['guide_contact_physics_ticks'],hard=x['hard_contact_physics_ticks']))
assert(controls,steps,nom,paired,firstflight)==(4800,96000,2,1,4)
base=[]
for z in c['baseline_four_saved_Git_small_results']:
    p=REPO/z['archive_path'];old=load(p);assert sha(p)==z['SHA']
    assert old['proposed_manual_first_bar_clear_stop_v1']==z['original_local_gate'];base.append(z['original_local_gate'])
assert len(base)==4 and sum(base)==2
assert k['text_snapshot_SHA_pairs_checked']==1259 and k['before_after_all_equal']is True
assert len(g['current_unique_missing_saved_smalltext'])==1 and len(g['current_raw_unknowns'])==2
assert g['inherited_prior_two_unique_real_saved_text_gaps']['both_historical_FSM_and_prechange_R62_fixture_remain_unreconstructed']is True
fixture=load(S/'snapshot/PARENT_R63_BINDING_PREFLIGHT_V1/RESULT.json')
f=[x for x in fixture['fixtures']if x['fixture']=='metadata_4'];assert len(f)==1 and f[0]['expected_accept']is False and f[0]['actual_accept']is False
bad=load(S/'snapshot/PARENT_R63_BINDING_PREFLIGHT_V1/metadata_4/results/case/SOURCE_MANIFEST.json');assert bad['files'][0]['SHA']=='0'*64
files=[S/n for n in('REVIEW_HANDOFF.md','REVIEW_INDEX.json','CASE_RECONCILIATION.json','FINAL_GAPS_AND_EXCLUSIONS.json','QUALIFICATION_BOUNDARIES.json','FINAL_CONSISTENCY_RECEIPT.json')]
out=dict(status='PASS_PARENT_R63_SIX_SMALL_RESULT_GATE_AND_SENTINEL_RECONCILIATION',actual_cases=actual,physical_cases=6,actual_controls=controls,actual_physics_steps=steps,nominal_pass=nom,selected_TRAIN_pass=paired,old_same_four_pass=sum(base),main_rear_firstflight_paired=firstflight,
    current_saved_text_gap_unique=1,inherited_prior_saved_text_gaps_unique=2,overlap_not_summed=True,current_conflicting_binary_unknowns=2,deliberate_zero_SHA_negative_fixture_not_missing_source=True,
    review_files=[dict(path=str(p),SHA=sha(p))for p in files],parent_snapshot_full_rehash_not_claimed=True,new_physics_models_FK_QA_or_raw_asset_reads=0,Git_authorized_by_this_check=False)
with(R/'PH9_PARENT_NUMERIC_CHECK.json').open('x',encoding='utf-8')as f:json.dump(out,f,indent=2,allow_nan=False)
print(json.dumps(out,indent=2))
