"""Publish original returned FIRST receipts; no remote/model/GPU observation."""
from pathlib import Path
import hashlib,json,time,tomllib,datetime
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def read(p):return json.loads(p.read_bytes())
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def local(epoch):return datetime.datetime.fromtimestamp(epoch,datetime.timezone(datetime.timedelta(hours=8))).isoformat()
launch=read(R/'ROOT210_ORIGINAL_UNIFIED_OWNER_LAUNCH_ACTUAL.json');state=read(R/'ROOT210_UNIFIED_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json')
closed=read(R/'ROOT210_PARALLEL_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json');assert closed['global_serial_control_client_lease']=='FREE'
go=state['current']['go'];specs=launch['specs'];firsts={};statuses={}
for key in specs:
 p=R/('ROOT210_'+key.upper()+'_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json');firsts[key]=read(p)
 statuses[key]='ACTUAL_FIRST_PPO_PASS' if firsts[key]['passed'] else 'NO_FIRST_PASS_IN_RETURNED_ORIGINAL_WAIT_CHECK_CAPTURED_ERROR_OR_STARTUP'
assert firsts['e0_72']['passed'],'No E0 training claim without actual update'
timing={k:dict(GO=local(v['learning_started_epoch']),save=local(v['save_deadline']),nominal=local(v['nominal_end_epoch']),max_parent=v['max_parent_seconds']) for k,v in go.items()}
earliest=max(v['nominal_end_epoch'] for v in go.values())-900
binding=dict(epoch=time.time(),run_id=launch['run_id'],owner=launch['owner'],go=go,canonical_generation='MOD4_SINGLE_WRITER72_20261026',
 scope='Exact current owner/run/GO required for any new serial control; not permanent active claim',
 after_close='Historical only; fresh canonicalNone or actual new owner required')
put('KNOWN_ACTIVE210_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json',binding)
work=dict(epoch=time.time(),run_id=launch['run_id'],statuses=statuses,firsts={k:v.get('first') for k,v in firsts.items()},GO=go,timing=timing,
 latest_normal900_earliest=local(earliest),canonical_after_original_FIRST=state['current_owner_matched'],
 one_original_owner=True,all_control_SSH_closed=True,global_control_lease='FREE',
 E0=dict(source_iteration=32066,source_SHA=specs['e0_72']['source_SHA'],ground_envs=2000,jump_envs=18000,requested_learning_window_seconds=10800,
  original_frozen_E0_preserved=True,full_actor_critic_STD17Adam_restored=True,physics_DR_and_command_episodes_fresh=True,
  original_Fudan19methods16weights_unchanged=True,flat_original_E0_reward_and_command_disjoint=True),
 W35=dict(source_iteration=32336,source_SHA=specs['w35_72']['source_SHA'],selected_geometry='originalCAD complete RM70 peak-to-trough70mm/1.5deg, not±70/not35',
  actual_scene211_passed=True,actual_own_robot212_zeroPT_passed=True,actual_first_PPO=firsts['w35_72']['passed'],full_RM70_skill=False,complete_SuperMimic_conversion=False),
 normal_collector='collect210_original_two_role_formals_cost_normal900_UNUSED_once.py',normal_collector_status='FROZEN_UNUSED',
 subsequent_NEW_CPU='review210_TWO_NEW_formals_initial_whole_CPU_UNUSED_once.py',subsequent_NEW_CPU_status='FROZEN_UNUSED',
 source_inputs_or_raw_read_for_this_publish=0,skill_success_not_inferred=True)
put('CURRENT_ACTUAL210_E0_THREE_HOUR_FULL_RM70_TWO_ROLE_FIRST_AND_NORMAL_WORK_ORDER.json',work)
old=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
put('PREVIOUS_AUTOMATION_BEFORE210_HISTORICAL_ONLY.json',dict(prompt=old['prompt'],status=old.get('status'),rrule=old.get('rrule'),targetThreadId=old.get('targetThreadId')))
prompt=f'''当前唯一实际主线是210原sole72writer静态两角色：E0最新32066支线保留10%原E0平地/90%逐字原FudanJUMP，按人类“要训一口气训3个小时”；另卡W35接原CAD全RM70一小时。原mod4-10 ACTIVE/hourly/原聊天01a07a2d-9036-7531-a012-692df9f56353；禁止新Goal/automation。实际文件/refs/index/receipts优先，once消费不重放。健康/未到正常窗口保持安静，有意义完成/失败/材料修复/资源预算网络/必要人类行动才通知。
FIRST READ {R/'CURRENT_ACTUAL210_E0_THREE_HOUR_FULL_RM70_TWO_ROLE_FIRST_AND_NORMAL_WORK_ORDER.json'}、KNOWN_ACTIVE210_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json、ROOT210_E0_72_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json、ROOT210_W35_72_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json、ROOT210_UNIFIED_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json。N={N}。旧完整prompt在PREVIOUS_AUTOMATION_BEFORE210_HISTORICAL_ONLY.json，只历史不旧once重跑。
实际run {launch['run_id']}；sole owner72 PID{launch['owner']['pid']}/create{launch['owner']['creation']}，cwd=/home/lc01/Zonglin Li/zonglin2、任务root独立，原glibc240/exe/fullargv见回执。两个真实roles实际FIRST状态={statuses}。每PASS首次20k*24=480000own transitions，新checkpoint全actor35/critic38/STD6/17Adam/DR；FIRST仅快照，不是持续存活/FINAL/技能成功。输入E0 branch32066 SHA2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610/17519967B/17Adam642840；原冻结E0 a92c…74a从未写；E0FIRST PASS32067/642860。W35输入ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f/17619013B/32336/648360，旧正式源不覆盖。源PT新必要读取/解码目的及W35单次stream-copy已消费；不为统计/Git重读。
时间以签发GO为准：{timing}；合并正常最早{local(earliest)}。E0max11100/save10800/exit300，W35max3900/save3600/exit300，原raw费用实际GO→terminal各自SUMONCE，不退款/补款/round/clamp/idle费/新grant/第二writer/复制canonical/清active。时间不等于完成。保留健康E0三小时，不hotpatch/热加role/改reward/重启/复查startupfree/第二watcher。W35若原FIRST未PASS，先读已保存原错误/完整stdout及原节点状态，不称已学习；不得盲目重跑launcher或第二writer。修复须独立新冻结必要目的，现owner健康任务不干预。
NEXT ONLY N/collect210_original_two_role_formals_cost_normal900_UNUSED_once.py，冻结未用，freshLOCAL exactCIM/globalserialleaseFREE且原签名LOCAL AND REMOTE latest nominal-now<=900；owner850/node180原等待不改。原COHORT_FINAL/OWNER_EXIT/NODE_EXIT/allownwaitout/原PID退出或原Z非执行/two-shared+privateEXfree/freshCNone/唯一owner段匹配两GO后，原独立rawfees SUMONCE，仅每qualified角色1NEWformal传输/两hostSHA。完整JSONguard后才review210_TWO_NEW_formals_initial_whole_CPU_UNUSED_once.py，脚本内CUDA_VISIBLE_DEVICES=''，每NEWformal1读/解码，旧E0/W35/native/normal86全0。严格finite35/38/6/STD/17Adam=输入+20updates/iter输入+updates，E0完整targetDR+JUMPmemory+混合任务state，W35完整D0-D7与新RM70课目字段。partial/FAIL不晋升；最终saveepoch对照deadline才可称原时长完成。
E0两任务不混reward公式：jump原commit8204e853dfd2ed06d85a322e1a998c3d20a3be2c原19方法/配置16weights/clip2.5*dt无total正裁剪/current+previous接触/base_air_time跨reset记忆原样；ground原E0 reward+DirectionalSpinCommand standing/正反/纯转/世界进度，persistent mode0；JUMPmode1。共用原Fudanplane μ/rest.5/.5，原jump vx±2.1/yaw±2/height.12..15/20s，不强制零yaw、不teacher动作、不脚本起跳。10%是root落实少量平地的明确默认。400N工程k2000/50policy100feedback400physics2.5msTGS32/4F32/6actionclip6PD延迟/D0white_v3D1-D7/perenv2mm/mimic.01保持。新mixed episodes/DR/physics/queue明确fresh，不称PhysX精确续态。
W35全RM70新独立课目用原arena_collision.usdc SHA9f05b0cae71752f36ba95465ed6723f96321c1fd2262bb1e2d0f363c8266397b/NPZf79dae96a377992da9901979429db4a2e1af050399091f721d75a576f5b3e954，原70mm峰谷/周期240.641934mm/全长2.406423m/宽2.0845m/1.5deg。211原8arena场景0PT+212真正ownMOD480env/8controls64physics16feedback/queue64each/Rewarddt.02实际PASS，均已消费，不是20k fullrestore/native24或完整技能。208V1错误WXYZ/emptycompute/重复PT/旧CLI均保留，V3xyzw/精确源cache1读解码/完整parentFIRST-FINAL已冻结。W35完整技能和SuperMimic转换仍未完成，20k actualfullstate/native24由新生产回执判，不源代码冒充。历史W35旧5039JSONL一次读取已消费，1229cycle/116原along超线/crossyaw UNKNOWN不再读。
一个已授权子代理/root/w35_rm70_expert_normalization208继续213仅LOCAL source/小报告CPU准备E2/E3旧专家归一化/完整技能入口/SuperMimic数据接口；无SSH/SDK/GPU/PT/raw/NPZ/Git权。无新/嵌套agent，无Astra/Sol额度。老E2/E3均未完整技能毕业；190 WM50只有synthetic组件，不是实际全native转换。213未冻结部分排除直到INDEX。原W35/E0/E2E3冻结模型保留，后台不能热加当前owner或第二writer。
一个GLOBAL serial控制SSH72/210/86/249；每newfinite fresh LOCAL exactCIM basename/fullpath/exe/fullargv/create。finite客户端活着ROOT只localreports/CIM/同handle，独立LOCALCPU可；无第二watcher/机械5minpoll/未知PID或GPU-PID扫描/kill/删lock/第三方干预/GUI重启/本地3060神经CUDA/Luna/OpenRouter。startupfree>15669MiB/util<=30允许nonemptycomputeUUID/RAM32GiB/disk25GiB；健康job不复查startupfree，runtime8GiB为保存磁盘guard。复用native160k/旧1µm指定查询，不新增FP64/bitwise/三角门禁。MATLAB71796保持GetActiveObjectonly，非主线。无root/速度/力注入、fakeairreset、foreignplant作owntruth或guard放松。
唯一canonical72=/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json，generationMOD4_SINGLE_WRITER72_20261026/modefinite_original_limits_restored_after_single4090_return/authorized2268000/9historical/extensions[]/reserve86412.86069250107，原twofcntl/HMACbody/charge_values不改。未来remote须fresh当前owner/run/go exact匹配，210关闭后binding历史化；CLOSE72后才210/86。旧210canonical永久retired。72pin301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795/loopback29754；210严格egde@10.24.5.27:4090→inner22原pin/durableUUID EF3105C85DD986BD新存储先freshUUID-rw；86robemo10.50.0.86 pin8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b仅/data/robemo/polar-rl-train；249displayonly原pin95b8067b17fc5331aac5e2d46acd6a087c46719dc853658b14bfa0e29e69242e。Secrets memory/noechoSTDIN/memfd only，无argv/env/disk/Git；noapt/sudo/globalpip/driver/profile/DNS。
Git actualHEAD/refs/index最优先；1503旧tags objects/peels保护。207phase已消费main87c899532aff2c87f6b340cc75b3ddb409fb8bac，201/203/205/206/207所有once已消费。210实际新Pi唯一phase mod4-e0-jump32066-ground10-three-hour-and-full-rm70-ppo210，任何相应tag已存在即消费，不重record/retag，pushfailure续既有objects。收208全部source/原V1V2误源/V3/CPU/实际211212/209五组+原0PT/210原1h未用转3h/Windows路径fixture false修复/两role原完整FIRST/所有完整UTF8/各CIM/lease/本monitor；旧模型/raw/NPZ/USD/media只真实pathbytes producerSHA/unknown，不FORGit读hash模型raw/hostGPU。当前未冻结213排除。后续FINAL/fees/formalCPU普通append不重tag；PostGit仅tool核验/对话不追HEAD造报告。双轮真腾空越270/完整台面接触12/稳定200physics=.5s仍未达到；RM70完整技能/全部老专家SuperMimic化也未完成。'''
request=dict(mode='update',id='mod4-10',kind='heartbeat',name=old.get('name','MOD4计划与双机并行巡检'),prompt=prompt,
 status=old.get('status','ACTIVE'),rrule=old.get('rrule','FREQ=HOURLY;INTERVAL=1'),targetThreadId=old.get('targetThreadId','01a07a2d-9036-7531-a012-692df9f56353'))
put('AUTOMATION210_ACTUAL_FIRST_THREE_HOUR_AND_RM70_UPDATE_REQUEST.json',request)
put('CAPTURE210_FROZEN_ACTUAL_FIRST_SCOPE.json',dict(epoch=time.time(),roots=[str(T/name) for name in (
 'W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031','E0_JUMP32066_GROUND_RETENTION_CONTINUATION_V209_20261031',N.name,
 'W35_RM70_ORIGINAL_CAD_SCENE_ADMISSION_V211_20261101','W35_RM70_OWN_MOD4_ROBOT_ADMISSION_V212_20261101')],
 active213_excluded_until_frozen=True,models_raw_assets_metadata_only=True,first_statuses=statuses,original_errors_preserved=True))
print(json.dumps(dict(passed=True,statuses=statuses,timing=timing,normal_earliest=local(earliest)),ensure_ascii=False))
