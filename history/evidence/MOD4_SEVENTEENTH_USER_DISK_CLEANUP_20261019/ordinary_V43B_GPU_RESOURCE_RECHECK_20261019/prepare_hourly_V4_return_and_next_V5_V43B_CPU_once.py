"""Local append-only handoff after the single hourly V4 resource reader actually returned."""
from pathlib import Path
import ast,hashlib,json,time,tomllib
B=Path(__file__).resolve().parent;R=B/'reports'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 receipt=json.loads((R/'HOURLY_V4_RESOURCE_AND_UNUSED_ROOTS_ACTUAL.json').read_bytes());assert receipt['actual_finite_transport_returned'] and not receipt['ready_for_unused_deployer_resource_checks'] and not receipt['checks']['H1_original_GPU_free_over7000MiB'] and all(v for k,v in receipt['checks'].items() if k!='H1_original_GPU_free_over7000MiB')
 raw=(B/'collect_pending_seventeenth_resources_hourly_V4_once.py').read_bytes();v5=raw.replace(b'HOURLY_V4_',b'HOURLY_V5_');assert v5.replace(b'HOURLY_V5_',b'HOURLY_V4_')==raw;ast.parse(v5)
 target=B/'collect_pending_seventeenth_resources_hourly_V5_once.py'
 with target.open('xb') as f:f.write(v5)
 old=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 head='''最新actual V43B覆盖V43下一reader状态：本轮唯一S/collect_pending_seventeenth_resources_hourly_V4_once.py已经实际返回并consume。新actual epoch1792412892.0877256，H1free1149MiB仍未超过原7000MiB，E3free24203MiB且empty，RAM528932184064bytes、disk284819779584bytes、原private/sharedfcntl均free、新target72两根仍不存在；所有是该receipt瞬时事实，不冒永久free/alive。第十七仍没有owner/worker/GO/PPO/费用，没有运行unused V2deployer或metadata collector；没有GPU/Task/模型hash/peer身份查询/账写入/重复清理。原receipt完整保存在S/reports/HOURLY_V4_RESOURCE_READER_STARTED_ACTUAL.json及HOURLY_V4_RESOURCE_AND_UNUSED_ROOTS_ACTUAL.json。
 下一真正有意义资源变化或后续hourly先fresh本机CIM，再仅运行新unused S/collect_pending_seventeenth_resources_hourly_V5_once.py一次；单72命令max60，远端READ与V4字节相同，只更换本机START/RETURNED/ERROR名。V4和所有更早reader不能重run，V5实际运行也consume；unready保存receipt并静默，不5minpoll/第二watcher/并发SSH。fresh ready且原unused root/out/canonical复核通过才用原unused V2deployer一次，H1共享授权保留，原>7000MiB/>25GiB/>8GiB和锁门槛不降。若下次仍pending只准备新的bounded缺项reader，不能热改/重复Task或独立E2-onlywriter。
 清理stage已实际unique d9a54a06d65b090aa7ee6b02d355106ac56f0853/tagobject b09a8e4fe2ee32b6c803157a64e52d6964c665fd/总1406，remote main/tag/peeled及全部原1405tag对象核过；原record/helper/tag已consume，不能重record或重标签。本V43B只是同一pending阶段只读容量/显存补档，新reader/source/reports/工作单monitor/appreceipt用ordinary追加Git，不造新GPU阶段。旧首次archive builder本机tagcount串替换被CPU guard拒、V2修正后才归档的source/error全部已保留，不冒GPU/网络故障。以下V43是完整授权/合同与历史快照；本条ownactual与nextV5优先。
 '''
 args=dict(mode='update',id='mod4-10',kind='heartbeat',name=old['name'],prompt=(head+old['prompt']).rstrip(),rrule=old['rrule'],status=old['status'],targetThreadId=old['target_thread_id'])
 put(B/'AUTOMATION_HOURLY_V4_RETURN_NEXT_V5_V43B_ARGS.json',args)
 proof=dict(epoch=time.time(),V4_actual_finite_returned_and_consumed=True,resource_snapshot=receipt,next_unused_reader=dict(path=str(target),bytes=len(v5),SHA=hashlib.sha256(v5).hexdigest(),only_receipt_names_changed_remote_READ_exact=True),seventeenth_actual_owner=None,seventeenth_actual_GO={},same_pending_no_new_GPU_trial=True,unique_cleanup_stage_already_recorded='d9a54a06d65b090aa7ee6b02d355106ac56f0853',ordinary_append_only=True,no_new_training_or_account_or_deletion_action=True)
 put(R/'HOURLY_V4_RETURN_AND_NEXT_V5_HANDOFF_V43B_CPU_ACTUAL.json',proof)
 put(B/'NEXT_ACTUAL_SEVENTEENTH_GPU_PENDING_V4_RETURNED_NEXT_V5_V43B_WORK_ORDER.json',dict(epoch=time.time(),instructions=head,proof=str(R/'HOURLY_V4_RETURN_AND_NEXT_V5_HANDOFF_V43B_CPU_ACTUAL.json')))
 print(json.dumps(dict(next_V5_prepared_unused=True,V4_returned_pending_unchanged=True,ordinary_append_required=True)))
if __name__=='__main__':main()
