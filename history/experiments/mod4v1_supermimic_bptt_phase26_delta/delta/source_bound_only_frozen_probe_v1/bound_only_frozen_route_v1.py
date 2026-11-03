"""SOURCE-only adapter route, NOT a runnable native parent/worker or training loop.

Import alongside the PINNED original a1_frozen_eval_runtime_v2/core alias. A future
NEW task schema/worker/index must explicitly select this route and validate its
new receipt; substituting it into an old unbounded-candidate task is not allowed.
"""
import hashlib
from pathlib import Path
import a1_frozen_eval_runtime_v2 as base
import bound_only_frozen_probe_v1 as p

INTEGRATION = 'SOURCE_ONLY_ZERO_UPDATE_BOUND_PROBE_ADAPTER_V1'
NATIVE_ENABLED = False


def validate_source_route_task(task):
    config = task.get('bound_only_probe', {})
    p.h.need(task.get('role') in p.QUALIFIED_CONTAINERS and config.get('purpose') == p.PURPOSE
        and config.get('policy_variant') == p.VARIANT and config.get('zero_update') is True
        and config.get('native_enabled') is False and type(config.get('collect_action_statistics')) is bool,
        'NEW explicit SOURCE-only ZERO_UPDATE bound-probe route task required')
    raw = Path(base.__file__).resolve().read_bytes()
    p.h.need((len(raw), hashlib.sha256(raw).hexdigest()) == p.BOUNDARY_PIN,
             'original full A1 adapter/boundary core source differs')
    return config


class BoundOnlyCheckpointAdapter(base.A1CheckpointAdapter):
    def __init__(self, torch_module, task):
        self.probe_config = dict(validate_source_route_task(task))
        # Original own FINAL binding and ONE original full A1 cache read/decode.
        super().__init__(torch_module, task)
    def actor(self, device, n=80):
        p.h.need(self.caller is None and type(n) is int and n == 80, 'one fresh bound-only N80 actor per whole cache')
        base._validate_approved_reference(self.task)
        mean = p.build_bound_only_mean_policy(self.cache, device, num_envs=80,
            expected_container_sha=p.QUALIFIED_CONTAINERS[self.task['role']],
            collect_action_statistics=self.probe_config['collect_action_statistics'], synthetic_only=False)
        self.caller = p.BoundOnlyPolicyCaller(mean, boundary=base.OriginalEpisodeBoundary(mean.t, mean.device))
        return self.caller
    # check/assert_entire_root_unchanged/check_actor are inherited without changes.
    def receipt(self):
        source_final = self.task['a1_producer']['FINAL']
        value = dict(self.cache.receipt(), integration=INTEGRATION, purpose=p.PURPOSE, policy_variant=p.VARIANT,
            policy_family='zero_update_tanh_postprocess_of_original_full_A1_not_training',
            source_producer_run_id=self.task['a1_producer']['run_id'],
            source_producer_actual_BPTT_policy_steps=source_final['actual_BPTT_policy_steps'],
            source_producer_counts=dict(source_final['counts']),
            source_producer_counts_are_historical_not_probe_updates=True,
            probe_BPTT_policy_steps=0, probe_training_updates=0,
            probe_optimizer_updates=dict(pi=0, wm=0, aux=0, critic=0),
            approved_RSL_model_source=dict(p.APPROVED_RSL), native_enabled=False,
            actual_qualified_native_execution=None, relative_or_training_effect=None)
        if self.caller is not None: value['frozen_mean'] = self.caller.receipt()
        return value
