"""Offline world-frame progress over the whole alive prefix and complete turns.

No speed magnitude graduation, half-circle selection, or post-failure samples.
Inputs are the measured root XY and heading; these routines do not simulate.
"""
import math
import numpy as np


def measure_world_cycles(times, root_xy, heading, direction, yaw_sign, first_failure_index=-1):
    t=np.asarray(times,dtype=float);xy=np.asarray(root_xy,dtype=float);h=np.asarray(heading,dtype=float)
    if yaw_sign not in (-1,1):raise ValueError('Use the commanded signed spin direction')
    if len(t)!=len(h) or xy.shape!=(len(t),2):raise ValueError('Trace shapes differ')
    if first_failure_index>=0:t,xy,h=t[:first_failure_index],xy[:first_failure_index],h[:first_failure_index]
    if len(t)<2:return {'valid':False,'complete_cycle_count':0,'reason':'Insufficient pre-failure samples'}
    if not np.isfinite(t).all() or not np.isfinite(xy).all() or not np.isfinite(h).all():raise ValueError('Nonfinite trace')
    if not np.all(np.diff(t)>0):raise ValueError('Times must increase')
    h=np.unwrap(h)
    phase=yaw_sign*(h-h[0])
    along_axis=np.array([math.cos(direction),math.sin(direction)])
    cross_axis=np.array([-math.sin(direction),math.cos(direction)])
    displacement=xy-xy[0];along=displacement@along_axis;cross=displacement@cross_axis
    total_duration=float(t[-1]-t[0])
    # Interpolate the first actual crossing of each full commanded-direction turn.
    # Keep the complete prefix from the very first sample; never pick good cycles.
    boundaries=[(float(t[0]),float(along[0]),float(cross[0]))]
    level=2*math.pi
    while level<=float(phase.max())+1e-12:
        candidates=np.flatnonzero((phase[:-1]<level)&(phase[1:]>=level))
        if not len(candidates):break
        i=int(candidates[0]);alpha=float((level-phase[i])/(phase[i+1]-phase[i]))
        values=[float(arr[i]+alpha*(arr[i+1]-arr[i])) for arr in (t,along,cross)]
        boundaries.append(tuple(values));level+=2*math.pi
    cycles=[{'duration_s':b[0]-a[0],'along_progress_m_s':(b[1]-a[1])/(b[0]-a[0]),
             'cross_drift_m_s':(b[2]-a[2])/(b[0]-a[0])} for a,b in zip(boundaries[:-1],boundaries[1:])]
    complete_duration=boundaries[-1][0]-boundaries[0][0]
    return {'valid':True,'whole_prefix_duration_s':total_duration,
        'whole_prefix_along_m_s':float(along[-1]/total_duration),
        'whole_prefix_cross_m_s':float(cross[-1]/total_duration),
        'net_along_displacement_m':float(along[-1]),'net_cross_displacement_m':float(cross[-1]),
        'max_cross_excursion_m':float(np.max(np.abs(cross))),
        'signed_net_turns':float((h[-1]-h[0])/(2*math.pi)),
        'complete_cycle_count':len(cycles),'complete_prefix_duration_s':complete_duration,
        'complete_prefix_along_m_s':boundaries[-1][1]/complete_duration if cycles else None,
        'complete_prefix_cross_m_s':boundaries[-1][2]/complete_duration if cycles else None,
        'partial_tail_duration_s':float(total_duration-complete_duration),'cycles':cycles,
        'first_failure_index':int(first_failure_index),'post_failure_samples_used':False}
