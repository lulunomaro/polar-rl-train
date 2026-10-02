from pathlib import Path
import numpy as np,json
ROOT=Path(__file__).resolve().parent
OLD=ROOT
a=np.load(OLD/'legacy10ms.npz');b=np.load(ROOT/'integrated_probe.npz')
d=json.loads((ROOT/'integrated_probe.json').read_text())
v=b['values'];cols=list(b['columns']);n=v.shape[1]
forces=np.stack([v[:,:,[cols.index(x) for x in ['left_fx','left_fy','left_fz']]],
                 v[:,:,[cols.index(x) for x in ['right_fx','right_fy','right_fz']]]],axis=2)
bin_means=forces.reshape(-1,10,n,2,3).mean(axis=1)
history=np.zeros((n,3,2,3),dtype=np.float32);expected=[]
for i,mean in enumerate(bin_means):
    history[:,2]=history[:,1];history[:,1]=history[:,0];history[:,0]=mean
    if (i+1)%2==0:expected.append(history.copy())
expected=np.stack(expected)
error=float(np.max(np.abs(expected-b['bin_history'])))
impulses=np.maximum(forces[:,:,:,2],0).reshape(-1,20,n,2).sum(axis=1)*.0005
impulse_error=float(np.max(np.abs(impulses-b['bin_impulse'])))
gate=(np.linalg.norm(expected,axis=-1).max(axis=2)>1).all(axis=2)
recorded_gate=b['height_credit']>0
physics_diff=float(np.max(np.abs(a['values']-b['values'])))
result={'physics_array_max_abs_diff':physics_diff,'bin_mean_max_error_N':error,
        'control_impulse_max_error_Ns':impulse_error,'gate_mismatch_count':int((gate!=recorded_gate).sum()),
        'integrated_contact_after_1s_per_env':gate[100:].mean(0).tolist(),
        'height_credit_after_1s_per_env':b['height_credit'][100:].mean(0).tolist(),
        'physics_pass':d['physics_pass'],'resets':d['resets'],
        'source':'independent numpy integration of raw2kHz forces; no peak-to-continuous-contact inference',
        'physical_unload_gap_slip_unchanged':physics_diff==0.,
        'probe_seconds':d['seconds']}
result['pass']=physics_diff==0 and error<.001 and impulse_error<1e-4 and result['gate_mismatch_count']==0 and d['physics_pass'] and d['resets']==0
(ROOT/'offline_verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
assert result['pass']
