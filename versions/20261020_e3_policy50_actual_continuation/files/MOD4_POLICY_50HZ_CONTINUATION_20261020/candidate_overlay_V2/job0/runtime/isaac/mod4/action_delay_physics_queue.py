"""D4 component: target transitions delayed on actual 2.5ms physics apply ticks.

Values are already processed position/velocity targets. The caller retains the
original scale, offset, coherent four-leg CAD projection and actuator limits.
This module has no Isaac imports and is not a production training entry.
"""
import torch

WIDTHS={'legs':4,'wheels':2}
FIELDS=('lag_steps','episode','pending','pending_valid','issued_tick','due_tick',
        'applied','applied_valid','applied_issue_tick','first_apply_tick',
        'last_submit_tick','last_apply_tick')

class PhysicsActionQueue:
    def __init__(self,n,device,seed,enabled=True,physics_us=2500,control_us=20000):
        assert isinstance(n,int) and n>0 and physics_us==2500 and control_us in (10000,20000)
        self.n=n;self.device=torch.device(device);self.enabled=bool(enabled)
        self.physics_us=physics_us;self.control_us=control_us;self.groups={};self.rng={}
        for key,width in WIDTHS.items():
            self.rng[key]=torch.Generator(device=self.device).manual_seed(int(seed)+(2100037 if key=='legs' else 3100097))
            vector=lambda:torch.zeros((n,width),device=self.device,dtype=torch.float32)
            integer=lambda value=0:torch.full((n,),value,device=self.device,dtype=torch.long)
            flag=lambda:torch.zeros(n,device=self.device,dtype=torch.bool)
            self.groups[key]=dict(lag_steps=integer(),episode=integer(),pending=vector(),pending_valid=flag(),issued_tick=integer(-1),due_tick=integer(-1),applied=vector(),applied_valid=flag(),applied_issue_tick=integer(-1),first_apply_tick=integer(-1),last_submit_tick=integer(-1),last_apply_tick=integer(-1))

    def _input(self,key,x):
        assert key in WIDTHS and torch.is_tensor(x) and x.shape==(self.n,WIDTHS[key])
        assert x.device==self.device and x.dtype==torch.float32 and bool(torch.isfinite(x).all())

    def _tick(self,tick):
        assert isinstance(tick,int) and not isinstance(tick,bool) and tick>=0
        return tick

    def reset(self,key,ids,neutral,new_scene_clock=False):
        self._input(key,neutral)
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long)
        assert ids.ndim==1 and len(torch.unique(ids))==len(ids) and bool(((ids>=0)&(ids<self.n)).all())
        if new_scene_clock:assert len(ids)==self.n,'Only a complete new scene can rebase physics timing'
        if not len(ids):return
        g=self.groups[key]
        g['lag_steps'][ids]=torch.randint(0,3,(len(ids),),device=self.device,generator=self.rng[key]) if self.enabled else 0
        g['episode'][ids]+=1
        for field in ('pending','applied'):g[field][ids]=neutral[ids]
        for field in ('pending_valid','applied_valid'):g[field][ids]=False
        for field in ('issued_tick','due_tick','applied_issue_tick','first_apply_tick','last_submit_tick'):g[field][ids]=-1
        if new_scene_clock:g['last_apply_tick'][ids]=-1

    def submit(self,key,x,tick):
        self._input(key,x);tick=self._tick(tick);g=self.groups[key]
        old=g['last_submit_tick'];repeat=old==tick;due=~repeat
        if bool(repeat.any()):assert torch.equal(g['pending'][repeat],x[repeat]),'Different command submitted at same policy decision'
        if bool(due.any()):
            assert bool(((old[due]<0)|((tick-old[due])*self.physics_us==self.control_us)).all()),'Skipped or reversed policy command clock'
            assert bool((g['last_apply_tick'][due]<tick).all()),'Submission occurred after physical application'
            assert not bool(g['pending_valid'][due].any()),'Previous command never reached actuator'
            g['pending'][due]=x[due];g['pending_valid'][due]=True
            g['issued_tick'][due]=tick;g['due_tick'][due]=tick+g['lag_steps'][due]
            g['last_submit_tick'][due]=tick

    def apply(self,key,tick):
        assert key in WIDTHS;tick=self._tick(tick);g=self.groups[key]
        old=g['last_apply_tick'];repeat=old==tick;advance=~repeat
        assert bool(((old[advance]<0)|(old[advance]==tick-1)).all()),'Skipped or reversed physical apply callback'
        select=advance & g['pending_valid'] & (g['due_tick']<=tick)
        if bool(select.any()):
            assert bool((g['due_tick'][select]==tick).all()),'Command first application was late'
            g['applied'][select]=g['pending'][select]
            g['applied_valid'][select]=True;g['applied_issue_tick'][select]=g['issued_tick'][select]
            g['first_apply_tick'][select]=tick;g['pending_valid'][select]=False
        g['last_apply_tick'][advance]=tick
        return g['applied'].clone()

    def receipt(self,key,tick):
        tick=self._tick(tick);g=self.groups[key]
        assert bool((g['last_apply_tick']==tick).all())
        first_latency=torch.where(g['applied_valid'],(g['first_apply_tick']-g['applied_issue_tick'])*self.physics_us,-1)
        sample_age=torch.where(g['applied_valid'],(tick-g['applied_issue_tick'])*self.physics_us,-1)
        return dict(physics_period_us=self.physics_us,control_period_us=self.control_us,requested_delay_us=g['lag_steps'].clone()*self.physics_us,actual_first_transition_delay_us=first_latency,held_command_sample_age_us=sample_age,actual_apply_tick=tick,command_issue_tick=g['applied_issue_tick'].clone(),valid_policy_command=g['applied_valid'].clone(),neutral_reset_hold=~g['applied_valid'],same_group_targets_coherent=True)

    def state_dict(self):
        return dict(version=1,n=self.n,enabled=self.enabled,physics_us=self.physics_us,control_us=self.control_us,rng={k:g.get_state().clone() for k,g in self.rng.items()},groups={k:{f:v.clone() for f,v in g.items()} for k,g in self.groups.items()})

    def validate_state(self,state):
        assert state['version']==1 and state['n']==self.n and state['enabled']==self.enabled and state['physics_us']==2500 and state['control_us']==self.control_us
        assert set(state['groups'])==set(state['rng'])==set(WIDTHS)
        for key,width in WIDTHS.items():
            g=state['groups'][key];assert set(g)==set(FIELDS)
            for field,v in g.items():
                expected=(self.n,width) if field in ('pending','applied') else (self.n,)
                dtype=torch.float32 if len(expected)==2 else torch.bool if field.endswith('_valid') else torch.long
                assert torch.is_tensor(v) and v.shape==expected and v.dtype==dtype and bool(torch.isfinite(v).all()),field
            assert bool(((g['lag_steps']>=0)&(g['lag_steps']<=2)).all()) and bool((g['episode']>=0).all())
            if not self.enabled:assert not bool(g['lag_steps'].any())
            assert all(bool((g[field]>=-1).all()) for field in FIELDS if g[field].dtype==torch.long)
            pending=g['pending_valid'];applied=g['applied_valid']
            assert bool((g['due_tick'][pending]==g['issued_tick'][pending]+g['lag_steps'][pending]).all())
            assert bool((g['issued_tick'][pending]==g['last_submit_tick'][pending]).all())
            assert bool((g['due_tick'][pending]>g['last_apply_tick'][pending]).all())
            latency=g['first_apply_tick'][applied]-g['applied_issue_tick'][applied]
            assert bool(((latency>=0)&(latency<=2)).all()) and bool((g['first_apply_tick'][applied]<=g['last_apply_tick'][applied]).all())
            assert bool((g['applied_issue_tick'][applied]>=0).all())
            generator=torch.Generator(device=self.device);generator.set_state(state['rng'][key].cpu())
        return True

    def load_state_dict(self,state):
        self.validate_state(state)
        self.groups={k:{f:v.to(self.device).clone() for f,v in g.items()} for k,g in state['groups'].items()}
        for key,generator in self.rng.items():generator.set_state(state['rng'][key].cpu())

    def recipe(self):
        return dict(profile='physical_target_0_2500_5000us_v1' if self.enabled else 'off',physics_period_us=2500,control_period_us=self.control_us,actual_transition_delay_us=[0,2500,5000] if self.enabled else [0],sub_ms_exact_timing_claimed=False,leg_four_targets_coherent=True,wheel_two_targets_coherent=True,leg_and_wheel_per_environment_episode_RNG_independent=True,queue_values='Original processed joint-position rad / joint-velocity rad_s targets',original_scale_offset_CAD_guard_and_gain_after_torque_speed_envelope_unchanged=True,reset_initial_target='Caller real default leg q and zero wheel velocity; stale commands cleared',holding_age_is_distinct_from_first_transition_latency=True,engineering_pressure_not_hardware_calibration=True,CPU_component_not_actual_SDK_or_learning=True)
