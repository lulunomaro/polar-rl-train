"""CAS only this new entry-scope metadata; preserve master/approvals and never write canonical."""
from entry_io import *
import tomllib
NEWROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012'
def main():
 assert not (R/'ENTRY_METADATA_SYNCED.json').exists()
 latest=max(R.glob('INITIALIZATION_REVIEWED_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));v=json.loads(latest.read_bytes());assert v['root']==NEWROOT
 target=json.loads((R/'INITIALIZATION_REVIEWED_TARGET_CPU_PASSED.json').read_bytes());assert target['passed']
 work=R/'NEXT_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_ACTUAL_WORK_ORDER.md'
 with work.open('x',encoding='utf8') as f:f.write('''# Follow the actually dispatched reset-entry source410

Read newest numeric INITIALIZATION_REVIEWED_ACTUAL, targetCPU, dispatch, own scope receipts and later final results. The failed398 immutable scope ran GPU SDK initialization but failed before any control/PPO: its first10 default origins were nonWave and strict v1 entry_map rejected emptyWave. Original logs/error/attention/source and noPPO cost classification retained; parentguardianchild all naturallyexited, two actualfcntl locksfree and active-Sactiveempty before new source410. Do not resume or replay398controller/SDK. Source410 clones all398bytes and adds12 independent v2 files; no hotpatch. Initialization-safe v2 only permits exact unchanged origins for actual allnonWave small fixtures (n<20000); production20k with zeroWave remains rejected. When Wave origins exist, original strict v1 math is called byteexact. Actual source410 target CPU passed saved20k map f42f0b.../2820changed17180exact, origin mutation invalidation, strictsource/assignment/map/origin and fulloldCPU/private command fixture, smallpreplacementexact and emptyproduction20k rejection; no CUDA claims from CPU. Fullpose30q/normal/clearance/zero velocity AST exact except resetXY lookup; original geometry/DR/reward/LR/command/RNG consumption and2m route unchanged.

New unique controller410 actual PID/start/argv/cwd receipts supersede snapshots. Newentry SDK10 actual10G4 cells onbothsides afterplacement, fullflatfootprint andselectedreset300controls1200callbacks; then newnative20k24warm120timed480/576callbacks andfull144control trace bothsides signedgentle/standing, actual map/groundrewardformula/ordinary audit. These genuinely changed entry scopes run once, not replay old384SDK/native or398failedSDK. Source remains acceptedobserved35 own369b026/17615538B/CPU102 andcomplete1293c97 ancestor; never degraded219f/a67b/discard orotherexpert default warmstart. Explicit strictold35actorcriticoptimizerstd/allD0D7/globalnamed/dictprivateCPUCUDA terraincommand identity then35to50actualassignment+entryidentity migration/CUDA diskroundtrip/episode+1; subsequent same50+entry strict. New entry identity independently dictowned, no namedRNG set changes. Not PhysXexactresume.

Allown SDK/nativepass then new128x2 and20kx4 completePPO preflights once, originalparent unique canonicalcharged anddiscardweights, independentfreshsame50entry20k0control0PPO seed20260928/no optional logger save; only allpassed thenfirst300s formal loadlearnsaveexit/save25/15slocalguardian fromb026. Manifest-beforePPO original_write_dynamic binding retained, source filenames andactual snapshotpaths strict. Missingfuturefullsave/startup/health is pending, not proof orfault. Read ownfinal fullsave/PID/PASSED/CPUactualfinitecount/sourcefreeze/snapshots/uniqueaccount/actualparentguardianchildexit/twolocksfree/active-Sactiveempty. Legal E1_WAVE50_entry_saved_review_ready, notallcoursefinished orsupervisionfault. Never revive executed oldmain/resume/once/budgettail. Ifactualfailed, preserve raw error/cost and repair onlyindependentmissing contract; do not relabel orblindresume.

Parent automatically publishes ownfourcase using actualbothhostunused job number148 onlyifstillunused. Read actualpublicationnumber, neverpreclaim/republish. Completeerrorfree twohost8JSONbyteSHA/fullterrainraw/queryNPZ; strict145/147 derived50mmpeakvalley tenwaves2.406422727m/9m40original40mirror/.4approach/bothwheels fulltenwaves200mmafter/80env1500controls15s20260928white3. Allroot30qparametersrecipesassignment/6000callbacks/worldfloat32 triangles+independentquery1e-6/groundcontactintegralCOMlinkhardware oldtolerances;1N actualsupport andposition separately/allvalidordinary-before andincompleteprefixes/standing26 no crossing/coverage unionsnotcountsaddition/prereset-before excludesreset teleport. 115/129threelegacy cases/fullsignedcircle alongcrossdedrift/two4pi/straightoriginalstrictfalse preserved; ownfinite count boundtoownactualCPU, sensorfinaldynamicbias vsstaticrecipe/.0075bound separate, no unrecordedinitialbias exact. Pairdirect147 andaccepted35 source diagnostics, completeowntrainingtrace dynamiccurrentrootcellfamily4/beforephysicscommands vsafterupdatehist andphysicalepisode prereset-before. Rootcommandproxy notcontact/fullroute/causalproof; original2m trainingroute cannotcontain full3.006m frozen test, newentry proves approach/onsetpartial exposure only.

Owncandidate fullscope decision beforemorePPO/70/qualified50/RM/MoE/permanentantiforgetting. Justified same-entry secondbounded block onlyaftercompletebehaviorandtrace; ≤2h andmax2scopeblocks thenfullreview, noautomaticthirdblindblock/infinitehold/onlyqueue. E0/CURB20/SLOPE5-8-10/WAVE35 acceptedobserved scopes remainfrozen, gateuntrained/hardwareuncalibrated/S8specificlater/93-94paused/WASD no GUI/reset/restart/stop. 005canonical1188000s330h/sevenextensions seventh100h alreadyonce, no newbudget/copy/clear/tail/recharge/extend. Activeactualaccountedtail overridesidle snapshot. CPU/SDK/native/frozen/fresh0PPOnocharge; PPOloadlearnsaveexit failedstartup originalparentunique. Actualfcntl locknotfileexistence, no kill/hotpatch/dual20k/otherAI. Fixedmaster812a4b/RM003002001/004005/clock2.5msx4 TGS32-4/100Hz/35actor38critic6action/DRwhite_v3+noise_bias_mild_v1/healthv3ground1e-6contactCOMfullsignedcircle tolerances andotherexpertgate/min(18h,.13B) planningremain. No teacher/newtruthactor-gate/reward/commandaxis/pure/S7/S8/70-20-10.

Allsavedsource/false/raw/cost/failedCPUreaders/initialSDKfailure/prelaunchSyntaxError/resource8GiB rejection andmeasuredstorageguard/sync/monitor/finalcandidate/Gitreceipt mustGit. No evidence/cache deletion, original8GiBrejection kept andshortscope storage admitted by2xactualpriorwholeoutput+2GiB. Newrealrepairstage uniqueannotatedtrial actualremote main/tag/peeled; laterordinarysupplement/pushfailoriginalobjectsonly, no recordcommit/tag replay. LargeweightsNPZrawJSONUSDZIP onlyactualpathsizeSHA/originalskept, credentialsnotoutputGit. Hourlymod4-10 sameACTIVEtarget, quiethealthy/pending, notifymeaningfulrepair/failure/completion/humanaction; noextra5minSSH/ping/Rich/monitor/automaticbudget. Reviewready doesn'tendmonitor; stoponlyactualbudgetendandallfinal.
''')
 names={'E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_TARGET_CPU_VERIFIED.json':R/'INITIALIZATION_REVIEWED_TARGET_CPU_PASSED.json',
 'E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_SOURCE_FREEZE.json':R/'INITIALIZATION_REVIEWED_SOURCE_FREEZE.json',
 'E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json':R/'INITIALIZATION_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json',
 'E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_CURRENT_ACTUAL.json':latest,
 'E1_WAVE50_ENTRY398_FAILED_ACTUAL_REVIEW.json':R/'FAILED398_AND_INITIALIZATION_REVIEWED_BOUNDARY.json',
 'E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_RESET_AST_CPU_ACTUAL.json':R/'INITIALIZATION_REVIEWED_RESET_AST_AND_STRICT_RESTORE_CPU_ACTUAL.json',work.name:work}
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   for name,p in names.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
   raw=f.open(io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json','rb').read();oldsha=H(raw);current=json.loads(raw)
  rev=current['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_WAVE'
  rev['wave50_entry_reset_CPU_scope'].update(target_fullstate_CPU_admission=True,GPU_SDK_native_fullstate_PPO_formal_deployed=True,only_controller_deployed_all_actual_future_stage_receipts_required=True)
  rev['wave50_entry_initialization_reviewed_GPU_scope']=dict(root=NEWROOT,source_count=410,phase=(v['current_state'] or {}).get('phase'),actual_scope_at_collection_epoch=v['epoch'],source_SHA=SOURCE_SHA,
   actual_parent=v['actual_processes'][0]['actual'] if v['actual_processes'] else None,attention=v['reports'].get('E1_ATTENTION.json'),target_CPU_passed=True,
   failed398_zero_control_SDK_preserved=True,entry_initialization_only_small_nonWave_exact=True,strict20k_math_unchanged=True,
   formal_final_not_yet_claimed=True,entry_only_original_geometry_commands_RNG_DR_reward_LR_route_unchanged=True,
   target_CPU_ref=io.E+'/reports/E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_TARGET_CPU_VERIFIED.json',current_actual_ref=io.E+'/reports/E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_CURRENT_ACTUAL.json',next_work_order=io.E+'/reports/'+work.name)
  rev['active_next_phase']=rev['wave50_entry_initialization_reviewed_GPU_scope']['phase'];rev['latest_actual_scope']='wave50_entry_initialization_reviewed_GPU_scope'
  with n.open_sftp() as f:io.put(f,NEWROOT+'/reports/ENTRY_CURRENT_CAS_NEXT.json',json.dumps(current,ensure_ascii=False,indent=2).encode())
  sync=run(n,r'''from pathlib import Path
import json,time,hashlib,os
D=Path(ROOT_TOKEN);R=Path(E_TOKEN)/'reports';B=Path(B_TOKEN);protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert h(p)==SHA_TOKEN
before=h(B);raw=(D/'reports/ENTRY_CURRENT_CAS_NEXT.json').read_bytes();tmp=p.with_name('CURRENT_entry410_'+str(time.time_ns())+'.tmp');tmp.write_bytes(raw);assert h(p)==SHA_TOKEN;os.replace(tmp,p)
assert all((R/n).read_bytes()==raw for n,raw in protected.items())
v=dict(epoch=time.time(),passed=True,entry410_actual_dispatch_CPU_and_failed398_synced=True,current_SHA=h(p),canonical_SHA_before=before,canonical_SHA_after=h(B),canonical_never_written_by_sync=True,master_approval_tracks_RM004_exact=True,no_GPU_launch_or_budget_write=True)
for q in (D/'reports/ENTRY_METADATA_SYNCED.json',R/'E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_METADATA_SYNCED.json'):assert not q.exists();q.write_text(json.dumps(v,indent=2))
print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(NEWROOT)).replace('E_TOKEN',repr(io.E)).replace('B_TOKEN',repr(io.B)).replace('SHA_TOKEN',repr(oldsha)))
  save('ENTRY_METADATA_SYNCED.json',sync)
 finally:io.cleanup(n,w)
 setting=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert setting['status']=='ACTIVE' and setting['rrule']=='FREQ=HOURLY;INTERVAL=1'
 oldprompt=D/'MONITOR_PREVIOUS_ENTRY_CPU_ONLY_PROMPT.md'
 with oldprompt.open('x',encoding='utf8') as f:f.write(setting['prompt'])
 prompt=f'''最新实际：已独立部署50mm入口修复source410，root={NEWROOT}，本机{D}/reports最新数字INITIALIZATION_REVIEWED_ACTUAL及自己的futurefullsave/PID/PASSED/actualphase优先。首controller3064496-start90661954只是定位，之后actual/proc argv/cwd/start/孩子/result/ownreceipt优先，不盲信号或假永久active。targetCPU410/fulloldsource102/20kmap2820changed17180exact/actualoriginmutation与smallpreplacementnonWaveexact/emptyproduction20k strictreject/resetAST原fullpose仅XY改变已实际通过。

旧source398首次SDK在控制循环前真实failed：RslRl wrapper初reset在10env迁入Wave格前，严格v1 entry_map因无Wave起点拒绝。原源码/log/error/attention/无PPO原分类保存，actual父guardian孩子全自然exit/两fcntl锁free/noactive以后才新410；不重398main/SDK/once。410=398全部原bytesexact+12独立v2files，只允许实际无Wave的小初始化保持原XYexact，20k无Wave仍拒绝，有Wave仍用原v1严格数学byteexact；非放松physics/fullstate/source/RNG阈值。

先读中央E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_TARGET_CPU_VERIFIED/SOURCE_FREEZE/DISPATCH_ACTUAL_RECEIPT/CURRENT_ACTUAL/RESET_AST_CPU_ACTUAL、E1_WAVE50_ENTRY398_FAILED_ACTUAL_REVIEW及{work.name}，current.rev004.wave50_entry_initialization_reviewed_GPU_scope实际优先。当前收集phase={(v['current_state'] or {}).get('phase')}、attention={bool(v['reports'].get('E1_ATTENTION.json'))}，是当时snapshot而非未来结果。自己的SDK/native/CUDA/PPO/fresh/formal须真实receipt通过，不能借CPU或进程冒正式训练/毕业。

新controller唯一自动new-entry SDK10实际10G4两侧完整flatfootprint/selectedreset300control1200callback→newnative20k24warm120timed480/576callback/actualmap-groundrewardformula-two signedstanding fulltrace→新128x2/20kx4 fullPPOdiscard一次同canonical→freshsame50entry20k0control0PPO seed20260928 fullCPUCUDA strict→首300sloadlearnsaveexit/save25/15sguardian。已ownpassedstage不重跑。完整来源acceptedobserved35 own369b026/CPU102/祖先1293c97，旧35全部actorcriticstdoptimizer/allD0D7/globalnamed/dictprivateCPUCUDA/terraincommand先exact，再显式35to50assignment+entrydictidentity/CUDA磁盘roundtrip/savedsourceepisode+1；后same50entry严格exact，非PhysXexactresume。来源非219f/a67b/discard或其它expert。原2m route、命令±.3yaw0 standing.2/RNG消耗、DRrewardLRhardwareclock全不变，entry前段暴露非全十波认证。所有未来actualstage读者按工作单积极运行；旧once/main/resume/预算/record/sync禁止重跑，missingfuture合法pending，真实失败保留error/raw/cost独立诊断，不hotpatch/kill/dual20k/clearactive。

ownfullsave/PID/PASSED/actualCPUfinitecount/完整snapshot+410ownfreeze/unique原parent结清/实际parentguardianchildexit/两锁fcntl-free/active-Sactive空才new四case，用实际publishnumber，两hostunused已核148但不盲重发或预claim。完整145/14750mm峰谷十波2.406422727m/9m镜像/.4approach→两轮全十波200mmafter/80env15s20260928white3，全root30qparamsrecipesassignment6000callbacks/worldfloat32triangle query1e-6/contactintegralCOMhardware/1N支撑与位置/所有有效prefix/no resetteleport/standing26与115/129fullsignedcircle沿横dedrift/two4pi/直线原false/sensorfinaldynamicbias静态配置分列/.0075bound保持。ownfinite绑定actualCPU不借旧count。完整candidate+trainingdynamicfamilyfulltrace决定前不更多PPO/70/qualified50/RM/MoE/永久抗遗忘；合理才同entry有界第二块，≤2h/最多两块全审，不第三盲块/无限hold/只队列。

本次所有preCPU读者/anchor/路径/外部asset/import/fixture错误与prelaunchSyntaxError/8GiB资源拒绝原件保留，后按实际priorwholeoutput2倍+2GiB独立空间核验通过，无删除raw/weights/source/cache。新scope已真实dispatch，旧“仅entryCPU/未GPU”只历史；147正5/27倒25/27notqualified、35正反27/27/CURB20/SLOPE接受ONLYobserved范围及E0冻结保持。005canonical1188000s330h/sevenextensions第七100h早已唯一应用，无加时/预算事务，actualactive/accounted真实尾段优先；PPOloadlearnsaveexit failedstartup原parent唯一扣，CPU/SDK/native/frozen/fresh0PPO不计。gate未训/硬件未标定/S8另具体批准/93-94paused/WASD播放器不GUI/reset/stop/restart。所有fixed合同和Git要求详见工作单及旧全文{oldprompt} SHA{H(oldprompt.read_bytes())}，actual最新优先。

所有savedsource/成功失败false/raw/cost/读者schema/拒绝/部署/同步/monitor/workorder/futureownfinal/candidate/Gitreceipt持续Git，新真实阶段唯一record_experiment annotatedtrial，actualtracked/remote main/tag/peeled最终工具证明；pushfailed续已有objects不重record/tag/commit，后receiptordinarysupplement，largePTNPZrawJSONUSDZIP只actualpathsizeSHA原件保持，credentials不输出Git，Git非训练依赖。此前eace7eb/0e7f与945c684已核保留，新stage以ENTRY_STAGE_GIT_RECORDED及actual工具优先，不凭prompt假报。

mod4-10同heartbeat ACTIVE每1h同target，健康pending DONT_NOTIFY静默无commentary，只实质阶段/真实修复/重大退化/完成/人类动作NOTIFY，不5minSSH/ping/Rich/其它monitor/自动预算；单scope reviewready不删monitor，仅预算真正结束且actualfinal全完成才停止。
'''
 save('ENTRY_HOURLY_MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=setting['name'],rrule=setting['rrule'],status='ACTIVE',targetThreadId=setting['target_thread_id'],prompt=prompt))
 print(json.dumps(dict(metadata_synced=True,monitor_request=str(R/'ENTRY_HOURLY_MONITOR_UPDATE_REQUEST.json'))))
if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
