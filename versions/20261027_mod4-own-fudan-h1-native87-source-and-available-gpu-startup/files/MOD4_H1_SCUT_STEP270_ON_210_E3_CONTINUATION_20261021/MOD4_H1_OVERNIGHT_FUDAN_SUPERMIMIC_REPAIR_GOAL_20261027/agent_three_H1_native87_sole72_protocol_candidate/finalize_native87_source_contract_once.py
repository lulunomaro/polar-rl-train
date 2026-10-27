"""Final independent AST checks and source contract freeze; no install/Task/GO."""
from pathlib import Path
import json,ast,hashlib,datetime
import native87_protocol_v1 as p
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent
OLD=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/controllers_v2'
OUT=D/'controllers_v2'
H=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
def put(name,v):
    with (D/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False)
class StripNative87(ast.NodeTransformer):
    def visit_If(self,node):
        self.generic_visit(node)
        if isinstance(node.test,ast.Call) and node.test.args and isinstance(node.test.args[0],ast.Constant) and node.test.args[0].value=='native87_policy_only':
            return node.orelse
        return node
class OriginalRAM(ast.NodeTransformer):
    def visit_IfExp(self,node):
        self.generic_visit(node)
        if isinstance(node.test,ast.Call) and node.test.args and isinstance(node.test.args[0],ast.Constant) and node.test.args[0].value=='native87_policy_only' and isinstance(node.body,ast.Constant) and node.body.value==32:
            return node.orelse
        return node
node_new=StripNative87().visit(ast.parse((OUT/'three_slot_finite_node_v1.py').read_text()))
node_old=ast.parse((OLD/'three_slot_finite_node_v1.py').read_text())
assert ast.dump(node_new,include_attributes=False)==ast.dump(node_old,include_attributes=False)
rnew=OriginalRAM().visit(ast.parse((OUT/'three_real_gpu_resource_v1.py').read_text()))
rold=ast.parse((OLD/'three_real_gpu_resource_v1.py').read_text())
assert ast.dump(rnew,include_attributes=False)==ast.dump(rold,include_attributes=False)
assert (OUT/'native87_protocol_v1.py').read_bytes()==(D/'native87_protocol_v1.py').read_bytes()
assert (OUT/'native87_closed_source_CPU_v1.py').read_bytes()==(D/'native87_closed_source_CPU_v1.py').read_bytes()
put('FINAL_NATIVE87_CONTROLLER_AST_AND_COPY_CPU_V2_ACTUAL.json',dict(passed=True,
    original_node_AST_exact_after_removing_only_native87_dispatch=True,
    original_resource_AST_exact_after_normalizing_only_native87_RAM32GiB_conditional=True,
    current_protocol_and_dispatcher_byteexact_in_final_controllers=True,
    first_controllers_and_report_preserved=True,
    actual_installed_SDK_CPU_passed=False,no_actual_node_owner_fee_Task_GO_or_network_executed=True))
N=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026'
inputs=[N/'reports/THREE_GPU86B_HEALTHY_H1_CPU_INITIAL_LOAD_ACTUAL.json',
    N/'reports/THREE_GPU86B_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json',
    N/'reports/THREE_GPU86B_CLOSED_AUTHORITY72_ORIGINAL_COST_ACTUAL.json',
    L/'root_augmented_world_model_candidate/v4/supermimic_wheel_leg_v3/replay.py']+[OLD/f for f in
    ['three_slot_common_v1.py','three_slot_finite_node_v1.py','three_slot_finite_owner_V86_authority72.py','three_real_gpu_resource_v1.py','forwarded_original_owner_control_v1.py','single_writer72_authority_V85M_source.py']]
put('SOURCE_LINEAGE_ERRORS_AND_PENDING_ACTUAL.json',dict(inputs=[dict(path=str(q),bytes=q.stat().st_size,SHA=H(q)) for q in inputs],
    reader_errors=[dict(kind='incorrect_protocol_location',path=str(N/'mixed86_protocol_v1.py'),resolution='Actual source is controllers_v2/mixed86_protocol_v1.py; original lookup error preserved here.')],
    source_review_corrections=[dict(kind='controller_snapshot_not_final',detail='First source generation predated explicit TGS position32/velocity4 protocol field addition. First controllers retained; final controllers_v2 carries current exact protocol, with copy test.'),
        dict(kind='semantic_flag_correction_before_execution',detail='Use new node dispatch and closed_production_continuation=False; no misleading legacy flag used.')],
    no_failed_CPU_test=True,no_model_bytes_read_hashed_or_copied=True,no_canonical_or_fee_execution=True))
put('NATIVE87_TYPED_SOURCE_OWNER_WORKER_INSTALLER_HANDOFF_CONTRACT.json',dict(
    status='source_candidate_only_actual_hooks_pending',kind=p.KIND,final_controller_dir=str(OUT),
    source_SHA=p.SOURCE_SHA,bootstrap_source_SHA=p.SOURCE_SHA,bootstrap_update=138,bootstrap_Adam=832460,
    source_kind='closed_production_policy_only',native86_retained_baseline_not_exact_continuation=True,
    roles_all_H1_native_same_method=True,seeds=p.SEEDS,GPUs=p.GPUS,method_config=p.METHOD,
    physical_contract=dict(physics_us=2500,control_us=10000,solver='TGS',position_iterations=32,velocity_iterations=4,clip6=True,original_success_unchanged=True),
    scope=dict(closed_production_continuation=False,native_continuation=False,native87_policy_only=True,
        new_native_architecture_fresh=True,fresh_environment_resume_scope='policy_only_no_source_environment_state',
        source20k_environment_or_DR_reshape_forbidden=True),
    worker=dict(root_native_entry='source/native_own_fudan87_training.py',API='run(runner,n,log_dir,B,J,out,task,go,src,phase)',
        wholepolicy_loader='original runner.load normal H1 source; root implements explicit policy_only_fresh4096_bootstrap resume helper',
        original_save_chain='install_step270_save_contract writes actual fresh4096 D0-D7 allstate; never old20k reshape',
        argv=['--slot','ROLE','--phase','production','--num-envs','4096','--seed','27|28|29','--source-scope','policy_only_fresh_environment'],
        GO_path='J/GO_PRODUCTION.json for all3 roles; original h1 node also writes B/GO_PRODUCTION.json historical duplicate',
        actual_worker_and_target_CPU_source_binder='pending root files exact SHA; no placeholder pass'),
    resources=dict(replay_transition_bytes=1205,replay_bytes=p.REPLAY_BYTES,replay_GiB=p.REPLAY_BYTES/1024**3,
        observation_history_bytes=4096*10*86*4,minimum_available_RAM_bytes=p.MIN_RAM_BYTES,
        GPU_empty_free_MiB_strictly_greater=15669,payload_free_disk_bytes=p.MIN_PAYLOAD_DISK_BYTES,
        fullsave_min_free_disk_bytes=p.MIN_SAVE_DISK_BYTES,
        estimate_note='Replay is device-resident. This estimate excludes physics/BPTT/optimizer allocator peaks; actual target VRAM peak admission remains pending.'),
    owner=dict(sole72_canonical=p.CANONICAL,authority_generation=p.AUTHORITY_GENERATION,
        closed86_balance_snapshot_only=577055.9868602753,strict_original_finite_threshold=86412.86069250107,
        caps=dict(parent=3900,save_deadline=3600,exit_headroom=300),charge_values_AST_exact=True,
        original_two_locks_authority_and_forwarder_unchanged=True,old210_authority_retired=True,
        previous86_all3_closure_distinct_from_new_H1_source=True),
    exact_replacements=['three_slot_common_v1.py','three_slot_finite_node_v1.py','three_slot_finite_owner_V86_authority72.py','three_real_gpu_resource_v1.py'],
    exact_additions=['native87_protocol_v1.py','native87_closed_source_CPU_v1.py'],
    no_actual_Task_GO_installer_or_fee_created=True,
    fresh_actual_required=list(p.READY_FLAGS),
    pending=['Root worker/SDK CPU source hooks and exact source inventory pins',
        'Fresh actual source wholepolicy/RSL/17Adam832460 + native fresh architecture verification',
        'Actual4096/5s D0-D7 reset/source30jointorder and new fullsave/retention protection',
        'Actual perGPU empty/RAM/durable/VRAM allocation and training-resource admission',
        'Manifest/sourceauth binds three H1 normal bootstrap source and independent previous86 allout/cost proof',
        'No paper speed reproduction claim: batch1024/WM-only64 differ from upstream500/G1batch4096 under finite3900s window']))
handoff='''源码协议候选已冻结；没有Task/GO、实际安装、模型读取/复制/hash、owner/node启动、fee或Git操作。

最终controller使用controllers_v2/。CONTROLLER_EXACT_REPLACEMENT_PINS_V2_ACTUAL.json逐文件列oldSHA->newSHA和唯一新增文件。原第一轮controllers/与pins/CPU报告保留，不能误用其早期METHOD快照。35/35 metadata/sourceCPU通过；新增最终AST检查证明node仅native87 dispatch分支差异，resource仅native87 RAM32GiB差异，最终protocol/dispatcher copy字节一致。charge_values与owner.account AST exact；authority/finite86412.86069250107/两锁/forwarder原字节不改，既有strict210->72 pinned borrowedHTTP/deps325路径保留，未连接任何host。

真实语义：三逻辑slot h1/e2/recovery都是同一新H1-native-v3修复方法，种子27/28/29；全用最新qualified正常H1 closed86 update138/Adam832460/SHA0c1e...d394作冻结policy-only source。closed_production_continuation=False、native_continuation=False；node有精确native87 dispatcher入口，未借旧flag。source20k DR/RNG/environment/replay/phase状态不可reshape成4096。新native网络/3optimizers fresh，不能称Native86 exact continuation。旧Native86仅保留比较baseline。

METHOD：每卡4096，timeout5s/500controls，原2.5ms/TGS32/4/decimation4/100Hz/clip6/D0-D7/成功条件不变；packed127/aux54/xi31/obs86/goal146xfuture10/hist10；WM2048x3/Pi2048,1024,512,256/H32/replay1000/UTD.4/batch1024/WM-only64/FP32 compilefalse。replay精确1205B/transition，4,935,680,000B=4.597GiB/device，未计物理/BPTT/allocator峰。RAM门槛32GiB，GPU empty>15669MiB、payload25GiB、fullsave8GiB。实际VRAM/SDK/保存仍pending；不把参数值当硬件已准入。

ready kind MOD4_H1_NATIVE87_POLICY_ONLY_FRESH4096_SOURCE_SDK_CPU。native87_valid_ready精确绑定source/seed/roleGPU/backend/method/config/pins/qualified138报告/previous86closure/reference/objective，并要求真实wholepolicy/RSL actor9+critic8+STD17Adam832460、新4096与fresh D0-D7/reset/actual30jointorder/providerfuture10/sourceinventory等全部flag。测试正例是synthetic metadata，外层明确actual_installed_SDK_CPU_passed=False，绝无实际ready。

native87_closed_source_CPU_v1.load会在未来执行root提供的exact-pinned CPUentry，等待EXIT0再验证实际报告；没有旧20k sourceguard fallback。worker CLI --slot ROLE --phase production --num-envs4096 --seed SEED --source-scope policy_only_fresh_environment。三role统一读取J/GO_PRODUCTION.json；旧h1node额外B/GO文件仍保留。Root source/native_own_fudan87_training.py run(...)接原runner.load和新的policy_only_fresh4096_bootstrap，以及原install_step270_save_contract。实际newworker/CPUentry尚由root提供并做source binder，本任务只交明确workerplan和installer hooks，不伪造安装成功。

native87_installer_plan_v1.py只验证exactfile inventory与approved Python清单、pathcontainment和pending hook集合，完全不写payload或Task；实际installer/resource动作由root后续负责。上轮86原all3cost/allout/sole72余额snapshot与新H1 bootstrap来源独立，原charge按真实GO到terminal原公式，无refund/clamp/secondwriter。报告与source reader错误全部保留，普通补档由root执行。
'''
with (D/'FROZEN_NATIVE87_PROTOCOL_HANDOFF.md').open('x',encoding='utf8') as f:f.write(handoff)
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
rows=[dict(path=q.relative_to(D).as_posix(),bytes=q.stat().st_size,SHA=H(q)) for q in sorted(D.rglob('*')) if q.is_file() and q.name!='FROZEN_NATIVE87_PROTOCOL_SHA_INDEX.json']
put('FROZEN_NATIVE87_PROTOCOL_SHA_INDEX.json',dict(frozen_at_UTC=stamp,count_excluding_index=len(rows),files_excluding_this_index=rows,
    source_CPU_only=True,actual_Task_GO_installer_SDK_fee=False,old_directories_untouched=True,parent_archive_pending=True))
print(json.dumps(dict(frozen_at_UTC=stamp,count_excluding_index=len(rows),index_SHA=H(D/'FROZEN_NATIVE87_PROTOCOL_SHA_INDEX.json'))))
