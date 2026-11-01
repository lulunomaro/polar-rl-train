import json,shutil,numpy as np
from hybrid_trial import run
from control_core import ROOT
cfg=json.load(open(ROOT/'results/mpc_phases_v2/best_config.json'));cfg['duration']=5.;folder=ROOT/'results/frozen_mpc_success_v1';folder.mkdir(exist_ok=False)
r,rows=run(cfg,True)
for name in ['hybrid_trial.py','full_lqr.py','control_core.py','dr_components.py','linear_mpc.py']:shutil.copy2(ROOT/name,folder/name)
(folder/'result.json').write_text(json.dumps(r,indent=2));(folder/'trajectory.json').write_text(json.dumps(rows));(folder/'config.json').write_text(json.dumps(cfg,indent=2));print(json.dumps(r),flush=True)
