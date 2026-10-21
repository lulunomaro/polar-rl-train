from pathlib import Path
import ast,hashlib,json,shutil,time
T=Path(__file__).resolve().parent;P=T/'H1_STEP270_E3_PAIR_V1_20261021';N=T/'H1_STEP270_E3_PAIR_V2_20261022'
assert not N.exists();(N/'reports').mkdir(parents=True);shutil.copytree(P/'controllers',N/'controllers')
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,text):
    ast.parse(text);(N/name).write_text(text,encoding='utf8',newline='\n')
cfg=dict(sequence=2,cohort_id=N.name,previous_stage_dir=str(P),previous_actual_run_id='H1_STEP270_RECOVERY_ORIGINAL_1792597123349933700',owner_root='/mnt/mod4_linux_durable_20261013/H1step270_joint_2210v2/owner',roots=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_joint_2210v2/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_joint_2210v2/recovery'))
(N/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json').write_text(json.dumps(cfg,indent=2),encoding='utf8')
PREP='''from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 cfg=read(N/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json');P=Path(cfg['previous_stage_dir'])
 receipt=read(P/'reports/PAIR_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json')
 proof=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
 oldq=read(P/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
 assert receipt['actual_finite_transport_returned'] and proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out'] and proof['all_original_private_shared_locks_free']
 assert set(proof['models'])=={'h1','recovery'} and proof['remaining_actual_snapshot']>82512.86069250107
 put('PAIR_LATEST_SOURCES_PREPARE_STARTED_ACTUAL.json',dict(epoch=time.time(),no_GO=True))
 rec=read(P/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json')
 rec.update(remaining_after=proof['remaining_actual_snapshot'],derived_current_cohort_source_cost_receipt_only=True,legacy18_pending_not_reconciled_again=True,source_current_cohort_original_cost_summary=proof)
 put('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)
 payloads={};specs={};sources={}
 for key in ('h1','recovery'):
  base=Path(oldq['payloads'][key]);dest=N/'payloads'/key;assert not dest.exists();shutil.copytree(base,dest)
  oldm=read(base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');model=proof['models'][key];final=model['final'];source=Path(final['local_path'])
  assert final['twohost_complete_SHA'] and source.stat().st_size==final['bytes']
  spec=dict(oldq['specs'][key]);oldAdam=spec['source_Adamstep']
  spec.update(previous_runtime_root=oldq['roots'][key],previous_exit_kind='node',source_SHA=final['SHA'],source_Adamstep=model['Adam'],closed_production_continuation=True,reuse_completed_native=False)
  shutil.copy2(source,dest/'job0/source'/spec['source_filename'])
  if key=='h1':
   shutil.copy2(T/'closed_step270_same_phase_production_source_CPU_v1.py',dest/'closed_production_continuation_CPU_v2.py')
   shutil.copy2(T/'target_H1_step270_closed_source_sdk_cpu_review_v1.py',dest/'target_H1_step270_closed_source_sdk_cpu_review_v1.py')
   proofname='CURRENT_ORIGINAL_PAIR_CLOSED_MODELS_COST_CPU_ACTUAL.json'
  else:
   worker=dest/'recovery_worker.py';text=worker.read_text('utf8');needle='{'+str(oldAdam)+'+20*updates}';assert text.count(needle)==1
   worker.write_text(text.replace(needle,'{'+str(model['Adam'])+'+20*updates}'),encoding='utf8')
   proofname='CURRENT_ORIGINAL_COHORT_CLOSED_COST_CPU_ACTUAL.json'
  for p in (N/'controllers').glob('*.py'):shutil.copy2(p,dest/p.name)
  task=read(dest/'job0/TASK.json')
  (dest/'PREVIOUS_TASK_METADATA_HISTORICAL.json').write_text(json.dumps(task,indent=2),encoding='utf8')
  task.update(id=cfg['cohort_id']+'_'+key,GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],source_SHA=final['SHA'],source_Adamstep=model['Adam'],source_H1_actual_latest_Adamstep=model['Adam'] if key=='h1' else None,source_parent_production_root=oldq['roots'][key],source_policy_hz=spec['policy_hz'],policy_hz=spec['policy_hz'],source_owned_updates=model['updates'],source_owned_completed_updates=model['updates'],exact_closed_source_updates=model['updates'],same_clock_complete_source_no_native_replay=True,explicit_step270_task_migration=False if key=='h1' else task.get('explicit_step270_task_migration',False),same_step270_phase_complete_continuation=key=='h1')
  (dest/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
  for name,value in [('QUALIFIED_RUNTIME_BASE_MANIFEST.json',oldm),(proofname,proof),('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',rec)]:
   (dest/name).write_text(json.dumps(value,indent=2),encoding='utf8')
  prior={x['relative']:x for x in oldm['files']};rows=[]
  for p in sorted(dest.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   rel=p.relative_to(dest).as_posix()
   sha=(final['SHA'] if rel=='job0/source/'+spec['source_filename'] else prior[rel]['SHA']) if p.suffix in ('.pt','.npz','.usd','.stl') else H(p)
   rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=sha))
  m=dict(oldm,source_SHA=final['SHA'],source_Adamstep=model['Adam'],files=rows,closed_step270_samephase_continuation=key=='h1')
  (dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),encoding='utf8')
  spec['manifest_SHA']=H(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');payloads[key]=str(dest);specs[key]=spec
  sources[key]=dict(SHA=final['SHA'],bytes=final['bytes'],Adam=model['Adam'],updates=model['updates'],path=final['path'])
 q=dict(epoch=time.time(),passed=True,payloads=payloads,specs=specs,sources=sources,roots=cfg['roots'],owner_root=cfg['owner_root'],previous_owner_root=read(P/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['owner_root'],both_latest_complete_model_CPU_original_cost_allout=True,no_native_or_query_replay=True,no_remote_Task_or_GO_yet=True)
 put('TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json',q)
 print(json.dumps(dict(prepared=True,sources=sources,no_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('PAIR_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_or_GO=True));raise
'''
write('prepare_pair_from_actual_closed_pair_CPU_once.py',PREP)
old=(P/'deploy_pair_new_original_writer_bounded_once.py').read_text('utf8')
start=old.index("H1_INSTALL=r'''");end=old.index('\ndef main():',start)
replacement='''H1_INSTALL=d.INSTALL.replace("key=='e2'", "key=='h1'").replace("key!='e2'", "key!='h1'").replace("assert int(line.split(',')[-1])>7000", "assert int(line.split(',')[-1])>15669")
H1_INSTALL=H1_INSTALL.replace("assert not B.exists();B.mkdir", """
mount=subprocess.check_output(['findmnt','-n','-o','UUID,FSTYPE,OPTIONS','--target',str(owned)],text=True).strip()
assert 'EF3105C85DD986BD' in mount.upper() and 'ntfs3' in mount and 'rw' in mount.split()[-1].split(',')
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());previous_owner=Path(v['previous_owner'])
assert c['active_segment'] is None and c['authorized_training_seconds']==1548000 and len(c['budget_extensions'])==8 and c['remaining_training_seconds']>82512.86069250107
assert json.loads((previous_owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled'] and json.loads((previous_owner/'COHORT_FINAL.json').read_bytes())['original_cost_settled']
assert not any(p.pid!=os.getpid() and any(x.startswith(str(previous_owner)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
for lock in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert not B.exists();B.mkdir""")
def install_h1(c,q):
 spec=q['specs']['h1'];root=q['roots']['h1'];local=Path(q['payloads']['h1'])
 manifest=json.loads((local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
 result=d.code(c,d.t.PY,H1_INSTALL,dict(root=root,spec=spec,manifest=manifest,source=q['sources']['h1'],previous_owner=q['previous_owner_root']),timeout=120)
 put('H1_FRESH_RESOURCE_UNUSED_ROOT_SOURCE_INSTALL_ACTUAL.json',result)
 sf=c.open_sftp();sf.get_channel().settimeout(90)
 try:
  for row in result['need_upload']:sf.put(str(local/row['relative']),root+'/'+row['relative'])
  sf.put(str(local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),root+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 finally:sf.close()
 cpu=d.code(c,d.t.PY,"import runpy,sys;sys.argv=['target_H1_step270_closed_source_sdk_cpu_review_v1.py',v['root']];runpy.run_path(v['root']+'/target_H1_step270_closed_source_sdk_cpu_review_v1.py',run_name='__main__')",dict(root=root),timeout=240)
 put('H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json',cpu)
 admitted=d.code(c,d.t.PY,"from pathlib import Path;import sys,json;sys.path.insert(0,v['root']);from closed_production_continuation_CPU_v2 import load;print(json.dumps(load(v['spec'],Path(v['root']))))",dict(root=root,spec=spec),timeout=90)
 put('H1_CLOSED_SAME_STEP270_PHASE_PRODUCTION_CPU_ADMITTED_ACTUAL.json',admitted)
'''
new=old[:start]+replacement+old[end:]
new=new.replace('both_installed_source_CPU_and_H1_actual_native_query_reuse=True','both_installed_source_CPU_and_H1_samephase_closed_continuation=True')
write('deploy_pair_new_original_writer_bounded_once.py',new)
for name in ('collect_pair_first_actual_GO_positive_PPO_once.py','collect_pair_complete_finals_original_cost_bounded_once.py','review_pair_complete_models_original_cost_CPU_once.py'):
 shutil.copy2(P/name,N/name);ast.parse((N/name).read_text('utf8'))
rows=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in N.rglob('*') if p.is_file()]
report=dict(epoch=time.time(),source_AST_reserved_only=True,no_future_model_source_prepared=True,no_remote_Task_or_GO=True,requires_both_actual_complete_models_CPU_cost_allout=True,controller_bytes_exact=all(H(p)==H(P/'controllers'/p.name) for p in (N/'controllers').glob('*.py')),samephase_H1_closed_loader_reserved=True,source_files=rows)
with (T/'reports/PAIR_V2_RESERVED_SAMEPHASE_WORKFLOW_SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(reserved=str(N),files=len(rows),no_models_or_GO=True)))
