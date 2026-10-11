"""One annotated real Wave repair/training stage; old objects and failures stay intact."""
from wave_io import *
import subprocess,importlib
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'))
import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';BASE=REPO/'history/evidence'/D.name
DEST=BASE/'disk_cache_repair_and_wave1800s_started'
ID='wave35-disk-cache-repaired-isolated1800s-training-started'

def main():
 assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only')
 assert not gitio.g('tag','--list','*'+ID) and not DEST.exists()
 assert json.loads((R/'WAVE_STARTUP_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 assert json.loads((R/'WAVE_MONITOR_ACTUAL_VERIFIED.json').read_bytes())['status']=='ACTIVE'
 proof=json.loads(sorted(R.glob('WAVE_OWN_ACTIVE_SCHEMA_CPU_ACTUAL_[0-9]*.json'))[-1].read_bytes());assert proof['passed'] and proof['actual_updates_observed']>0
 previous=gitio.refs();save('WAVE_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=gitio.g('rev-parse','HEAD'),old_tags=len(previous)))
 note=R/'WAVE35_EXPOSURE_REPAIR_STARTED_STAGE_REPORT.md';assert not note.exists()
 note.write_text('''# Independent Wave35 duration-only repair, disk blockage resolved and actual PPO started

Approved terrain-subexpert revision004 and human +100h bounded-retraining revision005 apply. The new independent root is /home/egde/rl_candidates/MOD4_S3_E1_WAVE35_EXPOSURE_REPAIR_20261011, source368: all366 inherited source bytes preserved plus one administrative005 budget/source guard and one unique controller. Warmstart is complete reviewed129 source364 model32063 SHA3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e,17615538bytes,CPU102. OldWave3662b4, CURB7b and other unqualified/discard weights are not warmstarts or save/optimizer targets.

OldWave366 full training trace144controls=1.44s/environment, gentle speed maximum about.3m/s and nominal maximum integral.432m contrasted with the full ten-wave route2.406422727m. That motivates a testable exposure hypothesis, not a causal proof. Old131 forward22/27 reverse25/27 and all seven valid unfinished prefixes remain unqualified; no altered approach/window reclassification or geometry increase. The sole behavioral axis is one1800s bounded learning exposure window, including load-learn-save-exit. The same35mm G3 geometry, reset, command resampling12–16s, physical20s episode, plane30/20/20/15/15 families, rewards, LR1e-4 adaptive, KEEPSTD1, allD0D7, hardware,100Hz control/2.5ms physics×4/TGS32-4/35actor38critic6actions remain unchanged. New independent output and sourcefreeze do not cover or update E0/CURB/SLOPE/other experts. SDK/native/small128×2/big20k×4/clock/DR/startup evidence already passed in this same mathematical scope, exact source/result SHA reused with no replay or new45minclock.

First new CPU stage was rejected before root creation or GPU at a resource guard: systemdisk free2491256832bytes below12GiB, while full source/restore prerequisites passed. Actual cache audit identified reproducible pip HTTP downloads. A separate resolved-path/regular-file/no-symlink/older7days/no-active-installer operation removed2393 download cache files totaling12428217450bytes; full path-size-SHA receipts retained, free space14924308480bytes afterward. No experiment artifacts, weights, raw traces, installed environment, training source or canonical ledger were removed. Original rejection, duplicate immutable local decision rejection, read-path/PowerShell parser errors and premature required health-file reader error/source remain. Independent continuations completed only unexecuted CPU/root or read-only work; no old once, main, GPU or budget transaction replay.

Unique parent2886947-start88071197 and actual child2887012-start88071309 were dispatched at2026-10-11 21:32+08. The child performs20k environments,24controls/update,seed20260928 and save_interval25. Own sameG3/samecommand full actor/critic/std/optimizer/allD0D7/globalnamed/dictprivateCPUCUDA startup, disk roundtrip and saved-source episode+1 strictly verified. This is not PhysX exact resume. An active own PID-bound saved snapshot has13 actual PPO updates,312controls,6.24M environment steps,9 changed actor tensors and optimizerstepdelta260,CPU102/source368. These facts prove actual learning; an active snapshot is not formal final, final PASSED, behavioral acceptance or graduation. The first CLOCK_TRAINING_HEALTH report can legally be pending until an event or600controls; original reader prematurely assuming its presence is preserved, the independent reader changes only schema handling. All own saved source/startup/current report bytes or actual large artifact indices are captured.

Original parent alone accounts load/learn/save/exit in sole canonical0051188000s330h, seven extensions including the previously registered100h. No new extension, clearactive, copying, duplicate charge or tail replay. Closure2mm ordinary-env reset/PPO, mimic.01/nonfinite/unknown/missingcallback/coverage ownSTOP_AFTER_SAVE, original ground1e-6/contact1N/COMlink/hardware/fullsignedcircle tolerances retained. Termination overlap counts cannot be summed as unique truncations. Natural saved-review-ready/parentguardianchild exit/two actualfcntl locks free/unique closed ledger form a lesson review boundary, not global completion or fault.

Candidate142 queue/job/result number was verified unused on both hosts before dispatch. Parent can publish four new frozen cases only after its own fullsave/CPU/sourcefreeze/PID/PASSED and unique closed segment. The future complete four-case review must match original terrain initialization, full ten waves/two-wheel200mm rear support and all root30q/parameters/recipes/assignments6000callbacks/actualground-contact-integral COMlink hardware, both directions and standing, ordinary/truncation coverage, full signed circles along/cross/dedrift and every effective failure/unfinished prefix; retain original strictfalse. No further PPO/50mm or qualifiedWave/E1/RM/MoE/permanent-antiforgetting claim before actual complete decision. E0, accepted CURB20 and SLOPE5/8/10 ranges remain frozen; gate is untrained, hardware uncalibrated, S8 needs later specific approval. Human WASD player is untouched.

New dispatch and own active startup central metadata CAS were completed; master/approval/tracks/RM bytes preserved and canonical never written by metadata. Existing mod4-10 same-target hourly ACTIVE heartbeat updated and actual TOML/prompt verified, healthy pending silent with meaningful-change notifications only. All saved failures, sources, CPU/readers/schema, cache receipts, dispatch, startup, metadata and monitor evidence recorded or sameSHA existing Git referenced; large weights/NPZ/USD/ZIP/raw kept at actual path-size-SHA, credentials excluded. This stage records training started and repair progress, not finished capability. Later final/142/sync/monitor/Git receipts require ordinary supplements. Push failure continues original objects without new record/tag/commit.
''',encoding='utf8')
 prior={}
 for p in (REPO/'history/evidence').rglob('*CAPTURE_INDEX.json'):
  data=json.loads(p.read_bytes())
  for row in data.get('entries',[]):
   if row.get('Git_path') and row.get('archived_sha256'):prior[row['sha256']]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir();rows=[];files=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();sha=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
  if sha in prior:
   ref=prior[sha];assert H((REPO/ref['Git_path']).read_bytes())==ref['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
  elif p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip') or len(raw)>8000000:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:txt=raw.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:txt=raw.decode('latin1');encoding='latin1_byte_preserving'
   clean,n=redact(txt);data=clean.encode('utf8') if n else raw
   out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name)
   row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=n)
  rows.append(row)
 p=DEST/'REPORT_CAPTURE_INDEX.json';p.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,all_saved_success_failure_reader_source_metadata_monitor_receipts_captured=True,large_originals_retained=True,credentials_excluded=True,later_results_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(p.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');original=rec.git
 def short_git(*args):
  if args[:2]==('add','--'):
   q=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),capture_output=True,check=True);return q.stdout.decode().strip()
  return original(*args)
 rec.git=short_git
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Repair Wave disk blockage and start independent1800s exposure training','--kind','training','--note-file',str(note),'--files',*files,'--validation','Actual new source368 CPU102/sourcefreeze/sameG3-command fullCPUCUDA restore-diskroundtrip-episode+1 verified. Own PID-bound active snapshot13PPO updates312controls6.24Msteps/9changedactor tensors/optimizerdelta260; final and142 behavior pending. Old failures and exact reused SDK-native-PPO-clock receipts retained; disk pip HTTP download cache only reclaimed, no trial/weight/environment/canonical changes. Central metadata and same hourly heartbeat actual verified; no old GPU/once/budget replay.','--push']
 try:rec.main()
 except BaseException:save('WAVE_STAGE_RECORD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_original_objects_only=True));raise
 tag='trial-20261011-'+ID;head=gitio.g('rev-parse','HEAD');obj=gitio.g('rev-parse',tag)
 remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
 tracked=set(gitio.g('ls-files').splitlines())
 for row in rows:
  if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 save('WAVE_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,all_current_saved_reports_tracked_exact=True,old_tags_preserved=len(previous),new_capture_files=len(files)))
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,new_files=len(files),same_SHA_refs=sum(x['capture']=='same_SHA_existing_Git_reference' for x in rows),largeindices=sum(x['capture']=='large_actual_path_size_SHA_index_only' for x in rows))))

if __name__=='__main__':main()
