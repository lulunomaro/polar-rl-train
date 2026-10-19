"""Prepare a same-pending-stage handoff and ordinary saved-report append."""
from pathlib import Path
import ast,hashlib,json,shutil,time,tomllib
B=Path(__file__).resolve().parent;R=B/'reports';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
receipt=R/'collect_pending_seventeenth_capacity_hourly_V2_once_RETURNED_ACTUAL.json';v=json.loads(receipt.read_bytes())
assert v['actual_finite_transport_returned'] and not v['ready_for_prepared_deployer_resource_checks'] and v['durable']['free']<25*1024**3
assert not (R/'THREE_NEXT_HOUR_DEPLOY_STARTED_ACTUAL.json').exists()
next_reader=B/'collect_pending_seventeenth_capacity_hourly_V3_once.py';assert not next_reader.exists();shutil.copy2(B/'collect_pending_seventeenth_capacity_hourly_V2_once.py',next_reader);ast.parse(next_reader.read_text('utf8'))
work='NEXT_ACTUAL_SEVENTEENTH_CAPACITY_RECHECK_UNCHANGED_V40C_WORK_ORDER.json'
put(B/work,dict(epoch=time.time(),version='40C',returned_capacity_receipt=dict(path=str(receipt),bytes=receipt.stat().st_size,SHA=H(receipt),actual=v),original_capacity_guard_unchanged=True,seventeenth_still_no_owner_worker_GO_PPO_or_charge=True,original_and_V2_capacity_readers_consumed_after_actual_return=True,next_unused_bounded_capacity_reader=dict(path=str(next_reader),bytes=next_reader.stat().st_size,SHA=H(next_reader)),no_dense_retry_second_watcher_GPU_Task_native_model_raw_hash_account_or_player_change=True,no_new_behavior_case_replay=True,prior_pending_unique_commit='5dc566764b027eb886ee7fc97de7467eb25a903e',prior_ordinary_capacity_append_commit='c1b331de6c46f2290f97eb803cda91d45c88d0f5',all1405_prior_tags_unchanged=True,this_is_same_pending_stage_ordinary_supplement_not_new_trial=True))
old=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert old['status']=='ACTIVE' and '最新actual V40B覆盖V40首次prepared容量读者状态：' in old['prompt']
prompt=old['prompt'].replace('最新actual V40B覆盖V40首次prepared容量读者状态：','最新actual V40C覆盖V40B容量读者状态：').replace('NEXT_ACTUAL_SEVENTEENTH_CAPACITY_RECHECK_UNCHANGED_V40B_WORK_ORDER.json',work)
start=prompt.index('本轮唯一容量读者Q/collect_pending_seventeenth_capacity_finite_once.py已经真实返回并consume');end=prompt.index('只有fresh容量ready',start)
paragraph=f'''本轮唯一V2容量读者Q/collect_pending_seventeenth_capacity_hourly_V2_once.py已经真实返回并consume；actual epoch={v['epoch']}，free={v['durable']['free']}bytes={v['durable']['free']/1024**3}GiB，ready=False，仍低于原strict>25GiB。原首次reader也早已consume；两份原started/returned/source全部保留。当前receipt全文Q/reports/collect_pending_seventeenth_capacity_hourly_V2_once_RETURNED_ACTUAL.json，原锁/GPUfree/RAM/compute只属该次瞬时事实；没有新17owner/GO/PPO/费用、旧模型/rawhash、peer身份读取或其他进程干预。
下一有意义容量变化或后续hourly只能fresh本机CIM核无其他自己finite实际alive占transport后，执行新unused Q/{next_reader.name}一次，单72连接只读容量/RAM/原私有共享锁/GPUfree/compute，命令max60。首次reader和V2均不能重run，V3一旦实际运行也consume；仍unready保留receipt/pending静默，不密集重试/第二watcher/5minpoll。只在下一有意义human/容量变化或hourly用新有界missing-capacity读者。原25GiB/GPU>7000MiB/RAM>8GiB/锁保护不降，H1human sharing持续有效、E3原GPUempty不改。ready只代表72瞬时资源，unused deployer还须fresh核210/72/canonical/旧ownerout，不冒永久alive/free或futureFINAL。
'''
prompt=prompt[:start]+paragraph+prompt[end:]
prompt=prompt.rstrip()+'\nV40B ordinary补档已实际commit c1b331de6c46f2290f97eb803cda91d45c88d0f5，remote main及1405旧tags/peels核过，所有V40B archive/helper已consume。本轮V40C是同pending阶段下一次有限容量只读补档，新增saved receipt/reader/workorder/monitor/appreceipt走ordinary追加，不新record/tag、不重GPU/Task/旧once；later实际Git回执优先。'
put(B/'AUTOMATION_ACTUAL_SEVENTEENTH_CAPACITY_RECHECK_V40C_ARGS.json',dict(mode='update',id='mod4-10',kind='heartbeat',name=old['name'],prompt=prompt,rrule=old['rrule'],status=old['status'],targetThreadId=old['target_thread_id']))
s=(B/'archive_capacity_recheck_V40B_ordinary_supplement_V2_once.py').read_text('utf8')
s=s.replace('V40B_V2','V40C').replace('V40B','V40C')
s=s.replace('5dc566764b027eb886ee7fc97de7467eb25a903e','c1b331de6c46f2290f97eb803cda91d45c88d0f5')
s=s.replace('collect_pending_seventeenth_capacity_finite_once_RETURNED_ACTUAL.json','collect_pending_seventeenth_capacity_hourly_V2_once_RETURNED_ACTUAL.json')
s=s.replace('25709084672',str(v['durable']['free'])).replace('23.943450927734375',str(v['durable']['free']/1024**3)).replace('next_unused_V2_bound','next_unused_V3_bound')
old_block=" for x in json.loads((REPO/'history/evidence'/B.name/'REPORT_CAPTURE_INDEX.json').read_bytes())['entries']:\n  if x.get('source_SHA') and x.get('Git_path') and x.get('archived_SHA'):prior[x['source_SHA']]=dict(Git_path=x['Git_path'],archived_SHA=x['archived_SHA'])"
new_block=" for prior_index in sorted((REPO/'history/evidence'/B.name).rglob('REPORT_CAPTURE_INDEX.json')):\n  for x in json.loads(prior_index.read_bytes())['entries']:\n   if x.get('source_SHA') and x.get('Git_path') and x.get('archived_SHA'):prior[x['source_SHA']]=dict(Git_path=x['Git_path'],archived_SHA=x['archived_SHA'])"
assert old_block in s;s=s.replace(old_block,new_block);ast.parse(s)
with (B/'archive_capacity_recheck_V40C_ordinary_supplement_once.py').open('x',encoding='utf8',newline='\n') as f:f.write(s)
print(json.dumps(dict(unchanged_pending=True,free_GiB=v['durable']['free']/1024**3,V2_reader_consumed=True,V3_prepared_not_run=True,no_new_GO_or_charge=True)))
