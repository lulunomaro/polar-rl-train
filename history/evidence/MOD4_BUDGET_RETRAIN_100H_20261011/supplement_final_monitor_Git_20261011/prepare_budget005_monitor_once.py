"""Retain the exact old heartbeat and prepare the new time/retraining authority."""
from prepare_authorization_and_dispatch_once import D,R,save,H
from pathlib import Path
import os,tomllib,json,time


def main():
 applied=json.loads((R/'BUDGET_APPLIED.json').read_bytes())
 assert applied['applied_once'] and applied['authorized_after']==1188000 and applied['extension_records']==7
 p=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml'
 metadata=tomllib.loads(p.read_text(encoding='utf-8'))
 assert metadata['status']=='ACTIVE' and metadata['rrule']=='FREQ=HOURLY;INTERVAL=2'
 old=metadata['prompt']
 previous=D/'MONITOR_PREVIOUS_COMPLETE138_PROMPT.md'
 with previous.open('xb') as f:f.write(old.encode())
 leading='''最新2026-10-11人类直接授权优先：“预算再给你100小时，没毕业的可以复训”。已实际执行新005时间/复训修订，唯一canonical第七次USER_ADD100H_20261011_7TH已在actualownfullsave/PASSED/父guardian孩子exit/两OS锁/active-Sactive空边界唯一登记360000s，原六次扩展/184completedsegments/charged511202.45738077164s不变。总授权1188000s330h，当前idle剩676797.5426192284s约187.9993h仅快照。先读中央MOD4_BUDGET_RETRAIN_100H_REVISION_005.md/json、MOD4_BUDGET_RETRAIN_100H_005_APPROVAL、USER_ADD100H_20261011_7TH_APPLIED、MOD4_BUDGET_RETRAIN_100H_005_METADATA_SYNCED，以及本机MOD4_BUDGET_RETRAIN_100H_20261011/reports。PLAN_APPROVAL仅更新时间ceiling1188000与新amendment，执行合同budget/当前005引用已真实同步；历史master812a4b与EXECUTION_TRACKS/RM003002001/004职责批准字节保持。旧828000/六扩展/新增0是005以前历史，不能据旧guard拒绝新获准时间或再重跑第六/第七次扩展。所有budgettail/once不可重跑；真实账本和unique新receipt优先。

005明确允许未毕业专家独立有界复训，原未完成/失败/false/raw/cost不重标。优先新CURB20正向方向/入口单轴合同和实际footprint+commandhistogram，再WAVE35正反完整通行纠正；暖启动仍完整129source3643c97，不自动拿退化df0c/2b4覆盖专家。E0和已接受SLOPE5/8/10度范围冻结，STAIR与真实RM后续先核新几何；合格专家冻结后才gate/整机切换。新增100h规划CURB25/WAVE25/剩余坡15/真台阶10/gate切换15/准入修复10；原S3含已用E1 30h加新增地形75h合计105h规划上限。这些不是必须花满或ledgerreserve，actualB及其它expert/gate保护、min(18h,.13B)修复规划优先。S7条件18h原规划保持，新时间不自动批准S8危险reset/实车/新硬件、传感接口、teacher或放松故障阈值。复训不能只留队列/无限hold或无诊断盲PPO。

下一积极执行此前CURB20 reset-entry CPU单轴准备，当前尚无新implementation/learningexecutor。新的范围完成来源全actorcriticstdoptimizer/allDR/globalnamed/dictprivateCPUCUDA/geometrycommand身份、显式新assignment迁移/CUDAroundtrip/savedsourceepisode+1/独立输出与必要新CPU/SDK/native/128x2-20kx4完整PPO各一次后，首300sload-learn-save-exit/save25/15s本机guardian，同唯一canonical正常扣。新controller预算准入须独立验证七条注册扩展sum+base10h=1188000及实际余量，旧硬编码828000入口不hotpatch/不复活，应在新isolatedwrapper/sourcefreeze里明确005时间合同。已有clock/DR/同scope合同exactSHA复用，不重45minclock/旧PPO或validcomplete回放。自己的完整save/PID/PASSED/唯一结清与四case完整审查后才能合理接续，每块<=2h/同范围最多两块后完整审查，系统性同问题无改善进入诊断，不自动延时/盲升几何。此授权不会使旧未合格Wave/CURB或未训练gate变为完成。

以下138/既有专家与真实路线证据继续有效，预算与复训权限以本005及最新actual优先：
'''
 a=old.index('solecanonical=')
 b=old.index('\n\n004 humanapprovalsidecar',a)
 replacement='''solecanonical=/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json，总1188000s330h/七扩展各一次/005新增360000s已应用。本轮budget登记无PPO不扣，idle676797.5426192284s/SHA__SHA__仅快照，futureactualactive/accounted扣真实未accounted尾段。PPOload/preflight/learn/save/exit原parent唯一同账，不复制追加/clearactive/重tail/重扩展/自动加时，<=120安全余不称0。两真实OS锁canonicalroot/native_floor_supervisor.lock及MOD4_scut_spin_rate_20261002/autonomy_controller.lock以fcntl实际核held，persistent存在非持锁不删。新权仅actualownfullsave/PASSED/旧launch闭合/实际父guardian孩子exit/两锁free/unique段active-Sactive结清。退出尚结账等候不是故障/clear，父故障trainer活跃保护保存修监督，不hotpatch/kill/dual20k/干预其它AI。第七次预算transaction已完成绝不重跑，旧forceexit权限不扩大。'''.replace('__SHA__',applied['after_sha256'])
 updated=leading+old[:a]+replacement+old[b:]
 updated=updated.replace('S3含已用E1 30h/S7conditional18h原规划','S3原含已用E1 30h加005新增地形75h合计105h规划上限/S7conditional18h原条件规划')
 updated=updated.replace('Wave1312b4前22倒25of27七prefix非qualified，不更多900s/升50mm。','Wave1312b4前22倒25of27七prefix非qualified，不盲续旧366900s；005准许新独立诊断修复范围复训，完整实际验收再下一几何轴。')
 assert '\ufffd' not in updated and '总828000s230h' not in updated
 current=D/'MONITOR_CURRENT_BUDGET005_RETRAIN_PROMPT.md'
 with current.open('xb') as f:f.write(updated.encode())
 row=dict(epoch=time.time(),path=str(current),prompt_sha256=H(updated.encode()),prompt_bytes=len(updated.encode()),
  previous_prompt_path=str(previous),previous_prompt_sha256=H(old.encode()),
  automation_fields_preserved={k:x for k,x in metadata.items() if k!='prompt'},
  new_budget_registered=True,expert_retraining_authorized=True,automation_update_pending=True)
 save('MONITOR_PREPARED.json',row)
 print(json.dumps(dict(path=str(current),chars=len(updated),sha256=row['prompt_sha256'],
  name=metadata['name'],rrule=metadata['rrule'],status=metadata['status'],target_thread_id=metadata['target_thread_id'])))


if __name__=='__main__':main()
