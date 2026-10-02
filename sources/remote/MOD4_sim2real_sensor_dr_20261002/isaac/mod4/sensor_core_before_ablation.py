"""Bounded actor-only sensing stress; no Isaac imports or plant mutations.

Ranges are provisional engineering stress ranges, NOT real sensor calibration.
The whole sensor packet shares an episode-held 0/1 control-step lag. Commands,
last actions, rewards, critic truth and physical reset are never transformed.
"""
import torch

NOISE = {'base_ang_vel': .03, 'projected_gravity': .005,
         '_mod4_leg_bias': .002, 'leg_vel': .1, 'wheel_vel': .2}
BIAS = {'base_ang_vel': .01, '_mod4_leg_bias': .005}


class SensorCore:
    def __init__(self, n, device, seed):
        self.n, self.device = n, device
        self.generator = torch.Generator(device=device).manual_seed(int(seed) + 31017)
        self.nominal = torch.ones(n, dtype=torch.bool, device=device)
        self.lag = torch.zeros(n, dtype=torch.long, device=device)
        self.reset_counts = torch.zeros(n, dtype=torch.long, device=device)
        self.bias = {k: torch.zeros((n, w), device=device)
                     for k, w in [('base_ang_vel', 3), ('_mod4_leg_bias', 4)]}
        self.lines = {}
        self.max_error = {k: torch.zeros((), device=device) for k in NOISE}
        self.packet_count = {k: 0 for k in NOISE}

    def uniform(self, shape, amplitude):
        return (torch.rand(shape, device=self.device, generator=self.generator) * 2 - 1) * amplitude

    def reset(self, ids, nominal):
        self.nominal[ids] = nominal
        self.lag[ids] = torch.randint(0, 2, (len(ids),), device=self.device, generator=self.generator)
        self.lag[ids] = torch.where(nominal, 0, self.lag[ids])
        self.reset_counts[ids] += 1
        for key, amplitude in BIAS.items():
            value = self.uniform((len(ids), self.bias[key].shape[1]), amplitude)
            value[nominal] = 0.
            self.bias[key][ids] = value
        for line in self.lines.values():
            line['valid'][ids] = False
            line['cached_valid'][ids] = False
            line['history'][:, ids] = 0.
            line['pending_reset'] = True

    def sample(self, key, value, step):
        if key not in NOISE:
            return value
        line = self.lines.get(key)
        if line is None:
            line = self.lines[key] = dict(history=torch.zeros((2, *value.shape), device=self.device),
                valid=torch.zeros(self.n, dtype=torch.bool, device=self.device), step=None,
                cached=torch.zeros_like(value), cached_valid=torch.zeros(self.n, dtype=torch.bool, device=self.device), pending_reset=True)
        # Observation managers may compute repeatedly within the same control tick.
        # Only the first compute advances the packet; reset environments invalidate
        # their own cache without advancing other environments a second time.
        new_tick = line['step'] != int(step)
        if new_tick:
            line['history'][1].copy_(line['history'][0])
            line['cached_valid'].zero_()
            line['step'] = int(step)
        if not new_tick and not line['pending_reset']:
            return line['cached']
        ids = torch.arange(self.n, device=self.device) if new_tick else (~line['cached_valid']).nonzero(as_tuple=False).flatten()
        if len(ids):
            noisy = value[ids].clone() + self.uniform((len(ids), value.shape[1]), NOISE[key])
            if key in self.bias:
                noisy += self.bias[key][ids]
            if key == 'projected_gravity':
                noisy = noisy / noisy.norm(dim=1, keepdim=True).clamp_min(1e-9)
            noisy[self.nominal[ids]] = value[ids][self.nominal[ids]]
            fresh = ~line['valid'][ids]
            line['history'][0, ids] = noisy
            # New episode starts from the current packet, never zeros or old data.
            line['history'][1, ids] = torch.where(fresh[:, None], noisy, line['history'][1, ids])
            line['valid'][ids] = True
            line['cached'][ids] = line['history'][self.lag[ids], ids]
            line['cached_valid'][ids] = True
            self.max_error[key] = torch.maximum(self.max_error[key], (noisy - value[ids]).abs().max())
            self.packet_count[key] += 1
            line['pending_reset'] = False
        return line['cached']

    def audit(self):
        clean = self.nominal
        return {'profile': 'sensor_v1', 'provisional_not_hardware_calibrated': True,
            'nominal_fraction': float(clean.float().mean()), 'lag_steps_min': int(self.lag.min()),
            'lag_steps_max': int(self.lag.max()), 'actual_lag_steps': self.lag.cpu().tolist(),
            'nominal_mask': clean.cpu().tolist(), 'reset_count_min': int(self.reset_counts.min()),
            'bias_abs_max': {k: float(v.abs().max()) for k,v in self.bias.items()},
            'observed_packet_error_max': {k:float(v) for k,v in self.max_error.items()}, 'packet_count': dict(self.packet_count),
            'nominal_bias_zero': all(bool((v[clean] == 0).all()) for v in self.bias.values()),
            'nominal_lag_zero': bool((self.lag[clean] == 0).all()),
            'noise_bound_raw_units': NOISE, 'persistent_bias_bound_raw_units': BIAS,
            'nominal_samples_clean': True, 'shared_sensor_lag_seconds': [0., .01],
            'action_delay_seconds': 0., 'critic_reward_and_plant_unchanged': True}
