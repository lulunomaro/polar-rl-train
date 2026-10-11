"""Unique real stage, preserve all prior evidence and append only new SHA captures."""
from direction_io import *
import subprocess,importlib
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'))
import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';BASE=REPO/'history/evidence'/D.name
DEST=BASE/'complete140_exposure_matched900_stage'
ID='curb20-complete140-exposure-diagnosed-matched900s-started'

def main():
 assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only')
 assert not gitio.g('tag','--list','*'+ID) and not DEST.exists()
 assert json.loads((R/'EXPOSURE_MATCHED_DISPATCH_STARTUP_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 previous=gitio.refs();save('EXPOSURE_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=gitio.g('rev-parse','HEAD'),old_tags=len(previous)))
 note=R/'COMPLETE140_EXPOSURE_MATCHED_STAGE_REPORT.md';assert not note.exists()
 note.write_text('''# Complete CURB20 direction candidate140 and bounded exposure continuation

Candidate140 own423 e6df fullsaved checkpoint was collected actualcomplete/errorfree across fourcases, twohost8probe/result JSON byteSHAexact plus full180MB raw terrain SHA2c058c7a75ba2c4957cc7f06d8b7c324db23211a0fe889d54b6e9e71d8b4ea96. Full initial root30q/parameters/recipes/assignments/callback6000/ground-contact integral COMlink hardware original tolerances and all signed skill circles independently reviewed. Up23/27 down27/27, ordinary0, closure.658670149mm, declaredroute48/two reasoncoverageexact. Standing26 does not require traversal. Upward incomplete original-positive environments3/6/15/36 turn/lateral while a wheel remains before the curb; all valid15s/ordinary-before/truncation prefixes retained. Same count as139, three below132 source1293c97, no graduation. Negative4pi7→3/8 diagnostic decline kept, positive8/8/world64/64, direct signedstraight errors preserved; E0 remains frozen, gate untrained.

Full original423 saved commandtrace actual168controls=1.68s per environment, 2820CURB signed/standing sampling verified, entryrootoffsets.8/1.65m, unchanged.3m/s maximum nominal commanddistance.504m, actual roots show no center side change. Rootproxy is not a wheel/contact passage claim; insufficient training exposure is a testable hypothesis, not proven causal attribution. Trace prephysics commands and saved after-update histogram endpoint difference [[0,5,-5],[-4,0,4]] exactly reconciled. Original SHA/CK placeholder SyntaxErrors, PowerShell quoted repair rejection, incorrectsamephase histogram assertion and guessed absentresults directory were read/prewrite failures, retained with distinct source/error/report; no physics replay or validator relaxation.

New isolated root424 preserves all423 source bytes and adds one unique controller. Own423 e6df explicitly selected only for one sameCURB geometry/entry/direction 900s load-learn-save-exit exposure continuation; model remains unqualified. No geometry, speed/direction math, standing/random consumption, DR/reward/LR/hardware/clock changes. Previously passed SDK10/native20k/small128x2/big20kx4/freshsame20k0PPO/clock/geometry evidence exactSHA reused, never replayed. New CPU104 source ownership/admission and source freeze424 passed; old423 naturalparentguardianchildexit/twoactualfcntl-free locks/unique330.210305929s closed before newauthority. Actualparent2845157 andchild2845252, sourceE6 manifest, nine fullsame-scope startup/CUDA/episode+1 receipts verified. No automatic thirdblock or furtherPPO/highercurb before ownfinal/141 actual full matched review plus exposure audit. Future finalsave/141 may still be pending; active snapshots do not count as final. Candidate141 unused actualqueues/results/jobs checked before assignment, not published here.

Solecanonical0051188000s330h7extensions, old seventh100h already registered, no expansion/copy/clearactive/retail/recharge. Originalparent unique active PPOloadlearnsaveexit accounting continues including loading, guardian15s/save25. Historicalmaster/approval/tracks/RM protected; startup currentmetadata and samehourlyACTIVE heartbeat verified. E0/Wave/SLOPE/gate/player untouched. All saved reports/source/errors/false/raw/cost/metadata/monitor/priorGit receipts captured or sameSHA existingGit referenced. Weights/rawNPZ/USD/ZIP only realpath-size-SHA, originals retained, credentials excluded. Later ownfinal/141/sync/monitor/Git receipts require ordinary supplemental commits.
''',encoding='utf8')
 prior={}
 for p in BASE.rglob('*CAPTURE_INDEX.json'):
  for row in json.loads(p.read_bytes()).get('entries',[]):
   if row.get('Git_path') and row.get('archived_sha256'):
    assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256'];prior[row['sha256']]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir();rows=[];files=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();sha=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
  if sha in prior:
   ref=prior[sha];row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
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
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Review complete CURB140 and start one bounded same-scope exposure continuation','--kind','training','--note-file',str(note),'--files',*files,'--validation','Complete fourcase140/fullraw and actual shortformal command exposure reviewed; original failures preserved. New source424 exact423 bytes plusonecontroller; CPU104, oldactualexits/twoOSlocks/uniqueclosed, SDK/native/PPOpreflight/fresh/clock exactSHAreuse; actualnine same-scope CUDA/sourceepisode+1 startup verified,900s continuation only, ownfinal/141 still independently required. No geometry/reward/LR/hardware/oldonce/validator/budget/player changes. Samehourlymonitor and metadata actually verified, allsaved reports indexed.','--push']
 try:rec.main()
 except BaseException:
  import traceback;save('EXPOSURE_STAGE_RECORD_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),continue_original_objects_only=True));raise
 tag='trial-20261011-'+ID;head=gitio.g('rev-parse','HEAD');obj=gitio.g('rev-parse',tag)
 remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
 tracked=set(gitio.g('ls-files').splitlines())
 for row in rows:
  if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 save('EXPOSURE_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,all_current_saved_reports_tracked_exact=True,old_tags_preserved=len(previous),new_capture_files=len(files)))
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,new_files=len(files),same_SHA_refs=sum(x['capture']=='same_SHA_existing_Git_reference' for x in rows),largeindices=sum(x['capture']=='large_actual_path_size_SHA_index_only' for x in rows))))

if __name__=='__main__':main()
