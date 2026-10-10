"""New128 full review and command-scope work order; no learning or old sync replay."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';B='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(v.encode('utf8') if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2).encode())
def main():
 vp=sorted(R.glob('G3_128_REVIEW_*.json'))[-1];v=json.loads(vp.read_bytes());assert v['review_complete'] and not v['pending'] and v['paired_initial_root30q_parameters_recipes_assignments_exact']
 for row in v['summary'].values():assert row['ordinary']==0
 save('PAIR128_CLOSEOUT_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-128-COMPLETE-NEXT-COMMAND-01',once=True,no_learning=True))
 decision=dict(epoch=time.time(),trial_id='E1-G3-128-PAIRED-DIAGNOSTIC-DECISION-01',complete_review=str(vp.resolve()),summary=v['summary'],original065source_forward_complete=17,original065candidate_forward_complete=13,paired040source_forward_complete=23,paired040candidate_forward_complete=21,paired040reverse_both=27,
 inference='Approach time contributes to route incompletion. Newinitialstate/contactphase also changed, so do not infer exact additive causal contribution or relabel original results. Candidate still worse than source forward and old127retention remains degraded.',not_all35mm_pass=True,permanent_anti_forgetting_proven=False,selected_next_learning_source=dict(iteration=32058,sha256='42cdc9d24519778a9da3e35b05a3eb3bb5745760c26a5842c78fcde2bd39e53b'),candidate32063_not_blind_continued=True,next50mm_not_admitted=True,
 next_scope='Actual eligible flat command retention only; need new command-native-save-resume contracts, single300s fullsave and complete behavior review',no_PPO_launched=True,new_budget_seconds=0)
 save('PAIR128_COMPLETE_RETENTION_DECISION.json',decision)
 old=json.loads((R/'NEXT_E1_G3_RETENTION_REPAIR_WORK_ORDER.json').read_bytes());old.update(epoch=time.time(),trial_id='E1-G3-NEXT-COMMAND-RETENTION-REPAIR-V2',pair128_complete=True,actual128_complete_review=str(vp.resolve()),pair128_decision=str((R/'PAIR128_COMPLETE_RETENTION_DECISION.json').resolve()),next_command_math=str((D/'implementation/retained_flat_command_math.py').resolve()),command_CPU_receipt=str((R/'RETAINED_FLAT_COMMAND_CPU_REVIEW.json').resolve()),command_CPU_named_RNG_disk_receipt=str((R/'FLAT_CPU_NAMED_GENERATOR_DISK_VERIFIED.json').resolve()),next_action='Prepare isolated actual assignment/support-aware flat command adapter, save/fullresume and callback command histograms; CPU proof does not authorize SDK or PPO until genuinely new scoped actual contracts pass.',pending_actuals=['actualplaneassignment+surface/rotationclearance, route-boundary truncated prefixes','SDK10env300control1200callbacks andnative20k24warm120timed576total, source338 exactreuse of existing geometry/clock/D0D7','newcommandstate/restoredoldstreams/onephysicalepisode/actualCUDAroundtrip/sourceSHA/ownCPU96','new128x2and20kx4 fullPPO discard once each samecanonical then formal300s only; no oldsame-scope replay'],new_learning_launched=False)
 save('NEXT_E1_G3_COMMAND_RETENTION_REPAIR_WORK_ORDER_V2.json',old)
 text='''# 128配对完整诊断与下一单轴命令修复

128两份冻结回放实际complete/errorfree，两机JSON byteexact/fullNPZ SHA/初始root30q参数recipesassignments配对、ground-contact/COMlink/hardware原容差通过。前支撑.65→.40m后，旧源32058前完整23/27、候选32063前21/27；倒向两者27/27；ordinary0，closure峰分别.653137569/.655802432mm。四个及六个前向未完成prefix保留，不能称全35mm通行。

原126/127前17/27与13/27、两轮全波24/27与19/27、旧world62→56/64、负4π5→2/8及各strictfalse/raw/成本全部保留。新起始状态也改变接触相位，因此缩短接近段能解释一部分窗口因素，但没有分离其精确因果贡献，更没有消除旧技能退化。选择已完整审查的32058，拒绝从32063盲续或升50mm。

下一真正新范围只在既有30%plane族且实际净空确认环境中保留旧signed直行与worldV.5/yaw±1–2在线数据；非平地继续gentleyaw0，比例、几何、reward、LR、clock、D0-D7/hardware不改；不把4π旋转或危险reset塞进S3。CPU分支/完整signedcircle积分/私有CPU随机流磁盘恢复已通过，仅为未部署组件。实际SDK/native命令与地形assignment、恢复/新physicalepisode/fullsave、PPO完整范围预检仍待新准入，不借CPU报告称任务通过。

按同名V2 JSON积极准备新隔离adapter与必要实际合同，通过后只300s完整load-learn-save-exit；弃预检权重、各段原parent唯一计同canonical，不复制/clear/recharge/追加预算。原338和任何旧once/main/resume/native/SDK/PPO/record/sync/budgettail入口均关闭不可复活。新actual结果/失败/拒绝/同步/保存巡检报告继续Git追加；monitorACTIVE每2h健康pending静默，不5minSSH。
'''
 save('PAIR128_COMPLETE_AND_NEXT_COMMAND_REPORT.md',text)
 files={'E1_G3_128_COMPLETE_MATCHED_ACTUAL_REVIEW.json':vp,'E1_G3_128_COMPLETE_RETENTION_DECISION.json':R/'PAIR128_COMPLETE_RETENTION_DECISION.json','NEXT_E1_G3_COMMAND_RETENTION_REPAIR_WORK_ORDER_V2.json':R/'NEXT_E1_G3_COMMAND_RETENTION_REPAIR_WORK_ORDER_V2.json','E1_G3_128_COMPLETE_AND_NEXT_COMMAND_REPORT.md':R/'PAIR128_COMPLETE_AND_NEXT_COMMAND_REPORT.md'}
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  with c.open_sftp() as f:
   budget=f.open(B).read();assert json.loads(budget)['active_segment'] is None
   for name,p in files.items():
    raw=p.read_bytes()
    with f.open(E+'/reports/'+name,'wbx') as out:out.write(raw)
    assert f.open(E+'/reports/'+name).read()==raw
  code=r'''from pathlib import Path
import hashlib,json,time,os
R=Path(REPORTS);B=Path(BUDGET);H=lambda b:hashlib.sha256(b).hexdigest()
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')};budget=B.read_bytes();assert H(budget)==EXPECTEDSHA and json.loads(budget)['active_segment'] is None
assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);event=v['E1_G3_short_observation_execution_event'];event.update(actual128_complete_review=str(R/'E1_G3_128_COMPLETE_MATCHED_ACTUAL_REVIEW.json'),actual128_decision=str(R/'E1_G3_128_COMPLETE_RETENTION_DECISION.json'),next_retention_work_order=str(R/'NEXT_E1_G3_COMMAND_RETENTION_REPAIR_WORK_ORDER_V2.json'),paired128_complete=True,actual_command_SDK_native_PPO_admission_pending=True,no_new_learning_launched_at_this_transaction=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.Pair128-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='E1 G3 actual128 complete command-retention scope20261010:';assert marker.encode() not in old
message=chr(10)*2+marker+'128 paired040 actualcomplete fullraw/contacts/initial root30q params recipes verified. Source32058 forward23of27/candidate32063 21of27; reverseboth27of27;ordinary0. Original06517/13 and all oldretention62to56/world,5to2/negative4pi preserved. Approachwindow partly contributes, not forgettingcure/all35mmpass. Select32058; no blind32063PPO/next50mm. Next V2workorder requires new command-only eligibleflat assignment/support+CPU/CUDA state/fullresume/native/PPO scopedadmission and actual commandhistograms before single300s boundedrepair; CPU synthetic alone insufficient. No learning/budgetextension/master/RM changes; oldonce closed, healthy3060worker unchanged; ACTIVE2h healthypendingquiet. All savedreportsGit including thisreceipt.'+chr(10)
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.Pair128-'+str(time.time_ns()));tmp.write_bytes(old+message.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),current_before_SHA=H(before),current_after_SHA=H(raw),actual128_complete_synced=True,master_RM_approval_tracks_canonical_bytes_preserved=True,new_budget_seconds=0)))
'''.replace('REPORTS',repr(E+'/reports')).replace('EXPECTEDSHA',repr(H(budget))).replace('BUDGET',repr(B))
  compile(code,'<pair128closeout>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');receipt=json.loads(raw)
  receipt['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()];save('PAIR128_COMPLETE_METADATA_SYNCED.json',receipt)
  with c.open_sftp() as f:
   raw=(R/'PAIR128_COMPLETE_METADATA_SYNCED.json').read_bytes()
   with f.open(E+'/reports/E1_G3_128_COMPLETE_METADATA_SYNCED.json','wbx') as out:out.write(raw)
   assert f.open(E+'/reports/E1_G3_128_COMPLETE_METADATA_SYNCED.json').read()==raw
  print(json.dumps(decision))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:
  save('PAIR128_CLOSEOUT_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_executed_mutations=True));raise
