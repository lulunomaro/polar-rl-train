from slope_io import *
import traceback
def main():
 assert json.loads((R/'STAGED_VERIFIED.json').read_bytes())['CPU']['passed']
 save('SCOPE_SYNC_STARTED.json',dict(epoch=time.time(),immutable_complete134_and_new_SCOPE_annotations_only=True))
 collection=sorted((PRE/'reports').glob('SLOPE134_COLLECTED_[0-9]*.json'))[-1]
 rv=json.loads((R/'SLOPE134_COMPLETE_ACTUAL_REVIEW.json').read_bytes());assert rv['review_complete']
 decision=dict(epoch=time.time(),source_SHA=SHA,new_slope_frozen_baseline_complete=True,ascending_complete=27,descending_complete=27,each_direction_envs=27,contact_confirmed_same_counts=True,only5deg_2m_15s_seed20260928_scope=True,not_all_RM_geometry_or_qualified_learned_expert=True,new_independent_scope_contract_admitted=True,own_learning_model_and_gate_not_yet_verified=True,no_extra_budget=True)
 dp=save('SLOPE134_COMPLETE_SCOPE_DECISION.json',decision)
 work='''# 独立 E1_SLOPE5 新合同和短窗工作单

134已实际complete/errorfree，完整两机JSON逐字SHA、rawNPZ、全部root30q/参数/recipes/assignments/6000callbacks/ground-contact积分/COMlink/hardware原容差独立审查。5°连续2m坡段/镜像/0.4m接近/200mm后支撑/80env1500controls15s20260928white3，上下行各27/27位置完成与实际1N接触证据吻合，standing26不要求跨坡。只此派生范围，不实际RM全坡面或合格学习专家。

本新独立root只暖启动已完整129审查source3643c97。完整actorcriticstdoptimizer/allD0D7/globalnamed/privateCPUCUDA及旧terraincommand先验证，明确G3→新SLOPE几何与assignment迁移，再CUDAroundtrip/savedsourceepisode+1。原严格assignment和named集合不放宽。独立storage/output不更新E0/Wave/CURB。targetCPU通过仅组件与状态schema，不物理准入。

新SDK10真实上下支撑与镜像300control1200callback、native20k24warm+120timed480/576callbacks、128x2与20kx4完整PPO弃权重，各一次；同scope新fullsave之后独立fresh20k零control零PPO实际sameSLOPE完整CPUCUDA恢复，不在已步进env重用fresh-only接口，不调用未初始化logger可选save。原clock/DR精确复用无45min重复。全部PASSED才唯一300s含load-learn-save-exit/save25/15s本地主机guardian，然后自己fullsave/PIDreceipt/PASSED/唯一账段与135terrain+flat+spin+world完整审查；不自动900s/升8度/更多PPO。

actualreceipt/currentstage优先，未来文件缺失为pending。旧389/CURB完整审查边界不是故障；不复活任何旧once。canonical828000s/六扩展各一次/新增0，PPOload/learn/save/exit同原账唯一扣，不clear/复制/扩展。两OS锁真实fcntl核验，persistent存在非持锁。所有false/raw/cost/prefix/reader/拒绝/同步/monitor/工作单入Git，大原件只真实path-size-SHA。人类本地WASD播放器不受本训练任务干预。004职责、E0冻结/gate未训/硬件未标定/S8后续具体批准/93-94paused保持。
'''
 wp=R/'NEXT_E1_SLOPE5_NEW_SCOPE_AND_135_REVIEW_WORK_ORDER.md';assert not wp.exists();wp.write_bytes(work.encode())
 n,w=connect_both()
 try:
  boundary(n)
  reports={'E1_SLOPE5_134_COMPLETE_ACTUAL_COLLECTION.json':collection.read_bytes(),'E1_SLOPE5_134_COMPLETE_ACTUAL_REVIEW.json':(R/'SLOPE134_COMPLETE_ACTUAL_REVIEW.json').read_bytes(),'E1_SLOPE5_134_COMPLETE_SCOPE_DECISION.json':dp.read_bytes(),'E1_SLOPE5_INDEPENDENT_SCOPE_STAGED.json':(R/'STAGED_VERIFIED.json').read_bytes(),'E1_SLOPE5_TARGET_FULLSTATE_CPU_VERIFIED.json':(R/'TARGET_FULLSTATE_CPU_PASSED.json').read_bytes(),'NEXT_E1_SLOPE5_NEW_SCOPE_AND_135_REVIEW_WORK_ORDER.md':wp.read_bytes()}
  with n.open_sftp() as f:
   assert all(name not in f.listdir(E+'/reports') for name in reports)
   for name,raw in reports.items():put(f,E+'/reports/'+name,raw)
   put(f,NEW+'/reports/NEXT_E1_SLOPE5_WORK_ORDER.md',wp.read_bytes())
  receipt=linux_json(n,r'''from pathlib import Path
import json,hashlib,time,os
R=Path(CENTRAL)/'reports';B=Path(BUDGET);budget=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);rev=v['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_SLOPE'
review=json.loads((R/'E1_SLOPE5_134_COMPLETE_ACTUAL_REVIEW.json').read_bytes());assert review['review_complete'];assert json.loads(budget)['active_segment'] is None
rev['slope5_134_frozen_scope'].update(actual_complete_review_pending=False,actual_complete_collection=str(R/'E1_SLOPE5_134_COMPLETE_ACTUAL_COLLECTION.json'),actual_complete_review=str(R/'E1_SLOPE5_134_COMPLETE_ACTUAL_REVIEW.json'),actual_complete_decision=str(R/'E1_SLOPE5_134_COMPLETE_SCOPE_DECISION.json'))
rev['slope5_independent_scope']=dict(root=ROOT,stage=str(R/'E1_SLOPE5_INDEPENDENT_SCOPE_STAGED.json'),CPU=str(R/'E1_SLOPE5_TARGET_FULLSTATE_CPU_VERIFIED.json'),source_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',actual_new_SDK_native_PPO_pending=True,learning_controller_staged_not_started=True,formal_seconds=300,new_budget_seconds=0,work_order=str(R/'NEXT_E1_SLOPE5_NEW_SCOPE_AND_135_REVIEW_WORK_ORDER.md'))
rev['next_independent_work_order']=str(R/'NEXT_E1_SLOPE5_NEW_SCOPE_AND_135_REVIEW_WORK_ORDER.md')
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.SLOPE134COMPLETE-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
h=R/'LATEST_HANDOFF.md';hb=h.read_bytes();tmp=h.with_name(h.name+'.SLOPE134-'+str(time.time_ns()));tmp.write_bytes(hb+b'\n\nLatest actual134: mirrored derived5degree2m fullroute ascending27/27 descending27/27, actual1N contact confirmed. Own independentSLOPE scope staged and targetCPU verified only; new SDK/native/fullPPO/freshsame-scope restore then300s pending. Source3643c97, oldCURB/Wave frozen review evidence preserved. No gate/wholeRM qualification or budgetextension.\n');assert h.read_bytes()==hb;os.replace(tmp,h)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,complete134_review_synced=True,independent_scope_staged=True,master_approval_tracks_RM_canonical_bytes_preserved=True,no_GPU_or_budget_transaction=True)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)).replace('ROOT',repr(NEW)))
  rp=save('SCOPE_METADATA_SYNCED.json',receipt)
  with n.open_sftp() as f:put(f,E+'/reports/E1_SLOPE5_134_COMPLETE_AND_NEW_SCOPE_METADATA_SYNCED.json',rp.read_bytes())
  print(json.dumps(receipt))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SCOPE_SYNC_ERROR.json',dict(error=traceback.format_exc(),no_blind_replay_or_overwrite=True));raise
