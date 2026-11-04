"""Create only the minimal fresh-learner owner/stager/close metadata adaptation."""
from pathlib import Path
import ast,hashlib
D=Path(__file__).resolve().parent;old=D/'source_original_owner_v4_20k_timeout8';new=D/'source_original_owner_v5_fresh1cd_timeout8';assert not new.exists()
worker=D/'source_fudan_native_worker_v5_fresh1cd_timeout8/worker_fudan_sequence_ppo_native_v1.py';assert hashlib.sha256(worker.read_bytes()).hexdigest()=='e4d5df2827a2d07d7c880f72bd09e483d4987072c005253c7f93e6b2cccfdeb5'
owner=(old/'fudan_original_owner_v1.py').read_text(encoding='utf8');original=owner

def replace(text,a,b):
 assert text.count(a)==1,a[:100]
 return text.replace(a,b)

owner=replace(owner,'Full N20000 learner continuation with low-only timeout8; no legacy branch resume.','Fresh N20000 Fudan learner; only original1cd actor/critic MLP warm start; timeout8.')
line=next(s for s in owner.splitlines()if s.startswith('PINNED_LEARNER_SOURCE='))
owner=replace(owner,line,"PINNED_MOTHER={'path':'/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt','SHA':'1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8','bytes':14715029,'iteration':43090}")
owner=replace(owner,"require(e.get('source_training_execution_qualified')is True and e.get('source_kind')=='fdn_n20000_full_learner_timeout8_source' and e['learner_source']==PINNED_LEARNER_SOURCE,'Qualified exact completed learner source required; no PT read here')","require(e.get('source_kind')=='fdn_fresh_mlp_warm_1cd_n20000_timeout8'and e['teacher']==PINNED_MOTHER and e['max_iterations']==25 and 'learner_source'not in e,'Fresh original1cd MLP warm-only25 pilot; no PT read here')")
owner=replace(owner,"task.update(source_kind=e['source_kind'],learner_source=dict(e['learner_source']),source_training_execution_qualified=e['source_training_execution_qualified'],teacher_metadata_is_ancestral_only=True)","task.update(source_kind=e['source_kind'],warm_start_only=True,full_learner_resume=False,inherited_old_iterations=0,teacher_metadata_is_ancestral_only=False)")
owner=replace(owner,'warm_start_only=False,full_fdn_learner_continuation=True','warm_start_only=True,full_fdn_learner_continuation=False,fresh_Fudan_learner=True,inherited_old_iterations=0')
owner=replace(owner,'load-fullFDNlearner-continuation-sequence-PPO-fullsave','load-single1cd-MLP-warm-freshFDN-sequence-PPO-fullsave')
oldnodes={n.name:n for n in ast.parse(original).body if isinstance(n,ast.FunctionDef)};newnodes={n.name:n for n in ast.parse(owner).body if isinstance(n,ast.FunctionDef)}
for name in('require','gpu','account','environment','qualify_waited'):assert ast.dump(oldnodes[name])==ast.dump(newnodes[name])
assert ast.dump(oldnodes['main'])==ast.dump(ast.parse(owner.replace('load-single1cd-MLP-warm-freshFDN-sequence-PPO-fullsave','load-fullFDNlearner-continuation-sequence-PPO-fullsave')).body[-2])
stager=(D/'stage_fudan_nonpt_v4_20k_timeout8.py').read_text(encoding='utf8')
stager=replace(stager,"role_key='e3_fudan_seq_n20000_timeout8_continue133'","role_key='e3_fudan_seq_n20000_timeout8_fresh1cd_25'")
stager=replace(stager,'max_iterations=300','max_iterations=25')
stager=replace(stager,"entry.update(source_kind='fdn_n20000_full_learner_timeout8_source',learner_source=P['learner_source'],source_training_execution_qualified=True)","entry.update(source_kind='fdn_fresh_mlp_warm_1cd_n20000_timeout8')")
close=(old/'fudan_worker_close_contract_v1.py').read_text(encoding='utf8');head=close[:close.index('   lineage=')];tail=close[close.index('  except Exception as exc:'):]
head=head.replace("BRANCH='FDN_FULL_LEARNER_CONTINUATION_FRESH_N20000_TIMEOUT8_ENV'","BRANCH='FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8'").replace("SOURCE_KIND='fdn_n20000_full_learner_timeout8_source'","SOURCE_KIND='fdn_fresh_mlp_warm_1cd_n20000_timeout8'").replace("PINNED_BASE={'encoder_optimizer_steps':2660,'policy_optimizer_steps':2660,'transitions_seen':78822912,'updates':133}","PINNED_BASE={'encoder_optimizer_steps':0,'policy_optimizer_steps':0,'transitions_seen':0,'updates':0}").replace("SOURCE_SHA='8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78'","SOURCE_SHA='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8'")
extra="""   task=json.loads((J/'TASK.json').read_bytes());source=f['source_checkpoint'];window=f['window_counters'];keys=('updates','policy_optimizer_steps','encoder_optimizer_steps','transitions_seen')
   checks.update(fresh_version4=f['version']==s['version']==intent['version']==4,branch=f['branch_kind']==s['branch_kind']==intent['branch_kind']==BRANCH,source_kind=f['source_kind']==s['source_kind']==intent['source_kind']==task['source_kind']==SOURCE_KIND,new_N20000=f['num_envs']==s['num_envs']==intent['num_envs']==task['num_envs']==20000,zero_inherited_base=f['base_counters']==s['base_counters']==intent['base_counters']==PINNED_BASE,inherited_iteration_zero=f['inherited_old_iterations']==s['inherited_old_iterations']==intent['inherited_old_iterations']==0,no_bad_candidate_reads=f['bad_candidate_reads']==s['bad_candidate_reads']==intent['bad_candidate_reads']==0,not_full_learner_resume=f['full_learner_resume']is False and s['full_learner_resume']is False and intent['full_learner_resume']is False,fresh_window_is_all_counters=window==c==s['window_counters']==intent['window_counters']and set(c)==set(keys),finite25_pilot=type(c['updates'])is int and 0<c['updates']<=task['max_iterations']==25,two_real_Adam=c['policy_optimizer_steps']==c['encoder_optimizer_steps']==20*c['updates'],optimized_N20000_transitions=c['transitions_seen']==20000*48*c['updates'],native_transition_count=native['actual_native_transitions']==20000*native['actual_native_policy_steps'],native_callbacks=native['physical_callbacks']==8*native['actual_native_policy_steps']and native['feedback_callbacks']==2*native['actual_native_policy_steps'],pending_not_optimized=0<=native['actual_native_policy_steps']-48*c['updates']<=48,source_receipts=source==s['source_checkpoint']==intent['source_checkpoint'],actual_original1cd_warm=source['source_sha256']==SOURCE_SHA and source['source_bytes']==14715029 and source['source_iter']==43090 and source['actor_critic_MLP_only']is True and source['source_optimizer_and_DR_state_not_restored']is True and source['old_iteration_not_inherited']is True,one_original_source_read=source['physical_byte_opens']==source['SHA_calculations']==source['CPU_decodes']==s['original_mother_reads']==1,whole_source_retained=source['whole_source_root_and_bytes_retained']is True and source['source_tensor_versions_unchanged']is True,timeout8_overlay=f['task_runtime_overlay']['sha256']==s['task_runtime_overlay']['sha256']==intent['task_runtime_overlay']['sha256']==OVERLAY_SHA and f['task_runtime_overlay']['bytes']==8571)
"""
close=head+extra+tail
payload={'fudan_original_owner_v1.py':owner,'fudan_worker_close_contract_v1.py':close}
for text in[*payload.values(),stager]:ast.parse(text);compile(text,'fresh1cd-source-only','exec')
new.mkdir()
for name,text in payload.items():(new/name).write_text(text,encoding='utf8',newline='\n')
(D/'stage_fudan_nonpt_v5_fresh1cd_timeout8.py').write_text(stager,encoding='utf8',newline='\n')
print('Created3 source-only files; oneAST/compile; original account/resources/child-wait/cleanup unchanged; no imports/SDK/model/GPU/SSH/C operations')
