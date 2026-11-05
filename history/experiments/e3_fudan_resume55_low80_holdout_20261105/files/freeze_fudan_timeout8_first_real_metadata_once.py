"""Freeze one positive own-metadata point, never reopen a model or raw trace."""
from pathlib import Path
import json,time
D=Path(__file__).resolve().parent;dest=D/'FDN_N20000_W6_TIMEOUT8_FIRST_REAL_TRAINING_EVIDENCE.json';assert not dest.exists()
ref=json.loads((D/'FDN_N20000_W6_TIMEOUT8_COLLECTOR_ONCE.json').read_bytes());out=Path(ref['output']);snap=json.loads((out/'LATEST_METADATA_SNAPSHOT.json').read_bytes());init=snap['native_initialization'];up=snap['native_update'];w=up['window_counters'];base=up['base_counters'];cum=up['counters'];n=up['native_counters'];r=up['source_checkpoint'];t=up['task_summary'];overlay=up['task_runtime_overlay']
assert snap['root']==ref['root'] and snap['worker_error']is None and up['version']==3 and up['actual_native_training_update']is True
assert init['source_envs']==init['fresh_envs']==up['rollout_N']==20000 and up['rollout_T']==48
assert base==dict(updates=133,policy_optimizer_steps=2660,encoder_optimizer_steps=2660,transitions_seen=78822912)
assert w['updates']>0 and w['policy_optimizer_steps']==w['encoder_optimizer_steps']==20*w['updates'] and w['transitions_seen']==960000*w['updates']
assert all(cum[k]==base[k]+w[k]for k in base)
assert all(r[k]==1 for k in('physical_byte_opens','SHA_calculations','CPU_decodes','learner_source_reads'))
assert r['source_sha256']=='8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78'and r['source_bytes']==1204250903 and r['complete_learner_loaded']is True
assert r['original_mother_reads']==r['ancestor_N4096_reads']==0
assert all(r[k]is True for k in('whole_source_root_and_bytes_retained','unknown_source_fields_retained','whole_CPU_identity_content_and_versions_unchanged','learner_load_uses_unchanged_core_clone'))
assert init['source_global_RNG_environment_DR_history_queues_or_pending_applied']is False
assert n['actual_native_policy_steps']==48*w['updates'] and n['actual_native_transitions']==20000*n['actual_native_policy_steps'] and n['physical_callbacks']==8*n['actual_native_policy_steps'] and n['feedback_callbacks']==2*n['actual_native_policy_steps']
assert overlay['bytes']==8571 and overlay['sha256']=='386107b02983505518e1dcfb5bbdeb6f243392d390dfd48e16a61d75cb2c51e2'
to=t['lowrise_timeout8'];assert to['policy_steps']==400 and to['duration_s']==8.0 and to['time_out']is True and to['step_dt_s']==.02
result=dict(kind='ACTUAL_N20000_FULL_LEARNER_RESUME_TIMEOUT8_FIRST_POSITIVE_POINT_NOT_SKILL_PASS',epoch=time.time(),snapshot_epoch=snap['epoch'],root=snap['root'],native_updates=w['updates'],window_counters=w,base_counters=base,cumulative_counters=cum,native_counters=n,source_receipt=r,learner_continuation=up['learner_continuation'],task_runtime_overlay=overlay,actual_original_global_episode_length_s=t['actual_env_cfg_episode_length_s'],lowrise_timeout8=to,learner_functional_metrics=up['learner_functional_metrics'],training_task_summary_not_independent_grade=t,window_still_running=snap['outer_owner_wait']is None,skill_improvement_claim=False,selected_model_raw_or_canonical_operations=0)
dest.write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf8')
print(json.dumps(dict(path=str(dest),new_updates=w['updates'],cumulative_updates=cum['updates'],new_optimized_transitions=w['transitions_seen'],actual_global_episode_s=t['actual_env_cfg_episode_length_s'],lowrise_timeout8=to,source_IO={k:r[k]for k in('physical_byte_opens','SHA_calculations','CPU_decodes','original_mother_reads','ancestor_N4096_reads')},no_skill_claim=True),indent=2))
