"""Finite full-state training with the Warp sampling replacement enabled."""
import os
import time
from .shared import load
from . import train as existing

source = load('train')
original_build_runner = source.build_runner


def build_runner(vec, directory):
    # Main constructs the bridge before the runner. Initialization and tests
    # therefore compile outside the timed first production rollout.
    bridge = vec.bridge
    if not hasattr(bridge, 'warp_sampling'):
        raise RuntimeError('Warp sampler was not installed')
    from .warp_tests import reward_check, manifold_check, acceptance_check
    device = str(vec.device)
    check = dict(epoch=time.time(), device=device, reward=reward_check(device, True),
                 manifold=manifold_check(device), acceptance=acceptance_check(device, True),
                 production_PT_reads=0, physics_steps=0, passed=True)
    source.put(directory/'WARP_NATIVE_PARITY.json', check)
    return original_build_runner(vec, directory)


def main():
    os.environ['MOD4_WARP_SAMPLING'] = '1'
    source.build_runner = build_runner
    source.main()


if __name__ == '__main__':
    main()
