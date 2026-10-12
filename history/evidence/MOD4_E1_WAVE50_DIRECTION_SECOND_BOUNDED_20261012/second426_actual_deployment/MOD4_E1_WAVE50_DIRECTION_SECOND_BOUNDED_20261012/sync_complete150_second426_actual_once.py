"""Append new actual full150/426 evidence and update current metadata by CAS only."""
from wave_direction_second_io import *
import tomllib

def latest(folder,pattern):return max(folder.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))

def main():
    assert not (R/'COMPLETE150_SECOND426_METADATA_SYNCED.json').exists()
    r0=PRIOR/'reports';cp=latest(r0,'DIRECTION_CANDIDATE_COLLECTED_[0-9]*.json');rp=latest(r0,'DIRECTION_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json');dp=latest(r0,'DIRECTION_DIRECT149_PREFIX_ACTUAL_[0-9]*.json')
    review=json.loads(rp.read_bytes());decision=json.loads((r0/'CANDIDATE150_COMPLETE_SCOPE_DECISION.json').read_bytes());assert review['review_complete'] and decision['all_four_actual_complete_errorfree_fullraw_reviewed']
    ap=latest(R,'SECOND_DIRECTION_ACTUAL_[0-9]*.json');actual=json.loads(ap.read_bytes());cpu=json.loads((R/'DIRECTION_SECOND_TARGET_CPU_PASSED.json').read_bytes());dispatch=json.loads((R/'DISPATCH_ACTUAL_RECEIPT.json').read_bytes());assert cpu['passed'] and cpu['source_count']==426 and dispatch['actual_Popen_argv_cwd_start_verified']
    assert actual['actual_owner'] and actual['actual_child'] and actual['reports'].get('E1_ATTENTION.json') is None
    markers=actual['runs'][0]['startup_markers'];assert len(markers)==9 and all(x['source_sha256']==SOURCE_SHA for x in markers.values())
    t=markers['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'];e=markers['E1_WAVE50_ENTRY_STARTUP_VERIFIED.json'];d=markers['E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json'];c=markers['E1_COMMAND_RETENTION_STARTUP_VERIFIED.json']
    assert t['terrain_state_restored_exact'] and not t['explicit_G3_to_WAVE50_geometry_transition'] and not t['explicitly_new_E1_terrain'] and t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and t['E1_episode_incremented_once']
    assert e['passed'] and e['same_entry_identity_restored_exact'] and not e['explicit_new_entry_scope'] and e['actual_entry_terrain_command_CUDA_disk_roundtrip_exact']
    assert d['passed'] and d['predecessor_direction_state_restored_exact'] and not d['explicit_new_episode_direction_scope'] and d['actual_CUDA_direction_disk_roundtrip_exact'] and d['saved_source_episode_plus_one_verified']
    assert c['predecessor_command_state_restored_exact'] and not c['explicitly_new_command_scope'] and c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and c['saved_source_episode_plus_one_verified']
    proof=save('SECOND_DIRECTION_OWN_STARTUP_CONTRACT_VERIFIED.json',dict(epoch=time.time(),passed=True,source_SHA=SOURCE_SHA,source_count=426,own_actual_child=actual['actual_child'],nine_startup_receipts_same50_entry_direction_strict=True,actual_CUDA_disk_roundtrip_source_episode_plus_one=True,actual_source_collection=str(ap),activity_is_not_final_or_qualified=True,PPO_changes_require_own_saved_CPU_evidence=True,no_GPU_or_budget_write=True))
    stamp=str(time.time_ns());names={
      'E1_WAVE50_DIRECTION150_COMPLETE_ACTUAL_COLLECTION_'+stamp+'.json':cp,
      'E1_WAVE50_DIRECTION150_COMPLETE_ACTUAL_REVIEW_'+stamp+'.json':rp,
      'E1_WAVE50_DIRECTION150_DIRECT149_PREFIX_ACTUAL_REVIEW_'+stamp+'.json':dp,
      'E1_WAVE50_DIRECTION150_COMPLETE_SCOPE_DECISION_'+stamp+'.json':r0/'CANDIDATE150_COMPLETE_SCOPE_DECISION.json',
      'E1_WAVE50_DIRECTION150_FEEDBACK_READER_NAMESPACE_REVIEW_'+stamp+'.json':r0/'FEEDBACK_READER_NAMESPACE_ACTUAL_REVIEW.json',
      'E1_WAVE50_DIRECTION_SECOND_BOUNDED_TARGET_CPU_VERIFIED_'+stamp+'.json':R/'DIRECTION_SECOND_TARGET_CPU_PASSED.json',
      'E1_WAVE50_DIRECTION_SECOND_BOUNDED_SOURCE_FREEZE_'+stamp+'.json':R/'SOURCE_FREEZE.json',
      'E1_WAVE50_DIRECTION_SECOND_BOUNDED_ACTUAL_SOURCE_REUSE_'+stamp+'.json':R/'REUSED_ACTUAL_CONTRACTS.json',
      'E1_WAVE50_DIRECTION_SECOND_BOUNDED_DISPATCH_ACTUAL_RECEIPT_'+stamp+'.json':R/'DISPATCH_ACTUAL_RECEIPT.json',
      'E1_WAVE50_DIRECTION_SECOND_BOUNDED_CURRENT_ACTUAL_'+stamp+'.json':ap,
      'E1_WAVE50_DIRECTION_SECOND_BOUNDED_OWN_STARTUP_CONTRACT_VERIFIED_'+stamp+'.json':proof,
      'E1_WAVE50_DIRECTION_SECOND900_RESOURCE_ACTUAL_'+stamp+'.json':R/'OLD424_BOUNDARY_AND_SECOND900_RESOURCES_ACTUAL.json',
      'E1_WAVE50_SCUT_PERFECT_GATE_COMPARISON_'+stamp+'.json':R/'SCUT_WAVE_GATE_SOURCE_AND_ACTUAL_COMPARISON.json',
      'E1_WAVE50_SCUT_GATE_COMPARISON_'+stamp+'.md':D/'SCUT_WAVE_GATE_COMPARISON.md'}
    n,w=io.connect_both()
    try:
        with n.open_sftp() as f:
            for name,p in names.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
            raw=f.open(io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json','rb').read();sha=H(raw);current=json.loads(raw)
        ref=lambda fragment:io.E+'/reports/'+next(x for x in names if fragment in x)
        rev=current['terrain_subexpert_revision004'];s=rev['wave50_direction_candidate150_actual_scope']
        s.update(complete_cases=4,pending=[],four_case_fullreview_pending=False,forward_complete=12,reverse_complete=25,not_qualified50_RM_or_MoE=True,current_collection_ref=ref('150_COMPLETE_ACTUAL_COLLECTION'),current_review_ref=ref('150_COMPLETE_ACTUAL_REVIEW'),direct149_ref=ref('150_DIRECT149'),scope_decision_ref=ref('150_COMPLETE_SCOPE_DECISION'),one_reviewed_second_direction_block_authorized=True)
        rev['wave50_direction_second_bounded_scope']=dict(root=ROOT,source_count=426,initialsourceSHA=SOURCE_SHA,original35_b026_129_lineage_preserved=True,target_fullstate_CPU_passed=True,nine_ownstartup_same50_entry_direction_CUDA_roundtrip_episode_plus_one_passed=True,chosen_window_seconds=900,maximum_authorized_seconds=1800,resource_1800_rejection_preserved=True,resource900_actual_same_format_2x_output_plus2GiB_passed=True,actual_dispatch_receipt=dispatch,current_actual_ref=ref('BOUNDED_CURRENT_ACTUAL'),startup_ref=ref('OWN_STARTUP_CONTRACT'),phase=actual['reports']['E1_STATE.json']['phase'],own_saved_PPO_changes_not_yet_CPU_verified=True,own_formal_final_pending=True,no_GPU_admission_replay=True,no_third_blind_duration_block_or70=True)
        rev['wave50_progression_threshold_source_review']=dict(comparison_ref=ref('SCUT_PERFECT_GATE'),approved_RM003_no_artificial_90_95_100_gate=True,previous_assistant27_each_hard_gate_wording_corrected=True,fullroute_support_data_integrity_contracts_unchanged=True,oldfalse_raw_cost_kept=True,no_actual_performance_qualification_inferred=True)
        rev['active_next_expert']='E1_WAVE';rev['active_next_phase']='WAVE50_same_entry_direction_second900_bounded_learning';rev['latest_actual_scope']='wave50_direction_second_bounded_scope'
        nxt=ROOT+'/reports/COMPLETE150_SECOND426_CAS_NEXT_'+stamp+'.json'
        with n.open_sftp() as f:io.put(f,nxt,json.dumps(current,ensure_ascii=False,indent=2).encode())
        v=run(n,r'''from pathlib import Path
import json,time,hashlib,os
D=Path(ROOT_TOKEN);R=Path(E_TOKEN)/'reports';B=Path(B_TOKEN);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected={k:(R/k).read_bytes() for k in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';assert h(p)==SHA_TOKEN;before=h(B);raw=Path(NEXT_TOKEN).read_bytes();tmp=p.with_name('CURRENT_complete150_second426_'+str(time.time_ns())+'.tmp');tmp.write_bytes(raw);assert h(p)==SHA_TOKEN;os.replace(tmp,p);assert all((R/k).read_bytes()==v for k,v in protected.items())
v=dict(epoch=time.time(),passed=True,complete150_and_actual_second426_synced=True,current_SHA=h(p),canonical_SHA_before=before,canonical_SHA_after=h(B),canonical_not_written_by_sync=True,master_approval_tracks_RM004_exact=True,no_GPU_or_oldonce_replay=True)
for q in (D/'reports/COMPLETE150_SECOND426_METADATA_SYNCED.json',R/('E1_WAVE50_COMPLETE150_SECOND426_METADATA_SYNCED_'+STAMP_TOKEN+'.json')):
 assert not q.exists();q.write_text(json.dumps(v,indent=2))
print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('E_TOKEN',repr(io.E)).replace('B_TOKEN',repr(io.B)).replace('SHA_TOKEN',repr(sha)).replace('NEXT_TOKEN',repr(nxt)).replace('STAMP_TOKEN',repr(stamp)))
        save('COMPLETE150_SECOND426_METADATA_SYNCED.json',v)
    finally:io.cleanup(n,w)
    setting=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert setting['status']=='ACTIVE' and setting['rrule']=='FREQ=HOURLY;INTERVAL=1'
    old=D/'MONITOR_PREVIOUS_FULL150_BEFORE_SECOND426_PROMPT.md';old.write_text(setting['prompt'],encoding='utf8')
    prefix=f'''最新actual优先：150四case已经complete/errorfree/twohost8JSONbyteSHA/fullraw182821946B SHA2452d4c4c36a2cfc0d32aa3f14c17ded7ba2477b3d3ccfd2c9a8fed2e2aaffc7/queryNPZ/原6000callbacks-ground1e-6-contact积分COMhardware完整审，正12/27倒25/27/ordinary0/route4/closure1.195710502mm，direct149位置与原1N前后支撑一致，全部15forward+2reverse有效prefix/oldfalse/raw/cost保持。未qualified50；左右4pi负0/8正7/8、world63/64/maxcross.051384614/直线负正1.5误差.066174537/.045016099，E0冻结/gate未训。旧150partial/pending是历史。

已真正唯一部署same50+entry+episode-direction第二有界900s窗口：root={ROOT}/source426=424全部oldbytesexact+truthfulsame-scopeworker与uniquecontroller，来源own424model32264 SHA{SOURCE_SHA}/18038795B/CPU104，仅同scope续训，原accepted35b026/1293c97祖先严格保持。首parent3165050-start92072197/child3165148-start92072342仅定位，actual/proc argv-cwd-start/自己的savedCPU-PID-phase优先。targetCPU426/full104/严格wrongassignment-map-origin-profile-boundepisode/privatecommand磁盘fixture通过，9ownstartup same50entrydirection CPUCUDA磁盘roundtrip/sourceepisode+1真正通过。活动不是ownfinal/毕业；只有自己的保存actorchanged+optimizerdelta才称真实PPO更新。read_second_direction_actual.py仅读最新SECOND_DIRECTION_ACTUAL数字timestamp；自己的futurefinal和publication优先。old424ownfullsave/PASSED/unique325.21194553375244s/父guardianchild实际exit/twofcntl-free/noactive已核。所有旧stage-main-resume-SDK-native-PPO-preflight-fresh-dispatch-record-sync-budgettailonce不可重跑。

1800s完整保存资源guard严格拒绝：实际durable ext4可用约4.75GB，原1800参考wholeoutput1536678072B的2倍+2GiB需要5220839792B。原拒绝保持，不删除raw-weights-source-env-cache或其它AI文件、不借tmpfs冒durable；独立900s选择实际完成的同20k24control/16columnfloat32 trace900s输出格式参考wholeoutput795686159B，2倍+2GiB并加sourceasset差额保持原比例通过。该CURB900参考仅资源输出格式，不冒Wave geometry或CPUCUDA准入复用。选择15分钟仍在005原max1800权限内，无加预算；scope其它reset-command-direction-geometry-reward-LR-DR-hardware-clock五族全不变，旧自己424SDKnative/smallbig/fresh/clockDRgeometry PASSED原pathsizeSHA复用无重预检45minclock。

人类询问华南虎门槛后，已逐字SHA核1a26356公开train/V14/父dones/July30实际env与原RM003计划。此前助手把正反27/27说成硬门槛表述过头，已明确纠正：批准计划“不造90/95/100晋级线”，全部样本完成是强观察证据而非机械晋级线。公开SCUT持续learn/普通逐envreset/该July30普通终止20*20ms=.4s过滤；数值异常立即处理，height课程源码可用但该July30保存enabled=false，作者私有考核未知。当前150位置/contact完成一致，15个正向真实未完不只1N边缘拒绝。前后双轮支撑不要求整段每tick双轮接触；完整路线/同episode/noresetteleport/原1N-query1e-6-积分COMhardware/validprefix原合同不改，不抹false或另造百分比线，不凭比较称50合格/升70。独立报告SCUT_WAVE_GATE_COMPARISON.md/SCUT_WAVE_GATE_SOURCE_AND_ACTUAL_COMPARISON.json已中央同步，当前性能决定综合方向-失败严重度-有效prefix-实际用途而非一个百分比。

先读中央current.rev004.wave50_direction_candidate150_actual_scope完整refs、wave50_direction_second_bounded_scope实际426和COMPLETE150_SECOND426_METADATA_SYNCED；本机{D}/reports数字actual/OWN_STARTUP_CONTRACT/未来ownsavedPPO-ownformal-candidate/fulltrace优先。原parent唯一900sloadlearnsaveexit/save25/15slocalguardian，futureownfullsave/CPU104/source426/actualsnapshots+freeze/PID/PASSED/unique结清/实际父guardian孩子exit/twofcntl-free/activeempty后自动新候选四case，实际twohostunused已核151但真实publication为准不盲claim或重发旧150149等validcomplete/failed。完成自身全raw/query/145147原50十波2.406422727m/.4approach/200mmafter/80env15s/6000callbacks/1N真实支撑与position分列/stand26/validprefix/noresetteleport和115129signedcircle沿横dedrift/two4pi/直线原false/finalbias动态静态/.0075/反馈actuallastreset审，再direct150与全trainingtrace动态rootcellfamily4/episode固定towardsign/standing/beforephysicscommand vsafterupdatehist分列。rootproxy非接触全路线或因果证书；原2mtrainingroute不容3.006m测试，仅入口前段暴露。两direction块300+900完成后不自动第三/70，系统性残差无改善独立诊断，不无限hold只队列。

newfull150/反馈reader错误误指旧149raw与严格SHA拒绝/独立namespace修复、资源拒绝/900sourceCPUdispatch/两builderpreexec引号SyntaxError及未执行独立续build/本次SCUTreader数字keyword SyntaxError与独立续review/同步/monitor/Gitreceipt全保留非GPU物理故障，不重GPU。新真实stage唯一record_experiment/remote main-tag-peeled实际工具证明，后来普通supplement；largePTNPZrawJSONUSDZIP仅actualpathsizeSHA原件保持/credentials不输出Git/pushfailedexistingobjects不重record-tag-commit/Git非训练依赖。0051188000s330h/7extensions第七100h早once，active原parent真实loadlearnsaveexit/accounted尾段优先，不扩展复制clearactive-tail-recharge。CPU-SDK-native-frozen-fresh0PPO不计；两fcntl held不按exists不删锁/kill/hotpatch/dual20k/其它AI/WASD干预。E0/CURB20/WAVE35/SLOPEONLYobserved冻结/gate未训/hardware未标定/S8另具体批准/93-94paused、fixed004005-master-RM-clockDRrewardhardware-healthv3-fullsignedcircle-fivefamilies及otherexpertgate-min(18h,.13B)规划保护继续以下原件。

mod4-10同heartbeatACTIVE每1h同target，healthy pendingDONT_NOTIFY静默，仅实质阶段/重大退化/真实修复/完成/人类动作NOTIFY，无5minSSH-ping-Rich/其它monitor/自动预算；reviewready不是allcoursefinished不删monitor，仅真实budgetend/allfinal完停止。旧全文{old} SHA{H(old.read_bytes())}保留。以下旧snapshot仅追溯，以上及之后actual优先：

'''
    save('SECOND_DIRECTION_HOURLY_MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=setting['name'],rrule=setting['rrule'],status='ACTIVE',targetThreadId=setting['target_thread_id'],prompt=prefix+setting['prompt']))
    print(json.dumps(dict(passed=True,complete150_forward=12,reverse=25,source426_startup9_passed=True,monitor_request=str(R/'SECOND_DIRECTION_HOURLY_MONITOR_UPDATE_REQUEST.json'))))

if __name__=='__main__':
    try:main()
    except BaseException:save('COMPLETE150_SECOND426_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_oldonce_replay=True));raise
