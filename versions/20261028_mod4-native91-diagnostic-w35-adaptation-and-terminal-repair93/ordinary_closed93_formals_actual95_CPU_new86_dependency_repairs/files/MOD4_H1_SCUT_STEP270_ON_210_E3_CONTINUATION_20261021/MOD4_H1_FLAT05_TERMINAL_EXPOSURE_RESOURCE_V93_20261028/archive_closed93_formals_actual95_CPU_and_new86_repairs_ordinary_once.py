"""Supplement consumed93 only; preserve all tags and use existing binary SHA."""
from pathlib import Path
import runpy,json,traceback,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
old=T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90B_20261027/archive_closed90B_native_and_delegated_W35_ordinary_once.py'
definition=runpy.run_path(str(old),run_name='ordinary_engine_definitions_only');s=definition['s']
for a,b in [
 ("'fudan':'mod4-native-flat5cm-supermimic-first-training90'","'fudan':'mod4-native91-diagnostic-w35-adaptation-and-terminal-repair93'"),
 ("TAG='trial-20261027-'","TAG='trial-20261028-'"),
 ("D=G/('versions/20261027_'+ID)","D=G/('versions/20261028_'+ID)"),
 ('ordinary_closed90B_native_and_delegated_W35_actual_CPU','ordinary_closed93_formals_actual95_CPU_new86_dependency_repairs'),
 ("nr=T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90B_20261027'/'reports'","nr=T/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028'/'reports'"),
 ('CLOSED90B_W35_ORDINARY_GIT_NOTE.md','CLOSED93_ACTUAL95_CPU_NEW86_ORDINARY_GIT_NOTE.md'),
 ('ORDINARY_CLOSED90B_W35_CAPTURE_STARTED_ACTUAL.json','ORDINARY_CLOSED93_ACTUAL95_CPU_NEW86_CAPTURE_STARTED_ACTUAL.json'),
 (" or p.name=='NOMINAL400_GAS_ONLY_OVERLAY_NOT_ADMITTED.usda'",'')]:
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
ns={'__name__':'ordinary_closed93_definitions_only','__file__':definition['m'].ns['__file__'],'same_sha_entries':{}}
exec(compile(s,ns['__file__'],'exec'),ns);git=ns['git']

def main():
 assert git('rev-parse','HEAD')=='ca8cbff6ebc937ee01fbcad8b86b13f90d08163c' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1466
 tag='trial-20261028-mod4-native91-diagnostic-w35-adaptation-and-terminal-repair93'
 assert git('rev-parse',tag)=='01ed5ab17088e2078bc77fc18c63293e5483a2f8'
 seed=G/'versions/20261028_mod4-native91-diagnostic-w35-adaptation-and-terminal-repair93/COMPLETE_FILE_CAPTURE_INDEX.json'
 ns['prior'](seed)
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 prompt=R/'CURRENT_CLOSED93_ACTUAL95_CPU_STAGE9_DETACHED_HOURLY_MONITOR_V6.txt'
 actual=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 assert actual['prompt']==prompt.read_text('utf8').rstrip('\n') and actual['status']=='ACTIVE' and actual['rrule']=='FREQ=HOURLY;INTERVAL=1'
 roots=[N,T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V95_20261028',
  L/'THREE93_correct_normal900_collector_selected_parent_fallback_v2',
  L/'NEW_HOST_PINNED_DEPLOYMENT_STAGE7B_VENDOR_TEST_DEPENDENCY_SPLIT_20261028',
  L/'NEW_HOST_PINNED_DEPLOYMENT_STAGE8_DETACHED_VENDOR_INSTALL_20261028',
  L/'NEW_HOST_STAGE8_READONLY_TERMINAL_FULL_LOG_SOURCE_20261028',
  L/'NEW_HOST_STAGE9_VENDOR_PACKAGING26_SOURCE_20261028',
  L/'flat95_task_focused_real_replay_source_v1']
 extras=[T/'prepare_native95_task_focused_qualified93_continuation_once.py']
 for root in roots:assert root.is_dir(),root
 note='''Actual93 closure and initial formal qualification completed. Selected normal900 collector V2 returned both complete formal models, original three-slot fee7291.4024312496185, closed539470.7667970657, canonicalNone and original owner/nodes/workers out and locksfree at capture. Failed210 original51.172107219696045 included once, never recharged. V1 naming refusal retained; V2 changed only relative path naming fallback within the already enumerated owned roots. All full original texts, failed traces, false/partial and reader/source preparation preserved.

Native93 formal256230153B/b008fc03d5de3e39217101523c7e8fc0ddebf5cd6e63699582b61053171d165e qualified with one initial NEWformal CPUload plus one frozen86 witness; native10692/106920WM/10372Pi, all finite strict models/norms/threeoptimizers and literal separateRSL17Adam832460. Full3654controls/14616callbacks/14966784 transitions,34503requests,zero takeoff/height/landing/recovery, no observedflat5cm/270skill. Initial source91 not redecoded for statistics. E2NEWformal14615089B/b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1,92NEWPPO/Adam859300/stored42822, full finiteD1-D7/commands/queue/40050recipe passed oneinitialload/input0. E0/W35/E2 adaptation skillregression remains pending; gate148 is not independent expert graduation.

Actual93 phase sampling1404928starts only65859requestedflight and173371horizonintersections, not zero phase exposure. New95source increases desired task-relevant replay start weight to half with max8originalvalidsamplercalls and truthful uniformfallback. States/histories/actions/reward/WM/BPTT/physics/terminal93 unchanged; extra samplerRNGdraws explicitly change, no sole-cause/learninggain claim. Frozen6sourceCPU scopes and real93evidence retained. New95typed payload fully restoresqualified93 and preserves models/norms/threeopts/counters; savednativelearningseed27 separated fromphysicalseed. Actual95original72sourceSDKCPU passed initialqualified93+frozen86 loads in a new admission purpose, exactmanifest/source/bank/asset/strictstate guarded, actualidentity+wait0. CPU683206c9...ccada/waitf870aced...61434; installer consumed. SelectedprotocolV2 exactfocus/seedCPUvalue binding plus5wrong-field negatives, oldprotocol retained. NO95owner/GO/learning/fee yet; genuine mixedcontroller and fresh boundary still required. This source preparation is not a newGPUtrialtag. No model/raw/USD read for this Git archive; newpayload copy read its source model only for the explicitly prepared training payload, metadata distinction retained.

New86 Stage7B actual boundedfailure and full original logs retained; Stage8 original installer return1 because corepackaging26 conflictsRLpackaging<24, not timeout, all exactrecordedownprocessesout and installerlockreleased. Full18originaltexts retained. LargeofficialKit wheel downloaded5,879,615,742B/fullSHA35b64cf35ce3d31875ef43025f243c8bd03e29cb28fe844b0cd06b76ba535714 preserved metadata only. Coveragetestextra originalmetadata/source proof retained; runtime.py unchanged. Stage9newtypedpackaging26metadata fix source+actualdetachedstartup recorded, 1800s ownedboundedinstaller and exact originalcleanup, supervisor507459/installer507460 identities in originalreceipt. Stage9firstlocalattempt lacked reportsdirectory beforemarker/READY/credential/network; originalerror retained, only missingdirectory created, originalunusedbytes then started. No rearmed consumed once. Stage9terminal/packageinstall/SDK/CUDA/GPU/PPO not yet observed; mutable future terminal logs explicitly pending after collection. Credentials only noechoSTDIN/memory, pin-beforeauth, newhostproject-only no outsidepaths/globalpackages/driver or unknownprocess actions.

Samehourlymod4-10 updated to actualclosure/95CPU/Stage9detached V6; no Goal created/resumed, activehourlytarget unchanged. Original unpublishedV5 E2iterationtext typo retained with metadata-only correction before apppublish. Root H1, one existing sequentialchild oldexpert/new86; active E3source and newmixed95controller mutable EXPLICIT_PENDING until frozen/actualphase. They are intentionally excluded from this stable capture and must be appended/recorded at actual95GPUphase. No fakeH1slot/hotadd/secondwriter. All original sole72 budget/3900/3600/300/900guards, resource/startup/physics/truewheelclearance and270 criteria unchanged.

Ordinary supplement of consumed93 only. Protect all1466tagobjects/peels, no record/tag again. Full UTF8/plainordered large curve capture, all saved source/error/false/reports; binary indices only actualpath/bytes/existingproducerSHA, unknown leftunknown. Pushfailure resumes existingobjects. PostGitverification conversationonly, no newreport chasingHEAD.
'''
 ns['run_stage']('fudan',roots,extras,note,'Close native93 and E2 formals; preserve95 admission and new86 dependency repairs')

if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/'CLOSED93_ACTUAL95_CPU_ORDINARY_ARCHIVE_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_never_record_or_retag=True),f,indent=2)
  raise
