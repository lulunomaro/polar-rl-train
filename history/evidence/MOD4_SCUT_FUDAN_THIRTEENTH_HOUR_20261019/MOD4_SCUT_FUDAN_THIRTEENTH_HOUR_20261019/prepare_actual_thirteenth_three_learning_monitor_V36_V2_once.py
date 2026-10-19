"""Prepare the next normal full-cohort handoff only after actual positive learning."""
from pathlib import Path
import ast,datetime,hashlib,json,shutil,time,tomllib
B=Path(__file__).resolve().parent;W=B.parent;P=W/'MOD4_SCUT_FUDAN_TWELFTH_HOUR_20261019';R=B/'reports'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as stream:json.dump(v,stream,ensure_ascii=False,indent=2)
d=json.loads((R/'THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes())
a=json.loads((R/'THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json').read_bytes())
f=json.loads((P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
v=json.loads((R/'TWELFTH_HOUR_LOCAL_EVENTS_AND_DRIFT_CPU_ACTUAL.json').read_bytes())
strict=json.loads((R/'TWELFTH_HOUR_LOCAL_STRICT_RECOVERY_NORMAL_AND_ACTUATOR_CPU_ACTUAL.json').read_bytes())
residual=json.loads((R/'TWELFTH_HOUR_LATE_YAW_ACTION_ACTUATOR_RESIDUAL_CPU_ACTUAL.json').read_bytes())
owner=d['owner']['detached_pid'];assert owner==340946 and a['three_actual_PPO_learning_verified'] and f['passed_all_three_whole_final_models_CPU']
assert set(f['one_original_writer_actual_segment']['experts'])=={'h1','e2','recovery'} and d['specs']['h1']['human_explicit_GPU_sharing'] is True
for key,x in a['experts'].items():
 assert x['actual_GO'] and x['actual_production_log_positive'] and x['actual_matching_GPU_worker_compute'] and x['GO']['source_SHA']==f['experts'][key]['final']['SHA']
assert (B/'payload/h1/three_real_gpu_resource_v1.py').read_bytes()==(B/'three_real_gpu_resource_shared_user_v2.py').read_bytes()==(P/'payload/h1/three_real_gpu_resource_v1.py').read_bytes()
for name in ('collect_next_hour_missing_closed_finals_bounded_owner_wait_V2_once.py','review_next_closed_hour_finals_whole_model_original_cost_CPU_once.py'):
 s=(P/name).read_text('utf8');assert '329132' in s;s=s.replace('329132',str(owner));ast.parse(s)
 with (B/name).open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
F=B/'future_same_recipe_hour_templates';F.mkdir()
for q in (P/'future_same_recipe_hour_templates').glob('*.py'):
 if q.name=='three_real_gpu_resource_shared_user_v2.py':
  shutil.copy2(q,F/q.name);continue
 s=q.read_text('utf8')
 if q.name=='prepare_next_three_closed_sources_one_hour_CPU_once.py':
  s=s.replace("T=W/'"+P.name+"'","T=W/'"+B.name+"'").replace('T3sf13_1910v18','T3sf14_1910v19').replace('THREE_GPU_SCUT_FUDAN_HOUR18_','THREE_GPU_SCUT_FUDAN_HOUR19_')
  assert "previous_runtime_root=old['roots'][key]" in s and "resource=prior/'three_real_gpu_resource_v1.py'" in s
 elif q.name=='deploy_three_next_closed_source_hours_once.py':
  s=s.replace('T3sf13_1910v18','NEXT_ROOT_ONLY').replace('T3sf12_1910v17','T3sf13_1910v18').replace('NEXT_ROOT_ONLY','T3sf14_1910v19').replace('329132',str(owner))
  assert "set(rows[0]['experts'])=={'h1','e2','recovery'}" in s and 'T3sf13_1910v18/owner' in s
 ast.parse(s)
 with (F/q.name).open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
assert len(list(F.glob('*.py')))==5 and (F/'three_real_gpu_resource_shared_user_v2.py').read_bytes()==(B/'payload/h1/three_real_gpu_resource_v1.py').read_bytes()
pre=(F/'prepare_next_three_closed_sources_one_hour_CPU_once.py').read_text('utf8')
assert pre.index("for c in C.glob('*.py')") < pre.index("resource=prior/'three_real_gpu_resource_v1.py'") < pre.index("m=dict(oldm,source_SHA=")
rewards=[]
for name in ('h1_scut_fudan_jump_reward_v1.py','h1_takeoff_progress_environment_v2.py','train_H1_ground_prelaunch_fullstate_v2.py'):
 rel=Path('payload/h1/job0/runtime/isaac/mod4')/name;assert (B/rel).read_bytes()==(P/rel).read_bytes();rewards.append(dict(path=str(B/rel),bytes=(B/rel).stat().st_size,SHA=H(B/rel)))
details={k:dict(source=d['specs'][k]['source_SHA'],Adam=d['specs'][k]['source_Adamstep'],worker=x['worker'],GO=x['GO'],save_Beijing=datetime.datetime.fromtimestamp(x['GO']['save_deadline'],datetime.timezone(datetime.timedelta(hours=8))).isoformat()) for k,x in a['experts'].items()}
closed={k:dict(final=x['final'],updates=x['updates'],Adam=x['all17Adam_after'],tensor_counts=x['whole_tensor_counts']) for k,x in f['experts'].items()}
errors=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(R.glob('*ORIGINAL_ERROR*.json'))]
work='NEXT_ACTUAL_THIRTEENTH_CLOSED_SOURCES_LOCAL_YAW_RECURRENCE_V36_WORK_ORDER.json'
put(B/work,dict(epoch=time.time(),version=36,previous_three_complete_CPU=f,previous_complete_sources=closed,actual_new_dispatch=d,actual_three_learning=a,details=details,unchanged_reward_files=rewards,local_new_source_behavior=v,local_strict_and_actual_actuator_review=str(R/'TWELFTH_HOUR_LOCAL_STRICT_RECOVERY_NORMAL_AND_ACTUATOR_CPU_ACTUAL.json'),late_yaw_action_actuator_existing_raw_comparison=str(R/'TWELFTH_HOUR_LATE_YAW_ACTION_ACTUATOR_RESIDUAL_CPU_ACTUAL.json'),current_errors_retained=errors,current_closing_helpers_bound_owner=owner,future_full_three_templates=str(F),future_namespace_only_reserved='T3sf14_1910v19',H1_sharing_exact_resource_override_after_controller_copy_retained=True,not_intermediate_whole_model_CPU_native_or_skill_PASS=True,local_player_unchanged_hour7_bundle=True))
put(R/'THIRTEENTH_ACTUAL_THREE_LEARNING_AND_FUTURE_SHARED_BINDING_CPU_ACTUAL.json',dict(epoch=time.time(),three_actual_GO_positive_PPO_matching_UUID_compute=True,actual_owner=owner,current_sources_all_three_latest_complete_hour12=True,previous_original_cost_once=f['one_original_writer_actual_segment']['charged_expert_seconds'],original_remaining_snapshot_read_only=f['remaining_snapshot'],human_authorized_H1_sharing_and_original_memory_lock_save_guards=True,resource_override_after_controller_copy_exact_bytes_retained=True,current_worker_PPO_reward_physics_SDK_runtime_LR_STD_and_accounting_unchanged=True,future_preparer_uses_each_actual_current_healthy_runtime_binding=True,future_owner_expects_three_completed_GO_experts=True,future_only_reserved='T3sf14_1910v19',local_only_new_source_four_trajectories_old_raw_read_only=True,current_metadata_not_whole_model_or_skill_qualification=True))
old=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert old['status']=='ACTIVE' and old['rrule']=='FREQ=HOURLY;INTERVAL=1'
prefix=old['prompt'][old['prompt'].index('最新用户“ H1 E3为什么这么慢 ”'):old['prompt'].index('最新actual V35')]
contract=old['prompt'][old['prompt'].index('人类三卡最大有意义利用'):old['prompt'].index('same mod4-10 ACTIVE/hourly/原target')]
contract=contract.replace('当前第十小时新3223源未自动替换玩家，不称已更新到第十小时','当前第十二小时新96db源未自动替换玩家，不称已更新到第十二小时').replace('旧cf5/db76/3302/1338/c174/81fc/a21a/1078/8d0c/3223本机结果','旧cf5/db76/3302/1338/c174/81fc/a21a/1078/8d0c/3223/96db本机结果')
head=f'''最新actual V36覆盖V35旧329132 active：第十二SCUT+Fudan小时三完整FINAL/wholeCPU/原独立费用sumonce结清，原owner与所有孩子actualout/EXIT0/canonicalNone/原两fcntl及private/shared实际free；H1 peer可继续存在。三卡已从各自这次最新完整源进入第十三小时，三actualGO/positivePPO/matchingUUIDworker compute均核真。M={B.as_posix()}；L=同workspace/{P.name}。先读M/{work}、M/reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json、THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json、THIRTEENTH_ACTUAL_THREE_LEARNING_AND_FUTURE_SHARED_BINDING_CPU_ACTUAL.json及L/reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json。later自己的完整sourceSHA/实际exe-argv-create/GO-save-EXIT/canonical/fcntl/freeMemory优先，不按PID/排程/快照冒永久alive/free/futureFINAL；旧工作单及Git全文保留只作历史。
第十二完整H1 {closed['h1']['final']['SHA']}/{closed['h1']['updates']}updates/Adam{closed['h1']['Adam']}；E2 {closed['e2']['final']['SHA']}/{closed['e2']['updates']}/Adam{closed['e2']['Adam']}；E3 {closed['recovery']['final']['SHA']}/{closed['recovery']['updates']}/Adam{closed['recovery']['Adam']}。三完整PT twohostSHA、199105/17598/17396全modelruntimefinite、17Adam每update20和actor9含STDcritic8全17项变化CPU真过。原{f['one_original_writer_actual_segment']['charged_expert_seconds']}s独立sumonce结清，remaining{f['remaining_snapshot']}仅读取snapshot，不二扣/refund/clearactive/取整。十一partial H1仍0GO0PPO0charge，旧第十42只归第十，不能移作十一新final。
当前neworiginalwriter{owner} root={d['source_root']}，E2node{d['nodes']['e2']['detached_pid']}、72H1node{d['nodes']['h1']['detached_pid']}/E3node{d['nodes']['recovery']['detached_pid']}。actual worker创建/GO/save/nominalend以下details及lateractual准；三actual学习metadata不冒中途wholeCPU/技能PASS/持续100%。原每卡GO到save3600/lifecycle3900含300exit/no24cutoff/20k×24，远端自主完整saveSDKclosechildwait/ownerterminal，不依Laptop/hourly，不hotextend/停健康卡或中途重型PT/行为审计。
closed_same_backend_production、reward_migration=False；原33错source/backend/GPU/Adam/schema/finite/EXIT/cost/runtime/AST负例拒绝，实际各target整source/installedSDKmath/RSL/runtimeassets核过。三SCUTFudan reward文件bytes exact前段，worker仅sourcefilenameAdam绑定，actorcritic六STD/17Adam/RNG/phase/20kDR整态继承；不回退源、重复SCUT迁移/telemetry插入、恢复旧reward或反向E3 native336。nativeCPU=None/source_native_CPU_SHA=null/nativeGPUwaitfalse，无重复standalone native/nativePASS；真正backend/physics/runtime改变仍走原流程。
人类“不用管占用的进程，你直接开始训练就行”的H1共享授权持续有效，只H1 key+human_explicit_GPU_sharing=True可与peer共存；E2/E3原GPUempty条件不改。保留free>7000MiB/RAM>8GiB/disk>25GiB、private持锁/shared短核、原canonical两fcntl及savedstop保护。H1 helper始终在controllers copy之后、manifest之前覆盖，部署前exactbytes核；本段及未来均按各自实际健康previous runtime/sourcefilename/Adam作AST规范化，不再复制十一partial或硬编码J旧绑定。peer PID66633/8526MiB仅历史snapshot，身份未知/AccessDenied原件保留，不再查身份、不kill/删锁/改peer，不冒整卡利用率都属自家。
只用新96db完整源本机CPU MuJoCo原October8 flat normal/jump×yaw0/pi四轨迹；旧case仅已有raw只读比较不重放。M/reports/TWELFTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json、TWELFTH_HOUR_LOCAL_STRICT_RECOVERY_NORMAL_AND_ACTUATOR_CPU_ACTUAL.json、TWELFTH_HOUR_LOCAL_EVENTS_AND_DRIFT_CPU_ACTUAL.json和TWELFTH_HOUR_LATE_YAW_ACTION_ACTUATOR_RESIDUAL_CPU_ACTUAL.json优先。两jump各原strict1起跳/1落地/1恢复且活15s，事件约1.135/1.385/2.815s，双轮最低净空峰.0727846m较上个实际已测3223的.0830886m低，prepare396且readyTrue，恢复最长4186callback较5066短。恢复后约12.7825s再次yaw越原.2rad（3223在15s内未越），末yaw-.271271比-.162085绝对值大；sticky recovered不能当持续stationkeeping。
两normal活15s，但末速度.0190732比.0142466大、净位移.287922比.219821大、末yaw-.493870比-.293521绝对漂移大。原起跳落地恢复事件仍有，但保持/净空/普通停车观测变差，不能只报PPO上涨或说整体修好。不同backend、无原20kDR、两yaw确定性小样本，不冒PhysX资格/统计显著/唯一奖励因果/完整normal无退化或毕业。
原46callback/14actuator/23reward列保持无重复，本机实际d.actuator_force六通道与d.ctrl在记录callback相等；normal九新项0/Fudan每weighted±2.5实核，不冒PhysX applied_torque或生产RewardManager/PPO return。新增只读旧raw对照：14到15s平均world wz约-.0321129rad/s（3223约-.0190252），actual wheel force indices2/5约.1900/-.1915（旧.1011/-.1019）；原joint-axis符号不是世界yaw力矩。两代在末秒action第0通道都100%触原clip-6，故不能把它独断为新唯一成因。原瞬时yaw-rate目标与累计heading恢复条件区别仅见既有source审查，非新完整live RewardManager/binary读回。所有原物理/控制/外部请求时钟/prepare80/takeoff16/land12/recover200和阈值未改，下一自然新源才新namespace复查，不重旧case/heldout调参/盲改rewardLRSTDphysicsCAD/actor输入/接触切mode/外力扶正或用户玩家。
下一小时末仅M自己的collect_next_hour_missing_closed_finals_bounded_owner_wait_V2_once.py与review_next_closed_hour_finals_whole_model_original_cost_CPU_once.py，绑定{owner}；不能重L329132或K partial旧collector/preparer/deployer/Task/native/once。相同source连接max900仅等actualCOHORT终态，actualclosed才取缺三完整FINAL/PT/原费用/out/canonicalNone/两原fcntl/private共享free，然后wholeCPU及时接续。H1 peer不等于本owneralive，不要求peer退出，如实存compute/freeMemory。提前距save加正常退出明显>900时，先localreports/CIM和短有界本机等待，临近再自己单collector；无第二watcher/并发SSH，不按排程猜FINAL，不机械等下heartbeat。missing/error原样留，finite实际返回/freshCIM后新有界只补缺，不重已完整PT/raw/once。
未来仅M/future_same_recipe_hour_templates全部五文件，M实际三路closed/fullCPU后复制新unused阶段prepare；T3sf14_1910v19仅reserved。模板是正常三完整final/各actualhealthy previous runtime与三charged experts；共享helper第五文件须一起复制并在controller copy后覆盖、manifest前及部署前exactbytes核，勿反向K partial两路或旧GPUempty阻断。metadata单连接max600/keepalive15/append-only journal，仅真实GO/PPO/GPU条件，不为瞬时public4active0新增等待，仍存rewardreadout，first正常批非aux效果或技能成绩；实际finite返回才交还transport。
'''
tail='''same mod4-10 ACTIVE/hourly/原target01a07a2d-9036-7531-a012-692df9f56353，无第二monitor/自动预算；健康unchanged/pending静默，仅新完整FINAL/新冻结/实质修复/重大退化/必需人类动作通知。第十二闭合/新本机yaw与normal退化及第十三接训通知后不重复firstmetadata；预算未结束不删monitor。
新stage scut-fudan-thirteenth-hour-closed-sources-local-recovery-drift-review只record一次，later实际Git回执优先，已record不重helper/record/tag/同commit，pushfail只已有objects。L unique3dd6197/taga317bf2/总1400及所有旧stage/helper/Task/native/once consume；十一preGO/unused绑定错误及原模板保留不覆盖。全部L/M新source/文本报告/原错误/未用helpers/工作单monitor/appreceipt/原费用入Git；>50MB全文orderedUTF8parts+全重组SHA，PT/NPZ/USD/ZIP/raw只producer actualpathsizeSHA保原件，不为Git重GPU/改账/重hash下载旧件/无限补HEAD。后续普通补档，trial用实际日期不回填历史。
'''
prompt=prefix+head+contract+tail+'\n第十二完整来源与第十三actual创建/GO排程：\n'+json.dumps(dict(closed=closed,owner=d['owner'],nodes=d['nodes'],source_root=d['source_root'],roots=d['roots'],details=details),ensure_ascii=False,indent=2)+'\n当前metadata原错误索引（原件保留，非GPU故障或网络已修复的证明）：\n'+json.dumps(errors,ensure_ascii=False)
put(B/'AUTOMATION_ACTUAL_THIRTEENTH_LOCAL_YAW_DRIFT_V36_ARGS.json',dict(mode='update',id='mod4-10',kind='heartbeat',name=old['name'],prompt=prompt,rrule=old['rrule'],status=old['status'],targetThreadId=old['target_thread_id']))
with (B/'STAGE_SUMMARY.md').open('x',encoding='utf8') as stream:stream.write('# Twelfth complete sources, thirteenth actual learning and local yaw/stopping regression\n\n'+json.dumps(dict(previous_complete_CPU=f,current_dispatch=d,current_actual_learning=a,source_reward_files_unchanged=rewards,new_source_local_behavior=v,local_actual_force_and_action_residual=residual,full_three_future_binding_and_shared_H1_exact_bytes_retained=True,no_budget_PPO_reward_LR_STD_physics_CAD_guard_or_player_change=True),ensure_ascii=False,indent=2))
print(json.dumps(dict(actual_three_learning=True,owner=owner,save={k:x['save_Beijing'] for k,x in details.items()},future_full_three_helpers_prepared=True,local_recurrent_yaw_and_larger_normal_drift_retained=True)))
