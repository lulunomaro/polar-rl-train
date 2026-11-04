"""Minimal SOURCE adapter. Caller owns original reset/bridge/step/close/resources.

The stable sensor API is passed explicitly. No native/SDK/torch module is imported;
no action-observer API is assumed. Fake injection tests establish plumbing only.
"""
from __future__ import annotations
from capture_contract import INTEGRATION, UNKNOWN, need, validate_source_request


class CaptureSession:
    def __init__(self, env, bridge, tap, recorder, snapshot, request):
        self.env, self.bridge, self.tap = env, bridge, tap
        self.recorder, self.snapshot, self.request = recorder, snapshot, request
        self.actor_observations = 0
        self.last_control_index = -1
        self.closed = False

    def observe_actor35(self, actor35, *, original_policy_buffer, control_index):
        """Observe an original returned buffer; do not synthesize/recompute it.

        Identity proves origin only, NOT bitwise equality versus an untapped run.
        Capture errors are recorded without replacing the original return object.
        """
        need(not self.closed, 'tap already restored')
        need(actor35 is original_policy_buffer, 'actor must be original returned policy buffer')
        shape = actor35.shape
        need(tuple(shape) == (self.request['num_envs'], 35), 'original actor buffer shape must be N80x35')
        need(type(control_index) is int and control_index == self.last_control_index + 1
             and control_index <= self.request['controls'], 'actor controls must be contiguous initial0 through bound')
        ticket = self.recorder.begin('actor35_original_buffer')
        payload = dict(control_index=control_index, shape=list(shape),
                       original_return_identity=True, actor35=UNKNOWN,
                       source='original_returned_policy_buffer',
                       untapped_bitwise_comparison=UNKNOWN)
        try:
            if ticket is not None:
                payload['actor35'] = self.snapshot(actor35)
        except BaseException as error:
            self.recorder.capture_error(error)
        finally:
            self.recorder.commit(ticket, payload)
        self.actor_observations += 1
        self.last_control_index = control_index
        return actor35

    def report(self):
        return dict(kind=INTEGRATION, source_only=True, native_enabled=False, exact=False,
                    gate1=UNKNOWN, capture_interface_passed=False,
                    request=dict(self.request), sensor=self.tap.report(),
                    actor35_source='original_returned_policy_buffer',
                    actor35_observations=self.actor_observations,
                    observed_controls=max(0, self.actor_observations - 1),
                    actor35_bitwise_untapped_comparison=UNKNOWN,
                    action_observer_status='DEFERRED_UNSEALED',
                    terminal_partial_reset_actual_coverage=UNKNOWN,
                    full_clean35_mid_end=UNKNOWN,
                    resource_close_wait_release_attested_here=False,
                    tap_restored=self.closed)

    def close(self):
        """Restore only this tap BEFORE caller invokes original bridge.close()."""
        if not self.closed:
            self.tap.close()
            self.closed = True


def install_after_first_reset(env, bridge, feedback_module, role_api, bridge_pin, request, *,
                              sensor_api, snapshot=None):
    """No reset/step/getter. All actual source/MRO binding checks stay in sensor.

    sensor_api must be supplied from the parent-reviewed frozen dependency;
    source_preflight pins the B seal and all thirteen files. No native admission.
    """
    request = validate_source_request(request)
    need(vars(bridge).get('real') is env, 'tap must use same original env/bridge instance')
    need(vars(bridge).get('initialized') is True and vars(bridge).get('state') is not None,
         'original bridge must already be initialized using first-reset initial_obs')
    need(all(key in vars(env) for key in ('_sensor_mild', '_feedback_delay_mild',
                                        '_sim_step_counter', '_feedback_100hz_tick')),
         'first original reset must initialize original sensor/delay state')
    need(vars(bridge).get('num_envs') == request['num_envs'], 'original bridge N80 mismatch')
    # This cap bounds recorder payloads, never controls or plant clocks. Bounded
    # retention is first32/last32 globally, NOT every channel/terminal guaranteed.
    # Future actual gate must declare coverage/inconclusive from original counts.
    recorder = sensor_api.BoundedRecorder(first=32, last=32, max_events=100000)
    snapshot = sensor_api.stdlib_snapshot if snapshot is None else snapshot
    tap = sensor_api.install_passive_capture(env, bridge, feedback_module, role_api, bridge_pin,
                                            recorder=recorder, snapshot=snapshot)
    return CaptureSession(env, bridge, tap, recorder, snapshot, request)
