"""One C2 case via the frozen formal runner, plus read-only packet/controller logs."""
from pathlib import Path
from dataclasses import asdict
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from RM_FPS_PLAYER_V1 import runtime
from RM_ROBUSTNESS_V1 import run_t01_formal as formal
from RM_ROBUSTNESS_V1.t01_contact_audit import AuditedPlant
from RM_ROBUSTNESS_V1.controller_heading_follow_v2 import GroundController


def main():
    case = sys.argv[sys.argv.index('--case')+1]
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', case):
        raise ValueError('Plain fresh case ID required')
    directory = Path(__file__).resolve().parent/'heading_follow_v2'
    if (directory/'runs'/case).exists():
        raise FileExistsError('Consumed output directory; do not rerun')
    diagnostic_dir = directory/'diagnostic_logs'
    diagnostic_dir.mkdir(parents=True, exist_ok=True)
    diagnostic_path = diagnostic_dir/(case+'.jsonl')
    original_controller, original_directory = runtime.GroundController, formal.D
    original_packet = AuditedPlant.sensor_packet
    instance, last_packet = [], [None]
    with diagnostic_path.open('x', encoding='utf-8', buffering=1) as diagnostic:
        def packet(plant, *args, **kwargs):
            p = original_packet(plant, *args, **kwargs)
            last_packet[0] = None if p is None else asdict(p)
            return p
        class BoundController(GroundController):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs, geometry=runtime.bridge.geometry())
                instance.append(self)
            def command(self, e, forward, yaw_rate):
                tau = super().command(e, forward, yaw_rate)
                row = dict(raw_packet=last_packet[0], estimated14=e.state14,
                    estimated_roll=e.roll, estimated_omega_body=e.omega_body,
                    sensor_age_s=e.sensor_age_s, requested_tau6_Nm=tau,
                    control=self.control_diagnostic,
                    timestamp_note='packet queue epoch; channel window/endpoints differ')
                diagnostic.write(json.dumps(formal.safe(row), ensure_ascii=False,
                    allow_nan=False, separators=(',', ':'))+'\n')
                return tau
        try:
            runtime.GroundController = BoundController
            AuditedPlant.sensor_packet = packet
            formal.D = directory
            formal.main()
        finally:
            runtime.GroundController, formal.D = original_controller, original_directory
            AuditedPlant.sensor_packet = original_packet
            if instance and (directory/'runs'/case).is_dir():
                formal.dump(directory/'runs'/case/'candidate_diagnostics.json',
                    dict(roll_follow=instance[-1].follow_diag,
                         final_control=instance[-1].control_diagnostic,
                         diagnostic_trace_path=str(diagnostic_path),
                         control_changes='only heading outer loop added to frozen C1',
                         diagnostic_changes='read-only packet/controller capture',
                         extra_truth_inputs=False))


if __name__ == '__main__':
    main()
