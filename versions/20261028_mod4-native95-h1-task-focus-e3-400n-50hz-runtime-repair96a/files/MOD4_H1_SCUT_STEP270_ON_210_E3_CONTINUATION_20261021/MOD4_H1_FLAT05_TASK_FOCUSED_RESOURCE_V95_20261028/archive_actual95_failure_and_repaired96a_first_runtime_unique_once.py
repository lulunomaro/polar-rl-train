"""One real95/96A phase, preserve both early failures and corrected runtime."""
from pathlib import Path
import json,runpy,traceback,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
old=T/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028/archive_actual93_diagnostic_W35_full_and_two_learning_slots_unique_once.py'
base=runpy.run_path(str(old),run_name='old93_archive_definitions_only');s=base['s']
ID='mod4-native95-h1-task-focus-e3-400n-50hz-runtime-repair96a'
for a,b in [("'fudan':'mod4-native91-diagnostic-w35-adaptation-and-terminal-repair93'","'fudan':'"+ID+"'"),
 ("nr=T/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028'/'reports'","nr=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V95_20261028'/'reports'"),
 (" or p.name=='NOMINAL400_GAS_ONLY_OVERLAY_NOT_ADMITTED.usda'",'')]:
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
ns={'__name__':'new95_96a_archive_definitions_only','__file__':base['ns']['__file__'],'same_sha_entries':{}}
exec(compile(s,ns['__file__'],'exec'),ns);git=ns['git']
def read(p):return json.loads(p.read_bytes())

def main():
 assert git('rev-parse','HEAD')=='7dc150bdd7a96c206272fdde1da4ec0af49f4166' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1466
 failed=read(L/'TWO95_EARLY_TERMINAL_READONLY_FORENSIC_SOURCE_V1/reports/TWO95_EARLY_ORIGINAL_TERMINALS_COST_FULL_TEXT_RETURNED_ACTUAL.json')
 assert failed['actual_readonly_finite_returned'] and all(x['original_out'] for x in failed['identities'].values())
 actual=read(L/'TWO96A_H1_E3_SAME_SOURCE_ROUTE_REPAIR_V1/reports/TWO96A_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json')
 assert actual['actual_two_real_nodes_launched']
 first=[]
 for directory in L.glob('TWO96A*'):
  if not directory.is_dir():continue
  for p in (directory/'reports').glob('*.json'):
   v=read(p)
   if v.get('actual_finite_returned') and set(v.get('results',{}))=={'h1','e3'}:first.append((directory,p))
 assert len(first)==1,'exact new96A first reader must actually return before unique capture'
 a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert a['status']=='ACTIVE' and a['rrule']=='FREQ=HOURLY;INTERVAL=1'
 seed=G/'versions/20261028_mod4-native91-diagnostic-w35-adaptation-and-terminal-repair93/ordinary_closed93_formals_actual95_CPU_new86_dependency_repairs/ORDINARY_CAPTURE_INDEX.json'
 ns['prior'](seed)
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 names=['flat95_task_focused_real_replay_source_v1','native96_H1_GO_alias_binding_source_v1',
  'E3_PPO50_gas400_source_preparation_20261028','THREE95_H1_E3_mixed72_source_v1',
  'TWO95_H1_E3_combined_first_actual_policy_observer_source_v1','TWO95_EARLY_TERMINAL_READONLY_FORENSIC_SOURCE_V1',
  'TWO96A_H1_E3_SAME_SOURCE_ROUTE_REPAIR_V1','TWO96A_EARLY_TERMINAL_READONLY_FORENSIC_SOURCE_V1',
  'native97_unique_sampler_diagnostic_receipts_source_v1','NEW_HOST_STAGE9_VENDOR_PACKAGING26_SOURCE_20261028',
  'NEW_HOST_STAGE9_READONLY_TERMINAL_FULL_LOG_SOURCE_20261028']
 roots=[N,*[L/name for name in names],first[0][0]]
 assert all(p.is_dir() for p in roots)
 extras=[T/'prepare_native95_task_focused_qualified93_continuation_once.py']
 note='''This actual95/96A phase retains the full failed deployment, its original cost, and the exact corrections. First95 source/SDK CPU admission passed qualifiednative93 fullstate plus frozen86 witness in a separate initial admission purpose; E3 typed normal86B59fa03e6.../Adam864320 and its actualSDK initialCPU also passed. Model architecture, normalizers, three native optimizers and frozenRSL832460 are preserved; E3 is normalPPO and its own17Adam has the distinct20steps/update rule. H1 true5cm wheelbottom clearance/12actualfloorlanding/200stable callbacks and ultimate270mm criterion remain unchanged. No skill graduation is claimed from source/CPU/update counts.

Native93 source10692/106920WM/10372Pi had full3654controls/34503requests/zero takeoff. Source95 boundedmixture requests half real-replay imagination starts during200ms preparation through flight, at most8originalsampler calls and uniformfallback. Whole paired states/histories unchanged; extra sampler RNG draws explicitly differ. No reward/physics/action/WMarchitecture/learnerBPTT or normalizer reset. Six sourceCPU scopes retain actual93 phase coverage evidence; 4.7percent flight starts is a diagnostic lead, not proven sole cause or learning gain. Saved learningseed27 separately bound.

Actual95 run TWO95_TASK_FOCUS_H1_E3_PPO50_GAS400_1793172150501997200 had two genuineGO and then two early deployment failures. H1 failedpreSDK unchangedABIguard because signedGO omittedlogical_slot/canonicalworkerkey; E3 AppLauncher initialized but runtime import failed due missingruntime/assets/import_contract.json beforemodelrestore/scene. H1fee3.654658794403076 andE3fee16.128061771392822 summedonce19.7827205657959 byoriginalsole72writer, closed539450.9840764999/CNone. Knownowner589937/nodes/workers allout; 187completeoriginaltexts and fullreadonly canonical snapshot preserved as evidence, never anotherauthority. SDKrc0 does not override primaryE3error/noFINAL/noPPO. Failed95 is resource/error provenance, not learned source. No refund/recharge/clearactive/secondwriter.

The original95 first reader failed beforemain on Windows siblingmodule import; explicitSHA-boundimportpreloader preservedoriginalsource then consumed actualnetwork reader, which found originalowneralreadyout and raisedNoSuchProcess before policy snapshots. Originalfalse/errors are retained, firstonce neverrerun. New earlyterminalforensic was a differentread-only purpose, not weakeningnormal900collector for a nonexistent healthyFINAL. It queries only originalexactknownidentities, retains alltext/GO/originalfees, noPT/GPU/kill/lockdelete/accountwrite.

New96A fixes deployment only: originalH1validate_task_go reproducedoldactualGOrejection, adding exactlytwosignedaliasfields passesunchangedguard andwrongaliasnegativesreject. Publicspec nowexplicitlogicalsloth1/nativecanonicalh1. E3 only adds the already-validated517cdcontract at actualRM_MOD4_USD.parent/runtime/assets/import_contract.json; worker/runtime.py/typedmodel/clock/DR/RNG unchanged. New96A input namespaces copy onlysealedmanifestinputs, neverGO/output/oldmarkers. Bigimmutableinputs useexactsameinode/stat andexistingproducerSHA; no repeatedPTdecode/hash. Same-source extensions explicitly referenceoriginal95CPU and actual externalwait OLDpath/argv, not a pretendnewCPU. OriginalSDKversions and sourcebytes guarded. The first96A inputextension failed comparingLF-normalizedmanifesttext tooriginalCRLFrawSHA afterpartialcopy. Error/partial retained. NEWmissing-onlyfinisher usesbase64exactoriginalrawmanifestbytes/SHA, verifiesexistinginputs and writesonlymissingE3manifest/extension; no oldonce rearm, no newmodelCPU.

Repaired96A actualsingle72owner/two genuineH1+E3nodes launched from newnamespaces with exactextensions/GOalias/sourceCPU pins. The new96A oneboundedfirstreader returned with bothroles rejected due originalruntimeerrors. H1 actual400N/reset/preload/nativelearning reached a second task-sampler call, whose diagnostic callback incorrectly reused an immutable atomic_json filename and raisedFileExistsError. E3 sceneinitialization reached SpringPressureSDK assertion because three inheritednominal-observer sources still expected3500 ratherthan declared2000. Neither has a healthy coherentfirstpublication orqualifiedFINAL. Exact partialprogress is retained in originalproducer/error receipts, not guessed or promoted. Newearlyterminalforensic confirmsoriginalowner591209 andbothnodes/workersout, CNone, originalsumonce663.7164537906647 (h1258.2691116333008+e3405.4473421573639), closed538787.2676227093. No refund/recharge/clearactive/secondwriter. Full238originaltexts andread-onlycanonical snapshot retained. Normal900collector is not run for these earlyfailures.

H1 source-only97IO repair changes only diagnosticreceiptfilename to include monotonicallyincreasing sampler-callnumber. Originalcallback plus actualatomic_json reproducessecond-callfailure; correctedcallback writesfirsttwoseparatereceipts andstillrejectsduplicatecall-ID. Originalatomic_json/learning/sampler/reward/physics/models/norms/opts unchanged. Frozenproof andcandidateentrycaptured. NEW97 completepayload/sourceSDK CPU andE3nominal-runtime fix are separate explicitpendingwork until their actualGPUphase, not falsely called95/96Alearning success. Original3900/3600/300 finite/save/exit andoriginalnormal900 closinggate unchanged. No earlymodeldownload/promotion or skill inference. Git does not pause or block any healthyjob.

New86 Stage9 source reuses existingcachedofficialKit/Torch/vision and typedcoverage-extra/packaging26 metadata delta withruntime.py unchanged. ActualStage9 failedearlyrequiredjointresolve becausefiles.pythonhosted.org DNS Errno-3 fetchingpackaging26 metadata, not a newlyproven dependencyconflict. Terminal/exit/knownallout/fulloriginalUTF8 logs collected; noSDK/CUDA/GPU/PPO on86 is claimed. Future boundednetworkrepair/source210 frozenregression+typedWMtap are explicitlypendingmutable until frozen, excluded here and must be appended later. Checkpoints are not WMtransitiondatasets; native100Hz and normal50Hz domains require exacttyped actualactions/queues/physics/DR before reuse.

All prior93 andordinary7dc150... objects retained,1466oldtags/peels protected. One new uniqueannotatedactualphase only, no93retag. All savederrors/false/source/CPU/actualGO/forensic/monitor/newreader results fullUTF8/plainordered; binaries only actualpath/bytes/existingproducerSHA, unknown remainsunknown. No PT/raw/USD/NPZ/GPU/hostread forGit, no stop/hotpatch/ledger mutation or repeatedonce. SameACTIVEhourlymod4-10/target, no continuousGoal/newmonitor. PostGitverification conversationonly, no reportchasingHEAD.
'''
 ns['run_stage']('fudan',roots,extras,note,'Repair H1 task-focus and E3 adaptation deployment; retain original failed95 costs and actual96A runtime')

if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/'ACTUAL95_96A_UNIQUE_ARCHIVE_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_never_retag=True),f,indent=2)
  raise
