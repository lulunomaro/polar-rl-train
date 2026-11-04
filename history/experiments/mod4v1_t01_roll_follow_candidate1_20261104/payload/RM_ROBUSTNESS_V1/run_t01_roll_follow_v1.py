"""One candidate-1 case through the frozen formal runner, no baseline source edit."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from RM_FPS_PLAYER_V1 import runtime
from RM_ROBUSTNESS_V1 import run_t01_formal as formal
from RM_ROBUSTNESS_V1.controller_roll_follow_v1 import GroundController


def main():
    original_controller, original_directory = runtime.GroundController, formal.D
    instance = []
    class BoundController(GroundController):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs, geometry=runtime.bridge.geometry())
            instance.append(self)
    case = sys.argv[sys.argv.index('--case')+1] if '--case' in sys.argv else None
    directory = Path(__file__).resolve().parent/'roll_follow_v1'
    try:
        runtime.GroundController = BoundController
        formal.D = directory
        formal.main()
    finally:
        runtime.GroundController, formal.D = original_controller, original_directory
        if instance and case and (directory/'runs'/case).is_dir():
            formal.dump(directory/'runs'/case/'candidate_diagnostics.json', instance[-1].follow_diag)


if __name__ == '__main__':
    main()
