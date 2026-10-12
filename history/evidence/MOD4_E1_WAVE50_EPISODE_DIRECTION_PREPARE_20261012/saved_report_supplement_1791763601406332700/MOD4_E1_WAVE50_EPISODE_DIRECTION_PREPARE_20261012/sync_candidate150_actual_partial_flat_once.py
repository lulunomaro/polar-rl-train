"""Append new versioned partial evidence; preserve original all-pending snapshot."""
from wave_direction_io import *
import tomllib
def main():
 cp=max(R.glob('DIRECTION_CANDIDATE_COLLECTED_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));rp=max(R.glob('DIRECTION_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));c=json.loads(cp.read_bytes());r=json.loads(rp.read_bytes());assert r['collection']==str(cp) and not r['review_complete'] and 'flat' in r['retention'] and len(c['cases'])==1
 stamp=str(time.time_ns());names={'E1_WAVE50_DIRECTION_CANDIDATE150_ACTUAL_COLLECTION_'+stamp+'.json':cp,'E1_WAVE50_DIRECTION_CANDIDATE150_PARTIAL_ACTUAL_REVIEW_'+stamp+'.json':rp};n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   for name,p in names.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
   raw=f.open(io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json','rb').read();oldsha=H(raw);current=json.loads(raw)
  rev=current['terrain_subexpert_revision004'];s=rev['wave50_direction_candidate150_actual_scope'];s.update(complete_cases=1,pending=c['pending'],flat_initialization_parameters_recipes_assignment_data_contract_reviewed=True,flat_originalstrictfalse_preserved=True,partial_flat_straight_diagnostics=r['summary']['retention']['flat'],current_collection_ref=io.E+'/reports/'+next(k for k in names if 'COLLECTION_' in k),current_review_ref=io.E+'/reports/'+next(k for k in names if 'REVIEW_' in k),four_case_fullreview_pending=True)
  path=ROOT+'/reports/CANDIDATE150_PARTIAL_CAS_NEXT_'+stamp+'.json'
  with n.open_sftp() as f:io.put(f,path,json.dumps(current,ensure_ascii=False,indent=2).encode())
  v=run(n,r'''from pathlib import Path
import json,time,hashlib,os
D=Path(ROOT_TOKEN);R=Path(E_TOKEN)/'reports';B=Path(B_TOKEN);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=h(B);protected={k:(R/k).read_bytes() for k in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';assert h(p)==SHA_TOKEN;raw=Path(NEXT_TOKEN).read_bytes();tmp=p.with_name('CURRENT_direction150partial_'+str(time.time_ns())+'.tmp');tmp.write_bytes(raw);assert h(p)==SHA_TOKEN;os.replace(tmp,p);assert all((R/k).read_bytes()==v for k,v in protected.items()) and h(B)==before
v=dict(epoch=time.time(),passed=True,actual150_partialflat_synced=True,original_pending_snapshot_kept_with_new_versioned_reports=True,current_SHA=h(p),canonical_SHA_exact_preserved=before,master_approval_tracks_RM004_exact=True,no_GPU_or_budget_write=True)
for q in (D/'reports/CANDIDATE150_PARTIAL_METADATA_SYNCED.json',R/'E1_WAVE50_DIRECTION150_PARTIAL_METADATA_SYNCED.json'):
 assert not q.exists();q.write_text(json.dumps(v,indent=2))
print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('E_TOKEN',repr(io.E)).replace('B_TOKEN',repr(io.B)).replace('SHA_TOKEN',repr(oldsha)).replace('NEXT_TOKEN',repr(path)))
  save('CANDIDATE150_PARTIAL_METADATA_SYNCED.json',v)
 finally:io.cleanup(n,w)
 setting=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert setting['status']=='ACTIVE' and setting['rrule']=='FREQ=HOURLY;INTERVAL=1'
 oldprompt=D/'MONITOR_PREVIOUS_DIRECTION150_FIRST_PENDING_PROMPT.md';oldprompt.write_text(setting['prompt'],encoding='utf8');facts=r['summary']['retention']['flat']['candidate']['straight']
 prefix=f'''最新补充actual：150四case当前仅retention-flat actualcomplete/errorfree，两hostprobe/result byteSHAexact及完整115/129初始化30q/参数recipesassignments通过；负/正1.5误差{facts[0]['error']}/{facts[1]['error']}m/s，source129 .026857004/.043898690，originalstrictfalse保持。terrain/spin/world首当前result未生成/attentionnull健康pending，不借flat或formal fullsave说qualified50。先读中央current.rev004.wave50_direction_candidate150_actual_scope最新versioned ACTUAL_COLLECTION/PARTIAL_ACTUAL_REVIEW refs及E1_WAVE50_DIRECTION150_PARTIAL_METADATA_SYNCED；本机{D}/reports最新DIRECTION_CANDIDATE_COLLECTED/ACTUAL_REVIEW数字timestamp及以后fullactual优先，旧allpending只是历史。

source424首formal已经ownfullsave/PASSED/CPU104/95snapshot+424freeze/PID3146332/6updates144control2.88Msteps576callbacks/9actorchanged/optimizerdelta120/unique325.21194553375244s自然退出、两fcntl锁free/noactive，own095f27666fceb6a443c819972611aa894a62ff19f103f8511574773d55d1a785/18038795B。旧formalactive不是当前，source424不是CURB旧source424，按完整root/ownSHA身份。新9startup全strictinitialold35→50entrydirection CUDA/episode+1；freshsame50entrydirection自己exact passed不套initial字段。read_direction_own_formal_CPU_call_reviewed_actual.py与verify_direction_initial_transition_CPU_call_reviewed_actual.py是已实际pass正确CPU读者；原j参数错误及prepared旧same50label保留，不再用错误版本，不重GPU。

本次完整ownformal/150partial/fulltrace/读者errors+独立修复/sync/monitor/Gitreceipt仍按ordinarysupplement actualtracked/remote工具为准；此前stage f0ee258/a49ff332与后f14b4fd普通补充已核1305tags，任何后来savedreport须补Git。所有fixed合同、后完整150四case/直接149/原50协议和115129诊断/ownfulltrace/独立scope决定前不更多PPO70/qualified50/全RM-MoE，<=2h/max2fullaudit及005unique预算/其它冻结expert/gate/WASD保护继续下文。mod4-10同ACTIVE每1h同target，healthy pending DONT_NOTIFY静默，仅实质阶段/重大退化/真实修复/完成/人类动作NOTIFY；无5minSSH/ping/Rich/额外monitor/自动预算。完整旧提示在{oldprompt} SHA{H(oldprompt.read_bytes())}，以下以及之后actual优先：

'''
 save('CANDIDATE150_PARTIAL_HOURLY_MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=setting['name'],rrule=setting['rrule'],status='ACTIVE',targetThreadId=setting['target_thread_id'],prompt=prefix+setting['prompt']))
 print(json.dumps(dict(actual150partialflat_synced=True,review_complete=False,monitor_request=str(R/'CANDIDATE150_PARTIAL_HOURLY_MONITOR_UPDATE_REQUEST.json'))))
if __name__=='__main__':
 try:main()
 except BaseException:save('PARTIAL_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
