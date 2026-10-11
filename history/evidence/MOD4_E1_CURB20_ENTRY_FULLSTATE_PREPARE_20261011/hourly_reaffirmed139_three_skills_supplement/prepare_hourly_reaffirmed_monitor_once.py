"""Apply the latest human cadence request to the same existing heartbeat only."""
from pathlib import Path
import json,time,tomllib,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
assert t['id']=='mod4-10' and t['kind']=='heartbeat' and t['status']=='ACTIVE' and t['rrule']=='FREQ=MINUTELY;INTERVAL=30'
old=t['prompt'];prior=D/'MONITOR_PREVIOUS_30MIN_FINAL_PROMPT.md';new=D/'MONITOR_CURRENT_HOURLY_REAFFIRMED_PROMPT.md';request=R/'MOD4_HOURLY_REAFFIRMED_MONITOR_REQUEST.json'
assert not prior.exists() and not new.exists() and not request.exists();prior.write_text(old,encoding='utf8')
prefix='''最新人类2026-10-11明确要求：“监守调成一小时一次吧”。现有mod4-10同一heartbeat、同一目标任务改为ACTIVE每1小时一次；旧每30分钟/每2小时及旧禁止小时巡检文字仅历史。仅变频，不新增其它驻守/5minSSH/ping/Rich/自动预算，不重跑任何旧once/main/resume/SDK/native/PPO/fresh/record/tag/sync/预算事务，不触碰人类本地WASD播放器。沿用健康或pending DONT_NOTIFY静默，仅实质阶段/真实修复/重大退化/完成/人类动作NOTIFY。本次设置请求、工具回执与实际核验按普通Git补充，非新物理试验或预算扩展。

本轮139只读实际收集已有flat/spin/world三case complete/errorfree，两hostprobe/result JSON byteSHAexact、115/129完整参数初始化合同严格配对已审。source364→own410负4pi7/8→5/8、正仍8/8；world仍63/64、maxcross.050733746m/s；直线±1.5误差.020799875/.046490490m/s，原strictfalse/所有残差保留，不称永久抗遗忘。terrain最后一case尚在原健康worker自然运行/attentionnull是合法pending，review_complete=false；以后actualcomplete优先，不假永久pending，不更多PPO/升高度或称CURB毕业。具体本机reports/CURB139_COLLECTED_1791706365827053100.json及CURB139_SCHEMA_REVIEW_1791706413790143300.json优先于旧flat-only快照，完整terrain结果仍必须全raw/NPZ SHA、132初始化/ground-contact-COMlink/hardware/方向两轮完整侧壁条带200mm后支撑/有效prefix验收。collector/reviewer仅仅读复用，不重任何validcomplete；完整决定后按004005积极合理有界接续或纠正，不无限hold/只留队列。

此前source410 formal完整保存与final/139partial/reader错误/同步/30min监控及阶段Gitreceipt普通supplement已actualremote核验commitb8497f5c501b2f440067f8b54ccf99a45ac508b8，1289旧tag对象与peeled保持、workingtreeclean。后来的139三skill/当前hourly请求与monitor/sync回执仍需普通supplement，以actualtracked/remote最终工具证明，不能凭提示假报补齐；所有未来139complete或新保存报告仍Git。005总1188000秒330h/七扩展、第七100h唯一登记早完成，新增0。以下actualfinal与固定合同继续，只有频率以上述最新每1小时为准：

'''
prompt=prefix+old;new.write_text(prompt,encoding='utf8')
row=dict(epoch=time.time(),id=t['id'],kind=t['kind'],name=t['name'],status='ACTIVE',rrule='FREQ=HOURLY;INTERVAL=1',target_thread_id=t['target_thread_id'],prior_rrule=t['rrule'],human_request='监守调成一小时一次吧',same_existing_heartbeat=True,new_automation_created=False,prior_prompt_string_SHA=H(old.encode()),new_prompt_normalized_string_SHA=H(prompt.replace('\r\n','\n').encode()),new_prompt_path=str(new.resolve()),old_prompt_retained=str(prior.resolve()),no_training_physical_or_budget_action=True,healthy_pending_silent=True)
request.write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(mode='update',id=t['id'],kind=t['kind'],name=t['name'],status='ACTIVE',rrule=row['rrule'],targetThreadId=t['target_thread_id'],prompt=prompt),ensure_ascii=True))
