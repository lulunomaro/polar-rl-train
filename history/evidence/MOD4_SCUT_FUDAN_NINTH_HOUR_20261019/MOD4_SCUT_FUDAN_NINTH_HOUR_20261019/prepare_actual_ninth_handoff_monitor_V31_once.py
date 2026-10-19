"""Bind the next collectors to actual ninth-hour identities; retain the player facts."""
from pathlib import Path
import ast,datetime,hashlib,json,time,tomllib
B=Path(__file__).resolve().parent;W=B.parent;P=W/'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019';R=B/'reports'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8') as stream:json.dump(v,stream,ensure_ascii=False,indent=2)
def main():
    d=json.loads((R/'THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes())
    a=json.loads((R/'THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json').read_bytes())
    f=json.loads((P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
    local=json.loads((R/'EIGHTH_HOUR_LOCAL_STRICT_RECOVERY_NORMAL_AND_ACTUATOR_CPU_ACTUAL.json').read_bytes())
    summary=json.loads((R/'EIGHTH_HOUR_LOCAL_EVENTS_AND_DRIFT_CPU_ACTUAL.json').read_bytes())
    owner=d['owner']['detached_pid'];assert owner==293563 and a['three_actual_PPO_learning_verified'] and f['passed_all_three_whole_final_models_CPU']
    assert all(not spec['reward_migration'] for spec in d['specs'].values())
    for name in ('collect_next_hour_missing_closed_finals_bounded_owner_wait_V2_once.py','review_next_closed_hour_finals_whole_model_original_cost_CPU_once.py'):
        s=(P/name).read_text('utf8').replace('281824',str(owner));ast.parse(s)
        with (B/name).open('x',encoding='utf8') as stream:stream.write(s)
    future=B/'future_same_recipe_hour_templates';future.mkdir()
    for name in ('prepare_next_three_closed_sources_one_hour_CPU_once.py','deploy_three_next_closed_source_hours_once.py','closed_production_continuation_CPU_v2.py','collect_next_three_actual_learning_metadata_finite_once.py'):
        s=(B/name).read_text('utf8')
        if name.startswith('prepare_'):
            s=s.replace("T=W/'"+P.name+"'","T=W/'"+B.name+"'").replace('T3sf9_1910v14','T3sf10_1910v15').replace('THREE_GPU_SCUT_FUDAN_HOUR14_','THREE_GPU_SCUT_FUDAN_HOUR15_')
        if name.startswith('deploy_'):
            s=s.replace('T3sf9_1910v14','FUTURE_ROOT').replace('T3sf8_1910v13','T3sf9_1910v14').replace('FUTURE_ROOT','T3sf10_1910v15').replace('281824',str(owner))
        ast.parse(s);(future/name).write_text(s,'utf8')
    rewards=[]
    for name in ('h1_scut_fudan_jump_reward_v1.py','h1_takeoff_progress_environment_v2.py','train_H1_ground_prelaunch_fullstate_v2.py'):
        rel=Path('payload/h1/job0/runtime/isaac/mod4')/name;assert (B/rel).read_bytes()==(P/rel).read_bytes()
        rewards.append(dict(path=str(B/rel),bytes=(B/rel).stat().st_size,SHA=H(B/rel)))
    details={k:dict(source=d['specs'][k]['source_SHA'],Adam=d['specs'][k]['source_Adamstep'],worker=x['worker'],GO=x['GO'],save_Beijing=datetime.datetime.fromtimestamp(x['GO']['save_deadline'],datetime.timezone(datetime.timedelta(hours=8))).isoformat()) for k,x in a['experts'].items()}
    closed={k:dict(final=x['final'],updates=x['updates'],Adam=x['all17Adam_after'],tensor_counts=x['whole_tensor_counts']) for k,x in f['experts'].items()}
    errors=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(R.glob('*ORIGINAL_ERROR*.json'))]
    work='NEXT_ACTUAL_SCUT_FUDAN_NINTH_HOUR_LOCAL_YAW_RETURN_V31_WORK_ORDER.json'
    put(B/work,dict(epoch=time.time(),version=31,previous_complete_CPU=f,new_dispatch=d,actual_three_learning=a,details=details,unchanged_reward_files=rewards,new_source_local_behavior=local,local_events_and_drift=summary,current_original_errors_retained=errors,future_closing_helpers_bound_owner=owner,future_same_recipe_templates=str(future),future_templates_not_executed=True,local_player_remains_human_requested_hour7_bundle=True,not_PhysX_statistical_or_course_PASS=True))
    put(R/'NINTH_HOUR_REWARD_BYTES_AND_FUTURE_BINDING_CPU_ACTUAL.json',dict(epoch=time.time(),reward_bytes_exact=rewards,owner_binding=owner,future_namespace='T3sf10_1910v15',only_prepared_not_deployed=True,current_actual_GO_PPO_GPU_passed=True,not_new_physical_or_skill_gate=True))
    old=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
    assert old['status']=='ACTIVE' and old['rrule']=='FREQ=HOURLY;INTERVAL=1'
    player=old['prompt'].split('\n\n最新actual V30',1)[0]
    assert '最终V3实际run=' in player and '100' in player
    player+='\n本地播放器阶段已实际unique9c85feb/tag9fb2b85/总1394远端main/tag/peeled与原1393标签对象核过，helper/record/tag已consume，不重run。这里只保留事实，不自动重开或换权重。\n\n'
    contract=old['prompt'][old['prompt'].index('人类三卡最大有意义利用'):old['prompt'].index('same mod4-10 ACTIVE/hourly/原target')]
    stale='RM7v7用户玩家不重开/中断/热改，新a21a未自动替换旧hour4 bundle，不称已更新。'
    assert stale in contract
    contract=contract.replace(stale,'RM7v7用户玩家保留人类已要求导出的第七小时新bundle与两处本地修复；当前第八小时新1078源未自动替换玩家，不称已更新到第八小时，不重开/中断/热改。')
    contract=contract.replace('旧cf5/db76/3302/1338/c174/81fc本机结果','旧cf5/db76/3302/1338/c174/81fc/a21a本机结果')
    cost=f['one_original_writer_actual_segment']['charged_expert_seconds'];remaining=f['remaining_snapshot']
    sources='；'.join(f"{k} {x['final']['SHA']}/{x['updates']}updates/Adam{x['all17Adam_after']}" for k,x in f['experts'].items())
    head=f'''最新actual V31覆盖V30旧281824 active：SCUT+Fudan第八小时已真实完整保存、三wholeCPU/原独立费用sumonce结清，原owner及所有孩子actualout/EXIT0/canonicalNone/原两fcntl及private/shared实际free。I={B.as_posix()}；H=同workspace/{P.name}。先读I/{work}、I/reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json、THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json及H/reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json。later自己的完整sourceSHA/创建exe-argv-create/GO/真实保存EXIT/原canonical/fcntl优先，不拿PID/计划/快照当永久alive或futureFINAL。旧current及prepared只作历史，原工作单与Git保留。
第八小时完整{sources}。三完整PT twohostSHA、199105/17598/17396全modelruntimefinite、17Adam每update20及actor9含STDcritic8全17项变化真过。原{cost}s独立sumonce结清、remaining{remaining}仅读取snapshot，不二扣/refund/clearactive/取整。
三4090从各自这些最新完整源接续同recipe第九小时，neworiginalwriter{owner}，sourceROOT{d['source_root']}，E2node{d['nodes']['e2']['detached_pid']}、72H1node{d['nodes']['h1']['detached_pid']}/E3node{d['nodes']['recovery']['detached_pid']}。实际三GO/positivePPO/matchingUUIDcompute已核；details真实creation/source/GO/save/nominalend与lateractual准，不冒中途wholeCPU/技能PASS/持续100%。每卡原3600GO到save/lifecycle3900含300exit/no24cutoff/20k×24，远端自主完整saveSDKclosechildwait/ownerterminal，不依Laptop/hourly；不hotextend/停健康三卡/中途重型PT或行为审计。
closed_same_backend_production、reward_migration=False；33错source/backend/GPU/Adam/schema/finite/EXIT/cost/runtime/AST负例拒绝，实际target whole-source/installedSDKmath/RSL/runtimeassets核过。三SCUTFudan rewardbytes exact上一段，worker仅sourcefilename/Adam绑定，actorcritic六STD/17Adam/RNG/phase/20kDR整态继承，不回退旧源/重复迁移/插两遍telemetry/恢复旧reward/反向E3 native336。nativeCPU=None/source_native_CPU_SHA=null/nativeGPUwaitfalse，无重复standalone native/nativePASS；真实backend或physics/runtime变化仍走原流程。
仅用新1078完整源做本机CPU MuJoCo原October8 flat normal/jump×yaw0/pi四轨迹，旧case只读raw比较，不重放。I/reports/EIGHTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json、EIGHTH_HOUR_LOCAL_STRICT_RECOVERY_NORMAL_AND_ACTUATOR_CPU_ACTUAL.json和EIGHTH_HOUR_LOCAL_EVENTS_AND_DRIFT_CPU_ACTUAL.json优先。两jump各原strict起跳1/落地1/恢复1且活15s，事件约1.1375/1.4075/2.605s，双轮最低净空峰约.0844603m、原prepare最长396callback且readyTrue。但约13.4225s恢复后yaw再次越原.2rad，15s末约+.210646rad，前代a21a在15s内未越且末-.152729；恢复最长4526callback较前代5127短。原recovered为sticky，不能把事件当持续stationkeeping；更高净空与再次晚期yaw越界是混合变化，不说整体修好。
两normal活15s，末零命令速度约.0070548m/s比前代.0138565小，净位移.119064m比.189638小，末yaw约+.0700283rad绝对值比前代-.300421小；只是这两个yaw的本机观测改善，不是完整normal不退化/PhysX资格/统计显著/唯一奖励因果或毕业。原46callback/14actuator/23reward列保留无重复插入，本机真实d.actuator_force六通道与d.ctrl在记录callback相等；normal九新项0和Fudan每weighted±2.5真核，不冒PhysX applied_torque或生产RewardManager/PPO return。源脚本SHA以实际bytes核，旧LF解释只属旧报告。
原瞬时yaw-rate目标与累计yaw恢复条件的源区别仍见H/reports/NORMAL_YAW_RATE_SOURCE_OBJECTIVE_CPU_ACTUAL.json，三reward/runtimebytes保持；没有为本次漂移盲改reward/LR/STD/actor输入/外部请求时钟/纠偏外力/physics/CAD/guard或heldout61011/12。下一自然保存的新源继续优先看恢复后yaw增长/普通停车与真实奖励生效项，不只报PPO/奖励涨。
下一小时末仅用I自己prepared collect_next_hour_missing_closed_finals_bounded_owner_wait_V2_once.py和review_next_closed_hour_finals_whole_model_original_cost_CPU_once.py，绑定{owner}，不重旧H281824或旧collector/preparer/deployer/Task/native/once。相同source连接max900只等实际终态metadata；actualclosed才取缺三完整FINAL/PT/原费用/out/canonicalNone/原两fcntl/private共享free，wholeCPU后及时接续，不机械等下一heartbeat。若提前距save加正常退出明显超过900，先只本机report/CIM和短有界本机等待，临近再启动自己单collector，无第二watcher/并发SSH。不按排程猜FINAL。missing/error原样留，finite实际返回/freshCIM后新有界只补缺，不重完整PT/raw/once。未来只用I/future_same_recipe_hour_templates，I实际closed/fullCPU后复制新unused阶段prepare，T3sf10_1910v15仅reserved。metadata同连接max600/keepalive15/append-only journal，只要求实际GO/PPO/GPU，不为瞬时public4active0额外等；保留奖励readout，first正常批非辅助效果或技能成绩。保留当前recipe/telemetry，勿重复插入。
'''
    tail='''same mod4-10 ACTIVE/hourly/原target01a07a2d-9036-7531-a012-692df9f56353，不建第二monitor/自动预算。健康unchanged/pending静默，只新完整FINAL/新冻结/实质修复/重大退化/必需人类动作通知。第八小时闭合、新本机晚期yaw再次越界及normal改善、第九小时实际接训通知后不重复旧成绩。原预算未结束不删monitor。
新stage scut-fudan-ninth-hour-closed-sources-local-late-yaw-recurrence只record一次，以lateractualGit回执为准；已record不重helper/record/tag/同commit，pushfail只已有objects。H unique0545ebf/tag12dd741/总1393、本地playerunique9c85feb/tag9fb2b85/总1394及旧stage/helper/Task/native/once均consume。全部H/I source/文本报告/错误/未用helpers/工作单monitor/appreceipt/原费用入Git；>50MB全文orderedUTF8parts+全重组SHA，PT/NPZ/USD/ZIP/raw只producer actualpathsizeSHA保原件，不为Git重GPU/改账/重hash下载旧件/无限补HEAD。后续新报告普通补档，跨午夜stage/trial用实际记录日期不回填历史。
'''
    prompt=player+head+contract+tail+'本阶段原错误索引：'+json.dumps(errors,ensure_ascii=False)+'\n\n第八小时完整源与第九小时实际创建/GO/排程：\n'+json.dumps(dict(closed=closed,owner=d['owner'],nodes=d['nodes'],source_root=d['source_root'],roots=d['roots'],details=details),ensure_ascii=False,indent=2)
    put(B/'AUTOMATION_ACTUAL_SAME_RECIPE_NINTH_HOUR_V31_ARGS.json',dict(mode='update',id='mod4-10',kind='heartbeat',name=old['name'],prompt=prompt,rrule=old['rrule'],status=old['status'],targetThreadId=old['target_thread_id']))
    (B/'STAGE_SUMMARY.md').write_text('# Eighth reward-hour closure, ninth-hour continuation, and recurrent late yaw in local jump recovery\n\n'+json.dumps(dict(closed=closed,cost_once=cost,remaining_snapshot=remaining,new_dispatch=d,actual_learning=a,local_evidence=local,local_summary=summary,current_errors=errors,scope='Same recipe/PPO/physics/LR/STD/budget, prior failed and false results retained; four new-source local traces only, no live player update or PhysX/course qualification.'),ensure_ascii=False,indent=2),'utf8')
    print(json.dumps(dict(owner=owner,save={k:x['save_Beijing'] for k,x in details.items()},future_helpers_prepared=True)))
if __name__=='__main__':main()
