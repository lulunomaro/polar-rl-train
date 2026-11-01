"""Run a frozen final LQR/MPC case through complete MuJoCo and D0--D7."""
import argparse,json,shutil,hashlib
from pathlib import Path
from control_core import ROOT
from hybrid_trial import run

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--controller',choices=['lqr','mpc'],default='lqr')
    p.add_argument('--full-dr',action='store_true')
    p.add_argument('--seed',type=int,default=5047)
    p.add_argument('--duration',type=float,default=5.)
    p.add_argument('--out',required=True,help='a fresh result directory name')
    args=p.parse_args()
    folder=(ROOT/'results'/args.out).resolve()
    if not folder.is_relative_to((ROOT/'results').resolve()):raise ValueError('output must stay below task results')
    folder.mkdir(parents=True,exist_ok=False)
    catalog=json.load(open(ROOT/'results/FINAL_EVIDENCE_V2/controllers.json'))
    cfg=dict(catalog[args.controller],full_dr=args.full_dr,seed=args.seed,duration=args.duration)
    (folder/'config.json').write_text(json.dumps(cfg,indent=2))
    for name in ['run_case.py','hybrid_trial.py','control_core.py','full_lqr.py','linear_mpc.py','dr_components.py']:
        shutil.copy2(ROOT/name,folder/name)
    r,rows=run(cfg,True)
    (folder/'result.json').write_text(json.dumps(r,indent=2));(folder/'trajectory.json').write_text(json.dumps(rows))
    (folder/'source_sha256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.py')},indent=2))
    print(json.dumps({'out':str(folder),'success_ever':r['success'],'stable_max_s':r['stable_time'],'stable_at_end_s':r['stable_at_end'],'stop_reason':r['stop_reason'],'cross':r['cross'],'nonwheel_controls':r['nonwheel_contact_controls']}),flush=True)
