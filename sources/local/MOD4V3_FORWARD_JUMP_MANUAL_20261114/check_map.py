"""Check single-tile loading, terrain replacement, and one-shot learned jumps."""
import json
import time
from types import SimpleNamespace
import numpy as np
from manual_jump import JumpControl, JumpSimulation, HERE, save_json
from map_terrain import SOURCE, NAMES


def main():
    out = HERE / "evidence/single_tile_check_r1"
    out.mkdir(parents=True, exist_ok=False)
    for name in ("manual_jump.py", "map_terrain.py", "check_map.py"):
        (out / name).write_bytes((HERE / name).read_bytes())
    sim = JumpSimulation(terrain=True)
    terrain, m, d = sim.terrain, sim.env.m, sim.env.d
    visual_count = sum((m.geom(i).name or "").startswith("map_visual_") for i in range(m.ngeom))
    assert visual_count == 1
    assert m.nhfield == 0
    stair_model = dict(meshes=m.nmesh, geoms=m.ngeom, terrain_tiles=visual_count)
    tile = terrain.tile()
    center = terrain.center(tile)
    ground_samples = [terrain.ground(m, d, center[0]+offset, center[1]) for offset in (-4.,-2.,0.)]
    with np.load(SOURCE/"tiles"/(tile["name"]+".npz")) as source:
        expected = np.unique(source["vertices"][:,2]).tolist()
    assert np.allclose(ground_samples, expected, atol=1e-6), (ground_samples, expected)
    control = JumpControl.__new__(JumpControl)
    control.sim, control.keys = sim, set()
    control._event = lambda text: None
    control._focus_control = lambda: None
    control.level_var = SimpleNamespace(get=lambda: 3)
    control.speed_var = SimpleNamespace(get=lambda: .6)
    control.turn_var = SimpleNamespace(get=lambda: 1.)
    control.family_var = SimpleNamespace(get=lambda: NAMES[2])
    control.go_to_terrain()
    slope_model = control.sim.env.m
    assert slope_model.nhfield == 1
    assert sum((slope_model.geom(i).name or "").startswith("map_visual_") for i in range(slope_model.ngeom)) == 1
    control.family_var = SimpleNamespace(get=lambda: NAMES[8])
    control.go_to_terrain()
    sim = control.sim
    assert sim.env.m.nhfield == 0
    assert sum((sim.env.m.geom(i).name or "").startswith("map_visual_") for i in range(sim.env.m.ngeom)) == 1
    sim.paused = False
    rows = []
    step_ms = []
    reset_before = sim.resets
    with (out/"trajectory.jsonl").open("w", encoding="utf8") as log:
        def advance(n, repeat=False):
            for _ in range(n):
                if repeat:
                    control._handle_key_down("space")
                start = time.perf_counter()
                sim.step(control.keys)
                step_ms.append((time.perf_counter()-start)*1000.)
                log.write(json.dumps(dict(keys=sorted(control.keys), **sim.telemetry()))+"\n")
        advance(50)
        control._handle_key_down("w")
        advance(75)
        control._handle_key_down("space")
        first = sim.requests
        advance(175, repeat=True)
        rows.append(dict(case="moving_space_hold", accepted=bool(sim.last_jump and sim.last_jump["accepted"]),
                         single_request=sim.requests == first, returned_to_drive=sim.phase == 0, last=sim.last_jump))
        control._handle_key_up("space")
        control._handle_key_down("space")
        advance(175, repeat=True)
        rows.append(dict(case="second_space_without_reset", accepted=bool(sim.last_jump and sim.last_jump["accepted"]),
                         single_request=sim.requests == first+1, returned_to_drive=sim.phase == 0, last=sim.last_jump))
    passed = all(r["accepted"] and r["single_request"] and r["returned_to_drive"] for r in rows) and sim.resets == reset_before
    result = dict(epoch=time.time(), passed=passed, visible_tiles=visual_count, rows=1, cols=1,
                  stair_model=stair_model, slope_heightfields=int(slope_model.nhfield),
                  terrain_switches_checked=["Wide stairs", "Slope", "Flat"],
                  headless_step_ms_mean=float(np.mean(step_ms)), headless_step_ms_p95=float(np.percentile(step_ms,95)),
                  map_source_scope=terrain.manifest["scope"], stair_case=tile["name"],
                  exact_source_stair_heights_m=expected, compiled_collision_stair_heights_m=ground_samples,
                  cases=rows, resets=sim.resets-reset_before, final=sim.telemetry())
    save_json(out/"RESULT.json", result)
    print(json.dumps(result, indent=2), flush=True)
    sim.close()
    assert passed


if __name__ == "__main__":
    main()
