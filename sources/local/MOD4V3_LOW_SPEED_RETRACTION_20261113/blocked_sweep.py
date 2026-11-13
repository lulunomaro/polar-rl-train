"""Bounded post-block retraction probes, all from naturally reached states."""
from pathlib import Path
import argparse
import json
from replay_probe import T, setup, run_case

p = argparse.ArgumentParser()
p.add_argument('--snapshot', type=int, required=True)
p.add_argument('--out', required=True)
p.add_argument('--model', choices=['teacher', 'parent'], default='teacher')
p.add_argument('--source', required=True)
p.add_argument('--seconds', type=float, default=8.)
p.add_argument('--deltas', type=float, nargs='+', default=[.173, .35, .65])
p.add_argument('--durations', type=float, nargs='+', default=[.16, .30, .60])
p.add_argument('--mean-offsets', type=float, nargs='+', default=[0.])
a = p.parse_args()
out = Path(a.out).resolve()
out.mkdir(parents=True, exist_ok=False)
show = setup(out, a.model)
rows = []
for delta in a.deltas:
    for duration in a.durations:
        for offset in a.mean_offsets:
            intervention = f'retract{delta:g}_{duration:g}_{offset:g}'
            rows.append(run_case(show, out, a.model, .4, 0, a.seconds,
                                 intervention=intervention,
                                 restore=dict(path=str(Path(a.source).resolve()), index=a.snapshot)))
            (out / 'PROGRESS.json').write_text(json.dumps(rows, indent=2) + '\n')
