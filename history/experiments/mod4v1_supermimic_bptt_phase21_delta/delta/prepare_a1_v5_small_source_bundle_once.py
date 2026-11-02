"""Prepare only fourteen already-pinned small Python files for a new A1 input.
No remote, selected PT, GPU, SDK, owner or canonical operation.
"""
from pathlib import Path
import json,hashlib,ast
R=Path(__file__).resolve().parent;D=R.parent/'mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/parent_source/original_budget_and_asset_refs';P=R/'payload_a1_v5_small_source';assert not P.exists();S=R/'source_resume_runtime_v2';V=R/'source_app_close_semantics_v5'
items={
 'three_slot_common_v1.py':(D/'three_slot_common_v1.py','eaf6aa1a06d2a49570eff54af5447395210c6de9f3a9c43d566d1adad4e53044'),
 'single_writer72_authority_V85M_source.py':(D/'single_writer72_authority_V85M_source.py','ceba8067ceaffa8f2a978a0165b1ef06fc28b980d5f9da29ba03c760d9c1d98c'),
 'shared_gpu_admission_v1.py':(R/'source_runtime/shared_gpu_admission_v1.py','0ed3ca0e1f449a4c63deb1d6ba4f9037672438e1def74ffbb654efa3a7c3c42d'),
 'supermimic_original_owner_shared_app_close_candidate_v5.py':(V/'supermimic_original_owner_shared_app_close_candidate_v5.py','0f1618046d5751879f0ce40ff4b7424c83303ed1f61066521215c1d40eb76619'),
 'worker_sources/worker_supermimic_bptt_app_close_candidate_v5.py':(V/'worker_supermimic_bptt_app_close_candidate_v5.py','7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7'),
 'worker_sources/app_close_semantics_v5.py':(V/'app_close_semantics_v5.py','d64732c9310da2db59b349ad921862c78a33e2be5b60a442d456e8a62d63f3c1'),
 'worker_sources/resume_runtime_app_close_v5.py':(V/'resume_runtime_app_close_v5.py','208c4774f1033627c01253afe45ade9c426fdd9be70e76328125a59a80a20c5a'),
 'worker_sources/native_supermimic_bridge.py':(R/'source_runtime/native_supermimic_bridge.py','8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29'),
 'worker_sources/ctx_reward_full_resume_candidate_v2.py':(S/'ctx_reward_full_resume_candidate_v2.py','8116ea358dfe32e0efd568d00661ab1e13b602d267ea4b580ced04ec39e898ac'),
 'worker_sources/resume_runtime_contracts_v3.py':(S/'resume_runtime_contracts_v3.py','dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7'),
 'worker_sources/resume_runtime_install_hook_v4.py':(S/'resume_runtime_install_hook_v4.py','85f2fd4e45802eb94eb2311cf69410e5b20b1264255a2b0b562aa3c67f87405e'),
 'worker_sources/command_tracking_torch_candidate_v1.py':(R/'source_command_review_v1/command_tracking_torch_candidate_v1.py','bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223'),
 'worker_sources/original_role_command_binding_candidate_v2.py':(R/'source_runtime/original_role_command_binding_candidate_v2.py','348d0a09911a36ca9007ab5bb15f0b3e82bac3ab554cb8d73c62f8f0b5a763ea'),
 'worker_sources/pose_cache_runtime_adapter_v3.py':(R/'source_pose_cache_runtime_adapter_v3/pose_cache_runtime_adapter_v3.py','73145a1caa7819e0938e66e53a1bb0be73e48d0d06c3cf9cd5dc76e9f0862209')}
seal=V/'CODE_DELIVERABLES_SHA256_V5.json';assert hashlib.sha256(seal.read_bytes()).hexdigest()=='59e5cb530fbf2e2066856d9ba594afec151f4c5b512382a8905671586fe993a7'
rows=[];contents={};provenance=[]
for install,(source,sha)in items.items():
 assert source.suffix=='.py'and len(sha)==64;raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==sha,(source,hashlib.sha256(raw).hexdigest());ast.parse(raw.decode('utf-8-sig'));relative=source.name;assert relative not in contents;contents[relative]=raw;rows.append(dict(source_relative=relative,install_relative=install,SHA=sha,bytes=len(raw)));provenance.append(dict(original_local_source=str(source),source_relative=relative,install_relative=install,SHA=sha,bytes=len(raw)))
assert len(rows)==14
P.mkdir();source_dir=P/'source';source_dir.mkdir()
for name,raw in contents.items():(source_dir/name).write_bytes(raw)
index=dict(kind='SEALED_A1_NATIVE_V5_SOURCE_INDEX_V1',sealed=True,v5_code_seal_SHA='59e5cb530fbf2e2066856d9ba594afec151f4c5b512382a8905671586fe993a7',files=rows)
(P/'SEALED_A1_SOURCE_INDEX_V5.json').write_text(json.dumps(index,indent=2),encoding='utf-8');(P/'SMALL_SOURCE_BUNDLE_PROVENANCE_V5.json').write_text(json.dumps(dict(rows=provenance,original_helpers_byte_identical=True,selected_PT_SDK_GPU_C_GO_operations=0,not_stage_or_admission=True),indent=2),encoding='utf-8');print(json.dumps(dict(source_dir=str(source_dir),source_index=str(P/'SEALED_A1_SOURCE_INDEX_V5.json'),files=len(rows),bytes=sum(r['bytes']for r in rows),source_index_SHA=hashlib.sha256((P/'SEALED_A1_SOURCE_INDEX_V5.json').read_bytes()).hexdigest(),no_stage_or_native_admission=True),indent=2))
