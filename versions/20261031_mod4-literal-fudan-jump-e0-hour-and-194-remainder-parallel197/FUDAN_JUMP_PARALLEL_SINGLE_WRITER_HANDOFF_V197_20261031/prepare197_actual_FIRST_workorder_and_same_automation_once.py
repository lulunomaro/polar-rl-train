"""Freeze local actual FIRST handoff, without accessing any remote/model/raw file."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, time, tomllib

N = Path(__file__).resolve().parent
T = N.parent
R = N / 'reports'
E = T / 'E0_82_LITERAL_FUDAN_JUMP72_ONE_HOUR_SOURCE_V198_20261031'

def read(p):
    return json.loads(Path(p).read_bytes())

def put(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)

def bjt(epoch):
    return datetime.fromtimestamp(epoch, timezone(timedelta(hours=8))).isoformat()

launch = read(R / 'ROOT197_ORIGINAL_UNIFIED_OWNER_LAUNCH_ACTUAL.json')
state = read(R / 'ROOT197_UNIFIED_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json')
finally_ = read(R / 'ROOT197_UNIFIED_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')
child = read(E / 'reports/ACTUAL198_DELEGATED_UNIFIED_FIRST_AND_CLIENT_RELEASE_HANDOFF.json')
assert state['current_owner_matched'] and not state['canonical_None']
assert finally_['all_owned_SSH_closed'] and finally_['SESSION_restored']
assert finally_['global_serial_control_client_lease'] == 'FREE'
assert child['passed'] and child['run_id'] == launch['run_id']
go = state['current']['go']
assert set(go) == {'h1_210', 'e0_72'}
assert go['e0_72']['save_deadline'] - go['e0_72']['learning_started_epoch'] == 3600
specs = launch['specs']
roles = {}
first_names = {'h1_210': 'ROOT197_PRIMARY210_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',
               'e0_72': 'ROOT197_E0_72_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json'}
for key, name in first_names.items():
    receipt = read(R / name)
    first = receipt['first']
    assert receipt['passed'] and first['passed'] and first['actual_new_PPO_updates'] == 1
    assert first['new_environment_transitions'] == 480000
    assert first['first_complete']['full_core_STD_optimizer_and_targetDR_saved']
    assert first['source_SHA'] == specs[key]['source_SHA']
    assert first['first_complete']['saved_iteration'] == specs[key]['source_iteration'] + 1
    assert first['new_Adam_step'] == specs[key]['source_Adamstep'] + 20
    roles[key] = dict(GPU_UUID=specs[key]['GPU_UUID'], actual_FIRST=first,
                      worker_identity=state['current']['rows'][key]['worker'],
                      job_root=specs[key]['job_root'],
                      times_BJT={k: bjt(go[key][k]) for k in ('learning_started_epoch', 'save_deadline', 'nominal_end_epoch')},
                      signed_original_GO=go[key], FIRST_not_continued_liveness_or_skill=True)

binding = dict(owner=launch['owner'], run_id=launch['run_id'], go=go)
put('KNOWN_ACTIVE197_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json', binding)
earliest = max(x['nominal_end_epoch'] for x in go.values()) - 900
readers = []
for name in ('collect197_original_two_role_formals_cost_normal900_UNUSED_once.py',
             'review197_TWO_NEW_formals_initial_whole_CPU_UNUSED_once.py'):
    p = N / name
    raw = p.read_bytes()
    compile(raw, str(p), 'exec')
    readers.append(dict(path=str(p), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest(), status='FROZEN_UNUSED'))

work = dict(epoch=time.time(), kind='ACTUAL197_TWO_GENUINE_LITERAL_JUMP_PPO_FIRSTS',
    human_instruction='e0分支可以交给子代理去启动，不浪费时间，训1个时，找一张空闲卡',
    actual_delegated_agent='/root/e0_jump_parallel_launch195',
    run_id=launch['run_id'], owner=launch['owner'], roles=roles,
    first_proof=first_names, authority_binding='KNOWN_ACTIVE197_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json',
    old194_handoff=dict(status='CONSUMED_COMPLETE_SAVED_PREFIX_AND_QUALIFIED_FULLSTATE',
        source_SHA=specs['h1_210']['source_SHA'], bytes=17518367,
        new_PPO_updates=311, saved_iteration=5310, Adam17_step=106240,
        actual_used_learning_window_seconds=5959.281657218933,
        remaining_seconds=1240.718342781067, original_requested_seconds=7200,
        original_raw_fee_sum_once=5975.628768444061, closing_balance_historical_snapshot=434306.7866637707,
        complete_waitout_locksfree_CNone=True, CPU192_finite_passed=True,
        scope='Safe own STOP_AFTER_SAVE and one final transfer/CPU read, not original two-hour completion'),
    unchanged_reward_and_physics=dict(repo_commit='8204e853dfd2ed06d85a322e1a998c3d20a3be2c',
        reward='JUMP19 methods and full rewards config /16 scales byte-literal',
        clip_single=2.5, total_positive_clip=False, self_dt=.02,
        stateful_current_previous_contact_and_crossreset_flight_memory='unchanged',
        plane_mu_restitution=[.5,.5], command_resample_s=20,
        command_vx=[-2.1,2.1], command_yaw=[-2,2], height_command=[.12,.15],
        gas='nominal400N engineering /k2000', target_DR='D0white_v3 and D1-D7',
        policy_hz=50, feedback_hz=100, physics_dt=.0025, TGS=[32,4],
        actor35_critic38_STD6_17Adam='Full source states retained; ordinary single-optimizer PPO',
        physical_guards='original per-env2mm /mimic.01/PD/6actionclip6/delay unchanged',
        runtime_mapping='Actual MOD4 own hip-wheel BODY geometry/contact/SDK state outside unchanged reward',
        no_force_or_state_injection=True, fresh_physics_DR_queue_history=True),
    normal_collection=dict(status='FROZEN_UNUSED', earliest_epoch=earliest, earliest_BJT=bjt(earliest),
        source_entries=readers, original_owner_wait_s=850, original_node_wait_s=180,
        requirements='Fresh LOCAL exact CIM/global serial lease FREE/local AND remote latest signed nominal-now<=900',
        evidence='Actual COHORT_FINAL/OWNER_EXIT/NODE_EXIT/all own waits-out/known original nonexecuting-or-out/private/sharedfree/freshCNone/unique owner segment exact GO',
        fees='Two independent original raw fees summed once; no clamp/refund/grant/canonical copy/second writer',
        formal_reads='One NEW final transfer and two-host SHA per qualified role; then one NEW CPU decode each, old194/E0/native/normal86 reads0',
        full_requested_duration='Compare final saved epochs to each signed save deadline; time alone and FIRST do not prove completion',
        physical_regression='New frozen necessary small standing/forward/reverse/actual plane flight-landing purpose still required; no old eval replay'),
    retired_unused_entries=['194 original normal900 collector and initialCPU: replaced by consumed197 safe saved-prefix handoff',
                            '195 solo-forward installer/FIRST/normal: superseded before execution by198/197 parallel branch'],
    retained_original_limits=child['controller_completion_evidence'],
    diagnostic_label_error=child['legacy_wrong_next_iteration_field'],
    current_control_finally=finally_,
    no_new_remote_GPU_model_raw_read_in_this_workorder=True,
    remaining_goal='No actual flight/landing/stable regression yet; true dualwheel270mm jump and stable recovery UNACHIEVED',
    Git='NEW actual197 phase once; all1500 old tag objects/peels protected; actual refs/index dominate pending words')
put('CURRENT_ACTUAL197_PARALLEL_E0_HOUR_AND194_REMAINDER_FIRST_AND_NORMAL_WORK_ORDER.json', work)

a_path = Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml')
a = tomllib.loads(a_path.read_text('utf8'))
assert a['id'] == 'mod4-10' and a['kind'] == 'heartbeat' and a['status'] == 'ACTIVE'
assert a['target_thread_id'] == '01a07a2d-9036-7531-a012-692df9f56353'
with (R / 'PREVIOUS_AUTOMATION_PROMPT_BEFORE197_HISTORICAL_ONLY.txt').open('x', encoding='utf8') as f:
    f.write('HISTORICAL ONLY. Superseded194 active and195 sequential instructions; never execute from this history.\n\n' + a['prompt'])

prompt = f'''当前实际主线197/198已由人类明确授权子代理找空闲卡并训练E0一小时，取代194单角色/195顺序待启动文字。同一mod4-10 ACTIVE/hourly/原聊天01a07a2d-9036-7531-a012-692df9f56353，不新Goal/create/resume/automation。实际文件/refs/HEAD/index/toolreceipt优先，已消费once永不重放。保持未变化、健康或未到正常窗口时安静，仅通知有意义完成/失败/实质修复/资源预算网络/必需用户行动。

FIRST READ {R.as_posix()}/CURRENT_ACTUAL197_PARALLEL_E0_HOUR_AND194_REMAINDER_FIRST_AND_NORMAL_WORK_ORDER.json、KNOWN_ACTIVE197_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json、ROOT197_PRIMARY210_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json、ROOT197_E0_72_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json、ROOT197_UNIFIED_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json。N197={N.as_posix()}；N198={E.as_posix()}。旧完整prompt保存在N197/reports/PREVIOUS_AUTOMATION_PROMPT_BEFORE197_HISTORICAL_ONLY.txt，仅历史不用作旧once执行指令。

实际run {launch['run_id']}；统一唯一owner72=982324/create1793450608.63，cwd=/home/lc01/Zonglin Li/zonglin2，与taskroot不同；root=/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_PARALLEL197_194REMAIN_E0JUMP_2610v197/owner。两个真实角色均实际FIRST PASS，各20k环境×24controls=480000新own transitions/1PPO。h1_210在原forwarded4090 GPU937bdb0b，worker3591422/create1793450620.92；E0_72在空闲72 GPU16828f91，worker982359/create1793450621.37，实际glibc240/fullargv/cwd见原回执。preexec bash身份照原报告保留，不伪称Python。所有root/子代理控制SSH最终closed、SESSION restored、global serial clientlease FREE；无额外健康watcher/热改/复查空GPU。FIRST不是持续存活、FINAL或跳跃技能。

E0从原E0_82全actor35/critic38/STD6/17Adam/LR复原，sourceSHA a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a/14031973B，原31984/Adam641200；实际FIRST31985/641220，17519967B SHAd4f2a19aaf54b483b760536a36a9da28d53ded0751cc83245c6f49f95ec4848f。1必要GPU读/解码已消费，不为统计/Git重读。restore报告next_iteration5000是保留的错误标签，实际FIRST/counters31985证明E0接续；不能为修标签热改/重跑/停止。CPU4groups+9reject、target64env0PT8controls64physics16feedback/RC0/privateEXfree已消费。E0 GO20:43:39.114369 BJT，SAVE21:43:39.114369，NOMINAL21:48:39.114369（2026-10-31），3600learning+300exit，不自动延长或新grant。job=/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_82_FUDAN_JUMP72_400N50_20261031v198/e0_72，control197。

原194按人类并行新指令，经它自己的STOP_AFTER_SAVE完整保存/正常退场，311新PPO/iteration5310/17Adam106240；formal17518367B SHA7b8a8cbba3b7da7f9a44567e4fab58d36dabcc412e659a83520801e4972d70b7，转1/两hostSHA/NEWCPU1读192finite PASS，allwaitout/locksfree/CNone。原fee5975.628768444061 SUMONCE/closing434306.7866637707仅历史snapshot。实际用5959.281657218933s，剩1240.718342781067s接续197，非原2小时已完成。h1_210 GO20:43:38.595230/SAVE21:04:19.313572/NOMINAL21:09:19.313572；实际FIRST5311/Adam106260/full17520927B SHA7fd62d81b2323bf5cad4e1face3e9f31a67f12377746f2ad3927c30f114fd756。完整actor/critic/STD/17Adam/LR和CPU/CUDA采样RNG复原，物理/DR episode/queue历史fresh不是精确PhysX续态。job=/mnt/mod4_linux_durable_20261013/MOD4_JUMP194_REMAINING_PARALLEL_20261031v197/h1_210，control197。194旧normal900/旧CPU未用但已被本次handoff替代，195solo installer/FIRST/normal未用且被parallel覆盖，永不再执行。旧194activebinding已经历史化。

当前两路都是原复旦JUMP平面/400N50DR，commit8204e853dfd2ed06d85a322e1a998c3d20a3be2c原19方法/完整rewards配置/16weight字节相同，clip_single2.5×dt/无total正裁剪/check_jump current+previous contact/base_air_time跨reset记忆原样。self.dt.02且外层仅抵消Lab额外dt。原平面μ/rest.5/.5/20s采样vx±2.1/yaw±2/height.12..15，不加零yaw/混walking奖励/teacher动作/脚本起跳/新成功项。外层MOD4真实hip锚点→轮轴BODY L0/theta/31body接触/WORLD vz/BODY FD/近似applied effort明确非实测扭矩。原6actions/clip6/PD/延迟/名义400N工程k2000/D0white_v3 D1-D7/50policy100feedback400physics2.5ms TGS32/4 F32/perenv2mm/mimic.01不改。E0walkingmode0→JUMPmode1是新任务，warmstart不保证走稳保留；之后须新冻结小量站立正反走/实际平面腾空落地回归。首次更新/奖励/接触离开/绝对root高不是技能，真实270稳定仍未达到。

NEXT ONLY N197/collect197_original_two_role_formals_cost_normal900_UNUSED_once.py（FROZEN UNUSED），freshLOCALexactCIM+globalserialleaseFREE，原签名LOCAL AND REMOTE latest signed nominal-now<=900。合并正常最早{bjt(earliest)}，owner850/node180不改，不提前/第二watcher/机械5minpoll/重复FIRST。实际COHORT_FINAL/OWNER_EXIT/NODE_EXIT/allownwait-out/known原PID退出或原Z非执行/两shared及privateEXfree/新鲜CNone/唯一原ownersegment精确两个GO后，两笔独立rawfee只SUMONCE，无退款/补款/rounding/clamp/idlefee/grant/canonicalcopy/clearactive/第二writer。每qualified角色仅1NEWformal传输/两hostSHA，输出ROOT197_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json与N197/current_closed197_models/{{e0_72,h1_210}}/formal/model_final.pt。partial/FAIL不晋升；最终saveepoch要对照各save_deadline才可称原时长完成。
完整JSONguards后才N197/review197_TWO_NEW_formals_initial_whole_CPU_UNUSED_once.py，脚本内CUDA_VISIBLE_DEVICES=''，每NEWformal读解码1，旧194input/E0input/native/normal86全0。严格finite actor35/critic38/STD6/17Adam：E0=641200+20updates/iter31984+updates；h1=106240+20updates/iter5310+updates。target_DR_state+original_jump_reward_memory/typed_E0_JUMP198_task或typed_JUMP197_resume_task/sourceSHA与currentTask绑定。普通PPO一optimizer，不套nativeWM3opts或称20nativeiter。所有input/194handoff/admit198/37sourceGOtests/统一launch+两FIRST都已消费，不统计/Git重读。子代理原本地OS RC因tool输出截断为UNKNOWN，FIRST/owner/finally齐全，不能伪填RC0或重跑入口。

唯一canonical72=/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json，generationMOD4_SINGLE_WRITER72_20261026/modefinite_original_limits_restored_after_single4090_return/authorized2268000/9historical/extensions[]/strictreserve86412.86069250107。原两fcntl/HMAC/charge_values AST保留，无新grant。197关闭前任何新remote须fresh72当前owner/run_id/go与KNOWN_ACTIVE197 exact3fields匹配，CLOSE72后才210/86；关闭后binding历史化，不假定仍active。ONE GLOBAL serial控制SSH72/210/86/249；每newfinite先fresh LOCAL CIM basename/fullpath/exe/fullargv/create；客户端活着root仅localreports/CIM/同handle，可独立LOCALCPU。无未知PID/GPU-PID扫描/kill/删lock/第三方干预/GUI重启/本地3060神经CUDA/Luna/OpenRouter。startupfree>15669MiB/util<=30允许nonemptycomputeUUID/RAM32GiB/disk25GiB；健康job不复查startupfree，runtime8GiB是磁盘fullsaveguard。复用native160k/1µm旧特定查询，不增FP64/bitwise/三角门禁。
210严格egde@10.24.5.27:4090→inner22原pin，durableUUID EF3105C85DD986BD新存储写先freshUUID-rw，无cleanup/fstabguess；210旧canonical永远retired。72pin301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795/ownerloopback29754；86robemo10.50.0.86/pin8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b仅/data/robemo/polar-rl-train；249仅display原pin95b8067b17fc5331aac5e2d46acd6a087c46719dc853658b14bfa0e29e69242e。Secrets memory/noechoSTDIN/memfd only，无argv/env/disk/Git；noapt/sudo/globalpip/driver/profile/DNS。MATLAB71796保留GetActiveObjectonly，非主线。

后台190/RM70/E2/E3归一化完整技能验收/SuperMimic化授权继续；190仅冻结WM50 LOCAL组件5groups/128syntheticpairs/1update，非实际expert/SDK/GPU或PiCritic全转换。V3仅诊断label澄清，不重复fixture。W35原5039行onepass已消费，1229cycle/116原along.05超线/crossyaw UNKNOWN；W35不是RM70。RM70=70mm峰谷/周期240.641934mm/全段2.406423m/宽2.0845m/坡1.5deg不是±70。E2E3未完整毕业；不hotadd197、不额外writer或padding占卡。仅本轮明确授权的/root/e0_jump_parallel_launch195已完成启动交接，当前无新agent授权；不用Astra/Sol额度/新嵌套。旧193窗口仅closed188eval，保留/noreopen/kill，不能称197live/PPO不能造蓝WM。196一次人类status只读已消费，不自动重复。

Git遵守AGENTS/ALL_TRIALS，194tag和1500旧tag全部保护。新的实际双Pi阶段唯一IDmod4-literal-fudan-jump-e0-hour-and-194-remainder-parallel197，经record_experiment ONCE；任何该phase tag存在即消费，不重record/retag，push失败只续已有objects。actualHEAD/refs/index优先于pending，旧194/195不再record。收N197/N198全部源/原label错误/TaskGO拒绝/actual0PT/admission/旧194stop与完整closing费/新CPU/两FIRST/所有完整UTF8/lease/CIM/子代理OS RCunknown/同automation回执。模型/rawJSONL/NPZ/USD/STL/MAT/media metadataonly真实path/bytes/producerSHA或unknown，绝不FORGit读/hash模型raw/hostGPU。后续两role FINAL/fees/formalCPU/物理回归只ordinaryappend或真正新phase，postGit只tool核验和对话不追HEAD造报告。真正双轮腾空越270/完整台面接触12/稳定200physics callbacks=.5s仍UNACHIEVED。'''

req = dict(mode='update', id=a['id'], kind=a['kind'], name=a['name'],
           prompt=prompt.rstrip('\n'), status=a['status'], rrule=a['rrule'],
           targetThreadId=a['target_thread_id'])
if 'notification_policy' in a:
    req['notificationPolicy'] = a['notification_policy']
put('AUTOMATION197_ACTUAL_TWO_ROLES_UPDATE_REQUEST.json', req)
put('CAPTURE_ACTUAL197_198_FROZEN_SCOPE.json', dict(epoch=time.time(), roots=[str(N),str(E)],
    full_UTF8_including_source_backups=True, binary_metadata_only=True,
    input_source_SHA=specs['h1_210']['source_SHA'], E0_source_SHA=specs['e0_72']['source_SHA'],
    active_remote_future_logs='Excluded until original normal collection, not permanent missing evidence',
    unselected_background190='Already archived component only; no new current source selected',
    no_model_raw_content_or_GPU_queries_for_Git=True,
    consumed_once_entries='194ownsave+close+savedCPU /198prepare+CPU+admit /197source+37GOtests+sealed+launchFIRSTs',
    frozen_unused_entries=readers,
    current_user_and_commentary='Delegated E0 onehour on free card; root safely saved194 prefix and resumed remainder in one canonical owner'))
print(json.dumps(dict(passed=True, run_id=launch['run_id'], roles={k:v['times_BJT'] for k,v in roles.items()},
                      normal_earliest_BJT=bjt(earliest), no_remote_or_model_raw_reads=True)))
