"""Caller-injected future CPU purpose only; no import/loader/driver or local run."""
DERIVED_FIXTURE_SHA256 = "51aba475d2d0addc8ea97b88aba1ae9c024bb9b8bbf529bdad378a7074e481cb"


def run_c2_cpu_fixture(torch_module, PhysicsActionQueue, tap_module, derived_fixture, *, seed=20261103):
    f, torch = derived_fixture, torch_module
    assert f.hashlib.sha256(f.Path(f.__file__).read_bytes()).hexdigest() == DERIVED_FIXTURE_SHA256
    assert f.TAP_SHA256 == "ec10b09b77548c560611e641d685e2cee029c9778ff8c8852a8bf070243bd95d"
    legacy, non_term = [], []

    class AssetProbe(f.FakeAsset):
        # NEW fake instrumentation only; inherited original setter functions remain intact.
        def __init__(self):
            super().__init__(); self.calls, self.error = [], None
        def _write(self, key, target, joint_ids=None):
            self.calls.append((key, target, joint_ids))
            if self.error is not None: raise self.error  # Explicit synthetic fault, not SDK behavior.
            return super()._write(key, target, joint_ids)

    for n in (2, 3):
        core = f.run_fixture(torch, PhysicsActionQueue, tap_module, n=n, seed=seed)
        assert len(core["cases"]) == 9 and core["totals"]["normal_apply_ticks"] == 432
        legacy.append(core)  # Original 9-lag/reset/idempotence/overflow counts stay separate.
        global_rng = torch.get_rng_state().clone()
        queues = [PhysicsActionQueue(n, "cpu", seed, enabled=True, physics_us=2500, control_us=20000) for _ in range(2)]
        assert type(queues[0]) is type(queues[1]) is PhysicsActionQueue
        envs, assets = [f.FakeEnv(q, None) for q in queues], [AssetProbe(), AssetProbe()]
        for env, asset in zip(envs, assets):
            for term in env._physics_action_delay.terms.values(): term._asset = asset
        saved = [tap_module.freeze_memory(f._full_state(q)) for q in queues]
        assert all("rng" in x["full_original_state_dict"] for x in saved)
        f._equal(torch, saved[0], saved[1], "new-case-same-original-class-and-seed")
        tap = tap_module.install_actuation_tap(envs[1])
        counts = dict(observed_events=0, normal_returns=0, raised=0, owned_cpu_tensors=0, full_queue_and_rng_rounds=0)
        try:
            for counter in (0, 17):
                for key, width in f.WIDTHS.items():
                    method = "set_joint_position_target" if key == "legs" else "set_joint_velocity_target"
                    for fail in (False, True):
                        target = torch.arange(n*width, dtype=torch.float32, device="cpu").reshape(n, width)/64 + counter
                        ids = torch.arange(width, dtype=torch.long, device="cpu")
                        originals = (target.clone(), ids.clone())
                        error = RuntimeError("synthetic non-term setter fault") if fail else None
                        for env, asset in zip(envs, assets):
                            env._sim_step_counter, asset.error = counter, error
                            writer = getattr(asset, method)
                            original = writer.__wrapped__ if asset is assets[1] else writer
                            assert original.__func__ is getattr(f.FakeAsset, method)
                            before = len(asset.calls)
                            try:
                                result = writer(target, joint_ids=ids)
                            except RuntimeError as exc:
                                assert fail and exc is error
                            else:
                                assert not fail and result is asset.results[key]
                            assert len(asset.calls) == before+1
                            call = asset.calls[-1]
                            assert call[0] == key and call[1] is target and call[2] is ids
                        events = tap.drain(); assert len(events) == 1
                        e = events[0]
                        assert e["capture_schema"] == "ACTUATION_CLOCK_SCOPE_V2_SOURCE_DISABLED" and e["kind"] == "target_write"
                        assert e["group"]["status"] == "UNKNOWN" and e["tick"]["status"] == "NOT_APPLICABLE"
                        assert e["write_scope"] == "NON_TERM_SETTER" and e["parent_term_apply_seq"] is None
                        assert type(e["raw_stored_counter"]) is int and e["raw_stored_counter"] == counter
                        assert e["setter"]["method"] == method and e["setter"]["joint_ids_source"] == "kwargs.joint_ids"
                        assert e["setter"]["joint_ids"] is e["kwargs"]["joint_ids"]
                        assert e["outcome"] == ("RAISED" if fail else "RETURNED")
                        if fail: assert e["exception_identity"] == id(error) and e["exception_type"] == "RuntimeError"
                        for captured, source, expected in zip((e["args"][0], e["kwargs"]["joint_ids"]), (target, ids), originals):
                            assert torch.is_tensor(captured) and captured.device.type == source.device.type == "cpu"
                            assert captured.data_ptr() != source.data_ptr()
                            f._equal(torch, captured, expected, "owned-non-term-argument-initial-bytes")
                            captured.add_(1)
                            f._equal(torch, source, expected, "owned-non-term-argument-no-alias")
                            counts["owned_cpu_tensors"] += 1
                        for q, state in zip(queues, saved): f._equal(torch, state, f._full_state(q), "non-term-full-state-private-RNG-unchanged")
                        f._equal(torch, f._full_state(queues[0]), f._full_state(queues[1]), "new-baseline-vs-observed")
                        f._equal(torch, global_rng, torch.get_rng_state(), "non-term-global-CPU-RNG-unchanged")
                        counts["observed_events"] += 1; counts["raised" if fail else "normal_returns"] += 1
                        counts["full_queue_and_rng_rounds"] += 1
                        assert not tap.context and tap.status()["observer_errors"] == tap.status()["dropped_events"] == 0
        finally:
            assert tap.close()["restored"] and tap.close()["restored"]
        assert all(len(a.calls) == 8 for a in assets)
        assert all(not any(k in a.__dict__ for k in ("set_joint_position_target", "set_joint_velocity_target")) for a in assets)
        for q, state in zip(queues, saved): f._equal(torch, state, f._full_state(q), "new-case-final-state")
        f._equal(torch, global_rng, torch.get_rng_state(), "new-case-final-global-RNG")
        assert counts == dict(observed_events=8, normal_returns=4, raised=4, owned_cpu_tensors=16, full_queue_and_rng_rounds=8)
        non_term.append(dict(n=n, counters=[0, 17], totals=counts, each_asset_original_setter_calls=8,
                             fake_asset_instrumentation="NEW _write subclass; inherited original setters; synthetic faults only"))
    return dict(original_fixture_by_n=legacy, non_term_setter_by_n=non_term,
                original_fixture_normal_apply_ticks=sum(x["totals"]["normal_apply_ticks"] for x in legacy),
                runtime_source_binding="UNKNOWN", physical_readback="UNKNOWN", DOF_target_identity="UNKNOWN",
                actual_sdk_pass=False, gate1="UNKNOWN", exact=False, stage2_GO=False)
