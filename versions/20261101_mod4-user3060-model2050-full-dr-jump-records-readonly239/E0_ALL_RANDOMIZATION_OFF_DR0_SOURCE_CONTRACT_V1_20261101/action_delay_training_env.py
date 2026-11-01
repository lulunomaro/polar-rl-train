"""Approved D4 candidate: existing D3 observations, separate physical target queue."""
import os
from feedback_delay_runtime import DelaySensorMod4Env
from action_delay_sdk_adapter import PhysicalActionDelayAdapter

class ActionDelayMod4Env(DelaySensorMod4Env):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        profile=os.environ.get('RM_PHYSICS_ACTION_DELAY_PROFILE','')
        assert profile in ('off','physical_target_0_2500_5000us_v1')
        self._physics_action_delay=PhysicalActionDelayAdapter(self,profile!='off',int(self.cfg.seed),collect=False)
    def action_delay_recipe(self):
        r=dict(self._physics_action_delay.queue.recipe())
        r.pop('CPU_component_not_actual_SDK_or_learning',None)
        r.update(actual_runtime='processed target before physical integration',
                 original_action_process_apply_actuator_path=True,
                 SDK_clock='issue=counter; apply=counter-1 before sim.step',
                 actor_last_action='Original requested policy action, no privileged queue observation',
                 initial_admission_has_predecessor_action_queue=False)
        return r
