from second_io import *
import subprocess,importlib
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';BASE=REPO/'history/evidence'/D.name;DEST=BASE/'reviewed_second1800s_started'
ID='wave35-reviewed-second-bounded-training-started'
def main():
 assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only') and not gitio.g('tag','--list','*'+ID) and not DEST.exists()
 proof=json.loads(sorted(R.glob('SECOND_OWN_STARTUP_CPU_ACTUAL_[0-9]*.json'))[-1].read_bytes());assert proof['passed'] and proof['actual_updates_observed']>0 and proof['actor_changed_tensor_count']>0
 assert json.loads((R/'SECOND_STARTUP_METADATA_SYNCED.json').read_bytes())['metadata_synced'] and json.loads((R/'SECOND_MONITOR_ACTUAL_VERIFIED.json').read_bytes())['status']=='ACTIVE'
 previous=gitio.refs();save('SECOND_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=gitio.g('rev-parse','HEAD'),old_tags=len(previous)))
 note=R/'SECOND_STAGE_REPORT.md';assert not note.exists()
 note.write_text(f'''# Reviewed second Wave35 bounded block actually learning

Human explicitly demanded action after the complete142 review had stopped at a work order. Approved004005 and the complete142 decision authorize exactly one additional1800s same-scope block. A new isolated root {ROOT} source369 preserves every368 source byte and adds one unique controller; no old main/resume/once was revived. CPU102 source is complete own368 model32160 SHA{SOURCE_SHA}/17615538B, reviewed142 forward25/27 reverse27/27. Two valid full15s unfinished forward env21/69 remain failures. Direct ancestral1293c97 source forward24/27 reverse27/27 and old366 forward22/27 reverse25/27 remain. Source368 negative4pi1/8 positive4pi4/8/world61/64 and all original strictfalse diagnostics are preserved, not claimed as E0 replacement or permanent antiforgetting. Own7f is a reviewed same-scope continuation only, not qualified Wave or another expert's default warmstart.

Actual old368 ownfullsave/PASSED/72snapshot+368freeze/PID2887012/unique1830.9085354804993s, parent/guardian/child exits, both realfcntl locks free, canonical-active and supervisor-active empty were independently verified. Original0051188000 seconds/seven registered extensions and actual remaining were read, no extension or budget transaction performed. All existing SDK/native/small128x2/big20kx4/sameG3samecommand fresh/startup/clock/DR evidence was exact path-size-SHA reused without GPU preflight or45minclock replay. Target CPU checked all369 source files, complete source state/independent actorcritic storage, source integrity, actual imported worker/Popen/output binding, sameG3samecommand runtime and CPU-noCUDA before unique dispatch. Old approval/master/tracks/RM bytes remain.

Parent2932881-start88740231 dispatched child2932922-start88740346 on2026-10-11 at23:23+08 into a distinct learning_logs root. Own full actorcritic/std/optimizer/allD0D7/globalnamed/dictprivateCPUCUDA restore, CUDA disk roundtrip and saved-source physicalepisode+1 passed strictly; terrainexacttrue, no geometry transition, predecessorcommandexacttrue, no new command scope. No PhysX exactresume claim. Actual own PID-bound snapshot proves {proof['actual_updates_observed']} PPO updates/{proof['actual_PPO_controls']} controls/{proof['actual_environment_steps']} environment steps, {proof['actor_changed_tensor_count']} actor tensors changed and optimizer stepdelta{proof['optimizer_step_delta']}; source checkpoint remains exact. These are active learning facts, not formal-final PASSED or behavior acceptance. Health can legally be event/600-control pending; future missing report is not physical failure.

One1800s load-learn-save-exit/save25/15s localguardian/20kenv/24control-update block, with originalparent unique canonical accounting, completes at most two blocks for this repair scope. New controller does not automatically start a third or increase35mm to50/70mm. Geometry35mm fulltenwaves2.406422727m/9m grid/.4m frozen approach/two-wheel200mm rear-support acceptance, reset/commands gentle±.3 yaw0 standing.2/resampling12–16s/physicalepisode20s/reward/LR1e-4adaptive/KEEPSTD1/allDR/hardware/plane30-20-20-15-15/2.5msx4 TGS32-4/100Hz/5msbin3history/35actor38critic6action unchanged. DR strength unchanged. E0, accepted CURB20 mirrored27/27 scope and SLOPE5/8/10 ranges frozen; gate untrained, hardware uncalibrated, S8 requires later approval,93/94paused and human WASD player untouched.

Actual both-host queue/result/jobs proved candidate143 unused before stage and dispatch. After ownfullsave/PASSED/CPU102/source369/snapshot/PID/unique closeout, parent publishes143-e1-wave35-second-bounded terrain/flat/spin/world. Full143 review must use complete JSON byteSHA/fullNPZ/root30q/parameters/recipes/assignment/6000callbacks/actual ground-contact integral COMlink hardware original tolerances, fulltenwaves before-support to two-wheel200mm after-support,1N contact vs position separately, standing26 not required to cross, all valid failed/pending prefixes and full signed circles alongcross/dedrift/left-right4pi/straight originalstrictfalse. Direct full pairing with142 and129 required. Full trainingtrace dynamic current-family semantics preserved; root/command proxies are not contact passage certificates. Sensor final dynamicbias observation is separate from unchanged static recipe/bounds; no fictional exact initial bias. If systematic residuals do not improve, stop this same-scope PPO and diagnose independently; do not blind third block or claim global MoE graduation.

Central dispatch and startup CAS completed, protected master/approval/tracks/RM exact, metadata never writes canonical. Same mod4-10 hourly ACTIVE heartbeat actually verified, meaningful changes only. Original next-root-not-deployed monitor preserved verbatim with SHA. Prepared read-only future final/collector/reviewer/trace readers do not claim future passes. PreGPU guessed missing reader paths and PowerShell quoting parser rejection are separately preserved; no remote action, physical failure or GPU replay resulted. All saved source, false/raw/cost/reader/schema, CPU/reuse/dispatch/startup/metadata/monitor evidence captured or exact old Git SHA referenced. Largeweights/rawNPZ/USD/ZIP actual path-size-SHA indices only, originals retained; credentials excluded. Later health/final/143/sync/monitor/Git receipts require ordinary supplements. Push failure continues original objects, never repeats record/tag/commit.
''',encoding='utf8')
 prior={}
 for p in (REPO/'history/evidence').rglob('*CAPTURE_INDEX.json'):
  for row in json.loads(p.read_bytes()).get('entries',[]):
   if row.get('Git_path') and row.get('archived_sha256'):prior[row['sha256']]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();sha=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
  if sha in prior:
   ref=prior[sha];assert H((REPO/ref['Git_path']).read_bytes())==ref['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
  elif p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip') or len(raw)>8000000:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:txt=raw.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:txt=raw.decode('latin1');encoding='latin1_byte_preserving'
   clean,n=redact(txt);data=clean.encode('utf8') if n else raw;out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name)
   row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=n)
  rows.append(row)
 p=DEST/'REPORT_CAPTURE_INDEX.json';p.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_evidence_captured=True,large_originals_retained=True,credentials_excluded=True,later_saved_results_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(p.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');original=rec.git
 def short_git(*args):
  if args[:2]==('add','--'):
   q=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),capture_output=True,check=True);return q.stdout.decode().strip()
  return original(*args)
 rec.git=short_git
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Start reviewed second bounded Wave35 training with actual full restore and PPO','--kind','training','--note-file',str(note),'--files',*files,'--validation','Actual source369/CPU102/sourcefreeze preserves368; reviewed142 selects7f. Oldfullsave/PASSED/exits/OSlocks/unique accounting actual boundary. Own full sameG3samecommand CPUCUDA restored, snapshot actor changes/positive optimizerdelta/PPO updates verified. No preflight or oldonce replay; second1800s only/no automaticthird. Central CAS and same hourly heartbeat actual verified. Future143 full behavior and own fulltrace remain pending, all original failures/diagnostics retained.','--push']
 try:rec.main()
 except BaseException:save('SECOND_STAGE_RECORD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_original_objects_only=True));raise
 tag='trial-20261011-'+ID;head=gitio.g('rev-parse','HEAD');obj=gitio.g('rev-parse',tag);remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
 tracked=set(gitio.g('ls-files').splitlines())
 for row in rows:
  if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 save('SECOND_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,old_tags_preserved=len(previous),saved_sources=len(rows),all_current_saved_reports_tracked_exact=True))
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,saved_sources=len(rows))))
if __name__=='__main__':main()
