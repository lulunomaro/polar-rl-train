"""New actual97 learning phase. Binary contents never read for this archive."""
from pathlib import Path
import json,runpy,traceback,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
old=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V95_20261028/archive_actual95_failure_and_repaired96a_first_runtime_unique_once.py'
prior=runpy.run_path(str(old),run_name='old95_archive_definitions_only');s=prior['s']
ID='mod4-native97-flat-task-focus-and-e3-400n-50hz-first-learning'
for a,b in [("'fudan':'mod4-native95-h1-task-focus-e3-400n-50hz-runtime-repair96a'","'fudan':'"+ID+"'"),
 ("nr=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V95_20261028'/'reports'","nr=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028'/'reports'")]:
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
ns={'__name__':'new97_archive_definitions_only','__file__':prior['ns']['__file__'],'same_sha_entries':{}}
exec(compile(s,ns['__file__'],'exec'),ns);git=ns['git']

def main():
 assert git('rev-parse','HEAD')=='23106184714a8c3296318e952f93db2c06e013a2' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1467
 first=json.loads((L/'TWO97_H1_E3_COMBINED_FIRST_INLINE_SOURCE_V1/reports/TWO97_ALL_FIRST_POLICY_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json').read_bytes())
 assert first['actual_finite_returned'] and first['results']['h1']['passed_first_NEW_native_policy'] and first['results']['e3']['passed_first_E3_real_PPO']
 a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert a['status']=='ACTIVE' and a['rrule']=='FREQ=HOURLY;INTERVAL=1' and a['prompt']==(R/'CURRENT_ACTUAL97_TWO_FIRST_UPDATES_STAGE10_DETACHED_MONITOR_V9.txt').read_text('utf8').rstrip('\n')
 seed=G/'versions/20261028_mod4-native95-h1-task-focus-e3-400n-50hz-runtime-repair96a/COMPLETE_FILE_CAPTURE_INDEX.json'
 ns['prior'](seed)
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 names=['E3_97_GAS400_COMPLETE_RUNTIME_SOURCE_CPU_PREPARATION_V1',
  'TWO97_H1_E3_NEW_FULL_CPU_OWNER_SOURCE_V1','TWO97_H1_E3_COMBINED_FIRST_INLINE_SOURCE_V1',
  'TWO97_correct_normal900_dual_native_PPO_collector_source_v1','TWO97_NEW_H1_NATIVE_FORMAL_INITIAL_CPU_SOURCE_V1',
  'NEW_HOST_STAGE10_TINY_PACKAGING_TLS_SHA_CACHE_CONTINUE_V1']
 roots=[N,*[L/name for name in names]];assert all(p.is_dir() for p in roots)
 extras=[T/'prepare_native97_unique_diagnostic_receipts_and_new_payload_once.py']
 note='''Actual97 real learning confirmed on both genuine original72 slots. Run TWO97_REPAIRED_DIAGNOSTIC_IO_AND_E3_NOMINAL400_1793175809325083200 has one original canonical writer and two source-admitted finite nodes, H1c27 native SuperMimic and E316828 normalPPO. Firstcombinedreader returned bothpassed. These are snapshots of actualupdates, not continuousalive/fullFINAL/convergence/skill. Original finite jobs continue on their owner/save/exit/account contract without interruption for Git. No hotpatch/kill/secondwriter, no healthy emptyGPU recheck.

H1 actual400Nbackend/preload/genuinefirstreset and fullnative93restore passed, firstcoherent240controls4096env=983040transitions, NEW700WM6Pi, global10762/107620/10378. FirstnewPi226controls650NEWwm. OwnWM+imaginedrollout/BPTT, notRSLPPO; literalfrozen86RSL832460 stays separatewitness. Source95taskfocus retains realpairedreplayrows and uses desiredhalfphasefocus with max8originalsamplercalls/uniformfallback; changedRNGdrawcount declared, no sole-cause/learninggain claim. Native97 changes only unique-per-call diagnosticreceipt filename, preservingimmutableatomic_json collisionguard. Original96Asecond-callFileExistsError was a loggingintegrationfailure, notbrokenautograd. Actual oldcallbackfailure and correctedtwocallIO checked withoriginalatomic_json, then NEWtargetsourceSDK/fullstateCPU passed onelegitimateadmissionpurpose. Allsource/false/read-onlyshell/schemaerrors retained; no oldmodels readmerelyforstats/Git.

E3 actual400N runtime SDK/observernominal values are now2000 inexactthreeproductiondependencyfiles, assertions/setters/RNG/DRfactor.9..1.1 andoriginal13recipephase preserved. Newsourceexactinverseproof andbytecomparison toalreadyactualE2/E0/W35400 implementation retained. New actualsourceSDK/fullstateCPU passed typed59fa input once, originalactor35/critic38/STD/17Adam864320/LR/D1-D7/32MBnearest34bank/20msqueue/actualassetparentcontract517c. ActualGPUfullCUDArestore/native24=192physicscallbacks48feedback/24RMcompute(dt.02)once/nominalpreload passed, then PPO1/Adam864340. Positive14713712B/cba43a634905ac0aa083e5512904114c39adf7ff58843be73309385be892ed20 isproducer-onlymetadata, no earlymodeldownload/hash/promotion. E3 is normalPPO adaptation, notnativeSuperMimic orcompletedskill. ExistingE0/W35/E2adaptedmodelskillregression remains pending, gate148 is not independent40050graduation.

Bothnew97inputs/sourceSDK/CPU reports andactualexternalwaitproofs are genuine new code-admission purposes. SourceH1 remainsqualified93b008...10692/106920/10372; E3inputnormal86B61c...typed59fa...864320; failed95/96Apartials never promoted. Original97fees/fullformalclosure/wholeinitialNEWformalCPU/skillchecks remain pending. Correctnormal900earliestepoch1793178879.9221745 BJT17:14:39.922, save17:24:39.922,nominal17:29:39.922. Local+remote gate unchanged, time notcompletionproof. New97collector frozen/UNUSED retainsoriginalowner850/node180/whole1140, rawindependentfee sum, allout/CNone/private/sharedlocks, exact2formaltransfer/twohostSHA, originalomni-onlyfreshsnapshotexception andselectedparentfallback. Nativeformalreviewer V2 frozen/UNUSED: oneNEWformal+onefrozen86witness/inputnative93zero, fullfinite strictmodels/norms/threeopts/sourceargs/counters/producer/gas100Hz andfees/allout gatesbeforeweights. Nativeopt_v20*globalPi distinctfromPPO20Adam/update. E3newformalreviewer source isexplicitpendinguntilfrozen, no oldE2schema reuse. No source/witness rereadforstatistics orGit.

Currentactualresourceuse is two confirmedlearning cards. Source210 frozenexpertregression/typed50Hztransitiontap is mutableSOURCEPENDING and excluded untilfrozen/actualadmission; checkpoint is not WMdata. New86Stage10 actuallydetached startupreturned0, sup509296/create1793176832.73 installer509297/.78,1800s deadline. It reusesexactStage9runtime/metadata/cache/Torch/vision/completeKit, stagesofficialtinyPackaging26 withTLS/publishedSHA andboundednetworkretry3, thennormaljointrequiredresolve/install/pipcheck. It changes no runtime.py/dependencyrequirements/systemDNS and is notGPU/SDK/PPOready untilactualproof. Stage9temporaryDNSfailure source andallpriorfailedsetups are retained inprecedingphase. Stage10terminal/source210data futureoutputs explicitlypendingordinaryappend, no repeatedonce/model/raw downloads. GPUoccupiedbythirdparty remains untouched; usernew86project-only/data/robemo/polar-rl-train, credentialsnoechoSTDIN/memoryonly.

SameACTIVEhourlymod4-10/originaltarget, continuousGoal remainsabsent; no newmonitor/Goal. Notificationsonlymeaningfulcompletion/failure/materialrepair/resources/budget/action; healthy/sourcependingquiet. Physical2.5ms/TGS32/4/FP32/actionclip6/PD/delay/DR,2mmperenvreset/1umoldquery/native160kevidence reuse unchanged; no extraFP64/bitwise/triangle auditgate. Nominal400Nengineeringassumption notmeasuredforcecurve/full140stroke. Actual5cm dualwheelclearance/real12floorlanding/200stablecallbacks and ultimate270cross/fullfootprint/topcontact12/200stable unchanged. No skill claimfromfirstupdates/imaginedscore/GPUutil.

One new unique actual97 phase, preserve1467oldtagobjects/peels andpreceding95/96Aactualcosterrors. FullsavedUTF8/source/errors/false/reports/orderedtexts; binaryindex only actualpath/bytes/existingproducerSHA, unknownstaysunknown, noPT/raw/USD/NPZ/GPU/hostreadforGit. Activefuture210/Stage10terminal/E3reviewer explicitlypending afterfreeze andlaterordinaryappendonactualHEAD; do notrecord/tag97again. Pushfailurecontinuesexistingobjects. PostGitverificationconversationonly,no reportchasingHEAD.
'''
 ns['run_stage']('fudan',roots,extras,note,'Run real native flat-jump and E3 400N 50Hz learning after diagnostic IO and runtime nominal repairs')

if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/'ACTUAL97_UNIQUE_ARCHIVE_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_never_retag=True),f,indent=2)
  raise
