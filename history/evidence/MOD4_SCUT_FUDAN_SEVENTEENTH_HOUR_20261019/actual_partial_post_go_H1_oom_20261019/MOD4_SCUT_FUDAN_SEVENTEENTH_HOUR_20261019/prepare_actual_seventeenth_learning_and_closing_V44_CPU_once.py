"""Bind future local tools only after actual seventeenth-hour three-expert PPO evidence."""
from pathlib import Path
import ast,datetime,hashlib,json,shutil,time,tomllib,traceback
B=Path(__file__).resolve().parent;W=B.parent;P=W/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019';S=W/'MOD4_SEVENTEENTH_USER_DISK_CLEANUP_20261019';R=B/'reports'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 d=json.loads((R/'THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());a=json.loads((R/'THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json').read_bytes());f=json.loads((P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());ready=json.loads((S/'reports/HOURLY_V5_RESOURCE_AND_UNUSED_ROOTS_ACTUAL.json').read_bytes())
 owner=d['owner']['detached_pid'];assert owner==413504 and a['three_actual_PPO_learning_verified'] and a['actual_finite_transport_returned'] and f['passed_all_three_whole_final_models_CPU'] and ready['ready_for_unused_deployer_resource_checks']
 assert set(f['one_original_writer_actual_segment']['experts'])=={'h1','e2','recovery'} and f['one_original_writer_actual_segment']['owner_parent_pid']==376288
 assert d['specs']['h1']['human_explicit_GPU_sharing'] is True
 for key,x in a['experts'].items():
  assert x['actual_GO'] and x['actual_production_log_positive'] and x['actual_matching_GPU_worker_compute'] and x['GO']['source_SHA']==f['experts'][key]['final']['SHA'] and x['GO']['original_owner_pid']==owner
  installed=json.loads((R/(key.upper()+'_NEW_SOURCE_TARGET_FULL_INSTALLED_RSL_SDK_CPU_ACTUAL.json')).read_bytes());qualified=json.loads((R/(key.upper()+'_NEW_SOURCE_ACTUAL_CLOSED_PRODUCTION_CONTINUATION_CPU.json')).read_bytes());assert installed['passed_CPU_only'] and installed['source_SHA']==x['GO']['source_SHA'] and qualified['actual_same_backend_closed_source_CPU_passed'] and qualified['qualification']['value']['passed']
 assert (B/'payload/h1/three_real_gpu_resource_v1.py').read_bytes()==(B/'three_real_gpu_resource_shared_user_v2.py').read_bytes()==(P/'payload/h1/three_real_gpu_resource_v1.py').read_bytes()
 helpers=[]
 for name in ('collect_next_hour_missing_closed_finals_bounded_owner_wait_V2_once.py','review_next_closed_hour_finals_whole_model_original_cost_CPU_once.py'):
  before=(P/name).read_text('utf8');assert '376288' in before;after=before.replace('376288',str(owner));ast.parse(after);assert after.replace(str(owner),'376288')==before
  with (B/name).open('x',encoding='utf8',newline='\n') as stream:stream.write(after)
  helpers.append(dict(path=str(B/name),SHA=H(B/name),only_owner_binding_changed=True))
 F=B/'future_same_recipe_hour_templates';F.mkdir();future=[]
 for q in sorted((P/'future_same_recipe_hour_templates').glob('*.py')):
  if q.name=='three_real_gpu_resource_shared_user_v2.py':shutil.copy2(q,F/q.name)
  else:
   text=q.read_text('utf8')
   if q.name=='prepare_next_three_closed_sources_one_hour_CPU_once.py':
    text=text.replace("T=W/'"+P.name+"'","T=W/'"+B.name+"'").replace('T3sf17_1910v22','T3sf18_1910v23').replace('THREE_GPU_SCUT_FUDAN_HOUR22_','THREE_GPU_SCUT_FUDAN_HOUR23_')
    assert "previous_runtime_root=old['roots'][key]" in text and "resource=prior/'three_real_gpu_resource_v1.py'" in text
   elif q.name=='deploy_three_next_closed_source_hours_once.py':
    text=text.replace('T3sf17_1910v22','NEXT_ROOT_ONLY').replace('T3sf16_1910v21','T3sf17_1910v22').replace('NEXT_ROOT_ONLY','T3sf18_1910v23').replace('376288',str(owner))
    assert "set(rows[0]['experts'])=={'h1','e2','recovery'}" in text and 'T3sf17_1910v22/owner' in text
   ast.parse(text)
   with (F/q.name).open('x',encoding='utf8',newline='\n') as stream:stream.write(text)
  future.append(dict(path=str(F/q.name),bytes=(F/q.name).stat().st_size,SHA=H(F/q.name)))
 assert len(future)==5 and (F/'three_real_gpu_resource_shared_user_v2.py').read_bytes()==(B/'payload/h1/three_real_gpu_resource_v1.py').read_bytes()
 pre=(F/'prepare_next_three_closed_sources_one_hour_CPU_once.py').read_text('utf8');assert pre.index("for c in C.glob('*.py')")<pre.index("resource=prior/'three_real_gpu_resource_v1.py'")<pre.index("m=dict(oldm,source_SHA=")
 rewards=[]
 for name in ('h1_scut_fudan_jump_reward_v1.py','h1_takeoff_progress_environment_v2.py','train_H1_ground_prelaunch_fullstate_v2.py'):
  rel=Path('payload/h1/job0/runtime/isaac/mod4')/name;assert (B/rel).read_bytes()==(P/rel).read_bytes();rewards.append(dict(path=str(B/rel),bytes=(B/rel).stat().st_size,SHA=H(B/rel)))
 details={k:dict(source=d['specs'][k]['source_SHA'],Adam=d['specs'][k]['source_Adamstep'],worker=x['worker'],GO=x['GO'],save_Beijing=datetime.datetime.fromtimestamp(x['GO']['save_deadline'],datetime.timezone(datetime.timedelta(hours=8))).isoformat()) for k,x in a['experts'].items()}
 closed={k:dict(final=x['final'],updates=x['updates'],Adam=x['all17Adam_after'],tensor_counts=x['whole_tensor_counts']) for k,x in f['experts'].items()}
 errors=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for base in (R,S/'reports') for p in sorted(base.glob('*ORIGINAL_ERROR*.json'))]
 proof=dict(epoch=time.time(),three_actual_GO_positive_PPO_matching_UUID_compute=True,actual_owner=owner,current_sources_all_three_latest_complete_hour16=True,actual_dispatch=d,actual_learning=a,details=details,previous_closed_sources=closed,previous_original_cost_once=f['one_original_writer_actual_segment']['charged_expert_seconds'],remaining_snapshot=f['remaining_snapshot'],human_H1_sharing_and_original_memory_lock_save_guards_retained=True,V5_actual_resource_ready_snapshot=ready,closing_helpers=helpers,future_full_three_templates=future,future_only_reserved='T3sf18_1910v23',unchanged_reward_files=rewards,H1_shared_helper_exact_CRLF_bytes_after_controller_copy_preserved=True,no_current_intermediate_whole_model_or_skill_CPU_claim=True,no_new_behavior_case_or_GPU_replay_or_budget_mutation=True,old_cleanup_and_preinstall_reader_errors_retained=errors)
 proofname='SEVENTEENTH_ACTUAL_THREE_LEARNING_AND_FULL_FUTURE_BINDING_CPU_ACTUAL.json';put(R/proofname,proof)
 work='NEXT_ACTUAL_SEVENTEENTH_THREE_LEARNING_AFTER_MEMORY_READY_V44_WORK_ORDER.json';put(B/work,dict(epoch=time.time(),version=44,current_proof=str(R/proofname),previous_complete_CPU=str(P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json'),current_dispatch=d,current_actual_learning=a,details=details,closing_bound_owner=owner,future_only_reserved='T3sf18_1910v23',old_failures_preserved=True,current_H1_source16_local_jump_recovery0_normal_mixed_results_remain_source16_only=True,local_player_unchanged_hour7=True))
 old=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert old['status']=='ACTIVE';p=old['prompt'];historical=p[p.index('最新用户“ H1 E3为什么这么慢 ”'):p.index('人类三卡最大有意义利用')];contract=p[p.index('人类三卡最大有意义利用'):p.index('same mod4-10 ACTIVE/hourly/原target')]
 head=f'''最新actual V44覆盖V43B资源pending：第十七SCUT+Fudan小时已由原第十六三完整源实际接训，三actualGO/positivePPO/matchingUUIDworker compute均核真。Q={B.as_posix()}；P={P.as_posix()}；S={S.as_posix()}。先读Q/{work}、Q/reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json、THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json、{proofname}与P/reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json。later完整SHA/exe-argv-create/GO-save-EXIT/canonical/fcntl/free实际优先；PID/排程/快照不当永久alive/free或futureFINAL。
 本轮唯一V5资源reader已实际返回并consume：epoch1792416497.250677、H1free9683MiB>7000、E3free24203empty、disk284497711104bytes、RAM531185303552bytes、原private/sharedfcntl均free、新72两根当时unused。此为瞬时资源事实，H1其他compute仍可能共存，不查询peer身份、不kill/删锁/改peer或把全卡利用率归自家；原shared授权仍仅H1key+human_explicit_GPU_sharing=True，E2/E3仍GPUempty，原显存>7000/RAM>8GiB/disk>25GiB/锁/savedstop不降。资源V4/V5和所有旧reader/旧首次deployerconsume，不再读旧pending流程；正在学习时不启动资源reader/第二watcher。
 原unused V2deployer已实际完成target72和source210安装整source/SDKmath/RSL/runtimeassets CPU核与原376288实际out/canonicalNone/两原fcntl/费用once交接，随后neworiginalwriter{owner} root={d['source_root']}、E2node{d['nodes']['e2']['detached_pid']}、72H1node{d['nodes']['h1']['detached_pid']}/E3node{d['nodes']['recovery']['detached_pid']}。真实worker/GO/save/nominalend见details及lateractual。V2deployer与首次metadata均consume，不重run、不热改健康三卡。原每卡GO到save3600/lifecycle3900含300exit/no24cutoff/20k×24，远端自主完整saveSDKclosechildwait/ownerterminal，不依Laptop/hourly，不hotextend/停健康卡/中途重型PT或行为审计；三actual学习不是wholeCPU新模型/技能PASS/持续100%。
 最新完整来源仍第十六H1cb118b2ac27cca44466fba9014f4583ee8db23fc2cb2d83c4034b15961178765/42updates/Adam674740；E2c51a920423c3d6bfc057f820f1aa2ab96384a50bd19168cffff29f5dc8ea5622/242/767500；E3d17aa67333b59446a50ff244b1111a51c0f932f880c08048fbbdedf21e1a8aed/98/697700。三PT完整twohostSHA、199105/17598/17396全modelruntimefinite、17Adam每update20/actor9含STDcritic8全变化原CPU真过；第十六费用10879.442652702332s sumonce已结清、remaining267523.45775580406只是旧snapshot，不二扣/refund/clearactive/复制ledger。十一partial H1仍0GO0PPO0charge，不凭同名update42误移来源。
 closed_same_backend_production/reward_migration=False，原33负例与各target整source/SDKmath/RSL/runtimeassets真核；三SCUTFudan rewardbytes exactP，worker仅sourcefilenameAdam，actorcritic六STD/17Adam/RNG/phase/20kDR整态继承且STD可学不reset/freeze。不重复迁移/telemetry/回退源/恢复旧reward/反向E3native336，nativeCPU=None/source_native_CPU_SHA=null/nativeGPUwaitfalse，无重复standalone native或nativePASS；真实backend/physics/runtime变化另走原流程。H1shared helper在controller copy之后、manifest之前copy2保真实CRLF并部署前exactbytes；future第五helper须同复制，按各actualhealthy runtime/sourcefilename/Adam作AST绑定，不反向Kpartial/J硬编码。
 下一本小时末仅Q自己的collect_next_hour_missing_closed_finals_bounded_owner_wait_V2_once.py和review_next_closed_hour_finals_whole_model_original_cost_CPU_once.py，已绑定{owner}；不重P376288/S旧资源reader/collector/preparer/deployer/Task/native/once。同source连接max900只等actualCOHORT终态，actualclosed才取缺三完整FINAL/PT与原费用/out/canonicalNone/两原fcntl/private/sharedfree，wholeCPU后及时接续。H1peer不等于本owneralive，不要求peer退出，如实存compute/freeMemory。提前距save加正常退出明显>900先localreports/CIM及短有界本机等，临近单collector；不第二watcher/并发SSH/按排程猜FINAL/机械等下一heartbeat。missing/error原样留，finite actual返回/freshCIM后新有界只补缺，不重已完整PT/raw/once。
 未来只用Q/future_same_recipe_hour_templates全部五文件，Q实际三路closed/fullCPU后复制新unused MOD4_SCUT_FUDAN_EIGHTEENTH_HOUR_20261019再prepare，T3sf18_1910v23仅reserved；实际跨午夜则新阶段按实际日期，不回填。模板正常三完整final/各actualhealthy previous runtime/三charged experts，共享第五helpercopy2及覆盖顺序保持。metadata单连接max600/keepalive15/append-only journal仅真实GO/PPO/GPU，不为public4active0额外等，保留rewardreadout，first正常批非aux效果或技能成绩；实际finite返回才交还transport。
 清理782份旧轨迹259494886175bytes仅属原用户精确授权已完成事实，未发现的回放/残缺checkpoint不冒已删；完整模型/最新16/runtime/文字索引/锁/其他job保留，不重删/递归清空或续旧installer备份。S完整删除manifest/producerSHA/stat/闭合证明及安装包partial272629760bytes未完成备份、原KeyboardInterrupt/SFTP/权限错误均保留；不重hash241GiB/不改旧false。旧首次deployer preinstall拒绝和容量V3本机guard拒绝仍属原失败，本轮资源ready不冒当时GPU/网络问题已修复。
 本轮没有重跑任何本机cb11行为，Q既有第十六四轨迹原jump strict1/1/0、15s活、末yaw+.469549恢复事件消失与normal末速.0100764/位移.157370/yaw-.0650358改善仍仅归完整cb11源；不同backend无20kDR两yaw小样本混合变化，不移给未闭合17、不冒PhysX/统计/唯一因果/整体修好或毕业。下一自然新完整H1源才新namespace看恢复后yaw/普通停车/动作与真实reward生效，不重旧case/盲改rewardLRSTDphysics阈值/actorinput/时钟/外力纠偏/heldout61011/12或用户玩家。
 '''
 tail='''same mod4-10 ACTIVE/hourly/原target01a07a2d-9036-7531-a012-692df9f56353，无第二monitor或自动预算；健康unchanged/pending静默，仅新完整FINAL/新冻结/实质修复/重大退化/必需人类动作通知。本次第十七三实际接训通知后不重复firstmetadata；预算未结束不删monitor。
 新stage scut-fudan-seventeenth-hour-actual-learning-after-resource-ready只record一次，later实际Git回执优先；已record则helper/record/tagconsume，pushfail只续已有objects。S清理stageunique d9a54a06d65b090aa7ee6b02d355106ac56f0853/tag b09a8e4fe2ee32b6c803157a64e52d6964c665fd/总1406与ordinary c3d09b61821a2a3c7e742d0e3b2eea8a8a38feda及全部旧stage/helper/Task/native/once consume。全部Q/S新source/原错误/文本报告/unused closing与future模板/工作单monitor/appreceipt/原费用进Git，>50MB全文orderedUTF8parts+descriptor+全重组SHA；PT/NPZ/USD/ZIP只producer实际pathsizeSHA，已授权删除旧raw明示deleted，不为Git重GPU/改账/下载旧件/重hash大件或无限补HEAD，trial按实际记录日期。
 '''
 args=dict(mode='update',id='mod4-10',kind='heartbeat',name=old['name'],prompt=(head+historical+contract+tail+'\n第十六完整源及第十七实际创建/GO排程：\n'+json.dumps(dict(closed=closed,owner=d['owner'],nodes=d['nodes'],source_root=d['source_root'],roots=d['roots'],details=details),ensure_ascii=False,indent=2)).rstrip(),rrule=old['rrule'],status=old['status'],targetThreadId=old['target_thread_id'])
 put(B/'AUTOMATION_ACTUAL_SEVENTEENTH_RESOURCE_READY_V44_ARGS.json',args)
 with (B/'ACTUAL_SEVENTEENTH_RESOURCE_READY_STAGE_SUMMARY.md').open('x',encoding='utf8') as stream:stream.write('# Seventeenth-hour actual learning after resource readiness\n\n'+head+'\n'+json.dumps(proof,ensure_ascii=False,indent=2))
 print(json.dumps(dict(actual_three_learning=True,owner=owner,save={k:x['save_Beijing'] for k,x in details.items()},closing_and_full_three_future_prepared=True,no_old_behavior_replay=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/'SEVENTEENTH_ACTUAL_HANDOFF_PREPARATION_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),local_only_no_GPU_or_account_mutation=True));raise
