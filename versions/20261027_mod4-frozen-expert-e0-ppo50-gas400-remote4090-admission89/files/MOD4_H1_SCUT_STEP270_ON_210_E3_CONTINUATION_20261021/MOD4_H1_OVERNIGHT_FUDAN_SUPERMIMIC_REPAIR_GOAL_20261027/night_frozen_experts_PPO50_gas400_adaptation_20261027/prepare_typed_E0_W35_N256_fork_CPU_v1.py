"""Explicit new source qualification: complete core + selected DR population, no physics.

The original source files/labels stay immutable. This is a population/clock/plant
fork, not exact PhysX continuation. Target CUDA restore and one new episode still
have to run before training; no private CUDA stream is converted to a CPU stream.
"""
from pathlib import Path
import copy, hashlib, json, os, sys, time, traceback

HERE = Path(__file__).resolve().parent
W = HERE.parents[2]
ORIGINAL = W / "MOD4_S4_GATE_FIRST_FINAL_FROZEN35_20261015/payload/source"
SPEC = {
    "E0": ("E0_frozen_source.pt", "b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8", 31903, 639560),
    "W35": ("E1_WAVE35_frozen_source.pt", "b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd", 32259, 646800),
}
CORE = {"actor_state_dict", "critic_state_dict", "optimizer_state_dict", "iter"}
PER_ENV = {"sensor_DR_state", "feedback_delay_state", "physical_action_delay_state", "spring_pressure_state", "gas_damping_state", "chassis_PD_state", "E1_terrain_state", "E1_retained_flat_command_state"}
OLD_N, NEW_N = 20000, 256

def H(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def exact(a, b, torch):
    if torch.is_tensor(a):
        return torch.is_tensor(b) and a.dtype == b.dtype and a.shape == b.shape and torch.equal(a, b)
    if isinstance(a, dict):
        return isinstance(b, dict) and set(a) == set(b) and all(exact(a[k], b[k], torch) for k in a)
    if isinstance(a, (list, tuple)):
        return type(a) is type(b) and len(a) == len(b) and all(exact(x, y, torch) for x, y in zip(a, b))
    return type(a) is type(b) and a == b

def main():
    out = HERE / "typed_source_forks_v1"
    assert not out.exists()
    out.mkdir()
    import torch
    torch.set_num_threads(2)
    cpu_rng = torch.get_rng_state().clone()
    all_rows = {}
    for role, (name, expected_sha, iteration, adam) in SPEC.items():
        source = ORIGINAL / name
        assert H(source) == expected_sha
        # The second source load is solely this declared new transformation;
        # earlier metadata inspection is already a separate preserved attempt.
        ck = torch.load(source, map_location="cpu", weights_only=False)
        assert ck["iter"] == iteration
        assert ck["actor_state_dict"]["mlp.0.weight"].shape == (256, 35)
        assert ck["critic_state_dict"]["mlp.0.weight"].shape == (256, 38)
        assert len(ck["optimizer_state_dict"]["state"]) == 17
        assert {int(v["step"]) for v in ck["optimizer_state_dict"]["state"].values()} == {adam}
        assert ck["spring_pressure_state"]["n"] == OLD_N
        assert ck["spring_pressure_recipe"]["nominal_stiffness_N_m"] == 3500
        assert ck["physical_action_delay_state"]["control_us"] == 10000
        result = copy.deepcopy(ck)
        changes, leaves = [], []
        def project(value, path):
            if torch.is_tensor(value):
                axes = [i for i, width in enumerate(value.shape) if width == OLD_N]
                assert len(axes) <= 1, (path, value.shape)
                leaf = {"path": path, "shape": list(value.shape), "dtype": str(value.dtype), "projected_axis": axes[0] if axes else None}
                leaves.append(leaf)
                if axes:
                    assert path.split('/')[0] in PER_ENV, path
                    assert axes == [0], ("unreviewed nonleading population axis", path)
                    transformed = value[:NEW_N].clone()
                    assert torch.equal(transformed, value[:NEW_N])
                    changes.append({"path": path, "kind": "select_original_env_ids_0_through_255", "before": list(value.shape), "after": list(transformed.shape)})
                    return transformed
                return value.clone()
            if isinstance(value, dict):
                return {k: project(v, path + '/' + str(k)) for k, v in value.items()}
            if isinstance(value, (list, tuple)):
                return type(value)(project(v, path + '/' + str(i)) for i, v in enumerate(value))
            if type(value) is int and value == OLD_N and path.rsplit('/', 1)[-1] in {"n", "num_envs"}:
                assert path.split('/')[0] in PER_ENV, path
                changes.append({"path": path, "kind": "explicit_population_count", "before": OLD_N, "after": NEW_N})
                return NEW_N
            return copy.deepcopy(value)
        for key in PER_ENV & set(ck):
            result[key] = project(ck[key], key)
        for key in set(ck) - PER_ENV:
            assert exact(result[key], ck[key], torch), key
        # All saved history is restored first, then original fresh-episode reset
        # clears timestamps/targets. No timestamp rescale or fake extra history.
        result["physical_action_delay_state"]["control_us"] = 20000
        result["physical_action_delay_recipe"]["control_period_us"] = 20000
        result["spring_pressure_recipe"]["nominal_stiffness_N_m"] = 2000
        result["spring_pressure_recipe"]["actual_stiffness_bounds_N_m"] = [1800, 2200]
        for key in CORE:
            assert exact(result[key], ck[key], torch)
        # Global and named CUDA RNG bytes retained literally, with the original
        # CUDA codec. Smaller new populations intentionally draw fewer values.
        for key in ck:
            if "rng" in key.lower():
                assert exact(result[key], ck[key], torch), key
        provenance = {
            "schema": "mod4.frozen_expert.PPO50_gas400_typed_fork.v1", "role": role,
            "original_source_path": str(source), "original_source_SHA": expected_sha,
            "original_iter": iteration, "original_Adam_step": adam,
            "original_population": OLD_N, "target_population": NEW_N, "selected_original_env_ids": list(range(NEW_N)),
            "policy_hz_before": 100, "policy_hz_after": 50, "physics_dt_s": .0025, "decimation": 8,
            "gas_nominal_k_before_N_m": 3500, "gas_nominal_k_after_N_m": 2000,
            "gas_upper_q_after_m": .020639440248416612, "gas_lower_q_m": -.0267046843609,
            "gas_damping_Ns_m": 3, "hardware_force_curve_calibrated": False,
            "actor35_critic38_STD_17Adam_all_literal_original": True,
            "relative_DR_factors_and_private_streams_retained": True,
            "original_history_restored_then_one_real_reset_required": True,
            "population_and_physics_changed_not_exact_PhysX_resume": True,
            "target_SDK_or_CUDA_or_physics_verified": False, "training_GO": False,
            "original_frozen_qualification_retained": True, "new_branch_skill_qualified": False,
            "producer_path": str(Path(__file__).resolve()), "producer_SHA": H(__file__),
        }
        result["PPO50_gas400_adaptation"] = provenance
        target = out / (role + "_N256_PPO50_GAS400_TYPED_SOURCE_NOT_GPU_ADMITTED.pt")
        torch.save(result, target)
        saved = torch.load(target, map_location="cpu", weights_only=False)
        assert exact(saved, result, torch)
        all_rows[role] = {"source": provenance, "target": {"path": str(target), "bytes": target.stat().st_size, "SHA": H(target)},
                          "per_env_transformations": changes, "source_tensor_leaf_schema": leaves,
                          "other_changed_fields": ["physical_action_delay_state/control_us", "physical_action_delay_recipe/control_period_us", "spring_pressure_recipe/nominal_stiffness_N_m", "spring_pressure_recipe/actual_stiffness_bounds_N_m", "PPO50_gas400_adaptation"],
                          "actual_saved_roundtrip_exact": True}
    assert torch.equal(cpu_rng, torch.get_rng_state()) and not torch.cuda.is_initialized()
    report = HERE / "reports/TYPED_N256_SOURCE_FORK_CPU_ACTUAL_V1.json"
    with report.open("x", encoding="utf8") as f:
        json.dump({"attempt_id": "E0_W35_TYPED_N256_PPO50_GAS400_SOURCE_CPU_20261027_V1", "epoch": time.time(), "roles": all_rows,
                   "CPU_rng_unchanged": True, "no_GPU_remote_or_budget": True, "Git_status": "pending_root_ordinary_supplement"}, f, ensure_ascii=False, indent=2)
    print(json.dumps({"report": str(report), "roles": {k: v["target"] for k, v in all_rows.items()}, "not_GPU_admitted": True}))

if __name__ == "__main__":
    try:
        main()
    except Exception:
        p = HERE / ("reports/TYPED_N256_ORIGINAL_ERROR_" + str(time.time_ns()) + ".json")
        p.parent.mkdir(exist_ok=True)
        p.write_text(json.dumps({"epoch": time.time(), "traceback": traceback.format_exc(), "no_GPU_remote_budget": True}, indent=2), encoding="utf8")
        raise
