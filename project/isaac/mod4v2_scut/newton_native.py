"""Finite native import/physics evidence for the requested backend migration."""
from pathlib import Path
import argparse
import json
import time
import traceback

import numpy as np
import warp as wp

from .newton_model import NewtonPlant


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--package', required=True)
    p.add_argument('--report', required=True, type=Path)
    p.add_argument('--cpu', action='store_true')
    p.add_argument('--num-envs', type=int, default=1)
    p.add_argument('--ticks', type=int, default=20)
    a = p.parse_args()
    result = dict(epoch=time.time(), kind='ACTUAL_NEWTON_NATIVE',
                  model_reads=0, PPO_updates=0, physical_ticks=0, passed=False)
    try:
        plant = NewtonPlant(a.package, a.num_envs, 'cpu' if a.cpu else 'cuda:0', a.cpu)
        result['model'] = plant.receipt
        assert plant.model.body_count == 31*a.num_envs
        assert plant.solver.mj_model.neq == 10
        result['initial_q'] = plant.state.joint_q.numpy().tolist()
        for tick in range(a.ticks):
            plant.step()
            result['physical_ticks'] += 1
        wp.synchronize()
        q, v = plant.state.joint_q.numpy(), plant.state.joint_qd.numpy()
        result.update(final_q=q.tolist(), final_v=v.tolist(),
                      finite=bool(np.isfinite(q).all() and np.isfinite(v).all()))
        assert result['finite']
        result['passed'] = True
    except Exception:
        result['error'] = traceback.format_exc()
    a.report.parent.mkdir(parents=True, exist_ok=True)
    with a.report.open('x', encoding='utf8') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
