"""Meaningful reader tests; synthetic cases never become future GPU passes."""
from pathlib import Path
import json,time,copy
import numpy as np
import yawpi_actual_reader_components_v3 as m
D=Path(__file__).resolve().parent;R=D/'reports';native=R/'YAWPI_OWN_NATIVE120_ACTUAL_CPU_ADMITTED_V3.json';ad=m.read(native);assert ad['passed_actual_data_and_factor_admission'] and ad['controls']==120 and ad['callbacks']==480
first=m.read(ad['factor_firstphysics_snapshot']['local_path']);birth=first['actual_last_birth'];m.birth_receipt(birth)
bad=[]
for key,value in [('profile','wrongprofile'),('full_collision_points',25199),('full_q30_exact',False),('XY_exact',False),('original_clearance_m',.001),('minimum_sampled_clearance_m',0.),('extra_physics_steps_forward_render_reset',1),('no_rng_draw',False)]:
 b=copy.deepcopy(birth);b[key]=value;bad.append(b)
b=copy.deepcopy(birth);b['factor_root_xyzw'][0][3:7]=b['original_root_xyzw'][0][3:7];bad.append(b)
b=copy.deepcopy(birth);b['factor_root_xyzw'][0][0]+=.1;bad.append(b)
b=copy.deepcopy(birth);b['factor_root_xyzw'][0][2]+=.1;bad.append(b)
rejected=0
for b in bad:
 try:m.birth_receipt(b)
 except AssertionError:rejected+=1
 else:raise AssertionError('Malformed own-birth fixture admitted')
half=1.2032113635;steps=3;g=np.arange(80)%3;worldsign=np.where(g==1,-1,1)
data=dict(root=np.zeros((steps,80,13)),group_ids=g,physical_wheel_force_N=np.zeros((steps*4,80,2,3),np.float32),COM_link_pos=np.zeros((steps,80,2,3),np.float32),episode=np.zeros((steps,80),np.int64),terminated=np.zeros((steps,80),bool))
data['physical_wheel_force_N'][...,2]=1.01
for s,x in enumerate((-half-.201,0.,half+.201)):data['COM_link_pos'][s,:,:,0]=(x*worldsign)[:,None]
report=dict(route_scope=dict(tile_centers=np.zeros((80,2)).tolist(),wave_x_halfspan_m=half),body_names=['left_wheel','right_wheel'])
per=m.route_rows(data,report);assert sum(x['contact_complete'] for x in per if x['group']==0)==27 and sum(x['contact_complete'] for x in per if x['group']==1)==27 and not any(x['contact_complete'] for x in per if x['group']==2)
data['terminated'][1,0]=True;per=m.route_rows(data,report);assert not per[0]['contact_complete'] and per[0]['all_valid_episodes'][0]['valid_controls']==1
data['terminated'][:]=False;data['episode'][1:,0]=1;per=m.route_rows(data,report);assert not per[0]['contact_complete'],'Cross-episode teleport was credited'
data['episode'][:]=0;data['physical_wheel_force_N'][:,0,:,2]=.99;per=m.route_rows(data,report)
# Original protocol position-vs-contact consistency must reject insufficient support.
raise AssertionError('Expected original support disagreement not rejected')
