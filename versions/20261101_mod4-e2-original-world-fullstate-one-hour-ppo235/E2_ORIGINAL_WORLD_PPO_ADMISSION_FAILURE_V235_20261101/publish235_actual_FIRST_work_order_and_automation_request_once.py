"""Publish only an actual successful E2 FIRST; no remote/model/raw/Git calls."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse, hashlib, json, time

N=Path(__file__).resolve().parent; T=N.parent; R=N/'reports'
def read(p): return json.loads(Path(p).read_bytes())
def put(name,value):
    with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--caller-root',type=Path,required=True);p.add_argument('--caller-index',type=Path,required=True);p.add_argument('--additional-frozen-root',type=Path,action='append',default=[]);a=p.parse_args()
    C=a.caller_root; CR=C/'reports'
    first=read(CR/'ROOT_E2_GUARD01_V3_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json')
    state=read(CR/'ROOT_E2_GUARD01_V3_ORIGINAL_SOLO_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json')
    close=read(CR/'ROOT_E2_GUARD01_V3_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')
    launch=read(CR/'ROOT_E2_GUARD01_V3_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json')
    node=read(CR/'ROOT_E2_GUARD01_V3_ORIGINAL_E2_NODE_LAUNCH_ACTUAL.json')
    assert first['passed'] and state['current_owner_matched'] and close['global_serial_control_client_lease']=='FREE'
    f=first['first']; g=state['current']['go']['e2']; b=f['first_complete']
    native=first['native24'];assert native['passed'] and native['actual_mimic_threshold_radians']==.01 and native['actual_closure_threshold_m']==.002
    restore=next(json.loads(x['UTF8']) for x in first['full_selected_UTF8'] if x['path'].endswith('/E2_FULLSTATE_BEFORE_NEW_CONTROL_ACTUAL.json'))
    assert restore['passed'] and restore['original_35_38_6_STD_full_optimizer_LR_D0_D7_E2_RNG_restored']
    guard=restore['guard_before_constructor'];assert guard['passed'] and guard['all_other_termination_params_unchanged'] and guard['unsupported_projection_paths']==[]
    assert f['actual_new_PPO_updates']==1 and f['new_environment_transitions']==480000 and f['new_Adam_step']==859320
    assert b['saved_iteration']==42823 and b['Adam_min']==b['Adam_max']==859320
    assert b['source_SHA']=='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1'
    assert g['max_parent_seconds']==3900 and g['save_deadline']==g['learning_started_epoch']+3600 and g['nominal_end_epoch']==g['learning_started_epoch']+3900
    BJT=timezone(timedelta(hours=8))
    def local(e):return datetime.fromtimestamp(e,BJT).isoformat()
    times=dict(GO=local(g['learning_started_epoch']),SAVE=local(g['save_deadline']),NOMINAL=local(g['nominal_end_epoch']),normal_earliest=local(g['nominal_end_epoch']-900))
    idxsha=hashlib.sha256(a.caller_index.read_bytes()).hexdigest()
    binding=dict(kind='KNOWN_ACTIVE235_EXACT_ORIGINAL_E2_SOLO_AUTHORITY_BINDING',epoch=time.time(),run_id=launch['run_id'],owner=launch['owner'],node=node['node'],go=state['current']['go'],
        current_owner_matched_at_FIRST=True,worker=state['current']['rows']['e2'].get('worker'),
        current_binding_only_until_actual_closed=True,future_remote_requires_fresh72_owner_run_full_GO_match=True,
        close72_before_target=True,not_continuous_health=True,original_binding_source=str(CR/'ROOT_E2_GUARD01_V3_ORIGINAL_SOLO_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json'))
    put('KNOWN_ACTIVE235_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json',binding)
    normal=C/'collect_e2_solo_original_formal_cost_normal900_ROOT_ONLY_once.py'
    review=C/'review_e2_solo_NEW_formal_initial_whole_CPU_ROOT_ONLY_once.py'
    work=dict(kind='CURRENT_ACTUAL235_E2_FULLSTATE_ONE_HOUR_FIRST_AND_NORMAL_WORK_ORDER',epoch=time.time(),run_id=launch['run_id'],
        selected_actual_attempt='235V4',selected_report_prefix='ROOT_E2_GUARD01_V3 inside independent V4 root',actual_FIRST=True,FIRST_receipt=f,native24=native,actual_guard_before_constructor=guard,fullstate_before_control=restore,owner=launch['owner'],node=node['node'],go=g,times_BJT=times,
        actual_first_report=str(CR/'ROOT_E2_GUARD01_V3_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json'),actual_binding_report=str(CR/'ROOT_E2_GUARD01_V3_ORIGINAL_SOLO_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json'),
        first_snapshot_not_continuous_health_final_or_skill=True,source_model_never_overwritten=True,
        source='E2 b3ae/14615089B/42822/17Adam859300/LR .00022500000000000002 full actor35 critic38 STD6 optimizer DR command RNG',
        explicit_guard_change='Legacy E2 mimic .05 -> current plan .01 before constructor; closure .002 unchanged; original rewards/commands/motors unchanged',
        original235V1_local_import_false_and235V2_0PPO_guard_false_preserved=True,
        original235V2_closed_original_fee_SUMONCE=404.86252546310425,
        source_old_V2_read1_decode1_consumed_and_new_V4_guard01_necessary_purpose_admitted=True,
        fresh_physics_episode_queue_not_exact_PhysX_resume=True,ordinary_PPO_one_optimizer_not_native_WM_three_optimizers=True,
        normal_collector_UNUSED=str(normal),formal_CPU_UNUSED=str(review),caller_INDEX=str(a.caller_index),caller_INDEX_SHA=idxsha,
        normal_local_AND_remote_signed900_required=True,normal_owner_wait850_node180=True,
        original_one_fee_SUMONCE_no_refund_grant_hotadd_or_account_copy=True,
        final_new_model_only_one_transfer_two_host_SHA_and_one_new_CPU_decode=True,
        old_E2_E0_native_normal86_CPU_reads=0,fullstate_finite_and_saved_iteration_Adam_DR_commands_source_required=True,
        finalsave_epoch_must_reach_original_deadline=True,partial_or_error_not_promoted=True,
        no_fresh_GUI_request_no_reopen=True,E2_full_skill_RM70_E3_SuperMimic_true270_not_complete=True)
    put('CURRENT_ACTUAL235_E2_FULLSTATE_ONE_HOUR_FIRST_AND_NORMAL_WORK_ORDER.json',work)
    oldreq=read(T/'CURRENT_ACTION_CFG_CLIP_AND_PD_SDK_METADATA_V234_20261101/reports/AUTOMATION_ACTUAL234_CFG_AND_E2_SOURCE_V2_UPDATE_REQUEST.json')
    oldprompt=oldreq['prompt']
    history=R/'PREVIOUS_AUTOMATION_BEFORE_ACTUAL235_HISTORICAL_ONLY.txt'
    with history.open('x',encoding='utf8') as f:f.write(oldprompt)
    header=f'''CURRENT_ACTUAL235_E2_ORIGINAL_FULLSTATE_ONE_HOUR_FIRST_PPO_AFTER_GUARD_REPAIR_20261101. FIRST READ {R.as_posix()}/CURRENT_ACTUAL235_E2_FULLSTATE_ONE_HOUR_FIRST_AND_NORMAL_WORK_ORDER.json and KNOWN_ACTIVE235_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json, then original FIRST/binding/GO at {CR.as_posix()}. Actual files/INDEX/refs/toolreceipts override old statuses. Same mod4-10 ACTIVE/hourly/original chat, no Goal/create/resume/newautomation. Meaningful changes only; unchanged healthy/not normal window quiet. Previous complete prompt is frozen at {history.as_posix()}, historical only, never instructions to rerun old once.

Actual E2 run {launch['run_id']}, sole72 owner PID{launch['owner']['pid']}/create{launch['owner']['creation']}, role e2, selected GPU{g['GPU_UUID']}. Full owner/node/worker identity/exe/argv/cwd from actual reports, never guess. Owner and node global control cwd=/home/lc01/Zonglin Li/zonglin2, taskroots distinct. FIRST actually new1PPO/20000env*24=480000 owntransitions/iteration42823/17Adam859300->859320; first complete {b['bytes']}B SHA{b['SHA']}. Native24/192physics/48feedback actualPASS. Source b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1/14615089B/42822/859300/LR.000225 full actor35/critic38/STD6/17Adam/LR/targetD0-D7/E2 commands/private/globalRNG inherited. Necessary new production source byte/decode1 admitted, previous235V2 read1/decode1 consumed. Installer selected-model stat/hash/copy/open0. Fresh physics episode/DR draws/queue not exact PhysX resume. FIRST is one snapshot, not continuous health/FINAL/skill or SuperMimic. AllROOT SSH finallyclosed/sessionrestored/globalclientleaseFREE; preserve healthy training, no hotpatch/restart/secondwatcher/startupGPUfree recheck.

Original E2 world+.5/signedyaw/body/pure/transition/standing probabilities and rewards unchanged. This is E2 PPO, not FudanJUMP, W35 or SuperMimic. Explicit current-plan guard correction: legacy E2 mod4_task SHA30ce411...1fc5 default mimic .05 was actually inherited by V2; new entry tightens only mimic to .01 before Mod4Env constructor with actual receipt, closure stays .002. Older .01 descriptions cannot override old .05 source; preserve old failure. Keep400N nominalengineering k2000/50policy100feedback400physics2.5msTGS32/4F32/6motorclip6/PD/torque-speed/delay/D0white_v3D1-D7/fixedSI35/38/no learnedobsnormalizer. V1 local env_isaaclab lacked compression.zstd, refused before network; separate existing Python314 caller V2 then constructor/restoration completed but assertion .05 vs .01 rejected,0PPO/noformal. OriginalV2 worker/node/owner allwaitout/locksfree/freshCNone and original rawfee404.86252546310425 SUMONCE; closing408718.077508688 historical snapshot. No refund/newgrant. New independent source/Task/manifest/Ready/purpose preserve both failures. V3 then refused before Task/GO/SDK/model because its new report prefix was also used as admission.kind while reused base fresh() expects ROOT_E2_SOLO_FRESH_CNONE_CIM_RESOURCE_ACTUAL. V4 fixes only this metadata kind literal, retains V3 worker/entry/helper/protocol byte-exact, uses independent namespace/root and own INDEX; ROOT_E2_GUARD01_V3 report/lease prefixes remain only inside this V4 root. V1/V2/V3 attempts consumed/retired, never rerun.

GO{times['GO']};SAVE{times['SAVE']};NOMINAL{times['NOMINAL']};normal earliest{times['normal_earliest']}. Original max3900/save3600/exit300, no newgrant or automatic extension. NEXT ONLY {normal.as_posix()} --root-lease-label ROOT_E2_GUARD01_V3_EXCLUSIVE_NORMAL900_<freshID> --auth-provider C:/Users/lulu/Desktop/claude/mjcf/MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py --additional-control-pattern <allcurrentknowncontrolbasenames> --caller-index-SHA {idxsha}. Use existing Python314 for control. FreshLOCALexactCIM/globalclientleaseFREE; original signed LOCAL AND REMOTE nominal-now<=900, owner850/node180 unchanged. Actual COHORT_FINAL/OWNER_EXIT/NODE_EXIT/allownwaitout/knownoriginalPIDOUTorZ/private+two sharedfree/freshCNone/exactuniqueownerGO fee segment. Read one original rawfee SUMONCE, no refund/recharge/round/clamp/idlefee/grant/copycanonical/clearactive/secondwriter. Only qualified NEWformal transfer1/twohostSHA. Full JSON guards then {review.as_posix()} --caller-index-SHA {idxsha}, CPU env_isaaclab with CUDA_VISIBLE_DEVICES='' insidePython, only NEWformal byte/decode1, alloldPT0. Fullfinite35/38/STD6/17Adam859300+20updates/iter42822+updates/sourceb3ae/typedtask/fullD0-D7/E2commandRNG; actual adaptive LR and finalsave>=original deadline. Partial/error not promoted. PPO oneoptimizer;20Adamsteps not20nativeiterations. No model/raw stats reread or second watcher. Any future remote first fresh72 exact current owner/run/fullGO then CLOSE72 before target; after actual closure this binding HISTORICAL, never assume active or CNone.

Latest qualified W35 closed227D still2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b/17619333B/32481/651260,77newPPO; originalfee3645.0908699035645 consumed. FullCAD RM70=70mm peak-to-trough,period240.641934mm/length2.406423m/width2.0845m/slope1.5deg, not35/not±70. Fullskill stillUNKNOWN; old222 partial and227B fixed343e are consumed/source-specific, latest2d0 full32s needs new frozen purpose/one newnecessaryread. E2 actual232 full20k/24s completed but parentFALSE because post-Appclose readcounter absent; preserve original error/counterUNKNOWN. 233 newJSONL onepass consumed; alongfail46147/cross9099/yaw8413 overlap; alongMAE.1063038 primary observed deficit, not unique cause/population success rate. Do not reread that raw. E3/full old experts/SuperMimic unfinished;190 only syntheticWM50 component.

E0 frozena92 and parent210e629 remain untouched; separate225copy17696bc...cbaf/2304x10s has9 sampled bilateralwheelairruns with headingdrift/nonwheelcontacts, not stablejump/270; no automatic newE0 3h selected. Original FudanJUMP19methods/config16weights/clip2.5/contactflightmemory/dt.02 unchanged on JUMP subenvs;10% ground separate originalE0 reward. Actual234 N1 current E0 package cfg.clip=None, crankdiff projection only, inherited JointPositionAction.apply sets targets then PD/DC/physicalstops; staticCADhip±.5 not current actiontarget clip. Actual234 ninecurrentPYsource bytepasses/one additionalget_dof_limits/0NNcontrols consumed, source scope E0package only. No unique jumpfailurecause or unselected hipheadfix. 234phase already consumed HEADc16c2e576668a397cc21f70e0f2404f8d532934a/tagobj c391f9d9fde2fc72d98eacc0fd214f314ca5a83a/1510tags, never rerecord/retag. No freshGUIrequest/no oldviewer reopen-query-kill/no PPO fabricatedblueWM.

ONE GLOBAL serial controlSSH72/210/86/249. Everynewfinite freshLOCALexactCIM basename/fullpath/exe/fullargv/create; whileclientalive ROOTonlylocalreports/CIM/samehandle+independentLOCALCPU. ROOT alone SDK/GPU/SSH/model/raw/GO/training/budget/Git; only same authorized208child LOCALsource/CPU, no new/nested/Astra/Sol. No unknownPID/GPU-PIDscans/kill/lockdelete/thirdparty/GUIrestart/local3060neuralCUDA/Luna/OpenRouter. Old990366 signalpermission consumed. Newstartupfree>15669MiB/util<=30 allowsnonemptycomputeUUID/RAM32GiB/disk25GiB;healthyjob no startuprecheck;runtime8GiB DISKsaveguard. No root/force/velocityinjection/fakeairreset/foreigntruth/guardrelax. Reuse native160k/oldscoped1um, no FP64/bitwise/triangle extra gates. MATLAB71796 preserve GetActiveObjectonly.

Solecanonical72=/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json generationMOD4_SINGLE_WRITER72_20261026/modefinite_original_limits_restored_after_single4090_return/authorized2268000/9historical/extensions[]/strictreserve86412.86069250107. Originaltwofcntl/HMACbody/charge_values unchanged, actualGO-to-terminal independent rawfees SUMONCE; no refund/recharge/round/clamp/idlefee/grant/secondwriter/canonicalcopy/clearactive. Old210canonical retired.72pin301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795/loopback29754;210strictegde@10.24.5.27:4090inner22 originalpin/durableUUIDEF3105C85DD986BD newstorage freshUUID-rw, no cleanup/fstabguess;86robemo10.50.0.86 pin8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b writesonly/data/robemo/polar-rl-train;249displayonly original95b8067b17fc5331aac5e2d46acd6a087c46719dc853658b14bfa0e29e69242e. Secrets memory/noechoSTDIN/memfdonly, noargv/env/disk/Git; noapt/sudo/globalpip/driver/profile/DNS.

Git235 actual newPi uniquephase mod4-e2-original-world-fullstate-one-hour-ppo235 via record_experiment ONCE; ANYthatphaseTAG exists CONSUMED never rerecord/retag. Protect1510 oldobjects/peels, actualHEAD/refs/CAPTURE_INDEX override pending words; pushfailure only existingobjects. Capture235 V1 interpreterfalse/V2 originalguardfalse andcompleteclosingfee/sourcecache/fullUTF8/V3 guard01 source plus preGO KINDrefusal/V4 metadata-only KINDfix/newsourceinterfaceproof/readpurpose/admission/TaskmanifestReady/CUDAfullrestore/native24/FIRST/CIM/session/appreceipt, all frozen ROOTcallers. PT/rawJSONL/NPZ/USD/STL/media metadataonly actualpathbytes existingproducerSHA/unknown, noFORGit content/hash/model/raw/hostGPU. Normal close/fee/NEWformalCPU later ordinaryappend, notretag. PostGit toolverification/conversation only, noHEAD-chasingreports. True270 dualwheelcross/fullfootprint/top12+stable200physics=.5s/fullRM70/E2E3/fullSuperMimic stillUNACHIEVED.
'''
    req={k:v for k,v in oldreq.items() if k!='prompt'};req['prompt']=header
    put('AUTOMATION_ACTUAL235_E2_FIRST_AND_NORMAL_UPDATE_REQUEST.json',req)
    roots=[N,T/'E2_QUALIFIED_FULLSTATE_SOLO_ROOT_CALLERS_V1_20261101',T/'E2_QUALIFIED_FULLSTATE_SOLO_ROOT_CALLERS_PY314_V2_20261101',C,*a.additional_frozen_root,T/'derive_ROOT235_callers_PY314_V2_before_use.py',T/'collect235_failed_original_owner_closed_once.py']
    unique=list(dict.fromkeys(str(x.resolve()) for x in roots))
    put('CAPTURE235_ACTUAL_FROZEN_SCOPE.json',dict(epoch=time.time(),roots=unique,
        actual_start_closed_receipt=str(CR/'ROOT_E2_GUARD01_V3_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json'),
        actual_FIRST_report=str(CR/'ROOT_E2_GUARD01_V3_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json'),actual_binding_report=str(CR/'ROOT_E2_GUARD01_V3_ORIGINAL_SOLO_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json'),
        automation_request_file='AUTOMATION_ACTUAL235_E2_FIRST_AND_NORMAL_UPDATE_REQUEST.json',
        trials=['235V1 pre-network interpreter refusal','235V2 original legacy .05 mimic vs required .01 guard refusal,0PPO andoriginal fee closed','235V3 preTask/preGO admission-kind schema refusal,0SDK/model/PPO','235V4 kind-only metadata repair and actual new PPO FIRST using frozen guard01 source'],
        pending_excluded=['Actual235 normal final/fee/newformalCPU not yet eligible','Unfrozen unrelated next source','models/raw/media contents'],
        remote_artifacts_metadata_only=[dict(path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E2_PPO50_GAS400_2610v93/e2/adaptation/final_valid_update92.pt',bytes=14615089,SHA=b['source_SHA'],kind='input'),b],binary_local_producer_metadata=[]))
    note=f'''E2 original fullstate one-hour PPO235

Actual FIRST adds one PPO update and 480,000 own transitions after full actor35/critic38/STD6/17Adam/LR/D0-D7/E2 command RNG restore and native24. Input b3ae/42822/859300 becomes42823/859320. Source model remains frozen. First checkpoint {b['bytes']}B SHA{b['SHA']}.

Preserve V1 pre-network interpreter refusal and V2 zero-PPO legacy mimic .05 versus required .01 assertion. V2 closed normally through original owner, original fee404.86252546310425 SUMONCE, no formal promotion. Frozen V3 source tightens mimic .05 to current-plan .01 before constructor; V3 caller preGO metadata-kind refusal is retained, V4 repairs only that kind literal and executes the unchanged guard01 source; closure2mm, original E2 rewards/commands/motors and other physics unchanged. Fresh physical episodes are not exact PhysX continuation. Full-tree finite saving retained.

GO {times['GO']}; SAVE {times['SAVE']}; normal earliest {times['normal_earliest']}. FIRST is not final, continuous health or E2 graduation. Normal final, fee and NEW formal CPU are pending original gates. FullRM70/E3/SuperMimic/true270 unfinished. Original frozen E0 and unselected jump repairs remain unchanged.

All source/false/errors/receipts/full UTF8 are indexed. Binary models/raw/NPZ/USD/media are metadata only; no model/raw/hostGPU reads for Git. Protect1510 old tag objects and peels. Future235 closing is an ordinary supplement, never retag235.
'''
    with (R/'ACTUAL235_E2_FULLSTATE_PPO_EXPERIMENT_NOTE.md').open('x',encoding='utf8') as f:f.write(note)
    print(json.dumps(dict(passed=True,run_id=launch['run_id'],times_BJT=times,caller_index_SHA=idxsha,updates=1)))
if __name__=='__main__':main()
