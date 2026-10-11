"""New final closeout metadata, separate from all executed startup syncs."""
from entry_io import *
import tomllib
NEWROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012'

def latest(pattern):return max(R.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))

def main():
 assert not (R/'ENTRY_FINAL_CLOSEOUT_METADATA_SYNCED.json').exists()
 ownpath=latest('ENTRY_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json');own=json.loads(ownpath.read_bytes())
 assert own.get('passed') and own.get('formal_complete') and own['closeout_ready'] and own['actual_source_count']==410
 currentpath=latest('INITIALIZATION_REVIEWED_ACTUAL_[0-9]*.json');v=json.loads(currentpath.read_bytes());assert v['root']==NEWROOT and v['current_state']['phase']=='E1_WAVE50_entry_saved_review_ready'
 collectionpath=latest('ENTRY_CANDIDATE_COLLECTED_[0-9]*.json');collection=json.loads(collectionpath.read_bytes())
 assert collection['own']['checkpoint']['sha256']==own['own_checkpoint']['sha256']
 work=R/'NEXT_E1_WAVE50_ENTRY_CANDIDATE_FULL_ACTUAL_REVIEW_WORK_ORDER.md'
 with work.open('x',encoding='utf8') as f:f.write('''# Review the actually saved source410 entry repair candidate

The source410 initial entry repair formal300s scope has its own complete save, actual CPU finite schema, source snapshots/freeze, PID receipt, PASSED and unique originalparent charge. Actual parentguardianchild exits, twofcntl-free, active-Sactiveempty and E1_WAVE50_entry_saved_review_ready are the legal review boundary. Do not revive any oldcontroller/main/resume/SDK/native/preflight/fresh/once/budgettail. Source398 genuine precontrol SDK initialization failure, all original false/error/raw/cost and independent410 repair remain preserved. Actual source410 new-entry SDK10/native20k/128x2/20kx4/freshsameentry passed once; reuse exact path-size-SHA, never repeat GPU or45minclock/DR.

Own formal starts from acceptedobserved35 own369b026/CPU102/ancestor1293c97, oldactorcriticoptimizerstd/allD0D7/globalnamed/dictprivateCPUCUDA/terraincommand strict thenexplicit35to50actualassignment+entryidentity/CUDA diskroundtrip/episode+1. Initialtransition terrainexactfalse is disclosed, not missingrestore. Freshsame50entry strictpassed; future same50entry requires all geometry/commands/entry exact. No PhysXexactresume claim. Own formal is not discardweights or degraded219f/a67b. New entry changes only resetXY, original fullpose30q/normal/zero velocities/clearance and commands/RNG consumption/DRrewardLRclockhardware unchanged. Original2m trainingroute cannot contain full3.006m frozen test; entry training exposure is approach/onset/partialroute, never rootproxy contact certification.

Read actual automatic publication job number and owncheckpoint SHA, no guessed or repeated job. collect_entry_candidate_actual.py only actualcomplete/errorfree, twohost8probe/resultJSON byteSHAexact plus fullterrainNPZ/queryNPZ originalpath-size-SHA. review_entry_candidate_actual.py strictly reuses145/147 derived50mm peakvalley tenwaves2.406422727m/9m40original40mirror/.4approach/twowheels fulltenwaves200mmafter/80env1500controls15s20260928white3. Allroot30q/parameters/recipes/assignment/6000callbacks/actualfloat32 worldtriangle independentquery1e-6/groundcontactintegralCOMlinkhardware oldtolerances. Original1N support and position completion separately, all valid ordinary-before/incompleteprefixes preserved, standing26 no crossingrequired, declaredtruncation coverage unionunique, sameepisodeprereset-before excludesreset teleport. No shorterapproach/longer15s/relabel. Legacy115/129 fullsignedcircle alongcross-dedrift/two4pi/straight originalstrictfalse retained. Finalsensor dynamicbias vsstaticrecipe/.0075bound/finite separated; no unrecordedinitialbias exact. Ownfinite count strictly bound actualownCPU.

review_entry_direct147_prefix_actual.py pairs all four initialconfig/params/staticrecipes/assignment and all physical validprefixes directly with complete147. Preserve every improved/regressed env and 1Nwheel support, headingxyzw, ordinary-before and route counts. review_entry_complete_dynamic_family_trace_actual.py audits complete own NPZ path-size-SHA, 20k rows/controls/callbacks, actual dynamic currentrootcell family4 (not staticassignment forever), bothsignedgentle+standing, beforephysicscommands vsafterupdatehist phase, samecontrolprereset-before, physicalepisodevalidprefixes. Root/commandproxy is not fullroute/contact/causalproof.

Only complete owncandidate fourcase and fulltrace may support the independent scope decision and a justified same-entry secondbounded block (<=2h, max2blocks thencompleteaudit). Systematic noimprovement requires independent diagnosis/nextapprovedaxis, no blindthirdblock/infinitehold/onlyqueue, no70mm orqualified50/fullRM/MoE/permanentantiforgetting beforeactualacceptance. E0/CURB20/WAVE35/SLOPE5-8-10 accepted ONLYobserved scopes frozen; gateuntrained/hardwareuncalibrated/S8specificlater/93-94paused/WASD no GUI/reset/restart/stop. Original004005/master/RM003002001/clockDRrewardLRhardware/healthv3/fullsignedcircle/ground1e-6/contact1N/COM tolerances unchanged, no teacher/newtruthactor-gate/rewardcommandaxis/pure/S7/S8/70-20-10.

005 canonical1188000s330h/sevenextensions seventh+100h alreadyonce, no budgetcopy/clearactive/tail/recharge/extend. Actualactive/accounted tail overrides snapshots. Originalparent unique PPOloadlearnsaveexit includingfailedstartup charged, CPU/SDK/native/frozen/fresh0PPO nocharge. Actualfcntl held/free not persistentfileexists; no deletelocks/kill/hotpatch/dual20k/otherAI. Otherexpert/gate/min(18h,.13B) planning protected, no ledgerreserve.

Allsavedsource/reports/successfailurefalse/raw/cost/readererrors/unusedpreparedcode/sync/monitor/workorders/Gitreceipt ordinarysupplement after the already recorded entry410 stage e6702ee/07f559. New real subsequentstage uniqueannotatedtrial actualremote main/tag/peeled; pushfail onlyexistingobjects, no record/commit/tag replay. LargeoriginalweightsNPZrawJSONUSDZIP path-size-SHAonly retained, credentials notoutputGit. Git nottrainingdependency. Hourlymod4-10 sameACTIVEtarget, quiethealthypending, notifymeaningfulrepair/materialfailure/completion/humanaction. Reviewready notallcoursefinished; stoponlyactualbudgetendandallfinal.
''')
 stamp=str(time.time_ns());names={
 'E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_OWN_FORMAL_CPU_VERIFIED.json':ownpath,
 'E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_FORMAL_FINAL_CURRENT_ACTUAL.json':currentpath,
 'E1_WAVE50_ENTRY_CANDIDATE_ACTUAL_COLLECTION_'+stamp+'.json':collectionpath,
 work.name:work}
 partials=sorted(R.glob('ENTRY_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]))
 if partials:
  partial=json.loads(partials[-1].read_bytes());assert partial['collection']==str(collectionpath)
  names['E1_WAVE50_ENTRY_CANDIDATE_PARTIAL_ACTUAL_REVIEW_'+stamp+'.json']=partials[-1]
 traces=sorted(R.glob('ENTRY_FULL_TRAINING_TRACE_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]))
 if traces:
  trace=json.loads(traces[-1].read_bytes());assert trace['passed'] and trace['own_checkpoint_SHA']==own['own_checkpoint']['sha256'];names['E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_COMPLETE_TRAINING_TRACE_ACTUAL.json']=traces[-1]
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   for name,p in names.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
   raw=f.open(io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json','rb').read();oldsha=H(raw);current=json.loads(raw)
  rev=current['terrain_subexpert_revision004'];scope=rev['wave50_entry_initialization_reviewed_GPU_scope'];assert scope['root']==NEWROOT and scope['source_count']==410
  scope.update(phase=v['current_state']['phase'],actual_scope_at_collection_epoch=v['epoch'],actual_parent_guardian_child_exit=True,two_actual_fcntl_free=True,active_Sactive_empty=True,
   new_entry_SDK_native_small_big_fresh_actual_passed=True,formal_final_not_yet_claimed=False,formal_final_actual_complete=True,
   own_checkpoint=own['own_checkpoint'],own_formal_CPU_verified=True,actual_finite_tensor_count=own['actual_finite_tensor_count'],own_source_count=410,own_snapshot_count=own['own_snapshot_count'],
   own_actual_actor_changed_count=len(own['actual_actor_tensors_changed']),own_optimizer_step_delta=own['actual_optimizer_step_delta'],unique_accounted_segment=own['unique_accounted_segment'],formal_full_training_trace_review_pending=not bool(traces),
   current_actual_ref=io.E+'/reports/E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_FORMAL_FINAL_CURRENT_ACTUAL.json',own_formal_CPU_ref=io.E+'/reports/E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_OWN_FORMAL_CPU_VERIFIED.json',next_work_order=io.E+'/reports/'+work.name)
  rev['wave50_entry_candidate_actual_scope']=dict(own_checkpoint_SHA=own['own_checkpoint']['sha256'],actual_publication=own['actual_publication'],collection_ref=io.E+'/reports/'+list(names)[2],four_case_fullreview_pending=True,not_qualified50_or_RM_or_MoE=True,next_work_order=io.E+'/reports/'+work.name)
  rev['active_next_phase']='entry_candidate_full_actual_review';rev['latest_actual_scope']='wave50_entry_candidate_actual_scope'
  path=NEWROOT+'/reports/ENTRY_FINAL_CURRENT_CAS_NEXT_'+stamp+'.json'
  with n.open_sftp() as f:io.put(f,path,json.dumps(current,ensure_ascii=False,indent=2).encode())
  result=run(n,r'''from pathlib import Path
import json,time,hashlib,os
D=Path(ROOT_TOKEN);R=Path(E_TOKEN)/'reports';B=Path(B_TOKEN)
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';h=lambda q:hashlib.sha256(q.read_bytes()).hexdigest();assert h(p)==OLD_TOKEN
before=h(B);raw=Path(NEXT_TOKEN).read_bytes();tmp=p.with_name('CURRENT_entry_final_'+str(time.time_ns())+'.tmp');tmp.write_bytes(raw);assert h(p)==OLD_TOKEN;os.replace(tmp,p)
assert all((R/name).read_bytes()==value for name,value in protected.items()) and h(B)==before
v=dict(epoch=time.time(),passed=True,own410_formal_final_and_candidate_collection_synced=True,current_SHA=h(p),canonical_SHA_exact_preserved=before,master_approval_tracks_RM004_exact=True,no_GPU_launch_or_budget_write=True)
for q in (D/'reports/ENTRY_FINAL_CLOSEOUT_METADATA_SYNCED.json',R/'E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_FINAL_CLOSEOUT_METADATA_SYNCED.json'):
 assert not q.exists();q.write_text(json.dumps(v,indent=2))
print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(NEWROOT)).replace('E_TOKEN',repr(io.E)).replace('B_TOKEN',repr(io.B)).replace('OLD_TOKEN',repr(oldsha)).replace('NEXT_TOKEN',repr(path)))
  save('ENTRY_FINAL_CLOSEOUT_METADATA_SYNCED.json',result)
 finally:io.cleanup(n,w)
 setting=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert setting['status']=='ACTIVE' and setting['rrule']=='FREQ=HOURLY;INTERVAL=1'
 oldprompt=D/('MONITOR_PREVIOUS_ENTRY_STARTUP_PROMPT_'+stamp+'.md');oldprompt.write_text(setting['prompt'],encoding='utf8')
 row=own['own_stage'];health=row['health']
 prefix=f'''最新source410自己的50mm reset-entry正式300s窗口已经自然完整保存退出，旧big/fresh/formalactive或仅CPUprepared均历史。owncheckpoint SHA{own['own_checkpoint']['sha256']}/{own['actual_publication']['source']['bytes']}B/actualCPU{own['actual_finite_tensor_count']}/source410/{own['own_snapshot_count']}actualmodule snapshots+410ownfreeze/ownPID{own['own_PID_bound_receipt']['pid']}/PASSED与unique原parent结清已actual核。实际control{health['control_steps']}，actor tensors改变{len(own['actual_actor_tensors_changed'])}/optimizerstepdelta{own['actual_optimizer_step_delta']}；完整数字health/raw/cost以本机ENTRY_OWN_FORMAL_CPU_ACTUAL与INITIALIZATION_REVIEWED_ACTUAL为准，不借CPU/fullsave称qualified50。actual父guardian孩子exit/twofcntl-free/active-Sactive空/E1_WAVE50_entry_saved_review_ready合法单scope审查边界，不复活任何oldmain/resume/SDK/native/PPO/fresh/once/budgettail。

中央E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_OWN_FORMAL_CPU_VERIFIED/FORMAL_FINAL_CURRENT_ACTUAL/FINAL_CLOSEOUT_METADATA_SYNCED与E1_WAVE50_ENTRY_CANDIDATE_ACTUAL_COLLECTION_{stamp}、{work.name}；current.rev004.wave50_entry_candidate_actual_scope实际优先。自己的new-entry SDK10实际10G4cells/native20k/128x2/20kx4完整discardPPO/freshsame50entry全部PASSED各一次不重GPU。来源accepted35 own369b026/CPU102/1293c97祖先，初formal先old35全actorcriticstdoptimizer/allD0D7/globalnamed/dictprivateCPUCUDA/terraincommand exact，再显式35→50actualassignment+entry/CUDAroundtrip/sourceepisode+1；terrainexactfalse是新scope披露，freshsameentry严格通过，未来same50entry全exact，非PhysXexactresume。entry只resetXY，原command/RNG/reward/DR/LR/hardware/clock/fullpose不变。

四case已实际自动publication，以自己的actualpublication/collect_entry_candidate_actual.py result与currentnamespaceattention优先，不假永久pending。仅actualcomplete/errorfree取两host8JSONbyteSHA/fullterrainNPZ/queryNPZ，review_entry_candidate_actual.py严格复用145/147原50mm十波2.406422727m/.4approach→两轮全十波200mmafter/80env1500controls15s与115/129三skill完整root30qparamsrecipesassignment/6000callbacks/query1e-6/actualgroundcontactintegralCOMhardware/1N支撑与位置/所有validprefix/originalstrictfalse/fullsignedcircle沿横dedrift/two4pi/直线原false。stand26无需通行，sameepisodeprereset-before排除teleport，不缩接近延15s。sensorfinal动态bias静态配方/.0075bound分列，ownfinite绑定实际CPU，不伪未落盘initialbias exact。

完整candidate+review_entry_direct147_prefix_actual.py+review_entry_complete_dynamic_family_trace_actual.py ownfulltrace才独立scope决定。dynamiccurrentrootcellfamily4与staticassignment/beforephysicscommands与afterupdatehist不同phase分列，rootcommandproxy非contact/fullroute/因果证书；原2m trainingroute不可容全3.006m frozen test，新entry只入口前段暴露。合理才同entry第二有界块<=2h/最多两块全审，系统性无改善独立诊断，不盲第三/70/qualified全WaveRM/MoE/permanentantiforgetting/无限hold/只队列。

全部newfinal/collection/fulltrace/读者errors/prepared未运行source/sync/monitor/Gitreceipt ordinarysupplement，entry410stage e6702ee/07f559已actualremote核验，后来Git以actualtracked/remote最终工具为准，不凭prompt假补齐。0051188000s330h/sevenextensions第七100h早once，无新扩展/复制/clearactive/tail/重结；actual预算账优先。E0/CURB20/WAVE35/SLOPE范围冻结/gate未训/S8另具体批准/WASD不GUI干预，完整fixed合同与Git要求详见新工作单及旧全文{oldprompt} SHA{H(oldprompt.read_bytes())}。mod4-10同heartbeat ACTIVE每1h同target，健康pending DONT_NOTIFY静默无commentary，仅实质阶段/真实修复/重大退化/完成/人类动作NOTIFY，无5minSSH/ping/Rich/其它monitor/自动预算，reviewready不删monitor仅实际预算结束且allfinal全完成才停止。

以下旧提示保留追溯，以上以及之后actual决定优先：

'''
 save('ENTRY_FINAL_HOURLY_MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=setting['name'],rrule=setting['rrule'],status='ACTIVE',targetThreadId=setting['target_thread_id'],prompt=prefix+setting['prompt']))
 print(json.dumps(dict(final_metadata_synced=True,monitor_request=str(R/'ENTRY_FINAL_HOURLY_MONITOR_UPDATE_REQUEST.json'))))

if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_FINAL_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
