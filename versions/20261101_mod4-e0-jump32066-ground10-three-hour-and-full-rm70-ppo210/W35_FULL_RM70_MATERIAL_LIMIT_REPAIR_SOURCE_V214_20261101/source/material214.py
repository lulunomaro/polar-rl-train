"""Source-level shared-material contract and log-only setter evidence.

No SDK/Torch import at module import. Stage prim/path/value counts are NOT
PhysX material-handle counts. The real parent must reject any64K error in logs.
"""
from pathlib import Path
import json,os,time

GEOMETRY_PRIM='/Asset/mesh'
MATERIAL_PRIM='/Asset/physics_material'
_phase='BEFORE_CONSTRUCTION'
_setter_calls=0
_stream=None


def plan(n):
    if type(n)is not int or not 1<=n<=20000:raise ValueError('Explicit bounded layout population required')
    return dict(num_envs=n,geometry_reference_prim=GEOMETRY_PRIM,
        material_reference_prim=MATERIAL_PRIM,whole_asset_per_env_references=0,
        shared_original_material_references=1,original_wheel_mu_buckets=33,
        geometry_scaled_or_flattened=False,material_coefficients_overridden=False,
        original_collision_contact_and_rest_offsets_unchanged=True,
        stage_topology_plan_not_PhysX_material_handle_count=True)


def log(kind,**value):
    global _stream
    row=dict(epoch=time.time(),kind=kind,phase=_phase,**value)
    directory=os.environ.get('MOD4_MATERIAL214_OUT')
    if directory:
        if _stream is None:
            _stream=(Path(directory)/'MATERIAL214_PHASE_AND_SETTER_EVENTS.jsonl').open('x',encoding='utf8')
        _stream.write(json.dumps(row,separators=(',',':'),allow_nan=False)+'\n');_stream.flush()
    print('MATERIAL214 '+json.dumps(row,separators=(',',':'),allow_nan=False),flush=True)
    return row


def phase(name,**value):
    global _phase
    _phase=name;return log('PHASE_BOUNDARY',**value)


def cached_summary(t,materials):
    values=materials.detach().cpu().reshape(-1,3)
    unique=t.unique(values,dim=0)
    return dict(cached_property_rows=len(values),distinct_cached_value_triples=len(unique),
        cached_value_examples=unique[:40].tolist(),
        value_counts_not_PhysX_material_handles=True)


def set_material_once(t,wp,view,materials,cpu_ids):
    global _setter_calls
    _setter_calls+=1;number=_setter_calls
    log('BEFORE_ACTUAL_SET_MATERIAL_PROPERTIES',call=number,selected_envs=int(cpu_ids.numel()),
        property_buffer_shape=list(materials.shape),**cached_summary(t,materials))
    result=view.set_material_properties(wp.from_torch(materials,dtype=wp.float32),
        wp.from_torch(cpu_ids,dtype=wp.int32))
    log('AFTER_ACTUAL_SET_MATERIAL_PROPERTIES',call=number,original_return_preserved=True)
    return result


def counts():return dict(observed_project_material_setter_calls=_setter_calls,
    SDK_internal_material_allocation_count='UNKNOWN_NOT_EXPOSED_BY_THIS_OBSERVER',
    no_additional_material_getter_in_setter_observer=True)


def own_mild_state(t,adapter):
    """Own already-created20k data only, never a saved teacher/PT projection."""
    return dict(factor=adapter.factor.clone(),nominal=adapter.nominal.clone(),mu=adapter.mu.clone(),
        reset_count=adapter.reset_count.clone(),generator=adapter.generator.get_state().clone(),
        cpu_generator=adapter.cpu_generator.get_state().clone(),
        output={name:value.clone()for name,value in adapter.output.items()})


def restore_own_mild_state(t,wp,adapter,state,tensor):
    """Model-free probe stress: same values/streams, explicit same physical setters.

    Original production sensor resume restores named RNG then one reset. This
    additional same-value material reapply is explicitly probe-only, to test the
    cumulative allocation risk without extra random draws or changed DR values.
    """
    n=len(adapter.factor);ids=t.arange(n,device=adapter.factor.device)
    for name in ('factor','nominal','mu','reset_count'):
        destination=getattr(adapter,name);saved=state[name]
        if destination.shape!=saved.shape or destination.dtype!=saved.dtype:raise ValueError('Own same-population state shape differs')
        destination.copy_(saved)
    adapter.generator.set_state(state['generator'].cpu())
    adapter.cpu_generator.set_state(state['cpu_generator'].cpu())
    adapter.robot.set_masses_index(masses=adapter.mass*adapter.factor[:,None],env_ids=ids)
    adapter.robot.set_inertias_index(inertias=adapter.inertia*adapter.factor[:,None,None],env_ids=ids)
    for name,value in state['output'].items():adapter.output[name].copy_(value)
    cpu_ids=ids.to(device='cpu',dtype=t.int32)
    materials=tensor(adapter.robot.root_view.get_material_properties()).clone().cpu()
    mu=adapter.mu
    values=t.stack((mu,mu,t.zeros_like(mu)),dim=-1)
    materials[cpu_ids.long()[:,None],adapter.wheel_shapes]=values[:,None,:]
    set_material_once(t,wp,adapter.robot.root_view,materials,cpu_ids)
    log('OWN_SAME_POPULATION_MILD_STATE_RESTORED',num_envs=n,new_random_draws=0,
        explicit_probe_only_same_value_material_reapply=True)


def finish():
    global _stream
    if _stream is not None:_stream.close();_stream=None
