"""Unique actual91 stage: real native policy and failed W35 restore, all retained."""
from pathlib import Path
import json,time,hashlib,traceback,importlib.util,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
P=T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90B_20261027/archive_actual_flat90_native_first_training_unique_once.py'
sp=importlib.util.spec_from_file_location('consumed90_archive_definitions_only',P);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s
ID='mod4-native-flat-mask91-and-w35-ppo50-gas400-mixed'
for a,b in [("'fudan':'mod4-native-flat5cm-supermimic-first-training90'","'fudan':'"+ID+"'"),("nr=T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90B_20261027'/'reports'","nr=T/'MOD4_H1_FLAT05_MASK_AWARE_MIXED72_RESOURCE_V91_20261027'/'reports'")]:
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
ns={'__name__':'new91_actual_archive_definitions_only','__file__':m.ns['__file__'],'same_sha_entries':{}}
exec(compile(s,m.ns['__file__'],'exec'),ns);git=ns['git']

def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

def main():
 assert git('rev-parse','HEAD')=='8de4c08f09a15b81e09d389e165b56f815a45fdb' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1464
 assert json.loads((R/'NATIVE91_FIRST_ACTUAL_NATIVE_POLICY_RETURNED_ACTUAL.json').read_bytes())['passed_first_native_flat_policy']
 ns['prior'](G/'versions/20261027_mod4-native-flat5cm-supermimic-first-training90/ordinary_closed90B_native_and_delegated_W35_actual_CPU/ORDINARY_CAPTURE_INDEX.json')
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 prompt=R/'CURRENT_ACTUAL91_MASKED_FLAT_NATIVE_FIRST_POLICY_W35_FAILURE_MONITOR_SOURCE_V2.txt'
 a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert a['status']=='ACTIVE' and a['rrule']=='FREQ=HOURLY;INTERVAL=1' and a['prompt']==prompt.read_text('utf8').rstrip('\n')
 roots=[N,L/'H1_W35_next_mixed72_owner_deployment_source_v2',L/'W35_v91_retention_saved_episode_baseline_fix_source_v1',L/'W35_v91_failure_terminal_active72_fee_reconciliation_source_v1',L/'flat91_mask_aware_goal_conditioning_source_v1']
 for path in [roots[1]/'FINAL_ACTUAL91_FULL_SOURCE_ERRORS_REPORTS_INDEX_V1.json',roots[2]/'FROZEN_SOURCE_FIX_INDEX_V1.json',roots[3]/'FROZEN_FORENSIC_SOURCE_ERRORS_FULL_INDEX_V1.json']:assert path.is_file()
 optional=L/'mixed91_native_W35_corrected_closure_source_v3'
 if (optional/'FROZEN_INDEX_V1.json').is_file():roots.append(optional)
 extras=[T/'prepare_native91_masked_flat90B_continuation_once.py',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v253.py']
 note='''Actual native flat SuperMimic91 first NEW policy update passed; W35 PPO adaptation failed during saved-episode restoration. New91 unique actual phase, not another90 record. All failures/source/CPU/GO/Pi/error and reader corrections retained.

Root continues H1 native flat-jump. One delegated child owns old frozen-expert400N/50Hz/newhost work; user repeatedly requested start and four4090 utilization, and asked whether normalized models have passed. Root honestly distinguishes E0 completed82NEWPPO plus formal/recipe checks from unverified adapted skill regression; W35 has not passed newPPO or skill. No inherited graduation labels and no model-checkpoint-as-WM-dataset claim. Current PPO workers lack complete typed WM transition taps; future source-only collection and source/SDK admission required.

Root prepared exact90B-native->91 source contract preserving global7841/78410WM/7649Pi and all modules/norms/threeoptimizers, same400N physics. Source91 mask-aware goal conditioning only Policy.forward/Critic.forward plus helperimport: mask after normalized values and literal binary masks, criticprefix unchanged. Old genericcritic norm count200014848 was capped; analytic goalabsmax100 did not include extreme column index, so no claim100definitelymaskcolumn or solecause. Original6sourceCPU plus actual253 targetSDK/RSL/fullsource/NEW90Bfullstate1load+normal86witness1 passed f725/waitproof15635, no input88Cnative reread. Explicit newmethod/source/producerencoding, no action/reward/WM/phase/physics change, no parameter/norm/opt reset. One local nativecopy necessarily readbytes via shutil.copy2, original broad no-read metadata preserved with append-only scope correction; no local PTdecode or rehash forsource preparation and no binary readforGit.

Prior90B root incorrectly reported missing final3 flat-control events after reading only last3491 curve rows. Existing published.original_producer.original_H1_events.flat_real_physics_events contains complete3494controls/13976callbacks,31135attempts/0takeoff/height/landing/recovery. Originalfalsegap report preserved and new text-only addendum corrects it, no PT/raw/actor/GPU reads. This remains no observed flat5cm or270success, not permanent impossibility/frozen evaluation.

One original72 owner553988/create1793115270.2, H1node553997/create1793115270.55 and W35node554009/create1793115270.9 genuinely launched. RunH1_W35_MIXED72_MASK91_PPO50_1793115003458552300. All approvedloader/argv/exe/create verified, token memory/stdin only; originalowner.account/Handler/HMAC/charge_values/control/locks/caps unchanged except genuine two-slot dispatch. Both real sourceCPU bindings/worker/manifest/privateheldREADY required; no fake registration or independent writer. H1 static TASK remains sealed, runtimegrantbinding outside manifest. W35 fresh dynamic Task source368 remains qualified, not failed partial.

V2 activation PRE rejected Windows backslash publicowner/W35node paths before C/GPU/mkdir/upload/Task/owner/GO; source/error retained. V3 POSIX paths passed fresh2GPU/private/shared/port/CNone554499/source admission and controller/Task installation, then runpy import failed before launcher.main because owner path absent fromsys.path. NEWV4 launch-only adds owner sys.path, does not re-copy/rewrite Task/CPU/manifest or rearm a launched process. Exact two real nodes plus owner started, no retry/kill/clearactive. All wrappererrors retained. Original firstH1 reader consumed once in a new single combinedfinite, then W35 observed independently even after its original error. No secondwatcher/parallelSSH.

ActualH1source/newgas/reset/command0/phase/encoder and first NEW700WM/6Pi passed. Firstcoherent240controls*4096=.98304Mtransitions, global7911/79110WM/7655Pi. Realflat firstsnapshot663requests/0takeoff/height/landing/recovery,0selectedresets/invalidcallbacks; GPUmemory16574MiB/util28 snapshot. It is real native ownWM+imaginedrollout/BPTT, not PPO, continuousalive proof, fullFINAL, learninggain or successfuljump. Earlymodel producer metadata only, no download/hash/promotion. CurrentH1 continues under its original window, healthy slot untouched.

ActualW35 failed retention_checkpoint.resume_e1_new_episode outer witness comparison: fresh env episode baseline was captured before g3.resume restores saved E1terrain episode and performs its original one reset. Outer comparison fresh+1 mismatches already-validated saved+1. No newPPO/native24/fullrestore publication, APP_CLOSING present; worker original rc0 from SDK shutdown never erases originalerror/noFINAL. This is a restore-chain code defect, not a proven400Nphysical failure. Child minimum source-only fix changes only baseline expression to saved ck episode on env.device clone, reversebytes/AST and tiny3env/doublereset rejection proofs passed. Newretention8d3a49766a076f508118b5f84c4a1e9557d6e8a84369b9502516827336604894/sourceindexcb2e21 preserved. No live worker/source hotpatch, rearm91 or failed-source promotion. Nextunused typedsource extension/baseCPUd022 plus safe singlewriter boundary remains required.

Independent originalW35 failure forensic retained V1 readerfalse: it wrongly demanded worker rc!=0, despite originalerror/noFINAL and possible SDKrc0. NewV2 removes only that invented reader condition. Actual owner/node/worker wait/out, source failure, private/sharedfree and selected16828free24203MiB/util0/computeUUIDrows0 passed. OriginalW35fee488.166357755661s fromGO1793115273.6601048 toownerterminal1793115761.8264625 already sumonce within same ACTIVE H1 segment. C remains activeH1; remaining552678.1901903152 is only snapshot, not closedbalance. No refund/rewrite/clearactive/H1stop/secondwriter. Wholeforensic source/error/actualfee index2ab39c...0d75 captured. Fresh future resource eligibility needed; no permanentfreeclaim or unknownPID query/kill.

ActualGO H11793115273.5989633/W351793115273.6601048. Originalworker save deadlines00:34:33.598963/.660105BJT28Oct, nominalends00:39:33.598963/.660105. Earlier derived collector earliestGO+900=23:49:33 was an arithmetic reader error, originalsource/false retained and append corrected. Normal local+remote max(actualnominalend)-now<=900 earliest1793118273.6601048=00:24:33.660105BJT. Old unused wrongclosingV2 mustnotrun. New corrected V3 owner850/node180serial uses actual signed nominalend and originalallout/CNone/locks/unique twofee segment, preserves failedW35 partial and only collects healthyH1formal once with twohostproducerSHA/fulltexts. No actual normalcollector/CPUreviewer consumed, no earlynative source promotion. Time isn't completion proof.

New86 exact Torch dependencies remain separately pending repair, all writes only/data/robemo/polar-rl-train, secret noechoSTDIN/memory only noargv/disk/Git. Stage1 partial/error already in90, no wrongversion substitute or newserverGPUtraining claim. Current H1 alone confirmedupdates; W35failed, othercard environment/readyqueue incomplete, notall4busy. Existing/source preparation frozen; pendingnew86 and futurecollector/forensic supplements explicitly listed, ordinary append once frozen. No localGPU/249/3060/GUI/HUD or thirdpartyprocess intervention.

Original finite sole72 generation/budget reserves86412.86069250107/2268000historical9extensions/new[]/3900lifecycle3600save300exit/actualGO-terminal independentlysumonce remain. Old210canonical permanentlyretired/fenced, no ledgercopy/unretire/clearactive/newwriter/refund/grant/rounding/clamp/idlefee. Temporaryunlimited expired0fees. Startup native4096empty>15669/RAM32/diskactualpostcopy25, normalPPO RAM8, runtime8completeupdatefullsave; healthytrainingnoemptyGPUguard. Physics2.5ms/TGS32/4/FP32/actionsclip6/PD/delay/DR/2mmperenvreset/1umoldscopedquery/native160kevidence reused, no newFP64/bitwise/triangle gates. Gas400 is engineeringnominal each eye200/stroke60/k2000/damping3, no measuredcurve/full140claim. Flat5cm truebothwheelbottomclearance+12realland+200stable=.5s; ultimate270cross/fullfootprint/topcontact12+stable200 unchanged. Genericvelocity/peaks/AABB/imaginedreward notskill. User30cm question advice only, noacceptedtaskchange.

SameACTIVEhourlymod4-10 target/no continuousGoal. Full UTF8/orderedparts/errors/source/reports, binaryactualpathbytesexistingproducerSHA only; no model/raw/USD/NPZ/GPU/host reads forGit or oldonce reruns. Protect all1464oldtagobjects/peels, one newtrial91; failedpush continuesexistingobjects. PostGit verificationconversationonlyno reportchasingHEAD.
'''
 ns['run_stage']('fudan',roots,extras,note,'Start masked-goal native flat training and preserve W35 original restore failure')

if __name__=='__main__':
 try:main()
 except BaseException:put('NATIVE91_UNIQUE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_no_retag=True));raise
