"""Independent224 architecture, using255 native H32 WM50 loss and replay code.

No old127 checkpoint is loaded or claimed compatible. This file changes only
the explicit dynamic measurement layout; native SE3 prediction is inherited.
"""
from types import SimpleNamespace
import torch
from native_depth_world_model50_v255 import DepthTeacherWM50, load_native_kernels
from measured_state224_v268 import MeasuredStateLayout268, SCHEMA_ID, require


class MeasuredDepthTeacherWM50(DepthTeacherWM50):
    def __init__(self, source, device, *, binding, seed, envs=2048, window=32,
                 batch=1024, hidden=(512, 512, 512), learning_rate=1e-4,
                 synthetic_CPU_test=False):
        require(isinstance(envs, int) and envs > 0 and window == 32 and batch > 0,
                'Positive bounded replay dimensions and original H32 required')
        binding.validate(synthetic_CPU_test=synthetic_CPU_test)
        self.binding = binding
        self.synthetic_CPU_test = synthetic_CPU_test
        self.device = torch.device(device)
        self.envs, self.window, self.batch = envs, window, batch
        self.last_physics_tick = None
        geometry, world, replay = load_native_kernels(source)
        self.measured_layout = MeasuredStateLayout268(geometry, world)
        self.geometry = SimpleNamespace(unflatten_state=self.measured_layout.unpack)

        class MeasuredModel(world.AugmentedWheelLegWorldModel):
            def terrain_relative(self, state):
                # Same255 depth context; no privileged terrain oracle.
                return torch.zeros_like(state[0])

        devices = [self.device.index or 0] if self.device.type == 'cuda' else []
        with torch.random.fork_rng(devices=devices):
            torch.manual_seed(seed)
            self.model = MeasuredModel(context_dim=40, hidden=hidden, num_joints=30,
                auxiliary_dim=151, action_dim=6, edge_x_m=0, platform_top_z_m=0).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        self.generator = torch.Generator(device=self.device)
        self.generator.manual_seed(seed + 1)
        self.buffer = replay.ReplayBuffer(64, envs, self.device,
            num_joints=30, context_dim=40, action_dim=6, state_dim=224)
        self.floor = world.learner_error_floor(world.WheelLegStateLayout(30, 151)).to(self.device)
        self.updates = self.controls = 0
        self.protocol = dict(kind='NATIVE_SUPERMIMIC_OWN_MEASURED224_DEPTH_CONTEXT40_WM50_V268',
            state_schema=SCHEMA_ID, state224=True, physical73=True, aux151=True,
            original127_prefix=True, additional97='own L0/theta4 + BODY contact31x3 /403N',
            context40=True, static31=True, depth9=True, actions6=True,
            physics_us=2500, policy_us=20000, physics_callbacks=8, feedback_samples=2,
            window=32, batch=batch, replay_capacity=64, hidden=list(hidden),
            time_loss_reduction='sum time / batch, original native loss semantics',
            gradient_clip=1.0, new_WM_parameters_and_optimizer=True,
            original_PPO_actor_critic_STD_17Adam_frozen=True, policy_BPTT_updates=0,
            closure_m=.01, mimic_rad=.01, gas_nominal_N=400, DR='unchanged D0-D7',
            architecture_resume='new224 architecture; reject old127 checkpoint as same-layout resume',
            context40_time_semantics='H32 WM supervision may use recorded xi at each time; its later depth9 is NOT available to policy imagination',
            policy_imagination_context_ready=False,
            policy_imagination_context_pending='first observed depth+pose anchor/belief with predicted-pose transforms; no later real depth fallback',
            binding=binding.metadata(), synthetic_CPU_test=synthetic_CPU_test)

    def add(self, transition, *, physics_end_tick, physics_us, feedback_samples,
            producer, synthetic_CPU_test=False):
        require(synthetic_CPU_test == self.synthetic_CPU_test, 'Actual/synthetic mode changed')
        self.binding.validate(synthetic_CPU_test=synthetic_CPU_test)
        require(producer.get('state_schema') == SCHEMA_ID and
                producer.get('binding_witness_SHA') == self.binding.witness_SHA and
                producer.get('measured_fields') == ['own_L0_theta4', 'contact_forces_BODY31x3'],
                'Measured224 producer provenance required; old127 label is insufficient')
        require(producer.get('s_physics_end_tick') == physics_end_tick - 8 and
                producer.get('s1_physics_end_tick') == physics_end_tick,
                'Both measured endpoints must match this50Hz transition')
        # Parent validation performs all shape/finite/clock/depth checks before
        # updating norms or replay. Its geometry facade now explicitly rejects127.
        return super().add(transition, physics_end_tick=physics_end_tick,
            physics_us=physics_us, feedback_samples=feedback_samples,
            producer=producer, synthetic_CPU_test=synthetic_CPU_test)

    def checkpoint(self):
        out = super().checkpoint()
        out['measured_state_schema'] = SCHEMA_ID
        out['measured_binding'] = self.binding.metadata()
        return out

    def policy_imagination(self, *args, **kwargs):
        raise NotImplementedError('PENDING: anchor-only depth belief/context builder. '
            'Recorded later depth9 from supervised WM replay is future truth, not policy input.')

    @staticmethod
    def require_checkpoint_schema(checkpoint):
        require(checkpoint.get('measured_state_schema') == SCHEMA_ID and
                checkpoint.get('protocol', {}).get('state224') is True and
                checkpoint.get('protocol', {}).get('aux151') is True,
                'Legacy127 is not an exact measured224 WM resume')
