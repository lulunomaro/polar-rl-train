"""Ordinary supplement of consumed90; no new record or tag."""
from pathlib import Path
import importlib.util,json,time,traceback,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
P=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027/archive_actual89C_failure_89D_first_PPO_and_flat_course_ordinary_once.py'
spec=importlib.util.spec_from_file_location('old_ordinary_definitions_only',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
s=m.s
for a,b in [
 ("'fudan':'mod4-frozen-expert-e0-ppo50-gas400-remote4090-admission89'","'fudan':'mod4-native-flat5cm-supermimic-first-training90'"),
 ("nr=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027'/'reports'","nr=T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90B_20261027'/'reports'"),
 ('ordinary_actual89C_logger_failure_89D_first_PPO_and_flat5cm_course','ordinary_closed90B_native_and_delegated_W35_actual_CPU'),
 ('ACTUAL89D_FIRST_PPO_ORDINARY_GIT_NOTE.md','CLOSED90B_W35_ORDINARY_GIT_NOTE.md'),
 ('ORDINARY_FIRST_PPO_COURSE_CAPTURE_STARTED_ACTUAL.json','ORDINARY_CLOSED90B_W35_CAPTURE_STARTED_ACTUAL.json')]:
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
ns={'__name__':'ordinary_closed90B_definitions_only','__file__':m.ns['__file__'],'same_sha_entries':{}}
exec(compile(s,m.ns['__file__'],'exec'),ns);git=ns['git']

def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)

def main():
 assert git('rev-parse','HEAD')=='c43cab6dc795bea14e2af84d7ceb0356689ca8db' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1464
 assert git('rev-parse','trial-20261027-mod4-native-flat5cm-supermimic-first-training90')=='4c8b4514de441d593ef065b3cdf1ee52634e6776'
 assert json.loads((R/'FLAT90B_FORMAL_NATIVE_FULLSTATE_INITIAL_CPU_AND_COST_ACTUAL.json').read_bytes())['passed']
 prior=G/'versions/20261027_mod4-native-flat5cm-supermimic-first-training90/COMPLETE_FILE_CAPTURE_INDEX.json'
 ns['prior'](prior)
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 prompt=R/'CURRENT_CLOSED90B_NATIVE_FLAT_AND_DELEGATED_W35_ACTUAL_CPU_MONITOR_V3.txt'
 a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 assert a['prompt']==prompt.read_text('utf8').rstrip('\n') and a['status']=='ACTIVE' and a['rrule']=='FREQ=HOURLY;INTERVAL=1'
 roots=[N,L/'flat91_mask_aware_goal_conditioning_source_v1',L/'W35_existing4090_mixed72_node_source_v1',L/'H1_W35_next_mixed72_owner_deployment_source_v1']
 for p in [roots[1]/'FROZEN_SOURCE_INDEX_ACTUAL.json',roots[2]/'FINAL_W35_ACTUAL_CPU_NODE_FULL_INDEX_V1.json',roots[3]/'INTERFACE_FROZEN_INDEX_V1.json']:assert p.is_file()
 note='''Closed90B formal native source qualified; no observed real flat-jump success. Normal collector252 actually returned full formal model256228297B/8b0ef2b6c60f4453ebb46a9718133e54e33cad5985ddd96459e479d10fc5ef43, twohostSHA, terminal/owner/node wait, canonicalNone, original locksfree and original fee3610.5603725910187s. Closed snapshot554499.7579419613. Normal finite duration passed, no refund/rewrite/secondwriter. All collected original text captured full UTF8 including141MB convergence curve in orderedparts; native model itself metadata only.

One initial NEWformal CPUload plus one necessary normal86 frozen RSL witness passed fullfinite strictWM/Pi/Critic/norms/threeopts, frozenactor9critic8STD6/17Adam832460, same400N/100Hz/preload/reset, native contract/newwindow and normalduration/account/allout. Global7841iter78410WM7649Pi; new13720WM1308Pi. No source88C native re-decode, saved actor or WM forward, GPU/SDK/physics in local review. Native critic steps20*globalPi reflect native5epochs4minibatches, not PPO20periteration. Literal normalizer counts and five analytic goal normalization ranges recorded in SAME initial load; don't rereadweights for addedstats orGit.

Formal3494 completecontrols, last collected curve3491controls and31093requestattempts/0takeoff/height/landing/stable recovery. Last3controls do not have an exported flatcounter in formalmanifest, so exactfull3494 flat totals remain unproven. No raw re-extraction/physics/frozen policy evaluation or skillgraduation. Invalidenvcallbacks408/censored24576 and resets35450 are original diagnostic scope, not global trainingfailure. Original first240control snapshot superseded, original generic270 counter/velocitymetric cannot stand in forflat jump.

Saved critic RunningNorm count200014848 is capped/frozen. Analytic new goal tail absmax100; actual extreme column index was not saved, do not attribute it definitely to maskchannels. Unknown-value tailmax.34195, actor max<=2.632. Generic masks normalized using historical continuous statistics can resurrect masked missing values and badly condition changed constant masks. New exact source-only patch changes only Policy.forward and Critic.forward plus one helperimport: normalizedvalues*knownmask after normalization and literal0/1mask; critic prefix untouched. Strict same modules/parameters/normbuffers/state_dict and existing optimizer continuity required, no model reset or old700physics. Six sourceCPU fixtures include synthetic finiteBPTT and zero state mutation, no saved actor/WM used. All source/fixture/error scopes retained. This is new inputencoding, requires NEWtyped90B->91 source/producer and fresh target SDK/runtime admission, is not deployed, no learninggain or sole-rootcause assertion. Oldwrongquaternion hypothesis remains refuted. One local wrong networks path under sm_deps produced reader-only failure and was corrected to actual source path; no model/training effect.

Human explicitly corrected delegation: one child owns all frozenexpert50Hz400N/newhost adaptation; root stays H1native. Child actualW35 target72 SDK/initialCPU passed,465filesfullSHA/postcopyfree16828/RAM/disk/readonlyfiniteCNoneclosing checks, actualownedCPUwait0 and exactSDKversions. Initialprocessidentity caught original bashwrapper beforeexec, not falsely execafterloader. Full W35 nativeCUDA restoration/native24/newPPO still pending actual mixedGO. W35 model17Adam646800/LR1e-5/STD/G3/retainedcommands/nearest250pose34bank and20ms typed source preserved. No independent W35owner/GPUtraining/ledgerwrite. Source CPU and all failed import/newline/reader/prototype cases fullfrozen index95c46f...56b9 captured. New common mixedowner interface15files/index5c5225...933db pureCPU17 tests, originalaccount/Handler/HMAC/charge_values exact except genuine2slot collection/label. It waits rootexactH1 protocol, futureNEWV2 sealing, no fake registration/hotadd/secondwriter. Existing E0 already closed82PPO, not nativeSuperMimic and no blind repeat.

Newhost Stage1 torch install partial/error already in unique90. Stage2 directory has only pending source JSON, not deployed, explicit pending future ordinary capture once frozen. No wrongversion substitution; project-only/data/robemo/polar-rl-train, no globalpackage/driver/otherpath/task changes. Secret only memory/noechoSTDIN; no credentials archived. ExistingSDK4090 W35 prioritized while barehost dependencies pending. No actual newserver GPU training. Atmostone sequentialchild/no nestedparallel, oneglobalserialSSH finite lease; root does not take over expert branch.

All modelsource vs physicalresource vs production source distinctions remain. Native is separate METHOD, frozenRSL only witness. Original physics2.5ms/TGS32/4/FP32/actionsclip6/PD/delay/DR/2mmperenvreset/1umscopedquery/native160kevidence reused; no newprecisiongates. Gas400N is nominalengineering assumption, not measuredcurve/fullstroke. Flat5cm truebothwheelbottomclearance+12reallanding+200stablecallbacks=.5s; final270cross/fullfootprint/topcontact12+200stable unchanged. User30cm discussion did not change active task. No current91Task/payload/owner/GO/fee, no unchangedwindow blindly started. Same originalsole72 finite budget/generation/reserve86412.86069250107/3900savecaps/900closing gate; old210permanentlyretired. No refund/grant/rounding/clamp/idlefee/copiedledger/clearactive. SameACTIVEhourlymod4-10 no continuousGoal, notificationonly meaningful result/materialrepair/boundary/action.

Ordinary supplement only of consumed90; protect all1464 tagobjects/peels. FullUTF8/source/errors/reports/orderedparts and existing binarymetadata only, no PT/raw/USD/NPZ/GPU/host reads forGit or oldonce reruns. Pushfailure continuesexistingobjects. PostGit verification conversationonly; no report chasingHEAD.
'''
 ns['run_stage']('fudan',roots,[],note,'Qualify closed flat native90B and preserve delegated W35 actual SDK admission')

if __name__=='__main__':
 try:main()
 except BaseException:put('ORDINARY_CLOSED90B_W35_ARCHIVE_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_never_record_tag=True));raise
