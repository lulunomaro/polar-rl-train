"""Local-only V55 handoff, next unused reader and existing heartbeat arguments."""
from pathlib import Path
import ast, datetime, hashlib, json, shutil, subprocess, time, traceback

B = Path(__file__).resolve().parent
R = B / 'reports'
H = lambda b: hashlib.sha256(b).hexdigest()

def put(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

def beijing(epoch):
    return datetime.datetime.fromtimestamp(epoch, datetime.timezone(datetime.timedelta(hours=8))).isoformat()

def main():
    cpu_name = 'review_auto_E3_fourth_closed_fifth_learning_V55_once_CPU_ACTUAL.json'
    receipt_name = 'collect_auto_E3_new_closed_windows_hourly_V4_once_RETURNED_ACTUAL.json'
    cpu = json.loads((R / cpu_name).read_bytes())
    receipt = json.loads((R / receipt_name).read_bytes())
    assert cpu['passed'] and cpu['current_window_actual_learning_verified']
    assert cpu['same_serial_parent_actual_identity_verified'] and receipt['actual_finite_transport_returned']
    assert len(cpu['new_closed_models']) == 1
    closed = cpu['new_closed_models'][0]
    active = cpu['current_window']
    assert closed['window'] == 'hour0004' and active['index'] == 5
    assert closed['owner_node_all_children_actual_out']
    assert closed['final']['twohost_complete_SHA'] and not cpu['original_canonical_settled']
    src = B / 'collect_auto_E3_new_closed_windows_hourly_TEMPLATE.py'
    dst = B / 'collect_auto_E3_new_closed_windows_hourly_V5_once.py'
    assert not dst.exists()
    shutil.copy2(src, dst)
    assert src.read_bytes() == dst.read_bytes()
    ast.parse(dst.read_text(encoding='utf8'))
    put('V55_NEXT_UNUSED_V5_READER_COPY_AST_CPU_ACTUAL.json', {
        'epoch': time.time(), 'source': str(src), 'destination': str(dst),
        'bytes': dst.stat().st_size, 'SHA': H(dst.read_bytes()),
        'copy2_exact_bytes': True, 'AST_passed': True, 'not_executed': True,
        'V4_reader_actual_returned_consumed': True, 'V55_CPU_review_consumed': True,
        'no_new_training_or_transport_or_model_hash': True})
    repo = B.parent / 'polar-rl-train'
    head = subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'], text=True).strip()
    assert not subprocess.check_output(['git','-C',str(repo),'status','--porcelain'], text=True).strip()
    go = active['GO']
    worker = cpu['current_window_evidence']['worker']
    nchanges = len(receipt.get('active_text_inventory_capture_changes', []))
    # The returned receipt's actual key is preserved in full, even if a later reader changes its summary schema.
    text_change_keys = {k:v for k,v in receipt.items() if 'change' in k.lower()}
    contract = json.loads((R/'AUTO_E3_V54_AUTOMATION_UPDATE_ARGS.json').read_bytes())
    old = contract['prompt']
    stable = '人类明确' + old.split('人类明确',1)[1]
    a = stable.index('V3 reader和V54 CPUreview')
    z = stable.index('Git按', a)
    readers = (
        'V4 reader和V55 CPUreview均实际返回consume，确实跳过旧已收完整hour1/2/3文本和模型，不重hash下载。唯一下一unused reader是A/collect_auto_E3_new_closed_windows_hourly_V5_once.py；下一新增closed窗或实质失败时先fresh本机CIM按exactbasename/相对或绝对argv+exe/create核无自己finite actualalive占transport，再单72执行一次，远端命令max90/有限复制，不另SSH/watcher/并发读者/5minpoll，不为健康不变取中途PT。finite实际返回才交还210/72/249；其间root只localreports+CIM。V5运行即consume，随后当前readerTEMPLATE copy2成新unused V6_once。异常保留全部原source/error，finite返回/freshCIM后新有界只补缺，不重已完整PT/raw/once，不为读者错误停或重健康父。\n'
        '返回后将A/review_auto_E3_new_closed_windows_CPU_TEMPLATE.py copy2为新unused review_*_once.py，唯一argv为本次RETURNED报告文件名；只核该receipt新的完整FINAL和actual下一active，不重旧审查或行为case，actual variable updates/Adam按spec绑定。新窗口text在采集中变化保留inventorySHA/capturedSHA及全文，不冒稳定SHA或GPU/网络故障；本轮5项active text差异有原回执。\n')
    stable = stable[:a] + readers + stable[z:]
    assert '8ab8630fc74cf422410e56533b2f6c03949d7e75' in stable
    stable = stable.replace('8ab8630fc74cf422410e56533b2f6c03949d7e75', head)
    stable = stable.replace('全量V51-53旧prompt', '全量V51-54旧prompt')
    stable = stable.replace('不自动导出新d2de', '不自动导出新7ef9')
    stable = stable.replace('此次第三完整模型/第四actuallearning', '此次第四完整模型/第五actuallearning')
    case_note = ('V54首次ordinary helper只允许小写的destination正则在Git add/commit/目录创建前拒绝大写目录，原helper/AssertionError/报告保留且consume。当前archive TEMPLATE已仅将正则修为A-Za-z0-9下划线，规范化AST和9CPU边界已过；V54_V2已成功ordinary远端核验，不重旧helper或record/tag。后续复制当前修正字节，不能冒旧SHA。本轮V55新unused ordinary helper只补同series资料，不造新GPU阶段。\n')
    prefix = (
        f"最新actual V55：E3自动hour0004真实完整闭合，同一父已自主进入hour0005。A={B.as_posix()}。先读A/NEXT_ACTUAL_AUTOMATIC_E3_FOURTH_CLOSED_FIFTH_LEARNING_V55_WORK_ORDER.json、reports/{cpu_name}、{receipt_name}及SERIES_CONFIG_NO_SECRET.json。later ownactual/fullSHA/实际exe-argv-create/GO/FINAL/CPU/EXIT/费用优先，旧PID、排程、资源快照不当永久alive/free/futureFINAL。\n"
        f"新完整E3 SHA{closed['final']['SHA']}/{closed['final']['bytes']}bytes/{closed['updates']}updates/Adam{closed['Adam_after']}，来源d2de72/Adam{closed['Adam_before']}。twohostSHA、173total96floating finite、17Adam每update20及actor9含六STD/critic8全变化CPU真过。旧owner121498/node121514/worker121521与全部孩子actualout。本窗pending{closed['pending_cost']['cost']['actual_production_seconds']}s，series四窗distinctrunid sumonce {cpu['series_completed_actual_pending_seconds']}s；旧single {cpu['previous_single_E3_actual_pending_seconds']}s、Windows9400.860692501068s、未知512s分列。canonical未打开/复制/写入/结清，不设0/退款/二扣/取整，guard非fresh原账余额。同名final_valid_update99不等于同模型。\n"
        f"原same parent112201/create1792432384.62已启动hour0005：owner{active['owner']['detached_pid']}/node{active['node']['detached_pid']}/worker{worker['pid']}、workercreate{worker['creation']}仅receipt身份。actualGO {beijing(go['learning_started_epoch'])}，save {beijing(go['save_deadline'])}、nominalend {beijing(go['nominal_end_epoch'])}仅排程；源新7ef9/Adam{active['spec']['source_Adamstep']}。positivePPO/matchingUUIDcompute/workercreateargv/同parent身份核真；snapshot最近完整update50/Adam710420仅生产metadata，不下载中途PT，不冒wholeCPU/未来FINAL/持续100%/技能PASS。原锁free仅边界，此后新node重新持有。controller reviewedSHA exact，未hotpatch/停或重启健康训练。\n")
    contract['prompt'] = prefix + case_note + stable
    assert 'V3 reader和V54' not in contract['prompt']
    assert 'collect_auto_E3_new_closed_windows_hourly_V5_once.py' in contract['prompt']
    put('AUTO_E3_V55_AUTOMATION_UPDATE_ARGS.json', contract)
    order = {
        'epoch': time.time(), 'version': 'V55', 'kind': 'same_series_ordinary_completion_audit',
        'CPU_review': str(R/cpu_name), 'reader_receipt': str(R/receipt_name),
        'actual_new_closed': closed, 'active_snapshot': active,
        'active_evidence': cpu['current_window_evidence'], 'parent_snapshot': cpu['parent_identity'],
        'snapshot_epoch': cpu['snapshot_epoch'],
        'series_closed_pending_seconds': cpu['series_completed_actual_pending_seconds'],
        'previous_single_pending_seconds': cpu['previous_single_E3_actual_pending_seconds'],
        'completed_E3_pending_subtotal': cpu['completed_E3_pending_subtotal'],
        'canonical_settled': False, 'original_windows_and_unknown_tail_separate': True,
        'next_unused_reader': str(dst), 'next_reader_not_run': True,
        'all_prior_once_consumed_no_replay': True, 'transport_actual_returned': True,
        'active_text_change_metadata': text_change_keys,
        'Git_before_ordinary_HEAD': head, 'unique_stage_tag_count_unchanged': 1412,
        'no_new_trial_record_or_tag': True, 'no_player_package_cleanup_or_training_change': True,
        'notification': 'new_complete_final_and_fifth_actual_learning',
        'next_instructions': contract['prompt']}
    q = B/'NEXT_ACTUAL_AUTOMATIC_E3_FOURTH_CLOSED_FIFTH_LEARNING_V55_WORK_ORDER.json'
    with q.open('x',encoding='utf8') as f:
        json.dump(order,f,ensure_ascii=False,indent=2)
    summary = (
        '# E3 automatic fourth closure and fifth learning — V55\n\n'
        f"Fourth final `{closed['final']['SHA']}`: {closed['updates']} actual PPO updates, Adam {closed['Adam_before']} to {closed['Adam_after']}. Complete two-host SHA, whole-model 173/96 finite, all 17 actor/critic parameter changes and 20 Adam steps/update verified. Fourth owner/node/all children actually exited.\n\n"
        f"The same original parent autonomously started hour0005 at {beijing(go['learning_started_epoch'])}. Actual GO, positive PPO, matching UUID compute and worker creation/argv verified at the receipt snapshot. Save/nominal end are schedules only. No training code or worker was modified or restarted.\n\n"
        f"Fourth actual interval: {closed['pending_cost']['cost']['actual_production_seconds']} s. Four series windows: {cpu['series_completed_actual_pending_seconds']} s; prior single E3: {cpu['previous_single_E3_actual_pending_seconds']} s. All remain pending original canonical reconciliation. Legacy Windows and unknown tail remain separately reserved; no new budget, original-ledger write, refund or double charge.\n\n"
        'V4 reader and V55 CPU review consumed. V5 reader copied with exact bytes and AST checked, not run. Prior three complete windows were skipped without rehash or redownload. Five active-text inventory/capture differences are retained with complete text.\n\n'
        'Same series ordinary Git append; preserve all 1412 existing tag objects/peels. Complete large text logs use ordered UTF8 parts and full reassembly SHA. Models remain producer path/size/SHA indexes. Package/player and completed cleanup scopes remain unchanged.\n')
    with (B/'AUTOMATIC_E3_FOURTH_CLOSURE_V55_SUMMARY.md').open('x',encoding='utf8') as f:
        f.write(summary)
    put('V55_ORDINARY_ARCHIVE_ARGS.json', {
        'base_HEAD': head, 'destination': 'fourth_closed_fifth_learning_V55_20261020',
        'review_report': cpu_name, 'reader_receipt': receipt_name,
        'title': 'Audit fourth automatic E3 full closure and fifth learning with complete logs and actual pending cost'})
    print(json.dumps({'handoff': str(q), 'next_reader': str(dst), 'prompt_characters':len(contract['prompt']), 'base_HEAD':head, 'only_local_preparation':True}))

if __name__ == '__main__':
    try:
        main()
    except BaseException:
        put('V55_LOCAL_HANDOFF_ORIGINAL_ERROR_'+str(time.time_ns())+'.json', {'epoch':time.time(),'error':traceback.format_exc(),'no_training_or_transport':True})
        raise
