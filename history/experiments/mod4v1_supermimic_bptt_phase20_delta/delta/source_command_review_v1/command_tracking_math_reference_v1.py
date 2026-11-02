"""Stdlib formulas: synthetic tests only, not a simulator or trainable model."""
import math


def e2_body_command(speed, world_direction, heading, body_limit=1.5):
    return (max(-body_limit, min(body_limit, 2. * speed * math.cos(heading - world_direction))), 0.)


def transition_yaw(elapsed, target):
    e = elapsed
    scale = (e if e < 1. else 1. if e < 4. else 5. - e if e < 5. else 0. if e < 6.
             else -(e - 6.) if e < 7. else -1. if e < 10. else e - 11. if e < 11. else 0.)
    return target * scale


def e2_next(command_t, *, speed, world_direction, next_heading, signed_yaw,
            moving, transition, standing, next_write_elapsed, body_limit=1.5):
    c = list(command_t)
    if moving:
        c[:2] = e2_body_command(speed, world_direction, next_heading, body_limit)
        c[2] = signed_yaw
    if transition:
        c[2] = transition_yaw(next_write_elapsed, signed_yaw)
    return (0., 0., 0.) if standing else tuple(c)


def w35_next(command_t, standing):
    return (0., 0., 0.) if standing else (command_t[0], 0., 0.)


def known_command_writes(time_left_seconds, horizon=16, dt=.02):
    """No new RNG: report first unknown resample; NEVER filter the command domain."""
    # Source first decrements time_left, then resamples when <=0, then writes.
    return [time_left_seconds - (i + 1) * dt > 1e-12 for i in range(horizon)]


def sampled_progress_axis(sampled_heading, sampled_body_vx):
    return sampled_heading + (math.pi if sampled_body_vx < 0. else 0.)


def raw35(command, height_metres, sensor, last_action, mode):
    x = sensor
    out = list(command) + [5. * height_metres]
    out += [.5 * v for v in x['base_ang_vel']]
    out += list(x['projected_gravity']) + list(x['leg_pos']) + [0., 0.]
    out += [.1 * v for v in x['leg_vel']] + [.1 * v for v in x['wheel_vel']]
    out += list(last_action) + list(mode)
    if len(out) != 35:
        raise ValueError('original raw35 widths required')
    return tuple(out)


class FeedbackSampleTape:
    """Original 0/1 sample lag queue semantics, EXOGENOUS noisy samples only.

    Synthetic scalar/list values can already contain original bias/noise. Real
    100Hz values require receipts, two sample stamps/control, original RNG streams.
    No new noise draw here, and no apply-time BODY frame rotation.
    """
    def __init__(self, lag):
        if lag not in (0, 1):
            raise ValueError('original delay is zero or one 100Hz sample')
        self.lag = lag
        self.cur = self.out = None
        self.sample_tick = None
        self.receipt = None
        self.samples_consumed = 0

    def apply(self, tick, noisy_value):
        if tick == self.sample_tick:
            return self.out
        if self.sample_tick is not None and self.sample_tick != tick - 1:
            raise ValueError('Skipped/reversed feedback sample clock')
        warmup = self.sample_tick is None
        out = noisy_value if self.lag == 0 or warmup else self.cur
        age_samples = 0 if self.lag == 0 or warmup else 1
        self.cur, self.out, self.sample_tick = noisy_value, out, tick
        self.samples_consumed += 1
        self.receipt = dict(sample_tick=tick - age_samples, apply_tick=tick,
                            actual_age_us=10000 * age_samples, warmup=warmup)
        return out

    def reset(self):
        self.cur = self.out = self.sample_tick = self.receipt = None
        self.samples_consumed = 0


def tracking_terms(command_t, velocity_b, omega_b, gravity_b, *, height_gate=1.):
    forward = command_t[0] - velocity_b[0] * math.sqrt(max(0., 1. - gravity_b[0] ** 2))
    yaw = command_t[2] - omega_b[2]
    return dict(track_lin_vel=math.exp(-forward ** 2 / .25),
                track_lin_vel_tight=math.exp(-forward ** 2 / .01),
                track_lin_vel_huge_gap=float(forward ** 2 > .5),
                track_lin_vel_square=(.25 * forward) ** 2,
                track_ang_vel=math.exp(-yaw ** 2 / .25),
                track_ang_vel_square=(.25 * yaw) ** 2 * height_gate)


def bounded_action(teacher, logits, radius=.05):
    base = max(-6., min(6., teacher))
    return max(-6., min(6., base + radius * math.tanh(logits)))


def native_action(teacher, logits, scale=.05):
    return max(-6., min(6., teacher + scale * logits))


def lambda_targets(rewards, dones, values_next, gamma=.99, lam=.95):
    """Reference only: final-step termination masks bootstrap, not its own reward."""
    target = values_next[-1]
    out = []
    for r, d, v in zip(reversed(rewards), reversed(dones), reversed(values_next)):
        target = r + gamma * (1. - d) * ((1. - lam) * v + lam * target)
        out.append(target)
    return list(reversed(out))


def valid_window_rows(done, stream_cut):
    live, out = True, []
    for d, cut in zip(done, stream_cut):
        out.append(live)
        live = live and not (d or cut)
    return out
