"""Freeze unused orchestration/proof sources; never calls transport or CPU entry."""
from pathlib import Path
import json,hashlib,datetime
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
 with (D/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False)
cpu=json.loads((D/'INSTALL_ACTIVATE_CPU_PROOF_SOURCE_REVIEW_V1_ACTUAL.json').read_bytes());assert cpu['passed']
OLD=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026'
inputs=[OLD/name for name in ['activate_three_gpu86B_sole72_owner_after_actual_CPU_unused_once.py',
 'install_native86B_CPU_path_fixed_actual72_SDK_unused_once.py','install_normal86B_H1_E3_typed_sources_actual_SDK_CPU_unused_once.py']]+[
 L/'agent_three_H1_native87_sole72_protocol_candidate/native87_closed_source_CPU_v1.py',
 L/'agent_native87_worker_and_target_CPU_entry_candidate/native87_protocol_v1.py']
put('SOURCE_LINEAGE_AND_DISCOVERY_ERRORS_ACTUAL.json',dict(inputs=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in inputs],
    preserved_reader_errors=[dict(path=str(OLD/'install_three_gpu86B_source_and_actual_CPU_unused_once.py'),
        correction='Guessed combined installer did not exist; reused actual native and normal installer templates separately.')],
    protocol_correction=dict(old_dispatcher_would_repeat_actual_CPU_at_node_start=True,
        new_same_basename_dispatcher_uses_external_exact_preinstalled_proof=True,old_frozen_source_unchanged=True),
    no_actual_host_model_install_Task_GO_fee_or_Git=True,no_failed_CPU_test=True))
put('INSTALL_ACTIVATE_SOURCE_BINDER_INTERFACE_ACTUAL.json',dict(
    status='unused_source_candidate_review_required',
    entries=[dict(name=name,SHA=H(D/name)) for name in
        ['install_three_H1_native87_source_sdk_CPU_finite_unused_once.py','activate_three_H1_native87_sole72_after_actual_CPU_unused_once.py']],
    supporting_local_module='native87_install_activate_support_v1.py',
    dispatcher_replacement=dict(name='native87_closed_source_CPU_v1.py',SHA=H(D/'native87_closed_source_CPU_v1.py'),
        copy_to_new_N_controllers_and_each_payload=True,rebind_manifest_approved_python_candidate_pins=True,old_frozen_versions_unchanged=True),
    prepared_report='N/reports/THREE_H1_NATIVE87_LOCAL_BOUND_SOURCE_PREPARED_ACTUAL.json',
    prepared_required_fields=['passed','specs','payloads','roots','owner_root','owner_script','sources'],
    prepared_payloads='each role value localpath string or {payload:localpath}',
    prepared_sources='each role {path:qualified original source path,bytes,SHA}; all normalH1 update138 bootstrap',
    source_execution_order=['210 h1 copy/fullSHA/oneCPU','72 currentC+e2 copy/fullSHA/oneCPU','72 currentC+recovery copy/fullSHA/oneCPU'],
    CPU_summary='N/reports/THREE_H1_NATIVE87_TARGET_SOURCE_SDK_CPU_RETURNED_ACTUAL.json',
    CPU_summary_fields=['passed','actual_finite_returned','results[key].ready_envelope','results[key].preinstalled_CPU_proof_SHA',
        'results[key].preinstalled_CPU_proof','specs_with_preinstalled_CPU_proof','prepared_source_report_SHA'],
    proof=dict(relative='job0/NATIVE87_PREINSTALLED_CPU_PROOF_ACTUAL.json',immutable_open_x=True,
        fresh_actual_only=True,external_spec_pin='preinstalled_CPU_proof_SHA',
        fields=['schema','not_synthetic','actual_CPU_waited_EXIT0','returncode','manifest_SHA','script_relative','script_SHA',
          'source_SHA','report_relative','report_SHA','ready_envelope','actual_identity(pid/exe/argv/creation/root)',
          'started_epoch','waited_epoch','started_receipt_SHA','waited_receipt_SHA'],
        cache_rule='Only explicit spec proofSHA branch, exact current manifest/code/report/STARTED/WAITED + valid_ready; no target script execution or model load',
        no_proof_rule='Fresh once only, refuse existing report/proof/log namespace rearm'),
    activation=dict(require_all3_actual_CPU=True,require_external_proof_pinned_specs=True,
        revalidate_proof_cache_without_CPU_execution_before_owner=True,all_current10_controller_files_copied=True,
        one_sole72_owner_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_fudan_native_2610v87/owner',
        owner_identity_root_is_cwd_not_owner_file_root=True,output_report='THREE_H1_NATIVE87_ACTUAL_OWNER_NODES_DETACHED.json',
        output_fields=['run_id','owner_root','owner_identity','owner','nodes','roots','specs','sources','payloads','sole72authority','no_secret']),
    original_guards=dict(sole72_remaining_snapshot=577055.9868602753,strict_finite_limit=86412.86069250107,
        GPU_empty_free_MiB_strictly_greater=15669,RAM_available_bytes_strictly_greater=32*1024**3,
        postpayload_disk_bytes_strictly_greater=25*1024**3,NTFS_UUID='EF3105C85DD986BD',rw_fresh_required=True,
        original_two_owner_locks_private_shared_free_required=True,previous86_allout_cost_proof_independent=True,
        original_owner_fee_and3900_3600_300_source_unchanged=True,no_retired210_canonical_IO_or_copy=True),
    secrets='original recover/session memory; deploy launch stdin; never new secret argv/disk/report. token/spec private fields cleared after launch.',
    actual_GPU_precontrol_passed=False,actual_install_CPU_activation_executed=False,
    local_source_CPU=dict(passed_count=cpu['passed_count'],total=cpu['total']),
    pending=['Root copy source scripts/support into final staging or execute at current fixed-N path',
        'Root bind new dispatcher SHA in controllers/payload manifest/source contract/spec candidate pins',
        'Root fill actual prepared q/spec/source/owner paths, validate source model inventory and protocol CPU kind',
        'Root add exact two new entry basenames to its transport allowlist and review before execution',
        'Actual target CPU/immutable proofs/current host resource/allout checks; not yet performed',
        'Actual signedGO and worker fresh4096/DR/order/solver before firstcontrol/Pi remain distinct']))
handoff='''未执行安装/激活脚本已冻结；本机25/25 source/metadata检查通过。没有网络、模型、Task/GO、fee或Git操作。

两个入口：install_three_H1_native87_source_sdk_CPU_finite_unused_once.py 与 activate_three_H1_native87_sole72_after_actual_CPU_unused_once.py；共享native87_install_activate_support_v1.py。N固定到新V87 namespace，准备报告/根路径接口见INSTALL_ACTIVATE_SOURCE_BINDER_INTERFACE_ACTUAL.json。root须把两个basename加入唯一finite transport allowlist并审核后才执行。

安装严格串行210 h1→72 e2→72 recovery。只用新ownroot和原前86 runtime，在原manifest字节一致时copy；新qualified H1 bootstrap可在210 old正式final本机copy，72需从root localpayload上传。每路fullmanifest/stat/SHA后只调用CPUdispatcher一次，dispatcher唯一启动actualtargetCPU并等待EXIT0，绝不runpy再load双执行。未知peer不操作；所有卡empty>15669MiB、RAM>32GiB、payload后disk>25GiB、210真实NTFS UUID/rw、private/sharedfree、previous86 allout/cost独立于H1source；72现有C仍None/finite严格86412.86069250107及577055.9868602753 snapshot，不复制canonical或IO退休210账本。

关键新修复是native87_closed_source_CPU_v1.py同名新版本。旧冻结dispatcher没有cache，会令node重复CPU/read与open-x失败。新fresh分支唯一执行actualCPU，保存actualpid/exe/argv/create/root与真实STARTED/WAITED receipts，退出0且新版valid_ready通过后open-x写immutable proof，绑定report/manifest/script/sourceSHA和not_synthetic。安装回执把proofSHA放在root侧specs_with_preinstalled_CPU_proof作为外部pin。activation必须消费这组specs，不能仅凭文件exists；预激活和node.load都用proofpin精确复核当前manifest/code/report/identity/waited证据，不再启动模型CPU。无proof分支才准fresh一次，已有失败报告/namespace不重arm。Python inventory仍完整exact；proof是明确运行期JSON，不放开任何Python。

root必须在新controllers和三个新payload中替换该dispatcher、更新manifest/candidate/approved_python pins；旧目录完全不改。activation复制完整当前10个controller文件，包含native87 protocol/CPUdispatcher/node/resource，三CPU实际全部pass和当前资源/C/锁检查后才创建独立owner_root、启动唯一72 owner与三node。owner_identity.root是cwd，报告另存owner_root。owner/charge/authority/两锁/3900/3600/300和strict210->72 borrowedHTTP/deps325代码没有修改。原凭据recover/sessionmemory/launch stdin沿用，token/SSH password不入报告/新argv/磁盘。

25项只编译本机和remote代码并验证synthetic proof正负metadata，不产生实际proof、ready、SDK或GPU成功。真实targetCPU、copy、host资源、全3实际source admission、owner/node/GO与worker GPU_PRECONTROL都pending。helper完整保存读者错误及旧dispatcher重复执行问题，普通补档由root负责。
'''
with (D/'FROZEN_INSTALL_ACTIVATE_CPU_PROOF_HANDOFF.md').open('x',encoding='utf8') as f:f.write(handoff)
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
rows=[dict(path=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='FROZEN_INSTALL_ACTIVATE_CPU_PROOF_SHA_INDEX.json']
put('FROZEN_INSTALL_ACTIVATE_CPU_PROOF_SHA_INDEX.json',dict(frozen_at_UTC=stamp,count_excluding_index=len(rows),files_excluding_this_index=rows,
    source_only=True,no_actual_install_CPU_activation=True,old_directories_untouched=True,parent_archive_pending=True))
print(json.dumps(dict(frozen_at_UTC=stamp,count_excluding_index=len(rows),dispatcher_SHA=H(D/'native87_closed_source_CPU_v1.py'),
    installer_SHA=H(D/'install_three_H1_native87_source_sdk_CPU_finite_unused_once.py'),activation_SHA=H(D/'activate_three_H1_native87_sole72_after_actual_CPU_unused_once.py'),
    index_SHA=H(D/'FROZEN_INSTALL_ACTIVATE_CPU_PROOF_SHA_INDEX.json'))))
