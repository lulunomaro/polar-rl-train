"""Local closed219 handoff; no experiment/model/raw reads or remote calls."""
from pathlib import Path
import json,time
N=Path(__file__).resolve().parent;R=N/'reports';T=N.parent
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False)
c=read(R/'ROOT219V3_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
cpu=read(R/'ROOT219V3_NEW_W35_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')
row=cpu['roles']['w35_72'];r=c['roles']['w35_72'];end=read(R/'ROOT219V3_NORMAL900_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')
assert c['passed_collection']and cpu['passed']and row['save_at_or_after_requested_deadline']
assert c['owner_closed']['canonical_None']and c['owner_closed']['shared_locks_free']and r['private_EX_free']
assert end['all_owned_SSH_closed']and end['SESSION_restored']and end['global_serial_control_client_lease']=='FREE'
assert row['new_PPO_updates']==68 and r['actual_material_limit_error_count']==0
previous=read(R/'CURRENT_ACTUAL219V3_W35_FIRST_CLOSED210_AND220_221_NO_FLIGHT_CLAMP_WORK_ORDER_V2.json')
work=dict(epoch=time.time(),kind='CLOSED219_QUALIFIED_FULL_RM70_PPO_AND_PENDING_SKILL_REGRESSION',
 run_id=c['run_id'],qualified_W35=row,new_environment_transitions=68*24*20000,
 original_fee_sum_once=c['owner_closed']['raw_fee_sum_once'],
 historical_closing_balance_snapshot=c['owner_closed']['closing_balance_snapshot'],
 original_owner_out_or_nonexecuting_zombie=c['owner_closed']['original_owner_out_or_original_nonexecuting_zombie'],
 original_node_exit=r['original_node_exit'],private_EX_free=r['private_EX_free'],shared_locks_free=True,
 actual_material_limit_error_count=0,returned_full_UTF8=dict(files=len(r['full_UTF8']),bytes=sum(x['bytes']for x in r['full_UTF8'])),
 single_NEW_formal_transfer_and_two_host_SHA=c['formals']['w35_72'],NEW_CPU_reads=cpu['NEW_formal_reads'],old_model_reads=cpu['old_model_reads'],
 CUDA_initialized=cpu['CUDA_initialized'],current_H1_learning=False,old219_active_binding_now='HISTORICAL_ONLY; future remote requires fresh CNone or actual new owner/run/go',
 E0_three_hour_previous=previous['E0_210_closed'],E0_actual220_221=previous['actual220_221'],
 full_RM70_skill=False,E2_E3_complete_skill=False,complete_SuperMimic_conversion=False,true270=False,
 next='Same authorized child source222: new bounded W35 fullRM70 skill validation source/CPU only until INDEX frozen. Root actual metadata/resources/task/model-use admission required; no new learning GO.',
 current_control_client_lease='FREE',no_NEW_grant_or_account_writer=True)
workname='CURRENT_CLOSED219_QUALIFIED_FULL_RM70_FORMAL_AND_PENDING222_SKILL_WORK_ORDER.json';put(R/workname,work)
audit=dict(epoch=time.time(),kind='LOCAL_SOURCE_REVIEW_DURING_ORIGINAL219_NORMAL_FINITE',
 data_reads='Only previously returned source text and small saved metadata JSON; no models/raw/NPZ/SDK/GPU/remote',
 original_rg_missing_path='ROOT220V2_SOURCE_PACKAGE/worker220_new_formal_mean_plane_flight.py did not exist; rg returned1. Correct source found with rg --files: evaluate220_NEW210_E0_mean_plane_flight_UNUSED_once.py. No execution or source change occurred.',
 verified_sources=[str(T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/package/run210_mixed_E0_JUMP_worker.py'),str(T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/package/mixed209_sdk.py'),str(T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/package/jump194_sdk.py'),str(T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/package/payload/job0/runtime/isaac/mod4/mod4_task.py')],
 findings=['Training and evaluation both use original wrapper clip_actions6 and35D fixedSI observations.',
 'LEG_ORDER=[left_crank,left_hip,right_crank,right_hip], WHEEL_ORDER=[left_wheel_spin,right_wheel_spin]; ActionCfg preserves order. Four leg position targets, then wheel velocity targets.',
 'Original leg action scale.5rad, wheel10rad/s; original CAD input-difference guard remains after target processing. Raw111 is not joint angle or measured torque.',
 'Original literal JUMP receives action_manager.action reordered [0,1,4,2,3,5]; previous action history updates with that same order. Actual221 matched clip6 with residual0.',
 'Mixed2000ground/18000jump is persistent mode0/mode1. E0 groundheight.25 and JUMP .12..15; source routes original rewards disjointly without blending.',
 'Cached210 LATEST_PROGRESS:6600controls/15,309,214 original flight-flag environment-controls. This contact-filter flag is not geometric clearance/stable landing, population success or a replacement for actual220 noflight result.'],
 no_new_E0_learning_or_actor_STD_reward_guard_patch_selected=True)
put(R/'ROOT219_CLOSING_INDEPENDENT_E0_ACTION_SOURCE_REVIEW_AND_ORIGINAL_RG_MISS.json',audit)
req=read(R/'AUTOMATION219_ACTUAL220_221_NO_FLIGHT_CLAMP_UPDATE_REQUEST.json')
intro='''CURRENT_CLOSED219_QUALIFIED_FULL_RM70_PPO68_AND_PENDING222_SKILL_20261101。覆盖219running/normal未用/ad504仍latest/C219active等旧词。FIRST READ N/reports/CURRENT_CLOSED219_QUALIFIED_FULL_RM70_FORMAL_AND_PENDING222_SKILL_WORK_ORDER.json、ROOT219V3_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json、ROOT219V3_NEW_W35_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json。N=T/W35_SOLO_INSTALL_FIRST_AND_CLOSED_READERS_SOURCE_V219_20261101，T=C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021。\n实际原219V3 normal和NEW formal CPU均已RETURNED0/CONSUMED，不可再跑collector/CPU/transfer/hash用于统计或Git。68新PPO/32640000own transitions/iter32404/17Adam649720；最终17619269B SHA343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd，181finite tensors/fullactor35critic38STD6/17Adam/完整D0-D7/newRM70terraincommand和typed214通过；实际保存epoch1793478874.050945>=原save_deadline1793478872.418197，原一小时窗口完成。adaptive最终LR.00017085937500000009，不假等初始.00011390625。原64K错误0，40fullUTF8/9508634B返回。1formal transfer/两hostSHA+1NEWCPU读解码，oldPT0/CUDA未初始化。原owner/node/workerallwait-out/privateEX+sharedfree/COHORT_FINAL/OWNER_EXIT/NODE_EXIT/精确唯一原owner账段/GO均通过，原费用3630.6560065746307 SUMONCE，closing412768.03090405464只历史snapshot。ROOT所有SSHfinallyclosed/sessionrestored/globalclientleaseFREE。当前没有H1学习；旧219 binding已HISTORICAL，任何新remote需fresh72 CNone或真正新owner/run/go，不能盲用旧ACTIVE219。\n这只是合格新模型，不是完整RM70技能/SuperMimic/E2E3/270毕业。人类持续授权的同child/root/w35_rm70_expert_normalization208正在NEW222 W35 fullRM70完整技能回归LOCALsource/CPU：复用213同UID along/cross/signedyaw/pre-reset接口与219production，最多32s/1600controls/原已准入规模；严格原CAD70mm峰谷/400N50D0-D7/guards/commands/reward不改，不自造gate，缺字段UNKNOWN。INDEX未冻结前EXPLICIT_PENDING排除，不执行SDK/模型/新训练；实际冻结状态以最新files/receipt为准。ROOT后续必要新targetmetadata/typedTask/resources/model1读取目的、单串行SSH与freshCNone仍要实际完成，不把sourceCPU称通过技能。没有新学习GO/预算grant。\nE0已完成三小时275updates，但220一条新20s controlled mean测试未腾空；221左crank1000/1000动作负饱和-6、原raw[-111.48,-60.97]，其余5无超6，clip+排列残差0。此问题未修复，不能只说训练不足，不能盲续。独立LOCALsource确认ActionCfg LEG_ORDER/原.5rad scale/10rad/s wheel/clip6/原CAD差动约束和JUMP reward动作history保持同顺序；无新模型raw读取。原15,309,214 flightflag累计不是几何腾空或成功率，不代替实际220 noflight。220父APPmarkerfalse仍保留。所有220/221目的已消费，旧E0不覆盖。\nGit219实际phase已CONSUMED main e50a6aafcba147feeaa09032931e7e6f56e5aff9/tagobject083e0444115d45d1d7616923142c6a370b80522f/1505tags，1504oldobjects/peels已保护。绝不再record/retag219；本219 closing/fee/NEWCPU/此source审阅/同appreceipt以及222若冻结，只ordinary219 supplement。actualHEAD/refs/index优先；push失败只续原objects。后面旧原prompt仅历史，不是once执行指令。\n\nHISTORICAL219_FIRST_AND_PRIOR_HARD_CONSTRAINTS_RETAINED_WHERE_NOT_OVERRIDDEN:\n'''
req['prompt']=intro+req['prompt'];reqname='AUTOMATION_CLOSED219_QUALIFIED_AND_PENDING222_UPDATE_REQUEST.json';put(R/reqname,req)
print(json.dumps(dict(passed=True,workorder=str(R/workname),request=str(R/reqname),skill_not_inferred=True)))
