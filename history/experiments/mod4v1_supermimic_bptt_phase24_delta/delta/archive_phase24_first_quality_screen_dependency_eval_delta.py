"""Archive actual quality diagnosis, all close/reader failures and new source fixes.
No remote/native/SDK/model/raw open or old trial replay. Point-in-time text delta.
"""
from pathlib import Path
import json,hashlib,sys,subprocess,datetime
R=Path(__file__).resolve().parent;REPO=Path(r'F:\RMPOLAR-RL\repo-lqr');REL=Path('history/experiments/mod4v1_supermimic_bptt_phase24_delta');D=REPO/REL
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
import record_experiment
G=lambda *a:subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
H=lambda raw:hashlib.sha256(raw).hexdigest()
assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and G('rev-parse','HEAD')=='01232718ef0ae41207dc50315d1bdbdeaa1c60d9'and not G('status','--porcelain');assert not D.exists()
quality=json.loads((R/'reports/FIRST_A1_ORIGINAL_QUALITY_SCREEN_SELECTION_V1.json').read_bytes());assert quality['qualified_final_skill_pass_rate']is None and quality['actual_same_protocol_mother_reference']is None and all(not x['qualified_execution']and x['decision']=='KEEP_REGISTRY_V12_SCOPED_BEST_NO_CANDIDATE_PROMOTION'for x in quality['screen']);assert quality['screen'][0]['original_requested_first_episode_credit']['n']==0 and quality['screen'][0]['original_requested_first_episode_credit']['N']==74
cpu=json.loads((R/'reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json').read_bytes());assert cpu['returncode']==0 and cpu['receipt']['passed']and cpu['native_steps']==cpu['original_model_reads']==0
stage=json.loads((R/'reports/FROZEN_E3_W35_BATCH_V2_ACTUAL_SOURCE_STAGE_RECEIPT_CORRECTED_V2.json').read_bytes());assert stage['stage']['staged']and stage['collector_erratum']['stage_replayed']is False
known={}
for part,commit in [('mod4v1_supermimic_bptt_phase18_sources','8e6160b8747af162b5a486b3f3aa1ad4782223fd'),('mod4v1_supermimic_bptt_phase19_delta','57626b09cbed02b5b2efabbfd0c0b632383bdce0'),('mod4v1_supermimic_bptt_phase20_delta','4afdba074f3d295cd78ed4bf46a5cc779ff97b70'),('mod4v1_supermimic_bptt_phase21_delta','d31b5349abb5ee7c7f3dcbae7eec84c02aae761a'),('mod4v1_supermimic_bptt_phase22_delta','53678ec8d2e05dcafb890a357078c25020101903'),('mod4v1_supermimic_bptt_phase23_delta','01232718ef0ae41207dc50315d1bdbdeaa1c60d9')]:
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
  if p.suffix.lower()in('.pyc','.npz','.npy','.usd','.usdc','.zip','.zst','.mp4','.png','.jpg','.jpeg','.stl','.bin','.partial','.unpublished','.jsonl','.csv','.parquet')or'__pycache__'in p.parts or before.st_size>50_000_000:
   row.update(status='binary_large_raw_or_unpublished_metadata_only_no_content_read',source_sha256=None);rows.append(row);continue
  raw=p.read_bytes();after=p.stat();row.update(bytes=len(raw),source_sha256=H(raw),unchanged_size_mtime_during_read=before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns)
 except FileNotFoundError:
  row.update(status='disappeared_during_capture_pending_next_append',source_sha256=None);rows.append(row);continue
 if not row['unchanged_size_mtime_during_read']:row['status']='moving_index_only_pending_later_append'
 elif str(p)in known and known[str(p)]['source_sha256']==row['source_sha256']:
  old=known[str(p)];assert(REPO/old['archive_path']).is_file();row.update(status='unchanged_reference_existing_phase18_through23',archive_path=old['archive_path'],archive_sha256=old['archive_sha256'],referenced_commit=old['known_commit']);refs+=1
 else:
  try:text=raw.decode('utf-8')
  except UnicodeDecodeError:row['status']='nonUTF8_metadata_index_only'
  else:
   safe,n=redact(text);data=safe.encode('utf-8')if n else raw;dest=D/'delta'/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);name=dest.relative_to(REPO).as_posix();files.append(name);row.update(status='text_redacted'if n else'complete_new_or_changed_text',redactions=n,archive_path=name,archive_sha256=H(data))
 rows.append(row)
(D/'.gitattributes').write_text('* -text\n',encoding='utf-8');(D/'SOURCE_INDEX.json').write_text(json.dumps(dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_phase23_commit='01232718ef0ae41207dc50315d1bdbdeaa1c60d9',unchanged_reference_count=refs,rows=rows,not_captured_yet='Later-created or changed progress, final, native reference source/seals and handoffs remain pending next append.'),indent=2),encoding='utf-8')
note='''# Phase24 — actual first quality screen, no candidate promotion, dependency-complete evaluation and embedded-reference software proof

## Primary outcome, not update-count completion
Human2026-11-02 23:39 corrected priority: training volume serves actual original skill pass rate, robustness and retention. Goalrev12 active, original80% intermediate/90% each final unachieved. No candidate promotion, no blanketallpass/3000/loss/RC0 substitute. H1, Registryv12 mothers/scopedbest and oldcandidates unchanged. A0 E02520/E22392 keptseparate; actualA1 E32182/W351973 were fullysaved/closed/settled/released viaoriginalSTOP_AFTER_SAVE, other6 zero-update freshbaselines, nottrained. No signals or active source/physics/DR/speed/acceptedthreshold/ledger/budget/lock changes.

## Actual V1 frozen loops and unsuccessful close
NEW actualoriginalN80 E3/W35 microbatch admitted originalsingleGPU/privateEX/globalfiniteEX/Creadonly protocol. Bothrealpolicy loops fullyran E3160/W351600, strictsourceRSL6219.../wholeA1CPUcache/pi/normguards passed, no optimizer/history/replay/RNGrestore or N80slice, no motherPTreopen. Then AppV6 close helper lacked static resume_runtime_contracts_v3 import. BothWORKER_ERROR and semanticexecutionfalse despite RC0. Actualparentwait andleasesrelease completed. Oldfailure/root/source/output preserved, nothotpatched. Do not callthis qualifiedfinalacceptance.

E3 originalrequestedrecipe0..11 firstepisodecredited0/74, normal6 excluded (all6 physicalterminated separately). W35 pooled26/86 isNOTmovingrate. A distinct once-only actualgradingpurpose streamed onlyitsNEW rawPositionalRows227 artifact remotely, no rawdownload oroldrawlabelreread:438attempted/438written/drop0/schema5; data139126B/38237f67eac0fcaa76efc597d7bddacb86b51c2b6393648509f29ab1aa832e81. Originalmoving10/69=14.4928%,false59/partial143; standing16/17=94.1176%,false1/partial33; unknown0. Reset/timeouts/partials exposed andoriginalconditionaldenoms retained. MovingWilson95[.08067,.24664],standing[.73018,.98954] descriptive. No pooling, no originalfullskill90claim, no matchedsameprotocolmother/pose/UID/cohort/relativeimprovement orcausalregression evidence. Decision KEEP_REGISTRY_V12_SCOPED_BEST_NO_CANDIDATE_PROMOTION; no furtherbaselinevolume scheduled justtoreach3000.

## V2 dependency-only correction and collector filename erratum
NEW V2source14/index69688... adds only22337B/dc4bc... originalstdlib resume contracts; original13source bytes/actor/acceptedcontrol/physics/resourceparent unchanged. ActualfullAppV6+baseimport verified(no stub/SDK/PT/C) beforestage andafterstage. Newroot ...MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_20261103_011752_1793639872103756500 sourcepreflight3600files andonceactualstageRC0 succeeded. InitialLOCALcaller thenrequestedoldSTAGE_COMPLETE_MICROBATCH_V1 filename, exited1 aftersuccessfulremoteoperation. Errorreport kept. NEWreadonlycollector recoveredexistingactualV2receipt, SHA993bf46284d208c5bf63d5bc55f8a121180b50ac96205373a68fada5d0e80941; stageNOTreplayed. Onlyunconsumedlocaldispatcher/observerfilename correctedbeforefirstexec; no native/sourcehotpatch. Actualnewparent1496791/ticks138166132 Popenonce1793640277.562, originalresourcegates/1800wait retained. Atv13handoffpublishedsnapshot1793641105 stillErrno11/locks0/noSDK-selectedmodel/Cwrites0, notsceneready. Capturecurrentpublishedmetadataasofcapture; lateradmission/final/timeout maysupersede andarependingnextappend. Neverextend/clearforeignlocks orreplayconsumedstage/dispatch/watcher.

## Embedded teacher reference: source and actual CPU proof, not native skill
Adapter400e06... remainsunchanged. V1ownsyntheticCPUfixture reached4N80positiveRSLmean/RNGchecks, then wronglyrequiredteacherpersistentnorm/buffer; actualapprovedRSLschema isstd_param+8MLPweights/bias, legitimateidentitynormalization/no teacherbuffers. Failure preserved, notproductionrestorebug. NEWfixtureV2 16128B/246f8... changesonlyschema-awaretestcases, withisolatedNEWownsyntheticnegativecaches(no rearm). ActualTorchCPU V2RC0:4xN80 originalRSLmeanerror0, candidate-residual mathematicaldifference.1559954(not effect), exactSTD full-value independentlydetected then originalwholemean/stickyguard, residualobs_norm.meannegativeisolatedanddetected, teacherbufferexplicitN/A(actualkeysrecorded), globalRNGunchanged. No originalPT/SDK/GPU/native/optimizer/C/locks. Itprovesreference software math, not actualmotherperformance orpairedcohort. Newnativeembeddedteacher source taskonlypendingatcapture, do notclaimimplemented/staged/graded.

## Only source hypotheses and disabled single factors
NEWonepage5317B/fb7d2346...+disabledJSON9151B/338dc7fd... combinesactualdiagnosticwithsealedprioraudits. FourUNPROVENhypotheses:unboundedresidual/off-modelreward/doneexploitation;100Hznoisy/delayedraw35vsWMstateinconsistency;recoverytime/phaseprediction;orientationcostpathcompetition. Verifiedrecoverycounters ARE learnedaux delta(not held), frames+1. H16=.32s vsstable50feedbackticks=.5s/request300=3s, criticbootstrapmeansshortHnotprovenfailure. E3vx0orientationcost20gx²+16gy² givesuprightandinvertedzero butpositive90deg, nottotalreward=0 orrootcauseproof. Onlybound-only .05*tanh vsunbounded andE3H32-only separatelypre-registered, implemented/enabledfalse; no newreward/task/physics/DR/speed/acceptancethreshold. Firstqualifiedevaluation+actualteacherreference, then decide futuretargetedtraining; no blindvolume.

AllactualV1results/closefailure/rawconsumergrade/nonpromotion,V2source/importtests/stage/readererror/correctedreceipt/dispatch/progress, embeddedreferenceV1fixturefailure/V2pass, sourceplans andv13handoff preserved. Models andrawcontents excluded fromGit reads; producerpath/bytes/SHArefs retained. Otherpostcapture source/progress/seals/handoffs pendinglaterappend. Feature-onlyuniqueannotatedtrial; mainreadonlyindependentlyadvancing. Thisarchive isnotproof of improved skill orgoalcompletion.
'''
(D/'NOTE.md').write_text(note,encoding='utf-8');files +=[(REL/n).as_posix()for n in('.gitattributes','SOURCE_INDEX.json','NOTE.md')]
original_git=record_experiment.git
def exact_short_git(*a):
 if len(a)>=2 and a[:2]==('add','--'):
  dest=a[2];selected=set(a[3:]);assert selected==set(files)and all(Path(x).is_relative_to(REL)for x in selected)
  value=original_git('add','--',dest,REL.as_posix());assert set(original_git('diff','--cached','--name-only').splitlines())==selected|{dest};return value
 return original_git(*a)
record_experiment.git=exact_short_git
sys.argv=['record_experiment.py','--id','mod4v1-supermimic-first-quality-screen-dependency-complete-eval-phase24','--title','Preserve first original skill screen, nonpromotion, close dependency fixes and embedded teacher CPU proof','--kind','evaluation','--note-file',str(D/'NOTE.md'),'--validation','Outcome-first;E3-original0of74;W35-moving10of69-standing16of17-partials-exposed;V1close-failed-notqualified-keepmother;V2deps-complete-originalwait-stage-not-replayed-reader-erratum;embeddedteacher-ownCPU-V1fixture-failed-V2mean0-std-and-residual-guard-PASS-notnative;bound-H32-disabled;no90claim-no-modelraw-Git-reads','--files',*files]
record_experiment.main();print(json.dumps(dict(commit=G('rev-parse','HEAD'),branch=G('branch','--show-current'),entries=len(rows),unchanged_references=refs,new_text_files=len(files),status=G('status','--porcelain')),indent=2))
