"""Append-only public-model algebra probe, not a physics episode."""
from pathlib import Path
import hashlib,json,traceback
import numpy as np
R=Path(__file__).resolve().parent

def plain(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items() if k!='jacobians'}
    if isinstance(x,(list,tuple)):return [plain(v) for v in x]
    return x

def main():
    n=1
    while (R/'model_probes'/f'{n:03d}').exists():n+=1
    out=R/'model_probes'/f'{n:03d}';(out/'sources').mkdir(parents=True)
    source=[]
    for name in ['nominal_model.py','export_public_nominal.py','probe_nominal.py','PUBLIC_NOMINAL_CONSTANTS.json']:
        raw=(R/name).read_bytes();(out/'sources'/name).write_bytes(raw);source.append({'file':name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    try:
        from nominal_model import NominalModel
        m=NominalModel();t=m.terms(m.q_nominal,np.zeros(4),np.zeros(4),[0,0,9.81],[0,0,0],[0,0,0]);f=m.solve_terms(t,m.tau_nominal)
        result={'status':'ALGEBRA_PROBE_NOT_MEASURED_FORCE','physics_steps':0,'sources':source,'terms':plain(t),'force':plain(f),'half_nominal_weight_N':m.mass.sum()*9.81/2}
    except Exception:
        (out/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
    (out/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8');print(json.dumps({'probe':n,'force':plain(f),'gas_tau4':plain(t['tauGas4']),'load4':plain(t['load4']),'half_weight_N':result['half_nominal_weight_N']},indent=2))
if __name__=='__main__':main()
