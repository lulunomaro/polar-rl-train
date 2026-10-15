"""One actual assignment/upload/resource-rejection stage; never rerun after record."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,importlib,importlib.util,json,subprocess,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
BASE='beb733d457cc9cb26554818c614bdf8b8f691cac'
ID='host72-two-e1-tasks-assigned-source-upload-resource-busy'
DEST=REPO/'history/evidence'/D.name/'two_tasks_pinned_uploaded_CPU_verified_and_resource_rejected_actual_v1'
s=importlib.util.spec_from_file_location('two_E1_tasks_archive_pure_helpers',W/'MOD4_S5_NOMINAL_AUDIT_SOURCE_ADAPTER_CPU_20261015/archive_nominal_isolated_source_target_native_and_unused29_stage_once.py');n=importlib.util.module_from_spec(s);s.loader.exec_module(n)
def git(*args):
 if args and args[0]=='add':
  files=[v for v in args[1:] if v!='--'];r=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=('\0'.join(files)+'\0').encode('utf8'),capture_output=True)
  assert r.returncode==0,r.stderr.decode('utf8','replace');return r.stdout.decode('utf8','replace').strip()
 return n.git(*args)
def H(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
NOTE='''Human requested relevant multi-machine RL papers and actual training assignments for the new dual4090 machine. Work remains strictly below /home/lc01/Zonglin Li/zonglin2 on host72 with no deletion, system-driver/profile/other-environment mutation or interference with other compute. DD-PPO synchronous distributed PPO, IMPALA actor/learner with V-trace, SEEDRL central inference and PBT independent populations are documented from primary papers. This assignment uses independent E1 terrain branches, not an implemented DD-PPO/PBT/V-trace system.

GPU0 assigned E1_CURB20 reset/taskentry-bound normal-command direction coverage with both mirrored20mm/150mm-strip ascents and descents; GPU1 assigned E1_SLOPE5 flat-ramp-flat continuity at original5degrees/2m/20s. Source3c97 is original G3 WAVE35 complete state, so explicit CURB migration is required, not an already qualified CURB model. Old CURB133/139 up22/23 vs protected26 and down27 are preserved, no blind resume. Source24b is original SLOPE5 fullstate, higher8/10degree evidence is frozen only. Both complete181tensor/102float/86perenv20k, originalactor9/critic8/17Adam CPUfinite independent local/remote, steps642840/642980 and iteration32063/32069. Original all410+404 source snapshots, manifests, exact robotUSD694e9..., resetNPZ78af9... and sourceweights were readonly streamed from original210, localarchive146397089B SHA42cfa7447066a67fe1d01d505f5ab594586b1791f05d487c0a2147a0b72ebab3,822 source-file rows. Asset collection V1 partially wrote exact import_contract then KeyError because optional robot_cfg.py was not present in original src_sha256; originalbytes/error retained, independent V2 reused exactcontract cbcdacdf... and no fabricated optional config. Source physical main is inverse-AST exact except owned supported headless AppLauncher import, no installed SDK edits. Prepared native V1 and V2 are unused, not targetnative or20kGPUrestore passes.

New bundle copied and safely extracted below own72tasks root; complete833 target files streamSHA locally matched. One local hidden-input helper was interrupted before network because prepared target controller needed validated private Python3.12 rather than assuming system3.8 Path.is_relative_to. Independent V2 reused same already created bundle, not a GPU replay. Local report writer NameError meta and corrected report retained. Actual target controller reached resource gate before creating any native worker or GPU lease: GPU0 had PID3025860 .venv_imder_cuda/bin/python, GPU1 PID3022346 /home/amax/rym/MD2E-MI/.venv/bin/python. Original controller EXIT1/trace is preserved. These are observed resource snapshots, not permanent process identities. Neither was stopped/modified or claimed as ours. Actual native/PPO/optimizer/cost0; local transport naturally exited and actualCIMabsent. Existing uploaded BASE and old controller are consumed and must not be rerun. Prepared V2 adds full prefix checkpoint and buffered row persistence on Python exception/eval mode, syntax-only/not uploaded, no process-crash durability claim.

Next existing hourly monitor makes one bounded actual resource snapshot; no secondwatcher/denseSSH. Use a new continuation to reuse existing uploaded exactassets and unused native phases when a designatedGPU becomes free. Both own originalbackend full8typed/globalnamed/privateCPUCUDA disk/sourceepisode+1/native/query/contact/health/physical source and then new-axis state migration/fullsave/native must actually pass before PPO. Source-level2m SLOPEboundary exposure is a hypothesis, not unique physical failure. New command axis has not yet been GPUadmitted. First learning windows each<=1800s parentloadlearnsaveexit with60sheadroom, original solecanonical sequentialGPU0thenGPU1 because originalmaster forbids concurrent chargeable learning without a new accounting contract. Original210 parent/locks/accounting bridge still required, no claim dispatched/implemented. Latest originalcanonical224segments activeNone charged548277.1062400341 remaining639722.8937599659 and twofcntlFree is a snapshot, no budget mutation/extension/newledger/refund/clearactive/tail. Keep original20k/seed60928/24controlupdate/LR1e-4adaptiveKEEPSTD1/35-38-6/2.5msx4TGS32-4/100Hz/allD0-D7/noise/rewardhardware, normal health guards, actual savedstate/cost/exit evidence. No S8 airborne jump,70,secondgatePPO or automatic budget. LaptopGPU remains paused,249 frozenevalonly, source210readonly except proper actual originalcanonical charge parent.

Important independent S5 reader correction: original matched35mm27/27 A/B/C report actualseed20260928/white_v3, not development20261002 as old heartbeat had labeled. Preserve original report/physical evidence and historicalwronglabel; six dev02/03 x nominal/whitev2/whitev3 original35 matchedcells still missing. Other S5 scopes and all ancestors/false/failedprefix/cost limitations unchanged. Same mod4-10ACTIVE/hourly/sametarget updated for actual newhuman authorization/two assigned tasks/resourcepending and scope correction, unchangedpending quiet. All saved originals/readers/false/unused/source/research/assets/hashindexes/workorder/monitor captured at this stage. Large binaries retained only path-size-SHA index, credentials excluded. Unique annotatedtrial once, later ordinarysupplements. Pushfailure recover existing objects only, never rerecord/tag/commit or replay runtime; Git not runtime dependency.
'''
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list','*'+ID) and not DEST.exists()
 assert json.loads((R/'TARGET_UPLOADED_ALL_SOURCE_SHA_AND_SAME_HOURLY_MONITOR_ACTUAL.json').read_bytes())['all_target_uploaded_SHA_local_exact']
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  v=line.split();old[v[0]]=(v[1],v[2] if len(v)>2 else v[1])
 assert len(old)==1349
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 note=D/'TWO_E1_TASKS_ACTUAL_ASSIGNMENT_RESOURCE_REJECTION_STAGE_NOTE.txt'
 with note.open('x',encoding='utf8') as f:f.write(NOTE)
 DEST.mkdir(parents=True);rows=[];files=[]
 for p in sorted(x for x in D.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  h=H(p);size=p.stat().st_size;row=dict(source_path=str(p.resolve()),bytes=size,sha256=h)
  if size>8*1024*1024 or p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip','.gz','.mp4','.dmp'):
   row.update(capture='large_or_binary_actual_path_size_SHA_index_only',original_retained=True)
  else:
   raw=p.read_bytes()
   try:clean,count=redact(raw.decode('utf8'))
   except UnicodeDecodeError:
    row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
   data=clean.encode('utf8') if count else raw;out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);rel=out.relative_to(REPO).as_posix();files.append(rel)
   row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=count)
  rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_saved_stage_success_rejection_false_unused_reader_errors_workorders_monitor_at_snapshot_captured=True,credentials_excluded=True,large_originals_retained=True,later_reports_require_ordinary_supplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');rec.git=git
 sys.argv=['record_experiment.py','--id',ID,'--title','Assign and upload two source-pinned E1 training tasks; retain actual dual-GPU resource rejection','--kind','diagnostic','--note-file',str(note),'--files',*files,'--validation','Complete original source/optimizer CPU checks and all833 uploaded targetSHA exact. Actual resource gate rejected both cards occupied before any own native/PPO/lease; no training or cost claimed. Same hourlymonitor, source-bound next admission and original sequential accounting constraints preserved.','--push']
 rec.main();head=git('rev-parse','HEAD');tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;obj=git('rev-parse',tag)
 n.m.cap.g=git;n.m.cap.a.gitio.g=git;n.m.cap.a.verify(rows,old,head,tag,obj)
 print(json.dumps(dict(commit=head,tag=tag,object=obj,actual_remote_main_tag_peel_all1349_oldtags_and_tracked_SHA_verified=True,sources=len(rows),no_actual_PPO=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('TWO_E1_TASK_STAGE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),resume_existing_capture_objects_not_record_tag_commit=True),f,indent=2)
  raise
