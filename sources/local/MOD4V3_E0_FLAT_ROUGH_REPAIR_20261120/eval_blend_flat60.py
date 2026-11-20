"""Run the existing flat60 protocol with only the E0 forward function replaced."""
from argparse import ArgumentParser
import hashlib
import json
from pathlib import Path
import runpy
import sys

from eval_drive import BASELINES, REPO
from play_e0_candidate import manifest_drive


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.manifest.read_text(encoding='utf-8'))
    original = REPO / BASELINES['c874'][0]
    replay_root = REPO / 'sources/local/MOD4V3_STEP7_DELAY_DIAG_20261110'
    sys.path.insert(0, str(replay_root))
    import replay_delay_diagnostic as replay

    simulation_type = replay.Simulation

    def make_simulation(options):
        simulation = simulation_type(options)
        simulation.actor = manifest_drive(simulation.actor, args.manifest, config)
        return simulation

    replay.Simulation = make_simulation
    protocol = REPO / 'sources/local/MOD4V3_LOW_SPEED_STAIR_CURRICULUM_2H_20261116/fixed_60_eval.py'
    sys.argv = [str(protocol), '--model', str(original), '--out', str(args.out)]
    runpy.run_path(str(protocol), run_name='__main__')
    result_file = args.out/'RESULT.json'
    result = json.loads(result_file.read_text(encoding='utf-8'))
    result['sha256_is_base_checkpoint'] = True
    result['e0_blend'] = {'manifest': str(args.manifest),
                          'manifest_sha256': hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
                          'patched_actor_checkpoint_sha256': config['e0_sha256'],
                          'fractions': config.get('fractions'), 'height_blend_m': config.get('height_blend_m')}
    result_file.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
