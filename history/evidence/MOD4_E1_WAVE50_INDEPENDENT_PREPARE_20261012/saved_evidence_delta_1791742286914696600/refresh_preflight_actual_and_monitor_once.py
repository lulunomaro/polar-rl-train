from wave50_io import *
import tomllib
def main():
 assert not (R/'PREFLIGHT_ACTUAL_METADATA_SYNCED.json').exists()
 p=max(R.glob('WAVE50_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));v=json.loads(p.read_bytes());assert not v['reports'].get('E1_ATTENTION.json')
 for name in ('WAVE50_SDK10_PASSED.json','WAVE50_NATIVE20K_PASSED.json','wave50_discard128_PASSED.json','wave50_discard20k_PASSED.json'):assert name in v['reports']
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   path=io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json';raw=f.open(path,'rb').read();current=json.loads(raw);oldSHA=H(raw)
   ref='E1_WAVE50_INDEPENDENT_GPU_PREFLIGHT_CURRENT_ACTUAL_'+p.stem.rsplit('_',1)[1]+'.json';io.put(f,io.E+'/reports/'+ref,p.read_bytes());io.put(f,io.E+'/reports/E1_WAVE50_INDEPENDENT_GPU_SCOPE_STAGE_GIT_RECORDED.json',(R/'STAGE_GIT_RECORDED.json').read_bytes())
  scope=current['terrain_subexpert_revision004']['wave50_independent_GPU_scope'];assert scope['root']==ROOT
  scope.update(phase=v['reports']['E1_STATE.json']['phase'],actual_SDK10_new50_scope_PASSED=True,actual_native20k_new50_scope_PASSED=True,actual_small128x2_and_big20kx4_complete_discard_PPO_PASSED=True,fresh_same50_fullresume_active_snapshot=True,actual_parent=v['actual_owner'],actual_child=v['actual_child'],own_formal_not_yet_complete=True,current_actual_ref=dict(path=io.E+'/reports/'+ref,bytes=p.stat().st_size,sha256=H(p.read_bytes())),latest_actual_overrides_snapshot=True)
  current['terrain_subexpert_revision004']['active_next_phase']=scope['phase']
  data=json.dumps(current,ensure_ascii=False,indent=2).encode()
  with n.open_sftp() as f:io.put(f,ROOT+'/reports/PREFLIGHT_METADATA_CAS_NEXT.json',data)
  sync=run(n,r'''from pathlib import Path
import hashlib,json,time,os
D=Path(ROOT_TOKEN);E=Path(E_TOKEN);p=E/'reports/MOE_PLAN_EXECUTION_CURRENT.json';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert h(p)==OLD_SHA_TOKEN
raw=(D/'reports/PREFLIGHT_METADATA_CAS_NEXT.json').read_bytes();temp=p.with_name('CURRENT_wave50_preflight_'+str(time.time_ns())+'.tmp');temp.write_bytes(raw);assert h(p)==OLD_SHA_TOKEN;os.replace(temp,p)
v=dict(epoch=time.time(),passed=True,current_SHA=h(p),new_source384_own_stages_synced=True,no_canonical_budget_or_old_sync_replay=True);(D/'reports/PREFLIGHT_ACTUAL_METADATA_SYNCED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('E_TOKEN',repr(io.E)).replace('OLD_SHA_TOKEN',repr(oldSHA)))
  save('PREFLIGHT_ACTUAL_METADATA_SYNCED.json',sync)
 finally:io.cleanup(n,w)
 setting=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 old=D/'MONITOR_PREVIOUS_WAVE50_SDK_DISPATCH_PROMPT.md';assert not old.exists();old.write_text(setting['prompt'],encoding='utf8')
 prefix=f'''最新source384自己的50mm SDK10实际10G4格/完整footprint/1200callback、native20k24warm120timed480/576callbacks、小128x2完整6144steps192callbacks、大20kx4完整1.92Msteps384callbacks已ownPASSED/CPU/PID与原parent各unique结清。旧SDK/native/big活动只是历史，不重stage/main/SDK/native/small/big/once。当前实际phase={v['reports']['E1_STATE.json']['phase']}，自己的fresh新20k0control0PPO显式seed20260928恢复只当时活动，后actualfreshPASSED/formal/fullsave/exit/候选优先，不假永久active。已完成四stage原path-size-SHA复用，不重GPU或clock。当前source384/root={ROOT}，原parent2983989-start89534237活跃snapshot，实际/proc/ownreceipt/phase优先；最后strictsame50 CPUCUDA完整恢复PASSED后原parent自动首300s正式loadlearnsaveexit/save25/15s localguardian，从完整35来源b026非discard。

本机{D}/read_own_formal_cpu_actual.py/collect_candidate_actual.py仅读已准备且compile通过，仅按actualstage复用，准备不是futurepass。ownformal未生成合法pending，不借big全保存冒正式final。完整自己的ownformal fullsave/source384/实际CPUtensorcount/PID/7startupmarkers/完整source snapshot/unique结清/actual父guardian孩子exit/twofcntlfree/activeempty后原parent自动四case。候选按实际E1_WAVE50_ASYNC_PUBLISHED和CANDIDATE_JOB_UNUSED_ACTUAL读取number，不硬套旧145或盲占号。完整新candidate raw/query/旧三skill审查器在actualschema完整后独立准备/复用：145同50mm物理/查询原合同与115/129旧skill，绑定自己的ownCPU实际count/actualresult SHA=manifest SHA=ownformal SHA，完整四case beforemorePPO/70mm；sensorfinal动态bias与静态配方分列、不伪未落盘initialbias；所有strictfalse/有效失败prefix保持。旧143/145审查源码参考不能套旧sourcecount369/102或旧job。

新stage Git trial-20261012-wave50-isolated384-sdk-passed-fullscope-controller-started commit9c43a30a5f186d8acf2abb4bb79f1cb02ee9e1ab/tagobjecte712f9ebbd23fcbe518e618410f9d19c6ef65438已actualremote main/tag/peeled核验，原1298tagobjects保持。后nativecomplete/smallbig/fresh/新prepared仅读者/monitor/当前sync/Gitreceipt仍ordinarysupplement，以actualtracked/remote最终工具优先，不凭本文假补齐。所有后来ownfinal/候选/fulltrace/savederrors仍Git，largeoriginals只actualpath-size-SHA。原monitor全文{old} SHA{H(old.read_bytes())}历史追溯，以下固定约束继续但actual优先：

'''
 prompt=prefix+setting['prompt'];p=D/'MONITOR_CURRENT_WAVE50_PREFLIGHT_PROMPT.md';assert not p.exists();p.write_text(prompt,encoding='utf8')
 save('PREFLIGHT_MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=setting['name'],rrule=setting['rrule'],status='ACTIVE',targetThreadId=setting['target_thread_id'],prompt=prompt))
 print(json.dumps(dict(current_phase=scope['phase'],monitor_request=str(R/'PREFLIGHT_MONITOR_UPDATE_REQUEST.json'))))
if __name__=='__main__':
 try:main()
 except BaseException:save('PREFLIGHT_SYNC_MONITOR_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_old_once_replay=True));raise
