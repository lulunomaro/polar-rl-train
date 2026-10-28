"""Source-only MOD4 native bridge for explicit dynamic54 / static31.

Original vec.step action object and output are preserved; terminal state comes
from the original trace's pre-reset snapshot. This is not a deployed worker.
"""
from dataclasses import dataclass
import torch
from actual_DR_memory_getter_v1 import ActualDRMemoryGetter, read_old_processed_applied
from static_dynamic_delay_contract_v1 import pack_dynamic_aux
from compact_episode_static31_v1 import compact_static_snapshot
from supermimic_wheel_leg_v3.geometry import unflatten_state
from supermimic_wheel_leg_v3.contract import SUPERMIMIC_STATE_KEY, SUPERMIMIC_TRANSITION_KEY

@dataclass
class NativeBridgeState:
    info: dict
    reward: torch.Tensor
    terminated: torch.Tensor
    truncated: torch.Tensor
    obs: dict

class CompactStatic31Cache:
    def __init__(self, env, binding):
        self.env=env
        self.reader=ActualDRMemoryGetter(env,binding)
        self.cache=None
    def _project(self):
        e=self.env;pd=e._explicit_pd;dr=e._mild_dr
        self.cache=compact_static_snapshot(self.reader.snapshot(),
            nominal_mass=dr.mass,nominal_inertia=dr.inertia,
            original_body_com=e._chassis_com.original_pose[...,:3],
            body_id=e._chassis_com.body_id,
            leg_ids=pd.leg_ids,wheel_ids=pd.wheel_ids,
            gas_ids=e._spring_pressure.ids,wheel_shape_ids=dr.wheel_shapes,
            nominal_gas_stiffness=e._spring_pressure.nominal)
    def capture_initial(self):
        self.reader.capture_initial();self._project()
        return self.xi()
    def refresh_after_resets(self,ids):
        previous=self.cache
        row=self.reader.refresh_after_resets(ids)
        if row['updated']:
            self._project()
            selected=torch.zeros(self.env.num_envs,device=self.env.device,dtype=torch.bool)
            selected[ids]=True
            if not torch.equal(previous[~selected],self.cache[~selected]):
                raise ValueError('nonreset static31 changed')
        return row
    def xi(self):
        if self.cache is None:raise ValueError('static31 initial capture missing')
        return self.cache.clone()

class NativeWheelLegBridge:
    def __init__(self, runner, trace, mdp, runtime_order_binding, before_action_hook):
        if not callable(before_action_hook):
            raise ValueError('original fullsave/trace/deadline before-action hook required')
        self.runner=runner;self.vec=runner.env;self.real=self.vec.unwrapped
        self.trace=trace;self.mdp=mdp;self.pre_action_hook=before_action_hook
        self.num_envs=self.real.num_envs;self.device=torch.device(self.real.device)
        if self.real.physics_dt!=.0025 or self.real.step_dt!=.01 or self.real.cfg.decimation!=4:
            raise ValueError('original 2.5ms/100Hz/decimation4 required')
        if mdp.num_joints!=30 or mdp.auxiliary_dim!=54 or mdp.packed_state_dim!=127 or mdp.context_dim!=31 or mdp.action_dim!=6:
            raise ValueError('explicit physical30/dynamic54/static31/action6 MDP required')
        self.static=CompactStatic31Cache(self.real,runtime_order_binding)
        self.static.capture_initial()
        self.ep_step=torch.zeros(self.num_envs,device=self.device,dtype=torch.int32)
        self.state=None
        self._pre_reset_hook_installed=False
        self._terminal_aux54=None

    @property
    def supermimic_mdp(self):return self.mdp

    def install_exact_pre_reset_aux_hook(self):
        if self._pre_reset_hook_installed:
            raise ValueError('duplicate native pre-reset auxiliary hook')
        old=self.real.termination_manager.compute
        bridge=self
        def compute(*args,**kwargs):
            result=old(*args,**kwargs)
            frame=bridge.trace.frame
            if frame is None:
                raise ValueError('original complete pre-reset trace frame missing')
            # Reuse the original copies of contact/torque; only queue memory is new.
            applied=read_old_processed_applied(bridge.real,int(bridge.real._sim_step_counter))
            bridge._terminal_aux54=pack_dynamic_aux(
                frame['history5ms'],frame['applied_torque'],applied)
            return result
        self.real.termination_manager.compute=compute
        self._pre_reset_hook_installed=True

    @torch.inference_mode()
    def pack(self,root,joint,velocity,aux):
        root=root.detach().clone()
        root[:,:3]-=self.real.scene.env_origins
        # Actual SDK root_state_w xyzw -> native wxyz, already source-verified.
        root[:,3:7]=root[:,[6,3,4,5]]
        value=torch.cat((root,joint.detach(),velocity.detach(),aux.detach()),-1)
        if value.shape!=(self.num_envs,127) or not torch.isfinite(value).all():
            raise ValueError('invalid physical73+dynamic54 packed state')
        return value

    @torch.inference_mode()
    def current(self):
        e=self.real;r=e.scene['robot']
        aux=pack_dynamic_aux(e._integrated_contact.history,r.data.applied_torque,
                            read_old_processed_applied(e,int(e._sim_step_counter)))
        return self.pack(r.data.root_state_w,r.data.joint_pos,r.data.joint_vel,aux),self.static.xi()

    def init_state(self):
        if not self._pre_reset_hook_installed:
            raise ValueError('mandatory pre-reset state capture hook missing')
        s,xi=self.current();zero=torch.zeros(self.num_envs,device=self.device)
        self.state=NativeBridgeState(info={SUPERMIMIC_STATE_KEY:dict(
            s=s,xi=xi,f=self.real.h1_phase.age_control.clone(),
            a_prev=torch.zeros(self.num_envs,6,device=self.device),ep_step=self.ep_step.clone())},
            reward=zero,terminated=zero.bool(),truncated=zero.bool(),obs={})
        return self.state

    def before_action(self):
        return self.pre_action_hook()

    @torch.inference_mode()
    def step(self,actions):
        if self.state is None:raise ValueError('init_state required before native step')
        old=self.state.info[SUPERMIMIC_STATE_KEY]
        self._terminal_aux54=None
        try:
            # Exact original incoming object, values and original vec.step behavior.
            output=self.vec.step(actions)
            _,physical_reward,done,_=output
            frame=self.trace.frame
            if frame is None or self._terminal_aux54 is None:
                raise ValueError('mandatory terminal pre-reset auxiliary state missing')
            s1=self.pack(frame['root13'],frame['q30'],frame['joint_velocity'],self._terminal_aux54)
            done=done.bool()
            applied_ingress=frame['executed6'].detach().clone()
            # The native tracking head must agree on real and imagined state.
            # Original V8 RewardManager still runs and remains in the full trace.
            native_reward=self.mdp.reward(unflatten_state(s1),old['f']+1,
                                           applied_ingress,old['a_prev']).detach()
            if native_reward.shape!=(self.num_envs,) or not torch.isfinite(native_reward).all():
                raise ValueError('invalid real native tracking reward')
            transition=dict(s=old['s'],s1=s1,a=applied_ingress,
                a_prev=old['a_prev'],xi=old['xi'],r=native_reward,f=old['f'],
                ep_step=old['ep_step'],done=done)
            if bool(done.any()):
                self.static.refresh_after_resets(torch.where(done)[0])
            s,xi=self.current()
            self.ep_step=torch.where(done,0,self.ep_step+1).to(torch.int32)
            previous=applied_ingress.clone();previous[done]=0
            self.state=NativeBridgeState(info={
                SUPERMIMIC_STATE_KEY:dict(s=s,xi=xi,f=self.real.h1_phase.age_control.clone(),
                                         a_prev=previous,ep_step=self.ep_step.clone()),
                SUPERMIMIC_TRANSITION_KEY:transition,
                'physical_V8_reward_snapshot':physical_reward.detach()},
                reward=native_reward,terminated=done,truncated=torch.zeros_like(done),obs={})
            return self.state
        finally:
            self._terminal_aux54=None

