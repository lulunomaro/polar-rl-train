from wave50_io import *
import tomllib
def main():
 assert not (R/'FORMAL_WINDOW_METADATA_SYNCED.json').exists()
 p=max(R.glob('WAVE50_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));v=json.loads(p.read_bytes());st=v['reports']['E1_STATE.json'];assert st['phase']=='bounded_E1_WAVE50_independent_learning' and 'WAVE50_FRESH_PROCESS_SAME_SCOPE_PASSED.json' in v['reports'] and not v['reports'].get('E1_ATTENTION.json')
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   path=io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json';raw=f.open(path,'rb').read();oldSHA=H(raw);current=json.loads(raw)
   ref='E1_WAVE50_INDEPENDENT_FORMAL_WINDOW_CURRENT_ACTUAL_'+p.stem.rsplit('_',1)[1]+'.json';io.put(f,io.E+'/reports/'+ref,p.read_bytes())
  scope=current['terrain_subexpert_revision004']['wave50_independent_GPU_scope'];assert scope['root']==ROOT
  scope.update(phase=st['phase'],all_new_scope_preflight_and_fresh_same50_actual_PASSED=True,own_formal_window_actually_dispatched=True,own_formal_final_not_yet_claimed=True,actual_parent=v['actual_owner'],actual_child=v['actual_child'],current_actual_ref=dict(path=io.E+'/reports/'+ref,sha256=H(p.read_bytes()),bytes=p.stat().st_size),latest_own_actual_overrides_snapshot=True)
  current['terrain_subexpert_revision004']['active_next_phase']=st['phase'];data=json.dumps(current,ensure_ascii=False,indent=2).encode()
  with n.open_sftp() as f:io.put(f,ROOT+'/reports/FORMAL_WINDOW_METADATA_CAS_NEXT.json',data)
  result=run(n,r'''from pathlib import Path
import json,hashlib,time,os
D=Path(ROOT_TOKEN);p=Path(E_TOKEN)/'reports/MOE_PLAN_EXECUTION_CURRENT.json';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert h(p)==SHA_TOKEN
raw=(D/'reports/FORMAL_WINDOW_METADATA_CAS_NEXT.json').read_bytes();temp=p.with_name('CURRENT_wave50_formal_'+str(time.time_ns())+'.tmp');temp.write_bytes(raw);assert h(p)==SHA_TOKEN;os.replace(temp,p)
v=dict(epoch=time.time(),passed=True,current_SHA=h(p),own_formal_window_actual_synced=True,no_canonical_budget_write_or_old_sync_replay=True);(D/'reports/FORMAL_WINDOW_METADATA_SYNCED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('E_TOKEN',repr(io.E)).replace('SHA_TOKEN',repr(oldSHA)))
  save('FORMAL_WINDOW_METADATA_SYNCED.json',result)
 finally:io.cleanup(n,w)
 setting=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 old=D/'MONITOR_PREVIOUS_WAVE50_FRESH_ACTIVE_PROMPT.md';assert not old.exists();old.write_text(setting['prompt'],encoding='utf8')
 prefix=f'''最新自己的source384正式50mm300s训练窗口已经原parent自动启动，旧native/small/big/freshactive仅历史。完整新SDK10/native20k/小128x2/大20kx4/freshsame50新20k0PPO均actual ownPASSED，前四GPUscope只此新范围各一次，绝不重预检/oldmain/once。新ownformal child2991995-start89621745/parent2983989-start89534237是当时定位，以真实/proc argv/cwd/start/自己的startup/manifest/latestcomplete/fullsave/CPU/PIDreceipt/phase优先。root={ROOT}/source384、sourceb026/CPU102，正式label e1_WAVE50_independent_observation，target300s含loadlearnsaveexit/save25/15slocalguardian。活动或big全保存不是formal final/已毕业；未生成future回执合法pending。自己的formal先全部old35状态identityexact，再明确35→50assignment migration/CUDAroundtrip/episode+1；fresh先前从discard new50 fullsave同50/commandexact恢复通过，不把freshsame50字段套formalinitial transition。

积极用read_wave50_actual.py/verify_formal_startup_save_cpu_actual.py/read_own_formal_cpu_actual.py仅读按actualstage；第一个保存未到25update或final时缺latestcomplete合法pending，不能误报故障/重启。verify_formal_startup_save_cpu_actual仅读CPU actor tensors/optimizer stepdelta+七restoremarker可证明自己的实际PPO变化，准备不称futurepass。原sourceSHA不混383/377CPU或discard，ownformal actualCPU count必须精确绑定自己的真实保存，oldsource102与direction104不套。

自己的完整fullsave/PID/PASSED/unique段原parent仅一次结清/actual父guardian孩子退出/twofcntlfree/activeempty后E1_WAVE50_independent_saved_review_ready合法单scope审查边界，非监督故障/全课程finished，不复活oldmain/resume/budgettail。不删hourlymonitor。原parent自动E1_WAVE50_ASYNC_PUBLISHED新四case实际job，读取真实候选号/ownSHA，collect_candidate_actual.py只actualcomplete/errorfree取两host8JSONbyteSHA/fullraw/queryNPZ。随后完整145 same50协议/query/原1e-6/root30qparamsrecipesassignments6000callbacks/groundcontactintegralCOMhardware原容差/十波2.406422727m/.4approach/两轮200mmafter/1N支撑与位置/全部有效prefix/no resetteleport/stand26无需通行及115/129fullsignedcircle alongcross-dedrift/signed4pi/直线原strictfalse；sensorfinal动态bias静态配方/.0075bound分列。fullroute+完整perenv命令/episode/prereset-before trace审后合理决定新singleaxis或same50下一有界块，不自动更多PPO/70mm/第三块/qualified全RM/MoE、不无限hold/只队列。保持原14550mm11/23未合格与35mm27/27冻结，E0/CURB/SLOPE/gate/WASD和全部固定合同/005unique预算/Git要求继续。旧提示原文{old} SHA{H(old.read_bytes())}只追溯。以下较旧活动snapshot被本actual覆盖：

'''
 prompt=prefix+setting['prompt'];save('FORMAL_WINDOW_MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=setting['name'],rrule=setting['rrule'],status='ACTIVE',targetThreadId=setting['target_thread_id'],prompt=prompt))
 print(json.dumps(dict(formal_window_actual_started=True,request=str(R/'FORMAL_WINDOW_MONITOR_UPDATE_REQUEST.json'))))
if __name__=='__main__':
 try:main()
 except BaseException:save('FORMAL_WINDOW_SYNC_MONITOR_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_old_once_replay=True));raise
