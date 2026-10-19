"""Retain the one returned capacity snapshot and prepare one unused hourly successor."""
from pathlib import Path
import ast,hashlib,json,shutil,time,tomllib
B=Path(__file__).resolve().parent;R=B/'reports';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
receipt_path=R/'collect_pending_seventeenth_capacity_finite_once_RETURNED_ACTUAL.json'
v=json.loads(receipt_path.read_bytes());assert v['actual_finite_transport_returned'] and not v['ready_for_prepared_deployer_resource_checks']
assert v['durable']['free']==25709084672 and v['H1_explicit_sharing_retained']
assert not (R/'THREE_NEXT_HOUR_DEPLOY_STARTED_ACTUAL.json').exists()
next_reader=B/'collect_pending_seventeenth_capacity_hourly_V2_once.py';assert not next_reader.exists();shutil.copy2(B/'collect_pending_seventeenth_capacity_finite_once.py',next_reader);ast.parse(next_reader.read_text('utf8'))
work='NEXT_ACTUAL_SEVENTEENTH_CAPACITY_RECHECK_UNCHANGED_V40B_WORK_ORDER.json'
out=dict(epoch=time.time(),version='40B',returned_capacity_receipt=dict(path=str(receipt_path),bytes=receipt_path.stat().st_size,SHA=H(receipt_path),actual=v),capacity_still_below_original25GiB_guard=True,seventeenth_still_no_owner_worker_GO_PPO_or_charge=True,original_capacity_reader_consumed_after_real_return=True,next_unused_bounded_capacity_reader=dict(path=str(next_reader),bytes=next_reader.stat().st_size,SHA=H(next_reader)),no_dense_retry_or_second_watcher=True,no_GPU_Task_native_model_raw_hash_or_account_change=True,no_new_behavior_case_replay_or_player_change=True,previous_unique_pending_archive=dict(commit='5dc566764b027eb886ee7fc97de7467eb25a903e',tag_object='2ef9cec2114452fb750e4ebe2a9fd46dc118e62e',total_tags=1405,helper_record_tag_consumed=True),this_is_same_pending_stage_ordinary_supplement_not_new_trial=True)
put(B/work,out)
old=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert old['status']=='ACTIVE' and '最新actual V40覆盖V39旧376288 active' in old['prompt']
prompt=old['prompt'].replace('最新actual V40覆盖V39旧376288 active：','最新actual V40B覆盖V40首次prepared容量读者状态：')
prompt=prompt.replace('先读Q/NEXT_ACTUAL_SEVENTEENTH_PREPARED_DISK_CAPACITY_PENDING_V40_WORK_ORDER.json','先读Q/'+work+'及Q/NEXT_ACTUAL_SEVENTEENTH_PREPARED_DISK_CAPACITY_PENDING_V40_WORK_ORDER.json')
start=prompt.index('下一必要有限动作先fresh本机CIM');end=prompt.index('只有fresh容量ready',start)
paragraph=f'''本轮唯一容量读者Q/collect_pending_seventeenth_capacity_finite_once.py已经真实返回并consume；actual epoch={v['epoch']}，free仍{v['durable']['free']}bytes={v['durable']['free']/1024**3}GiB，ready=False，原私有/共享fcntl实际free、H1sharing原授权保留。RAM/GPUfree/compute均只属该receipt瞬时事实，不查peer身份，不冒本项目新训练或永久free。原started/returned全文见Q/reports/collect_pending_seventeenth_capacity_finite_once_STARTED_ACTUAL.json与RETURNED_ACTUAL.json，没有GPU/Task/native/旧PT/rawhash/账写入。
下一有意义容量变化或后续hourly只允许fresh本机CIM核无自己finite实际alive占transport后，执行新unused Q/{next_reader.name}一次，单72连接只读容量/RAM/原私有共享锁/GPUfree/compute，命令max60，不起第二watcher或5minpoll。原首次reader不能重run，V2一旦实际运行也consume；仍unready则保留receipt/pending静默，仅下一次有意义/human/h后新有界missing-capacity读者。原25GiB/GPU>7000MiB/RAM>8GiB/锁保护不降，H1允许human sharing、E3仍GPUempty。ready只代表72瞬时资源，原unused deployer还必须fresh复核210/72/canonical/旧owner实际out，不能拿任何snapshot永久hold或冒futureFINAL。
'''
prompt=prompt[:start]+paragraph+prompt[end:]
prompt=prompt.replace('本pending一旦record也consume；','本pending已实际unique5dc5667/tag2ef9cec/总1405远端main/tag/peel核过，原helper/record/tag均consume；')
prompt+='\n本轮V40B是同pending阶段的只读容量补档，新增saved reports/reader/monitor/appreceipt须ordinary追加Git，不重record/tag或制造新GPU阶段；远端回执优先。\n'
put(B/'AUTOMATION_ACTUAL_SEVENTEENTH_CAPACITY_RECHECK_V40B_ARGS.json',dict(mode='update',id='mod4-10',kind='heartbeat',name=old['name'],prompt=prompt,rrule=old['rrule'],status=old['status'],targetThreadId=old['target_thread_id']))
print(json.dumps(dict(unchanged_pending=True,free_GiB=v['durable']['free']/1024**3,reader_consumed=True,next_reader_prepared=True,no_new_GO_or_charge=True)))
