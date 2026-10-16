"""Offline trace contract only. Synthetic checks are not robot/GPU qualification."""
import math

def review(rows, dt=.0025):
    """One env/episode valid prefix; upstream must supply actual full-collider evidence."""
    assert rows and dt==.0025
    keys={'t','episode','wheel_N','wheel_clearance_m','all_collision_clear','riser_clearance_m','on_upper_platform','upward_takeoff','illegal_contact','ordinary','guard','tilt_rad','yaw_error','vx_error','callbacks_complete'}
    for i,r in enumerate(rows):
        assert keys <= r.keys()
        assert len(r['wheel_N'])==len(r['wheel_clearance_m'])==2
        assert all(math.isfinite(float(x)) for x in [r['t'],*r['wheel_N'],*r['wheel_clearance_m'],r['riser_clearance_m'],r['tilt_rad'],r['yaw_error'],r['vx_error']])
        assert all(type(r[k]) is bool for k in ('all_collision_clear','on_upper_platform','upward_takeoff','illegal_contact','ordinary','guard','callbacks_complete'))
        assert r['callbacks_complete'], 'Missing physics callback cannot receive credit'
        assert i==0 or abs(r['t']-rows[i-1]['t']-dt)<1e-8
    # Never connect a reset, ordinary failure or unknown guard to a later completion.
    stop=next((i for i,r in enumerate(rows) if r['episode']!=rows[0]['episode'] or r['ordinary'] or r['guard'] or r['illegal_contact']),len(rows))
    before=False;air_n=land_n=recovery_n=0;airborne=cleared=landed=recovered=False
    for r in rows[:stop]:
        support=min(r['wheel_N'])>1
        air=max(r['wheel_N'])<=1 and min(r['wheel_clearance_m'])>.005 and r['all_collision_clear']
        if not airborne:
            if support:before=True
            air_n=air_n+1 if air and before and r['upward_takeoff'] else 0
            airborne=air_n>=16
        if airborne and air and r['riser_clearance_m']>0 and r['on_upper_platform']:cleared=True
        if cleared:
            land_n=land_n+1 if support and r['on_upper_platform'] else 0
            landed |= land_n>=12
        if landed:
            stable=support and r['on_upper_platform'] and abs(r['tilt_rad'])<math.radians(10) and abs(r['yaw_error'])<.2 and abs(r['vx_error'])<=.03
            recovery_n=recovery_n+1 if stable else 0
            recovered |= recovery_n>=200
    return dict(valid_prefix_physics_rows=stop,airborne=airborne,cleared=cleared,landed=landed,recovered=recovered,complete=all((before,airborne,cleared,landed,recovered)),evidence_level='OFFLINE_INPUT_CONTRACT_ONLY_NOT_PHYSICS_CERTIFICATION')
