"""Unique annotated stage captures all current reports/errors; no training replay."""
from pathlib import Path
import hashlib,json,sys,time,subprocess,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(REPO/'archive_tools'));import record_experiment as record
from capture_history import redact
H=lambda b:hashlib.sha256(b).hexdigest()
ID='e1-curb20-fullstate-errors-preserved-and-formal300s-started'
TAG='trial-20261011-'+ID
OUT=REPO/'history/evidence/MOD4_E1_CURB20_FORMAL_DISPATCH_REVIEWED_20261011'
def git(*args):
 v=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8');assert v.returncode==0,v.stderr;return v.stdout.strip()
def main():
 assert not (R/'FORMAL_REVIEWED_STAGE_GIT_STARTED.json').exists() and not git('tag','--list',TAG)
 assert not git('status','--porcelain')
 (R/'FORMAL_REVIEWED_STAGE_GIT_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),unique_new_stage=True,tag=TAG,no_original_tag_replay=True),indent=2))
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
 actual=json.loads(sorted(R.glob('FORMAL_REVIEWED_ACTUAL_[0-9]*.json'))[-1].read_bytes())
 index=dict(epoch=time.time(),entries=entries,all_current_local_saved_reports_and_sources_captured=True,complete83MB_native_raw_context_index_only=True,actual_stage_root=actual['root'],actual_phase=actual['reports']['E1_STATE.json']['phase'],old_failed_raw_false_cost_preserved=True,weights_binary_are_indices_only=True,source_checkpoint_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',canonical_authorized_seconds=828000,new_budget_seconds=0)
 (OUT/'REPORT_CAPTURE_INDEX.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf8')
 note='Independent CURB20 fresh-process own fullstate resume repair and bounded formal deployment, revision004.\n\nSource384 actually completed4 PPO updates/96controls/1.92Menvsteps/384callbacks, healthordinary/integrity/unknown0/nonfinitefalse/STOPnone and a CPU102 fullsaved checkpoint7f1. Postlearning validation then called a fresh-environment-only restore in the stepped environment; original action_delay stepcounter0 guard rejected it. Original error/false/fullcheckpoint/raw/unique291.510988474s and parent/guardian/child actual exit remain; no oldfailed record is changed to pass. Earlier380 preload viewfailure210.317s, smallPASSED25.1108s, stdlib dispatch rejection and all reader/prewrite errors remain.\n\nNew386 preserves every384 sourcebyte and adds only a fresh-process restore-only probe and an isolated controller. Actual installed zero-step guard remains strict. CPU checks complete savedCURB102 and probe main has no step/learn/update. In an independently created fresh20k environment the probe restores own sameCURB full actorcriticstdoptimizer/allD0D7/globalnamed/privateCPUCUDA/terrain/command, CUDA diskroundtrip and sourceepisode+1; then fullsave with zero additional controls/PPO. Only actual PASS permits first300s formal from complete129 selected3c97, never discarded7f1. SDK/native/small/clock and already-completed big learning are exactreuse; no additional big PPO. Formal uses ownparent unique load-learn-save-exit budget; probe has no PPO/canonical write. The386 fresh process actually completed all8 fullrestore receipts/PID/source/episode+1 before optionalsave hit uninitialized rsl logger.writer. Independent388CPU admits actual384 fullsave and386 actualfullrestore together; originalprobe exitfailure/partialweights remainsfailed. A literal dispatch error on388 started preserved old restore-only main (zeroPPO), protected until naturalexit and retained as invalidrepeat. New389 only adds reviewedwrapper binding intendedmain and exactPopen entry, repeats noGPUpreflight, then formal300s. Actual latest report establishes pending/passed phase; no future claim.\n\nOwn fullsaved model is followed by133CURB/flat/spin/world complete/errorfree twohostJSON/fullNPZ/data-ground-contact-COMlink/hardware/signedcircle review. No automatic morePPO/height or qualifiedCURB/trueRM002/stairs/gate claim. E0 and unqualifiedWave are independent and protected; master/approval/tracks/RM003002001, clock/DR/LR/std/reward/hardware/plane30+20/20/15/15 unchanged; budgettotal828000/sixextensions once/new0. All saved text/code/errors/receipts/current snapshots/monitor/workorders captured, largeweights/raw onlyactualpathsizeSHA; poststage reports ordinarysupplement. Existing trialobjects unchanged.\n'
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
 sys.argv=['record_experiment.py','--id',ID,'--title','Independent CURB20 fullstate errors preserved and formal300s correctly dispatched','--kind','repair','--note-file',str(OUT/'REPORT.md'),'--validation','Actual CPU/native/small/PID/unique-ledger proofs and preserved pre-learning failure; new CUDA/formal/133 status only from own actual receipts','--files',*files,'--push']
 try:record.main()
 except BaseException:
  v=dict(epoch=time.time(),error=redact(traceback.format_exc())[0],existing_commit=git('rev-parse','HEAD'),existing_tag_object=git('rev-parse',TAG) if git('tag','--list',TAG) else None,do_not_record_recommit_or_retag=True,retry_original_objects_if_push_pending=True)
  (R/'FORMAL_REVIEWED_STAGE_GIT_ERROR.json').write_text(json.dumps(v,indent=2));raise
 v=dict(epoch=time.time(),commit=git('rev-parse','HEAD'),tag=TAG,tag_object=git('rev-parse',TAG),peeled=git('rev-parse',TAG+'^{}'),captured_files=len(files),large_or_binary_indices=sum(x['capture']=='actual_path_size_SHA_index_only' for x in entries),new_budget_seconds=0)
 remote=git('ls-remote','origin','refs/heads/main','refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines();found={x.split()[1]:x.split()[0] for x in remote}
 assert found['refs/heads/main']==v['commit'] and found['refs/tags/'+TAG]==v['tag_object'] and found['refs/tags/'+TAG+'^{}']==v['peeled']==v['commit']
 assert not git('status','--porcelain')
 v.update(remote_main_tag_and_peeled_verified=True,push_pending=False,all_report_index_entries_verified_from_actual_bytes=True)
 (R/'FORMAL_REVIEWED_STAGE_GIT_RECORDED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
if __name__=='__main__':main()
