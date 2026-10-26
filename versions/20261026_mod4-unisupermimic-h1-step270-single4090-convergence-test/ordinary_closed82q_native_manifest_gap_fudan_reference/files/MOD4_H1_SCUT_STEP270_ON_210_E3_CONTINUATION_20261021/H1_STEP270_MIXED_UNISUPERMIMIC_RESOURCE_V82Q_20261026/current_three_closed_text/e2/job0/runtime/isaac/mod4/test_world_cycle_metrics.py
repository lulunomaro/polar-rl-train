"""CPU ideal and negative-control checks; no policy/physics acceptance."""
from pathlib import Path
import json
import math
import numpy as np
from world_cycle_metrics import measure_world_cycles


def main():
    cases=[]
    t=np.arange(0,15.0001,.01)
    for speed in [.15,.3,.5]:
        for omega in [-2.,-1.,1.,2.]:
            direction=.7;phase0=-1.1
            phase=phase0+omega*t;heading=phase+direction
            along=speed*t+speed/(2*omega)*(np.sin(2*phase)-math.sin(2*phase0))
            cross=speed/(2*omega)*(math.cos(2*phase0)-np.cos(2*phase))
            xy=np.stack([along*math.cos(direction)-cross*math.sin(direction),
                         along*math.sin(direction)+cross*math.cos(direction)],axis=1)
            wrapped=np.arctan2(np.sin(heading),np.cos(heading))
            r=measure_world_cycles(t,xy,wrapped,direction,1 if omega>0 else -1)
            assert r['complete_cycle_count']>=2
            assert abs(r['complete_prefix_along_m_s']-speed)<1e-5
            assert abs(r['complete_prefix_cross_m_s'])<1e-5
            assert r['max_cross_excursion_m']<=speed/abs(omega)+1e-5
            cases.append({'speed':speed,'yaw':omega,'complete_cycles':r['complete_cycle_count']})
    omega=1.;body_v=.5
    circle=np.stack([body_v*np.sin(t),body_v*(1-np.cos(t))],axis=1)
    negative=measure_world_cycles(t,circle,t,0.,1)
    assert abs(negative['complete_prefix_along_m_s'])<1e-5
    assert abs(negative['complete_prefix_cross_m_s'])<1e-5
    short=measure_world_cycles(t[:51],circle[:51],t[:51],0.,1)
    assert short['complete_cycle_count']==0 and short['complete_prefix_along_m_s'] is None
    wrong=measure_world_cycles(t,circle,-t,0.,1)
    assert wrong['complete_cycle_count']==0
    poisoned=circle.copy();poisoned[400:]=np.nan
    prefix=measure_world_cycles(t,poisoned,t,0.,1,first_failure_index=400)
    assert prefix['valid'] and prefix['whole_prefix_duration_s']==t[399]
    assert not prefix['post_failure_samples_used']
    out={'ideal_cases':cases,'constant_body_circle_zero_net_progress':True,
         'no_complete_turn_is_not_graduation':True,'wrong_spin_direction_no_positive_cycles':True,
         'post_failure_excluded':True,'cpu_only':True,'actual_robot_measured':False}
    Path(__file__).with_name('WORLD_CYCLE_METRICS_CPU_CHECKS.json').write_text(json.dumps(out,indent=2))
    print(json.dumps({k:v for k,v in out.items() if k!='ideal_cases'}))


if __name__=='__main__':main()
