"""Save final policy configurations and physics/contact proof trajectories."""
import json,hashlib,shutil,platform,time
from pathlib import Path
import numpy as np,mujoco,scipy
from hybrid_trial import run
from control_core import ROOT

if __name__=='__main__':
    source=json.load(open(ROOT/'results/robust_flight_v1/best_config.json'));source['duration']=5.
    batch=json.load(open(ROOT/'results/FINAL_FULLDR_MATCHED_V2/summary.json'))
    out=ROOT/'results/FINAL_EVIDENCE_V2';out.mkdir(exist_ok=False)
    for name in ['hybrid_trial.py','control_core.py','full_lqr.py','linear_mpc.py','dr_components.py','kinematics.py','model_parameters.json','render_trajectory.py','matched_validation.py','final_evidence.py']:shutil.copy2(ROOT/name,out/name)
    configurations={};chosen=[]
    for mode in [False,True]:
        cfg=dict(source,mpc=mode,feedback_predict_s=.005 if mode else 0.,full_dr=False)
        name='mpc' if mode else 'lqr';configurations[name]=cfg;chosen.append(('nominal_'+name,cfg))
        candidates=[r['result'] for r in batch['rows'] if r['result']['config']['full_dr'] and r['result']['config']['mpc']==mode]
        good=[r for r in candidates if r.get('success') and r.get('stable_at_end',0)>=.5 and r.get('stop_reason')=='complete']
        good.sort(key=lambda r:(r.get('nonwheel_contact_controls',999)>0,-r.get('stable_at_end',0)))
        if good:chosen.append(('fullDR_'+name,good[0]['config']))
        bad=next((r for r in candidates if not r.get('success') and r.get('stop_reason')=='health'),None)
        if bad:chosen.append(('failure_'+name,bad['config']))
    (out/'controllers.json').write_text(json.dumps(configurations,indent=2))
    receipts=[]
    for name,cfg in chosen:
        r,rows=run(cfg,True);folder=out/name;folder.mkdir();(folder/'config.json').write_text(json.dumps(cfg,indent=2));(folder/'result.json').write_text(json.dumps(r,indent=2));(folder/'trajectory.json').write_text(json.dumps(rows))
        success_window=[row for row in rows if row['stable_s']>=.5]
        proof={'case':name,'seed':cfg['seed'],'full_dr':cfg['full_dr'],'mpc':cfg['mpc'],'success':r['success'],'stable_at_end':r['stable_at_end'],'stable_max':r['stable_time'],'stop':r['stop_reason'],'cross':r['cross'],'first_success_time':success_window[0]['time'] if success_window else None,'window_last':success_window[-1] if success_window else None,'trajectory_controls':len(rows),'physics_time':r['last']['time'],'nonwheel_controls':r['nonwheel_contact_controls']}
        receipts.append(proof);print(json.dumps({k:v for k,v in proof.items() if k!='window_last'}),flush=True)
    manifest={'version':'FINAL_EVIDENCE_V2','python':platform.python_version(),'mujoco':mujoco.__version__,'numpy':np.__version__,'scipy':scipy.__version__,'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.py')},'cases':receipts,'model_source_sha256':json.load(open(ROOT/'MODEL_PROVENANCE.json'))['source_xml_sha256'],'model_derived_sha256':json.load(open(ROOT/'MODEL_PROVENANCE.json'))['derived_xml_sha256'],'feedback':'sensor-consistent IMU+leg feedback; privileged world translation and yaw retained'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps({'evidence_complete':True,'cases':len(chosen)}),flush=True)
