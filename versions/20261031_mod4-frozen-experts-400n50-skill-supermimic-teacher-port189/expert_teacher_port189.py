"""Frozen PPO teacher boundary for a separately admitted native learner.

This module does not construct a robot, open a checkpoint, or start a learner.
The original processed policy35 is an input; it is never guessed from state127.
"""
from dataclasses import dataclass
import torch
from torch.nn import functional as F

ACTION_ORDER = (
    "left_crank", "left_hip", "right_crank", "right_hip",
    "left_wheel_spin", "right_wheel_spin",
)
POLICY_US = 20000
PHYSICS_US = 2500
FEEDBACK_US = 10000


def require(value, message):
    if not bool(value):
        raise ValueError(message)


class FrozenPPO35Teacher:
    """The saved 35/256/128/64/6 ELU mean, without sampling STD or RNG."""

    def __init__(self, actor_state):
        expected = {"distribution.std_param"}
        expected |= {f"mlp.{i}.{suffix}" for i in (0, 2, 4, 6)
                     for suffix in ("weight", "bias")}
        require(set(actor_state) == expected,
                "Only the explicitly reviewed PPO35 actor keyset is admitted")
        sizes = (35, 256, 128, 64, 6)
        self.layers = []
        for i, (din, dout) in zip((0, 2, 4, 6), zip(sizes, sizes[1:])):
            weight = actor_state[f"mlp.{i}.weight"]
            bias = actor_state[f"mlp.{i}.bias"]
            require(tuple(weight.shape) == (dout, din) and
                    tuple(bias.shape) == (dout,), "Actor architecture differs")
            require(torch.isfinite(weight).all() and torch.isfinite(bias).all(),
                    "Nonfinite teacher")
            self.layers.append((weight.detach().clone(), bias.detach().clone()))
        std = actor_state["distribution.std_param"]
        require(tuple(std.shape) == (6,) and torch.isfinite(std).all(),
                "Six original finite distribution parameters required")
        self.saved_std = std.detach().clone()

    def mean(self, original_processed_policy35):
        obs = original_processed_policy35
        require(obs.ndim == 2 and obs.shape[-1] == 35 and obs.shape[0] > 0,
                "Original runtime policy35 required; no state-to-obs shortcut")
        require(torch.isfinite(obs).all(), "Nonfinite policy35")
        # No re-normalization, extra command scaling, noise, sample, or clip here.
        with torch.no_grad():
            value = obs
            for i, (weight, bias) in enumerate(self.layers):
                value = F.linear(value, weight, bias)
                if i != 3:
                    value = F.elu(value)
        return value


def teacher_clipped_command(mean6):
    require(mean6.ndim == 2 and mean6.shape[-1] == 6 and
            torch.isfinite(mean6).all(), "Finite original mean6 required")
    return mean6.detach().clamp(-6.0, 6.0)


def teacher_warmstart_loss(student_raw_mean6, teacher_raw_mean6):
    """Standalone BC objective, not an unreviewed extra BPTT reward weight.

    Compare the student's RAW output to the teacher's original clipped command.
    Clipping the student's output first would kill gradients outside +/-6.
    All six channels are in original normalized action units, before .5/10 scales.
    """
    require(student_raw_mean6.shape == teacher_raw_mean6.shape,
            "Student and teacher must have the same six named action channels")
    require(student_raw_mean6.ndim == 2 and student_raw_mean6.shape[0] > 0 and
            student_raw_mean6.shape[-1] == 6 and
            torch.isfinite(student_raw_mean6).all(), "Finite student raw6 required")
    target = teacher_clipped_command(teacher_raw_mean6)
    return ((student_raw_mean6 - target) / 6.0).square().mean()


@dataclass(frozen=True)
class PairIdentity:
    run_id: str
    expert: str
    teacher_SHA: str
    runtime_SHA: str
    action_order: tuple
    joint_names30: tuple


def validate_measured_pair(identity, before, terminal):
    """Validate one 50 Hz decision -> PRE-RESET own-PhysX endpoint.

    The runtime integration must supply these already observed values. This is
    not an SDK getter, collector, or a claim that old sparse traces contain them.
    Public H1 100 Hz age, when relevant, remains separate from policy_control.
    """
    require(identity.run_id and identity.expert, "Named run/expert required")
    for digest in (identity.teacher_SHA, identity.runtime_SHA):
        require(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest),
                "Exact source identities required")
    require(tuple(identity.action_order) == ACTION_ORDER, "Action order mismatch")
    require(len(identity.joint_names30) == 30 and
            len(set(identity.joint_names30)) == 30, "Named joint30 binding required")
    needed_before = {"state127", "xi31", "policy35", "teacher_raw6", "issued6",
                     "previous_issued6", "episode_id", "policy_control", "time_us"}
    needed_terminal = {"state127_pre_reset", "episode_id_for_terminal", "policy_control",
                       "time_us", "done", "physics_time_us8", "feedback_time_us2",
                       "processed_targets6_at8_callbacks"}
    require(needed_before <= before.keys(), "Missing decision fields; no zero fill")
    require(needed_terminal <= terminal.keys(), "Missing terminal/queue fields; no zero fill")
    batch = before["state127"].shape[0]
    require(batch > 0, "Nonempty batch required")
    shapes = ((before, "state127", (batch, 127)),
              (before, "xi31", (batch, 31)), (before, "policy35", (batch, 35)),
              *((before, key, (batch, 6)) for key in
                ("teacher_raw6", "issued6", "previous_issued6")),
              (terminal, "state127_pre_reset", (batch, 127)),
              (terminal, "processed_targets6_at8_callbacks", (batch, 8, 6)),
              (terminal, "physics_time_us8", (batch, 8)),
              (terminal, "feedback_time_us2", (batch, 2)))
    for data, key, shape in shapes:
        value = data[key]
        require(torch.is_tensor(value) and tuple(value.shape) == shape and
                torch.isfinite(value).all(), f"Bad measured field {key}")
    vectors = ((before, "episode_id"), (before, "policy_control"), (before, "time_us"),
               (terminal, "episode_id_for_terminal"), (terminal, "policy_control"),
               (terminal, "time_us"), (terminal, "done"))
    for data, key in vectors:
        value = data[key]
        require(torch.is_tensor(value) and tuple(value.shape) == (batch,),
                f"Bad identity vector {key}")
        if key != "done":
            require(value.dtype in (torch.int32, torch.int64),
                    f"Integer identity/time required: {key}")
    require(terminal["done"].dtype == torch.bool, "Explicit terminal mask required")
    require(torch.equal(before["episode_id"], terminal["episode_id_for_terminal"]),
            "Post-reset state cannot replace terminal state")
    require(torch.equal(before["policy_control"] + 1, terminal["policy_control"]),
            "Exactly one policy transition required")
    require(torch.equal(before["time_us"] + POLICY_US, terminal["time_us"]),
            "50 Hz transition required; old 100 Hz WM steps are not interchangeable")
    offsets8 = torch.arange(1, 9, device=before["time_us"].device) * PHYSICS_US
    offsets2 = torch.arange(1, 3, device=before["time_us"].device) * FEEDBACK_US
    require(torch.equal(before["time_us"][:, None] + offsets8,
                        terminal["physics_time_us8"]), "Eight original callback times required")
    require(torch.equal(before["time_us"][:, None] + offsets2,
                        terminal["feedback_time_us2"]), "Two original feedback times required")
    require(torch.equal(before["issued6"], teacher_clipped_command(before["teacher_raw6"])),
            "Teacher mean and original wrapper command differ")
    require((before["previous_issued6"].abs() <= 6).all(), "Previous issued command differs")
    # The learner receives the real terminal endpoint, never the auto-reset pose.
    return dict(s=before["state127"], s1=terminal["state127_pre_reset"],
                xi=before["xi31"], a=before["issued6"],
                a_prev=before["previous_issued6"], done=terminal["done"],
                teacher_policy35=before["policy35"],
                teacher_raw6=before["teacher_raw6"],
                processed_targets6_at8_callbacks=terminal["processed_targets6_at8_callbacks"])
