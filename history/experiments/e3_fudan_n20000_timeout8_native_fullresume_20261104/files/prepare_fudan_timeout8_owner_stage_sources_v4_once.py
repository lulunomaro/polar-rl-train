"""Create unused owner/stage metadata variants. No PT, SDK, SSH, locks or ledger operations."""
from pathlib import Path
import ast,json,hashlib
D=Path(__file__).resolve().parent
old=D/'source_original_owner_v3_20k';new=D/'source_original_owner_v4_20k_timeout8';stage=D/'stage_fudan_nonpt_v4_20k_timeout8.py'
assert not new.exists() and not stage.exists()
c=json.loads((D/'reports/FDN_N20000_W5_20261104_205335/CLOSED_RESULT.json').read_bytes());m=c['metadata'];f=m['FDN_FINAL.json'];s=m['FDN_LATEST_COMPLETE_SAVE.json'];x=m['OWNER_EXIT_ACTUAL.json'];o=m['OUTER_OWNER_WAIT_ACTUAL.json'];q=m['FDN_PARENT_WAIT_QUALIFICATION.json']
assert c['closed']is True and x['errors']==[] and all(x[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))
assert o['original_owner_reaped']is True and o['actual_wait_returncode']==0 and q['qualified']is True and all(v is True for v in q['checks'].values())
assert f['counters']=={'encoder_optimizer_steps':2660,'policy_optimizer_steps':2660,'transitions_seen':78822912,'updates':133}
assert s==f['latest_complete_save'] and s['sha256']=='8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78'and s['bytes']==1204250903
assert f['window_counters']['updates']==69 and f['native_counters']['actual_native_policy_steps']==3360
source=dict(path=s['path'],sha256=s['sha256'],bytes=s['bytes'],run=f['run'],counters=f['counters'],source_envs=20000,actual_native_policy_steps=3360,unoptimized_pending_controls=48,source_training_execution_qualified=True)
source_kind='fdn_n20000_full_learner_timeout8_source'
def replace_once(text,a,b):
    assert text.count(a)==1,(a,text.count(a));return text.replace(a,b)
owner=(old/'fudan_original_owner_v1.py').read_text(encoding='utf8')
pin=next(line for line in owner.splitlines()if line.startswith('PINNED_LEARNER_SOURCE='))
owner=replace_once(owner,pin,'PINNED_LEARNER_SOURCE='+repr(source))
owner=replace_once(owner,'New warm branch, no legacy SuperMimic or PPO20 continuation claim.','Full N20000 learner continuation with low-only timeout8; no legacy branch resume.')
owner=replace_once(owner,"require(e.get('source_training_execution_qualified')is True and e['learner_source']==PINNED_LEARNER_SOURCE,","require(e.get('source_training_execution_qualified')is True and e.get('source_kind')=="+repr(source_kind)+" and e['learner_source']==PINNED_LEARNER_SOURCE,")
owner=replace_once(owner,"task.update(learner_source=dict(e['learner_source']),","task.update(source_kind=e['source_kind'],learner_source=dict(e['learner_source']),")
owner=replace_once(owner,'source_envs=4096,new_envs=20000,stream_cut=True,','source_envs=20000,new_envs=20000,stream_cut=True,lowrise_episode_timeout_s=8.0,original_global_episode_length_unchanged=True,')
oldtree=ast.parse((old/'fudan_original_owner_v1.py').read_text(encoding='utf8'));tree=ast.parse(owner);compile(tree,'owner_timeout8','exec')
for name in('require','gpu','account','environment','qualify_waited','main'):
    a=next(v for v in oldtree.body if isinstance(v,ast.FunctionDef)and v.name==name);b=next(v for v in tree.body if isinstance(v,ast.FunctionDef)and v.name==name)
    assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False),name
text=(D/'stage_fudan_nonpt_v3_20k.py').read_text(encoding='utf8')
text=replace_once(text,"role_key='e3_fudan_seq_n20000_learner_continue64_72'","role_key='e3_fudan_seq_n20000_timeout8_continue133'")
text=replace_once(text,"entry.update(learner_source=P['learner_source'],source_training_execution_qualified=True)","entry.update(source_kind="+repr(source_kind)+",learner_source=P['learner_source'],source_training_execution_qualified=True)")
compile(ast.parse(text),'stage_timeout8','exec')
new.mkdir();(new/'fudan_original_owner_v1.py').write_text(owner,encoding='utf8',newline='\n');stage.write_text(text,encoding='utf8',newline='\n')
print(json.dumps(dict(source=source,source_kind=source_kind,owner_source=str(new/'fudan_original_owner_v1.py'),stage_source=str(stage),original_account_resource_environment_main_and_wait_AST_unchanged=True,AST_compile_pass=True,PT_SDK_SSH_GPU_C_or_lock_operations=0),indent=2))
