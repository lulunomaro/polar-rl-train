"""Measure original full-field collision corridors for native training terrain."""
import numpy as np
from fsm_paths import HERE
from fsm_io import put,sha256
from fsm_maps import metadata,reference
from manual_fsm_runtime import ManualPolicy,ManualSimulation


def main():
    sim=ManualSimulation(ManualPolicy(load_jumps=False,detector={}))
    sim.load_map(metadata('rm27_west'))
    xs=np.arange(-2.4,4.601,.01)
    ys=np.arange(-1.6,1.601,.04)
    heights=[]
    reports=[]
    for course in ('rm27_west','rm27_east'):
        origin_x,origin_y,direction=reference.RM[course]
        z=np.array([[sim.ground_z(origin_x+direction*x,origin_y+direction*y,4.5)
                     for x in xs] for y in ys])
        heights.append(z)
        center=z[len(ys)//2]
        reports.append(dict(course=course,origin=[origin_x,origin_y],direction=direction,
            sampled_min_height_m=float(z.min()),sampled_max_height_m=float(z.max()),
            centerline=[dict(x=float(x),z=float(center[i])) for i,x in enumerate(xs) if i%5==0],
            original_source=str(reference.MAP_CACHE/'scene_rmuc2027_mod4v3_v1.xml')))
        print(course,'surveyed',z.shape,'height',z.min(),z.max(),flush=True)
    output=HERE/'RM27_SURVEY.npz'
    np.savez_compressed(output,xs=xs,ys=ys,heights=np.array(heights))
    put(HERE/'evidence/STAGE2_RM27_SURVEY.json',dict(rows=reports,path=output.name,sha256=sha256(output),
        source_sha256=sha256(reference.MAP_CACHE/'scene_rmuc2027_mod4v3_v1.xml'),
        purpose='Offline original collision corridor survey for native training terrain only; never policy/FSM inputs',
        grid_spacing_m=[.01,.04],original_cpu_map_unchanged=True))


if __name__=='__main__':main()
