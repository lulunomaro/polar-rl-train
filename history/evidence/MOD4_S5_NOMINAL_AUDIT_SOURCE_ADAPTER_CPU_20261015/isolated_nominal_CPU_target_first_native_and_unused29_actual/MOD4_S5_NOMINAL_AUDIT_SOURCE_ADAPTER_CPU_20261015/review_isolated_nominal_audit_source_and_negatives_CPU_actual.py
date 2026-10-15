"""Independent source inverse, real audit-method CPU fixtures, and strict negatives.

This does not import Isaac Sim, call a GPU setter, or certify future target physics.
"""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import os
import sys
import time
import traceback
import types

os.environ['CUDA_VISIBLE_DEVICES'] = ''
import numpy as np
import torch

D = Path(__file__).resolve().parent
W = D.parent
O = D / 'isolated'
R = D / 'reports'
S = W / 'MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload'
MOD = S / 'runtime/isaac/mod4'
NS = types.SimpleNamespace
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


helper = load('nominal_d0_source_audit_v1', O / 'nominal_d0_source_audit_v1.py')
sys.path.insert(0, str(MOD))
from spring_pressure_component import SpringPressure
from gas_damping_factor import GasDamping, PROFILE as GAS_PROFILE
from chassis_com_component import ChassisCOM, PROFILE as COM_PROFILE
from explicit_pd_component import ExplicitPD, PROFILE as PD_PROFILE


def rejection(fn):
    try:
        fn()
    except (AssertionError, RuntimeError, AttributeError, ValueError) as e:
        return dict(rejected=True, exception=type(e).__name__, reason=str(e))
    raise AssertionError('Expected strict rejection was missing')


def node(path, name, parent=None):
    tree = ast.parse(Path(path).read_text(encoding='utf8'))
    body = tree.body if parent is None else next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == parent).body
    return copy.deepcopy(next(x for x in body if getattr(x, 'name', None) == name))


def compile_nodes(nodes, namespace):
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), '<actual_saved_source_AST>', 'exec'), namespace)
    return namespace


def class_(path, name, **kwargs):
    namespace = dict(torch=torch, np=np, types=types, tensor=lambda x: x, PROFILE=kwargs.pop('PROFILE', 'fixture'),
                     mild_dr_present_or_nominal=helper.mild_dr_present_or_nominal,
                     capture_nominal_d0_reference=helper.capture_nominal_d0_reference,
                     s5_parameter_audit=helper.parameter_audit, **kwargs)
    return compile_nodes([node(path, name)], namespace)[name]


def methods(path, names):
    namespace = dict(torch=torch, np=np, hashlib=hashlib, tensor=lambda x: x,
                     js=lambda x: x.detach().cpu().tolist(), mild_dr_present_or_nominal=helper.mild_dr_present_or_nominal)
    return compile_nodes([node(path, n) for n in names], namespace)


class Inverse(ast.NodeTransformer):
    def visit_IfExp(self, n):
        if isinstance(n.test, ast.Call) and isinstance(n.test.func, ast.Name) and n.test.func.id == 'mild_dr_present_or_nominal':
            return self.visit(n.body)
        return self.generic_visit(n)

    def visit_Call(self, n):
        if isinstance(n.func, ast.Name) and n.func.id == 's5_parameter_audit':
            return ast.Call(func=ast.Attribute(value=ast.Attribute(value=n.args[0], attr='_mild_dr', ctx=ast.Load()), attr='audit', ctx=ast.Load()), args=[], keywords=[])
        return self.generic_visit(n)


def inverse_sources(manifest):
    proofs = []
    for row in manifest['candidates']:
        assert H(row['original']) == row['original_SHA'] and H(row['candidate']) == row['candidate_SHA']
        original = ast.parse(Path(row['original']).read_text(encoding='utf8'))
        new = ast.parse(Path(row['candidate']).read_text(encoding='utf8'))
        assert isinstance(new.body[0], ast.ImportFrom) and new.body[0].module == 'nominal_d0_source_audit_v1'
        new.body.pop(0)
        name = Path(row['candidate']).name
        if name == 'spring_pressure_audit_runtime.py':
            ctor = next(n for n in ast.walk(new) if isinstance(n, ast.FunctionDef) and n.name == '__init__')
            guard = ctor.body[1]
            assert isinstance(guard, ast.If) and len(guard.orelse) == 1
            assert ast.unparse(guard.test) == 'mild_dr_present_or_nominal(self.env)'
            assert ast.unparse(guard.orelse[0]) == 'capture_nominal_d0_reference(self.env)'
            ctor.body[1:] = guard.body
        elif name == 'gas_damping_sdk_adapter.py':
            f = next(n for n in ast.walk(new) if isinstance(n, ast.FunctionDef) and n.name == 'install_expected_value_auditors')
            assert ast.unparse(f.body[0]) == 'adapter = self'
            guard = f.body[1]
            assert ast.unparse(guard.test) == 'mild_dr_present_or_nominal(self.env)' and not guard.orelse
            f.body = guard.body + f.body[2:]
        elif name in ('chassis_com_pose_roundtrip_sdk_adapter.py', 'explicit_pd_sdk_adapter.py'):
            f = next(n for n in ast.walk(new) if isinstance(n, ast.FunctionDef) and n.name == 'install_expected_value_auditor')
            assert ast.unparse(f.body[0]) == 'if not mild_dr_present_or_nominal(self.env):\n    return'
            f.body.pop(0)
        elif name == 'nominal_parameter_audit.py':
            assert new.body[-1].name == 'parameter_audit'
            new.body.pop()
            next(n for n in new.body if isinstance(n, ast.FunctionDef)).name = 'parameter_audit'
        elif name.startswith('factor_runtime'):
            f = next(n for n in new.body if isinstance(n, ast.FunctionDef) and n.name == 'private_rng')
            loop = next(n for n in f.body if isinstance(n, ast.For))
            assert ast.unparse(loop.body[0]).startswith("if k == '_mild_dr' and (not mild_dr_present_or_nominal(e)):")
            loop.body.pop(0)
        new = Inverse().visit(new)
        assert ast.dump(new, include_attributes=False) == ast.dump(original, include_attributes=False), name
        proofs.append(dict(file=name, inverse_AST_exact=True, original_SHA=row['original_SHA'], candidate_SHA=row['candidate_SHA']))
    return proofs


def fixture(n, seed, white):
    e = NS(num_envs=n, device='cpu')
    g = torch.Generator().manual_seed(seed + 101)
    mass = torch.tensor([2., .3, .3]).repeat(n, 1)
    inertia = torch.eye(3).reshape(1, 1, 9).repeat(n, 3, 1)
    material = torch.tensor([.9, .9, 0.]).repeat(n, 3, 1)
    pose0 = torch.zeros(n, 3, 7); pose0[..., -1] = 1.
    legs = NS(stiffness=torch.full((n,4),60.), damping=torch.full((n,4),2.), episode_scale=torch.ones(n,1), step_scale=torch.ones(n,1))
    wheels = NS(stiffness=torch.zeros(n,2), damping=torch.full((n,2),.6), episode_scale=torch.ones(n,1), step_scale=torch.ones(n,1))
    spring = SpringPressure(n, 'cpu', seed, True); spring.reset(torch.arange(n))
    gas = GasDamping(n, 'cpu', seed, True); gas.reset(torch.arange(n))
    com = ChassisCOM(n, 'cpu', seed, True); com.reset(torch.arange(n))
    pd = ExplicitPD(n, 'cpu', seed, True); pd.reset(torch.arange(n))
    stiffness = torch.zeros(n,8); stiffness[:,6:] = spring.actual_stiffness(torch.tensor([3500.,3500.]))
    damping0 = torch.zeros(n,8); damping0[:,6:] = 3.
    damping = damping0.clone(); damping[:,6:] = gas.actual_damping_Ns_per_m()
    pose = pose0.clone(); pose[:,0,:3] += com.delta_m
    gasact = NS(stiffness=stiffness[:,6:].clone(), damping=damping[:,6:].clone())
    force = torch.full((n,8),2000.); armature = torch.zeros(n,8)
    view = NS(get_masses=lambda:mass, get_inertias=lambda:inertia, get_material_properties=lambda:material,
              get_coms=lambda:pose, get_dof_stiffnesses=lambda:stiffness, get_dof_dampings=lambda:damping,
              get_dof_max_forces=lambda:force, get_dof_armatures=lambda:armature)
    data = NS(joint_stiffness=stiffness.clone(), joint_damping=damping.clone(), body_com_pose_b=pose.clone(), body_com_pos_b=pose[...,:3].clone())
    robot = NS(root_view=view, data=data, actuators=dict(legs=legs,wheels=wheels,gas_springs=gasact), body_names=['chassis','left_wheel','right_wheel'])
    e.scene = dict(robot=robot)
    e._sensor_mild = NS(bias=torch.zeros(n,3), episode=torch.ones(n,dtype=torch.long), generator=g, state_dict=lambda:dict(bias=torch.zeros(n,3)))
    e._feedback_delay_mild = NS(delay=torch.zeros(n), generator=torch.Generator().manual_seed(seed+102), state_dict=lambda:dict(delay=torch.zeros(n)))
    queue = NS(groups=dict(legs=dict(lag_steps=torch.zeros(n,dtype=torch.long),episode=torch.ones(n,dtype=torch.long))), generator=torch.Generator().manual_seed(seed+103),state_dict=lambda:dict(lag_steps=torch.zeros(n,dtype=torch.long)))
    e._physics_action_delay = NS(queue=queue)
    term = NS(generator=torch.Generator().manual_seed(seed+104))
    e.command_manager = NS(get_term=lambda name:term)
    cls = class_(MOD/'spring_pressure_training_env.py', 'LearningSpringPressure', SpringPressureSDK=object, PROFILE='D5fixture')
    sp = object.__new__(cls)
    sp.component=spring;sp.nominal=torch.tensor([3500.,3500.]);sp.robot=robot;sp.ids=[6,7];sp.actuator=gasact
    sp.initial_other=dict(damping=damping0.clone(),force_limit=force.clone(),armature=armature.clone())
    sp.reset_count=1;sp.selected_reset_count=n;e._spring_pressure=sp
    cls = class_(O/'gas_damping_sdk_adapter.py','GasDampingSDK',PROFILE=GAS_PROFILE)
    ga = object.__new__(cls)
    ga.env=e;ga.robot=robot;ga.component=gas;ga.actuator=gasact;ga.ids=[6,7];ga.original_damping=damping0.clone();ga.other_ids=list(range(6))
    ga.fixed=dict(get_dof_max_forces=force.clone(),get_dof_armatures=armature.clone())
    ga.reset_calls=1;ga.selected_reset_samples=n;ga.setter_calls=1;e._gas_damping=ga
    cls = class_(O/'chassis_com_pose_roundtrip_sdk_adapter.py','ChassisCOMSDK',PROFILE=COM_PROFILE)
    ca = object.__new__(cls)
    ca.env=e;ca.robot=robot;ca.component=com;ca.body_id=0;ca.original_pose=pose0.clone();ca.orientation_after_parent_reset=pose[...,3:].clone()
    ca.setter_calls=1;ca.reset_calls=1;ca.cache_invalidations=1;ca.orientation_roundtrip_max=0.;ca.raw_quaternion_bytes_always_exact=True;e._chassis_com=ca
    cls = class_(O/'explicit_pd_sdk_adapter.py','ExplicitPDSDK',PROFILE=PD_PROFILE)
    pa = object.__new__(cls)
    pa.env=e;pa.robot=robot;pa.component=pd;pa.legs=legs;pa.wheels=wheels;pa.motor_ids=list(range(6));pa.leg_ids=list(range(4));pa.wheel_ids=[4,5]
    pa.nominal=dict(leg_kp=legs.stiffness.clone(),leg_kd=legs.damping.clone(),wheel_kd=wheels.damping.clone(),wheel_kp=wheels.stiffness.clone())
    values=pd.coefficients();legs.stiffness=values['leg_kp'].clone();legs.damping=values['leg_kd'].clone();wheels.damping=values['wheel_kd'].clone()
    pa.model_write_calls=1;pa.reset_calls=1;e._explicit_pd=pa
    if white:
        e._mild_dr=NS(factor=torch.ones(n),nominal=torch.ones(n,dtype=torch.bool),mu=torch.full((n,),.9),output=dict(legs=legs.episode_scale,wheels=wheels.episode_scale),
            gains=dict(gas_springs=dict(stiffness=torch.full((n,2),3500.),damping=torch.full((n,2),3.)),
                       legs=dict(stiffness=pa.nominal['leg_kp'],damping=pa.nominal['leg_kd']),
                       wheels=dict(damping=pa.nominal['wheel_kd'])),com=pose0[...,:3].clone(),generator=torch.Generator().manual_seed(seed+1717),audit=lambda:dict(base_audit=True))
    return e,dict(mass=mass,inertia=inertia,materials=material,pose=pose,stiffness=stiffness,damping=damping)


def run():
    path=R/'NOMINAL_ISOLATED_GUARDS_METADATA_D0_D7_NEGATIVES_CPU_ACTUAL.json'
    assert not path.exists()
    manifest=json.loads((R/'NOMINAL_ISOLATED_SOURCE_CANDIDATES_MATERIALIZED_ACTUAL.json').read_bytes())
    inverse=inverse_sources(manifest)
    original_rng=torch.get_rng_state().clone()
    original_env={k:os.environ.get(k) for k in ('RM_MILD_DR_PROFILE','RM_DR_OFF')}
    rows=[]
    fn_names=['private_rng','json_tree','full_initial_queue_states','params']
    old_methods=methods(S/'factor_runtime_3060_reference17b_v1.py',fn_names)
    new_methods=methods(O/'factor_runtime_3060_reference17b_v1.py',fn_names)
    old_audit=methods(MOD/'nominal_parameter_audit.py',['parameter_audit'])['parameter_audit']
    for n in (80,88):
        for seed in (20261002,20261003):
            os.environ['RM_DR_OFF']='1';os.environ['RM_MILD_DR_PROFILE']='nominal'
            env,values=fixture(n,seed,False)
            # Old legacy uniform-COM and unconditional metadata failures are retained.
            failures=dict(old_params=rejection(lambda:old_methods['params'](env)),
                          old_private_rng=rejection(lambda:old_methods['private_rng'](env)),
                          old_uniform_COM_nominal_audit=rejection(lambda:old_audit(env)))
            ref=helper.capture_nominal_d0_reference(env)
            pre=new_methods['private_rng'](env)
            failures['old_gas_hook']=rejection(lambda:class_(MOD/'gas_damping_sdk_adapter.py','GasDampingSDK').install_expected_value_auditors(env._gas_damping))
            failures['old_COM_hook']=rejection(lambda:class_(MOD/'chassis_com_pose_roundtrip_sdk_adapter.py','ChassisCOMSDK').install_expected_value_auditor(env._chassis_com))
            failures['old_PD_hook']=rejection(lambda:class_(MOD/'explicit_pd_sdk_adapter.py','ExplicitPDSDK').install_expected_value_auditor(env._explicit_pd))
            for obj,method in ((env._gas_damping,'install_expected_value_auditors'),(env._chassis_com,'install_expected_value_auditor'),(env._explicit_pd,'install_expected_value_auditor')):
                getattr(obj,method)()
            assert env._spring_pressure.audit()['D6_gas_damping_varies_separately']
            assert torch.equal(env._spring_pressure.initial_other['damping'],env._gas_damping.original_damping)
            audit=helper.parameter_audit(env)
            assert audit['actual_parameters_pass'] and not hasattr(env,'_mild_dr')
            metadata=new_methods['params'](env)
            assert all(metadata[k] is None for k in ('mild_factor','mild_nominal','mild_mu','mild_outputs'))
            assert not any(k.startswith('_mild_dr/') for k in metadata['actual_captured_RNG_bytes'])
            assert pre==new_methods['private_rng'](env)
            negatives=[]
            for key in ('mass','inertia','materials'):
                old=values[key].clone();values[key].add_(.01)
                negatives.append(dict(case='all_clones_'+key+'_changed',**rejection(lambda:helper.parameter_audit(env))))
                values[key].copy_(old)
            for motor in ('legs','wheels'):
                for key in ('episode_scale','step_scale'):
                    t=getattr(env.scene['robot'].actuators[motor],key);t[0]=.99
                    negatives.append(dict(case=motor+'_'+key,**rejection(lambda:helper.parameter_audit(env))));t[0]=1.
            for name,t in (('COM_actual',values['pose']),('COM_buffer',env.scene['robot'].data.body_com_pose_b),
                           ('PD_legkp',env._explicit_pd.legs.stiffness),('PD_wheelkd',env._explicit_pd.wheels.damping),
                           ('D6_actual_damping',values['damping']),('D5_actual_stiffness',values['stiffness'])):
                old=t.clone();t.reshape(-1)[6 if name.startswith(('D5_','D6_')) else 0]+=.01
                negatives.append(dict(case=name,**rejection(lambda:helper.parameter_audit(env))));t.copy_(old)
            os.environ['RM_MILD_DR_PROFILE']='white_v2'
            negatives.append(dict(case='absent_MildDR_outside_nominal',**rejection(lambda:helper.parameter_audit(env))))
            os.environ['RM_MILD_DR_PROFILE']='nominal';os.environ['RM_DR_OFF']='0'
            negatives.append(dict(case='legacy_DR_not_disabled',**rejection(lambda:helper.parameter_audit(env))))
            os.environ['RM_DR_OFF']='1'
            assert helper.parameter_audit(env)['actual_parameters_pass']
            assert all(torch.equal(ref[k],values[k]) for k in ref)
            assert pre==new_methods['private_rng'](env), 'Audits/negative fixtures consumed a generator'
            # Both white profiles keep original metadata bytes and hook behavior.
            white=[]
            for profile in ('white_v2','white_v3'):
                os.environ['RM_MILD_DR_PROFILE']=profile
                e,_=fixture(n,seed,True)
                assert old_methods['params'](e)==new_methods['params'](e)
                assert old_methods['private_rng'](e)==new_methods['private_rng'](e)
                for filename,classname,method,attr in (
                    ('gas_damping_sdk_adapter.py','GasDampingSDK','install_expected_value_auditors','_gas_damping'),
                    ('chassis_com_pose_roundtrip_sdk_adapter.py','ChassisCOMSDK','install_expected_value_auditor','_chassis_com'),
                    ('explicit_pd_sdk_adapter.py','ExplicitPDSDK','install_expected_value_auditor','_explicit_pd')):
                    x,_=fixture(n,seed,True);y,_=fixture(n,seed,True)
                    class_(MOD/filename,classname).__dict__[method](getattr(x,attr))
                    class_(O/filename,classname).__dict__[method](getattr(y,attr))
                    assert x._mild_dr.audit()==y._mild_dr.audit()
                assert helper.parameter_audit(e)==e._mild_dr.audit()
                white.append(dict(profile=profile,metadata_RNG_and_three_audit_wrappers_original_exact=True))
            rows.append(dict(n=n,seed=seed,old_rejections=failures,new_nominal_metadata_and_original_D5_D6_D7_audits_passed=True,
                             negative_cases=negatives,white_profiles=white,no_generator_draw_or_fake_MildDR=True))
    # Spring constructor audit registration: actual AST with a disclosed parent fixture.
    spring_results=[]
    class ParentFixture:
        def __init__(self,env):
            self.__dict__.update(vars(env._spring_pressure));self.env=env
    for white in (False,True):
        os.environ['RM_DR_OFF']='1';os.environ['RM_MILD_DR_PROFILE']='white_v3' if white else 'nominal'
        e,_=fixture(80,20261002,white)
        oldcls=class_(MOD/'spring_pressure_audit_runtime.py','SpringPressureSDK',OriginalPressureSDK=ParentFixture)
        newcls=class_(O/'spring_pressure_audit_runtime.py','SpringPressureSDK',OriginalPressureSDK=ParentFixture)
        if white:
            x,_=fixture(80,20261002,True);y,_=fixture(80,20261002,True)
            oldcls(x);newcls(y);assert x._mild_dr.audit()==y._mild_dr.audit()
            spring_results.append(dict(white=True,original_wrapper_result_exact=True))
        else:
            failure=rejection(lambda:oldcls(e));newcls(e)
            assert hasattr(e,helper.REFERENCE_ATTRIBUTE) and not hasattr(e,'_mild_dr')
            spring_results.append(dict(white=False,old_rejection=failure,new_actual_AST_registration_passed_parent_is_fixture=True))
    for key,value in original_env.items():
        if value is None:os.environ.pop(key,None)
        else:os.environ[key]=value
    assert torch.equal(original_rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    for row in manifest['candidates']:assert H(row['original'])==row['original_SHA']
    result=dict(epoch=time.time(),passed=True,source_inverse_AST=inverse,actual_CPU_fixtures=rows,
                spring_constructor_parent_fixture_results=spring_results,
                global_CPU_RNG_unchanged=True,CUDA_initialized=False,optimizer_updates=0,
                all_original_source_and_physical_setter_reset_sampler_hardware_methods_unchanged=True,
                gas_to_spring_overlay_retained_and_original_nominal_reference_restored=True,
                no_fake_MildDR_factor_mask_RNG=True,
                scope='Real saved source audit methods on CPU tensor/SDK readback fixtures and inverse AST; no full SDK constructor/target readback or physical control certified.',
                target_CPU_native_or_GPU_admission=False,nominal_scope_not_dispatched=True,
                no_PPO_budget_S8_jump_or_second_gate_authorization=True)
    with path.open('x',encoding='utf8') as f:json.dump(result,f,indent=2,allow_nan=False)
    print(json.dumps(dict(passed=True,fixtures=len(rows),strict_negative_cases=sum(len(x['negative_cases']) for x in rows),source_inverse_exact=len(inverse),no_GPU_or_target_admission=True)))


if __name__=='__main__':
    try:run()
    except BaseException:
        with (R/('NOMINAL_CPU_REVIEW_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc(),no_GPU_network_PPO_budget=True),f,indent=2)
        raise
