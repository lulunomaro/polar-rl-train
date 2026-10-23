from pathlib import Path
from datetime import datetime,timezone,timedelta
import ast,hashlib,json,shutil,subprocess,time,tomllib,traceback

D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports'
P=T/'H1_STEP270_REWARD_REPLAY_V2_RESOURCE_V35_20261023';N=T/'H1_STEP270_REWARD_REPLAY_V2_RESOURCE_V36_20261023';F=T/'H1_STEP270_REWARD_REPLAY_V2_RESOURCE_V37_20261023'
C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88';G=W/'polar-rl-train'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def git(*args):
    return subprocess.run(['git','-C',str(G),*args],capture_output=True,check=True).stdout.decode('utf8').strip()

try:
    proof=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
    closed=read(R/'REPLAY_V2_CURRENT35_CLOSED_HEALTH_RETENTION_EPISODE_CPU_ACTUAL.json')
    transfer=read(P/'reports/PEER_FORENSICS_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json')
    meta=read(N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json')
    cpu=read(N/'reports/H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json');ecpu=read(N/'reports/RECOVERY_TWO50_FULL_TARGET_SOURCE_RSL_SDK_CPU_ACTUAL.json')
    resource=read(N/'reports/NEXT_E3_BOUNDARY_RESOURCE_COMPONENTS_ACTUAL.json');q=read(N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
    tuck=read(R/'HUMAN_LEG_TUCK_EXISTING_DERIVED_REPLAY_CPU_ACTUAL.json')
    assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
    assert closed['passed_checkpoint_health_and_recording_scope'] and transfer['passed'] and transfer['source_above_original_disk25'] and transfer['all_own_storage_processes_actual_out']
    assert meta['passed'] and meta['actual_finite_returned'] and cpu['passed_CPU_only'] and ecpu['passed_CPU_only']
    assert cpu['reward_module_SHA']=='518d5f98bd8ad4517ea4616d5bf49353c0c7231817b8740f7637c048d342f217' and cpu['reward_runtime_SHA']=='0ec7db1fc55ca0d552341e24237048a916d1cbb6b125905eb22b0001b60a8e34'
    gos=meta['source210']['current']['go'];ppos={k:meta['source210']['current']['rows'][k]['latest_save'] for k in ('h1','recovery')}
    for k in ('h1','recovery'):assert gos[k]['source_SHA']==proof['models'][k]['final']['SHA'] and ppos[k]['updates']>0
    assert ppos['h1']['actual17Adam_steps']==[proof['models']['h1']['Adam']+20*ppos['h1']['updates']]
    assert ppos['recovery']['Adam_step']==proof['models']['recovery']['Adam']+20*ppos['recovery']['updates']
    assert not F.exists();F.mkdir();(F/'reports').mkdir()
    for folder in ('paired_controllers','h1_only_controllers','repair_sources'):shutil.copytree(N/folder,F/folder)
    for p in N.glob('*.py'):
        if 'UNUSED_OLD' in p.name or 'UNEXECUTED' in p.name:continue
        s=p.read_text('utf8').replace(P.name,N.name).replace('H1step270_reward_replay2_2310v36','H1step270_reward_replay2_2310v37');ast.parse(s)
        with (F/p.name).open('x',encoding='utf8') as f:f.write(s)
    for p in F.rglob('*.py'):ast.parse(p.read_text('utf8'))
    for p in (N/'repair_sources').rglob('*'):
        if p.is_file():assert H(p)==H(F/'repair_sources'/p.relative_to(N/'repair_sources'))
    prep=(F/'prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py').read_text('utf8')
    assert N.name in prep and ';E=P' in prep and "repair=N/'repair_sources'" in prep
    assert "reward_stage/'target_H1_step270_closed_source_sdk_cpu_review_v1.py'" in prep
    assert 'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json' in prep and 'PAIR_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json' in prep
    put(R/'NEXT37_SAME_REPLAY_V2_PAIRED_PREDECESSOR_SOURCE_AST_ACTUAL.json',dict(epoch=time.time(),passed_AST=True,current36_both_actual_GO_PPO=True,future_stage=str(F),no_future_payload_Task_GO_or_fee=True,repair_source_bytes_exact=True,preparer_dynamic_both_latest_closed36_sources=True,correct_target_checker_basename=True,no_unvalidated_leg_tuck_reward_installed=True))
    s=(D/'review_closed35_replay_v2_health_retention_text_CPU_once.py').read_text('utf8').replace(P.name,N.name).replace('REPLAY_V2_CURRENT35_CLOSED_HEALTH_RETENTION_EPISODE_CPU_ACTUAL.json','REPLAY_V2_CURRENT36_CLOSED_HEALTH_RETENTION_EPISODE_CPU_ACTUAL.json').replace('REPLAY_V2_CLOSED35_TEXT_CPU_ORIGINAL_ERROR_','REPLAY_V2_CLOSED36_TEXT_CPU_ORIGINAL_ERROR_');ast.parse(s)
    with (D/'review_closed36_replay_v2_health_retention_text_CPU_once.py').open('x',encoding='utf8') as f:f.write(s)
    put(R/'HUMAN_LEG_TUCK_READER_V1_BROADCAST_ERROR_AND_V2_CORRECTION_SCOPE_ACTUAL.json',dict(epoch=time.time(),V1_source='review_human_leg_tuck_on_existing_derived_replay_CPU_once.py',V1_error='NumPy mixed advanced indexing moved wheel axis to the front; shapes (2,48,57,3) versus (48,57,1,3)',V1_error_preserved=True,V1_not_reexecuted=True,V2_source='review_human_leg_tuck_on_existing_derived_replay_CPU_V2_once.py',V2_changed_only_np_take_axis2_and_error_filename=True,derived_small_artifact_read_only=True,no_original_two_raw_reread_or_new_PhysX=True,not_training_failure=True))
    work=T/'reports/NEXT_ACTUAL_REPLAY_V2_PAIR35_COMPLETE118_77_HUMAN_TUCK_PAIR36_PPO_WORK_ORDER.json'
    put(work,dict(epoch=time.time(),latest_actual=True,complete35_models_cost_CPU=proof,closed35_health_retention_episode=closed,closed35_three_NPZ_verified_on72=transfer,old11_remaining_unselected_entries=5,no_new_old11_batch_this_window=True,current_stage=N.name,current_mode_paired=True,actual_run_id=meta['run_id'],owner=meta['source210']['owner'],H1_worker=meta['source210']['H1_worker'],E3_worker=meta['source72']['worker'],actual_GO=gos,first_PPO=ppos,H1_installed_CPU=cpu,E3_installed_CPU=ecpu,resource_snapshot_before_GO=resource,human_leg_tuck_new_observation=tuck,human_leg_tuck_hypothesis_requires_phase_and_actual_new_recording_evidence=True,not_unique_cause_or_unvalidated_reward_V3=True,next37_AST_only=str(F),no_formal270mm_success_or_graduation=True))
    gate=datetime.fromtimestamp(max(x['nominal_end_epoch'] for x in gos.values())-900,timezone(timedelta(hours=8))).isoformat()
    old=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))['prompt']
    tail=old[old.index('runtime0ec7db1fc55ca0d552'):old.index('本新reward V2阶段必须且仅一次record_experiment')]
    hm=proof['models']['h1'];em=proof['models']['recovery'];health=closed['health'];ret=closed['retention']
    prompt=f'''REPLAY_V2_CLOSED35_PAIR36_AND_HUMAN_TUCK latestactual覆盖REPLAY_V2_INSTALLED_PAIR35 active/36reserved。人类回放修复与存储授权已执行，不重复问。人类本轮追加“还有看你的图里，跳上台阶后腿以旧保持站立状态，我觉得跳上台阶时因该收腿，有感觉吗？”，已用现有小派生记录作新收腿量化诊断，未重原两raw/模型/GPU，当前仍同518奖励，不冒已经再改V3。
T={T.as_posix()}；D=T/{D.name}；B=T/H1_STEP270_REWARD_PATH_V1_20261022；当前N={N.name} paired=True。先读T/reports/{work.name}、N/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json、D/reports/REPLAY_V2_CURRENT35_CLOSED_HEALTH_RETENTION_EPISODE_CPU_ACTUAL.json、HUMAN_LEG_TUCK_EXISTING_DERIVED_REPLAY_CPU_ACTUAL.json、NEXT37_SAME_REPLAY_V2_PAIRED_PREDECESSOR_SOURCE_AST_ACTUAL.json及P/reports/PEER_FORENSICS_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json（P={P.name}）。actual完整SHA/exe argv/create/GO FINAL CPU EXIT/canonical锁优先，PID/首PPO/排程/资源仅snapshot，不冒永久alive/free/futureFINAL。
上一35首个518奖励完整窗两FINAL/wholeCPU/原费/allout真过：H1完整{hm['updates']}PPO/全17Adam{hm['Adam']}/{hm['final']['bytes']}bytes/SHA{hm['final']['SHA']}；E3完整{em['updates']}/Adam{em['Adam']}/{em['final']['bytes']}bytes/SHA{em['final']['SHA']}。两hostSHA/H1202/106 E3173/96finite/全17Adam每update20/actor9含六STDcritic8全变化/同270phase和E350Hz整态CPU过；原owner两node孩子out/canonicalNone/两fcntl/H1lease与72private共享free。H1原费{hm['actual_cost']['charged_seconds']}s/E3{em['actual_cost']['charged_seconds']}s各GO至terminal独立sumonce，总{proof['actual_cost_sumonce']}s，remaining{proof['remaining_actual_snapshot']}只闭合后当前GO前snapshot。collector/wholeCPU/textreader consume，不重PT/rawhash/旧native/query/首metadata，不退款二扣。
35实际{health['control_steps']}controls/{health['actual_physics_callbacks']}callbacks=expected，unknown0/integrity0/nonfiniteFalse/coverageexact/stopNone，ordinary{health['ordinary_episode_reset_events']}，reason={json.dumps(health['termination_events_by_reason'])}；timeouts单列，legacy_single_peak2mm=False保持、无disk_savedstop。1次arena普通单环境reset后继续完整118FINAL，无新missingquery，是本窗边界运行证据，不冒旧env11843同轨迹复现/所有未来保证。FINAL当前20k episode snapshot={json.dumps(closed['H1_current_episode_snapshot'])}。selectedreset清旧事件，非整窗累计/历史/冻结评测，不与旧峰值比较收益退步，不称270mm成功。摘要是同一次CPU已加载FINAL，无额外PT/actor/optimizer/RNG/GPU。
35retention={json.dumps(ret)}。115不可变intent/receipt/history exact、230中途raw/preupdate持续批准prune，原all_success_and_failed_control_prefixes_retained=False/failureflagFalse/无IOerror保留；只是保存文字审查，不重首窗目录audit/12CPU/raw/PT/GPU。已prune不可恢复。
35本次仅3仍存在NPZ0/116/117，合1046125436bytes fullproducer/source/targetSHA+signedack后释放210核真重复，原件现72 /home/lc01/Zonglin Li/zonglin2/forensic_originals/PEER_TLS_H1_STEP270_REWARD_REPLAY_V2_RESOURCE_V35_20261023/retained_control_npz；配套preupdate/PT/FINAL/source/errors/logs仍210。INDEX只是转存前snapshot，不称3旧210路径仍在。所有senderreceiver out/全文回执，sourceafter{transfer['source_free_after']}bytes>25GiB仅当前GO前snapshot，不永久free。helperconsume不重本批/hash。本窗未搬old11，累计61+12+6+6+5+6+6已72，尚5未选未fresh逐个stat/hash；32/30/28/26各3仍210、31/29/27已72，依各SHA实际位置不盲历史INDEX。
新human收腿诊断只读已提取closed31小派生NPZ/既有USD重建，不重原prefix117/118 raw。案例10042车身参考点到轮轴3D距离开头301/303mm→轮底顶点447/445mm，案例2887几乎全程445..448mm；支持这些旧片段离地仍伸腿，不是仅渲染观感。不是完整起跳落地/新35策略/唯一失败原因；原jointorder推导不是fresh PhysX readback，保存运动学不是callback重放。现有leg_tuck目标.22m/权重.5、原active请求AND实际air_ticks>0范围，可能缺少请求结束后的空中衔接，需结合真实phase/接触/新记录验证，不凭外观强制全程收腿/加动作脚本。新V1 NumPy高级索引broadcast读者错和V2 np.take(axis2)修正并列保留，不改训练失败/重V1/重原raw。两个小派生reader已consume，不重复读同case来冒新回放。用户的收腿观察继续作为下一步回放重点；当前36健康窗不hotpatch/停训，未做新V3奖励声明。
当前runid={meta['run_id']}；owner={json.dumps(meta['source210']['owner'])}；H1worker={json.dumps(meta['source210']['H1_worker'])}；E3worker={json.dumps(meta['source72']['worker'])}；actualGO/save/end={json.dumps(gos)}；两首PPO={json.dumps(ppos)}。来源为35两最新完整118/724800/175519...与77/802420/c9b29...，以完整SHA字段为准；H1同270phase/0ec7/518、E3同50Hz整态继续，不退32/d0f/旧源/failedprefix。首PPO仅producer snapshot非currentwholeCPU/全tensor变化/技能/持续alive利用率/未来FINAL。sourceH1savedoptimizerLR={cpu['actual_optimizer_saved_LR']}与配置初值1e-4 adaptive分列；六STD/17Adam不reset/freeze。preparer两条非致命\\S SyntaxWarning actual0原文保留，deployer/installed整sourceSDKmathRSL/phase17Adam/boundary/reward实际SDKcompute含pushwrapper/valid_ready/E3CPU/首metadata consume，不重root/Task/owner/helper/首metadata/中途PT，无跨窗serial父。未选H1only本窗不运行。
所有210transport统一Python314 -B -X utf8 B/same_authorized_session_compressed_transport_v2.py <对应unused helper绝对路径>，同授权会话basename.zst流式memory筛选，strictpin/秘密memory stdin不变，不解压盘/其他会话取凭据。每次fresh本机CIM exactbasename/相对绝对argv/exe/create，只有一个自己finite独占210/72/249；其actualalive期间root只localreports+CIM，returned归还，无第二SSH/watcher/5minpoll。
每slot原GO到save3600/lifecycle3900含300exit原端自主全saveSDKclosechildwait，唯一原writer收到各terminal独立sumonce，still7800reserve/82512.86069250107门槛不降3900/退款/二writer/clearcanonical。N唯一unused collect_selected_pair_finals_unused_once.py只maxactualnominalend-now<=900临近，正确gateBJT={gate} epoch自动换算，原本机assert保持；wrapper单finite210max900核owner/H1node孩子out/COHORT_FINAL/OWNER_EXIT/canonicalNone/两fcntl/H1lease，再72max210核E3孩子out/private共享free，仅缺两新完整FINAL/PT/全文text/原费。returned后review_selected_pair_models_unused_once.py用env_isaaclab CPUtorch完整finite/17Adam20每update/actor9含STDcritic8变化/270phase50Hz/原费用allout，同次H1FINAL非gating episode摘要；再D/review_closed36_replay_v2_health_retention_text_CPU_once.py只文字CPU，不额外PT。明显>900只localreports/CIM/<=60s短等，不机械下一heartbeat。失败原prefix/error/fee保留，健康另一槽继续，不以rc0冒FINAL/设0退款；actualreturn/freshCIM后仅newunused missing-only不重旧件/once。两槽未都完整不运行要求bothFINAL的37正常入口，先诊断actualfailure，分别latestqualified源新unused接续。
N unused relocate_selected_pair_closed_forensics_unused_once.py仅两完整闭合CPU/health/原费/allout后wrapper freshsource/canonicalNone/锁/disk，>25GiB不创建转存，不足先fresh72保留25，本窗仍在NPZ最小足够subset source+selected>25且target-selected>25才新target/controller，max20GiB上限不是必搬。全producer/source/targetSHA/mtime/inode/signedack后只释放210核真重复/全senderreceiver out/全text。当前3不足就真实blocked留源，检查source_above_original_disk25不以rc0冒free或newdeployer，可newunused missing-only旧11剩5或其他已闭合仍原位NPZ需要部分，先freshcapacity，不重旧batch/降25或8/删唯一原件/停健康窗。TLS31e6和passedCPU复用，单顺序SSH+peerTLS/pin/tokenkey只memory stdin memfd，不经C慢链/改防火墙权限挂载；512MiB只是copy选量余量非新训练gate，无需重问许可。
下一唯一F={F.name}仅sourceAST/controllers/repair_sources/config reserved，无未来模型payload/Task/GO/fee。36两完整FINAL/wholeCPU/health/原费/allout/freshsource>25后，probe读36 PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL再fresh72 empty/free7000/RAM8/disk25无peer身份；returned再preparer动态两source都取36最新完整fullSHA/Adam/整态独立结清（E=P），不退35/32/18。四resource全真paired否则H1only，一个分支/唯一writer；deployer/firstPPO均wrapper，再fresh旧allout/canonicalNone/两fcntl/H1lease/unusedroot/H1empty15669/E3empty7000/RAM8/disk25/installed全sourceSDK RSL/phase17Adam/boundary/reward实际SDKcompute/valid_ready。H1only另原owneraccountauthAST，scheduler仅该分支引用27历史四编辑证明并动态新sourceAdam/ownerSHA，不要paired36不存在H1only回执。owner/closing按36 PAIR_ORIGINAL_ACCOUNT_DETACHED/PAIR_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED。repair_sources518/checkerf806/runtime0ec7/loader/derivedauth/真实target检查器basename/reference整字节续，518→same518，不退d0f/510/352/oldinitial/failedprefix。只有actualGO/PPO后才后继reserved；未来37若H1only，E3仍最新qualified36，按actualmode后继。资源拒绝留error只newunused namespace，不重旧pair19/旧33/failed34/consume。
{tail}
Git新reward V2阶段唯一record已实际完成：trial-20261023-h1-step270-replay31-forward-clearance-reward-v2，record/peel e8b7448a5d977bd46a0542536f8bb8e72ab4ab68，tagobject16412885b392693c8a9ac4b691627791d42497b0；随后ordinary main48aca991fa3f3b967024e49682c9f4654491545b真实核。入口record_replay31_forward_clearance_reward_v2_and_pair35_v2_once.py已consume，旧未用record草稿也不运行。1424tags原objects/peels不变，旧reward0fdb/cleanup唯一trial都consume。本轮35完整118/77/724800802420/原费退出/health与1arena/115retention回执/3NPZ72真实位置/36新两PPO/37dynamicpaired/新human收腿派生量化和V1读者错+V2修正/全部warnings/source/工作单/monitor回执同阶段ordinary全部追加，不只成功摘要；pushfail只续已有objects。binary仅producer真实pathsize已知SHA，不为Git重PT/rawhash/GPU/训练host/账，大文字orderedUTF8parts/重组SHA，postGit工具回执留对话不无限追HEAD。
same mod4-10 ACTIVE/hourly/原target01a07a2d-9036-7531-a012-692df9f56353，无第二monitor/预算未尽不删。仅新完整FINAL/新评测/实质修复/资源预算边界/必要人类动作通知，健康未变pending静默。本轮两完整/收腿定量/新36首PPO及转存已通知，不重复首metadata/旧raw/cleanup/已答批准。MoE/player原100Hz包不自动导出热改，T2-z仅询问无下载/worldmodel/新inputs/PPO授权。'''
    put(R/'CLOSED35_ACTUAL36_HUMAN_TUCK_MONITOR_UPDATE_ARGS_ACTUAL.json',dict(mode='update',id='mod4-10',kind='heartbeat',name='MOD4计划与双机并行巡检',status='ACTIVE',rrule='FREQ=HOURLY;INTERVAL=1',targetThreadId='01a07a2d-9036-7531-a012-692df9f56353',prompt=prompt))
    src=C/'append_pair119_76_three_peer_transport_pair32_V120_ordinary_once.py';s=src.read_text('utf8')
    s=s.replace('H1_STEP270_REWARD_BOUNDARY_RESOURCE_V31_20261023',P.name).replace('H1_STEP270_REWARD_BOUNDARY_RESOURCE_V32_20261023',N.name)
    s=s.replace('complete31_H1119_E376_Adam720060_799380_threepeer_transport_pair32_both_PPO','complete35_replayV2_H1118_E377_human_leg_tuck_pair36_bothPPO')
    s=s.replace('NEXT_ACTUAL_PAIR31_COMPLETE119_76_THREE_PEER_TRANSPORT_REPAIRED_PAIR32_PPO_V120_WORK_ORDER.json',work.name)
    anchor=" known={}\n";assert s.count(anchor)==1
    extra=""" known={}
 for ip in ROOT.rglob('EXTERNAL_MODEL_ASSET_INDEX.json'):
  for row in json.loads(ip.read_bytes()).get('artifacts',[]):
   if row.get('path') and row.get('SHA'):known[str(Path(row['path']).resolve())]=row['SHA']
 for stage in (T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V32_20261023',P):
  for x in json.loads((stage/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']
"""
    s=s.replace(anchor,extra);ast.parse(s)
    helper=C/'append_replay_v2_closed35_human_tuck_pair36_ordinary_once.py'
    with helper.open('x',encoding='utf8') as f:f.write(s)
    assert not git('status','--porcelain')
    put(C/'reports/REPLAY_V2_CLOSED35_HUMAN_TUCK_PAIR36_ORDINARY_CONFIG.json',dict(destination='replayV2_closed35_human_tuck_pair36_20261023',base_HEAD=git('rev-parse','HEAD'),title='Record replay V2 complete window, measured leg extension, and pair36 continuation'))
    print(json.dumps(dict(next37_AST_only=True,work_order=str(work),correct_close_gate_BJT=gate,ordinary_helper=str(helper),both_actual_PPO=True)))
except BaseException:
    put(R/('CLOSED35_ACTUAL36_HANDOFF_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc()));raise
