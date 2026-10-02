"""Pure report checks; no simulation imports."""
def assess(d):
    missing=[k for k in ['groups','physics_pass','nonfinite','DR_audit'] if k not in d]
    if missing:return {'accepted':False,'reason':'missing fields','missing':missing}
    failures=[]
    if d['nonfinite'] or not d['physics_pass']:failures.append('physics')
    if not d['DR_audit'].get('parameters_pass'):failures.append('DR_parameters')
    if d.get('seconds',0)<15:failures.append('short_run_not_acceptance')
    for i,g in enumerate(d['groups']):
        if g.get('strict_pass_window',0)<.8:failures.append(f'group_{i}_window')
        if g.get('profile')=='ramp_brake_reverse' and g.get('stop_abs_speed',999)>.12:failures.append(f'group_{i}_stop')
    return {'accepted':not failures,'failures':failures,'scope':'simulator nominal/mild test only; not real robot approval'}

def compare(nominal,dr):
    if nominal.get('checkpoint')!=dr.get('checkpoint') or nominal.get('seed')!=dr.get('seed'):
        raise ValueError('Pair must use identical checkpoint and seed')
    a,b=nominal['groups'],dr['groups']
    if len(a)!=len(b):raise ValueError('Different groups')
    differences=[]
    for x,y in zip(a,b):
        if (x['command_vx'],x.get('profile'))!=(y['command_vx'],y.get('profile')):raise ValueError('Different command profiles')
        differences.append({'command':x['command_vx'],'profile':x.get('profile'),
          'changes':{k:y[k]-x[k] for k in ['vel_error','tilt','height_error','delta','d2','strict_pass_window'] if x.get(k) is not None and y.get(k) is not None}})
    return {'nominal':assess(nominal),'DR':assess(dr),'differences':differences}
