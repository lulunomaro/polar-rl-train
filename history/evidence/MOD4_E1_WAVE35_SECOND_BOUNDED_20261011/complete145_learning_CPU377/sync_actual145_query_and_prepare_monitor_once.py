from second_io import *
import tomllib

def main():
    q=json.loads((R/'WAVE50_145_ACTUAL_QUERY_COMPONENT_REVIEW.json').read_bytes());assert q['passed'] and q['component_only_not_fullroute_or_scope_graduation']
    n,w=io.connect_both()
    try:
        z=run(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(CENTRAL_TOKEN)/'reports';B=Path(BUDGET_TOKEN);budget=B.read_bytes();q=json.loads((R/'E1_WAVE50_145_ACTUAL_QUERY_COMPONENT_REVIEW.json').read_bytes())
assert q['passed'] and q['actual_GPU_query_max_error_m']<=1e-6 and q['component_only_not_fullroute_or_scope_graduation']
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();c=json.loads(before);v=c['terrain_subexpert_revision004'];s=v['wave50_worldmesh_query_scope'];assert s['job_id']==q['job_id']
s.update(actual_query_component_passed=True,actual_query_component_report=str(R/'E1_WAVE50_145_ACTUAL_QUERY_COMPONENT_REVIEW.json'),actual_GPU_query_max_error_m=q['actual_GPU_query_max_error_m'],actual_GPU_vs_ideal_profile_difference_m=q['actual_GPU_vs_ideal_profile_difference_m'],phase='WAVE50_actual_worldmesh_query_passed_fullroute_review_pending',full_raw_review_pending=True)
v['active_next_phase']=s['phase'];assert p.read_bytes()==before;tmp=p.with_name(p.name+'.ACTUAL145QUERY-'+str(time.time_ns()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2));os.replace(tmp,p);assert B.read_bytes()==budget
z=dict(epoch=time.time(),metadata_synced=True,job_id=q['job_id'],actual_query_component_passed=True,full_raw_review_pending=True,canonical_SHA=hashlib.sha256(budget).hexdigest(),no_GPU_PPO_budget_transaction=True)
p=R/'E1_WAVE50_145_ACTUAL_QUERY_METADATA_SYNCED.json';assert not p.exists();p.write_text(json.dumps(z,indent=2));print(json.dumps(z))
'''.replace('CENTRAL_TOKEN',repr(io.E)).replace('BUDGET_TOKEN',repr(io.B)))
        save('WAVE50_145_ACTUAL_QUERY_METADATA_SYNCED.json',z)
    finally:io.cleanup(n,w)
    t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert t['rrule']=='FREQ=HOURLY;INTERVAL=1' and t['status']=='ACTIVE'
    old=D/'MONITOR_PREVIOUS_145_QUERY_PENDING_PROMPT.md';assert not old.exists();old.write_text(t['prompt'],encoding='utf8')
    prefix=f'''最新145 actual初始化query优先：已实际独立CPU重审GPU落盘worldmesh_query NPZ，80cell全部actualfloat32world triangles/procedural triangles byteexact、独立expectedheight exact；actual_GPU_query_max_error_m=3.077315561695465e-7<=原1e-6，actual_GPU_vs_ideal_profile_difference_m=2.7057948894723682e-6。仅此新145实际组件测得，144失败GPU数值未落盘仍不伪称测得。读中央E1_WAVE50_145_ACTUAL_QUERY_COMPONENT_REVIEW/ACTUAL_QUERY_METADATA_SYNCED和本机WAVE50_145_ACTUAL_QUERY_COMPONENT_REVIEW；current.rev004.wave50_worldmesh_query_scope.actual_query_component_passed=true，full_raw_review_pending=true。初始化pass不替全路线或50mm毕业，下一继续actualcomplete/errorfree两hostJSONbyteSHA/fullterrainNPZ/queryNPZ及完整6000callback接触COMhardware/两轮全十波+200mm后支撑审；任何后来actualfullreview/完整决定优先，不按旧querypending或活动PID永久套状态。

新145修复真实stage trial-20261012-wave50-worldmesh-query-failure-preserved-independent145-deployed commit903067044c52dc592229da7f34a4b12c20dc90ed/tagobject87476bff193a9054e0e9c1bf23b6cc632b857a79已actualremote main/tag/peeled核验，249savedsource与所有oldtagobjects保持。之后新query/collection/current/metadata/monitor/Gitreceipt继续ordinarysupplement，具体actualtracked/remote最终工具优先不凭prompt假完成。上一145querypending监控全文在{old} SHA{H(old.read_bytes())}，下面旧快照只历史，固定合同继续。

'''
    prompt=prefix+t['prompt'];p=D/'MONITOR_CURRENT_145_ACTUAL_QUERY_PROMPT.md';assert not p.exists();p.write_text(prompt,encoding='utf8')
    req=dict(id='mod4-10',mode='update',kind='heartbeat',name=t['name'],rrule=t['rrule'],status='ACTIVE',targetThreadId=t['target_thread_id'],prompt=prompt)
    save('WAVE50_145_ACTUAL_QUERY_MONITOR_UPDATE_REQUEST.json',req);print(json.dumps(dict(request=str(R/'WAVE50_145_ACTUAL_QUERY_MONITOR_UPDATE_REQUEST.json'),query_passed=True,full_raw_review_pending=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('WAVE50_145_QUERY_SYNC_MONITOR_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
