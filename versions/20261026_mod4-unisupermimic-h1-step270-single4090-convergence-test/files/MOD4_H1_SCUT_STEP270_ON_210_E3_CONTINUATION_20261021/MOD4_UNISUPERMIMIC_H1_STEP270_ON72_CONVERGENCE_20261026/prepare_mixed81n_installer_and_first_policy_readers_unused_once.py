"""Exact new-task install/CPU dispatch; original owner charging and other slots untouched."""
from pathlib import Path
import ast
import json
import time

H=Path(__file__).resolve().parent;T=H.parent
A=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V81_20261026'
F=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81N_20261026'
code=r'''
from pathlib import Path
import fcntl,json,os,psutil,shutil,subprocess,time
B=Path(v['root']);s=v['spec'];old=Path(s['previous_runtime_root']);owned=Path('/home/lc01/Zonglin Li/zonglin2')
assert s['key']=='e2' and s['h1_step270_method_test'] and s['execution_backend']=='target72' and s['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
assert str(B)==str(owned/'tasks/H1step270_mixed_supermimic_2610v81n/e2') and str(old)==str(owned/'tasks/H1step270_three_experts_2610v80/e2') and B.resolve().is_relative_to(owned.resolve())
proof=v['closedproof'];assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['models']['h1']['final']['SHA']==s['source_SHA'] and proof['models']['h1']['Adam']==s['source_Adamstep'] and all(x['actual_cost']['duration_bound_passed'] for x in proof['models'].values())
e=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());r=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and r['terminal_all_own_children_waited'] and r['returncode']==0 and r['final']['passed'] and r['final']['final']['SHA']==proof['models']['e2']['final']['SHA']
failed=owned/'research/UNISUPERMIMIC_MOD4_WHEELLEG_TEST_20261026/e2';fe=json.loads((failed/'NODE_EXIT_ACTUAL.json').read_bytes());fr=json.loads((failed/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert fe['actual_all_own_children_waited'] and fe['validation_fcntl_released_if_acquired'] and fr['original_error'] and not (failed/'job0/production_STARTED_ACTUAL.json').exists()
assert not any(p.pid!=os.getpid() and any(a.startswith((str(old)+'/',str(failed)+'/')) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
for p in (Path(s['private_lock']),owned/'state/finite_environment_validation.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);assert not any(s['GPU_UUID'] in line for line in compute.splitlines())
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if s['GPU_UUID'] in x);assert int(line.split(',')[-1])>15669
assert not B.exists();B.mkdir(parents=True);before={r['relative']:r for r in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']};need=[];copied=0
for row in v['manifest']['files']:
 rel=row['relative'];dest=B/rel;source=old/rel;prior=before.get(rel);assert dest.resolve().is_relative_to(B.resolve());dest.parent.mkdir(parents=True,exist_ok=True)
 if prior and prior['SHA']==row['SHA'] and prior['bytes']==row['bytes'] and source.is_file() and not source.is_symlink() and source.stat().st_size==row['bytes']:
  shutil.copy2(source,dest);copied+=1
 else:need.append(row)
print(json.dumps(dict(epoch=time.time(),root=str(B),need_upload=need,source_files_reused=copied,GPU_line=line,durable_free=shutil.disk_usage(owned).free,explicit_H1_method_source80_crosshost_and_old_physical_E2_slot_closure=True,no_E2_policy_source_or_samebackend_H1_claim=True,no_GO_or_canonical_write=True)))
'''
(F/'e2_target72_same_backend_install_source_v1.py').write_text('"""Explicit new H1 method install, not the old E2 same-backend policy protocol."""\nCODE='+repr(code)+'\n','utf8')

s=(F/'deploy_actual_mixed81m_original_writer_unused_once.py').read_text('utf8')
needle=" with (NR/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)"
assert s.count(needle)==1
s=s.replace(needle," if name.startswith('E2_TWO50'):name=name.replace('E2_TWO50','H1_METHOD72',1)\n"+needle,1)
needle="  if source==expected:\n   assert args['root'] in (q['roots']['e2'],q['roots']['recovery']);source=source.replace('import runpy,sys;','import runpy,sys;sys.path.insert(0,v[\\'root\\']);',1)"
assert s.count(needle)==1
custom="""  if source==expected:
   assert args['root'] in (q['roots']['e2'],q['roots']['recovery'])
   if args['root']==q['roots']['e2']:
    source=\"from pathlib import Path;import contextlib,io,json,runpy,sys;B=Path(v['root']);sys.path.insert(0,str(B));buffer=io.StringIO()\\nwith contextlib.redirect_stdout(buffer):\\n sys.argv=['target_H1_step270_closed_source_sdk_cpu_review_v1.py',str(B)];runpy.run_path(str(B/'target_H1_step270_closed_source_sdk_cpu_review_v1.py'),run_name='__main__')\\n sys.argv=[str(B/'test_native_h1_goal_mdp_and_learner_CPU_v1.py')];runpy.run_path(sys.argv[0],run_name='__main__')\\ncpu=json.loads((B/'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json').read_bytes());cpu['new_native_H1_method_CPU']=json.loads((B/'reports/NATIVE_H1_GOAL_MDP_AND_LEARNER_CPU_V1_ACTUAL.json').read_bytes());print(json.dumps(cpu))\"
   else:source=source.replace('import runpy,sys;','import runpy,sys;sys.path.insert(0,v[\\'root\\']);',1)
  old_guard=\"from pathlib import Path;import json,sys;sys.path.insert(0,v['root']);from original_account_policy50_source_CPU import load;print(json.dumps(load(v['spec'],Path(v['root']))))\"
  if source==old_guard and args['root']==q['roots']['e2']:
   source=source.replace('from original_account_policy50_source_CPU import load','from closed_production_continuation_CPU_v2 import load',1)
""".rstrip()
s=s.replace(needle,custom,1)
s=s.replace("not_learning_until_actual_three_GO_PPO=True","not_learning_until_actual_PPO_and_native_policy_evidence=True")
ast.parse(s)
(F/'deploy_actual_mixed81n_H1_method_original_writer_unused_once.py').write_text(s,'utf8')

s=(A/'collect_three_experts81_same_V8_journal_first_PPO_finite_unused_once.py').read_text('utf8').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V81_20261026','H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81N_20261026')
needle="go=json.loads((B/'job0/GO_PRODUCTION.json').read_bytes());assert go['run_id']"
assert s.count(needle)==1
addition="method=None\nif v['key']=='e2':\n method=json.loads((B/'job0/production/FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json').read_bytes());startup=json.loads((B/'job0/production/ACTUAL_H1_NEW_METHOD_STARTUP_CONTRACT.json').read_bytes());assert method['policy_updates']>0 and method['world_updates']>0 and startup['actual_envs']==20000 and startup['physics_dt']==.0025 and startup['control_dt']==.01 and startup['actual_geometry']['height']==.27\n"
s=s.replace(needle,addition+needle,1)
s=s.replace("source_CPU=v['row']['closed_source_CPU'],latest_save=","native_H1_method_first_policy=method,source_CPU=v['row']['closed_source_CPU'],latest_save=",1)
s=s.replace('all_three_actual_GO_and_positive_PPO=True','H1_E3_actual_PPO_and_H1_method_native_policy_positive=True')
s=s.replace('THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json','MIXED81N_ACTUAL_GO_PPO_AND_NATIVE_POLICY_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json')
ast.parse(s)
(F/'collect_actual_mixed81n_PPO_and_H1_native_policy_first_finite_unused_once.py').write_text(s,'utf8')
with (H/'reports/MIXED81N_INSTALL_CPU_DISPATCH_AND_TYPED_FIRST_POLICY_SOURCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),custom_H1_test_install_only_selected_e2_slot=True,old80_physical_E2_slot_and_failed_method_V1_noGPU_actual_out_required=True,source_model_only_qualified80_H1_crosshost=True,real_H1_empty15669_RAM8_disk25_retained=True,source_perfile_reuse_SHA_bytes_containment_copyloop_retained=True,actual_fresh_target_H1_SDK_RSL_fullsource_CPU_and_native_tensor_learner_CPU_required=True,first_native_policy_not_mislabeled_PPO=True,H1_E3_source_and_original_controller_cost_unchanged=True,no_GO=True),f,indent=2)
print(json.dumps(dict(mixed81n_installer_and_typed_first_reader_prepared=True,no_GO=True)))
