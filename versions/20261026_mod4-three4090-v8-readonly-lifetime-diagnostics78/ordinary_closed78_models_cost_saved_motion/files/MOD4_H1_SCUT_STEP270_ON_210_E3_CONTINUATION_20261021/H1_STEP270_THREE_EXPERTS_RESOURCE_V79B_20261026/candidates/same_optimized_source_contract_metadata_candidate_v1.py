"""Source-only70 metadata/inventory candidate. Never sufficient for target CPU admission or GO."""
from pathlib import PurePath
import math,re

def validate_closed69_metadata(proof,key,source_Adam_at69_start):
    assert key in ('h1','e2','recovery')
    assert proof['passed'] and proof['all_owner_nodes_children_actual_out']
    assert proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free']
    model=proof['models'][key];final=model['final'];updates=model['updates']
    assert isinstance(updates,int) and updates>0 and final['updates']==updates
    assert model['Adam']==source_Adam_at69_start+20*updates
    assert final['twohost_complete_SHA'] and re.fullmatch('[0-9a-f]{64}',final['SHA'])
    assert isinstance(final['bytes'],int) and final['bytes']>0 and final['local_path']
    changed=model['all17_changed']
    assert len(changed['actor_state_dict'])==9 and len(changed['critic_state_dict'])==8
    assert 'distribution.std_param' in changed['actor_state_dict']
    cost=model['actual_cost'];values=[cost[k] for k in ('started_epoch','ended_epoch','charged_seconds')]
    assert all(math.isfinite(x) for x in values)
    assert cost['actual_returncode']==0 and cost['duration_bound_passed'] is True
    assert 0<cost['charged_seconds']<=3900
    assert abs(cost['charged_seconds']-(cost['ended_epoch']-cost['started_epoch']))<1e-5
    # A previous delayed-owner exception cannot qualify another source silently.
    assert not proof.get('not_a_pass_of_original_owner_duration_bound',False)
    return dict(metadata_passed=True,key=key,source_SHA=final['SHA'],source_Adam=model['Adam'],
                source_updates=updates,not_full_model_or_installed_SDK_CPU_admission=True,
                require_fresh_installed_source_SDK_RSL_and_original_resource_guards=True)

def validate_same_optimized_protected_inventory(prior,current):
    prefixes=('job0/runtime/','job0/assets/','lib/')
    before={r['relative']:r for r in prior['files'] if r['relative'].startswith(prefixes)}
    after={r['relative']:r for r in current['files'] if r['relative'].startswith(prefixes)}
    assert before and set(before)==set(after)
    for rel,row in before.items():
        assert after[rel]['bytes']==row['bytes'] and after[rel]['SHA']==row['SHA'],rel
    return dict(metadata_inventory_passed=True,protected_files=len(before),
                same_optimized_no_new_runtime_or_asset_additions=True,
                not_content_SHA_or_full_model_CPU_validation=True)
