"""Injection-only ORIGINAL PhysicsActionQueue + sealed tap CPU fixture.
This module never imports torch/Isaac, loads an original class, or runs a driver.
Only env/action-term/asset scaffolding below is FAKE; queue must be pinned original.
No local real-Torch execution was performed when this SOURCE artifact was created.
"""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import inspect

QUEUE_SHA256 = "a4238c581611ef7cdb710692291ddac48e076364b0587f631eb71fd6a7d15eb8"
TAP_SHA256 = "b9b9e288124a1ba8c031a030c00a231f4d02d2ba7efee9981141ae90b8e28828"
FIELDS = ("lag_steps", "episode", "pending", "pending_valid", "issued_tick", "due_tick",
          "applied", "applied_valid", "applied_issue_tick", "first_apply_tick", "last_submit_tick", "last_apply_tick")
WIDTHS = {"legs": 4, "wheels": 2}


class FixtureUnknown(ValueError):
    pass


def build_plan(n=3):
    if type(n) is not int or n not in (2, 3):
        raise ValueError("Fixture supports explicitly N2 or N3")
    return [{"lags": {"legs": a, "wheels": b}, "controls": [0, 8],
             "physics_ticks": list(range(16)), "partial_reset_ids": [1], "n": n}
            for a in range(3) for b in range(3)]


def validate_injections(torch_module, PhysicsActionQueue, tap_module):
    """Hash original files; accept supplied objects only, no loader/fallback/stub."""
    if torch_module is None or getattr(torch_module, "__name__", None) != "torch":
        raise FixtureUnknown("Caller must inject installed real torch module")
    if not inspect.isclass(PhysicsActionQueue) or PhysicsActionQueue.__name__ != "PhysicsActionQueue":
        raise FixtureUnknown("Caller must inject original PhysicsActionQueue class")
    if PhysicsActionQueue.__init__.__globals__.get("torch") is not torch_module:
        raise FixtureUnknown("Original queue torch global differs from injected module")
    origin = inspect.getsourcefile(PhysicsActionQueue)
    if not origin or hashlib.sha256(Path(origin).read_bytes()).hexdigest() != QUEUE_SHA256:
        raise FixtureUnknown("Original queue source pin differs")
    for method in ("__init__", "submit", "apply", "reset", "state_dict", "receipt"):
        fn = getattr(PhysicsActionQueue, method)
        if Path(fn.__code__.co_filename).resolve() != Path(origin).resolve():
            raise FixtureUnknown("Original method was replaced: " + method)
    if PhysicsActionQueue.__init__.__globals__.get("FIELDS") != FIELDS or PhysicsActionQueue.__init__.__globals__.get("WIDTHS") != WIDTHS:
        raise FixtureUnknown("Original queue fields/widths differ")
    tap_path = getattr(tap_module, "__file__", None)
    if not tap_path or hashlib.sha256(Path(tap_path).read_bytes()).hexdigest() != TAP_SHA256:
        raise FixtureUnknown("Sealed actuation tap source pin differs")
    return {"original_queue_sha256": QUEUE_SHA256, "tap_sha256": TAP_SHA256,
            "torch_version": str(torch_module.__version__), "device": "cpu",
            "binding": "INJECTED_ORIGINAL_CPU_COMPONENT_NOT_RUNTIME_SDK_BINDING"}


def _equal(torch, left, right, label):
    """Whole-state comparison with byte-level Tensor equality, including signed zero."""
    if torch.is_tensor(left) or torch.is_tensor(right):
        assert torch.is_tensor(left) and torch.is_tensor(right), label
        assert left.device.type == right.device.type == "cpu", label
        assert left.shape == right.shape and left.dtype == right.dtype, label
        a = left.detach().contiguous().reshape(-1).view(torch.uint8)
        b = right.detach().contiguous().reshape(-1).view(torch.uint8)
        assert torch.equal(a, b), label
    elif type(left) is dict:
        assert type(right) is dict and left.keys() == right.keys(), label
        for key in left: _equal(torch, left[key], right[key], label + "/" + str(key))
    elif type(left) in (tuple, list):
        assert type(right) is type(left) and len(left) == len(right), label
        for i, (a, b) in enumerate(zip(left, right)): _equal(torch, a, b, label + "/" + str(i))
    else:
        assert type(left) is type(right) and left == right, label


def _full_state(queue):
    # The two method spies/tap are the ONLY expected additional instance keys.
    attrs = {k: v for k, v in queue.__dict__.items() if k not in ("submit", "apply", "groups", "rng")}
    return {"original_attributes": {k: str(v) if k == "device" else v for k, v in attrs.items()},
            "full_original_state_dict": queue.state_dict()}


class _OriginalReturnProbe:
    """Calls the real original methods once; retains their return/exception identity."""
    def __init__(self, queue):
        self.queue, self.last, self.errors, self.calls = queue, {}, {}, {}
        self.return_values = {}
        self.original = {name: getattr(queue, name) for name in ("submit", "apply")}
        for name, original in self.original.items():
            def spy(*args, _name=name, _original=original, **kwargs):
                self.calls[_name] = self.calls.get(_name, 0) + 1
                try: value = _original(*args, **kwargs)
                except BaseException as exc:
                    self.errors[_name] = exc
                    raise
                self.last[_name] = value
                if _name == "apply":
                    key = args[0] if args else kwargs["key"]
                    tick = args[1] if len(args) > 1 else kwargs["tick"]
                    self.return_values[(key, tick)] = value
                return value
            setattr(queue, name, spy)
        self.installed = {name: getattr(queue, name) for name in self.original}

    def remove(self):
        for name in self.original:
            assert getattr(self.queue, name) is self.installed[name], "Tap did not restore probe identity"
            delattr(self.queue, name)


class FakeAsset:
    """FAKE argument writer only; no SDK/articulation/physical readback."""
    def __init__(self):
        self.arguments, self.results = {}, {}

    def _write(self, key, target, joint_ids=None):
        self.arguments[key] = target
        self.results[key] = object()
        return self.results[key]

    def set_joint_position_target(self, target, joint_ids=None):
        return self._write("legs", target, joint_ids)

    def set_joint_velocity_target(self, target, joint_ids=None):
        return self._write("wheels", target, joint_ids)


class FakeActionTerm:
    """FAKE term forwards into REAL queue; models only original adapter ordering."""
    def __init__(self, env, key, asset, probe):
        self.env, self.key, self._asset, self.probe = env, key, asset, probe
        self._processed_actions = None
        self.last_actions = self.last_selected = None
        self.issue_token, self.apply_token = object(), object()

    def process_actions(self, actions):
        self.last_actions = actions
        self._processed_actions = actions.clone()
        value = self.env._physics_action_delay.queue.submit(self.key, self._processed_actions, self.env._sim_step_counter)
        assert value is self.probe.last["submit"] is None
        return self.issue_token

    def apply_actions(self):
        selected = self.env._physics_action_delay.queue.apply(self.key, self.env._sim_step_counter - 1)
        assert selected is self.probe.last["apply"], "Queue apply return identity changed"
        self.last_selected = selected
        requested = self._processed_actions
        self._processed_actions = selected
        try:
            writer = self._asset.set_joint_position_target if self.key == "legs" else self._asset.set_joint_velocity_target
            result = writer(selected, joint_ids=list(range(WIDTHS[self.key])))
            assert self._asset.arguments[self.key] is selected, "Writer argument identity changed"
            assert result is self._asset.results[self.key], "Writer return identity changed"
        finally:
            self._processed_actions = requested
        return self.apply_token


class FakeEnv:
    """Explicitly FAKE env holding an injected REAL queue; no actor35 or SDK."""
    def __init__(self, queue, probe):
        self._sim_step_counter = 0
        self._physics_action_delay = SimpleNamespace(queue=queue, terms={})
        asset = FakeAsset()
        self._physics_action_delay.terms = {k: FakeActionTerm(self, k, asset, probe) for k in WIDTHS}


def _materialize(torch, value):
    """Only after callback returns, for old stdlib validator; no on-tick CPU I/O."""
    if torch.is_tensor(value): return value.detach().tolist()
    if type(value) is dict: return {k: _materialize(torch, v) for k, v in value.items()}
    if type(value) in (tuple, list): return [_materialize(torch, v) for v in value]
    return value


def run_fixture(torch_module, PhysicsActionQueue, tap_module, *, n=3, seed=20261103):
    """Caller-only real CPU execution. Returns small receipt, writes no file.

    Baseline and observed queues are independently constructed from SAME original
    class/seed. No reset/RNG is patched; controlled lag assignment is synthetic
    test setup on both queues, not a DR/runtime-binding claim.
    """
    torch = torch_module
    provenance = validate_injections(torch, PhysicsActionQueue, tap_module)
    plan = build_plan(n)
    global_rng = torch.get_rng_state().clone()
    totals = {"state_bitwise_checks": 0, "owned_tensor_checks": 0, "normal_apply_ticks": 0,
              "original_method_identity_checks": 0, "partial_resets": 0, "same_tick_probes": 0}
    cases = []

    def check(base, observed):
        _equal(torch, _full_state(base), _full_state(observed), "full-original-queue/private-RNG")
        _equal(torch, global_rng, torch.get_rng_state(), "global-Torch-CPU-RNG")
        totals["state_bitwise_checks"] += 1

    def create(lags, capacity=8192):
        base, observed = [PhysicsActionQueue(n, "cpu", seed, enabled=True, physics_us=2500, control_us=20000) for _ in range(2)]
        assert type(base) is type(observed) is PhysicsActionQueue
        neutrals = {k: torch.zeros((n, w), dtype=torch.float32, device="cpu") for k, w in WIDTHS.items()}
        ids = torch.arange(n, dtype=torch.long, device="cpu")
        for key in WIDTHS:
            for q in (base, observed):
                q.reset(key, ids, neutrals[key], new_scene_clock=True)
                q.groups[key]["lag_steps"].fill_(lags[key])
        check(base, observed)
        probes = [_OriginalReturnProbe(q) for q in (base, observed)]
        envs = [FakeEnv(q, p) for q, p in zip((base, observed), probes)]
        tap = tap_module.install_actuation_tap(envs[1], capacity=capacity)
        return base, observed, probes, envs, tap, neutrals

    def close(probes, envs, tap):
        assert tap.close()["restored"]
        for env in envs:
            for term in env._physics_action_delay.terms.values():
                assert "process_actions" not in term.__dict__ and "apply_actions" not in term.__dict__
                assert "set_joint_position_target" not in term._asset.__dict__
                assert "set_joint_velocity_target" not in term._asset.__dict__
        for probe in probes: probe.remove()
        assert tap.close()["restored"]
        totals["original_method_identity_checks"] += 1

    def control(base, observed, probes, envs, tap, start):
        check(base, observed)
        for key, width in WIDTHS.items():
            values = torch.arange(n * width, dtype=torch.float32, device="cpu").reshape(n, width) / 32 + start / 8
            for env in envs:
                env._sim_step_counter = start
                term = env._physics_action_delay.terms[key]
                arg = values.clone()
                result = term.process_actions(arg)
                assert result is term.issue_token and term.last_actions is arg
            check(base, observed)
        expected_episode = {k: observed.groups[k]["episode"].tolist() for k in WIDTHS}
        for tick in range(start, start + 8):
            for key in WIDTHS:
                for env in envs:
                    env._sim_step_counter = tick + 1
                    term = env._physics_action_delay.terms[key]
                    assert term.apply_actions() is term.apply_token
                check(base, observed)
                a, b = [q.receipt(key, tick) for q in (base, observed)]
                _equal(torch, a, b, "original-receipt")
                valid = observed.groups[key]["applied_valid"]
                expected = observed.groups[key]["lag_steps"][valid] * 2500
                _equal(torch, b["actual_first_transition_delay_us"][valid], expected, "first-latency-not-held-age")
                if start == 8 and tick == 8 and int(observed.groups[key]["lag_steps"][0]) > 0:
                    assert int(b["held_command_sample_age_us"][0]) == 20000
                totals["normal_apply_ticks"] += 1
        events = tap.drain()
        status = tap.status()
        assert status["observer_errors"] == 0 and status["dropped_events"] == 0
        for event in events:
            if event["kind"] != "queue_apply": continue
            captured = event["selected_target"]
            assert torch.is_tensor(captured) and captured.device.type == "cpu"
            original = observed.groups[event["group"]]["applied"]
            returned = probes[1].return_values[(event["group"], event["tick"])]
            assert captured.data_ptr() != original.data_ptr() and captured.data_ptr() != returned.data_ptr()
            for field in FIELDS:
                source = observed.groups[event["group"]][field]
                assert event["pre"][field].data_ptr() != source.data_ptr()
                assert event["post"][field].data_ptr() != source.data_ptr()
            before = _full_state(observed)
            returned_before = returned.clone()
            saved = captured.clone()
            captured.add_(123)
            _equal(torch, before, _full_state(observed), "captured-Tensor-owned-no-alias")
            _equal(torch, returned_before, returned, "captured-Tensor-not-return-alias")
            captured.copy_(saved)
            totals["owned_tensor_checks"] += 1
        tap_module.validate_apply_window(_materialize(torch, events), start, expected_episode, status)
        assert probes[0].calls == probes[1].calls, "Observer invoked original extra times"
        check(base, observed)
        return events

    for item in plan:
        base, observed, probes, envs, tap, neutrals = create(item["lags"])
        try:
            for start in item["controls"]: control(base, observed, probes, envs, tap, start)
            # Partial reset is the ORIGINAL queue method, never patched by tap.
            for key in WIDTHS:
                before = observed.state_dict()["groups"][key]
                for q in (base, observed): q.reset(key, [1], neutrals[key])
                after = observed.groups[key]
                others = [i for i in range(n) if i != 1]
                for field in FIELDS: _equal(torch, before[field][others], after[field][others], "unselected-reset-row/" + field)
                _equal(torch, before["last_apply_tick"], after["last_apply_tick"], "global-physics-clock-preserved")
                assert int(after["episode"][1]) == int(before["episode"][1]) + 1
                for field in ("pending_valid", "applied_valid"): assert not bool(after[field][1])
                for field in ("issued_tick", "due_tick", "applied_issue_tick", "first_apply_tick", "last_submit_tick"): assert int(after[field][1]) == -1
                for field in ("pending", "applied"): _equal(torch, after[field][1], neutrals[key][1], "selected-neutral")
                check(base, observed)
                totals["partial_resets"] += 1
            control(base, observed, probes, envs, tap, 16)
            cases.append({"legs_lag": item["lags"]["legs"], "wheels_lag": item["lags"]["wheels"], "two_controls_and_post_partial_reset": "PASS"})
        finally: close(probes, envs, tap)
        check(base, observed)

    # Same-tick idempotency and original exception semantics, separate from the
    # strict eight-unique-callback validator (which intentionally rejects repeats).
    base, observed, probes, envs, tap, neutrals = create({"legs": 2, "wheels": 1})
    try:
        for key, width in WIDTHS.items():
            x = torch.ones((n, width), dtype=torch.float32, device="cpu")
            for q in (base, observed): assert q.submit(key, x, 0) is None
            for operation in ("submit-repeat", "submit-different", "apply-repeat", "apply-skipped"):
                saved = [_full_state(q) for q in (base, observed)]
                messages = []
                if operation == "apply-repeat":
                    for q in (base, observed): q.apply(key, 0)
                    saved = [_full_state(q) for q in (base, observed)]
                for i, q in enumerate((base, observed)):
                    try:
                        if operation == "submit-repeat": assert q.submit(key, x, 0) is probes[i].last["submit"] is None
                        elif operation == "submit-different": q.submit(key, x + 1, 0)
                        elif operation == "apply-repeat": assert q.apply(key, 0) is probes[i].last["apply"]
                        else: q.apply(key, 2)
                    except AssertionError as exc:
                        method = "submit" if operation.startswith("submit") else "apply"
                        assert exc is probes[i].errors[method], "Original exception identity changed"
                        messages.append((type(exc).__name__, str(exc)))
                if operation in ("submit-different", "apply-skipped"):
                    assert len(messages) == 2 and messages[0] == messages[1]
                else: assert not messages
                for q, old in zip((base, observed), saved): _equal(torch, old, _full_state(q), "sameTick/rejected-call-state-unchanged")
                check(base, observed)
                totals["same_tick_probes"] += 1
        assert probes[0].calls == probes[1].calls
    finally: close(probes, envs, tap)
    check(base, observed)

    # Bounded buffer: original queue state/RNG still exact even when tap loses coverage.
    base, observed, probes, envs, tap, neutrals = create({"legs": 0, "wheels": 2}, capacity=1)
    try:
        for key, width in WIDTHS.items():
            for env in envs:
                env._sim_step_counter = 0
                env._physics_action_delay.terms[key].process_actions(torch.zeros((n, width), dtype=torch.float32, device="cpu"))
        for tick in range(8):
            for key in WIDTHS:
                for env in envs:
                    env._sim_step_counter = tick + 1
                    env._physics_action_delay.terms[key].apply_actions()
                check(base, observed)
        status = tap.status()
        assert status["dropped_events"] > 0 and status["observer_errors"] == 0
        events = tap.drain()
        assert len(events) <= 1 and probes[0].calls == probes[1].calls
        try: tap_module.validate_apply_window(_materialize(torch, events), 0, {}, status)
        except tap_module.CaptureUnknown: pass
        else: raise AssertionError("Overflow was promoted to complete coverage")
    finally: close(probes, envs, tap)
    check(base, observed)
    return {"status": "REAL_TORCH_CPU_ORIGINAL_QUEUE_COMPONENT_FIXTURE_PASS_NOT_SDK",
            "provenance": provenance, "n": n, "cases": cases, "totals": totals,
            "original_queue_private_rng_and_full_state_bitwise_equal": True,
            "global_torch_cpu_rng_unchanged": True, "captured_cpu_tensors_owned": True,
            "same_tick_and_original_exception_identity": True, "bounded_overflow_unknown": True,
            "fake_scaffolding": ["FakeEnv", "FakeAsset", "FakeActionTerm"],
            "runtime_source_binding": "UNKNOWN", "physical_readback": "UNKNOWN", "actor35": "NOT_TESTED",
            "actual_sdk_pass": False, "gate1_admitted": False, "exact": False, "stage2": False}
