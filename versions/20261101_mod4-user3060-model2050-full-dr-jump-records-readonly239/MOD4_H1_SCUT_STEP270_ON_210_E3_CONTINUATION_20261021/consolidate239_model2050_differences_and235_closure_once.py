"""Consolidate existing text/JSON evidence only; no models/raw/network/SDK."""
from pathlib import Path
import hashlib,json,time
T=Path(__file__).resolve().parent
N=T/'USER3060_SELECTED_MODEL2050_PROVENANCE_V239_20261101';R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def meta(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
P=T/'USER3060_MODEL2050_NOMINAL_AND_TRAINING_DR_V239_20261101/reports'
j=read(R/'ROOT239_MODEL2050_EXPORT_TRAINING_PLAY_TEXTS_ACTUAL.json');extra=read(P/'ROOT239_2050_NOMINAL_EXPORT_TRAINING_PLAY_TEXTS_ACTUAL.json')
assert j['passed'] and extra['passed'] and j['model_binary_raw_reads']==extra['model_binary_raw_reads']==0
assert read(P/'ROOT239_2050_NOMINAL_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
texts={x['path']:x for x in j['full_UTF8']+extra['full_UTF8']}
run=next(p.rsplit('/',1)[0] for p in texts if p.endswith('/run_manifest.json'))
manifest=json.loads(texts[run+'/run_manifest.json']['UTF8'])
contract=json.loads(texts[run+'/src_snapshot/import_contract.json']['UTF8'])
delivery=json.loads(next(x['UTF8'] for p,x in texts.items() if p.endswith('/contract_rm2025_later.json')))
assert manifest['env']['RM_DR_OFF']=='0' and manifest['start_iteration']==2000
assert delivery['policy_hz']==100 and manifest['env']['RM_PHYSICS_DT_S']=='0.001'
assert all(x['stiffness_n_m']==3500 for x in contract['gas_springs'].values())
C4=T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101';close=read(C4/'reports/ROOT_E2_GUARD01_V3_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
cpu=read(C4/'reports/ROOT_E2_GUARD01_V3_NEW_E2_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')
assert close['passed_collection'] and cpu['passed'] and close['owner_closed']['canonical_None']
q=cpu['roles']['e2'];assert q['new_PPO_updates']==91 and q['save_at_or_after_requested_deadline']
fee=close['owner_closed']['original_one_owner_segment']['charged_expert_seconds']
put('ROOT239_CLOSED235_QUALIFIED_FORMAL_ORDINARY_SUPPLEMENT.json',dict(epoch=time.time(),passed=True,
 actual235_RUN='E2_B3AE_WORLD_MIMIC01_PPO235V4_20261101_0937',new_PPO_updates=91,new_own_transitions=43680000,
 formal={k:q[k] for k in ('path','bytes','SHA','finite_tensors','saved_iteration','Adam17_step','actual_saved_optimizer_LR','actual_saved_epoch','save_at_or_after_requested_deadline')},
 raw_original_fee_SUMONCE=fee,closing_balance_snapshot_not_live=405079.21081233025,
 all_original_owner_node_worker_waitout_and_locks_free=close['owner_closed']['passed'],canonical_None_at_original_close=True,
 input_model_rereads=0,NEW_formal_reads=cpu['NEW_formal_reads'],CUDA_initialized=cpu['CUDA_initialized'],
 current235_binding_now_HISTORICAL=True,full_E2_skill_or_SuperMimic_not_inferred=True,
 source_reports=[meta(C4/'reports/ROOT_E2_GUARD01_V3_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json'),meta(C4/'reports/ROOT_E2_GUARD01_V3_NEW_E2_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')]))
facts=dict(epoch=time.time(),human_selected='ONNX exported from checkpoint model_2050',host='LULU/lulunomaro@10.24.4.249, original pinned SSH',
 selected_export='D:/claude2/fangzhen/train/deploy/mod4_fudan_recovery_model2050.onnx',
 export_sidecar_iteration=2050,export_actor_obs=35,export_actions=6,export_hidden=[128,64,32],export_activation='elu',
 export_sidecar_checkpoint='D:/claude2/fangzhen/train/deploy/mod4_fudan_recovery_model2050.pt',
 matching_training_run=run,matching_run_model2050='metadata inventory only; PT/ONNX bytes not opened or hashed',
 cryptographic_identity_between_run_PT_deploy_PT_and_ONNX='UNKNOWN; no export source SHA in the selected sidecar',
 training_source_iteration=2000,training_source_SHA=manifest['init_checkpoint_sha256'],training_num_envs=manifest['num_envs'],
 training_policy_Hz=100,training_physics_dt=.001,training_TGS=[32,32],nominal_training_gas=contract['gas_springs'],
 training_DR_OFF=False,training_DR_implementation='Original SCUT EventCfg/noise/delay, not our current D0white_v3+D1-D7 exact recipe',
 DR_active_log_and_source=True,all_randomized_actual_setter_values_not_independently_readback=True,
 DR_terms_source=['mass/inertia','COM x+-40mm/y,z+-20mm','wheel friction .7..1.3','PD and motor effort','joint armature/friction','sensor noise/bias/delay','target delay','gas stiffness .8..1.2/damping .7..1.3','velocity-setting push and external wrench'],
 playback=dict(policy_Hz=50,physics_dt=.0025,gas_k=3500,DR_sampling_in_captured_player=False,
  course_step_height=.11,tread=.7,root_at_t3=dict(z=.5981809885758279,terrain_top=.22,local_height=.37818098857582794),
  maximum_recorded_advance=2.226625117168544,final_live_log_reset_count=19,
  bilateral_air_contacts_or_landing_stability_not_recorded=True,single270mm_jump_not_verified=True,
  action='raw ONNX -> constant PD -> torque clip, once each20ms then hold8 MuJoCo steps',
  CAD_diff_projection=False,action_clip6_in_player=False,torque_speed_curve_in_player=False,
  player_reset='tilt >70deg or root < local_top+.07; no closure/mimic termination check in this script'),
 training_guards=dict(closure_m=.002,mimic_rad=.05,bad_orientation_rad=1.4706289056333368,low_base_threshold=-1.,base_contact_disabled_FUDAN_EXACT=True),
 reward_same16weights=True,reward_byte_literal_identical=False,
 reward_source_differences=['manual Fudan function port','reset_fudan_state clears last_contacts and base_air_time; our literal branch preserves upstream cross-reset memory','L0/theta use WORLD thigh/wheel vertical delta and atan2; our adapter uses own hip anchors/wheel BODY geometry'],
 old_our_E0_branch=dict(status='Retired for future training by human, originals preserved',nominal_gas_k=2000,policy_Hz=50,physics_dt=.0025,TGS=[32,4],mimic_rad=.01,
  starting_model='Frozen E0 walking expert a92, not the other branch trained jump checkpoint2000',
  inherited_left_crank_saturation='Actual220/221/223/224: e629 mean below-6 all1000 controls; original a92 also below-6 on same32 NEW223 inputs; source STD23.36029 predates3h',
  independent_repair225_short_test='Actual230:9 sampled bilateral wheel-air runs, heading drift/nonwheel contacts; not stable270',
  old_model_or_raw_reopened_for_this_comparison=False),
 conclusion='DR alone is not established as the reason our E0 branch failed. Starting actor saturation is direct evidence; nominal spring, timing, guards, adapter and test terrain also differ. No single-variable causal proof.',
 DR0_status='Two off-only source packages frozen, actual0PT/model/learning/GO not selected or run. Human now reviewing2050 route; no automatic start or adoption of other stronger spring/looser guards.',
 new_learning_or_SDK_or_model_binary_actions=0,all_ROOT_SSH_closed=True)
put('CURRENT_ACTUAL239_MODEL2050_TRAINING_PLAY_DIFFERENCES_AND_CLOSED235_WORK_ORDER.json',facts)
note='''# 3060 model_2050 与旧 E0 跳跃支线的核验差异

已只读核对原 3060 主机的 model_2050 ONNX 说明、对应编号训练记录、训练源码快照、气弹簧合同、播放器源码和实际播放日志。未上传、删除、启动任务、运行推理或读取 PT/ONNX 权重。所有 ROOT SSH 已关闭。

| 项目 | 3060 model_2050 对应记录 | 我们已作废的 E0 跳跃支线 |
|---|---|---|
| 起点 | 先前复旦平面跳跃 model_2000，再做台阶续训 | 冻结 E0 平地专家的后代 |
| 气弹簧 | 训练、播放 k=3500 N/m | 名义400N工程模型 k=2000 N/m |
| 训练时钟 | 100Hz policy、1ms physics、TGS32/32 | 50Hz policy、2.5ms physics、TGS32/4 |
| DR | RM_DR_OFF=0，SCUT 事件/噪声/延迟等开启 | D0 white_v3、D1-D7，总计划的另一套范围与实现 |
| 保护 | 训练 mimic=.05；播放器仅倾斜70度/低底盘重置 | mimic=.01、闭链2mm、原MOD4终止保留 |
| 所见台阶 | 每级11cm、踏面70cm，日志到累计22cm | 最终验收为单级27cm真实越台和稳定恢复 |

2050 播放日志在3秒时 root z=.59818m、当地台面=.22m、相对台面底盘高=.37818m。该日志支持机器人进入更高的阶梯区域，未记录双轮接触/完整脚印/稳定落台，不能代替270mm验收。末段日志累计19次重置。播放器固定名义参数，没有重放训练整套DR；因此“开DR训练出的模型能跳”有记录依据，“这次播放在fullDR随机化中完成”没有。

训练侧16项权重相同，但3060实现不是逐字相同的原函数：其适配器重写函数，reset清空接触/air-time记忆，腿长/腿角使用WORLD竖直差。我们保留原函数与跨reset语义，另用真实own hip锚点到轮轴BODY映射。这也是任务差别，不能仅凭同权重宣布行为完全等价。

我们旧E0支线已有直接异常证据：左crank均值连续1000/1000低于-6；冻结E0原件在同批32条新状态上也有该特征，原左STD已23.36029。它不是最近三小时才产生，也不能简单归为DR过多或训练不足。长训前未先排除该输出饱和是本方工作失误。独立修复副本225在230短评测出现9段双轮采样腾空，但有航向漂移/非轮接触，仍非稳定跳跃或270成功。原件不改，旧支线依人类要求不再续训。

上述差异不能给出唯一物理因果，也不能证明400N50Hz下必定学不会。当前有依据的选择是从已出现跳跃行为的2050路线做独立适配与回归，逐项守住400N50Hz/原奖励/原guard，而不是直接复制其更硬弹簧、速度注入或较宽保护。等待人类选择后续起点；DR0仅源码和0PT准入源码冻结，未实际运行。

导出说明绑定deploy/model2050.pt、ONNX与2050编号；训练目录中存在对应model_2050.pt。说明未含导出源SHA，本次未打开模型，因此训练PT→deployPT→ONNX的逐字身份仍UNKNOWN，不伪称三者hash已核同。

同次正常收尾：E2实际235V4完整一小时结束，新增91PPO/43,680,000 own transitions，iter42913/17Adam861120，正式7367172a4673ba2f13869916f6a08c6de89fa6354767c10febc408bc2b39de2b/14616497B，175finite tensors，NEWformal CPU一次通过。原费3638.866696357727 SUMONCE、closing405079.21081233025仅历史快照。原235 binding已历史化，未来须fresh当前authority。该收尾不是E2全技能或SuperMimic验收。

所有239 codec拒绝、修复和全文、235原closing/费用/NEWCPU与两份DR0冻结源码一起归档；无新训练/GO/grant，原模型/轨迹未为Git重读。后续决定/新结果普通追加或真正新学习phase，不能重record既有235/237标签。
'''
with (R/'COMPARISON239_MODEL2050_AND_OLD_E0_BRANCH.md').open('x',encoding='utf8') as f:f.write(note)
prior=read(T/'E0_FROZEN_BASE_DR0_JUMP_GROUND10_CURRICULUM_V238_20261101/reports/AUTOMATION_USER238_DR0_RESTART_UPDATE_REQUEST.json')
header='''CURRENT_ACTUAL239_MODEL2050_READONLY_COMPARISON_AND_CLOSED235_20261101 supersedes235active/normal-unused/DR-alone-cause words. FIRST READ T/USER3060_SELECTED_MODEL2050_PROVENANCE_V239_20261101/reports/CURRENT_ACTUAL239_MODEL2050_TRAINING_PLAY_DIFFERENCES_AND_CLOSED235_WORK_ORDER.json and COMPARISON239_MODEL2050_AND_OLD_E0_BRANCH.md. User selected exportedmodel2050 ONNX on3060;actualtext-only lookup consumed,allSSHfinallyFREE,0model/PT/ONNX/SDK/NN/inference/task writes. Training RM_DR_OFF0/SCUT events actual registered,100Hz/1msTGS32/32/k3500;play50Hz/.0025/k3500/noDRsamplers/11cmrisers,logreachedcumulative22cm,19resets,no full270contact/landing proof. 16weights same butmanualport/resetcontactairmemory/WORLDgeometry differ fromourliteralJUMP. ExportsourceSHA absent,runPT-deployPT-ONNX byteidentityUNKNOWN;do not claimhashverified orrepeatlookup forstats/Git. Human askswhyothercanjump:oldE0inheritedleftcranksaturation directevidence,notDRsolecause;startingmodel/spring/rates/guards/testdiffer,nouniquecausalclaim. OldE0descendants2df/e629/225 retiredfortraining;originala92frozen. DR0 userapprovedallrandomizationoff earlier, butlatest3060finding/newroutechoiceispending:do notautomaticallylaunchDR0 orsilentlyadopt2050 untilstrategyselected+typednewsource/admission. DR0 core T/E0_ALL_RANDOMIZATION_OFF_DR0_SOURCE_CONTRACT_V1_20261101/INDEX_DR0_OFF_SOURCE_CORE_FROZEN.json SHA71d34a674382769f04f36a1ee6fc2018ba7e5215d14fbc7553471b11cf94f029 and64env0PTsource T/E0_DR0_OFF64_ZERO_PT_ADMISSION_SOURCE_V1_20261101/INDEX_DR064_SOURCE_FROZEN.json SHAd28f747423efd71143699f39bbea0827bd97033a6cd520965454ce4f52e5c3d6 frozenSOURCE_ONLY/UNSELECTED,SDKmodelGPUremote0,noactualoff0PT/learning. E2actual235V4normal+NEWformalCPU RETURNED0/CONSUMED,91newPPO/43,680,000transitions/42913/Adam861120,formal7367172a4673ba2f13869916f6a08c6de89fa6354767c10febc408bc2b39de2b/14616497B/175finite/1transfertwoSHA1CPUdecode,oldPT0. fullsave>=deadline/allwaitout/sharedprivatefree/CNone;rawfee3638.866696357727 SUMONCE/closing405079.21081233025 historicalnotlive.235bindingHISTORICAL,do notrerunnormal/CPU/FIRST/transfer/hash. FutureANYremote freshcurrent72authority thenclose72beforetarget. No currentH1learning afteractualclosure;notpermanentfreeclaim/fullskill. LatestW35qualified2d0/32481/651260;full32snewsourceREADYonly,notexecuted. User237GUIComputerUsephysicallyEscape-stopped,no freshGUIrequest/query-reopen-kill. Same208child onlyLOCALsourceCPU,no new/nested/Astra/Sol. Sameautomation ACTIVE/hourly/originalchat,noGoal/newautomation. Keepquietunchanged,notifymeaningfuloutcomesonly. New239phase unique mod4-user3060-model2050-full-dr-jump-records-readonly239;actualtag/HEAD/index first,anyexistingtagCONSUMEDneverretag;protect1512oldobjectspeels. Includeall239false/texts/235closing/DR0coresource andsource-readererrors+appreceipts,metadataonlybinary/noFORGitmodelrawGPU;laterappendonly. Allsole72budget/globalserial/security400N50D0-D7/2mm/mimic01boundaries retained. Below historical235normal/DR0 oldprompts are NOT once rerun directives.\n\n'''
req={k:v for k,v in prior.items()};req['prompt']=header+prior['prompt']
put('AUTOMATION_ACTUAL239_AND_CLOSED235_UPDATE_REQUEST.json',req)
roots=[T/'USER3060_FULLDR_JUMP_READONLY_V239_20261101',T/'USER3060_FULLDR_JUMP_READONLY_V239V2_20261101',T/'USER3060_FULLDR_JUMP_READONLY_DETAILS_V239_20261101',N,P.parent,
 C4,T/'E0_ALL_RANDOMIZATION_OFF_DR0_SOURCE_CONTRACT_V1_20261101',T/'E0_DR0_OFF64_ZERO_PT_ADMISSION_SOURCE_V1_20261101']
roots += [T/p for p in ('read239_3060_user_jump_inventory_once.py','read239_3060_user_jump_inventory_V2_once.py','read239_3060_selected_jump_records_once.py','read239_selected_model2050_export_training_play_once.py','read239_model2050_training_DR_nominal_and_player_XML_once.py',Path(__file__).name)]
put('CAPTURE239_ACTUAL_FROZEN_SCOPE.json',dict(epoch=time.time(),roots=[str(p) for p in roots],automation_request_path=str(R/'AUTOMATION_ACTUAL239_AND_CLOSED235_UPDATE_REQUEST.json'),
 trials=['239 original codec utf8-sig refusal before directory inventory','239V2 corrected codec metadata-only inventory','239 selected source/log capture, many launcherlogs retained','239 human selected2050 exact export/play/training source','239 additional nominalgas/contract/XML/registeredDR evidence','235 normal/oneNEWformalCPU ordinarysupplement','238 alloff core+64env0PT source only; readerfalse retained'],
 pending_excluded=['No DR0 actual0PT/learning selected','No new2050 adaptation/model import orbinarySHA/inference','No newW35latest32s SDK execution','No GUI query/reopen'],
 binary_local_producer_metadata=[dict(path=q['path'],bytes=q['bytes'],SHA=q['SHA'],producer='Original235normal+NEWCPU consumed')],
 remote_artifacts_metadata_only=[dict(path=p,bytes=x['bytes'],SHA=x.get('SHA','unknown'))for p,x in texts.items() if p.endswith(('.pt','.onnx','.npz'))]))
print(json.dumps(dict(passed=True,comparison=str(R/'COMPARISON239_MODEL2050_AND_OLD_E0_BRANCH.md'),new_model_reads=0,new_learning=False,closed235_updates=91)))
