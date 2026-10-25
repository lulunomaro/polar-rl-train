#!/usr/bin/env python3
"""Fresh MoE scope binding; preserve H1 v1, never read checkpoint/ONNX bytes."""
import hashlib
import json
from pathlib import Path
import shutil
import time

z=Path(__file__).resolve().parents[1]
t=z.parents[1]
w=z.parents[2]
old=t/'MOD4_T2Z_H1_TRANSFER_PAPER_PREPARATION_20261025/engineering_agent'
oldroot='/home/lc01/Zonglin Li/zonglin2/research/T2Z_H1_TRANSFER_PREP_20261025'
newroot='/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025'
def sha_text(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def write_new(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2,ensure_ascii=False)
def stat_only(path):
    p=Path(path)
    try:
        s=p.stat()
        return dict(exists=True,stat_bytes=s.st_size,stat_mtime_ns=s.st_mtime_ns,
                    content_read=False,digest_recomputed=False)
    except FileNotFoundError:
        return dict(exists=False,content_read=False,digest_recomputed=False)
copies=[]
for folder in ('source_snapshot','metadata'):
    for src in sorted((old/folder).rglob('*')):
        if not src.is_file():continue
        dst=z/src.relative_to(old)
        dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():raise RuntimeError('Fresh bundle destination must be unused')
        shutil.copyfile(src,dst)
        assert sha_text(src)==sha_text(dst)
        copies.append(dict(source=str(src),destination=str(dst),sha256=sha_text(dst),kind='exact_public_text_metadata_copy'))
for name in ('prepare_isolated.py','download_required.py','cpu_import_interface_check.py','validate_local_bundle.py'):
    src=old/'scripts'/name
    dst=z/'scripts'/name
    content=src.read_text(encoding='utf-8').replace(oldroot,newroot).replace('T2ZH1','T2ZMOE')
    if dst.exists():raise RuntimeError('Fresh script destination must be unused')
    dst.write_text(content,encoding='utf-8')
    copies.append(dict(source=str(src),source_sha256=sha_text(src),destination=str(dst),sha256=sha_text(dst),kind='fresh_root_and_identifier_binding_only'))
manifest=json.loads((old/'WEIGHTS_MANIFEST.json').read_text(encoding='utf-8-sig'))
manifest.update(id='T2ZMOE_ENG_MINIMUM_OFFICIAL_WEIGHTS_MANIFEST_20261025_V1',
    created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),remote_root=newroot,
    preparation_scope='Whole MoE plus RL T2-z migration; H1 is one expert',
    predecessor_manifest=dict(path=str(old/'WEIGHTS_MANIFEST.json'),sha256=sha_text(old/'WEIGHTS_MANIFEST.json')),
    download_authorization='Root serial owner only after M4 CPU/IO release; preparation only, no training')
write_new(z/'WEIGHTS_MANIFEST.json',manifest)
capacity=json.loads((old/'CAPACITY_PLAN.json').read_text(encoding='utf-8-sig'))
capacity.update(id='T2ZMOE_ENG_CAPACITY_PLAN_20261025_V1',remote_root=newroot,
    scope='Whole MoE+RL research preparation; no current policy transfer/inference',
    prior_capacity_plan=dict(path=str(old/'CAPACITY_PLAN.json'),sha256=sha_text(old/'CAPACITY_PLAN.json')),
    scope_rebind_epoch=time.time(),
    estimate_warning='Original H1 dataset50GiB/cache20GiB/checkpoints60GiB are illustrative only; wholeMoE coverage not measured or reserved',
    existing_policy_file_transfer_authorized=False)
write_new(z/'CAPACITY_PLAN.json',capacity)
player=w/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/policy/manifest.json'
p=json.loads(player.read_text(encoding='utf-8-sig'))
proof=t/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'
c=json.loads(proof.read_text(encoding='utf-8-sig'))
assert c['passed'] and c['all_owner_nodes_children_actual_out'] and c['original_canonical_cost_settled']
frozen={}
for role,item in p['sources'].items():
    frozen[role]=dict(item,actual_file_stat_only=stat_only(item['path']),sha_evidence='Existing player manifest; not recomputed now')
latest={role:dict(item) for role,item in frozen.items()}
for role,key,hz in [('H1','h1',100),('E3','recovery',50)]:
    row=c['models'][key]
    f=row['final']
    latest[role]=dict(path=f['local_path'],remote_original_path=f['path'],bytes=f['bytes'],
        SHA=f['SHA'],Adam=row['Adam'],policy_hz=hz,source_generation='closed67',
        complete_checkpoint_proof=str(proof),proof_sha256=sha_text(proof),
        reported_twohost_complete_SHA=f['twohost_complete_SHA'],
        actual_file_stat_only=stat_only(f['local_path']),sha_evidence='Existing complete67 producer report; not recomputed now')
registry=dict(schema_version=1,id='MOD4_WHOLE_MOE_RL_T2Z_POLICY_REGISTRY_20261025_V1',epoch=time.time(),
    scope='Whole MoE+RL T2-z engineering registry, not a runnable policy or learned five-way gate',
    root=newroot,source_player_manifest=dict(path=str(player),sha256=sha_text(player),epoch=p['epoch']),
    current_frozen_player_pool=frozen,latest_closed_training_candidate_pool=latest,
    pools_are_distinct=True,player_rewritten=False,live_reload=False,
    player_ONNX=dict(path=str(player.parent/'hybrid_moe.onnx'),existing_manifest_sha256=p['onnx_SHA'],
        actual_file_stat_only=stat_only(player.parent/'hybrid_moe.onnx'),not_loaded=True),
    expert_ids=['E0','W35','H1','E2','E3'],gate_id='gate148',
    current_gate_scope='Original trained E0/W35 binary gate; H1/E2/E3 are public mode dispatch',
    new_five_way_learned_gate=p['new_five_way_learned_gate'],
    routing=dict(normal='gate148 argmax E0/W35 on normal_view observation',mode4='H1 original35view',
        mode3='E3 original35view',mode6='E2 with normal_view before inference',
        action_selection='one complete6vector, clamp[-6,6], no weight/action averaging'),
    control=dict(observation_width=35,action_width=6,normal_mode_columns='28:35 rewritten onehot normal',
        native_Hz=p['policy_hz'],player_outer_Hz=100,E2_E3_hold_outer_ticks=2,
        physical_dt_s=0.0025,H1_decimation=4,E3_decimation=8),
    weights_or_models_read=False,expert_policy_inference=False,GPU_used=False,
    future_transfer_status='NOT_COPIED_TO_RESEARCH_ENV',archive_status='PENDING_ROOT_GIT')
registry['checkpoint_pool_total_bytes']=sum(x['bytes'] for x in latest.values())
write_new(z/'MOE_POLICY_REGISTRY.json',registry)
write_new(z/'reports/MOE_FRESH_SCOPE_BINDING_V1_ACTUAL.json',dict(id='T2ZMOE_ENG_FRESH_BINDING_20261025_V1',epoch=time.time(),
    previous_H1_root_deployed=False,old_H1_bundle_unchanged=True,old_H1_final_index_sha256=sha_text(old/'reports/ENGINEERING_FINAL_INDEX_ACTUAL.json'),
    new_root=newroot,copies=copies,source_commit=manifest['upstream_commit'],
    weights_identical_fixed_revisions_and_digests=True,weight_download=False,remote_connection=False,
    registry_only_PT_or_ONNX_content_read=False,Git_action=False,archive_status='PENDING_ROOT_GIT'))
print(json.dumps(dict(root=str(z),remote_root=newroot,public_text_copies=len(copies),registry_checkpoint_bytes=registry['checkpoint_pool_total_bytes'],status='FRESH_LOCAL_PREPARED')))
