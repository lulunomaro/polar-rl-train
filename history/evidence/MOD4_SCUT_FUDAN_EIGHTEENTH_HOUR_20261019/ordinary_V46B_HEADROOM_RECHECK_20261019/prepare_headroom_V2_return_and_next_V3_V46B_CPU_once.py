"""Append the actual bounded V2 return and prepare only the next unused reader."""
from pathlib import Path
import ast,hashlib,json,time,tomllib
B=Path(__file__).resolve().parent;R=B/'reports'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 v=json.loads((R/'EIGHTEENTH_HOURLY_V2_RESOURCES_AND_EMPIRICAL_H1_HEADROOM_ACTUAL.json').read_bytes());assert v['actual_finite_transport_returned'] and not v['ready_for_unused_deployer_resource_checks'] and not v['checks']['H1_additional_empirical_free_at_least15669MiB'] and all(x for k,x in v['checks'].items() if k!='H1_additional_empirical_free_at_least15669MiB');assert not (R/'THREE_NEXT_HOUR_DEPLOY_STARTED_ACTUAL.json').exists()
 old=(B/'collect_eighteenth_pending_headroom_hourly_V2_once.py').read_bytes();new=old.replace(b'HOURLY_V2_',b'HOURLY_V3_');assert new.replace(b'HOURLY_V3_',b'HOURLY_V2_')==old;ast.parse(new)
 target=B/'collect_eighteenth_pending_headroom_hourly_V3_once.py'
 with target.open('xb') as f:f.write(new)
 actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert actual['status']=='ACTIVE'
 head='''最新actual V46B覆盖V46下一资源reader状态：人类直接说“继续”后，本轮唯一R/collect_eighteenth_pending_headroom_hourly_V2_once.py已真实返回并consume。actual epoch1792424961.6693141，H1free仍9683MiB未到15669MiB，E3free24203empty、RAM531194568704bytes、disk284176121856bytes、原private/shared锁free、新72两根仍不存在；这些只属该receipt快照，不冒永久free/alive。第十八仍无owner/worker/GO/PPO/费用，unused deployer/metadata未执行。没有GPU/Task/native/旧PT/rawhash/peer身份查询/账改写/重复清理。
 下一真正有意义资源变化或后续hourly先fresh本机CIM核无自己finite实际alive占transport，才仅执行新unused R/collect_eighteenth_pending_headroom_hourly_V3_once.py一次，单72命令max60；远端READ与V2字节相同，仅本机START/RETURNED/ERROR名称变化。V2与旧readerconsume，不能重run，V3实际执行也consume；unready保留receipt静默，不5minpoll/第二watcher/并发SSH，下一有意义/hourly才新unused bounded缺项reader。原H1sharing与额外至少15669MiB、原>7000/RAM/disk/锁/savedstop保持；fresh ready才按R现有unused deployer fresh复核原413504闭合/canonical/out/资源/unusedroot再派发一次，不绕过门槛或因卡闲另造writer。
 第十八partial-closed/headroom-pending stage已实际unique61d55f1bff0957dbf0caf46fd97ac7e65d3739ee/tagobject7425d714525412f1e02421363b710d596e075598/总1408，remote main/tag/peeled及全部原1407tag对象核过；原record/helper/tag均consume，不重record/重tag。本V46B仅同pending阶段只读补档，新增saved report/reader/工作单monitor/appreceipt用ordinary追加Git，不制造新GPU阶段；later实际Git回执优先。跨午夜只采用真实新记录日期，不回填历史；尚未真正第十八派发/三PPO，不生成绑定虚构owner的closing或第十九active模板。以下V46为完整来源/费用/协议和历史快照，本条V2actual返回与nextV3优先。
 '''
 args=dict(mode='update',id='mod4-10',kind='heartbeat',name=actual['name'],prompt=(head+actual['prompt']).rstrip(),rrule=actual['rrule'],status=actual['status'],targetThreadId=actual['target_thread_id'])
 put(B/'AUTOMATION_HEADROOM_V2_RETURN_NEXT_V3_V46B_ARGS.json',args)
 proof=dict(epoch=time.time(),human_latest='继续',V2_actual_finite_returned_and_consumed=True,actual_resources=v,next_unused_reader=dict(path=str(target),bytes=len(new),SHA=hashlib.sha256(new).hexdigest(),only_receipt_names_changed_remote_READ_exact=True),eighteenth_actual_owner=None,eighteenth_actual_GO={},eighteenth_actual_charge0=True,unused_deployer_and_metadata_still_unused=True,same_pending_stage_no_new_GPU_trial=True,ordinary_Git_append_required=True)
 put(R/'HEADROOM_V2_RETURN_NEXT_V3_V46B_CPU_ACTUAL.json',proof)
 put(B/'NEXT_ACTUAL_EIGHTEENTH_HEADROOM_V2_RETURNED_NEXT_V3_V46B_WORK_ORDER.json',dict(epoch=time.time(),instructions=head,proof=str(R/'HEADROOM_V2_RETURN_NEXT_V3_V46B_CPU_ACTUAL.json')))
 print(json.dumps(dict(V2_actual_returned_pending_unchanged=True,next_V3_prepared_unused=True,no_deployer_GPU_or_account_action=True)))
if __name__=='__main__':main()
