"""Freeze module sources before the sensor-consistent feedback correction."""
import shutil,json,hashlib
from control_core import ROOT
folder=ROOT/'snapshots/before_sensor_consistent_v1';folder.mkdir(parents=True,exist_ok=False)
for name in ['hybrid_trial.py','full_lqr.py','control_core.py','dr_components.py','linear_mpc.py']:
    shutil.copy2(ROOT/name,folder/name)
(folder/'SHA256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.py')},indent=2))
print(str(folder),flush=True)
