"""Only after complete80 closure: exact producer-indexed small journal cases, no original raw/PT."""
from pathlib import Path
import hashlib,importlib.util,json,os,re,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import hashlib,json,os,stat
B=Path(v['root']).resolve();out=[]
for a in v['artifacts']:
 p=Path(a['path']);assert p.resolve().parent==B and not p.is_symlink()
 st=p.stat();assert stat.S_ISREG(st.st_mode) and st.st_nlink==1 and st.st_size==a['bytes']
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 assert h.hexdigest()==a['SHA']
 again=p.stat();assert (st.st_ino,st.st_dev,st.st_size,st.st_mtime_ns)==(again.st_ino,again.st_dev,again.st_size,again.st_mtime_ns)
 out.append(dict(a,inode=st.st_ino,device=st.st_dev,mtime_ns=st.st_mtime_ns,source_full_SHA_matches_existing_producer=True))
print(json.dumps(dict(epoch=__import__('time').time(),files=out,only_immutable_new80_small_journal_cases=True,no_original_raw_model_GPU_policy_or_physics=True)))
'''
try:
 proof=json.loads((R/'THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
 diag=proof['models']['h1']['landing_event_journal_diagnostic'];value=diag.get('value') or {}
 if not diag.get('complete_control_row_coverage_valid'):
  put('CLOSED80_LANDING_JOURNAL_SMALL_CASES_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),status='OPTIONAL_JOURNAL_NOT_VALID_NO_BINARY_READ',diagnostic=diag,not_a_model_or_skill_failure=True));sys.exit(0)
 assert value['case_cap']==64 and value['cases_started']<=64
 root='/mnt/mod4_linux_durable_20261013/H1step270_three_experts_2610v80/h1/job0/production/control_prefix_raw';artifacts=[]
 for case in value['cases']:
  if not case['versions']:continue
  a=case['versions'][-1];assert a['path'].startswith(root+'/') and re.fullmatch(r'landing_event_case_\d{4}_through_\d+\.npz',Path(a['path']).name)
  assert a['last_control']==case['controls'][-1] and a['recorded_frames']==len(case['controls'])<=81
  artifacts.append(dict(a,case_id=case['case_id'],env_id=case['env_id'],episode=case['episode'],landing_control=case['landing_control'],closed_reason=case['closed_reason']))
 assert len({a['path'] for a in artifacts})==len(artifacts)<=64
 U=T/'H1_STEP270_CLOSED80_LANDING_JOURNAL_READONLY_20261026';assert not U.exists();U.mkdir()
 put('CLOSED80_LANDING_JOURNAL_SMALL_CASES_CPU_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,producer_cases=artifacts,scope='Only producer-indexed80 optional CPU landing trajectories; not full raw/PT or frozen evaluation'))
 if artifacts:
  sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
  sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
  c=route.connect()
  try:
   source=d.code(c,route.PY,CODE,dict(root=root,artifacts=artifacts),timeout=120);sf=c.open_sftp();files=[]
   try:
    for a in source['files']:
     p=U/Path(a['path']).name;sf.get(a['path'],str(p));assert p.stat().st_size==a['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==a['SHA'];files.append(dict(a,local_path=str(p),twohost_full_SHA=True))
   finally:sf.close()
  finally:c.close()
 else:source=dict(files=[],no_landing_cases_or_no_versions=True);files=[]
 put('CLOSED80_LANDING_JOURNAL_SMALL_CASES_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),status='COMPLETE_EXACT_SMALL_DERIVED_CASES_RETURNED',files=files,source=source,original_index=value,no_original_raw_PT_policy_GPU_physics_or_account_action=True,not_fullcallback_replay_or_frozen_skill_graduation=True))
 print(json.dumps(dict(small_closed80_landing_cases_returned=len(files),no_original_raw_or_model=True)))
except BaseException as error:
 if isinstance(error,SystemExit) and error.code==0:raise
 put('CLOSED80_LANDING_JOURNAL_SMALL_CASES_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_rerun_or_training_mutation=True));raise
