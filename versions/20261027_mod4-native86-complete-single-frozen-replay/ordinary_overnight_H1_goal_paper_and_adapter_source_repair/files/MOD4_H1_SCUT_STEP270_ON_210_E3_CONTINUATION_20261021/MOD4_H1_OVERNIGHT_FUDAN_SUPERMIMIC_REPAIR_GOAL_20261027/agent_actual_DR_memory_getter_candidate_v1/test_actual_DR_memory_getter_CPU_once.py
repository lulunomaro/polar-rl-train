"""Real pure components + labeled duck environment memory; no SDK admission."""
from pathlib import Path
from types import SimpleNamespace as S
import sys,json,traceback,hashlib,datetime
import torch
import actual_DR_memory_getter_v1 as g
D=Path(__file__).resolve().parent;T=D.parent.parent
R=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2/job0/runtime/isaac/mod4'
sys.path.insert(0,str(R))
from chassis_com_component import ChassisCOM
from explicit_pd_component import ExplicitPD
from spring_pressure_component import SpringPressure
from gas_damping_factor import GasDamping
from sensor_mild_math import SensorCorruption
from action_delay_physics_queue import PhysicsActionQueue
rows=[]
def yes(v):assert bool(v)
def case(name,fn):
    try:rows.append(dict(name=name,passed=True,detail=fn()))
    except Exception:rows.append(dict(name=name,passed=False,traceback=traceback.format_exc()))
def rejects(fn):
    try:fn()
    except (ValueError,AttributeError,KeyError):return True
    raise AssertionError('Expected strict rejection')

def fixture():
    n=3;body=('chassis',)+tuple('body'+str(i) for i in range(1,31));joint=tuple('j'+str(i) for i in range(30))
    binding=g.RuntimeOrderBinding(body,joint,joint[:4],joint[4:6],joint[6:8],5)
    pd=ExplicitPD(n,'cpu',11,True);com=ChassisCOM(n,'cpu',12,True)
    spring=SpringPressure(n,'cpu',13);gas=GasDamping(n,'cpu',14);sensor=SensorCorruption(n,'cpu',15,'noise_bias_mild_v1')
    q=PhysicsActionQueue(n,'cpu',16)
    data=S(joint_armature=torch.full((n,30),.002),joint_friction_coeff=torch.full((n,30),.003),
           joint_stiffness=torch.zeros(n,30),joint_damping=torch.zeros(n,30))
    actuators=dict(legs=S(joint_indices=list(range(4)),episode_scale=torch.ones(n,4),step_scale=torch.ones(n,4),stiffness=torch.zeros(n,4),damping=torch.zeros(n,4)),
       wheels=S(joint_indices=[4,5],episode_scale=torch.ones(n,2),step_scale=torch.ones(n,2),stiffness=torch.zeros(n,2),damping=torch.zeros(n,2)),
       gas_springs=S(joint_indices=[6,7]))
    original=torch.zeros(n,31,7);original[:,:,6]=1;original[:,:,0]=.001
    dr=S(factor=torch.ones(n),mass=torch.arange(1,32,dtype=torch.float32)[None].expand(n,-1).clone(),
         inertia=torch.ones(n,31,9)*.02,materials=torch.ones(n,5,3)*.2,mu=torch.full((n,),.9),
         reset_count=torch.zeros(n,dtype=torch.int64),wheel_shapes=[1,3])
    env=S(num_envs=n,device='cpu',scene={'robot':S(body_names=list(body),joint_names=list(joint),actuators=actuators,data=data)},
       cfg=S(events=S(gas_spring_preload=S(params={'joint_names':list(joint[6:8]),'targets':[.2206,.2206]}))),
       _mild_dr=dr,_chassis_com=S(body_id=0,original_pose=original,component=com),
       _explicit_pd=S(component=pd,leg_ids=[0,1,2,3],wheel_ids=[4,5]),
       _spring_pressure=S(component=spring,nominal=torch.tensor([3500.,3500.]),ids=[6,7],names=list(joint[6:8])),
       _gas_damping=S(component=gas,ids=[6,7]),_sensor_mild=sensor,
       _physics_action_delay=S(queue=q),action_manager=S(action=torch.full((n,6),12345.)))
    neutral=torch.arange(n*6,dtype=torch.float32).reshape(n,6)*.01
    def reset(ids):
        dr.reset_count[ids]+=1;dr.factor[ids]=.95+.01*dr.reset_count[ids].float()
        dr.mu[ids.cpu()]=.7+.01*dr.reset_count[ids].cpu().float()
        for key,width in [('legs',4),('wheels',2)]:
            actuators[key].episode_scale[ids]=1+torch.arange(width)[None]*.01+dr.reset_count[ids,None]*.001
        for component in (pd,com,spring,gas,sensor):component.reset(ids)
        coeff=pd.coefficients();actuators['legs'].stiffness.copy_(coeff['leg_kp']);actuators['legs'].damping.copy_(coeff['leg_kd']);actuators['wheels'].damping.copy_(coeff['wheel_kd'])
        data.joint_stiffness[:,[6,7]]=spring.actual_stiffness(env._spring_pressure.nominal)
        data.joint_damping[:,[6,7]]=gas.actual_damping_Ns_per_m()
        q.reset('legs',ids,neutral[:,:4]);q.reset('wheels',ids,neutral[:,4:])
    reset(torch.arange(n))
    return env,binding,reset,neutral

def mapping():
    e,b,reset,neutral=fixture();reader=g.ActualDRMemoryGetter(e,b);v=reader.capture_initial()
    yes(tuple(v)==g.FIELD_NAMES);yes(v['motor_episode_scale'].shape==(3,6))
    yes(torch.equal(v['body_mass'],e._mild_dr.mass*e._mild_dr.factor[:,None]))
    yes(torch.equal(v['body_inertia'],e._mild_dr.inertia*e._mild_dr.factor[:,None,None]))
    yes(torch.equal(v['body_com'][:,0],e._chassis_com.original_pose[:,0,:3]+e._chassis_com.component.delta_m))
    yes(torch.equal(v['joint_stiffness'][:,:4],e._explicit_pd.component.coefficients()['leg_kp']))
    yes(bool((e.scene['robot'].data.joint_stiffness[:,:4]==0).all()))
    yes(torch.equal(v['material_static_friction'][:,[1,3]],e._mild_dr.mu[:,None].expand(-1,2)))
    yes(bool((v['material_restitution'][:,[1,3]]==0).all()));yes(bool((v['material_restitution'][:,[0,2,4]]==.2).all()))
    return dict(fields=14,motor_dim=6,xi_dim=reader.xi().shape[-1],original_components=['ChassisCOM','ExplicitPD','SpringPressure','GasDamping','SensorCorruption','PhysicsActionQueue'],D0='duck memory reproduces pinned MildDR attrs, not an SDK instance')
case('all14_source_memory_mappings',mapping)

def reset_cache():
    e,b,reset,_=fixture();reader=g.ActualDRMemoryGetter(e,b);reader.capture_initial();before=reader.xi().clone()
    oldrows=reader.friction_transfer_rows
    yes(reader.refresh_after_resets()['updated']==0);yes(reader.friction_transfer_rows==oldrows)
    reset(torch.tensor([1]));yes(torch.equal(reader.reset_ids_since_capture(),torch.tensor([1])))
    row=reader.refresh_after_resets(torch.tensor([1]));yes(row['friction_transfer_rows']==1)
    yes(torch.equal(before[[0,2]],reader.xi()[[0,2]]));yes(not torch.equal(before[1],reader.xi()[1]))
    return dict(no_reset_no_friction_transfer=True,selected_friction_transfer_rows=1,nonreset_xi_cached_exact=True)
case('selected_reset_detector_cache_only_changed_rows',reset_cache)

def old_applied():
    e,b,_,neutral=fixture();yes(torch.equal(g.read_old_processed_applied(e,0),neutral))
    q=e._physics_action_delay.queue;target=-neutral-2
    for key,sl in [('legs',slice(0,4)),('wheels',slice(4,6))]:
        q.submit(key,target[:,sl],0)
        for tick in range(4):q.apply(key,tick)
    actual=g.read_old_processed_applied(e,4)
    yes(torch.equal(actual,target));yes(not torch.equal(actual,e.action_manager.action))
    return dict(uses_original_queue_applied_not_policy_action=True)
case('dynamic_old_applied_at_control_boundary',old_applied)

def negative(change,action='capture'):
    e,b,reset,_=fixture();r=g.ActualDRMemoryGetter(e,b)
    if action=='reset':
        r.capture_initial();before=r.xi().clone();change(e,reset)
        rejects(r.refresh_after_resets);yes(torch.equal(before,r.xi()));return dict(failed_update_atomic=True)
    change(e,reset)
    return rejects(r.capture_initial)
case('missing_mu_rejected',lambda:negative(lambda e,r:delattr(e._mild_dr,'mu')))
case('motor2_instead_of6_rejected',lambda:negative(lambda e,r:setattr(e.scene['robot'].actuators['legs'],'episode_scale',torch.ones(3,1))))
case('wrong_body_order_rejected',lambda:negative(lambda e,r:e.scene['robot'].body_names.reverse()))
case('wrong_gas_order_rejected',lambda:negative(lambda e,r:e.cfg.events.gas_spring_preload.params['joint_names'].reverse()))
case('nonfinite_factor_rejected',lambda:negative(lambda e,r:e._mild_dr.factor.fill_(float('nan'))))
case('dynamic_step_gain_rejected',lambda:negative(lambda e,r:e.scene['robot'].actuators['legs'].step_scale.fill_(.99)))
case('PD_model_factor_disagreement_rejected',lambda:negative(lambda e,r:e.scene['robot'].actuators['legs'].stiffness.add_(1)))
case('D5_buffer_factor_disagreement_rejected',lambda:negative(lambda e,r:e.scene['robot'].data.joint_stiffness.__setitem__((slice(None),[6,7]),0)))
case('incomplete_reset_chain_rejected',lambda:negative(lambda e,r:e._mild_dr.reset_count.add_(1),'reset'))
case('missed_multiple_resets_rejected',lambda:negative(lambda e,r:(r(torch.tensor([1])),r(torch.tensor([1]))),'reset'))
def pending():
    e,_,_,_=fixture();q=e._physics_action_delay.queue;q.submit('legs',torch.ones(3,4),0)
    return rejects(lambda:g.read_old_processed_applied(e,0))
case('pending_dynamic_queue_rejected',pending)
def count_atomic():
    def change(e,reset):reset(torch.tensor([1]));e._mild_dr.mu[1]=float('nan')
    return negative(change,'reset')
case('failed_reset_read_does_not_publish_partial_cache',count_atomic)

report=dict(schema='mod4.actual_DR_memory_getter.source_component_CPU.v1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    passed=all(x['passed'] for x in rows),passed_count=sum(x['passed'] for x in rows),total=len(rows),tests=rows,
    actual_SDK_admitted=False,duck_environment_fixture=True,original_pure_components_CPU=True,
    no_actor_WM_PT_raw_physics_setter_SDK_start_GPU_SSH_Git=True,
    module_SHA=hashlib.sha256((D/'actual_DR_memory_getter_v1.py').read_bytes()).hexdigest())
with (D/'ACTUAL_DR_MEMORY_GETTER_CPU_V1_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2,ensure_ascii=False)
print(json.dumps(dict(passed=report['passed'],passed_count=report['passed_count'],total=report['total'])))
if not report['passed']:sys.exit(1)
