"""Bounded SOURCE/TEXT evidence inventory only. Never import or execute audited code.
All output is NEW in this file's directory. No recursive scan or model access.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json

OUT = Path(__file__).resolve().parent
R = OUT.parent
T = R.parent / 'mod4v1_experts_fulldr_rm70_20261101'
REF = T / 'acceptance_contract_sourceonly_v1' / 'original_reference_text'
E0 = R / 'discovery/reward_command_audit_v1/E0/runtime/isaac/mod4'
S50 = R / 'discovery/reward_command_audit_v1/SLOPE_INDEPENDENT50/runtime/isaac/mod4'
# Each tuple is an explicit source path, observed line interval, and routing purpose.
INPUTS = {
 'current_contract': (R/'source_acceptance_review/EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json',105,156,'E0 null predicate/denominator; S50 separate at527:582'),
 'current_contract_md': (R/'source_acceptance_review/EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.md',23,47,'Existing bounded null contract; not overwritten'),
 'measurement_gaps': (R/'source_measurement_review_v1/SOURCE_EVIDENCE_AND_GAPS_V1.json',57,70,'Physical/getter gaps are not acceptance authority'),
 'posttrain_final': (T/'MOD4V1_EIGHT_EXPERTS_POSTTRAIN_FINAL_V1.md',51,66,'Selection and descriptive events are not graduation'),
 'normalization_decisions': (T/'NORMALIZATION_ACCEPTANCE_AND_DECISIONS.md',23,29,'Preserved generic world-cycle tolerances; no all-profile Boolean'),
 'parent_scope': (T/'acceptance_contract_sourceonly_v1/PARENT_SCOPE_STATEMENTS_V1.json',8,10,'Protocol pass is not full-skill pass'),
 'e0_saved_review': (REF/'E0_REVIEW_MD__HANDOFF_FROZEN_E0V2_FULL1000_SAVED_TEXT_REVIEW.md',22,35,'Explicit missing numerical per-command skill tolerances'),
 'e0_catalog': (REF/'E0_CATALOG__e0_original_profile_catalog_v1.py',1,20,'Ten diagnostic profile labels and transition phase classifier'),
 'e0_metrics': (REF/'E0_METRICS__e0_long_command_domain_telemetry_v1.py',41,93,'Same-command signed-window sampling and diagnostic MAE; finish199:206'),
 'e0_saved_metadata': (REF/'E0_SAVED20S__E0_V2_FULL1000_EARLY_COMMAND_INSTANCE_SAVED_TEXT_ACCEPTANCE_REVIEW_ACTUAL.json',2854,2858,'Published text-review explicit missing thresholds; not event raw'),
 'formals189': (REF/'FORMALS189__EXPERT189_SAVED_FORMALS_AND_SKILL_GAPS_ACTUAL.json',125,145,'Preserved world criteria; unjoined C-only plan reference not opened'),
 's50_saved_final': (REF/'SLOPE50_FINAL__FIRST_CURB_SLOPE_FINAL_MODELS_AND_EXACT_DISTINCT_INTERVAL_COST_CPU_ACTUAL.json',29,45,'Learning/fullsave facts; explicit no inferred frozen skill pass at78'),
 'curb_freeze_workorder': (REF/'CURB_FREEZE__NEXT_CURB113_FROZEN_CLOSED_THREE_BLOCKS_FINAL_NEW_STEP_HOP_REVIEW_NO_AUTO_PPO_ACTUAL_WORK_ORDER.json',7,10,'Selection/frozen work order, not S50 grader'),
 'slope_legacy_join': (T/'legacy_source_joins/E1_SLOPE5_SOURCE_JOIN_v1.json',614,663,'Later S50 own scope is not S135 or earlier24b accepted substitute'),
 'slope_coverage_plan': (T/'legacy_source_joins/coverage_plans/CURB_SLOPE_50HZ400N_SOURCE_COVERAGE_PLAN_v1.json',200,229,'Plan-only status, no S50 accepted cohort'),
 'role_contracts': (T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/ROLE_CONTRACTS.json',998,1011,'S50 explicitly descriptive, accepted cohort gap'),
 'e1_worker': (T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/e1_parallel_worker_safe.py',23,42,'S50 own training-axis factory, descriptive branch103:105'),
 's50_cpu_published': (T/'E1_three_variants_CPU_actual_v1/SLOPE_INDEPENDENT50_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json',247,272,'Published task_contract payload; no checkpoint access'),
 's50_original_task': (T/'staged_sources/E1_SLOPE_INDEPENDENT50_40050_MOD4V1_SOURCE_V2/original_exact/TASK.json',1,17,'Original deployment/learning task verbatim payload'),
 's50_original_producer': (T/'staged_sources/E1_SLOPE_INDEPENDENT50_40050_MOD4V1_SOURCE_V2/original_exact/producer/expert_independent_worker_v1.py',35,37,'Writes independent_expert_task_contract = task; not a grader'),
 'pair1_assessor': (T/'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/assess_pair1_retention_closed_metadata_v1.py',26,35,'E0 diagnostic Pareto selection, not new skill pass'),
 'pair4_assessor': (T/'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_assess_pair4_v4/assess_pair4_retention_closed_metadata_v4.py',101,114,'S50 missing accepted rule, frozen mother retained'),
 'e0_manifest': (R/'discovery/reward_command_audit_v1/E0/original_run_manifest.json',6,105,'Actual recorded E0 env and role source provenance'),
 'e0_entry': (E0/'train_mod4v1_e0.py',131,147,'Actual E0 task build path; no old probe gate call'),
 'scut_gate_v3': (E0/'scut_style_gate_v3.py',35,52,'Real narrower project qualification Boolean exists, not exact E0 task port'),
 'scut_gate_v2': (E0/'scut_style_gate_v2.py',14,60,'Old flat probe groups and >=.8 physical admission, not E0 original command cohort'),
 'scut_curriculum_v4': (E0/'scut_curriculum_gate_v4.py',129,138,'Signed fixed-rate component confirmation >=80% each direction, not all E0 profiles'),
 'world_cycle_metric': (E0/'world_cycle_metrics.py',10,47,'Measured prefix/cycle metrics only, no speed graduation'),
 'world_spin_probe': (E0/'world_spin_probe.py',196,228,'World progress separate from learning admission; old Booleans diagnostic'),
 's50_metadata': (R/'discovery/reward_command_audit_v1/SLOPE_INDEPENDENT50/E1_CANONICAL_SOURCE_METADATA.json',113,117,'Full-ramp scope and root key names, not binary acceptance'),
 's50_entry': (S50/'train_independent_owned_axis_v1.py',80,83,'Own configure_slope entry import'),
 's50_extra_runtime': (S50/'variant_extra_state_runtime_v2.py',43,55,'Contract kind validation/preservation, not success'),
 's50_axis': (S50/'independent_expert_axis_v1.py',16,27,'Family4 tile boundary timeout, not route completion'),
}

def fresh_json(name, value):
    p = OUT/name
    with p.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False)
        f.write('\n')

def inventory():
    rows=[]; decoded={}
    allowed_r=(R/'source_acceptance_review',R/'source_measurement_review_v1',R/'discovery/reward_command_audit_v1')
    for key,(path,start,end,purpose) in INPUTS.items():
        path=path.resolve()
        assert path.suffix.lower() in ('.md','.json','.py')
        assert path.is_relative_to(T) or any(path.is_relative_to(root) for root in allowed_r)
        assert not any(part.lower().endswith(('.pt','.npz','.jsonl')) for part in path.parts)
        blob=path.read_bytes() # ONLY explicit allowlisted text sources; never model stat/hash/open.
        assert 0<len(blob)<=512*1024, (key,'bounded text-size limit')
        text=blob.decode('utf-8-sig');lines=text.splitlines()
        assert 1<=start<=end<=len(lines), (key,start,end,len(lines))
        rows.append(dict(id=key,path=str(path),bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest(),
                         line_count=len(lines),evidence_lines=f'{start}-{end}',purpose=purpose))
        decoded[key]=json.loads(text) if path.suffix.lower()=='.json' else text
    return rows,decoded

def main():
    rows,data=inventory()
    contract=data['current_contract']['experts']
    for role in ('E0','SLOPE_INDEPENDENT50'):
        assert contract[role]['original_atomic_predicate'] is None
    task=data['s50_original_task']
    published=data['s50_cpu_published']['known_variant_extra_schema']['task_contract']
    assert task==published, 'Original TASK versus published task_contract differs; do not silently reconcile'
    findings={
      'kind':'ORIGINAL_ACCEPTANCE_GAP_BOUNDED_SOURCE_REVIEW_V2_NOT_RUNTIME',
      'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
      'status':'NO_JOINED_ORIGINAL_FULLROLE_BINARY_AUTHORITY_IN_EXAMINED_SET',
      'roles':{
       'E0':{
        'original_atomic_predicate':None,'original_binary_denominator':None,
        'original_fullrole_standing_group_predicate':None,'binary_skill_rate':None,
        'diagnostic_profiles':contract['E0']['necessary_groups'],
        'sampling_is_not_acceptance':'12918 sampled signed2pi windows are not passed full commands; population_controls is MAE exposure, not binary denominator.',
        'authoritative_negative_evidence':['e0_saved_review','e0_metrics','e0_saved_metadata','formals189'],
        'narrow_numeric_rules_located':[
          {'source':'formals189','lines':'125-130','rule':'along/cross max(0.03,0.1V), signed yaw0.2, complete same-command signed cycles','gap':'No joined all-profile atomic/graduation/standing/transition cohort rule'},
          {'source':'scut_gate_v3','lines':'35-47','rule':'Inherited probe qualification with every existing group fraction>=0.8 and physical/evidence checks','gap':'Explicit SCUT-inspired project qualification, not exact task port; original E0 natural domain not mapped'},
          {'source':'scut_curriculum_v4','lines':'129-138','rule':'Two fixed signed-rate spin rows; within abs yaw error0.2 for >=80% each direction, plus assess physical pass','gap':'Fixed spin target confirmation only; no E0 moving-world/standing/transition full12s acceptance'},
        ],
        'cannot_promote_to_role_acceptance':['MAE improvement','zero ordinary failure','completed sampling window','old probe eligibility or numeric .8','outer requested90 target'],
       },
       'SLOPE_INDEPENDENT50':{
        'original_atomic_predicate':None,'original_binary_denominator':None,
        'original_accepted_cohort':None,'original_standing_group_predicate':None,'binary_skill_rate':None,
        'task_contract_is_original_TASK_equal_published_CPU_text':True,
        'task_contract_key_names':list(task),
        'task_contract_axis':task['axis'],
        'task_contract_join':'original producer stores the unmodified learning/deployment TASK dict; contains no acceptance Boolean or cohort.',
        'authoritative_negative_evidence':['role_contracts','s50_cpu_published','s50_original_task','s50_original_producer','s50_extra_runtime','pair4_assessor'],
        'source_rules_not_acceptance':['Full 5deg/2m ramp and both supports scope','target family4 own axis','abs(dx)>3.5 or abs(dy)>3 boundary timeout','20s natural command/DR/RNG','full-save/50-update learning facts'],
        'forbidden_substitutions':['SLOPE135 endpoint1.2 or27/27','no-fall','MAE','boundary or timeout counts','success/(80-boundaries)','whole route exposure text as Boolean'],
       },
      },
      'minimum_missing_original_authority':[
       'Original own role/profile/geometry/reference-frame scope and dated authoritative source or its exact frozen grader',
       'Atomic accepted predicate, original tolerances, stage/ordered-contact and original standing versus moving treatment',
       'Accepted sampling unit and complete denominator, including failure/incomplete/reset/censor and decision timing',
      ],
      'coverage':{
       'explicit_source_files_hashed':len(rows),'only_text_md_json_py':True,
       'scope_roots':[str(T),str(R/'source_acceptance_review'),str(R/'source_measurement_review_v1'),str(R/'discovery/reward_command_audit_v1')],
       'name_only_discovery':[{
         'scope':str(T),'pattern':'**/*{ACCEPT,accept,CONTRACT,contract,GRADER,grader}*.{py,md,json}',
         'observed_filename_matches':402,'all_matches_content_read':False,'note':'Initial result truncated at100; irrelevant H1 names not followed; no outside output-spill file opened.'},
         {'scope':str(T),'pattern':'**/*{MASTER_PLAN,master_plan,skill_grader,SKILL_GRADER,grader,GRADER}*.{md,json,py}','observed_filename_matches':0,'proof_of_global_absence':False},
         {'scope':str(T/'skill_contracts'),'observation':'Listed E3-only contracts; no E0/S50 candidate there'},
         {'scope':str(T/'source_views'),'observation':'Listed8 redacted transport/launcher source views only; not used as grader authority'},
       ],
       'content_searches':[
        {'scope':'Explicit saved E0 reviews and source','queries':'accept|grad|pass|threshold|tolerance|command|denominator','followup':'E0 source sampling/finish code and numeric probe gate scope inspected'},
        {'scope':'Explicit S50 own source/CPU metadata/legacy join/frozen work orders','queries':'accepted_original|predicate|cohort|task_contract|scope|axis|boundary|fullramp','followup':'Resolved task_contract through original TASK and exact producer save assignment'},
        {'scope':str(E0),'queries':'world_cycle_metrics|scut_style_gate|scut_curriculum_gate|target_evidence|spin_skill_pass|strict_pass_window','followup':'Found narrower probe qualification rules; not silently mapped to current E0 task'},
       ],
       'glob_limitations':['T ./\u002a.md returned0 despite known root MD files: not evidence of absence','New output directory did not exist before first write (glob os error2)'],
       'unjoined_explicit_reference':{'source':'formals189','lines':'143-145','basename':'MOD4_MOE_MASTER_PLAN.md','published_bytes':47599,'published_SHA256':'812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b','reason':'Only C-task path referenced; no matching T source found; C not opened by request'},
       'limitations':'Bounded examined-set conclusion only. Not an exhaustive historic/remote search or global nonexistence assertion.',
      },
      'native_or_checkpoint_operations':{'native':0,'SDK_imports':0,'Torch_imports':0,'GPU':0,'PT_open_stat_hash':0,'NPZ_JSONL_raw_open':0,'SSH':0,'C_task_reads':0,'account_lock_Git':0,'old_source_writes':0},
    }
    fresh_json('AUDIT_INPUTS_SHA256_V2.json',dict(kind='EXPLICIT_TEXT_INPUTS_ONLY',files=rows))
    fresh_json('ACCEPTANCE_AUTHORITY_FINDINGS_V2.json',findings)
    print(json.dumps({'input_files':len(rows),'task_contract_exact_text_join':True,'E0_binary':None,'S50_binary':None,'native':0}))

if __name__=='__main__':main()
