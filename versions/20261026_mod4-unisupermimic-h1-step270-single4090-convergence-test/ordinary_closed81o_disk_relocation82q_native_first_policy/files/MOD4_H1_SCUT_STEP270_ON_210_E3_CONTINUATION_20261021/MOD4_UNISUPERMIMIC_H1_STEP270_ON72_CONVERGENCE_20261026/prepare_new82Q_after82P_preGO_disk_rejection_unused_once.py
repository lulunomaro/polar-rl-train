from pathlib import Path
import ast,hashlib,importlib.util,json,shutil,time
H=Path(__file__).resolve().parent;T=H.parent;P=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82P_20261026';N=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
read=lambda p:json.loads(Path(p).read_bytes());SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not N.exists();(N/'reports').mkdir(parents=True);(N/'preparation_exact_history').mkdir()
boundary=read(P/'reports/ACTUAL82P_PREGO_RESOURCE_BOUNDARY_AND_PARTIAL_CPU_OUTPUTS_RETURNED.json');assert boundary['actual_finite_returned'] and boundary['source210']['no82P_owner_node_GO_or_own_process'] and boundary['target72']['exact82P_partial_noNODE_noGO_actual_out']
space=read(H/'reports/CLOSED81O_FOR82Q_OLD80_79C_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json');assert space['passed'] and space['all_full_SHA_retained_on72'] and space['all_own_storage_processes_actual_out'] and space['source_above_original_disk25']
shutil.copytree(P/'reports',N/'preparation_exact_history/82P_reports_original_bytes');shutil.copytree(P/'controllers',N/'controllers');shutil.copytree(P/'payloads',N/'payloads',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
q=read(P/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');q['epoch']=time.time();q['owner_root']=q['owner_root'].replace('2610v82p','2610v82q')
for key in ('h1','recovery','e2'):
 out=N/'payloads'/key;prior=read(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');hist=out/'prebind82Q_exact_history';hist.mkdir()
 for name in ('THREE_SLOT_COMPLETE_MANIFEST_V1.json','job0/TASK.json'):shutil.copy2(out/name,hist/(Path(name).name+'.original_bytes.txt'))
 task=read(out/'job0/TASK.json');task['id']=N.name+'_'+key;(out/'job0/TASK.json').write_text(json.dumps(task,indent=2),'utf8')
 before={r['relative']:r for r in prior['files']};rows=[]
 for p in sorted(out.rglob('*')):
  if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
  rel=p.relative_to(out).as_posix()
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  digest=before[rel]['SHA'] if p.suffix in ('.pt','.npz','.usd','.stl') else SHA(p);rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=digest))
 prior['files']=rows;(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(prior,indent=2),'utf8');q['specs'][key]['manifest_SHA']=SHA(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');q['payloads'][key]=str(out);q['roots'][key]=q['roots'][key].replace('2610v82p','2610v82q')
 assert SHA(out/'same_optimized_source_contract_metadata_candidate_v1.py')=='c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e'
for name in ('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',):shutil.copy2(P/'reports'/name,N/'reports'/name)
(N/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').write_text(json.dumps(q,indent=2),'utf8')
for old,new in [('deploy_actual82p_checkpoint_context_fixed_H1_method_original_writer_unused_once.py','deploy_actual82q_checkpoint_context_fixed_H1_method_original_writer_unused_once.py'),('collect_actual82p_PPO_and_native_H1_policy_first_finite_unused_once.py','collect_actual82q_PPO_and_native_H1_policy_first_finite_unused_once.py')]:
 s=(P/old).read_text('utf8').replace(P.name,N.name).replace('82P_EXACT_SOURCE','82Q_EXACT_SOURCE').replace('MIXED82P_ACTUAL','MIXED82Q_ACTUAL');ast.parse(s);(N/new).write_text(s,'utf8')
s=(P/'e2_target72_same_backend_install_source_v1.py').read_text('utf8').replace('2610v82p/e2','2610v82q/e2');(N/'e2_target72_same_backend_install_source_v1.py').write_text(s,'utf8')
# Only the stale metadata label in original ready admission is renamed; charge_values is exact.
sp=importlib.util.spec_from_file_location('new_ready',N/'controllers/three_slot_common_v1.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
closed=read(P/'reports/H1_METHOD72_SOURCE_ORIGINAL_ACCOUNT_CPU_ADMITTED_ACTUAL.json');row=dict(key='e2',phase='ready',original_error=False,manifest_SHA=q['specs']['e2']['manifest_SHA'],closed_source_CPU=closed)
assert m.valid_ready(row,q['specs']['e2'])
for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py'):
 if name.endswith('common_v1.py'):
  extract=lambda p:ast.dump(next(x for x in ast.parse(p.read_text('utf8')).body if isinstance(x,ast.FunctionDef) and x.name=='charge_values'),include_attributes=False)
  assert extract(N/'controllers'/name)==extract(T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026/controllers'/name)
 else:assert (N/'controllers'/name).read_bytes()==(P/'controllers'/name).read_bytes()
w=(B/'same_authorized_session_compressed_transport_v133.py').read_text('utf8');needle="        'read_actual81o_failed_method_error_and_original_terminal_cost_unused_once.py',";assert needle in w
names=['deploy_actual82q_checkpoint_context_fixed_H1_method_original_writer_unused_once.py','collect_actual82q_PPO_and_native_H1_policy_first_finite_unused_once.py'];w=w.replace(needle,needle+'\n'+''.join('        '+repr(n)+',\n' for n in names),1);(B/'same_authorized_session_compressed_transport_v134.py').write_text(w,'utf8')
with (N/'reports/NEW82Q_AFTER82P_PREGO_DISK_WITH_ORIGINAL_READY_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_source_CPU_only=True,actual82P_targetSDK_and_nativeCPU_passed_before_H1_disk_guard_rejected=True,no82P_owner_GO_or_fee=True,actual_closed_NPZ5_retained_on72_and_duplicates_released=True,original25GiB_not_lowered=True,exact_candidate_v5_bridge_retained=True,original_charge_values_AST_and_owner_bytes_exact=True,original_valid_ready_with_renamed_current_healthy_source_metadata_passed=True,new82Q_actual_installed_checks_still_required=True,source_Adams={k:v['Adam'] for k,v in q['sources'].items()},nonfatal_three_backslash_S_ASTwarnings=True),f,indent=2)
print(json.dumps(dict(prepared82Q=True,no_GO=True,original_ready_CPU=True)))
