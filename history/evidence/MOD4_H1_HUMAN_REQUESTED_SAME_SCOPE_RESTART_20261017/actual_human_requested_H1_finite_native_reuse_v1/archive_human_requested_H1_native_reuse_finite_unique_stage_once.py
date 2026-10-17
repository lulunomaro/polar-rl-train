"""One new actual finite-training stage; exact title+note file tag; never relaunches runtime."""
from pathlib import Path
import os,sys,json,time,hashlib,importlib.util,importlib,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;REPO=W/'polar-rl-train';A=W/'MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017';O=W/'MOD4_H1_CLOSED24_TARGET72_SAME_SCOPE_FINITE_20261017'
BASE='9f921ad467fa582006630ce8f8461d8eeca09c2c';ID='human-requested-h1-same-scope-native-reuse-finite-training';TAG='trial-20261017-'+ID
TITLE='Start human-requested finite H1 continuation with strict same-source native reuse'
DEST=REPO/'history/evidence'/B.name/'actual_human_requested_H1_finite_native_reuse_v1'
NOTE=B/'HUMAN_REQUESTED_H1_ACTUAL_FINITE_STAGE_NOTE_UTF8.txt';MSG=B/'HUMAN_REQUESTED_H1_ANNOTATED_TAG_MESSAGE_UTF8.txt'
sp=importlib.util.spec_from_file_location('previous_A_stage_pure_functions_only',A/'archive_H1_closed_final_native180_E3_frozen_actual_unique_stage_once.py');prev=importlib.util.module_from_spec(sp);sp.loader.exec_module(prev);rawgit=prev.rawgit;H=prev.H
def git(*args):
 if args[:2]==('tag','-a'):
  assert args[2]==TAG and args[3]=='-m' and MSG.read_text('utf8')==args[4];return rawgit('tag','-a',TAG,'-F',str(MSG))
 if args and args[0]=='push':return rawgit('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
 return rawgit(*args)
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists()
 deployed=json.loads((R/'HUMAN_REQUESTED_H1_STRICT_NATIVE_REUSE_NEW_FINITE_PPO_DETACHED_ACTUAL.json').read_bytes())
 cpu=json.loads((R/'HUMAN_REQUESTED_H1_IMMUTABLE_FIRST_COMPLETE_LOCAL_CPU_V2_ACTUAL.json').read_bytes());assert cpu['passed_real_immutable_first_complete_local_CPU']
 contract=json.loads((R/'HUMAN_REQUESTED_H1_FINITE_SAME_SOURCE_NATIVE_REUSE_PAYLOAD_CPU_ACTUAL.json').read_bytes());assert contract['passed_CPU_only']
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  s=line.split();tags[s[0]]=(s[1],s[2] if len(s)>2 else s[1])
 assert len(tags)==1371;prior={}
 for root in (A,O):
  for index in (REPO/'history/evidence'/root.name).rglob('REPORT_CAPTURE_INDEX.json'):
   for row in json.loads(index.read_bytes())['entries']:
    if row.get('Git_path'):prior[row['sha256']]=row
 note='''Human explicitly requested immediate training after the agent disclosed that no project computation was running. This new finite H1 continuation runs on72GPU0 from the actual complete fe1709/Adam644660/owned24 source. It is a new original1800s grant,300s exit headroom,max24fullupdates/free8GiB saved-stop, inside unchanged1188000s330h/sevenextensions. No extension of an old grant, new budget, duplicate canonical, tail, refund or clearactive.

The source already completed its own native180/720 with all3.6Mpolicy14.4MphysicalCPU and two fullPT localCPU on the same actual72GPU0/backend/runtime/assets. New node strictly verifies old native final, actualGPU/CPUwaitedEXIT0, native parent/childrenout, manifest/source/runtime/assets/Adam/core/reportSHA and currentGPU identity before ready. New pure validator positive plus11negative cases passed; this is CPU evidence, not a new native run. No old native/Task/raw replay. New target complete manifest/source199tensor105float/actualRSL5/SDKmath CPU then fresh actual original owner/listener/signedheld-slotACK/node were dispatched. OriginalO and native-only exit/locks/resource boundaries are rechecked, no live source, installedSDK, driver, environment or other task mutation. New namespace fixes stale taskGPU/update labels while preserving the inherited originaltask separately.

Actual new originalowner787613 root/mnt/mod4_linux_durable_20261013/H1r_1710v3/owner and72node3193056 root/home/lc01/Zonglin Li/zonglin2/tasks/H1r_1710v3. ActualGO1792250187.6653013 (2026-10-17 23:16:27.665301+08),productionworker3193062. Save schedule23:41:27,nominalend23:46:27; actual futurebounds/FINAL/out/cost/locks are pending until measured, not guaranteed by schedule. Initialbounded300s collection returnedempty models without errors and was kept. New bounded600s same-target read inspects actual workerlog/GPU and collects only missing immutablefirst/startup0, then one source metadata read; no added watcher or old artifact recollection.

New firstPPO is qualified only by twohost complete SHA plus local allmodel/runtimefinite, startup0 sourceactor9includingSTD/critic8/17Adam literalexact, exactsourceepisode+1/phaseage0, all17Adam644660to644680 and actual all17actorcritic changes,24controls480000productionenvsteps. Source native0flight/landing/recovery and prelaunchproxy remain not jump skills. E2 behavior and E3 recovery paid reviewhold remain zeroGO/worker, no hotadd or reward/LR/STD/threshold change.210 D21.6GBbelow25GiB still no ownGPUworker;72GPU1 no newpaid;3060 frozenonly/Laptoppaused. This is one activeH1 training slot, not threeGPU learning or100percentutilization. H1 frozen components remain CPUprepared; this stage does not assert3060H1Task/fullorjumpqualification.

20k/20260928/24/LR1e-4adaptiveKEEPSTD1/35-38-6/.0025x4TGS32/4/100Hz/history5msbin3/D0D7white_v3+noise/hardware and original seven masked H1 rewards plus cappedprelaunch source are unchanged. query1e-6/COM1e-5/closure2mm ordinaryreset/mimic.01/unknown-nonfinite-missingcallbacks ownfailedprefixsave-stop remain. All ancestorsfalse/E0/W35/gate148/f51650mm/CURB/E2/E3/H1old/native and publicSDK-not-binary/cookedShape/COM/hardwaredeadline boundaries preserved. Same existingmod4-10 hourly target only; credentialsHMACSSH+childstdinmemory, noargv/log/disk/Git; oldNargvdisclosure unchanged.

All current successes, incomplete300s collection, CPU fixtures, copied code, unusedV1reader/newV2reader, manifests, firstmodelindices, newworkorder/monitor/appreceipts included. Original stage and all oldonce/helpers remain consumed. LargePT/assets indexonly; originals retained. Futurefirst/FINAL/cost/receipt followups use ordinary supplements, not repeat record/tag/commit. Exact current firstCPU report:\n'''+json.dumps(cpu)
 for p,text in ((NOTE,note),(MSG,TITLE+'\n\n'+note)):
  with p.open('x',encoding='utf8',newline='\n') as f:f.write(text)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];deferred=[]
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(str(p));continue
  raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest();row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=digest)
  if digest in prior:
   ref=prior[digest];assert H(REPO/ref['Git_path'])==ref['archived_sha256'];row.update(capture='same_SHA_prior_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
  elif p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.usda','.usdc','.zip','.tar','.gz','.mp4','.dmp'):row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   clean,n=redact(raw.decode('utf8'));assert n==0,'Credential redaction required before archive';dst=DEST/p.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw);rel=dst.relative_to(REPO).as_posix();files.append(rel);row.update(capture='complete_exact_bytes',Git_path=rel,archived_sha256=H(dst))
  rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,all_saved_sources_errors_pending_CPU_and_monitor_receipts=True,large_artifacts_index_only=True,future_saved_reports_need_ordinary_supplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');rec.git=git
 sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Actual humanrequestedH1GO23:16:27;strict same-source/backend native reuse;fulltargetCPU;newfirst199tensor105float startupcoreexact17Adam644660to644680 actor9STDcritic8changes;originalcanonical finite1800 no new budget.','--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);prev.prev.prev.g.n.m.cap.a.gitio.g=git;prev.prev.prev.g.n.m.cap.a.verify(rows,tags,head,TAG,obj)
 print(json.dumps(dict(commit=head,tag=TAG,object=obj,actual_remote_main_tag_peel_all1371_old_objects_and_tracked_SHA_verified=True,total_tags=1372,source_entries=len(rows),capture_files=len(files),deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('HUMAN_REQUESTED_H1_UNIQUE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_continue_existing_objects_only_no_repeat_record_tag_commit_or_GPU=True),f,indent=2)
  raise
