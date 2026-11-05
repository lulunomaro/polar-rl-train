"""Independent LOW80 confirmation: five existing low-rise poses, sixteen rows each.

Install the unchanged training overlay first.  Only recipe allocation and passive
endpoint caches differ; the overlay's update math, reset, rewards and physics stay
in force.  This scope has denominator 80 and is not the original 74-case grader.
The seven flags and eight metrics are sampled by the existing phase update,
using its existing locals/contact read, before any framework episode reset.
"""
import torch
import e3_fudan_task_runtime_v1 as overlay

LOW80_SCOPE = 'LOW80_INDEPENDENT_FIVE_POSE16_CONFIRM_V1'
LOW80_NUM_ENVS = 80
LOW80_FLAG_COLUMNS = (
    'height_ok', 'upright_ok', 'speed_ok', 'angular_ok',
    'wheels_ok', 'chassis_ok', 'joint_good',
)
LOW80_METRIC_COLUMNS = (
    'height_m', 'gravity_z', 'root_speed_m_s', 'angular_speed_rad_s',
    'wheel0_force_N', 'wheel1_force_N', 'chassis_force_N', 'upright',
)
_INSTALLED = False


def install_before_build():
    global _INSTALLED
    assert not _INSTALLED, 'one install in a new own process'
    _INSTALLED = True
    overlay.install_before_build()
    import e3_recovery_runtime_v1 as old
    from h1_fullstate_environment_v1 import tensor
    BasePhase = old.RecoveryPhase

    class Low80ConfirmationPhase(BasePhase):
        def __init__(self, n, device):
            assert n == LOW80_NUM_ENVS, 'LOW80 requires exactly eighty environments'
            super().__init__(n, device)
            self.recipe.copy_(13 + torch.arange(n, device=device, dtype=torch.long) % 5)
            self.low80_last_flags = torch.zeros((n, 7), device=device, dtype=torch.bool)
            self.low80_last_metrics = torch.zeros((n, 8), device=device, dtype=torch.float32)

        def update(self,gravity_z,root_speed,angular_speed):
            upright=((1-gravity_z)/2).clamp(0,1);low=self.recipe>=13;env=self.env;assert env is not None
            root=tensor(env.scene['robot'].data.root_state_w);height=root[:,2]-env.scene.env_origins[:,2];rise=((height-.1781)/(.25-.1781)).clamp(0,1);potential=torch.where(low,.5*upright+.5*upright*rise,upright);self.peak.copy_(torch.where(low&self.needs_initial,potential,self.peak));self.needs_initial.zero_();now=torch.where(self.request,torch.maximum(self.peak,potential),self.peak);self.delta.copy_(now-self.peak);self.peak.copy_(now)
            # Fixed-size passive evidence: reuse this update's already-read height and low mask.
            self.low_episode_peak_height.copy_(torch.where(low,torch.maximum(self.low_episode_peak_height,height),self.low_episode_peak_height))
            self.low_rollout_summary[:3].add_(torch.stack((low.sum(dtype=torch.float64),torch.where(low,height,0.).sum(dtype=torch.float64),(low&(height>=.23)).sum(dtype=torch.float64))))
            good=(gravity_z<-.984807753)&(root_speed<.03)&(angular_speed<.2)&self.request
            if bool(low.any()):
                force=tensor(env.scene.sensors['full_robot_contact'].contact_view.get_net_contact_forces(dt=float(env.physics_dt))).reshape(self.n,31,3).norm(dim=-1);wheel=force[:,env.e3_wheels];base=force[:,env.e3_contact_names.index('chassis')];good&=~low|((height>=.23)&(wheel>1.).all(-1)&(base<1.))
                self.low_criterion_summary.add_(torch.stack((
                    (low&(height>=.23)).sum(dtype=torch.float64),
                    (low&(gravity_z<-.984807753)).sum(dtype=torch.float64),
                    (low&(root_speed<.03)).sum(dtype=torch.float64),
                    (low&(angular_speed<.2)).sum(dtype=torch.float64),
                    (low&(wheel>1.).all(-1)).sum(dtype=torch.float64),
                    (low&(base<1.)).sum(dtype=torch.float64),
                    (low&good).sum(dtype=torch.float64))))
                self.low80_last_flags.copy_(torch.stack((height>=.23,gravity_z<-.984807753,root_speed<.03,angular_speed<.2,(wheel>1.).all(-1),base<1.,good),dim=-1))
                self.low80_last_metrics.copy_(torch.stack((height,gravity_z,root_speed,angular_speed,wheel[:,0],wheel[:,1],base,upright),dim=-1))
            self.stable.copy_(torch.where(good,self.stable+2,0));event=(self.stable>=50)&~self.credited;self.delta.add_(event.float());self.credited|=event;self.age+=2

        def state_dict(self):
            state = super().state_dict()
            state['tensors'].update({
                name: getattr(self, name).clone()
                for name in ('low80_last_flags', 'low80_last_metrics')
            })
            return state

    old.RecoveryPhase = Low80ConfirmationPhase


def bind_after_build(env, root):
    overlay.bind_after_build(env, root)
    phase = env.recovery
    assert env.num_envs == phase.n == LOW80_NUM_ENVS
    assert phase.recipe.shape == (LOW80_NUM_ENVS,) and phase.recipe.dtype == torch.long
    expected = 13 + torch.arange(LOW80_NUM_ENVS, device=phase.recipe.device, dtype=torch.long) % 5
    assert torch.equal(phase.recipe, expected), 'LOW80 requires recipe 13 + arange(80) % 5'
    assert overlay._POSES is not None and len(overlay._POSES) == 5
    assert len(env.e3_wheels) == 2
    assert phase.low80_last_flags.shape == (LOW80_NUM_ENVS, 7)
    assert phase.low80_last_flags.dtype == torch.bool
    assert phase.low80_last_metrics.shape == (LOW80_NUM_ENVS, 8)
    assert phase.low80_last_metrics.dtype == torch.float32
    env.low80_confirmation_scope = dict(
        kind=LOW80_SCOPE,
        denominator=LOW80_NUM_ENVS,
        pose_count=5,
        envs_per_pose=16,
        recipes=(13, 14, 15, 16, 17),
        original_74_denominator_reused=False,
        flag_columns=LOW80_FLAG_COLUMNS,
        metric_columns=LOW80_METRIC_COLUMNS,
        wheel_force_column_order='env.e3_wheels[0], env.e3_wheels[1]',
        cache_stage='existing phase.update before framework reset',
        joint_good_definition='original good, including request and all low-rise criteria',
        initial_cache='false flags and zero float32 metrics',
        reset_cache_policy='preserve last sampled frame; inherited reset unchanged',
    )
