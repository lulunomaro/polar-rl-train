from pathlib import Path
import json,time,tomllib,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';T=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml')
def main():
 proof=json.loads((R/'LOCAL128_FINAL_FULLTRACE_CLOSEOUT_ACTUAL_REVIEW.json').read_bytes());assert proof['passed']
 attempts=[]
 for p in sorted((D/'attempts').glob('*/EXIT_RECEIPT.json')):
  a=p.parent;exit=json.loads(p.read_bytes());dispatch=json.loads((a/'DISPATCH_RECEIPT.json').read_bytes());assert exit['child_pid']==dispatch['child_pid']
  progress=a/'output/LOCAL_PPO_PROGRESS.json';pp=json.loads(progress.read_bytes()) if progress.exists() else None
  rows=dict(attempt=a.name,parent_wall_seconds=exit['wall_seconds'],mode=exit['actual_mode'],exit_code=exit['exit_code'],child_pid=exit['child_pid'],child_start=dispatch['child_create_time'],actual_PPO_updates=pp['actual_updates'] if pp else 0,canonical_reconciliation_pending=exit['actual_mode']=='train',native_SDK_fullrestore0PPO_not_charged=exit['actual_mode']!='train',failed_learning_startup_cost_retained=exit['actual_mode']=='train' and not pp,parent_EXIT_actual_path=str(p))
  attempts.append(rows)
 costs=[a for a in attempts if a['mode']=='train'];assert len(costs)==3 and sum(a['actual_PPO_updates'] for a in costs)==43
 p=R/'LOCAL_TEMP_ALL_ATTEMPTS_COST_CLASSIFICATION_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),passed=True,attempts=attempts,unique_training_startup_attempts=len(costs),all_actual_parent_loadlearnsaveexit_seconds=sum(a['parent_wall_seconds'] for a in costs),parent_unique_ID_is_childPID_start_not_filename=True,v8_real2PPO_failedsave_preserved=True,v9_failed0PPO_learning_startup_cost_retained=True,v10_real41PPO_finalpassed=True,worker_pre_teardown_cost_not_added_to_parent_cost=True,canonical_reconciliation_pending=True,no_canonicalwrite_copy_refund_or_second_authority=True),ensure_ascii=False,indent=2),encoding='utf8')
 cfg=tomllib.loads(T.read_text(encoding='utf8'));assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1'
 old=D/'MONITOR_PREVIOUS_LOCAL_V10_ACTIVE_BEFORE_FULLFINAL.md';assert not old.exists();old.write_text(cfg['prompt'],encoding='utf8')
 prompt=f'''最新本机actual优先：临时128env v10窗口已在2026-10-13约04:42+08自然完整保存退出，不再active，不能把旧4/22更新快照套永久活动。ownfinal model32305 SHA97361dff5410a325094f8219d6afabe443dabd30331108bd27d4d73969ecfc89/1418935B/107floating/原d05c源20k→128显式本机后端分支、v8 retained同128来源。41updates984controls125952envsteps3936callbacks，actor9changed/optimizerdelta820/12CPUCUDAstartup和episode+1实际passed。ordinary/integrity/unknown0/nonfinitefalse/STOPnone，closure.712992332mm/mimic.001691456rad，time_out50/route40/unique90两coverageexact；原父EXIT0、actual父27780/孩子27316-create1791835930.1418393均已实际退出、msvcrtOSlockfree，不按persistentfile存在判held。合法temporary_saved_review_ready，非故障/全课程结束/50mm毕业。

先读{R}/LOCAL128_FINAL_FULLTRACE_CLOSEOUT_ACTUAL_REVIEW.json与LOCAL_TEMP_ALL_ATTEMPTS_COST_CLASSIFICATION_ACTUAL.json、ownLOCAL_PPO_FORMAL_FINAL_ACTUAL/LOCAL_LATEST_COMPLETE/EXIT_RECEIPT。21份NPZ全984×128×16 finite、连续control coverage、非reset前后root exact、episode增量与raw90resetexact/方向-route-lifetime boundepisodeexact；动态currentrootcellfamily4且bornWave19，两signedtoward/standing9840/5904/2952，原站立无需通行。beforephysicscommand与afterupdatehist不同phase不强行一致。最长新物理episodeprefix仅9.84s/env，rootcommandproxy不是双轮contact/full十波/因果或通过性改善证书。source459d05c原19043064B再次SHA核未改。50/70不合格，原459四4090评测raw保存但完整行为复审仍pending。

本窗口已完成，无新训练授权派生；不自动更多PPO/重v10/oldmain-resume-once/新GPU评测/70mm/其它expert，不恢复远端暂停。人类有新的明确继续或评测指令再依实际保存边界独立准入；当前健康idle DONT_NOTIFY，不反复生成相同健康报告或重复通知completed。仅读已有完成报告/actualPIDcreationargv与msvcrt边界；read_local_training_actual.py仅真实状态变化需要时复用，保存的新report照常补Git，不能凭过期guardianchild_runningtrue报故障或重启。

成本原三字段分列不改：workerformal1827.568517923355s、workerENDED1827.5745396614075s均在Kit退出前；原parentEXIT1830.2517688274384s含loadlearnsaveexit，未来原canonical唯一对账以parent实际段为准，不相加/复制重扣/退款。v8真实2PPO但fsync失败的完整retainedownsave、v9缺proof0PPO学习启动原成本均保留，原native/SDK/fullrestore0PPO不计。0051188000/七扩展早once原canonical远端对账仍pending，本轮不SSH/写canonical/clearactive/tail/recharge/新预算；本机记录只是actualcost证据不第二权威。不要将初STARTED.no_PPOtrue快照套已实际41更新，也不把原worker成本字段改成完整parentEXIT。

原registry/8和9失败/所有false/raw/原TOMLtargetkey和读取heldlockPermissionError错误保持，最终补档用既有stage的ordinarysupplement，无新trial/重recordtagcommit。全部ownfinal/21traceSHA/cost/新observer源码/监控更新和native回执补Git，具体remote main/tag/peeled/tracked核验actual优先不凭此提示假完成；后Gitreceipt也supplement，大PTNPZUSDZIPdump只actualpathsizeSHA原件保留，credentials不输出Git。

mod4-10同heartbeatACTIVE每1h同target。仅本机获恢复授权，远端正式训练/评测继续暂停，不SSH/ping3060或4090、不恢复旧入口/预算事务。健康DONT_NOTIFY，仅新实质阶段/真实修复/重大退化/完成/人类动作NOTIFY。无额外驻守/5minmonitor/自动加时，单窗口reviewready不删监守，仅真正预算结束且allfinal全完成才停止。WASD不GUI/reset/stop/restart。全部DRrewardLRclocksolverhardwarequery-contact-COMhealth容差与其它E0/35/CURB/SLOPE冻结、gate未训/S8另批准保持。上一完整固定合同和全部本机适配原失败追溯{old} SHA{hashlib.sha256(old.read_bytes()).hexdigest()}，之后actual/newhuman优先。
'''
 q=R/'LOCAL_FINAL_HOURLY_MONITOR_UPDATE_REQUEST.json';assert not q.exists();q.write_text(json.dumps(dict(id='mod4-10',mode='update',kind='heartbeat',name=cfg['name'],status='ACTIVE',rrule=cfg['rrule'],targetThreadId=cfg['target_thread_id'],prompt=prompt),ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(dict(passed=True,request=str(q),cost_attempts=len(costs),parent_seconds=sum(a['parent_wall_seconds'] for a in costs))))
if __name__=='__main__':main()
