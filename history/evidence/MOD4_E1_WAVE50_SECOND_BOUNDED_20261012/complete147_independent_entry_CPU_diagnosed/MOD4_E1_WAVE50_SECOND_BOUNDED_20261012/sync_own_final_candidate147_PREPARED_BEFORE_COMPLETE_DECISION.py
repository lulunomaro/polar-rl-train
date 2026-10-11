"""Closeout metadata and latest actually reviewed candidate; no training launch."""
from second50_io import *
import tomllib

def latest(pattern):return max(R.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))

def main():
 assert not (R/'FORMAL_FINAL_CLOSEOUT_METADATA_SYNCED.json').exists()
 final_path=R/'SECOND50_FORMAL_FINAL_ACTUAL_REVIEW.json';final=json.loads(final_path.read_bytes());assert final['passed'] and final['closeout_ready'] and final['source_count']==386
 cpu_path=latest('SECOND50_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json');startup_path=latest('SECOND50_OWN_STARTUP_CPU_ACTUAL_[0-9]*.json');trace_path=latest('SECOND50_FULL_TRAINING_TRACE_ACTUAL_[0-9]*.json');actual_path=latest('SECOND50_ACTUAL_[0-9]*.json');review_path=latest('SECOND50_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json');review=json.loads(review_path.read_bytes());collection_path=Path(review['collection']);assert review['own']['checkpoint']['sha256']==final['own_checkpoint']['sha256']
 work=R/'NEXT_E1_WAVE50_CANDIDATE147_COMPLETE_AND_AXIS_DECISION_WORK_ORDER.md'
 with work.open('x',encoding='utf8') as f:f.write(f'''# Own386 second50 fullsave closed; finish147 and decide a justified next axis

Read SECOND50_FORMAL_FINAL_ACTUAL_REVIEW, latest ownCPU/startup/fulltrace/actualcollection/candidate collection-review and later actual. Ownsource386 model32357 SHA{final['own_checkpoint']['sha256']}/17615730B/CPU102/actual81 module snapshots+386 fullsourcefreeze/PID3010588, actual94updates2256controls45.12Menvsteps9024callbacks. Unique{final['actual_load_learn_save_exit_seconds']}s includesloadlearnsaveexit originalparent once settled. Ordinary1 base_contact atcontrol1412/env18887 preserved, integrityunknown0/nonfinitefalse/STOPnone/closure1.221559010mm/mimic.001691456rad. timeout15963/route17091/overlap8/unique33046 withbothreasoncoverageexact; never sumcounts asunion. Actualparentguardianchildgone/twofcntl-free/active-Sactiveempty legal E1_WAVE50_second_bounded_saved_review_ready, not supervisorfailure/coursefinished. Never revive oldmain/resume/once or budgettail.

Seven fullsame50 startup andactual CPUCUDA roundtrip/episode+1 verified, sourceown384219f andorigin35b026/ancestor1293c97 identities remainstrict. Terrainexacttrue/newG3false/commandpredexacttrue/newscopefalse, nonPhysXexactresume. Original50 SDK/native/smallbig/fresh andclockDR preflights reusedexactSHA, no replays. All5 savedtraceNPZ exactpath-size-SHA; actual2256controls22.56s/env/maxcontiguousphysicalepisode20s, dynamiccurrentrootcellfamily4 withnegative2418053/positive2503484/standing1440383 controls, allsamecontrolprereset-before excludesresetteleport, beforephysicscommands vsafterupdatehist notforcedsamephase. Root/commandproxy notwheelcontact/fullroute orcausalcertificate. No DRstrength, reward/LR/geometry/reset/command/physics changes.

Actualparentpublished147 fourcases ownfinalSHA; collect_second50_candidate_actual.py readonlycompleteerrorfree/twohost8JSON/fullterrainNPZ/queryNPZ and healthyworker actualCIM/argv/creation/children/attention. Missingfutureterrain result islegalpending andworker mustnotrestart. review_second50_candidate_actual.py strict145 same50 worldfloat32 triangles+independentexpected1e-6, complete tenwaves2.406422727m/.4m approach/bothwheels200mmafter/80env15s seed20260928white3, allinitialroot30qparamsrecipesassignments6000callbacks/groundcontactintegralCOMhardware oldthresholds. Legacy115/129 fullsignedcircle alongcrossdedrift/two4pi/straightoriginalfalse andactualreset schema. Original1Ncontact versusposition separate, stand26 no crossing, allvalidprefix/ordinary-before/truncationcoverage/prereset-before/no resetteleport retained; no shortenedapproach/extended15s/relabeling. Finalsensor dynamicbias andstaticrecipe separate/.0075bound/finite, no nonexistentinitialbias exactclaim. Ownactualfinite102 binding required.

Once allfour fullraw actuallyreviewed, run review_second50_direct146_prefix_actual.py fordirect146 exactinitialparamsrecipesassignment/perenv completion improvements/regressions/xyzwheading/allvalidprefix/actual1N fullsupport. Pair with145 original50 reference andfinalowntrainingtrace. Decide onlyobserved50 scope; no graduation fromsave/retention/CPU. Two duration-only blocks(initial300+this1800) alreadycompleted. No blindthird orautomatic70. Ifcompletebehavior meetswhole50 scope, freeze onlythatobservedcandidate; next70 requiresactualCAD/geometry/query newCPU/fullsupport andunique newfrozen audit, never callwholeRM/MoE graduated. Ifsystematicresidual remains, endthissame50 PPO andactively prepare independent trajectory/entry/command-axis diagnosis andcomponentcontract; noindefinitehold/onlyqueue orblindmorePPO. Any genuinelynew learning axis needs isolatedfullsourcefreeze/strictsourceidentity, actualnewcomponent/fullCPUCUDA resume andownmissingphysicalscope only, exactreuseallunchangedcontracts, boundedguardian+uniqueoriginalcanonicalaccounting. E0/CURB20/SLOPE5-8-10/WAVE35 frozen; gateuntrained/hardwareuncalibrated/S8specificlater/93-94paused/WASDuntouched.

005canonical1188000s/sevenextensions no newbudget, actualactive/accounted/tails overrideidle668407.7181019783 snapshot. CPU/SDK/native/frozen/fresh0PPO nocharge; nocopy/clear/tail/extension/recharge. Twoactualfcntl locks/no kill/hotpatch/dual20k/otherAI. FixedclockDRrewardLRhardware/fivefamilies/commands/healthv3/ground1e-6/contactCOM/fullsignedcircle unchanged; otherexpert/gate/min(18h,.13B) planningprotected withoutledgerreserve. Allsavedsource/errors/false/raw/cost/unused/sync/monitor/workorders/Gitreceipts mustGit, existingstage047eb5ef/tag459baf preserved, laterordinarysupplement actualremote main/tracked/oldtag proof; largePTNPZrawJSONUSDZIP actualpathsizeSHAonly/credentialsnotoutputGit. Newrealnextstage uniqueannotatedtrial viarecord_experiment, failedpushcontinueoriginalobjects. SamehourlyACTIVE mod4-10 quiethealthy/noextra5minmonitor/automaticbudget; reviewready notallcoursesfinished.
''')
 names={
 'E1_WAVE50_SECOND_BOUNDED_OWN_FORMAL_CPU_VERIFIED.json':cpu_path,
 'E1_WAVE50_SECOND_BOUNDED_FORMAL_FINAL_ACTUAL_REVIEW.json':final_path,
 'E1_WAVE50_SECOND_BOUNDED_OWN_FORMAL_PPO_CPU_VERIFIED.json':startup_path,
 'E1_WAVE50_SECOND_BOUNDED_COMPLETE_TRAINING_TRACE_ACTUAL.json':trace_path,
 'E1_WAVE50_SECOND_BOUNDED_FORMAL_FINAL_CURRENT_ACTUAL.json':actual_path,
 'E1_WAVE50_CANDIDATE147_CURRENT_ACTUAL_COLLECTION.json':collection_path,
 'E1_WAVE50_CANDIDATE147_CURRENT_ACTUAL_REVIEW.json':review_path,work.name:work}
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   for name,p in names.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
   raw=f.open(io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json','rb').read();oldsha=H(raw);current=json.loads(raw)
  rev=current['terrain_subexpert_revision004'];scope=rev['wave50_second_bounded_scope'];assert scope['root']==ROOT and scope['source_count']==386
  scope.update(phase=final['actual_state']['phase'],own_formal_final_not_yet_claimed=False,own_formal_actual_complete=True,own_checkpoint_SHA=final['own_checkpoint']['sha256'],own_final_CPU_finite_tensors=102,own_snapshot_file_count=81,own_actual_parent=None,own_actual_child=None,own_parent_guardian_child_exit_and_two_fcntl_free=True,own_unique_budget_segment_settled=True,formal_final_review_ref=io.E+'/reports/E1_WAVE50_SECOND_BOUNDED_FORMAL_FINAL_ACTUAL_REVIEW.json',own_formal_CPU_ref=io.E+'/reports/E1_WAVE50_SECOND_BOUNDED_OWN_FORMAL_CPU_VERIFIED.json',complete_training_trace_ref=io.E+'/reports/E1_WAVE50_SECOND_BOUNDED_COMPLETE_TRAINING_TRACE_ACTUAL.json')
  rev['wave50_candidate147_actual_scope']=dict(phase='candidate147_complete_raw_reviewed_scope_decision_pending' if review['review_complete'] else 'candidate147_three_retention_cases_reviewed_terrain_pending',own_SHA=final['own_checkpoint']['sha256'],actual_parent_publication=True,review_complete=review['review_complete'],pending=review['pending'],actual_collection_ref=io.E+'/reports/E1_WAVE50_CANDIDATE147_CURRENT_ACTUAL_COLLECTION.json',actual_review_ref=io.E+'/reports/E1_WAVE50_CANDIDATE147_CURRENT_ACTUAL_REVIEW.json',scope_graduation_not_claimed=True,no_automatic_third_same50_duration_only_block_or70mm=True,next_work_order=io.E+'/reports/'+work.name)
  rev['active_next_expert']='E1_WAVE';rev['active_next_phase']=rev['wave50_candidate147_actual_scope']['phase'];rev['latest_actual_scope']='wave50_candidate147_actual_scope'
  with n.open_sftp() as f:io.put(f,ROOT+'/reports/OWN_FINAL_CANDIDATE147_CAS_NEXT.json',json.dumps(current,ensure_ascii=False,indent=2).encode())
  sync=run(n,r'''from pathlib import Path
import json,time,hashlib,os
D=Path(ROOT_TOKEN);R=Path(E_TOKEN)/'reports';B=Path(B_TOKEN);before=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert h(p)==SHA_TOKEN
raw=(D/'reports/OWN_FINAL_CANDIDATE147_CAS_NEXT.json').read_bytes();tmp=p.with_name('CURRENT_second50_final_'+str(time.time_ns())+'.tmp');tmp.write_bytes(raw);assert h(p)==SHA_TOKEN;os.replace(tmp,p)
assert B.read_bytes()==before and all((R/n).read_bytes()==raw for n,raw in protected.items())
v=dict(epoch=time.time(),passed=True,own_second50_formal_complete_and_actualcandidate147_synced=True,current_SHA=h(p),canonical_SHA=hashlib.sha256(before).hexdigest(),master_approval_tracks_RM004_exact=True,no_GPU_PPO_or_budget_write=True)
for q in (D/'reports/FORMAL_FINAL_CLOSEOUT_METADATA_SYNCED.json',R/'E1_WAVE50_SECOND_BOUNDED_FORMAL_FINAL_CLOSEOUT_METADATA_SYNCED.json'):assert not q.exists();q.write_text(json.dumps(v,indent=2))
print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('E_TOKEN',repr(io.E)).replace('B_TOKEN',repr(io.B)).replace('SHA_TOKEN',repr(oldsha)))
  save('FORMAL_FINAL_CLOSEOUT_METADATA_SYNCED.json',sync)
 finally:io.cleanup(n,w)
 setting=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert setting['status']=='ACTIVE' and setting['rrule']=='FREQ=HOURLY;INTERVAL=1'
 previous=D/'MONITOR_PREVIOUS_SECOND50_ACTIVE_PROMPT.md'
 with previous.open('x',encoding='utf8') as f:f.write(setting['prompt'])
 candidate_status='147已全部actualcomplete/errorfree/fullraw审查，原terrainpending仅历史；完整direct146和scope决定以之后actual优先。' if review['review_complete'] else '实际已审三retentionflat/spin/world，terrain当时result未生成是健康pending；之后actualcomplete优先，不假永久pending。'
 prompt=f'''最新source386自己的50mm第二1800s正式窗口已自然完整保存退出，旧386active/model32275活动保存/未来finalpending均历史。ownmodel32357 SHA{final['own_checkpoint']['sha256']}/17615730B/CPU102/source386/实际81module snapshots+386fullfreeze/PID3010588-start89922117/PASSED/unique{final['actual_load_learn_save_exit_seconds']}s含loadlearnsaveexit原parent一次结清。94updates2256control45.12Menvsteps9024callbacks exact/9actor tensors changed/optimizerdelta1880。ordinary1 control1412 env18887 base_contact原样保留，integrityunknown0/nonfinitefalse/STOPnone/closure1.221559010mm/mimic.001691456rad；time_out15963 route17091 overlap8 unique33046，两coverageexact，不相加当unique。parent3010516/guardian/childactual全部退出/twofcntl-free/active-Sactive空/E1_WAVE50_second_bounded_saved_review_ready合法单scope审查边界非故障/全课程finished，不复活oldmain/resume/once/budgettail。

先读中央E1_WAVE50_SECOND_BOUNDED_OWN_FORMAL_CPU_VERIFIED、FORMAL_FINAL_ACTUAL_REVIEW、OWN_FORMAL_PPO_CPU_VERIFIED、COMPLETE_TRAINING_TRACE_ACTUAL、FORMAL_FINAL_CURRENT_ACTUAL、E1_WAVE50_CANDIDATE147_CURRENT_ACTUAL_COLLECTION/REVIEW、FORMAL_FINAL_CLOSEOUT_METADATA_SYNCED和{work.name}；本机{R}最新数字actual优先。current.rev004.wave50_candidate147_actual_scope才下一审查。自己的全same50 CPUCUDA严格恢复/sourceepisode+1通过，terrainexacttrue/newG3false/commandpredexacttrue/newcommandfalse，非初35→50或PhysXexactresume。source219f/original35b026/ancestor1293c97身份与原SDK/native/smallbig/fresh/clockDR精确SHA复用，无重预检。005总1188000/sevenextensions第七100h早已应用，idle668407.7181019783s只快照，未来actualactive/accounted尾段优先，无新扩展/复制/clearactive/重tail/重结。

147四case已原parent实际发布owna67b模型。当前review_complete={review['review_complete']}，{candidate_status}负/正1.5误差.062802039/.042432778，负4pi0/8正3/8、world64/64/maxcross.043386544；所有originalstrictfalse/spinphysicalsmokefalse/旧退化保持，E0冻结/gate未训，不以旧skill替terrain验收。collector里的真实GPUterrain孩子3184/31016 creation1791746654只是当时定位，healthy3060不重启；使用actualCIM/argv/creation/children/results/attention优先。collect_second50_candidate_actual.py仅读actualcomplete/errorfree两host8JSONbyteSHA/fullterrainNPZ/queryNPZ，review_second50_candidate_actual.py复用145原50mm峰谷十波2.406422727m/.4approach/两轮200mmafter/80env1500controls15s/20260928white3 allroot30qparamsrecipesassignments6000callbacks/actualworldfloat32triangle query原1e-6/groundcontactintegralCOMhardware原容差。original1N支撑与位置分列/stand26无需通行/所有有效ordinary前和未完整prefix/声明truncation两coverageexact/同episodeprereset-before排除resetteleport，不缩接近延15s或重标。115/129fullsignedcircle alongcrossdedrift/two4pi/直线原false、sensorfinal动态bias静态配方/.0075bound分列、不伪未落盘initialbias exact/ownCPU102 binding保持。prepared读者不是futurepass。

完整5NPZ/2256controls22.56s/env/maxphysicalepisode20s actualpath-size-SHA已CPU独立审，dynamiccurrentrootcell family4 negative2418053 positive2503484 standing1440383，staticassignment不冒永久family，beforephysicscommands/afterupdatehist不同phase、prereset-before排除teleport；rootcommandproxy非两轮接触/全路线/因果证书。147完整四case后review_second50_direct146_prefix_actual.py直接配对146实际全初态/参数staticrecipesassignments/逐env改善和退化/xyzwheading/全部有效prefix/原1N完整前后支撑，结合完整owntrainingtrace后独立scope决定。两50 duration-only块已经初300+本1800，不自动第三盲块或70；系统性残差未改善停止此same50PPO，积极独立轨迹/入口/命令单轴合同诊断或下一004005批准轴，不无限hold/只队列。若全50真实通过仅接受冻结observed50，再先核真实70 CAD/geometry/query新组件合同与唯一新frozen全路线审查，不能机械借derived50冒真实RM70/全E1/MoE/永久抗遗忘毕业。

新stage047eb5ef612b7b93be0aabdf64c98ed3d0f17fe5/tag459baf88e1477bb69ad4a2a2d33055c9d41b850d已有actualremote main/tag/peeled，后普通supplement14dd4f230488b1cdeea93428dd0e3547b7bacb1b核验1300oldtags。原Git补档索引sha256缺字段和独立已知schema修复、builder数字field SyntaxError及缺未来reader全部pre-capture/commit拒绝原源码错误保留，非GPU物理故障。后来ownfinal/147/fulltrace/collection/sync/monitor/Gitreceipt必须ordinarysupplement，actualtracked/remote最终工具为准，不能凭prompt假补齐。大weightsNPZrawJSONUSDZIP只actualpathsizeSHA原件保持，credentials临时env不输出不Git，pushfail仅续originalobjects不重record/tag/commit，Git非训练依赖。旧全文保存在{previous} SHA{H(previous.read_bytes())}仅追溯。未来新realaxis部署唯一annotatedtrial；健康无新savedreport不造trial。

下面原合同继续，所有旧活动/未部署/pending只历史，以上ownfullsave与后actual147优先：

'''+setting['prompt']
 save('FINAL_MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=setting['name'],rrule=setting['rrule'],status='ACTIVE',targetThreadId=setting['target_thread_id'],prompt=prompt))
 print(json.dumps(dict(own_final_complete=True,candidate_review_complete=review['review_complete'],monitor_request=str(R/'FINAL_MONITOR_UPDATE_REQUEST.json'))))
if __name__=='__main__':
 try:main()
 except BaseException:save('FINAL_CLOSEOUT_SYNC_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_budget_or_old_once_replay=True));raise
