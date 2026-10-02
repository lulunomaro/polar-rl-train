"""Print the symmetric hard-stop envelope across hip angles."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "chassis_mod4_work"))
import simulate_folded_pose as folded  # noqa: E402

for hip in (-0.50, -0.45, -0.40, -0.35, -0.30, -0.25, -0.20,
            -0.15, -0.10, 0.00, 0.10, 0.20, 0.30, 0.40, 0.50):
    row = folded.set_pose(hip, -0.7, 0.0, -1.0)
    wheel_x = float(folded.data.xpos[folded.WHEELS[0], 0])
    print(
        f"hip={hip:+.3f} leg={row['leg_height_m']:.6f} "
        f"full={row['full_height_m']:.6f} low_nonwheel={row['lowest_nonwheel_m']:.6f} "
        f"root={row['root_height_m']:.6f} wheel_x={wheel_x:+.6f}"
    )
