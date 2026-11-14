"""Exercise held-space, repeated jumps and manual driving in live MuJoCo physics."""
from pathlib import Path
import json
import time
from manual_jump import JumpControl, JumpSimulation, HERE, save_json


def main():
    output = HERE / "evidence/controls_r1"
    output.mkdir(parents=True, exist_ok=False)
    (output / "player_source.py").write_bytes((HERE / "manual_jump.py").read_bytes())
    (output / "check_source.py").write_bytes(Path(__file__).read_bytes())
    sim = JumpSimulation()
    control = JumpControl.__new__(JumpControl)
    control.sim, control.keys = sim, set()
    control._event = lambda text: None
    rows = []
    with (output / "trajectory.jsonl").open("w", encoding="utf8") as log:
        def run(steps, repeated_space=False):
            for _ in range(steps):
                if repeated_space:
                    control._handle_key_down("space")
                sim.step(control.keys)
                log.write(json.dumps(dict(keys=sorted(control.keys), **sim.telemetry())) + "\n")

        run(75)
        for key, expected in (("w", 1), ("s", -1), ("a", 1), ("d", -1)):
            control._handle_key_down(key)
            run(75)
            actual = sim.env.vx if key in {"w", "s"} else float(sim.env.d.qvel[5])
            command = sim.cmd_vx if key in {"w", "s"} else sim.cmd_wz
            passed = actual * expected > .1 and command * expected > .1
            rows.append(dict(key=key, measured=actual, command=command, passed=passed))
            control._handle_key_up(key)
            run(60)
        control._handle_key_down("w")
        run(75)
        reset_before = sim.resets
        control._handle_key_down("space")
        first = sim.requests
        run(150, repeated_space=True)
        rows.append(dict(test="held_space_only_one_jump", passed=sim.requests == first and sim.phase == 0,
                         last_jump=sim.last_jump.copy(), resets=sim.resets-reset_before))
        run(50, repeated_space=True)
        rows.append(dict(test="held_after_landing_no_repeat", passed=sim.requests == first))
        control._handle_key_up("space")
        control._handle_key_down("space")
        run(150, repeated_space=True)
        rows.append(dict(test="release_and_press_second_jump", passed=sim.requests == first+1 and sim.phase == 0,
                         last_jump=sim.last_jump.copy(), resets=sim.resets-reset_before))
        control._handle_key_up("space")
        control._handle_key_up("w")
        control._handle_key_down("a")
        run(75)
        rows.append(dict(test="steer_after_landing", passed=sim.cmd_wz > .5 and sim.env.d.qvel[5] > .1))
        control._handle_key_up("a")
        run(50)
    result = dict(epoch=time.time(), rows=rows, passed=all(row["passed"] for row in rows),
                  events=sim.events, final=sim.telemetry())
    save_json(output / "RESULT.json", result)
    print(json.dumps(dict(passed=result["passed"], rows=rows), indent=2), flush=True)
    sim.close()
    assert result["passed"], "See per-case evidence"


if __name__ == "__main__":
    main()
