from pathlib import Path
import runpy,json,traceback,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
old=T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90B_20261027/archive_closed90B_native_and_delegated_W35_ordinary_once.py'
previous=runpy.run_path(str(old),run_name='ordinary90_definitions_only');s=previous['s'];ID='mod4-native97-flat-task-focus-and-e3-400n-50hz-first-learning'
for a,b in [("'fudan':'mod4-native-flat5cm-supermimic-first-training90'","'fudan':'"+ID+"'"),("nr=T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90B_20261027'/'reports'","nr=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028'/'reports'"),('ordinary_closed90B_native_and_delegated_W35_actual_CPU','ordinary_closed97_formals_and_stage10_runtime_conflict'),('CLOSED90B_W35_ORDINARY_GIT_NOTE.md','CLOSED97_STAGE10_ORDINARY_GIT_NOTE.md'),('ORDINARY_CLOSED90B_W35_CAPTURE_STARTED_ACTUAL.json','ORDINARY_CLOSED97_STAGE10_CAPTURE_STARTED_ACTUAL.json'),("TAG='trial-20261027-'+ID;D=G/('versions/20261027_'+ID)","TAG='trial-20261028-'+ID;D=G/('versions/20261028_'+ID)"),(" or p.name=='NOMINAL400_GAS_ONLY_OVERLAY_NOT_ADMITTED.usda'",'')]:
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
ns={'__name__':'closed97_ordinary_definitions_only','__file__':previous['ns']['__file__'],'same_sha_entries':{}};exec(compile(s,ns['__file__'],'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='83223781238bcc5c3a77db968e595d64a6ad75a0' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1468
 scope=json.loads((R/'CLOSED97_TWO_QUALIFIED_FORMALS_AND_REAL_EVENT_SCOPE_ACTUAL.json').read_bytes());assert scope['original_two_models_initial_CPU_qualified']
 a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert a['status']=='ACTIVE' and a['rrule']=='FREQ=HOURLY;INTERVAL=1' and a['prompt']==(R/'CURRENT_CLOSED97_ACTUAL98_AND_STAGE11_DETACHED_MONITOR_V11.txt').read_text('utf8').rstrip('\n')
 ns['prior'](G/'versions/20261028_mod4-native97-flat-task-focus-and-e3-400n-50hz-first-learning/COMPLETE_FILE_CAPTURE_INDEX.json')
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 roots=[N,L/'TWO97_correct_normal900_dual_native_PPO_collector_source_v1',L/'TWO97_NEW_H1_NATIVE_FORMAL_INITIAL_CPU_SOURCE_V1',L/'TWO97_NEW_E3_PPO_FORMAL_INITIAL_CPU_SOURCE_V1',L/'NEW_HOST_STAGE10_READONLY_TERMINAL_FULL_LOG_SOURCE_V1']
 extras=[T/'prepare_stage10_readonly_terminal_new_source_once.py',T/'finish_stage10_reader_after_local_absent_lowercase_token_once.py']
 note='''Ordinary supplement only of already consumed actual97 unique phase. Both original finite slots fully closed and two NEW formal models transferred once/full twohost SHA. Native H1 256231497B/6b3c8e9ddb56cac053e7ab386a4ec89723b799a6d4147f65232ad1e889824074 qualified by one initialNEW formal load and one necessarynormal86 witness, no source93 decode. Global12066/120660WM/11682Pi, NEW13740WM1310Pi. E3 normalPPO formal14715029B/1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8 qualified by oneNEW wholeCPU/inputPT0;87NEWPPO/17Adam866060. Native/PPO rules distinct. Strictfullfinite models/norms/optimizers/actual400 reset-preload/clock/source/normalduration/allout and literal frozenRSL passed. Never rereadweights for archive or statistics.

Original sole72 raw fees independently sumonce H1 3615.187491416931+E3 3644.546591281891=7259.734082698822; closed531527.5335400105 is a snapshot, no refund/recharge/secondwriter. Originalowner595647/nodes/workers out/CNone/private/shared locks free at actual collection. Collector54761 returned normally; preserve fullall originalUTF8 including141306793B curve and1310 focusreceipts. Formal3500 controls14336000transitions/14000callbacks; flat34502attempts/0observedtakeoff/height/landing/recovery with69invalidenvcallbacks retained, not falsely declared fullvalid. Lastcurve3499 formal separatelyexports3500 events. Focus49.569% attemptedstarts actuallyselected, notuniqueenvs orairborne data. No jump skill from updates or rewards.

Stage10 original terminal actually failed because officialIsaacSimcore6.0.1 requiresTorch2.11 against2.10cu128, nottimeout. InitialNvidia DNS retries/fullprimary errors and allreadonly fulltext preserved. Known ownsup/installer/pipout/lockreleased, noGPU/model/GO/account. Newreadonly reader and localstrictpreparer absentlowercase-token error retained, correctmissing-only source finished before network. No oldlauncher rerun. SameACTIVEhourly/noGoal preserved; V10/V11 handoffs and app toolresults captured. Actual98 NEWfrozen motion and E0regression andStage11 source/startup are next uniqueactual98 phase capture, not part of this ordinaryscope; activefutureStage11terminal/transitiontap explicitlypending. Keep1468oldtagobjects/peels; do notrecord/tag97again. Fullsource/errors/false/reports and orderedUTF8parts; binaries actualpath/bytes/existingproducerSHA only, no content/GPU/host queries forGit. PostGit verification conversationonly.
'''
 ns['run_stage']('fudan',roots,extras,note,'Qualify complete native97 and E3 finals and preserve Stage10 runtime dependency failure')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/'ORDINARY_CLOSED97_STAGE10_ARCHIVE_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_never_record_tag_again=True),f,indent=2)
  raise
