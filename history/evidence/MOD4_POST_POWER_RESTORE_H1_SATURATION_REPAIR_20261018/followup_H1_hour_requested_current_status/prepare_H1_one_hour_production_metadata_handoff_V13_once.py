"""Capture a requested live status; no model audit or runtime mutation."""
from pathlib import Path
import json,time
from datetime import datetime,timezone,timedelta
B=Path(__file__).resolve().parent;H=B/'hour1_h1_8a7c_v1';R=B/'reports'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 p=H/'reports/H1_ONE_HOUR_HUMAN_STATUS_1646_READONLY_ACTUAL.json';v=json.loads(p.read_bytes());row=v['target']['rows']['NODE_CURRENT.json']['row'];g=v['owner']['rows']['OWNER_CURRENT.json']['go']['h1'];progress=v['target']['rows']['job0/production/OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json']
 assert v['actual_transport_returned'] and row['phase']=='production' and row['worker']['pid']==22790 and progress['completed']==2 and not v['target']['errors'] and not v['owner']['errors']
 assert g['save_deadline']-g['learning_started_epoch']==3600 and g['nominal_end_epoch']-g['learning_started_epoch']==3900
 fmt=lambda e:datetime.fromtimestamp(e,timezone(timedelta(hours=8))).isoformat()
 put(R/'H1_ONE_HOUR_PRODUCTION_METADATA_NOT_FULL_MODEL_AUDIT_V13_ACTUAL.json',dict(epoch=time.time(),source_report=str(p),actual_production_metadata=True,completed_updates_at_snapshot=2,not_mid_hour_checkpoint_model_or_behavior_audit=True,GO=g,worker=row['worker'],started_Beijing=fmt(g['learning_started_epoch']),save_deadline_Beijing=fmt(g['save_deadline']),maximum_lifecycle_Beijing=fmt(g['nominal_end_epoch']),snapshot_not_permanent_alive_or_future_FINAL=True,fresh_CIM_after_collection_known_finite0=True,all_transports_handed_back=True,no_GPU_model_hash_or_budget_mutation=True))
 a=json.loads((B/'AUTOMATION_H1_ONE_HOUR_ACTUAL_HANDOFF_HOURLY_ARGS_V12.json').read_bytes())
 prefix='''最新真实current覆盖V12旧nativepending：人类问“现在正在训练吗”，本次只一次有界只读metadata实核，已进入production。先读R/reports/H1_ONE_HOUR_PRODUCTION_METADATA_NOT_FULL_MODEL_AUDIT_V13_ACTUAL.json与H/reports/H1_ONE_HOUR_HUMAN_STATUS_1646_READONLY_ACTUAL.json。sourceowner110623/create1792311677.47、node22089/create1792311679.18，72GPU0真实productionworker22790/create1792312703.97且nvidia compute同PID14048MiB，自己的native原独立CPU已过后原owner实际GO1792312701.371657=北京时间16:38:21.371657。capture1792313200.758282时phaseproduction、actualcompleted2updates/960000envsteps、target/ownererrors均空，sourcego同一小时方案。save_deadline1792316301.371657=17:38:21.371657，nominal_end1792316601.371657=17:43:21.371657只是完整保存退出安排，不保证未来FINAL/永远alive。没有中途重型PT/firstCPU/冻结审计，未重native、改live或原账。全模型PPOpositive/最终更新数/Adam只在整段保存后完整PT CPU核，不用这次metadata冒完整模型验收或public4辅助效果；前2更新仍normal行actualaux0也不能说整段没aux。只按一小时段自然完成，不在24更新或半小时截停。保持所有原source/physics/hardware/预算/安全保存合同。
本只读collector actual返回且fresh exactargv CIMknownfinite0，root收回transport；未来仍先CIM，仅actualalive自己的finite独占210/72/249，不另SSH/第二watcher。原8a7c冻结/小时任务阶段已唯一record并actualremote/tracked/all1376旧tag核：commitb6e86c0f0f487f584c262279a168424fd44e2dde/tagtrial-20261018-h1-8a7c-review-one-hour-continuation/objectcd220ac51b2b57e724aa948cad9e06c6e19eccb3，共1377tags。V1归档历史manifestalias在任何note/DEST/record前assert拒绝保留，V2只实际新root producer/manifest+旧完整索引修复后成功；两helper均consume，不重run/record/tag/同stagecommit。此后状态请求/工作单/monitor/appreceipt仅ordinary补档，lateractualHEAD/remote/tracked优先，pushfail只已有objects。已向人类回答正在训练与16:38→17:38安排，健康unchanged不重复通知。
以下V12完整scope/一小时合同与所有false/时序证据继续有效，但其中“最新native/go空”只是旧snapshot，不能覆盖上方真实production：
'''
 a['prompt']=prefix+a['prompt'];put(B/'AUTOMATION_H1_ONE_HOUR_ACTUAL_PRODUCTION_HOURLY_ARGS_V13.json',a)
 print(json.dumps(dict(production=True,started=fmt(g['learning_started_epoch']),save_deadline=fmt(g['save_deadline']),updates_at_snapshot=progress['completed'],local_only=True)),flush=True)
if __name__=='__main__':main()
