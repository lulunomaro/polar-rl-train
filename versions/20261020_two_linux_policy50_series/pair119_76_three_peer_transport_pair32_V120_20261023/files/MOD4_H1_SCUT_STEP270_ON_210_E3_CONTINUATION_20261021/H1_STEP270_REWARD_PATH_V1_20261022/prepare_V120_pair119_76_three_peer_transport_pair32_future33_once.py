from pathlib import Path
from datetime import datetime, timezone, timedelta
import ast, hashlib, json, shutil, time, tomllib, traceback

B=Path(__file__).resolve().parent; T=B.parent; W=T.parent; R=B/'reports'
C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88'
P=T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V31_20261023'
N=T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V32_20261023'
F=T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V33_20261023'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

def main():
    proof=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
    closed=read(R/'V119_CURRENT31_CLOSED_BOUNDARY_HEALTH_RETENTION_EPISODE_CPU_ACTUAL.json')
    transfer=read(P/'reports/PEER_FORENSICS_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json')
    meta=read(N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json')
    cpu=read(N/'reports/H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json')
    ecpu=read(N/'reports/RECOVERY_TWO50_FULL_TARGET_SOURCE_RSL_SDK_CPU_ACTUAL.json')
    prepared=read(N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
    resource=read(N/'reports/NEXT_E3_BOUNDARY_RESOURCE_COMPONENTS_ACTUAL.json')
    repair=read(R/'V120_SAME_AUTHORIZED_THREAD_COMPRESSED_SESSION_AND_MISSING_ONLY_COLLECTOR_CPU_ACTUAL.json')
    assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
    assert closed['passed_checkpoint_health_and_recording_scope'] and transfer['passed'] and transfer['source_above_original_disk25'] and transfer['all_own_storage_processes_actual_out']
    assert meta['passed'] and meta['actual_finite_returned'] and cpu['passed_CPU_only'] and ecpu['passed_CPU_only'] and repair['passed_CPU']
    assert all(resource[k] for k in ('expected_GPU_empty','GPU7000_passed','disk25_passed','RAM8_passed'))
    src=meta['source210']; gos=src['current']['go']; ppos={k:src['current']['rows'][k]['latest_save'] for k in ('h1','recovery')}
    assert set(gos)==set(proof['models'])=={'h1','recovery'}
    for k in gos:
        assert gos[k]['source_SHA']==proof['models'][k]['final']['SHA'] and ppos[k]['updates']>0
    assert ppos['h1']['actual17Adam_steps']==[proof['models']['h1']['Adam']+20*ppos['h1']['updates']]
    assert ppos['recovery']['Adam_step']==proof['models']['recovery']['Adam']+20*ppos['recovery']['updates']
    assert cpu['reward_runtime_SHA']=='0ec7db1fc55ca0d552341e24237048a916d1cbb6b125905eb22b0001b60a8e34'
    assert not F.exists(); F.mkdir(); (F/'reports').mkdir()
    for name in ('paired_controllers','h1_only_controllers','repair_sources'):shutil.copytree(N/name,F/name)
    for p in N.glob('*.py'):
        if 'UNEXECUTED' in p.name or 'UNUSED_OLD' in p.name:continue
        s=p.read_text('utf8').replace(P.name,N.name).replace('H1step270_reward_boundary_2310v32','H1step270_reward_boundary_2310v33');ast.parse(s)
        with (F/p.name).open('x',encoding='utf8') as f:f.write(s)
    for p in F.rglob('*.py'):ast.parse(p.read_text('utf8'))
    for p in (N/'repair_sources').rglob('*'):
        if p.is_file():assert H(p)==H(F/'repair_sources'/p.relative_to(N/'repair_sources'))
    prep=(F/'prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py').read_text('utf8')
    assert N.name in prep and ';E=P' in prep and 'PAIR_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json' in prep and 'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json' in prep
    assert 'H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json' not in prep
    put(R/'V120_NEXT_BOUNDARY_RESOURCE33_PAIRED_PREDECESSOR_UNUSED_SOURCE_AST_ACTUAL.json',dict(epoch=time.time(),passed_AST=True,current_stage=str(N),future_stage=str(F),current32_both_realGO_positivePPO_observed=True,no_future_model_payload_Task_GO_or_fee=True,same_boundary_reward_trace_adapter_loader_byteexact=True,previous_proof_mode='paired',H1_and_E3_sources_dynamic_from_actual_closed32=True,H1_only_scheduler_historical_CPU_reference_is_conditional=True))
    reader=(B/'review_closed31_boundary_health_retention_text_CPU_once.py').read_text('utf8').replace(P.name,N.name).replace('V119_CURRENT31_CLOSED_BOUNDARY_HEALTH_RETENTION_EPISODE_CPU_ACTUAL.json','V120_CURRENT32_CLOSED_BOUNDARY_HEALTH_RETENTION_EPISODE_CPU_ACTUAL.json').replace('CLOSED31_TEXT_CPU_ORIGINAL_ERROR_','CLOSED32_TEXT_CPU_ORIGINAL_ERROR_');ast.parse(reader)
    with (B/'review_closed32_boundary_health_retention_text_CPU_once.py').open('x',encoding='utf8') as f:f.write(reader)
    put(R/'V120_PAIR32_INSTALLED_BOTH_SOURCES_FIRST_PPO_WARNING_RETURN0_ACTUAL.json',dict(epoch=time.time(),sources=prepared['sources'],H1_installed_source_CPU=cpu,E3_installed_source_CPU=ecpu,actual_first_PPO=ppos,actual_preparer_returncode=0,nonfatal_SyntaxWarning_count=2,nonfatal_SyntaxWarning='invalid escape sequence \\S',same_authorized_compressed_session_adapter=str(B/'same_authorized_session_compressed_transport_v1.py'),no_training_hotpatch_or_old_case_replay=True))
    work=T/'reports/NEXT_ACTUAL_PAIR31_COMPLETE119_76_THREE_PEER_TRANSPORT_REPAIRED_PAIR32_PPO_V120_WORK_ORDER.json'
    put(work,dict(epoch=time.time(),latest_actual=True,previous_stage=P.name,complete_original_pair_models_cost_CPU=proof,closed_H1_health_retention_episode=closed,current31_three_NPZ_verified_transfer=transfer,local_transport_error_preserved=list(map(str,(P/'reports').glob('PAIR_CLOSING_ORIGINAL_ERROR_*.json'))),same_authorized_session_compressed_transport_CPU=repair,missing_only_collector_actual_returned=True,current_stage=N.name,current_mode_paired=True,actual_run_id=meta['run_id'],owner=src['owner'],H1_worker=src['H1_worker'],E3_worker=meta['source72']['worker'],actual_GO=gos,first_PPO=ppos,H1_installed_source_CPU=cpu,E3_installed_source_CPU=ecpu,E3_fresh_resource_snapshot=resource,next33_only_AST=str(F),old_pair11_cumulative_unselected_producer_entries=11,unselected_not_fresh_statted_or_hashed=True,not_270mm_skill_or_future_FINAL=True))
    gate=datetime.fromtimestamp(max(x['nominal_end_epoch'] for x in gos.values())-900,timezone(timedelta(hours=8))).isoformat()
    model=proof['models']['h1']; emodel=proof['models']['recovery']; health=closed['health']; ret=closed['retention']; episode=closed['H1_current_episode_snapshot']
    old=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))['prompt']
    tail=old[old.index('runtime0ec7db1fc55ca0d552'):old.index('Git同reward唯一trial')]
    prompt=f'''V120 latestactual覆盖V119当前31active/未来32reserved。人类回放奖励和明确存储授权已执行，同reward继续，不重复问。
T={T.as_posix()}；B=T/H1_STEP270_REWARD_PATH_V1_20261022；当前N={N.name}，paired=True。先读T/reports/{work.name}、N/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json、B/reports/V119_CURRENT31_CLOSED_BOUNDARY_HEALTH_RETENTION_EPISODE_CPU_ACTUAL.json、V120_NEXT_BOUNDARY_RESOURCE33_PAIRED_PREDECESSOR_UNUSED_SOURCE_AST_ACTUAL.json与P/reports/PEER_FORENSICS_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json（P={P.name}）。完整SHA/actual exe argv create/GO FINAL CPU EXIT/canonical锁回执优先；旧PID/排程/资源/首PPO只snapshot，不冒永久alive/free或futureFINAL。
上一31两真实完整FINAL/wholeCPU/原费/allout核真：H1完整{model['updates']}PPO/全17Adam{model['Adam']}/{model['final']['bytes']}bytes/fullSHA{model['final']['SHA']}；E3完整{emodel['updates']}/Adam{emodel['Adam']}/{emodel['final']['bytes']}bytes/fullSHA{emodel['final']['SHA']}。两hostSHA/H1202/106 E3173/96finite/全17Adam每update20/actor9含六STDcritic8全变化/同H1270phase和E350Hzbackend CPU真过。原owner/两node孩子allout、canonicalNone/两原fcntl/H1lease与72private共享free。H1原费{model['actual_cost']['charged_seconds']}s/E3{emodel['actual_cost']['charged_seconds']}s各真实GO至terminal独立sumonce，总{proof['actual_cost_sumonce']}s，remaining{proof['remaining_actual_snapshot']}仅闭合后当前GO前snapshot非fresh余额。collector原错误和missing-only补缺/CPU/textreader均consume，不重PT/rawhash/native/query/首metadata；来源必须两份最新完整，不退30/29/28/18或failedprefix。
H1本窗{health['control_steps']}controls/{health['actual_physics_callbacks']}callbacks=expected，unknown0/integrity0/nonfiniteFalse/coverageexact/stopNone，ordinary{health['ordinary_episode_reset_events']}，原各终止数={json.dumps(health['termination_events_by_reason'])}，timeouts单列，legacy_single_peak2mm=False保留，无disk_savedstop。31arena0不挪用29完整118/2arena或23完整120/5arena修复证据；历史已验证单环境arena reset后继续FINAL，不冒重现旧env11843同轨迹/未来保证，不重GPU。
FINAL当前20k episode snapshot={json.dumps(episode)}。仅selectedreset未清掉的当前episode状态，非整窗累计/全历史/冻结正式评测，不与旧峰值比较收益退步，不称270mm成功。摘要来自原wholeCPU同次加载，无额外PT/actor/optimizer/RNG/GPU或新门槛。
本窗retention={json.dumps(ret)}。119producer完整pathbytesSHA/116不可变intentreceipt/history exact，保留0/117/118，232中途NPZ/preupdate按持续批准prune，原all_success_and_failed_control_prefixes_retained=False和failureflagFalse不改，approvedprune不可恢复。只保存文字审查，不重首窗目录stat/12CPU/raw/PT/GPU。
31三份NPZ0/117/118合{sum(x['bytes'] for x in transfer['files'])}bytes已完整producer/source/targetSHA和signedack后才释放210核真重复；原件现72 /home/lc01/Zonglin Li/zonglin2/forensic_originals/PEER_TLS_{P.name}/retained_control_npz，配套preupdate/PT/FINAL/source/errors/logs仍210。INDEX是转存前snapshot，不能说3个旧210路径仍有原件。全部senderreceiver actualout/全文receipt返回，sourceafter{transfer['source_free_after']}bytes>25GiB仅GO前snapshot，后续仍fresh25。helperconsume不重搬/hash。旧30/28/26各3NPZ仍210，旧29/27已72；旧pair11累计61+12+6+6+5+6已按SHA报告72，尚11producer未选未fresh逐个stat/hash。本轮没再搬旧11，不能冒迁完或重旧批。
本次真实localtransport错误：31原collector在SSH连接前因旧授权会话.jsonl已变为同名.jsonl.zst而FileNotFoundError，原source/error/STARTED保留consume不重run。新CPU仅用同一exactbasename压缩文件流式解码，原recover筛选函数和host pin字节不改、密码只memory/stdin，无解压落盘/输出/环境变量/其他会话读取。新missing-only collector只新STARTED/error名，原closing AST exact，缺的两FINAL/PT/text一次补齐，已actualreturn consume。B/reports/V120_SAME_AUTHORIZED_THREAD_COMPRESSED_SESSION_AND_MISSING_ONLY_COLLECTOR_CPU_ACTUAL.json核真，未因该本机错误signal训练/造失败或退款。
此后凡需210transport，必须用本机Python314 -B -X utf8 B/same_authorized_session_compressed_transport_v1.py <对应unused helper绝对路径>执行。它只替换本进程旧SESSION.open为同一zstd stream，再runpy原helper；不编辑旧transport、不绕过准入/host pin、不重旧once。当前32metadata/deployer/storage和未来同名helpers已在allowlist；新missing-only basename若需要须新版本allowlist并CPU核原筛选，不盲run旧失败collector。纯CPU reviewer/preparer不需要wrapper。
当前fresh E3资源snapshot={json.dumps(resource)}，allocation0/emptyTrue/free24203/RAM8/disk25过后deployer再次fresh检查才GO。只allocation计数，不查peer身份/PIDargv/kill/删锁。snapshot非永久空卡，健康worker不能重套空卡或启动剩余VRAM停训。
当前runid={meta['run_id']}；owner={json.dumps(src['owner'])}；H1worker={json.dumps(src['H1_worker'])}；E3worker={json.dumps(meta['source72']['worker'])}；actualGO/save/end={json.dumps(gos)}；两首PPO={json.dumps(ppos)}。H1从最新119/{model['final']['SHA']}/{model['Adam']}同270phase/0ec7/d0f reward整态继续；E3从最新76/{emodel['final']['SHA']}/{emodel['Adam']}同50Hzbackend继续。首PPO仅producer snapshot，非本窗wholeCPU/全tensor变化/技能/持续利用率/alive/futureFINAL。sourcefilename仅alias，以完整SHA/Adam/整态为身份。sourceH1actualsavedoptimizerLR={cpu['actual_optimizer_saved_LR']}和配置1e-4 adaptive分列，六STD/全17Adam不reset/freeze。两条非致命\\S SyntaxWarning actual0/installed整sourceSDKmathRSL/phase17Adam/boundary实际函数/rewardSDKcompute/valid_ready/E3sourceCPU/首metadata均consume，不重Task/root/owner/helper/首metadata/中途PT，无跨窗serial父；未选H1-only分支禁止运行。
每slotGO至save3600/lifecycle3900含300exit原端自主全save SDKclose childwait，唯一原writer收到各terminal独立sumonce，不依Laptop、不二扣/退款/clearcanonical。still7800reserve及82512.86069250107严格门槛。
N唯一unused collect_selected_pair_finals_unused_once.py仅max实际nominalend-now<=900临近，准确gateBJT={gate}由epoch自动换算。先fresh本机CIM exactbasename/相对或绝对argv+exe/create确认无自己finite，再经上述zstd wrapper单finite210max900等COHORT_FINAL/OWNER_EXIT/owner H1node孩子allout/canonicalNone/两fcntl/H1lease，再72max210核E3node孩子out/private共享free，只缺两新FINAL/PT/全text/各原费用。原<=900本机assert保持，V116旧未用稿历史不改。returned后唯一unused review_selected_pair_models_unused_once.py用CPUtorch核两完整finite/17Adam每update20/actor9含STDcritic8变化/H1270phase/E350Hz/各原费/allout，同次H1FINAL非gating episode摘要不额外PT；再B/review_closed32_boundary_health_retention_text_CPU_once.py动态health/retention文字CPU。明显>900只localreports/CIM/<=60s短等，不5minpoll/第二watcher/机械等下一heartbeat。failure保留prefix/error/cost，健康另一槽继续；不以rc0/prefix冒FINAL/设0退款。returned/freshCIM后只新unused missing-only，不重旧完整件/once；两槽未都完整不运行要求bothFINAL的33正常preparer，先诊断新failure、仅最新qualified各来源新unused接续。
N unused relocate_selected_pair_closed_forensics_unused_once.py仅两实际完整闭合CPU/health/费用/allout后通过同wrapper freshsource/canonicalNone/原锁/disk；>25GiB不建转存，不足先fresh72保留25GiB，仍在本窗NPZ最小足够subset source+selected>25且target-selected>25才新target/controller，max20GiB上限非必搬；producer/source/target完整SHA/mtime/inode/signedack后仅释放210核真重复/allout/全text。当前3不足则真实blocked留源，检查source_above_original_disk25不以rc0冒free、不newdeployer；可新unused精确missing-only旧11剩11或其他已闭合仍在原件所需部分，freshcapacity、不重旧批/降25或8/删唯一原件/停健康窗。复用TLS core31e6c729fad4c7e73e60843535f602f95ab0eec0b18f2cc24262d1167840dcd7及passedCPU，单顺序SSH控制/独立peerTLS/pin交付指纹/tokenkey只memory/stdin/memfd，不经C慢链/改防火墙权限挂载。512MiB只missing-only copy选量余量非新训练gate，不重复问已有转存许可。
下一唯一F={F.name}仅sourceAST/controllers/repair_sources/config reserved，无未来source模型payload/Task/GO/费用。32两实际完整FINAL/wholeCPU/health/费/allout/freshsource>25后，F/read_E3_resource_only_after_actual_H1_closed_CPU_once.py先读32 PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json，再fresh72 empty/free7000/RAM8/disk25不查peer；returned后prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py动态H1和E3都取届时32最新完整fullSHA/Adam/整态/独立结清源（E=P），不退31/30/29/28/18。四resource全真paired=True否则H1onlyFalse，只所选newdeployer（通过wrapper）→returned对应firstPPO（wrapper），一分支/唯一writer。H1-only scheduler仅该分支读27历史四编辑CPU并动态新source/Adam/ownerSHA，不要求paired32不存在的H1-only回执。previousowner用32 PAIR_ORIGINAL_ACCOUNT_DETACHED，closingreceipt用PAIR_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED。deployer再次fresh旧allout/canonicalNone/两fcntl/H1lease/unusedroot/H1empty15669/E3empty7000/RAM8/disk25/installed整sourceSDKRSL/phase17Adam/boundary函数/rewardSDKcompute/valid_ready，H1only另owneraccountauthAST。当前32repair_sources 0ec7runtime/loader/checker/target/derivedauth/reference整字节复制，0ec7→same0ec7同reward，不退510rootonly/352/674740/publiconly/partial/fallback。资源拒绝保留原error，只新unused namespace不重pair19/consume；actualGO/PPO后才后继reserved。若未来33 H1-only，下一恢复E3仍最新qualified32，按actualmode生成后继。
S=MOD4_HOST72_CLOSED_TASKS_CLEANUP_AUTHORIZED_20261022_V112，人类“两项都做”仅15旧窗+164副本已释放256202215424bytes；1450已批准不可恢复中途/90保留配套/1619全文audit/自身退出consume。不能重cleanup/hash或扩删其他oldraw/forensic/failed/native/FINAL/source/error/log；旧INDEXall_retained/NOT_AUTHORIZED历史snapshot，实际INTENT/ACTION/COMPLETE与hardlink元数据回执为准。存储问题已答，不重问或重复通知。
{tail}
Git同reward唯一trial0fdb24bd67cbb0442c706de643aa7cc3b15cb989/trial-20261022-h1-step270-forward-clearance-reward-v1和独立cleanup唯一trial均consume，不重record/tag/helper。1423tags原objects/peels不动；前次ordinaryfd5930069fb1594bb3648c7023e3c8899a18e7b6/61775文字引用/364新Gitfiles/2大文字orderedUTF8parts核真。本轮31两完整119/76/720060799380/原费退出/health/116retention回执/3NPZ真实72位置/本机旧session缺失错误/同压缩会话CPU修复/新missing-only全回执/new32两GO首PPO/33动态paired前窗/source/全部warning/工作单/monitor回执同阶段ordinary全档，不只成功摘要。pushfail仅续已有objects；binary只producer真实pathsize已有SHA，不为Git重PT/rawhash/GPU/训练host/账，大文字全orderedUTF8parts/重组SHA，postGit工具回执留对话不无限追HEAD。
same mod4-10 ACTIVE/hourly/原target01a07a2d-9036-7531-a012-692df9f56353，无第二monitor/预算未尽不删。只新完整FINAL/新评测/实质修复/资源预算边界/必要人类动作通知；健康或未变pending静默。本轮31完整/new32两PPO/本机transport修复已通知，不重复首metadata/旧raw/旧cleanup/已答问题。MoE/player原100Hz包不自动导出/热改；T2-z仅询问，无download/worldmodel/newinputs/PPO授权。'''
    put(R/'V120_PAIR32_ACTUAL_MONITOR_UPDATE_ARGS.json',dict(mode='update',id='mod4-10',kind='heartbeat',name='MOD4计划与双机并行巡检',status='ACTIVE',rrule='FREQ=HOURLY;INTERVAL=1',targetThreadId='01a07a2d-9036-7531-a012-692df9f56353',prompt=prompt))
    text=(C/'append_pair119_76_old11six_pair31_V119_ordinary_once.py').read_text('utf8')
    text=text.replace("P=T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V30_20261023'","P=T/'"+P.name+"'")
    text=text.replace('H1_STEP270_REWARD_BOUNDARY_RESOURCE_V31_20261023/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json',N.name+'/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json')
    text=text.replace('NEXT_ACTUAL_PAIR30_COMPLETE119_76_OLD11_SIX_PAIR31_PPO_V119_WORK_ORDER.json',work.name).replace('complete30_H1119_E376_Adam717680_797860_old11six_pair31_both_PPO','complete31_H1119_E376_Adam720060_799380_threepeer_transport_pair32_both_PPO')
    assert text.count('known={}')==1
    text=text.replace('known={}',"known={}\n for x in json.loads((T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V30_20261023/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['models'].values():known[str(Path(x['final']['local_path']).resolve())]=x['final']['SHA']")
    ast.parse(text)
    with (C/'append_pair119_76_three_peer_transport_pair32_V120_ordinary_once.py').open('x',encoding='utf8') as f:f.write(text)
    put(C/'reports/REWARD_V120_ORDINARY_ARCHIVE_CONFIG.json',dict(destination='pair119_76_three_peer_transport_pair32_V120_20261023',base_HEAD='fd5930069fb1594bb3648c7023e3c8899a18e7b6',title='Record complete pair31, compressed-session transport repair and paired32 actual PPO'))
    print(json.dumps(dict(pair32_both_realPPO=True,complete_sources={k:v['final']['SHA'] for k,v in proof['models'].items()},future33_dynamic_paired_predecessor_AST_only=True,correct_collect_gate_BJT=gate,ordinary_archive_prepared=True)))

if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('V120_HANDOFF_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc()));raise
