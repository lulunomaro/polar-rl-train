#!/usr/bin/env python3
"""Append-only final provenance; hash text files only, never model weights."""
import ast
import hashlib
import json
from pathlib import Path
import time

z=Path(__file__).resolve().parents[1]
t=z.parents[1];w=z.parents[2]
old=t/'MOD4_T2Z_H1_TRANSFER_PAPER_PREPARATION_20261025/engineering_agent'
def item(p):
    assert p.suffix.lower() not in ('.pt','.pth','.onnx','.safetensors','.npz','.zip')
    data=p.read_bytes()
    return dict(path=str(p),relative=str(p.relative_to(z)) if p.is_relative_to(z) else None,
                bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
oldindex=json.loads((old/'reports/ENGINEERING_FINAL_INDEX_ACTUAL.json').read_text(encoding='utf-8'))
for original in oldindex['files']:
    p=Path(original['path'])
    assert item(p)['sha256']==original['sha256']
for p in (z/'scripts').glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
reg=json.loads((z/'MOE_POLICY_REGISTRY.json').read_text(encoding='utf-8'))
assert all(x['actual_file_stat_only']['exists'] and x['actual_file_stat_only']['stat_bytes']==x['bytes']
           for pool in ('current_frozen_player_pool','latest_closed_training_candidate_pool') for x in reg[pool].values())
sources=[w/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/policy/manifest.json',
    w/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/export_requested_latest_player_V2_once.py',
    w/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/rm7v7_moe_sim.py',
    w/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/runtime_config.json',
    w/'mod4-onnx-mujoco-launcher/export_latest_moe.py',
    t/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json']
ledger=dict(schema_version=1,id='T2ZMOE_ENG_FINAL_LOCAL_PREPARATION_20261025_V1',epoch=time.time(),
    status='LOCAL_SOURCE_ENV_DOWNLOAD_REGISTRY_PREPARED_NOT_REMOTE_INSTALLED',
    corrected_scope='Entire MoE mixedRL T2-z; H1 one expert',
    predecessor='Frozen H1 engineering bundle retained unchanged',old_H1_index=item(old/'reports/ENGINEERING_FINAL_INDEX_ACTUAL.json'),
    old_H1_indexed_files_unchanged_verified=len(oldindex['files']),
    new_root='/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025',
    source_commit='c72f051f5cffcb1f372a32bc488df273556d39b9',
    manifest=item(z/'WEIGHTS_MANIFEST.json'),registry=item(z/'MOE_POLICY_REGISTRY.json'),
    actual_actions=dict(local_json_text_read=True,local_model_path_stat_only=True,
        checkpoint_or_ONNX_bytes_read=False,checkpoint_or_ONNX_hash_recomputed=False,
        local_AST_cli_digest_and_registry_QA=True,HTTP=False,remote_connection=False,
        source_clone=False,environment_install=False,weights_download=False,GPU_query=False,
        GPU_compute=False,policy_gate_inference=False,rollout=False,player_change=False,
        current_training_environment_change=False,driver_systemlibs_compat_change=False,
        budget_or_Git_change=False),
    QA=dict(bundle_latest=str(sorted((z/'reports').glob('LOCAL_VALIDATION_*_ACTUAL.json'))[-1]),
        bundle_checks=11,registry_latest=str(sorted((z/'reports').glob('MOE_REGISTRY_QA_*_ACTUAL.json'))[-1]),
        registry_cases=14,invalid_onehot_negative_cases=2,bash_n='PASS',
        after_finalizer_all_Python_AST='PASS',real_CPU_import_and_models='NOT_RUN'),
    new_actual_errors=[],scope_revision_preserved_as_authorized_new_stage=True,
    limitations=['OfficialfullWM24GBfitUNKNOWN','No2x24GBmemorypool','BWMcheckpointlicenseundeclared',
        'FullIsaacRSLPPOstacknotinstalledinnewvenv','Registryisnotnewfivewaylearnedgate',
        'Noexpertcheckpointcopiedforresearchinference','SeparatefuturetrainingGOrequired'],
    text_only_source_provenance=[item(p) for p in sources],archive_status='PENDING_ROOT_GIT')
out=z/'reports/MOE_ENGINEERING_FINAL_SCOPE_AND_QA_V1_ACTUAL.json'
with out.open('x',encoding='utf-8') as stream:json.dump(ledger,stream,indent=2,ensure_ascii=False)
files=[item(p) for p in sorted(z.rglob('*')) if p.is_file() and p.name!='MOE_ENGINEERING_FINAL_INDEX_V1_ACTUAL.json']
index=z/'reports/MOE_ENGINEERING_FINAL_INDEX_V1_ACTUAL.json'
with index.open('x',encoding='utf-8') as stream:
    json.dump(dict(schema_version=1,id='T2ZMOE_ENG_ALL_LOCAL_FILES_INDEX_20261025_V1',epoch=time.time(),
        archive_status='PENDING_ROOT_GIT',files=files,total_bytes=sum(x['bytes'] for x in files),
        index_self_excluded=True,old_H1_originals_referenced_not_rewritten=True),stream,indent=2,ensure_ascii=False)
print(json.dumps(dict(status='FINAL_LOCAL_PREPARATION_COMPLETE',files_excluding_index=len(files),
                     bytes_excluding_index=sum(x['bytes'] for x in files),old_H1_files_unchanged=len(oldindex['files']),index=str(index))))
