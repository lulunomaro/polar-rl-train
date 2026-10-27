"""One actual expert source/SDK admission phase, not a PPO success claim."""
from pathlib import Path
import importlib.util,json,time,traceback,hashlib,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
S=T/'H1_NATIVE88C_GAS400_FROZEN_SINGLE_DIAGNOSTIC_SOURCE210_R3_20261027'
P=S/'archive_actual88C_frozen_motion_and_imagination_alignment_unique_once.py'
spec=importlib.util.spec_from_file_location('prior_diagnostic_archive_definitions_only_for_E0',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);s=m.s
ID='mod4-frozen-expert-e0-ppo50-gas400-remote4090-admission89'
for a,b in [("'fudan':'mod4-native88c-frozen-motion-and-imagination-alignment-diagnostic'","'fudan':'"+ID+"'"),("nr=T/'H1_NATIVE88C_GAS400_FROZEN_SINGLE_DIAGNOSTIC_SOURCE210_R3_20261027'/'reports'","nr=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89C_20261027'/'reports'")]:
 assert s.count(a)==1;s=s.replace(a,b,1)
ns={'__name__':'E0_actual_source_admission_archive_definitions_only','__file__':m.ns['__file__'],'same_sha_entries':{}}
exec(compile(s,m.ns['__file__'],'exec'),ns);git=ns['git']
def put(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
def main():
 assert git('rev-parse','HEAD')=='f1a765e0a403f63b159e7c87822b5bec531fede1' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1462
 assert json.loads((R/'E0_V89C_ACTUAL_REMOTE4090_SOURCE_SDK_CPU_ADMITTED_RETURNED_ACTUAL.json').read_bytes())['actual_source_SDK_CPU_passed']
 ns['prior'](G/'versions/20261027_mod4-native88c-frozen-motion-and-imagination-alignment-diagnostic/COMPLETE_FILE_CAPTURE_INDEX.json')
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 A=L/'night_frozen_experts_PPO50_gas400_adaptation_20261027'
 freeze=A/'FULL_PRE_CONTROLLER_IMMUTABLE_CHECKPOINT_v1.json'
 assert hashlib.sha256(freeze.read_bytes()).hexdigest()=='d99f407b04059dbca13f1f033064f8398f771771f6c535568803e9585d2c49b9'
 pending=L/'E0_PPO50_gas400_single72_controller_source_preparation_v1'
 put('ACTIVE_CONTROLLER_PENDING_AND_FROZEN_EXPERT_CAPTURE_BOUNDARY_ACTUAL.json',dict(epoch=time.time(),whole_expert_source_folder_now_frozen=str(A),freeze_index_SHA=hashlib.sha256(freeze.read_bytes()).hexdigest(),active_controller_excluded_until_frozen=str(pending),no_controller_or_GPU_GO_claim=True))
 prompt=S/'reports/CURRENT_ACTUAL_E0_CPU_ADMITTED_89C_H1_REFERENCE_MONITOR_V2.txt'
 d=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 assert d['prompt']==prompt.read_text(encoding='utf8').rstrip('\n') and d['status']=='ACTIVE' and d['rrule']=='FREQ=HOURLY;INTERVAL=1'
 put('SAME_HOURLY_AUTOMATION_E0_CPU_NOT_GO_SOURCE_VERIFIED_ACTUAL.json',dict(epoch=time.time(),same_automation='mod4-10',ACTIVE_hourly=True,prompt_exact_except_terminal_LF=True,no_Goal_created=True))
 roots=[N,T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89_20261027',T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89B_20261027',S,A,L/'real_Fudan_video_phase_retarget_reachability_candidate_v1']
 extras=[W/'AGENTS.md',T/'MOD4_FUDAN_USER_UPSTEP_VIDEO_NATIVE_VISUAL_20261027/check_own_leg_excursion_keyposes_from_saved_canonical_once.py']+[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(230,233)]
 note='''Admit the separate E0 PPO50Hz/nominal400N source on the remote4090 host and preserve every preparation/reader refusal. Actual GPU PPO has not started.

User explicitly directs all expert adaptation to free remote4090, not the local5070 laptop or the previously offered remote3060. One gpt6.1sol xhigh helper prepares E0 thenW35; root continues H1 reference repair. Original frozen expert weights and qualifications remain preserved in new forks. The helper whole pre-controller folder is now frozen and fully captured, including E0/W35 sources, N256unused and N20Kselected typed conversions, D1-D7/Adam/STD/LR proofs, actual original manifest lookup,249read-only lease, all source/schema/path/CRLF/warning failures and checkpoint indexes. Large PT/USD/NPZ only prior producer metadata, no binary content read for Git. Active new single-slot controller source folder excluded and explicitly pending ordinary capture after freeze, not deployed or another writer.

E0 original b10958...61f8 becomes typed54f534...0371/14035948B with original20k actor35critic38,17Adam639560,originalLR/STD/private/global RNG/D1-D7 retained, four gas scalar recipe changes and50Hz control/100Hz feedback/20ms queue. Actual original run_manifest1dbde597...af1/44247B acquired once from exact known210 path; no policy/source checkpoint read for that lookup. E0 requires flat133/74 reset compatibility; W35 nearest.25 pose34/32MBbank is a separate exact-compatibility path, never blindly use flat74 there. W35 sourceCPU only, original NPZ two opens scope preserved, no measured dynamics/SDK/actuation proof.

WorkerV1 added16GiB runtime stop and V1/V2 introduced22000MiB/util5 startup conditions without original contract provenance; deployment review rejected them beforeGPU. V2 only runtime8GiB fix, V3 exactly removes unsupported utilization cutoff and returns to existing4090empty>15669MiB while selectedcomputeUUID0 strict. All versions and exact byte/AST proofs retained. V3 SHA1858c639...4152 is actual installed fixed-entry content, never mislabeled V1. Original finite3900/3600/300 and runtime8GiB completeupdate fullsave preserved.

Actual89 source installer failed in PRE at shutil.disk_usage of nonexistent new task parent before mkdir/upload/CPU/App/GO. Local source/tar/error retained, zero fee. New89B corrects only known owned-existing disk root and selected source version; actual payload aftercopy25GiB/fullSHA/source inventory passed, then CPU reader failed while restoring real16byte CUDA private generator state into a CPU5056-byte generator after one newtyped checkpoint initialload. Original CUDA bytes and model remained unchanged. New89C copies already verified89B bytes into a new unused namespace, actual stat/fullSHA verified, and uses exact CPUadmissionV2d052...1663: all original queue shape/finite/lag/timestamp/order validation remains; original uint8[16] CUDA RNG is checked structurally only, never replaced with CPU fake state or claimed restored. A necessary second newtyped checkpoint CPU load followed old process cache loss. No old frozen-model read for Git. Full original errors and corrections retained.

Actual89C target source/SDK CPU passed on72: receiptSHAd06aa8550f915258b0b42a711d73b9859f5fbce68fbcea6289b8647cd0f4208c, all newtyped tensors CPUfinite, actor/critic/Adam/LR/STD/core/D1-D7/source manifest and reset source, actual installed pxr gas400 composition, actualSDK versions/API and queue20ms structure passed. No TorchCUDA initialized/App/physical rollout/Task/GO/budget mutation. ActualCUDA fullrestore,24controls/192physicscallbacks/48feedback/RMdt.02 once percontrol and firstnewPPO remain future runtime admission, not inferred from CPU. Root sole72 single writer must bind signedGO/own lifecycle before worker importSDK. No fake second slot registration.

H1 remains unfixed. Root realvideo sideview shows the actual strongextension/tuck/cross/landing sequence; old standing-jump teacher90percent attenuation/current9223 synthesized landing are not that verified real trajectory. New bounded16keypose IK investigation at amplitudes1/.5/.25/.1 uses existing canonicalJSON and authored400 geometry only, no raw NPZ/model/physics. Some stronger phases fit, descent2.00s remains pending-unreachable-OR-solver-not-converged even.1 in60iterations; no fullclip or dynamic impossibility claim, no new reference exported/deployed. New local read-only truncations and initial cache NaN warning retained in source/conversation. Prior actual frozen diagnostic unique01a801... consumed; its source/errors are ordinary references here, never recorded again.

Sole72canonical generationMOD4_SINGLE_WRITER72_20261026 finite limits remains; actual source installation only readsCNone/locksfree and closed562175.5721518993 snapshot. Old210canonical permanently retired. No training fee, extra grant/refund/rounding/clamp/idlefee/ledgercopy/clearactive/newwriter or localGPU use. Original2.5ms/TGS32/4,2mm per-env reset and true270dualwheelcross/fullfootprint/topcontact12+stable200callback criteria unchanged. No FP64/bitwise/triangle gate. All source/errors/full UTF8/orderedparts and actual SDK receipts captured; binaries path/size/existingproducerSHA only. Protect all1462oldtagobjects/peels, one new actual expert source/SDK admission trial; future same-phase actualGO/PPO and active controller afterfreeze ordinary supplement. Push failure resumes existing objects, postGit verification conversation only.
'''
 ns['run_stage']('fudan',roots,extras,note,'Admit E0 remote4090 PPO50 gas400 source and preserve CUDA RNG reader repair')
if __name__=='__main__':
 try:main()
 except BaseException:put('E0_ACTUAL_SOURCE_ADMISSION_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_no_repeat_record_tag=True));raise
