#!/usr/bin/env python3
"""JSON-only MoE registry and synthetic routing/clock contract; no model reads."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import time
import uuid

EXPERTS={'E0','W35','H1','E2','E3'}
ROLES=EXPERTS|{'gate148'}
def validate_registry(r):
    assert set(r['expert_ids'])==EXPERTS
    assert r['gate_id']=='gate148' and r['pools_are_distinct']
    assert r['new_five_way_learned_gate'] is False
    assert r['weights_or_models_read'] is False and r['expert_policy_inference'] is False
    assert r['control']['observation_width']==35 and r['control']['action_width']==6
    assert r['control']['native_Hz']=={'E0':100,'W35':100,'H1':100,'E2':50,'E3':50}
    for poolname in ('current_frozen_player_pool','latest_closed_training_candidate_pool'):
        pool=r[poolname]
        assert set(pool)==ROLES
        for role,item in pool.items():
            assert isinstance(item['path'],str) and item['path'].lower().endswith('.pt')
            assert re.fullmatch('[0-9a-f]{64}',item['SHA'])
            assert item['bytes']>0
            stat=item['actual_file_stat_only']
            assert stat['content_read'] is False and stat['digest_recomputed'] is False
            if stat['exists']:assert stat['stat_bytes']==item['bytes']
    old=r['current_frozen_player_pool'];new=r['latest_closed_training_candidate_pool']
    for role in ('E0','W35','gate148','E2'):assert old[role]['SHA']==new[role]['SHA']
    for role in ('H1','E3'):
        assert old[role]['SHA']!=new[role]['SHA']
        assert new[role]['source_generation']=='closed67'
        assert new[role]['reported_twohost_complete_SHA'] is True
    assert sum(x['bytes'] for x in new.values())==r['checkpoint_pool_total_bytes']==101876943


def contract(observation,gate_choice):
    assert len(observation)==35 and gate_choice in (0,1)
    modebits=observation[28:35]
    assert modebits.count(1)==1 and modebits.count(0)==6
    mode=modebits.index(1)
    role={4:'H1',3:'E3',6:'E2'}.get(mode,('E0','W35')[gate_choice])
    view=list(observation)
    if role not in ('H1','E3'):view[28:35]=[1,0,0,0,0,0,0]
    return role,view,2 if role in ('E2','E3') else 1


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--registry',type=Path,default=Path(__file__).resolve().parents[1]/'MOE_POLICY_REGISTRY.json')
    p.add_argument('--outdir',type=Path,default=Path(__file__).resolve().parents[1]/'reports')
    args=p.parse_args()
    data=args.registry.read_bytes() # Text registry only; never follow checkpoint paths.
    r=json.loads(data.decode('utf-8-sig'))
    result=dict(id='T2ZMOE_REGISTRY_AND_SYNTHETIC_CONTRACT_V1',epoch=time.time(),
                registry_sha256=hashlib.sha256(data).hexdigest(),checkpoint_content_read=False,
                checkpoint_hash_recomputed=False,policy_or_gate_inference=False,GPU_used=False,
                real_player_or_training_adapter_tested=False,archive_status='PENDING_ROOT_GIT')
    code=0
    try:
        validate_registry(r)
        rows=[]
        for mode in range(7):
            for gate in (0,1):
                obs=[0.0]*35;obs[28+mode]=1
                role,view,period=contract(obs,gate)
                expected={4:'H1',3:'E3',6:'E2'}.get(mode,('E0','W35')[gate])
                assert role==expected
                assert view[28:35]==(obs[28:35] if role in ('H1','E3') else [1,0,0,0,0,0,0])
                calls=sum(tick%period==0 for tick in range(12))
                assert calls==(6 if role in ('E2','E3') else 12)
                rows.append(dict(mode=mode,stub_gate_choice=gate,expected_role=role,
                                 synthetic12_outer_ticks_policy_calls=calls))
        # Invalid mode packets fail before any future adapter or model call.
        for invalid in ([0.0]*35,[0.0]*28+[1,1,0,0,0,0,0]):
            try:contract(invalid,0)
            except AssertionError:pass
            else:raise AssertionError('Invalid synthetic onehot accepted')
        result.update(status='PASS_JSON_AND_SYNTHETIC_CONTRACT_ONLY',rows=rows)
    except Exception as exc:
        result.update(status='FAILURE_PRESERVED',error_type=type(exc).__name__)
        code=1
    args.outdir.mkdir(parents=True,exist_ok=True)
    out=args.outdir/f'MOE_REGISTRY_QA_{time.time_ns()}_{uuid.uuid4().hex[:8]}_ACTUAL.json'
    with out.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2)
    print(json.dumps(dict(receipt=str(out),status=result['status'])))
    return code


if __name__=='__main__':raise SystemExit(main())
