"""Prepare unbound same-V8 continuation and new75 saved-only readers; no remote/model/GPU action."""
from pathlib import Path
import ast, copy, hashlib, json, shutil, time, traceback
P=Path(__file__).resolve().parent; T=P.parent; R=P/'reports'
F=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V76_20261026'
U=T/'H1_STEP270_CLOSED75_SAVED_REPLAY_AFTER_V8_20261026'
oldU=T/'H1_STEP270_CLOSED74B_SAVED_REPLAY_BEFORE_V8_20261026'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def write(p,s):
    ast.parse(s)
    with Path(p).open('x',encoding='utf8') as f:f.write(s)
def replace(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b,1)

def main():
    first=json.loads((R/'THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
    assert first['passed'] and first['actual_finite_returned'] and not F.exists() and not U.exists()
    (F/'reports').mkdir(parents=True);(F/'candidates').mkdir();(U/'reports').mkdir(parents=True)
    shutil.copy2(P/'candidates/same_optimized_source_contract_metadata_candidate_v1.py',F/'candidates/same_optimized_source_contract_metadata_candidate_v1.py')
    guard=(P/'candidates/same_three_closed_source_H1_V8_reward_CPU_v1.py').read_text('utf8')
    guard=guard.replace('Uninstalled same-V7/same-optimized triple continuation','Uninstalled strict same-V8/same-optimized triple continuation')
    guard=replace(guard,"bool(spec.get('reward_migration'))==(key=='h1')","not spec.get('reward_migration')")
    guard=replace(guard,'THREE_EXPERT_V8_CONTINUATION_AUTH_ACTUAL.json','THREE_EXPERT_SAME_V8_CONTINUATION_AUTH_76_ACTUAL.json')
    guard=replace(guard,"auth['kind']=='actual_closed_three_V8_H1_reward_continuation'","auth['kind']=='actual_closed_three_same_V8_continuation'")
    begin=guard.index(" before={x['relative']:x for x in prior['files']};after=")
    end=guard.index(" for name in ('H1_TRACE_RETENTION_HUMAN_APPROVAL_ACTUAL.json'",begin)
    helper='''def strict_same_V8_root_inventory(before,after,role,key):
 allowed={role}
 if key=='recovery':allowed.add('recovery_worker.py')
 for name,row in before.items():
  if name.endswith('.py') and name not in allowed:assert name in after and after[name]['SHA']==row['SHA'] and after[name]['bytes']==row['bytes'],name
 assert not {name for name in after if name.endswith('.py') and name not in before}

'''
    guard=guard[:begin]+" before={x['relative']:x for x in prior['files']};after={x['relative']:x for x in current['files']}\n strict_same_V8_root_inventory(before,after,role,key)\n"+guard[end:]
    guard=guard.replace('def load(spec,B):',helper+'def load(spec,B):',1)
    guard=replace(guard,"'H1_V7_REWARD_ONLY_AUTH_AND_CPU_ACTUAL.json','SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json'","'H1_V7_REWARD_ONLY_AUTH_AND_CPU_ACTUAL.json','H1_V8_SAMPLED_LEG_EXCESS_SOURCE_AND_CPU_AUTH_ACTUAL.json','SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json'")
    guard=replace(guard,"  assert H(old/'h1_step270_path_reward_v1.py')==v8['prior_reward_SHA'] and H(old/'h1_production_control_prefix_trace_v1.py')==v8['prior_trace_SHA']","  assert read(B/'job0/TASK.json')['reward_recipe_version']==read(old/'job0/TASK.json')['reward_recipe_version']=='step270_sampled_leg_excess_v8_reward_only'")
    guard=replace(guard,"  kind='closed_same_backend_reward_migration'","  kind='closed_same_backend_production'")
    gp=F/'candidates/same_three_closed_source_same_V8_CPU_v1.py';write(gp,guard)

    # Verify the changed inventory rule directly with actual existing manifest metadata, never a model read.
    ns={'__name__':'synthetic_functions_only'}
    tree=ast.parse(guard)
    for name in ('strict_same_V8_root_inventory','exact_recovery_step'):
        node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name)
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(gp),'exec'),dict(ast=ast),ns)
    tests=[]
    check=ns['strict_same_V8_root_inventory']
    for key in ('h1','e2','recovery'):
        manifest=json.loads((P/'payloads'/key/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
        before={x['relative']:x for x in manifest['files']};after=copy.deepcopy(before)
        role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
        after[role]['SHA']='f'*64
        if key=='recovery':after['recovery_worker.py']['SHA']='e'*64
        check(before,after,role,key);tests.append(dict(key=key,case='only_guard_and_exact_recovery_assert_role_allowed',accepted=True))
        forbidden=['h1_step270_path_reward_v1.py','h1_production_control_prefix_trace_v1.py','step270_reward_installed_CPU_v1.py','sampling_acceleration_installed_CPU_v2.py'] if key=='h1' else [next(n for n in before if n.endswith('.py') and n!=role and n!='recovery_worker.py')]
        for name in forbidden:
            bad=copy.deepcopy(after);bad[name]['SHA']='0'*64
            try:check(before,bad,role,key)
            except AssertionError:tests.append(dict(key=key,case='changed_runtime_python_'+name,rejected=True))
            else:raise AssertionError('Changed V8 source admitted')
        bad=copy.deepcopy(after);bad['unapproved_runtime.py']=dict(relative='unapproved_runtime.py',SHA='0'*64,bytes=1)
        try:check(before,bad,role,key)
        except AssertionError:tests.append(dict(key=key,case='extra_root_python',rejected=True))
        else:raise AssertionError('Extra Python admitted')
    exact=ns['exact_recovery_step'];old='assert steps == {845840+20*updates}\nx=1\n';new='assert steps == {847000+20*updates}\nx=1\n'
    exact(old,new,845840,847000);tests.append(dict(case='single_exact_Adam_assert_AST',accepted=True))
    try:exact(old,new.replace('x=1','x=2'),845840,847000)
    except AssertionError:tests.append(dict(case='extra_recovery_runtime_change',rejected=True))
    else:raise AssertionError('Extra recovery change admitted')

    binder=(P/'bind_complete74b_sources_with_H1_V8_V2_unused_once.py').read_text('utf8')
    binder=binder.replace('before actual73b','before actual75').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V74B_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V75_20261026').replace('2610v75','2610v76').replace('latest74b_original_cost_closure','latest75_original_cost_closure').replace('actual74b_original_models_cost_allout','actual75_original_models_cost_allout')
    binder=replace(binder,"reward_migration=key=='h1'","reward_migration=False")
    binder=replace(binder,'same_three_closed_source_H1_V8_reward_CPU_v1.py','same_three_closed_source_same_V8_CPU_v1.py')
    a=binder.index("  if key=='h1':\n   M=T/");b=binder.index("  if key=='recovery':",a)
    binder=binder[:a]+'''  if key=='h1':
   v8=read(out/'H1_V8_SAMPLED_LEG_EXCESS_SOURCE_AND_CPU_AUTH_ACTUAL.json');assert v8['approved']
   for name,digest in v8['candidate_files'].items():assert H(out/name)==digest
'''+binder[b:]
    binder=binder.replace('THREE_EXPERT_V8_CONTINUATION_AUTH_ACTUAL.json','THREE_EXPERT_SAME_V8_CONTINUATION_AUTH_76_ACTUAL.json').replace("kind='actual_closed_three_V8_H1_reward_continuation'","kind='actual_closed_three_same_V8_continuation'").replace('actual_closed74b_report_SHA','actual_closed75_report_SHA').replace("only_H1_V8_reward_added=key=='h1'","same_V8_reward_and_trace_retained=True").replace("same_V7_three_expert_continuation=key!='h1'","same_V8_three_expert_continuation=True").replace('bound_actual74b_sources','bound_actual75_sources')
    write(F/'bind_complete75_sources_same_V8_unused_once.py',binder)
    deploy=(P/'deploy_actual_three_experts75_H1_V8_original_writer_unused_once.py').read_text('utf8')
    deploy=deploy.replace('only after72 closes','only after75 closes').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V75_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V76_20261026').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V74B_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V75_20261026')
    deploy=replace(deploy,'needle="assert not s.get(\'reward_migration\') and valid_ready(row,s)";assert source.count(needle)==1;source=source.replace(needle,"assert s[\'reward_migration\'] and valid_ready(row,s)",1)', 'needle="assert s[\'reward_migration\'] and valid_ready(row,s)";assert source.count(needle)==1;source=source.replace(needle,"assert not s.get(\'reward_migration\') and valid_ready(row,s)",1)')
    deploy=deploy.replace('no_active72_hotpatch=True','no_active75_hotpatch=True')
    write(F/'deploy_actual_three_experts76_same_V8_original_writer_unused_once.py',deploy)
    e2=(P/'e2_target72_same_backend_install_source_v1.py').read_text('utf8').replace('from complete73b','from complete75').replace('2610v75','2610v76').replace('2610v74b','2610v75')
    write(F/'e2_target72_same_backend_install_source_v1.py',e2)
    # Installer copy loop and all other expressions remain exact except the two owned namespaces.
    oldcode=ast.literal_eval(ast.parse((P/'e2_target72_same_backend_install_source_v1.py').read_text('utf8')).body[1].value)
    code=ast.literal_eval(ast.parse(e2).body[1].value)
    assert code==oldcode.replace('2610v75','2610v76').replace('2610v74b','2610v75')
    for oldname,newname in [('collect_three_experts75_V8_first_PPO_finite_V2_unused_once.py','collect_three_experts76_same_V8_first_PPO_finite_unused_once.py'),('collect_actual_three75_finals_original_cost_unused_once.py','collect_actual_three76_finals_original_cost_unused_once.py'),('review_three_expert_complete_models_original_cost_CPU_unused_once.py','review_three_expert_complete_models_original_cost_CPU_unused_once.py')]:
        text=(P/oldname).read_text('utf8').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V75_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V76_20261026')
        write(F/newname,text)
    for oldname,newname in [('extract_closed74b_last_two_saved_prefixes_CPU_unused_once.py','extract_closed75_last_two_saved_prefixes_CPU_unused_once.py'),('reconstruct_closed74b_saved_motion_USD_CPU_unused_once.py','reconstruct_closed75_saved_motion_USD_CPU_unused_once.py'),('analyze_render_closed74b_saved_step_timing_CPU_unused_once.py','analyze_render_closed75_saved_step_timing_CPU_unused_once.py')]:
        text=(oldU/oldname).read_text('utf8').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V74B_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V75_20261026').replace('H1_STEP270_CLOSED74B_SAVED_ONLY_20261026','H1_STEP270_CLOSED75_SAVED_ONLY_20261026').replace('2610v74b','2610v75').replace('CLOSED74B','CLOSED75').replace('Closed74b','Closed75').replace('closed74b','closed75').replace('Unused74b','Unused75').replace('New74b','New75').replace('new74b','new75').replace('complete74b','complete75')
        write(U/newname,text)
    transport=T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v118.py'
    wrapper=(transport.with_name('same_authorized_session_compressed_transport_v117.py')).read_text('utf8')
    anchor="        'collect_actual_three75_finals_original_cost_unused_once.py',"
    names=['extract_closed75_last_two_saved_prefixes_CPU_unused_once.py','deploy_actual_three_experts76_same_V8_original_writer_unused_once.py','collect_three_experts76_same_V8_first_PPO_finite_unused_once.py','collect_actual_three76_finals_original_cost_unused_once.py']
    wrapper=replace(wrapper,anchor,anchor+'\n'+''.join('        '+repr(name)+',\n' for name in names).rstrip('\n'))
    write(transport,wrapper)
    put(F/'reports/SOURCE_ONLY76_SAME_V8_CONTINUATION_PREPARED_ACTUAL.json',dict(epoch=time.time(),source_only=True,qualified_future_source_SHA_Adam_None=True,no_payload_controller_Task_model_GO_or_fee=True,prior75_complete_original_cost_and_actual_target_SDK_CPU_required=True,only_H1_guard_role_change_not_reward_or_trace_change=True,source_candidate=str(gp),candidate_SHA=H(gp),synthetic_not_installed_admission_tests=tests,E2_copyloop_exact_except_owned_76_and75_namespaces=True,transport=str(transport)))
    put(U/'reports/SOURCE_ONLY75_SAVED_REPLAY_PROTOCOL_PREPARED_ACTUAL.json',dict(epoch=time.time(),source_only=True,wait_complete75_models_original_cost_and_allout=True,last_two_actual_retained_prefixes_only=True,no_74_raw_reexecution_or_policy_physics_GPU=True))
    put(R/'SOURCE_PREPARATION_OVERBROAD_NUMERIC_FILENAME_READER_CLASSIFICATION_ACTUAL.json',dict(epoch=time.time(),attempt='local source discovery with rg --files -g *76*',actual_issue='Matched unrelated numeric receipt filenames; tool output truncated. No remote action or training failure. Replaced with exact top-level directory filter and explicit source paths.',original_reports_unchanged=True))
    print(json.dumps(dict(source_only76_ready=True,guard_inventory_tests=len(tests),new75_saved_only_reader_prepared=True,transport118_exact_new_entries=names,no_payload_or_GO=True)))

if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('SOURCE_ONLY76_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_retry_or_remote_training_action=True));raise
