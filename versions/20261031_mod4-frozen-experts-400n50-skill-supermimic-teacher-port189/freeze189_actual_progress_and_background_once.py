"""Freeze actual bounded progress and prepare an update of the SAME heartbeat."""
from pathlib import Path
import hashlib,json,time,tomllib

B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports'
def load(name):return json.loads((R/name).read_bytes())
def put(name,value):
    with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False)

teacher=load('ROOT189_E0_NEW_CPU_TEACHER_PORT_RETURNED_ACTUAL.json')
collector=load('ROOT189_MEASURED_COLLECTOR_SOURCE_CPU_RETURNED_ACTUAL.json')
cycles=load('ROOT189_W35_FIRST_SAVED_CYCLE_SINGLE_PASS_RETURNED_ACTUAL.json')
assert teacher['passed'] and collector['passed'] and cycles['passed']
assert cycles['all_SSH_closed'] and cycles['SESSION_restored']
metrics=cycles['readback']['numerical']
put('CURRENT189_ACTUAL_E0_TEACHER_CPU_AND_W35_CYCLE_ACCEPTANCE_BACKGROUND_V2.json',dict(
    epoch=time.time(),schema='mod4.experts189.background_actual.v2',
    human_instruction='后台继续完成归一化完整技能验收和supermimic化',
    same_automation='mod4-10',new_Goal_or_automation_created=False,
    actual_E0_teacher=dict(groups=len(teacher['groups']),negative_refusals=len(teacher['rejects']),
                          checkpoint_byte_opens=1,decodes=1,original_scaled_probe_rows=72,
                          actual_model_SHA='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a',
                          teacher_weights_STD_RNG_unchanged=True,optimizer_steps=0,
                          new_SuperMimic_model_or_learning_started=False),
    actual_collector_source=dict(groups=len(collector['groups']),negative_refusals=len(collector['rejects']),
                                 actual_SDK_integration=False,actual_physical_transitions_collected=0),
    actual_W35_first_saved_cycle_content=dict(producer=cycles['readback']['producer'],
                    single_raw_open=1,forward_passes_including_EOF=1,local_raw_saved=False,
                    numerical=metrics,all_SSH_closed=True,SESSION_restored=True,
                    fresh_original188_authority=cycles['fresh72_authority']),
    known_missing_for_full_W35_world_acceptance=['same-cycle cross displacement',
                                               'same-cycle commanded signed-yaw error'],
    original_acceptance=dict(along_cross_tol='max(0.03,0.1V)',signed_yaw_error_tol_rad_s=.2,
                             no_new_aggregate_success_rate=True,original_false_and_partial_retained=True),
    next_source_spec='NEXT189_E0_REAL_RUNTIME_COLLECTOR_AND_SKILL_CYCLE_SPEC_FROZEN.json',
    next_executable_remote='NONE: compose and freeze complete E0 runtime caller, source/Task/counts before deployment',
    ordered_background=['E0 full own-runtime teacher collection and missing skill matrix',
                        'E0 independent native WM/Pi/Critic initialization and BC/BPTT admission',
                        'W35 and E2 original full-command/world-cycle functional acceptance',
                        'E3 genuine recovery and original nonintervening control-chain review',
                        'CURB20/SLOPE5 actual later producer join then400N50 and native port'],
    H1_main='188 original Fudan stairs3 PPO remains independent; do not revive obsolete ordinaryH1_86B or native178 windows',
    existing_188_no_hotpatch_or_relaunch=True,
    no_expert_skill_graduation_or_complete_SuperMimic_conversion_claim=True,
    Git_phase='mod4-frozen-experts-400n50-skill-supermimic-teacher-port189',
    Git_status='pending unique189 actual CPU/evidence phase; never retag188'))

put('NEXT189_E0_REAL_RUNTIME_COLLECTOR_AND_SKILL_CYCLE_SPEC_FROZEN.json',dict(
    schema='mod4.experts189.E0_next_actual_runtime_spec.v1',epoch=time.time(),
    source_expert='E0 qualified400N50 final82, a92c9e8d…c74a/14031973B/17Adam641200',
    source_runtime_lineage=str(T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/E0_82_NEW86_EARLY_RESAMPLE_COMPLETE_CASE_SOURCE_20261029_V2'),
    status='SPEC_FROZEN_COMPLETE_CALLER_NOT_YET_BUILT_NOT_ADMITTED',
    task='Retain original E0 standing/straight/pure/world/transition command profiles and D0-D7; collect necessary complete native pairs and missing strict-cycle facts',
    clock=dict(policy_Hz=50,physics_Hz=400,feedback_Hz=100,policy_us=20000,physics_callbacks_per_control=8),
    preserve=['original35/38 observation order and fixed scales', 'original teacher deterministic mean thenclip6',
              'original command sampler/resets/RNG sequence; no extra actor or RNG draw',
              'nominal400N/k2000/DR; original preload, motor envelope and PD/delay',
              '2mm per-env reset, mimic.01, TGS32/4 and F32', 'full frozen teacher state, STD and17Adam'],
    collection=['bind named30 joints and six action order from actual SDK source readback',
                'capture existing original processed policy35 and teacher raw6 on its sole natural actor call',
                'capture own packed127 plus correct dynamic54 auxiliary and staticxi31, no absent fields filled with zeros',
                'capture all eight already-applied processed queue target vectors and two feedback timestamps',
                'capture original terminal endpoint before selected reset; keep episode/command/control IDs',
                'cache and reuse natural physical callback values; no added contact-view getter',
                'exact selected-env/data byte bounds and source read counts declared by complete new caller'],
    cycle_missing_fields=['natural-control rootXY displacement projected both along and perpendicular to fixed original sampled world direction',
                          'actual signed yaw increment plus original commanded signed-yaw integral/duration',
                          'same episode+commandUID+direction+profile for full signed>=2pi sample-endpoint span',
                          'all original terminal masks, partial spans and initial-origin observed state'],
    acceptance='Original along/cross tolerance max(.03,.1V), signed yaw error .2rad/s; retain individual false and no exposure; no invented global pass rate',
    native_method=['PPO stays frozen as teacher; weights are not renamed to native checkpoint',
                   'student uses deployment-available feedback/history/commands; xi only where original native contract permits privileged WM/critic context',
                   'separate50Hz WM truth from own originalPhysX transitions; old100Hz H1 WM cannot be silently reused at20ms',
                   'initial standalone BC matches original clipped six-dimensional command; source module preserves student raw gradient outsideclip',
                   'later task-specific differentiable reward/BPTT and WM/Pi/Critic+norm/optimizers need a separate frozen typed actual admission',
                   'a learned student must pass original own-plant retained skill matrix before replacement'],
    future_remote_requirements=['fresh LOCAL exact CIM and exclusive root serial lease',
                                'fresh72 CNone or exact actual current owner/run_id/go then CLOSE72 before target',
                                'ready task only fresh light resources and original private/shared guards',
                                'learning solely original72 writer/caps/reserve, no new grant or second writer'],
    current_remote_model_raw_SDK_GPU_access_authorized_by_this_SPEC=False))

config_path=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml')
old=tomllib.loads(config_path.read_text('utf8'))
assert old['id']=='mod4-10' and old['kind']=='heartbeat' and old['status']=='ACTIVE'
assert old['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
put('PREVIOUS_AUTOMATION188_BEFORE_EXPERT189_BACKGROUND_UPDATE.json',old)
prefix='''最新人类追加授权：后台继续完成老专家400N/50Hz归一化、完整技能验收和SuperMimic化。这是与188上台阶主线并行的既有专家续办，覆盖下文“唯一主线/旧专家停办”词；188健康训练/原normal900与所有once边界保持，不为专家热改或打断188。原mod4-10同一hourly/聊天继续；不新建automation/Goal，不新建agent（Astra和Sol额度均耗尽）。

首先读取 P/reports/CURRENT189_ACTUAL_E0_TEACHER_CPU_AND_W35_CYCLE_ACCEPTANCE_BACKGROUND_V2.json 和 NEXT189_E0_REAL_RUNTIME_COLLECTOR_AND_SKILL_CYCLE_SPEC_FROZEN.json。P=C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/FROZEN_EXPERTS_400N50_SKILL_SUPERMIMIC_CONTINUATION_V189_20261031。实际HEAD/ref/index/receipt优先。

已实际完成189：4个400N50正式模型小文本清单；E0新教师端口CPU7组+10拒绝PASS，一次新目的E0formal1bytepass/1decode/72确定性35维源探针，原actor/STD/RNG不变、optimizer0、CUDA0。native采集组件另2组+7拒绝PASS但尚未接SDK，不是已SuperMimic开训或技能毕业。源35输入必须使用真实runtime已处理观测；不猜state127->35，不重归一化旧actor。

W35新技能验收必要目的已CONSUMED/RETURNED0：原exact86 cycle producer5039行2618543B/f5f6cbd98259358b0755992e2393a8e63e1061fdf1789fbbdfc6dbfe7aa53561只一次open/一次forward含EOF；未保存本地raw/模型0/SDK0/GPU0。先新鲜72匹配actual188→CLOSE72→strict86，已全部SSH关闭/SESSION恢复。不得重读/下载/hash该JSONL；用已保存派生JSON。完整1229圈/945unique env，逐圈前进MAE .0217215888523m/s；1113圈沿向误差<=原.05、116圈超出。排终止1214圈/936unique、MAE .0218204217157，仍116圈超出。不能把均值或沿向通过数冒称完整技能通过：producer缺同圈cross位移和原signed-yaw命令误差；原false/15终止/3810partial保留。

下一步必须持续实施而非只列错误：从P冻结NEXT spec组成NEW完整E0真实runtime采集+缺失整圈字段caller，沿用原E0_82_NEW86_EARLY_RESAMPLE_COMPLETE_CASE_SOURCE_20261029_V2命令/任务/DR和原已验证时钟，冻结source/Task/读取计数/实际SDK准入后在可用已授权4090执行。P/measured_teacher_collector189.py和expert_teacher_port189.py是已测组件，不是完整GPUcaller，不能直接启动。采集真实own127+xi31/原policy35/teacherraw与clip6/8callback processedqueue/2feedback/原terminal-before-reset和episode/commandUID；不用旧稀疏checkpoint/commandtraces冒充完整WM数据。新native50Hz需要自己的WM/Pi/Critic+norms/opts和实际训练准入；旧H1native100Hz不能直接当50Hz真值。PPO专家冻结作教师并保留可用，不覆写旧模型；先独立BC再源证据支持的原任务BPTT，不换成H1/Fudan跳跃奖励。完成后真实原plant完整技能复验，再W35/E2/E3；补CURB20/SLOPE5需先实际later producer/source精确join。旧普通H1_86B只历史lead，不另开覆盖当前188。没有合格源的额外E4/E5不凭名字造专家。

沿用原完整圈along/cross tol=max(.03,.1V)、signed-yaw误差.2rad/s和全失败样本，禁止新造90/95/100%总通过线。E0旧20k20s、W35旧16s、E2旧18s、E3旧.48s原证据精确复用，不为“验收”无区别重跑旧once。新技能字段与真正新teacher/native任务有新目的才读取。D0-D7工程范围/400N50/2.5ms32/4/F32/2mm每env原样；无实物弹簧或摩擦曲线不谎称实物认证。

189所有source/CPU原结果/必要raw单遍派生/原reader errors/本次授权与自动化回执需独立actual CPU/验收phase唯一tag mod4-frozen-experts-400n50-skill-supermimic-teacher-port189，经record_experiment一次；任何189tag存在即CONSUMED不重record/retag。保护既有1498标签对象与peels。后续189源/新caller/实际GPU/验收按实际阶段或ordinary追加；binary只真实path/bytes/已有producerSHA，绝不为Git重读模型/raw。189不声称新增GPU学习。188独立normal收尾仍按下文原最早17:59:28；若到窗且未消费优先完成原normal+NEWformalCPU再继续专家，若已关闭读取实际新状态，不沿用active188绑定。远端控制永远GLOBAL serial、每finite新鲜LOCAL exactCIM、current72→close→target、原唯一72账和3900/3600/300不变；无额外grant/writer/force/reset/guard放松。

以下188原工作单保留，历史“唯一”由本次专家并行授权覆盖：
'''
request=dict(id=old['id'],mode='update',kind=old['kind'],name=old['name'],
             prompt=prefix+old['prompt'],status=old['status'],rrule=old['rrule'],
             targetThreadId=old['target_thread_id'])
put('AUTOMATION189_BACKGROUND_UPDATE_REQUEST.json',request)
print(json.dumps(dict(passed=True,request=str(R/'AUTOMATION189_BACKGROUND_UPDATE_REQUEST.json'),
                      prompt_characters=len(request['prompt']),W35_cycle_MAE=metrics['all_complete']['cycle_progress_event_MAE_m_s'])))
