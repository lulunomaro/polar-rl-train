"""SOURCE candidate: finite A1 same-view segments; no resources, models or SDK.
Only bind_plan_source_final performs bounded FINAL JSON I/O. Checkpoints are
opened solely by the unchanged admitted PinnedOwnFullCheckpoint worker API.
"""
from pathlib import Path
import hashlib,json,os
from resume_runtime_contracts_v3 import (FINAL_KIND,RAW35_ACTOR_VIEW,COUNT_FIELDS,
    validate_worker_variant,validate_resume_descriptor,validate_count_snapshot)

PLAN_KIND='MOD4V1_QUALITY_MICROTRAIN_SUBSET_PLAN_V1'
SCHEMA='A1_RAW35_LEGACY_FINITE_VERIFIED_INCREMENT_V1'
PURPOSE='QUALITY_FEEDBACK_DRIVEN_A1_SAME_VIEW_MICROTRAIN_NOT_ACCEPTANCE_V1'
ROLES=('E0','E2','E3','W35','CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50')
SOURCE_ONLY_STATUS=dict(source_candidate_implemented=True,implemented_for_actual_training=False,
    enabled_for_actual_training=False,actual_training_operations=0,new_stager_or_dispatcher=False)

def need(value,message):
    if not value:raise ValueError(message)
def integer(value):return type(value)is int and value>=0
def same_path(a,b):return os.path.normcase(os.path.abspath(a))==os.path.normcase(os.path.abspath(b))
def sha(value):return isinstance(value,str) and len(value)==64 and all(x in '0123456789abcdef' for x in value)
def zero_counts():return {name:0 for name in COUNT_FIELDS}

def source_final(entry):
    """Validate retained source metadata; never stat/resolve/open checkpoint paths."""
    descriptor=validate_resume_descriptor(entry['resume_bptt']);source=entry['microtrain']['source_final']
    need(isinstance(source,dict) and sha(source.get('SHA')) and integer(source.get('bytes')) and 0<source['bytes']<=262144,'bounded pinned actual source FINAL required')
    need(Path(source['path']).name=='FINAL.json','source evidence must be FINAL.json, not a checkpoint')
    final=source['metadata'];counts=validate_count_snapshot(final.get('counts'))
    need(final.get('kind')==FINAL_KIND and final.get('passed_execution')is True and final.get('teacher_unchanged')is True,'successful original producer FINAL required')
    need(final.get('role')==entry['role'] and final.get('run_id')==descriptor['producer_run_id'],'source FINAL role/run lineage differs')
    need(isinstance(descriptor.get('producer_role_key'),str) and final.get('role_key')==descriptor['producer_role_key'],'source role-key lineage differs')
    need(final.get('actor_view')==RAW35_ACTOR_VIEW and final.get('algorithm_family')=='a1_raw35_legacy_v1','source is not A1 same-view legacy')
    need(final.get('algorithm_variant')in('A1_RAW35_FRESH','A1_RAW35_RESUME'),'source algorithm variant differs')
    need(final.get('actual_BPTT_policy_steps')==counts['pi_bptt_optimizer_steps'],'source verified counter differs')
    checkpoint=final['checkpoint']
    need(same_path(checkpoint['path'],descriptor['path']) and checkpoint['SHA']==descriptor['SHA'] and checkpoint['bytes']==descriptor['bytes'],'source FINAL/checkpoint byte identity differs')
    need(checkpoint.get('counts')==counts and checkpoint.get('full_new_model_critic_aux_optimizers_replay_RNG_hist_saved')is True,'source is not complete full payload')
    need(Path(descriptor['path']).parent==Path(source['path']).parent/'checkpoints' and Path(descriptor['path']).name.endswith('_complete.pt'),'source checkpoint outside own source production/checkpoints')
    return counts

def bind_plan_source_final(entry,reader=None):
    """Future owner metadata only; exact single FINAL byte read, never PT I/O."""
    entry=dict(entry);entry['microtrain']=dict(entry['microtrain'])
    if entry.get('resume_bptt')is None:return entry
    source=dict(entry['microtrain']['source_final']);need(Path(source['path']).name=='FINAL.json','source FINAL filename differs')
    if reader is None:
        with Path(source['path']).open('rb')as stream:raw=stream.read(262145)
    else:raw=reader(source['path'])
    need(isinstance(raw,bytes) and 0<len(raw)<=262144,'bounded FINAL byte read differs')
    need(len(raw)==source['bytes'] and hashlib.sha256(raw).hexdigest()==source['SHA'],'actual source FINAL byte pin differs')
    metadata=json.loads(raw)
    if source.get('metadata')is not None:need(source['metadata']==metadata,'declared/actual source FINAL differs')
    source['metadata']=metadata;entry['microtrain']['source_final']=source
    return entry

def validate_microtrain_entry(entry):
    need(entry.get('role')in ROLES,'exact eight-role catalog only; H1 excluded')
    need(isinstance(entry.get('role_key'),str) and entry['role_key'],'own role key required')
    need(entry.get('num_envs')in(512,1024,2048),'original explicit batch choices only')
    selected=validate_worker_variant(entry)
    need(selected['actor_view']==RAW35_ACTOR_VIEW and selected['algorithm_family']=='a1_raw35_legacy_v1' and entry.get('algorithm_family','a1_raw35_legacy_v1')=='a1_raw35_legacy_v1','only A1 raw35 legacy; no A0 or cross-view migration')
    segment=entry['microtrain'];need(segment.get('schema')==SCHEMA,'microtrain schema differs')
    increment=segment.get('target_verified_increment');need(type(increment)is int and 1<=increment<=300,'positive requested increment at most 300')
    if entry.get('resume_bptt')is None:
        need(segment.get('source_final')is None,'fresh segment must not splice a producer lineage')
        baseline=zero_counts()
    else:baseline=source_final(entry)
    target=baseline['pi_bptt_optimizer_steps']+increment
    if entry.get('target_bptt_steps')is not None:need(type(entry['target_bptt_steps'])is int and entry['target_bptt_steps']==target,'planned cumulative target is not source baseline plus increment')
    output=dict(entry);output.update(selected);output['target_bptt_steps']=target
    output['microtrain']=dict(segment,declared_source_counts=baseline,target_cumulative_verified_counter=target,purpose=PURPOSE)
    return output

def validate_microtrain_plan(plan,*,reader=None):
    need(plan.get('kind')==PLAN_KIND and plan.get('H1_excluded')is True,'explicit source-only subset plan/H1 exclusion required')
    requested=plan['requested_roles'];deferred=plan['deferred_roles']
    need(isinstance(requested,list) and 1<=len(requested)<=2 and len(set(requested))==len(requested) and set(requested)<=set(ROLES),'one or two unique requested roles only')
    need(isinstance(deferred,list) and len(set(deferred))==len(deferred) and set(deferred)==set(ROLES)-set(requested),'deferred must be exact unrequested catalog')
    entries=plan['entries'];need(len(entries)==len(requested) and [e['role']for e in entries]==requested,'only requested entries may enter pending/SDK queue')
    need(len({e['role_key']for e in entries})==len(entries),'own canonical role keys must be unique')
    output=dict(plan);output['entries']=[validate_microtrain_entry(bind_plan_source_final(e,reader))for e in entries]
    return output

def bind_microtrain_task(task,entry):
    entry=validate_microtrain_entry(entry);out=dict(task,microtrain=entry['microtrain'],quality_microtrain_purpose=PURPOSE)
    need(task['target_bptt_steps']==entry['target_bptt_steps'],'owner cumulative target differs')
    return out

def bind_microtrain_go(go,entry):
    segment=validate_microtrain_entry(entry)['microtrain']
    need(go['max_actual_BPTT_policy_updates']==segment['target_cumulative_verified_counter'],'original cumulative GO policy target differs')
    return dict(go,microtrain_target_verified_increment=segment['target_verified_increment'],microtrain_declared_start_counter=segment['declared_source_counts']['pi_bptt_optimizer_steps'],quality_microtrain_purpose=PURPOSE)

def validate_worker_microtrain_task(task):
    normalized=validate_microtrain_entry(task)
    need(task['target_bptt_steps']==normalized['target_bptt_steps'] and task['microtrain']==normalized['microtrain'],'worker target or normalized metadata drift')
    return True

def validate_microtrain_payload(payload,task):
    """Before original strict full loader mutates any model/optimizer."""
    validate_worker_microtrain_task(task);need(task.get('resume_bptt')is not None,'resume payload requested on fresh segment')
    descriptor=task['resume_bptt'];metadata=task['microtrain']['source_final']['metadata']
    need(payload.get('run_id')==descriptor['producer_run_id']==metadata['run_id'],'embedded/declared/actual FINAL producer runs differ')
    need(payload.get('role')==task['role'] and payload.get('role_key')==descriptor['producer_role_key']==metadata['role_key'],'embedded producer role/key differs')
    need(payload.get('actor_view')==RAW35_ACTOR_VIEW and payload.get('algorithm_family')=='a1_raw35_legacy_v1','payload same-view family differs')
    need(validate_count_snapshot(payload['context_reward_extension']['counts'])==task['microtrain']['declared_source_counts'],'actual full payload counters differ from source FINAL')
    return True

def start_microtrain_segment(task,counts,*,resume_receipt=None):
    validate_worker_microtrain_task(task);counts=validate_count_snapshot(counts);expected=task['microtrain']['declared_source_counts']
    need(counts==expected,'actual restored/fresh nine counters differ from declared source; no count offset')
    resumed=task.get('resume_bptt')is not None
    if resumed:
        need(isinstance(resume_receipt,dict) and resume_receipt['restored_counts']==counts,'original full loader counter receipt differs')
        cache=resume_receipt['byte_cache'];need(all(type(cache.get(k))is int and cache[k]==1 for k in ('physical_byte_opens','SHA_calculations','decodes')) and cache.get('whole_full_checkpoint_retained')is True,'resume must retain one physical byte cache/hash/decode')
        need(resume_receipt.get('reset_resume_stream_cut_required')is True and resume_receipt.get('no_actor_only_fallback')is True and resume_receipt.get('no_counter_offset_or_fresh_count_splicing')is True,'original full fresh-environment stream-cut loader receipt required')
    else:need(counts==zero_counts() and resume_receipt is None,'fresh lineage must actually start at zero')
    increment=task['microtrain']['target_verified_increment'];target=counts['pi_bptt_optimizer_steps']+increment
    need(target==task['target_bptt_steps'],'loaded actual counter plus requested increment differs')
    return dict(schema=SCHEMA,purpose=PURPOSE,role=task['role'],run_id=task['run_id'],role_key=task['role_key'],
        source_lineage='OWN_SAME_VIEW_FULL_RESUME'if resumed else'OWN_FRESH_ZERO',source_resume=task.get('resume_bptt'),
        source_FINAL_identity=None if not resumed else{k:task['microtrain']['source_final'][k]for k in ('path','bytes','SHA')},
        starting_counts=dict(counts),starting_verified_counter=counts['pi_bptt_optimizer_steps'],target_verified_increment=increment,
        target_cumulative_verified_counter=target,one_explicit_fresh_env_reset_before_load=True,extra_reset_after_load=0,
        live_history_after_reset='zeros_then_original_fresh_episode_padding',saved_history_is_not_reused_as_new_episode=True,
        original_full_resume_receipt=resume_receipt,goal_is_quality_feedback_not_update_count_acceptance=True)

def finish_microtrain_segment(segment,counts,*,stopped):
    need(isinstance(segment,dict) and type(stopped)is bool,'actual post-load segment baseline/original stop bool missing')
    end=validate_count_snapshot(counts);start=segment['starting_counts'];delta={k:end[k]-start[k]for k in COUNT_FIELDS}
    need(all(v>=0 for v in delta.values()),'producer counters regressed across finite segment')
    need(delta['pi_bptt_optimizer_steps']<=segment['target_verified_increment'],'actual verified increment exceeded finite requested segment')
    return dict(segment,ending_counts=dict(end),actual_counter_increments=delta,actual_verified_increment=delta['pi_bptt_optimizer_steps'],
        total_original_verified_counter=end['pi_bptt_optimizer_steps'],target_reached=end['pi_bptt_optimizer_steps']>=segment['target_cumulative_verified_counter'],
        original_WindowSavedStop_observed=bool(stopped),skill_pass_rate=None,overall_eight_coverage=None)

def enforce_microtrain_waited_result(original,entry):
    """Adds segment identity checks AFTER, never replaces, original fast-close gate."""
    result=dict(original);reasons=list(original.get('reasons',[]))
    if original.get('passed_execution')is True and original.get('original_error')is False:
        try:
            entry=validate_microtrain_entry(entry);final=original['final'];segment=final['microtrain_segment']
            need(segment['schema']==SCHEMA and segment['purpose']==PURPOSE,'FINAL segment schema differs')
            need(segment['role']==entry['role'] and segment['role_key']==entry['role_key'] and segment['run_id']==final['run_id'],'segment execution identity differs')
            need(segment['starting_counts']==entry['microtrain']['declared_source_counts'],'FINAL baseline differs from selected producer')
            need(segment.get('source_resume')==entry.get('resume_bptt') and segment.get('source_lineage')==('OWN_SAME_VIEW_FULL_RESUME'if entry.get('resume_bptt')is not None else'OWN_FRESH_ZERO'),'FINAL source lineage differs')
            expected_identity=None if entry.get('resume_bptt')is None else{k:entry['microtrain']['source_final'][k]for k in ('path','bytes','SHA')}
            need(segment.get('source_FINAL_identity')==expected_identity and final.get('target_reached')is segment['target_reached'],'FINAL source identity or target report differs')
            need(segment['target_verified_increment']==entry['microtrain']['target_verified_increment'] and segment['target_cumulative_verified_counter']==entry['target_bptt_steps'],'FINAL requested increment/target differs')
            computed=finish_microtrain_segment({k:v for k,v in segment.items()if k not in ('ending_counts','actual_counter_increments','actual_verified_increment','total_original_verified_counter','target_reached','original_WindowSavedStop_observed','skill_pass_rate','overall_eight_coverage')},final['counts'],stopped=final['parent_finite_saved_stop'])
            need(computed==segment and final['checkpoint']['microtrain_segment']==segment,'FINAL/checkpoint segment receipt or actual delta differs')
        except (KeyError,TypeError,ValueError)as exc:reasons.append('bad_quality_microtrain_segment:'+str(exc))
    result.update(reasons=reasons,passed_execution=original.get('passed_execution')is True and not reasons,original_error=original.get('original_error')is not False or bool(reasons),quality_microtrain_is_not_skill_acceptance=True)
    return result
