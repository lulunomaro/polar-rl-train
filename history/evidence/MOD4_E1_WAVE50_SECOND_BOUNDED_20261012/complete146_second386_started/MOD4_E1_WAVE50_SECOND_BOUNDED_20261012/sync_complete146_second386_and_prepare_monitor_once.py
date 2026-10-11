"""One metadata CAS only; no trainer, evaluation or budget transaction."""
from second50_io import *
import tomllib

def latest(pattern):return max(R.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))

def main():
 assert not (R/'COMPLETE146_AND_SECOND386_METADATA_SYNCED.json').exists()
 decision=json.loads((PRIOR/'reports/WAVE50_146_COMPLETE_SCOPE_DECISION.json').read_bytes());assert decision['full_four_cases_complete_errorfree_and_raw_reviewed'] and decision['not_qualified50mm_scope']
 actualpath=latest('SECOND50_ACTUAL_[0-9]*.json');actual=json.loads(actualpath.read_bytes());assert actual['actual_owner'] and actual['actual_child'] and not actual['reports'].get('E1_ATTENTION.json')
 startup_path=latest('SECOND50_OWN_STARTUP_CONTRACT_ACTUAL_[0-9]*.json');startup=json.loads(startup_path.read_bytes());assert startup['passed'] and startup['source_count']==386 and startup['source_SHA']==SOURCE_SHA
 work=R/'NEXT_E1_WAVE50_SECOND_BOUNDED_FULL_ACTUAL_REVIEW_WORK_ORDER.md'
 with work.open('x',encoding='utf8') as f:f.write(f'''# Same50 second1800s dispatched with actual strict CUDA fullrestore; complete own final and candidate before next axis

Read SECOND_TARGET_CPU_PASSED, SOURCE_FREEZE, REUSED_ACTUAL_CONTRACTS, DISPATCH_ACTUAL_RECEIPT, latest numeric SECOND50_ACTUAL and SECOND50_OWN_STARTUP_CONTRACT_ACTUAL. Source386 root {ROOT} preserves all384 bytes plus only a truthful same50-manifest worker and uniquecontroller. Initial full source {SOURCE} SHA{SOURCE_SHA}/17615730B/CPU102; original35 b026 and ancestor1293c97 identity preserved. Strict same50 full actorcriticstdoptimizer/allD0D7/globalnamed/dictprivateCPUCUDA/geometrycommand restore, seven own startup receipts, actual CUDA disk roundtrip and saved-source episode+1 actually passed; terrainexacttrue/newG3false/commandpredecessorexacttrue/newcommandfalse. Non-PhysX exact resume. Never hardcode first35to50 transition or borrow oldbig/fresh proof as this formal proof.

Complete146 actualreview is forward7/27 reverse25/27, ordinary0/route7/closure1.325404970mm, allfour completeerrorfree. Full183035056B raw SHA6669ff5659662b387f7c38fe8a6c4bd8c9b06c98dc58f5d45210fee0f5be1f45 and twohost8JSON/fullquery exact. Complete145 frozen50 baseline11/23 and all146 validprefix/oldskill strictfalse retained. Positioncomplete and original1N two-wheel pre/postsupport agree independently. Initial384 training144controls only1.44s/env, nominalmaxcommand .432m; inadequate route exposure is a testable inference, not causality. Rootcommand proxy not contactcertificate. This is one new second same50 exposure block1800s including loadlearnsaveexit/save25/15s localguardian, 20k/24controlsupdate, unique canonical. No SDK/native/small/big/fresh/clock/DR replay: all actualoriginal path-size-SHA reused. Source checkpoint/E0/CURB/SLOPE/WAVE35 and otherexpert outputs untouched.

Read read_second50_actual.py and verify_second50_startup_save_cpu_actual.py only according to actualstage. Missing future save/health is legal pending. A generated save positive actor/optimizer delta is active PPO proof, not ownfinal. Once own e1_WAVE50_second_bounded_observation_PASSED/fullsave/source386/actualsnapshots+ownfreeze/CPU102/ownPID/unique segment and actual parentguardianchildexit/two fcntl-free/noactive are available, run read_second50_own_formal_cpu_actual.py. Legal E1_WAVE50_second_bounded_saved_review_ready is not a supervisor failure/coursefinished; never revive any oldmain/resume/once or ledger tail.

Parent automatically publishes actual unused candidate number, only read own publication then collect_second50_candidate_actual.py. Prepared review_second50_candidate_actual.py reuses145 same50 worldfloat32 triangle/query identity and original1e-6, full tenwaves2.406422727m/.4approach/bothwheel200mmafter/80env1500controls15s/20260928white3, allroot30q-paramsrecipesassignments/6000callbacks/groundcontactintegralCOMlinkhardware originaltolerance. Original1N contact andposition separate, standing26 no crossing, all validordinary-before/incompleteprefix and declaredtruncationcoverage, prereset-before/samephysicalepisode exclude resetteleport; no windowextension/approachshortening/relabeling. Finalsensor mutablebias/staticrecipe separate with original.0075bound/finite; no nonexistentinitialbias exactclaim. Legacy115/129 D7 actualinitialization/fullsignedcircle alongcrossdedrift/two4pi/straightstrictfalse and strict reset-audit actualschema unchanged. ActualCPUcount bound ownfinal, source count386 not384/102 assumption.

After own complete collection+review, separately directly pair146 allfour actual q30/params/staticrecipes/assignments/fullraw and perenv completion/prefix/1N contacts (145 remains original geometry reference); audit full saved dynamic-current-rootcell family4/signedgentle+standing and commands-beforephysics vs hist-afterupdate with review_second50_complete_dynamic_family_trace_actual.py. ActualtraceNPZ indices only Git, no GPU rerun. Rootproxy is not fullroute or contactproof. Decide complete second scope before any new training or70mm. No automatic third same50 duration-only block. If systematic residual remains, end this same-scope PPO and actively prepare one independently justified trajectory/entry/command axis or other approved nextscope, no indefinitehold/queue and no blindthird. Accepted35/CURB20/SLOPE ranges remainfrozen, gateuntrained, no wholeRM/MoE/antiforgetting claim.

005solecanonical1188000s330h/sevenextensions already applied, actualactive/accounted/tail supersedes idle snapshot; unique originalparent loadlearnsaveexit only, no extension/copy/clearactive/retail/recharge. CPU/SDK/native/frozen/fresh0PPO nocharge. Twoactualfcntl locks, no deletion/kill/hotpatch/dual20k/otherAI/WASD intervention. OriginalclockDRrewardLRhardware/fivefamilies/commands/healthv3/ground1e-6/contactCOM/fullsignedcircle thresholds unchanged, otherexpert/gate/min(18h,.13B) planning protected withoutledgerreserve. Allsavedsuccess/false/raw/cost/schemaerrors/source/sync/monitor/workorders/Gitreceipts mustGit, newstage once annotatedtrial actualremote main/tag/peeled, laterordinarysupplements; largeweightsNPZrawJSONUSDZIP indicesonly originalsretained, credentialsnotoutput/Git, pushfailure onlyexistingobjects. SamehourlyACTIVE mod4-10 quiethealthy, no5min/extramonitor/automaticbudget, reviewready nottermination.
''')
 files={
 'E1_WAVE50_CANDIDATE146_COMPLETE_ACTUAL_COLLECTION.json':Path(decision['collection']),
 'E1_WAVE50_CANDIDATE146_COMPLETE_ACTUAL_REVIEW.json':Path(decision['review']),
 'E1_WAVE50_CANDIDATE146_COMPLETE_SCOPE_DECISION.json':PRIOR/'reports/WAVE50_146_COMPLETE_SCOPE_DECISION.json',
 'E1_WAVE50_CANDIDATE146_COMPLETE_PREFIX_CONTACT_EXPOSURE_DIAGNOSIS.json':Path(decision['diagnosis']),
 'E1_WAVE50_CANDIDATE146_READER_RESET_SCHEMA_REVIEW.json':PRIOR/'reports/CANDIDATE146_RESET_SCHEMA_READER_REVIEW.json',
 'E1_WAVE50_SECOND_BOUNDED_TARGET_CPU_VERIFIED.json':R/'SECOND_TARGET_CPU_PASSED.json',
 'E1_WAVE50_SECOND_BOUNDED_SOURCE_FREEZE.json':R/'SOURCE_FREEZE.json',
 'E1_WAVE50_SECOND_BOUNDED_REUSED_ACTUAL_CONTRACTS.json':R/'REUSED_ACTUAL_CONTRACTS.json',
 'E1_WAVE50_SECOND_BOUNDED_DISPATCH_ACTUAL_RECEIPT.json':R/'DISPATCH_ACTUAL_RECEIPT.json',
 'E1_WAVE50_SECOND_BOUNDED_DISPATCH_CURRENT_ACTUAL.json':actualpath,
 'E1_WAVE50_SECOND_BOUNDED_OWN_STARTUP_CONTRACT_VERIFIED.json':startup_path,
 'E1_WAVE50_SECOND_BOUNDED_LOCAL_WBX_READER_REJECTION_REVIEW.json':R/'LOCAL_CANDIDATE_RECEIPT_WBX_REJECTION_REVIEW.json',
 'E1_WAVE50_SECOND_BOUNDED_LOCAL_PATH_READER_REJECTION_REVIEW.json':R/'CPU_LOCAL_PATH_READER_REJECTION_REVIEW.json',
 work.name:work}
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   for name,p in files.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
   raw=f.open(io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json','rb').read();oldsha=H(raw);current=json.loads(raw)
  rev=current['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_WAVE'
  rev['wave50_candidate146_actual_scope'].update(phase='candidate146_complete_reviewed_not_qualified50mm',review_complete=True,pending=[],forward_complete=7,reverse_complete=25,each_direction=27,ordinary=0,route_declared_truncations=7,full_raw=decision['full_raw'],complete_collection_ref=io.E+'/reports/E1_WAVE50_CANDIDATE146_COMPLETE_ACTUAL_COLLECTION.json',complete_review_ref=io.E+'/reports/E1_WAVE50_CANDIDATE146_COMPLETE_ACTUAL_REVIEW.json',complete_scope_decision_ref=io.E+'/reports/E1_WAVE50_CANDIDATE146_COMPLETE_SCOPE_DECISION.json',diagnosis_ref=io.E+'/reports/E1_WAVE50_CANDIDATE146_COMPLETE_PREFIX_CONTACT_EXPOSURE_DIAGNOSIS.json',not_qualified50mm_scope=True,all_original_false_and_prefix_preserved=True)
  rev['wave50_second_bounded_scope']=dict(root=ROOT,source_count=386,phase=actual['reports']['E1_STATE.json']['phase'],source_checkpoint_SHA=SOURCE_SHA,original35_lineage_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd',target_CPU_passed=True,own_actual_parent=actual['actual_owner'],own_actual_child=actual['actual_child'],seconds=1800,only_duration_exposure_axis=True,same50_geometry_commands_DR_reward_LR=True,all_preflight_clock_SHA_reused_no_replay=True,own_same50_CUDA_fullrestore_and_episode_plus_one_actual_passed=True,own_formal_final_not_yet_claimed=True,no_automatic_third_block_or70mm=True,new_budget_seconds=0,reports={name:dict(path=io.E+'/reports/'+name,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for name,p in files.items()},latest_actual_own_receipts_override_snapshot=True)
  rev['active_next_phase']=rev['wave50_second_bounded_scope']['phase'];rev['latest_actual_scope']='wave50_second_bounded_scope'
  with n.open_sftp() as f:io.put(f,ROOT+'/reports/COMPLETE146_SECOND386_CAS_NEXT.json',json.dumps(current,ensure_ascii=False,indent=2).encode())
  v=run(n,r'''from pathlib import Path
import json,time,hashlib,os
D=Path(ROOT_TOKEN);R=Path(E_TOKEN)/'reports';B=Path(B_TOKEN);before=B.read_bytes();protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';h=lambda q:hashlib.sha256(q.read_bytes()).hexdigest();assert h(p)==SHA_TOKEN
raw=(D/'reports/COMPLETE146_SECOND386_CAS_NEXT.json').read_bytes();tmp=p.with_name('CURRENT_second50_'+str(time.time_ns())+'.tmp');tmp.write_bytes(raw);assert h(p)==SHA_TOKEN;os.replace(tmp,p)
assert B.read_bytes()==before and all((R/name).read_bytes()==raw for name,raw in protected.items())
v=dict(epoch=time.time(),passed=True,complete146_notqualified_and_actualsecond386_synced=True,current_SHA=h(p),canonical_SHA=hashlib.sha256(before).hexdigest(),master_approval_tracks_RM004_exact=True,no_GPU_PPO_budget_write_or_old_sync_replay=True)
for q in (D/'reports/COMPLETE146_AND_SECOND386_METADATA_SYNCED.json',R/'E1_WAVE50_COMPLETE146_AND_SECOND386_METADATA_SYNCED.json'):assert not q.exists();q.write_text(json.dumps(v,indent=2))
print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('E_TOKEN',repr(io.E)).replace('B_TOKEN',repr(io.B)).replace('SHA_TOKEN',repr(oldsha)))
  save('COMPLETE146_AND_SECOND386_METADATA_SYNCED.json',v)
 finally:io.cleanup(n,w)
 setting=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert setting['status']=='ACTIVE' and setting['rrule']=='FREQ=HOURLY;INTERVAL=1'
 previous=D/'MONITOR_PREVIOUS_COMPLETE146_PROMPT.md'
 with previous.open('x',encoding='utf8') as f:f.write(setting['prompt'])
 prompt=f'''最新actual优先：146四case已actualcomplete/errorfree/fullraw独立完整审查，正向7/27倒退25/27/ordinary0/route7/closure1.325404970mm，未qualified50；旧146partial/pending和384formalactive都历史。完整raw183035056B SHA6669ff5659662b387f7c38fe8a6c4bd8c9b06c98dc58f5d45210fee0f5be1f45/twohost8JSON/root30q-paramsrecipesassignment/6000callbacks/actualqueryground1e-6/contactintegralCOMhardware全核。原1N前后两轮接触支撑与位置完成逐episode吻合，全部有效未完成prefix/原strictfalse保留。145冻结50mm前11倒23与146前7倒25分别保留，不称改善或毕业。负4pi0/8正4/8/world63/64/maxcross.052828551/直线±1.5误差.066670597/.048466872，E0冻结/gate未训，不作E0替换或router故障。

已积极实际唯一dispatch新的同50mm第二1800s窗口，root={ROOT}/source386=384全部oldbytesexact+一个仅真实same50manifest披露worker和uniquecontroller，stage/main/dispatch/once已经执行禁止复跑或--resume。首parent3010516-start89921988/child3010588-start89922117仅定位，以actual/proc argv/cwd/start/ownfullsave/PIDreceipt/phase优先。当前bounded_E1_WAVE50_second_bounded_learning/attentionnull，七ownstartup fullsame50 CPUCUDA磁盘roundtrip/sourceepisode+1已真实通过；terrainexacttrue/newG3false/commandpredexacttrue/newcommandfalse，不套384初35→50字段，不PhysXexactresume。来源own384model32264 SHA{SOURCE_SHA}/17615730B/CPU102，original35b026及1293c97完整祖先身份保持；不是discard/其它专家默认暖启动。ownfinal尚未生成不能称formalcomplete或毕业，missingfuture保存/health合法pending。

先读中央E1_WAVE50_CANDIDATE146_COMPLETE_ACTUAL_COLLECTION/COMPLETE_ACTUAL_REVIEW/COMPLETE_SCOPE_DECISION/COMPLETE_PREFIX_CONTACT_EXPOSURE_DIAGNOSIS/READER_RESET_SCHEMA_REVIEW、E1_WAVE50_SECOND_BOUNDED_TARGET_CPU_VERIFIED/SOURCE_FREEZE/REUSED_ACTUAL_CONTRACTS/DISPATCH_ACTUAL_RECEIPT/DISPATCH_CURRENT_ACTUAL/OWN_STARTUP_CONTRACT_VERIFIED、E1_WAVE50_COMPLETE146_AND_SECOND386_METADATA_SYNCED与{work.name}，本机{R}最新数字SECOND50_ACTUAL/STARTUP/未来OWN_FORMAL优先。current.rev004.wave50_second_bounded_scope才当前范围，旧未部署不复活。原stage本地重复wbxreceipt拒绝在remote源已部署后但CPU/GPU前、独立续未执行CPU的Path+str TypeError、原146legacyspin reset_audit缺字段误零读者错误及独立严格actualschema修复全部保存，非生产物理失败。独立仅完成未执行CPU和唯一dispatch，未重GPU/旧once。

本轴只增加路线有效训练暴露。初384完整144control=1.44s/env/.3名义最大积分.432m不足全十波2.406422727m+.4approach+.2after，仅可检验推断无因果消融，rootproxy非接触证书。second1800s含loadlearnsaveexit/save25/15slocalguardian/20k24controlupdate；原SDK10实际10G4格/native20k/small128x2/big20kx4/freshsame50及clock/DR/hardware所有ownPASSED原path-size-SHA精确复用，不重复预检/45minclock。完整actorcriticstdoptimizer/allD0D7/globalnamed/dictprivateCPUCUDA/geometrycommand严格same50恢复，旧named集合/assignment/privateRNG不放宽。来源219f模型不覆盖，E0/CURB/SLOPE/WAVE35不入optimizer或输出。

积极用read_second50_actual.py/verify_second50_startup_contract_actual.py/verify_second50_startup_save_cpu_actual.py仅读actualstage，活动保存正actor/optimizerdelta只是PPO证据非final。ownfullsave/PASSED/source386/actualsrcsnapshot+ownfreeze/CPU102/ownPID/唯一原parent结清及实际parentguardianchildexit/twofcntl-free/active-Sactive空后read_second50_own_formal_cpu_actual.py核完整边界；E1_WAVE50_second_bounded_saved_review_ready合法单课审查非故障/全课程finished，不复活main/once/预算tail。原parent自动新actualcandidate四case，用publication实际number；stage和dispatch已actual两hostqueue/results/jobs无占用核新147，未发布时合法pending，不能盲重发146/145/144/所有旧validcomplete/failed。

collect_second50_candidate_actual.py仅actualcomplete/errorfree twohost8JSONbyteSHA/fullterrainNPZ/queryNPZ；review_second50_candidate_actual.py严格复用145同50峰谷十波/9m镜像/.4前接近/两轮完整十波200mmafter/80env1500controls15s20260928white3、allroot30q-paramsrecipesassignments/6000callbacks/实际float32worldtriangles query1e-6/groundcontactintegralCOMhardware原容差。stand26不要求通行，原1Ncontact与position分列、所有有效ordinary前/未完整prefix、声明truncation两coverageexact/不重叠counts相加，sameepisodeprereset-before排除resetteleport，不缩接近/延15s/重标原失败。115/129三skill完整signedcircle alongcross-dedrift/左右4pi/直线原false保留，legacyreset按实际schema严格，不缺字段冒0。sensorfinal动态bias与静态配方分列/.0075bound/finite不松，不伪未落盘initialbias exact。准备读者不是futurepass，任何reader错误保留独立修不重GPU。完整四case后再直接配对146全初态/参数/staticrecipes/assignments/逐envprefix，并review_second50_complete_dynamic_family_trace_actual.py核全部NPZ原SHA/动态currentrootcell family4/两signedstanding/prereset-before/beforephysicscommand与afterupdatehist不同phase；rootproxy非contact/fullroute证书。

第二50块完整行为+ownfulltrace决定前不更多PPO/70/qualified50/全RM/MoE/permanentantiforgetting。最多两同scope块已用初300+本1800，不自动第三盲duration-only块；系统性残差无改善结束此same50PPO，积极独立轨迹/入口/命令轴合同诊断或下一004005批准单轴，不能无限hold/只队列。35mmown369b026正反27/27/CURB20own4247b上下27/27/SLOPEown24b5-8-10上下27/27 ONLY observed范围和E0保持冻结；STAIR/真实RM新geometry先核，gate未训/硬件未标定/S8后续具体批准/93-94paused，WASD播放器勿GUI按键/R/reset/停止/重启。

005solecanonical={io.B}总1188000s330h/sevenextensions第七100h早唯一登记。本scope实际active原parent正常扣loadlearnsaveexit/accounted和未accounted真实尾段，CPU/SDK/native/frozen/fresh0PPO不计，旧idle670233.654仅历史；不追加/复制/clearactive/重tail/重结/扩展/加时，<=120安全余不称0。两锁canonicalroot/native_floor_supervisor.lock和MOD4_scut_spin_rate_20261002/autonomy_controller.lock以fcntl实际held判非文件exists，不删锁/kill/hotpatch/dual20k/其它AI干预，父故障trainer活跃先保护保存修监督。其他expert/gate/min(18h,.13B)修复规划保护无ledgerreserve，每块<=2h。004独立actorcriticoptimizerstd/fullDR/RNG/queuesgeometrycommand/output/save，合格才hardtop1一tick完整6action，不平均动作参数/新层级gate/env_id-assignment-futurecontact真值actor-gate。

master812a4b/历史approvaltracks/RM003002001保持，2.5msx4/TGS32-4/100Hz/5msbin3history/35actor38critic6action/LR1e-4adaptiveKEEPSTD1/rewardhardware/allD0D7/plane30+20/20/15/15不变。实际clearplaneassignment/rootwheel支撑/1m净空条件signedstraightabs1–1.5/worldV.5yaw±1–2/standing.2；nonplane±.3yaw0/command12–16s/episode20s，不改命令轴。DRwhite_v3+noise_bias_mild_v1原强度，RM_DR_OFF1仅旧monolithic关闭不关独立DR，无strongpush/newarmature/jointfriction已随机化假称。无pure/teacher/S7/S8/70-20-10。healthv3closure2mm单envordinaryreset继续PPO，mimic.01/nonfiniteunknownmissingcallbackcoverage ownSTOP_AFTER_SAVE，ground1e-6/contact1N/COMhardware/fullsignedcircle tolmax(.03,.1V)/signedyaw±.2/worldBODYvx2Vcos(theta-alpha)vy0/nopositioncorrection不变，不用SCUT10.25mm/人工90-95-100线。RM003起伏10→20→35→50→真实70mm峰谷/坡5-8-10；RM002外缘实际高度分别准入/RM001spin净空洞台阶台面排除/有限网格1.4373mm保持。

3060健康namespace E1_WAVE50_QUERY_REVIEW worker17688只历史定位，actualCIM/argv/creation/children/result/attention/sharedOSlock优先，146complete后无GPU孩子合法idle，不重启healthy。singleGPUlock/restrictedbridge/JSONboundedretry/demand0trigger/noperiodic/noboot/no4090launch/no canonicalwrite/baseguard不变；136/144失败及119/121/125/所有旧false/raw/cost保留。所有旧once/stage/main/resume/SDK/native/PPO/fresh/record/sync/budgettail执行后不可重跑，仅读actualstage可复用。

所有savedsource/成功失败false/raw/cost/reader-schema/拒绝/未采用/部署/sync/monitor/workorders/Gitreceipt持续Git，workspace/repoAGENTS与ALL_TRIALS_AND_REPORTS_GIT_POLICY/NEXT_AI_GIT_WORKFLOW优先。新386真实阶段唯一record_experiment annotatedtrial，以SECOND_STAGE_GIT_RECORDED与actualremote main/tag/peeled为准不能凭文字假补齐；完整146/新sourceCPU/errors/dispatch/startup/未来ownfinal/候选/fulltrace及后Gitreceipt普通supplement，全oldtagobjects保持。largeweightsNPZrawJSONUSDZIP只actualpathsizeSHA原件保持，credentials仅临时env不输出不Git，pushfail仅已有objects不重record/tag/commit，Git非训练依赖。健康无新savedreport不造trial。此前完整prompt在{previous} SHA{H(previous.read_bytes())}仅历史追溯。

mod4-10同一heartbeat ACTIVE每1h/同target，healthy pendingDONT_NOTIFY静默无commentary，仅实质阶段/真实修复/重大退化/完成/人类动作NOTIFY，无5minSSH/ping/Rich/其它monitor/自动预算。reviewready不是全课程finished不删monitor，只有预算真正结束且actualfinal全完成才停止。
'''
 (D/'MONITOR_CURRENT_SECOND50_PROMPT.md').write_text(prompt,encoding='utf8')
 save('MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=setting['name'],rrule=setting['rrule'],status='ACTIVE',targetThreadId=setting['target_thread_id'],prompt=prompt))
 print(json.dumps(dict(metadata_passed=True,second_actual_dispatched_and_startup_CUDA_passed=True,monitor_request=str(R/'MONITOR_UPDATE_REQUEST.json'))))
if __name__=='__main__':
 try:main()
 except BaseException:save('COMPLETE146_SECOND386_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_budget_or_old_sync_replay=True));raise
