shutil.copytree(P/'controllers',N/'controllers')
payloads={};specs={};sources={}
rec=read(P/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json')
rec.update(remaining_after=proof['remaining_actual_snapshot'],source_current_cohort_original_cost_summary=proof,latest70_original_cost_closure=proof,derived_current_cohort_source_cost_receipt_only=True,legacy18_pending_not_reconciled_again=True)
put(R/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)
for key in ('h1','recovery'):
 base=Path(oldq['payloads'][key]);out=N/'payloads'/key
 shutil.copytree(base,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 oldm=read(base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');model=proof['models'][key];final=model['final'];source=Path(final['local_path'])
 assert source.stat().st_size==final['bytes'] and final['twohost_complete_SHA']
 spec=dict(oldq['specs'][key]);spec.update(previous_runtime_root=oldq['roots'][key],previous_exit_kind='node',source_SHA=final['SHA'],source_Adamstep=model['Adam'],closed_production_continuation=True,reuse_completed_native=False)
 if key=='h1':spec['reward_migration']=False
 captures=out/'source_bind_history70';captures.mkdir()
 for name in ('THREE_SLOT_COMPLETE_MANIFEST_V1.json','job0/TASK.json','SAME_OPTIMIZED_CONTINUATION_SOURCE_AUTH_ACTUAL.json'):
  shutil.copy2(out/name,captures/Path(name).name)
 shutil.copy2(source,out/'job0/source'/spec['source_filename'])
 role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
 shutil.copy2(path,out/role)
 shutil.copy2(N/'forwarded_original_owner_control_v2.py',out/'forwarded_original_owner_control_v1.py')
 shutil.copy2(R/'ACTUAL_SEND_PACKET_FRAGMENTATION_CPU_INTEGRATION_ACTUAL.json',out/'NETWORK_HTTP_RESPONSE_CPU_ACTUAL.json')
 shutil.copy2(N/'same_optimized_source_contract_metadata_candidate_v1.py',out/'same_optimized_source_contract_metadata_candidate_v1.py')
 if key=='recovery':(out/'recovery_worker.py').write_text(new_worker,encoding='utf8')
 task=read(out/'job0/TASK.json')
 task.update(id=N.name+'_'+key,source_SHA=final['SHA'],source_Adamstep=model['Adam'],source_H1_actual_latest_Adamstep=model['Adam'] if key=='h1' else None,source_parent_production_root=oldq['roots'][key],source_policy_hz=spec['policy_hz'],policy_hz=spec['policy_hz'],source_owned_updates=model['updates'],source_owned_completed_updates=model['updates'],exact_closed_source_updates=model['updates'],same_clock_complete_source_no_native_replay=True,same_step270_phase_complete_continuation=key=='h1',explicit_human_authorized_reward_path_change=False,reward_recipe_version='same_V6A_sagittal_tuck_and_sampling_optimization_continuation' if key=='h1' else None)
 (out/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
 proofname='CURRENT_ORIGINAL_PAIR_CLOSED_MODELS_COST_CPU_ACTUAL.json' if key=='h1' else 'CURRENT_ORIGINAL_COHORT_CLOSED_COST_CPU_ACTUAL.json'
 for name,val in [('QUALIFIED_RUNTIME_BASE_MANIFEST.json',oldm),(proofname,proof),('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)]:
  (out/name).write_text(json.dumps(val,indent=2),encoding='utf8')
 auth=dict(epoch=time.time(),approved=True,kind='actual_closed70_to_same_optimized_network71',human_scope='Continue authorized step270 repair and sampling acceleration training; unchanged V6A reward/physics/actor/PPO',source_complete_SHA=final['SHA'],source_Adam=model['Adam'],source_updates=model['updates'],source_complete_original_cost_report_SHA=H(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'),new_guard_SHA=H(out/role),metadata_contract_SHA=H(out/'same_optimized_source_contract_metadata_candidate_v1.py'),exact_Adam_guard_CPU_report_SHA=H(R/'NETWORK71_EXACT_SOURCE_AST_CPU_ACTUAL.json'),no_new_reward_inputs_physics_or_amp=True,no_prior_approval_JSON_rewritten=True)
 auth.update(network_module_SHA=H(out/'forwarded_original_owner_control_v1.py'),network_CPU_report_SHA=H(out/'NETWORK_HTTP_RESPONSE_CPU_ACTUAL.json'))
 (out/'SAME_OPTIMIZED_CONTINUATION_SOURCE_AUTH_ACTUAL.json').write_text(json.dumps(auth,indent=2),encoding='utf8')
 prior={x['relative']:x for x in oldm['files']};rows=[]
 for p in sorted(out.rglob('*')):
  if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
  rel=p.relative_to(out).as_posix()
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  if p.suffix in ('.pt','.npz','.usd','.stl'):
   digest=final['SHA'] if rel=='job0/source/'+spec['source_filename'] else prior[rel]['SHA']
  else:digest=H(p)
  rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=digest))
 manifest=dict(oldm,source_SHA=final['SHA'],source_Adamstep=model['Adam'],files=rows,closed_step270_samephase_continuation=key=='h1',explicit_command_audit_adapter_repair=False)
 md.validate_same_optimized_protected_inventory(oldm,manifest)
 (out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
 spec['manifest_SHA']=H(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');payloads[key]=str(out);specs[key]=spec
 sources[key]=dict(SHA=final['SHA'],bytes=final['bytes'],Adam=model['Adam'],updates=model['updates'],path=final['path'])
root='H1step270_sampling_opt1_sagtuck6a_net2_2510v71'
q=dict(epoch=time.time(),passed=True,payloads=payloads,specs=specs,sources=sources,roots=dict(h1='/mnt/mod4_linux_durable_20261013/'+root+'/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/'+root+'/recovery'),owner_root='/mnt/mod4_linux_durable_20261013/'+root+'/owner',previous_owner_root=oldq['owner_root'],both_latest_complete_model_CPU_original_cost_allout=True,no_native_or_query_replay=True,no_remote_Task_or_GO_yet=True,not_fresh_resource_or_installed_source_CPU_admission=True)
put(R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json',q)
deploy=(P/'deploy_selected_pair_unused_once.py').read_text('utf8')
with (N/'deploy_selected_pair_unused_once.py').open('x',encoding='utf8') as f:f.write(deploy)
for name in ('collect_selected_pair_first_PPO_unused_once.py','collect_selected_pair_finals_unused_once.py','review_selected_pair_models_unused_once.py'):
 shutil.copy2(P/name,N/name)
print(json.dumps(dict(prepared_local_payloads=True,source_final_Adam={k:v['Adam'] for k,v in sources.items()},guard_fixture_tests=len(tests),same_V6A_reward_and_optimized_runtime=True,no_remote_install_Task_GO_or_fee=True)))
