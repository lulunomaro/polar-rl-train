from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
def bjt(t):return datetime.fromtimestamp(t,timezone(timedelta(hours=8))).isoformat()
first=read(R/'ROOT194_FIRSTV2_ACTUAL_NEW_PPO_OR_ORIGINAL_ERROR_RETURNED.json');assert first['passed']
launch=read(R/'ROOT194_FIRSTV2_ORIGINAL72_OWNER_LAUNCH_ACTUAL.json');state=read(R/'ROOT194_FIRSTV2_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST.json')
assert state['owner_matches_original_canonical']
go=state['owner_current']['go'];g=go['h1_210']
assert g['max_parent_seconds']==7500 and g['save_deadline']-g['learning_started_epoch']==7200
values={Path(x['path']).name:json.loads(x['UTF8']) for x in first['full_selected_UTF8'] if x['path'].endswith('.json')}
worker=values['WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json'];restore=values['ACTUAL194_CUDA_FULLSTATE_RESTORE_BEFORE_NEW_CONTROL.json']
assert restore['passed'] and first['first']['new_Adam_step']==100040
binding=dict(owner=launch['owner'],run_id=launch['run_id'],go=go)
put('KNOWN_ACTIVE194_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json',binding)
work=dict(epoch=time.time(),status='ACTUAL194_ONE_FORWARDED4090_LITERAL_JUMP_PLANE_TWO_HOUR_FIRST_PASSED_NOT_FINAL',
 human=['先按照复旦的奖励训平地跳跃适应dr和400n 50hz 先训2个小时','复旦的跳跃别乱改瞎适配'],
 current_main='JUMP16 plane adaptation, not STAIRS3/native/MATLAB/LQR',run_id=launch['run_id'],owner=launch['owner'],worker=worker,
 source_model_SHA=g['source_SHA'],source_iteration=4999,source_byte_reads_GPU_decodes=1,
 original19methods_and_reward_config_text_identity=True,source_CPU_groups=5,TaskGO_controller_negative_cases=18,
 target64_0PT=dict(controls=8,physics=64,feedback=16,actual_returncode=0,App_closed=True,private_EX_released=True),
 actual_first=first['first'],restore=restore,first_progress_snapshot_only=values.get('LATEST_PROGRESS.json'),
 go=g,timing_BJT=dict(GO=bjt(g['learning_started_epoch']),normal_earliest=bjt(g['nominal_end_epoch']-900),save=bjt(g['save_deadline']),nominal_exit=bjt(g['nominal_end_epoch'])),
 two_hour_duration_explicit_latest_human_authority=True,canonical_budget_grant_or_copy_or_refund=False,
 learning_snapshot_not_continuous_liveness_or_skill=True,
 original_reward16_unchanged=dict(methods=str(N/'train_package/literal_original_methods.py'),config=str(N/'train_package/literal_original_config.py'),clip_single=2.5,total_positive_clip=False,dt_once=True,original_flight_contact_history_retained_across_reset=True),
 outside_reward_mapping=dict(own_MOD4_hip_anchor_to_wheel_axis_FK=True,actual31body_contact_forces=True,approximate_SDK_applied_motor_effort_not_hardware=True,original_body_FD_linear_velocity=True,actualWORLD_vz=True,MOD4_safety_terminations_unchanged=True),
 before_action_report_legacy_filename='ACTUAL_SOURCE188_LITERAL_REWARD_AND_TARGET_PLANT_BEFORE_ACTION.json; not included in FIRST selection because legacy name. Normal full UTF8 collector will retain it. No extra watcher or download.',
 physical_clock='400Hz2.5msTGS32/4F32,50Hzpolicy,100Hzfeedback,6actionclip6,2mmperenv,mimic.01,400Nengineeringk2000D0-D7',
 no_new_budget_or_second_writer=True,latest_qualified_formal_still188_until194_normal_and_initialCPU_pass=True,
 next_only=dict(normal='collect194_original_formal_cost_normal900_UNUSED_once.py',initialCPU='review194_NEW_formal_initial_CPU_UNUSED_once.py',state='FROZEN_UNUSED',no_early_transfer_or_model_read=True),
 no_current_complete270_jump_stable_skill=True)
put('CURRENT_ACTUAL194_LITERAL_JUMP_PLANE_400N50_DR_TWO_HOUR_FIRST_AND_NORMAL_WORK_ORDER.json',work)
put('CAPTURE_ACTUAL194_FIRST_AND_CLOSED188_191_193_FROZEN_SCOPE.json',dict(epoch=time.time(),
 included=[str(N),str(T/'FUDAN_STAIRS3_LITERAL_REWARD_TERRAIN_400N50_ADAPT_V188_20261031'),str(T/'STAIRS188_QUALIFIED_FORMAL_TRUE270_ACCEPTANCE_V191_20261031'),str(T/'STAIRS188_ORIGINAL_COURSE_USER_MUJOCO_V193_20261031')],
 explicit_pending=[dict(path=str(T/'EXPERTS_RM70_SUPERMIMIC_READY_QUEUE_V190_20261031'),reason='Incomplete/unfrozen WM50 component, no SDK/admission/GO'),dict(scope='193 viewer future log/exit and194 future normal/formal/fees/initialCPU',reason='later ordinary append')],no_model_raw_binary_or_host_GPU_reads_for_Git=True,
 prior189_tag_consumed=True,prior188_tag_consumed=True))
actual=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
put('PREVIOUS_AUTOMATION189_BEFORE_ACTUAL194_HISTORICAL_ONLY.json',{k:v for k,v in actual.items() if isinstance(v,(str,int,float,bool,list,dict))})
prompt=f'''当前主线已实际切换到194：人类要求“先按照复旦的奖励训平地跳跃适应dr和400n50hz先训2个小时”，并再次明确“复旦的跳跃别乱改瞎适配”。这覆盖188台阶续训/192待建/无新训练的旧文字。现有mod4-10保持ACTIVE、每小时、原聊天01a07a2d-9036-7531-a012-692df9f56353；不新建或恢复Goal，不另建automation。实际文件、HEAD/ref/index/toolreceipt优先，已消费once不重放。

首先读 {N.as_posix()}/reports/CURRENT_ACTUAL194_LITERAL_JUMP_PLANE_400N50_DR_TWO_HOUR_FIRST_AND_NORMAL_WORK_ORDER.json、KNOWN_ACTIVE194_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json、ROOT194_FIRSTV2_ACTUAL_NEW_PPO_OR_ORIGINAL_ERROR_RETURNED.json。N194={N.as_posix()}。只通知有意义完成、修复、失败、资源/预算/网络问题或必须用户行动；健康与未到正常采集窗口保持安静。

实际194 run={launch['run_id']}，原端口转发egde@10.24.5.27:4090 inner22/GPU937bdb0b。owner72={launch['owner']['pid']}/{launch['owner']['creation']}，worker210={worker['pid']}/{worker['creation']}；准确exe/fullargv/cwd在原FIRST。owner cwd=/home/lc01/Zonglin Li/zonglin2，与任务根不同。20,000环境、24controls实际FIRST已新增1PPO更新/480,000own transitions，iteration5000，17Adam100020→100040，fullactor35/critic38/learnedSTD/optimizer/新DR检查点17518367B SHA2737183fa83f41d018bcee6a06d62fb4370f04657179c382550bab8b1245f425。已恢复另一AI交付4999的完整PPO；sourceSHA5932295297ed93b65fd88fe142d6fc66099c0a936f23091a79a3b2752c51dfa4，GPU单读/解码已消费，不能为统计/Git重读。新DR/物理/queue历史明确fresh，不假称原4999已有DR或PhysX精确续态。当前FIRST是快照，不是连续存活、FINAL或跳跃成功。保留健康训练，不热改/重启/增加startup空GPU检查/第二watcher。

奖励为commit8204e853dfd2ed06d85a322e1a998c3d20a3be2c的jump原19方法、完整rewards配置及16权重原文逐字一致；不是上台阶3，不是native改写奖励。原clip_single=2.5、无total正裁剪、原check_jump/current+previous接触/原base_air_time和跨reset记忆不改。50Hz下原self.dt=.02且外层仅抵消Lab额外dt。原平面μ/rest.5/.5，原20s重采样vx±2.1/yaw±2/height.12..15；不凭空加零yaw、脚本起跳、成功加分或改目标常数。MOD4外层只绑定真实hip锚点到轮轴BODY的L0/theta、31body接触、SDK实际WORLD vz/BODY位置差分速度、近似applied motor effort（不是测得物理扭矩）；外国机器人几何/actor/原终止不冒充MOD4。保留own400N工程k2000、D0white_v3/D1-D7、50Hzpolicy/100Hzfeedback/400Hzphysics2.5msTGS32/4F32、6actionclip6/PD/延迟/每env2mm/mimic.01。跳起后bad_orientation/closure仍按原MOD4重置，不为制造成功放宽。

新sourceCPU5组PASS/19方法+完整config文字一致，18TaskGO/controller负例PASS，实际64env0PT8controls64physics16feedback8rewardcalls/RC0/Appclosed/EX释放均已消费。实际20kCUDAfullrestore/FIRST已消费。原before-action报告残留ACTUAL_SOURCE188...文件名，FIRST选择器未采集它；正常全UTF8会收，禁止为此第二watcher或补读model。

两小时由本次人类明确授权：GO={bjt(g['learning_started_epoch'])}；SAVE={bjt(g['save_deadline'])}；NOMINAL={bjt(g['nominal_end_epoch'])}；正常采集最早={bjt(g['nominal_end_epoch']-900)}。max7500/save7200/exit300；只调整本任务时限，原预算/两fcntl/HMAC/原raw收费函数均不变，没有新grant。时间不是完成。NEXT ONLY N194/collect194_original_formal_cost_normal900_UNUSED_once.py，冻结未用，freshLOCALexactCIM/global控制leaseFREE，原签名local AND remote nominal-now<=900，原owner850/node180等待不改。实际COHORT_FINAL/OWNER_EXIT/NODE_EXIT/原wait-out/CNone/private-sharedfree/唯一原owner段精确GO后，只原一笔rawfee SUMONCE、1NEWformal传输/两hostSHA。完整JSONguard通过后才N194/review194_NEW_formal_initial_CPU_UNUSED_once.py：脚本内CUDA_VISIBLE_DEVICES=''，1NEWformal读解码、旧4999/native/normal86均0，finiteactor35/critic38/STD6/17Adam=100020+20updates/iter4999+updates/DR+original_jump_reward_memory/typed_JUMP194_task。失败/partial不晋升。原188/191/193所有once均已消费，不重跑。

188已完全CLOSED+新formalCPU PASS，66updates/iter5065/17Adam101340/31680000transitions，正式SHA bdd85c72b1b20c729333879e56e941b9ecc5e2d886ead345dcaf3c6bf9cd6f1d，原费3671.391360282898 SUMONCE，closing440282.41543221474仅历史快照。191新32首回合270验收0越沿/落台/稳定；最高共同轮底.270573m但无越沿且closure终止，不是技能。191V1Kit目录拒绝preApp/model已保留，V2仅路径修复后实际closed/SSHfree。193新原上台阶3录像273controls2184physics5.46s仅bad_orientation；用户看到了转圈/跳后结束，不能声称已修好。非零yaw原指令不能证明唯一原因。GUIV1语法错误pre-read保留，V2 PID65168真277mesh/31body/真实PhysX+原课程已原生视觉核验，保留用户窗口/2hbound/noautoquery-reopen-kill；它是closed188/new193eval，不是当前194live，不给PPO造蓝WM。显示数据一次读已消费，不为统计/Git重开NPZ。

后台老专家归一化完整技能验收/SuperMimic化、RM70全起伏/E2/E3补齐授权持续。189 E0新CPU端口7组+10拒绝、collector2+7已完成，不是GPU转化。W35原5039行one-pass已消费，1229完整cycle MAE.02172158885，116超过原沿向.05，缺cross/yaw字段故完整验收UNKNOWN；不能再读JSONL。W35仅35mm，不是fullRM70。全RM应按原CAD70mm峰谷/周期240.641934mm/全段2.406423m/宽2.0845m及坡1.5deg，不是±70；E2/E3仍未完整毕业。190只有不完整WM50warm源，未冻结/无caller/SDK/GO，不冒称SuperMimic开训。可在194运行中补齐独立LOCALCPU来源/准备，禁止hotadd现owner或第二writer；有实际ready任务再统一调度，不能为占卡padding。所有Astra/Sol额度耗尽，不恢复、不新建/嵌套agent。

唯一canonical72在/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json，generationMOD4_SINGLE_WRITER72_20261026、modefinite_original_limits_restored_after_single4090_return、authorized2268000/9historical/extensions[]/strictreserve86412.86069250107。原raw实际GO→terminal收费SUMONCE，无退款/补款/rounding/clamp/idle费/grant/secondwriter/copy/clearactive；210旧canonical永远retired。未来任何remote必须fresh72当前owner/run_id/go匹配194 exact3fields，close72后才210/86；194关闭后该binding历史化，不假定仍active。一个GLOBAL serial控制SSH72/210/86/249；每个newfinite fresh LOCAL exactCIM basename/fullpath/exe/fullargv/create；finite活着root仅localreports/CIM/同handle，独立LOCALCPU可。无第二watcher/机械5minpoll/未知PID或GPU-PID扫描/kill/删lock/第三方干预/GUI重启/本地或3060神经CUDA/Luna。startupfree>15669MiB/util<=30允许非空computeUUID/RAM32GiB/disk25GiB；runtime8GiB为保存磁盘guard。保留已过native160k/1µm特定查询，不增FP64/bitwise/三角审计。MATLAB71796保留/GetActiveObject only，非主线。

210严格10.24.5.27:4090原pin/inner22，durableUUID EF3105C85DD986BD新存储写先freshUUID-rw；72pin301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795；86robemo10.50.0.86原pin8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b仅/data/robemo/polar-rl-train；249仅display原pin。Secrets仅memory/noechoSTDIN/memfd，无argv/env/disk/Git；无apt/sudo/globalpip/driver/profile/DNS。

Git实际HEAD/ref/index优先。188/189标签已消费，当前1499旧tag全部保护。实际194新Pi后唯一phase mod4-fudan-jump-original-plane-400n50-dr-two-hour-ppo194，archive_ACTUAL194_original_JUMP_plane_two_hour_and188_closing_ONCE.py仅一次；任何194tag已存在即消费，禁止重record/retag，push失败续原objects。收194所有source/CPU/负例/实际admission/CUDA-FIRST/monitor和188closing费/formalCPU、191原失败V2实际、193原失败修复/窗口/用户反馈全部fullUTF8；190未冻结源排除。二进制PT/rawJSONL/NPZ/USD/STL/media只真实path/bytes/producerSHA或unknown，无FORGit内容/hash/model/hostGPU读。正常结束/最终formals/费用/初始CPU/未来GUI日志普通append不重tag。PostGit只对话/tool验证，不为追HEAD造报告。最终双轮真实越270/完整台面接触12/稳定200physics=.5s仍未达到。
'''
req=dict(id='mod4-10',mode='update',kind='heartbeat',name=actual['name'],status=actual['status'],rrule=actual['rrule'],targetThreadId=actual['target_thread_id'],prompt=prompt)
if 'notification_policy' in actual:req['notificationPolicy']=actual['notification_policy']
put('AUTOMATION194_TWO_HOUR_ACTUAL_UPDATE_REQUEST.json',req)
print(json.dumps(dict(passed=True,run_id=launch['run_id'],timing=work['timing_BJT'],worker=worker['pid'],prompt_characters=len(prompt)),ensure_ascii=False))
