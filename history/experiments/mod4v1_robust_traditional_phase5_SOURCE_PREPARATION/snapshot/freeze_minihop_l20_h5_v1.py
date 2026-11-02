"""Select on completed TRAIN only, freeze independent H5 BEFORE new physics."""
from pathlib import Path
import json,hashlib,copy,math
R=Path(__file__).resolve().parent;D=R/'MINIHOP_L20_H5_V1';D.mkdir(exist_ok=False)
def write(p,x):
    with p.open('x',encoding='utf-8')as f:json.dump(x,f,indent=2,allow_nan=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];scores={}
for label in('l40','l20'):
    rr=[]
    for seed in range(4221,4225):
        p=R/f'results/r47_{label}_DR{seed}/result.json';x=json.loads(p.read_bytes())
        assert x['complete']and x['controls']==600 and x['physics_steps']==12000
        row=dict(candidate=label,seed=seed,pass_original=x['proposed_flat_clear80mm_recover2s_v2'],
                 peak_pitch_rad=x['max_pitch_rad'],end_stable_s=x['end_stable_s'],
                 mesh_clearance_m=x['maximum_main_mesh_clearance_during_full_air_m'],
                 guide_ticks=x['after_trigger_guide_contact_physics_ticks'],hard_ticks=x['after_trigger_hard_contact_physics_ticks'],
                 result_path=str(p),result_SHA=sha(p),trace_producer=x['trace_artifact'],physics_producer=x['physical_artifact'])
        assert row['pass_original']==bool(x['complete']and row['mesh_clearance_m'] is not None and row['mesh_clearance_m']>=.08 and row['guide_ticks']==0 and row['hard_ticks']==0 and row['end_stable_s']>=2.)
        rr.append(row);rows.append(row)
    scores[label]=dict(passes=sum(x['pass_original']for x in rr),worst_pitch_rad=max(x['peak_pitch_rad']for x in rr),minimum_end_stable_s=min(x['end_stable_s']for x in rr))
rank=sorted(scores,key=lambda c:(-scores[c]['passes'],scores[c]['worst_pitch_rad'],-scores[c]['minimum_end_stable_s']))
assert rank[0]=='l20'and scores['l20']['passes']==4
selection=dict(kind='R47_TRAIN_SELECTION_BEFORE_H5_NOT_A_PRETRAIN_RULE',physical_trajectories=8,unique_DR_seeds=4,
        total_physics_steps=96000,rows=rows,score=scores,selected='l20',
        rule='after_TRAIN_before_holdout: highest_original_pass_count_then_lower_worst_peak_pitch_then_longer_min_endstable',
        not_independent_holdout=True,no_old_scores_rewritten=True)
write(R/'reports/R47_LANDING_TRAIN_FACTS.json',selection)
base=json.loads((R/'results/r47_l20_DR4221/config.json').read_bytes());base.pop('case_id',None);base.pop('seed',None)
base['cohort']='frozen_H5_independent_operator_timed_flat_minihop';base['nominal']=False
write(D/'FROZEN_BASE_CONFIG.json',base)
manifest=json.loads((R/'results/r47_l20_DR4221/SOURCE_MANIFEST.json').read_bytes())
sources=[]
for record in manifest['files']:
    p=Path(record['path']);assert p.is_file()and sha(p)==record['SHA'],str(p)
    sources.append(record)
write(D/'CONTROLLER_SOURCE_INDEX.json',dict(files=sources,model_SHA=manifest['model_SHA'],
        model_assets_producer_refs=manifest['model_assets'],raw_assets_rehashed_for_this_freeze=False,
        each_actual_episode_existing_provenance_guard_still_checks_model_assets=True))
protocol=dict(kind='FROZEN_H5_INDEPENDENT_OPERATOR_TIMED_FLAT_MINIHOP',seeds=list(range(62100,62164)),nominal=False,
    controller_profile='l20_capture_position_nominal_K_feedforward_schedule_v3_runtime_loader_v4',
    selection='reports/R47_LANDING_TRAIN_FACTS.json',selected_on_TRAIN_only=True,control_sources='CONTROLLER_SOURCE_INDEX.json',
    source_index_SHA=sha(D/'CONTROLLER_SOURCE_INDEX.json'),base_config_SHA=sha(D/'FROZEN_BASE_CONFIG.json'),
    duration_s=6.,control_dt_s=.01,physics_dt_s=.0005,max_workers=4,all_D0_to_D7_original=True,
    information_path='original_100Hz_boxcar_then_D1_then_D3; no_raw2k_enrichment_used_for_control',
    acceptance='unchanged_v2: complete AND peak_both_main_mesh_clearance_during_operational_fullair>=.08 AND after_trigger_guide_ticks==0 AND after_trigger_hard_ticks==0 AND end_stable_s>=2',
    operational_air='sum_all_positive_environment_normals<=1N_for20ms_not_hardware_contact_certificate',
    endstable='original100Hz bothmainmean>1N/no-guide-hard-bin/pitch-roll<.15/absbodyvx<.35; not2k_continuous_support',
    episode_counts_expected=dict(controls=600,physics_steps=12000),planned_total_physics_steps=768000,
    software_error_rule='stop_remaining_waves_save_actual_prefix_and_unstarted; do_not_count_error_as_robot_fail',
    robot_failure_rule='retain_all_robot_failures_and_continue_planned_seeds_no_retuning_no_replacement',
    frozen_no_tuning=True,confidence='report_exact_count_and_Wilson95_descriptive_DR_scope;64of64_lower_is_about.9434_not95percent_reliability_proof',
    not_qualified=['270mm_step','RM_terrain','moving_jump','automatic_contact_FSM','C_closed_loop_jump','bus_electrical_power','target_board','HIL','WCET','impact_ratings'],
    power_allocator_integrated=False,controller_truth_inputs=False,private_audit_truth_only=True,
    output_raw='producer_streamed_SHA_only_for_later_archive_no_raw_rehash',PH5_pending=True,prior_H1_H2_H4_unchanged=True)
write(D/'PROTOCOL.json',protocol)
print(json.dumps(dict(frozen=True,selected=rank[0],train_scores=scores,seeds=[62100,62163],source_files=len(sources),
      protocol_SHA=sha(D/'PROTOCOL.json'),physics_steps=0,holdout_not_started=True),indent=2))
