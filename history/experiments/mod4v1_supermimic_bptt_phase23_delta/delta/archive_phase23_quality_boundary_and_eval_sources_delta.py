"""Append outcome priority, actual cooperative full saves, and frozen-eval sources.
No remote, SDK, original model/raw reads, ledger work or old once replay.
"""
from pathlib import Path
import json,hashlib,sys,subprocess,datetime
R=Path(__file__).resolve().parent;REPO=Path(r'F:\RMPOLAR-RL\repo-lqr');REL=Path('history/experiments/mod4v1_supermimic_bptt_phase23_delta');D=REPO/REL
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
import record_experiment
G=lambda *a:subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
H=lambda raw:hashlib.sha256(raw).hexdigest()
assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and G('rev-parse','HEAD')=='53678ec8d2e05dcafb890a357078c25020101903'and not G('status','--porcelain');assert not D.exists()
closed=json.loads((R/'reports/A1_ADMISSION2_QUALITY_BOUNDARY_CLOSED_TRUTH_V1.json').read_bytes());stop=json.loads((R/'reports/QUALITY_BOUNDARY_ORIGINAL_COOPERATIVE_STOP_REQUEST_V1.json').read_bytes());assert closed['all8_original_actual_wait_fullsave_semantic_success']and closed['original_skill_assessment_not_done']and stop['returncode']==0 and stop['receipt']['signals_Cwrite_ledger_budget_hyperparameter_active_source_changes']==0
known={}
for part,commit in [('mod4v1_supermimic_bptt_phase18_sources','8e6160b8747af162b5a486b3f3aa1ad4782223fd'),('mod4v1_supermimic_bptt_phase19_delta','57626b09cbed02b5b2efabbfd0c0b632383bdce0'),('mod4v1_supermimic_bptt_phase20_delta','4afdba074f3d295cd78ed4bf46a5cc779ff97b70'),('mod4v1_supermimic_bptt_phase21_delta','d31b5349abb5ee7c7f3dcbae7eec84c02aae761a'),('mod4v1_supermimic_bptt_phase22_delta','53678ec8d2e05dcafb890a357078c25020101903')]:
 for x in json.loads((REPO/'history/experiments'/part/'SOURCE_INDEX.json').read_bytes())['rows']:
  if x.get('archive_path')and x.get('source_sha256'):known[x['source_path']]={**x,'known_commit':x.get('referenced_commit')or commit}
D.mkdir(parents=True);rows=[];files=[];refs=0
for p in sorted(R.rglob('*'),key=str):
 row=dict(source_path=str(p))
 if p.suffix.lower()in('.pt','.pth','.ckpt','.onnx','.safetensors'):
  row.update(status='model_reference_only_no_stat_or_read',source_sha256=None);rows.append(row);continue
 if not p.is_file():continue
 try:
  before=p.stat();row.update(stat_bytes=before.st_size,mtime_ns=before.st_mtime_ns)
  if p.suffix.lower()in('.pyc','.npz','.npy','.usd','.usdc','.zip','.zst','.mp4','.png','.jpg','.jpeg','.stl','.bin','.partial','.unpublished')or'__pycache__'in p.parts or before.st_size>50_000_000:
   row.update(status='binary_large_or_unpublished_metadata_only_no_content_read',source_sha256=None);rows.append(row);continue
  raw=p.read_bytes();after=p.stat();row.update(bytes=len(raw),source_sha256=H(raw),unchanged_size_mtime_during_read=before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns)
 except FileNotFoundError:
  row.update(status='disappeared_during_capture_pending_next_append',source_sha256=None);rows.append(row);continue
 if not row['unchanged_size_mtime_during_read']:row['status']='moving_index_only_pending_later_append'
 elif str(p)in known and known[str(p)]['source_sha256']==row['source_sha256']:
  old=known[str(p)];assert(REPO/old['archive_path']).is_file();row.update(status='unchanged_reference_existing_phase18_through22',archive_path=old['archive_path'],archive_sha256=old['archive_sha256'],referenced_commit=old['known_commit']);refs+=1
 else:
  try:text=raw.decode('utf-8')
  except UnicodeDecodeError:row['status']='nonUTF8_metadata_index_only'
  else:
   safe,n=redact(text);data=safe.encode('utf-8')if n else raw;dest=D/'delta'/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);name=dest.relative_to(REPO).as_posix();files.append(name);row.update(status='text_redacted'if n else'complete_new_or_changed_text',redactions=n,archive_path=name,archive_sha256=H(data))
 rows.append(row)
(D/'.gitattributes').write_text('* -text\n',encoding='utf-8');(D/'SOURCE_INDEX.json').write_text(json.dumps(dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_phase22_commit='53678ec8d2e05dcafb890a357078c25020101903',unchanged_reference_count=refs,rows=rows,not_captured_yet='All first-created or changed later source/progress/final/handoffs remain pending next append.'),indent=2),encoding='utf-8')
note='''# Phase23 — user quality priority, actual native A1 candidates, original cooperative full-save boundary, evaluator sources

User2026-11-02 23:39 clarified: increased training is a means to improve actual original skill pass rate. Goal revision11 active; ~3000 is training scale plan, not an independent success/completion gate. Primary result is each nonH1 expert original acceptance/complete cohort and independent robustness, intermediate80/final90, no count/loss/RC0/nofall/pooled proxy. H1, originalphysics/fullD0-D7/2c-bae/speed/acceptedthresholds/C/singlewriter/reserve/resource locks/finitewindow rules unchanged. A0 E02520/E22392 archived separately, never spliced into A1 raw35.

## Actual first V6 admission timeout and new Admission2
Oldroot V6 parent1488631 naturally expired original1800preGO wait at23:10:38, all8 zeroGO/unstarted/noSDK/model. No extensions/refunds/foreign interference. Posttimeout originalC cleared but another frozen-eval private/finite lease existed; readonly releaseobserver actually saw allrelevant leases clear23:16:25. NEW Admission2 freshroot ...MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000 had original14samePINs/sourceindexf126, newmetadata/root/markers. Sourcepreflight/stage/Popenonce parent1490574/startticks137458072, no oldpurpose replay. ActualoriginaltwoGPU/gates admittedE3+W35, freshN1024/fullDR/raw35/no oldPPOoptimizerrestore. PoseV4 realstartup gravity error~8.5e-8/6e-8 passed; actual policy BPTT future andWMVJP count strict. No skill improvement was inferred from updates.

## Actual cooperative stop, not a signal or hotpatch
After source review and fresh exactownPID/root/C/GO/fullsave checks, originalSTOP_AFTER_SAVE markers were written onlyto8ownrolejobs, pending6first/active2last at1793636448.9317915. No SIGSTOP/INT/CONT/KILL, source/hyperparameter/ledger/budget/lock changes bycontroller. Existing fixed8owner does not skip pending; allsix genuinely constructedSDK/reset/loadedteacher/initialized newlearner then beforefirstaction stopped with zero policy updates, originalhistory/norm initialization occurred. These are zero-update fresh frozen-baseline captures, NOTtrained/graded/passed; source did notpromise finite-minutes close. Actual errors would stillblockpending andcounts wouldremain truth.

Actually all8 normaloriginalchildwait/semantic/fullsave/account/leases successful, parentexit1793636655.654124 (~00:24:15Nov03), noerrors. E3actual2182/iter2282 complete236664417B SHAa4c56390b4c549ba8bfb808a63206c0816ad50e8c9659dc053f98cc66b3c8127; W351973/iter2073 complete233435425B SHAb2f2878ff9aa04ddcd283fe71f5b5924b1bff78b3f04118cfa689244b0665cff; other6 producer0/iter0. Whole4models/4opts/replay/RNG/history saved, actualteacherweights/buffers andoriginalnominalguard intact. AppV6 narrow expectednonreturnfastintent validatedwithactualwait, nofakepost-Appreturn. ActualderivedGO-to-wait6903.554010629654expertseconds kept, no newledger/refund/clamp. Observer finishednaturally, noownGPUworker left atthiscapture. No originalskillgraduation/90claim.

## Quality evaluator, source versus actual evidence
Reviewed eight-role A1 frozen integration45stdlibchecks and independently newE3W35subsetparent24stdlibchecks sealed. OriginalN80/scopes/accepted loops/seed/DR/physics/controls untouched; newsubset schema/barrier explicit2, sixdeferred/full8catalog, notfake8projection. OriginalprivateEX/finiteEX/Creadonly/minimum/emptyGPU23500MiB-util0/RAM96GiB/disk25GiB/1800wait/900ready/2400deadline/actualwait/finally retained. Cached wholeownA1fullrootonebyte/hash/CPUdecode/pi-onlyGPU, no replay/RNG/historyslice/optimizer ormotherPTreopen. Originalnoisydelayed35 and first|previousactualterm/trunc preserved. RSLsource6219/10334 selected byparent-agent fromactualCPU ownsynthetic4xN80reference0.0, notnewhumanapproval orpastnativeGPUobservation; futureevalselfbindingstrictbeforeaction. Parent13flatpayload197903B/index42e alreadyprepared. Source-onlystager/consumer maystillbeunfinished atcapture and mustnotbecalledactualnativeevaluation; laterchangespendingnextappend.

E3 original74requested firstepisodecredit/normal6 separate. W35 originalFINAL pooledcounts notmovingrate; split source consumer for FUTURE NEW actualeval PositionalRows227 JSONL+SCHEMAS227 and producerbytesSHA/rows/drops will be one actualgrading read, notoldraw reopensforlabels/status. Untilmeasured, moving/standing/referenceUID/cache/effectnull. Plannedpairedreset protocols do notprove actualmother/candidate comparison. E0/S50 originalbinaryauthority remainnull after bounded33source search plus exactreferencedMasterPlan47599B/812a4...read; old historicalplan instructions didnotchangephysics/budget/authorization. No MAE/nofall/S135proxy.

Allactualsource/test failures, oldV5twoerrors, original0GOtimeout, newnativeartifactrefs, cooperativecontrol/source audits, qualitygoal11/handoffs and point-in-time newevalsources preserved/referenced. Mainread-only independentlyadvances; uniqueannotatedfeaturetrial only. No selectedmodel/raw/SDK or physical reruns for Git. Actualfrozenqualityresults andlaternewsource/close/handoffs remainpendingappend; thisarchive is not proof of increased pass rate.
'''
(D/'NOTE.md').write_text(note,encoding='utf-8');files +=[(REL/n).as_posix()for n in('.gitattributes','SOURCE_INDEX.json','NOTE.md')]
original_git=record_experiment.git
def exact_short_git(*a):
 if len(a)>=2 and a[:2]==('add','--'):
  dest=a[2];selected=set(a[3:]);assert selected==set(files)and all(Path(x).is_relative_to(REL)for x in selected)
  value=original_git('add','--',dest,REL.as_posix());assert set(original_git('diff','--cached','--name-only').splitlines())==selected|{dest};return value
 return original_git(*a)
record_experiment.git=exact_short_git
sys.argv=['record_experiment.py','--id','mod4v1-supermimic-quality-first-native-closed-eval-source-phase23','--title','Record quality-first native candidates, cooperative complete-save closure and frozen-eval sources','--kind','training','--note-file',str(D/'NOTE.md'),'--validation','Goalrev11-outcome-first;actualA1E32182W351973-fullsaved-normalclosewait-cost-leases;other6-zero-update-baseline-nottrained;no-signals-hotpatch-budgetchange;oldA04912separate;N80microbatchSource24-integration45-notactualeval;originalgradegapsnull-no90claim','--files',*files]
record_experiment.main();print(json.dumps(dict(commit=G('rev-parse','HEAD'),branch=G('branch','--show-current'),entries=len(rows),unchanged_references=refs,new_text_files=len(files),status=G('status','--porcelain')),indent=2))
