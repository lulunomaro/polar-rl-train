"""Load an independent E0 checkpoint into the existing WASD expert ensemble."""
from argparse import ArgumentParser
import hashlib
import json
import os
from pathlib import Path
import sys

import torch
from torch import nn

HERE = Path(__file__).resolve().parent
PLAYER = HERE.parent / 'MOD4V3_AUTONOMOUS_MOE_REPAIR_20261120'
sys.path.insert(0, str(PLAYER))
import play_repaired as player

ORIGINAL_LOADER = player.load_manifest


class BlendedDrive(nn.Module):
    def __init__(self, original, candidate, forward_fraction, neutral_fraction, reverse_fraction,
                 height_blend=None):
        super().__init__()
        self.original = original
        self.candidate = candidate
        self.fractions = (reverse_fraction, neutral_fraction, forward_fraction)
        self.height_blend = height_blend

    def forward(self, observation):
        command = observation[..., :1]
        reverse, neutral, forward = self.fractions
        # Interpolate in the command window the player crosses during a gear change.
        fraction = torch.lerp(command.new_tensor(neutral), command.new_tensor(forward), (command/.15).clamp(0,1))
        fraction = torch.lerp(fraction, command.new_tensor(reverse), (-command/.15).clamp(0,1))
        if self.height_blend is not None:
            lower, upper = self.height_blend
            # obs[3] carries the live stance command, scaled by five.
            height = observation[..., 3:4] / 5.
            fraction = fraction * ((height - lower) / (upper - lower)).clamp(0.0, 1.0)
        original = self.original(observation)
        if not torch.any(fraction):
            return original
        return torch.lerp(original, self.candidate(observation), fraction)


def load_drive(original, checkpoint, expected_sha, fractions=(1., 1., 1.), height_blend=None):
    if any(not 0. <= float(fraction) <= 1. for fraction in fractions) or len(fractions) != 3:
        raise ValueError('Expected three fractions in [0,1] ordered forward, neutral, reverse')
    if height_blend is not None:
        height_blend = tuple(map(float, height_blend))
        if len(height_blend) != 2 or not .20 <= height_blend[0] < height_blend[1] <= .42:
            raise ValueError('height_blend must be a rising interval within the supported stance range')
    sha = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    if sha != expected_sha:
        raise ValueError(f'E0 checkpoint digest differs: {sha}')
    payload = torch.load(checkpoint, map_location='cpu', weights_only=False)
    actor = player.stair.build_c874_mlp()
    actor.load_state_dict({k.removeprefix('mlp.'): value for k,value in payload['actor_state_dict'].items()
                           if k.startswith('mlp.')}, strict=True)
    actor.eval().requires_grad_(False)
    if height_blend is None and all(float(fraction) == 1. for fraction in fractions):
        drive = actor
    else:
        drive = BlendedDrive(original, actor, *map(float, fractions),
                             height_blend=height_blend).eval().requires_grad_(False)
    return drive


def manifest_drive(original, manifest_path, config):
    checkpoint = (manifest_path.parent / os.path.expandvars(config['e0_checkpoint'])).resolve()
    return load_drive(original, checkpoint, config['e0_sha256'], config.get('fractions', (1., 1., 1.)),
                      config.get('height_blend_m'))


def install_e0(policy, manifest_path, config):
    drive = manifest_drive(policy.stair.e0, manifest_path, config)
    # E0 appears in the output of the main stair model and each height entry.
    # Their internal E1 loco_base, all routing heads and all E2 weights stay pinned.
    policy.stair.e0 = drive
    for _, expert in policy.stair_height_bank:
        expert.e0 = drive
    policy.provenance['drive_e0'] = config['e0_sha256']
    identity = dict(parent=policy.runtime_sha, drive_e0=config['e0_sha256'], fractions=config.get('fractions', [1., 1., 1.]),
                    height_blend=config.get('height_blend_m'),
                    loader=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    policy.runtime_sha = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    return policy


def load_candidate(manifest):
    config = json.loads(manifest.read_text(encoding='utf-8'))
    baseline = (manifest.parent / config['baseline']).resolve()
    policy, hashes, prep = ORIGINAL_LOADER(baseline)
    if policy.runtime_sha != config['baseline_runtime_sha256']:
        raise ValueError(f'MoE base digest differs: {policy.runtime_sha}')
    install_e0(policy, manifest, config)
    return policy, {**hashes, 'drive_e0': config['e0_sha256']}, prep


def main():
    parser = ArgumentParser()
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--status-file', type=Path)
    parser.add_argument('--proving-ground', action='store_true')
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    status = args.status_file or candidate.with_name('PLAYER_STATUS.json')
    player.maps.CACHE_DIR = status.parent / 'scene_cache' / str(os.getpid())
    player.load_manifest = load_candidate
    sys.argv = [str(player.__file__), '--candidate', str(candidate), '--status-file', str(status)]
    if args.proving_ground:
        sys.argv.append('--proving-ground')
    player.main()


if __name__ == '__main__':
    main()
