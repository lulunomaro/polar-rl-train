"""Pure report checks; no simulation imports."""
import math

def finite(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)

def assess(d):
    missing=[k for k in ['groups','physics_pass','nonfinite','DR_audit'] if k not in d]
    if missing:return {'accepted':False,'reason':'missing fields','missing':missing}
    failures=[]
    if not isinstance(d['groups'],list) or not d['groups']:
        return {'accepted':False,'failures':['empty_groups']}
    if d['nonfinite'] or not d['physics_pass']:failures.append('physics')
    if not d['DR_audit'].get('parameters_pass'):failures.append('DR_parameters')
    if not finite(d.get('seconds')) or d['seconds']<15:failures.append('short_run_not_acceptance')
    seen={(g.get('command_vx'),g.get('profile')) for g in d['groups']}
    required={(v,'constant') for v in [0.,.3,.6,1.]}
    limit=d.get('speed_limit')
    if not finite(limit) or limit<=0:failures.append('missing_speed_limit')
    else:required.update({(-limit,'constant'),(limit,'constant')})
    if d.get('ramp_suite'):required.update({(v,'ramp_brake_reverse') for v in [-1.5,1.5,-2.,2.]})
    if not required<=seen:failures.append('missing_command_groups')
    for i,g in enumerate(d['groups']):
        value=g.get('strict_pass_window')
        if not finite(value) or not .8<=value<=1.:failures.append(f'group_{i}_window')
        value=g.get('survival_fraction')
        if not finite(value) or not .8<=value<=1.:failures.append(f'group_{i}_survival')
        if g.get('profile')=='ramp_brake_reverse':
            value=g.get('stop_abs_speed')
            if not finite(value) or not 0<=value<=.12:failures.append(f'group_{i}_stop')
    return {'accepted':not failures,'failures':failures,'scope':'simulator nominal/mild test only; not real robot approval'}

def compare(nominal,dr):
    if not nominal.get('checkpoint') or nominal.get('seed') is None or nominal.get('checkpoint')!=dr.get('checkpoint') or nominal.get('seed')!=dr.get('seed'):
        raise ValueError('Pair must use identical checkpoint and seed')
    a,b=nominal['groups'],dr['groups']
    if len(a)!=len(b):raise ValueError('Different groups')
    differences=[]
    for x,y in zip(a,b):
        if (x['command_vx'],x.get('profile'))!=(y['command_vx'],y.get('profile')):raise ValueError('Different command profiles')
        differences.append({'command':x['command_vx'],'profile':x.get('profile'),
          'changes':{k:y[k]-x[k] for k in ['vel_error','tilt','height_error','delta','d2','strict_pass_window'] if x.get(k) is not None and y.get(k) is not None}})
    return {'nominal':assess(nominal),'DR':assess(dr),'differences':differences}
