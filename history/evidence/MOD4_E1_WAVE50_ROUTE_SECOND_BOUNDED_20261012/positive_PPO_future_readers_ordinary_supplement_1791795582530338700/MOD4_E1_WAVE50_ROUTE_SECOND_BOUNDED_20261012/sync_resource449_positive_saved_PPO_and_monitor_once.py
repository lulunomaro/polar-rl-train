from route_second_io import *
import tomllib

def main():
    assert not (R/'RESOURCE449_POSITIVE_SAVED_PPO_METADATA_SYNCED.json').exists()
    p=max(R.glob('RESOURCE449_OWN_SAVED_PPO_CPU_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));proof=json.loads(p.read_bytes());assert proof['actual_PPO_saved_CPU_verified'] and proof['startup_passed']
    stamp=str(time.time_ns());n,w=io.connect_both()
    try:
        with n.open_sftp() as f:
            ref=io.E+'/reports/WAVE50_ROUTE449_OWN_SAVED_PPO_CPU_VERIFIED_'+stamp+'.json';io.put(f,ref,p.read_bytes())
            work=io.E+'/reports/NEXT_WAVE50_ROUTE449_OWN_FINAL_CANDIDATE_ACTUAL_WORK_ORDER_'+stamp+'.md';io.put(f,work,(D/'NEXT_RESOURCE449_OWN_FINAL_CANDIDATE_ACTUAL_WORK_ORDER.md').read_bytes())
            raw=f.open(io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json','rb').read();old=H(raw);v=json.loads(raw)
        rev=v['terrain_subexpert_revision004'];s=rev['wave50_route_startup_resource_reviewed_scope'];assert s['source_count']==449 and s['selected_source_SHA']==INIT_SHA
        s.update(actual_GPU_startup_fullstate_and_PPO_proof_pending=False,ten_actual_same_scope_startup_receipts_passed=True,own_positive_saved_PPO_CPU_ref=ref,own_activity_checkpoint=proof['own_checkpoint'],own_activity_PID=proof['own_PID'],activity_actor_tensors_changed=proof['actual_actor_tensors_changed'],activity_optimizer_step_delta=proof['optimizer_step_delta_min'],activity_saved_trace_controls=proof['saved_trace_controls'],own_formal_final_pending=True,activity_checkpoint_not_final_or_qualified=True,next_work_order=work)
        rev['active_next_phase']='WAVE50_route449_sameidentity_startup_passed_own_saved_PPO_CPU107_positive_active'
        nxt=io.E+'/reports/RESOURCE449_POSITIVE_PPO_CURRENT_'+stamp+'.json'
        with n.open_sftp() as f:io.put(f,nxt,json.dumps(v,ensure_ascii=False,indent=2).encode())
        result=run(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(E_TOKEN)/'reports';p=R/'MOE_PLAN_EXECUTION_CURRENT.json';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();protected={k:(R/k).read_bytes() for k in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')};assert h(p)==OLD_TOKEN
tmp=p.with_name('RESOURCE449_POSITIVE_'+str(time.time_ns())+'.tmp');tmp.write_bytes(Path(NEXT_TOKEN).read_bytes());assert h(p)==OLD_TOKEN;os.replace(tmp,p);assert all((R/k).read_bytes()==v for k,v in protected.items())
result=dict(epoch=time.time(),passed=True,current_SHA=h(p),own_positive_saved_PPO_CPU107_and_ten_same_identity_startup_synced=True,master_approval_tracks_RM004_bytes_exact=True,canonical_not_written=True)
out=R/('WAVE50_ROUTE449_POSITIVE_SAVED_PPO_METADATA_SYNCED_'+STAMP_TOKEN+'.json');assert not out.exists();out.write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''.replace('E_TOKEN',repr(io.E)).replace('OLD_TOKEN',repr(old)).replace('NEXT_TOKEN',repr(nxt)).replace('STAMP_TOKEN',repr(stamp)))
        save('RESOURCE449_POSITIVE_SAVED_PPO_METADATA_SYNCED.json',result)
    finally:io.cleanup(n,w)
    settings=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    oldprompt=D/'MONITOR_PREVIOUS_RESOURCE449_STARTUP_PENDING.md';assert not oldprompt.exists();oldprompt.write_text(settings['prompt'],encoding='utf8')
    prefix=f'''最新补充actual优先：source449自己的same50-entry-direction-route第二1800s窗口已实际PPO更新，非仅进程。自己的活动保存model32275 SHA{proof['own_checkpoint']['sha256']}/actualCPU107/source449/tenstartup strictsame50-entry-direction-route CPUCUDA磁盘roundtrip/sourceepisode+1全部通过，9actor tensors改变/optimizerdelta240.0/savedtrace288controls已仅读ownCPU核。活动保存不是formal final/qualified50。中央WAVE50_ROUTE449_OWN_SAVED_PPO_CPU_VERIFIED/POSITIVE_SAVED_PPO_METADATA_SYNCED与current.rev004.wave50_route_startup_resource_reviewed_scope；本机{p}及未来RESOURCE449_OWN_FORMAL/候选四caseactual/fulltrace优先，不套旧446failed或449startupmissing永久状态。verify_resource449_own_saved_PPO_cpu_actual.py仅读正常通过。

新未来仅读read_resource449_own_formal_actual.py/collect_resource449_candidate_actual.py/review_resource449_candidate_actual.py/review_resource449_direct152_prefix_actual.py/review_resource449_complete_dynamic_family_trace_actual.py均已独立准备compile，准备非futurepass；按实际stage严格完整ownfinal/退出两锁唯一结清/四casequeryraw/contactCOMhardware/全signedcircle原false/完整dynamicfamilytrace及direct152审，详见NEXT_WAVE50_ROUTE449_OWN_FINAL_CANDIDATE_ACTUAL_WORK_ORDER。不得盲发153或重任何validcomplete/failed/oldonce。初443300+本4491800最多两learning块后fullaudit，不第三盲块/70/无限hold/只队列。失败4460PPO独立3466.325003385544s原parent一次扣保持，不退款/重结/clearactive。

本轮cleanup719+446failure保留+新449resource-reviewed dispatch stage trial-20261012-old719-cleaned-route446-failure-preserved-new449-started commit6eb0ce289fc34f3ee73feca55630c7e06a35b914/tagobject23c99e2e29fc042fb1b49ad8a016f9b86410c4c8已actualremote main/tag/peeled核验，250savedsource/1309oldtags保持；stage后新positiveCPU/未来preparedreaders/工作单/sync/monitor/Gitreceipt仍ordinarysupplement，以后来actualtracked/remote最终工具为准不能凭prompt假补齐。原446Source/error/卡退出/精确人类PID终止两signal/partialbytesreceipt与独立reader修复全部保留，不再复跑；human719清理与exactPID3340979终止授权均已用，不扩展未来delete/kill。source684/accepted35/CURB20/SLOPE/E0/gate/WASD/fixedDRrewardclockhardwarehealth/005唯一预算与全部下文合同保持。

旧449startup-pending全文{oldprompt} SHA{H(oldprompt.read_bytes())}追溯；以下旧pending仅历史，以上及之后ownactual优先：

'''
    save('RESOURCE449_POSITIVE_PPO_MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=settings['name'],rrule=settings['rrule'],status='ACTIVE',targetThreadId=settings['target_thread_id'],prompt=prefix+settings['prompt']))
    print(json.dumps(dict(passed=True,monitor_request=str(R/'RESOURCE449_POSITIVE_PPO_MONITOR_UPDATE_REQUEST.json'))))

if __name__=='__main__':
    try:main()
    except BaseException:save('RESOURCE449_POSITIVE_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_sync_GPU_or_budget_replay=True));raise
