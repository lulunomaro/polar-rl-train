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
 stage=json.loads((R/'STAGE_GIT_RECORDED.json').read_bytes());assert stage['remote_main_tag_peeled_verified'] and not stage['push_pending']
 assert not git('diff','--cached','--name-only') and not git('status','--porcelain')
 save('POST_STAGE_SUPPLEMENT_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-MATCHED-SCUT-128-POST-STAGE-REPORTS-01',stage=stage,no_new_trial_or_learning=True,continue_existing_objects_if_push_pending=True))
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  with c.open_sftp() as f:
   raw=(R/'STAGE_GIT_RECORDED.json').read_bytes()
   with f.open(E+'/reports/E1_G3_MATCHED_RETENTION_SCUT_128_GIT_RECORDED.json','wbx') as out:out.write(raw)
   assert f.open(E+'/reports/E1_G3_MATCHED_RETENTION_SCUT_128_GIT_RECORDED.json').read()==raw
  code=r'''from pathlib import Path
import hashlib,json,os,time
R=Path(REPORTS);B=Path(BUDGET);H=lambda b:hashlib.sha256(b).hexdigest();budget=B.read_bytes();j=json.loads(budget);assert j['authorized_training_seconds']==828000 and j['active_segment'] is None
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
receipt=json.loads((R/'E1_G3_MATCHED_RETENTION_SCUT_128_GIT_RECORDED.json').read_bytes());assert receipt['remote_main_tag_peeled_verified'] and not receipt['push_pending']
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);v['E1_G3_short_observation_execution_event']['matched_retention_SCUT_128_git_record']=dict(path=str(R/'E1_G3_MATCHED_RETENTION_SCUT_128_GIT_RECORDED.json'),commit=receipt['commit'],tag=receipt['tag'],tagobject=receipt['tagobject'],push_pending=False,remote_verified=True,later_reports_require_supplement=True)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.MatchedGit-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),stage_git_metadata_synced=True,master_RM_approval_tracks_canonical_bytes_preserved=True,current_before_SHA=H(before),current_after_SHA=H(raw),remaining_seconds=j['remaining_training_seconds'],new_budget_seconds=0)))
'''.replace('REPORTS',repr(E+'/reports')).replace('BUDGET',repr(B))
  compile(code,'<matchedGitSync>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');receipt=json.loads(raw);save('STAGE_GIT_METADATA_SYNCED.json',receipt)
  with c.open_sftp() as f:
   raw=(R/'STAGE_GIT_METADATA_SYNCED.json').read_bytes()
   with f.open(E+'/reports/E1_G3_MATCHED_RETENTION_SCUT_128_GIT_METADATA_SYNCED.json','wbx') as out:out.write(raw)
   assert f.open(E+'/reports/E1_G3_MATCHED_RETENTION_SCUT_128_GIT_METADATA_SYNCED.json').read()==raw
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
 dest=P/'history/evidence'/D.name;ip=dest/'REPORT_CAPTURE_INDEX.json';index=json.loads(ip.read_bytes());known={(x['source'],x['sha256']) for x in index['reports_and_implementation']}|{(x['source'],x['sha256']) for x in index['prior_identical_reports_reused']}
 sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
 files=[];new=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix.lower() not in ('.py','.json','.md','.txt','.yaml','.yml'):continue
  b=p.read_bytes();source=str(p.resolve());h=H(b)
  if (source,h) in known:continue
  clean,n=redact(b.decode('utf8'));raw=clean.encode();out=dest/'post_stage'/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists();out.write_bytes(raw);assert redact(clean)[0]==clean
  gp=out.relative_to(P).as_posix();files.append(gp);new.append(dict(source=source,bytes=len(b),sha256=h,Git_path=gp,archived_bytes=len(raw),archived_sha256=H(raw),capture='redacted_full' if n else 'byteexact_full',source_encoding='utf8',redactions=n,post_stage_supplement=True))
 assert new
 index['reports_and_implementation'].extend(new);index['post_stage_supplement']=dict(epoch=time.time(),all_saved_current_reports_accounted=True,stage_commit=stage['commit'],files=len(new),remote_verification_tool_output_not_new_report=True);ip.write_bytes(json.dumps(index,ensure_ascii=False,indent=2).encode());files.append(ip.relative_to(P).as_posix())
 subprocess.run(['git','-C',str(P),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(x.encode() for x in files)+b'\0',check=True,capture_output=True)
 git('commit','-m','Record paired E1 review Git metadata and final monitor receipts')
 run=subprocess.run(['git','-C',str(P),'push','origin','HEAD'],capture_output=True,text=True,encoding='utf8',errors='replace')
 if run.returncode:
  save('POST_STAGE_PUSH_ERROR.json',dict(epoch=time.time(),commit=git('rev-parse','HEAD'),stdout=run.stdout,stderr=run.stderr,continue_original_objects_only=True));raise RuntimeError('Push pending; do not repeat committed supplement')
 tag=stage['tag'];r=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines());head=git('rev-parse','HEAD')
 assert r['refs/heads/main']==head and r['refs/tags/'+tag]==stage['tagobject'] and r['refs/tags/'+tag+'^{}']==stage['commit']
 tracked=set(git('ls-tree','-r','--name-only','HEAD').splitlines())
 for x in index['reports_and_implementation']:
  assert x['Git_path'] in tracked and H((P/x['Git_path']).read_bytes())==x['archived_sha256']
 assert not git('status','--porcelain')
 print(json.dumps(dict(supplement_commit=head,stage_commit=stage['commit'],tag=tag,tagobject=stage['tagobject'],remote_main_tag_peeled_verified=True,push_pending=False,total_reports=len(index['reports_and_implementation']),post_stage_reports=len(new),all_saved_D_L_reports_Git_accounted=True,UTF8_verified=True,actual128_complete=True,new_learning_launched=False,new_budget_seconds=0)))
if __name__=='__main__':
 try:main()
 except Exception:
  p=R/'POST_STAGE_SYNC_OR_SUPPLEMENT_ERROR.json'
  if not p.exists():p.write_bytes(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_executed_mutations=True),indent=2).encode())
  raise
