from pathlib import Path

r=Path(__file__).resolve().parent
t=(r/'mod4_env_baseline.py').read_text(encoding='utf-8')
needle='    def step(self, action):'
hook='''    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._contact_eager5ms_enabled = os.environ.get("RM_CONTACT_EAGER5MS", "0") == "1"
        if self._contact_eager5ms_enabled:
            self._install_contact_eager5ms()

    def _install_contact_eager5ms(self):
        """Consume only the SCUT history sensor at its configured physics cadence.

        Physics, sensor threshold, history length and force formula are unchanged.
        Other lazy sensors stay untouched. A batched/decimated physics backend
        without substep callbacks is deliberately rejected.
        """
        if self._physics_handles_decimation:
            raise RuntimeError("5 ms contact capture requires physical substep scene updates")
        sensor = self.scene.sensors["wheel_contact_scut"]
        period = float(sensor.cfg.update_period)
        stride = int(round(period / float(self.physics_dt)))
        if abs(period - 0.005) > 1e-9 or stride < 1 or abs(stride * self.physics_dt - period) > 1e-9:
            raise RuntimeError("Contact cadence contract is not 5 ms / integer physics ticks")
        if int(sensor.cfg.history_length) != 3:
            raise RuntimeError("Contact history must preserve three samples")
        _ = sensor.data  # align an initial read; reset history remains sensor-owned
        original_update = self.scene.update
        self._contact_physics_tick = 0

        def update_with_contact_capture(dt):
            if abs(float(dt) - float(self.physics_dt)) > 1e-9:
                raise RuntimeError("Contact capture received a decimated update")
            original_update(dt)
            self._contact_physics_tick += 1
            if self._contact_physics_tick % stride == 0:
                _ = sensor.data

        self.scene.update = update_with_contact_capture
        self._contact_capture_metadata = {"enabled": True, "period_s": period,
            "physics_dt": float(self.physics_dt), "stride": stride, "history_length": 3,
            "semantics": "instantaneous sensor force at 5 ms endpoints; not accumulated impulses or continuous contact"}
        import json
        print("CONTACT_CAPTURE_CONFIG " + json.dumps(self._contact_capture_metadata), flush=True)

'''
assert t.count(needle)==1
t=t.replace(needle,hook+needle)
(r/'mod4_env.py').write_text(t,encoding='utf-8')
compile(t,'mod4_env.py','exec')
print('Candidate environment syntax passed')

# Same probe, with substep timestamps and the true contact-gated reward recorded.
p=Path(__file__).resolve().parent.parent/'MOD4_CONTACT_PROBE_20260930/contact_probe_v2.py'
q=p.read_text(encoding='utf-8')
q=q.replace('samples=[];sample_dt=[];history_stamp=[];', 'samples=[];sample_dt=[];history_stamp=[];history_substep=[];height_credit=[];')
q=q.replace('            sample_dt.append(float(dt))', '''            sample_dt.append(float(dt))
            import warp as wp
            history_substep.append(wp.to_torch(env.scene.sensors['wheel_contact_scut']._timestamp_last_update).clone())''')
q=q.replace('        h=task.root_height_above_ground(env)', '''        height_credit.append(task.height_track_both_wheels(env, sigma=task.SCUT_H_SOFT_SIGMA).clone())
        h=task.root_height_above_ground(env)''')
q=q.replace('columns=np.array(', 'history_substep_timestamp=torch.stack(history_substep).cpu().numpy(),height_credit=torch.stack(height_credit).cpu().numpy(),\n        columns=np.array(')
q=q.replace("'history_actual_update_intervals_s':", "'eager5ms_metadata':getattr(env,'_contact_capture_metadata',{'enabled':False}),\n        'history_substep_update_intervals_s':np.unique(np.round(np.diff(torch.stack(history_substep).cpu().numpy()[:,0])[np.diff(torch.stack(history_substep).cpu().numpy()[:,0])>0],5)).tolist(),\n        'height_credit_after_1s_mean_per_env':torch.stack(height_credit)[100:].mean(0).cpu().tolist(),\n        'history_actual_update_intervals_s':")
(r/'sampling_pair_probe.py').write_text(q,encoding='utf-8')
compile(q,'sampling_pair_probe.py','exec')
print('Pair probe syntax passed')
