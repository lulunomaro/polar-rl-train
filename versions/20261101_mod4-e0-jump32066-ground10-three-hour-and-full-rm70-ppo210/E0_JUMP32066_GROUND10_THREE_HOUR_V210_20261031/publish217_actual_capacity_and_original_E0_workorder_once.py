"""Local report-only publication after original217 has returned. No raw/model read."""
from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
Q=T/'W35_SHARED_MATERIAL_20K_ORIGINAL_PHYSX_ADMISSION_V217_20261101'
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
probe=read(Q/'reports/ROOT217_ORIGINAL_20K_SHARED_MATERIAL_NATIVE_OR_ERROR_RETURNED_ACTUAL.json')
assert probe['passed'] and probe['returncode']==0 and probe['all_own_children_waited']and probe['private_EX_released']
assert probe['actual_material_limit_error_count']==0 and all(probe['actual_original_shared_CAD_material_checks'])
assert read(Q/'reports/ROOT217_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
native=probe['native_result'];assert native['num_envs']==20000 and native['controls']==8
current=read(R/'CURRENT_ACTUAL210_E0_THREE_HOUR_CONTINUES_W35_MATERIAL_FAILURE_AND216_EXIT_V2.json')
comparison=read(T/'W35_FULL_RM70_MATERIAL_LIMIT_REPAIR_SOURCE_V214_20261101/reports/ROOT214_E0_SAVED_UPDATES_SOURCE_COMPARISON_ACTUAL.json')
summary=dict(epoch=time.time(),actual_original217_passed=True,elapsed_parent_seconds=probe['epoch']-probe['started_epoch'],
 source214_index_SHA='8a27849574f33e5d7e0c619526ddfead25ac57c54bede975315082e2a25ce171',
 source214_worker_SHA='dc105696ae3c65702d963d7d91650cec656d471fcc3a478d62b5b27dc17a29d5',
 actual_num_envs=20000,controls=8,physics_callbacks=64,feedback_samples=16,
 processed_queue_calls_each=64,reward_dt=.02,material_setter_calls=3,
 own20k_D0_D7_restore_and_new_episode=True,actual_bound_CAD_material=[.9,.8,0.],
 terrain_shared_material_checks=probe['actual_original_shared_CAD_material_checks'],
 zero_known_64K_errors=True,all_original_terminations_zero=True,
 max_closure_error_m=native['original_health_report']['max_closure_error_m'],
 max_mimic_error_rad=native['original_health_report']['max_mimic_error_rad'],
 actual_PhysX_material_handle_count='UNKNOWN_NOT_USD_PRIM_COUNT',
 actual_parent_original_identity=probe['original_worker_identity'],
 original_identity_was_preexec_bash_not_fabricated_Python=True,
 waited_RC0=True,SDK_finally_completed=True,private_EX_released=True,
 original_source_PT_opens=0,NN_constructors=0,optimizer_updates=0,
 full_W35_PPO_restore_or_native24_or_FIRST=False,full_RM70_skill=False,
 E0_untouched=True,global_serial_control_client_lease='FREE',
 metadata_reader_scope=dict(phase_JSONL_numerical_parse_passes=1,
  phase_JSONL_separate_full_UTF8_capture_passes=1,total_metadata_JSONL_opens=2,
  old_trajectory_JSONL_reads=0,original_purpose_field_actual_phase_metadata_JSONL_pass=1,
  clarification='The original field counts the numerical pass; the frozen parent also opens its new small metadata report for full-UTF8 retention. Keep both source and actual counts.'),
 generated_USD_capture_scope=dict(local_original_full_UTF8_preserved=True,
  Git_embedding_must_be_metadata_only=True,
  generated_USD_paths=[dict(path=x['path'],bytes=x['bytes'],SHA=x['SHA'])for x in probe['full_UTF8']if Path(x['path']).suffix.lower()in('.usd','.usda','.usdc')]))
put(Q/'reports/ROOT217_ACTUAL_CAPACITY_PASS_AND_READER_CAPTURE_SCOPE.json',summary)
current.update(epoch=time.time(),current_update='E0 original three-hour learning window continues; W35 original failed worker out; actual217 full20k shared-material model-free admission PASS',
 actual217_material_repair=summary,latest_saved_E0_source_comparison_report=str(T/'W35_FULL_RM70_MATERIAL_LIMIT_REPAIR_SOURCE_V214_20261101/reports/ROOT214_E0_SAVED_UPDATES_SOURCE_COMPARISON_ACTUAL.json'),
 latest_E0_saved_snapshot_only_not_current_watch=dict(epoch_BJT='2026-11-01T01:12:38.65+08:00',new_PPO_updates=67,new_environment_transitions=32160000,saved_iteration=32133,Adam=644180),
 W35_next='Prepare frozen218 W35-only original one-hour join; no production before original210 E0 closing+NEWformalCPU+freshCNone. Do not hotadd to210 or create another writer.',
 old_experts213='Frozen source+CPU, not actual E2/E3 full-skill acceptance or complete SuperMimic conversion',
 protected_old_tags_before_actual210_archive=1503)
put(R/'CURRENT_ACTUAL210_E0_CONTINUES_AND217_20K_MATERIAL_REPAIR_PASS_V3.json',current)
old_request=read(R/'AUTOMATION210_ACTUAL216_W35_FAILED_E0_CONTINUES_UPDATE_REQUEST_V2.json')
with(R/'PREVIOUS_AUTOMATION210_V2_BEFORE_ACTUAL217_HISTORICAL.txt').open('x',encoding='utf8')as f:f.write(old_request['prompt'])
prompt='''CURRENT_ACTUAL210_E0_THREE_HOUR_CONTINUES_AND217_FULL20K_SHARED_MATERIAL_REPAIR_PASSED_20261101。覆盖W35仍卡死/214未冻结/217未执行/两路均学习的话。当前E0三小时是唯一实际学习，W35原启动失败0PPO且已按人类仅该PID授权退出，修复的20k实际准入已经通过。原mod4-10 ACTIVE/hourly/原聊天01a07a2d-9036-7531-a012-692df9f56353，不新Goal/create/resume/automation。实际files/refs/HEAD/index/toolreceipts优先，任何consumed once永不重放。健康/未到正常采集窗口安静，只通知有意义完成/修复/失败/资源预算网络或必需人类行动。
FIRST READ N/reports/CURRENT_ACTUAL210_E0_CONTINUES_AND217_20K_MATERIAL_REPAIR_PASS_V3.json、KNOWN_ACTIVE210_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json，Q/reports/ROOT217_ORIGINAL_20K_SHARED_MATERIAL_NATIVE_OR_ERROR_RETURNED_ACTUAL.json 与 ROOT217_ACTUAL_CAPACITY_PASS_AND_READER_CAPTURE_SCOPE.json。N=T/E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031；Q=T/W35_SHARED_MATERIAL_20K_ORIGINAL_PHYSX_ADMISSION_V217_20261101；T=C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021。原此前完整prompt在N/reports/PREVIOUS_AUTOMATION210_V2_BEFORE_ACTUAL217_HISTORICAL.txt，只历史，不是旧once执行指令。

210 run PARALLEL210_E0_3H_RM70_1H_1793463669094560900，唯一原owner72 PID990302/create1793463861.26，cwd=/home/lc01/Zonglin Li/zonglin2，与taskroot不同；ownerroot=/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_PARALLEL210_E0_3H_RM70_1H_2611v210/owner。E0 node990312/create1793463861.67、worker990337/create1793463867.96，GPU-16828f91-2b45-b646-8dc0-9481138e2842，精确exe/fullargv/cwd在原FIRST/owner回执，不能猜。job=/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_JUMP32066_GROUND10_THREE_HOUR_20261031v210/e0_72，control210v2。FIRST已实际新1PPO/480000own transitions/iteration32067/17Adam642860，完整first22961801B SHAd1807cb26361d9741b7c281705c4fb4598dbdf7e9dec4ae24c53b39ab11a6c72。另一次必要材质对照小JSON在01:12:38.65BJT记录新增67PPO/32160000transitions/iteration32133/17Adam644180，完整22962066B SHA0d82b616e45b1b90408fc2726af2e83698f93aef7bbb9f228f064a60bc3c8151。只是当时保存快照，不持续存活/FINAL/跳跃技能，不重复读取状态或PT为统计。root控制SSH已finallyclosed/SESSIONrestored/globalclientleaseFREE；保留健康E0，无startup空GPU复查/第二watcher/热改/停止。
E0原输入2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610/17519967B/32066/17Adam642840，原冻结E0_82 a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a/14031973B/31984/641200原件不改。原actor35/critic38/STD6/17Adam/LR完整接续，采样CPU/CUDARNG恢复；物理/DR/episode/queue历史fresh，不假PhysX精确续态。输入必要GPU1读解码已消费，旧模型/旧raw/normal86禁止为统计/Git重读。
人类“要训一口气训3个小时”：GO2026-11-01T00:24:25.233659+08，SAVE03:24:25.233659，NOMINAL03:29:25.233659，max11100/save10800/exit300，原raw收费不改，无新grant。NEXT ONLY N/collect210_original_two_role_formals_cost_normal900_UNUSED_once.py，FROZEN UNUSED，合并正常最早03:14:25.233659+08，原LOCAL AND REMOTE signed latest nominal-now<=900；freshLOCAL exactCIM+globalcontrolleaseFREE，原owner850/node180不改。COHORT_FINAL/OWNER_EXIT/NODE_EXIT/allownwaitout/已知原PID退出或原Z非执行/privateEX+两sharedfree/freshCNone/唯一原ownersegment精确两GO后，原各独立rawfees SUMONCE。W35本role -9/0PPO不qualified，不伪造formal；仅qualified E0允许1NEWformal传输/两hostSHA。完整JSONguard后review210_TWO_NEW_formals_initial_whole_CPU_UNUSED_once.py：CPU脚本内CUDA_VISIBLE_DEVICES=''，每NEWformal读解码1，旧E0/W35/native/normal86全0；finite35/38/6/STD/17Adam=642840+20updates/iter32066+updates、完整targetDR+原JUMPmemory+mixed persistent2000ground mask与typed task。partial/FAIL不晋升，finalsaveepoch对照原deadline才称三小时完成。普通PPO一optimizer，不套native3opts或把20Adam步称20nativeiter。

2000ground/18000JUMP disjoint env；ground使用原E0 reward和DirectionalSpinCommand，JUMP pinned commit8204e853dfd2ed06d85a322e1a998c3d20a3be2c原19方法/完整config16weights逐字相同，clip_single2.5*dt/无total正裁剪/current+previous接触/base_air_time跨reset记忆原样；self.dt.02且只抵消Lab额外dt。原JUMP vx±2.1/yaw±2/height.12..15/20s，平面μ/rest.5/.5。persistentmode0ground/mode1JUMP，不混reward项、不teacher动作、脚本起跳/强制零yaw/新成功项。原6actions clip6/PD/扭矩转速/延迟/400N名义工程k2000/D0white_v3D1-D7/50policy100feedback400physics2.5msTGS32/4F32/perenv2mm/mimic.01不改。根height/contactrelease/奖励/首次更新不是跳跃/270技能。

W35原role worker990366/create1793463868.49，c27卡，setup实际PhysX PxPhysics::createMaterial 64K上限，未fullrestore/native24/FIRST/PPO。原STOP_AFTER_SAVE+一次SIGINT无效；人类明确“授权只终止W35故障进程”，216严格原PID/create/exe/argv/cwd及owner/go后TERM→必要KILL，仅该原PID；原post-signal identity reader RC1保留，独立readonly续收证明原workerOUT、原node wait=-9/NODE_EXIT/allwaited/privateEXfree/ownerACK。许可已消费，不是任意未来worker kill许可。无正常SDK App.close声明，无W35partial权重晋升，原费由原owner自然记录，normal时SUMONCE，不退款/补款/idlefee/重算。E0未signal或改动。
214已FROZEN INDEX8a27849574f33e5d7e0c619526ddfead25ac57c54bede975315082e2a25ce171。修复仅几何引用从每env完整/Asset改原/Asset/mesh prototype并单共享原/Asset/physics_material；完整CAD点面/70mm峰谷/周期240.641934mm/全长2.406423m/宽2.0845m/1.5deg和D0原33μ桶采样/RNG不改。不是±70，不是35mm。原CAD摩擦实际static.9/dynamic.8/rest0，actual绑定不能猜。原E0和W35 mild_dr字节相同且E0已持续更新/重置，不能称μsampler本身唯一原因。
217实际CONSUMED/RC0：20,000原ownMOD4构造→freshreset→自身20k D0参数/原D1-D7physicalsetter restore→一次原new_episode reset→8controls/64physics16feedback/queue64each，0PT/NN/optimizer/account写。3次实际material setter的前后marker、9次actual USD boundmaterial检查齐，唯一原CAD共享material(.9,.8,0)，已知64K错误0；原所有termination0/closuremax.00154438/mimicmax.00154408。约551s返回，原parentwait0/SDKfinally/allchildrenout/privateEXreleased，SSHfinallyclosed/sessionrestored/FREE。Stageprim/valuecounts不是PhysXhandlecounts；handle数仍UNKNOWN。原preexec身份bash保留，不伪造Pythonexe。V1相对CLI导致LOCAL绝对CIM比对拒绝在marker/network前，原false保留；V2新CIM报告+绝对CLI，同一尚未消费目的实际执行。217所有目的已消费，不重跑为stats/Git。源fullstate/native24/PPO FIRST以及完整RM70技能仍待下一学习回执，不能把0PT当训练毕业。父reader1次phase metadata数值parse+另1次全文保留，实际metadata2opens已澄清，轨迹raw0。新生成USD只metadata入Git，原全文local保留。
同一用户授权child/root/w35_rm70_expert_normalization208正在新218仅LOCAL源和CPU准备下一W35-only一小时原solewriter合同；只有冻结INDEX后可选，不新/nested helper/Astra/Sol。输入仍ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f/17619013B/32336/17Adam648360/LR.00011390625；生产用原mild_dr，探针observer/额外材料重放不进生产。217真实PASS可复用；但新W35学习必须等210 E0原normal完全closed+qualified新CPU+freshCNone，原TaskGO/readback/资源/唯一writer仍须ROOT执行。不能hotadd当前210或建第二writer。源CPU/准备不能称新Pi，旧W35原件不覆盖。
213旧专家归一化source已FROZEN54ca90c1a4970d9fe137a12b5435c46585b6524d3b97089d33fd1b14c4a37690/39files；LOCAL3groups/12saved-schema joins/4reject PASS，模型rawNPZSDKGPUremote0。E2新1200controls24s/20k/1680worker完整sameUID along/cross/signedyaw/pre-reset入口仍source-only，实际targetmetadata/newtypedcaller待ROOT；原900目的已消费不复读。E3 V14只是unusedmetadata组件，不假runtime ready；完整E2/E3技能未毕业。190仅WM50 synthetic组件，不是全部老专家SuperMimic化。W35旧5039JSONL onepass已消费，1229cycle/116沿向超线/crossyaw UNKNOWN不复读。继续授权背景任务，资源只给实际ready工作，不padding。

一个GLOBALserial控制SSH72/210/86/249，每newfinite freshLOCAL exactCIM basename/fullpath/exe/fullargv/create；finite客户端活着ROOT只localreports/CIM/同handle，可独立LOCALCPU；无第二watcher/机械5minpoll/未知PID或GPU-PID扫描/kill/删lock/第三方干预/GUI重启/本地3060神经CUDA/Luna/OpenRouter。startupfree>15669MiB/util<=30允许nonemptycomputeUUID/RAM32GiB/disk25GiB；健康job不复查startupfree，runtime8GiB为保存磁盘guard。复用native160k/旧1µm特定查询，不增FP64/bitwise/三角门禁。MATLAB71796保留/GetActiveObjectonly，非主线。无外力/root/速度注入/fakeairreset/foreignplant作owntruth/guard放松。新GUI须新实际用途，旧205/193不是live，不自动reopen/query/kill，PPO不凭空造蓝WM。
唯一canonical72=/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json，generationMOD4_SINGLE_WRITER72_20261026/modefinite_original_limits_restored_after_single4090_return/authorized2268000/9historical/extensions[]/reserve86412.86069250107。原twofcntl/HMACbody/charge_values不改，原actualGO→terminal raw费用独立SUMONCE；不refund/recharge/clamp/round/idlefee/grant/secondwriter/canonicalcopy/clearactive。当前仍原210 owner exactrun/go active；未来remote fresh72 exact3fields，关闭后binding历史化，不假CNone或旧ACTIVE。CLOSE72后才210/86；旧210canonical永远retired。72pin301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795/ownerloopback29754；210严格egde@10.24.5.27:4090→inner22原pin/durableUUID EF3105C85DD986BD新存储先freshUUID-rw；86robemo10.50.0.86/pin8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b仅/data/robemo/polar-rl-train；249仅display原pin95b8067b17fc5331aac5e2d46acd6a087c46719dc853658b14bfa0e29e69242e。Secrets memory/noechoSTDIN/memfd，不argv/env/disk/Git；noapt/sudo/globalpip/driver/profile/DNS。
Git AGENTS/ALL_TRIALS适用，actualHEAD/refs/tool/CAPTURE_INDEX优先，1503旧tagobjects/peels保护。actual210新Pi唯一phase mod4-e0-jump32066-ground10-three-hour-and-full-rm70-ppo210，用record_experiment一次；任何该tag存在即CONSUMED不重record/retag，pushfailure续原objects。首档日期实际Nov1不回填Oct31；标题E0实际学习+W35原启动失败，不称两路都新PPO。收208-217全部frozen source/CPU/原V1V2错误/2090PT/210混合3h/原Windows路径fixturefalse修复/两role FIRST/211212实际0PT/213214frozen/215无效正常停止/216人类授权精确退出+readerfalse/217实际PASS及全部UTF8/CIM/lease/本app回执；218active排除直到INDEX。binary/PT/rawJSONL/NPZ/USD/STL/media仅真实pathbytes现有producerSHA/unknown，无FORGit内容/hash/model/hostGPU。新生成USD若嵌在原report，Git版本做明确metadata-only投影并记录原SHA/归档SHA，local原报告保留。210normal关闭/费用/NEWformalCPU与以后新source普通append不重tag；postGit只工具核验/对话，不追HEAD造报告。最终真实双轮腾空越270/完整台面接触12/稳定200physicscallbacks=.5s仍未达到。
'''
request=dict(old_request,prompt=prompt)
put(R/'AUTOMATION210_ACTUAL217_FULL20K_REPAIR_PASS_UPDATE_REQUEST_V3.json',request)
print(json.dumps(dict(passed=True,local_reports_only=True,actual217_passed=True,E0_original_three_hour_window_unchanged=True,automation_request_written=True)))
