import io, re, sys
path = sys.argv[1]
step = int(sys.argv[2]) if len(sys.argv) > 2 else 200
cur = {}
rows = []
it = None
for ln in io.open(path, encoding='utf8', errors='ignore'):
    m = re.search(r'Learning iteration\s+(\d+)/', ln)
    if m:
        if it is not None and cur:
            rows.append((it, dict(cur)))
        it = int(m.group(1)); cur = {}
        continue
    m = re.match(r'\s*([A-Za-z0-9_/]+):\s*([-+0-9.eE]+)\s*$', ln)
    if m and it is not None:
        cur[m.group(1)] = float(m.group(2))
if it is not None and cur:
    rows.append((it, dict(cur)))
keys = ['Metrics/spin_rate_ratio', 'Metrics/yaw_error_rad_s', 'Metrics/spin_translation_m_s',
        'Metrics/gyro_command_abs', 'Metrics/wheel_torque_saturation', 'Metrics/upright_fraction',
        'Metrics/posture_height_m', 'Episode_Reward/spin_hold', 'Episode_Reward/spin_rate',
        'Episode_Reward/gyro_stance']
print('iter  ' + '  '.join(k.replace('Metrics/', '').replace('Episode_Reward/', 'R:')[:16] for k in keys))
n = 0
for it, d in rows:
    if not any(k in d for k in keys):
        continue
    n += 1
    if n % step:
        continue
    print('%6d ' % it + '  '.join(('%8.3f' % d[k]) if k in d else '     --  ' for k in keys))
print('samples', n, 'last iter', it)
