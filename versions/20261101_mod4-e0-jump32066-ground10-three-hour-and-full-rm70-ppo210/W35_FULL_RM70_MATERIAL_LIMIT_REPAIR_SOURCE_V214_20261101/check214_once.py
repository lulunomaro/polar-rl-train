"""New214 source/material-value preservation CPU purpose, not a PhysX test."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
from types import SimpleNamespace
import ast,copy,hashlib,json,sys,time,traceback

HERE=Path(__file__).resolve().parent;SRC=HERE/'source';R=HERE/'reports';T=HERE.parent
ORIGINAL=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4/mild_dr.py'
ID='NEW214_MATERIAL_SOURCE_AND_20K_BUCKET_RNG_PRESERVATION_CPU_V1'
sys.path.insert(0,str(SRC))


def method(raw,classname,name):
    c=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef)and n.name==classname)
    f=next(n for n in c.body if isinstance(n,ast.FunctionDef)and n.name==name)
    return f


def main():
    frozen=json.loads((R/'CPU214_PURPOSE_FROZEN.json').read_bytes())
    assert frozen['ID']==ID and frozen['num_envs']==20000
    for row in frozen['source_rows']:
        raw=Path(row['path']).read_bytes()
        assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['SHA']
    with (R/'CPU214_ONCE_CONSUMED.json').open('x')as f:json.dump(dict(ID=ID,epoch=time.time()),f)
    groups=[]
    for path in SRC.glob('*.py'):compile(ast.parse(path.read_bytes(),filename=str(path)),str(path),'exec')
    groups.append('complete214_source_syntax_no_SDK_import')
    import material214 as m
    plan=m.plan(20000)
    assert plan['shared_original_material_references']==1 and plan['whole_asset_per_env_references']==0
    assert plan['geometry_reference_prim']=='/Asset/mesh'and plan['material_reference_prim']=='/Asset/physics_material'
    src=(SRC/'usd214.py').read_text()
    assert "shared.GetPrim().GetReferences().AddReference(str(asset),MATERIAL_PRIM)"in src
    assert 'strongerThanDescendants'in src and 'CreateStaticFrictionAttr'not in src
    assert 'CreateDynamicFrictionAttr'not in src and 'CreateRestitutionAttr'not in src
    assert 'source_slope'not in src or 'flatten'not in src
    groups.append('single_original_material_subprim_reference_no_geometry_or_coefficient_rewrite_source_contract')
    original=ORIGINAL.read_bytes();modified=(SRC/'mild_dr214.py').read_bytes()
    old=method(original,'MildDR','__call__');new=method(modified,'MildDR214','__call__')
    random_calls=lambda f:[ast.dump(n,include_attributes=False)for n in ast.walk(f)if isinstance(n,ast.Call)
        and((isinstance(n.func,ast.Attribute)and n.func.attr in ('rand','randint','uniform_')))]
    assert random_calls(old)==random_calls(new)
    import torch as t
    t.set_num_threads(1);assert not t.cuda.is_initialized()
    # Run the exact old/new reset method bodies against plain CPU value buffers.
    # This proves source assignments/RNG preservation,not backend material reuse.
    class View:
        def __init__(self,n):self.materials=t.tensor([.9,.9,0.]).repeat(n,4,1);self.calls=0
        def get_material_properties(self):return self.materials
        def set_material_properties(self,values,ids):
            self.calls+=1;self.materials[ids.long()]=values[ids.long()];return None
    class Robot:
        def __init__(self,n):
            self.root_view=View(n)
            self.actuators={k:SimpleNamespace(episode_scale=t.ones(n,w))for k,w in [('legs',4),('wheels',2)]}
        def set_masses_index(self,masses,env_ids):self.mass=masses.clone()
        def set_inertias_index(self,inertias,env_ids):self.inertia=inertias.clone()
    wp=SimpleNamespace(float32='f32',int32='i32',from_torch=lambda value,**kwargs:value)
    def make():
        n=20000;robot=Robot(n)
        return SimpleNamespace(robot=robot,recipe=dict(mass=(.9,1.1),motor=(.9,1.1),friction=(.7,1.)),
            generator=t.Generator().manual_seed(20260928+1717),cpu_generator=t.Generator().manual_seed(20260928+1818),
            factor=t.ones(n),nominal=t.ones(n,dtype=t.bool),mu=t.full((n,),.9),reset_count=t.zeros(n,dtype=t.long),
            mass=t.ones(n,2),inertia=t.ones(n,2,9),wheel_shapes=[0,1],
            friction_buckets=t.cat((t.tensor([.9]),t.linspace(.7,1.,32))),
            output={k:a.episode_scale for k,a in robot.actuators.items()})
    def compile_method(f):
        tree=ast.Module(body=[f],type_ignores=[]);namespace={'torch':t,'wp':wp,'tensor':lambda x:x}
        exec(compile(ast.fix_missing_locations(tree),'<exact_reset_method>','exec'),namespace)
        return namespace['__call__']
    f0=compile_method(old);f1=compile_method(new);a=make();b=make();env=SimpleNamespace(num_envs=20000,device='cpu')
    old_log=m.log;m.log=lambda *args,**kwargs:None
    try:
        f0(a,env,None);f1(b,env,None)
        snapshot=m.own_mild_state(t,b)
        g=b.generator.get_state().clone();cpu=b.cpu_generator.get_state().clone()
        m.restore_own_mild_state(t,wp,b,snapshot,lambda x:x)
        assert t.equal(g,b.generator.get_state())and t.equal(cpu,b.cpu_generator.get_state())
        f0(a,env,None);f1(b,env,None)
        for name in ('factor','nominal','mu','reset_count'):
            assert t.equal(getattr(a,name),getattr(b,name)),name
        assert t.equal(a.generator.get_state(),b.generator.get_state())
        assert t.equal(a.cpu_generator.get_state(),b.cpu_generator.get_state())
        assert t.equal(a.robot.root_view.materials,b.robot.root_view.materials)
        for name in ('legs','wheels'):assert t.equal(a.output[name],b.output[name])
        assert a.robot.root_view.calls==2 and b.robot.root_view.calls==3
        assert t.unique(b.mu).numel()<=33 and float(b.mu.min())>=.7-1e-7 and float(b.mu.max())<=1.
    finally:m.log=old_log
    groups.append('exact_old_new_20k_reset_bucket_mass_motor_and_RNG_preserved_plus_own_restore_no_draw')
    negative=[]
    for n in (0,20001):
        try:m.plan(n)
        except ValueError:negative.append('invalid_layout_population_'+str(n))
        else:raise AssertionError('Expected bounded layout refusal')
    bad=copy.deepcopy(snapshot);bad['mu']=bad['mu'][:-1]
    try:m.restore_own_mild_state(t,wp,b,bad,lambda x:x)
    except ValueError:negative.append('own_state_wrong_population')
    else:raise AssertionError('Expected own-state shape refusal')
    assert not t.cuda.is_initialized()
    report=dict(ID=ID,passed=True,groups=groups,negative_refusals=negative,synthetic_num_envs=20000,
        original_reset_calls=2,new_reset_calls=2,new_probe_only_same_value_restore_calls=1,
        synthetic_actual_setter_calls=dict(original=2,candidate_with_extra_own_reapply=3),
        material_bucket_value_distribution_and_random_streams_unchanged=True,
        actual_PhysX_handle_allocation_or_USD_composition_tested=False,
        cannot_certify_64K_capacity_without_actual20k_target=True,
        model_NPZ_USD_SDK_GPU_remote_Git_reads=0,neural_updates=0,old213_or208_tests_replayed=False,
        candidate_root_actual_probe_required=True,oldW35_failure_not_reclassified=True,Git_pending_root=True)
    with (R/'CPU214_ACTUAL.json').open('x',encoding='utf8')as f:json.dump(report,f,indent=2)
    print(json.dumps(dict(ID=ID,passed=True,groups=len(groups),negative_refusals=negative,synthetic_num_envs=20000)))


if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('CPU214_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x')as f:json.dump(dict(ID=ID,error=traceback.format_exc(),robot_failure=False),f,indent=2)
        raise
