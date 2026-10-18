from pathlib import Path
import json,time,numpy as np
from current_sim import CurrentSim
D=Path(__file__).resolve().parent
def main():
    s=CurrentSim();params=s.parameter_readback();cases=[]
    for label,x,y,v,w,steps in [('stand',-1,0,0,0,300),('forward',-1,-3,.5,0,500),('reverse',-1,-3,-.4,0,400),('turn',-1,-3,0,1.5,400),('ripples',-.5,0,.5,0,900),('gentle_ramp',0,2.7,.4,0,900)]:
        s.reset(x,y,0);start=s.base_position.copy();begin=time.perf_counter();minup=1.;minz=1.;fault=None
        for i in range(steps):
            s.command.vx=v*min(1.,i/80);s.command.wz=w*min(1.,i/80);s.step_control()
            h=s.health();minup=min(minup,h['upright_cos']);minz=min(minz,s.base_position[2])
            if minup<.65 or minz<.17:fault='fallen or low body';break
        cases.append(dict(case=label,control_steps=i+1,simulation_seconds=float(s.data.time),wall_seconds=time.perf_counter()-begin,displacement=(s.base_position-start).tolist(),min_upright_cos=minup,min_root_z=minz,fault=fault,health=s.health()))
        print(json.dumps(cases[-1]),flush=True)
    report=dict(parameter_readback=params,cases=cases,all_cases_upright_finite=all(x['fault'] is None and x['health']['finite'] for x in cases),scope='Local nominal MuJoCo smoke, not Isaac retention graduation')
    (D/'SMOKE_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    if not report['all_cases_upright_finite']:raise RuntimeError('Local playback behavior requires review; see SMOKE_REVIEW.json')
if __name__=='__main__':main()
