import json,shutil,hashlib
from control_core import ROOT
from hybrid_trial import run
cfg=json.load(open(ROOT/'results/smooth_landing_v1/best_config.json'));cfg.update(duration=5.)
out,rows=run(cfg,True);folder=ROOT/'results/frozen_nominal_success_v5';folder.mkdir(exist_ok=False)
for name in ['hybrid_trial.py','full_lqr.py','control_core.py','dr_components.py','linear_mpc.py']:shutil.copy2(ROOT/name,folder/name)
(folder/'result.json').write_text(json.dumps(out,indent=2));(folder/'trajectory.json').write_text(json.dumps(rows));(folder/'config.json').write_text(json.dumps(cfg,indent=2));print(json.dumps(out),flush=True)
