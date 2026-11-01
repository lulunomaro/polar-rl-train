"""Own actual240 receipts only. No new SSH, model/raw/SDK/NN reads."""
from pathlib import Path
import datetime as dt,hashlib,json,time
T=Path(__file__).resolve().parent;N=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101';R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stamp(t):return dt.datetime.fromtimestamp(t,dt.timezone(dt.timedelta(hours=8))).isoformat()
first=read(R/'ROOT240_FIRST_NEW_PPO_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json');state=read(R/'ROOT240_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json')
launch=read(R/'ROOT240_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json');node=read(R/'ROOT240_ORIGINAL_JUMP_NODE_LAUNCH_ACTUAL.json')
assert first['passed'] and state['current_owner_matched'] and read(R/'ROOT240_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
go=state['current']['go'];assert set(go)=={'jump_72'};g=go['jump_72'];assert g['run_id']==launch['run_id'] and g['source_CPU_SHA']==read(R/'ROOT240_ACTUAL_TASK_MANIFEST_READY_AND_PUBLIC_SCHEDULE.json')['Ready_entire_VALUE_SHA_for_GO_source_CPU']
initial={Path(x['path']).name:json.loads(x['UTF8'])for x in first['full_selected_UTF8']if x['path'].endswith('.json')}
worker=initial['WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json']
binding=dict(kind='KNOWN_ACTIVE240_EXACT_ORIGINAL_MODEL2050_SOLO_AUTHORITY_BINDING',epoch=time.time(),run_id=launch['run_id'],owner=launch['owner'],
 node=node['node'],worker_original_identity_before_wait=worker,worker_at_FIRST_node_report=initial.get('NODE_CURRENT.json',{}).get('row',{}).get('worker'),
 go=go,canonical_path='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json',
 authority_generation='MOD4_SINGLE_WRITER72_20261026',scope='FIRST snapshot authority; future remote requires fresh exact knownowner/run/fullGO match, after closure historical')
put('KNOWN_ACTIVE240_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json',binding)
normal=N/'normal240/collect240_original_formal_cost_normal900_UNUSED_once.py';review=N/'normal240/review240_NEW_formal_initial_whole_CPU_UNUSED_once.py'
times=dict(GO_BJT=stamp(g['learning_started_epoch']),SAVE_BJT=stamp(g['save_deadline']),NOMINAL_BJT=stamp(g['nominal_end_epoch']),normal_earliest_BJT=stamp(g['nominal_end_epoch']-900))
order=dict(epoch=time.time(),kind='CURRENT_ACTUAL240_MODEL2050_LITERAL40050_GROUND10_FIRST_AND_NORMAL_WORK_ORDER',run_id=launch['run_id'],
 actual_learning_STARTED_at_FIRST_snapshot=True,continuous_health_or_skill_not_inferred=True,all_ROOT_SSH_finally_closed_SESSION_restored_globallease_FREE=True,
 **times,owner=launch['owner'],node=node['node'],original_worker_identity_before_wait=worker,go=g,
 selected_model_source=dict(path='D:/claude2/fangzhen/train/deploy/mod4_fudan_recovery_model2050.pt',SHA=g['source_SHA'],bytes=386869,iteration=2050,Adam17=41240,
  LR=g['source_saved_LR'],hidden=[128,64,32],source_ONNX_actor8tensors_exact=True,selected_CPU_decode_consumed=1,production_GPU_decode_consumed=1,
  original_training_directory_same_number_PT_byte_mismatch_preserved=True,original_training_PT_tensor_identity_UNKNOWN=True),
 actual_FIRST=first['first'],actual_native24=first['native24'],actual_CUDA_fullrestore=first['source_restore'],
 recipe=dict(num_envs=20000,ground_envs=2000,JUMP_envs=18000,persistent_modes=dict(ground=0,jump=1),reward_routing='Separate originalE0ground or byte-literal FudanJUMP per environment, no term blending',
  original_Fudan_commit='8204e853dfd2ed06d85a322e1a998c3d20a3be2c',original19methods_fullconfig16weights_byte_literal=True,
  self_dt=.02,clip_single=2.5,total_positive_clip=False,current_previous_contact_and_air_memory_across_reset_unchanged=True,
  source_manual2050_adapter_NOT_used=True,plane_friction_restitution=[.5,.5],original_JUMP_commands=dict(vx=[-2.1,2.1],yaw=[-2.,2.],height=[.12,.15],resample_s=20),
  policy_hz=50,feedback_hz=100,physics_hz=400,physics_dt=.0025,TGS=[32,4],dtype='float32',nominal_gas_N_engineering_each=400,k=2000,
  D0white_v3_D1_D7=True,action_clip=6,original_PD_torque_speed_target_delay=True,per_env_closure_m=.002,mimic_rad=.01,
  gamma=.9801,lam=.9025,source_rollout48x10ms_equals_target24x20ms=True,
  source_parameters_and_all17Adam_and_actual_LR_retained=True,new_physics_DR_episodes_queues_samplingRNG_explicit=True,no_exact_PhysX_resume=True,
  scripted_force_root_velocity_or_teacher_injection=False,old_E0_models_read_or_trained=False),
 actual_admission80=dict(passed=True,controls=8,physics=64,feedback=16,PT_NN_PPO=0,RC=0,all_waited_EX_free=True),
 original_errors_preserved=['Initial matching-number trainingPT/deployPT byte-hash mismatch; selected exported actor later proved exact all8 tensors',
  'Two local guessedE2 caller path lookups absent; actual source paths then located',
  'New interface sourceV1 invalid diagnostic keyword syntax before any fixture; V2 key-only repair5groups29reject',
  'AdmissionV1 bare sys.executable bypassed originalglibc240 wrapper: GLIBC_2.33 refusal before SDK/env/model/PPO; actualwait1/EXfree. V2 wrapper-only newout native80pass'],
 NEXT_ONLY=dict(normal_collector=str(normal),normal_status='FROZEN_UNUSED',normal_index_SHA=H(N/'INDEX240_NORMAL_READERS_FROZEN.json'),
  root_lease_label='ROOT240_EXCLUSIVE_NORMAL900_<freshID>',auth_provider=str(T.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py'),
  guards='FreshLOCALexactCIM/globalserialFREE; original signedLOCAL+REMOTE nominal-now<=900; originalowner850/node180 waits. ActualCOHORT_FINAL/OWNER_EXIT/NODE_EXIT/allownwaitout/knownoriginalPIDOUTorZ/shared+privateEXfree/freshCNone/uniqueoriginalownersegmentexactGO; one original rawfeeSUMONCE. No secondwatcher/earlycollector/oldonce.',
  formal_transfer='Onlyqualified1NEWformal/twohostSHA; errorspartial notpromoted; stdout64K refuses',
  NEW_formal_CPU=str(review),CPU_status='FROZEN_UNUSED_AFTER_FULL_JSON_GUARDS',NEW_formal_decodes=1,all_old_input2050_E0_native_normal86_PT_reads=0,
  CPU_asserts='Allfinite35/38/STD6,hidden12864/32,17Adam41240+20updates,iter2050+updates,actualLR/fullD0-D7/mixed2000groundmask/originalJUMPmemory/typed240/sourceaacco/finalsave>=GOdeadline. CUDAhiddeninsidePython.',
  not_native_WM_three_optimizer=True,normal_PPO_one_optimizer=True),
 no_new_budget_grant_or_canonical_copy_or_clearactive=True,strictreserve=86412.86069250107,
 old_E0_branch_retired_and_frozen_original_preserved=True,DR0_source_unselected_no_actualProbe_or_learning=True,
 W35_latest32481_full32s_SOURCE_READY_not_actual_eval=True,old_experts_SuperMimic_E3_and_true270_still_unfinished=True,
 no_fresh_GUI_or_oldviewer_query_reopen_kill=True)
put('CURRENT_ACTUAL240_MODEL2050_LITERAL40050_GROUND10_FIRST_AND_NORMAL_WORK_ORDER.json',order)
note=f'''# model2050 原完整PPO接续到400N50Hz：实际240

人类已选择从model2050适配到总计划400N、50Hz。旧E0跳跃后代停止续训，原冻结E0与所有历史保留。DR0两份源仅未选源码，没有实际新开DR0。

选中输入为3060 deploy/mod4_fudan_recovery_model2050.pt，386869B，SHA {g['source_SHA']}。初次与训练目录同编号PT的字节hash不相同，原false保留；不伪称二者模型相同或不同。后续新的必要身份目的：一次所选PT CPU decode和一次实际ONNX解析/外部initializer解码，证明actor8个权重与偏置张量全部相同。该PT完整actor35/critic38/STD6/17Adam通过，68tensor finite，源iter2050/Adam41240/LR{g['source_saved_LR']}。没有为了统计/Git重复读旧模型。

新目标使用ownMOD4原400N工程k2000、50Hzpolicy/100Hzfeedback/400Hzphysics、2.5msTGS32/4/F32、D0white_v3及D1-D7、clip6/原PD与扭矩转速/真实延迟/2mm每env闭链/.01mimic。保留输入128/64/32网络、全部actor/critic/learnedSTD/17Adam与实际LR；全新物理episode/DR/queue/采样RNG明确fresh，输入未保存RNG，不假精确续态。原100Hz的48步rollout适配到50Hz的24步，均.48s；gamma.9801/lam.9025按物理时间折扣。

2000个平地环境使用独立原E0奖励/命令，18000个JUMP环境使用pinned Fudan原19方法/完整config/16权重逐字相同的原奖励。clip2.5*dt.02/不total正裁剪/原contact与air-time跨reset记忆保留；只在外层映射own真实状态并抵消Lab额外dt。不继承另一AI手工移植的reset/几何适配，不加脚本力/速度/teacher动作，不放宽guard。

新source接口5groups/29reject，normal reader接口2groups/7reject。原接口V1非法诊断keyword导致语法拒绝在执行前；V2仅改keyword。原80env准入V1误用裸sys.executable绕开已存在glibc240 loader，GLIBC_2.33在SDK构造前拒绝，0PT/0NN/0PPO、wait1/EX释放；独立V2只换回原run-python.sh及新输出命名空间，真实80env/native8=64physics/16feedback/原奖励8calls，wait0/allownOUT/EX释放通过。没有安装/修改系统依赖。

唯一原owner PID{launch['owner']['pid']}/create{launch['owner']['creation']}，实际cwd={launch['owner']['cwd']}，任务owner根另存；node PID{node['node']['pid']}/create{node['node']['creation']}。原HMAC/twofcntl/raw收费函数沿用原源码，3900/save3600/exit300，不新grant/退款/补款/改账/复制canonical。源CPU资格是实际选中PPO CPU+实际0PT target，非伪造native loaded-model资格；完整CUDA复原与20k native24在实际新PPO前完成。

真实FIRST：新增1PPO/480000 own transitions，iter2051/17Adam41260；native24=192physics/48feedback；完整first {first['first']['first_complete']['bytes']}B SHA {first['first']['first_complete']['SHA']}。只代表当时更新/保存快照，不是连续健康或跳跃/270技能。

GO {times['GO_BJT']}；SAVE {times['SAVE_BJT']}；NOMINAL {times['NOMINAL_BJT']}；正常采集最早 {times['normal_earliest_BJT']}。原normal collector与NEWformal CPU已冻结未用。仅到原双900门禁后采集一次原收尾/一笔rawfee与1NEWformal/两hostSHA，再完整CPU一次；旧输入与旧once均0。后续无自动加时。

所有ROOT控制SSH最终关闭/SESSION恢复/globalleaseFREE。未来任何remote先fresh72精确当前owner/run/fullGO，再关闭72后访问其他目标；actual240关闭后binding历史化。保持当前训练，不加健康watcher或startup空GPU复查，不热改、重开旧GUI或称旧录像为live。W35/RM70/E2E3/完整SuperMimic与最终真实270稳定验收仍待完成。

本实际240唯一phase：mod4-model2050-onnx-matched-literal-fudan-jump400n50-ground10-ppo240。保留所有原错误、source、CPU、SDK、FIRST和完整UTF8；PT/ONNX/data/NPZ/USD/media仅真实path/bytes/已有producerSHA。后续正常收尾普通append，不重record/retag；保护所有1513旧tag对象/peels。
'''
with(R/'ACTUAL240_MODEL2050_LITERAL40050_FIRST_EXPERIMENT_NOTE.md').open('x',encoding='utf8')as f:f.write(note)
prior=read(T/'USER3060_SELECTED_MODEL2050_PROVENANCE_V239_20261101/reports/AUTOMATION_ACTUAL239_AND_CLOSED235_UPDATE_REQUEST.json')
header=f'''CURRENT_ACTUAL240_MODEL2050_ONNX_MATCHED_LITERAL40050_GROUND10_FIRST_20261101 supersedes239choicepending/DR0main/noH1learning. FIRST READ N/reports/CURRENT_ACTUAL240_MODEL2050_LITERAL40050_GROUND10_FIRST_AND_NORMAL_WORK_ORDER.json and KNOWN_ACTIVE240_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json; N=T/MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101. Human selected2050->400N50,oldE0descendantsretired/originala92frozen,DR0offpackagesUNSELECTED/noactualDR0SDKorPi. Actualnewrun{launch['run_id']};sole72owner{launch['owner']['pid']}/create{launch['owner']['creation']},node{node['node']['pid']}/create{node['node']['creation']},GPU16828f91. Exactworkerbeforewait/currentexe/argv/cwd inFIRST/binding,preexecbashpreserved. Originalowner/nodeglobalcwd /home/lc01/Zonglin Li/zonglin2 distincttaskroots. Source selecteddeployPT2050 {g['source_SHA']}/386869B/2050/17Adam41240/LR{g['source_saved_LR']},actualONNXactor8lineartensorsidentical/fullCPU68finite/1decode CONSUMED;initialsame-numbertrainingPTbytehashmismatchfalsepreserved,trainingPTtensoridentityUNKNOWN,noforstats/Git PT/ONNX rereads. Sourcehidden128/64/32/fullactor35critic38STD6/all17AdamLR restoredexactCUDA,productionGPU1read/decodeCONSUMED;originalsourceRNGnotpresent,targetDR/episodes/queues/samplerfresh. ActualFIRSTnew1PPO/480000owntransitions/2051/17Adam41260/full{first['first']['first_complete']['bytes']}B SHA{first['first']['first_complete']['SHA']};native24/192physics48feedbackactualPASS,notcontinuoushealth/FINAL/jump270. AllROOTSSHfinallyclosed/SESSIONrestored/globalclientleaseFREE;preservehealthyjob/nohotpatch/restart/secondwatcher/startupfree-recheck. Recipe20k:2000persistentoriginalE0ground/18000literaloriginalFudanJUMP,disjointrewardandcommands;noE0weights. Original19methods/fullconfig16weights byte-literal,clip2.5*dt.02/no totalpositiveclip/contactpreviousairmemoryacrossreset原样;outerLabdtcancelledonly/ownFK+actualSDKbindingsoutside. Originalplaneμ/rest.5/.5,vx±2.1/yaw±2/height.12..15/20s unchanged,nostrongk3500source/noexternalvelocitypush. Target400Nengineeringk2000/D0white_v3D1-D7/50policy100feedback400physics2.5ms32/4F32/6clip/PDtorque-speed/delay/perenv2mm/.01. 48source100Hzsteps->24target50Hz=.48s/gamma.9801/lam.9025,notrewardchange. SourceCPU5groups29reject/normalCPU2groups7rejectCONSUMED;V1syntaxdiagnostickeyfalsepreexec,admitV1barePythonGLIBC_2.33preSDKfalse/allwait1EXfree,independentV2originalglibc240wrapper-only80env0PT8controls64physics16feedbackRC0/allwaitEXfreeCONSUMED,noinstall. GO {times['GO_BJT']}/SAVE {times['SAVE_BJT']}/NOMINAL {times['NOMINAL_BJT']},normalearliest {times['normal_earliest_BJT']};3900/save3600/exit300/noextension/newgrant. NEXT ONLY N/normal240/collect240_original_formal_cost_normal900_UNUSED_once.py --root-lease-label ROOT240_EXCLUSIVE_NORMAL900_<freshID> --auth-provider C:/Users/lulu/Desktop/claude/mjcf/MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py --additional-control-pattern <allknowncurrentcontrolbasenames> --caller-index-SHA 5281aa5a2b9ad31e8a36b034f349bf2910d6557f530fa00fe0a14ca1878d13fd. FROZEN_UNUSED/Python314/freshLOCALexactCIM/globalserialFREE/originalsignedLOCAL+REMOTE900/owner850-node180 unchanged. ActualCOHORT_FINAL/OWNER_EXIT/NODE_EXIT/allownwaitout/knownPIDOUTorZ/private+sharedEXfree/freshCNone/uniqueownerexactGOsegment beforeoriginalonefeeSUMONCE+qualifiedNEWformaltransfer1twoSHA. Partial/errornotpromoted;known64Krefuses. ThenfullJSONguards->N/normal240/review240_NEW_formal_initial_whole_CPU_UNUSED_once.py --caller-index-SHA same5281:env_isaaclabCPU/CUDAhiddeninside/NEWformal1bytehashdecode/allold2050E0native86PT0;finite35/38/STD6hidden12864/32/17Adam41240+20updates/iter2050+updates/sourceaacco/typed240/fullD0-D7+mixed2000mask+originalJUMPmemory/actualadaptiveLR/save>=deadline. OrdinaryPPOoneoptimizer,notnative3opts/20nativeiter. Neverrerun240FIRST/admit/sourceCPU/old235closedonce forstats/Git. FutureANYremote fresh72 exactcurrent240owner/run/fullGO,close72before210/86;afterclosurebindingHISTORICAL. Sole72budget/security/globalserial allretain. Same208childonlyLOCALW35sourceCPU preparing authority240 adapter forlatest32481full32s;notactualSDK/nohotadd/nootherwriter;onlyfreezeINDEXinclude. W352d0/32481latestqualified/full32snotexecuted,oldE2latest736717/42913closed91,fullskillsSM/E3/true270unfinished. NoGUIfreshrequest/query/reopen/kill. Sameautomation ACTIVE/hourly/originalchat/noGoal/newautomation/notifymeaningfulonly/quietunchanged. Newactual240uniquephase mod4-model2050-onnx-matched-literal-fudan-jump400n50-ground10-ppo240;actualrefs/indexfirst/ANYtagCONSUMEDneverrecordretag/protect1513oldobjectspeels;all240false/source/fullUTF8/CPU/admit/CUDA-FIRST/normalunused/appreceipts capture,PTONNXdataNPZUSDmedia metadataonly/noFORGitreads. LaterclosingfeeNEWCPUordinaryappend;postGitnoHEAD-chasingreports. Below old239/238/235statuses andonce are HISTORICAL,notrerun directives.\n\n'''
request=dict(prior);request['prompt']=header+prior['prompt'];put('AUTOMATION_ACTUAL240_FIRST_UPDATE_REQUEST.json',request)
binary=[dict(path=str(N/'source_model/model_2050_from_selected_export.pt'),bytes=386869,SHA=g['source_SHA'],producer='Necessary240selectedsourceCPU')]
installation=read(R/'INSTALL240_SOURCE_ASSET_MANIFEST.json')
for x in installation['files']:
 if Path(x['relative']).suffix.lower()in('.npz','.npy','.usd','.usda','.usdc','.stl','.obj'):
  binary.append(dict(path=x['local_path'],bytes=x['bytes'],SHA=x['SHA'],producer='Necessary240targetnamespace source-asset copy samepass SHA'))
for x in read(N/'onnx_identity/reports/ROOT240_ONNX_EXPORT_TRAINING_PLAY_TEXTS_ACTUAL.json')['artifacts']:
 binary.append(dict(path=x['local_path'],bytes=x['bytes'],SHA=x['SHA'],producer='Necessary240selectedONNXidentitytransfer1'))
roots=[N]+[T/p for p in ('transfer240_selected2050_fullPPO_source_once.py','read240_selected2050_ONNX_identity_assets_once.py','review240_selected2050_fullPPO_and_ONNX_CPU_once.py','prepare240_model2050_literal40050_package_once.py','test240_new_source_TaskGO_interfaces_CPU_once.py','test240_new_source_TaskGO_interfaces_CPU_V2_once.py','install240_model2050_target80_0PT_once.py','install240_admit80_V2_original_loader_only_once.py','start240_original_single_owner_model2050_FIRST_once.py',Path(__file__).name)]
put('CAPTURE240_ACTUAL_FROZEN_SCOPE.json',dict(epoch=time.time(),roots=[str(x)for x in roots],automation_request_path=str(R/'AUTOMATION_ACTUAL240_FIRST_UPDATE_REQUEST.json'),
 trials=['240 selected2050 transfer/hashmismatch originalfalse','240 ONNXexternal2 reads+selectedfullPPOCPU1 actor8identityPASS','240 originalcallerlookupfalse','240 sourceCPU_V1syntaxfalse andV2interfacepass','240 admissionV1bareloaderGLIBCfalse beforeSDK/allwaitout','240 admissionV2wrapperonly80actualnative8pass','240 soleownerCUDAfullrestore/native24/FIRSTnewPPO actual','240normalreadernewCPU andfrozenunused'],
 pending_excluded=['240 closingfee/newformal/initialCPU not yet eligible','W35authority240source active until frozenINDEX','No GUI or new physics eval admitted','DR0packages remainunselected'],
 binary_local_producer_metadata=binary,remote_artifacts_metadata_only=[first['first']['first_complete']],no_model_raw_GPU_for_Git=True))
print(json.dumps(dict(passed=True,run_id=launch['run_id'],**times,FIRST_new_PPO=1,iteration=2051,all_ROOT_SSH_free=True)))
