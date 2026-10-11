from direction_io import *
import subprocess
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as old
REPO=W/'polar-rl-train';DEST=REPO/'history/evidence'/D.name;ID='curb20-episode-entry-direction-scope-started'
def capture():
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 assert not DEST.exists();DEST.mkdir(parents=True);rows=[];files=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=H(raw))
  if p.suffix.lower() in ('.npz','.npy','.pt','.pth','.usd','.zip') or len(raw)>8000000:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:t=raw.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:t=raw.decode('latin1');encoding='latin1_byte_preserving'
   clean,count=redact(t);data=clean.encode('utf8') if count else raw;out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);name=out.relative_to(REPO).as_posix();files.append(name)
   row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=count)
  rows.append(row)
 p=DEST/'REPORT_CAPTURE_INDEX.json';p.write_bytes(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_reports_sources_errors_metadata_monitor_captured=True,large_originals_preserved=True,credentials_excluded=True,later_saved_reports_require_ordinary_supplement=True),ensure_ascii=False,indent=2).encode());files.append(p.relative_to(REPO).as_posix());return rows,files
def main():
 assert not old.g('status','--porcelain') and not (R/'STAGE_GIT_RECORDED.json').exists();previous=old.refs();assert not old.g('tag','--list','*'+ID)
 save('DIRECTION_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=old.g('rev-parse','HEAD'),old_tags=len(previous)))
 note=R/'STAGE_REPORT.md';assert not note.exists()
 note.write_text('''# Independent CURB20 episode-entry command direction repair started

Human requested finishing the repair and starting retraining. Complete139 source410 remains unqualified (up23/27,down27/27), four valid incomplete prefixes and all original false/raw/cost retained. New isolated direction scope keeps old410 bytes, original20mm geometry/entry/standing/DR/reward/LR/hardware/clock/family quotas. Only actualCURB command sign is bound once per physical episode to the actual legal reset entry relative to authored cell bounds. Original absolute random velocity and random draws remain exact; no liveposition/yawcorrection or teacher/truth input. New command state has a separate checkpoint dictionary and full assignment/entry/episode identity. Warmstart remains full129 source3643c97, not failed410/discard.

CPU component against actual20000-entry map (2820CURB,17180nonCURB), original random/standing/speed, selected episode/reset, strict wrongassignment/entry rejection and diskrestore passed. Actualsource actor9 including distribution.std_param +critic8=17 independent tensors and alloriginaloptimizer/DR/RNG validated. The original reader incorrectly assumed model_state_dict then16tensors; both errors preserved. Originalsource420 remains CPU-only, noGPU/main. Source421 preserves420 bytes plus schema reader; exclusive sourcefreeze write refused before any GPU, literal-substitution syntax refusal and metadata newline pre-CAS syntax error retained. Independent actual-schema read-only admission and uploaded-only CAS completed; validators and activity were not hotpatched or relaxed.

Unique source421 controller actually dispatched. New10env300controlSDK admitted actualCURB command range; new20knative24warm120timed needed because command axis changed. Actual own later receipts determine pass/progress. Complete128x2 and20kx4 PPO discard preflights then independentfresh20k0control0PPO strictsameCURBentrydirection fullCPUCUDA/alloldstreams/savedepisode+1 restore precede one300s formal load-learn-save-exit/save25/local15sguardian. Clock/DR/geometry reuse bySHA, no45min clock or any oldonce rerun. No automatic extra block/highergeometry before four new candidate140 matched actual behavior cases. Candidate140 twohostjobs/centralqueue/results unused verified beforedispatch. Gate untrained/E0,SLOPE frozen/Wave,CURB isolated/WASDuntouched.

Sole005 canonical1188000s330h, seven extensions and seventh100h already applied, no newextension/clear/recharge/copiedledger. CPU/SDK/native/fresh0PPO do not charge; eachPPO loadlearnsaveexit originalparent unique accounting. Source410 actualfullsave/PASSED/alloldprocessesgone/twofcntl locksfree/idle boundary checked before newauthority. Current new scope own held locks are expected, nodual20k or signals.

Same mod4-10 heartbeat ACTIVEhourly retained; prompt updates current source421 and pending/formal boundaries, quiethealthy/pending. Central metadata references ownactualCPU/dispatch/state and preserves historicalmaster/approval/tracks/RM, never writesbudgetledger. All current saved errors/source/CPU/dispatch/physical snapshots/metadata/monitor/workorder captured; weights/rawNPZ/USD/ZIP only actualpath-size-SHA, originals retained, credentials excluded. LaterPPO/fresh/formal/candidate/final/monitor/Gitreceipts require ordinary supplements. Pushfailure continues original objects only.
''',encoding='utf8')
 rows,files=capture();p=subprocess.run([sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Start independent CURB20 episode entry command direction repair','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Actual source421 CPU admitted and uniquecontroller dispatched; original410 SHA preserved; originalCPU/schema/exclusivewrite/preCASsyntax errors retained. ActualSDK10 direction scope PASSED; later native/PPO/formal own receipts authoritative. Exact fullsource3c97; newdirection state independent; no reward/hardware/clock/DR change or budgetextension. Samehourlyheartbeat actualverified; centralactualmetadata synced; all savedcurrentreports captured and largeactualoriginals indexed.','--push'],capture_output=True,text=True,encoding='utf8',errors='replace')
 if p.returncode:save('DIRECTION_STAGE_RECORD_ERROR.json',dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,continue_existing_objects_only=True));raise RuntimeError('Inspect actual original record objects')
 tag,head=p.stdout.strip().splitlines()[-1].split();obj=old.g('rev-parse',tag);remote={x.split()[1]:x.split()[0] for x in old.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
 save('STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,old_tags_preserved=len(previous),captured_files=len(files)))
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,captured_files=len(files),indexed_sources=len(rows))))
if __name__=='__main__':main()
