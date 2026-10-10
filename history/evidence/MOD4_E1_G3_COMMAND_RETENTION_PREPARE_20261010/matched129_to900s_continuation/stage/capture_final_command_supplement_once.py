"""New stage Git metadata then one ordinary supplement for saved receipts only."""
from pathlib import Path
import hashlib,json,os,shlex,subprocess,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=W/'polar-rl-train';H=lambda b:hashlib.sha256(b).hexdigest()
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';B='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],encoding='utf8').strip()
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
def main():
 stage=json.loads((R/'EPISODE_STAGE_GIT_RECORDED.json').read_bytes());assert stage['remote_main_tag_peeled_verified'] and not stage['push_pending']
 assert not git('diff','--cached','--name-only') and not git('status','--porcelain')
 save('COMMAND_FINAL_SUPPLEMENT_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-MATCHED-SCUT-128-POST-STAGE-REPORTS-01',stage=stage,no_new_trial_or_learning=True,continue_existing_objects_if_push_pending=True))
 dest=P/'history/evidence'/D.name/'final_formal_and_monitor_supplement';assert not dest.exists();dest.mkdir(parents=True)
 ip=dest/'REPORT_CAPTURE_INDEX.json';known=set();known_large=set();prior=[]
 for q in (P/'history/evidence').rglob('*CAPTURE_INDEX*.json'):
  try:v=json.loads(q.read_bytes())
  except (ValueError,UnicodeDecodeError):continue
  for x in v.get('reports_and_implementation',[]):
   if x.get('source') and x.get('sha256') and x.get('Git_path'):known.add((x['source'],x['sha256']));prior.append(x)
  for x in v.get('large_originals_index_only',[]):
   if x.get('source') and x.get('sha256'):known_large.add((x['source'],x['sha256']))
 index=dict(reports_and_implementation=[],large_originals_index_only=[],prior_identical_reports_reused=[])

 sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
 files=[];new=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  b=p.read_bytes();source=str(p.resolve());h=H(b)
  if (source,h) in known or (source,h) in known_large:
   index['prior_identical_reports_reused'].append(dict(source=source,bytes=len(b),sha256=h,prior_index_exact=True));continue
  if p.suffix.lower() in ('.npz','.pt','.zip','.usd','.npy') or len(b)>50000000 or ('remote_evidence' in p.parts and len(b)>2000000):
   index['large_originals_index_only'].append(dict(source=source,bytes=len(b),sha256=h,index_only=True,original_retained=True));continue
  if p.suffix.lower() not in ('.py','.json','.md','.txt','.yaml','.yml','.log') and 'remote_evidence' not in p.parts:continue
  clean,n=redact(b.decode('utf8'));raw=clean.encode();out=dest/'post_stage'/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists();out.write_bytes(raw);assert redact(clean)[0]==clean
  gp=out.relative_to(P).as_posix();files.append(gp);new.append(dict(source=source,bytes=len(b),sha256=h,Git_path=gp,archived_bytes=len(raw),archived_sha256=H(raw),capture='redacted_full' if n else 'byteexact_full',source_encoding='utf8',redactions=n,post_stage_supplement=True))
 for q in R.glob('SCOPE_ARTIFACTS_COLLECTED_*.json'):
  v=json.loads(q.read_bytes());index['large_originals_index_only'].extend(dict(source=x['path'],bytes=x['bytes'],sha256=x['sha256'],index_only=True,original_retained=True) for x in v['files'] if x.get('index_only') and x.get('sha256'))
 for q in R.glob('CANDIDATE_129_COLLECTED_*.json'):
  v=json.loads(q.read_bytes());index['large_originals_index_only'].extend(dict(source=x.get('source',x.get('path')),bytes=x['bytes'],sha256=x['sha256'],index_only=True,original_retained=True) for x in v['files'] if x.get('large_original_index_only'))
 assert new
 index['reports_and_implementation'].extend(new);index['post_stage_supplement']=dict(epoch=time.time(),all_saved_current_reports_accounted=True,stage_commit=stage['commit'],files=len(new),remote_verification_tool_output_not_new_report=True);ip.write_bytes(json.dumps(index,ensure_ascii=False,indent=2).encode());files.append(ip.relative_to(P).as_posix())
 subprocess.run(['git','-C',str(P),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(x.encode() for x in files)+b'\0',check=True,capture_output=True)
 git('commit','-m','Record command retention actual fullsave, preserved refusals, raw indices and monitor receipts')
 run=subprocess.run(['git','-C',str(P),'push','origin','HEAD'],capture_output=True,text=True,encoding='utf8',errors='replace')
 if run.returncode:
  save('COMMAND_FINAL_PUSH_ERROR.json',dict(epoch=time.time(),commit=git('rev-parse','HEAD'),stdout=run.stdout,stderr=run.stderr,continue_original_objects_only=True));raise RuntimeError('Push pending; do not repeat committed supplement')
 tag=stage['tag'];r=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines());head=git('rev-parse','HEAD')
 assert r['refs/heads/main']==head and r['refs/tags/'+tag]==stage['tagobject'] and r['refs/tags/'+tag+'^{}']==stage['commit']
 tracked=set(git('ls-tree','-r','--name-only','HEAD').splitlines())
 for x in index['reports_and_implementation']:
  assert x['Git_path'] in tracked and H((P/x['Git_path']).read_bytes())==x['archived_sha256']
 assert not git('status','--porcelain')
 print(json.dumps(dict(supplement_commit=head,stage_commit=stage['commit'],tag=tag,tagobject=stage['tagobject'],remote_main_tag_peeled_verified=True,push_pending=False,total_reports=len(index['reports_and_implementation']),post_stage_reports=len(new),all_saved_D_L_reports_Git_accounted=True,UTF8_verified=True,own_formal_and129_stage_only_actual_reports=True,no_replay_or_budget_extension=True,new_budget_seconds=0)))
if __name__=='__main__':
 try:main()
 except Exception:
  p=R/'COMMAND_FINAL_SUPPLEMENT_ERROR.json'
  if not p.exists():p.write_bytes(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_executed_mutations=True),indent=2).encode())
  raise
