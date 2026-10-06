"""Publish actual failure precedence and the new isolated authority without changing old freezes."""
from pathlib import Path
import json,sys,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent;E=W/'MOD4_MOE_PLAN_EXECUTION_20261007/reports';REPO=W/'polar-rl-train'
OUT=R/'DT2000_LONGRUN_REJECTION_PUBLISHED.json';assert not OUT.exists()
read=lambda p:json.loads(p.read_text(encoding='utf8'))
a=read(R/'DT2000_LONGRUN_FAILURE_AUDIT.json');v=read(R/'CLOCK1000_CURRENT_ACTUAL.json');launch=read(R/'CLOCK1000_WORKER_REVIEW_LAUNCHED.json')
assert v['owner'] and v['owner']['start_ticks']==launch['owner']['start_ticks'] and not v['reports']['SELECTED_CLOCK_ATTENTION.json']
sdk=v['reports']['ALIGNED_SDK_PASSED.json'];assert sdk['physical_task_passed'] and sdk['clock']['physics_dt_s']==.001
event=read(R/'DT2000_BASELINE_SUSPENDED.json');event.update(current_fallback_root=launch['root'],current_source_count=189,
 current_owner=launch['owner'],actual_current_phase=v['phase'],aligned_SDK_passed=sdk,
 worker_manifest_review=read(R/'WORKER_WORKER_MANIFEST_REVIEW.json'),SDK_repeated=False,new_1ms_PPO_not_yet_observed=v['active_segment'] is None)
doc=REPO/'history/plans/MOD4_DT2000_LONGRUN_REJECTION.json';doc.write_text(json.dumps(event,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
text='''# 2 ms长段故障与已批准1 ms回退执行记录

本记录优先于此前“2 ms健康固化”的时点快照。主计划v1.5及原补充SHA不改；人类的固化指令以“健康”为条件，真实故障发生后按原计划既有回退条款执行，不放宽2 mm闭链检查。

实际2 ms A0在367次完整PPO更新、8808控制步/1.7616亿环境策略步后出现一个环境的真实任务终止；session最大闭链误差2.134397 mm，mimic1.953125 mrad。自动请求自己的STOP_AFTER_SAVE，完整23875保存SHA5dbcb191fb15d07fcbe6e74e1cba90abe0e78c89345b27ba8d227b3eb3aac09c/CPU68有限，父、guardian和trainer均退出。实际加载/学习/保存/退出2181.462239秒只结账一次，active与S.active_training空。此前短物理和完整4轮PPO证据有效保留，但不足以证明长段稳定；未隔离证明故障只由dt引起。

当前采用新的隔离1 ms候选，不复活旧1 ms入口，不用失败23875或预检权重作源。保持100 Hz控制、原5 ms接触bin、solver16/4、20k×24和原PPO/任务/white_v3/名义硬件。原23509完整actor/critic/optimizer/std/iter KEEP_STD1作为唯一明确初始化。1 ms恰好5个物理样本一bin，使用原aligned积分路径；未改变接触、闭链或硬件门槛。

新的10env3秒SDK已实际通过：3240真实回调、选中reset一次、其他行和global clock不变；独立平均力历史误差2.74659e-5 N、控制冲量误差2.84195e-7 N·s、闭链最大0.251497 mm。此证据不是20k/PPO或能力毕业。

首个187来源部署缺少命名native worker文件，解释器在Kit/动态步/PPO前退出；原错误与现场保留。已用新189来源隔离接续明确补齐worker路径，原187逐字相同，完整SDK按SHA复用，未重复测量或结账。当前唯一入口为MOD4_PHYSICS_DT1000_WORKER_REVIEW_20261007/continue_clock1000_worker_manifest_review_once.py。它独立取得同canonical两锁，先20k短物理，再原23509的flat/spin/world15秒参数与完整root/q回归，必要128×2/20k×4完整PPO，丢弃预检权重；真正通过后首45min有界A0适应。同S1A6h上限及全部已有成本保留。若新范围只有有限性能小残差，按原授权实际审查；真实模型/任务/数据失败不能忽略。

目前1 ms正式训练和成熟能力尚未确认。后续A0/A1/A2在同最终健康时钟、同23509、相同命令/DR/seed和实际匹配更新量比较。既有22项历史/encoder CPU证明保留，真实SDK标签/cache/reset/critic及新架构PPO仍待完成，不称MoE已部署。3060旧0.5 ms结果保持原scope；新最终时钟评测包另校准，不阻塞4090自己已验证范围。

总828000秒230h及六次既有扩展不变；本次没有新时间、清账本、重复结尾段或强杀。首次账本读者误用不存在的charged_seconds字段，仅只读schema错误，已按唯一completed segment起止时间正确审计，非生产故障。两小时监控保持，按真实phase/receipt推进，不把review_ready当毕业或强制父永远活跃。
'''
(REPO/'history/plans/MOD4_DT2000_LONGRUN_REJECTION.md').write_text(text,encoding='utf8')
contract=REPO/'history/plans/MOD4_MOE_EXECUTION_CONTRACT.json';cc=read(contract)
cc['locked_training_baseline'].update(status='SUSPENDED_AFTER_ACTUAL_LONGRUN_TASK_FAILURE',actual_failure_document='history/plans/MOD4_DT2000_LONGRUN_REJECTION.json',not_current_healthy_training_clock=True)
cc['actual_clock_failure']=event
cc['execution_state']=dict(stage='S0P/S1A',status='ISOLATED1MS_VALIDATION_AFTER_ACTUAL2MS_FAILURE',runtime_root=launch['root'],source_count=189,actual=v['phase'],encoder_training_pending=True)
contract.write_text(json.dumps(cc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
tracks=read(E/'EXECUTION_TRACKS.json');tracks['physics_performance'].update(current_fallback_root=launch['root'],current_source_count=189,actual_phase=v['phase'],new_candidate_not_adopted=True,aligned_SDK_passed=sdk)
tracks['learning'].update(root=launch['root'],actual_phase=v['phase'],actual_new_owner=launch['owner'],status='1ms native/old-skill/PPO checks pending before bounded A0; original2ms stopped and preserved')
(E/'EXECUTION_TRACKS.json').write_text(json.dumps(tracks,indent=2),encoding='utf8')
handoff=E/'LATEST_HANDOFF.md';handoff.write_text(handoff.read_text(encoding='utf8')+'\n\n'+text,encoding='utf8')
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as s:
  er='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/'
  for p in [doc,doc.with_suffix('.md'),contract,E/'EXECUTION_TRACKS.json',handoff]:
   s.put(str(p),er+p.name+'.failure_review');s.posix_rename(er+p.name+'.failure_review',er+p.name)
   with s.open(er+p.name,'rb') as f:assert hashlib.sha256(f.read()).digest()==hashlib.sha256(p.read_bytes()).digest()
  s.put(str(handoff),launch['root']+'/reports/LATEST_HANDOFF.md')
finally:c.close()
OUT.write_text(json.dumps(dict(epoch=time.time(),current_root=launch['root'],actual_stage=v['phase'],approved_master_SHA_unchanged=True,new_budget_seconds=0),indent=2),encoding='utf8')
print(OUT)
