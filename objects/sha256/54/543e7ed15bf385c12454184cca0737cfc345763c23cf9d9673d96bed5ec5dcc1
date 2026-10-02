from pathlib import Path
import json
import numpy as np

r = Path(__file__).resolve().parent
old = json.loads((r/'legacy10ms.json').read_text(encoding='utf-8'))
new = json.loads((r/'eager5ms.json').read_text(encoding='utf-8'))
a = np.load(r/'legacy10ms.npz'); b = np.load(r/'eager5ms.npz')
result = {
    'checkpoint_sha256': old['checkpoint_sha256'],
    'same_checkpoint': old['checkpoint_sha256'] == new['checkpoint_sha256'],
    'same_seed': old['seed'] == new['seed'], 'seconds': old['seconds'],
    'old_intervals_s': old['contact_diagnostic']['history_substep_update_intervals_s'],
    'new_intervals_s': new['contact_diagnostic']['history_substep_update_intervals_s'],
    'physics_pass': old['physics_pass'] and new['physics_pass'],
    'resets': [old['resets'],new['resets']],
    'trace_arrays': list(a.files),
    'array_differences': {}, 'per_env': [],
    'interpretation': 'Different reward/statistics are sampling changes, not policy learning. Five-second probe is not fifteen-second graduation.'
}
for k in a.files:
    if k in b.files and a[k].shape == b[k].shape and a[k].dtype.kind in 'fiu':
        result['array_differences'][k] = float(np.max(np.abs(a[k].astype(float)-b[k].astype(float))))
for i,(x,y) in enumerate(zip(old['contact_diagnostic']['environments'], new['contact_diagnostic']['environments'])):
    g1=next(g for g in old['groups'] if g['command_vx']==x['command'])
    g2=next(g for g in new['groups'] if g['command_vx']==y['command'])
    result['per_env'].append({'env':i,'command':x['command'],
        'height_credit':[old['contact_diagnostic']['height_credit_after_1s_mean_per_env'][i],new['contact_diagnostic']['height_credit_after_1s_mean_per_env'][i]],
        'window_contact_group_mean':[g1['both_wheels_scut_history'],g2['both_wheels_scut_history']],
        'unload_longest_ms':[x['longest_neither_contact_ms'],y['longest_neither_contact_ms']],
        'relative_gap_max_mm':[x['relative_gap_max_mm'],y['relative_gap_max_mm']],
        'support_slip_approx_m_s':[x['mean_support_slip_m_s'],y['mean_support_slip_m_s']],
        'wheel_impulse_Ns':[x['wheel_vertical_impulse_Ns'],y['wheel_vertical_impulse_Ns']],
        'root_peak_to_peak_mm':[x['root_z_peak_to_peak_mm'],y['root_z_peak_to_peak_mm']]})
(r/'comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
