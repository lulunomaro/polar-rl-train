"""Unique annotated stage captures all current reports/errors; no training replay."""
from pathlib import Path
import hashlib,json,sys,time,subprocess,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(REPO/'archive_tools'));import record_experiment as record
from capture_history import redact
H=lambda b:hashlib.sha256(b).hexdigest()
ID='e1-independent-curb20-fullstate-migration-repaired-and-learning-deployed'
TAG='trial-20261011-'+ID
OUT=REPO/'history/evidence/MOD4_E1_CURB20_FULL_STATE_PREPARE_20261011'
def git(*args):
 v=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8');assert v.returncode==0,v.stderr;return v.stdout.strip()
def main():
 assert not (R/'FULLSTATE_STAGE_GIT_STARTED.json').exists() and not git('tag','--list',TAG)
 assert not git('status','--porcelain')
 (R/'FULLSTATE_STAGE_GIT_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),unique_new_stage=True,tag=TAG,no_original_tag_replay=True),indent=2))
 entries=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();rel=p.relative_to(D).as_posix();entry=dict(source_path=str(p),bytes=len(raw),sha256=H(raw))
  if p.suffix.lower() in ('.pt','.npz','.npy','.usd','.usdc','.zip','.pyc') or len(raw)>50000000:
   entry.update(capture='actual_path_size_SHA_index_only',original_retained=True,reason='Binary original or complete large raw context snapshot; individual text reports captured in full')
  else:
   text=raw.decode('utf8');clean,count=redact(text);captured=clean.encode() if clean!=text else raw
   q=OUT/rel;assert not q.exists();q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(captured)
   entry.update(capture='redacted_text' if clean!=text else 'complete_exact_bytes',redactions=count,Git_path=q.relative_to(REPO).as_posix(),archived_bytes=len(captured),archived_sha256=H(captured))
  entries.append(entry)
 actual=json.loads(sorted(R.glob('ENVIRONMENT_VIEW_ACTUAL_[0-9]*.json'))[-1].read_bytes())
 index=dict(epoch=time.time(),entries=entries,all_current_local_saved_reports_and_sources_captured=True,complete83MB_native_raw_context_index_only=True,actual_stage_root=actual['root'],actual_phase=actual['reports']['E1_STATE.json']['phase'],old_failed_raw_false_cost_preserved=True,weights_binary_are_indices_only=True,source_checkpoint_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',canonical_authorized_seconds=828000,new_budget_seconds=0)
 (OUT/'REPORT_CAPTURE_INDEX.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf8')
 note='''Independent E1_CURB20 full-state migration and bounded learning deployment under human-approved revision004.

132 mirrored20mm frozen fullroute and source372 SDK/native are valid complete evidence and are reused exactly, with132 ascent26/27/descent27/27 and its incomplete valid prefix retained. Source364 full129 3c97 is selected; E0 and unqualified Wave weights are separate and protected. This is derived20mm curb, not actualRM002 heights, stairs, qualifiedCURB or trained gate.

New378 fullrestore scope was reviewed before launch; an inherited fullsave-validator adapter mismatch was detected statically and preserved, then an isolated380 validator was admitted. First dispatch used stdlib Python without torch and was rejected before launch; independent targetTorch dispatch succeeded. Small128x2 actual6144steps/192callbacks passed and is discarded/exactly reused. First380 big restore failed before learning because the source-identity view lacked actual ManagerTermBase num_envs/device properties. Its PID2429546 load/exit210.31723833084106s was settled once by its parent; no PPO update or own checkpoint occurred. Original .error.txt exists in root, not discard_logs; actual log/error-path review and prewrite guard rejection are retained alongside correction.

New384 preserves380 bytes and adds four isolated files. Source view now carries actual num_envs/device; CPU fixture uses installed manager properties and unchanged strict source assignment loader, checks original wrongassignment rejection, exact private RNG restoration, explicit newassignment binding and unchanged live env. Source102/independent ownership verified. Original loader/named schema, DR, hardware, reward, LR/std/clock/geometry/fivefamily allocation unchanged. SDK/native/clock/small are not repeated. New genuine384 CUDA big4iteration admission, sameCURB ownfullresume proof and subsequent only300s load-learn-save-exit are governed by actual receipts; future133 fourcase review is required before further PPO. The saved actual report determines current pending/completed status; deployment and data/health admission do not imply behavioral graduation.

All new local scripts, rejected/unused versions, CPU/schema failures, deployment receipts, original error/raw/false/cost, sourcefreeze/maps, readonly snapshots and annotation synchronization are captured or actual large-path-size-SHA indexed. Runtime and canonical are not changed for Git. Existing annotated trials remain; poststage generated reports require an ordinary supplement.''' 
 (OUT/'REPORT.md').write_text(note,encoding='utf8')
 files=[p.relative_to(REPO).as_posix() for p in OUT.rglob('*') if p.is_file()]
 # Use stdin pathspec for Git add so exact long Windows paths remain bounded.
 original_git=record.git
 def bounded_git(*args):
  if args and args[0]=='add' and args[1]=='--':
   v=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(x.encode() for x in args[2:])+b'\0',capture_output=True)
   if v.returncode:raise RuntimeError(v.stderr.decode(errors='replace'))
   return v.stdout.decode().strip()
  return original_git(*args)
 record.git=bounded_git
 sys.argv=['record_experiment.py','--id',ID,'--title','Independent CURB20 fullstate restoration repaired and bounded learning deployed','--kind','repair','--note-file',str(OUT/'REPORT.md'),'--validation','Actual CPU/native/small/PID/unique-ledger proofs and preserved pre-learning failure; new CUDA/formal/133 status only from own actual receipts','--files',*files,'--push']
 try:record.main()
 except BaseException:
  v=dict(epoch=time.time(),error=redact(traceback.format_exc())[0],existing_commit=git('rev-parse','HEAD'),existing_tag_object=git('rev-parse',TAG) if git('tag','--list',TAG) else None,do_not_record_recommit_or_retag=True,retry_original_objects_if_push_pending=True)
  (R/'FULLSTATE_STAGE_GIT_ERROR.json').write_text(json.dumps(v,indent=2));raise
 v=dict(epoch=time.time(),commit=git('rev-parse','HEAD'),tag=TAG,tag_object=git('rev-parse',TAG),peeled=git('rev-parse',TAG+'^{}'),captured_files=len(files),large_or_binary_indices=sum(x['capture']=='actual_path_size_SHA_index_only' for x in entries),new_budget_seconds=0)
 remote=git('ls-remote','origin','refs/heads/main','refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines();found={x.split()[1]:x.split()[0] for x in remote}
 assert found['refs/heads/main']==v['commit'] and found['refs/tags/'+TAG]==v['tag_object'] and found['refs/tags/'+TAG+'^{}']==v['peeled']==v['commit']
 assert not git('status','--porcelain')
 v.update(remote_main_tag_and_peeled_verified=True,push_pending=False,all_report_index_entries_verified_from_actual_bytes=True)
 (R/'FULLSTATE_STAGE_GIT_RECORDED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
if __name__=='__main__':main()
