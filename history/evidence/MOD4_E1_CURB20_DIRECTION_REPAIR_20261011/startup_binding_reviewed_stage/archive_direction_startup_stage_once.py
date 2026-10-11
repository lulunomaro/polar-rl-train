from direction_io import *
import subprocess
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as old
REPO=W/'polar-rl-train';BASE=REPO/'history/evidence'/D.name;DEST=BASE/'startup_binding_reviewed_stage';ID='curb20-direction-prelearn-startup-binding-repaired'
def capture():
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 prior={}
 for p in BASE.rglob('REPORT_CAPTURE_INDEX.json'):
  for r in json.loads(p.read_bytes())['entries']:
   if r.get('Git_path'):prior[(str(Path(r['source_path']).resolve()).casefold(),r['sha256'])]=r
 assert not DEST.exists();DEST.mkdir();rows=[];files=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();h=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=h);ref=prior.get((str(p.resolve()).casefold(),h))
  if ref:
   assert H((REPO/ref['Git_path']).read_bytes())==ref['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
  elif p.suffix.lower() in ('.npz','.npy','.pt','.pth','.usd','.zip') or len(raw)>8000000:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:t=raw.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:t=raw.decode('latin1');encoding='latin1_byte_preserving'
   clean,count=redact(t);data=clean.encode('utf8') if count else raw;out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name)
   row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=count)
  rows.append(row)
 p=DEST/'REPORT_CAPTURE_INDEX.json';p.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_results_errors_sources_proofs_monitor_sync_captured=True,large_originals_preserved=True,credentials_excluded=True,later_results_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(p.relative_to(REPO).as_posix());return rows,files
def main():
 assert not old.g('status','--porcelain') and not (R/'DIRECTION_STARTUP_STAGE_GIT_RECORDED.json').exists();previous=old.refs();assert not old.g('tag','--list','*'+ID)
 assert json.loads((R/'DIRECTION_STARTUP_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 save('DIRECTION_STARTUP_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=old.g('rev-parse','HEAD'),old_tags=len(previous)))
 note=R/'DIRECTION_STARTUP_STAGE_REPORT.md';assert not note.exists()
 note.write_text('''# CURB20 prelearning command-state binding failure preserved and isolated startup repair

Source421 SDK10 andnative20k newdirection scope completed healthy and independently validated actualtrace direction/standing/nonCURB contracts, all originaltolerances. Source421 small128 failed before anycontrol/PPO while writing manifest because newly introduced episode direction state had not yet been bound afterenvironmentinitialization. Originalassertion/error/crash/fullpartialsrcsnapshot and unique originalparent failedstartupcost remain false; actual parentguardianchild exited, locksfree/active-Sactive settled before newauthority. No physical failure or validator relaxation, nohotpatch/replay.

Newsource423 isolatedroot preserves421 allbytes and adds only a freshsmallworker that invokes existing_write_dynamic once beforemanifest/learning and a unique controller that exactlyreuses421 ownSDK/native results bySHA. No extrareset/randomdraw/newgeometry/plant/reward/LR/DR/hardware/clock. Direction mathematics/fullcheckpoint unchanged; source identity1293c97 fullactorcriticstdoptimizer/streams remains warmstart. Actual CPU import/main/Popen consistent, originalSDK/native children/results and previousfailed PID segment verified. Unique423controller dispatched, new small128x2 completePPO/PASSED/fullsave/48controls6144envsteps192callbacks; newbig20kx4 actualownstate/PASSED laterauthority. StrictfreshsameCURBentrydirection newprocess0control0PPO/seed20260928 then300s formal from3c97 required; discardedpreflight notformal source. No extraPPOblock/highergeometry beforecandidate140 matched fullroute and diagnostics review.

All saved source421 raw/error/snapshots/native fulltrace indices, source423CPU/stage/dispatch/small/currentbig/metadata/monitor and previousstageGitreceipt captured. OldsameSHA reports referenceoriginalGit paths; largecheckpoint/rawNPZ/USD/ZIP onlytruepathsizeSHA, originalsretained, credentials excluded. Samehourlyheartbeat updated423status; earlier421attn is history. Central protects historicalmaster/approval/tracks/RM and noledgerwrites. Sole005330h/sevenextensions originalparentchargesPPOloadlearnsaveexit once, noextension/recharge/clear. E0/SLOPE/Wave/CURB isolation andWASDuntouched, gateuntrained. Later fresh/formal/candidate reports ordinarysupplement.
''',encoding='utf8')
 rows,files=capture();p=subprocess.run([sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Repair CURB20 prelearning episode command state binding in isolated source423','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Actual421SDK10/native20k PASSEDexactSHA reused; originalsmall failedmanifest beforecontrol/PPO retained and originalparent uniquelysettled afteractualexits/locksfree. Source423 original421 allbytes preserved, onlynewsmall startup_write_dynamic beforemanifest plusnewcontroller. CPU/Popen actualpassed, small128x2 completePPO/PASSED, big/fresh/formal ownactual receipts laterpriority. No physical replay/clock/DR/reward/LR/hardware/budgetextension orhotpatch; samehourlymonitorverified/currentmetadata synced. Savedreports/errors/source/currentresults fullycaptured andlarge originalsindexed.','--push'],capture_output=True,text=True,encoding='utf8',errors='replace')
 if p.returncode:save('DIRECTION_STARTUP_STAGE_RECORD_ERROR.json',dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,continue_original_objects_only=True));raise RuntimeError('Inspect original record objects')
 tag,head=p.stdout.strip().splitlines()[-1].split();obj=old.g('rev-parse',tag);remote={x.split()[1]:x.split()[0] for x in old.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
 save('DIRECTION_STARTUP_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,old_tags_preserved=len(previous),captured_files=len(files)))
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,captured_files=len(files),indexed_sources=len(rows),same_SHA_references=sum(r['capture']=='same_SHA_existing_Git_reference' for r in rows))))
if __name__=='__main__':main()
