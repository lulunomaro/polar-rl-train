"""Analyze frozen-policy probes; alternate contact summaries never replace gates."""
import json
from pathlib import Path
import numpy as np

root = Path(__file__).resolve().parent
metrics = []

def longest(mask, dt):
    edge = np.diff(np.r_[False, mask, False].astype(int))
    widths = np.flatnonzero(edge == -1) - np.flatnonzero(edge == 1)
    return float(widths.max(initial=0) * dt)

for tag in ['solver_16_4', 'solver_32_8']:
    result = json.loads((root / (tag+'.json')).read_text())
    z = np.load(root/(tag+'.npz'), allow_pickle=False)
    x = z['values']; ts = np.cumsum(z['dt']); dt = float(np.median(z['dt']))
    cols = list(z['columns']); ci = {str(k):i for i,k in enumerate(cols)}
    assert result['physics_pass'] and not result['nonfinite'] and result['resets'] == 0
    assert np.all(np.isfinite(x))
    assert np.allclose(z['dt'], dt)
    control_n = int(round(.01/dt))
    assert len(x)%control_n == 0
    for env, d in enumerate(result['contact_diagnostic']['environments']):
        a=x[ts>1.,env]; f=np.stack([a[:,ci['left_fz']],a[:,ci['right_fz']]],axis=-1)
        fn=np.stack([a[:,ci['left_force_norm']],a[:,ci['right_force_norm']]],axis=-1)
        slip=np.stack([a[:,ci['left_support_slip']],a[:,ci['right_support_slip']]],axis=-1)
        contact=fn>1
        ctrl=x[:,env].reshape(-1,control_n,x.shape[-1])
        full=ctrl[:,:, [ci['left_force_norm'],ci['right_force_norm']]]
        endpoint=full[:,-1,:]
        # A 3-control-sample endpoint window versus peaks of ALL physics samples
        # in the same 30 ms duration. These are diagnostics, not acceptance gates.
        endpoint_hist=np.maximum.reduce([endpoint[2:],endpoint[1:-1],endpoint[:-2]])
        blockpeak=full.max(axis=1)
        all_hist=np.maximum.reduce([blockpeak[2:],blockpeak[1:-1],blockpeak[:-2]])
        endpoint_hist=endpoint_hist[98:];all_hist=all_hist[98:]
        paired_count=min(len(endpoint_hist),len(all_hist))
        endpoint_hist=endpoint_hist[:paired_count];all_hist=all_hist[:paired_count]
        load_total=f.sum(axis=1)
        # Non-overlapping 30 ms load impulse summaries, no normalization to
        # a guessed vehicle weight; report measured mean vertical force.
        blocks=load_total[:len(load_total)//(3*control_n)*(3*control_n)].reshape(-1,3*control_n)
        loadavg=blocks.mean(axis=1)
        legtorque=a[:,[ci[f'leg_torque_{i}'] for i in range(4)]]
        legqd=a[:,[ci[f'leg_qd_{i}'] for i in range(4)]]
        pdtarget=a[:,[ci[f'leg_pd_target_{i}'] for i in range(4)]]
        legq=a[:,[ci[f'leg_q_{i}'] for i in range(4)]]
        computed=a[:,[ci[f'leg_computed_torque_{i}'] for i in range(4)]]
        frequencies=np.fft.rfftfreq(len(a),dt)
        def spectral_peak(signal,low,high):
            power=np.abs(np.fft.rfft((signal-signal.mean())*np.hanning(len(signal))))**2
            use=(frequencies>=low)&(frequencies<=high)
            return float(frequencies[use][power[use].argmax()])
        sides=result['contact_diagnostic']['mesh_audit'][0]['points']//2
        facet_expected=float(np.abs(a[:,[ci['wheel_qd_l'],ci['wheel_qd_r']]]).mean()*sides/(2*np.pi))
        record={'solver':tag,'env':env,'command':d['command'],
            'mean_speed_m_s':float(a[:,ci['speed']].mean()),
            'relative_gap_max_mm':d['relative_gap_max_mm'],
            'root_height_peak_to_peak_mm':d['root_z_peak_to_peak_mm'],
            'both_contact_physics':float(contact.all(axis=1).mean()),
            'neither_contact_physics':float((~contact.any(axis=1)).mean()),
            'longest_neither_above_1N_ms':longest(~contact.any(axis=1),dt)*1000,
            'mean_wheel_vertical_force_N':f.mean(axis=0).tolist(),
            'wheel_vertical_force_p99_N':np.quantile(f,.99,axis=0).tolist(),
            'total_force_30ms_mean_p05_N':float(np.quantile(loadavg,.05)),
            'total_force_30ms_mean_min_N':float(loadavg.min()),
            'total_force_30ms_mean_p95_N':float(np.quantile(loadavg,.95)),
            'contact_endpoint_3x10ms_both':float((endpoint_hist>1).all(axis=1).mean()),
            'contact_allphysics_30ms_peak_both':float((all_hist>1).all(axis=1).mean()),
            'loaded_force_weighted_support_slip_m_s':((slip*np.maximum(f,0)).sum(axis=0)/np.maximum(np.maximum(f,0).sum(axis=0),1e-12)).tolist(),
            'loaded_support_slip_p95_m_s':[float(np.quantile(slip[contact[:,j],j],.95)) for j in range(2)],
            'leg_applied_torque_p99_abs_Nm':np.quantile(np.abs(legtorque),.99,axis=0).tolist(),
            'leg_qd_rms_rad_s':np.sqrt(np.mean(legqd**2,axis=0)).tolist(),
            'leg_pd_error_rms_rad':np.sqrt(np.mean((pdtarget-legq)**2,axis=0)).tolist(),
            'leg_computed_minus_applied_gt_0p1_fraction':float((np.abs(computed-legtorque)>.1).mean()),
            'leg_positive_power_mean_W':float(np.maximum(legtorque*legqd,0).sum(axis=1).mean()),
            'wheel_qd_max_abs_rad_s':float(np.abs(a[:,[ci['wheel_qd_l'],ci['wheel_qd_r']]]).max()),
            'sum_Fz_dominant_10_200Hz':spectral_peak(load_total,10,200),
            'root_height_dominant_0p5_20Hz':spectral_peak(a[:,ci['root_z']],.5,20),
            'expected_facets_times_actual_rotation_Hz':facet_expected,
        }
        metrics.append(record)

payload={'warning':'5 s diagnostic, 4 s steady statistics, two environments per speed; not 15 s graduation. Gaps use input USD hull support, relative to loaded baseline; cooking/offsets excluded. Slip is velocity of lowest support vertex approximation. Alternate all-physics peak window is never a replacement acceptance gate.',
    'metrics':metrics,'same_checkpoint':len({json.loads((root/(t+'.json')).read_text())['checkpoint_sha256'] for t in ['solver_16_4','solver_32_8']})==1}
(root/'comparison.json').write_text(json.dumps(payload,indent=2))
for q in metrics:
    if abs(q['command'])==1.5:
        print(json.dumps(q))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('seaborn-v0_8-whitegrid')
for env,command in [(2,-1.5),(3,1.5)]:
    fig,axes=plt.subplots(4,1,figsize=(11,9),sharex=True,layout='constrained')
    for tag,color in [('solver_16_4','#1479b8'),('solver_32_8','#de7b26')]:
        z=np.load(root/(tag+'.npz'),allow_pickle=False);t=np.cumsum(z['dt']);ci={str(k):i for i,k in enumerate(z['columns'])};a=z['values'][:,env]
        mask=(t>=2)&(t<=2.4);a=a[mask];t=t[mask]
        axes[0].plot(t,a[:,ci['left_fz']]+a[:,ci['right_fz']],color=color,label=tag)
        axes[1].plot(t,a[:,ci['root_z']]*1000,color=color,label=tag)
        diag=json.loads((root/(tag+'.json')).read_text())['contact_diagnostic']['environments'][env]
        gap=(a[:,ci['left_gap']]*1000-diag['loaded_gap_baseline_mm'][0])
        axes[2].plot(t,gap,color=color,label=tag)
        axes[3].plot(t,a[:,ci['left_support_slip']],color=color,label=tag)
    for ax,label in zip(axes,['Sum wheel Fz (N)','Root height (mm)','Left relative support gap (mm)','Left support slip approx. (m/s)']):ax.set_ylabel(label);ax.legend(loc='upper right')
    axes[-1].set_xlabel('Simulation time (s)');fig.suptitle(f'Frozen model7450, commanded {command:+.1f} m/s; diagnostic only')
    fig.savefig(root/f'contact_{command:+.1f}.png',dpi=150);plt.close(fig)
