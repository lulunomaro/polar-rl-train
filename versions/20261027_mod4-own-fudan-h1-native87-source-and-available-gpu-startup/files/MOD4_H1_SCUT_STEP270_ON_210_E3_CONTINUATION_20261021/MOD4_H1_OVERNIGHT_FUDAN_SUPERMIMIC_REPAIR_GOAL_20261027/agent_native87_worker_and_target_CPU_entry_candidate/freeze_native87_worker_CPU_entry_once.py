"""Freeze source candidate and existing CPU result; never invokes target entry."""
from pathlib import Path
import ast,json,hashlib,datetime
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,v):
    with (D/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False)
cpu=json.loads((D/'NATIVE87_WORKER_SOURCE_AND_NEW_TINY_API_CPU_V1_ACTUAL.json').read_bytes());assert cpu['passed']
for q in D.glob('*.py'):ast.parse(q.read_text('utf8'))
worker=D/'h1_native_own87_worker_v1.py';target=D/'target_native87_source_sdk_cpu_v1.py';protocol=D/'native87_protocol_v1.py'
inputs=[L/'root_native_bridge_integration_candidate'/name for name in
    ['native_own_fudan87_training.py','fresh_policy_only_bootstrap87_v1.py','converted_MOD4_jump_mdp_v4.py','native_wheel_leg_bridge_v4.py','native_finalization_own_v3.py',
     'MOD4_OWN_CONVERTED_FUDAN_JUMP_REFERENCE_V1_NOT_ADMITTED.json']]+[
    L/'root_augmented_world_model_candidate/v5/supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py',
    L/'root_compact_static_context_candidate/compact_episode_static31_v1.py',
    L/'agent_actual_DR_memory_getter_candidate_v1/actual_DR_memory_getter_v1.py',
    L/'agent_static_dynamic_delay_contract_candidate/static_dynamic_delay_contract_v1.py',
    T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2/target_native86_source_sdk_cpu_review_v1.py']
put('SOURCE_INPUTS_ERRORS_AND_SCOPE_CORRECTIONS_ACTUAL.json',dict(inputs=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in inputs],
    reader_errors=[dict(path='payloads/e2/source/native86_closed_source_CPU_v1.py',correction='Actual previous dispatcher is payloadroot/native86_closed_source_CPU_v1.py'),
        dict(path='payloads/e2/native86_target_source_SDK_CPU_v1.py',correction='Actual previous CPU template is target_native86_source_sdk_cpu_review_v1.py'),
        dict(path='root_augmented_world_model_candidate/test_augmented_WM_finite_CPU_unused_once.py',correction='Missing guessed test name; no old fixture executed.'),
        dict(path='root_native_bridge_integration_candidate/native_own_fudan87_training.py',correction='Not yet present on first lookup; root then supplied source; imported only for config/API in the new tiny fixture.')],
    corrections=[dict(kind='Task field name',detail='Initial worker expected seed; root interface specified native_seed. First worker text is preserved; final worker uses native_seed, no worker was executed.'),
        dict(kind='preGO_CPU_vs_GPU_admission',detail='Old ready requirement for actual4096/order/DR GPU replaced in new protocol copy with source/configured/expected facts, actual_environment_count=None and actual_GPU readback False. Actual precontrol remains mandatory.'),
        dict(kind='native network initialisation scope',detail='PreGO flags renamed to new_native_architecture_source_API_CPU_passed/new_native_optimizer_scope_source_CPU_passed; tiny fixture is not full runtime initialization.')],
    no_failed_CPU_test=True,no_actual_model_or_target_entry_execution=True))
put('NATIVE87_WORKER_TARGET_CPU_BINDER_INTERFACE_ACTUAL.json',dict(
    source_only=True,worker=dict(name=worker.name,SHA=H(worker)),target_CPU=dict(name=target.name,SHA=H(target)),
    protocol_replacement=dict(name='native87_protocol_v1.py',SHA=H(protocol),
        kind='MOD4_H1_NATIVE87_POLICY_ONLY_SOURCE_SDK_CPU_PRECONTROL_V2',replace_only_in_new_payload_and_owner_root=True,old_frozen_controller_dir_unchanged=True),
    worker_CLI=['--slot','h1|e2|recovery','--phase','production','--num-envs','4096','--seed','27|28|29','--source-scope','policy_only_fresh_environment'],
    CPU_CLI=['--slot','ROLE','--num-envs','4096','--seed','SEED','--source-scope','policy_only_fresh_environment'],
    Task_required=['key','kind','native_seed','source_SHA','bootstrap_source_SHA','source_filename','source_Adamstep','source_normal_PPO_update',
        'bootstrap_source_kind','fresh_environment_resume_scope','method_config','native87_contract_SHA','GPU_UUID','execution_backend',
        'native_reference_relative','native_reference_SHA','qualified_H1_report_SHA','previous86_closure_SHA','reference_artifact_SHA','objective_contract_SHA'],
    GO_read='J/GO_PRODUCTION.json all3 roles',
    contract_file='NATIVE87_SOURCE_CONTRACT_ACTUAL.json',
    contract_required=dict(schema='mod4.native87.policy_only_fresh4096.source_contract.v1',
        fields=['source_SHA','source_Adamstep','method_config','approved_python','original_runtime_pins','candidate_pins',
          'expected_runtime_joint_names','expected_leg_joint_names','expected_installed_versions','qualified_H1_report_relative',
          'previous86_typed_close_relative','previous86_authority_close_relative']),
    inventory='full THREE_SLOT_COMPLETE_MANIFEST_V1.json; each contained regular file bytes/SHA; every actual *.py exactly in approved_python, no blanket exception',
    no_manifest_hash_cycle='Task contains contractSHA, manifest contains Task+contract; GO/spec carries manifestSHA. Contract must not contain its own SHA or manifestSHA.',
    CPU_scope=dict(actual_source_model_load_count=1,whole_finite_actor9_critic8_STD6_17Adam832460=True,
        actual_RSL_strict_load_roundtrip=True,actual_installed_SDK_RSL_source_versions_pinned=True,
        original_RewardManager_boundary_sampling_CPU=True,tiny_API_fixture_only=True,
        configured_environment_count=4096,actual_environment_count=None,actual_GPU_runtime_readback_passed=False,actual_GPU_fresh4096_DR_readback_passed=False),
    actual_precontrol=dict(required=True,checks=['fresh4096 clock0/age0/5s/seed','actual runtime30 ordered names','actual31 body count',
        'original TGS32/4/2.5ms/100Hz/clip6','original patched D0-D7 backend auditors and new component populations',
        'root run GPU_PRECONTROL xi31/current127/provider binding before firstcontrol/Pi']),
    root_entry='source/native_own_fudan87_training.py:run(runner,n,log_dir,B,J,out,task,go,src,phase)',
    fresh_resume='source/fresh_policy_only_bootstrap87_v1.py:resume_policy_only_fresh4096; no old20k DR reshape',
    save_API='original install_step270_save_contract unchanged',
    local_validation=dict(passed=cpu['passed'],passed_count=cpu['passed_count'],total=cpu['total'],target_entry_executed=False),
    pending=['Root exact binder/sourceauth/manifest/Task assembly without hash cycles',
        'Actual target finite source/SDK/RSL CPU admission once, including model bytes and wholepolicy',
        'Real postGO fresh4096 DR/backend/solver/order/source precontrol gates before physicalcontrol/Pi',
        'Real VRAM/BPTT/fullsave resource admission and all original finite protections']))
handoff='''新worker/targetCPU source candidate已冻结；没有实际source模型读取/hash/copy、SDKscene、GPU、SSH、Task/GO、fee或Git。

worker h1_native_own87_worker_v1.py按原86B worker精确改动生成，原字节在ORIGINAL_NATIVE86B_WORKER_BYTES.txt；首版seed字段草稿也保留。最终CLI slot/seed绑定Task.native_seed，N4096、timeout5s、原2.5ms/TGS32/4/100Hz/clip6/270geometry/reward/command/no script/2mm perenv reset保持；checkpoint_API.resume_h1_new_episode精确接root resume_policy_only_fresh4096，install_step270_save_contract原样接新真实4096全D0-D7 save。三role统一读J/GO_PRODUCTION.json。rescue learn只调用source/native_own_fudan87_training.py run(...)，无旧native86 continuation restore。

native87_source_guard_v1.py执行实际完整manifest/pathcontainment/regularfile/size/SHA/Python全集检查，source contract+candidate pins+original runtime pins精确，不returntrue或放开目录。validate_task_go绑定最新H1PPO SHA0c1e...d394/Adam832460/update138、slotseed、新scope/config、manifest和contract、PRECONTROL_V2 sourcekind及3900/300期限。CPU入口在未来实际target才一次torch.load bootstrap，整树finite、actor9/critic8/STD6/17Adam832460、normal phase270、installed RSL严格载入回读、SDK/RSL版本与源码、原RewardManager/boundary/sampling CPU，以及新vendor_v5/MDP_v4 tinyAPI都实际执行。此入口本机从未启动。

旧protocol把preGO CPU当实际4096/order/DR的字段已在新copy修正。ready kind MOD4_H1_NATIVE87_POLICY_ONLY_SOURCE_SDK_CPU_PRECONTROL_V2；configured4096，actual_env=None，actual GPU order/DR=False。新网络/optimizer字段明确source API scope，不冒充完整2048网络或4096场景实际运行。新module仍名native87_protocol_v1.py以适配旧controller import，binder须在新owner/payload统一替换并重pin，旧冻结controllers_v2完全不改。

实际GPU门槛未减：worker learn前检查实际4096/5s/seed/clock0/age0、RSLclip6、TGS32/4、actual30jointorder、31body、原patched D0-D7 backend auditor、新component population和queue；root run随后还有真实GPU_PRECONTROL xi31/current127/provider/solver等。失败在firstphysicalcontrol/Pi前退出并保留原错，CPU报告绝不写这些已pass。

14/14新source/negative/API CPU检查通过，包括真实vendor_v5+MDP_v4/provider的batch2、hidden8 fixture：packed127/aux54/static31/obs86/goal1460/WMinput167、Pi6/Critic有限和config_for。没有执行旧once，没有实际policy actorforward或optimizer。模型2048/4096真实准入仍pending。源码/错误、原草稿/原worker都在完整SHA索引；binder所需Task/GO/contract字段见NATIVE87_WORKER_TARGET_CPU_BINDER_INTERFACE_ACTUAL.json。
'''
with (D/'FROZEN_NATIVE87_WORKER_TARGET_CPU_HANDOFF.md').open('x',encoding='utf8') as f:f.write(handoff)
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
rows=[dict(path=q.relative_to(D).as_posix(),bytes=q.stat().st_size,SHA=H(q)) for q in sorted(D.rglob('*')) if q.is_file() and q.name!='FROZEN_NATIVE87_WORKER_TARGET_CPU_SHA_INDEX.json']
put('FROZEN_NATIVE87_WORKER_TARGET_CPU_SHA_INDEX.json',dict(frozen_at_UTC=stamp,count_excluding_index=len(rows),files_excluding_this_index=rows,
    source_CPU_only=True,old_frozen_directories_untouched=True,actual_target_CPU_or_model_executed=False,parent_archive_pending=True))
print(json.dumps(dict(frozen_at_UTC=stamp,count_excluding_index=len(rows),worker_SHA=H(worker),target_CPU_SHA=H(target),protocol_SHA=H(protocol),
    index_SHA=H(D/'FROZEN_NATIVE87_WORKER_TARGET_CPU_SHA_INDEX.json'))))
