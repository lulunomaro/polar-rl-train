"""Source-only N20000/full-learner continuation descriptor change. Original resource/account/wait code stays exact."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;dst=D/'source_original_owner_v3_20k'
if dst.exists():assert dst.is_dir() and not any(dst.iterdir()),'Only the empty directory from failed source preparation may remain'
else:dst.mkdir()
source=json.loads((D/'FDN_W3_4096_CLOSED_FOR_N20000_SOURCE.json').read_text(encoding='utf8'))['source'];assert source['source_training_execution_qualified'] and source['source_envs']==4096
old=(D/'source_original_owner_v2/fudan_original_owner_v1.py').read_text(encoding='utf8');new=old
edits={"e['num_envs']==4096":"e['num_envs']==20000",'Declared finite Fudan PPO cohort':'Declared finite N20000 Fudan PPO cohort',"put(J/'TASK.json',task)":"task.update(learner_source=dict(e['learner_source']),source_training_execution_qualified=e['source_training_execution_qualified'],teacher_metadata_is_ancestral_only=True);put(J/'TASK.json',task)","warm_start_only=True,source_Adam_iteration_or_DR_not_resumed=True":"warm_start_only=False,full_fdn_learner_continuation=True,source_environment_DR_history_queues_not_resumed=True,source_envs=4096,new_envs=20000,stream_cut=True",'actualGOthroughload-warm-sequence-PPO-fullsave':'actualGOthroughload-fullFDNlearner-continuation-sequence-PPO-fullsave','max_policy_iterations=300':'max_new_policy_iterations=300,training_num_envs=20000'}
for a,b in edits.items():assert new.count(a)==1,a;new=new.replace(a,b)
anchor="require(m['asset_USD_SHA']=="
assert new.count(anchor)==1
validation="require(e.get('source_training_execution_qualified')is True and e['learner_source']==PINNED_LEARNER_SOURCE,'Qualified exact completed learner source required; no PT read here');"
new=new.replace(anchor,validation+anchor)
idx=new.index('def require(');new=new[:idx]+'PINNED_LEARNER_SOURCE='+repr(source)+'\n'+new[idx:]
oldtree=ast.parse(old);newtree=ast.parse(new)
for name in ('gpu','account','environment'):
 a=next(x for x in oldtree.body if isinstance(x,ast.FunctionDef)and x.name==name);b=next(x for x in newtree.body if isinstance(x,ast.FunctionDef)and x.name==name);assert ast.get_source_segment(old,a)==ast.get_source_segment(new,b),name
start='until=time.monotonic()+1800';end='while pending or slots:';assert old[old.index(start):old.index(end)]==new[new.index(start):new.index(end)]
(dst/'fudan_original_owner_v1.py').write_text(new,encoding='utf8')
gate=(D/'source_original_owner_v2/fudan_worker_close_contract_v1.py').read_text(encoding='utf8');anchor=' except Exception as exc:error=repr(exc)';assert gate.count(anchor)==1
extra="""  lineage=f['learner_continuation'];base=lineage['base_counters'];window=f['window_counters'];keys=('updates','policy_optimizer_steps','encoder_optimizer_steps','transitions_seen')
  checks.update(new_N20000_cohort=lineage['new_envs']==20000 and lineage['source_envs']==4096,fresh_cross_cohort_stream_cut=lineage['fresh_env_history_DR']is True and lineage['source_env_history_DR_queues_applied']is False and lineage['pending_rollout_discarded_at_stream_cut']is True,learner_base_is_pinned_completed_source=base==g['learner_source_counters'] if 'learner_source_counters'in g else base==PINNED_BASE,new_window_updates_positive=window['updates']>0,new_window_counters_are_exact_deltas=set(window)==set(keys)and all(type(window[k])is int and window[k]==c[k]-base[k]for k in keys),new_window_two_Adam=window['policy_optimizer_steps']==window['encoder_optimizer_steps']==20*window['updates'],new_window_trained_transitions=window['transitions_seen']==20000*48*window['updates'],new_window_native_transition_count=native['actual_native_transitions']==20000*native['actual_native_policy_steps'],new_window_native_callback_count=native['physical_callbacks']==8*native['actual_native_policy_steps']and native['feedback_callbacks']==2*native['actual_native_policy_steps'],untrained_partial_not_counted_as_optimized=0<=native['actual_native_policy_steps']-48*window['updates']<=48,save_window_metadata=s['window_counters']==window and s['learner_continuation']==lineage,no_mother_reopen=s['original_mother_reads']==0 and s['learner_source_reads']==1)
"""
gate=gate.replace(anchor,extra+anchor);gate=gate.replace("KIND='MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1'","KIND='MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1'\nPINNED_BASE="+repr(source['counters']));ast.parse(gate);(dst/'fudan_worker_close_contract_v1.py').write_text(gate,encoding='utf8')
stage=(D/'stage_fudan_nonpt_v2.py').read_text(encoding='utf8');assert stage.count('num_envs=4096')==1 and stage.count("e3_fudan_seq_lowrise_w2_mapping_72")==1
stage=stage.replace('num_envs=4096','num_envs=20000').replace('e3_fudan_seq_lowrise_w2_mapping_72','e3_fudan_seq_n20000_learner_continue64_72');anchor="put(R/'OWNER_PLAN.json',";assert stage.count(anchor)==1;stage=stage.replace(anchor,"entry.update(learner_source=P['learner_source'],source_training_execution_qualified=True);"+anchor);ast.parse(stage);(D/'stage_fudan_nonpt_v3_20k.py').write_text(stage,encoding='utf8')
rows=[]
for p in (dst/'fudan_original_owner_v1.py',dst/'fudan_worker_close_contract_v1.py',D/'stage_fudan_nonpt_v3_20k.py'):
 raw=p.read_bytes();compile(raw,str(p),'exec');rows.append(dict(path=p.name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
out=D/'FDN_N20000_OWNER_STAGE_SOURCE_RESULT.json';assert not out.exists();out.write_text(json.dumps(dict(epoch=time.time(),source_pin=source,source_only=True,original_gpu_account_environment_and_resource_wait_exact=True,no_Torch_tests_models_SDK_GPU_or_C_operations=True,files=rows),indent=2),encoding='utf8');print(json.dumps(rows,indent=2))
