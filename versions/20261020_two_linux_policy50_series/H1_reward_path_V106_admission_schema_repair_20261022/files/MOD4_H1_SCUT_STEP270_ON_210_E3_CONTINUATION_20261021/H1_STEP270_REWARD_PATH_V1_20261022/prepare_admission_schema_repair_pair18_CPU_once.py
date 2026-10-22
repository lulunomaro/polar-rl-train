from pathlib import Path
import ast,copy,hashlib,json,shutil,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';P=T/'H1_STEP270_E3_REWARD_PATH_PAIR_V17_20261022'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 old=(B/'closed_step270_reward_path_source_CPU_v1.py').read_text('utf8')
 new=old.replace("assert spec['key']==m['key']=='h1'", "assert spec.get('reward_migration') is True\n    assert spec['key']==m['key']=='h1'")
 new=new.replace("kind='closed_same_backend_production'", "kind='closed_same_backend_reward_migration'")
 new=new.replace('same_assets_PPO_account_and_physics_reward_allowlist_CPU=True,','same_assets_PPO_account_and_physics_reward_allowlist_CPU=True,same_physics_assets_and_PPO_AST=True,')
 loader=B/'closed_step270_reward_migration_owner_schema_source_CPU_v2.py';loader.write_text(new,encoding='utf8');ast.parse(new)
 tree=ast.parse((P/'controllers/three_slot_common_v1.py').read_text('utf8'));func=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='valid_ready')
 env=dict(json=json,hashlib=hashlib);exec(compile(ast.Module(body=[func],type_ignores=[]),'actual_original_valid_ready','exec'),env);ready=env['valid_ready']
 captured=read(R/'ACTUAL_REWARD_STARTUP_CURRENT_AND_ORIGINAL_ERROR_TEXT_ACTUAL.json')
 row=next(json.loads(v)['row'] for k,v in captured['texts'].items() if k.endswith('/h1/NODE_CURRENT.json'))
 spec=read(P/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')['specs']['h1']
 cases=[]
 assert not ready(row,spec);cases.append(dict(case='actual_pair17_admission_schema_rejected',expected=False,actual=False))
 fixed=copy.deepcopy(row);fs=dict(spec,reward_migration=True);val=fixed['closed_source_CPU']['value'];val.update(kind='closed_same_backend_reward_migration',same_physics_assets_and_PPO_AST=True)
 fixed['closed_source_CPU']['SHA']=hashlib.sha256(json.dumps(val,indent=2).encode()).hexdigest()
 assert ready(fixed,fs);cases.append(dict(case='existing_original_reward_migration_contract',expected=True,actual=True))
 for name,mut in [('without_migration_spec',lambda r,s:s.pop('reward_migration')),('wrong_source',lambda r,s:s.update(source_SHA='unknown')),('wrong_GPU',lambda r,s:s.update(GPU_UUID='unknown')),('original_error',lambda r,s:r.update(original_error=True)),('missing_physics_proof',lambda r,s:r['closed_source_CPU']['value'].pop('same_physics_assets_and_PPO_AST')),('tampered_qualification_SHA',lambda r,s:r['closed_source_CPU'].update(SHA='bad')),('wrong_manifest',lambda r,s:r.update(manifest_SHA='bad'))]:
  r=copy.deepcopy(fixed);s=copy.deepcopy(fs);mut(r,s);assert not ready(r,s);cases.append(dict(case=name,expected=False,actual=False))
 put(R/'ORIGINAL_OWNER_REWARD_MIGRATION_ADMISSION_SCHEMA_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,cases=cases,original_loader=dict(path=str(B/'closed_step270_reward_path_source_CPU_v1.py'),SHA=H(B/'closed_step270_reward_path_source_CPU_v1.py')),new_loader=dict(path=str(loader),SHA=H(loader)),original_controller_SHA=H(P/'controllers/three_slot_common_v1.py'),original_controller_byteexact_no_account_or_PPO_change=True,actual_pair17_H1_no_GO=True,local_wrong_node_basename_read_error='three_slot_node_v1.py absent; actual source is three_slot_finite_node_v1.py; no helper or SSH ran from this failed local read'))
 # Preserve current full-pair collectors unused. This new finite closes only the actual E3 interval.
 collector=(P/'collect_pair_complete_finals_original_cost_bounded_once.py').read_text('utf8')
 collector=collector.replace("set(co['go'])=={'h1','recovery'}", "set(co['go'])=={'recovery'}")
 collector=collector.replace("metadata=json.loads((R/'PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert metadata['passed']", "retired=json.loads((N.parent/'H1_STEP270_REWARD_PATH_V1_20261022/reports/UNSTARTED_H1_ADMISSION_ORIGINAL_FINALLY_TERMINAL_ACTUAL.json').read_bytes());assert retired['passed'] and retired['no_H1_learning_GO_or_cost_interval']\n    assert retired['current_owner']['go']['recovery']['nominal_end_epoch']-time.time()<=900")
 for oldname,newname in [('PAIR_CLOSING_COLLECTOR_STARTED_ACTUAL','E3_ONLY_CLOSING_COLLECTOR_STARTED_ACTUAL'),('PAIR_CLOSED_SOURCE210_CANONICAL_COST_ACTUAL','E3_ONLY_CLOSED_SOURCE210_CANONICAL_COST_ACTUAL'),('PAIR_CLOSED_TARGET72_ACTUAL','E3_ONLY_CLOSED_TARGET72_ACTUAL'),('PAIR_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL','E3_ONLY_COMPLETE_FINAL_ORIGINAL_COST_RETURNED_ACTUAL'),('PAIR_CLOSING_ORIGINAL_ERROR_','E3_ONLY_CLOSING_ORIGINAL_ERROR_')]:collector=collector.replace(oldname,newname)
 ast.parse(collector);(P/'collect_actual_E3_only_after_unstarted_H1_terminal_bounded_once.py').write_text(collector,encoding='utf8')
 reviewer=(T/'E3_bridge_continuation_V8/review_actual_recovery_bridge_complete_model_original_cost_CPU_once.py').read_text('utf8').replace('TWO50_CURRENT_COHORT_COMPLETE_FINALS_ORIGINAL_COST_RETURNED_ACTUAL','E3_ONLY_COMPLETE_FINAL_ORIGINAL_COST_RETURNED_ACTUAL').replace('TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL','E3_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL')
 reviewer=reviewer.replace("report=dict(epoch=time.time(),passed=True,models=models", "report=dict(epoch=time.time(),passed=True,passed_scope=['E3_complete_checkpoint','E3_original_cost','unstarted_H1_and_all_nodes_out'],H1_learning_GO_absent=True,models=models")
 (P/'review_actual_E3_only_complete_model_original_cost_CPU_once.py').write_text(reviewer,encoding='utf8');ast.parse(reviewer)
 N=T/'H1_STEP270_E3_REWARD_PATH_PAIR_V18_20261022';assert not N.exists();N.mkdir();(N/'reports').mkdir();shutil.copytree(P/'controllers',N/'controllers')
 for name in ('deploy_pair_new_original_writer_bounded_once.py','collect_pair_first_actual_GO_positive_PPO_once.py','collect_pair_complete_finals_original_cost_bounded_once.py','review_pair_complete_models_original_cost_CPU_once.py','relocate_actual_closed_H1_forensics_peer_TLS_bounded_once.py'):shutil.copy2(P/name,N/name)
 cfg=read(P/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json');cfg.update(sequence=18,cohort_id=N.name,previous_stage_dir=str(P),owner_root='/mnt/mod4_linux_durable_20261013/H1step270_rewardmigration_2210v18/owner',roots=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_rewardmigration_2210v18/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_rewardmigration_2210v18/recovery'))
 put(N/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json',cfg)
 prep=(P/'prepare_pair_after_closed15_with_reward_path_CPU_once.py').read_text('utf8')
 a=prep.index(" receipt=read(P/'reports/PAIR_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json')");z=prep.index(" put('PAIR_LATEST_SOURCES_PREPARE_STARTED_ACTUAL.json'",a)
 prep=prep[:a]+''' receipt=read(P/'reports/E3_ONLY_COMPLETE_FINAL_ORIGINAL_COST_RETURNED_ACTUAL.json')
 e3proof=read(P/'reports/E3_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json')
 prior=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V15_20261022'
 h1proof=read(prior/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
 oldq=read(P/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
 h1q=read(prior/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
 retired=read(T/'H1_STEP270_REWARD_PATH_V1_20261022/reports/UNSTARTED_H1_ADMISSION_ORIGINAL_FINALLY_TERMINAL_ACTUAL.json')
 assert retired['passed'] and retired['no_H1_learning_GO_or_cost_interval']
 assert receipt['actual_finite_transport_returned'] and e3proof['passed'] and e3proof['H1_learning_GO_absent'] and e3proof['all_owner_nodes_children_actual_out'] and e3proof['original_canonical_cost_settled'] and e3proof['all_original_private_shared_locks_free']
 assert h1proof['passed'] and h1proof['all_owner_nodes_children_actual_out'] and h1proof['original_canonical_cost_settled']
 proof=dict(e3proof,models=dict(h1=h1proof['models']['h1'],recovery=e3proof['models']['recovery']))
 assert proof['remaining_actual_snapshot']>82512.86069250107
''' +prep[z:]
 prep=prep.replace("spec=dict(oldq['specs'][key]);oldAdam=spec['source_Adamstep']", "spec=dict(oldq['specs'][key]);oldAdam=spec['source_Adamstep'];previous_root=h1q['roots']['h1'] if key=='h1' else oldq['roots'][key]")
 prep=prep.replace("base=Path(oldq['payloads'][key])", "base=Path(h1q['payloads']['h1'] if key=='h1' else oldq['payloads'][key])")
 prep=prep.replace("previous_runtime_root=oldq['roots'][key]", "previous_runtime_root=previous_root")
 prep=prep.replace("closed_step270_reward_path_source_CPU_v1.py", "closed_step270_reward_migration_owner_schema_source_CPU_v2.py")
 prep=prep.replace("  if key=='h1':\n", "  if key=='h1':\n   spec['reward_migration']=True\n",1)
 prep=prep.replace("source_parent_production_root=oldq['roots'][key]", "source_parent_production_root=previous_root")
 # Qualification for H1 is the genuine pair15 complete model, never an invented pair17 FINAL.
 prep=prep.replace("for name,value in [('QUALIFIED_RUNTIME_BASE_MANIFEST.json',oldm),(proofname,proof)", "for name,value in [('QUALIFIED_RUNTIME_BASE_MANIFEST.json',oldm),(proofname,h1proof if key=='h1' else proof)")
 prep=prep.replace("  for p in (N/'controllers').glob('*.py')", "  if key=='h1':\n   (dest/'OWNER_REWARD_MIGRATION_SCHEMA_CPU_ACTUAL.json').write_text((T/'H1_STEP270_REWARD_PATH_V1_20261022/reports/ORIGINAL_OWNER_REWARD_MIGRATION_ADMISSION_SCHEMA_CPU_ACTUAL.json').read_text('utf8'),encoding='utf8')\n  for p in (N/'controllers').glob('*.py')")
 prep=prep.replace("spec.update(previous_runtime_root=previous_root", "spec.update(previous_runtime_root=previous_root")
 (N/'prepare_pair_after_actual_E3_closed_with_original_reward_migration_CPU_once.py').write_text(prep,encoding='utf8');ast.parse(prep)
 deploy=(N/'deploy_pair_new_original_writer_bounded_once.py').read_text('utf8')
 needle=" put('H1_CLOSED_SAME_STEP270_PHASE_PRODUCTION_CPU_ADMITTED_ACTUAL.json',admitted)"
 addition="""
 owner_ready=d.code(c,d.t.PY,"from pathlib import Path;import sys,json;sys.path.insert(0,v['root']);from three_slot_common_v1 import valid_ready;q=v['admitted'];s=v['spec'];row=dict(key='h1',phase='ready',closed_source_CPU=q,manifest_SHA=s['manifest_SHA'],original_error=False);assert s['reward_migration'] and valid_ready(row,s);print(json.dumps(dict(passed=True,original_valid_ready_actual_CPU=True,kind=q['value']['kind'],controller_unchanged=True)))",dict(root=root,spec=spec,admitted=admitted),timeout=60)
 put('H1_INSTALLED_ORIGINAL_OWNER_REWARD_MIGRATION_VALID_READY_CPU_ACTUAL.json',owner_ready)
"""
 assert deploy.count(needle)==1;deploy=deploy.replace(needle,needle+addition)
 # Additional fresh check of the failed, unstarted pair17 H1 before any new install.
 deploy=deploy.replace("def install_h1(c,q):\n", "def install_h1(c,q):\n failed=d.code(c,d.t.PY,\"from pathlib import Path;import json,psutil,os;p=Path(v['root']);e=json.loads((p/'NODE_EXIT_ACTUAL.json').read_bytes());assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and e['terminal_received_by_source'];assert not (p/'GO_PRODUCTION.json').exists();assert not any(x.pid!=os.getpid() and any(a.startswith(str(p)+'/') for a in x.info['cmdline'] or []) for x in psutil.process_iter(['pid','cmdline']));print(json.dumps(dict(passed=True,failed_H1_unstarted_allout=True)))\",dict(root='/mnt/mod4_linux_durable_20261013/H1step270_rewardpath_2210v17/h1'),timeout=60)\n put('FAILED_UNSTARTED_PAIR17_H1_FRESH_ALLOUT_ACTUAL.json',failed)\n")
 (N/'deploy_pair_new_original_writer_bounded_once.py').write_text(deploy,encoding='utf8');ast.parse(deploy)
 files=[dict(path=str(p),SHA=H(p)) for p in N.rglob('*.py')]
 put(R/'PAIR18_ORIGINAL_REWARD_MIGRATION_SCHEMA_REPAIR_UNUSED_WORKFLOW_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,files=files,new_stage=str(N),no_future_source_prepared_remote_Task_or_GO=True,current_pair17_H1_no_GO_not_FINAL=True,E3_current_learning_untouched=True,original_common_owner_node_PPO_account_unchanged=True))
 print(json.dumps(dict(schema_CPU_cases=len(cases),reserved=str(N),no_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put(R/('ADMISSION_SCHEMA_REPAIR_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc()));raise
