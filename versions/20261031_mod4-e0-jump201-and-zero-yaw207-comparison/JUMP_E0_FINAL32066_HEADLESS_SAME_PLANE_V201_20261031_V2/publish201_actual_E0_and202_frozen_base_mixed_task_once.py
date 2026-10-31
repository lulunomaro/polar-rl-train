"""Keep actual201 results and the user's frozen-E0/mixed-environment requirement."""
from pathlib import Path
import json,time,tomllib
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';N=T/'FUDAN_JUMP_PARALLEL_SINGLE_WRITER_HANDOFF_V197_20261031'
M=T/'E0_FROZEN_BASE_MIXED_GROUND_JUMP_TASK_V202_20261031';(M/'reports').mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
actual=read(R/'ROOT201V2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json');case=actual['result']
finally_=read(R/'ROOT201V2_ALL_SSH_CLOSED_SESSION_RESTORED_LEASE_FREE.json')
assert actual['passed_execution'] and actual['returncode']==0 and not actual['worker_errors']
assert case['model_iteration']==32066 and case['controls']==1000 and case['physics_callbacks']==8000
assert finally_['all_owned_SSH_closed'] and finally_['SESSION_restored'] and finally_['global_serial_lease']=='FREE'
cpu=read(N/'reports/ROOT197_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')['roles']['e0_72']
assert cpu['SHA']==case['model_SHA']
primary=read(T/'JUMP197_FINAL5367_USER_MUJOCO_V200_20261031_V2/reports/ROOT200V2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json')['result']
frozen_base=dict(SHA='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a',bytes=14031973,
    original_RSL_iteration=31984,original_Adam17_step=641200,
    path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0/adaptation/final_valid_update82.pt',
    role='IMMUTABLE FROZEN E0 FLAT EXPERT /reference and warmstart source only',
    writes_by_197_198_200_201=0,checkpoint_reads_for_this_policy_record=0)
spec=dict(epoch=time.time(),status='USER_REQUIREMENT_AND_TASK_SPEC_FROZEN__RUNTIME_SOURCE_CALLER_PENDING',
    user_exact='记住e0平地专家是冻结的，我们的跳跃是在冻结专家的基础上，保持少量平地环境，进行跳跃训练',
    frozen_original_E0=frozen_base,
    branch_policy='New trainable full-state COPY in a different namespace; never write original E0 file or substitute jump output for frozen flat expert',
    latest_pure_jump_branch=dict(iteration=32066,SHA=case['model_SHA'],new_updates=82,retained_as_historical_branch_not_overwritten=True),
    default_next_start='Full-state copy of original frozen E0_82; retain actor/critic/STD/17Adam/LR/counters; no random/cold restart',
    desired_env_mix=dict(total=20000,ground=2000,jump=18000,ground_fraction=.1,jump_fraction=.9,
        ratio_source='Root default for human instruction少量, not a claimed human-specified exact percentage',
        persistent_per_env_task_mode=dict(ground=0,jump=1),same_episode_task_stays_fixed=True),
    reward_contract=dict(jump='Pinned Fudan JUMP19 methods/fullconfig16weights byte-literal; original dt/clipping/flight memory',
        ground='Exact frozen E0 original flat reward and command/task source; join actual source/profile before use, never substitute generic H1 reward',
        routing='Return original ground reward for ground envs and literal JUMP reward for jump envs; no new walking term in JUMP, no arbitrary blend coefficient',
        mixed_batch_changes_total_optimization_distribution_explicit=True),
    PPO_contract='Trainable branch acts on all its own ground/jump envs with task-conditioned35obs/38critic/6actions; never pass frozen-teacher actions as on-policy branch samples',
    flat_coverage='Preserve original E0 standing/forward/reverse/turn command domains and reset/DR; not just no-command standing. Exact source binding pending.',
    physics='Original400N engineeringk2000/50policy100feedback400physics/2.5msTGS32-4F32/D0white_v3D1-D7/clip6/PD/delay/perenv2mm/mimic.01',
    before_new_GO=['Exact E0 flat profile/reward/source join',
        'Complete two-task reset/mode/commands/reward runtime source and sourceCPU checks',
        'Actual target0PT mixed task mode/reward/queue/physics readback',
        'New exact input fullstate CUDA restore/typedTaskGO/freshresources/sole72writer',
        'Finite user-scoped window with original caps/no budget grant; no automatic extra two hours'],
    after_training='Separate ground standing/forward/reverse retention and original plane true-flight/landing regression; no graduation from reward or contact flags',
    not_yet_implemented=['Mixed runtime adapter','actual target admission','mixed-task GPU learning'],
    current_training_running=False,main200_user_window_remains_primary5367=True,
    no_runtime_reward_or_model_changed_by_this_spec=True,no_model_raw_NPZ_SDK_GPU_or_SSH_actions=True)
put(M/'reports/FROZEN202_USER_FROZEN_E0_BASE_AND_GROUND_RETENTION_MIX_TASK_SPEC.json',spec)
summary=dict(epoch=time.time(),kind='ACTUAL201_E0_FINAL32066_HEADLESS_ONE_CASE',
    source_model_SHA=case['model_SHA'],new_branch_training_updates=82,iteration=32066,Adam17_step=642840,
    original_E0_stays_frozen=frozen_base,actual_case=case,worker=actual['actual_worker_identity'],
    actual_waited_RC=0,all_SSH_finally=finally_,
    comparison_scope='Separate deterministic N1 seed27 first episodes, same source plant/commands; not a population success rate or exact PhysX bitwise replay',
    primary200_report_only_summary=dict(iteration=5367,controls=primary['controls'],terminal_flags=primary['terminal_flags'],wheel_center_max_world_z_50Hz=primary['wheel_center_max_world_z_50Hz']),
    interpretation='E0 case completed20s with original physical guards untriggered except timeout; wheel-center excursions much lower than primary, stable jump not certified',
    wheel_center_max_is_not_jump_height_or_common_peak=True,
    failed201V1='Before model/action, version-string replacement corrupted numeric assertions/queue; original errors kept; not a strategy failure',
    repaired_V2='Numeric AST preserved except model iteration; actual one modelGPU read/decode and same original task',
    E0_new_pose_NPZ_numerical_or_GUI_member_reads=0,primary_old_NPZ_model_reads=0,
    latest_user_requirement=spec['user_exact'],mixed_task_spec=str(M/'reports/FROZEN202_USER_FROZEN_E0_BASE_AND_GROUND_RETENTION_MIX_TASK_SPEC.json'),
    current_mix_not_implemented_or_started=True,no_new_learning=True)
put(R/'CURRENT_ACTUAL201_E020S_LOW_EXCURSION_AND_FROZEN_E0_MIX202_REQUIREMENT.json',summary)
a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
prefix=f'''CURRENT_ACTUAL201_E0_SAME_PLANE_CASE_AND_HUMAN_FROZEN_E0_GROUND_RETENTION_MIX202_20261031 overridesE0-no-eval-yet and pureJUMP-next-round wording below. FIRST READ {R.as_posix()}/CURRENT_ACTUAL201_E020S_LOW_EXCURSION_AND_FROZEN_E0_MIX202_REQUIREMENT.json and {M.as_posix()}/reports/FROZEN202_USER_FROZEN_E0_BASE_AND_GROUND_RETENTION_MIX_TASK_SPEC.json, then actual201V1/V2 reports and200/closed197 actuals. Samemod4-10 hourlyACTIVE/originalthread, noGoal/newautomation; actualrefs/index/receipts first, consumedonce neverrepeat. Quietunchangedpending, materialchangesonly.
LatestHUMANexact“记住e0平地专家是冻结的，我们的跳跃是在冻结专家的基础上，保持少量平地环境，进行跳跃训练”。OriginalE0_82 a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a/14031973B/31984/Adam641200 remainsFROZEN/reference/warmstart only, never overwritten by197/198/201. 32066 is a separate trainable jump COPY, not the frozen original. Last198 one-hour used100%JUMP envs, mixed ground not already implemented; retain this limitation. Root default NEXT mixed task90%JUMP18000+10%originalground2000 of20k (human said少量, exact10% is root default). Defaultnewmixedbranch starts full actor/critic/STD/17Adam/LR/counter copy of frozenE0_82, notrandomcoldstart; keep32066 prior branch separate. OriginalE0 file never written, jump output never replaces frozenflat librarymodel. FrozenE0 original flat reward/profile/commands need EXACTsource join before runtime, don't substitute genericcurrentH1 reward. JUMP19/config16weight/dt/clip/flight byte-literal remains unchanged; outer routing chooses eachtask original reward, no addedwalkingterm or arbitraryweightedmix. One trainablebranch policy acts in both sets; never feedfrozenE0teacheractions as ifonpolicy. Explicit0flat/1jump modes, per-envpersistent taskID, original standing/forward/reverse/turn domains, same400N50D0-D7/2mm/TGS32-4. Full source/CPU/actualmixed0PT/taskGO/fullstaterestore/freshresources/solewriter required before anynewlearning. New202 currentlySPEC_FROZEN_IMPLEMENTATION_PENDING, no readySDKcaller/GO/mixedlearning; no automaticnewtwohour/grant.
Actual201 headless assessment nowRETURNED0/CONSUMED, not E0GUI. V1 naiveversion replace200->201 changed2000assertto2010 andqueue20000to20100; premodel guardstopped beforecheckpointload/action0, originalKitOSRC0 but functionERRORstrictFAIL preserved, notphysicalE0failure. NEWV2 distinctnamespace repaired regex preservingallnumericAST except5367->32066; gas2000/queue20000 preserved, same reward/commands/physics. OriginalV1 task-onlyuploadedNEW32066formalonce/postcopyhashonce, V2 reusesimmutableuploadedinput withfirstactualGPUbyte/readdecode1; originalE0/inputothermodels0. V2 actualworker3651153/create1793457956.03/fullargv/cwd inreceipt,waitRC0/Appclosed/privateEXfree/allSSHclosed/SESSIONrestored/FREE. Case1000controls8000physics2000feedback20s/time_outONLY/allotheroriginaltermsfalse. WheelcentermaxL/R[.0772213638,.0974249989]m vsprimary200 [.4529222548,.4521372318]m; these areindependentper-wheelcentermaxima, NOT wheelbottom/jumpheight/commonpeak orsuccessrate. Fudancontactflight79/1000/bothforcez<=1N159 notgraduation. Thus thisN1 E0excursion is muchlowerthanmain and doesnotcertifystablejump, notclaim“E0cannotjump”fromonecase. Actualartifact830515B SHA4c1b4cf5bf659a0114c2bbbd8e8a5558585c4872c3374e7bc10b5290f2241fb9 transfer1/twohostSHA. New201NPZ firstnumerical/visualcontent stillUNREAD; do notopenforstats/Git. Ownstaticcontractmetadata162015B one necessary source bytepass retainedbodyentries only; not additional contact/physics evidence. No201viewerlaunched and don'tswitchmainwindow withoutfreshuserrequest. User alreadywatchedmain200andreported转圈着跳; preservecurrent65960window/noautoquery-reopen-kill.
201allsourceV1failure/V2repair/fullUTF8/CIM/resource/actual20s/transfermetadata/sourcegeometrymetadata/humanconstraint/mix202spec/automationreceipt needuniqueactualevaluationphase mod4-e0-final32066-literal-jump-plane-headless201 viarecord_experimentONCE; existing201tag=>CONSUMEDneverrecord/retag, pushfailurecontinueobjects. Actual200tag alreadyCONSUMED main0facf30269e03380a0c174b24e8165ac4810c2df/tagobj49b68222273fb06118e8618bfb91de2697e19670/1502tags, protectall1502oldobjectspeels. 202spec source-only receivesnoGPUtag; activeunfrozenmixsourceexcludeduntilfrozen. BinaryPT/NPZ/USD/raw/media onlypathbytesexistingproducerSHA/unknown, zero FORGit model/rawhash/hostGPU. postGit toolverify/dialogueonly, noreportchasingHEAD. All original sole72budget/security/serial/physics/ultimate270constraints below retain. No currentlyrunningH1learning, no fakefourcardclaim.\n\n'''
req=dict(mode='update',id=a['id'],kind=a['kind'],name=a['name'],prompt=prefix+a['prompt'],status=a['status'],rrule=a['rrule'],targetThreadId=a['target_thread_id'])
if 'notification_policy' in a:req['notificationPolicy']=a['notification_policy']
put(R/'AUTOMATION201_E0_ACTUAL_AND_FROZEN_BASE_MIX202_UPDATE_REQUEST.json',req)
print(json.dumps(dict(passed=True,actualE0controls=case['controls'],frozen_E0_unchanged=True,mixed_task_status=spec['status'])))
