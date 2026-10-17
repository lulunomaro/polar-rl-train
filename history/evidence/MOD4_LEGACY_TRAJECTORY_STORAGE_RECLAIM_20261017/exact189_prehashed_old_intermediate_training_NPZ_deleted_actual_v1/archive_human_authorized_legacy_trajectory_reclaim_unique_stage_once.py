"""Record this distinct, explicitly human-authorized cleanup stage exactly once."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import os,sys,time,json,hashlib,importlib.util,importlib,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';REPO=W/'polar-rl-train'
BASE='4f22fd8e1741fb0952fe890f9c66862a027c3f2a'
ID='human-authorized-old-intermediate-trajectory-space-reclaim'
TAG='trial-20261017-'+ID
TITLE='Reclaim 39.8GB of authorized obsolete training trajectories on source210'
DEST=REPO/'history/evidence'/B.name/'exact189_prehashed_old_intermediate_training_NPZ_deleted_actual_v1'
spec=importlib.util.spec_from_file_location('previous_archive_pure_helpers',W/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/archive_three_gpu_single_PPO_seven_hour_stage_once.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
NOTE='''Human explicitly authorized: 大量老旧远古训练轨迹可以删除了. This is a narrow exception to the prior raw-original retention rule for the exact189-file list, not automatic cleanup or permission to delete checkpoints/reports/frozen evaluation evidence/current tasks or write the readonly Windows C system partition. Single4090 host10.24.4.210 was inventoried in owned MOD4 roots only. All selected intermediate training NPZ files are from October15 or earlier. Preserve S4 completed gate148 sources/checkpoints and raw0/1/146/147; delete indexed completed middle raw2..145 only. Preserve every selected retention run first/terminal sample, short runs, named failures, frozen eval raw, assets, code, reports and all model weights.

Exact local and durable remote pre-deletion manifests contain resolved absolute paths, sizes, allocated sizes, UID/dev/inode/mtime identities and actually read full SHA. S4 hashes match its original archived148 completed rollout index. Process path references to old selected roots are rejected; global process-FD absence is NOT proven or claimed because kernel permissions reject unrelated/protected proc FD inspection. No privilege escalation, process signals, SDK/GPU/budget/canonical/OS lock or mount changes. Same-file identity, old cutoff, no symlinks/hardlinks, exact NPZ basename allowlist and original directory boundaries are checked again before each unlink. No recursive deletion or directory removal. Durable per-file deletion journal is fsynced; only this exact source210 file list was unlinked.

Actual189 files deleted:39782667642 apparent bytes/39783354368 allocated bytes. Windows D released33518743552 allocated bytes; Linux home6264610816. D available was3445854208B and is now36964507648B, exceeding the unchanged25GiB startup requirement. Home available2782736384B to9047347200B. All27509 unselected old-scope files have exact unchanged inode/size/mtime metadata before/after; all189 selected paths absent. This is not a claim global disk inventory is entirely ours. Pre-cleanup227.1GB owned project total is historical. Listed raw originals intentionally deleted by explicit authorization are NOT falsely called retained; old Git indexes/reports remain correct historical precleanup captures. No backup copy is asserted.

Preserve local V1/V2 count assertions before any SSH/hash/delete:149 aggregate nonretention NPZ was incorrectly treated as149 completed rollout rows, while actual archived completed index and exactly named files are148 indices0..147. The V2 diagnostic inference that raw148 exists was wrong and is explicitly corrected, without altering that old report. Preserve V3 /proc/1/fd and V4 /proc/2546/fd permission rejection before any hash/delete, and V5's narrower exact-owned-path guard with no global FD claim. Original missing-local-directory lookup errors are retained. The successful V5 inventory/hash and single apply once are separately sourced and indexed; no old failed once was rerun to change its false.

Existing mod4-10 heartbeat only is updated via native app tool and exact app TOML readback, same ACTIVE/hourly/target. Old full prompt retained. H1 physical storage blocker is resolved on previously authorized writable Windows D; old current-contract preGO rejection remains untouched and cannot be hot-added. Cleanup dispatched no H1 worker/native/GO/PPO and collected no new recovery FINAL; future H1 requires current original writer genuine FINAL/full sourceCPU/cost/out/canonicalNone/two fcntl handback, retained complete closed121 source/Adam643700, own new backend/source native180 and strict resource admission. E2 remains paid-learning hold after fixed10122/fixed1050/fixed1121of64, no reward/LR/STD/threshold change. Recovery follows actual finite original interval; no new training window or budget from cleanup. Original master1188000s/330h/seven extensions, guards, other hosts/users and readonly C unchanged.

Archive all successful/rejected readers, source, exact manifests, deletion receipts, app verification and handoff. Existing old trial objects/peels remain untouched. This unique record_experiment stage uses exact annotated tag title+note file-F once; subsequent reports are ordinary supplements. If push fails continue existing commit/tag objects only, never rerun record/tag/commit/apply. Final remote verification may remain tool output to avoid infinite receipt commits.'''
MSG=B/'ACTUAL_CLEANUP_ANNOTATED_TAG_MESSAGE_UTF8.txt'

def git(*args):
 if args[:2]==('tag','-a'):
  assert args[2]==TAG and args[3]=='-m' and args[4]==TITLE+'\n\n'+NOTE
  assert MSG.read_text(encoding='utf8')==args[4]
  return g.git('tag','-a',TAG,'-F',str(MSG))
 if args and args[0]=='push':return g.git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
 return g.git(*args)

def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists() and not git('tag','--list',TAG)
 actual=json.loads((R/'SOURCE210_HUMAN_AUTHORIZED_OLD_INTERMEDIATE_TRAJECTORY_DELETION_ACTUAL.json').read_bytes());assert actual['passed'] and actual['deleted_count']==189 and actual['all_selected_deleted_paths_absent']
 assert json.loads((R/'AUTOMATION_OLD_TRAJECTORY_CLEANUP_STORAGE_RESTORED_APP_EXACT_VERIFIED_ACTUAL.json').read_bytes())['actual_app_readonly_TOML_exact']
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  r=line.split();old[r[0]]=(r[1],r[2] if len(r)>2 else r[1])
 assert len(old)==1367
 note=B/'HUMAN_AUTHORIZED_OLD_TRAJECTORY_CLEANUP_ACTUAL_STAGE_NOTE.txt'
 with note.open('x',encoding='utf8',newline='\n') as f:f.write(NOTE)
 with MSG.open('x',encoding='utf8',newline='\n') as f:f.write(TITLE+'\n\n'+NOTE)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[]
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest();row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
  if p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.usda','.usdc','.zip','.tar','.gz','.mp4') or len(raw)>50_000_000:
   row.update(capture='large_artifact_path_size_SHA_index_only',local_original_retained=True)
  else:
   try:clean,n=redact(raw.decode('utf8'))
   except UnicodeDecodeError:row.update(capture='binary_path_size_SHA_index_only',local_original_retained=True);rows.append(row);continue
   data=clean.encode('utf8') if n else raw;dest=DEST/p.relative_to(B);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);rel=dest.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=n)
  rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_local_saved_sources_reports_errors_workorder_monitor_app_receipt_captured=True,local_originals_retained=True,exact189_remote_old_intermediate_raw_intentionally_deleted_by_human_authorization=True,deleted_remote_files_have_full_predelete_SHA_and_actual_perfile_receipts=True,no_claim_deleted_remote_originals_retained=True,no_training_or_budget_changes=True,later_saved_reports_need_ordinary_supplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');rec.git=git
 sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','repair','--note-file',str(note),'--files',*files,'--validation','189 exact old NPZ trajectories fully prehashed and deleted;27509 protected file identities unchanged;D actual free36.9645GB above original25GiB;no training or budget change;existing heartbeat exact verified.','--push']
 rec.main();head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);g.n.m.cap.a.gitio.g=git;g.n.m.cap.a.verify(rows,old,head,TAG,obj)
 print(json.dumps(dict(commit=head,tag=TAG,object=obj,actual_remote_main_tag_peel_all1367_original_tag_objects_peels_tracked_SHA_verified=True,total_tags=1368,tracked_sources=len(rows),new_capture_files=len(files),deleted_remote_legacy_raw_files=189,allocated_bytes_reclaimed=39783354368,no_new_GPU_training_budget_or_cleanup_replay=True)),flush=True)

if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('LEGACY_CLEANUP_STAGE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_or_tag_exists_continue_existingobjects_only_no_rerecord_retag_recommit_or_redelete=True),f,indent=2)
  raise
