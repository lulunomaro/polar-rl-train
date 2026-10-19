"""Copy to unused *_once.py; one local JSON cfg; no remote actions or training changes."""
from pathlib import Path
import ast, datetime, hashlib, json, re, shutil, subprocess, sys, time, traceback

B=Path(__file__).resolve().parent
R=B/'reports'
NAME=Path(__file__).stem

def put(path,value):
    with path.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)

def local_name(value):
    assert isinstance(value,str) and re.fullmatch(r'[A-Za-z0-9_.-]{3,180}',value)
    return value

def beijing(epoch):
    return datetime.datetime.fromtimestamp(epoch,datetime.timezone(datetime.timedelta(hours=8))).isoformat()

def main():
    assert NAME.endswith('_once') and 'TEMPLATE' not in NAME
    cfg=json.loads((R/local_name(sys.argv[1])).read_bytes())
    for key in ('review_report','reader_receipt','previous_automation_args','work_order','summary','next_reader','version','destination'):
        local_name(cfg[key])
    version=cfg['version'];assert re.fullmatch('V[0-9]+',version)
    cpu=json.loads((R/cfg['review_report']).read_bytes())
    receipt=json.loads((R/cfg['reader_receipt']).read_bytes())
    assert cpu['passed'] and cpu['current_window_actual_learning_verified'] and cpu['same_serial_parent_actual_identity_verified']
    assert receipt['actual_finite_transport_returned'] and not cpu['original_canonical_settled']
    closed=cpu['new_closed_models'];assert closed
    for row in closed:
        assert row['final']['twohost_complete_SHA'] and row['owner_node_all_children_actual_out']
        assert row['all_model_runtime_finite'] and not row['original_canonical_settled']
    active=cpu['current_window'];go=active['GO'];evidence=cpu['current_window_evidence'];worker=evidence['worker'];parent=cpu['parent_identity']
    assert active['spec']['source_SHA']==closed[-1]['final']['SHA']
    assert active['spec']['source_Adamstep']==closed[-1]['Adam_after']
    assert evidence['actual_GO'] and evidence['positive_PPO'] and evidence['matching_UUID_compute'] and evidence['matching_worker_creation_argv']
    source=B/'collect_auto_E3_new_closed_windows_hourly_TEMPLATE.py';destination=B/cfg['next_reader']
    assert not destination.exists();shutil.copy2(source,destination);raw=destination.read_bytes();assert raw==source.read_bytes();ast.parse(raw.decode('utf8'))
    put(R/(version+'_NEXT_UNUSED_READER_COPY_AST_CPU_ACTUAL.json'),{'epoch':time.time(),'source':str(source),'destination':str(destination),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'copy2_exact_AST_passed':True,'not_executed':True,'current_reader_and_review_consumed':True,'no_new_transport_training_model_read':True})
    repo=B.parent/'polar-rl-train'
    def git(*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
    head=git('rev-parse','HEAD');assert not git('status','--porcelain')
    contract=json.loads((R/cfg['previous_automation_args']).read_bytes())
    previous=contract['prompt'];stable='人类明确'+previous.split('人类明确',1)[1]
    boundary=re.search(r'\nV\d+ reader和V\d+ CPUreview',stable);assert boundary
    policy_start=stable.index('Git按',boundary.start());human_contract=stable[:boundary.start()+1]
    policy=stable[policy_start:stable.index('same mod4-10',policy_start)]
    policy=re.sub(r'latest ordinary[a-f0-9]{40}','latest ordinary'+head,policy)
    policy=re.sub(r'全量V51-\d+旧prompt','全量V51-'+str(int(version[1:])-1)+'旧prompt',policy)
    policy=re.sub(r'不自动导出新[^或\n]+或重开','不自动导出当前新E3模型或重开',policy)
    reader_version=int(re.search(r'_V([0-9]+)_once\.py$',cfg['next_reader']).group(1))
    current_reader=Path(cfg['reader_receipt']).name.removesuffix('_RETURNED_ACTUAL.json')+'.py'
    changes=len(receipt['active_text_changes_preserved'])
    readers=(f"本轮{current_reader}与{cfg['review_report']}均实际返回consume，已完整旧窗{cpu['old_complete_windows_not_rehashed']}跳过，不重hash下载。唯一下一unused reader是A/{cfg['next_reader']}；下一新增closed窗或实质失败时先fresh本机CIM按exactbasename/相对或绝对argv+exe/create核无自己finite actualalive占transport，再单72执行一次，远端命令max90/有限复制，不另SSH/watcher/并发读者/5minpoll，不为健康不变取中途PT。finite实际返回才交还210/72/249，其间root只localreports+CIM。运行即consume，随后当前readerTEMPLATE copy2成新unused V{reader_version+1}_once。异常保留原source/error，finite返回/freshCIM后新有界只补缺，不重完整PT/raw/once，不为读者错误停或重健康父。\n"
        "返回后将A/review_auto_E3_new_closed_windows_CPU_TEMPLATE.py copy2为新unused review_*_once.py，唯一argv为该次RETURNED报告文件名；只核该receipt新的完整FINAL和actual下一active，不重旧审查或行为case，variable updates/Adam按实际spec绑定。\n"
        f"本轮{changes}项active text在采集中变化，inventorySHA/capturedSHA及全文均保留，不冒稳定SHA或GPU/网络故障。当前修正archive TEMPLATE仅接受A-Za-z0-9下划线目录，原V54小写guard失败及V2修正成功均已保留consume；后续copy当前模板，不能冒旧SHA。\n")
    final_rows=[]
    for row in closed:
        pending=row['pending_cost'];final_rows.append(f"{row['window']}完整SHA{row['final']['SHA']}/{row['final']['bytes']}bytes/{row['updates']}updates/Adam{row['Adam_after']}，源Adam{row['Adam_before']}；twohostSHA/173total96floating finite/17Adam每update20/actor9含STD与critic8全变化CPU过，owner/node/全部孩子actualout。实际pending{pending['cost']['actual_production_seconds']}s，sourceSHA{pending['GO']['source_SHA']}。")
    prefix=(f"最新actual {version}：E3新闭合窗{[x['window'] for x in closed]}已完整FINAL/wholeCPU，同一父自主进入hour{active['index']:04d}。A={B.as_posix()}。先读A/{cfg['work_order']}、reports/{cfg['review_report']}、{cfg['reader_receipt']}及SERIES_CONFIG_NO_SECRET.json。later ownactual/fullSHA/真实exe-argv-create/GO/FINAL/CPU/EXIT/费用优先，旧PID/排程/资源snapshot不当永久alive/free/futureFINAL。\n"
        +'\n'.join(final_rows)+'\n'
        +f"series已闭合distinctrunid sumonce {cpu['series_completed_actual_pending_seconds']}s，旧single{cpu['previous_single_E3_actual_pending_seconds']}s；Windows9400.860692501068s与未知512s分列，canonical未open/copy/write/结清，不设0/退款/二扣/取整，不把guard当fresh原账余额。同名checkpoint不等于同模型。\n"
        +f"same parent{parent['pid']}/create{parent['creation']}，active owner{active['owner']['detached_pid']}/node{active['node']['detached_pid']}/worker{worker['pid']}/workercreate{worker['creation']}仅receipt身份。actualGO {beijing(go['learning_started_epoch'])}，save {beijing(go['save_deadline'])}/nominalend {beijing(go['nominal_end_epoch'])}只排程；sourceSHA{active['spec']['source_SHA']}/Adam{active['spec']['source_Adamstep']}。positivePPO/matchingUUIDcompute/workercreateargv/同parent身份真核，不冒中途wholeCPU/未来FINAL/持续100%/技能PASS。controller reviewedSHA exact，未热改/停/重健康训练。原锁free只属窗边界，此后新node重新持有。\n")
    monitor=("same mod4-10 ACTIVE/hourly/target01a07a2d-9036-7531-a012-692df9f56353不变，不新增monitor，预算未结束不删monitor。只新完整FINAL/实质失败修复/预算边界/必需人类动作通知；本轮新完整模型和实际自动接续通知后，健康/资源pending未变静默。")
    contract['prompt']=prefix+human_contract+readers+policy+monitor
    args_name='AUTO_E3_'+version+'_AUTOMATION_UPDATE_ARGS.json'
    put(R/args_name,contract)
    order={'epoch':time.time(),'version':version,'CPU_review':str(R/cfg['review_report']),'reader_receipt':str(R/cfg['reader_receipt']),'new_closed_models':closed,'active_snapshot':active,'active_evidence':evidence,'parent_snapshot':parent,'snapshot_epoch':cpu['snapshot_epoch'],'series_pending_seconds':cpu['series_completed_actual_pending_seconds'],'prior_single_pending_seconds':cpu['previous_single_E3_actual_pending_seconds'],'completed_E3_pending_subtotal':cpu['completed_E3_pending_subtotal'],'canonical_settled':False,'next_unused_reader':str(destination),'reader_not_run':True,'current_reader_review_consumed':True,'base_HEAD':head,'all1412_tags_preserved_no_new_trial_tag':True,'no_training_or_player_package_or_cleanup_change':True,'automation_args':args_name,'next_instructions':contract['prompt']}
    put(B/cfg['work_order'],order)
    with (B/cfg['summary']).open('x',encoding='utf8') as f:
        f.write('# '+version+' E3 serial completion audit\n\n'+'\n\n'.join(final_rows)+'\n\n'+f"Same original parent autonomously entered hour{active['index']:04d}, GO {beijing(go['learning_started_epoch'])}. Actual PPO, matching UUID compute and process creation/argv verified at snapshot. Schedules are not future finals.\n\nSeries completed pending seconds: {cpu['series_completed_actual_pending_seconds']}; prior single E3: {cpu['previous_single_E3_actual_pending_seconds']}. Canonical remains untouched and unsettled; legacy Windows/unknown tail remain separate.\n\nCurrent reader/review consumed; next unused reader prepared, not run. All old complete windows skipped without rehash/redownload. Complete text logs and active inventory/capture differences retained. Ordinary Git append, no new trial/tag, training or player/package/cleanup change.\n")
    put(R/(version+'_ORDINARY_ARCHIVE_ARGS.json'),{'base_HEAD':head,'destination':cfg['destination'],'review_report':cfg['review_report'],'reader_receipt':cfg['reader_receipt'],'title':cfg['title']})
    print(json.dumps({'version':version,'new_complete_models':len(closed),'active_index':active['index'],'next_unused_reader':cfg['next_reader'],'prompt_characters':len(contract['prompt']),'base_HEAD':head,'only_local_handoff':True}))

if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/(NAME+'_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),{'epoch':time.time(),'error':traceback.format_exc(),'no_training_or_transport':True})
        raise
