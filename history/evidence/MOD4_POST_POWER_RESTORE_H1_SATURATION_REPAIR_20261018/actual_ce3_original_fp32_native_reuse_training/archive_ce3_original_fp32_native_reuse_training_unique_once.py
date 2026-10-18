"""One technical continuation stage; never rerun record/tag after commit exists."""
from pathlib import Path
import json,time,hashlib,importlib.util,importlib,sys,traceback
B=Path(__file__).resolve().parent;R=B/'reports';N=B/'resumed_ce3_original_fp32_v1';REPO=B.parent/'polar-rl-train'
BASE='034e897588f91482065275e8085847d109d22dab';ID='ce3-original-fp32-native-reuse-training';TAG='trial-20261018-'+ID;TITLE='Resume ce3 H1 training using the original FP32 native audit'
DEST=REPO/'history/evidence'/B.name/'actual_ce3_original_fp32_native_reuse_training';NOTE=B/'CE3_ORIGINAL_FP32_REUSE_TRAINING_NOTE_UTF8.txt';MSG=B/'CE3_ORIGINAL_FP32_REUSE_TRAINING_TAG_UTF8.txt'
sp=importlib.util.spec_from_file_location('past_history_ordinary_functions_only',B/'append_original_training_config_history_reconciliation_ordinary_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);rawgit=m.git;H=m.H;TEXT=m.TEXT
def git(*args):
 if args[:2]==('tag','-a'):
  assert args[2]==TAG and args[3]=='-m' and args[4]==MSG.read_text(encoding='utf8');return rawgit('tag','-a',TAG,'-F',str(MSG))
 if args and args[0]=='push':return rawgit('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
 return rawgit(*args)
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists() and not NOTE.exists()
 dispatch=json.loads((N/'reports/CE3_ORIGINAL_FP32_SAME_SEGMENT_FINITE_DETACHED_ACTUAL.json').read_bytes());assert dispatch['Adam']==646100 and dispatch['native_reused_same_source_backend_GPU_no_replay']
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1375
 old=json.loads((REPO/'history/evidence'/B.name/'followup_original_human_training_config_history/REPORT_CAPTURE_INDEX.json').read_bytes());prior={r['sha256']:r for r in old['entries'] if r.get('Git_path')}
 note='Technical restoration of original formal H1 FP32 native audit and continuation from complete ce3 source. Human asked to proceed after original-chat research and specifically said the technical plan/audit flow was agent-driven; do not reframe agent implementation choices as human-authored parameters or repeatedly ask the same authorization. Continue the existing unstarted H1 finite task; no added budget, subject, automatic future window, reward/LR/STD/action/CAD/physics threshold change. Original FP32 absolute1e-4 all3.6Mpolicy/14.4Mphysical audit passed, strict dualFP64false and old failednode preserved independently. Complete native initial/final PT twohost199tensor105float/sourcecore9STD8critic17Adam646100 exact already verified, no native GPU/oldPT/raw replay or rehash. New reuse validator source/backend/GPU/Adam/runtime/assets/SDK/source CPU proof bound with positive+13negative CPU tests. Original four common/owner/resource/production worker bytes unchanged, newnode only uses exact native proof then original finite production. Copy original TASK historical bytes separately; actual newTASK fixes inherited645140/pending labels without changing old originals. Fresh72 selectedGPU24203MiBfree, RAM/durable>originalguards, old P2 success and cq failednode actualout, private/shared realfcntl free before newroot. Source D actually mounted, oldowner81434 identityout/COHORT_FINAL goempty/cost0, canonicalNone/two original realfcntlFree, port29754 available and current budget checked before originalwriter102842/listener/signedE2E3holdACK/node19262. New namespace H1cr_1810p3 only, source metadata owner not210GPU admission. Actual GO originalowner102842/create1792308138.14 at1792308141.9455233; target productionworker19267/create1792308143.47 on72GPU0 UUID16828f91, no native worker. Original cap1800/headroom300/max24/start25GiB/free8GiB completeupdate savedstop and oneoriginalwriter actualintervalonce1188000seconds retained. E2/E3 preGO reviewholds0worker/GO/charge. Initial/source models loaded exact, immutablefirst/FINAL only if actual collection and whole local CPU report says pass, no presumed progress from PID or schedule. Same bounded collector exact creationargv only while alive owns210/72/249transport; rootlocalCIM/reports only, no extraSSH/Git-hostconnection/watcher. Remote finite chain independent of laptop/hourly. Prepared futurefinalcollector uses actual newdispatch owner rather than old81434 and only missingFINAL/model/cost/out/locks; final frozen helper prepares a newsource independent native120/full1500 later, no reused old ce3 case or automatic nexttraining. All original contracts/ancestorfalse/unknown/CPU_FP32notbitexact/sourceSDKnotbinary/authorednotcookedShape kept. Same hourly mod4-10 updated actual technical continuation, old pending reference question retired by newer proceed instruction, no repeated approval framing. All new source/reports/local lookup miss/workorder/appreceipt/CIM/errors captured; large PT/asset/raw only prior or new actual producer path-size-SHA index, partial deferred. One unique record/tag only, poststage receipt ordinary, pushfail existingobjects only; no archival runtime/account mutation.'
 for p,s in ((NOTE,note),(MSG,TITLE+'\n\n'+note)):
  with p.open('x',encoding='utf8') as f:f.write(s)
 known={str(Path(r['source_path']).resolve()):dict(bytes=r['bytes'],SHA=r['sha256'],provenance='prior complete Git index') for r in old['entries'] if r.get('sha256') and Path(r['source_path']).suffix.lower() not in TEXT}
 for mf in B.rglob('*MANIFEST*.json'):
  v=json.loads(mf.read_bytes())
  for row in v.get('files',[]):
   if not isinstance(row,dict) or not row.get('relative') or not row.get('SHA'):continue
   p=mf.parent/row['relative']
   if p.is_file() and p.suffix.lower() not in TEXT:known[str(p.resolve())]=dict(bytes=row['bytes'],SHA=row['SHA'],provenance=str(mf))
 for p in B.rglob('*COLLECTION_ACTUAL.json'):
  v=json.loads(p.read_bytes())
  for key in ('models','downloaded_models','downloaded_final_models','files'):
   for row in v.get(key,[]):
    if row.get('twohost_complete_SHA') and row.get('local_path'):known[str(Path(row['local_path']).resolve())]=dict(bytes=row['bytes'],SHA=row['SHA'],provenance=str(p))
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];captured=0;deferred=[]
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial not complete'));continue
  if p.suffix.lower() not in TEXT:
   r=known.get(str(p.resolve()))
   if r is None:deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='No existing producer hash; no archival rehash'));continue
   assert p.stat().st_size==r['bytes'];rows.append(dict(source_path=str(p.resolve()),bytes=r['bytes'],sha256=r['SHA'],capture='actual_large_index_only',index_provenance=r['provenance'],original_retained=True));continue
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in prior:
   r=prior[sha];rows.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='existing_complete_Git_SHA_reference',Git_path=r['Git_path'],archived_sha256=r['archived_sha256'],redaction_count=r.get('redaction_count',0),redaction_reason=r.get('redaction_reason'),original_retained=True));continue
  try:txt=raw.decode('utf8');enc='utf8'
  except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
  safe,n=redact(txt);archived=safe.encode(enc) if n else raw;dst=DEST/p.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(archived);rel=dst.relative_to(REPO).as_posix();r=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=rel,archived_bytes=len(archived),archived_sha256=H(dst),byte_preserving_decode=enc,redaction_count=n,redaction_reason='Capture only credential redaction; original retained' if n else None,original_retained=True);rows.append(r);prior[sha]=r;files.append(rel);captured+=1
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,new_texts=captured,actual_technical_continuation_not_human_authored_implementation=True,no_GPU_or_account_mutation_for_archive=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','repair','--note-file',str(NOTE),'--files',*files,'--validation','Strict original FP32 native reuse positive plus13 negatives; fresh resource/actual original canonical and locks handoff; production actualGO independent finite cap. Complete first and final CPU only as recorded, original dualFP64false retained.','--push'];rec.main();head=git('rev-parse','HEAD');obj=git('rev-parse',TAG)
 v=m.m.u.u.old.prev.prev.prev.prev.g.n.m.cap.a;v.gitio.g=rawgit;v.verify(rows,tags,head,TAG,obj);assert len(git('tag','--list').splitlines())==1376
 print(json.dumps(dict(commit=head,tag=TAG,object=obj,remote_main_tag_peeled_all1375_old_tags_and_tracked_SHA_verified=True,total_tags=1376,entries=len(rows),new_texts=captured,deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CE3_ORIGINAL_FP32_UNIQUE_GIT_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_only_push_existing_objects_no_repeat_record_tag_GPU=True),f,indent=2)
  raise
