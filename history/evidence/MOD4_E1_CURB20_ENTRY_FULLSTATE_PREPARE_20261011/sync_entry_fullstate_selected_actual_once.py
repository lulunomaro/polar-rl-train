from pathlib import Path
import sys,json,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(D));from stage_entry_fullstate_and_cpu_once import NEW,save
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io

def main():
 actual=max((p for p in R.glob('ENTRY_FULLSTATE_ACTUAL_*.json') if p.stem.removeprefix('ENTRY_FULLSTATE_ACTUAL_').isdigit()),key=lambda p:int(p.stem.removeprefix('ENTRY_FULLSTATE_ACTUAL_')))
 a=json.loads(actual.read_bytes());sdk=a['reports']['ENTRY_ORIGIN_BOUND_SDK10_PASSED.json'];small=a['reports']['entry_discard128_PASSED.json']
 assert sdk['passed'] and sdk['actual_CURB_start_environments']==10 and not a['reports'].get('E1_ATTENTION.json')
 save('ENTRY_ORIGIN_BOUND_SCOPE_ACTUAL_REVIEW.json',dict(epoch=time.time(),SDK10_actual_own_PASSED=sdk,small128_discard_own_PASSED=small,original398_SDK_scope_false_preserved=True,valid398_native20k_exact_reused=True,full_BIG_fresh_and_formal_pending_at_snapshot=True,no_new_budget_extension=True))
 order=R/'NEXT_ENTRY_FULLSTATE_AND_139_REVIEW_WORK_ORDER.md';assert not order.exists()
 order.write_text('''# 独立CURB20 origin-bound入口全状态与候选139工作单

source409新独立root已实际CPU准入和唯一dispatch。398全部旧源码字节保持，另11份entrycache身份/fullstate/worker/controller隔离。CPU真实旧SDK后改原点fixture从0变10覆盖、selectedsubset和原20k映射byteexact通过；CPU不当物理合同。新的actual origin-bound SDK10已300control/1200callback及10/10真实CURB起点PASSED；旧398 SDK进程PASSED保留而其范围不足0/10披露。398native20k完整trace、2820CURB与双方向standing镜像准入精确复用，不再GPU。小128x2自己的完整保存/CPU102/6144envsteps/192callback/PASSED且原父唯一结账，弃权重。

正在进行的新20kx4完整PPO预检以自己的actualownrun/PID/PASSED为准。完整save后独立fresh20k新进程0control0PPO验证sameCURB+sameentry全actorcriticstdoptimizer/D0D7/globalnamed/dictprivateCPUCUDA/terraincommand/episode+1；禁止已步进env fresh-only误用与未初始化logger可选save。所有本scope实际PASSED才原父自动一次300sload-learn-save-exit/save25/15s本机guardian，从完整129source3643c97加载，不用discard。初始明确G3→CURB+新entrymap身份，后sameentry严格exact，非PhysXexactresume；原strict oldnamed不放宽。

ownformal CPU102/source409/实际snapshot/rollingfreeze/latestcomplete/PIDreceipt/PASSED/唯一completedsegment核验后自动发布新139地形与retention-flat/spin/world。两机实际139queue/results/jobs占号检查已无占用，旧132/133/129等complete不重发。候选4case全部actualcomplete/errorfree才收跨主机probe/result JSON byteexact/fullNPZ SHA，完整root30q/parameters/recipes/assignments/6000callbacks/actualground-contact积分COMlinkhardware原容差审查；132同20mm竖直150mm条带/9m镜像/approach.4/200mm后支撑的初始化配对，旧115合同和1293c97直接旧技能诊断保留。完整signedcircle沿横向/dedrift/左右4pi/直线误差，ordinary/declaredtruncation覆盖和全部有效未完成prefix原样，不把resetteleport算进度、不缩接近延窗重标旧失败。站立不要求跨坎。

formal完整保存自然退出/reviewready是合法边界，不全课程finished。actualfinal以后新中央同步/CPU核验/139审查及Git补交继续积极完成；未四case决定不盲续900s/升35或50mm/qualifiedCURB/MoE部署。005唯一预算1188000s330h/七扩展已登记，PPOloadlearnsaveexit各原父同canonical唯一扣账，无PPO不计；不得重tail/扩展/clearactive。旧parentguardian孩子exit/两OS锁free/唯一段结清才新权，不kill/hotpatch/双20k/干预别人。

E0/Wave/SLOPE权重和optimizer冻结不更新，gate未训/硬件未标定/S8仍后续具体批准，WASD播放器不触碰。DR/reward/LR/clock/35actor38critic6action/plane30+20/20/15/15及原healthv3不变。mod4-10同一ACTIVE每30分钟，健康pendingDONT_NOTIFY；所有成功失败/reader-schema/新保存报告/同步/监控/Gitreceipt补交，大raw权重NPZ仅真实path-size-SHA，凭据不输出不Git。
''',encoding='utf8')
 n,w=io.connect_both()
 try:
  files={'E1_CURB20_ENTRY_ORIGIN_BOUND_TARGET_FULLSTATE_CPU_VERIFIED.json':R/'ENTRY_TARGET_FULLSTATE_CPU_PASSED.json','E1_CURB20_ENTRY_FULLSTATE_DISPATCH_ACTUAL_RECEIPT.json':R/'ENTRY_FULLSTATE_DISPATCH_ACTUAL_RECEIPT.json','E1_CURB20_ENTRY_FULLSTATE_CURRENT_ACTUAL.json':actual,'E1_CURB20_ENTRY_ORIGIN_BOUND_SCOPE_ACTUAL_REVIEW.json':R/'ENTRY_ORIGIN_BOUND_SCOPE_ACTUAL_REVIEW.json','E1_CURB20_ENTRY398_COMPLETE_TRACE_SCOPE_ACTUAL_REVIEW.json':W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011/reports/ENTRY_NATIVE_COMPLETE_FAMILY_SCHEMA_ACTUAL_REVIEW.json','NEXT_E1_CURB20_ENTRY_FULLSTATE_AND_139_REVIEW_WORK_ORDER.md':order}
  with n.open_sftp() as f:
   assert not set(files)&set(f.listdir(io.E+'/reports'))
   for name,p in files.items():
    io.put(f,io.E+'/reports/'+name,p.read_bytes())
    with f.open(io.E+'/reports/'+name,'rb') as inp:assert inp.read()==p.read_bytes()
  v=io.linux_json(n,r'''from pathlib import Path
import json,time,os,hashlib
R=Path(CENTRAL)/'reports';B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes())
protected={x:(R/x).read_bytes() for x in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
b=j(B);assert b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
a=j(R/'E1_CURB20_ENTRY_FULLSTATE_CURRENT_ACTUAL.json');p=R/'MOE_PLAN_EXECUTION_CURRENT.json';old=p.read_bytes();c=json.loads(old);rev=c['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_CURB'
scope=dict(root=ROOT,source_count=409,reset_only_axis=True,CPU_origin_cache_target_fullschema_passed=True,new_actual_CURB_SDK10_passed=True,old398_native20k_exact_reused=True,old398_SDK10_scope_admission=False,actual_current=str(R/'E1_CURB20_ENTRY_FULLSTATE_CURRENT_ACTUAL.json'),actual_scope_review=str(R/'E1_CURB20_ENTRY_ORIGIN_BOUND_SCOPE_ACTUAL_REVIEW.json'),work_order=str(R/'NEXT_E1_CURB20_ENTRY_FULLSTATE_AND_139_REVIEW_WORK_ORDER.md'),formal_target_seconds=300,formal_complete_pending_actual=a['formal_final_pending'],own_actual_phase=a['reports']['E1_STATE.json']['phase'],original_weights_DR_reward_LR_clock_retained=True)
rev.update(curb20_entry_fullstate_reviewed_scope=scope,active_next_phase='CURB20_entry_fullstate_actual_preflight_then_bounded_retrain',monitor_cadence_minutes=30)
rev['curb20_entry_native_scope']['actual_complete_trace_scope_review']=str(R/'E1_CURB20_ENTRY398_COMPLETE_TRACE_SCOPE_ACTUAL_REVIEW.json');rev['curb20_entry_native_scope']['actual_SDK10_CURB_entry_scope_admission']=False
assert p.read_bytes()==old;tmp=p.with_name(p.name+'.ENTRYFULL-'+str(time.time_ns()));tmp.write_bytes(json.dumps(c,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';old=p.read_bytes();note='\n\nCURB20 new source409 isolated origin-bound entry/fullstate scope CPU admitted and actually dispatched after old398 actualexit/two locks/idle005 boundary. OldSDK10 actual coverage0/10 preserved alongside originalPASSED, valid398native20k fulltrace reused. NewSDK10 actual10/10 CURB/1200callbacks and small128 fullsave passed. Current own big/fresh/formal actual receipts override this snapshot; no repeat once/controller/PPO. Master/approval/tracks/RM unchanged; canonical original parent normal accounting only. Monitor30minACTIVE/silenthealthy preserved, local WASD untouched. New workorder requires own formal PID/save/CPU/unique segment then complete139 fourcase review before morePPO. All saved reports continue Git supplement.\n';assert p.read_bytes()==old;tmp=p.with_name(p.name+'.ENTRYFULL-'+str(time.time_ns()));tmp.write_bytes(old+note.encode());os.replace(tmp,p)
assert all((R/x).read_bytes()==raw for x,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,scope=scope,protected_master_approval_tracks_RM_bytes_exact=True,canonical_writer_actions=0,canonical_actual_authorized_seconds=j(B)['authorized_training_seconds'],original_parent_accounting_independent=True,old398_SDK_scope_gap_disclosed=True,actual_monitor_minutes=30)))
'''.replace('CENTRAL',repr(io.E)).replace('BUDGET',repr(io.B)).replace('ROOT',repr(NEW)))
  p=save('ENTRY_FULLSTATE_SCOPE_METADATA_SYNCED.json',v)
  with n.open_sftp() as f:io.put(f,io.E+'/reports/E1_CURB20_ENTRY_FULLSTATE_SCOPE_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(dict(metadata_synced=True,root=NEW,formal_pending=True,monitor_minutes=30)))
 finally:io.cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_FULLSTATE_SELECTED_METADATA_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_sync_replay=True));raise
